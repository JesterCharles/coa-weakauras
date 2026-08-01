"""Seed the per-class ability inventory -- what renders, where, and as what.

    python3 tools/mkabilities.py chronomancer          # seed / refresh
    python3 tools/mkabilities.py chronomancer --check   # report gaps only

Writes `resources/abilities-<class>.md`, a reviewable table that becomes the
SOURCE OF TRUTH for the builder's category lists.

WHY THIS EXISTS. The categories used to be six hand-typed Python lists inside
build_<class>.py (OFFENSIVE, DEFENSIVE, ELSEWHERE, ...). At one class that is
fine. At 21 it is 126 lists, and nothing can tell you what a list is MISSING --
which is how Arc Collision never made it into Chronomancer at all, and how four
survival cooldowns ended up in the offensive row. A table you can read start to
finish makes both kinds of error visible.

WHERE THE SEED COMES FROM, and why it changed.

The first version seeded from `cooldown-abilities-<class>.json` alone -- the
db.exil.es cooldown scrape. That has a hole with a bias: **an ability with no
cooldown is never discovered.** The abilities that lack a cooldown row are
fillers, spenders and direct heals, i.e. the main rotation, so the scrape was
blindest at exactly the abilities that matter most. Three were lost that way
and each was caught by a player, not by the tooling:

    Arc Collision   524853
    Waves of Time   801265
    Reverse Wound   801303   -- a level-1, 31%-mana direct heal, mentioned 13
                                times in the Time sidekick, present ZERO times
                                in the inventory

So the seed is now the class SKILLBOOK, `coa-<class>-skills.json` (what the
character can actually learn), unioned with the cooldown audit for the handful
of names the skills page omits. The cooldown audit is demoted to ENRICHMENT:
it supplies cooldown, GCD and spec, it no longer decides membership. The review
step becomes "assign a role", not "notice what is absent".

    coa-<class>-skills.json    membership. name, icon, and a `meta` string
                               like "Ability Lvl 10 · max L58" or "Talent
                               Passive"
    cooldown-abilities-*.json  membership too (14 real names the skills page
                               misses), then enrichment: id, specs
    exiles-<class>.json        id resolution, and the CANDIDATES list below
    spell-meta-<class>.json    rank, level, cost -- from the db.exil.es JSON API

CANDIDATES. `exiles-<class>.json` is a raw name search (476 rows for
Chronomancer against the skillbook's 181). Most of the surplus is components,
hidden passives, triggers, dummies and per-stack auras -- dumping it into the
table would make the table unreadable, which is the one thing it must not be.
Instead, exiles rows that are NOT in the seed and that LOOK castable (a GCD or
a mana cost) are listed under `## Candidates` at the bottom as a bullet list,
not a table -- the builder's parser only reads pipe rows, so candidates cannot
reach a pack by accident. Decide one by writing it into the table; it then
drops out of the candidate list on the next refresh because it is a known name.

SPECS ARE NOT INFERRED. Sidekick mention counts look like a great spec signal
and are not: checked against the 80 hand-reviewed Chronomancer rows they get 42
right, 27 too broad, and **11 wrong**. A wrong narrow hides an ability from a
spec, which is the same failure this file exists to prevent. New rows get
`all`, and the mention counts go in Notes as a hint for whoever reviews.

COLUMNS

    Ability   display name, and the key everything else joins on
    ID        the CASTABLE spell id -- not a rank, not a component
    Specs     which specs can use it; `all` means the whole class
    Role      where it renders (below)
    Rank      the db.exil.es rank_text, kept because it decides gating
    Notes     free text, and the place to record a decision

ROLES, in priority order. An ability that could be two things takes the FIRST
that applies, so the order is the tie-break:

    main       core rotation, 44px row. One per spec, hand-picked
    offensive  damage cooldowns
    defensive  survival, mitigation, damage undo
    utility    everything else with a cooldown: dispels, control, movement
    resource   drives a bar or a segment, never its own icon
    buff       tracked as an aura in the "on me" row, not as a cooldown
    target     tracked on your target (your DoTs / your HoTs)
    longterm   30-minute self buffs and stances
    ignore     not a player button at all -- pet spells, components, procs

`ignore` is load-bearing. Chronomancer's five "Chronobuff" abilities carry
cooldowns and look like buttons in every scrape, but their tooltips give them
away as the PET's spellbook ("Shroud your MASTER"). Without a place to write
that down, every future scrape re-adds them.

The seed is a STARTING POINT, not an answer. Hand edits always win on refresh.
A skillbook entry the page marks Passive seeds as `ignore` (a passive is not a
button, and the ones worth showing need a "Spell Known" trigger rather than a
cooldown icon); everything else seeds as `utility`, the row most likely to be
wrong. Read it, fix it, and the builder follows.
"""
import json
import os
import re
import sys

