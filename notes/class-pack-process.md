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

## THE RESEARCH GATE — applies to every step below

**The moment you notice you are guessing, stop writing code and run
`/web-research`.** Exhaust the research avenue *first*. This is not advice for
hard problems only; it is the rule, and the trigger is the feeling of
uncertainty, not the size of the task.

This section exists because ignoring it cost **four shipped releases** on one
cue (Runemaster 1.3–1.6, Elemental Mastery). Each one shipped a different
*guess* at how the client surfaces a spell transform — a proc aura, then the
spellbook, then the action bar, then a spell override — and each was written
before anyone had read the source that answers it. The answer was one line in a
public repo the whole time:

```lua
-- Ascension-Addons/WeakAuras-Ascension, Prototypes.lua:3806
local effectiveSpellId = spellname
```

This fork does no spell-override resolution. Two releases were built on a
condition that could never be true, and both failed *silently*, which is the
only failure mode that matters here — a wrong guess in a WeakAura does not
error, it just never fires, and it costs a full in-game test round-trip to
learn nothing.

### Tripwires — say any of these out loud and you are already guessing

- "it's probably implemented as…" / "Ascension usually…"
- "let me cover all the plausible surfaces" — shotgunning is guessing wearing a
  hat, and it makes the eventual failure *uninterpretable*
- "the docs say X" when the docs describe **upstream** and this is a **fork**
- "another pack does something like this" — *like* is not *the same as*
- reaching for custom Lua before checking whether a native prototype exists
- any claim about a rotation, priority, or proc that did not come from a cited
  source

### Check the CHANGELOG before you trust any class research

**Every scrape is a photograph of a moving target.** Ascension rebalances every
couple of weeks, so a Sidekick page, a database row and a rotation guide are all
claims about *a date*, and the changelog is the only thing that says whether
that date still counts.

```bash
python3 tools/changelog_watch.py --class <slug> --pages 6
```

Run it **at the start of Phase 0, before the research**, and again before
shipping. It exits nonzero when something is new, so it works unattended.

This is not hypothetical. The watcher exists because Runemaster shipped 1.0 on
2026-07-28 and the changelog dated 2026-07-31 changed eight of its abilities —
three days, and nothing noticed. It happened again on Pyromancer: Phase 0
research scraped Sidekick, which says the Phoenix lasts **1 minute**, while

    [pyromancer] Phoenix Egg is now permanent, up from 1 minute,
                 but has a cast time to resummon.

had been live since 2026-07-31. The requirements doc was written around an
expiry timer that no longer exists.

`citations.py` already measures this — `newest_changelog()` marks a class's
rotation citations STALE when the devs patched it after the citation date. Read
that warning; it is the same signal.

What to look for, in priority order:

| Changelog shape | Why it matters |
|---|---|
| *"X replaced with Y"* / *"X now reads:"* | a §2 talent change — the ability the pack draws may not exist |
| *"is now baseline"* | it stopped being a talent; gating assumptions change |
| *"new spell … available from the class trainer"* | an ability **no scrape has ever heard of** |
| *"reworked"* | the rotation claim built on it is void |
| *"now permanent"* / duration and charge changes | trackers built on the old duration are wrong |
| number tweaks | usually safe to ignore for a WA |

⚠️ **Do not `--accept` until the entries have actually been acted on.** Accept
marks them seen; accepting to clear the output is deleting the only record that
work is outstanding.

### Source precedence — highest wins, always

| Rank | Source | Note |
|---|---|---|
| 1 | **The client's own behaviour** — `/rmprobe`, `/rmdump`, a fresh in-game export | The only authority. `internalVersion` proves the shipped client is ahead of the public fork repo. |
| 2 | **The fork's source** — `Ascension-Addons/WeakAuras-Ascension` | `Prototypes.lua` for triggers, `Types_ClassicPlus.lua` for Ascension additions. Grep it; do not infer it. |
| 3 | `notes/weakauras-data-model.md` | Written *from* rank 2, so it can drift. It carries the `effectiveSpellId` correction now. |
| 4 | Upstream WeakAuras docs / GitHub | **Different addon.** Useful for concepts, wrong on specifics. The wiki documents a far newer WA than this 3.3.5 backport. |
| 5 | `resources/import-strings/*.txt` | Proves a shape *can* work; never proves one is *required* or correct. |

Retail precedent is rank 4, and porting it needs an explicit API check. Tracking
a transformed button via `FindSpellOverrideByID` (Condemn/Execute, Lava
Beam/Chain Lightning) is standard in retail and **impossible here** — that API
is Cataclysm-era and this is a 3.3.5 client.

