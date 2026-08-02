"""Refresh resources/utility-icons.json -- spell id -> icon texture.

    python3 tools/utility_icons.py

The raid-utility page renders an icon beside every ability. The texture NAME
comes from db.ascension.gg's `g_spells` map (harvested by fetch_spell_icons.py
out of the page cache), and the texture FILE is fetched by fetch_hud_icons.py
into docs/assets/spell-icons/, which is committed for the same reason the class
icons are: Pages serves docs/ and a page that hotlinks someone else's CDN
breaks when they move it.

An id with no entry has no art anywhere, which is the same signal
resources/icon-missing.json records -- see the note there about how weak that
signal turned out to be (5 of 6 flagged interrupts were real).
"""
import json
import os
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from classes import dest  # noqa: E402
from fetch_spell_icons import page, harvest  # noqa: E402
from fetch_hud_icons import fetch, OUT  # noqa: E402
import utility_tables as U  # noqa: E402


def main():
    own, cache = U.owners(), U.spells()
    want = {sid for sid, d in cache.items() if sid in own and U.classify(d)}
    print(f"{len(want)} abilities on the page")

    names = {}
    for sid in sorted(want):
        got = harvest(page(sid))
        if sid in got:
            names[sid] = got[sid]
    print(f"  {len(names)} have a texture name; {len(want) - len(names)} have none")

    have = {os.path.splitext(f)[0] for f in os.listdir(OUT)}
    todo = sorted(set(names.values()) - have)
    for i, n in enumerate(todo, 1):
        fetch(n)
        if i % 20 == 0 or i == len(todo):
            print(f"  fetched {i}/{len(todo)}")
    have = {os.path.splitext(f)[0] for f in os.listdir(OUT)}

    out = {
        "_comment": "spell id -> icon texture name, for the abilities on the "
                    "raid-utility page. Textures live in "
                    "docs/assets/spell-icons/.",
        "_refresh": "python3 tools/utility_icons.py",
        "ids": {k: v for k, v in sorted(names.items(), key=lambda kv: int(kv[0]))
                if v in have},
    }
    p = dest("utility-icons.json")
    json.dump(out, open(p, "w"), indent=1)
    print(f"wrote {p}: {len(out['ids'])} ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
