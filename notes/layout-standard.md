---
title: CoA WeakAura layout standard
date: 2026-07-28
type: reference
status: budding
tags: [weakauras, conquest-of-azeroth, layout, standard]
sources:
  - "Generated guide artifact (mkguide.py, Runemaster final8)"
---

# Layout standard for every CoA class pack

Band order, sizes and spacing are fixed across all 21 classes so a player who
learns one pack can read any of them. Only the *contents* change per class, and
how many resources the class actually spends.

**Authority:** this file is derived from the generated guide artifact, which
`mkguide.py` renders 1:1 from a built pack. When this doc and the code disagree,
**the code wins** and this doc gets corrected — the previous version of this file
declared 8 bands with anchors that never existed in any shipped build.

## The ladder

```
                 anchor   icon   unit     band
  ┌────────────┐  -18     38px   player   reminders      missing imbues/etchings
  ├────────────┤  (drv)   28px   TARGET   on target      your DoTs or your HoTs
  ├────────────┤  -84     36px   player   on me          procs, running CDs, buffs
  ├────────────┤ -132     44px   —        MAIN           core rotation, always on
  ├─ ─ ─ ─ ─ ─ ┤ -168     20px   —        resource 1   ┐ RESOURCE STACK
  ├─ ─ ─ ─ ─ ─ ┤ -194     16px   —        resource 2   │ 1..N bands, ordered
  ├─ ─ ─ ─ ─ ─ ┤ (drv)     ..    —        resource N   ┘ by config
  ├────────────┤ -224*    26px   —        offensive CDs  wraps at 12
  ├────────────┤ -254*    26px   —        defensive+util wraps at 12, trinkets last
  └────────────┘ (drv)    28px   —        long-term      derived from 6/7 depth

  * anchors shown for a 2-resource class. The resource stack is the only
    variable-height section above the cooldowns, so every anchor below it is
    derived from the stack's real depth:

      1 resource   Engravement, Riftblade   mana                 -168
      2 resources  Glyphic                  mana + glyphs        -168 -194
      3 resources  Pyromancer               heat, ember, mana    -168 -194 -2xx

    A shorter stack pulls everything below it UP. This is the only dynamic
    geometry in a pack and it is engine-owned, not per-class arithmetic.

  (drv) = anchor derived, not a constant. See "Derived anchors" below.
```

| Band | Anchor | Icon | Unit | Owner | Purpose |
|---|---|---|---|---|---|
| Reminders | −18 | 38px | player | Core | Only when something is *missing* — imbues, consumables, a dropped self-buff. Names the hand for engravings |
| On target | derived | 28px | **target** | Spec | Your DoTs *or* your HoTs, whichever applies to the current target. Swaps automatically on retarget |
| On me | −84 | 36px | player | Spec | Everything currently up on you: procs, running cooldowns, own buffs |
| Main damage | −132 | 44px | — | Spec | Core rotation. Always visible, largest icons, glows on proc |
| **Resource stack** | −168 … | h20 / h16 | — | Spec | **1..N bands**, one per resource the class actually uses. Every band's width is locked to the main row. See below |
| Offensive cooldowns | −224\* | 26px | — | Spec | Damage cooldowns, most-pressed first. Interrupt and mobility pinned last |
| Defensive + utility | −254\* | 26px | — | Spec | Defensives, then utility, then on-use trinkets by slot |
| Long-term buffs | derived | 28px | — | **Core** | Stances, hour-long imbues, raid auras. Checked once per pull |

## The resource stack

A class has **one to three** resources and the pack renders one band per
resource. There is no "primary" and "secondary" — that framing came from
Runemaster, which happens to have at most two.

| Count | Class | Resources |
|---|---|---|
| 1 | Runemaster · Engravement, Riftblade | mana |
| 2 | Runemaster · Glyphic | mana + 3-cell glyph bar |
| 2 | Chronomancer · Artificer | mana + combo points |
| 3 | **Pyromancer** (class 24) | ember, mana, heat |

### Three axes

A resource is described by three independent choices. Do not collapse them —
each one varies for a real class, and the earlier single-`kind` schema could not
express ember at all.

