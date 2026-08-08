---
title: HUD visualization plan — icon sweep results and the preview-state work ADR-002 implies
date: 2026-08-08
type: plan
status: active
tags: [weakauras, conquest-of-azeroth, site, hud, icons, plan]
sources:
  - "[[ADR-002-hud-visualization]]"
  - "[[pass-2-orchestration]]"
---

# HUD visualization plan

Companion to ADR-002. Section 1 is DONE in this branch; sections 2-3 are the
ordered follow-on work with acceptance signals.

## 1. Icon sweep — done this round

Baseline (2026-08-08, before): 181 unique abilities across 16 classes built
with `inv_misc_questionmark` displayIcon; 512 questionmark tiles across the
published class previews; 96 textures in `misses.json` drawing lettered
placeholder tiles.

| Fix | Where it landed | Count |
|---|---|---|
| id → texture from db.exil.es page `og:image` (client DBC art) | `resources/icon-meta-<class>.json` × 14, `resources/exiles-id-meta.json` (runemaster) | 193 entries, 177 abilities resolved |
| Upstream art collision broken by OVERRIDE (chronomancer precedent) | `build_starcaller.py` (Astral Reconstitution ← spell_nature_astralrecalgroup), `build_tinker.py` (Overclocked Machine ← inv_eng_superchargedengine) | 2 |
| Skillbook-name miss routed through FALLBACK (client art, no runtime override) | `build_templar.py` (Greater Zealous Oath ← templar_buff_1) | 1 |
| Stale deliberate-no-art registers updated | `build_chronomancer.py` NO_UPSTREAM_ART → {Fray Magic}; `build_venomancer.py` → {} | 2 files |
| i.exil.es icons-clean added as last-resort preview-art source | `tools/fetch_hud_icons.py` (PNG → `sips` → jpg) | 90 of 94 misses recovered |
| Preview art cache backfilled for every built pack | `docs/assets/spell-icons/` (+~1,600 jpg), `misses.json` 96 → 6 | |

Verification: all 21 builders rebuilt; the only remaining `no art upstream`
names are the four documented below; the fixture diff was **icon-field only**
(589 displayIcon deltas, 0 other deltas, all transitions FROM questionmark —
scratchpad `hudviz-diff.py`); `python3 tests/run.py` green after
`tests/freeze.py` on the 15 affected classes. mksite NOT run (pass rule) —
the published pages keep their questionmarks until the orchestrator's apply
pass regenerates docs/.

### Documented artless — the honest final state (4)

Both sources were asked per id on 2026-08-08. "no record" on the tooltip
endpoint is the 43-byte `registerSpell(<id>, 0, {})` empty literal
(`ascension-spells.json` `_note`), i.e. db.ascension.gg has no such spell.

| Class | Ability | id | db.exil.es page | db.ascension.gg tooltip |
|---|---|---|---|---|
| barbarian | Wrist Snap | 800383 | og:image IS inv_misc_questionmark | no record |
| chronomancer | Fray Magic | 800053 | page live, NO og:image | no record |
| chronomancer | Shifting Sands | 806317 | page live, NO og:image | no record |
| witch-hunter | Disappear | 805772 | og:image IS inv_misc_questionmark | no record |

These render the client's own trigger art in game (iconSource -1) and a
lettered tile in the preview. Filling one means reading the texture off the
game client — a person's job, same as `icon-wanted.json`.

### Remaining preview-art misses (6, `misses.json`)

`inv_misc_food_wildberries`, `inv_misc_head_turtle_01`,
`spell_holy_blessingofwisdom`, `spell_holy_greaterblessingofmight`,
`spell_holy_sealofblessing` (pre-existing; 404 on all four hosts under these
spellings) and `tempest's call` (stormbringer 560567 — the DBC value
literally contains the apostrophe+space; i.exil.es 404s both raw and
URL-encoded spellings, so the pack carries the true name and the preview
draws the letter).

