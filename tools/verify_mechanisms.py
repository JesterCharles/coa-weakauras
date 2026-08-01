"""Report which mechanisms a built pack uses that are NOT witnessed on this fork.

    python3 tools/verify_mechanisms.py chronomancer
    python3 tools/verify_mechanisms.py chronomancer --sv ~/Downloads/WeakAuras.lua

WHY. This toolchain generates WeakAuras data for a FORK (internalVersion 89.5)
whose addon source is not on this machine. Upstream WeakAuras source answers
"how is this supposed to work"; it does not answer "does this fork do it". The
gap between those two questions has cost an in-game import cycle every time it
was crossed on a guess.

So: before shipping, list every distinctive field/value the pack emits and say
whether anything KNOWN-WORKING already uses it. Two evidence sources, best
first:

  1. the client's own SavedVariables -- auras this fork has actually loaded,
     saved and round-tripped. The strongest signal available offline.
  2. decoded community packs in resources/import-strings/ -- known-good auras
     built by other players for this server.

A mechanism absent from both is not necessarily broken. It IS the thing to
probe first when a pack misbehaves, and the thing to mention when handing the
pack over -- rather than discovering it from a screenshot.

Exit code is always 0: this reports risk, it does not gate a build.
"""
import glob
import os
import re
import sys

from classes import get, SP
from wacodec import wa_decode

ROOT = os.path.dirname(SP)

# The mechanisms worth tracking: things the builder chooses deliberately and
# that would fail SILENTLY -- no error in the build, none in game -- if the
# fork does not honour them.
MECHANISMS = [
    ("Spell Known trigger",     "event", "Spell Known",
     "detects a passive; an aura2 trigger cannot"),
    ("grow GRID",               "grow", "GRID",
     "row wrapping; useLimit truncates instead"),
    ("gridType HD",             "gridType", "HD",
     "each wrapped row re-centred horizontally"),
    ("SELECTFRAME anchoring",   "anchorFrameType", "SELECTFRAME",
     "band anchored to another band so the ladder collapses"),
    ("iconSource manual",       "iconSource", 0,
     "displayIcon wins over the trigger's icon"),
    ("useExactSpellId",         "useExactSpellId", True,
     "aura matched by id rather than name"),
    ("useStacks",               "useStacks", True,
     "per-cell stack thresholds on a segment bar"),
    ("showOnMissing",           "matchesShowOn", "showOnMissing",
     "fires when NONE of the auras is present"),
    ("ownOnly",                 "ownOnly", True,
     "only auras YOU applied"),
]

CONDITION_PROPS = ["displayIcon", "sub.%d.glow", "desaturate"]


def walk(node, out):
    """Every (key, value) pair anywhere in a decoded display."""
    if isinstance(node, dict):
        for k, v in node.items():
            out.append((k, v))
            walk(v, out)
    elif isinstance(node, list):
        for v in node:
            walk(v, out)


def pack_pairs(path):
    d = wa_decode(open(path).read().strip())
    out = []
    walk(d.get("c"), out)
    walk(d.get("d"), out)
    return out


def sv_text(sv):
    if sv and os.path.exists(os.path.expanduser(sv)):
        return open(os.path.expanduser(sv), encoding="utf-8",
                    errors="replace").read()
    return ""


def main(argv):
    sv_path = None
    if "--sv" in argv:
        i = argv.index("--sv")
        sv_path = argv[i + 1]
        del argv[i:i + 2]
    else:
        for guess in ("~/Downloads/WeakAuras.lua",):
            if os.path.exists(os.path.expanduser(guess)):
                sv_path = guess
                break

    cls = get(argv[0] if argv else "runemaster")
    pack = cls.pack_path(f"{cls.slug}-all-specs")
    if not os.path.exists(pack):
        raise SystemExit(f"not built: {pack}")

    used = pack_pairs(pack)
    sv = sv_text(sv_path)
    # Collect (key, value) PAIRS, not a text blob. Substring-searching a
    # concatenated dump reports a hit whenever the key appears anywhere and the
    # value appears anywhere -- which marked SELECTFRAME as witnessed when no
    # community pack uses it at all. A verifier that over-reports is worse than
    # none, because it launders a guess into a fact.
    community = set()
    for f in glob.glob(os.path.join(ROOT, "resources", "import-strings", "*.txt")):
        for k, v in pack_pairs(f):
            if isinstance(v, (str, int, bool, float)):
                community.add((k, v))

    print(f"{cls.name}: mechanisms used by the pack, and whether anything "
          f"known-working uses them\n")
    print(f"  client SavedVariables: {sv_path or 'NOT FOUND'}")
    print(f"  community packs      : "
          f"{len(glob.glob(os.path.join(ROOT, 'resources', 'import-strings', '*.txt')))}\n")

    unwitnessed = []
    for label, key, value, why in MECHANISMS:
        if not any(k == key and v == value for k, v in used):
            continue                      # the pack does not use it
        lit = ("true" if value is True
               else f'"{value}"' if isinstance(value, str) else str(value))
        in_sv = bool(re.search(rf'\["{re.escape(key)}"\] = {re.escape(lit)}', sv)) \
            if sv else False
        in_com = (key, value) in community
        mark = "client" if in_sv else ("community" if in_com else "NOWHERE")
        if mark == "NOWHERE":
            unwitnessed.append((label, why))
        print(f"  {label:24} {mark:10} {why}")

    if unwitnessed:
        print(f"\n  {len(unwitnessed)} mechanism(s) witnessed NOWHERE. If the "
              f"pack misbehaves, probe these first:")
        for label, why in unwitnessed:
            print(f"    - {label}: {why}")
    else:
        print("\n  every mechanism has precedent")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
