---
title: Starcaller pack requirements
date: 2026-08-08
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, starcaller, requirements]
sources:
  - "[[class-requirements-template]]"
  - "resources/sidekick-starcaller-moon-guard.md (scraped 2026-08-08)"
  - "resources/sidekick-starcaller-moon-priest.md (scraped 2026-08-08)"
  - "resources/sidekick-starcaller-sentinel.md (scraped 2026-08-08)"
  - "resources/sidekick-starcaller-warden.md (scraped 2026-08-08)"
  - "resources/cooldown-abilities-starcaller.json (db.exil.es audit, 2026-08-08)"
  - "db.ascension.gg ?spell=<id>&power tooltips, 2026-08-08"
---

# Starcaller — class pack requirements

Class 26, token `STARCALLER`, **four** specs: **moon-guard** (tank),
**moon-priest** (healer), **sentinel** (ranged DPS), **warden** (melee DPS).
Roles from citable Sidekick kit statements (`resources/spec-roles.md`
provenance note, 2026-08-08); moon-priest is the one healer, so
`helpful=True` target-band scope applies to it and to nothing else.

The class-wide spine, twice over:

1. **Dual resource on every spec** — Energy funds the filler attacks
   (Celestial Strike / Celestial Cleave / Moon Arrow / Huntress Shot /
   Sentinel Glaive), while everything with impact is priced as a **percentage
   of maximum mana**, and the fillers pay the mana back. All four Sidekick
   Resource paragraphs say "dual resource" in those words.
2. **Scattered Stars** — a 30 s, 4-stack (extendable by Galaxy and spec
   passives) Arcane debuff **on the enemy**, built by builders and procs in
   every spec and consumed by every spec's spenders (Starsweep, Lunar Lance,
   Starfire Shot, Trueshot, Umbral Blade, Moonflow-during-Eclipse). It lives
   on the TARGET, not the player, so it renders in the target band with a
   stack count, not in the resource envelope.

Class-wide stance systems, both "shares a cooldown with other X":
- **Aspects** (Cosmos, Stars, Warden, Huntress, Moonwell, Goddess — spec kits
  vary which are learnable): passive proc layers, one active at a time.
- **Aegis spells** (Celestial, Astral, Infused): short defensive windows on
  one shared cooldown, each draining % max mana.

---

## −1. Changelog — run FIRST

`python3 tools/changelog_watch.py --class starcaller --pages 6` →
**13 NEW entries, all dated 2026/07/31**, scanned 2026-08-07/08.

