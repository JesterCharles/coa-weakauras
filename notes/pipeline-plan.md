---
title: Plan — config-driven class pipeline, proven by Chronomancer
date: 2026-07-28
type: plan
status: budding
tags: [weakauras, conquest-of-azeroth, pipeline, plan]
sources:
  - "[[class-pack-process]]"
  - "[[runemaster-retro]]"
  - "[[layout-standard]]"
  - "[[weakauras-data-model]]"
---

# Plan: build the pipeline, then build Chronomancer through it

## Goal

One shared engine plus a per-class config, so a class pack is a data job any
agent can run independently. Chronomancer (class 22) is not a side quest — it is
the acceptance test. If Chronomancer ships through the new path with fewer than
a handful of in-game iterations, the pipeline is real and the remaining 19
classes fan out.

**Scope ends when Chronomancer ships.** Fan-out is a separate plan.

## Decisions taken (2026-07-28)

Pre-review:

1. **Healer scope: current target only, no raid frames.** Group health *and*
   raid-wide HoT state stay with VuhDo/Grid, which own that job on 3.3.5a. The
   pack gains one **target band** carrying `unit="target", own_only=True` —
   `helpful=False` yields your DoTs on an enemy, `helpful=True` yields your HoTs
   on an ally, and retargeting swaps the contents with no extra machinery. There
   is no multi-target tracking in a class pack, for healers or anyone else.
   Applies to every class, not just healers. *(Revised 2026-07-28: the earlier
   "multi-target HoT band" is dropped — `wabuild.py:70` already parameterises
   `unit`/`helpful`/`own_only`, so this is a data change, not a new mechanism.)*
2. **Builder shape: config + shared engine + specified-but-unimplemented hook.**
   Band assembly moves into a shared `wapack.py`. Per class: a declarative
   config.
3. **Version control: yes.** `git init` at
   `~/second-brain/projects/coa-weakauras`. Non-negotiable once agents run in
   parallel against one engine.

From `/plan-eng-review` + Codex:

4. **Refactor gate is structural equality, not byte-equality.** `wacodec.py`
   already decodes — decode both sides and compare the normalised region tree,
   parentage, triggers, anchors and conditions, ignoring uid values and key
   order. Byte-equality would fight every legitimate refactor (dict-key order,
   `add(region)` sequence) and pressure the engine into preserving accidental
   ordering. Byte-compare survives as a one-time harness smoke test only.
   **Child order is NOT normalised.** `controlledChildren` order is semantic —
   it encodes "most-pressed first" and "trinkets pinned last". Sorting it would
   false-pass exactly the row-order and priority bugs the layout standard cares
   about. Normalise uids and key order only. *(Revised — the first draft said
   "canonicalise child order", which was wrong.)*
5. **Config is a Python data module first; JSON deferred to Phase 5.**
   `classes/<class>.py` exporting a plain dict. No schema layer, no parser, no
   validation framework — and it can hold a callable where one class genuinely
   needs it. JSON was decided earlier on the grounds that agents generate it more
   reliably, but that only pays off at fan-out, which is out of scope; the risk
   lands now and the benefit lands later. Freeze a JSON schema in Phase 5, once
   Chronomancer has shown what the fields actually are rather than what we
   imagine them to be. *(Revised 2026-07-28 on Codex's strategic finding: the
   resource schema was being designed from Pyromancer mechanics not yet
   gathered.)*
6. **`WA_VERIFY` no-gate pack** — the human screenshot pass is the real
   bottleneck, not generation. See Phase 1b.
7. **Commit every scraped snapshot per class.** db.exil.es / db.ascension.gg /
   ascensionsidekick.com are third-party and can change or vanish; they are the
   *least* reproducible asset here, not the most. `exiles-runemaster.json` is
   48KB. Cheap to commit, expensive to lose.
