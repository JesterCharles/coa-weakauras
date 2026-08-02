"""Diagnostic ladder for the Ascension WA fork.

Four tiny packs, each adding exactly one of the features the full pack relies
on. Whichever one fails to appear after import identifies the culprit.

Pack 5 is a different shape: it does not test whether a feature works, it
reads back which cooldown condition variables this fork actually exposes.
"""
import os

import wabuild as B
from wacodec import LuaTable
from classes import build_path

SP = os.path.dirname(os.path.abspath(__file__))
ICON = "Interface\\Icons\\spell_frost_frostbolt02"


def emit(name, root, kids):
    s = B.export_string(root, kids)
    open(build_path("_diag", f"diag-{name}"), "w").write(s)
    print(f"diag-{name}.txt  {len(kids)} displays  {len(s)} chars")


# 1. Baseline: one always-on spell cooldown icon. No group, no conditions.
k = [B.icon("DIAG1 Icon", "DIAG1", [B.spell_cd_trigger("Frostbolt",
                                                       show_on="showAlways")],
            ICON, x=0, y=-140, size=44,
            subregions=[B.sub_background(),
                        B.sub_text("%p", size=14, anchor="INNER_BOTTOM"),
                        B.sub_border(color=(0.04, 0.04, 0.05, 1), size=2,
                                     offset=1, edge="Square Full White")])]
emit("1-baseline", B.group("DIAG1", None, ["DIAG1 Icon"]), k)

# 2. Baseline + the desaturate/alpha condition.
k = [B.icon("DIAG2 Icon", "DIAG2",
            [B.spell_cd_trigger("Frostbolt", show_on="showAlways"),
             B.spell_cd_trigger("Frostbolt", show_on="showOnCooldown")],
            ICON, x=0, y=-140, size=44,
            subregions=[B.sub_background(),
                        B.sub_text("%p", size=14, anchor="INNER_BOTTOM"),
                        B.sub_border(color=(0.04, 0.04, 0.05, 1), size=2,
                                     offset=1, edge="Square Full White")],
            conditions=[B.cond(
                B.T({"trigger": 2, "variable": "show", "value": 1}),
                [B.change("desaturate", True), B.change("alpha", 0.45)])])]
emit("2-condition", B.group("DIAG2", None, ["DIAG2 Icon"]), k)

# 3. Baseline + a mana bar (the unit/Power trigger).
k = [B.aurabar("DIAG3 Mana", "DIAG3", [B.power_trigger("player", 0)],
               x=0, y=-168, w=270, h=12, color=(0.3, 0.45, 0.95, 1.0),
               subregions=[B.sub_text("%p", size=10, anchor="INNER_RIGHT",
                                      x=-4, justify="RIGHT")])]
emit("3-manabar", B.group("DIAG3", None, ["DIAG3 Mana"]), k)

# 4. Baseline icon inside a group gated by a polled custom Lua trigger.
gate = B.T({
    "type": "custom", "custom_type": "status", "check": "update",
    "events": "PLAYER_ENTERING_WORLD",
    "custom": ("function()\n"
               "    -- always true: proves the gate mechanism itself works\n"
               "    return true\n"
               "end"),
    "unit": "player", "debuffType": "HELPFUL",
    "names": LuaTable(), "spellIds": LuaTable(),
    "auranames": LuaTable(), "auraspellids": LuaTable(),
    "subeventPrefix": "SPELL", "subeventSuffix": "_CAST_START",
})
inner = B.icon("DIAG4 Icon", "DIAG4 Gate",
               [B.spell_cd_trigger("Frostbolt", show_on="showAlways")],
               ICON, x=0, y=-140, size=44,
               subregions=[B.sub_background(),
                           B.sub_text("%p", size=14, anchor="INNER_BOTTOM"),
                           B.sub_border(color=(0.04, 0.04, 0.05, 1), size=2,
                                        offset=1, edge="Square Full White")])
g = B.group("DIAG4 Gate", "DIAG4", ["DIAG4 Icon"])
g["triggers"] = B._trigger_wrap([gate])
emit("4-gate", B.group("DIAG4", None, ["DIAG4 Gate"]), [g, inner])


