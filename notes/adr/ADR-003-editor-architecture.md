---
title: ADR-003 — In-browser editor architecture (codec, data model, class bundles, validation)
date: 2026-08-08
type: adr
status: accepted
tags: [weakauras, conquest-of-azeroth, editor, javascript, codec, adr]
sources:
  - "[[plans/pass-2-orchestration]]"
  - "[[wa-import-string-format]]"
  - "[[weakauras-data-model]]"
  - "[[../../second-brain/projects/coa-weakauras/notes/js-wa-codec-landscape]]"
---

# ADR-003 — Editor architecture: decode, edit, re-encode in the browser

## Context

Pass 2's goal (notes/plans/pass-2-orchestration.md) is an in-browser editor
where a player starts from a shipped class template and customizes it — with
access to their class & spec's skills, talents and abilities — then exports a
valid `!WA:2!` import string for the Ascension 3.3.5 fork. Hard constraint,
owner-confirmed: **pure static, all client-side, GitHub Pages stays the whole
deploy** (pass-2-orchestration.md, Decisions table). No backend, no build
server, no WASM toolchain requirement beyond what a static page can vendor.

The repo already has a complete, verified Python codec
(`tools/wacodec.py`, 431 lines, both directions), a field-level data model
reference read off the fork's source (`notes/weakauras-data-model.md`), a
builder whose invariants are enforced by 22 checks (`tests/run.py`), and
per-class data in `resources/` that the builders consume. The editor is a
fourth consumer of all of that — it must not invent a second truth.

## Decision

### D1. Port `wacodec.py` to JS by hand; take only the DEFLATE layer off the shelf

The `!WA:2!` pipeline has exactly three layers plus an envelope
(notes/wa-import-string-format.md, verified end-to-end 2026-07-27 against four
live client exports; reference implementation `tools/wacodec.py`):

| Layer | What it is | JS plan |
|---|---|---|
| 1. Print codec | LibDeflate `EncodeForPrint`: 6-bit custom alphabet `a-z A-Z 0-9 ( )` in **that index order**, **little-endian** bit packing (3 bytes → 4 chars from the least-significant end; tail flushed 6 bits at a time, low bits first) — NOT base64 (wacodec.py:11-54; wa-import-string-format.md §Layer 1) | Hand-port. ~40 lines. No library exists for this alphabet; getting bit order wrong fails deflate with `invalid distance too far back` (wa-import-string-format.md) |
| 2. Compression | **raw DEFLATE**, no zlib header — `zlib wbits=-15` is byte-compatible with LibDeflate `CompressDeflate`/`DecompressDeflate` (wacodec.py:57-63) | **pako** (`inflateRaw`/`deflateRaw`). Verified: pako implements raw mode by forcing `windowBits` negative, `-15` default (unpkg pako@2.1.0/lib/inflate.js, retrieved 2026-08-08), and pako v3 documents **"Binary-equivalent output — same deflate bytes as original zlib 1.3.2"** (nodeca.github.io/pako, retrieved 2026-08-08). Vendored as a single file in `docs/assets/` — no npm build step, full bundle <15 KB gzipped per its README |
| 3. Serialization | **LibSerialize v1** binary object stream: version byte `0x01`, then type-byte dispatch (7-bit small ints, embedded 12-bit ints written low-then-high, 5-bit type table for numbers/strings/tables/arrays/mixed, IEEE754 big-endian floats, short-decimal "FLOATSTR" floats), plus **per-type reference lists** — strings >2 bytes and ALL tables appended in encounter order, repeats emitted as 1-based refs, tables registered *before* their contents (wacodec.py:66-411; wa-import-string-format.md §Layer 2). This is NOT AceSerializer — the `^1^S...` text format belongs to pre-2.18 strings | Hand-port, mirroring wacodec.py function-for-function. **No pure-JS LibSerialize exists**: npm searches for `weakauras` and `libserialize` and a GitHub repo search (`libserialize javascript`) found none (registry.npmjs.org + api.github.com via Firecrawl, 2026-08-08). What does exist is either the wrong layer or the wrong runtime — see Alternatives |
| 4. WA envelope | Top-level table `{d, c, s, v, m}`; `c` is the FLAT list of all descendants; emit `s="5.21.2 Beta"`, `v=2000`, `internalVersion=89.5` on every aura (wa-import-string-format.md §Layer 3; weakauras-data-model.md §5.1, §9.5) | Comes free with layer 3; the editor edits the decoded tree and re-wraps |