8. **Hook contract specified, zero hooks implemented.** Segmented resources are
   a *first-class engine band kind*, so the hook layer's only cited consumer
   (Glyphic's glyph bar) was never a hook consumer. Nothing today justifies
   building it.
9. **Code is truth over `layout-standard.md`.** The doc declares 8 bands; the
   shipped code has 9 and two anchors disagree. Correct the doc to `final8`.
10. **Split the extraction from the behaviour change.** Extract with the 9
    constants intact; derive spacing from icon heights later, as its own phase.
11. **One ordered id resolver** replacing `FALLBACK` / `OVERRIDE` / `IN_GAME` /
    `CROSSCHECK` / `ID_OVERRIDE` / `VARIANTS`.
12. **Validation exits nonzero** on any unresolved name, with an explicit
    override flag. An unattended agent must not ship a broken pack and report
    success.
13. **Tests: stdlib only.** `python3 tests/run.py`, ~12 checks, no venv, no
    pytest, no deps.
14. **Region and trigger counts asserted against a threshold per pack**, plus one
    in-game FPS check on Chronomancer with a stated baseline and scenario.
    Printing a number is console noise, not a gate — the threshold is what makes
    it catch a regression. Baseline is the shipped Runemaster pack's counts.
15. **Diagrams in the plan and in code comments** — the band ladder doubles as
    the spec for derived spacing.
16. **Chronomancer stays the acceptance test.** Codex argued it bundles too many
    new variables. Rejected: engine breakage attributes to the structural gate on
    Runemaster, not to Chronomancer, so the residual risk is class-data-only —
    which is exactly what the test is meant to measure.

---

## The band ladder

Authority is the **generated guide artifact** (`mkguide.py`, rendered 1:1 from
the built `final8` pack), not the constants in `build_runemaster.py`. Reading
the constants is what produced the two earlier wrong ladders — three of them
(`Y_PROCS`, `Y_CDS`, `Y_DOTS`) are dead code corresponding to bands that have
never rendered. Full spec in `notes/layout-standard.md`.

```
                 anchor   icon   unit     band
  ┌────────────┐  -18     38px   player   reminders      missing imbues/etchings
  ├────────────┤  (drv)   28px   TARGET   on target      your DoTs or your HoTs
  ├────────────┤  -84     36px   player   on me          procs, running CDs, buffs
  ├────────────┤ -132     44px   —        MAIN           core rotation, always on
  ├─ ─ ─ ─ ─ ─ ┤ -168     20px   —        resource 1   ┐ RESOURCE STACK
  ├─ ─ ─ ─ ─ ─ ┤ -194     16px   —        resource 2   │ 1..N bands, ordered
  ├─ ─ ─ ─ ─ ─ ┤ (drv)     ..    —        resource N   ┘ by config
  ├────────────┤ -224*    26px   —        offensive CDs  wraps at 12
  ├────────────┤ -254*    26px   —        defensive+util wraps at 12, trinkets last
  └────────────┘ (drv)    28px   —        long-term      derived from 6/7 depth

  * anchors shown for a 2-resource class. Resource count varies 1-3:

      1  Engravement, Riftblade   mana
      2  Glyphic                  mana + glyphs
      2  Chronomancer/Artificer   mana + combo points
      3  Pyromancer (class 24)    heat, ember, mana

  (drv) anchors are engine-computed. THREE independent sources of variable
  height below the main row -- the target band's placement, the resource stack's
  depth, and cooldown wrapping -- so no anchor below MAIN can be a constant.
```

**Band 7 already overflows in `final8`.** Engravement utility is 23 icons =
642px against a 274px main row, and the old fixed −300 long-term anchor left
only 19px of clearance. `CD_PER_ROW = 12` was clearly meant to wrap it and was
never wired up. Not hypothetical, not deferred — fixed in Phase 1c.

## The pipeline

```
  gather ──────────► categorise ──► build ──► guide ──► [HUMAN] ──► ship
   db.exil.es         classes/      wapack   mkguide    in-game     ~/ascoa/
   db.ascension       <class>.json  engine   artifact   screenshot  weakauras/
   sidekick                │                    │           │        <class>/
   audit_cds.py            │                    │           │        4 files
   fetch_icons.py          ▼                    ▼           ▼
                     validate:            REVIEW HERE,   tooltips win →
                     unresolved → exit 1  BEFORE import  in-game-verified.json

  ─── agents parallelise everything left of [HUMAN]. that gate is the only
      shared serial resource. WA_VERIFY (Phase 1b) shrinks passes/class 4 → 1.
```

## The load-bearing risk

`build_runemaster.py` is 1023 lines with zero tests, and its output is
**verified in game** at tag `final8`. Extracting an engine from it by hand is
exactly the kind of refactor that silently breaks a working pack — and the
feedback loop is a human screenshot, so breakage is expensive to detect.

**Mitigation, and it gates everything after it:** freeze the shipped export,
decode it, and make every extraction commit prove structural equality against
that tree. Pin `VERSION`/`UID_SALT`, since the salt feeds every uid.

If Phase 1a cannot hold structural equality, stop and reconsider before touching
Chronomancer. Never debug the engine and a new class at the same time.

---

## SEQUENCING REVISED — 2026-07-28

**Phase 0 is complete. Chronomancer now runs BEFORE the engine extraction.**

The plan below sequences extraction (Phases 1a/1b/1c/2) ahead of Chronomancer,
with Chronomancer as the acceptance test. That order is reversed:

1. **Now** — `build_chronomancer.py`, forked from `build_runemaster.py` with
   Chronomancer data. Runemaster is untouched and stays comparator-protected
   throughout.
2. **Then** — extract `wapack.py` from what the two builders *actually* share.

Reason: extracting an engine from a single example is guesswork about which
parts are class-agnostic. A second real class is the evidence. Codex's pass-2
review hinted at the same thing from the other direction ("JSON config is
premature ... freeze it only after Chronomancer reveals the real shape"), and
decision 5 already deferred the config format for exactly that reason.

What this does NOT change:
- The comparator and `tests/run.py` stay the gate. Runemaster must keep
  rebuilding to its fixture while Chronomancer is developed.
- The layout standard in [[layout-standard]] still governs both.
- Phases 1a-1c and 2 still happen, just informed by two classes instead of one.

Phase 4 below (Chronomancer through the new path) becomes Phase 4 *through the
forked path*; steps 1-6 of it are otherwise unchanged.

## What Phase 0 actually delivered

- Path authority fixed; the builder runs again (`SP` pointed at `tools/` while
  data had moved to `resources/`)
- `tests/compare.py` structural comparator + `tests/run.py`, 23 checks,
  including 5 mutation checks proving the comparator can fail
- `tests/fixtures/` frozen at `final11`
- Version control: public repo `github.com/JesterCharles/coa-weakauras`
- Trinkets removed (crash source, and player gear rather than class content)
- Class + spec load gating on every leaf, asserted at build time
- `docs/` GitHub Pages site and `submissions/` generators

---

## Phase 0 — Path authority, repo, comparator, golden fixture

**The builder does not currently run.** `SP = os.path.dirname(__file__)` resolves
to `tools/`, but four data files were moved to `resources/`:

```
$ python3 tools/build_runemaster.py
FileNotFoundError: .../tools/exiles-runemaster.json
```

Nothing in this plan can start from a "known-good baseline" until that is fixed,
and there are **three forks of the builder** to disambiguate first:

| Path | Size | Modified | Status |
|---|---|---|---|
| `tools/build_runemaster.py` | 46,931 | Jul 28 **01:31** | Current. Will not run |
| `output/build_runemaster.py` | 26,501 | Jul 27 16:53 | **Stale fork**, pre-`final8` (no `VERSION`) |
| `output/*.txt` | — | Jul 27 16:33–16:58 | **Stale output** from the stale fork |
| `~/ascoa/weakauras/runemaster/*.txt` | — | Jul 28 **01:31** | **The shipped `final8` pack** |

The mtime match says `tools/build_runemaster.py` produced the shipped pack at
01:31, before the data files moved. The trap: "capture golden fixtures from the
shipped pack" reads as `output/` to anyone who hasn't checked, which would
freeze a **pre-`final8` build** as the target every future refactor must match.

**Steps, in order:**

1. **Establish path authority.** One tree per role, stated in the README:
   ```
   resources/   ALL source data -- scraped snapshots, verified ids, class config
   tools/       code only. SP points at ../resources
   output/      build artifacts. gitignored. NEVER a source of truth
   ~/ascoa/weakauras/<class>/   the shipped pack
   ```
   Delete `output/build_runemaster.py` and the stale `output/*.txt`. Delete the
   duplicate `tools/in-game-verified.json` (identical to `resources/` today,
   forkable tomorrow). Fix `SP` in every tool that reads data.
2. **Create `resources/pack-ids.json`.** `fetch_icons.py:32` reads it and it
   does not exist, so the gather pipeline is not end-to-end.
3. **Prove regeneration.** Run the builder; decode both it and
   `~/ascoa/weakauras/runemaster/`; compare structurally. **If the current tree
   cannot reproduce what shipped, stop and find out why** — that is a finding
   worth having before a refactor, not during one.
4. `git init`; commit as the baseline **only once step 3 passes**. Commit the
   scraped snapshots (decision 7). `in-game-verified.json` is ground truth and
   irreplaceable.
5. Freeze the golden fixture from `~/ascoa/weakauras/runemaster/` — all-specs
   plus each of the three per-spec strings, at `VERSION = "final8"`. Pin
   `VERSION`/`UID_SALT`; the salt feeds every uid.
6. `tests/compare.py` — decode via `wacodec`, normalise **uids and key order
   only**, diff. Child order is preserved, not sorted (decision 4). **The
   comparator needs its own tests: one that false-passes is worse than none.**
   ~5 mutation checks — perturb a band constant, drop a trigger, reparent a
   region, flip `disjunctive`, reorder a row; each must fail.
7. `tests/run.py` — plain asserts, stdlib only, no deps.

Exit: the tree regenerates the shipped pack structurally; `python3 tests/run.py`
green on unchanged source and provably red on each of the 5 mutations.

## Phase 1a — Extract the engine, constants intact

Move out of `build_runemaster.py` into `wapack.py`, **one commit per
extraction**, comparator green after each:

- band geometry and the Y-anchor ladder — as the existing constants, unchanged.
  **Delete the dead ones in their own commit**: `Y_PROCS`, `Y_CDS`, `Y_DOTS`,
  `SZ_STATE` are referenced nowhere and describe bands that have never
  rendered. Comparator must stay green across that commit — if it goes red, a
  constant was not actually dead and the ladder is wrong again. `CD_PER_ROW` and
  `dot_bars()` are also currently dead but are **kept**, wired up in Phase 1c
- `cd_icon`, `cd_group`, `buff_group`, `dot_bars`, `mana_bar`, `seg_bar`,
  `row_w`, `thin` — already generic in shape, class-specific only in inputs.
  `mana_bar` hardcodes `BAR_H` and always emits value text, so it needs a height
  parameter and a text toggle before `prominence: "minor"` is expressible;
  `seg_bar` already takes `h`. Extract as-is here, parameterise in 1c
- proc→glow wiring, charge text, urgency thresholds
- **id resolution collapsed to one ordered resolver** (decision 11), precedence
  matching `class-pack-process.md`: in-game tooltip → db.exil.es →
  db.ascension.gg → coabuildhub → ascensionsidekick
- icon resolution and the no-repeated-art check
- spec gating via `load.use_spellknown` **at the leaf** — extract as-is. The
  missing class gate is a behaviour change and belongs in 1c, not here
- the validation pass (integrity, overlaps, duplicate ids/uids, dangling
  condition references) — now **exits nonzero** on unresolved names, with
  `--allow-unresolved` to override (decision 12)
- print region and trigger counts per built pack (decision 14)

Ship the band ladder ASCII above as the header comment of `wapack.py`.

Exit: `build_runemaster.py` is config + driver only; comparator still green.

## Phase 1b — `WA_VERIFY`

A build flag that strips `load.use_spellknown` gating so every spec's displays
render on one character in one login. Turns ~4 screenshot passes per class into
1. This is the only work in the plan that touches the actual bottleneck.

**Stripping the gate is not sufficient on its own.** Every spec root anchors at
the same coordinates, so ungated they render on top of each other — overlap, not
a readable screenshot. Verify builds therefore also **offset each spec root
horizontally**, so the stacks sit side by side:

```
  WA_VERIFY off              WA_VERIFY on
  (one spec loaded)          (all specs, offset)

      [ spec ]           [spec1] [spec2] [spec3]
                          x=-400   x=0    x=+400
```

The offset lives on `spec_group`'s anchor and only exists in verify builds.

A verify build must be **unshippable**: it carries a loud marker in the group
name and the ship step refuses it. Nothing else stops a gate-stripped pack from
reaching a player, and the failure is silent (T6).

Exit: one `WA_VERIFY` import shows all three Runemaster specs side by side,
legibly, and the ship step rejects that build.

## Phase 1c — Derived spacing, wrap, target band

*Separate from 1a by design (decision 10).* **This is the only phase that
changes Runemaster's output**, so all five behavioural changes land here
together and re-baseline the fixture once. The ladder diagram is the spec.

1. **Derived spacing.** The whole ladder computed top-down from real band
   heights plus a fixed inter-band gap — engine-owned, not per-class
   arithmetic. Must handle a **1..3 band resource stack of mixed heights**, not
   just present/absent: Runemaster only ever exercised 1-vs-2 at a uniform
   height, and Pyromancer's three (ember 16px, mana 20px, heat 10px `minor`) is
   unreachable with fixed anchors. Stack depth cannot be inferred from band
   count — it must sum real heights. Build a synthetic 3-resource config and
   assert the ladder collapses correctly at 1, 2 and 3 with a `minor` entry
   present; Runemaster alone cannot prove this.
2. **Wrap bands 6 and 7 at `CD_PER_ROW = 12`.** Fixes the live Engravement
   overflow (23 icons, 642px). Each wrapped row costs another `CD_ROW_STEP`.
3. **Long-term anchor becomes derived**, computed from the actual depth bands 6
   and 7 reach. Fixed −300 cannot survive a wrap.
4. **Split band 2 by unit.** "On me" keeps `unit="player"` entries; the new
   target band takes everything currently carried as
   `{"unit": "target", "helpful": False}`. `dot_bars()` is the implementation —
   already written, currently zero callers — so the *rendering* is not new.
   **The data migration is the real work**, and it is more than wiring: target
   entries are currently mixed into `buff_group()` state tuples, some carrying
   ad-hoc options and alias lists (`SHORT_ENTRIES`' "Frost Prison" has
   `"alt": ["Permafrost Rune", "Glacial Rune", "Cryobrand", "Frozen"]`).
   Splitting them requires deciding display-id naming, preserving every
   alternate aura name, and keeping `own_only` on — drop it and the band fills
   with every other player's auras in a raid, silently (T5).

5. **Fix leaf gating — two holes, both shipped in `final8`.**

   | | all-specs pack | per-spec pack |
   |---|---|---|
   | Core leaves | `use_class` | `use_class` + `spellknown(that spec)` |
   | Spec leaves | `use_class` + `spellknown(own spec)` | same |

   ```python
   c["load"]["use_class"] = True
   c["load"]["class"] = CLASS_TOKEN            # every leaf, no exceptions

   spec = owning_spec(c) or SPEC_ONLY_TITLE    # Core inherits in a per-spec build
   if spec:
       c["load"]["use_spellknown"] = True
       c["load"]["spellknown"] = SPEC_KNOWN[spec]
   ```

   - **No class gate anywhere.** `wabuild.py:281` emits an empty
     `"class": {"multi": {}}` with no `use_class` flag, so every pack loads on
     every character of every class.
   - **Per-spec packs don't spec-gate Core.** `restrict_to_spec()` (`:969`)
     keeps `RM Core` whole and only drops the other spec groups, so the
     Riftblade-only pack's alerts render on a Glyphic character.

   Core stays class-wide in the all-specs pack on purpose — engravings and
   etchings are class-wide, so spec-gating them there would hide them on two
   specs out of three.

   The visible symptom is the reminder band: inverse-triggered ("show when
   missing"), so on a character that can never satisfy it, it is permanently on
   screen.

   Blocked on the token: CoA classes are ids 12–32, not base WoW classes, so
   decode the manually-corrected export in `resources/import-strings/` and read
   the real `load` block rather than guessing between `class.multi`,
   `class.single` and `class_and_spec`.

   Assert both afterwards: any leaf without a class gate fails the build, and in
   a per-spec build any leaf without a spec gate fails too.

**Commit protocol — expected-diff, not green.** Steps 1–5 each change output by
design, so "comparator green after each commit" is impossible after the first
one. Instead: each commit produces a structural diff, the diff is reviewed
against what that commit was *supposed* to change, and an approved diff
re-baselines the fixture for the next commit. Five commits, five reviewed
diffs, five re-baselines. A diff containing anything the commit did not intend
is a stop.

*(This replaces the first draft's "green after each, re-baseline once at the
end", which contradicted itself.)*

Exit: comparator green against the re-baselined fixture; a class with no
resource stack of 1, 2 and 3 each produces a correctly-collapsed ladder; a
23-icon utility row wraps without colliding with long-term.

## Phase 2 — Config schema + driver

1. `classes/<class>.py` — a **Python data module** exporting a plain dict
   (decision 5). No schema layer, no parser. Carries exactly what is per-class:
   `class_id`, specs and their `SPEC_KNOWN` spell, `ELSEWHERE`, `OFFENSIVE`,
   `OFFENSIVE_TAIL`, `DEFENSIVE`, `PROC_GLOW`, `CHARGES`, the **ordered resource
   list**, long-term buffs, target-band entries, data-source paths.

   **Target-band entries carry their full shape from the start** — `unit`,
   `helpful`, `own_only` and `aliases` all land in Phase 2, not Phase 3.
   Runemaster already needs `helpful=False` at port time, and every alias list
   in `SHORT_ENTRIES` has to survive the migration. Deferring `helpful` to the
   healer phase would mean a second migration of the same data.

   The resource list is where the old "primary + optional secondary" schema
   breaks. A class has 1 to 3 resources and each needs **three independent
   axes** — a single `kind` field cannot express Pyromancer's ember at all.
   Ordered most-glanced first:
   ```python
   "resources": [
     {"source": "aura_stacks", "aura": "Ember", "count": 5,
      "render": "segments", "prominence": "primary"},
     {"source": "power",  "power": "mana",
      "render": "bar",      "prominence": "primary"},
     {"source": "power",  "power": "heat",
      "render": "bar",      "prominence": "minor"},
   ]
   ```
   - `source` — `power` (UnitPower) · `aura_stacks` (one aura, stack count fills
     N cells) · `aura_set` (N distinct auras, one per cell)
   - `render` — `bar` (20px) · `segments` (16px)
   - `prominence` — `primary` (full height, value text) · `minor` (half height,
     no value text, **full width retained**)

   `aura_set` is what `seg_bar` already implements. **`aura_stacks` is new
   code**, built when a class in scope needs it.

   **Open — power-type resolution is unspecified.** `power_trigger(unit,
   power_type=0)` takes the type as a parameter, but nothing maps a name like
   `"mana"` or `"heat"` to an int, and a CoA custom power may not be exposed
   through `UnitPower` at all. Runemaster only ever needed `0`. Resolve this
   with real data during the Chronomancer gather — do not invent a mapping
   table from guesses.

   **Open — combo points may not be `aura_stacks`.** In WoW-like clients combo
   points are usually a unit power and are often target-scoped rather than
   player-scoped. Verify against Artificer in game before the abstraction bakes
   the wrong assumption in.

   Validation rejects an empty resource list, an unknown value on any axis, a
   `segments`/`aura_stacks` entry with no `count`, or a stack whose declared
   order does not run primary-before-minor.
2. `build_class.py --class <name> [--spec <spec>] [--wa-verify]` replaces the
   per-class scripts.
3. Hand-rolled validation, clear errors naming the class and field —
   `chronomancer: Time spec missing SPEC_KNOWN`. Fail at config time, never at
   import time in game.
4. **Hook contract written down, not built** (decision 8):
   ```
   engine bands are first-class, including every resource-stack kind.
   a hook may only:  contribute regions to ONE named band slot
                     read the resolved config, never mutate it
   a hook may not:   reorder bands, alter anchors, touch other classes
   status: SPECIFIED, ZERO IMPLEMENTATIONS. build on first real consumer.
   ```
5. **Specify the id resolver, don't just name it.** Decision 11 collapses six
   maps into one ordered resolver, but an unspecified resolver becomes another
   pile of overrides. Write down the normalised per-source record before
   writing the resolver: source name, spell id, display name, aliases, variant
   ids, and how a tie or a disagreement is broken. Sources are in-game tooltip →
   db.exil.es → db.ascension.gg → coabuildhub → ascensionsidekick.
6. Port Runemaster to `classes/runemaster.py`. **Comparator stays green
   through the port** — same tree, new plumbing.

Exit: `build_class.py --class runemaster` reproduces the Phase-1c baseline.

## Phase 3 — Healer config, no new mechanism

Phase 1c already built the target band and Runemaster already exercises it with
DoTs. A healer is now a **config difference, not an engine difference**: the
same band with `helpful=True` entries.

The `helpful` field itself lands in Phase 2 with the rest of the target-band
shape, so this phase adds **no engine change at all** — only data and one check.

1. One check the comparator cannot give: Runemaster has no `helpful=True`
   entries, so verify an ally-targeted HoT renders with timer and stacks.
2. Confirm against the decoded `chronomancer-nnoop.txt` that a working community
   aura surfaces HoTs the same way before trusting it.

`notes/layout-standard.md` is already corrected (decision 9) and rewritten
against the guide artifact — it now carries the full 9-band ladder, the target
band contract, the derived anchors, and the dead-constant list.

## Phase 4 — Chronomancer through the new path

Run `class-pack-process.md` end to end, recording every deviation as it happens.

1. Gather: db.exil.es class 22, `audit_cds.py`, `fetch_icons.py`, Sidekick for
   Artificer / Infinite / Time mechanics. Commit the snapshots.
2. Categorise into `classes/chronomancer.py`. Artificer pairs mana with combo
   points → a 2-entry resource stack, `[{bar, mana}, {segments, combo}]`. Time
   exercises the target band's `helpful=True` path.
3. Diff mechanism choices against both decoded community auras in
   `resources/import-strings/`.
4. Build all-specs + three per-spec. Generate and **review the guide artifact
   before importing** — the step that reverses how Runemaster went.
5. One `WA_VERIFY` in-game pass, screenshot per spec, plus a **specified FPS
   check** (decision 14): stated addon set, target dummy, sustained combat, all
   bands populated, compared against the same measurement taken on the shipped
   Runemaster pack. An unscoped "check the FPS" catches nothing.
   Resolve the two open data questions here: **power-type resolution** for
   Chronomancer's resources, and whether **combo points are a unit power or an
   aura stack**. Expect to be wrong about **names**; every tooltip returned goes
   into `in-game-verified.json` and wins.
6. Ship to `~/ascoa/weakauras/chronomancer/`, four files, `VERSION` bumped.

Exit: Chronomancer confirmed in game. **Iteration count recorded — that number is
the pipeline's actual score.**

## Phase 5 — Refine, then codify the agent job

1. Fold every Chronomancer deviation back into `class-pack-process.md`,
   `layout-standard.md`, and the config shape. This is the point of running
   Chronomancer first; do it before any fan-out.
2. **Freeze the JSON schema now, not before** (decision 5). Two classes have
   been through the pipeline, so the fields are observed rather than imagined.
   Port `classes/*.py` to `classes/*.json` plus hand-rolled validation. This is
   the step that makes agent-generated configs possible, which is what fan-out
   needs.
3. Write `notes/class-job-runbook.md` — one self-contained job description an
   agent executes with no cross-class context: inputs, commands, pass/fail
   checks, and the artifact to hand back.
4. Make the human gate explicit and queued: agents run gather→build→guide
   concurrently, then stop and queue for the screenshot pass.

**Plan ends here.** Fan-out across the remaining 19 is scoped separately, and
should open with two classes in parallel — one melee, one caster — as a smoke
test, plus a second healer to prove the target band's `helpful=True` path
generalised rather than fitting Chronomancer specifically.

---

## Carried non-negotiables

From `runemaster-retro.md`, encoded as engine invariants and asserted in the
validation pass rather than remembered:

- gate at the **leaf** on **both class and spec** — `load.use_class` on every
  leaf without exception, `load.use_spellknown` on spec leaves. Group triggers
  and group load are inert. Missing the class gate loads the pack on every
  character of every class, and the ungated Core reminders then render
  permanently (shipped in `final8`)
- dynamic groups `grow: "HORIZONTAL"`, never `"RIGHT"`
- `disjunctive: "any"` on any multi-trigger display meaning "any of these"
- texture path in `displayIcon`; `icon` is a boolean
- resource bar width derived from the main row's icon count
- **bump `VERSION` every release** or WeakAuras silently keeps the old copy
- change one mechanism at a time so a failure is unambiguous

## Open, tracked

- Does the fork expose spell charges to `%s`? Unverified in shipped Runemaster
  (Runeblade/Zenith counters). Confirm during the Chronomancer in-game pass.
- Do all Runemaster proc→ability glow mappings match real aura names? Same pass.
- Firecrawl concurrency under parallel agents (one Colima VM, 8GB/4CPU) —
  belongs to the deferred fan-out scope.
