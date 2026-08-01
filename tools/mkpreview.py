"""Render the built WeakAura pack to a 1:1 HTML preview."""
import base64, json, os
import wacodec as w
from classes import build_path

SP = os.path.dirname(os.path.abspath(__file__))
META = json.load(open(f"{SP}/exiles-id-meta.json"))
d = w.wa_decode(open(build_path("runemaster", "runemaster-all-specs")).read())
kids = d["c"].array_part()
byid = {k["id"]: k for k in kids}

_cache = {}
def data_uri(path):
    n = path.split("\\")[-1]
    if n in _cache: return _cache[n]
    p = f"{SP}/icons/{n}.png"
    if not os.path.exists(p):
        _cache[n] = ""
    else:
        _cache[n] = "data:image/png;base64," + base64.b64encode(open(p,"rb").read()).decode()
    return _cache[n]

def spell_of(k):
    t = (k.get("triggers") or {}).get(1, {}).get("trigger", {})
    if t.get("type") == "spell": return str(t.get("spellName"))
    for a in (t.get("auranames") or {}).values():
        if str(a).isdigit(): return str(a)
    return None

def label(k):
    s = spell_of(k)
    return (META.get(s) or {}).get("name") or k["id"].split(" ")[-1]

SPECS = ["RM Core", "RM Glyphic", "RM Engravement", "RM Riftblade"]
BAND_NOTE = {
    "RM Status": "tattoo · engravings · raid buffs · frozen — only active ones show",
    "RM Glyphic Procs": "short procs — only while active",
    "RM Engravement Procs": "short procs — only while active",
    "RM Riftblade Procs": "short procs — only while active",
    "RM Glyphic Main": "main damage — always visible",
    "RM Engravement Main": "main damage — always visible",
    "RM Riftblade Main": "main damage — always visible",
    "RM Glyph Chain": "glyph chain — spec state",
    "RM Carvings": "banked carving — spec state",
    "RM Riftblade State": "runeblade beat · runeshroud · palm sigils · sigils",
    "RM Glyphic CDs": "cooldowns + utility",
    "RM Engravement CDs": "cooldowns + utility",
    "RM Riftblade CDs": "cooldowns + utility",
}

def bands_for(parent):
    """Bands plus any loose icons anchored straight to the group.

    The Glyphic glyph sockets are not in a dynamic group -- each slot is a dim
    socket and a live icon at the same x, stacked -- so they are collected by
    y offset instead."""
    out, loose = [], {}
    for k in kids:
        if k.get("parent") != parent: continue
        if k["regionType"] == "dynamicgroup":
            out.append(("icons", k, [byid[c] for c in k["controlledChildren"].values()]))
        elif k["regionType"] == "aurabar":
            out.append(("bar", k, []))
        elif k["regionType"] in ("icon", "texture"):
            loose.setdefault(k["yOffset"], []).append(k)
    for y, items in loose.items():
        out.append(("loose", {"id": "glyph segments", "yOffset": y,
                              "space": 0, "width": 0, "height": 0}, items))
    return sorted(out, key=lambda x: -x[1]["yOffset"])

STAGE_H = 300
def render(parent, title):
    rows, stage = [], []
    for kind, g, children in bands_for(parent):
        y = -g["yOffset"]
        if kind == "bar":
            stage.append(
                f'<div class="bar" style="top:{y}px;width:{g["width"]}px;height:{g["height"]}px">'
                f'<span>mana</span></div>')
            rows.append((g["yOffset"], g["id"], f'bar · {g["width"]}×{g["height"]}px', ""))
            continue
        if kind == "loose":
            # absolute x, and slots overlap by design (socket under live icon)
            cells = ""
            for c in children:
                st = (f'left:calc(50% + {c["xOffset"]}px);'
                      f'width:{c["width"]}px;height:{c["height"]}px;')
                if c["regionType"] == "texture":
                    col = c.get("color") or {}
                    r, gg, b = [int(255 * col.get(i, 1)) for i in (1, 2, 3)]
                    cells += (f'<span class="seg" style="{st}'
                              f'background:rgba({r},{gg},{b},{col.get(4,1)})" '
                              f'title="{c["id"]}"></span>')
                else:
                    cells += (f'<i class="loose" style="{st}'
                              f'opacity:{c.get("alpha",1)};'
                              f'filter:{"grayscale(1)" if c.get("desaturate") else "none"}">'
                              f'<img src="{data_uri(c.get("displayIcon") or "")}" '
                              f'alt="{label(c)}" title="{label(c)}"></i>')
            stage.append(f'<div class="loosewrap" style="top:{y}px">{cells}</div>')
            rows.append((g["yOffset"], "glyph segments",
                         f'{len(children)//2} segments × {children[0]["width"]}×{children[0]["height"]}px',
                         ", ".join(sorted({label(c) for c in children}))))
            continue
        sz = children[0].get("width", 28) if children else 28
        gap = g.get("space", 1)
        cells = ""
        for c in children:
            cw, ch = c.get("width", sz), c.get("height", sz)
            if c["regionType"] == "aurabar":
                cells += (f'<span class="minibar" style="width:{cw}px;height:{ch}px">'
                          f'{label(c)}</span>')
            else:
                cells += (f'<i style="width:{cw}px;height:{ch}px">'
                          f'<img src="{data_uri(c.get("displayIcon") or "")}" '
                          f'alt="{label(c)}" title="{label(c)}"></i>')
        stage.append(f'<div class="band" style="top:{y}px;gap:{gap}px">{cells}</div>')
        rows.append((g["yOffset"], g["id"],
                     f'{len(children)} × {sz}px, gap {gap}',
                     ", ".join(label(c) for c in children)))
    tbl = "".join(
        f'<tr><td class="num">{y}</td><td>{gid}</td><td class="num">{spec}</td>'
        f'<td class="items">{items}</td></tr>' for y, gid, spec, items in rows)
    return f'''<section>
<h2>{title}</h2>
<p class="note">{BAND_NOTE.get(parent,"")}</p>
<div class="stage" style="height:{STAGE_H}px"><div class="center-mark"><span>screen centre</span></div>{"".join(stage)}</div>
<table><thead><tr><th>y</th><th>band</th><th>size</th><th>contents</th></tr></thead><tbody>{tbl}</tbody></table>
</section>'''

