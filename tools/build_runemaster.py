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
import json
import os
import re

import wabuild as B
from wacodec import LuaTable

SP = os.path.dirname(os.path.abspath(__file__))
# Source data lives in resources/, code lives in tools/. Some files still sit
# alongside the code (icons.json, in-game-verified.json), so resolve against
# resources/ first and fall back to tools/. Without this the build dies at
# import time:
#   FileNotFoundError: .../tools/exiles-runemaster.json
RESOURCES = os.path.join(os.path.dirname(SP), "resources")


def data(name):
    """Resolve a data file: resources/ wins, tools/ is the legacy fallback."""
    p = os.path.join(RESOURCES, name)
    return p if os.path.exists(p) else os.path.join(SP, name)


# Bump on every published build. Feeds the uid salt AND the group name,
# so a reimport is unambiguously a new pack and the loaded version is
# visible in the WeakAuras list.
# Release tag. Feeds the uid salt AND the group name. WeakAuras dedupes
# imports on uid, so a rebuilt pack MUST carry a different salt or the client
# treats it as already-installed and silently keeps the old copy. Bump this
# (final2, final3, ...) on any future release.
VERSION = "final14"

# WA_SPEC=glyphic|engravement|riftblade emits a single-spec pack: Core plus
# that one spec, for players who only ever play the one.
SPEC_ONLY = os.environ.get("WA_SPEC", "").strip().lower() or None
SPEC_TITLE = {"glyphic": "Glyphic", "engravement": "Engravement",
              "riftblade": "Riftblade"}.get(SPEC_ONLY)
GLOW = os.environ.get("WA_GLOW") == "1"
ICONS = json.load(open(data("icons.json")))

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

# ---- layout ---------------------------------------------------------------
# Every band is centred at x=0 and stacked vertically. Scattering groups to
# different x offsets is what made the old layout read as disjointed next to a
# Luxthos-style pack. Dynamic groups only lay out ACTIVE children, so the
# active-only bands self-centre and stay tidy however many are showing.
Y_ALERT = -18       # missing-buff reminders, high and central
Y_PROCS = -60       # spec procs, short windows, active-only
Y_BUFFS = -84       # single row: procs, running CDs, buffs, debuffs
Y_MAIN = -132       # main damage row
Y_BAR = -168        # resource bar, clears the main row
Y_SEG = -194        # Glyphic glyph bar. Riftblade and Engravement have
                    # nothing here, so their bottom block starts at this
                    # band instead of leaving it empty.
Y_CDS = -242        # rotational cooldowns (wraps)
CD_PER_ROW = 12
CD_ROW_STEP = 30
SZ_CD = 26
SZ_ALERT = 38
SZ_BUFF = 36         # buff row -- larger so the timer is legible
Y_LONG = -300       # long-term buffs, pinned to the bottom
Y_DOTS = -333       # applied DoTs / debuffs, below the cooldown block

SZ_MAIN = 44
SZ_SMALL = 28
SZ_STATE = 28
GAP = 2             # tight, but enough that overlaid text does not collide
BAR_W = 270
BAR_H = 20           # resource bar height
SEG_H = 16           # glyph segment height
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
EXILES = json.load(open(data("exiles-runemaster.json")))
# Every Runemaster ability that actually has a cooldown, audited from
# db.exil.es spell pages (see audit_cds.py). Hand-maintained lists kept missing
# things like Convergence and Primordial Fury.
COOLDOWNS = json.load(open(data("cooldown-abilities.json")))


def _cd_secs(text):
    m = re.match(r"([\d.]+)\s*(sec|min|hour)", text)
    return (float(m.group(1)) * {"sec": 1, "min": 60, "hour": 3600}[m.group(2)]
            if m else 1e9)


