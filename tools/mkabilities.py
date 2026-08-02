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

from classes import SP, data, dest, get

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


def pack_refs(cls, exiles, meta):
    """{display id: {ability names it references}} for the BUILT PACK.

    The third membership source, and the only one that cannot be short.

    The skillbook and the cooldown audit are both scrapes of somebody else's
    page, and both have been wrong in the same direction: Runemaster's
    skillbook held 150 entries and omitted Runeblade, Runic Explosion,
    Hoarfrost and Tempo -- abilities the shipped pack RENDERS. A row that is
    never created cannot be reported missing, so coverage measured against
    those two sources alone read 100% while the main rotation was incomplete.

    A pack, by contrast, cannot reference an ability it does not have. So
    whatever it points at is a floor on membership: if we are drawing it, it
    needs a row.

    Read from TRIGGERS, not from display ids. Ids like "RM Engravement Main
    Runic Explosion" would need per-class band-prefix stripping, which is one
    more thing to maintain per class and gets Chronomancer's "CM Artificer
    Utility Buy Time" wrong the moment a band is renamed. Triggers carry the
    spell directly and mean the same thing in every class:

        spell   spellName          an id or a name
        aura2   auranames          MIXED ids and names, in one table
                auraspellids       ids, when useExactSpellId is set
        item    enchant            a weapon-enchant name

    `unit` triggers (the mana and resource bars) carry no ability and drop out
    on their own, which is why resource displays do not pollute the result.
    """
    path = os.path.join(os.path.dirname(SP), "docs", "packs", cls.slug,
                        f"{cls.slug}-coa.txt")
    if not os.path.exists(path):
        return {}
    import wacodec as w
    kids = w.wa_decode(open(path, encoding="utf-8").read())["c"].array_part()
    bands = {k["id"] for k in kids
             if k.get("regionType") in ("group", "dynamicgroup")}

    # id -> name, so a trigger holding only an id still names its ability.
    by_id = {}
    for n, v in exiles.items():
        for i in (v.get("ids") or []):
            by_id.setdefault(str(i), n)
    for i, v in meta.items():
        if v.get("name"):
            by_id.setdefault(str(i), v["name"])

    def vals(x):
        if isinstance(x, dict):
            return list(x.values())
        if isinstance(x, (list, tuple)):
            return list(x)
        return [x] if x else []

    out = {}
    for k in kids:
        if k["id"] in bands:
            continue
        trs = k.get("triggers") or {}
        names = set()
        for e in (trs.values() if isinstance(trs, dict) else trs):
            tr = e.get("trigger") if isinstance(e, dict) else None
            if not isinstance(tr, dict):
                continue
            raw = []
            if tr.get("type") == "spell":
                raw += vals(tr.get("spellName"))
            elif tr.get("type") == "aura2":
                raw += vals(tr.get("auranames")) + vals(tr.get("auraspellids"))
            elif tr.get("type") == "item":
                raw += vals(tr.get("enchant"))
            for r in raw:
                s = str(r).strip()
                if not s:
                    continue
                # A trigger entry is either an id or a display name. Resolve
                # ids where we can and drop the ones we cannot: an unresolved
                # number is not a name a reviewer could act on, and inventing
                # a row called "712324" would be noise, not coverage.
                if s.isdigit():
                    s = by_id.get(s)
                    if not s:
                        continue
                names.add(s)
        out[k["id"]] = names
    return out


def pack_names(cls, exiles, meta):
    """{ability name: one display that references it}, from pack_refs."""
    out = {}
    for display, names in pack_refs(cls, exiles, meta).items():
        for n in names:
            out.setdefault(n, display)
    return out


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
    # Third source: whatever the built pack points at. See pack_names().
    drawn = pack_names(cls, exiles, meta)
    names = set(book) | set(cds) | set(existing) | set(drawn)

    rows, added = [], []
    for name in sorted(names):
        if name in existing:
            rows.append(existing[name])           # hand edits win, always
            continue
        cd = cds.get(name, {})
        sid = cd.get("id") or (exiles.get(name, {}).get("ids") or [""])[0]
        m = meta.get(str(sid), {})
        meta_str = (book.get(name) or {}).get("meta", "")

        # Specs: the cooldown audit first, then the skillbook, then `all`.
        #
        # The audit only has a row for an ability with a cooldown, so every
        # filler, spender and direct heal fell through to `all` and rendered on
        # every spec. Accelerate, Decelerate, Chronostasis, Moment's Reprieve
        # and Rehatch each did exactly that: five single-spec abilities drawn
        # on all three.
        #
        # The skillbook fallback is sound for the reason set out in
        # sidekick_skills.py -- coaKits states each spec's abilities outright,
        # which is a different thing from the mention-count inference this
        # module refuses to make. It still loses to the audit, to a hand edit
        # and to an in-game tooltip.
        specs = ",".join(cd.get("specs") or []) \
            or ",".join((book.get(name) or {}).get("specs") or []) \
            or "all"
        rank = m.get("rank") or ""
        if not rank:
            found = RANK_IN_META.search(meta_str)
            rank = found.group(1) if found else ""
        # A passive is not a button. Seeding it `utility` puts 56 non-buttons
        # in the row a reviewer is meant to scrutinise; `ignore` keeps the
        # decision visible without drowning the real work.
        role = "ignore" if "Passive" in meta_str else "utility"
        note = seed_note(meta_str, sidekick_hits(cls, name))
        if name in drawn:
            # Worth saying loudly on the row itself: this one is ALREADY on
            # screen. It is not a candidate to consider, it is a display
            # whose role was never written down.
            note += f"; RENDERED BY THE PACK as `{drawn[name]}`"

        row = [name, str(sid), specs, role, rank, note]
        rows.append(row)
        added.append(row)

    cand = candidates(exiles, meta, set(names))

    # What each spec is FOR. A healer's rows are a different set from a damage
    # spec's, so this belongs in front of whoever is assigning roles rather
    # than in a file they might not open. Unknown is printed as unknown --
    # `spec_role` returns None rather than guessing damage, because guessing
    # damage is how a healer's target band goes missing silently.
    _roles = ", ".join(f"**{cls.spec_label(s)}** {cls.spec_role(s) or '?'}"
                       for s in cls.specs)
    _heal = ("\nThis class heals. A healing spec earns the target band — your "
             "HoTs and absorbs\non your CURRENT target, glowing when one needs "
             "a refresh — and its main row is a\nhealing rotation. Raid frames "
             "stay out; VuhDo/Grid own that job on 3.3.5a.\n"
             if cls.healers else "")

    body = "".join("| " + " | ".join(r) + " |\n" for r in rows)
    text = (f"# {cls.name} — ability inventory\n\n"
            f"Specs: {_roles}. (`resources/spec-roles.md`, observed in game.)\n"
            f"{_heal}\n"
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
