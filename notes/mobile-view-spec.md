# Spec: mobile view for the raid-utility page

**Status:** **approved** 2026-08-03 — in implementation
**Decision record:** `notes/mobile-view-adr.md`
**Acceptance bar:** the coverage grid has real height on the first screen at 390x844
and 412x915 with a raid loaded, and desktop geometry at 1440x900 / 1920x1080 is
unchanged to the pixel.

---

## 0. Ground rules

- `docs/raid-utility.html` is **generated**. All markup changes go in
  `tools/utility_page.py` and regenerate with `python3 tools/mksite.py --utility-only`.
- `python3 tools/mksite.py` with no flag **refuses to build** (Pyromancer v0.1 gate).
  Do not reach for `--allow-unverified` — it silently writes `docs/pyromancer/` and four
  pack files into the site output. Use `--utility-only` throughout.
- Also regenerate `notes/raid-utility.md` via `python3 tools/utility_tables.py` if row
  content changes. It should not in this work.
- Playwright modules live at
  `NODE_PATH=/private/tmp/claude-501/-Users-jestercharles-coa-weakauras/98003bdd-b53a-4e7e-8945-46e2d95a98c9/scratchpad/node_modules`.
- **Verify interaction by hit-testing, not by looking.** `elementFromPoint` at a control's
  own centre. Screenshots have already missed one overlap bug on this page.

---

## 1. The three axes, as concrete CSS

### 1.1 Layout mode

Wrap the existing one-screen rules in a media query. **Nothing inside them changes.**

```css
@media (min-width: 721px) and (min-height: 760px) {
  body:has(main.util.uwide){height:100dvh;overflow:hidden;display:flex;flex-direction:column}
  body:has(main.util.uwide)>header.site{flex:none}
  .util.uwide{flex:1;min-height:0;overflow:hidden}
  .ovbody{flex:1;min-height:0;display:flex;flex-direction:column}
  .panel:not([hidden]){flex:1;min-height:0;overflow-y:auto}
  #panel-overview{overflow:hidden;padding-bottom:0}
  .mxwrap{overflow:auto;flex:1;min-height:0}
}
```

Outside the query — now the default — the document scrolls:

```css
.util.uwide{overflow:visible}              /* was overflow:hidden, css:74 */
.panel:not([hidden]){overflow-y:visible}   /* was auto, css:111 */
.mxwrap{flex:none;overflow-y:visible;min-height:auto}
#panel-overview{padding-bottom:40px}       /* was 0, css:112 — last card must not sit flush */
```

The `overflow:visible` pair is **not cosmetic**. A sticky element does not stick if an
ancestor has `overflow` other than visible on the same axis. Leave either as-is and the
sticky status line scrolls away with no error and no obvious cause.

`760` is provisional — re-derive after §3 lands. Re-check the synthetic 768x800 case
(measured 243px of grid, below the 320px floor) at that point.

### 1.2 Grid form

```css
.mxwrap { container-type: inline-size; container-name: grid; }

@container grid (max-width: 1040px) {
  /* the current css:661-699 card block, verbatim */
}

@supports not (container-type: inline-size) {
  @media (max-width: 720px) {
    /* the same block, today's threshold */
  }
}
```

Two additions inside the card block, both required by §2.4:

```css
.mx tbody{display:flex;flex-direction:column}   /* order: needs flex items */
```

Above a ~700px container, give the card stack two columns — it now serves widths up to
~1092px and `tr.mxr`'s class-name row (`flex:1 0 100%`, css:673) looks stranded at 1000px.
The container already exists, so this is one more `@container` rule.

### 1.3 Control sizing and interaction

```css
@media (pointer: coarse) { /* the §5 allowlist, 44px */ }
@media (hover: none)     { /* sheet presentation */ }
```

`.abcard` is gated on `(hover:hover) and (pointer:fine)` rather than "not `hover:none`",
so it cannot fire mid-tap on a hybrid. The sheet's CSS ships under `(any-pointer:coarse)`.
**Which affordance actually opens is decided per event** — see §4.2.

---

## 2. The mobile first screen

Order in the scrolling document:

| # | element | height | behavior |
|---|---|---|---|
| 1 | `header.site` | 54px | scrolls away (already `position:relative`, site.css:445) |
| 2 | status line | 44px | **sticky, `top:0`** |
| 3 | `.cov` answer block | 72-208px | scrolls |
| 4 | `tr.mxr` class cards | 121px each | scrolls, roster-first |
| 5 | legend | ~56px collapsed | `<details>`, **below** the cards |

