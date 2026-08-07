---
title: Class pack requirements — the template that precedes any building
date: 2026-08-06
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, process, requirements]
sources:
  - "[[class-pack-process]]"
  - "[[layout-standard]]"
---

# Class requirements — fill this in BEFORE planning the implementation

Copy to `notes/requirements-<class>.md`, answer every section, and get it read
before a single band is written. Runemaster proved the cost of the other order:
the pack was built, then the questions arrived as bug reports, and each answer
was a release.

**Every factual claim here needs a source.** The research gate in
`class-pack-process.md` governs — `/web-research` first, and cite. An
unanswered section is a legitimate output; an *invented* answer is not. Mark
gaps `UNKNOWN — <what would settle it>` and they become the in-game checklist.

---

## −1. Changelog — run this FIRST, before any research

```bash
python3 tools/changelog_watch.py --class <slug> --pages 6
```

Every source below is a claim about a **date**. Ascension rebalances every
couple of weeks, and the changelog is the only thing that says whether a scrape
still counts. Record the newest entry date here; `citations.py` measures
staleness against it.

- [ ] changelog scanned, newest entry: `____-__-__`
- [ ] every `replaced with` / `now reads` / `now baseline` / `new spell` /
      `reworked` entry triaged into §2 or §0 below
- [ ] `--accept` **only after** the entries are acted on — accepting to clear
      the output deletes the record that work is outstanding

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| | | | |

---

## 0. Ability surface — both databases, not one

The inventory is not complete until **db.exil.es and db.ascension.gg have both
been asked about every ability.** They are two snapshots of the same
TrinityCore tables and they disagree, and the disagreement is the signal:

| Both have it | live ability |
|---|---|
| One has it, other has a different id | same ability, different row — confirm by reading BOTH tooltips |
| One has it, other has no record | **deprecated, cut, renamed, or never implemented** — do not ship it |

`tools/crosscheck.py` already does this for raid-utility rows via the
`?spell=<id>&power` endpoint (which answers even for ids whose HTML 404s, and
re-asks by NAME because the id is not the join key). It must be run across the
**whole class inventory**, not just utility.

A name hit is a *candidate*, never a match — three of five name hits on the
utility pass were different abilities wearing the same word. Read both
tooltips and write one line of reasoning per verdict.

- [ ] every inventory row cross-checked against both DBs
- [ ] `no-record` rows removed or explicitly justified in the Notes cell
- [ ] deprecated/unused/placeholder names filtered (`utility_tables.JUNK`)

---

## 1. Mandatory buffs — what must be tracked or the rotation is unreadable

List every buff/aura the player **has to see** to play correctly. Three sources,
all of them required:

**From the class kit** — stances, attunements, imbues, long-term self-buffs.
Ask: if this is missing or wrong, is the player quietly losing throughput?
Those earn a *missing-buff alert*, not just a tracker (cf. Runemaster's
`NO ENGRAVING` / `NO ETCHING`).

**From talents** — see §2. A talent buff that gates the rotation is mandatory
even though it does not exist on an untalented character.

**From abilities** — procs that say "press this now", and running cooldowns
whose only other cue is a swipe that reads as *unavailable* rather than
*active*.

| Buff | Source (class/talent/ability) | Why the rotation needs it | Where it renders |
|---|---|---|---|
| | | | |

---

## 2. Talent-driven rotation changes — the section Runemaster was built without

**A talent that materially changes the rotation is a WeakAura requirement, not
trivia.** Enumerate the talent tree and flag every entry that does any of:

- **replaces** an ability with a different spell id (Zenith → 712389 under
  Echoes of Eternity / Runelord). An exact-id trigger stops matching and the
  icon does not dim — it **vanishes from the row**. Record variant ids in
  `tools/in-game-verified.json` under `variants`.
- **transforms** an ability into other spells (Elemental Mastery → Ignis /
  Hydros / Lithos / Stratus). Track the **replacement's** id with a native
  `["Spell Known"]` trigger — this fork resolves no spell overrides.
