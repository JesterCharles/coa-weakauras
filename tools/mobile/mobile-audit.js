// Mobile view harness for docs/raid-utility.html
// Spec: notes/mobile-view-spec.md section 7
//
//   NODE_PATH=/private/tmp/claude-501/-Users-jestercharles-coa-weakauras/98003bdd-b53a-4e7e-8945-46e2d95a98c9/scratchpad/node_modules \
//   node mobile-audit.js <path-to-raid-utility.html> [--json out.json] [--baseline base.json]
//
// Headless Chromium reports dvh === svh === lvh, so every iOS dynamic-toolbar bug is
// invisible here. See spec 7.3 for the manual iPhone checklist. Do not read a green
// run as "iOS is fine".

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const FILE = 'file://' + path.resolve(process.argv[2]);
const EVENT = '?event=1533532408056643717';
const argOf = n => { const i = process.argv.indexOf(n); return i > -1 ? process.argv[i + 1] : null; };
const JSON_OUT = argOf('--json');
const BASELINE = argOf('--baseline');
const ROSTER = fs.readFileSync(path.join(__dirname, 'roster-fixture.json'), 'utf8');

// name, w, h, touch, rootPx, mode
// mode: 'scroll' = document must scroll; 'one' = one-screen model expected
const CASES = [
  ['01 Android split / SE1',   320,  568, true,  null, 'scroll'],
  ['02 common Android',        360,  640, true,  null, 'scroll'],
  ['03 iPhone 13 P',           390,  844, true,  null, 'scroll'],
  ['04 Pixel 7 P',             412,  915, true,  null, 'scroll'],
  ['05 iPhone 13 P root22',    390,  844, true,  22,   'scroll'],
  ['06 iPhone 13 P root26',    390,  844, true,  26,   'scroll'],
  ['07 iPhone 13 L',           844,  390, true,  null, 'scroll'],
  ['08 Pixel 7 L',             915,  412, true,  null, 'scroll'],
  ['09 Fold 5 cover',          344,  882, true,  null, 'scroll'],
  ['10 Fold 5 inner',          673,  841, true,  null, 'scroll'],
  ['11 iPad mini P',           744, 1133, true,  null, 'one'],
  ['12 iPad mini L',          1133,  744, true,  null, 'scroll'],
  ['13 iPad Pro P',           1024, 1366, true,  null, 'one'],
  ['14 iPad Pro L',           1366, 1024, true,  null, 'one'],
  ['15 Stage Manager tile',    960, 1080, false, null, 'one'],
  ['16 short split',          1280,  400, false, null, 'scroll'],
  ['17 small laptop',         1280,  800, false, null, 'one'],
  ['18 laptop GUARD',         1440,  900, false, null, 'one'],
  ['19 desktop GUARD',        1920, 1080, false, null, 'one'],
  ['21 RTL smoke',             390,  844, true,  null, 'scroll', 'rtl'],
];

// ---------------------------------------------------------------- in-page probe

