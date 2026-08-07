---
title: Witch Hunter — class pack requirements (Phase 0)
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, witch-hunter, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[sidekick-witch-hunter-boltslinger]]"
  - "[[sidekick-witch-hunter-houndmaster]]"
  - "[[sidekick-witch-hunter-black-knight]]"
  - "[[sidekick-witch-hunter-inquisition]]"
---

# Witch Hunter — requirements

Class **15**, token `WITCHHUNTER`, specs **Boltslinger**, **Houndmaster**,
**Black Knight**, **Inquisition** — the first FOUR-spec class through the
process. First build — no pack exists yet.

Research sources, in precedence order used below: the 2026/07/31–08/01
changelog entries (dev statements, newest), db.exil.es spell pages / JSON API
(scraped 2026-08-07: `exiles-witch-hunter.json` 583 spells,
`spell-meta-witch-hunter.json`), and the four Sidekick spec pages scraped
2026-08-07 to `resources/sidekick-witch-hunter-<spec>.md`. The Sidekick
snapshot POSTDATES the newest changelog entry (2026-08-01), but at least one
talent text is provably stale against the changelog (Rearmament, §-1), so
Sidekick is a reference with known stale spots, not truth.

**Spec roles.** `resources/spec-roles.md` had no Witch Hunter rows (unknown,
not damage-by-default). What the sources say, citably
(sidekick-witch-hunter-\<spec\> pages, 2026-08-07):

- Boltslinger — "Middling in arena as a damage dealer" / "Middling in
  battlegrounds as a damage dealer"; kit is escapes + ranged burst, no ally
  heal, no tank tools → **damage**.
- Houndmaster — "Middling in arena as a damage dealer"; "A pet-centric ranged
  spec … Self-healing is light" → **damage**.
- Black Knight — "**Solid main-tank for raid bosses** … Strong dungeon tank —
  AoE pulls and threat"; taunts (Chains of Darkness, Vicious Mockery),
  `Night's Watch` threat toggle, High Threat abilities, Gaze of the Black
  Knight party damage-transfer → **tank**.
- Inquisition — "Solid in arena as a damage dealer"; "Top-tier sustained
  single-target DPS" → **damage**.

All four go into `spec-roles.md`, provenance noted as Sidekick kit statements
pending in-game observation. **No spec heals; no spec gets a healing target
band. Black Knight's target band carries its threat DoT/debuffs.**

---

## −1. Changelog — 29 entries, scanned FIRST (2026-08-07, pages 6)

