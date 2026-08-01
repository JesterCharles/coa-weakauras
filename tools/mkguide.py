"""Render an annotated layout guide for the Runemaster pack.

Every band is drawn 1:1 from the actual export and labelled, so the page can be
shared as "here is how to read this WeakAura".
"""
import base64
import json
import os
import re

import wacodec as w
from classes import build_path

SP = os.path.dirname(os.path.abspath(__file__))
META = json.load(open(f"{SP}/exiles-id-meta.json"))
d = w.wa_decode(open(build_path("runemaster", "runemaster-all-specs")).read())
KIDS = d["c"].array_part()
BY = {k["id"]: k for k in KIDS}

_cache = {}


def uri(path):
    n = path.split("\\")[-1]
    if n not in _cache:
        p = f"{SP}/icons/{n}.png"
        _cache[n] = ("data:image/png;base64,"
                     + base64.b64encode(open(p, "rb").read()).decode()
                     if os.path.exists(p) else "")
    return _cache[n]


def spell_of(k):
    t = (k.get("triggers") or {}).get(1, {}).get("trigger", {})
    if t.get("type") == "spell":
        return str(t.get("spellName"))
    for a in (t.get("auranames") or {}).values():
        if str(a).isdigit():
            return str(a)
    return None


def label_of(k):
    s = spell_of(k)
    nm = (META.get(s) or {}).get("name")
    if nm:
        return nm
    i = k["id"]
    for pre in (" Offense ", " Utility ", " Buffs ", " Main ", " DoTs ",
                "RM Short ", "RM Status ", "RM Tattoo ", "RM Engraving ",
                "RM Raid "):
        if pre in i:
            return i.split(pre)[-1]
    return i.replace("RM ", "")


# band id -> (short name, what it is for). Keys are matched exactly or as a
# trailing word, never as a loose prefix.
BANDS = [
    ("RM Alerts", "Reminders",
     "Only appear when something is missing. Names the hand for engravings."),
    ("Buffs", "Buffs, debuffs and procs",
     "Everything currently up: procs, running cooldowns, your own buffs and "
     "your target's debuffs. Active-only, so it packs to whatever is live."),
    ("Main", "Main damage",
     "Your core rotation. Largest icons, always visible."),
    ("Mana", "Resource",
     "Mana. Exactly the width of the main row above it."),
    ("RM Glyph", "Glyph bar",
     "Glyphic only. Frost / Flame / Arcane, dim until you build them."),
    ("Offense", "Offensive cooldowns",
     "Damage cooldowns. Ley Lock and Leyline Adjustment are always last."),
    ("Utility", "Defensive + utility",
     "Defensives first, then utility, then your two on-use trinkets."),
    ("RM Longterm", "Long-term buffs",
     "Tattoo, weapon engravings and raid auras. Set and forget."),
]


BANDS_D = [(k, d) for k, _, d in BANDS]


def band_meta(region):
    bid = region["id"] if isinstance(region, dict) else region
    if isinstance(region, dict) and region.get("regionType") == "texture":
        return "Glyph bar", dict(BANDS_D).get("RM Glyph", "")
    for key, name, desc in BANDS:
        if bid == key or bid.endswith(" " + key):
            return name, desc
    return bid, ""


def height(k):
    if k["regionType"] == "aurabar":
        return k["height"]
    if k["regionType"] == "dynamicgroup":
        ch = [BY[c] for c in k["controlledChildren"].values()]
        return max(c.get("height", 0) for c in ch) if ch else 0
    return k.get("height", 0)


def bands_for(spec):
    out = []
    seen = set()
    for k in KIDS:
        if k.get("parent") not in ("RM Core", spec):
            continue
        if k["regionType"] == "dynamicgroup":
            out.append((k, [BY[c] for c in k["controlledChildren"].values()]))
        elif k["regionType"] == "aurabar":
            out.append((k, []))
        elif k["regionType"] == "texture":
            key = round(k["yOffset"])
            if key in seen:
                continue
            seen.add(key)
            segs = [x for x in KIDS if x["regionType"] == "texture"
                    and round(x["yOffset"]) == key
                    and x.get("parent") == spec]
            out.append((k, segs))
    return sorted(out, key=lambda x: -x[0]["yOffset"])


TOP = 8


