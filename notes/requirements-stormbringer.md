---
title: Stormbringer — class pack requirements (Phase 0)
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, stormbringer, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[sidekick-stormbringer-lightning]]"
  - "[[sidekick-stormbringer-wind]]"
  - "[[sidekick-stormbringer-maelstrom]]"
---

# Stormbringer — requirements

Class **16**, token `STORMBRINGER`, specs **Lightning**, **Wind**,
**Maelstrom**. First build — no pack exists yet.

Research sources, in precedence order used below: the 2026/07/31–08/06
changelog entries (dev statements, newest), db.exil.es spell pages / JSON API
(scraped 2026-08-07: `exiles-stormbringer.json` 492 spells,
`spell-meta-stormbringer.json` 491 rows), and the three Sidekick spec pages
scraped 2026-08-07 to `resources/sidekick-stormbringer-<spec>.md`. The
Sidekick *rotation blob* (`sidekick-data.js`) snapshot is dated **2026-08-02**,
which POSTDATES the big 07/31 rework — but its maelstrom talent texts still
carry pre-rework wording (see §-1), so it is treated as a reference with known
stale spots, not truth.

**Spec roles.** `resources/spec-roles.md` had no Stormbringer rows (unknown,
not damage-by-default). What the sources say, citably:

- Lightning — "There is no self-heal anywhere in the kit" and every PvE/PvP
  line calls it a damage dealer (sidekick-stormbringer-lightning).
- Wind — "Unlike a real healer it has no ally HP heal at all … a
  buff-shield-and-control support whose only 'sustain' is the Kiss of the
  Clouds absorb, **not** a group's healer" (sidekick-stormbringer-wind). No
  heal, no tank kit → `damage` in the three-role vocabulary, with the caveat
  that it plays as an Augmentation-style buffer around a permanent pet.
- Maelstrom — "It carries no ally heal … There's no healer-grade throughput
  and no ally heal underneath" (sidekick-stormbringer-maelstrom).

All three go into `spec-roles.md` as `damage`, provenance noted there as
Sidekick kit statements pending in-game observation. **No spec gets a healing
target band; Maelstrom gets a DoT/debuff target band.**

---

## −1. Changelog — 13 entries, scanned FIRST (2026-08-07, pages 6)

Newest entry: **2026/08/06**. NOT `--accept`ed until everything below is
built or filed.

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| Drown AoE-pull bugfix | 08/06 | bugfix | none |
| **Ride the Lightning "now on a separate GCD from the main GCD"** | 07/31 | GCD | §5/§6 — the main-global sweep is wrong on this button; db.exil.es still renders `GCD 1.5` so the audit calls it on-GCD. Deferred, see §6.2 |
| Ride the Lightning 40→30 yd | 07/31 | numbers | none |
| Volt no longer scales with haste | 07/31 | numbers | none |
| **Air Elemental gains Cyclonean Protection (804067) + Wind Tunnel (804050)** | 07/31 | new pet spells | §3 — pet abilities, not player buttons; both resolve on db.exil.es |
| **Drown max stacks 6→8** | 07/31 | stacks | §4 — `Drowning` (806406) db desc already says "up to 8 stacks", confirming db.exil.es is post-rework |
| **Unshackle and Windsurf no longer on the GCD** | 07/31 | GCD | §5 — db.exil.es agrees (`gcd_ms 0` on 706625 / 500042), so `audit_cds` derives them off-GCD correctly |
| **Shockingly Powerful: Torrential Wrath crits trigger Conductive directly** | 07/31 | proc rework | §2 — Sidekick page still shows the old "-25% chance to not consume" text: STALE |
| **Conductive "no longer consumes, lower value per stack, stacks higher"** | 07/31 | resource rework | §1/§4 — db.exil.es 92098 desc still says "Torrential Wrath consumes all stacks": STALE there too. Cap now UNKNOWN, see §6.4 |
| Stormcloud can now crit | 07/31 | numbers | none |
| Kinetic Energy 8→10 sec | 07/31 | numbers | none |
| Thorim's Gift 10→15% inherit | 07/31 | numbers | none |
| Flux Arc 8→10 sec | 07/31 | numbers | none |

