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
# `ally` as well as `allies`. Missing it hid Cultist's `Protection From Light`
# (804065), a 30s -40% Holy/Fire cooldown on a single ally, from the ACTIVE
# raid-DR table -- its tooltip says "an ally", never "allies".
GROUP = re.compile(r"\b(party|raid|all(y|ies)|group|friendly target)\b", re.I)
OUT_OF_COMBAT = re.compile(r"(cannot|can not|not) (be (cast|used)|usable)"
                           r"[^.]{0,20}in combat", re.I)

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
    "rez": "`effect_id 18` (RESURRECT) or `113` (RESURRECT_NEW), **usable in "
           "combat, on a player**. Both effect ids are in use -- matching only "
           "18 finds 2 spells and misses almost everything.\n\n"
           "Out-of-combat resurrects are NOT here: a res you cannot cast mid-"
           "pull is not a raid cooldown. That excludes eleven, including "
           "Chronomancer's `Resynchronize` (30 min, whole party, but "
           "\"cannot be used in combat\") and every 8-10 sec cast. Necromancer's "
           "`Reanimate` is excluded too -- it raises a CORPSE as a temporary "
           "pet, not a player.\n\n"
           "Reagent cost is tracked per ability rather than boss usability: a "
           "battle rez targets an ally, so boss immunity is meaningless, while "
           "the reagent is the thing that stops you casting it.",
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
| `Barbarian · Barbarian (row 1, col 5)` | `all (tree)`<br>`r1 c5` | A talent in the **class** tree. Any spec can take it, but it **costs a point**. |
| `Stormbringer · Stormbringer — Maelstrom (row 5, col 8)` | `Maelstrom`<br>`r5 c8` | A talent in that **spec's** tree. |

**A `rN cN` under the spec means you must spec into it**, and says where the
node sits so you can find it in the tree. No position means the ability is
baseline -- it is in no tree, so there is nothing to spend a point on.

So `all` and `all (tree)` differ in whether the raid can assume it is present:
baseline is always there, a class-tree talent is a build choice.

Where a class has a reviewed `resources/abilities-<slug>.md`, its Specs column
wins over the tree -- that is why Runemaster and Chronomancer rows read
`glyphic,engravement,riftblade` and `artificer,infinite,time` instead of `all`.

**The tree LABEL is authoritative; the tree SLUG is not.** `stormbringer-gifts`
is the Maelstrom tree, `felsworn-felblood` is Infernal, and
`pyromancer-destruction` is FLAMEWEAVING -- the healing spec. Reading slugs as
spec names is wrong on at least three classes, so the parser reads the label.

## ❌ and ⚠ -- is it actually in the game?

**⚠ = no icon on db.ascension.gg, unverified.** A CoA ability with no art may
be unimplemented, cut, or a leftover row.

**Confirmed absent = removed from the tables entirely.** One so far: Barbarian's
`Wrist Snap`, checked in game 2026-08-02. It is not annotated, it is gone -- a
struck-through row still reads as an option at a glance, and the point of
checking was to stop planning around it. `resources/icon-missing.json` keeps
the record under `confirmed_absent` so nobody re-adds it.

Barbarian still has `Jawbreaker` (14s), so removing `Wrist Snap` costs the
class nothing -- it had two listed and one was never real.

**How much is ⚠ worth? Less than it first looked.** Six interrupts carried it
and five were checked in game: `Hellgaze`, `Throatpunch`, `Halt`, `Solar Burn`
and `Distracto Shot` are all REAL. Only `Wrist Snap` was not. So a missing icon
ran about 1-in-6 on the sample that has been tested -- a reason to check, not a
reason to disbelieve the row. The earlier revision of this section called it
"very likely not in the game", and the testing says otherwise.

Both lists live in `resources/icon-missing.json`. Confirm one in game, move its
id to `confirmed_present` or `confirmed_absent`, and regenerate. 20 remain
unverified.

## Buttons only, not the effects they apply

Every row should be **the ability the class presses**, never the debuff or aura
it puts on the target. Three filters enforce that, and each was added because
something got through:

* **Same class, same tooltip, one has a cooldown.** The one without is the
  component. db.exil.es copies a parent's tooltip verbatim onto its child and
  carries the parent's mana cost across, so `Frayed` (510237) looked castable
  on every field -- it is the silence `Fray Magic` (510236) applies. Past-
  participle names are the human tell: `Burned`, `Frozen`, `Shattered`,
  `Dazzled`.