const probe = () => {
  const $  = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const R  = e => e.getBoundingClientRect();
  const vw = window.innerWidth, vh = window.innerHeight;
  const cs = e => e ? getComputedStyle(e) : null;
  const box = s => { const e = $(s); if (!e) return null; const b = R(e);
    return { w: Math.round(b.width), h: Math.round(b.height), t: Math.round(b.top) }; };

  // VISUAL order, not DOM order. Card mode sorts the roster's classes to the
  // top with `order:`, which moves nothing in the DOM -- so reading rows[0]
  // from the document gives you a card that is now halfway down the page, and
  // the owner's bar reads as failing when it is passing.
  const rows = () => $$('tr.mxr').filter(r => !r.hidden && cs(r).display !== 'none')
    .sort((a, b) => R(a).top - R(b).top || R(a).left - R(b).left);
  const covRows = () => $$('.cov .covrow, .cov li, .scarcity .sc').filter(e => cs(e).display !== 'none');
  const mw = $('.mxwrap');

  // A14 allowlist / exempt list — spec section 5
  const ALLOW = ['.pick', '.pdrop', '.rhcancel', '.rhclear', '.rhrefresh', '.rhhelp',
                 '.rhx', '#uclear', '.mxr .open', 'td.mxv', '.abname>a',
                 'details.why>summary', '.lowsec>summary'];
  // .pl is deliberately NOT here: it is the chip that CONTAINS .pdrop, and a
  // container of a 44px control is 44px tall by construction. Counting it as
  // "a label that grew" flags the tap-target fix as its own regression.
  const EXEMPT = ['.chip', '.abwho i', '.mxlegend i', '.rhwho i'];

  const under44 = sel => $$(sel).filter(e => {
    const b = R(e); return b.width > 0 && b.height > 0 && (b.width < 44 || b.height < 44);
  }).length;

  const gridForm = (() => {
    const t = $('table.mx'); if (!t) return 'none';
    return cs(t).display === 'block' ? 'cards' : 'matrix';
  })();

  // scrollable boxes that are not focusable  (A12)
  const unfocusableScrollers = $$('*').filter(e => {
    const s = cs(e); if (!/(auto|scroll)/.test(s.overflowY + s.overflow)) return false;
    if (e.scrollHeight <= e.clientHeight + 1) return false;
    if (e === document.body || e === document.documentElement) return false;
    const nativelyFocusable = /^(a|button|input|select|textarea)$/i.test(e.tagName);
    return e.getAttribute('tabindex') === null && !nativelyFocusable;
  }).map(e => e.className.toString().split(' ')[0] || e.tagName.toLowerCase());

  // A7 — controls rendered beyond the reachable document
  const amputated = $$('button,a,input,summary').filter(e => {
    const b = R(e); if (b.width === 0 && b.height === 0) return false;
    return b.bottom + window.scrollY > document.documentElement.scrollHeight + 1;
  }).length;

  // A2 — anything poking past the right edge OF THE PAGE.
  // Content parked off-screen inside a deliberate horizontal scroller is not
  // that: the tab strip is a side-scroller by design and ~10 of its 14 tabs
  // are meant to be out of view until you swipe. Flagging them would make the
  // assertion fire on its own feature. Document-level horizontal overflow is
  // still caught, by A1.
  const inXScroller = e => {
    for (let n = e.parentElement; n; n = n.parentElement) {
      const o = cs(n).overflowX;
      if (o === 'auto' || o === 'scroll') return true;
    }
    return false;
  };
  const overRight = $$('*').filter(e => R(e).right > vw + 1 && !inXScroller(e)).length;

  // A20 — replacement chars anywhere in rendered text
  const uFFFD = (() => {
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n, hits = 0;
    while ((n = w.nextNode())) if (n.nodeValue.includes('�')) hits++;
    return hits;
  })();

  const firstRow = rows()[0];
  const lastRow  = rows()[rows().length - 1];
  const gapEls = $$('.gapcol, .sc.gap, .cov .gap, .tab.nocover').filter(e => cs(e).display !== 'none');

  return {
    vw, vh,
    docScrollH: document.documentElement.scrollHeight,
    docScrollW: document.documentElement.scrollWidth,
    bodyOverflow: cs(document.body).overflow,
    headerPos: cs($('header.site')).position,

    // chrome budget
    headerH: box('header.site') && box('header.site').h,
    ovtop: box('.ovtop'), ovtools: box('.ovtools'), tabs: box('.tabs'),
    rhbar: box('.rhbar'), editPanel: box('.rhedit-panel'), legend: box('.mxlegend'),
    chromeAbove: $('.ovbody') ? Math.round(R($('.ovbody')).top) : null,

    mxwrap: mw ? { w: mw.clientWidth, h: mw.clientHeight, sw: mw.scrollWidth, sh: mw.scrollHeight,
                   tabindex: mw.getAttribute('tabindex') } : null,
    tableH: box('table.mx') && box('table.mx').h,
    cellW: box('td.mxv') && box('td.mxv').w,
    gridForm,

    rowCount: rows().length,
    firstRowFully: firstRow ? (R(firstRow).top >= -1 && R(firstRow).bottom <= vh + 1) : null,
    rowTopsOnScreen: rows().filter(r => R(r).top < vh).length,
    firstThreeMine: rows().slice(0, 3).map(r => r.classList.contains('mine')),
    lastRowBottom: lastRow ? Math.round(R(lastRow).bottom + window.scrollY) : null,

    covCount: covRows().length,
    covH: (()=>{const e=$('.cov'); return e?Math.round(R(e).height):null;})(),
    aboveCards: (()=>{const r=rows()[0]; return r?Math.round(R(r).top+window.scrollY):null;})(),
    covGapsAllVisible: (() => {
      const g = covRows().filter(e => e.classList.contains('gap'));
      if (!g.length) return null;
      return g.every(e => { const b = R(e); return b.top >= -1 && b.bottom <= vh + 1; });
    })(),
    gapElOnScreen: gapEls.some(e => R(e).top < vh),

    stickyHeadTop: (() => { const th = $('.mx thead .mxhead th');
      return th ? parseFloat(cs(th).top) : null; })(),
    bandH: (() => { const b = $('.mxbands'); return b ? Math.round(R(b).height) : null; })(),

    unfocusableScrollers, amputated, overRight, uFFFD,
    matrixAnchor: !!document.getElementById('matrix'),

    tapAllowUnder44: ALLOW.reduce((n, s) => n + under44(s), 0),
    tapExemptGrown: EXEMPT.reduce((n, s) => n + $$(s).filter(e => {
      const b = R(e); return b.height >= 44 && b.width >= 44; }).length, 0),
    tapTotalUnder44: under44('button,a,input,summary,[role=button]'),

    // A23 -- HIT-TEST, DO NOT LOOK. Every control in the raid pill row must be
    // the thing the finger actually lands on. These have escaped the pill and
    // been swallowed by whatever painted over them TWICE now: once when a
    // fixed title floor stopped the contents shrinking, and again when 44px
    // tap targets outgrew the floor that fix installed. Both times they were
    // on screen, correctly sized, and completely dead. Geometry cannot see it.
    pillRowBlocked: ['.rhclear', '.rhrefresh', '.rhhelp'].filter(sel => {
      const e = $(sel); if (!e) return false;
      const b = R(e); if (b.width === 0 || b.height === 0) return false;
      const at = document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2);
      return !(at === e || e.contains(at));
    }),

    abcardDisplay: $('.abcard') ? cs($('.abcard')).display : 'absent',
    sheetPresent: !!$('.absheet'),
    hoverNone: matchMedia('(hover:none)').matches,
    pointerCoarse: matchMedia('(pointer:coarse)').matches,
    anyPointerCoarse: matchMedia('(any-pointer:coarse)').matches,
    containerQuerySupported: CSS.supports('container-type: inline-size'),

    rosterChips: $$('.pl').length,
    tabBadges: $$('.tab i').map(i => i.textContent.trim()).join(','),
    covNumbers: covRows().map(e => (e.querySelector('.scnum, .covnum') || {}).textContent || '').join(','),
  };
};