- [x] changelog scanned, newest entry: `2026-08-06`
- [x] every replaced/reworked/new-spell entry triaged into the sections below
- [ ] `--accept` only after the pack is built against these

---

## 0. Ability surface — both databases

`tools/crossdb_sweep.py stormbringer` runs over the whole reviewed inventory
(every row with an id); verdicts recorded in `resources/crossdb-stormbringer.json`
and per-row consequences written into the inventory Notes.

Known traps found during id resolution (db.exil.es side), all already
corrected in the inventory:

| Name | Wrong id | Why | Castable |
|---|---|---|---|
| Stormcloud | 572128 | rank `Proc` — the cloud effect, not the button; db.exil.es has NO castable row | **801859** on db.ascension.gg: 42% mana, instant, 1 min CD, talent tooltip verbatim → `CROSSCHECK` in the builder |
| Conduction | 567560 | rank `Damage` — Torrential Wrath's payoff component, never a button | n/a — `ignore` |
| Thorim's Fury | 802702 | rank `Duration +` — a component; **no CoA castable of this name exists**. The Sidekick rotation blob still cites it for Lightning's burst window — stale, aliased to null |
| Electrify | — | no record in either DB; cited by the Maelstrom blob's cooldown line — aliased to null |

A large *legacy layer* also surfaced: `Supercharge` (806496), `Thorim's
Amusement/Respect/Favor`, `Crackling Surge`, `Summon: Thunder Orb` (801802),
`Megawatt Missile`, `Orb Siphon`, `Stormforged Strike` — the pre-CoA hero-class
Stormbringer economy. None of it appears in any of the three CoA spec pages'
talent trees or rotation text. Kept out of every band; `no-record` /
kit-membership verdicts per row in the inventory. See §6.7.

- [x] every inventory row with an id cross-checked against both DBs (sweep)
- [x] `no-record` rows resolved by name re-ask + tooltip read, verdict in Notes
- [x] deprecated/placeholder names filtered (`DEPRECATED`, `Unused`, `NEEDS REDONE`)

---

## 1. Mandatory buffs

**Class-wide.**

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Static** (aura **803102**, stacks 0–100, duration −1) | class economy | Every spec is build-and-spend on it: generators (Volt ticks 2, Forked Lightning 5/enemy, Gale 20, Brine 25, Shock 20, Electrocute 20, Charge 100) vs spenders (Call Lightning 50, Arm of Thorim ALL, Aeroblast 50, Unshackle 50, Torrential Wrath 50, Stormflow 20, Thunder Ward ALL…). db.exil.es 803102: player aura, "Stack 100", "While out of combat, your Static will begin to fizzle out" | resource envelope, all three specs — see §4 |
| **Storm Ascendance** (681110, 2 min CD, 15 s) | class CD | the burst window; Lightning's Lord of Lightning rides it | offensive row + running-CD icon in "on me" |
| **Stormcloak** (804833, 30 s CD, 15 s) | class | mitigation + Static generation window | defensive row + "on me" |
| **Charge** (804826, 60 s CD) | class | 100 Static + 30% haste for next cast, 10 s window — press-and-spend cue | offensive row + "on me" |
| **Aegis family** — Shocking Aegis (680316), Whirlwind Aegis, Tempest Aegis | class kit | "Can only have 1 Aegis up at a time" — a set-and-forget hour-class self buff; missing = quiet throughput loss | long-term band + `NO AEGIS` alert (§5) |
| **Greater Call of the Lightning** (575846, 30 min) / Greater Call of the Wind / Greater Call of the Storm | class kit | party resist/mana/Intellect empowerment, 30-min self-maintained | long-term band |

