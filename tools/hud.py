"""Resolve a built pack into absolute screen geometry, for the HUD preview.

    python3 tools/hud.py docs/packs/runemaster/runemaster-coa.txt

WeakAuras stores every display's offset RELATIVE TO ITS PARENT GROUP, and the
groups nest -- a rotation icon sits at (0,0) inside `RM Main`, which sits at
y=-132 inside the pack root. To draw the pack as the player will actually see
it, those offsets have to be summed up the parent chain.

Everything in these packs anchors CENTER/CENTER, so the resolved coordinate is
an offset from the middle of the screen, with y counting UP. That is why every
band comes out negative: the HUD sits below your character.
"""
import json
import os
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from wacodec import wa_decode  # noqa: E402

MISSES = os.path.join(os.path.dirname(SP), "docs", "assets", "spell-icons",
                      "misses.json")


def _missing():
    try:
        return set(json.load(open(MISSES)))
    except Exception:
        return set()


# Trigger types that keep a display on screen whenever the pack is loaded.
# A spell-cooldown display with inverse=true is visible ready OR on cooldown,
# and a unit/power display is always up -- these are the HUD you actually look
# at. Everything else (aura2, custom) only appears while its aura is active.
PERSISTENT_TRIGGERS = {"spell", "unit", "status"}


def _persistent(node):
    """True when this display is on screen the whole time you are playing."""
    trig = (node.get("triggers") or {}).get(1) or {}
    return (trig.get("trigger") or {}).get("type") in PERSISTENT_TRIGGERS


# What a display IS, from its first trigger. This is the semantic layer the
# preview (and later the editor) names tiles by: a spell-cooldown icon is a
# "cooldown" whatever its art, an aura2 display only exists while its aura
# does, unit/status displays track a resource. Anything else falls back to its
# regionType, which at least says what shape it draws.
ROLE_BY_TRIGGER = {"spell": "cooldown", "aura2": "aura",
                   "unit": "resource", "status": "resource",
                   "custom": "custom"}


def _vals(x):
    return list(x.values()) if isinstance(x, dict) else list(x or [])


def _flat_checks(chk):
    """A condition check is either a leaf {trigger, variable, ...} or an
    AND/OR combinator carrying `checks` -- the urgency tiers are ANDed with
    their GCD guard, so the leaves have to be dug out."""
    if not isinstance(chk, dict):
        return []
    subs = _vals(chk.get("checks"))
    if subs:
        out = []
        for s in subs:
            out.extend(_flat_checks(s))
        return out
    return [chk]


def _caps(node):
    """-> (role, proc, urgent, desat) for one leaf, read off the pack itself.

    Derived from what wapack.py actually emits, never re-guessed here:
      proc    a condition on an aura trigger's `show` that turns a sub glow on
              -- the PROC_GLOW shape. Keyed to AURA triggers on purpose: the
              spell-known replacement glow uses the same `show`+glow change on
              a non-aura trigger and is not a proc cue.
      urgent  any condition reading `expirationTime` -- the graduated
              timer/glow/pulse ladder (and the aura refresh cue, which is the
              same "time is running out" statement).
      desat   a condition that desaturates -- the `spellUsable` readiness rule.
    """
    trigs = node.get("triggers") or {}
    first = (trigs.get(1) or {}).get("trigger") or {}
    role = ROLE_BY_TRIGGER.get(first.get("type"),
                               node.get("regionType") or "icon")
    aura_triggers = {i for i, t in trigs.items()
                     if isinstance(i, int) and isinstance(t, dict)
                     and (t.get("trigger") or {}).get("type") == "aura2"}
    proc = urgent = desat = False
    for c in _vals(node.get("conditions")):
        if not isinstance(c, dict):
            continue
        props = {ch.get("property") for ch in _vals(c.get("changes"))
                 if isinstance(ch, dict)}
        glow = any(isinstance(p, str) and p.startswith("sub.")
                   and p.endswith(".glow") for p in props)
        if "desaturate" in props:
            desat = True
        for chk in _flat_checks(c.get("check")):
            if chk.get("variable") == "expirationTime":
                urgent = True
            if (chk.get("variable") == "show" and glow
                    and chk.get("trigger") in aura_triggers):
                proc = True
    return role, proc, urgent, desat


