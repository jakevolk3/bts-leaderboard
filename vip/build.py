import json, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
PERIOD = "August 2026"

rows = json.load(open(os.path.join(HERE, 'data.json')))
rows.sort(key=lambda r: -r['aug'])

m = lambda v: f"${v:,.0f}"
e = lambda s: html.escape(str(s))

def line(r, i):
    rank = i + 1
    cls = f' r{rank}' if rank <= 3 else ''
    return (f'<div class="row{cls}">'
            f'<div class="rank">{rank}</div>'
            f'<div class="who">{e(r["name"])}<span class="at">@{e(r["handle"])}</span></div>'
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
  .r1,.r2,.r3{background:linear-gradient(90deg,#fffaf992,transparent);}
  .r1 .rank,.r2 .rank,.r3 .rank{color:var(--gold);font-size:19px;}
  .r1 .who,.r2 .who,.r3 .who{font-size:16px;font-weight:800;}
  .r1 .gmv,.r2 .gmv,.r3 .gmv{color:var(--gold);font-size:17px;}
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
  <p class="note">Live GMV only, net of returns. Updated {PERIOD}.</p>
</div>
</body>
</html>
"""

open(os.path.join(HERE, 'index.html'), 'w').write(doc)
print('wrote index.html', len(doc), 'bytes,', len(rows), 'sellers')
