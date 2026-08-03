"""Generate the public GitHub Pages site into docs/.

    python3 tools/mksite.py

Everything is derived -- the class list and spec names come from classes.py
(itself parsed from resources/), the per-class accent colours from the icon art
via iconcolor.py, and the per-pack stats from decoding the built import strings
themselves. There is no hand-maintained list of packs to drift out of date,
which matters at 21 classes x 4 packs.

Load tokens and class ids are deliberately NOT published. They are WeakAuras
and database internals; a player picking a class knows its name and its spec
names, and that is what the page shows and what search matches.

Publishing an update is: build -> mksite -> commit -> push.
"""
import collections
import html
import json
import os
import re
import shutil
import sys

SP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SP)
RESOURCES = os.path.join(ROOT, "resources")
DOCS = os.path.join(ROOT, "docs")

sys.path.insert(0, SP)
from wacodec import wa_decode  # noqa: E402
from classes import CLASSES, built as built_classes  # noqa: E402
from iconcolor import class_icon, colors_for, read_png  # noqa: E402
import hud  # noqa: E402
import rankings  # noqa: E402
import verified  # noqa: E402

# Cosmetic construction gate on the pack pages. NOT SECURITY -- the repo is
# public and every pack is directly fetchable; see docs/assets/gate.js. Set to
# None to remove the gate entirely.
WA_GATE_CODE = "emberfall"

# Where the site's own name in the header points, and it is NOT index.html
# while the packs page is being kept out of sight. Removing "Classes" from the
# nav hid the signpost and left the brand as a second door straight to it --
# every page carried one, including the raid utility, which is the page being
# shared. Set this back to "index.html" when the packs page is ready and both
# routes come back together.
#
# Still not a gate: index.html builds, deploys and is reachable by anyone who
# types it or follows an old link. This is about not pointing at it.
HOME = "raid-utility.html"

NOSCRIPT_UTIL = """<noscript><style>
  /* No JS: the filter box and the roster picker do nothing, so they are not
     offered. EVERYTHING else on this page is server-rendered and works --
     the coverage block, the whole coverage grid, and every ability list.
     Nothing here is JS-only that is not also printed statically.
     (It used to say "the scarcity counts". Those were deleted; the coverage
     block is what replaced them, and it is server-rendered too.) */
  #fbox,#qcount,.tabs,.rhbar{display:none}
  .mxr .open::after,.mxr .pick{display:none}
  /* every panel open, i.e. the long-scroll page it used to be */
  .panel[hidden]{display:block !important}
  /* The one-screen layout is a JS-era shape: it locks `main` to the viewport
     and lets only the grid scroll, which is right when tabs can swap what is
     in that box and wrong when all eleven panels are stacked open. Hand the
     page back its own scrollbar. */
  .util.uwide{height:auto;overflow:visible;max-width:1760px;margin:0 auto;
    padding-bottom:80px}
  .mxwrap{overflow-x:auto;overflow-y:visible;flex:none}
  .ovbody,.panel.on{display:block}
</style></noscript>"""

SITE_TITLE = "Conquest of Azeroth WeakAuras"
TAGLINE = ("WeakAura packs for all 21 Ascension Conquest of Azeroth custom "
           "classes. One layout, every class, gated so unused packs cost "
           "nothing.")
REPO = "https://github.com/JesterCharles/coa-weakauras"

# Which classes have shipped packs, and what each pack is.
# `file` is the built artifact in tools/packs/<slug>/; `slug` is what it becomes
# in docs/packs/<slug>/. Both sides are per-class folders holding the same
# filenames, so the copy below is a straight move between two mirrored trees.
# Derived from classes.py -- a class appears here as soon as it has a builder on
# disk, so there is no second list to keep in step.
SHIPPED = {
    c.slug: [("All specs", f"{c.slug}-all-specs.txt", f"{c.slug}-coa.txt",
              "Every spec in one pack. Displays load only for the spec you are "
              "currently playing.")] +
            [(c.spec_label(sp), f"{c.slug}-{sp}.txt", f"{c.slug}-{sp}.txt",
              f"{c.spec_label(sp)} only." if i else
              f"{c.spec_label(sp)} only — smaller import if you never "
              f"play the others.")
             for i, sp in enumerate(c.specs)]
    for c in built_classes()
}


def slugify(name):
    return name.lower().replace(" ", "-")


def read_classes():
    """Class list for the site, sourced from classes.py so the slugs, specs and
    ids match every other tool. Kept as plain dicts because the page builders
    below index into them."""
    return sorted(({"id": c.id, "name": c.name, "slug": c.slug,
                    "specs": c.specs,
                    "labels": {s: c.spec_label(s) for s in c.specs}}
                   for c in CLASSES.values()),
                  key=lambda c: c["name"])


def version_of(builder):
    """Read VERSION out of a builder script."""
    src = open(os.path.join(SP, builder)).read()
    m = re.search(r'^VERSION = "([^"]+)"', src, re.M)
    return m.group(1) if m else "?"


