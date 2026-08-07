---
title: Barbarian pack requirements
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, barbarian, requirements]
sources:
  - "[[class-requirements-template]]"
  - "resources/sidekick-barbarian-brutality.md (snapshot 2026-08-07, blob 2026-08-02)"
  - "resources/sidekick-barbarian-headhunting.md"
  - "resources/sidekick-barbarian-ancestry.md"
  - "resources/exiles-barbarian.json + spell-meta-barbarian.json (db.exil.es)"
  - "db.ascension.gg ?spell=<id>&power"
---

# Barbarian — requirements before building

Class 12, token `BARBARIAN`, specs `brutality`, `headhunting`, `ancestry`.
All three specs run on **Energy**; Ancestry adds the Tankard / Fill Level
gauge on top. Melee class throughout; primary stat Agility on all three specs
(Sidekick, all three pages).

**Spec roles.** `resources/spec-roles.md` has no barbarian rows — nobody has
observed the class in game, so the role stays formally UNKNOWN there.
Sidekick, the only source with a claim, is explicit that every spec is a
damage dealer and none is a healer: Brutality "There is no group-facing heal
or support ability in this kit"; Headhunting dispels "Self only", "Survival
Hunter"-shaped; Ancestry "it's a melee DPS spec wearing support clothing via
auras and a haste cooldown, **not a healer**". The pack is therefore built
with `helpful=False` target bands (your bleeds/debuffs) on every spec and no
healing surface. spec-roles.md is left untouched because its contract is
"observed in game"; the Sidekick claim lives here and in the citations.

---

## −1. Changelog

- [x] changelog scanned (`changelog_watch.py --class barbarian --pages 6`),
      newest barbarian entry: `2026-07-31`
- [x] every entry triaged below
- [x] `--accept` run 2026-08-07 after every entry above was acted on (Axe
      Twirling re-roled to `buff`, Crusher recorded in §2, Born in Blood
      tracker left cap-free)

| Entry (2026-07-31) | Category | Where it lands |
|---|---|---|
| Crush now pauses swing timer instead of restarting | number/behaviour tweak | no WA impact |
| **Crusher added as a switch node with Hail of Hammers** — removes Crush's cast time but −25% damage and removes its stun | §2 talent | Crush keeps its id either way; cd icon reads correctly with and without. db.exil.es's Crusher text (auto-attack reset) is STALE vs this entry |
| Hail of Hammers also increases Crush crit damage | number tweak | none |
| **Born in Blood: 10% ms/stack (up from 5), max 10 stacks (down from 20), base duration 4 s (up from 3)** | buff change | tracker shows live stack count and timer, no hardcoded max — reads correctly |
| Whirling Assault: 500% above 80% HP (from 300%) | number tweak | none |
| Giant Tosser: +100% Headhunter's Spear damage >20 yd, energy refund 50%→15% | number tweak | none |
| Incredibly Strong: increases Maiming Spear duration instead of reducing max range | number tweak | none |
| Drunken Brawler: stacks 5 s (up from 3), 2% dodge/stack | number tweak | none |
| Iron Gut: 30% poison-duration cut + 30% resist chance | number tweak | none |
| Ramhorn Rage now doubles passive health regen | additive effect | no WA change |
| Thick Skull can break Horrify as well as Stuns | behaviour | no WA change |
| **Axe Twirling is now TOGGLEABLE — no cooldown, no fixed duration, −15% damage dealt while on** | §1/§2 rework | changes the tracker: a toggle is an on-me aura, NOT a cooldown icon. Sidekick prose ("Pop Axe Twirling on cooldown", "Lasts 10 seconds") and db.exil.es's tooltip both predate this and are STALE — the changelog wins |

---

## 0. Ability surface — both databases

Inventory seeded from `coa-barbarian-skills.json` (231 skillbook entries,
Sidekick bundle 2026-08-02) unioned with the cooldown audit; ids resolved
through `exiles-barbarian.json` (453 spells, db.exil.es `/class/barbarian/llms.txt`
digest).

- [x] every inventory row with an id swept against db.ascension.gg
      (`tools/crossdb_sweep.py barbarian` → `resources/crossdb-barbarian.json`,
      209/209 = 100%; 204 record, 5 no-record)