def _ordered_children(node, by_id):
    """controlledChildren decodes to {1: id, 2: id, ...}. The numeric key IS
    the layout order for a dynamic group, so it has to be sorted numerically --
    dict order would put 10 before 2."""
    cc = node.get("controlledChildren") or {}
    if isinstance(cc, dict):
        keys = sorted(cc, key=lambda k: int(k) if str(k).isdigit() else 0)
        ids = [cc[k] for k in keys]
    else:
        ids = list(cc)
    return [by_id[i] for i in ids if i in by_id]


def _anchor_target(node):
    """-> the display id this node hangs off, or None for a normal offset.

    WeakAuras anchors one aura to another's region with
    anchorFrameType="SELECTFRAME" and anchorFrameFrame="WeakAuras:<id>"
    (WeakAuras.lua:6066-6075). The stored yOffset is then a GAP from the
    target's edge, not an offset from the parent -- reading it as the latter
    puts a band that hangs 4px under a three-row group 4px under the group's
    own anchor instead, which is roughly 90px too high.
    """
    if node.get("anchorFrameType") != "SELECTFRAME":
        return None
    frame = node.get("anchorFrameFrame") or ""
    return frame.split(":", 1)[1] if frame.startswith("WeakAuras:") else None


def _is_grid(node):
    """A GRID group's anchor is the TOP of its first row; every other grow mode
    centres its content on the anchor. The distinction matters anywhere a
    height is turned back into an edge."""
    return (node.get("regionType") == "dynamicgroup"
            and (node.get("grow") or "").upper() == "GRID")


def _size(node, by_id, keep=None):
    """Outer size of a node. A dynamic group has no meaningful stored width, so
    it is measured from the row it will lay out -- and only from the children
    that will actually be on screen, or the row would be centred against a
    width that includes displays nobody can see."""
    if node.get("regionType") == "dynamicgroup":
        kids = _ordered_children(node, by_id)
        if keep:
            kids = [k for k in kids if keep(k)]
        if not kids:
            return 0, 0
        space = int(node.get("space") or 0)
        sizes = [_size(k, by_id, keep) for k in kids]
        grow = (node.get("grow") or "").upper()
        if grow == "VERTICAL":
            return (max(w for w, _ in sizes),
                    sum(h for _, h in sizes) + space * (len(kids) - 1))
        if grow == "GRID":
            # A wrapped band is as wide as its WIDEST ROW and as tall as the
            # rows stacked. Measuring it as one long row -- which is what the
            # horizontal fall-through below does -- reports a 25-icon utility
            # band as ~700px wide and throws off every anchor derived from it.
            width = int(node.get("gridWidth") or 0) or len(kids)
            cspace = int(node.get("columnSpace") or space or 0)
            rspace = int(node.get("rowSpace") or space or 0)
            rows = [sizes[i:i + width] for i in range(0, len(sizes), width)]
            return (max(sum(w for w, _ in r) + cspace * (len(r) - 1)
                        for r in rows),
                    sum(max(h for _, h in r) for r in rows)
                    + rspace * (len(rows) - 1))
        return (sum(w for w, _ in sizes) + space * (len(kids) - 1),
                max(h for _, h in sizes))
    return int(node.get("width") or 0), int(node.get("height") or 0)


def displays(pack_path, only_persistent=False):
    """-> [{id, x, y, w, h, kind, icon}] in absolute screen coordinates.

    With `only_persistent`, active-only displays are dropped BEFORE layout, not
    filtered out of the result afterwards. That ordering is the whole point: a
    dynamic group lays out only the children that are loaded and showing, so
    dropping the 27 buff icons re-centres the rows that remain, exactly as the
    addon does in play. Filtering afterwards would leave the survivors sitting
    at positions computed for a row that is not on screen.

    Offsets are resolved TOP-DOWN rather than by summing a node's own stored
    offsets up the parent chain, because a dynamic group does not store its
    children's positions at all -- WeakAuras lays them out at runtime. Every
    band in these packs is a HORIZONTAL dynamic group, so a naive sum puts all
    27 buff icons on top of each other at x=0.

    The simulation matches DynamicGroup.lua for the settings these packs use:
    children in controlledChildren order, separated by `space`, and the whole
    row centred on the group's own anchor.

    GRID is simulated too, and has to be. This function once documented GRID as
    "a grow mode the packs do not use" and fell back to stored offsets for it --
    but a dynamic group's children all store (0,0), so the fallback silently
    stacked an entire band on one point. The moment CD_PER_ROW was wired to
    gridWidth the cooldown rows became GRID, and every wrapped row on the site
    collapsed into a pile while the page still claimed to be drawn to scale.
    A fallback that "does not invent a position" still invents ONE, and being
    visibly wrong beats being quietly wrong.

    gridType "HD" is row-first, each completed row re-centred horizontally and
    rows stacking downward, which is what wabuild.dynamicgroup emits. Gaps come
    from columnSpace/rowSpace: GRID ignores `space` entirely.

    CIRCLE really is unused and still falls back -- but it now says so loudly
    instead of drawing a stack.

    SELECTFRAME anchoring is resolved too, via `_anchor_target`. A band that
    hangs off another band's BOTTOM edge has no meaningful parent offset, so
    reading its stored yOffset as one drew Chronomancer's 22-icon utility row
    through the buff row and the alerts -- an overlap the pack does not have.
    Those bands are deferred until the band they follow has been measured.

    `icon` is the bare texture name, or None when the art is not cached. `kind`
    is the regionType, so a bar can be drawn as a bar rather than a square.
    """
    return layout(wa_decode(open(pack_path).read().strip()), only_persistent)