# Already shown in the main row / state band / proc row -- never repeat here.
ELSEWHERE = {
    "Glyphic Ruin", "Primordial Blast", "Thaumaturgy", "Elemental Burst",
    "Runic Obliteration", "Runeblade", "Fist of the Ancients", "Runic Brand",
    "Runic Explosion", "Smolder", "Fracture", "Hoarfrost", "Hurricane",
    "Runeshroud", "Frigid Blast",
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
CROSSCHECK = {"Magebreaker": 804061}
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
_SB = os.path.expanduser("~/second-brain/projects/coa-weakauras/resources")
SPEC_TEXT = {sp: open(f"{_SB}/sidekick-runemaster-{sp}.md").read()
             for sp in ("glyphic", "engravement", "riftblade")}


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


# Real icon for each spell id, scraped per-spell from db.exil.es. Previously
# icons came from a hand-built name lookup while triggers used verified ids, so
# the art and the tooltip could disagree -- e.g. slot 1 drew Primordial Blast's
# orb while the trigger was Runeblade.
ID_META = json.load(open(data("exiles-id-meta.json")))

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


def ic(name):
    # resolve art through the SAME id the trigger uses, so a corrected id
    # corrects the icon too -- otherwise the tooltip id lands but the art
    # still comes from the stale scraped id
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


def thin(size=2):
    return B.sub_border(color=DARK, size=size, offset=1, edge=EDGE)


children = []
B.set_salt(f"runemaster-{SPEC_ONLY or 'all'}-{VERSION}")
ROOT = (f"Runemaster {SPEC_TITLE} [CoA]" if SPEC_TITLE
        else "Runemaster [CoA]")


def add(region):
    children.append(region)
    return region["id"]


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


def spec_group(id_, kids, trigger):
    g = B.group(id_, ROOT, kids, x=0, y=0)
    g["triggers"] = B._trigger_wrap([trigger])
    return g


# Abilities that hold charges rather than a plain cooldown. These get a count
# drawn in the corner; everything else would just show a meaningless "1".
# Zenith only has charges once Runelord is talented (it becomes 712389), but
# the count is harmless on the base version.
CHARGES = {"Runeblade": 3, "Zenith": 2}

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


# Cooldown urgency. `expirationTime` with op "<" takes SECONDS REMAINING and
# is the variable the working community packs use for this (33 uses in the
# Templar pack), so the tiers are built on verified ground.
URGENCY = [(20, "timer"), (10, "glow"), (5, "pulse")]


def cd_icon(display_id, parent, name, size, charges=False, urgency=False):
    """A cooldown icon.

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
    a cast -- the cue for holding a press rather than clipping it.
    """
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

    triggers = [B.spell_cd_trigger(sid(name), show_on="showAlways", exact=True)]
    conds = []
    if urgency:
        # Every urgency tier is ANDed with "this is a real cooldown, not the
        # GCD". The trigger reports the global cooldown (use_showgcd), so a
        # bare `expirationTime < 5` fires the urgent glow on every global, on
        # every icon in the row -- which is exactly what shipped in final12.
        #
        # The guard is on `duration`, NOT `gcdCooldown`. `gcdCooldown` is
        # declared hidden on the prototype and is therefore not exposed as a
        # condition variable; WeakAuras drops the unknown sub-check and the AND
        # collapses back to the bare expirationTime test. `duration` is
        # guaranteed present whenever progressType == "timed" (data-model
        # 6.3), so it always compiles.
        #
        # The GCD is 1.5s and hastes DOWN, never up, so 3s separates it from
        # any real cooldown with room to spare. Only Unleash Essences (2.5s)
        # and Trap Runes (3.0s) fall below the line, and a cooldown that short
        # sits permanently inside the 5s tier anyway -- it would pulse orange
        # for its whole duration, which is noise, not information.
        GCD_FLOOR = "3"

        def real_cd(seconds):
            return B.check_and(
                B.T({"trigger": 1, "variable": "expirationTime",
                     "op": "<", "value": seconds}),
                B.T({"trigger": 1, "variable": "duration",
                     "op": ">", "value": GCD_FLOOR}))

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
        conds.append(B.cond(
            B.T({"trigger": len(triggers), "variable": "show", "value": 1}),
            [B.change(f"sub.{glow_index}.glow", True),
             B.change(f"sub.{glow_index}.glowColor",
                      B.rgba(1.0, 0.95, 0.5, 1.0))]))

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
             text_size=None):
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
                               charges=n in CHARGES)))
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
             w=None, size=SZ_SMALL):
    """Applied DoTs / maintained debuffs as a compact icon row with a timer.

    These used to be four stacked 230px bars, which dominated the layout and
    read as oversized buttons. Icons with the remaining duration underneath
    carry the same information in one band.
    """
    ids = []
    for name, col, note in entries:
        ids.append(add(B.icon(
            f"{gid} {name}", gid,
            [B.aura_trigger([str(sid(name)), name], unit=unit,
                            helpful=helpful)],
            ic(name), size=size,
            subregions=[B.sub_text("%p", size=10, anchor="INNER_BOTTOM"),
                        B.sub_text("%s", size=10, anchor="INNER_TOPRIGHT"),
                        B.sub_border(color=col + (1.0,), size=2, offset=1,
                                     edge=EDGE)])))
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


