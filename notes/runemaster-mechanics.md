---
title: Runemaster (CoA) — mechanics, retail analogs, tracking surface
date: 2026-07-27
type: note
status: budding
tags: [wow, ascension, conquest-of-azeroth, runemaster, weakauras, class-design]
sources:
  - "[[../resources/sidekick-runemaster-glyphic]]"
  - "[[../resources/sidekick-runemaster-engravement]]"
  - "[[../resources/sidekick-runemaster-riftblade]]"
---

# Runemaster — mechanics and what a WeakAura must show

Class ID **32** on db.ascension.gg. Cloth. Resources: **Mana + Runes + Essences**.
Three specs. Note the DB and the live game disagree on spec names:

| Icon slug / live name | db.ascension.gg name | Skill line ID | Role |
|---|---|---|---|
| Glyphic | Spellslinger | 116 | Ranged DPS (Int) |
| Engravement | Conjuration | 117 | Melee DPS (Agi) |
| Riftblade | Riftblade | 119 | Melee DPS (Agi) |
| — | Runemaster (shared) | 481 | — |

**db.ascension.gg is stale for this class.** Runeblade, Zenith, Runic Brand, Hurricane,
Hoarfrost, Genesis, Primordial Fury, Fist of the Ancients, Elemental Carving, Wild Steam,
Guarding Rune and Speed Rune all appear on Sidekick's live talent trees but return *no*
class-32 rows in the DB. Treat Sidekick as authoritative for current names and behaviour,
and the DB only as an ID hint. See [[wa-import-string-format]] for why this pushed the
design to name-based matching.

## Class-wide systems (all three specs)

**Runic Tattoos** — an attunement stance. Six elements, and the set is
**Air, Arcane, Earth, Fire, Frost, Water** — there is **no Ice tattoo**. Talents key off
the active tattoo (Stone Petroglyph on Earth, Nomad's Scroll on Air, mana sustain on
Water). Buff IDs seen in a working community aura: Earth `803756`, Water `803784`,
Air `802630`, Arcane `803760`, Fire `803749`, and `807836` which that author labelled
"Ice" but which must be **Frost** given the spell list.

