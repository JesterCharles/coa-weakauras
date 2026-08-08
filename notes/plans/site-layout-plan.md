---
title: Site layout plan — the ordered fixes ADR-001 implies
date: 2026-08-08
type: plan
status: proposed
tags: [weakauras, conquest-of-azeroth, site, layout, plan]
sources:
  - "[[ADR-001-site-layout]]"
---

# Site layout plan

Ordered by impact. Every item names its file, the change, the one-line why,
and the acceptance signal. **Safe-now** items touch only presentation and can
land in the apply pass; **editor-dependent** items wait on ADR-003/004.
`docs/` is regenerated, never hand-edited; the full build needs
`--allow-unverified` while 20 classes are drafts (`mksite.py:735-771`) — the
apply pass should expect that and keep the badges.

## 1. Reorder the class page around the artifact — safe-now

- **File:** `tools/mksite.py` (`build()`, body assembly :904-960)
- **What:** Section order becomes masthead → HUD → Packs → Layout → Server
  changes → Top logs. Fold the "Three steps" import instructions into the
  Packs section (as its intro or a `<details>`), since they are one
  paragraph about the buttons below them.
- **Why:** The copy-import CTA currently sits below an empty logs panel and
  a 14-row changelog on every one of 21 pages (ADR-001 F3).
- **Signal:** On a regenerated `docs/chronomancer/index.html`, the first
  `.pack .copy` button appears before `#ranks` and `.changelog` in DOM
  order; site regenerates and `tests/run.py` stays green.

## 2. Collapse the two ledgers to their verdicts — safe-now

- **File:** `tools/mksite.py` (`rankings_panel` :370-461, `changelog_panel`
  :293-367)
- **What:** Top logs with zero entries across all categories renders as its
  section label + one line ("Nothing logged yet — source link") instead of
  four empty layers. Changelog renders its verdict line always, and the
  entry list inside `<details>` (open when outstanding > 0, closed when all
  accounted).
- **Why:** Empty and all-clear panels are statements, not reading material;
  they cost 1-2 screens above nothing (ADR-001 F3, alternative C).
- **Signal:** Chronomancer page (all accounted, no logs): `.cl-list` is
  inside a closed `details`; `#ranks` contains no `.ranklayer`. A class with
  outstanding entries renders the list open.

## 3. Honest state on the index — safe-now

- **Files:** `tools/mksite.py` (`class_tile` :221-253, index body
  :987-1046), `docs/assets/site.css` (pip :127-130), `docs/assets/search.js`
  (tooltip state :109)