- [x] changelog scanned, newest starcaller entry: `2026-07-31`
- [x] every entry triaged (below)
- [x] `--accept` only after this table was written and acted on

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| Moon Guard level 50 passive merged into level 30; new lvl 50 passive: Light of Elune absorb-to-mana | 2026/07/31 | passive rework | no WA surface (passives, no button) |
| Celestial Cleave castable without a target, +1 yd range, wider cone, targeting fixes | 2026/07/31 | mechanics | no WA surface (same button, same id) |
| Warden level 30/40/50 vertical-line talents shifted position | 2026/07/31 | tree position | no WA surface |
| Lunar Combatant reworked: INT from Strength, weapon damage from spell power | 2026/07/31 | passive rework | no WA surface; **Sidekick kit text still shows the OLD tooltip** ("effectiveness of consuming Scattered Stars") — flagged stale, §6 |
| Celestial Glaives + Lunar Combatant effects combined into the Celestial Glaives node | 2026/07/31 | talent merge | no WA surface (both passive); same staleness flag |
| Starfire Shot mana scaling reduced | 2026/07/31 | numeric | no WA surface |
| Sentinel lvl 20 passive now 10% INT → Ranged Crit | 2026/07/31 | passive rework | no WA surface |
| **NEW talent** (old Tyrande's Training slot): Starfire Shot gains a Lunar Eclipse effect — a Burn DoT that blocks stealth/invis | 2026/07/31 | new talent | sentinel target band candidate: the Burn DoT (aura name/id UNKNOWN — §6). Harmless untalented (active-only) |
| Tyrande's Training moved to lvl 50 spec passive; also affects Trueshot; 25% crit vs burning | 2026/07/31 | passive rework | no WA surface |
| Warden's Blade under Aspect of the Goddess spawns **Elune's Cradle** — a HoT circle healing 8 allies / 3 s | 2026/07/31 | new effect | moon-priest note: ground zone, not a unit aura — nothing trackable on the current target; §6 records it |
| Lunar Lance (and Moonlit Lancer DoT) now Spellfire instead of Arcane | 2026/07/31 | school change | no WA surface (same ids) |
| Can now wear daggers | 2026/07/31 | itemization | no WA surface |
| Touch of Moonlight now properly scales with healing power | 2026/07/31 | numeric | no WA surface |

**Staleness:** `resources/sidekick-data.js` (mtime 2026-08-02) and the four
spec pages (re-scraped 2026-08-08) both post-date the 2026/07/31 batch, but
the *content* still predates it in at least two places: the Lunar Combatant /
Celestial Glaives kit texts show pre-merge tooltips, and no page mentions the
new Starfire Shot Lunar-Eclipse-Burn talent or Elune's Cradle. The batch is
otherwise passives, numerics and tree positions, so the rotation-structure
claims stand; the two WA-adjacent unknowns are §6 items.

---

## 0. Ability surface — both databases

`tools/exiles.py starcaller` → 481 spells (195 names carry multiple ranks —
spell-meta decides which can be gated). `tools/spellmeta.py starcaller` →
481 ids with rank/cost/GCD/tooltip. `tools/mkabilities.py starcaller` seeded
the inventory; roles assigned by an automated pass 2026-08-08 and cleared in
bulk (production-run.md Pyromancer precedent, provenance recorded in the
buildlog `inventory-reviewed` note), one line of reasoning per Notes cell.

`tools/crossdb_sweep.py starcaller`: see the buildlog `crossdb` step for
the final counts — 100% of inventory rows with an id asked of
db.ascension.gg, every `no-record` resolved in its Notes cell by a name
re-ask against both tooltips, nothing deleted on the verdict alone.

- [x] every inventory row cross-checked against both DBs
- [x] `no-record` rows resolved in the Notes cell
- [x] deprecated/unused/placeholder names filtered (`utility_tables.JUNK`,
      plus the `DEPRECATED` marker rows the audit drops)

**Sweep result (2026-08-08): 238/238 rows with an id checked; 233 record,
5 no-record, all resolved in Notes cells.** Component-id corrections in the
builder's `CROSSCHECK` dict, each read against both tooltips:
- Starburst 704796 (rank "ATS Slow", the slow component) → **801996**
  (full castable: 10% base mana, 20 s cd, the cited AoE builder)
- Avatar of Vengeance 531757/531756 (rank "DoT"/"Teleport" components) →
  **680822** (the official tree's node spellId; full castable, 1 min cd)
- Aspect of the Goddess 801401 (rank "Heal" component) → **802203** (full
  castable Aspect, shared Aspect cooldown)
- Alignment 524702 (desc literally "Deprecated") → **805507** (live
  tooltip verbatim to the sentinel kit text)

No-record resolutions that are NOT cuts (the incomplete-snapshot branch):
Huntress Shot 680220, Moon Arrow 801972, Starfire Shot 801978, Trueshot
520590 — all four are db.exil.es Rank-1 castables with full tooltips, and
801978/520590 are the official ascension.gg tree's own node spellIds;
operator data outranks db.ascension's missing rows. Triggers name-match, so
rank drift is safe. One cut: **Guided Reflexes** (exiles desc "Deprecated"
+ no db.ascension record + not tree-granted — the Manastorm shape; §6 keeps
the in-game look since Starslip's text still references it).

Three 1-hit prose names recorded in `resources/aliases-starcaller.json`:
Astral Armor (Aegis rider, not a cooldown), Essence of the Moonwell (the
Moonwell zone essence; the button is Moonwell 804739), Guided Reflexes.

---

## 1. Mandatory buffs

| Buff | Source (class/talent/ability) | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Scattered Stars** (804378, 30 s, stacks 4+) — ON THE ENEMY | class spine, every spec builds/spends it | every spender's payoff scales per stack consumed; overwriting at cap or spending at 1 both waste | target band (`helpful=False`) with `%s` stack count + `%p`, every DPS/tank spec; moon-priest reads it through Moonflow-during-Eclipse (§6) |
| Active **Aspect** (of the Cosmos / Stars / Warden / Huntress / Moonwell / Goddess) | class stance system, "shares a cooldown with other Aspects" | the whole proc layer rides the active Aspect; moon-guard swaps them mid-fight ("swap into Moonwell before dumping") | long-term band icons (active-only); no missing-Aspect alert in 0.1 — aura visibility unproven, §6 |
| **Aegis windows** (Celestial / Astral / Infused Aegis) | class defensives, shared cooldown | short mitigation windows; "roughly an 8-10 second window with no Aegis where the spec feels squishy" (moon-guard) | buff row (active-only) + defensive icons |
| **Vengeance of Elune availability** | moon-guard: "can only be used after parrying"; Cosmic Vengeance / Lunar Blades widen to block/dodge | a proc-gated hit that expires unused | PROC_GLOW on Vengeance of Elune keyed to its enabling aura (name; id §6) |
| **Moonblade window** | moon-guard talent: "Consuming Scattered Stars has a 15% chance to transform Celestial Strike into Moonblade for 8 seconds" | free mana-refunding devastate window | §2 transform: Spell Known on Moonblade's numeric id |
| **Lunar Phase** (stacking player buff, +1/4 s; crits via Moon Gazing) | moon-priest engine | Rapid Cycle haste per stack; Flash Flood consumes 4; Touch of Moonlight refunds via Eclipse | buff row entry with `%s` stacks (stack-carrying aura id §6 — machinery decoys exist) |
| **Lunar Eclipse** (800386, activatable, usable while casting) | moon-priest passive kit + Moon Priest L10 | "Time Huntress Shot's Lunar Eclipse to make Moonflow free" | utility icon (its own cooldown) + PROC_GLOW on Moonflow while the Eclipse state is up (§6 aura) |
| **Full Moon / New Moon cycle** (Cycle of the Moon) | moon-priest | swings Hand of Elune between more healing and cheaper casts (Full Cycle) | buff row entries by name (active-only, harmless if invisible); §6 aura names |
| **Lunar Resplendence** (mana regen window) | moon-priest/sentinel | "While active, Moon Arrow restores % mana and extends it" | buff row |
| **Shadowsong's Mandate** window | warden burst cd | "chain crits into Warden's Blade procs" | buff row + offensive icon |
| **Avatar of Vengeance** transform | warden cd | Metamorphosis-moment; range + INT buff window | buff row + offensive icon |
| **Starfire Barrage** (sentinel: every 3rd Starfire Shot transforms the button) | sentinel passive | the barrage is the payoff cast | §2 transform: Spell Known on Starfire Barrage's numeric id if castable; else window aura by name (§6) |
| **Alignment** (sentinel: mana refill, damage down, threat nullified) | sentinel cd | cited in Sidekick build notes as the mana panic button | utility icon + buff row |
| **Celestial Form** | moon-priest cd | "crit-and-cooldown burst window ... accelerate your heal cooldowns during a crunch" | offensive(healing) icon + buff row |
| **Aspect of the Goddess** | moon-priest healing amp | "keep active ... turns ranged autos + star consumption into ally healing" | long-term/buff row + healing cd icon |
| **Celestial Mind / Greater Celestial Mind** (ally INT blessing) | class buff | Kings-mould blessing, checked once per pull | long-term band |
| **Elune's Presence** (party temp max health) | class cd | pull cooldown | utility icon |

---

## 2. Talent-driven rotation changes

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| Blade of the Moon (moon-guard tree) | transform target: **Moonblade** | consuming Scattered Stars has 15% chance to **transform Celestial Strike into Moonblade for 8 s** | free 130% WD + mana refund window | `["Spell Known"]` trigger on Moonblade's NUMERIC id — this fork resolves no overrides; both Celestial Strike and Moonblade displays share the slot, exactly one loaded-and-showing (the reaper/chronomancer pattern). If Moonblade's castable id fails `gateable()`, fall back to window-aura by name (§6) |
| Starfire Barrage (sentinel) | transform target: **Starfire Barrage** | every 3rd Starfire Shot **transforms Starfire Shot into Starfire Barrage** | the barrage is the AoE payoff | same Spell Known pattern on Starfire Barrage's numeric id; counter aura (if any) is §6 |
| Cosmic Vengeance / Lunar Blades (moon-guard) | — | Vengeance of Elune usable after block/dodge as well as parry | more Vengeance windows | no new surface — the PROC_GLOW cue fires whenever the enabling aura is up, whichever talent granted it |
| Galaxy (class tree) | — | Scattered Stars +2 stacks (moon-guard build takes it) | deeper spend windows | none — target-band stack count reads whatever the cap is |
| Bright Moon (class tree) | — | Lunar Phase +4 stacks | deeper Phase banking | none — buff-row `%s` reads any count (this is why Lunar Phase is NOT a fixed-cell stack bar) |
| Moonlit Lancer (class tree) | — | Lunar Lance gains a DoT | DoT upkeep on target | target-band entry by name, active-only, harmless untalented |
| NEW 07/31 talent (old Tyrande's Training slot, sentinel) | — | Starfire Shot gains Lunar Eclipse Burn DoT (blocks stealth) | Burn upkeep enables Tyrande's-Training crit | target-band entry by name once the aura name is known — §6; nothing ships on a guess |
| Second Moon (class tree) | — | every 10th Scattered Star consumed launches a comet | passive payoff | no WA surface |
| Moonwell Tides (class tree) | — | Vial of Moonwell Water also heals 25% current mana | CC-break doubles as a heal | no new surface (same button) |
| Shooting Star / Twinkle Toes (class tree) | — | sprint | mobility | utility icon |
| Rally the Sentinels (moon-guard tree) | — | Sentinel Glaive restores mana + applies a Star | glaive joins the mana engine | no new surface (same button) |
| Infused Blades / Stellar Amplification (warden) | — | Astral Blade resets/refunds/free | "burn Astral Blade on cooldown" stays true | cd icon reads the reset; free-cast proc aura is a PROC_GLOW candidate (§6 id) |

Every adaptation reads correctly both with and without the talent: transform
faces are dual displays where only the granted spell's `IsSpellKnown` is
true, window buffs are active-only, and no main-row button is gated on a
talent-only id.

---

## 3. Pets

- [x] Does this class summon a pet? **No combat pet.** Four "summon"
      mentions in the skillbook, none a pet: **Bubble Buddy** (moon-priest,
      untaken water line — a short deployable that mimics your Torrent
      channel; a cooldown button, not a controlled unit), **Celestial
      Steed** / **Huntress Saber** / **Moonchaser Kodo** (mounts; the Saber
      is sentinel's cast-while-moving platform — a utility icon),
      **Geyser** (a water burst, not a unit), **Starlight** (a beam zone),
      **Vigil of the Moon** (a stealth-revealing watcher zone).
- [x] Pet abilities the player presses? **None** — no summon has commands.
- [x] Pet buffs/debuffs to track? **None** carried by a pet unit.
- [x] Does pet presence gate the rotation? **No.** No NO-PET alert.
- [x] Pet resource? **No.**

No pet section. Deployables/mounts render as ordinary cooldown/utility
icons on their owning specs.

---

## 4. Primary damage source and how the main bar reads

**Resource envelope, all four specs, identical fixed height:** the
**Energy bar** (power_type 3, the Barbarian/Felsworn mechanism) nearest the
main row — Energy is the moment-to-moment funding on every spec — with the
**mana bar** (power_type 0) under it. Both width-locked to the spec's own
main row. Scattered Stars is deliberately NOT here: it lives on the enemy,
so it renders in the target band with stacks (`%s`), which also makes it
correct on retarget.

| Spec | Primary damage/healing | Main row, in press order (cited) | Icons | Resource |
|---|---|---|---|---|
| Moon-guard | block/parry-fed Arcane cleave (Starburst/Starsweep engine) | Starburst → Starsweep → Celestial Cleave → Starsunder → Lunar Lance → Celestial Strike | 6 | Energy + mana |
| Moon-priest | % max-mana heals funded by Energy shots | Moonflow → Prayer of Elune → Hand of Elune → Touch of Moonlight → Huntress Shot → Moon Arrow | 6 | Energy + mana |
| Sentinel | ranged arcane build-spend (Scattered Star engine) | Huntress Shot → Moon Arrow → Starfire Shot → Lunar Lance → Trueshot → Starcall | 6 | Energy + mana |
| Warden | mana-drain melee burst (Starsunder/Astral Blade) | Starsunder → Celestial Strike → Astral Blade → Umbral Blade → Sentinel Glaive → Fan of Knives | 6 | Energy + mana |

Press orders quoted from the cited rotation text
(`resources/sidekick-starcaller-*.md`):
- moon-guard solo/AoE: "Starburst > Starsweep > Celestial Cleave >
  Starsweep, repeated … Single target runs the same shape with the other
  pair: Starsunder to build, Lunar Lance to spend"; Celestial Strike is the
  Energy filler ("alternate Energy-funded filler swings").
- moon-priest dungeon: "Moonflow on cooldown (or free during Lunar
  Eclipse), Prayer of Elune for stacked group damage plus a magic dispel,
  Hand of Elune / Touch of Moonlight as tank filler and single-target spike
  coverage. Keep Huntress Shot/Moon Arrow flowing to fund mana."
- sentinel solo: "filler Huntress Shot … Moon Arrow whenever Huntress Shot
  is down … consume stacked Scattered Stars for burst via Starfire Shot,
  Lunar Lance, or Trueshot (2 charges) → on a pack, lead Starcall."
- warden solo (numbered): "2) Open with Sentinel Glaive … 3) Starsunder on
  entering melee … 4) Celestial Strike as your Energy dump … 5) Astral
  Blade on cooldown … 6) Umbral Blade once you have 2-3 Scattered Stars …
  8) Fan of Knives to spread Scattered Stars" — reordered to sustain press
  priority with the melee builders first, opener glaive and AoE knives last.

