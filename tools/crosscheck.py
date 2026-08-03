"""Does the SECOND spell database have a record of each raid-utility row?

    python3 tools/crosscheck.py            # refresh, then write the resource
    python3 tools/crosscheck.py --report   # read the resource, print the list

Every row on the raid utility page comes from the db.exil.es mirror under
`tools/spellchk/`, so "is it on db.exil.es" is answered by the row existing at
all. The open question is the other side: db.ascension.gg is a second snapshot
of the same TrinityCore tables, and a spell that only ONE of the two has ever
heard of is the shape a cut, renamed or never-implemented ability takes.

THE ENDPOINT. `?spell=<id>&power` answers for every id, including ones whose
HTML page 404s -- 23 raid-utility ids 404 and eleven of them return complete
data here, so the page status is not the check. Two answers matter:

    $WowheadPower.registerSpell(560470, 0, {});          <- NO RECORD
    $WowheadPower.registerSpell(800808, 0, {"name_enus" ... <- has one

THE ID IS NOT THE JOIN KEY, and asking only by id overstates absence by a
third. `Distracto Shot` is 560470 on db.exil.es and 561269 on db.ascension.gg
-- same name, same 4% mana, same interrupt tooltip, different row. So every id
that comes back empty is asked again BY NAME, and a name hit flagged
`isCoaClass` is a candidate for the same ability.

A candidate is not a match. Three of the five name hits are different
abilities wearing the same word: Bloodmage's `Siphon` steals two buffs here
and summons three skeletons there, and Sun Cleric's `Solar Burn` is an
interrupt here and a nature damage-over-time there. Tooltips were read side by
side and the verdicts live in NAME_MATCH below, one line of reasoning each,
because no rule separates "the same ability under another id" from "a
different ability with the same name".

WHAT ABSENCE IS WORTH. Not a verdict. Two ids still in the no-record set --
`Solar Burn` and `Hellgaze` -- were confirmed in game by a person on
2026-08-02 and are in the game regardless of what this database says. So the
page marks these rows "in-game verification in process" and keeps them; only
somebody logging in can remove a row, and that goes in
`resources/icon-missing.json` under `confirmed_absent`.

This is a DIFFERENT signal from the no-art one that file tracks. No art means
the database has the spell and no picture for it; no record means it does not
have the spell. The second is the stronger doubt, and the page says which.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)

CACHE = os.path.join(SP, "spellchk")
OUT = os.path.join(os.path.dirname(SP), "resources", "cross-source.json")
# Same courtesy pause fetch_spell_icons.py uses. A full sweep is 259 requests
# against somebody's community database; a cache hit costs nothing.
THROTTLE = 0.35
EMPTY = re.compile(r"registerSpell\(\d+,\s*0,\s*\{\s*\}\s*\)")
# One search-result row. `isCoaClass` is the field that matters: db.ascension.gg
# indexes the whole server, so a name search returns retail and NPC spells too,
# and only the CoA-flagged rows can be the ability a CoA class presses.
SROW = re.compile(r'\{"id":(\d+),"name":"((?:[^"\\]|\\.)*)","icon":"([^"]*)"'
                  r'.*?"isCoaClass":(\d)')

# HAND VERDICTS on the name hits. mirror id -> (ascension id or None, why).
#
# Every one of these was decided by reading the two tooltips next to each
# other, and three of the five say the databases are describing DIFFERENT
# abilities that happen to share a word. Nothing here is derivable -- a name
# match is a lead, and the entry records which way it went and on what.
NAME_MATCH = {
    "560470": ("561269", "same ability: 4% of base mana, instant, "
                         "'interrupt an enemy's spellcasting and prevents any "
                         "spell from that school' -- the Tinker Noise Box "
                         "shot, filed under a different id"),
    "802869": (None, "SAME ability, DIFFERENT tooltip: ascension's 803424 "
                     "Pursuit is the -20% damage-taken gap-closer with no "
                     "stun clause at all, and the stun is why this row is on "
                     "the page. The row's CLAIM is what is unconfirmed"),
    "803327": (None, "different ability: ascension's 804074 Siphon summons "
                     "three Brittle Skeletons; the mirror's steals two "
                     "beneficial magic effects"),
    "801846": (None, "different ability: ascension's 705672 Exhale is a "
                     "1 min, 20 Static slow-dispel; the mirror's is a 40s "
                     "cone root"),
    "500148": (None, "different ability: ascension's 274532/978623 Solar Burn "
                     "is a Spellstorm damage-over-time; the mirror's is a 25s "
                     "interrupt (and a person has confirmed the interrupt in "
                     "game, so this is the database being incomplete)"),
}


def power(sid, refresh=False):
    """Raw `?spell=<id>&power` response for one id, cached on disk."""
    p = os.path.join(CACHE, f"asc-power-{sid}.txt")
    if refresh or not (os.path.exists(p) and os.path.getsize(p) > 0):
        subprocess.run(["curl", "-s", "-m", "25",
                        f"https://db.ascension.gg/?spell={sid}&power",
                        "-o", p], check=False, timeout=40)
        time.sleep(THROTTLE)
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def search(name):
    """Every CoA-flagged spell on db.ascension.gg whose name is exactly this.

    The `@` some names carry in the listview is a display prefix, not part of
    the name, and stripping it is what makes `@Distracto Shot` match.
    """
    key = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    p = os.path.join(CACHE, f"asc-search-{key}.html")
    if not (os.path.exists(p) and os.path.getsize(p) > 1000):
        subprocess.run(["curl", "-s", "-m", "30",
                        "https://db.ascension.gg/?search=" +
                        urllib.parse.quote(name), "-o", p],
                       check=False, timeout=45)
        time.sleep(THROTTLE)
    try:
        h = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    return [{"id": int(m.group(1)), "icon": m.group(3), "coa": int(m.group(4))}
            for m in SROW.finditer(h)
            if m.group(2).lstrip("@").lower() == name.lower()]


def state(sid, name=""):
    """"record" / "other-id" / "no-record" / "unreachable", plus what was seen.

    `other-id` means both databases have the ability and disagree about its
    spell id -- a pass, and the only reason the name search exists.
    """
    t = power(sid)
    if not t.strip():
        # An empty body is a failed request, NOT an absent spell. Recording it
        # as absence would manufacture the exact finding this file exists to
        # report, so it gets its own state and is excluded from the count.
        return {"ascension": "unreachable"}
    if EMPTY.search(t):
        hits = [h for h in search(name) if h["coa"]] if name else []
        d = {"ascension": "no-record"}
        if hits:
            d["name_hits"] = [h["id"] for h in hits]
        other, why = NAME_MATCH.get(sid, (None, ""))
        if why:
            d["verdict"] = why
        if other:
            d["ascension"] = "other-id"
            d["asc_id"] = other
        return d
    n = re.search(r'"name_enus":\s*"((?:[^"\\]|\\.)*)"', t)
    i = re.search(r'"icon":\s*"([^"]*)"', t)
    return {"ascension": "record",
            "asc_name": n.group(1) if n else "",
            "asc_icon": i.group(1) if i else ""}


def sweep():
    import utility_tables as U
    rows = []
    for cat, _t, _n, _c, rs, _m in U.tables():
        for r in rs:
            rows.append({"cat": cat, "class": r[1], "spec": r[2],
                         "rc": r[3], "name": r[4], "sid": str(r[12])})
    spells = {}
    for i, r in enumerate(sorted(rows, key=lambda x: int(x["sid"]))):
        sid = r["sid"]
        where = {"class": r["class"], "spec": r["spec"], "cat": r["cat"]}
        if r["rc"]:
            where["node"] = r["rc"]
        # Two ids carry two rows each, and the second row is a second CLASS --
        # so the list has to be per row and not per spell, or the report names
        # one of the two classes that need checking.
        if sid in spells:
            spells[sid]["rows"].append(where)
            continue
        d = state(sid, r["name"])
        # exil.es is not queried: every row on the page IS a db.exil.es record,
        # read out of the mirror this repo already keeps. Stating it as a field
        # keeps the JSON readable as a two-column answer rather than one.
        d["exiles"] = True
        d["name"] = r["name"]
        d["rows"] = [where]
        spells[sid] = d
        if i % 40 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr, flush=True)
    return rows, spells


def main(argv):
    if "--report" in argv:
        doc = json.load(open(OUT, encoding="utf-8"))
    else:
        rows, spells = sweep()
        counts = {}
        for d in spells.values():
            counts[d["ascension"]] = counts.get(d["ascension"], 0) + 1
        doc = {
            "_comment": "Does db.ascension.gg have a record of each spell on "
                        "the raid utility page? Every row here is already a "
                        "db.exil.es record, so `no-record` means the ability "
                        "is on ONE of the two databases.",
            "_method": "tools/crosscheck.py -- `?spell=<id>&power`, which "
                       "answers even for ids whose HTML page 404s. A 43-byte "
                       "`registerSpell(id, 0, {})` is the absence. Every "
                       "absence is then re-asked BY NAME, because the two "
                       "databases do not agree on spell ids.",
            "_states": {
                "record": "same spell id on both databases, same name",
                "other-id": "both have the ability, under different ids -- "
                            "a pass, confirmed by reading both tooltips",
                "no-record": "db.exil.es only. A name search either found "
                             "nothing or found a different ability wearing "
                             "the same name; see `verdict`",
                "unreachable": "the request failed. Not a finding",
            },
            "_absence_is_not_proof": "Two no-record ids (500148 Solar Burn, "
                                     "560471 Hellgaze) were confirmed in game "
                                     "by hand on 2026-08-02. The page marks "
                                     "these rows 'in-game verification in "
                                     "process' and keeps them; only an in-game "
                                     "check can remove one.",
            "_scope": f"{len(rows)} rows, {len(spells)} unique spell ids",
            "counts": counts,
            "spells": dict(sorted(spells.items(), key=lambda kv: int(kv[0]))),
        }
        json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1,
                  ensure_ascii=False)
        print(f"wrote {OUT}", file=sys.stderr)

    miss = {k: v for k, v in doc["spells"].items()
            if v["ascension"] == "no-record"}
    print(f'{doc["_scope"]}  {doc["counts"]}')
    by = {}
    for sid, v in miss.items():
        for r in v["rows"]:
            by.setdefault(r["class"], []).append(
                (v["name"], sid, r["cat"], r["spec"], r.get("node", "")))
    for cls in sorted(by):
        print(f"\n{cls}")
        for name, sid, cat, spec, node in sorted(by[cls]):
            print(f"  {name:26} {sid:>7}  {cat:12} "
                  f"{spec}{' ' + node if node else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
