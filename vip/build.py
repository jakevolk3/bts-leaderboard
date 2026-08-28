import json, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
PERIOD = "August 2026"
GOLD, SILVER = 30000, 5000

rows = json.load(open(os.path.join(HERE, 'data.json')))
rows.sort(key=lambda r: -r['aug'])

m = lambda v: f"${v:,.0f}"
e = lambda s: html.escape(str(s))

def tier(v):
    return ('gold', 'Gold') if v >= GOLD else (('silver', 'Silver') if v >= SILVER else ('', ''))

def line(r, i):
    rank = i + 1
    tcls, tname = tier(r['aug'])
    badge = f'<span class="badge">{tname}</span>' if tname else ''
    return (f'<li class="row {tcls}" style="--i:{i}">'
            f'<span class="rank">{rank}</span>'
            f'<span class="who"><b>{e(r["name"])}</b><i>@{e(r["handle"])}</i></span>'
            f'{badge}'
            f'<span class="gmv">{m(r["aug"])}</span>'
            f'</li>')

CSS = """
  @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800;900&display=swap');
  :root{
    --bg:#0a0e17; --card:#131a28; --line:#1f2a3d;
    --txt:#eef3fa; --dim:#7d8ba3;
    --blue:#4da3e0; --gold:#f5c451; --gold-d:#c8901b; --silver:#c3ccd8;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  body{
    font-family:'Archivo','Segoe UI',system-ui,-apple-system,sans-serif;
    background:var(--bg);color:var(--txt);min-height:100vh;
    -webkit-font-smoothing:antialiased;
  }
  body:before{
    content:'';position:fixed;inset:0;pointer-events:none;
    background:
      radial-gradient(60vw 40vh at 15% -5%, rgba(77,163,224,.20), transparent 65%),
      radial-gradient(55vw 38vh at 88% 6%, rgba(245,196,81,.14), transparent 62%),
      radial-gradient(70vw 45vh at 50% 105%, rgba(232,80,58,.10), transparent 70%);
  }
  .wrap{position:relative;max-width:660px;margin:0 auto;padding:46px 16px 64px;}

  header{text-align:center;margin-bottom:26px;}
  .live{
    display:inline-flex;align-items:center;gap:7px;font-size:10.5px;font-weight:800;
    letter-spacing:.18em;text-transform:uppercase;color:var(--dim);
    border:1px solid var(--line);border-radius:100px;padding:5px 14px;margin-bottom:16px;
  }
  .dot{width:6px;height:6px;border-radius:50%;background:#2fae6b;
       box-shadow:0 0 0 0 rgba(47,174,107,.7);animation:pulse 2.2s infinite;}
  @keyframes pulse{70%{box-shadow:0 0 0 7px rgba(47,174,107,0);}100%{box-shadow:0 0 0 0 rgba(47,174,107,0);}}
  h1{
    font-size:clamp(38px,9.5vw,68px);font-weight:900;line-height:.92;
    letter-spacing:-.035em;text-transform:uppercase;
  }
  h1 .a{background:linear-gradient(180deg,#8fd0ff,#3d8fd0);-webkit-background-clip:text;
        background-clip:text;color:transparent;}
  h1 .b{background:linear-gradient(180deg,#ffe9a8,#d99a20);-webkit-background-clip:text;
        background-clip:text;color:transparent;}
  .when{margin-top:11px;font-size:11.5px;font-weight:700;letter-spacing:.2em;
        text-transform:uppercase;color:var(--dim);}

  ol{list-style:none;display:flex;flex-direction:column;gap:7px;}
  .row{
    display:flex;align-items:center;gap:13px;
    background:linear-gradient(100deg,var(--card),#111826);
    border:1px solid var(--line);border-radius:13px;padding:13px 16px;
    animation:in .5s both;animation-delay:calc(var(--i)*22ms);
  }
  @keyframes in{from{opacity:0;transform:translateY(9px);}to{opacity:1;transform:none;}}
  @media(prefers-reduced-motion:reduce){.row{animation:none;}.dot{animation:none;}}

  .rank{
    width:30px;flex-shrink:0;text-align:center;
    font-size:16px;font-weight:800;color:var(--dim);font-variant-numeric:tabular-nums;
  }
  .who{flex:1;min-width:0;display:flex;flex-direction:column;gap:1px;}
  .who b{font-size:15px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .who i{font-style:normal;font-size:11.5px;font-weight:600;color:var(--dim);
         overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .gmv{font-size:17px;font-weight:800;flex-shrink:0;font-variant-numeric:tabular-nums;
       letter-spacing:-.02em;}
  .badge{
    font-size:9px;font-weight:900;letter-spacing:.11em;text-transform:uppercase;
    padding:4px 10px;border-radius:100px;flex-shrink:0;
  }

  /* Gold */
  .row.gold{
    border-color:rgba(245,196,81,.38);
    background:linear-gradient(100deg,rgba(245,196,81,.13),rgba(245,196,81,.02) 42%,var(--card));
    box-shadow:0 0 26px -8px rgba(245,196,81,.35);
  }
  .row.gold .rank,.row.gold .gmv{color:var(--gold);}
  .row.gold .who b{font-size:16.5px;font-weight:900;}
  .row.gold .badge{
    background:linear-gradient(135deg,#ffe9a8,var(--gold),#b8830f);color:#3a2900;
    box-shadow:0 1px 8px rgba(245,196,81,.4);
  }
  /* Silver */
  .row.silver{border-color:rgba(195,204,216,.20);}
  .row.silver .badge{background:linear-gradient(135deg,#eef2f7,#aab5c4);color:#1b2331;}
  .row.silver .gmv{color:#dbe4ef;}

  .note{
    margin-top:24px;text-align:center;font-size:11.5px;line-height:1.75;
    color:var(--dim);font-weight:600;
  }
  .note b{color:var(--gold);font-weight:800;}
  .note s{color:var(--silver);text-decoration:none;font-weight:800;}

  @media(max-width:430px){
    .wrap{padding:34px 11px 48px;}
    .row{padding:11px 12px;gap:9px;border-radius:11px;}
    .rank{width:21px;font-size:14px;}
    .who b{font-size:13.5px;} .who i{font-size:10.5px;}
    .gmv{font-size:15px;}
    .badge{font-size:8px;padding:3px 7px;letter-spacing:.07em;}
    .row.gold .who b{font-size:14.5px;}
  }
"""

doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0a0e17">
<title>Frost Buddy VIP Live — Scoreboard</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="live"><span class="dot"></span>Frost Buddy VIP Live</div>
    <h1><span class="a">VIP LIVE</span><br><span class="b">SCOREBOARD</span></h1>
    <div class="when">{PERIOD} &middot; Live GMV</div>
  </header>
  <ol>
{chr(10).join('    ' + line(r, i) for i, r in enumerate(rows))}
  </ol>
  <p class="note">
    <b>Gold {m(GOLD)}+</b> &nbsp;&middot;&nbsp; <s>Silver {m(SILVER)}+</s><br>
    Live GMV only, net of returns. Clearing a line makes you eligible for review — spots are limited.
  </p>
</div>
</body>
</html>
"""

open(os.path.join(HERE, 'index.html'), 'w').write(doc)
print('wrote index.html', len(doc), 'bytes,', len(rows), 'sellers')
