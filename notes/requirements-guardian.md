---
title: Guardian pack requirements
date: 2026-08-08
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, guardian, requirements]
sources:
  - "[[class-requirements-template]]"
  - "resources/sidekick-guardian-vanguard.md (page snapshot 2026-08-08, blob 2026-08-02)"
  - "resources/sidekick-guardian-inspiration.md"
  - "resources/sidekick-guardian-gladiator.md"
  - "resources/exiles-guardian.json + spell-meta-guardian.json (db.exil.es)"
  - "db.ascension.gg ?spell=<id>&power"
---

# Guardian — requirements before building

Class 18, token `GUARDIAN`, specs `vanguard`, `inspiration`, `gladiator`.
All three specs run on **Energy** (Sidekick "Resource: Energy" on every page);
primary stat Strength on all three. Sword-and-board melee class throughout —
even the support spec "is literally standing in melee with a shield".

**Spec roles** (`resources/spec-roles.md`, Sidekick-cited, pending in-game):
vanguard **tank** ("Strong dungeon tank — AoE pulls and threat", Prot Warrior
analogue, taunts + High Threat abilities + defense-to-crit-immunity stat
priority); inspiration **damage** (Augmentation-Evoker-shaped support buffer —
"a buff and mitigation unit wearing a shield, **not a direct-heal caster**",
"No hard single-target heal"); gladiator **damage** (DPS-Prot hybrid).
No spec heals, so every target band is `helpful=False` (your debuffs/bleeds)
and no healing surface exists to go missing.

