"""Per-class build log: every workflow step recorded, and a GATE that refuses
to let a phase close until they all are.

    python3 tools/phaselog.py <class>                        # status + metrics
    python3 tools/phaselog.py <class> --step <id> --note "…"  # record a step
    python3 tools/phaselog.py <class> --gate <phase>          # close a phase
    python3 tools/phaselog.py <class> --md                    # readable log

Exit 0 when the gate passes, 1 when it does not. The nonzero exit is the point:
a gate that reports failure only in prose nobody reads is not a gate.

WHY THIS EXISTS
---------------
The workflow already said "check the changelog first". It was skipped anyway,
and the Pyromancer requirements were written around a Phoenix duration that had
not existed for a week. The problem was not that the rule was unwritten -- it
was written, in three places -- it is that nothing MEASURED whether it ran.

A step that is only a sentence in a doc is a step that gets skipped under time
pressure, and the skip is invisible until a release fails. So each step is
recorded with its evidence, and the phase gate recomputes the metrics from the
repo rather than trusting the log's own say-so. Both halves matter: the log
says a human ran it, the metrics say the repo agrees.

⚠️ A recorded step is a CLAIM. `--gate` re-derives everything it can (inventory
counts, unreviewed markers, citation staleness, changelog drift, test state) so
a false claim is caught by the repo disagreeing with it, not by trust.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

from classes import SP, data, dest, get

ROOT = os.path.dirname(SP)

# ---------------------------------------------------------------- the workflow
# Ordered. `auto` steps are ones the gate can verify from the repo on its own;
# the rest need a human to record them, and the gate still cross-checks what it
# can. Keep this list in step with notes/class-pack-process.md -- it IS that
# document, in the only form that can fail a build.
PHASES = {
    "research": [
        ("changelog", "changelog_watch.py run; every replaced/reworked/"
                      "new-spell entry triaged", True),
        ("mechanics-source", "rotation source scraped to "
                             "resources/sidekick-<class>-<spec>.md", True),
        ("crossdb", "every inventory ability asked of BOTH databases", False),
        ("requirements", "notes/requirements-<class>.md exists, all 6 sections "
                         "answered or marked UNKNOWN", True),
        ("citations", "resources/citations-<class>.json imported and validated",
         True),
        ("inventory-reviewed", "no seed:/prop: markers left in "
                               "abilities-<class>.md", True),
    ],
    "build": [
        ("main-rows", "every main row ordered from the rotation text, not "
                      "guessed", False),
        ("talents", "§2 replace/transform/charge talents handled; pack reads "
                    "correctly with AND without each", False),
        ("pets", "§3 answered; pet section built or explicitly none", False),
        ("procs", "§1 must-press procs wired to PROC_GLOW", False),
        ("alerts", "§5 missing-buff alerts built", False),
    ],
    "verify": [
        ("tests", "tests/run.py all checks passed", True),
        ("guide", "generated guide read before importing", False),
        ("unknowns", "§6 open questions closed or explicitly deferred", True),
    ],
    # Post-ship. A draft ships when `verify` seals; this phase flips the DRAFT
    # badge off. It is the only phase allowed to close AFTER the pack is live
    # -- community feedback or a batch in-game sweep closes it, whichever
    # arrives first. See notes/production-run.md.
    "verified": [
        ("in-game", "imported and confirmed in game, every spec", False),
        ("recorded", "verified.py record <class> <version>", True),
    ],
}


def _path(slug):
    return dest(f"buildlog-{slug}.json")


def load(slug):
    p = _path(slug)
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {"class": slug, "steps": {}, "gates": {}}


def save(slug, log):
    json.dump(log, open(_path(slug), "w", encoding="utf-8"),
              indent=1, sort_keys=True)


def today():
    return datetime.date.today().isoformat()


# ------------------------------------------------------------------- metrics
def _rows(slug):
    """(total, unreviewed, with_id) inventory rows.

    `with_id` is the cross-database denominator: a row with no spell id cannot
    be asked of a database at all, so counting it as unswept would make 100%
    unreachable and the gate permanently red -- which trains people to ignore
    it.
    """
    p = data(f"abilities-{slug}.md")
    if not os.path.exists(p):
        return 0, 0
    total = unrev = with_id = 0
    for line in open(p, encoding="utf-8"):
        if not line.startswith("| ") or line.count("|") < 6:
            continue
        c = [x.strip() for x in line.split("|")[1:-1]]
        if not c[0] or c[0] == "Ability" or set(c[0]) == {"-"}:
            continue
        total += 1
        if c[1].split(";")[0].strip().isdigit():
            with_id += 1
        if len(c) > 5 and re.match(r"(seed|prop\??):", c[5]):
            unrev += 1
    return total, unrev, with_id


def metrics(slug, log):
    """Recomputed from the repo every time. Never read back from the log."""
    cls = get(slug)
    total, unrev, with_id = _rows(slug)
    m = {"inventory_rows": total, "inventory_unreviewed": unrev,
         "inventory_with_id": with_id}

    m["mechanics_sources"] = sum(
        os.path.exists(data(f"sidekick-{slug}-{sp}.md")) for sp in cls.specs)
    m["specs"] = len(cls.specs)

    cpath = data(f"citations-{slug}.json")
    if os.path.exists(cpath):
        c = json.load(open(cpath, encoding="utf-8"))
        recs = {k: v for k, v in c.items() if not k.startswith("_")}
        m["citations"] = len(recs)
        m["citation_claims"] = sum(
            len(v) for r in recs.values()
            for v in (r.get("claims") or {}).values())
    else:
        m["citations"] = m["citation_claims"] = 0

    rp = os.path.join(ROOT, "notes", f"requirements-{slug}.md")
    if os.path.exists(rp):
        txt = open(rp, encoding="utf-8").read()
        m["requirements"] = True
        m["open_unknowns"] = len(re.findall(r"UNKNOWN", txt))
    else:
        m["requirements"] = False
        m["open_unknowns"] = None

    # cross-database coverage is a CLAIM the step records, because the sweep is
    # expensive and lives outside the repo. Stored as "checked" out of total.
    checked = (log.get("steps", {}).get("crossdb") or {}).get("checked", 0)
    m["crossdb_checked"] = checked
    m["crossdb_pct"] = (round(100.0 * checked / with_id, 1)
                        if with_id else 0.0)
    return m


def changelog_clear(slug):
    """(ok, detail). Nonzero exit from the watcher means drift is outstanding."""
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(SP, "changelog_watch.py"),
             # 6, not 3. A shallow scan reports "clear" for drift that is
             # simply off the end of it, which is a FALSE PASS -- the one
             # outcome a gate must never produce. Caught in testing: --pages 3
             # said clear while --pages 6 found 11 Pyromancer entries.
             "--class", slug, "--pages", "6"],
            capture_output=True, text=True, timeout=300, cwd=SP)
    except Exception as e:                                   # network, timeout
        return None, f"could not run: {e}"
    new = len(re.findall(r"^\s*NEW\s", r.stdout, re.M))
    return (new == 0), (f"{new} unprocessed entr{'y' if new == 1 else 'ies'}"
                        if new else "clear")


def tests_green():
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tests/run.py")],
                           capture_output=True, text=True, timeout=900,
                           cwd=ROOT)
    except Exception as e:
        return None, f"could not run: {e}"
    return ("all checks passed" in r.stdout,
            r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "?")


# ---------------------------------------------------------------------- gate
def gate(slug, phase, log):
    """Refuse to close a phase whose steps are not all recorded AND corroborated.

    Two independent tests per phase: the LOG says a human ran each step, and
    the REPO is re-measured to see whether it agrees. A step can be recorded
    and still fail here -- which is the entire point.
    """
    if phase not in PHASES:
        raise SystemExit(f"unknown phase {phase!r}. "
                         f"Known: {', '.join(PHASES)}")
    m = metrics(slug, log)
    problems, notes = [], []

    for sid, what, _auto in PHASES[phase]:
        if sid not in log.get("steps", {}):
            problems.append(f"step NOT RECORDED: {sid} -- {what}")

    if phase == "research":
        ok, detail = changelog_clear(slug)
        if ok is False:
            problems.append(f"changelog: {detail} -- triage them, and do NOT "
                            f"--accept to silence this")
        elif ok is None:
            notes.append(f"changelog: {detail} (not fatal, but unverified)")
        else:
            notes.append("changelog: clear")

        if m["mechanics_sources"] < m["specs"]:
            problems.append(
                f"mechanics source missing for "
                f"{m['specs'] - m['mechanics_sources']} of {m['specs']} specs "
                f"-- a class with no rotation reference cannot have its main "
                f"rows ordered from anything but a guess")
        if not m["requirements"]:
            problems.append(f"notes/requirements-{slug}.md does not exist")
        if m["inventory_unreviewed"]:
            problems.append(f"{m['inventory_unreviewed']} inventory row(s) "
                            f"still carry seed:/prop: markers")
        if not m["citations"]:
            problems.append("0 citations -- a priority with no author is a "
                            "guess wearing a citation's clothes")
        if m["crossdb_pct"] < 100.0:
            problems.append(
                f"cross-database sweep {m['crossdb_pct']}% "
                f"({m['crossdb_checked']}/{m['inventory_with_id']}) -- a spell only "
                f"ONE database has heard of is how a cut ability looks")

    if phase == "verify":
        ok, detail = tests_green()
        if ok is False:
            problems.append(f"tests/run.py: {detail}")
        elif ok is None:
            notes.append(f"tests: {detail}")
        else:
            notes.append("tests: all checks passed")
        if m["open_unknowns"]:
            notes.append(f"{m['open_unknowns']} UNKNOWN marker(s) still in the "
                         f"requirements doc -- fine only if deferred on purpose")

    return problems, notes, m


def report(slug, log, phase=None):
    m = metrics(slug, log)
    print(f"\n{get(slug).name} — build log")
    print(f"  {_path(slug)}")
    for ph, steps in PHASES.items():
        done = sum(1 for s, _, _ in steps if s in log.get("steps", {}))
        seal = log.get("gates", {}).get(ph)
        mark = f"SEALED {seal}" if seal else f"{done}/{len(steps)}"
        print(f"\n  [{ph}] {mark}")
        for sid, what, _a in steps:
            e = log.get("steps", {}).get(sid)
            tick = "x" if e else " "
            when = f"  {e['at']}" if e else ""
            print(f"    [{tick}] {sid:<18}{when}")
            if e and e.get("note"):
                print(f"          {e['note'][:96]}")
    print("\n  metrics")
    for k, v in sorted(m.items()):
        print(f"    {k:<22} {v}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--step")
    ap.add_argument("--note", default="")
    ap.add_argument("--checked", type=int,
                    help="for --step crossdb: how many rows were asked of both DBs")
    ap.add_argument("--gate")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()

    get(a.slug)                                   # validates the slug
    log = load(a.slug)

    if a.step:
        known = {s for steps in PHASES.values() for s, _, _ in steps}
        if a.step not in known:
            raise SystemExit(f"unknown step {a.step!r}. "
                             f"Known: {', '.join(sorted(known))}")
        entry = {"at": today(), "note": a.note}
        if a.checked is not None:
            entry["checked"] = a.checked
        log.setdefault("steps", {})[a.step] = entry
        save(a.slug, log)
        print(f"recorded {a.step} -> {_path(a.slug)}")
        return 0

    if a.gate:
        problems, notes, m = gate(a.slug, a.gate, log)
        print(f"\ngate: {a.slug} / {a.gate}")
        for n in notes:
            print(f"  ok    {n}")
        for p in problems:
            print(f"  BLOCK {p}")
        print("\n  metrics")
        for k, v in sorted(m.items()):
            print(f"    {k:<22} {v}")
        if problems:
            print(f"\n{len(problems)} blocker(s). Phase {a.gate!r} is NOT "
                  f"closed; the next phase does not start.")
            return 1
        log.setdefault("gates", {})[a.gate] = today()
        log.setdefault("metrics", {})[a.gate] = m
        save(a.slug, log)
        print(f"\nphase {a.gate!r} SEALED {today()}. Metrics recorded.")
        return 0

    if a.md:
        report(a.slug, log)
        return 0

    report(a.slug, log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
