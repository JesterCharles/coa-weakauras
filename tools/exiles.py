"""Build `exiles-<class>.json` -- the name -> spell id map -- for any class.

    python3 tools/exiles.py pyromancer
    python3 tools/exiles.py pyromancer --refresh    # re-download the digest
    python3 tools/exiles.py pyromancer --trees      # also print the MoA trees

WHY THIS EXISTS. Every other data file in the chain had a generator and this
one did not. `exiles-runemaster.json` and `exiles-chronomancer.json` were
produced by hand, which made them the one input a new class could not simply
run for -- and they sit at the BOTTOM of the chain:

    exiles-<class>.json   <- here
      -> spell-meta-<class>.json   (spellmeta.py reads its ids)
      -> cooldown-abilities-*.json (audit_cds.py reads its names)
      -> abilities-<class>.md      (mkabilities.py resolves ids through it)

WHERE THE DATA COMES FROM, and why not the obvious route. db.exil.es has a
name search, and `/search` is `Disallow`ed for general crawlers in its
robots.txt -- so building a name lookup on it is the wrong answer even though
it would work. The right one is published: the operator ships per-class digests
explicitly FOR agents at `/class/{slug}/llms.txt`, which returns the entire
class -- every trainable spell with its id, plus every Mind-of-Ascension tree
-- in ONE ~40KB request. See tools/sources.py for the policy read.

That endpoint is also more complete than the HTML class page is convenient:
Pyromancer's digest carries 480 spells against the 216 its Sidekick skillbook
lists, which is the surplus mkabilities.py expects and files under
`## Candidates` rather than into the table.

WHAT IS AND IS NOT WRITTEN. The schema is `{name: {"ids": [id], "icon": null}}`
and it does NOT change here, because four other tools read it. Two notes on
that shape:

  * `ids` is a list carrying one entry. It has never held more -- both existing
    files are 1:1 -- but the readers all iterate it, so it stays a list.
  * `icon` is left null. Art comes from `icon-meta-<class>.json`
    (fetch_spell_icons.py, db.ascension.gg), which is keyed by id and is the
    better source. An existing file's icons are PRESERVED on re-run, so
    refreshing Chronomancer cannot silently drop the 120 it already has.

MIND OF ASCENSION TREES ARE A HINT, NOT SPEC MEMBERSHIP. The digest files each
talent under a spec tree and it is tempting to read that as "which spec has
this". Do not write it into the Specs column. It is the same trap as
db.exil.es's `line` field, which agrees with the hand-reviewed Chronomancer
rows 34 times and contradicts them 33; and as Sidekick mention counts, which
score 42 right / 27 too broad / 11 wrong. `--trees` prints it for a human
reviewer and nothing consumes it.
"""
import argparse
import json
import os
import re
import subprocess
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import sources  # noqa: E402
from classes import get, data, dest  # noqa: E402

URL = "https://db.exil.es/class/{slug}/llms.txt"
# Shared with audit_cds.py and fetch_spell_icons.py, and gitignored: this is a
# cache, not the asset. The distilled JSON in resources/ is what is tracked.
CACHE_DIR = os.path.join(SP, "spellchk")

# - [Al Dente](https://db.exil.es/spell/300921) (2 ranks)
_SPELL = re.compile(r"^- \[(?P<name>.+?)\]\("
                    r"https://db\.exil\.es/spell/(?P<id>\d+)\)"
                    r"(?:\s*\((?P<ranks>\d+) ranks?\))?\s*$")
# ### Pyromancer â Flameweaving (slug: `pyromancer-destruction`)
_TREE = re.compile(r"^### .*?\(slug: `(?P<slug>[^`]+)`\)\s*$")
# - (row 0, col 1) Ember Touch — [spell](https://db.exil.es/spell/800818)
_TALENT = re.compile(r"^- \(row (?P<row>\d+), col (?P<col>\d+)\) "
                     r"(?P<name>.+?) [-—–]+ \[spell\]\("
                     r"https://db\.exil\.es/spell/(?P<id>\d+)\)\s*$")


