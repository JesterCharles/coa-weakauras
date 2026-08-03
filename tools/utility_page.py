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

from utility_tables import tables, class_specs, spec_mask   # noqa: E402
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


def _alias_table():
    """class name -> [search alias, ...].

    Three sources, none of them derivable from the class name:
      * community slang from resources/class-aliases.json (`rm`, `kox`)
      * the WeakAuras load token from resources/class-tokens.md, which is
        parsed rather than copied so that table stays authoritative -- and it
        is worth searching because several are nothing like the class name
        (Runemaster loads as SPIRITMAGE, Templar as MONK)
      * every word of the class name itself, so "xoroth" finds Knight of
        Xoroth without anyone having to list it
    """
    from classes import CLASSES  # noqa: PLC0415  -- avoids an import cycle
    p = _data("class-aliases.json")
    raw = {}
    if os.path.exists(p):
        raw = json.load(open(p, encoding="utf-8")).get("aliases") or {}
    out = {}
    for c in CLASSES.values():
        al = {a.lower() for a in raw.get(c.name, ())}
        if getattr(c, "token", None):
            al.add(c.token.lower())
        al.update(w.lower() for w in re.split(r"[^A-Za-z]+", c.name) if len(w) > 2)
        al.discard(c.name.lower())
        out[c.name] = sorted(al)
    return out


ALIASES = _alias_table()


def aliases_for(name):
    return ALIASES.get(name, [])


def spec_alias_map():
    """Raid-Helper spec name -> {"c": class, "s": spec or None}.

    Only the four that do NOT match a tree label; the other 65 resolve by
    name and need no entry. `s: null` means the class is certain and the spec
    is not -- the page says so rather than picking one.
    """
    p = _data("spec-aliases.json")
    if not os.path.exists(p):
        return {}
    raw = json.load(open(p, encoding="utf-8")).get("specs") or {}
    return {k.lower(): {"c": v["class"], "s": v.get("spec")}
            for k, v in raw.items()}


def ability_icon(sid, px=22):
    tex = ICONS.get(str(sid))
    if not tex:
        return f'<span class="aicon none" style="width:{px}px;height:{px}px"></span>'
    return (f'<img class="aicon" src="assets/spell-icons/{tex}.jpg" alt="" '
            f'width="{px}" height="{px}" loading="lazy">')

# Columns carry WORDS, not a code.
#
# The old header row read `INT SIL REZ DR DR·P PRG STL SOO STN RT`, which is a
# key the reader has to learn before the grid says anything -- and `DR·P` is
# not learnable at all. At 1240px the content column gives every tool column
# ~96px, and "Spellsteal" sets in 72px at 13px. The abbreviations were never
# buying width; they were only costing meaning. So each column now prints its
# real name, over two lines where the name has two parts, and the pair that the
# abbreviation actually mangled -- active vs passive raid DR -- says so in
# words on the second line.
#
# (cat, short label, full name, header lines)
BANDS = [
    ("stop",  "Stops a cast", [
        ("interrupt",       "Interrupt",  "Interrupt",          ("Interrupt",)),
        ("silence",         "Silence",    "Silence",            ("Silence",)),
    ]),
    ("tools", "Raid tools", [
        ("rez",             "Battle rez", "Battle rez",         ("Battle", "rez")),
        ("raid_dr",         "Raid DR",    "Raid DR (active)",   ("Raid DR", "active")),
        ("raid_dr_passive", "Passive DR", "Raid DR (passive)",  ("Raid DR", "passive")),
        ("raid_dmg",        "Raid DMG",   "Raid damage (active)", ("Raid DMG", "active")),
        ("purge",           "Purge",      "Purge",              ("Purge",)),
        ("spellsteal",      "Spellsteal", "Spellsteal",         ("Spellsteal",)),
        ("tranq",           "Soothe",     "Soothe",             ("Soothe",)),
    ]),
    ("trash", "Trash only", [
        ("stun",            "Stun",       "Stun",               ("Stun",)),
        ("root",            "Root",       "Root",               ("Root",)),
    ]),
]
CATS = [c for _b, _l, cs in BANDS for c, _s, _n, _h in cs]

