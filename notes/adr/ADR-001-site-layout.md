---
title: ADR-001 — Site layout and readability
date: 2026-08-08
type: adr
status: proposed
tags: [weakauras, conquest-of-azeroth, site, layout, adr]
sources:
  - "[[pass-2-orchestration]]"
  - "[[site-layout-comparables]]"
---

# ADR-001 — Site layout and readability

## Context

The production run put all 21 classes on the site. The site is three page
types, all emitted by `tools/mksite.py`: the index (a 21-tile class roster),
21 class pages (HUD preview, logs, changelog, import steps, packs, layout
table), and `raid-utility.html` (its own generator, already through a full
mobile pass — `notes/mobile-view-spec.md` §8a records the measured outcome,
278/1 harness assertions).

The true goal shaping this audit: the site is evolving toward an **in-browser
editor** where a player customizes a class template — their spec's skills,
talents, abilities — starting from these packs
(`notes/plans/pass-2-orchestration.md:12-17`). Every recommendation below
states how it serves or at least does not obstruct that.

The audit covered the index, three class pages chosen for diversity —
Chronomancer (the one verified class, 3 specs), Bloodmage (4-spec draft),
Sun Cleric (healer, 4 specs) — and raid-utility. Comparables were researched
via `/web-research` (Firecrawl, retrieved 2026-08-08): wago.io browse +
listing + aura page, luxthos.com profile page, raidbots.com, wowhead's Frost
Mage guide and talent calculator. Full observations:
`~/second-brain/projects/coa-weakauras/notes/site-layout-comparables.md`.

### Findings, with evidence

**F1 — The index teaches class names only to mouse users.** The roster is 21
unlabeled 56px icon tiles (`mksite.py:221-253`; e.g. `docs/index.html:54-65`).
Names surface via hover tooltip (`search.js:132-134`, `mouseenter` only) or
keyboard focus (`search.js:135`). On touch there is no hover and a tap
navigates immediately (`search.js:136`), so a phone user browsing 21 custom
classes they may not recognize gets zero names before committing to a click.
The design rationale (icon band = a WA dynamic group, `site.css:93-98`) is
good; the information cost is not. Every researched comparable is
name-first: wago's class picker lists class AND spec names as visible text
(site-layout-comparables, wago browse, retrieved 2026-08-08); wowhead's
talent calc pairs its icon row with names on the artifact.

**F2 — Draft status is invisible until three clicks deep.** 20 of 21 classes
ship as drafts (every `docs/*/index.html` except chronomancer carries
`packver unver`), yet the index says "**21** of 21 classes built"
(`docs/index.html:311`) and every tile is `data-state="ready"`
(`mksite.py:239-240`); the green pip (`site.css:127-130`) means only "has a
pack". The tooltip says "Pack available" (`search.js:109`). The only draft
signal on the whole site is a 0.72rem amber `draft` chip inside each pack
block's `.meta` line (`site.css:313,403`; `docs/bloodmage/index.html:145`),
whose explanation lives in a `title` attribute (`mksite.py:270-274`) — hover
only, dead on touch. The repo's own delivery philosophy is "publish a
credible standard, feedback converges it" (MEMORY: packs ship imperfect) —
honesty about draft state is load-bearing for that loop, and both comparables
that host imports put freshness/provenance on the card itself (wago:
views/stars/installs/date per listing card; luxthos: "Updated 7 months ago"
under every copy button — site-layout-comparables, retrieved 2026-08-08).

**F3 — The class page buries its primary action under an empty panel.**
Section order is HUD → Top logs → Server changes → Import steps → Packs →
Layout (`mksite.py:916-959`). "Top logs" is empty on all 21 pages — no
`docs/*/index.html` contains a `ranktable`; every layer renders "Nothing
collected for this bracket yet" (`docs/chronomancer/index.html:91`). The
changelog renders up to 14 rows even when all are "accounted"
(`mksite.py:344`, `docs/chronomancer/index.html:104-118`). So the copy-import
CTA — the reason the page exists — sits below one empty panel and one long
ledger. On wago's aura page "Copy import string" is the first block after the
title/preview, with provenance adjacent and everything else in tabs below
(site-layout-comparables, wago aura page, retrieved 2026-08-08).

**F4 — The Layout table contradicts the real ladder.** It claims "top of
screen to bottom" and sorts by least-negative yOffset (`mksite.py:706-708`),
but shape-B bands (merged bands whose displays hang directly off a top-level
node) take their anchor from `max()` of the leaves' offsets, which are
*relative to the group*, not screen positions (`mksite.py:694-697`). Result:
Utility renders at "-4" above Main at "-132"
(`docs/chronomancer/index.html:214,225`; `docs/sun-cleric/index.html:229,243`),
the inverse of the documented ladder, where utility sits below offense at
−202-and-deeper (`notes/layout-standard.md:24-34`). The page's most
authoritative-looking artifact is wrong in its own terms. `tools/hud.py`
already resolves true geometry for the HUD preview (`mksite.py:492-495`), so
the correct ordering exists in the same build.

