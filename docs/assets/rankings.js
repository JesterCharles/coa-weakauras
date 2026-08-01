// Encounter-bracket switching for the Top logs panel on a class page.
//
// Every bracket is rendered server-side and only visibility changes here, so
// the panel works with JS off -- you get Overall, which is the right default
// anyway. Same approach as hud.js, for the same reason.
(function () {
  "use strict";

  var root = document.getElementById("ranks");
  if (!root) return;

  var layers = Array.prototype.slice.call(root.querySelectorAll(".ranklayer"));
  var buttons = Array.prototype.slice.call(root.querySelectorAll(".rankcat"));
  if (!layers.length || !buttons.length) return;

  function show(cat) {
    layers.forEach(function (l) {
      l.classList.toggle("on", l.dataset.cat === cat);
    });
    buttons.forEach(function (b) {
      var on = b.dataset.cat === cat;
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  buttons.forEach(function (b) {
    b.addEventListener("click", function () { show(b.dataset.cat); });
  });
})();