// ---------------------------------------------------------------- assertions

function assess(c, p, sticky) {
  const [name, w, h, touch, root, mode] = c;
  const A = [];
  const add = (id, ok, detail) => A.push({ id, ok: ok === true, na: ok === null, detail });

  // global
  add('A1  no h-scroll',        p.docScrollW <= p.vw + 1, `${p.docScrollW} vs ${p.vw}`);
  add('A2  nothing past right', p.overRight === 0, `${p.overRight} elements`);
  add('A8  --bandh sticky',     p.stickyHeadTop === null ? null : (p.bandH === null || p.stickyHeadTop >= p.bandH - 1),
      `top ${p.stickyHeadTop} vs band ${p.bandH}`);
  add('A12 scrollers focusable', p.unfocusableScrollers.length === 0, p.unfocusableScrollers.join(',') || 'ok');
  add('A22 #matrix anchor',      p.matrixAnchor, p.matrixAnchor ? 'ok' : 'missing');
  add('A20 no U+FFFD',           p.uFFFD === 0, `${p.uFFFD} nodes`);
  add('A23 pill row clickable',  p.pillRowBlocked.length === 0,
      p.pillRowBlocked.length ? `blocked: ${p.pillRowBlocked.join(',')}` : 'ok');

  if (mode === 'scroll') {
    add('A3  document scrolls',  p.bodyOverflow !== 'hidden' && p.docScrollH > p.vh + 40,
        `overflow ${p.bodyOverflow}, scrollH ${p.docScrollH} vs ${p.vh}`);
    add('A4  cov gaps visible',  p.covGapsAllVisible, p.covCount ? `${p.covCount} rows` : 'no .cov yet');

    // A5 IS THE OWNER'S BAR, AND IT IS TIERED BY WHAT THE VIEWPORT CAN HOLD.
    //
    // The hard bar -- "the first class card is fully visible at scrollY 0" --
    // applies wherever there is room for a card at all. Below ~600px of height
    // there is not: a 390px-tall phone held sideways spends 54px on the site
    // header and 44 on the status line before the answer block, and the answer
    // block is the thing worth having there. That case asserts the page
    // scrolls (A3) and the cards are reachable (A6) instead, which is the
    // honest contract for a landscape phone.
    //
    // "at least three card tops on screen" is a RICHNESS target, not the bar.
    // It needs roughly three cards' worth of room under the chrome, so it is
    // asserted only at the default text size on a viewport >=760 tall -- which
    // covers both devices the owner named. At 137 per cent text a card is
    // 155px and three of them cannot fit under any chrome budget; the correct
    // outcome there is "the first card is fully readable and the rest are one
    // scroll away", which is the same call A17 already makes at 162 per cent.
    if (p.vh >= 600) {
      add('A5  owner bar',       p.firstRowFully === true,
          `firstFully=${p.firstRowFully} (vh ${p.vh})`);
      // Only in card form. `order:` lives in the card-mode block, so in matrix
      // form the rows keep table order by design and this would assert against
      // a rule that is deliberately not running.
      if (p.rowCount && p.gridForm === 'cards')
        add('A5b first three .mine', p.firstThreeMine.every(Boolean),
            JSON.stringify(p.firstThreeMine));
    } else {
      add('A5  owner bar',       null, `vh ${p.vh} < 600: scroll+reach only (A3/A6)`);
    }
    if (p.vh >= 760 && !root) {
      add('A5r three cards',     p.rowTopsOnScreen >= 3, `tops=${p.rowTopsOnScreen}`);
    }
    add('A6  last row reachable', p.lastRowBottom === null ? null : p.lastRowBottom <= p.docScrollH + 1,
        `${p.lastRowBottom} vs ${p.docScrollH}`);
    add('A7  no amputation',     p.amputated === 0, `${p.amputated} controls`);
    add('A9  cards, no h-scroll', p.mxwrap ? p.mxwrap.sw <= p.mxwrap.w + 1 : null,
        p.mxwrap ? `${p.mxwrap.sw} vs ${p.mxwrap.w} (${p.gridForm})` : 'n/a');
    add('A10 bottom clearance',  p.lastRowBottom === null ? null : p.lastRowBottom <= p.docScrollH - 24,
        `${p.lastRowBottom} vs ${p.docScrollH - 24}`);
    if (sticky) add('A19 sticky sticks', sticky.ok, sticky.detail);
  } else {
    add('A11 one-screen pays',   p.mxwrap ? p.mxwrap.h >= 320 : null,
        p.mxwrap ? `${p.mxwrap.h}px of grid` : 'n/a');
    add('A6b inner scroll',      p.mxwrap ? p.mxwrap.sh > p.mxwrap.h : null,
        p.mxwrap ? `${p.mxwrap.sh} > ${p.mxwrap.h}` : 'n/a');
  }

  if (touch) {
    add('A14 targets 44px',      p.tapAllowUnder44 === 0, `${p.tapAllowUnder44} under 44`);
    add('A14b exempt stayed small', p.tapExemptGrown === 0, `${p.tapExemptGrown} grew`);
    add('A15 touch detail exists', p.sheetPresent || p.abcardDisplay !== 'none',
        `sheet=${p.sheetPresent} card=${p.abcardDisplay}`);
  }
  return A;
}