from classes import data, dest, get

ROLES = ["main", "offensive", "defensive", "utility", "resource", "buff",
         "target", "longterm", "ignore"]

HEADER = ("| Ability | ID | Specs | Role | Rank | Notes |\n"
          "|---|---|---|---|---|---|\n")

# Marks a Notes cell the seeder wrote and nobody has looked at. Delete it (or
# replace the note) to mark the row reviewed.
SEED = "seed: "

# A skills-page `meta` reads like "Ability Lvl 10 · max L58" or "Talent
# Passive". Only the two leading words carry a decision: is it a Talent or a
# baseline Ability, and is it Passive.
RANK_IN_META = re.compile(r"\b(Rank \d+|Specialization|Chronobuff)\b")


def read(path):
    """Parse an existing inventory so a refresh never clobbers hand edits."""
    rows = {}
    if not os.path.exists(path):
        return rows
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 6 or cells[0] in ("Ability",):
            continue
        rows[cells[0]] = cells
    return rows


def load_json(path, what):
    """Read a required data file, or say which scrape has not been run.

    Deliberately NOT a silent `{}` fallback. A missing skillbook used to mean
    the seeder quietly fell back to the cooldown audit and reported success
    with a third of the class missing -- the exact silent no-op this pipeline
    keeps getting bitten by.
    """
    if not os.path.exists(path):
        raise SystemExit(
            f"missing {what}: {path}\n"
            f"  the inventory seeds from the class skillbook; run the scrape "
            f"that produces this file before seeding.")
    return json.load(open(path, encoding="utf-8"))


def sidekick_hits(cls, name):
    """How often each spec's sidekick names this ability.

    A HINT ONLY -- see the module docstring. Never narrows the Specs column.
    Word-bounded so `Ripple` does not also count `A Ripple In Time`.
    """
    pat = re.compile(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])",
                     re.I)
    out = {}
    for spec in cls.specs:
        path = data(cls.sidekick(spec))
        if not os.path.exists(path):
            continue
        out[spec] = len(pat.findall(open(path, encoding="utf-8").read()))
    return out


def seed_note(meta_str, hits):
    """Provenance for a freshly-seeded row: what the skills page called it,
    and which sidekicks talk about it. Both are what a reviewer needs to
    place the ability, and neither is recoverable once the row exists.

    The `seed:` prefix is the review marker, and it is a marker rather than an
    inference on purpose. Counting "unreviewed" as "role is utility and Notes
    is empty" stopped working the moment the seeder started writing Notes --
    it reported 3 of 125 fresh rows as needing a decision. A reviewer deletes
    the prefix (or replaces the note) and the row stops being counted.
    """
    bits = []
    if meta_str:
        bits.append(meta_str)
    seen = "/".join(f"{s[0]}{n}" for s, n in hits.items() if n)
    if seen:
        bits.append(f"sidekicks {seen}")
    elif hits:
        bits.append("no sidekick mention")
    return SEED + "; ".join(bits)


def candidates(exiles, meta, known):
    """exiles rows outside the seed that look like a player button.

    `gcd_ms` or `cost_pct` is the filter: a component, a hidden passive or a
    per-stack aura has neither. It over-reports (48 rows for Chronomancer,
    including deprecated spells and near-name traps) and that is the intent --
    a candidate costs one line to dismiss and a miss costs a shipped pack.
    """
    out = []
    for name in sorted(set(exiles) - known):
        ids = exiles[name].get("ids") or []
        if not ids:
            continue
        m = meta.get(str(ids[0]), {})
        if (m.get("gcd_ms") or 0) > 0 or (m.get("cost_pct") or 0) > 0:
            out.append((name, ids[0], m))
    return out


