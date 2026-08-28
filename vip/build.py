import json, html, os

GOLD, SILVER, SHOW_MIN = 30000, 5000, 1000
PERIOD = "August 2026 (through Aug 26)"

rows = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")))
gold   = [r for r in rows if r['aug'] >= GOLD]
silver = [r for r in rows if SILVER <= r['aug'] < GOLD]
build  = [r for r in rows if r['aug'] < SILVER]
shown_build = [r for r in build if r['aug'] >= SHOW_MIN]
hidden = len(build) - len(shown_build)

m = lambda v: f"${v:,.0f}"
e = lambda s: html.escape(str(s))

def trend(r):
    if r['jul'] <= 0:
        return '<span class="tr new">new</span>' if r['aug'] > 0 else ''
    d = (r['aug'] - r['jul']) / r['jul'] * 100
    if abs(d) < 5:
        return '<span class="tr flat">flat vs July</span>'
    cls, arr = ('up', '▲') if d > 0 else ('down', '▼')
    amt = f'{r["aug"] / r["jul"]:.0f}\u00d7' if d >= 300 else f'{abs(d):.0f}%'
    return f'<span class="tr {cls}">{arr} {amt} vs July</span>'

def line(r, rank, tier):
    target = None if tier == 'gold' else (GOLD if tier == 'silver' else SILVER)
    label  = 'to Gold' if tier == 'silver' else 'to Silver'
    if target:
        pct  = min(100, r['aug'] / target * 100)
        foot = f'<div class="togo">{m(target - r["aug"])} {label}</div>'
    else:
        pct, foot = 100, '<div class="togo gold">Gold line cleared</div>'
    gph = f'{m(r["aug"] / r["hours"])}/hr' if r['hours'] >= 1 else '—'
    hrs = f'{r["hours"]:.0f} hrs on air' if r['hours'] >= 1 else 'under 1 hr on air'
    rcls = f' r{rank}' if tier == 'gold' else ''
    return f'''<div class="row{rcls}">
  <div class="rank">{rank}</div>
  <div class="who">
    <div class="handle">{e(r['name'])} <span class="at">@{e(r['handle'])}</span></div>
    <div class="subline">{hrs} · {gph} {trend(r)}</div>
    <div class="meter"><i style="width:{pct:.1f}%"></i></div>
    {foot}
  </div>
  <div class="money"><div class="gmv">{m(r['aug'])}</div><div class="gmvlbl">live GMV</div></div>
</div>'''

def board(rs, tier, empty="No sellers at this level this month."):
    if not rs:
        return f'<div class="board"><div class="row empty">{empty}</div></div>'
    return '<div class="board">' + ''.join(line(r, i + 1, tier) for i, r in enumerate(rs)) + '</div>'

tot   = sum(r['aug'] for r in rows)
hours = sum(r['hours'] for r in rows)

