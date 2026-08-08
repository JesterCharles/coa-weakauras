---
title: Editor UX plan — v0 flow wireframes and the ranked scope tiers
date: 2026-08-08
type: plan
status: proposed
tags: [weakauras, conquest-of-azeroth, editor, ux, plan]
sources:
  - "[[ADR-004-editor-ux]]"
  - "[[pass-2-orchestration]]"
---

# Editor UX plan

The concrete work ADR-004 implies. Screens are described to wireframe
precision; nothing here is code. Ordering is the build order — each item
lists its acceptance signal. Items marked **(seam: ADR-003)** cannot start
until the editor-architecture ADR defines the overlay/codec contract.

## The v0 flow, screen by screen

```
class page ── [Customize] ──> editor (template loaded, spec picked)
                                 │  select icon/band on preview
                                 │  edit in properties panel
                                 │  live warnings (width, size floor)
                                 ▼
                              save-as named variant (localStorage)
                                 │
                                 ▼
                              export: copy string / download / send-back
```

### Screen 1 — entry from the class page

Not a new page section so much as one action: a **Customize** button in
each pack block's `.actions` row, next to "Copy import string" /
"Download .txt" (`docs/<class>/index.html`, pack article markup). NN/g
tip 1: the customization affordance sits on the artifact it customizes.
The all-specs pack's button opens the editor with the spec picker unset;
a per-spec pack's button opens with that spec preselected.

- The button carries the same draft/verified badge context the pack shows;
  no separate "editor" nav entry in v0 (the `emberfall` gate stays until
  the pass completes — `pass-2-orchestration.md:25`).
- **Acceptance:** from any shipped class page, one click lands in the
  editor with that class's current template loaded; the URL encodes
  class + spec (`/editor/?class=runemaster&spec=glyphic` or equivalent
  hash) so a link reproduces the entry state.

### Screen 2 — the editor surface

One screen, three regions. Desktop: preview left (~2/3), panel right
(~1/3). Coarse-pointer/narrow: preview full-width, panel as a bottom
sheet; selection targets honor the 44px rule
(`notes/mobile-view-spec.md:90`).

**2a. Top bar** (persistent, the Wowhead-toolbar shape):

- spec picker (the existing `hudspec` buttons), mode toggle
  ("In play" / "Everything" — reused as-is from the site preview),
- variant name + **deviation chip**: "modified from Runemaster v1.8 —
  4 changes" (click = change list, each entry revertable individually),
- Reset-to-template, Undo/Redo,
- Export (goes to Screen 4).

**2b. Preview** — the interactive HUD:

- Rendered from the same band/geometry data the export will encode
  **(seam: ADR-003** — v0 can render from the same JSON `mksite.py`
  already emits for the static preview, but the export path must consume
  the identical structure**)**.
- Hover/focus: icon outline + name tooltip (names are already `title`
  attrs in the shipped preview). Click: select → panel shows properties.
  Click a band's margin or its label: select the band. Esc / click-away:
  deselect, panel shows HUD-level properties.
- Hidden abilities render at ~35% opacity when the top-bar "show hidden"
  toggle is on; invisible otherwise.
- Selection is single in v0 (KLE ships multi-select; v0 does not need it —
  no v0 operation applies to a set).
- **Acceptance:** every icon and band in a shipped template is selectable
  by pointer and by keyboard (tab order follows band order); the selection
  is visibly marked in the preview and named in the panel.

**2c. Properties panel** — contents depend on selection:

| Selection | Controls (v0) |
|---|---|
| nothing (HUD level) | whole-HUD X/Y offset (numeric + nudge arrows); global icon scale; "show hidden" toggle; variant management (rename, duplicate, delete) |
| a band | band icon size (numeric, floor-warned per ADR-004 D6); show/hide entire band; reorder list of the band's abilities (drag handle rows or up/down buttons — list semantics, mirrors `controlledChildren` order); "+ Add ability" (Screen 3) |
| an icon | name, role, spec(s), talent badge if any (read-only identity); Hide; "move to…" (offense ↔ defense+utility only, per ADR-004 D1); position-in-band (same reorder list, scrolled to this entry) |

Everything else the pack knows about the ability — triggers, load,
conditions, GCD flag — is shown nowhere or as read-only fine print, per
ADR-004 D5. No control in v0 has more than one meaning, and no v0 control
writes anything the layout engine derives.

- **Width warning** renders on the band in the preview and beside the size
  control: "this row is 1.34× the resource bar (shipped limit 1.2×) — it
  will read as clutter in game", recomputed on every add/resize with the
  same formula `rowwidths.py` enforces (`n*size + (n-1)*gap` vs bar
  width).