**1. `source` — where the number comes from**

| Value | Reads | Example |
|---|---|---|
| `power` | `UnitPower` on the player | mana, energy, rage, heat |
| `aura_stacks` | **One** aura on the player, its stack count fills N cells | **ember** (5 stacks) |
| `aura_set` | **N distinct** auras, one per cell | Glyphic's Frost / Flame / Arcane |

`aura_set` is what `seg_bar` implements today. `aura_stacks` does not exist yet
and is the one genuinely new mechanism the stack needs.

**2. `render` — how it draws**

| Value | Height | Renders as |
|---|---|---|
| `bar` | 20px | Continuous `aurabar`, value text right-aligned |
| `segments` | 16px | N discrete cells spanning the row width. Two textures per cell: a dim outline always present, a solid fill over it |

**3. `prominence` — how loud it is**

Not every resource a class tracks is equally worth glancing at. Pyromancer
spends ember and mana together on the same abilities, while heat is background
state.

| Value | Renders as |
|---|---|
| `primary` | Full height, full width, value text |
| `minor` | **Half height** (bar 10px, segments 8px), full width, **value text dropped** |

`minor` deliberately keeps the full width. Reducing it would break the
width-lock invariant, which is the only thing stopping the resource bands and
the main row from drifting apart.

```
  MAIN   [ 44 ][ 44 ][ 44 ][ 44 ][ 44 ]

  ember  [##][##][##][  ][  ]              16px  segments/aura_stacks  primary
  mana   [============ 74% ===]            20px  bar/power             primary
  heat   [======          ]                10px  bar/power             MINOR
```

### Rules for the stack

- **Every band spans the main row's width**, derived from its icon count. All
  resources line up with each other and with the main row. `minor` included.
- **Order is by prominence, most-glanced nearest the main row.** This is the
  existing "vertical order encodes urgency" rule, not a new one. Pyromancer is
  ember, mana, heat.
- **Never render a resource the class does not spend.** A vestigial bar costs
  prime screen space next to the main row. Tracking three is fine when all three
  are real, as on Pyromancer.
- **`segments` needs an always-true trigger** for the dim cells — the CoA spec
  aura is a database entry, not a buff the player carries, and gating on it
  makes the empty cells never draw. `load.use_spellknown` already restricts the
  band to the right spec.
- Segment fills use **two displays**, not one display plus a condition —
  conditions in this fork have misfired before.
- The stack is the **only variable-height section above the cooldowns**, so
  every anchor below it is derived from the stack's real depth. Mixed heights
  (20 + 16 + 10) mean the depth cannot be inferred from band count alone.

## The target band

Raid-wide HoT state belongs to VuhDo/Grid, which own that job on 3.3.5a. The
pack tracks **the current target only**, and the same band serves both roles:

```
unit="target", own_only=True
    helpful=False  ->  your DoTs      shown while an enemy is targeted
    helpful=True   ->  your HoTs      shown while an ally is targeted
```

Both sets are active-only, so retargeting swaps the contents with no extra
machinery: enemy target shows your debuffs, friendly target shows your HoTs, no
target shows nothing. There is no multi-target tracking in a class pack, for
healers or anyone else.

Each icon carries time remaining (`%p`) and stacks (`%s`).

`own_only` is non-negotiable here — without it the band fills with every other
player's auras on your target and becomes unreadable in a raid.

## Derived anchors

Everything below the main row is computed, not fixed. Three independent sources
of variable height, which is why hand-tuned constants cannot survive 21 classes:

- **On target** — the ladder above the main row has no free gap. Reminders
  (−18, 38px) span +1…−37 and "on me" (−84, 36px) spans −66…−102, so this band
  is placed by the engine from real icon heights rather than a hand-picked
  constant.
- **The resource stack** — 1 to 3 bands of 20px or 16px. Everything below it
  shifts by the difference. Runemaster only ever exercised the 1-vs-2 case; a
  3-resource class like Pyromancer was never possible with fixed anchors.
- **Long-term buffs** — the cooldown bands wrap at 12 icons per row, so their
  total depth is data-dependent. Long-term sits below whatever depth they
  actually reach. The old fixed −300 gave only 19px of clearance in the deepest
  shipped case and breaks outright the moment a row wraps.

