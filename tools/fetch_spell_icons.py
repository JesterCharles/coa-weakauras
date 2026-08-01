"""Resolve icon art per spell id from db.ascension.gg, for any class.

    python3 tools/fetch_spell_icons.py chronomancer
    python3 tools/fetch_spell_icons.py chronomancer --only 561284,680456

Writes `resources/icon-meta-<class>.json` as `{"<id>": "<texture>"}`.

WHY NOT fetch_icons.py. That one is hardcoded to Runemaster, writes the
single shared `exiles-id-meta.json`, and drives every lookup through Firecrawl
at ~4s per spell. This needs neither: db.ascension.gg serves the data to plain
`curl`, and its spell pages embed a `g_spells` map:

    var _ = g_spells; _[561284]={"icon":"inv_wand_16","name_enus":"Artificer's Wand"};

Crucially each page carries that line for EVERY spell it references -- ranks,
procs, triggered spells, whatever the tooltip links. So harvesting all matches
from each page rather than just the requested one means the set closes fast:
Chronomancer resolves in a fraction of the requests a naive one-page-per-id
loop would make.

Pages cache under tools/spellchk/ (shared with audit_cds.py), so reruns are
free and a partial run can just be repeated.
"""
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from classes import data, dest, get, SP

CACHE = os.path.join(SP, "spellchk")
os.makedirs(CACHE, exist_ok=True)

# _[<id>]={"icon":"<texture>","name_enus":"<name>"}
G_SPELLS = re.compile(r'_\[(\d+)\]=\{"icon":"([^"]+)","name_enus":"((?:[^"\\]|\\.)*)"')
QM = "inv_misc_questionmark"


def page(sid):
    """Raw HTML for one spell page, cached on disk."""
    p = os.path.join(CACHE, f"asc-{sid}.html")
    if not (os.path.exists(p) and os.path.getsize(p) > 2000):
        subprocess.run(
            ["curl", "-s", "-m", "25", f"https://db.ascension.gg/?spell={sid}",
             "-o", p], check=False, timeout=40)
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def harvest(html):
    """Every id -> texture the page mentions, not just the one asked for."""
    out = {}
    for sid, icon, _name in G_SPELLS.findall(html):
        if icon and icon != QM:
            out[sid] = icon
    return out


def main(argv):
    only = None
    if "--only" in argv:
        i = argv.index("--only")
        only = [s.strip() for s in argv[i + 1].split(",") if s.strip()]
        del argv[i:i + 2]

    cls = get(argv[0] if argv else "runemaster")
    exiles = json.load(open(data(cls.exiles)))
    want = only or sorted({str(i) for v in exiles.values() for i in v["ids"]})

    out_path = dest(f"icon-meta-{cls.slug}.json")
    known = {}
    if os.path.exists(out_path):
        known = json.load(open(out_path))

    todo = [s for s in want if s not in known]
    print(f"{cls.name}: {len(want)} ids, {len(known)} already known, "
          f"{len(todo)} to fetch")

    done = 0
    while todo:
        batch, todo = todo[:24], todo[24:]
        # Re-check: an earlier page in this run may already have supplied it.
        batch = [s for s in batch if s not in known]
        if not batch:
            continue
        with ThreadPoolExecutor(max_workers=6) as pool:
            for html in pool.map(page, batch):
                known.update(harvest(html))
        done += len(batch)
        todo = [s for s in todo if s not in known]
        print(f"  fetched {done}, resolved {len(known)}, {len(todo)} left")

    json.dump(dict(sorted(known.items(), key=lambda kv: int(kv[0]))),
              open(out_path, "w"), indent=1)
    missing = [s for s in want if s not in known]
    print(f"\nwrote {out_path}")
    print(f"  {len(known)} ids carry art")
    if missing:
        # db.ascension serves a questionmark on these spells' own pages, so it
        # is absent upstream rather than a scrape miss. Cosmetic, and the fix
        # is art chosen by hand into the builder's OVERRIDE.
        by_name = {i: n for n, v in exiles.items() for i in map(str, v["ids"])}
        print(f"  {len(missing)} have no art upstream: "
              f"{', '.join(sorted(by_name.get(m, m) for m in missing)[:12])}"
              f"{' ...' if len(missing) > 12 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
