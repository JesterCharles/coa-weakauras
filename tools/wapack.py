"""The class-agnostic half of a CoA WeakAuras pack builder.

`build_<slug>.py` is now class CONTENT -- which abilities exist, which band
each one belongs in, what the resource envelope looks like. Everything that is
the same shape for every class lives here: id resolution, icon art, the widget
vocabulary (`cd_icon`, `buff_group`, `dot_bars`, ...), band merging, leaf
gating and the anchored ladder.

WHY THIS EXISTS
    Runemaster and Chronomancer were written as two standalone scripts. An AST
    comparison of the two found 16 top-level functions byte-identical once
    comments were stripped, three more above 90%, and the remaining nine
    differing by exactly three things: the id prefix ("RM " / "CM "), the class
    content inside `longterm_band`, and four places where Chronomancer had
    simply been improved and Runemaster never caught up.

    That third category is the cost being paid. The anchored ladder is the
    worked example: Chronomancer's bands hung off each other from the day they
    were written, Runemaster's shipped `anchorFrameType="SCREEN"` for two
    releases, and the fix had to be ported by hand. At 21 classes that is 21
    ports for one engine bug.

HOW A BUILDER USES IT
    import wapack as W
    W.init("chronomancer", version="1.2", prefix="CM", cd_per_row=7)
    from wapack import *              # noqa: F403  -- see below
    W.configure(charges={...}, proc_glow={...}, ...)

    The star import is deliberate and the order matters. Engine functions
    resolve their globals in THIS module at call time, so importing them early
    is safe; the scalars (`ROOT`, `SPEC_TITLE`, `SPECS`, `children`) only exist
    once `init()` has run, which is why the star import follows it. Keeping the
    names unqualified is what let both builders move onto this engine with
    their assembly code textually unchanged, which is what made the port
    verifiable against the frozen fixtures.

CONVERGENCE FLAGS
    `init()` takes five keyword flags that all default to the Chronomancer
    behaviour, i.e. the one a new class should get. Runemaster passes the other
    value on each because it predates them:

        roles_from_inventory   read abilities-<slug>.md for roles and per-spec
                               ids, instead of hand-curated OFFENSIVE /
                               DEFENSIVE lists in the builder
        trust_spell_meta       let spell-meta-<slug>.json decide whether an id
                               is safe for load.use_spellknown and for an
                               exact-match cooldown trigger
        override_first         a hand-written OVERRIDE outranks a scrape
        balanced_rows          10 cooldowns at CD_PER_ROW=7 lay out 5+5, not
                               7+3
        icons                  "scrape": build the art table from the class's
                               own skills + exiles scrapes. "legacy": the
                               name-keyed icons.json Runemaster still uses.

    Every flag is a Runemaster behaviour change waiting to happen, NOT a
    permanent fork. Each one removed is its own release, its own fixture diff
    read line by line, and its own in-game pass. Do not add a sixth to work
    around a difference in a NEW class -- a new class starts on the defaults.

THE GATE
    tests/run.py check 1 rebuilds every class and compares the normalised tree
    against tests/fixtures/. This module was extracted with that check green on
    all 8 packs at every step. Any change here that moves a fixture is a
    behaviour change and needs the diff read, not a re-freeze.
"""
import json
import os
import re

import wabuild as B
from classes import get as _get_class, data, dest  # noqa: F401

SP = os.path.dirname(os.path.abspath(__file__))