The engine computes the whole ladder top-down from real band heights plus a
fixed inter-band gap. No class declares an anchor.

## Rules

- **Everything is centred** — dynamic groups use `grow: "HORIZONTAL"`, never
  `"RIGHT"`, which left-aligns and makes rows of different length look ragged.
- **Every resource band's width is derived from the main row's icon count**,
  never set by hand, so they cannot drift apart.
- **Resource count varies 1–3 by class**, and the pack renders exactly what the
  class spends. Engravement and Riftblade have one (mana); Glyphic has two
  (mana + a 3-segment glyph bar); Chronomancer's Artificer has two (mana +
  combo points); Pyromancer has three (heat, ember, mana). A shorter stack pulls
  everything below it up.
- **Cooldown rows escalate as they come back**: timer appears at 20s, the icon
  glows at 10s, the glow turns urgent at 5s. The **main damage row is exempt** —
  those sit on 6–8s cooldowns, so the number is simply always shown there.
- **Spell cooldown triggers show the global cooldown — unless the ability is
  off-GCD.** `use_showgcd` is set by default in `wabuild.spell_cd_trigger`, so a
  ready ability sweeps for the ~1s after a cast: the cue for holding a press
  rather than clipping it. Templar sets it on 49 triggers, so it is verified
  ground on this fork.

  ⚠️ **WeakAuras applies the flag blindly.** For any spell not already on its
  own cooldown it substitutes the tracked global (`GenericTrigger.lua:2795`),
  with no per-spell knowledge — it polls one reference spell and every flagged
  trigger borrows that timer. On an ability that does not obey the global, the
  icon sweeps *every time you press something else*. **26 of Runemaster's 59
  cooldown abilities are off-GCD**, so this is the common case, not the corner
  case. Shipped broken in `final14`.

  `OFF_GCD` in the builder derives from `resources/cooldown-abilities.json`,
  scraped rather than curated: db.exil.es omits the `GCD` row for off-GCD
  spells and `audit_cds.py` records that as `gcd: false`. Full method, and how
  to run it for the next class, in [`off-gcd-detection.md`](off-gcd-detection.md).

  **Every escalation tier must be ANDed with `onCooldown == 1`** (`check_and`,
  combinator `trigger = -2` + `variable = "AND"`). With the GCD reported through
  the same trigger, a bare `expirationTime < 5` fires the urgent glow on *every
  icon in the row, on every global cooldown*. Any new condition reading
  `expirationTime` on a spell cooldown trigger inherits this requirement.

  `onCooldown` is exact: its `conditionTest` is `not state.gcdCooldown and
  state.expirationTime > GetTime()` (`Prototypes.lua:5700`), so the prototype
  itself excludes the global.

  ⚠️ **Do not guard on `gcdCooldown` directly.** It is declared `store = true`
  with no `conditionType` / `conditionTest`, so it is not a condition variable;
  WeakAuras drops the unknown sub-check and the AND silently collapses back to
  the bare `expirationTime` test, with no error. That shipped as `final12`.

  This is **not** because it is `hidden` — an earlier revision of this note gave
  that reason and it was wrong. `onCooldown` and `spellUsable` are both
  `hidden = true` and both work. `conditionType` is what makes a variable usable
  in a condition; `hidden` only keeps it out of the display-text picker.

  `final13`/`final14` used a `duration > 3` floor instead, which cost the
  escalation cues on every ability with a sub-3s cooldown (Unleash Essences
  2.5s, Trap Runes 3.0s) and was built on the wrong number besides: the global
  here is **1.0s base**, not 1.5s, and ranges 0.5s (`Warpdagger`) to 1.5s
  (`Elder Magi Rune`). Any fixed-length GCD heuristic is wrong on this server.

  Displays built with `genericShowOn: "showOnCooldown"` should generally pass
  `show_gcd=False`, or they pop into existence once per global. Treat this as
  a default rather than a law: Templar ships 13 triggers pairing
  `use_showgcd = true` with `showOnCooldown`, so the combination is legal and
  someone chose it deliberately. We have no display that wants it yet.
