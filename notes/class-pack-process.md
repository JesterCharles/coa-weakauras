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

## 2. Gather data (all scriptable, no in-game step)

```bash
# class id: db.ascension.gg/?classes  (12-32, NOT alphabetical)
# authoritative ids + cooldowns:
https://db.exil.es/class/<class>          # 689-ish name->id pairs for Runemaster
https://ascensionsidekick.com/<class>/<spec>   # mechanics, rotations, talent trees
```

- `tools/dbsearch.py` — batch search db.ascension.gg
- `tools/audit_cds.py` — pull the Cooldown row from every ability's page
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
