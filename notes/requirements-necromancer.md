---
title: Necromancer — class pack requirements
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, necromancer, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
---

# Necromancer — requirements

Class **23**, token `NECROMANCER`, specs **Animation**, **Death**, **Rime**.
First build — no pack exists yet. **THE PET QUESTION IS THE CLASS** — §3 is
the load-bearing section: 54 pet/minion/summon mentions in the skills data,
the highest of any class.

Research sources, in precedence order used below: the 2026/07/31–08/07
changelog batch (dev statements, newest), db.exil.es spell pages / JSON API
(scraped 2026-08-07: `exiles-necromancer.json` 728 spells,
`spell-meta-necromancer.json`), db.ascension.gg `?spell=<id>&power` tooltips
(crossdb sweep + hand reads), the official talent builder
(`talents-necromancer.json`, ascension.gg RSC payload), and the three
Sidekick spec pages scraped 2026-08-07 to
`resources/sidekick-necromancer-<spec>.md`.

⚠️ **Sidekick staleness, known spot.** The 08-07 page scrape and the 08-02
`sidekick-data.js` blob both have **no record of Graveyard**, the brand-new
trainer spell the 2026/07/31 changelog announces. For anything the 07/31
batch touched, changelog + databases outrank Sidekick.

**Spec roles.** `resources/spec-roles.md` has no Necromancer rows (unknown,
not damage-by-default). What the sources say, citably:

- Animation — "It is not a retail healer analog. There is no targeted
  heal-an-ally cast. The throughput healing … only heals you and your own
  Undead" (sidekick-necromancer-animation). → `damage` (pet army).
- Death — "It is not mechanically close to any real allied-healer spec …
  because it has no external heal in the kit at all"; "Pure disease
  throughput" (sidekick-necromancer-death). → `damage`.
- Rime — "damage dealer" grades on every PvE/PvP row; "Closest to a Frost
  Death Knight reskinned as a pure ranged caster"
  (sidekick-necromancer-rime). → `damage`.

No tank kit appears in any page. All three treated as `damage`, pending
in-game observation (spec-roles.md is observed-in-game only, so it is NOT
edited here). **No spec gets a healing target band; Death and Rime get
DoT/debuff target bands; Animation gets none** (no maintain-DoT in its cited
rotation).

---

## −1. Changelog — 15 entries, scanned FIRST (2026-08-07, pages 6)

