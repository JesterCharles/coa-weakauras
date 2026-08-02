"""Rebuild notes/raid-utility.md -- who brings which raid utility, all 21 classes.

    python3 tools/utility_tables.py > notes/raid-utility.md
    python3 tools/utility_tables.py --check      # counts only, writes nothing

CLASSIFIES BY SPELL EFFECT ID, NOT BY TOOLTIP TEXT, and that is the whole point
of the file. Ascension Sidekick's kit data does not contain Chronomancer's
`Fray Magic` at all, so any candidate list derived from its descriptions
silently omits a real 30 sec interrupt. Two attempts made exactly that mistake.
Effect ids come off Spell.dbc and cannot be phrased around.

    68   INTERRUPT_CAST
    18   RESURRECT           -- and 113 RESURRECT_NEW. BOTH are in use: matching
    113  RESURRECT_NEW          only 18 returns two spells and misses seventeen.
    126  STEAL_BENEFICIAL_BUFF
    38   DISPEL              -- misc_value is the DISPEL TYPE. 9 = Enrage, which
                                is the soothe/tranq category. Everything else
                                needs the tooltip to separate a purge (beneficial
                                effect off an ENEMY) from a cleanse, because the
                                target flag does NOT decide it -- `Show of Force`
                                is target_a 6 and reads "on a friendly target".

DATA. Reads the local mirror under `tools/spellchk/`, which is gitignored and
holds one raw API response per spell id plus one digest per class. Nothing is
fetched here: populate the mirror with `tools/exiles.py` (class digests) and a
per-id pass against `https://db.exil.es/api/v1/spells/{id}` first. See
`tools/sources.py` for that host's policy -- it welcomes inference-time agents
and asks that volume stay low, and a full mirror is ~11k requests, so keep it
warm rather than refetching.

NO REAGENT FIELD EXISTS. The API carries `power_cost`, `power_cost_percent` and
`power_type` and nothing else, so `Materials Required` is resource cost only and
`--` means "no cost", never "no reagent". Do not add a reagent column from
another source without saying where it came from.
"""
import collections
import glob
import json
import os
import re
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from classes import CLASSES, data  # noqa: E402
from exiles import digest, parse  # noqa: E402

CACHE = os.path.join(SP, "spellchk")
# -2 is POWER_HEALTH: Bloodmage pays life for several abilities. An
# unmapped id prints as `power-2`, which is how this was caught.
POWER = {-2: "health", 0: "mana", 1: "rage", 2: "focus", 3: "energy",
         6: "runic power"}
# Rows that are components, stubs or scaffolding rather than player buttons.
JUNK = re.compile(r"deprecated|unused|placeholder|test|delayer|trigger|"
                  r"dispel effect$|generic effe", re.I)

# A stun or silence whose tooltip ALSO interrupts non-player casting. In PvE
# that is functionally an interrupt, and effect 68 does not mark it -- which is
# the blind spot of classifying purely by effect id, exactly mirroring the
# blind spot of classifying purely by text.
NPC_INTERRUPT = re.compile(r"interrupt\w*\s+non-?player", re.I)
GROUP = re.compile(r"\b(party|raid|allies|group)\b", re.I)

ORDER = ["interrupt", "silence", "stun", "root", "rez", "purge", "spellsteal",
         "tranq", "raid_dr", "raid_dr_passive"]