# ---- layout ---------------------------------------------------------------
# Shared by every class. A class that wants a different value overrides it
# after init() -- but think hard first: these ARE the layout standard
# (notes/layout-standard.md), and a pack that picks its own numbers stops
# being recognisable as the same product.
Y_ALERT = -18       # missing-buff reminders, high and central
Y_PROCS = -60       # spec procs, short windows, active-only
# The target band sits in the one gap the ladder above the main row leaves.
# Reminders (-18, 38px) span +1..-37 and "on me" (-84, 36px) spans -66..-102,
# so a 28px band centred at -51 spans -37..-65 and fits exactly between them.
Y_TARGET = -51      # your HoTs / your DoTs on the CURRENT target
Y_BUFFS = -84       # single row: procs, running CDs, buffs, debuffs
Y_MAIN = -132       # main damage row
Y_BAR = -164        # stacked resource bar (shares the envelope below it)
BAR_H_STACKED = 14  #   its height
Y_SEG = -180        # segmented bar, directly beneath its resource bar
Y_BAR_SOLO = -170   # one resource: it is the whole envelope
BAR_H_SOLO = 24     #   so it gets the full height
CD_ROW_STEP = 30
SZ_CD = 26
SZ_ALERT = 38
SZ_BUFF = 36         # buff row -- larger so the timer is legible
Y_CDS = -202        # first cooldown row, one anchor for every spec
LONG_GAP = 16       # extra clearance between the last cooldown row and long-term
Y_DOTS = -311       # applied DoTs / debuffs, below the cooldown block
SZ_MAIN = 44
SZ_SMALL = 28
SZ_STATE = 28
GAP = 2             # tight, but enough that overlaid text does not collide
BAR_W = 270
BAR_H = BAR_H_SOLO   # default resource bar height
SEG_H = 10           # segment height (thin: it shares the envelope)
GLYPH_GAP = 2        # gap between segments
SOLID = "Interface\\ChatFrame\\ChatFrameBackground"
EDGE = "Square Full White"
DARK = (0.04, 0.04, 0.05, 1)

# Cooldown urgency. `expirationTime` with op "<" takes SECONDS REMAINING and
# is the variable the working community packs use for this (33 uses in the
# Templar pack), so the tiers are built on verified ground.
URGENCY = [(20, "timer"), (10, "glow"), (5, "pulse")]

# Icons per cooldown row before it wraps, wired to `gridWidth` on a
# grow="GRID" band.
#
# THIS IS PER-CLASS, derived from the NARROWEST main row in the pack, because
# every resource bar is width-locked to its own spec's main row and a cooldown
# row that overruns the narrowest one looks broken on that spec even if it fits
# the others. A row of w icons is `w*SZ_CD + (w-1)*GAP` = 28w - 2, and
# tools/rowwidths.py fails a built pack past 1.2x. Recompute it per class; do
# NOT copy a value across. Set by init().
CD_PER_ROW = 7

# ---- identity. All set by init(); declared here so the module reads as a
# whole and so a use before init() fails loudly rather than on a stale value.
CLS = None
VERSION = None
PFX = None           # id prefix: "CM", "RM"
SPEC_ONLY = None     # WA_SPEC -- build one spec instead of the all-specs pack
SPEC_TITLE = None
SPECS = ()
SPEC_NAMES = ()
CLASS_TOKEN = None
ROOT = None
TOP = []
root = None
children = []

# WA_GLOW=1 additionally glows main-row icons the moment they come off
# cooldown. Off by default: the main row is where you look anyway, so glowing
# it constantly spends the one cue that should mean "press this now".
GLOW = os.environ.get("WA_GLOW") == "1"

# ---- data. Loaded by init().
EXILES = {}
COOLDOWNS = {}
SPELL_META = {}
ICONS = {}
ID_META = {}
ABILITIES = {}
SPEC_IDS = {}
SPEC_TEXT = {}
IN_GAME = {}
ID_OVERRIDE = {}
VARIANTS = {}
OFF_GCD = set()
ELSEWHERE = set()
UNRESOLVED = []
LEAF_SPECS = {}

# ---- class config. Supplied by the builder through init()/configure().
OVERRIDE = {}        # name -> icon texture, hand-written, outranks the scrape
FALLBACK = {}        # name -> icon texture, used only when nothing resolved
ICON_GAP = {}        # spell id -> icon texture, for ids whose page has no art
CHARGES = {}         # name -> charge count
PROC_GLOW = {}       # ability -> the procs that say "press this now"
PROC_STACKS = set()  # of those, the ones whose proc also stacks
NEEDS_ALL = set()    # displays whose multiple triggers mean ALL, not ANY
SPEC_KNOWN = {}      # spec label -> signature spell id, the per-spec gate
CONTINUUM = []       # names that lead the offense row, in press order
NO_BUFF = set()      # offense names that apply no buff worth a buff-row icon
MERGE_BANDS = ("Main", "Buffs")