**Lightning.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Electrocutioner** proc | spec passive 92096: 5% on spell damage; "Resets the cooldown of Electrocute and makes your next usable regardless of the target's health percentage" | the execute button outside execute range — must-press | `PROC_GLOW` on Electrocute + proc row |
| **Lord of Lightning** (707618 passive → 20 s buff) | talent | the burst window on top of Storm Ascendance | "on me" |
| **Dark Skies** (300593 → 5 stacks) | talent | crit ramp, wiped on crit | "on me", stacks |
| **Storm Chaser** (300612 → 2 stacks, 10 s) | class talent | next Call Lightning faster | "on me", stacks |
| **Electrical Charge** (704149 → 20 stacks) | talent | at 20, spells stop depleting Static for 10 s — a free-dump window | "on me", stacks |
| **Volt** on target (500928, 18 s DoT) | baseline | the maintain DoT and a Static generator | target band |

**Wind.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Air Elemental present** | Summon: Air Elemental 804019 | "Everything hangs on the Air Elemental staying up. Its death or dispel takes your damage with it" | `NO PET` alert (§3, §5) |
| **Invigoration** (680918, 10–15 stacks, on PET) | talent | the pet's damage ramp; additional applications do not refresh | pet section, stacks, `unit="pet"` |
| **Unshackle** (706625 → 15 s buff on pet) | talent | the damage window; extended by Static spends (Wrath of Al'Akir) | pet section + offensive row |
| **Gift of Air** (583254, 30 s on pet) | talent | pet empowerment from Kiss of the Clouds | pet section |
| **Lexicon of Servitude** (520087 → 15 s banked buff) | talent | next summon instant + free — the recovery plan when the pet dies | "on me" + utility row |
| **Tailwind** (804035, 15 s) | talent choice | group haste+damage, crit-extended | "on me" |
| **Aerodynamics** (806124, 15 s) | talent choice | group AP/SP | "on me" |
| **Kiss of the Clouds** shield (500039) | spec | the group absorb, re-applied on cooldown | main row (§4) |

**Maelstrom.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Conductive** stacks | spec passive 92098 (builder: Brine) | decides what Torrential Wrath / Deluge are worth; changelog: no longer consumed, stacks higher | resource envelope segment row (§4) — tracked BY NAME, id §6.4 |
| **Kinetic Energy** (806409 → 3 stacks, 10 s) | talent | crit ramp from Conductive-consuming casts | "on me", stacks |
| **Drown / Drowning** on target (806407 cast → 806406 aura, 8 s, 8 stacks) | spec | the maintain debuff (Sidekick maintain bucket) + heal cut | target band, stacks |
| **Stormcloud** on target (15 s, +20% spell damage taken) | talent | wants to be up before Torrential Wrath | target band |
| **Stormflow** channel (567555, 8 s) | spec | the channel window (instant Brine, leech with Blessing of Lei Shen) | main row CD icon |
| **Predictable Weather** proc (807233) | class talent | next Storm Alert / Torrential Wrath instant | proc row |

**Missing-buff alerts** (§5): `NO AEGIS` (class), `NO CALL` deliberately NOT
alerted (the Greater Calls are party empowerments, not unambiguous self-state —
active-only long-term icons instead), `NO PET` (Wind).

---

## 2. Talent-driven rotation changes

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| **Tempest Sovereign** (Maelstrom) | 560020 (passive) | **transforms Shock → Brine (807105) and Call Lightning → Torrential Wrath (804017)** | the entire Maelstrom builder/finisher loop is the transformed pair | Maelstrom main row tracks the REPLACEMENT ids directly (Brine, Torrential Wrath); base Shock / Call Lightning stay on the other specs' rows only. No icon-swap conditions needed — spec rows already separate them |
| **Freewind** (Wind) | 707359 passive → castable **801873** | **transforms Eye of the Storm into Freewind** (found during the Stormcloud id hunt: ascension 707359 says it outright) | the utility root becomes a line gust | both icons drawn on Wind's utility row; the untalented/talented state shows whichever the character knows. Eye of the Storm's ranked id keeps it class-gated, so neither hides. db.exil.es's 548621 is the Damage component — 801873 is the castable (`CROSSCHECK`) |
| **Raging Zephyr** (Wind) | 704201 | **transforms Whirlpool into Raging Zephyr** (3 charges, 35 s recharge) | the peel button changes identity | Wind utility row carries Raging Zephyr's own id with charges; Whirlpool not drawn on Wind (talent assumed taken — build-defining per Sidekick build). Whirlpool remains findable via inventory if feedback disagrees |
| **Thunder Wave** (Lightning) | 705692 (passive) | 5% chance transforms Forked Lightning into Thunder Wave | a free empowered AoE press | proc-glow on Forked Lightning matched by aura NAME "Thunder Wave"; aura id unverified → §6.5 |
| **Electrocutioner** (Lightning) | 92096 | proc resets Electrocute CD + lifts the 35% health gate | must-press window | `PROC_GLOW["Electrocute"]`, aura by name |
| **Lightning Cage** (Lightning) | 560030, 3 min CD, 30 s | channel-in-place burst window, +50 Static | burst window | offensive row with urgency tiers |
| **Shockingly Powerful** (Maelstrom) | — | post-changelog: Torrential Wrath crits trigger Conductive directly | faster Conductive ramp | no display change; noted so the segment row is not "wrong" when stacks appear without Brine |
| **Predictable Weather** (class) | 807233 | every 30 s next Storm Alert / Torrential Wrath instant | free instant | proc row icon |
| **Hurricanes** (Wind) | 300839 | Unshackle also buffs YOU 15% for 15 s | self window | "on me" buff by name "Hurricanes"/"Unshackle" — self aura id unverified, name match |
| **Nimbus** (Wind) | 704212 | resets Evacuate / Windsurf / Unshackle | recovery button | utility row |
| **Charges** | — | Gale 3 (baseline text), Updraft 2, Stormbreaker 3, Raging Zephyr 3 | — | `CHARGES` table, counts from db.exil.es tooltips |
| **Electrical Charge** (Lightning) | 704149 | at 20 stacks spells stop depleting Static | dump window | stack icon in "on me" |

With/without check: every talent row above except Tempest Sovereign and
Raging Zephyr only ADDS a proc/buff display, which is active-only and thus
correct untalented (never fires). The two transforms assume the talented
state; both are the spec's defining mechanic per Sidekick ("Brine (Shock
transformed via Tempest Sovereign)" is the spec's stated loop) — the layout
assumes them, said here explicitly. An untalented Maelstrom character keeps
class-row Shock via the shared kit; feedback reopens if that read is wrong.