- [x] all 5 `no-record` rows re-asked BY NAME and resolved in their Notes
      cells, nothing deleted: **Barbed Spear** — ascension indexes variant
      560976 with the same tooltip (other-id, same ability; official tree
      carries 560881 so the exil.es id ships). **Headhunter's Spear** —
      ascension indexes only its components by name (805837 Regen, 503587
      Reset, 560579 proc); official tree carries 804137. **Maiming Spear** —
      absent from ascension's index entirely, but the official ascension.gg
      talent tree itself carries 804139, which outranks the index.
      **Axe Volley** — no ascension row by id or name; kept because the
      Headhunting L15 passive 570234 ("Transforms Barbaric Whirl into Axe
      Volley") names it on both DBs; in-game check §6. **Wrist Snap** — no
      ascension row; kept because Broken Bones (a `record`) is a passive rider
      on it and exil.es renders the full 15 s interrupt tooltip; §6.
- [x] deprecated/unused/placeholder names filtered (audit_cds drops them;
      `DEPRECATED` names in exiles skipped)

Id corrections made during review (the "db.exil.es links a proc" smell):

| Name | exiles id | Why it is wrong | Resolution |
|---|---|---|---|
| Maximum Carnage | 560932 | rank `Damage` — the whirl's damage component, no cd row | **560933**, verified on BOTH DBs (exil.es: 1 min cd, Skill Brutality, off-GCD; ascension tooltip matches). Exiles entry corrected so the audit derives cd/GCD from the real page |
| Berserker | 561397 | rank `Passive` ("ranged crits grant you Berserker") — not the pressed button | **804141** castable candidate (Headhunting skill on both DBs, 1 min cd on ascension, no cd row on exil.es) — hedged, §6 |
| War Cry | 500674 | rank `Ranged Haste HIdden`, a component | **unresolved** — only other candidate 501133 is a "SLS" stale stub (the Chronomancer decoy shape). Row `ignore`, §6 |
| Cheers! | 801652 | both DBs agree 801652 is the tankard-quaff EMOTE | the damage-redirect ability Sidekick describes has NO record anywhere — prose-only claim. Row `ignore`, §6 |
| Clanlord's Totem | 560529 | rank `Damage`, tooltip is "." on both DBs | no castable row found by name. Row `ignore`, §6 |
| Impaling Spears | 501052 | rank `Test` — Carnage-spender variant of Impaling Spear | not shipping a Test-rank id. Row `ignore`, §6 |

---

## 1. Mandatory buffs

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Enrage cycle: Unbridled Rage (801761, 8 s) / Onslaught (801758, 10 s) / Battle Vigor (801768, 15 s)** | class kit (brutality) | Smash **requires an active Enrage** ("Requires Enraged", skills desc; Sidekick: "Smash is only castable while an enrage is up... never overlap your three Enrage effects") — with no enrage the main filler goes dark | on-me row (active-only, each with timer); Smash desaturates via `spellUsable == 0` when no enrage is up |
| **Born in Blood** (560521, 4 s base, stacks to 10) | ability procs (Furious Berserker, Vengeance For Zul'jin, Thick Skull...) | the class's self-heal engine; Sidekick headhunting: "keep the HoT rolling proactively" | on-me row with stacks + timer |
| **Axe Twirling** (800401, toggle post-2026-07-31) | headhunting | burst/cleave state, −15% damage while on — you must SEE whether it is on | on-me row (active aura) |
| **Ancestral Combat** (801782, "Lasts until triggered 20 times") | ancestry | rotation rule #1: "Keep Ancestral Combat's self-buff rolling" — its procs build Fill Level | on-me row with stacks; missing = press the button (cd icon in main row) |
| **Full Tankard** (805814) / **Empty Tankard** (806055) | ancestry Fill Level system | Ale of The God-King wants a full Tankard, Breath of The North "can only be used after emptying your Tankard" | proc-glow on those two buttons + buff row entries |
| **Fill Level** stacks (92083 passive; aura stack count) | ancestry | the gauge itself — Liquid Courage DR and Ice Cold Bubbles scale per held stack | on-me row stack count (cell-count gauge blocked by unknown max — §6) |
| **Puncture Wounds** bleed on target (Puncture Wound 804143, 6 s) | headhunting passive 805997 | priority #1: "maintain Puncture Wounds uptime" | target band, refresh glow |
| Honored Ancestor present | ancestry pet (Ancestor's Call 804729) | the spec "levels around its permanent Honored Ancestor pet" — no pet, no Ancestral Whirl, no Ale target | reminder band missing-pet alert (§3) |

No weapon-imbue/engraving-style kit exists on this class — the reminder band
carries only the pet alert (ancestry).

---

## 2. Talent-driven rotation changes

From `talents-barbarian.json` (official ascension.gg builder) + the changelog.
No talent found that **replaces** an ability with a different spell id (no
Zenith/Runelord analogue in any source read); the tree modifies in place.

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| Crusher (switch node w/ Hail of Hammers) | 803817 | Crush loses cast time and stun, −25% dmg | Crush becomes instant | none needed — same spell id, cd icon reads correctly both ways |
| Axe Twirling rework (baseline, 2026-07-31) | 800401 | toggle, no cd, no duration, −15% dmg while on | track as aura state, not cooldown | on-me aura icon; NOT in cooldown rows |
| Whirling Death | — | Whirling Advance triggers with no cooldown, 1/30 s | mobility tweak | none — Whirling Advance stays a utility cd icon |
| You Want Axe? | 560564 | discounts casts after a Spear while Enraged, refunds Berserker Axe charges | ramp mechanic | charges already drawn on Berserker Axe (3 charges) |
| Spear Thrower (L30 passive) | — | Throw Weapon can reset Spear cooldowns | Spears come back early | cd icons track real cooldowns, resets show automatically |
| Anger Issues | — | crits cut Maximum Carnage cd | cd icon tracks live cd | none |
| The Finest Ale | — | Ale of The God-King no longer empties Tankard | changes Tankard flow, not the buttons | none — state cues read live auras |
| Thane's Guard / Thane's Grip (ancestry) | — | shield vs dual-2H builds | gear choice, no button change | none |
| Sen'jin's Guidance | — | Javelin Toss access/behaviour (headhunting build) | Javelin Toss may be absent untalented | leaf gates on own spell id — absent spell = absent icon, correct both ways |

Every row reads correctly with and without the talent because cooldown icons
gate on their own spell id and buff icons are active-only. No exact-id
variant registry needed (nothing replaces ids as far as any source says).

---

## 3. Pets

**Yes — Ancestry has a permanent pet.** The "1 pet mention" in the class data
and the "Honored Ancestor" of the ancestry descriptions are the same thing:

- **Honored Ancestor**, summoned by **Ancestor's Call** (804729): "Call an
  Honored Ancestor to aid you in battle **until dismissed** that scales with
  your Agility and attack power. Whenever you use Barbaric Whirl or Whirling
  Advance, your Honored Ancestor mimics it." (db.exil.es tooltip.) Sidekick:
  "summons the **permanent** Honored Ancestor pet that nearly every other
  node in the tree (Ale of The God-King, Drunken Frenzy, The Spins, Might of
  Utgarde) exists to empower." `Dismiss Ancestor` / `Ancestor's Recall`
  (rez) exist alongside.
- Pet abilities the player presses: none — Ancestral Whirl is triggered by
  the PLAYER's Keg Smash / Ancestral Combat (The Spins, Might of Utgarde).
  The Honored Ancestor Visual (race) spells are cosmetics, `ignore`.
- Buffs: Ale of The God-King (805780) empowers the pet for 20 s — tracked as
  the player-facing cd icon + running buff, not a pet aura.
- Resource: none named in any source.
- **Presence gates the rotation** → missing-pet alert in the reminder band,
  same shape as the missing-engraving alert: show when no pet, ancestry only.

| Pet | Summoned by | Duration | Track | Where |
|---|---|---|---|---|
| Honored Ancestor | Ancestor's Call 804729 | permanent until dismissed | presence only | `NO ANCESTOR` reminder alert (ancestry) |

Brutality and Headhunting: **no pets**.

---

## 4. Primary damage source and main rows

All three specs: **Energy** (`power`/bar). Ancestry adds the Tankard gauge —
see Resource column.

| Spec | Primary damage | Main row, in press order (cited) | Icons | Resource / segments |
|---|---|---|---|---|
| Brutality | Enrage-empowered Smash filler loop; Unbridled Rage burst windows | Smash · Ancestral Strike · Brutal Swing · Barbaric Whirl · Crush · Decapitate | 6 | energy bar |
| Headhunting | Spear crits → Puncture Wounds bleeds; Berserker Axe while Enraged | Barbed Spear · Throw Weapon · Berserker Axe · Gutspiller · Impaling Spear | 5 | energy bar |
| Ancestry | Keg Smash + Ancestral Combat Frost procs, Tankard spenders | Ancestral Combat · Keg Smash · Ale of The God-King · Breath of The North | 4 | energy bar (+ Tankard state via buffs/glows, §6) |

Press-order sources: Brutality — Sidekick rotation "Smash and Ancestral
Strike as your Energy fillers → Brutal Swing when 2+ targets are clumped →
[Barbaric Whirl on any pull of 3+] → Crush to stun → Decapitate to execute
below 35%". Headhunting — the explicit priority list "maintain Puncture
Wounds (Spear crits) > … > Barbed Spear > Berserker during Enrage > filler
Throw Weapon/Berserker Axe". Ancestry — the numbered rotation "1) Keep
Ancestral Combat rolling 2) Keg Smash on cooldown 3) Ale of the God-King the
instant your Tankard is full 4) Breath of the North whenever the Tankard is
empty".

