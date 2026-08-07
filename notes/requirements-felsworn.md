---
title: Felsworn — class pack requirements (Phase 0)
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, felsworn, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[sidekick-felsworn-slayer]]"
  - "[[sidekick-felsworn-infernal]]"
  - "[[sidekick-felsworn-tyrant]]"
---

# Felsworn — requirements

Class **14**, token `DEMONHUNTER`, specs **Slayer** (melee damage),
**Infernal** (ranged caster damage), **Tyrant** (tank). No pack exists yet;
this is the first pass.

Research source for everything below unless stated: the three Sidekick spec
pages, scraped **2026-08-07** via Firecrawl and committed to
`resources/sidekick-felsworn-<spec>.md` (slug verified — the site serves the
class at `/felsworn/<spec>`, not `/demon-hunter/`), plus
`resources/coa-felsworn-skills.json` (191 skillbook entries),
`resources/exiles-felsworn.json` (390 spells from the db.exil.es class digest)
and `resources/spell-meta-felsworn.json` (390 API rows).

**Spec roles** — no felsworn rows existed in `resources/spec-roles.md`.
Sidekick states them outright and the kit corroborates: Slayer "Solid in
arena as a damage dealer … you cannot heal or dispel anyone" → **damage**;
Infernal "The pressure is AoE burst, not healing … No ally-targeted healing
here, and no self-heal either" → **damage**; Tyrant "Top-tier main-tank for
raid bosses … Killing people is not how you contribute" → **tank**. No spec
heals, so no `helpful=True` target band anywhere in this pack. Rows added to
`spec-roles.md` marked as Sidekick-sourced pending in-game confirmation.

## −1. Changelog — 19 entries, all 2026/07/31

`changelog_watch.py --class felsworn --pages 6`, newest entry **2026/07/31**.
Run FIRST, before any scrape was believed. The Sidekick scrape post-dates the
whole batch (its Cripple text already reads the reworked 40%), so the
mechanics source is NOT stale against it.

| Entry (2026/07/31) | Category | Where it lands |
|---|---|---|
| **Cripple now reduces moving and casting speed by 40% (from 50%), ticks down 8% (from 10%) per stack** | reworked | §1/§4 — Cripple is a *stacking, decaying* debuff; a target-band bar with stacks, not a flat slow |
| **Legionfall now additionally causes your next Annihilan Strike to cost 50% less energy** | reworked | §1 — a Slayer proc buff worth a glow on Annihilan Strike, IF the buff is a visible aura (§6) |
| **Chaotic now gives 2 energy per melee ability critical strike, down from 3** | numbers | none (passive refund) |
| Immolation Aura Ranks 1–7 damage increased | numbers | none |
| Hateforged Barrier absorb −30% | numbers | none |
| Nether Strength CDR 1s → 0.5s | numbers | none |
| Felbane can no longer target bosses | scope | §4 — utility icon keeps, note only |
| Bulwark of Azzinoth DR 10% → 5% | numbers | none |
| Pure Hatred scaling 30% → 15% | numbers | none |
| Outland Slaver, Nether Disciple, Felcaked Blades, Azzinoth's Assault base dmg, Scaling talents | numbers | none |

- [x] changelog scanned, newest entry: `2026-07-31`
- [x] every replaced/reworked entry triaged (two land in the pack: Cripple,
      Legionfall; the rest are number tweaks)
- [x] `--accept` only after this table was written

---

## 0. Ability surface — both databases

Full-inventory sweep via `tools/crossdb_sweep.py felsworn`, 2026-08-07:
**all 169 id-bearing inventory rows return `record` on db.ascension.gg**
(every row exists on db.exil.es by construction — the ids come from its class
digest). Zero `no-record` rows; no name re-asks were needed. The 22 rows with
no id in any source are unbuildable passives, each justified in its Notes
cell (`Felguard` and `Crashing Shadows` are the two whose tooltips read
castable — §6).