def render(spec, title, blurb):
    rows, stage = [], []
    for g, children in bands_for(spec):
        y = -g["yOffset"] + TOP
        h = height(g)
        name, desc = band_meta(g)
        if g["regionType"] == "aurabar" and not children:
            stage.append(f'<div class="bar" style="top:{y}px;'
                         f'width:{g["width"]}px;height:{h}px"></div>')
        elif g["regionType"] == "texture":
            for c in children:
                col = c.get("color") or {}
                r, gg, b = [int(255 * col.get(i, 1)) for i in (1, 2, 3)]
                stage.append(
                    f'<span class="seg" style="top:{y}px;'
                    f'left:calc(50% + {c["xOffset"]}px);width:{c["width"]}px;'
                    f'height:{c["height"]}px;'
                    f'background:rgba({r},{gg},{b},{col.get(4, 1)})"></span>')
        else:
            cap = MAX_SHOWN.get(name)
            shown = children[:cap] if cap else children
            cells = "".join(
                f'<i style="width:{c.get("width", 26)}px;'
                f'height:{c.get("height", 26)}px">'
                f'<img src="{uri(c.get("displayIcon") or "")}" '
                f'alt="{label_of(c)}" title="{label_of(c)}"></i>'
                for c in shown)
            if cap and len(children) > cap:
                cells += (f'<span class="more" '
                          f'style="height:{shown[0].get("height", 26)}px">'
                          f'+{len(children) - cap}</span>')
            stage.append(f'<div class="band" style="top:{y}px;'
                         f'gap:{g.get("space", 2)}px">{cells}</div>')
        stage.append(f'<div class="tag" style="top:{y}px">{name}</div>')
        labels = list(dict.fromkeys(label_of(c) for c in children))
        cap = MAX_SHOWN.get(name)
        if cap and len(labels) > cap:
            items = ", ".join(labels[:cap]) + f" &hellip; +{len(labels) - cap} more"
        else:
            items = ", ".join(labels)
        rows.append((name, desc, items or "&mdash;", len(children)))

    tbl = "".join(
        f"<tr><td class='b'>{n}</td><td>{de}</td>"
        f"<td class='num'>{c or ''}</td><td class='items'>{it}</td></tr>"
        for n, de, it, c in rows)
    return f"""<section>
<h2>{title}</h2>
<p class="blurb">{blurb}</p>
<div class="stage">{"".join(stage)}</div>
<div class="scroll"><table>
<thead><tr><th>Band</th><th>What it is</th><th>#</th><th>Contents</th></tr></thead>
<tbody>{tbl}</tbody></table></div>
</section>"""


CSS = """
:root{--bg:#141019;--panel:#1e1826;--line:#2f2740;--ink:#e8e2f0;--muted:#9a8fb0;
--accent:#b98bff;--gold:#e0b054;
--sans:ui-sans-serif,system-ui,"Segoe UI",Helvetica,Arial,sans-serif;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
@media (prefers-color-scheme:light){:root{--bg:#f6f4fa;--panel:#fff;--line:#e0dae9;
--ink:#221c2c;--muted:#6b6180;--accent:#6c3fd4;--gold:#8a6210;}}
:root[data-theme="dark"]{--bg:#141019;--panel:#1e1826;--line:#2f2740;--ink:#e8e2f0;
--muted:#9a8fb0;--accent:#b98bff;--gold:#e0b054;}
:root[data-theme="light"]{--bg:#f6f4fa;--panel:#fff;--line:#e0dae9;--ink:#221c2c;
--muted:#6b6180;--accent:#6c3fd4;--gold:#8a6210;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1040px;margin:0 auto;padding:44px 22px 80px;display:flex;
flex-direction:column;gap:34px}
.eyebrow{font-family:var(--mono);font-size:.7rem;letter-spacing:.15em;
text-transform:uppercase;color:var(--accent);margin:0 0 8px}
h1{font-size:clamp(1.6rem,3vw,2.1rem);margin:0 0 8px;letter-spacing:-.02em;
text-wrap:balance}
header p{margin:0;color:var(--muted);max-width:66ch}
section{background:var(--panel);border:1px solid var(--line);border-radius:10px;
padding:20px;display:flex;flex-direction:column;gap:12px}
h2{margin:0;font-size:1.05rem;letter-spacing:-.01em}
.blurb{margin:0;color:var(--muted);font-size:.86rem;max-width:66ch}
.stage{position:relative;height:400px;border:1px solid var(--line);
border-radius:8px;overflow:hidden;
background:radial-gradient(120% 80% at 50% 0%,#2b2435 0%,#0c0a11 100%)}
.band{position:absolute;left:50%;transform:translate(-50%,-50%);display:flex;
align-items:center}
.tmpl b{display:block;background:linear-gradient(#4a4160,#2a2438);border:1px solid #0b0910;box-shadow:0 0 0 1px #4a3f68;flex:none}\n.bar.tmpl{background:linear-gradient(#4a6be0,#2f49b8)}\n.seg.tmpl{background:rgba(185,139,255,.35)}\n.tmplsec{border-color:var(--accent)}\n.band i{display:block;border:1px solid #0b0910;box-shadow:0 0 0 1px #3d3356;
overflow:hidden;flex:none}
.band img{width:100%;height:100%;display:block;object-fit:cover;
transform:scale(1.08)}
.bar{position:absolute;left:50%;transform:translate(-50%,-50%);
background:linear-gradient(#4a6be0,#2f49b8);border:1px solid #0b0910;
box-shadow:0 0 0 1px #3d3356}
.more{display:flex;align-items:center;padding:0 8px;font-family:var(--mono);font-size:.68rem;color:var(--muted);background:rgba(255,255,255,.05);border:1px dashed #4a3f68;border-radius:3px;flex:none}
.seg{position:absolute;transform:translate(-50%,-50%);display:block;
border:1px solid rgba(0,0,0,.6)}
.tag{position:absolute;left:10px;transform:translateY(-50%);
font-family:var(--mono);font-size:.62rem;letter-spacing:.07em;
text-transform:uppercase;color:var(--gold);background:rgba(10,8,14,.72);
border:1px solid #3d3356;border-radius:3px;padding:2px 6px;white-space:nowrap}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:.82rem;min-width:560px}
th{text-align:left;font-family:var(--mono);font-size:.66rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--muted);font-weight:500;
border-bottom:1px solid var(--line);padding:0 10px 7px 0}
td{border-bottom:1px solid var(--line);padding:7px 10px 7px 0;
vertical-align:top}
tr:last-child td{border-bottom:0}
td.b{font-weight:600;white-space:nowrap}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums;
color:var(--muted)}
.items{color:var(--muted);font-size:.78rem}
.note{background:var(--panel);border:1px solid var(--line);border-left:3px solid
var(--gold);border-radius:8px;padding:16px 18px}
.note h3{margin:0 0 6px;font-size:.92rem}
.note p{margin:0 0 8px;color:var(--muted);font-size:.85rem;max-width:70ch}
.note p:last-child{margin:0}
"""

