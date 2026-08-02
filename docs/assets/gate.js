/* Cosmetic construction gate for the WeakAuras pack pages.
 *
 * ⚠ THIS IS NOT SECURITY, AND MUST NEVER BE DESCRIBED AS SECURITY.
 *
 * The repository is PUBLIC. Every pack this hides is also at
 * github.com/JesterCharles/coa-weakauras/tree/main/docs/packs and is fetchable
 * directly by URL, so the passcode is bypassed by viewing source, by opening
 * the .txt, or by reading this file. It exists for exactly one reason: the
 * packs are mid-rebuild and a passing visitor should not import a half-built
 * one by accident.
 *
 * If real access control is ever needed, this file is not the answer -- the
 * repo has to become private and the site has to move somewhere that can
 * actually authenticate. Do not "harden" this by hashing the code or
 * minifying it; that only makes a bypassable gate look unbypassable, which is
 * worse than an obviously cosmetic one.
 *
 * Remove it by dropping data-gate from <body> in tools/mksite.py.
 */
(function () {
  var body = document.body;
  var code = body.getAttribute("data-gate");
  if (!code) return;
  var KEY = "coa-wa-gate";
  try {
    if (window.localStorage.getItem(KEY) === code) return;
  } catch (e) { /* private mode: just show the prompt every time */ }

  body.classList.add("gated");
  var wrap = document.createElement("div");
  wrap.className = "gate";
  wrap.innerHTML =
    '<div class="gatebox">' +
    '<h1>Under construction</h1>' +
    '<p>These packs are being rebuilt and are not ready to import. ' +
    'If you have the passcode, enter it to look anyway.</p>' +
    '<form><input type="password" autocomplete="off" spellcheck="false" ' +
    'aria-label="passcode" placeholder="passcode"><button>Enter</button></form>' +
    '<p class="gatenote">Not a security measure &mdash; this site and its ' +
    'packs are public on GitHub. It is a speed bump while the rebuild ' +
    'lands.</p>' +
    '<p class="gatenote"><a href="../index.html">Back to classes</a> &middot; ' +
    '<a href="../raid-utility.html">Raid utility</a></p>' +
    '</div>';
  var form = wrap.querySelector("form");
  var input = wrap.querySelector("input");
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    if (input.value.trim() !== code) {
      wrap.querySelector(".gatebox").classList.add("bad");
      input.select();
      return;
    }
    try { window.localStorage.setItem(KEY, code); } catch (e) { /* ignore */ }
    body.classList.remove("gated");
    wrap.remove();
  });
  document.addEventListener("DOMContentLoaded", function () {
    body.appendChild(wrap);
    input.focus();
  });
  if (document.readyState !== "loading") {
    body.appendChild(wrap);
    input.focus();
  }
})();