def row_w(n, size=SZ_MAIN):
    """Exact pixel width of a flush row, so the resource bar lines up with it."""
    return n * size + (n - 1) * GAP


def mana_bar(gid, parent, y, color, w=None):
    add(B.aurabar(gid, parent, [B.power_trigger("player", 0)],
                  x=0, y=y, w=w or BAR_W, h=BAR_H, color=color,
                  subregions=[
                      B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                 justify="RIGHT"),
                  ]))
    return gid


# ================================================================== 1. CORE
CORE = []

# One centred, active-only status row. Tattoo, engravings, raid buffs and
# target state all live in a single dynamic group so they pack together and
# stay centred instead of sitting at fixed offsets across the screen.
LONGTERM = []

TATTOOS = [
    ("Air", "802630", (0.70, 0.90, 0.95)),
    ("Arcane", "803748", (0.75, 0.40, 0.95)),
    ("Earth", "801094", (0.62, 0.44, 0.20)),
    ("Fire", "801106", (0.95, 0.45, 0.15)),
    ("Frost", "807834", (0.40, 0.75, 1.00)),
    ("Water", "801107", (0.20, 0.55, 0.90)),
]
for elem, aura_id, col in TATTOOS:
    LONGTERM.append(add(B.icon(
        f"RM Tattoo {elem}", "RM Longterm",
        [B.aura_trigger([aura_id, f"Runic Tattoos: {elem}"], own_only=False)],
        ic(f"Runic Tattoos: {elem}"), size=SZ_SMALL,
        subregions=[B.sub_text(elem[:3].upper(), size=9,
                               anchor="INNER_BOTTOM", color=col + (1.0,)),
                    thin()])))

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
    LONGTERM.append(add(B.icon(
        f"RM Engraving {elem}", "RM Longterm", trig,
        ic(f"Weapon Engraving: {elem}"), size=SZ_SMALL,
        subregions=[B.sub_text(elem[:2].upper(), size=9,
                               anchor="INNER_TOPLEFT", color=col + (1.0,)),
                    B.sub_text("%p", size=9, anchor="INNER_BOTTOM"),
                    thin()])))

# Short buffs are emitted per spec (merged with that spec's target debuffs
# into one "what is up right now" row), so they are data here rather than
# displays.
SHORT_ENTRIES = [
    ("Frost Prison", (0.4, 0.8, 1.0), {"unit": "target", "helpful": False,
                                       "alt": ["Permafrost Rune", "Glacial Rune",
                                               "Cryobrand", "Frozen"]}),
    ("Runeshroud", (0.6, 0.5, 0.9), {}),
    ("Palm Sigil: Arcane", (0.75, 0.40, 0.95), {}),
    ("Palm Sigil: Earth", (0.62, 0.44, 0.20), {}),
    ("Palm Sigil: Fire", (0.95, 0.45, 0.15), {}),
    ("Palm Sigil: Frost", (0.40, 0.75, 1.00), {}),
    ("Palm Sigil: Water", (0.20, 0.55, 0.90), {}),
    ("Palm Sigil: Wind", (0.70, 0.90, 0.95), {}),
]