CSS = """
  :root{
    --blue:#4da3e0; --blue-dark:#2f7fc1; --red:#e8503a; --orange:#f5a623;
    --gold:#c8901b; --gold-lt:#ffd76e; --silver:#7d8996; --silver-lt:#dfe5ec;
    --green:#2fae6b; --ink:#1e2430; --paper:#fff8f0; --card:#fff; --muted:#7a8494;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:linear-gradient(180deg,#fff 0%,var(--paper) 45%,#f6e9d6 100%);color:var(--ink);min-height:100vh;}
  .wrap{max-width:900px;margin:0 auto;padding:32px 20px 56px;}
  .banner{text-align:center;margin-bottom:6px;}
  .pill{display:inline-block;background:var(--ink);color:#fff;font-weight:800;letter-spacing:.14em;font-size:11.5px;padding:6px 16px;border-radius:4px;transform:rotate(-1.5deg);text-transform:uppercase;}
  h1{font-size:clamp(32px,5.6vw,52px);font-weight:900;color:var(--blue);text-shadow:2px 2px 0 #d9e8f5;margin:12px 0 2px;letter-spacing:-.01em;}
  h1 .g{color:var(--gold);text-shadow:2px 2px 0 #f7e8c4;}
  .sub{font-weight:700;opacity:.72;margin-bottom:13px;font-size:14.5px;}
  .updated{display:inline-block;background:#fff;border:1px solid #eadfce;border-radius:20px;padding:5px 14px;font-size:12px;font-weight:700;color:var(--muted);}

  .notice{background:#fff;border-left:5px solid var(--orange);border-radius:12px;padding:16px 18px;margin:22px 0 4px;box-shadow:0 3px 14px rgba(30,36,48,.08);}
  .notice h4{font-size:12.5px;font-weight:900;text-transform:uppercase;letter-spacing:.07em;color:var(--red);margin-bottom:7px;}
  .notice p{font-size:14px;line-height:1.58;color:#3c4553;}
  .notice p+p{margin-top:9px;}
  .notice b{color:var(--ink);}

  .statgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:12px;margin:20px 0;}
  .stat{background:var(--card);border-radius:14px;padding:15px;text-align:center;box-shadow:0 3px 14px rgba(30,36,48,.08);}
  .stat .num{font-size:22px;font-weight:900;color:var(--blue-dark);}
  .stat.g .num{color:var(--gold);} .stat.s .num{color:var(--silver);}
  .stat .lbl{font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-top:4px;}

  .tierhead{display:flex;align-items:center;gap:12px;margin:32px 0 3px;}
  .tb{font-size:11px;font-weight:900;letter-spacing:.1em;text-transform:uppercase;padding:6px 13px;border-radius:20px;white-space:nowrap;}
  .tb.gold{background:linear-gradient(135deg,var(--gold-lt),var(--gold));color:#4d3800;}
  .tb.silver{background:linear-gradient(135deg,var(--silver-lt),var(--silver));color:#2f3740;}
  .tb.build{background:#e9edf2;color:#5d6773;}
  .tierhead .bar{flex:1;height:3px;background:linear-gradient(90deg,#e3cf9e,transparent);border-radius:2px;}
  .tiernote{font-size:12.5px;color:var(--muted);margin-bottom:11px;line-height:1.55;}
  .tiernote b{color:#4a5462;}

  .board{background:var(--card);border-radius:16px;box-shadow:0 4px 20px rgba(30,36,48,.10);overflow:hidden;}
  .row{display:flex;align-items:center;gap:13px;padding:14px 16px;border-bottom:1px solid #f0eee9;}
  .row:last-child{border-bottom:none;}
  .row.empty{justify-content:center;color:var(--muted);font-size:13.5px;font-weight:600;padding:20px;text-align:center;}
  .rank{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:15px;flex-shrink:0;background:#eef3f8;color:var(--blue-dark);}
  .r1 .rank{background:linear-gradient(135deg,var(--gold-lt),var(--gold));color:#4d3800;font-size:18px;}
  .r2 .rank{background:linear-gradient(135deg,#f0e4c4,#d9bd76);color:#4d3800;font-size:17px;}
  .who{flex:1;min-width:0;}
  .handle{font-weight:800;font-size:15px;}
  .handle .at{font-weight:600;color:var(--muted);font-size:12.5px;}
  .subline{font-size:11.5px;color:var(--muted);margin-top:2px;}
  .tr{margin-left:5px;font-weight:800;}
  .tr.up{color:var(--green);} .tr.down{color:var(--red);}
  .tr.flat,.tr.new{color:var(--muted);}
  .meter{height:6px;background:#eef1f5;border-radius:3px;margin-top:7px;overflow:hidden;}
  .meter i{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--blue-dark));border-radius:3px;}
  .r1 .meter i,.r2 .meter i{background:linear-gradient(90deg,var(--gold-lt),var(--gold));}
  .togo{font-size:11px;color:var(--muted);margin-top:4px;font-weight:600;}
  .togo.gold{color:var(--gold);font-weight:800;}
  .money{text-align:right;flex-shrink:0;}
  .gmv{font-weight:900;font-size:17px;}
  .gmvlbl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;}
  .morerow{padding:13px 16px;font-size:12.5px;color:var(--muted);text-align:center;font-weight:600;background:#fbfcfd;}

  .twocol{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:18px;}
  @media(max-width:640px){.twocol{grid-template-columns:1fr;}}
  .card{background:var(--card);border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(30,36,48,.10);}
  .card h3{font-size:13.5px;font-weight:900;text-transform:uppercase;letter-spacing:.06em;margin-bottom:11px;}
  .card.gc{border-top:4px solid var(--gold);} .card.gc h3{color:var(--gold);}
  .card.sc{border-top:4px solid var(--silver);} .card.sc h3{color:var(--silver);}
  .req{background:#fbf7ef;border-radius:10px;padding:10px 12px;font-size:13.5px;font-weight:800;margin-bottom:12px;}
  .req span{display:block;font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px;}
  .perks{list-style:none;font-size:13.5px;line-height:1.55;}
  .perks li{padding:6px 0 6px 21px;position:relative;border-bottom:1px dashed #eee7dc;}
  .perks li:last-child{border-bottom:none;}
  .perks li:before{content:'✓';position:absolute;left:0;font-weight:900;color:var(--green);}
  .perks li.no{color:var(--muted);}
  .perks li.no:before{content:'—';color:#c3ccd6;}

  footer{margin-top:30px;font-size:12px;color:var(--muted);line-height:1.65;text-align:center;}
  footer b{color:#5c6673;}
  .legal{margin-top:9px;font-size:11.5px;opacity:.85;}
"""