# ---- universal template ---------------------------------------------------
# Rendered from the real Glyphic build rather than an abstract schematic: it is
# the spec that exercises every band, including the secondary resource, so it
# doubles as the template other classes are measured against.
# In the template view the band is named for its ROLE, not for what
# Runemaster happens to put there.
GENERIC = {"Glyph bar": "Secondary resource"}

# The buff row can hold ~27 entries, but it is active-only and in play shows a
# handful. Drawing all of them makes the diagram unreadable and misrepresents
# how it looks, so cap it and say how many were left out.
MAX_SHOWN = {"Buffs, debuffs and procs": 8}

TEMPLATE_ROLES = {
    "Reminders": "Only when something is missing &mdash; imbues, consumables, "
                 "a dropped self-buff.",
    "Buffs, debuffs and procs": "Everything currently up. Active-only, so it "
                                "packs to whatever is live.",
    "Main damage": "The core rotation. Always visible, largest icons. Glows "
                   "when a proc says to press it.",
    "Resource": "Primary resource. Width locked to the main row above it.",
    "Secondary resource": "<b>Glyphs here; combo points, runes or essences "
                          "for other classes.</b> Omit the band if the class has "
                          "none, and everything below shifts up.",
    "Offensive cooldowns": "Damage cooldowns, most-pressed first. Interrupt "
                           "and mobility pinned to the end.",
    "Defensive + utility": "Defensives, then utility, then on-use trinkets.",
    "Long-term buffs": "Stances, hour-long imbues, raid auras. Checked once "
                       "per pull.",
}