- **adds a proc** that resets or empowers something → `PROC_GLOW`
- **adds or removes charges** → `CHARGES`
- **changes what the resource means**, or adds a segment/stack the bar must show
- **removes an ability from the bar entirely** when talented

| Talent | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| | | | | |

For each row, answer: **does the pack read correctly both with and without this
talent?** A pack that only works on one build is a pack that silently misleads
the other. Where a talent is build-defining, say which state the layout assumes.

---

## 3. Pets — are there any, and what do they need?

Historically the inventory binned every pet spell to `ignore` ("not a player
button"). That is **no longer sufficient**. Answer explicitly, even when the
answer is "none":

- [ ] Does this class summon a pet? Permanent, temporary, or cooldown-length?
- [ ] Does the pet have abilities the **player** presses or must react to?
- [ ] Does the pet apply buffs/debuffs that need tracking?
- [ ] Does pet presence/absence gate the rotation — i.e. does "no pet" deserve
      a missing-buff alert the way a missing weapon imbue does?
- [ ] Does the pet have a resource (energy/focus/happiness) worth a bar?

If any answer is yes, the pack needs a **pet section** — its own band or icons.
Notes:
- `["Spell Known"]` takes a `petspell` toggle (`usePet` →
  `IsSpellKnown(id, true)`), which is how you ask whether the *pet* knows a
  spell rather than the player.
- Pet auras need `unit = "pet"` on the aura trigger, not `"player"`.
- A pet cooldown is a real cooldown row entry, not an `ignore`.

| Pet | Summoned by | Duration | Abilities/buffs to track | Where it renders |
|---|---|---|---|---|
| | | | | |

---

## 4. Primary damage source and how the main bar reads

The main row is the thing the player actually looks at. Specify it per spec
before laying anything out.

Per spec:
- **Primary damage source** — the ability the throughput actually comes from
- **The read** — left-to-right, what the main row says. Press priority is the
  order; `controlledChildren` order is load-bearing and must encode it.
- **Row width** — icon count. `CD_PER_ROW` is derived from the **narrowest**
  main row in the pack (`28w - 2 <= 1.2 * narrowest`); never copied from
  another class.
- **Resource** — what drives the bar, and whether the spec needs a segmented
  bar under it (only where the spec is genuinely played around a segmented
  resource — a permanent bar for a system the spec ignores wastes prime space).

| Spec | Primary damage | Main row, in press order | Icons | Resource / segments |
|---|---|---|---|---|
| | | | | |

---

## 5. Miss-handling — "what happens if I miss an important skill?"

This is the section that decides whether the pack is a *display* or a *coach*.
For every ability that meaningfully hurts when missed, say which cue carries it
and what the failure mode is if that cue does not fire.

Escalation vocabulary already built into the engine:

| Cue | Says | Built by |
|---|---|---|
| desaturate on `spellUsable == 0` | "cannot press this — resource/form" | `cd_icon`, check 9 |
| cooldown swipe + GCD sweep | "not yet / do not clip" | `use_showgcd`, check 10 |
| timer appears at 20s | "coming back" | urgency tier 1 |
| glow at 10s, urgent glow + tint at 5s | "get ready / now" | tiers 2–3 |
| proc glow | "press this NOW" | `PROC_GLOW` |
| active-only buff row | "this is running" | `buff_group` |
| missing-buff alert | "you forgot something before the pull" | `RM Alerts` |

Then the harder half — **how do we know the cue itself did not silently fail?**
A WeakAura that never fires does not error. Every cue in the table below needs
a stated way to prove it fired:

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| | | | |

Acceptable proofs, strongest first: seen in game; caught by a `tests/run.py`
check (name it); a `/rmprobe`-style differ showing the underlying state change.
"It looks right in the builder" is not a proof — `effectiveSpellId` looked
right in the builder across two releases.

---

## 6. Open questions

Everything marked `UNKNOWN` above, collected. This is the in-game checklist for
the single import step, and the reason that step is one trip rather than four.

- [ ] …