TITLES = {
    "interrupt": "1. Interrupts",
    "silence": "2. Silences",
    "stun": "3. Stuns",
    "root": "4. Roots",
    "rez": "5. Battle Rezzes",
    "purge": "6. Purges",
    "spellsteal": "7. Spellsteals",
    "tranq": "8. Tranq Shots / Soothes (remove enrage)",
    "raid_dr": "9. Raid damage reduction — active",
    "raid_dr_passive": "9b. Raid damage reduction — passive auras",
}
EFFNOTE = {
    "interrupt": "`effect_id 68` -- INTERRUPT_CAST. Verified against Pyromancer "
                 "**Spellburn** and Runemaster **Ley Lock**.",
    "rez": "`effect_id 18` (RESURRECT) or `113` (RESURRECT_NEW). **Both are in "
           "use** -- Bloodmage **Vampyr Bite** is 18, Pyromancer **Phoenix "
           "Rebirth** is 113. Matching only 18 finds 2 spells and misses "
           "almost everything.",
    "purge": "`effect_id 38` (DISPEL) where the tooltip names a *beneficial* "
             "effect on an *enemy*. Target flags alone are unreliable -- "
             "**Show of Force** is `target_a 6` and reads \"on a friendly "
             "target\".",
    "silence": "`mechanic 9` (SILENCE). A silence stops the NEXT cast and "
               "locks casting for a duration. Several also state that they "
               "interrupt non-player spellcasting, which makes "
               "them the best interrupt substitute available -- those are "
               "marked **(int)**. Only rows with a cost or a cooldown are "
               "listed; a silence with neither is a component or a talent.",
    "stun": "`mechanic 12` (STUN). **A stun is not an interrupt.** Most raid "
            "bosses are stun-immune, so treat these as trash and add tools, "
            "not as a cast-stopping plan. Several carry an "
            "\"interrupts non-player spellcasting\" clause and are marked "
            "**(int)** -- that clause is worth exactly as much as the stun "
            "landing, which on a boss is usually nothing.",
    "root": "`mechanic 7` (ROOT) or `13` (FREEZE). Snares and slows "
            "(`mechanic 11`) are deliberately NOT here -- a slow is not a root, "
            "and folding them in would triple the table with abilities that do "
            "not hold anything in place.",
    "raid_dr": "`aura_id 87` (MOD_DAMAGE_PERCENT_TAKEN) or `229` "
               "(AoE damage taken), where the tooltip names the party, raid or "
               "allies AND the ability has a cooldown or a cost -- i.e. "
               "something you press.",
    "raid_dr_passive": "Same auras, group-scoped, but **no cooldown and no "
                       "cost**: talents and stances that shape the raid's "
                       "damage intake without being pressed. Separated because "
                       "a raid cooldown plan cares about the first list; roster "
                       "composition cares about this one.",
    "spellsteal": "`effect_id 126` -- STEAL_BENEFICIAL_BUFF.",
    "tranq": "`effect_id 38` with `misc_value 9` -- dispel type Enrage.",
}


FRONT = """---
title: CoA raid utility -- interrupts, battle rezzes, purges, spellsteals, soothes
date: 2026-08-02
type: reference
status: budding
tags: [wow, ascension, conquest-of-azeroth, reference, raid, utility, interrupts]
source: "db.exil.es /api/v1/spells/{id}, all 11,193 spell ids across the 21 class rosters"
---

# Raid utility, all 21 CoA classes

Who brings an interrupt, a battle rez, a purge, a spellsteal, and an enrage
removal. Ability names link to the spell page.

**REGENERATE, do not hand-edit.** `python3 tools/utility_tables.py > notes/raid-utility.md`
reads the cached spell mirror under `tools/spellchk/` and rebuilds this file
whole -- frontmatter, tables and notes. The server patches, and a
hand-maintained copy of 55 rows will rot; this repo has been bitten three times
in one week by a note that disagreed with the code. Refresh the mirror first if
the data looks stale (`tools/exiles.py` for the class digests, and the volume
note in `tools/sources.py`).
"""

