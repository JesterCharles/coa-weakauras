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
| Barbarian | all (tree)<br>r0 c4 | [Jawbreaker](https://db.exil.es/spell/802792) |  | 14s | 30 energy | Instant | Attempt to break an enemy's jaw, interrupting them and preventing any spell from that school from being cast for 4 seconds. |
| Felsworn | Infernal<br>r5 c1 | [Felbreak](https://db.exil.es/spell/800203) |  | 18s | 10 energy | 0.5s | Interrupt a spell from being cast, preventing the target from casting spells of that school for 3 seconds and draining mana from the target … |
| Witch Hunter | Black Knight<br>r5 c2 | [Guard Strike](https://db.exil.es/spell/804432) |  | 18s | 100 rage | Instant | Bash an enemy with your weapon's hilt, interrupting them and preventing any spell from that school of magic from being cast for 3 seconds. |
| Stormbringer | all | [Gust of Wind](https://db.exil.es/spell/500932) |  | 35s | 37% mana | Instant | Send forth a gust of wind in a frontal cone, knocking enemies back and interrupting all enemies current spell cast, preventing any spell fro… |
| Stormbringer | Maelstrom<br>r4 c7 | [Mystic Thunder](https://db.exil.es/spell/504846) |  | 30s | 15% mana | Instant | Interrupt the target's current spell cast and then mark them for 5 seconds. If they cast again while marked they are silenced for 3 seconds. |
| Knight of Xoroth | all | [Hellgaze](https://db.exil.es/spell/560471) |  | 15s | — | Instant | Interrupts spellcasting and prevents any spell from that school from being cast for 4 sec. |
| Guardian | all | [Shield of Denial](https://db.exil.es/spell/704159) |  | 30s | 15 energy | Instant | Toss a shield at an enemy that bounces to up 2 nearby enemies, dealing 155 Physical damage and interrupting their spellcast, preventing any … |
| Bloodmage | Sanguine<br>r3 c3 | [Aneurysm](https://db.exil.es/spell/806099) |  | 24s | 10% health | Instant | Counter the enemy's spellcast, preventing any spell from that school of magic from being cast for 4 seconds. Successfully interrupting an en… |
| Ranger | Brigand<br>r5 c1 | [Throatpunch](https://db.exil.es/spell/500617) |  | 12s | 25 focus | Instant | Punch an enemy in the throat, interrupting the enemy's spellcast, preventing any spell from that school of magic from being cast for 2 secon… |
| Chronomancer | all | [Fray Magic](https://db.exil.es/spell/510236) |  | 30s | 27% mana | Instant | Stop your enemies' timeline, interrupting their spell cast for 4 sec. Successfully interrupting an enemy will additionally silence them for … |
| Necromancer | Rime<br>r4 c0 | [Heartchill](https://db.exil.es/spell/801739) |  | 30s | 19% mana | Instant | Chill an enemy's heart, interrupting their current spell cast. Successfully interrupting a spell also reduces their movement speed and haste… |
| Pyromancer | all | [Spellburn](https://db.exil.es/spell/800808) |  | 25s | 9% mana | Instant | Counters the enemy's spellcast, preventing any spell from that school of magic from being cast for 5 sec. |
| Cultist | Dreadnought<br>r5 c7 | [Crushing Dissonance](https://db.exil.es/spell/804056) |  | 30s | 18% mana | Instant | Unleash a wave of maddening resonance, interrupting the current spell cast of all enemies around you and preventing any spell in that school… |
| Tinker | all | [Build: Rusthound](https://db.exil.es/spell/803437) **(pet — pet bar)** |  | 30s | 10% mana | 6s | Construct a Rusthound to accompany the Tinker until dismissed. — Meltdown: Bite an enemy, interrupting their current spellcast and preventing any spells from being cast from that school for 5 sec and reduces their Fire Resistance and healing received by 20%. |
| Venomancer | all | [Nullifying Toxin](https://db.exil.es/spell/805096) |  | 16s | 9% mana | Instant | Inject an enemy with nullifying toxin, interrupting them and preventing any spell from that school from being cast for 3 sec. |
| Reaper | Harvest<br>r6 c6 | [Siphon Essence](https://db.exil.es/spell/806125) |  | 20s | — | Instant | Attempt to drain an enemies vitals, leeching 22 + 31.03% AP health, interrupting casting and preventing any spell from that school from bein… |
| Primalist | Geomancy<br>r7 c4 | [Cave In](https://db.exil.es/spell/500615) |  | 24s | 18% mana | Instant | Cave in your target, interrupting spellcasting and preventing any spell in that school from being cast for 4 seconds. Successfully interrupt… |
| Runemaster | all | [Ley Lock](https://db.exil.es/spell/800995) |  | 6s | 16% mana | 0.5s | Interrupt your target's spellcasting, preventing any spell in that school from being cast for 2.5 sec. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | all (tree)<br>r0 c4 | [Jawbreaker](https://db.exil.es/spell/802792) |  | 14s | 30 energy | Instant | Attempt to break an enemy's jaw, interrupting them and preventing any spell from that school from being cast for 4 seconds. |
| Felsworn | Infernal<br>r5 c1 | [Felbreak](https://db.exil.es/spell/800203) |  | 18s | 10 energy | 0.5s | Interrupt a spell from being cast, preventing the target from casting spells of that school for 3 seconds and draining mana from the target … |
| Witch Hunter | Black Knight<br>r5 c2 | [Guard Strike](https://db.exil.es/spell/804432) |  | 18s | 100 rage | Instant | Bash an enemy with your weapon's hilt, interrupting them and preventing any spell from that school of magic from being cast for 3 seconds. |
| Stormbringer | all | [Gust of Wind](https://db.exil.es/spell/500932) |  | 35s | 37% mana | Instant | Send forth a gust of wind in a frontal cone, knocking enemies back and interrupting all enemies current spell cast, preventing any spell fro… |
| Stormbringer | Maelstrom<br>r4 c7 | [Mystic Thunder](https://db.exil.es/spell/504846) |  | 30s | 15% mana | Instant | Interrupt the target's current spell cast and then mark them for 5 seconds. If they cast again while marked they are silenced for 3 seconds. |
| Knight of Xoroth | all | [Hellgaze](https://db.exil.es/spell/560471) |  | 15s | — | Instant | Interrupts spellcasting and prevents any spell from that school from being cast for 4 sec. |
| Guardian | all | [Shield of Denial](https://db.exil.es/spell/704159) |  | 30s | 15 energy | Instant | Toss a shield at an enemy that bounces to up 2 nearby enemies, dealing 155 Physical damage and interrupting their spellcast, preventing any … |
| Bloodmage | Sanguine<br>r3 c3 | [Aneurysm](https://db.exil.es/spell/806099) |  | 24s | 10% health | Instant | Counter the enemy's spellcast, preventing any spell from that school of magic from being cast for 4 seconds. Successfully interrupting an en… |
| Ranger | Brigand<br>r5 c1 | [Throatpunch](https://db.exil.es/spell/500617) |  | 12s | 25 focus | Instant | Punch an enemy in the throat, interrupting the enemy's spellcast, preventing any spell from that school of magic from being cast for 2 secon… |
| Chronomancer | all | [Fray Magic](https://db.exil.es/spell/510236) |  | 30s | 27% mana | Instant | Stop your enemies' timeline, interrupting their spell cast for 4 sec. Successfully interrupting an enemy will additionally silence them for … |
| Necromancer | Rime<br>r4 c0 | [Heartchill](https://db.exil.es/spell/801739) |  | 30s | 19% mana | Instant | Chill an enemy's heart, interrupting their current spell cast. Successfully interrupting a spell also reduces their movement speed and haste… |
| Pyromancer | all | [Spellburn](https://db.exil.es/spell/800808) |  | 25s | 9% mana | Instant | Counters the enemy's spellcast, preventing any spell from that school of magic from being cast for 5 sec. |
| Cultist | Dreadnought<br>r5 c7 | [Crushing Dissonance](https://db.exil.es/spell/804056) |  | 30s | 18% mana | Instant | Unleash a wave of maddening resonance, interrupting the current spell cast of all enemies around you and preventing any spell in that school… |
| Tinker | all | [Build: Rusthound](https://db.exil.es/spell/803437) **(pet — pet bar)** |  | 30s | 10% mana | 6s | Construct a Rusthound to accompany the Tinker until dismissed. — Meltdown: Bite an enemy, interrupting their current spellcast and preventing any spells from being cast from that school for 5 sec and reduces their Fire Resistance and healing received by 20%. |
| Venomancer | all | [Nullifying Toxin](https://db.exil.es/spell/805096) |  | 16s | 9% mana | Instant | Inject an enemy with nullifying toxin, interrupting them and preventing any spell from that school from being cast for 3 sec. |
| Reaper | Harvest<br>r6 c6 | [Siphon Essence](https://db.exil.es/spell/806125) |  | 20s | — | Instant | Attempt to drain an enemies vitals, leeching 22 + 31.03% AP health, interrupting casting and preventing any spell from that school from bein… |
| Primalist | Geomancy<br>r7 c4 | [Cave In](https://db.exil.es/spell/500615) |  | 24s | 18% mana | Instant | Cave in your target, interrupting spellcasting and preventing any spell in that school from being cast for 4 seconds. Successfully interrupt… |
| Runemaster | all | [Ley Lock](https://db.exil.es/spell/800995) |  | 6s | 16% mana | 0.5s | Interrupt your target's spellcasting, preventing any spell in that school from being cast for 2.5 sec. |
```

</details>

**18 across 17 classes.**
None found for: Starcaller, Sun Cleric, Templar, Witch Doctor.

## 2. Silences

`mechanic 9` (SILENCE), or `aura_id 27` (MOD_SILENCE) on a spell whose tooltip never claims to interrupt. Two rows are here for that second reason -- Reaper's `Ghastly Screech` and Witch Hunter's `Subjugate` both carry `effect_id 68` and were filed as interrupts on that alone, while their text describes a silence and nothing else. They keep the effect and are marked **(interrupts too)**; neither class loses its interrupt, since Reaper has `Siphon Essence` and Witch Hunter has `Guard Strike`.

The WORD is not enough on its own, which is why the aura is required: `Fray Magic`, `Mystic Thunder` and `Distracto Shot` all mention silencing and all three interrupt FIRST, silencing as a rider. They stay under Interrupts.

A silence stops the NEXT cast and locks casting for a duration. Several also state that they interrupt non-player spellcasting, which makes them the best interrupt substitute available -- those are marked **(int)**. Only rows with a cost or a cooldown are listed; a silence with neither is a component or a talent.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | Shadowhunting<br>r6 c7 | [Spirit Shock](https://db.exil.es/spell/807743) **(int)** |  | 28s | 25% mana | Instant | Shock an enemy's spirit, silencing them for 4 seconds and interrupting non-player spellcasting for 4 seconds. |
| Witch Hunter | all | [Subjugate](https://db.exil.es/spell/500089) **(interrupts too)** |  | 1.5 min | 8% mana | Instant | Silences an enemy and reduces their movement speed by 50% for 4 sec. |
| Knight of Xoroth | all (tree)<br>r0 c2 | [Chainwhip](https://db.exil.es/spell/800081) |  | 20s | 100 rage | Instant | Swing a chain at an enemy dealing 12 + 35% AP Physical Damage and silencing them for 2 seconds, generating a large amount of threat. If you … |
| Guardian | Vanguard<br>r5 c6 | [Hammer of the Law](https://db.exil.es/spell/704418) |  | 40s | 40 energy | Instant | Smash an enemy and enemies behind them in a line, dealing 95 + 100% AP High Threat Physical Damage and silencing them for 3.5 seconds. |
| Templar | all (tree)<br>r4 c8 | [Interdict](https://db.exil.es/spell/560116) |  | 2 min | — | Instant | Forbid an enemy from sinning, silencing them for 5 seconds. If they are an Undead or Demon they are unable to be healed for the duration. |
| Templar | all | [Atone for your Sins!](https://db.exil.es/spell/561309) ⚠ |  | 2 min | 10 energy | Instant | Forbid an enemy from sinning, silencing them for 6 sec. If they are an Undead or Demon they are unable to be healed. |
| Bloodmage | Fleshweaver<br>r5 c8 | [Arterial Bind](https://db.exil.es/spell/681077) |  | 1.5 min | 15% health | Instant | Place a pool of blood on the ground beneath enemies and allies, healing allies for 203 + 33% healing every 1 sec and silencing all enemies f… |
| Tinker | all | [Anti-Magic Grenades](https://db.exil.es/spell/804861) |  | 2 min | 10% mana | Instant | Toss grenades that dispel up to 3 benefical magic effects and silences all enemies within 12 yds for 4 sec. |
| Reaper | all (tree)<br>r5 c1 | [Ghastly Screech](https://db.exil.es/spell/806146) **(interrupts too)** |  | 1.5 min | 200 runic power | Instant | Screech with ghastly intent, silencing all enemies within 8 yds for 4 seconds, and dealing 90 + 25% AP Shadowfrost Damage at the end of the … |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | Shadowhunting<br>r6 c7 | [Spirit Shock](https://db.exil.es/spell/807743) **(int)** |  | 28s | 25% mana | Instant | Shock an enemy's spirit, silencing them for 4 seconds and interrupting non-player spellcasting for 4 seconds. |
| Witch Hunter | all | [Subjugate](https://db.exil.es/spell/500089) **(interrupts too)** |  | 1.5 min | 8% mana | Instant | Silences an enemy and reduces their movement speed by 50% for 4 sec. |
| Knight of Xoroth | all (tree)<br>r0 c2 | [Chainwhip](https://db.exil.es/spell/800081) |  | 20s | 100 rage | Instant | Swing a chain at an enemy dealing 12 + 35% AP Physical Damage and silencing them for 2 seconds, generating a large amount of threat. If you … |
| Guardian | Vanguard<br>r5 c6 | [Hammer of the Law](https://db.exil.es/spell/704418) |  | 40s | 40 energy | Instant | Smash an enemy and enemies behind them in a line, dealing 95 + 100% AP High Threat Physical Damage and silencing them for 3.5 seconds. |
| Templar | all (tree)<br>r4 c8 | [Interdict](https://db.exil.es/spell/560116) |  | 2 min | — | Instant | Forbid an enemy from sinning, silencing them for 5 seconds. If they are an Undead or Demon they are unable to be healed for the duration. |
| Templar | all | [Atone for your Sins!](https://db.exil.es/spell/561309) ⚠ |  | 2 min | 10 energy | Instant | Forbid an enemy from sinning, silencing them for 6 sec. If they are an Undead or Demon they are unable to be healed. |
| Bloodmage | Fleshweaver<br>r5 c8 | [Arterial Bind](https://db.exil.es/spell/681077) |  | 1.5 min | 15% health | Instant | Place a pool of blood on the ground beneath enemies and allies, healing allies for 203 + 33% healing every 1 sec and silencing all enemies f… |
| Tinker | all | [Anti-Magic Grenades](https://db.exil.es/spell/804861) |  | 2 min | 10% mana | Instant | Toss grenades that dispel up to 3 benefical magic effects and silences all enemies within 12 yds for 4 sec. |
| Reaper | all (tree)<br>r5 c1 | [Ghastly Screech](https://db.exil.es/spell/806146) **(interrupts too)** |  | 1.5 min | 200 runic power | Instant | Screech with ghastly intent, silencing all enemies within 8 yds for 4 seconds, and dealing 90 + 25% AP Shadowfrost Damage at the end of the … |
```

</details>

**9 across 8 classes.**
None found for: Barbarian, Chronomancer, Cultist, Felsworn, Necromancer, Primalist, Pyromancer, Ranger, Runemaster, Starcaller, Stormbringer, Sun Cleric, Venomancer.

## 3. Stuns

`mechanic 12` (STUN). **A stun is not an interrupt.** Most raid bosses are stun-immune, so treat these as trash and add tools, not as a cast-stopping plan. Several carry an "interrupts non-player spellcasting" clause and are marked **(int)** -- that clause is worth exactly as much as the stun landing, which on a boss is usually nothing.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | all | [Headbutt](https://db.exil.es/spell/520523) |  | 40s | 20% energy | Instant | Savagely headbutt an enemy, dealing 48 Physical damage, knocking them down briefly and stunning them for 4 sec. |
| Witch Hunter | Inquisition<br>r4 c6 | [Darkslayer's Lantern](https://db.exil.es/spell/802139) |  | 2 min | 30% mana | Instant | Empower a lantern with your Flames of Sin and let it shine, dealing 441 + 15% AP Fire Damage and stunning all enemies within 5 yds for 5 sec… |
| Knight of Xoroth | all (tree)<br>r0 c6 | [Chains of Malice](https://db.exil.es/spell/803185) |  | 1.5 min | — | Instant | Lock an enemy down with magical chains, stunning them and dragging them with you for 5 seconds. Every 1 sec, the enemy will suffer 48 Physic… |
| Guardian | all | [Battle Rush](https://db.exil.es/spell/802197) |  | 30s | — | Instant | Charge an enemy, dealing 21.714 Physical damage and stunning them for 1 sec. |
| Bloodmage | all | [Shadow Missile](https://db.exil.es/spell/536273) |  | 24s | — | Instant | Sends a shadowy bolt at the enemy, causing 65 to 66 Shadow damage and stunning them for 3 sec. |
| Bloodmage | all | [Pursuit](https://db.exil.es/spell/802869) **!** |  | 1.5 min | — | Instant | Requires Cursed Form Appear behind an enemy, dealing 411 Physical Damage, stunning the target for 4 sec, and reducing all damage taken by 20… |
| Ranger | all | [Eternal Knockdown](https://db.exil.es/spell/520758) |  | 25s | — | Instant | Knock an enemy down, dealing 48 Physical Damage and stunning them for 168 hour. For the duration, enemies take 0% increased damage from Assa… |
| Ranger | all | [Bushwhack](https://db.exil.es/spell/557333) ⚠ |  | none | 60 focus | Instant | Appear behind your target from the shadows, stunning them for 4 sec. |
| Cultist | all | [Summon: Mindbender](https://db.exil.es/spell/803062) **(pet — pet bar)** |  | 1.5 min | 40% mana | 1.5s | Summons a Mindbender to aid you in battle until dismissed. This minion excels at supporting allies and can periodically heal allies within 40 yds. — Facehug: The Mindbender teleports to an enemy and channels on them for up to 3 sec, Stunning the target for the… |
| Sun Cleric | all (tree)<br>r5 c2 | [Glare](https://db.exil.es/spell/805583) |  | 2 min | 20% mana | 1.5s | Flash powerful light that deals 168 + 27.41% SP Holy Damage and stuns enemies within 8 yds for 5 seconds. |
| Tinker | Mechanics<br>r4 c7 | [Build: Scrapmaw](https://db.exil.es/spell/500242) **(pet — pet bar)** ⚠ |  | 30s | 15% mana | 6s | Build a Scrapmaw to accompany the Tinker until dismissed. — Drill Smash: Repeatedly drill into an enemy, dealing 125 Physical Damage, repeating every 1 sec and stunning them for 4 sec. |
| Tinker | all | [Vanguard X-173: Onslaught](https://db.exil.es/spell/801828) |  | 20s | 30 energy | Instant | Causes 216 to 219 Physical Damage to enemies in a 15yd frontal cone and stunning enemies hit for 3 sec. |
| Venomancer | all | [Poison Eruption](https://db.exil.es/spell/520232) **!** |  | 2 min | 8% mana | Instant | Requires Scorpid Form Erupt in a poisonous frenzy, leeching 185 health and stunning enemies within 8 yds for 5 sec. |
| Primalist | Mountain King<br>r3 c4 | [Mountain Hammer](https://db.exil.es/spell/681130) |  | ≥1 min | 200 rage | Instant | Throw a hammer at an enemy dealing 67 + 35.5% nature SP + 15.5% AP Physical Damage and stunning them for 5 seconds. |
| Primalist | all | [Monolith Smash](https://db.exil.es/spell/991349) **(int)** |  | 30s | 3% mana | 5s | Stuns an enemy for 3 sec and Interrupts non-player spellcasting for 3 sec. |
| Runemaster | all (tree)<br>r0 c4 | [Ice Rune](https://db.exil.es/spell/524930) |  | 1 min | 12% mana | Instant | Requires Frozen Target Unleash a frost rune at an enemy, stunning them for 4 sec. Affected enemies are considered Frozen. |
| Runemaster | all | [Everfrost Scroll](https://db.exil.es/spell/801090) |  | 1 min | 5% mana | Instant | Stun an enemy target for 3.5 sec, increasing Frost damage they take from you by 20% for the duration. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | all | [Headbutt](https://db.exil.es/spell/520523) |  | 40s | 20% energy | Instant | Savagely headbutt an enemy, dealing 48 Physical damage, knocking them down briefly and stunning them for 4 sec. |
| Witch Hunter | Inquisition<br>r4 c6 | [Darkslayer's Lantern](https://db.exil.es/spell/802139) |  | 2 min | 30% mana | Instant | Empower a lantern with your Flames of Sin and let it shine, dealing 441 + 15% AP Fire Damage and stunning all enemies within 5 yds for 5 sec… |
| Knight of Xoroth | all (tree)<br>r0 c6 | [Chains of Malice](https://db.exil.es/spell/803185) |  | 1.5 min | — | Instant | Lock an enemy down with magical chains, stunning them and dragging them with you for 5 seconds. Every 1 sec, the enemy will suffer 48 Physic… |
| Guardian | all | [Battle Rush](https://db.exil.es/spell/802197) |  | 30s | — | Instant | Charge an enemy, dealing 21.714 Physical damage and stunning them for 1 sec. |
| Bloodmage | all | [Shadow Missile](https://db.exil.es/spell/536273) |  | 24s | — | Instant | Sends a shadowy bolt at the enemy, causing 65 to 66 Shadow damage and stunning them for 3 sec. |
| Bloodmage | all | [Pursuit](https://db.exil.es/spell/802869) **!** |  | 1.5 min | — | Instant | Requires Cursed Form Appear behind an enemy, dealing 411 Physical Damage, stunning the target for 4 sec, and reducing all damage taken by 20… |
| Ranger | all | [Eternal Knockdown](https://db.exil.es/spell/520758) |  | 25s | — | Instant | Knock an enemy down, dealing 48 Physical Damage and stunning them for 168 hour. For the duration, enemies take 0% increased damage from Assa… |
| Ranger | all | [Bushwhack](https://db.exil.es/spell/557333) ⚠ |  | none | 60 focus | Instant | Appear behind your target from the shadows, stunning them for 4 sec. |
| Cultist | all | [Summon: Mindbender](https://db.exil.es/spell/803062) **(pet — pet bar)** |  | 1.5 min | 40% mana | 1.5s | Summons a Mindbender to aid you in battle until dismissed. This minion excels at supporting allies and can periodically heal allies within 40 yds. — Facehug: The Mindbender teleports to an enemy and channels on them for up to 3 sec, Stunning the target for the… |
| Sun Cleric | all (tree)<br>r5 c2 | [Glare](https://db.exil.es/spell/805583) |  | 2 min | 20% mana | 1.5s | Flash powerful light that deals 168 + 27.41% SP Holy Damage and stuns enemies within 8 yds for 5 seconds. |
| Tinker | Mechanics<br>r4 c7 | [Build: Scrapmaw](https://db.exil.es/spell/500242) **(pet — pet bar)** ⚠ |  | 30s | 15% mana | 6s | Build a Scrapmaw to accompany the Tinker until dismissed. — Drill Smash: Repeatedly drill into an enemy, dealing 125 Physical Damage, repeating every 1 sec and stunning them for 4 sec. |
| Tinker | all | [Vanguard X-173: Onslaught](https://db.exil.es/spell/801828) |  | 20s | 30 energy | Instant | Causes 216 to 219 Physical Damage to enemies in a 15yd frontal cone and stunning enemies hit for 3 sec. |
| Venomancer | all | [Poison Eruption](https://db.exil.es/spell/520232) **!** |  | 2 min | 8% mana | Instant | Requires Scorpid Form Erupt in a poisonous frenzy, leeching 185 health and stunning enemies within 8 yds for 5 sec. |
| Primalist | Mountain King<br>r3 c4 | [Mountain Hammer](https://db.exil.es/spell/681130) |  | ≥1 min | 200 rage | Instant | Throw a hammer at an enemy dealing 67 + 35.5% nature SP + 15.5% AP Physical Damage and stunning them for 5 seconds. |
| Primalist | all | [Monolith Smash](https://db.exil.es/spell/991349) **(int)** |  | 30s | 3% mana | 5s | Stuns an enemy for 3 sec and Interrupts non-player spellcasting for 3 sec. |
| Runemaster | all (tree)<br>r0 c4 | [Ice Rune](https://db.exil.es/spell/524930) |  | 1 min | 12% mana | Instant | Requires Frozen Target Unleash a frost rune at an enemy, stunning them for 4 sec. Affected enemies are considered Frozen. |
| Runemaster | all | [Everfrost Scroll](https://db.exil.es/spell/801090) |  | 1 min | 5% mana | Instant | Stun an enemy target for 3.5 sec, increasing Frost damage they take from you by 20% for the duration. |
```

</details>

**17 across 12 classes.**
None found for: Chronomancer, Felsworn, Necromancer, Pyromancer, Reaper, Starcaller, Stormbringer, Templar, Witch Doctor.

## 4. Roots

`mechanic 7` (ROOT) or `13` (FREEZE). Snares and slows (`mechanic 11`) are deliberately NOT here -- a slow is not a root, and folding them in would triple the table with abilities that do not hold anything in place.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | all | [Bwonsamdi's Judgement](https://db.exil.es/spell/525386) |  | none | 10% mana | Instant | Deals 85 Shadow Damage to an enemy and roots them for 2 sec. |
| Stormbringer | all | [Exhale](https://db.exil.es/spell/801846) **!** |  | 40s | 11% mana | Instant | Exhale a gust of wind in a 15 yd cone in front of you, dealing 109.2 Nature Damage and rooting up to 0 enemies in place for 8 sec. Damage ca… |
| Knight of Xoroth | all | [Hellhaul](https://db.exil.es/spell/503142) |  | 3 min | — | Instant | You bind an enemy target with magical Hellfire Chains, rooting them and dragging them with you for 5 sec. Every 0.25 sec for the duration th… |
| Guardian | all (tree)<br>r0 c1 | [Net Throw](https://db.exil.es/spell/802304) |  | 15s | 15 energy | Instant | Toss a weighted net at an enemy that roots them for 4 seconds. While active, the target cannot dodge attacks. |
| Ranger | Farstrider<br>r8 c6 | [Whipvine Arrow](https://db.exil.es/spell/806342) **!** |  | 1 min | 25 focus | 1.7s | Launch an arrow with magical vines attached to it at your target, dealing 78 + 33% ranged AP Nature Damage and rooting them for 40 seconds (… |
| Chronomancer | all (tree)<br>r0 c4 | [Clasp of Infinity](https://db.exil.es/spell/805847) ⚠ |  | 20s | 23% mana | Instant | Conjure a magical binding upon an enemy that bounces to nearby enemies, rooting them in place for 4 seconds. |
| Necromancer | all | [Cryo Freeze](https://db.exil.es/spell/680363) |  | 20s | 7% mana | Instant | Unleashes a frost explosion at teleportaion location and freezes all enemies nearby. |
| Necromancer | all | [Black Ice](https://db.exil.es/spell/801746) |  | 30s | 10% mana | Instant | A ring of ice erupts from the target, rooting enemies around them in ice for 8 sec, and applying Deathchill. Damage caused may interrupt the… |
| Pyromancer | all | [Cindergrip](https://db.exil.es/spell/805476) |  | none | 19% mana | 1.5s | Raise a lava crag from beneath an enemy, rooting them in place, dealing 28 Fire damage every 3 sec for 12 sec (8 sec vs players). Damage cau… |
| Tinker | all | [Hydraulic Charge](https://db.exil.es/spell/800582) **!** |  | 15s | 6% mana | Instant | Charge an enemy with your Clockwork Assistant and strike as one, each dealing 362 Physical Damage and rooting enemies in place for 2 sec. |
| Venomancer | all (tree)<br>r3 c4 | [Spindlebind](https://db.exil.es/spell/800887) ⚠ |  | 16s | 30 energy | Instant | Emit webs at all enemies in a 10 yd cone behind you, rooting them for 4 seconds, and unleashing a beetle on the trapped enemy from below, in… |
| Venomancer | all | [Venocannon](https://db.exil.es/spell/804967) |  | 1 min | — | Instant | Burst out of your burrow, rooting yourself in place for 0.001 sec. While active, all spells have 15 yd of additional range, and the cast tim… |
| Primalist | all | [Swoop](https://db.exil.es/spell/806546) |  | 30s | — | Channel 3s | Swoop an enemy, flying to their position and knocking them down. Rooting the target for 3 sec, disabling movement abilities. |
| Runemaster | all | [Glacial Rune](https://db.exil.es/spell/805730) ⚠ |  | 20s | 9% mana | Instant | Place a rune at the target location that explodes after 1 sec with frigid magic, dealing 362.824 Frost Damage to enemies inside and freezing… |
| Runemaster | all | [Cryobrand](https://db.exil.es/spell/807822) ⚠ |  | none | 4% mana | Instant | Blast an enemy with frost magic, freezing them in place for 40 sec (8 sec vs players). Can only affect 1 enemy at a time. Does not break ste… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | all | [Bwonsamdi's Judgement](https://db.exil.es/spell/525386) |  | none | 10% mana | Instant | Deals 85 Shadow Damage to an enemy and roots them for 2 sec. |
| Stormbringer | all | [Exhale](https://db.exil.es/spell/801846) **!** |  | 40s | 11% mana | Instant | Exhale a gust of wind in a 15 yd cone in front of you, dealing 109.2 Nature Damage and rooting up to 0 enemies in place for 8 sec. Damage ca… |
| Knight of Xoroth | all | [Hellhaul](https://db.exil.es/spell/503142) |  | 3 min | — | Instant | You bind an enemy target with magical Hellfire Chains, rooting them and dragging them with you for 5 sec. Every 0.25 sec for the duration th… |
| Guardian | all (tree)<br>r0 c1 | [Net Throw](https://db.exil.es/spell/802304) |  | 15s | 15 energy | Instant | Toss a weighted net at an enemy that roots them for 4 seconds. While active, the target cannot dodge attacks. |
| Ranger | Farstrider<br>r8 c6 | [Whipvine Arrow](https://db.exil.es/spell/806342) **!** |  | 1 min | 25 focus | 1.7s | Launch an arrow with magical vines attached to it at your target, dealing 78 + 33% ranged AP Nature Damage and rooting them for 40 seconds (… |
| Chronomancer | all (tree)<br>r0 c4 | [Clasp of Infinity](https://db.exil.es/spell/805847) ⚠ |  | 20s | 23% mana | Instant | Conjure a magical binding upon an enemy that bounces to nearby enemies, rooting them in place for 4 seconds. |
| Necromancer | all | [Cryo Freeze](https://db.exil.es/spell/680363) |  | 20s | 7% mana | Instant | Unleashes a frost explosion at teleportaion location and freezes all enemies nearby. |
| Necromancer | all | [Black Ice](https://db.exil.es/spell/801746) |  | 30s | 10% mana | Instant | A ring of ice erupts from the target, rooting enemies around them in ice for 8 sec, and applying Deathchill. Damage caused may interrupt the… |
| Pyromancer | all | [Cindergrip](https://db.exil.es/spell/805476) |  | none | 19% mana | 1.5s | Raise a lava crag from beneath an enemy, rooting them in place, dealing 28 Fire damage every 3 sec for 12 sec (8 sec vs players). Damage cau… |
| Tinker | all | [Hydraulic Charge](https://db.exil.es/spell/800582) **!** |  | 15s | 6% mana | Instant | Charge an enemy with your Clockwork Assistant and strike as one, each dealing 362 Physical Damage and rooting enemies in place for 2 sec. |
| Venomancer | all (tree)<br>r3 c4 | [Spindlebind](https://db.exil.es/spell/800887) ⚠ |  | 16s | 30 energy | Instant | Emit webs at all enemies in a 10 yd cone behind you, rooting them for 4 seconds, and unleashing a beetle on the trapped enemy from below, in… |
| Venomancer | all | [Venocannon](https://db.exil.es/spell/804967) |  | 1 min | — | Instant | Burst out of your burrow, rooting yourself in place for 0.001 sec. While active, all spells have 15 yd of additional range, and the cast tim… |
| Primalist | all | [Swoop](https://db.exil.es/spell/806546) |  | 30s | — | Channel 3s | Swoop an enemy, flying to their position and knocking them down. Rooting the target for 3 sec, disabling movement abilities. |
| Runemaster | all | [Glacial Rune](https://db.exil.es/spell/805730) ⚠ |  | 20s | 9% mana | Instant | Place a rune at the target location that explodes after 1 sec with frigid magic, dealing 362.824 Frost Damage to enemies inside and freezing… |
| Runemaster | all | [Cryobrand](https://db.exil.es/spell/807822) ⚠ |  | none | 4% mana | Instant | Blast an enemy with frost magic, freezing them in place for 40 sec (8 sec vs players). Can only affect 1 enemy at a time. Does not break ste… |
```

</details>

**15 across 12 classes.**
None found for: Barbarian, Bloodmage, Cultist, Felsworn, Reaper, Starcaller, Sun Cleric, Templar, Witch Hunter.

## 5. Battle Rezzes

`effect_id 18` (RESURRECT) or `113` (RESURRECT_NEW), **usable in combat, on a player**. Both effect ids are in use -- matching only 18 finds 2 spells and misses almost everything.

Out-of-combat resurrects are NOT here: a res you cannot cast mid-pull is not a raid cooldown. That excludes eleven, including Chronomancer's `Resynchronize` (30 min, whole party, but "cannot be used in combat") and every 8-10 sec cast. Necromancer's `Reanimate` is excluded too -- it raises a CORPSE as a temporary pet, not a player.

Reagent cost is tracked per ability rather than boss usability: a battle rez targets an ally, so boss immunity is meaningless, while the reagent is the thing that stops you casting it.

| Class | Spec | Ability | Reagent Required | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Templar | all | [Spiritual Ascension](https://db.exil.es/spell/500688) | none | 5 min | — | 2s | Call an ally's spirit back to their body, bringing them back to life. Usable while in combat. |
| Necromancer | all | [Call of The Scourge](https://db.exil.es/spell/801792) | none | 10 min | 68% mana | 2s | Bring a dead ally back to life with 70 health and 135 mana. Can be used in combat. |
| Pyromancer | all | [Reborn from Ash](https://db.exil.es/spell/804231) | Elemental Fire | 10 min | — | 2s | Returns a dead ally to life with 400 health and 635 mana, can also be used on self while dead. Can be used in combat. |
| Starcaller | all | [Tidal Rebirth](https://db.exil.es/spell/801793) | none | 10 min | 75% mana | 2s | Instantly brings a dead ally back to life with 400 health and 635 mana. This spell is usable in combat. |
| Venomancer | all | [Spawn](https://db.exil.es/spell/805568) | none | 10 min | 20% mana | 2s | Bring a dead ally back to life with 400 health and 635 mana. Can be used in combat. Not usable in arena. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Reagent Required | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Templar | all | [Spiritual Ascension](https://db.exil.es/spell/500688) | none | 5 min | — | 2s | Call an ally's spirit back to their body, bringing them back to life. Usable while in combat. |
| Necromancer | all | [Call of The Scourge](https://db.exil.es/spell/801792) | none | 10 min | 68% mana | 2s | Bring a dead ally back to life with 70 health and 135 mana. Can be used in combat. |
| Pyromancer | all | [Reborn from Ash](https://db.exil.es/spell/804231) | Elemental Fire | 10 min | — | 2s | Returns a dead ally to life with 400 health and 635 mana, can also be used on self while dead. Can be used in combat. |
| Starcaller | all | [Tidal Rebirth](https://db.exil.es/spell/801793) | none | 10 min | 75% mana | 2s | Instantly brings a dead ally back to life with 400 health and 635 mana. This spell is usable in combat. |
| Venomancer | all | [Spawn](https://db.exil.es/spell/805568) | none | 10 min | 20% mana | 2s | Bring a dead ally back to life with 400 health and 635 mana. Can be used in combat. Not usable in arena. |
```

</details>

**5 across 5 classes.**
None found for: Barbarian, Bloodmage, Chronomancer, Cultist, Felsworn, Guardian, Knight of Xoroth, Primalist, Ranger, Reaper, Runemaster, Stormbringer, Sun Cleric, Tinker, Witch Doctor, Witch Hunter.

## 6. Purges

`effect_id 38` (DISPEL) where the tooltip names a *beneficial* effect on an *enemy*. Target flags alone are unreliable -- **Show of Force** is `target_a 6` and reads "on a friendly target".

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Templar | all | [Righteous Reprimand](https://db.exil.es/spell/572308) **!** |  | 10s | 6% mana | Instant | Removes 1 beneficial magic effect from an enemy. |
| Chronomancer | Time<br>r6 c4 | [Continuum Restoration](https://db.exil.es/spell/801271) ⚠ |  | 1.5 min | 60% mana | 1.5s | Restore the continuum at target location for all allies and enemies within 15 yds, removing all beneficial magic effects from enemies and ha… |
| Cultist | Godblade<br>r3 c4 | [Netherstrike](https://db.exil.es/spell/806222) |  | 6s | 10% mana | Instant | Generates 10 Insanity Strike an enemy quickly for 125% Weapon Damage plus 40 Shadow Damage, purging 1 beneficial magic effect from them. Onl… |
| Sun Cleric | all | [Gavel of Wrath](https://db.exil.es/spell/800617) |  | 5s | 10% mana | Instant | Smash an enemy for 100% Weapon Damage plus 45 and dispel 1 beneficial magic effect from them. Shares a cooldown with other Gavels. |
| Reaper | all | [Soul Shear](https://db.exil.es/spell/520862) |  | 16s | — | Instant | Purge an enemy's soul, removing 2 beneficial magic effects from them. |
| Reaper | all | [Reap Magic](https://db.exil.es/spell/704258) |  | none | — | Instant | Steals 1 beneficial Magic Effect from an enemy. If you successfuly steal an effect, you also siphon 160 Health from the target as Shadow Dam… |
| Primalist | all | [Neutralizing Touch](https://db.exil.es/spell/572307) **!** |  | 10s | — | Instant | Removes 1 beneficial magic effect from an enemy. |
| Runemaster | all | [Resonance Rune](https://db.exil.es/spell/803679) |  | 1 min | 30% mana | 1.5s | Place an arcane rune on the ground that dispels 3 harmful magic effects from allies in the radius, and purges 3 beneficial magic effects fro… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Templar | all | [Righteous Reprimand](https://db.exil.es/spell/572308) **!** |  | 10s | 6% mana | Instant | Removes 1 beneficial magic effect from an enemy. |
| Chronomancer | Time<br>r6 c4 | [Continuum Restoration](https://db.exil.es/spell/801271) ⚠ |  | 1.5 min | 60% mana | 1.5s | Restore the continuum at target location for all allies and enemies within 15 yds, removing all beneficial magic effects from enemies and ha… |
| Cultist | Godblade<br>r3 c4 | [Netherstrike](https://db.exil.es/spell/806222) |  | 6s | 10% mana | Instant | Generates 10 Insanity Strike an enemy quickly for 125% Weapon Damage plus 40 Shadow Damage, purging 1 beneficial magic effect from them. Onl… |
| Sun Cleric | all | [Gavel of Wrath](https://db.exil.es/spell/800617) |  | 5s | 10% mana | Instant | Smash an enemy for 100% Weapon Damage plus 45 and dispel 1 beneficial magic effect from them. Shares a cooldown with other Gavels. |
| Reaper | all | [Soul Shear](https://db.exil.es/spell/520862) |  | 16s | — | Instant | Purge an enemy's soul, removing 2 beneficial magic effects from them. |
| Reaper | all | [Reap Magic](https://db.exil.es/spell/704258) |  | none | — | Instant | Steals 1 beneficial Magic Effect from an enemy. If you successfuly steal an effect, you also siphon 160 Health from the target as Shadow Dam… |
| Primalist | all | [Neutralizing Touch](https://db.exil.es/spell/572307) **!** |  | 10s | — | Instant | Removes 1 beneficial magic effect from an enemy. |
| Runemaster | all | [Resonance Rune](https://db.exil.es/spell/803679) |  | 1 min | 30% mana | 1.5s | Place an arcane rune on the ground that dispels 3 harmful magic effects from allies in the radius, and purges 3 beneficial magic effects fro… |
```

</details>

**8 across 7 classes.**
None found for: Barbarian, Bloodmage, Felsworn, Guardian, Knight of Xoroth, Necromancer, Pyromancer, Ranger, Starcaller, Stormbringer, Tinker, Venomancer, Witch Doctor, Witch Hunter.

## 7. Spellsteals

`effect_id 126` -- STEAL_BENEFICIAL_BUFF.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Felsworn | all | [Consume Magic](https://db.exil.es/spell/800353) |  | none | 30 energy | Instant | Steal 1 beneficial magic effects from an enemy. If you successfully steal an effect, you deal 8 Shadow Damage to the enemy. |
| Bloodmage | all | [Siphon](https://db.exil.es/spell/803327) **!** |  | 6s | — | Instant | Steal 2 beneficial magic effects from an enemy. |
| Runemaster | all | [Leyfeed](https://db.exil.es/spell/520269) ⚠ |  | none | 20% mana | 1s | Feed off the latent magic of an enemy, stealing 2 beneficial magic effects from them. Usable while moving. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Felsworn | all | [Consume Magic](https://db.exil.es/spell/800353) |  | none | 30 energy | Instant | Steal 1 beneficial magic effects from an enemy. If you successfully steal an effect, you deal 8 Shadow Damage to the enemy. |
| Bloodmage | all | [Siphon](https://db.exil.es/spell/803327) **!** |  | 6s | — | Instant | Steal 2 beneficial magic effects from an enemy. |
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
| Witch Hunter | all | [Sedative Shot](https://db.exil.es/spell/572406) ⚠ |  | none | 35 focus | Instant | Shoot an arrow at an enemy with sedative toxins, dealing 50% Ranged Weapon Damage as Nature Damage and removing 1 enrage effect from them. |
| Stormbringer | all | [Calm the Storm](https://db.exil.es/spell/572303) |  | none | Depletes 10 | Instant | Depletes 10 Static Calm an enemy, removing 1 enrage effect from them. |
| Venomancer | all | [Myotoxin](https://db.exil.es/spell/572304) |  | 10s | 10% mana | Instant | Inject an enemy with myotoxins, removing 1 enrage effect, repeating every 4 sec for 20 sec. |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Hunter | all | [Purge Evil](https://db.exil.es/spell/572306) |  | 20s | 25% mana | Instant | Purge the evil from an enemy, removing all enrage effects from them. |
| Witch Hunter | all | [Sedative Shot](https://db.exil.es/spell/572406) ⚠ |  | none | 35 focus | Instant | Shoot an arrow at an enemy with sedative toxins, dealing 50% Ranged Weapon Damage as Nature Damage and removing 1 enrage effect from them. |
| Stormbringer | all | [Calm the Storm](https://db.exil.es/spell/572303) |  | none | Depletes 10 | Instant | Depletes 10 Static Calm an enemy, removing 1 enrage effect from them. |
| Venomancer | all | [Myotoxin](https://db.exil.es/spell/572304) |  | 10s | 10% mana | Instant | Inject an enemy with myotoxins, removing 1 enrage effect, repeating every 4 sec for 20 sec. |
```

</details>

**4 across 3 classes.**
None found for: Barbarian, Bloodmage, Chronomancer, Cultist, Felsworn, Guardian, Knight of Xoroth, Necromancer, Primalist, Pyromancer, Ranger, Reaper, Runemaster, Starcaller, Sun Cleric, Templar, Tinker, Witch Doctor.

## 9. Raid damage reduction — active

`aura_id 87` (MOD_DAMAGE_PERCENT_TAKEN), `229` (AoE damage taken) at a NEGATIVE magnitude, or `81` (SPLIT_DAMAGE_PCT), where the tooltip agrees AND the ability has a cooldown or a cost -- i.e. something you press.

**Sign matters.** Witch Hunter's `Set Bounty` carries aura 87 on an enemy at *+3* and reads "increasing all Physical damage they take" -- an amplifier reads almost identically to a mitigation and is the opposite of one, so only negative magnitudes count.

**Damage sharing is damage reduction** for whoever is being hit, so `aura 81` is in: Reaper's `Reaper's Pact`, Witch Hunter's `Gaze of the Black Knight`, Barbarian's `Cheers!`. Chronomancer's `The Vast Infinite` shares through an absorb aura (`69`) instead and is admitted on share wording alone, which is why the ten plain group absorbs are NOT here.

**Six phrasings, one mechanic.** An earlier rule demanded the literal words *damage taken* and dropped Runemaster's `Guarding Rune` -- aura 87, -40%, 2 min, "allies" in the text -- because the server wrote "take -40% reduced Magic Damage". It dropped eight more the same way.

**The group can live in the effect, not the prose.** Cultist's `Nether Shield` is a 10 yd ground aura at -40% magic damage taken whose tooltip says only "while inside", naming no party, raid or ally.

Still missed on purpose: roughly fourteen abilities deliver mitigation through a SUMMON or a triggered child spell, so the aura is not in the parent's effects at all and no effect-id rule can reach them. Matching those on text alone pulls in a placeholder tooltip -- "Reduces all party and raid member's magic damage taken by 0%" -- that at least five unrelated spells share verbatim. They need a hand-curated list, the way `spell-observed.json` works.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | Ancestry<br>r4 c6 | [Cheers!](https://db.exil.es/spell/805810) |  | 3s | 20 energy | Instant | Designate an ally as your drinking partner for 30 minutes, reducing all damage they take by -5%, and causing 10% of all damage they take to … |
| Felsworn | Tyrant<br>r8 c6 | [Infernal Whipcrack](https://db.exil.es/spell/805243) |  | 1.5 min | — | Instant | Enrage up to 8 allies within 20 yds, reducing their damage taken by -15% and increasing their haste by 10% for 10 seconds. |
| Witch Hunter | Black Knight<br>r9 c4 | [Gaze of the Black Knight](https://db.exil.es/spell/802138) ⚠ |  | 3 min | 27% mana | Instant | Apply a dark shield to yourself, absorbing 2255 + 30% Stamina + 11% AP damage and then gaze upon your party members, causing 25% of the dama… |
| Guardian | Vanguard<br>r9 c4 | [Bastion](https://db.exil.es/spell/802283) |  | 5 min | 40 energy | Instant | Raise your shield and lead your allies within 12 yds, reducing their damage taken by -40% for 10 seconds. |
| Guardian | all | [Emperor's Decree](https://db.exil.es/spell/806139) |  | 30s | 25 energy | Instant | Empowers an ally for 15 sec, reducing all damage they take by 35% and increasing all healing they take by 30%. Grants Motivation to all near… |
| Templar | all | [Grace of Aman'Thul](https://db.exil.es/spell/801477) |  | 20s | 20 energy | Instant | Unleash a defensive Oath Breaker, causing damage taken from melee attacks to heal yourself and allies within 10 yds for 136. Lasts 0 or unti… |
| Chronomancer | all | [Decelerate](https://db.exil.es/spell/572632) |  | none | 32% mana | Instant | Decelerates magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. Lasts 10… |
| Chronomancer | Time<br>r9 c4 | [The Vast Infinite](https://db.exil.es/spell/706083) |  | 5 min | 30% mana | Instant | All party and raid members become one, equally sharing 25% of all damage dealt to them for 10 seconds, up to a maximum of 100% of their tota… |
| Pyromancer | all | [Lucifron's Lagniappe](https://db.exil.es/spell/805497) **!** |  | 30s | 10% mana | Instant | Enhance an ally for 30 sec, increasing their spell haste by 10% and reducing all damage taken by 10%. Can only target 1 ally at a time. |
| Cultist | Heretic<br>r2 c4 | [Abyssal Covenant](https://db.exil.es/spell/500751) |  | 5s | 14% mana | Instant | Link yourself to an ally for 30 minutes, transfering 10% of all damage taken by them to you and causing 20% of all damage you deal to be con… |
| Cultist | all | [Whispers of Yogg-Saron](https://db.exil.es/spell/572637) ⚠ |  | none | 27% mana | Instant | Destabilizes magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. |
| Cultist | all | [Nether Shield](https://db.exil.es/spell/680571) **!** |  | 1.5 min | 12% mana | Instant | Envelop a 10 yd area in nether energy, reducing all Magic Damage taken by 40% for 10 sec while inside. |
| Cultist | Heretic<br>r8 c4 | [Hand of Yogg-Saron](https://db.exil.es/spell/704476) |  | 2 min | 18% mana | Instant | Tether yourself to an ally for 15 seconds, increasing all damage they deal and reducing all damage they take by 15%. |
| Cultist | all | [Protection From Light](https://db.exil.es/spell/804065) |  | 30s | 3% mana | Instant | Reduces all Holy Damage and Fire Damage taken by an ally by 40% for 10 sec. While active, the ally is Healed for 24 to 25 every 2 sec. |
| Sun Cleric | Seraphim<br>r9 c4 | [Scroll of Hope](https://db.exil.es/spell/680646) |  | 5 min | 40% mana | Instant | Read from a scroll of hope, reducing Magic Damage taken by party and raid members within 15 yds by -30% for 10 seconds. If any ally falls be… |
| Tinker | all | [Arcane Bionics](https://db.exil.es/spell/541493) |  | none | 8% mana | Instant | Augment a party member with the essence of arcane, decreasing damage taken from spells by up to 3% and healing spells by up to 3%. Lasts 5 m… |
| Tinker | all | [Lesser Med Pack](https://db.exil.es/spell/570150) |  | 2 min | 30% mana | Instant | Heals an ally for [spell:total] over 3 sec. While active, the ally takes 5% less damage from all sources. |
| Tinker | all (tree)<br>r5 c4 | [Kinetic Shield](https://db.exil.es/spell/806224) |  | 5 min | 38% mana | Instant | Create magnetic shields of kinetic energy on an ally target for 10 seconds, reducing damage taken by -35% and making them immune to stun eff… |
| Venomancer | Vizier<br>r8 c2 | [Shadra's Aid](https://db.exil.es/spell/504352) |  | 3 min | 19% mana | Instant | Envelop an ally in Shadra's grace, reducing all damage taken by -20% and causing direct damage taken to restore 3% maximum health for 15 sec… |
| Primalist | all | [Essence of Dispersion](https://db.exil.es/spell/572818) ⚠ |  | none | 20% mana | Instant | Disperses magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. |
| Primalist | all | [Fae Dust](https://db.exil.es/spell/804664) |  | none | 4% mana | Instant | Sprinkle an ally with Fae Dust, increasing their stealth detection and reducing all Nature and Arcane damage they take by 3%. Lasts 15 min. |
| Runemaster | Engravement<br>r5 c4 | [Guarding Rune](https://db.exil.es/spell/500464) |  | 2 min | 23% mana | Instant | Inscribe a defensive rune beneath you in a 10 yd radius, summoning a barrier that causes allies within the radius to take -40% reduced Magic… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | Ancestry<br>r4 c6 | [Cheers!](https://db.exil.es/spell/805810) |  | 3s | 20 energy | Instant | Designate an ally as your drinking partner for 30 minutes, reducing all damage they take by -5%, and causing 10% of all damage they take to … |
| Felsworn | Tyrant<br>r8 c6 | [Infernal Whipcrack](https://db.exil.es/spell/805243) |  | 1.5 min | — | Instant | Enrage up to 8 allies within 20 yds, reducing their damage taken by -15% and increasing their haste by 10% for 10 seconds. |
| Witch Hunter | Black Knight<br>r9 c4 | [Gaze of the Black Knight](https://db.exil.es/spell/802138) ⚠ |  | 3 min | 27% mana | Instant | Apply a dark shield to yourself, absorbing 2255 + 30% Stamina + 11% AP damage and then gaze upon your party members, causing 25% of the dama… |
| Guardian | Vanguard<br>r9 c4 | [Bastion](https://db.exil.es/spell/802283) |  | 5 min | 40 energy | Instant | Raise your shield and lead your allies within 12 yds, reducing their damage taken by -40% for 10 seconds. |
| Guardian | all | [Emperor's Decree](https://db.exil.es/spell/806139) |  | 30s | 25 energy | Instant | Empowers an ally for 15 sec, reducing all damage they take by 35% and increasing all healing they take by 30%. Grants Motivation to all near… |
| Templar | all | [Grace of Aman'Thul](https://db.exil.es/spell/801477) |  | 20s | 20 energy | Instant | Unleash a defensive Oath Breaker, causing damage taken from melee attacks to heal yourself and allies within 10 yds for 136. Lasts 0 or unti… |
| Chronomancer | all | [Decelerate](https://db.exil.es/spell/572632) |  | none | 32% mana | Instant | Decelerates magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. Lasts 10… |
| Chronomancer | Time<br>r9 c4 | [The Vast Infinite](https://db.exil.es/spell/706083) |  | 5 min | 30% mana | Instant | All party and raid members become one, equally sharing 25% of all damage dealt to them for 10 seconds, up to a maximum of 100% of their tota… |
| Pyromancer | all | [Lucifron's Lagniappe](https://db.exil.es/spell/805497) **!** |  | 30s | 10% mana | Instant | Enhance an ally for 30 sec, increasing their spell haste by 10% and reducing all damage taken by 10%. Can only target 1 ally at a time. |
| Cultist | Heretic<br>r2 c4 | [Abyssal Covenant](https://db.exil.es/spell/500751) |  | 5s | 14% mana | Instant | Link yourself to an ally for 30 minutes, transfering 10% of all damage taken by them to you and causing 20% of all damage you deal to be con… |
| Cultist | all | [Whispers of Yogg-Saron](https://db.exil.es/spell/572637) ⚠ |  | none | 27% mana | Instant | Destabilizes magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. |
| Cultist | all | [Nether Shield](https://db.exil.es/spell/680571) **!** |  | 1.5 min | 12% mana | Instant | Envelop a 10 yd area in nether energy, reducing all Magic Damage taken by 40% for 10 sec while inside. |
| Cultist | Heretic<br>r8 c4 | [Hand of Yogg-Saron](https://db.exil.es/spell/704476) |  | 2 min | 18% mana | Instant | Tether yourself to an ally for 15 seconds, increasing all damage they deal and reducing all damage they take by 15%. |
| Cultist | all | [Protection From Light](https://db.exil.es/spell/804065) |  | 30s | 3% mana | Instant | Reduces all Holy Damage and Fire Damage taken by an ally by 40% for 10 sec. While active, the ally is Healed for 24 to 25 every 2 sec. |
| Sun Cleric | Seraphim<br>r9 c4 | [Scroll of Hope](https://db.exil.es/spell/680646) |  | 5 min | 40% mana | Instant | Read from a scroll of hope, reducing Magic Damage taken by party and raid members within 15 yds by -30% for 10 seconds. If any ally falls be… |
| Tinker | all | [Arcane Bionics](https://db.exil.es/spell/541493) |  | none | 8% mana | Instant | Augment a party member with the essence of arcane, decreasing damage taken from spells by up to 3% and healing spells by up to 3%. Lasts 5 m… |
| Tinker | all | [Lesser Med Pack](https://db.exil.es/spell/570150) |  | 2 min | 30% mana | Instant | Heals an ally for [spell:total] over 3 sec. While active, the ally takes 5% less damage from all sources. |
| Tinker | all (tree)<br>r5 c4 | [Kinetic Shield](https://db.exil.es/spell/806224) |  | 5 min | 38% mana | Instant | Create magnetic shields of kinetic energy on an ally target for 10 seconds, reducing damage taken by -35% and making them immune to stun eff… |
| Venomancer | Vizier<br>r8 c2 | [Shadra's Aid](https://db.exil.es/spell/504352) |  | 3 min | 19% mana | Instant | Envelop an ally in Shadra's grace, reducing all damage taken by -20% and causing direct damage taken to restore 3% maximum health for 15 sec… |
| Primalist | all | [Essence of Dispersion](https://db.exil.es/spell/572818) ⚠ |  | none | 20% mana | Instant | Disperses magic used against the targeted party member. Reduces all spell damage taken by 5% and reduces all healing taken by 5%. |
| Primalist | all | [Fae Dust](https://db.exil.es/spell/804664) |  | none | 4% mana | Instant | Sprinkle an ally with Fae Dust, increasing their stealth detection and reducing all Nature and Arcane damage they take by 3%. Lasts 15 min. |
| Runemaster | Engravement<br>r5 c4 | [Guarding Rune](https://db.exil.es/spell/500464) |  | 2 min | 23% mana | Instant | Inscribe a defensive rune beneath you in a 10 yd radius, summoning a barrier that causes allies within the radius to take -40% reduced Magic… |
```

</details>

**22 across 13 classes.**
None found for: Bloodmage, Knight of Xoroth, Necromancer, Ranger, Reaper, Starcaller, Stormbringer, Witch Doctor.

## 9b. Raid damage reduction — passive auras

Same auras, group-scoped, but **no cooldown and no cost**: talents and stances that shape the raid's damage intake without being pressed. Separated because a raid cooldown plan cares about the first list; roster composition cares about this one.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Stormbringer | all | [Summon: Air Elemental](https://db.exil.es/spell/804019) **(pet — passive)** ⚠ |  | none | 75% mana | 5s | Call an Air Elemental to aid you in combat that gains a stack of Invigoration whenever it deals damage. — Cyclonean Protection: Reduces the damage taken from area of effect attacks of party members within 20 yds by 15%. |
| Guardian | Vanguard<br>r6 c6 | [Unscuffable](https://db.exil.es/spell/503837) |  | none | — | Instant | Allies within 30 yds now take -10% less Magic Damage from area of effect attacks. |
| Templar | all | [Tithe of Alacrity](https://db.exil.es/spell/804818) |  | none | — | 3s | Emanate an aura for 1 hour, empowering party and raid members with 15% reduced damage taken from area of effect attacks. |
| Cultist | Dreadnought<br>r6 c4 | [Voidwarding](https://db.exil.es/spell/560002) |  | none | — | Instant | Reduces damage taken by party and raid members by -3%. Does not stack with similar effects. In addition, increases all of your resistances b… |
| Cultist | Heretic<br>r5 c0 | [Protection From Light](https://db.exil.es/spell/704434) |  | none | — | Instant | Reduces all damage taken by party and raid members by -3%. In addition, your Holy Damage taken is reduced by -10%. |
| Starcaller | Moon Guard<br>r5 c4 | [Shrouded Stars](https://db.exil.es/spell/704785) |  | none | — | Instant | Reduces damage taken by all party and raid members by -3%. Does not stack with similar effects. |
| Venomancer | Fortitude<br>r5 c3 | [Charmed Plating](https://db.exil.es/spell/300974) |  | none | — | Instant | Reduces damage taken by all party and raid members by 3%. Does not stack with similar effects. In addition, reduces your chance to be hit by… |
| Reaper | Domination<br>r5 c3 | [Ethereal Guard](https://db.exil.es/spell/300969) |  | none | — | Instant | Reduces the damage taken by party and raid members by -3%. Does not stack with similar effects. In addition, increases your melee haste by 1… |
| Reaper | all | [Reaper's Pact](https://db.exil.es/spell/804001) |  | none | — | Instant | You link yourself with an ally, reducing all damage they take by 5% and redirecting 20% of all damage they take to you. Lasts 10 min. This e… |
| Primalist | all | [Lesser Boon of the Turtle](https://db.exil.es/spell/524750) |  | none | — | Instant | Damage taken reduced by 2%. Only 1 Lesser Boon may be active on an ally at a time. |
| Primalist | Grovekeeper<br>r5 c2 | [Ring of Life](https://db.exil.es/spell/804705) |  | none | — | Instant | Allies within 40 yds receive 6% increased healing. Does not stack with similar effects. In addition, your Magic Damage taken is reduced by -… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Stormbringer | all | [Summon: Air Elemental](https://db.exil.es/spell/804019) **(pet — passive)** ⚠ |  | none | 75% mana | 5s | Call an Air Elemental to aid you in combat that gains a stack of Invigoration whenever it deals damage. — Cyclonean Protection: Reduces the damage taken from area of effect attacks of party members within 20 yds by 15%. |
| Guardian | Vanguard<br>r6 c6 | [Unscuffable](https://db.exil.es/spell/503837) |  | none | — | Instant | Allies within 30 yds now take -10% less Magic Damage from area of effect attacks. |
| Templar | all | [Tithe of Alacrity](https://db.exil.es/spell/804818) |  | none | — | 3s | Emanate an aura for 1 hour, empowering party and raid members with 15% reduced damage taken from area of effect attacks. |
| Cultist | Dreadnought<br>r6 c4 | [Voidwarding](https://db.exil.es/spell/560002) |  | none | — | Instant | Reduces damage taken by party and raid members by -3%. Does not stack with similar effects. In addition, increases all of your resistances b… |
| Cultist | Heretic<br>r5 c0 | [Protection From Light](https://db.exil.es/spell/704434) |  | none | — | Instant | Reduces all damage taken by party and raid members by -3%. In addition, your Holy Damage taken is reduced by -10%. |
| Starcaller | Moon Guard<br>r5 c4 | [Shrouded Stars](https://db.exil.es/spell/704785) |  | none | — | Instant | Reduces damage taken by all party and raid members by -3%. Does not stack with similar effects. |
| Venomancer | Fortitude<br>r5 c3 | [Charmed Plating](https://db.exil.es/spell/300974) |  | none | — | Instant | Reduces damage taken by all party and raid members by 3%. Does not stack with similar effects. In addition, reduces your chance to be hit by… |
| Reaper | Domination<br>r5 c3 | [Ethereal Guard](https://db.exil.es/spell/300969) |  | none | — | Instant | Reduces the damage taken by party and raid members by -3%. Does not stack with similar effects. In addition, increases your melee haste by 1… |
| Reaper | all | [Reaper's Pact](https://db.exil.es/spell/804001) |  | none | — | Instant | You link yourself with an ally, reducing all damage they take by 5% and redirecting 20% of all damage they take to you. Lasts 10 min. This e… |
| Primalist | all | [Lesser Boon of the Turtle](https://db.exil.es/spell/524750) |  | none | — | Instant | Damage taken reduced by 2%. Only 1 Lesser Boon may be active on an ally at a time. |
| Primalist | Grovekeeper<br>r5 c2 | [Ring of Life](https://db.exil.es/spell/804705) |  | none | — | Instant | Allies within 40 yds receive 6% increased healing. Does not stack with similar effects. In addition, your Magic Damage taken is reduced by -… |
```

</details>

**11 across 8 classes.**
None found for: Barbarian, Bloodmage, Chronomancer, Felsworn, Knight of Xoroth, Necromancer, Pyromancer, Ranger, Runemaster, Sun Cleric, Tinker, Witch Doctor, Witch Hunter.

## 10. Raid damage — active

What a player brings that makes the REST OF THE RAID hit harder -- haste, crit, attack or spell power, damage done. Two signals as everywhere else, but the second one here is a TEXT arm, and it is not optional.

**No effect-id rule can reach the banners.** Guardian's `Banner of Conquest` and `Banner of Swiftness` grant +5% crit and +5% haste to party and raid within 40 yds and carry not one offensive aura -- the buff lives in a triggered child spell. 135 owned spells are in that state, ten times the fourteen the raid-DR note records. A text arm is affordable here and was not there, because this family's phrasing is stereotyped rather than free prose.

**The clause is the unit, not the spell.** These are written as "<group clause>. ... In addition, <caster clause>" and only one half is ever in the effects: Ranger's `Double The Pace` grants the raid 10% haste in prose and carries its aura on the CASTER, while Reaper's `Ethereal Guard` is the same shape with the halves swapped and is a damage REDUCTION. So only clauses naming the group count, with the caster's own half cut out of each.

Three abilities do both jobs -- `Lucifron's Lagniappe`, `Hand of Yogg-Saron`, `Infernal Whipcrack` -- and appear under Raid damage reduction instead, because a row can only be filed once and losing one from a shipped table is worse.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | Ancestry<br>r8 c7 | [War Cry](https://db.exil.es/spell/500995) ⚠ |  | 3 min | — | Instant | Unleash a blood curdling war cry, increasing melee and ranged attack speed by 20%, and attack power by 150 of allies within 25 yds for 20 se… |
| Barbarian | Ancestry<br>r6 c10 | [Splash Zone](https://db.exil.es/spell/705156) |  | 30s | 25 energy | Instant | Share a drink from your Tankard with all party and raid members, granting 95 increased attack or spell power for 15 seconds. Does not stack … |
| Barbarian | Ancestry<br>r8 c10 | [Tavern Brawl!](https://db.exil.es/spell/804456) |  | 5 min | 25 energy | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from simil… |
| Barbarian | Ancestry<br>r8 c10 | [Clanlord's Totem](https://db.exil.es/spell/804737) |  | 1 min | 20 energy | Instant | Drop the Clanlord's Totem at the target location where it will remain for 15 seconds. The totem emanates an aura for 15 seconds, causing all… |
| Witch Doctor | all | [Call Avatar: Devilsaur](https://db.exil.es/spell/801585) **(pet — pet bar)** |  | 30s | 14% mana | 3s | You call forth a Devilsaur as your Avatar Dinosaur. Devilsaurs are massive and terrifying creatures capable of destroying groups of foes, and bolstering allies with powerful roars. You can only use 1 Avatar Dinosaur at a time. — Rallying Roar: Emanate an aura … |
| Witch Doctor | Brewing<br>r6 c5 | [Arcane Brew](https://db.exil.es/spell/801689) |  | 2 min | 8% mana | Instant | Throw your Arcane Brew at an ally, increasing their spell power and Spirit by 74 for 10 seconds. Spell power scales with caster level. |
| Witch Hunter | all | [Set Bounty](https://db.exil.es/spell/805760) |  | 45s | — | Instant | Set a bounty on the target enemy's head, increasing allies' critical strike chance against them by 3%, and increasing all Physical damage th… |
| Stormbringer | Wind<br>r8 c10 | [Surge of Might](https://db.exil.es/spell/520083) |  | 1 min | 15% mana | Instant | Emanate an aura around you for 15 seconds, causing allied players within 100 yds to deal 70% nature SP additional damage as Nature Damage wh… |
| Stormbringer | Wind<br>r8 c10 | [Tempest's Call](https://db.exil.es/spell/560567) ⚠ |  | 5 min | 26% mana | Instant | Bring the power of wind and storm to all nearby allies, increasing haste by 30% for 20 seconds. After being affected by this spell, allies c… |
| Stormbringer | all | [Blessing of Air](https://db.exil.es/spell/804022) |  | 10s | 27% mana | Instant | Emanate an aura to all party and raid members within 100 yds increasing their spell haste by 3%. Does not stack with similar effects. |
| Stormbringer | Wind<br>r4 c10 | [Tailwind](https://db.exil.es/spell/804035) |  | none | Depletes 20 | Instant | Depletes 20 Static Tap into the swift winds, increasing your damage by 10% and granting all allied players 5% increased haste for 15 seconds… |
| Stormbringer | Wind<br>r6 c10 | [Aerodynamics](https://db.exil.es/spell/806124) |  | none | Depletes 40 | Instant | Depletes 40 Static Envelop party and raid members within 40 yds in magical mist, increasing their attack or spell power by 95 for 15 seconds… |
| Knight of Xoroth | Defiance<br>r9 c6 | [Legion's Presence](https://db.exil.es/spell/804879) |  | 3 min | — | Instant | Emanate an aura to allies within 25 yds for 15 seconds, increasing their damage dealt by 10%. Fire Damage dealt by Hellfire Imps is increase… |
| Guardian | Inspiration<br>r4 c10 | [Banner of Swiftness](https://db.exil.es/spell/500259) |  | 20s | 25 energy | Instant | Attach a Banner of Swiftness to your back, increasing the haste of party and raid members within 40 yds by 5%. Does not stack with similar e… |
| Guardian | Inspiration<br>r2 c10 | [Banner of Conquest](https://db.exil.es/spell/500261) |  | 20s | 25 energy | Instant | Attach a Banner of Conquest to your back, increasing the critical strike chance of party and raid members within 40 yds by 5%. Does not stac… |
| Guardian | Inspiration<br>r8 c10 | [Champion's Presence](https://db.exil.es/spell/520835) |  | 5 min | 30 energy | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from simil… |
| Guardian | Inspiration<br>r6 c10 | [Song of Steel](https://db.exil.es/spell/704540) |  | none | 30 energy | Instant | Boost the morale of party and raid members, increasing their attack or spell power by 95 for 15 seconds. Does not stack with similar effects… |
| Guardian | Inspiration<br>r8 c10 | [Inspiring Presence](https://db.exil.es/spell/705352) |  | 1 min | 25 energy | Instant | Emanate an aura around you for 15 seconds, causing allied players within 100 yds to deal 35% AP additional damage as Holy Damage when they d… |
| Guardian | Inspiration<br>r4 c4 | [Hero's March](https://db.exil.es/spell/801774) |  | 2 min | — | Instant | Beat the drums of war, causing your auto attacks to trigger a Sound of War and increasing your haste by 15% for 20 seconds. In addition, all… |
| Guardian | Inspiration<br>r7 c4 | [Battle Drums](https://db.exil.es/spell/803683) |  | 3 min | 50 energy | Instant | Place down 3 Battle Drums around you for 1 minute. Allies may click on the drums to increase their critical strike chance, haste, damage, an… |
| Guardian | all | [Hero's Decree](https://db.exil.es/spell/803964) |  | 30s | 25 energy | Instant | Marks an ally for 15 sec, causing them to become immune to snares, and granting Inspiration to all nearby party members. While marked, any t… |
| Guardian | all | [Spellcaster's Decree](https://db.exil.es/spell/806138) |  | 30s | 25 energy | Instant | Empowers an ally for 15 sec, increasing their spell haste by 10% and reducing the cost of their spells and abilities by 10% and granting Ins… |
| Bloodmage | Fleshweaver<br>r8 c10 | [Red Thirst](https://db.exil.es/spell/520493) |  | 5 min | 26% health | Instant | Enrage allies within 40 yds, increasing haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from similar … |
| Bloodmage | Fleshweaver<br>r8 c10 | [Purify Blood](https://db.exil.es/spell/680679) |  | 1 min | 26% health | Instant | Emanate an aura for 15 seconds, causing allied players to deal 70% shadow SP additional damage as Shadow Damage when they deal direct damage… |
| Ranger | Farstrider<br>r8 c10 | [Frenzy](https://db.exil.es/spell/520492) |  | 5 min | 25 focus | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from simil… |
| Ranger | Farstrider<br>r8 c10 | [Command Aura](https://db.exil.es/spell/524600) |  | 1 min | — | Instant | Emanate an aura for 15 seconds, causing allied players to deal 35% ranged AP additional damage as Stormstrike Damage when they deal direct d… |
| Ranger | Farstrider<br>r4 c10 | [Battle Screech](https://db.exil.es/spell/705070) |  | none | 40 focus | Instant | Empower party and raid members within 40 yds, increasing their attack or spell power by 15 for 15 seconds. Does not stack with similar effec… |
| Ranger | Farstrider<br>r2 c10 | [Horn of War](https://db.exil.es/spell/800086) |  | 1 min | — | Instant | Generates 1 Advantage Emanate an aura for 30 seconds that grants 5% increased critical strike chance to party and raid members. Does not sta… |
| Ranger | Farstrider<br>r6 c10 | [Horn of Alacrity](https://db.exil.es/spell/806360) ⚠ |  | 1 min | — | Instant | Generates 1 Advantage Emanate an aura for 30 seconds that grants 5% increased haste to party and raid members. Does not stack with similar e… |
| Chronomancer | all | [Hasten](https://db.exil.es/spell/801304) ⚠ |  | 1.5 min | 17% mana | Instant | Hasten time for an ally, increasing movement speed and haste by 20% and granting them a 0% chance when they deal damage to strike the target… |
| Chronomancer | all | [Maw of Chaos](https://db.exil.es/spell/806316) |  | 24s | 10% mana | Instant | Instantly Heals an ally for 244 to 248, increasing their Spell Haste by 15% for 6 sec. Grants 1 Chromatic. |
| Pyromancer | all | [Firepower](https://db.exil.es/spell/805487) |  | 30s | 15% mana | Instant | Empower party and raid members within 30 yds that are currently in a Path of Flames for 10 sec. While active, affected allies gain 20% incre… |
| Cultist | all | [Summon: Faceless Servant](https://db.exil.es/spell/500709) |  | none | 40% mana | 3s | Summons a Faceless Servant to aid you in battle until dismissed. While active, this minion provides 2% increased critical strike chance to a… |
| Cultist | all | [Instill Despair](https://db.exil.es/spell/500718) |  | 10s | 9% mana | 1.5s | Defile an ally's weapon for 30 sec, granting 5% increased haste and giving them a 15% chance to steal 96 health from enemies they damage, he… |
| Cultist | all | [Horrific Revelation](https://db.exil.es/spell/704473) |  | none | 3% mana | Instant | Heals a friendly target for 344, scaling with Insanity, and increases their critical strike chance by 1%, stacking 15 times, for 15 sec. |
| Starcaller | all | [Stellar Alignment](https://db.exil.es/spell/807564) |  | 5 min | 15% mana | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 sec. After being affected by this spell, allies cannot benefit from similar e… |
| Sun Cleric | Blessings<br>r9 c4 | [Blessing of Triumph](https://db.exil.es/spell/804250) |  | 3 min | 13% mana | Instant | Redeem a Blessed ally for 20 seconds, granting 25% increased haste and 10% increased damage. If the ally falls below 35% maximum health they… |
| Tinker | Invention<br>r9 c4 | [Combat Symbiosis](https://db.exil.es/spell/805305) |  | 1.5 min | 24% mana | Instant | Electrify an allies' body, increasing their haste by 20% and causing damage dealt by them to heal nearby allies for 15% of the value. Lasts … |
| Primalist | Grovekeeper<br>r9 c2 | [Ancient of War](https://db.exil.es/spell/504222) ⚠ |  | 2.5 min | — | Instant | Funnel nature's fury into yourself, transforming into an Ancient of War for 20 seconds. While active, your Hammer of Life effectiveness is i… |
| Primalist | all | [Boon of the Elements](https://db.exil.es/spell/680428) |  | none | 300 rage | Instant | Increase an ally's critical strike chance by 5% and reduces the resource costs of their abilities by 10% for 20 sec. While active, the targe… |
| Primalist | Grovekeeper<br>r6 c10 | [Flourishing Growth](https://db.exil.es/spell/805442) |  | 10s | 20% mana | Instant | Empower party and raid members within 40 yds with verdant strength, increasing their attack or spell power by 95 for 20 seconds. Does not st… |
| Primalist | Grovekeeper<br>r8 c10 | [Neptulon's Wrath](https://db.exil.es/spell/807467) |  | 1 min | 19% mana | Instant | Emanate an aura for 15 seconds, causing allied players to deal 35% AP additional damage as Froststorm Damage when they deal direct damage. A… |
| Primalist | Grovekeeper<br>r8 c10 | [Primal Awakening](https://db.exil.es/spell/807560) |  | 5 min | 26% mana | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from simil… |
| Runemaster | all (tree)<br>r9 c2 | [Power Engraving](https://db.exil.es/spell/500296) |  | 5 min | 18% mana | Instant | Create a Power Engraving beneath you for 20 seconds, granting 20% increased Magic Damage dealt and 20% increased critical strike chance to u… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | Ancestry<br>r8 c7 | [War Cry](https://db.exil.es/spell/500995) ⚠ |  | 3 min | — | Instant | Unleash a blood curdling war cry, increasing melee and ranged attack speed by 20%, and attack power by 150 of allies within 25 yds for 20 se… |
| Barbarian | Ancestry<br>r6 c10 | [Splash Zone](https://db.exil.es/spell/705156) |  | 30s | 25 energy | Instant | Share a drink from your Tankard with all party and raid members, granting 95 increased attack or spell power for 15 seconds. Does not stack … |
| Barbarian | Ancestry<br>r8 c10 | [Tavern Brawl!](https://db.exil.es/spell/804456) |  | 5 min | 25 energy | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from simil… |
| Barbarian | Ancestry<br>r8 c10 | [Clanlord's Totem](https://db.exil.es/spell/804737) |  | 1 min | 20 energy | Instant | Drop the Clanlord's Totem at the target location where it will remain for 15 seconds. The totem emanates an aura for 15 seconds, causing all… |
| Witch Doctor | all | [Call Avatar: Devilsaur](https://db.exil.es/spell/801585) **(pet — pet bar)** |  | 30s | 14% mana | 3s | You call forth a Devilsaur as your Avatar Dinosaur. Devilsaurs are massive and terrifying creatures capable of destroying groups of foes, and bolstering allies with powerful roars. You can only use 1 Avatar Dinosaur at a time. — Rallying Roar: Emanate an aura … |
| Witch Doctor | Brewing<br>r6 c5 | [Arcane Brew](https://db.exil.es/spell/801689) |  | 2 min | 8% mana | Instant | Throw your Arcane Brew at an ally, increasing their spell power and Spirit by 74 for 10 seconds. Spell power scales with caster level. |
| Witch Hunter | all | [Set Bounty](https://db.exil.es/spell/805760) |  | 45s | — | Instant | Set a bounty on the target enemy's head, increasing allies' critical strike chance against them by 3%, and increasing all Physical damage th… |
| Stormbringer | Wind<br>r8 c10 | [Surge of Might](https://db.exil.es/spell/520083) |  | 1 min | 15% mana | Instant | Emanate an aura around you for 15 seconds, causing allied players within 100 yds to deal 70% nature SP additional damage as Nature Damage wh… |
| Stormbringer | Wind<br>r8 c10 | [Tempest's Call](https://db.exil.es/spell/560567) ⚠ |  | 5 min | 26% mana | Instant | Bring the power of wind and storm to all nearby allies, increasing haste by 30% for 20 seconds. After being affected by this spell, allies c… |
| Stormbringer | all | [Blessing of Air](https://db.exil.es/spell/804022) |  | 10s | 27% mana | Instant | Emanate an aura to all party and raid members within 100 yds increasing their spell haste by 3%. Does not stack with similar effects. |
| Stormbringer | Wind<br>r4 c10 | [Tailwind](https://db.exil.es/spell/804035) |  | none | Depletes 20 | Instant | Depletes 20 Static Tap into the swift winds, increasing your damage by 10% and granting all allied players 5% increased haste for 15 seconds… |
| Stormbringer | Wind<br>r6 c10 | [Aerodynamics](https://db.exil.es/spell/806124) |  | none | Depletes 40 | Instant | Depletes 40 Static Envelop party and raid members within 40 yds in magical mist, increasing their attack or spell power by 95 for 15 seconds… |
| Knight of Xoroth | Defiance<br>r9 c6 | [Legion's Presence](https://db.exil.es/spell/804879) |  | 3 min | — | Instant | Emanate an aura to allies within 25 yds for 15 seconds, increasing their damage dealt by 10%. Fire Damage dealt by Hellfire Imps is increase… |
| Guardian | Inspiration<br>r4 c10 | [Banner of Swiftness](https://db.exil.es/spell/500259) |  | 20s | 25 energy | Instant | Attach a Banner of Swiftness to your back, increasing the haste of party and raid members within 40 yds by 5%. Does not stack with similar e… |
| Guardian | Inspiration<br>r2 c10 | [Banner of Conquest](https://db.exil.es/spell/500261) |  | 20s | 25 energy | Instant | Attach a Banner of Conquest to your back, increasing the critical strike chance of party and raid members within 40 yds by 5%. Does not stac… |
| Guardian | Inspiration<br>r8 c10 | [Champion's Presence](https://db.exil.es/spell/520835) |  | 5 min | 30 energy | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from simil… |
| Guardian | Inspiration<br>r6 c10 | [Song of Steel](https://db.exil.es/spell/704540) |  | none | 30 energy | Instant | Boost the morale of party and raid members, increasing their attack or spell power by 95 for 15 seconds. Does not stack with similar effects… |
| Guardian | Inspiration<br>r8 c10 | [Inspiring Presence](https://db.exil.es/spell/705352) |  | 1 min | 25 energy | Instant | Emanate an aura around you for 15 seconds, causing allied players within 100 yds to deal 35% AP additional damage as Holy Damage when they d… |
| Guardian | Inspiration<br>r4 c4 | [Hero's March](https://db.exil.es/spell/801774) |  | 2 min | — | Instant | Beat the drums of war, causing your auto attacks to trigger a Sound of War and increasing your haste by 15% for 20 seconds. In addition, all… |
| Guardian | Inspiration<br>r7 c4 | [Battle Drums](https://db.exil.es/spell/803683) |  | 3 min | 50 energy | Instant | Place down 3 Battle Drums around you for 1 minute. Allies may click on the drums to increase their critical strike chance, haste, damage, an… |
| Guardian | all | [Hero's Decree](https://db.exil.es/spell/803964) |  | 30s | 25 energy | Instant | Marks an ally for 15 sec, causing them to become immune to snares, and granting Inspiration to all nearby party members. While marked, any t… |
| Guardian | all | [Spellcaster's Decree](https://db.exil.es/spell/806138) |  | 30s | 25 energy | Instant | Empowers an ally for 15 sec, increasing their spell haste by 10% and reducing the cost of their spells and abilities by 10% and granting Ins… |
| Bloodmage | Fleshweaver<br>r8 c10 | [Red Thirst](https://db.exil.es/spell/520493) |  | 5 min | 26% health | Instant | Enrage allies within 40 yds, increasing haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from similar … |
| Bloodmage | Fleshweaver<br>r8 c10 | [Purify Blood](https://db.exil.es/spell/680679) |  | 1 min | 26% health | Instant | Emanate an aura for 15 seconds, causing allied players to deal 70% shadow SP additional damage as Shadow Damage when they deal direct damage… |
| Ranger | Farstrider<br>r8 c10 | [Frenzy](https://db.exil.es/spell/520492) |  | 5 min | 25 focus | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from simil… |
| Ranger | Farstrider<br>r8 c10 | [Command Aura](https://db.exil.es/spell/524600) |  | 1 min | — | Instant | Emanate an aura for 15 seconds, causing allied players to deal 35% ranged AP additional damage as Stormstrike Damage when they deal direct d… |
| Ranger | Farstrider<br>r4 c10 | [Battle Screech](https://db.exil.es/spell/705070) |  | none | 40 focus | Instant | Empower party and raid members within 40 yds, increasing their attack or spell power by 15 for 15 seconds. Does not stack with similar effec… |
| Ranger | Farstrider<br>r2 c10 | [Horn of War](https://db.exil.es/spell/800086) |  | 1 min | — | Instant | Generates 1 Advantage Emanate an aura for 30 seconds that grants 5% increased critical strike chance to party and raid members. Does not sta… |
| Ranger | Farstrider<br>r6 c10 | [Horn of Alacrity](https://db.exil.es/spell/806360) ⚠ |  | 1 min | — | Instant | Generates 1 Advantage Emanate an aura for 30 seconds that grants 5% increased haste to party and raid members. Does not stack with similar e… |
| Chronomancer | all | [Hasten](https://db.exil.es/spell/801304) ⚠ |  | 1.5 min | 17% mana | Instant | Hasten time for an ally, increasing movement speed and haste by 20% and granting them a 0% chance when they deal damage to strike the target… |
| Chronomancer | all | [Maw of Chaos](https://db.exil.es/spell/806316) |  | 24s | 10% mana | Instant | Instantly Heals an ally for 244 to 248, increasing their Spell Haste by 15% for 6 sec. Grants 1 Chromatic. |
| Pyromancer | all | [Firepower](https://db.exil.es/spell/805487) |  | 30s | 15% mana | Instant | Empower party and raid members within 30 yds that are currently in a Path of Flames for 10 sec. While active, affected allies gain 20% incre… |
| Cultist | all | [Summon: Faceless Servant](https://db.exil.es/spell/500709) |  | none | 40% mana | 3s | Summons a Faceless Servant to aid you in battle until dismissed. While active, this minion provides 2% increased critical strike chance to a… |
| Cultist | all | [Instill Despair](https://db.exil.es/spell/500718) |  | 10s | 9% mana | 1.5s | Defile an ally's weapon for 30 sec, granting 5% increased haste and giving them a 15% chance to steal 96 health from enemies they damage, he… |
| Cultist | all | [Horrific Revelation](https://db.exil.es/spell/704473) |  | none | 3% mana | Instant | Heals a friendly target for 344, scaling with Insanity, and increases their critical strike chance by 1%, stacking 15 times, for 15 sec. |
| Starcaller | all | [Stellar Alignment](https://db.exil.es/spell/807564) |  | 5 min | 15% mana | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 sec. After being affected by this spell, allies cannot benefit from similar e… |
| Sun Cleric | Blessings<br>r9 c4 | [Blessing of Triumph](https://db.exil.es/spell/804250) |  | 3 min | 13% mana | Instant | Redeem a Blessed ally for 20 seconds, granting 25% increased haste and 10% increased damage. If the ally falls below 35% maximum health they… |
| Tinker | Invention<br>r9 c4 | [Combat Symbiosis](https://db.exil.es/spell/805305) |  | 1.5 min | 24% mana | Instant | Electrify an allies' body, increasing their haste by 20% and causing damage dealt by them to heal nearby allies for 15% of the value. Lasts … |
| Primalist | Grovekeeper<br>r9 c2 | [Ancient of War](https://db.exil.es/spell/504222) ⚠ |  | 2.5 min | — | Instant | Funnel nature's fury into yourself, transforming into an Ancient of War for 20 seconds. While active, your Hammer of Life effectiveness is i… |
| Primalist | all | [Boon of the Elements](https://db.exil.es/spell/680428) |  | none | 300 rage | Instant | Increase an ally's critical strike chance by 5% and reduces the resource costs of their abilities by 10% for 20 sec. While active, the targe… |
| Primalist | Grovekeeper<br>r6 c10 | [Flourishing Growth](https://db.exil.es/spell/805442) |  | 10s | 20% mana | Instant | Empower party and raid members within 40 yds with verdant strength, increasing their attack or spell power by 95 for 20 seconds. Does not st… |
| Primalist | Grovekeeper<br>r8 c10 | [Neptulon's Wrath](https://db.exil.es/spell/807467) |  | 1 min | 19% mana | Instant | Emanate an aura for 15 seconds, causing allied players to deal 35% AP additional damage as Froststorm Damage when they deal direct damage. A… |
| Primalist | Grovekeeper<br>r8 c10 | [Primal Awakening](https://db.exil.es/spell/807560) |  | 5 min | 26% mana | Instant | Enrage all nearby allies, increasing their haste by 30% for 20 seconds. After being affected by this spell, allies cannot benefit from simil… |
| Runemaster | all (tree)<br>r9 c2 | [Power Engraving](https://db.exil.es/spell/500296) |  | 5 min | 18% mana | Instant | Create a Power Engraving beneath you for 20 seconds, granting 20% increased Magic Damage dealt and 20% increased critical strike chance to u… |
```

</details>

**44 across 16 classes.**
None found for: Felsworn, Necromancer, Reaper, Templar, Venomancer.

## 10b. Raid damage — passive auras

Same signals, but **no cooldown and no cost**: the 3% raid auras every class carries, and the proc-conditional talents. Separated from the active list for the same reason the DR pair is: a raid cooldown plan cares about what you press, roster composition cares about what is simply on.

This one is deliberately NOT a column in the coverage grid. All 21 classes have at least one, and a column that is always full can never show a gap -- it would be the largest table on the page and the least informative thing in the grid.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | Headhunting<br>r7 c6 | [Manhunter](https://db.exil.es/spell/300879) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Barbarian | all | [Barbaric Rage](https://db.exil.es/spell/300967) |  | none | — | Instant | Increases party and raid member's physical damage by 3%. Does not stack with similar effects. |
| Barbarian | Ancestry<br>r2 c10 | [Frozen Blades](https://db.exil.es/spell/573256) |  | none | — | Instant | Critical strikes now grant party and raid members 5% critical strike chance for 8 seconds. Does not stack with similar effects. |
| Barbarian | Ancestry<br>r4 c10 | [Uniting Voice](https://db.exil.es/spell/705162) |  | none | — | Instant | Casting Ancestral Roar now increases haste of party and raid members by 5% for 20 seconds. Does not stack with similar effects. Critical str… |
| Barbarian | Brutality<br>r7 c4 | [Symbol of the Warspear](https://db.exil.es/spell/804730) |  | none | — | Instant | You are marked by the Warspear symbol, granting 9% increased Attack Power to party and raid members within 100 yds. Does not stack with simi… |
| Barbarian | Ancestry<br>r3 c2 | [Ancestral Fury](https://db.exil.es/spell/804731) |  | none | — | Instant | Emanate a powerful aura, granting 10% increased melee and ranged haste to party and raid members within 100 yds. Does not stack with similar… |
| Witch Doctor | Shadowhunting<br>r6 c6 | [Strength of Da Loa](https://db.exil.es/spell/300871) |  | none | — | Instant | Increases the attack power of party and raid members by 5%. Does not stack with similar effects. In addition, health and mana restoration pr… |
| Witch Doctor | Shadowhunting<br>r6 c2 | [Darkspear Traditionalist](https://db.exil.es/spell/503707) |  | none | — | Instant | Emanate a powerful aura, granting 10% increased melee and ranged haste to party and raid members within 100 yds. Does not stack with similar… |
| Witch Doctor | Voodoo<br>r7 c7 | [Dark Loa's Blessing](https://db.exil.es/spell/560545) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, your Shadow Puppets now ch… |
| Felsworn | Tyrant<br>r5 c6 | [Betrayer](https://db.exil.es/spell/300476) |  | none | — | Instant | Dodging attacks causes 40% off-hand Weapon Damage to attackers and enrages your party and raid members within 20 yds, increasing their criti… |
| Felsworn | all | [Fel Empowerment](https://db.exil.es/spell/300962) |  | none | — | Instant | Increases party and raid member's spell damage by 3%. Does not stack with similar effects. |
| Felsworn | Infernal<br>r7 c5 | [Fel Infusion](https://db.exil.es/spell/560533) |  | none | — | Instant | Increases critical strike chance of all party and raid members within 100 by 3%. Does not stack with similar effects. In addition, increases… |
| Felsworn | Slayer<br>r7 c6 | [Felguard](https://db.exil.es/spell/560542) |  | none | — | Instant | Emanate a powerful aura, granting 10% increased melee and ranged haste to party and raid members within 100 yds. Does not stack with similar… |
| Felsworn | Tyrant<br>r7 c7 | [Eye of the Tyrant](https://db.exil.es/spell/560549) |  | none | — | Instant | Grant 10% increased melee and ranged haste to party and raid members within 100 yds. Does not stack with similar effects. In addition, your … |
| Felsworn | Slayer<br>r4 c3 | [Scars of Suffering](https://db.exil.es/spell/570158) |  | none | — | Instant | Casting Azzinoth's Assault now scars the enemy, increasing your allies' attack power against them by 15% Agility for 10 seconds. |
| Felsworn | Tyrant<br>r7 c1 | [Doomscarring](https://db.exil.es/spell/685321) |  | none | — | Instant | Your melee critical strikes now deal an additional 1 + 30% AP Physical Damage and scars enemies for 12 seconds, increasing your allies' atta… |
| Felsworn | all | [Demonfire Pact](https://db.exil.es/spell/800031) |  | none | — | Instant | Emanate an aura that increases the critical strike chance of nearby allies by 3% and their damage against Demons by 5%. Does not stack with … |
| Witch Hunter | Inquisition<br>r7 c7 | [Monster Hunting](https://db.exil.es/spell/300872) |  | none | — | Instant | Increases melee and ranged haste of party and raid members within 100 yds by 10%. Does not stack with similar effects. In addition, increase… |
| Witch Hunter | Boltslinger<br>r7 c5 | [Slayer](https://db.exil.es/spell/300968) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your criti… |
| Witch Hunter | Houndmaster<br>r7 c4 | [Veiled in Darkness](https://db.exil.es/spell/524854) |  | none | — | Instant | A veil of dark magic encircles you at all times, granting 5% increased Attack Power to party and raid members within 100 yds. Does not stack… |
| Witch Hunter | all | [Eternal Presence](https://db.exil.es/spell/560001) |  | none | — | Instant | Increases the attack power of party and raid members by 5%. Does not stack with similar effects. In addition, increases your attack power by… |
| Witch Hunter | all | [Leyline Disturbance](https://db.exil.es/spell/560540) |  | none | — | Instant | Increases melee and ranged haste of party and raid members within 100 yds by 10%. Does not stack with similar effects. Additionally, the dur… |
| Witch Hunter | all | [Solar Avenger](https://db.exil.es/spell/806196) |  | none | — | Instant | Gives your Physical Damage attacks and effects a 10% chance to empower nearby allies affected by Solar Guidance, granting them 5% increased … |
| Stormbringer | Maelstrom<br>r7 c5 | [Conductor In Charge](https://db.exil.es/spell/300961) |  | none | — | Instant | Increases all damage dealt by party and raid members by 3% and your Frost Damage dealt by 5%. Does not stack with similar effects. |
| Stormbringer | Lightning<br>r4 c5 | [Electrifying Aura](https://db.exil.es/spell/560568) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Stormbringer | all | [Updraft: Haste](https://db.exil.es/spell/704204) |  | none | — | Instant | Allies in your Updraft have 5% increased haste. |
| Stormbringer | Wind<br>r2 c10 | [Focal Point](https://db.exil.es/spell/706629) |  | none | — | Instant | Casting Call Lightning now increases the critical strike chance of party and raid members by 5% for 10 seconds. Does not stack with similar … |
| Knight of Xoroth | Hellfire<br>r6 c6 | [Hellbringer](https://db.exil.es/spell/300963) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. |
| Knight of Xoroth | War<br>r6 c4 | [Conqueror's Will](https://db.exil.es/spell/520372) |  | none | — | Instant | Increases the critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your d… |
| Knight of Xoroth | Hellfire<br>r6 c6 | [Xorothian Empowerment](https://db.exil.es/spell/704994) |  | none | — | Instant | Increases the attack power of all party and raid members 5%. Does not stack with similar effects. |
| Guardian | Gladiator<br>r6 c4 | [Overwhelming Presence](https://db.exil.es/spell/712367) ⚠ |  | none | — | Instant | Increases the attack power of all party and raid members 5%. Does not stack with similar effects. In addition, increases your Agility by 10%… |
| Templar | Crusader<br>r7 c5 | [Serendipity](https://db.exil.es/spell/300929) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, increases your Holy Damage… |
| Templar | Zealot<br>r7 c6 | [Devotion of Khaz'goroth](https://db.exil.es/spell/560096) |  | none | — | Instant | Increases all party and raid member's melee and ranged haste by 10%. Does not stack with similar effects. Damage dealt with auto attacks red… |
| Templar | Oathkeeper<br>r5 c3 | [Call of the Monastery](https://db.exil.es/spell/560550) |  | none | — | Instant | Increases the attack power of all party and raid members 5%. Does not stack with similar effects. In addition, increases your attack power b… |
| Bloodmage | Sanguine<br>r6 c3 | [Dark Presence](https://db.exil.es/spell/300957) |  | none | — | Instant | Increases spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your spell haste by 3… |
| Bloodmage | Eternal<br>r7 c3 | [Eternal Presence](https://db.exil.es/spell/560001) |  | none | — | Instant | Increases the attack power of party and raid members by 5%. Does not stack with similar effects. In addition, increases your attack power by… |
| Bloodmage | Accursed<br>r5 c4 | [Dark Sigil](https://db.exil.es/spell/560535) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, you now heal for 15%… |
| Bloodmage | Fleshweaver<br>r2 c10 | [Fleshbending](https://db.exil.es/spell/680684) |  | none | — | Instant | Your critical strikes now increase the critical strike chance of all party and raid members by 5% for 10 seconds. Does not stack with simila… |
| Bloodmage | Fleshweaver<br>r4 c10 | [Blood-Cursed Weapons](https://db.exil.es/spell/684331) ⚠ |  | none | — | Instant | Casting Crimson Tide now additionally increases the haste of all party and raid members by 5% for 15 seconds. Does not stack with similar ef… |
| Bloodmage | Accursed<br>r6 c6 | [Dark Frenzy](https://db.exil.es/spell/704644) |  | none | — | Instant | Increases spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, while a Cursed Form is active, … |
| Ranger | Brigand<br>r7 c7 | [Guile of the Cutthroat](https://db.exil.es/spell/560531) |  | none | — | Instant | Increases party and raid member's melee and ranged attack power by 5%. Does not stack with similar effects. In addition, increases your dama… |
| Ranger | all (tree)<br>r7 c2 | [Double The Pace](https://db.exil.es/spell/705031) |  | none | — | Instant | Increases all party and raid member's melee and ranged haste by 10%. Does not stack with similar effects. In addition, increases your critic… |
| Ranger | all | [Rally The Archers](https://db.exil.es/spell/705088) |  | none | — | Instant | Woodland Arrow now grants party members within 15 yds of you 4% increased ranged attack power for 10 sec, scaling with Agility. |
| Ranger | all | [Emerald Dreamer Front](https://db.exil.es/spell/803510) |  | none | — | Instant | Grants party members within 8 yds 0% increased damage and critical strike chance for 8 sec. |
| Chronomancer | Artificer<br>r7 c3 | [Infinity Stone](https://db.exil.es/spell/300873) |  | none | — | Instant | Increases the critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your c… |
| Chronomancer | Infinite<br>r7 c5 | [Infinite Horizon](https://db.exil.es/spell/560528) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, your Unmake and Timerend g… |
| Chronomancer | Time<br>r7 c3 | [Wonders of Time](https://db.exil.es/spell/560541) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. Additionally, all healing done now has a… |
| Necromancer | Rime<br>r7 c4 | [Chilling Presence](https://db.exil.es/spell/300958) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases the critic… |
| Necromancer | Animation<br>r7 c4 | [Corpse Wagon](https://db.exil.es/spell/503738) |  | none | — | Instant | Increases all damage dealt by party and raid members by 3%. Does not stack with similar effects. |
| Necromancer | Rime<br>r4 c8 | [Icecrown](https://db.exil.es/spell/531135) |  | none | — | Instant | Your Frost Damage dealt now increases your allies' critical strike chance against the enemy by 1% for 10 seconds, stacking 3 times. |
| Necromancer | Death<br>r7 c3 | [Apothecary's Cauldron](https://db.exil.es/spell/560537) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your Magic Damage… |
| Necromancer | all | [Improved Razorice](https://db.exil.es/spell/704671) |  | none | — | Instant | Razorice now grants affected allies 5% increased Frost damage. |
| Pyromancer | Draconic<br>r6 c8 | [Inner Flame](https://db.exil.es/spell/301974) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Pyromancer | Incineration<br>r6 c7 | [Fiery Passion](https://db.exil.es/spell/560525) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, your spell haste is increas… |
| Cultist | all | [N'zoth's Cunning](https://db.exil.es/spell/300888) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Cultist | Corruption<br>r5 c4 | [Visions](https://db.exil.es/spell/560526) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, your Shadow Damage is incre… |
| Starcaller | Sentinel<br>r4 c4 | [Elune's Blessing](https://db.exil.es/spell/300876) |  | none | — | Instant | Increases party and raid member's melee and ranged haste by 10%. Does not stack with similar effects. |
| Starcaller | Moon Priest<br>r7 c5 | [Flow of Waters](https://db.exil.es/spell/560539) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your criti… |
| Starcaller | Warden<br>r6 c1 | [Vigil of the Watchers](https://db.exil.es/spell/680709) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Sun Cleric | all | [Seraphim's Guidance](https://db.exil.es/spell/300964) |  | none | — | Instant | Increases party and raid member's physical damage by 3%. Does not stack with similar effects. |
| Sun Cleric | Valkyrie<br>r5 c5 | [March of the Valkyr](https://db.exil.es/spell/560534) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, your chance to parry is in… |
| Sun Cleric | Blessings<br>r6 c8 | [Glaring Rays](https://db.exil.es/spell/804257) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3% and your spell haste by an additional 3%. Does not stack with similar effects. |
| Tinker | all | [Marksmanship](https://db.exil.es/spell/300869) |  | none | — | Instant | Increases party and raid member's attack power by 3%. Does not stack with similar effects. |
| Tinker | Invention<br>r5 c4 | [Fine Tuning](https://db.exil.es/spell/300877) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, not critically heali… |
| Tinker | Demolition<br>r6 c5 | [The BIG Guns!](https://db.exil.es/spell/560593) |  | none | — | Instant | Increases the attack power of all party and raid members 5%. Does not stack with similar effects. In addition, increases your ranged attack … |
| Tinker | Mechanics<br>r6 c4 | [Mechanical Enhancements](https://db.exil.es/spell/706632) |  | none | — | Instant | Increases all party and raid member's melee and ranged haste by 10%. Does not stack with similar effects. In addition, the range of your off… |
| Venomancer | all | [Rune of Haste](https://db.exil.es/spell/300874) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. |
| Venomancer | Rot<br>r7 c4 | [Fungal Link](https://db.exil.es/spell/300959) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, the range of your Rot spell… |
| Reaper | Domination<br>r4 c5 | [Soulsight](https://db.exil.es/spell/300565) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, dealing direct damag… |
| Reaper | Harvest<br>r6 c4 | [Blood Harvester](https://db.exil.es/spell/300889) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Reaper | Soul<br>r7 c4 | [Death's Presence](https://db.exil.es/spell/520371) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. |
| Reaper | all | [Icecrown](https://db.exil.es/spell/706732) |  | none | — | Instant | Increases your allies' critical strike chance against the enemy by 1% for 10 sec, stacking 3 times. |
| Primalist | Grovekeeper<br>r2 c10 | [Vitality Surge](https://db.exil.es/spell/504214) |  | none | — | Instant | All effective healing done now has a 25% chance to increase the haste of party and raid members by 5% for 20 seconds. Does not stack with si… |
| Primalist | Geomancy<br>r6 c4 | [Molten Fervor](https://db.exil.es/spell/680476) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your spell haste … |
| Primalist | all | [Primal Hunger](https://db.exil.es/spell/706154) |  | none | — | Instant | Causes critical strikes to restore 2% maximum Health. Cannot occur more than once every sec. Also increases all party and raid members' atta… |
| Primalist | Wildwalker<br>r7 c2 | [Killer's Path](https://db.exil.es/spell/706633) |  | none | — | Instant | Increases the attack power of party and raid members by 5%. Does not stack with similar effects. In addition, increases your critical strike… |
| Runemaster | Riftblade<br>r7 c3 | [Runic Power](https://db.exil.es/spell/300944) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, critical strikes now incre… |
| Runemaster | Glyphic<br>r6 c6 | [Runes of Quickness](https://db.exil.es/spell/560527) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, the range of your Glyphic s… |
| Runemaster | Engravement<br>r6 c3 | [Leyline Disturbance](https://db.exil.es/spell/560540) |  | none | — | Instant | Increases melee and ranged haste of party and raid members within 100 yds by 10%. Does not stack with similar effects. Additionally, the dur… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Barbarian | Headhunting<br>r7 c6 | [Manhunter](https://db.exil.es/spell/300879) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Barbarian | all | [Barbaric Rage](https://db.exil.es/spell/300967) |  | none | — | Instant | Increases party and raid member's physical damage by 3%. Does not stack with similar effects. |
| Barbarian | Ancestry<br>r2 c10 | [Frozen Blades](https://db.exil.es/spell/573256) |  | none | — | Instant | Critical strikes now grant party and raid members 5% critical strike chance for 8 seconds. Does not stack with similar effects. |
| Barbarian | Ancestry<br>r4 c10 | [Uniting Voice](https://db.exil.es/spell/705162) |  | none | — | Instant | Casting Ancestral Roar now increases haste of party and raid members by 5% for 20 seconds. Does not stack with similar effects. Critical str… |
| Barbarian | Brutality<br>r7 c4 | [Symbol of the Warspear](https://db.exil.es/spell/804730) |  | none | — | Instant | You are marked by the Warspear symbol, granting 9% increased Attack Power to party and raid members within 100 yds. Does not stack with simi… |
| Barbarian | Ancestry<br>r3 c2 | [Ancestral Fury](https://db.exil.es/spell/804731) |  | none | — | Instant | Emanate a powerful aura, granting 10% increased melee and ranged haste to party and raid members within 100 yds. Does not stack with similar… |
| Witch Doctor | Shadowhunting<br>r6 c6 | [Strength of Da Loa](https://db.exil.es/spell/300871) |  | none | — | Instant | Increases the attack power of party and raid members by 5%. Does not stack with similar effects. In addition, health and mana restoration pr… |
| Witch Doctor | Shadowhunting<br>r6 c2 | [Darkspear Traditionalist](https://db.exil.es/spell/503707) |  | none | — | Instant | Emanate a powerful aura, granting 10% increased melee and ranged haste to party and raid members within 100 yds. Does not stack with similar… |
| Witch Doctor | Voodoo<br>r7 c7 | [Dark Loa's Blessing](https://db.exil.es/spell/560545) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, your Shadow Puppets now ch… |
| Felsworn | Tyrant<br>r5 c6 | [Betrayer](https://db.exil.es/spell/300476) |  | none | — | Instant | Dodging attacks causes 40% off-hand Weapon Damage to attackers and enrages your party and raid members within 20 yds, increasing their criti… |
| Felsworn | all | [Fel Empowerment](https://db.exil.es/spell/300962) |  | none | — | Instant | Increases party and raid member's spell damage by 3%. Does not stack with similar effects. |
| Felsworn | Infernal<br>r7 c5 | [Fel Infusion](https://db.exil.es/spell/560533) |  | none | — | Instant | Increases critical strike chance of all party and raid members within 100 by 3%. Does not stack with similar effects. In addition, increases… |
| Felsworn | Slayer<br>r7 c6 | [Felguard](https://db.exil.es/spell/560542) |  | none | — | Instant | Emanate a powerful aura, granting 10% increased melee and ranged haste to party and raid members within 100 yds. Does not stack with similar… |
| Felsworn | Tyrant<br>r7 c7 | [Eye of the Tyrant](https://db.exil.es/spell/560549) |  | none | — | Instant | Grant 10% increased melee and ranged haste to party and raid members within 100 yds. Does not stack with similar effects. In addition, your … |
| Felsworn | Slayer<br>r4 c3 | [Scars of Suffering](https://db.exil.es/spell/570158) |  | none | — | Instant | Casting Azzinoth's Assault now scars the enemy, increasing your allies' attack power against them by 15% Agility for 10 seconds. |
| Felsworn | Tyrant<br>r7 c1 | [Doomscarring](https://db.exil.es/spell/685321) |  | none | — | Instant | Your melee critical strikes now deal an additional 1 + 30% AP Physical Damage and scars enemies for 12 seconds, increasing your allies' atta… |
| Felsworn | all | [Demonfire Pact](https://db.exil.es/spell/800031) |  | none | — | Instant | Emanate an aura that increases the critical strike chance of nearby allies by 3% and their damage against Demons by 5%. Does not stack with … |
| Witch Hunter | Inquisition<br>r7 c7 | [Monster Hunting](https://db.exil.es/spell/300872) |  | none | — | Instant | Increases melee and ranged haste of party and raid members within 100 yds by 10%. Does not stack with similar effects. In addition, increase… |
| Witch Hunter | Boltslinger<br>r7 c5 | [Slayer](https://db.exil.es/spell/300968) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your criti… |
| Witch Hunter | Houndmaster<br>r7 c4 | [Veiled in Darkness](https://db.exil.es/spell/524854) |  | none | — | Instant | A veil of dark magic encircles you at all times, granting 5% increased Attack Power to party and raid members within 100 yds. Does not stack… |
| Witch Hunter | all | [Eternal Presence](https://db.exil.es/spell/560001) |  | none | — | Instant | Increases the attack power of party and raid members by 5%. Does not stack with similar effects. In addition, increases your attack power by… |
| Witch Hunter | all | [Leyline Disturbance](https://db.exil.es/spell/560540) |  | none | — | Instant | Increases melee and ranged haste of party and raid members within 100 yds by 10%. Does not stack with similar effects. Additionally, the dur… |
| Witch Hunter | all | [Solar Avenger](https://db.exil.es/spell/806196) |  | none | — | Instant | Gives your Physical Damage attacks and effects a 10% chance to empower nearby allies affected by Solar Guidance, granting them 5% increased … |
| Stormbringer | Maelstrom<br>r7 c5 | [Conductor In Charge](https://db.exil.es/spell/300961) |  | none | — | Instant | Increases all damage dealt by party and raid members by 3% and your Frost Damage dealt by 5%. Does not stack with similar effects. |
| Stormbringer | Lightning<br>r4 c5 | [Electrifying Aura](https://db.exil.es/spell/560568) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Stormbringer | all | [Updraft: Haste](https://db.exil.es/spell/704204) |  | none | — | Instant | Allies in your Updraft have 5% increased haste. |
| Stormbringer | Wind<br>r2 c10 | [Focal Point](https://db.exil.es/spell/706629) |  | none | — | Instant | Casting Call Lightning now increases the critical strike chance of party and raid members by 5% for 10 seconds. Does not stack with similar … |
| Knight of Xoroth | Hellfire<br>r6 c6 | [Hellbringer](https://db.exil.es/spell/300963) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. |
| Knight of Xoroth | War<br>r6 c4 | [Conqueror's Will](https://db.exil.es/spell/520372) |  | none | — | Instant | Increases the critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your d… |
| Knight of Xoroth | Hellfire<br>r6 c6 | [Xorothian Empowerment](https://db.exil.es/spell/704994) |  | none | — | Instant | Increases the attack power of all party and raid members 5%. Does not stack with similar effects. |
| Guardian | Gladiator<br>r6 c4 | [Overwhelming Presence](https://db.exil.es/spell/712367) ⚠ |  | none | — | Instant | Increases the attack power of all party and raid members 5%. Does not stack with similar effects. In addition, increases your Agility by 10%… |
| Templar | Crusader<br>r7 c5 | [Serendipity](https://db.exil.es/spell/300929) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, increases your Holy Damage… |
| Templar | Zealot<br>r7 c6 | [Devotion of Khaz'goroth](https://db.exil.es/spell/560096) |  | none | — | Instant | Increases all party and raid member's melee and ranged haste by 10%. Does not stack with similar effects. Damage dealt with auto attacks red… |
| Templar | Oathkeeper<br>r5 c3 | [Call of the Monastery](https://db.exil.es/spell/560550) |  | none | — | Instant | Increases the attack power of all party and raid members 5%. Does not stack with similar effects. In addition, increases your attack power b… |
| Bloodmage | Sanguine<br>r6 c3 | [Dark Presence](https://db.exil.es/spell/300957) |  | none | — | Instant | Increases spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your spell haste by 3… |
| Bloodmage | Eternal<br>r7 c3 | [Eternal Presence](https://db.exil.es/spell/560001) |  | none | — | Instant | Increases the attack power of party and raid members by 5%. Does not stack with similar effects. In addition, increases your attack power by… |
| Bloodmage | Accursed<br>r5 c4 | [Dark Sigil](https://db.exil.es/spell/560535) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, you now heal for 15%… |
| Bloodmage | Fleshweaver<br>r2 c10 | [Fleshbending](https://db.exil.es/spell/680684) |  | none | — | Instant | Your critical strikes now increase the critical strike chance of all party and raid members by 5% for 10 seconds. Does not stack with simila… |
| Bloodmage | Fleshweaver<br>r4 c10 | [Blood-Cursed Weapons](https://db.exil.es/spell/684331) ⚠ |  | none | — | Instant | Casting Crimson Tide now additionally increases the haste of all party and raid members by 5% for 15 seconds. Does not stack with similar ef… |
| Bloodmage | Accursed<br>r6 c6 | [Dark Frenzy](https://db.exil.es/spell/704644) |  | none | — | Instant | Increases spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, while a Cursed Form is active, … |
| Ranger | Brigand<br>r7 c7 | [Guile of the Cutthroat](https://db.exil.es/spell/560531) |  | none | — | Instant | Increases party and raid member's melee and ranged attack power by 5%. Does not stack with similar effects. In addition, increases your dama… |
| Ranger | all (tree)<br>r7 c2 | [Double The Pace](https://db.exil.es/spell/705031) |  | none | — | Instant | Increases all party and raid member's melee and ranged haste by 10%. Does not stack with similar effects. In addition, increases your critic… |
| Ranger | all | [Rally The Archers](https://db.exil.es/spell/705088) |  | none | — | Instant | Woodland Arrow now grants party members within 15 yds of you 4% increased ranged attack power for 10 sec, scaling with Agility. |
| Ranger | all | [Emerald Dreamer Front](https://db.exil.es/spell/803510) |  | none | — | Instant | Grants party members within 8 yds 0% increased damage and critical strike chance for 8 sec. |
| Chronomancer | Artificer<br>r7 c3 | [Infinity Stone](https://db.exil.es/spell/300873) |  | none | — | Instant | Increases the critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your c… |
| Chronomancer | Infinite<br>r7 c5 | [Infinite Horizon](https://db.exil.es/spell/560528) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, your Unmake and Timerend g… |
| Chronomancer | Time<br>r7 c3 | [Wonders of Time](https://db.exil.es/spell/560541) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. Additionally, all healing done now has a… |
| Necromancer | Rime<br>r7 c4 | [Chilling Presence](https://db.exil.es/spell/300958) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases the critic… |
| Necromancer | Animation<br>r7 c4 | [Corpse Wagon](https://db.exil.es/spell/503738) |  | none | — | Instant | Increases all damage dealt by party and raid members by 3%. Does not stack with similar effects. |
| Necromancer | Rime<br>r4 c8 | [Icecrown](https://db.exil.es/spell/531135) |  | none | — | Instant | Your Frost Damage dealt now increases your allies' critical strike chance against the enemy by 1% for 10 seconds, stacking 3 times. |
| Necromancer | Death<br>r7 c3 | [Apothecary's Cauldron](https://db.exil.es/spell/560537) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your Magic Damage… |
| Necromancer | all | [Improved Razorice](https://db.exil.es/spell/704671) |  | none | — | Instant | Razorice now grants affected allies 5% increased Frost damage. |
| Pyromancer | Draconic<br>r6 c8 | [Inner Flame](https://db.exil.es/spell/301974) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Pyromancer | Incineration<br>r6 c7 | [Fiery Passion](https://db.exil.es/spell/560525) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, your spell haste is increas… |
| Cultist | all | [N'zoth's Cunning](https://db.exil.es/spell/300888) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Cultist | Corruption<br>r5 c4 | [Visions](https://db.exil.es/spell/560526) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, your Shadow Damage is incre… |
| Starcaller | Sentinel<br>r4 c4 | [Elune's Blessing](https://db.exil.es/spell/300876) |  | none | — | Instant | Increases party and raid member's melee and ranged haste by 10%. Does not stack with similar effects. |
| Starcaller | Moon Priest<br>r7 c5 | [Flow of Waters](https://db.exil.es/spell/560539) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your criti… |
| Starcaller | Warden<br>r6 c1 | [Vigil of the Watchers](https://db.exil.es/spell/680709) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Sun Cleric | all | [Seraphim's Guidance](https://db.exil.es/spell/300964) |  | none | — | Instant | Increases party and raid member's physical damage by 3%. Does not stack with similar effects. |
| Sun Cleric | Valkyrie<br>r5 c5 | [March of the Valkyr](https://db.exil.es/spell/560534) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, your chance to parry is in… |
| Sun Cleric | Blessings<br>r6 c8 | [Glaring Rays](https://db.exil.es/spell/804257) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3% and your spell haste by an additional 3%. Does not stack with similar effects. |
| Tinker | all | [Marksmanship](https://db.exil.es/spell/300869) |  | none | — | Instant | Increases party and raid member's attack power by 3%. Does not stack with similar effects. |
| Tinker | Invention<br>r5 c4 | [Fine Tuning](https://db.exil.es/spell/300877) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, not critically heali… |
| Tinker | Demolition<br>r6 c5 | [The BIG Guns!](https://db.exil.es/spell/560593) |  | none | — | Instant | Increases the attack power of all party and raid members 5%. Does not stack with similar effects. In addition, increases your ranged attack … |
| Tinker | Mechanics<br>r6 c4 | [Mechanical Enhancements](https://db.exil.es/spell/706632) |  | none | — | Instant | Increases all party and raid member's melee and ranged haste by 10%. Does not stack with similar effects. In addition, the range of your off… |
| Venomancer | all | [Rune of Haste](https://db.exil.es/spell/300874) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. |
| Venomancer | Rot<br>r7 c4 | [Fungal Link](https://db.exil.es/spell/300959) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, the range of your Rot spell… |
| Reaper | Domination<br>r4 c5 | [Soulsight](https://db.exil.es/spell/300565) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. In addition, dealing direct damag… |
| Reaper | Harvest<br>r6 c4 | [Blood Harvester](https://db.exil.es/spell/300889) |  | none | — | Instant | Increases critical strike chance of all party and raid members by 3%. Does not stack with similar effects. |
| Reaper | Soul<br>r7 c4 | [Death's Presence](https://db.exil.es/spell/520371) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. |
| Reaper | all | [Icecrown](https://db.exil.es/spell/706732) |  | none | — | Instant | Increases your allies' critical strike chance against the enemy by 1% for 10 sec, stacking 3 times. |
| Primalist | Grovekeeper<br>r2 c10 | [Vitality Surge](https://db.exil.es/spell/504214) |  | none | — | Instant | All effective healing done now has a 25% chance to increase the haste of party and raid members by 5% for 20 seconds. Does not stack with si… |
| Primalist | Geomancy<br>r6 c4 | [Molten Fervor](https://db.exil.es/spell/680476) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, increases your spell haste … |
| Primalist | all | [Primal Hunger](https://db.exil.es/spell/706154) |  | none | — | Instant | Causes critical strikes to restore 2% maximum Health. Cannot occur more than once every sec. Also increases all party and raid members' atta… |
| Primalist | Wildwalker<br>r7 c2 | [Killer's Path](https://db.exil.es/spell/706633) |  | none | — | Instant | Increases the attack power of party and raid members by 5%. Does not stack with similar effects. In addition, increases your critical strike… |
| Runemaster | Riftblade<br>r7 c3 | [Runic Power](https://db.exil.es/spell/300944) |  | none | — | Instant | Increases the all damage dealt by party and raid members by 3%. Does not stack with similar effects. In addition, critical strikes now incre… |
| Runemaster | Glyphic<br>r6 c6 | [Runes of Quickness](https://db.exil.es/spell/560527) |  | none | — | Instant | Increases the spell haste of all party and raid members by 3%. Does not stack with similar effects. In addition, the range of your Glyphic s… |
| Runemaster | Engravement<br>r6 c3 | [Leyline Disturbance](https://db.exil.es/spell/560540) |  | none | — | Instant | Increases melee and ranged haste of party and raid members within 100 yds by 10%. Does not stack with similar effects. Additionally, the dur… |
```

</details>

**79 across 21 classes.**
Every class has one.

## 10c. Long-duration raid buffs

Group buffs lasting **ten minutes or more** -- the `Greater Power Wuju` / `Witching Edict` / `Toxic Pheromones` family. Buff-check items, not raid cooldowns, so they are kept out of both damage tables.

Sorted on the DURATION field rather than the text: ten of these carry `duration_ms 1800000` and their tooltips never say "30 min" at all, so a text rule misses every one of them and files them as raid cooldowns.

| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | all | [Power Wuju](https://db.exil.es/spell/707671) |  | none | 8% mana | Instant | Give an ally some wuju mon, increasing their melee and ranged attack power by 30. Lasts 30 min. Can only have 1 Wuju active on a target at a… |
| Witch Doctor | all | [Greater Power Wuju](https://db.exil.es/spell/712458) ⚠ |  | none | 16% mana | Instant | Give all party and raid members some wuju mon, increasing their melee and ranged attack power by 232. Lasts 30 min. Can only have 1 Wuju act… |
| Witch Hunter | all | [Greater Witching Edict](https://db.exil.es/spell/681442) ⚠ |  | none | 20% mana | Instant | Declare a witching edict to all party and raid members, increasing their spell power by 62. |
| Witch Hunter | all | [Witching Edict](https://db.exil.es/spell/707684) ⚠ |  | none | 10% mana | Instant | Create a magic edict with an ally, increasing their spell power by 25. |
| Knight of Xoroth | all | [Mark of Blaumeux](https://db.exil.es/spell/707693) ⚠ |  | none | — | Instant | Mark an ally with the power of Blaumeux, increasing their spell power by 25 and Shadow Resist by 15 for 30 min. |
| Knight of Xoroth | all | [Greater Mark of Blaumeux](https://db.exil.es/spell/712460) ⚠ |  | none | — | Instant | Mark nearby party and raid members with the power of Blaumeux, increasing their spell power by 62. |
| Templar | all | [Tithe of Might](https://db.exil.es/spell/804784) |  | none | — | 3s | Emanate an aura for 1 hour, empowering party and raid members with 3% increased critical strike chance. |
| Ranger | all | [Greater Woodsman's Adaptation](https://db.exil.es/spell/680294) |  | none | 50 focus | Instant | Enhance your party and raid members focus, increasing their melee and ranged attack power by 232. Lasts 30 min |
| Ranger | all | [Woodsman's Adaptation](https://db.exil.es/spell/800266) |  | none | 20 focus | Instant | Enhance an ally's focus, increasing their melee and ranged attack power by 30. Lasts 30 min |
| Necromancer | all | [Grim Mandate](https://db.exil.es/spell/572787) ⚠ |  | none | 90 mana | Instant | Places a Mandate on the friendly target, increasing spell power by 37 for 30 min. |
| Necromancer | all | [Greater Grim Mandate](https://db.exil.es/spell/572790) |  | none | 90 mana | Instant | Empowers raid and party members with a dark Mandate, increasing spell power by 62 for 30 min. |
| Cultist | all | [Whispers of C'thun](https://db.exil.es/spell/572791) |  | none | 5% mana | Instant | Gift an ally with the madness of C'thun, increasing spell power by 37 for 30 min. |
| Cultist | all | [Greater Whispers of C'thun](https://db.exil.es/spell/573067) |  | none | 10% mana | Instant | Gift nearby allies with the madness of C'thun, increasing spell power by 62 for 30 min. |
| Sun Cleric | all | [Devotion of Dawn](https://db.exil.es/spell/572384) ⚠ |  | none | 5% mana | Instant | Places a Devotion on the friendly target, increasing attack power by 35 for 30 min. Players may only have one Devotion on them per Sun Cleri… |
| Sun Cleric | all | [Greater Devotion of Dawn](https://db.exil.es/spell/572390) ⚠ |  | none | 15% mana | Instant | Places a Devotion on all raid and party members, increasing attack power by 232 for 30 min. Players may only have one Devotion on them per S… |
| Sun Cleric | all | [Devotion of Radiance](https://db.exil.es/spell/575040) ⚠ |  | none | 5% mana | Instant | Places a Devotion on the friendly target, increasing spell power by 28 for 30 min. Players may only have one Devotion on them per Sun Cleric… |
| Sun Cleric | all | [Greater Devotion of Radiance](https://db.exil.es/spell/575045) ⚠ |  | none | 15% mana | Instant | Places a Devotion on all raid and party members, increasing spell power by 62 for 30 min. Players may only have one Devotion on them per Sun… |
| Tinker | all | [Greater Power Module](https://db.exil.es/spell/680315) ⚠ |  | none | 9% mana | Instant | Activates power module on raid and party members, increasing attack power by 232 for 30 min. Only one Module per Tinker can be active. |
| Tinker | all | [Power Module](https://db.exil.es/spell/706742) |  | none | 9% mana | Instant | Activates power module on an allied player, increasing attack power by 19 for 30 min. Only one Module per Tinker can be active. |
| Venomancer | all | [Toxic Pheromones](https://db.exil.es/spell/707689) |  | none | 12% mana | Instant | Create a magic edict with an ally, increasing their spell power by 28. |
| Venomancer | all | [Greater Toxic Pheromones](https://db.exil.es/spell/712459) |  | none | 12% mana | Instant | Create a magic edict with an ally, increasing their spell power by 62. |
| Primalist | all | [Greater Primal Instinct](https://db.exil.es/spell/680310) ⚠ |  | none | 10% mana | Instant | Invokes an Instinct in all raid and party members, increasing attack power by 232 for 30 min. |
| Primalist | all | [Primal Instinct](https://db.exil.es/spell/800197) |  | none | 5% mana | Instant | Invokes a savage instinct on a friendly target, increasing attack power by 30 for 30 min. Players may only have one Instinct on them per Pri… |

<details><summary>Copy this table as markdown</summary>

```markdown
| Class | Spec | Ability | Usable on Boss | CD | Materials Required | Cast Time | Description |
|---|---|---|---|---|---|---|---|
| Witch Doctor | all | [Power Wuju](https://db.exil.es/spell/707671) |  | none | 8% mana | Instant | Give an ally some wuju mon, increasing their melee and ranged attack power by 30. Lasts 30 min. Can only have 1 Wuju active on a target at a… |
| Witch Doctor | all | [Greater Power Wuju](https://db.exil.es/spell/712458) ⚠ |  | none | 16% mana | Instant | Give all party and raid members some wuju mon, increasing their melee and ranged attack power by 232. Lasts 30 min. Can only have 1 Wuju act… |
| Witch Hunter | all | [Greater Witching Edict](https://db.exil.es/spell/681442) ⚠ |  | none | 20% mana | Instant | Declare a witching edict to all party and raid members, increasing their spell power by 62. |
| Witch Hunter | all | [Witching Edict](https://db.exil.es/spell/707684) ⚠ |  | none | 10% mana | Instant | Create a magic edict with an ally, increasing their spell power by 25. |
| Knight of Xoroth | all | [Mark of Blaumeux](https://db.exil.es/spell/707693) ⚠ |  | none | — | Instant | Mark an ally with the power of Blaumeux, increasing their spell power by 25 and Shadow Resist by 15 for 30 min. |
| Knight of Xoroth | all | [Greater Mark of Blaumeux](https://db.exil.es/spell/712460) ⚠ |  | none | — | Instant | Mark nearby party and raid members with the power of Blaumeux, increasing their spell power by 62. |
| Templar | all | [Tithe of Might](https://db.exil.es/spell/804784) |  | none | — | 3s | Emanate an aura for 1 hour, empowering party and raid members with 3% increased critical strike chance. |
| Ranger | all | [Greater Woodsman's Adaptation](https://db.exil.es/spell/680294) |  | none | 50 focus | Instant | Enhance your party and raid members focus, increasing their melee and ranged attack power by 232. Lasts 30 min |
| Ranger | all | [Woodsman's Adaptation](https://db.exil.es/spell/800266) |  | none | 20 focus | Instant | Enhance an ally's focus, increasing their melee and ranged attack power by 30. Lasts 30 min |
| Necromancer | all | [Grim Mandate](https://db.exil.es/spell/572787) ⚠ |  | none | 90 mana | Instant | Places a Mandate on the friendly target, increasing spell power by 37 for 30 min. |
| Necromancer | all | [Greater Grim Mandate](https://db.exil.es/spell/572790) |  | none | 90 mana | Instant | Empowers raid and party members with a dark Mandate, increasing spell power by 62 for 30 min. |
| Cultist | all | [Whispers of C'thun](https://db.exil.es/spell/572791) |  | none | 5% mana | Instant | Gift an ally with the madness of C'thun, increasing spell power by 37 for 30 min. |
| Cultist | all | [Greater Whispers of C'thun](https://db.exil.es/spell/573067) |  | none | 10% mana | Instant | Gift nearby allies with the madness of C'thun, increasing spell power by 62 for 30 min. |
| Sun Cleric | all | [Devotion of Dawn](https://db.exil.es/spell/572384) ⚠ |  | none | 5% mana | Instant | Places a Devotion on the friendly target, increasing attack power by 35 for 30 min. Players may only have one Devotion on them per Sun Cleri… |
| Sun Cleric | all | [Greater Devotion of Dawn](https://db.exil.es/spell/572390) ⚠ |  | none | 15% mana | Instant | Places a Devotion on all raid and party members, increasing attack power by 232 for 30 min. Players may only have one Devotion on them per S… |
| Sun Cleric | all | [Devotion of Radiance](https://db.exil.es/spell/575040) ⚠ |  | none | 5% mana | Instant | Places a Devotion on the friendly target, increasing spell power by 28 for 30 min. Players may only have one Devotion on them per Sun Cleric… |
| Sun Cleric | all | [Greater Devotion of Radiance](https://db.exil.es/spell/575045) ⚠ |  | none | 15% mana | Instant | Places a Devotion on all raid and party members, increasing spell power by 62 for 30 min. Players may only have one Devotion on them per Sun… |
| Tinker | all | [Greater Power Module](https://db.exil.es/spell/680315) ⚠ |  | none | 9% mana | Instant | Activates power module on raid and party members, increasing attack power by 232 for 30 min. Only one Module per Tinker can be active. |
| Tinker | all | [Power Module](https://db.exil.es/spell/706742) |  | none | 9% mana | Instant | Activates power module on an allied player, increasing attack power by 19 for 30 min. Only one Module per Tinker can be active. |
| Venomancer | all | [Toxic Pheromones](https://db.exil.es/spell/707689) |  | none | 12% mana | Instant | Create a magic edict with an ally, increasing their spell power by 28. |
| Venomancer | all | [Greater Toxic Pheromones](https://db.exil.es/spell/712459) |  | none | 12% mana | Instant | Create a magic edict with an ally, increasing their spell power by 62. |
| Primalist | all | [Greater Primal Instinct](https://db.exil.es/spell/680310) ⚠ |  | none | 10% mana | Instant | Invokes an Instinct in all raid and party members, increasing attack power by 232 for 30 min. |
| Primalist | all | [Primal Instinct](https://db.exil.es/spell/800197) |  | none | 5% mana | Instant | Invokes a savage instinct on a friendly target, increasing attack power by 30 for 30 min. Players may only have one Instinct on them per Pri… |
```

</details>

**23 across 11 classes.**
None found for: Barbarian, Bloodmage, Chronomancer, Felsworn, Guardian, Pyromancer, Reaper, Runemaster, Starcaller, Stormbringer.

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

## ! and ⚠ -- is it actually in the game?

**! = in-game verification in process.** db.exil.es has the spell and
db.ascension.gg has no record of it at all -- the ability is on ONE of the two
databases, which is the shape a cut, renamed or never-implemented row takes.

**⚠ = no icon art anywhere reachable.** db.ascension.gg is the only art source
this project has -- db.exil.es returns 22 keys per spell and not one of them is
an icon -- so a row with no texture there has none. 43 of the 260 rows are in
that state and every one of them is marked, because the hand-picked subset that
used to be marked was not a judgement about which rows deserved doubt, it was
whichever ids somebody had happened to look at.

**Every row on this page has now been asked of both databases** -- 259 spell
ids, `tools/crosscheck.py`, recorded in `resources/cross-source.json`. 246 are
the same id with the same name on both. One more is on both under two
different ids: Tinker's `Distracto Shot` is 560470 here and 561269 there, same
4% mana, same interrupt tooltip. THE ID IS NOT THE JOIN KEY, and an id-only
check would have called that one missing.

The remaining twelve are db.exil.es only. Five of the twelve have a namesake
on db.ascension.gg and three of those namesakes are a different ability
wearing the same word -- Bloodmage's `Siphon` steals two buffs here and
summons three skeletons there. Tooltips were read side by side; the verdicts
are in `cross-source.json`.

**Confirmed absent = removed from the tables entirely.** Two so far, both
checked in game and both with no art: Barbarian's `Wrist Snap` (2026-08-02) and
Tinker's `Build: Noise Box` (2026-08-03). Neither is annotated, both are gone --
a struck-through row still reads as an option at a glance, and the point of
checking was to stop planning around it. `resources/icon-missing.json` keeps
the record under `confirmed_absent` so nobody re-adds them.

Removing `Wrist Snap` cost Barbarian nothing; it had two interrupts listed and
one was never real. Removing `Build: Noise Box` costs Tinker more than it
looks, because the row it takes with it is `Distracto Shot` -- the box was the
only thing that cast it. **Tinker's whole interrupt column is now one pet
ability**, `Meltdown`, at 5 yards off the Rusthound's bar.

**WHICH MARK IS WORTH MORE, and it is the reverse of what this section used to
say.** Seven no-art abilities have been checked in game and two were absent --
`Wrist Snap` and `Build: Noise Box` -- against five real ones (`Hellgaze`,
`Throatpunch`, `Halt`, `Solar Burn`, `Distracto Shot`). Roughly 2-in-7.

The cross-source check has done worse on the same sample. `Hellgaze` and
`Solar Burn` have no db.ascension.gg record at all and are both in the game;
`Build: Noise Box` has a complete record there and is not. So:

* **No art is the wider net and the only one that has caught an absence.**
  Every id in the cross-source `no-record` set also has no art, so ⚠ is a
  superset of `!` on the current rows -- ten rows carry both.
* **A record on the second database is not evidence of presence.** That is the
  Noise Box lesson and it cost a Tinker interrupt to learn.

Neither mark is a verdict and a row only leaves this page on an in-game check.
Confirm one, move its id to `confirmed_present` or `confirmed_absent` in
`resources/icon-missing.json`, and regenerate -- a confirmed id drops both
marks, and a confirmed-absent SUMMON takes its pet's ability with it.

## Pets and builds -- can the player aim it?

Six rows are cast by something the class summons, not by the class. The page
prints the button and marks how much control comes with it, because those are
three different answers:

| Mark | Means |
|---|---|
| **(pet — no control)** | A summoned OBJECT firing on a timer. No action bar exists. You choose where and when to drop it and nothing after that. |
| **(pet — pet bar)** | A pet with a multi-ability kit, so a pet action bar exists. Whether THIS ability is manually castable or autocast-only is not in either spell database -- it needs an in-game look. |
| **(pet — passive)** | An aura the pet carries. Nothing to press; the requirement is that the pet is out. |

**Tinker has no player-pressed interrupt.** Both rows in that column are
summons. `Build: Noise Box` (Invention, 90s, 30% mana) drops a *gameobject* --
`effect 28`, misc_value 52036 -- whose aura `807742` is `aura 23`
PERIODIC_TRIGGER_SPELL at **amplitude 3000ms, radius 8 yd, duration 15s**: five
ticks, three seconds apart, at whatever enemy is near the box. `Build:
Rusthound` (Mechanics) gives a permanent pet whose `Meltdown` is a **5 yard**,
30s bite off the pet bar -- the only one of the two that could be fired on
command, and only with the hound already in melee of the target.

For raid planning that is not interrupt cover. It is the difference between
"we have an interrupt on that cast" and "we have a box that might".

**`gcd_ms 0` is not the tell** -- pet kits mix it, Rusthound's `Rustbite` is
1500 and its `Meltdown` is 0. What identifies one is `skill_line` naming a pet
or a build, cross-checked against a summon button in the same class's list.
Both halves are needed: Stormbringer's `Electrifying Aura` has `skill_line
Lightning`, and Lightning is a real Stormbringer SPEC.

The six, and the evidence for each, are in `resources/pet-abilities.json`.

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
* **A pet is not the class.** Six rows are cast by a pet or by a summoned
  object, and db.exil.es files them under the owning class's spell list, so
  they arrived looking like class buttons. The row is rewritten to the
  `Build:` / `Summon:` / `Call` button the player actually presses, and the pet
  ability is named in the description and on a chip. See below.

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