def main(argv):
    check_only = "--check" in argv
    argv = [a for a in argv if not a.startswith("--")]
    cls = get(argv[0] if argv else "runemaster")

    skills = load_json(data(cls.skills), f"{cls.name} skillbook")
    exiles = load_json(data(cls.exiles), f"{cls.name} spell search")
    cds = load_json(data(cls.cooldowns), f"{cls.name} cooldown audit")
    meta_path = data(f"spell-meta-{cls.slug}.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}

    out_path = dest(f"abilities-{cls.slug}.md")
    existing = read(out_path)

    # MEMBERSHIP: the skillbook, plus the names only the cooldown audit knows
    # (14 for Chronomancer -- Wand of Time, Timeguard, Chronobeam and friends),
    # plus anything already reviewed. The audit no longer decides on its own.
    book = {s["name"]: s for s in skills}
    names = set(book) | set(cds) | set(existing)

    rows, added = [], []
    for name in sorted(names):
        if name in existing:
            rows.append(existing[name])           # hand edits win, always
            continue
        cd = cds.get(name, {})
        sid = cd.get("id") or (exiles.get(name, {}).get("ids") or [""])[0]
        m = meta.get(str(sid), {})
        meta_str = (book.get(name) or {}).get("meta", "")

        specs = ",".join(cd.get("specs") or []) or "all"
        rank = m.get("rank") or ""
        if not rank:
            found = RANK_IN_META.search(meta_str)
            rank = found.group(1) if found else ""
        # A passive is not a button. Seeding it `utility` puts 56 non-buttons
        # in the row a reviewer is meant to scrutinise; `ignore` keeps the
        # decision visible without drowning the real work.
        role = "ignore" if "Passive" in meta_str else "utility"
        note = seed_note(meta_str, sidekick_hits(cls, name))

        row = [name, str(sid), specs, role, rank, note]
        rows.append(row)
        added.append(row)

    cand = candidates(exiles, meta, set(names))

    body = "".join("| " + " | ".join(r) + " |\n" for r in rows)
    text = (f"# {cls.name} — ability inventory\n\n"
            f"What renders, where, and as what. Generated by\n"
            f"`tools/mkabilities.py {cls.slug}`; **hand edits are preserved** "
            f"on refresh.\n\n"
            f"Seeded from the class skillbook (`{cls.skills}`), not the "
            f"cooldown audit —\nan ability with no cooldown has no audit row, "
            f"which is how Reverse Wound,\nArc Collision and Waves of Time "
            f"were missed. The audit only enriches now.\n\n"
            f"Role priority: {' > '.join(ROLES[:4])}. An ability that could be\n"
            f"two things takes the first that applies.\n\n"
            f"A Notes cell starting `{SEED.strip()}` is a row the seeder wrote "
            f"and nobody has\nreviewed. Delete the prefix once you have placed "
            f"the ability.\n\n"
            f"Role and ID both take per-spec overrides, `<default>; "
            f"<spec>:<value>`:\n"
            f"`defensive; time:offensive` renders one ability in two different "
            f"rows, and\n`520188; time:801280` covers the case where one NAME "
            f"is two different\nspells — the specs that have no override use "
            f"the default.\n\n"
            + HEADER + body)

    if cand:
        text += (f"\n## Candidates\n\n"
                 f"In `{cls.exiles}` but not in the skillbook or the cooldown "
                 f"audit, and\ncarrying a GCD or a mana cost — so possibly a "
                 f"player button we have not\nplaced. Most are components, "
                 f"deprecated spells or near-name traps.\n\n"
                 f"Decide one by writing it into the table above; it leaves "
                 f"this list on the\nnext refresh. Bullets, not a table, so "
                 f"the builder's parser cannot read them.\n\n")
        for name, sid, m in cand:
            desc = ", ".join(
                f"{k}={m[k]}" for k in ("level", "gcd_ms", "cost_pct", "rank")
                if m.get(k))
            text += f"- `{sid}` **{name}** — {desc or 'no metadata'}\n"

    unreviewed = [r for r in rows if r[5].startswith(SEED)]
    ranked = [r for r in rows if r[4].startswith("Rank ")]
    # The ID cell may carry per-spec overrides -- "520188; time:801280" for an
    # ability that is genuinely two spells. The row is built iff its DEFAULT id
    # (the part before the first `;`) is real, so split before testing or every
    # split ability is reported as unbuildable.
    no_id = [r for r in rows if not r[1].split(";")[0].strip().isdigit()]

    if not check_only:
        open(out_path, "w", encoding="utf-8").write(text)
        print(f"wrote {out_path}")
    print(f"  {len(rows)} abilities "
          f"({len(book)} skillbook, {len(cds)} cooldown audit, "
          f"{len(existing)} already reviewed)")
    print(f"  {len(added)} NEW this run")
    for r in added[:40]:
        print(f"     {r[0][:34]:34} {r[1]:>8} {r[3]:<9} {r[5][:44]}")
    if len(added) > 40:
        print(f"     ... and {len(added) - 40} more")
    print(f"  {len(unreviewed)} still carry the `{SEED.strip()}` marker and "
          f"need a decision")
    print(f"  {len(ranked)} are RANKED -- these cannot be gated or matched "
          f"on an exact id")
    if no_id:
        print(f"  {len(no_id)} have NO id and cannot be built: "
              f"{', '.join(r[0] for r in no_id[:6])}")
    print(f"  {len(cand)} candidates in {cls.exiles} not yet placed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