Newest entry: **2026-08-01**. NOT `--accept`ed until everything below is
built or filed.

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| **Houndmaster L10 passive renamed to Deadeye, + Shadowblast crit +20%** | 08/01 | rename | §2 — the spec's L10 passive is now "Deadeye"; the Sidekick tree still calls it "Houndmaster". Affects SPEC_KNOWN candidate naming, not display content |
| **Houndmaster's Whistle now free at the top of the Houndmaster tree** | 08/01 | pet baseline | §3 — the permanent Shadowhound is baseline for the spec; NO HOUND alert is fair on every talented Houndmaster |
| **Decimate: hound bonus 30→20%, now ALSO buffs the caster (+20% dmg, +30% haste, armor ignore)** | 07/31 | rework | §1/§3 — Decimate is now a self-buff too → running-CD icon in "on me" as well as the pet window. Sidekick tooltip (hounds only) is STALE |
| **Rearmament now causes Traps to incur no cooldown for 8 sec** | 07/31 | rework | §2 — Sidekick still says "resetting the cooldown of all Traps and Decimate": STALE. Cue unchanged (press Rearmament, then traps), text noted |
| Deal with the Devil cost +10% (down from +25%) | 07/31 | numbers | none |
| Night Elf can be Witch Hunter | 07/31 | race | none |
| **Trap Launcher learnable at level 40** (launch traps 30 yd) | 07/31 | new spell | §0 — resolves (802272, 30 s CD); utility row |
| Darkslayer's Lantern interrupts non-players 3 s vs stun-immune | 07/31 | behaviour | none (already an offensive stun row entry) |
| Stake Rank 1–7 damage increased (7 entries) | 07/31 | numbers | none |
| **Brimming Hatred also regens 5% max mana on crit (1/3 s)** | 07/31 | numbers | none — passive, not a display |
| **Tonics: effectiveness +50–100%, duration 15 s → 10 s** | 07/31 | numbers | §1 — tonic buffs are 10 s windows now; buff-row timers carry it |
| Vengeful Intent can trigger from avoided damage | 07/31 | numbers | none |
| **New passive Black Guard in place of Guard Strike (Black Knight tree)** | 07/31 | new talent | §2 — passive, no display |
| **Guard Strike (interrupt) now CLASS-WIDE from trainer at L18, moved out of the Black Knight tree** | 07/31 | moved spell | §0/§4 — the interrupt goes on EVERY spec's utility row (pinned last), not just Black Knight's. db.exil.es 804432 (18 s CD, off-GCD) corroborates |
| Heartless +10/20% (to 25/50%) | 07/31 | numbers | none |
| **Heartseeking Bolt cooldown 15 s → 10 s** | 07/31 | numbers | §4 — cooldown audit read 2026-08-07 postdates this; trust the audit value |
| Stake now ignores armor in execute range | 07/31 | numbers | none |
| **Edicts persist through death** (6 entries: Witching / Knight's / Inquisitor's, plain+Greater, all ranks) | 07/31 | QoL | §1 — Edicts are long-term band rows; persisting through death makes a missing-Edict ALERT even less urgent → active-only icons, no alert |

- [x] changelog scanned, newest entry: `2026-08-01`
- [x] every replaced/reworked/new-spell entry triaged into the sections below
- [ ] `--accept` only after the pack is built against these

---

## 0. Ability surface — both databases

`tools/crossdb_sweep.py witch-hunter` runs over the whole reviewed inventory
(every row with an id); verdicts in `resources/crossdb-witch-hunter.json`,
per-row consequences in the inventory Notes. (Results section filled after
the sweep — see the buildlog crossdb step.)

Known traps found during id resolution (db.exil.es side):

| Name | Id question | Resolution |
|---|---|---|
| Unleash The Hounds / Unleash the Hounds | TWO rows, 800768 vs 807918, same words different capitalisation | tooltip read via sweep; the talent text says "Summon 1 Lesser Shadow Hound … for 20 seconds" |
| Sixfold Shot | 500567 is rank Passive lvl 0 — the L50 passive, not the transformed shot | the TRANSFORM TARGET's castable id is what a Spell Known trigger needs; §6 |
| Witch Hunt | 520551 rank Proc | the Momentum system is not in any Sidekick rotation — legacy/aspirational layer, kept out of bands |
| Collect Bounty / Set Bounty / Coiling Shot / Repeater | stance-kit loop (Crossbow Stance) with real levels in spell-meta | not in any cited rotation; see §6 stance question |

- [x] every inventory row with an id cross-checked against both DBs (sweep)
- [x] `no-record` rows resolved by name re-ask + tooltip read, verdict in Notes
- [x] deprecated/placeholder names filtered (`deprecaetd`, `PLACEHOLDER`, `SLS` stubs)

---

## 1. Mandatory buffs

