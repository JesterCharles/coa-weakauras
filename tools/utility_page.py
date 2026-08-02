"""The raid-utility page body -- coverage grid, scarcity strip, ability lists.

Imported by tools/mksite.py, which supplies the site chrome. Reads the SAME
rows as notes/raid-utility.md via utility_tables.tables(), so the page and the
markdown cannot disagree; there is no second copy of the data and no markdown
parser in the path.

WHY IT IS NOT TEN TABLES. It was, and it read as a data dump. The reader is a
raid leader answering "we are short an interrupt, who brings one", "who has a
battle rez", and "if I swap a Necromancer for a Bloodmage what do I lose" --
and the last of those is unanswerable from data grouped by utility TYPE,
because comparing two CLASSES means scanning ten tables. So the page leads
with a coverage grid (21 classes x 10 tools, one screen) and the lists became
the record rather than the index.
"""
import html
import json
import os
import re
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)

from utility_tables import tables            # noqa: E402
from iconcolor import colors_for             # noqa: E402
from classes import data as _data            # noqa: E402


def _spell_icons():
    """spell id -> icon texture, from resources/utility-icons.json.

    Absent id means db.ascension.gg has no art for it, which the page shows as
    a neutral placeholder rather than a broken image -- 27 of 107 abilities are
    in that state and it is NOT strong evidence they are missing from the game
    (5 of 6 flagged interrupts turned out to be real).
    """
    p = _data("utility-icons.json")
    if not os.path.exists(p):
        return {}
    return json.load(open(p, encoding="utf-8")).get("ids") or {}


ICONS = _spell_icons()


def ability_icon(sid, px=22):
    tex = ICONS.get(str(sid))
    if not tex:
        return f'<span class="aicon none" style="width:{px}px;height:{px}px"></span>'
    return (f'<img class="aicon" src="assets/spell-icons/{tex}.jpg" alt="" '
            f'width="{px}" height="{px}" loading="lazy">')

BANDS = [
    ("stop",  "Stops a cast", [
        ("interrupt",       "INT",  "Interrupt"),
        ("silence",         "SIL",  "Silence"),
    ]),
    ("tools", "Raid tools", [
        ("rez",             "REZ",  "Battle rez"),
        ("raid_dr",         "DR",   "Raid DR (active)"),
        ("raid_dr_passive", "DR·P", "Raid DR (passive)"),
        ("purge",           "PRG",  "Purge"),
        ("spellsteal",      "STL",  "Spellsteal"),
        ("tranq",           "SOO",  "Soothe"),
    ]),
    ("trash", "Trash only", [
        ("stun",            "STN",  "Stun"),
        ("root",            "RT",   "Root"),
    ]),
]
CATS = [c for _b, _l, cs in BANDS for c, _a, _n in cs]
BAND_OF = {c: b for b, _l, cs in BANDS for c, _a, _n in cs}
ABBR = {c: a for _b, _l, cs in BANDS for c, a, _n in cs}
LONG = {c: n for _b, _l, cs in BANDS for c, _a, n in cs}
NCOL = 1 + len(CATS)


SLUG = {}   # class name -> icon slug


def slugify(n):
    return n.lower().replace(" ", "-").replace("'", "")


# ------------------------------------------------------------ derivations
def cd_secs(cd):
    """Sort key for a cooldown string. 'none' means no cooldown at all, which
    for availability is the best case, so it sorts first."""
    if not cd or cd == "none":
        return -1.0
    m = re.match(r"([\d.]+)\s*(min|s)", cd)
    if not m:
        return 9e9
    v = float(m.group(1))
    return v * 60 if m.group(2) == "min" else v


def cd_short(cd):
    """Cooldown as it appears in a grid cell. Narrow by construction."""
    if not cd or cd == "none":
        return "—"
    return cd.replace(" min", "m").replace(" ", "")


SCHOOLS = ("holy", "fire", "frost", "shadow", "nature", "arcane", "physical")


