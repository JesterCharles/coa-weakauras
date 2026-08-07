---
title: Runemaster — class pack requirements (retroactive)
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, runemaster, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[runemaster-mechanics]]"
  - "[[runemaster-retro]]"
---

# Runemaster — requirements

⚠️ **RETROACTIVE.** Runemaster shipped and was verified in game at **v1.7**
*before* the requirements template existed. This document is therefore not the
plan the pack was built from — it is the plan reconstructed afterwards, and
sections 1–5 are answered by `notes/runemaster-mechanics.md`, the shipped pack
and `notes/runemaster-retro.md` rather than by research done up front.

It exists for two reasons: the phase gate needs one, and the changelog triage
below has to live somewhere durable.

---

## −1. Changelog triage — 11 entries, all resolved

`changelog_watch.py --class runemaster --pages 6`, newest **2026/08/03**.
Every entry categorised; **3 needed action, 8 did not.**

| Entry | Date | Category | Verdict |
|---|---|---|---|
| **"Swapped Mind Over Matter in the Class Tree with Battle Engravings in the Talent Tree, meaning all Runemasters can now take Battle Engravings."** | 08/03 | tree move | ⚠️ **ACTED.** `Battle Engravings` (706674) had **no inventory row at all**. Added, role `ignore` — db.exil.es marks it Passive and it modifies Ley Lock (removes cast time, −0.5s duration) rather than being a button. `Mind Over Matter` (802669) already `ignore`, unaffected |
| "Mind Wrath … now affects 2 targets up from 1." | 08/03 | number | no action. 800757 is a Passive that modifies Ley Lock; already `ignore`, not rendered |
| "Overloaded Flame Glyph duration 5s → 12s, tick 1s → 1.5s" | 07/31 | duration | ⚠️ **ACTED.** No inventory row. Added (520107, `ignore`). The scrape **already carries dur=12000**, so the data is post-rework and nothing tracked was stale |
| "Unleashed Flame Glyph duration 6s → 10s" | 07/31 | duration | ⚠️ **ACTED.** No inventory row. Added (520097, `ignore`). Scrape already carries dur=10000 |
| "Runic Explosion base damage increased ~25%." | 07/31 | number | no code change, but see the citation note below — a 25% damage change is the shape that moves press priority |
| "Tempo now additionally increases the damage of Runic Brand." | 07/31 | passive damage | no action. 807172 `ignore` |
| "Hoarfrost AoE Range 5 → 8 yds." | 07/31 | number | no action |
| "Runic Brand AP scaling 30% → 28%, +15% SP scaling" | 07/31 | number | no action |
| "Fist of the Ancients AP scaling 65% → 58%, +20% SP scaling" | 07/31 | number | no action |
| "Primordial Strength AP→SP conversion 25% → 30%" | 07/31 | number | no action |
| "There is work being done to improve the Weapon Enhancements." | 07/31 | notice | no action **yet**, but watch it: Weapon Engravings are load-bearing here — the `NO ENGRAVING` alert, the long-term band and six imbue auras all key off them. A rework lands squarely on the pack |

**Why the three additions matter even though none of them renders.** The
inventory is the coverage floor: `tests/run.py` check 13 asserts every ability
the pack *references* has a row, and the reverse direction — an ability the
game has that the inventory has never heard of — is exactly how Runemaster
once shipped rendering Runeblade and Runic Explosion while its skillbook listed
neither. A row costs nothing and makes the next scrape idempotent.

### Not `--accept`ed, and why

One question is genuinely open: **Runic Explosion's +25% may change press
order** in Engravement's main row. Press order is `controlledChildren` order
and is load-bearing. The authority for it is
`resources/citations-runemaster.json`, whose Sidekick records predate
2026/07/31 — so by `citations.py`'s own staleness rule they no longer speak to
the current balance.

Re-scrape the three Sidekick pages and re-import citations before accepting.
Accepting now would mark 11 entries "seen" while that question is unresolved,
which is the exact misuse the process forbids.

---

## 0. Ability surface — both databases

✅ **Swept.** `crossdb_sweep.py runemaster` — **286/286** rows with an id asked
of db.ascension.gg. 283 `record`, **3 `no-record`**, all three resolved without
removing anything:

| Ability | ID | Resolution |
|---|---|---|
| `Etch` | 805623 | Inventory says **"verified in game"**. The client outranks a database — keep |
| `Wild Steam` | 802632 | Same — **"verified in game"**, renders on Engravement's offense row. Keep |
| `Manastorm` | 502614 | db.exil.es' own description is literally "Deprecated". Already `ignore` |

This is the worked example for the rule that **`no-record` is a stop, not a
delete-list**.

---

## 1. Mandatory buffs

| Buff | Source | Why | Where |
|---|---|---|---|
| Weapon Engravings (6 elements) | class | the whole proc economy keys off the imbue | ✅ long-term band + `NO ENGRAVING` alert |
| Etchings (3, + Greater) | class | flat throughput, set before the pull | ✅ `NO ETCHING` alert |
| Runic Tattoos (6 elements) | class | attunement stance; Water sustains mana, Fire is damage | ✅ long-term band + the mana-driven swap prompts (1.3) |
| Glyph chain (Frost/Flame/Arcane) | Glyphic | the spec's segmented resource | ✅ `seg_bar` |
| Proc set (Power Overwhelming, Spellfire Runes, Windsage, Surging Slash, …) | talents | "press this now" | ✅ `PROC_GLOW` |

---

## 2. Talent-driven rotation changes

| Talent | What changes | WA adaptation |
|---|---|---|
| **Echoes of Eternity / Runelord** | **replace** Zenith 712325 with 712389 | ✅ `variants` in `in-game-verified.json` → non-exact trigger + no spellknown gate on the base. Fixed in 1.3 after the icon *vanished* from the row |
| **Elemental Mastery** | **transforms** Primordial Blast into Ignis / Hydros / Lithos / Stratus | ✅ `spell_swap()` — native `["Spell Known"]` on each replacement. Took four releases; see the research gate |
| Glyphic Overload, Eye of the Beholder | procs | ✅ `PROC_GLOW` |

---

## 3. Pets

**None.** Runemaster summons nothing. Answered explicitly, per the template.

---

## 4. Primary damage source and main-bar read

| Spec | Primary damage | Main row | Icons |
|---|---|---|---|
| Glyphic | glyph-chain detonation | Glyphic Ruin, Primordial Blast, Thaumaturgy, Elemental Burst, Runic Obliteration | 5 |
| Engravement | Runic Brand + engraving procs | Runeblade, Fist of the Ancients, Runic Brand, Primordial Blast, Runic Explosion | 5 |
| Riftblade | two-handed melee weaving | Runeblade, Smolder, Fracture, Hoarfrost, Hurricane, Primordial Blast | 6 |

`CD_PER_ROW = 9`, derived from the narrowest row (5 → `row_w(5)` = 228px).

---

## 5. Miss-handling

Fully built — this class is where the escalation vocabulary came from:
`spellUsable → desaturate`, GCD sweep, 20s timer → 10s glow → 5s urgent tint,
`PROC_GLOW`, active-only buff row, and the two missing-buff alerts. Enforced by
`tests/run.py` checks 9 and 10.

---

## 6. Open questions

1. **Runic Explosion press order** after the +25% — blocked on re-scraping
   Sidekick and re-importing citations. This is what holds the changelog
   `--accept`.
2. **Weapon Enhancement rework** announced 07/31, not yet shipped. When it
   lands it touches the engraving alert, the long-term band and six auras.
