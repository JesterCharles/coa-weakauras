---
title: Sun Cleric pack requirements
date: 2026-08-08
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, sun-cleric, requirements]
sources:
  - "[[class-requirements-template]]"
  - "resources/sidekick-sun-cleric-blessings.md (scraped 2026-08-07)"
  - "resources/sidekick-sun-cleric-piety.md (scraped 2026-08-07)"
  - "resources/sidekick-sun-cleric-seraphim.md (scraped 2026-08-07)"
  - "resources/sidekick-sun-cleric-valkyrie.md (scraped 2026-08-07)"
  - "resources/coa-sun-cleric-skills.json (sidekick-data.js snapshot 2026-08-02)"
  - "resources/exiles-sun-cleric.json (db.exil.es llms.txt digest, 2026-08-07)"
---

# Sun Cleric — class pack requirements

Class 27, load token `SUNCLERIC`. Four specs: **Blessings** (single-ally
"bodyguard" healer), **Piety** (ranged Holy/Fire caster DPS), **Seraphim**
(block tank), **Valkyrie** (melee DPS). Roles are Sidekick-cited, pending
in-game — see §4 and `resources/spec-roles.md`.

The class-wide engine: **Vows** feed **Solar Power** (a stacking aura,
0–20), and at 20 stacks you may unleash **Dawn**, the window in which your
next casts trigger your Vow's Fulfillment effect. Every spec plays around
that loop with different generators.

---

## −1. Changelog — run FIRST

- [x] changelog scanned 2026-08-07 (`changelog_watch.py --class sun-cleric
      --pages 6`), newest sun-cleric entry: `2026-07-31`
- [x] every mechanical entry triaged below
- [x] `--accept` only after the entries are acted on

12 new entries, all dated 2026/07/31. Triage:

| Entry | Category | Where it lands |
|---|---|---|
| All Gavel Spells 100% weapon damage (from 80%) | number tweak | ignore |
| Ancient Rites now also grants 150/300/450% int as mana | number tweak (still a passive) | ignore |
| Luminary Mendicant now also silences via Horusath Blast | passive rider tweak | ignore (still a passive) |
| Adjudicator: Justicar's Wrath +50% vs single target | number tweak | ignore |
| **A new capstone has been added to Valkyrie: Sunstorm** | **new spell** | §0/§2 — resolves in db.exil.es as 760379 (2-min cd, casts Justice every 1s for 6s); absent from the Sidekick blob; inventory row added, valkyrie offense row |
| Justice 50% weapon damage (from 40%) | number tweak | ignore |
| **Radiant Halberds effect merged with Champion's Arrival** | talent merge | no WA change — Champion's Arrival is a passive rider; Radiant Halberds never had an inventory row |
| Sun Stride now also frees you from slows and roots | behaviour tweak | noted in the utility row cell; no display change |
| **Adjudication renamed to Herald of Dawn** (to not confuse with Seraphim's Adjudicator) | **rename** | §1 — inventory row renamed, id 804630 from db.exil.es; PROC_GLOW on Dawnsear keyed to the new name; alias row parked so a blob refresh does not re-seed the old name |
| Adjudication rank-1-Dawnsear bug fix | behaviour fix | ignore |
| Vows now have a reduced global cooldown | number tweak | ignore |
| **Vows are now on the stance bar** | mechanics: the Vow family is formally the class stance | §1 — confirms the Vow family as the long-term "stance" row + the class-wide NO VOW alert |

Snapshot staleness: `sidekick-data.js` mtime 2026-08-02, republish check
2026-08-07 returned "unchanged" — the blob **post-dates** the newest
sun-cleric changelog entry (2026-07-31) but demonstrably lags it in content
(it still says "Adjudication", and carries neither Sunstorm nor Vow of
Benediction). Where blob and changelog disagree, the changelog won: rename
applied, both missing spells added from the db.exil.es digest (scraped
2026-08-07). The four spec pages were scraped live on 2026-08-07.

---

## 0. Ability surface — both databases

Inventory seeded from `coa-sun-cleric-skills.json` (245 skillbook rows)
enriched by `cooldown-abilities-sun-cleric.json` (40 rows, 22 off-GCD,
unresolved empty) + `exiles-sun-cleric.json` (478 spells, 230 multi-rank) +
`spell-meta-sun-cleric.json` (478 rows). 252 inventory rows after the
changelog additions.

- [x] every inventory row with an id asked of BOTH databases
      (`crossdb_sweep.py sun-cleric` — 231/231, buildlog `crossdb` step)
- [x] `no-record` rows resolved: exactly one, **Sun Ray 500145** — re-asked
      BY NAME per protocol → other-id (db.ascension knows Sun Ray under
      504764/572759/802943 "(Dawn)"/802944/803238/804944). Both DBs have the
      ability; which id is the castable is unsettled (§6) and nothing ships
      on it while its role is `ignore` (it is the Burning Heat transform face
      of Sunflare — the Lithic Lance shape). Verdict written into the row.
- [x] deprecated/unused/placeholder names filtered (none reached the
      inventory; exiles surplus stays in `## Candidates`)

---

## 1. Mandatory buffs

**From the class kit:**

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Vows** (Grace / Light — blessings; Radiance — piety; Benediction — seraphim; Dawn / Eclipse / Valkyr — valkyrie) | class stance family ("Only 1 Vow can be active at a time"; changelog 07/31: "Vows are now on the stance bar") | every spec's Solar Power generation hangs on a Vow: blessings "Keep a Vow active so Solar Power builds"; seraphim "get a Vow rolling so Dawnguard's block stacks start"; valkyrie pre-pull names "whichever set-and-forget Vow fits the pull". No Vow = no Solar Power = no Dawn windows | long-term band per spec + class-wide **NO VOW** alert (the NO BOON shape) |
| **Dawn** (the fulfillment window) | unleashed at 20 Solar Power (Solar Power 500149 tooltip: "You may unleash Dawn at 20 stacks") | the payoff state every page plays around ("time your Dawn window before a heavy-damage stretch"; "auto-crits Horusath Blast and unlocks Sunslam") | on-me row; readiness is the Solar Power bar being full |
| **Devotions** (Grace / Dawn / Emperors / Radiance + Greater) | 30-min ally buffs, "one Devotion per Sun Cleric" | the class blessing — absence is quiet group throughput loss, but it sits on the ALLY, so absence is not cheaply detectable (the Primalist Instinct precedent) | long-term band of the owning spec; no alert (§6) |
| **Holy Form** (blessings/piety) | form until cancelled | "run Holy Form on threat-safe trash for cheaper, better self-healing" | long-term band |

**From talents / spec passives:**

| Buff | Spec | Why | Where |
|---|---|---|---|
| **Sunrise / Sunset** (500477 / 500511) | piety | the school lock-in ("knowing whether you're locked into Sunrise or Sunset" is the difficulty text's first item) | on-me row |
| **Twin Flames / Sun Power** (807061 / 807077) | piety | Duality of Light's stay-committed payoff stacks | on-me row |
| **Scorch Marks / Spears of Glory / Learning Light / Blinding Light** | piety | cast-flow procs (instant/faster casts) | on-me row |
| **Herald of Dawn** (804630, renamed from Adjudication 07/31) | piety | "Casting Rapture → next Dawnsear strikes twice + Solar Flare" | PROC_GLOW → Dawnsear |
| **Burning Heat** transform | piety | next Sunflare becomes Sun Ray (Horusath Blast guarantees it) | PROC_GLOW → Sunflare (granted-aura name §6) |
| **Angelic Presence** | seraphim | avoidance proc; "Prioritize Illumination while Angelic Presence is active" | on-me row |
| **Sunsworn** (stacks) / **Bastion of Hope** / **Gleaming Armor** / **Celestial Protection** / **The Chosen** / **Chosen of the Light** | seraphim | the tank's proc-driven defense layer — absorbs, DR windows, mana | on-me row |
| **Lord Commander** (block → Daybreak proc) | seraphim | free reactive heal | PROC_GLOW → Daybreak (granted-aura name §6) |
| **Sunwalker** (stacks) | blessings, seraphim | stacking next-Shine discount | on-me row + PROC_GLOW → Shine |
| **Cultivate Divinity** / **Vitality** / **Solar Invigoration** | blessings | crit-heal payoff procs and the ally-amp window | on-me row |
| **Ancient Etchings** (stacks) | piety | stacking Horusath Blast cast-time cut | on-me row |

**From abilities:** running cooldown buffs (Paragon, Champion of the Sun,
Transgression, Seraphic Bulwark, Blessing of Triumph on the ally, Dawnfall,
Solar Concord, Sunstorm …) render via cd_buffs / the on-me row so "active"
reads differently from "unavailable".

---

## 2. Talent-driven rotation changes

This fork resolves NO spell overrides. Findings from the four trees + spec
passives:

| Talent | What changes | Rotation impact | WA adaptation |
|---|---|---|---|
| **Valkyrie – Level 15 Passive** (681084) | "Transforms your Vow of Radiance into Vow of the Valkyr" | valkyrie's Solar Power comes from autos, not casts | the Vow long-term rows are per-spec already (Radiance is piety's row, Valkyr is valkyrie's), and both are active-only aura displays — a transformed-away Vow simply never lights. No Spell Known swap needed: no shared button changes id |
| **Burning Heat** (piety) | proc: "next Sunflare into Sun Ray" (Horusath Blast guarantees) | fish for the Sun Ray window | temporary proc transform, NOT a permanent swap → glow Sunflare off the proc aura (the Lithic Lance shape). Sun Ray holds no slot; its castable id is unsettled anyway (§0) |
| **Herald of Dawn** (piety, renamed 07/31) | Rapture → next Dawnsear strikes twice | press Dawnsear now | PROC_GLOW → Dawnsear on aura 804630/name |
| **Sunstorm** (valkyrie capstone, NEW 07/31) | 2-min cd: auto-casts Justice every 1s for 6s | burst window | offensive cooldown icon (760379); buff rides cd_buffs |
| **Sunslam** (valkyrie) | "Only usable while Dawn is active" | Dawn-gated main-row button | `spellUsable == 0 → desaturate` carries the gate (check 9 mechanism); no extra trigger |
| **Seraphic Bulwark** (seraphim) | "2 Charges, 25 sec recharge" | held mitigation | CHARGES = 2 |
| **Dawn cast-count talents** (Guiding Glow, Solstice) | more fulfillment casts per Dawn | none visible | no WA change |
| Choose-one pairs (Zealous/Hegemony, Fortuitous/Angelic Light, Devoted to the Light/Sun, Final Vows/Taking Vows, Blightbreaker/Harmonious Bells …) | passive modifiers | none change what is pressed | no WA change |

Pack reads correctly untalented: proc-glow displays are active-only, the
charge count falls back to a plain cooldown, Vow rows are active-only aura
displays, and cooldown/utility leaves gate on their own spell id where
gateable.

---

## 3. Pets

- [x] Does this class summon a pet? **No.** Zero skillbook rows summon a
      persistent combat pet. The only summon-shaped entries are Scrying Orb
      (a controllable vision orb, no combat read, no id — `ignore`) and
      ground objects (Sunwell, Circle of Valor, Sun Gate, Dawnfall), which
      are zone cooldowns, not pets.
- [x] Player-pressed pet abilities? **None.**
- [x] Pet buffs/debuffs to track? **None.**
- [x] Pet absence alert? **Not applicable.**
- [x] Pet resource bar? **Not applicable.**

| Pet | Summoned by | Duration | Abilities/buffs to track | Where it renders |
|---|---|---|---|---|
| — none — | | | | |

---

## 4. Primary damage source and the main row

Spec roles (Sidekick-cited, pending in-game — recorded in
`resources/spec-roles.md` with the per-spec quotes):

- **blessings — healing** ("Strong in arena as a healer"; Holy
  Paladin/Discipline feel; kit corroboration 36/55 spec abilities mention
  heal/absorb/shield (65%) vs 5–15 on the other three — the ~5x healer
  signal)
- **piety — damage** (ranged Holy/Fire caster; "no heal button in the spec
  line itself")
- **seraphim — tank** ("Strength/Stamina block tank with a one-hand weapon
  and shield"; taunt Injunction, threat passive Sol Invictus)
- **valkyrie — damage** (melee hybrid; "The spec line has no direct
  in-combat heal spell")

| Spec | Primary damage/healing | Main row, in press order (cited from the Rotations text) | Icons | Resource |
|---|---|---|---|---|
| Blessings | Illumination/Shine throughput + the Bless bodyguard | Illumination → Shine → Daybreak → Radiant Cascade → Bless | 5 | Solar Power (aura 500149 stacks 0–20) + mana |
| Piety | Dawnsear/Sunflare nukes into Radiant Flame, Horusath, Rapture | Dawnsear → Sunflare → Radiant Flame → Horusath Blast → Rapture | 5 | Solar Power + mana |
| Seraphim | Justicar's Wrath threat + shield AoE, self-healing chassis | Justicar's Wrath → Dawnbreak → Hammer of Kings → Solar Nova → Illumination → Seraphic Bulwark | 6 | Solar Power + mana |
| Valkyrie | Glorious Execution/Justice weapon strikes in the Dawn cycle | Glorious Execution → Justice → Horusath Blast → Sunslam | 4 | Solar Power + mana |

Main-row derivations, one line each, from the spec pages' Rotations text:
- *Blessings dungeon:* "alternate Illumination/Shine as primary heals, and
  keep Daybreak and a rolling Bless on the tank … Keep Radiant Cascade for
  spread-healing bounces". Workhorse pair first, instant top-off, spread
  heal, then the rolling bodyguard tag.
- *Piety difficulty text:* "Build with Dawnsear and Sunflare, channel
  Radiant Flame, fire Horusath Blast and Rapture off cooldown, and it
  functions fine." Quoted order kept verbatim.
- *Seraphim solo/dungeon:* "Smash Justicar's Wrath on cooldown … Radiate
  Dawnbreak off your shield … Drop Hammer of Kings' encircling damage aura
  … use Solar Nova for burst AoE"; "Illumination as your single-target
  heal"; "Seraphic Bulwark's charges are held for the exact burst window" —
  the tank's in-row mitigation slot (the Mountain King Rock Barrier
  precedent).
- *Valkyrie difficulty text:* "Justice and Glorious Execution on cooldown …
  is enough to function", "Horusath Blast as filler", "Use Sunslam for its
  stun while Dawn is active". Glorious Execution first as spender + mana
  engine.

`CD_PER_ROW` derives from the narrowest row: valkyrie's 4 icons,
row_w(4)=182px, 28w−2 ≤ 1.2×182 → **7**.

**Resource envelope:** every spec runs **Solar Power** (ONE aura, 500149,
stacking 0–20, dur −1 — the `aura_stacks` shape) plus **mana**. Solar Power
renders as a 10-cell `stack_bar` at `step=2` (the Stormbringer Static
precedent: cells read in twos, full row = 20 = Dawn ready), nearest the main
row on every spec — it is the thing every page says to track. Mana renders
under it: full-height on blessings and piety (the kit taxes it hard: "mana
management is your real constraint"; "Mana funds the Holy/Fire spells"),
half-height `minor` on seraphim ("can run tight" but self-replenishing) and
valkyrie ("Mana can run dry in a long, poorly-managed fight" but Glorious
Execution refunds it — a side pool by its own text). Same two-band depth on
all four specs, so no anchor below the envelope moves.

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Vow missing | no Solar Power generation, no Dawn windows, on every spec | class-wide NO VOW alert (show-on-missing over the seven Vow auras) | tests/run.py inventory check + in-game pass (deferred, draft bar); the NO BOON shape is in-game-proven on Primalist-adjacent packs |
| Dawn window wasted | the whole Fulfillment payoff | Solar Power bar full (10/10 cells) + Dawn on-me icon | stack_bar mechanism in-game-proven (Pyromancer ember, Chronomancer fragments); 20-stack ceiling is tooltip-cited (500149) |
| Herald of Dawn proc wasted | double Dawnsear lost | PROC_GLOW on Dawnsear | glow mechanism proven (Runemaster/Pyromancer); aura name pending in-game (§6) |
| Burning Heat / Sun Ray window wasted | biggest Sunflare hit skipped | PROC_GLOW on Sunflare | §6 — granted-aura name unverified |
| Lord Commander proc wasted (seraphim) | free Daybreak lost | PROC_GLOW on Daybreak | §6 — granted-aura name unverified |
| Sunslam pressed outside Dawn | dead press | `spellUsable == 0 → desaturate` | check 9 enforces the condition on every cd_icon |
| Bless drops off the tank (blessings) | the whole Blessing family goes dark ("Purity, Retribution and Triumph are dead buttons") | target band bar (helpful=True) with refresh glow + Bless main-row icon | dot_bars refresh_at proven on three shipped classes |
| Sunshine/HoT drops (blessings) | rolling heal gone | target band bar with time + refresh glow | same mechanism |
| Burning Light / Purgation / Sins of the Father drop (piety) | DoT/amp uptime lost | target band bars by name | same mechanism |
| Seraphic Bulwark charge capped (seraphim) | wasted block income | charge count + escalation tiers ANDed with onCooldown | checks 9/10 |
| Unaffordable press (mana-dry heals) | "Run dry and you're down to instants" | desaturate on spellUsable == 0 | check 9 |

---

## 6. Open questions

- [ ] `UNKNOWN — Solar Power presentation: 500149 reads as a 20-stack aura
      ("You may unleash Dawn at 20 stacks", dur −1) and the pack ships it as
      a 10-cell step-2 stack_bar; whether the client shows it as an aura
      stack (vs a hidden counter) needs the one in-game read that settles
      every stack_bar.`
- [ ] `UNKNOWN — Dawn castable vs auto-state: Dawn 804584 carries a gcd and
      "Casting Dawn" appears in talent text, but no cooldown row exists;
      shipped as an on-me aura only, no button slot. If the client wants a
      pressable Dawn, feedback will say so.`
- [ ] `UNKNOWN — Vow of Grace / Vow of Light / Vow of the Eclipse / Vow of
      the Valkyr castable ids: the resolvable ids are component rows
      (Energize/Heal/Damage/Trigger); the long-term band matches the auras
      by name, which survives a wrong id. Castable ids need in-game
      tooltips.`
- [ ] `UNKNOWN — proc-granted aura names: Herald of Dawn, Burning Heat's
      Sun Ray window, Lord Commander's Daybreak grant, Cultivate Divinity's
      two payoffs, Beatification's Flash buff — displays match BY NAME +
      id where one resolves; whether the in-game aura name matches needs the
      verified pass.`
- [ ] `UNKNOWN — Sun Ray castable id (crossdb other-id: exiles 500145 vs
      asc 504764/572759/802943/802944/803238/804944); role held at ignore
      (transform face), so nothing ships on it.`
- [ ] `UNKNOWN — Chosen of the Light: New Day resets it and Holy Conquest
      cuts its mana cost (castable-shaped), but 706442 is rank=Proc and the
      two DB tooltips disagree; shipped as an on-me aura only, castable id
      unresolved.`
- [ ] `UNKNOWN — Solar Guidance: Guidance: Intervention / Touch of Light
      are "Only usable on allies with Solar Guidance active", and no
      castable "Solar Guidance" resolves in either DB. The two Guidance
      buttons ship as cooldown rows; how the Guided state is applied needs
      an in-game read.`
- [ ] `UNKNOWN — Mercy vs Blightbreaker: Sidekick's cited disease-cleanse
      castable is "Mercy" (503650 = rank Proc) while db.exil.es hangs the
      castable abolish tooltip on "Blightbreaker" 503375 (4s cd) and
      Sidekick calls Blightbreaker a choose-one talent. Mercy row ships the
      button (id hedge recorded); one tooltip read settles the name.`
- [ ] `UNKNOWN — Divine Retribution: cited as a signature valkyrie burst,
      but 570147 has no cooldown row and an empty tooltip — the accumulator
      smell. Shipped as an offensive icon on that id; if it never fires, the
      id is wrong, not the mechanism.`
- [ ] `UNKNOWN — Solar Invigoration castable id (562311 rank=Proc, cited as
      a castable ally-amp CD).`
- [ ] `UNKNOWN — March of the Valkyr and Sun Disc: rotation text says "put
      up" both, spell-meta says rank=Passive dur=−1. Both ship as long-term
      aura displays, which read correctly in either case.`
- [ ] `UNKNOWN — An'she's Blessing (piety cast-while-moving): castable
      cooldown or passive? sm rank=Passive; held ignore.`
- [ ] `UNKNOWN — Battle Priest (seraphim): audit found a 10s cd + 1.5s gcd
      row but the tooltip reads passive; held longterm (aura display, safe
      either way).`
- [ ] `UNKNOWN — Sins of the Father debuff name on target (rank=Trigger
      Damage component applies it); target band matches by name.`
- [ ] `UNKNOWN — Beatification / Divine Vision / Sunwalker-on-valkyrie /
      Controlled Fury's Rage mention / Suncharged stacks / the Aeon spells
      (Aeons of Conflict/Harmony teach four Aeon spells no database has
      heard of) — all held at ignore/hedged roles, listed here so the
      in-game sweep has its checklist.`
- [ ] `UNKNOWN — Flash (5s-cd Solar Power filler) is named in no rotation
      text; shipped in the offense row on the strength of being castable,
      press order uncited.`
- [ ] Hedged inventory rows (the 11 cleared `prop?:` markers, per the
      production bulk-clear default) are listed in the buildlog
      inventory-reviewed note; the in-game sweep is their checklist.