### 2.1 Sticky containing-block trap

The status line is assembled from elements inside `.ovtop`. A sticky element is
constrained to its containing block — its parent's padding box — so it would stick for
about the height of `.ovtop` and then leave. Silently.

```css
.ovtop{display:contents}   /* scroll mode only */
```

`display:contents` removes the box, so `.ovtop`'s own `display:flex;gap:8px 16px`
(css:82) stops applying. Re-express the tabs/tools gap as a margin.

### 2.2 Status line (44px, sticky)

Carries: Discord mark, raid title, `.rhage` staleness (js:311-328 already maintains it),
headcount, **gap count in red**, and a 44px collapsed filter icon.

Unloaded, the same line is `.rhopen` (`Load tonight's raid`, already styled as the primary
action, css:943-951) plus `.rhhelp`.

`.rhstate`'s unmatched-signup warning renders as a second line **whenever non-empty**. It
is an error about data integrity; errors do not hide.

The filter expands full-width on tap, with `#qcount` beneath it. Add `inputmode` and
`enterkeyhint="search"` — `#rhid` already has `enterkeyhint` (utility_page.py:498).

> At 320px this row survives on **10px of slack**, with `#fbox` pinned exactly at its
> `min-width:150` floor (css:88) and `.rhpill` at its `min-width:118` + 22px `.rhhelp`.
> Every child is at its floor simultaneously. A 22px root or a longer event title tips it.
> That is why the filter collapses — not to reclaim space it never spent.

### 2.3 `.cov` — the answer block

Server-rendered by `utility_page.py` (§3). Row height **68px** with a who-line, 56px bare.

| state | render |
|---|---|
| no raid loaded | rarest-first static counts from `counts` — the honest cold-open answer to "what is scarce" |
| 0 gaps | one 44px green summary line |
| 1-2 gaps | individual named red rows, `order:-1`, each actionable |
| **3+ gaps** | **one red row naming them comma-separated** — reuse the `.gapline` string `drawRaid()` already builds (js:341) — plus the summary |
| covered rows | count + 2-3 character names + `+N` |

The 3+ collapse is a design call, not a budget dodge: when 4 of 11 tools are uncovered the
raid has a composition problem and the headline matters more than the breakdown. It also
keeps A5 passing at a 22px root, where the uncollapsed form fails.

**Who-line clamping.** One line, `overflow:hidden; text-overflow:ellipsis;
white-space:nowrap`, with `+N` as a `flex:none` item pinned right so it is never what gets
ellipsed.

> **Never truncate names in JS.** The live roster contains `𝓥𝓾𝓵𝓽𝓱𝓻𝓪𝓼𝓾𝔃` — 10 glyphs,
> `String.length === 20`, astral-plane surrogate pairs. `.slice(0,n)` splits the pair and
> emits U+FFFD. CSS ellipsis is grapheme-safe; `Intl.Segmenter` if it must be JS. **The
> hazard already exists in shipped code** — apply the CSS clamp to `.abwho i` (`fillWho()`,
> js:689-709) and `.acwho .w` (`bearers()`, js:904-938) too, not only to `.cov`.

**Band separation survives.** Rows carry `b-stop` / `b-tools` / `b-trash`; the trash band
sits below a hard rule under a "TRASH ONLY — a stun is not an interrupt" header.
`.sc-trash` already overrides scarcity outright (css:233) and already encodes this.

**Reuse `.scarcity`/`.sc`/`.bartrack` (css:217-260)** rather than writing new CSS. It is
~50 lines of already-reviewed styling with a rarest-first tile, a `.barfill` bar, a red
`.sc.gap` state and `order:-1`. The component was designed, styled, and orphaned. Revive
it; do not delete it.

**Each `.cov` row links to its panel** with a real `aria-controls`. These rows are the
mobile navigation (§2.5).

### 2.4 Class cards, roster-first

`li.ab.notmine{order:2}` (css:1028-1030) already does this for the ability lists and
`body.mypick .mxr:not(.mine){opacity:.22}` (css:443) already dims the rest. Card mode makes
`tbody` a block, so add `display:flex;flex-direction:column` to make `order` available.

