# Mobile layout harness

21 viewports, ~20 assertions, run against `docs/raid-utility.html`.
Design record: `notes/mobile-view-adr.md`, `notes/mobile-view-spec.md`.

```
NODE_PATH=<path-to>/node_modules node tools/mobile/mobile-audit.js \
  docs/raid-utility.html --json out.json [--baseline base.json]
```

Needs Playwright on `NODE_PATH`; it is not vendored here.

**The roster is a fixture, not a live call.** `roster-fixture.json` is a captured
Raid-Helper payload. The live API rate-limited after ~100 requests during
development and then returned an empty roster, which reads in the numbers as
"the chrome got smaller" rather than as "the test lost its data". The fixture
also pins the astral-plane character name that A20 exists to catch.

**`--baseline` is a geometry guard, not a pass/fail count.** It compares
`.ovtop` / `.rhbar` / `.tabs` / `.mxlegend` heights, chrome height, `.mxwrap`
dimensions and cell width at 1440x900 and 1920x1080, before and after. Desktop
is shipped and liked; the bar there is zero pixels.

**What this cannot test.** Headless Chromium reports `dvh === svh === lvh`, so
every iOS dynamic-toolbar bug is invisible here, as are rubber-banding, the
`body.rhlock` scroll-lock behaviour and soft-keyboard occlusion. A green run is
not evidence that iOS is fine. See spec section 7.3 for the manual iPhone pass.
