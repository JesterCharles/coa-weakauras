---
title: ADR-002 — HUD preview visualization: icon truth first, then state, then motion
date: 2026-08-08
type: adr
status: accepted
tags: [weakauras, conquest-of-azeroth, site, hud, icons, adr]
sources:
  - "[[pass-2-orchestration]]"
  - "[[layout-standard]]"
  - "[[wa-visual-vocabulary]]"
---

# ADR-002 — HUD preview visualization

## Context

The class page's HUD preview (`tools/mksite.py hud_preview`, `tools/hud.py`)
is a to-scale drawing of the pack: every display at its real resolved
geometry, with the real spell art where cached. Its job is "what lands on
your screen and what does it mean" — and it is the surface the coming
in-browser editor will edit on (pass-2-orchestration, agents C/D).

Two gaps, one per half of this ADR:

1. **Art truth.** 181 unique abilities across 16 classes rendered
   `inv_misc_questionmark` in the built packs — 512 grey question-mark tiles
   across the published previews (`grep -c inv_misc_questionmark
   docs/*/index.html`, 2026-08-08). The repo's standing belief was that
   db.ascension.gg is the only art source and these gaps were permanent
   (commit `e9ac974`: "db.exil.es returns 22 keys per spell and not one of
   them is an icon").
2. **State truth.** In game, a pack icon is never just art: it carries a
   cooldown sweep, a GCD sweep, escalation glows, a proc glow, desaturation
   and tints — seven meaning-bearing states (`tools/wapack.py cd_icon`,
   :640-830; [[wa-visual-vocabulary]]). The preview draws none of them, so it
   under-communicates what the pack actually does. The owner has decided
   (pass-2 decisions table): research and recommend animations only;
   implement later only where cheap CSS covers it.

## Decision

### 1. db.exil.es spell PAGES are an art source, and the icon gap closes through them

The "no icon field" finding was about db.exil.es's JSON API. Its rendered
spell pages publish the client's own DBC texture name in `og:image`:
`https://i.exil.es/coa/static/icons-clean/<texture>.png` (verified on the
cached Firecrawl scrape of spell 801105 — Frost Prison →
`novart_magicspell_(74)_border` — and on 183 fresh scrapes, 2026-08-08, every
one returning a texture). Because it is the DBC value, it is BY CONSTRUCTION
the art the client draws — which resolves the Hasten dilemma
(`build_chronomancer.py` NO_UPSTREAM_ART: db.ascension had no art, the game
draws a boot, a guessed placeholder drew a clock; exil.es serves
`nhi_magicspeed_border`, the boot).

Applied: 193 id→texture entries added to the per-class `icon-meta-*.json`
files (exiles-id-meta.json for runemaster), 177 of 181 abilities resolved.
Two genuine upstream art collisions surfaced by the duplicate-art check were
broken by builder OVERRIDEs, the documented remedy (chronomancer precedent):
Astral Reconstitution / Cosmic Presence share `inv_cosmicvoid_buff`
(starcaller), Overclocked Machine / Machine Synergy share
`nhi_tech_steammachine_border` (tinker). One name-mismatch case (Greater
Zealous Oath: inventory carries the skillbook name, the live spell is Greater
Gift of Zeal 680306) went to templar's FALLBACK, which does not override the
client at runtime. Four abilities are **documented artless** — evidence in
the plan file — and that is their honest final state.

`i.exil.es/coa/static/icons-clean/` also SERVES those textures, so it joined
`tools/fetch_hud_icons.py` as the last-resort source (PNG → sips → jpg). 90
of 94 preview misses recovered — including the tattoo_*, weapon_engraving_*
and wd_* families the tool's docstring called "custom art that exists only on
the Ascension client". misses.json: 94 → 6.

### 2. Preview state rendering: semantic tiles first, then two cheap CSS cues; no timed animation

The preview is a RESTING snapshot, not a simulation. A cooldown timer, a live
GCD sweep or a countdown-driven escalation cannot be true in a static page —
animating them would show a state the pack is not in, which fails the "what
lands on your screen and what does it mean" test. What CAN be true statically
is **which states each tile is capable of**, and that is what the preview
should say. Ranked (full costing in the plan file):

1. **Semantic tile classes** (prereq, build-time only). `hud.py` already has
   the decoded pack; whether a leaf has urgency conditions, a proc-glow
   condition, a desaturate condition, or is an aurabar/segment is derivable
   at build time. Emit `data-role` on each tile. Zero runtime cost; it is
   also the semantic layer the editor needs to make tiles selectable by
   meaning.
2. **Proc-glow affordance** (CSS only). Tiles whose leaf carries a proc-glow
   condition get a static golden ring + soft `box-shadow` halo in the
   pack's proc colour (1.0,0.95,0.5), with a slow ~2s opacity pulse under
   `prefers-reduced-motion: no-preference`. This is the pack's single
   loudest cue ("press this NOW") and the one in-game visual that IS
   animated all the time it is active (ButtonGlow marching ants,
   `LibCustomGlow-1.0.lua:588-682`). A pulse honestly represents "this tile
   glows when its proc is up" without claiming a live proc.
3. **Hover state-card** (CSS + ~20 lines JS, or `title` extension for JS-off).
   Hovering a cooldown tile lists its ladder: "sweeps on cooldown · timer
   <20s · glows <10s · urgent <5s · grey when unaffordable". States are per
   tile and already known from (1). Teaches the vocabulary exactly where the
   player is looking; doubles as the editor's inspection surface.

Explicitly NOT recommended:

- **Animated cooldown sweep** (CSS `conic-gradient` wipe). Cosmetic here: a
  looping sweep on a static preview claims a live cooldown that does not
  exist, and 150+ tiles × infinite animation is real paint cost. Belongs in
  the EDITOR on a selected tile as a "preview this state" toggle, not on the
  page.
- **GCD sweep**. Micro-timing (0.5-1.5s on this server) invisible at 26-44px
  preview scale; meaning only exists relative to a cast that is not
  happening.
- **Desaturate-on-hover demos, urgency colour cycling**. State theatre; they
  animate through states the icon is not in, which is the same lie as the
  sweep, with less payoff.

## Alternatives considered

- **Leave the questionmarks and rely on the client's own art in game**
  (chronomancer's original NO_UPSTREAM_ART position, `build_chronomancer.py`
  :68-73 pre-change). Right call while the only fillers were guesses; wrong
  once the client's own texture NAME is readable from exil.es og:image. The
  packs still defer to the trigger at runtime (`settle_icon_source`,
  `wapack.py:1771` — iconSource stays -1), so the fix only changes what the
  preview/options list shows, and it now shows the same art as the game.
- **Animated GIF previews** (wago.io's approach — [[site-layout-comparables]],
  retrieved 2026-08-08). Truthful motion, but hand-captured per class per
  spec × 21 classes, unmaintainable on every pack revision, and useless as an
  editor surface. The generated preview is the project's differentiator;
  keep investing there.
- **Live WA simulation in JS** (decode + run triggers on a timeline). The
  editor round may want a "simulate" toggle eventually; as a site preview it
  is a game engine nobody asked for.
- **Static state badges instead of hover cards** (tiny glyphs on each tile).
  Rejected for noise: 150+ tiles × up to 4 badges destroys the geometry the
  preview exists to show. The hover card carries the same facts at zero
  resting-state cost.

## Consequences

- 177/181 missing-art abilities now carry the client's own art in pack data;
  packs rebuilt, `tests/run.py` green, fixtures refrozen for the 15 affected
  classes. Published previews still show the old questionmarks until the
  orchestrator's mksite pass regenerates `docs/` (mksite is out of this
  agent's scope by the pass rules).
- db.exil.es is promoted from "no art at all" to the SECOND art source, above
  db.ascension.gg for truth (it is the DBC value) — the plan file proposes
  updating `icon-wanted.json`'s `_source_status` claim and re-sweeping the
  raid-utility page's 47 artless ids through it as follow-up.
- `fetch_hud_icons.py` gains an i.exil.es fallback (macOS `sips` dependency,
  same machine every build has run on). ~1,600 newly cached textures under
  `docs/assets/spell-icons/` (the committed-cache pattern the tool already
  established).
- The recommended preview work is deliberately ordered so item (1) is pure
  build-time data that the editor (ADR-003/004) consumes regardless of
  whether (2)/(3) ever ship.

## Sources

- `tools/wapack.py:640-830` (cd_icon escalation/proc/desaturate), `:1771`
  (settle_icon_source), `:1843-1848` (no-art report)
- `tools/build_chronomancer.py` NO_UPSTREAM_ART + OVERRIDE comments;
  `tools/build_tinker.py` / `build_starcaller.py` OVERRIDE precedents
- WeakAuras-Ascension @ 5741c0c (recloned 2026-08-08):
  `RegionTypes/Icon.lua:334,478-494` (cooldown frame, reverse),
  `GenericTrigger.lua:2617-2627` (GCD substitution),
  `Prototypes.lua:4083-4111` (onCooldown / spellUsable),
  `SubRegionTypes/Glow.lua:226-245`,
  `Libs/LibCustomGlow-1.0/LibCustomGlow-1.0.lua:588-682` (ButtonGlow anatomy)
- github.com/Stanzilla/LibCustomGlow README (Firecrawl, 2026-08-08) — glow
  type parameters
- db.exil.es spell pages via Firecrawl (2026-08-08): 183/183 probes returned
  an `og:image` icons-clean texture; per-id evidence in the plan file
- Second brain: [[wa-visual-vocabulary]], [[site-layout-comparables]]
- Commits `e9ac974`, `65f4d80` (the prior art-sweep record this supersedes)