stat = lambda n, l, c='': f'<div class="stat {c}"><div class="num">{n}</div><div class="lbl">{l}</div></div>'
more = (f'<div class="morerow">+ {hidden} more VIP Live sellers under {m(SHOW_MIN)} this month — '
        f'keep going live and you\'ll show up here.</div>') if hidden else ''

build_html = board(shown_build, 'build', 'No sellers in this range this month.')
if hidden:
    build_html += f'<div class="board" style="margin-top:10px">{more}</div>'

doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Frost Buddy VIP Live — Tier Standings</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

  <div class="banner">
    <span class="pill">Frost Buddy VIP Live</span>
    <h1>TIER <span class="g">STANDINGS</span></h1>
    <div class="sub">Ranked by live GMV · {len(rows)} VIP Live sellers</div>
    <span class="updated">{PERIOD}</span>
  </div>

  <div class="notice">
    <h4>How tiers work — please read</h4>
    <p>Clearing a GMV line makes you <b>eligible for review</b>. It does not automatically place you in a tier.
       Gold and Silver are <b>capacity-limited</b> — we hold a set number of spots so that samples, China boxes and
       Live promotion actually mean something. Hitting the number gets you considered; it doesn't hand you the seat.</p>
    <p>Tiers are reviewed <b>monthly</b>. Tier is held on performance, so it can be earned — and it can be lost.</p>
  </div>

  <div class="statgrid">
    {stat(len(gold), f'clearing gold · {m(GOLD)}', 'g')}
    {stat(len(silver), f'clearing silver · {m(SILVER)}', 's')}
    {stat(len(build), 'building')}
    {stat(m(tot), 'VIP live GMV')}
    {stat(f'{hours:,.0f}', 'hours on air')}
  </div>

  <div class="tierhead"><span class="tb gold">Gold — Frost Buddy Elite</span><div class="bar"></div></div>
  <div class="tiernote">Line: <b>{m(GOLD)}+ live GMV in a month</b>. Small by design. These sellers have proven they
     convert traffic, which is why this is the tier Frost Buddy puts promotion behind.</div>
  {board(gold, 'gold', 'No one cleared the Gold line this month.')}

  <div class="tierhead"><span class="tb silver">Silver</span><div class="bar"></div></div>
  <div class="tiernote">Line: <b>{m(SILVER)}+ live GMV in a month</b>. Bar shows how far you are from Gold.</div>
  {board(silver, 'silver')}

  <div class="tierhead"><span class="tb build">Building</span><div class="bar"></div></div>
  <div class="tiernote">Going live, not yet at the Silver line. Bar shows distance to {m(SILVER)}.
     Sample support starts at Silver.</div>
  {build_html}

  <div class="twocol">
    <div class="card gc">
      <h3>Gold — Frost Buddy Elite</h3>
      <div class="req"><span>Line</span>{m(GOLD)}+ live GMV / month</div>
      <ul class="perks">
        <li>China boxes</li>
        <li>Frost Buddy promotes your Lives</li>
        <li>Priority samples</li>
        <li>Early access to drops</li>
        <li>Gold-only group chat</li>
      </ul>
    </div>
    <div class="card sc">
      <h3>Silver</h3>
      <div class="req"><span>Line</span>{m(SILVER)}+ live GMV / month</div>
      <ul class="perks">
        <li>Sample support</li>
        <li>Silver group chat</li>
        <li>Coupon codes for your audience</li>
        <li class="no">China boxes</li>
        <li class="no">Frost Buddy Live promotion</li>
        <li class="no">Early drop access</li>
      </ul>
    </div>
  </div>

  <footer>
    <p><b>Live GMV</b> is net of cancellations and returns, counting orders attributed to your TikTok LIVE
       sessions. Video and showcase sales are not counted — this board is Live only.</p>
    <p><b>$/hr</b> is live GMV divided by hours on air. It's here because converting beats clocking hours:
       a focused 90 minutes that sells is worth more than an eight-hour stream that doesn't.</p>
    <p class="legal">Figures may lag TikTok Shop by 1–2 days. Lines, perks and spot counts are set by
       Frost Buddy and can change.</p>
  </footer>

</div>
</body>
</html>
"""


open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'), 'w').write(doc)
print('wrote vip/index.html', len(doc), 'bytes')
print(f'gold={len(gold)} silver={len(silver)} building={len(build)} (shown {len(shown_build)}, hidden {hidden})')