# CATEGORIES THAT GET A TAB BUT NOT A GRID COLUMN.
#
# `raid_dmg_passive` is 79 rows across ALL 21 classes, and `raid_buff_longterm`
# is 23 across 11. A coverage grid column that every class fills can never show
# a gap, so as a column the passive list would be the biggest table on the page
# and the least informative thing in it -- while costing the grid 8% of its
# width. Both are real data and both get a full section; neither earns a
# column. The grid stays at ten.
LIST_ONLY = [
    ("raid_dmg_passive",   "Passive DMG", "Raid damage (passive)", "tools"),
    ("raid_buff_longterm", "Long buffs",  "Long-duration raid buffs", "tools"),
]
TABCATS = CATS + [c for c, _s, _n, _b in LIST_ONLY]
BAND_OF = {c: b for b, _l, cs in BANDS for c, _s, _n, _h in cs}
BAND_OF.update({c: b for c, _s, _n, b in LIST_ONLY})
SHORT = {c: s for _b, _l, cs in BANDS for c, s, _n, _h in cs}
SHORT.update({c: s for c, s, _n, _b in LIST_ONLY})
LONG = {c: n for _b, _l, cs in BANDS for c, _s, n, _h in cs}
LONG.update({c: n for c, _s, n, _b in LIST_ONLY})
HEAD = {c: h for _b, _l, cs in BANDS for c, _s, _n, h in cs}
NCOL = 1 + len(CATS)


SLUG = {}    # class name -> icon slug
SPECS = {}   # class name -> [spec label, ...]


def slugify(n):
    return n.lower().replace(" ", "-").replace("'", "")


# ------------------------------------------------------------ derivations
def cd_secs(cd):
    """Sort key for a cooldown string. 'none' means no cooldown at all, which
    for availability is the best case, so it sorts first."""
    if not cd or cd == "none":
        return -1.0
    # A LOWER BOUND STILL SORTS. `>=1 min` is a real cooldown that happens to
    # be imprecise, and leaving it unparsed sent it to 9e9 -- dead last in its
    # table, below every genuine "no cooldown" row. Sorted at its floor, which
    # is the closest true statement available.
    m = re.match(r"\u2265?\s*([\d.]+)\s*(min|s)", cd)
    if not m:
        return 9e9
    v = float(m.group(1))
    return v * 60 if m.group(2) == "min" else v


def cd_short(cd):
    """Cooldown as it appears in a grid cell. Narrow by construction.

    The `\u2265` on a bounded value SURVIVES the abbreviation. Dropping it to
    save two pixels would turn "at least a minute" into "a minute", which is
    the one thing tools/ascension.py exists to avoid.
    """
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
    cspecs = class_specs()
    for c in classes:
        SLUG[c] = slugify(c)
        SPECS[c] = cspecs[c][0]
    return by_cat, notes, classes, cspecs


