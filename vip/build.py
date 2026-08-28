import json, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
PERIOD = "August 2026"
GOLD, SILVER = 30000, 5000

rows = json.load(open(os.path.join(HERE, 'data.json')))
rows.sort(key=lambda r: -r['aug'])

m = lambda v: f"${v:,.0f}"
e = lambda s: html.escape(str(s))

def tier(v):
    if v >= GOLD:
        return 'gold', 'Gold'
    if v >= SILVER:
        return 'silver', 'Silver'
    return '', ''

def line(r, i):
    rank = i + 1
    tcls, tname = tier(r['aug'])
    badge = f'<span class="badge {tcls}">{tname}</span>' if tname else ''
    return (f'<div class="row {tcls}">'
            f'<div class="rank">{rank}</div>'
            f'<div class="who">{e(r["name"])}<span class="at">@{e(r["handle"])}</span></div>'
            f'{badge}'
            f'<div class="gmv">{m(r["aug"])}</div>'
            f'</div>')

CSS = """
  :root{--blue:#4da3e0;--gold:#c8901b;--gold-lt:#ffd76e;--ink:#1e2430;--paper:#fff8f0;--muted:#7a8494;}
  *{margin:0;padding:0;box-sizing:border-box;}
  body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
       background:linear-gradient(180deg,#fff 0%,var(--paper) 60%,#f6e9d6 100%);
       color:var(--ink);min-height:100vh;}
  .wrap{max-width:620px;margin:0 auto;padding:38px 18px 56px;}
  h1{text-align:center;font-size:clamp(30px,7vw,46px);font-weight:900;color:var(--blue);
     text-shadow:2px 2px 0 #d9e8f5;letter-spacing:-.01em;line-height:1.05;}
  h1 span{color:var(--gold);text-shadow:2px 2px 0 #f7e8c4;}
  .when{text-align:center;font-size:13px;font-weight:700;color:var(--muted);
        text-transform:uppercase;letter-spacing:.1em;margin:9px 0 24px;}
  .board{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 22px rgba(30,36,48,.11);}
  .row{display:flex;align-items:center;gap:14px;padding:13px 18px;border-bottom:1px solid #f2f0ec;}
  .row:last-child{border-bottom:none;}
  .rank{width:30px;font-weight:900;font-size:15px;color:var(--muted);flex-shrink:0;text-align:center;}
  .who{flex:1;min-width:0;font-weight:700;font-size:15px;
       overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .at{color:var(--muted);font-weight:600;font-size:12.5px;margin-left:7px;}
  .gmv{font-weight:900;font-size:16px;flex-shrink:0;font-variant-numeric:tabular-nums;}
  .badge{font-size:9.5px;font-weight:900;letter-spacing:.09em;text-transform:uppercase;
         padding:3px 9px;border-radius:20px;flex-shrink:0;}
  .badge.gold{background:linear-gradient(135deg,var(--gold-lt),var(--gold));color:#4d3800;}
  .badge.silver{background:linear-gradient(135deg,#dfe5ec,#a9b4c0);color:#2f3740;}
  .row.gold{background:linear-gradient(90deg,#fff8e8,transparent);}
  .row.gold .rank,.row.gold .gmv{color:var(--gold);}
  .row.gold .who{font-weight:800;}
  .row.silver{background:linear-gradient(90deg,#f7f9fb,transparent);}
  .note{text-align:center;font-size:11.5px;color:var(--muted);margin-top:16px;line-height:1.6;}
  @media(max-width:420px){
    .at{display:block;margin:1px 0 0;}
    .row{padding:11px 14px;gap:10px;}
  }
"""

doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Frost Buddy VIP Live — Scoreboard</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <h1>VIP LIVE <span>SCOREBOARD</span></h1>
  <div class="when">{PERIOD} &middot; Live GMV</div>
  <div class="board">
{chr(10).join('    ' + line(r, i) for i, r in enumerate(rows))}
  </div>
  <p class="note">Gold {m(GOLD)}+ &middot; Silver {m(SILVER)}+ &middot; live GMV, net of returns.<br>
     Clearing a line makes you eligible for review &mdash; spots are limited.</p>
</div>
</body>
</html>
"""

open(os.path.join(HERE, 'index.html'), 'w').write(doc)
print('wrote index.html', len(doc), 'bytes,', len(rows), 'sellers')
