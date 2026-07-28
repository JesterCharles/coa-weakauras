---
title: Eng review — config-driven class pipeline plan
date: 2026-07-28
type: review
status: budding
tags: [weakauras, conquest-of-azeroth, pipeline, review]
sources:
  - "[[pipeline-plan]]"
  - "[[layout-standard]]"
---

# Eng review — `pipeline-plan.md`

Sections 1–4 ran 2026-07-28 and produced 10 issues, all resolved. Outside voice
(Codex) ran twice: once on the original plan (5 findings, 4 integrated, 1
rejected with reasoning) and once on the revised plan. This file carries the
required outputs that close the review.

---

## P0 — the tree does not build (confirmed by execution)

Codex pass 2's headline finding, verified:

```
$ python3 tools/build_runemaster.py
FileNotFoundError: .../tools/exiles-runemaster.json
```

`SP = os.path.dirname(__file__)` → `tools/`, but `exiles-runemaster.json`,
`cooldown-abilities.json`, `exiles-id-meta.json` and `coa-runemaster-skills.json`
live in `resources/`. Three forks of the builder exist:

| Path | Size | Modified | Status |
|---|---|---|---|
| `tools/build_runemaster.py` | 46,931 | Jul 28 **01:31** | Current. Will not run |
| `output/build_runemaster.py` | 26,501 | Jul 27 16:53 | Stale fork, pre-`final8` |
| `output/*.txt` | — | Jul 27 16:33–16:58 | Stale output from the stale fork |
| `~/ascoa/weakauras/runemaster/*.txt` | — | Jul 28 **01:31** | **The shipped `final8` pack** |

`in-game-verified.json` also exists in both `tools/` and `resources/` — byte
identical today, forkable tomorrow.

The mtime match says `tools/build_runemaster.py` produced the shipped pack at
01:31, before the data moved. The trap: Phase 0's "capture golden fixtures from
the shipped pack" reads as `output/` to anyone who hasn't checked, which would
freeze a pre-`final8` build as the refactor target forever.

Phase 0 now fixes path authority and **proves regeneration against
`~/ascoa/weakauras/runemaster/` before freezing anything**. → T0.

---

## What already exists

The plan's framing — "extract an engine from `build_runemaster.py`" — undersells
how much engine is already built. 2960 lines across 10 tools, of which roughly
60% is already class-agnostic.

| File | Lines | State | Plan's treatment |
|---|---|---|---|
| `wabuild.py` | 501 | **Already class-agnostic.** Triggers, subregions, regions, groups. `aura_trigger` already parameterises `unit` / `helpful` / `own_only` — the entire target-band mechanism | Reused, correctly |
| `wacodec.py` | 430 | **Already class-agnostic.** Encode/decode; this is what read the community strings | Reused as the structural comparator — the review's single biggest scope reduction |
| `mkguide.py` | 384 | **Already generic** — reads any built pack | Reused. Its output is now the layout authority |
| `mkpreview.py` | 204 | Generic | Untouched |
| `build_dump.py` | 176 | Generic | Untouched |
| `build_diag.py` | 74 | Generic | Untouched |
| `dbsearch.py` | 69 | Parameterised by class | Reused |
| `audit_cds.py` | 59 | Parameterised by class | Reused |
| `fetch_icons.py` | 40 | Parameterised by class | Reused |
| `build_runemaster.py` | 1023 | Class-specific. **~40% is data**, not logic | Split into engine + config |

Consequences the plan now reflects:

- **`dot_bars()` is already written** (`build_runemaster.py:476`) with `unit` and
  `helpful` parameters, and has zero callers. The target band is not new code —
  it is wiring up a function that was written and never connected.
- **`seg_bar()` already takes `h`**, so `prominence: "minor"` is free for
  segments. `mana_bar()` does not, and always emits value text — the one real
  gap in the resource stack work.
- **`wacodec.py` decoding** is why the structural comparator is cheap. The
  original plan's byte-equality gate would have been built from scratch *and*
  fought the refactor.

**Genuinely new code**, total: the structural comparator, the config schema +
driver, `aura_stacks`, a height/text parameter on `mana_bar`, `WA_VERIFY`, and
the derived-ladder computation. That is materially narrower than "extract an
engine."

---

## NOT in scope

Considered during review and explicitly deferred.

