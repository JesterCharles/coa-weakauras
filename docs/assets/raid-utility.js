/* Raid utility page. Three interactions, all optional: with JS off the page
 * is the scarcity strip + the full coverage grid + all ten sections, which is
 * everything except the class-kit expansion -- and every one of those
 * abilities is still on the page below, in its category section. Nothing is
 * hidden behind JS that is not also printed somewhere static.
 *
 * 1. Expand a grid row into that class's full kit.       (question 5)
 * 2. Pick classes into "my roster"; the scarcity strip   (questions 1-4, for
 *    recounts against the roster instead of all 21.       the raid you have)
 * 3. Text filter over class + ability names.
 */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) {
    return Array.prototype.slice.call((r || document).querySelectorAll(s));
  };

  var rows = $$("tr.mxr");
  var kits = {};
  $$("tr.kitrow").forEach(function (k) { kits[k.dataset.class] = k; });

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

  /* ------------------------------------------------------------ 2. roster
   *
   * ONE selection with two entry points -- the icon band at the top of the
   * page and the icon on every grid row -- rather than the two overlapping
   * mechanisms this page used to have. The old "filter by class" band dimmed
   * grid rows to .18 and hid ability rows; the old roster picker dimmed grid
   * rows to .26 and recounted the scarcity strip. Same gesture, same icons,
   * two different meanings and no way to tell which one you had just used.
   * Now: picking a class does all of it, from either place. */
  var KEY = "coa-roster";
  var mine = {};
  try { mine = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}

  var counts = {};                      // cat -> classes that have it
  rows.forEach(function (r) {
    $$("td.mxv", r).forEach(function (td) {
      var i = Array.prototype.indexOf.call(r.children, td);
      (counts[i] = counts[i] || []).push(r.dataset.class);
    });
  });
  // column index -> category, read off the header links
  var cols = {};
  $$("thead th.mxh a").forEach(function (a, i) {
    cols[i + 1] = a.getAttribute("href").slice(1);
  });

  function recount() {
    var picked = Object.keys(mine).filter(function (k) { return mine[k]; });
    var on = picked.length > 0;
    // NB "roster" is already a class in site.css (the index icon band),
    // so the body flag is namespaced.
    document.body.classList.toggle("mypick", on);
    var btn = $(".cfclear");
    if (btn) btn.hidden = !on;
    var n = $("#rostern");
    if (n) n.textContent = picked.length;

    // the top icon band and the grid rows are two views of the same state
    $$(".cf").forEach(function (b) {
      b.classList.toggle("on", !!mine[b.dataset.class]);
    });
    rows.forEach(function (r) {
      r.classList.toggle("mine", !!mine[r.dataset.class]);
    });
    // and the ability lists show only the roster, so a category tab answers
    // "what do MY classes bring" without a second control. apply() is the
    // single writer of li.hidden -- roster and text filter compose there
    // rather than overwriting each other.
    apply();

    Object.keys(cols).forEach(function (i) {
      var cat = cols[i];
      var all = counts[i] || [];
      var n = on ? all.filter(function (c) { return mine[c]; }).length
                 : all.length;
      var total = on ? picked.length : rows.length;
      var b = $('[data-count="' + cat + '"]');
      if (!b) return;
      b.textContent = n;
      b.parentNode.lastChild.textContent = "/" + total;
      var bar = $('[data-bar="' + cat + '"]');
      bar.style.width = (total ? Math.round(100 * n / total) : 0) + "%";
      // A tool your roster does not bring at all is the headline of the
      // whole page, so that tile is flagged, not dimmed.
      bar.closest("li.sc").classList.toggle("gap", on && n === 0);
    });
  }

  function toggle(c) {
    mine[c] = !mine[c];
    if (!mine[c]) delete mine[c];
    try { localStorage.setItem(KEY, JSON.stringify(mine)); } catch (e) {}
    recount();
  }
  rows.forEach(function (r) {
    var pick = $(".pick", r);
    if (pick) pick.addEventListener("click", function () {
      toggle(r.dataset.class);
    });
  });
  $$(".cf").forEach(function (b) {
    b.addEventListener("click", function () { toggle(b.dataset.class); });
  });
  var cfc = $(".cfclear");
  if (cfc) cfc.addEventListener("click", function () {
    mine = {};
    try { localStorage.removeItem(KEY); } catch (e) {}
    recount();
  });
  recount();

  /* ------------------------------------------------------------ 3. filter
   * The single writer of `hidden` on both grid rows and ability rows: text
   * query AND roster, composed. Called by recount() too, which is why it
   * looks its elements up lazily -- recount runs before this block. */
  var q, box, abs;
  function apply() {
    q = q || $("#uq"); box = box || $("#fbox"); abs = abs || $$("li.ab");
    var v = q.value.trim().toLowerCase();
    var picked = Object.keys(mine).filter(function (k) { return mine[k]; });
    var ros = picked.length > 0;
    box.classList.toggle("has", !!v);
    rows.forEach(function (r) {
      var hay = (r.dataset.class + " " + r.dataset.has + " " + r.title)
                  .toLowerCase();
      var hit = !v || hay.indexOf(v) > -1;
      r.hidden = !hit;
      if (!hit && r.classList.contains("open")) {
        r.classList.remove("open");
        kits[r.dataset.class].hidden = true;
      }
    });
    abs.forEach(function (li) {
      var hay = ((li.dataset.cat || "") + " " + li.textContent).toLowerCase();
      var cls = $(".abcls b", li);
      li.hidden = (!!v && hay.indexOf(v) === -1) ||
                  (ros && !!cls && !mine[cls.textContent]);
    });
    $$("section.utilsec").forEach(function (s) {
      s.classList.toggle("empty",
        (!!v || ros) && !$$("li.ab", s).some(function (li) { return !li.hidden; }));
    });
    // a band heading with nothing left under it goes too
    $$(".bandblock, .lowsec").forEach(function (bb) {
      bb.classList.toggle("empty", !!v && !$$("section.utilsec", bb)
        .some(function (s) { return !s.classList.contains("empty"); }));
    });
  }
  q.addEventListener("input", apply);
  $("#uclear").addEventListener("click", function () {
    q.value = ""; apply(); q.focus();
  });
  // give every grid row a title carrying its ability names, so the filter
  // matches ability text in the grid too
  rows.forEach(function (r) {
    r.title = $$("td.mxv", r).map(function (t) { return t.title; }).join(" ");
  });
  apply();
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
      '<div><b>' + esc(a.n) + "</b><span>" + esc(a.c) + " &middot; " + spec + "</span></div>" +
      '<span class="accat b-' + esc(a.band) + '">' + esc(a.cat) + "</span></div>" +
      '<dl class="acstats">' +
      "<dt>Cooldown</dt><dd>" + esc(a.cd === "none" ? "—" : a.cd) + "</dd>" +
      "<dt>Cost</dt><dd>" + esc(a.cost) + "</dd>" +
      "<dt>Cast</dt><dd>" + esc(a.cast) + "</dd>" +
      "</dl>" +
      (chips.length ? '<p class="acchips">' + chips.join("") + "</p>" : "") +
      '<p class="acdesc">' + esc(a.d) + "</p></div>"
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