Newest Necromancer entry: **2026/08/07**. NOT `--accept`ed until everything
below was built or filed; accepted after triage.

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| Corpse Explosion CD correction: intended value **60 s** (not 30) | 08/07 | cooldown | §0/§4 — matches db.ascension tooltip 533236 ("1 min cooldown"); the audit's cd row agrees |
| **Graveyard — brand-new trainer spell at 60**: mark a graveyard, resurfaces corpses, plague damage | 07/31 | new spell | §0 — no scrape has it. Resolved to **805197** (33% mana, 3 min CD, "creating a corpse" — feeds Corpse Explosion). Inventory row added by hand; offense row, all specs |
| Necromancer AI less likely to attack no-danger targets | 07/31 | AI | none — server-side behaviour |
| Summoned Minions instantly re-summoned on BG resurrect | 07/31 | QoL | none |
| Unholy Runes fix: now buffs Blight; **Blight 5% chance to reset Corpse Explosion CD** | 07/31 | talent proc | §2 — a CD-reset proc on a death talent; Corpse Explosion's cd icon simply comes back early (native trigger reads the real CD), no extra display |
| **Foul Invocation now also emits a Disease Cloud** while active (you + minions) | 07/31 | rework | §1/§2 — the transform is damage now, not just a health buff; drawn as defensive CD + running-buff row entry |
| Scourge Disciple fix: Skeletal Archers properly grant haste | 07/31 | bugfix | none — passive aura |
| **Anti-Magic Shell applies to minions, not the Necromancer** | 07/31 | bugfix | §3 — the animation talent shields SUMMONS on raise; never a player-buff display |
| Frozen Barbs (Crypt Fiend) can now miss | 07/31 | bugfix | none |
| Study of Death summons **5** Zombies, up from 3 | 07/31 | numbers | none for WA (free zombies ride Unholy Frenzy's press) |
| Entomb: target immune to **Physical only** | 07/31 | rework | §0 note on the utility row; no display change |
| Corpse Explosion explodes ALL corpses; CD 10 s → 30 s (→ 60 s per 08/07) | 07/31 | rework + cooldown | §4 — a real cooldown now; offense row with urgency tiers |
| Fiend talent 30% (from 20%) | 07/31 | numbers | none |
| Sepulchral Might fix (minion SP) | 07/31 | bugfix | none |
| **Fetid, Glacial, Bone Ward persist through death** | 07/31 | rework | §1 — strengthens the wards-as-longterm read; a dropped ward is now purely a "you forgot it" state → NO WARD alert |

- [x] changelog scanned, newest entry: `2026-08-07`
- [x] every replaced/reworked/new-spell entry triaged into the sections below
- [x] `--accept` run after triage (2026-08-07)

---

## 0. Ability surface — both databases

`tools/crossdb_sweep.py necromancer` over all **241** inventory rows with an
id: **240 record, 1 no-record**. Verdicts in
`resources/crossdb-necromancer.json`; per-row consequences in the inventory
Notes.

The one no-record, resolved (not deleted): **Hoarfrost 801762** — its own
db.exil.es text keys off Glacial Dagger (a Runemaster riftblade mechanic),
the skillbook has no row, and Sidekick's only hit is the substring of the
talent "Hoarfrost Hands". Digest contamination → `ignore`, does not ship.

Known traps found during id resolution — every one carries a tooltip-read
verdict, in the inventory Notes and the builder `CROSSCHECK`:

| Name | Wrong id | Why | Castable |
|---|---|---|---|
| Graveyard | 500365 (exiles) | db.ascension's 500365 carries a Raise: Abomination tooltip — wrong row | **805197** — tooltip matches the changelog text (33% mana, instant, 3 min CD, slows + raises Undead + creates a corpse) |
| Unholy Frenzy | 578117 (exiles) | the 15 s buff aura: no cost, no CD, empty ascension tooltip | **805029** — 15% mana, 3 min CD castable (tip) |
| Lichplague | 578306 (exiles) | rank "Passive" | **802132** — 30 RP, 1.5 s cast, 30 s CD (tip); the death-tree grant |
| March of the Dead | 301007 (exiles) | "Rank 4" | **707007** — 40 RP, 10 s CD (tip); the animation-tree grant |
| Animate: Skeletal Archer | 500330 (exiles) | single-archer component ("You summon a Skeletal Archer…") | **805040** — 27% mana, 30 s CD, animates 3 (tip); tree grant |
| Mass Grave | 572408 (exiles) | its "Cast Time Reducer Aura" | **803741** — 22% mana, 30 s CD (tip); class-tree button |
| Foul Invocation | 520364 (exiles) | no cost, no CD | **804371** — 25% mana, 2 min CD (tip); class-tree button |
| Bone Tithe | 802084 (exiles) | bare stub | **802121** — 25% mana, 2 min CD, usable while stunned (tip) |
| Phylactery | 500731 (exiles) | "Phylactery Aura" | **500933** — 2 min CD + Corpse Dust reagent (tip) |
| Icequake | — | 801751 "Icequake Trigger" is the effect row | **500191** — 35 RP Deathchill consumer (tip) |

- [x] every inventory row cross-checked against both DBs (241/241)
- [x] `no-record` rows resolved and justified in the Notes cell
- [x] deprecated/unused/placeholder names filtered (NYI, Rancid Air UNUSED,
      Bone Frozen stub, "Unholy Command: Initiate…" junk — all `ignore`)

---

## 1. Mandatory buffs

**From the class kit — the WARDS.** Fetid Ward (680388, class tree, every
build), Glacial Ward (681460, rime), Bone Ward (681529, animation): 30 min
self+minion buffs, "Only 1 Ward can be active at a time", persist through
death since 07/31. A missing ward is quiet throughput/survivability loss →
**NO WARD alert** (the missing-imbue shape): fires when none of the three
ward auras is on the player, gated on knowing Fetid Ward so a levelling
character is not nagged. Also longterm-band entries (which ward is up).

**From the class kit — the STANCES.** Undead: Assault / Protect / Pacify
(500982/500985/500983, infinite duration, "Only 1 Undead Stance can be
active"). Longterm band, active-only — no alert (no stance is a legitimate
state and the cost of a wrong nag is permanent screen noise). Specs hedged —
§6.4.

**From talents.** Lich Form (rime, 500981, infinite transform: +frost damage,
RP tick; Cryoshroud and faster Champion CDs key off it) — longterm band.
Foul Invocation running (2 min CD transform, 20 s) — buff row.

**From abilities — the "press this now" procs (§5 / PROC_GLOW):**

| Proc aura | Lights up | Source text |
|---|---|---|
| Permafrost (704681) | Glacial Impact | "treats your next 2 spells cast as the target were Frozen" |
| Refreshing Chill (300940) | Ice Barrage | "reset the cooldown of Ice Barrage and make your next cast within 15 seconds free" |
| Bone King (707175) | Lichfrost | "Casting Command spells now has a 15% chance to make your next Lichfrost within 5 seconds instant cast" (animation) |
| Deadly Bond (572772) | Command: Undead | "Casting Command spells now has a 30% chance to cause their next use within 6 seconds to be free of cost" (animation L20 passive) |

Stack states worth the on-me row: Diabolical (15 stacks, consumed by Crypt
Swarm), Underking (10 stacks → free Animate CD chunk), Tundra Warriors
(3 stacks, minion crit), Frozen Bodies (10 stacks → empowered Glacial
Impact; aura 707562, exiles). All aura-id-or-name matched; visibility is
§6.6.

---

## 2. Talent-driven rotation changes

No talent in any of the three trees **replaces** an ability with a different
spell id (no Zenith/Elemental-Mastery shape found in the tree payload or the
changelog) — so no spell-swap displays and no `variants` entries. What the
trees do instead:

| Talent | ID | What changes | WA adaptation |
|---|---|---|---|
| Animate: Bone Wraith / Animate: Tomb King | 805032 / 805044 | **choose-one** switch node (animation) | both drawn in the offense row, each under its own Spell Known gate — either build reads correctly, the untaken one never appears |
| Overwhelming Force / Tears of Lordaeron | 531128 / 705752 | choose-one RP economy passives (class) | no display — passives |
| Lich Commander / Corpse Commander | 704713 / 707739 | choose-one cost passives (class) | no display |
| Depravity / Mindless Fury, Chomp / Fetid Mark, Army of the Dead / Unstoppable Frenzy, Crypt Keeper / Unrelenting, Necrotic Chains / Ner'zhul's Blessing, Frigid Death / Freeze Dry, Blood and Ice / Death and Ice, Frigid Winds / Piercing Icicles, Foul Contagion / Necrosis | — | choose-one passives | no display; procs from either side match by name and simply never fire on the other build |
| Study of Death | 704721 | Unholy Frenzy also summons 5 Greater Zombies; minion damage shortens its CD | no extra display — the Unholy Frenzy cd icon reads correctly either way (native CD trigger) |
| Unholy Runes (07/31) | — | Blight gains a 5% Corpse Explosion CD-reset proc | none — the CE icon's native cooldown trigger reflects a reset automatically |
| Bone King / Deadly Bond / Refreshing Chill / Permafrost | above | "free next X" procs | `PROC_GLOW` on the ability they empower; wrong/absent talent = glow never fires (reads as "nothing to do", never lies) |
| Champion of Kel'Thuzad (rime tree, TE) | — | "Skeletal Mages now only cost 1 Life Force" | none — Life Force display is a count, not a budget calculator |
| Withering | 301250 | Crypt Plague stacks 15 (from 10) | none — the target-band stack text shows the real count either way |
| Long March | 704717 | March of the Dead loses its CD, gains 1 s cast | none — native CD trigger shows whatever the client reports |

Every row above reads correctly **with and without** the talent because the
pack only ever draws native cooldown/aura state; nothing is keyed to a
talent's presence except the per-id Spell Known gates on the switch pair.

---

## 3. Pets — THE section

**Yes, pervasively.** Three kinds of minion, and they are NOT the same
mechanism:

| Kind | Spells | Duration | Cost |
|---|---|---|---|
| **Raised** (semi-permanent army) | Raise: Ghoul / Lesser+Greater Skeletal Warrior / Skeletal Rogue / Crypt Fiend / Gargoyle / Abomination / Decaying Colossus / Banshee / Skeletal Mage | until killed or sacrificed | mana + occupy 1–3 **Life Force** |
| **Animated** (fire-and-forget waves) | Animate: Skeletal Archer (3, 15 s) / Bone Construct / Bone Wraith / Plaguefather / Tomb King / Zombies / Frost Wyrm | 15–30 s | mana or RP, real cooldowns, **"Does not occupy Life Force"** (tip 500330) |
| **Proc'd** | Study of Death zombies, Muck Summoner/Wormfood Rotlings, Giant Bones frost giant | seconds | free |

Answers to the template's five questions:

- **Summon a pet?** Many at once. Raised minions are a Life-Force-budgeted
  ARMY (Mass Raise raises "all currently selected minions on your Life Force
  hotbar"), not the single 3.3.5 pet unit. Whether ANY raised minion
  occupies the real `pet` unit is **UNKNOWN — settles with one in-game
  `/target pet` check**; every pet-side display is therefore built on
  player-side surfaces (aura stacks, spell cooldowns), not `unit="pet"`
  triggers. (Contrast Stormbringer's single Air Elemental, which does ride
  `unit="pet"` — mechanism noted, facts not transferred.)
- **Abilities the player presses?** Yes — the whole Command family. The
  generic button is **Command: Undead** (504868, 30 RP, "Refer to individual
  Raise spells for their Command effect"); Command: Bonefreeze (rime, 20 s
  CD) and Command: Hook / Command: Blight (class tree, real CDs) are their
  own buttons. The per-minion `Command: <Minion>` rows are read as dispatch
  targets, not buttons — §6.2.
- **Buffs/debuffs to track?** Minion-side auras (Zombie Plague, Rotting
  Flesh, Frenzied Ghoul) are NOT drawn — no reliable unit to ask (see
  UNKNOWN above). Player-side pet state that IS drawn: Tundra Warriors,
  Underking, Diabolical stacks; Scourge Disciple's haste is passive.
- **Does pet absence gate the rotation?** Animation: yes, but "no minions"
  has no single aura to key on — the honest surface is the **Life Force
  bar** (below). Rime: the Skeletal Mage is THE pet ("Re-raise a fresh
  Skeletal Mage if you lose your pet") but its presence has no known
  player-visible aura → **UNKNOWN — §6.3**; no NO PET alert ships in the
  draft rather than a guessed one that lies.
- **A resource worth a bar? YES — Life Force**, the pet budget itself.

**Life Force rendering.** No native "minion count" trigger exists on this
fork (prototype list read from `Prototypes.lua` — Totem, Pet Behavior and
aura triggers only; nothing counts guardians). The native surface the client
itself maintains is the **"Life Force" player aura 524901** (rank "Visual",
duration −1, kept alive by "Life Force Visual Updater" passives 500494/
500524 and "Necro Life Force Re-adder" 805602 — "If life force is not
active, apply it"). The pack draws **its stack count** as a labelled
indicator in the resource envelope. Whether stacks report AVAILABLE or USED
Life Force (a "Used Life Force" aura 805012 also exists) is **UNKNOWN —
§6.1**; the display shows the aura's own number either way, which cannot
lie, only need relabelling after one in-game read.

**Command rows are the pet section's cooldown surface**: Command: Undead in
the main rows, Command: Bonefreeze in rime's main row, Hook/Blight in
utility, the Raise family in utility (pre-pull ritual), the Animate family
in animation's offense row.

---

## 4. Primary damage source and the main bar

Resources, all three specs: **Runic Power + mana**, plus Life Force as the
pet budget. RP costs render on db.ascension tooltips as "40 Runic Power"
etc., and the fork's `Power` prototype exposes RUNIC_POWER (= UnitPower
type 6, `Types.lua:1425`), so the RP band is a `power` bar on type 6 and
mana on type 0 — **whether this server actually reports Necromancer RP
through UnitPower(., 6) is §6.5**; a wrong guess shows an empty bar
(visible), never a wrong number. Envelope (fixed height): RP bar (14 px,
primary — the spender currency) + mana bar (10 px, minor) + Life Force
count riding the RP bar's left edge as `%2.s` text from a second trigger
(no third band — the envelope stays standard height).

| Spec | Primary damage | Main row, in press order (cited) | Icons | Resource / envelope |
|---|---|---|---|---|
| Animation | the minion army (RP-fuelled Animate waves) | Crypt Swarm · Command: Undead · Animate: Skeletal Archer · March of the Dead · Unholy Frenzy | 5 | RP bar + mana bar + Life Force count |
| Death | stacked diseases (Crypt Plague engine) | Plague of Undeath · Flesh to Worms · Lichplague · Crypt Swarm · Lichfrost · Command: Undead · Virulency | 7 | same |
| Rime | freeze-then-detonate frost casts | Lichfrost · Ice Barrage · Glacial Impact · Command: Bonefreeze · Command: Skeletal Mage | 5 | same |

Press orders are transcribed claims —
`citations-necromancer.json` `sidekick-page-necromancer-<spec>-2026-08-07`,
each carrying the quoted rotation text.

`CD_PER_ROW`: narrowest main row is 5 icons → `row_w(5) = 228 px`;
`28w − 2 ≤ 1.2 × 228` → w ≤ 9.8 → **9**. To be confirmed against the built
packs by `tools/rowwidths.py`.

Target bands: Death — Plague of Undeath, Flesh to Worms, Lichplague,
Harvest Plague (DoTs, refresh glow) + Crypt Plague and Expunge (stack
reads). Rime — Deathchill (stack read). Animation — none.

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Ward dropped (any spec) | 30-min self+minion buff quietly gone | NO WARD alert (red-bordered, desaturated, glow) | aura-missing shape is proven in game on Runemaster/Chronomancer alerts; the ward AURA-ID match is §6.7 until one in-game read |
| Virulency off CD unspent (death) | disease stack decays instead of copying | cd icon urgency tiers (timer 20 s → glow 10 s → pulse 5 s), ANDed with `onCooldown == 1` | check 9 (no bare expirationTime), check 10 (GCD flags) |
| Glacial Impact window missed (rime) | the guaranteed-crit payoff wasted | PROC_GLOW on Permafrost; desaturate on `spellUsable == 0` carries the "needs a Frozen target" state if the server reports it — §6.8 | check 9 enforces the desaturate condition exists; whether IsUsableSpell reflects "Requires Frozen Target" only the client can say |
| Free Ice Barrage unspent (rime) | a free, reset cast expires | PROC_GLOW on Refreshing Chill | glow wired to id-or-name; a wrong id reads as "nothing to do", never lies |
| Bone King instant Lichfrost (animation) | free instant nuke expires (5 s window) | PROC_GLOW on Lichfrost | same |
| Command: Undead free cast (animation) | Deadly Bond's free Command expires (6 s) | PROC_GLOW on Command: Undead | same |
| Unholy Frenzy held (all) | 3-min burst (+ Study of Death zombies / Giant Bones giant) idle | urgency tiers on its cd icon | checks 9/10 |
| RP capped | Animates/Commands wasted regen | RP bar with value text — no overcap warning in the draft (cap varies with Ner'zhul's Blessing/Runic Reservoir) | visible number; §6 candidate for a tint later |
| Minion army wiped (animation) | damage AND self-healing gone | Life Force count changes; no dedicated alert (see §3 UNKNOWN) | deferred to feedback |

Every cooldown icon: `spellUsable == 0 → desaturate`, `use_showgcd` per the
audit (17 of 39 cooldown abilities are OFF-GCD — derived, never typed),
escalation tiers ANDed with `onCooldown == 1`.

---

## 6. Open questions

The in-game checklist. Everything marked UNKNOWN above, collected:

- [ ] **6.1 Life Force aura semantics** — UNKNOWN — do 524901 "Life Force"
      stacks report AVAILABLE or USED Life Force (805012 "Used Life Force"
      also exists)? One `/run` UnitAura read or a screenshot settles it;
      relabel the indicator accordingly.
- [ ] **6.2 The Command dispatch model** — UNKNOWN — is Command: Undead
      (504868) the one button whose effect dispatches per raised minion
      ("Refer to individual Raise spells"), or do per-minion Command
      buttons appear on the Life Force hotbar? Death's Command surface
      (Expunge/Master of Death applier) rides on this; if per-minion
      buttons are real, the death/animation main-row Command slot needs
      re-pointing. One look at the in-game bars settles it.
- [ ] **6.3 Rime NO PET alert** — UNKNOWN — does the Skeletal Mage (or any
      raised minion) occupy the real `pet` unit, or expose a player-visible
      presence aura? If yes, a Stormbringer-shaped NO PET alert becomes
      buildable; the draft ships without one rather than with a guess.
- [ ] **6.4 Undead stance availability** — stances widened from the
      skillbook's animation-only filing to all specs because every spec's
      Command tooltips reference Undead: Pacify; confirm Death/Rime actually
      learn the stance buttons.
- [ ] **6.5 Runic Power as UnitPower type 6** — strong inference (tooltip
      cost lines + fork's RUNIC_POWER entry + "Energize Runic Power"
      681300); an empty RP bar in game means the guess was wrong and the
      surface is elsewhere (an aura, like Pyromancer's Heat).
- [ ] **6.6 Proc aura visibility** — Bone King (707175), Deadly Bond
      (572772), Refreshing Chill (300940), Permafrost (704681), Frozen
      Bodies (707562), Diabolical (704723), Underking (302516), Tundra
      Warriors (92122): all matched id-or-name; whether each proc's BUFF
      reuses the talent's id is unverified. A wrong id = glow never fires
      (fails safe).
- [ ] **6.7 Ward aura ids** — the NO WARD alert matches the three castable
      ids + names (680388/681460/681529); whether the 30-min self-aura
      reuses the castable's id is the standard one-trip check.
- [ ] **6.8 Glacial Impact "Requires Frozen Target"** — does IsUsableSpell
      go false without a Frozen target (desaturate carries it), or not
      (only the Permafrost glow carries it)?
- [ ] **6.9 Animate: Crypt Fiend / Animate: Zombies** — audit CDs of 2 s /
      15 s with component-ish ranks; confirm which of the Animate rows are
      real buttons on a 60 character.
- [ ] **6.10 Trainer Raise spells' spec spread** — skillbook files
      Lesser/Greater Skeletal Warrior, Skeletal Rogue, Crypt Fiend under
      animation; if all specs get them from the trainer, their utility-row
      rows should widen to `all`.
- [ ] **6.11 Hedged bulk-pass rows** — the inventory rows whose Notes carry
      HEDGE markers (Animate: Crypt Fiend, Animate: Zombies, Command:
      Skeletal Mage, Command: Undead, stances, trainer raises) are the ones
      most likely wrong; feedback and the in-game sweep are their checklist.