- **Acceptance:** reproducing the `final15` bug by hand (adding icons to
  Engravement utility until 21 sit un-wrapped) shows the warning before
  export; export still allowed (warn, don't lock).

### Screen 3 — the add-ability picker

Modal (desktop) / full sheet (mobile) opened from a band's "+ Add
ability".

- Content: the class inventory JSON (from `resources/abilities-<class>.md`
  via a build-time export), filtered to the current spec's `Specs` column,
  minus abilities already visible in the template.
- Grouped by role in ladder order; the group matching the selected band is
  expanded first, others collapsed. Search box filters across groups by
  name.
- Each row: icon art, name, role tag, spec tags, talent badge where the
  inventory notes one, and the Notes cell's first clause as a hint line
  ("shipped pack, band RM Offense" / "a CC").
- `ignore`-flagged rows are absent in v0 (they return in v2 behind "show
  everything" — ADR-004 D3/tier table).
- Picking a row inserts it at the end of the selected band and selects it.
- **Acceptance:** on Runemaster/Glyphic the picker offers exactly the
  non-`ignore`, Glyphic-or-all rows of `abilities-runemaster.md` not
  already shown; a hidden template ability reappears via the picker or the
  hidden list, and both paths restore its original band position.

### Screen 4 — export

A focused panel, not a new page:

- Primary: **Copy import string** + Download .txt — same actions, same
  styling, same three-step import instructions the class pages already
  teach.
- The exported pack carries a variant-distinct uid salt so it re-imports
  cleanly over both the shipped pack and the player's own previous export
  **(seam: ADR-003** — mechanism; the requirement is fixed here: an
  unbumped export silently keeps the old copy in WA,
  `class-pack-process.md:464-466`**)**.
- Secondary: **"Send this back"** — opens a prefilled GitHub issue: title
  "`<class>/<spec>` variant feedback", body = the deviation change list +
  the overlay JSON in a code fence. No accounts, no backend; static-host
  compatible.
- Outstanding warnings (width, size floor) are restated once above the
  copy button.
- **Acceptance:** an exported string imports in game next to the shipped
  pack without collision; the issue link opens prefilled with an overlay
  that, pasted back into the editor (v2 import path; until then a manual
  check), reproduces the variant.

## Cross-cutting v0 work

1. **Inventory + template JSON export** — build step emitting, per class:
   the ability inventory (role/specs/id/talent-badge/hint) and the
   template's band structure with per-icon geometry. Acceptance: the
   static preview and the editor render from the same file and the site
   build fails if the two would diverge. **(seam: ADR-003** owns the
   template-side schema**)**
2. **Overlay format v0** — named fields for: hidden set, per-band order,
   band moves, per-band size, global scale, HUD offset, variant name,
   template version it was made against. Acceptance: JSON-serializable,
   diffable, additive-evolvable; template-version mismatch on load
   produces a visible "made against v1.7, template is now v1.8" notice
   (the changelog-staleness lesson, applied to the editor).
3. **Warning framework** — one mechanism rendering band-anchored and
   panel-anchored warnings from rule functions (width, size floor).
   Acceptance: rules are data + pure functions, so v1 thresholds reuse it
   unchanged.
4. **Variant storage** — localStorage keyed by class+spec+name; the
   Starter-Build trap is closed: leaving with unnamed changes prompts
   name-or-discard, never silent loss. Acceptance: reload restores the
   last-open variant; the shipped template is bit-identical after any
   amount of editing (immutability test).

## Ranked scope tiers (from ADR-004, with acceptance signals)

| Tier | Surface | Acceptance signal |
|---|---|---|
| **v0** | show/hide abilities; reorder within band; move between cooldown bands; whole-HUD offset; per-band size + global scale (floor-warned); spec selection; named variants; export + send-back | a Runemaster player hides two utility icons, shrinks the utility band, exports, and the string imports and renders in game exactly as the preview showed; the shipped template file is untouched |
| **v1** | escalation thresholds (20/10/5s); resource warn/danger thresholds; glow/bar/text colors; per-spec variants of one customization; band-order swap behind a warning | changing the urgent-glow threshold to 3s exports a pack whose conditions still carry the `onCooldown == 1` AND (check-9 shape holds on edited output); no v1 control can remove an escalation tier |
| **v2** | picker over the full inventory incl. `ignore` behind "show everything"; declared-talent toggles + §2 transform swaps; custom aura by id; overlay import (paste a shared variant) | UNKNOWN-2 (talent dataset) resolved first; a declared Battle Engravings toggle swaps the Ley Lock presentation as one unit; a pasted overlay reproduces another player's variant on a fresh browser |

Tier gates: v1 starts only after v0's warning framework has survived one
round of real feedback issues; v2 starts only after ADR-003's codec is
proven by the pass-2 prototype (agent E) and UNKNOWN-2 is settled.

## Explicitly out of scope (all tiers, per ADR-004)

Free-drag positioning; editing load gates, triggers, conditions, GCD
flags; band-ladder math; Lua of any kind; blank-canvas building; raid
multi-target tracking (VuhDo/Grid own it — `class-pack-process.md:511-516`);
authoring in-game Custom Options panels (alternative C, possible later
complement).