All four rows are 6 icons ⇒ narrowest row_w(6) = 274 px;
`28w − 2 ≤ 1.2 × 274 = 328.8` allows 11, capped by taste at **9** (the
Runemaster-tested width) — confirmed after the build with
`tools/rowwidths.py`.

Target band, own-only, per spec:
- **Moon-guard** (`helpful=False`): Scattered Stars (804378, stacks),
  Starburst attack-speed slow (by name).
- **Moon-priest** (`helpful=True` — the healer): your HoTs/absorbs on the
  current ally target: Elune's Favor HoT (by name), Moonwater (Rippling
  Moonwater stacks), Bathe stacks, Celestial Mind, Moonwater Blessing,
  Aegis of Neptulon absorb (by name). Enemy target shows nothing helpful —
  correct, VuhDo owns raid frames.
- **Sentinel** (`helpful=False`): Scattered Stars (stacks), Lunar Lance DoT
  (Moonlit Lancer, by name), Starlight root/slow zone untracked (zone, not
  unit aura).
- **Warden** (`helpful=False`): Scattered Stars (stacks), Astral Blade
  amp (by name), Bonds of Justice tether (by name).

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Scattered Stars overcap / spending low | wasted stack damage on every spec | target-band stack count `%s` on the debuff bar | dot_bars stacks text; aura id 804378 confirmed both DBs; in-game visual is §6 |
| Spenders held while stars are up (Starsweep / Starfire Shot / Umbral Blade / Lunar Lance) | the payoff cast idles | cd swipe + desaturate when unaffordable | checks 9/10 |
| Vengeance of Elune window expiring (moon-guard) | free unavoidable AoE lost | PROC_GLOW on the icon while the enabling state is up | §6 enabling aura id; glow keyed by name meanwhile |
| Moonblade window expiring (moon-guard) | free devastate + mana refund lost | transform face swap (Spell Known) + glow | builder prints leaf gates; §6 in-game confirm |
| Aegis gap (moon-guard) | "8-10 second window with no Aegis" | Aegis icons' cooldown escalation tiers (timer 20 s, glow 10 s, urgent 5 s) | check 9, tiers ANDed `onCooldown == 1` |
| Moonflow held during Lunar Eclipse (moon-priest) | free no-cooldown group heal lost | PROC_GLOW on Moonflow keyed to the Eclipse state | §6 the Eclipse state aura; glow keyed by name meanwhile |
| Lunar Phase banked past cap (moon-priest) | haste stacks wasted | buff-row `%s` count | aura2 stacks text; §6 the stack aura id |
| Trueshot charges capped (sentinel) | recharge time wasted | charge count on the icon (CHARGES) | wabuild charge_text; §6 in-game |
| Mana dry (every spec) | burst locked out "at the worst possible moment" (warden text) | mana bar + `spellUsable == 0 → desaturate` on every spend icon | check 9 |
| Off-GCD abilities sweeping falsely | icon reads unavailable after every press | `use_showgcd` off, derived from cooldown-abilities-starcaller.json | check 10, both directions |
| GCD clipping | wasted globals | GCD sweep on on-GCD icons | check 10 |
| Aspect dropped / wrong Aspect | whole proc layer idle (silent throughput loss) | long-term band icons (active-only: absence = empty slot) | §6 — a true missing-Aspect alert needs a proven aura id; deferred |
| Blessing (Celestial Mind) missing pre-pull | INT buff lost | long-term band icon | same shape as every blessing row |
| DoT drops (Moonlit Lancer, Burn) | sustain + Tyrande's-crit rider lost | target band `%p` + refresh glow | dot_bars refresh_at; §6 names |

