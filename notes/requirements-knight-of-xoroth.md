---
title: Knight of Xoroth — class pack requirements (Phase 0)
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, knight-of-xoroth, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[sidekick-knight-of-xoroth-war]]"
  - "[[sidekick-knight-of-xoroth-hellfire]]"
  - "[[sidekick-knight-of-xoroth-defiance]]"
---

# Knight of Xoroth — requirements

Class **17**, token `FLESHWARDEN`, specs **War**, **Hellfire**, **Defiance**.
First build — no pack exists yet.

Research sources, in precedence order used below: the 2026/07/31 changelog
batch (dev statements), db.exil.es digest / JSON API (scraped 2026-08-07:
`exiles-knight-of-xoroth.json` 413 spells, `spell-meta-knight-of-xoroth.json`
413 rows), db.ascension.gg tooltips (curl, 2026-08-07), and the three Sidekick
spec pages scraped 2026-08-07 to `resources/sidekick-knight-of-xoroth-<spec>.md`.
The Sidekick skill blob (`sidekick-data.js`, snapshot 2026-08-02) POSTDATES the
newest class changelog entry (2026-07-31), so `coa-knight-of-xoroth-skills.json`
(208 entries) is current — with one known stale tooltip, see §-1 (Seeking
Flame).

**Spec roles** (added to `resources/spec-roles.md`, provenance = Sidekick kit
statements pending in-game observation):

- War — damage. "Middling sustained single-target DPS … damage dealer" on
  every PvE/PvP line; "no big damage-reduction cooldown"
  (sidekick-knight-of-xoroth-war).
- Hellfire — damage. "Closest to Vengeance Demon Hunter, **re-tuned as a pure
  damage spec rather than a tank** … essentially no defensive cooldown of its
  own" (sidekick-knight-of-xoroth-hellfire).
- Defiance — **tank**. "Strong dungeon tank — AoE pulls and threat", "Middling
  main-tank for raid bosses", stat priority "Defense rating (to
  crit-immunity)" (sidekick-knight-of-xoroth-defiance). Follows the
  felsworn-tyrant precedent: nothing structural changes — its main row is the
  cited tanking loop, role recorded with citation.

No spec heals anyone: war "Nothing you have heals anyone but you", hellfire
"No healing or lifesteal in the spec at all", defiance "No external healing
anywhere". **No healing target band anywhere; enemy-target DoT band only.**

---

## −1. Changelog — 13 entries, scanned FIRST (2026-08-07, pages 6)

Newest class entry: **2026-07-31**. All scrapes below are 2026-08-07 →
fresher than the changelog. NOT `--accept`ed until triaged (this table).

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| Lesser Pestilence of Apocalypse → Imp mana every 5 sec | 07/31 | pet numbers | §3 — pet-internal (806962 is rank `Pet`), no player button |
| Greater Imp abilities now cost mana (bugfix) | 07/31 | pet bugfix | §3 — Imp spellbook, not player buttons |
| Greater Imp AP +31% / SP +36% scaling | 07/31 | numbers | none |
| Burst base damage +35% | 07/31 | pet numbers | §3 — Imp ability (no player-skillbook entry; not in `coa-knight-of-xoroth-skills.json`) |
| Burning Slap base damage +22% | 07/31 | pet numbers | §3 — Imp ability (630930, rank-less, gcd 0) |
| **Doom 30 s → 1 min CD, +50% Imp damage, 20 s** | 07/31 | player CD change | §4 hellfire cooldown row — db.exil.es 802602 already shows cd 60000/dur 20000, post-changelog ✓ |
| Burning Slap extends Burning Mischief 2 s | 07/31 | pet mechanics | §3 — Imp-internal |
| **Burning Mischief now 30 s CD, 100% leech, +15% Fire** | 07/31 | pet CD change | §3 — Imp ability (630933 shows cd 30000 ✓, post-changelog) |
| Hellstorm direct +40%, DoT doubled | 07/31 | numbers | none |
| Hellfire Forgemaster +10% | 07/31 | numbers | none |
| Infernal Bulwark rework (armor contribution, blocked −15%) | 07/31 | talent numbers | none (passive mitigation, no WA surface) |
| Hellsmelted Armor +5/10% block at all times | 07/31 | talent numbers | none (passive; per-imp part already §3) |
| **Seeking Flame now generates 2 "Deathfire", up from 1** | 07/31 | resource numbers | §4 — "Deathfire" returns ZERO hits on db.ascension.gg name search (2026-08-07): dev shorthand for **Demonfire**. Sidekick's tooltip still reads "Generates 1 Demonfire" — known stale spot. No WA impact (we track the stack aura, not the generation rate) |

