---
title: Templar — class pack requirements (Phase 0)
date: 2026-08-08
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, templar, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[sidekick-templar-zealot]]"
  - "[[sidekick-templar-oathkeeper]]"
  - "[[sidekick-templar-crusader]]"
---

# Templar — requirements

Class **19**, token **`MONK`** (from `resources/class-tokens.md` — not
derivable from the name), specs **Zealot** (damage, dual-wield), **Oathkeeper**
(tank, staff), **Crusader** (damage, 2H). No pack exists yet; this is the
Phase 0 document written before any band.

Research source for everything below unless stated: the three Sidekick spec
pages, scraped **2026-08-08** to `resources/sidekick-templar-<spec>.md`, read
against the changelog below. Ids from `resources/exiles-templar.json`
(refreshed 2026-08-08, 472 spells) and cross-checked per §0.

⚠️ **The Sidekick blob (`sidekick-data.js`) is dated 2026-08-02 and the
changelog's newest templar entry is 2026-08-06.** Upstream has published no
newer blob (`sidekick_skills.py --refresh` reported unchanged), so every
Sidekick claim touched by an 08/06 entry is STALE by the recency test and the
changelog wins. The specific collisions are called out inline.

## −1. Changelog — run FIRST

`changelog_watch.py --class templar --pages 6`, scanned 600 entries over
2026/07/31..2026/08/07. **70 new entries**, newest **2026/08/06**. Not
`--accept`ed until the structural ones below are built.

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| **Divine Fury now transforms Vindication instead of Titanstrike** | 08/06 | transform | **§2**. Sidekick's zealot page still says "your Chastise becomes Divine Fury" — two generations stale. The pack pairs Vindication ↔ Divine Fury in one slot, Spell Known on Divine Fury's numeric id (500689) |
| **Scarlet Training now transforms your Argent Blade into Scarlet Hammer, instead of Chastise** | 07/31 | transform | **§2**. Sidekick crusader page still says "transforms your next Chastise into Scarlet Hammer" — stale. Pack pairs Argent Blade ↔ Scarlet Hammer, Spell Known on Scarlet Hammer 500752 |
| **Argent Blade no longer extends the duration of your Oath Chain, and now instead triggers Scourgebane** | 08/06 | reworked | §4 crusader — the "protect the Chain with Argent Blade" rotation prose is void; Titanstrike (and Oath Flow) are the remaining extenders. Sidekick's crusader playstyle is stale here |
| **Reduced the maximum stacks of Oath buffs to 10 (was 20)** | 08/06 | stack cap | §1/§4 — any Oath stack readout caps at 10 |
| **Blessing of Aggramar reworked: Oath Breaker at ≥10 stacks of Oath Chain refreshes active Blade of Faith on nearby enemies** | 08/06 | reworked | §2 zealot — implies **Oath Chain itself stacks**; see §6 UNKNOWN |
| **Warrior of Tyr now 100% proc (was 20%), 10 Energy (was 5)** | 08/06 | proc → deterministic | §1 — no longer a proc worth glowing; it is now flat energy income off periodic damage |
| **Greater Crusader's Oath renamed Greater Gift of Fervor** | 08/06 | rename | §0 — exiles digest (refreshed 08/08) still calls 572630 `Greater Crusader's Oath`; the row carries the new name in Notes |
| Base duration of Oath Chain 15 sec (was 10); Oath Chain talent now +20% (was flat 5 sec) | 08/06 | duration | §1 timer |
| Condemn duration 21 sec (was 15); Blade of Faith 30 sec (was 21) | 08/06 | duration | §4 target band timers |
| Divine Stand base threat 150% (was 110%) | 08/06 | numbers | corroborates oathkeeper = tank (§ roles) |
| Swapped Templar's Might with the Holy Tempest/Whirling Tempest switch node | 08/06 | tree layout | none — no pack impact |
| Gift/Tithe family "persists through death" (16 entries) | 07/31 | QoL | none |
| Scourgebane/Sacred Swing/Reckoning/Blade of Faith/Righteous Upheaval etc. damage numbers | 08/06 | numbers | none |

- [x] changelog scanned, newest entry: `2026-08-06`
- [x] every `replaced with` / `now reads` / `reworked` / rename entry triaged
      into §2 or §0
- [ ] `--accept` after the transforms and stack cap are built (build phase)

---

## 0. Ability surface — both databases

Inventory seeded from `coa-templar-skills.json` (216 skillbook rows) enriched
by the cooldown audit (38 cooldown rows, 28 off-GCD, **0 unresolved**); ids
resolved via `exiles-templar.json` (472 rows). Cross-database sweep
(`crossdb_sweep.py templar`): **227 of 227 inventory rows with an id return
`record` on db.ascension.gg — zero `no-record`, zero `no-response`.**

Wrong-id smells found and resolved by tooltip reads BEFORE the sweep (each
recorded in the row's Notes):

| Ability | Digest id | Problem | Resolution |
|---|---|---|---|
| **Absolution** | 520659 | rank `Proc`, empty tooltip — the documented wrong-id smell | castable is **800424** (db.ascension tooltip: "Taunt all enemies within 8 yds for 4 sec…", 2 min cd); inventory id corrected |
| **Scarlet Hammer** | 500752 | rank `Debuff`, level 10, melee-proc tooltip | castable is **807035** (level 30 = Scarlet Training's level; tooltip "Drop a scarlet hammer… 155% Weapon Damage", 2H-gated); carried in builder CROSSCHECK for the transform face |
| **Greater Zealous Oath** | (none) | skillbook name has no digest id | live spell is **Greater Gift of Zeal 680306** (exiles candidate, level 60; the 07/31 changelog uses the new name) |
| **Mortal Abdication** | 13976911 | rank `Test` — `utility_tables.JUNK` marker | role `ignore` |
| **Light's Grace** | 804913 | skillbook description is literally "This no longer exists." | role `ignore` |
| **Norgannon's Wrath** | 520557 | rank `Root`, no cooldown row | kept (zealot 1/1 active on the Sidekick tree); stays duplicated per the no-cd-row gating rule; §6 |

Known name traps found during review:

- **Sidekick's "full ability kit" lists carry base-class MONK contamination** —
  `Left Hook`, `Right Hook`, `Sacred Slam`, `Staff Sweep`, `Holy Rune`,
  `Engrave Fists`, `Chakra of Wrath`, `Follow Up` refer to the Ascension Monk
  base kit that Templar aliases onto (token MONK), not to CoA Templar
  abilities. They appear 1–4 times in the blob (prose/contamination band) and
  are not in the CoA skillbook seed.
- **`Greater Crusader's Oath` (572630)** renamed `Greater Gift of Fervor`
  2026/08/06 — both databases still answer under the old name.