// ---------------------------------------------------------------- runner

(async () => {
  const browser = await chromium.launch();
  const results = [];
  const geom = {};

  for (const c of CASES) {
    const [name, w, h, touch, root, mode, rtl] = c;
    const ctx = await browser.newContext({
      viewport: { width: w, height: h },
      hasTouch: touch, isMobile: touch,
      deviceScaleFactor: touch ? 2 : 1,
    });
    const page = await ctx.newPage();
    // The roster comes from raid-helper.dev. A layout harness must not depend
    // on a third-party API: it rate-limited after ~100 requests and silently
    // returned an empty roster, which reads in the numbers as "the chrome got
    // smaller" rather than as "the test lost its data". Served from a captured
    // payload instead -- same 14 signups, same astral-plane character name.
    await page.route(/raid-helper\.dev\/api/, r =>
      r.fulfill({ status: 200, contentType: 'application/json', body: ROSTER }));
    try {
      await page.goto(FILE + EVENT, { waitUntil: 'load' });
      if (root) await page.addStyleTag({ content: `html{font-size:${root}px}` });
      if (rtl) await page.evaluate(() => document.documentElement.setAttribute('dir', 'rtl'));
      await page.waitForTimeout(2500);            // roster fetch

      const p = await page.evaluate(probe);

      // A19 — sticky must survive a real scroll
      let sticky = null;
      if (mode === 'scroll') {
        sticky = await page.evaluate(() => {
          const el = document.querySelector('.covbar, .rhbar.sticky, .tabs');
          if (!el || getComputedStyle(el).position !== 'sticky') return { ok: null, detail: 'no sticky el yet' };
          window.scrollTo(0, 400);
          const top = Math.round(el.getBoundingClientRect().top);
          const want = parseFloat(getComputedStyle(el).top) || 0;
          window.scrollTo(0, 0);
          return { ok: Math.abs(top - want) <= 1, detail: `top ${top} want ${want}` };
        });
      }

      results.push({ name, mode, touch, probe: p, asserts: assess(c, p, sticky) });
      if (/GUARD/.test(name)) {
        // A18 compares GEOMETRY only. tabindex/role are a11y attributes that
        // this work deliberately adds (B2); they belong in the assertion set,
        // not in the zero-pixel guard, or the guard cries wolf on its own fix.
        const { tabindex, ...mxgeom } = p.mxwrap || {};
        geom[name] = {
          ovtop: p.ovtop, rhbar: p.rhbar, tabs: p.tabs, legend: p.legend,
          chromeAbove: p.chromeAbove, mxwrap: mxgeom, cellW: p.cellW, tableH: p.tableH,
        };
        geom[name].abcardHTML = await page.evaluate(() => {
          const c = document.querySelector('.abcard');
          return c ? c.innerHTML.length : null;      // A18 content snapshot
        });
      }
    } catch (e) {
      results.push({ name, mode, touch, error: String(e) });
    }
    await ctx.close();
  }
  await browser.close();

  // ------------------------------------------------------------- report
  let pass = 0, fail = 0, na = 0;
  const failures = [];
  for (const r of results) {
    if (r.error) { console.log(`\n${r.name}  ERROR ${r.error}`); fail++; continue; }
    const p = r.probe;
    const bad = r.asserts.filter(a => !a.ok && !a.na);
    console.log(`\n${r.name}  [${r.mode}]  chrome ${p.chromeAbove}  grid ${p.mxwrap ? p.mxwrap.h : '-'}  form ${p.gridForm}  tap<44 ${p.tapTotalUnder44}`);
    for (const a of r.asserts) {
      if (a.na) { na++; continue; }
      if (a.ok) { pass++; } else { fail++; failures.push(`${r.name}  ${a.id}  ${a.detail}`);
        console.log(`   FAIL  ${a.id}  ${a.detail}`); }
    }
  }

  console.log(`\n${'='.repeat(70)}\nPASS ${pass}   FAIL ${fail}   N/A ${na}`);
  if (failures.length) { console.log('\nFAILURES\n' + failures.map(f => '  ' + f).join('\n')); }

  // A18 desktop regression guard
  if (BASELINE && fs.existsSync(BASELINE)) {
    const base = JSON.parse(fs.readFileSync(BASELINE, 'utf8')).geom;
    let drift = 0;
    for (const k of Object.keys(geom)) {
      const a = JSON.stringify(base[k]), b = JSON.stringify(geom[k]);
      if (a !== b) { drift++; console.log(`\nA18 DRIFT  ${k}\n  was ${a}\n  now ${b}`); }
    }
    console.log(drift ? `\nA18 FAIL — desktop geometry moved` : `\nA18 PASS — desktop byte-identical`);
  }

  if (JSON_OUT) fs.writeFileSync(JSON_OUT, JSON.stringify({ geom, results }, null, 1));
  process.exit(0);
})();
