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

| 29 | Venomancer | fortitude | tank |
| 29 | Venomancer | rot | damage |
| 29 | Venomancer | stalking | damage |
| 29 | Venomancer | vizier | healing |

**Venomancer provenance (29):** not yet observed in game — filled from citable
Sidekick kit statements, one per spec: fortitude "Closest to Brewmaster
Monk… Both use a stance/form gimmick, Beetle Form here" with a taunt (Vile
Sting: "Taunts an enemy target to attack you") and "built to be extremely
hard to burst down rather than to top DPS charts" — and "Every spec-line heal
points at yourself… You cannot keep a duo partner up", so tank, not healer;
rot "This is a pure ranged damage spec. Its support is a group spell-haste
aura… not any ally healing" (its Serpent's Fang splash is "modest
off-healing rather than a healer's engine"); stalking "Stalking is a pure DPS
spec with no group buff… You are pressure and execute, not a leech-tank";
vizier "Vizier does what any pure healer does: keeps a frontline ally, or
itself, alive" / "Vizier is a pure mana healer built around Shadra's Prayer"
(`resources/sidekick-venomancer-*.md`, scraped 2026-08-07). Kit
corroboration: vizier 11/27 abilities mention heal/absorb/shield (41%) vs
fortitude 19% (self-heals), rot 28% (Serpent's Fang line), stalking 10% —
muted vs the usual 5x because rot's kit genuinely heals as a side effect.
Replace with an in-game read when one exists.

| 20 | Bloodmage | sanguine | damage |
| 20 | Bloodmage | accursed | damage |
| 20 | Bloodmage | eternal | tank |
| 20 | Bloodmage | fleshweaver | healing |

**Bloodmage provenance (20):** not yet observed in game — filled from citable
Sidekick kit statements, one per spec: sanguine "Strong sustained
single-target DPS on patchwork fights … Not a party healer. … the spec
carries itself and nobody else"; accursed "damage dealer" blurbs on every PvE
row, "Not a party healer. … Spot patches only"; eternal "a shapeshifting
bruiser/tank that lives in two stances" with a real tank kit (Blood Howl AoE
taunt, Bare Fangs taunt, Eternal Curse threat/armor/Stamina stance,
Defense-to-crit-immunity stat floor); fleshweaver — the dungeon text is a
full healer loop ("Sanguine Mend as your primary tank/spot heal … Blood Veil
on the tank before a big hit, Fleshcraft as the true 'oh crap' button")
(`resources/sidekick-bloodmage-*.md`, scraped 2026-08-07). ⚠️ The
heal-mention count is NOT the discriminator here: sanguine 21/67 (31%),
accursed 16/65 (25%), eternal 10/51 (20%), fleshweaver 16/31 (52%) — the
whole class self-heals by lifesteal, so every spec scores high. The
discriminator is ALLY-targeted healing, which three spec pages explicitly
deny ("You have no ally-targeted heals" — sanguine dungeon text; "no
ally-targeted heal" — eternal; "Not a party healer" — accursed) and
fleshweaver's entire rotation is built on. Replace with an in-game read when
one exists.

| 27 | Sun Cleric | blessings | healing |
| 27 | Sun Cleric | piety | damage |
| 27 | Sun Cleric | seraphim | tank |
| 27 | Sun Cleric | valkyrie | damage |

**Sun Cleric provenance (27):** not yet observed in game — filled from citable
Sidekick kit statements, one per spec: blessings "Strong in arena as a healer …
Solid dungeon healer — spot-heals pull damage", "Closest to Holy Paladin, with
a strong side-order of Discipline Priest" — kit corroboration 36/55 spec
abilities mention heal/absorb/shield (65%) vs 5–15 on the other three specs;
piety "Solid in arena as a damage dealer … no heal button in the spec line
itself", "Closest to Balance Druid, with a Fire-Mage flavor"; seraphim "You
fight in melee as a Strength/Stamina block tank with a one-hand weapon and
shield" (taunt: Injunction 800624, threat passive: Sol Invictus, block chassis:
Seraphic Bulwark/Blessed One/Dawnguard); valkyrie "Middling in arena as a
damage dealer … The spec line has no direct in-combat heal spell", Ret/WW
melee hybrid (`resources/sidekick-sun-cleric-*.md`, scraped 2026-08-07).
Replace with an in-game read when one exists.


| 26 | Starcaller | moon-guard | tank |
| 26 | Starcaller | moon-priest | healing |
| 26 | Starcaller | sentinel | damage |
| 26 | Starcaller | warden | damage |

**Starcaller provenance (26):** not yet observed in game — filled from
citable Sidekick kit statements, one per spec: moon-guard "Solid main-tank
for raid bosses … Strong dungeon tank — AoE pulls and threat" (block/parry
kit: Chosen of the Moon taunt + physical DR, Command taunt, Moonlit Bulwark,
Blanket of Stars, threat passive Lunar Authority); moon-priest "Solid
raid/tank healer … Strong dungeon healer — spot-heals pull damage" (Resto
Shaman/Disc feel; heals priced as % max mana: Hand of Elune, Moonflow,
Prayer of Elune, Moonwell); sentinel "reads as a damage spec whose output
occasionally heals rather than a primary healer" (ranged arcane, plant-and-
cast); warden "You're a self-sufficient hybrid, not anyone's healer …
Havoc Demon Hunter feel" (melee glaive DPS)
(`resources/sidekick-starcaller-*.md`, scraped 2026-08-08). Replace with an
in-game read when one exists.