- [x] changelog scanned, newest class entry: `2026-07-31`
- [x] every entry triaged into the sections below — zero replaced/reworked/
      new-player-spell entries; the batch is Imp (pet) tuning + numbers
- [x] `--accept` after this table was written (all entries acted on above)

---

## 0. Ability surface — both databases

`tools/crossdb_sweep.py knight-of-xoroth` over the whole reviewed inventory;
verdicts in `resources/crossdb-knight-of-xoroth.json`, consequences in the
inventory Notes cells.

Known traps found during id resolution (db.exil.es side), all corrected in the
inventory before the sweep:

| Name | Wrong id | Why | Castable |
|---|---|---|---|
| Pestilence of War | 680815 | rank `Heal` — the DF-spent heal component | **802345** (db.ascension: "Emanate a pestilence… each Demonfire spent heals 1%", 4 s cd). 802604 is the PET's copy (rank `Pet`) |
| Pestilence of Apocalypse | 704467 | rank `Damage` — component | **804786** ("Emanate the Pestilence of Apocalypse… 10% increased Fire damage", 4 s cd). 806962 is the PET's copy |
| Sacrificial Circle | 706752 | rank `Force` — component (706753 is the `Heal` half) | **805677** (full tooltip, 1 min cd) |
| Demonfury | 805668 | tooltip carries **DISABLED** marker; only id of that name in either DB | excluded from every band — the documented deprecated/unused filter. §6 |
| Demon's Blood (aura) | 573453 | rank `Shapeshift Holder` — a holder | **800999** is the stacking player buff ("stacking up to 10 times"); 804345 is the granting passive |

Sweep result (2026-08-07): **216/216 id rows asked, 213 record, 3 no-record —
all three resolved OTHER-ID by name re-ask + tooltip read** (the same ability
under a different id on db.ascension.gg): Consuming Blade 500909 → 804843
(live 30-Rage/Demonfire tooltip; 573330 is the Deprecated rank-6 legacy),
Fist of Xoroth 500025 → 806038 (the 5 s stun strike), Flesh Hook 500020 →
800605 (pull + 10 Rage). All three are drawn with name-matched triggers, so
the id split costs nothing.

- [x] every inventory row with an id cross-checked against both DBs
      (`crossdb-knight-of-xoroth.json`)
- [x] `no-record` rows resolved by name re-ask + tooltip read, verdict in Notes
- [x] deprecated/unused/placeholder names filtered (`DISABLED`, `Hidden`,
      `SLS`, `Remover`, `Checker`, `Holder` families)

---

## 1. Mandatory buffs

**Class-wide.**

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Demonfire** (aura **500906**, "Consumed to empower abilities. Stacks 6 times") | class economy | every spec is build-and-spend on it: war builds with Gore/Meatsaw/Brimstone Bludgeon, spends on Skulltaker/Warbringer; hellfire builds with Infernal Strike (2)/Seeking Flame, spends on Hellmaw/Skulltaker/Flames of Xoroth/Hellfire Form; defiance builds with Shieldgore (2)/Implosion, spends on Suffuse/Hellfire Bellows/Hellrider | resource envelope, 6-cell stack bar, all three specs — §4 |
| **Demon's Blood** (aura **800999**, stacks to 10; Heart of Xoroth raises the cap) | class passive (804345: damage taken 25% → 3 Rage + a stack; war's Bloodied Blade: melee damage → a stack) | fuels Black Shield's absorb and Juggernaut's DR/heal; war's Chop Shop crit and Hellborn auto-unleash key off it | resource envelope, thin 10-cell minor stack bar — §4 |
| **Active Pestilence** (War 802345 / Death 801054 / Conquest 801053 / Apocalypse 804786 / Famine 802344 — all "Emanate…", 4 s cd, infinite aura) | class kit | the stance system: war reads "Keep Pestilence of Death active before every pull"; hellfire "Keep Pestilence of Apocalypse up almost constantly". Missing = quiet throughput loss | long-term band (active-only, one icon per pestilence) + `NO PESTILENCE` alert — §5 |
| **Suffuse** (801063, self-heal + DR, "Lasts N sec for each Demonfire consumed") | class kit (tree AE node) | the class self-sustain; defiance's primary spender | defensive row + "on me" running buff |
| **Black Shield** (805679, 2 min cd, off-GCD) | class kit | the Demon's Blood absorb | defensive row + "on me" |
| **Juggernaut** (520294, 2 min cd, off-GCD) | class kit | the Demon's Blood DR + tick-heal window | defensive row + "on me" |
| **Demon Heart** (805669, 1 min cd, off-GCD, +6 Demonfire) | class kit | instant resource refill — burst setup | offensive row |
| **Burning Rage** (520295, 1 min cd) | class kit | CC-immunity enrage window | utility row + "on me" |

