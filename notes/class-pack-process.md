---
title: Process for building a CoA class WeakAura pack
date: 2026-07-28
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, process, playbook]
sources:
  - "[[runemaster-retro]]"
  - "[[weakauras-data-model]]"
  - "[[layout-standard]]"
---

# Building a class pack — the repeatable process

Runemaster took ~29 iterations. Everything below exists so the next class takes
a handful. Steps are ordered so that anything which can invalidate later work
happens first.

## 0. Bring infrastructure up

```bash
colima start --memory 8 --cpu 4                     # if not running
docker-compose -f ~/second-brain/tools/firecrawl/docker-compose.yaml up -d
```

Spin both down when the class is finished.

## 1. Read the references first — do not re-derive

| Read | For |
|---|---|
| `notes/weakauras-data-model.md` | field semantics: gating, `disjunctive`, `grow`, icon fields, conditions |
| `notes/layout-standard.md` | the band layout every class follows |
| `notes/runemaster-retro.md` | the ten bugs, so none is repeated |
| `resources/import-strings/*.txt` | four decoded working packs — the reference for "does this mechanism work" |
| `notes/off-gcd-detection.md` | why `use_showgcd` needs per-ability data, and where it comes from |
| `notes/universal-vs-class.md` | **the fork guide** — what to copy verbatim, replace, and rewrite |

### `tools/classes.py` — one place a class is described

Every tool reads class metadata from here: id, load token, spec list, and the
names of that class's data files and packs. It parses
`resources/class-tokens.md` and `resources/ascension-coa-class-ids.md` rather
than copying them, so the reference tables stay authoritative.

```bash
python3 tools/classes.py          # all 21, and which have a builder
```

Slugs are hyphenated — `knight-of-xoroth`, not `knightofxoroth` — because the
91 class/spec icons under `docs/assets/class-icons/` and the published docs/
URLs already use that form. One slug per class, everywhere: data files, pack
names, docs directories, icon paths.

**The tooling is class-driven, not Runemaster-shaped.** A class with a
`build_<slug>.py` in `tools/` is picked up automatically by:

| Tool | What it does for a new class |
|---|---|
| `tests/run.py` | runs all 11 checks against its packs — nothing to write |
| `tests/freeze.py` | freezes its fixtures (`python3 tests/freeze.py <class>` for one) |
| `tools/audit_cds.py` | `python3 tools/audit_cds.py <class>` |
| `tools/mksite.py` | adds its pack page and flips its card to shipped |
| `tools/mksubmit.py` | emits its submission entries |

The one thing that is not automatic: after the first build, `tests/run.py` will
tell you to record `core_leaves=<n>` in `classes.CORE_LEAVES`. That pins the
Core/spec split as a regression guard.

## 2. Gather data (all scriptable, no in-game step)

```bash
# class id: db.ascension.gg/?classes  (12-32, NOT alphabetical)
# authoritative ids + cooldowns:
https://db.exil.es/class/<class>          # 689-ish name->id pairs for Runemaster
https://ascensionsidekick.com/<class>/<spec>   # mechanics, rotations, talent trees
```

- `tools/dbsearch.py` — batch search db.ascension.gg
- `tools/audit_cds.py` — pull the Cooldown **and GCD** rows from every ability's
  page. The GCD half is load-bearing, not a nicety: see
  [`off-gcd-detection.md`](off-gcd-detection.md). Check its `unresolved` list is
  empty before trusting the output — a page that failed to render looks exactly
  like an off-GCD ability.
- `tools/fetch_icons.py` — real name + icon per spell id

**Source precedence:** in-game tooltip → db.exil.es → db.ascension.gg →
coabuildhub → Sidekick. Sidekick is best for *mechanics* and worst for *names*.

**Known trap:** db.exil.es sometimes links a proc rather than the castable
ability. Cross-check against db.ascension.gg's `advType: "Ability"` entries, and
treat "this ability has no cooldown row" as a smell that the id is wrong.

## 3. Categorise abilities

Fill four lists in the builder — everything else is derived:

- `ELSEWHERE` — shown in another band; never repeat in a cooldown row
- `OFFENSIVE` + `OFFENSIVE_TAIL` — damage cooldowns; interrupt/mobility pinned last
- `DEFENSIVE` — defensives
- `PROC_GLOW` — proc → the ability it tells you to press
- `CHARGES` — abilities with charges
- `SPEC_KNOWN` — one spell unique to each spec, for `load.use_spellknown`

Anything with a cooldown that is not categorised falls into Utility
automatically, so nothing silently disappears.

## 4. Build, then check the generated guide BEFORE importing

```bash
python3 build_<class>.py            # all specs
WA_SPEC=<spec> python3 build_<class>.py
python3 mkguide.py                  # publish as an artifact
```