| 19 | Templar | zealot | damage |
| 19 | Templar | oathkeeper | tank |
| 19 | Templar | crusader | damage |

**Templar provenance (19):** not yet observed in game — filled from citable
Sidekick kit statements, one per spec: zealot "Solid sustained single-target
DPS on patchwork fights … Middling in arena as a damage dealer" (its only
group-heal shape, Chakra of Light, is an optional 0/2 support pick the page
itself calls a choice, "identical rotation, pointed at healing"); oathkeeper
"Strong main-tank for raid bosses … Strong dungeon tank — AoE pulls and
threat" (Absolution AoE taunt, Beckon single taunt, Divine Stand threat
passive, Keeping the Oath stagger — and the 08/06 changelog buffs Divine
Stand threat, which is a tank statement from the devs) — its Benediction ally
heal is a tank's reactive sustain, not healer throughput, and heal-mention
corroboration (14/70, 20%) sits well under the ~33% healer band; crusader
"Top-tier sustained single-target DPS on patchwork fights … Strong in arena
as a damage dealer" ("The healing is incidental self-heal off Argent Blade
and Titanstrike, not throughput, and it cannot cover a group")
(`resources/sidekick-templar-*.md`, scraped 2026-08-08). Replace with an
in-game read when one exists.

| 18 | Guardian | vanguard | tank |
| 18 | Guardian | inspiration | damage |
| 18 | Guardian | gladiator | damage |

**Guardian provenance (18):** not yet observed in game — filled from citable
Sidekick kit statements, one per spec: vanguard "Middling main-tank for raid
bosses … Strong dungeon tank — AoE pulls and threat" (Closest to Protection
Warrior; taunts: Challenging Cry, Shield Challenge; High Threat abilities;
stat priority "Defense (to crit-immunity)"); inspiration "Closest to
Augmentation Evoker … a buff and mitigation unit wearing a shield, not a
direct-heal caster … No hard single-target heal" (a support buffer, still
`damage` in this three-role vocabulary); gladiator "a DPS-Prot hybrid …
Solid in arena as a damage dealer", no taunt in the rotation text and
"self-healing is thin" (`resources/sidekick-guardian-*.md`, scraped
2026-08-08). Kit corroboration: heal/absorb mentions inspiration 9/74 (12%),
vanguard 2/56 (4%), gladiator 2/49 (4%) — no spec near the 33–35% healer
band. Zero "absorb" mentions class-wide: Guardian's defensive economy is
BLOCK, not absorbs. Replace with an in-game read when one exists.

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
| 26 | Starcaller moon-guard | 4 / 64 (6%) |
| 26 | Starcaller moon-priest | **30 / 72 (42%)** |
| 26 | Starcaller sentinel | 4 / 52 (8%) |
| 26 | Starcaller warden | 0 / 19 (0%) |

The healer stands out by roughly 5x. That is a strong enough signal to *flag* a
spec for a look, and nowhere near strong enough to set this table from — the
same rule that keeps Sidekick mention counts out of the Specs column. Fill a
row by playing the spec.