**F5 — Both hub pages dead-end away from the packs.** The brand links to
`raid-utility.html` on every page (`mksite.py:52,189`), Classes is off the
nav on purpose (`mksite.py:194-199`), so a class page has no route back to
the index at all (`docs/chronomancer/index.html:17-31`), and the index's own
logo navigates *away* from it. Deliberate during the `emberfall` era
(`mksite.py:43-52`), but it must reverse when the gate drops, and the plan
should carry the reversal so it is not forgotten.

**F6 — Typography and chrome details.**
(a) `meta name="color-scheme" content="light"` on a dark-only site
(`mksite.py:179`) — UA form controls and scrollbars get light hints against
`#080a0d`; should be `dark`.
(b) The heading scale is compressed: `h2` is 1.15rem (`site.css:240`)
against 0.92rem body — hierarchy is carried almost entirely by the `.lbl`
kicker (`site.css:59-64`), which works, but leaves h2 weak when a section has
no kicker (Packs and Layout have none, `mksite.py:943,952`).
(c) The index hint line teaches only desktop affordances — "Hover for
details · / to search · arrows · Enter" (`docs/index.html:316-318`) — and
shows them to touch users for whom none exist.
(d) HUD tiles carry `title` tooltips only (`mksite.py:551-552`): hover-only
detail, nothing on touch. Acceptable now; it becomes the editor canvas later
and will need a tap affordance then (the raid-utility bottom sheet,
`mobile-view-spec.md` §4.3, is shipped precedent in this repo).

**F7 — Raid-utility is the model, not the patient.** After its mobile pass
(`notes/mobile-view-spec.md` §8a: chrome 738px → 186px on iPhone 13, 278/1
assertions, desktop byte-identical), it demonstrates the patterns the class
pages lack: answer-first ordering (gap rows above navigation), server-rendered
truth with JS only toggling visibility, and a documented noscript contract
(`docs/raid-utility.html:14-33`). No new layout work is proposed for it here;
its remaining known-and-accepted items are recorded in the spec (§8a).

## Decision

**Reorder every class page around the artifact, wago-style, and make state
(draft/verified, dates, names) visible at the point of decision — without
touching the visual language, which is working.**

Concretely:

1. **Class page order becomes: masthead → HUD preview → Packs (with import
   steps folded in) → Layout → Server changes → Top logs.** The HUD stays
   first — it is the site's differentiator and the future editor canvas. The
   pack blocks move directly under it as the "artifact block": actions,
   version, draft state, dates. Top logs moves last and collapses to a single
   line when empty; the changelog collapses to its verdict line plus a
   `<details>` for entries. This is the wago aura-page shape (import CTA
   first block after preview; everything else tabs/below) applied to the
   existing single-column page.

2. **State becomes honest and visible.** The index progress bar counts
   verified vs draft separately; tiles and tooltips say "draft"; the class
   masthead carries one draft banner sentence (replacing five identical
   title-attribute chips as the only signal); pack meta gains a date
   (`verified_at` from `resources/verified-builds.json` for verified packs,
   build artifact date for drafts) because every comparable stamps freshness
   on the card.

3. **Names become text.** Class names render as visible labels in the roster
   band (a name strip under the icon row or persistent readout coupling),
   preserving the flush-icon aesthetic while ending the hover-to-learn
   requirement. The readout already renders name + spec text
   (`search.js:66-101`); the fix is coupling it to touch and making at least
   the name reachable without hover.

4. **The Layout table derives from resolved geometry** (`tools/hud.py`
   output), not raw `yOffset`s, and drops the Y column for players. Band
   order on the page must match band order on screen.

5. **The editor gets its seat now, cheaply.** The pack block's `.actions` row
   (`site.css:315`, currently Copy + Download) is the reserved home for
   "Customize" — a third action that the `minmax(250px,1fr)` card grid
   (`site.css:306-307`) absorbs with no layout change. The HUD preview
   remains the editor's canvas-in-waiting; nothing in this ADR adds structure
   that an editor pane would have to displace.

## Alternatives considered