**No missing-buff ALERT band ships in 0.1** (the cultist precedent): the
candidates (missing Aspect, missing Celestial Mind) hang on aura visibility
no scrape proves, and a wrong-id inverse alert is permanently on screen —
the Runemaster reminder failure. The long-term band carries the state
passively; §6 holds the alert candidates for the in-game pass.

---

## 6. Open questions — the in-game checklist

- [ ] **Scattered Stars aura id 804378 on the enemy**: both DBs carry it
      (30 s, stacking 4) and every kit references it, but applier machinery
      ids exist (572320/572321/706391/804380 "Applier Passive", 804994-5
      comet/CD-reduction components, 680325 PVP modder). Watch the stacks
      fill on a target dummy; confirm own-only matching works (another
      Starcaller's stars must not light your band).
- [ ] **Starburst castable id**: db.exil.es's 704796 is rank "ATS Slow" (a
      component). The name re-ask candidate lands in CROSSCHECK — confirm
      the moon-guard button's real id in game.
- [ ] **Moonblade castable id + gateability**: the Blade of the Moon
      transform face needs a numeric id `IsSpellKnown` answers true for
      during the 8 s window. If the grant is aura-shaped rather than
      spell-grant-shaped, swap to the window-aura pattern.
- [ ] **Starfire Barrage castable id**: same question for sentinel's every-
      3rd-shot transform; also whether a visible counter aura tracks shots
      1-2.
