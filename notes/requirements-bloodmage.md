---
title: Bloodmage pack requirements
date: 2026-08-08
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, bloodmage, requirements]
sources:
  - "[[class-requirements-template]]"
  - "resources/sidekick-bloodmage-sanguine.md (scraped 2026-08-07)"
  - "resources/sidekick-bloodmage-accursed.md (scraped 2026-08-07)"
  - "resources/sidekick-bloodmage-eternal.md (scraped 2026-08-07)"
  - "resources/sidekick-bloodmage-fleshweaver.md (scraped 2026-08-07)"
  - "resources/coa-bloodmage-skills.json (sidekick-data.js snapshot 2026-08-02)"
  - "resources/exiles-bloodmage.json (db.exil.es llms.txt digest, 2026-08-07)"
---

# Bloodmage — class pack requirements

Class 20, load token `SONOFARUGAL`. Four specs: **Sanguine** (ranged caster
DPS, health-cost economy), **Accursed** (form-swap melee DPS), **Eternal**
(tank/bruiser in Eternal Curse), **Fleshweaver** (healer, pure Rage economy).
Roles are Sidekick-cited, pending in-game — see §4 and
`resources/spec-roles.md`.

The class identity is the **health-cost economy**: on two of four specs the
player's own health bar is a spent resource. See §4/§5 for what the pack does
and does not claim about that.

---

## −1. Changelog — run FIRST

- [x] changelog scanned 2026-08-07 (`changelog_watch.py --class bloodmage
      --pages 6`, 600 entries over dates 2026/07/31..2026/08/07), newest
      bloodmage entry: `2026-07-31`
- [x] every mechanical entry triaged below
- [x] `--accept` only after the entries are acted on

12 bloodmage entries, all dated 2026/07/31. Triage:

| Entry | Category | Where it lands |
|---|---|---|
| Hemal Excision curses now last max 30s | behaviour tweak | no WA change — the siphon is a utility CD; no curse-timer display planned |
| Hemal Excision no longer castable on pets/guardians/non-players | behaviour tweak | no WA change |
| Hemal Excision no longer preserved through map changes | behaviour tweak | no WA change |
| Bloodbolt rage cost 40 → 30 | number tweak | ignore |
| Wicked Howl CD 3 min → 2 min | number tweak | **corroborated**: the 2026-08-07 audit reads 2 min, so the scrape post-dates the change |
| Transgression no longer requires Insatiable, 30s → 15s, no free Vampiric Fang | behaviour rework | §1 — Transgression tracked as an on-me aura only; no duration is hard-coded, the aura's own `%p` carries whatever the server says |
| Class tree repathed (Alacrity ↔ Dark Curse / Bloody Sacrifice) | talent filing | no WA change |
| Eternal Curse is now instant cast | behaviour tweak | no WA change — stance tracked as an aura, not a cast |
| Forbidden Power → spell pen from armor pen | number tweak | ignore |
| Rage (talent) +10% SP from AP | number tweak | ignore |
| Blood Hunt +10 Expertise | number tweak | ignore |
| Blood Shards now Spellshadow, benefits from Dark Hunt | number/school tweak | ignore |

No *replaced with* / *now reads* / *now baseline* / *new spell* entries.
Snapshot staleness: `sidekick-data.js` mtime 2026-08-02 and the four spec
pages were scraped live 2026-08-07 — everything in the corpus post-dates the
newest bloodmage changelog entry (2026-07-31).

---

## 0. Ability surface — both databases

Inventory seeded from `coa-bloodmage-skills.json` (250 skillbook rows → 254
inventory rows after audit enrichment), enriched by
`cooldown-abilities-bloodmage.json` (37 cooldown rows, 19 off-GCD, 0
unresolved) + `exiles-bloodmage.json` (596 spells, 227 multi-rank) +
`spell-meta-bloodmage.json`.

- [x] every inventory row with an id (240/240) asked of BOTH databases
      (`crossdb_sweep.py bloodmage`; buildlog `crossdb` step)
- [x] 4 `no-record` rows re-asked BY NAME with tooltip reads, verdicts in the
      Notes cells: **Atherann's Anguish** other-id (ascension 570146, same
      hemoplague tooltip); **Infuse** present on ascension as CoA-flagged
      Damage/Heal components (681404/802156); **Curse of the Worgen** →
      `ignore` (ascension's only name-hit 560409 is a hidden party aura — a
      different thing wearing the name; exiles tooltip empty; Vampirism
      "disables" it); **Gore Barrage** → `buff` (ascension 807777 says it is
      now a stacking aura spent by Bloodmoon Blast/Veinburst; the exiles
      castable 504114 is one-DB-only and does not ship as a button)