- **Every spell cooldown icon desaturates when it cannot be cast**
  (`spellUsable == 0` → `desaturate = true`, added in `final14`). This is a
  *different question* from the cooldown, and the swipe cannot answer it: an
  ability that is off cooldown but unaffordable — no mana, no resource, wrong
  form — otherwise reads as "press me". Verified on this fork: Templar drives
  `desaturate` off `spellUsable` 9 times and off `onCooldown` 15 more.

  It needs **no GCD guard**. `spellUsable` reflects `IsUsableSpell`, which is
  independent of any cooldown, so a global does not flip it.

  It applies to `cd_icon` output *only*. `spellUsable` lives on the
  `Cooldown Progress (Spell)` prototype and means nothing on the aura,
  enchant and custom-Lua leaves, so those must not carry the condition.
  `tests/run.py` check 9 enforces both halves of this and check 9's second
  half re-asserts the `final12` bare-`expirationTime` ban.
- **`inverse = true` with `cooldown = true` is correct for cooldown icons**,
  despite the rule written after the trinket crash. `inverse` reverses the
  swipe direction (`cooldown:SetReverse`), it does not mean "show when there
  is no cooldown" — see `weakauras-data-model.md` §572. Templar ships **all
  48** of its spell cooldown icons this way. The `Icon.lua:642` crash
  (arithmetic on a nil `expirationTime`) came from the **item** cooldown
  trigger, which can report nil where the spell prototype does not. Scope the
  rule to item triggers; do not carry the broad version into a new class.
- **Cooldown rows should wrap at 12** icons and push the long-term band down. A
  row of 23 (Engravement utility, `final8`) is 642px against a 274px main row
  and must not ship flush.

  ⚠️ **This is the intent, NOT what ships.** `CD_PER_ROW = 12` and `Y_CDS` are
  defined in `build_runemaster.py` and never referenced — dead constants. Every
  cooldown row is emitted `grow: "HORIZONTAL"` with `useLimit: false`, which is
  one unbroken line at any child count, and the band ladder advances by a fixed
  `CD_ROW_STEP` that assumes a single row regardless.

  Measured in `final15`, always-visible rows against the 270px resource bar:

  | Row | Icons | Width | vs bar |
  |---|---|---|---|
  | Engravement Utility | 21 | 586px | 2.17x |
  | Riftblade Utility | 16 | 446px | 1.65x |
  | Glyphic Offense | 14 | 390px | 1.44x |
  | Glyphic Utility | 13 | 362px | 1.34x |
  | Riftblade Offense | 12 | 334px | 1.24x |
  | Engravement Offense | 11 | 306px | 1.13x |

  Wiring the wrap needs both halves: `useLimit: true` + `limit: CD_PER_ROW` on
  the dynamic group, **and** a band ladder that advances by
  `ceil(n / CD_PER_ROW) * CD_ROW_STEP` instead of a flat step — otherwise a
  wrapped row grows down into the band beneath it.

  This is the concrete case of the standing rule below: the constants in the
  builder are not authority for what shipped.
- **Active-only rows are the norm** — buff/proc rows are empty until something
  is up, so a 27-entry row is a handful of icons in play.
- **Vertical order encodes urgency**: react-within-a-global nearest the
  character, set-and-forget furthest away.
