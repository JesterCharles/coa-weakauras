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

Each table is followed by a collapsed **"Copy this table as markdown"** block
holding the same rows as raw source, for lifting into a spreadsheet, a Discord
post or a wiki without reselecting the rendered table by hand.

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

## Reading the Spec column

The spell page states one of three things, and they are NOT the same:

| Page says | Column | Means |
|---|---|---|
| `Runemaster` | `all` | Baseline. Every spec has it, no talent point. |
| `Barbarian · Barbarian (row 1, col 5)` | `all (tree)` | A talent in the **class** tree. Any spec can take it, but it **costs a point**. |
| `Stormbringer · Stormbringer — Maelstrom (row 5, col 8)` | `Maelstrom` | A talent in that **spec's** tree. |

So `all` and `all (tree)` differ in whether the raid can assume it is present:
baseline is always there, a class-tree talent is a build choice.

Where a class has a reviewed `resources/abilities-<slug>.md`, its Specs column
wins over the tree -- that is why Runemaster and Chronomancer rows read
`glyphic,engravement,riftblade` and `artificer,infinite,time` instead of `all`.

**The tree LABEL is authoritative; the tree SLUG is not.** `stormbringer-gifts`
is the Maelstrom tree, `felsworn-felblood` is Infernal, and
`pyromancer-destruction` is FLAMEWEAVING -- the healing spec. Reading slugs as
spec names is wrong on at least three classes, so the parser reads the label.

## ⚠ probably not in the game

An ability marked ⚠ has **no icon on db.ascension.gg**, and a CoA ability with
no art is very likely unimplemented, cut, or a leftover database row. 26 of the
126 abilities here are marked, including `Wrist Snap`, `Halt`, `Solar Burn`,
`Throatpunch` and `Distracto Shot` -- five of the twenty-four interrupts.

This is a STRONG HINT, not a verdict: only logging in settles it. The list
lives in `resources/icon-missing.json`; confirm one in game and delete its id
(recording it under `confirmed_present`), then regenerate.

It matters most for the interrupt table. If those five are not real, five
classes lose their only listed interrupt.

## The "Usable on Boss" column

**Blank means untested, not "no".** Nothing in db.exil.es records immunity, so
this column cannot be derived and is never guessed -- a raid plans around it,
and a guess there is worse than a gap.

Fill it in `resources/boss-usable.json`, NOT in this file:

```json
"spells": {
  "800995": {"boss": "yes",     "note": "Ley Lock -- lands on every ZG boss"},
  "991349": {"boss": "no",      "note": "Monolith Smash -- stun immune"},
  "806599": {"boss": "partial", "note": "Stormhammer -- lands on Jin'do, not Hakkar"}
}
```

Then re-run the generator. The column is rebuilt from that file every time, so
a value typed into this markdown is destroyed on the next run and a value in
the JSON survives. That is the whole reason it is a separate file: this page is
regenerated wholesale, and hand-tested knowledge is the one thing here that
cannot be regenerated.

`yes` / `no` / `partial`; omit the id entirely while it is untested.

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

**Not covered at all:** incapacitates, fears, horrors, polymorphs, banishes and
knockbacks. They carry CC mechanics and would land in these tables on a
mechanic-only match, but none of them is an interrupt, a stun or a root --
`Breath of Time` incapacitates, `Holy Water Tonic` banishes, `Abyssal
Enslavement` polymorphs. If a raid needs those, they want their own table.

**A mechanic id alone does not classify an ability, and the tooltip has to
agree.** `mechanic` is tagged per EFFECT, and it rides on effects that do
something else entirely. Barbarian's `Deathmatch` carries `mechanic 9` on its
ARMOUR aura -- it is a 6 sec 1v1 banish that zeroes both players' armour and
silences nobody -- and a mechanic-only match filed it under Silences. The same
both-signals rule was already applied to interrupts and purges; the CC tables
were the ones missing it, and it cost 1 silence, 7 stuns and 3 roots that were
never any of those things.

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


def boss_usable():
    """spell id -> "yes" / "no" / "partial", from resources/boss-usable.json.

    HAND-TESTED, and deliberately the only source. db.exil.es carries no
    immunity data at all, so whether a stun lands on a boss cannot be derived
    from anything in the mirror -- and a guess in this column is worse than a
    blank, because a raid plans around it. An id with no entry renders empty.

    It lives in a data file rather than in the markdown because this page is
    regenerated wholesale; a value typed into the table would be destroyed by
    the next run, which is exactly the trap the "do not hand-edit" banner
    warns about.
    """
    p = data("boss-usable.json")
    if not os.path.exists(p):
        return {}
    raw = json.load(open(p, encoding="utf-8")).get("spells") or {}
    return {str(k): (v.get("boss") or "").strip() for k, v in raw.items()}