def dr_magnitude(desc):
    """Percent damage reduction, out of the tooltip.

    Returns '' when the tooltip does not state one. Templar's Grace of
    Aman'Thul is a heal-on-melee-hit, not a percentage, and has to render
    blank rather than guess -- an unparsed row simply shows no big number,
    which is the same failure mode as a blank cell today but without the
    column of blanks.
    """
    l = desc.lower()
    for pat in (r"damage taken[^.%]{0,60}?by\s*(?:up to\s*)?-?(\d+(?:\.\d+)?)%",
                r"(\d+(?:\.\d+)?)%\s+reduced damage taken",
                r"damage taken reduced by\s*-?(\d+(?:\.\d+)?)%"):
        m = re.search(pat, l)
        if m:
            v = m.group(1)
            if "." in v:
                v = v.rstrip("0").rstrip(".")
            return v + "%"
    return ""


def dr_kind(desc):
    """What the reduction applies to. '' means all damage."""
    l = desc.lower()
    if "area of effect" in l:
        return "AoE only"
    if ("spell damage taken" in l or "damage taken from spells" in l
            or "magic damage taken" in l):
        return "magic only"
    head = l.split("damage taken")[0][-70:]
    named = [s for s in SCHOOLS if s in head]
    if named:
        return "/".join(s.capitalize() for s in named) + " only"
    return ""


def dr_scope(desc):
    """raid / party / ally.

    The distinction the current page loses entirely: Chronomancer's Decelerate
    is a 5% single-target magic damper and Guardian's Bastion is -40% to
    everyone in 12 yds, and today they are adjacent rows in one table with no
    hint that they are different kinds of thing.
    """
    l = desc.lower()
    if "party and raid" in l:
        return "raid"
    if re.search(r"(allies|party members)\s+within", l):
        return "party"
    if re.search(r"targeted party member|an ally|ally target|target 1", l):
        return "ally"
    return ""


# ------------------------------------------------------------------- data
def load():
    raw = tables()
    by_cat, notes = {}, {}
    for cat, title, note, col, rows, missing in raw:
        by_cat[cat] = rows
        notes[cat] = (title.split(". ", 1)[-1], note, col, missing)
    classes = sorted({r[1] for rows in by_cat.values() for r in rows})
    for c in classes:
        SLUG[c] = slugify(c)
    return by_cat, notes, classes


def cell_data(rows):
    """Everything a grid cell needs, from the rows of one class+category."""
    rows = sorted(rows, key=lambda r: cd_secs(r[8]))
    return {
        "cd": cd_short(rows[0][8]),
        "extra": len(rows) - 1,
        "talent": all(r[3] for r in rows),
        "unverified": all("noicon" in r[6] for r in rows),
        "names": ", ".join(r[4] for r in rows),
        # every spell id behind this cell, so the hover card can show the
        # whole stack rather than just the shortest cooldown the cell prints
        "ids": [str(r[12]) for r in rows],
    }


# ------------------------------------------------------------------ render
def esc(s):
    return html.escape(str(s))


