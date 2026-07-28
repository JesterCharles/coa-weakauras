// Class explorer for the index page: filter the list, drive the preview pane.
//
// The list is rendered server-side and rows are only hidden as you type, so
// with JS off you still get every class as a working link. The preview pane is
// pure enhancement -- CSS keeps it hidden until we set body.js, because an
// empty panel with nothing to drive it is worse than no panel.
//
// Searchable fields, from data- attributes written by mksite.py:
//   data-name    display name   "Knight of Xoroth"
//   data-specs   spec names     "Glyphic Engravement Riftblade"
// That is deliberately all of it. Load tokens and class ids are WeakAuras and
// database internals -- a player looking for their class knows the name and
// the spec names, and nothing else belongs in the match.
(function () {
  "use strict";

  var list = document.getElementById("classlist");
  if (!list) return;

  document.body.classList.add("js");

  var input = document.getElementById("q");
  var box = document.getElementById("searchbox");
  var clear = document.getElementById("clear");
  var countEl = document.getElementById("count");
  var resetBtn = document.getElementById("reset");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var rows = Array.prototype.slice.call(list.querySelectorAll(".row"));

  var pv = document.getElementById("preview");
  var pvIcon = document.getElementById("pvicon");
  var pvKicker = document.getElementById("pvkicker");
  var pvName = document.getElementById("pvname");
  var pvSpecs = document.getElementById("pvspecs");
  var pvNote = document.getElementById("pvnote");
  var pvAction = document.getElementById("pvaction");

  var state = "all";
  var visible = rows.slice();
  var current = null;

  // Fold punctuation and accents so "knight of xoroth", "Knight-of-Xoroth" and
  // "knightofxoroth" all match the same row.
  function norm(s) {
    return (s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")   // strip combining marks
      .replace(/[^a-z0-9 ]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  rows.forEach(function (row) {
    row._name = row.dataset.name || "";
    row._hay = norm(row._name + " " + (row.dataset.specs || ""));
    row._title = row.querySelector(".rowname");
  });

  function matches(row, terms) {
    for (var i = 0; i < terms.length; i++) {
      if (row._hay.indexOf(terms[i]) === -1) return false;
    }
    return true;
  }

  // Mark the first term that occurs in the NAME. Scanning the raw lowercased
  // name rather than the normalised one keeps the offsets valid -- norm()
  // collapses punctuation runs and would shift them.
  function highlight(row, terms) {
    var h = row._title;
    if (!h) return;
    var name = row._name;
    if (!terms.length) { h.textContent = name; return; }

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

  function show(row) {
    if (!row || !pv) return;
    current = row;
    rows.forEach(function (r) { r.classList.toggle("on", r === row); });

    var ready = row.dataset.state === "ready";
    pv.style.setProperty("--c", row.dataset.accent || "#b4442a");

    pvIcon.src = row.dataset.icon || "";
    pvIcon.alt = "";
    pvKicker.textContent = ready ? "Pack available" : "Not built yet";
    pvName.textContent = row._name;

    var labels = (row.dataset.specLabels || "").split("|").filter(Boolean);
    var icons = (row.dataset.specIcons || "").split("|").filter(Boolean);
    pvSpecs.textContent = "";
    labels.forEach(function (label, i) {
      var li = document.createElement("li");
      if (icons[i]) {
        var img = document.createElement("img");
        img.src = icons[i];
        img.alt = "";
        img.loading = "lazy";
        li.appendChild(img);
      }
      li.appendChild(document.createTextNode(label));
      pvSpecs.appendChild(li);
    });

    pvNote.textContent = ready
      ? "Rotation, cooldowns and buffs for every spec. Displays load only for "
        + "the spec you are playing."
      : "No pack yet. Classes are built one at a time and each one follows the "
        + "same band layout, so nothing you learn here goes to waste.";

    pvAction.textContent = "";
    if (ready) {
      var a = document.createElement("a");
      a.className = "pvgo";
      a.href = row.dataset.href;
      a.textContent = "Open " + row._name + " →";
      pvAction.appendChild(a);
    } else {
      var span = document.createElement("span");
      span.className = "pvsoon";
      span.textContent = "Planned";
      pvAction.appendChild(span);
    }
  }

  function apply() {
    var raw = input ? input.value : "";
    var terms = norm(raw).split(" ").filter(Boolean);
    visible = [];

    rows.forEach(function (row) {
      var okState = state === "all" || row.dataset.state === state;
      var ok = okState && matches(row, terms);
      row.hidden = !ok;
      if (ok) { visible.push(row); highlight(row, terms); }
    });

    if (box) box.classList.toggle("has", raw.length > 0);
    if (countEl) {
      countEl.innerHTML = "<b>" + visible.length + "</b> of " + rows.length;
    }
    document.body.classList.toggle("noresults", visible.length === 0);

    // Keep the preview on the current row when it survived the filter,
    // otherwise fall to the top of what is now on screen.
    if (visible.length) {
      show(visible.indexOf(current) !== -1 ? current : visible[0]);
    }
    syncUrl(raw);
  }

  // replaceState, not pushState -- one history entry per keystroke would make
  // the back button unusable.
  function syncUrl(raw) {
    if (!window.history || !history.replaceState) return;
    var url = new URL(window.location.href);
    if (raw) url.searchParams.set("q", raw); else url.searchParams.delete("q");
    if (state !== "all") url.searchParams.set("show", state);
    else url.searchParams.delete("show");
    history.replaceState(null, "", url.pathname + url.search + url.hash);
  }

  function move(d) {
    if (!visible.length) return;
    var i = visible.indexOf(current);
    var next = i === -1 ? 0 : Math.max(0, Math.min(visible.length - 1, i + d));
    show(visible[next]);
    visible[next].scrollIntoView({ block: "nearest" });
  }

  function open(row) {
    if (row && row.dataset.state === "ready" && row.dataset.href) {
      window.location.href = row.dataset.href;
    }
  }

  rows.forEach(function (row) {
    row.addEventListener("mouseenter", function () { show(row); });
    row.addEventListener("focus", function () { show(row); });
    row.addEventListener("click", function (e) {
      // Planned rows are not links, so a click only moves the preview.
      if (row.dataset.state !== "ready") { e.preventDefault(); show(row); }
    });
  });

  if (input) {
    input.addEventListener("input", apply);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { input.value = ""; apply(); input.blur(); }
      else if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") { e.preventDefault(); open(current); }
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

  // "/" focuses search from anywhere, guarded so it does not steal the key
  // while you are already typing.
  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" ||
              t.isContentEditable)) return;
    e.preventDefault();
    if (input) { input.focus(); input.select(); }
  });

  (function boot() {
    var p = new URLSearchParams(window.location.search);
    var q = p.get("q");
    var show0 = p.get("show");
    if (q && input) input.value = q;
    if (show0 === "ready" || show0 === "planned") {
      state = show0;
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", String(c.dataset.show === show0));
      });
    }
    // Open on a shipped class rather than whatever sorts first -- the preview
    // should show something you can actually download.
    var firstReady = rows.filter(function (r) {
      return r.dataset.state === "ready";
    })[0];
    current = firstReady || rows[0] || null;
    apply();
  })();
})();
