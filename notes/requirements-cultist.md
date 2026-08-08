---
title: Cultist pack requirements
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, cultist, requirements]
sources:
  - "[[class-requirements-template]]"
  - "resources/sidekick-cultist-corruption.md (scraped 2026-08-07)"
  - "resources/sidekick-cultist-dreadnought.md (scraped 2026-08-07)"
  - "resources/sidekick-cultist-godblade.md (scraped 2026-08-07)"
  - "resources/sidekick-cultist-heretic.md (scraped 2026-08-07)"
  - "resources/cooldown-abilities-cultist.json (db.exil.es audit, 2026-08-07)"
  - "db.ascension.gg ?spell=<id>&power tooltips, 2026-08-07"
---

# Cultist — class pack requirements

Class 25, token `CULTIST`, **four** specs: **corruption** (ranged shadow
DPS), **dreadnought** (tank), **godblade** (melee DPS), **heretic** (healer).
Roles from citable Sidekick kit statements (`resources/spec-roles.md`
provenance note, 2026-08-07); heretic is the one healer, so `helpful=True`
target-band scope applies to it and to nothing else.

The class-wide spine: **Insanity**, a 0–100(+) meter every spec builds and
manages against the **Total Madness** backfire at 100 (cleansed only by an
allied Cultist's Restore Sanity, 801157). Every ability also costs a % of
base mana, so all four specs are dual-resourced.

---

## −1. Changelog — run FIRST

`python3 tools/changelog_watch.py --class cultist --pages 6` → 22 recorded
entries, **all dated 2026/07/31**, scanned 2026-08-07 ("nothing new" — the
entries were already recorded, none accepted before this triage).

- [x] changelog scanned, newest cultist entry: `2026-07-31`
- [x] every entry triaged (below)
- [x] `--accept` run only after this table was written and acted on

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| **NEW: Eldritch Shock — Insanity spender, damage OR heal** | 2026/07/31 | new spell | inventory row (808036, both DBs; instant, 8 s cd, drains 20 Insanity). ABSENT from the skillbook scrape and from every Sidekick page incl. today's — no build site has integrated it. Ships as an offensive-row icon; spec membership is §6 |
| Dark Whispers reworked to **Twilight Horror** (Eldritch Shock synergy capstone) | 2026/07/31 | reworked | 560977, Passive — corruption capstone talent; passive, no button; its **Inspired Malice** rider is a §1 proc candidate (aura id unresolved — §6) |
| Twilight Horror ↔ Abyssal Destruction swapped places | 2026/07/31 | tree position | no WA surface |
| Horrorbolt Volley now a pre-capstone | 2026/07/31 | tree position | no WA surface (talent still exists; transform handling in §2) |
| Horrorbolt Volley cast 3.5 s → 2.5 s | 2026/07/31 | numeric | no WA surface |
| Dark Infusion moved to the class tree | 2026/07/31 | tree position | inventory Specs widened from heretic to all (skillbook still says heretic — changelog outranks it; §6 confirms) |
| Black Blood spell-power / healing-taken scaling fix | 2026/07/31 | numeric | no WA surface |
| Black Blood ally-targeting priority (Abyssal Covenant first) | 2026/07/31 | mechanics | no WA surface (server-side smart heal) |
| Black Blood no first-tick, duration refresh no tick reset | 2026/07/31 | mechanics | target-band note: re-casts DO now refresh duration — the heretic Sidekick text ("duration doesn't refresh") **predates this entry**; §6 |
| Void Reaver: next Blade of the Empire mana-free | 2026/07/31 | mechanics | no WA surface (rider on an existing proc) |
| Void Augmentation / Dread and Terror / Instilling Fear / Dark Reservoir / Oblivion's Embrace / Doomsayer-family now affect Eldritch Shock | 2026/07/31 | talent scope | no WA surface (numeric riders) |
| Dark Prophet heals 2 lowest allies, down from 5 | 2026/07/31 | numeric | no WA surface |
| Abyssal Destruction: periodic/channeled damage generates 2 Insanity | 2026/07/31 | resource numeric | no WA surface |
| Doomsayer ↔ Devourer swapped in class tree | 2026/07/31 | tree position | no WA surface |
| Doomsayer + Embodied Presences combined | 2026/07/31 | talent merge | inventory note (both names still resolve; passive either way) |
| Eldritch Devastation 6 s → 4 s, faster ticks | 2026/07/31 | numeric | no WA surface |
| Dark Channeler added as switch node with Misery; Misery buffed | 2026/07/31 | tree mechanics | both passives, no button; no WA surface |
| Madness debuff 10 s → 20 s | 2026/07/31 | numeric | no WA surface |

**Staleness:** the Sidekick spec pages were scraped fresh 2026-08-07 but
their *content* still predates 2026/07/31 in at least two places: no page
mentions Eldritch Shock, and the heretic page still teaches the pre-patch
Black Blood refresh rule. Rotation-structure claims are otherwise unaffected
— the batch is tree positions, numerics and one new spell — so the pages
remain the mechanics source with those two exceptions flagged here and in §6.
`resources/sidekick-data.js` (mtime 2026-08-02) also post-dates the batch but
predates Sidekick integrating it, so the citation import carries no
Eldritch Shock claim either.

---

## 0. Ability surface — both databases

`tools/exiles.py cultist` → 572 spells. `tools/mkabilities.py cultist`
seeded 247 rows (240 skillbook + audit additions); roles assigned by an
automated pass 2026-08-07 and cleared in bulk (production-run.md precedent),
one line of reasoning per Notes cell.

`tools/crossdb_sweep.py cultist`: **228 of 228** inventory rows with an id
asked of db.ascension.gg (db.exil.es is the id source). Result: **227
record, 1 no-record** — Psychic Burst 681319, resolved in its Notes cell:
db.ascension returns an empty registerSpell, only the Veiled Knight talent
references it, role `ignore` (the Manastorm shape), nothing deleted on the
verdict.

Name re-asks resolved seven component-shaped ids (the reaper Cull pattern),
each read against both tooltips and recorded in the row's Notes cell +
the builder's CROSSCHECK dict:
- Ancient Curse 354191 (`Damage` component) → **500712** (castable, tab 27)
- Herald of the Depths 92131 (`Spec Passive`) → **520326** (45 s cd
  transform, advType Ability)
- Presence of Y'Shaarj 573277 (curse component) → **803035** ("Assume a
  powerful Presence")
- Presence of Yogg-Saron 801560 (`Radial`) → **803082** ("Assume a crazed
  Presence")
- Dreadnought 92-family passive → **567524** (ranked castable the L10
  passive teaches; 45 s cd absorb transform)
- Wrath of The Black Empire 500724 (stale Void-Rune tooltip) → **800413**
  (live: 2 s cast, drains 20 Insanity)
- Eldritch Shock (changelog-new, not in any scrape) → **808036** added as a
  new row

Two prose names resolved to different data names
(`resources/aliases-cultist.json`): Sidekick's godblade "Obliteration" is
**Hammer of Twilight**, dreadnought's "Void Strikes" is **Entropic Slam**.
One cited ability is unbuildable: **Eye of N'zoth** has no castable id in
either DB (§6).

- [x] every inventory row cross-checked against both DBs (100%, see
      buildlog `crossdb` step for the count)
- [x] `no-record` rows resolved in the Notes cell — none deleted on the
      verdict alone
- [x] deprecated/unused/placeholder names filtered (`utility_tables.JUNK`;
      plus rank markers `UNUSED` — e.g. Black Blood 804113 is rank UNUSED,
      the live HoT aura is found by name re-ask)

Known component-shaped ids caught by rank text before the sweep (the reaper
Cull pattern — db.exil.es links a component, the castable lives elsewhere):
Obliteration 92129 (`Specialization`), Void Strikes 567529 (`Scaling`),
Void-Enhanced Shield 572025 (`Insanity Value`), Eye of N'zoth 573313
(`Proc`), Ancient Curse 354191 (`Damage`), Presence of Y'Shaarj 573277
(curse component). Each is re-asked by name; corrections land in the
builder's `CROSSCHECK` dict with one line of tooltip reasoning.

---

## 1. Mandatory buffs

| Buff | Source (class/talent/ability) | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Insanity** (500706, stacks 0–100, dur −1) | class meter | every spec's thresholds hang on it: corruption >60 empowered Obliteration Beam + Embrace the Void, godblade >40 Shadow of the Void, dreadnought 60–80 shield scaling, heretic spend-before-cap; 100 = Total Madness backfire | 10-cell `stack_bar` step=10 in the resource envelope (the Stormbringer Static pattern), every spec |
| Presence (one per spec: C'Thun 803339 / Y'Shaarj / N'Zoth 803037 / Yogg-Saron) | class stance system, "only 1 active" | Sidekick heretic dungeon text: "Pick your Presence" — a forgotten Presence is silent throughput loss | long-term band; §5 alert deferred to §6 (aura visibility unproven) |
| Whispers of C'thun / N'Zoth / Y'shaarj / Yogg-Saron (+ Greater) | ally blessing, "one Whisper per Cultist" | Kings-mould raid buff, checked once per pull | long-term band |
| Corrupting Whispers (92130 family) | corruption spec proc | "boosts your magic damage" — the payoff for riding high Insanity | buff row + §6 aura id |
| Presence of C'Thun haste windows | corruption (fed by Gaze casts) | "self-haste burst" windows to chain casts into | buff row |
| Horrorbolt Volley window (255020, 15 s) | corruption talent | after 3 Horrorbolts the filler transforms — the window is the AoE burst | buff row + PROC_GLOW on Horrorbolt; §6 (counter vs window aura) |
| Shadow of the Void stacks (300277) | godblade >40 Insanity passive | "ride the stacks" is the cited priority's third clause | buff row |
| Voidborne (681104, 3 min) | godblade burst cd | burst-and-anti-stun window | buff row + offensive icon |
| Dreadnought (567524, 20 s absorb transform) / Doomcloak / Abyssal Ward windows | dreadnought mitigation layers | "want to land against incoming burst" — running-state visibility (Void-Enhanced Shield / Bulwark of Shadow / Eldritch Bastion turned out passive — §6) | buff row + defensive icons |
| Herald of the Depths window (92131) | heretic L10 spec passive | "not just the passive that neutralises Total Madness; an active window … Sanity Tap before you pop it" | buff row; §6 (window aura vs passive id) |
| Eldritch Eye (802049, 15 s) / Malevolent Power proc | heretic procs | "Eldritch Mending is a trap to hard-cast. Fire it off Malevolent Power's every-third-melee proc, or off Eldritch Eye" | PROC_GLOW on Eldritch Mending (+ Malevolence) |
| Black Blood (on allies) | heretic main throughput | the HoT your damage pays out | target band (`helpful=True`) on current ally target |
| Abyssal Covenant (500701) | heretic tank link | "It drops when you change instance, so recast it every time" | target band entry + long-term|
| Total Madness / Madness (570172 / 520674) | class cap backfire | the thing the whole meter avoids | stack-bar top cells read as the warning (cells 9–10 lit); no separate alert in 0.1 — §6 |

---

### Void Runes — a third resource, deliberately NOT a band in 0.1

Live db.ascension tooltips prove a **Void Rune** stack mechanic exists:
Psychic Leech (800452) "Consumes 2 Void Runes", Entropic Strike (805111)
"generating 2 Void Runes", plus checker machinery (`Void Rune` 301185,
`At Least 2/3/6 Void Runes`, decay timers) — the Tinker Scrap shape. **No
Sidekick page mentions Void Runes anywhere** — playstyle, rotation and
resource paragraphs are all silent — so no cited claim says any spec is
*played around* them; they read as a talent-line sub-mechanic (the godblade
Entropic Strike / Seething Void line, a corruption Void Rune line). The
layout standard forbids rendering a resource the cited play does not spend,
so 0.1 ships no Void Rune band; §6 carries it. The stale skillbook rows that
mention runes ("Wrath of The Black Empire … Consumes All Void Runes",
500724) are superseded by the live 800413 tooltip ("draining 20 Insanity").

## 2. Talent-driven rotation changes

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| Horrorbolt Volley | talent; counter/window aura 255020, castable id UNRESOLVED | after 3 Horrorbolts, Horrorbolt **transforms into Horrorbolt Volley for 15 s** | corruption filler becomes 5-target AoE | tracked as the WINDOW, not the button: buff-row entry + PROC_GLOW on Horrorbolt keyed to the "Horrorbolt Volley" aura (by name + 255020). A `["Spell Known"]` face-swap needs the castable id, which neither DB resolves — §6 |
| Eldritch Smite | (godblade tree) | **transforms Blade of the Empire into Smite of the Empire** | godblade/heretic melee builder changes button | Smite of the Empire has NO id in either DB (exiles MISSING) — transform face deferred, §6. Blade of the Empire icon stays; wrong-face cost is art only |
| Voidseeker | (godblade tree) | Netherstrike "resets to become an any-health execute" | execute weave | reset shows as the cooldown clearing on the Netherstrike icon — no new surface; §6 whether a distinct execute spell id exists |
| Twilight Horror (capstone, was Dark Whispers) | 560977 Passive | Casting Horrorbolt grants **Inspired Malice** | corruption capstone proc | buff-row entry by name (aura id unresolved — §6); active-only, harmless untalented |
| Herald of the Depths | 92131 | converts the Insanity cap into a self-buff window; **drains Insanity when it ends** | heretic: "let it ride to 100" INVERTS the cap rule | buff-row entry; the stack-bar top cells stop being a warning under it — noted, not automated, in 0.1 (§6) |
| Dreadnought (L10) | (spec passive) | "Reaching 100 Insanity no longer causes Total Madness" | dreadnought: cap is safe | same treatment: no per-spec cap-warning variance in 0.1; the bar renders the same cells |
| Strength of the Black Empire | (dreadnought L40) | Dreadnought transform becomes a void monstrosity with damage reduction | transform window | buff-row entry by name; active-only |
| Glimpse of Madness | 500719 | Obliteration Beam cd cut + applies Madness to all struck | corruption AoE cadence | no new surface (cd trigger reads the live cd) |
| Dark Revelation | (corruption L40) | periodic damage can reset Gaze of C'Thun + 5 Insanity | free Gaze weaves | Gaze icon's cd trigger shows the reset happening; no new surface |
| Blade of Yogg-Saron | (heretic tree) | Blade of the Empire hits apply Black Blood to allies | heals ride the builder | target band already carries Black Blood |
| Dark Infusion moved to class tree | 500721 | all specs can take the pre-load heal | emergency layer on non-heretics | inventory Specs widened to all; utility row |
| Blade of C'thun / Eldritch Smite of C'thun | (corruption tree) | Blade of the Empire gains cd + Insanity + resets >60 | corruption melee-hybrid weave | cooldown icon only if cited; not in the cited caster loop — inventory `ignore`-or-offensive per row note |

Every adaptation reads correctly both with and without the talent: window
buffs are active-only, PROC_GLOW keys on auras that never fire untalented,
and no main-row button is gated on a talent id.

---

## 3. Pets

- [x] Does this class summon a pet? **Yes — three kinds.**
      (1) PERMANENT minions: **Summon: Faceless Servant** 500709
      (corruption, "until dismissed", party crit aura) and
      **Summon: Mindbender** 803062 (heretic, "until dismissed",
      periodically heals allies). (2) A LONG-CD temporary:
      **Summon: Faceless Destroyer** 572115 (godblade, 10 min cd, 1 min).
      (3) TOTEM-SHAPED tentacles, "only 1 Old God Tentacle active":
      Tentacle of C'Thun / N'Zoth / Y'shaarj / Yogg-Saron, Eldritch
      Tentacle, Eldritch Obelisk — placed, act on their own, duration-capped.
- [x] Pet abilities the player presses? **Godblade only**: Abyssal Command
      (tentacle slam) and Cosmic Ooze (tentacle root) are real buttons that
      command the deployables — ordinary cooldown-row icons (the Tinker
      `Bot:` pattern). The permanent minions have no player-pressed commands
      in any scrape.
- [x] Pet buffs/debuffs to track? Tentacle of Yogg-Saron's ally
      healing-received aura is a heretic buff-row candidate (by name);
      nothing else surfaces in the scrapes.
- [x] Does pet presence gate the rotation? **Corruption and heretic, softly**:
      a dismissed Faceless Servant is a silently missing party crit aura; a
      missing Mindbender is missing ally healing. That is the
      missing-imbue shape → **NO PET alert** per the Stormbringer/Tinker
      mechanism (aura on `unit="pet"`, `showOnMissing`, gated on knowing the
      summon). ⚠️ Both alerts need a pet-carried aura id, and none is proven
      — the alerts are DEFERRED to §6 rather than shipped on a guess (a
      wrong id = permanently-on alert, the known failure). 0.1 ships the
      summon buttons as long-term/utility icons instead.
- [x] Pet resource bar? **No.** Nothing in any scrape gives any summon a
      resource.

| Pet | Summoned by | Duration | Track | Where |
|---|---|---|---|---|
| Faceless Servant | Summon: Faceless Servant 500709 (corruption) | until dismissed | summon known + presence (§6) | long-term band icon; alert deferred |
| Mindbender | Summon: Mindbender 803062 (heretic) | until dismissed | same | long-term band icon; alert deferred |
| Faceless Destroyer | Summon: Faceless Destroyer 572115 (godblade) | 1 min / 10 min cd | cd icon | offensive row |
| Old God Tentacles (one at a time) | Tentacle of C'Thun / Eldritch Tentacle / Tentacle of N'Zoth / Y'shaarj / Yogg-Saron | seconds | cd icons; Yogg ally aura by name (heretic buff row) | offense/utility rows per spec |
| Eldritch Obelisk | Eldritch Obelisk (godblade) | zone | cd icon | offensive row |
| Manifestations of Y'shaarj | Dark Calling (auto-proc <35% hp) | 10 s | nothing (no button) | — |

---

## 4. Primary damage source and how the main bar reads

**Resource envelope, all four specs, identical height:** the Insanity meter
(aura 500706) as a **10-cell `stack_bar` at `step=10`** — the Stormbringer
Static pattern; the 40/60/80 thresholds read as cell counts — with the
**mana bar** under it. Both width-locked to the main row. Insanity sits
nearest the main row because every spec's decisions hang on it.

| Spec | Primary damage | Main row, in press order (cited) | Icons | Resource |
|---|---|---|---|---|
| Corruption | Insanity-fed shadow casting (Horrorbolt engine) | Darkwither → Horrorbolt → Gaze of C'Thun → Ancient Curse → Wrath of The Black Empire → Obliteration Beam | 6 | Insanity cells + mana bar |
| Dreadnought | shield-tank attrition (Shieldtoss leech engine) | Dreadfall → Twilight Shieldtoss → Entropic Slam → Sermon of Dread | 4 | Insanity cells + mana bar |
| Godblade | Strength melee build-spend (Hammer of Twilight) | Voidforged Edge → Netherstrike → Hammer of Twilight → Rift | 4 | Insanity cells + mana bar |
| Heretic | damage-that-heals (Malevolence/Black Blood) | Malevolence → Blade of the Empire → Gaze of C'Thun → Eldritch Mending → Void Shield → Sanity Tap | 6 | Insanity cells + mana bar |

Press orders quoted from the cited rotation text, with two prose names
resolved through `resources/aliases-cultist.json`:
- corruption solo/dungeon rotation: "Open at range with Darkwither …
  Horrorbolt is your filler … Weave Gaze of C'Thun on cooldown, and Ancient
  Curse … Drop Wrath of the Black Empire as your big hit, and use
  Obliteration Beam once you're above 60 Insanity".
- dreadnought: "Open on approach with Dreadfall … keeping Twilight
  Shieldtoss cycling … Spend Insanity with Void Strikes"; **"Void Strikes"
  has no castable record and resolves to Entropic Slam** (the only
  Insanity-draining melee spender in the kit — aliases file); Sermon of
  Dread from the dungeon text (AP shred upkeep). Void-Enhanced Shield and
  Bulwark of Shadow turned out to be passives (tooltips, §6) so they are
  not buttons; the pressed absorb is Dreadnought (567524, 45 s).
- godblade: "Keep Voidforged Edge on cooldown … weave Netherstrike … dump
  Obliteration … set up with Rift". **"Obliteration" resolves to Hammer of
  Twilight** (Twilight's Call/Warrior of the Old Gods evidence — aliases
  file). "Open at range with Eye of N'zoth" is unbuildable: no castable id
  exists in either DB (§6), so the row ships four wide.
- heretic dungeon sustain priority: "Black Blood kept up > Blade of the
  Empire > Malevolence > Gaze of C'Thun > instant Eldritch Mending >
  Void Shield" (Malevolence leads the row as the Black Blood applicator),
  Sanity Tap as the ever-present Insanity→mana valve.

`CD_PER_ROW` from the NARROWEST main row: 4 icons ⇒ row_w(4) = 182 px;
`28w − 2 ≤ 1.2 × 182 = 218.4` allows 7 — confirmed after the build with
`tools/rowwidths.py`.

Target band, own-only, per spec:
- **Corruption** (`helpful=False`): Darkwither (healing-taken shred DoT),
  Ancient Curse, Madness (by name — Obliteration Beam stamp), Mind Rot (by
  name).
- **Dreadnought** (`helpful=False`): Sermon of Dread (AP shred; by name).
- **Godblade** (`helpful=False`): Rift (by name), Empire's Grasp snare
  untracked (short).
- **Heretic** (`helpful=True` — the healer): Black Blood (by name — the HoT
  your damage pays), Abyssal Covenant (500701 link), Void Shield (by name),
  Dark Infusion pre-load (by name).

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Insanity cap (all specs but talent-excepted) | Total Madness backfire: 500% max-health shadow damage | stack-bar cells 9–10 lighting IS the warning (top of a 10-cell bar) | cells are plain aura_stacks thresholds; aura id 500706 in-game verify is §6 |
| Insanity thresholds (>40 godblade, >60 corruption/dreadnought) | Shadow of the Void drops / empowered Beam + Embrace the Void unavailable | cell count readable at a glance; threshold cells lit | same |
| Sitting on unspent Insanity (heretic) | mana starvation — Sanity Tap unspent | Sanity Tap in the main row; `spellUsable` desaturate when <20 Insanity | check 9 (desaturate condition present); §6 whether Insanity cost gates IsUsableSpell |
| Presence dropped | silent throughput loss, spec-wide | long-term band icon (active-only: absent = empty slot) | §6 — a true missing-alert needs the aura id proven |
| Whispers missing pre-pull | missing Kings-mould raid buff | long-term band icon | same shape as every blessing row |
| Abyssal Covenant not on the tank (heretic) | tank loses the damage-link heal; "recast every instance change" | target-band entry + long-term icon | dot_bars by name; §6 aura visibility on ally |
| Black Blood not maintained (heretic) | main HPS engine idle | target band `helpful=True` with refresh glow | dot_bars refresh_at; §6 the ally-carried aura name |
| Eldritch Mending hard-cast (heretic) | mana trap; "fire it off the procs" | PROC_GLOW on Eldritch Eye / Malevolent Power proc auras | §6 proc aura ids |
| Volley window skipped (corruption) | AoE burst window wasted | PROC_GLOW on Horrorbolt during the window + buff-row entry | §6 window aura id (255020 candidate) |
| Off-cooldown damage cds | throughput | urgency tiers ANDed `onCooldown == 1` | check 9, *no bare expirationTime tier* |
| Off-GCD abilities | phantom sweep reads as unavailable | `use_showgcd` off (derived from cooldown-abilities-cultist.json) | check 10, both directions |
| Unaffordable spends | icon reads "press me" while unpayable | `spellUsable == 0 → desaturate` | check 9 |
| GCD clipping | wasted globals | GCD sweep on on-GCD icons | check 10 |
| DoT drops (Darkwither, Sermon of Dread…) | sustain + rider debuffs lost | target band bars `%p` + refresh glow | dot_bars refresh_at; §6 names |

No missing-buff ALERT band ships in 0.1: the two candidates (missing
Presence, missing permanent pet) both hang on aura visibility this fork
cannot prove from scrapes, and a wrong-id inverse alert is permanently on
screen — the exact Runemaster reminder failure. Both are §6 items for the
in-game pass; the long-term band carries the state passively meanwhile.

---

## 6. Open questions — the in-game checklist

- [ ] **Insanity aura id 500706**: both DBs carry it ("Reaching 100 Insanity
      will cause you to enter Total Madness", dur −1) and it is the only
      meter-shaped candidate, but decoys exist (`Insanity Bracket Checker`
      681258, `+1 Insanity Stack` 681103, `Sanity` 500727 heretic drain,
      bracket markers 680601-4). Only the game separates the stack-carrying
      aura from its machinery — the Pyromancer Ember Trigger trap. Watch the
      cells fill.
- [ ] **Eldritch Shock 808036 spec membership**: changelog says a new class
      spender; db tree filing says Heretic (filing ≠ membership). Shipped
      Specs=all, offensive row. Confirm which specs learn it.
- [ ] **Horrorbolt Volley castable id**: 255020 is rank "Stack Counter"
      (dur 15 s) — matches the transform window, unproven. Neither DB has a
      castable Volley row. If the game grants a real replacement spell,
      capture its id and wire the reaper transform-face pattern; until then
      the window renders as a buff + glow keyed to 255020/name.
- [ ] **Smite of the Empire id** (Eldritch Smite transform): no id in either
      DB. Capture in game; until then Blade of the Empire keeps its face.
- [ ] **Presence auras**: does an active Presence show as a player aura
      under its own castable id (C'Thun 803339 rank "Presence" dur −1 looks
      right; Y'Shaarj/N'Zoth/Yogg-Saron unproven)? Settles both the
      long-term icons and the deferred NO PRESENCE alert.
- [ ] **Permanent pet alert ids** (Faceless Servant, Mindbender): find an
      aura the PET carries (the Stormbringer 806010 shape) or confirm
      `unit="pet"` absence behaviour; then ship NO PET alerts for
      corruption/heretic.
- [ ] **Inspired Malice aura id** (Twilight Horror capstone): no id in
      either DB (name-miss in exiles). Buff row matches by name; confirm the
      aura name string in game.
- [ ] **Corrupting Whispers proc aura**: 92130 is the L10 Specialization
      passive; the proc aura it grants ("grant you Corrupting Whispers")
      needs its id. Buff row matches by name meanwhile.
- [ ] **Herald of the Depths window**: 92131 is the passive; whether the
      ride-to-100 WINDOW is a distinct visible aura decides its buff-row
      entry. Matches by name meanwhile.
- [ ] **Black Blood ally aura name/id**: 804113 is rank UNUSED; the live
      HoT the heretic target band tracks by name — confirm the on-ally aura
      is literally named "Black Blood".
- [ ] **Malevolent Power / As The Prophecy Foretold proc auras**: ids
      unresolved; PROC_GLOW keys by name.
- [ ] **Sanity Tap usability below 20 Insanity**: does `IsUsableSpell` go
      false (desaturate carries the cue) when Insanity < 20 on this fork?
- [ ] **Black Blood refresh rule**: changelog 2026/07/31 says duration CAN
      now be refreshed; the Sidekick page still teaches the old rule. The
      refresh-glow threshold on the heretic target band assumes refreshing
      is now correct play. Confirm.
- [ ] **Shadow of the Void aura 300277**: rank None, dur unknown — confirm
      it is the visible stacking buff (godblade buff row).
- [ ] **Dreadnought/Herald cap immunity**: both specs neutralize Total
      Madness; the 10-cell bar still colours nothing special at the top in
      0.1. If in-game reads confirm the windows, consider per-spec cap
      styling (feedback item, not a defect).
- [ ] **Component-id corrections** (CROSSCHECK dict): Obliteration, Void
      Strikes, Void-Enhanced Shield, Eye of N'zoth, Ancient Curse, Presence
      of Y'Shaarj — castable ids resolved from db.ascension tooltips during
      the sweep; confirm each icon sweeps in game.
- [ ] **"Void Strikes" = Entropic Slam alias**: the dreadnought main row
      ships Entropic Slam where the prose says Void Strikes
      (aliases-cultist.json). If the game has a real Void Strikes button,
      capture its id and swap the slot.
- [ ] **"Obliteration" = Hammer of Twilight alias**: same shape for the
      godblade spender; confirm the button's real name in game.
- [ ] **Eye of N'zoth castable id**: cited godblade opener, no castable in
      either DB (573313 Proc / 802728 Passive / 1885214 flavor). Capture in
      game; until then the godblade main row is four icons.
- [ ] **Void-Enhanced Shield / Bulwark of Shadow / Eldritch Bastion**:
      Sidekick presents all three as dreadnought's defensive layers; every
      data tooltip says passive (block-value scaling 572025, >80-Insanity
      threshold aura 572758, +15% shield armor 560091/561336). Shipped as
      `ignore`; if any is a real button in game, add it to the defensive
      row.
- [ ] **Dreadnought 567524**: shipped as the pressed 45 s absorb transform
      (tooltip). Confirm the button exists on a dreadnought bar and the
      transform state aura name for the buff row.
- [ ] **Void Runes**: live tooltips prove the mechanic (Psychic Leech
      consumes 2, Entropic Strike generates 2, aura candidate 301185 with
      At-Least-N checkers up to 6) but no cited source says any spec is
      played around it, so no band ships. If in-game play or feedback shows
      a rune-centred build, add a small stack_bar on the proven aura id.
- [ ] **Wrath of the Black Empire generates vs drains**: Sidekick's
      corruption Resource text says it GENERATES Insanity; the live 800413
      tooltip says it DRAINS 20. The icon renders either way; confirm which
      is live (affects only §1 prose, not the pack).
- [ ] **Hedged inventory rows**: every Notes cell containing "reads like" /
      "could read" / "no other tooltip names it" — collected at review time;
      see the inventory. Feedback and the in-game sweep are their checklist.
