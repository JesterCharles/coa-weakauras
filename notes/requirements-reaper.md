---
title: Reaper pack requirements
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, reaper, requirements]
sources:
  - "[[class-requirements-template]]"
  - "resources/sidekick-reaper-domination.md (scraped 2026-08-07)"
  - "resources/sidekick-reaper-harvest.md (scraped 2026-08-07)"
  - "resources/sidekick-reaper-soul.md (scraped 2026-08-07)"
  - "resources/cooldown-abilities-reaper.json (db.exil.es audit, 2026-08-07)"
  - "db.ascension.gg ?spell=<id>&power tooltips, 2026-08-07"
---

# Reaper — class pack requirements

Class 30, token `REAPER`, specs **domination** (tank), **harvest** (damage),
**soul** (damage). Roles from citable Sidekick kit statements (see
`resources/spec-roles.md` provenance note); no spec heals, so no
`helpful=True` target band exists anywhere in this pack.

---

## −1. Changelog — run FIRST

`python3 tools/changelog_watch.py --class reaper --pages 6` → 33 entries, all
dated **2026/07/31**, scanned 2026-08-07.

- [x] changelog scanned, newest entry: `2026-07-31`
- [x] every entry triaged (below). **No** `replaced with` / `now reads` /
      `now baseline` / `new spell` / `reworked` entries — the whole batch is
      numeric tuning plus five mechanics tweaks.
- [x] `--accept` run only after this table was written.

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| Crow's Harvest R1–R7 +damage | 2026/07/31 | numeric | no WA surface |
| Reap R1–R8 +damage | 2026/07/31 | numeric | no WA surface |
| Slaughter R1–R7 +damage | 2026/07/31 | numeric | no WA surface |
| Soulstrider 20%→25% | 2026/07/31 | numeric | no WA surface |
| Harvester's Scythe 15%→20% | 2026/07/31 | numeric | no WA surface |
| Spectre Strength +armor pen | 2026/07/31 | numeric | no WA surface |
| Hemorrhage 10%→20% | 2026/07/31 | numeric | no WA surface |
| Shudder Scythe strike 30%→40% | 2026/07/31 | numeric | no WA surface |
| **Limbo 5s→6s** | 2026/07/31 | duration | inventory note; Sidekick snapshot still says 5s → §0 staleness note |
| **Harvesting Grounds 10s→15s** | 2026/07/31 | duration | inventory note |
| Scythe Rush now roots 1s | 2026/07/31 | mechanics | inventory note; no new WA surface |
| Spectre Stride roots 2s | 2026/07/31 | mechanics | inventory note |
| Empyrean Fortitude 2→5 RP | 2026/07/31 | resource numeric | no WA surface |
| Soul Infusion cost refund on miss | 2026/07/31 | resource mechanics | no WA surface (server-side refund) |

**Staleness:** the Sidekick pages were scraped 2026-08-07 but their content
predates 2026/07/31 (they still carry Limbo at 5 sec). Rotation *structure*
claims are unaffected by this batch — every entry is tuning — so the pages
remain the mechanics source, with numbers deferred to db tooltips.

---

## 0. Ability surface — both databases

`tools/crossdb_sweep.py reaper`: **211 of 211** inventory rows with an id
asked of db.ascension.gg (db.exil.es side is the id source itself).
Result: 209 record, 2 no-record, both justified in the inventory Notes:

- **Shrieking Scythe 502700** — RENAMED; only db.exil.es knows the name.
  Role `ignore`, canonical name **Shrieker** (801332, both DBs + skillbook).
  `resources/aliases-reaper.json`.
- **Shudder Scythe 801321** — the ability exists on db.ascension as
  components (801322 `Damage`) and talent 805708; 801321 is the only
  castable-shaped id anywhere. Ships with §6 flag.

Name re-asks resolved five wrong/missing ids (Cull → 800930,
Gravesite → 804722, Masochistic Rage → 803030) and added four rows the
skillbook lacks (Blood Siphon 805340, Crimson Thirst 807415, Purgatory
504046, Possess 806600). **Sever** has no id in any source — the cited
harvest interrupt is unbuildable (aliases, §6).

