// Live class filtering for the index page.
//
// All 21 cards are rendered server-side and simply hidden as you type -- there
// is no fetch, no template, and the page works with JS off (you just get the
// full unfiltered grid, which is the correct fallback).
//
// Searchable fields per card, from data- attributes written by mksite.py:
//   data-name    display name        "Runemaster"
//   data-specs   spec names          "glyphic engravement riftblade"
//   data-token   load token          "SPIRITMAGE"
//   data-id      class id            "27"
// The token matters more than it looks: CoA load tokens are NOT derivable from
// the class name (Runemaster loads as SPIRITMAGE, Templar as MONK), so someone
// reading a token out of an export has no way to get back to the class without
// this.
(function () {
  "use strict";

  var grid = document.getElementById("grid");
  if (!grid) return;

  var input = document.getElementById("q");
  var box = document.getElementById("searchbox");
  var clear = document.getElementById("clear");
  var countEl = document.getElementById("count");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var resetBtn = document.getElementById("reset");
  var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));

  var state = "all";
  var cursor = -1;
  var visible = cards.slice();

  // Fold accents and punctuation so "knight of xoroth", "Knight-of-Xoroth"
  // and "knightofxoroth" all match the same card.
  function norm(s) {
    return (s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")   // strip combining marks
      .replace(/[^a-z0-9 ]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  cards.forEach(function (card) {
    card._name = card.dataset.name || "";
    card._hay = norm([
      card.dataset.name,
      card.dataset.specs,
      card.dataset.token,
      card.dataset.id
    ].join(" "));
    // Cache the un-highlighted title so repeated keystrokes rebuild from the
    // original rather than from already-marked-up HTML.
    card._title = card.querySelector("h3");
  });

  function matches(card, terms) {
    for (var i = 0; i < terms.length; i++) {
      if (card._hay.indexOf(terms[i]) === -1) return false;
    }
    return true;
  }

  // Rebuild the title with <mark> around the first term that appears in the
  // NAME (terms may have matched on spec or token instead, which we do not
  // highlight -- marking nothing is better than marking the wrong thing).
  function highlight(card, terms) {
    var h = card._title;
    if (!h) return;
    var name = card._name;
    if (!terms.length) { h.textContent = name; return; }

    // Search the RAW lowercased name, not the normalised one. norm() collapses
    // punctuation runs, so an offset into it does not reliably index back into
    // the original -- "Knight-of-Xoroth" normalises to a different length. The
    // raw scan can only ever find a real substring, so the slice is always safe.
    var lower = name.toLowerCase();
    var at = -1, len = 0;
    for (var i = 0; i < terms.length; i++) {
      var p = lower.indexOf(terms[i]);
      if (p !== -1 && (at === -1 || p < at)) { at = p; len = terms[i].length; }
    }
    if (at === -1) { h.textContent = name; return; }

    h.textContent = "";
    h.appendChild(document.createTextNode(name.slice(0, at)));
    var m = document.createElement("mark");
    m.textContent = name.slice(at, at + len);
    h.appendChild(m);
    h.appendChild(document.createTextNode(name.slice(at + len)));
  }

  function apply() {
    var raw = input ? input.value : "";
    var terms = norm(raw).split(" ").filter(Boolean);
    visible = [];

    cards.forEach(function (card) {
      var okState =
        state === "all" ||
        (state === "ready" && card.dataset.state === "ready") ||
        (state === "planned" && card.dataset.state === "planned");
      var ok = okState && matches(card, terms);
      card.hidden = !ok;
      if (ok) { visible.push(card); highlight(card, terms); }
    });

    if (box) box.classList.toggle("has", raw.length > 0);
    if (countEl) {
      countEl.innerHTML =
        "<b>" + visible.length + "</b> of " + cards.length + " classes";
    }
    document.body.classList.toggle("noresults", visible.length === 0);

    setCursor(-1);
    syncUrl(raw);
  }

  // Keep the query in the URL so a filtered view can be linked. replaceState,
  // not pushState -- every keystroke in the back stack would be unusable.
  function syncUrl(raw) {
    if (!window.history || !history.replaceState) return;
    var url = new URL(window.location.href);
    if (raw) url.searchParams.set("q", raw); else url.searchParams.delete("q");
    if (state !== "all") url.searchParams.set("show", state);
    else url.searchParams.delete("show");
    history.replaceState(null, "", url.pathname + url.search + url.hash);
  }

  function setCursor(i) {
    cards.forEach(function (c) { c.classList.remove("cursor"); });
    cursor = i;
    if (i >= 0 && visible[i]) {
      visible[i].classList.add("cursor");
      visible[i].scrollIntoView({ block: "nearest" });
    }
  }

  // Column count comes from the resolved grid template, so arrow keys follow
  // the layout at any breakpoint without a hard-coded number.
  function cols() {
    var t = getComputedStyle(grid).gridTemplateColumns;
    var n = t ? t.split(" ").filter(Boolean).length : 1;
    return Math.max(1, n);
  }

  function move(d) {
    if (!visible.length) return;
    var next = cursor < 0 ? (d > 0 ? 0 : visible.length - 1) : cursor + d;
    setCursor(Math.max(0, Math.min(visible.length - 1, next)));
  }

  if (input) {
    input.addEventListener("input", apply);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { input.value = ""; apply(); input.blur(); }
      else if (e.key === "ArrowDown") { e.preventDefault(); move(cols()); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-cols()); }
      else if (e.key === "ArrowRight" && cursor >= 0) { e.preventDefault(); move(1); }
      else if (e.key === "ArrowLeft" && cursor >= 0) { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") {
        // With no cursor, Enter takes the single result if there is exactly
        // one -- type three letters, hit Enter, you are on the page.
        var target = cursor >= 0 ? visible[cursor]
                   : (visible.length === 1 ? visible[0] : null);
        if (target && target.tagName === "A") { e.preventDefault(); target.click(); }
      }
    });
  }

  if (clear) {
    clear.addEventListener("click", function () {
      input.value = ""; apply(); input.focus();
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      input.value = "";
      state = "all";
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", String(c.dataset.show === "all"));
      });
      apply(); input.focus();
    });
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      state = chip.dataset.show;
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", String(c === chip));
      });
      apply();
    });
  });

  // "/" to focus from anywhere, the convention every search-first site uses.
  // Guarded so it does not steal the key while you are typing in a field.
  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" ||
              t.isContentEditable)) return;
    e.preventDefault();
    if (input) { input.focus(); input.select(); }
  });

  // Restore ?q= / ?show= on load so a shared link opens filtered.
  (function boot() {
    var p = new URLSearchParams(window.location.search);
    var q = p.get("q");
    var show = p.get("show");
    if (q && input) input.value = q;
    if (show === "ready" || show === "planned") {
      state = show;
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", String(c.dataset.show === show));
      });
    }
    apply();
  })();
})();