# ---- convergence flags. See the module docstring.
ROLES_FROM_INVENTORY = True
TRUST_SPELL_META = True
OVERRIDE_FIRST = True
BALANCED_ROWS = True

# `_bottom_rows` is replaceable because Runemaster still curates its rows by
# hand. Set through configure(bottom_rows=...); anything else uses the
# inventory-driven default below.
BOTTOM_ROWS = None


def init(slug, version, prefix, *, cd_per_row=None, spec_env="WA_SPEC",
         override=None, fallback=None, icon_gap=None, crosscheck=None,
         icons="scrape", id_meta_file=None, elsewhere=None,
         roles_from_inventory=True, trust_spell_meta=True,
         override_first=True, balanced_rows=True):
    """Load a class's data and stand up the pack skeleton.

    Everything after this point in a builder is content. `init` resolves
    identity from classes.py (never retyped -- the load token is not derivable
    from the class name), loads the scrapes, folds in the tooltip-verified id
    registry, and creates `root` / `children`.
    """
    global CLS, VERSION, PFX, SPEC_ONLY, SPEC_TITLE, SPECS, SPEC_NAMES
    global CLASS_TOKEN, ROOT, TOP, root, children
    global EXILES, COOLDOWNS, SPELL_META, ICONS, ID_META, ABILITIES, SPEC_IDS
    global SPEC_TEXT, IN_GAME, ID_OVERRIDE, VARIANTS, OFF_GCD, ELSEWHERE
    global OVERRIDE, FALLBACK, ICON_GAP, CD_PER_ROW
    global ROLES_FROM_INVENTORY, TRUST_SPELL_META, OVERRIDE_FIRST
    global BALANCED_ROWS

    CLS = _get_class(slug)
    VERSION = version
    PFX = prefix
    ROLES_FROM_INVENTORY = roles_from_inventory
    TRUST_SPELL_META = trust_spell_meta
    OVERRIDE_FIRST = override_first
    BALANCED_ROWS = balanced_rows
    if cd_per_row is not None:
        CD_PER_ROW = cd_per_row

    SPEC_ONLY = os.environ.get(spec_env, "").strip().lower() or None
    SPEC_TITLE = CLS.spec_label(SPEC_ONLY) if SPEC_ONLY in CLS.specs else None
    SPECS = tuple(CLS.specs)
    SPEC_NAMES = tuple(CLS.spec_label(sp) for sp in CLS.specs)
    CLASS_TOKEN = CLS.token

    OVERRIDE = dict(override or {})
    FALLBACK = dict(fallback or {})
    ICON_GAP = dict(icon_gap or {})

    EXILES = json.load(open(data(CLS.exiles)))
    COOLDOWNS = json.load(open(data(CLS.cooldowns)))
    OFF_GCD = {n for n, v in COOLDOWNS.items() if v.get("gcd") is False}

    # Art. "scrape" is the forward path: the class's own two scrapes, skills
    # first because it covers more names, exiles filling its gaps. "legacy" is
    # the name-keyed icons.json Runemaster was built on, which is keyed to ITS
    # spells and does not transfer.
    _QM = "inv_misc_questionmark"
    if icons == "scrape":
        ICONS = {n: v["icon"] for n, v in EXILES.items() if v.get("icon")}
        for _r in json.load(open(data(CLS.skills))):
            if _r.get("icon") and _r["icon"] != _QM:
                ICONS[_r["name"]] = _r["icon"]
            else:
                ICONS.setdefault(_r["name"], _QM)
    else:
        ICONS = json.load(open(data("icons.json")))

    # id -> art, so a corrected id corrects the art with it. Scraped per id by
    # tools/fetch_spell_icons.py, which resolves far more ids than the class's
    # own spell count because each db.ascension page also carries art for every
    # spell it cross-references.
    #
    # Two file shapes are in play and they are NOT interchangeable:
    # icon-meta-<slug>.json (fetch_spell_icons.py) maps id -> texture name,
    # while the older exiles-id-meta.json maps id -> {"icon": texture}. Reading
    # one as the other yields a dict where a string belongs and blows up in
    # ic(), which is at least loud -- but only because ic() concatenates. Wrap
    # on the shape the file actually has.
    _raw = json.load(open(data(id_meta_file or f"icon-meta-{CLS.slug}.json")))
    ID_META = {i: (a if isinstance(a, dict) else {"icon": a})
               for i, a in _raw.items()}
    if icons == "scrape":
        # The tree payload fills any gaps. EVERY id an entry lists, not just
        # its primary: an ability whose row names several ranks is one art.
        for _v in EXILES.values():
            if _v.get("icon"):
                for _i in _v.get("ids") or []:
                    ID_META.setdefault(str(_i), {"icon": _v["icon"]})

    SPELL_META = (json.load(open(data(f"spell-meta-{CLS.slug}.json")))
                  if trust_spell_meta else {})

    # The ability inventory: roles, per-spec ids, which specs have what.
    ABILITIES = _abilities() if roles_from_inventory else {}
    SPEC_IDS = {n: a["ids"] for n, a in ABILITIES.items() if a["ids"]}
    if elsewhere is not None:
        ELSEWHERE = set(elsewhere)
    else:
        ELSEWHERE = {n for n, a in ABILITIES.items()
                     if a["default"] in ("main", "resource", "longterm",
                                         "ignore", "buff", "target")}

    # Ground truth read off in-game tooltips. A screenshotted tooltip outranks
    # db.exil.es, db.ascension.gg, coabuildhub and Sidekick, and it feeds BOTH
    # the spell id and the icon.
    _verified = {k: v for k, v in
                 json.load(open(data("in-game-verified.json"))).items()
                 if not k.startswith("_")}
    IN_GAME = {k: v["id"] for k, v in _verified.items()}
    ID_OVERRIDE = {**(crosscheck or {}), **IN_GAME}
    # A talent can REPLACE an ability with a different spell id rather than
    # just modifying it -- Runelord swaps Zenith 712325 for 712389. An exact-id
    # trigger on the base then silently stops matching once you spec into the
    # talent. Every known id gets its own trigger, any-of.
    VARIANTS = {k: [v["id"]] + list(v.get("variants", []))
                for k, v in _verified.items()}

    # Which spec pages mention an ability. Read from resources/ and driven off
    # classes.py -- never from an out-of-repo path, or the build stops being
    # reproducible from a clean clone.
    SPEC_TEXT = {sp: open(data(CLS.sidekick(sp))).read() for sp in CLS.specs}

    B.set_salt(f"{CLS.slug}-{SPEC_ONLY or 'all'}-{VERSION}")
    ROOT = (f"{CLS.name} {SPEC_TITLE} [CoA] v{VERSION}" if SPEC_TITLE
            else f"{CLS.name} [CoA] v{VERSION}")
    children = []
    TOP = [f"{PFX} Core"] + [f"{PFX} {s}" for s in SPEC_NAMES]
    root = B.group(ROOT, None, TOP, x=0, y=0)
    root["url"] = ""
    return CLS