- [x] every inventory row cross-checked against both DBs
- [x] `no-record` rows justified in the Notes cell
- [x] junk filtered (Genocide SLS, Painbringer's Barbarian tooltip, Deathmyst)

---

## 1. Mandatory buffs

The class has **no imbue/stance kit** in the Runemaster sense — nothing that
a character must apply before the pull or silently lose throughput, so the
pack ships **no missing-buff alert band** (the §5 rationale). What must be
visible:

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| Soul Infusion (803031) | resource cascade (3 Reaped Souls) | gates Reliquary of the Lost, Soulslam, Blood Siphon, Spectral Scythe, Tormented Souls, Soulspear-instant | PROC_GLOW on those icons + buff row |
| Reaped Souls (500363, 0–3 stacks) | Soul Fragments at 5 stacks | the spend/bank decision every spec plays around | 3-cell stack bar in the resource envelope |
| Soul Fragment (805077, 0–5 stacks) | builders | how close the next Reaped Soul is | fused count inside the filling Reaped Soul cell (the Pyromancer heat pattern) |
| Eater of Souls window | dom passive at 3 Reaped Souls | the mitigation+regen window the bank decision buys | dom buff row |
| Tormented Souls stacks | pressed spender | DR charges being eaten by hits | buff row (all specs) |
| Fatesealer stacks | soul passive | stacking DR state | soul buff row |
| Crimson Thirst / Extinction / Souls for the Slaughter / Painmail | harvest procs | "the stack list is the spec" (Sidekick difficulty text) | harvest buff row |
| Purgatory stacks | soul talent | +20%×2 Soulrend/Reliquary window | soul buff row |
| Ghost | Sinister Litany talent rider | next-hit damage buff | buff row (all specs) |
| Ghostly Weapon | soul imbue, 15 s, 2 charges | Lamenting heals off it; 'keep it imbued' | soul buff row + offensive cd icon |
| Bolstered Form / Dark Deal / Soul Knight windows | dom actives/procs | the mitigation layers the Difficulty text says you must overlap | dom buff row |

---

## 2. Talent-driven rotation changes

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| Decimation | 704193 (grants 500523) | every 6th Reap becomes **Decimate** | dom main row gains a slot-sharing hit | own display gated `["Spell Known"] 500523` (numeric), sharing the Reap slot — the loaded-and-showing mechanism; without the talent the display never loads |
| Redshade | 524735 (grants 505170) | Reap becomes **Thresh** "for a stretch" | harvest main row slot-share | own display gated `["Spell Known"] 505170` |
| Sinister Litany | 805185 | new pressed button: instant 3 Reaped Souls | resource burst | offensive row icon (already in inventory, role offensive) |
| Veilwalk | 803990 | 2-charge sprint | mobility | utility icon, CHARGES=2 |
| Limbo / Jailer's Bargain / Tormented Souls | 800845 / 805718 / 500481 | AE-tree actives every spec can take | defensives | utility-row icons on every spec (class-wide rows) |
| Wraith Claw | 807234 | upgraded Ghost Claw, 2 charges | harvest slow | own icon, CHARGES=2; Ghost Claw icon stays (both known states possible — UNKNOWN §6 whether learning Wraith Claw unlearns Ghost Claw) |
| Blood Siphon (via Improved Blood Siphon) | 805340 | talent-granted Soul Infusion spender | harvest burst | offensive icon; PROC_GLOW on Soul Infusion |
| Crimson Thirst / Purgatory | 807415 / 504046 | stacking buffs | readable state | buff-row entries (active-only, harmless untalented) |
| Endbringer | 800922 | 3 min Dirge empowerment | soul burst | offensive icon + buff-row entry |

Every adaptation reads correctly both with and without the talent: slot-share
displays are gated on the *replacement* spell being known, buff entries are
active-only, and cooldown icons for unlearned talents never load past the
spec gate + `IsSpellKnown`-shaped triggers. Layout assumes the untalented
row width (5 main icons; the transforms share slots rather than adding).

---

## 3. Pets

- [x] Does this class summon a pet? **Temporary combat summons only.**
      Spectral Scythe (20 s per Reaped Soul spent), Spectral Warden (20 s,
      3 min cd) on domination; Wailing Soul (controllable scout that possesses
      one enemy) on soul. Nothing permanent, nothing with a spellbook.
- [x] Pet abilities the player presses? **No** — the summons act on their
      own; Wailing Soul is a possess mini-game with no WA surface.
- [x] Pet buffs/debuffs to track? Spectral Warden's group absorb is worth a
      buff-row entry; nothing else.
- [x] Does pet presence gate the rotation? **No** — summons are cooldown
      spends, and their absence is the cooldown swipe.
- [x] Pet resource bar? **No.**

**Verdict: no pet section.** The summons are cooldown icons in the offense /
defense rows, exactly like any other cooldown.

| Pet | Summoned by | Duration | Track | Where |
|---|---|---|---|---|
| Spectral Scythe(s) | Spectral Scythe (dom, 45 s) | 20 s | the cd icon | offense row |
| Spectral Warden | Spectral Warden (dom, 3 min) | 20 s | cd icon + group absorb buff | defense row + buff row |
| Wailing Soul | Wailing Soul (soul) | short | cd icon | utility row |

---

## 4. Primary damage source and the main bar

All three specs spend **Runic Power** (bar under the main row; power type 6 —
§6 UNKNOWN until an import confirms the client exposes it for `REAPER`) and
bank **Soul Fragments → Reaped Souls → Soul Infusion**:

- Soul Fragment 805077 — db.ascension tooltip: "At **5** stacks, generate a
  Reaped Soul." (Sidekick's soul page says 3 — the db tooltip outranks it.)
- Reaped Soul 500363 — "At **3** stacks you are granted Soul Infusion."
- Soul Infusion 803031 — the gate for the big spenders.

Resource envelope, every spec: **Reaped Souls as a 3-cell `aura_stacks` bar
with the Soul Fragment count fused into the filling cell** (the Pyromancer
heat-in-ember pattern, `stack_bar(..., feeder=...)`), and the **Runic Power
bar** under it. Both width-locked to the 5-icon main row.

| Spec | Primary damage | Main row, in press order (cited) | Icons | Resource |
|---|---|---|---|---|
| Domination | attrition cleave (Reap/Dreadwake/Requiem) | Reap → Soul Strike → Dreadwake → Requiem → Deathwind (+ Decimate slot-share) | 5 | RP bar + Reaped Souls cells |
| Harvest | leech melee (Harvester engine) | Crow's Harvest → Doomrend → Reap → Murder → Slaughter (+ Thresh slot-share) | 5 | RP bar + Reaped Souls cells |
| Soul | fragment-cascade melee | Deathchaser → Wraithblade → Dirge → Reap → Reliquary of the Lost | 5 | RP bar + Reaped Souls cells |

Press orders are quoted from the numbered Sidekick rotation text of each
spec page (`resources/sidekick-reaper-<spec>.md`, Rotations section).
`CD_PER_ROW` from the narrowest main row (5 icons ⇒ 7, confirmed by
`tools/rowwidths.py` after the build).

Target band (`helpful=False`, own-only) per spec:
- **Domination**: Withering Touch (60 s shred), Requiem's slow is untracked
  (short, AoE).
- **Harvest**: Doomrend (anti-heal shield), Darkrend Scythe (bleed), Ruin,
  Blood Frenzy (burst DoT).
- **Soul**: Soulrend, Soulrot, Deathchaser, Weakened Soul, Withering Touch.

---

## 5. Miss-handling

No missing-buff alert band ships: the class has no pre-pull self-buff whose
absence is silent throughput loss (no imbues, no stances; §1). Death's
Presence is the one candidate and its aura visibility is unproven — an alert
keyed on a hidden passive would be **permanently on screen**, the exact
Runemaster reminder-band failure, so it stays out until the in-game pass
(§6).

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Soul Infusion spenders (Reliquary, Soulslam, Blood Siphon, Spectral Scythe, Tormented Souls) | banked resource wasted, burst window skipped | PROC_GLOW on Soul Infusion aura (803031 + name) | tests/run.py checks the glow conditions exist; aura id in-game verify is §6 |
| Slaughter under 35% | execute + Reaped Soul refund lost | `spellUsable` desaturate lifts when target qualifies (usability includes range/health reqs on this fork — §6 to confirm for health-gated casts) | check 9 half 1; in-game §6 |
| Off-cooldown damage cds (Endbringer, Harvest Time, Spectral Scythe…) | throughput | urgency tiers: timer 20 s, glow 10 s, urgent 5 s, ANDed `onCooldown == 1` | check 9, *no bare expirationTime tier* |
| Off-GCD abilities (20 of 35 audited) | phantom sweep reads as unavailable | `use_showgcd` off | check 10, both directions |
| Unaffordable RP spends | icon reads "press me" while unpayable | `spellUsable == 0 → desaturate` | check 9 |
| DoT/debuff drops (Doomrend, Soulrend, Soulrot, Withering Touch…) | sustain + damage riders lost | target band bars with `%p`, refresh glow | dot_bars refresh_at; in-game §6 |
| GCD clipping | wasted globals | GCD sweep on every on-GCD icon | check 10 |

---

## 6. Open questions — the in-game checklist

- [ ] **Runic Power power-type**: the bar assumes `UnitPower(player, 6)`
      (Wrath runic power slot). Confirm the CoA client exposes it for REAPER;
      if the bar reads 0/0 permanently, capture the right power type.
- [ ] **Reaped Soul / Soul Fragment / Soul Infusion aura ids**: 500363 /
      805077 / 803031 carry the right tooltips on db.ascension, but decoy ids
      exist (`+1 Reaped Souls` 504390, `Soul Fragment` 573051/706787,
      `Soul Infusion Activate` 803032). Same trap as Pyromancer's Ember
      Trigger — only the game separates the stack-carrying aura from its
      machinery. Watch the cells fill.
- [ ] **Fragment cell count**: db tooltip says 5 fragments per Reaped Soul;
      the soul Sidekick page (Soul Collector text) says 3. Built as 5 per the
      source precedence. Confirm, and whether fragments overcap-waste at full
      Reaped Souls (decides feeder warn colors).
- [ ] **Sever (harvest interrupt)**: no id in any source. Find the real id
      from the in-game spellbook; until then harvest ships without an
      interrupt icon.
- [ ] **Shudder Scythe 801321**: db.ascension no-record on the id (components
      only). Confirm the icon's cooldown trigger actually tracks in game.
- [ ] **Shrieker vs Shrieking Scythe**: the soul silence icon is NOT in the
      draft. The only current-name id (Shrieker 801332) carries rank tag
      'Heal', a component tag check 22 refuses in a pressable row, and the
      old-name id (Shrieking Scythe 502700) exists only on db.exil.es.
      Capture the real button id in game and add it to the offense row.
- [ ] **Reliquary of the Lost id**: 500629's rank text reads like a counter
      and 500630 is the bolt damage. Built on 500629 (the exil.es castable).
      If the icon never sweeps, capture the real button id.
- [ ] **Decimate / Thresh slot-share**: confirm the server grants/removes
      500523 / 505170 dynamically (the `["Spell Known"]` gate flips) rather
      than proc-flagging the base button.
- [ ] **Death's Presence**: if its aura is visible on the player, add a soul
      `NO DEATH'S PRESENCE` pre-pull alert; hidden-passive risk keeps it out
      of the draft.
- [ ] **Wraith Claw vs Ghost Claw**: does learning Wraith Claw unlearn Ghost
      Claw? Both icons ship; if one is dead on a talented character, drop it.
- [ ] **Crimson Harvest / Crimson Scythe**: ranked castable per db.ascension
      but uncited by any rotation; shipped in the harvest offense row.
      Confirm it is a real button (and whether 'Crimson Scythe' is its twin).
- [ ] **Slaughter usability gating**: does `IsUsableSpell` go false above 35%
      target health on this fork (desaturate would then carry the execute
      cue), or only on resource?
- [ ] **Murder on soul / Soul Strike on harvest / Reap+Spectre Stride specs
      widened to all**: membership calls made against skillbook narrowness
      from cited rotation prose (inventory notes). A dead icon on the wrong
      spec is invisible (spellknown gate) — confirm which specs actually
      learn them.
- [ ] **Blood Frenzy / Darkrend Scythe / Ruin target-aura names**: the target
      band matches these debuffs by name; confirm the on-target aura names
      match the ability names.
- [ ] **advClass numbering**: db.ascension lists reaper talents under
      advClass=32 while `ascension-coa-class-ids.md` files Reaper as 30 —
      no build surface reads this id, recorded for the reference table's
      next audit.