**The absorb expectation is falsified by the data.** The batch brief predicted
Guardian as the absorb-heaviest class (38 mentions). Measured: **zero**
"absorb" mentions in `coa-guardian-skills.json` and zero across all three spec
pages, against ~90 "block" mentions. Guardian's defensive economy is **BLOCK**
— block chance, block value, on-block procs (Reprisal, Retaliation, Fine
Plating, Vanguard's Shield, Veteran of the Third War, Recuperation). The
"maintained own-bubbles" §4 question dissolves: there are no bubbles. The
block economy renders as: Raise Shield/Brace/Counter Stance in the defensive
row, the on-block stack auras in the on-me row, and Reprisal's
only-after-a-block requirement carried by `spellUsable` desaturation.

---

## −1. Changelog

- [x] changelog scanned (`changelog_watch.py --class guardian --pages 6`),
      newest guardian entries: `2026-08-07`
- [x] every entry triaged below (60 entries over 2026-07-31 + 2026-08-07)
- [x] `--accept` run 2026-08-08 after triage

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| **Final Verdict usable at 35% health, up from 20%** | 07-31 | behaviour | execute slot in gladiator main row; the pack draws no HP-threshold cue in v0.1 (§6) — the button's own `spellUsable` desaturate reads the range live either way |
| **Supremacy talent now allows the use of Reprisal as well as refreshing a charge** | 07-31 | §2 talent | Reprisal usability gains a second path beyond blocking; `spellUsable` desaturate reads it live, charges drawn on the icon |
| **Reprisal GCD 1.5s → 1.0s** | 07-31 | GCD data | on-GCD either way; spell-meta already carries gcd_ms 1000 (fresh) |
| Reprisal damage +~30% all ranks | 07-31 | number tweak | none |
| Legionnaire / Crashing Force Reprisal amps | 07-31 | number tweak | none |
| Spear Throw damage/AP scaling up | 07-31 | number tweak | none |
| Pulverize / Ram AP scaling up | 07-31 | number tweak | none |
| Broad Sweep 90% WD all ranks, target cap 4→8, flat damage ×2 | 07-31 | number tweak | none (no icon change) |
| Centurion Strike weapon damage up all ranks | 08-07 | number tweak | none |
| Broad Sweep / Pulverize / Ram flat damage up all ranks | 08-07 | number tweak | none |
| Tactical Combat block value up | 08-07 | number tweak | none |
| Experienced Combatant 20%→40% Str-to-AP, Shield Training 10%→20% Str-to-block | 08-07 | number tweak | none |

The Sidekick **blob** snapshot (2026-08-02) predates the 08-07 entries; all
08-07 entries are number tweaks, so nothing structural rides on the gap. The
three **page** scrapes were taken 2026-08-08, after both changelog dates.

---

## 0. Ability surface — both databases

Inventory seeded from `coa-guardian-skills.json` (220 skillbook entries,
Sidekick bundle 2026-08-02) unioned with the cooldown audit; ids resolved
through `exiles-guardian.json` (391 spells). 223 rows after 3 hand-added
aura-only rows (High Guard, Peril, Vanguard's Shield — check 13).

- [x] every inventory row with an id swept against db.ascension.gg
      (`tools/crossdb_sweep.py guardian` → `resources/crossdb-guardian.json`,
      196/196 = 100%; 195 record, 1 no-record)
- [x] the 1 `no-record` re-asked BY NAME and resolved, nothing deleted:
      **Linebreaker** — digest linked 503114, a stale line-hit+slow version
      with an empty ascension record; BOTH DBs carry **806220** with the live
      absorb-destroyer text matching the Sidekick kit (1 min cd, 30% energy).
      Both tooltips read; inventory, cooldown audit and crossdb corrected.
- [x] deprecated/unused/placeholder filtered (Into The Fray rank DEPRECATED →
      ignore; Chainwhip Passive SLS + Press the Attack 803421 are "SLS" stale
      stubs, the Chronomancer decoy shape; Song of Steel TO REWORK 704532 is
      the pre-rework channel kept beside the live 704540)

Id corrections made during review (the "db.exil.es links a component" smell):

| Name | digest id | Why it is wrong | Resolution |
|---|---|---|---|
| Press the Attack | 704157 | rank `Damage`, L24 — the damage component | **801219** (rank null, L58, full AE-tree tooltip verbatim on BOTH DBs) |
| Reflective Shield | 300926 | rank `Passive`, dur −1 — the grantor | **355779** (rank null, L20, "reflect the next harmful spell… within 3 sec" on BOTH DBs; tree icon matches) |
| Counter Stance | 501535 | rank `Heal` — smells like a component | kept: 501535 answers on BOTH DBs with the full castable text ("You are granted 8 charges… Requires Shields"); rank still blocks own-id gating so it stays duplicated |

Audit gap closed by hand: **Ram** (802284) is the only sub-4-character name in
the digest and `audit_cds.py`'s `len(n) < 4` candidate filter drops it — a
main-row ability on all three specs. Page scraped manually with the same
parser (10 sec cooldown, GCD 1.5 sec) and appended to
`cooldown-abilities-guardian.json`.

Prose-only names (unbuildable, recorded in `aliases-guardian.json` as null):
**Hero's Serenade** (1 blob mention, no row in either DB), **Shield
Formation** (2 blob mentions, reads like shorthand for the Formations family).
**Challenging Cry** — 4 blob mentions and the vanguard prose says "use
Challenging Cry / Shield Challenge to re-taunt", but NO db.exil.es row exists
by that name; Shield Challenge (500257) is the taunt both DBs carry → §6.

---

## 1. Mandatory buffs

| Buff | Source (class/talent/ability) | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Shield Reinforcements** — Spiked 653131 (vanguard, L4) / Weighted 653277 + Jagged 653279 (gladiator, L12/L40) / Magic 653280 + Poised 653278 (inspiration, L22/L30) | class kit, 1-hour shield imbues | Guardian's engraving analogue: a dropped imbue is quiet throughput/mitigation loss for a whole hour | long-term band per spec + per-spec `NO REINFORCEMENT` alert (fires only when none of that spec's imbues is up) |
| **Raise Shield** (500168, 25s cd off-GCD) | class kit | THE block window; Reprisal, Resilient, Knight's Conviction all key off it; three talents reset it (King's Guard, Refuse To Die, Deflector) | defensive cd icon with escalation + running buff in on-me row |
| **Formations/Poses** — Tower 800317, Line 803130, Offensive 802282, Defensive 802293, Assault 803417 | class kit stances (dur −1) | Footman's Calling (−10% damage taken + threat) only while Tower/Line is active — a tank in no formation is quietly squishier | long-term band (active-only, per spec) |
| **Glory** (stacks to 3, built by Ram) | gladiator L10 passive | 3 stacks empower the next Ram — the spec's burst engine | on-me row stack count (by name; 92106 is the teaching spec passive) |
| **Favor** (stacks to 20, crits/killing blows) | gladiator L50 passive | at 20, next auto deals +500% WD; Heroism keys free spenders off it | on-me row stack count (by name; no id in digest — §6) |
| **Tempo** (stacks to 3, built by Ballads) | inspiration L10 passive | 3rd stack auto-consumes into Sound of War — the spec's rhythm | on-me row stack count (by name) |
| **High Guard** (707621) | vanguard L50 passive, granted by Raise Shield/Advance/Battle Rush | "your next Heavy Blow triggers no cooldown" — a free press you should not sit on | PROC_GLOW on Heavy Blow + on-me row |
| **Vanguard's Shield** (804383, 10 stacks) | vanguard talent | stacking magic-DR that spells strip — the tank's magic mitigation state | on-me row stack count |
| **Fine Plating** (503797) | vanguard talent | on-block stacking physical DR | on-me row stack count |
| **Spear Throw** healing cut on target | gladiator | "keep Spear Throw's healing-reduction debuff up" — anti-heal identity | target band with refresh read |
| **Standard of Valiance + Banners** (500274; 500261/500259) | inspiration | "keep the Standard and Banners refreshed" — the support loop | utility cd icons; placed-standard uptime is NOT drawn (ground object, no verified self-aura — §6) |
| **Counter Stance** charges (501535) | class kit | 8 parry charges; expending one heals — worth seeing it is up | defensive cd icon + on-me row |