**War.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| Pestilence of Death up | 801054 | "+crit damage… Keep active before every pull" (dungeon rotation text) | long-term + alert (class-level) |
| **Gorged / Goredrenched** (Gorged 681205; Goredrenched 805964, 30 s) | Gore's lifesteal loop; "at 3 stacks empowers your next Brimstone Bludgeon" | the sustain loop — "Keep Gore rolling for its Gorged lifesteal" | "on me" buff row, stacks |
| **Decimation** (524913, 2 min cd, off-GCD, 30 s window) | war ability | "next Skulltaker or Warbringer guaranteed crit" — burst-window setup | offensive row + PROC_GLOW on Skulltaker/Warbringer while its buff is up |
| **Burning Blade** (524919, off-GCD) | war ability | attack-counted weapon ignite + armor pen while active | "on me" buff row |
| **Conqueror's Will** | war ability | party crit buff — "Keep Conqueror's Will's party crit buff up too" | long-term band |
| The Butcher / Demonic Frenzy / Hellknight stacks | war passives | ramp state | "on me" buff row (active-only) |

**Hellfire.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| Pestilence of Apocalypse up | 804786 | "up almost constantly so nearby enemies take increased Fire damage" | long-term + alert (class-level) |
| **Hellfire Form** (ranked 503300–503308 + 805696/807433 — rank id UNKNOWN §6) | hellfire ability, 3 min cd | the Metamorphosis-style burst window, fueled by banked Demonfire | offensive row + "on me" running buff |
| **Melt** debuff on target (803334, 24 s) | hellfire ability | armor shred per Demonfire consumed, +damage taken from Blade/Flames of Xoroth | target band |
| **Hellmaw** DoT (806965, 12 s) | hellfire spender | the hit-and-burn | target band |
| **Seeking Flame** slow | hellfire filler | "the slow keeps pressure on" | target band (situational — see §4) |

**Defiance.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Hellfire Imps active** (Call: Hellfire Imp 804883, 10 s cd; Implosion 524897; Brimstone Buckler block procs; 30 s duration each, Servitude extends) | spec identity | "more imps out means more mitigation" (Imp Guards, Imp Aura, Hellsmelted Armor per imp); Sacrificial Circle fuel | imp-count display — §3/§6 (counting mechanism UNKNOWN) |
| **Curse of Xoroth** DoT on target (503472, 45 s cd, 10 s) | defiance ability | the DoT that primes Black Shield via Ritual Fire (302552) | target band |
| **Torn Flesh** on target (800341, 15 s, from Shieldgore/Meatsaw) | spec | the bleed the kit scales against | target band |
| **Soul Furnace** absorb (from Sacrificial Circle) | defiance | the leave-behind shield | "on me" buff row |
| **Hellrider** (803889, 10 s+) | defiance ability | haste/speed window per Demonfire | "on me" buff row |
| **Legion's Presence** (804879, 3 min cd, 15 s) | defiance ability | ally damage-buff aura window | offensive row |

**Defiance addition found during the role pass:** **Oath of Defiance** —
"Increases threat generated, causes you to generate Rage when taking damage,
and your block rating is increased by % of Strength. Reduces damage dealt"
(SK defiance kit) — the TANK STANCE. A defiance character without it is
quietly not tanking, which is exactly the missing-imbue shape → long-term row
+ a `NO OATH` alert (§5).