Three conditions:

1. **Kitrow parity.** `tr.mxr` and its `tr.kitrow` are siblings and must carry the **same**
   `order` value — equal values preserve source order, so each pair stays glued.
   `recount()` toggles `.mine` on rows (js:108); it must toggle it on the matching kitrow
   too. The filter path already keeps them in sync (js:719-722), so only the `.mine`/`order`
   path is new.
2. `margin:0 0 5px` (css:672) still works in a column flex container; `[hidden]{display:none}`
   (css:625) still removes items from flex layout. Both verified.
3. **Known cost, named not inherited:** `order` changes visual order without changing DOM
   order, so tab and screen-reader order stay in source order (WCAG 2.4.3). This is the same
   cost css:1028-1030 already pays on this page.

### 2.5 Tabs hidden

```css
.tabs{display:none}   /* scroll mode */
```

**`display:none`, never removed from the DOM.** `gaps()` iterates `$$(".tab")` and reads
`t.firstChild.textContent` (js:159-167); `apply()` writes the badges (js:761-782).
`display:none` also removes the orphaned `role="tablist"` from the accessibility tree, so
there is no tablist ARIA to reconcile — but `.cov` rows must carry proper `aria-controls`
instead.

> **This is the referee ruling flagged in ADR D6, not agent consensus.** If the owner
> prefers the visible 48px sticky scroller: it needs `flex-wrap:nowrap; overflow-x:auto;
> scroll-snap-type:x proximity; overscroll-behavior-x:contain`, a right-edge fade with a
> deliberate half-tab peek, **and** the full tablist ARIA fix (`aria-selected`,
> `aria-controls`, `role="tabpanel"`, roving tabindex) becomes mandatory rather than moot —
> plus a visual mark distinguishing the strip's multiplexed badges from `.cov`'s coverage
> numbers when a filter is active, since both would then be on screen showing different
> numbers for the same category.

### 2.6 Roster

Collapsed to the status line. Behind its tap, **two different containers**:

- **Read-only list → bottom sheet.** `.pl` chips with 44px `.pdrop`, plus
  `restore N removed` (js:382-385) — it is an undo, needs no keyboard, and it is what you
  reach for right after dropping the wrong person.
- **Add-a-walk-in → full-screen route.** `inset:0`, own scroller, **form at the top of the
  panel** so the keyboard opens below it. iOS Safari does not resize the layout viewport
  for the keyboard; a bottom-anchored sheet gets covered, not moved. The ~80-option
  `<datalist>` becomes a filtered list against the alias resolution that already exists
  (`terms()`/`ALIAS`, js:657-674).

### 2.7 Legend

Cut to four entries, moved **below** the card stack, inside `<details>`, ~56px collapsed.

Card mode kills entry 7 ("blank = does not bring it") outright — `td.mxx{display:none}`
(css:679) means there are no blanks. Entry 1 ("shortest cooldown") is self-evident once
`content:attr(data-l)` labels every chip (css:682). The four that survive render as bare
unguessable glyphs in a card: `.spn` spec name, `<i class="t">` talent, `<i class="p">+N`,
`<i class="q">?` unverified.

---

## 3. Generator changes — `tools/utility_page.py`

~25 lines. Reads `counts`, **already computed at line 425** and currently used only to sort
tabs. No new data, no second pass over `by_cat`.

1. **Emit `.cov` inside `#panel-overview`**, not as a sibling of `.ovbody`. `show()`
   toggles `hidden` on `.panel` elements (js:833-838); a ledger outside that tree would
   survive tab switches it should not.
2. Server-rendered, so the noscript contract at `docs/raid-utility.html:14-31` survives.
3. **Resolve `conf` (lines 426-428)** — computed today and never read. Surface it as a `?`
   marker on a `.cov` count **only when `cover > 0 && conf === 0`**: the raid's entire
   coverage of that tool rests on abilities with no database record, i.e. "you might have
   this, or you might have nothing." Every other verified/unverified split is a caveat that
   already lives in the ability list as `.chip.unv`/`.chip.unv2`.
4. **Add `id="matrix"`** to `#panel-overview` or `.mxwrap`. Ten `href="#matrix"` links
   (line 758) currently point at nothing.
5. **Fix the noscript comment** at html:17 — it still promises "the scarcity counts" that
   were deleted.

---

## 4. JS changes — `docs/assets/raid-utility.js`