## 2. Follow-ups the sweep implies (for the orchestrator / next round)

1. **Regenerate the site** (orchestrator apply pass): mksite + publish.
   Acceptance: `grep -c inv_misc_questionmark docs/*/index.html` drops from
   512 to ≤ the 7 artless leaf instances; lettered tiles only on the 4
   artless names + 6 missing textures.
   DONE 2026-08-08 (36c7eea, layout apply pass): pages regenerated with the
   backfilled cache; questionmark refs 512 → 9 (the remaining refs are the
   documented artless leaves whose displayIcon IS the questionmark texture,
   drawn per spec layer).
2. **Correct the icon-wanted record.** `resources/icon-wanted.json`
   `_source_status` says "db.exil.es has no icon field at all" — true of the
   API, false of the pages. Re-sweep its 47 raid-utility ids through the
   page og:image route (same probe as this round, cached in
   `tools/spellchk/`). Expectation from this round's 183/183 hit rate: most
   resolve. Acceptance: icon-wanted count shrinks; each survivor carries
   page-level evidence.
3. **Runemaster/chronomancer icon-meta parity.** Runemaster still routes art
   through `exiles-id-meta.json` + `icons="legacy"` (`build_runemaster.py:189-192`);
   every other class is on `icon-meta-<slug>.json`. Converge during engine
   extraction. Acceptance: one file shape, `id_meta_file` parameter deleted.
4. **`fetch_icons.py` regex bug.** `/icons-clean/([^"\')]+?)\.png` drops any
   texture with parentheses (`novart_magicspell_(74)_border`). Harmless today
   (tool is runemaster-legacy) but the pattern reads as reusable. Fix to
   `(.+?)\.png` + basename/trailing-dot normalisation as in this round's
   probe. Acceptance: re-running it on 801105 yields the novart texture.

## 3. Preview state rendering — recommended, ranked (recommend-only this round)

Per ADR-002: static truth first; no timed animation on the page. Costs are
for `tools/mksite.py` + `tools/hud.py` + `docs/assets/site.css` (the apply
pass owns those files, not this agent).

| # | Item | What | Cost | Acceptance signal |
|---|---|---|---|---|
| 1 (DONE 36c7eea) | Semantic tile roles | `hud.py` derives per-leaf capabilities from the decoded pack (urgency conds present / proc-glow cond / desaturate cond / kind) → `data-role` + modifier classes on each preview tile | Build-time only; ~30 lines in hud.py `emit`, ~10 in mksite. No runtime cost | Every tile in a rebuilt page carries `data-role`; roles match `wapack.py` emission (spot-check one class: count of proc tiles == PROC_GLOW entries loaded for that spec) |
| 2 | Proc-glow affordance | Tiles with the proc role get a static golden ring + halo (pack proc colour 1.0,0.95,0.5); slow ~2s opacity pulse gated on `prefers-reduced-motion: no-preference` | CSS only (~12 lines); depends on 1 | Proc-capable tiles are visually distinct at rest; `prefers-reduced-motion: reduce` shows the static ring only |
| 3 | Hover state-card | Hover/focus on a tile lists its state ladder ("sweeps on cooldown · timer <20s · glow <10s · urgent <5s · grey when unaffordable"), from the role data | CSS + ~20 lines JS; JS-off fallback = extend the existing `title` text (zero JS, already wired) | Card text matches the escalation ladder in [[layout-standard]] for a cd tile; buff/resource tiles say their own states |
| — | NOT: animated cooldown sweep, GCD sweep, desaturate demos, urgency cycling | Claim live state a static page is not in; 150+ tiles × infinite animation | — | Reserved for the editor as per-tile "preview this state" toggles (ADR-003/004 surface) |

Editor tie-in: item 1 is the semantic layer the in-browser editor needs to
select and describe tiles by meaning; it pays for itself even if 2-3 never
ship.
