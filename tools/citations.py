"""Rotation citations: who says an ability matters, when they said it, and
whether anyone else agrees.

    python3 tools/citations.py runemaster              # corroboration report
    python3 tools/citations.py runemaster --import-sidekick
    python3 tools/citations.py runemaster --validate
    python3 tools/citations.py --template > /tmp/c.json   # hand-entry skeleton

WHY A SCHEMA AND NOT A COLUMN. Press order decides what the main row shows and
what order the cooldown rows sit in, which is most of what a player looks at.
Getting it from one source is how you inherit that source's uncertainty
silently -- and the source we have says so out loud, on every Runemaster spec:

    "Refine: Point allocation & optimal order aren't settled yet — confirm in
     the official Vol'jin builder and adjust on live."

So a priority is not a fact, it is a CLAIM with an author and a date, and the
useful question is how many independent authors agree. Three sources naming
Runic Brand first is worth more than one naming it first, and the disagreements
are worth more than either -- they are where the real question is.

WHAT A CITATION IS. One source's statement about one class+spec at one moment:

    source        the host, which must appear in tools/sources.py
    policy        copied from that host's entry at import time, so a record
                  carries the terms it was collected under
    origin        scheduled | manual | community
    retrieved_at  when. Staleness is measured against the changelog, and a
                  class the devs patched after this date has stale priorities
    content_sha256  of the extracted claim text, so a re-scrape that changed
                  nothing is visibly a no-op
    claims        maintain / priority / cooldowns / signature, each a list of
                  ABILITY NAMES that must exist in abilities-<class>.md

ORIGIN=MANUAL IS FIRST-CLASS, not a fallback. A source that publishes
`use=reference` may not be fetched, but a human reading it and transcribing
five rows is a person exercising the reference right the operator granted.
Those records carry the same provenance fields as an automated one and are
worth the same in corroboration -- the difference is `origin`, not standing.

NAMES ARE VALIDATED against the inventory. A citation naming an ability that
has no row is not a strong claim about a weak ability, it is a typo or a rename,
and it would otherwise sit in the corpus corroborating nothing forever.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import sources  # noqa: E402
from classes import get, data, dest  # noqa: E402

BUCKETS = ("maintain", "priority", "cooldowns", "signature")
ORIGINS = ("scheduled", "manual", "community")


def path_for(cls):
    return f"citations-{cls.slug}.json"


def load(cls):
    p = data(path_for(cls))
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(cls, obj):
    p = dest(path_for(cls))
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, p)
    return p


def inventory_names(cls):
    """Ability names with a row, so a citation cannot name something absent."""
    p = data(f"abilities-{cls.slug}.md")
    out = set()
    if not os.path.exists(p):
        return out
    for line in open(p, encoding="utf-8"):
        if line.startswith("| ") and line.count("|") >= 6:
            n = line.split("|")[1].strip()
            if n and n != "Ability" and set(n) != {"-"}:
                out.add(n)
    return out


def newest_changelog(cls):
    """Newest changelog date recorded for this class, or None.

    Read from the watcher's accepted state rather than the network: staleness
    is a property of what we have already seen, and making this function fetch
    would put a network call inside a validation pass.
    """
    p = data("changelog-seen.json")
    if not os.path.exists(p):
        return None
    try:
        st = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    dates = [e.get("date") for e in (st.get("entries") or {}).values()
             if e.get("class") == cls.slug and e.get("date")]
    return max(dates) if dates else None


def _norm_date(s):
    """'2026/07/31' and '2026-07-31T12:00:00Z' compare as the same shape."""
    m = re.match(r"(\d{4})[-/](\d{2})[-/](\d{2})", s or "")
    return "-".join(m.groups()) if m else ""


def validate(cls, cites, names):
    """[(citation_id, problem)] -- empty means the corpus is usable."""
    bad = []
    for cid, c in sorted(cites.items()):
        for field in ("class", "spec", "source", "origin", "retrieved_at",
                      "claims"):
            if not c.get(field):
                bad.append((cid, f"missing `{field}`"))
        if c.get("class") and c["class"] != cls.slug:
            bad.append((cid, f"class is {c['class']}, expected {cls.slug}"))
        if c.get("spec") and c["spec"] not in cls.specs:
            bad.append((cid, f"unknown spec {c['spec']!r}"))
        if c.get("origin") and c["origin"] not in ORIGINS:
            bad.append((cid, f"origin must be one of {'/'.join(ORIGINS)}"))
        if c.get("source") and c["source"] not in sources.SOURCES:
            bad.append((cid, f"source {c['source']!r} is not in sources.py"))
        for b, vals in (c.get("claims") or {}).items():
            if b not in BUCKETS:
                bad.append((cid, f"unknown claim bucket {b!r}"))
                continue
            for n in (vals if isinstance(vals, list) else [vals]):
                if n and n not in names:
                    bad.append((cid, f"{b}: {n!r} has no inventory row"))
    return bad


def sidekick_import(cls, cites):
    """Turn the committed Sidekick bundle into one citation per spec.

    Reads the SNAPSHOT, not the network. The bundle is already committed under
    the terms recorded in sources.py, and re-fetching inside an import would
    make provenance depend on when you happened to run it.
    """
    raw_path = data("sidekick-data.js")
    if not os.path.exists(raw_path):
        raise SystemExit("citations: resources/sidekick-data.js missing -- run "
                         "`python3 tools/sidekick_skills.py --all` first")
    raw = open(raw_path, encoding="utf-8").read()
    asc = json.loads(raw[raw.index("=") + 1:].strip().rstrip(";"))
    skill = asc.get("coaSkill", {}).get(cls.name) or {}
    stamp = _norm_date(__import__("time").strftime("%Y-%m-%d"))

    added = 0
    for spec_name, block in skill.items():
        spec = re.sub(r"[^a-z0-9]+", "-", spec_name.lower()).strip("-")
        if spec not in cls.specs:
            continue
        rot = block.get("rotation") or {}
        maintain = [x for x in (rot.get("maintain") or []) if isinstance(x, str)]
        cds, caveats = [], []
        for e in (rot.get("priority") or []):
            if not isinstance(e, dict):
                continue
            k, v = (e.get("k") or ""), (e.get("v") or "")
            if k.lower().startswith("cooldown"):
                # "Line up A, B, C with your burst window."
                m = re.search(r"line up (.+?) with", v, re.I)
                if m:
                    cds += [s.strip() for s in re.split(r",| and ", m.group(1))
                            if s.strip()]
            if k.lower().startswith("refine"):
                caveats.append(v)
        core = rot.get("core") or []
        sig = None
        for c in core:
            m = re.search(r"Signature \(([^)]+)\)", str(c))
            if m:
                sig = m.group(1)
                break

        claims = {"maintain": maintain, "cooldowns": cds, "priority": []}
        if sig:
            claims["signature"] = [sig]
        body = json.dumps(claims, sort_keys=True, ensure_ascii=False)
        cid = f"sidekick-{cls.slug}-{spec}-{stamp}"
        cites[cid] = {
            "class": cls.slug,
            "spec": spec,
            "source": "ascensionsidekick.com",
            "source_url": f"https://ascensionsidekick.com/{cls.slug}/{spec}",
            "policy": sources.SOURCES["ascensionsidekick.com"]["policy"],
            "origin": "scheduled",
            "retrieved_at": stamp,
            "content_sha256": hashlib.sha256(body.encode()).hexdigest()[:16],
            "claims": claims,
            "caveats": caveats,
        }
        added += 1
    return added


def report(cls, cites, names):
    """Corroboration per spec: who is named, by how many, and where they clash."""
    stale_after = newest_changelog(cls)
    by_spec = defaultdict(list)
    for cid, c in cites.items():
        by_spec[c.get("spec")].append((cid, c))

    for spec in cls.specs:
        rows = by_spec.get(spec) or []
        print(f"\n{cls.name} / {spec}  --  {len(rows)} citation(s)")
        if not rows:
            print("    none. Priorities here are UNCITED: whatever the builder "
                  "renders is somebody's guess, including ours.")
            continue

        stale = [cid for cid, c in rows
                 if stale_after and _norm_date(c.get("retrieved_at")) <
                 _norm_date(stale_after)]
        counts = defaultdict(lambda: defaultdict(list))
        for cid, c in rows:
            for b, vals in (c.get("claims") or {}).items():
                for n in (vals if isinstance(vals, list) else [vals]):
                    if n:
                        counts[b][n].append(c.get("source", "?"))

        for b in BUCKETS:
            if not counts.get(b):
                continue
            print(f"  {b}:")
            for n, srcs in sorted(counts[b].items(),
                                  key=lambda kv: (-len(kv[1]), kv[0])):
                mark = "" if len(srcs) > 1 else "   (single source)"
                print(f"    {len(srcs)}x  {n}{mark}")
        if stale:
            print(f"  STALE: {len(stale)} citation(s) predate the newest "
                  f"{cls.name} changelog entry ({stale_after}). Re-research "
                  f"before trusting a priority.")
        cav = [v for _, c in rows for v in (c.get("caveats") or [])]
        for v in dict.fromkeys(cav):
            print(f"  CAVEAT: {v[:150]}")

    singles = sum(1 for spec in cls.specs
                  for cid, c in (by_spec.get(spec) or [])
                  for b, vals in (c.get("claims") or {}).items()
                  for n in (vals if isinstance(vals, list) else [vals]) if n)
    srcs = {c.get("source") for _, c in
            [x for spec in cls.specs for x in (by_spec.get(spec) or [])]}
    print(f"\n{len(cites)} citation(s), {singles} claim(s), "
          f"{len(srcs)} distinct source(s): {', '.join(sorted(s for s in srcs if s))}")
    if len(srcs) < 2:
        print("  ONE SOURCE. Corroboration is not measurable until a second "
              "one exists -- every count above is just that source repeating "
              "itself.")


TEMPLATE = {
    "<source>-<class>-<spec>-<YYYY-MM-DD>": {
        "class": "runemaster",
        "spec": "glyphic",
        "source": "coa.ascensionlogs.gg",
        "source_url": "https://coa.ascensionlogs.gg/rankings",
        "policy": "reference",
        "origin": "manual",
        "transcribed_by": "your name",
        "retrieved_at": "2026-08-01",
        "claims": {
            "priority": ["Elemental Burst"],
            "maintain": [],
            "cooldowns": [],
        },
        "caveats": ["read by hand from the rankings page; this source "
                    "publishes use=reference and is not fetched"],
    }
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cls", nargs="?")
    ap.add_argument("--import-sidekick", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--template", action="store_true")
    args = ap.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, indent=1, ensure_ascii=False))
        return 0
    if not args.cls:
        ap.error("give a class slug (or --template)")

    cls = get(args.cls)
    cites = load(cls)
    names = inventory_names(cls)

    if args.import_sidekick:
        n = sidekick_import(cls, cites)
        p = save(cls, cites)
        print(f"imported {n} Sidekick citation(s) -> {p}")

    bad = validate(cls, cites, names)
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for cid, why in bad:
            print(f"  {cid}: {why}")
    if args.validate:
        return 1 if bad else 0

    report(cls, cites, names)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