**Class-wide.**

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Rage** (power) | class economy | Boltslinger/Houndmaster generate and spend it (Damnation "deplete your rage", Witchbane/Shadowblast costs); Black Knight/Inquisition carry a smaller pool (March of the Black King generates, Hunt generates 20) | resource envelope, all four specs — §4 |
| **Mana** (power) | class economy | "Dual Rage and Mana" (Sidekick, boltslinger + houndmaster resource text); Inquisition "Mana, which is unusual for a melee spec … watch your mana in long fights" | resource envelope |
| **Tonic up** — Witchblood / Vampiric / Surging / Pyro / Dark / Holy Water | class kit | "Only 1 Tonic can be active at a time"; 10 s windows post-07/31, Tonic Supply chains them | tonic cooldown icons in defensive/offensive rows; running tonic shows in "on me" via cd_buffs |
| **Edicts** — Inquisitor's (Agility), Knight's (armor+attributes), Witching (spell power), each plain + Greater | class kit | 30-min raid buffs, persist through death (07/31); a missing one is quiet raid throughput loss | long-term band, active-only; NO alert (persist-through-death makes staleness rare, and which Edict is "yours" is build-dependent) |
| **Slayer's Mark** (804068, 90 s CD, 8 s) | class | ramping crit window on the target | offensive row + target band |

**Boltslinger.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Bounty Hunter** stacks (2) | talent: Darkslayer/Witchbane apply, Heartseeking Bolt consumes | "Build Bounty Hunter stacks … then spend them on a charged Heartseeking Bolt" — the spec's stated loop | `PROC_GLOW` on Heartseeking Bolt + stacks in "on me" |
| **Slinging Bolts** proc (500161, 20 s) | L40 passive | "Your next Damnation is usable regardless of the target's current health" — execute outside the window, must-press | `PROC_GLOW` on Damnation |
| **Bolt and Dash** (520670, 10 s) | talent choice | next Heartseeking Bolt +25% and no cooldown | `PROC_GLOW` on Heartseeking Bolt + "on me" |
| **Bane of Witches** buff (The Bane of Witches 520130, 8 s) | talent | +10% Physical after Heartseeking Bolt — the damage window | "on me" |
| **Tormentor** DoT on target (14 s) | spec | "keep Tormentor's DoT … rolling"; Strafing Shot spreads it on crits | target band |

**Houndmaster.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Shadowhound present** | Houndmaster's Whistle 801343 (free at tree top, 08/01) | the pet IS the spec; "A Shadow Hound core … Nobody fights you 1v1" | `NO HOUND` alert (§3, §5) |
| **Shadow Rage** on the hound (stacking, 15 s) | talent: Shadowblast grants it | the hound's damage ramp | pet buffs in "on me", `unit="pet"`, stacks |
| **Decimate** (804194, 2 min CD, 20 s) | talent | empowers hounds +20% and — since 07/31 — the CASTER too (+20% dmg, +30% haste, armor ignore) | offensive row + running-CD icon in "on me" (player) |
| **Quickdraw window** | spec: "Only usable after critically striking with an ability" | the crit-gated shot; `spellUsable` desaturate carries it | main row (desaturate when unusable) |
| **Scent of Magic** (15 s) | talent | hound's next Shadow Leap −10 s CD | "on me" |

**Black Knight.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Shadow Brand** on target (12 s DoT, High Threat) | talent: direct ability damage applies | the threat maintain; Night King consumes it, Wide Swings keys off it | target band |
| **Pommel Smash** stacks on target | baseline (stacking magic-damage-taken) | Bulwark of Darkness: Dawn Blade +5%/stack | target band, stacks |
| **Dawn Knight** proc (L50 passive) | avoidance/autos, 40% | "next Dawn Blade free of cost and +25%" — React bucket: "fire the empowered ability the instant it lights up" (Sidekick blob) | `PROC_GLOW` on Dawn Blade |
| **Desecrate window** | "Only usable after avoiding an attack" | avoidance-gated counterstrike | main row (desaturate when unusable) |
| **Witching** stacks (561235, 15 s, 3 stacks) | Witch Knight talent | magic resist + melee haste ramp | "on me", stacks |
| **Clinch Fighting** (572182, cheat-death buff window) | talent | Noctis Blade +50% for 6 s after the save | "on me" |
| **Knight's Seal / Dark Oath** (680498, 45 s CD, 8 s) | talent | −5% damage taken + empowered next Desecrate | offensive row + "on me" |

