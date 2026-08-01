"""Fill in `abilities-<class>.md` roles from evidence, not from guesses.

    python3 tools/backfill_roles.py runemaster --dry-run   # propose, change nothing
    python3 tools/backfill_roles.py runemaster             # write the table

Only for a class whose pack ALREADY SHIPPED. Runemaster was built from six
hand-typed Python lists before mkabilities.py existed, so its inventory seeded
with all 170 rows marked `seed:` -- unreviewed -- despite the pack itself being
verified in game. Re-deciding 170 rows by hand would be re-deriving answers the
shipped pack already contains, and would introduce disagreements between the
table and the thing players are running.

THREE SOURCES OF EVIDENCE, strongest first. Every row this writes records
which one decided it, so a reviewer can see the basis rather than a bare role.

  1. THE SHIPPED PACK. A leaf's band IS its role -- that mapping is the whole
     point of the band layout. Verified in game, so it outranks everything.
     `RM Utility` merges defensive and utility into one row, so the split
     comes from the builder's DEFENSIVE list rather than from the band.

  2. A GENERIC DISPLAY. Engravings, etchings and tattoos are tracked
     COLLECTIVELY -- "RM Alert No Etching", "RM Engraving Fire" -- not one
     display per ability. Those abilities are covered without appearing by
     name, so matching on display id alone reports them as missing when they
     are not. This is the category a name match gets wrong in both directions.

  3. THE SKILLBOOK META. "Talent Passive" / "Ability Specialization" is not a
     button, so it is `ignore` with the meta quoted as the reason.

  4. db.exil.es SPELL META. `rank` plus the three cost axes settle the rest:
     an ability with no cooldown, no GCD and no mana cost is not something you
     press, whatever the skillbook calls it. `rank` in {Passive, Proc, Dummy,
     Stacks, Specialization} says the same thing directly. This is the source
     that turns "reads like a passive" into a fact, and it is why
     spell-meta-<class>.json is a prerequisite rather than an enrichment --
     Runemaster shipped without one, which is why 58 of its rows had no
     evidence to decide on.

Anything none of those settles is left as `seed:` and REPORTED. That residual
is the honest coverage gap, and it is the number worth looking at: an ability
with a real cooldown that the shipped pack does not render is either a missing
display or a deliberate omission, and only a human knows which.
"""
import argparse
import json
import os
import re
import sys

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import wacodec as w  # noqa: E402
from classes import get, data  # noqa: E402

# Band -> role. The layout standard's contract, read in the one direction that
# matters here.
BAND_ROLE = {
    "Main": "main",
    "Offense": "offensive",
    "Utility": "utility",     # refined by the builder's DEFENSIVE list
    "Buffs": "buff",
    "Longterm": "longterm",
    "Alerts": "reminder",
}

# Displays that stand for a WHOLE FAMILY of abilities rather than one each.
# Runemaster-shaped, because it is the only shipped class that predates
# mkabilities.py; a second class needing this should add its own families
# rather than generalise these.
#
# Matched on a NOUN SUFFIX, not on "contains the word". "Chaos Engraving" is
# an engraving; "Glyph Seeker" is a talent ABOUT glyphs and is not one, and a
# substring match files it as a resource -- which is how three talents and one
# real utility ability were mis-assigned on the first run of this tool.
GENERIC_SUFFIX = {
    "engraving": ("longterm", "tracked collectively by the per-element "
                              "RM Engraving displays and the No Engraving alert"),
    "tattoos": ("longterm", "tracked collectively by the per-element RM Tattoo "
                            "displays"),
}
# "Etching of the Magi", "Greater Etching of the Leylines" -- a prefix family.
GENERIC_PREFIX = {
    "etching": ("longterm", "tracked collectively by the per-element RM Tattoo "
                            "displays and the No Etching alert"),
}

PASSIVE_RE = re.compile(r"\b(Passive|Specialization|Proc)\b", re.I)

# db.exil.es `rank` values that mean "not a castable ability". Same list the
# id resolver uses to reject a row that links a component rather than a spell.
NON_CASTABLE_RANK = {"passive", "proc", "dummy", "stacks", "specialization",
                     "deprecated"}


def read_table(path):
    """[(kind, payload)] preserving every line, so a rewrite is lossless."""
    out = []
    for line in open(path, encoding="utf-8"):
        raw = line.rstrip("\n")
        if raw.startswith("| ") and raw.count("|") >= 6:
            cells = [c.strip() for c in raw.split("|")[1:-1]]
            if cells[0] not in ("Ability",) and set(cells[0]) != {"-"}:
                out.append(("row", cells))
                continue
        out.append(("raw", raw))
    return out