**Sidekick prose names that are NOT abilities**, recorded in
`resources/aliases-felsworn.json` as `canonical: null` so they stay settled:
`Glaiving` (560578 is a Fury Unleashed passive; the rotation prose means the
off-hand proc engine), `Demonsoul`, `Tyrant's Presence` (2026-08-02 data.js
talent names with no id in any source).

Known id traps found during Phase 0, resolved through spell-meta rank_text and
recorded for the builder's CROSSCHECK table:

| Ability | Wrong id | Why wrong | Castable |
|---|---|---|---|
| Demonic Will | 500497 | rank `Heal` — the heal component | see §6 / crossdb |
| Burning Hatred | 520259 | cd 0 / dur 4s, smells like a component | see §6 / crossdb |
| Fel Empowerment | 300962 | level 0, gcd 0, dur −1 — reads as the party-aura *effect*; skillbook files a same-named tyrant ability with an empty tooltip | see §6 |

db.exil.es carries a large stub surplus for this class (`Inner Demon SLS2`,
`Twin Slice Test`, `Twin Slice UNUSED`, `Felrend Energy Generator DEPRECATED`,
`Demon Form (Slaying)`, `Add 2 Felfury`, …) — machinery spells, not buttons.
The skillbook decides membership; exiles rows that look castable but are not
in the skillbook land in `## Candidates` (Glaiving 560578 and Doomscar 520239
are the two the rotation text actually names — both promoted into the table).

- [x] every inventory row cross-checked against both DBs (see phaselog)
- [x] `no-record` rows resolved in the Notes cell, none deleted
- [x] deprecated/placeholder names filtered (`utility_tables.JUNK` + Notes)

---

## 1. Mandatory buffs

**Class economy, all three specs.** Sidekick's header on every page reads
`Resource: Energy + Demonic Rage`; every tooltip and all three Resource
sections say **Felfury**. "Demonic Rage" appears nowhere else — treated as a
site label for the same thing. The economy is a **Felfury builder–spender
loop over Energy**:

- **Felfury** is aura **800058** ("Represents your Felfury charges",
  duration −1) — an `aura_stacks` resource. Cap reads as **6** (Demonic
  Embrace: "Casting Inner Demon with at least 6 Felfury"; The Demon Within:
  "you reach 6 Felfury"; Burning Hatred: "instantly generating 6 Felfury").
  Infernal's **Fel Addict** talent "increases maximum Felfury stacks" — by
  how much is UNKNOWN — 6-cell bar assumed, see §6.
- **Energy** is the `power` resource (UnitPower), rendered as a bar.

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Felfury** (800058) | class economy | every spender costs 2, Inner Demon consumes all of it, Felheart gives 1% haste per stack | 6-cell `stack_bar` in the resource envelope, all specs |
| **Inner Demon window** | castable 804216, consumes Felfury, "Lasts 5 sec per Felfury consumed" | THE class mechanic: every spec has "Inner Demon:" riders (Fel Fireball→Felstrike, Ruin tail, Sargeron Smite echo, Bulwark DR, Grommash's Folly haste/heal, Azzinoth's Assault extends it) — you bank spenders into the window | "on me" buff row, all specs + cooldown icon |
| **Bane** (one per target) | Slayer: Bane of Frailty/Power; Infernal: Bane of Chaos/Fire/Betrayal | "Can only have 1 Bane active on a target at a time"; Sidekick: "keep a Bane rolling" | target band (your debuffs on target) |
| **Cripple** (stacking, decaying) | class | post-rework it ticks down 8%/stack — the stack count is the state | target band with stacks |
| **Hateforged Barrier** | class kit, absorb + regen while it holds | both melee specs' sustain plan names it | "on me" row (active-only) + defensive CD icon |
| **Demonic Will** | Tyrant | "on cooldown for its physical DR and heal-on-damage" — running state matters | "on me" row + main row |
| **Burning Hatred** | Tyrant enrage | leech window you fight inside | "on me" row + CD icon |
| **Tyrannical Resolve** | Tyrant, 3 min | ignore-damage window ending in a Felfire burst — timing is the skill | "on me" row + CD icon |
| **Immolation Aura** | Slayer, 60s dur | opener; "recurring Fire pulse" — running state | "on me" row + CD icon |
| **Legionfall proc** | Slayer talent (changelog 07/31) | next Annihilan Strike −50% energy | PROC_GLOW on Annihilan Strike IF the aura is visible — §6 |
| **Chaotic stacks** | class talent, +3% dmg ×3 | throughput state, passive proc | "on me" row (active-only), low priority |

