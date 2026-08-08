---
title: Venomancer pack requirements
date: 2026-08-08
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, venomancer, requirements]
sources:
  - "[[class-requirements-template]]"
  - "resources/sidekick-venomancer-fortitude.md (scraped 2026-08-07)"
  - "resources/sidekick-venomancer-rot.md (scraped 2026-08-07)"
  - "resources/sidekick-venomancer-stalking.md (scraped 2026-08-07)"
  - "resources/sidekick-venomancer-vizier.md (scraped 2026-08-07)"
  - "resources/coa-venomancer-skills.json (sidekick-data.js snapshot 2026-08-02)"
  - "resources/exiles-venomancer.json (db.exil.es llms.txt digest, 2026-08-07)"
---

# Venomancer — class pack requirements

Class 29, load token `PROPHET`. Four specs: **Fortitude** (tank, Rage,
Brewmaster analog), **Rot** (ranged DoT caster, mana, Affliction analog),
**Stalking** (melee builder/finisher, Energy + Brood Marks, Feral analog),
**Vizier** (pure HoT healer, mana, Resto Druid/Preservation analog). Roles are
Sidekick-cited, pending in-game — see §4 and `resources/spec-roles.md`.

The db tree/site slug is `venomancer` everywhere checked (Sidekick page URLs,
db.exil.es `/class/venomancer` digest); the load token alone is `PROPHET`.

---

## −1. Changelog — run FIRST

- [x] changelog scanned 2026-08-07 (`changelog_watch.py --class venomancer
      --pages 6`), newest venomancer entry: `2026-07-31`
- [x] every mechanical entry triaged below
- [x] `--accept` only after the entries are acted on

28 new entries, all dated 2026/07/31. Triage:

| Entry | Category | Where it lands |
|---|---|---|
| Serpent's Fang R1–R8 damage/healing up | number tweak | ignore |
| Spore / Wilt SP coefficients up; rot mana costs down (Mycosis, Fungal Assailant, Wilt, Spore, Venom Bolt) | number tweaks | ignore |
| Suffocating Coils proc chance 5% → 8% | number tweak | ignore |
| **From Life Comes Death is now a passive instead of a cooldown** | reworked | §2 — no cooldown icon may exist for it; it is not in the inventory as a button (correct), mushroom-on-kill is a passive |
| **Brood Marks no longer have a duration** | duration change | §4 — the Brood Mark target-band icon must not rely on a timer; `%p` renders empty on an infinite aura, stacks carry the read |
| **Withering Venom now generates 1 Brood Mark** | rotation interaction | §4 — corroborates Withering Venom in the stalking main row |
| **Cycle of Decay now allows Spore and Wilt to critically strike** | talent behaviour | §1 — settles what the Cycle of Decay proc window means (crit window for the DoTs); tracked on-me |
| Mycelial Ring +50% mushroom damage with it learned | number tweak | ignore |
| Prophetic Speaker: Decay max targets +5 | number tweak | ignore |
| **You can now shapeshift while silenced** / all forms grant polymorph immunity | form behaviour | §1 — forms are core state; corroborates the long-term form row |
| **Weaver Form ICD removed; now generates 5% base mana (was 5% missing)** | reworked resource | §1 — Weaver Form is rot's standing form; long-term row |
| **Spider Lord scarab summon 5% → 15%, now also procs from Carapace Crash** | proc tweak | §3 — scarabs stay proc-summoned creatures, no pet section |
| Undead can now be Venomancers | flavor | ignore |

Snapshot staleness: `sidekick-data.js` mtime 2026-08-02 **post-dates** the
newest venomancer changelog entry (2026-07-31). The four spec pages were
scraped live on 2026-08-07. Nothing in the corpus is older than the changelog.

---

## 0. Ability surface — both databases

Inventory seeded from `coa-venomancer-skills.json` (262 skillbook rows)
enriched by `cooldown-abilities-venomancer.json` (44 rows, `unresolved` empty,
21 off-GCD) + `exiles-venomancer.json` (506 spells, 230 multi-rank) +
`spell-meta-venomancer.json`. 270 rows after review (3 aura-only rows added:
Widow's Kiss, Brood Mark, Shadra's Vigil).

- [x] every inventory row with an id asked of BOTH databases
      (`crossdb_sweep.py venomancer`: 258/258 — buildlog `crossdb` step)
