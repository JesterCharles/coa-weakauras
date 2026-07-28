"""Structural comparison of two WeakAuras export strings.

The refactor gate for the whole pipeline. Byte-equality is the wrong tool --
`wacodec` serialises nested tables, so any dict-key reordering changes the
bytes while the aura is identical in game. Byte-comparison would fight every
legitimate refactor and pressure the engine into preserving accidental
ordering.

So: decode both sides and compare the normalised tree.

WHAT IS NORMALISED AWAY
    uid / preferToUpdate / skipWagoUpdate   volatile, regenerated per build
    information / semver / tocversion       metadata, not behaviour
    internalVersion                          WeakAuras' own
    dict key order                           serialisation detail

WHAT IS DELIBERATELY *NOT* NORMALISED
    controlledChildren ORDER.  It is semantic -- it encodes "most-pressed
    first" and "trinkets pinned last". Sorting it would false-pass exactly the
    row-order and button-priority bugs the layout standard exists to prevent.

Stdlib only. No pytest, no jsonschema.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "tools"))

from wacodec import wa_decode  # noqa: E402

VOLATILE = {
    "uid", "preferToUpdate", "skipWagoUpdate", "information",
    "tocversion", "semver", "internalVersion",
}


def normalise(obj):
    """Recursively drop volatile keys and impose a stable key order.

    Lists and LuaTable arrays keep their order -- see the module docstring.
    """
    if isinstance(obj, dict):
        return {k: normalise(v)
                for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))
                if k not in VOLATILE}
    if isinstance(obj, list):
        return [normalise(v) for v in obj]
    return obj


def load(path):
    return wa_decode(open(path).read().strip())


def displays(pack):
    """id -> display, for every child in the pack."""
    return {d["id"]: d for d in pack["c"].values()}


def diff(old, new):
    """Compare two decoded packs. Returns a list of human-readable differences.

    Empty list means structurally identical.
    """
    out = []
    o, n = displays(old), displays(new)

    for i in sorted(set(o) - set(n)):
        out.append(f"removed display: {i}")
    for i in sorted(set(n) - set(o)):
        out.append(f"added display: {i}")

    for i in sorted(set(o) & set(n)):
        a, b = normalise(o[i]), normalise(n[i])
        if a == b:
            continue
        for k in sorted({k for k in set(a) | set(b) if a.get(k) != b.get(k)},
                        key=str):
            out.append(f"{i}: {k}: {a.get(k)!r} -> {b.get(k)!r}")

    ra, rb = normalise(old["d"]), normalise(new["d"])
    if ra != rb:
        for k in sorted({k for k in set(ra) | set(rb) if ra.get(k) != rb.get(k)},
                        key=str):
            out.append(f"<root>: {k}: {ra.get(k)!r} -> {rb.get(k)!r}")

    return out


def diff_files(old_path, new_path):
    return diff(load(old_path), load(new_path))