def no_icon():
    """Spell ids with no art on db.ascension.gg -- probably not in the game.

    A CoA ability with no icon is very likely unimplemented, cut, or a
    leftover database row. That is a judgement the user raised about `Wrist
    Snap` and it generalises: 26 of the 126 abilities in these tables have no
    art at all.

    Tracked in resources/icon-missing.json rather than recomputed here, so the
    page regenerates without a scrape and a confirmed-in-game id can be removed
    by hand and stay removed.
    """
    p = data("icon-missing.json")
    if not os.path.exists(p):
        return set()
    return set(json.load(open(p, encoding="utf-8")).get("ids") or {})


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
            out[str(sid)].append((c.name, name, None))
        for _slug, t in trees.items():
            for _r, _col, name, sid in t["rows"]:
                # THREE distinct states, and the spell page spells them out:
                #   "Runemaster"                        -> baseline, no point
                #   "Barbarian . Barbarian (row 1..)"   -> CLASS tree talent
                #   "Stormbringer . Stormbringer - Maelstrom (row 5..)"
                #                                       -> SPEC tree talent
                # The tree LABEL carries the spec; the slug does not and is
                # wrong on three classes. A root-tree talent is available to
                # every spec but still COSTS A POINT, so it is not the same as
                # baseline and must not render as plain `all`.
                out[str(sid)].append((c.name, name, t["spec"] or "all (tree)"))
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
    # THE MECHANIC ALONE IS NOT ENOUGH, and the tooltip has to agree.
    # `mechanic` is tagged per EFFECT, and it rides on effects that do
    # something else entirely: Barbarian's `Deathmatch` carries mechanic 9 on
    # its ARMOUR aura -- it is a 6 sec 1v1 banish that zeroes both players'
    # armour and silences nobody -- and mechanic-alone filed it under Silences.
    # Same rule already applied to interrupts and purges; the CC tables were
    # the ones missing it.
    if pressable:
        # A row can carry several CC mechanics; take the most specific first so
        # a rooting silence is not filed by whichever id happened to sort low.
        if 9 in mech and re.search(r"silenc", t, re.I):
            return "silence"
        if 12 in mech and re.search(r"\bstun\w*", t, re.I):
            return "stun"
        if mech & {7, 13} and re.search(r"\broot\w*|freez\w*|entangl\w*|"
                                        r"\bhold\w* .{0,12}in place|immobili",
                                        t, re.I):
            return "root"
    if has(38) and re.search(r"beneficial|purg", t, re.I) and re.search(r"enem", t, re.I):
        return "purge"
    if any(e.get("aura_id") in (87, 229) for e in _eff(d)) and GROUP.search(t) \
            and re.search(r"damage taken|damage dealt to", t, re.I):
        return "raid_dr" if (d.get("cooldown_ms") or d.get("power_cost_percent")
                             or d.get("power_cost")) else "raid_dr_passive"
    return None


def main(argv):
    own, inv, cache, boss = owners(), inventory(), spells(), boss_usable()
    noart = no_icon()
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
            for cname, _a, tree_spec in own[sid]:
                c = next(x for x in CLASSES.values() if x.name == cname)
                mark = " **(int)**" if NPC_INTERRUPT.search(d.get("description") or "") else ""
                if sid in noart:
                    mark += " ⚠"
                # Reviewed inventory wins; the tree label is the fallback and
                # covers the 18 classes that have no inventory. `all` means the
                # talent sits in the class root tree, not a spec tree.
                # A spell in the roster but in NO spec tree is inherent to the
                # whole class -- that is what "just the class name" means on
                # the spell page (Ley Lock reads plain "Runemaster"). So the
                # fallback is `all`, not `?`. `?` now only survives if a class
                # has no digest at all.
                spec = inv.get((c.slug, int(sid))) or tree_spec or "all"
                rows.append((c.id, cname, spec,
                             f"[{d['name']}](https://db.exil.es/spell/{sid}){mark}",
                             boss.get(sid, ""),
                             fmt_cd(d.get("cooldown_ms")), fmt_cost(d),
                             fmt_cast(d), desc(d), d["name"]))
        seen, out = set(), []
        # A spell listed BOTH as a trainable class spell and as a talent in a
        # spec tree yields two rows; keep the one naming a real spec.
        # `all (tree)` is INFORMATIVE, so it outranks a bare roster listing.
        _generic = lambda sp: sp in ("all", "?")            # noqa: E731
        for r in sorted(rows, key=lambda x: (x[0], x[1], x[9], _generic(x[2]))):
            if (r[1], r[9]) in seen:
                continue
            seen.add((r[1], r[9]))
            out.append(r)
        if not out:
            print("_None found._\n")
            continue
        head = ("| Class | Spec | Ability | Usable on Boss | CD | "
                "Materials Required | Cast Time | Description |")
        rule = "|---|---|---|---|---|---|---|---|"
        body = [f"| {cn} | {sp} | {nm} | {bo} | {cd} | {co} | {ca} | {ds} |"
                for _i, cn, sp, nm, bo, cd, co, ca, ds, _raw in out]
        print(head)
        print(rule)
        for line in body:
            print(line)
        # The same table again as raw source, collapsed. Fencing the ONLY copy
        # would stop it rendering; showing only the rendered one leaves no way
        # to lift it into a spreadsheet or a Discord post without reselecting
        # 20 rows by hand.
        print()
        print("<details><summary>Copy this table as markdown</summary>")
        print()
        print("```markdown")
        print(head)
        print(rule)
        for line in body:
            print(line)
        print("```")
        print()
        print("</details>")
        miss = sorted({c.name for c in CLASSES.values()} - {r[1] for r in out})
        print(f"\n**{len(out)} across {len({r[1] for r in out})} classes.**")
        print(f"None found for: {', '.join(miss)}." if miss else "Every class has one.")
    print(TAIL)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
