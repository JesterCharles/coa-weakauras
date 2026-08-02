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


## 1. Interrupts

`effect_id 68` -- INTERRUPT_CAST. Verified against Pyromancer **Spellburn** and Runemaster **Ley Lock**.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | all (tree) | [Jawbreaker](https://db.exil.es/spell/802792) |  | 14s | 30 energy | Instant | Attempt to break an enemy's jaw, interrupting them and preventing any spell from that school from being cast for 4 seconds. |
| Felsworn | Infernal | [Felbreak](https://db.exil.es/spell/800203) |  | 18s | 10 energy | 0.5s | Interrupt a spell from being cast, preventing the target from casting spells of that school for 3 seconds and draining mana from the target … |
| Witch Hunter | all | [Subjugate](https://db.exil.es/spell/500089) |  | 1.5 min | 8% mana | Instant | Silences an enemy and reduces their movement speed by 50% for 4 sec. |
| Witch Hunter | WitchKnight | [Guard Strike](https://db.exil.es/spell/804432) |  | 18s | 100 rage | Instant | Bash an enemy with your weapon's hilt, interrupting them and preventing any spell from that school of magic from being cast for 3 seconds. |
| Stormbringer | all | [Gust of Wind](https://db.exil.es/spell/500932) |  | 35s | 37% mana | Instant | Send forth a gust of wind in a frontal cone, knocking enemies back and interrupting all enemies current spell cast, preventing any spell fro… |
| Stormbringer | Maelstrom | [Mystic Thunder](https://db.exil.es/spell/504846) |  | 30s | 15% mana | Instant | Interrupt the target's current spell cast and then mark them for 5 seconds. If they cast again while marked they are silenced for 3 seconds. |
| Knight of Xoroth | all | [Hellgaze](https://db.exil.es/spell/560471) |  | 15s | — | Instant | Interrupts spellcasting and prevents any spell from that school from being cast for 4 sec. |
| Guardian | all | [Shield of Denial](https://db.exil.es/spell/704159) |  | 30s | 15 energy | Instant | Toss a shield at an enemy that bounces to up 2 nearby enemies, dealing 155 Physical damage and interrupting their spellcast, preventing any … |
| Bloodmage | Sanguine | [Aneurysm](https://db.exil.es/spell/806099) |  | 24s | 10% health | Instant | Counter the enemy's spellcast, preventing any spell from that school of magic from being cast for 4 seconds. Successfully interrupting an en… |
| Ranger | Brigand | [Throatpunch](https://db.exil.es/spell/500617) |  | 12s | 25 focus | Instant\* | Punch an enemy in the throat, interrupting the enemy's spellcast, preventing any spell from that school of magic from being cast for 2 secon… |
| Chronomancer | all | [Fray Magic](https://db.exil.es/spell/510236) |  | 30s | 27% mana | Instant | Stop your enemies' timeline, interrupting their spell cast for 4 sec. Successfully interrupting an enemy will additionally silence them for … |
| Necromancer | Rime | [Heartchill](https://db.exil.es/spell/801739) |  | 30s | 19% mana | Instant | Chill an enemy's heart, interrupting their current spell cast. Successfully interrupting a spell also reduces their movement speed and haste… |
| Pyromancer | incineration | [Spellburn](https://db.exil.es/spell/800808) |  | 25s | 9% mana | Instant | Counters the enemy's spellcast, preventing any spell from that school of magic from being cast for 5 sec. |
| Cultist | Dreadnought | [Crushing Dissonance](https://db.exil.es/spell/804056) |  | 30s | 18% mana | Instant | Unleash a wave of maddening resonance, interrupting the current spell cast of all enemies around you and preventing any spell in that school… |
| Starcaller | all | [Halt](https://db.exil.es/spell/805432) |  | 15s | 11% mana | Instant | Interrupt an enemy's current spellcast and prevents any spell in that school from being cast for 3 sec. |
| Sun Cleric | all | [Solar Burn](https://db.exil.es/spell/500148) |  | 25s | 5% mana | Instant | Blasts an enemy with sun rays, interrupting spellcasting and preventing spells of that school from being cast for 4 sec. |
| Tinker | all | [Distracto Shot](https://db.exil.es/spell/560470) |  | 25s | 4% mana | Instant | Interrupts spellcasting and prevents any spell from that school from being cast for 4 sec. Also silences for 3 sec. |
| Tinker | all | [Meltdown](https://db.exil.es/spell/581313) |  | 30s | — | Instant | Bite an enemy, interrupting their current spellcast and preventing any spells from being cast from that school for 5 sec and reduces their F… |
| Venomancer | all | [Nullifying Toxin](https://db.exil.es/spell/805096) |  | 16s | 9% mana | Instant | Inject an enemy with nullifying toxin, interrupting them and preventing any spell from that school from being cast for 3 sec. |
| Reaper | Harvest | [Siphon Essence](https://db.exil.es/spell/806125) |  | 20s | — | Instant | Attempt to drain an enemies vitals, leeching 22 + 31.03% AP health, interrupting casting and preventing any spell from that school from bein… |
| Reaper | all (tree) | [Ghastly Screech](https://db.exil.es/spell/806146) |  | 1.5 min | 200 runic power | Instant | Screech with ghastly intent, silencing all enemies within 8 yds for 4 seconds, and dealing 90 + 25% AP Shadowfrost Damage at the end of the … |
| Primalist | Geomancy | [Cave In](https://db.exil.es/spell/500615) |  | 24s | 18% mana | Instant | Cave in your target, interrupting spellcasting and preventing any spell in that school from being cast for 4 seconds. Successfully interrupt… |
| Runemaster | glyphic,engravement,riftblade | [Ley Lock](https://db.exil.es/spell/800995) |  | 6s | 16% mana | 0.5s | Interrupt your target's spellcasting, preventing any spell in that school from being cast for 2.5 sec. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | all (tree) | [Jawbreaker](https://db.exil.es/spell/802792) |  | 14s | 30 energy | Instant | Attempt to break an enemy's jaw, interrupting them and preventing any spell from that school from being cast for 4 seconds. |
| Felsworn | Infernal | [Felbreak](https://db.exil.es/spell/800203) |  | 18s | 10 energy | 0.5s | Interrupt a spell from being cast, preventing the target from casting spells of that school for 3 seconds and draining mana from the target … |
| Witch Hunter | all | [Subjugate](https://db.exil.es/spell/500089) |  | 1.5 min | 8% mana | Instant | Silences an enemy and reduces their movement speed by 50% for 4 sec. |
| Witch Hunter | WitchKnight | [Guard Strike](https://db.exil.es/spell/804432) |  | 18s | 100 rage | Instant | Bash an enemy with your weapon's hilt, interrupting them and preventing any spell from that school of magic from being cast for 3 seconds. |
| Stormbringer | all | [Gust of Wind](https://db.exil.es/spell/500932) |  | 35s | 37% mana | Instant | Send forth a gust of wind in a frontal cone, knocking enemies back and interrupting all enemies current spell cast, preventing any spell fro… |
| Stormbringer | Maelstrom | [Mystic Thunder](https://db.exil.es/spell/504846) |  | 30s | 15% mana | Instant | Interrupt the target's current spell cast and then mark them for 5 seconds. If they cast again while marked they are silenced for 3 seconds. |
| Knight of Xoroth | all | [Hellgaze](https://db.exil.es/spell/560471) |  | 15s | — | Instant | Interrupts spellcasting and prevents any spell from that school from being cast for 4 sec. |
| Guardian | all | [Shield of Denial](https://db.exil.es/spell/704159) |  | 30s | 15 energy | Instant | Toss a shield at an enemy that bounces to up 2 nearby enemies, dealing 155 Physical damage and interrupting their spellcast, preventing any … |
| Bloodmage | Sanguine | [Aneurysm](https://db.exil.es/spell/806099) |  | 24s | 10% health | Instant | Counter the enemy's spellcast, preventing any spell from that school of magic from being cast for 4 seconds. Successfully interrupting an en… |
| Ranger | Brigand | [Throatpunch](https://db.exil.es/spell/500617) |  | 12s | 25 focus | Instant\* | Punch an enemy in the throat, interrupting the enemy's spellcast, preventing any spell from that school of magic from being cast for 2 secon… |
| Chronomancer | all | [Fray Magic](https://db.exil.es/spell/510236) |  | 30s | 27% mana | Instant | Stop your enemies' timeline, interrupting their spell cast for 4 sec. Successfully interrupting an enemy will additionally silence them for … |
| Necromancer | Rime | [Heartchill](https://db.exil.es/spell/801739) |  | 30s | 19% mana | Instant | Chill an enemy's heart, interrupting their current spell cast. Successfully interrupting a spell also reduces their movement speed and haste… |
| Pyromancer | incineration | [Spellburn](https://db.exil.es/spell/800808) |  | 25s | 9% mana | Instant | Counters the enemy's spellcast, preventing any spell from that school of magic from being cast for 5 sec. |
| Cultist | Dreadnought | [Crushing Dissonance](https://db.exil.es/spell/804056) |  | 30s | 18% mana | Instant | Unleash a wave of maddening resonance, interrupting the current spell cast of all enemies around you and preventing any spell in that school… |
| Starcaller | all | [Halt](https://db.exil.es/spell/805432) |  | 15s | 11% mana | Instant | Interrupt an enemy's current spellcast and prevents any spell in that school from being cast for 3 sec. |
| Sun Cleric | all | [Solar Burn](https://db.exil.es/spell/500148) |  | 25s | 5% mana | Instant | Blasts an enemy with sun rays, interrupting spellcasting and preventing spells of that school from being cast for 4 sec. |
| Tinker | all | [Distracto Shot](https://db.exil.es/spell/560470) |  | 25s | 4% mana | Instant | Interrupts spellcasting and prevents any spell from that school from being cast for 4 sec. Also silences for 3 sec. |
| Tinker | all | [Meltdown](https://db.exil.es/spell/581313) |  | 30s | — | Instant | Bite an enemy, interrupting their current spellcast and preventing any spells from being cast from that school for 5 sec and reduces their F… |
| Venomancer | all | [Nullifying Toxin](https://db.exil.es/spell/805096) |  | 16s | 9% mana | Instant | Inject an enemy with nullifying toxin, interrupting them and preventing any spell from that school from being cast for 3 sec. |
| Reaper | Harvest | [Siphon Essence](https://db.exil.es/spell/806125) |  | 20s | — | Instant | Attempt to drain an enemies vitals, leeching 22 + 31.03% AP health, interrupting casting and preventing any spell from that school from bein… |
| Reaper | all (tree) | [Ghastly Screech](https://db.exil.es/spell/806146) |  | 1.5 min | 200 runic power | Instant | Screech with ghastly intent, silencing all enemies within 8 yds for 4 seconds, and dealing 90 + 25% AP Shadowfrost Damage at the end of the … |
| Primalist | Geomancy | [Cave In](https://db.exil.es/spell/500615) |  | 24s | 18% mana | Instant | Cave in your target, interrupting spellcasting and preventing any spell in that school from being cast for 4 seconds. Successfully interrupt… |
| Runemaster | glyphic,engravement,riftblade | [Ley Lock](https://db.exil.es/spell/800995) |  | 6s | 16% mana | 0.5s | Interrupt your target's spellcasting, preventing any spell in that school from being cast for 2.5 sec. |
```

</details>

**23 across 19 classes.**
None found for: Templar, Witch Doctor.

## 2. Silences

`mechanic 9` (SILENCE). A silence stops the NEXT cast and locks casting for a duration. Several also state that they interrupt non-player spellcasting, which makes them the best interrupt substitute available -- those are marked **(int)**. Only rows with a cost or a cooldown are listed; a silence with neither is a component or a talent.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | Shadowhunting | [Spirit Shock](https://db.exil.es/spell/807743) **(int)** |  | 28s | 25% mana | Instant | Shock an enemy's spirit, silencing them for 4 seconds and interrupting non-player spellcasting for 4 seconds. |
| Knight of Xoroth | all (tree) | [Chainwhip](https://db.exil.es/spell/800081) |  | 20s | 100 rage | Instant | Swing a chain at an enemy dealing 12 + 35% AP Physical Damage and silencing them for 2 seconds, generating a large amount of threat. If you … |
| Guardian | Vanguard | [Hammer of the Law](https://db.exil.es/spell/704418) |  | none | 40 energy | Instant | Smash an enemy and enemies behind them in a line, dealing 95 + 100% AP High Threat Physical Damage and silencing them for 3.5 seconds. |
| Templar | all (tree) | [Interdict](https://db.exil.es/spell/560116) |  | 2 min | — | Instant | Forbid an enemy from sinning, silencing them for 5 seconds. If they are an Undead or Demon they are unable to be healed for the duration. |
| Templar | all | [Atone for your Sins!](https://db.exil.es/spell/561309) ⚠ |  | 2 min | 10 energy | Instant | Forbid an enemy from sinning, silencing them for 6 sec. If they are an Undead or Demon they are unable to be healed. |
| Bloodmage | Fleshweaver | [Arterial Bind](https://db.exil.es/spell/681077) |  | 1.5 min | 15% health | Instant | Place a pool of blood on the ground beneath enemies and allies, healing allies for 203 + 33% healing every 1 sec and silencing all enemies f… |
| Tinker | all | [Anti-Magic Grenades](https://db.exil.es/spell/804861) |  | 2 min | 10% mana | Instant | Toss grenades that dispel up to 3 benefical magic effects and silences all enemies within 12 yds for 4 sec. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | Shadowhunting | [Spirit Shock](https://db.exil.es/spell/807743) **(int)** |  | 28s | 25% mana | Instant | Shock an enemy's spirit, silencing them for 4 seconds and interrupting non-player spellcasting for 4 seconds. |
| Knight of Xoroth | all (tree) | [Chainwhip](https://db.exil.es/spell/800081) |  | 20s | 100 rage | Instant | Swing a chain at an enemy dealing 12 + 35% AP Physical Damage and silencing them for 2 seconds, generating a large amount of threat. If you … |
| Guardian | Vanguard | [Hammer of the Law](https://db.exil.es/spell/704418) |  | none | 40 energy | Instant | Smash an enemy and enemies behind them in a line, dealing 95 + 100% AP High Threat Physical Damage and silencing them for 3.5 seconds. |
| Templar | all (tree) | [Interdict](https://db.exil.es/spell/560116) |  | 2 min | — | Instant | Forbid an enemy from sinning, silencing them for 5 seconds. If they are an Undead or Demon they are unable to be healed for the duration. |
| Templar | all | [Atone for your Sins!](https://db.exil.es/spell/561309) ⚠ |  | 2 min | 10 energy | Instant | Forbid an enemy from sinning, silencing them for 6 sec. If they are an Undead or Demon they are unable to be healed. |
| Bloodmage | Fleshweaver | [Arterial Bind](https://db.exil.es/spell/681077) |  | 1.5 min | 15% health | Instant | Place a pool of blood on the ground beneath enemies and allies, healing allies for 203 + 33% healing every 1 sec and silencing all enemies f… |
| Tinker | all | [Anti-Magic Grenades](https://db.exil.es/spell/804861) |  | 2 min | 10% mana | Instant | Toss grenades that dispel up to 3 benefical magic effects and silences all enemies within 12 yds for 4 sec. |
```

</details>

**7 across 6 classes.**
None found for: Barbarian, Chronomancer, Cultist, Felsworn, Necromancer, Primalist, Pyromancer, Ranger, Reaper, Runemaster, Starcaller, Stormbringer, Sun Cleric, Venomancer, Witch Hunter.

## 3. Stuns

`mechanic 12` (STUN). **A stun is not an interrupt.** Most raid bosses are stun-immune, so treat these as trash and add tools, not as a cast-stopping plan. Several carry an "interrupts non-player spellcasting" clause and are marked **(int)** -- that clause is worth exactly as much as the stun landing, which on a boss is usually nothing.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | all | [Headbutt](https://db.exil.es/spell/520523) |  | 40s | 20% energy | Instant | Savagely headbutt an enemy, dealing 48 Physical damage, knocking them down briefly and stunning them for 4 sec. |
| Witch Hunter | Inquisition | [Darkslayer's Lantern](https://db.exil.es/spell/802139) |  | 2 min | 30% mana | Instant | Empower a lantern with your Flames of Sin and let it shine, dealing 441 + 15% AP Fire Damage and stunning all enemies within 5 yds for 5 sec… |
| Knight of Xoroth | all (tree) | [Chains of Malice](https://db.exil.es/spell/803185) |  | 1.5 min | — | Instant | Lock an enemy down with magical chains, stunning them and dragging them with you for 5 seconds. Every 1 sec, the enemy will suffer 48 Physic… |
| Guardian | all | [Battle Rush](https://db.exil.es/spell/802197) |  | 30s | — | Instant | Charge an enemy, dealing 21.714 Physical damage and stunning them for 1 sec. |
| Bloodmage | all | [Shadow Missile](https://db.exil.es/spell/536273) |  | 24s | — | Instant | Sends a shadowy bolt at the enemy, causing 65 to 66 Shadow damage and stunning them for 3 sec. |
| Bloodmage | all | [Pursuit](https://db.exil.es/spell/802869) ⚠ |  | 1.5 min | — | Instant | Requires Cursed Form Appear behind an enemy, dealing 411 Physical Damage, stunning the target for 4 sec, and reducing all damage taken by 20… |
| Ranger | all | [Eternal Knockdown](https://db.exil.es/spell/520758) |  | 25s | — | Instant | Knock an enemy down, dealing 48 Physical Damage and stunning them for 168 hour. For the duration, enemies take 0% increased damage from Assa… |
| Ranger | all | [Bushwhack](https://db.exil.es/spell/557333) ⚠ |  | none | 60 focus | Instant | Appear behind your target from the shadows, stunning them for 4 sec. |
| Cultist | all | [Facehug](https://db.exil.es/spell/800013) |  | 1.5 min | — | Channel 3s | The Mindbender teleports to an enemy and channels on them for up to 3 sec, Stunning the target for the duration. |
| Sun Cleric | all (tree) | [Glare](https://db.exil.es/spell/805583) |  | none | 20% mana | 1.5s | Flash powerful light that deals 168 + 27.41% SP Holy Damage and stuns enemies within 8 yds for 5 seconds. |
| Tinker | all | [Vanguard X-173: Onslaught](https://db.exil.es/spell/801828) |  | 20s | 30 energy | Instant | Causes 216 to 219 Physical Damage to enemies in a 15yd frontal cone and stunning enemies hit for 3 sec. |
| Tinker | all | [Drill Smash](https://db.exil.es/spell/806173) |  | 30s | — | Instant | Repeatedly drill into an enemy, dealing 125 Physical Damage, repeating every 1 sec and stunning them for 4 sec. |
| Venomancer | all | [Poison Eruption](https://db.exil.es/spell/520232) ⚠ |  | 2 min | 8% mana | Instant | Requires Scorpid Form Erupt in a poisonous frenzy, leeching 185 health and stunning enemies within 8 yds for 5 sec. |
| Primalist | Mountain King | [Mountain Hammer](https://db.exil.es/spell/681130) |  | none | 200 rage | Instant | Throw a hammer at an enemy dealing 67 + 35.5% nature SP + 15.5% AP Physical Damage and stunning them for 5 seconds. |
| Primalist | all | [Monolith Smash](https://db.exil.es/spell/991349) **(int)** |  | none | 3% mana | 5s | Stuns an enemy for 3 sec and Interrupts non-player spellcasting for 3 sec. |
| Runemaster | riftblade | [Ice Rune](https://db.exil.es/spell/524930) |  | 1 min | 12% mana | Instant | Requires Frozen Target Unleash a frost rune at an enemy, stunning them for 4 sec. Affected enemies are considered Frozen. |
| Runemaster | all | [Everfrost Scroll](https://db.exil.es/spell/801090) |  | none | 5% mana | Instant | Stun an enemy target for 3.5 sec, increasing Frost damage they take from you by 20% for the duration. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | all | [Headbutt](https://db.exil.es/spell/520523) |  | 40s | 20% energy | Instant | Savagely headbutt an enemy, dealing 48 Physical damage, knocking them down briefly and stunning them for 4 sec. |
| Witch Hunter | Inquisition | [Darkslayer's Lantern](https://db.exil.es/spell/802139) |  | 2 min | 30% mana | Instant | Empower a lantern with your Flames of Sin and let it shine, dealing 441 + 15% AP Fire Damage and stunning all enemies within 5 yds for 5 sec… |
| Knight of Xoroth | all (tree) | [Chains of Malice](https://db.exil.es/spell/803185) |  | 1.5 min | — | Instant | Lock an enemy down with magical chains, stunning them and dragging them with you for 5 seconds. Every 1 sec, the enemy will suffer 48 Physic… |
| Guardian | all | [Battle Rush](https://db.exil.es/spell/802197) |  | 30s | — | Instant | Charge an enemy, dealing 21.714 Physical damage and stunning them for 1 sec. |
| Bloodmage | all | [Shadow Missile](https://db.exil.es/spell/536273) |  | 24s | — | Instant | Sends a shadowy bolt at the enemy, causing 65 to 66 Shadow damage and stunning them for 3 sec. |
| Bloodmage | all | [Pursuit](https://db.exil.es/spell/802869) ⚠ |  | 1.5 min | — | Instant | Requires Cursed Form Appear behind an enemy, dealing 411 Physical Damage, stunning the target for 4 sec, and reducing all damage taken by 20… |
| Ranger | all | [Eternal Knockdown](https://db.exil.es/spell/520758) |  | 25s | — | Instant | Knock an enemy down, dealing 48 Physical Damage and stunning them for 168 hour. For the duration, enemies take 0% increased damage from Assa… |
| Ranger | all | [Bushwhack](https://db.exil.es/spell/557333) ⚠ |  | none | 60 focus | Instant | Appear behind your target from the shadows, stunning them for 4 sec. |
| Cultist | all | [Facehug](https://db.exil.es/spell/800013) |  | 1.5 min | — | Channel 3s | The Mindbender teleports to an enemy and channels on them for up to 3 sec, Stunning the target for the duration. |
| Sun Cleric | all (tree) | [Glare](https://db.exil.es/spell/805583) |  | none | 20% mana | 1.5s | Flash powerful light that deals 168 + 27.41% SP Holy Damage and stuns enemies within 8 yds for 5 seconds. |
| Tinker | all | [Vanguard X-173: Onslaught](https://db.exil.es/spell/801828) |  | 20s | 30 energy | Instant | Causes 216 to 219 Physical Damage to enemies in a 15yd frontal cone and stunning enemies hit for 3 sec. |
| Tinker | all | [Drill Smash](https://db.exil.es/spell/806173) |  | 30s | — | Instant | Repeatedly drill into an enemy, dealing 125 Physical Damage, repeating every 1 sec and stunning them for 4 sec. |
| Venomancer | all | [Poison Eruption](https://db.exil.es/spell/520232) ⚠ |  | 2 min | 8% mana | Instant | Requires Scorpid Form Erupt in a poisonous frenzy, leeching 185 health and stunning enemies within 8 yds for 5 sec. |
| Primalist | Mountain King | [Mountain Hammer](https://db.exil.es/spell/681130) |  | none | 200 rage | Instant | Throw a hammer at an enemy dealing 67 + 35.5% nature SP + 15.5% AP Physical Damage and stunning them for 5 seconds. |
| Primalist | all | [Monolith Smash](https://db.exil.es/spell/991349) **(int)** |  | none | 3% mana | 5s | Stuns an enemy for 3 sec and Interrupts non-player spellcasting for 3 sec. |
| Runemaster | riftblade | [Ice Rune](https://db.exil.es/spell/524930) |  | 1 min | 12% mana | Instant | Requires Frozen Target Unleash a frost rune at an enemy, stunning them for 4 sec. Affected enemies are considered Frozen. |
| Runemaster | all | [Everfrost Scroll](https://db.exil.es/spell/801090) |  | none | 5% mana | Instant | Stun an enemy target for 3.5 sec, increasing Frost damage they take from you by 20% for the duration. |
```

</details>

**17 across 12 classes.**
None found for: Chronomancer, Felsworn, Necromancer, Pyromancer, Reaper, Starcaller, Stormbringer, Templar, Witch Doctor.

## 4. Roots

`mechanic 7` (ROOT) or `13` (FREEZE). Snares and slows (`mechanic 11`) are deliberately NOT here -- a slow is not a root, and folding them in would triple the table with abilities that do not hold anything in place.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | all | [Bwonsamdi's Judgement](https://db.exil.es/spell/525386) |  | none | 10% mana | Instant | Deals 85 Shadow Damage to an enemy and roots them for 2 sec. |
| Stormbringer | all | [Exhale](https://db.exil.es/spell/801846) ⚠ |  | 40s | 11% mana | Instant | Exhale a gust of wind in a 15 yd cone in front of you, dealing 109.2 Nature Damage and rooting up to 0 enemies in place for 8 sec. Damage ca… |
| Knight of Xoroth | all | [Hellhaul](https://db.exil.es/spell/503142) |  | 3 min | — | Instant | You bind an enemy target with magical Hellfire Chains, rooting them and dragging them with you for 5 sec. Every 0.25 sec for the duration th… |
| Guardian | all (tree) | [Net Throw](https://db.exil.es/spell/802304) |  | 15s | 15 energy | Instant | Toss a weighted net at an enemy that roots them for 4 seconds. While active, the target cannot dodge attacks. |
| Ranger | Farstrider | [Whipvine Arrow](https://db.exil.es/spell/806342) ⚠ |  | 1 min | 25 focus | 1.7s | Launch an arrow with magical vines attached to it at your target, dealing 78 + 33% ranged AP Nature Damage and rooting them for 40 seconds (… |
| Chronomancer | artificer,infinite,time | [Clasp of Infinity](https://db.exil.es/spell/805847) ⚠ |  | 20s | 23% mana | Instant | Conjure a magical binding upon an enemy that bounces to nearby enemies, rooting them in place for 4 seconds. |
| Necromancer | all | [Cryo Freeze](https://db.exil.es/spell/680363) |  | none | 7% mana | Instant | Unleashes a frost explosion at teleportaion location and freezes all enemies nearby. |
| Necromancer | all | [Black Ice](https://db.exil.es/spell/801746) |  | 30s | 10% mana | Instant | A ring of ice erupts from the target, rooting enemies around them in ice for 8 sec, and applying Deathchill. Damage caused may interrupt the… |
| Pyromancer | flameweaving | [Cindergrip](https://db.exil.es/spell/805476) |  | none | 19% mana | 1.5s | Raise a lava crag from beneath an enemy, rooting them in place, dealing 28 Fire damage every 3 sec for 12 sec (8 sec vs players). Damage cau… |
| Tinker | all | [Hydraulic Charge](https://db.exil.es/spell/800582) ⚠ |  | 15s | 6% mana | Instant | Charge an enemy with your Clockwork Assistant and strike as one, each dealing 362 Physical Damage and rooting enemies in place for 2 sec. |
| Venomancer | all (tree) | [Spindlebind](https://db.exil.es/spell/800887) ⚠ |  | 16s | 30 energy | Instant | Emit webs at all enemies in a 10 yd cone behind you, rooting them for 4 seconds, and unleashing a beetle on the trapped enemy from below, in… |
| Venomancer | all | [Venocannon](https://db.exil.es/spell/804967) |  | 1 min | — | Instant | Burst out of your burrow, rooting yourself in place for 0.001 sec. While active, all spells have 15 yd of additional range, and the cast tim… |
| Primalist | all | [Swoop](https://db.exil.es/spell/806546) |  | 30s | — | Channel 3s | Swoop an enemy, flying to their position and knocking them down. Rooting the target for 3 sec, disabling movement abilities. |
| Runemaster | glyphic,engravement,riftblade | [Glacial Rune](https://db.exil.es/spell/805730) ⚠ |  | 20s | 9% mana | Instant | Place a rune at the target location that explodes after 1 sec with frigid magic, dealing 362.824 Frost Damage to enemies inside and freezing… |
| Runemaster | all | [Cryobrand](https://db.exil.es/spell/807822) ⚠ |  | none | 4% mana | Instant | Blast an enemy with frost magic, freezing them in place for 40 sec (8 sec vs players). Can only affect 1 enemy at a time. Does not break ste… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | all | [Bwonsamdi's Judgement](https://db.exil.es/spell/525386) |  | none | 10% mana | Instant | Deals 85 Shadow Damage to an enemy and roots them for 2 sec. |
| Stormbringer | all | [Exhale](https://db.exil.es/spell/801846) ⚠ |  | 40s | 11% mana | Instant | Exhale a gust of wind in a 15 yd cone in front of you, dealing 109.2 Nature Damage and rooting up to 0 enemies in place for 8 sec. Damage ca… |
| Knight of Xoroth | all | [Hellhaul](https://db.exil.es/spell/503142) |  | 3 min | — | Instant | You bind an enemy target with magical Hellfire Chains, rooting them and dragging them with you for 5 sec. Every 0.25 sec for the duration th… |
| Guardian | all (tree) | [Net Throw](https://db.exil.es/spell/802304) |  | 15s | 15 energy | Instant | Toss a weighted net at an enemy that roots them for 4 seconds. While active, the target cannot dodge attacks. |
| Ranger | Farstrider | [Whipvine Arrow](https://db.exil.es/spell/806342) ⚠ |  | 1 min | 25 focus | 1.7s | Launch an arrow with magical vines attached to it at your target, dealing 78 + 33% ranged AP Nature Damage and rooting them for 40 seconds (… |
| Chronomancer | artificer,infinite,time | [Clasp of Infinity](https://db.exil.es/spell/805847) ⚠ |  | 20s | 23% mana | Instant | Conjure a magical binding upon an enemy that bounces to nearby enemies, rooting them in place for 4 seconds. |
| Necromancer | all | [Cryo Freeze](https://db.exil.es/spell/680363) |  | none | 7% mana | Instant | Unleashes a frost explosion at teleportaion location and freezes all enemies nearby. |
| Necromancer | all | [Black Ice](https://db.exil.es/spell/801746) |  | 30s | 10% mana | Instant | A ring of ice erupts from the target, rooting enemies around them in ice for 8 sec, and applying Deathchill. Damage caused may interrupt the… |
| Pyromancer | flameweaving | [Cindergrip](https://db.exil.es/spell/805476) |  | none | 19% mana | 1.5s | Raise a lava crag from beneath an enemy, rooting them in place, dealing 28 Fire damage every 3 sec for 12 sec (8 sec vs players). Damage cau… |
| Tinker | all | [Hydraulic Charge](https://db.exil.es/spell/800582) ⚠ |  | 15s | 6% mana | Instant | Charge an enemy with your Clockwork Assistant and strike as one, each dealing 362 Physical Damage and rooting enemies in place for 2 sec. |
| Venomancer | all (tree) | [Spindlebind](https://db.exil.es/spell/800887) ⚠ |  | 16s | 30 energy | Instant | Emit webs at all enemies in a 10 yd cone behind you, rooting them for 4 seconds, and unleashing a beetle on the trapped enemy from below, in… |
| Venomancer | all | [Venocannon](https://db.exil.es/spell/804967) |  | 1 min | — | Instant | Burst out of your burrow, rooting yourself in place for 0.001 sec. While active, all spells have 15 yd of additional range, and the cast tim… |
| Primalist | all | [Swoop](https://db.exil.es/spell/806546) |  | 30s | — | Channel 3s | Swoop an enemy, flying to their position and knocking them down. Rooting the target for 3 sec, disabling movement abilities. |
| Runemaster | glyphic,engravement,riftblade | [Glacial Rune](https://db.exil.es/spell/805730) ⚠ |  | 20s | 9% mana | Instant | Place a rune at the target location that explodes after 1 sec with frigid magic, dealing 362.824 Frost Damage to enemies inside and freezing… |
| Runemaster | all | [Cryobrand](https://db.exil.es/spell/807822) ⚠ |  | none | 4% mana | Instant | Blast an enemy with frost magic, freezing them in place for 40 sec (8 sec vs players). Can only affect 1 enemy at a time. Does not break ste… |
```

</details>

**15 across 12 classes.**
None found for: Barbarian, Bloodmage, Cultist, Felsworn, Reaper, Starcaller, Sun Cleric, Templar, Witch Hunter.

## 5. Battle Rezzes

`effect_id 18` (RESURRECT) or `113` (RESURRECT_NEW). **Both are in use** -- Bloodmage **Vampyr Bite** is 18, Pyromancer **Phoenix Rebirth** is 113. Matching only 18 finds 2 spells and misses almost everything.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | all | [Reclaim Soul](https://db.exil.es/spell/801796) |  | none | 30% mana | 8s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Templar | all | [Spiritual Ascension](https://db.exil.es/spell/500688) |  | 5 min | — | 2s | Call an ally's spirit back to their body, bringing them back to life. Usable while in combat. |
| Bloodmage | all | [Vampyr Bite](https://db.exil.es/spell/801563) |  | none | — | 8s | Brings a dead player back to life with 70% health and mana. For the next 20 sec, the target takes 50% increased healing, but being damaged e… |
| Chronomancer | all | [Do Over](https://db.exil.es/spell/800669) |  | none | 36% mana | 8s | Restores a dead ally to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Chronomancer | time | [Resynchronize](https://db.exil.es/spell/804495) |  | 30 min | — | Instant | Switch to the timeline where your party didn't die, returning all party members to life with 583 health and 833 mana. Can be cast while dead… |
| Necromancer | all | [Call of The Scourge](https://db.exil.es/spell/801792) |  | 10 min | 68% mana | 2s | Bring a dead ally back to life with 70 health and 135 mana. Can be used in combat. |
| Necromancer | all | [Reanimate](https://db.exil.es/spell/804172) |  | 3 min | 250 runic power | Instant | Revives the corpse of a non-elite Undead or Humanoid, binding it to your control for up to 10 sec. While controlled, the target will decay o… |
| Pyromancer | flameweaving | [Phoenix Rebirth](https://db.exil.es/spell/706867) |  | none | 60% mana | 10s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Pyromancer | flameweaving | [Reborn from Ash](https://db.exil.es/spell/804231) |  | 10 min | — | 2s | Returns a dead ally to life with 400 health and 635 mana, can also be used on self while dead. Can be used in combat. |
| Cultist | all | [Ritual of Awakening](https://db.exil.es/spell/801791) |  | none | 60% mana | 8s | Brings a dead player back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Starcaller | all | [Tidal Rebirth](https://db.exil.es/spell/801793) |  | 10 min | 75% mana | 2s | Instantly brings a dead ally back to life with 400 health and 635 mana. This spell is usable in combat. |
| Starcaller | all | [Celestial Awakening](https://db.exil.es/spell/801795) |  | none | 60% mana | 8s | Brings a dead ally back to life with 70 Health and 135 Mana. The target gains 200% increased Mana regeneration for 10 sec. Cannot be cast wh… |
| Sun Cleric | all | [Revivify](https://db.exil.es/spell/801790) |  | none | 60% mana | 8s | Brings a dead ally back to life with 70 health and 135 mana. Not usable in combat. |
| Sun Cleric | all | [Val'kyr Ressurrection](https://db.exil.es/spell/804608) |  | none | — | 5s | Brings a dead player back to life with 2000 health and 833 mana. Cannot be cast when in combat. |
| Tinker | all | [Defibrillate](https://db.exil.es/spell/802175) |  | none | 20% mana | 10s | Brings up to 5 dead allies within 15 yds back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Venomancer | all | [Prayer Beads](https://db.exil.es/spell/520681) |  | none | 60% mana | 8s | Pray to Shadra and honor the venomcult, allowing you to bring a dead ally back to life with 70 health and 135 mana. Cannot be cast when in c… |
| Venomancer | all | [Spawn](https://db.exil.es/spell/805568) |  | 10 min | 20% mana | 2s | Bring a dead ally back to life with 400 health and 635 mana. Can be used in combat. Not usable in arena. |
| Primalist | all | [Return to Life](https://db.exil.es/spell/801794) |  | none | 60% mana | 10s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | all | [Reclaim Soul](https://db.exil.es/spell/801796) |  | none | 30% mana | 8s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Templar | all | [Spiritual Ascension](https://db.exil.es/spell/500688) |  | 5 min | — | 2s | Call an ally's spirit back to their body, bringing them back to life. Usable while in combat. |
| Bloodmage | all | [Vampyr Bite](https://db.exil.es/spell/801563) |  | none | — | 8s | Brings a dead player back to life with 70% health and mana. For the next 20 sec, the target takes 50% increased healing, but being damaged e… |
| Chronomancer | all | [Do Over](https://db.exil.es/spell/800669) |  | none | 36% mana | 8s | Restores a dead ally to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Chronomancer | time | [Resynchronize](https://db.exil.es/spell/804495) |  | 30 min | — | Instant | Switch to the timeline where your party didn't die, returning all party members to life with 583 health and 833 mana. Can be cast while dead… |
| Necromancer | all | [Call of The Scourge](https://db.exil.es/spell/801792) |  | 10 min | 68% mana | 2s | Bring a dead ally back to life with 70 health and 135 mana. Can be used in combat. |
| Necromancer | all | [Reanimate](https://db.exil.es/spell/804172) |  | 3 min | 250 runic power | Instant | Revives the corpse of a non-elite Undead or Humanoid, binding it to your control for up to 10 sec. While controlled, the target will decay o… |
| Pyromancer | flameweaving | [Phoenix Rebirth](https://db.exil.es/spell/706867) |  | none | 60% mana | 10s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Pyromancer | flameweaving | [Reborn from Ash](https://db.exil.es/spell/804231) |  | 10 min | — | 2s | Returns a dead ally to life with 400 health and 635 mana, can also be used on self while dead. Can be used in combat. |
| Cultist | all | [Ritual of Awakening](https://db.exil.es/spell/801791) |  | none | 60% mana | 8s | Brings a dead player back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Starcaller | all | [Tidal Rebirth](https://db.exil.es/spell/801793) |  | 10 min | 75% mana | 2s | Instantly brings a dead ally back to life with 400 health and 635 mana. This spell is usable in combat. |
| Starcaller | all | [Celestial Awakening](https://db.exil.es/spell/801795) |  | none | 60% mana | 8s | Brings a dead ally back to life with 70 Health and 135 Mana. The target gains 200% increased Mana regeneration for 10 sec. Cannot be cast wh… |
| Sun Cleric | all | [Revivify](https://db.exil.es/spell/801790) |  | none | 60% mana | 8s | Brings a dead ally back to life with 70 health and 135 mana. Not usable in combat. |
| Sun Cleric | all | [Val'kyr Ressurrection](https://db.exil.es/spell/804608) |  | none | — | 5s | Brings a dead player back to life with 2000 health and 833 mana. Cannot be cast when in combat. |
| Tinker | all | [Defibrillate](https://db.exil.es/spell/802175) |  | none | 20% mana | 10s | Brings up to 5 dead allies within 15 yds back to life with 70 health and 135 mana. Cannot be cast when in combat. |
| Venomancer | all | [Prayer Beads](https://db.exil.es/spell/520681) |  | none | 60% mana | 8s | Pray to Shadra and honor the venomcult, allowing you to bring a dead ally back to life with 70 health and 135 mana. Cannot be cast when in c… |
| Venomancer | all | [Spawn](https://db.exil.es/spell/805568) |  | 10 min | 20% mana | 2s | Bring a dead ally back to life with 400 health and 635 mana. Can be used in combat. Not usable in arena. |
| Primalist | all | [Return to Life](https://db.exil.es/spell/801794) |  | none | 60% mana | 10s | Brings a dead ally back to life with 70 health and 135 mana. Cannot be cast when in combat. |
```

</details>

**18 across 12 classes.**
None found for: Barbarian, Felsworn, Guardian, Knight of Xoroth, Ranger, Reaper, Runemaster, Stormbringer, Witch Hunter.

## 6. Purges

`effect_id 38` (DISPEL) where the tooltip names a *beneficial* effect on an *enemy*. Target flags alone are unreliable -- **Show of Force** is `target_a 6` and reads "on a friendly target".

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Templar | all | [Righteous Reprimand](https://db.exil.es/spell/572308) ⚠ |  | 10s | 6% mana | Instant | Removes 1 beneficial magic effect from an enemy. |
| Chronomancer | time | [Continuum Restoration](https://db.exil.es/spell/801271) ⚠ |  | 1.5 min | 60% mana | 1.5s | Restore the continuum at target location for all allies and enemies within 15 yds, removing all beneficial magic effects from enemies and ha… |
| Cultist | Godblade | [Netherstrike](https://db.exil.es/spell/806222) |  | none | 10% mana | Instant | Generates 10 Insanity Strike an enemy quickly for 125% Weapon Damage plus 40 Shadow Damage, purging 1 beneficial magic effect from them. Onl… |
| Sun Cleric | all | [Gavel of Wrath](https://db.exil.es/spell/800617) |  | none | 10% mana | Instant | Smash an enemy for 100% Weapon Damage plus 45 and dispel 1 beneficial magic effect from them. Shares a cooldown with other Gavels. |
| Reaper | all | [Soul Shear](https://db.exil.es/spell/520862) |  | 16s | — | Instant | Purge an enemy's soul, removing 2 beneficial magic effects from them. |
| Reaper | all | [Reap Magic](https://db.exil.es/spell/704258) |  | none | — | Instant | Steals 1 beneficial Magic Effect from an enemy. If you successfuly steal an effect, you also siphon 160 Health from the target as Shadow Dam… |
| Primalist | all | [Neutralizing Touch](https://db.exil.es/spell/572307) ⚠ |  | 10s | — | Instant | Removes 1 beneficial magic effect from an enemy. |
| Runemaster | engravement | [Resonance Rune](https://db.exil.es/spell/803679) |  | 1 min | 30% mana | 1.5s | Place an arcane rune on the ground that dispels 3 harmful magic effects from allies in the radius, and purges 3 beneficial magic effects fro… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Templar | all | [Righteous Reprimand](https://db.exil.es/spell/572308) ⚠ |  | 10s | 6% mana | Instant | Removes 1 beneficial magic effect from an enemy. |
| Chronomancer | time | [Continuum Restoration](https://db.exil.es/spell/801271) ⚠ |  | 1.5 min | 60% mana | 1.5s | Restore the continuum at target location for all allies and enemies within 15 yds, removing all beneficial magic effects from enemies and ha… |
| Cultist | Godblade | [Netherstrike](https://db.exil.es/spell/806222) |  | none | 10% mana | Instant | Generates 10 Insanity Strike an enemy quickly for 125% Weapon Damage plus 40 Shadow Damage, purging 1 beneficial magic effect from them. Onl… |
| Sun Cleric | all | [Gavel of Wrath](https://db.exil.es/spell/800617) |  | none | 10% mana | Instant | Smash an enemy for 100% Weapon Damage plus 45 and dispel 1 beneficial magic effect from them. Shares a cooldown with other Gavels. |
| Reaper | all | [Soul Shear](https://db.exil.es/spell/520862) |  | 16s | — | Instant | Purge an enemy's soul, removing 2 beneficial magic effects from them. |
| Reaper | all | [Reap Magic](https://db.exil.es/spell/704258) |  | none | — | Instant | Steals 1 beneficial Magic Effect from an enemy. If you successfuly steal an effect, you also siphon 160 Health from the target as Shadow Dam… |
| Primalist | all | [Neutralizing Touch](https://db.exil.es/spell/572307) ⚠ |  | 10s | — | Instant | Removes 1 beneficial magic effect from an enemy. |
| Runemaster | engravement | [Resonance Rune](https://db.exil.es/spell/803679) |  | 1 min | 30% mana | 1.5s | Place an arcane rune on the ground that dispels 3 harmful magic effects from allies in the radius, and purges 3 beneficial magic effects fro… |
```

</details>

**8 across 7 classes.**
None found for: Barbarian, Bloodmage, Felsworn, Guardian, Knight of Xoroth, Necromancer, Pyromancer, Ranger, Starcaller, Stormbringer, Tinker, Venomancer, Witch Doctor, Witch Hunter.

## 7. Spellsteals

`effect_id 126` -- STEAL_BENEFICIAL_BUFF.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Felsworn | all | [Consume Magic](https://db.exil.es/spell/800353) |  | none | 30 energy | Instant | Steal 1 beneficial magic effects from an enemy. If you successfully steal an effect, you deal 8 Shadow Damage to the enemy. |
| Bloodmage | all | [Siphon](https://db.exil.es/spell/803327) ⚠ |  | 6s | — | Instant | Steal 2 beneficial magic effects from an enemy. |
| Runemaster | all | [Leyfeed](https://db.exil.es/spell/520269) ⚠ |  | none | 20% mana | 1s | Feed off the latent magic of an enemy, stealing 2 beneficial magic effects from them. Usable while moving. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Felsworn | all | [Consume Magic](https://db.exil.es/spell/800353) |  | none | 30 energy | Instant | Steal 1 beneficial magic effects from an enemy. If you successfully steal an effect, you deal 8 Shadow Damage to the enemy. |
| Bloodmage | all | [Siphon](https://db.exil.es/spell/803327) ⚠ |  | 6s | — | Instant | Steal 2 beneficial magic effects from an enemy. |
| Runemaster | all | [Leyfeed](https://db.exil.es/spell/520269) ⚠ |  | none | 20% mana | 1s | Feed off the latent magic of an enemy, stealing 2 beneficial magic effects from them. Usable while moving. |
```

</details>

**3 across 3 classes.**
None found for: Barbarian, Chronomancer, Cultist, Guardian, Knight of Xoroth, Necromancer, Primalist, Pyromancer, Ranger, Reaper, Starcaller, Stormbringer, Sun Cleric, Templar, Tinker, Venomancer, Witch Doctor, Witch Hunter.

## 8. Tranq Shots / Soothes (remove enrage)

`effect_id 38` with `misc_value 9` -- dispel type Enrage.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Hunter | all | [Purge Evil](https://db.exil.es/spell/572306) |  | 20s | 25% mana | Instant | Purge the evil from an enemy, removing all enrage effects from them. |
| Witch Hunter | all | [Sedative Shot](https://db.exil.es/spell/572406) ⚠ |  | none | 35 focus | Instant\* | Shoot an arrow at an enemy with sedative toxins, dealing 50% Ranged Weapon Damage as Nature Damage and removing 1 enrage effect from them. |
| Stormbringer | all | [Calm the Storm](https://db.exil.es/spell/572303) |  | none | Depletes 10 | Instant | Depletes 10 Static Calm an enemy, removing 1 enrage effect from them. |
| Venomancer | all | [Myotoxin](https://db.exil.es/spell/572304) |  | 10s | 10% mana | Instant | Inject an enemy with myotoxins, removing 1 enrage effect, repeating every 4 sec for 20 sec. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Hunter | all | [Purge Evil](https://db.exil.es/spell/572306) |  | 20s | 25% mana | Instant | Purge the evil from an enemy, removing all enrage effects from them. |
| Witch Hunter | all | [Sedative Shot](https://db.exil.es/spell/572406) ⚠ |  | none | 35 focus | Instant\* | Shoot an arrow at an enemy with sedative toxins, dealing 50% Ranged Weapon Damage as Nature Damage and removing 1 enrage effect from them. |
| Stormbringer | all | [Calm the Storm](https://db.exil.es/spell/572303) |  | none | Depletes 10 | Instant | Depletes 10 Static Calm an enemy, removing 1 enrage effect from them. |
| Venomancer | all | [Myotoxin](https://db.exil.es/spell/572304) |  | 10s | 10% mana | Instant | Inject an enemy with myotoxins, removing 1 enrage effect, repeating every 4 sec for 20 sec. |
```

</details>

**4 across 3 classes.**
None found for: Barbarian, Bloodmage, Chronomancer, Cultist, Felsworn, Guardian, Knight of Xoroth, Necromancer, Primalist, Pyromancer, Ranger, Reaper, Runemaster, Starcaller, Sun Cleric, Templar, Tinker, Witch Doctor.

## 9. Raid damage reduction — active

`aura_id 87` (MOD_DAMAGE_PERCENT_TAKEN) or `229` (AoE damage taken), where the tooltip names the party, raid or allies AND the ability has a cooldown or a cost -- i.e. something you press.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Felsworn | Tyrant | [Infernal Whipcrack](https://db.exil.es/spell/805243) |  | 1.5 min | — | Instant | Enrage up to 8 allies within 20 yds, reducing their damage taken by -15% and increasing their haste by 10% for 10 seconds. |
| Guardian | Vanguard | [Bastion](https://db.exil.es/spell/802283) |  | 5 min | 40 energy | Instant | Raise your shield and lead your allies within 12 yds, reducing their damage taken by -40% for 10 seconds. |
| Templar | all | [Grace of Aman'Thul](https://db.exil.es/spell/801477) |  | 20s | 20 energy | Instant | Unleash a defensive Oath Breaker, causing damage taken from melee attacks to heal yourself and allies within 10 yds for 136. Lasts 0 or unti… |
| Chronomancer | artificer | [Decelerate](https://db.exil.es/spell/572632) |  | none | 32% mana | Instant | Decelerates magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. Lasts 10… |
| Pyromancer | all | [Lucifron's Lagniappe](https://db.exil.es/spell/805497) |  | 30s | 10% mana | Instant | Enhance an ally for 30 sec, increasing their spell haste by 10% and reducing all damage taken by 10%. Can only target 1 ally at a time. |
| Cultist | all | [Whispers of Yogg-Saron](https://db.exil.es/spell/572637) ⚠ |  | none | 27% mana | Instant | Destabilizes magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. |
| Cultist | all | [Protection From Light](https://db.exil.es/spell/804065) |  | 30s | 3% mana | Instant | Reduces all Holy Damage and Fire Damage taken by an ally by 40% for 10 sec. While active, the ally is Healed for 24 to 25 every 2 sec. |
| Sun Cleric | Seraphim | [Scroll of Hope](https://db.exil.es/spell/680646) |  | 5 min | 40% mana | Instant | Read from a scroll of hope, reducing Magic Damage taken by party and raid members within 15 yds by -30% for 10 seconds. If any ally falls be… |
| Tinker | all | [Arcane Bionics](https://db.exil.es/spell/541493) |  | none | 8% mana | Instant | Augment a party member with the essence of arcane, decreasing damage taken from spells by up to 3% and healing spells by up to 3%. Lasts 5 m… |
| Tinker | all (tree) | [Kinetic Shield](https://db.exil.es/spell/806224) |  | 5 min | 38% mana | Instant | Create magnetic shields of kinetic energy on an ally target for 10 seconds, reducing damage taken by -35% and making them immune to stun eff… |
| Venomancer | Vizier | [Shadra's Aid](https://db.exil.es/spell/504352) |  | 3 min | 19% mana | Instant | Envelop an ally in Shadra's grace, reducing all damage taken by -20% and causing direct damage taken to restore 3% maximum health for 15 sec… |
| Primalist | all | [Essence of Dispersion](https://db.exil.es/spell/572818) ⚠ |  | none | 20% mana | Instant | Disperses magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Felsworn | Tyrant | [Infernal Whipcrack](https://db.exil.es/spell/805243) |  | 1.5 min | — | Instant | Enrage up to 8 allies within 20 yds, reducing their damage taken by -15% and increasing their haste by 10% for 10 seconds. |
| Guardian | Vanguard | [Bastion](https://db.exil.es/spell/802283) |  | 5 min | 40 energy | Instant | Raise your shield and lead your allies within 12 yds, reducing their damage taken by -40% for 10 seconds. |
| Templar | all | [Grace of Aman'Thul](https://db.exil.es/spell/801477) |  | 20s | 20 energy | Instant | Unleash a defensive Oath Breaker, causing damage taken from melee attacks to heal yourself and allies within 10 yds for 136. Lasts 0 or unti… |
| Chronomancer | artificer | [Decelerate](https://db.exil.es/spell/572632) |  | none | 32% mana | Instant | Decelerates magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. Lasts 10… |
| Pyromancer | all | [Lucifron's Lagniappe](https://db.exil.es/spell/805497) |  | 30s | 10% mana | Instant | Enhance an ally for 30 sec, increasing their spell haste by 10% and reducing all damage taken by 10%. Can only target 1 ally at a time. |
| Cultist | all | [Whispers of Yogg-Saron](https://db.exil.es/spell/572637) ⚠ |  | none | 27% mana | Instant | Destabilizes magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. |
| Cultist | all | [Protection From Light](https://db.exil.es/spell/804065) |  | 30s | 3% mana | Instant | Reduces all Holy Damage and Fire Damage taken by an ally by 40% for 10 sec. While active, the ally is Healed for 24 to 25 every 2 sec. |
| Sun Cleric | Seraphim | [Scroll of Hope](https://db.exil.es/spell/680646) |  | 5 min | 40% mana | Instant | Read from a scroll of hope, reducing Magic Damage taken by party and raid members within 15 yds by -30% for 10 seconds. If any ally falls be… |
| Tinker | all | [Arcane Bionics](https://db.exil.es/spell/541493) |  | none | 8% mana | Instant | Augment a party member with the essence of arcane, decreasing damage taken from spells by up to 3% and healing spells by up to 3%. Lasts 5 m… |
| Tinker | all (tree) | [Kinetic Shield](https://db.exil.es/spell/806224) |  | 5 min | 38% mana | Instant | Create magnetic shields of kinetic energy on an ally target for 10 seconds, reducing damage taken by -35% and making them immune to stun eff… |
| Venomancer | Vizier | [Shadra's Aid](https://db.exil.es/spell/504352) |  | 3 min | 19% mana | Instant | Envelop an ally in Shadra's grace, reducing all damage taken by -20% and causing direct damage taken to restore 3% maximum health for 15 sec… |
| Primalist | all | [Essence of Dispersion](https://db.exil.es/spell/572818) ⚠ |  | none | 20% mana | Instant | Disperses magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. |
```

</details>

**12 across 10 classes.**
None found for: Barbarian, Bloodmage, Knight of Xoroth, Necromancer, Ranger, Reaper, Runemaster, Starcaller, Stormbringer, Witch Doctor, Witch Hunter.

## 9b. Raid damage reduction — passive auras

Same auras, group-scoped, but **no cooldown and no cost**: talents and stances that shape the raid's damage intake without being pressed. Separated because a raid cooldown plan cares about the first list; roster composition cares about this one.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Stormbringer | all | [Cyclonean Protection](https://db.exil.es/spell/804067) ⚠ |  | none | — | Instant | Reduces the damage taken from area of effect attacks of party members within 20 yds by 15%. |
| Templar | all | [Tithe of Alacrity](https://db.exil.es/spell/804818) |  | none | — | 3s | Emanate an aura for 1 hour, empowering party and raid members with 15% reduced damage taken from area of effect attacks. |
| Cultist | Dreadnought | [Voidwarding](https://db.exil.es/spell/560002) |  | none | — | Instant | Reduces damage taken by party and raid members by -3%. Does not stack with similar effects. In addition, increases all of your resistances b… |
| Cultist | Heretic | [Protection From Light](https://db.exil.es/spell/704434) |  | none | — | Instant | Reduces all damage taken by party and raid members by -3%. In addition, your Holy Damage taken is reduced by -10%. |
| Starcaller | Moon Guard | [Shrouded Stars](https://db.exil.es/spell/704785) |  | none | — | Instant | Reduces damage taken by all party and raid members by -3%. Does not stack with similar effects. |
| Venomancer | Fortitude | [Charmed Plating](https://db.exil.es/spell/300974) |  | none | — | Instant | Reduces damage taken by all party and raid members by 3%. Does not stack with similar effects. In addition, reduces your chance to be hit by… |
| Reaper | Domination | [Ethereal Guard](https://db.exil.es/spell/300969) |  | none | — | Instant | Reduces the damage taken by party and raid members by -3%. Does not stack with similar effects. In addition, increases your melee haste by 1… |
| Primalist | all | [Lesser Boon of the Turtle](https://db.exil.es/spell/524750) |  | none | — | Instant | Damage taken reduced by 2%. Only 1 Lesser Boon may be active on an ally at a time. |
| Primalist | Life | [Ring of Life](https://db.exil.es/spell/804705) |  | none | — | Instant | Allies within 40 yds receive 6% increased healing. Does not stack with similar effects. In addition, your Magic Damage taken is reduced by -… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Stormbringer | all | [Cyclonean Protection](https://db.exil.es/spell/804067) ⚠ |  | none | — | Instant | Reduces the damage taken from area of effect attacks of party members within 20 yds by 15%. |
| Templar | all | [Tithe of Alacrity](https://db.exil.es/spell/804818) |  | none | — | 3s | Emanate an aura for 1 hour, empowering party and raid members with 15% reduced damage taken from area of effect attacks. |
| Cultist | Dreadnought | [Voidwarding](https://db.exil.es/spell/560002) |  | none | — | Instant | Reduces damage taken by party and raid members by -3%. Does not stack with similar effects. In addition, increases all of your resistances b… |
| Cultist | Heretic | [Protection From Light](https://db.exil.es/spell/704434) |  | none | — | Instant | Reduces all damage taken by party and raid members by -3%. In addition, your Holy Damage taken is reduced by -10%. |
| Starcaller | Moon Guard | [Shrouded Stars](https://db.exil.es/spell/704785) |  | none | — | Instant | Reduces damage taken by all party and raid members by -3%. Does not stack with similar effects. |
| Venomancer | Fortitude | [Charmed Plating](https://db.exil.es/spell/300974) |  | none | — | Instant | Reduces damage taken by all party and raid members by 3%. Does not stack with similar effects. In addition, reduces your chance to be hit by… |
| Reaper | Domination | [Ethereal Guard](https://db.exil.es/spell/300969) |  | none | — | Instant | Reduces the damage taken by party and raid members by -3%. Does not stack with similar effects. In addition, increases your melee haste by 1… |
| Primalist | all | [Lesser Boon of the Turtle](https://db.exil.es/spell/524750) |  | none | — | Instant | Damage taken reduced by 2%. Only 1 Lesser Boon may be active on an ally at a time. |
| Primalist | Life | [Ring of Life](https://db.exil.es/spell/804705) |  | none | — | Instant | Allies within 40 yds receive 6% increased healing. Does not stack with similar effects. In addition, your Magic Damage taken is reduced by -… |
```

</details>

**9 across 7 classes.**
None found for: Barbarian, Bloodmage, Chronomancer, Felsworn, Guardian, Knight of Xoroth, Necromancer, Pyromancer, Ranger, Runemaster, Sun Cleric, Tinker, Witch Doctor, Witch Hunter.

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