### This is not a WeakAuras rule

It applies just as hard to **class content**: rotations, ability priorities,
what a talent actually does, which spec uses what. A priority order invented
from ability tooltips is a guess, and it ships as confident nonsense that a
player follows into a raid. Cite it — `resources/citations-*.json` and
`resources/rankings-*.json` exist for exactly this, and `tests/run.py` check 15
enforces a citation corpus. If `/web-research` cannot find a source, the
honest output is "uncited", not an invented ordering.

### The one legitimate reason to ship without an answer

When research genuinely bottoms out — the mechanism is server-side and
undocumented — **build the instrument, not another guess.** `tools/build_probe.py`
(`/rmprobe`) is the worked example: it takes a baseline and reports only what
*changed*, so one proc produces a handful of lines. A snapshot tool
(`/rmdump`) answers "what does the world look like"; a differ answers "what did
that do", which is the question you actually have. One round-trip with a differ
beats four releases of guessing.

## THE BUILD LOG — every step recorded, every phase gated

```bash
python3 tools/phaselog.py <class>                       # status + metrics
python3 tools/phaselog.py <class> --step <id> --note "…"  # record a step
python3 tools/phaselog.py <class> --gate <phase>          # close a phase
```

**A rule in a document is not a gate.** "Check the changelog first" was written
in three places and skipped anyway, and the Pyromancer requirements were
written around a Phoenix duration that had not existed for a week. Nothing had
*measured* whether the step ran.

So every step below is recorded in `resources/buildlog-<class>.json`, and a
phase does not close until `--gate` passes. It exits nonzero when it does not.

The gate is deliberately **two independent tests**:

1. the **log** says a human ran each step, and
2. the **repo is re-measured** — inventory counts, unreviewed markers, citation
   presence, changelog drift, test state — so a step can be recorded and still
   fail. That is the entire point: a recorded step is a *claim*, and the gate
   checks the repo against it rather than trusting it.

Metrics recorded at each seal: inventory rows, unreviewed rows,
cross-database coverage %, citations and claims, mechanics sources per spec,
open UNKNOWNs.

⚠️ **Never `--accept` the changelog to clear a gate.** Accepting marks entries
seen; accepting to silence a red gate deletes the only record that work is
outstanding. Same for recording a step you did not run — the metrics will
disagree and the gate will say so, but the log will be a lie either way.

⚠️ **Scan depth is part of correctness.** The gate runs the watcher at
`--pages 6`. At `--pages 3` it reported "clear" for drift that was simply off
the end of the scan — a **false pass**, which is the one outcome a gate must
never produce.

## PHASE 0 — REQUIREMENTS, before any implementation plan

**Specify the class, then plan it. Not the other way round.** Copy
`notes/class-requirements-template.md` to `notes/requirements-<class>.md` and
answer it in full before a band is written.

Runemaster was built in the other order, and every question the template asks
arrived later as a bug report — each one costing a release. The template is
that list of questions, asked up front:

| § | Question |
|---|---|
| — | **Is the CHANGELOG clear for this class?** `changelog_watch.py` first, or every answer below is dated |
| 0 | Is every ability confirmed against **both** databases, with deprecations cut? |
| 1 | Which buffs are **mandatory** to see — from the class, from talents, from abilities? |
| 2 | Which **talents** change the rotation, and does the pack read right with *and* without each? |
| 3 | Are there **pets**? Do they have abilities, buffs, or a resource to track? |
| 4 | What is the **primary damage source** per spec, and how does the main row read? |
| 5 | **What happens if I miss an important skill** — which cue catches it, and how do we prove that cue fires? |

An unanswered section is a legitimate output; an invented answer is not. Mark
gaps `UNKNOWN — <what would settle it>`; they become the checklist for the
single in-game trip in §5.

Three of these are new obligations that the shipped classes do not yet satisfy,
so they are called out where the steps below would otherwise skip them:

- **Both databases** (§0) — `tools/crosscheck.py` currently runs only over
  raid-utility rows. A spell that only ONE database has ever heard of is the
  shape a cut, renamed or never-implemented ability takes, and shipping it puts
  a dead button on someone's screen. Run it over the whole inventory. See §3.
- **Talents** (§2) — a talent that replaces, transforms, recharges or removes
  an ability is a **WeakAura requirement**. Runemaster shipped four releases of
  Elemental Mastery and a vanishing Zenith because this was never specified.
- **Pets** (§3) — `mkabilities.py` bins pet spells to `ignore`, "not a player
  button at all". That is a *default*, not a verdict. If the pet has abilities
  the player reacts to, buffs worth tracking, or a resource, the pack owes it a
  section.

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
| `notes/class-requirements-template.md` | **Phase 0** — copy per class and answer before planning |
| `notes/requirements-<class>.md` | this class's answers, once written |

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

