"""Top-performing characters per class/spec, and the builds behind them.

    python3 tools/rankings.py --template > resources/rankings-runemaster.json
    python3 tools/rankings.py runemaster            # summary
    python3 tools/rankings.py runemaster --validate # exit nonzero on faults

WHAT THIS IS FOR. Sidekick says what a class can do and states plainly that
optimal order is unsettled. The official talent builder says what a build can
reach. Neither says what the people actually clearing content chose. That last
one is the strongest evidence available for how a spec is really played, and it
is the gap this file fills.

The valuable half is the DISAGREEMENTS. A top parse whose talents match the
published builds corroborates them; a top parse with NO published build behind
it is the more interesting record, because it means either the build sites are
behind or that player found something nobody has written up. `build.status`
carries that distinction rather than dropping the entry.

HAND-ENTERED, ON PURPOSE. coa.ascensionlogs.gg publishes
`Content-Signal: use=reference` and returns "API access not allowed" to
programmatic reads, so this project links to it and does not crawl it (see
tools/sources.py). A person reading the rankings and transcribing rows is
exercising the reference right its operator granted; a crawler is not. Every
record therefore carries `collected_by` and `collected_at` -- provenance for a
human act, not a fetch.

If API access is granted later, an importer writes THIS SAME SHAPE and nothing
downstream changes. That is the point of writing the schema before the access.

EMPTY IS A VALID STATE, not a failure. Zul'Gurub released 2026-08-01 at 14:00,
so its rankings are empty until people clear it, and a category with no entries
and a dated note is a correct record of "nobody has done this yet". Treating
that as missing data would make the panel lie during exactly the window when
players most want to look at it.
"""
import argparse
import json
import os
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import sources  # noqa: E402
from classes import CLASSES, get, data, dest  # noqa: E402

# Ordered: the panel renders them in this order and defaults to the first.
CATEGORIES = [
    ("overall", "Overall"),
    ("world-boss", "World Bosses"),
    ("dungeon", "Dungeons"),
    ("raid", "Zul'Gurub"),
]
CATEGORY_KEYS = [k for k, _ in CATEGORIES]

# What we can say about the build behind a parse.
BUILD_STATUS = {
    "matches": "talents match a build we have a citation for",
    "differs": "talents readable, and they differ from every cited build",
    "unpublished": "talents readable, no published build covers them",
    "unknown": "no talents recorded for this character",
}


def path_for(cls):
    return f"rankings-{cls.slug}.json"


def load(cls):
    p = data(path_for(cls))
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def blank(cls):
    """A valid, empty record. Better than a missing file: it states that the
    class has been considered and nothing has been collected yet."""
    return {
        "class": cls.slug,
        "source": "coa.ascensionlogs.gg",
        "source_url": "https://coa.ascensionlogs.gg/rankings",
        "policy": sources.SOURCES["coa.ascensionlogs.gg"]["policy"],
        "collected_at": None,
        "collected_by": None,
        "categories": {
            k: {"label": lbl, "note": "", "entries": []}
            for k, lbl in CATEGORIES
        },
    }