# 5. Which cooldown condition variables does this fork actually expose?
#
# Five identical icons on one spell, differing ONLY in the single condition
# that recolours the border. Every icon carries the same trigger the real pack
# uses -- spell cooldown, showAlways, use_showgcd -- so what lights here is
# what would light in `cd_icon`.
#
# HOW TO READ IT. Import, then stand still and do two things:
#
#   (a) Cast a DIFFERENT, off-cooldown spell. The probe spell is not on
#       cooldown, only the global is running. Any border that lights during
#       this window is a variable that CANNOT distinguish the GCD.
#   (b) Cast the probe spell itself and watch its real cooldown drain. Any
#       border that stays dark here is a variable that does not see a real
#       cooldown at all, i.e. it is not exposed and WeakAuras silently
#       dropped the check.
#
# The verdict we are after: if ONCOOLDOWN stays dark in (a) and lights in
# (b), it is exact, and `GCD_FLOOR` in build_runemaster.py can go -- which
# hands Unleash Essences (2.5s) and Trap Runes (3.0s) their urgency tiers
# back. DURATION>3 is the incumbent heuristic and should behave that way by
# construction; it is here as the control. EXPIRE<5 is the final12 bug and
# SHOULD light on every global -- if it does not, the trigger is not
# reporting the GCD and the premise is wrong. GCDCOOLDOWN tests the claim
# that the variable is hidden on the prototype: a check WeakAuras drops
# leaves an empty condition, so it will light constantly or never, and
# either way it is unusable.
#
# WA_DIAG_SPELL overrides the probe spell. Use one the test character
# actually knows -- a name that does not resolve gives a permanently dark
# row and looks like five failures.
#
# Runic Brand (12s, glyphic + engravement) is the default because it has no
# charges. A charge ability reports the RECHARGE duration and stays "not on
# cooldown" while a charge is banked, so onCooldown and duration both answer
# a different question than the one being asked -- which rules out Zenith
# despite it being the only cooldown all three specs share. On riftblade,
# override to a plain cooldown of its own.
PROBE = os.environ.get("WA_DIAG_SPELL", "Runic Brand")

PROBES = [
    ("ONCOOLDOWN", (0.30, 1.00, 0.40, 1),
     B.T({"trigger": 1, "variable": "onCooldown", "value": 1})),
    ("USABLE=0", (1.00, 0.30, 0.30, 1),
     B.T({"trigger": 1, "variable": "spellUsable", "value": 0})),
    ("DURATION>3", (0.40, 0.65, 1.00, 1),
     B.T({"trigger": 1, "variable": "duration", "op": ">", "value": "3"})),
    ("EXPIRE<5", (1.00, 0.60, 0.15, 1),
     B.T({"trigger": 1, "variable": "expirationTime", "op": "<",
          "value": "5"})),
    ("GCDCOOLDOWN=0", (1.00, 1.00, 1.00, 1),
     B.T({"trigger": 1, "variable": "gcdCooldown", "value": 0})),
]

kids = []
# Centred row: five 44px icons on a 90px pitch, so the middle one sits on 0.
for i, (label, colour, check) in enumerate(PROBES):
    did = f"DIAG5 {label}"
    kids.append(B.icon(
        did, "DIAG5",
        [B.spell_cd_trigger(PROBE, show_on="showAlways", show_gcd=True)],
        ICON, x=(i - 2) * 90, y=-140, size=44,
        subregions=[
            B.sub_background(),
            # %p is the trigger's own progress readout. Watching the number
            # tells you whether the trigger is tracking the GCD or the real
            # cooldown at the moment a border lights.
            B.sub_text("%p", size=14, anchor="INNER_BOTTOM"),
            B.sub_text(label, size=9, anchor="OUTER_BOTTOM", y=-2),
            # Dark by default, bright when the probe fires. Border rather than
            # glow: a glow bleeds into its neighbours at this spacing.
            B.sub_border(color=(0.10, 0.10, 0.12, 1), size=2, offset=1,
                         edge="Square Full White"),
        ],
        conditions=[B.cond(check, [B.change("sub.4.border_color",
                                            B.rgba(*colour))])]))

emit("5-cdvars", B.group("DIAG5", None, [k["id"] for k in kids]), kids)