### 4.1 `.cov` is written by `apply()`, in the same loop, from the same `cover` object

Nothing else may write it. `.cov` is a fifth surface for a truth that already lives in
`.gapcol` headers, the `.gapline` sentence and `.tab.nocover` badges; if `apply()` is not
the single writer they will disagree the first time someone edits js:761-782.

> **`apply()` multiplexes and `.cov` must not inherit it.** `if (v) mode="find"` beats
> `else if (cover) mode="raid"`, and `.nocover` is applied only when `mode === "raid"`
> (js:766-778). If `.cov` inherited that, typing one character in the filter would silently
> convert the mobile home screen from a coverage report into a search-hit count **with every
> gap flag removed**. `.cov`'s coverage number and gap state are **never** multiplexed;
> search hits render as a second, differently styled number.

`recount()` additionally toggles `.mine` on the matching `tr.kitrow` (§2.4).

### 4.2 `bind()` gains a per-event path

```js
// unchanged, unconditional — desktop is byte-identical
el.addEventListener('mouseenter', ...)   // js:978-987
el.addEventListener('mousemove',  ...)
el.addEventListener('mouseleave', ...)

// new
el.addEventListener('pointerdown', ev => {
  if (ev.pointerType === 'mouse') return;
  openSheet(...);          // and suppress the hover path for this interaction
});
```

This is the only fix that closes the shipped bug both media-query gates leave in place: on
a **touchscreen laptop** `(hover:none)` is false, so a finger fires `mouseenter` with no
`mouseleave`, and the card opens and sticks.

Opening the sheet sets `card.hidden = true`.

### 4.3 The sheet

Bottom-anchored, `max-height:70dvh`, `overflow:auto`, `overscroll-behavior:contain`,
focus-trapped, dismissed by backdrop tap / Esc / a real close button.

Content is `one(a)` **plus** `bearers(a)` — the latter is the piece with no mobile
equivalent today, including the `.acwho.miss` "not on your Felsworn: both are Tyrant" case.

**Reorder for the sheet only:** name + class·spec → **bearers** → cd/cost/cast → chips →
description. `one()` (js:940-962) emits bearers last, so on a 70dvh sheet the answer to "so
who DOES have it" is the thing most likely below the fold. Implement as `one(a, sheet)`
with the falsy default producing today's string byte-for-byte — `bind()`'s `mouseenter`
calls `one(DATA[i])` with one argument.

`.abcard`'s CSS (785-846) is ~95% reusable. Two things must change: `pointer-events:none`
(css:785) is reverted for the sheet — the description and bearer names need to be
selectable and the ability link tappable — and `place()` (js:963-970) **must not run**,
which also sidesteps its use of `window.innerWidth/innerHeight` instead of `visualViewport`.

### 4.4 Scroll lock

`body.rhlock{overflow:hidden}` (css:961) is inert today because `body` is already
`overflow:hidden`. **The moment mobile scrolls it becomes load-bearing, and
`overflow:hidden` on `body` does not prevent scroll in iOS Safari.** Replace with
`position:fixed` + saved `scrollY` restore, or `overscroll-behavior` + `inert`.

**This ships in the same commit as document scrolling.** Not after.

### 4.5 Panel scroll reset

`show()` calls `window.scrollTo({top:0})` (js:837), but the scroller is
`.panel:not([hidden])` (css:110-111), whose `scrollTop` survives the `hidden` toggle. So
today: scroll to the bottom of Interrupts, switch to Purges, switch back — still at the
bottom, on desktop too. Under document scrolling the `window.scrollTo` becomes live and the
behavior changes again. Reset the correct box for the active mode.

---

## 5. Tap targets

**44px under `(pointer:coarse)`, by name.** Applied with padding / `min-height` on the box,
not transparent `::after` hit-slop, so the target is visibly where it is tappable.