def cell_data(rows, specs):
    """Everything a grid cell needs, from the rows of one class+category.

    `mask` is the one addition that changes what the grid MEANS. A cell used to
    say only "this class brings this tool", and 33 of the 103 rows behind those
    cells are locked to a single spec tree -- so a raid lead reading the grid
    counted Bloodmage as interrupt cover when `Aneurysm` is Sanguine-only, one
    of that class's four specs. Across the interrupt column that is 7 of the 19
    classes with an interrupt.

    The mask is a UNION over the cell's rows, which is right: the question a
    grid cell answers is "can this class press one of these", and two abilities
    on different specs cover between them what neither covers alone.
    """
    rows = sorted(rows, key=lambda r: cd_secs(r[8]))
    mask = [False] * len(specs)
    for r in rows:
        for i, ok in enumerate(spec_mask(specs, r[2])):
            mask[i] = mask[i] or ok
    return {
        "cd": cd_short(rows[0][8]),
        "extra": len(rows) - 1,
        "talent": all(r[3] for r in rows),
        "unverified": all("noicon" in r[6] for r in rows),
        # ALL, not any: a cell is the class's whole answer for that column, and
        # a class whose second interrupt is confirmed still brings an
        # interrupt. Only when every ability behind the cell is waiting on an
        # in-game check does the cell itself carry the doubt.
        "pending": all("norecord" in r[6] for r in rows),
        "names": ", ".join(r[4] for r in rows),
        # every spell id behind this cell, so the hover card can show the
        # whole stack rather than just the shortest cooldown the cell prints
        "ids": [str(r[12]) for r in rows],
        "mask": mask,
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
    # The spec is NOT a chip here any more -- it is its own column, next to
    # the class. It answers a different question from the rest of these ("can
    # the person I have press this") and reading it meant finding one chip
    # among five that all looked alike.
    out = []
    if r[3]:
        out.append(f'<span class="chip tal" title="costs a talent point">'
                   f'{esc(r[3])}</span>')
    # Two different claims, and the first is much stronger. int68 means the
    # spell carries a real INTERRUPT_CAST effect; `int` only means its tooltip
    # says it interrupts non-player casting, which on a boss is usually worth
    # nothing.
    if "int68" in r[6]:
        out.append('<span class="chip int68" title="carries a real '
                   'INTERRUPT_CAST effect as well as the silence">'
                   'interrupts too</span>')
    if "int" in r[6]:
        out.append('<span class="chip int" title="tooltip also claims it '
                   'interrupts non-player spellcasting">int</span>')
    # ONE DATABASE, NOT TWO. db.exil.es has this spell and db.ascension.gg has
    # no record of it at all -- not merely no art for it, which is the weaker
    # chip below. Absence from one snapshot is not proof of absence from the
    # game (five ids in this state have been found in game by hand), so the
    # chip states what is HAPPENING rather than passing a verdict: somebody is
    # checking. A row only ever leaves this page on an in-game check.
    if "norecord" in r[6]:
        out.append('<span class="chip unv2" title="on db.exil.es only '
                   '&mdash; db.ascension.gg has no record of this spell. '
                   'Not proof it is missing: five spells in this state have '
                   'been confirmed in game by hand.">'
                   '<b>!</b> in-game verification in process</span>')
    elif "noicon" in r[6]:
        out.append('<span class="chip unv" title="no icon on the spell db '
                   '&mdash; a reason to check, not a verdict: five of six '
                   'flagged interrupts turned out to be real">unverified</span>')
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
    # data-specs is per ABILITY here, not per cell: the grid unions a class's
    # abilities together because "can this class press one of these" is the
    # grid's question, but a list row is one button and a Sanguine Bloodmage
    # who cannot press `Aneurysm` should see that on the row itself.
    sm = "".join("1" if m else "0" for m in spec_mask(SPECS.get(r[1], []), r[2]))
    # `all` is the common case and prints as a word rather than a spec name,
    # so it stays quiet -- the column is scanned for the exceptions.
    generic = r[2] in ("all", "all (tree)", "?")
    spec = (f'<span class="abspec{" gen" if generic else ""}">'
            f'{esc("every spec" if generic else r[2])}</span>')
    # .abwho is filled by the roster code once a raid is loaded, and the column
    # collapses when there is none. Rendered empty rather than injected later
    # so the grid template never changes shape mid-life.
    return f"""<li class="ab" data-cat="{esc(LONG[cat])}" data-sid="{r[12]}" data-cls="{esc(r[1])}" data-specs="{sm}" style="--c:{accent}">{cls}
  {spec}
  <span class="abname">{ability_icon(r[12], 20)}<a href="{r[5]}" target="_blank" rel="noopener noreferrer">{esc(r[4])}</a>{big}
    <span class="abchips">{chips(r, cat)}</span></span>
  <span class="abwho" aria-label="who brings it"></span>
  <span class="abnums"><span class="n cd" data-l="CD">{cd}</span
    ><span class="n cost" data-l="Cost">{esc(r[9])}</span
    ><span class="n cast" data-l="Cast">{cast}</span></span>
  <span class="abdesc">{esc(r[11])}</span>
</li>"""


def render():
    by_cat, notes, classes, cspecs = load()
    colors = colors_for([SLUG[c] for c in classes])
    acc = {c: colors[SLUG[c]]["accent"] for c in classes}

    grid = {c: {} for c in classes}
    for cat, rows in by_cat.items():
        for c in classes:
            mine = [r for r in rows if r[1] == c]
            if mine:
                grid[c][cat] = cell_data(mine, cspecs[c][0])

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
    # `uwide` lifts the site's 1240px cap for this page only. Every other page
    # here is prose or a card list and 1240 is right for those; this one's
    # primary object is a 21x10 table that wants 1180px on its own, and the
    # rails either side of it were pure loss at 1240. It is the one page whose
    # content, not its typography, sets the measure.
    # ONE SCREEN, AND THE TABLE IS THE ONLY THING THAT SCROLLS.
    #
    # Everything above the grid has been cut back to what a raid lead uses. The
    # lede, the "who brings what" heading and its instruction paragraph, the
    # roster rail and the scarcity rail are all gone -- they were prose and
    # furniture stacked on top of the only object anyone came for. What is left
    # is one row (title, tabs, filter) and the table, and the page itself no
    # longer scrolls: `main` is the viewport, and the grid scrolls inside its
    # own box under a stuck header.
    #
    # The width that bought back is spent on the table, which is what makes it
    # possible to NAME the spec in a cell instead of encoding it.
    A('<main class="util uwide">')
    A('<div class="ovtop">')
    # The page name lives CENTRED IN THE SITE HEADER now (mksite's
    # `header_title`). It used to open this row and cost ~130px that eleven
    # tabs, the filter and the raid control all needed. The <h1> stays in the
    # document for structure and for anything reading the outline, just off
    # screen -- a page with no h1 is a worse document, and the header span is
    # decoration as far as assistive tech is concerned.
    A('<h1 class="vh">Raid utility</h1>')
    # Deep links still work -- the hash names the panel and the JS opens it on
    # load. Without JS every panel renders open and the tab bar hides itself,
    # so the page degrades to a long scroll rather than to nothing.
    A('<nav class="tabs" role="tablist">')
    A('<button class="tab on" role="tab" data-panel="overview">Overview</button>')
    for cat in sorted(TABCATS, key=lambda c: (BAND_OF[c] == "trash",
                                              -counts.get(c, 0), LONG[c])):
        # A tab with no grid column has no coverage number to show, and must
        # never be flagged as a gap: "your raid has no passive damage aura" is
        # meaningless when every class has one and the grid never asked.
        nocol = ' data-nocol="1"' if cat not in CATS else ""
        A(f'<button class="tab tb-{BAND_OF[cat]}" role="tab" '
          f'data-panel="{cat}"{nocol}>{esc(SHORT[cat])}'
          f'<i>{len(by_cat.get(cat, ()))}</i></button>')
    A('</nav>')
    # The raid control sits LEFT of the filter, in the top row, because it is
    # the thing that changes what every other number on the page means. Once an
    # event is loaded the button becomes a pill naming it, so "is tonight's raid
    # actually loaded" is answered by looking rather than by remembering.
    # The raid control and the filter travel as ONE flex item. Left as
    # siblings of the tab bar they land on different lines the moment the tabs
    # are wide -- the tabs claim the first line and the filter wraps below,
    # which is exactly the split this row exists to avoid.
    A('<div class="ovtools">')
    # The input replaces the button IN PLACE. It used to open a form down in
    # the bar below, which meant clicking "Load" threw your eye to the other
    # side of the page and back. No Load or Cancel buttons either: Enter
    # submits, and the × inside the field is the way out.
    A('<div class="rhslot">'
      '<button class="rhopen" type="button">Load tonight’s raid</button>'
      '<form class="rhform" hidden>'
      '<label class="editbox rhbox">'
      '<input id="rhid" type="text" placeholder="paste the event link or id" '
      'autocomplete="off" spellcheck="false" enterkeyhint="go">'
      '<button class="rhcancel" type="button" aria-label="cancel">'
      '&times;</button></label></form>'
      '<span class="rhpill" hidden></span>'
      '<button class="rhhelp" type="button" aria-label="how to find your '
      'event id" title="how to find your event id">i</button>'
      '</div>')
    A('<label class="editbox" id="fbox"><span class="slash">/</span>'
      '<input id="uq" type="search" placeholder="filter — try rm, kox, '
      '15s, sanguine" autocomplete="off"><button id="uclear" type="button" '
      'aria-label="clear filter">&times;</button></label>')
    A('<output class="qcount" id="qcount" hidden></output>')
    A('</div>')
    A('</div>')

    # ---- the raid, from Raid-Helper.
    #
    # This replaces the 21-icon roster and the per-class spec chips. Picking a
    # comp by hand was the complaint, and it was also the least reliable way to
    # get one: the guild already declares its raid in Discord, with specs, and
    # a second hand-maintained copy on a web page is a copy that is wrong.
    #
    # raid-helper.dev's event endpoint reads without a token and sends
    # `access-control-allow-origin: *` (probed 2026-08-03), so the browser can
    # fetch it straight from GitHub Pages. The site never talks to Discord and
    # holds no bot credentials -- Raid-Helper's own public API is the bridge.
    # No load button down here -- it lives in .rhslot on the top row. Two of
    # them existed for one build and only the first was ever hidden on load,
    # so a loaded page showed both the event pill and an untouched "Load
    # tonight's raid".
    A('<div class="rhbar">')
    A('<div class="rhstate" hidden></div>')
    A('</div>')

    # ---- how to find an event id.
    #
    # Three screenshots rather than three sentences, because the hard step is
    # not "paste an id", it is knowing that Raid-Helper's Discord embed hides a
    # `Web View` link at the bottom and that Discord throws an interstitial in
    # front of it. Somebody who has never clicked Web View cannot follow prose
    # about it; they can follow a picture of their own raid post.
    A('<div class="rhmodal" hidden>')
    A('<div class="rhsheet" role="dialog" aria-modal="true" '
      'aria-labelledby="rhhelptitle">')
    A('<button class="rhx" type="button" aria-label="close">&times;</button>')
    A('<h2 id="rhhelptitle">Finding tonight’s event</h2>')
    A('<p class="rhlede">The id lives in Raid-Helper’s own web view. '
      'Three clicks from the raid post in Discord.</p>')
    A('<ol class="rhsteps">')
    A('<li><b>1</b><div><p>In Discord, find the Raid-Helper post and click '
      '<b>Web View</b> at the bottom of it.</p>'
      '<img src="assets/rh-help/1-webview.png" alt="The Raid-Helper post in '
      'Discord, with the Web View link highlighted underneath the signup '
      'list" loading="lazy" width="934" height="1000"></div></li>')
    A('<li><b>2</b><div><p>First time only, Discord asks before it lets you '
      'out. Click <b>Visit Site</b>. Ticking <i>Trust raid-helper.xyz links '
      'from now on</i> skips this next time — optional.</p>'
      '<img src="assets/rh-help/2-visit.png" alt="Discord’s Leaving Discord '
      'prompt, with the trust checkbox and the Visit Site button highlighted" '
      'loading="lazy" width="1000" height="570"></div></li>')
    A('<li><b>3</b><div><p>The event opens in your browser. Copy the whole '
      'address, or just the long number at the end of it, and paste it '
      'here.</p>'
      '<img src="assets/rh-help/3-url.png" alt="The Raid-Helper web view in a '
      'browser, with the event id highlighted in the address bar" '
      'loading="lazy" width="1000" height="533"></div></li>')
    A('</ol>')
    A('<p class="rhfoot">Either form works — <code>raid-helper.xyz/event/'
      '1533532408056643717</code> or just <code>1533532408056643717</code>. '
      'Paste it once and this page remembers it.</p>')
    A('</div></div>')

    A('<div class="ovbody">')

    # --------------------------------------------------------- 3. .matrix
    A('<section class="panel on" id="panel-overview">')
    # The key belongs ABOVE the thing it explains. It used to sit under a
    # 1200px table in 11px grey, i.e. after the reader had already guessed.
    A('<p class="mxlegend">'
      '<span><i class="k v">14s</i>shortest cooldown</span>'
      '<span><i class="k v">&mdash;</i>no cooldown</span>'
      '<span><i class="k v"><b class="spn">Sanguine</b></i>'
      'only that spec has it</span>'
      '<span><i class="k t">t</i>costs a talent point</span>'
      '<span><i class="k p">+1</i>brings another</span>'
      '<span><i class="k unv">14s?</i>unverified in game</span>'
      '<span><i class="k x">&nbsp;</i>blank = does not bring it</span></p>')

    # id="matrix": ten href="#matrix" links have shipped against no target.
    # tabindex="0": this is the only scrolling box on the page in one-screen
    # mode, and Safari does not make overflow containers focusable on its own,
    # so a keyboard user could not scroll it.
    A('<div class="mxwrap" id="matrix" tabindex="0" '
      'role="region" aria-label="Coverage grid"><table class="mx">')
    A('<thead><tr class="mxbands"><td class="mxc"></td>')
    for band, label, cs in BANDS:
        A(f'<td class="bl b-{band}" colspan="{len(cs)}"><span>{esc(label)}'
          f'</span></td>')
    A('</tr><tr class="mxhead"><th class="mxc" scope="col">Class</th>')
    for band, label, cs in BANDS:
        for i, (cat, short, name, head) in enumerate(cs):
            # "active"/"passive" qualify the name above them; "rez" is part of
            # the name. Only the qualifier gets the quieter second-line style.
            lines = "".join(
                f'<span class="hw{" q" if w in ("active", "passive") else ""}">'
                f'{esc(w)}</span>' for w in head)
            A(f'<th class="mxh b-{band}{" bstart" if not i else ""}" '
              f'scope="col" abbr="{esc(name)}">'
              f'<a href="#{cat}" title="{esc(name)}">{lines}</a></th>')
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
            for i, (cat, short, name, head) in enumerate(cs):
                bs = " bstart" if not i else ""
                d = have.get(cat)
                if not d:
                    # No dot. 126 of the 210 cells are empty, and a dot in
                    # every one of them is 126 marks competing with the 84
                    # that mean something. Absence should be background.
                    A(f'<td class="mxx b-{band}{bs}"></td>')
                    continue
                mk = '<i class="t" title="talent point">t</i>' if d["talent"] else ""
                if d["extra"]:
                    mk += (f'<i class="p" title="{d["extra"]} more">'
                           f'+{d["extra"]}</i>')
                # The unverified "?" rides the cooldown rather than the cell.
                # As a cell-level ::after it dropped below the spec name onto a
                # line of its own the moment cells grew a second row of text.
                #
                # "!" outranks "?" and replaces it: the second database having
                # no RECORD of the ability is the stronger doubt, and printing
                # both marks on one cell says two things where there is one.
                if d["pending"]:
                    mk += ('<i class="q pend" title="on db.exil.es only — '
                           'db.ascension.gg has no record of it. In-game '
                           'verification in process.">!</i>')
                elif d["unverified"]:
                    mk += ('<i class="q" title="no icon on the spell db '
                           '— may not exist in game">?</i>')
                mask = d["mask"]
                # NAME THE SPEC. Do not encode it.
                #
                # This cell used to carve itself into one slice per spec and
                # light the ones that could press it. Nobody could read it --
                # a lit quarter-tile is a quantity, and the question is not
                # "how many specs" but "WHICH". Cutting the two rails freed
                # ~350px, the cells went from 82px to ~140px, and at that width
                # the answer just fits as a word.
                #
                # Two names print in full; three or more would set two lines
                # deep in a table that is already 21 rows, so those fall back
                # to a count with the names on the tooltip.
                sl = ""
                if not all(mask):
                    names = cspecs[c][0]
                    lit = [n for n, ok in zip(names, mask) if ok]
                    label = (", ".join(lit) if len(lit) <= 2
                             else f"{len(lit)} of {len(mask)} specs")
                    sl = f'<b class="spn">{esc(label)}</b>'
                    tip = (f'{d["names"]} — {sum(mask)} of {len(mask)} '
                           f'specs: {", ".join(lit)}')
                else:
                    tip = d["names"]
                # data-l is the column name printed inside the cell on a
                # phone, where the header row is off to the side of a scroll.
                A(f'<td class="mxv b-{band}{bs}'
                  f'{" unv" if d["unverified"] or d["pending"] else ""}'
                  f'{" pend" if d["pending"] else ""}'
                  f'{" part" if not all(mask) else ""}" '
                  f'title="{esc(tip)}" data-l="{esc(short)}" '
                  f'data-ids="{",".join(d["ids"])}" '
                  f'data-specs="{"".join("1" if m else "0" for m in mask)}">'
                  f'<span class="cd">{d["cd"]}</span>{mk}{sl}</td>')
        A('</tr>')

        # ---- .kit: the class-first view. Question 5 lives here.
        A(f'<tr class="kitrow" data-class="{esc(c)}" hidden>'
          f'<td colspan="{NCOL}"><div class="kit" style="--c:{acc[c]}">')
        for band, label, cs in BANDS:
            present = [cat for cat, _s, _n, _h in cs if cat in have]
            if not present:
                continue
            if band == "trash":
                # One dim line. A class's stuns must not occupy a third of its
                # kit panel when the question is "what does it bring to a boss".
                bits = []
                for cat in present:
                    for r in sorted([r for r in by_cat[cat] if r[1] == c],
                                    key=lambda r: cd_secs(r[8])):
                        bits.append(f'<a href="{r[5]}" target="_blank" '
                                    f'rel="noopener noreferrer">'
                                    f'{esc(r[4])}</a> '
                                    f'<i>{esc(SHORT[cat])} {cd_short(r[8])}</i>')
                A(f'<p class="kittrash"><b>Trash only</b> '
                  f'{" &nbsp;/&nbsp; ".join(bits)}</p>')
                continue
            A(f'<div class="kitband kb-{band}"><p class="kbl">{esc(label)}</p>')
            for cat in present:
                rows = sorted([r for r in by_cat[cat] if r[1] == c],
                              key=lambda r: cd_secs(r[8]))
                A(f'<p class="kcat">{esc(LONG[cat])}</p>'
                  f'<ul class="ablist tight">')
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
          '<span class="abcls">Class</span>'
          '<span class="abspec">Spec</span>'
          '<span class="abname">Ability</span>'
          '<span class="abwho">In your raid</span>'
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
    for cat in TABCATS:
        band = BAND_OF[cat]
        A(f'<section class="panel pn-{band}" id="panel-{cat}" hidden>')
        A(f'<p class="bandnote bn-{band}">{BANDNOTE[band]}</p>')
        section(cat)
        A('</section>')
    A('</div>')          # /.ovbody
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
                # Which of the class's specs can press this one, as a bitstring
                # aligned to specdata[class].s. The hover card needs it to name
                # the players in tonight's raid who can actually cast it --
                # the cell's own mask is a union over every ability in the
                # cell, so it cannot answer that per-ability.
                "sm": "".join("1" if m else "0"
                              for m in spec_mask(SPECS.get(r[1], []), r[2])),
            }
    A('<script type="application/json" id="abdata">'
      + json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
      + '</script>')

    # ---- spec roster data.
    #
    # `v` is whether the NAMES are trustworthy, and it is false for eighteen of
    # the twenty-one classes. Only Runemaster, Chronomancer and Pyromancer have
    # been played far enough to fill in resources/spec-roles.md; the rest carry
    # db.exil.es tree labels, which are wrong on at least one class -- see
    # class_specs(). The partition is real either way, so the counting is
    # sound; the page marks the words as unconfirmed rather than asserting
    # them.
    specpayload = {c: {"s": cspecs[c][0], "v": cspecs[c][1],
                       "a": aliases_for(c)} for c in classes}
    A('<script type="application/json" id="specdata">'
      + json.dumps(specpayload, separators=(",", ":")).replace("</", "<\\/")
      + '</script>')
    # Raid-Helper calls a spec by a name that is not always the tree label --
    # four of the guild's 69 differ. See resources/spec-aliases.json.
    A('<script type="application/json" id="specalias">'
      + json.dumps(spec_alias_map(), separators=(",", ":")).replace("</", "<\\/")
      + '</script>')
    A('</main>')
    return "\n".join(out)