- **Two `Condemnation` talents exist on the zealot page** (a crit passive and a
  choose-one Zealotry trigger) — a name, not an id, so the inventory rows key
  on ids.

- [x] every inventory row with an id cross-checked against both DBs
- [x] `no-record` rows resolved or explicitly justified in the Notes cell
- [x] deprecated/unused/placeholder names filtered (`utility_tables.JUNK`)

---

## 1. Mandatory buffs

**The class economy.** Every spec runs **Energy** (rogue/monk style,
regenerating; power type 3) with an **Oath** layer on top: builders grant
Oaths, **Oath Breakers** consume them (except Oathkeeper — see §2/Keeping the
Oath). A small mana pool exists but "pays for a couple of utility spells and
nothing else" (zealot page) — **mana gets no bar**; Energy is the one power
band, per the layout rule against rendering a resource the class does not
spend.

| Buff | Source (class/talent/ability) | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Oath Chain** (704576) | class economy | The shared timer every banked Oath rides. Letting it lapse wipes the bank — "let the Chain lapse and every stack goes with it" (crusader page). Base 15s post-08/06 | resource envelope: aurabar on the Oath Chain aura, under the Energy bar |
| **Oath: Righteous Lunge** | builder | typed Oath — "abilities damage and heal for more", stacks to 10 | "on me" buff row with stack count |
| **Oath: Condemn** | builder (crusader) | typed Oath — crit chance, stacks to 10 | "on me" buff row with stack count |
| **Oath: Holy Cleave** | builder (crusader/oathkeeper) | typed Oath — extra target struck, stacks to 10 | "on me" buff row with stack count |
| **Zealotry** proc engine | Zealot spec passive | off-hand autos + Vindication trigger it; Righteous Upheaval's payoff scales with triggers during the Chain | §6 UNKNOWN — whether trigger count is readable as an aura |
| **Heaven's Finest** (805390) | zealot talent | 6 stacks → +100% Energy regen for 8s | "on me" buff row, stacks |
| **Unbroken Creed** (804932) | zealot L50 passive | 3 stacks consumed by damaging Oath Breaker for bonus autos | "on me" buff row, stacks |
| **Scarlet Champion** (805415) / **High General** (524617) | crusader talent | 5 crit stacks → High General: next Chastise +25%, guaranteed crit — a "press Chastise now" cue | PROC_GLOW on Chastise + buff row |
| **Warrior of Dawn** (560648) | crusader talent | half-cost Argent Blade proc; also the Scarlet Hammer transform gate | buff row; the transform itself is §2 |
| **Divine Strikes** stacks | crusader talent | Scourgebane damage ramps Argent Blade +5%/stack to 10 | buff row, stacks |
| **Librams** (Fervor 805423, Zeal 575328, Consecration 801441, Grace 801463, Tenacity 801461) | class kit | "Only 1 Libram spell can be active at a time" — a rolling ~20s steroid the rotation cycles on cooldown | active Libram in buff row; **NO-LIBRAM missing-buff alert** (§5) |
| **Staffguard** (705295) | oathkeeper talent | the absorb each Sacred Swing grants — active mitigation state | buff row (oathkeeper) |
| **Mending Ward** (806273) | oathkeeper talent | 3-stack low-health heal ward | buff row, stacks |
| **Sacred Swing usable window** | oathkeeper | "Only usable after avoiding an attack" — the dodge/parry gate IS the rotation | main row icon desaturate via `spellUsable` (check 9 mechanism) |
| **Gift of Zeal / Gift of Fervor** + Greater versions | class raid buffs | pre-pull buff, persists through death post-07/31 | long-term band |
| **Tithes** (10 auras) | oathkeeper kit | party auras, one active | long-term band (oathkeeper) |