Tattoos are set before a pull rather than rotated in combat ("set your Runic Tattoo to
whatever the group needs — Earth for Granite Shield uptime, Water if your own mana margin
is thin"), so the tattoo itself needs only a small persistent indicator. The bespoke work
is in the *conditional payoffs*: Stone Petroglyph and Granite Shield on Earth, Unleashed
Tattoos (Fire → +30% Glyphic Ruin crit damage, Water → -50% Glyphic Ruin cost), the
Riftblade/Leystone Springs Water bonuses, Wind Walker on Air.

**Weapon Engravings** — six weapon imbues that proc on hit, *not* an aura. The set is
**Air, Arcane, Earth, Fire, Ice, Water** — note this is where "Ice" lives, and there is no
Frost engraving. This is the exact inverse of the tattoo list and is easy to get backwards.

They are exposed to WeakAuras as **temporary weapon enchants**, matched by enchant name
(`Fire Engraving`, `Ice Engraving`, …). They last **1 hour** and only one type can be
active, so a missing-imbue check is an out-of-combat setup cue, not a rotational one.
Engravement dual-wields and talents read "**each weapon** enchanted by Weapon Engraving:
Earth", so a trigger must check **both** weapons, not just main-hand.

What actually changes in combat is the *proc-chance window*: Master Engraver (+5%),
Uncovered Engravings (+20% for 5s off Fist of the Ancients), Zenith (+100% for 6s, 12s
with Runic Affinity), Decoder (20% instant off Elemental Burst / Runeblade) and
Convergence (next 10 engravings deal bonus damage, 15s).

**Shared cooldowns** — Zenith (engraving-chance burst), Granite Resolve (-30% physical,
usable while stunned), Ley Lock (hard interrupt), Warding Rune (magic immunity window),
Speed Rune (party movement path), Power Engraving (party magic-damage zone),
Phase Out (stealth + Runeshroud), Warpdagger (throw-and-teleport).

## Glyphic — retail analog: Arcane Mage

Build-and-detonate. **Elemental Burst, Primordial Blast and Runic Obliteration** generate
a **Glyph**, which escalates in a chain: Frost Glyph → (while active) Flame Glyph →
(while active) Arcane Glyph. Glyphs are **unleashed** by Glyphic Ruin (hard cast, big) or
Thaumaturgy (instant, cheap). Unleashing splashes nearby enemies via Primordial Salvos.

The chain is **not** a strict one-active-glyph escalator, and two things break that model:
Runic Obliteration is a multi-missile instant where "each missile grants you a Glyph", so
it can advance several stages in one cast; and **Glyphic Overload instantly generates all
three glyphs at once** ("Instantly generate Frost Glyph, Flame Glyph, and Arcane Glyph on
yourself and overload, granting all active Glyphs an additional effect the next time you
unleash them"). Any chain display must handle all three being up simultaneously.

Glyphic Overload is *not* the guaranteed-crit effect — that is a separate talent,
**Arcane Student** ("While Glyphic Overload is active, your Glyphic Ruin is guaranteed to
critically strike").

Glyph aura IDs from a working aura: Frost `520090`, Flame `520091`, Arcane `520092`.
Glyphic Overload `520099`, Thaumaturgy `520071`, Frigid Blast proc `802648`.

Single-target play deliberately runs a **tight 2-glyph loop** keeping Flame Glyph's fire
DoT stacked, because the Arcane unleash splash is wasted on one target. Full three-glyph
chain is the AoE pattern. This is the single most important thing a rotation aura must get
right, and it is the opposite of what the ability tooltips imply.

Burst window: Eye of the Beholder + Glyphic Overload (which makes Glyphic Ruin a
guaranteed crit). Mana is punishing — costs are a flat % of *base* mana and there is no
burst mana return.

## Engravement — retail analog: Enhancement Shaman

Agility dual-wield melee. Autoattacks proc Weapon Engravings. Separately —
**not** fed by engravings — **Fist of the Ancients** unleashes an **Elemental Carving at
random** (Fire = armor pen, Water = mana, Earth = % missing health, Air = haste). The
randomness is the mechanic: "Elemental Carvings are RNG you manage rather than control —
bank Water for mana and Earth for the self-heal, time Fire and Air for burst." Which one
just landed therefore needs to be on screen.

**Runeblade** is the filler: **3 charges, 6 sec recharge**, refreshed 3 at a time by
Eternal Magic.

**Runic Brand** is not a self-detonating DoT. It marks the enemy for 8s with
**`Marked: Runic Brand`**, and "your next **Runeblade** on the enemy causes a Runic
Explosion" — the mark is *spent by Runeblade*. Leyborn raises it to 3 stacks. **Power
Overwhelming** (35% off Runeblade / Primordial Blast) resets Runic Brand's cooldown, and
**Branded** guarantees the next one crits. Runic Brand cast while a tattoo is active also
projects that tattoo's aura within 8yd for 8s, and "switching Runic Tattoos removes the
current aura" — that sentence is about *this* projected aura, not about tattoo stances.

Zenith has **2 charges** (Echoes of Eternity, 45s recharge) and its Runelord follow-up
gives +30% Runic Brand and Weapon Engraving damage for 8s.

Cooldowns: Zenith → Runelord follow-up, Runic Tempest (resets Fist of the Ancients and
unlocks Runeshroud abilities), Fists of Power (haste), Power Engraving (party DPS zone),
Guarding Rune (party magic reduction), Genesis (accumulate-then-detonate brand).

## Riftblade — retail analog: Enhancement Shaman + Frost DK runes, *but the core is unique*

**The actual played core is Runeblade, not sigils.** Sidekick states it outright:
"The engine is Runeblade weaving into elemental weapon strikes and cooldown detonations.
**This is a straight two-handed melee spec, not an attunement or sigil builder.**" The
recommended 25/25 Riftblade build takes no sigil, blade or Runestone node, and neither
rotation writeup mentions them. The sigil system below is real and in the kit, but it is
an alternate/levelling path — do not make it the centrepiece.

The real tracking need is the **Runeblade beat**: 3 charges on a 6s recharge, refreshed by
Primordial Blast and Smolder, with three separate payoffs landing on **every 3rd cast** —
Runic Omen (+30% damage), Surging Slash (next Runeblade within 15s becomes Surging Slash)
and Riftblade itself (restores mana, +20% under Runic Tattoos: Water). Around that:
Spellfire Runes (Runeblade 20% / Warpdagger 100% chance to reset Smolder and buff it
+20%), Windsage (Smolder → next 3 Runeblades strike an extra time), Swift Etching
(+15% melee haste, +10% crit for 10s after Hurricane) and the Frozen-target state that
several abilities multiply off.

### The Sigil → Runestone recipe system (secondary)

This part genuinely **has no retail equivalent**. Sigil generators are *not* only the three
blades — Glyphic Invocation ("generates 1 Sigil matching your current Attunement") and
Shrouded Hand's Imbue Flame/Frost/Arcane also each generate one:

- Arcane Blade → 1 **Arcane** Sigil
- Fire Blade → 1 **Fire** Sigil
- Frost Blade → 1 **Frost** Sigil

At three sigils, **Elemental Burst** expends the combination and fires the Runestone
matching that exact multiset. **Runecarve** clears sigils without breaking Runeshroud.
**Unleash Essences is a different system** — it spends an *Essence Combination* defined by
*Lost Page* passives, not Sigils, and must not be treated as an Elemental Burst alias.

| Recipe | Runestone | Effect summary |
|---|---|---|
| 3 Arcane | Foretelling `803016` | Arcane damage, multi-target |
| 3 Fire | Pyrostrike `803009` | Big single-target Fire hit |
| 3 Frost | Frost Prison `803014` | Frost damage + stun (DR: cannot re-apply) |
| 2 Arcane + 1 Fire | Walking Flame `803012` | Spellfire, splash + DoT |
| 2 Arcane + 1 Frost | Frozen Touch `803015` | Melee attacks cleave bonus Frost |
| 2 Fire + 1 Arcane | Torch `803011` | Spellfire DoT |
| 2 Frost + 1 Arcane | Spellsnap `803017` | Spellfrost splash + Frost/Arcane vuln debuff |
| 2 Frost + 1 Fire | Dazzling Spray `803010` | Frostfire + incapacitate (breaks on damage) |

There are ten 3-sigil multisets but only eight Runestones. **2 Fire + 1 Frost** and
**1 Arcane + 1 Fire + 1 Frost** have no Runestone in the full kit.

Two caveats that constrain any predictor built on this. First, every Runestone is a
**learned passive** — each reads "*Allows* Elemental Burst to expend the above Sigil
combination", and two of them grant their generator ("Teaches Arcane Blade", "Teaches
Frost Blade"). A character who has not learned Torch has *three* dead combinations, not
two, so a hard-coded "these two are dead" warning is wrong for exactly the under-built
players who most need it; the warning has to be driven by which passives are known.
Second, **nothing in the source states a 3-sigil cap** or that Elemental Burst requires
exactly three — that is inference from the recipes, and it is unverified.

Also unique: **Runeshroud**, a stealth state that rewrites each blade's effect
(Arcane → spell haste reduction, Fire → DoT + healing reduction, Frost → stun).
**Palm Sigils are six, not three** — Arcane, Earth, Fire, Frost, Water, Wind — each a
"your next instance of direct damage" consumable, and Earthen Codex turns activating one
into a guaranteed-crit window (+20% crit damage for 10s *or* the next 3 attacks).

## What this means for tracking

Spec-unique *buff* displays self-filter — a Riftblade never has a Flame Glyph, so Glyphic
glyph icons never activate. But that argument **does not extend to cooldown displays or to
the shared kit**: Zenith, Granite Resolve, Ley Lock, Warding Rune, Speed Rune, Power
Engraving, Phase Out, Warpdagger, Runeblade, Primordial Blast, Elemental Burst, tattoos
and engravings are common to all three specs, and a spell-cooldown trigger set to
`showAlways` will render even for a spell the player does not know. Without gating, a
Glyphic player sees Engravement and Riftblade rows.

`load.class_and_spec` cannot do the gating — the only observed value, `64`, collides with
retail's Frost Mage ID and is probably the underlying cloth-caster mapping rather than a
real CoA spec ID. The workable gate is a **custom Lua group trigger** calling
`GetSpellInfo("<signature spell>")`, which returns nil on 3.3.5a for a spell the player
does not know.

Finally, **name collisions are real**, so the "prefer names over IDs" rule has exceptions.
Verified same-name-different-thing cases: *Runic Obliteration* (a castable Glyphic
generator vs an Engravement L50 passive), *Fists of Power* (an Engravement talent and an
Engravement L10 passive), *Runic Tattoos* (a class talent reducing resource costs, and the
six stance spells), and *Genesis*, *Hurricane*, *Swift Etching* and *Elemental Burst*
appearing across multiple specs with different roles.