| Deferred | Rationale |
|---|---|
| **Fan-out to the remaining 19 classes** | Original Phase 6. The plan ends when Chronomancer ships; fan-out is a separate plan written *after* Chronomancer's deviations are folded back in. Planning it now would encode assumptions the acceptance test exists to test |
| **Hook layer implementation** | Contract specified in Phase 2, zero implementations. Its only cited consumer (Glyphic's glyph bar) turned out to be a first-class engine band, so the layer has no proven user. Build on first real consumer |
| **Raid frames / group health** | VuhDo and Grid own this on 3.3.5a. Building it would be a second addon, not a class pack |
| **Multi-target HoT tracking** | Dissolved rather than deferred. `unit="target"` + `helpful=True` covers the current target; raid-wide state belongs to the raid frames above |
| **Byte-equality refactor gate** | Replaced by structural equality. Retained only as a one-time harness smoke test |
| **pytest / jsonschema / venv** | Stdlib only, ~12 checks. The 38-path coverage plan was over-built for a project where one integration test retires ~25 paths |
| **Firecrawl concurrency tuning** | One Colima VM, 8GB/4CPU. Only bites under parallel agents, which is fan-out scope |
| **Survey of all 21 classes' resources** | Pyromancer forced the resource schema to generalise. Surveying the other 19 now is a full gather cycle that delays Phase 0; the three-axis schema absorbs what we know |
| **`aura_stacks` implementation** | Specified in the schema, built when a class in scope needs it. Chronomancer's Artificer combo points may be the first — inside scope if so |

---

## Failure modes

For each new codepath: one realistic production failure, whether a test covers
it, whether error handling exists, and whether the user sees it.

| Codepath | Failure | Test? | Handled? | Visible? |
|---|---|---|---|---|
| Structural comparator | Normalises too aggressively and false-passes a real regression | **Yes** — 5 mutation checks exist precisely for this | n/a | Would be silent → mutation checks are the mitigation |
| Structural comparator | Normalises too little; refactor churn shows as a diff | Integration test | n/a | Loud, cheap |
| Ordered id resolver | Two sources disagree; resolver silently picks the wrong id | Resolver unit check | **Yes** — nonzero exit on unresolved | Loud at build |
| Ordered id resolver | A talent *replaces* a spell id (Runelord swaps Zenith 712325→712389); exact-id trigger stops matching | ⚠️ **No** | Partial — `VARIANTS` handles known cases | **Silent in game.** Icon vanishes on spec change |
| Derived ladder | Stack depth summed from band count not real heights → overlap | **Yes** — synthetic 1/2/3-resource config with a `minor` entry | n/a | Visible in guide artifact before import |
| CD wrap at 12 | Wrapped row pushes long-term off-screen | ⚠️ Partial — depth assertion | **Yes** — build assertion | Loud at build |
| Target band | `own_only` dropped → band fills with other players' auras | ⚠️ **No** | No | **Silent until a raid.** Unreadable exactly when it matters |
| Target band | Ally targeted, `helpful=True` entries never fire | Phase 3 check | No | Silent — empty band reads as "no HoTs up" |
| `WA_VERIFY` | Ships to a player with gates stripped | ⚠️ **No** | No | **Silent.** All specs' displays at once |
| `aura_stacks` | Stack count exceeds declared `count` | Schema validation | **Yes** | Loud at build |
| Config validation | Unresolved name with `--allow-unresolved` set habitually | n/a | Flag exists | Loud, then ignored — human factor |

**Critical gaps** — no test, no error handling, and silent:

1. **`own_only` on the target band.** Regression here is invisible solo and
   catastrophic in a raid. It is one field in one call. → T5.
2. **`WA_VERIFY` leaking into a shipped pack.** The flag exists to collapse the
   screenshot gate; nothing stops a build with it set from being shipped. → T6.
3. **Talent-replaced spell ids.** Pre-existing, not introduced by this plan, but
   the plan moves the resolver and inherits the gap. Only detectable by
   respeccing in game. → T7 (P3 — flagged, not fixed here).

---

## Worktree parallelization

| Step | Modules touched | Depends on |
|---|---|---|
| Phase 0 — repo, comparator, fixtures | `tests/`, repo root | — |
| Phase 1a — extract engine | `tools/wapack.py`, `tools/build_runemaster.py` | Phase 0 |
| Phase 1b — `WA_VERIFY` | `tools/wapack.py` | Phase 1a |
| Phase 1c — ladder, wrap, target band | `tools/wapack.py` | Phase 1a |
| Phase 2 — config schema + driver | `classes/`, `tools/build_class.py` | Phase 1c |
| Phase 3 — healer config | `classes/`, schema | Phase 2 |
| Phase 4 — Chronomancer | `classes/`, `resources/` | Phase 3 |
| Phase 5 — refine + runbook | `notes/` | Phase 4 |

**Lanes:**

```
Lane A:  0 -> 1a -> 1c -> 2 -> 3 -> 4 -> 5      all share tools/wapack.py
Lane B:  1b                                      shares wapack.py -> NOT parallel
Lane C:  Chronomancer data gather                independent, no code deps
```

**Verdict: sequential implementation, no meaningful parallelization.** Every
code phase writes `tools/wapack.py`, and the plan's own non-negotiable is
"change one mechanism at a time so a failure is unambiguous." Parallel worktrees
would fight the structural-equality gate, which is the whole safety net.

**One genuine exception:** Lane C — gathering Chronomancer's data (db.exil.es
class 22, `audit_cds.py`, `fetch_icons.py`, Sidekick pages, decoding the two
community auras) touches only `resources/` and depends on no code. It can run in
a parallel worktree from day one and be waiting when Phase 4 opens. Worth doing:
it is the only wall-clock the pipeline work can buy back.

