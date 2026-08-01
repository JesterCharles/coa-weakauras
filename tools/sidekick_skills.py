"""Generate `coa-<class>-skills.json` -- the membership source -- from Sidekick.

    python3 tools/sidekick_skills.py runemaster        # one class
    python3 tools/sidekick_skills.py --all             # all 21
    python3 tools/sidekick_skills.py runemaster --refresh   # re-download data.js

WHY THIS EXISTS. `coa-<class>-skills.json` decides MEMBERSHIP: mkabilities.py
seeds the inventory from it, so an ability missing here is an ability the
inventory never creates a row for, which means no tool can report it absent.
It is the bottom of the stack, and it had no generator at all -- the two files
on disk were hand-produced and nothing could refresh or verify them.

That failed silently and badly. `coa-runemaster-skills.json` carried 150
entries and was missing Runeblade, Runic Explosion, Hoarfrost, Tempo,
Primordial Strength, Power Overwhelming and Frost Prison -- main-rotation
abilities, every one rendered by the shipped pack and every one changed in the
2026-07-31 patch. Coverage measured against that inventory reported 100% while
Runeblade was not in it.

WHERE THE DATA IS. ascensionsidekick.com is a client-rendered app: the HTML is
a 4KB shell, which is why the first scrape went through Firecrawl and why it
was lossy. The whole site's content is one static bundle at /data.js -- 3.8MB
of `window.ASC = {...}` -- and `coaKits[<Class>]` inside it holds:

    specs[]     one entry per spec, each with abilities[] {n, lvl, t, s, d, ic}
    shared[]    abilities available to the whole class
    petLines[]  pet spellbooks (Chronomancer's two Protectors)

No rendering, no Firecrawl, no Docker. It yields 258 Runemaster abilities
against the old file's 150, and 234 Chronomancer against 181.

SPECS COME FROM THE SOURCE HERE, and that is a different claim from the one
mkabilities.py refuses to make. That module rejects inferring specs from
Sidekick MENTION COUNTS, which scored 42 right / 27 too broad / 11 wrong
against hand review. This is not mention counting: `coaKits` lists each spec's
abilities explicitly, so the attribution is Sidekick's own statement. Treat it
as a strong proposal that still loses to a hand edit and to an in-game tooltip
-- Sidekick can be stale or wrong, it just is not GUESSING.

`t` is the talent flag and `d` often opens "Level 20 Passive ...", which is
where `meta` comes from. The old file's richer "Ability Lvl 10 · max L58" is
not in the bundle; that loss is covered, because spell-meta-<class>.json now
carries level, rank and cost from db.exil.es and is the better source for all
three.
"""
import argparse
import json
import os
import re
import sys
import urllib.request

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from classes import CLASSES, get, dest, data  # noqa: E402

URL = "https://ascensionsidekick.com/data.js"
CACHE = "sidekick-data.js"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

_PASSIVE = re.compile(r"\bPassive\b")
_LEVEL = re.compile(r"^Level (\d+)\b")


def bundle(refresh=False):
    """The parsed window.ASC object, from a committed snapshot by default.

    Cached rather than fetched per run: it is one 3.8MB download that serves
    all 21 classes, and committing it follows the same rule as every other
    scrape here -- a third-party page that can change or vanish is the least
    reproducible asset, not the most.
    """
    path = data(CACHE)
    if refresh or not os.path.exists(path):
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8", "replace")
        with open(dest(CACHE), "w", encoding="utf-8") as f:
            f.write(raw)
        path = dest(CACHE)
        print(f"  downloaded {len(raw):,} bytes -> {path}")
    raw = open(path, encoding="utf-8").read()
    return json.loads(raw[raw.index("=") + 1:].strip().rstrip(";"))


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _meta(a):
    """Reconstruct the `meta` string mkabilities.py reads.

    Only two things in it ever decided anything: Talent-or-Ability, and
    Passive. Both survive; the level text does not, and spell-meta carries it
    better anyway.
    """
    kind = "Talent" if a.get("t") else "Ability"
    desc = a.get("d") or ""
    if _PASSIVE.search(desc[:40]):
        kind += " Passive"
    m = _LEVEL.match(desc)
    if m:
        kind += f" Lvl {m.group(1)}"
    return kind


