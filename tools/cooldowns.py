"""Build `cooldown-abilities-<class>.json` from the db.exil.es JSON API.

    python3 tools/cooldowns.py pyromancer
    python3 tools/cooldowns.py pyromancer --add "Firewall" "Kiss of Al'ar"
    python3 tools/cooldowns.py pyromancer --drop "Deprecated"

WHAT THIS REPLACES, and the evidence for replacing it. `audit_cds.py` gets the
same facts by rendering each spell's HTML page through Firecrawl and reading
the `Cooldown` and `GCD` rows. That works and it costs a running Firecrawl at
localhost:3002 plus the three ~700-line Sidekick page dumps, neither of which a
new class has on day one.

`spell-meta-<class>.json` already carries `cd_ms` and `gcd_ms`, from the same
site's JSON API, for every id in `exiles-<class>.json`. Cross-checked against
the hand-verified Chronomancer audit: **54 of 54 rows agree on GCD, 54 of 54 on
the cooldown string.** Zero disagreements. So the Firecrawl render was buying
nothing the API does not already answer.

THE GCD HALF IS THE LOAD-BEARING HALF -- see notes/off-gcd-detection.md.
WeakAuras applies `use_showgcd` blindly, so an off-GCD ability sweeps every
time you press something else unless the builder is told. `gcd: false` here is
what `OFF_GCD` in the engine is derived from. The API reports `gcd_ms` null or
0 for off-GCD spells, which is the same signal as db.exil.es omitting the GCD
row, and the 54/54 agreement is the proof.

    "absence of evidence vs evidence of absence" still applies. audit_cds.py
    guarded against a failed render by requiring a `Spell ID` row before
    recording `false`. The equivalent guard here is that a spell absent from
    spell-meta gets NO ROW AT ALL rather than a row saying off-GCD -- a fetch
    that did not land cannot be mistaken for an ability off the global.

MEMBERSHIP. A row is written for a name that (a) is in the class skillbook,
`coa-<class>-skills.json`, and (b) has a cooldown in spell-meta. Names with a
cooldown that the skillbook does not list are printed as CANDIDATES and not
written: on Chronomancer that set is 18 names of which 6 are real abilities
(Chronobeam, Chronurgy, Disc of Legend, Fray Magic, Reflection, Unearth) and 12
are deprecated rows, summons and immunity dummies. That ratio is why they are a
review step and not an inference -- promote one with `--add`.

Decisions persist: any name already in the output file is KEPT on a re-run, so
`--add` is a one-time edit rather than a flag to remember forever. `--drop`
removes one and records nothing, so a re-run does not resurrect it -- put a
dropped name back with `--add` if that was wrong.

SPECS ARE LEFT EMPTY, and that is deliberate. audit_cds.py filled this column
by substring-matching ability names against the Sidekick spec pages, which
scored 42 right / 27 too broad / 11 WRONG against the hand-reviewed
Chronomancer rows -- and a wrong narrow HIDES an ability from a spec. Empty
means "shared by every spec" to every reader of this file. Real per-spec
membership belongs in the reviewed Specs column of `abilities-<class>.md`,
which mkabilities.py seeds from the skillbook's own per-spec ability lists (a
structured source, not a text match).
"""
import argparse
import json
import os
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from classes import get, data, dest  # noqa: E402


def fmt_cd(ms):
    """Match audit_cds.py's rendered string exactly: '30 sec cooldown',
    '1.5 min cooldown'. Only `cd_secs()` ever parses it, and it wants a
    leading number and one of sec/min/hour."""
    s = ms / 1000.0
    if s < 60:
        v, u = s, "sec"
    elif s < 3600:
        v, u = s / 60, "min"
    else:
        v, u = s / 3600, "hour"
    v = int(v) if abs(v - int(v)) < 1e-9 else round(v, 1)
    return f"{v} {u} cooldown"