- [x] deprecated/unused/placeholder names filtered or role=ignore with the
      marker quoted (`Hemomancy` "REMOVED", `Nostrum`/`Suture`
      rank=Deprecated, `Blood Prodigy` rank=DEPRECATED, `Blood Moon`
      rank="Aura (UNUSED)"); exiles surplus stays in `## Candidates`

---

## 1. Mandatory buffs

**From the class kit:**

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Shield family** — Blood Shield / Coagulated Shield / Vital Shield (fleshweaver), Shadowfang Shield (sanguine) | class/spec | "Only 1 Shield can be active at a time" (three fleshweaver tooltips); 30-min self-buffs a caster sets pre-pull and quietly loses sustain without | long-term band + **NO SHIELD** alert, spec-gated to sanguine and fleshweaver only (accursed/eternal have no Shield ability — a class-wide alert would nag them permanently) |
| **Eternal Curse** (stance) | eternal | "Stay transformed via Eternal Curse as your default grinding stance"; the tank's armor/Stamina/threat and the whole transformed kit hang on it | long-term band + **NO CURSE** alert, eternal-gated |
| **Cursed Form state** (Blood Curse / Accursed Form / Final Embrace / Transgression / Sanguine Essence) | accursed, sanguine, fleshweaver | which mode you are in decides which half of the kit works ("Requires Mortal Form" / "Requires Cursed Form" on most buttons) | on-me row, active-only (form flips are deliberate on these specs, so an *alert* would be wrong — only eternal treats a form as the default state) |
| **Offerings** (Bloodsoaked / Greater Bloodsoaked / Sanguinary / Greater Sanguinary / Slaughterhouse) | sanguine | 30-min ally buffs, set once | long-term band |
| **Bloodthorns / Greater Bloodthorns** | fleshweaver | 30-min ally thorns, named in the dungeon pre-pull text | long-term band |
| Party auras (Dark Presence, Invigorated Flesh — sanguine; Dark Frenzy, Dark Sigil — accursed; Eternal Presence, Rejuvenating Shadows — eternal; Blood-Cursed Armor — fleshweaver) | spec passives | "Does not stack with similar effects" | long-term band of the owning spec (active-only; if the passive's aura is hidden the icon simply never shows — §6) |

**From talents / procs (the "press this now" set):**

| Buff | Spec | Why | Where |
|---|---|---|---|
| **Thirst** (stacks to 10, then flips into Insatiable) | sanguine | THE spec meter: "Dump Thirst via Vampiric Fang around 3-5 stacks … never let it hit 10" | 10-cell stack bar in the resource envelope (by name); **Insatiable** as a red on-me entry |
| **Insatiable** (self-penalty at 10 Thirst) | sanguine | "flips into a self-inflicted output penalty ticking every 1.5 sec" | on-me row, red — the visible cost of missing the Vampiric Fang dump |
| **Pooled Vitality** (stacks to 10, consumed by empowered heals) | fleshweaver | "your big Rage-cost heals consume 10 stacks to fire empowered"; Gorge banks 10 | 10-cell stack bar in the resource envelope (by name) |
| **Wretched** (Essence Harvester: Vampiric Fang reset below 35%) | sanguine | free reset window | PROC_GLOW → Vampiric Fang |
| **Monstrous Hunger** (next 6 Bloodfang Bites empowered) | eternal | "pop Monstrous Hunger" burst-sustain window | PROC_GLOW → Bloodfang Bite (aura by name; the castable has no id — §6) |
| **Final Embrace** window (Bloodfang Bite → Crimson Maw) | accursed | the improved-form burst | PROC_GLOW → Crimson Maw (§2) |
| **Saturating Sutures** (next Sanguine Mend free) | class tree | "15% chance to reduce the cost of your next Sanguine Mend by -100%" | PROC_GLOW → Sanguine Mend (aura name unverified — §6) |
| Blood Rush (20% haste 5s), The Cup Runneth Over, Sovereignty, Ultra Instinct, Sanguine Scripture, Gore Barrage stacks | various | proc windows the talent build takes | on-me row, active-only |

**From abilities:** running cooldown buffs (Blood Craving, Sacrificial Rite,
Bloodsurge, Endure the Curse, Eternal Resolve, Ironhide, Blood Pact, Wicked
Howl, Apotheosis, Red Thirst …) render in the on-me row so "active" reads
differently from "unavailable".

---

## 2. Talent-driven rotation changes

This fork resolves NO spell overrides (`Prototypes.lua:3806`). Findings from
the four talent trees and kit texts:

| Talent | What changes | Rotation impact | WA adaptation |
|---|---|---|---|
| **Final Embrace** (accursed L59) | "transforming your Bloodfang Bite into Crimson Maw" for its 20s window | burst window with a different button | NOT a Spell Known swap — the transform is a 20s aura window, not a learn event. Both icons exist; **Crimson Maw glows while Final Embrace is up** (PROC_GLOW). Wrong on neither build: without the talent the aura never exists and Crimson Maw's icon still gates on its own id |
| **Vampirism** (sanguine) | "Teaches Embrace of the Vampyr, but disables the use of Curse of the Worgen" | swaps one utility for another | Curse of the Worgen is already out (crossdb §0); Embrace of the Vampyr resolves in neither scrape's skillbook — §6, nothing drawn for either side |
| **Transgression** (sanguine) | temp Cursed Form, casts free Vampiric Fang — changelog 07/31: no longer requires Insatiable, 15s | a proc window, not a button | on-me aura by name; no duration hard-coded |
| **A Pointed Death** (sanguine) | "Born in Blood gains 2 additional charges" | charge economy on a spell not in any scrape | §6 — Born in Blood resolves in neither DB digest nor skillbook; nothing drawn |
| **Blood Debt** (eternal) | "Removes the cooldown from Bloodfang Bite, but increases its Rage cost" | filler becomes spammable | no WA change — the cooldown swipe reads correctly either way (no CD = no swipe), desaturate on `spellUsable` carries the cost half |
| **Crimson Hymn** (sanguine) | "Removes the cooldown of your Dark Liturgy" | spam window | no WA change — same shape as Blood Debt |
| **Rotclaw** (eternal) | "2 Charges, 6 sec recharge" (tooltip) | charge economy | CHARGES = {Rotclaw: 2} |
| **Puncturing Fangs** (accursed) | skillbook desc says it is a Bloodmoon Blast modifier; the rotation text presses it as a form button | main-row membership depends on which is true | shipped in the main row per the cited rotation; §6 records the tooltip conflict |
| **Dark Blood / Unchained / Dark Frenzy** (form-cost modifiers) | reduce costs / allow moving casts / GCD reduction in form | none change what is pressed | no WA change |
| Choose-one pairs (Leeching Tome/…, Swarm of Flies/…, Coated In Darkness/…, Blood-Cursed Weapons/Armor) | passive modifiers | none change what is pressed | no WA change (Blood-Cursed Armor is a longterm aura row) |

Pack reads correctly untalented: proc-glow displays are active-only (no proc
= no glow), charge counts fall back to a plain cooldown, and talent-granted
buttons live in cooldown rows gated on their own spell id where gateable, so
an untalented character never sees a button they do not have.

---

## 3. Pets

1 pet-ish mention in the corpus (Hemal Excision "can no longer be cast on
pets" — other people's pets). Answered explicitly:

- [x] Does this class summon a pet? **No.** No tame, no permanent companion,
      no pet bar in any spec page. The closest things are **Animated Blood**
      (60s blood-worm summon — a DPS cooldown, uncontrolled) and eternal's
      **Call of the Darkwing** procs (server-side flyby, not a unit the
      player owns).
- [x] Pet abilities the player presses? **No.**
- [x] Pet buffs/debuffs to track? **No.**
- [x] Does pet absence gate the rotation? **No** — no NO PET alert.
- [x] Pet resource bar? **No.**

Animated Blood renders as an ordinary offensive cooldown icon; nothing else
is needed.

---

## 4. Primary damage source and the main row

Spec roles (Sidekick-cited, pending in-game — `resources/spec-roles.md`,
provenance block there; ally-heal denial is the discriminator, not
heal-mention counts, because the whole class lifesteals):

| Spec | Primary damage/healing | Main row, in press order (cited from the Rotations text) | Icons | Resource |
|---|---|---|---|---|
| Sanguine | health-cost Shadow nukes ramped by Thirst | Bloodmoon Blast → Atherann's Anguish → Sanguine Rupture → Vampiric Fang → Valanar's Vengeance → Keleseth's Calamity | 6 | Rage (power 1) + Thirst 10-cell stack bar |
| Accursed | form-swap melee (Reave/Ravenous Strike) fed by caster-form Rage builders | Reave → Ravenous Strike → Puncturing Fangs → Bloodbolt → Veinburst → Hemoburst | 6 | Rage (power 1), solo full-height |
| Eternal | transformed bites + cleave threat | Ravenous Bite → Bloodfang Bite → Rotclaw → Claw Sweep | 4 | Rage (power 1), solo full-height |
| Fleshweaver | Rage-fuelled instant heals | Sanguine Mend → Dark Liturgy → Crimson Tide → Heartbreak → Blood Tap → Vampyr's Kiss | 6 | Rage (power 1) + Pooled Vitality 10-cell stack bar |

Main-row derivations, one line each, from the spec pages' Rotations sections:

- *Sanguine dungeon:* "Keep your DoTs rolling: Atherann's Anguish planted for
  its detonation … Filler: Bloodmoon Blast and Sanguine Rupture on cooldown
  … dumped into Valanar's Vengeance and Keleseth's Calamity as your Thirst
  stacks cheapen them. Dump Thirst via Vampiric Fang before it caps at 10."
  Bloodmoon Blast leads as "the main filler". Malediction, Shadow Hemorrhage,
  Hematophage and Taldaram's Torment are DoT-shaped and live on the target
  band, where the refresh cue is.
- *Accursed:* transformed priority "Reave (best value when the target is
  bleeding, below 35%, or you're behind it) > cleave freely > Ravenous Strike
  spammed in the gaps"; caster phase "weave Bloodbolt, Veinburst and
  Hemoburst on cooldown to build Rage". Both modes share the row; the loaded
  form decides which half is castable and desaturation carries it.
- *Eternal:* "Ravenous Bite and Bloodfang Bite carry both your threat and
  your self-healing. Rotclaw keeps a bleed and your Rage up, and Claw Sweep
  spreads threat across the pack." Blood Howl is per-pull (utility), not
  rotational.
- *Fleshweaver dungeon:* "Sanguine Mend as your primary tank/spot heal. Dark
  Liturgy links a hurt member through Blood Bond … Crimson Tide and
  Hemoglobe when the group is clustered"; solo names Heartbreak as the opener
  and "Blood Tap in particular, as your Rage and Pooled Vitality builders",
  with "Vampyr's Kiss to refund a chunk of Rage". Hemoglobe is a 3-min CD →
  offensive (healing CD) row, not a main slot.

**Resource envelope:** every spec runs on **Rage** (`power`, type 1) and the
class spends **no mana anywhere** ("Pure Rage economy, with no mana anywhere
in the kit" — fleshweaver; "no mana pool is spent" — sanguine; "Pure Rage,
no mana" — eternal; accursed "Rage, but lopsided"). So: no mana bar,
anywhere — a vestigial bar costs prime space. Sanguine adds the **Thirst**
stack bar and fleshweaver the **Pooled Vitality** stack bar (both `aura_stacks`,
10 cells, matched by NAME because the buff ids are unverified — §6);
accursed and eternal get a solo full-height Rage bar.

**Health as a resource** (sanguine, fleshweaver): the player's own health bar
is spent by most casts. The pack does NOT draw a health bar — the default UI
and every unit-frame addon already own that surface, and duplicating it next
to the main row buys nothing. What the pack DOES show about the health
economy: the Thirst bar (the rate limiter on health spend), the Insatiable
red entry (the cost of overcasting), and a **LOW BLOOD** alert at ≤35% health
(the kit's own threshold: Essence Harvester, Blood Scent, Enduring and
Mineralization-style passives all key off 35%) gated to the two
health-spending specs. What it cannot show: "this cast would be unsafe" —
health-cost desaturation has no native trigger (`spellUsable` reflects
mana/rage affordability, not health margins) — recorded in §5/§6.

`CD_PER_ROW` derives from the narrowest main row: eternal's 4 icons,
row_w(4)=182px, `28w − 2 ≤ 1.2 × 182` → **7**. Confirmed by
`tools/rowwidths.py` against the built packs.

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Vampiric Fang before 10 Thirst | Insatiable self-penalty ticking every 1.5s | Thirst stack bar filling + **Insatiable** red on-me entry; Wretched PROC_GLOW on the reset | stack-bar mechanism proven in game (Chronomancer Sands/Fragments, Pyromancer Ember); Thirst/Insatiable aura NAMES are §6 — if wrong, cells stay dark, which is visible on the first import |
| Shield dropped (sanguine/fleshweaver) | 30-min sustain quietly gone | NO SHIELD alert (show-on-missing over the Shield family) | the NO BOON/NO SKIN shape, in-game verified on Pyromancer/Primalist packs; bloodmage aura names pending in-game |
| Eternal Curse dropped (eternal) | tank loses armor/Stamina/threat stance | NO CURSE alert + stance in long-term band | same alert shape; the stance aura name is §6 |
| Overcasting health (sanguine/fleshweaver) | "Over-casting without dumping Thirst … can kill you" | **LOW BLOOD** alert at ≤35% player health | `health_trigger` percent check — same native Health prototype the resource bars use; threshold cited from the kit's own 35% passives |
| Monstrous Hunger window wasted (eternal) | 6 empowered Bloodfang Bites lost | PROC_GLOW on Bloodfang Bite | glow mechanism proven in game; aura name §6 |
| Final Embrace window wasted (accursed) | Crimson Maw burst lost | PROC_GLOW on Crimson Maw while Final Embrace runs | same |
| DoTs drop (sanguine: Taldaram's Torment / Malediction / Hematophage / Shadow Hemorrhage / Twisted Magic) | ramp restarts from zero | target band with time remaining + refresh glow | dot_bars refresh_at proven on four shipped classes |
| Blood Veil / Bloodthorns / Blood Rituals absent on the target (fleshweaver) | tank takes the hit uncovered | target band helpful=True on the CURRENT target (VuhDo owns raid frames) | same mechanism, helpful side proven on Chronomancer Time / Primalist Grovekeeper |
| Unaffordable press (rage-dry cold start, fleshweaver) | "an ambush at 0 Rage leaves you no shield and no panic button" | desaturate on `spellUsable == 0` | check 9 |
| Off-GCD icons sweeping falsely | 19 of 37 cooldown abilities are off-GCD | `use_showgcd` off for those | check 10, derived from `cooldown-abilities-bloodmage.json` |

---

## 6. Open questions

- [ ] `UNKNOWN — Thirst / Insatiable / Pooled Vitality buff ids: the stack
      bars and the red entry match by NAME (the resolvable ids are the L10
      teaching passives, the Aeon-of-Resilience shape). One in-game read
      settles all three; if the buff names differ the cells stay dark, which
      is visible immediately.`
- [ ] `UNKNOWN — Eternal Curse castable id: 92114 is the L10 teach; the
      candidate castable is 804518 'Eternal Curse Shapeshift' (component-smell
      name). The pack tracks the STANCE AURA by name and gates nothing on
      804518, so nothing breaks either way.`
- [ ] `UNKNOWN — Monstrous Hunger has NO id in either database yet is cited
      as a rotation cooldown. No button ships; the PROC_GLOW window matches
      the aura by name. If a castable id surfaces, it earns an offense-row
      icon.`
- [ ] `UNKNOWN — Ravenous Bite resolves only as 560365 'Ravenous Bite
      (Packleader)' (Rank 1). Shipped on that id in the eternal main row;
      an in-game tooltip would settle whether the live button is another id.`
- [ ] `UNKNOWN — Puncturing Fangs: skillbook desc reads as a Bloodmoon Blast
      modifier, the rotation text presses it as a form button. Shipped as a
      main-row button per the cited rotation; first in-game look decides.`
- [ ] `UNKNOWN — Accursed Form (504710) and Hunt (704656) resolve to
      passive-rank ids while the rotation presses them; icons ship without
      own-id gates (class+signature gate only) so a wrong id cannot hide
      them.`
- [ ] `UNKNOWN — Sanguine Essence: the rotation says 'drop into Sanguine
      Essence' but 505188 is rank=Passive; the castable is unresolved. The
      form AURA is tracked by name on the on-me row; no button ships.`
- [ ] `UNKNOWN — Gore Barrage: ascension says stacking aura, exiles says 8s
      castable. Shipped as an on-me stack aura by name only. Feedback or
      in-game read decides whether a button returns.`
- [ ] `UNKNOWN — Dissipate (553278): 40s CD in the audit, empty tooltip in
      both scrapes. Ships as a utility icon on the id evidence alone.`
- [ ] `UNKNOWN — party-aura passives (Dark Presence, Invigorated Flesh, Dark
      Frenzy, Dark Sigil, Eternal Presence, Rejuvenating Shadows,
      Blood-Cursed Armor): if 3.3.5 implements them as hidden dummy auras
      (the Eternity Warper shape) the long-term icons never show. Active-only
      displays, so the failure is an absent icon, not a lie.`
- [ ] `UNKNOWN — Born in Blood (A Pointed Death's target) and Embrace of the
      Vampyr (Vampirism's grant) resolve in no scrape; nothing drawn.`
- [ ] `UNKNOWN — Sated (Fleshcraft's debuff on the ally) is a harmful aura on
      a friendly target; the helpful=True target band cannot carry it.
      Deliberately not drawn in 0.1; feedback decides if it earns a slot.`
- [ ] Hedged inventory rows (bulk-cleared per the production default) are
      listed in the buildlog `inventory-reviewed` note; the in-game sweep is
      their checklist.