**Sidekick is a REFERENCE, not ground truth.** It is one community build site,
it lags the server, and the recency test decides whether it counts at all:
**if its snapshot is older than the newest `changelog_watch.py` entry, it is not
a source of truth for anything that entry touched.** Compare the citation's
`retrieved_at` against the changelog before letting a Sidekick claim settle
anything — and `retrieved_at` is the *snapshot's* date, not the date the import
ran. `citations.py` stamped today's date until 2026/08/07, which reported the
corpus fresher than it was (blob 08/02, citations claiming 08/06); it now reads
the mtime of `resources/sidekick-data.js`. Never move a citation's date forward
by re-importing off an old blob — re-scrape (`sidekick_skills.py --all`) first,
or the date says "fresh" over the same stale claims.

**A name that appears ONCE in `sidekick-data.js` is prose, not a claim.** The
rotation blurbs are generated ("Line up X, Y, Z with your burst window") and
they name abilities Sidekick's own skill data has no record of. Every claim that
resolves to an inventory row appears 3-10 times in the blob, because it is in the
skill data too. `grep -c "<name>" resources/sidekick-data.js` is the whole check.
Worked example: Pyromancer's `Comet Storm`, `Firewall` and `Draconic Assault`
were all 1-hit, and all three turned out to be a component, a deprecated id and
an ability db.ascension.gg has never heard of.

**Known trap:** db.exil.es sometimes links a proc rather than the castable
ability. Cross-check against db.ascension.gg's `advType: "Ability"` entries, and
treat "this ability has no cooldown row" as a smell that the id is wrong.

### Both databases, over the whole inventory — MANDATORY

One database is a draft. `tools/crosscheck.py` asks the second one
(`db.ascension.gg`, via `?spell=<id>&power`, which answers even where the HTML
404s) and it must run over **every ability in the class inventory**, not just
the raid-utility rows it was originally written for.

| Verdict | Meaning | Action |
|---|---|---|
| `record` | both DBs, same id and name | ship it |
| `other-id` | both have the ability under different ids | ship it — after reading **both** tooltips |
| `no-record` | one DB has never heard of it | **stop and resolve it.** Deprecated, cut, renamed, never implemented — *or* the second database is simply incomplete |

⚠️ **`no-record` is a STOP, not a delete-list.** Source precedence still holds:
the client outranks a database. Runemaster's sweep returned three, and all
three resolve correctly *without* removing anything — `Etch` and `Wild Steam`
are both marked "verified in game" in the inventory, so an in-game tooltip
beats db.ascension.gg's silence, and `Manastorm`'s own db.exil.es description
is literally "Deprecated", so it was already `ignore`. Resolve each one; do not
bulk-delete on the verdict.

**The id is not the join key.** Asking only by id overstates absence by a third
— `Distracto Shot` is 560470 on one and 561269 on the other, same ability. Every
empty id is re-asked BY NAME.

**A name hit is a candidate, not a match.** Three of five name hits on the
utility pass were different abilities sharing a word — one class's `Siphon`
steals buffs, another's summons skeletons. Read both tooltips, write one line of
reasoning per verdict, and record it in the row's Notes cell.

Also filter the obvious dead: `deprecated|unused|placeholder|test|delayer|
trigger` (`utility_tables.JUNK`) and the `DEPRECATED` / `unused` name markers
`audit_cds.py` already drops.

## 3. Categorise abilities

Roles live in `resources/abilities-<slug>.md`, one reviewed row per ability —
NOT in curated lists in the builder. `tools/mkabilities.py <slug>` seeds the
table from the scrapes and marks every unreviewed row `seed:`; the build
**refuses to run** while any `seed:` marker survives, because a row nobody has
read is not a decision. Roles are `main`, `resource`, `longterm`, `buff`,
`target`, `offensive`, `defensive`, `utility`, `ignore`, with `spec:role` for a
per-spec override. Anything not categorised falls into Utility, so nothing
silently disappears.

### `ignore` is a default for pet spells, not a verdict

The role list above sends pet spells to `ignore` — "not a player button at
all" — and that was written when no class in the pack had a pet worth drawing.
**Requirements §3 overrides it per class.** If the pet has abilities the player
presses or reacts to, buffs worth tracking, or a resource, those rows are not
`ignore`; they are real entries that need a pet section.

The engine already has the pieces:

| Need | Mechanism |
|---|---|
| does the *pet* know a spell | `["Spell Known"]` with the `petspell` toggle → `IsSpellKnown(id, true)` |
| a buff on the pet | aura trigger with `unit = "pet"`, not `"player"` |
| pet ability cooldown | an ordinary `cd_icon` row entry |
| pet missing entirely | the same shape as the missing-engraving alert |

Chronomancer's five "Chronobuff" abilities are the counter-example worth
keeping: they carry cooldowns and look like buttons in every scrape, but their
tooltips give them away as the PET's spellbook ("Shroud your MASTER"). `ignore`
is right *there* because the player never presses them. Decide it per ability,
from the tooltip — never from the fact that the word "pet" appears.

What still lives in the builder, because it has no table:

- `PROC_GLOW` — proc → the ability it tells you to press
- `PROC_STACKS` — of those, the ones whose proc also stacks
- `CHARGES` — abilities with charges
- `SPEC_KNOWN` — one spell unique to each spec, for `load.use_spellknown`
- `NO_BUFF` — offense names that apply no buff, so they earn no buff-row icon
- `OVERRIDE` / `FALLBACK` — art, only where a human has stated intent

Runemaster predates the table and still hand-curates `OFFENSIVE` /
`OFFENSIVE_TAIL` / `DEFENSIVE` behind `roles_from_inventory=False`. Do not copy
that shape into a new class.

**Provenance, per class.** Runemaster's and Chronomancer's roles were assigned
by a human reading each row. **Pyromancer's were proposed by an automated pass
and cleared in bulk on 2026-08-02** at the user's instruction — the reasoning
for every row is still in its Notes cell, so a wrong call is findable, but no
human read them one at a time. The rows most likely to be wrong are the ones
whose Notes hedge ("reads like", "could read", "no other tooltip names it"):
`Melt`, `Emberheart`, `Dancing Flames`, `Draconic Tempest`, `Dragon Leap`,
`Stoke`, `Supernova`, `Flame Swell`, `Conjure Campfire`, `Soar`. Check those
against the game before trusting the first Pyromancer build.

The `prop:` / `prop?:` markers exist for this: an automated pass writes them,
they block the build exactly as `seed:` does, and clearing one is a human
saying "I read this". Clearing them in bulk skips that, which is a choice
available to whoever owns the class and not a default.

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

## 5. In-game verification — post-ship, not a ship gate

**Since the production run (`production-run.md`), the in-game pass no longer
blocks shipping.** A class ships as a DRAFT once phaselog's `research`, `build`
and `verify` phases seal, via `mksite.py --allow-unverified`, which badges the
pack visibly. The `verified` phase closes afterwards — a batch in-game sweep or
a credible community confirmation, whichever arrives first.

When the pass happens: screenshot per spec. Expect to be wrong about **names** —
that is the one class of error no amount of scraping settles. Any tooltip that
comes back goes into `resources/in-game-verified.json` and wins over everything.

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

**Operating policy for the remaining 18 classes lives in
[[production-run]]** — the draft bar, the freeze on shipped classes, archetype
batching, and the isolation rule (clustered order, sealed per-class runs, no
cross-class claims). This section describes the mechanics it builds on.

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

What is genuinely per-class: `tools/wapack.py` holds everything else.

**Settled after Chronomancer:** `build_<class>.py` is class CONTENT over a
shared engine. See "The engine" below.

**Healing specs — settled on Chronomancer's Time, and it holds.** Raid-frame
health and multi-target HoT state are scoped OUT: VuhDo/Grid own that job on
3.3.5a. What a pack carries is the **target band** — your own HoTs and absorbs
on whoever you are targeting right now, glowing when one needs a refresh
(`dot_bars(helpful=True, refresh_at=...)`) — and a main row that is a healing
rotation. Nothing wider.

Which specs heal is in `resources/spec-roles.md`, read off the game and parsed
by `classes.py` (`cls.spec_role(spec)`, `cls.healers`). `mkabilities.py` prints
it at the top of the inventory, because a role review needs it in front of it.

**It is not derivable, and the one place it looks derivable is wrong.**
db.exil.es files Pyromancer's *healing* spec, Flameweaving, under the tree slug
`pyromancer-destruction`. Tree slugs are filing, like `spell.line` and Sidekick
mention counts — never role, never membership.

## Non-negotiables

- **Requirements before implementation.** `notes/requirements-<class>.md` from
  the template, answered, before a band is written. See *Phase 0*.
- **Changelog before research, and again before shipping.**
  `python3 tools/changelog_watch.py --class <slug>`. A scrape is a photograph of
  a moving target; the changelog is what says whether the photo still counts.