for name, col in [("Runes of Quickness", (0.4, 0.9, 1.0)),
                  ("Leyline Disturbance", (0.9, 0.7, 1.0)),
                  ("Runic Power", (1.0, 0.85, 0.4))]:
    LONGTERM.append(add(B.icon(
        f"RM Raid {name}", "RM Longterm",
        [B.aura_trigger([str(sid(name)), name], own_only=False)],
        ic(name), size=SZ_SMALL, subregions=[thin()])))



# Long-term buffs -- tattoo, weapon engravings, raid auras -- live at the very
# bottom. Fixed y rather than following each spec's stack, so they stay in one
# place no matter which spec is loaded. Glyphic's stack is the deepest (it has
# the glyph bar), so this clears that.
add(B.dynamicgroup("RM Longterm", "RM Core", LONGTERM, x=0, y=Y_LONG,
                   grow="HORIZONTAL", space=GAP))
CORE.append("RM Longterm")

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

def emit_bottom_block(spec_name, spec_key, out, procs, state=()):
    """Three stacked rows under the resource bar:

        1. Offense   -- damage cooldowns, Ley Lock + Leyline Adjustment last
        2. Utility   -- defensives and utility merged
        3. Buffs     -- short-window procs, active-only

    Glyphic keeps its glyph bar at Y_SEG so its block starts one band lower;
    the other two specs have nothing there and start at Y_SEG itself rather
    than leaving the gap empty. Returns the y for the DoT row.
    """
    have = {n for n, v in COOLDOWNS.items()
            if (spec_key in v["specs"] or not v["specs"])
            and _cd_secs(v["cd"]) <= 300 and n not in ELSEWHERE}
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

    y = Y_SEG - (CD_ROW_STEP if spec_key == "glyphic" else 0)

    for label, names in (("Offense", offense), ("Utility", utility)):
        ids = []
        for n in names:
            ids.append(add(cd_icon(f"RM {spec_name} {label} {n}",
                                   f"RM {spec_name} {label}", n, SZ_CD,
                                   charges=n in CHARGES, urgency=True)))
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
        add(B.dynamicgroup(f"RM {spec_name} {label}", f"RM {spec_name}", ids,
                           x=0, y=y, grow="HORIZONTAL", space=GAP))
        out.append(f"RM {spec_name} {label}")
        y -= CD_ROW_STEP

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
    cd_buffs = [(n, (1.0, 0.80, 0.30)) for n in offense
                if n not in named and n not in OFFENSIVE_TAIL]

    # ONE row for everything currently up: procs, running cooldowns, self
    # buffs and target debuffs. They are all active-only, so the row packs to
    # whatever is actually live rather than to its full length.
    out.append(buff_group(f"RM {spec_name} Buffs", f"RM {spec_name}",
                          procs + cd_buffs + list(state),
                          y=Y_BUFFS, size=SZ_BUFF, glow=True))
    return y


# =============================================================== 2. GLYPHIC# =============================================================== 2. GLYPHIC
G = []
G.append(cd_group("RM Glyphic Main", "RM Glyphic",
                  ["Glyphic Ruin", "Primordial Blast", "Thaumaturgy",
                   "Elemental Burst", "Runic Obliteration"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14))
G.append(mana_bar("RM Glyphic Mana", "RM Glyphic", Y_BAR,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5)))
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
# One row: what is up on me (short buffs) and on my target (debuffs).
add(spec_group("RM Glyphic", G, spec_gate("Glyphic")))

