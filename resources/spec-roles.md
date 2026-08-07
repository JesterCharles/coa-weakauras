---
title: Which CoA specs heal, tank, and do damage
date: 2026-08-02
type: reference
status: seedling
tags: [wow, ascension, conquest-of-azeroth, reference, specs, roles]
source: "observed in game, per class, as the class is built"
---

# Spec roles

What a spec *is for*. Not derivable from anything already in this repo, and
wrong in the one place it looks derivable — see the trap below.

## Why this file exists

Role changes what a pack must show. A healing spec earns the target band
(`dot_bars(helpful=True)`: your HoTs and absorbs on your current target,
glowing when one needs a refresh) and its main row is a healing rotation, not a
damage one. Assigning a role to 200-odd abilities without knowing which of
those two you are looking at means guessing, and the inventory review is
explicitly the step where guessing is not allowed.

**Healing surfaces stay scoped OUT.** Settled on Chronomancer's Time spec, the
first healer in any pack here, and it holds for every healer since: raid-frame
health and multi-target HoT state belong to VuhDo/Grid, which own that job on
3.3.5a. What a pack carries is the *target* band — what you have on whoever you
are targeting right now — and nothing wider.

## THE TRAP

**db.exil.es's tree slug is not the role and can be its opposite.**
Pyromancer's healing spec, Flameweaving, is filed upstream as
`pyromancer-destruction`:

```
### Pyromancer — Flameweaving (slug: `pyromancer-destruction`)
```

Read that slug as a hint about the spec and you would build the healer as a
destruction DPS. Tree slugs are filing, in the same way `spell.line` and
Sidekick mention counts are filing — none of the three is access, membership or
role. This one is just the loudest example.

## The table

`Role` is one of `damage`, `healing`, `tank`. A class absent from this table
has not been observed yet; the tools treat that as unknown rather than assuming
damage, because assuming damage is exactly how a healer's target band would go
missing without any error.

| ID | Class | Spec | Role |
|---|---|---|---|
| 22 | Chronomancer | artificer | damage |
| 22 | Chronomancer | infinite | damage |
| 22 | Chronomancer | time | healing |
| 24 | Pyromancer | incineration | damage |
| 24 | Pyromancer | flameweaving | healing |
| 24 | Pyromancer | draconic | damage |
| 32 | Runemaster | glyphic | damage |
| 32 | Runemaster | engravement | damage |
| 32 | Runemaster | riftblade | damage |
| 15 | Witch Hunter | boltslinger | damage |
| 15 | Witch Hunter | houndmaster | damage |
| 15 | Witch Hunter | black-knight | tank |
| 15 | Witch Hunter | inquisition | damage |

**Witch Hunter provenance (15):** not yet observed in game — filled from
citable Sidekick statements, one per spec: black-knight "Solid main-tank for
raid bosses … Strong dungeon tank — AoE pulls and threat" (plus taunts,
Night's Watch threat toggle, High Threat abilities); boltslinger and
houndmaster "Middling in arena as a damage dealer" with no ally heal or tank
kit anywhere; inquisition "Top-tier sustained single-target DPS … Solid in
arena as a damage dealer" (`resources/sidekick-witch-hunter-*.md`, scraped
2026-08-07). No spec heals, so no healing target band can go missing. Confirm
in game with the first witch-hunter `verified` pass.

## Corroboration

Observation comes first — these were read off the specs in game. The kit
agrees, which is worth recording because it gives a cheap check for the
19 classes not yet built: count the abilities whose tooltip mentions
healing, absorbing or shielding, per spec.

| Class | Spec | abilities mentioning heal/absorb/shield |
|---|---|---|
| 24 | Pyromancer incineration | 2 / 43 (5%) |
| 24 | Pyromancer flameweaving | **28 / 84 (33%)** |
| 24 | Pyromancer draconic | 4 / 51 (8%) |

The healer stands out by roughly 5x. That is a strong enough signal to *flag* a
spec for a look, and nowhere near strong enough to set this table from — the
same rule that keeps Sidekick mention counts out of the Specs column. Fill a
row by playing the spec.
