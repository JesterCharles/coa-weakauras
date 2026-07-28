"""Generate the public GitHub Pages site into docs/.

    python3 tools/mksite.py

Everything is derived -- the class list comes from
resources/ascension-coa-class-ids.md, the tokens from resources/class-tokens.md,
and the per-pack stats from decoding the built import strings themselves. There
is no hand-maintained list of packs to drift out of date, which matters at 21
classes x 4 packs.

Publishing an update is: build -> mksite -> commit -> push.
"""
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

SITE_TITLE = "Conquest of Azeroth WeakAuras"
TAGLINE = ("WeakAura packs for all 21 Ascension Conquest of Azeroth custom "
           "classes. One layout, every class, gated so unused packs cost "
           "nothing.")
REPO = "https://github.com/JesterCharles/coa-weakauras"

# Which classes have shipped packs, and what each pack is.
# `file` is the built artifact in tools/; `slug` is what it becomes in docs/packs/.
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


def read_tokens():
    """{class display name: load token}, from classes.py."""
    return {c.name: c.token for c in CLASSES.values()}


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

def page(title, body, depth=0, accent=None, desc=TAGLINE):
    """Wrap a body in the site chrome.

    `accent` is a (hex, deep-hex) pair. It is written onto <body> as --c/--cd,
    which every accent-coloured rule in site.css reads. On a class page that is
    the class's own colour, so the whole page is tinted by whose page it is;
    the index leaves it unset and each card carries its own instead.
    """
    up = "../" * depth
    tint = ""
    if accent:
        tint = f' style="--c:{accent[0]};--cd:{accent[1]}"'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="color-scheme" content="dark">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="{up}assets/site.css">
</head>
<body{tint}>
<header class="site">
  <a class="brand" href="{up}index.html">
    <span class="mark">CoA</span>
    <span>WeakAuras</span>
  </a>
  <nav>
    <a href="{up}index.html">Classes</a>
    <a href="{REPO}">GitHub</a>
  </nav>
</header>
<main>
{body}
</main>
<footer>
  <p>Unofficial community tool for Ascension Conquest of Azeroth.
     Not affiliated with Blizzard Entertainment.
     <a href="{REPO}/blob/main/NOTICE">Data sources</a>.</p>
</footer>
<script src="{up}assets/copy.js"></script>
<script src="{up}assets/search.js"></script>
</body>
</html>
"""


def class_card(c, tokens, shipped, colors, i):
    """One tile in the atlas.

    Every searchable field is written as a data- attribute rather than being
    scraped back out of the rendered text -- search.js matches on name, spec
    names, load token and class id, and only the name is visible.
    """
    slug = c["slug"]
    col = colors[slug]
    icon = f"assets/class-icons/{slug}/_class-{slug}.png"
    token = tokens.get(c["name"], "")
    specs = "".join(
        f'<img src="assets/class-icons/{slug}/{s}.png" alt="" '
        f'title="{html.escape(c["labels"][s])}" loading="lazy">'
        for s in c["specs"])

    tag, extra = ("a", f' href="{slug}/index.html"') if shipped else ("div", "")
    state = "ready" if shipped else "planned"
    label = "Available" if shipped else "Planned"

    return f"""<{tag} class="card{'' if shipped else ' pending'}"{extra}
  style="--c:{col['accent']};--cd:{col['deep']};--i:{i}"
  data-name="{html.escape(c['name'], quote=True)}"
  data-specs="{html.escape(' '.join(c['labels'][s] for s in c['specs']), quote=True)}"
  data-token="{html.escape(token, quote=True)}"
  data-id="{c['id']}"
  data-state="{state}">
  <div class="cardtop">
    <img class="classicon" src="{icon}" alt="" loading="lazy" width="52" height="52">
    <span class="cid">{c['id']}</span>
  </div>
  <div class="cardbody">
    <h3>{html.escape(c['name'])}</h3>
    <div class="specs">{specs}</div>
    <p class="token">{html.escape(token)}</p>
  </div>
  <div class="cardfoot">
    <span class="state"><i class="dot"></i>{label}</span>
  </div>