---

## 2. Talent-driven rotation changes

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| **Divine Fury** (zealot, free at L40) | 500689 | **transforms Vindication** (801446) per 08/06 changelog; Sidekick prose ("Chastise becomes Divine Fury every ~10 Zealotries") is stale | the builder button becomes an AoE holy hit when the transform is up | **one slot, two faces**: Vindication icon + Divine Fury icon, Divine Fury gated `["Spell Known"]` on numeric 500689, Vindication shown when 500689 is NOT known (Spell Known inverse) — the fork resolves no overrides |
| **Scarlet Training** (crusader, free at L30) | — (passive) | **transforms Argent Blade** (804929) **into Scarlet Hammer** (500752) per 07/31 changelog (was Chastise) | cast Argent Blade while Warrior of Dawn is active → next Argent Blade is Scarlet Hammer | same mechanism: Argent Blade ↔ Scarlet Hammer pair on Spell Known 500752 |
| **Keeping the Oath** (oathkeeper L10 passive) | — | Oath Breakers **no longer consume Oaths**; 40% of direct damage delayed over 8s (stagger) | oathkeeper spends freely; the Oath bank is not a spend decision | no consume cue on oathkeeper; stagger state is server-side (no aura documented) — §6 |
| **Justicar of the Light** (oathkeeper, choose-one) | — | **removes the cooldown from Benediction** | Benediction becomes spammable | cd icon stays correct either way (a 0-cd spell simply never sweeps) |
| **Chakra of Light** (zealot, optional 0/2 in build) | — | Oath Breakers heal allies around the target | support overlay; "identical rotation, pointed at healing" | nothing structural — same buttons |
| **Fervent Castigation** (zealot choose-one) | — | Righteous Upheaval / Blade of Faith casts grant Oath: Retribution + start the Chain | finisher also opens the Chain | Oath Chain bar already covers it |
| **Testament of Strength** (crusader) | 300514 | next 3 Titanstrikes usable at any health % | converts the execute into a bankable Chain extension | cd icon + buff row entry; Titanstrike's <35% gating is server-side (`spellUsable` desaturate carries it) |
| **Blessing of Aggramar** (zealot, reworked 08/06) | — | Oath Breaker at ≥10 Oath Chain stacks refreshes Blade of Faith on nearby enemies | changes when to re-cast Blade of Faith | no new surface; Blade of Faith DoT timer already on target band |
| **Battle Hardened / Upheave!** etc. choose-ones | — | cooldown/number tweaks | none | cd triggers read live values |

Every transform row must read correctly **with and without** the talent: the
base face is the default; the replacement face only appears when the
replacement id is known. Below L30/L40 the passives are absent and the base
buttons never swap — correct by construction.

---

## 3. Pets

**None.** Answered explicitly:

- [x] Does this class summon a pet? **No permanent or cooldown pet.** The only
  summons are **Testament of Hope** (1397742: "Summons 2 copies of yourself
  that charge at a nearby enemy… 20 seconds", a defensive: each copy −10%
  damage taken) and Crusader's **Mirror Image** (confusion copies). Both are
  fire-and-forget cooldowns, not controllable pets.
- [x] Pet abilities the player presses or reacts to? **No.**
- [x] Pet buffs/debuffs to track? **No** — the copies' damage-reduction rides
  on the player and the cooldown icon covers it.
