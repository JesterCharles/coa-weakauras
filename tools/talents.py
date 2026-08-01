"""The official talent trees, from ascension.gg's own builder.

    python3 tools/talents.py --refresh              # re-download the builder
    python3 tools/talents.py runemaster             # extract + report
    python3 tools/talents.py runemaster --gaps      # inventory vs tree only

WHY THE OFFICIAL BUILDER. Sidekick says what a class can do and says outright
that optimal order is unsettled. Logs say what people actually took, and that
source does not permit automated reads. The builder says what the tree ALLOWS,
which is the game operator's own definition and therefore not an inference from
anything. ascension.gg publishes `Allow: /` for every agent including ClaudeBot,
with a comment inviting citation, so this is the one authoritative source that
is also freely readable.

WHERE THE DATA IS. The builder is a Next.js App Router page and the tree ships
in its RSC flight payload -- 294 `self.__next_f.push([1,"..."])` chunks which
concatenate into one 9MB string holding a `talents` object:

    classes[]        classId, className, tabs[] {tabId, tabName, sortOrder}
    entriesByTab     "<classId>:<tabId>" -> [node, ...]
    essenceByClass   the level-30+ Ability Essence system

A node carries everything needed to reason about a build:

    x, y             position in the tree grid
    spellId/spellIds THE JOIN back to abilities-<class>.md
    teCost, aeCost   talent point cost
    reqTabTE         points required in this tab before the node unlocks
    maxPoints        ranks
    entryType        Ability = grants a castable, Talent = a passive modifier
    isPassive        DO NOT USE -- see below
    description      the full tooltip

`isPassive` IS UNRELIABLE and reading it produces confident nonsense. On
Runemaster it reports 0 for 145 of 160 nodes, including "Graceful" (increases
your haste by 5%) and "Glyph God" (reduces the cooldown of Glyphic Overload) --
both unambiguously passive. Trusting it reported 38 talent-granted buttons we
supposedly did not track, every one of which was a passive stat modifier.

`entryType` is the flag that works, and it is verifiable rather than asserted:
its 33 `Ability` nodes on Runemaster have an inventory row 33 times out of 33,
while its 127 `Talent` nodes hit 68% -- exactly the split you expect if one
means "grants a button" and the other means "changes how a button behaves".
That 33/33 is also the useful result: the game's own tree agrees our inventory
covers every talent-granted ability.

TAB NAMES DO NOT MATCH SPEC NAMES, and this is the trap. Runemaster's tabs are
`Runic`, `Arcane` and `Riftblade`, while its specs are Glyphic, Engravement and
Riftblade -- and the mapping is NOT the obvious one:

    Glyphic     -> tab 11 "Arcane"      (not "Runic")
    Engravement -> tab 85 "Runic"       (not "Arcane")
    Riftblade   -> tab 86 "Riftblade"

Nobody would guess that, and `sortOrder` is 0 on all four Runemaster tabs so it
cannot break the tie either. Chronomancer and Pyromancer DO match by name, and
both carry a junk tab that is not a spec at all (`Blessings`, `None`). So the
resolution order is: match by name, else match by the spec's SPEC_KNOWN
signature spell, else report the tab as unmapped rather than guessing.

The signature fallback is itself incomplete on purpose -- SPEC_KNOWN holds a
gating ABILITY, which is not always a talent. Chronomancer's Infinite signature
(Maw of Chaos) is baseline and appears in no tree, so Infinite maps by name and
would have no fallback if it did not. Both paths exist because neither is
sufficient alone.
"""
import argparse
import json
import os
import re
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import sources  # noqa: E402
from classes import CLASSES, get, data, dest  # noqa: E402

