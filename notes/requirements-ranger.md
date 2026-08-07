---
title: Ranger — class pack requirements
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, ranger, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
---

# Ranger — requirements

Class **21**, token `RANGER`, specs **Archery**, **Brigand**, **Farstrider**.
First build — no pack exists yet.

Research sources, in precedence order used below: the 2026/07/31 changelog
batch (dev statements, newest), db.exil.es spell pages / JSON API (scraped
2026-08-07: `exiles-ranger.json` 577 spells, `spell-meta-ranger.json`),
db.ascension.gg `?spell=<id>&power` tooltips (crossdb sweep), the official
talent builder (`talents-ranger.json`, ascension.gg RSC payload), and the
three Sidekick spec pages scraped 2026-08-07 to
`resources/sidekick-ranger-<spec>.md`.

⚠️ **Sidekick talent-text staleness, known spots.** The scrape is dated
2026-08-07 but its Skirmisher text still reads "reduces the duration of its
damaging effect by -30%" — which the 07/31 changelog explicitly removed
("Skirmisher talent no longer reduces the duration of Toxic Dart"), and the
07/31 merge of Corrosive Poison into the level-10 passive is likewise absent.
Sidekick talent texts therefore predate 2026-07-31 in at least the Archery
tree; treated as a reference with known stale spots, not truth.

**Spec roles.** `resources/spec-roles.md` had no Ranger rows (unknown, not
damage-by-default). What the sources say, citably:

- Archery — "No heal anywhere in the spec: no shield, no HoT, no proc-heal"
  and "Despite the class name, judge it as a pure MM-Hunter DPS spec"
  (sidekick-ranger-archery). → `damage`.
- Brigand — "Brigand is a dagger-wielding melee assassin, not a healer
  despite the archetype tag" and "There is no direct heal spell anywhere in
  this spec, and no Horn auras either" (sidekick-ranger-brigand). → `damage`.
- Farstrider — "It still does meaningful personal ranged damage on its own
  Advantage builder/finisher loop, with only minor incidental healing rather
  than a real HPS rotation … not anything resembling a Discipline/Holy/Resto
  kit" (sidekick-ranger-farstrider). An Augmentation-style buffer that is
  still `damage` in the three-role vocabulary. → `damage`.

No tank kit appears in any of the three pages. All three go into
`spec-roles.md` as `damage`, provenance noted there as Sidekick kit
statements pending in-game observation. **No spec gets a healing target
band; all three get DoT/debuff target bands.**

---

## −1. Changelog — 30 entries, scanned FIRST (2026-08-07, pages 6)

Newest Ranger entry: **2026/07/31**. NOT `--accept`ed until everything below
is built or filed.

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| Archery talent-pacing preamble (tier moves rationale) | 07/31 | tree layout | none — position only |
| Skirmish ↔ Swiftshot, Deadeye ↔ Studded Arrows, Opportunist ↔ Superb Shot position swaps | 07/31 | tree layout | none — position only |
| **Corrosive Poison merged into the level-10 spec passive**; passive now: "Your Toxic Dart deals 30% more damage and ticks 30% faster. Your abilities ignore 25% of target's armor against poisoned targets" | 07/31 | talent removed / passive rework | §2 — Corrosive Poison is no longer a pickable talent; the Sidekick tree text predates this. Skirmisher (92115) remains the L10 archery passive spell |
| Ravage ranks 1–7 damage up; AP scaling 6%→8% | 07/31 | numbers | none |
| Hookshot ranks 1–6 damage up | 07/31 | numbers | none |
| **Skewer/Viper's Bite and Barbed Quills capstones gained a connection; Skewer added to Brigand capstones as a switch node with Viper's Bite** | 07/31 | talent structure | §2 — switch node: a build takes ONE of Skewer (800093, polearm cleave+pull) / Viper's Bite (803104). Both drawn on Brigand's rows, each gated on its own id |
| Skirmisher now also increases Toxic Dart damage 30%; no longer reduces its duration | 07/31 | numbers / rework | §-1 staleness note; no WA change (passive) |
| **Onslaught now 2 min CD, down from 3 min** | 07/31 | cooldown | §0 — exiles' only "Onslaught" row 800361 is "Onslaught Stacks" (component, cd 0) on db.ascension: the castable's id is unresolved in both DBs. Changelog CD noted as ground truth for whatever id the sweep settles; a no-cooldown-row id is never own-id-gated |
| Knuckleduster now increases Bushwhack range | 07/31 | numbers | none |
| Freezing Toxin slow 20%→30% | 07/31 | numbers | none |
| **Cutthroat CD 45 s, down from 1 min** | 07/31 | cooldown | §0 — exiles' only "Cutthroat" row 573280 is rank "Proc" (cd 0) on db.ascension: component, castable id unresolved. Same handling as Onslaught |
| Blur additionally reduces stealth detection | 07/31 | numbers | none |
| Woodland Stalker inverted-uptime bugfix (was active everywhere EXCEPT in Eluder) | 07/31 | bugfix | none — passive aura, no display |
| Waterskins healing +30% | 07/31 | numbers | none |