TAIL = """
---

## How these were classified

**Primarily by SPELL EFFECT ID, with the tooltip as a second pass.** Neither
source is sufficient alone, and both failure modes were hit while building
this file.

*Text alone under-reports.* Ascension Sidekick's kit data does not contain
Chronomancer's `Fray Magic` at all, so every candidate list derived from its
descriptions silently omits a real 30 sec interrupt.

*Effect ids alone under-report too.* Several abilities interrupt non-player
casting through a stun or a silence and carry no `effect_id 68`. Classifying
purely on 68 reports Templar and Witch Doctor as having no cast-stopping tool
at all.

*And the ROSTER has two halves.* The class digest lists "Trainable / class
spells" and, separately, the Mind-of-Ascension trees. Reading only the first
dropped Necromancer's `Heartchill`, Bloodmage's `Aneurysm` and Stormbringer's
`Mystic Thunder` -- three real interrupts -- and reported two of those classes
as having none. `owners()` unions both.

| Table | Signal | Verified against |
|---|---|---|
| Interrupts | `effect_id 68` (INTERRUPT_CAST) | Pyromancer Spellburn, Runemaster Ley Lock |
| Battle rezzes | `effect_id 18` **or** `113` | Bloodmage Vampyr Bite (18), Pyromancer Phoenix Rebirth (113) |
| Purges | `effect_id 38` + tooltip says *beneficial* + *enemy* | Templar Righteous Reprimand |
| Spellsteals | `effect_id 126` (STEAL_BENEFICIAL_BUFF) | Felsworn Consume Magic |
| Soothes | `effect_id 38` with `misc_value 9` (dispel type Enrage) | Witch Hunter Purge Evil |

Two traps found while doing it:

* **Resurrects use TWO effect ids.** Matching only `18` returns 2 spells and
  misses seventeen. `113` (RESURRECT_NEW) is the common one.
* **Target flags do not decide friendly vs enemy.** `Show of Force` carries
  `target_a 6` and its tooltip reads "on a friendly target", so purges are
  identified from effect + tooltip together, never from the target flag alone.

## A stun is not an interrupt

The single most important thing on this page. **Most raid bosses are
stun-immune.** An ability that says it "interrupts non-player spellcasting"
does so only if its stun lands, so on a boss that clause is usually worth
nothing. Those abilities are marked **(int)** in the Stuns table and they are
NOT counted as interrupts anywhere.

A silence is different: it stops the next cast and locks casting for a
duration, which does not depend on a stun landing. Whether a given boss resists
silence is an in-game question this database cannot answer -- but a silence at
least fails for a reason you can see, where a stun on a stun-immune target
fails silently.

Ranked by what actually stops a boss cast:

1. **Interrupts** (table 1) -- the real thing, `mechanic 26` / `effect 68`
2. **Silences** (table 2), especially those marked **(int)**
3. **Stuns** (table 3) -- assume these do nothing on a boss until proven

Roots (table 4) are separate again and stop movement, not casting. Snares and
slows (`mechanic 11`) are excluded entirely: a slow is not a root.

## What this file does NOT know

* **No reagents.** The API exposes `power_cost`, `power_cost_percent` and
  `power_type` and nothing else. If an ability consumes an item, this database
  does not say so. `Materials Required` is resource cost only, and a dash means
  "no cost", never "no reagent".
* **Spec is `?` for 18 classes.** Only Runemaster, Chronomancer and Pyromancer
  have a reviewed `resources/abilities-<slug>.md`. The Mind-of-Ascension tree
  slugs look like spec names and are NOT: Felsworn's tree is filed `felblood`
  while its specs are slayer / infernal / tyrant, the same trap as
  `pyromancer-destruction` being the HEALING spec. Tree filing is deliberately
  not used as a fallback.
* **`Instant*`** means `cast_time_ms` came back negative -- a ranged-weapon
  marker, not a real cast time.

## Rows worth a second look

* **`Reap Magic`** (Reaper) reads "Steals 1 beneficial Magic Effect" but
  carries `effect_id 38` (dispel), not 126. Filed under Purges on the effect
  id. The data contradicts itself; only the game settles it.
* **`Subjugate`** (Witch Hunter) and **`Ghastly Screech`** (Reaper) describe
  silences rather than interrupts, but carry effect 68. Included on that basis.
* **`Reanimate`** (Necromancer) matches the resurrect effect but revives a
  corpse as a temporary pet, not a player. Listed so its absence is not
  mistaken for an oversight; it is not a battle rez.
"""