def md(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t


def icon(cn, px=22):
    s = SLUG[cn]
    return (f'<img src="assets/class-icons/{s}/_class-{s}.png" alt="" '
            f'width="{px}" height="{px}" loading="lazy">')


def chips(r, cat):
    """Everything true about this ability that is not a number.

    Note what is NOT here as a column: `observed` (Usable on Boss) and the
    battle-rez Reagent. Both are hand-filled and both are empty for all 103
    rows right now. As columns they render as a wall of blanks that scans as
    "no"; as chips their absence claims nothing and their arrival is loud.
    """
    out = [f'<span class="chip spec">{esc(r[2])}</span>']
    if r[3]:
        out.append(f'<span class="chip tal" title="costs a talent point">'
                   f'{esc(r[3])}</span>')
    if "int" in r[6]:
        out.append('<span class="chip int" title="tooltip also claims it '
                   'interrupts non-player spellcasting">int</span>')
    if "noicon" in r[6]:
        out.append('<span class="chip unv" title="no icon on the spell db '
                   '&mdash; may not exist in game">unverified</span>')
    if r[7]:
        out.append('<span class="chip obs">'
                   f'{"reagent" if cat == "rez" else "boss"}: {esc(r[7])}'
                   '</span>')
    if cat in ("raid_dr", "raid_dr_passive"):
        sc = dr_scope(r[11])
        if sc:
            out.append(f'<span class="chip scope {sc}" title="who it covers">'
                       f'{sc}</span>')
        k = dr_kind(r[11])
        if k:
            out.append(f'<span class="chip kind">{esc(k)}</span>')
    return "".join(out)


def ability_row(r, cat, show_class=True, accent=None):
    """One ability.

    A CSS grid row, not a table row. The three numbers live in one .abnums
    flex strip with fixed widths, so they still line up into columns down the
    list on desktop, and on a phone the strip becomes a labelled wrap instead
    of forcing min-width:940px on the whole page.
    """
    mag = dr_magnitude(r[11]) if cat in ("raid_dr", "raid_dr_passive") else ""
    cls = ""
    if show_class:
        cls = f'<span class="abcls">{icon(r[1])}<b>{esc(r[1])}</b></span>'
    big = f'<span class="mag">{mag}</span>' if mag else ""
    cd = esc(r[8]) if r[8] != "none" else "—"
    cast = esc(r[10]).replace("\\*", "*")   # the source escapes it for markdown
    # data-cat lets the filter match "battle rez" against a row whose text
    # says only "Spiritual Ascension"
    return f"""<li class="ab" data-cat="{esc(LONG[cat])}" data-sid="{r[12]}" style="--c:{accent}">{cls}
  <span class="abname">{ability_icon(r[12], 20)}<a href="{r[5]}" rel="noopener">{esc(r[4])}</a>{big}
    <span class="abchips">{chips(r, cat)}</span></span>
  <span class="abnums"><span class="n cd" data-l="CD">{cd}</span
    ><span class="n cost" data-l="Cost">{esc(r[9])}</span
    ><span class="n cast" data-l="Cast">{cast}</span></span>
  <span class="abdesc">{esc(r[11])}</span>
</li>"""


def render():
    by_cat, notes, classes = load()
    colors = colors_for([SLUG[c] for c in classes])
    acc = {c: colors[SLUG[c]]["accent"] for c in classes}

    grid = {c: {} for c in classes}
    for cat, rows in by_cat.items():
        for c in classes:
            mine = [r for r in rows if r[1] == c]
            if mine:
                grid[c][cat] = cell_data(mine)

    counts = {cat: sum(1 for c in classes if cat in grid[c]) for cat in CATS}
    conf = {cat: sum(1 for c in classes
                     if cat in grid[c] and not grid[c][cat]["unverified"])
            for cat in CATS}
    N = len(classes)
    out = []
    A = out.append

    # ------------------------------------------------------- 1. .utilhead
    # `wrap` is the site's own container -- max-width 1240px, auto margins,
    # responsive gutter. Every other page uses it; this one did not, so the
    # content sat flush at x=0 and stretched the grid across the whole
    # viewport. That is where "a TON of empty space" came from: not the
    # design, a missing class from the port.
    A('<main class="util wrap">')
    A('<div class="utilhead"><h1>Raid utility</h1>')
    A('<p class="lede">Every interrupt, battle rez, purge, spellsteal, enrage '
      'removal and raid damage reduction across all 21 Conquest of Azeroth '
      'classes &mdash; classified by spell effect id, not by tooltip text.</p>')
    A('<div class="utiltools">'
      '<label class="editbox" id="fbox"><span class="slash">/</span>'
      '<input id="uq" type="search" placeholder="filter class or ability" '
      'autocomplete="off"><button id="uclear" type="button" '
      'aria-label="clear filter">&times;</button></label>'
      '<button class="rosterbtn" id="rosterclear" type="button" hidden>'
      'clear roster (<span id="rostern">0</span>)</button></div></div>')

    # --------------------------------------------------------- 1b. tabs
    # One long page was the complaint: nobody scrolls 190KB to find the four
    # soothes. Overview carries the two things that answer a question at a
    # glance (scarcity + the grid); each category gets its own panel.
    #
    # Deep links still work -- the hash names the panel and the JS opens it on
    # load. Without JS every panel renders open and the tab bar hides itself,
    # so the page degrades to exactly what it was before.
    # Class filter. The icons are the affordance a WoW player already reads,
    # and it answers the roster question from the other end: "show me only what
    # these five classes bring" rather than "who has an interrupt".
    A('<div class="clsfilter" aria-label="filter by class">')
    A('<span class="cfl">Filter by class</span><div class="cfrow">')
    for c in classes:
        A(f'<button class="cf" type="button" data-class="{esc(c)}" '
          f'title="{esc(c)}" style="--c:{acc[c]}">{icon(c, 30)}'
          f'<span>{esc(c)}</span></button>')
    A('</div><button class="cfclear" type="button" hidden>Clear</button></div>')

    A('<nav class="tabs" role="tablist">')
    A('<button class="tab on" role="tab" data-panel="overview">Overview</button>')
    for cat in sorted(CATS, key=lambda c: (BAND_OF[c] == "trash",
                                           -counts[c], LONG[c])):
        A(f'<button class="tab tb-{BAND_OF[cat]}" role="tab" '
          f'data-panel="{cat}">{esc(LONG[cat])}'
          f'<i>{len(by_cat.get(cat, ()))}</i></button>')
    A('</nav>')

    # ------------------------------------------------------- 2. .scarcity
    A('<section class="panel on" id="panel-overview">')
    A('<p class="lbl">What is scarce</p>')
    A('<p class="secnote">How many of the 21 classes bring each tool, rarest '
      'first. The short bars are the ones that decide a roster. Pick classes '
      'in the grid below and these recount against <b>your</b> roster.</p>')
    A('<ul class="scarcity">')
    for cat in sorted(CATS, key=lambda c: (counts[c], LONG[c])):
        pct = round(100 * counts[cat] / N)
        unv = counts[cat] - conf[cat]
        A(f'''<li class="sc sc-{BAND_OF[cat]}" data-cat="{cat}"><a href="#{cat}">
  <span class="scname">{esc(LONG[cat])}</span>
  <span class="scnum"><b data-count="{cat}">{counts[cat]}</b><em>/{N}</em></span>
  <span class="bartrack"><span class="barfill" data-bar="{cat}"
    style="width:{pct}%"></span></span>
  {f'<i class="unvn">{unv} unverified</i>' if unv else ''}
</a></li>''')
    A('</ul>')

    # --------------------------------------------------------- 3. .matrix
    A('<p class="lbl" id="matrix">Coverage grid</p>')
    A('<p class="secnote">One row per class, one column per tool. The number '
      'is that class’s <b>shortest cooldown</b> in the column; <b>&mdash;'
      '</b> means no cooldown at all. <b>t</b> marks a tool that costs a '
      'talent point, <b>+n</b> that the class brings more than one. Click a '
      'class to open its full kit; click its icon to add it to your roster.'
      '</p>')

    A('<div class="mxwrap"><table class="mx">')
    A('<thead><tr class="mxbands"><td class="mxc"></td>')
    for band, label, cs in BANDS:
        A(f'<td class="bl b-{band}" colspan="{len(cs)}"><span>{esc(label)}'
          f'</span></td>')
    A('</tr><tr><th class="mxc" scope="col">Class</th>')
    for band, label, cs in BANDS:
        for i, (cat, ab, name) in enumerate(cs):
            A(f'<th class="mxh b-{band}{" bstart" if not i else ""}" '
              f'scope="col" abbr="{esc(name)}">'
              f'<a href="#{cat}" title="{esc(name)}">{ab}</a></th>')
    A('</tr></thead><tbody>')

    for c in classes:
        have = grid[c]
        # data-has lists the tools this class brings, so the filter matches
        # "battle rez" or "soothe" as well as class and ability names
        A(f'<tr class="mxr" data-class="{esc(c)}" '
          f'data-has="{esc(" ".join(LONG[k] for k in CATS if k in have))}" '
          f'style="--c:{acc[c]}">'
          f'<th class="mxc" scope="row"><span class="mxcin">'
          f'<button class="pick" type="button" '
          f'aria-label="add {esc(c)} to roster">{icon(c)}</button>'
          f'<button class="open" type="button" aria-expanded="false">'
          f'{esc(c)}</button></span></th>')
        for band, label, cs in BANDS:
            for i, (cat, ab, name) in enumerate(cs):
                bs = " bstart" if not i else ""
                d = have.get(cat)
                if not d:
                    A(f'<td class="mxx b-{band}{bs}"><span aria-label="none">'
                      f'&middot;</span></td>')
                    continue
                mk = '<i class="t" title="talent point">t</i>' if d["talent"] else ""
                if d["extra"]:
                    mk += (f'<i class="p" title="{d["extra"]} more">'
                           f'+{d["extra"]}</i>')
                A(f'<td class="mxv b-{band}{bs}'
                  f'{" unv" if d["unverified"] else ""}" '
                  f'title="{esc(d["names"])}" '
                  f'data-ids="{",".join(d["ids"])}">'
                  f'<span class="cd">{d["cd"]}</span>{mk}</td>')
        A('</tr>')

        # ---- .kit: the class-first view. Question 5 lives here.
        A(f'<tr class="kitrow" data-class="{esc(c)}" hidden>'
          f'<td colspan="{NCOL}"><div class="kit" style="--c:{acc[c]}">')
        for band, label, cs in BANDS:
            present = [cat for cat, _a, _n in cs if cat in have]
            if not present:
                continue
            if band == "trash":
                # One dim line. A class's stuns must not occupy a third of its
                # kit panel when the question is "what does it bring to a boss".
                bits = []
                for cat in present:
                    for r in sorted([r for r in by_cat[cat] if r[1] == c],
                                    key=lambda r: cd_secs(r[8])):
                        bits.append(f'<a href="{r[5]}" rel="noopener">'
                                    f'{esc(r[4])}</a> '
                                    f'<i>{ABBR[cat]} {cd_short(r[8])}</i>')
                A(f'<p class="kittrash"><b>Trash only</b> '
                  f'{" &nbsp;/&nbsp; ".join(bits)}</p>')
                continue
            A(f'<div class="kitband kb-{band}"><p class="kbl">{esc(label)}</p>')
            for cat in present:
                rows = sorted([r for r in by_cat[cat] if r[1] == c],
                              key=lambda r: cd_secs(r[8]))
                A(f'<p class="kcat"><span class="kab">{ABBR[cat]}</span>'
                  f'{esc(LONG[cat])}</p><ul class="ablist tight">')
                for r in rows:
                    A(ability_row(r, cat, show_class=False, accent=acc[c]))
                A('</ul>')
            A('</div>')
        gaps = [LONG[cat] for cat in CATS
                if cat not in have and BAND_OF[cat] != "trash"]
        if gaps:
            A(f'<p class="kitgap"><b>Brings no</b> {esc(", ".join(gaps))}.</p>')
        A('</div></td></tr>')
    A('</tbody></table></div>')
    A('<p class="mxlegend">'
      '<span><i class="k v">14s</i>shortest cooldown</span>'
      '<span><i class="k v">&mdash;</i>no cooldown</span>'
      '<span><i class="k t">t</i>costs a talent point</span>'
      '<span><i class="k p">+1</i>brings another</span>'
      '<span><i class="k unv">14s?</i>unverified in game</span>'
      '<span><i class="k x">&middot;</i>none</span></p>')
    A('</section>')

    # --------------------------------------------------- 4. .utilsec x 10
    def section(cat):
        title, note, _col, missing = notes[cat]
        rows = by_cat[cat]
        if cat in ("raid_dr", "raid_dr_passive"):
            # Q3 is "do we have enough raid DR" -- so the biggest wall leads,
            # then the longest cooldown. Rows whose tooltip states no
            # percentage sort last rather than as zero.
            def drkey(r):
                m = dr_magnitude(r[11])
                return (-float(m[:-1]) if m else 1e9, -cd_secs(r[8]))
            rows = sorted(rows, key=drkey)
        else:
            # Everywhere else the shortest cooldown is the best tool, and
            # "which class brings the best one" is the question being asked.
            rows = sorted(rows, key=lambda r: (cd_secs(r[8]), r[1]))
        paras = note.split("\n\n")
        A(f'<section class="utilsec" id="{cat}">')
        A(f'<p class="lbl">{esc(title)} <span class="lblnum">'
          f'{len(rows)} abilities &middot; '
          f'{len({r[1] for r in rows})} classes</span></p>')
        A(f'<p class="secnote">{md(paras[0])}</p>')
        if len(paras) > 1:
            A('<details class="why"><summary>What is excluded, and why'
              '</summary>' +
              "".join(f'<p>{md(p)}</p>' for p in paras[1:]) + '</details>')
        # A column header for the list. Desktop only: on a phone every number
        # already carries its own label, so a header row would be noise.
        A('<ul class="ablist"><li class="ab abhead" aria-hidden="true">'
          '<span class="abcls">Class</span><span class="abname">Ability</span>'
          '<span class="abnums"><span class="n cd">CD</span>'
          '<span class="n cost">Cost</span>'
          '<span class="n cast">Cast</span></span></li>')
        for r in rows:
            A(ability_row(r, cat, accent=acc[r[1]]))
        A('</ul>')
        # The full "None for:" roll-call is 16 class names for a scarce tool
        # and the coverage grid already shows it. Print it only when it is
        # short enough to read, which is exactly when it is surprising.
        if not missing:
            tail = "Every class has one."
        elif len(missing) <= 6:
            tail = "None for: " + ", ".join(missing) + "."
        else:
            tail = (f"{N - len(missing)} of {N} classes "
                    f"&mdash; see the <a href=\"#matrix\">coverage grid</a>.")
        A(f'<p class="tallies">{tail}</p></section>')

    # One panel per category. The band each belongs to is carried on the tab
    # AND on the panel, so the stun/interrupt separation survives the move from
    # one scrolling page to tabs -- a trash panel says so at the top, where the
    # old design relied on the section being buried at the foot.
    BANDNOTE = {
        "stop": "Actually stops a boss cast.",
        "tools": "Raid utility.",
        "trash": "TRASH ONLY \u2014 most raid bosses are immune, so this will "
                 "not stop a cast however much the tooltip sounds like it "
                 "does. A stun is not an interrupt.",
    }
    for cat in CATS:
        band = BAND_OF[cat]
        A(f'<section class="panel pn-{band}" id="panel-{cat}" hidden>')
        A(f'<p class="bandnote bn-{band}">{BANDNOTE[band]}</p>')
        section(cat)
        A('</section>')
    # ------------------------------------------------- 5. hover-card data
    # ONE payload for the page rather than a data-* blob per cell: 103
    # abilities inlined once is ~14KB, the same thing repeated on every cell
    # that references them is several times that. The grid cells carry only
    # ids; the card is built from this.
    payload = {}
    for cat, rows in by_cat.items():
        for r in rows:
            payload[str(r[12])] = {
                "n": r[4], "c": r[1], "cat": LONG[cat], "band": BAND_OF[cat],
                "spec": r[2], "rc": r[3], "cd": r[8], "cost": r[9],
                "cast": r[10].replace("\\*", "*"), "d": r[11],
                "u": r[5], "i": ICONS.get(str(r[12]), ""),
                "m": r[6], "obs": r[7],
            }
    A('<script type="application/json" id="abdata">'
      + json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
      + '</script>')
    A('</main>')
    return "\n".join(out)