- [x] changelog scanned, newest Ranger entry: `2026-07-31`
- [x] every replaced/reworked/new-spell entry triaged into the sections below
- [x] `--accept` run after triage (2026-08-07)

---

## 0. Ability surface — both databases

`tools/crossdb_sweep.py ranger` runs over the whole reviewed inventory (every
row with an id); verdicts in `resources/crossdb-ranger.json`, per-row
consequences in the inventory Notes.

Known traps found during id resolution, corrected in the inventory /
`CROSSCHECK`:

Known traps found during id resolution — every one carries a tooltip-read
verdict, in the inventory Notes and in the builder `CROSSCHECK`:

| Name | Wrong id | Why | Castable |
|---|---|---|---|
| Viper's Bite | 520580 (exiles) | db.ascension.gg calls 520580 "Ravaging Venom Cast" — a cast component | **803104** — official talent builder's `spell_ids`; db.ascension tooltip is the full castable (60 Focus, 20 s CD, "Generates 2 Advantage … 4 quick strikes") → `CROSSCHECK` |
| Silent, But Deadly | 524872 (exiles) | thin stub row | **524873** — builder id; full passive text on db.ascension |
| Falcon's Call | 800251 (exiles) | bare "Summons a falcon." — component | **804715** — builder id; full tooltip (30 Focus, 1 min CD, AoE slow + falcon per enemy) → `CROSSCHECK` |
| Knockout | 560425 (exiles) | rank "Cleanser", desc "cleanses dots" — component | **801435** — class-tree id; full tooltip (25 Focus, 18 s CD incap that strips bleeds/poisons) → `CROSSCHECK` |
| Survival Potion | 704341 (exiles) | rank "Dispel Effect" — component | **802839** — class-tree id; full tooltip (1 min CD poison/disease dispel-over-time) → `CROSSCHECK` |
| Dirty Blades | 520571 (exiles) | rank "Leech" — component | **680276** — builder grant → `CROSSCHECK` |
| Poison Quiver | 500104 (exiles) | 500104 is the stacking TARGET DEBUFF ("Increases damage taken … stacking 5 times", 15 s) | no separate castable row surfaced; long-term entry + `NO QUIVER` alert match the self-state by NAME, any-of (§6.3) |

No-record rows (db.ascension has neither the id nor a name hit —
`dbsearch` re-ask, 0 hits each):

| Name | Verdict |
|---|---|
| Brigand Strike 802562 | exil.es desc is literally "Deprecated" — the cut-ability shape, `ignore` |
| Toxicant 561045 | only exil.es (Rank 3) + the skillbook know it, no rotation cites it — one-source ability, NOT shipped (`ignore`, §6.7) |
| Emerald Arrow 804712 | kept: the operator's own talent builder grants exactly this id, exil.es renders the full Rank 1 tooltip, and the Farstrider rotation presses it — db.ascension judged behind |
| Whipvine Arrow 806342 | kept on the same three-way evidence (builder grant + exil.es 1-min-CD tooltip + cited rotation) |

- [x] every inventory row with an id cross-checked against both DBs (sweep —
      230/230 asked, `resources/crossdb-ranger.json`)
- [x] `no-record` rows resolved by name re-ask + tooltip read, verdict in Notes
- [x] deprecated/placeholder names filtered (Deprecated / UNUSED / unused-horn rows binned `ignore` with reasoning)

---

## 1. Mandatory buffs