Settle layout on the guide. This is the step that saves import cycles — but note
the guide **centres with CSS**, so it proves geometry and contents, not
WeakAuras' own layout behaviour.

The build must print all of:

```
no repeated icon art within any row
all tracked names resolved to spell ids
leaf gates: N via load.spellknown
```

and the validation pass must show `integrity 0`, `overlaps 0`, no duplicate
ids or uids, and no condition referencing a missing subregion.

## 5. One in-game import

Ask for a screenshot per spec. Expect to be wrong about **names** — that is the
one class of error no amount of scraping settles. Any tooltip that comes back
goes into `resources/in-game-verified.json` and wins over everything.

## 6. Ship

```
~/ascoa/weakauras/<class>/
  README.md
  <class>-coa.txt            all specs        <- always the CURRENT release
  <class>-<spec>.txt         one per spec     <- always the CURRENT release
  archive/
    v<NN>-<class>-coa.txt    every superseded all-specs pack, one flat folder
```

**The delivery folder always holds the current release at the top level.**
Before overwriting it, copy the outgoing **all-specs** file to
`archive/v<NN>-<class>-coa.txt`, numbered for the version being replaced. Only
the all-specs pack is archived — the per-spec packs are strict subsets of it and
rebuild from the same tag. (`runemaster/archive/v8-*` predates that rule and has
all four.)

One flat `archive/` folder, not a folder per release: at 21 classes a
per-release directory each would bury the four files that actually matter.

Copy from `docs/packs/`, which `mksite.py` has already regenerated, so the
delivery folder and the site can never disagree.

Bump `VERSION` on **every** release — it salts the uids. Without a bump,
WeakAuras treats the import as already-installed and silently keeps the old
copy, which is bug #1 in the retro and cost ten iterations.

⚠️ **`VERSION` is not recoverable from a delivered file.** It only feeds
`set_salt()`, so it never appears as a readable string, and the group name is
the same on every release — a delivered pack cannot be identified by opening it
or by looking at the WeakAuras list. (The builder comment claiming VERSION feeds
"the uid salt AND the group name" is wrong; it only does the former.) Identify a
stray file by recomputing uids: `sha256(f"{class}-{spec}-{version}|{display_id}")`
mapped through `wabuild._UID_ALPHA`, and see which candidate version matches.
The delivery README and the `v<NN>-` prefix exist because of this.

## Running classes in parallel

Once Chronomancer confirms this process, each class becomes one self-contained
job that a separate agent can take independently:

```
gather -> categorise -> build -> guide -> [in-game pass] -> ship
```

Everything before the in-game pass is scriptable and has no cross-class
dependency, so agents can run concurrently up to that gate and then queue for
verification — the human screenshot step is the only serial point.

What is shared and already stable (do not re-derive per class):

| Shared | Why it is class-agnostic |
|---|---|
| `wacodec.py`, `wabuild.py` | encoding and region/trigger construction |
| `mkguide.py` | reads any built pack |
| `audit_cds.py`, `fetch_icons.py`, `dbsearch.py` | parameterised by class |
| `notes/weakauras-data-model.md` | addon behaviour, not class behaviour |
| `notes/layout-standard.md` | the band layout all classes follow |
| `resources/in-game-verified.json` | tooltip ground truth, keyed by spell name |

What is genuinely per-class: the category lists in `build_<class>.py`
(`ELSEWHERE`, `OFFENSIVE`, `DEFENSIVE`, `PROC_GLOW`, `CHARGES`, `SPEC_KNOWN`)
and any bespoke display for a mechanic with no analogue.

**Open question to settle during Chronomancer:** whether `build_<class>.py`
should stay a copied-and-edited script or become a thin driver over a per-class
config file. Copying is fine for two classes and a liability by twenty.

**Known gap:** the layout standard has never been exercised against a **healing**
spec. Chronomancer's Time spec is the first. Group-frame health, multi-target
HoT tracking and healer-specific cooldowns have no slot in the current standard
— decide whether to extend it or to scope healing surfaces out of these packs,
and record the decision before building the other healer classes.

## Non-negotiables

- Gate at the **leaf** with `load.use_spellknown`. Group triggers are inert.
- Dynamic groups use `grow: "HORIZONTAL"`. Never `"RIGHT"`.
- Set `disjunctive: "any"` on any multi-trigger display that means "any of these".
- Texture path goes in `displayIcon`; `icon` is a boolean.
- Resource bar width is derived from the main row's icon count.
- Change one mechanism at a time so a failure is unambiguous.

## Forking the builder

