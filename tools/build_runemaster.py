"""Build the `Runemaster [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Rev 4. Compact layout modelled on the standard Frost-DK rotation pack look:
flush icons in horizontal bands, thin flat borders, zoomed art, and
DESATURATION carrying availability rather than glow on everything.

        [ tattoo + engravings ]        [ procs ]     <- band 1, active-only
              [  MAIN DAMAGE ROW - flush  ]          <- band 2
              [  mana bar, same width     ]          <- band 3
              [  spec state segments      ]          <- band 4
              [ cooldowns + utility, dim  ]          <- band 5
              [ DoT / debuff bars         ]          <- band 6

Spec rows are gated by a custom Lua group trigger calling GetSpellInfo on a
signature spell, because shared-kit and cooldown displays do NOT self-filter.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W
from wacodec import LuaTable

# Release tag. Feeds the uid salt and the group name. WeakAuras dedupes imports
# on uid, so a rebuilt pack MUST carry a different salt or the client treats it
# as already-installed and silently keeps the old copy. Bump on any release.
# The pre-release tags were final2..final17; `1.0` is the first db.ascension
# submission.
#
# 1.2: the cooldown ladder anchors band-to-band instead of stepping by a
# build-time row count, and the long-term row is one band per spec.
VERSION = "1.2"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {
    "Runeblade": "runeblade2",
    "Genesis": "inv_ascend_magicartifact_13",
    "Runecarve": "inv_misc_rune_14",
    "Wild Steam": "spell_frost_frostward",
    "Marked: Runic Brand": "5_mageskill14_border",
    "Surging Slash": "runeblade2",
    "Uncovered Engravings": "inv_misc_rune_05",
    "Runelord": "custom_t_nhance_rpg_icons_magickeeper_border",
    "Earthen Fists": "inv_misc_trinket6oog_stonefist2",
    "Sky and Stone": "nhi_earthmask_border",
    "Harnessing Leylines": "inv_ascend_magicartifact_13",
    "Runeslinger": "custom_t_nhance_rpg_icons_magicspeed_border",
    "Transcribing": "inv_inscription_80_contract_vulpera",
    "Scroll of Magic": "custom_t_nhance_rpg_icons_scrollofmagic_border",
    "Runic Explosion": "novart_magicspell_(58)_border",
    "Primordialism": "spell_nature_astralrecalgroup",
    "Blade Rift": "5_magicresistance_border",
    "Frozen": "nhi_icestone_border",
    "Runic Brand": "5_mageskill14_border",
}
OVERRIDE = {
    "Runeshroud": "ability_rogue_shroudofconcealment",
    "Palm Sigil: Arcane": "nhi_arcanestone_border",
    "Palm Sigil: Earth": "nhi_earthmask_border",
    "Palm Sigil: Fire": "custom_t_nhance_rpg_icons_firerune_border",
    "Palm Sigil: Frost": "nhi_icestone_border",
    "Palm Sigil: Water": "spell_frost_summonwaterelemental",
    "Palm Sigil: Wind": "spell_nature_cyclone",
    "Runic Tempest": "spell_nature_unrelentingstorm",
    # No icon on db.exil.es and absent from the other sources; standard 3.3.5
    # icons picked to be thematic and distinct from neighbouring art.
    "Cinderwake": "spell_fire_selfdestruct",
    "Etch": "inv_inscription_papyrus",
    "Glyphic Infusion": "spell_arcane_studentofmagic",
    "Ice Rune": "spell_frost_frozencore",
    "Leyline Adjustment": "spell_arcane_blink",
    "Resonance Rune": "spell_arcane_massdispel",
    "Torch": "spell_fire_burnout",
    "Whisperwind": "spell_nature_earthbind",
    # both resolve to nhi_icestone_border upstream; keep them distinguishable
    "Inscription: Permafrost": "spell_frost_glacier",
}


# Already shown in the main row / state band / proc row -- never repeat here.
ELSEWHERE = {
    "Glyphic Ruin", "Primordial Blast", "Thaumaturgy", "Elemental Burst",
    "Runic Obliteration", "Runeblade", "Fist of the Ancients", "Runic Brand",
    "Runic Explosion", "Smolder", "Fracture", "Hoarfrost", "Hurricane",
    "Frigid Blast",
} | {f"Weapon Engraving: {e}"          # shown in the status row
     for e in ("Air", "Arcane", "Earth", "Fire", "Ice", "Water")}

# Damage cooldowns, in the order you press them. Ley Lock and Leyline
# Adjustment are pinned to the end of this row.
OFFENSIVE = ["Zenith", "Genesis", "Convergence", "Power Engraving",
             "Primordial Fury", "Runic Tempest", "Fists of Power",
             "Turbulence", "Ley Power", "Glyphic Overload",
             "Eye of the Beholder", "Manuscription", "Rune Master",
             "Stack The Deck", "Glyphic Infusion", "Runed Cascade",
             "Prismatic Blade", "Spellblades", "Wild Steam"]
OFFENSIVE_TAIL = ["Ley Lock", "Leyline Adjustment"]

DEFENSIVE = ["Granite Resolve", "Warding Rune", "Phase Out", "Guarding Rune",
             "Echo Rune", "Magebreaker", "Augur's Shield", "Permafrost Rune",
             "Glacial Rune", "Inscription: Permafrost", "Casting Cuffs",
             "Resonance Rune"]
# Not tooltip-verified, but db.exil.es points at a spell db.ascension.gg does
# not mark as an ability while ascension.gg has a clear Ability/Talent entry.
# Replace with a tooltip id when one is captured.
CROSSCHECK = {"Magebreaker": 804061}

# Ids whose db.exil.es page does not expose an icon; taken from the other DBs.
ICON_GAP = {
    "705560": "novart_magicspell_(58)_border",    # Runic Obliteration
    "92153": "inv_misc_trinket6oog_stonefist2",   # Fists of Power
    "803011": "novart_magicspell_(51)_border",    # Runestone: Torch
    "500501": "spell_arcane_arcane04",            # Genesis (was colliding
                                                  # with Ley Power's icon)
    # Arcane and Ice are the exact failure ic()'s docstring warns about: the
    # tooltip-verified id lands but the art lookup misses, because
    # exiles-id-meta.json was scraped against db.exil.es's WRONG ids (653263
    # Arcane / 653217 Ice) while IN_GAME corrects them to 653265 / 653264.
    # Meta therefore has weapon_engraving_{air,earth,fire,water} and nothing
    # under the corrected keys, so both fell through to a questionmark and
    # collided as duplicate art in the long-term row.
    "653265": "weapon_engraving_arcane",          # Weapon Engraving: Arcane
    "653264": "weapon_engraving_ice",             # Weapon Engraving: Ice
}


# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values.
#
# THE FLAGS ARE A TODO LIST, NOT A CONFIGURATION. Every one of them holds
# Runemaster on behaviour Chronomancer has already moved past, and each is its
# own release: change one, read the fixture diff line by line, confirm in game,
# re-freeze. A NEW class passes none of these -- see build_chronomancer.py.
#
#   roles_from_inventory  resources/abilities-runemaster.md exists and is
#                         reviewed; the OFFENSIVE / DEFENSIVE lists below stop
#                         being hand-maintained the day this flips.
#   trust_spell_meta      spell-meta-runemaster.json exists. Until it is
#                         trusted, every cooldown trigger is exact-id and every
#                         gate is taken at face value -- which is how five
#                         Chronomancer abilities shipped invisible.
#   override_first        OVERRIDE currently only wins where the id resolved no
#                         art at all.
#   balanced_rows         10 cooldowns lay out 9+1 rather than 5+5.
#   icons                 name-keyed icons.json, keyed to Runemaster's own
#                         spells. The per-class scrape (skills + exiles) is the
#                         forward path and needs icon-meta-runemaster.json.
#
# CD_PER_ROW: Runemaster's narrowest main row is five icons (228px), so
# 28w - 2 <= 1.2 * 228 allows 9.
CLS = W.init("runemaster", version=VERSION, prefix="RM", cd_per_row=9,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK,
             icon_gap=ICON_GAP, elsewhere=ELSEWHERE,
             icons="legacy", id_meta_file="exiles-id-meta.json",
             roles_from_inventory=False, trust_spell_meta=False,
             override_first=False, balanced_rows=False)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above


# The game tags your active spec with a hidden aura. Gating on that is exact,
# so the previous GetSpellInfo scoring heuristic is gone -- that heuristic let
# several spec groups match at once and stacked their rows, which is what
# produced the duplicate Primordial Blast icons.
# NOTE: these `CoA Aura - Runemaster - <Spec>` entries exist in the spell
# database but are NOT auras the player carries -- gating on them hid every
# display. Kept for reference only; gating is load.use_spellknown.
SPEC_AURA = {
    "Glyphic": 887088,
    "Engravement": 887089,
    "Riftblade": 887090,
}


def spec_gate(spec):
    return B.aura_trigger([str(SPEC_AURA[spec])], unit="player",
                          helpful=True, own_only=False)


def sigil_gate():
    return spec_gate("Riftblade")


# Abilities that hold charges rather than a plain cooldown. These get a count
# drawn in the corner; everything else would just show a meaningless "1".
# Zenith only has charges once Runelord is talented (it becomes 712389), but
# the count is harmless on the base version.
CHARGES = {"Runeblade": 3, "Zenith": 2}


def _bottom_rows(spec_key):
    """(offense, utility) ability names for one spec, in press order.

    Split out of emit_bottom_block so the ladder can be planned across ALL
    specs before any band is emitted: a shared band has one yOffset, so the
    depth it reserves has to cover the spec that wraps deepest.
    """
    have = {n for n, v in COOLDOWNS.items()
            if (spec_key in v["specs"] or not v["specs"])
            and cd_secs(v["cd"]) <= 300 and n not in ELSEWHERE}
    have |= {n for n in ID_OVERRIDE if n in EXILES and n not in ELSEWHERE}
    # The audit DISCOVERS abilities; the curated lists are authoritative. Fists
    # of Power and friends have no cooldown row on db.exil.es but are real
    # buttons, so never drop a curated name just because the scrape is thin.
    have |= {n for n in OFFENSIVE + OFFENSIVE_TAIL + DEFENSIVE
             if n not in ELSEWHERE and (n in ID_OVERRIDE or n in EXILES)
             and in_spec(n, spec_key)}

    # the tail is pinned to every spec, spec-membership check bypassed
    offense = [n for n in OFFENSIVE if n in have] + \
              [n for n in OFFENSIVE_TAIL
               if n in ID_OVERRIDE or n in EXILES]
    defensive = [n for n in DEFENSIVE if n in have]
    utility = defensive + sorted(have - set(offense) - set(defensive))
    return offense, utility

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text.
PROC_GLOW = {
    "Smolder": ["Spellfire Runes"],              # resets Smolder
    "Runeblade": ["Windsage", "Surging Slash"],  # next Runeblade(s) empowered
    "Runic Brand": ["Power Overwhelming"],       # resets Runic Brand
    "Fist of the Ancients": ["Runic Tempest"],   # resets Fist of the Ancients
    "Glyphic Ruin": ["Glyphic Overload", "Eye of the Beholder"],
    "Primordial Blast": ["Eye of the Beholder"],
}
# Class content the engine reads while it lays bands out. `bottom_rows` is the
# hook that keeps the curated OFFENSIVE / DEFENSIVE lists above authoritative;
# it disappears with roles_from_inventory.
W.configure(charges=CHARGES, proc_glow=PROC_GLOW, bottom_rows=_bottom_rows,
            # The tail applies no buff, so it earns no buff-row icon.
            no_buff=set(OFFENSIVE_TAIL))


# ================================================================== 1. CORE
CORE = []

# One centred, active-only status row. Tattoo, engravings, raid buffs and
# target state all live in a single dynamic group so they pack together and
# stay centred instead of sitting at fixed offsets across the screen.
TATTOOS = [
    ("Air", "802630", (0.70, 0.90, 0.95)),
    ("Arcane", "803748", (0.75, 0.40, 0.95)),
    ("Earth", "801094", (0.62, 0.44, 0.20)),
    ("Fire", "801106", (0.95, 0.45, 0.15)),
    ("Frost", "807834", (0.40, 0.75, 1.00)),
    ("Water", "801107", (0.20, 0.55, 0.90)),
]

# Engravings: Air/Arcane/Earth/Fire/Ice/Water (no Frost -- that is a tattoo).
# Tracked BOTH as an aura and as a temporary weapon enchant on either hand,
# because the aura-only version showed nothing in game. activeTriggerMode -10
# means any one of these firing is enough.
ENGRAVINGS = [("Air", (0.70, 0.90, 0.95)), ("Arcane", (0.75, 0.40, 0.95)),
              ("Earth", (0.62, 0.44, 0.20)), ("Fire", (0.95, 0.45, 0.15)),
              ("Ice", (0.55, 0.85, 1.00)), ("Water", (0.20, 0.55, 0.90))]
# Two spells exist per element and they are NOT interchangeable:
#   "Weapon Engraving: Fire" (653022) is the CAST -- "engrave a fire rune onto
#   your weapon for 1 hour"; it is never present as a buff.
#   "Fire Engraving"         (653211) is the resulting IMBUE aura.
# Tracking the cast id as an aura can never fire, which is why the engraving
# row stayed empty. These are the imbue ids.
# Cast-spell ids read straight off in-game tooltips. db.exil.es was wrong on
# two of them (Arcane 653263 and Ice 653217), so these override it.
ENGRAVING_CAST = {e: IN_GAME[f"Weapon Engraving: {e}"]
                  for e in ("Air", "Arcane", "Earth", "Fire", "Ice", "Water")}
# The imbue auras the casts apply, from db.exil.es.
ENGRAVING_AURA = {"Air": 653223, "Arcane": 653267, "Earth": 653219,
                  "Fire": 653211, "Ice": 653266, "Water": 653214}
# Match every plausible surface for an engraving, because the row has stayed
# empty across several attempts and we still do not know which one the client
# actually exposes:
#   - the imbue aura by id and by name ("Fire Engraving")
#   - the cast-spell name ("Weapon Engraving: Fire"), in case it lingers
#   - a temporary weapon enchant on either hand, by name
# "Frost" is included as an alias for Ice: the data says the engraving set uses
# Ice and that Frost belongs to the tattoos, but that is worth not betting on.
ALIAS = {"Ice": ["Frost Engraving", "Weapon Engraving: Frost"]}
# Short buffs are emitted per spec (merged with that spec's target debuffs
# into one "what is up right now" row), so they are data here rather than
# displays.
SHORT_ENTRIES = [
    ("Frost Prison", (0.4, 0.8, 1.0), {"unit": "target", "helpful": False,
                                       "alt": ["Permafrost Rune", "Glacial Rune",
                                               "Cryobrand", "Frozen"]}),
    # Deliberately in TWO places, unlike everything else here: the buff row
    # says "you are shrouded right now" (which gates Warpdagger, the Imbues
    # and Inscription: Permafrost), the utility row says "you can re-enter in
    # N seconds" off its 10s cooldown. Neither answers the other's question,
    # so Runeshroud is NOT in ELSEWHERE.
    ("Runeshroud", (0.6, 0.5, 0.9), {}),
    ("Palm Sigil: Arcane", (0.75, 0.40, 0.95), {}),
    ("Palm Sigil: Earth", (0.62, 0.44, 0.20), {}),
    ("Palm Sigil: Fire", (0.95, 0.45, 0.15), {}),
    ("Palm Sigil: Frost", (0.40, 0.75, 1.00), {}),
    ("Palm Sigil: Water", (0.20, 0.55, 0.90), {}),
    ("Palm Sigil: Wind", (0.70, 0.90, 0.95), {}),
]

RAID_BUFFS = [("Runes of Quickness", (0.4, 0.9, 1.0)),
              ("Leyline Disturbance", (0.9, 0.7, 1.0)),
              ("Runic Power", (1.0, 0.85, 0.4))]


def longterm_band(spec_name, bands, y):
    """The long-term row -- tattoos, weapon engravings, raid auras -- ONE PER
    SPEC, anchored under that spec's own cooldown stack.

    It used to be a single band in Core at a fixed Y_LONG that cleared the
    DEEPEST spec. Core has one yOffset for the whole pack, so Glyphic and
    Riftblade -- which wrap utility at two rows where Engravement takes three --
    sat 46px above their own last cooldown row, holding space for a spec that
    was not loaded. That gap is invisible in the in-play view because these
    displays are active-only, which is why it went unnoticed: it only appears
    once a long-term buff is actually up.

    Per-spec costs one copy of each icon per spec. The gate comes free: the
    merge tags any leaf whose parent chain reaches `RM <Spec>` with that spec,
    and apply_leaf_gates then puts the spec's signature spell on it. Those
    signatures are learned at level 10-15 while Runic Tattoos are level-30
    attunements, so gating this content behind them costs a levelling character
    nothing it could already use.
    """
    band = f"RM {spec_name} Longterm"
    out = []
    for elem, aura_id, col in TATTOOS:
        out.append(add(B.icon(
            f"RM {spec_name} Tattoo {elem}", band,
            [B.aura_trigger([aura_id, f"Runic Tattoos: {elem}"], own_only=False)],
            ic(f"Runic Tattoos: {elem}"), size=SZ_SMALL,
            subregions=[B.sub_text(elem[:3].upper(), size=9,
                                   anchor="INNER_BOTTOM", color=col + (1.0,)),
                        thin()])))
    for elem, col in ENGRAVINGS:
        names = [str(ENGRAVING_CAST[elem]), str(ENGRAVING_AURA[elem]),
                 f"Weapon Engraving: {elem}", f"{elem} Engraving"] \
            + ALIAS.get(elem, [])
        trig = [B.aura_trigger(names, own_only=False),
                B.enchant_trigger(f"{elem} Engraving", weapon="main"),
                B.enchant_trigger(f"{elem} Engraving", weapon="off")]
        for alt in ALIAS.get(elem, []):
            if alt.endswith("Engraving") and ":" not in alt:
                trig.append(B.enchant_trigger(alt, weapon="main"))
        out.append(add(B.icon(
            f"RM {spec_name} Engraving {elem}", band, trig,
            ic(f"Weapon Engraving: {elem}"), size=SZ_SMALL,
            subregions=[B.sub_text(elem[:2].upper(), size=9,
                                   anchor="INNER_TOPLEFT", color=col + (1.0,)),
                        B.sub_text("%p", size=9, anchor="INNER_BOTTOM"),
                        thin()])))
    for name, col in RAID_BUFFS:
        out.append(add(B.icon(
            f"RM {spec_name} Raid {name}", band,
            [B.aura_trigger([str(sid(name)), name], own_only=False)],
            ic(name), size=SZ_SMALL, subregions=[thin()])))
    add(B.dynamicgroup(band, f"RM {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)

# ---- missing-buff reminders ------------------------------------------------
# Sit high and central so they are hard to miss. Each fires only when the thing
# is absent, so they are invisible once you are buffed.
ALERTS = []

# Missing engraving on EITHER hand. Custom Lua because the off-hand must only
# be checked when it actually holds a weapon:
#   * a two-hander leaves slot 17 empty -> off-hand is not applicable
#   * a shield or held-in-off-hand occupies slot 17 but cannot be engraved
# equipSlot is used rather than the item class, because class is localised.
ENGRAVE_CHECK_LUA = r"""function()
    local mh, _, _, oh = GetWeaponEnchantInfo()

    if not mh then
        aura_env.why = "MAIN HAND"
        return true
    end

    local link = GetInventoryItemLink("player", 17)
    if link then
        local _, _, _, _, _, _, _, _, slot = GetItemInfo(link)
        -- anything in slot 17 that is not a shield or a held item is a weapon
        -- and can carry an engraving
        if slot ~= "INVTYPE_SHIELD" and slot ~= "INVTYPE_HOLDABLE" then
            if not oh then
                aura_env.why = "OFF HAND"
                return true
            end
        end
    end

    aura_env.why = nil
    return false