No missing-buff alert beyond `NO REINFORCEMENT`: enrage-style hard gates do
not exist here, and an alert for a stance out of combat would be permanently
on screen (the Runemaster reminder failure).

---

## 2. Talent-driven rotation changes

From `talents-guardian.json` (official ascension.gg builder), the tree scrapes
and the changelog. Three genuine **transforms** (this fork resolves no spell
overrides — the pack tracks the REPLACEMENT id with a native `["Spell Known"]`
trigger, numeric):

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| **Inspiring Leader** (inspiration) | 505344 | "transforms your Pulverize and your Broad Sweep into **Ballads**" | the whole inspiration loop becomes Ballad-driven | inspiration main row carries the Ballads (801776/801772); Pulverize/Broad Sweep stay all-specs rows so an untalented inspiration still reads. Ballads are ranked ids → never own-id-gated, stay duplicated |
| **Press the Attack!** | 301216 | passive: "Transforms Standard of Valiance into Press the Attack" (801219) | SoV button becomes a channel | both displays ship; Press the Attack gates on Spell Known 801219 (numeric), SoV stays — whichever the character owns is the one that loads |
| **Shield Tosser** (vanguard) | 500591 | "Every 3rd Broad Sweep transforms Pulverize into **Shield Toss** (500461)" | a mid-combat cycling transform, not a talent-permanent one | UNKNOWN mechanism on this fork (§6) — v0.1 ships Pulverize's icon untouched rather than betting the main row on an unverified surface |
| **Supremacy** (gladiator) | 504140 | changelog 07-31: "now allows the use of Reprisal as well as refreshing a charge" | Reprisal usable without a block | no structural change: `spellUsable` desaturate reads usability live, charge count on the icon |
| High Guard (vanguard) | 707621 | next Heavy Blow free of cooldown | free press windows | PROC_GLOW on Heavy Blow |
| Guardbreaker / King's Guard / Refuse To Die / Wreck Formation / Plate Buster | — | cd resets (Ram, Raise Shield, Hammer of the Law, Challenging Cry/Hold the Line) | cooldowns come back early | cd icons track live cooldowns — resets show automatically |
| Champion (gladiator) | 300972 | Centurion Strike extends Raise Shield | uptime linkage | none — both icons read live state |
| Heroism (gladiator) | 705323 | 3 Glory / 20 Favor → next 2 Pulverizes or Broad Sweeps free | burst windows | free-cast aura name unverified (§6) — stack counts shipped, glow deferred |
| Valiant Knight (vanguard choice) | — | melee crits → next Pulverize free +25% | proc window | proc aura name unverified (§6) |
| Banner Lord (inspiration) | 800322 | multiple Banners at once for +cost | changes exclusivity, not buttons | none |
| Shieldlord's Strength (vanguard) | — | 2H maces with shield | gear choice | none |
| Crusher-style id replacement | — | **none found** — no talent in any source replaces a rotation ability with a different id outside the transforms above | — | — |

