"""Pull per-spell metadata from db.exil.es's JSON API, for any class.

    python3 tools/spellmeta.py chronomancer

Writes `resources/spell-meta-<class>.json`:

    {"501820": {"name": "Gravity Bomb", "rank": "Rank 2", "cd_ms": 90000,
                "gcd_ms": 1500, "cost_pct": 36, "level": 14,
                "duration_ms": 5000, "channeled": false}}

WHY. `load.use_spellknown` holds ONE spell id and `IsSpellKnown` is exact, so
gating an ability on the wrong id fails SILENTLY -- the display simply never
appears, with no error and nothing in the build output. That is retro bug #6
and it cost Runemaster four iterations; on Chronomancer it hid five abilities
(Gravity Bomb, Unearth, Temporal Focus, Time Out!, Fortify Timeline).

`rank` is the detector. db.exil.es's class listing links whichever row it likes,
and three kinds of row are NOT the castable ability:

    "Rank N"       one rank of a ranked spell. IsSpellKnown is true only for
                   the exact rank the character has, so a level-14 rank id
                   fails on a level-60 character who has rank 4.
    "DR" / "Damage" / "Player Aura" / "Wand Spell"
                   a component of the ability -- its aura, its damage effect,
                   its diminishing-returns entry. Never castable, never known.
    cost 0 + gcd 0 an effect rather than a button.

`is_castable()` below encodes that, and the builder refuses to own-id-gate
anything it rejects.

This replaces Firecrawl scraping for these questions: the API answers "is it an
aura, on whom, for how long, on the GCD?" directly, in one request per id, with
no browser. `audit_cds.py` still owns the GCD/cooldown audit because it also
resolves spec membership from the Sidekick pages.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from classes import data, dest, get

API = "https://db.exil.es/api/v1/spells"

# rank_text values that mean "this row is not the castable ability"
NOT_CASTABLE_RANKS = {"DR", "Damage", "Player Aura", "Wand Spell", "Heal",
                      "Trigger", "Proc", "Aura", "Effect"}


def is_castable(meta):
    """Can `load.use_spellknown` be trusted with this id?

    Conservative on purpose: a false 'no' costs one duplicated display, while
    a false 'yes' hides the ability outright and does it silently.
    """
    if not meta:
        return False
    rank = (meta.get("rank") or "").strip()
    if rank.startswith("Rank "):
        return False                     # IsSpellKnown is exact per rank
    if rank in NOT_CASTABLE_RANKS:
        return False
    if not meta.get("gcd_ms") and not meta.get("cost_pct"):
        return False                     # no cost and off the GCD -> an effect
    return True


def fetch(sid):
    out = subprocess.run(["curl", "-s", "-m", "20", f"{API}/{sid}"],
                         capture_output=True, text=True).stdout
    try:
        d = json.loads(out)
    except Exception:
        return sid, None
    if not d.get("name"):
        return sid, None
    line = d.get("skill_line") or {}
    return sid, {
        "name": d.get("name"),
        "rank": d.get("rank_text"),
        "cd_ms": d.get("cooldown_ms"),
        "gcd_ms": d.get("gcd_ms"),
        "cost_pct": d.get("power_cost_percent"),
        "level": d.get("level_required"),
        "duration_ms": d.get("duration_ms"),
        "channeled": d.get("channeled"),
        # The tooltip. The one field that says what an ability DOES, which is
        # what deciding its Role actually needs -- everything else here is
        # shape, not purpose. Newlines flattened so it survives a table cell.
        "desc": " ".join((d.get("description") or "").split()),
        # The spell TREE db.exil.es files this under ("Time", "Infinite",
        # "Artificer", "Pet - Bronze Protector"). It looks like spec
        # membership and IS NOT: checked against the 80 hand-reviewed
        # Chronomancer rows it agrees 34 times and contradicts 33 --
        # Accelerated Recovery is filed under Time and every spec casts it.
        # Filing, not access. Kept as a hint; never write it into Specs.
        # `audit_cds.py` stays the only trustworthy source for that, because
        # it reads the Sidekick pages, which are per spec.
        "line": line.get("name") or "",
    }


def main(argv):
    cls = get(argv[0] if argv else "runemaster")
    exiles = json.load(open(data(cls.exiles)))
    want = sorted({str(i) for v in exiles.values() for i in v["ids"]}, key=int)

    out_path = dest(f"spell-meta-{cls.slug}.json")
    known = json.load(open(out_path)) if os.path.exists(out_path) else {}
    # Refetch anything cached before a field was added, rather than needing a
    # --refresh nobody remembers to pass. A stale cache that silently answers
    # with the old shape is the same silent no-op that keeps biting here.
    todo = [s for s in want if s not in known or "desc" not in known[s]]
    print(f"{cls.name}: {len(want)} ids, {len(todo)} to fetch")

    for i in range(0, len(todo), 32):
        batch = todo[i:i + 32]
        with ThreadPoolExecutor(max_workers=8) as pool:
            for sid, meta in pool.map(fetch, batch):
                if meta:
                    known[sid] = meta
        print(f"  {min(i + 32, len(todo))}/{len(todo)}")

    json.dump(dict(sorted(known.items(), key=lambda kv: int(kv[0]))),
              open(out_path, "w"), indent=1)

    bad = [(s, m) for s, m in known.items() if not is_castable(m)]
    print(f"\nwrote {out_path}\n  {len(known)} spells")
    print(f"  {len(bad)} are NOT safe to gate on ({len(known) - len(bad)} are)")
    for s, m in sorted(bad, key=lambda kv: kv[1]["name"])[:15]:
        print(f"    {s:>7} {m['name'][:26]:26} rank={m.get('rank')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