URL = "https://ascension.gg/en/v2/coa-builder/voljin"
CACHE = "talents-voljin.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def download():
    """Fetch the builder and extract just the talents object.

    The page is 11.8MB and 95% of it is markup we will never read. Caching the
    extracted 4MB object instead keeps the committed snapshot reviewable and
    means a re-parse does not re-run the flight reassembly.
    """
    sources.require(URL)
    import urllib.request
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        html = r.read().decode("utf-8", "replace")
    chunks = re.findall(
        r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', html)
    if not chunks:
        raise SystemExit(
            "talents: no RSC flight chunks found. The builder probably stopped "
            "being a Next.js App Router page; re-check the payload shape.")
    payload = "".join(json.loads('"' + c + '"') for c in chunks)
    i = payload.find('{"meta":{"runtimeBuildProcess"')
    if i < 0:
        raise SystemExit("talents: flight payload has no talents object")
    depth, j = 0, i
    while j < len(payload):
        if payload[j] == "{":
            depth += 1
        elif payload[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    obj = json.loads(payload[i:j + 1])
    p = dest(CACHE)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"  {len(obj['classes'])} classes, "
          f"{sum(len(v) for v in obj['entriesByTab'].values())} talent nodes "
          f"-> {p}")
    return obj


def bundle(refresh=False):
    p = data(CACHE)
    if refresh or not os.path.exists(p):
        return download()
    return json.load(open(p, encoding="utf-8"))


def spec_known(cls):
    """SPEC_KNOWN from the class builder -- signature spell per spec."""
    p = os.path.join(SP, cls.builder)
    if not os.path.exists(p):
        return {}
    src = open(p, encoding="utf-8").read()
    m = re.search(r"^SPEC_KNOWN\s*=\s*\{(.*?)\}", src, re.S | re.M)
    if not m:
        return {}
    return {_slug(k): int(v)
            for k, v in re.findall(r'"([^"]+)"\s*:\s*(\d+)', m.group(1))}


def map_tabs(cls, tabs, nodes_by_tab, sigs):
    """{spec: tabId} plus ('class', tabId) and the tabs we could not place."""
    out, unmapped = {}, []
    by_name = {_slug(t["tabName"]): t["tabId"] for t in tabs}
    for spec in cls.specs:
        if spec in by_name:
            out[spec] = by_name[spec]
    # signature spell for anything the names did not settle
    if len(out) < len(cls.specs):
        where = {}
        for tid, nodes in nodes_by_tab.items():
            for n in nodes:
                for s in (n.get("spellIds") or [n.get("spellId")]):
                    if s:
                        where.setdefault(int(s), set()).add(tid)
        for spec in cls.specs:
            if spec in out:
                continue
            hits = where.get(sigs.get(spec) or -1) or set()
            # A signature that lands in exactly one tab is a mapping. Two would
            # be ambiguous and is not worth a guess.
            if len(hits) == 1:
                out[spec] = next(iter(hits))
    claimed = set(out.values())
    class_tab = by_name.get("class")
    for t in tabs:
        if t["tabId"] in claimed or t["tabId"] == class_tab:
            continue
        unmapped.append((t["tabId"], t["tabName"]))
    return out, class_tab, unmapped


def extract(cls, asc):
    """Per-class talent data, spec-keyed, ready to write."""
    entry = next((c for c in asc["classes"] if c["classId"] == cls.id), None)
    if entry is None:
        raise SystemExit(f"talents: no builder entry for {cls.name} "
                         f"(classId {cls.id})")
    nodes_by_tab = {}
    for k, v in asc["entriesByTab"].items():
        c, t = k.split(":")
        if int(c) == cls.id:
            nodes_by_tab[int(t)] = v
    sigs = spec_known(cls)
    spec_tab, class_tab, unmapped = map_tabs(
        cls, entry["tabs"], nodes_by_tab, sigs)

    def clean(n):
        return {
            "id": n.get("id"), "name": n.get("name"),
            "spell_ids": [s for s in (n.get("spellIds")
                                      or [n.get("spellId")]) if s],
            "x": n.get("x"), "y": n.get("y"),
            "te_cost": n.get("teCost"), "ae_cost": n.get("aeCost"),
            "req_tab_te": n.get("reqTabTE"), "max_points": n.get("maxPoints"),
            # entryType, not isPassive -- see the module docstring.
            "grants_ability": n.get("entryType") == "Ability",
            "entry_type": n.get("entryType"),
        }

    out = {
        "class": cls.slug, "class_id": cls.id,
        "source": "ascension.gg", "source_url": URL,
        "realm": asc.get("meta", {}).get("runtimeBuildProcess", ""),
        "class_tab": [clean(n) for n in nodes_by_tab.get(class_tab or -1, [])],
        "specs": {spec: [clean(n) for n in nodes_by_tab.get(tid, [])]
                  for spec, tid in spec_tab.items()},
        "tab_map": {spec: {"tab_id": tid,
                           "tab_name": next(t["tabName"] for t in entry["tabs"]
                                            if t["tabId"] == tid)}
                    for spec, tid in spec_tab.items()},
        "unmapped_tabs": [{"tab_id": t, "tab_name": n} for t, n in unmapped],
        "missing_specs": [s for s in cls.specs if s not in spec_tab],
    }
    return out


def report(cls, tal):
    names = {}
    p = data(f"abilities-{cls.slug}.md")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if line.startswith("| ") and line.count("|") >= 6:
                c = [x.strip() for x in line.split("|")[1:-1]]
                if c[0] and c[0] != "Ability" and set(c[0]) != {"-"}:
                    names[c[0]] = c[3]

    print(f"\n{cls.name}  --  official talent tree")
    for spec, meta in sorted(tal["tab_map"].items()):
        nodes = tal["specs"][spec]
        act = [n for n in nodes if n["grants_ability"]]
        print(f"  {spec:<14} tab {meta['tab_id']:>3} {meta['tab_name']!r:<14} "
              f"{len(nodes):>3} nodes, {len(act):>2} grant a button")
        if _slug(meta["tab_name"]) != spec:
            print(f"                 NAME MISMATCH: the builder calls this "
                  f"tab {meta['tab_name']!r}, resolved by signature spell")
    print(f"  {'class tree':<14} {'':>3} {'':<16} {len(tal['class_tab']):>3} "
          f"nodes, shared by every spec")
    if tal["unmapped_tabs"]:
        print(f"  unmapped tabs (not one of this class's specs): "
              f"{', '.join(repr(t['tab_name']) for t in tal['unmapped_tabs'])}")
    if tal["missing_specs"]:
        print(f"  NO TREE FOUND for: {', '.join(tal['missing_specs'])} -- "
              f"neither the tab name nor the signature spell resolved it")

    # The join that matters: which talents grant an ability we track, and
    # which grant one we have never heard of.
    tracked, untracked = [], []
    for spec, nodes in sorted(list(tal["specs"].items())
                              + [("class tree", tal["class_tab"])]):
        for n in nodes:
            if not n["grants_ability"] or not n["name"]:
                continue
            (tracked if n["name"] in names else untracked).append((spec, n))
    total = len(tracked) + len(untracked)
    print(f"\n  {len(tracked)}/{total} talent-granted abilities have an "
          f"inventory row")
    if untracked:
        print(f"  {len(untracked)} the official tree grants and we do NOT "
              f"track -- each is a coverage hole in a shipped pack:")
        for spec, n in untracked:
            ids = ", ".join(str(s) for s in n["spell_ids"]) or "no spell id"
            print(f"      {spec:<12} {n['name']:<28} {ids}")
    else:
        print("  no holes: every ability the official tree can grant is "
              "already tracked")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cls", nargs="?")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--gaps", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    asc = bundle(args.refresh)
    if not args.cls and not args.all:
        if args.refresh:
            return 0
        ap.error("give a class slug, or --all, or --refresh")

    targets = (sorted(CLASSES.values(), key=lambda c: c.id) if args.all
               else [get(args.cls)])
    for cls in targets:
        try:
            tal = extract(cls, asc)
        except SystemExit as e:
            print(f"{cls.name}: {e}")
            continue
        p = dest(f"talents-{cls.slug}.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(tal, f, indent=1, ensure_ascii=False)
            f.write("\n")
        if not args.gaps:
            report(cls, tal)
        print(f"  wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
