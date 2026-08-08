---
title: Witch Doctor — class pack requirements (Phase 0)
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, witch-doctor, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[sidekick-witch-doctor-voodoo]]"
  - "[[sidekick-witch-doctor-brewing]]"
  - "[[sidekick-witch-doctor-shadowhunting]]"
---

# Witch Doctor — requirements

Class **13**, token `WITCHDOCTOR`, specs **Voodoo**, **Brewing**,
**Shadowhunting**. First build — no pack exists yet.

Research sources, in precedence order used below: the 2026/07/31 changelog
entries (dev statements, newest), db.exil.es spell pages / JSON API (scraped
2026-08-07: `exiles-witch-doctor.json` 577 spells,
`spell-meta-witch-doctor.json`), and the three Sidekick spec pages scraped
2026-08-07 to `resources/sidekick-witch-doctor-<spec>.md` (hyphenated slug
`witch-doctor` verified against the live site). The Sidekick snapshot
POSTDATES the newest changelog entry (2026-07-31), but its generated rotation
prose provably conflates at least one name (Zalazane's Malice, §0 traps), so
Sidekick is a reference with known soft spots, not truth.

**Spec roles.** `resources/spec-roles.md` had no Witch Doctor rows (unknown,
not damage-by-default). What the sources say, citably
(sidekick-witch-doctor-\<spec\> pages, 2026-08-07):

- Voodoo — "Strong in arena as a damage dealer" / "Solid in battlegrounds as
  a damage dealer"; "Voodoo has no ally heal, so your 'support' is protection
  and pressure … damage IS the support here" → **damage**.
- Brewing — "Solid dungeon healer — spot-heals pull damage" / "Strong in
  arena as a healer"; primary stat Spirit, the kit is a heal loop
  (Loa's Brew / Potion Toss / Mojo Beam / Cauldron) → **healing**.
- Shadowhunting — "Strong in arena as a damage dealer"; "The spec is built to
  contribute sustained ranged damage, not to stand and heal" → **damage**.

All three go into `spec-roles.md`, provenance noted as Sidekick kit statements
pending in-game observation. **Brewing gets the healing target band
(`dot_bars(helpful=True)` on the current target ONLY — VuhDo owns raid
frames) and a healing-rotation main row.**

---

## −1. Changelog — 19 entries, scanned FIRST (2026-08-07, pages 6)

Newest entry: **2026-07-31**. NOT `--accept`ed until everything below is
built or filed.

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| **Spirit Volley base damage −34%** — "was the best to use in all scenarios, even single target" | 07/31 | rebalance | §4 — Spirit Volley is the AoE cast, NOT a single-target main-row entry; any pre-07/31 priority naming it first is stale. Sidekick scrape (08/07) postdates the nerf and does not put it in the single-target loop |
| Spirit Volley cast-time haste double-dip fixed; now uses ranged crit | 07/31 | numbers | none |
| Bwonsamdi's Gift: Spirit Volley bonus 3%→2%/Spirit; no longer reduces Mimic Ward CD | 07/31 | numbers | none (passive) |
| Loa Spirits: Reclamation extra-cast chance 25%→20% at max Spirits | 07/31 | numbers | none — confirms "max Spirits" is a capped bank (5) |
| Godslayer damage split base/scaling | 07/31 | numbers | none |
| Spirit Glaive base+scaling +69% | 07/31 | numbers | none |
| Veil of Darkness base+scaling +22% | 07/31 | numbers | none |
| Hex of Malice base+scaling +18% | 07/31 | numbers | none |
| Auto Shot +19% | 07/31 | numbers | none |
| Voodoo Fire +20% | 07/31 | numbers | none |
| Reclamation +21% | 07/31 | numbers | none |
| Mojo: Jungle Thistle threat reduction removed, secondary +10% | 07/31 | numbers | none (brewing utility) |
| Puppeteer's Threads triggered damage no longer reflectable | 07/31 | behaviour | none |
| Spirit in a Bottle rank progression fix | 07/31 | numbers | none |
| Healing Ward radius consistency fix | 07/31 | numbers | none |
| Spirit Link Idol full-duration + Hastened interaction fix | 07/31 | behaviour | none — confirms Hastened (−25% Ward/Idol/Effigy CD) affects Idols |
| Loa Spirits could trigger from Mimic Ward replications — fixed | 07/31 | behaviour | none |

- [x] changelog scanned, newest entry: `2026-07-31`
- [x] every entry triaged (no replaced/reworked/new-spell entries this round —
      all tuning/fixes)
- [ ] `--accept` only after the pack is built against these

---

## 0. Ability surface — both databases

`tools/crossdb_sweep.py witch-doctor` runs over the whole reviewed inventory
(every row with an id); verdicts in `resources/crossdb-witch-doctor.json`,
per-row consequences in the inventory Notes. (Results in the buildlog crossdb
step.)

Known traps found during id resolution (db.exil.es side):

| Name | Id question | Resolution |
|---|---|---|
| Zalazane's Malice | Sidekick rotation prose says "keep Zalazane's Malice applied … spread by Bad Juju/Hexfire" as if it were the DoT | the CoA skills tooltip (705902, Passive) reads "Increases the damage of Hex of Malice by % and the duration of Jinxes by sec" — it is a passive AMPLIFIER. The applied DoT is **Hex of Malice**; the maintain claim lands on Hex of Malice. Recorded in aliases |
| Spirit Shock | db.exil.es 806294 rank literally `Deprecated` | castable is **807743** (25% mana, 28 s cd silence+interrupt — ascension tooltip read 2026-08-07) |
| Veil of Darkness | 524670: cd 0, gcd 0, cost 0, dur 0 — the component smell | castable is **802100** (8% mana, 1 min cd, 15 s +15% damage window — ascension tooltip) |
| Jin'do's Wrath | 707505 rank Passive (duration −1) | **NOT a button.** Both db rows (707505 talent, 707913 lvl 31) are passives: "Increases the critical strike chance of Hexfire by 25%". The Sidekick press claim ("Jin'do's Wrath and Hexfire to cash in") lands on **Hexfire** — the passive empowers it. Dropped from the main row |
| Spirit Volley | 503712 rank `Specialization` | castable is **504582** (1.8 s cast AoE, collects a Spirit, −3 s Spirit Glaive cd — ascension tooltip) |
| Call of Sseratus | 572899 rank `Summon`, cd 0 | castable is **681222** (28% mana, 40 s cd, summons 4 Serpent Wards for 15 s — ascension tooltip) |
| Voodoo Cauldron | 504418: cd 0 — component smell | castable is **804684** (11% mana, **3 min cd**, 15 s zone — ascension tooltip). A 3-min cooldown, NOT a rotation upkeep: it moves off the main row into the healing-cooldown row |
| Big Bad Voodoo | 801665: cd 0 | castable is **802719** (25% mana, 5 min cd immunity zone — ascension tooltip) |
| Umbral Glaive | 801673's own db.exil.es description is literally "Deprecated" | ascension **504588** is a live castable (8 s cd leech glaive) — other-id; §6.6 |
| Reclamation / Malefic Arrow | crossdb NO-RECORD on db.ascension.gg | resolved WITHOUT deleting: the 2026/07/31 dev changelog names Reclamation (a dev statement outranks a database's silence), and ascension carries an "Improved Malefic Arrow" talent — its base must be live. That DB's snapshot is incomplete for this class; §6.10 |

- [x] every inventory row with an id cross-checked against both DBs (sweep)
- [x] `no-record` rows resolved by name re-ask + tooltip read, verdict in Notes
- [x] deprecated/unused/placeholder names filtered (`DEPRECATED`, `SLS` stubs,
      `Stack Applier/Remover/Visual` machinery)

---

## 1. Mandatory buffs

**Class-wide.**

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Mana** (power) | class economy | every spec: "Primarily mana, and it's spent hard" (voodoo); "Mana, spent aggressively" (brewing); "Mana-based" (shadowhunting) | resource envelope, all three specs — §4 |
| **Spirits banked** (voodoo + shadowhunting) | Loa Spirits / Reclamation / Shadow Puppets / Spirit Hunting | "Banking Spirits is a damage loop and a scaling loop at once" (voodoo); Spirit Eclipse ammo (shadowhunting) | **UNKNOWN — no player-aura id for the Spirit count resolves from any scrape; Spirits appear to be summoned entities, not an aura (§6.1). No Spirit bar in the draft** |
| **Veil of Darkness** on target | class ability | +% damage you deal to that target — the burst opener | offensive row; target band |
| **Ward/Idol/Effigy drops** | class kit | totem-style: "Drop a … near you", one Ward / one Effigy at a time; Hastened −25% CD | cooldown rows (player-side tracking; §3 — these are NOT pets) |

**Voodoo.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Hex of Malice** DoT on target (24 s) | spec | "Zalazane's Malice uptime tracked or Bad Juju, Jin'do's Wrath and Hexfire give you nothing" (the prose name is the amplifier; the DoT is Hex of Malice) — Ritual Hexing: +% damage of Bad Juju / Malefic Wrath / Hexfire against Hexed enemies | target band, refresh glow |
| **De Other Side** stacks (20 s, "additional procs do not refresh") | Shadow Puppets impacts | "increases your damage and critical strike chance … stacking up to X times"; "Keep your De Other Side stacks alive off Shadow Puppets" | "on me", stacks |
| **Puppeteer's Threads** on target | L10 passive, applied by damaging abilities | "the connective tissue. Hexfire snaps your threads to unleash their damage" | target band |
| **Voice of Bwonsamdi** (90 s CD, 20 s) | spec | "your burst window on priority targets" | offensive row + running CD in "on me" |
| **War Golem** (3 min CD, 10 s) | spec | "when the group is about to eat a big targeted or AoE magic hit" — absorb + spell redirect | defensive row |
| **Overflowing Juju / Voodoo Unleashed** resets | talents | "resets chain to keep Bad Juju and Shadow Puppets flowing" | Bad Juju's own cooldown trigger follows resets natively; no extra display |

**Brewing** (healer).

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Voodoo Cauldron** placed | spec | "Keep Voodoo Cauldron down for its heal-over-time pulse and healing-received zone" — but the castable (804684) is a **3 min cooldown, 15 s zone**, so the prose overstates the cadence | healing-cooldown row (offensive slot), urgency tiers |
| **Master Mixologist** (2 min CD, 10 s) | spec | "the group heal-burst and wipe-prevention amplify window"; also Spirit in a Bottle while moving | offensive-slot cooldown + running window in "on me" |
| **Jungle Shrooms HoT on target** | Ingredient: Jungle Shrooms via Potion Toss | "Potion Toss: Heal the target ally for every sec" — the per-target HoT the band can read | healing target band |
| **Frog Bones absorb on target** | Ingredient: Frog Bones via Potion Toss | "Grants target ally an absorption shield" | healing target band |
| **Bloodthistle leech on target** | Ingredient: Bloodthistle via Potion Toss | "Causes target ally to leech % of all damage they deal" | healing target band |
| **Mojo Beam channel window** | spec | "While channeling … instantly cast Potion Toss, Splash Potion and Spirit in a Bottle" | main row (Mojo Beam's own CD icon; channel state is the cast bar's job) |
| **Cauldron brewed (Ingredient/Spice/Base)** | spec | "The Cauldron is the spec" | utility-row cooldown icons; §6.3 for a missing-Cauldron alert |

**Shadowhunting.**

| Buff | Source | Why | Renders |
|---|---|---|---|
| **Serpent Wards out** | Serpent Ward / Call of Sseratus (15 s) | "Keep Serpent Wards up via Call of Sseratus. Resummon the pack when it expires" | main row CD icon — the swipe IS the "wards expiring" cue (§3) |
| **Hex of Malice** DoT on target | spec (spread by Shadowflare, refreshed by Umbral Glaive) | "holding Hex of Malice and Hex of Death uptime for the healing cut and damage bonuses" | target band, refresh glow |
| **Hex of Death** on target | passive, applied by Malefic Arrow | healing-received cut on the kill target | target band (by name; passive-applied) |
| **The True Spirit** stacks (10 s, 5) | talent, per Ward/Spirit summoned | "empowers your next Spirit Glaive or Spirit Eclipse" | "on me", stacks; PROC_GLOW on Spirit Eclipse + Spirit Glaive |
| **Frenzied Spirits** (20 s CD) | spec | Spirit-spend crit + self-heal window | defensive row + "on me" |
| **Shadow Avatar** (90 s CD, 15 s) | spec | burst: haste + Spirit Glaive CDR (Vol'jin's Blessing) | offensive row + "on me" |
| **Veil of Darkness → Mimic Ward → Shadow Avatar → Fool's Play** | spec | the cited burst line-up | offensive row, press order |

**Missing-buff alerts** (§5): none class-wide — the class has no
imbue/engraving-shaped prepull kit and no permanent pet. §6.3 keeps the
missing-Cauldron idea as a feedback question rather than shipping an alert on
an unverified aura.

---

## 2. Talent-driven rotation changes

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| **Overflowing Juju** (voodoo L30 passive) | resolved in inventory | "chance to reset the cooldown of Bad Juju" | extra Bad Juju presses | cooldown trigger follows resets natively; no extra display |
| **Voodoo Unleashed** (voodoo) | inventory | "casting Bad Juju now reduces the cooldown of Shadow Puppets" | faster Shadow Puppets loop | same — swipe follows |
| **The True Spirit** (shadowhunting) | 802268 (aura, −1 dur, stacks 5) | next Spirit Glaive / Spirit Eclipse empowered per summon | spend timing | `PROC_GLOW` on both spenders + `PROC_STACKS` |
| **A Price To Pay** (shadowhunting) | inventory | Spirit Eclipse at 5 Spirits resets Spirit Glaive + guaranteed crit | eclipse-then-glaive pairing | Spirit Glaive's cooldown trigger follows the reset; glow deferred (§6.1 — needs the Spirit count) |
| **Frenzied Spirits** (shadowhunting) | 560748 | consumes Spirits: crit + self-heal window | spend choice vs Spirit Eclipse | defensive-row icon; window in "on me" |
| **Serpent Handler** (choice) | inventory | Call of Sseratus +5 s CD, +2 wards | ward upkeep cadence | cooldown trigger reads the real CD either way |
| **Hexfire Mass** (choice) | inventory | Hex of Malice damage can summon a Serpent Ward | free wards | no display (fire-and-forget) |
| **Malicious Golems** (voodoo) | inventory | Hex of Malice / Shadow Puppets damage reduces War Golem CD | more golems | cooldown trigger follows CDR natively |
| **Chosen One** (class) | inventory | Mimic Ward summons +1 ward | numbers | none |
| **Mojo: Jungle Thistle** (brewing) | inventory | resets Potion Toss / Splash Potion + swaps Ingredients | burst-heal window | utility cooldown icon; Potion Toss swipe follows the reset |
| **Master Brewer** (brewing) | inventory | chance to unleash Cauldron: Jungle Shrooms | passive | none |
| **Splash On 'Em** (brewing) | inventory | Loa's Brew / Mojo Beam healing shaves Potion Toss / Splash Potion CD | faster instants | cooldown triggers follow CDR natively |
| **Rite of the Loa** (shadowhunting) | inventory | places every selected Ward/Effigy/Idol at once | pre-pull convenience | utility row |
| **Spirit Warden** (class) | inventory | Idol summon → +10% Spirit 1 min | minor self-buff | "on me" is active-only; no dedicated row |

No talent in any scrape REPLACES an ability with a different spell id or
TRANSFORMS a button (no Elemental-Mastery / Sixfold-Shot shape found in the
talent texts of any of the three trees) — so no `spell_swap` and no Spell
Known transform wiring this build. §6.5 keeps a watch on it.

With/without check: every proc row above only ADDS an active-only display —
correct untalented (never fires). Cooldown-reset talents ride the native
cooldown trigger, correct in both states.

---

## 3. Pets

- [x] Does this class summon a pet? **NO permanent companion, on any spec.**
      Everything summon-shaped is a totem-style drop or a short temporary:
      Wards ("Drop a … Can only have 1 Ward active at a time" — Serpent 15 s,
      Viper, Healing, Voodoo, Mimic 12 s), Idols (Cleansing / Spirit / Dark /
      Jungle / Serene / Swift / Spirit Link), Effigies (Cursed / Dark /
      Graven / Hexing / Shadow — "1 Effigy at a time"), War Golem (10 s),
      Shadow Puppets (rush-and-die), Big Bad Voodoo (copy, 8 s), Fool's Play
      (copy of the ENEMY, 20 s), Call of Sseratus (4 Serpent Wards, 15 s).
      Decided per tooltip, not from the word "summon".
- [x] Pet abilities the player presses: none — no pet bar, no pet spellbook.
      The summons are cast-and-forget; the player-side button IS the tracking
      surface (cooldown rows).
- [x] Pet buffs/debuffs to track: none on a pet unit. Berserking haste rides
      the Wards invisibly; nothing to draw.
- [x] Pet presence gating the rotation: Shadowhunting wants Serpent Wards up
      — that is a 15 s duration + resummon loop, and the CUE is Call of
      Sseratus / Serpent Ward coming off cooldown (urgency tiers), not a
      NO-PET alert. No `unit="pet"` machinery anywhere in this pack.
- [x] Pet resource: none.
- [x] **Avatar Dinosaurs** — the one genuinely pet-shaped thing found in the
      kit: Call Avatar: Devilsaur / Pterrordax / Stegodon / War Raptor, plus
      Bind Avatar ("Take direct control of your current Avatar Dinosaur …
      When this ends, the Avatar Dinosaur dies") and Dismiss Avatar, with
      `(Pet)`-ranked support rows in db.exil.es (Feline Frenzy, Touch of
      Sseratus, Gift of the Loa Pet Trigger/Forcecast). **Appears in NO cited
      rotation on any of the three spec pages**, so the whole layer is
      excluded from bands — the Witch Hunter Crossbow-Stance precedent — and
      filed as §6.9 rather than built on a guess. No NO-PET alert, no
      `unit="pet"` rows this build.

| Pet | Summoned by | Duration | Track | Renders |
|---|---|---|---|---|
| Serpent Wards | Call of Sseratus / Serpent Ward / Viper Ward | 10–15 s | resummon cadence | main-row / offense CD icons (player-side) |
| War Golem | War Golem (voodoo) | 10 s | the save window | defensive row |
| Shadow Puppets | Shadow Puppets (voodoo) | seconds | De Other Side stacks (on YOU) | "on me" stacks |
| Mimic Ward | Mimic Ward | 12 s | burst window | offensive row |

---

## 4. Primary damage source and the main bar

Press orders from the Sidekick per-spec rotation text (solo/dungeon
paragraphs, scraped 2026-08-07), imported as citations.

| Spec | Primary damage | Main row, in press order | Icons | Resource |
|---|---|---|---|---|
| Voodoo | Bad Juju + Shadow Puppets (De Other Side ramp), Hex of Malice amplified | Bad Juju · Shadow Puppets · Hexfire · Hex of Malice · Malefic Wrath | 5 | mana bar |
| Brewing (healing) | — healing rotation: "Loa's Brew as the primary heal filler, backed by the instant Potion Toss … Splash Potion for stacked-group healing, and Spirit in a Bottle on tank or cleave" + Mojo Beam channel-weave | Loa's Brew · Potion Toss · Spirit in a Bottle · Splash Potion · Mojo Beam | 5 | mana bar |
| Shadowhunting | ranged/RAP kit: Reclamation / Malefic Arrow / Spirit Glaive / Spirit Eclipse with Serpent Wards out | Reclamation · Malefic Arrow · Spirit Glaive · Spirit Eclipse · Call of Sseratus | 5 | mana bar |

- **Mana only, all three specs.** One full-height `power` bar
  (`Y_BAR_SOLO` / `BAR_H_SOLO`). The Spirit bank would be a second band on
  two specs but has NO readable aura id (§6.1) — never render what cannot be
  read; a wrong id fails silently.
- Voodoo order: "Bad Juju on cooldown (main nuke) → Shadow Puppets on
  cooldown → Jin'do's Wrath and Hexfire to cash in" — and Jin'do's Wrath is a
  PASSIVE (both db rows: Hexfire crit +25%), so the cash-in press is Hexfire.
  Hex of Malice is the maintain (its slot doubles as the reapply button);
  Malefic Wrath is the filler nuke ("chain nukes: Bad Juju, Malefic Wrath,
  Hexfire" — playstyle).
- Shadowhunting order: "1) Keep Serpent Wards up via Call of Sseratus 2) fill
  … Reclamation … and Malefic Arrow 3) Spirit Glaive … then spend banked
  Spirits with Spirit Eclipse" — most-pressed first puts the fillers ahead of
  the 15 s-cadence resummon; Shadowflare (the Hex spreader) and Spirit Volley
  (the AoE cast) sit in the offensive row.
- Narrowest main row is 5 icons on every spec → row_w(5) = 228 px;
  `28w − 2 ≤ 1.2 × 228` → **w ≤ 9.8 → CD_PER_ROW = 9**, to be confirmed
  against `tools/rowwidths.py` on the built pack.

Off the main row, still cited: Voice of Bwonsamdi, Veil of Darkness, Mimic
Ward, Shadow Avatar, Fool's Play, Master Mixologist, Frenzied Spirits, War
Golem, Malignant Jinx, Shadowstalker, Umbral Glaive, Spirit Volley (AoE),
Spirit Shock (interrupt, pinned last) → offensive/defensive/utility rows.

---

## 5. Miss-handling

| Ability / state | Cost of missing it | Cue | Proof the cue fires |
|---|---|---|---|
| Hex of Malice dropped (voodoo, shadowhunting) | "Bad Juju, Jin'do's Wrath and Hexfire give you nothing" / healing-cut + bonuses lost | target-band bar, refresh glow ≤4 s | `dot_bars` refresh condition on aura `expirationTime` (aura trigger — no GCD guard needed); mechanism shipped on 6 classes |
| Puppeteer's Threads unspent (voodoo) | Hexfire detonation lost | target-band bar (threads visible on target) | same mechanism |
| De Other Side stacks lapse (voodoo) | damage + crit ramp resets ("additional procs do not refresh") | "on me" stack icon with timer | buff row active-only, stacks via `%s`; shipped shape |
| Serpent Wards expire (shadowhunting) | sustained damage stops | Call of Sseratus / Serpent Ward swipe + urgency tiers | check 9 (tiers ANDed `onCooldown == 1`), check 10 |
| The True Spirit unspent (shadowhunting) | empowered Glaive/Eclipse wasted | proc glow on Spirit Glaive + Spirit Eclipse | `PROC_GLOW`; check 9 |
| Jungle Shrooms HoT / Frog Bones absorb lapse on tank (brewing) | tank healing throughput lost | healing target band, refresh glow | `dot_bars(helpful=True)`; Chronomancer Time mechanism |
| Voodoo Cauldron down (brewing) | heal pulse + heals-received zone lost | healing-cooldown row icon with urgency tiers (3 min cd, 15 s zone) | check 9/10 on the icon |
| Mana dry | casts stop | mana bar + `spellUsable == 0 → desaturate` on every cd icon | check 9 *desaturate when unusable* |
| Off-GCD buttons sweeping falsely | phantom cooldown | `use_showgcd` off, derived from `cooldown-abilities-witch-doctor.json` | check 10, both directions |
| Cooldowns coming back | clipped burst | urgency tiers 20/10/5 ANDed `onCooldown == 1` | check 9, *no bare expirationTime tier* |

---

## 6. Open questions

- [ ] **6.1 Spirit-count read** — UNKNOWN — voodoo and shadowhunting bank
      "Spirits" (cap 5 per A Price To Pay / the 07/31 Loa Spirits entry), but
      no scrape yields a player-aura id for the count: 561067 "Spirit" is the
      run-through-a-spirit reclaim buff, 561065 "Shadowhunting Spirit" has an
      empty tooltip, and the "Spirit N Stack Visual/Applier/Remover" rows
      (561378–82, 504689, 505184) are machinery. Spirits may be summoned
      ENTITIES (561067: "Running through a Spirit reclaims it"), in which
      case there is nothing UnitAura can count. NO Spirit bar ships in the
      draft. Settles: in-game `/rmdump` diff while banking a Spirit (the
      Pyromancer Ember method).
- [ ] **6.2 Brewing target-band aura ids** — Jungle Shrooms / Frog Bones /
      Bloodthistle Potion-Toss effects and Loa's Brew's "random effect"
      empowerments are matched BY NAME (the applied auras' own ids are
      rank-`Aura`/`Proc` rows, the component smell). A name mismatch fails
      silently. Settles: heal a target once per Ingredient in game.
- [ ] **6.3 Missing-Cauldron alert** — "The Cauldron is the spec" suggests a
      `NO CAULDRON` reminder, but whether a brewed Cauldron registers as a
      player aura on this fork is unverified — no alert ships on unverified
      ground (the Runemaster reminder-band lesson). Settles: one in-game read
      of the brewed state; feedback can vote it in.
- [ ] **6.4 Hex of Death aura name** — applied by Malefic Arrow via a passive
      (706557, dur −1). Target-band row matches by name. Settles: tooltip on
      a hexed target.
- [ ] **6.5 Transforms** — no replace/transform talent found in any of the
      three trees' scraped texts; if in-game shows a button transforming
      (Spirit Eclipse at 5 stacks, Frenzied Spirits state), wire a Spell
      Known trigger on the replacement id then.
- [ ] **6.6 Ascension-tooltip-resolved castable ids** — Veil of Darkness
      802100, Spirit Shock 807743, Call of Sseratus 681222, Voodoo Cauldron
      804684, Big Bad Voodoo 802719, Spirit Volley 504582, Umbral Glaive
      504588 (whose two snapshots disagree on the tooltip text: exil
      "curses…refreshes Hex of Malice" vs ascension "leech…next Umbral Glaive
      crits"). Each replaces a component-smell db.exil.es row (cd 0 gcd 0 /
      Passive / Specialization / literal `Deprecated`) after a name re-ask +
      tooltip read on db.ascension.gg (2026-08-07). Settles: in-game
      tooltips → `in-game-verified.json`.
- [ ] **6.7 Hedged inventory rows** — the automated role pass's hedged rows
      (14, listed in the buildlog inventory step note: Dark Effigy, Death
      Draught 'UNUSED' tooltip, Devotion of Gonk, Feast of the Loa, Jani's
      Intent, Juju, Juju Injection, Major Rejuvenating Mojo, Mojo: Fish
      Bones / Frog Shrooms, Staff of the Coven, Viper Ward, Voodoo Puddle);
      community feedback and the post-ship sweep walk them.
- [ ] **6.8 Big Bad Voodoo spec membership** — skills JSON tags it
      brewing+shadowhunting; the voodoo Sidekick page never names it. Kept
      off voodoo's rows. Settles: spellbook read.
- [ ] **6.9 The Loa Invocation / Devotion / Appeasement / Avatar layer** —
      ~22 real inventory rows ("Invokes <Loa>", Shadow Marks, Devotions
      sharing a 5 s cooldown, Avatar Dinosaurs with `(Pet)` support rows)
      that appear in NO cited rotation on any spec page. Excluded from all
      bands this build (the Witch Hunter stance-kit precedent). If feedback
      says a live build plays through Invocations, the layer earns its own
      research round — including a real pet section for Avatars.
- [ ] **6.10 db.ascension.gg incompleteness** — Reclamation and Malefic Arrow
      are crossdb NO-RECORD there while the dev changelog (Reclamation,
      2026/07/31) and an Improved Malefic Arrow talent prove the abilities
      live; Dire Rage's spec list is unknown (hedged `all`). Settles:
      spellbook read per spec.
