// Class roster: filter the band, follow the pointer with a tooltip, keep the
// readout in step.
//
// The band is rendered server-side and tiles are only hidden as you type, so
// with JS off you still get every class as a working link. Everything below is
// enhancement.
//
// Searchable fields, from data- attributes written by mksite.py:
//   data-name    display name   "Knight of Xoroth"
//   data-specs   spec names     "Glyphic Engravement Riftblade"
// Deliberately all of it. Load tokens and class ids are WeakAuras and database
// internals -- a player knows the class name and the spec names.
(function () {
  "use strict";

  var roster = document.getElementById("roster");
  if (!roster) return;

  var input = document.getElementById("q");
  var box = document.getElementById("editbox");
  var clear = document.getElementById("clear");
  var countEl = document.getElementById("count");
  var resetBtn = document.getElementById("reset");
  var tiles = Array.prototype.slice.call(roster.querySelectorAll(".cls"));

  var tip = document.getElementById("tip");
  var tipName = document.getElementById("tipname");
  var tipSpecs = document.getElementById("tipspecs");
  var tipState = document.getElementById("tipstate");

  var roPortrait = document.getElementById("roportrait");
  var roName = document.getElementById("roname");
  var roSpecs = document.getElementById("rospecs");
  var roState = document.getElementById("rostate");
  var roAction = document.getElementById("roaction");

  var visible = tiles.slice();
  var current = null;

  function norm(s) {
    return (s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")   // strip combining marks
      .replace(/[^a-z0-9 ]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  // data-state is one of verified / draft / planned -- the honest three.
  // "ready" here means only "there is a pack to open".
  var STATE_TEXT = {
    verified: "Verified in game",
    draft: "Community draft",
    planned: "Not built yet"
  };

  tiles.forEach(function (t) {
    t._name = t.dataset.name || "";
    t._hay = norm(t._name + " " + (t.dataset.specs || ""));
    t._labels = (t.dataset.specLabels || "").split("|").filter(Boolean);
    t._icons = (t.dataset.specIcons || "").split("|").filter(Boolean);
    t._state = t.dataset.state || "planned";
    t._ready = t._state !== "planned";
  });

  function matches(t, terms) {
    for (var i = 0; i < terms.length; i++) {
      if (t._hay.indexOf(terms[i]) === -1) return false;
    }
    return true;
  }

  // ---------------------------------------------------------------- readout
  function select(t) {
    if (!t) return;
    current = t;
    tiles.forEach(function (o) { o.classList.toggle("on", o === t); });

    document.documentElement.style.setProperty("--c", t.dataset.accent);
    roPortrait.src = t.dataset.icon;
    roName.textContent = t._name;

    roSpecs.textContent = "";
    t._labels.forEach(function (label, i) {
      var s = document.createElement("span");
      s.className = "rospec";
      if (t._icons[i]) {
        var img = document.createElement("img");
        img.src = t._icons[i];
        img.alt = "";
        img.loading = "lazy";
        s.appendChild(img);
      }
      s.appendChild(document.createTextNode(label));
      roSpecs.appendChild(s);
    });

    if (roState) {
      // "Not built yet" already lives in the action slot; the state line
      // carries only the verified/draft distinction.
      roState.textContent = t._ready ? STATE_TEXT[t._state] || "" : "";
      roState.className = "rostate " + t._state;
    }

    roAction.textContent = "";
    if (t._ready) {
      var a = document.createElement("a");
      a.className = "rogo";
      a.href = t.dataset.href;
      a.textContent = "Open pack";
      roAction.appendChild(a);
    } else {
      var span = document.createElement("span");
      span.className = "rosoon";
      span.textContent = "Not built yet";
      roAction.appendChild(span);
    }
  }

  // ---------------------------------------------------------------- tooltip
  function showTip(t, ev) {
    tipName.textContent = t._name;
    tipName.style.color = t.dataset.accent;
    tipSpecs.textContent = t._labels.join(", ");
    tipState.textContent = STATE_TEXT[t._state] || "Not built yet";
    tipState.className = "tipstate " + t._state;
    tip.classList.add("show");
    moveTip(ev);
  }

  function moveTip(ev) {
    if (!ev || !tip.classList.contains("show")) return;
    var pad = 14;
    var r = tip.getBoundingClientRect();
    // Flip to the other side of the cursor near an edge so the tooltip is
    // never clipped by the viewport.
    var x = ev.clientX + pad;
    var y = ev.clientY + pad;
    if (x + r.width > window.innerWidth - 8) x = ev.clientX - r.width - pad;
    if (y + r.height > window.innerHeight - 8) y = ev.clientY - r.height - pad;
    tip.style.left = Math.max(8, x) + "px";
    tip.style.top = Math.max(8, y) + "px";
  }

  function hideTip() { tip.classList.remove("show"); }

  tiles.forEach(function (t) {
    t.addEventListener("mouseenter", function (e) { select(t); showTip(t, e); });
    t.addEventListener("mousemove", moveTip);
    t.addEventListener("mouseleave", hideTip);
    t.addEventListener("focus", function () { select(t); });
    t.addEventListener("click", function (e) {
      // Unbuilt classes are <button>, so a click only moves the selection.
      if (!t._ready) { e.preventDefault(); select(t); }
    });
  });

  // ----------------------------------------------------------------- filter
  function apply() {
    var raw = input ? input.value : "";
    var terms = norm(raw).split(" ").filter(Boolean);
    visible = [];

    tiles.forEach(function (t) {
      var ok = matches(t, terms);
      t.hidden = !ok;
      if (ok) visible.push(t);
    });

    if (box) box.classList.toggle("has", raw.length > 0);
    if (countEl) {
      countEl.textContent = visible.length === tiles.length
        ? tiles.length + " shown"
        : visible.length + " of " + tiles.length + " shown";
    }
    document.body.classList.toggle("noresults", visible.length === 0);
    hideTip();

    if (visible.length) {
      select(visible.indexOf(current) !== -1 ? current : visible[0]);
    }
    syncUrl(raw);
  }

  // replaceState, not pushState -- a history entry per keystroke would make
  // the back button useless.
  function syncUrl(raw) {
    if (!window.history || !history.replaceState) return;
    var url = new URL(window.location.href);
    if (raw) url.searchParams.set("q", raw); else url.searchParams.delete("q");
    history.replaceState(null, "", url.pathname + url.search + url.hash);
  }

  function move(d) {
    if (!visible.length) return;
    var i = visible.indexOf(current);
    var next = i === -1 ? 0 : Math.max(0, Math.min(visible.length - 1, i + d));
    select(visible[next]);
    visible[next].scrollIntoView({ block: "nearest", inline: "nearest" });
  }

  function open() {
    if (current && current._ready) window.location.href = current.dataset.href;
  }

  if (input) {
    input.addEventListener("input", apply);
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { input.value = ""; apply(); input.blur(); }
      else if (e.key === "ArrowRight") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); move(-1); }
      else if (e.key === "ArrowDown") { e.preventDefault(); move(perRow()); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-perRow()); }
      else if (e.key === "Enter") { e.preventDefault(); open(); }
    });
  }

  // How many tiles fit on one line right now, measured from where they
  // actually sit rather than from a hard-coded column count -- the band wraps
  // at whatever the viewport allows.
  function perRow() {
    if (visible.length < 2) return 1;
    var top = visible[0].offsetTop, n = 0;
    for (var i = 0; i < visible.length; i++) {
      if (visible[i].offsetTop !== top) break;
      n++;
    }
    return Math.max(1, n);
  }

  if (clear) {
    clear.addEventListener("click", function () {
      input.value = ""; apply(); input.focus();
    });
  }
  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      input.value = ""; apply(); input.focus();
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" ||
              t.isContentEditable)) return;
    e.preventDefault();
    if (input) { input.focus(); input.select(); }
  });

  window.addEventListener("scroll", hideTip, { passive: true });

  (function boot() {
    var q = new URLSearchParams(window.location.search).get("q");
    if (q && input) input.value = q;
    // Open on a class you can actually download rather than whatever sorts
    // first.
    current = tiles.filter(function (t) { return t._ready; })[0] || tiles[0];
    apply();
  })();
})();
