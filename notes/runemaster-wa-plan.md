---
title: Runemaster WeakAura — steal vs build plan (rev 2, post-review)
date: 2026-07-27
type: note
status: budding
tags: [weakauras, runemaster, conquest-of-azeroth, plan]
sources:
  - "[[runemaster-mechanics]]"
  - "[[wa-import-string-format]]"
---

# Runemaster WeakAura — what to steal, what to build

One pack, `Runemaster [CoA]`, covering all three specs.

**Rev 2** after an independent review against the Sidekick ability kits. Rev 1 had the
tattoo element list wrong (Ice vs Frost), misread Glyphic Overload, and made the Riftblade
sigil predictor the headline feature when Sidekick states plainly that Riftblade "is a
straight two-handed melee spec, **not** an attunement or sigil builder." Priorities below
reflect the corrections.

## Steal

| Thing | Stolen from | Why it transfers |
|---|---|---|
| Export envelope (`m`/`d`/`c`/`s`/`v`) | all four community auras | Confirmed shape for Ascension's WA 5.21.2 fork |
| `aura2` trigger with `useName` + `auranames` | Rohendave's Runemaster aura | Accepts a name **or** a numeric ID as a string |
| `item` / Weapon Enchant trigger keyed by enchant *name* | Rohendave's Engravings group | Only way Weapon Engravings are exposed |
| `spell` / Cooldown Progress trigger | Rohendave + Templar Pack | Standard, works as retail does |
| `custom` Lua trigger (`custom_type`, `events`, `custom`) | Templar Pack | Confirms custom Lua is allowed; API is 3.3.5a (`arg9`/`arg12` CLEU, `UnitBuff`, `GetSpellInfo`) |
| subRegion stack (`subbackground`/`subtext`/`subglow`/`subborder`) | Templar Pack | Modern subregion schema confirmed |
| `dynamicgroup` auto-layout | Rohendave's cooldown groups | Handles a variable row of icons |

Retail-pattern reuse per spec:

- **Glyphic ← Arcane Mage.** Stacking builder + detonate. Layout transfers nearly unchanged.
- **Engravement ← Enhancement Shaman.** Weapon-imbue uptime, random proc readouts, and a
  target mark consumed by a filler — all solved layouts.
- **Riftblade ← Frost DK / Enhancement.** Once the sigil system is correctly demoted, the
  real core (charge-based filler + every-Nth-cast counter + reset procs) maps cleanly onto
  existing retail templates. Rev 1's "nothing transfers" claim was an artifact of aiming at
  the wrong mechanic.

## Build from scratch

**1. Spec gating.** Not optional. Shared-kit and cooldown displays do *not* self-filter, so
each spec's rows sit in a group whose trigger is custom Lua:
`GetSpellInfo("<signature spell>") ~= nil`. Returns nil on 3.3.5a for unknown spells.

**2. Riftblade Runeblade beat.** The headline. Charge count (3, 6s recharge), a
**cast-count-to-3 counter** for the three payoffs that land together (Runic Omen, Surging
Slash, Riftblade's mana return), and the reset procs around it — Spellfire Runes (Smolder
reset, 100% off Warpdagger) and Windsage (next 3 Runeblades strike extra). Needs a CLEU
custom trigger counting `SPELL_CAST_SUCCESS` on Runeblade, because nothing exposes the
every-3rd beat as an aura.

**3. Engravement Marked: Runic Brand.** Stacks (up to 3 with Leyborn) + the 8s clock + a
"spend with Runeblade now" cue, since the mark is consumed by Runeblade rather than
self-detonating. Paired with a loud **Power Overwhelming** reset cue (35% proc).

**4. Elemental Carving readout.** Four random outcomes off Fist of the Ancients that the
player is expected to *bank and spend*. Which one is live must be visible.

**5. Glyphic stack + chain state.** Scroll of Magic / Glyph Master stack to 3 and want
maintaining. The chain display must handle **all three glyphs up at once** (Glyphic
Overload generates all three) and multi-stage jumps from Runic Obliteration.

**6. Riftblade Sigil → Runestone predictor.** Kept, demoted to secondary and gated so it
only appears for a character that actually has the blades. Still genuinely without a retail
analogue. The "dead combination" warning must be driven by *which Runestone passives are
known*, not hard-coded to two, because an under-built character has more than two.

**7. Frozen-target check.** Cross-spec damage multiplier (Glyphic Destruction doubles
Glyphic Ruin into Frozen; Frost Spectre/Fracture crit guarantees). Cheap, high value.

**8. Raid-buff presence.** Runes of Quickness / Leyline Disturbance — Sidekick's own pitch
for the class is that the group gets a haste aura "just from you being there," which makes
a silently-missing aura the most expensive possible failure. Cheapest useful display here.

## Deliberately not built

- No DPS meter, boss timers, or gear checks.
- No `load.class_and_spec` gating (value `64` collides with retail Frost Mage).
- No missing-imbue *rotational* warning — engravings last an hour; one small persistent
  setup icon is the right weight. The dynamic half (proc-chance windows: Zenith,
  Uncovered Engravings, Convergence) is what gets built instead.
- No elaborate tattoo stance bar. Tattoos are set pre-pull; one indicator suffices.

## Open risk

Nothing here has been verified against a running client. Unverified inferences, all of
which fail visibly (a display that simply never fires) and are one-field fixes in the WA
editor:

- Sigils are exposed as trackable player auras named `<Element> Sigil` at all.
- A 3-sigil cap, and that Elemental Burst requires exactly three.
- Aura names match spell names (`Marked: Runic Brand`, `<Element> Carving`, `Transcribing`).
- Enchant strings are `<Element> Engraving` — verified for Fire/Ice/Earth/Air/Water/Arcane
  from a working aura, so this one is solid.
- Name collisions (documented in [[runemaster-mechanics]]) mean a few triggers should move
  to IDs once IDs can be read in-game.
