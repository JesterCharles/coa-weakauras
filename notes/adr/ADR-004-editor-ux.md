---
title: "ADR-004 — Editor UX: preview-as-selection, form-as-editor, template-first"
date: 2026-08-08
type: adr
status: proposed
tags: [weakauras, conquest-of-azeroth, editor, ux, adr]
sources:
  - "[[pass-2-orchestration]]"
  - "[[layout-standard]]"
  - "[[class-pack-process]]"
  - "~/second-brain/projects/coa-weakauras/notes/editor-ux-comparables.md"
  - "~/second-brain/projects/coa-weakauras/notes/site-layout-comparables.md"
---

# ADR-004 — Editor UX and interactions

## Context

The site ships 21 class packs as drafts; the true goal is an in-browser
editor where a player starts from their class's shipped template and
customizes it — which abilities show, rows and positions, sizes, colors,
thresholds — then exports a WA import string
(`notes/plans/pass-2-orchestration.md:11-17`). Audience: Ascension CoA
players, mostly non-technical, no Lua. Hosting is pure static / client-side
on GitHub Pages (`pass-2-orchestration.md:23-24`). The drafts converge
through community feedback — "publish a credible standard per class/spec,
let player feedback converge it" (memory:
`packs-ship-imperfect-feedback-is-the-mechanism.md`) — so the editor is the
feedback amplifier, not just a convenience.

What the editor edits is the band-ladder structure in
`notes/layout-standard.md`: eight fixed-order bands (reminders / on target /
on me / main / resource envelope / offensive CDs / defensive+utility /
long-term), every anchor below the main row **computed, not fixed**
(`layout-standard.md:270-288` "Derived anchors"), every resource band's
width **derived from the main row's icon count** (`layout-standard.md:296`),
and merge order inside a band load-bearing ("most-pressed first",
`class-pack-process.md:618`). The vocabulary a player picks abilities from
is the per-class inventory (`resources/abilities-<class>.md`), whose role
taxonomy is `main / resource / longterm / buff / target / offensive /
defensive / utility / ignore` with priority "main > offensive > defensive >
utility" (`resources/abilities-runemaster.md:12-13`) and per-spec role/id
overrides (`abilities-runemaster.md:30-33`).