---

## Implementation Tasks

Synthesized from this review's findings. Each task derives from a specific
finding above. Run with Claude Code or Codex; checkbox as you ship.

- [ ] **T0 (P0, human: ~1.5h / CC: ~20min)** — repo — Fix path authority and prove the tree regenerates the shipped pack
  - Surfaced by: Codex pass 2 — builder raises `FileNotFoundError`; three forks; stale `output/` would be frozen as the fixture
  - Files: `tools/*.py` (`SP`), `output/` (delete stale fork + txt), `tools/in-game-verified.json` (delete dup), `resources/pack-ids.json` (create), `README.md`
  - Verify: `python3 tools/build_runemaster.py` exits 0 and structurally matches `~/ascoa/weakauras/runemaster/`. **Blocks every other task.**
- [ ] **T20 (P1, human: ~1h / CC: ~15min)** — `tools/wapack.py` — Class-gate every leaf with `load.use_class`
  - Surfaced by: User, in game — the pack loads on every character of every class. `wabuild.py:281` emits `"class": {"multi": {}}` with no `use_class` flag; `apply_leaf_gates()` gates only leaves whose `owning_spec()` resolves, leaving 17 Core displays ungated. The 2 reminders are inverse-triggered, so they render permanently on any other class. Shipped in `final8`
  - Files: `tools/wabuild.py`, `tools/wapack.py`, `classes/runemaster.py`
  - Blocked on: the CoA class token — decode the manually-corrected export in `resources/import-strings/`
  - Verify: build fails if any leaf lacks a class gate; log in on a non-Runemaster character and see nothing
- [ ] **T1 (P1, human: ~3h / CC: ~25min)** — `tests/` — Build the structural comparator and its 5 mutation checks
  - Surfaced by: Section 1 — "byte-equality is the wrong gate; `wacodec.py` already decodes"
  - Files: `tests/compare.py`, `tests/run.py`
  - Verify: `python3 tests/run.py` green on clean tree, red on each of 5 perturbations
- [ ] **T2 (P1, human: ~30min / CC: ~5min)** — repo — `git init`, commit baseline including scraped snapshots
  - Surfaced by: Section 1 — "gitignoring the scraped bulk is backwards; third-party pages are the least reproducible asset"
  - Files: `.gitignore`, whole tree
  - Verify: `git log` shows one baseline commit; `resources/*.json` tracked
- [ ] **T3 (P1, human: ~20min / CC: ~5min)** — `tools/` — Delete dead constants in an isolated commit
  - Surfaced by: Section 2 — `Y_PROCS` / `Y_CDS` / `Y_DOTS` / `SZ_STATE` referenced nowhere; source of two wrong band ladders
  - Files: `tools/build_runemaster.py`
  - Verify: comparator green across the deletion commit — red means a constant was not dead
- [ ] **T4 (P1, human: ~2h / CC: ~20min)** — `tools/wapack.py` — Collapse 5 id maps into one ordered resolver
  - Surfaced by: Section 2 — `FALLBACK` / `OVERRIDE` / `IN_GAME` / `CROSSCHECK` / `ID_OVERRIDE` / `VARIANTS`, precedence as ad-hoc dict merges
  - Files: `tools/wapack.py`
  - Verify: resolver check asserts documented precedence; comparator stays green
- [ ] **T5 (P1, human: ~15min / CC: ~5min)** — `tools/wapack.py` — Assert `own_only` on every target-band trigger
  - Surfaced by: Failure modes — critical gap 1, silent until a raid
  - Files: `tools/wapack.py`, `tests/run.py`
  - Verify: build assertion fails if any target-band entry omits `own_only`
- [ ] **T6 (P1, human: ~15min / CC: ~5min)** — `tools/build_class.py` — Make `WA_VERIFY` builds unshippable
  - Surfaced by: Failure modes — critical gap 2, silent
  - Files: `tools/build_class.py`
  - Verify: `WA_VERIFY` output carries a loud group-name marker and the ship step refuses it
