"""Which built versions have actually been seen working in game.

    python3 tools/verified.py                          # status for every class
    python3 tools/verified.py runemaster               # one class
    python3 tools/verified.py record runemaster 1.1 \
        --by jestercharles --spec glyphic --spec engravement --spec riftblade \
        --note "utility row wraps at 9, no overlap with long-term"

WHY THIS FILE EXISTS. Publishing was a side effect of regenerating the site:
mksite.py copies tools/packs/ into docs/packs/, and docs/ is what GitHub Pages
serves. So a rebuild-and-commit shipped whatever had just been built, and
nothing anywhere recorded whether a human had ever looked at it in game.

That is how Chronomancer 1.1 went live carrying six displays nobody had tested.
It was harmless -- additive icons, no audience yet -- but nothing could have
caught it, and "nothing could have caught it" is the part worth fixing.

resources/in-game-verified.json is NOT this. It holds tooltip ground truth
keyed by spell NAME -- what an ability's id and cooldown really are. It says
nothing about whether a built PACK was ever loaded. The only trace that
Runemaster 1.0 was verified is the sentence in its commit message, which no
tool can read.

WHAT COUNTS AS VERIFIED. A person imported that exact version and looked at
each spec in game. Per-spec, because the whole point of the layout is that each
spec loads its own displays, and a pack can be right on one spec and wrong on
another -- the ungated Core reminders shipped in final8 looked fine on the spec
that could satisfy them.

THE GATE IS NOT A WALL. Publishing an unverified pack stays possible, because
that is where the alpha channel is heading anyway. It just cannot be SILENT:
mksite refuses without --allow-unverified, and with it the pack block carries a
visible "not verified in game" badge. The failure mode being designed out is
shipping untested work while the page implies otherwise.
"""
import argparse
import json
import os
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from classes import CLASSES, get, data, dest  # noqa: E402

FILE = "verified-builds.json"


def load():
    p = data(FILE)
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return {k: v for k, v in d.items() if not k.startswith("_")}


def save(rec):
    out = {
        "_comment": (
            "Built pack versions confirmed working IN GAME, per spec. Written "
            "by tools/verified.py; read by mksite.py before it publishes. This "
            "is NOT in-game-verified.json, which holds tooltip ground truth "
            "keyed by spell name and says nothing about a built pack."),
    }
    out.update(dict(sorted(rec.items())))
    p = dest(FILE)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, p)
    return p


def status(cls, version, rec=None):
    """(verified, detail). `verified` is True only for an exact version match.

    Exact, not "greater than or equal": 1.2 being verified says nothing about
    1.3, and a version bump exists precisely because the output changed.
    """
    rec = load() if rec is None else rec
    entry = (rec.get(cls.slug) or {}).get(version)
    if not entry:
        seen = sorted((rec.get(cls.slug) or {}))
        return False, (f"v{version} not recorded"
                       + (f" (recorded: {', '.join(seen)})" if seen else
                          " (nothing recorded for this class)"))
    missing = [s for s in cls.specs if s not in (entry.get("specs") or [])]
    if missing:
        return False, (f"v{version} recorded but not on every spec -- "
                       f"missing {', '.join(missing)}")
    return True, (f"v{version} verified {entry.get('verified_at','?')}"
                  + (f" by {entry['verified_by']}"
                     if entry.get("verified_by") else ""))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("record", help="record a version as verified in game")
    r.add_argument("cls")
    r.add_argument("version")
    r.add_argument("--spec", action="append", default=[],
                   help="repeat per spec actually looked at")
    r.add_argument("--by", default="")
    r.add_argument("--at", default="", help="YYYY-MM-DD (default: today)")
    r.add_argument("--note", default="")
    # Named `only`, not `cls`: a subparser argument of the same name would be
    # overwritten by this one parsing to None, which silently broke `record`.
    ap.add_argument("only", nargs="?", help="limit the status report to one class")
    args = ap.parse_args()

    if args.cmd == "record":
        cls = get(args.cls)
        bad = [s for s in args.spec if s not in cls.specs]
        if bad:
            raise SystemExit(f"unknown spec(s) for {cls.name}: "
                             f"{', '.join(bad)}. Known: {', '.join(cls.specs)}")
        rec = load()
        entry = rec.setdefault(cls.slug, {}).setdefault(args.version, {})
        entry["specs"] = sorted(set(entry.get("specs", [])) | set(args.spec))
        entry["verified_at"] = args.at or __import__("time").strftime("%Y-%m-%d")
        if args.by:
            entry["verified_by"] = args.by
        if args.note:
            entry.setdefault("notes", []).append(args.note)
        p = save(rec)
        ok, detail = status(cls, args.version, rec)
        print(f"recorded -> {p}\n  {cls.name}: {detail}")
        if not ok:
            print("  still incomplete: record every spec before this counts "
                  "as verified.")
        return 0

    import re
    rec = load()
    targets = [get(args.only)] if args.only else sorted(
        CLASSES.values(), key=lambda c: c.id)
    worst = 0
    for cls in targets:
        b = os.path.join(SP, cls.builder)
        if not os.path.exists(b):
            continue
        m = re.search(r'^VERSION = "([^"]+)"', open(b).read(), re.M)
        v = m.group(1) if m else "?"
        ok, detail = status(cls, v, rec)
        print(f"  {'OK  ' if ok else 'NOT '} {cls.name:<16} {detail}")
        worst = max(worst, 0 if ok else 1)
    return worst


if __name__ == "__main__":
    sys.exit(main())