def write_table(path, items):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for kind, p in items:
            if kind == "row":
                f.write("| " + " | ".join(p) + " |\n")
            else:
                f.write(p + "\n")
    os.replace(tmp, path)


def _pack(cls):
    path = os.path.join(os.path.dirname(SP), "docs", "packs", cls.slug,
                        f"{cls.slug}-coa.txt")
    return w.wa_decode(open(path, encoding="utf-8").read())["c"].array_part()


def all_leaf_ids(cls):
    kids = _pack(cls)
    bands = {k["id"] for k in kids
             if k.get("regionType") in ("group", "dynamicgroup")}
    return [k["id"] for k in kids if k["id"] not in bands]


def pack_roles(cls, defensive):
    """{ability name: (role, evidence)} from the shipped pack's bands."""
    path = os.path.join(os.path.dirname(SP), "docs", "packs", cls.slug,
                        f"{cls.slug}-coa.txt")
    d = w.wa_decode(open(path, encoding="utf-8").read())
    kids = d["c"].array_part()
    bands = {k["id"] for k in kids
             if k.get("regionType") in ("group", "dynamicgroup")}
    leaves = [k for k in kids if k["id"] not in bands]
    out = {}
    for k in leaves:
        parent = k.get("parent", "")
        band = parent.split()[-1] if parent else ""
        role = BAND_ROLE.get(band)
        if not role:
            continue
        # "RM Glyphic Offense Frost Glyph" -> the band word is not always last
        # in the parent, so also try the second token.
        out.setdefault(k["id"], (role, f"shipped pack, band {parent}"))
    return out


