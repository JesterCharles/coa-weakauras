---
title: "What transfers between class packs, and what does not"
date: 2026-07-28
type: reference
status: budding
tags: [weakauras, conquest-of-azeroth, engine, process, chronomancer]
---

# What transfers between class packs

Runemaster is the only built class, so this is the fork guide for the second
one — and the evidence base for extracting `wapack.py` afterwards, which
`pipeline-plan.md` deliberately sequences **after** Chronomancer. Extracting an
engine from one example is guesswork about what is class-agnostic; this file is
the measurement, not the guess.

Measured against `build_runemaster.py` at `final17` (1495 lines) by walking the
module AST and classifying each top-level definition.

| | Lines | What to do with it |
|---|---|---|
| **Machinery** | 661 | Reuse verbatim |
| **Data tables** | 107 | Replace wholesale |
| **Assembly** | 408 | Rewrite per class |

**~56% of the builder is machinery a second class reuses unchanged.** That is
the number to re-measure after Chronomancer: if it holds, the extraction is
mechanical; if it collapses, the "universal" parts were Runemaster-shaped after
all and the plan's sequencing was right.

## Machinery — reuse verbatim

These carry no class knowledge. They read tables; they do not contain them.

| Function | Does |
|---|---|
| `cd_icon` | cooldown icon: urgency tiers, readiness desaturate, off-GCD opt-out, proc glow, charges |
| `cd_group` / `buff_group` / `dot_bars` / `seg_bar` / `mana_bar` | the five band shapes |
| `merge_bands` | collapses per-spec bands into shared ones |
| `_band_order` | topological sort that preserves each spec's row order |
| `apply_leaf_gates` / `assert_gated` / `restrict_to_spec` | the whole gating layer |
| `ic` / `sid` / `_id_for` | icon and spell-id resolution with override precedence |
| `data` | resources/ over tools/ path resolver |
| `row_w` / `thin` / `charge_text` / `add` | small helpers |

## Data tables — replace wholesale

107 lines total. This is the per-class work that is genuinely data.

| Table | Lines | What it is |
|---|---|---|
| `OVERRIDE` | 22 | icon overrides where the scrape is wrong or missing |
| `FALLBACK` | 21 | icons for ids with no art at all |
| `SHORT_ENTRIES` | 12 | the active-only buff/debuff row |
| `PROC_GLOW` | 8 | ability → the procs that light it |
| `TATTOOS` | 8 | long-term buff row |
| `ELSEWHERE` | 7 | abilities shown in another band, never repeated |
| `OFFENSIVE` | 6 | damage cooldowns, in press order |
| `SPEC_KNOWN` | 5 | each spec's signature spell — **the gating keystone** |
| `DEFENSIVE` | 4 | defensive cooldowns |
| `ENGRAVINGS` / `ETCHINGS` | 6 | Runemaster-only kit; a new class replaces the concept |
| `CHARGES` / `ALIAS` / `ID_OVERRIDE` / `OFFENSIVE_TAIL` | 4 | small per-class corrections |
| `CLASS_TOKEN` / `ROOT` / `VERSION` | 4 | identity |

`OFF_GCD` is **not** in this list on purpose: it derives itself from
`cooldown-abilities-<class>.json`. Never type it. See
[`off-gcd-detection.md`](off-gcd-detection.md).

`CLASS_TOKEN` should come from `classes.py` rather than being re-typed — it is
not derivable from the class name (Runemaster is `SPIRITMAGE`, Templar is
`MONK`).

## Assembly — rewrite per class

408 lines: the Core block, the per-spec blocks, and the layout calls that place
them. This is where a class's actual shape lives, and it is the part that
should NOT be copied hopefully. Runemaster has a glyph bar; Chronomancer has
combo points and a different resource story.

`emit_bottom_block` sits on the boundary — its *structure* (offense row, utility
row, buff row, in that order) is universal; the `have` set it computes from the
curated lists is class-specific. Expect to keep the shape and replace the
inputs.

## Universal facts about the addon — never re-derive these

Paid for once, on Runemaster. Every one of these cost at least one iteration.

**Gating**
- Group triggers / conditions / load are **inert**. Gate at the leaf, always.
- `use_class` works. An early result suggesting otherwise was a stale
  SavedVariables state on the client, not the condition.
- `load.spellknown` holds **one** spell id. "Spec A or spec B" is not
  expressible — which is why two-spec abilities stay duplicated after a merge.
- `conditionType` is what makes a trigger variable usable in a condition.
  `hidden` does not. `onCooldown` and `spellUsable` are both `hidden = true` and
  both work; `gcdCooldown` has no `conditionType` and is silently dropped.

**Cooldowns**
- `use_showgcd` is applied **blindly** — WeakAuras substitutes the tracked
  global for any spell not already on cooldown, with no per-spell knowledge
  (`GenericTrigger.lua:2795`). Off-GCD abilities must opt out or they sweep
  whenever you press something else.
- Guard escalation tiers with `onCooldown == 1`, never a duration threshold.
  The global is 1.0s base on this server, not 1.5s, and varies 0.5–1.5s.
- `spellUsable == 0 → desaturate` on every cooldown icon. The swipe cannot say
  "you cannot afford this".
- `inverse = true` + `cooldown = true` is **correct** for spell cooldown icons.
  The `Icon.lua:642` nil crash came from the **item** cooldown trigger.

**Layout**
- A dynamic group lays out only children that are loaded **and** showing —
  `ActivateChild` runs from the child's `Expand()` (`DynamicGroup.lua:1227`).
  This is what makes one shared band per class possible instead of one per spec.
- A shared band therefore has **one** `yOffset`. Anything that needs per-spec
  vertical positions must either not be shared, or be absorbed into a
  fixed-height envelope. See `layout-standard.md`.
- Dynamic groups do **not** wrap unless `useLimit` is set. `grow="HORIZONTAL"`
  with `useLimit: false` is one unbroken line at any child count.
- `controlledChildren` order encodes "most-pressed first" and is load-bearing.
  Merging rows across specs must preserve it — `_band_order` topologically
  sorts rather than concatenating.

**Process**
- Bump `VERSION` every release or WeakAuras silently keeps the old copy.
- `VERSION` is not recoverable from a delivered file — it only salts uids.
- The constants in a builder are **not** authority for what shipped. Runemaster
  carried `CD_PER_ROW` and `Y_CDS` as dead constants while the note claimed a
  wrap that did not exist. Verify against the generated guide or a decoded pack.
- When a check compares two outputs of the **same** builder, a bug in logic they
  share moves both sides together and cancels out. Invariants about intent
  belong in the builder (`assert_gated`), not only in `tests/run.py`.

## What is already automatic

Nothing below needs doing per class — `tools/classes.py` drives it off a
`build_<slug>.py` existing:

- `tests/run.py` runs all 11 checks against the new class's packs
- `tests/freeze.py` freezes its fixtures
- `tools/audit_cds.py <class>` scrapes its cooldowns **and** GCD data
- `tools/mksite.py` adds its page and flips its card to shipped
- `tools/mksubmit.py` emits its db.ascension submission entries

The one manual step: after the first build, `tests/run.py` reports the
`core_leaves` count to record in `classes.CORE_LEAVES`.
