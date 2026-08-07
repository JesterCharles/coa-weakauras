---
title: WeakAuras Data Model — Field-Level Reference for Programmatic Import Generation
date: 2026-07-27
type: reference
status: budding
tags:
  - weakauras
  - wow
  - ascension
  - 3.3.5a
  - lua
  - reverse-engineering
  - coa-runemaster
sources:
  - "https://github.com/Ascension-Addons/WeakAuras-Ascension — THE TARGET FORK. Cloned 2026-07-27, HEAD 2026-02-17, `## Interface: 30300`, `## Version: 5.21.2`, `internalVersion = 86`. Fork of NoM0Re/WeakAuras-WotLK."
  - "https://github.com/WeakAuras/WeakAuras2 — upstream tag `5.21.2` (`internalVersion = 88`), read in full via git worktree"
  - "https://github.com/WeakAuras/WeakAuras2 — upstream `main` @ 2026-07-27 (`internalVersion = 90`)"
  - "https://github.com/WeakAuras/WeakAuras2/wiki/_pages — the wiki has only 27 pages and contains NO page on Group / Dynamic Group / Region Types / Conditions / Sub-Regions / Import-Export. Relevant existing pages: Custom-Dynamic-Group, Custom-Anchor, Editing-Aura-Regions, Aura-Types, API-Documentation."
  - "https://github.com/WeakAuras/WeakAuras2/wiki/Custom-Dynamic-Group — the only wiki page documenting regionData / custom grow / custom sort"
  - "https://github.com/geexmmo/python-weakauras-tool — existing Python codec (drives the real Lua libs via Lupa)"
  - "NOT A SOURCE: https://mintlify.wiki/NoM0Re/WeakAuras-WotLK/development/importing-exporting is LLM-generated and fabricates the contents of `non_transmissable_fields`. Do not cite."
---

# WeakAuras Data Model — Field-Level Reference

Written to support a Python generator that emits `!WA:2!` import strings for the
Ascension (Conquest of Azeroth) 3.3.5a WeakAuras fork.

## 0. Version grounding — READ THIS FIRST

**The premise that this fork is "2.x/3.x era" is wrong, and that matters.**

| Fact | Evidence |
|---|---|
| Fork reports version string `5.21.2 Beta` | client export `s` field |
| Upstream WeakAuras has a real tag `5.21.2` | `git ls-remote --tags` on WeakAuras/WeakAuras2 |
| Upstream `5.21.2` has `internalVersion = 88` | `WeakAuras/WeakAuras.lua:6` at tag `5.21.2` |
| Upstream `main` (2026-07-27) has `internalVersion = 90` | `WeakAuras/WeakAuras.lua:6` |
| Fork reports `internalVersion = 89.5` | client export |

CONFIRMED: the Ascension fork is a **backport of modern WeakAuras 5.21.x to the
3.3.5a client**, not a 2.x/3.x-era addon. The `.5` on `89.5` is a fork-local
marker (upstream `internalVersion` is always an integer), sitting between
upstream 89 and 90 — i.e. the fork tracks a very recent upstream.

**Consequence: read the modern source, not old tags.** Everything below is
CONFIRMED against the upstream `5.21.2` worktree unless flagged otherwise. The
one place old-vs-new matters is `Modernize.lua` legacy steps (§9.3), which will
never run for us because we emit a high `internalVersion`.

Reference paths in this doc are relative to the addon root, e.g.
`WeakAuras/RegionTypes/DynamicGroup.lua`.

---

## 1. How a `dynamicgroup` positions its children

### 1.1 The single most important fact

`WeakAuras/RegionTypes/RegionPrototype.lua`, in `Private.regionPrototype.modify`
(the function every region runs through):

```lua
region:SetOffset(data.xOffset or 0, data.yOffset or 0);      -- ← ALWAYS runs
region:SetOffsetRelative(0, 0)
region:SetOffsetAnim(0, 0);
...
if not parent or parent.regionType ~= "dynamicgroup" then
  if not (data.anchorFrameType == "CUSTOM"
          or data.anchorFrameType == "UNITFRAME"
          or data.anchorFrameType == "NAMEPLATE")
     or data.regionType == "dynamicgroup"
     or data.regionType == "group"
  then
    Private.AnchorFrame(data, region, parent);                -- ← SKIPPED for
  end                                                         --   dyngroup kids
end
```

**CONFIRMED — answer to Q1:** if a region's parent is a `dynamicgroup`,
`Private.AnchorFrame` is **never called for it**. Therefore on a child of a
dynamic group these fields are **completely ignored**:

- `anchorFrameType` (all values — `SCREEN`, `PRD`, `MOUSE`, `SELECTFRAME`,
  `UNITFRAME`, `NAMEPLATE`, `CUSTOM`, `UIPARENT`)