**The in-memory shape is LuaTable-faithful, not plain JSON.** `wacodec.py`
models Lua tables as insertion-ordered dicts with 1-based integer keys for the
array part (`LuaTable`, wacodec.py:90-99); the JS port uses a `Map`-backed
equivalent preserving insertion order and integer-vs-string key identity.
Evidence this matters: wago.io — which does NOT decode in JS at all, it shells
out to a real Lua interpreter (`backend/api/helpers/encode-decode/WeakAura.js`,
methodgg/wago.io master, retrieved 2026-08-08) — still needs a hand-maintained
`fixNumericIndexes`/`fixWATables` repair pass on its encode path because JSON
loses numeric table keys to strings. We skip that entire failure class by
never leaving Lua-table semantics.

**uid handling.** uids are opaque 11-char strings; charset is not validated
(weakauras-data-model.md §5.6). The shipped builder salts them
deterministically so a rebuilt pack dedupes or force-fresh-imports as intended
(`wabuild.py:14-33`). The editor: preserves uids while editing; on export it
**re-salts every uid** (sha-256 of `editor|<user-salt>|<original-uid>`, same
recipe as `wabuild.uid`) so a customized pack takes WA's clean-import path
instead of the update dialog — because the editor's signature edits are
geometry, and the update dialog's "Size & Position" category defaults OFF for
the root aura, which silently discards exactly those edits
(weakauras-data-model.md §5.3). A fresh import has no such hole.

**Round-trip fidelity requirement — stated precisely:**

- **Serialized-payload layer: byte-identical.** A decode→re-encode with zero
  edits must reproduce the inflated byte stream exactly, including reference
  list order. This is provably achievable — measured 2026-08-08 with
  wacodec.py against three CLIENT-exported strings
  (`resources/import-strings/templar-pack.txt`, `chronomancer-nnoop.txt`,
  `runemaster-daweed.txt`): `serialize(deserialize(payload)) == payload`
  byte-for-byte on all three (76321, 13562, 3981 bytes). The JS port is held
  to the same bar, and it is the right bar: it proves the port reproduces
  every serialization decision (int widths, float reprs, ref ordering), which
  is what protects an edited pack from corrupting the fields it did NOT touch.
- **Compressed/string layer: equivalence, not byte-identity, for
  client-exported input.** zlib and LibDeflate emit different valid DEFLATE
  streams for the same payload (measured: re-encoding those three client
  strings changes length by ±0.2%; `deflate(payload) != original bytes`).
  Byte-identity here is impossible across compressor implementations and
  worthless: WeakAuras only ever sees the inflated payload. For input that
  THIS toolchain produced (the 84 shipped packs, all deflated by zlib level
  9), full-string byte-identity IS expected if pako's zlib-equivalence claim
  holds — measured in Python: `wa_encode(wa_decode(runemaster-coa.txt))` is
  byte-identical, 24226 chars. The prototype asserts it for JS and records
  the result (UNKNOWN-1).

### D2. The template data model: a knob manifest over a frozen tree

The editor does not offer the decoded tree raw. It splits every display into
**player surface** (knobs) and **load-bearing structure** (frozen), and ships
the split as data, not as editor heuristics.

**Player-safe surface** (all evidenced as safe in the fork's source via
notes/weakauras-data-model.md):

| Knob | Fields | Why safe |
|---|---|---|
| Position of a band/root | `xOffset`/`yOffset` on groups & dynamicgroups, root `scale` | groups are positioned normally; §1.3 trap applies only to *children* of dynamicgroups |
| Icon size | `width`/`height` on leaves (and band `space`, `gridWidth`, `rowSpace`) | dynamicgroups lay out from the child's DATA table (§1.2), so editing data is exactly right; `gridWidth` rebalances via the builder's row rule (wapack.py:1194-1204) |
| Colors | `barColor`, `backgroundColor`, subregion `border_color`, `text_color`, `glowColor`, condition-change color values | plain `{r,g,b,a}` values, no wiring |
| Urgency thresholds | the `value` strings in the 20/10/5s condition tiers (wapack.py:115, 744-753) | values only — the check SHAPE (the `onCooldown` AND-guard) is frozen; values must stay clean numeric strings (§6.6) |
| Which abilities show | remove a leaf: delete display + its entry in the parent's `controlledChildren`; restore from template | §5.5 requires payload consistency, which a paired remove preserves; dynamicgroups re-center around survivors (wapack.py:1289-1301) |
| Font sizes | `text_fontSize` on subtext subregions | condition-settable property, independently safe (§8A.4) |

