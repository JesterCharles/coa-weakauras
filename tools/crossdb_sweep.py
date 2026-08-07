"""Ask db.ascension.gg about EVERY ability in a class inventory.

    python3 tools/crossdb_sweep.py <class>
    python3 tools/crossdb_sweep.py <class> --report   # re-read, no network

`crosscheck.py` does this for the raid-utility page. This does it for a class,
which is what Phase 0 §0 requires and what `phaselog.py --gate research`
measures.

WHY BOTH DATABASES. db.exil.es and db.ascension.gg are two snapshots of the
same TrinityCore tables and they disagree, and the disagreement is the signal:
a spell only ONE of them has ever heard of is the shape a cut, renamed or
never-implemented ability takes. Pyromancer's `Stoke` is the worked example --
db.exil.es has a castable 803952, db.ascension.gg has no record, and Sidekick
lists the Flameweaving version as a passive TALENT. It was holding a main-row
slot on the healing spec.

THE ENDPOINT. `?spell=<id>&power` answers for every id, including ones whose
HTML page 404s. A 43-byte `registerSpell(id, 0, {})` is the absence.

⚠️ THE ID IS NOT THE JOIN KEY. Asking only by id overstates absence by about a
third -- the same ability carries different ids on the two databases. Every
empty id must be re-asked BY NAME before it is called dead, and a name hit is a
CANDIDATE, not a match: three of five name hits on the utility pass were
different abilities wearing the same word. Read both tooltips and write the
verdict into the row's Notes cell.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from classes import data, dest, get

TIMEOUT = 25


def rows(slug):
    """{ability: id} from the reviewed inventory, skipping rows with no id."""
    out = {}
    p = data(f"abilities-{slug}.md")
    for line in open(p, encoding="utf-8"):
        if not line.startswith("| ") or line.count("|") < 6:
            continue
        c = [x.strip() for x in line.split("|")[1:-1]]
        if not c[0] or c[0] == "Ability" or set(c[0]) == {"-"}:
            continue
        sid = c[1].split(";")[0].strip()
        if sid.isdigit():
            out[c[0]] = int(sid)
    return out


def ask(sid):
    try:
        out = subprocess.run(
            ["curl", "-s", "--max-time", str(TIMEOUT),
             f"https://db.ascension.gg/?spell={sid}&power"],
            capture_output=True, text=True).stdout
    except Exception:
        return "error"
    m = re.search(r"registerSpell\(\s*%d\s*,\s*\d+\s*,\s*(\{.*?\})\s*\)" % sid,
                  out, re.S)
    if not m:
        return "no-response"
    return "record" if len(m.group(1)) > 5 else "no-record"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    get(a.slug)
    out_path = dest(f"crossdb-{a.slug}.json")

    if a.report:
        if not os.path.exists(out_path):
            raise SystemExit(f"no sweep on disk: {out_path}")
        res = json.load(open(out_path, encoding="utf-8"))
    else:
        inv = rows(a.slug)
        print(f"asking db.ascension.gg about {len(inv)} abilities…")
        with ThreadPoolExecutor(max_workers=8) as p:
            verdicts = list(p.map(ask, inv.values()))
        res = {"_comment": "db.ascension.gg ?spell=<id>&power over the whole "
                           "class inventory. `no-record` means ONE database has "
                           "the ability -- re-ask BY NAME before calling it "
                           "dead, and read both tooltips before calling a name "
                           "hit a match.",
               "_class": a.slug,
               "verdicts": {n: {"id": i, "state": v}
                            for (n, i), v in zip(inv.items(), verdicts)}}
        json.dump(res, open(out_path, "w", encoding="utf-8"),
                  indent=1, sort_keys=True)
        print(f"wrote {out_path}")

    v = res["verdicts"]
    import collections
    counts = collections.Counter(x["state"] for x in v.values())
    print()
    for state in ("no-record", "no-response", "error"):
        named = sorted(n for n, x in v.items() if x["state"] == state)
        if named:
            print(f"  {state.upper()} ({len(named)}):")
            for n in named:
                print(f"    {n:<34} {v[n]['id']}")
    print(f"\n  {dict(counts)}")
    print(f"  checked {len(v)} of {len(v)} inventory rows with an id")
    return 0


if __name__ == "__main__":
    sys.exit(main())