- `anchorFrameFrame`
- `anchorPoint`
- `selfPoint` (the **group's** `selfPoint` is used instead — see below)
- `anchorFrameParent`
- `customAnchor`

So: **setting `anchorFrameType = "SCREEN"` on a dynamicgroup child is harmless
and is in fact exactly what the WeakAuras UI itself writes.** It is not the
cause of piled-up icons. It is inert.

### 1.2 What IS read off the child

`WeakAuras/RegionTypes/DynamicGroup.lua`, `createRegionData` (inside `modify`):

```lua
local controlPoint = region.controlPoints:Acquire()
...
if childData.regionType == "text" then
  regionData.dimensions = childRegion     -- measured live
else
  regionData.dimensions = childData        -- ← the child's DATA table
end
controlPoint.regionData = regionData
childRegion:SetParent(controlPoint)
childRegion:SetAnchor(data.selfPoint, controlPoint, data.selfPoint)
--                    ^^^^ `data` here is the GROUP's data
```

and `DoPositionChildrenPerFrame`:

```lua
controlPoint:SetAnchorPoint(data.selfPoint, self, data.selfPoint, x, y)  -- frame == ""
controlPoint:SetWidth(regionData.dimensions.width)
controlPoint:SetHeight(regionData.dimensions.height)
```

Fields read from the CHILD by a dynamic group:

| Child field | Used for | Notes |
|---|---|---|
| `width` | layout arithmetic (`regionData.dimensions.width`) | read from the **data table**, not the rendered frame. **Required.** nil ⇒ Lua arithmetic error in the grower. |
| `height` | layout arithmetic | same |
| `regionType` | `== "text"` switches to live measurement | |
| `frameStrata` | `1` ⇒ inherit group's strata; else `Private.frame_strata_types[frameStrata]` | |
| `xOffset` / `yOffset` | **added on top of the computed slot** | see §1.3 — this is a real trap |
| `id` | must appear in the group's `controlledChildren` | see §1.4 |

Fields read from the **group** and applied to every child: `selfPoint` (used for
BOTH the control-point-to-group anchor and the child-to-control-point anchor),
`grow`, `align`, `space`, `stagger`, `sort`, `limit`/`useLimit`, `radius`,
`rotation`, `stepAngle`, `fullCircle`, `arcLength`, `constantFactor`, `gridType`,
`gridWidth`, `rowSpace`, `columnSpace`, `centerType`, `scale`, `animate`.

Note the child's own `scale` is also ignored — the control point is scaled with
the **group's** `scale`.

**Corroboration #1 — the options UI hides exactly these fields.**
`WeakAurasOptions/CommonOptions.lua`, `PositionOptions()`:

```lua
local function IsParentDynamicGroup()
  if data.parent then
    local parentData = WeakAuras.GetData(data.parent)
    return parentData and parentData.regionType == "dynamicgroup"
  end
end
```

used as the `hidden` predicate for `anchorFrameType`, `anchorFrameParent`,
`anchorFrameFrame`, `chooseAnchorFrameFrame`, `selfPoint`, `anchorPoint`,
`anchorFrameSpaceOne`, `anchorFramePoints`. `width`, `height`, `xOffset` and
`yOffset` stay **visible** — which independently confirms both halves of §1.2
and §1.3.

**Corroboration #2 — Modernize says so.** `Modernize.lua`, the v2→v3 step
(April 2018):

```lua
if data.internalVersion < 3 then
  if data.parent then
    local parentData = WeakAuras.GetData(data.parent)
    if parentData and parentData.regionType == "dynamicgroup" then
      -- Version 3 allowed for offsets for dynamic groups, before that they were ignored
      data.xOffset = 0
      data.yOffset = 0
    end
  end
end
```

i.e. offsets *used* to be ignored inside dynamic groups and have been honoured
since internalVersion 3. This is the 2.x-era difference the brief was worried
about, and it resolved in favour of "offsets apply" seven years ago.

### 1.3 TRAP: child `xOffset`/`yOffset` still apply inside a dynamic group

`SetOffset` runs unconditionally in `regionPrototype.modify`, before the
dyngroup skip. `SetAnchor` → `UpdatePosition`:

```lua
local xOffset = self.xOffset + (self.xOffsetAnim or 0) + (self.xOffsetRelative or 0)
local yOffset = self.yOffset + (self.yOffsetAnim or 0) + (self.yOffsetRelative or 0)
self:RealClearAllPoints();
self:SetPoint(self.anchorPoint, self.relativeTo, self.relativePoint, xOffset, yOffset)
```

**CONFIRMED:** a dynamicgroup child with `xOffset = 40, yOffset = -110` is laid
out into its correct slot by the group and *then displaced by (40, -110)*. If
every child in a group carries the same offsets, **they all shift together and
still look laid out**; if they carry *different* offsets the row goes ragged.

⇒ **Always emit `xOffset = 0, yOffset = 0` on dynamicgroup children.** Put the
positioning on the group.

### 1.4 The real "all children pile up at one point" failure mode

If a child's `parent` names a dynamicgroup but the child's `id` is **not** in
that group's `controlledChildren` (typo, stale id, rename, duplicate id), then:

1. `region:ReloadControlledChildren()` iterates `data.controlledChildren` only —
   the child is never acquired, never gets a control point.
2. `regionPrototype.modify` still sees `parent.regionType == "dynamicgroup"` and
   therefore **skips `Private.AnchorFrame`**.
3. `SetAnchor` is never called, so `UpdatePosition` returns early
   (`if (not self.anchorPoint or not self.relativeTo ...) then return end`).
4. The frame has **no anchor point at all** and falls back to the WoW default.

**Every orphaned child ends up at the same place ⇒ overlapping icons.** This is
the mechanism to check first when icons pile up.

### 1.5 `anchorFrameType` semantics (only meaningful on non-dyngroup-children)

`Private.anchor_frame_types` (`WeakAuras/Types.lua:1521`) and
`GetAnchorFrame` (`WeakAuras/WeakAuras.lua:6004`):

| Value | UI label | Returns |
|---|---|---|
| `SCREEN` | "Screen/Parent Group" | `parent` — i.e. **the parent group's region** when the aura is in a group, otherwise `WeakAurasFrame` |
| `UIPARENT` | "Screen" | `UIParent` (ignores group nesting) |
| `PRD` | "Personal Resource Display" | the PRD frame |
| `MOUSE` | "Mouse Cursor" | a follow-cursor frame |
| `SELECTFRAME` | "Select Frame" | `_G[anchorFrameFrame]`, or another aura's region if `anchorFrameFrame` starts with `"WeakAuras:"` |
| `NAMEPLATE` | "Nameplates" | nameplate for `region.state.unit` |
| `UNITFRAME` | "Unit Frames" | `WeakAuras.GetUnitFrame(unit)` |
| `CUSTOM` | "Custom" | result of `region.customAnchorFunc` (`data.customAnchor` Lua source) |

`Private.anchor_frame_types_group` (groups/dynamicgroups) omits `NAMEPLATE` and
`UNITFRAME` — a group may only use `SCREEN`, `UIPARENT`, `PRD`, `MOUSE`,
`SELECTFRAME`, `CUSTOM`.

**`SCREEN` is the correct default for everything we emit.** On a 3.3.5 client
`PRD` is present (WA draws its own PRD frame) but pointless for us; `NAMEPLATE`
is unreliable on 3.3.5.

Additional rule in `Private.AnchorFrame`:

```lua
local anchorPoint = data.anchorPoint
if data.parent then
  if data.anchorFrameType == "SCREEN" or data.anchorFrameType == "MOUSE" then
    anchorPoint = "CENTER"      -- ← FORCED for any child of any group
  end
end
region:SetAnchor(data.selfPoint, anchorParent, anchorPoint);
```

**CONFIRMED:** for a child of a plain `group` with `anchorFrameType = "SCREEN"`,
`anchorPoint` is *forced* to `CENTER` regardless of what we emit. Only
`selfPoint` and `xOffset`/`yOffset` matter. So plain-group children are always
positioned as `child.selfPoint` → `group CENTER` + `(xOffset, yOffset)`.

---

## 2. `grow` values and the arrangement fields

`Private.grow_types` (`WeakAuras/Types.lua:2954`) and the `growers` table
(`WeakAuras/RegionTypes/DynamicGroup.lua:517`).

All growers produce `newPositions[frame][regionData] = { x, y, show }` in a
coordinate space whose **origin (0,0) is the group's `selfPoint`** — the control
point is anchored `data.selfPoint` → group `data.selfPoint` at `(x, y)`.

| `grow` | UI label | Behaviour | Origin |
|---|---|---|---|
| `LEFT` | Left | `x` starts 0, decreases by `width + space` per child | first child's edge sits ON the anchor; row extends left |
| `RIGHT` | Right | `x` starts 0, increases by `width + space` | first child on anchor, extends right |
| `UP` | Up | `y` starts 0, increases by `height + space` | first child on anchor, extends up |
| `DOWN` | Down | `y` starts 0, decreases by `height + space` | first child on anchor, extends down |
| `HORIZONTAL` | Centered Horizontal | computes `totalWidth`, starts at `-totalWidth/2`, walks right | **the whole row is centred on the anchor** |
| `VERTICAL` | Centered Vertical | computes `totalHeight`, starts at `-totalHeight/2` | **centred column** |
| `CIRCLE` | *"Counter Clockwise"* | polar, `dAngle` positive | centred on anchor |
| `COUNTERCIRCLE` | *"Clockwise"* | polar, `dAngle` negative | centred on anchor |
| `GRID` | Grid | see `gridType` below | depends on `gridType` |
| `CUSTOM` | Custom | runs `data.customGrow(newPositions, activeRegions)` | user-defined |

⚠️ Note the labels for `CIRCLE`/`COUNTERCIRCLE` are inverted relative to the
constant names in `Types.lua` — that is upstream, not a typo here.

**Centring:** only `HORIZONTAL`, `VERTICAL`, `CIRCLE`, `COUNTERCIRCLE`, and the
centred `gridType`s (`H*`/`V*`/`*H`/`*V`) centre on the anchor. `LEFT`/`RIGHT`/
`UP`/`DOWN` align *from* the anchor.

⇒ For rows that must line up with a centred bar, use `grow = "HORIZONTAL"`.
CONFIRMED correct.

### 2.1 Field-by-field

| Field | Type | Default | Meaning |
|---|---|---|---|
| `grow` | string | `"DOWN"` | see table. Unknown value falls back to `growers.DOWN` (`createGrowFunc`). |
| `space` | number | `2` | gap between consecutive children (px). For `CIRCLE` with `constantFactor == "SPACING"`, radius is derived as `(numVisible * space) / (2π)`. |
| `stagger` | number | `0` | perpendicular offset added per child. **Only used by `LEFT`/`RIGHT`/`UP`/`DOWN`/`HORIZONTAL`/`VERTICAL`.** |
| `align` | `"LEFT"`\|`"CENTER"`\|`"RIGHT"` | `"CENTER"` | **ONLY affects `stagger`.** `staggerCoefficient(align, stagger)` returns 0 / 0.5 / 1 and shifts the whole staggered run so it hangs from the left edge, centre, or right edge. **With `stagger == 0`, `align` does literally nothing.** (CONFIRMED: `data.align` appears at exactly 4 call sites in `DynamicGroup.lua`, all `staggerCoefficient`.) |
| `selfPoint` | anchor point string | `"TOP"` (region default) | double duty: anchors the control point to the group AND the child to the control point. Effectively "which corner of each child sits at its computed slot". |
| `sort` | `"none"`\|`"ascending"`\|`"descending"`\|`"hybrid"`\|`"custom"` | `"none"` | `none` = order of `controlledChildren` (`dataIndex`) then `state.index`. `ascending`/`descending` = by `state.expirationTime`. `hybrid` uses `sortHybridTable` + `hybridPosition` (`hybridFirst`/`hybridLast`) + `hybridSortMode` (`ascending`/`descending`). `custom` runs `data.customSort(a,b)` and re-sorts on the events named in `data.sortOn`. |
| `useLimit` / `limit` | bool / number | `false` / `5` | `local limit = data.useLimit and data.limit or math.huge`; `numVisible = min(limit, #regionDatas)`. Children beyond the limit are simply not positioned (and their control point is not shown). |
| `radius` | number | `200` | `CIRCLE`/`COUNTERCIRCLE` radius, used when `constantFactor` is `RADIUS` or `ANGLE`. |
| `rotation` | number (deg) | `0` | starting angle for `CIRCLE`/`COUNTERCIRCLE` (`sAngle`). Not a texture rotation. |
| `stepAngle` | number (deg) | `15` | per-child angle when `constantFactor == "ANGLE"`. |
| `fullCircle` | bool | `true` | if false, `arcLength` degrees are divided over `numVisible - 1`; if true, over `numVisible`. |
| `arcLength` | number (deg) | `360` | used only when `fullCircle == false`. |
| `constantFactor` | `"RADIUS"`\|`"ANGLE"`\|(anything else ⇒ spacing) | `"RADIUS"` | `RADIUS`: fixed radius, angle divided over children. `ANGLE`: fixed radius + fixed `stepAngle`. otherwise: radius derived from `space`. |
| `gridType` | 2-char string | `"RD"` | `Private.grid_types`: `RU RD LU LD UR DR UL DL HD HU VR VL DH UH LV RV HV VH`. First char = primary axis/direction, second = secondary. `R`/`L` = right/left, `U`/`D` = up/down, `H` = centred horizontal, `V` = centred vertical. Row-first iff first char is `R`, `L`, or `H`. |
| `gridWidth` | number | `5` | children per primary run before wrapping (`if i % gridWidth == 0`). |
| `rowSpace` / `columnSpace` | number | `1` / `1` | grid gaps. |
| `centerType` | `"LR"`\|`"RL"`\|`"CLR"`\|`"CRL"` | `"LR"` | fill order for `HORIZONTAL`/`VERTICAL`. `CLR` = centre, then alternate left/right (`4 2 1 3`); `CRL` = centre, then right/left (`3 1 2 4`). |
| `animate` | bool | `false` | animates control-point moves (0.2 s translate). |
| `useAnchorPerUnit` / `anchorPerUnit` | bool / `"NAMEPLATE"`\|`"UNITFRAME"`\|`"CUSTOM"` | `false` | splits children into one layout per unit frame. Leave off. |
| `scale` | number | `1` | clamped `0 < scale <= 10`, else 1. |
| `border*`, `backdropColor` | | | group backdrop; suppressed entirely when `useAnchorPerUnit`. |

Dynamicgroup `default` table verbatim (`DynamicGroup.lua:12`):

```lua
controlledChildren = {}, border = false, borderColor = {0,0,0,1},
backdropColor = {1,1,1,0.5}, borderEdge = "Square Full White", borderOffset = 4,
borderInset = 1, borderSize = 2, borderBackdrop = "Blizzard Tooltip",
grow = "DOWN", selfPoint = "TOP", align = "CENTER", space = 2, stagger = 0,
sort = "none", animate = false, anchorPoint = "CENTER",
anchorFrameType = "SCREEN", xOffset = 0, yOffset = 0, radius = 200,
rotation = 0, stepAngle = 15, fullCircle = true, arcLength = 360,
constantFactor = "RADIUS", frameStrata = 1, scale = 1, useLimit = false,
limit = 5, gridType = "RD", centerType = "LR", gridWidth = 5, rowSpace = 1,
columnSpace = 1
```

Fork-only addition: `sharedFrameLevel = true` (see §8B).

Fields read by the code but **absent from the default** (so nil unless you set
them): `useAnchorPerUnit`, `anchorPerUnit`, `anchorOn`, `customAnchorPerUnit`,
`customGrow`, `growOn`, `customSort`, `sortOn`, `sortHybridTable`,
`hybridPosition`, `hybridSortMode`, `groupIcon`, `anchorFrameParent`,
`anchorFrameFrame`.

### 2.2 `selfPoint` should follow `grow` + `align`

`selfPoint` is not independent in practice — the options UI *derives* it
whenever you change `grow` or `align`
(`WeakAurasOptions/RegionOptions/DynamicGroup.lua:9-85`). If you emit a
`grow`/`align`/`selfPoint` combination the UI would never produce, the layout
will not match what a human would build. Use this table:

| `grow` | `align = LEFT` | `align = CENTER` | `align = RIGHT` |
|---|---|---|---|
| `RIGHT` | `TOPLEFT` | `LEFT` | `BOTTOMLEFT` |
| `LEFT` | `TOPRIGHT` | `RIGHT` | `BOTTOMRIGHT` |
| `UP` | `BOTTOMLEFT` | `BOTTOM` | `BOTTOMRIGHT` |
| `DOWN` | `TOPLEFT` | `TOP` | `TOPRIGHT` |
| `HORIZONTAL` | `TOP` | `CENTER` | `BOTTOM` |
| `VERTICAL` | `LEFT` | `CENTER` | `RIGHT` |
| `CIRCLE` / `COUNTERCIRCLE` | `CENTER` | `CENTER` | `CENTER` |

For `grow = "GRID"` the UI uses a separate `gridSelfPoints[gridType]` map:
`RU`/`UR` → `BOTTOMLEFT`, `LU`/`UL` → `BOTTOMRIGHT`, `RD`/`DR` → `TOPLEFT`,
`LD`/`DL` → `TOPRIGHT`, `HD`/`DH` → `TOP`, `HU`/`UH` → `BOTTOM`,
`VR`/`RV` → `LEFT`, `VL`/`LV` → `RIGHT`, `HV`/`VH` → `CENTER`.

⇒ For the common case `grow = "HORIZONTAL"`, `align = "CENTER"`, emit
`selfPoint = "CENTER"`. (This is what you are already doing, and it is correct.)

---

## 3. `group` vs `dynamicgroup`

### 3.1 A plain `group` does NOT position its children

`WeakAuras/RegionTypes/Group.lua` has no layout code at all. Its `modify` only:
sets its own `selfPoint`, draws an optional border sized to the bounding box of
its children, and fixes frame levels.

Children of a plain group are positioned by the normal
`Private.AnchorFrame` path (because `parent.regionType ~= "dynamicgroup"`), i.e.:

- `anchorFrameType = "SCREEN"` ⇒ anchor parent is **the group's region frame**
- `anchorPoint` is **forced to `"CENTER"`** (because `data.parent` is set)
- child sits at `child.selfPoint` → group CENTER + `(child.xOffset, child.yOffset)`

⇒ **Children of a plain group keep their own coordinates**, relative to the
group's centre. That is exactly the behaviour you want for hand-laid-out packs.

The group's own frame is 2×2 px (`region:SetWidth(2); region:SetHeight(2)`), and:

```lua
if data.information.groupOffset then data.selfPoint = "BOTTOMLEFT"
else data.selfPoint = "CENTER" end
```

`information.groupOffset` is a **legacy flag** set by `Modernize` for groups that
predate `internalVersion 40`. Emit `information = {}` (no `groupOffset`) — you
get `selfPoint = "CENTER"`, which is modern behaviour. Note `data.information`
must be a table or this line errors; `Private.data_stub` guarantees it via
`PreAdd`.

### 3.2 A group's trigger does NOT control child visibility — CONFIRMED

This is a hard, source-confirmed answer, and it is a very common mistake.

`WeakAuras/WeakAuras.lua`, `scanForLoadsImpl`:

```lua
for id in pairs(toCheck) do
  local data = WeakAuras.GetData(id)
  if (data and not data.controlledChildren) then    -- ← groups skipped entirely
    ... loadFunc ... toLoad/toUnload ...
```

`pAdd` (`WeakAuras.lua:3205`):

```lua
if Private.IsGroupType(data) then           -- regionType == "group" or "dynamicgroup"
  Private.ClearAuraEnvironment(id);
  ...
  db.displays[id] = data;
  cycleCheck(data)
  if WeakAuras.GetRegion(data.id) then Private.SetRegion(data) end
  Private.ScanForLoadsGroup({[id] = true});
  loadEvents["GROUP"][id] = true
else -- Non group aura
  data.controlledChildren = nil
  ...
  for _, triggerSystem in pairs(triggerSystems) do triggerSystem.Add(data) end
  ...
  Private.LoadConditionPropertyFunctions(data);
  Private.LoadConditionFunction(data)
  loadFuncs[id] = loadFunc;
  triggerState[id] = { ... }
end
```

**On a `group` or `dynamicgroup`:**

- `data.triggers` is **never registered with any trigger system** — inert.
- `data.conditions` is **never compiled** (`LoadConditionFunction` not called) — inert.
- `data.load` is **never compiled** (`loadFuncs[id]` never set) — inert.
- The group's loaded state is derived purely from its children:
  `Private.ScanForLoadsGroup` sets `loaded[id] = any_loaded` over
  `Private.TraverseLeafs(data)`.

⇒ **You cannot gate a row of icons by putting a trigger on the group that
contains them.** The group is always shown; the row always renders. To gate a
row, put the gating trigger (or a Load condition) on **each leaf aura**, or use
a per-leaf condition that sets `alpha = 0`.

`Private.IsGroupType` = `data.regionType == "group" or data.regionType == "dynamicgroup"`.
Note the load-scan guard keys on `data.controlledChildren` being **truthy** — an
empty table `{}` is truthy in Lua, so an empty group is still skipped.

### 3.3 `controlledChildren` and `parent`

- `controlledChildren` is an **array of child `id` strings, in display order**,
  on the parent.
- `parent` is the **parent's `id` string**, on the child.
- **Both are required and must agree.** The dynamic group iterates
  `data.controlledChildren` (`ReloadControlledChildren`); the anchoring code and
  the import code both key off `data.parent`.
- `pAdd` explicitly nils `controlledChildren` on non-group auras:
  `data.controlledChildren = nil` — so never emit it on a leaf.
- Order in `controlledChildren` is the `dataIndex` used by `sort = "none"` and by
  `Private.FixGroupChildrenOrderForGroup` for frame levels.
- Nesting is allowed to arbitrary depth (group → group → dynamicgroup → leaf).
  Nested groups force export `v = 2000` (see §5.1).

### 3.4 ⚠️ A `dynamicgroup` may NOT contain a `group` or `dynamicgroup`

`Private.SyncParentChildRelationships` (`WeakAuras.lua:2488`) runs at login and
rewrites your saved variables. Its own header comment lists what it strips:

```
--    The child doesn't exist in the database
--    The child ID is duplicated in data.controlledChildren (only the first will be kept)
--    The child's data.parent points to a different parent
--    The parent is a dynamic group and the child is a group/dynamic group
```

and the enforcement:

```lua
elseif dynamicGroup and child.controlledChildren then
  prettyPrint("Detected corruption in saved variables: "..id..
              " is a dynamic group and controls "..childID..
              " which is a group/dynamicgroup.")
  child.parent = nil
  children[child.id] = nil
  childrenToRemove[index] = true
end
```

**CONFIRMED:** nest dynamic groups inside plain groups, never the other way
round. `group → dynamicgroup → leaf` is fine. `dynamicgroup → group` is severed
at the next login, leaving the inner group orphaned at an arbitrary position.

The same pass also enforces bidirectional consistency: a `parent` that doesn't
exist, a `parent` that isn't a group, a `controlledChildren` entry that doesn't
exist, a duplicate entry, or a child whose `parent` names someone else — all are
stripped with a `prettyPrint` warning. So the payload rules in §5.5 are enforced
twice: once at import, once at every login.

---

## 4. `icon` region fields

`WeakAuras/RegionTypes/Icon.lua`. Default table verbatim (line 16):

```lua
icon = true, desaturate = false, iconSource = -1, progressSource = {-1, ""},
adjustedMax = "", adjustedMin = "", inverse = false, width = 64, height = 64,
color = {1,1,1,1}, selfPoint = "CENTER", anchorPoint = "CENTER",
anchorFrameType = "SCREEN", xOffset = 0, yOffset = 0, zoom = 0,
keepAspectRatio = false, frameStrata = 1, cooldown = true,
cooldownTextDisabled = false, cooldownSwipe = true, cooldownEdge = false,
useCooldownModRate = true
```
plus `Private.regionPrototype.AddProgressSourceToDefault` ⇒
`progressSource = {-1, ""}`, `useAdjustededMax = false`, `useAdjustededMin = false`
(note the upstream typo **`useAdjustededMin`/`useAdjustededMax`** — three `d`s),
and `AddAlphaToDefault` ⇒ `alpha = 1`.

### 4.1 Which field actually sets the texture

`region:UpdateIcon()` (Icon.lua:504) — CONFIRMED verbatim:

```lua
function region:UpdateIcon()
  local iconPath
  if self.iconSource == -1 then
    iconPath = self.state.icon
  elseif self.iconSource == 0 then
    iconPath = self.displayIcon
  else
    local triggernumber = self.iconSource
    if triggernumber and self.states[triggernumber] then
      iconPath = self.states[triggernumber].icon
    end
  end
  iconPath = iconPath or self.displayIcon or "Interface\\Icons\\INV_Misc_QuestionMark"
  Private.SetTextureOrAtlas(self.icon, iconPath)
end
```

| Field | Role |
|---|---|
| `displayIcon` | **THE texture path.** String. Used directly when `iconSource == 0`, and as the fallback for every other `iconSource` value. This is the one that matters. |
| `iconSource` | number. `-1` = Automatic (icon from the *active* trigger's state), `0` = Manual (use `displayIcon`), `N >= 1` = icon from trigger N's state. Values enumerated by `Private.IconSources(data)` (`WeakAuras.lua:6551`): `[-1] = "Automatic"`, `[0] = "Manual Icon"`, `[i] = "Trigger i"` for `i = 1..#data.triggers`. |
| `icon` | **On an `icon` region this field is dead.** `grep 'data.icon\b'` across the addon hits only `BuffTrigger2.lua` (writing a scanned aura's icon into trigger data) and `AuraBar.lua:1256` (`region.iconVisible = data.icon`). It is in the icon default table for historical reasons. Setting it `true` is harmless; it does not draw anything. |
| `customIcon` | **Not a region field at all.** It is a *trigger* field for `trigger.type == "custom"` (a Lua snippet returning an icon), and `CompressDisplay` strips it for non-custom triggers (`Transmission.lua:129`). |

**Recommended:** set `iconSource = 0` + `displayIcon = "<path>"` when you want a
guaranteed fixed icon. With `iconSource = -1` the trigger wins whenever it
supplies an icon, and `displayIcon` is only the fallback — which is exactly how
art and tooltip end up disagreeing.

`Private.SetTextureOrAtlas` checks `GetAtlasInfo(path)`; on 3.3.5 atlases don't
exist, so it always falls through to `texture:SetTexture(path)`. Paths are the
usual `Interface\\Icons\\SPELL_FOO` form (backslashes) or a bare file name that
the client resolves.

### 4.2 The rest of the icon fields

| Field | Type | Default | Meaning |
|---|---|---|---|
| `width` / `height` | number | 64 / 64 | region size. **Also what a parent dynamicgroup uses for layout** (§1.2). Required in practice. |
| `zoom` | number 0–1 | 0 | crops the icon border: `texWidth = 1 - 0.5 * zoom`. `0.3` ≈ the usual "cut off the ugly border" value. |
| `keepAspectRatio` | bool | false | if true, tex coords are corrected by `width/height`; if false the art is stretched. |
| `color` | `{r,g,b,a}` | `{1,1,1,1}` | vertex colour multiplied over the icon texture. |
| `desaturate` | bool | false | greyscale. Common condition target. |
| `alpha` | number | 1 | region alpha. |
| `inverse` | bool | false | inverts the **cooldown swipe direction** (fill vs drain), not the colours. Passed to `cooldown:SetReverse`. |
| `cooldown` | bool | true | whether the region wires a cooldown frame at all. When false, `region.UpdateValue`/`UpdateTime` are not installed and no swipe is drawn. |
| `cooldownSwipe` | bool | true | draw the dark radial swipe. |
| `cooldownEdge` | bool | false | draw the rotating bright edge line. |
| `cooldownTextDisabled` | bool | false | Blizzard's built-in countdown numbers hidden (`SetHideCountdownNumbers`). Leave `false` only if you want the native numbers; most packs use a `subtext` with `%p` and set this `true`. |
| `useCooldownModRate` | bool | true | honour haste-scaled cooldown mod rate. On 3.3.5 `SetCooldown`'s third arg is ignored; harmless. |
| `progressSource` | `{trigger, property, ...}` | `{-1, ""}` | which trigger/state field drives progress. `-1` = automatic. Longer tuples of the form `{trigger, type, property, total, modRate, inverse, paused, remaining}` are produced by `Private.GetProgressSourceFor`; `{-1, ""}` is always safe. |
| `adjustedMin` / `adjustedMax` | **string** | `""` | only honoured when `useAdjustededMin`/`useAdjustededMax` are true. Parsed by `AddMinMaxProgressSource`: a `"NN%"` string becomes a relative percentage, otherwise `tonumber()`. **They are strings, not numbers** — emitting a number here will be replaced by the default by `Private.validate` (type mismatch, §9.1). |
| `frameStrata` | number | 1 | `1` = inherit parent's strata; otherwise an index into `Private.frame_strata_types`. |

`properties` (valid condition `property` strings for `icon`): `desaturate`,
`width`, `height`, `color`, `inverse`, `cooldownSwipe`, `cooldownEdge`,
`cooldownTextDisabled`, `zoom`, `iconSource`, `displayIcon`, plus everything
`Private.regionPrototype.AddProperties` injects (`alpha`, `xOffset`, `yOffset`,
`sub.N.*` for each subregion — see §6).

`validate` for `icon` is `Private.EnforceSubregionExists(data, "subbackground")` —
see §9.2.

---

## 5. `uid` vs `id` on import

Import entry point: `WeakAuras.Import` (`WeakAuras/Transmission.lua:534`) →
`ImportNow` → `OptionsPrivate.OpenUpdate` →
`WeakAurasOptions/OptionsFrames/Update.lua`.

### 5.1 Payload shape

`Private.DisplayToString` (`Transmission.lua:356`):

```lua
local version = 1421
for child in Private.TraverseSubGroups(data) do version = 2000 break end
local transmit = { m = "d", d = CompressDisplay(data, version), v = version, s = versionString }
if data.controlledChildren then
  transmit.c = {}
  for child in Private.TraverseAllChildren(data) do   -- FLAT, depth-first, ALL descendants
    ... transmit.c[index] = CompressDisplay(child, version) ...
  end
end
```

- `d` = root aura table. `c` = **flat array of every descendant** (not just
  direct children), depth-first.
- `v = 1421` when the tree is one level deep, `v = 2000` when there are nested
  sub-groups.
- `v >= 2000` strips `Private.non_transmissable_fields_v2000` =
  `{authorMode, skipWagoUpdate, ignoreWagoUpdate, preferToUpdate, information.saved}`
  — i.e. **`parent` and `controlledChildren` ARE transmitted**.
- `v = 1421` strips `Private.non_transmissable_fields` which additionally
  removes `controlledChildren` and `parent`; the importer rebuilds them by array
  order (`Transmission.lua:571`).

⇒ **Emit `v = 2000` and always carry explicit `parent` + `controlledChildren`.**
That is what you are already doing and it is correct.

`CompressDisplay` also sets `copiedData.tocversion = WeakAuras.BuildInfo`, so
`tocversion = 30300` on this client.

### 5.2 The exact match rule

`MatchInfo` (`Update.lua:1230`):

```lua
if not data.uid then return nil, "Import has no UID, cannot be matched to existing auras." end
for _, child in ipairs(children) do
  if not child.uid then return nil, "Import has no UID, ..." end
end
...
target = OptionsPrivate.Private.GetDataByUID(data.uid)
if target and hasChildren(data) ~= hasChildren(target) then target = nil end
if not target then return nil end   -- ⇒ fresh import
```

**CONFIRMED rule:**

1. Every aura in the payload (root and every child) **must** have a `uid`, or
   matching is refused outright.
2. WA looks up **only the ROOT's `uid`** via `GetDataByUID`. Child uids are used
   afterwards to align the trees (`BuildMatches` → `MatchChild`: a child matches
   iff the *same uid* exists in the installed tree).
3. If the root uid resolves to an installed aura **and** both are groups (or
   both are not) ⇒ **UPDATE path** (the "you already have this aura" dialog).
4. Otherwise ⇒ **fresh IMPORT path**.
5. `id` plays **no part** in matching. It only affects naming.

Two further gates that turn an update into an error:

- `CheckForChangedRegionTypes` — if a matched uid changed `regionType` between
  group and non-group forms: `"Incompatible changes to group region types detected"`.
- `CheckForIncompatibleStructures` — `"Incompatible changes to group structure detected"`.

### 5.3 Why re-importing with the same uids looked like a silent no-op

This is the important bit and it is **not** what it looks like.

`Private.update_categories` (`WeakAuras/Types.lua:3826`) — the update dialog
applies a diff **per category**, and each category has a `default` checkbox
state:

| Category | Fields | `default` |
|---|---|---|
| `anchor` — "Size & Position" | `xOffset`, `yOffset`, `selfPoint`, `anchorPoint`, `anchorFrameType`, `anchorFrameFrame`, `frameStrata`, `height`, `width`, `fontSize`, `scale` | **`false`** |
| `userconfig` | `config` | **`false`** |
| `name` | `id` | true |
| `display` | *(everything not listed elsewhere)* | true |
| `trigger` | `triggers` | true |
| `conditions` | `conditions` | true |
| `load` | `load` | true |
| `action` | `actions` | true |
| `animation` | `animation` | true |
| `authoroptions` | `authorOptions` | true |
| `arrangement` — "Group Arrangement" | `grow`, `space`, `stagger`, `sort`, `hybridPosition`, `radius`, `align`, `rotation`, `constantFactor`, `hybridSortMode` | true |
| `oldchildren` | — | true (remove obsolete auras) |
| `newchildren` | — | true (add missing auras) |
| `metadata` | `url`, `desc`, `version`, `semver`, `wagoID` | true |

And `FieldToCategory(field, isRoot)`:

```lua
if category == nil then category = "display" end
-- For child auras, anchor fields are arrangement
if not isRoot and category == "anchor" then category = "arrangement" end
```

**CONFIRMED consequences:**

- On an update, **the ROOT aura's `xOffset`/`yOffset`/`width`/`height`/`scale`/
  `anchorFrameType` changes are NOT applied unless the user ticks "Size &
  Position"**, which is off by default. Move the whole pack in your generator
  and re-import — nothing moves.
- For **child** auras those same fields are reclassified into `arrangement`,
  which defaults **on** — so child geometry does update.
- Fields in `Private.internal_fields` are excluded from the diff entirely:
  `uid`, `internalVersion`, `sortHybridTable`, `tocversion`, `parent`,
  `controlledChildren`, `source`. So bumping `internalVersion` or `tocversion`
  never registers as a change.
- If the computed diff is empty across all active categories, the dialog offers
  nothing to do — the "silent no-op".

### 5.4 The fresh-import path (what happens to ids)

`ImportPhase1` / `ImportPhase2` (`Update.lua:2084`, `2110`):

```lua
ImportPhase1 = function(self, uidMap, uid, phase2Order)
  local data = uidMap:GetPhase1Data(uid)
  local newId = OptionsPrivate.Private.FindUnusedId(data.id)   -- "Foo", "Foo 2", "Foo 3"...
  uidMap:ChangeId(uid, newId)
  data.id = newId
  WeakAuras.Add(data)
  ...
```

`GetPhase2Data` then rewrites `parent` and `controlledChildren` **from the uid
graph**, using the post-rename ids. So **id collisions with already-installed
auras are handled correctly and automatically** — WA renames and keeps
parent/child links consistent. You do not need globally unique ids.

### 5.5 Uniqueness rules you MUST satisfy inside one payload

`BuildUidMap` (`Update.lua:293`):

```lua
local idToUid = {}
idToUid[data.id] = data.uid
for i, child in ipairs(children) do
  if idToUid[child.id] then
    error("Duplicate id in import data: "..child.id)     -- ← HARD ERROR
  end
  idToUid[child.id] = child.uid
end
...
uidMap.map[data.uid] = { originalName = data.id, id = data.id, data = data }
...
for i, id in ipairs(data.controlledChildren) do
  tinsert(uidChildren, idToUid[id])        -- unknown id ⇒ nil ⇒ silently dropped
end
```

| Constraint | Violation effect |
|---|---|
| `id` unique **within the payload** | **Lua error**: `Duplicate id in import data: <id>`. Import aborts. |
| `uid` unique **within the payload** | `uidMap.map[uid]` is silently overwritten — the earlier aura vanishes from the tree; may then error in `handleSortHybridTable` (`uidMap.map[childUid].sortHybrid` on nil). |
| every entry of `controlledChildren` present in the payload | `idToUid[id]` is nil ⇒ dropped from the group's child list ⇒ child imports but is never laid out (§1.4). |
| every child's `parent` present in the payload | `map[uid].parent = nil` ⇒ child is treated as another root. |
| root has **no** `parent` key | otherwise it is treated as a child of a nonexistent aura. |

Note `DisplayToString` de-duplicates uids on **export** from the installed DB,
but there is no equivalent de-dup on **import** — a generator must guarantee it.

### 5.6 Practical recipe for a rebuildable pack

- Generate `uid` as an 11-character base64 string (`WeakAuras.GenerateUniqueID`,
  `Transmission.lua:97`, alphabet `a-zA-Z0-9()`). Any 11-char string works; the
  charset is not validated.
- **To ship a genuinely new build:** change the root `uid` (salt it with the
  build version). WA finds no match and takes the clean import path, renaming
  ids as needed. The user ends up with both packs and can delete the old one.
- **To ship an in-place update:** keep uids stable, and tell the user to tick
  **"Size & Position"** in the update dialog, or the layout will not move.
- Keep an always-visible version stamp in the pack. (You already do this; it is
  the right call given §5.3.)

---

## 6. `conditions` schema

`WeakAuras/Conditions.lua` + `WeakAurasOptions/ConditionOptions.lua`.

### 6.1 Shape

The in-repo authoritative comment (`ConditionOptions.lua:13-46`):

```
-- [] Index
--    - check
--      - trigger: Trigger number. Negative values indicate a special check:
--          -1: Global conditions
--          -2: Combinator
--      - variable: Variable inside the trigger state to check
--      - op: Operator to use for check
--      - value: Value to check
--      - checks: Sub Checks for Combinations, each containing trigger, variable, op, value or checks
--    - changes
--      [] Index
--         - property: Property that is changed
--         - value: New value
```

```lua
data.conditions = {
  { check = { trigger = 2, variable = "show", value = 1 },
    changes = { { property = "desaturate", value = true },
                { property = "sub.3.glow", value = true } },
    linked = false },
  ...
}
```

- `linked = true` makes condition N an **`elseif`** of condition N-1
  (`Conditions.lua:473-477`). Always false/absent on `conditions[1]`.
- `references`, `referenceCount`, `samevalue`, `sameop` are **options-UI-only
  merge artefacts** — never read at runtime. Do not emit them.
- **There is no `disjunctive` field on conditions.** AND/OR is expressed with the
  combinator (below). `disjunctive` belongs to `data.triggers` (§6.7).

### 6.2 `check.trigger`

| Value | Meaning |
|---|---|
| `1 .. #data.triggers` | that trigger's state (`region.states[N]`) |
| `-1` | **global conditions** (`Private.GetGlobalConditions()`) |
| `-2` | **combinator** (AND / OR) |
| `0` | never valid — skipped by the options builder |

**Combinator gotcha (CONFIRMED):** the runtime dispatches AND/OR on
`check.variable` (`Conditions.lua:234`), but global-condition event registration
dispatches on `check.trigger == -2` (`Conditions.lua:955`). Emit **both**
`trigger = -2` and `variable = "AND"|"OR"`, with the operands in
`check.checks = { <check>, <check>, ... }` (recursive, same schema). The options
UI caps visible nesting at 3 levels; the runtime recursion is unbounded.

### 6.3 Universally available `check.variable`s

**On every positive trigger index, regardless of trigger system**
(`Private.GetTriggerConditions`, `WeakAuras.lua:4141-4176`):

| variable | type | notes |
|---|---|---|
| `show` | `bool` | "Active". `value` is the **number** `1` (true) or `0` (false). **This is the only variable guaranteed for every trigger type — your existing use of it is correct.** |
| `activationTime` | `elapsedTimer` | seconds since the trigger activated; `operator_types = "without_equal"` (only `>=` / `<=`) |

**Global (`trigger = -1`)** (`Conditions.lua:701-745`):
`incombat` (bool), `hastarget` (bool), `attackabletarget` (bool),
`rangecheck` (range), `customcheck` (customcheck), `alwaystrue` (alwaystrue).

**Per trigger system, additionally:**

- **`aura2`** (`BuffTrigger2.lua:3537-3666`) — always: `debuffClass` (select),
  `unitCaster` (string), `nameCaster` (string, no operator), `expirationTime`
  (timer), `duration` (number), `stacks` (number), `name` (string), `spellId`
  (number, `==`/`~=` only), `matchCount`, `matchCountPerUnit`, `unitCount`,
  `totalStacks` (all number). Conditional: `maxUnitCount` (if
  `unit ~= "multi"`), `buffed` (bool — only when `matchesShowOn == "showAlways"`
  on a non-group trigger, or the group+`combinePerUnit` case),
  `tooltip1..tooltip4` (only with `fetchTooltip`), `stackGainTime`,
  `stackLostTime`, `initialTime`, `refreshTime` (elapsedTimer, if
  `unit ~= "multi"`).
  ⚠️ **`aura2` has NO `unit`, `icon`, `value` or `total` condition variables.**
- **Generic triggers** (`GenericTrigger.lua:4921-5060`) — derived from the
  prototype: `expirationTime` + `duration` + `paused` when
  `progressType == "timed"`; `value` + `total` when `"static"`; `stacks` if the
  prototype has a `stacksFunc`; `name` if it has a `nameFunc`; `itemInRange` if
  `hasItemID`; `count` if `countEvents`; **plus every prototype arg that has all
  three of `conditionType`, `name`, `display` and passes its `enable` check.**
  For `Cooldown Progress (Spell)` that adds `charges`, `spellCount`, `stacks`,
  `maxCharges`, `readyTime`, `chargeGainTime`, `chargeLostTime`,
  `effectiveSpellId`, `gcdCooldown`, `onCooldown`, `spellUsable`,
  `insufficientResources`, `spellInRange`.

  ⚠️ **`effectiveSpellId` IS NOT AN OVERRIDE LOOKUP ON THIS FORK — CONFIRMED
  AGAINST SOURCE.** `Prototypes.lua:3806` reads, in full:

  ```lua
  local effectiveSpellId = spellname
  ```

  It is the id you typed, verbatim. Upstream WeakAuras resolves spell overrides
  into this variable; **the Ascension fork does not** — `ignoreoverride` does
  not appear anywhere in its `Prototypes.lua`, and there is no
  `use_ignoreoverride` option. So `effectiveSpellId == <some other spell>` can
  never be true, and a condition written that way fires never, silently.

  This cost two shipped Runemaster releases (1.5, 1.6). The list above was
  transcribed from upstream and is right about the NAMES but wrong about what
  one of them MEANS here. `use_ignoreSpellKnown` (`Prototypes.lua:3986`) is
  real; `use_ignoreoverride` is not.

  **There is no override API to reach for either** — `FindSpellOverrideByID` is
  Cataclysm-era and this is a 3.3.5 client, so the retail habit of tracking a
  transformed spell that way (Condemn replacing Execute, Lava Beam replacing
  Chain Lightning) does not port. To track "this button became another spell",
  use `["Spell Known"]` (`Prototypes.lua:8253`) on the REPLACEMENT's id: with
  no override system, a 3.3.5 server makes a button change by granting the new
  spell and taking the base away.
  ⚠️ That prototype takes a **number** — `:8271` is
  `type(trigger.spellName) == "number" and trigger.spellName or 0`, so a string
  id silently becomes spell 0.
- **Custom / TSU triggers** — `stateupdate` triggers declare their own via
  `Private.GetTsuConditionVariablesExpanded`.

### 6.4 `op` and `value` encoding per condition type

`Private.operator_types` = `== ~= > < >= <=`;
`equality_operator_types` = `== ~=`;
`operator_types_without_equal` = `>= <=`;
`string_operator_types` = `==` ("Is Exactly"), `find('%s')` ("Contains"),
`match('%s')` ("Matches (Pattern)").

| Condition type | valid `op` | `value` |
|---|---|---|
| `number` | `operator_types` (or `without_equal` / `only_equal` per the template) | numeric **string**; runtime does `tonumber(value)` |
| `timer` | same | numeric string, **inlined raw into generated Lua** |
| `elapsedTimer` | same | numeric string, **inlined raw** |
| `bool` | **no `op` key at all** | number **`0`** or **`1`** — not a Lua boolean |
| `select` | `==` / `~=` only | key from the template's `values` (number or string); non-numeric values are single-quoted with **no escaping** |
| `unit` | `==` / `~=` only | key from `values`, or `"member"` + a free-text unit |
| `string` | `string_operator_types` (or none if `operator_types == "none"`) | string; safely `%q`-escaped |
| `range` | `op` (count) + `op_range` (yards) | `value` = count string, `range` = yards string, `type` = `"group"` \| `"enemies"` |
| `customcheck` | `op` is repurposed as a **space-separated event list** (e.g. `"UNIT_HEALTH:player PLAYER_REGEN_ENABLED"`) | `value` = Lua source, loaded as `"return " .. value` |
| `alwaystrue` / `combination` | none | none |

### 6.5 Valid `changes[].property` strings

Resolved from `Private.GetProperties(data)`:
`Private.regionTypes[data.regionType].properties` (a table, or a
`function(data)` for `icon`/`aurabar`), plus sub-region properties namespaced as

```lua
properties["sub." .. index .. "." .. key] = property        -- Conditions.lua:637
```

so the string form is **`"sub.<1-based subRegions index>.<propertyKey>"`**, e.g.
`"sub.3.glow"`, `"sub.2.text_color"`. Parsed by
`string.match(property, "^sub%.(%d*).(.*)")` and dispatched as
`region.subRegions[N]:<setter>(...)`.

**There is no `subo.` prefix** — the 4-part `sub.N.<type>.<option>` form exists
only in the options tree, never in `changes[].property`.

Universally present on every region (from
`Private.regionPrototype.AddProperties`): `alpha`, `xOffsetRelative`,
`yOffsetRelative`, `sound`, `chat`, `customcode`, `glowexternal`, plus
`progressSource` / `adjustedMin` / `adjustedMax` if the region default has
`progressSource`. Per-region lists are in §4 (icon), §7.4 (aurabar), §8
(texture), §8A (sub-regions).

Two kinds of property:
- **`setter`** properties are applied on activation and **reverted to the base
  value on deactivation**.
- **`action`** properties (`sound`, `chat`, `customcode`, `glowexternal`) fire
  once on activation and are **never reverted**.

Value encoding follows the property's declared type: `bool` ⇒ Lua boolean,
`number` ⇒ number, `string`/`texture`/`list`/`icon`/`textureLSM` ⇒ string or
number, `color` ⇒ `{r,g,b,a}`.

### 6.6 What happens on invalid input — CONFIRMED

| Mistake | Result |
|---|---|
| Unknown / misspelled `changes[].property` | **Silently ignored.** Every consumer is guarded (`if propertyData and propertyData.type ...`, `Conditions.lua:525` and `:555`). Other changes in the same condition still apply. No error. |
| `sub.N.*` pointing at a non-existent sub-region | same — silently ignored |
| Unknown `check.variable`, or `check.trigger` out of range | The generated check falls through to `check = "false"` (`Conditions.lua:470-472`). **The condition simply never activates.** No error, no breakage; the deactivate branch still restores the base value. |
| **Malformed `value` on a `timer` / `elapsedTimer` / `select` condition** | ⚠️ **BREAKS EVERY CONDITION ON THAT AURA.** These types concatenate `value` *raw* (or single-quote it with no escaping) into the generated Lua source. A syntax error makes `loadstring` fail, `Private.LoadConditionFunction` stores nil, and the whole aura's condition function is dead. Always emit numeric condition values as clean numeric strings. |
| A `timer`-typed variable that is not also a progress source | `Conditions.lua:274` indexes `progressSource[8]` without a nil guard ⇒ Lua error out of `ConstructConditionFunction`. Unreachable with stock trigger data, reachable with hand-authored checks. |

There is **no runtime validator** for condition types — only the options UI
checks anything.

### 6.7 `data.triggers` — related shape notes

```lua
data.triggers = {
  [1] = { trigger = {...}, untrigger = {} },
  [2] = { trigger = {...}, untrigger = {} },
  activeTriggerMode  = -10,          -- non-array key on the same table
  disjunctive        = "any" | "all" | "custom",
  customTriggerLogic = "<lua source>",   -- only when disjunctive == "custom"
}
```

- `activeTriggerMode`: `-10` (`Private.trigger_modes.first_active` — "first
  active trigger drives the display") or a positive integer pinning the display
  to that trigger. `nil` or `> #data.triggers` is coerced to `-10` on
  `WeakAuras.Add`.
- `disjunctive`: defaults to `"all"` when absent — i.e. **an aura with two
  triggers and no `disjunctive` shows only when BOTH are active.** If you want
  "any of these", you must set `disjunctive = "any"` explicitly. (Note: while
  the options window is open WA ignores this and uses `triggerCount > 0`, so
  behaviour differs between the config UI and live play.)
- Every entry needs both `trigger` and `untrigger` tables, even if `untrigger`
  is empty.

### 6.8 Valid `trigger.type` values — CORRECTION

**`Private.trigger_types` does not exist in this version.** The set is built at
load time as `WeakAuras.genericTriggerTypes ∪ {"aura2"}`, where
`genericTriggerTypes = {"custom"} ∪ keys(Private.category_event_prototype)`.

> Complete valid set: **`"aura2"`, `"custom"`, `"spell"`, `"item"`, `"unit"`,
> `"addons"`, `"combatlog"`, `"event"`.**

`"status"` and `"event"` as *trigger modes* are `trigger.custom_type`
(`"event"` / `"status"` / `"stateupdate"`), **not** `trigger.type`. The old
`"aura"` (BuffTrigger v1) type is no longer registered.

Prototype lookup (`GenericTrigger.lua:4531-4537`) needs **both** keys:

```lua
if trigger.type and trigger.event then
  if Private.category_event_prototype[trigger.type] then
    return Private.event_prototypes[trigger.event]
  end
end
```

`type` is only a category gate; the prototype is keyed purely by `event`, which
is the English display name (`"Cooldown Progress (Spell)"`, `"Health"`,
`"Power"`, `"Weapon Enchant"`, …).

### 6.9 `Cooldown Progress (Spell)` — required fields

Minimal working trigger:

```lua
{ type = "spell", event = "Cooldown Progress (Spell)",
  spellName = 12345, genericShowOn = "showOnCooldown", track = "auto" }
```

| Field | Notes |
|---|---|
| `spellName` | `required = true`, so `use_spellName` is **not** needed at runtime (the options UI writes it anyway). A **number** is used as a spellId directly; a string is resolved via `GetSpellInfo`. Prefer numeric spell IDs. |
| `use_exact_spellName` | boolean. ⚠️ **This is the correct field name** — the `showExactOption` machinery reads `trigger["use_exact_" .. name]`. `useExactSpellId` is an **`aura2`** field and does nothing here. |
| `realSpellName` | ⚠️ **Dead field.** Declared only as a LuaLS annotation (`Init.lua:170`); zero code references. Do not emit. |
| `genericShowOn` | `"showOnCooldown"` \| `"showOnReady"` \| `"showAlways"`. ⚠️ **NO runtime default.** If absent or invalid, `showOnCheck = "false"` and **the trigger can never fire.** The `default = "showOnCooldown"` is applied only lazily by the options panel, never by `WeakAuras.Add`. **Always emit it explicitly.** `use_genericShowOn` is irrelevant at runtime. |
| `track` | `"auto"` \| `"charges"` \| `"cooldown"`. Safely defaults to `"auto"`; `use_track` is not consulted. |
| other `use_*` | plain booleans read directly: `use_showgcd`, `use_showlossofcontrol`, `use_ignoreoverride` (inverted), `use_matchedRune`, `use_ignoreSpellKnown`, `use_trackcharge` + `trackcharge`, `use_remaining` + `remaining`. |

### 6.10 `aura2` — required fields

`BuffTrigger.Add` defaults `trigger.unit = trigger.unit or "player"` and
`trigger.debuffType = trigger.debuffType or "HELPFUL"`.

| Field | Required? | Notes |
|---|---|---|
| `type = "aura2"` | **YES** | exact string; without it the trigger is skipped entirely |
| `unit` | no (defaults `"player"`) | `player group raid party boss arena nameplate pet member multi` + target-unit types. `member` needs `specificUnit`. |
| `debuffType` | no (defaults `"HELPFUL"`) | `"HELPFUL"` \| `"HARMFUL"` \| `"BOTH"` |
| `useName` + `auranames` | effectively yes | names are built **only** `if trigger.useName and trigger.auranames`. `auranames` is an array of strings; numeric entries are resolved to names via `GetSpellName`. **With neither `auranames` nor `auraspellids`, the trigger matches EVERY aura of that `debuffType` on the unit.** |
| `useExactSpellId` + `auraspellids` | no | array of spellId **strings**; empty/non-numeric entries dropped |
| `matchesShowOn` | no (defaults `"showOnActive"`) | non-group triggers only: `"showOnActive"` \| `"showOnMissing"` \| `"showAlways"` \| `"showOnMatches"` |
| `ownOnly` | no, **tri-state** | `true` = caster must be you/pet/vehicle; `false` = must NOT be; **`nil` = no caster check.** Emitting `false` is not the same as omitting it. |
| `useMatch_count` + `match_count` + `match_countOperator` | all three together | `match_count` must `tonumber()` |
| `useStacks` + `stacks` + `stacksOperator` | no | `stacksOperator` defaults `">="`, `stacks` defaults `0`; **`stacks` is compared via `tonumber`, so a string is fine** |
| `fetchTooltip` | no | gates `tooltip1..4` condition variables |
| `combineMatches` | ⚠️ **not a live field** | legacy-converter output only. The live field is **`combineMode`**: `"showLowest"` (default) \| `"showHighest"` \| `"showLowestSpellId"` \| `"showHighestSpellId"`. |

---

## 7. `aurabar` region

`WeakAuras/RegionTypes/AuraBar.lua`. The Ascension fork's default table is
**identical** to upstream 5.21.2 (verified line-by-line):

```lua
icon = false, desaturate = false, iconSource = -1, progressSource = {-1, ""},
adjustedMax = "", adjustedMin = "",
texture = "Blizzard", textureSource = "LSM",
width = 200, height = 15,
orientation = "HORIZONTAL", inverse = false,
barColor = {1,0,0,1}, barColor2 = {1,1,0,1},
enableGradient = false, gradientOrientation = "HORIZONTAL",
backgroundColor = {0,0,0,0.5},
spark = false, sparkWidth = 10, sparkHeight = 30, sparkColor = {1,1,1,1},
sparkTexture = "Interface\\CastingBar\\UI-CastingBar-Spark",
sparkBlendMode = "ADD", sparkOffsetX = 0, sparkOffsetY = 0,
sparkRotationMode = "AUTO", sparkRotation = 0, sparkHidden = "NEVER",
selfPoint = "CENTER", anchorPoint = "CENTER", anchorFrameType = "SCREEN",
xOffset = 0, yOffset = 0,
icon_side = "RIGHT", icon_color = {1,1,1,1},
frameStrata = 1, zoom = 0
```
plus `progressSource = {-1,""}`, `useAdjustededMax = false`,
`useAdjustededMin = false`, `alpha = 1.0`.

### 7.1 Bar fields

| Field | Values | Meaning |
|---|---|---|
| `texture` | **an LSM media NAME**, not a path | Fetched as `SharedMedia:Fetch("statusbar_atlas", texture, true) or SharedMedia:Fetch("statusbar", texture) or ""`. Only used when `textureSource ~= "Picker"`. WA itself registers only `Clean`, `Stripes`, `Thick Stripes`, `Thin Stripes`; LibSharedMedia's own built-ins add `Blizzard` and `Solid`. |
| `textureSource` | `"LSM"` \| `"Picker"` | `"Picker"` makes the bar use the raw string in **`textureInput`** as a literal path instead. |
| `textureInput` | string path | **Not in the default table** — nil unless you set it. Required when `textureSource == "Picker"`. |
| `barColor` | `{r,g,b,a}` | foreground colour (or gradient start). |
| `barColor2` | `{r,g,b,a}` | gradient end; only used when `enableGradient == true`. |
| `enableGradient` | bool | ⚠️ implemented with `Texture:SetGradient(orientation, CreateColor…)`, an 9.x+ API. Treat as retail-only; leave `false` on 3.3.5. |
| `gradientOrientation` | `"HORIZONTAL"` \| `"VERTICAL"` | |
| `backgroundColor` | `{r,g,b,a}` | vertex colour of the bar background, which reuses the *same* statusbar texture. |
| `orientation` | `"HORIZONTAL"` (right→left), `"HORIZONTAL_INVERSE"` (left→right), `"VERTICAL"` (bottom→top), `"VERTICAL_INVERSE"` (top→bottom) | Only these four. Negative scale flips the *effective* orientation. |
| `inverse` | bool | progress becomes `1 - progress` in `SetProgress`. |
| `sparkHidden` | `"NEVER"` \| `"FULL"` \| `"EMPTY"` \| `"BOTH"` | when to hide the spark. Internally forced to `"ALWAYS"` whenever `spark == false` (`bar.spark.sparkHidden = data.spark and data.sparkHidden or "ALWAYS"`). |
| `spark` | bool | master on/off for the spark. |
| `spark*` | `sparkTexture` (raw path), `sparkColor`, `sparkWidth`, `sparkHeight`, `sparkBlendMode` (`ADD`\|`BLEND`), `sparkOffsetX/Y`, `sparkRotationMode` (`AUTO`\|`MANUAL`), `sparkRotation` (only multiples of 90 are meaningful), plus `sparkDesaturate`/`sparkMirror` which are **not in the default table** | |
| `progressSource` | `{trigger, property}` | `{-1, ""}` = automatic. |
| `adjustedMin` / `adjustedMax` | **strings** | gated by `useAdjustededMin` / `useAdjustededMax` (yes, three `d`s). `"25%"` ⇒ relative percentage; otherwise `tonumber()`. |
| `smoothProgress` | bool, **not in default** | uses `SmoothStatusBarMixin`, installs `PreShow = ResetSmoothedValue`. |

### 7.2 Icon fields — and how the icon eats the bar

| Field | Meaning |
|---|---|
| `icon` | **BOOLEAN — "Show Icon".** `region.iconVisible = data.icon` (`AuraBar.lua:1256`). Unlike the `icon` region (where this field is dead), on `aurabar` this genuinely toggles the icon square. |
| `displayIcon` | the icon path/spellID. **Not in the default table** — you must set it. |
| `iconSource` | same semantics as §4.1: `-1` auto, `0` manual (`displayIcon`), `N` = trigger N. |
| `icon_side` | `"LEFT"` \| `"RIGHT"`. For vertical orientations the UI relabels these Top/Bottom but the **stored values are still `LEFT`/`RIGHT`**. |
| `icon_color` | `{r,g,b,a}` vertex colour on the icon. |
| `desaturate` | greyscales the icon. |
| `zoom` | `texWidth = 0.25 * zoom` — note this is a **different formula from the `icon` region** (`1 - 0.5 * zoom`). |
| `useTooltip` | bool, not in default. Tooltip hit area is `SetAllPoints(icon)` — the icon, not the bar. |

**`width`/`height` are the WHOLE region, icon included.** The icon is always
square, `iconsize = min(width, height)`, and `GetRealSize` returns
`totalWidth - iconWidth` for HORIZONTAL when the icon is visible.

⇒ With `width = 270, height = 20, icon = true`, the drawable bar is **250 px**.
If you are lining a bar up with a row of icons, either set `icon = false` or
subtract `min(width,height)` from your target width.

### 7.3 `validate` and subregions

```lua
if data.subRegions then
  for _, s in ipairs(data.subRegions) do
    if s.type == "aurabar_bar" then s.type = "subforeground" end   -- legacy rename
  end
end
Private.EnforceSubregionExists(data, "subforeground")
Private.EnforceSubregionExists(data, "subbackground")
```

⇒ **Emit `subforeground` and `subbackground` yourself** (as `subRegions[1]` and
`[2]`, in that order, to match what the client writes) or your `sub.N.*`
condition indices get shifted by two.

### 7.4 Condition properties for `aurabar`

`textureSource`, `textureInput`, `texture`, `barColor`, `barColor2`,
`gradientOrientation`, `enableGradient`, `icon`, `icon_color`, `iconSource`,
`displayIcon`, `desaturate`, `backgroundColor`, `sparkColor`, `sparkHeight`,
`sparkWidth`, `width`, `height`, `orientation`, `inverse`, plus the prototype
set (`alpha`, `sound`, `chat`, `customcode`, `xOffsetRelative`,
`yOffsetRelative`, `glowexternal`, `progressSource`, `adjustedMin`,
`adjustedMax`) and one `overlays.N` entry per overlay the triggers expose.

Aurabar subregion anchor points (`anchor_point` on a subregion): the 9 standard
points, the 9 `INNER_*` points, the 9 `ICON_*` points, and `SPARK`. The
`anchor_area` field takes `"bar"` \| `"icon"` \| `"fg"` \| `"bg"`.

---

## 8. `texture` region

`WeakAuras/RegionTypes/Texture.lua`. Fork default (identical to upstream):

```lua
texture = "Interface\\Addons\\WeakAuras\\PowerAurasMedia\\Auras\\Aura3",
desaturate = false, width = 200, height = 200, color = {1,1,1,1},
blendMode = "BLEND", textureWrapMode = "CLAMPTOBLACKADDITIVE",
rotation = 0, mirror = false, rotate = false,
selfPoint = "CENTER", anchorPoint = "CENTER", anchorFrameType = "SCREEN",
xOffset = 0, yOffset = 0, frameStrata = 1
```
plus `alpha = 1.0`. **No `progressSource`** on this region type.

| Field | Meaning |
|---|---|
| `texture` | a **raw texture path** (or fileID). NOT an LSM name — contrast with `aurabar.texture`. Upstream routes it through `Private.SetTextureOrAtlas`; **the Ascension fork calls `region.texture:SetTexture(data.texture)` directly** (`Texture.lua:159`) — no atlas support, no wrap-mode arguments. |
| `blendMode` | exactly two values: `"BLEND"` (L["Opaque"]) and `"ADD"` (L["Glow"]). Confirmed in the fork's `Private.blend_types`. |
| `color` | `{r,g,b,a}` vertex colour. This is how you get a solid colour out of a white texture. |
| `rotate` | bool, "Allow Full Rotation". Controls the tex-coord scale factor: `1` when true, `sqrt(2)` when false (zooms out so corners don't clip during rotation). |
| `rotation` | number 0–360 degrees. |
| `mirror` | bool, horizontal flip. |
| `textureWrapMode` | upstream: `"CLAMP"` \| `"MIRROR"` \| `"REPEAT"` \| `"CLAMPTOBLACKADDITIVE"`. **The Ascension fork has no `Private.texture_wrap_types` and never passes wrap modes to `SetTexture` — the field is inert there.** Emit `"CLAMPTOBLACKADDITIVE"` to match the client's own output; it has no effect. |
| `discrete_rotation` | **Does not exist any more.** Removed by Modernize steps `< 60` / `< 61` / `< 63`. Do not emit. |
| `desaturate` | bool. |

Condition properties for `texture`: `texture`, `color`, `desaturate`, `width`,
`height`, `mirror`, `rotation`, plus `alpha`, `sound`, `chat`, `customcode`,
`xOffsetRelative`, `yOffsetRelative`, `glowexternal`.
**`blendMode`, `rotate` and `textureWrapMode` are NOT condition-settable.**

`validate` enforces `subbackground`.

### 8.1 Safe texture paths on a 3.3.5 client

For a plain solid-colour rectangle (the usual "fake status bar" trick), ranked:

1. `Interface\AddOns\WeakAuras\Media\Textures\Square_FullWhite` — ships with the
   addon (`Square_FullWhite.tga`), fully opaque white, already registered by WA
   as the LSM border media `"Square Full White"`. Guaranteed present because the
   addon itself installs it. **Best choice.**
2. `Interface\Buttons\WHITE8X8` — Blizzard's canonical 8×8 opaque white; present
   on every client including 3.3.5.
3. `Interface\ChatFrame\ChatFrameBackground` — also solid white and present on
   all clients; used by AceGUI inside WA's own options.

Avoid: anything resolved through `SetAtlas` (atlases do not exist on 3.3.5), and
the `statusbar_atlas` LSM entries WA registers from `PowerBarColor` (retail only,
guarded by `if PowerBarColor then`).

Other shipped shapes in `WeakAuras/Media/Textures/` you can rely on:
`Square_White`, `Square_White_Border`, `Circle_White`, `Circle_White_Border`,
`Square_Smooth*`, `Circle_Smooth*`, `Ring_*px`, `square_border_1px/5px/10px`,
`Triangle45`, `Trapezoid`, `Square_AlphaGradient`, `Statusbar_Clean`,
`Statusbar_Stripes{,_Thick,_Thin}`, `Border_DropShadow`.

---

## 8A. Sub-regions

`WeakAuras/SubRegionTypes/`. Sub-regions live in `data.subRegions`, an ordered
array of `{ type = "<subtype>", ... }` tables. Their index is what `sub.N.*`
condition properties address.

**The Ascension fork ships exactly these files:** `Background.lua`,
`Border.lua`, `Glow.lua`, `Model.lua`, `StopMotion.lua`, `SubText.lua`,
`Texture.lua`, `Tick.lua` ⇒ types `subbackground`, `subforeground`, `subborder`,
`subglow`, `subtext`, `subtexture`, `submodel`, `substopmotion`, `subtick`.
Upstream additionally has `subcirculartexture` and `sublineartexture` —
**those two do not exist on the fork; emitting them prints
`"ERROR in '%s' unknown or incompatible sub element type '%s'"`.**

| Type | `supports(regionType)` | User-addable |
|---|---|---|
| `subbackground` | everything except `group`/`dynamicgroup` | no (auto-injected) |
| `subforeground` | `aurabar` only | no (auto-injected) |
| `subborder` | `texture`, `progresstexture`, `icon`, `aurabar`, `empty` | yes |
| `subglow` | `icon`, `aurabar`, `texture`, `progresstexture`, `empty` | yes |
| `subtext` | `texture`, `progresstexture`, `icon`, `aurabar`, `empty` | yes |
| `subtexture`, `submodel`, `substopmotion` | those 5 plus `text` | yes |
| `subtick` | `aurabar` only | yes |

### 8A.1 `subbackground` / `subforeground`

`default = {}`, `properties = {}`. They are **not visual objects** — `subCreate`
returns a plain Lua table `{ Update = noop, SetFrameLevel = ... }` that forwards
`SetFrameLevel` to the parent region (or, for `subforeground`, to `parent.bar`
and `parent.iconFrame`). Their only job is to occupy a z-order slot in the
subregion stack. There are **no `sub.N.*` properties on them.**

### 8A.2 `subborder`

```lua
border_visible = true, border_color = {1,1,1,1},
border_edge = "Square Full White",     -- LSM "border" media NAME
border_offset = 0, border_size = 2,
-- aurabar parents additionally get: anchor_area = "bar"
```
Drawn as a `SetBackdrop{ edgeFile = LSM:Fetch("border", border_edge), edgeSize = border_size }`
with `SetBackdropColor(0,0,0,0)` — outline only, no fill.

Condition properties: **only `border_visible` (bool) and `border_color` (color)**.
`border_edge`, `border_size` and `border_offset` are not condition-settable.

`border_edge` must be an LSM `border` media name. WA registers only
`"Square Full White"` and `"Drop Shadow"`; Blizzard/Ace supply `"Blizzard Tooltip"`,
`"Blizzard Dialog"`, `"None"`, etc. `"Square Full White"` + a dark
`border_color` + `border_size = 1..2` gives the thin flat outline compact packs use.

### 8A.3 `subglow`

```lua
glow = false, useGlowColor = false, glowColor = {1,1,1,1},
glowType = "buttonOverlay",   -- "Pixel" when the parent is an aurabar
glowLines = 8, glowFrequency = 0.25, glowDuration = 1,
glowLength = 10, glowThickness = 1, glowScale = 1,
glowBorder = false, glowXOffset = 0, glowYOffset = 0,
-- aurabar parents additionally get: anchor_area = "bar"
```
(`glowStartAnim` is read by `modify` but is **not** in the default ⇒ nil.)

`glowType` values on the fork (`Private.glow_types`): `"ACShine"`, `"Pixel"`,
`"buttonOverlay"`, `"Proc"` — **all four present on the Ascension fork**
(upstream gates `Proc` behind TBC/Mists/Retail).

Condition properties: `glow`, `glowType`, `useGlowColor`, `glowColor`,
`glowLines`, `glowFrequency`, `glowDuration`, `glowLength`, `glowThickness`,
`glowScale`, `glowBorder`, `glowXOffset`, `glowYOffset`, `glowStartAnim`.
`glow` is the `defaultProperty`.

### 8A.4 `subtext`

Default depends on parent type. For `parentType == "icon"`:

```lua
text_text = "%p", text_color = {1,1,1,1}, text_font = <default LSM font name>,
text_fontSize = <default>, text_fontType = "OUTLINE", text_visible = true,
text_justify = "CENTER", text_selfPoint = "AUTO", anchor_point = "CENTER",
anchorXOffset = 0, anchorYOffset = 0,
text_shadowColor = {0,0,0,1}, text_shadowXOffset = 0, text_shadowYOffset = 0,
text_automaticWidth = "Auto", text_fixedWidth = 64, text_wordWrap = "WordWrap"
```

For every other parent: `text_text = "%n"`, `text_fontType = "None"`,
`anchor_point = "INNER_RIGHT"` on `aurabar` / `"BOTTOMLEFT"` elsewhere,
`text_shadowXOffset = 1`, `text_shadowYOffset = -1`.

`text_font` is an **LSM `font` media name**, with fallback to `STANDARD_TEXT_FONT`.

⚠️ **Name mismatch (CONFIRMED):** the data fields are `anchorXOffset` /
`anchorYOffset`, but the *condition property* strings are
**`text_anchorXOffset` / `text_anchorYOffset`**. Both spellings exist in the
file and they are not interchangeable.

Condition properties: `text_visible` (defaultProperty), `text_text`,
`text_color`, `text_fontSize`, `text_anchorXOffset`, `text_anchorYOffset`.
Everything else (`text_font`, `text_fontType`, `text_justify`, `anchor_point`,
`text_selfPoint`, `text_shadow*`, `text_automaticWidth`, `text_fixedWidth`,
`text_wordWrap`) is **not** condition-settable.

---

## 8B. Ascension fork deltas vs upstream — CONFIRMED

Verified by cloning `https://github.com/Ascension-Addons/WeakAuras-Ascension`
(fork of `NoM0Re/WeakAuras-WotLK`; `## Interface: 30300`, `## Version: 5.21.2`,
HEAD `2026-02-17`).

⚠️ **The public fork repo is BEHIND the shipped CoA client.** Public repo has
`local internalVersion = 86`; your client's exports carry `89.5`. Since
`Modernize` ends with
`data.internalVersion = max(data.internalVersion or 0, WeakAuras.InternalVersion())`,
an export carrying `89.5` proves the shipped client's `InternalVersion()` is
`89.5`. **Trust the client's own export over this repo**, and re-verify any
fork delta below against a fresh in-game export before relying on it.

| Area | Upstream 5.21.2 | Ascension fork (master, iv 86) |
|---|---|---|
| `internalVersion` | 88 | **86** (shipped client: **89.5**) |
| Encode prefix / codec | `!WA:2!`, LibSerialize + LibDeflate L9 | **identical** |
| `non_transmissable_fields` / `_v2000` | — | **byte-identical** |
| dyngroup-child anchor bypass (`RegionPrototype.lua:828`) | present | **present, identical code** |
| `region:SetOffset(data.xOffset…)` before the bypass (`:818`) | present | **present** |
| group/trigger load skip (`if data and not data.controlledChildren`) | present | **present** |
| `update_categories.anchor.default` | `false` | **`false`** |
| `anchor_frame_types` | includes `PRD` | **no `PRD`** (`SCREEN UIPARENT MOUSE SELECTFRAME UNITFRAME NAMEPLATE CUSTOM`) |
| `anchor_frame_types_group` | includes `PRD` | **no `PRD`** (`SCREEN UIPARENT MOUSE SELECTFRAME CUSTOM`) |
| `group` / `dynamicgroup` default | no `sharedFrameLevel` | **`sharedFrameLevel = true`** on BOTH, with the comment `-- true to ensure identical behavior on newer clients` |
| icon texture resolution | `Private.SetTextureOrAtlas` (atlas-aware) | **`Private.SetTextureOrSpellTexture`** — `if tonumber(path) then texture:SetTexture(select(3, GetSpellInfo(spellID)) or spellID)` ⇒ **`displayIcon` may be a numeric spell ID** and WA resolves the spell's icon for you |
| icon `default` cooldown fields | `cooldown`, `cooldownSwipe`, `cooldownEdge`, `cooldownTextDisabled`, `useCooldownModRate` | **only `cooldown` and `cooldownEdge`** — `cooldownSwipe`, `cooldownTextDisabled`, `useCooldownModRate` do not exist in `default`, in `properties`, or anywhere in `Icon.lua` |
| icon condition properties | 11 entries | **9** — no `cooldownSwipe`, no `cooldownTextDisabled` |
| `Private.texture_wrap_types` | 4 values | **does not exist**; `Texture.lua` calls `SetTexture(data.texture)` with no wrap args ⇒ `textureWrapMode` is inert |
| sub-region types | +`subcirculartexture`, `sublineartexture` | **absent** — 9 types only |
| `glow_types` | `Proc` gated to TBC/Mists/Retail | **all four unconditionally**, incl. `Proc` |
| `Types_*.lua` | per-expansion | fork adds **`Types_ClassicPlus.lua`** with Ascension-specific trigger prototypes (not audited here) |

**Practical implications:**

- Never emit `anchorFrameType = "PRD"`.
- Emit `sharedFrameLevel = true` on groups and dynamicgroups (the client's own
  exports do).
- `displayIcon` can be `"802630"` (a spell ID string) — the fork resolves it via
  `GetSpellInfo`. This is a genuinely useful fork feature for id-driven packs.
- `cooldownSwipe = true` / `cooldownTextDisabled = false` / `useCooldownModRate = true`
  on an `icon` are **write-only noise on this fork**: never read, and they add
  spurious entries to the `display` diff category on re-import. In particular
  **you cannot suppress Blizzard's cooldown countdown text via
  `cooldownTextDisabled`** — verify against the shipped 89.5 client before
  relying on either behaviour.
- `enableGradient` on `aurabar` and anything atlas-based will not work on 3.3.5.

---

## 9. Required fields, silent misbehaviour, and `internalVersion`

### 9.1 `Private.validate` — how defaults are filled, and its one sharp edge

`WeakAuras.lua:417`:

```lua
function Private.validate(input, default)
  for field, defaultValue in pairs(default) do
    if(type(defaultValue) == "table" and type(input[field]) ~= "table") then
      input[field] = {};
    elseif(input[field] == nil) or (type(input[field]) ~= type(defaultValue)) then
      input[field] = defaultValue;
    end
    if(type(input[field]) == "table") then
      Private.validate(input[field], defaultValue);
    end
  end
end
```

- **Missing fields are safe** if they appear in the region's `default` table or
  in `Private.data_stub` — they get filled.
- **⚠️ A field emitted with the WRONG LUA TYPE is silently replaced by the
  default.** `"64"` where the default is `64` ⇒ becomes `64`. `0` where the
  default is `""` ⇒ becomes `""`. This is the quietest failure mode in the whole
  format. Match the default table's types exactly.
- Fields **not** present in any default table (e.g. `displayIcon`, `texture`)
  are left `nil` if you omit them — those are the genuinely required ones.

### 9.2 `PreAdd` order of operations

`WeakAuras.PreAdd(data)` (`WeakAuras.lua:3108`):

1. legacy stub validate for `internalVersion < 7` / `< 8`
2. `Private.Modernize(data)` ← **runs on the raw emitted table**
3. `Private.validate(data, regionTypes[regionType].default)`
4. `regionTypes[regionType].validate(data)` ← `EnforceSubregionExists`
5. `Private.validate(data, Private.data_stub)`
6. per-subRegion `Private.validate(subRegionData, subRegionTypes[type].default)`
7. `validateUserConfig(data, data.authorOptions, data.config)`

An unknown subregion `type` prints
`"ERROR in '%s' unknown or incompatible sub element type '%s'"` and is left
un-defaulted (it will then usually error at render time).

### 9.3 `EnforceSubregionExists` renumbers your `sub.N.*` conditions

`RegionPrototype.lua:1203`:

```lua
if #indexes == 0 then
  tinsert(data.subRegions, 1, { ["type"] = subregionType })
  move_condition_subregions(data, 1, 1)      -- shifts every sub.N.* by +1
elseif #indexes > 1 then
  ... table.remove ... move_condition_subregions(data, -1, indexes[i])
end
```

Enforced subregions per region type (CONFIRMED from each `validate`):

| Region | Enforced |
|---|---|
| `icon` | `subbackground` |
| `aurabar` | `subforeground`, `subbackground` |
| `texture` | `subbackground` |
| `text` | `subbackground` |
| `progresstexture` | `subbackground` |
| `model`, `stopmotion` | `subbackground` |
| `group`, `dynamicgroup` | none (no `validate`) |

Because `move_condition_subregions` shifts your `sub.N.*` properties by the same
amount as the insertion, the result stays self-consistent — but **your indices
will not be the ones you wrote**. Emit `subbackground` yourself as
`subRegions[1]` (and `subforeground` for `aurabar`) so the numbering you compute
is the numbering the client uses. Duplicate enforced subregions are silently
deleted.

### 9.4 `Private.data_stub` — the minimum table shape

`Types.lua:3985`. Every aura is validated against this, so these keys always
exist afterwards. Emitting them yourself avoids false diffs on re-import:

```lua
triggers = { { trigger = { type = "aura2", names = {}, event = "Health",
                           subeventPrefix = "SPELL", subeventSuffix = "_CAST_START",
                           spellIds = {}, unit = "player", debuffType = "HELPFUL" },
               untrigger = {} } },
load = { size = {multi={}}, spec = {multi={}}, class = {multi={}}, talent = {multi={}} },
actions = { init = {}, start = {}, finish = {} },
animation = { start = {type="none",duration_type="seconds",easeType="none",easeStrength=3},
              main  = {...same...},
              finish= {...same...} },
conditions = {}, config = {}, authorOptions = {}, information = {},
```

The source comment calls this *"the minimal data stub which prevents false
positives in diff upon reimporting an aura"* — i.e. this exact shape is what you
should emit to make re-import diffs clean.

Additionally required and **not** in any default table:

| Field | Where required |
|---|---|
| `id` | `pAdd` errors: `"Improper arguments to WeakAuras.Add - id not defined"` |
| `uid` | required by `MatchInfo`/`BuildUidMap`; `pAdd` will generate one if absent, but then matching is impossible |
| `regionType` | no region is created without it; `Private.regionTypes[nil]` ⇒ no defaults, no validate |
| `triggers.activeTriggerMode` | `pAdd` fixes it up: `if not ... or > #data.triggers then = Private.trigger_modes.first_active (-10)` |
| `displayIcon` (icon) | otherwise falls back to `INV_Misc_QuestionMark` |
| `texture` (texture region) | otherwise nothing renders |
| `width` / `height` | in region defaults, but **must be right** — a parent dynamicgroup lays out using these numbers from the data table, not the frame |
| `parent` / `controlledChildren` | see §3.3, §5.5 |
| `information` | must be a table — `Group.lua:93` reads `data.information.groupOffset` |

### 9.5 What `internalVersion` is and what emitting the wrong value does

`internalVersion` is a monotonically increasing integer identifying the **data
schema**, bumped whenever `Modernize.lua` gains a new migration step. It is
independent of the user-facing addon version.

- `WeakAuras.InternalVersion()` returns the addon's `local internalVersion`
  (`WeakAuras.lua:6`). Upstream `5.21.2` ⇒ `88`; upstream `main` ⇒ `90`; the
  Ascension fork reports `89.5`.
- `Private.Modernize(data)` runs a long chain of `if data.internalVersion < N then ... end`
  blocks and finishes with
  `data.internalVersion = max(data.internalVersion or 0, WeakAuras.InternalVersion())`.

**Emitting too LOW:** Modernize runs every migration step above your value
against your table. Those steps mutate aggressively (renaming trigger fields,
rewriting `sortHybridTable`, converting `data.auto` → `iconSource`, injecting
`information.groupOffset = true` for `internalVersion < 40`, etc.). With a value
below 40 your groups get `selfPoint = "BOTTOMLEFT"`, which shifts every child.
With a value below 2 you get `"Data for '%s' is too old, can't modernize."`.

**Emitting too HIGH:** `WeakAuras.Import` (`Transmission.lua:566`):

```lua
local highestVersion = data.internalVersion or 0
for _, child in ipairs(children) do
  highestVersion = max(highestVersion, child.internalVersion or 0)
end
if highestVersion > WeakAuras.InternalVersion() then
  -- Do not run PreAdd but still show Import Window
  return ImportNow(data, children, target, linkedAuras, nil, callbackFunc)
end
```

**⚠️ This is a nasty one:** if ANY aura in the payload declares an
`internalVersion` higher than the client's, WA **skips `PreAdd` entirely** —
no Modernize, **no `Private.validate` against the region defaults, no
`EnforceSubregionExists`, no `data_stub` fill** — and still opens the import
window. Every field you omitted stays `nil`, and regions error at render time.

**Rule: emit exactly the `internalVersion` the client's own exports carry
(`89.5` here) on the root AND on every child.** Never emit a higher value; never
guess a lower one.

`tocversion` is likewise overwritten on export (`CompressDisplay` sets
`copiedData.tocversion = WeakAuras.BuildInfo`) and is in `internal_fields`, so
it never affects diffs. `30300` is correct and harmless.

---

## 10. Quick checklist for the generator

1. `internalVersion = 89.5` and `tocversion = 30300` on **every** aura.
2. `v = 2000`, `m = "d"`, `d = root`, `c = [flat list of ALL descendants]`.
3. Unique `id` **and** unique `uid` across the whole payload.
4. Root has no `parent`. Every other aura has `parent = <parent id>` and appears
   in that parent's `controlledChildren`.
5. No aura appears in `controlledChildren` unless it is in the payload.
6. Leaf auras must NOT carry `controlledChildren`.
7. Dynamicgroup children: `xOffset = 0, yOffset = 0`, correct `width`/`height`.
8. Never put a gating trigger/condition/load on a `group` or `dynamicgroup` — it
   is inert. Gate the leaves.
9. Emit `subbackground` as `subRegions[1]` (plus `subforeground` for `aurabar`).
10. Match the Lua **types** in the region default tables exactly (`adjustedMin`
    is a string, `stacks` is a string, `iconSource` is a number, …).
11. `triggers.activeTriggerMode = -10` (`first_active`). Set
    `triggers.disjunctive = "any"` explicitly on any multi-trigger aura — the
    default is `"all"`.
12. `genericShowOn` is mandatory on every `Cooldown Progress (Spell)` trigger.
13. `selfPoint` on a dynamicgroup must follow the `grow` × `align` table (§2.2).
14. Never nest a `group`/`dynamicgroup` inside a `dynamicgroup` (§3.4).
15. Never emit `anchorFrameType = "PRD"` on this fork; emit
    `sharedFrameLevel = true` on groups.
16. Condition `bool` values are the numbers `0`/`1`, not Lua booleans. Numeric
    condition values must be clean numeric strings (§6.6).
17. Bump the root `uid` for every published build, and keep a visible version
    stamp inside the pack.

---

## 11. Diagnosis of the current `build_runemaster.py` / `wabuild.py`

Ranked by how badly each breaks layout.

### 11.1 CRITICAL — `spec_group()` gates rows with a trigger on a plain `group`

```python
def spec_group(id_, kids, trigger):
    g = B.group(id_, ROOT, kids, x=0, y=0)
    g["triggers"] = B._trigger_wrap([trigger])   # ← INERT (§3.2)
    return g
```

`scanForLoadsImpl` skips every aura with a truthy `controlledChildren`, and
`pAdd`'s group branch never calls `triggerSystem.Add`, `LoadConditionFunction`,
or sets `loadFuncs[id]`. **A group's `triggers`, `conditions` and `load` are all
inert.** So the Glyphic / Engravement / Riftblade spec groups are *all* shown
simultaneously. Since `Y_MAIN`, `Y_CDS`, `Y_STATE` etc. are the same constants
for every spec, three rows of icons render on top of each other at identical
coordinates.

**That is the reported "icons appear overlapped/duplicated".**

Fix: move the spec-aura gate onto every leaf — either as an extra trigger with
`triggers.disjunctive = "all"`, or (better) as a **Load** condition
(`load.use_*`) on each leaf so unloaded auras cost nothing.

### 11.2 HIGH — `_common()` puts `xOffset`/`yOffset` on every region

Currently benign only because every dynamicgroup child happens to be created
with `x=0, y=0`. The moment a child gets a nonzero offset it is displaced from
its computed slot (§1.3). Make `icon()`/`aurabar()`/`texture()` refuse a nonzero
`x`/`y` when the parent is a dynamicgroup, or assert it in `add()`.

### 11.3 HIGH — no duplicate-`id` / duplicate-`uid` guard in `add()`

```python
def add(region):
    children.append(region)
    return region["id"]
```

A duplicate `id` anywhere in the payload is a **hard Lua error** at import
(`error("Duplicate id in import data: "..child.id)`), and a duplicate `uid`
silently drops an aura from the tree (§5.5). Since `uid(id_)` is a pure hash of
the id, duplicate ids also produce duplicate uids. Add a set-based assert in
`add()`.

### 11.4 HIGH — the "silent re-import no-op" is the `anchor` category, not `uid`

`UID_SALT` exists because re-imports "silently no-op'd". The real mechanism is
that `update_categories.anchor` (`xOffset`, `yOffset`, `width`, `height`,
`scale`, `frameStrata`, `selfPoint`, `anchorPoint`, `anchorFrameType`) has
**`default = false`** on the update dialog for the **root** aura (§5.3). Salting
the uid is a valid workaround (it forces the clean-import path), but it means
every build leaves a stale copy behind. Document "tick Size & Position" as the
alternative.

### 11.5 MEDIUM — icons carry no `subbackground`

`icon()` passes `subregions` straight through. `EnforceSubregionExists` inserts
`subbackground` at index 1 and shifts every `sub.N.*` in `conditions` by +1, so
the result is self-consistent — but the index you compute (`"sub.2.glow"`) is
not the index the client stores (`"sub.3.glow"`), which makes every re-import
diff noisy and makes debugging harder. Emit `subbackground` as `subRegions[1]`
explicitly. Same for `aurabar` (`subforeground` then `subbackground`).

### 11.6 MEDIUM — fork-inert icon fields

`icon()` emits `cooldownSwipe`, `cooldownTextDisabled`, `useCooldownModRate`.
On the Ascension fork's `Icon.lua` these fields exist **nowhere** — not in
`default`, not in `properties`, not read by `modify` (§8B). They are dead weight
that pollutes the `display` diff category. In particular
`cooldownTextDisabled = False` is not why the countdown numbers appear.
(Re-verify against the shipped 89.5 client, which is newer than the public repo.)

### 11.7 MEDIUM — `_group_common()` gives every group an `aura2` trigger

The default `{type="aura2", unit="player", debuffType="HELPFUL"}` with no
`useName`/`auranames` would, on a *leaf*, match **every buff on the player**
(§6.10). On a group it is inert, so it is currently harmless — but it is
misleading, and it will silently become a real bug if that helper is ever reused
for a leaf.

### 11.8 LOW — `aurabar` width vs the icon

`mana_bar()` uses `BAR_W = 270` and compares it against `row_w(n)`. If any
aurabar ever sets `icon = True`, the drawable bar becomes
`width - min(width, height)` and will no longer line up with the icon row (§7.2).

### 11.9 LOW — trigger field hygiene

- `spell_cd_trigger` emits `realSpellName` — a **dead field** with zero code
  references. Drop it.
- `spell_cd_trigger(exact=True)` emits `useExactSpellId`, which is an **`aura2`**
  field. The Cooldown-Progress field is **`use_exact_spellName`**. Exact-id
  matching is currently not happening.
- `aura_trigger` emits `stacks` as a string — correct (`tonumber` is applied).
- `enchant_trigger` sets both `use_showOn`/`showOn` and
  `use_genericShowOn`/`genericShowOn`; only the one the `Weapon Enchant`
  prototype declares is read.
- `_trigger_wrap` never sets `disjunctive`, so multi-trigger auras (the
  engraving icons, which stack an aura trigger plus two enchant triggers) are
  evaluated as **ALL must be active**. That is almost certainly not intended —
  set `disjunctive = "any"`. **This is a second, independent reason those
  displays "showed nothing in game".**
