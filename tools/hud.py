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
    row centred on the group's own anchor. Anything using a grow mode the packs
    do not use (CIRCLE, GRID) falls back to the stored offsets rather than
    inventing a position.

    `icon` is the bare texture name, or None when the art is not cached. `kind`
    is the regionType, so a bar can be drawn as a bar rather than a square.
    """
    d = wa_decode(open(pack_path).read().strip())
    nodes = d["c"]
    by_id = {k["id"]: k for k in nodes.values()}
    missing = _missing()
    out = []

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
        else:
            for kid in kids:
                emit(kid,
                     ox + int(kid.get("xOffset") or 0),
                     oy + int(kid.get("yOffset") or 0))

    def emit(node, x, y):
        if node.get("controlledChildren"):
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
        out.append({
            # `band` lets the caller name a display without re-deriving the
            # namespace: a leaf's parent group IS its band after the merge.
            "band": node.get("parent") or "",
            "id": node["id"], "x": round(x, 1), "y": round(y, 1),
            "w": w, "h": h,
            "kind": node.get("regionType") or "icon",
            "icon": icon,
        })

    walk(d["d"], 0, 0)
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
