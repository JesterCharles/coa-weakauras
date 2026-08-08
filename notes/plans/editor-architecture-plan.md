---
title: Editor architecture — ordered build plan (from ADR-003)
date: 2026-08-08
type: plan
status: active
tags: [weakauras, conquest-of-azeroth, editor, javascript, codec, plan]
sources:
  - "[[../adr/ADR-003-editor-architecture]]"
  - "[[pass-2-orchestration]]"
---

# Editor architecture — build plan

Ordered. Each step ships alone and has an acceptance signal that can fail.
Step 1 is the pass's prototype dependency (agent E waits on nothing else);
steps 2-5 are post-pass work in priority order. File paths are the decision,
not a sketch — deviations go back through the ADR.

## 1. Codec port (`docs/assets/wacodec.js`) + prototype page

The JS twin of `tools/wacodec.py`: EncodeForPrint alphabet codec,
pako `inflateRaw`/`deflateRaw` (vendored, version-pinned, single file
`docs/assets/pako.min.js`), LibSerialize v1 reader/writer with the reference
lists and the LuaTable-faithful container (insertion-ordered Map, 1-based
array part). Same function names as the Python module so the two stay
diffable by eye. No framework, no build step — a `<script>` tag works on
GitHub Pages as-is.

Prototype page `docs/editor/proto.html` (off the nav, emberfall-gated like
everything else): fetch `../packs/runemaster/runemaster-coa.txt`, decode,
show root id + display count, resize ONE named Offense icon 26→34
(width AND height), re-encode with re-salted uids, copy button.

**Acceptance — ADR-003 D5, all five:**
- A1 decode parity with `python3 tools/wacodec.py` (root id, 237 children,
  canonical-JSON byte equality);
- A2 zero-edit re-encode: serialized payload byte-identical after
  print-decode + inflate; record (don't gate on) full-string identity —
  this settles UNKNOWN-1;
- A3 Python cross-check: JS output string decodes to a tree deep-equal to
  the original except the two edited fields;
- A4 validator refuses a duplicated-id fixture (stub validator OK here —
  full set is step 4);
- A5 in-game: string imports on the CoA client, icon visibly larger,
  screenshot filed the way `tools/in-game-verified.json` entries are.

Also in this step: a node-runnable fixture test
(`tests/editorarch-codec-parity` or folded into `tests/run.py` as a
subprocess check if node is present) asserting A2-style payload identity on
all four community strings in `resources/import-strings/` and all 84 shipped
packs. UNKNOWN-2 (float repr parity) falls out of this corpus run.

## 2. Class data bundles (`tools/mkeditordata.py` → `docs/editor/data/<slug>.json`)

New tool, wired into `mksite.py`'s build the same way the pack copy is.
Reads through `classes.py` + the same parsers `wapack.init()` uses:
abilities inventory, skills (name+icon), cooldown/GCD audit, talents,
icon-meta, in-game-verified ids, class token + spec labels. Excludes
spell-meta (baked into templates already — ADR-003 D3). Icon texture names
resolve against the already-shipped `docs/assets/spell-icons/`.

**Acceptance:**
- bundle exists for every class with a shipped pack, ≤128 KB raw each
  (measured guardrail asserted in the tool: it FAILS the build over budget,
  it does not truncate);
- a spot-check class (Runemaster) round-trips: every ability name in its
  bundle resolves to the same id `wapack.sid()` resolves, verified by a
  small test that imports both;
- site build regenerates bundles when the underlying resources change
  (touch a resource, rebuild, bundle mtime moves).

## 3. Knob manifest emitted by the builder (`wapack.finish()` → alongside each pack)

`wapack` emits `<pack>.knobs.json` next to each built pack, classifying
every display it just built: kind (cd-icon / buff-icon / bar / band / root /
frozen), owning band, ability name, spec set, and the knob list per ADR-003
D2 (size, colors, urgency values, removable, band geometry). Fused/feeder
cells, seg-bar cells and spell-swap leaves are marked `frozen` — the builder
knows which is which at emit time; nothing downstream re-derives it.
`mksite.py` copies manifests with the packs.

**Acceptance:**
- every display id in every shipped pack appears in its manifest exactly
  once (asserted in `tests/run.py` — same loop that already walks all 84
  packs);
- fixtures unchanged: emitting the manifest must not touch the pack bytes
  (check 1 stays green with no fixture re-freeze);
- frozen coverage: every display whose id matches the feeder/seg/swap
  naming (`* Feed *`, `* Fill *`, `* Empty *`, spell_swap targets) is
  `frozen` in the manifest.

## 4. Browser validator (`docs/assets/wavalidate.js`)

The Tier 1 + Tier 2 set from ADR-003 D4: payload uniqueness and
parent/child consistency, no group-in-dynamicgroup, internalVersion 89.5
exactly, class/spec gates present on every leaf, urgency tiers keep the
`onCooldown` guard, numeric condition values stay clean numeric strings,
knob writes preserve Lua types, dynamicgroup children keep zero offsets.
Tier 3 as warnings (1.2× row-width rule). Export is refused on any Tier 1/2
failure with the failing display ids listed — same reporting voice as
`assert_gated()`.

**Acceptance:**
- all 84 shipped packs pass clean (parity with Python: any pack
  `tests/run.py` calls green must validate green in JS — asserted by the
  node fixture run from step 1);
- a mutation kit fails correctly: duplicated id, dropped
  `controlledChildren` entry, bare-expirationTime tier, string-where-number
  knob write, internalVersion 90 — five fixtures, five refusals, mirroring
  the "comparator honesty" pattern of tests/run.py checks 2-6;
- validator + codec together stay under 64 KB raw JS (no framework creep).

## 5. Editable surface wired to the knobs (the actual editor page)

`docs/editor/index.html`: pick class → load pack string + knob manifest +
class bundle; render the display list grouped by band with the HUD preview
geometry the site already computes; expose exactly the manifest's knobs;
remove/restore abilities; live validator; export = re-salt uids → encode →
copy. Interaction model is ADR-004's territory — this step consumes its
decisions, it does not make them.

**Acceptance:**
- edit → export → re-import loop passes A3-style locality for every knob
  kind (size, color, threshold, remove, band move) on one pack;
- a removed ability's display AND its `controlledChildren` entry are both
  gone, and the validator passes;
- an exported no-edit pack is payload-byte-identical to the shipped one
  except uids (the re-salt is the only diff);
- one full customization round verified in game (the packs-ship-imperfect
  feedback loop applies to the editor too).

## Sequencing note

Step 1 unblocks agent E immediately and is the pass's only in-scope build.
Steps 2-4 are independent of each other once 1 lands (bundles, manifest,
validator touch disjoint files); 5 needs all of them plus ADR-004. The
emberfall gate stays until the pass completes (pass-2-orchestration.md).
