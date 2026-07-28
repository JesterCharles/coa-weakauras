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

SITE_TITLE = "Conquest of Azeroth WeakAuras"
REPO = "https://github.com/JesterCharles/coa-weakauras"

# Which classes have shipped packs, and what each pack is.
# `file` is the built artifact in tools/; `slug` is what it becomes in docs/packs/.
SHIPPED = {
    "runemaster": [
        ("All specs", "runemaster-all-specs.txt", "runemaster-coa.txt",
         "Every spec in one pack. Displays load only for the spec you are "
         "currently playing."),
        ("Glyphic", "runemaster-glyphic.txt", "runemaster-glyphic.txt",
         "Glyphic only -- smaller import if you never play the others."),
        ("Engravement", "runemaster-engravement.txt", "runemaster-engravement.txt",
         "Engravement only."),
        ("Riftblade", "runemaster-riftblade.txt", "runemaster-riftblade.txt",
         "Riftblade only."),
    ],
}


def slugify(name):
    return name.lower().replace(" ", "-")


def read_classes():
    """Parse the class table out of resources/ascension-coa-class-ids.md."""
    path = os.path.join(RESOURCES, "ascension-coa-class-ids.md")
    out = []
    for line in open(path):
        m = re.match(r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if not m:
            continue
        cid, name, specs = m.groups()
        out.append({
            "id": int(cid),
            "name": name,
            "slug": slugify(name),
            "specs": [s.strip() for s in specs.split(",")],
        })
    return sorted(out, key=lambda c: c["name"])


def read_tokens():
    """Parse resources/class-tokens.md -> {class name: load token}."""
    path = os.path.join(RESOURCES, "class-tokens.md")
    out = {}
    for line in open(path):
        m = re.match(r"\|\s*\d+\s*\|\s*\**([^|*]+?)\**\s*\|\s*`?([A-Z]+)`?\s*\|",
                     line)
        if m:
            out[m.group(1).strip()] = m.group(2)
    return out


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

def page(title, body, depth=0):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{up}assets/site.css">
</head>
<body>
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
</body>
</html>
"""


def class_card(c, tokens, shipped):
    icon = f"assets/class-icons/{c['slug']}/_class-{c['slug']}.png"
    specs = "".join(
        f'<img src="assets/class-icons/{c["slug"]}/{s}.png" alt="{html.escape(s)}" '
        f'title="{html.escape(s)}" loading="lazy">'
        for s in c["specs"])
    if shipped:
        badge = '<span class="badge ok">Available</span>'
        href = f'{c["slug"]}/index.html'
        tag = "a"
        extra = f' href="{href}"'
    else:
        badge = '<span class="badge soon">Planned</span>'
        tag = "div"
        extra = ""
    return f"""<{tag} class="card{'' if shipped else ' pending'}"{extra}>
  <img class="classicon" src="{icon}" alt="" loading="lazy">
  <div class="cardbody">
    <h3>{html.escape(c['name'])}</h3>
    <div class="specs">{specs}</div>
  </div>
  {badge}
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


def layout_sections(pack_path, class_name):
    """Describe each spec's bands, read straight out of the decoded export.

    Only real bands are listed. The spec container groups sit at y=0 and hold
    other groups rather than displays, so they are skipped -- listing them
    reads as "a band called RM Glyphic at 0" which is meaningless to a player.
    """
    d = wa_decode(open(pack_path).read().strip())
    kids = list(d["c"].values())
    by_id = {k["id"]: k for k in kids}
    by_parent = {}
    for k in kids:
        by_parent.setdefault(k.get("parent"), []).append(k)

    root_id = d["d"].get("id")
    tops = [by_id[i] for i in (d["d"].get("controlledChildren") or {}).values()
            if i in by_id]

    out = []
    for top in tops:
        bands = []
        for g in by_parent.get(top["id"], []):
            if not g.get("controlledChildren"):
                continue
            leaves = [c for c in by_parent.get(g["id"], [])
                      if not c.get("controlledChildren")]
            y = g.get("yOffset")
            if not leaves or not y:
                continue
            # "RM Glyphic Utility Granite Resolve" -> "Granite Resolve"
            names = []
            for c in leaves:
                n = c["id"]
                if n.startswith(g["id"]):
                    n = n[len(g["id"]):].strip()
                # Core leaves are named "RM Alert No Engraving" against a band
                # called "RM Alerts", so the prefix strip above misses them.
                n = re.sub(r"^RM\s+", "", n)
                names.append(n or c["id"])
            preview = ", ".join(names[:6])
            if len(names) > 6:
                preview += f" &hellip; +{len(names) - 6} more"
            label = g["id"]
            if label.startswith(top["id"]):
                label = label[len(top["id"]):].strip() or label
            label = re.sub(r"^RM\s+", "", label)
            bands.append((int(y), label, len(leaves), preview))

        if not bands:
            continue
        bands.sort(key=lambda b: -b[0])
        rows = "\n".join(
            f"<tr><td class='b'>{html.escape(lbl)}</td>"
            f"<td class='num'>{y}</td><td class='num'>{n}</td>"
            f"<td class='items'>{prev}</td></tr>"
            for y, lbl, n, prev in bands)
        title = re.sub(r"^RM\s+", "", top["id"])
        if title.lower() == "core":
            title = "Shared (all specs)"
        out.append(f"""<h3 class="specname">{html.escape(title)}</h3>
  <div class="scroll">
    <table>
      <thead><tr><th>Band</th><th>Y</th><th>Icons</th><th>Contents</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </div>""")
    return "\n".join(out)


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

        ver = version_of("build_runemaster.py")
        token = tokens.get(c["name"], "?")
        main_pack = os.path.join(DOCS, "packs", packs[0][2])

        body = f"""<section class="hero">
  <img class="hero-icon" src="../assets/class-icons/{c['slug']}/_class-{c['slug']}.png" alt="">
  <div>
    <p class="eyebrow">Class {c['id']} &middot; loads as <code>{token}</code></p>
    <h1>{html.escape(c['name'])}</h1>
    <p class="lede">Rotation, cooldowns, buffs and reminders for all
      {len(c['specs'])} specs. Displays load only for the class and spec you
      are actually playing, so importing several class packs costs nothing on
      the ones you are not.</p>
    <p><span class="badge ver">{html.escape(ver)}</span></p>
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
{layout_sections(main_pack, c['name'])}
</section>
"""
        out = os.path.join(DOCS, c["slug"], "index.html")
        open(out, "w").write(page(f"{c['name']} — {SITE_TITLE}", body, depth=1))
        print(f"  wrote {c['slug']}/index.html ({len(all_stats)} packs)")

    # ------------------------------------------------------------- index page
    ready = [c for c in classes if c["slug"] in SHIPPED]
    todo = [c for c in classes if c["slug"] not in SHIPPED]
    cards = "\n".join(class_card(c, tokens, True) for c in ready)
    cards += "\n" + "\n".join(class_card(c, tokens, False) for c in todo)

    body = f"""<section class="hero index">
  <div>
    <h1>{SITE_TITLE}</h1>
    <p class="lede">WeakAura packs for Ascension's Conquest of Azeroth custom
       classes. One consistent layout across every class, so learning one pack
       teaches you all of them.</p>
    <p class="lede">Every display is gated to its class and spec, so you can
       import as many as you like &mdash; the ones you are not playing do not
       load and cost nothing.</p>
    <p><span class="badge ok">{len(ready)} available</span>
       <span class="badge soon">{len(todo)} planned</span></p>
  </div>
</section>

<section>
  <h2>Classes</h2>
  <div class="grid">
{cards}
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