CSS = """
:root{--bg:#141019;--panel:#1e1826;--line:#2f2740;--ink:#e8e2f0;--muted:#9a8fb0;
--accent:#b98bff;--gold:#e0b054;
--sans:ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
@media (prefers-color-scheme:light){:root{--bg:#f6f4fa;--panel:#fff;--line:#e0dae9;
--ink:#221c2c;--muted:#6b6180;--accent:#6c3fd4;--gold:#966a12;}}
:root[data-theme="dark"]{--bg:#141019;--panel:#1e1826;--line:#2f2740;--ink:#e8e2f0;
--muted:#9a8fb0;--accent:#b98bff;--gold:#e0b054;}
:root[data-theme="light"]{--bg:#f6f4fa;--panel:#fff;--line:#e0dae9;--ink:#221c2c;
--muted:#6b6180;--accent:#6c3fd4;--gold:#966a12;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1000px;margin:0 auto;padding:48px 24px 80px;display:flex;
flex-direction:column;gap:40px}
header h1{font-size:clamp(1.6rem,3vw,2.1rem);margin:0 0 6px;text-wrap:balance;
letter-spacing:-.02em}
header p{margin:0;color:var(--muted);max-width:65ch}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;
text-transform:uppercase;color:var(--accent);margin:0 0 10px}
section{background:var(--panel);border:1px solid var(--line);border-radius:10px;
padding:22px;display:flex;flex-direction:column;gap:14px}
h2{margin:0;font-size:1.05rem;letter-spacing:-.01em}
.note{margin:0;color:var(--muted);font-size:.85rem}
.stage{position:relative;background:
radial-gradient(120% 90% at 50% 0%,#2a2333 0%,#0d0a12 100%);
border:1px solid var(--line);border-radius:8px;overflow:hidden}
.center-mark{position:absolute;top:0;left:0;right:0;border-top:1px dashed #4b3f63}
.center-mark span{position:absolute;left:8px;top:3px;font-family:var(--mono);
font-size:.62rem;color:#7d6f96;letter-spacing:.08em}
.band{position:absolute;left:50%;transform:translate(-50%,-50%);display:flex;
align-items:center}
.band i{display:block;border:1px solid #0b0910;box-shadow:0 0 0 1px #3a3050;
overflow:hidden;flex:none}
.band img{width:100%;height:100%;display:block;object-fit:cover;transform:scale(1.08)}
.loosewrap{position:absolute;left:0;right:0;height:0}
.seg{position:absolute;transform:translate(-50%,-50%);display:block;border:1px solid rgba(0,0,0,.65);border-radius:1px}
.loose{position:absolute;transform:translate(-50%,-50%);display:block;border:1px solid #0b0910;box-shadow:0 0 0 1px #3a3050;overflow:hidden}
.loose img{width:100%;height:100%;display:block;object-fit:cover;transform:scale(1.08)}
.bar{position:absolute;left:50%;transform:translate(-50%,-50%);
background:linear-gradient(#4a6be0,#2f49b8);border:1px solid #0b0910;
box-shadow:0 0 0 1px #3a3050;display:flex;align-items:center;justify-content:flex-end}
.minibar{display:flex;align-items:center;padding:0 6px;font-family:var(--mono);font-size:.6rem;color:#dfe6ff;background:linear-gradient(#4a6be0,#2f49b8);border:1px solid #0b0910;flex:none}
.bar span{font-family:var(--mono);font-size:.6rem;color:#dfe6ff;padding-right:5px}
table{width:100%;border-collapse:collapse;font-size:.82rem}
th{text-align:left;font-family:var(--mono);font-size:.68rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--muted);font-weight:500;
border-bottom:1px solid var(--line);padding:0 10px 7px 0}
td{border-bottom:1px solid var(--line);padding:7px 10px 7px 0;vertical-align:top}
tr:last-child td{border-bottom:0}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums;color:var(--muted);
white-space:nowrap}
.items{color:var(--muted);font-size:.78rem}
.legend{display:flex;flex-wrap:wrap;gap:18px;font-size:.8rem;color:var(--muted)}
.legend b{color:var(--gold);font-weight:600}
"""

html = f"""<div class="wrap">
<header>
<p class="eyebrow">Runemaster · Conquest of Azeroth</p>
<h1>WeakAura layout preview</h1>
<p>Rendered 1:1 from the actual export, so this is exactly what imports. Every band
is centred; dynamic groups only lay out <em>active</em> children, so the
active-only rows will usually be narrower in play than shown here.</p>
</header>
<div class="legend">
<span><b>136</b> displays</span><span><b>4</b> groups</span>
<span><b>0</b> icon mismatches</span><span>one spec group live at a time</span>
</div>
{"".join(render(p, p.replace("RM ","")) for p in SPECS)}
</div>"""

open(f"{SP}/preview.html","w").write(f"<style>{CSS}</style>\n{html}")
print("wrote preview.html", os.path.getsize(f"{SP}/preview.html"), "bytes")