def builder_defensive(cls):
    """The DEFENSIVE list, read out of the builder rather than re-derived."""
    src = open(os.path.join(SP, cls.builder), encoding="utf-8").read()
    m = re.search(r"^DEFENSIVE\s*=\s*\[(.*?)\]", src, re.S | re.M)
    if not m:
        return set()
    return set(re.findall(r'"([^"]+)"', m.group(1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cls")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cls = get(args.cls)

    inv = data(f"abilities-{cls.slug}.md")
    items = read_table(inv)
    rows = [p for k, p in items if k == "row"]

    defensive = builder_defensive(cls)
    leaf_roles = pack_roles(cls, defensive)
    # The glyph resources, read off the pack rather than guessed from the word
    # "glyph": the bar renders "RM Glyph Empty/Fill <Name>" per glyph, so that
    # display id set IS the list of abilities the bar stands in for.
    glyph_names = set()
    for leaf_id in all_leaf_ids(cls):
        m = re.match(r"^RM Glyph (?:Empty|Fill) (.+)$", leaf_id)
        if m:
            glyph_names.add(m.group(1).lower())
    skills_meta = {}
    try:
        sk = json.load(open(data(cls.skills), encoding="utf-8"))
        src = sk.items() if isinstance(sk, dict) else (
            (s.get("name"), s) for s in sk)
        for k, v in src:
            if isinstance(v, dict):
                skills_meta[v.get("name", k)] = v.get("meta", "") or ""
    except Exception:
        pass

    cds = {}
    try:
        cds = json.load(open(data(cls.cooldowns), encoding="utf-8"))
    except Exception:
        pass

    # db.exil.es meta, keyed by id -- re-key by name. A name can map to several
    # ids (ranks); keep the one with the most evidence of being castable, so a
    # ranked spell is not written off because rank 1 is a passive stub.
    smeta = {}
    meta_path = data(f"spell-meta-{cls.slug}.json")
    if os.path.exists(meta_path):
        for _id, v in json.load(open(meta_path, encoding="utf-8")).items():
            n = v.get("name")
            if not n:
                continue
            score = (v.get("cd_ms") or 0) + (v.get("gcd_ms") or 0) + \
                    (v.get("cost_pct") or 0)
            prev = smeta.get(n)
            if prev is None or score > prev[0]:
                smeta[n] = (score, v)
    else:
        print(f"  NOTE: {os.path.basename(meta_path)} is missing. Run "
              f"`python3 tools/spellmeta.py {cls.slug}` first -- without it "
              f"there is no evidence to decide a talent that has no cooldown "
              f"row, and those rows will stay undecided.\n")

    decided = {"pack": 0, "generic": 0, "passive": 0, "meta": 0}
    residual = []

    for cells in rows:
        name, note = cells[0], cells[5]
        if not note.startswith("seed:"):
            continue                     # a human already decided; never touch

        # 1. shipped pack
        hit = None
        for leaf_id, (role, why) in leaf_roles.items():
            if leaf_id == name or leaf_id.endswith(" " + name):
                hit = (role, why)
                break
        if hit:
            role, why = hit
            if role == "utility" and name in defensive:
                role, why = "defensive", why + " (builder DEFENSIVE list)"
            cells[3] = role
            cells[5] = f"{why}; verified in game"
            decided["pack"] += 1
            continue

        # 2. a generic display covers this family
        low = name.lower()
        fam = None
        if low in glyph_names:
            fam = ("resource", "Glyphic's glyph bar renders these as segments, "
                               "not as their own icons")
        else:
            for suf, v in GENERIC_SUFFIX.items():
                if low.endswith(" " + suf) or low == suf:
                    fam = v
                    break
            if fam is None:
                for pre, v in GENERIC_PREFIX.items():
                    # "Etching of ...", "Greater Etching of ..."
                    if re.search(rf"\b{pre}\b of\b", low):
                        fam = v
                        break
        if fam:
            cells[3], cells[5] = fam[0], fam[1]
            decided["generic"] += 1
            continue

        # 3. skillbook meta says it is not a button
        meta = skills_meta.get(name, "")
        seed_meta = re.search(r"seed: ([^;]+)", note)
        meta = meta or (seed_meta.group(1).strip() if seed_meta else "")
        if meta and PASSIVE_RE.search(meta):
            cells[3] = "ignore"
            cells[5] = f'skillbook says "{meta}" -- not a player button'
            decided["passive"] += 1
            continue

        # 4. db.exil.es meta: rank, or the absence of every cost axis
        sm = smeta.get(name)
        if sm:
            v = sm[1]
            rank = (v.get("rank") or "").strip()
            cd, gcd, cost = (v.get("cd_ms") or 0, v.get("gcd_ms") or 0,
                             v.get("cost_pct") or 0)
            if rank.lower() in NON_CASTABLE_RANK:
                cells[3] = "ignore"
                cells[5] = f'db.exil.es rank={rank} -- not a castable ability'
                decided["meta"] += 1
                continue
            if cd == 0 and gcd == 0 and cost == 0:
                cells[3] = "ignore"
                cells[5] = ("db.exil.es: no cooldown, no GCD, no cost -- an "
                            "effect, not a button")
                decided["meta"] += 1
                continue

        residual.append((name, meta, name in cds))

    # The inventory's membership set is the skillbook union the cooldown
    # audit. Neither is the pack. So an ability the SHIPPED PACK RENDERS can be
    # absent from the inventory entirely, and nothing else would ever say so --
    # the seed cannot report a row it never created.
    #
    # Runemaster shipped exactly this: the skillbook carries "Frost Glyph" and
    # not "Flame Glyph" or "Arcane Glyph", while the Glyphic bar renders all
    # three. Coverage measured against the inventory alone reported 100%.
    known = {c[0] for c in rows}
    orphans = []
    for leaf_id in all_leaf_ids(cls):
        if any(leaf_id == n or leaf_id.endswith(" " + n) for n in known):
            continue
        orphans.append(leaf_id)
    if orphans:
        print(f"\n  {len(orphans)} display(s) the pack RENDERS with no "
              f"inventory row. Coverage cannot be 100% while this is nonzero:")
        for o in sorted(orphans)[:20]:
            print(f"      {o}")
        if len(orphans) > 20:
            print(f"      ... and {len(orphans) - 20} more")
        print()

    print(f"{cls.name}: {len(rows)} rows")
    print(f"  {decided['pack']:3d}  role from the shipped pack's band")
    print(f"  {decided['generic']:3d}  covered by a generic family display")
    print(f"  {decided['passive']:3d}  not a button, per the skillbook")
    print(f"  {decided['meta']:3d}  not a button, per db.exil.es rank/cost")
    print(f"  {len(residual):3d}  UNDECIDED -- left as seed:")

    withcd = [r for r in residual if r[2]]
    if withcd:
        print(f"\n  {len(withcd)} of the undecided have a REAL COOLDOWN and are "
              f"not in the pack.\n  Each is either a missing display or a "
              f"deliberate omission; only a human knows which:")
        for n, m, _ in withcd:
            print(f"      {n:<34} {m}")
    rest = [r for r in residual if not r[2]]
    if rest:
        print(f"\n  {len(rest)} undecided with no cooldown row:")
        for n, m, _ in rest[:40]:
            print(f"      {n:<34} {m}")
        if len(rest) > 40:
            print(f"      ... and {len(rest) - 40} more")

    if args.dry_run:
        print("\ndry run -- nothing written")
        return 0
    write_table(inv, items)
    print(f"\nwrote {inv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