def configure(**kw):
    """Class content the engine reads. Called after init() because several of
    these are computed from data init() loads.

    Unknown keys are refused: a typo here is silent otherwise -- the engine
    keeps its empty default and the pack simply builds without the charge
    counts, or the proc glows, or the per-spec gates.
    """
    known = {"charges": "CHARGES", "proc_glow": "PROC_GLOW",
             "proc_stacks": "PROC_STACKS", "needs_all": "NEEDS_ALL",
             "spec_known": "SPEC_KNOWN", "continuum": "CONTINUUM",
             "no_buff": "NO_BUFF", "merge_bands": "MERGE_BANDS",
             "bottom_rows": "BOTTOM_ROWS", "override": "OVERRIDE",
             "fallback": "FALLBACK", "icon_gap": "ICON_GAP",
             "elsewhere": "ELSEWHERE"}
    bad = sorted(set(kw) - set(known))
    if bad:
        raise SystemExit(f"wapack.configure: unknown key(s) {bad}. "
                         f"Known: {', '.join(sorted(known))}")
    for k, v in kw.items():
        globals()[known[k]] = v


def cd_secs(text):
    m = re.match(r"([\d.]+)\s*(sec|min|hour)", text)
    return (float(m.group(1)) * {"sec": 1, "min": 60, "hour": 3600}[m.group(2)]
            if m else 1e9)


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

    With TRUST_SPELL_META off the answer is always yes, which is what a class
    built before spell-meta existed already does everywhere. That is a WEAKER
    guarantee, not a different one -- the flag exists so an unconverged class
    keeps its current output, not because trusting every id is defensible.
    """
    if not TRUST_SPELL_META:
        return True
    from spellmeta import is_castable
    return is_castable(SPELL_META.get(str(sid)))


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


def in_spec(name, spec_key):
    v = COOLDOWNS.get(name)
    if v:
        return spec_key in v["specs"] or not v["specs"]
    hits = [sp for sp, t in SPEC_TEXT.items() if name in t]
    return spec_key in hits or not hits


def spec_cooldowns(spec, lo, hi):
    """Ability names for one spec with a cooldown in [lo, hi), shortest first.
    An empty `specs` list means the ability is shared across all three."""
    got = [(n, cd_secs(v["cd"])) for n, v in COOLDOWNS.items()
           if (spec in v["specs"] or not v["specs"])
           and lo <= cd_secs(v["cd"]) < hi]
    return [n for n, _ in sorted(got, key=lambda x: x[1])]


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


def ic(name):
    # A hand-written OVERRIDE outranks everything. It is the only place a human
    # has stated intent -- usually to break a genuine art collision between two
    # abilities that share a texture upstream and CAN sit in a row together --
    # so a scrape must never win over it. (It used to: ID_META was consulted
    # first and OVERRIDE only reached when the id had no art, which quietly
    # made every override a no-op the moment the icon scrape improved.) A class
    # still on OVERRIDE_FIRST=False has that no-op behaviour and its overrides
    # are load-bearing only where the id resolved no art at all.
    if OVERRIDE_FIRST and name in OVERRIDE:
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


def triggers_of(display):
    """Pull the trigger list back out of a built display.

    Triggers are stored as a LuaTable of {trigger, untrigger} pairs under
    numeric keys, so re-wrapping one means unwrapping it first. Used to append
    a gate to an icon that cd_icon has already finished building.
    """
    tg = display.get("triggers") or {}
    return [tg[k]["trigger"] for k in sorted(k for k in tg if isinstance(k, int))]


def thin(size=2):
    return B.sub_border(color=DARK, size=size, offset=1, edge=EDGE)


def add(region):
    children.append(region)
    return region["id"]


def by_id_all():
    return {c["id"]: c for c in children}


def spec_group(id_, kids, trigger=None):
    """The per-spec container.

    Pass no trigger. Gating belongs on the LEAVES (apply_leaf_gates), because
    a merged band's children come from several specs and a gate on the
    container cannot express that. `trigger` exists only for Runemaster, which
    still gates at this level.
    """
    g = B.group(id_, ROOT, kids, x=0, y=0)
    if trigger is not None:
        g["triggers"] = B._trigger_wrap([trigger])
    return g


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


def emit_bottom_block(spec_name, spec_key, out, procs, state=()):
    """Three stacked rows under the resource bar:

        1. Offense   -- damage cooldowns
        2. Utility   -- defensives and utility merged
        3. Buffs     -- short-window procs, active-only

    Every spec starts at the same Y_CDS: the resource envelope above is a
    fixed height whatever a spec puts in it, so there is no per-spec offset to
    apply and no empty band left behind. Returns the y for the DoT row.
    """
    offense, utility = (BOTTOM_ROWS or _bottom_rows)(spec_key)

    y = Y_CDS

    for label, names in (("Offense", offense), ("Utility", utility)):
        ids = []
        for n in names:
            ids.append(add(cd_icon(f"{PFX} {spec_name} {label} {n}",
                                   f"{PFX} {spec_name} {label}", n, SZ_CD,
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
        _per = -(-len(ids) // _rows) if BALANCED_ROWS else CD_PER_ROW
        add(B.dynamicgroup(f"{PFX} {spec_name} {label}",
                           f"{PFX} {spec_name}", ids,
                           x=0, y=y, grow="GRID", space=GAP,
                           grid_width=_per, row_space=CD_ROW_STEP - SZ_CD))
        out.append(f"{PFX} {spec_name} {label}")
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
    # skipped here. NO_BUFF is class content -- configure(no_buff=...).
    cd_buffs = [(n, (1.0, 0.80, 0.30)) for n in offense
                if n not in named and n not in NO_BUFF]

    # ONE row for everything currently up: procs, running cooldowns, self
    # buffs and target debuffs. They are all active-only, so the row packs to
    # whatever is actually live rather than to its full length.
    out.append(buff_group(f"{PFX} {spec_name} Buffs", f"{PFX} {spec_name}",
                          procs + cd_buffs + list(state),
                          y=Y_BUFFS, size=SZ_BUFF, glow=True))
    return y


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
        groups = [(s, f"{PFX} {s} {band}") for s in SPEC_NAMES
                  if f"{PFX} {s} {band}" in by]
        if not groups:
            continue

        seqs, owners, leaf_of = [], {}, {}
        for spec, gid in groups:
            cc = by[gid]["controlledChildren"]
            kids = list(cc.values()) if isinstance(cc, dict) else list(cc)
            seq = []
            for cid in kids:
                ability = cid[len(f"{PFX} {spec} {band} "):]
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
                new_id = f"{PFX} {band} {ability}"
                leaf["id"] = new_id
                leaf["parent"] = f"{PFX} {band}"
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
                    by[cid]["parent"] = f"{PFX} {band}"
                    LEAF_SPECS[cid] = {s}
                    kids_out.append(cid)

        # Carry the template's grid settings through. A wrapped band that lost
        # them here would silently revert to one unbroken line -- the merge is
        # exactly where the per-spec band stops existing, so it is the last
        # place a dropped field is still recoverable.
        merged = B.dynamicgroup(f"{PFX} {band}", ROOT, kids_out,
                                x=template.get("xOffset", 0),
                                y=template.get("yOffset", 0),
                                grow=template.get("grow", "HORIZONTAL"),
                                space=template.get("space", GAP),
                                grid_width=template.get("gridWidth"),
                                grid_type=template.get("gridType", "HD"),
                                row_space=template.get("rowSpace", 4))
        children.append(merged)
        merged_ids.append(f"{PFX} {band}")
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
            if pid in (f"{PFX} {s}" for s in SPEC_NAMES):
                break
            nxt = by.get(pid, {}).get("parent")
            if nxt is None:
                break
            pid = nxt
        for s in SPEC_NAMES:
            if pid == f"{PFX} {s}":
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
             and c["id"] in (f"{PFX} {s}" for s in SPEC_NAMES)}
    children[:] = [c for c in children if c["id"] not in empty]

    TOP[:] = [t for t in TOP if t not in empty] + merged_ids
    root["controlledChildren"] = B.arr(TOP)


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
            own_id = (None if c["id"].startswith(f"{PFX} Buffs ")
                      else _leaf_spell(c))
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


def restrict_to_spec():
    """Drop every display that does not belong to Core or the chosen spec.

    Post-merge the shared bands hold all three specs, so membership comes from
    the LEAF_SPECS tag rather than from which `RM <Spec>` group a display sits
    under. Groups are kept if anything survives inside them, then emptied
    groups are pruned -- which is what removes the merged bands from a per-spec
    build if that spec happened to contribute nothing to one.
    """
    by = {c["id"]: c for c in children}
    keep_roots = {f"{PFX} Core", f"{PFX} {SPEC_TITLE}"}

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


def chain_ladder():
    """Hang each cooldown band off the one above it, per spec.

    Offense keeps the one genuinely fixed anchor -- it sits under the
    fixed-height resource envelope, so its position really is a constant --
    and Utility then hangs off Offense, Longterm off Utility.

    Long-term chains in the ALL-SPECS pack too, because it is one band per
    spec. The old restriction was real but was a symptom: a single Core band
    cannot anchor to three different Utility bands with two of them unloaded,
    so it was left on a fixed worst-case offset. Giving each spec its own band
    removes the choice entirely.
    """
    for sp in ([SPEC_TITLE] if SPEC_ONLY else SPEC_NAMES):
        have = by_id_all()
        prev = f"{PFX} {sp} Offense"
        for band, gap in ((f"{PFX} {sp} Utility", CD_ROW_STEP - SZ_CD),
                          (f"{PFX} {sp} Longterm", LONG_GAP)):
            if band in have and prev in have:
                anchor_below(band, prev, gap=gap)
                prev = band


def settle_icon_source(manual=()):
    """Decide, per icon, whether OUR art or the trigger's own art wins.

    iconSource 0 makes our displayIcon authoritative, -1 defers to the
    trigger's `state.icon` (RegionTypes/Icon.lua UpdateIcon).

    Only take 0 where the art is a DELIBERATE choice -- a hand-written
    OVERRIDE, or a display listed in `manual`. Everywhere else the client's own
    spell texture is the better source: it is what the player already
    recognises from their action bar, and it exists even when db.ascension.gg
    serves a questionmark. Setting 0 across the board replaced Hasten's real
    boot icon with a clock scraped from somewhere else.
    """
    for c in children:
        if c.get("regionType") != "icon":
            continue
        name = next((n for n in OVERRIDE if c["id"].endswith(" " + n)), None)
        c["iconSource"] = 0 if (name or c["id"] in manual) else -1


def finish(gates):
    """Write the pack and print the build report.

    `gates` is the (gated, anyof, classed) triple apply_leaf_gates() returned.
    Everything printed here is a check that has caught a real bug at least
    once; none of it changes the pack.
    """
    s = B.export_string(root, children)
    name = f"{CLS.slug}-{SPEC_ONLY}" if SPEC_ONLY else f"{CLS.slug}-all-specs"
    out = CLS.pack_path(name)
    open(out, "w").write(s)
    print(f"{len(children)} displays, {len(s)} chars -> {out}")

    # Repeated art in a row means an id resolved to the wrong texture -- two
    # identical icons side by side. Since the bands merged, a row also holds
    # the deliberately-duplicated abilities (one copy per spec), which share
    # art by definition and can never load together. Only flag leaves whose
    # spec sets OVERLAP, i.e. that could actually appear side by side.
    dupes = []
    noart = set()
    for g in children:
        if g["regionType"] != "dynamicgroup":
            continue
        kids = [k for k in children
                if k.get("parent") == g["id"]
                and isinstance(k.get("displayIcon"), str)]
        byart = {}
        for k in kids:
            # A shared questionmark is MISSING ART, not a mis-resolved id -- a
            # different failure with a different fix, reported separately
            # below. Folding it in here makes this check cry wolf on nine rows
            # and buries the two real collisions it exists to catch.
            if k["displayIcon"].endswith("inv_misc_questionmark"):
                noart.add(k["id"])
                continue
            byart.setdefault(k["displayIcon"], []).append(k)
        for art, ks in byart.items():
            if len(ks) < 2:
                continue
            clash = [k["id"] for k in ks
                     for j in ks
                     if k is not j
                     and (LEAF_SPECS.get(k["id"], set(SPEC_NAMES))
                          & LEAF_SPECS.get(j["id"], set(SPEC_NAMES)))]
            if clash:
                dupes.append((g["id"], art.split("\\")[-1], sorted(set(clash))))
    if dupes:
        print(f"  DUPLICATE ART IN {len(dupes)} ROW(S):")
        for r, a, w in dupes:
            print(f"    {r}: {a} <- {w}")
    else:
        print("  no repeated icon art within any row")
    if noart:
        # Genuinely absent upstream: db.ascension.gg serves a questionmark on
        # these spells' own pages too, so this is not a scrape miss. Cosmetic,
        # and the fix is art sourced by hand into OVERRIDE.
        names = sorted({i.split(" ", 2)[-1] for i in noart})
        print(f"  no art upstream ({len(names)}): {', '.join(names)}")

    gated, anyof, classed = gates
    print(f"  leaf gates: {classed} via load.class={CLASS_TOKEN}, "
          f"{gated} via load.spellknown, {anyof} set to any-of")
    if UNRESOLVED:
        print(f"  UNRESOLVED ({len(UNRESOLVED)}): {UNRESOLVED}")
    else:
        print("  all tracked names resolved to spell ids")
    return out