def layout(d, only_persistent=False):
    """The geometry pass of `displays`, over an already-decoded pack.

    Split out so a test can prune a band and re-run the layout, which is the
    only way to check that the ladder still closes up when a row renders
    SHORTER than the builder planned -- the case fixed yOffsets get wrong and
    the reason the packs anchor instead.
    """
    nodes = d["c"]
    by_id = {k["id"]: k for k in nodes.values()}
    missing = _missing()
    out = []
    # id -> (centre x, bottom edge y) for every group already placed. A
    # SELECTFRAME band needs its target's real BOTTOM, which is only known
    # once that target has been measured, so anchored bands are deferred.
    extents = {}
    pending = []

    def shown(node):
        """A group is shown when anything under it is; an all-transient band
        disappears entirely in the in-play view, which is correct -- an empty
        dynamic group draws nothing."""
        if not only_persistent:
            return True
        if node.get("controlledChildren"):
            return any(shown(k) for k in _ordered_children(node, by_id))
        return _persistent(node)

    def walk(node, ox, oy):
        kids = [k for k in _ordered_children(node, by_id) if shown(k)]
        if not kids:
            return
        grow = (node.get("grow") or "").upper()
        dynamic = node.get("regionType") == "dynamicgroup"
        space = int(node.get("space") or 0)

        if dynamic and grow in ("HORIZONTAL", "VERTICAL"):
            sizes = [_size(k, by_id, shown) for k in kids]
            total = (sum(s[0] for s in sizes) if grow == "HORIZONTAL"
                     else sum(s[1] for s in sizes)) + space * (len(kids) - 1)
            run = -total / 2.0          # rows are centred on the group anchor
            for kid, (kw, kh) in zip(kids, sizes):
                if grow == "HORIZONTAL":
                    kx, ky = run + kw / 2.0, 0
                    run += kw + space
                else:
                    # y counts up, so a vertical row grows downward from the top
                    ky, kx = -(run + kh / 2.0), 0
                    run += kh + space
                emit(kid, ox + kx, oy + ky)
        elif dynamic and grow == "GRID":
            sizes = [_size(k, by_id, shown) for k in kids]
            width = int(node.get("gridWidth") or 0) or len(kids)
            cspace = int(node.get("columnSpace") or space or 0)
            rspace = int(node.get("rowSpace") or space or 0)
            rows = [list(zip(kids, sizes))[i:i + width]
                    for i in range(0, len(kids), width)]
            # Row-first, each row centred on its own width -- a short last row
            # sits centred under a full one rather than left-aligned.
            top = 0.0
            for row in rows:
                rw = sum(s[0] for _, s in row) + cspace * (len(row) - 1)
                rh = max(s[1] for _, s in row)
                run = -rw / 2.0
                for kid, (kw, kh) in row:
                    emit(kid, ox + run + kw / 2.0, oy + top - rh / 2.0)
                    run += kw + cspace
                top -= rh + rspace
        else:
            if dynamic:
                # Stored offsets are (0,0) for every dynamic-group child, so
                # this path draws them on top of each other. Say so rather than
                # publishing a pile that looks like a layout.
                print(f"  !! hud: {node.get('id')} uses grow={grow or 'NONE'}, "
                      f"which is not simulated -- its {len(kids)} children will "
                      f"stack. Add it to hud.walk() before trusting this preview.")
            for kid in kids:
                if _anchor_target(kid):
                    # Its position depends on a band that may not be placed
                    # yet. Carry the parent origin along as the fallback for
                    # a target that turns out not to be in this pack at all.
                    pending.append((kid, ox, oy))
                    continue
                emit(kid,
                     ox + int(kid.get("xOffset") or 0),
                     oy + int(kid.get("yOffset") or 0))

    def place_anchored(node, ox, oy):
        """Hang `node` off the bottom edge of the band it anchors to.

        selfPoint TOP / anchorPoint BOTTOM with a negative yOffset, which is
        what wabuild emits: the node's top edge lands `gap` below the target's
        bottom edge, both centred on the same x.
        """
        target = extents.get(_anchor_target(node))
        if target is None:
            return False
        tx, tbottom = target
        top = tbottom + int(node.get("yOffset") or 0)
        _, h = _size(node, by_id, shown)
        emit(node, tx + int(node.get("xOffset") or 0),
             top if _is_grid(node) else top - h / 2.0)
        return True

    def emit(node, x, y):
        if node.get("controlledChildren"):
            _, h = _size(node, by_id, shown)
            if h:
                extents[node["id"]] = (x, y - h if _is_grid(node)
                                       else y - h / 2.0)
            walk(node, x, y)
            return
        w = int(node.get("width") or 0)
        h = int(node.get("height") or 0)
        if not w or not h:
            return
        tex = node.get("displayIcon")
        icon = None
        if isinstance(tex, str) and tex:
            leaf = tex.replace("/", "\\").split("\\")[-1].strip().lower()
            if leaf and leaf not in missing:
                icon = leaf
        role, proc, urgent, desat = _caps(node)
        out.append({
            # `band` lets the caller name a display without re-deriving the
            # namespace: a leaf's parent group IS its band after the merge.
            "band": node.get("parent") or "",
            "id": node["id"], "x": round(x, 1), "y": round(y, 1),
            "w": w, "h": h,
            "kind": node.get("regionType") or "icon",
            "icon": icon,
            # Semantic layer (ADR-002): what the tile IS and which states it
            # is capable of, so the preview can say so without animating them.
            "role": role, "proc": proc, "urgent": urgent, "desat": desat,
        })

    walk(d["d"], 0, 0)
    # Anchors chain -- long-term hangs off utility, which hangs off offense --
    # so resolve repeatedly until a pass places nothing new.
    while pending:
        rest = [p for p in pending if not place_anchored(*p)]
        if len(rest) == len(pending):
            for node, ox, oy in rest:
                # WeakAuras falls back to the parent region when the anchor
                # frame is absent, so this draws what the player would see --
                # but it is a hole in the layout, not a position anyone chose.
                print(f"  !! hud: {node.get('id')} anchors to "
                      f"{_anchor_target(node)}, which is not in this pack -- "
                      f"falling back to its stored offset.")
                emit(node, ox + int(node.get("xOffset") or 0),
                     oy + int(node.get("yOffset") or 0))
            break
        pending = rest
    # Painter's order: top of the screen first, then left to right. A stable
    # order keeps the generated HTML from churning between builds.
    out.sort(key=lambda i: (-i["y"], i["x"], i["id"]))
    return out


def bounds(items, pad=14):
    """-> (x0, y0, x1, y1) box enclosing every display, with a little air."""
    if not items:
        return (-160, -300, 160, 10)
    x0 = min(d["x"] - d["w"] / 2 for d in items) - pad
    x1 = max(d["x"] + d["w"] / 2 for d in items) + pad
    y0 = min(d["y"] - d["h"] / 2 for d in items) - pad
    y1 = max(d["y"] + d["h"] / 2 for d in items) + pad
    return (x0, y0, x1, y1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    items = displays(sys.argv[1])
    x0, y0, x1, y1 = bounds(items)
    have = sum(1 for d in items if d["icon"])
    print(f"{len(items)} displays  x[{x0:.0f},{x1:.0f}]  y[{y0:.0f},{y1:.0f}]")
    print(f"{have} with cached art, {len(items) - have} placeholder")
    for d in items[:12]:
        print(f"  {d['y']:>5} {d['x']:>5} {d['w']:>3}x{d['h']:<3} "
              f"{d['kind']:<8} {d['icon'] or '--':<34} {d['id']}")