---

## 3. Pets

- [x] Does this class summon a pet? **Wind: YES — permanent Air Elemental**
      (Summon: Air Elemental 804019, duration −1, taught by spec passive 92097
      at L10). **Maelstrom: temporary only** — Electrified Water Elemental
      (573441, 20 s, from Electrified Waters / Static Electricity talent
      procs); a cooldown-length summon, not a §3 pet. **Lightning: none.**
- [x] Player-pressed pet commands (Wind): Flurry (707543, 8 s CD), Skyfall
      (804830, 90 s), Windsurf (500042, 90 s, off-GCD), Unshackle (706625,
      120 s, off-GCD), Invigorate Elemental (520085), Return Wind Spirit
      (revive), Dismiss Elemental. All real cooldown-row entries, not `ignore`.
- [x] Pet buffs to track: Invigoration 680918 (stacks, on pet), Unshackle
      buff (on pet), Gift of Air 583254 (on pet) — `unit="pet"` aura triggers.
- [x] Pet presence gates the rotation: yes — `NO PET` missing-alert for Wind
      (mechanism §6.6).
- [ ] Pet resource: none observed (no focus/energy text anywhere) — nothing
      rendered.

The 10 "pet-ish" inventory mentions, resolved from tooltips:
`Stormbringer Pet Scaling Aura 1–4` (524080–3), `…Scaling Aura` (524784),
`…Periodic Scaling Trigger` (524785), `…Heal Aura Applier` (524783) — scaling
components, `ignore`. `Windpelt` (806016, rank "Air Elemental") — the pet's
own attack, `ignore`. `Cyclonean Protection` (804067) and `Wind Tunnel`
(804050) — the two NEW pet abilities from 07/31: cast by the pet, not the
player; `ignore` as buttons, noted here so the next scrape does not re-ask.