# 6. Spell Known: does it span RANKS, and does it go false for an untalented
#    ability? Both questions gate per-ability load gating for the whole project.
#
# WHY IT MATTERS. Every leaf today gates on its SPEC's signature spell, so an
# Artificer sees every Artificer icon whether or not they talented it -- the
# pack is a spellbook dump, not a rotation display. Gating each leaf on its OWN
# spell would fix that, except `load.use_spellknown` holds one id and
# IsSpellKnown is EXACT: against a ranked spell's rank-1 id it is false for a
# level-60 character who holds rank 6, and the display vanishes with no error
# anywhere. That already shipped once (Gravity Bomb, Unearth, Time Out!,
# Fortify Timeline). 27 of Chronomancer's 117 spell leaves are ranked, so the
# id route reaches 16 of them and is not worth having.
#
# Matching by NAME should span ranks. SHOULD -- the only Spell Known trigger
# witnessed on this fork is Templar's, which passes an ID with exact=False, and
# the by-name case is witnessed nowhere. Guessing it costs invisible abilities
# no test can catch, so it gets probed instead.
#
# READ THE SCREENSHOT LEFT TO RIGHT. A cell is LIT when its condition is true.
# Run it on a level-60 Chronomancer.
#
#   name-any    "Accelerated Recovery" by name, exact=False
#   name-exact  same, exact=True         -- LIT means by-name spans ranks
#   id-rank1    id 800857 (RANK 1)       -- DARK is the expected result and is
#                                           the whole reason for this pack
#   ctrl-known  "Ripple", unranked       -- LIT, or the trigger itself is broken
#   ctrl-absent "Maw of Chaos" (Infinite)-- DARK on Artificer/Time
#   load-rank1  LOAD-gated on id 800857  -- the cell is ABSENT, not dark, if
#                                           load.spellknown rejects the rank
#
# Outcomes: name-any or name-exact lit + id-rank1 dark  -> gate by name, and
# 23 duplicated leaves collapse with it. Both name cells dark -> by-name does
# not span ranks here; keep the spec signature and pick an example build for
# the site preview instead.
RANKED_NAME = "Accelerated Recovery"
RANKED_RANK1_ID = 800857          # rank 1's id; a 60 holds a much higher rank
CTRL_KNOWN = "Ripple"             # unranked, the Time signature
CTRL_ABSENT = "Maw of Chaos"      # Infinite's signature

PROBES6 = [
    ("name-any", B.spell_known_trigger(RANKED_NAME, exact=False), False),
    ("name-exact", B.spell_known_trigger(RANKED_NAME, exact=True), False),
    ("id-rank1", B.spell_known_trigger(RANKED_RANK1_ID, exact=True), False),
    ("ctrl-known", B.spell_known_trigger(CTRL_KNOWN, exact=False), False),
    ("ctrl-absent", B.spell_known_trigger(CTRL_ABSENT, exact=False), False),
    ("load-rank1", None, True),
]

kids = []
for i, (label, trig, load_gated) in enumerate(PROBES6):
    did = f"DIAG6 {label}"
    # Always-on cooldown trigger so the cell is ON SCREEN regardless; the probe
    # is trigger 2 and only drives the border. A cell that vanishes entirely
    # therefore means LOAD rejected it, which is a different answer from dark.
    trigs = [B.spell_cd_trigger(CTRL_KNOWN, show_on="showAlways")]
    if trig is not None:
        trigs.append(trig)
    c = B.icon(
        did, "DIAG6", trigs, ICON,
        x=(i - 2) * 90, y=-140, size=44,
        subregions=[
            B.sub_background(),
            B.sub_text(label, size=9, anchor="OUTER_BOTTOM", y=-2),
            B.sub_border(color=(0.10, 0.10, 0.12, 1), size=2, offset=1,
                         edge="Square Full White"),
        ],
        conditions=([B.cond(B.T({"trigger": 2, "variable": "show", "value": 1}),
                            [B.change("sub.3.border_color",
                                      B.rgba(0.35, 0.95, 0.45, 1))])]
                    if trig is not None else None))
    # disjunctive "any" HERE, deliberately, and it is the opposite of what the
    # real pack wants. A gate uses "all" so a false probe HIDES the display --
    # but then "probe was false" and "load rejected the id" both render as an
    # absent cell, and this pack exists precisely to tell those two apart. So
    # the always-on cooldown trigger keeps every cell on screen and the probe
    # only drives the border: LIT = true, DARK = false, ABSENT = load refused.
    if trig is not None:
        c["triggers"] = B._trigger_wrap(trigs, -10, "any")
    if load_gated:
        c["load"]["use_spellknown"] = True
        c["load"]["spellknown"] = RANKED_RANK1_ID
    kids.append(c)

