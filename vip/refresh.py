#!/usr/bin/env python3
"""Refresh the VIP Live scoreboard from TikTok Shop analytics.

Credentials come from the environment, never the repo:
  TTS_APP_KEY  TTS_APP_SECRET  TTS_SHOP_CIPHER  TTS_REFRESH_TOKEN

Usage:  python3 vip/refresh.py [--month YYYY-MM]
Writes vip/data.json for the given month (default: current), then runs build.py.
"""
import argparse, collections, datetime, hashlib, hmac, json, os, subprocess, sys
import time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://open-api.tiktokglobalshop.com"
BRAND = {"frostbuddy"}          # shop's own account, not a VIP seller

def env(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(f"missing required env var {name}")
    return v

APP_KEY, APP_SECRET = env("TTS_APP_KEY"), env("TTS_APP_SECRET")
SHOP_CIPHER, REFRESH_TOKEN = env("TTS_SHOP_CIPHER"), env("TTS_REFRESH_TOKEN")


def get_token():
    url = ("https://auth.tiktok-shops.com/api/v2/token/refresh?"
           + urllib.parse.urlencode({"app_key": APP_KEY, "app_secret": APP_SECRET,
                                     "refresh_token": REFRESH_TOKEN,
                                     "grant_type": "refresh_token"}))
    with urllib.request.urlopen(url, timeout=60) as r:
        d = json.loads(r.read())
    if d.get("code") != 0:
        sys.exit(f"token refresh failed: {d.get('message')}")
    return d["data"]["access_token"]


def sign(path, params):
    keys = sorted(k for k in params if k not in ("sign", "access_token"))
    msg = APP_SECRET + path + "".join(f"{k}{params[k]}" for k in keys) + APP_SECRET
    return hmac.new(APP_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()


def call(token, path, params):
    p = dict(params, app_key=APP_KEY, timestamp=str(int(time.time())),
             shop_cipher=SHOP_CIPHER)
    p["sign"] = sign(path, p)
    req = urllib.request.Request(f"{BASE}{path}?" + urllib.parse.urlencode(p))
    req.add_header("x-tts-access-token", token)
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def month_bounds(ym):
    y, m = (int(x) for x in ym.split("-"))
    start = datetime.date(y, m, 1)
    end = datetime.date(y + (m == 12), (m % 12) + 1, 1)
    return start, end


def pull_month(token, start, end):
    """All live sessions in [start, end). Returns (sessions, latest_available_date)."""
    out, page_token, latest, fails = [], None, None, 0
    while True:
        p = {"start_date_ge": start.isoformat(), "end_date_lt": end.isoformat(),
             "page_size": "100", "currency": "USD",
             "sort_field": "gmv", "sort_order": "DESC"}
        if page_token:
            p["page_token"] = page_token
        try:
            r = call(token, "/analytics/202509/shop_lives/performance", p)
        except Exception as ex:
            fails += 1
            if fails > 20:
                sys.exit(f"giving up after repeated failures: {ex}")
            time.sleep(3)
            continue
        if r.get("code") != 0:
            sys.exit(f"api error: {r.get('message')}")
        fails = 0
        d = r.get("data") or {}
        latest = d.get("latest_available_date") or latest
        rows = d.get("live_stream_sessions") or []
        out += rows
        page_token = d.get("next_page_token")
        if not page_token or not rows:
            return out, latest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", default=datetime.date.today().strftime("%Y-%m"))
    ap.add_argument("--force", action="store_true",
                    help="write even if the monthly total went down")
    args = ap.parse_args()

    start, end = month_bounds(args.month)
    lo = int(datetime.datetime.combine(start, datetime.time()).timestamp())
    hi = int(datetime.datetime.combine(end, datetime.time()).timestamp())

    token = get_token()
    sessions, latest = pull_month(token, start, end)

    gmv, last_day = collections.defaultdict(float), None
    for s in sessions:
        u = s.get("username")
        if u in BRAND:
            continue
        try:
            st = int(s.get("start_time"))
        except (TypeError, ValueError):
            continue
        if not (lo <= st < hi):          # the API window can bleed past the month
            continue
        sp = s.get("sales_performance") or {}
        gmv[u] += float((sp.get("gmv") or {}).get("amount") or 0)
        day = datetime.date.fromtimestamp(st)
        last_day = day if last_day is None else max(last_day, day)

    path = os.path.join(HERE, "data.json")
    prev = json.load(open(path))
    roster = [(r["handle"], r["name"]) for r in prev["rows"]]
    rows = [{"handle": h, "name": n, "gmv": round(gmv.get(h, 0.0), 2)} for h, n in roster]
    rows.sort(key=lambda r: -r["gmv"])

    off = sorted(((h, v) for h, v in gmv.items() if h not in dict(roster)),
                 key=lambda z: -z[1])[:5]
    coverage_end = last_day or start
    doc = {
        "period": start.strftime("%B %Y"),
        "coverage": f"{start.strftime('%b %-d')} – {coverage_end.strftime('%b %-d, %Y')}",
        "updated": datetime.date.today().strftime("%B %-d, %Y"),
        "source": "TikTok Shop live-session analytics",
        "rows": rows,
    }
    total = sum(r["gmv"] for r in rows)
    prev_total = sum(r["gmv"] for r in prev["rows"])

    # Within one month GMV only accumulates. A drop means the pull is bad
    # (partial paging, an API hiccup), and publishing it would wrongly demote
    # sellers. A drop across a month boundary is just the reset.
    if (not args.force and prev.get("period") == doc["period"]
            and total < prev_total * 0.98):
        sys.exit(f"refusing to write: {doc['period']} total fell from "
                 f"${prev_total:,.0f} to ${total:,.0f}. The pull is likely "
                 f"incomplete. Re-run, or pass --force if this is expected.")

    json.dump(doc, open(path, "w"), indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, "build.py")], check=True)

    print(f"month={args.month} sessions={len(sessions)} "
          f"coverage={doc['coverage']} tiktok_latest={latest}")
    print(f"total=${total:,.0f} gold={sum(1 for r in rows if r['gmv']>=30000)} "
          f"silver={sum(1 for r in rows if 5000<=r['gmv']<30000)} "
          f"active={sum(1 for r in rows if r['gmv']>0)}/{len(rows)}")
    if off:
        print("off-roster creators with GMV:", ", ".join(f"@{h} ${v:,.0f}" for h, v in off))


if __name__ == "__main__":
    main()