| element | today | becomes |
|---|---|---|
| `.pick` (css:340) ×21 | 34px | 44 — the primary roster control, highest volume |
| `.pdrop` (css:883) ×12 | `padding:1px 5px` ≈ 18px | 44 |
| `.rhcancel` (css:130) | `padding:0 9px` ≈ 17px | 44 |
| `.rhclear` / `.rhrefresh` (css:938, 1007) | ≈ 16px | 44 |
| `.rhhelp` (css:954) | 22 explicit | 44 |
| `.rhx` (css:969) | ≈ 24x32 | 44 |
| `#uclear` (css:94) | `padding:0 10px` | 44 |
| `.mxr .open` (css:675-677) | ≈ 38px | 48 |
| `td.mxv` chips (css:680-681) | `padding:3px 8px 4px` | 44 min-height; also the sheet trigger |
| `.abname>a` (css:548) | inline text | 44px flex row |
| `details.why>summary` (css:197) | ≈ 20px | 44 |
| `.tab` (css:713, 735) | ≈ 31px | n/a — hidden on mobile |
| `.lowsec>summary` (css:607) | `padding:17px 19px` | already fine |

**Deliberately left small, and asserted to stay small:** `.chip` (css:586), `.abwho i`
(css:1047), `.pl` (css:874), `.mxlegend i` (css:450), `.rhwho i` (css:167). These are labels,
not controls. A 44px non-target is a worse defect than a 20px label — the harness asserts
they did not grow, so a future blanket sweep fails the test.

---

## 6. Bug fixes bundled

| # | bug | fix |
|---|---|---|
| B1 | `--bandh` read at css:280, written nowhere; band row is 31px vs a hardcoded 29 (38 at 22px root) | set it from the real height, or derive the second sticky row's `top` via `calc` |
| B2 | `.mxwrap` is a scroller with `tabindex === null` | add `tabindex="0"` — Safari does not make it focusable heuristically |
| B3 | ten `href="#matrix"`, zero `id="matrix"` | §3.4 |
| B4 | `.rhmodal` uses `4vh` (css:964) | `4dvh` — on iOS `vh` is the *large* viewport |
| B5 | `#panel-overview{padding-bottom:0}` (css:112) | 40px in scroll mode; last card must not sit flush |
| B6 | `scroll-margin-top:74px` (css:182, 604, 606) compensates for a sticky header that does not exist — `header.site.haspt{position:relative}` (site.css:445) beats the `sticky` at site.css:72, and the page carries `class="site haspt"` | re-derive from the real sticky bar height via **one shared custom property**, not a fourth hardcoded number |
| B7 | `.slice()` on character names emits U+FFFD | CSS clamp, §2.3 — including on already-shipped `fillWho()` and `bearers()` |
| B8 | noscript comment promises deleted scarcity counts | §3.5 |
| B9 | dead `.rbhead`, `.cfrow`, `.cf` (css:696-698) | delete |
| B10 | `conf` computed, never read | §3.3 |

**Do NOT add `viewport-fit=cover`** unless `env(safe-area-inset-*)` padding lands in the
same commit. Without cover, iOS insets the layout viewport for you and this is safe; with
cover and no `env()`, the last card goes under the home indicator. The current meta
(`width=device-width,initial-scale=1`, no `maximum-scale`) is correct and must stay correct
— zoom is not blocked.

---

## 7. Verification

### 7.1 Device matrix — 21 cases

Every case loads `?event=<id>` and waits for the roster fetch.

| # | case | viewport | touch |
|---|---|---|---|
| 1 | Android split / iPhone SE1 | 320x568 | ✓ |
| 2 | common Android | 360x640 | ✓ |
| 3 | **iPhone 13 portrait** | **390x844** | ✓ |
| 4 | **Pixel 7 portrait** | **412x915** | ✓ |
| 5 | iPhone 13, 22px root | 390x844 | ✓ |
| 6 | iPhone 13, 26px root | 390x844 | ✓ |
| 7 | iPhone 13 landscape | 844x390 | ✓ |
| 8 | Pixel 7 landscape | 915x412 | ✓ |
| 9 | Fold 5 cover | 344x882 | ✓ |
| 10 | Fold 5 inner | 673x841 | ✓ |
| 11 | iPad mini portrait | 744x1133 | ✓ |
| 12 | iPad mini landscape | 1133x744 | ✓ |
| 13 | iPad Pro portrait | 1024x1366 | ✓ |
| 14 | iPad Pro landscape | 1366x1024 | ✓ |
| 15 | Stage Manager tile | 960x1080 | ✗ |
| 16 | short split | 1280x400 | ✗ |
| 17 | small laptop | 1280x800 | ✗ |
| 18 | **laptop — regression guard** | **1440x900** | ✗ |
| 19 | **desktop — regression guard** | **1920x1080** | ✗ |
| 20 | rotation | 390x844 → 844x390 → 390x844 | ✓ |
| 21 | RTL smoke | 390x844, `dir="rtl"` | ✓ |

