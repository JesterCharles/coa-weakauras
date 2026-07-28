"""Builder for Ascension CoA WeakAuras.

Region defaults are harvested from working community auras (tocversion 30300,
internalVersion 89.5) so the emitted tables match what the client itself writes.
"""
import hashlib

from wacodec import LuaTable, wa_encode

TOC = 30300
IV = 89.5
SEMVER = "1.0.0"

_UID_ALPHA = ("abcdefghijklmnopqrstuvwxyz"
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


# Salt mixed into every uid. WeakAuras dedupes imports on `uid`: with a fixed
# salt, a rebuilt pack carries the SAME uids as the copy already installed, so
# WA treats it as already-imported and the user sees no change no matter how
# many times they import. Bumping this makes a build genuinely new.
UID_SALT = "v1"


def set_salt(salt):
    global UID_SALT
    UID_SALT = salt


def uid(seed):
    """Deterministic 11-char uid, namespaced by UID_SALT."""
    h = hashlib.sha256((UID_SALT + "|" + seed).encode()).digest()
    return "".join(_UID_ALPHA[b % len(_UID_ALPHA)] for b in h[:11])


def T(d):
    t = LuaTable()
    for k, v in d.items():
        t[k] = v
    return t


def arr(items):
    t = LuaTable()
    for i, v in enumerate(items):
        t[i + 1] = v
    return t


def rgba(r, g, b, a=1.0):
    return T({1: r, 2: g, 3: b, 4: a})


# ------------------------------------------------------------------ triggers
def _trigger_wrap(triggers, mode=-10, disjunctive=None, custom_logic=None):
    """`disjunctive` defaults to "all" in WeakAuras when unset -- every trigger
    must be active. Multi-trigger displays that mean "any of these" MUST say so
    explicitly; working community packs set it on every such aura."""
    t = LuaTable()
    for i, tr in enumerate(triggers):
        t[i + 1] = T({"trigger": tr, "untrigger": LuaTable()})
    t["activeTriggerMode"] = mode
    if disjunctive:
        t["disjunctive"] = disjunctive
    if custom_logic:
        t["customTriggerLogic"] = custom_logic
    return t


def aura_trigger(names, unit="player", helpful=True, stacks=None,
                 stacks_op=">=", own_only=True, match_count=None,
                 show_on=None):
    """Aura (aura2) trigger matched by NAME. `names` may hold names or id-strings."""
    tr = T({
        "type": "aura2",
        "event": "Health",
        "unit": unit,
        "debuffType": "HELPFUL" if helpful else "HARMFUL",
        "useName": True,
        "auranames": arr([str(n) for n in names]),
        "names": LuaTable(),
        "spellIds": LuaTable(),
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
        "useStacks": stacks is not None,
        "stacks": str(stacks) if stacks is not None else "1",
        "stacksOperator": stacks_op,
    })
    if show_on:
        # "showOnMissing" fires when NONE of `names` is present -- the basis
        # for a "you forgot this buff" reminder
        tr["matchesShowOn"] = show_on
    if own_only:
        tr["ownOnly"] = True
    if match_count is not None:
        tr["useMatch_count"] = True
        tr["match_count"] = str(match_count)
        tr["match_countOperator"] = ">="
    return tr


def spell_cd_trigger(spell, show_on="showOnCooldown", exact=False,
                     show_gcd=True):
    """Cooldown Progress (Spell). `spell` may be a name string or numeric id.

    `show_gcd` sets `use_showgcd`, which makes the trigger report the global
    cooldown when the ability itself is not on cooldown -- so the icon sweeps
    for the ~1.5s you cannot press anything, and you can see whether it is
    worth holding a cast. Verified: the Templar community pack sets it on 49
    of its spell cooldown triggers.

    Callers that pair this with `show_on="showOnCooldown"` should pass
    `show_gcd=False`; otherwise the display pops into existence on every GCD.
    """
    return T({
        "type": "spell",
        "event": "Cooldown Progress (Spell)",
        "unit": "player",
        "debuffType": "HELPFUL",
        "use_spellName": True,
        "spellName": spell,
        "use_exact_spellName": bool(exact),
        "use_showgcd": bool(show_gcd),
        "use_genericShowOn": True,
        "genericShowOn": show_on,
        "use_track": True,
        "names": LuaTable(),
        "spellIds": LuaTable(),
        "auraspellids": LuaTable(),
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
    })


def enchant_trigger(enchant, weapon="main", show_on="showOnActive"):
    """Weapon Enchant trigger, matched by enchant NAME (Weapon Engravings)."""
    return T({
        "type": "item",
        "event": "Weapon Enchant",
        "unit": "player",
        "debuffType": "HELPFUL",
        "use_enchant": True,
        "enchant": enchant,
        "use_itemName": True,
        "use_weapon": True,
        "weapon": weapon,
        "use_showOn": True,
        "showOn": show_on,
        "use_genericShowOn": True,
        "genericShowOn": "showOnCooldown",
        "names": LuaTable(),
        "spellIds": LuaTable(),
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
    })


def health_trigger(unit="player"):
    """Unit Health -- always active, so it can hold an always-on display."""
    return T({
        "type": "unit",
        "event": "Health",
        "unit": unit,
        "debuffType": "HELPFUL",
        "names": LuaTable(),
        "spellIds": LuaTable(),
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
    })


def slot_cd_trigger(slot, show_on="showAlways"):
    """Cooldown Progress (Slot) -- equipment slot. 13/14 are the trinkets."""
    return T({
        "type": "item",
        "event": "Cooldown Progress (Slot)",
        "unit": "player",
        "debuffType": "HELPFUL",
        "use_itemSlot": True,
        "itemSlot": slot,
        "use_genericShowOn": True,
        "genericShowOn": show_on,
        "names": LuaTable(),
        "spellIds": LuaTable(),
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
    })


def power_trigger(unit="player", power_type=0):
    return T({
        "type": "unit",
        "event": "Power",
        "unit": unit,
        "debuffType": "HELPFUL",
        "use_powertype": True,
        "powertype": power_type,
        "use_showCost": False,
        "names": LuaTable(),
        "spellIds": LuaTable(),
        "subeventPrefix": "SPELL",
        "subeventSuffix": "_CAST_START",
    })


# --------------------------------------------------------------- sub regions
def sub_background():
    return T({"type": "subbackground"})


def sub_border(color=(0.58, 0.76, 1.0, 1.0), size=12, offset=6, visible=True,
               edge="Blizzard Dialog"):
    """`edge="Square Full White"` with a dark colour gives the thin, flat outline
    used by compact rotation packs, rather than a chunky Blizzard frame."""
    return T({
        "type": "subborder",
        "border_visible": visible,
        "border_edge": edge,
        "border_color": rgba(*color),
        "border_size": size,
        "border_offset": offset,
    })


def sub_glow(enabled=False, glow_type="buttonOverlay", color=(1, 1, 1, 1)):
    return T({
        "type": "subglow",
        "glow": enabled,
        "glowType": glow_type,
        "useGlowColor": color != (1, 1, 1, 1),
        "glowColor": rgba(*color),
        "glowLines": 8,
        "glowFrequency": 0.25,
        "glowLength": 10,
        "glowThickness": 1,
        "glowScale": 1,
        "glowBorder": False,
        "glowXOffset": 0,
        "glowYOffset": 0,
        "glowDuration": 1,
    })


def sub_text(text="%s", size=12, anchor="INNER_BOTTOMRIGHT", visible=True,
             color=(1, 1, 1, 1), justify="CENTER", x=0, y=0):
    return T({
        "type": "subtext",
        "text_text": text,
        "text_visible": visible,
        "text_color": rgba(*color),
        "text_font": "Friz Quadrata TT",
        "text_fontSize": size,
        "text_fontType": "OUTLINE",
        "text_justify": justify,
        "text_selfPoint": "AUTO",
        "text_anchorPoint": anchor,
        "anchor_point": anchor,
        "anchorXOffset": x,
        "anchorYOffset": y,
        "text_shadowColor": rgba(0, 0, 0, 1),
        "text_shadowXOffset": 0,
        "text_shadowYOffset": 0,
        "text_automaticWidth": "Auto",
        "text_fixedWidth": 64,
        "text_wordWrap": "WordWrap",
        "text_text_format_s_format": "none",
        "rotateText": "NONE",
    })


# ------------------------------------------------------------------- regions
def _common(id_, parent, x, y, subregions, triggers, conditions):
    return {
        "id": id_,
        "uid": uid(id_),
        "parent": parent,
        "xOffset": x,
        "yOffset": y,
        "anchorPoint": "CENTER",
        "selfPoint": "CENTER",
        "anchorFrameType": "SCREEN",
        "frameStrata": 1,
        "alpha": 1,
        "version": 1,
        "semver": SEMVER,
        "internalVersion": IV,
        "tocversion": TOC,
        "subRegions": arr(subregions or []),
        "triggers": _trigger_wrap(triggers),
        "conditions": arr(conditions or []),
        "load": T({
            "use_never": False,
            "class": T({"multi": LuaTable()}),
            "spec": T({"multi": LuaTable()}),
            "size": T({"multi": LuaTable()}),
            "talent": T({"multi": LuaTable()}),
        }),
        "actions": T({"start": LuaTable(), "finish": LuaTable(),
                      "init": LuaTable()}),
        "animation": T({
            "start": T({"type": "none", "duration_type": "seconds",
                        "easeType": "none", "easeStrength": 3}),
            "main": T({"type": "none", "duration_type": "seconds",
                       "easeType": "none", "easeStrength": 3}),
            "finish": T({"type": "none", "duration_type": "seconds",
                         "easeType": "none", "easeStrength": 3}),
        }),
        "information": LuaTable(),
        "authorOptions": LuaTable(),
        "config": LuaTable(),
    }


def icon(id_, parent, triggers, icon_path, x=0, y=0, size=36,
         subregions=None, conditions=None, cooldown=True, desaturate=False,
         zoom=0.3, alpha=1.0, inverse=False):
    d = _common(id_, parent, x, y, subregions, triggers, conditions)
    d.update({
        "regionType": "icon",
        # `icon` is a BOOLEAN (draw the icon at all); the texture path lives in
        # `displayIcon`. Writing the path into `icon` leaves displayIcon empty,
        # so WeakAuras falls back to resolving art from the trigger -- which is
        # how the art could disagree with the tooltip.
        "icon": True,
        "displayIcon": icon_path,
        # -1 (automatic) is what every working community pack uses, so keep it.
        # It derives art from the trigger and falls back to displayIcon. Both
        # are now correct: triggers carry exact verified ids, and displayIcon
        # carries the icon scraped for that same id.
        "iconSource": -1,
        "width": size,
        "height": size,
        "zoom": zoom,
        "alpha": alpha,
        "color": rgba(1, 1, 1, 1),
        "desaturate": desaturate,
        "keepAspectRatio": False,
        "cooldown": cooldown,
        "cooldownSwipe": True,
        "cooldownEdge": False,
        "cooldownTextDisabled": False,
        "useCooldownModRate": True,
        "inverse": inverse,
        "useTooltip": True,
        "progressSource": T({1: -1, 2: ""}),
        "adjustedMin": "",
        "adjustedMax": "",
        "useAdjustededMin": False,
        "useAdjustededMax": False,
    })
    return T(d)


def texture(id_, parent, triggers, tex="Spells\\AuraRune256b", x=0, y=0,
            w=48, h=48, color=(1, 1, 1, 1), subregions=None, conditions=None,
            blend="ADD", rotation=0):
    d = _common(id_, parent, x, y, subregions, triggers, conditions)
    d.update({
        "regionType": "texture",
        "texture": tex,
        "width": w,
        "height": h,
        "color": rgba(*color),
        "blendMode": blend,
        "textureWrapMode": "CLAMPTOBLACKADDITIVE",
        "rotate": False,
        "rotation": rotation,
        "mirror": False,
        "desaturate": False,
    })
    return T(d)


def aurabar(id_, parent, triggers, x=0, y=0, w=180, h=16,
            color=(0.3, 0.6, 1.0, 1.0), subregions=None, conditions=None,
            icon_path=None, inverse=False):
    d = _common(id_, parent, x, y, subregions, triggers, conditions)
    d.update({
        "regionType": "aurabar",
        "width": w,
        "height": h,
        "orientation": "HORIZONTAL",
        "texture": "Clean",
        "textureSource": "LSM",
        "barColor": rgba(*color),
        "barColor2": rgba(*color),
        "enableGradient": False,
        "gradientOrientation": "HORIZONTAL",
        "backgroundColor": rgba(0, 0, 0, 0.5),
        "icon": icon_path is not None,
        "icon_side": "LEFT",
        "icon_color": rgba(1, 1, 1, 1),
        "iconSource": -1,
        "desaturate": False,
        "inverse": inverse,
        "zoom": 0,
        "spark": False,
        "sparkTexture": "Interface\\CastingBar\\UI-CastingBar-Spark",
        "sparkWidth": 10,
        "sparkHeight": 30,
        "sparkColor": rgba(1, 1, 1, 1),
        "sparkBlendMode": "ADD",
        "sparkHidden": "NEVER",
        "sparkOffsetX": 0,
        "sparkOffsetY": 0,
        "sparkRotation": 0,
        "sparkRotationMode": "AUTO",
        "progressSource": T({1: -1, 2: ""}),
        "adjustedMin": "",
        "adjustedMax": "",
        "useAdjustededMin": False,
        "useAdjustededMax": False,
    })
    if icon_path:
        d["displayIcon"] = icon_path
    return T(d)


def _group_common(id_, parent, children, x, y, triggers, conditions):
    d = _common(id_, parent, x, y, [], triggers or [
        T({"type": "aura2", "event": "Health", "unit": "player",
           "debuffType": "HELPFUL", "names": LuaTable(),
           "spellIds": LuaTable(), "subeventPrefix": "SPELL",
           "subeventSuffix": "_CAST_START"})], conditions)
    d.update({
        "controlledChildren": arr(children),
        "scale": 1,
        "sharedFrameLevel": True,
        "border": False,
        "borderEdge": "Square Full White",
        "borderBackdrop": "Blizzard Tooltip",
        "borderColor": rgba(0, 0, 0, 1),
        "backdropColor": rgba(1, 1, 1, 0.5),
        "borderSize": 2,
        "borderOffset": 4,
        "borderInset": 1,
    })
    d.pop("parent", None) if parent is None else None
    return d


def group(id_, parent, children, x=0, y=0, conditions=None):
    d = _group_common(id_, parent, children, x, y, None, conditions)
    d["regionType"] = "group"
    if parent is None:
        d.pop("parent", None)
    return T(d)


def dynamicgroup(id_, parent, children, x=0, y=0, grow="HORIZONTAL",
                 space=4, align="CENTER", sort="none", limit=8):
    """grow="HORIZONTAL" centres children on the anchor.

    "RIGHT" left-aligns them at the anchor and extends rightward, so rows of
    different lengths end up ragged and never line up with a centred bar."""
    d = _group_common(id_, parent, children, x, y, None, None)
    d.update({
        "regionType": "dynamicgroup",
        "grow": grow,
        "align": align,
        "space": space,
        "stagger": 0,
        "sort": sort,
        "sortHybridTable": LuaTable(),
        "animate": False,
        "useLimit": False,
        "limit": limit,
        "gridType": "RD",
        "gridWidth": 5,
        "rowSpace": 1,
        "columnSpace": 1,
        "rotation": 0,
        "arcLength": 360,
        "stepAngle": 15,
        "fullCircle": True,
        "radius": 200,
        "constantFactor": "RADIUS",
        "centerType": "LR",
    })
    return T(d)


# ---------------------------------------------------------------- conditions
def cond(checks, changes):
    return T({"check": checks, "changes": arr(changes)})


def check_and(*checks):
    """AND combinator check. The runtime dispatches AND/OR on `variable`
    (Conditions.lua:234) but registers global-condition events on
    `trigger == -2` (Conditions.lua:955), so BOTH must be emitted."""
    return T({"trigger": -2, "variable": "AND", "checks": arr(list(checks))})


def check_trigger(index, prop, op=None, value=None, variable=None):
    c = T({"trigger": index, "variable": variable or prop})
    if op is not None:
        c["op"] = op
    if value is not None:
        c["value"] = value
    return c


def change(prop, value):
    return T({"property": prop, "value": value})


# -------------------------------------------------------------------- export
def build_export(root, children, wa_version="5.21.2 Beta", v=2000):
    d = LuaTable()
    d["d"] = root
    d["c"] = arr(children)
    d["s"] = wa_version
    d["v"] = v
    d["m"] = "d"
    return d


def export_string(root, children):
    return wa_encode(build_export(root, children))