- [x] Does pet presence gate the rotation? **No.**
- [x] Pet resource? **No.**

No pet section. Testament of Hope is an ordinary defensive cooldown row entry.

---

## 4. Primary damage source and the main rows

Rotation text: the per-spec Sidekick pages (Playstyle / Rotations / Resource
sections), corrected by the 08/06 changelog where stale. Press order below is
the citation's order, not an invention.

| Spec | Primary damage | Main row, in press order | Icons | Resource / segments |
|---|---|---|---|---|
| **Zealot** | Condemn DoT + Zealotry procs + Oath Breaker finishers | Condemn · Righteous Lunge · Vindication(↔Divine Fury) · Righteous Upheaval · Blade of Faith · Holy Cleave | 6 | Energy bar + Oath Chain bar |
| **Oathkeeper** | Oath loop into Reckoning/Benediction; survival is the job | Sacred Swing · Righteous Lunge · Reckoning · Benediction · Holy Cleave · Chastise | 6 | Energy bar + Oath Chain bar |
| **Crusader** | typed-Oath maintenance; Condemn/Blade of Faith DoTs, Chastise(↔Scarlet Hammer) nuke | Righteous Lunge · Holy Cleave · Condemn · Argent Blade(↔Scarlet Hammer) · Chastise · Titanstrike · Blade of Faith | 7 | Energy bar + Oath Chain bar |

Row-by-row rationale (one line each, from the cited text):

- **Zealot**: "Stack Condemn early… keep it up" → Condemn first; "Build Oaths
  with Righteous Lunge and Vindication" → builders next; "Righteous Upheaval
  when you've triggered enough Zealotry… otherwise Blade of Faith" → the two
  finishers; "spread Condemn… with Holy Cleave" → AoE last. Chastise is off
  zealot's main row: the cited finisher choice is Upheaval-else-Blade-of-Faith,
  and Divine Fury (the transform) occupies Vindication's slot when up.
- **Oathkeeper**: "use Sacred Swing off your dodges and parries to keep Oaths
  flowing" → first; Righteous Lunge the unconditional builder; "Spend into
  Reckoning as your default Oath Breaker" → Reckoning; "Benediction is your
  baseline reactive heal… bank toward Benediction by default" → Benediction;
  Holy Cleave for cleave packs; "Switch to Reckoning/Chastise only when a pull
  needs to die faster" → Chastise last.
- **Crusader**: "Open with Righteous Lunge" → first; "Build Holy Cleave for the
  extra-target Oath" → second; "Condemn for the crit Oath and its stacking
  DoT" → third; Argent Blade is the Chain-era spam/heal button and the Scarlet
  Hammer face (still the self-heal + Scourgebane trigger post-08/06); "Dump
  into Chastise… or Blade of Faith"; "Titanstrike is your execute below 35%".
  Righteous Tempest is a deliberate AoE spender → offensive cooldown row, not
  main ("Deliberately hold your Oath Breakers here").

**Narrowest main row = 6 icons** (zealot, oathkeeper) → `row_w(6) = 274px`;
`CD_PER_ROW`: `w*28 - 2 <= 1.2 * 274` → `w <= 11.9` → **11**. Verified by
`rowwidths.py` after build. (Recomputed for this pack; never copied.)

**Resource envelope (fixed height, all specs identical):**
- **Energy** — `power_trigger(player, 3)`, full-height bar, value text.
- **Oath Chain** — aurabar on aura 704576 (timer + its stack count if it
  stacks; §6). The bank's shared timer is the one number the class is played
  around on every spec.