**Load-bearing structure — frozen in v1, with the reason each is frozen:**

- `controlledChildren` ORDER: it is press-priority and `sort="none"` layout
  order; the builder topologically sorts to preserve it and the test
  comparator refuses to normalise it away (wapack.py:1235-1250).
- `id` strings: they are the anchor ladder's address space —
  `anchorFrameFrame = "WeakAuras:<display id>"` (wapack.py:1648-1675) — and
  the parent/child link keys (§3.3). Rename one and the ladder or the tree
  silently breaks. (WA renames on import collision itself, §5.4, so global
  uniqueness against the user's installed auras is not our problem.)
- `triggers` wiring: `disjunctive` any/all is semantic (NEEDS_ALL displays
  light wrongly under "any" — wapack.py:1493-1506), trigger indices are
  referenced by conditions (`check.trigger`) and text placeholders (`%2.s`).
- `load` gates: class token + `spellknown` per leaf is what makes 21 packs
  coexist (wapack.py:1433-1544; tests/run.py check 7).
- `subRegions` array membership/order: `sub.N.*` condition properties index
  it positionally, and the client inserts `subbackground` at index 1 if
  absent, renumbering everything (§9.3).
- uids individually (regenerated as a set on export, never hand-edited).
- `xOffset`/`yOffset` on dynamicgroup children: must stay 0 (§1.3).
- `internalVersion` (89.5 exactly — higher skips PreAdd entirely, §9.5),
  `tocversion`, `v=2000`, region `regionType`.

**Schema.** The builder emits, next to each pack, a knob manifest the editor
loads with the pack string:

```json
{ "pack": "runemaster-coa", "version": "1.9",
  "displays": {
    "RM Riftblade Offense Zenith": {
      "kind": "cd-icon", "band": "RM Riftblade Offense",
      "ability": "Zenith", "spec": "riftblade",
      "knobs": { "size": ["width","height"], "urgency": [20,10,5],
                 "removable": true } },
    "RM Glyphic Mana": { "kind": "bar",
      "knobs": { "color": "barColor", "size": ["width","height"] } }
  },
  "bands": { "RM Riftblade Offense": { "knobs": ["space","gridWidth","y"] } } }
```

Generated where the knowledge lives — `wapack.py` knows which leaf is a
cd-icon with urgency tiers versus a fused feeder cell that must not be
touched — so the editor never re-derives structure from the tree by guesswork.

### D3. Class data ships as one static JSON bundle per class, built by a new tool step

**What the editor needs per class** (all already in `resources/`, consumed
today by `wapack.init()` — wapack.py:200-333): the reviewed ability inventory
(name, id, per-spec ids, specs, role — `abilities-<slug>.md`), skills with
icon texture names (`coa-<slug>-skills.json`), cooldown/GCD audit
(`cooldown-abilities-<slug>.json`, source of the OFF_GCD set), talents
(`talents-<slug>.json`), id→icon map (`icon-meta-<slug>.json`), the in-game
verified id registry (`tools/in-game-verified.json`, 2.6 KB), and class
identity (token, spec labels) from `tools/classes.py`.

**Measured** (2026-08-08, Runemaster, the largest class by inventory):

| Piece | raw | gzip |
|---|---|---|
| abilities inventory (parsed rows) | 21.8 KB | 3.7 KB |
| skills (name+icon) | 12.3 KB | 3.0 KB |
| cooldown audit | 5.6 KB | 1.2 KB |
| talents | 27.4 KB | 3.5 KB |
| icon-meta (pyromancer, largest measured) | 36 KB | — |
| **bundle total** | **~100 KB** | **~15-20 KB** |

`spell-meta-<slug>.json` (192 KB raw / 27 KB gzip for Runemaster) is
**excluded**: its consumer is the builder's `gateable()` decision
(wapack.py:365-387), and those decisions are already baked into the shipped
template's gates and trigger exactness. The editor never re-derives them.

**Budget: ≤128 KB raw per class bundle, loaded on demand** (one class per
editor session — nobody edits 21 classes at once). 21 bundles ≈ 2 MB in the
repo, which is smaller than the icon art already shipped
(`docs/assets/spell-icons/`: 374 files, 2.4 MB) — icon art is REUSED, not
re-shipped: bundle entries carry texture names that resolve to
`docs/assets/spell-icons/<name>.jpg`, the same mapping the HUD preview uses
(tools/hud.py:22).

**Generated by a new `tools/mkeditordata.py`**, invoked from `mksite.py`'s
build alongside the pack copy (mksite.py already mirrors
`tools/packs/<slug>/` → `docs/packs/<slug>/`; bundles land in
`docs/editor/data/<slug>.json`). It reuses `classes.py` + the same parsers
`wapack` uses, so a class converging (e.g. Runemaster still on legacy
`icons.json` — wapack.py:246-258) changes the bundle the day it changes the
pack. The knob manifest (D2) is emitted by the builder per pack for the same
reason.

### D4. Validation runs in the browser, on every export, as a hard gate

The repo's invariants exist because each caught a shipped bug (tests/run.py
header, lines 1-48). The editor cannot run Python, so the exportable subset
is ported to JS and `export()` refuses on ERROR. Tiered:

**Tier 1 — import-breaking (hard error, from the fork's import code):**
- unique `id` AND unique `uid` across the payload — duplicate id is a hard
  Lua error at import, duplicate uid silently drops an aura
  (weakauras-data-model.md §5.5);
- every `controlledChildren` entry exists in the payload; every child's
  `parent` exists; root carries no `parent`; leaves carry no
  `controlledChildren` (§5.5, §3.3);
- no group/dynamicgroup nested inside a dynamicgroup — severed at next login
  (§3.4);
- `internalVersion == 89.5` on every aura, never higher (higher skips
  PreAdd/validate entirely and regions error at render — §9.5).

**Tier 2 — silently-broken-aura (hard error, from shipped bugs):**
- every leaf keeps `load.use_class` + the class token; spec leaves keep
  `spellknown` (the JS twin of `assert_gated()`, wapack.py:1547-1592;
  tests/run.py check 7 at :194-243);
- no urgency tier with a bare `expirationTime` — every one stays ANDed with
  the `onCooldown` guard, or it fires on every global cooldown (shipped as
  final12; wapack.py:715-742; tests/run.py check 9 at :330);
- edited condition values remain clean numeric strings — a malformed value on
  a timer condition kills EVERY condition on that aura via loadstring failure
  (§6.6);
- Lua type preservation on every edited field: `Private.validate` silently
  replaces a wrong-typed field with the default (`"64"` where `64` belongs —
  §9.1), so the editor type-checks each knob write against the decoded
  original's type;
- `use_showgcd` untouched per ability (off-GCD abilities must not carry it —
  tests/run.py check 10 at :334-429); v1 enforces this by not exposing
  triggers at all;
- dynamicgroup children keep `xOffset = yOffset = 0` (§1.3).

**Tier 3 — layout-quality (warning, exportable anyway):**
- a resized cooldown row wider than 1.2× its spec's main row (the
  `rowwidths.py` rule, wapack.py:118-126);
- `grow`/`align`/`selfPoint` combinations the WA options UI would never
  write (§2.2 table) — only reachable if band knobs are extended later.

The Tier 1+2 validator is ~150 lines over the decoded tree and doubles as
the prototype's self-check. Parity with Python is held by fixtures: the same
validator decisions are asserted against the shipped packs in `tests/run.py`
(which already rebuilds all 84), so a divergence shows up as a JS test
failure against a pack Python calls green (see plan, step 4).

### D5. Prototype: decode a shipped pack, resize one icon, re-encode, import

The thinnest proof that de-risks D1 (agent E of the pass implements it —
pass-2-orchestration.md §The agents). One static page, no framework, vendored
pako + the ported codec, kept off the nav like the rest of the emberfall-gated
site. It:

1. fetches `docs/packs/runemaster/runemaster-coa.txt` same-origin (the copy
   button already fetches pack files this way — mksite.py:284);
2. decodes it in JS and renders `d.id` + child count;
3. re-encodes with zero edits and asserts fidelity;
4. applies ONE knob edit — icon `width`/`height` 26→34 on a single named
   Offense leaf (both fields, since dynamicgroup layout reads both — §1.2);
5. re-encodes and offers the string for copy.

**Acceptance test, precisely** (all five must pass):

- **A1 (decode parity):** JS decode of `runemaster-coa.txt` yields the same
  tree as `python3 tools/wacodec.py` on the same file: root id equal, `c`
  length equal (237 at current build), and a canonical JSON dump of both
  (arrays for array parts, sorted string keys for map parts) is
  byte-identical.
- **A2 (zero-edit payload fidelity):** decode→re-encode with no edits: the
  re-serialized payload (after EncodeForPrint-decode + inflate of the output
  string) is **byte-identical** to the original payload. Additionally record
  whether the full output STRING is byte-identical to the input (settles
  UNKNOWN-1 on pako/zlib equivalence); string-identity is a bonus, not a
  gate.
- **A3 (edit locality):** after the one edit, `wacodec.wa_decode` (Python) of
  the JS-produced string deep-equals the Python decode of the original
  except exactly the two edited fields on the one edited display.
- **A4 (validator):** the D4 Tier-1+2 validator passes on the edited tree,
  and a deliberately broken fixture (duplicated id) is refused.
- **A5 (in-game):** the edited string imports into the Ascension CoA client
  without error and the edited icon renders visibly larger; the rest of the
  pack is unchanged in play. Manual, screenshot-verified — same standard as
  `tools/in-game-verified.json`. Export with re-salted uids so the import is
  clean-path (D1), avoiding the §5.3 size-and-position discard.

## Alternatives considered

