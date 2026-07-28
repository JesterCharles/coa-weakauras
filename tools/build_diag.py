"""Diagnostic ladder for the Ascension WA fork.

Four tiny packs, each adding exactly one of the features the full pack relies
on. Whichever one fails to appear after import identifies the culprit.
"""
import os

import wabuild as B
from wacodec import LuaTable

SP = os.path.dirname(os.path.abspath(__file__))
ICON = "Interface\\Icons\\spell_frost_frostbolt02"


def emit(name, root, kids):
    s = B.export_string(root, kids)
    open(os.path.join(SP, f"diag-{name}.txt"), "w").write(s)
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