**A. Card-grid index with names, specs and status on each tile** (the shape
wago's listing cards take — thumbnail, title, stats, tags). Rejected: the
flush icon band is the site's identity ("the grammar comes from the addon",
`site.css:1-17`) and the class page already carries the detail a card would
duplicate. The deciding evidence is that the band's information failure is
narrow (names + status), fixable with labels and honest pips, without
importing a generic card grid the design rationale explicitly avoids
(`mksite.py:227-230`: "putting them on the tile would turn the band back
into a card grid").

**B. Tabbed class page** (Description / Auras / Versions as tabs, wago-style).
Rejected for now: wago needs tabs because its pages host arbitrary
user-generated depth (247 comments, 142 versions — site-layout-comparables,
wago aura page). This site's class page has five fixed sections; reordering
plus collapsing the two ledgers achieves the same "artifact first" outcome at
a fraction of the JS and with the noscript story intact
(`raid-utility` precedent: server-rendered layers, visibility-only JS,
`mksite.py:371-376`). Tabs re-enter the conversation when the editor lands,
as ADR-004's problem.

**C. Suppress empty/loud panels at build time** (don't render Top logs when
empty; cap changelog at 3 rows). Partially adopted, but suppression alone was
rejected as the whole fix: the rankings panel's empty states are deliberate
statements ("nobody has cleared this yet", `mksite.py:383-386`) and the
changelog's outstanding-count answers a real question
(`mksite.py:296-301`). Demoting them below the fold and collapsing to their
verdict lines keeps the statements without the scroll tax.

**D. Do nothing until the editor** ("the site is temporary scaffolding").
Rejected: the pass exists because the site is the delivery channel today —
docs/ IS the distribution (`mksite.py:738-741`) — and F2/F4 are honesty
defects in a project whose feedback loop depends on players trusting what
the page says (MEMORY: packs ship imperfect; feedback is the mechanism).

## Consequences

- The primary CTA lands within one screen of the masthead on desktop and two
  on mobile, for all 21 classes, without redesigning any component.
- Draft honesty becomes site-wide; the cost is admitting "1 of 21 verified"
  on the index, which is the truth and is the mechanism the project chose.
- `layout_sections()` must consume `hud.py` geometry — a build change with
  test impact (`tests/run.py` currently has no assertion on band order;
  the plan adds the acceptance signal).
- "Customize" has a reserved, styled home before the editor exists, so
  ADR-003/004 can land a prototype without a layout pass.
- The reordered page changes nothing in `docs/assets/*.js` — sections are
  position-independent — so risk concentrates in `mksite.py` string
  assembly, covered by regenerating and diffing.
- Raid-utility is untouched; its mobile spec remains authoritative for that
  page.

## Unknowns

- **UNKNOWN-1:** Whether tile name labels under the roster band survive the
  44px mobile icon size (`site.css:364-369`) without wrapping chaos at 21
  entries. Settled by: rendering the band at 360px and 390px widths with
  labels and measuring (Playwright, same harness pattern as
  `mobile-view-spec.md` §7).
- **UNKNOWN-2:** Whether any player-facing value justifies keeping the Y
  column once band order is fixed — i.e. do players use the numbers at all.
  Settled by: community feedback after the reorder ships (the project's
  stated convergence mechanism), or by the editor making coordinates
  editable, which changes the question.
- **UNKNOWN-3:** Build-date source for draft packs — artifact mtime is not
  stable across rebuilds from clean checkouts. `resources/buildlog-*.json`
  carries per-gate dates (e.g. `buildlog-pyromancer.json`: research
  2026-08-07) but not a per-pack built-at stamp. Settled by: the orchestrator
  deciding whether builders write a `built_at` into the buildlog when the
  pack artifact is produced (one line in `build_dump.py`/builders), vs
  reading git log for the artifact path at mksite time.

## Sources

- `tools/mksite.py` — generator; cited at :43-52, :179, :189, :194-202,
  :221-253, :270-274, :296-301, :344, :371-376, :383-386, :492-495,
  :551-552, :694-708, :738-741, :916-959
- `docs/assets/site.css` — :1-17, :59-64, :93-98, :127-130, :240, :306-315,
  :364-369, :403
- `docs/index.html` — :54-65, :311, :316-318
- `docs/chronomancer/index.html` — :17-31, :91, :104-118, :214, :225
- `docs/bloodmage/index.html` — :145
- `docs/sun-cleric/index.html` — :229, :243
- `docs/assets/search.js` — :66-101, :109, :132-136
- `docs/assets/gate.js` — whole file (cosmetic gate contract)
- `notes/layout-standard.md` — :24-34 (the band ladder)
- `notes/mobile-view-spec.md` — §4.3, §7, §8a
- `notes/plans/pass-2-orchestration.md` — :12-17, :19-27
- `resources/verified-builds.json` — `verified_at` per class/version
- `resources/buildlog-pyromancer.json` — gate dates, no built-at
- `~/second-brain/projects/coa-weakauras/notes/site-layout-comparables.md` —
  wago.io browse / frost-mage listing / aura page `S16Dtxiff`, luxthos.com
  Cooldown Manager profiles, raidbots.com, wowhead.com Frost Mage guide and
  talent calculator; all retrieved 2026-08-08 via self-hosted Firecrawl
- Project memory — "Packs ship imperfect; feedback is the mechanism"
