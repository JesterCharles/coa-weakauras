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
| 14 | Felsworn | slayer | damage |
| 14 | Felsworn | infernal | damage |
| 14 | Felsworn | tyrant | tank |
| 22 | Chronomancer | artificer | damage |
| 22 | Chronomancer | infinite | damage |
| 22 | Chronomancer | time | healing |
| 24 | Pyromancer | incineration | damage |
| 24 | Pyromancer | flameweaving | healing |
| 24 | Pyromancer | draconic | damage |
| 16 | Stormbringer | lightning | damage |
| 16 | Stormbringer | wind | damage |
| 16 | Stormbringer | maelstrom | damage |

**Stormbringer provenance (16):** not yet observed in game — filled from
citable Sidekick kit statements, one per spec: lightning "There is no self-heal
anywhere in the kit", wind "no ally HP heal at all … not a group's healer"
(a buffer/support that is still `damage` in this three-role vocabulary),
maelstrom "no healer-grade throughput and no ally heal underneath"
(`resources/sidekick-stormbringer-*.md`, scraped 2026-08-07). No tank kit
appears in any of the three pages. Replace with an in-game read when one
exists.
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

**Felsworn provenance differs from the rest of this table:** the three rows
were filled 2026-08-07 from Sidekick's explicit statements (tyrant: "Top-tier
main-tank for raid bosses … as a tank"; slayer: "damage dealer … you cannot
heal or dispel anyone"; infernal: "damage dealer … No ally-targeted healing
here, and no self-heal either"), not from in-game observation. No spec heals,
so the roles cannot hide a missing healer target band — the failure this file
guards against. Confirm in game with the first felsworn `verified` pass.
| 21 | Ranger | archery | damage |
| 21 | Ranger | brigand | damage |
| 21 | Ranger | farstrider | damage |

**Ranger provenance (21):** not yet observed in game — filled from citable
Sidekick kit statements, one per spec: archery "No heal anywhere in the spec:
no shield, no HoT, no proc-heal … judge it as a pure MM-Hunter DPS spec";
brigand "a dagger-wielding melee assassin, not a healer despite the archetype
tag … There is no direct heal spell anywhere in this spec"; farstrider "only
minor incidental healing rather than a real HPS rotation … not anything
resembling a Discipline/Holy/Resto kit" (an Augmentation-style buffer, still
`damage` in this three-role vocabulary)
(`resources/sidekick-ranger-*.md`, scraped 2026-08-07). No tank kit appears
in any of the three pages. Replace with an in-game read when one exists.
| 30 | Reaper | domination | tank |
| 30 | Reaper | harvest | damage |
| 30 | Reaper | soul | damage |

**Reaper provenance (30):** not yet observed in game — filled from citable
Sidekick statements, one per spec: domination "Solid main-tank for raid
bosses … Strong dungeon tank"; harvest "This spec has no ally-targeted heal.
Its role in a group is soaking and holding pressure off the healer";
soul "This spec has no real heal-the-group kit … damage dealer"
(`resources/sidekick-reaper-*.md`, scraped 2026-08-07). All self-sustain is
leech, never an ally heal, so no healer target band can be hidden by these
rows. Replace with an in-game read when one exists.
| 13 | Witch Doctor | voodoo | damage |
| 13 | Witch Doctor | brewing | healing |
| 13 | Witch Doctor | shadowhunting | damage |

**Witch Doctor provenance (13):** not yet observed in game — filled from
citable Sidekick kit statements, one per spec: brewing "Solid dungeon healer —
spot-heals pull damage … Strong in arena as a healer" with a full heal loop
(Loa's Brew / Potion Toss / Mojo Beam / Cauldron); voodoo "Strong in arena as
a damage dealer … Voodoo has no ally heal, so your 'support' is protection
and pressure"; shadowhunting "Strong in arena as a damage dealer … built to
contribute sustained ranged damage, not to stand and heal"
(`resources/sidekick-witch-doctor-*.md`, scraped 2026-08-07). No tank kit
appears in any of the three pages. Replace with an in-game read when one
exists.
| 17 | Knight of Xoroth | war | damage |
| 17 | Knight of Xoroth | hellfire | damage |
| 17 | Knight of Xoroth | defiance | tank |

**Knight of Xoroth provenance (17):** not yet observed in game — filled from
citable Sidekick kit statements, one per spec: war "Middling sustained
single-target DPS … damage dealer" on every PvE/PvP line, "Nothing you have
heals anyone but you"; hellfire "Closest to Vengeance Demon Hunter, re-tuned
as a pure damage spec rather than a tank … No healing or lifesteal in the
spec at all"; defiance "Strong dungeon tank — AoE pulls and threat …
Middling main-tank for raid bosses", stat priority "Defense rating (to
crit-immunity)" (`resources/sidekick-knight-of-xoroth-*.md`, scraped
2026-08-07). No spec has an ally heal, so no healer target band can be hidden
by these rows. Replace with an in-game read when one exists.

| 31 | Primalist | geomancy | damage |
| 31 | Primalist | grovekeeper | healing |
| 31 | Primalist | mountain-king | tank |
| 31 | Primalist | wildwalker | damage |

**Primalist provenance (31):** not yet observed in game — filled from citable
Sidekick kit statements, one per spec: geomancy "it stays a self-reliant DPS
caster rather than any kind of support … Not a heal"; grovekeeper
"Grovekeeper is a dual-resource melee-healer" with a full healer dungeon loop
(Tears of the Earthmother on the tank / Spirit Charge / Seismic Wave / Sacred
Grove) — kit corroboration 21/60 abilities mention heal/absorb/shield (35%)
vs 1–9% on the other three specs; mountain-king "Solid main-tank for raid
bosses … Solid dungeon tank — AoE pulls and threat" (taunt: Gaze of
Theradras, threat passive: Heart of the Mountain); wildwalker "This is a DPS
spec, not a healer" (`resources/sidekick-primalist-*.md`, scraped
2026-08-07). Replace with an in-game read when one exists.

| 25 | Cultist | corruption | damage |
| 25 | Cultist | dreadnought | tank |
| 25 | Cultist | godblade | damage |
| 25 | Cultist | heretic | healing |

**Cultist provenance (25):** not yet observed in game — filled from citable
Sidekick kit statements, one per spec: corruption "this pure ranged caster's
only self-recovery is the slow Psychic Leech health drain: a trickle, not a
heal to fall back on"; dreadnought "Middling main-tank for raid bosses …
Solid dungeon tank — AoE pulls and threat" (sword-and-board, Insanity from
blocking, Horrifying Presence taunt); godblade "a Strength melee DPS whose
weapon strikes carry a Shadow-magic tail, not a healer or a caster"; heretic
"Strong raid/tank healer … Top-tier dungeon healer — spot-heals pull damage"
(Disc-style damage-that-heals loop)
(`resources/sidekick-cultist-*.md`, scraped 2026-08-07). Replace with an
in-game read when one exists.

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