- [x] `no-record` rows resolved in Notes cells, none deleted on the verdict:
      - **Fang of Shadra 800888** — exiles tooltip names Leg Strike / Lethal
        Toxin / Stalker Form, mechanics absent from the current kit; ascension's
        806941 is an empty "Energise" dummy; 1 blob hit → stale revision, `ignore`
      - **Miasma 804549** — other-id (ascension 570208, same poison-cloud
        tooltip); Improved Miasma talent is in the stalking kit → real, kept
      - **Ritual Healing 800900** — the current kit's Ritual Healing is the
        **L50 passive** (skillbook + vizier prose); exiles 800900 is an old
        channel, ascension 800908 an empty row → `ignore`
      - **Widow's Kiss 800885** — ascension carries the name under other ids
        (804118/807244/807483/807600); the display matches the aura BY NAME → §6
      - Facemelter 800871 / Rotfang 804977 `?power` no-response both times;
        ascension's own name search returns the **same ids** → record
- [x] deprecated/unused/placeholder rows filtered with evidence: "Champion of
      the Spider" (tooltip literally "Deprecatged"), "Spider Senses" ("you see
      this, upate game, make bugreport"), Unbreakable (rank=UNUSED), plus four
      cross-class leaks (Spellslinger→Runemaster, Relentless→Barbarian,
      Hate→axe class, Fel Cloak→Felsworn) — all `ignore` with the reason in
      the Notes cell

---

## 1. Mandatory buffs

**From the class kit:**

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Venoms** (Adrenal / Hallucinogenic / Weakening class-wide; Blight stalking; Debilitating + Nullifying rot; Rejuvenating vizier) | class | "You can have a maximum of 2 unique Venoms active at a time"; every spec's cited rotation activates them (stalking "set Blight Venom as your active venom"; rot "Keep up to 2 Venoms active"; vizier "Rejuvenating Venom active"; fortitude's Vile Sting "fires your active Venoms", Venomics scales them). 2-hour self-buffs (805775/805776/805731/805777/630868 all dur 7200000) | long-term band per spec + class-wide **NO VENOM** alert (show when zero venom auras up — never per-venom, the 2-of-7 choice is deliberate) |
| **Forms** (Beetle fortitude / Weaver rot / Spider stalking / Vizier vizier) | class | shapeshift kit — changelog: shapeshift while silenced, polymorph immunity while in form. Stalking's finishers read "Requires Spider Form"; vizier pre-pull is "Vizier Form up"; Weaver Form is rot's mana-regen form; Beetle Form is fortitude's tank stance *swapped situationally* | long-term band per spec; **NO SPIDER FORM** (stalking) and **NO VIZIER FORM** (vizier) alerts. Rot and fortitude get NO alert — their forms are actively shifted out of (shift-break, spike-tank swaps) and a nag would be permanently wrong (§6) |
| **Pheromones / Envenomed Weapons** (Beetle/Spider/Toxic Pheromones + Greater variants) | class | 30-min ally buffs, "Does not stack with other similar effects" — the Instinct shape | long-term band of the owning spec; no alert (they sit on the ALLY, absence not cheaply readable) |

**From talents / spec passives:**