| Pet | Summoned by | Duration | Track | Renders |
|---|---|---|---|---|
| Air Elemental | 804019 (Wind) | permanent | presence; Invigoration stacks; Unshackle; Gift of Air | `NO PET` alert + pet buffs in "on me" band (`unit="pet"`) |
| Electrified Water Elemental | talent procs (Maelstrom) | 20 s | nothing (fire-and-forget) | — |

---

## 4. Primary damage source and the main bar

Press orders below come from the Sidekick per-spec rotation text
(solo/dungeon paragraphs), imported as citations; the Refine caveat ("point
allocation & optimal order aren't settled") is carried on every one.

| Spec | Primary damage | Main row, in press order | Icons | Resource / segments |
|---|---|---|---|---|
| Lightning | Static spenders (Arm of Thorim, Call Lightning) | Volt · Forked Lightning · Call Lightning · Electrocute · Arm of Thorim | 5 | mana bar + **Static meter** |
| Wind | Air Elemental + Static spenders | Gale · Aeroblast · Updraft · Flurry · Kiss of the Clouds | 5 | mana bar + Static meter |
| Maelstrom | Torrential Wrath / Stormflow | Brine · Torrential Wrath · Stormflow · Drown · Deluge | 5 | mana bar + Static meter + **Conductive segments** |

- **Static meter** — one aura (803102), stacks 0–100. Rendered as a segmented
  10-cell bar (one cell per 10 Static) with the exact stack count as a number
  on the bar; spend thresholds (20/40/50) stay readable as cell counts. This
  is `aura_stacks` at a 10-per-cell scale — same mechanism as Pyromancer's
  ember bar, one aura, `useStacks` thresholds.
- **Conductive** (Maelstrom only) — its own thin segment row, 6 cells
  (db.exil.es cap; changelog says "stacks higher" — cap re-check is §6.4).
- Narrowest main row is 5 icons on every spec → `CD_PER_ROW` from
  `28w − 2 ≤ 1.2 × (5·44 + 4·2 = 228)` → **w ≤ 9.8 → 9**, confirmed against
  `tools/rowwidths.py` on the built pack.
- Row widths: all three always-visible rows lock to `row_w(5)`.

Off the main row, still cited: Conjure Storm (AoE, Lightning), Lightning
Cage + Storm Ascendance (burst), Ride the Lightning (mobility), Skyfall /
Unshackle (Wind windows), Stormcloud → offensive row (Maelstrom), Electrocute
on Maelstrom (execute via Storm Synergy; drawn in the offensive row, not
main — it is talent-unlocked there).

---

## 5. Miss-handling

| Ability / state | Cost of missing it | Cue | Proof the cue fires |
|---|---|---|---|
| Volt dropped (Lightning) | Static generation + slow lost | target-band bar with refresh glow ≤4 s | check 4/9 family in `tests/run.py` (target band built by `dot_bars`, refresh condition on aura `expirationTime` — no GCD guard needed on aura triggers) |
| Drown dropped (Maelstrom) | maintain debuff + heal cut lost | target-band bar, refresh glow | same mechanism |
| Electrocutioner proc wasted | free execute lost | proc glow on Electrocute | `PROC_GLOW` — check 9 asserts tiers ANDed with `onCooldown`; glow is `sub.N.glow`, mechanism shipped on 3 classes |
| Arm of Thorim pressed at low Static | wasted finisher | Static cell count next to the main row; desaturate on `spellUsable == 0` covers the unaffordable case | check 9 *desaturate when unusable* |
| Static at 100 | overcap waste — and the Sidekick core-loop line claims an overload penalty ("100% lose 90% health + 10s stun") | number visible on the meter; NO red-tint warning built until §6.1 settles what 100 actually does | deferred — §6.1 |
| Off-GCD buttons sweeping falsely | phantom cooldown | `use_showgcd` off, derived from `cooldown-abilities-stormbringer.json` (Unshackle, Windsurf, Gust of Wind, Mystic Thunder, Storm Ascendance, Charge, Stormcloak, Thunder Ward, Lightning Cage…) | check 10, both directions |
| Cooldowns coming back | clipped burst | urgency tiers 20/10/5 ANDed `onCooldown == 1` | check 9, *no bare expirationTime tier* |
| Aegis missing | quiet throughput loss | `NO AEGIS` alert (fires when none of the three Aegis auras is up — mutually exclusive by tooltip) | inverse aura trigger, `disjunctive` shape same as Runemaster's engraving alerts; verify in-game post-ship |
| Air Elemental dead (Wind) | "its death takes your damage with it" | `NO PET` alert | §6.6 mechanism, then in-game |

---

## 6. Open questions

- [ ] **6.1 Static at 100 — what actually happens?** Sidekick's core-loop
      line for every spec: "Static (70% small dmg bonus, 85% larger bonus,
      100% lose 90% health + 10s stun)". `Reached 100 Static` (803124, "Your
      Static reached 100%!") exists; so does the legacy Supercharge layer,
      which muddies whether the penalty text is CoA-current. Settles: reach
      100 Static in game once. If real, the Static number goes yellow ≥85 and
      red ≥95, exactly the fused-heat pattern.
