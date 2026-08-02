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

  /* ------------------------------------------------------------ 2. roster */
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
    var btn = $("#rosterclear");
    btn.hidden = !on;
    $("#rostern").textContent = picked.length;

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

  rows.forEach(function (r) {
    var pick = $(".pick", r);
    if (!pick) return;
    pick.addEventListener("click", function () {
      var c = r.dataset.class;
      mine[c] = !mine[c];
      r.classList.toggle("mine", !!mine[c]);
      try { localStorage.setItem(KEY, JSON.stringify(mine)); } catch (e) {}
      recount();
    });
    if (mine[r.dataset.class]) r.classList.add("mine");
  });
  $("#rosterclear").addEventListener("click", function () {
    mine = {};
    try { localStorage.removeItem(KEY); } catch (e) {}
    rows.forEach(function (r) { r.classList.remove("mine"); });
    recount();
  });
  recount();

  /* ------------------------------------------------------------ 3. filter */
  var q = $("#uq"), box = $("#fbox"), abs = $$("li.ab");
  function apply() {
    var v = q.value.trim().toLowerCase();
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
      li.hidden = !!v && hay.indexOf(v) === -1;
    });
    $$("section.utilsec").forEach(function (s) {
      s.classList.toggle("empty",
        !!v && !$$("li.ab", s).some(function (li) { return !li.hidden; }));
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