- [ ] **T7 (P1, human: ~45min / CC: ~10min)** — `tools/wapack.py` — Nonzero exit on unresolved names, `--allow-unresolved` override
  - Surfaced by: Section 2, issue 8 — unattended agent would ship a broken pack and report success
  - Files: `tools/wapack.py`, `tools/build_class.py`
  - Verify: build exits 1 on a deliberately-broken config, 0 with the flag
- [ ] **T8 (P1, human: ~4h / CC: ~40min)** — `tools/wapack.py` — Derived ladder handling a 1–3 band mixed-height resource stack
  - Surfaced by: Section 2, issue 6 + resource stint — Pyromancer's 16/20/10px stack is unreachable with fixed anchors
  - Files: `tools/wapack.py`, `tests/run.py`
  - Verify: synthetic 1/2/3-resource configs with a `minor` entry collapse correctly
- [ ] **T9 (P1, human: ~1h / CC: ~15min)** — `tools/wapack.py` — Wrap cooldown bands at `CD_PER_ROW`, derive long-term anchor
  - Surfaced by: Section 2 — Engravement utility ships at 642px vs a 274px main row; long-term has 19px clearance
  - Files: `tools/wapack.py`
  - Verify: 23-icon row wraps; no overlap with long-term at any depth
- [ ] **T10 (P2, human: ~2h / CC: ~20min)** — `tools/build_class.py` — Config schema validation, hand-rolled
  - Surfaced by: Section 3, issue 9C — stdlib only, better errors than jsonschema
  - Files: `tools/build_class.py`
  - Verify: bad config exits 1 naming class and field
- [ ] **T11 (P2, human: ~1h / CC: ~10min)** — `tools/wapack.py` — Parameterise `mana_bar` height and value text
  - Surfaced by: Resource stint — `prominence: "minor"` is inexpressible without it; `seg_bar` already takes `h`
  - Files: `tools/wapack.py`
  - Verify: a `minor` bar renders at 10px with no value text
- [ ] **T12 (P2, human: ~45min / CC: ~10min)** — `tools/wapack.py` — Print region and trigger counts per built pack
  - Surfaced by: Section 4, issue 10A — no aura-count or CPU budget; a pack that drops frames is uninstalled silently
  - Files: `tools/build_class.py`
  - Verify: build prints counts; one in-game FPS check on Chronomancer
- [ ] **T13 (P2, human: ~30min / CC: ~10min)** — `notes/` — Band ladder + pipeline ASCII into `wapack.py` header comments
  - Surfaced by: Section 1, issue 4A — zero diagrams against stated preference
  - Files: `tools/wapack.py`
  - Verify: ladder comment matches `layout-standard.md`
- [ ] **T14 (P3, human: ~2h / CC: ~20min)** — `tools/wapack.py` — Detect talent-replaced spell ids
  - Surfaced by: Failure modes — critical gap 3, pre-existing, only visible by respeccing in game
  - Files: `tools/wapack.py`
  - Verify: a known replacement pair (Zenith 712325→712389) resolves under both ids

- [ ] **T15 (P1, human: ~1h / CC: ~10min)** — `tools/wapack.py` — Offset spec roots in `WA_VERIFY` builds
  - Surfaced by: Codex pass 2 — stripping gates renders all specs at the same coordinates; that is overlap, not one screenshot
  - Files: `tools/wapack.py` (`spec_group` anchor), `tools/build_class.py`
  - Verify: one verify import shows three specs side by side, legibly
- [ ] **T16 (P1, human: ~2h / CC: ~20min)** — `classes/` — Normalise target-band data out of `buff_group` state tuples
  - Surfaced by: Codex pass 2 — `dot_bars()` exists, but entries carry ad-hoc options and alias lists (`SHORT_ENTRIES` "Frost Prison" has 4 alts); this is a data migration, not wiring
  - Files: `classes/runemaster.py`, `tools/wapack.py`
  - Verify: every alias survives the split; expected-diff review shows no dropped aura name
- [ ] **T17 (P2, human: ~1.5h / CC: ~15min)** — `tools/wapack.py` — Specify the normalised per-source record for the id resolver
  - Surfaced by: Codex pass 2 — "the resolver is named, not specified; it will become another pile of overrides"
  - Files: `notes/class-pack-process.md`, `tools/wapack.py`
  - Verify: schema documents source, id, name, aliases, variants, tie-breaking before the resolver is written