- [ ] **Vengeance of Elune enabling aura**: "can only be used after
      parrying" — find the aura (or usability flip) that marks the window;
      until then the glow keys by name and may never fire (fails invisible,
      not wrong).
- [ ] **Lunar Eclipse state aura**: 800386 is the activatable; the state it
      applies ("your next Lunar Phase spell triggers its Lunar effect")
      needs its aura id for the Moonflow PROC_GLOW.
- [ ] **Lunar Phase stack-carrying aura id**: 524781 is the passive
      generator; decoys 704519 ("4 Stacks of"), 706479 (marker), 680355
      (decrement). Buff row matches by name meanwhile.
- [ ] **Full Moon / New Moon aura names** (Cycle of the Moon): confirm the
      visible aura names for the buff-row entries.
- [ ] **Aspect aura visibility**: does the active Aspect show as a player
      aura under its own castable id? Settles the long-term icons and the
      deferred NO-ASPECT alert.
- [ ] **Aegis running-state auras**: Celestial/Astral/Infused Aegis window
      auras by name — confirm names/ids for the buff row.
- [ ] **Trueshot 2 charges on this fork**: does GetSpellCharges answer for
      it (charge text), or is the recharge invisible?
- [ ] **NEW Starfire Shot Lunar-Eclipse-Burn talent**: aura name unknown —
      changelog-only, no scrape has it. Capture the Burn debuff name/id in
      game, then add the sentinel target-band entry.
