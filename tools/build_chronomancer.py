"""Build the `Chronomancer [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Second class through the process in `notes/class-pack-process.md`, and the one
that tests whether that process is real. Layout follows
`notes/layout-standard.md` -- flush icon bands at fixed offsets, DESATURATION
carrying availability rather than glow on everything.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your HoTs / your DoTs ]          <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 9
              [ defensive + utility       ]           <- band 7, wraps at 9
              [ long-term buffs           ]           <- band 8, active-only

Three things here have no Runemaster analogue:

  * The TIME spec is the first HEALING spec in any pack. Healing surfaces are
    deliberately scoped OUT -- raid frames belong to VuhDo/Grid on 3.3.5a. What
    the pack does carry is the target band: your own HoTs/absorbs on your
    current target, glowing when one needs a refresh.

  * The four AEONS are mutually-exclusive infinite self-buffs that reshape both
    Epoch and Ripple. `Eternity Warper` (806301) gives Ripple a different effect
    per Aeon, so Ripple is emitted as FIVE displays -- one per Aeon plus a
    no-Aeon default -- and the dynamic group lays out whichever one is showing.
    That reuses the same loaded-and-showing mechanism that lets one band serve
    three specs, instead of betting the main rotation icon on icon-swap
    conditions.

  * ARTIFICER spends combo points alongside mana, so its resource envelope
    holds two bands where Engravement and Riftblade held one.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import json
import os
import re

import wabuild as B
from classes import get as _get_class, data, dest  # noqa: F401
from wacodec import LuaTable

SP = os.path.dirname(os.path.abspath(__file__))

# Identity comes from classes.py, which parses resources/class-tokens.md and
# resources/ascension-coa-class-ids.md rather than copying them. Retyping the
# token here is the documented way to get it wrong: it is NOT derivable from
# the class name (Runemaster is SPIRITMAGE, Templar is MONK) and Chronomancer
# only happens to match its own name.
CLS = _get_class("chronomancer")

# Release tag. Feeds the uid salt ONLY -- set_salt() below, nothing else.
# WeakAuras dedupes imports on uid, so a rebuilt pack MUST carry a different
# salt or the client treats it as already-installed and silently keeps the old
# copy. Bump this (1.1, 1.2, ...) on any future release.
#
# It does NOT reach the group name: every release imports as the same
# "Chronomancer [CoA]", so the loaded version is NOT visible in the WeakAuras
# list and a delivered file carries no readable version string. Identify one by
# recomputing uids -- see notes/class-pack-process.md.
VERSION = "1.0"

# WA_SPEC=artificer|infinite|time emits a single-spec pack: Core plus that one
# spec, for players who only ever play the one.
SPEC_ONLY = os.environ.get("WA_SPEC", "").strip().lower() or None
SPEC_TITLE = CLS.spec_label(SPEC_ONLY) if SPEC_ONLY in CLS.specs else None
GLOW = os.environ.get("WA_GLOW") == "1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {}
OVERRIDE = {
    # ONLY deliberate choices belong here, because an entry here overrides the
    # CLIENT's own art for the spell (see the iconSource note below).
    #
    # Two pairs share art upstream and can appear side by side, which is what
    # the duplicate-art check is for. Both replacements are borrowed from
    # Chronomancer spells that carry real art and never appear in a cooldown
    # row, so the fix cannot introduce a fresh clash.
    "Slow Time": "achievement_challengemode_auchindoun_hourglass",
    "Incarnation of Order": "spell_arcane_portal_valeofblossoms",
}

# Art that db.ascension.gg does not have. It serves a questionmark on these
# spells' own pages, so the SCRAPE has nothing -- but the CLIENT does, and its
# texture is the right one. Hasten is the proof: db.ascension has no art, the
# game draws a boot, and a placeholder picked from the class's icon pool drew a
# clock instead. So these are deliberately NOT given art here; they are left to
# resolve from the trigger. Listed only so a future run does not "fix" them.
NO_UPSTREAM_ART = {
    "Hasten", "Unearth", "Fray Magic", "Reflection", "Chronobeam", "Chronurgy",
    "Wand of Time", "Nozdormu's Wisdom", "Greater Nozdormu's Wisdom",
    "Chromie's Wisdom", "Greater Chromie's Wisdom",
}

# ---- layout ---------------------------------------------------------------
# Every band is centred at x=0 and stacked vertically. Scattering groups to
# different x offsets is what made the old layout read as disjointed next to a
# Luxthos-style pack. Dynamic groups only lay out ACTIVE children, so the
# active-only bands self-centre and stay tidy however many are showing.
Y_ALERT = -18       # missing-buff reminders, high and central
Y_PROCS = -60       # spec procs, short windows, active-only
# The target band sits in the one gap the ladder above the main row leaves.
# Reminders (-18, 38px) span +1..-37 and "on me" (-84, 36px) spans -66..-102,
# so a 28px band centred at -51 spans -37..-65 and fits exactly between them.
Y_TARGET = -51      # your HoTs / your DoTs on the CURRENT target
Y_BUFFS = -84       # single row: procs, running CDs, buffs, debuffs
Y_MAIN = -132       # main damage row

# ---- resource envelope -----------------------------------------------------
# A FIXED-HEIGHT block under the main row, spanning roughly -156..-186. Every
# spec fills it however its resources require and the block is the same height
# either way, so everything below it sits at ONE anchor for all three specs.
#
# This replaces a per-spec ladder (`Y_SEG - CD_ROW_STEP if glyphic`). That
# worked while each spec owned its own band groups, but the bands are shared
# now and a dynamic group has a single yOffset -- so Glyphic's taller stack was
# pushing an empty 30px slot onto Engravement and Riftblade, which have no
# glyph bar to put in it.
#
# The tradeoff, deliberately taken: Glyphic's mana bar is thinner than the
# other two specs', because it shares the envelope with the glyph bar.
Y_BAR = -164        # Glyphic mana bar (shares the envelope with the glyphs)
BAR_H_STACKED = 14  #   its height
Y_SEG = -180        # Glyphic glyph bar, directly beneath its mana bar
Y_BAR_SOLO = -170   # Engravement / Riftblade: mana is the whole envelope
BAR_H_SOLO = 24     #   so it gets the full height
# Icons per cooldown row before it wraps, wired to `gridWidth` on a
# grow="GRID" band.
#
# THIS IS PER-CLASS, derived from the NARROWEST main row in the pack, because
# every resource bar is width-locked to its own spec's main row and a cooldown
# row that overruns the narrowest one looks broken on that spec even if it fits
# the others. A row of w icons is `w*SZ_CD + (w-1)*GAP` = 28w - 2.
#
#   Chronomancer's narrowest main row is now five icons -> row_w(5) = 228px
#   (Time was four until Reverse Wound joined its row), which allows 9 the way
#   Runemaster does. 7 is kept: the constraint is that a cooldown row must not
#   OVERRUN the narrowest bar, and a narrower row is never the thing that looks
#   broken. Widening to 9 would reflow every band depth for no cue gained.
#   28w - 2 <= 1.2 * 182  ->  w <= 7.8  ->  7   (194px = 1.07x)
#
# Runemaster's narrowest is five icons -> 228px, which is why its builder uses
# 9. Do not copy a value between classes; recompute it, and let
# tools/rowwidths.py confirm against the built packs.
CD_PER_ROW = 7
CD_ROW_STEP = 30
SZ_CD = 26
SZ_ALERT = 38
SZ_BUFF = 36         # buff row -- larger so the timer is legible
Y_CDS = -202        # first cooldown row, one anchor for every spec
LONG_GAP = 16       # extra clearance between the last cooldown row and long-term
# From classes.py, NOT retyped. A stale spec list here is silent: _ROWS
# below iterates it, so wrong keys yield zero rows and the band ladder
# collapses every band onto the one above it.
SPECS = tuple(CLS.specs)
Y_DOTS = -311       # applied DoTs / debuffs, below the cooldown block

SZ_MAIN = 44
SZ_SMALL = 28
SZ_STATE = 28
GAP = 2             # tight, but enough that overlaid text does not collide
BAR_W = 270
BAR_H = BAR_H_SOLO   # default resource bar height
SEG_H = 10           # glyph segment height (thin: it shares the envelope)
GLYPH_GAP = 2        # gap between glyph segments
SOLID = "Interface\\ChatFrame\\ChatFrameBackground"
EDGE = "Square Full White"
DARK = (0.04, 0.04, 0.05, 1)


# Authoritative name -> spellId map scraped from db.exil.es (class 32).
# Cross-checked: Zenith resolves to 712325, the same id used by a working
# community aura, and Smolder/Fracture match db.ascension.gg. Triggers key off
# these ids rather than names, because several names taken from Sidekick either
# do not exist or collide onto the same spell -- which is what produced the
# duplicate icons.
EXILES = json.load(open(data(CLS.exiles)))
# Every Runemaster ability that actually has a cooldown, audited from
# db.exil.es spell pages (see audit_cds.py). Hand-maintained lists kept missing
# things like Convergence and Primordial Fury.
COOLDOWNS = json.load(open(data(CLS.cooldowns)))

# ---- icon art --------------------------------------------------------------
# Runemaster resolved art through icons.json plus a hand-built ICON_GAP. Both
# are name-keyed to ITS spells, so neither transfers. Chronomancer has two
# scrapes that carry art for itself:
#
#   coa-chronomancer-skills.json  181 entries, from db.ascension.gg's listing
#   exiles-chronomancer.json      120 entries, from db.exil.es's tree payload
#
# Skills covers more names; exiles fills its gaps. 14 names are questionmarks
# on db.ascension AND on their own spell pages, so those are genuinely missing
# upstream rather than a scrape miss -- they land in FALLBACK below.
_QM = "inv_misc_questionmark"
ICONS = {n: v["icon"] for n, v in EXILES.items() if v.get("icon")}
for _r in json.load(open(data(CLS.skills))):
    if _r.get("icon") and _r["icon"] != _QM:
        ICONS[_r["name"]] = _r["icon"]
    else:
        ICONS.setdefault(_r["name"], _QM)

# Per-spell metadata from db.exil.es's JSON API (tools/spellmeta.py). Only
# used for one question, but a load-bearing one: is this id safe to hand to
# `load.use_spellknown`?
SPELL_META = json.load(open(data(f"spell-meta-{CLS.slug}.json")))


def gateable(sid):
    """False if IsSpellKnown() cannot be trusted with this id.

    `load.use_spellknown` holds ONE id and IsSpellKnown is EXACT, so a wrong id
    hides the display with no error anywhere -- not in the build output, not in
    game. Five Chronomancer abilities shipped invisible this way: Gravity Bomb,
    Unearth, Time Out! and Fortify Timeline are ranked spells (IsSpellKnown is
    true only for the rank the character actually has, and db.exil.es links
    whichever rank it likes), and Temporal Focus's listed id was the
    diminishing-returns entry rather than the ability.

    Conservative on purpose. A false negative costs one duplicated display; a
    false positive costs an ability nobody can see and no test can catch.
    """
    from spellmeta import is_castable
    return is_castable(SPELL_META.get(str(sid)))


# id -> art, so a corrected id corrects the art with it. Scraped per id by
# tools/fetch_spell_icons.py; 780 ids resolved, which covers far more than the
# class's own 476 because each db.ascension page also carries art for every
# spell it cross-references.
ID_META = {i: {"icon": a}
           for i, a in json.load(open(data(f"icon-meta-{CLS.slug}.json"))).items()}
for _n, _v in EXILES.items():          # tree payload fills any gaps
    if _v.get("icon"):
        for _i in _v["ids"]:
            ID_META.setdefault(str(_i), {"icon": _v["icon"]})


def _cd_secs(text):
    m = re.match(r"([\d.]+)\s*(sec|min|hour)", text)
    return (float(m.group(1)) * {"sec": 1, "min": 60, "hour": 3600}[m.group(2)]
            if m else 1e9)


# Already shown in the main row / state band / proc row -- never repeat here.
# ---- the ability inventory ------------------------------------------------
# resources/abilities-<class>.md is the source of truth for what renders and
# where. It replaced six hand-typed Python lists, which at 21 classes would
# have been 126 of them with no way to see what a list was MISSING -- which is
# how Arc Collision never entered the pack at all and four survival cooldowns
# ended up in the damage row.
#
# ROLE IS PER SPEC. That is the whole reason the column parses rather than
# being a bare word: for a HEALER the primary-action row is what you press at
# other people, so Infinite Shield, Timeguard, Time Out!, Fortify Timeline and
# Continuum Restoration are Time's "offensive" row while staying defensive for
# the two damage specs. A single global role cannot express that, and the
# earlier one produced a Time layout whose damage row was nearly empty while
# defence and utility overflowed.
#
#     Role := <default> [; <spec>:<role>]*
#     "defensive; time:offensive"
#
# THE ID COLUMN PARSES THE SAME WAY, for the rarer case where one NAME is two
# different spells. Buy Time is the example: Artificer and Infinite cast 520188
# (8yd banish, 180s, on the global), Time casts 801280 (10yd stasis, 120s, off
# it), and 520185 -- what db.exil.es returns for the name -- is only the aura
# and castable by nobody. A name-keyed id cannot express that, and picking
# either one silently breaks the other spec's icon: the cooldown trigger tracks
# a spell that character cannot cast, and the leaf's spellknown gate (derived
# from the same id, see _leaf_spell) then hides it outright.
#
#     ID := <default> [; <spec>:<id>]*
#     "520188; time:801280"
def _abilities():
    """name -> {"id":, "ids": {spec: id}, "specs": set|None,
    "roles": {spec: role}, "default":}"""
    path = data(f"abilities-{CLS.slug}.md")
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        if len(c) < 6 or c[0] == "Ability":
            continue
        name, sid, specs, role = c[0], c[1], c[2], c[3]
        parts = [p.strip() for p in role.split(";") if p.strip()]
        default = parts[0] if parts else "utility"
        roles = {}
        for extra in parts[1:]:
            if ":" in extra:
                sp, r = extra.split(":", 1)
                roles[sp.strip()] = r.strip()
        id_parts = [p.strip() for p in sid.split(";") if p.strip()]
        sid = id_parts[0] if id_parts else ""
        ids = {}
        for extra in id_parts[1:]:
            if ":" in extra:
                sp, i = extra.split(":", 1)
                if i.strip().isdigit():
                    ids[sp.strip()] = int(i.strip())
        out[name] = {
            "id": int(sid) if sid.isdigit() else None,
            "ids": ids,
            "specs": None if specs in ("all", "") else set(
                x.strip() for x in specs.split(",") if x.strip()),
            "default": default,
            "roles": roles,
            "seeded": c[5].startswith("seed: "),
        }

    # A row mkabilities.py wrote and nobody has read is not a decision, and
    # both ways of treating it as one are wrong: build it and the seeder's
    # `utility` guess floods the utility band with talents and passives; skip
    # it and we are back to abilities silently absent from the pack, which is
    # the bug the reseed exists to kill. So: refuse, and say which rows.
    seeded = sorted(n for n, a in out.items() if a["seeded"])
    if seeded:
        raise SystemExit(
            f"{len(seeded)} abilities in resources/abilities-{CLS.slug}.md "
            f"still carry the `seed:` marker and have no reviewed role.\n"
            f"  Assign a Role and delete the `seed:` prefix from Notes.\n"
            f"  First few: {', '.join(seeded[:8])}\n"
            f"  Progress:  python3 tools/mkabilities.py {CLS.slug} --check")
    return out


ABILITIES = _abilities()


def role_of(name, spec):
    """Where `name` renders for `spec`. Per-spec override wins."""
    a = ABILITIES.get(name)
    if not a:
        return "utility"
    return a["roles"].get(spec, a["default"])


def _named(role, spec):
    """Ability names in `role` for `spec`, inventory order."""
    return [n for n, a in ABILITIES.items()
            if role_of(n, spec) == role
            and (a["specs"] is None or spec in a["specs"])]


# Shown in another band, or not a player button at all -- never in a cooldown
# row. `ignore` covers the pet spellbook (five "Chronobuff" abilities whose
# tooltips read "Shroud your MASTER"), passives and deprecated entries.
ELSEWHERE = {n for n, a in ABILITIES.items()
             if a["default"] in ("main", "resource", "longterm", "ignore",
                                 "buff", "target")}

# Ground truth read off in-game tooltips. A screenshotted tooltip is the truth:
# it outranks db.exil.es, db.ascension.gg, coabuildhub and Sidekick, and it
# feeds BOTH the spell id and the icon. db.exil.es's class page links the PROC
# for some abilities rather than the castable spell, and has plainly wrong ids
# for two engravings, so this registry is not an edge case -- it is the top of
# the precedence chain. Extend it whenever a tooltip is captured.
_VERIFIED = {k: v for k, v in
             json.load(open(data("in-game-verified.json"))).items()
             if not k.startswith("_")}
IN_GAME = {k: v["id"] for k, v in _VERIFIED.items()}
# Not tooltip-verified, but db.exil.es points at a spell db.ascension.gg does
# not mark as an ability while ascension.gg has a clear Ability/Talent entry.
# Replace with a tooltip id when one is captured.
# db.exil.es maps "Aeon of Resilience" to 92119, which is the LEVEL 10 PASSIVE
# whose entire tooltip is "Teaches you Aeon of Resilience" -- it has no cooldown
# row, the documented smell for a wrong id, and it is flagged Passive. The
# castable stance is 806291.
#
# Two independent routes agree: 806291 is the hole in the otherwise contiguous
# 806290/806292/806293 Aeon block, and a working community pack uses it
# alongside the other three. The cooldown audit corroborates by omission -- it
# found the other three Aeons at 10 sec and could not find Resilience at all.
CROSSCHECK = {
    "Aeon of Resilience": 806291,
    # db.exil.es links a COMPONENT of the ability rather than the ability, and
    # the component is never castable and never known -- so the icon draws the
    # wrong art AND its gate silently fails. tools/spellmeta.py flags these by
    # rank_text; all three were caught in game first.
    "Temporal Focus": 806165,     # 528056 is rank "DR", the mitigation aura
    "Singularity Core": 804438,   # 804437 is rank "Damage", the damage effect
    "Infinite Clone": 804492,     # 704154 is rank "Player Aura"
}
ID_OVERRIDE = {**CROSSCHECK, **IN_GAME}
# A talent can REPLACE an ability with a different spell id rather than just
# modifying it -- Runelord swaps Zenith 712325 for 712389. An exact-id trigger
# on the base then silently stops matching, and the icon vanishes once you
# spec into the talent. Every known id gets its own trigger, any-of.
VARIANTS = {k: [v["id"]] + list(v.get("variants", []))
            for k, v in _VERIFIED.items()}

# Which spec pages mention an ability. The cooldown audit carries this for
# anything with a cooldown; curated names without one (Fists of Power, ...)
# still need it, or the global curated lists leak across specs.
# Read from resources/, and drive the spec list off classes.py. Runemaster's
# builder reads these from ~/second-brain/, which means that build is not
# reproducible from a clean clone -- do not copy that here.
SPEC_TEXT = {sp: open(data(CLS.sidekick(sp))).read() for sp in CLS.specs}


def in_spec(name, spec_key):
    v = COOLDOWNS.get(name)
    if v:
        return spec_key in v["specs"] or not v["specs"]
    hits = [sp for sp, t in SPEC_TEXT.items() if name in t]
    return spec_key in hits or not hits


def spec_cooldowns(spec, lo, hi):
    """Ability names for one spec with a cooldown in [lo, hi), shortest first.
    An empty `specs` list means the ability is shared across all three."""
    got = [(n, _cd_secs(v["cd"])) for n, v in COOLDOWNS.items()
           if (spec in v["specs"] or not v["specs"])
           and lo <= _cd_secs(v["cd"]) < hi]
    return [n for n, _ in sorted(got, key=lambda x: x[1])]
UNRESOLVED = []


def _id_for(name):
    """Best-known id: in-game tooltip first, then db.exil.es."""
    if name in ID_OVERRIDE:
        return ID_OVERRIDE[name]
    e = EXILES.get(name)
    return e["ids"][0] if e else None


def sid(name):
    """Spell id for a name. Records misses so the build can report them."""
    if name in ID_OVERRIDE:
        return ID_OVERRIDE[name]
    e = EXILES.get(name)
    if not e:
        if name not in UNRESOLVED:
            UNRESOLVED.append(name)
        return name
    return e["ids"][0]


# One NAME, two SPELLS -- see the ID column note above _abilities(). Kept as a
# separate map rather than folded into ID_OVERRIDE because every other id in
# this file is a single answer to "what is this ability", and this one is only
# answerable once you know which spec is asking.
SPEC_IDS = {n: a["ids"] for n, a in ABILITIES.items() if a["ids"]}


def sid_for(name, spec):
    """Spell id for a name AS THIS SPEC CASTS IT.

    Falls back to sid() for the ~200 abilities that are one spell everywhere,
    and for a spec with no override on an ability that has them (Artificer and
    Infinite both take the default 520188 for Buy Time).
    """
    if spec and name in SPEC_IDS and spec in SPEC_IDS[name]:
        return SPEC_IDS[name][spec]
    if name in SPEC_IDS:
        # the row's own default id, NOT db.exil.es -- for Buy Time the db name
        # resolves to 520185, the aura, which no spec can cast
        own = ABILITIES[name]["id"]
        if own:
            return own
    return sid(name)


# Real icon for each spell id, scraped per-spell from db.exil.es. Previously
# icons came from a hand-built name lookup while triggers used verified ids, so
# the art and the tooltip could disagree -- e.g. slot 1 drew Primordial Blast's
# orb while the trigger was Runeblade.

# Ids whose db.exil.es page does not expose an icon; taken from the other DBs.
ICON_GAP = {}


def ic(name):
    # A hand-written OVERRIDE outranks everything. It is the only place a human
    # has stated intent -- usually to break a genuine art collision between two
    # abilities that share a texture upstream and CAN sit in a row together --
    # so a scrape must never win over it. (It used to: ID_META was consulted
    # first and OVERRIDE only reached when the id had no art, which quietly
    # made every override a no-op the moment the icon scrape improved.)
    if name in OVERRIDE:
        return "Interface\\Icons\\" + OVERRIDE[name]
    # Otherwise resolve art through the SAME id the trigger uses, so a
    # corrected id corrects the icon too -- otherwise the tooltip id lands but
    # the art still comes from the stale scraped id.
    _i = _id_for(name)
    if _i is not None:
        i = str(_i)
        path = (ID_META.get(i) or {}).get("icon") or ICON_GAP.get(i)
        if path:
            return "Interface\\Icons\\" + path
    path = OVERRIDE.get(name)
    if not path:
        path = ICONS.get(name)
        if not path or path == "inv_misc_questionmark":
            path = FALLBACK.get(name) or path or "inv_misc_questionmark"
    return "Interface\\Icons\\" + path


def _triggers_of(display):
    """Pull the trigger list back out of a built display.

    Triggers are stored as a LuaTable of {trigger, untrigger} pairs under
    numeric keys, so re-wrapping one means unwrapping it first. Used to append
    a gate to an icon that cd_icon has already finished building.
    """
    tg = display.get("triggers") or {}
    return [tg[k]["trigger"] for k in sorted(k for k in tg if isinstance(k, int))]


def thin(size=2):
    return B.sub_border(color=DARK, size=size, offset=1, edge=EDGE)


children = []
B.set_salt(f"chronomancer-{SPEC_ONLY or 'all'}-{VERSION}")
ROOT = (f"Chronomancer {SPEC_TITLE} [CoA]" if SPEC_TITLE
        else "Chronomancer [CoA]")


def add(region):
    children.append(region)
    return region["id"]


# NO SPEC AURA GATE. Runemaster carried a `SPEC_AURA` table mapping each spec
# to a `CoA Aura - <Class> - <Spec>` id, and it is a trap twice over:
#
#   1. Those ids are DATABASE ENTRIES, not auras the player carries. Gating on
#      them hid 119 of 141 displays -- retro bug #7.
#   2. Even if they were real, a group's triggers are INERT. WeakAuras skips
#      load-scanning for anything with `controlledChildren`, so a gate here
#      does nothing at all -- retro bug #2, six iterations.
#
# Gating is `load.use_spellknown` on every LEAF, applied by apply_leaf_gates().
# The spec group is a plain container.


def spec_group(id_, kids):
    """Plain container. Deliberately carries NO triggers -- see above."""
    return B.group(id_, ROOT, kids, x=0, y=0)


# Abilities that hold charges rather than a plain cooldown. These get a count
# drawn in the corner; everything else would just show a meaningless "1".
# Zenith only has charges once Runelord is talented (it becomes 712389), but
# the count is harmless on the base version.
# Fabric of Time gains a second charge from Timeblender; the count is
# harmless on the base version.
CHARGES = {"Fabric of Time": 2}


# Artificer's Continuum spells. Mutually exclusive -- "you can only have 1
# Continuum spell active at a time" -- and each empowers your wand for a window
# that grows as you spend Echo Fragments.
CONTINUUM = ["Singularity Core", "Flux Emitter", "Paradox Cannon",
             "Aether Compression"]


def _bottom_rows(spec_key):
    """(offense, utility) ability names for one spec, in press order.

    Both come from the inventory, so a recategorisation is a one-line edit to
    a markdown table rather than a hunt through the builder.

    Split out of emit_bottom_block so the ladder can be planned across ALL
    specs before any band is emitted: a shared band has one yOffset, so the
    depth it reserves has to cover the spec that wraps deepest.
    """
    # Only ONE Continuum spell can be active at a time and the whole Artificer
    # loop is built around keeping it up, so they lead the row rather than
    # sorting in with everything else.
    offense = _named("offensive", spec_key)
    _order = {n: i for i, n in enumerate(offense)}
    # Continuum first, in CONTINUUM order (press priority), then the rest in
    # inventory order.
    offense.sort(key=lambda n: (0, CONTINUUM.index(n)) if n in CONTINUUM
                 else (1, _order[n]))
    defensive = _named("defensive", spec_key)
    utility = defensive + sorted(_named("utility", spec_key))

    return offense, utility


# How deep the cooldown stack goes on the spec that stacks deepest.
#
# Offense and Utility are per-spec bands now, so each spec's ladder closes up
# behind its own rows. Long-term is NOT -- it lives in Core and has one
# yOffset for the whole pack -- so it has to clear the worst case.
#
# Take the max of each spec's OWN (offense + utility) total, not the sum of the
# per-band maxima. Those differ: Artificer wraps 3+2 and Time 2+3, so the
# per-band maxima sum to 6 rows while no spec ever uses more than 5. Summing
# the maxima put Long-term a dead row lower than anything could reach.
# In a per-spec build only ONE spec is in the pack, so Long-term can sit right
# under that spec's own stack. The all-specs pack still has to clear the
# deepest, because Long-term is a Core band with a single yOffset -- that is
# the one gap the un-merge could not remove.
_DEEPEST = max(
    sum(max(1, -(-len(_bottom_rows(_s)[_i]) // CD_PER_ROW)) for _i in (0, 1))
    for _s in ([SPEC_ONLY] if SPEC_ONLY else SPECS))

Y_LONG = Y_CDS - _DEEPEST * CD_ROW_STEP - LONG_GAP

# Abilities that do NOT trigger the global cooldown.
#
# `use_showgcd` is per-trigger and WeakAuras applies it BLINDLY: for any spell
# not already on its own cooldown it substitutes the tracked global
# (`GenericTrigger.lua:2795`), with no per-spell knowledge of whether that
# spell obeys one -- the addon polls a single reference spell for the global
# and has nothing else to go on. Set the flag on an off-GCD ability and its
# icon sweeps every time you press something ELSE: a cooldown that is not
# real, on an ability you could have used the whole time. Shipped in final14.
#
# Scraped, not curated. db.exil.es renders a `GCD` row on the spell page when
# the ability is on the global and omits the row entirely when it is not;
# `audit_cds.py` turns that absence into `gcd: false`. 26 of Runemaster's 59
# cooldown abilities are off-GCD, which is far too many to have kept by hand
# and would not have scaled to 21 classes at all.
#
# Ground truth behind the rendered row is Spell.dbc field 206
# StartRecoveryCategory (133 = on the global, 0 = not) / field 207
# StartRecoveryTime. See `notes/off-gcd-detection.md`.
OFF_GCD = {n for n, v in COOLDOWNS.items() if v.get("gcd") is False}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text.
PROC_GLOW = {
    # Each Continuum glows while its OWN 5 sec buff is running. The cooldown
    # swipe answers "when can I swap"; it cannot answer "which one is empowering
    # my wand right now", which is the thing you actually read mid-fight.
    "Singularity Core": ["Singularity Core"],
    "Flux Emitter": ["Flux Emitter"],
    "Paradox Cannon": ["Paradox Cannon"],
    "Aether Compression": ["Aether Compression"],
    # ability -> the procs that say "press this now"
    "Artificer's Wand": ["Clocked In"],     # next wand instant, banks a fragment
    "Chromatic Shard": ["Chaos Fusion"],    # castable while moving
    "Melt Reality": ["Chaotic Time"],       # amped and replicated
    "Epoch": ["Sands of Time"],             # -20% cast time per stack
    "Reverse Wound": ["Endless Sands"],     # -20% cast time per stack, to 5
}

# Abilities whose PROC_GLOW buff also STACKS, drawn as a number on the icon
# rather than as a bar of its own. Endless Sands is a Reverse Wound modifier
# (-20% cast time per stack, up to 5) built by Epoch and Correct the Mistake,
# so it belongs on the button it changes -- a second segmented bar under the
# Sands of Time one would put two five-stack meters side by side and make the
# player read which is which mid-cast.
PROC_STACKS = {"Reverse Wound"}


# Cooldown urgency. `expirationTime` with op "<" takes SECONDS REMAINING and
# is the variable the working community packs use for this (33 uses in the
# Templar pack), so the tiers are built on verified ground.
URGENCY = [(20, "timer"), (10, "glow"), (5, "pulse")]


def cd_icon(display_id, parent, name, size, charges=False, urgency=False,
            spec=None):
    """A cooldown icon.

    `spec` is the spec key this copy is being built for, and only matters for
    the handful of abilities in SPEC_IDS whose name maps to a different spell
    per spec. Passing it is NOT optional for those -- see the guard below.

    urgency=True (the Offense / Defense / Utility rows) adds graduated cues as
    the cooldown comes back:
         20s left -> the timer appears
         10s left -> it glows
          5s left -> the glow turns urgent and the icon tints

    urgency=False (the main damage row) keeps the plain always-on cooldown
    text: those abilities sit on 6-8s cooldowns, so a 20s reveal would mean
    the number is simply always there, and the escalation would be noise.
    Both kinds still glow when a proc says to press them.

    Both kinds also sweep for the global cooldown (`use_showgcd` on the
    trigger), so a ready ability still reads as "not yet" for the ~1.5s after
    a cast -- the cue for holding a press rather than clipping it. Abilities
    listed in OFF_GCD opt out: they do not obey the global, so showing it
    would sweep them every time you pressed something else.
    """
    # Loud, not silent. A per-spec ability built without a spec would pick the
    # default id and render an icon that tracks the wrong spell on two thirds
    # of the class -- exactly the failure this map exists to prevent, and one
    # that is invisible in the built pack.
    if spec is None and name in SPEC_IDS:
        raise SystemExit(
            f"cd_icon({display_id!r}): {name!r} has per-spec ids "
            f"({SPEC_IDS[name]}) -- pass spec= so the right one is used.")

    subs = [B.sub_background()]
    if urgency:
        # hidden until 20s remain; native cooldown text is off so there is
        # only ever one number on the icon
        subs.append(B.sub_text("%p", size=max(12, int(size * 0.34)),
                               anchor="INNER_BOTTOM", visible=False))
        timer_index = len(subs)
    subs.append(thin())
    subs.append(B.sub_glow(False, "buttonOverlay", (1.0, 0.85, 0.35, 1.0)))
    glow_index = len(subs)
    if charges:
        subs.append(B.sub_text("%s", size=max(11, int(size * 0.34)),
                               anchor="INNER_TOPRIGHT", color=(1, 1, 1, 1)))

    # RANKED spells must match by NAME, not by exact id. `use_exact_spellName`
    # pins the trigger to one rank, so a level-14 rank-2 id tracks nothing on a
    # character who has rank 4 -- the icon simply never appears. Same root
    # cause as the gate problem above, on the other surface: Gravity Bomb,
    # Unearth, Time Out! and Fortify Timeline all shipped invisible.
    #
    # Name matching is rank-agnostic, which is exactly what a cooldown row
    # wants: you care that Gravity Bomb is on cooldown, not which rank of it.
    _sid = sid_for(name, spec)
    _exact = gateable(_sid)
    # OFF_GCD is name-keyed off the cooldown audit, which is also name-keyed, so
    # a split ability gets ONE answer for both halves. Buy Time is on the global
    # for Artificer/Infinite and off it for Time; the audit has no row for
    # either, so both sweep the global. Wrong only for Time, and only as a 1.5s
    # sweep on an ability with a 120s cooldown -- accept until a spec-keyed
    # audit exists, rather than hand-maintain a second exception list here.
    triggers = [B.spell_cd_trigger(_sid, show_on="showAlways", exact=_exact,
                                   show_gcd=name not in OFF_GCD)]
    conds = []
    if urgency:
        # Every urgency tier is ANDed with "this is a real cooldown, not the
        # GCD". The trigger reports the global cooldown (use_showgcd), so a
        # bare `expirationTime < 5` fires the urgent glow on every global, on
        # every icon in the row -- which is exactly what shipped in final12.
        #
        # The guard is `onCooldown`, which is EXACT. Its conditionTest is
        # `not state.gcdCooldown and state.expirationTime > GetTime()`
        # (`Prototypes.lua:5700`), i.e. the prototype itself excludes the
        # global, using the same `gcdCooldown` flag GetSpellCooldown sets when
        # the reported cooldown came from the global rather than the spell.
        #
        # `gcdCooldown` cannot be used directly: it is declared `store = true`
        # with NO `conditionType` / `conditionTest`, so it is not a condition
        # variable and WeakAuras drops the sub-check, collapsing the AND back
        # to the bare expirationTime test. Note this is NOT because it is
        # `hidden` -- both `onCooldown` and `spellUsable` are `hidden = true`
        # and both work. `conditionType` is what makes a variable usable.
        #
        # This replaces a `duration > 3` floor (final13/14), which cost the
        # escalation cues on every ability whose own cooldown was under 3s --
        # Unleash Essences (2.5s) and Trap Runes (3.0s). The floor was also
        # built on the wrong number: the global here is 1.0s base, not 1.5s,
        # and ranges from 0.5s (Warpdagger) to 1.5s (Elder Magi Rune).
        def real_cd(seconds):
            return B.check_and(
                B.T({"trigger": 1, "variable": "expirationTime",
                     "op": "<", "value": seconds}),
                B.T({"trigger": 1, "variable": "onCooldown", "value": 1}))

        conds += [
            B.cond(real_cd("20"),
                   [B.change(f"sub.{timer_index}.text_visible", True)]),
            B.cond(real_cd("10"),
                   [B.change(f"sub.{glow_index}.glow", True)]),
            B.cond(real_cd("5"),
                   [B.change(f"sub.{glow_index}.glowColor",
                             B.rgba(1.0, 0.45, 0.15, 1.0)),
                    B.change("color", B.rgba(1.0, 0.85, 0.7, 1.0))]),
        ]
    # Readiness, which is a different question from cooldown. `spellUsable`
    # is false when you cannot cast right now for a reason the cooldown swipe
    # never shows -- out of mana, missing the resource, wrong form. Without
    # it an off-cooldown icon looks pressable when it is not, which is the
    # single most misleading state a rotation pack can be in.
    #
    # Verified exposed on this fork: the Templar community pack drives
    # desaturate off `spellUsable` 9 times (and off `onCooldown` 15 more).
    # It is independent of the cooldown, so it does NOT need the GCD guard --
    # a global does not make a spell unusable, it makes it un-castable, and
    # the sweep already says that.
    conds.append(B.cond(
        B.T({"trigger": 1, "variable": "spellUsable", "value": 0}),
        [B.change("desaturate", True)]))

    procs = PROC_GLOW.get(name)
    if procs:
        triggers.append(B.aura_trigger(
            [str(sid(pn)) for pn in procs] + procs, own_only=False))
        proc_trigger = len(triggers)
        conds.append(B.cond(
            B.T({"trigger": proc_trigger, "variable": "show", "value": 1}),
            [B.change(f"sub.{glow_index}.glow", True),
             B.change(f"sub.{glow_index}.glowColor",
                      B.rgba(1.0, 0.95, 0.5, 1.0))]))
        if name in PROC_STACKS:
            # `%s` is trigger 1's stack count, which on a spell cooldown
            # trigger means CHARGES -- Reverse Wound has none, so it would
            # draw a permanent "1". `%N.s` is the documented per-trigger form
            # (TextReplacements: `%<trigger>.<variable>`), so the number comes
            # off the Endless Sands aura instead.
            stack_text = B.sub_text(f"%{proc_trigger}.s",
                                    size=max(11, int(size * 0.34)),
                                    anchor="INNER_TOPRIGHT",
                                    color=(1.0, 0.95, 0.6, 1.0), visible=False)
            # Same shape as the `%s` key sub_text writes for trigger 1. Without
            # it WeakAuras has no format entry for this placeholder and the
            # text option page comes up blank for the sub-region.
            stack_text[f"text_text_format_{proc_trigger}.s_format"] = "none"
            subs.append(stack_text)
            # Hidden unless the buff is actually up: an aura trigger reports no
            # stacks when the aura is absent, and an empty `%N.s` still leaves
            # the sub-region drawing at full size in the corner.
            conds.append(B.cond(
                B.T({"trigger": proc_trigger, "variable": "show", "value": 1}),
                [B.change(f"sub.{len(subs)}.text_visible", True)]))

    icon = B.icon(display_id, parent, triggers, ic(name), size=size,
                  inverse=True, subregions=subs, conditions=conds or None)
    icon["cooldownTextDisabled"] = bool(urgency)
    return icon


def proc_glow_for(name, subs, triggers):
    """Attach a proc-driven glow. Returns the conditions list, or None."""
    procs = PROC_GLOW.get(name)
    if not procs:
        return None
    subs.append(B.sub_glow(False, "buttonOverlay", (1.0, 0.9, 0.45, 1.0)))
    glow_index = len(subs)
    triggers.append(B.aura_trigger(
        [str(sid(p)) for p in procs] + procs, own_only=False))
    return [B.cond(
        B.T({"trigger": len(triggers), "variable": "show", "value": 1}),
        [B.change(f"sub.{glow_index}.glow", True)])]


def charge_text(size):
    """Charge counter. %s maps to the trigger's stack count, which the spell
    cooldown trigger populates with charges."""
    return B.sub_text("%s", size=max(11, size // 2), anchor="INNER_TOPRIGHT",
                      color=(1, 1, 1, 1))


def cd_group(gid, parent, names, y, size=SZ_SMALL, x=0, glow=False,
             text_size=None, spec=None):
    """Flush row of cooldown icons.

    Trigger 1 (showAlways) drives the icon; trigger 2 (showOnCooldown) feeds a
    condition that desaturates and dims it. Availability therefore reads at a
    glance without anything flashing. `variable: "show"` is used because it is
    the one condition variable every trigger type exposes.
    """
    ids = []
    for n in names:
        # ONE trigger only. Adding a second `showOnCooldown` trigger plus a
        # desaturate condition collapsed these icons to cooldown-only: nothing
        # rendered out of combat, and in combat only the spells actually on
        # cooldown appeared, dimmed. Keep the display dead simple -- always
        # visible, cooldown swipe carries availability.
        ids.append(add(cd_icon(f"{gid} {n}", gid, n, size,
                               charges=n in CHARGES, spec=spec)))
    add(B.dynamicgroup(gid, parent, ids, x=x, y=y, grow="HORIZONTAL", space=GAP))
    return gid


def buff_group(gid, parent, entries, y, x=0, size=SZ_SMALL, icon_for=None,
               unit="player", helpful=True, glow=False, stacks=True):
    """Flush row of aura icons. These only exist while the aura is up, so they
    are the natural place for a glow -- everything shown here is actionable."""
    ids = []
    for entry in entries:
        # (name, colour) or (name, colour, {"unit":..., "helpful":...}) -- the
        # override lets a target debuff live in an otherwise player-buff row
        name, col = entry[0], entry[1]
        opts = entry[2] if len(entry) > 2 else {}
        e_unit = opts.get("unit", unit)
        e_helpful = opts.get("helpful", helpful)
        # timer sized off the icon rather than a fixed small value -- at 26px
        # it was 8pt and unreadable
        subs = [B.sub_text("%p", size=max(12, int(size * 0.38)),
                           anchor="INNER_BOTTOM")]
        if stacks:
            subs.append(B.sub_text("%s", size=max(11, int(size * 0.34)),
                                   anchor="INNER_TOPRIGHT",
                                   color=(1, 0.95, 0.6, 1)))
        subs.append(thin())
        if glow:
            subs.append(B.sub_glow(True, "buttonOverlay", col + (1.0,)))
        ids.append(add(B.icon(
            f"{gid} {name}", gid,
            [B.aura_trigger([sid(name), name], unit=e_unit,
                            helpful=e_helpful)],
            ic(icon_for(name) if icon_for else name), size=size,
            subregions=subs)))
    add(B.dynamicgroup(gid, parent, ids, x=x, y=y, grow="HORIZONTAL", space=GAP))
    return gid


def dot_bars(gid, parent, entries, y, x=0, unit="target", helpful=False,
             w=None, size=SZ_SMALL, refresh_at=None):
    """THE TARGET BAND: what YOU have on your CURRENT target.

    `helpful=False` -> your DoTs, shown while an enemy is targeted.
    `helpful=True`  -> your HoTs and absorbs, shown while an ally is targeted.

    Both sets are active-only, so retargeting swaps the contents with no extra
    machinery: an enemy target shows your debuffs, a friendly target shows your
    HoTs, no target shows nothing. There is deliberately NO multi-target
    tracking here, for healers or anyone else -- raid-wide HoT state belongs to
    VuhDo/Grid, which own that job on 3.3.5a.

    `own_only` is non-negotiable and comes from aura_trigger's default. Without
    it the band fills with every other player's auras on your target and is
    unreadable in a raid.

    `refresh_at` glows an icon once it has fewer than that many seconds left --
    the "reapply this now" cue. `expirationTime` on an aura2 trigger is SECONDS
    REMAINING, and unlike the same variable on a Cooldown Progress (Spell)
    trigger it needs NO `onCooldown` guard: there is no global cooldown
    contaminating an aura's timer. Witnessed in a working pack
    (chronomancer-nnoop's Ripple: expirationTime <= 3.5 -> sub glow).

    ⚠️ `B.sub_background()` is emitted EXPLICITLY. WeakAuras' own
    `EnforceSubregionExists` inserts a background at index 1 on import if one
    is absent, shifting every `sub.N.*` reference by one -- so a glow computed
    against this list would arrive pointing at the border instead.
    """
    ids = []
    for name, col, note in entries:
        subs = [B.sub_background(),
                B.sub_text("%p", size=10, anchor="INNER_BOTTOM"),
                B.sub_text("%s", size=10, anchor="INNER_TOPRIGHT"),
                B.sub_border(color=col + (1.0,), size=2, offset=1,
                             edge=EDGE)]
        conds = None
        if refresh_at:
            subs.append(B.sub_glow(False, "buttonOverlay",
                                   (1.0, 0.85, 0.35, 1.0)))
            conds = [B.cond(
                B.T({"trigger": 1, "variable": "expirationTime",
                     "op": "<=", "value": str(refresh_at)}),
                [B.change(f"sub.{len(subs)}.glow", True)])]
        # Match by exact spell id where we can, by NAME where the spell is
        # ranked.
        #
        # Exact id is much safer for the Aeon-applied effects, whose names are
        # "Protection", "Renewal", "Resilience", "Oblivion" -- generic enough
        # that a name match would bind to any other aura sharing the word.
        #
        # But a ranked spell must fall back to the name: IsSpellKnown-style
        # exactness applies here too, and Melt Reality / Timerend / Unmake /
        # Decomposition / Accelerated Recovery are all Rank 1 ids, so an exact
        # match would track a rank the character has outgrown.
        _sid = sid(name)
        _ranked = str((SPELL_META.get(str(_sid)) or {}).get("rank") or "") \
            .startswith("Rank ")
        _trig = (B.aura_trigger([str(_sid)], unit=unit, helpful=helpful,
                                exact_id=True)
                 if not _ranked else
                 B.aura_trigger([str(_sid), name], unit=unit, helpful=helpful))
        ids.append(add(B.icon(
            f"{gid} {name}", gid, [_trig],
            ic(name), size=size, subregions=subs, conditions=conds)))
    add(B.dynamicgroup(gid, parent, ids, x=x, y=y, grow="HORIZONTAL", space=GAP))
    return gid


def seg_bar(prefix, parent, entries, y, always_trigger, total_w, out,
            h=SEG_H, gap=GLYPH_GAP, text="%p"):
    """A DK-rune-style segmented bar spanning `total_w`.

    Each segment is two stacked solid textures: a dim outline in the element
    colour, held on by `always_trigger`, and a solid fill drawn over it while
    that aura is up. Two displays rather than one plus a condition, because
    conditions in this fork have misfired before.
    """
    n = len(entries)
    w = (total_w - (n - 1) * gap) // n
    for i, (name, keys, col) in enumerate(entries):
        x = int((i - (n - 1) / 2) * (w + gap))
        out.append(add(B.texture(
            f"{prefix} Empty {name}", parent, [always_trigger],
            tex=SOLID, x=x, y=y, w=w, h=h, color=col + (0.38,),
            blend="BLEND")))
        out.append(add(B.texture(
            f"{prefix} Fill {name}", parent,
            [B.aura_trigger(keys, own_only=False)],
            tex=SOLID, x=x, y=y, w=w, h=h, color=col + (1.0,), blend="BLEND",
            subregions=[B.sub_text(text, size=11, anchor="CENTER",
                                   color=(1, 1, 1, 1))])))


def stack_bar(prefix, parent, aura, cells, col, y, always_trigger, total_w, out,
              h=SEG_H, gap=GLYPH_GAP):
    """Segmented bar driven by the STACK COUNT of a single aura.

    `seg_bar` above reads N different auras and lights cell i when aura i is
    up -- Glyphic's Frost/Flame/Arcane. This reads ONE aura and lights cell i
    when it holds at least i stacks, which is what a points-style resource
    actually is: Artificer's Echo Fragments (804455, "Stacks 5 times") and
    Time's Sands of Time (804488, "stacking 5 times, upon spending the 5th
    stack all stacks are consumed").

    The difference is entirely in the trigger -- `useStacks` + a per-cell
    threshold instead of N name matches. `aura_trigger` already emits both
    fields, and the pairing is witnessed in a working pack
    (chronomancer-nnoop's `Glow 2`: useStacks true, stacks "5").

    Same two-displays-per-cell rule as seg_bar: a dim outline always present,
    a solid fill over it. NOT one display plus a condition -- conditions in
    this fork have misfired before, and a resource bar is glanced at more than
    anything else in the pack.
    """
    w = (total_w - (cells - 1) * gap) // cells
    for i in range(cells):
        x = int((i - (cells - 1) / 2) * (w + gap))
        out.append(add(B.texture(
            f"{prefix} Empty {i + 1}", parent, [always_trigger],
            tex=SOLID, x=x, y=y, w=w, h=h, color=col + (0.38,),
            blend="BLEND")))
        # stacks >= i+1: cell 1 lights at one stack, cell 5 only at five.
        out.append(add(B.texture(
            f"{prefix} Fill {i + 1}", parent,
            [B.aura_trigger([str(aura)], stacks=i + 1, stacks_op=">=")],
            tex=SOLID, x=x, y=y, w=w, h=h, color=col + (1.0,),
            blend="BLEND")))


def row_w(n, size=SZ_MAIN):
    """Exact pixel width of a flush row, so the resource bar lines up with it."""
    return n * size + (n - 1) * GAP


def mana_bar(gid, parent, y, color, w=None, h=None):
    add(B.aurabar(gid, parent, [B.power_trigger("player", 0)],
                  x=0, y=y, w=w or BAR_W, h=h or BAR_H, color=color,
                  subregions=[
                      B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                 justify="RIGHT"),
                  ]))
    return gid


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# Active-only row at the bottom: state you check once per pull rather than
# react to. Runemaster filled this with runic tattoos and weapon engravings;
# Chronomancer has no imbue kit at all, so it carries the class Intellect buff
# and -- on Time -- which AEON is currently up.
LONGTERM = []

# The 30-minute self-buff family. This is Chronomancer's equivalent of
# Runemaster's tattoos and weapon engravings: things you set once at the start
# of a session and only notice when they have dropped.
#
# WISDOMS ARE MUTUALLY EXCLUSIVE. Chromie's Wisdom says it outright -- "Only
# one Wisdom per Chronomancer can be active" -- so Intellect and Spirit are a
# choice, not a stack. That is why the reminder below fires on NONE of the four
# rather than per-buff: nagging for the one you deliberately did not take would
# be permanently on screen, which is the exact failure the reminder band had on
# Runemaster.
WISDOMS = [
    ("Nozdormu's Wisdom", 572391, (0.55, 0.75, 1.00)),          # +Intellect
    ("Greater Nozdormu's Wisdom", 572396, (0.55, 0.75, 1.00)),
    ("Chromie's Wisdom", 801523, (0.95, 0.80, 0.45)),           # +Spirit
    ("Greater Chromie's Wisdom", 680307, (0.95, 0.80, 0.45)),
]
# The three "Surround yourself with <school> magic" buffs, all 30 min, all
# self-cast. Whether these are ALSO mutually exclusive is unconfirmed -- the
# tooltips do not say so and only the Wisdoms carry the exclusivity line. The
# band is active-only either way, so it renders correctly under both readings;
# worth one in-game check before the reminder below is trusted.
TEMPORALS = [
    ("Temporal Restoration", 680456, (0.45, 0.90, 0.55)),   # mana regen in combat
    ("Temporal Resilience", 680389, (0.80, 0.70, 0.50)),    # armor + slows attackers
    ("Temporal Swiftness", 680390, (0.60, 0.85, 1.00)),     # spell haste from Spirit
]
for _name, _aura, _col in WISDOMS + TEMPORALS:
    LONGTERM.append(add(B.icon(
        f"CM Longterm {_name}", "CM Longterm",
        [B.aura_trigger([str(_aura), _name], own_only=False)],
        ic(_name), size=SZ_SMALL,
        subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                               color=_col + (1.0,)),
                    thin()])))

# The four Aeons. Infinite-duration mutually-exclusive self-buffs that reshape
# BOTH Epoch and Ripple, so which one is up is persistent state rather than a
# proc -- long-term is exactly the band for it.
#
# MATCH BY SPELL ID, NEVER BY NAME. Two decoys share the namespace: 807158 is
# a second "Aeon of Resilience" teaching passive, and 583921 is
# "Aeon of Oblivion SLS", a stale stub carrying the same name AND the same
# icon with 1% crit against the live 30%. A name match takes either one.
#
# Resilience is 806291, NOT the 92119 db.exil.es reports -- that id is the
# level 10 passive whose whole tooltip is "Teaches you Aeon of Resilience",
# and it has no cooldown row, which is the documented smell for a wrong id.
# Two independent routes agree on 806291: it is the hole in the otherwise
# contiguous 806290/806292/806293 block, and a working community pack uses it
# alongside the other three.
#
# NO `%p` TIMER on these. duration_ms is -1, so UnitAura reports duration 0 and
# expirationTime 0; a timer subregion would render empty forever.
AEONS = [
    ("Renewal",    806290, (0.45, 0.90, 0.55)),
    ("Resilience", 806291, (0.95, 0.85, 0.45)),
    ("Protection", 806292, (0.55, 0.75, 1.00)),
    ("Oblivion",   806293, (0.90, 0.35, 0.35)),
]
for _label, _aura, _col in AEONS:
    LONGTERM.append(add(B.icon(
        f"CM Longterm Aeon of {_label}", "CM Longterm",
        [B.aura_trigger([str(_aura)], exact_id=True)],
        ic(f"Aeon of {_label}"), size=SZ_SMALL,
        subregions=[B.sub_text(_label[:3].upper(), size=9,
                               anchor="INNER_BOTTOM", color=_col + (1.0,)),
                    thin()])))

add(B.dynamicgroup("CM Longterm", "CM Core", LONGTERM, x=0, y=Y_LONG,
                   grow="HORIZONTAL", space=GAP))
CORE.append("CM Longterm")

# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Data here rather than displays, same as Runemaster.
SHORT_ENTRIES = [
    ("Temporal Focus", (0.70, 0.80, 1.00), {}),
    ("Time Out!", (1.00, 0.60, 0.30), {}),
    ("Hasten", (0.50, 0.90, 1.00), {}),
    ("Timeguard", (0.80, 0.70, 1.00), {}),
    ("Shield of the Ages", (0.60, 0.85, 1.00), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# High and central, and invisible once you are buffed -- each fires only on
# ABSENCE. Chronomancer has one class-wide case; Time adds its own no-Aeon
# reminder inside the spec block, where the spec gate applies to it.
ALERTS = []

for _label, _set, _art in (("NO WISDOM", WISDOMS, "Nozdormu's Wisdom"),
                           ("NO TEMPORAL", TEMPORALS, "Temporal Restoration")):
    ALERTS.append(add(B.icon(
        f"CM Alerts {_label.title()}", "CM Alerts",
        [B.aura_trigger([str(a) for _n, a, _c in _set]
                        + [_n for _n, _a, _c in _set],
                        own_only=False, show_on="showOnMissing")],
        ic(_art), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text(_label, size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])))

add(B.dynamicgroup("CM Alerts", "CM Core", ALERTS, x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
CORE.append("CM Alerts")

add(B.group("CM Core", ROOT, CORE, x=0, y=0))

def emit_bottom_block(spec_name, spec_key, out, procs, state=()):
    """Three stacked rows under the resource bar:

        1. Offense   -- damage cooldowns, Ley Lock + Leyline Adjustment last
        2. Utility   -- defensives and utility merged
        3. Buffs     -- short-window procs, active-only

    All three specs start at the same Y_CDS: the resource envelope above is a
    fixed height whatever a spec puts in it, so there is no per-spec offset to
    apply and no empty band left behind. Returns the y for the DoT row.
    """
    offense, utility = _bottom_rows(spec_key)

    y = Y_CDS

    for label, names in (("Offense", offense), ("Utility", utility)):
        ids = []
        for n in names:
            ids.append(add(cd_icon(f"CM {spec_name} {label} {n}",
                                   f"CM {spec_name} {label}", n, SZ_CD,
                                   charges=n in CHARGES, urgency=True,
                                   spec=spec_key)))
        # NO TRINKETS. On-use trinkets are player gear, not class content --
        # every player runs a different pair, so a class pack cannot know them
        # and anyone who wants them can add two icons themselves.
        #
        # They were also a crash source: slot_cd_trigger defaults to
        # genericShowOn="showAlways", so the trigger stayed active while the
        # slot was empty or the trinket had no on-use cooldown, and WeakAuras
        # then supplied no duration/expirationTime. Paired with cooldown=True
        # the swipe path in Icon.lua PreShow did arithmetic on nil:
        #   Icon.lua:642: attempt to perform arithmetic on field
        #   'expirationTime' (a nil value)
        # which errored on every ScanEvents and wedged the WA UI.
        #
        # Standing rule regardless of trinkets: NEVER pair inverse=True with
        # cooldown=True. An inverse display shows precisely when there is no
        # cooldown to draw, so the swipe can only ever be nil arithmetic.
        if not ids:
            continue
        # GRID, not HORIZONTAL: these are the two rows that overrun. It wraps
        # on the children actually SHOWING, so a shared band still renders
        # exactly the loaded spec's icons and re-centres around them --
        # a build-time split into chunks could not, since each spec owns a
        # different subset and would get two ragged part-rows.
        # BALANCED rows, not fill-then-spill. CD_PER_ROW is the MAXIMUM a row
        # may hold; once the row count is known, divide evenly instead. Ten
        # icons at CD_PER_ROW=7 is 7+3, which reads as a full row with a stub
        # under it; 5+5 reads as one block. Odd counts put the extra on top
        # (9 -> 5+4), so the wider row is the one nearer the main rotation.
        _rows = max(1, -(-len(ids) // CD_PER_ROW))
        _per = -(-len(ids) // _rows)
        add(B.dynamicgroup(f"CM {spec_name} {label}", f"CM {spec_name}", ids,
                           x=0, y=y, grow="GRID", space=GAP,
                           grid_width=_per, row_space=CD_ROW_STEP - SZ_CD))
        out.append(f"CM {spec_name} {label}")
        # This spec's OWN row count. The bands are no longer shared, so each
        # spec's ladder closes up behind its own rows instead of reserving
        # room for the deepest spec in the pack.
        y -= max(1, -(-len(names) // CD_PER_ROW)) * CD_ROW_STEP

    # An offensive cooldown that is CURRENTLY RUNNING belongs in the buff row
    # too -- otherwise the only cue that Zenith or Primordial Fury is live is
    # the cooldown swipe, which reads as "unavailable" rather than "active".
    # Derived from the offense row so a new cooldown cannot be forgotten; the
    # tail (Ley Lock, Leyline Adjustment) is skipped as it applies no buff, and
    # anything that does not apply one simply never shows.
    # dedupe against BOTH the procs and the state entries -- Genesis is a
    # target debuff and already listed there, and a repeated name would emit
    # two displays with the same id, which WeakAuras rejects on import
    named = {e[0] for e in procs} | {e[0] for e in state}
    # Mobility and self-rescue apply no buff worth a second icon, so they are
    # skipped here rather than listed in a separate tail.
    _NO_BUFF = {"Displacement", "Backtrack", "Rewind", "Infinite Clone"}
    cd_buffs = [(n, (1.0, 0.80, 0.30)) for n in offense
                if n not in named and n not in _NO_BUFF]

    # ONE row for everything currently up: procs, running cooldowns, self
    # buffs and target debuffs. They are all active-only, so the row packs to
    # whatever is actually live rather than to its full length.
    out.append(buff_group(f"CM {spec_name} Buffs", f"CM {spec_name}",
                          procs + cd_buffs + list(state),
                          y=Y_BUFFS, size=SZ_BUFF, glow=True))
    return y


# ============================================================== 2. ARTIFICER
# Ranged wand spec. Artificer's Wand is the filler and the Echo Fragment
# generator; fragments are spent on Distortion spells and on extending whichever
# Continuum spell is active (only one at a time).
A = []
A.append(cd_group("CM Artificer Main", "CM Artificer",
                  ["Artificer's Wand", "Wand of Time", "Discordance",
                   "Shatter Echo", "Decomposition"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="artificer"))
A.append(mana_bar("CM Artificer Mana", "CM Artificer", Y_BAR,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5), h=BAR_H_STACKED))
# Echo Fragments: "Used to empower some abilities. Stacks 5 times." One aura
# (804455) whose stack count fills the row, so this is stack_bar rather than
# seg_bar -- there is no set of five distinct auras to match.
stack_bar("CM Fragment", "CM Artificer", 804455, 5, (0.55, 0.85, 1.00),
          Y_SEG, B.health_trigger("player"), row_w(5), A)
# Your DoT on the target. Threads of Eternity rides Discordance.
# "Thread of Eternity" (572127) is the DOT. "ThreadS of Eternity" (806209) is
# the PASSIVE that applies it -- rank "Passive", duration -1, never on a target.
# One letter apart, and the band showed nothing because of it.
A.append(dot_bars("CM Artificer Target", "CM Artificer",
                  [("Thread of Eternity", (0.75, 0.55, 1.00), {})],
                  y=Y_TARGET, refresh_at=4))
_y_A = emit_bottom_block("Artificer", "artificer", A,
                         [("Discovery", (0.6, 0.9, 1.0)),
                          ("Clocked In", (1.0, 0.85, 0.4)),
                          ("Singularity Core", (0.8, 0.6, 1.0)),
                          ("Flux Emitter", (0.5, 0.9, 0.8)),
                          ("Aether Compression", (0.7, 0.8, 1.0)),
                          ("Paradox Cannon", (1.0, 0.7, 0.4))],
                         SHORT_ENTRIES)
add(spec_group("CM Artificer", A))

# =============================================================== 3. INFINITE
# Chaos DoT caster. Mana only -- Sidekick is explicit that there is "no dual
# Order/Chaos economy" -- so the resource envelope holds one full-height bar
# and no segment row.
I = []
I.append(cd_group("CM Infinite Main", "CM Infinite",
                  ["Chromatic Shard", "Melt Reality", "Timerend", "Unmake",
                   "Discordance"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="infinite"))
I.append(mana_bar("CM Infinite Mana", "CM Infinite", Y_BAR_SOLO,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5)))
# The spec IS its DoTs -- Anomaly Spikes, the haste stacks and the cooldown
# shave all key off periodic damage, so anything dropping is a real loss.
I.append(dot_bars("CM Infinite Target", "CM Infinite",
                  [("Melt Reality", (0.90, 0.35, 0.85), {}),
                   ("Timerend", (0.70, 0.60, 1.00), {}),
                   ("Unmake", (0.85, 0.45, 0.35), {}),
                   ("Decomposition", (0.60, 0.85, 0.55), {})],
                  y=Y_TARGET, refresh_at=5))
_y_I = emit_bottom_block("Infinite", "infinite", I,
                         [("Anomaly Spikes", (0.9, 0.5, 1.0)),
                          ("Hourglass of Eternity", (0.5, 0.9, 1.0)),
                          ("Infinite Power", (1.0, 0.85, 0.4)),
                          ("Chaos Fusion", (1.0, 0.5, 0.3)),
                          ("Chaotic Time", (0.8, 0.4, 0.9))],
                         SHORT_ENTRIES)
add(spec_group("CM Infinite", I))

# =================================================================== 4. TIME
# The first HEALING spec in any CoA pack. Healing surfaces are scoped OUT by
# design -- no raid frames, no multi-target HoT grid. What it gets instead is
# the target band above, carrying your own HoTs and absorbs on whoever you have
# selected, glowing when one needs a refresh.
T = []

# Ripple is FIVE displays, not one. `Eternity Warper` (806301) gives the Ripple
# channel a different effect per active Aeon, and each of those four effects is
# its own spell with its own art. So each variant is gated on its Aeon's aura
# and only the matching one is ever showing -- the dynamic group lays out
# exactly one, the same loaded-and-showing mechanism that lets a single band
# serve three specs.
#
# The alternative -- one display with four aura triggers swapping displayIcon
# by condition -- is fewer displays but bets the MAIN ROTATION ICON on
# condition reliability, and conditions in this fork have misfired before.
#
# The fifth is not padding. A character who has never cast an Aeon has none:
# the level 10 passive only TEACHES Aeon of Resilience, it does not apply the
# stance. That state is reachable and it needs an icon.
# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

# Displays whose icon is chosen by a CONDITION at runtime. They need
# iconSource = 0 or SetIcon has no effect -- state.icon wins and the swap
# is invisible. Kept as a registry so the blanket pass below cannot quietly
# reset them the way it did once already.
NEEDS_MANUAL_ICON = set()

# (label, Aeon aura id, Eternity Warper's Ripple spell id, art name)
#
# The icon shows WHICH Ripple you are about to cast, so you never have to check
# your Aeon first -- Aeon of Oblivion means Ripple reads as Rippling Oblivion.
#
# Two ids per row and the trigger matches EITHER. `auraspellids` is an
# any-of list, so one aura2 trigger covers both without touching disjunctive:
#   * the Aeon stance itself (806290..806293), infinite duration; and
#   * the `Rippling *` spell Eternity Warper grants (560382..560395), which the
#     research flagged as a duration -1 self aura the server may swap in when
#     the Aeon changes.
# Whichever the client actually exposes, the icon resolves. Matching only the
# Aeon left Ripple stuck on its default face in game.
RIPPLE_MODES = [
    ("Renewal",    806290, 560382, "Rippling Renewal"),
    ("Resilience", 806291, 560395, "Rippling Resilience"),
    ("Protection", 806292, 560393, "Rippling Protection"),
    ("Oblivion",   806293, 560386, "Rippling Oblivion"),
]

# The main row is built by hand rather than through cd_group, because Ripple
# is five icons that occupy ONE slot. Each variant carries Ripple's own
# cooldown trigger PLUS its Aeon's aura, so exactly one is ever loaded-and-
# showing, and the dynamic group lays out the row around whichever that is.
_time_main = []
# Press order. Reverse Wound sits next to Accelerated Recovery because that is
# what it is read against: it is the spot heal between HoT refreshes, and the
# Endless Sands count on its corner says how cheap the next cast is.
for _n in ("Epoch", "Accelerated Recovery", "Reverse Wound",
           "Correct the Mistake"):
    _time_main.append(add(cd_icon(f"CM Time Main {_n}", "CM Time Main", _n,
                                  SZ_MAIN, spec="time")))

# Ripple is ONE display whose ICON changes with the active Aeon, so you can see
# which effect you are about to get without checking your stance first.
#
# This is what the Icon region is built for. `RegionTypes/Icon.lua` declares
#     displayIcon = { display = {L["Icon"], L["Manual"]}, setter = "SetIcon",
#                     type = "icon" }
# as a CONDITION PROPERTY, so a condition may call SetIcon at runtime.
#
# ⚠️ It only works with `iconSource = 0`. UpdateIcon() resolves:
#       iconSource == -1 -> state.icon   (whatever the TRIGGER supplies)
#       iconSource ==  0 -> displayIcon  (what we set)
#     iconPath = iconPath or self.displayIcon or QUESTIONMARK
# Every icon we emit carried -1, which is why five different Rippling textures
# all drew as the same staff: the trigger tracks spell 806296 for all of them,
# so state.icon won and displayIcon was never more than a fallback.
_ripple = cd_icon("CM Time Main Ripple", "CM Time Main", "Ripple", SZ_MAIN,
                  spec="time")
_ripple["iconSource"] = 0
NEEDS_MANUAL_ICON.add(_ripple["id"])
_rip_conds = list((_ripple.get("conditions") or {}).values()) \
    if isinstance(_ripple.get("conditions"), dict) else list(_ripple.get("conditions") or [])
_rip_trigs = _triggers_of(_ripple)

# Trigger 2 is ETERNITY WARPER itself (806301) -- the level 50 passive that
# gives Ripple its per-Aeon behaviour in the first place.
#
# Without it the icon LIES to a levelling character: Aeon of Resilience is
# taught at level 10, so a level 20 Chronomancer with an Aeon up would see
# "Rippling Oblivion" and be promised an effect the passive has not granted.
# Every face is therefore ANDed with this, and below 50 Ripple stays on its
# own icon, which is exactly what it does.
#
# ⚠️ NOT an aura trigger. 806301 is `effect=6 aura=4` -- APPLY_AURA /
# SPELL_AURA_DUMMY on self -- which is how 3.3.5 implements a passive, and
# those are hidden from UnitAura. An aura2 trigger on it never fires, so every
# AND below failed and Ripple stayed on its default face no matter the Aeon.
#
# "Spell Known" is the prototype built for this question: it runs
# `WeakAuras.IsSpellKnown(806301)` off SPELLS_CHANGED / PLAYER_TALENT_UPDATE,
# so it is true exactly when the character actually has Eternity Warper, and
# it re-checks on a respec.
_rip_trigs.append(B.spell_known_trigger(806301))
_EW = len(_rip_trigs)

# Match the AEON STANCES only (806290..806293). They are genuinely mutually
# exclusive -- one Aeon at a time, shared cooldown.
#
# NOT the `Rippling *` spells: those are `aura=42` PROC_TRIGGER_SPELL auras on
# self with duration -1, so if the server grants all four when Eternity Warper
# is learned they would all match at once and the last condition would win,
# pinning the icon to one face permanently.
for _label, _aeon, _rip, _art in RIPPLE_MODES:
    _rip_trigs.append(B.aura_trigger([str(_aeon)], exact_id=True))
    _rip_conds.append(B.cond(
        B.check_and(
            B.T({"trigger": len(_rip_trigs), "variable": "show", "value": 1}),
            B.T({"trigger": _EW, "variable": "show", "value": 1})),
        [B.change("displayIcon", ic(_art))]))
_ripple["triggers"] = B._trigger_wrap(_rip_trigs)
# "any": trigger 1 alone must keep Ripple on screen with no Aeon and no
# Eternity Warper. The conditions, not the trigger logic, pick the face.
_ripple["triggers"]["disjunctive"] = "any"
_ripple["conditions"] = B.arr(_rip_conds)
_time_main.append(add(_ripple))

add(B.dynamicgroup("CM Time Main", "CM Time", _time_main, x=0, y=Y_MAIN,
                   grow="HORIZONTAL", space=GAP))
T.append("CM Time Main")
# row_w(5): Epoch + Accelerated Recovery + Reverse Wound + Correct the Mistake
# + exactly ONE Ripple variant. Five Ripple displays are stored but only one is
# ever loaded-and-showing, so the row a player sees is five icons wide and the
# bar has to lock to that -- it was row_w(4) before Reverse Wound joined the row.
T.append(mana_bar("CM Time Mana", "CM Time", Y_BAR,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5), h=BAR_H_STACKED))
# Sands of Time: "stacking 5 times. Upon spending the 5th stack, all stacks are
# consumed." Built by casting Epoch, so it is the spec's real spend meter.
# 804488 is the BUFF; 501843 is the castable that grants it -- both are
# legitimately named "Sands of Time", which is why this matches by id.
stack_bar("CM Sands", "CM Time", 804488, 5, (0.95, 0.80, 0.45),
          Y_SEG, B.health_trigger("player"), row_w(5), T)
# YOUR HoTs and absorbs on YOUR TARGET, glowing when one is nearly out. This is
# the band the whole healing-scope decision turns on.
# YOUR heals and absorbs on YOUR TARGET, glowing when one is nearly out.
#
# The previous contents could never appear: "Aeon of Protection" is the STANCE
# you stand in (duration -1, on you), not the absorb it puts on the target, and
# "Mark of Order" is a passive. The real per-target effects are the four Aeon
# ones, each named for its Aeon without the "Aeon of" prefix:
#     Protection 560374  8s absorb
#     Renewal    560355  3s HoT
#     Resilience 560373  6s damage reduction
#     Oblivion   560376  5s damage buff on the target
T.append(dot_bars("CM Time Target", "CM Time",
                  [("Accelerated Recovery", (0.50, 0.90, 0.60), {}),
                   ("Protection", (0.55, 0.75, 1.00), {}),
                   ("Renewal", (0.45, 0.90, 0.55), {}),
                   ("Resilience", (0.95, 0.85, 0.45), {}),
                   ("Oblivion", (0.90, 0.35, 0.35), {})],
                  y=Y_TARGET, helpful=True, refresh_at=4))
_y_T = emit_bottom_block("Time", "time", T,
                         [("Sands of Time", (0.95, 0.8, 0.45)),
                          ("Endless Sands", (1.0, 0.9, 0.6)),
                          ("Ripple in Time", (0.6, 0.85, 1.0)),
                          ("Cadence of Time", (0.8, 0.7, 1.0)),
                          ("Shield of the Ages", (0.6, 0.85, 1.0)),
                          ("Fabric of Time", (0.9, 0.75, 1.0))],
                         SHORT_ENTRIES)
add(spec_group("CM Time", T))


# ------------------------------------------------- Infinite Clone -> Rewind
# One slot, two faces. Casting Infinite Clone (804492, 3 min) leaves a 10 sec
# player aura (704154) during which Rewind (801294) returns you to the clone's
# health, mana and position. You almost always want to spend it before it
# lapses, so the icon becomes Rewind for those ten seconds and its glow
# escalates as the window closes.
#
# Same mechanism as the Ripple variants and the shared bands: both displays
# live in the row, exactly one is ever loaded-and-showing, so the row lays out
# around whichever it is. `disjunctive` must be ALL (its default) or the
# always-true cooldown trigger shows both at once.
CLONE_WINDOW = 704154          # the 10 sec "Infinite Clone" player aura


def _subglow_index(display):
    """1-based index of the glow subregion, for a `sub.N.glow` property."""
    subs = display.get("subRegions") or []
    subs = list(subs.values()) if isinstance(subs, dict) else list(subs)
    for i, sub in enumerate(subs, 1):
        if isinstance(sub, dict) and sub.get("type") == "subglow":
            return i
    return None


def pair_clone_rewind():
    """Infinite Clone and Rewind share ONE slot.

    Casting Infinite Clone (804492, 3 min) leaves a 10 sec player aura
    (704154). While it is up, Rewind (801294) returns you to the clone's
    health, mana and position -- and you almost always want to spend it before
    it lapses, so the icon becomes Rewind for those ten seconds and the glow
    escalates as the window closes.

    Exactly one of the two is ever loaded-and-showing, so the row lays out
    around whichever it is.

    ⚠️ Finds them by NAME, not by band. An earlier version filtered on
    `" Offense " in id`; when Rewind was recategorised as defensive both
    displays moved to the Utility band, this matched nothing, and the pairing
    silently vanished -- no window trigger, no glow, two unrelated icons. The
    assert at the end is why that cannot repeat: a pairing that matches
    nothing is a build failure, not a quiet no-op.
    """
    CLONE_WINDOW = 704154            # the 10 sec "Infinite Clone" player aura
    found = {}
    for c in list(children):
        for suffix in (" Infinite Clone", " Rewind"):
            if not c["id"].endswith(suffix):
                continue
            is_rewind = suffix == " Rewind"
            trs = _triggers_of(c)
            trs.append(B.aura_trigger([str(CLONE_WINDOW)], exact_id=True)
                       if is_rewind
                       else B.aura_trigger([str(CLONE_WINDOW)], exact_id=True,
                                           show_on="showOnMissing"))
            c["triggers"] = B._trigger_wrap(trs)
            c["triggers"].pop("disjunctive", None)   # ALL: cooldown AND window
            NEEDS_ALL.add(c["id"])
            found.setdefault(c["id"].rsplit(suffix, 1)[0], set()).add(suffix)
            if not is_rewind:
                continue
            # Escalate on the WINDOW's remaining time, not Rewind's own
            # cooldown -- the thing you can lose is the window. On an aura2
            # trigger `expirationTime` is seconds remaining and needs no GCD
            # guard; that guard is only for spell-cooldown triggers.
            gi = _subglow_index(c)
            if gi is None:
                continue
            n = len(trs)
            conds = list((c.get("conditions") or {}).values()) \
                if isinstance(c.get("conditions"), dict) else list(c.get("conditions") or [])
            for secs, colour in ((5, (1.0, 0.85, 0.35, 1.0)),
                                 (3, (1.0, 0.30, 0.20, 1.0))):
                conds.append(B.cond(
                    B.T({"trigger": n, "variable": "expirationTime",
                         "op": "<=", "value": str(secs)}),
                    [B.change(f"sub.{gi}.glow", True),
                     B.change(f"sub.{gi}.glowColor", B.rgba(*colour))]))
            c["conditions"] = B.arr(conds)

    paired = [k for k, v in found.items() if len(v) == 2]
    if not paired:
        raise SystemExit(
            "pair_clone_rewind matched no Infinite Clone / Rewind pair. They "
            "must share a band -- check their Role in the ability inventory.")
    for band, halves in found.items():
        if len(halves) != 2:
            raise SystemExit(
                f"{band}: found only {sorted(halves)}. Infinite Clone and "
                f"Rewind share one slot, so they need the SAME role in "
                f"resources/abilities-{CLS.slug}.md.")
    print(f"  clone/rewind paired in {len(paired)} band(s)")


pair_clone_rewind()

# ==================================================================== ROOT
TOP = ["CM Core", "CM Artificer", "CM Infinite", "CM Time"]
root = B.group(ROOT, None, TOP, x=0, y=0)
root["url"] = ""


# ============================================================ band merging
# Which spec(s) each leaf belongs to. Populated by merge_bands() and read by
# apply_leaf_gates() and restrict_to_spec(), both of which used to infer the
# spec by walking up to a `RM <Spec>` parent -- impossible once the bands are
# shared.
LEAF_SPECS = {}

SPEC_NAMES = tuple(CLS.spec_label(sp) for sp in CLS.specs)
# Offense and Utility are deliberately NOT merged.
#
# A merged band has ONE yOffset, so the band under it must clear the spec that
# wraps DEEPEST -- Infinite's 17 offensive cooldowns at three rows. Every
# shallower spec then carries the unused rows as dead vertical space, which in
# game is a 30px hole under the row and another under the next one. Time and
# Artificer both wrap at two.
#
# Un-merging costs displays (a shared cooldown gets one copy per spec instead
# of one total) and hands back part of the final16 saving. It buys a ladder
# that is tight on EVERY spec, which is the whole point of a fixed layout.
#
# Main and Buffs stay merged: Main is one row on every spec so there is nothing
# to reserve, and Buffs is active-only, so its stored length never becomes
# vertical space.
MERGE_BANDS = ("Main", "Buffs")


def _band_order(seqs):
    """One order preserving every spec's sequence, where that is possible.

    Each spec orders its own row "most-pressed first" and that ordering is
    load-bearing (`controlledChildren` order is what the comparator refuses to
    normalise away). Merging three rows into one must not quietly reshuffle
    them, so this is a topological sort over the union: an edge a->b for every
    adjacent pair in every spec.

    Main, Offense and Utility have NO conflicting pairs, so for them the merge
    is exactly lossless. Buffs has five cycles (Convergence vs Zenith, and the
    shared block against spec-specific entries), which no single order can
    satisfy; there the cycle-breaking falls back to first-appearance, which is
    tolerable because Buffs is active-only -- a handful of icons at a time, not
    a rotation you read left to right.
    """
    nodes, edges, indeg = [], {}, {}
    for seq in seqs:
        for a in seq:
            if a not in edges:
                edges[a] = []
                indeg[a] = 0
                nodes.append(a)
        for a, b in zip(seq, seq[1:]):
            if b not in edges[a]:
                edges[a].append(b)
                indeg[b] += 1
    out, ready = [], [n for n in nodes if indeg[n] == 0]
    while len(out) < len(nodes):
        if not ready:
            # cycle: break it at the earliest first-appearance node still left
            ready = [n for n in nodes if n not in out and indeg[n] > 0][:1]
        n = ready.pop(0)
        if n in out:
            continue
        out.append(n)
        for m in edges[n]:
            indeg[m] -= 1
            if indeg[m] == 0 and m not in out:
                ready.append(m)
    return out


def _leaf_spell(leaf):
    """The spell id a `use_spellknown` gate would test for this leaf."""
    trs = leaf.get("triggers") or {}
    for i in sorted(k for k in trs if isinstance(k, int)):
        tr = trs[i]["trigger"]
        s = tr.get("spellName")
        if isinstance(s, (str, int)) and str(s).isdigit():
            return int(s)
    return None


def merge_bands():
    """Collapse the three per-spec copies of each band into one shared band.

    Only ONE spec's leaves are ever loaded, and a dynamic group lays out only
    children that are loaded AND showing -- `ActivateChild` is called from the
    child's `Expand()` (DynamicGroup.lua:1227). So a single band holding all
    three specs' abilities renders exactly the loaded spec's icons, correctly
    centred, with no empty slots.

    An ability the specs share therefore needs one display rather than three.
    65 of the 185 spec leaves were such copies.

    Gating decides which abilities can actually be merged, because a merged
    leaf can no longer inherit a spec gate from its parent group:

      * one spec        -- keep the spec's signature-spell gate, unchanged
      * all three, Buffs -- class gate only. These are aura displays and are
        self-gating: an active-only display cannot show unless the buff is
        genuinely on you, so no spell check is needed or possible (a buff id is
        not a spell IsSpellKnown would recognise).
      * all three, cooldown row -- gate on the ability's OWN spell id. Exact,
        and it also fixes a levelling character seeing abilities they have not
        learned.
      * anything else (two specs, or no db.exil.es cooldown row) -- keep one
        copy per spec. `load.spellknown` holds a single id, so "Glyphic OR
        Engravement" is not expressible; and an ability with no cooldown row
        may be a proc id rather than the castable spell, where IsSpellKnown
        would fail and the icon would silently never appear.
    """
    by = {c["id"]: c for c in children}
    merged_ids, drop = [], set()

    for band in MERGE_BANDS:
        groups = [(s, f"CM {s} {band}") for s in SPEC_NAMES
                  if f"CM {s} {band}" in by]
        if not groups:
            continue

        seqs, owners, leaf_of = [], {}, {}
        for spec, gid in groups:
            cc = by[gid]["controlledChildren"]
            kids = list(cc.values()) if isinstance(cc, dict) else list(cc)
            seq = []
            for cid in kids:
                ability = cid[len(f"CM {spec} {band} "):]
                seq.append(ability)
                owners.setdefault(ability, set()).add(spec)
                leaf_of[(spec, ability)] = cid
            seqs.append(seq)

        template = by[groups[0][1]]
        order = _band_order(seqs)
        kids_out = []

        for ability in order:
            specs = owners[ability]
            # SPEC_IDS is disqualifying: those leaves only look identical. They
            # carry a different spell id per spec, so merging them would keep
            # one spec's id and hand it to all three -- and the spellknown gate
            # is derived from that same id, so the other two specs would lose
            # the icon entirely rather than merely mistrack it.
            shareable = (len(specs) == len(SPEC_NAMES)
                         and ability not in SPEC_IDS
                         and (band == "Buffs" or ability in COOLDOWNS))
            if shareable:
                # one copy, taken from the first spec that has it
                src = next(leaf_of[(s, ability)] for s in SPEC_NAMES
                           if (s, ability) in leaf_of)
                leaf = by[src]
                new_id = f"CM {band} {ability}"
                leaf["id"] = new_id
                leaf["parent"] = f"CM {band}"
                # record the specs that ACTUALLY have this ability, not the
                # set we think shareable implies. Tagging it `SPEC_NAMES` here
                # would make assert_gated() validate its own assumption, and a
                # bug in `shareable` would sail straight through.
                LEAF_SPECS[new_id] = set(specs)
                kids_out.append(new_id)
                drop |= {leaf_of[(s, ability)] for s in specs} - {src}
            else:
                for s in SPEC_NAMES:
                    cid = leaf_of.get((s, ability))
                    if not cid:
                        continue
                    by[cid]["parent"] = f"CM {band}"
                    LEAF_SPECS[cid] = {s}
                    kids_out.append(cid)

        # Carry the template's grid settings through. A wrapped band that lost
        # them here would silently revert to one unbroken line -- the merge is
        # exactly where the per-spec band stops existing, so it is the last
        # place a dropped field is still recoverable.
        merged = B.dynamicgroup(f"CM {band}", ROOT, kids_out,
                                x=template.get("xOffset", 0),
                                y=template.get("yOffset", 0),
                                grow=template.get("grow", "HORIZONTAL"),
                                space=template.get("space", GAP),
                                grid_width=template.get("gridWidth"),
                                grid_type=template.get("gridType", "HD"),
                                row_space=template.get("rowSpace", 4))
        children.append(merged)
        merged_ids.append(f"CM {band}")
        drop |= {gid for _, gid in groups}

    # Anything still under a `RM <Spec>` group keeps that spec (Glyphic's glyph
    # bar, the mana bars) -- they were never duplicated across specs.
    for c in children:
        if c["id"] in drop or c.get("controlledChildren"):
            continue
        if c["id"] in LEAF_SPECS:
            continue
        pid = c.get("parent")
        while pid and pid not in SPEC_NAMES:
            if pid in (f"CM {s}" for s in SPEC_NAMES):
                break
            nxt = by.get(pid, {}).get("parent")
            if nxt is None:
                break
            pid = nxt
        for s in SPEC_NAMES:
            if pid == f"CM {s}":
                LEAF_SPECS[c["id"]] = {s}

    # drop the emptied per-spec band groups, and any spec group left with no
    # children at all
    children[:] = [c for c in children if c["id"] not in drop]
    alive = {c["id"] for c in children}
    for c in children:
        cc = c.get("controlledChildren")
        if not cc:
            continue
        kept = [k for k in (cc.values() if isinstance(cc, dict) else cc)
                if k in alive]
        c["controlledChildren"] = B.arr(kept)
    empty = {c["id"] for c in children
             if c.get("controlledChildren") is not None
             and not len(c["controlledChildren"])
             and c["id"] in (f"CM {s}" for s in SPEC_NAMES)}
    children[:] = [c for c in children if c["id"] not in empty]

    TOP[:] = [t for t in TOP if t not in empty] + merged_ids
    root["controlledChildren"] = B.arr(TOP)


merge_bands()

# ---------------------------------------------------------------- leaf gating
# A plain `group`'s triggers/conditions/load are INERT: WeakAuras skips
# load-scanning for any aura with controlledChildren, and never registers a
# group with the trigger system. Gating on the group therefore did nothing and
# all three spec groups rendered at once, stacked at identical coordinates --
# the overlapping duplication seen in game. Every leaf carries its own gate.
#
# Verified against three working community packs: none of their 31 groups
# carries a meaningful trigger; they all gate at the leaf.
# Spell that only this spec knows. Used as the leaf load condition.
# One spell only that spec knows, for load.use_spellknown. Chosen as the
# lowest-level spec-unique ability in each tree, because a levelling character
# who has not learned it yet loses the whole spec's displays -- the gate holds
# ONE id and a wrong or late one fails silently.
SPEC_KNOWN = {
    "Artificer": 804503,   # Shatter Echo, L11
    "Infinite": 806316,    # Maw of Chaos, L10
    "Time": 806296,        # Ripple, L11
}

# CoA classes do NOT get their own load tokens -- they alias onto base class
# tokens, and the mapping is not derivable from the class id (Runemaster is
# class 32 and loads as SPIRITMAGE). Read straight out of a client that had the
# class assigned by hand in the WA UI, so this is observed, not guessed.
#
# The load shape is `class.single`, NOT `class.multi`:
#     ["load"] = {
#         ["use_class"] = true,
#         ["class"] = { ["single"] = "SPIRITMAGE", ["multi"] = {} },
#     }
#
# Every class pack needs its own token captured the same way -- see
# resources/class-tokens.md for all 21. The mapping is arbitrary and NOT
# derivable from the class name or id (Venomancer is PROPHET, Templar is MONK,
# Runemaster is SPIRITMAGE). Never guess one.
#
# Confirmed working in game 2026-07-28: with use_class set on every leaf the
# pack no longer loads on other classes at all. An earlier test suggested it
# was inert -- that was a stale SavedVariables state, not the condition.
CLASS_TOKEN = CLS.token


def apply_leaf_gates():
    """Gate every leaf on class, and on spec where one applies.

                          all-specs pack      per-spec pack
        Core leaves       class               class + that spec
        Spec leaves       class + own spec    class + own spec

    EVERY leaf carries a class gate. Spec leaves additionally carry the spell
    only their spec knows.

                          all-specs pack           per-spec pack
        Core leaves       class                    class + that spec's spell
        Spec leaves       class + own spec spell   class + own spec spell

    Core is class-only in the all-specs pack on purpose. Engravings and
    etchings apply to the whole class, so spec-gating them there would hide
    them on two specs out of three. Only the spec-scoped build narrows Core to
    a single spec.

    Core is deliberately NOT gated on a class-wide spell either. That was tried
    (Primordial Blast, shared by all three specs) and it is wrong for a
    LEVELLING character: someone who has not learned it yet would lose the
    "you forgot your weapon engraving" reminder, which is exactly the player
    who needs it most. The class gate has no such hole.

    Before this, Core leaves had no load condition at all, so the two reminder
    displays -- inverse-triggered, firing when something is MISSING -- rendered
    permanently on any character that could never satisfy them. That shipped in
    final8 and is what this fixes.

    Two earlier attempts failed:
      * a trigger on the parent group -- inert, WeakAuras never registers a
        group with the trigger system, so all three specs rendered at once;
      * a `CoA Aura - Runemaster - <Spec>` aura (887088/9/90) as an extra
        trigger -- those spell entries exist in the database but are NOT active
        buffs on the player, so with disjunctive="all" every gated display
        vanished.
    `use_spellknown` is used by a working community aura on this exact client.
    """
    by = {c["id"]: c for c in children}

    def owning_spec(node):
        """Which spec this leaf belongs to, or None for Core.

        Reads the tag merge_bands() left rather than walking up to a
        `RM <Spec>` parent: after the merge the bands are shared, so the parent
        chain no longer identifies a spec.
        """
        specs = LEAF_SPECS.get(node["id"])
        if not specs:
            return None
        return next(iter(specs)) if len(specs) == 1 else None

    gated = anyof = classed = 0
    for c in children:
        if c.get("controlledChildren"):
            continue
        trigs = c["triggers"]
        own = [trigs[i]["trigger"] for i in sorted(i for i in trigs
                                                   if isinstance(i, int))]
        # "any of these spotted it" is the intent for a proc-glow icon, where
        # extra triggers are alternative ways to notice the same thing. It is
        # exactly WRONG for a display whose extra trigger is a GATE: with
        # "any", the always-true cooldown trigger satisfies the display on its
        # own and the gate does nothing.
        #
        # That shipped: all five Ripple variants rendered side by side, an
        # eight-icon main row, because this line overwrote the "all" they were
        # built with. NEEDS_ALL is why the exception is explicit rather than
        # inferred -- the two intents are indistinguishable from the trigger
        # list alone.
        if len(own) > 1 and c["id"] not in NEEDS_ALL:
            c["triggers"] = B._trigger_wrap(own, -10, "any")
            anyof += 1

        # class gate: EVERY leaf, no exceptions. This is the load-bearing one.
        c["load"]["use_class"] = True
        c["load"]["class"]["single"] = CLASS_TOKEN
        classed += 1

        # spec gate: spec leaves always; Core inherits only in a per-spec build
        spec = owning_spec(c) or SPEC_TITLE
        if spec:
            c["load"]["use_spellknown"] = True
            c["load"]["spellknown"] = SPEC_KNOWN[spec]
            gated += 1
        elif LEAF_SPECS.get(c["id"]) == set(SPEC_NAMES):
            # Shared by all three specs, so no single signature spell can gate
            # it. Cooldown icons gate on their OWN spell -- exact, and it stops
            # a levelling character seeing an ability they cannot cast yet.
            # Buff icons cannot: a buff id is not a spell IsSpellKnown knows.
            # They do not need it either, being active-only and therefore
            # self-gating -- the display cannot appear unless the buff is up.
            own_id = _leaf_spell(c) if not c["id"].startswith("CM Buffs ") else None
            # A ranked or component id cannot gate. Leaving the leaf on the
            # class gate alone shows it on all three specs, which is right:
            # every spec HAS the ability, we just cannot express "knows any
            # rank of it" in a single spellknown id.
            if own_id and not gateable(own_id):
                own_id = None
            if own_id:
                c["load"]["use_spellknown"] = True
                c["load"]["spellknown"] = own_id
                gated += 1
    return gated, anyof, classed


def assert_gated():
    """A leaf without a class gate is a bug, not a style choice.

    Cheap enough to run every build, and it is the only thing standing between
    us and shipping another pack that loads on all 21 classes.
    """
    bad_class, bad_known, bad_share = [], [], []
    sigs = set(SPEC_KNOWN.values())
    for c in children:
        if c.get("controlledChildren"):
            continue
        load = c.get("load", {})
        if not load.get("use_class") or \
                load.get("class", {}).get("single") != CLASS_TOKEN:
            bad_class.append(c["id"])
        # a spec-scoped pack must additionally narrow every leaf to that spec,
        # Core included -- otherwise the Riftblade-only pack's alerts show up
        # while you are playing Glyphic.
        if SPEC_ONLY and (not load.get("use_spellknown")
                          or not load.get("spellknown")):
            bad_known.append(c["id"])

        # A leaf may only drop the signature-spell gate -- by carrying no spec
        # gate, or its own spell id instead -- if EVERY spec has the ability.
        # Otherwise it loads on specs that cannot cast it. This is the one
        # failure the merge can introduce that comparing built packs cannot
        # see: tests/run.py check 11 compares two outputs of this same builder,
        # so a bug here moves both sides together and cancels out. It has to be
        # caught where the spec membership actually exists, which is here.
        specs = LEAF_SPECS.get(c["id"])
        if specs is not None and len(specs) < len(SPEC_NAMES):
            sk = load.get("spellknown") if load.get("use_spellknown") else None
            if sk not in sigs:
                bad_share.append(f"{c['id']} (specs={sorted(specs)}, "
                                 f"spellknown={sk})")
    if bad_class or bad_known or bad_share:
        for i in bad_class:
            print(f"  NO CLASS GATE:     {i}")
        for i in bad_known:
            print(f"  NO SPEC GATE:       {i}")
        for i in bad_share:
            print(f"  SHARED BUT NOT ON EVERY SPEC: {i}")
        raise SystemExit(
            f"refusing to emit: {len(bad_class)} leaves without a class gate, "
            f"{len(bad_known)} without a spec gate, "
            f"{len(bad_share)} shared without being on every spec")


_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()

def restrict_to_spec():
    """Drop every display that does not belong to Core or the chosen spec.

    Post-merge the shared bands hold all three specs, so membership comes from
    the LEAF_SPECS tag rather than from which `RM <Spec>` group a display sits
    under. Groups are kept if anything survives inside them, then emptied
    groups are pruned -- which is what removes the merged bands from a per-spec
    build if that spec happened to contribute nothing to one.
    """
    by = {c["id"]: c for c in children}
    keep_roots = {"CM Core", f"CM {SPEC_TITLE}"}

    def kept(node):
        specs = LEAF_SPECS.get(node["id"])
        if specs is not None:
            return SPEC_TITLE in specs
        seen = set()
        while node is not None:
            if node["id"] in keep_roots:
                return True
            pid = node.get("parent")
            if pid is None or pid in seen:
                return False
            seen.add(pid)
            node = by.get(pid)
        return False

    leaves = [c for c in children if not c.get("controlledChildren")]
    keep = {c["id"] for c in leaves if kept(c)}

    # keep a group iff something under it survived
    changed = True
    while changed:
        changed = False
        for c in children:
            cc = c.get("controlledChildren")
            if cc is None:
                continue
            kids = list(cc.values()) if isinstance(cc, dict) else list(cc)
            if any(k in keep for k in kids) and c["id"] not in keep:
                keep.add(c["id"])
                changed = True

    children[:] = [c for c in children if c["id"] in keep]
    for c in children:
        cc = c.get("controlledChildren")
        if cc is None:
            continue
        kids = list(cc.values()) if isinstance(cc, dict) else list(cc)
        c["controlledChildren"] = B.arr([k for k in kids if k in keep])
    root["controlledChildren"] = B.arr([r for r in TOP if r in keep])


def anchor_below(band_id, above_id, gap=4):
    """Hang `band_id` off the BOTTOM of `above_id` instead of a fixed yOffset.

    WeakAuras anchors an aura to another aura's region with
        anchorFrameType = "SELECTFRAME"
        anchorFrameFrame = "WeakAuras:<display id>"
    which resolves through `Private.regions[name].region`
    (WeakAuras.lua:6066-6075). It is a first-class feature -- there is an
    explicit cycle guard for it at :2620 -- not a trick.

    This is what makes the ladder DYNAMIC. A dynamic group's Resize() calls
    self:SetHeight(height) from its real content, so a band that renders one
    row instead of two shrinks, and everything anchored beneath it follows up.
    Fixed yOffsets cannot do that: they reserve the planned depth whether or
    not the icons materialise, which is the hole you get when a character has
    not learned enough of a row to fill it.

    TOP-to-BOTTOM with a negative offset, so `gap` is the visible space between
    the two bands.
    """
    b = by_id_all()[band_id]
    b["anchorFrameType"] = "SELECTFRAME"
    b["anchorFrameFrame"] = f"WeakAuras:{above_id}"
    b["selfPoint"] = "TOP"
    b["anchorPoint"] = "BOTTOM"
    b["xOffset"] = 0
    b["yOffset"] = -gap


def by_id_all():
    return {c["id"]: c for c in children}


# Chain the cooldown ladder. Offense keeps its fixed anchor -- it is the one
# band whose position is genuinely a constant, sitting under the resource
# envelope -- and everything below hangs off the band above it.
for _sp in ([SPEC_TITLE] if SPEC_ONLY else SPEC_NAMES):
    _off, _util = f"CM {_sp} Offense", f"CM {_sp} Utility"
    _ids = by_id_all()
    if _off in _ids and _util in _ids:
        anchor_below(_util, _off, gap=CD_ROW_STEP - SZ_CD)
        # Long-term chains too, but ONLY in a per-spec pack. In the all-specs
        # pack it is one Core band and cannot anchor to three different Utility
        # bands, two of which are unloaded at any moment -- anchoring to an
        # absent region just postpones and falls back to the parent.
        if SPEC_ONLY and "CM Longterm" in _ids:
            anchor_below("CM Longterm", _util, gap=LONG_GAP)

# iconSource: 0 makes OUR displayIcon authoritative, -1 defers to the trigger's
# own state.icon (RegionTypes/Icon.lua UpdateIcon).
#
# Only take 0 where the art is a DELIBERATE choice -- a hand-written OVERRIDE.
# Everywhere else the client's own spell texture is the better source: it is
# what the player already recognises from their action bar, and it exists even
# when db.ascension.gg serves a questionmark for the spell. Setting 0 across
# the board replaced Hasten's real boot icon with a clock scraped from
# somewhere else.
for _c in children:
    if _c.get("regionType") != "icon":
        continue
    _name = next((n for n in OVERRIDE if _c["id"].endswith(" " + n)), None)
    _c["iconSource"] = 0 if (_name or _c["id"] in NEEDS_MANUAL_ICON) else -1

if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    s = B.export_string(root, children)
    name = f"chronomancer-{SPEC_ONLY}" if SPEC_ONLY else "chronomancer-all-specs"
    out = CLS.pack_path(name)
    open(out, "w").write(s)
    print(f"{len(children)} displays, {len(s)} chars -> {out}")
    # Repeated art in a row means an id resolved to the wrong texture -- two
    # identical icons side by side. Since the bands merged, a row also holds
    # the deliberately-duplicated abilities (one copy per spec), which share
    # art by definition and can never load together. Only flag leaves whose
    # spec sets OVERLAP, i.e. that could actually appear side by side.
    _dupes = []
    _NOART = set()
    for _g in children:
        if _g["regionType"] != "dynamicgroup":
            continue
        _kids = [k for k in children
                 if k.get("parent") == _g["id"] and isinstance(k.get("displayIcon"), str)]
        _byart = {}
        for _k in _kids:
            # A shared questionmark is MISSING ART, not a mis-resolved id --
            # a different failure with a different fix, reported separately
            # below. Folding it in here makes this check cry wolf on nine rows
            # and buries the two real collisions it exists to catch.
            if _k["displayIcon"].endswith("inv_misc_questionmark"):
                _NOART.add(_k["id"])
                continue
            _byart.setdefault(_k["displayIcon"], []).append(_k)
        for _art, _ks in _byart.items():
            if len(_ks) < 2:
                continue
            _clash = [k["id"] for k in _ks
                      for j in _ks
                      if k is not j
                      and (LEAF_SPECS.get(k["id"], set(SPEC_NAMES))
                           & LEAF_SPECS.get(j["id"], set(SPEC_NAMES)))]
            if _clash:
                _dupes.append((_g["id"], _art.split("\\")[-1],
                               sorted(set(_clash))))
    if _dupes:
        print(f"  DUPLICATE ART IN {len(_dupes)} ROW(S):")
        for _r, _a, _w in _dupes:
            print(f"    {_r}: {_a} <- {_w}")
    else:
        print("  no repeated icon art within any row")
    if _NOART:
        # Genuinely absent upstream: db.ascension.gg serves a questionmark on
        # these spells' own pages too, so this is not a scrape miss. Cosmetic,
        # and the fix is art sourced by hand into OVERRIDE.
        _names = sorted({i.split(" ", 2)[-1] for i in _NOART})
        print(f"  no art upstream ({len(_names)}): {', '.join(_names)}")
    print(f"  leaf gates: {_CLASSED} via load.class={CLASS_TOKEN}, "
          f"{_GATED} via load.spellknown, {_ANY} set to any-of")
    if UNRESOLVED:
        print(f"  UNRESOLVED ({len(UNRESOLVED)}): {UNRESOLVED}")
    else:
        print("  all tracked names resolved to spell ids")