</{tag}>"""


def pack_block(label, pack_file, stats, desc, idx):
    return f"""<article class="pack">
  <div class="packhead">
    <h3>{html.escape(label)}</h3>
    <span class="meta">{stats['displays']} displays &middot;
      {stats['triggers']} triggers &middot;
      {stats['bytes'] // 1024} KB</span>
  </div>
  <p class="desc">{html.escape(desc)}</p>
  <div class="actions">
    <button class="copy" data-src="../packs/{pack_file}" id="copy{idx}">
      Copy import string
    </button>
    <a class="dl" href="../packs/{pack_file}" download>Download .txt</a>
  </div>
</article>"""


def _band_preview(group_id, leaves, band_label="", spec_labels=()):
    """"RM Glyphic Utility Granite Resolve" -> "Granite Resolve", capped.

    Three prefixes have to come off, because a merged band holds displays that
    still carry the name they had when they lived under a spec:
    the "RM " namespace, the spec ("Glyphic"), and the band ("Buffs"). Without
    all three the table reads "Glyphic Buffs Glyphic Overload" instead of
    "Glyphic Overload".
    """
    def strip(n, prefix):
        if prefix and n.lower().startswith(prefix.lower() + " "):
            return n[len(prefix):].strip()
        return n

    names = []
    for c in leaves:
        n = c["id"]
        if n.startswith(group_id):
            n = n[len(group_id):].strip()
        # Core leaves are named "RM Alert No Engraving" against a band called
        # "RM Alerts", so the prefix strip above misses them.
        n = re.sub(r"^RM\s+", "", n)
        for _ in range(2):          # spec then band, in either order
            for p in list(spec_labels) + [band_label]:
                n = strip(n, p)
        names.append(n or c["id"])
    preview = ", ".join(names[:6])
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
    specs_lower = {s.lower(): s for s in spec_labels}

    def scope_of(name):
        """A top-level node named for a spec scopes its bands to that spec.
        Everything else -- Core, and the merged bands -- is shared."""
        return specs_lower.get(name.lower(), "Shared")

    bands = []
    for top in tops:
        top_name = re.sub(r"^RM\s+", "", top["id"])
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
            bands.append((int(y), re.sub(r"^RM\s+", "", label),
                          scope_of(top_name), len(gl),
                          _band_preview(g["id"], gl, label, spec_labels)))

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
                                            spec_labels)))

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

def build():
    os.makedirs(os.path.join(DOCS, "packs"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "assets"), exist_ok=True)

    # Class icons live in docs/assets/class-icons/ and are tracked there
    # directly -- Pages only serves docs/, so keeping a second copy outside it
    # would just duplicate ~1 MB of PNGs for nothing.

    classes = read_classes()
    tokens = read_tokens()
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

    # -------------------------------------------------- per-class pack pages
    for c in classes:
        packs = SHIPPED.get(c["slug"])
        if not packs:
            continue
        os.makedirs(os.path.join(DOCS, c["slug"]), exist_ok=True)

        blocks, all_stats = [], []
        for i, (label, built, published, desc) in enumerate(packs):
            src = os.path.join(SP, built)
            if not os.path.exists(src):
                print(f"  !! missing build artifact: {built}")
                continue
            dst = os.path.join(DOCS, "packs", published)
            shutil.copy2(src, dst)
            st = pack_stats(dst)
            all_stats.append(st)
            blocks.append(pack_block(label, published, st, desc, i))

        ver = version_of(f"build_{c['slug']}.py")
        token = tokens.get(c["name"], "?")
        main_pack = os.path.join(DOCS, "packs", packs[0][2])
        head = all_stats[0] if all_stats else {"displays": 0, "triggers": 0}

        body = f"""<section class="hero">
  <img class="hero-icon" src="../assets/class-icons/{c['slug']}/_class-{c['slug']}.png"
       alt="" width="88" height="88">
  <div>
    <p class="eyebrow">Class {c['id']} &middot; loads as {html.escape(token)}</p>
    <h1>{html.escape(c['name'])}</h1>
    <p class="lede">Rotation, cooldowns, buffs and reminders for all
      {len(c['specs'])} specs. Displays load only for the class and spec you
      are actually playing, so importing several class packs costs nothing on
      the ones you are not.</p>
    <div class="stats">
      <div class="stat"><b>{head['displays']}</b><span>Displays</span></div>
      <div class="stat"><b>{head['triggers']}</b><span>Triggers</span></div>
      <div class="stat"><b>{len(c['specs'])}</b><span>Specs</span></div>
      <div class="stat"><b>{len(all_stats)}</b><span>Packs</span></div>
    </div>
    <p><span class="badge ver">{html.escape(ver)}</span>
       <span class="badge tok">{html.escape(token)}</span></p>
  </div>
</section>

<section>
  <h2>Import</h2>
  <ol class="steps">
    <li>Copy a string below.</li>
    <li>In game type <code>/wa</code>.</li>
    <li>Click <strong>Import</strong>, paste, confirm.</li>
  </ol>
  <p class="note">Re-importing an updated version replaces the old one. If the
     pack looks unchanged after an update, check the version in the group name
     &mdash; WeakAuras keeps the old copy when the version has not moved.</p>
</section>

<section>
  <h2>Packs</h2>
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
"""
        out = os.path.join(DOCS, c["slug"], "index.html")
        open(out, "w").write(page(
            f"{c['name']} — {SITE_TITLE}", body, depth=1,
            accent=(colors[c["slug"]]["accent"], colors[c["slug"]]["deep"]),
            desc=f"{c['name']} WeakAura pack for Ascension Conquest of Azeroth "
                 f"— {head['displays']} displays across "
                 f"{len(c['specs'])} specs, gated to {token}."))
        print(f"  wrote {c['slug']}/index.html ({len(all_stats)} packs)")

    # ------------------------------------------------------------- index page
    # Shipped classes first, then planned -- both alphabetical. Search filters
    # within that order rather than re-ranking, so a card never moves position
    # between two keystrokes, which is what makes arrow-key navigation stable.
    ready = [c for c in classes if c["slug"] in SHIPPED]
    todo = [c for c in classes if c["slug"] not in SHIPPED]
    ordered = ready + todo
    cards = "\n".join(
        class_card(c, tokens, c["slug"] in SHIPPED, colors, i)
        for i, c in enumerate(ordered))

    total_specs = sum(len(c["specs"]) for c in classes)

    body = f"""<section class="hero index">
  <div>
    <p class="eyebrow">Ascension &middot; Conquest of Azeroth</p>
    <h1>Every custom class,<br>one WeakAura layout.</h1>
    <p class="lede">Rotation, cooldowns and buffs for Conquest of Azeroth's
       custom classes. The bands sit in the same place on every pack, so
       learning one teaches you all of them.</p>
    <p class="lede">Each display is gated to its class and spec. Import as many
       as you like &mdash; the ones you are not playing never load.</p>
    <div class="stats">
      <div class="stat"><b>{len(ready)}</b><span>Available</span></div>
      <div class="stat"><b>{len(todo)}</b><span>Planned</span></div>
      <div class="stat"><b>{len(classes)}</b><span>Classes</span></div>
      <div class="stat"><b>{total_specs}</b><span>Specs</span></div>
    </div>
  </div>
</section>

<section>
  <h2>Find your class</h2>
  <div class="finder">
    <div class="searchrow">
      <div class="searchbox" id="searchbox">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="11" cy="11" r="7"></circle>
          <path d="M20 20l-4.2-4.2"></path>
        </svg>
        <input id="q" type="search" autocomplete="off" spellcheck="false"
               placeholder="Search class, spec, or load token&hellip;"
               aria-label="Search classes">
        <button id="clear" type="button" aria-label="Clear search">&times;</button>
        <span class="slash">/</span>
      </div>
      <div class="chips" role="group" aria-label="Filter by availability">
        <button class="chip" type="button" data-show="all"
                aria-pressed="true">All</button>
        <button class="chip" type="button" data-show="ready"
                aria-pressed="false">Available</button>
        <button class="chip" type="button" data-show="planned"
                aria-pressed="false">Planned</button>
      </div>
      <span class="count" id="count"><b>{len(classes)}</b> of {len(classes)} classes</span>
    </div>
  </div>

  <div class="grid" id="grid">
{cards}
  </div>

  <div class="empty">
    <b>No class matches that.</b>
    Search covers class names, spec names and load tokens
    &mdash; try <code>rune</code>, <code>frost</code> or <code>SPIRITMAGE</code>.
    <br><button id="reset" type="button">Show all {len(classes)}</button>
  </div>
</section>
"""
    open(os.path.join(DOCS, "index.html"), "w").write(
        page(SITE_TITLE, body, depth=0))
    print(f"  wrote index.html ({len(ready)} available, {len(todo)} planned)")

    open(os.path.join(DOCS, ".nojekyll"), "w").write("")


if __name__ == "__main__":
    build()
    print("\nsite written to docs/")