def owners():
    """spell id -> [(class name, ability name)], from the cached class digests.

    BOTH halves of the digest, and the second one is not optional. The
    "Trainable / class spells" list ALONE misses abilities that exist only as
    Mind-of-Ascension talents -- it dropped Necromancer's `Heartchill`,
    Bloodmage's `Aneurysm` and Stormbringer's `Mystic Thunder`, all three real
    interrupts, and reported those classes as having none. That is the same
    shape of bug as trusting Sidekick: an incomplete membership source reads as
    a confident empty answer.

    Tree membership is used for CLASS attribution only. The tree SLUG is not a
    spec name and is never read as one -- see inventory().
    """
    out = collections.defaultdict(list)
    for c in sorted(CLASSES.values(), key=lambda x: x.id):
        try:
            spells, trees = parse(digest(c.slug))
        except SystemExit:
            print(f"  no digest for {c.slug} -- run tools/exiles.py {c.slug}",
                  file=sys.stderr)
            continue
        for name, (sid, _r) in spells.items():
            out[str(sid)].append((c.name, name))
        for _slug, rows in trees.items():
            for _r, _col, name, sid in rows:
                if (c.name, name) not in out[str(sid)]:
                    out[str(sid)].append((c.name, name))
    return out


def inventory():
    """(slug, id) -> reviewed Specs cell, for the classes that have an inventory.

    The Mind-of-Ascension tree slugs are deliberately NOT used as a fallback.
    They look like spec names and are not: Felsworn's tree is filed `felblood`
    against specs slayer/infernal/tyrant, and `pyromancer-destruction` is the
    HEALING spec. A wrong spec here is worse than an honest `?`.
    """
    inv = {}
    for c in CLASSES.values():
        p = data(f"abilities-{c.slug}.md")
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            t = line.strip()
            if not t.startswith("|") or t.startswith("|---") or t.startswith("| Ability"):
                continue
            cells = [x.strip() for x in t.strip("|").split("|")]
            if len(cells) >= 6 and cells[1].split(";")[0].strip().isdigit():
                inv[(c.slug, int(cells[1].split(";")[0]))] = cells[2]
    return inv


