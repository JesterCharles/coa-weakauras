// Copy-to-clipboard for import strings.
//
// The strings are 10-21 KB, which is fine for the clipboard but far too much
// to inline into the page for every pack -- so each button fetches its .txt on
// demand. Same origin under Pages, so no CORS involved.
//
// navigator.clipboard needs a secure context (https, or localhost). GitHub
// Pages is https; a file:// preview is not, hence the textarea fallback.
(function () {
  "use strict";

  var cache = {};

  function legacyCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-1000px";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  function write(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return legacyCopy(text) ? Promise.resolve()
                            : Promise.reject(new Error("copy blocked"));
  }

  function flash(btn, cls, label) {
    var original = btn.dataset.label || btn.textContent.trim();
    btn.dataset.label = original;
    btn.classList.remove("done", "err");
    btn.classList.add(cls);
    btn.textContent = label;
    clearTimeout(btn._t);
    btn._t = setTimeout(function () {
      btn.classList.remove("done", "err");
      btn.textContent = original;
    }, 2200);
  }

  function load(src) {
    if (cache[src]) return Promise.resolve(cache[src]);
    return fetch(src).then(function (r) {
      if (!r.ok) throw new Error(r.status + " " + r.statusText);
      return r.text();
    }).then(function (t) {
      cache[src] = t.trim();
      return cache[src];
    });
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest("button.copy");
    if (!btn) return;
    var src = btn.dataset.src;
    if (!src) return;

    btn.disabled = true;
    load(src)
      .then(write)
      .then(function () { flash(btn, "done", "Copied ✓"); })
      .catch(function (err) {
        flash(btn, "err", "Copy failed — use Download");
        if (window.console) console.error("copy failed:", err);
      })
      .then(function () { btn.disabled = false; });
  });
})();