def digest(slug, refresh=False):
    """The class digest text, from cache unless asked to refresh."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"class-{slug}.txt")
    if refresh or not os.path.exists(path):
        url = URL.format(slug=slug)
        sources.require(url)        # policy gate -- see tools/sources.py
        out = subprocess.run(["curl", "-s", "-m", "40", url],
                             capture_output=True, text=True).stdout
        if not out.startswith("#"):
            raise SystemExit(
                f"exiles: {url} did not return a digest "
                f"(got {len(out)} bytes starting {out[:60]!r}). "
                f"Check the slug against `python3 tools/classes.py`.")
        open(path, "w", encoding="utf-8").write(out)
        print(f"  downloaded {len(out):,} bytes -> {path}")
    return open(path, encoding="utf-8").read()


def parse(text):
    """(spells, trees). spells is name -> (id, ranks); trees is slug -> rows."""
    spells, trees = {}, {}
    section, tree = None, None
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            tree = None
            continue
        m = _TREE.match(line)
        if m:
            tree = m.group("slug")
            trees.setdefault(tree, [])
            continue
        if section and section.startswith("Trainable"):
            m = _SPELL.match(line)
            if m:
                # First wins. A duplicate name is the same ability at another
                # rank. WHICH id that leaves is not guaranteed to be the
                # castable one -- db.exil.es links whichever rank it likes,
                # and re-deriving Chronomancer reproduced 453 of 457 ids but
                # disagreed on 4 (Rewind, Aeon of Oblivion, Fray Magic, Chaos
                # Incarnate Transform), every one of which already has a
                # correction in that builder's CROSSCHECK / in-game registry.
                # That is the designed path: this file proposes, spell-meta
                # and the tooltip registry dispose.
                spells.setdefault(m.group("name"),
                                  (int(m.group("id")),
                                   int(m.group("ranks") or 1)))
            continue
        if tree:
            m = _TALENT.match(line)
            if m:
                trees[tree].append((int(m.group("row")), int(m.group("col")),
                                    m.group("name"), int(m.group("id"))))
    return spells, trees


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cls")
    ap.add_argument("--refresh", action="store_true",
                    help="re-download the digest before parsing")
    ap.add_argument("--trees", action="store_true",
                    help="print the Mind of Ascension trees (a HINT only -- "
                         "never write tree membership into Specs)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    cls = get(args.cls)
    spells, trees = parse(digest(cls.slug, args.refresh))
    if not spells:
        raise SystemExit(f"exiles: no spells parsed for {cls.name}. The "
                         f"digest format may have changed -- check "
                         f"{os.path.join(CACHE_DIR, f'class-{cls.slug}.txt')}")

    # Never lose hand- or scrape-enriched art on a refresh.
    out_path = dest(cls.exiles)
    old = {}
    if os.path.exists(data(cls.exiles)):
        old = json.load(open(data(cls.exiles)))
    rows = {name: {"ids": [sid],
                   "icon": (old.get(name) or {}).get("icon")}
            for name, (sid, _) in sorted(spells.items())}

    added = sorted(set(rows) - set(old))
    gone = sorted(set(old) - set(rows))
    kept_icons = sum(1 for v in rows.values() if v["icon"])
    print(f"{cls.name}: {len(rows)} spells "
          f"({len(old)} before, +{len(added)} -{len(gone)}), "
          f"{kept_icons} icons carried over")
    ranked = sum(1 for _, r in spells.values() if r > 1)
    print(f"  {ranked} names have multiple ranks -- spell-meta decides which "
          f"of those can be gated on")
    if gone:
        # Loud: a name vanishing means the class changed upstream or the
        # digest shape did, and both want a human before the file moves.
        print(f"  DROPPED ({len(gone)}): {', '.join(gone[:12])}"
              f"{' ...' if len(gone) > 12 else ''}")
    if added and old:
        print(f"  new ({len(added)}): {', '.join(added[:12])}"
              f"{' ...' if len(added) > 12 else ''}")

    if args.trees:
        print(f"\n  Mind of Ascension trees -- A HINT, NOT SPEC MEMBERSHIP.")
        print(f"  db.exil.es FILES a talent under a tree; that is not the same "
              f"as which spec can\n  cast it. Read it, do not import it.")
        for slug, rowsl in sorted(trees.items()):
            print(f"\n  {slug}  ({len(rowsl)} talents)")
            for r, c, name, sid in rowsl:
                print(f"    r{r} c{c:<2} {name[:44]:44} {sid}")

    if args.dry_run:
        print("\ndry run -- nothing written")
        return 0
    json.dump(rows, open(out_path, "w"), indent=1)
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
