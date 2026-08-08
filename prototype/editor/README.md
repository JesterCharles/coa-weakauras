# Editor prototype — decode / edit / re-encode in the browser

ADR-003 D5's thin proof, implemented per notes/plans/editor-architecture-plan.md
step 1. A static page decodes a real shipped `!WA:2!` pack string, edits one
icon's width+height, and re-encodes a valid import string — no backend, no
framework, no build step.

## Files

| File | What |
|---|---|
| `wacodec.js` | JS port of `tools/wacodec.py` (746 lines): EncodeForPrint 6-bit codec, raw DEFLATE via pako, LibSerialize v1 both directions with per-type reference lists and the LuaTable-faithful container (insertion-ordered Map, 1-based integer array keys — never plain JSON objects). Plus the D4 validator stub, uid re-salt (`editor\|<salt>\|<uid>` sha-256, wabuild recipe), and the canonical-JSON parity oracle. UMD: browser global `wacodec` or node `require` |
| `vendor/pako.min.js` | pako 2.1.0 dist, vendored (sha256 `ede2693a…8514907`). Only `inflateRaw`/`deflateRaw` are used |
| `index.html` | The prototype page: paste-or-load a pack string, decode, display tree, one editable control (icon width+height), validate + re-encode with uid re-salt, copy |
| `test.js` | Node-runnable acceptance gates A1–A4 + a 95-string corpus sweep |
| `proto-pydump.py` / `proto-pydiff.py` | Python cross-check helpers driven by `test.js`; both go through the repo's own `tools/wacodec.py` |

## Repro

```
node prototype/editor/test.js          # gates A1-A4 + corpus (needs python3)
python3 -m http.server                 # from repo root, then open
#   http://localhost:8000/prototype/editor/index.html
```

## Gate results (2026-08-08, runemaster-coa.txt v1.8, 237 children)

- **A1 decode parity — PASS.** JS and Python decodes agree: root id
  `Runemaster [CoA] v1.8`, 237 children, canonical JSON dumps (807,276 chars)
  byte-identical.
- **A2 zero-edit payload fidelity — PASS.** Re-serialized payload is
  byte-identical to the original inflated payload (174,279 bytes).
  **UNKNOWN-1 settled: the FULL output string is also byte-identical**
  (24,226 chars) — pako 2.1.0 `deflateRaw` level 9 matches CPython zlib
  byte-for-byte on our payloads. Corpus: payload byte-identical on all
  95 strings (91 shipped packs + 4 community client exports); full-string
  identical on 91/95 — the 4 misses are exactly the 4 CLIENT-exported
  community strings, whose LibDeflate streams no compressor reproduces
  (expected per ADR-003; equivalence, not identity, is the bar there).
- **A3 edit locality — PASS.** Icon `RM Riftblade Offense Zenith` width+height
  26→34, re-encoded in JS, cross-decoded with the PYTHON codec: exactly two
  fields differ (`width 26→34`, `height 26→34`), nothing else.
- **A4 validator — PASS.** Stub (unique ids + class load gate on every leaf)
  passes the shipped pack and the edited tree; refuses a duplicated-id
  fixture (`duplicate id: "RM Alert No Engraving"`) and a leaf with
  `load.use_class` deleted (`leaf missing class load gate`).
- **Browser flow — verified headless** (Chromium): load → decode (11.7 ms) →
  edit → validate + re-encode (14.6 ms), zero console errors; the page's
  output string Python-decodes to exactly the 2 edited fields + 238 re-salted
  uids and nothing else.

## A5 (in-game) — the one human step

Open the page, load the shipped Runemaster pack, resize one Offense icon,
copy the export (leave "re-salt uids" checked), import it in the Ascension
CoA client, and screenshot the visibly larger icon — file it the way
`tools/in-game-verified.json` entries are.

## Notes / deviations from ADR-003

- **pako provenance:** vendored from the locally npm-installed pako 2.1.0
  dist (`pako.min.js` from the npm tarball) rather than fetched over the
  network — same artifact, version-pinned, sha256 recorded above.
- **Line-count delta vs Python (746 vs 431):** the extra is what CPython gets
  from stdlib — a compact SHA-256 (sync uid re-salt in both runtimes), a
  UTF-8 surrogateescape codec (exact twin of Python's `errors="surrogateescape"`),
  the canonical-JSON oracle, the D4 validator stub, and the UMD wrapper.
  The codec proper mirrors wacodec.py function-for-function.
- **Float formatting:** `pyFloatRepr()` reproduces Python `repr()` exactly
  (fixed notation for exponents in [-4, 16), else `e±XX`), because JS
  `String()` thresholds differ (`0.00001` vs Python's `1e-05`) and the
  NUM_FLOATSTR path is length-sensitive. UNKNOWN-2 settled by the corpus
  sweep: payload byte-identity on all 95 strings.
- `test.js` A3 encodes WITHOUT uid re-salt so locality is measurable; the
  page re-salts on export (default on) per ADR-003 D1. Repeated re-encodes
  salt from the uids captured at decode, so the mapping is stable per salt.
