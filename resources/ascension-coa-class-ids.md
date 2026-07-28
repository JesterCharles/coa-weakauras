---
title: Ascension CoA class IDs, spec lists, and useful db.ascension.gg endpoints
date: 2026-07-27
type: reference
status: budding
tags: [wow, ascension, conquest-of-azeroth, reference, class-ids]
source_url: https://db.ascension.gg/?classes
---

# Ascension Conquest of Azeroth — class IDs and specs

21 CoA classes occupy IDs **12–32**. They are **not** in alphabetical order, so do not
infer an ID from a name. Base WoW classes keep 1–11 (10 is unused).

| ID | Class | Specs (icon slugs, live names) |
|---|---|---|
| 12 | Barbarian | brutality, headhunting, ancestry |
| 13 | Witch Doctor | voodoo, brewing, shadowhunting |
| 14 | Felsworn | slayer, infernal, tyrant |
| 15 | Witch Hunter | boltslinger, houndmaster, black-knight, inquisition |
| 16 | Stormbringer | lightning, wind, maelstrom |
| 17 | Knight of Xoroth | war, hellfire, defiance |
| 18 | Guardian | vanguard, inspiration, gladiator |
| 19 | Templar | zealot, oathkeeper, crusader |
| 20 | Bloodmage | sanguine, accursed, eternal, fleshweaver |
| 21 | Ranger | archery, brigand, farstrider |
| 22 | Chronomancer | artificer, infinite, time |
| 23 | Necromancer | animation, death, rime |
| 24 | Pyromancer | incineration, flameweaving, draconic |
| 25 | Cultist | corruption, dreadnought, godblade, heretic |
| 26 | Starcaller | moon-guard, moon-priest, sentinel, warden |
| 27 | Sun Cleric | blessings, piety, seraphim, valkyrie |
| 28 | Tinker | demolition, invention, mechanics |
| 29 | Venomancer | fortitude, rot, stalking, vizier |
| 30 | Reaper | domination, harvest, soul |
| 31 | Primalist | geomancy, grovekeeper, mountain-king, wildwalker |
| 32 | Runemaster | glyphic, engravement, riftblade |

71 specs total. Local icon set (class + spec icons) lives at `~/ascoa/ascension-icons/`.

## Scraping db.ascension.gg

The site is aowow. Firecrawl renders it fine with `waitFor: 5000`. The rendered markdown
table only shows the first 50 rows, but the **complete** dataset is embedded in the page
as a JS listview literal — parse that instead:

```python
m = re.search(r'new Listview\(\{"template":"spell".*?"data":(\[.*?\]),"name"', rawHtml, re.S)
rows = json.loads(m.group(1))
```

Useful endpoints:

| URL | Returns |
|---|---|
| `?classes` | all class IDs + names in one listview |
| `?class=<id>` | class blurb, spec blurbs, and every spell for that class |
| `?spells=7.<classId>.<skillId>` | spells filtered to one spec's skill line |
| `?search=<name>` | multi-template search; several spell listviews per page |

Per-row fields worth knowing: `id`, `name` (prefixed `@`), `icon`, `level`, `rank`,
`skill` (spec skill-line array), `advClass` (class id), `advTab`, `advType`
(`""` / `Ability` / `Talent`), `isCoaClass`.

## Sidekick — the better source

`https://ascensionsidekick.com/<class>/<spec>` carries the **full talent tree with live
tooltips**, a rotation writeup, stat priority, dispel list, and a complete ability kit —
and it is maintained against the current build, which db.ascension.gg is not.
`https://ascensionsidekick.com/weakauras` hosts community WeakAuras with import strings.

`https://ascension.gg/en/v2/coa-builder/<name>` is a JS SPA that renders nothing useful
to a scraper (11MB of HTML, no embedded state). Skip it; Sidekick covers the same ground.