* **A reviewed inventory wins.** Where `resources/abilities-<slug>.md` was read
  row by row, an ability missing from it was excluded on purpose. That is how
  Runemaster's `Fragmented` (a Fire Sigil-granted steal) and `Matter Swap` (a
  familiar swap that happens to stun) leave the tables while `Leyfeed`, which
  the inventory annotates "a spellsteal", stays.
* **The tooltip must agree with the mechanic.** See below.

Two limits on that middle filter, both learned the hard way:

  It applies to **Runemaster and Chronomancer only**. Pyromancer's inventory
  was machine-proposed and bulk-cleared, so absence from it means "the pass did
  not place it", not "a person decided against it" -- treating it as
  authoritative dropped `Lucifron's Lagniappe`, a real 30s raid-DR cooldown
  still sitting in that class's candidate list.

  It matches on **name as well as id**. The inventory carries hand-corrected
  ids and therefore disagrees with the digest on exactly the abilities that
  matter most: `Fray Magic` is 800053 there and 510236 in the digest, and an
  id-only check deleted Chronomancer's only interrupt.

Audited all 114 rows for component signatures -- APPLY_AURA-only effects, no
cooldown, a near-name or adjacent-id sibling that has one. Everything still
listed is a button. Note that "no cooldown and applies an aura" is NORMAL for a
real CoA ability and is not on its own evidence of anything: `Cindergrip`,
`Decelerate` and `Cryobrand` all look like that and all appear in a reviewed
inventory as real.

## The hand-observed columns

Two columns hold facts **no database carries**: db.exil.es records neither
immunity nor reagents. Both are therefore hand-filled, and **blank means
untested, never "no"** -- a raid plans around these, and a guess is worse than
a gap.

| Table | Column | Question |
|---|---|---|
| Battle Rezzes | **Reagent Required** | what item it consumes |
| everything else | **Usable on Boss** | does it land on a raid boss |

Fill them in `resources/spell-observed.json`, NOT in this file:

```json
"spells": {
  "800995": {"boss": "yes",     "note": "Ley Lock -- lands on every ZG boss"},
  "991349": {"boss": "no",      "note": "Monolith Smash -- stun immune"},
  "806599": {"boss": "partial", "note": "Stormhammer -- Jin'do yes, Hakkar no"},
  "801792": {"reagent": "Corpse Dust", "note": "Call of The Scourge"},
  "500688": {"reagent": "none", "note": "Spiritual Ascension -- confirmed free"}
}
```

Then re-run the generator. The column is rebuilt from that file every time, so
a value typed into this markdown is destroyed on the next run and a value in
the JSON survives. That is the whole reason it is a separate file: this page is
regenerated wholesale, and hand-tested knowledge is the one thing here that
cannot be regenerated.

`boss`: `yes` / `no` / `partial`. `reagent`: the item, or `none` once
confirmed to need nothing. Omit a field entirely while it is untested.

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


def observed():
    """spell id -> "yes" / "no" / "partial", from resources/spell-observed.json.

    HAND-TESTED, and deliberately the only source. db.exil.es carries no
    immunity data at all, so whether a stun lands on a boss cannot be derived
    from anything in the mirror -- and a guess in this column is worse than a
    blank, because a raid plans around it. An id with no entry renders empty.

    It lives in a data file rather than in the markdown because this page is
    regenerated wholesale; a value typed into the table would be destroyed by
    the next run, which is exactly the trap the "do not hand-edit" banner
    warns about.
    """
    p = data("spell-observed.json")
    if not os.path.exists(p):
        return {}
    raw = json.load(open(p, encoding="utf-8")).get("spells") or {}
    return ({str(k): (v.get("boss") or "").strip() for k, v in raw.items()},
            {str(k): (v.get("reagent") or "").strip() for k, v in raw.items()})