- **Guessing is a stop condition.** Run `/web-research` and exhaust it before
  writing code — see *The research gate* at the top. Applies to class content
  (priorities, procs, talents) exactly as much as to addon behaviour.
- **Two databases, or the ability does not ship.** A `no-record` on either
  db.exil.es or db.ascension.gg is how a cut or renamed ability looks.
- **Talents that replace, transform or recharge an ability are requirements**,
  not trivia — and the pack must read correctly with *and* without each.
- **Pets get answered explicitly**, even when the answer is "none".
- **Grep the fork's source before believing any trigger behaviour.**
  `notes/` is written *from* that source and can drift; upstream docs describe a
  different addon.
- Gate at the **leaf** with `load.use_spellknown`. Group triggers are inert.
- Dynamic groups use `grow: "HORIZONTAL"`. Never `"RIGHT"`.
- Set `disjunctive: "any"` on any multi-trigger display that means "any of these".
- Texture path goes in `displayIcon`; `icon` is a boolean.
- Resource bar width is derived from the main row's icon count.
- Change one mechanism at a time so a failure is unambiguous.

## The engine

`tools/wapack.py` is the class-agnostic half. **Do not fork a builder.** An AST
comparison of the two standalone builders found 16 top-level functions
byte-identical once comments were stripped, three more above 90%, and the
remaining nine differing by exactly three things: the id prefix, the class
content inside `longterm_band`, and four places where Chronomancer had been
improved and Runemaster never caught up. That third category is the cost of
copying — the anchored ladder is the worked example, fixed in Chronomancer from
the day its bands were written and ported to Runemaster two releases late.

A new builder is content over the engine:

```python
import wapack as W
VERSION = "1.0"
OVERRIDE = {...}; FALLBACK = {...}; CROSSCHECK = {...}
CLS = W.init("<slug>", version=VERSION, prefix="XX", cd_per_row=<n>,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)
from wapack import *          # after init() — it is what gives these values
...                           # CHARGES / PROC_GLOW / SPEC_KNOWN, then bands
W.configure(charges=CHARGES, proc_glow=PROC_GLOW, ...)
```

`build_chronomancer.py` is the reference. It passes **no** convergence flags,
which is what a new class should look like. `build_runemaster.py` passes five
(`roles_from_inventory`, `trust_spell_meta`, `override_first`, `balanced_rows`,
`icons`); those are a TODO list holding it on pre-convergence behaviour, one
release each. Never add a sixth for a new class — fix the new class instead.

`CD_PER_ROW` is per-class and must be recomputed, never copied: it comes from
the NARROWEST main row in the pack, since every resource bar is width-locked to
its own spec's row. `28w - 2 <= 1.2 * narrowest`, confirmed by
`tools/rowwidths.py` against the built packs.

The gate for any engine change is `tests/run.py` check 1 — every class rebuilds
to its frozen fixture. The extraction itself landed with all 8 packs
**byte**-identical, not merely structurally equal.

First thing to check in any new class, before anything else: the `data()` /
`dest()` split. `data()` falls back to `tools/` when a file is missing from
`resources/`, which is exactly the case for a class being scraped for the first
time — always WRITE through `dest()`. `audit_cds.py` sat broken for weeks on
that shape of bug and nothing failed loudly.

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
- **This fork resolves no spell overrides.** `effectiveSpellId` is the id you
  typed (`Prototypes.lua:3806`), `use_ignoreoverride` does not exist, and
  `FindSpellOverrideByID` is not a 3.3.5 API. To track "this button became
  another spell", put a native `["Spell Known"]` trigger on the REPLACEMENT's
  id — a 3.3.5 server changes a button by granting the new spell and taking the
  base away. That prototype takes a **number**; a string id silently becomes
  spell 0 (`Prototypes.lua:8271`).
- Custom triggers come in exactly two shapes on this fork:
  `custom_type = "event"` + `events`, or `custom_type = "status"` +
  `check = "update"`. A `status` trigger carrying `events` matches neither and
  never runs.

**Layout** — `notes/layout-standard.md` is the contract, but verify against the
generated guide, never against the constants in the builder. Runemaster shipped
with `CD_PER_ROW` and `Y_CDS` defined and never referenced, so the documented
wrap-at-12 did not exist and Engravement's utility row shipped 586px wide
against a 274px main row. **Before shipping, measure every always-visible row's
width** (`n * size + (n-1) * space`) against the resource bar; anything past
~1.2x needs a wrap or a cut.

**Delivery** — flat `archive/v<NN>-<class>-coa.txt`, bump `VERSION`, update the
delivery README's "Current version" line and *What's new*.