def pack_stats(path):
    """Decode a built pack and describe what is in it."""
    d = wa_decode(open(path).read().strip())
    kids = list(d["c"].values())
    leaves = [k for k in kids if not k.get("controlledChildren")]
    groups = [k for k in kids if k.get("controlledChildren")]
    triggers = 0
    for k in leaves:
        triggers += sum(1 for i in k.get("triggers", {}) if isinstance(i, int))
    return {
        "displays": len(kids),
        "leaves": len(leaves),
        "groups": len(groups),
        "triggers": triggers,
        "bytes": os.path.getsize(path),
        "root": d["d"].get("id", ""),
    }


# ----------------------------------------------------------------- templates

def page(title, body, depth=0, accent=None, desc=TAGLINE, gate=False,
         extra_css=(), extra_js=(), head_extra="", header_title=""):
    """Wrap a body in the site chrome.

    `body` is everything between the header and the footer, including its own
    <main> if it wants one. It is NOT wrapped here, because the class page
    opens with a full-bleed colour masthead that has to escape the centred
    content column.

    `header_title` puts the page's own name in the CENTRE of the site header.
    Only the raid-utility page uses it: that page is one screen with no room
    for a masthead, and its <h1> was sitting in the same row as eleven tabs, a
    filter and the raid control, taking ~130px the tabs needed. Pages that pass
    nothing render the header exactly as before.

    `accent` is a (hex, deep-hex) pair written onto <body> as --c/--cd. Every
    accent-coloured rule in site.css reads it, so a class page is tinted
    throughout by whose page it is; the index leaves it at the default and each
    row carries its own.
    """
    up = "../" * depth
    tint = ""
    if accent:
        tint = f' style="--c:{accent[0]};--cd:{accent[1]}"'
    # Cosmetic gate, pack pages only. The attribute is what gate.js reads; the
    # content still ships in the HTML, which is exactly why this is a speed
    # bump and not security. See docs/assets/gate.js.
    if gate and WA_GATE_CODE:
        tint += f' data-gate="{html.escape(WA_GATE_CODE)}"'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="color-scheme" content="light">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="{up}assets/site.css">
{"".join(f'<link rel="stylesheet" href="{up}assets/{c}">' for c in extra_css)}
{head_extra}
</head>
<body{tint}>
<header class="site{" haspt" if header_title else ""}">
  <a class="brand" href="{up}{HOME}">
    <span class="mark">CoA</span>
    <span>WeakAuras</span>
  </a>
  {f'<span class="ptitle">{html.escape(header_title)}</span>' if header_title else ''}
  <nav>
    <!-- Classes is OFF THE NAV on purpose: the WeakAuras packs page is not
         ready to be shown yet. This hides the signpost, it does not gate the
         page -- index.html still builds, still deploys, and .brand above still
         links to it. If it must be genuinely unreachable it needs the gate,
         not a missing nav item. -->
    <a href="{up}raid-utility.html">Raid utility</a>
    <a href="{REPO}">GitHub</a>
  </nav>
</header>
{body}
<footer>
  <p>Unofficial community tool for Ascension Conquest of Azeroth.
     Not affiliated with Blizzard Entertainment.
     <a href="{REPO}/blob/main/NOTICE">Data sources</a>.</p>
</footer>
{"".join(f'<script src="{up}assets/{j}"></script>' for j in extra_js)}
<script src="{up}assets/gate.js"></script>
<script src="{up}assets/copy.js"></script>
<script src="{up}assets/search.js"></script>
<script src="{up}assets/hud.js"></script>
<script src="{up}assets/rankings.js"></script>
</body>
</html>
"""


def class_tile(c, shipped, colors):
    """One icon in the roster band.

    Just the art, at the texture's own 56px, flush against its neighbours --
    the same shape a WeakAuras dynamic group draws. The name, specs and status
    live in the tooltip and the readout, which is how the game surfaces them
    too; putting them on the tile would turn the band back into a card grid.

    Load tokens and class ids are WeakAuras and database internals: not shown,
    not searchable.
    """
    slug = c["slug"]
    col = colors[slug]
    icon = f"assets/class-icons/{slug}/_class-{slug}.png"
    labels = [c["labels"][s] for s in c["specs"]]
    spec_icons = [f"assets/class-icons/{slug}/{s}.png" for s in c["specs"]]

    href = f"{slug}/index.html"
    tag, extra = ("a", f' href="{href}"') if shipped else ("button", ' type="button"')
    state = "ready" if shipped else "planned"

    return f"""<{tag} class="cls {state}"{extra}
  style="--c:{col['accent']}"
  data-name="{html.escape(c['name'], quote=True)}"
  data-specs="{html.escape(' '.join(labels), quote=True)}"
  data-spec-labels="{html.escape('|'.join(labels), quote=True)}"
  data-spec-icons="{html.escape('|'.join(spec_icons), quote=True)}"
  data-icon="{icon}"
  data-href="{href}"
  data-accent="{col['accent']}"
  data-state="{state}"
  aria-label="{html.escape(c['name'], quote=True)}"