def no_icon():
    """(suspected, confirmed_absent) spell ids.

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
        return set(), set()
    raw = json.load(open(p, encoding="utf-8"))
    return (set(raw.get("ids") or {}),           # no icon, unverified
            set(raw.get("confirmed_absent") or {}))   # checked, not in the game


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
            out[str(sid)].append((c.name, name, None, None))
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
                # row/col so a reader can find the node in the tree. Only a
                # TALENT has one -- a baseline ability is in no tree at all.
                out[str(sid)].append((c.name, name, t["spec"] or "all (tree)",
                                      f"r{_r} c{_col}"))
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
        # Plain asterisk: the MARKDOWN writer escapes it, because escaping here
        # leaked a literal backslash into the HTML page, which renders the
        # site's cast column as `Instant\*`.
        return "Instant*"
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


def _components(cache, own):
    """Ids that are the APPLIED EFFECT of another ability, not a button.

    db.exil.es copies a parent's tooltip verbatim onto the aura it applies, and
    gives the child an adjacent id and often the parent's mana cost -- so a
    component looks castable on every field this file reads. Chronomancer's
    `Frayed` (510237) is the silence debuff of `Fray Magic` (510236): identical
    text, 27% cost on both, but cd=0 and a single APPLY_AURA effect where the
    parent has INTERRUPT_CAST.

    The general signal: same class, same tooltip, one has a cooldown and the
    other does not. The one without is the component. Past-participle naming
    (`Burned`, `Frozen`, `Shattered`, `Dazzled`, `Frayed`) is the human tell,
    but the tooltip match is what is actually checked.
    """
    by = collections.defaultdict(list)
    for sid, d in cache.items():
        if sid not in own:
            continue
        t = " ".join((d.get("description") or "").split())[:120]
        if not t:
            continue
        for cname, _n, _sp, _rc in own[sid]:
            by[(cname, t)].append((sid, d))
    out = set()
    for rows in by.values():
        if len(rows) < 2:
            continue
        withcd = [r for r in rows if r[1].get("cooldown_ms")]
        if not withcd:
            continue
        for sid, d in rows:
            if not d.get("cooldown_ms"):
                out.add(sid)
    return out


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
        # BATTLE rezzes only: usable in combat, on a PLAYER.
        #
        # Order the checks negative-first. "Not usable in combat" contains the
        # substring "usable in combat", so a positive-first test reads Sun
        # Cleric's `Revivify` as a battle rez -- it is the opposite.
        if OUT_OF_COMBAT.search(t):
            return None
        # Necromancer's `Reanimate` raises a CORPSE as a temporary pet. It
        # matches the resurrect effect and is not a rez in any raid sense.
        if not re.search(r"\b(ally|allies|player|party|raid member)\b", t, re.I):
            return None
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


def tables():
    """[(cat, title, note, column, rows)] -- the structured tables.

    Split out so the site can render the SAME rows as HTML without
    parsing the markdown back. One source, two outputs.
    Each row is (class, spec, name, url, marks, observed, cd, cost,
    cast, desc).
    """
    own, inv, cache = owners(), inventory(), spells()
    boss, reagent = observed()
    noart, gone = no_icon()
    comps = _components(cache, own)
    buckets = collections.defaultdict(list)
    # Where a class has a REVIEWED inventory, that review is authoritative and
    # an id missing from it was excluded by a human on purpose. Runemaster's
    # `Fragmented` (712338) is the case: a Fire Sigil-granted steal effect that
    # carries effect 126 and looks like a spellsteal here, while the inventory
    # lists only `Leyfeed` and annotates it "a spellsteal". Trusting the effect
    # id over the review would re-add every component a person already threw
    # out. Classes with no inventory are unaffected.
    # ONLY the two inventories a human actually read row by row. Pyromancer's
    # was machine-proposed and bulk-cleared (see the provenance note in
    # notes/class-pack-process.md), so absence from it means "the pass did not
    # place it", not "a person decided against it" -- and treating it as
    # authoritative silently dropped `Lucifron's Lagniappe`, a real 30s raid-DR
    # cooldown sitting unpromoted in that class's candidate list.
    reviewed = {"runemaster", "chronomancer"}
    # Match on NAME as well as id. The inventory carries hand-CORRECTED ids, so
    # it disagrees with the digest on exactly the abilities most likely to
    # matter: Chronomancer's `Fray Magic` is 800053 in the inventory and 510236
    # in the digest, and an id-only check dropped the class's only interrupt.
    inv_names = collections.defaultdict(set)
    for c in CLASSES.values():
        p_ = data(f"abilities-{c.slug}.md")
        if not os.path.exists(p_):
            continue
        for line in open(p_, encoding="utf-8"):
            if line.startswith("| ") and not line.startswith("| Ability"):
                cells = [x.strip() for x in line.strip().strip("|").split("|")]
                if len(cells) >= 6:
                    inv_names[c.slug].add(cells[0])
    for sid, d in cache.items():
        # Confirmed-absent ids are EXCLUDED, not annotated. An ability somebody
        # logged in and could not find is not part of the raid picture, and a
        # struck-through row still reads as an option at a glance. What was
        # checked and found missing is recorded in resources/icon-missing.json
        # under `confirmed_absent` so the result is not re-litigated.
        if sid not in own or sid in comps or sid in gone:
            continue
        cat = classify(d)
        if not cat:
            continue
        drop = False
        for cname, _n, _sp, _rc in own[sid]:
            c = next(x for x in CLASSES.values() if x.name == cname)
            if (c.slug in reviewed and (c.slug, int(sid)) not in inv
                    and d["name"] not in inv_names.get(c.slug, ())):
                drop = True
        if drop:
            continue
        buckets[cat].append((sid, d))

    out_tables = []
    for cat in ORDER:
        col = "Reagent Required" if cat == "rez" else "Usable on Boss"
        rows = []
        for sid, d in buckets.get(cat, []):
            for cname, _a, tree_spec, rc in own[sid]:
                c = next(x for x in CLASSES.values() if x.name == cname)
                spec = inv.get((c.slug, int(sid))) or tree_spec or "all"
                marks = []
                if NPC_INTERRUPT.search(d.get("description") or ""):
                    marks.append("int")
                if sid in noart:
                    marks.append("noicon")
                rows.append((c.id, cname, spec, rc or "", d["name"],
                             f"https://db.exil.es/spell/{sid}", marks,
                             (reagent if cat == "rez" else boss).get(sid, ""),
                             fmt_cd(d.get("cooldown_ms")), fmt_cost(d),
                             fmt_cast(d), desc(d), sid))
        seen, keep = set(), []
        _generic = lambda sp: sp in ("all", "?")            # noqa: E731
        for r in sorted(rows, key=lambda x: (x[0], x[1], x[12], _generic(x[2]))):
            if (r[1], r[12]) in seen:
                continue
            seen.add((r[1], r[12]))
            keep.append(r)
        missing = sorted({c.name for c in CLASSES.values()} - {r[1] for r in keep})
        out_tables.append((cat, TITLES[cat], EFFNOTE[cat], col, keep, missing))
    return out_tables


def _md_spec(spec, rc):
    """Spec cell for markdown: position under the spec, `<br>` for the break."""
    return f"{spec}<br>{rc}" if rc else spec


def _md_cell(t):
    """Escape markdown-significant characters for a table cell."""
    return t.replace("*", "\\*")


def _md_name(name, url, marks):
    s = f"[{name}]({url})"
    if "int" in marks:
        s += " **(int)**"
    if "noicon" in marks:
        s += " \u26a0"
    return s


def main(argv):
    out_tables = tables()
    if "--check" in argv:
        for cat, _t, _n, _c, rows, _m in out_tables:
            print(f"  {cat:16} {len(rows)}")
        return 0

    print(FRONT)
    for cat, title, note, col, rows, missing in out_tables:
        print(f"\n## {title}\n\n{note}\n")
        if not rows:
            print("_None found._\n")
            continue
        head = (f"| Class | Spec | Ability | {col} | CD | "
                "Materials Required | Cast Time | Description |")
        rule = "|---|---|---|---|---|---|---|---|"
        body = [f"| {cn} | {_md_spec(sp, rc)} | {_md_name(nm, url, mk)} | "
                f"{ob} | {cd} | {co} | {_md_cell(ca)} | {ds} |"
                for _i, cn, sp, rc, nm, url, mk, ob, cd, co, ca, ds, _sid in rows]
        print(head)
        print(rule)
        for line in body:
            print(line)
        # The same table again as raw source, collapsed. Fencing the ONLY copy
        # would stop it rendering; showing only the rendered one leaves no way
        # to lift 20 rows into a spreadsheet or a Discord post by hand.
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
        print(f"\n**{len(rows)} across {len({r[1] for r in rows})} classes.**")
        print(f"None found for: {', '.join(missing)}."
              if missing else "Every class has one.")
    print(TAIL)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