Every cooldown icon gates on its own spell id and buff icons are active-only,
so each row reads correctly with and without its talent.

---

## 3. Pets

**None.** Zero pet mentions in `coa-guardian-skills.json` (0 hits), zero in
all three Sidekick spec pages, no petLines entry in the coaKits bundle, and no
summon anywhere in the kit. Answered explicitly: no pet section, no pet
alert, nothing binned to `ignore` on pet grounds.

---

## 4. Primary damage source and main rows

All three specs: **Energy** (`power_trigger(power_type=3)`, barbarian
precedent — the first energy class; still unverified in game there, §6).
No segmented second resource on any spec: Glory (3) and Favor (20) are
proc-stack states consumed automatically, not spent resources — the Tankard
precedent says stack counts in the on-me row, not an invented gauge. Energy
is the only bar.

| Spec | Primary damage | Main row, in press order (cited) | Icons | Resource |
|---|---|---|---|---|
| Vanguard | block-fueled shield strikes; Heavy Blow/Pulverize threat loop | Heavy Blow · Pulverize · Ram · Hammer of Kings | 4 | energy bar |
| Inspiration | Ballad loop + Sound of War procs | Ram · Ballad of the Conqueror · Ballad of the Dragonslayer · Broad Sweep | 4 | energy bar |
| Gladiator | Ram/Pulverize priority swings, Glory/Favor burst | Ram · Pulverize · Reprisal · Centurion Strike · Broad Sweep · Spear Throw · Final Verdict | 7 | energy bar |

Press-order sources (manual citations `sidekick-page-guardian-*-2026-08-08`):
vanguard "Heavy Blow on cooldown → Pulverize as your Energy-dump filler → Ram
whenever Energy allows", opener "Advance in → Hammer of Kings on the pull";
inspiration "Ram on cooldown > cast Ballads on cooldown > Broad Sweep as your
energy-dump filler"; gladiator "Spend Ram and Pulverize on cooldown … Fill
remaining energy with Reprisal and Centurion Strike … Broad Sweep as a cheap
opening builder … Spear Throw when you need the healing-reduction debuff …
Save Final Verdict to finish an enemy below the execute threshold".