Narrowest main row = Ancestry (4 icons) → `CD_PER_ROW` derived from it at
build time and verified with `tools/rowwidths.py`.

Notable off-GCD main-row entry: **Brutal Swing** (gcd 0 in spell-meta,
"your off-global dump between specials" — Sidekick) → `use_showgcd` off via
the audit.

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Enrage dropped (brutality) | Smash uncastable — filler loop dies | Smash desaturates (`spellUsable == 0`, IsUsableSpell reflects the Requires-Enraged clause) + enrage buffs visible with timers in on-me row | tests/run.py check 9 (desaturate present); enrage icons are plain aura leaves — seen only in game, §6 |
| Unbridled Rage window (brutality/headhunting) | main burst window lost | cd icon escalation tiers (timer 20 s, glow 10 s, urgent 5 s), ANDed with `onCooldown == 1` | check 9 (no bare expirationTime) |
| Puncture Wounds uptime (headhunting) | priority #1 damage stream stops | target-band bleed bar with refresh glow at ≤2 s | dot_bars refresh mechanism, same shape verified on Chronomancer/Pyromancer packs |
| Ale of The God-King at full Tankard | "don't let a fill go stale" — wasted fill | PROC_GLOW: Ale glows while `Full Tankard` (805814) aura up | aura-trigger glow — same PROC_GLOW shape as Chronomancer Continuum; aura ids unverified in game, §6 |
| Breath of The North at empty Tankard | spender window missed | PROC_GLOW: Breath glows while `Empty Tankard` (806055) aura up | same; §6 |
| Ancestral Combat dropped (ancestry) | Fill Level generation stops | main-row cd icon reads ready + its buff absent from on-me row | cd icon; buff row active-only |
| Born in Blood rolling | self-heal engine stalls | on-me icon with stacks + timer | aura leaf; in-game §6 |
| Overcapped Energy | wasted regen | NOT built — no energy-overcap cue in v1; Brutal Swing sits in the main row as the documented dump | deferred, §6 |
| Defiance forgotten at low HP | death | defensive cd row with escalation | check 9/10 |
| Honored Ancestor missing (ancestry) | whole tree unpowered | `NO ANCESTOR` reminder alert | §6 — needs in-game confirmation of the detection trigger |