def fmt_gcd(ms):
    """False when the spell is off the global, else the length as db.exil.es
    renders it -- one decimal place, always ('1.0 sec', not '1 sec')."""
    return f"{ms / 1000.0:.1f} sec" if ms else False


def build(cls):
    """(rows, candidates). rows is the writable set; candidates are names with
    a cooldown that the skillbook does not list."""
    for f in (cls.exiles, f"spell-meta-{cls.slug}.json", cls.skills):
        if not os.path.exists(data(f)):
            raise SystemExit(
                f"missing {f} -- run tools/exiles.py and tools/spellmeta.py "
                f"first, see notes/class-pack-process.md section 2")
    exiles = json.load(open(data(cls.exiles)))
    meta = json.load(open(data(f"spell-meta-{cls.slug}.json")))
    book = {r["name"] for r in json.load(open(data(cls.skills)))}

    rows, candidates = {}, []
    for name, row in sorted(exiles.items()):
        sid = row["ids"][0]
        m = meta.get(str(sid))
        # No metadata at all means the fetch never landed for this id. Skip it
        # -- writing gcd:false here would be inventing evidence of absence.
        if not m or not m.get("cd_ms"):
            continue
        entry = {"id": sid, "cd": fmt_cd(m["cd_ms"]),
                 "specs": [], "gcd": fmt_gcd(m.get("gcd_ms"))}
        if name in book:
            rows[name] = entry
        else:
            candidates.append((name, entry, m.get("rank")))
    return rows, candidates


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cls")
    ap.add_argument("--add", nargs="*", default=[], metavar="NAME",
                    help="promote a candidate into the file")
    ap.add_argument("--drop", nargs="*", default=[], metavar="NAME",
                    help="remove a name and do not resurrect it")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    cls = get(args.cls)
    rows, candidates = build(cls)
    by_name = {n: e for n, e, _ in candidates}

    out_path = dest(cls.cooldowns)
    old = json.load(open(data(cls.cooldowns))) if os.path.exists(
        data(cls.cooldowns)) else {}

    # Previously-promoted names survive a re-run without re-passing --add.
    for name in old:
        if name not in rows and name in by_name:
            rows[name] = by_name[name]
    for name in args.add:
        if name in by_name:
            rows[name] = by_name[name]
        elif name in rows:
            print(f"  --add {name!r}: already present")
        else:
            raise SystemExit(
                f"--add {name!r}: not a candidate. It must appear in "
                f"{cls.exiles} with a cooldown in spell-meta. Candidates: "
                f"{', '.join(sorted(by_name)) or '(none)'}")
    for name in args.drop:
        rows.pop(name, None)

    # Carry the reviewed Specs column forward if a previous run had one -- this
    # tool never fills it, but audit_cds.py did, and Runemaster's builder still
    # reads it.
    for name, e in rows.items():
        if not e["specs"] and (old.get(name) or {}).get("specs"):
            e["specs"] = old[name]["specs"]

    rows = dict(sorted(rows.items()))
    off = sum(1 for v in rows.values() if v["gcd"] is False)
    print(f"{cls.name}: {len(rows)} abilities with a cooldown "
          f"({len(old)} before), {off} off the global "
          f"({off * 100 // max(1, len(rows))}%)")

    if candidates:
        pend = [(n, e, r) for n, e, r in candidates if n not in rows]
        if pend:
            print(f"\n  {len(pend)} CANDIDATES -- have a cooldown, not in the "
                  f"skillbook. Promote a real one with --add:")
            for n, e, rank in pend:
                print(f"    {n[:42]:42} {e['id']:>8}  {e['cd']:<18}"
                      f"{'off-GCD' if e['gcd'] is False else e['gcd']:<9}"
                      f"{rank or ''}")

    gone = sorted(set(old) - set(rows))
    if gone:
        print(f"\n  DROPPED ({len(gone)}): {', '.join(gone)}")

    if args.dry_run:
        print("\ndry run -- nothing written")
        return 0
    json.dump(rows, open(out_path, "w"), indent=1)
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