Spec widenings (coaKits wrong-narrow, reasoning in Notes cells): Pulverize
and Broad Sweep → all (vanguard presses both, inspiration's transform base);
Reprisal → vanguard,gladiator (the gladiator loop spends it).

Narrowest main row = 4 icons (vanguard, inspiration) → `CD_PER_ROW`:
`28w − 2 ≤ 1.2 × 182` gives w ≤ 7.9 → **7**, verified with
`tools/rowwidths.py` at build time.

Charges: **Reprisal 2** ("2 Charges, 6 sec recharge", both DBs). Inspiration's
"Ram and Ballad run on charge bars" prose has no charge count in any DB row →
§6, no charge number invented.

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Reinforcement imbue dropped | an hour of quiet mitigation/throughput loss | `NO REINFORCEMENT` alert (per spec, fires when none of the spec's imbues is up) + long-term band | alert is aura-absence over ids on both DBs; unverified as player auras in game — §6 |
| Raise Shield window wasted | block procs (Reprisal, Resilient, Fine Plating…) all idle | cd icon escalation (timer 20s, glow 10s, urgent 5s) ANDed with `onCooldown == 1` + running-buff icon | tests/run.py check 9 (no bare expirationTime), check 10 (off-GCD: no global sweep) |
| Reprisal charges sitting | free counterattack + Energy refund lost | charge count on icon; desaturates via `spellUsable == 0` when no block/Supremacy window | check 9 (desaturate present); usability semantics in game — §6 |
| High Guard unspent (vanguard) | free Heavy Blow expires | PROC_GLOW on Heavy Blow keyed to High Guard 707621 | aura-trigger glow, same shape as Chronomancer Continuum; id from talents payload, unverified — §6 |
| Glory at 3 / Favor at 20 unspent (gladiator) | empowered Ram / bonus auto window wasted | stack counts in on-me row | plain aura leaves; seen only in game — §6 (no threshold glow in v0.1) |
| Spear Throw debuff dropped (gladiator) | target heals through your kill window | target band bar with refresh glow | dot_bars refresh mechanism, verified shape on prior packs |
| Standard/Banner uptime (inspiration) | party buffs idle | utility cd icons with escalation | check 9/10; placed-standard uptime not drawn (§6) |
| Song of Battle / Champion's Presence windows | burst/CC windows lost | offensive cd icons with escalation | check 9/10 |
| Defensives forgotten under fire | death | defensive row with escalation; Brace/Bastion off-GCD flagged from the audit | check 9/10 |
| Missed interrupt (Shield of Denial) | caster add free-casts | utility cd icon, pinned last per layout standard | check 9/10 |

## 6. Open questions

- [ ] **Energy power type in game** — `power_type=3` is the 3.3.5 client
      convention (barbarian precedent), still unverified in any CoA import.
      Settled by: one in-game look at any energy class pack.
- [ ] **Reinforcement auras as player buffs** — all five ids resolve on both
      DBs, durations 1 hr; whether UnitAura exposes them (weapon-imbue-style
      enchants would need the enchant trigger instead) is UNKNOWN — settled
      by one in-game look at the buff frame with an imbue up. The alert and
      the long-term band both ride on it.
- [ ] **High Guard aura id 707621** — from the talents payload, not a DB
      tooltip. If wrong, the Heavy Blow glow silently never fires. Settled by
      tooltip.
- [ ] **Favor aura** — no id in any source (the L50 passive text is
      truncated upstream). Tracked by name; settled by in-game buff frame.
- [ ] **Warmaster** — effect text truncated in every source ("chance to grant
      you Warmaster" … granting what?). Tracked by name in the on-me row;
      settled by tooltip.
- [ ] **Heroism / Valiant Knight free-cast aura names** — the "next N free"
      windows are real claims with no aura id anywhere. No glow shipped;
      settled by /probe-style diff or tooltip.
- [ ] **Shield Tosser mechanism** — "every 3rd Broad Sweep transforms
      Pulverize into Shield Toss (500461)": whether the fork grants/removes
      the spell mid-combat (Spell Known would track it) or swaps the button
      server-side is UNKNOWN. v0.1 ships Pulverize untouched; settled in game.
- [ ] **Challenging Cry** — cited by vanguard prose (4 blob mentions) as a
      taunt beside Shield Challenge, but NO db.exil.es row by that name and
      no ascension hit. Not shipped; settled by in-game spellbook.
- [ ] **Ballad / Ram charge counts (inspiration)** — "run on charge bars"
      (Sidekick prose); no charge count in any DB row. No charge number
      drawn; settled by tooltip.
- [ ] **Placed-Standard uptime surface** — a Standard is a ground object;
      whether the caster carries a trackable self-aura while one is planted
      is UNKNOWN. Not drawn; settled by /probe diff.
- [ ] **Motivation / Inspiration economy** — `Motivation` riders ("Motivation:
      Grants Vanguard's Might") and ally-side `Inspiration` (803958, with
      803967 Decay) are a cross-spec economy no source explains end-to-end.
      The granted auras the pack draws (Vanguard's Might, Knight's Valor) are
      tracked by name; the economy itself is not modelled. Settled by
      research round 2 or in-game reads.
- [ ] **Final Verdict 35% execute cue** — no HP-threshold glow in v0.1; the
      button's own usability (execute range) desaturates it live. A
      target-HP condition is buildable later if feedback asks.
- [ ] Hedged inventory rows from the bulk role pass (reasoning in every Notes
      cell; no human read them one at a time): the spec widenings on
      `Pulverize`, `Broad Sweep`, `Reprisal`; `Song of Battle` (no exil.es cd
      row — possible wrong id); `Counter Stance` (rank Heal); `Bastion Slam`
      vs main-row membership; `Assume Peak Posture` kept as a utility button;
      `Bark Orders`/`Shield Unit`/`Honorable Demeanor` binned ignore. Check
      against the game before trusting the first build's placement.