**Inquisition.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Flames of Sin** (from Dawn Blade / Torchlight / Stake / Fiery Judgement / Purifier's Edge / Flourish) | L10 passive 92094 | the entire spec: autos deal +30% as Fire while it runs; every builder extends it | "on me" — the spec's most-watched buff |
| **Dawn** stacks (503658, 5 s, 10) | talent: Fire damage builds | +2%/stack to Torchlight and Dusk Blade | "on me", stacks |
| **Dusk** stacks (5 s, 10) | talent: Physical damage builds | +2%/stack to Stake and Dawn Blade | "on me", stacks |
| **Purity / Wickedness** stacks on TARGET (681413 / 681523, 6 each) | talent: main-hand / off-hand autos | +2%/stack Fire+Holy / Shadow+Physical you deal to them; Torchlight consumes | target band, stacks |
| **Heartstopper** proc (L40) | 30% on Purifier's Edge / Fiery Judgement | "allow the use of Stake within 8 seconds regardless of the target's health" — execute outside the window | `PROC_GLOW` on Stake |
| **Searing Hilt** (10 s) | talent: Purifier's Edge grants | +10% melee attack speed | "on me" |
| **Torch the Wicked!** stacks (12, 6 s) | talent | +2% attack speed per Flames of Sin hit | "on me", stacks |
| **Cycle of Despair** payoff (6 s) | talent: 20+20 Dawn/Dusk stacks consumed | +20% damage/haste/ms/crit window | "on me" |

**Missing-buff alerts** (§5): `NO HOUND` (Houndmaster). No Edict alert
(§1 class table). No stance alert this build (§6.2).

---

## 2. Talent-driven rotation changes

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| **Sixfold Shot** (Houndmaster L50) | 500567 (passive) | "Every 5th Darkslayer … transforms your Quickdraw into Sixfold Shot" | the empowered shot replaces Quickdraw periodically | `spell_swap("Quickdraw", …)` on the transformed spell's own id — Spell Known on the REPLACEMENT (no override system on 3.3.5). Castable id of the transformed shot is §6.4 — swap only wired if it resolves; base Quickdraw icon is correct otherwise (`use_ignoreSpellKnown` keeps it lit) |
| **Deadeye** (rename of Houndmaster L10 passive, 08/01) | 92093 | rename + Shadowblast crit +20% | none (passive) | SPEC_KNOWN uses the id, not the name — rename-proof. §6.5 flags the id-survives-rename assumption |
| **Heartstopper** (Inquisition L40) | 680540 | Stake usable regardless of health % for 8 s | execute outside execute range | `PROC_GLOW["Stake"]`, aura by name |
| **Slinging Bolts** (Boltslinger L40) | 500161 | Damnation usable regardless of health % | same shape | `PROC_GLOW["Damnation"]` |
| **Dawn Knight** (Black Knight L50) | 680497 | next Dawn Blade free + 25% | React bucket must-press | `PROC_GLOW["Dawn Blade"]` |
| **Purified Bola** (class talent) | 707230 | Bola Throw → Purified Bola Throw, **2 charges**, costs 10 Rage | the slow gains charges | Bola Throw drawn with its base id; charges cosmetic on the base (`CHARGES` only where baseline text says charges). §6.6 |
| **Hunt** (Inquisition) | 802006 | 2 Charges, 25 s recharge (talent tooltip) | gap-closer economy | `CHARGES["Hunt"] = 2` |
| **Rearmament** (Boltslinger tree per blob; Houndmaster page shows it too) | 805738 | post-07/31: Traps incur no cooldown for 8 s | trap window | urgency-tiered cooldown icon; window shows via cd_buffs "on me" |
| **Bringer of Darkness** (Houndmaster) | — | Repulse resets Vault, next Vault free | escape chain | no display — Vault's own swipe resets, which the icon already shows |
| **Escape Artist** (Boltslinger) | — | Daring Escape resets Vault + 10 Rage | same | same — cooldown trigger follows the reset natively |
| **Wicked Intent** (Black Knight) | — | 15% Desecrate resets Noctis Blade | extra Noctis press | cooldown trigger follows resets natively |
| **Torch the Wicked!** (Inquisition) | 560226 | Pyro Tonic also resets Torchlight | tonic→torch pairing | cooldown trigger follows; no extra display |

With/without check: every proc row above only ADDS an active-only display —
correct untalented (never fires). `spell_swap` on Quickdraw keeps the base
icon when the passive is unknown. No row of this pack assumes a talent the
spec's Sidekick build does not take.

---

## 3. Pets

- [x] Does this class summon a pet? **Houndmaster: YES — permanent
      Shadowhound** (Houndmaster's Whistle 801343, duration −1, free at the
      top of the tree since 08/01). Plus temporary Lesser Shadow Hounds:
      Unleash the Hounds (807918, 10 s CD, 20 s), Kennel Master extras,
      Houndmaster talent (call-summons on Houndmaster's Call), Daredevil's
      3-hound panic summon at 35% health. **Other three specs: none.**
- [x] Player-pressed pet commands: Houndmaster's Call (leap attack — castable
      id unresolved on db.exil.es, §6.3), Unleash the Hounds (807918),
      Decimate (804194, empowers hounds + caster), Call From The Shadows
      (578118 — pet rez), Shadow Bond (705471 — damage split toggle), Dismiss
      Hound (ignore). Real cooldown-row entries, not `ignore`.
- [x] Pet buffs to track: Shadow Rage (stacking, on hound, from Shadowblast),
      Decimate (20 s, on hounds), Scent of Magic effect (hound's Shadow Leap
      CD) — `unit="pet"` aura triggers for the hound ones.
- [x] Pet presence gates the rotation: yes — `NO HOUND` missing-alert for
      Houndmaster (same aura-on-pet + Spell Known shape as Stormbringer's
      NO PET; the absent-unit inverse mechanism is §6.1, unverified on fork).
- [x] Pet resource: none observed (no focus/energy anywhere in the kit) —
      nothing rendered.

| Pet | Summoned by | Duration | Track | Renders |
|---|---|---|---|---|
| Shadowhound | Houndmaster's Whistle 801343 | permanent | presence; Shadow Rage stacks; Decimate | `NO HOUND` alert + pet buffs in "on me" (`unit="pet"`) |
| Lesser Shadow Hounds | Unleash the Hounds 807918 / Daredevil / Houndmaster talent | 15–20 s | nothing (fire-and-forget) | — |

---

## 4. Primary damage source and the main bar

Press orders from the Sidekick per-spec rotation text (solo/dungeon
paragraphs), imported as citations; the Refine caveat ("point allocation &
optimal order aren't settled") is carried on every one.

| Spec | Primary damage | Main row, in press order | Icons | Resource |
|---|---|---|---|---|
| Boltslinger | Bounty-Hunter-charged Heartseeking Bolt + Tormentor/Witchbane | Darkslayer · Witchbane · Tormentor · Heartseeking Bolt · Damnation | 5 | rage bar + mana bar |
| Houndmaster | the hounds (Decimate windows) | Shadowblast · Quickdraw · Houndmaster's Call · Darkflock · Unleash the Hounds | 5 | rage bar + mana bar |
| Black Knight | Noctis Blade + Shadow Brand threat kit | Noctis Blade · Pommel Smash · Desecrate · Dawn Blade · March of the Black King | 5 | mana bar + rage bar |
| Inquisition | Flames-of-Sin-fuelled autos + fire strikes | Dawn Blade · Purifier's Edge · Dusk Blade · Torchlight · Stake | 5 | mana bar + rage bar |

- **Rage + mana, all four specs.** Both are `power` sources (`UnitPower` 1 and
  0); the spec's PRIMARY (Sidekick "Resource" line: Rage for Boltslinger /
  Houndmaster, Mana for Black Knight / Inquisition) renders nearest the main
  row at full height; the other renders under it, half height (`minor`
  prominence per layout-standard). Fixed-height envelope on every spec, same
  two-band depth — no per-spec anchors shift.
- No aura-stack resource band: Bounty Hunter (2), Dawn/Dusk (10) and
  Purity/Wickedness (6, on target) are BUFF-ROW stacks, not bars — none is a
  spend-meter the way Ember or Static is; the spender cues ride PROC_GLOW.
- Narrowest main row is 5 icons on every spec → `CD_PER_ROW` from
  `28w − 2 ≤ 1.2 × (5·44 + 4·2 = 228)` → **w ≤ 9.8 → 9**, to be confirmed
  against `tools/rowwidths.py` on the built pack.

Off the main row, still cited: Disappear, Grimshade Arbalest, Smoke Grenade
(Boltslinger burst bucket, blob), Vampiric Tonic (Houndmaster bucket), Gaze
of the Black Knight (Black Knight bucket), Pyro Tonic / Stoicism / Surging
Tonic (Inquisition bucket) → offensive/defensive rows.

---

## 5. Miss-handling

| Ability / state | Cost of missing it | Cue | Proof the cue fires |
|---|---|---|---|
| Tormentor dropped (Boltslinger) | DoT + Bounty feed loss | target-band bar, refresh glow ≤4 s | `dot_bars` refresh condition on aura `expirationTime` (no GCD guard needed on aura triggers) — mechanism shipped on 4 classes |
| Shadow Brand dropped (Black Knight) | threat maintain lost | target-band bar, refresh glow | same mechanism |
| Bounty Hunter stacks wasted | uncharged Heartseeking Bolt | glow on Heartseeking Bolt while stacks up | `PROC_GLOW` — check 9 asserts tiers ANDed with `onCooldown` |
| Slinging Bolts / Heartstopper proc wasted | free execute lost | proc glow on Damnation / Stake | `PROC_GLOW`, same |
| Dawn Knight proc wasted | free Dawn Blade lost | proc glow on Dawn Blade | `PROC_GLOW`, same |
| Quickdraw / Desecrate / Stake / Damnation pressed when gated | dead press | `spellUsable == 0 → desaturate` (crit-gated, avoidance-gated, execute-gated are all usability states) | check 9 *desaturate when unusable* |
| Shadowhound dead (Houndmaster) | "Nobody fights you 1v1" → nobody fights FOR you | `NO HOUND` alert | §6.1 mechanism, then in-game |
| Off-GCD buttons sweeping falsely | phantom cooldown | `use_showgcd` off, derived from `cooldown-abilities-witch-hunter.json` (Guard Strike, Slayer's Mark, Decimate, Rearmament, traps, tonic-class off-GCD rows per audit) | check 10, both directions |
| Cooldowns coming back | clipped burst | urgency tiers 20/10/5 ANDed `onCooldown == 1` | check 9, *no bare expirationTime tier* |
| Flames of Sin dropped (Inquisition) | −30% auto fire damage | "on me" buff icon with timer — it is refreshed by every builder, so the CUE is its absence from the row | buff row is active-only; verified shape on 4 classes |

---

## 6. Open questions

- [ ] **6.1 Pet-presence trigger mechanism** (`NO HOUND`) — built as aura-on-
      `unit="pet"` `showOnMissing` + Spell Known(Houndmaster's Whistle) gate,
      the Stormbringer §6.6 shape; whether the fork reports an absent unit as
      "missing" is unverified on 3.3.5. The hound's own trackable aura id is
      also unverified (Shadowhound Visual 500036 rank `Scaling` is the
      candidate). Settles: dismiss the hound once in game.
- [ ] **6.2 Stances** — Crossbow Stance (800665, Boltslinger), Musket Stance
      (800529, Houndmaster), Blade Stance (802002, Inquisition), plus Weapon
      Swapping (802001). Rendered in each spec's long-term band (active-only);
      whether a stance registers as a player aura on this fork is unverified,
      and NO missing-stance alert is built on that ground. The Crossbow-Stance
      sub-kit (Coiling Shot, Punishing Bolt, Heartstop Bolt, Collect Bounty /
      Set Bounty loop) appears in no cited rotation → kept out of all bands.
      Settles: one in-game read per stance.
- [ ] **6.3 Houndmaster's Call castable id** — db.exil.es 706332 is rank
      `Damage` (a component) and 680240 is `(Energize)`; neither is the
      button. The OFFICIAL TALENT BUILDER's node carries **802273**
      (talents-witch-hunter.json), which is the id the character is granted —
      the inventory uses it. db.exil.es has no row for 802273, so `gateable()`
      rejects an own-id gate and the trigger matches id+name. Settles: in-game
      tooltip → in-game-verified.json.
- [ ] **6.4 Sixfold Shot transformed-shot id** — 500567 is the L50 passive.
      The Quickdraw spell_swap needs the TRANSFORMED shot's castable id;
      not resolvable from the scrapes. Swap not wired this build; Quickdraw
      icon carries `use_ignoreSpellKnown` so the button stays lit while
      transformed. Settles: in-game tooltip during a Sixfold window.
- [ ] **6.5 Deadeye rename** — SPEC_KNOWN gates Houndmaster on 92093 on the
      assumption the 08/01 rename kept the spell id. A renamed-AND-reissued id
      would silently unload every Houndmaster display. Settles: one login on a
      Houndmaster.
- [ ] **6.6 Purified Bola charges** — talent replaces Bola Throw (2 charges);
      base Bola Throw has none. `CHARGES` left off the base id (a "2" on an
      uncharged button lies to the untalented). If in-game shows the talented
      button keeps id 500093, add the charge text then.
- [ ] **6.7 Vampiric Tonic id** — official tree grants 802276, db.exil.es
      digest row is 802271 (cd 0, the smell). Sweep verdict in inventory
      Notes; tooltip read settles.
- [ ] **6.8 Pavise castable id** — 504854 is rank `Visual Dummy`. Talent
      choice ability; drawn by name-match only if it earns a row; no own-id
      gate. Settles: tooltip.
- [ ] **6.9 Black Knight rage bar** — Sidekick calls the spec "Mana- and
      Rage-hybrid" but its Resource line says Mana; the rage bar is rendered
      minor. If in-game shows the spec's UnitPower is not rage at all, drop
      the minor bar.
- [ ] **6.10 `prop:`-hedged inventory rows** — UNKNOWN until the in-game
      sweep: the automated role pass's hedged rows are listed in the buildlog
      inventory step note; community feedback walks them too.
- [ ] **6.11 Boltslinger main-row Damnation vs Twilight Frenzy** — Damnation
      (execute) holds the fifth slot from the rotation text; Twilight Frenzy
      (AoE spin) sits in the offensive row. A cleave-heavy player may want
      them swapped — preference bucket, feedback decides.
- [ ] **6.12 Disappear (805772)** — UNKNOWN whether it is live: crossdb
      NO-RECORD on db.ascension.gg (only an empty legacy stub 37872 carries
      the name), while db.exil.es has the full CoA tooltip (3 s stealth, −90%
      damage taken, 3 min CD) and the Sidekick blob cites it. Kept, role
      defensive per the tooltip. Settles: one press in game.

The unverified grounds above (6.1 pet inverse, 6.2 stance auras, 6.3–6.8 id
questions, 6.9 rage read) are each marked UNKNOWN in spirit; every one is
deferred deliberately to the post-ship `verified` phase per
notes/production-run.md.