## 6. Open questions

- [ ] **Fill Level max stacks** — UNKNOWN. Tooltip says "1 stack every 2 sec"
      with no cap; no source states one. Settled by: in-game Fill Level aura
      at cap, or a `/rmdump` diff. Until then the pack draws NO fixed-cell
      Tankard gauge; it shows the stack count and the Full/Empty state auras.
- [ ] **Full Tankard 805814 / Empty Tankard 806055 as player auras** —
      plausible (both resolve on both DBs, durations −1 / 5 s) but UNVERIFIED
      in game; if they never appear, the Ale/Breath glows silently never fire.
      Settled by: one in-game look at the buff frame with a full/empty Tankard.
- [ ] **Ancestor presence detection** — the alert triggers on the pet-summon
      aura surface; whether a pet aura or `UnitExists("pet")`-style state is
      exposed for it is unverified. Settled by: in-game import.
- [ ] **War Cry / Cheers! / Clanlord's Totem — cited by Sidekick's ancestry
      rotation, unbuildable**: War Cry's two candidate ids are a hidden
      component (500674) and an "SLS" stale stub (501133); Cheers! resolves
      only to the quaff emote on both DBs; Clanlord's Totem only to a "."
      Damage component. All three rows `ignore`. Settled by: in-game
      spellbook/tooltips.
- [ ] **Berserker castable id** — built on 804141 ("ranged abilities have a
      20% chance to unleash Berserker Throw", 1 min cd on ascension, no cd row
      on exil.es); exiles' 561397 is the crit-granted passive, and the
      skillbook text ("rapidly throw axes... Requires Enraged") matches
      neither exactly — a rework seam. Settled by tooltip.
- [ ] **Axe Volley + Wrist Snap** — no db.ascension.gg record by id or name;
      kept on transform-passive/rider corroboration (see §0). Settled by
      in-game sighting.
- [ ] **Headbutt / Ancestral Strike spec attribution** — Sidekick's coaKits
      files both under single specs (ancestry / ancestry+brutality) while its
      own Brutality rotation text uses both. Rows set to the wider reading
      (see Notes cells); a wrong-narrow hides an icon, a wrong-wide costs a
      dead icon on one spec. Settled by: in-game spellbook per spec.
- [ ] **Energy-overcap cue** — "never overcap Energy" is rule #1 on two
      specs; v1 ships no overcap warning (power-threshold glow on the energy
      bar is buildable later). Deferred by choice.
- [ ] Hedged inventory rows from the bulk role pass (reasoning kept in every
      Notes cell; no human read them one at a time): `Break`,
      `Barbaric Strike`, `Savage Strike`, `Rancor`, `Hullbreaker`,
      `Disembowel`, `Javelin Toss`, `Killing Spree`, `Hate` (zero Sidekick
      mentions), plus the spec-attribution widenings on `Ancestral Strike`,
      `Whirling Advance` and `Smash` — check against the game before trusting
      the first build's placement.