Research base (all retrieved 2026-08-08 via `/web-research`, raw scrapes and
full observations in
`~/second-brain/projects/coa-weakauras/notes/editor-ux-comparables.md`;
agent A's parallel pass in `site-layout-comparables.md`):

- **wago.io** (browse; Elemental listing; Luxthos Shaman aura page
  `wago.io/Hkc9ktj4X`, 580k views / 64k installs): the incumbent WA site is
  a registry-viewer — GIF previews, "Copy import string", 132 versions with
  changelogs, Code Review tab — **not** a web editing surface.
  Customization is deferred to the game: a sibling pack's own description
  reads "You can turn off groups that you don't need. You can add keybind
  text on any aura in Custom Options." An "Editor" tab exists on the aura
  page; what it edits did not render in the scrape (UNKNOWN-1 below).
- **Wowhead talent calculator** (`wowhead.com/talent-calc`): class chosen
  first; persistent toolbar Pin · Show Names · Annotate · Reset · Link;
  Load/Export Builds; export is a loadout **code pasted into the game**.
- **The in-game Starter Build** (`wowhead.com/guide/classes/
  dragonflight-talent-trees`): every spec ships an immutable default build;
  "You cannot change the Starter Build, but you can use it as a base from
  which to create your own build" via New Loadout + name; deviating from it
  produces a warning with the option to return; unnamed edits of the
  template are **lost on switch** and the guide warns users to always
  save-as.
- **Raidbots** (`mimiron.raidbots.com` — its beta host, answering the
  "mimiron?" question; Quick Sim page): scoping to *your* character is by
  pasting an export string; options are layered — smart defaults, then
  "Custom APL and SimC Options", then "Show Simc Input" as the raw escape
  hatch.
- **keyboard-layout-editor.com** (the non-WoW template customizer): "load
  one of the presets and start customizing it!"; the rendered keyboard is
  the **selection** surface, but "the selected keys can be modified on the
  _Properties_ tab" — a form panel; Raw data tab as escape hatch; JSON
  export.
- **NN/g** (Schade, "Customization vs. Personalization", 2016; "7 Tips for
  Successful Customization", 2016): customization must be discoverable near
  the content it affects, simple, **layered** ("show the most useful
  options first … As for tertiary options: don't even offer them"), and
  never load-bearing ("Generic site experiences, with no customization,
  should be strong enough").

## Decision

### D1. The HUD preview is the selection surface; a properties panel is the editing surface

The editor is the existing class-page HUD preview (already "drawn to scale
straight from the import string" — `docs/runemaster/index.html`, hudnote)
made interactive: click/tap an icon or a band to **select** it; all editing
happens in a **properties panel** docked beside (desktop) or beneath
(mobile sheet) the preview. No free dragging of icons to pixel positions.

Why not a pure canvas: every comparable that lets novices customize a
template uses exactly this hybrid (KLE's canvas + Properties tab; WA's own
in-game options panel over a live preview), and none ships free-drag. More
decisively, the repo's layout engine makes pixel positions **derived
state**: anchors below the main row are computed from real band depths
(`layout-standard.md:270-288`), widths are locked to the main row
(`layout-standard.md:296`), and wrapped rows re-center per loaded spec
(`layout-standard.md:414-431`). A drag surface would let players set values
the engine immediately recomputes — the classic broken-feedback loop.

"Position" therefore means what the engine can honor:

- **whole-HUD offset** (the ladder's anchor point relative to the
  character) — one control, safe;
- **order within a band** (list reorder — this is `controlledChildren`
  order, which is real and load-bearing, `class-pack-process.md:618`);
- **which band an ability sits in** (move between offensive CDs and
  defensive+utility; role change within the cooldown pair).

The band ladder's vertical order itself is not draggable in v0: "vertical
order encodes urgency" (`layout-standard.md:479`) and it is the invariant
that makes any CoA pack readable by someone who learned another one
(`layout-standard.md:13-15`).

### D2. Template-first, save-as, visible deviation — the Starter Build shape

The editor never opens blank. Entry is a "Customize" action on the class
page next to the pack it customizes (NN/g tip 1: near the content), landing
with the **shipped template loaded** for the spec the player picks (spec
picker = the same three buttons the preview already has,
`docs/runemaster/index.html:55`). The shipped template is immutable; edits
live in a named **variant** (localStorage), exactly the Starter Build →
New Loadout shape, including its trap: the wowhead guide documents that
unnamed edits are lost on switch, so the editor requires a name at first
save and shows a persistent "modified from Runemaster v1.8 — N changes"
deviation chip (the Wowhead calculator keeps its edit state as a
first-class HUD element: "Spent: 0/34"; same principle).

### D3. Add/remove via a picker scoped to the class+spec inventory, grouped by role

Adding an ability opens a picker over the class's real inventory
(`resources/abilities-<class>.md` shipped as JSON — data-shape seam to
ADR-003), scoped to the selected spec via the `Specs` column, grouped by
the role taxonomy in the order the ladder draws it (reminders → target →
buff → main → resource → offensive → defensive → utility → longterm), with
search. Rows the inventory marks `ignore` (passives, effects-not-buttons —
the majority of `abilities-runemaster.md`) are excluded by default behind a
"show everything" toggle, because "not a player button" is a curated
verdict the picker should not silently reverse. Removing = select icon →
Hide (reversible from an "hidden abilities" list; NN/g tip 7: selections
must be easy to change).

This is the same scoping every comparable uses — wago browses by
class/spec, Wowhead makes you pick a class before showing a tree — and on
Ascension, where no armory exists, **declaring class+spec is the only
scoping available** (Raidbots' paste-your-character has no equivalent
here).

### D4. Talent-dependent abilities are declared, not detected

The §2 transform problem: a talent that replaces/transforms/grants an
ability is a WeakAura requirement (`class-pack-process.md:203-205,
539-541`), and this fork resolves no overrides — the shipped packs already
handle it in-game by gating on the replacement's own Spell Known id
(`layout-standard.md:640-646`). The browser cannot detect talents, so the
editor mirrors the in-game truth: abilities whose existence depends on a
talent carry a **talent badge** in the picker and preview ("only with
Battle Engravings" — `abilities-runemaster.md:51` is the live example), and
in v2 a declared-talent toggle set filters the inventory and swaps §2
transform pairs as a unit. Until then the badge alone ships: the load gate
already makes a wrongly-included talent ability cost nothing in game (it
never loads — `layout-standard.md:553-557`), so the failure mode of not
filtering is cosmetic, not broken.

### D5. Deliberately NOT editable (the invariant floor)

The editor edits a **parameter overlay** on the template; the underlying
build machinery re-emits the pack. Never exposed:

| Locked | Why (evidence) |
|---|---|
| Load gates (class token, `spellknown`) | the entire performance story and the reason 21 packs coexist (`layout-standard.md:481-558`); a wrong id fails silently |
| Trigger wiring and condition structure | escalation tiers must stay ANDed with `onCooldown == 1` or every icon glows on every GCD — shipped broken twice (`layout-standard.md:317-347`) |
| `use_showgcd` per ability | derived from scraped off-GCD data, not opinion (`layout-standard.md:305-323`) |
| Desaturate-when-unusable | a correctness cue, not a style (`layout-standard.md:355-369`) |
| Band ladder math, width lock, wrap mechanics | derived state; see D1 |
| uid/version salting | an un-salted re-import is **silently ignored** by WeakAuras (`class-pack-process.md:464-466`); the editor must salt exports itself — mechanism is ADR-003's to define |

The exact overlay-vs-template contract (which JSON fields the editor may
write, how the client-side codec re-emits) is **ADR-003's editable-surface
seam — ADR-003 had not landed when this was written**; its research note
(`~/second-brain/projects/coa-weakauras/notes/js-wa-codec-landscape.md`)
already establishes that full client-side decode→edit→re-encode is viable
(pako for DEFLATE, a small JS port of `wacodec.py` for LibSerialize, byte-
identity demanded at the serialized layer). This ADR binds only the UX-side
contract: the overlay is small, diffable, and serializable independently of
the pack string.

### D6. Readability guardrails: the editor warns live, using the repo's own rules

Shared principles between site and editor — the preview must read as the
game will, and the editor must not let a player build an unreadable HUD
*without noticing*:

- **Same data path.** The editor preview is generated from the same built
  pack the export encodes (as the site's preview already is — "drawn to
  scale straight from the import string"). No second rendering that can
  drift.
- **Width warning.** Any always-visible row wider than **1.2× the resource
  bar** gets an inline warning on the band — this is the shipped rule,
  measured and enforced by `tools/rowwidths.py` ("exits non-zero past
  1.2x", `layout-standard.md:440-442`); the editor runs the same check
  live as the player adds icons.
- **Icon size floors.** Shipped floors are the smallest sizes any pack
  uses: 26px cooldown icons, 28px target/long-term, 36-44px above the main
  row (`layout-standard.md:24-34`). Resizing below the shipped floor for a
  band warns ("smaller than any shipped pack"); it does not block, because
  the floors are precedent, not measured legibility data (UNKNOWN-4).
- **Escalation vocabulary is preserved, not styled away.** Sweep (cooldown
  swipe + GCD sweep), glow (proc, ≤10s), urgent glow (≤5s), tint
  (desaturate-unusable) each carry one meaning
  (`layout-standard.md:71,302-304,355-360`); v0 exposes none of them, v1
  exposes thresholds/colors but never removal of a tier.
- **Warnings, not locks, wherever the result is legal.** Structural
  invariants (D5) are locks because the engine derives them; readability
  choices are the player's, flagged. NN/g tip 5 is the backstop: the
  shipped default must stay good enough that a player who never opens the
  editor loses nothing.

### D7. Export and the feedback loop

The export screen produces the same artifact the site already teaches:
copy import string / download .txt, with the existing three-step import
instructions (`docs/runemaster/index.html`, "Three steps"). Alongside it,
a **"send this back"** affordance serializes the overlay (a small JSON
diff, not the pack) into a prefilled GitHub issue link — this is the
static-hosting-compatible form of the feedback mechanism the pack process
depends on (memory: packs ship imperfect; feedback converges them). The
deviation chip's change list is the issue body.

### Scope tiers (justified by what comparables ship first and what the data supports)

- **v0** — the overlay a template already parameterizes: show/hide any
  ability in the template; reorder within a band; move between the two
  cooldown bands; whole-HUD offset; per-band icon size (floor-warned) and
  a global scale; spec selection; named variants; export + feedback link.
  This matches the first customization every comparable offers (wago packs:
  "turn off groups that you don't need"; KLE: move/recolor preset keys) and
  requires no new data.
- **v1** — parameters with meaning attached: escalation thresholds
  (20/10/5s), resource warn/danger thresholds (the fused-heat 50/80 shape,
  `layout-standard.md:173-177`), glow/bar/text colors, per-spec variants,
  band-order swap behind a warning. Ships second because thresholds and
  colors are where a wrong value silently degrades the safety vocabulary —
  they need the warning framework from D6 proven first.
- **v2** — vocabulary expansion: add abilities from the full spec inventory
  (including `ignore`-flagged rows behind the toggle), declared-talent
  toggles with §2 transform swaps, custom aura tracking by id, shareable
  overlay strings. Gated on data that does not exist yet (UNKNOWN-2) and on
  ADR-003's codec being proven in the prototype.

## Alternatives considered

**A. Canvas-first direct manipulation (drag icons anywhere).** Rejected.
No comparable ships it (KLE, the closest, explicitly routes edits through
a Properties tab); it fights the derived-anchor engine (D1); and it makes
the unreadable-HUD failure mode the *default* outcome rather than a warned
exception. The 1.2x rule exists because a shipped pack got this wrong with
the full build system watching (`layout-standard.md:382-397`).

**B. Forms-only, preview passive (the wago/in-game model).** Rejected as
the whole story, adopted as half of it. It is the incumbent (wago defers
customization to WA's in-game options panel), so it demonstrably works —
but it also demonstrably breaks novices: the customization surface is a
second UI, in another program, discovered by reading a description. NN/g
tip 1 (customization near the content) is the direct argument for making
the preview itself clickable.

**C. Author-side Custom Options (ship WA custom-options panels inside the
packs, no web editor).** Rejected as the primary path. It is what Luxthos
does and it reaches only players who find the in-game panel; it cannot
amplify feedback (changes never leave the player's client), and every
option is hand-authored Lua-side config the pipeline would have to
generate and maintain per class. Kept as a possible v2+ complement for
in-combat-adjacent tweaks the web cannot do.

**D. Fork-and-edit raw (expose the decoded table, wago-Editor style).**
Rejected for the audience. "No Lua required" is a product constraint
(memory: packs-ship-imperfect), and the repo's own history shows raw-table
edits are where silent failures live (`final12`, `final14` in
`layout-standard.md`). A read-only "inspect" view may exist for debugging,
but it is not the editor.

**E. Blank-canvas builder (compose a HUD from scratch).** Rejected.
Starter Build, KLE and NN/g all point the same way: templates first,
customization layered on, defaults load-bearing. A from-scratch builder
also multiplies the invariant surface (every D5 lock becomes a decision a
novice must get right).

## Consequences

- The editor inherits the site's preview renderer as its core component;
  preview fidelity work (ADR-002's icon/animation pass) pays into the
  editor directly, and divergence between preview and export becomes the
  worst class of bug — hence D6's same-data-path rule.
- The overlay format becomes a public artifact (feedback issues carry it),
  so it needs versioning discipline from day one — small, named fields,
  additive evolution.
- Export salting (D5, last row) must be settled with ADR-003 before v0
  ships, or edited packs will silently fail to re-import over their own
  previous version — the exact bug that cost ten iterations on Runemaster
  (`class-pack-process.md:464-466`).
- v0 requires abilities/template data as static JSON per class; that
  export step lands in the build pipeline (`mksite.py`-adjacent), not in
  the editor.
- Locking band order and trigger wiring means some player requests will be
  refusable-by-design; the deviation chip and feedback link give those
  requests a channel instead of a workaround.
- Desktop-first: v0 editing targets desktop; on coarse pointers the
  44px touch-target rule from the mobile pass applies to selection targets
  (`notes/mobile-view-spec.md:90`), but full mobile editing is not a v0
  acceptance criterion.

## UNKNOWNs

1. **What wago's Editor tab actually edits** (raw table? metadata only?).
   Settled by: visiting an aura page logged in, or reading the
   `methodgg/wago.io` frontend source (link captured in scrape).
2. **Structured per-spec talent data** for declared-talent toggles — the
   skillbook JSON marks talents as text ("skillbook says Talent Passive"),
   but no per-spec talent-tree dataset exists in `resources/`. Settled by:
   a db.exil.es/db.ascension.gg talent-tree scrape + `mkabilities.py`
   column audit, before v2 planning.
3. **ADR-003's editable-surface contract** (overlay fields, re-encode
   path, salting mechanism). Settled by: ADR-003 landing; the codec
   research note already de-risks the pipeline.
4. **Measured legibility floors** — 26px is shipped precedent, not tested
   in-game minimum. Settled by: the post-ship in-game verification passes
   (`class-pack-process.md:428-438`) recording the sizes players actually
   report unreadable, via the feedback channel.
5. **What players change first** (validates the tier ordering). NN/g
   warns most users never customize; the ordering here is inferred from
   comparables, not observed. Settled by: the feedback-link overlay diffs
   themselves — the editor measures its own use.

## Sources

- `notes/plans/pass-2-orchestration.md` (governing decisions, static
  hosting, agent D scope)
- `notes/layout-standard.md` (band ladder, derived anchors, width lock,
  1.2x rule, escalation tiers, desaturate, gate-at-leaf, Spell Known)
- `notes/class-pack-process.md` (§2 talents, research gate, VERSION/uid
  salting, carry-forward checklist)
- `resources/abilities-runemaster.md` (role taxonomy, per-spec overrides,
  `ignore` verdicts, Battle Engravings)
- `docs/runemaster/index.html` (shipped preview, spec/mode toggles,
  hudnote, pack blocks, import steps)
- `notes/mobile-view-spec.md` (44px coarse-pointer rule)
- `~/second-brain/projects/coa-weakauras/notes/editor-ux-comparables.md` —
  this pass's research: wago.io browse + Elemental listing + Luxthos aura
  page (`wago.io/Hkc9ktj4X`), wowhead.com talent-calc + Dragonflight
  talent guide (Starter Build, loadout import/export),
  mimiron.raidbots.com home + Quick Sim, keyboard-layout-editor.com,
  nngroup.com/articles/customization-personalization/ and
  nngroup.com/articles/customization/ — all retrieved 2026-08-08
- `~/second-brain/projects/coa-weakauras/notes/site-layout-comparables.md`
  (agent A, 2026-08-08 — wago card anatomy, wowhead toolbar/state HUD)
- `~/second-brain/projects/coa-weakauras/notes/js-wa-codec-landscape.md`
  (agent C research, 2026-08-08 — client-side codec viability)
- Memory: `packs-ship-imperfect-feedback-is-the-mechanism.md`
