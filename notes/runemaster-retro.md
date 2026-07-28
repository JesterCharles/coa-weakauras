---
title: Runemaster retro — what cost us, what worked
date: 2026-07-28
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, runemaster, retrospective, process]
sources:
  - "[[weakauras-data-model]]"
  - "[[layout-standard]]"
  - "[[../resources/verified-in-game-ids]]"
---

# Runemaster retro

Shipped: 4 packs (all-specs + one per spec), a layout standard, a diagnostic
aura, and a generated layout guide. It took **~29 build iterations** and far too
many in-game import cycles. Almost all of that was avoidable, and the causes
cluster into one theme.

## The single root cause

**I inferred WeakAuras' behaviour from four sample files instead of reading the
source, and I defended my inferences against the user's in-game evidence.**

Every expensive bug below is a variant of that. The turning point was spawning a
research agent to read the WeakAuras source — it found in one pass what a dozen
screenshot round-trips had not. That should have been step 2, not step 20.

## Bugs ranked by what they cost

| # | Bug | Cost | Why it happened |
|---|---|---|---|
| 1 | **uid dedup** — uids were `sha256(name)`, identical every build, so WeakAuras treated every re-import as already-installed and silently kept the old copy | ~10 iterations of "nothing changed" | Never questioned why fixes had no effect; kept fixing the *content* instead of asking why nothing landed |
| 2 | **Group triggers are inert** — gated specs on the parent group. WA skips load-scanning for anything with `controlledChildren`, so all three spec groups rendered **stacked at identical coordinates** | ~6 iterations; the "overlapping duplication" | Never checked whether *any* working pack gates on a group. None of 31 did |
| 3 | **`grow: "RIGHT"`** left-aligns rows at the anchor instead of centring them | ~5 iterations of "disjointed" | Assumed "RIGHT" meant "lay out horizontally". My own HTML preview centred with flexbox and *hid* the bug |
| 4 | **`disjunctive` defaults to `"all"`** — the engraving icons had 5 triggers and required all 5 simultaneously | engravings invisible for ~8 iterations | Never set the field; never noticed working packs set `"any"` on all 34 of their multi-trigger auras |
| 5 | **`icon` vs `displayIcon`** — `icon` is a BOOLEAN; the texture path belongs in `displayIcon`. Art fell back to trigger resolution | 3 iterations, and a false "0 mismatches" result | My validation checked a field the game never reads |
| 6 | **Scraped ids were wrong** — db.exil.es links the *proc* for some abilities (Convergence 560241, Primordial Fury 801095, Fists of Power 92153) and had two engraving ids plainly wrong | 4 iterations | Told the user "there is no cooldown" based on a scrape, when their tooltip said 1.5 min. Trusted the scrape over the game |
| 7 | **`CoA Aura - <Class> - <Spec>`** (887088/9/90) are database entries, **not** player buffs. Gating on them hid 119 of 141 displays | 2 iterations | Elegant-looking inference, never verified |
| 8 | **`Interface\Buttons\WHITE8X8`** is not reliably present; the glyph segments drew nothing | 2 iterations | Guessed a texture path |
| 9 | **`check: "event"`** on a custom status trigger never re-evaluates after an import, so gated groups stayed hidden | 1 iteration | — |
| 10 | **`showOnCooldown` + desaturate condition** on every cooldown icon collapsed the row to cooldown-only: nothing out of combat | 1 iteration | Added two mechanisms at once, so the failure was ambiguous |

## What worked

- **Reverse-engineering the `!WA:2!` format** and round-trip validating it
  against four community auras before writing anything. Solid from the start.
- **db.exil.es as the id source** — 689 name→id pairs plus per-spell cooldowns.
  Correct in the large majority of cases, and the only source with cooldowns.
- **Generating cooldown rows from an audit** rather than hand-written lists.
  Hand lists silently missed Convergence, Primordial Fury and 34 others.
- **Build-time checks.** Each was added after a bug escaped, and each then
  caught a *later* one — the duplicate-art check caught a duplicate display id
  that WeakAuras would have rejected outright on import.
- **The research sub-agent.** Highest-leverage single action in the whole task.
- **The generated guide/preview.** Good for layout and for sharing, but see the
  caveat: it centres with CSS, so it cannot catch WeakAuras' own layout bugs.
- **Version-salted uids and per-spec packs** — both came out of bug #1.

## Rules taken forward

1. **A tooltip beats every scrape.** In-game screenshots are ground truth; they
   go in `resources/in-game-verified.json`, which feeds id *and* icon.
2. **Before inventing a mechanism, check whether a working pack uses it.** Three
   decoded community packs sit in `resources/import-strings/`. If none of them
   does the thing, that is a strong signal it does not work.
3. **Change one mechanism at a time.** Bugs #2/#4 and #5/#6 were each masked by
   the other because two things changed together.
4. **When a fix has no visible effect, suspect the delivery, not the content.**
   Ten iterations were spent editing a pack the client was discarding.
5. **A passing check is only as good as the field it reads.** Validate against
   what the game consumes.