- [ ] **Elune's Cradle** (Warden's Blade + Aspect of the Goddess): ground
      HoT circle — probably no unit aura to track; confirm and close.
- [ ] **Lunar Combatant / Celestial Glaives post-merge kit text**: Sidekick
      still shows pre-07/31 tooltips; passives either way, no pack surface —
      re-check after the next Sidekick blob refresh.
- [ ] **Moon-priest untaken water line** (Torrent, Pond, Deluge, Tide
      abilities, Bubble Buddy, Flash Flood, Way of the Naga family): present
      in the spec kit, absent from the taken build and from the cited
      rotation. Shipped as utility/ignore per row; if feedback shows a tide
      build is standard, revisit with a fresh scrape.
- [ ] **Hedged inventory rows** (the `prop?:` set at review time, cleared in
      bulk per production-run.md — 62 rows, mostly no-cost/no-cd effect rows
      proposed `ignore`). The ones that are real buttons but uncited by any
      rotation: Coilfang Cascade (1 min damage-amp cd), Drawstring of Elune
      (2 min range/star amp), Pond / Slipstream / Torrent / Tide Lash /
      Water Bolt-line (the untaken water kit), Lunar Focus (sprint),
      Moonwater Blessing windows. Feedback and the in-game sweep are their
      checklist.
- [ ] **"Essence of the Moonwell" citation claim**: named by the Sidekick
      moon-priest build blob, no record under that name in either DB —
      likely prose for the Moonwell zone (the pack ships Moonwell 804739);
      confirm.
- [ ] **"Astral Armor" citation claim** (moon-guard blob): exiles 806156 is
      a 3 s damage/silence row, not an armor cd — name is likely blob prose;
      no button ships under it.