def render_template():
    stage, rows = [], []
    for g, children in bands_for("RM Glyphic"):
        y = -g["yOffset"] + TOP
        h = height(g)
        name, _ = band_meta(g)
        name = GENERIC.get(name, name)
        if g["regionType"] == "aurabar" and not children:
            stage.append(f'<div class="bar" style="top:{y}px;'
                         f'width:{g["width"]}px;height:{h}px"></div>')
        elif g["regionType"] == "texture":
            for c in children:
                col = c.get("color") or {}
                r, gg, b = [int(255 * col.get(i, 1)) for i in (1, 2, 3)]
                stage.append(
                    f'<span class="seg" style="top:{y}px;'
                    f'left:calc(50% + {c["xOffset"]}px);width:{c["width"]}px;'
                    f'height:{c["height"]}px;'
                    f'background:rgba({r},{gg},{b},{col.get(4, 1)})"></span>')
        else:
            cap = MAX_SHOWN.get(name)
            shown = children[:cap] if cap else children
            cells = "".join(
                f'<i style="width:{c.get("width", 26)}px;'
                f'height:{c.get("height", 26)}px">'
                f'<img src="{uri(c.get("displayIcon") or "")}" alt=""></i>'
                for c in shown)
            if cap and len(children) > cap:
                cells += (f'<span class="more" '
                          f'style="height:{shown[0].get("height", 26)}px">'
                          f'+{len(children) - cap}</span>')
            stage.append(f'<div class="band" style="top:{y}px;'
                         f'gap:{g.get("space", 2)}px">{cells}</div>')
        stage.append(f'<div class="tag" style="top:{y}px">{name}</div>')
        rows.append((name, f"y {g['yOffset']:.0f}",
                     f"{max((c.get('height', 0) for c in children), default=h)}px",
                     TEMPLATE_ROLES.get(name, "")))
    tbl = "".join(f"<tr><td class='b'>{n}</td><td class='num'>{p}</td>"
                  f"<td class='num'>{sz}</td><td>{de}</td></tr>"
                  for n, p, sz, de in rows)
    return f"""<section class="tmplsec">
<h2>The template &mdash; every class pack follows this</h2>
<p class="blurb">Band order, sizes and spacing are fixed across all 21 Conquest
of Azeroth classes, so a player who learns one pack can read any of them. Only
the <em>contents</em> change. Shown here as Glyphic, because it is the spec that
uses every band including the secondary resource.</p>
<div class="stage">{"".join(stage)}</div>
<div class="scroll"><table>
<thead><tr><th>Band</th><th>Anchor</th><th>Icon</th><th>Role in the template</th>
</tr></thead><tbody>{tbl}</tbody></table></div>
</section>

<div class="note">
<h3>Rules that hold for every class</h3>
<p><strong>Everything is centred.</strong> Dynamic groups grow horizontally from
the centre, never from an edge, so rows of different lengths stay aligned with
the resource bar and with each other.</p>
<p><strong>The resource bar is exactly as wide as the main row</strong>, derived
from that row's icon count rather than set by hand, so the two cannot drift.</p>
<p><strong>Two resources is the common case.</strong> Glyphic pairs mana with a
three-segment glyph bar; Chronomancer's Artificer pairs mana with combo points.
That band is the slot for whatever the class's second currency is.</p>
<p><strong>Cooldown rows escalate as they come back:</strong> the timer appears
at 20s, the icon glows at 10s, and the glow turns urgent at 5s. The main damage
row is exempt &mdash; those sit on 6-8s cooldowns, so the number is simply
always shown there.</p>
<p><strong>Active-only rows are the norm.</strong> The buff row can hold around
27 entries but shows only what is currently up &mdash; usually a handful. It is
truncated in these diagrams for legibility; the <code>+N</code> chip is the
number left out.</p>
</div>
"""


SPECS = [
    ("RM Riftblade", "Riftblade",
     "Melee. Runeblade is the filler and carries a charge count; the elemental "
     "strikes and Primordial Blast fill the rest of the main row."),
    ("RM Engravement", "Engravement",
     "Melee. Marked: Runic Brand sits in the proc row because it is spent by "
     "Runeblade rather than left to tick."),
    ("RM Glyphic", "Glyphic",
     "Ranged. The only spec with the glyph bar: three segments that light up "
     "as you build Frost, Flame and Arcane."),
]

html = f"""<div class="wrap">
<header>
<p class="eyebrow">Runemaster &middot; Conquest of Azeroth</p>
<h1>WeakAura layout guide</h1>
<p>Every band below is drawn 1:1 from the actual import, so this is exactly
what lands on screen. Only one spec is ever active at a time; the shared rows
&mdash; reminders, short buffs and long-term buffs &mdash; appear for all three.</p>
</header>
<div class="note">
<h3>Reading it top to bottom</h3>
<p>The vertical order is deliberate: the things you must react to within a
couple of globals sit nearest your character, and the things you set once and
forget sit furthest away.</p>
<p>Rows that track buffs are <strong>active-only</strong> &mdash; they are empty
until the buff is up, so the pack looks far sparser in play than it does here,
where everything is drawn at once.</p>
</div>
{render_template()}\n{"".join(render(s, t, b) for s, t, b in SPECS)}
</div>"""

open(f"{SP}/guide.html", "w").write(f"<style>{CSS}</style>\n{html}")
print("wrote guide.html", os.path.getsize(f"{SP}/guide.html"), "bytes")
