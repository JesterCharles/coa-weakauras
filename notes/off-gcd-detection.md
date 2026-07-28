---
title: "Detecting off-GCD abilities"
date: 2026-07-28
type: reference
status: seedling
tags: [wow, ascension, conquest-of-azeroth, weakauras, gcd, tooling]
sources:
  - "https://wowdev.wiki/DB/Spell — Spell.dbc field layout, fields 206/207"
  - "https://db.exil.es/spell/<id> — rendered spell pages, the GCD row"
  - "WeakAuras2 5.21.2 — GenericTrigger.lua:2772-2806, Prototypes.lua:5560-5730"
---

# Detecting off-GCD abilities

## Why this exists

`use_showgcd` on a `Cooldown Progress (Spell)` trigger makes an icon sweep for
the global cooldown, so a ready ability reads as "not yet" for the ~1s after a
cast. That is the cue for holding a press rather than clipping it, and it is on
by default in `wabuild.spell_cd_trigger`.

**WeakAuras applies it blindly.** `GenericTrigger.lua:2795`:

```lua
if (showgcd) then
  if ((gcdStart or 0) + (gcdDuration or 0) > startTime + duration) then
    if startTime == 0 then gcdCooldown = true end
    startTime = gcdStart;
    duration  = gcdDuration;
    modRate   = gcdModrate
  end
end
```

There is no check that the spell obeys a global. `CheckGCD` polls a single
reference spell (29515 on 3.3.5a, 61304 elsewhere) and every trigger with the
flag borrows that timer. So on an ability that is **not** on the global, the
icon sweeps every time you press something else — a cooldown that is not real,
on an ability you could have used the whole time.

The addon cannot fix this: it holds no per-spell GCD data. The builder has to
be told. Shipped broken in `final14`, fixed in `final15`.

## Ground truth

`Spell.dbc` (3.3.5a):

| Field | Name | Meaning |
|-------|------|---------|
| 206 | `StartRecoveryCategory` | `133` = affected by the global cooldown, `0` = not |
| 207 | `StartRecoveryTime` | the global in ms — `1500` on retail Wrath, `0` when off-GCD |

## How we read it

We do not parse DBC. **db.exil.es renders a `GCD` row on the spell page when
the ability is on the global, and omits the row entirely when it is not.**

```
| Cooldown | 12 sec cooldown |
| GCD      | 1.0 sec         |     <- Runic Brand, on the global
```

```
| Cooldown | 45 sec cooldown |
                                   <- Zenith, no GCD row at all: off-GCD
```

`tools/audit_cds.py` turns that absence into `gcd: false` in
`resources/cooldown-abilities.json`, and `build_runemaster.py` derives:

```python
OFF_GCD = {n for n, v in COOLDOWNS.items() if v.get("gcd") is False}
```

**Absence of evidence vs evidence of absence.** A page that failed to render
also has no GCD row. `audit_cds.py` therefore requires a `Spell ID` row — proof
the scrape actually landed — before recording `false`. A scrape that did not
settle records nothing and is reported as unresolved, so a network blip can
never silently mark an ability off-GCD.

## The numbers, Runemaster

26 of 59 cooldown abilities are off the global — 44%. Far too many to have kept
by hand, and it would not have scaled to 21 classes.

The global on this server is **1.0s base**, not the 1.5s of retail Wrath, and
it is not uniform: `Warpdagger` is 0.5s, `Elder Magi Rune` is 1.5s. Any
heuristic keyed on a fixed GCD length is wrong here by construction.

## Related: separating GCD from a real cooldown in a condition

Use **`onCooldown`**. Its `conditionTest` (`Prototypes.lua:5700`) is

```lua
state.paused or (not state.gcdCooldown and state.expirationTime and
                 state.expirationTime > GetTime())
```

so the prototype already excludes the global, using the same `gcdCooldown` flag
the snippet above sets. This is exact and replaced a `duration > 3` floor that
cost the escalation cues on every ability with a sub-3s cooldown.

**`gcdCooldown` itself is not usable in a condition.** It is declared
`store = true` with no `conditionType` / `conditionTest`, so WeakAuras drops the
sub-check and an `AND` collapses back to whatever else was in it — silently, no
error. That shipped as `final12`.

This is *not* because it is `hidden`. Both `onCooldown` and `spellUsable` are
`hidden = true` and both work fine as conditions. **`conditionType` is what
makes a variable usable**; `hidden` only keeps it out of the display-text
picker. The earlier note in `layout-standard.md` gave the wrong reason.

## Doing this for the next class

1. Point `audit_cds.py` at the class (it reads `exiles-<class>.json`,
   `coa-<class>-skills.json` and the Sidekick pages).
2. Run it with Firecrawl up. Expect ~7 minutes for ~340 candidate abilities at
   8 workers; pages cache to `tools/spellchk/` so reruns are free.
3. Check the `unresolved` list is empty. Rerun if not.
4. `OFF_GCD` then derives itself. `tests/run.py` check 10 enforces both
   directions — no off-GCD ability showing the global, no on-GCD ability
   missing it.
