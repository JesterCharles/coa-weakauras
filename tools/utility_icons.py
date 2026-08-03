"""Refresh resources/utility-icons.json -- spell id -> icon texture.

    python3 tools/utility_icons.py

The raid-utility page renders an icon beside every ability. The texture NAME
comes from db.ascension.gg's `g_spells` map (harvested by fetch_spell_icons.py
out of the page cache), and the texture FILE is fetched by fetch_hud_icons.py
into docs/assets/spell-icons/, which is committed for the same reason the class
icons are: Pages serves docs/ and a page that hotlinks someone else's CDN
breaks when they move it.

An id with no entry has no art anywhere, which is the same signal
resources/icon-missing.json records -- and that signal turned out to be STRONG,
which is the opposite of what this file used to say. All six flagged interrupts
have now been checked in game and exactly one, Ranger's Throatpunch, is a real
interrupt. Four are not in the game at all and one carries INTERRUPT_CAST it
cannot honour. The earlier '5 of 6 were real' reading came from hand-checks that
later reversed.
"""
import json
import os
import re
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from classes import dest  # noqa: E402
from fetch_spell_icons import page, harvest, QM  # noqa: E402
from fetch_hud_icons import fetch, OUT  # noqa: E402
import utility_tables as U  # noqa: E402
import ascension  # noqa: E402

ASC = ascension._load()


def tooltip_icon(sid):
    """Texture from `?spell=<id>&power`, or "" -- the second endpoint.

    Shares tools/crosscheck.py's cache so a full sweep and an icon refresh do
    not each fetch the same 259 responses.
    """
    from crosscheck import power  # noqa: PLC0415 -- avoids an import cycle
    m = re.search(r'"icon":\s*"([^"]*)"', power(sid))
    tex = m.group(1) if m else ""
    return "" if tex == QM else tex


def _why_no_art(sid):
    """Which source gave up, and how. Decides whether an id is worth chasing."""
    a = ASC.get(str(sid))
    if not a:
        return "no record on db.ascension.gg"
    if a.get("icon") == "inv_misc_questionmark":
        return "db.ascension.gg renders inv_misc_questionmark"
    if not a.get("icon"):
        return "db.ascension.gg record carries no icon field"
    return "has an icon upstream -- investigate, this should have resolved"


def main():
    own, cache = U.owners(), U.spells()
    # THE ROWS, not everything that classifies. Those were the same set until
    # six rows were re-attributed to the summon button that grants them: a
    # `Build:` spell carries no INTERRUPT_CAST of its own, so `classify` says
    # nothing about it and all six went iconless while art was fetched for the
    # pet abilities that no longer appear anywhere on the page.
    want = {str(r[12]) for _c, _t, _n, _col, rows, _m in U.tables() for r in rows}
    print(f"{len(want)} abilities on the page")

    names = {}
    for sid in sorted(want):
        got = harvest(page(sid))
        if sid in got:
            names[sid] = got[sid]
            continue
        # The page 404s for some ids and the tooltip endpoint still answers --
        # 23 ids in that state, 11 of them with complete data. Asking the
        # second endpoint is the difference between "no art" and "did not ask".
        tex = tooltip_icon(sid)
        if tex:
            names[sid] = tex
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

    # And the inverse list, so the gap is tracked instead of invisible.
    #
    # db.ascension.gg is the ONLY art source that exists for this project --
    # db.exil.es returns 22 keys per spell and not one of them is an icon -- so
    # when it renders `inv_misc_questionmark` there is nowhere else to look and
    # re-running this tool will never improve the result. Writing the leftovers
    # down turns "some rows have a placeholder" into a list somebody can work
    # through from the game client.
    want_names = {sid for sid in want}
    left = sorted(want_names - set(names), key=int)
    gap = {
        "_comment": "Raid-utility abilities with no icon art anywhere we can "
                    "reach. Not proof on its own, but a strong warning: of "
                    "the six flagged interrupts checked in game, five were "
                    "not real -- see resources/icon-missing.json.",
        "_source_status": "db.exil.es has no icon field at all. "
                          "db.ascension.gg renders inv_misc_questionmark, has "
                          "no record, or 404s and still answers questionmark "
                          "from the tooltip endpoint.",
        "_how_to_fill": "put <texture>.jpg in docs/assets/spell-icons/, add "
                        '"<id>": "<texture>" to resources/utility-icons.json, '
                        "then python3 tools/mksite.py --utility-only",
        "_refresh": "rewritten by python3 tools/utility_icons.py",
        "count": len(left),
        # Class and reason per id, not just a name. A bare id -> name map is a
        # list somebody has to re-derive context for before they can act on it;
        # this one says who owns the ability and which source gave up on it,
        # which is what decides whether it is worth chasing.
        "ids": {sid: {
            "class": next((c for c, _n, _s, _r in own.get(sid, [])), "?"),
            "ability": cache[sid]["name"],
            "why": _why_no_art(sid),
        } for sid in left if sid in cache},
    }
    gp = dest("icon-wanted.json")
    json.dump(gap, open(gp, "w"), indent=1)
    print(f"wrote {gp}: {len(left)} abilities still without art")
    return 0


if __name__ == "__main__":
    sys.exit(main())
