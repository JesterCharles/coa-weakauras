---
title: Pass 2 — site solidification and the road to the in-browser editor
date: 2026-08-08
type: plan
status: active
tags: [weakauras, conquest-of-azeroth, site, editor, plan, adr]
sources:
  - "[[production-run]]"
---

# Pass 2 — orchestration plan

The production run put all 21 classes on the site as drafts. This pass runs
specialized agents over the SITE itself, in service of the true goal: an
**in-browser editor** where a player customizes their class's pack — with
access to their class & specialization skills, talents and abilities — starting
from these templates.

## Decisions (owner-confirmed 2026-08-08)

| Decision | Answer |
|---|---|
| Editor scope this round | Direction (ADRs + plans) **plus one thin prototype**: decode a pack string in the browser, edit one property, re-encode a valid import |
| Hosting | **Pure static / client-side.** GitHub Pages stays the whole deploy. JS codec, class data shipped as JSON. ADRs design inside this constraint |
| The `emberfall` gate | Stays until these passes are done |
| Preview animations | Research + recommend only; implement later only where cheap CSS covers it |

## Rules binding every agent in this pass

1. **Web scraping goes through `/web-research` ONLY** — no raw fetches of
   external sites. The second brain (`~/second-brain`) is readable freely.
2. **Never guess.** Every claim in an ADR is backed by research output,
   repo documentation, second-brain content, or a cited example (a decoded
   pack, a tool's source, a fork source file). The research gate from
   `class-pack-process.md` applies to UI/architecture work exactly as it
   applied to class content.
3. **Every agent produces two files:**
   - `notes/adr/ADR-NNN-<slug>.md` — context, decision, alternatives
     considered (with the evidence for each), consequences.
   - `notes/plans/<slug>-plan.md` — the concrete, ordered work the ADR
     implies, each item with its acceptance signal.
4. Agents work in isolated worktrees; the orchestrator merges. Site files
   (`tools/mksite.py`, `docs/assets/*`) are read-only to research agents —
   fixes land through the plan files, not ad-hoc edits, except the icon
   pass which owns its data files.

## The agents

| # | Agent | ADR | Scope |
|---|---|---|---|
| A | Site layout & readability | ADR-001 | Audit all page types (index, class page, raid-utility) for hierarchy, typography, mobile behavior; research comparable community sites; concrete layout fixes ranked by impact |
| B | HUD visualization & icons | ADR-002 | Sweep all 21 previews for missing/placeholder art (the builders' `no art upstream` lists are the seed); fix resolvable icons in the data; research WA's in-game visual vocabulary (sweep, glow, tint) and recommend which preview animations carry meaning worth the cost |
| C | Editor architecture | ADR-003 | The client-side story: decode/edit/re-encode of this fork's WA import strings in JS (`wacodec.py` + `notes/wa-import-string-format.md` are the references), data model for templates, how class/spec/talent data ships as static JSON, size/perf budgets |
| D | Editor UX & interactions | ADR-004 | Research existing in-browser editors and talent calculators; interaction model for template → customize (skills/talents/abilities pickers per class & spec); readability/visibility principles that both the current site and the editor share |
| E | Prototype (after C) | — | Thin proof: browser page that decodes a real pack string, edits one property, re-encodes an import WeakAuras accepts |

## Sequencing

A, B, C, D run in parallel. E runs after C's ADR lands (it implements C's
riskiest assumption). The orchestrator merges each agent's branch, then runs
an apply pass over A's and B's ranked fixes.

## Acceptance for this pass

- ADR-001..004 + plan files merged, every claim sourced.
- Icon sweep: every "no art upstream" name either resolved to real art or
  documented as genuinely artless with the evidence.
- Prototype proves decode → edit → re-encode round-trip on at least one
  shipped pack.
- Site regenerated + tests green after applied fixes.
