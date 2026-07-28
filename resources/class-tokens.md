---
title: CoA class -> WeakAuras load token map
date: 2026-07-28
type: reference
status: budding
tags: [weakauras, conquest-of-azeroth, reference, class-ids, load]
source: "/dump WeakAuras.class_types, in game, 2026-07-28"
---

# Class tokens for `load.use_class`

> **Confirmed working in game 2026-07-28.** With `use_class` set on every leaf
> the pack no longer loads on other classes at all. An earlier test suggested
> the condition was inert — that was a stale SavedVariables state on the
> client, not the condition. This is the primary gate for every class pack;
> see [[layout-standard]].

Read straight out of `WeakAuras.class_types` in game. **The token is not
derivable from the class name or the class id** — several CoA classes load
under an unrelated internal name (Runemaster is `SPIRITMAGE`, Venomancer is
`PROPHET`, Templar is `MONK`). Never guess one.

Load shape is single-select:

```lua
["load"] = {
    ["use_class"] = true,
    ["class"] = { ["single"] = "SPIRITMAGE", ["multi"] = {} },
},
```

## The 21 CoA classes

| ID | Class | Token |
|---|---|---|
| 12 | Barbarian | `BARBARIAN` |
| 13 | Witch Doctor | `WITCHDOCTOR` |
| 14 | Felsworn | `DEMONHUNTER` |
| 15 | Witch Hunter | `WITCHHUNTER` |
| 16 | Stormbringer | `STORMBRINGER` |
| 17 | Knight of Xoroth | `FLESHWARDEN` |
| 18 | Guardian | `GUARDIAN` |
| 19 | Templar | `MONK` |
| 20 | Bloodmage | `SONOFARUGAL` |
| 21 | Ranger | `RANGER` |
| 22 | **Chronomancer** | **`CHRONOMANCER`** |
| 23 | Necromancer | `NECROMANCER` |
| 24 | Pyromancer | `PYROMANCER` |
| 25 | Cultist | `CULTIST` |
| 26 | Starcaller | `STARCALLER` |
| 27 | Sun Cleric | `SUNCLERIC` |
| 28 | Tinker | `TINKER` |
| 29 | Venomancer | `PROPHET` |
| 30 | Reaper | `REAPER` |
| 31 | Primalist | `WILDWALKER` |
| 32 | Runemaster | `SPIRITMAGE` |

All 21 captured. Starcaller was one of the two entries `/dump` elided; a
filtered loop returned it as `STARCALLER`.

## Base classes also in the table

`WARRIOR` · `PALADIN` · `HUNTER` · `PRIEST` · `DEATHKNIGHT` · `SHAMAN` ·
`MAGE` · `WARLOCK` · `DRUID` · plus `HERO` ("Hero", not a base class)

`ROGUE` is absent from the visible output.

## The two skipped entries

The dump ended with `<skipped 2>`. Arithmetic:

```
30 visible + 2 skipped = 32 total
21 CoA + 10 base + HERO = 32
```

So the two skipped are almost certainly **Starcaller** and **`ROGUE`** — the
only two otherwise-expected entries not shown. Confirm with a filtered dump
before relying on it:

```
/run for k,v in pairs(WeakAuras.class_types) do if k=="ROGUE" or v:find("Starcaller") then print(k,v) end end
```

## Why this matters

Each class pack gates every leaf on its own token (see
[[layout-standard]]). The mapping is arbitrary, so every pack needs its token
looked up here rather than inferred. Chronomancer's is `CHRONOMANCER`, which
happens to be the obvious one — Runemaster's is not, and that is the warning.
