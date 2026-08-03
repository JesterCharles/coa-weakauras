/* Raid utility page. Everything here is an enhancement: with JS off the page
 * is the full coverage grid plus all ten ability sections, and nothing is
 * hidden behind script that is not also printed statically.
 *
 * 1. Expand a grid row into that class's full kit.
 * 2. Pull tonight's raid out of Raid-Helper and count coverage against it.
 * 3. Filter, across every tab at once.
 */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) {
    return Array.prototype.slice.call((r || document).querySelectorAll(s));
  };
  var norm = function (s) {
    return String(s == null ? "" : s).toLowerCase().replace(/[^a-z0-9]/g, "");
  };

  var rows = $$("tr.mxr");
  var kits = {};
  $$("tr.kitrow").forEach(function (k) { kits[k.dataset.class] = k; });

  var SPEC = {}, SPECALIAS = {};
  try { SPEC = JSON.parse($("#specdata").textContent); } catch (e) {}
  try { SPECALIAS = JSON.parse($("#specalias").textContent); } catch (e) {}

  /* ------------------------------------------------------------ 1. expand */
  rows.forEach(function (r) {
    var btn = $(".open", r);
    if (!btn) return;
    btn.addEventListener("click", function () {
      var open = r.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      kits[r.dataset.class].hidden = !open;
    });
  });

  /* --------------------------------------------------- spec -> class index
   * A Raid-Helper signup carries NO class -- `className` on a signup is the
   * ROLE (Tank/Melee/Ranged/Healer/Support) and the only identity is
   * `specName`. So the spec name is the join key, and this is the index it
   * joins against. Checked against a real event: of the 69 specs the guild's
   * template configures, 65 match a tree label outright and none is ambiguous
   * across two classes. The other four are in resources/spec-aliases.json. */
  var SPEC2CLASS = {};
  Object.keys(SPEC).forEach(function (c) {
    SPEC[c].s.forEach(function (s, i) {
      SPEC2CLASS[norm(s)] = { c: c, i: i };
    });
  });
  function resolveSpec(specName) {
    var k = norm(specName);
    if (SPEC2CLASS[k]) return SPEC2CLASS[k];
    var a = SPECALIAS[k];
    if (!a) return null;
    // s:null means the CLASS is known and the SPEC is not -- do not guess one,
    // the page shows it as unresolved instead.
    if (a.s == null) return { c: a.c, i: -1 };
    var idx = (SPEC[a.c] ? SPEC[a.c].s : []).map(norm).indexOf(norm(a.s));
    return idx < 0 ? { c: a.c, i: -1 } : { c: a.c, i: idx };
  }

  /* ---------------------------------------------------------- 2. the raid
   * `mine` is class -> array of booleans, one per spec. It is no longer
   * clicked together by hand; it is whatever Raid-Helper says signed up. */
  var KEY = "coa-raid", IDKEY = "coa-rhid";
  var mine = {};
  function nspec(c) { return (SPEC[c] && SPEC[c].s.length) || 0; }
  function allOn(c) {
    var a = [], n = nspec(c);
    while (a.length < n) a.push(true);
    return a;
  }

  function reach(c, bits) {
    var m = mine[c];
    if (!m) return true;                       // not in the raid: no opinion
    if (!bits) return true;
    for (var i = 0; i < bits.length; i++) {
      if (bits.charAt(i) === "1" && m[i]) return true;
    }
    return false;
  }

  var colCells = {};
  rows.forEach(function (r) {
    $$("td.mxv", r).forEach(function (td) {
      var i = Array.prototype.indexOf.call(r.children, td);
      (colCells[i] = colCells[i] || []).push({ c: r.dataset.class, td: td });
    });
  });
  var cols = {};
  $$("thead th.mxh a").forEach(function (a, i) {
    cols[i + 1] = a.getAttribute("href").slice(1);
  });

  /* cat -> how many rostered classes can actually press it. Kept on the module
   * so apply() can paint it onto the tab badges: with the scarcity strip gone
   * the tabs are the only place left that can answer "how many interrupts does
   * this raid have", and they were already showing a number. */
  var cover = null;

  function recount() {
    var list = Object.keys(mine);
    var on = list.length > 0;
    document.body.classList.toggle("mypick", on);
    rows.forEach(function (r) {
      r.classList.toggle("mine", !!mine[r.dataset.class]);
    });
    $$("td.mxv").forEach(function (td) {
      var c = td.parentNode.dataset.class;
      td.classList.toggle("nospec", !!mine[c] && !reach(c, td.dataset.specs));
    });
    cover = null;
    if (on) {
      cover = {};
      Object.keys(cols).forEach(function (i) {
        cover[cols[i]] = (colCells[i] || []).filter(function (x) {
          return mine[x.c] && reach(x.c, x.td.dataset.specs);
        }).length;
      });
    }

    /* PAINT THE GAP, NOT JUST THE COVER.
     *
     * A tool nobody in the raid can press shows up in this grid as an empty
     * column across your rows -- absence drawn as absence, i.e. invisible.
     * That is the one question the page exists to answer, so once a raid is
     * loaded the empty column gets flagged outright: the header goes red and
     * the column carries a wash the whole height of the table.
     *
     * Note this is per COLUMN and not per row. Dimming the classes you did not
     * bring stays as it is -- those twelve rows are not a gap, they are
     * reference, and making them loud would bury the nine that are yours. */
    var head = $$("thead th.mxh");
    Object.keys(cols).forEach(function (i) {
      var cat = cols[i], bad = !!cover && !cover[cat];
      var th = head[i - 1];
      if (th) {
        // never for the trash band: a raid with no stun is not a finding
        bad = bad && !th.classList.contains("b-trash");
        th.classList.toggle("gapcol", bad);
      }
      rows.forEach(function (r) {
        var td = r.children[i];
        if (td) td.classList.toggle("gapcol", bad);
      });
    });

    apply();
    return cover;
  }

  /* The tools this raid has NOBODY for. The single most useful sentence on the
   * page once a comp is loaded, and it is the one thing a grid of struck cells
   * makes you work for -- you would have to scan ten columns to notice that a
   * whole one is empty. Trash-band tools are excluded: a raid missing a stun is
   * not a finding. */
  function gaps() {
    if (!cover) return [];
    return $$(".tab").filter(function (t) {
      return t.dataset.panel !== "overview" &&
             !t.dataset.nocol &&              // no column, so no coverage
             !t.classList.contains("tb-trash") &&
             !cover[t.dataset.panel];
    }).map(function (t) { return t.firstChild.textContent.trim(); });
  }

  /* ------------------------------------------------- 3. Raid-Helper fetch
   * GET https://raid-helper.dev/api/v4/events/<id> reads without a token and
   * answers `access-control-allow-origin: *`, so a static page can call it
   * from the browser with no backend and no bot credentials. The site never
   * talks to Discord -- Raid-Helper's public API is the whole bridge. */
  var RH = "https://raid-helper.dev/api/v4/events/";
  var bar = $(".rhbar"), rhForm = $(".rhform"), rhOpen = $(".rhopen"),
      rhState = $(".rhstate"), rhInput = $("#rhid");

  function eventId(s) {
    // Accept a bare id or any raid-helper URL pasted whole -- people copy the
    // link out of Discord far more often than they dig out the number.
    var m = String(s || "").match(/(\d{6,})/);
    return m ? m[1] : "";
  }

  function say(html, cls) {
    if (!rhState) return;
    rhState.hidden = false;
    rhState.innerHTML = html;
    rhState.className = "rhstate" + (cls ? " " + cls : "");
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* THE ROSTER IS A LIST OF PEOPLE, not a set of class flags.
   *
   * Signing up and turning up are different things, so the fetched list is
   * only a starting point: `EDITS` records who was dropped and who was added
   * by hand, keyed to the event, and is replayed over every fetch. That way
   * hitting refresh five minutes before pull picks up the two late signups
   * WITHOUT throwing away the fact that you already know Melou is not coming.
   *
   * A hand-added player may be a spec with no name -- "somebody is bringing a
   * Sanguine Bloodmage" is the whole fact a coverage grid needs, and demanding
   * a character name for it would just get "x" typed in. */
  var RAID = [];          // [{n, s, c, i, e, manual}]
  var ROSTER = null;      // class -> spec index -> [player]
  var EDITS = { drops: [], adds: [] };
  var lastEvent = "", lastBench = 0, lastUnresolved = [];
  var lastTitle = "", lastDate = "";
  var lastFetch = 0, pollTimer = null, inFlight = false;

  function editKey() { return "coa-edits-" + (lastEvent || "none"); }
  function loadEdits() {
    try {
      EDITS = JSON.parse(localStorage.getItem(editKey()) || "") ||
              { drops: [], adds: [] };
    } catch (e) { EDITS = { drops: [], adds: [] }; }
    EDITS.drops = EDITS.drops || [];
    EDITS.adds = EDITS.adds || [];
  }
  function saveEdits() {
    try { localStorage.setItem(editKey(), JSON.stringify(EDITS)); } catch (e) {}
  }

  // A stable handle for one person, so a drop survives a refetch.
  function pid(p) { return (p.n || "") + "|" + (p.c || "") + "|" + p.i; }

  function parseSignups(su) {
    var out = [], benched = 0, unresolved = [];
    su.forEach(function (s) {
      // Bench and absence are signups too. A benched player is not in the
      // raid, and counting them is how a roster quietly over-reports.
      var role = String(s.className || "");
      if (/bench|absence|late|tentative/i.test(role) ||
          /bench|absence/i.test(String(s.specName || ""))) { benched++; return; }
      var hit = resolveSpec(s.specName);
      if (!hit) { unresolved.push(s.specName || "(blank)"); return; }
      out.push({
        n: String(s.name || "?").split("-")[0],
        // Raid-Helper hands back the guild's own Discord emoji for the spec,
        // which IS the icon they clicked in the signup post.
        e: s.specEmoteId || s.classEmoteId || "",
        c: hit.c, i: hit.i,
        s: hit.i < 0 ? "?" : SPEC[hit.c].s[hit.i]
      });
    });
    return { list: out, benched: benched, unresolved: unresolved };
  }

  function rebuild() {
    // signups, minus who you dropped, plus who you added by hand
    var dropped = {};
    EDITS.drops.forEach(function (k) { dropped[k] = 1; });
    RAID = BASE.filter(function (p) { return !dropped[pid(p)]; });
    EDITS.adds.forEach(function (a) {
      var hit = resolveSpec(a.spec);
      if (!hit) return;
      RAID.push({ n: a.name || "", e: "", c: hit.c, i: hit.i,
                  s: hit.i < 0 ? "?" : SPEC[hit.c].s[hit.i], manual: true });
    });

    mine = {};
    var roster = {};
    RAID.forEach(function (p) {
      if (!mine[p.c]) mine[p.c] = new Array(nspec(p.c)).fill(false);
      if (p.i < 0) mine[p.c] = allOn(p.c);   // spec unknown: do not invent one
      else mine[p.c][p.i] = true;
      var slot = roster[p.c] = roster[p.c] || {};
      (slot[p.i] = slot[p.i] || []).push(p);
    });
    ROSTER = RAID.length ? roster : null;
    // published for the hover card, which lives in the other IIFE
    window.CoaRaid = ROSTER ? { roster: roster, spec: SPEC } : null;
    try { localStorage.setItem(KEY, JSON.stringify(mine)); } catch (e) {}
    recount();
    drawRaid();
  }

  var BASE = [];

  /* The Discord mark, inline. An <img> to Discord's CDN would be a request per
   * page view for a logo, and the guild's own server icon is not in the API
   * response (it gives serverId, not the icon hash). The mark plus the event's
   * own title is enough to say "yes, tonight's raid is loaded". */
  var DISCORD =
    '<svg class="dmark" viewBox="0 0 24 18" width="15" height="12" ' +
    'aria-hidden="true"><path fill="currentColor" d="M20.3 1.6A19.8 19.8 0 0 0 ' +
    '15.4.1a13.8 13.8 0 0 0-.6 1.3 18.3 18.3 0 0 0-5.5 0A13.6 13.6 0 0 0 8.6.1' +
    ' 19.7 19.7 0 0 0 3.7 1.6C.6 6.3-.3 10.8.2 15.3a19.9 19.9 0 0 0 6 3 14.7 ' +
    '14.7 0 0 0 1.3-2.1 13 13 0 0 1-2-1c.2-.1.4-.3.5-.4a14.2 14.2 0 0 0 12 0l.5.4' +
    'a13 13 0 0 1-2 1 14.5 14.5 0 0 0 1.2 2.1 19.8 19.8 0 0 0 6-3c.6-5.2-.8-9.7' +
    '-3.4-13.7ZM8.0 12.6c-1.2 0-2.2-1.1-2.2-2.4S6.8 7.8 8 7.8s2.2 1.1 2.2 2.4' +
    '-1 2.4-2.2 2.4Zm8 0c-1.2 0-2.2-1.1-2.2-2.4s1-2.4 2.2-2.4 2.2 1.1 2.2 2.4' +
    '-1 2.4-2.2 2.4Z"/></svg>';

  var rhSlot = $(".rhslot"), rhPill = $(".rhpill");

  function ago(ms) {
    if (!ms) return "";
    var s = Math.round((Date.now() - ms) / 1000);
    if (s < 45) return "just now";
    var m = Math.round(s / 60);
    if (m < 60) return m + "m ago";
    return Math.round(m / 60) + "h ago";
  }

  function drawPill() {
    if (!rhPill) return;
    var on = !!(RAID.length || BASE.length);
    rhPill.hidden = !on;
    if (rhOpen) rhOpen.hidden = on;
    if (!on) return;
    rhPill.innerHTML = DISCORD +
      '<b>' + esc(lastTitle || ("event " + lastEvent)) + "</b>" +
      (lastDate ? '<em>' + esc(lastDate) + "</em>" : "") +
      // "when did this last actually talk to Raid-Helper" is the question a
      // silently-polling page owes its reader. Without it, a stale comp and a
      // fresh one look identical.
      '<em class="rhage" title="last checked">' + esc(ago(lastFetch)) + "</em>" +
      '<button class="rhrefresh" type="button" aria-label="check for new '
      + 'signups now" title="check for new signups now">&#8635;</button>' +
      '<button class="rhclear" type="button" aria-label="clear the loaded raid"' +
      ' title="clear the loaded raid">&times;</button>';
  }

  function drawRaid() {
    drawPill();
    if (!RAID.length && !BASE.length) {
      rhState.hidden = true;
      if (editBox) editBox.hidden = true;
      return;
    }
    var g = gaps();
    say('<b>' + RAID.length + ' in the raid</b>' +
        (lastBench ? ' <span>(' + lastBench + ' benched)</span>' : "") +
        (g.length
          ? ' <span class="gapline">no ' + esc(g.join(", ")).toLowerCase() +
            "</span>"
          : ' <span class="okline">every tool covered</span>') +
        (lastUnresolved.length
          ? ' <span class="unmatched">could not place: ' +
            esc(lastUnresolved.join(", ")) + "</span>"
          : ""));
    // The full list is always on, in the band the class chips used to occupy.
    // It was behind a "who's here" toggle for one build and that was wrong:
    // the roster IS the context for every number on the page, and hiding it
    // makes you click to find out whether the grid is telling you about ten
    // people or about twenty-one classes.
    drawEditor();
  }

  /* ---- the raid list: drop a no-show, add a walk-in ------------------ */
  var editBox = null;

  function specOptions() {
    var out = [];
    Object.keys(SPEC).sort().forEach(function (c) {
      SPEC[c].s.forEach(function (s) { out.push(c + " · " + s); });
    });
    return out;
  }

  function drawEditor() {
    if (!editBox) {
      editBox = document.createElement("div");
      editBox.className = "rhedit-panel";
      rhState.parentNode.appendChild(editBox);
    }
    var rowsHtml = RAID.map(function (p, i) {
      return '<span class="pl' + (p.manual ? " man" : "") + '">' +
        (p.e ? '<img src="https://cdn.discordapp.com/emojis/' + esc(p.e) +
               '.png?size=32" width="15" height="15" alt="" loading="lazy">' : "") +
        '<b>' + esc(p.n || "(unnamed)") + "</b><em>" + esc(p.c) + " " +
        esc(p.s) + "</em>" +
        '<button type="button" class="pdrop" data-i="' + i +
        '" aria-label="remove">&times;</button></span>';
    }).join("");
    var back = EDITS.drops.length
      ? '<button type="button" class="pundo">restore ' + EDITS.drops.length +
        " removed</button>"
      : "";
    editBox.innerHTML =
      '<div class="plrow">' + (rowsHtml || '<em class="none">nobody</em>') +
      "</div>" +
      '<form class="paddrow">' +
      '<label class="editbox pbox"><input class="pspec" list="specopts" ' +
      'placeholder="add a spec — e.g. Bloodmage · Sanguine" autocomplete="off"></label>' +
      '<label class="editbox pbox pname"><input class="pnm" ' +
      'placeholder="name (optional)" autocomplete="off"></label>' +
      '<button type="submit" class="padd">add</button>' + back + "</form>" +
      '<datalist id="specopts">' +
      specOptions().map(function (o) {
        return '<option value="' + esc(o) + '">';
      }).join("") + "</datalist>";
    editBox.hidden = false;
  }

  document.addEventListener("click", function (ev) {
    var t = ev.target;
    if (t.classList.contains("pdrop")) {
      var p = RAID[+t.dataset.i];
      if (!p) return;
      if (p.manual) {
        // a hand-added row is removed outright rather than remembered as a
        // drop -- otherwise removing it would leave a tombstone forever
        var key = (p.n || "") + "|" + p.c + "|" + p.i;
        EDITS.adds = EDITS.adds.filter(function (a) {
          var h = resolveSpec(a.spec);
          return !h || ((a.name || "") + "|" + h.c + "|" + h.i) !== key;
        });
      } else {
        EDITS.drops.push(pid(p));
      }
      saveEdits(); rebuild();
      return;
    }
    if (t.classList.contains("pundo")) {
      EDITS.drops = []; saveEdits(); rebuild();
    }
  });

  document.addEventListener("submit", function (ev) {
    if (!ev.target.classList.contains("paddrow")) return;
    ev.preventDefault();
    var f = ev.target;
    var raw = f.querySelector(".pspec").value.trim();
    if (!raw) return;
    // "Bloodmage · Sanguine" or just "sanguine" -- the spec alone is enough,
    // and it is what someone types when they are told "we got a Sanguine".
    var spec = raw.indexOf("·") >= 0 ? raw.split("·").pop().trim() : raw;
    if (!resolveSpec(spec)) {
      f.querySelector(".pspec").setAttribute("aria-invalid", "true");
      return;
    }
    EDITS.adds.push({ spec: spec, name: f.querySelector(".pnm").value.trim() });
    saveEdits(); rebuild();
    f.querySelector(".pspec").value = "";
    f.querySelector(".pnm").value = "";
    f.querySelector(".pspec").focus();
  });

  function applyRaid(data, id) {
    var parsed = parseSignups((data && data.signUps) || []);
    BASE = parsed.list;
    lastBench = parsed.benched;
    lastUnresolved = parsed.unresolved;
    lastEvent = id;
    lastTitle = (data && (data.title || data.displayTitle)) || "";
    lastDate = (data && data.date) || "";
    lastFetch = Date.now();
    loadEdits();
    try { localStorage.setItem(IDKEY, id); } catch (e) {}
    rebuild();
  }

  /* POLLING, AND WHY IT IS SLOW.
   *
   * Signups move right up to invite time, so a page opened at 6pm and read at
   * 7pm is lying. But a raid roster is not a stock ticker -- it changes a few
   * times an hour at most, and this is somebody else's free API. So: a slow
   * 20-minute background poll, a manual refresh for "someone just signed up,
   * check now", and -- the one that actually does the work -- a refetch when
   * the tab regains focus after being away a while. The real pattern is
   * alt-tab to Discord, see a signup, alt-tab back, and focus catches that the
   * instant it matters where a timer would not.
   *
   * Polling only runs while the tab is visible. Nobody needs a backgrounded
   * tab hitting raid-helper.dev every 20 minutes for a raid that ended.
   */
  var POLL_MS = 20 * 60 * 1000;      // background cadence
  var STALE_MS = 5 * 60 * 1000;      // on refocus, refetch if older than this

  function schedulePoll() {
    if (pollTimer) clearTimeout(pollTimer);
    pollTimer = setTimeout(function () {
      if (document.visibilityState === "visible" && lastEvent) {
        load(lastEvent, true);
      } else {
        schedulePoll();          // hidden: skip this turn, keep the loop alive
      }
    }, POLL_MS);
  }

  function load(id, quiet) {
    if (!id || inFlight) return;
    inFlight = true;
    // A background poll must never blank the roster that is on screen. Only a
    // first, deliberate load gets to say "loading".
    if (!quiet) say("loading raid " + esc(id) + "…");
    else if (rhPill) rhPill.classList.add("busy");
    fetch(RH + encodeURIComponent(id))
      .then(function (r) {
        if (!r.ok) throw new Error("Raid-Helper returned " + r.status);
        return r.json();
      })
      .then(function (d) {
        if (!d || !d.signUps) throw new Error("no signups in that event");
        applyRaid(d, id);
      })
      .catch(function (e) {
        // Say what actually failed. "Could not load" sends someone to re-check
        // an event id that was fine. A failed POLL keeps the roster it already
        // has and flags itself on the pill -- losing tonight's comp because a
        // background request timed out would be the worst outcome here.
        if (quiet) {
          if (rhPill) rhPill.classList.add("stale");
        } else {
          say('<span class="err">' + esc(e.message) +
              "</span> — check the event id, or that the event still exists.");
        }
      })
      .then(function () {
        inFlight = false;
        if (rhPill) rhPill.classList.remove("busy");
        schedulePoll();
      });
  }

  // Refetch on regaining focus, but only if what we hold is actually stale.
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState !== "visible" || !lastEvent) return;
    if (Date.now() - lastFetch > STALE_MS) load(lastEvent, true);
    else drawPill();                       // at least re-age the timestamp
  });

  if (rhOpen) {
    rhOpen.addEventListener("click", function () {
      rhForm.hidden = false; rhOpen.hidden = true;
      // The filter steps aside while you are pasting an event link. You are
      // doing one thing, and sharing the row three ways squeezed the field to
      // 138px -- too narrow to see the end of a URL you just pasted.
      document.body.classList.add("rhediting");
      rhInput.focus();
    });
  }
  if (rhForm) {
    rhForm.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var id = eventId(rhInput.value);
      if (!id) { say('<span class="err">that is not an event id</span>'); return; }
      rhForm.hidden = true; rhOpen.hidden = false;
      document.body.classList.remove("rhediting");
      load(id);
    });
    $(".rhcancel").addEventListener("click", function () {
      rhForm.hidden = true; rhOpen.hidden = false;
      rhInput.value = "";
      document.body.classList.remove("rhediting");
    });
    // Escape is the other way out of a text field people reach for.
    rhInput.addEventListener("keydown", function (ev) {
      if (ev.key !== "Escape") return;
      ev.stopPropagation();
      rhForm.hidden = true; rhOpen.hidden = false;
      rhInput.value = "";
      document.body.classList.remove("rhediting");
    });
  }
  document.addEventListener("click", function (ev) {
    if (ev.target.classList.contains("rhrefresh")) {
      if (rhPill) rhPill.classList.remove("stale");
      load(lastEvent, true);
      return;
    }
    if (!ev.target.classList.contains("rhclear")) return;
    mine = {};
    BASE = []; RAID = [];
    EDITS = { drops: [], adds: [] };
    if (editBox) editBox.hidden = true;
    window.CoaRaid = null;   // else hover cards keep naming last night's raid
    try {
      localStorage.removeItem(KEY);
      localStorage.removeItem(IDKEY);
      localStorage.removeItem(editKey());
    } catch (e) {}
    lastEvent = ""; lastBench = 0; lastUnresolved = []; lastFetch = 0;
    if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
    rhState.hidden = true;
    lastTitle = ""; lastDate = "";
    drawPill();
    recount();
  });

  /* An event id in the URL is the shareable form: drop
   * raid-utility.html?event=1533532408056643717 in the raid channel and
   * everyone opens the page already on tonight's comp. */
  var urlId = eventId((location.search.match(/[?&]event=([^&]+)/) || [])[1]);
  var savedId = "";
  try { savedId = localStorage.getItem(IDKEY) || ""; } catch (e) {}
  if (urlId) {
    load(urlId);
  } else if (savedId) {
    // Re-fetch rather than trust the cached roster: signups move right up to
    // invite time, and a stale comp is the one thing worse than no comp.
    load(savedId);
  }

  /* ---------------------------------------------------------- 4. the filter
   *
   * Searches EVERY tab, not the open one. The panels are one per category, so
   * typing an ability name while on Overview used to look like "no results"
   * when the hit was two tabs away. Now every tab shows its own match count
   * and the total sits next to the box.
   *
   * Aliases matter as much as the fields do: this guild says rm, kox, pyro.
   * resources/class-aliases.json carries the slang and the WeakAuras load
   * tokens (Runemaster loads as SPIRITMAGE), and a query term that hits an
   * alias is expanded to the class name before matching. */
  var q = $("#uq"), box = $("#fbox"), qcount = $("#qcount");
  var abs = $$("li.ab").filter(function (li) {
    return !li.classList.contains("abhead");
  });

  var ALIAS = {};
  Object.keys(SPEC).forEach(function (c) {
    (SPEC[c].a || []).forEach(function (a) {
      (ALIAS[a] = ALIAS[a] || []).push(c);
    });
  });

  // One haystack per row/ability, built once. Grid rows previously searched
  // only the class name and the tool list, so a cooldown or a spec name in a
  // cell was invisible to the box that sits directly above them.
  abs.forEach(function (li) {
    li.dataset.q = ((li.dataset.cat || "") + " " + (li.dataset.cls || "") + " " +
      li.textContent + " " +
      (SPEC[li.dataset.cls] ? SPEC[li.dataset.cls].s.join(" ") : ""))
      .toLowerCase().replace(/\s+/g, " ");
  });
  // A grid row's haystack is its own text PLUS every ability the class owns.
  // Built from abs so the two corpora cannot drift: with the row searching
  // only its cells, a term that hit an ability description showed up in the
  // count ("15 abilities · 4 classes") while the grid showed three rows, and
  // the reader has no way to tell which number lied.
  var byClass = {};
  abs.forEach(function (li) {
    var c = li.dataset.cls;
    if (c) (byClass[c] = byClass[c] || []).push(li.dataset.q);
  });
  rows.forEach(function (r) {
    var c = r.dataset.class, cells = $$("td.mxv", r);
    r.dataset.q = [
      c, r.dataset.has,
      cells.map(function (t) { return t.title; }).join(" "),
      cells.map(function (t) { return t.textContent; }).join(" "),
      (SPEC[c] ? SPEC[c].s.join(" ") : ""),
      (byClass[c] || []).join(" ")
    ].join(" ").toLowerCase().replace(/\s+/g, " ");
  });

  // Every whitespace-separated term must match (AND), and a term matches if it
  // hits the text directly OR is an alias of a class that does.
  function terms(v) {
    return v.split(/\s+/).filter(Boolean).map(function (t) {
      var extra = ALIAS[t] || ALIAS[norm(t)];
      return { t: t, alt: extra ? extra.map(function (c) { return c.toLowerCase(); }) : null };
    });
  }
  function hit(hay, ts) {
    for (var i = 0; i < ts.length; i++) {
      var ok = hay.indexOf(ts[i].t) > -1;
      if (!ok && ts[i].alt) {
        for (var j = 0; j < ts[i].alt.length && !ok; j++) {
          ok = hay.indexOf(ts[i].alt[j]) > -1;
        }
      }
      if (!ok) return false;
    }
    return true;
  }

  function escH(x) {
    return String(x).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* The people in tonight's raid who can press THIS ability.
   *
   * Per ability, not per class: `li.dataset.specs` is the ability's own spec
   * bitstring, so a Bloodmage row for a Sanguine-only interrupt names only the
   * Sanguine Bloodmages and not the Fleshweaver sitting next to them. A player
   * whose spec never resolved is shown with a ? rather than silently claimed.
   */
  function fillWho(li) {
    var cell = li.querySelector(".abwho");
    if (!cell) return;
    if (!ROSTER) { if (cell.innerHTML) cell.innerHTML = ""; return; }
    var slot = ROSTER[li.dataset.cls], bits = li.dataset.specs;
    if (!slot) { if (cell.innerHTML) cell.innerHTML = ""; return; }
    var out = [];
    Object.keys(slot).forEach(function (i) {
      var idx = +i;
      if (idx >= 0 && bits && bits.charAt(idx) !== "1") return;
      slot[i].forEach(function (p) { out.push({ p: p, q: idx < 0 }); });
    });
    var html = out.map(function (o) {
      return '<i class="' + (o.q ? "q" : "") + '"' +
        ' title="' + escH(o.p.n || "unnamed") + " — " + escH(o.p.s) + '">' +
        (o.p.e ? '<img src="https://cdn.discordapp.com/emojis/' + escH(o.p.e) +
                 '.png?size=32" width="14" height="14" alt="" loading="lazy">' : "") +
        escH(o.p.n || o.p.s) + "</i>";
    }).join("");
    if (cell.innerHTML !== html) cell.innerHTML = html;
  }

  function apply() {
    var v = q.value.trim().toLowerCase();
    var ts = terms(v);
    var ros = Object.keys(mine).length > 0;
    box.classList.toggle("has", !!v);

    rows.forEach(function (r) {
      var ok = !v || hit(r.dataset.q, ts);
      r.hidden = !ok;
      if (!ok && r.classList.contains("open")) {
        r.classList.remove("open");
        kits[r.dataset.class].hidden = true;
      }
    });

    var perCat = {}, total = 0, classes = {};
    abs.forEach(function (li) {
      // The TEXT FILTER hides. The raid does NOT -- it ranks.
      //
      // A loaded raid used to hide every ability belonging to a class you did
      // not bring, so opening the Interrupt tab showed only your own kit and
      // the question "who could we ask to swap in" had no answer on the page.
      // Now yours sort to the top and everyone else's stay underneath, dimmed:
      // the list still answers "what do we have" first and "what exists"
      // second, instead of pretending the rest of the game is not there.
      var ok = !v || hit(li.dataset.q, ts);
      li.hidden = !ok;
      var out = ros && li.dataset.cls && !mine[li.dataset.cls];
      li.classList.toggle("notmine", !!out);
      li.classList.toggle("nospec",
        !!mine[li.dataset.cls] && !reach(li.dataset.cls, li.dataset.specs));
      fillWho(li);
      if (!ok) return;
      // Counts stay scoped to the raid when one is loaded -- "7 abilities"
      // must mean seven you can actually press.
      if (out) return;
      // count once per ability, not once per rendered copy (kit rows repeat
      // the same ability inside their class panel)
      if (li.closest("tr.kitrow")) return;
      total++;
      classes[li.dataset.cls] = 1;
      var cat = li.closest("section.panel");
      if (cat) perCat[cat.id.replace("panel-", "")] =
        (perCat[cat.id.replace("panel-", "")] || 0) + 1;
    });

    // Each tab reports its own hits, so a match on another tab is visible from
    // wherever you are standing.
    // Badge precedence: an active search wins, then the loaded raid's
    // coverage, then the page-wide ability total it was built with.
    $$(".tab").forEach(function (t) {
      var i = $("i", t);
      if (!i) return;
      if (!i.dataset.all) i.dataset.all = i.textContent;
      var cat = t.dataset.panel, n, mode;
      if (v) { n = perCat[cat] || 0; mode = "find"; }
      // A tab with no grid column keeps its page-wide total under a loaded
      // raid: there is no column to count against, and showing 0 read as
      // "your raid brings none of these" when the truth is all 21 classes do.
      else if (cover && !t.dataset.nocol) { n = cover[cat] || 0; mode = "raid"; }
      else { n = i.dataset.all; mode = ""; }
      i.textContent = n;
      t.classList.toggle("nohit", (mode === "find") && n === 0);
      // A tool the raid has nobody for is the headline, so it is flagged red
      // rather than just reading zero -- but never for the trash band, where
      // "no stun" is not a problem.
      t.classList.toggle("nocover",
        mode === "raid" && n === 0 && !t.classList.contains("tb-trash"));
      i.title = mode === "raid"
        ? n + " of your raid bring this (" + i.dataset.all + " abilities in the game)"
        : "";
    });

    if (qcount) {
      qcount.hidden = !v;
      var nc = Object.keys(classes).length;
      qcount.textContent = total
        ? total + (total === 1 ? " ability" : " abilities") + " · " +
          nc + (nc === 1 ? " class" : " classes")
        : "nothing matches “" + q.value.trim() + "”";
      qcount.classList.toggle("none", !!v && !total);
    }

    $$("section.utilsec").forEach(function (s) {
      s.classList.toggle("empty",
        !!v && !$$("li.ab", s).some(function (li) { return !li.hidden; }));
    });
  }

  q.addEventListener("input", apply);
  $("#uclear").addEventListener("click", function () {
    q.value = ""; apply(); q.focus();
  });
  // The box prints a "/" prefix like a command palette. It was decoration --
  // the key was never bound, so the affordance was a lie. It is bound now.
  document.addEventListener("keydown", function (ev) {
    var t = ev.target, tag = (t.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || t.isContentEditable) {
      if (ev.key === "Escape" && t === q) { q.value = ""; apply(); q.blur(); }
      return;
    }
    if (ev.key === "/" && !ev.metaKey && !ev.ctrlKey && !ev.altKey) {
      ev.preventDefault();
      q.focus();
      q.select();
    }
  });
  recount();
}());