**Long-term band (30-min / toggle family):**

| Buff | Spec | What |
|---|---|---|
| Illidari Intuition / Greater (800212/680308) | Slayer | +Agility ally buff, 30 min |
| Man'ari Intuition / Greater (523478/523495) | Tyrant | +armor/stats ally buff, 30 min |
| Demonfire Pact (800031) | Slayer | party crit aura, toggle (dur −1), "Only 1 Pact per player" |
| Felguard | class | party melee/ranged haste aura (skillbook desc; Sidekick also credits it with the Inner-Demon melee leech rider on Slayer) |
| Agonizing Presence (807727) | Tyrant | +threat toggle |
| Betrayer's Inclinations (804758) | Slayer | demon tracking toggle — utility, not alert-worthy |

**Missing-buff alerts (§5):** `NO INTUITION` (either Intuition family member,
self-check before pull — they are ally-castable 30-min buffs) and `NO AURA`
for the toggle family (Demonfire Pact / Felguard / Agonizing Presence /
Fel Empowerment), scoped to the spec that owns each. Exact grouping decided
in the build; mutual exclusivity of the toggles is UNKNOWN — the alert fires
on none-of-the-set, the safe shape either way (the Chronomancer Wisdom rule).

---

## 2. Talent-driven rotation changes

**The transform: Inner Demon / Demon Form.** Inner Demon (804216) is the
castable metamorphosis — "Undergo a metamorphosis … enabling Inner Demon
effects. Lasts 5 sec per Felfury consumed." A separate `Demon Form` spell id
exists (**804221**, duration −1, empty tooltip) plus stubs
(`Demon Form (Felblood)` 801208, `Demon Form (Slaying)` 800707,
`Activate Demon Form, Passively` 706263). Talent text uses both words:
Demonscale/Trampling Hooves (tyrant) say "Demon Form", everything else says
"While Inner Demon is active". Reading: **one window, two names; the aura the
player carries during the window is the thing to track and its id is UNKNOWN
(804216's own aura vs 804221)** — the build tracks BOTH ids in one aura
trigger (`auraspellids` is any-of), which renders correctly under either
answer. No spell-replacement is described anywhere in the kit text: buttons
keep their ids inside the window (riders, not overrides), so **no Spell Known
variant tracking is needed** — the fork resolves no overrides and none are
required here.

| Talent | What changes | Rotation impact | WA adaptation |
|---|---|---|---|
| **The Demon Within** (Infernal) | "you reach 6 Felfury, you will consume it to enter Demon Form" — auto-cast at cap | the window starts itself; banking stops being manual | none needed: the same window aura fires; the Felfury bar empties visibly. Icon for Inner Demon stays (talented chars just see it glow less) |
| **Fel Addict** (Infernal) | raises max Felfury stacks | bar cap wrong for talented chars | 6-cell bar ships; §6 in-game check for the talented cap |
| **Legionfall** (Slayer) | next Annihilan Strike −50% energy after (trigger UNKNOWN) | press cue | PROC_GLOW if the aura id is found — §6, deferred otherwise |
| **Azzinoth's Battery** (Slayer) | Azzinoth's Assault chance not to consume Felfury | none visible | none |
| **Twin Fury** (Slayer) | +1 Felfury on Twin Slice/Annihilan crits | income only | none — bar already shows it |
| **Demonic Embrace** (class) | Inner Demon at 6 Felfury restores 50 Energy | encourages full-bar casts | none — both bars show the state |
| **Felshock** (Infernal) | Felfury-spender crits extend Inner Demon | window length varies | none — aura timer carries it |
| **Infernal Summoner** (Infernal) | direct damage can reset Infernal's CD | Infernal can come off CD early | cooldown trigger already re-reads the client's CD; no adaptation |
| **Fel Blades / Scars of Suffering** (Slayer, choose-one) | Azzinoth's Assault applies armor shred stacks OR ally AP scar | target-band candidates | not tracked in v1 — enemy-side rider debuffs, §6 note |
| **Chaos Storm** (Slayer) | "Fel Empowerment Ability" channel spin | AoE button when talented | cooldown icon, gated on its own id (spell-known gate fails silently only if id is a proc — crossdb checked) |

Pack reads correctly with AND without each: every adaptation above is either
"none needed" or an active-only display that simply never fires untalented.

---

## 3. Pets

- [x] Does this class summon a pet? **Infernal only, and only temporary:**
      `Infernal` (560284, 45s CD) drops an infernal that "summons its pet"
      fighting beside you for a short window; `Twisted Sight` (532229) summons
      a demonic eye (scouting, 45s). Slayer's `Resolve To Offense` orbits a
      Spectral Glaive (a visual rider on Infernal Resolve). No permanent pet
      anywhere in the kit.
- [x] Pet abilities the player presses or reacts to? **No** — no pet spellbook
      in `coaKits` (sidekick_skills petLines is empty for this class).
- [x] Pet buffs/debuffs needing tracking? **No** — the Infernal's fear is on
      the drop, part of the cast decision, not ongoing state.
- [x] Does pet presence gate the rotation? **No** — nothing keys off "pet
      active"; Infernal Summoner keys off the COOLDOWN, which the CD icon
      already shows.
- [x] Pet resource bar? **No.**

**Verdict: no pet section.** Infernal (the ability) is an offensive cooldown
icon on the Infernal spec, nothing more.

---

## 4. Primary damage source and the main row

Press order below is cited: `resources/citations-felsworn.json`
(`sidekick-rotation-felsworn-<spec>-2026-08-07`, transcribed from the
Rotations + Playstyle sections; single source, caveat recorded — Sidekick's
own pages carry "point allocation & optimal order aren't settled yet").

| Spec | Primary damage | Main row, in press order | Icons | Resource / segments |
|---|---|---|---|---|
| Slayer | Azzinoth's Assault (spender) into Annihilan Strike | Azzinoth's Assault, Annihilan Strike, Twin Slice, Immolation Aura, Bane of Frailty | 5 | Felfury 6-cell `stack_bar` + Energy bar |
| Infernal | Ruin / Sargeron Smite (spenders) over Fel Fireball filler | Fel Fireball, Sargeron Smite, Ruin, Felwrath, Bane of Chaos | 5 | Felfury 6-cell `stack_bar` + Energy bar |
| Tyrant | survival IS the job; Felrend/Carve carry threat | Felrend, Carve, Demonic Will, Twin Slice, Burning Hatred | 5 | Felfury 6-cell `stack_bar` + Energy bar |

- Twin Slice is the Slayer/Tyrant Felfury filler ("Generates 1 Felfury").
  "Glaiving", named by the Slayer rotation prose, is NOT a button — 560578 is
  a Fury Unleashed passive (alias null); the filler slot is Twin Slice, and
  Bane of Frailty (the cited Playstyle opener/maintain) takes the fifth slot.
- Tyrant's main row is its tanking rotation per the cited text: "spamming
  Demonic Will, Felrend and Carve … keeps you standing", Twin Slice feeds
  Felfury, Burning Hatred is the 6-Felfury enrage in the solo priority.
- `CD_PER_ROW` derives from the narrowest main row: all three are 5 icons
  (182px) → `28w − 2 ≤ 1.2 × 182` → **w = 7**. Recomputed, not copied;
  confirmed post-build with `tools/rowwidths.py`.
- Resource envelope: identical on all three specs (Felfury segments 16px +
  Energy bar 20px), so the fixed-height envelope has no per-spec variance.
- Energy bar colour: energy yellow; Felfury cells: fel green.

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Azzinoth's Assault (Slayer) | Felfury caps, armor shred drops | main-row CD swipe + desaturate when unaffordable | check 9/10 (desaturate + GCD sweep) |
| Bane (both DPS specs) | "keep a Bane rolling" — throughput loss | target-band bar + refresh glow at 4s | active-only aura bar; §6 in-game confirm it fills |
| Inner Demon window | riders wasted, spenders unbanked | "on me" icon while up + CD icon escalation tiers | tiers ANDed with `onCooldown == 1` (check 9); aura id any-of §2 |
| Felfury overcap (Tyrant explicitly: "Felfury overcaps… extended fights waste resource") | wasted income | 6-cell bar full = visibly full; spenders glow via PROC_GLOW is NOT built (no aura says "at cap" beyond the bar) | the bar itself; deferred anything louder to feedback |
| Demonic Will (Tyrant) | DR + heal window down | CD icon escalation + "on me" icon while running | checks 9/10 |
| Hateforged Barrier | absorb down when a burst lands | defensive CD icon + "on me" while holding | checks 9/10 |
| Tyrannical Resolve | dead without the emergency button | CD icon escalation at 20/10/5s | check 9 tiers |
| Fury of the Illidari / Fury Unleashed (Slayer) | burst window unspent | offensive CD icons, charges count on Fury of the Illidari (2 charges) | CHARGES + check 9 |
| Intuition / toggle aura forgotten | flat throughput loss all pull | `NO INTUITION` / `NO AURA` reminder band, fires on absence | inverse-trigger alert; §6 in-game confirm ids |
| Felbreak interrupt (Slayer kit) | a cast lands | utility CD icon, off-GCD status from audit | check 10 |

---

## 6. Open questions

Collected UNKNOWNs. None blocks the draft bar; each is the in-game / feedback
checklist for the `verified` phase.

- [ ] **Felfury aura id in game** — 800058 is the digest's "Represents your
      Felfury charges" row. UNKNOWN — one in-game `/dump UnitAura` pass would
      confirm the id and whether stacks read 0–6 on the player aura.
- [ ] **Felfury cap under Fel Addict** — "increases maximum Felfury stacks"
      by an unstated amount. UNKNOWN — read the talented tooltip in game. The
      shipped bar is 6 cells; a talented cap above 6 renders as a full bar
      early (safe failure).
- [ ] **Inner Demon window aura id** — 804216 (the castable) vs 804221
      (`Demon Form`). Both tracked any-of in one trigger. UNKNOWN — in-game
      aura read settles which fires.
- [ ] **Legionfall proc aura** — changelog says "next Annihilan Strike costs
      50% less"; no aura id found in the digest under that name. UNKNOWN —
      deferred; no glow shipped for it (a glow that never fires is worse than
      no glow).
- [ ] **Fel Empowerment** — 300962 reads as a party-aura effect (level 0,
      gcd 0); the skillbook's tyrant entry has an empty tooltip; Chaos Storm
      is tagged "Fel Empowerment Ability". UNKNOWN what the castable is —
      kept OUT of the alert set until settled.
- [ ] **Toggle-aura mutual exclusivity** (Felguard / Demonfire Pact /
      Agonizing Presence / Fel Empowerment) — "Does not stack with similar
      effects" suggests a family; UNKNOWN whether one-at-a-time per player.
      Alert fires on none-of-set, correct under both readings.
- [ ] **Fel Blades / Scars of Suffering enemy debuffs** (Slayer choose-one
      talents) — target-band candidates not shipped in v1; add on feedback.
- [ ] Rows whose automated role reasoning hedges are listed in the inventory
      Notes and mirrored here after the role pass (see abilities-felsworn.md;
      hedged rows called out in the buildlog step note).
- [ ] **Single rotation source** — every priority above is one author
      (Sidekick, 2026-08-07, which itself carries the "order isn't settled"
      caveat). Community feedback is the second source; drafts ship on one.
