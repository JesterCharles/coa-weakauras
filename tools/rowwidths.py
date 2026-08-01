"""Measure every always-visible row against the resource bar it sits under.

    python3 tools/rowwidths.py                 # every built class
    python3 tools/rowwidths.py chronomancer    # one class
    python3 tools/rowwidths.py --max 1.2       # fail threshold (default 1.2)

Exits non-zero if any always-visible row is wider than the threshold, so it can
gate a release the way the frozen-fixture check gates a refactor.

WHY THIS EXISTS. `layout-standard.md` has always said cooldown rows wrap at 12
icons, and `build_runemaster.py` has always defined `CD_PER_ROW = 12`. Neither
was ever true: the constant had no callers and every row shipped
`useLimit: false`, which is one unbroken line at any child count. Engravement's
utility row went out at 586px against a 274px main row. Nothing failed, because
nothing measured.

The rule is a doc sentence until something reads a built pack and says no.

WHAT COUNTS AS ALWAYS-VISIBLE. Only rows that are on screen while you stand
still. A 27-entry buff row is a handful of icons in play, so measuring its
stored child count would condemn a row that never renders that wide:

    spell / unit / status   -> always on screen (unless showOnCooldown)
    aura2 / custom / item   -> active-only, not measured

`item` is the Weapon Enchant reminders, which are inverse-triggered -- they show
when something is MISSING, so an empty band is the healthy state.

This reads the per-spec packs, not the all-specs pack. A shared band holds every
spec's children and only lays out the loaded ones, so the all-specs pack would
report a width no player ever sees.
"""
import os
import sys

from classes import built, get, SP
from wacodec import wa_decode

ALWAYS_VISIBLE = {"spell", "unit", "status"}


def _items(v):
    """WA stores arrays as 1-based Lua tables, which decode to dicts."""
    if isinstance(v, dict):
        return list(v.values())
    return list(v or [])


def always_visible(display):
    """True if this leaf is on screen with nothing happening."""
    for t in _items(display.get("triggers")):
        if not isinstance(t, dict):
            continue
        trig = t.get("trigger")
        if not isinstance(trig, dict):
            continue
        if trig.get("type") not in ALWAYS_VISIBLE:
            continue
        if trig.get("genericShowOn") == "showOnCooldown":
            continue
        return True
    return False


def _tracked_spell(display):
    """The spell a display's always-visible trigger watches, if any."""
    for t in _items(display.get("triggers")):
        if not isinstance(t, dict):
            continue
        trig = t.get("trigger")
        if isinstance(trig, dict) and trig.get("type") == "spell":
            return str(trig.get("spellName") or trig.get("realSpellName") or "")
    return None


def measure(path, limit):
    """Yield (band id, icon count, width, ratio) for one pack's visible rows."""
    decoded = wa_decode(open(path).read().strip())
    kids = list(decoded["c"].values())
    by_id = {k["id"]: k for k in kids}

    # Every resource band is width-locked to the main row, so any of them
    # answers "how wide is this pack meant to be".
    bars = [k.get("width", 0) for k in kids if k["regionType"] == "aurabar"]
    bar = max(bars) if bars else 0

    rows = []
    for band in kids:
        if band["regionType"] != "dynamicgroup":
            continue
        shown = [by_id[i] for i in _items(band.get("controlledChildren"))
                 if i in by_id and always_visible(by_id[i])]
        if not shown:
            continue
        # Collapse VARIANTS of one button. Chronomancer's Ripple is five
        # displays -- one per Aeon plus a no-Aeon default -- that all track the
        # same spell and are gated so exactly one can ever be showing. Counting
        # the stored children would report an 8-icon row the player never sees.
        # Keying on the tracked spell is the honest proxy: two leaves in one
        # band on the same spell are variants of a single slot. No band has
        # ever legitimately held two live displays of the same spell -- the
        # duplicate-art check would already have failed if it did.
        slots = {_tracked_spell(k) or k["id"] for k in shown}
        n = len(slots)
        size = max(k.get("width", 0) for k in shown)
        # A GRID band's widest line is its grid width, not its child count,
        # and GRID takes its horizontal gap from columnSpace -- `space` is
        # ignored by that grower, so reading it here would under-measure.
        if band.get("grow") == "GRID":
            per_row = min(n, band.get("gridWidth") or n)
            gap = band.get("columnSpace", 1)
        else:
            per_row, gap = n, band.get("space", 4)
        width = per_row * size + (per_row - 1) * gap
        lines = -(-n // per_row) if per_row else 1
        rows.append((band["id"], n, lines, width, width / bar if bar else 0))
    return bar, rows


def main(argv):
    limit = 1.2
    if "--max" in argv:
        i = argv.index("--max")
        limit = float(argv[i + 1])
        del argv[i:i + 2]

    classes = [get(argv[0])] if argv else list(built())
    if not classes:
        raise SystemExit("no built classes -- nothing to measure")

    over = 0
    for cls in classes:
        for spec, pack in cls.packs:
            if spec is None:          # all-specs pack holds every spec's
                continue              # children; the number would be fiction
            path = cls.pack_path(pack)
            if not os.path.exists(path):
                print(f"  {pack}: not built, skipped")
                continue
            bar, rows = measure(path, limit)
            print(f"\n{cls.name} / {cls.spec_label(spec)}"
                  f"   resource bar {bar}px")
            for band, n, lines, width, ratio in rows:
                flag = ""
                if ratio > limit:
                    flag = f"  <-- {ratio:.2f}x, wrap or cut"
                    over += 1
                wrap = f" in {lines} rows" if lines > 1 else ""
                print(f"  {band:<34} {n:>2} icons  {width:>4.0f}px"
                      f"  {ratio:.2f}x{wrap}{flag}")

    print()
    if over:
        print(f"{over} always-visible rows exceed {limit}x the resource bar")
        return 1
    print(f"all always-visible rows within {limit}x the resource bar")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