**Missing-buff alerts** (§5): `NO PESTILENCE` on **war and hellfire only** —
the Pestilence abilities live in those two kits (skills JSON: Death/War/
Conquest war, Apocalypse hellfire+war, Famine hellfire; the defiance page
never names one), so the alert is per-spec, the Stormbringer NO AEGIS shape,
gated on knowing that spec's own pestilence. No imbue/weapon-kit alert — the
class has no engraving-like pre-pull kit. Hellfire additionally gets the
`NO PET` alert — see §3 (gated on knowing Summon: Greater Imp).

---

## 2. Talent-driven rotation changes

All five player-button transforms are stated verbatim in the Sidekick talent
tooltips ("Transforms your X into Y"); this fork resolves no spell overrides,
so each is tracked on the REPLACEMENT's own id (native Spell Known — a 3.3.5
server changes a button by granting the new spell and taking the base away).

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| **Brimstone Bludgeon** (war TE) | 520005 | "Transforms your Sever into Brimstone Bludgeon" | the AoE keystone + Pestilence unleash — named first in the war rotation | war main row tracks **520005** directly; base Sever (500904) not drawn on war main (talent is build-defining per the cited loop). Untalented/levelling character: see note below |
| **Warbringer** (war TE) | 802581 | "Transforms your Flames of Xoroth into Warbringer" | the second Demonfire-scaling AoE slam | war offensive row tracks **802581** directly; base Flames of Xoroth stays hellfire-only |
| **Shieldgore** (defiance TE) | 804353 | "Transforms your Infernal Strike into Shieldgore" | the spec's main threat/damage button + 2 Demonfire | defiance main row tracks **804353** directly; base Infernal Strike stays hellfire-only |
| **Hellfire Bellows** (defiance TE, choose-one) | 520292 | "Transforms your Flames of Xoroth into Hellfire Bellows" | the Demonfire-dump AoE cone | defiance offensive row tracks **520292**, self-gated on its own id known → absent untalented, no dead button |
| **Impcaller** (defiance TE, choose-one) | passive 706755 | "Transforms your Call: Hellfire Imp into Impcaller" — Infernal Strike summons an imp instead, Call button goes away | imp generation moves onto the rotation | Call: Hellfire Imp (804883) kept on the defiance row own-id-gated; with Impcaller taken the base id stops being known and the icon self-removes. Impcaller grants no new button (it is an aura on Infernal Strike) — nothing else to draw. §6 |
| **Doom** (hellfire) | 802602 | "Transforms your Greater Imp into a Doomguard" for 12–20 s | pet burst window | ordinary hellfire offensive-row cd icon (a player button with its own id — pet transform, not a bar transform) |
| **Greater Imp** (hellfire tree node) | 92101 grants Summon: Greater Imp 520661 | the spec's pet exists at all | §3 — `NO PET` alert gated on knowing 520661 |
| **Suffuse** (class AE node) | 801063 | grants the castable | defensive row entry, own-id-gated on every spec |
| **Charges** | — | Gore "2 Charges, 8 sec recharge" (805555); Hellbound Charge "2 Charges, 60 sec recharge" (807247) | — | `CHARGES` table |

With/without check: the three main-row transforms assume the talented state,
which is the spec's defining loop per the cited Sidekick text (same declared
assumption as Stormbringer's Tempest Sovereign row — said here explicitly). An
untalented character loses those icons (Spell Known on the replacement fails)
rather than seeing a dead button; base Sever / Infernal Strike / Flames of
Xoroth are not double-drawn because each base belongs to a different spec's
row. Every other talent row only ADDS an active-only display, correct
untalented.

---

## 3. Pets — the pet class of this batch