- [ ] **6.2 Ride the Lightning "separate GCD"** (changelog 07/31). db.exil.es
      still renders `GCD | 1.5 sec` for 800099, so the audit files it on-GCD
      and the icon will sweep with the main global — which the changelog says
      is wrong. `OFF_GCD` is derived, never hand-written, so this stays as
      the audit has it until db.exil.es catches up or an in-game read settles
      it. Deferred deliberately.
- [ ] **6.3 Sidekick rotation-blob staleness** — the blob (2026-08-02) cites
      "Thorim's Fury" (Lightning) and "Electrify" (Maelstrom) as burst
      cooldowns; neither name has a castable CoA id in either database.
      Aliased to null in `aliases-stormbringer.json`. Re-import citations
      after the next Sidekick data refresh.
- [ ] **6.4 Conductive stack aura + cap post-rework.** Passive is 92098; the
      db desc says the stacks live under the same name, cap 6, and still says
      "consumes" — the 07/31 changelog says no longer consumed, "stacks
      higher". Segment row built at 6 cells, matched BY NAME. Settles: one
      in-game read of the buff tooltip at cap.
- [ ] **6.5 Thunder Wave proc signal** — which aura appears when Forked
      Lightning transforms (705692 is the passive; a hidden proc aura is
      likely). Proc glow matched by name "Thunder Wave"; may never fire.
      Settles: in-game.
- [ ] **6.6 Pet-presence trigger mechanism** — `NO PET` is built on a Health
      trigger with `unit="pet"` + `showOnMissing`-style inverse; whether the
      fork's Health prototype reports an absent unit as "missing" (vs never
      firing) is unverified on 3.3.5. Settles: dismiss the pet once in game.
      (Runemaster/Chronomancer never needed a unit-existence inverse.)
- [ ] **6.7 Legacy layer live-ness** — Supercharge (806496), Summon: Thunder
      Orb (801802), Megawatt Missile, Orb Siphon, Stormforged Strike,
      Whirlpool-on-Wind. All excluded from every band this build. If a player
      reports one on a live CoA bar, it becomes a data-change reopen.
- [ ] **6.8 Hurricanes / Unshackle self-buff aura id** (Wind) — name-matched;
      confirm the self aura is named "Hurricanes" in game.
- [ ] **6.9 `prop:`-hedged inventory rows** — the automated role pass's
      hedged rows are listed in the buildlog step note and carried here by
      reference; the in-game sweep walks them.