- **What:** Thread `_verified_ok` into the tiles: `data-state` becomes
  `verified` / `draft` / `planned`; the pip gets a draft colour (amber
  `#f0c674`, already the site's draft hue, css:403); tooltip and readout say
  "Community draft" not "Pack available"; the progress bar label reads
  "1 verified · 20 drafts · 21 of 21 built".
- **Why:** The index currently claims 21/21 "built" with no draft signal
  anywhere before the pack block's 0.72rem chip (ADR-001 F2).
- **Signal:** `grep -c 'data-state="draft"' docs/index.html` equals the
  count of classes failing `verified.status`; bar label matches
  `resources/verified-builds.json`.

## 4. Draft banner + dates on the class page — safe-now

- **File:** `tools/mksite.py` (`pack_block` :256-289, classhead :904-914)
- **What:** (a) One sentence in the masthead of an unverified class: the
  current title-attr text ("Community draft: generated and validated, but
  nobody has confirmed this exact version in game yet. Feedback converges
  it.") printed once, visibly, instead of living in five hover tooltips.
  (b) Pack meta gains a date: `verified_at` for verified packs ("v1.2 ·
  verified 2026-08-02"), build date for drafts — pending UNKNOWN-3's source
  decision (buildlog `built_at` vs git log; orchestrator's call).
- **Why:** The draft explanation is unreachable on touch, and no comparable
  ships an import without a freshness stamp (ADR-001 F2).
- **Signal:** Bloodmage masthead contains the draft sentence exactly once;
  Chronomancer's pack meta contains "2026-08-02"; the title attribute may
  stay but is no longer the only carrier.

## 5. Fix the Layout table's band order — safe-now

- **File:** `tools/mksite.py` (`layout_sections` :637-727), reusing
  `tools/hud.py`
- **What:** Order bands by resolved on-screen geometry (the same
  `hud.displays()` output the preview trusts), not raw `yOffset`; drop the Y
  column (or keep it only as resolved px, if UNKNOWN-2 resolves in its
  favour). Keep Band / Shown for / Icons / Contents.
- **Why:** The table currently renders Utility above Main — the inverse of
  the shipped ladder — because shape-B anchors are group-relative
  (ADR-001 F4; `mksite.py:694-697` vs `layout-standard.md:24-34`).
- **Signal:** A new `tests/run.py` check: for each built class, the Layout
  table's band sequence equals the top-to-bottom sequence of band groups in
  `hud.displays()` for that pack. Chronomancer's table shows Main above
  Offense above Utility.

## 6. Visible class names on the roster — safe-now, gated on UNKNOWN-1

- **Files:** `tools/mksite.py` (`class_tile`), `docs/assets/site.css`
- **What:** Add a name label to each tile (short label under the icon, or a
  band-wide name strip that tracks hover/focus AND renders the full list on
  touch). Preserve the flush band; do not become a card grid
  (`mksite.py:227-230` states the constraint).
- **Why:** 21 unlabeled icons of custom classes are unreadable to anyone new,
  and unlabelable on touch (ADR-001 F1); every comparable is name-first.
- **Signal:** UNKNOWN-1's measurement passes at 360/390px (no horizontal
  scroll, labels legible at 44px icons); a touch user can read all 21 names
  without navigating.

## 7. Small chrome fixes — safe-now

- **File:** `tools/mksite.py`
- **What:**
  (a) `:179` `color-scheme` light → `dark`.
  (b) Index hint line (:1019-1021): keep keyboard hints inside a
  `@media (hover:hover)`-gated span or drop "Hover for details" — do not
  advertise affordances touch users don't have.
  (c) `page()` script tags (:210-215): emit `search.js`/`rankings.js` only on
  pages that use them (cosmetic, do last).
- **Why:** UA chrome mismatch on a dark site; hint teaches dead gestures.
- **Signal:** Regenerated pages carry `content="dark"`; index hint shows no
  hover/keyboard text in a coarse-pointer emulation.

## 8. Restore the two-way route when the gate drops — editor-dependent (timing), trivial (content)

- **File:** `tools/mksite.py` (`HOME` :52, nav :194-202)
- **What:** `HOME = "index.html"`, "Classes" back on the nav — the change the
  code comment already promises ("Set this back… when the packs page is
  ready").
- **Why:** Today no page links back to the class picker; the editor needs the
  hub reachable (ADR-001 F5).
- **Signal:** From any class page, one click reaches the index; brand on the
  index is self-referential. Lands in the same commit that removes
  `data-gate` (`WA_GATE_CODE = None`).

## 9. Reserve the Customize action — editor-dependent

- **Files:** `tools/mksite.py` (`pack_block` `.actions` :283-288),
  `docs/assets/site.css` (:315)
- **What:** When ADR-003's codec and ADR-004's interaction model land, the
  third action in each pack block is "Customize" (opens the editor with that
  pack loaded). Until then, change nothing — the flex row and card grid
  already absorb a third button without a layout change; that headroom is
  the reservation.
- **Why:** The editor entry point must not force a page redesign later
  (ADR-001 decision 5; wago precedent: Editor is a peer of Copy on the
  artifact).
- **Signal:** Adding a third `<a>` to `.actions` on a 250px-wide `.pack` card
  wraps cleanly (flex-wrap already set, css:315) — verifiable now in
  devtools, exercised for real when the editor lands.

## 10. HUD tile touch affordance — editor-dependent

- **Files:** `docs/assets/hud.js`, `docs/assets/site.css`
- **What:** When the HUD becomes interactive (editor canvas), tile detail
  moves from `title` attributes to the bottom-sheet pattern raid-utility
  shipped (`mobile-view-spec.md` §4.2-4.3: `pointerdown` +
  `pointerType !== 'mouse'`, desktop hover unchanged).
- **Why:** Hover-only tooltips are acceptable for a static preview,
  disqualifying for an editor (ADR-001 F6d).
- **Signal:** Deferred to the editor pass; the acceptance test is A15's shape
  (touch pointerdown opens the sheet, mouse does not).

## Out of scope

- `docs/raid-utility.html` — through its own mobile pass; its spec's
  known-and-accepted list stands (`mobile-view-spec.md` §8a).
- Preview animations — ADR-002's remit.
- Any hand-edit to `docs/` or `site.css` outside a `mksite.py` regeneration —
  the orchestrator applies these through the generator (pass-2 rule 4).