- [x] Does this class summon a pet? **Hellfire: YES — permanent Greater Imp**
      (Summon: Greater Imp **520661**, duration −1, granted by the hellfire
      tree node Greater Imp 92101, "Level 10 Passive Teaches you Summon:
      Greater Imp"). **Defiance: temporary imp swarm** — Hellfire Imps
      (30 s each) from Call: Hellfire Imp 804883 (10 s cd), Implosion 524897
      (40 s cd), Brimstone Buckler block procs; plus **Call: Hellfire Abyssal**
      805074 (45 s cd, cooldown-length summon). **War: none** (Evil Duo, a war
      L50 passive, references "your Greater Imp" — cross-tree AE pick synergy;
      no war summon button. `ignore` as a button, noted so nobody re-asks).
- [x] Player-pressed pet-related buttons: hellfire — Summon: Greater Imp
      (520661), Doom (802602, transforms the pet), Recall Imp (revive; id via
      crossdb §6); defiance — Call: Hellfire Imp, Implosion, Call: Hellfire
      Abyssal, Sacrificial Circle (805677, consumes imps), Demonic Grit
      (805678, 3 min, buffs summons). All real cooldown-row entries, not
      `ignore`.
- [x] Imp's OWN abilities (changelog: Burst, Burning Slap 630930, Burning
      Mischief 630933, Lesser Pestilences 802604/806962/803255): the Imp's
      spellbook — rank `Pet` markers, mana costs, "your Imp/Doomguard deals…"
      phrasing. The player never presses them → `ignore`, the Chronomancer
      Chronobuff precedent. Decided per tooltip, recorded here.
- [x] Pet presence gates the rotation: hellfire yes — "excellent single
      target damage and control" rides the Imp; Doom/Hellfire Rituals/Evil
      Duo/Impish Pestilence all key off it. `NO PET` alert for Hellfire, the
      stormbringer/tinker shape: trigger 1 asks unit="pet" for a pet aura and
      fires on absence, trigger 2 gates on `IsSpellKnown(520661)` so a
      character who cannot summon is not nagged. Pet aura family: Greater Imp
      Scaling 520662 (dur −1) — candidate, §6.
- [x] Defiance imps do NOT get a `NO PET` alert — they are 30 s cooldown-
      length summons regenerated by the rotation itself; the useful display is
      an imp COUNT, whose mechanism is UNKNOWN (no player-side stack aura
      found in either DB; Hellfire Imp Hidden Aura 302546 is rank
      `Hellsmelted Armor`, a component). §6. Draft ships without a count.
- [ ] Pet resource: the Greater Imp casts from ITS mana (changelog). No
      player-side display — nothing rendered. (A pet mana bar is one band too
      many for a draft; noted §6 for feedback.)

| Pet | Summoned by | Duration | Track | Renders |
|---|---|---|---|---|
| Greater Imp | 520661 (hellfire, tree-granted) | permanent | presence (`NO PET` alert); Doom window (802602 cd icon + its 12–20 s buff on pet, `unit="pet"`) | hellfire alerts + offensive row |
| Doomguard | Doom 802602 | 12–20 s | the transform window | "on me"/pet aura while Doom runs |
| Hellfire Imps | 804883 / 524897 / block procs (defiance) | 30 s | count UNKNOWN §6; Sacrificial Circle (805677) and Demonic Grit (805678) as cd icons | defiance rows |
| Hellfire Abyssal | 805074 (defiance) | short | fire-and-forget | offensive row cd icon |

---

## 4. Primary damage source and the main bar

Press orders from the Sidekick per-spec rotation text (solo/dungeon
paragraphs), imported as citations.

| Spec | Primary damage | Main row, in press order | Icons | Resource / segments |
|---|---|---|---|---|
| War | Demonfire spenders (Skulltaker) + Brimstone Bludgeon cleave | Brimstone Bludgeon · Gore · Meatsaw · Skulltaker · Sever* | 5 | rage bar + **Demonfire 6-cell** + Demon's Blood minor |
| Hellfire | Demonfire dumps (Hellmaw/Flames of Xoroth) inside Hellfire Form | Infernal Strike · Seeking Flame · Hellmaw · Flames of Xoroth · Skulltaker | 5 | rage bar + Demonfire 6-cell + Demon's Blood minor |
| Defiance | Shieldgore threat + Suffuse sustain | Shieldgore · Call: Hellfire Imp · Suffuse · Implosion · Hellfire Bellows | 5 | rage bar + Demonfire 6-cell + Demon's Blood minor |