- Mana: **not rendered** (utility-only pool).
- Typed Oath stacks (10 max each) render as stack counts on their "on me"
  buff-row icons, not as segment bars — three 10-cell bars would triple the
  envelope for numbers that are secondary to the Chain timer.

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Condemn dropped | "a huge share of your damage per press" (zealot); crit Oath (crusader) | target-band DoT bar + refresh glow at ≤4s | check 13 inventory row; in-game sweep (§6) |
| Blade of Faith dropped | hard-critting 30s DoT | target-band bar + refresh glow | same |
| Oath Chain about to lapse | whole Oath bank wipes (crusader explicitly) | Oath Chain aurabar in the envelope; low-time tint | aura2 `expirationTime` condition — needs no GCD guard (aura trigger) |
| Libram not running | rolling ~20s steroid offline; Lorescribe/Fury of Aggramar feedback loops stall | **NO LIBRAM missing-buff alert** (aura2 `showOnMissing` over all five Libram buffs — the classic seal/stance upkeep shape) | alert is inverse-triggered; verified by the same mechanism as Runemaster's NO ENGRAVING (in-game §6) |
| High General up, Chastise not pressed | guaranteed-crit +25% Chastise wasted | PROC_GLOW on Chastise off High General (524617) | check 9/10 machinery; buff row shows the proc |
| Righteous Upheaval pressed early (zealot) | payoff scales with Zealotry triggers during the Chain | §6 UNKNOWN — no readable counter found in scrapes | — |
| Off-cooldown finisher unaffordable | icon reads "press me" while Energy is short | `spellUsable == 0` → desaturate on every cd icon | check 9 |
| Off-GCD ability sweeping on every press | false "not ready" | `use_showgcd` off for every `gcd:false` ability from the audit | check 10 |
| Titanstrike above 35% health | dead button outside execute | `spellUsable` desaturate (server refuses the cast) | check 9; in-game confirm (§6) |
| Sacred Swing without a recent avoid | oathkeeper's Oath engine stalls | `spellUsable` desaturate on the main-row icon | check 9; in-game confirm (§6) |
| Testaments locked by Sacred Restraint | defensive/offensive Testaments compete (1 min lockout) | Sacred Restraint in the buff row (debuff on self) | §6 — aura id needs confirming |

---

## 6. Open questions

- [x] **Does Oath Chain stack? YES — answered from db.ascension.gg 704576:**
  "Allows you to hold Oath buffs. Once 10 stacks are reached you are unable to
  build more Oaths." The Chain aura IS the Oath bank counter; the envelope bar
  shows its timer and `%s` stacks.
- [ ] **Zealotry trigger count during the Chain** (Righteous Upheaval's
  payoff): UNKNOWN — no aura in either database is named as the counter.
  What settles it: in-game aura scan during a Chain (`/rmdump` differ).
- [x] **Typed Oath aura ids — answered from the exiles digest:**
  `Oath: Righteous Lunge` 804904 ("abilities damage or heal for 5% more"),
  `Oath: Condemn` 804922 (+3% crit), `Oath: Holy Cleave` 804903 (extra
  target), `Oath: Argent Blade` 807931, `Oath: Retribution` 804924. All have
  inventory rows. Still open: `Oath: Vindication` — digest 704244 is marked
  `unused` and carries the OLD crit text, so that display matches by NAME.
- [x] **Sacred Restraint aura id**: 102208 (exiles digest); buff row.
- [x] **Keeping the Oath stagger readout** (oathkeeper): the digest carries
  **`Oathkeeper` 803237** — "40% of damage taken is now delayed and dealt to
  you over 8 seconds" — which is the stagger aura by name. Buff-row entry;
  whether it exposes the delayed POOL SIZE stays open for the in-game pass.
- [ ] **Monk-chassis kit** (Left/Right Hook, Sacred Slam, Staff Sweep, Holy
  Runes, Follow Ups, Chakra of Wrath, Templar Strike, Flaming Blade,
  Quickpalm, Beatdown…): ~30 castable-looking rows the MONK token carries that
  no CoA templar tree node or rotation text names. All `ignore` with per-row
  reasoning. If feedback says templars actually weave these, they get a band —
  that is a feedback question, not a research one.
- [ ] **Spiritual Abdication** (704408, oathkeeper, 1 min cd): tooltip body is
  EMPTY on db.ascension.gg — nothing citable to draw. Ignored until the
  in-game pass says what it does.
- [ ] **Eternal Blessing / Aggramar's Will / Norgannon's Wrath** have no
  db.exil.es cooldown row — cooldown icons render off their live values, and
  the three stay duplicated per the no-cd-row gating rule.
- [ ] **Unbroken Creed** files under crusader in the skillbook but the zealot
  tree carries it as the L50 passive — buff row spans both until the in-game
  pass settles it.
- [ ] **Weak Spot** (zealot): 16.667 min cooldown for +3% phys for 15s —
  ignored as an unpolished oddity; feedback can promote it.
- [ ] **Scarlet Hammer / Divine Fury transform mechanics in client terms**:
  built as Spell Known on the replacement ids (500752 / 500689) per the
  fork's no-override rule; whether the server grants/removes the spell (vs an
  action-bar-only swap) is confirmable only in game. If the icon never swaps,
  the base face stays — a readable, non-lying fallback.
- [ ] **Energy max** (100 vs talent-modified) — bar reads live UnitPower so no
  build dependency; note only.
- [ ] Whether the five Librams are learnable side-by-side at all levels
  (affects how loud the NO LIBRAM alert may be while levelling). Alert gates
  on the class token only, same trade Runemaster took.