def validate(cls, rec):
    """[problem] -- empty means the panel can render it."""
    bad = []
    if rec is None:
        return ["no rankings file; run --template to create one"]
    if rec.get("class") != cls.slug:
        bad.append(f"class is {rec.get('class')!r}, expected {cls.slug!r}")
    src = rec.get("source")
    if src and src not in sources.SOURCES:
        bad.append(f"source {src!r} is not declared in tools/sources.py")
    cats = rec.get("categories") or {}
    for k in CATEGORY_KEYS:
        if k not in cats:
            bad.append(f"missing category {k!r}")
    for k, cat in cats.items():
        if k not in CATEGORY_KEYS:
            bad.append(f"unknown category {k!r}")
            continue
        entries = cat.get("entries")
        if entries is None:
            bad.append(f"{k}: entries missing (use [] for 'nothing yet')")
            continue
        seen_ranks = set()
        for e in entries:
            who = e.get("character") or "?"
            if not e.get("character"):
                bad.append(f"{k}: an entry has no character name")
            if e.get("spec") and e["spec"] not in cls.specs:
                bad.append(f"{k}/{who}: unknown spec {e['spec']!r}")
            r = e.get("rank")
            if not isinstance(r, int) or r < 1:
                bad.append(f"{k}/{who}: rank must be a positive integer")
            elif r in seen_ranks:
                bad.append(f"{k}: rank {r} appears twice")
            else:
                seen_ranks.add(r)
            st = (e.get("build") or {}).get("status")
            if st not in BUILD_STATUS:
                bad.append(f"{k}/{who}: build.status must be one of "
                           f"{'/'.join(BUILD_STATUS)}")
            # A record with entries but no provenance is an unattributable
            # claim about real people, which is worse than no record.
            if entries and not rec.get("collected_at"):
                bad.append("entries present but collected_at is empty")
                break
    return bad


def summary(cls, rec):
    if rec is None:
        print(f"{cls.name}: no rankings file")
        return
    stamp = rec.get("collected_at") or "never"
    print(f"\n{cls.name} rankings  --  collected {stamp}"
          + (f" by {rec['collected_by']}" if rec.get("collected_by") else ""))
    total = 0
    for k, lbl in CATEGORIES:
        cat = (rec.get("categories") or {}).get(k) or {}
        entries = cat.get("entries") or []
        total += len(entries)
        note = f"  -- {cat['note']}" if cat.get("note") else ""
        print(f"  {lbl:<14} {len(entries)} entr{'y' if len(entries)==1 else 'ies'}{note}")
        for e in sorted(entries, key=lambda x: x.get("rank", 99)):
            st = (e.get("build") or {}).get("status", "unknown")
            flag = "" if st == "matches" else f"   [{st}]"
            print(f"      {e.get('rank'):>2}. {e.get('character','?'):<18} "
                  f"{e.get('spec','?'):<12}{flag}")
    if not total:
        print("  nothing collected yet. That is a valid state -- the panel "
              "says so rather than pretending the data is missing.")
        return
    unknown = sum(1 for k, _ in CATEGORIES
                  for e in ((rec["categories"].get(k) or {}).get("entries") or [])
                  if (e.get("build") or {}).get("status") != "matches")
    if unknown:
        print(f"\n  {unknown} of {total} top parses do NOT match a cited build "
              f"-- the interesting half: either the build sources are behind, "
              f"or those players found something nobody has written up.")


TEMPLATE_ENTRY = {
    "rank": 1,
    "character": "Charactername",
    "spec": "<one of this class's spec slugs>",
    "metric": "dps",
    "value": 0,
    "armory_url": "https://coa.ascensionlogs.gg/armory/character/<id>",
    "report_url": None,
    "build": {
        "status": "unknown",
        "talents_url": None,
        "note": "no talents recorded for this character",
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cls", nargs="?")
    ap.add_argument("--template", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--init", action="store_true",
                    help="write a blank valid record for the class")
    args = ap.parse_args()

    if args.template and not args.cls:
        rec = blank(next(iter(CLASSES.values())))
        rec["categories"]["overall"]["entries"] = [TEMPLATE_ENTRY]
        print(json.dumps(rec, indent=1, ensure_ascii=False))
        return 0
    if not args.cls:
        ap.error("give a class slug (or --template)")

    cls = get(args.cls)
    if args.init:
        p = dest(path_for(cls))
        if os.path.exists(p):
            print(f"{p} already exists; not overwriting")
            return 1
        with open(p, "w", encoding="utf-8") as f:
            json.dump(blank(cls), f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"wrote {p}")
        return 0

    rec = load(cls)
    bad = validate(cls, rec)
    if bad:
        print(f"{cls.name}: {len(bad)} problem(s)")
        for b in bad:
            print(f"  {b}")
    if args.validate:
        return 1 if bad else 0
    summary(cls, rec)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