- **Gate at the leaf.** A plain group's triggers, conditions and load are inert
  — WeakAuras skips load-scanning for any aura with `controlledChildren` — so
  every leaf carries its own gate:

  | | all-specs pack | per-spec pack |
  |---|---|---|
  | Core leaves | `use_class` | `use_class` + `spellknown(that spec)` |
  | Spec leaves | `use_class` + `spellknown(own spec)` | same |

  - **`use_class`** → the class token from [[class-tokens]]. **Every leaf, no
    exceptions.** Confirmed working in game 2026-07-28.
  - **`use_spellknown`** → the spell only that spec knows. Spec leaves always;
    Core leaves only in a spec-scoped build.

  Core is class-only in the all-specs pack on purpose: engravings and etchings
  apply to the whole class, so spec-gating them there would hide them on the
  other specs. Only the spec-scoped build narrows Core to a single spec.

  **Do not gate Core on a class-wide spell.** That was tried — Primordial Blast
  (`800732`), shared by all three Runemaster specs — and it is wrong for a
  **levelling character**: someone who has not learned it yet loses the "you
  forgot your weapon engraving" reminder, which is exactly the player who needs
  it most. The class gate has no such hole.

  ```python
  c["load"]["use_class"] = True                # every leaf, no exceptions
  c["load"]["class"]["single"] = CLASS_TOKEN

  spec = owning_spec(c) or SPEC_TITLE          # Core inherits in a per-spec build
  if spec:
      c["load"]["use_spellknown"] = True
      c["load"]["spellknown"] = SPEC_KNOWN[spec]
  ```

  Assert both: a leaf without a class gate loads on every character of every
  class, and a spec-scoped pack whose Core is unnarrowed shows one spec's
  alerts while you play another. The build refuses to emit rather than ship
  either.

  **CoA classes alias onto base class tokens**, and the mapping is not
  derivable from the class id — Runemaster is class 32 and loads as
  `SPIRITMAGE`. The field is `class.single`, not `class.multi`:

  ```lua
  ["load"] = {
      ["use_class"] = true,
      ["class"] = { ["single"] = "SPIRITMAGE", ["multi"] = {} },
      ["use_spellknown"] = true,
      ["spellknown"] = 801179,
  },
  ```

  **Every class pack needs its token captured, not guessed.** Assign the class
  by hand in the WA UI on one display, then read `class.single` back out of
  `WTF/Account/<ACCOUNT>/SavedVariables/WeakAuras.lua` (account-level — WA
  declares `SavedVariables`, not `SavedVariablesPerCharacter`).

  **Two holes this closes, both shipped in `final8`:**
  1. Nothing sets `use_class` (`wabuild.py:281` emits an empty
     `"class": {"multi": {}}` with no flag), so every pack loads on every
     character of every class.
  2. `restrict_to_spec()` keeps `RM Core` whole and only drops the other spec
     groups, so a per-spec pack's Core leaves are ungated — the Riftblade pack's
     alerts render on a Glyphic character.

  The visible symptom is the reminder band: it is inverse-triggered ("show when
  missing"), so on any character that cannot satisfy it, it is **permanently on
  screen**.

  Assert both: a build where any leaf lacks a class gate fails, and a per-spec
  build where any leaf lacks a spec gate fails.

- **Load gating is the performance story.** WeakAuras skips trigger
  registration for auras that fail load, so a correctly gated pack costs
  essentially nothing on a character it does not apply to. Ungated, every
  installed class pack evaluates on every character — with 21 packs on a 2010
  client that dominates the per-pack region count by a wide margin.
- **Display ids are unique; names are not.** The same ability legitimately
  appears in two bands — an offensive cooldown shows as a CD icon in the
  cooldown band *and* as a running buff in "on me", because a swipe reads as
  "unavailable" while the buff reads as "active". That is deliberate
  (`build_runemaster.py:783-794`). What WeakAuras rejects on import is a
  duplicate **display id**, so the invariant is uniqueness of `<band> <name>`,
  not of `<name>`. Within a single band, a repeated name *is* a fault — which is
  why `cd_buffs` dedupes against the procs and state entries before merging.

## Known dead code (delete during engine extraction)

Defined in `build_runemaster.py`, referenced nowhere, and corresponding to no
band that has ever rendered. These are what produced the earlier wrong versions
of this document:

`Y_PROCS = -60` · `Y_CDS = -242` · `Y_DOTS = -333` · `CD_PER_ROW = 12` ·
`SZ_STATE = 28` · `dot_bars()` (`:476`, zero callers)

`CD_PER_ROW` and `dot_bars()` are the exceptions — both get wired up rather than
deleted: `CD_PER_ROW` becomes the band 6/7 wrap, and `dot_bars()` becomes the
target band's implementation.

Generated view: `tools/mkguide.py` reads a built pack and renders this plus the
per-spec breakdown. Build the guide and agree the layout *before* spending an
in-game import cycle.