Plus a **synthetic 20-signup roster** alongside the real 12 — `.rhedit-panel` scales with
signups and the collapse must be verified against the larger one.

### 7.2 Assertions

**Global**

- **A1** `documentElement.scrollWidth <= innerWidth + 1`. *(passes today; must stay)*
- **A2** No element's `getBoundingClientRect().right > innerWidth + 1`.
- **A8** Where `.mx thead` is displayed: `.mxhead th` computed `top >= .mxbands.offsetHeight - 1`.
  *(**fails today** — 29 vs 31, 29 vs 38 zoomed)*
- **A12** Every scrollable box is focusable. *(**fails today** on `.mxwrap`)*
- **A13** `.tab[role=tab]` has `aria-selected` + `aria-controls`; the panel has
  `role="tabpanel"`. *(**fails today**. Under §2.5 the tabs are `display:none` on mobile, so
  this is asserted in one-screen mode; it becomes mandatory everywhere if the owner picks
  the visible scroller)*
- **A22** `document.getElementById('matrix')` is non-null. *(**fails today**)*

**Scroll mode** (1-13, 15, 16, 20, 21)

- **A3** `body` computed `overflow !== 'hidden'` **and**
  `documentElement.scrollHeight > innerHeight + 40`. *(**fails everywhere today** —
  `scrollHeight === innerHeight`)*
- **A4** At `scrollY === 0` with a raid loaded, **every zero-coverage `.cov` row is fully
  within the viewport.** Asserts the outcome of `order:-1`, not the rule.
- **A5** *The owner's bar.* At `scrollY === 0` the first `tr.mxr:not([hidden])` is **fully**
  visible (`top >= 0 && bottom <= innerHeight`), **≥3** rows have `top < innerHeight`, and
  under a loaded raid **the first three carry `.mine`**. A bare count is passable by three
  classes that are not in tonight's raid.
- **A6** The last `tr.mxr:not([hidden])` is reachable after `scrollTo(0, scrollHeight)`.
- **A7** No control is amputated: every `button, a, input, summary` has
  `bottom <= documentElement.scrollHeight`. *(**fails today** at 320x568)*
- **A9** `.mxwrap` has no horizontal scroll in card form. *(**fails today** at 844x390 and
  915x412 — 1040 vs 792)*
- **A10** Last card `bottom <= scrollHeight - 24`.
- **A19** **Sticky actually sticks.** Scroll to 400px; the sticky status line's `top` is
  within 1px of its sticky offset. 400px is well past where `.ovtop` would have ended, so
  this catches all three failure modes at once — ancestor `overflow`, containing-block clip,
  and a missed `top`.

**One-screen mode** (14, 17, 18, 19)

- **A11** `.mxwrap.clientHeight >= 320` — the model engages only where it pays.
  *(1440x900 = 422 ✅; 1133x744 = 207 ❌ and must therefore fall out of one-screen mode)*
- **A6b** `.mxwrap` scrolls internally and its last row is reachable that way.
- **R2 guard** In matrix mode, `.mxc` stays at `left ≈ 0` after `.mxwrap.scrollLeft = 400`
  — `container-type: inline-size` establishes containment around a `position:sticky` child.

**Coarse pointer** (1-14, 20)

- **A14** Every element in the §5 allowlist has `width >= 44 && height >= 44`. **Bar: 0
  failures.** The exempt list is asserted to have **stayed small**. Inline prose links are
  counted separately on a ratchet — the number may fall, never rise.
- **A15** Dispatch `pointerdown` with `pointerType:'touch'` on `td.mxv[data-ids]` → the
  sheet opens. Then dispatch with `pointerType:'mouse'` at 1440x900 → the sheet does **not**
  open and the hover card does. *(**fails today** — css:817 deletes the card with no
  replacement)*
- **A16** With the sheet open, `body` does not scroll behind it. Same for `.rhmodal`.
- **A20** Render a roster containing `𝓥𝓾𝓵𝓽𝓱𝓻𝓪𝓼𝓾𝔃`; no rendered text node contains U+FFFD.
  Check `.cov`, `.abwho`, `.acwho`, and the `.pl` chips.