><img src="{icon}" alt="" loading="lazy" width="56" height="56"></{tag}>"""


def pack_block(label, pack_file, stats, desc, idx, version="",
               verified_ok=True):
    """One downloadable pack.

    The version is shown because it is the only way to answer "is this newer
    than what I already imported". It is the SAME string the pack writes into
    its WeakAuras group name, so the page and the in-game list agree: you read
    "v1.1" here and see "Chronomancer [CoA] v1.1" in /wa. Before that pairing
    existed a delivered file could only be identified by recomputing uids.
    """
    ver = (f' &middot; <span class="packver">v{html.escape(version)}</span>'
           if version else "")
    if version and not verified_ok:
        # Said on the pack itself, not in a footnote. A player deciding whether
        # to import needs it at the point of decision.
        ver += (' &middot; <span class="packver unver" '
                'title="Generated and validated, but nobody has loaded this '
                'exact version in game yet">not verified in game</span>')
    return f"""<article class="pack">
  <div class="packhead">
    <h3>{html.escape(label)}</h3>
    <span class="meta">{stats['displays']} displays &middot;
      {stats['triggers']} triggers &middot;
      {stats['bytes'] // 1024} KB{ver}</span>
  </div>
  <p class="desc">{html.escape(desc)}</p>
  <div class="actions">
    <button class="copy" data-src="../packs/{pack_file}" id="copy{idx}">
      Copy import string
    </button>
    <a class="dl" href="../packs/{pack_file}" download>Download .txt</a>
  </div>
</article>"""


def rankings_panel(c):
    """Top logged parses per encounter category, with links out to the source.

    Every layer is rendered server-side and only visibility changes, the same
    way hud_preview works, so the panel is readable with JS off -- you get the
    Overall list, which is the right default anyway.

    LINKS OUT, NEVER SCRAPES. coa.ascensionlogs.gg publishes
    `Content-Signal: use=reference` and blocks programmatic API reads, so the
    rows here are transcribed by a person and every one of them carries a link
    back to the character it came from. See tools/sources.py.

    An empty category is rendered as a STATEMENT, not as a blank. "Nobody has
    cleared this yet" and "we failed to collect anything" look identical in an
    empty table and mean opposite things, and Zul'Gurub released the same day
    this shipped -- so the note field says which it is.
    """
    info = CLASSES.get(c["slug"])
    rec = rankings.load(info) if info else None
    if rec is None:
        return ""
    if rankings.validate(info, rec):
        # A malformed record would render as confident nonsense about real
        # named players. Drop the panel and say so in the build output.
        print(f"  !! {c['slug']}: rankings file invalid, panel omitted "
              f"(python3 tools/rankings.py {c['slug']} --validate)")
        return ""

    src = html.escape(rec.get("source_url") or "", quote=True)
    cats, layers = [], []
    for i, (key, _default_label) in enumerate(rankings.CATEGORIES):
        cat = (rec.get("categories") or {}).get(key) or {}
        label = cat.get("label") or _default_label
        entries = sorted(cat.get("entries") or [],
                         key=lambda e: e.get("rank", 99))
        cats.append(
            '<button class="rankcat{on}" type="button" data-cat="{k}" '
            'aria-pressed="{p}">{lbl}</button>'.format(
                on=" on" if i == 0 else "", k=html.escape(key, quote=True),
                p="true" if i == 0 else "false", lbl=html.escape(label)))

        if entries:
            rows = []
            for e in entries:
                b = e.get("build") or {}
                st = b.get("status", "unknown")
                who = html.escape(str(e.get("character", "?")))
                link = e.get("armory_url")
                who_html = (f'<a href="{html.escape(link, quote=True)}" '
                            f'rel="nofollow noopener" target="_blank">{who}</a>'
                            if link else who)
                badge = "" if st == "matches" else (
                    f'<span class="rankflag rank-{html.escape(st)}">'
                    f'{html.escape(st)}</span>')
                rows.append(
                    f'<tr><td class="rankn">{html.escape(str(e.get("rank","")))}</td>'
                    f'<td>{who_html}</td>'
                    f'<td>{html.escape(str(c["labels"].get(e.get("spec",""), e.get("spec","")or""))) }</td>'
                    f'<td class="rankv">{html.escape(str(e.get("value","") or ""))}</td>'
                    f'<td>{badge}</td></tr>')
            inner = ('<table class="ranktable"><thead><tr><th>#</th>'
                     '<th>Character</th><th>Spec</th><th>Metric</th>'
                     '<th>Build</th></tr></thead><tbody>'
                     + "".join(rows) + "</tbody></table>")
        else:
            note = cat.get("note") or (
                "Nothing collected for this bracket yet.")
            inner = f'<p class="rankempty">{html.escape(note)}</p>'
        layers.append(
            '<div class="ranklayer{on}" data-cat="{k}">{inner}</div>'.format(
                on=" on" if i == 0 else "",
                k=html.escape(key, quote=True), inner=inner))

    stamp = rec.get("collected_at")
    prov = (f"Read by hand from the rankings on {html.escape(stamp)}."
            if stamp else "Nothing transcribed yet.")
    return f"""
<section id="ranks">
  <p class="lbl">Who is actually clearing content</p>
  <h2>Top logs</h2>
  <p class="desc">Where the defaults come from. Sidekick says what a class can
     do and says outright that optimal order is unsettled; the official builder
     says what a build can reach; these are the people doing it. A parse whose
     talents match no published build is flagged, because that is the
     interesting case, not a broken row.</p>
  <div class="rankcats" role="group" aria-label="Encounter">{''.join(cats)}</div>
  {''.join(layers)}
  <p class="note">{prov} Source:
     <a href="{src}" rel="nofollow noopener" target="_blank">Conquest of
     Azeroth Logs</a>. We link to it and do not crawl it.</p>
</section>
"""


def hud_preview(c, packs):
    """A to-scale drawing of the pack as it lands on screen.

    Every display is placed at the xOffset/yOffset/width/height it will really
    occupy, resolved through the dynamic-group layout by tools/hud.py, with the
    actual spell art where it is cached. This is the one thing a screenshot of
    somebody else's UI cannot tell you: how much room the pack takes, and where.

    Drawn per SPEC, never from the all-specs pack. That file holds every spec's
    displays at once, a state no player is ever in -- it would render three
    rotations stacked on one bar.

    Two modes, both true and worth contrasting:
      play -- only displays that stay on screen. This is your HUD.
      all  -- adds the active-only buff and alert rows, which is what the pack
              CAN draw. Those rows re-centre as auras come and go, so the wide
              spread is a maximum, not a resting state.
    """
    spec_packs = [(label, os.path.join(DOCS, "packs", c["slug"], published))
                  for label, _built, published, _desc in packs[1:]]
    spec_packs = [(l, p) for l, p in spec_packs if os.path.exists(p)]
    if not spec_packs:
        return ""

    # One coordinate frame per mode, shared by every spec, so switching spec
    # compares like with like instead of rescaling under you.
    data = {}
    for mode, persistent in (("play", True), ("all", False)):
        per_spec = {label: hud.displays(path, only_persistent=persistent)
                    for label, path in spec_packs}
        every = [d for items in per_spec.values() for d in items]
        data[mode] = (hud.bounds(every), per_spec)

    tabs = "".join(
        '<button class="hudspec{on}" type="button" data-spec="{slug}" '
        'aria-pressed="{pressed}">{label}</button>'.format(
            on=" on" if i == 0 else "",
            slug=html.escape(label, quote=True),
            pressed="true" if i == 0 else "false",
            label=html.escape(label))
        for i, (label, _p) in enumerate(spec_packs))

    layers = []
    for mode, (bx, per_spec) in data.items():
        x0, y0, x1, y1 = bx
        span_x, span_y = (x1 - x0) or 1, (y1 - y0) or 1
        # Namespace prefix for this class's display ids ("RM", "CM", ...).
        _ids = [d["id"] for ds in per_spec.values() for d in ds if " " in d["id"]]
        tile_prefix = (collections.Counter(i.split(" ", 1)[0] for i in _ids)
                       .most_common(1)[0][0] if _ids else "")
        for i, (label, _p) in enumerate(spec_packs):
            tiles = []
            for d in per_spec[label]:
                left = (d["x"] - x0) / span_x * 100
                top = (y1 - d["y"]) / span_y * 100
                w = d["w"] / span_x * 100
                h = d["h"] / span_y * 100
                # Was hardcoded to strip "RM ", so every Chronomancer tile
                # tooltip read "CM Artificer Main Shatter Echo".
                band = d.get("band", "")
                if band.startswith(tile_prefix):
                    band = band[len(tile_prefix):].strip()
                for _sp in c["labels"].values():
                    if band.startswith(_sp + " "):
                        band = band[len(_sp):].strip()
                name = _ability_name(d["id"], tile_prefix, band,
                                     list(c["labels"].values()))
                cls = "t" + (" bar" if d["kind"] == "aurabar" else "")
                pos = (f"--l:{left:.3f}%;--t:{top:.3f}%;"
                       f"--w:{w:.3f}%;--h:{h:.3f}%")
                extra = ""
                if d["icon"]:
                    pos += (f";background-image:url(../assets/spell-icons/"
                            f"{d['icon']}.jpg)")
                elif d["kind"] != "icon":
                    # A resource bar or a glyph slot has no icon by definition,
                    # so it is not a missing-art case. Drawing the lettered
                    # placeholder on one makes a bar look like a broken icon.
                    cls += " slot" if d["kind"] != "aurabar" else ""
                else:
                    # Ascension ships custom textures that are on no icon CDN.
                    # Draw a rune tile with the ability's initial rather than a
                    # broken image.
                    cls += " noart"
                    extra = (' data-letter='
                             f'"{html.escape(name[:1].upper(), quote=True)}"')
                tiles.append(f'<i class="{cls}"{extra} '
                             f'title="{html.escape(name, quote=True)}" '
                             f'style="{pos}"></i>')
            layers.append(
                f'<div class="hudlayer{" on" if (i == 0 and mode == "play") else ""}"'
                f' data-mode="{mode}"'
                f' data-spec="{html.escape(label, quote=True)}"'
                f' style="aspect-ratio:{span_x:.2f} / {span_y:.2f}">'
                f'{"".join(tiles)}</div>')

    return f"""<div class="hud" id="hud">
  <div class="hudbar">
    <div class="hudspecs" role="group" aria-label="Spec">{tabs}</div>
    <div class="hudmodes" role="group" aria-label="What to show">
      <button class="hudmode on" type="button" data-mode="play"
              aria-pressed="true">In play</button>
      <button class="hudmode" type="button" data-mode="all"
              aria-pressed="false">Everything</button>
    </div>
  </div>
  <div class="hudscreen">
    <span class="hudaxis">below your character</span>
{chr(10).join(layers)}
  </div>
  <p class="hudnote">
    Drawn to scale straight from the import string, at the size and position
    the pack really uses. <b>In play</b> shows only what stays on screen.
    <b>Everything</b> adds the buff and alert rows, which are active-only
    &mdash; in play they hold just the auras that are up, and the row
    re-centres as they come and go.
  </p>
</div>"""


def _pack_prefix(tops):
    """The display-id namespace this pack uses -- "RM", "CM", ...

    Every builder namespaces its displays with the class's initials so two
    installed packs cannot collide on a display id. It was hardcoded to "RM"
    here, which meant Chronomancer rendered every band label and every ability
    name with the raw prefix still attached, and scope_of() below could never
    match a spec container so all 12 bands claimed to be "Shared".
    """
    first = [t["id"].split(" ", 1)[0] for t in tops if " " in t["id"]]
    return collections.Counter(first).most_common(1)[0][0] if first else ""


def _ability_name(leaf_id, prefix, band_label, spec_labels):
    """"CM Artificer Utility Time Out!" -> "Time Out!".

    Longest-prefix match against the id shapes a builder actually emits, and
    it strips ONCE. The previous version stripped each spec label and the band
    label off the front repeatedly wherever they matched, which is fine until a
    class has a spec whose name is also an English word: Chronomancer's TIME
    spec turned "Time Out!" into "Out!" and "Time Loop" into "Loop".

    Matching whole id prefixes rather than loose words cannot do that -- after
    "CM Artificer Utility " comes off, nothing further is stripped.
    """
    band = band_label.strip()
    cands = []
    for sp in spec_labels:
        cands.append(f"{prefix} {sp} {band} ")
        cands.append(f"{prefix} {sp} ")
    cands += [f"{prefix} {band} ", f"{prefix} "]
    for c in sorted(cands, key=len, reverse=True):
        if c.strip() and leaf_id.startswith(c):
            return leaf_id[len(c):].strip() or leaf_id
    return leaf_id


def _band_preview(group_id, leaves, band_label="", spec_labels=(), prefix="RM"):
    """The first few ability names in a band, for the Layout table."""
    names = []
    for c in leaves:
        n = c["id"]
        if n.startswith(group_id):
            n = n[len(group_id):].strip()
        names.append(_ability_name(n if n != c["id"] else c["id"],
                                   prefix, band_label, spec_labels)
                     or c["id"])
    preview = ", ".join(html.escape(n) for n in names[:6])
    if len(names) > 6:
        preview += f" &hellip; +{len(names) - 6} more"
    return preview


def layout_sections(pack_path, spec_labels):
    """One table of every band in the pack, top of screen to bottom.

    A band is any group whose children are displays. Finding them needs two
    shapes, because the final16 band merge changed the tree: bands shared by
    all specs were lifted OUT of the spec containers and are now siblings of
    them at the top level, while a spec container keeps only the displays that
    could not be merged (its resource envelope, and anything whose gate cannot
    be expressed as a single spellknown id).

    The previous version only ever descended one level into the top-level
    containers, so after the merge it rendered 2 bands out of 8 and 17
    displays out of 171 -- the whole main rotation was missing from the page.
    """
    d = wa_decode(open(pack_path).read().strip())
    kids = list(d["c"].values())
    by_id = {k["id"]: k for k in kids}
    by_parent = {}
    for k in kids:
        by_parent.setdefault(k.get("parent"), []).append(k)

    tops = [by_id[i] for i in (d["d"].get("controlledChildren") or {}).values()
            if i in by_id]
    prefix = _pack_prefix(tops)
    specs_lower = {s.lower(): s for s in spec_labels}

    def scope_of(name):
        """A top-level node named for a spec scopes its bands to that spec.
        Everything else -- Core, and the merged bands -- is shared."""
        return specs_lower.get(name.lower(), "Shared")

    bands = []
    for top in tops:
        top_name = top["id"][len(prefix):].strip() if top["id"].startswith(prefix) else top["id"]
        children = by_parent.get(top["id"], [])
        groups = [c for c in children if c.get("controlledChildren")]
        leaves = [c for c in children if not c.get("controlledChildren")]

        # Shape A: a container of bands (RM Core, and pre-merge packs).
        for g in groups:
            gl = [c for c in by_parent.get(g["id"], [])
                  if not c.get("controlledChildren")]
            y = g.get("yOffset")
            if not gl or not y:
                continue
            label = g["id"]
            if label.startswith(top["id"]):
                label = label[len(top["id"]):].strip() or label
            if label.startswith(prefix):
                label = label[len(prefix):].strip() or label
            bands.append((int(y), label, scope_of(top_name), len(gl),
                          _band_preview(g["id"], gl, label, spec_labels,
                                        prefix)))

        # Shape B: the node IS a band -- displays hang directly off it. Its own
        # yOffset is 0 for a spec container, so the anchor comes from the
        # displays; the topmost one is what the player sees the band start at.
        if leaves:
            y = top.get("yOffset") or max(
                (int(c.get("yOffset") or 0) for c in leaves), default=0)
            if y:
                bands.append((int(y), top_name, scope_of(top_name),
                              len(leaves),
                              _band_preview(top["id"], leaves, top_name,
                                            spec_labels, prefix)))

    if not bands:
        return ""

    # Least-negative y first: WeakAuras yOffset counts down from the player, so
    # this is literally top of screen to bottom.
    bands.sort(key=lambda b: -b[0])
    rows = "\n".join(
        f"<tr><td class='b'>{html.escape(lbl)}</td>"
        f"<td class='sc'>{html.escape(scope)}</td>"
        f"<td class='num'>{y}</td><td class='num'>{n}</td>"
        f"<td class='items'>{prev}</td></tr>"
        for y, lbl, scope, n, prev in bands)
    total = sum(b[3] for b in bands)
    return f"""<div class="scroll">
    <table>
      <thead><tr><th>Band</th><th>Shown for</th><th>Y</th><th>Icons</th>
        <th>Contents</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </div>
  <p class="desc">{len(bands)} bands, {total} displays.
     &ldquo;Shared&rdquo; bands render for every spec &mdash; each one draws
     only the icons the spec you are playing has loaded.</p>"""


# --------------------------------------------------------------------- build

_verified_ok = {}


def _check_verified(classes, allow_unverified):
    """Refuse to publish a pack nobody has loaded in game, unless told to.

    docs/ IS the distribution: GitHub Pages serves it, so copying a build into
    docs/packs/ and committing is a release. Regenerating the site therefore
    shipped whatever had just been built, and nothing recorded whether a human
    had ever seen it work. Chronomancer 1.1 went live carrying six untested
    displays exactly that way.

    Not a wall -- an unverified pack can still ship, because that is what the
    alpha channel will be. It just cannot ship SILENTLY: you pass the flag, and
    the page says so on every affected pack.
    """
    _verified_ok.clear()
    unverified = []
    for c in classes:
        if c["slug"] not in SHIPPED:
            continue
        v = version_of(f"build_{c['slug']}.py")
        ok, detail = verified.status(CLASSES[c["slug"]], v)
        _verified_ok[c["slug"]] = ok
        if not ok:
            unverified.append(f"{c['name']} v{v}: {detail}")
    if not unverified:
        return
    print("  unverified packs:")
    for u in unverified:
        print(f"    {u}")
    if not allow_unverified:
        raise SystemExit(
            "\nmksite: refusing to publish -- docs/ is what players download.\n"
            "  Verify in game and record it:\n"
            "    python3 tools/verified.py record <class> <version> --by you "
            "--spec <each spec>\n"
            "  Or publish anyway, with a visible badge on each affected pack:\n"
            "    python3 tools/mksite.py --allow-unverified")
    print("  --allow-unverified: publishing anyway, badged on the page")


UTILITY_INTRO = (
    "Who brings an interrupt, a battle rez, a purge, a spellsteal and an "
    "enrage removal &mdash; across all 21 Conquest of Azeroth classes. "
    "Classified by spell effect id from db.exil.es, not by tooltip text. "
    "Every ability links to its spell page.")


def utility_tables_page():
    """The raid-utility page body. See tools/utility_page.py for the design.

    Returns None if the local spell mirror under tools/spellchk/ is absent, so
    a fresh clone still builds the rest of the site -- that directory is
    gitignored and holds ~12k cached API responses.
    """
    try:
        from utility_page import render
        return render()
    except Exception as e:                       # noqa: BLE001
        print(f"  !! raid utility page skipped: {e}")
        return None


def _md_inline(t):
    """Just enough inline markdown for the generated notes: `code` and **bold**."""
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t.replace("\n\n", "<br><br>")


def build_utility_only():
    """Write docs/raid-utility.html and touch NOTHING else.

    The full build republishes every pack, and the verified gate rightly
    refuses while any class is unconfirmed in game. That gate is about packs
    players download; the utility page is generated reference data and shares
    none of that risk. Separating them means a pending class cannot hold the
    page hostage, and adding the page cannot smuggle an unverified pack onto
    the live site as a side effect.
    """
    util = utility_tables_page()
    if not util:
        raise SystemExit("no raid-utility page produced")
    out = os.path.join(DOCS, "raid-utility.html")
    open(out, "w", encoding="utf-8").write(page(
        "Raid utility - CoA", util, depth=0,
        desc="Interrupts, battle rezzes, purges, spellsteals and enrage "
             "removals across all 21 CoA classes.",
        extra_css=("raid-utility.css",), extra_js=("raid-utility.js",),
        header_title="Raid utility",
        head_extra=NOSCRIPT_UTIL))
    print(f"  wrote {out}")
    return 0


def build(allow_unverified=False):
    os.makedirs(os.path.join(DOCS, "packs"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "assets"), exist_ok=True)

    # Class icons live in docs/assets/class-icons/ and are tracked there
    # directly -- Pages only serves docs/, so keeping a second copy outside it
    # would just duplicate ~1 MB of PNGs for nothing.

    classes = read_classes()
    _check_verified(classes, allow_unverified)
    if not classes:
        raise SystemExit("no classes parsed -- check ascension-coa-class-ids.md")

    # One accent per class, read out of that class's own icon. See
    # tools/iconcolor.py -- nothing here or in the CSS names a colour, so a new
    # class is coloured the moment its art lands in docs/assets/class-icons/.
    colors = colors_for([c["slug"] for c in classes])

    # The site renders class art up to 72px. Most icons are 56x56, which
    # upscales acceptably; anything smaller is visibly soft on the class page
    # hero. Warn rather than fail -- a soft icon is a blemish, not a broken
    # build, and blocking the site on missing art would be worse.
    for c in classes:
        icon = class_icon(c["slug"])
        if not os.path.exists(icon):
            print(f"  !! no class icon: {c['slug']}")
            continue
        w, h, _px = read_png(icon)
        if min(w, h) < 56:
            print(f"  !! {c['slug']} class icon is {w}x{h}, want 56x56 "
                  f"(renders soft at 72px)")

    # ------------------------------------------------------- raid utility
    util = utility_tables_page()
    if util:
        open(os.path.join(DOCS, "raid-utility.html"), "w",
             encoding="utf-8").write(page(
        "Raid utility - CoA", util, depth=0,
        desc="Interrupts, battle rezzes, purges, spellsteals and enrage "
             "removals across all 21 CoA classes.",
        extra_css=("raid-utility.css",), extra_js=("raid-utility.js",),
        header_title="Raid utility",
        head_extra=NOSCRIPT_UTIL))
        print("  wrote raid-utility.html")

    # -------------------------------------------------- per-class pack pages
    for c in classes:
        packs = SHIPPED.get(c["slug"])
        if not packs:
            continue
        os.makedirs(os.path.join(DOCS, c["slug"]), exist_ok=True)
        # One folder per class. Flat, 21 classes x 4 packs is 84 files in one
        # directory with the class name repeated in every filename.
        os.makedirs(os.path.join(DOCS, "packs", c["slug"]), exist_ok=True)

        blocks, all_stats = [], []
        for i, (label, built, published, desc) in enumerate(packs):
            src = os.path.join(SP, "packs", c["slug"], built)
            if not os.path.exists(src):
                print(f"  !! missing build artifact: {built}")
                continue
            dst = os.path.join(DOCS, "packs", c["slug"], published)
            shutil.copy2(src, dst)
            st = pack_stats(dst)
            all_stats.append(st)
            # href is relative to docs/<class>/index.html
            blocks.append(pack_block(
                label, f"{c['slug']}/{published}", st, desc, i,
                version=version_of(f"build_{c['slug']}.py"),
                verified_ok=_verified_ok.get(c["slug"], True)))

        main_pack = os.path.join(DOCS, "packs", c["slug"], packs[0][2])
        head = all_stats[0] if all_stats else {"displays": 0, "triggers": 0}
        spec_line = ", ".join(c["labels"][s] for s in c["specs"])

        body = f"""<div class="classhead">
  <div class="inner">
    <img src="../assets/class-icons/{c['slug']}/_class-{c['slug']}.png"
         alt="" width="96" height="96">
    <div>
      <p class="kicker">Conquest of Azeroth</p>
      <h1>{html.escape(c['name'])}</h1>
      <p class="specline">{html.escape(spec_line)}</p>
    </div>
  </div>
</div>

<main class="wrap">
<section>
  <p class="lbl">What lands on your screen</p>
  <h2>The pack, drawn to scale</h2>
  <p class="desc">Rotation, cooldowns, buffs and reminders for all
     {len(c['specs'])} specs. Displays load only for the class and spec you are
     actually playing, so importing several class packs costs nothing on the
     ones you are not.</p>
{hud_preview(c, packs)}
</section>
{rankings_panel(c)}
<section>
  <p class="lbl">Import</p>
  <h2>Three steps</h2>
  <ol class="steps">
    <li>Copy a string below.</li>
    <li>In game, type <code>/wa</code>.</li>
    <li>Click Import, paste, confirm.</li>
  </ol>
  <p class="note">Re-importing an updated version replaces the old one. If the
     pack looks unchanged after an update, delete the old group first &mdash;
     WeakAuras keeps what it already has when nothing tells it the pack
     moved.</p>
</section>

<section>
  <h2>Packs</h2>
  <p class="desc">Take the all-specs pack unless you only ever play the one
     spec. They are built from the same source and lay out identically.</p>
  <div class="packs">
{chr(10).join(blocks)}
  </div>
</section>

<section>
  <h2>Layout</h2>
  <p class="desc">Bands top to bottom, drawn from the actual import. Things you
     react to within a global sit nearest your character; set-and-forget sits
     furthest away. Buff rows are active-only &mdash; empty until something is
     up, so the pack looks far sparser in play than these counts suggest.</p>
{layout_sections(main_pack, [c['labels'][s] for s in c['specs']])}
</section>
</main>
"""
        out = os.path.join(DOCS, c["slug"], "index.html")
        # gate=True on the PACK pages only. The index and the raid-utility page
        # stay open: the gate exists so nobody imports a half-rebuilt pack by
        # accident, and neither of those hands out a pack.
        open(out, "w").write(page(
            f"{c['name']} — {SITE_TITLE}", body, depth=1,
            accent=(colors[c["slug"]]["accent"], colors[c["slug"]]["deep"]),
            desc=f"{c['name']} WeakAura pack for Ascension Conquest of Azeroth "
                 f"— {head['displays']} displays across "
                 f"{len(c['specs'])} specs ({spec_line}).",
            gate=True))
        print(f"  wrote {c['slug']}/index.html ({len(all_stats)} packs)")

    # ------------------------------------------------------------- index page
    # Shipped classes first, then planned -- both alphabetical. Filtering hides
    # rows within that fixed order rather than re-ranking, so a row never jumps
    # position between two keystrokes; that is what makes arrowing down the
    # list predictable.
    ready = [c for c in classes if c["slug"] in SHIPPED]
    todo = [c for c in classes if c["slug"] not in SHIPPED]
    ordered = ready + todo
    tiles = "\n".join(
        class_tile(c, c["slug"] in SHIPPED, colors) for c in ordered)

    pct = round(len(ready) / max(1, len(classes)) * 100)

    body = f"""<div class="wrap">
  <div class="intro">
    <h1>Every Conquest of Azeroth class,
        <span>one HUD you already know.</span></h1>
    <p>Rotation, cooldowns and buffs sit in the same place on every class, so
       learning one pack teaches you all of them. Each display is gated to its
       class and spec &mdash; import as many as you like and the ones you are
       not playing never load.</p>
  </div>

  <p class="lbl">Pick a class</p>

  <div class="rosterwrap">
    <div class="editbox" id="editbox">
      <span class="slash">/</span>
      <input id="q" type="search" autocomplete="off" spellcheck="false"
             placeholder="class or spec name" aria-label="Search classes">
      <button id="clear" type="button" aria-label="Clear search">&times;</button>
    </div>

    <div class="roster" id="roster">
{tiles}
    </div>

    <div class="bar">
      <div class="bartrack"><div class="barfill" style="width:{pct}%"></div></div>
      <div class="barlbl">
        <span><b>{len(ready)}</b> of {len(classes)} classes built</span>
        <span id="count">{len(classes)} shown</span>
      </div>
    </div>

    <p class="hint">Hover for details &middot; <kbd>/</kbd> to search &middot;
       <kbd>&larr;</kbd><kbd>&rarr;</kbd> to move &middot;
       <kbd>Enter</kbd> to open</p>
  </div>

  <div class="noresult">
    <b>No class by that name.</b>
    Try part of a class name, or a spec like &ldquo;Riftblade&rdquo;.
    <br><button id="reset" type="button">Show all {len(classes)}</button>
  </div>

  <!-- Selected class. Built by search.js from the focused tile. -->
  <div class="readout" id="readout">
    <img class="roportrait" id="roportrait" alt="" width="64" height="64">
    <div>
      <div class="roname" id="roname"></div>
      <div class="rospecs" id="rospecs"></div>
    </div>
    <div id="roaction"></div>
  </div>
</div>

<div class="tip" id="tip" role="tooltip">
  <div class="tipname" id="tipname"></div>
  <p class="tipspecs" id="tipspecs"></p>
  <p class="tipstate" id="tipstate"></p>
</div>
"""
    open(os.path.join(DOCS, "index.html"), "w").write(
        page(SITE_TITLE, body, depth=0))
    print(f"  wrote index.html ({len(ready)} available, {len(todo)} planned)")

    open(os.path.join(DOCS, ".nojekyll"), "w").write("")


if __name__ == "__main__":
    if "--utility-only" in sys.argv:
        sys.exit(build_utility_only())
    build("--allow-unverified" in sys.argv)
    print("\nsite written to docs/")
