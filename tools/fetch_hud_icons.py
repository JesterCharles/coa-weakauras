"""Fetch the spell icon art a built pack references, for the HUD preview.

    python3 tools/fetch_hud_icons.py                 # every built class
    python3 tools/fetch_hud_icons.py runemaster      # one
    python3 tools/fetch_hud_icons.py --report        # what is cached / missing

The class page draws a to-scale preview of the pack: every display at the
xOffset/yOffset/width/height it will actually occupy on your screen. Boxes
alone would show the geometry; the icon art is what makes it read as the HUD
you are about to import.

Icon names come out of the decoded pack's `displayIcon` field, which is a
`Interface\\Icons\\<texture>` path. Stock WoW textures resolve against
Blizzard's own render CDN. Conquest of Azeroth adds custom art (tattoo_*,
weapon_engraving_*, ...) that exists only on the Ascension client, so a chunk
of every class will always miss -- that is expected, not a failure, and
misses.json records them so the site can draw a labelled placeholder instead
of a broken image.

Cached under docs/assets/spell-icons/ and committed, for the same reason the
rest of resources/ is: these sites change without notice and a build should
not depend on a live fetch.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

SP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SP)
OUT = os.path.join(ROOT, "docs", "assets", "spell-icons")
MISSES = os.path.join(OUT, "misses.json")

sys.path.insert(0, SP)
from wacodec import wa_decode  # noqa: E402
from classes import built as built_classes  # noqa: E402

# Ascension's own database first. It is the only host that carries the custom
# Conquest of Azeroth art (custom_*, 5_mageskill*, _rune*), which is more than
# half of a CoA class -- Blizzard's CDN alone resolved 49 of Runemaster's 113.
# Blizzard's render service and wowhead's mirror follow for stock textures.
SOURCES = [
    "https://db.ascension.gg/static/images/wow/icons/large/{name}.jpg",
    "https://render.worldofwarcraft.com/us/icons/56/{name}.jpg",
    "https://wow.zamimg.com/images/wow/icons/large/{name}.jpg",
]


def icon_names(pack_path):
    """Every distinct displayIcon texture in a built pack, lowercased."""
    d = wa_decode(open(pack_path).read().strip())
    names = set()
    for k in d["c"].values():
        if k.get("controlledChildren"):
            continue
        di = k.get("displayIcon")
        if isinstance(di, str) and di:
            leaf = di.replace("/", "\\").split("\\")[-1].strip().lower()
            if leaf:
                names.add(leaf)
    return names


def fetch(name):
    """-> (name, True) if the art is on disk afterwards."""
    dst = os.path.join(OUT, f"{name}.jpg")
    if os.path.exists(dst) and os.path.getsize(dst) > 500:
        return name, True
    for url in SOURCES:
        r = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "15", "-o", dst, "-w", "%{http_code}",
             url.format(name=name)],
            capture_output=True, text=True)
        if r.stdout.strip() == "200" and os.path.exists(dst) \
                and os.path.getsize(dst) > 500:
            return name, True
    # Leave nothing behind on a miss: a 0-byte or error-page file on disk would
    # be served as a broken image and would also defeat the cache check above.
    if os.path.exists(dst):
        os.remove(dst)
    return name, False


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    report_only = "--report" in argv
    want = [a for a in argv if not a.startswith("-")]

    packs = []
    for c in built_classes():
        if want and c.slug not in want:
            continue
        p = os.path.join(ROOT, "docs", "packs", c.slug, f"{c.slug}-coa.txt")
        if os.path.exists(p):
            packs.append((c.slug, p))
    if not packs:
        raise SystemExit("no built packs found -- run mksite.py first")

    names = set()
    for slug, p in packs:
        got = icon_names(p)
        print(f"  {slug}: {len(got)} distinct icons")
        names |= got
    names = sorted(names)

    if report_only:
        have = [n for n in names if os.path.exists(os.path.join(OUT, f"{n}.jpg"))]
        print(f"\n{len(have)}/{len(names)} cached")
        missing = [n for n in names if n not in set(have)]
        if missing:
            print("missing:", ", ".join(missing[:20]),
                  f"... +{len(missing) - 20}" if len(missing) > 20 else "")
        return

    print(f"\nfetching {len(names)} icons -> docs/assets/spell-icons/")
    ok, miss = [], []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, good in ex.map(fetch, names):
            (ok if good else miss).append(name)

    # Misses are recorded rather than retried every build: custom Ascension art
    # is never going to appear on Blizzard's CDN, and re-requesting 40 known
    # 404s on every run is just noise.
    miss = sorted(miss)
    json.dump(miss, open(MISSES, "w"), indent=1)
    print(f"\n{len(ok)} fetched, {len(miss)} unavailable "
          f"(custom Ascension art -- placeholder is drawn instead)")
    if miss:
        print("  " + ", ".join(miss[:14]) +
              (f" ... +{len(miss) - 14}" if len(miss) > 14 else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