**Class-wide.**

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Advantage** (aura **804329**, duration −1, "Consumed by some abilities to boost their effectiveness"; applier chain 503830 → 804329) | class economy | every spec is a Focus/Advantage builder-spender: builders (Quick Shot +1, Hunting Shot +1/enemy, Ravage +1, Wild Strike +1 (+1 Ravager), Deadshot +2, Viper's Bite +2, Skewer +1, Falconstrike +2) vs spenders that scale per stack spent (Precision Shot, Skullpiercer, Serrated Shot, Incendiary Shot, Skirmish, Assault, Emerald Arrow, Whipvine Arrow, Woodland Arrow). Cap 5 — "Spend Skullpiercer at 5 Advantage" (Sidekick brigand), "used with 5 stacks of Advantage" (Phoenix Plumes / Forest Fighter tooltips) | resource envelope: 5-cell `stack_bar`, all three specs — §4 |
| **Focus** (power resource, "Hunter-Focus or Rogue-Energy style regen" — Sidekick, all three Resource paragraphs) | class economy | nearly every button costs it | resource envelope: power bar (typeless `UnitPower` read — §6.1) |
| **Quiver family** — Poison / Searing / Hunting / Skirmisher's / Light / Verdant ("Only 1 Quiver may be active at a time. Shares a cooldown with other Quivers" — every quiver tooltip) | class kit | "Keep one Quiver active" opens the Archery solo rotation; a missing quiver is quiet throughput loss | long-term band (active-only, one lights up) + `NO QUIVER` alert on Archery (§5) |
| **Elude** (800701, stealth) | class kit | the opener window (Archery: "Elude stealth-window abilities"; Brigand: Bushwhack/Flank from behind) | "on me" row, active-only |
| **Adrenaline Rush** (520578) | class kit | mobility/burst window | utility row + "on me" |

**Archery.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Silent, But Deadly** proc | talent 524873: "Direct Physical damage dealt now has an 8% chance to allow you to use Deadshot regardless of the targets health for 8 sec" | the execute button outside its window — must-press | `PROC_GLOW` on Deadshot; proc aura name-matched (§6.2) |
| **Skirmish** (802039) | spec ability: crit + Focus-cost reduction, "Lasts … for each stack of Advantage" | the burst window the whole sequence sharpens around (Sidekick strengths) | "on me" + offensive row |
| **Serrated Shot** bleed on target | spec spender | the bleed to maintain | target band |
| **Toxic Dart** on target (807237) | class DoT (Skirmisher passive buffs it 30%) | the poison that feeds the L10 armor-ignore | target band |

**Brigand.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Guile of the Cutthroat** (560531) | talent: party/raid +5% AP passive aura | the spec's one support tool — presence check | long-term band |
| **Dirty Blades** | talent (builder 680276): 4 s auto-attack Nature window, extended per Advantage | an active window worth seeing run | "on me" |
| **Ravage** bleed on target (803851) | builder: "Ravage an enemy, causing them to bleed out" | Viper's Bite hits harder vs bleeding — the engine's fuel | target band |
| **Barbed Quills** bleed on target (560965, stacks 4) | talent: Wild Strike/Quills tear, 9 s | stacking-bleed layer Viper's Bite feeds on | target band, stacks |
| **Bounty** debuff on target (560722, via Bounty Hunter 803114: Flank/Rusty Shiv, +25% Advantage-spender damage, 8 s) | talent | spender-amp window | target band |
| **Toxic Dart** on target | class DoT | poison state for Viper's Bite's Nature conversion | target band |

**Farstrider.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Horn of War** (800086, crit) / **Horn of Alacrity** (806360, haste + self Focus/s) | spec talents, shared Horn cooldown | "a skilled Ranger keeps a Horn up far more than the raw cooldown suggests" — the spec's identity | offensive row icons + "on me" active-only |
| **Battle Screech** (705070), **Battle Prowess** (805888), **Defense of the Ancients** (705094), **Frenzy** (520492), **Command Aura** (524600) | spec talents, party buffs | the Augmentation layer, layered "as the pull demands" | long-term band |
| **Thalassian Brand** on target (560805) | talent: ally-RAP mark + Nature DoT | the priority-target mark | target band |
| **Toxic Dart** on target | DoT layer | "Open tougher fights with Toxic Dart and Quel'dorei Poison" — but Quel'dorei Poison itself is a PASSIVE on both DBs (a 3 s poison rider on Woodland/Emerald Arrow), so only Toxic Dart is a refresh decision | target band |
| **Wingman** (talent 705098: −2% damage taken per active Falcon/Dragonhawk) | talent | the defensive ramp falcons feed | "on me", name-matched, hedged (§6.4) |

**Missing-buff alerts** (§5): `NO QUIVER` (Archery — the one spec whose
rotation text opens with "Keep one Quiver active"). No `NO HORN` alert:
Horns are rotational cooldowns with a shared CD, not set-and-forget state —
the cooldown icon carries them. No pet alert — no permanent pet (§3).

---

## 2. Talent-driven rotation changes

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| **Falconstrike** (Farstrider) | passive 573060 | "Every 5th Quick Shot within 15 sec transforms into Falconstrike. Using a Horn instantly transforms Quick Shot into Falconstrike" (db.ascension 573060) | the builder button periodically becomes a 2-Advantage falcon strike | TRANSIENT transform, not a permanent replacement — `spell_swap`-style variant tracking needs the strike spell's own id, which no source carries (§6.5). Quick Shot stays the tracked button; the transform window is visible on the button itself in game |
| **Skewer ⇄ Viper's Bite** (Brigand capstones) | 800093 / 803104 | 07/31: switch node — a build takes one | the 5-Advantage dump differs per build | both drawn on Brigand rows, each leaf gated on its OWN spell id (`load.spellknown`), so whichever the character knows renders — the pack reads correctly with either |
| **Silent, But Deadly** (Archery, choose-one) | 524873 | 8% chance: Deadshot usable regardless of health, 8 s | execute outside the window — must-press | `PROC_GLOW["Deadshot"]`, aura name-matched (§6.2) |
| **Archery Master** (Archery) | 706281 | Quick Shot crits generate +1 Advantage | faster banking | no display change — the Advantage bar shows it |
| **Ravager** (Brigand L10) | 92116 | Wild Strike +1 Advantage; removes ranged minimum range | loop speed | no display change |
| **Rub It In** (Brigand L30) | 705085 | 20%/stack refund on spend | spend cadence | no display change — bar shows it |
| **Bounty Hunter** (Brigand) | 803114 | Flank/Rusty Shiv apply Bounty (+25% spender damage, 8 s) | spender-amp window to exploit | Bounty in the target band |
| **Barbed Quills** (Brigand, choose-one) | 560965 | Wild Strike/Quills apply a 4-stack bleed; Quills spreads periodics | bleed layer | target band entry; untalented it simply never fires (active-only) |
| **Forest Fighter** (Farstrider) | 706282 | 5-stack Skullpiercer/Emerald Arrow −5 s Woodland Arrow CD | horn-chain speed | no display change |
| **Phoenix Plumes** (Farstrider) | tree node | 5-stack Skullpiercer/Woodland Arrow restore 3% Focus + War Falcon | sustain | no display change |
| **Blow the Horns!** (Farstrider) | 573042/300464 | Horn CD −25% | horn uptime | cooldown icon reflects real CD at runtime |
| **Wingman** (Farstrider, choose-one) | 705098 | −2% damage taken per Falcon/Dragonhawk | defensive ramp | "on me" name-matched entry (§6.4) |
| **Dragonhawk Tamer** (Farstrider, choose-one) | 573056 | Horns also summon a Dragonhawk | more Wingman fuel | none — temp summon (§3) |
| **Falcon Diving** (Farstrider, choose-one) | 520783 | kills summon a War Falcon (12 s) | leveling cleave | none — temp summon (§3) |
| **Corrosive Poison** | — | REMOVED 07/31 — merged into the L10 spec passive | — | not drawn anywhere; if it survives in a scrape it is stale data |

With/without check: every row above except the Skewer/Viper's Bite switch
only ADDS an active-only display (proc, DoT, buff), which is correct
untalented — it never fires. The switch node is handled by own-id gating on
both leaves, so both builds read correctly.

---

## 3. Pets

- [x] Does this class summon a pet? **No permanent pet on any spec.**
      Farstrider summons **temporary** War Falcons (6 s via Falconstrike /
      Phoenix Plumes, 12 s via Falcon's Call / Falcon Diving) and Dragonhawks
      (via Dragonhawk Tamer) — cooldown-length fire-and-forget adds, the
      "Maelstrom water elemental" shape, not a §3 pet. Archery and Brigand
      summon nothing.
- [x] Player-pressed pet abilities: none — falcons act on their own
      ("threat-free extra damage … Let Dream Flowers and Falcon/Dragonhawk
      adds provide passive off-heal and extra damage", Sidekick farstrider).
- [x] Pet buffs/debuffs to track: only the PLAYER-side Wingman ramp (§1
      Farstrider, hedged §6.4). Falcon presence itself is not tracked — 6–12 s
      lifetimes make a presence icon churn without a decision attached.
- [x] Pet presence gating the rotation: no — nothing casts *through* the
      falcons; no alert.
- [x] Pet resource: none anywhere in the three pages.

The 7 "pet-ish" inventory mentions resolved from tooltips: Falcon-family
summons above (`ignore` as buttons where passive, utility where castable —
Falcon's Call 804715 is a real castable slow), `Falcon Scaling` (800249) /
`Falcon Scout` (561395) / `Falcon Guide` (520586) components or class-tree
passives per row Notes, Dragonhawk Tamer 573056 passive.

| Pet | Summoned by | Duration | Track | Renders |
|---|---|---|---|---|
| War Falcon | Falconstrike / Falcon's Call / Falcon Diving / Phoenix Plumes | 6–12 s | nothing (fire-and-forget) | — |
| Dragonhawk | Dragonhawk Tamer (on Horn) | temp | nothing | — |

---

## 4. Primary damage source and the main bar

Press orders below come from the Sidekick per-spec rotation text (solo /
dungeon paragraphs), imported as citations; the "optimal order isn't settled"
caveat is carried on every one.

| Spec | Primary damage | Main row, in press order | Icons | Resource / segments |
|---|---|---|---|---|
| Archery | Advantage spenders (Precision Shot dump) | Quick Shot · Hunting Shot · Precision Shot · Skullpiercer · Serrated Shot · Deadshot | 6 | Advantage 5-cell `stack_bar` + Focus bar |
| Brigand | Advantage spenders vs a bleeding target | Ravage · Wild Strike · Viper's Bite · Assault · Skullpiercer | 5 | Advantage 5-cell `stack_bar` + Focus bar |
| Farstrider | Advantage finishers (Skullpiercer / Emerald Arrow) | Quick Shot · Skullpiercer · Emerald Arrow · Woodland Arrow · Toxic Dart | 5 | Advantage 5-cell `stack_bar` + Focus bar |

Row reads, from the cited text:

- **Archery** (dungeon ST priority, quoted): "Run single-target priority
  (Precision Shot dump > Skullpiercer > Serrated Shot > Deadshot execute) …
  once Advantage is banked", builders "Open with Hunting Shot on cooldown …
  Fill gaps with Quick Shot". Deadshot sits last as the execute.
- **Brigand** (solo/dungeon, quoted): "Ravage first to lay the bleed …
  Weave Wild Strike … Fire Viper's Bite whenever the target is bleeding …
  Dump with Assault … below 20% … Spend Skullpiercer at 5 Advantage".
  Skewer (if talented over Viper's Bite) rides the offensive row via its own
  gate.
- **Farstrider** (solo, quoted): "Quick Shot to build Advantage. Dump into
  Skullpiercer (hits hardest at full stacks) or Emerald Arrow … Open tougher
  fights with Toxic Dart and Quel'dorei Poison … Swap to Whipvine Arrow as
  your finisher when you need to keep moving"; dungeon: "chain Woodland
  Arrow during the pull to shave the Horn cooldown". Woodland Arrow makes
  the main row (the horn-chain is the spec's stated identity); Whipvine
  Arrow is the mobility swap → offensive row.

- **Advantage meter** — one aura (**804329**), stacks 0–5, duration −1.
  5-cell `stack_bar`, the ember/fragment shape (`aura_stacks`).
- **Focus bar** — power trigger with `use_powertype` OFF: reads the unit's
  ACTIVE power, whatever type the server exposes Focus as (§6.1) — the one
  reading that cannot pick the wrong column.
- Narrowest main row is 5 icons (Brigand, Farstrider) → `CD_PER_ROW` from
  `28w − 2 ≤ 1.2 × (5·44 + 4·2 = 228)` → **w ≤ 9.8 → 9**, confirmed against
  `tools/rowwidths.py` on the built packs.

Off the main row, still cited: Incendiary Shot / Brutal Shot (Archery AoE),
Skirmish + Neurotoxin Arrow + Crippling Shot (Archery windows/control),
Bushwhack / Knockout / Throatpunch / Hookshot / Outmaneuver / Flank (Brigand
control kit), Whipvine Arrow / Falcon's Call / Freedom / Backstep
(Farstrider utility), Horns (offensive row), Survival Potion (defensive).

---

## 5. Miss-handling

| Ability / state | Cost of missing it | Cue | Proof the cue fires |
|---|---|---|---|
| Quiver missing (Archery) | quiet throughput loss on every ranged hit | `NO QUIVER` alert: no quiver aura up AND Spell Known on Poison Quiver | inverse aura trigger + spellknown gate, the Runemaster engraving-alert shape; aura-name match is §6.3, in-game post-ship |
| Serrated Shot / Ravage / Barbed Quills / Toxic Dart dropped | bleed/poison uptime lost; Viper's Bite loses its bonus | target-band bars with refresh glow | `dot_bars` refresh condition on aura `expirationTime` (no GCD guard needed on aura triggers), mechanism shipped on 4 classes |
| Silent, But Deadly proc wasted | free execute lost | proc glow on Deadshot | `PROC_GLOW` — glow is `sub.N.glow`; name-matched aura §6.2 |
| Spender pressed with no Advantage | wasted finisher scaling | Advantage cell bar beside the main row; `spellUsable == 0` desaturate covers the unaffordable case | check 9 *desaturate when unusable* |
| Advantage at cap while building | overcap waste | 5-cell bar visibly full next to the main row | visual only — no penalty text exists in any source, so no warning tint invented |
| Deadshot window open (<20% or proc) | execute damage lost | Deadshot in the main row + proc glow | cooldown icon + glow; sub-20% gating is the game's own button state (`spellUsable`) |
| Off-GCD buttons sweeping falsely | phantom cooldown | `use_showgcd` off, derived from `cooldown-abilities-ranger.json` | check 10, both directions |
| Cooldowns coming back | clipped burst | urgency tiers 20/10/5 ANDed `onCooldown == 1` | check 9, *no bare expirationTime tier* |
| Horn window down (Farstrider) | party buff uptime lost | Horn cooldown icons in the offensive row with urgency tiers; active horn shows in "on me" | cooldown swipe + tiers; check 9/10 |

---

## 6. Open questions

- [ ] **6.1 Focus power type.** Every source says Focus is the power
      resource; none says which `UnitPower` column the fork exposes it as
      (focus 2? energy 3?). The bar is built with `use_powertype = false`, so
      it reads the player's ACTIVE power and cannot pick the wrong column;
      the residual risk is a multi-power display quirk. Settles: one in-game
      look at the bar.
- [ ] **6.2 Silent, But Deadly proc aura id.** 524873 is the passive; the
      8-second "Deadshot usable" window presumably leaves an aura whose id no
      database names. Proc glow matched by name "Silent, But Deadly"; may
      never fire. Settles: in-game.
- [ ] **6.3 Quiver self-buff aura ids.** The quiver CASTABLES resolve
      (Searing 500103 dur −1), but whether the self-state aura carries the
      same id per quiver is unverified; the `NO QUIVER` alert and the
      long-term entries match by name + id, any-of. Settles: in-game buff
      tooltip with one quiver up.
- [ ] **6.4 Wingman ramp visibility.** Whether the −2%/falcon DR is exposed
      as a stacking player aura named "Wingman" is unverified — name-matched
      "on me" entry that may never fire. Settles: in-game with falcons up.
- [ ] **6.5 Falconstrike strike-spell id.** 573060 is the passive; the
      transformed button's own castable id appears in no source (the
      "n Falconstrike n" tooltip nests it without linking). Until it is
      known, the main row tracks Quick Shot and the transform is visible on
      the game's own button; a `spell_swap` variant needs the id. Settles:
      in-game spellbook/tooltip read, or a future db row.
- [ ] **6.6 Advantage cap talent modifiers.** Cap 5 is cited from spender
      tooltips; no source mentions a cap-raising talent, but none states
      "maximum 5" outright either. A talented cap above 5 would render as a
      full bar early, which fails safe. Settles: in-game.
- [ ] **6.7 Hedged inventory rows.** The automated role pass's hedged rows,
      by name (reasoning in the inventory Notes; bulk-clear recorded in
      `buildlog-ranger.json`): **Power Shot**, **Falconmark**, **Cannon
      Blast** (stale-blob-only citation), **Beastslayer**, **Venom Blade**,
      **Hydra's Bite**, **Falcon Dive**, **Javelin Toss**, **Uncover
      Weakness**, **Master Marksman** (off-GCD 1-min cd with passive-reading
      tooltip), **Backstreet Justice** (applier unstated), **Onslaught** and
      **Cutthroat** (changelog-real, no castable id in either DB —
      unbuildable), **Toxicant** (one-source, not shipped), **Reposition**
      (rank Deprecated but still referenced by Farstrider's Leap),
      **Farstrider's Command** proc-glow aura name, **Blow The Horns!** stack
      aura id. Feedback and the post-ship in-game sweep are their checklist.