def extract(asc, cls):
    """[{name, icon, meta, specs, desc}] for one class, specs from the source."""
    kits = asc.get("coaKits", {})
    kit = kits.get(cls.name)
    if kit is None:                       # tolerate a renamed display name
        want = _slug(cls.name)
        kit = next((v for k, v in kits.items() if _slug(k) == want), None)
    if kit is None:
        raise SystemExit(
            f"sidekick_skills: no coaKits entry for {cls.name!r}. "
            f"Known: {', '.join(sorted(kits))}")

    found = {}
    for sp in kit.get("specs") or []:
        spec = _slug(sp.get("n", ""))
        for a in sp.get("abilities") or []:
            e = found.setdefault(a["n"], {"specs": set(), "a": a})
            e["specs"].add(spec)
            if not e["a"].get("d") and a.get("d"):
                e["a"] = a
    for a in kit.get("shared") or []:
        if isinstance(a, dict) and a.get("n"):
            found.setdefault(a["n"], {"specs": set(), "a": a})["specs"].add("all")

    known = set(cls.specs)
    out = []
    for name, e in sorted(found.items()):
        specs = e["specs"]
        # Present on every spec is the same statement as `all`, and the
        # inventory's Specs column already spells `all` that way.
        if "all" in specs or known and known <= (specs - {"all"}):
            slist = ["all"]
        else:
            slist = sorted(s for s in specs if s in known)
        a = e["a"]
        out.append({
            "name": name,
            "icon": a.get("ic") or "",
            "meta": _meta(a),
            "specs": slist or ["all"],
            "desc": (a.get("d") or "")[:400],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cls", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--refresh", action="store_true",
                    help="re-download data.js before extracting")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.cls and not args.all:
        ap.error("give a class slug or --all")

    asc = bundle(args.refresh)
    targets = (sorted(CLASSES.values(), key=lambda c: c.id) if args.all
               else [get(args.cls)])

    for cls in targets:
        try:
            rows = extract(asc, cls)
        except SystemExit as e:
            print(f"{cls.name}: {e}")
            continue
        path = data(cls.skills)
        before = set()
        if os.path.exists(path):
            try:
                before = {s["name"] for s in json.load(open(path, encoding="utf-8"))}
            except Exception:
                pass
        # UNION, never replace. The bundle and the original hand-scrape are
        # complementary: the bundle adds 116 Runemaster names the scrape
        # missed, and the scrape holds 8 the bundle does not list -- including
        # Runefeed and Power of Air, both real abilities. Overwriting would
        # trade one silent hole for a smaller silent hole, which is the same
        # bug. Membership only ever grows here; removing a name is a human
        # decision made in the inventory, where it can carry a reason.
        now = {r["name"] for r in rows}
        kept = []
        if os.path.exists(path):
            try:
                for s in json.load(open(path, encoding="utf-8")):
                    if s.get("name") and s["name"] not in now:
                        s.setdefault("specs", ["all"])
                        s["source"] = "prior scrape (not in the Sidekick bundle)"
                        kept.append(s)
            except Exception:
                pass
        rows = sorted(rows + kept, key=lambda r: r["name"])
        added, gone = sorted(now - before), sorted(before - now)

        print(f"\n{cls.name}: {len(rows)} abilities "
              f"({len(before)} before, +{len(added)} -{len(gone)})")
        if added:
            print(f"  ADDED   {', '.join(added[:12])}"
                  + (f" ... +{len(added)-12} more" if len(added) > 12 else ""))
        if gone:
            # Not a removal -- these are KEPT from the prior scrape and tagged.
            # Reported because a name the bundle stopped listing is either an
            # upstream rename (so there is now a duplicate under two names) or
            # a real removal, and only a human can tell which.
            print(f"  KEPT from the prior scrape, absent from the bundle: "
                  f"{', '.join(gone[:12])}"
                  + (f" ... +{len(gone)-12} more" if len(gone) > 12 else ""))
            print("          (check each for an upstream RENAME -- a rename "
                  "leaves the same ability listed twice)")
        if args.dry_run:
            continue
        with open(dest(cls.skills), "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"  wrote {dest(cls.skills)}")

    if args.dry_run:
        print("\ndry run -- nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