/* tabs, class filter, hover card ------------------------------------------
   All three are enhancements. Without JS the tab bar and the class filter are
   hidden by the noscript rule and every panel renders open, so the page falls
   back to the long-scroll version rather than to nothing. */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) {
    return Array.prototype.slice.call((r || document).querySelectorAll(s));
  };

  /* ---- tabs ---------------------------------------------------------- */
  var tabs = $$(".tab"), panels = $$(".panel");
  function show(name, push) {
    tabs.forEach(function (t) { t.classList.toggle("on", t.dataset.panel === name); });
    panels.forEach(function (p) { p.hidden = p.id !== "panel-" + name; });
    if (push && history.replaceState) history.replaceState(null, "", "#" + name);
    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
  }
  tabs.forEach(function (t) {
    t.addEventListener("click", function () { show(t.dataset.panel, true); });
  });
  // A deep link -- or a scarcity tile, which links to #<cat> -- opens that tab.
  function fromHash() {
    var h = (location.hash || "").replace(/^#/, "");
    if (h && $("#panel-" + h)) show(h, false);
  }
  window.addEventListener("hashchange", fromHash);
  fromHash();

  /* The class filter that used to live here is gone -- it WAS the roster,
     implemented twice. See block 2 above. */

  /* ---- how-to modal --------------------------------------------------
     The hard step is not pasting an id, it is knowing that Raid-Helper hides a
     `Web View` link at the foot of its Discord embed and that Discord puts an
     interstitial in front of it. Three screenshots beat three sentences. */
  var modal = $(".rhmodal");
  if (modal) {
    var lastFocus = null;
    var openModal = function () {
      lastFocus = document.activeElement;
      modal.hidden = false;
      document.body.classList.add("rhlock");
      var x = $(".rhx", modal);
      if (x) x.focus();
    };
    var closeModal = function () {
      modal.hidden = true;
      document.body.classList.remove("rhlock");
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    };
    document.addEventListener("click", function (ev) {
      if (ev.target.closest(".rhhelp")) { openModal(); return; }
      if (ev.target.closest(".rhx")) { closeModal(); return; }
      // click the backdrop, not the sheet
      if (ev.target === modal) closeModal();
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && !modal.hidden) closeModal();
    });
  }

  /* ---- hover card ---------------------------------------------------- */
  var raw = $("#abdata");
  if (!raw) return;
  var DATA = JSON.parse(raw.textContent);
  var card = document.createElement("div");
  card.className = "abcard";
  card.hidden = true;
  document.body.appendChild(card);

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  /* Who in tonight's raid can actually press this one.
   *
   * `a.sm` is the ability's own spec bitstring, not the cell's -- a cell unions
   * every ability in it, so asking the cell would name people who can press a
   * DIFFERENT ability in the same square. A player counts if their spec index
   * is set in that bitstring, or if their spec never resolved (index -1), in
   * which case they are shown with a "?" rather than silently claimed. */
  function bearers(a) {
    var R = window.CoaRaid && window.CoaRaid.roster;
    if (!R || !a.sm || !R[a.c]) return "";
    var slot = R[a.c], out = [];
    Object.keys(slot).forEach(function (i) {
      var idx = +i;
      if (idx >= 0 && a.sm.charAt(idx) !== "1") return;
      slot[i].forEach(function (p) { out.push({ p: p, unsure: idx < 0 }); });
    });
    if (!out.length) {
      // Nobody can press it -- but the class IS in the raid, which is exactly
      // the case a struck cooldown raises and does not answer. Naming who you
      // brought and on what spec turns "why is this crossed out" into "because
      // both your Felsworn are Tyrant" without a trip back to the roster line.
      var wrong = [];
      Object.keys(slot).forEach(function (i) {
        slot[i].forEach(function (p) { wrong.push(p); });
      });
      if (!wrong.length) return "";
      return '<p class="acwho miss"><span class="no">not on your ' +
        esc(a.c) + ":</span>" + wrong.map(function (p) {
          return '<span class="w">' + esc(p.n) + "<em>" + esc(p.s) + "</em></span>";
        }).join("") + "</p>";
    }
    return '<p class="acwho">' + out.map(function (o) {
      var img = o.p.e
        // The guild's own spec emoji, straight off Discord's CDN -- the same
        // icon they clicked to sign up.
        ? '<img src="https://cdn.discordapp.com/emojis/' + esc(o.p.e) +
          '.png?size=32" width="16" height="16" alt="" loading="lazy">'
        : "";
      return '<span class="w' + (o.unsure ? " q" : "") + '">' + img +
        esc(o.p.n) + "<em>" + esc(o.p.s) + "</em></span>";
    }).join("") + "</p>";
  }

  function one(a) {
    var ico = a.i
      ? '<img src="assets/spell-icons/' + esc(a.i) + '.jpg" width="34" height="34" alt="">'
      : '<span class="ph"></span>';
    var chips = [];
    if (a.m && a.m.indexOf("int") >= 0) chips.push('<i class="c int">interrupts NPC casts</i>');
    if (a.m && a.m.indexOf("noicon") >= 0) chips.push('<i class="c warn">unverified in game</i>');
    if (a.obs) chips.push('<i class="c ok">' + esc(a.obs) + "</i>");
    var spec = esc(a.spec) + (a.rc ? ' <em>' + esc(a.rc) + "</em>" : "");
    return (
      '<div class="ac"><div class="achead">' + ico +
      '<div><b><a href="' + esc(a.u) + '" target="_blank" rel="noopener noreferrer">' +
      esc(a.n) + "</a></b><span>" + esc(a.c) + " &middot; " + spec + "</span></div>" +
      '<span class="accat b-' + esc(a.band) + '">' + esc(a.cat) + "</span></div>" +
      '<dl class="acstats">' +
      "<dt>Cooldown</dt><dd>" + esc(a.cd === "none" ? "—" : a.cd) + "</dd>" +
      "<dt>Cost</dt><dd>" + esc(a.cost) + "</dd>" +
      "<dt>Cast</dt><dd>" + esc(a.cast) + "</dd>" +
      "</dl>" +
      (chips.length ? '<p class="acchips">' + chips.join("") + "</p>" : "") +
      '<p class="acdesc">' + esc(a.d) + "</p>" + bearers(a) + "</div>"
    );
  }
  function place(ev) {
    var pad = 14, w = card.offsetWidth, h = card.offsetHeight;
    var x = ev.clientX + pad, y = ev.clientY + pad;
    if (x + w > window.innerWidth - 8) x = ev.clientX - w - pad;
    if (y + h > window.innerHeight - 8) y = Math.max(8, window.innerHeight - h - 8);
    card.style.left = x + "px";
    card.style.top = y + "px";
  }
  function bind(el, ids) {
    // THE NATIVE TOOLTIP HAS TO GO, and it cannot be suppressed -- the browser
    // renders title= on its own schedule, wherever it likes, and it was
    // landing on top of this card a second after it opened, covering the
    // ability name with a worse copy of the same sentence. It is moved to a
    // data attribute instead of deleted, so it is still there for anything
    // that wants it and the server-rendered no-JS page keeps it.
    if (el.title) { el.dataset.tip = el.title; el.removeAttribute("title"); }
    el.addEventListener("mouseenter", function (ev) {
      var list = ids.filter(function (i) { return DATA[i]; });
      if (!list.length) return;
      card.innerHTML = list.map(function (i) { return one(DATA[i]); }).join("");
      card.hidden = false;
      place(ev);
    });
    el.addEventListener("mousemove", place);
    el.addEventListener("mouseleave", function () { card.hidden = true; });
  }
  $$("td.mxv[data-ids]").forEach(function (td) {
    bind(td, (td.dataset.ids || "").split(",").filter(Boolean));
  });
  $$(".ab[data-sid]").forEach(function (li) { bind(li, [li.dataset.sid]); });
}());
