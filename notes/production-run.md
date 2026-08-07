---
title: The production run — drafts for all 18 remaining classes
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, process, production]
sources:
  - "[[class-pack-process]]"
  - "[[class-requirements-template]]"
---

# The production run

Three classes shipped (Runemaster, Chronomancer, Pyromancer). Eighteen remain,
~60 specs. This note is the operating policy for producing all of them: what
"done" means, what is frozen, how classes are batched, and how community
feedback replaces the perfection loop.

**The point of the site is a credible DRAFT per class and spec that the
community converges through feedback — not a perfect pack per class.**
`class-pack-process.md` still governs *how* a class is built; this note governs
*when to stop*.

## The draft bar — definition of done

A class ships when the `research`, `build` and `verify` phases seal in
`phaselog.py`. The in-game pass is **no longer part of the ship gate** — it
moved to a post-ship `verified` phase. Concretely, a draft has:

- changelog triaged, mechanics sources per spec, 100% cross-database sweep,
  requirements doc answered, citations imported, zero `seed:`/`prop:` markers
  (`--gate research`)
- main rows ordered from cited rotation text, §2 talents handled, §3 pets
  answered, procs wired, alerts built (`--gate build`)
- `tests/run.py` green, guide read, §6 UNKNOWNs closed or deferred on purpose
  (`--gate verify`)

It ships via `mksite.py --allow-unverified`, which badges every affected pack
**draft** on the page — said on the pack itself, at the point of decision.
`python3 tools/verified.py record` flips the badge off later, when either a
batch in-game sweep or a credible community confirmation closes the `verified`
phase. Neither blocks the next class.

What a draft explicitly tolerates, because feedback settles it cheaper than
another research round: wrong *names* (the one error class no scrape settles),
suboptimal press order within a cited priority, art choices, row-width taste.
What it never tolerates: uncited rotation claims, abilities only one database
has heard of, unreviewed inventory markers, red tests. The draft bar lowers the
*verification* standard, not the *honesty* standard.

## Inventory review in draft mode

Row-by-row human reads do not scale to 18 classes × ~200 rows. The Pyromancer
precedent is the production default: an automated pass proposes roles with one
line of reasoning per row in the Notes cell, and the `prop:` markers are
cleared in bulk — **with the bulk-clear recorded in the buildlog note, so the
provenance is never disguised as a human read.** The rows whose Notes hedge
("reads like", "could read") are copied into §6 of the requirements doc as
open questions; feedback and the eventual in-game sweep are their checklist.

## Freeze policy — the three shipped classes

Runemaster, Chronomancer and Pyromancer are **frozen**. A frozen class gets a
release only when:

1. `changelog_watch.py` flags drift that touches it, or
2. community feedback reports a defect, or
3. an engine fix lands that `tests/run.py` check 1 shows changes its output.

No self-initiated polish. An idea for an improvement goes into the class's
requirements doc §6 as a note, where feedback can vote on it — it does not
become a release on its own.

## Batching — archetype clusters, isolated runs

Classes are produced in batches of 2–3, clustered by kit shape (pet classes
together, healer-carrying classes together, cooldown-stacking melee together)
so the per-archetype answers — pet section shape, target band, resource
envelope — amortize across neighbours.

**Cluster membership is decided at batch start, from data, not from lore:**
skim `resources/coa-<class>-skills.json` and the Sidekick spec pages for the
candidates, and let Phase 0 correct the guess. `resources/spec-roles.md` grows
one class at a time, observed in game; a class not yet in it has unknown roles,
and that unknown is an UNKNOWN in the requirements doc, not an assumption.

### The isolation rule — clustering never shares claims

The conflation risk of running similar classes together is real: an agent that
just built one pet class will pattern-match the next one. So the order is
clustered, but **every class runs as a sealed job**:

- one agent/session per class, fresh context, no memory of the neighbour
- its factual inputs are the shared notes (`weakauras-data-model.md`,
  `layout-standard.md`, the process docs) plus **its own** scrapes, inventory,
  citations and requirements doc — nothing else
- another class's abilities, requirements or citations files are *pattern*
  references at most, never sources for a claim. "The other pet class does X"
  is the "another pack does something like this" tripwire from the research
  gate, wearing a new hat.
- the gates enforce this mechanically: a skill name imported from a neighbour
  does not resolve in this class's inventory (`all tracked names resolved`
  fails the build), and a citation corpus is per-class (check 15).

What legitimately transfers between neighbours is *process* knowledge — "pet
presence alerts use the missing-engraving shape" — and that transfers by being
written into the shared notes, where every class reads it, not by agent
context.

Everything before ship is scriptable and has no cross-class dependency, so a
batch can run its classes concurrently to the `verify` gate. With the in-game
pass moved post-ship there is no serial human step left in the ship path; the
human's per-class job is reading the requirements doc and the buildlog gates
before `mksite` runs.

## The feedback loop — how drafts converge

Feedback is the mechanism that replaces iteration-toward-perfect. Per report:

1. **Intake** — a report names a class, spec, and what read wrong.
2. **Triage** — reproduce against the built pack and the requirements doc.
   Three shapes: a *defect* (pack disagrees with its own cited sources — fix
   and release), a *data change* (the game moved — changelog triage, then
   fix), or a *preference* (goes to §6, ships when enough reports agree).
3. **Release** — normal ship rules: bump `VERSION`, archive the outgoing
   all-specs file, update the delivery README, regenerate the site.
4. A feedback report that confirms a pack works in game **is** an acceptable
   `verified` close — record it with `verified.py record --note` naming the
   source.

Standing cadence, all shipped classes: `changelog_watch.py --pages 6` weekly.
It exits nonzero on news, so it works unattended; drift on a frozen class is
reopen trigger #1.

## What this note changes in the repo

- `phaselog.py`: `verify` phase no longer contains `in-game`/`recorded`; they
  are the post-ship `verified` phase.
- `mksite.py`: the unverified badge now reads **draft**, with tooltip copy
  saying feedback converges it.
- `--allow-unverified` stays a deliberate flag, not a default — shipping a
  draft is a choice made visibly, every time.