- **A21** For every category, `.cov`'s number equals the corresponding `.tab i` number under
  a loaded raid with no filter. Then apply a filter and assert `.cov`'s coverage number and
  gap state are **unchanged**.

**Text-scaled** (5, 6)

- **A17** Re-run A1, A3, A4, A7, A9, A14, A19 at 22px and 26px root. **A5 at 22px only** —
  at a 26px root (162%) the first card is fully readable and the rest are one scroll away,
  which is the correct outcome, and it cannot pass without cutting the answer block.

**Desktop regression** (18, 19)

- **A18** Measured geometry **byte-identical before and after**: `.ovtop`, `.rhbar`,
  `.tabs`, `.mxlegend` heights; chrome above `.ovbody`; `.mxwrap` client and scroll
  dimensions; `td.mxv` cell width. **Plus an `.abcard.innerHTML` snapshot at 1440x900 on
  hover** — a signature change to a shared string builder holds the geometry bar while
  silently changing content, and geometry assertions would not catch it.

> **A18 runs before the layout change lands, not after.** Every rule moved into a media
> query is a rule that can silently stop applying on desktop, and there is no CSS test
> harness.

### 7.3 What the harness cannot test

**Headless Chromium reports `dvh === svh === lvh === innerHeight`.** Every iOS
dynamic-toolbar bug, rubber-banding, the `body.rhlock` failure, and `visualViewport`
displacement by the soft keyboard are **invisible to Playwright**. Manual pass on a real
iPhone in Safari:

1. Scroll down, then up — does the grid reflow or jitter as the toolbar animates?
2. Open the how-to modal, drag the backdrop — does the page behind move?
3. Focus the filter, then the add-a-walk-in form — does the keyboard cover the results?
4. Rotate to landscape and back with a raid loaded — is state preserved, and is the grid
   still cards?

Items 1 and 2 *cannot* fail by construction: dropping the `dvh` dependence removes the
mechanism, and the scroll lock is fixed in the same change. That is deliberate.

---

## 8. Sequencing

Each step ends green before the next starts.

| # | commit | gate |
|---|---|---|
| 1 | Harness + baseline. Extend the audit script to all 21 cases; capture A18 baseline at 1440x900 and 1920x1080 | baseline recorded, known-failing assertions enumerated |
| 2 | Bug fixes with no layout dependency: B1, B2, B3, B4, B8, B9, B10 | A8, A12, A22 pass; A18 unchanged |
| 3 | **Layout mode** (§1.1) **+ scroll lock** (§4.4) **+ B5, B6** — these must be one commit | A3, A7 pass; A18 unchanged |
| 4 | **Grid form** container query (§1.2) | A9 passes; rotation case 20 is form-invariant; R2 guard passes |
| 5 | Chrome collapse: status line, roster split, legend, tabs (§2.1, 2.2, 2.5, 2.6, 2.7) | chrome ≤ ~218px at 390x844; A19 passes |
| 6 | **`.cov`** — generator (§3) + `apply()` wiring (§4.1) | A4, A21 pass |
| 7 | Roster-first card order (§2.4) | A5 passes including `.mine` |
| 8 | Sheet + `pointerdown` (§4.2, 4.3) + B7 | A15, A16, A20 pass |
| 9 | Tap targets (§5) | A14 = 0 failures; exempt list unchanged |
| 10 | Re-derive `760` post-collapse; re-check 768x800 against A11 | full matrix green |
| 11 | Manual iPhone pass (§7.3) | four checks signed off |
| 12 | `mksite.py --utility-only`, verify no `docs/pyromancer/` output, commit, push | Pages build green |

---

## 9. Explicitly out of scope

- Any second HTML artifact, UA sniff, or width redirect.
- JS-measured viewport height written into CSS custom properties.
- `viewport-fit=cover` without `env()` insets in the same commit.
- `maximum-scale=1` / `user-scalable=no`.
- Hand-edits to `docs/raid-utility.html`.
- RTL. Case 21 asserts only "does not explode"; logical properties are a later change.
- Redesigning the matrix. The container query changes *when* card mode engages, not what it
  looks like.
- Shipping fewer rows to mobile. Data parity is the point.
- `.cov` on desktop. Withdrawn — desktop is shipped and liked.
- Adding a link to the raid-utility page from the live `index.html`. That needs a full
  `mksite.py` run, which is blocked on Pyromancer verification.