emit("6-spellknown", B.group("DIAG6", None, [k["id"] for k in kids]), kids)


# 7. Which aura carries Pyromancer's Ember COUNT, and does Heat stack 0-100?
#
# The scrape says Heat is a stacking aura -- "Each stack of Heat now increases
# the damage dealt by Dragon Leap by 3%" (Blessing of the Firelands, 504397) --
# and that at 100 Heat you gain an Ember and the bar empties. What it does NOT
# say is which id holds the EMBER count, and four ids are plausible:
#
#     807389  Heat            "Heating up! At 100 Heat you will generate..."
#     572806  Ember           rank "Generate Ember" -- may be the event, not
#                             the counter
#     807534  Ember Trigger   "Allows you to cast powerful abilities"
#     807536  Ember Consume   same tooltip, so one of the two is the state
#     805860  Fully Heated    no tooltip at all -- possibly the at-cap flag
#
# Guessing costs an import cycle and, worse, a resource bar that reads as
# working while showing the wrong number. So: one cell per candidate, each
# showing its own stack count, always visible.
#
# HOW TO READ IT. Import, then play a Pyromancer for ~30 seconds.
#   * the cell whose number climbs 1..5 and drops when you spend is the EMBER
#     counter -> that id goes in stack_bar()
#   * the cell that climbs toward 100 and resets is HEAT -> that id drives the
#     number-in-the-slot and the overcap glow thresholds
#   * a cell stuck at 0 with a lit border is an aura you HAVE with no stacks
#   * a DARK border means the aura is not on you at all
#
# `own_only=False` deliberately: a server-applied resource aura is not always
# flagged as cast by the player, and filtering it out here would look exactly
# like "this id is wrong".
PYRO_RES = [(807389, "Heat 807389"), (572806, "Ember 572806"),
            (807534, "EmberTrig 807534"), (807536, "EmberCons 807536"),
            (805860, "FullyHeated 805860")]
kids = []
for i, (aid, label) in enumerate(PYRO_RES):
    did = f"DIAG7 {aid}"
    kids.append(B.icon(
        did, "DIAG7",
        [B.health_trigger(), B.aura_trigger([str(aid)], own_only=False)],
        ICON, x=(i - 2) * 90, y=-140, size=44,
        subregions=[
            B.sub_background(),
            # %2.s is the STACK COUNT of trigger 2, the aura. Trigger 1's own
            # %s would be charges on the control spell, which is not the
            # question -- the same per-trigger form cd_icon uses for its
            # stack text.
            B.sub_text("%2.s", size=18, anchor="INNER_BOTTOM"),
            B.sub_text(label, size=9, anchor="OUTER_BOTTOM", y=-2),
            B.sub_border(color=(0.10, 0.10, 0.12, 1), size=2, offset=1,
                         edge="Square Full White"),
        ],
        conditions=[B.cond(
            B.T({"trigger": 2, "variable": "show", "value": 1}),
            [B.change("sub.4.border_color", B.rgba(0.35, 0.95, 0.45, 1))])]))
    # Unit Health as the always-on control, NOT a spell cooldown. diag-6 used
    # a known spell for that job, and every one of those is class-specific --
    # Ripple is Chronomancer's, so a Pyromancer importing this would see five
    # empty cells and read it as "none of these ids exist".
    kids[-1]["triggers"] = B._trigger_wrap(
        [B.health_trigger(), B.aura_trigger([str(aid)], own_only=False)],
        -10, "any")
    kids[-1][f"text_text_format_2.s_format"] = "none"

emit("7-pyro-resource", B.group("DIAG7", None, [k["id"] for k in kids]), kids)