- [ ] **T18 (P2, human: ~45min / CC: ~10min)** — `tools/build_class.py` — Turn counts and FPS into gates with thresholds
  - Surfaced by: Codex pass 2 — "counts printed is console noise"; "FPS check is not actionable — no threshold, baseline, scenario, or addon set"
  - Files: `tools/build_class.py`, `notes/class-pack-process.md`
  - Verify: build fails past threshold; FPS procedure names addon set, dummy, sustained combat, and the Runemaster baseline
- [ ] **T19 (P3, human: ~30min / CC: ~10min)** — `tools/wapack.py` — Independent layout invariant assertions
  - Surfaced by: Codex pass 2 — `mkguide.py` renders the built pack, so it documents layout bugs faithfully; it cannot validate them
  - Files: `tests/run.py`
  - Verify: assertions catch band overlap and wrong band order without reading the guide

_No new tasks from Section 4 beyond T12 and T18._

---

## Diagrams — where inline ASCII belongs

| File | Diagram | Why |
|---|---|---|
| `tools/wapack.py` (header) | Band ladder with anchors and heights | Doubles as the spec for derived spacing. Highest-value comment in the codebase |
| `tools/wapack.py` (ladder fn) | Stack-depth computation, 1/2/3 resources | The mixed-height sum is the non-obvious part |
| `tools/build_class.py` (header) | gather → categorise → build → guide → \[HUMAN\] → ship | Names the serial bottleneck where an agent must stop |
| `tests/compare.py` (header) | What normalisation drops vs preserves | A reader must know why a diff is or is not real |

---

## Review log

| Section | Findings | Resolved |
|---|---|---|
| 1 Architecture | 4 | 4 |
| 2 Code quality | 4 | 4 |
| 3 Test | 1 + regression rule | 1 (scope cut 38 paths → 12 checks) |
| 4 Performance | 1 + 1 routed to TODO | 1 |
| Outside voice (pass 1) | 5 | 4 integrated, 1 rejected with reasoning |
| Outside voice (pass 2) | 15 | 13 integrated, 1 corrected, 1 partial |
| Post-review (user direction) | 2 | Target band, resource stack |

Two findings came from the user rather than the review, and both were larger
than anything the review caught: the target-band unification (killed the
multi-target HoT work entirely) and the 3-resource stack (broke the
primary/secondary schema outright). Both were invisible from inside the
Runemaster codebase.

### Codex pass 2 disposition

| # | Finding | Disposition |
|---|---|---|
| 1 | Builder doesn't run; wrong data paths | **Confirmed by execution.** T0, Phase 0 rewritten |
| 2 | Split authority across `resources/`/`tools/`/`output/` | **Confirmed, worse than stated** — stale builder fork + stale output + duplicated ground truth. T0 |
| 3 | `WA_VERIFY` produces overlap, not one screenshot | Correct. Spec roots now offset. T15 |
| 4 | Comparator must not sort child order | Correct — `controlledChildren` order is semantic. Decision 4 amended |
| 5 | `mkguide.py` is a circular authority | Partial. Valid for *what shipped* (its use here), invalid for *what is correct*. T19 adds independent invariants |
| 6 | Phase 1c contradicts itself | Correct. Replaced with expected-diff-per-commit |
| 7 | `dot_bars()` "just needs wiring" understates the data migration | Correct — aliases and ad-hoc options. T16 |
| 8 | `helpful` scheduled a phase too late | Correct. Full target-band shape moves to Phase 2 |
| 9 | Power-type resolution missing | Real gap, **mis-stated** — `power_trigger(unit, power_type=0)` is a parameter with a default, not hardcoded. Left open, resolved with real data in Phase 4 |
| 10 | Combo points as `aura_stacks` is an unstated bet | Correct. Flagged open, verified in Phase 4 |
| 11 | "Names dedupe across bands" is wrong | Correct — an offensive CD deliberately appears in two bands (`:783-794`). Rule corrected to display-id uniqueness |
| 12 | Printed counts are not a gate | Correct. Threshold added, T18 |
| 13 | FPS check not actionable | Correct. Scenario and baseline specified, T18 |
| 14 | Resolver named, not specified | Correct. T17 |
| 15 | `fetch_icons.py` needs `pack-ids.json`, which doesn't exist | **Confirmed** (`fetch_icons.py:32`). T0 |
| — | JSON config premature | Accepted. Python data module first, JSON frozen in Phase 5 |

One correction to Codex: finding 9 claims `power_trigger()` hardcodes
`powertype=0`. It does not — `wabuild.py:178` takes `power_type=0` as a default
parameter. The underlying gap (no name→int mapping, custom CoA powers may not be
`UnitPower` at all) is real and stands.