`notes/universal-vs-class.md` measures `build_runemaster.py` line by line:
**~56% is machinery that transfers unchanged**, 107 lines are data tables to
replace wholesale, and 408 lines are assembly to rewrite for the class's actual
shape. Read it before copying anything — the point is to copy the 661 lines
deliberately and rewrite the rest, not to fork 1495 lines hopefully and prune.

Do **not** extract `wapack.py` yet. `pipeline-plan.md` sequences that after
Chronomancer on purpose: an engine drawn from one example is a guess about what
is class-agnostic. Re-measure the 56% once a second class is built; if it holds,
the extraction is mechanical.

First thing to check in any fork, before anything else: the `data()` resolver.
`audit_cds.py` sat broken for weeks because it still resolved against `tools/`
after the data moved to `resources/`, and nothing failed loudly.

## Carry-forward checklist — every class inherits these

Everything below was paid for once on Runemaster. A new class must satisfy all
of it. Where a test enforces the rule, the test name is given: run
`python3 tests/run.py` and it fails loudly rather than shipping quietly.

**Cooldown icons** (`cd_icon`)

| Rule | Why | Enforced by |
|---|---|---|
| `spellUsable == 0` → `desaturate` on every spell-cooldown icon | Off cooldown but unaffordable otherwise reads as "press me" | check 9, *desaturate when unusable* |
| `use_showgcd` **off** for every off-GCD ability | WA substitutes the global blindly; an off-GCD icon otherwise sweeps whenever you press something else | check 10, *no off-GCD ability shows the global* |
| `use_showgcd` **on** for every on-GCD ability | otherwise you lose the anti-clipping cue | check 10, *keeps the sweep* |
| Escalation tiers ANDed with `onCooldown == 1` | a bare `expirationTime` tier fires on every global, on every icon | check 9, *no bare expirationTime tier* |
| `OFF_GCD` derived from `cooldown-abilities.json`, never hand-written | 26 of 59 on Runemaster; hand-maintenance does not scale to 21 classes | — (derive it, don't type it) |

**Bands and gating** (from `final16`/`final17`)

| Rule | Why | Enforced by |
|---|---|---|
| One shared band per row, not one per spec | A dynamic group lays out only loaded+showing children (`DynamicGroup.lua:1227`), so a shared band renders exactly the loaded spec's icons. Cut Runemaster 229 → 171 displays | check 11, *merged pack loads the same displays* |
| Merge order is a topological sort, never a concatenation | `controlledChildren` order encodes "most-pressed first" and is load-bearing | `_band_order` |
| A leaf that drops its signature gate must be on **every** spec | `load.spellknown` holds one id, so two-spec abilities cannot be expressed and must stay duplicated | `assert_gated`, *SHARED BUT NOT ON EVERY SPEC* |
| Shared **buff** rows take the class gate alone | Active-only aura displays are self-gating, and a buff id is not something `IsSpellKnown` recognises | — |
| An ability with no db.exil.es cooldown row stays duplicated | Its id may be a proc rather than the castable spell; `IsSpellKnown` would fail and the icon would silently never appear | — |
| Resource area is a **fixed-height envelope** | A shared band has one `yOffset`, so a variable-height resource stack pushes an empty slot onto specs that do not need it | `layout-standard.md` |

**Where an invariant belongs.** If a check would compare two outputs of the same
builder, a bug in logic they share moves both sides together and cancels out —
`tests/run.py` check 11 has exactly this limit. Assertions about *intent* go in
the builder, where the source data still exists. Prove it either way by mutating
the builder and confirming the check fails.

**Things that are true of the addon, not of Runemaster** — do not re-derive:

- `conditionType` is what makes a trigger variable usable in a condition.
  `hidden` does not. `gcdCooldown` has no `conditionType` and is therefore
  unusable; `onCooldown` and `spellUsable` are both `hidden` and both work.
- `inverse = true` + `cooldown = true` is correct for spell cooldown icons.
  The `Icon.lua:642` nil crash came from the **item** cooldown trigger.
- Group triggers / conditions / load are inert. Leaf only.
- `VERSION` salts uids and nothing else — it is not recoverable from a
  delivered file. See §6.

**Layout** — `notes/layout-standard.md` is the contract, but verify against the
generated guide, never against the constants in the builder. Runemaster shipped
with `CD_PER_ROW` and `Y_CDS` defined and never referenced, so the documented
wrap-at-12 did not exist and Engravement's utility row shipped 586px wide
against a 274px main row. **Before shipping, measure every always-visible row's
width** (`n * size + (n-1) * space`) against the resource bar; anything past
~1.2x needs a wrap or a cut.

**Delivery** — flat `archive/v<NN>-<class>-coa.txt`, bump `VERSION`, update the
delivery README's "Current version" line and *What's new*.