\* Sever: the war row carries Brimstone Bludgeon (the transform); Sever's slot
is the rage top-up filler the rotation text names ("using Sever to top up
rage"). Because BB transforms Sever, both never co-exist: each is own-id-gated
(Spell Known), so the row shows Sever untalented and Brimstone Bludgeon
talented — rowwidths counts 5 either way at runtime. War quotes: "Open hard
pulls with Brimstone Bludgeon … build Demonfire with Gore … and Meatsaw …
using Sever to top up rage. Dump stacked Demonfire into Skulltaker." Hellfire:
"weave a cheap filler strike in Infernal Strike … firing Seeking Flame …
dump stacked Demonfire into Hellmaw … or into Flames of Xoroth for AoE …
Skulltaker for a crit finisher." Defiance: "Shieldgore on cooldown … Call:
Hellfire Imp on cooldown … Hellfire Bellows against packs … Implosion on
pulls … Dump Demonfire into Suffuse liberally."

- **Rage bar** — `UnitPower` type 1 (rage) on the player, full-height primary
  bar. "Rage is primary… It never goes dry the way mana does" (all three spec
  pages) — but spend gating is real, so the bar stays primary.
- **Demonfire** — ONE aura (**500906**), stacks 0–6 ("Stacks 6 times";
  Demon Heart grants 6; Rain of Chaos keys off "a full 6") → `aura_stacks`
  6-cell segment bar, the Pyromancer-ember mechanism. Bringer of Fire
  (hellfire passive) raises the cap — cells stay 6 in the draft, §6.
- **Demon's Blood** — ONE aura (**800999**), stacks to 10 (Heart of Xoroth
  raises it) → thin `minor` 10-cell stack bar. It is genuinely background AND
  independent (it feeds Black Shield/Juggernaut when SPENT, not converted),
  so `minor`, not `fused`.
- Narrowest main row is 5 icons on every spec → `CD_PER_ROW` from
  `28w − 2 ≤ 1.2 × (5·44 + 4·2 = 228)` → **w ≤ 9.8 → 9**, to be confirmed
  with `tools/rowwidths.py` on the built pack.

Off the main row, still cited: war — Warbringer, Decimation, Demonfury
(EXCLUDED — DISABLED, §0), Burning Blade, Demonfury's slot goes to Demon
Heart; hellfire — Hellfire Form, Doom, Hellstorm, Melt, Unleash Pestilence;
defiance — Curse of Xoroth, Sacrificial Circle, Call: Hellfire Abyssal,
Legion's Presence, Hellstorm, Chains of Xoroth.

---

## 5. Miss-handling