end"""

alert = B.icon(
    "RM Alert No Engraving", "RM Alerts",
    [B.T({
        "type": "custom", "custom_type": "status", "check": "update",
        "events": ("UNIT_INVENTORY_CHANGED PLAYER_EQUIPMENT_CHANGED "
                   "PLAYER_ENTERING_WORLD"),
        "custom": ENGRAVE_CHECK_LUA,
        "customName": "function()\n    return aura_env.why or \"\"\nend",
        "unit": "player", "debuffType": "HELPFUL",
        "names": LuaTable(), "spellIds": LuaTable(),
        "auranames": LuaTable(), "auraspellids": LuaTable(),
        "subeventPrefix": "SPELL", "subeventSuffix": "_CAST_START",
    })],
    ic("Weapon Engraving: Fire"), size=SZ_ALERT, desaturate=True,
    cooldown=False,
    subregions=[B.sub_background(),
                B.sub_text("NO ENGRAVING", size=10, anchor="INNER_BOTTOM",
                           color=(1, 0.35, 0.35, 1)),
                B.sub_text("%n", size=9, anchor="INNER_TOP",
                           color=(1, 0.75, 0.35, 1)),
                B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                             edge=EDGE),
                B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
alert["customText"] = "function()\n    return aura_env.why or \"\"\nend"
ALERTS.append(add(alert))

# None of the three Etchings (or their Greater versions) present.
ETCHINGS = ["Etching of the Magi", "Etching of the Dextrous",
            "Etching of the Leylines", "Greater Etching of the Magi",
            "Greater Etching of the Dextrous", "Greater Etching of the Leylines"]
ALERTS.append(add(B.icon(
    "RM Alert No Etching", "RM Alerts",
    [B.aura_trigger([str(sid(n)) for n in ETCHINGS] + ETCHINGS,
                    own_only=False, show_on="showOnMissing")],
    ic("Etching of the Magi"), size=SZ_ALERT, desaturate=True,
    subregions=[B.sub_background(),
                B.sub_text("NO ETCHING", size=11, anchor="INNER_BOTTOM",
                           color=(1, 0.35, 0.35, 1)),
                B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                             edge=EDGE),
                B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])))

add(B.dynamicgroup("RM Alerts", "RM Core", ALERTS, x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
CORE.append("RM Alerts")

add(B.group("RM Core", ROOT, CORE, x=0, y=0))


# =============================================================== 2. GLYPHIC
G = []
G.append(cd_group("RM Glyphic Main", "RM Glyphic",
                  ["Glyphic Ruin", "Primordial Blast", "Thaumaturgy",
                   "Elemental Burst", "Runic Obliteration"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14))
G.append(mana_bar("RM Glyphic Mana", "RM Glyphic", Y_BAR,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5), h=BAR_H_STACKED))
# Glyph chain is the spec's segmented resource; all three can be up at once
# under Glyphic Overload.
# Glyph segments: Frost -> Flame -> Arcane fill as you build. All three can be
# lit at once under Glyphic Overload.
seg_bar("RM Glyph", "RM Glyphic",
        [("Frost Glyph", ["92152", "Frost Glyph"], (0.35, 0.70, 1.00)),
         ("Flame Glyph", ["520091", "Flame Glyph"], (1.00, 0.45, 0.12)),
         ("Arcane Glyph", ["520092", "Arcane Glyph"], (0.78, 0.38, 1.00))],
        # Always-true trigger: the empty segments must be visible whenever the
        # aura is loaded. They previously keyed off the CoA spec aura 887088,
        # which is a database entry and NOT a buff the player carries, so the
        # dim segments never drew and only filled glyphs ever appeared.
        # load.use_spellknown already restricts these to Glyphic.
        Y_SEG, B.health_trigger("player"),
        row_w(5), G)

_y_G = emit_bottom_block("Glyphic", "glyphic", G,
[("Glyphic Overload", (1.0, 0.85, 0.2)),
                     ("Eye of the Beholder", (1.0, 0.75, 0.3)),
                     ("Frigid Blast", (0.5, 0.8, 1.0)),
                     ("Transcribing", (0.8, 0.6, 1.0)),
                     ("Runeslinger", (0.6, 1.0, 0.7)),
                     ("Scroll of Magic", (0.9, 0.6, 1.0))],
SHORT_ENTRIES + [("Flame Glyph", (0.95, 0.45, 0.15), {"unit": "target", "helpful": False}),
     ("Manuscription", (0.75, 0.45, 0.95), {"unit": "target", "helpful": False}),
     ("Unleashed Power", (0.60, 0.80, 1.00), {"unit": "target", "helpful": False}),
     ("Magic Etchings", (0.80, 0.70, 0.50), {"unit": "target", "helpful": False})])
longterm_band("Glyphic", G, _y_G)
# One row: what is up on me (short buffs) and on my target (debuffs).
add(spec_group("RM Glyphic", G, spec_gate("Glyphic")))

# ============================================================ 3. ENGRAVEMENT
E = []
E.append(cd_group("RM Engravement Main", "RM Engravement",
                  ["Runeblade", "Fist of the Ancients", "Runic Brand",
                   "Primordial Blast", "Runic Explosion"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14))
E.append(mana_bar("RM Engravement Mana", "RM Engravement", Y_BAR_SOLO,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5)))
_y_E = emit_bottom_block("Engravement", "engravement", E,
[("Fire Carving", (0.95, 0.45, 0.15)),
                     ("Water Carving", (0.20, 0.55, 0.90)),
                     ("Earth Carving", (0.62, 0.44, 0.20)),
                     ("Air Carving", (0.70, 0.90, 0.95)),
                     ("Marked: Runic Brand", (0.90, 0.30, 0.20),
                      {"unit": "target", "helpful": False}),
                     ("Power Overwhelming", (1.0, 0.85, 0.2)),
                     ("Uncovered Engravings", (1.0, 0.8, 0.3)),
                     ("Runelord", (1.0, 0.6, 0.2)),
                     ("Earthen Fists", (0.7, 0.5, 0.3)),
                     ("Sky and Stone", (0.6, 0.9, 1.0)),
                     ("Convergence", (0.8, 0.7, 1.0))],
SHORT_ENTRIES + [("Genesis", (0.80, 0.50, 1.00), {"unit": "target", "helpful": False}),
     ("Magic Etchings", (0.80, 0.70, 0.50), {"unit": "target", "helpful": False})])
longterm_band("Engravement", E, _y_E)
# Palm Sigils are not Riftblade-only -- Engravement uses them too -- so they get
# the same state band under the resource bar. Carvings are a random proc off
# Fist of the Ancients and belong in the proc row below.
# One row: what is up on me (short buffs) and on my target (debuffs).
add(spec_group("RM Engravement", E, spec_gate("Engravement")))

# ============================================================== 4. RIFTBLADE
R = []
R.append(cd_group("RM Riftblade Main", "RM Riftblade",
                  ["Runeblade", "Smolder", "Fracture", "Hoarfrost",
                   "Hurricane", "Primordial Blast"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14))
R.append(mana_bar("RM Riftblade Mana", "RM Riftblade", Y_BAR_SOLO,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(6)))

# No segmented bar for Riftblade. Sidekick is explicit that this is "a straight
# two-handed melee spec, not an attunement or sigil builder", so a permanent
# sigil bar would occupy prime space under the resource bar for a system the
# spec is not played around. The segmented bar stays Glyphic-only.

_y_R = emit_bottom_block("Riftblade", "riftblade", R,
[("Spellfire Runes", (1.0, 0.6, 0.2)),
                     ("Windsage", (0.7, 1.0, 0.8)),
                     ("Surging Slash", (1.0, 0.85, 0.4)),
                     ("Swift Etching", (0.6, 0.9, 1.0)),
                     ("Primordialism", (0.9, 0.7, 1.0)),
                     ("Blade Rift", (0.8, 0.6, 1.0))],
SHORT_ENTRIES + [("Smolder", (1.00, 0.50, 0.15), {"unit": "target", "helpful": False}),
     ("Hoarfrost", (0.45, 0.80, 1.00), {"unit": "target", "helpful": False}),
     ("Runestone: Torch", (1.00, 0.70, 0.30), {"unit": "target", "helpful": False})])
longterm_band("Riftblade", R, _y_R)
# One row: what is up on me (short buffs) and on my target (debuffs).
add(spec_group("RM Riftblade", R, spec_gate("Riftblade")))
# Offense and Utility are NOT merged, matching Chronomancer.
#
# A merged band is one dynamic group with ONE yOffset serving all three specs,
# so emit_bottom_block must step by the DEEPEST spec's row count and every band
# below lands at the same y for everyone. Per-spec long-term bands then all sit
# at that same worst-case anchor and the gap survives -- un-merging alone fixes
# nothing, and per-spec long-term alone fixes nothing. Together they work.
#
# Main and Buffs stay merged: nothing below them depends on how far they wrap,
# so sharing those is free.
MERGE_BANDS = ("Main", "Buffs")
W.configure(merge_bands=MERGE_BANDS)


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
SPEC_KNOWN = {
    "Glyphic": 801179,       # Glyphic Ruin
    "Engravement": 712326,   # Fist of the Ancients
    "Riftblade": 801104,     # Hoarfrost
}
W.configure(spec_known=SPEC_KNOWN)


_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()
W.chain_ladder()
if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    W.finish((_GATED, _ANY, _CLASSED))
