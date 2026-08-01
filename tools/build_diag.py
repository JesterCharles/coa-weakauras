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
