// Spec and mode switching for the HUD preview on a class page.
//
// All layers are rendered server-side (one per spec per mode) and only their
// visibility changes here, so the preview works without JS -- you get the
// first spec's in-play view, which is the right default anyway.
(function () {
  "use strict";

  var hud = document.getElementById("hud");
  if (!hud) return;

  var layers = Array.prototype.slice.call(hud.querySelectorAll(".hudlayer"));
  var specBtns = Array.prototype.slice.call(hud.querySelectorAll(".hudspec"));
  var modeBtns = Array.prototype.slice.call(hud.querySelectorAll(".hudmode"));
  if (!layers.length) return;

  var spec = layers[0].dataset.spec;
  var mode = "play";

  function render() {
    layers.forEach(function (l) {
      l.classList.toggle("on", l.dataset.spec === spec && l.dataset.mode === mode);
    });
    specBtns.forEach(function (b) {
      var on = b.dataset.spec === spec;
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", String(on));
    });
    modeBtns.forEach(function (b) {
      var on = b.dataset.mode === mode;
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", String(on));
    });
  }

  specBtns.forEach(function (b) {
    b.addEventListener("click", function () { spec = b.dataset.spec; render(); });
  });
  modeBtns.forEach(function (b) {
    b.addEventListener("click", function () { mode = b.dataset.mode; render(); });
  });

  render();
})();