| Ability / state | Cost of missing it | Cue | Proof the cue fires |
|---|---|---|---|
| No Pestilence emanating (war/hellfire) | war: crit damage + rotation healing (Pest. of War: "your rotation is your healer"); hellfire: 10% Fire damage taken field | per-spec `NO PESTILENCE` alert — fires when none of the five Emanate auras (802345/801054/801053/804786/802344) is up AND the spec's own pestilence is known | inverse aura trigger + spell-known gate, `NEEDS_ALL` — the Stormbringer NO AEGIS shape; in-game proof post-ship |
| Melt / Curse of Xoroth / Torn Flesh / Hellmaw dropped | armor shred / Black Shield priming / bleed lost | target-band bar with refresh glow ≤4 s | `dot_bars` refresh condition on aura `expirationTime` (no GCD guard needed on aura triggers) — mechanism shipped on 9 classes |
| Decimation window wasted | guaranteed-crit Skulltaker/Warbringer lost | PROC_GLOW on Skulltaker + Warbringer while the Decimation buff is up | `PROC_GLOW` — check 9 asserts escalation tiers ANDed with `onCooldown` |
| Demonfire dumped low / overcapped | weak finishers / wasted generation at 6 | 6-cell bar right under the main row | segment-bar mechanism verified in game on Pyromancer (ember) |
| Skulltaker/Suffuse pressed unaffordable | wasted press | desaturate on `spellUsable == 0` on every cd icon | check 9 *desaturate when unusable* |
| Off-GCD buttons sweeping falsely | phantom cooldown | `use_showgcd` off, derived from `cooldown-abilities-knight-of-xoroth.json` (Decimation, Black Shield, Juggernaut, Demon Heart, Burning Rage, Chainwhip, Implosion, Chains of Malice, Hellhaul, Legion's Presence…) | check 10, both directions |
| Cooldowns coming back | clipped burst | urgency tiers 20/10/5 ANDed `onCooldown == 1` | check 9, *no bare expirationTime tier* |
| Greater Imp dead (hellfire) | the spec's ST damage rides it | `NO PET` alert (pet-unit aura absence AND Summon known) | stormbringer §6.6 mechanism — absent-unit inverse unverified on this fork; deferred with it |

---

## 6. Open questions

- [ ] **6.1 Demonfire aura id in game.** 500906 is the only "Demonfire"
      stack aura in either DB ("Stacks 6 times") but its tooltip carries a
      "Requires Shadow Form" line — a holder smell. Decoys: Demonfire Hidden
      2–6 (680816, 704217, 707630, 707718, 707914, all dur −1). Bar matches
      by id 500906 + name fallback. Settles: one in-game read of the buff.
- [ ] **6.2 Demon's Blood aura id.** 800999 ("stacking up to 10 times") vs
      the 573453 holder and 520298 SLS2 stub. Matched by 800999 + name.
      Settles: in-game buff tooltip.
- [ ] **6.3 Hellfire Form castable rank.** 503300–503308 are ranks 1–9(+);
      805696 / 807433 also exist. spell-meta picks 503300 "Rank 2". A ranked
      id cannot be own-id-gated and the cd icon may track the wrong rank.
      Draft tracks by NAME where possible; settles: in-game.
- [ ] **6.4 Defiance imp COUNT mechanism.** No player-side stack aura found
      for active Hellfire Imps (302546 is a Hellsmelted Armor component).
      Draft ships without an imp counter; feedback/in-game decides whether
      one exists (e.g. a hidden stack aura) — the display everyone will ask
      for.
- [ ] **6.5 Impcaller state.** With Impcaller taken, does Call: Hellfire Imp
      (804883) stop being known (icon self-removes, as built) or stay on the
      bar transformed in place? Settles: one respec in game.
- [ ] **6.6 Greater Imp presence aura.** `NO PET` alert asks unit="pet" for
      Greater Imp Scaling (520662) by id+name; whether the fork reports an
      absent pet unit as "missing" (vs never firing) is the same unverified
      mechanism Stormbringer/Tinker deferred. Settles: dismiss the pet once.
- [ ] **6.7 Demonfury.** Sidekick lists it in the war kit; the only db id
      (805668) is marked DISABLED. Excluded from every band. If a player
      reports the button live, it becomes a data-change reopen.
- [ ] **6.8 Sever ↔ Brimstone Bludgeon co-existence.** The war rotation text
      names both; the talent text says transform. Built as own-id-gated pair
      in one row (both never known at once, per fork transform semantics).
      If in game a talented character still knows Sever, the row shows 6 and
      rowwidths' 1.2× margin absorbs it — but confirm and re-split.
- [ ] **6.9 Bringer of Fire Demonfire cap.** "Increases your maximum
      Demonfire stacks" (hellfire) — by how much is not stated anywhere
      scraped. Cells stay 6; a 7th stack would simply keep the 6th cell lit
      (last cell is `>=`).
- [ ] **6.10 Pestilence exclusivity.** Assumed one active Pestilence at a
      time ("Changing your active Pestilence…" — Brimstone Battlemaster
      implies a single slot). The `NO PESTILENCE` alert only needs "at least
      one", so it is correct under both readings.
- [ ] **6.11 `prop:`-hedged inventory rows** — the automated role pass's
      hedged rows are listed in the buildlog step note; the in-game sweep
      walks them.
- [ ] **6.12 Greater Imp mana bar** — pet resource display skipped in the
      draft; add if feedback asks.
- [ ] **6.13 "Apocalypse" (630936).** A real 2-min channel tooltip — but it
      costs MANA and sits in the 6309xx block beside the Imp's Burning Slap
      (630930) and Burning Mischief (630933), and every spec-page "mention"
      is a substring hit on Pestilence of Apocalypse. Read as the Greater
      Imp's ability → `ignore`. If a player reports the button, reopen.
- [ ] **6.14 Demonfire ORBS.** Chain Grab's tooltip ("Hooks the nearest
      Demonfire Orb, bringing it to your position") and the blob's core-loop
      line ("Deathfire Orbs") imply generators drop ground orbs that grant
      stacks. Does not change the 6-cell stack display; noted so the pickup
      mechanic is not mistaken for a missing resource.
- [ ] **6.15 NO OATH alert mechanism** — fires on Oath of Defiance's aura
      absent AND the spell known; whether the stance aura is visible to
      UnitAura is unverified (a hidden stance would leave the alert
      permanently on — the Runemaster reminder failure). Built anyway
      because the aura is a castable stance, not a passive; first in-game
      read settles it.