**WASM build of `weakauras-codec-rs` (Zireael-N).** The only existing
open-source codec that genuinely handles `!WA:2!` both directions
(README: decodes `!WA:2!`, encodes `BinarySerialization`; retrieved
2026-08-08; a `wasm-weakauras-parser` wrapper repo exists). Rejected:
(a) its `LuaValue::Map` is a `BTreeMap` — sorted keys, not insertion order —
so it cannot reproduce the client's serialized byte stream and fails the D1
fidelity bar by construction; (b) its own README warns "Table references from
LibSerialize are not fully supported" (node-weakauras-parser, same author,
retrieved 2026-08-08) while our packs and the reference tracker depend on
exact ref semantics; (c) a Rust/wasm-pack toolchain enters a repo that is
currently stdlib-Python + static files (tests/run.py:5 "no pytest, no venv,
no dependencies").

**`node-weakauras-parser` (npm).** Full v2 codec, but a native Node module
(prebuilt binaries per OS, Rust to build from source — npm README, retrieved
2026-08-08). Not a browser artifact; unusable on GitHub Pages. Rejected.

**npm `weakauras-codec` (rsuurd).** Pure JS + pako and browser-bundled — but
implements only the AceSerializer TEXT format (`^1`/`^S`/`^N`/`^T`; throws
"Not Ace-serialized content" and "Floats not supported yet" — read in its
dist bundle via unpkg, retrieved 2026-08-08), decode-only, last published
2020-02-12 (registry metadata). Wrong layer entirely for `!WA:2!`. Its one
contribution: independent confirmation of the EncodeForPrint alphabet, which
appears verbatim in its bundle. Rejected.

**Lua-in-the-browser (fengari or similar) running the real LibDeflate +
LibSerialize.** This is wago.io's architecture transplanted client-side —
maximum authenticity, and wago.io itself demonstrates the cost: the
Lua↔JSON bridge loses numeric keys and needs a hand-grown repair pass
(`fixNumericIndexes`, WeakAura.js, retrieved 2026-08-08), plus a Lua VM
payload dwarfing the 431-line codec being avoided. Rejected.

**Plain-JSON working model inside the editor.** Rejected for the same
wago-evidenced reason — the port keeps LuaTable semantics end to end (D1).

**Backend service that decodes/encodes.** Violates the pass's hard
constraint outright (pass-2-orchestration.md: "Pure static / client-side").
Rejected without further analysis.

## Consequences

- Two codec implementations (Python, JS) must agree forever. Mitigation is
  mechanical, not disciplinary: the JS port is fixture-tested against the
  same four client strings and 84 shipped packs the Python codec is, with
  payload byte-identity as the oracle (plan step 1); any Python-side change
  to `wacodec.py` shows up as a JS fixture failure in the same run.
- pako is the first vendored third-party asset in `docs/`. It is a single
  file, version-pinned, and only its raw-mode entry points are used.
- The knob manifest makes the builder the single authority on what is
  editable — a new class gets an editor surface the day its pack builds,
  and an editor feature request ("let me move the buff row") becomes a
  builder change with tests, not an editor hack.
- Re-salted uids mean a re-exported customization is always a NEW aura group
  in WA; players iterating on their layout accumulate old copies to delete
  by hand. Accepted for v1: it is the shipped packs' own release model
  (wabuild.py:19-22), and the §5.3 alternative (update path) silently drops
  root geometry edits, which is worse than clutter.
- v1 edits displays that exist in the template; it cannot ADD an ability the
  template omitted (that requires trigger synthesis — builder territory).
  The "which abilities are shown" surface is remove/restore. Extension is a
  future ADR once the builder's widget vocabulary is callable from data.

## Sources

- `notes/plans/pass-2-orchestration.md` — governing decisions and constraint.
- `notes/wa-import-string-format.md` — the three layers, verified 2026-07-27.
- `tools/wacodec.py` — reference codec (cited by line above).
- `tools/wabuild.py`, `tools/wapack.py` — uid salting, layout/gating/merge
  machinery (cited by line above).
- `notes/weakauras-data-model.md` — fork-source-verified field semantics
  (§ references above).
- `tests/run.py` — the 22 checks; header lines 1-48, checks cited by line.
- Round-trip measurements, 2026-08-08, this repo: payload byte-identity on
  `resources/import-strings/{templar-pack,chronomancer-nnoop,runemaster-daweed}.txt`;
  full-string identity on `docs/packs/runemaster/runemaster-coa.txt`;
  bundle sizes from `resources/*-runemaster.*`/`*-pyromancer.*`.
- Web (all via /web-research → Firecrawl, retrieved 2026-08-08, notes in
  `~/second-brain/projects/coa-weakauras/notes/js-wa-codec-landscape.md`):
  nodeca.github.io/pako (v3.0.1, binary-equivalence claim);
  unpkg.com/pako@2.1.0/lib/inflate.js (raw windowBits handling);
  methodgg/wago.io `backend/api/helpers/encode-decode/WeakAura.js` (Lua
  shell-out, JSON repair pass); registry.npmjs.org/weakauras-codec +
  unpkg dist bundle (Ace-only, dead); registry.npmjs.org/node-weakauras-parser
  (native, LibSerialize since v3.1, table-ref caveat);
  Zireael-N/weakauras-codec-rs README (Rust v2 codec, BTreeMap maps).

## UNKNOWNs

1. **pako deflateRaw level-9 byte-equivalence to Python zlib on our
   payloads.** pako v3 claims binary equivalence with zlib 1.3.2; our packs
   are deflated by whatever zlib CPython links. Settled by prototype
   acceptance A2's recorded string-identity result. Consequence either way
   is cosmetic (payload identity is the gate).
2. **JS float short-repr parity with Python `repr()` for NUM_FLOATSTR.**
   wacodec.py:277-284 emits a float as a decimal string when
   `len(repr(a)) < 7` and it round-trips; JS `String(x)` is
   shortest-round-trip too, but formatting corners (e.g. exponent notation
   thresholds) may differ. Settled by A2 payload byte-identity across all 84
   shipped packs + the internalVersion 89.5 float every aura carries.
3. **In-game behavior of an edited pack imported over an installed original**
   (uid-matched update path): predicted-discard of root geometry per §5.3 is
   source-read, not client-observed on 89.5. Made irrelevant for v1 by
   re-salting, but settle it (one manual import) before ever offering an
   "update in place" export mode.
4. **Add-an-ability editing** — what a data-driven trigger vocabulary would
   need to expose. Out of scope here; settled by a future ADR after the
   prototype and UX pass (ADR-004) land.
