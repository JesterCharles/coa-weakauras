---
title: Runemaster IDs verified from in-game tooltips
date: 2026-07-27
type: reference
status: budding
tags: [wow, ascension, conquest-of-azeroth, runemaster, spell-ids, ground-truth]
---

# IDs read directly off in-game tooltips

This is the only fully trustworthy tier of data. Where it disagrees with
db.exil.es, **this wins** — see [[../notes/runemaster-mechanics]] for the
source-reliability ranking.

## Weapon Engravings (cast spells)

All six are instant, 73 mana, and engrave a rune onto your weapon for **1 hour**.

| Engraving | ID | Effect |
|---|---|---|
| Fire | **653022** | 35% chance to ignite, 91 Fire damage per stack after 3 sec |
| Earth | **653218** | 20% chance for 86 extra Nature damage to enemies within 5 yds |
| Water | **653213** | 35% chance for 56 damage, drains 43 mana, grants allies Replenishment (5% max mana per 5 sec for 15 sec) |
| Air | **653222** | 20% chance to replicate 45% of the damage dealt to the target |
| Arcane | **653265** | 30% chance for 163 Arcane damage and −30% healing received for 10 sec |
| Ice | **653264** | 45% chance for 159 Frost damage and a movement slow |

**db.exil.es was wrong on two of these:** it lists Arcane as `653263` and Ice as
`653217`. The tooltips say `653265` and `653264`. Do not trust the scraped values
for these two.

The element set is confirmed as **Air, Arcane, Earth, Fire, Ice, Water** — there
is no Frost engraving. Frost belongs to the tattoos (`Runic Tattoos: Frost`
807834), and the two lists are otherwise easy to confuse.

## Abilities where db.exil.es returns the wrong id

db.exil.es's class page sometimes links a **proc or damage component** rather
than the castable ability, so its name→id map silently returns a spell that has
no cooldown and that the player does not know. The display then never fires.

| Ability | Correct id (tooltip) | db.exil.es gave | What the wrong id is |
|---|---|---|---|
| Convergence | **801086** — 147 mana, instant, 1.5 min CD | 560241 | the damage proc ("Procs from Convergence") |
| Primordial Fury | **806543** — 171 mana, instant, 1.5 min CD | 801095 | a 45-damage component |

Convergence: "For 15 sec, the next 10 Weapon Engravings you trigger will now deal
an additional 515 Elemental Damage."
Primordial Fury: "Your runic tattoos flare up for 15 sec, causing Runeblade to
strike up to 5 additional enemies. For the duration, your Runic Tattoos have 100%
increased effectiveness."

**Detection.** Cross-reference db.exil.es against db.ascension.gg and flag any
name where the exil.es id is not the id ascension.gg marks `advType: "Ability"`.
Across all of Runemaster that flags exactly three names — Convergence,
Greater Runes (705624) and Rune of the Elder Magus (705567). It does **not**
catch Primordial Fury, because db.ascension.gg lacks that spell entirely, so the
check narrows the search but does not replace a tooltip.

A second, cheaper smell: any ability you intend to track as a cooldown whose
db.exil.es page shows **no Cooldown row** is probably the wrong id.

## Still unverified

- Whether the engraving surfaces as a **player aura**, a **temporary weapon
  enchant**, or neither. The current pack matches cast id, imbue id, both names,
  and a weapon enchant on either hand, plus an `IMB` catch-all that fires on any
  main-hand enchant regardless of name.
- The `CoA Aura - Runemaster - <Spec>` gate auras (887088 / 887089 / 887090).
  119 of 141 displays hang off these, so if they are not player-visible auras the
  spec content shows nothing.