def spells():
    out = {}
    for p in glob.glob(os.path.join(CACHE, "spell-*.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if d.get("name"):
            out[str(d["id"])] = d
    return out


def fmt_cd(ms):
    if not ms:
        return "none"
    s = ms / 1000
    return f"{s:g}s" if s < 60 else (f"{s/60:g} min" if s < 3600 else f"{s/3600:g} hr")


def fmt_cast(d):
    if d.get("channeled"):
        return f"Channel {(d.get('duration_ms') or 0)/1000:g}s"
    ct = d.get("cast_time_ms") or 0
    if ct < 0:
        # Negative is a ranged-weapon marker on this server, not a cast time.
        return "Instant\\*"
    return "Instant" if ct == 0 else f"{ct/1000:g}s"


def fmt_cost(d):
    bits = []
    pct = d.get("power_cost_percent") or 0
    flat = d.get("power_cost") or 0
    pt = POWER.get(d.get("power_type"), f"power{d.get('power_type')}")
    if pct:
        bits.append(f"{pct}% {pt}")
    elif flat:
        bits.append(f"{flat} {pt}")
    # CoA custom resources are AURAS, not power types, so "Consumes 1 Ember"
    # only ever appears in the tooltip prose.
    m = re.match(r"(Consumes?|Depletes?)\s+([A-Za-z0-9\s]{1,20}?)(?=[A-Z][a-z])",
                 d.get("description") or "")
    if m:
        bits.append(m.group(0).strip())
    return " · ".join(dict.fromkeys(bits)) or "—"


def desc(d, n=140):
    t = " ".join((d.get("description") or "").split()).replace("|", "/")
    return (t[:n] + "…") if len(t) > n else t


def _eff(d):
    return [e for e in d.get("effects") or [] if e.get("effect_id")]


def classify(d):
    """One of the five buckets, or None. Effect id first, tooltip only to
    disambiguate what the effect id genuinely cannot."""
    t = d.get("description") or ""
    if not t.strip() or JUNK.search(d["name"]):
        return None
    has = lambda i: any(e["effect_id"] == i for e in _eff(d))  # noqa: E731
    mech = {e.get("mechanic") for e in _eff(d)}
    # ORDER MATTERS, and the specific signals go FIRST. A crowd-control
    # mechanic rides on plenty of abilities whose POINT is something else --
    # Necromancer's `Reanimate` raises a corpse and carries mechanic 12 on the
    # mind-control, and a mechanic-first order files a resurrect under Stuns.
    if has(68) and re.search(r"interrupt|silenc|counter", t, re.I):
        return "interrupt"
    if has(126) and re.search(r"steal", t, re.I):
        return "spellsteal"
    if (has(18) or has(113)) and re.search(r"\blife\b|resurrect|revive|rebirth", t, re.I):
        return "rez"
    if any(e["effect_id"] == 38 and e.get("misc_value") == 9 for e in _eff(d)):
        return "tranq"
    # CC mechanics ride on far more rows than the rare effects above -- talent
    # modifiers, applied-debuff components, broken stubs ("silencing for -0.001
    # sec"). Requiring a cost OR a cooldown keeps the ones that are a BUTTON.
    # The rarer categories do not need this and are not subjected to it: an
    # interrupt or a battle rez with neither is still worth listing.
    pressable = bool(d.get("cooldown_ms") or d.get("power_cost_percent")
                     or d.get("power_cost"))
    if pressable:
        # A row can carry several CC mechanics; take the most specific first so
        # a rooting silence is not filed by whichever id happened to sort low.
        if 9 in mech:
            return "silence"
        if 12 in mech:
            return "stun"
        if mech & {7, 13}:
            return "root"
    if has(38) and re.search(r"beneficial|purg", t, re.I) and re.search(r"enem", t, re.I):
        return "purge"
    if any(e.get("aura_id") in (87, 229) for e in _eff(d)) and GROUP.search(t) \
            and re.search(r"damage taken|damage dealt to", t, re.I):
        return "raid_dr" if (d.get("cooldown_ms") or d.get("power_cost_percent")
                             or d.get("power_cost")) else "raid_dr_passive"
    return None


def main(argv):
    own, inv, cache = owners(), inventory(), spells()
    buckets = collections.defaultdict(list)
    for sid, d in cache.items():
        if sid not in own:
            continue
        cat = classify(d)
        if cat:
            buckets[cat].append((sid, d))

    if "--check" in argv:
        print(f"{len(cache)} spells in the mirror, {len(own)} owned by a class")
        for cat in ORDER:
            print(f"  {cat:11} {len(buckets.get(cat, []))}")
        return 0

    print(FRONT)
    for cat in ORDER:
        print(f"\n## {TITLES[cat]}\n\n{EFFNOTE[cat]}\n")
        rows = []
        for sid, d in buckets.get(cat, []):
            for cname, _a in own[sid]:
                c = next(x for x in CLASSES.values() if x.name == cname)
                mark = " **(int)**" if NPC_INTERRUPT.search(d.get("description") or "") else ""
                rows.append((c.id, cname, inv.get((c.slug, int(sid)), "?"),
                             f"[{d['name']}](https://db.exil.es/spell/{sid}){mark}",
                             fmt_cd(d.get("cooldown_ms")), fmt_cost(d),
                             fmt_cast(d), desc(d), d["name"]))
        seen, out = set(), []
        for r in sorted(rows):
            if (r[1], r[8]) in seen:
                continue
            seen.add((r[1], r[8]))
            out.append(r)
        if not out:
            print("_None found._\n")
            continue
        print("| Class | Spec | Ability | CD | Materials Required | Cast Time | Description |")
        print("|---|---|---|---|---|---|---|")
        for _i, cn, sp, nm, cd, co, ca, ds, _raw in out:
            print(f"| {cn} | {sp} | {nm} | {cd} | {co} | {ca} | {ds} |")
        miss = sorted({c.name for c in CLASSES.values()} - {r[1] for r in out})
        print(f"\n**{len(out)} across {len({r[1] for r in out})} classes.**")
        print(f"None found for: {', '.join(miss)}." if miss else "Every class has one.")
    print(TAIL)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