# ============================================================ 3. ENGRAVEMENT
E = []
E.append(cd_group("RM Engravement Main", "RM Engravement",
                  ["Runeblade", "Fist of the Ancients", "Runic Brand",
                   "Primordial Blast", "Runic Explosion"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14))
E.append(mana_bar("RM Engravement Mana", "RM Engravement", Y_BAR,
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
R.append(mana_bar("RM Riftblade Mana", "RM Riftblade", Y_BAR,
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
# One row: what is up on me (short buffs) and on my target (debuffs).
add(spec_group("RM Riftblade", R, spec_gate("Riftblade")))

# ==================================================================== ROOT
TOP = ["RM Core", "RM Glyphic", "RM Engravement", "RM Riftblade"]
root = B.group(ROOT, None, TOP, x=0, y=0)
root["url"] = ""

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
CLASS_TOKEN = "SPIRITMAGE"


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
    group_to_spec = {f"RM {k}": k for k in SPEC_KNOWN}

    def owning_spec(node):
        seen = set()
        while node is not None:
            pid = node.get("parent")
            if pid in group_to_spec:
                return group_to_spec[pid]
            if pid is None or pid in seen:
                return None
            seen.add(pid)
            node = by.get(pid)
        return None

    gated = anyof = classed = 0
    for c in children:
        if c.get("controlledChildren"):
            continue
        trigs = c["triggers"]
        own = [trigs[i]["trigger"] for i in sorted(i for i in trigs
                                                   if isinstance(i, int))]
        # "any of these spotted it" is the intent everywhere we use >1 trigger
        if len(own) > 1:
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
    return gated, anyof, classed


def assert_gated():
    """A leaf without a class gate is a bug, not a style choice.

    Cheap enough to run every build, and it is the only thing standing between
    us and shipping another pack that loads on all 21 classes.
    """
    bad_class, bad_known = [], []
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
    if bad_class or bad_known:
        for i in bad_class:
            print(f"  NO CLASS GATE:     {i}")
        for i in bad_known:
            print(f"  NO SPEC GATE:       {i}")
        raise SystemExit(
            f"refusing to emit: {len(bad_class)} leaves without a class gate, "
            f"{len(bad_known)} without a spec gate")


_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()

def restrict_to_spec():
    """Drop every display that does not belong to Core or the chosen spec."""
    by = {c["id"]: c for c in children}
    keep_roots = {"RM Core", f"RM {SPEC_TITLE}"}

    def kept(node):
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

    keep = [c for c in children if kept(c)]
    children[:] = keep
    root["controlledChildren"] = B.arr([r for r in TOP if r in keep_roots])


if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    s = B.export_string(root, children)
    name = f"runemaster-{SPEC_ONLY}" if SPEC_ONLY else "runemaster-all-specs"
    out = os.path.join(SP, f"{name}.txt")
    open(out, "w").write(s)
    print(f"{len(children)} displays, {len(s)} chars -> {out}")
    from collections import Counter as _C
    _dupes = []
    for _g in children:
        if _g["regionType"] != "dynamicgroup":
            continue
        _kids = [k for k in children
                 if k.get("parent") == _g["id"] and isinstance(k.get("displayIcon"), str)]
        _c = _C(k["displayIcon"] for k in _kids)
        for _art, _n in _c.items():
            if _n > 1:
                _dupes.append((_g["id"], _art.split("\\")[-1],
                               [k["id"] for k in _kids if k["displayIcon"] == _art]))
    if _dupes:
        print(f"  DUPLICATE ART IN {len(_dupes)} ROW(S):")
        for _r, _a, _w in _dupes:
            print(f"    {_r}: {_a} <- {_w}")
    else:
        print("  no repeated icon art within any row")
    print(f"  leaf gates: {_CLASSED} via load.class={CLASS_TOKEN}, "
          f"{_GATED} via load.spellknown, {_ANY} set to any-of")
    if UNRESOLVED:
        print(f"  UNRESOLVED ({len(UNRESOLVED)}): {UNRESOLVED}")
    else:
        print("  all tracked names resolved to spell ids")
