---
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


## 1. Interrupts

`effect_id 68` -- INTERRUPT_CAST. Verified against Pyromancer **Spellburn** and Runemaster **Ley Lock**.

| Class | Spec | Ability | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|
| Barbarian | ? | [Jawbreaker](https://db.exil.es/spell/802792) | 14s | 30 energy | Instant | Attempt to break an enemy's jaw, interrupting them and preventing any spell from that school from being cast for 4 seconds. |
| Barbarian | ? | [Wrist Snap](https://db.exil.es/spell/800383) | 15s | 10 energy | Instant | Snap an enemy's wrist with a powerful throwing axe, interrupting them and preventing any spell from that school from being cast for 4 sec. |
| Felsworn | ? | [Felbreak](https://db.exil.es/spell/800203) | 18s | 10 energy | 0.5s | Interrupt a spell from being cast, preventing the target from casting spells of that school for 3 seconds and draining mana from the target … |
| Witch Hunter | ? | [Guard Strike](https://db.exil.es/spell/804432) | 18s | 100 rage | Instant | Bash an enemy with your weapon's hilt, interrupting them and preventing any spell from that school of magic from being cast for 3 seconds. |
| Witch Hunter | ? | [Subjugate](https://db.exil.es/spell/500089) | 1.5 min | 8% mana | Instant | Silences an enemy and reduces their movement speed by 50% for 4 sec. |
| Stormbringer | ? | [Gust of Wind](https://db.exil.es/spell/500932) | 35s | 37% mana | Instant | Send forth a gust of wind in a frontal cone, knocking enemies back and interrupting all enemies current spell cast, preventing any spell fro… |
| Stormbringer | ? | [Mystic Thunder](https://db.exil.es/spell/504846) | 30s | 15% mana | Instant | Interrupt the target's current spell cast and then mark them for 5 seconds. If they cast again while marked they are silenced for 3 seconds. |
| Knight of Xoroth | ? | [Hellgaze](https://db.exil.es/spell/560471) | 15s | — | Instant | Interrupts spellcasting and prevents any spell from that school from being cast for 4 sec. |
| Guardian | ? | [Shield of Denial](https://db.exil.es/spell/704159) | 30s | 15 energy | Instant | Toss a shield at an enemy that bounces to up 2 nearby enemies, dealing 155 Physical damage and interrupting their spellcast, preventing any … |
| Bloodmage | ? | [Aneurysm](https://db.exil.es/spell/806099) | 24s | 10% health | Instant | Counter the enemy's spellcast, preventing any spell from that school of magic from being cast for 4 seconds. Successfully interrupting an en… |
| Ranger | ? | [Throatpunch](https://db.exil.es/spell/500617) | 12s | 25 focus | Instant\* | Punch an enemy in the throat, interrupting the enemy's spellcast, preventing any spell from that school of magic from being cast for 2 secon… |
| Chronomancer | ? | [Fray Magic](https://db.exil.es/spell/510236) | 30s | 27% mana | Instant | Stop your enemies' timeline, interrupting their spell cast for 4 sec. Successfully interrupting an enemy will additionally silence them for … |
| Necromancer | ? | [Heartchill](https://db.exil.es/spell/801739) | 30s | 19% mana | Instant | Chill an enemy's heart, interrupting their current spell cast. Successfully interrupting a spell also reduces their movement speed and haste… |
| Pyromancer | incineration | [Spellburn](https://db.exil.es/spell/800808) | 25s | 9% mana | Instant | Counters the enemy's spellcast, preventing any spell from that school of magic from being cast for 5 sec. |
| Cultist | ? | [Crushing Dissonance](https://db.exil.es/spell/804056) | 30s | 18% mana | Instant | Unleash a wave of maddening resonance, interrupting the current spell cast of all enemies around you and preventing any spell in that school… |
| Starcaller | ? | [Halt](https://db.exil.es/spell/805432) | 15s | 11% mana | Instant | Interrupt an enemy's current spellcast and prevents any spell in that school from being cast for 3 sec. |
| Sun Cleric | ? | [Solar Burn](https://db.exil.es/spell/500148) | 25s | 5% mana | Instant | Blasts an enemy with sun rays, interrupting spellcasting and preventing spells of that school from being cast for 4 sec. |
| Tinker | ? | [Distracto Shot](https://db.exil.es/spell/560470) | 25s | 4% mana | Instant | Interrupts spellcasting and prevents any spell from that school from being cast for 4 sec. Also silences for 3 sec. |
| Tinker | ? | [Meltdown](https://db.exil.es/spell/581313) | 30s | — | Instant | Bite an enemy, interrupting their current spellcast and preventing any spells from being cast from that school for 5 sec and reduces their F… |
| Venomancer | ? | [Nullifying Toxin](https://db.exil.es/spell/805096) | 16s | 9% mana | Instant | Inject an enemy with nullifying toxin, interrupting them and preventing any spell from that school from being cast for 3 sec. |
| Reaper | ? | [Ghastly Screech](https://db.exil.es/spell/806146) | 1.5 min | 200 runic power | Instant | Screech with ghastly intent, silencing all enemies within 8 yds for 4 seconds, and dealing 90 + 25% AP Shadowfrost Damage at the end of the … |
| Reaper | ? | [Siphon Essence](https://db.exil.es/spell/806125) | 20s | — | Instant | Attempt to drain an enemies vitals, leeching 22 + 31.03% AP health, interrupting casting and preventing any spell from that school from bein… |
| Primalist | ? | [Cave In](https://db.exil.es/spell/500615) | 24s | 18% mana | Instant | Cave in your target, interrupting spellcasting and preventing any spell in that school from being cast for 4 seconds. Successfully interrupt… |
| Runemaster | glyphic,engravement,riftblade | [Ley Lock](https://db.exil.es/spell/800995) | 6s | 16% mana | 0.5s | Interrupt your target's spellcasting, preventing any spell in that school from being cast for 2.5 sec. |

**24 across 19 classes.**
None found for: Templar, Witch Doctor.

## 1b. Stuns / silences that interrupt NPCs

NOT `effect_id 68`. These are stuns or silences whose tooltip says they interrupt **non-player** spellcasting -- which in a raid is an interrupt, since the target is always an NPC. Listed separately because the mechanic is different: they will not stop a player cast, and several have no cooldown of their own because a talent grants them. Effect-id classification alone reports Templar and Witch Doctor as having no interrupt; that is wrong in every practical raid sense.

| Class | Spec | Ability | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|
| Witch Doctor | ? | [Spirit Shock](https://db.exil.es/spell/807743) | 28s | 25% mana | Instant | Shock an enemy's spirit, silencing them for 4 seconds and interrupting non-player spellcasting for 4 seconds. |
| Stormbringer | ? | [Stormhammer](https://db.exil.es/spell/806599) | none | 6% mana | Instant | Stuns the target for 2 sec and interrupts non-player spellcasting for 3 sec. |
| Templar | ? | [Aggramar's Will](https://db.exil.es/spell/572573) | none | 3% mana | Instant | Stuns the target for 3 sec and interrupts non-player spellcasting for 3 sec. This spell cannot miss. |
| Templar | ? | [Divine Force](https://db.exil.es/spell/806153) | none | 15 energy | Instant | Leap at an enemy with divine force, stunning them for 6 seconds, dealing 25 + 100% SP + 55% AP Holy Damage, and interrupting non-player spel… |
| Cultist | ? | [Mass Nightmare](https://db.exil.es/spell/805114) | 3 min | 21% mana | Instant | Spread nightmares of the black empire to up to 5 nearby enemies, horrifying them for 5 seconds and interrupting non-player spellcasting for … |
| Tinker | ? | [Focused Impact](https://db.exil.es/spell/706688) | none | — | Instant | Stuns the target for 3 sec and interrupts non-player spellcasting for 3 sec. This spell cannot miss. |
| Primalist | ? | [Monolith Smash](https://db.exil.es/spell/991349) | none | 3% mana | 5s | Stuns an enemy for 3 sec and Interrupts non-player spellcasting for 3 sec. |

**7 across 6 classes.**
None found for: Barbarian, Bloodmage, Chronomancer, Felsworn, Guardian, Knight of Xoroth, Necromancer, Pyromancer, Ranger, Reaper, Runemaster, Starcaller, Sun Cleric, Venomancer, Witch Hunter.

## 2. Battle Rezzes

`effect_id 18` (RESURRECT) or `113` (RESURRECT_NEW). **Both are in use** -- Bloodmage **Vampyr Bite** is 18, Pyromancer **Phoenix Rebirth** is 113. Matching only 18 finds 2 spells and misses almost everything.

| Class | Spec | Ability | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|
| Witch Doctor | ? | [Reclaim Soul](https://db.exil.es/spell/801796) | none | 30% mana | 8s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Templar | ? | [Spiritual Ascension](https://db.exil.es/spell/500688) | 5 min | — | 2s | Call an ally's spirit back to their body, bringing them back to life. Usable while in combat. |
| Bloodmage | ? | [Vampyr Bite](https://db.exil.es/spell/801563) | none | — | 8s | Brings a dead player back to life with 70% health and mana. For the next 20 sec, the target takes 50% increased healing, but being damaged e… |
| Chronomancer | all | [Do Over](https://db.exil.es/spell/800669) | none | 36% mana | 8s | Restores a dead ally to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Chronomancer | time | [Resynchronize](https://db.exil.es/spell/804495) | 30 min | — | Instant | Switch to the timeline where your party didn't die, returning all party members to life with 583 health and 833 mana. Can be cast while dead… |
| Necromancer | ? | [Call of The Scourge](https://db.exil.es/spell/801792) | 10 min | 68% mana | 2s | Bring a dead ally back to life with 70 health and 135 mana. Can be used in combat. |
| Necromancer | ? | [Reanimate](https://db.exil.es/spell/804172) | 3 min | 250 runic power | Instant | Revives the corpse of a non-elite Undead or Humanoid, binding it to your control for up to 10 sec. While controlled, the target will decay o… |
| Pyromancer | flameweaving | [Phoenix Rebirth](https://db.exil.es/spell/706867) | none | 60% mana | 10s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Pyromancer | flameweaving | [Reborn from Ash](https://db.exil.es/spell/804231) | 10 min | — | 2s | Returns a dead ally to life with 400 health and 635 mana, can also be used on self while dead. Can be used in combat. |
| Cultist | ? | [Ritual of Awakening](https://db.exil.es/spell/801791) | none | 60% mana | 8s | Brings a dead player back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Starcaller | ? | [Celestial Awakening](https://db.exil.es/spell/801795) | none | 60% mana | 8s | Brings a dead ally back to life with 70 Health and 135 Mana. The target gains 200% increased Mana regeneration for 10 sec. Cannot be cast wh… |
| Starcaller | ? | [Tidal Rebirth](https://db.exil.es/spell/801793) | 10 min | 75% mana | 2s | Instantly brings a dead ally back to life with 400 health and 635 mana. This spell is usable in combat. |
| Sun Cleric | ? | [Revivify](https://db.exil.es/spell/801790) | none | 60% mana | 8s | Brings a dead ally back to life with 70 health and 135 mana. Not usable in combat. |
| Sun Cleric | ? | [Val'kyr Ressurrection](https://db.exil.es/spell/804608) | none | — | 5s | Brings a dead player back to life with 2000 health and 833 mana. Cannot be cast when in combat. |
| Tinker | ? | [Defibrillate](https://db.exil.es/spell/802175) | none | 20% mana | 10s | Brings up to 5 dead allies within 15 yds back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Venomancer | ? | [Prayer Beads](https://db.exil.es/spell/520681) | none | 60% mana | 8s | Pray to Shadra and honor the venomcult, allowing you to bring a dead ally back to life with 70 health and 135 mana. Cannot be cast when in c… |
| Venomancer | ? | [Spawn](https://db.exil.es/spell/805568) | 10 min | 20% mana | 2s | Bring a dead ally back to life with 400 health and 635 mana. Can be used in combat. Not usable in arena. |
| Primalist | ? | [Return to Life](https://db.exil.es/spell/801794) | none | 60% mana | 10s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |

**18 across 12 classes.**
None found for: Barbarian, Felsworn, Guardian, Knight of Xoroth, Ranger, Reaper, Runemaster, Stormbringer, Witch Hunter.

## 3. Purges

`effect_id 38` (DISPEL) where the tooltip names a *beneficial* effect on an *enemy*. Target flags alone are unreliable -- **Show of Force** is `target_a 6` and reads "on a friendly target".

| Class | Spec | Ability | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|
| Templar | ? | [Righteous Reprimand](https://db.exil.es/spell/572308) | 10s | 6% mana | Instant | Removes 1 beneficial magic effect from an enemy. |
| Chronomancer | time | [Continuum Restoration](https://db.exil.es/spell/801271) | 1.5 min | 60% mana | 1.5s | Restore the continuum at target location for all allies and enemies within 15 yds, removing all beneficial magic effects from enemies and ha… |
| Cultist | ? | [Netherstrike](https://db.exil.es/spell/806222) | none | 10% mana | Instant | Generates 10 Insanity Strike an enemy quickly for 125% Weapon Damage plus 40 Shadow Damage, purging 1 beneficial magic effect from them. Onl… |
| Sun Cleric | ? | [Gavel of Wrath](https://db.exil.es/spell/800617) | none | 10% mana | Instant | Smash an enemy for 100% Weapon Damage plus 45 and dispel 1 beneficial magic effect from them. Shares a cooldown with other Gavels. |
| Reaper | ? | [Reap Magic](https://db.exil.es/spell/704258) | none | — | Instant | Steals 1 beneficial Magic Effect from an enemy. If you successfuly steal an effect, you also siphon 160 Health from the target as Shadow Dam… |
| Reaper | ? | [Soul Shear](https://db.exil.es/spell/520862) | 16s | — | Instant | Purge an enemy's soul, removing 2 beneficial magic effects from them. |
| Primalist | ? | [Neutralizing Touch](https://db.exil.es/spell/572307) | 10s | — | Instant | Removes 1 beneficial magic effect from an enemy. |
| Runemaster | engravement | [Resonance Rune](https://db.exil.es/spell/803679) | 1 min | 30% mana | 1.5s | Place an arcane rune on the ground that dispels 3 harmful magic effects from allies in the radius, and purges 3 beneficial magic effects fro… |

**8 across 7 classes.**
None found for: Barbarian, Bloodmage, Felsworn, Guardian, Knight of Xoroth, Necromancer, Pyromancer, Ranger, Starcaller, Stormbringer, Tinker, Venomancer, Witch Doctor, Witch Hunter.

## 4. Spellsteals

`effect_id 126` -- STEAL_BENEFICIAL_BUFF.

| Class | Spec | Ability | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|
| Felsworn | ? | [Consume Magic](https://db.exil.es/spell/800353) | none | 30 energy | Instant | Steal 1 beneficial magic effects from an enemy. If you successfully steal an effect, you deal 8 Shadow Damage to the enemy. |
| Bloodmage | ? | [Siphon](https://db.exil.es/spell/803327) | 6s | — | Instant | Steal 2 beneficial magic effects from an enemy. |
| Runemaster | ? | [Fragmented](https://db.exil.es/spell/712338) | none | — | Instant | Fire Sigil now grants an additional effect to the next use of the following abilities: Fragmentation: Dispels and steals 1 beneficial magic … |
| Runemaster | all | [Leyfeed](https://db.exil.es/spell/520269) | none | 20% mana | 1s | Feed off the latent magic of an enemy, stealing 2 beneficial magic effects from them. Usable while moving. |

**4 across 3 classes.**
None found for: Barbarian, Chronomancer, Cultist, Guardian, Knight of Xoroth, Necromancer, Primalist, Pyromancer, Ranger, Reaper, Starcaller, Stormbringer, Sun Cleric, Templar, Tinker, Venomancer, Witch Doctor, Witch Hunter.

## 5. Tranq Shots / Soothes (remove enrage)

`effect_id 38` with `misc_value 9` -- dispel type Enrage.

| Class | Spec | Ability | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|
| Witch Hunter | ? | [Purge Evil](https://db.exil.es/spell/572306) | 20s | 25% mana | Instant | Purge the evil from an enemy, removing all enrage effects from them. |
| Witch Hunter | ? | [Sedative Shot](https://db.exil.es/spell/572406) | none | 35 focus | Instant\* | Shoot an arrow at an enemy with sedative toxins, dealing 50% Ranged Weapon Damage as Nature Damage and removing 1 enrage effect from them. |
| Stormbringer | ? | [Calm the Storm](https://db.exil.es/spell/572303) | none | Depletes 10 | Instant | Depletes 10 Static Calm an enemy, removing 1 enrage effect from them. |
| Venomancer | ? | [Myotoxin](https://db.exil.es/spell/572304) | 10s | 10% mana | Instant | Inject an enemy with myotoxins, removing 1 enrage effect, repeating every 4 sec for 20 sec. |

**4 across 3 classes.**
None found for: Barbarian, Bloodmage, Chronomancer, Cultist, Felsworn, Guardian, Knight of Xoroth, Necromancer, Primalist, Pyromancer, Ranger, Reaper, Runemaster, Starcaller, Sun Cleric, Templar, Tinker, Witch Doctor.

---

## How these were classified

**Primarily by SPELL EFFECT ID, with the tooltip as a second pass.** Neither
source is sufficient alone, and both failure modes were hit while building
this file.

*Text alone under-reports.* Ascension Sidekick's kit data does not contain
Chronomancer's `Fray Magic` at all, so every candidate list derived from its
descriptions silently omits a real 30 sec interrupt.

*Effect ids alone under-report too.* Table 1b is the proof: seven abilities
interrupt non-player casting through a stun or silence and carry no `effect_id
68`. Classifying purely on 68 reports **Templar and Witch Doctor as having no
interrupt**, which is wrong in every practical raid sense.

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