| Buff | Spec | Why | Where |
|---|---|---|---|
| **Exposed Flesh** (stacking debuff ON YOU, L10 spec passive 92144) | fortitude | the whole loop: "You deliberately let yourself get hit to fuel offense and cooldowns, then shed the stacks on Regrow Exoskeleton, Barbed Stinger or Expulsion" | on-me row with stack count (`helpful=False`); cap unknown → not a segmented bar (§6) |
| **Brood Mark** (stack debuff ON TARGET, 804972, no duration since 07/31) | stalking | the spec meter: "Venom Fang applies Marks and your finishers consume them"; Blistering Fangs refunds at 5+ | target band with stacks (per-target state, so the target band is the honest surface — see §4) |
| **Fungal Growth** (stacks ON TARGET, 804971, 30s) | rot | "Fungal Growth stacks periodic-damage amplification on the target"; Mycosis +20%/stack | target band with stacks |
| **Widow's Kiss** (self haste, 4s) | stalking | "Every 3rd Venom Fang becomes Widow's Kiss… granting you increased haste"; "Widow's Kiss's haste kept rolling" | on-me row, by name |
| **Acidfang** (stacks, 15s, 806602) | stalking | "increasing the Quickness of your next Facemelter" | on-me row with stacks |
| **Skulk** (stealth state) | stalking | "Skulk (stealth) makes Venom Fang free and hard-hitting for openers" | on-me row + PROC_GLOW → Venom Fang |
| **Rot Lich** (proc, L10 spec passive 92142) | rot | "Rot Lich can reset and grant an instant Serpent's Fang" | on-me row + PROC_GLOW → Serpent's Fang (proc aura name assumed = "Rot Lich" → §6) |
| **Cycle of Decay** (proc, L50 passive) | rot | proc window named in the rotation text; changelog: lets Spore and Wilt crit | on-me row, by name |
| **A Pit of Snakes** (stacks, 8s) | rot | "Serpent's Fang chains… stacking damage" | on-me row with stacks |
| **Tome of Ahn'kahet** (proc: next spell free) | class | "The next spell has its costs reduced by -100%" — no single button to glow | on-me row |
| **Surprise Strategy** (proc: next Shadra's Prayer +20%, instant) | class (reads on vizier) | a "press this now" for the healer's main button | on-me row + PROC_GLOW → Shadra's Prayer (aura name → §6) |
| **Alacrity** (dodge stacks off Chitin Rush), **Protogenesis** (10-stack heal ramp), **Carapace Regeneration** (3-stack active mitigation) | fortitude | tank ramps and running mitigation | on-me row with stacks |
| **Death Spray** (proc: next Venom Fang/Widow's Kiss free +20%) | stalking | energy relief the difficulty text names | PROC_GLOW → Venom Fang (aura name → §6) |

**From abilities:** running cooldown windows (Noxious Empowerment, Contagion,
Venocannon, Catalyst, Toxic Rage, Molt, Extraction, Serpent Lord's Amulet,
Mycelial Replenishment, Serpent Lord's Ring, Locust Swarm) render in the on-me
row via the offense-row derivation; Harden and Lifeblood (defensive, so not
derived) are explicit SHORT_ENTRIES.

---

## 2. Talent-driven rotation changes

This fork resolves NO spell overrides. Findings from the four trees:

| Talent | What changes | Rotation impact | WA adaptation |
|---|---|---|---|
| **Widow's Kiss** (stalking 1/1) | "Every 3rd Venom Fang **becomes** Widow's Kiss" — a cyclic, automatic transform | extra damage + self-haste every 3rd builder | **NOT a Spell Known swap** — the base button stays learned and the cycle is server-side. Track the resulting haste aura on-me by name. No per-press cue is possible without a cast counter; deferred (§6) |
| **From Life Comes Death** (rot) | changelog 07/31: now a **passive**, was a cooldown | mushrooms on kill happen by themselves | nothing rendered — it has no button row, correct by construction |
| **Spindlebind (Tunneler)** (stalking) | "Your Spindlebind now has 2 charges, a 25 sec cooldown" | charge economy | CHARGES (count harmless on the untalented 16s version — the Fabric of Time precedent) |
| **Serpent Lord** (stalking) | "Augments Spider Form… giving some of your Spider Form abilities a 1 sec cast time" and extra range | soft-ranged option | no button change; row stays a utility entry — toggle-vs-passive unresolved (§6) |
| **Spider Lord** (fortitude) | "Augments Beetle Form into a Spider Lord" + scarab procs (07/31 buffed) | passive augment | no WA change — scarabs are proc summons |
| **Book of Shadra** (rot) | "Doubles the duration, cooldown, and healing of Green Salve; it now seeks another ally" | Green Salve behaviour | no WA change — the cooldown swipe reads the real cooldown either way |
| **Sporelord / Blightfang / Fungal Growth verticals** (rot) | mushrooms ride Fungal Assailant / Serpent's Fang / Decay | burst layering | no WA change — mushrooms are ground objects, no player aura cited |
| **Vulnerability** (stalking L40) | auto-attacks apply Blight Venom while it is active | passive application | no WA change — Blight Venom is already a long-term row |
| **Intoxicating Venoms** (rot L40) | Mycosis enhanced by the active Venom | reinforces the NO VENOM alert | covered by the venom long-term band |
| Charge abilities | **Alkahest 2** ("2 Charges, 12 sec recharge"), **Carapace Regeneration 3**, **Skitter 3** ("dashes on three charges"), **Spindlebind 2** (talented) | spam-on-recharge economy | CHARGES |

Pack reads correctly untalented: proc-glow displays are active-only (no proc =
no glow), charge counts fall back to a plain cooldown, and talent-granted
windows simply never light. No permanent replaces/transforms exist in any
tree, so no `spell_swap()` is needed.

---

## 3. Pets

- [x] Does this class summon a pet? **No controllable pet.** Four summon
      mentions in the whole kit, all temporary/proc creatures: **Fungal
      Assailant** (rot, cooldown summon "to attack an enemy… Lasts" — a
      cooldown button, the witch-doctor totem shape), **Scarabs** (fortitude
      passive: "Gives damage dealt a % chance to summon Scarabs"), **Scarab**
      560989 (the 12-sec summoned creature itself), **Spider Lord** (fortitude
      passive augment whose scarab proc the 07/31 changelog buffed). No
      Call/Revive/Mend/dismiss verbs anywhere; no pet bar implied.
- [x] Player-pressed pet abilities? **None.**
- [x] Pet buffs/debuffs to track? **None** (no `unit="pet"` rows).
- [x] Does pet absence gate the rotation? **No** — no NO-PET alert.
- [x] Pet resource bar? **No.**

The tracking surface for every summon is the player-side button: Fungal
Assailant renders as an offensive cooldown icon; Scarabs/Spider Lord are
passives (`ignore`).

---

## 4. Primary damage source and the main row

Spec roles (Sidekick-cited, pending in-game — recorded with provenance in
`resources/spec-roles.md`):

- **fortitude — tank** ("Closest to Brewmaster Monk… built to be extremely
  hard to burst down"; taunt Vile Sting; "swap to Beetle Form" tank stance)
- **rot — damage** ("Closest to Affliction Warlock… This is a pure ranged
  damage spec"; its off-heals are "modest off-healing rather than a healer's
  engine")
- **stalking — damage** ("Closest to retail Feral Druid… You are pressure and
  execute"; "Stalking is a pure DPS spec with no group buff")
- **vizier — healing** ("Vizier does what any pure healer does"; "Vizier is a
  pure mana healer built around Shadra's Prayer and a spread of HoT and AoE
  heals"). Kit corroboration: 11/27 spec abilities mention
  heal/absorb/shield (41%) vs 10–28% on the other three — the healer signal,
  muted because rot's Serpent's Fang line also heals (28%).

| Spec | Primary damage/healing | Main row, in press order (cited from the Rotations text) | Icons | Resource |
|---|---|---|---|---|
| Fortitude | Rage-spender Nature pressure + Exposed Flesh shed loop | Chitin Rush → Venomtip Poison → Hivebreak → Carapace Crash → Barbed Stinger → Expulsion | 6 | Rage (`power` 1), solo full-height |
| Rot | ramping DoTs under Fungal Growth | Wilt → Spore → Venom Bolt → Serpent's Fang → Mycosis → Decay | 6 | mana, solo full-height |
| Stalking | Energy builders into Brood-Mark finishers | Venom Fang → Nerubian Sting → Withering Venom → Facemelter → Rotfang → Widowmaker | 6 | Energy (`power` 3) full + mana `minor` ("A separate mana pool fuels the utility and mobility layer") |
| Vizier | HoT blanket + charge heals | Serpent's Fang → Shadra's Prayer → Shadra's Balm → Mending Mist → Green Salve → Alkahest | 6 | mana, solo full-height |

Main-row derivations, one line each, from the spec pages' Rotations sections:
- *Fortitude:* "Open with Chitin Rush… keep Chitin Rush rolling as your main
  rage-spender. Apply Venomtip Poison… Use Carapace Crash and Hivebreak for
  cleave… apply Barbed Stinger on a tough single target… Shed Exposed Flesh
  via Regrow Exoskeleton / Barbed Stinger / Expulsion." Hivebreak before
  Carapace Crash because Toxic Expulsion makes Hivebreak the Venomtip
  consumer; Regrow Exoskeleton is off-GCD 1-min and sits in the defensive row.
- *Rot:* "apply Wilt and Spore, then Venom Bolt and Serpent's Fang to build
  Fungal Growth… Cast Mycosis for a big direct hit… Layer Decay for the AoE
  mushroom burst."
- *Stalking:* "Build Brood Marks with Venom Fang. Weave Nerubian Sting on
  cooldown… letting Withering Venom ramp its DoT alongside… Spend high-Mark
  finishers, Facemelter… and Rotfang… Once the target drops under 35%,
  Widowmaker."
- *Vizier:* "Lead with Serpent's Fang into your HoTs — Shadra's Prayer, Balm,
  Mending Mist" (difficulty text); "Green Salve is a fast heal that seeks a
  second wounded ally, and Alkahest's charges top and extend Shadra's Prayer."

All four main rows are 6 icons → narrowest row_w(6) = 274px;
`28w − 2 ≤ 1.2 × 274` → **CD_PER_ROW = 11**, confirmed by rowwidths after the
build.

**Resource envelope:** no spec has a countable player-aura resource — Brood
Marks (stalking) live ON THE TARGET, so they render in the target band with a
stack count rather than as an envelope stack bar: per-target state must vanish
on retarget, which the target band does for free and an envelope bar would
fake. Exposed Flesh (fortitude) has an unknown stack cap (Unbreakable raises
it) → on-me stacks, not segments (§6).

**Target band contents:**
- fortitude (harmful): Venomtip Poison, Wicked Poison (by name), Barbed
  Stinger (by name — vulnerability rider unresolved, §6)
- rot (harmful): Wilt, Spore, Venom Bolt (stacking heal cut), Mycosis (absorb
  shield), Suffocating Coil, Fungal Growth (stacks, by name) — the
  maintained-DoT read that IS this spec
- stalking (harmful): Brood Mark (stacks, 804972), Withering Venom,
  Facemelter, Rotfang, Nerubian Sting (stacks)
- vizier (helpful — your HoTs on the CURRENT target only, VuhDo owns raid
  frames): Shadra's Prayer, Shadra's Balm, Green Salve, Mending Mist, Shadra's
  Vigil (by name), Shadra's Aid, Rejuvenating Venom (by name)

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| No Venom active | every spec loses its venom procs; 2-hour buff forgotten after death | **NO VENOM** alert (show-on-missing over the 7 venom ids+names) | mechanism proven in game (Runemaster NO ENGRAVING, Pyromancer NO SKIN); venom aura names pending in-game (§6) |
| Out of Spider Form (stalking) | finishers unusable ("Requires Spider Form") | **NO SPIDER FORM** alert | same show-on-missing shape; form aura name = spell name assumed (§6) |
| Out of Vizier Form (vizier) | "Pre-pull: Vizier Form up" — heal loop degraded | **NO VIZIER FORM** alert | same |
| Wilt/Spore/Venom Bolt drop (rot) | the ramp restarts; "Managing DoT refreshes… is the main way to stretch the pool" | target band bars with time + refresh glow | dot_bars refresh_at proven on shipped classes |
| Brood Marks capped/wasted (stalking) | finisher payout lost; Blistering Fangs refund missed | Brood Mark stacks in target band | stack display proven (aura2 `%s`) |
| Exposed Flesh unshed (fortitude) | mitigation/heal payout lost, physical damage taken ramps | Exposed Flesh stacks on-me + shed buttons in main row with cooldown swipes | stacks proven; shed timing is player judgment by design |
| Rot Lich proc wasted | instant free Serpent's Fang lost | PROC_GLOW → Serpent's Fang | glow mechanism proven; aura name §6 |
| Skulk opener wasted | free 850% Venom Fang lost | PROC_GLOW → Venom Fang while Skulking | same |
| Surprise Strategy wasted (vizier) | instant +20% Shadra's Prayer lost | PROC_GLOW → Shadra's Prayer | same; aura name §6 |
| Charge caps (Alkahest, Carapace Regeneration, Skitter) | wasted charge income | charge count + escalation tiers ANDed with onCooldown | checks 9/10 |
| Unaffordable press (rage/energy/mana dry) | dead button reads as "press me" | desaturate on spellUsable == 0 | check 9 |
| Off-GCD abilities (21 of 44) sweeping on every press | false "not ready" | `use_showgcd` off, derived from the audit | check 10 |

---

## 6. Open questions

- [ ] `UNKNOWN — venom AURA names/ids: activating a Venom is assumed to apply a
      self-aura carrying the venom's name (2h ids 805775/805776/805731/805777/
      630868 + Hallucinogenic 560188 rank=Passive + Weakening 706000 rank=Proc).
      The NO VENOM alert and long-term rows match id OR name and fail soft; one
      in-game read settles all seven.`
- [ ] `UNKNOWN — form AURA names: Spider/Beetle/Weaver/Vizier Form auras
      assumed to carry the spell names (Weaver 704419 and Vizier 504798 are
      teaching-passive-shaped ids, matched by name). Settled by shifting once
      per spec in game.`
- [ ] `UNKNOWN — proc aura names for Rot Lich, Cycle of Decay, Surprise
      Strategy, Death Spray, Tome of Ahn'kahet, A Pit of Snakes, Acidfang
      granted by Acid Burns: displays match name+id and fail soft; the
      verified pass is their checklist.`
- [ ] `UNKNOWN — Widow's Kiss live id: exiles 800885 is a stale revision
      (Stalker Form/Lethal Toxin text); ascension carries 804118/807244/807483/
      807600 under the name. The on-me aura matches BY NAME. No per-press
      "3rd Venom Fang" cue is buildable without a cast counter; deferred.`
- [ ] `UNKNOWN — Fungal Assailant id 503929 is rank=Damage (component smell)
      and the ability has no db.exil.es cooldown row; shipped as a cooldown
      icon on that id, duplicated per spec (no own-id gate). If it never fires,
      the id is wrong, not the mechanism.`
- [ ] `UNKNOWN — Locust Swarm 560247 rank='Spider Lord' and skillbook files it
      stalking while the fortitude page kit lists and rotates it; shipped on
      both (fortitude,stalking) with the id hedge recorded.`
- [ ] `UNKNOWN — Exposed Flesh stack CAP: base cap not stated anywhere scraped;
      Molt applies 15, Unbreakable raises the cap. On-me stack count shipped
      instead of a segmented bar; an in-game read could upgrade it.`
- [ ] `UNKNOWN — Beetle Form alert question: overview says "Fortitude fights in
      Beetle Form, its tank stance" but the rotation swaps it situationally
      ("swap to Beetle Form for Harden and the Reformed shed-heal"). No alert
      shipped — a nag would be wrong half the time. Feedback decides.`
- [ ] `UNKNOWN — Weaver Form (rot): standing form vs shift-tool; regen rework
      07/31 suggests standing. No alert shipped; long-term row only. Feedback
      decides.`
- [ ] `UNKNOWN — Barbed Stinger's Nature-vulnerability debuff ("via Shadra's
      Gift" — 804367 is an empty row): target-band icon matches "Barbed
      Stinger" by name; the actual debuff name needs an in-game read.
      Corrosion (fortitude, no cost/CD/rotation sentence) kept ignore as a
      component-read; related.`
- [ ] `UNKNOWN — vizier SPEC_KNOWN gate: the L10 Shadra's Vigil passive has no
      resolvable teaching id (505203 is the 20s aura), so the gate is Serpent's
      Mist 573305 (L20 Specialization). A vizier below L20 loses spec displays;
      documented trade (Chronomancer precedent).`
- [ ] `UNKNOWN — uncited press order: Venoxis Fang, Rime, Venocannon, Unity,
      Toxflinger, Toxic Sludge, Big Mushroom, Impale, Brood Trap are real
      buttons named in no rotation sentence; shipped in offense/utility rows in
      inventory order.`
- [ ] `UNKNOWN — Cycle of Decay buff effect text (the L50 grant is truncated in
      every scrape); changelog says it lets Spore and Wilt crit. On-me icon by
      name either way.`
- [ ] `UNKNOWN — Serpent Lord (stalking augment): toggle vs passive; utility
      row entry shipped; if it turns out passive the icon never fires and costs
      nothing.`
- [ ] `UNKNOWN — Greater Spider Form Pheromones / Skitterer Form / Ritual
      Cleansing / Blightcap Injestion resolve to no id in either DB; not
      built.`
- [ ] Hedged inventory rows are recorded in the buildlog `inventory-reviewed`
      note; the post-ship verified pass is their checklist.
