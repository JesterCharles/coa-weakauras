"""Build the `Witch Doctor [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Seventh class through `notes/class-pack-process.md`, class CONTENT over the
shared engine (`tools/wapack.py`) in the Chronomancer shape -- no convergence
flags. Requirements: `notes/requirements-witch-doctor.md`.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your DoTs / your HoTs ]          <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 9
              [ defensive + utility       ]           <- band 7, wraps at 9
              [ long-term buffs           ]           <- band 8, active-only

Three things here have no analogue in the earlier classes:

  * BREWING IS A HEALER (spec-roles.md; "Solid dungeon healer" -- Sidekick).
    Its target band is dot_bars(helpful=True) -- YOUR HoTs/absorbs on the
    CURRENT target only, VuhDo owns raid frames -- and its main row is the
    cited healing rotation (Loa's Brew / Potion Toss / Spirit in a Bottle /
    Splash Potion / Mojo Beam).

  * NO PET, DESPITE 20+ SUMMON TOOLTIPS. Every summon is a totem-style drop
    ("Drop a ... Can only have 1 Ward active at a time") or a short temporary
    (War Golem 10 s, Shadow Puppets, Serpent Wards 15 s), so the player-side
    BUTTON is the tracking surface -- cooldown icons, no unit="pet" rows and
    no NO-PET alert. The Avatar-Dinosaur layer is real but appears in no
    cited rotation and is excluded (requirements §3, §6.9).

  * THE SPIRIT BANK IS NOT DRAWN. Voodoo and Shadowhunting bank "Spirits"
    (cap 5) but no scrape yields a player-aura id for the count, and Spirits
    may be summoned entities rather than an aura (requirements §6.1). A bar
    on a guessed id fails silently, so no bar ships until an in-game read.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT. Never imported in game; the inventory roles were
# machine-proposed and bulk-cleared (recorded in buildlog-witch-doctor.json),
# and requirements §6 lists what only the client can settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {}
OVERRIDE = {
    # ONLY deliberate choices belong here: an entry overrides the CLIENT's own
    # art for the spell. Filled where the build's duplicate-art check fired --
    # each pair shares art upstream and sits in the same row:
    #
    # Brew Cocktail / Brew Stew both draw inv_drink_04 in every scrape and are
    # both brewing utility. The stew is the FOOD, so it gets the meat.
    "Brew Stew": "inv_misc_food_15",
    # Voodoo's utility row: Serene Idol and Dark Idol resolve to the same
    # ability_creature_cursed_04 art. The serene one takes the calm-blue totem
    # icon; Dark Idol keeps the scraped art.
    "Serene Idol": "spell_nature_brilliance",
    # Death Draught and Mass Allcure Elixir share nhi_arcanepotion_border in
    # three utility rows. Death Draught is the feign death, so it takes the
    # classic feign icon and the elixir keeps the potion art.
    "Death Draught": "ability_rogue_feigndeath",
    # Concoct Rejuvenating Mojo / Mojo Cauldron share inv_ascend_potion_14 in
    # the brewing utility row. The cauldron is the raid dispenser, so it takes
    # the Brewfest cask (a real 3.3.5 texture).
    "Mojo Cauldron": "inv_cask_01",
    # Major / plain Rejuvenating Mojo share the zandalari urn in the brewing
    # utility row. The Major one takes the classic healing-potion bottle.
    "Major Rejuvenating Mojo": "inv_potion_54",
    # Serpent Ward / Viper Ward share spell_nature_guardianward in the
    # shadowhunting offense row. The viper takes the wrath viper aspect.
    "Viper Ward": "ability_hunter_aspectoftheviper",
}

# db.exil.es points at rows db.ascension.gg does not corroborate as the
# castable; corrections here are name -> id, and an in-game tooltip outranks
# them (resources/in-game-verified.json). Every entry was resolved by a name
# re-ask + tooltip read on db.ascension.gg 2026-08-07 (requirements §0, §6.6).
CROSSCHECK = {
    # exiles 524670 is a zero-everything component; 802100 is the castable
    # (8% mana, 1 min cd, 15 s +15% damage window).
    "Veil of Darkness": 802100,
    # exiles 806294's rank is literally "Deprecated"; 807743 is the castable
    # interrupt (25% mana, 28 s cd, 4 s silence).
    "Spirit Shock": 807743,
    # exiles 572899 is the Summon component; 681222 is the castable
    # (28% mana, 40 s cd, 4 wards for 15 s).
    "Call of Sseratus": 681222,
    # exiles 504418 has cd 0; 804684 is the castable (11% mana, 3 MIN cd,
    # 15 s zone) -- which is also why it is a healing COOLDOWN, not upkeep.
    "Voodoo Cauldron": 804684,
    # exiles 801665 has cd 0; 802719 is the castable (5 min cd immunity zone).
    "Big Bad Voodoo": 802719,
    # exiles' primary row 503712 is the Specialization talent; 504582 is the
    # castable AoE (1.8 s cast, collects a Spirit, -3 s Spirit Glaive cd).
    "Spirit Volley": 504582,
    # exiles 801673 self-describes as "Deprecated" (the Manastorm smell);
    # ascension 504588 is a live 8 s cd leech glaive. Snapshot tooltips
    # disagree on the text -- requirements §6.6.
    "Umbral Glaive": 504588,
    # exiles maps the name to 500993; the OFFICIAL brewing tree grants 706369
    # (talents-witch-doctor.json), which is the id the character learns.
    "Spirit Link Idol": 706369,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- every spec
# here renders five 44px main icons, so row_w(5) = 228px and the rule
# `28w - 2 <= 1.2 * 228` allows w <= 9.8 -> 9. Confirmed against the built
# packs by tools/rowwidths.py. Do NOT copy this number to another class.
CLS = W.init("witch-doctor", version=VERSION, prefix="WD", cd_per_row=9,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# No ability in any scrape carries charges (db.exil.es renders no Charges row
# for this class and no talent text grants one).
CHARGES = {}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text.
PROC_GLOW = {
    # "Summoning a Serpent Ward or Spirit now increases the damage of your
    # next Spirit Glaive or Spirit Eclipse by %, stacking times" (The True
    # Spirit, 802268) -- both spenders light up while the stack is banked.
    "Spirit Glaive": ["The True Spirit"],
    "Spirit Eclipse": ["The True Spirit"],
}
# The True Spirit stacks to 5, so the count is drawn on the buttons it
# empowers rather than as a bar of its own.
PROC_STACKS = {"Spirit Glaive", "Spirit Eclipse"}

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: target debuffs, ground drops and summons. A name missing from
# here costs nothing but a display that never shows; a name wrongly here hides
# a running cooldown, so only the unambiguous cases are listed.
NO_BUFF = {"Shadowflare", "Umbral Glaive", "Spirit Volley", "Veil of Darkness",
           "Mimic Ward", "Dark Effigy", "Viper Ward", "Serpent Ward",
           "Voodoo Puddle", "Voodoo Cauldron", "Hex of Malice"}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# Core carries nothing class-wide: the class has no imbue/engraving-shaped
# prepull kit, no permanent pet, and requirements §5 found no missing-buff
# alert that would not sit on unverified ground (§6.3's Cauldron idea is a
# feedback question, not a display). The group still exists so the pack keeps
# the standard Core/spec skeleton.
add(B.group("WD Core", ROOT, CORE, x=0, y=0))

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates(). None
# needed this build -- no pet alert, no window-paired icons.
NEEDS_ALL = set()

# ---- long-term buffs --------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row. Witch Doctor's long-term content
# is inventory-driven, three families:
#
#   Wujus     ally-targeted persistent buffs, "1 Wuju active on a target at a
#             time" -- the class's Edict-equivalent.
#   Auras     party auras that "do not stack with similar effects" (Strength
#             of Da Loa, Darkspear Traditionalist, Dark Loa's Blessing).
#   other     hedged self-buff castables (Juju, Staff of the Coven, Devotion
#             of Gonk) -- active-only, so a wrong read never renders.
LONGTERM_COL = {
    "Wuju": (0.95, 0.85, 0.45),
    "Aura": (0.55, 0.75, 1.00),
    "other": (0.75, 0.70, 1.00),
}


def _family(name):
    if "wuju" in name.lower():
        return "Wuju"
    if name in ("Strength of Da Loa", "Darkspear Traditionalist",
                "Dark Loa's Blessing"):
        return "Aura"
    return "other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `WD <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The levelling tradeoff is the standing one -- the L10 spec
    passives gating each spec arrive with the first talent point.
    """
    band = f"WD {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"WD {spec_name} Longterm {name}", band,
            # By id AND name: the Wujus come in plain and Greater pairs whose
            # names are suffixes of each other, and several rows are ranked --
            # matching either covers both failure shapes.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"WD {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide defensive windows, merged per spec into that spec's "what is up
# right now" row. These are DEFENSIVE-row cooldowns, and cd_buffs only derives
# running-state icons from the OFFENSE row -- without an entry here their only
# cue would be a swipe that reads "unavailable" rather than "active".
SHORT_ENTRIES = [
    ("Vol'jin's Vigil", (0.55, 0.85, 0.75), {}),
    ("Dire Rage", (0.90, 0.35, 0.35), {}),
    ("Big Bad Voodoo", (0.70, 0.50, 0.95), {}),
]


def envelope(spec_name, bands):
    """Mana only, all three specs (Sidekick Resource line on each page), so
    the fixed-height envelope holds one full-height bar. The Spirit bank is
    deliberately NOT drawn -- requirements §6.1: no readable aura id."""
    bands.append(mana_bar(f"WD {spec_name} Mana", f"WD {spec_name}",
                          Y_BAR_SOLO, (0.30, 0.45, 0.95, 1.0), w=row_w(5)))


# ================================================================== 2. VOODOO
# Shadow/Nature caster whose support is pressure. Press order is the cited
# rotation (sidekick-witch-doctor-voodoo, 2026-08-07): Bad Juju on cooldown,
# Shadow Puppets on cooldown (Spirit + De Other Side stacks), Hexfire to cash
# in ("Jin'do's Wrath and Hexfire" -- and Jin'do's Wrath is a PASSIVE that
# empowers Hexfire, so the press is Hexfire), Hex of Malice kept rolling,
# Malefic Wrath as the filler nuke.
VD = []
VD.append(cd_group("WD Voodoo Main", "WD Voodoo",
                   ["Bad Juju", "Shadow Puppets", "Hexfire", "Hex of Malice",
                    "Malefic Wrath"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="voodoo"))
envelope("Voodoo", VD)
# Your DoTs on the target: the Hex of Malice maintain ("Bad Juju, Jin'do's
# Wrath and Hexfire give you nothing" without it), the Puppeteer's Threads
# the L10 passive leaves (Hexfire detonates them), and the Veil of Darkness
# damage-amp window. Threads and Veil match by name: Threads' row id is the
# passive (92084) and Veil's on-target aura id is uncaptured.
VD.append(dot_bars("WD Voodoo Target", "WD Voodoo",
                   [("Hex of Malice", (0.70, 0.50, 0.95), {}),
                    ("Puppeteer's Threads", (0.60, 0.85, 1.00),
                     {"by_name": True}),
                    ("Veil of Darkness", (0.90, 0.35, 0.85),
                     {"by_name": True})],
                   y=Y_TARGET, refresh_at=4))
_y_VD = emit_bottom_block("Voodoo", "voodoo", VD,
                          [("De Other Side", (0.80, 0.55, 1.00))],
                          SHORT_ENTRIES)
longterm_band("Voodoo", "voodoo", VD, _y_VD)
add(spec_group("WD Voodoo", VD))


# ================================================================= 3. BREWING
# THE HEALER (spec-roles.md). Press order from the cited rotation: Loa's Brew
# as the primary filler, instant Potion Toss whenever up, Spirit in a Bottle
# on tank/cleave (heal + chip), Splash Potion for stacked groups, Mojo Beam as
# the channel-weave anchor. Voodoo Cauldron turned out to be a 3 MIN cooldown
# (804684), so it sits in the healing-cooldown row, not the main row.
BR = []
BR.append(cd_group("WD Brewing Main", "WD Brewing",
                   ["Loa's Brew", "Potion Toss", "Spirit in a Bottle",
                    "Splash Potion", "Mojo Beam"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="brewing"))
envelope("Brewing", BR)
# YOUR HoTs and absorbs on YOUR TARGET -- the healing band the spec-role
# decision turns on. All by name: the Potion Toss-applied effects (Jungle
# Shrooms HoT, Frog Bones absorb, Bloodthistle leech) resolve to component-
# smell ids in every scrape (requirements §6.2); Mark of Pa'ku stacks when
# you directly heal the marked ally.
BR.append(dot_bars("WD Brewing Target", "WD Brewing",
                   [("Jungle Shrooms", (0.45, 0.90, 0.55), {"by_name": True}),
                    ("Frog Bones", (0.55, 0.75, 1.00), {"by_name": True}),
                    ("Bloodthistle", (0.90, 0.35, 0.35), {"by_name": True}),
                    ("Mark of Pa'ku", (0.95, 0.80, 0.45), {"by_name": True})],
                   y=Y_TARGET, helpful=True, refresh_at=4))
_y_BR = emit_bottom_block("Brewing", "brewing", BR,
                          [],
                          SHORT_ENTRIES)
longterm_band("Brewing", "brewing", BR, _y_BR)
add(spec_group("WD Brewing", BR))


# =========================================================== 4. SHADOWHUNTING
# Ranged/RAP hybrid. Press order from the cited rotation: Reclamation (moving
# filler, banks a Spirit), Malefic Arrow (applies Hex of Death), Spirit Glaive
# (Shadow Resistance cut), Spirit Eclipse (the Spirit dump), Call of Sseratus
# (the 15 s ward pack -- its swipe IS the "wards expiring" cue). Burst:
# Veil of Darkness -> Mimic Ward -> Shadow Avatar -> Fool's Play, all in the
# offense row.
SH = []
SH.append(cd_group("WD Shadowhunting Main", "WD Shadowhunting",
                   ["Reclamation", "Malefic Arrow", "Spirit Glaive",
                    "Spirit Eclipse", "Call of Sseratus"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="shadowhunting"))
envelope("Shadowhunting", SH)
# The maintains: Hex of Malice (spread by Shadowflare, re-upped by Umbral
# Glaive), Hex of Death (the heal-absorb Malefic Arrow leaves -- passive-
# applied, by name), and the Veil window.
SH.append(dot_bars("WD Shadowhunting Target", "WD Shadowhunting",
                   [("Hex of Malice", (0.70, 0.50, 0.95), {}),
                    ("Hex of Death", (0.90, 0.35, 0.35), {"by_name": True}),
                    ("Veil of Darkness", (0.90, 0.35, 0.85),
                     {"by_name": True})],
                   y=Y_TARGET, refresh_at=4))
_y_SH = emit_bottom_block("Shadowhunting", "shadowhunting", SH,
                          [("The True Spirit", (1.00, 0.85, 0.40)),
                           ("Voodoo Hunger", (0.60, 0.60, 0.95))],
                          SHORT_ENTRIES)
longterm_band("Shadowhunting", "shadowhunting", SH, _y_SH)
add(spec_group("WD Shadowhunting", SH))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. The three L10 spec
# passives are a contiguous block (92084/92085/92086), the same shape as
# Witch Hunter's 92091-94; Spell Known on a passive is proven ground on this
# fork (Chronomancer's Eternity Warper gate, verified in game).
SPEC_KNOWN = {
    "Voodoo": 92084,          # Puppeteer's Threads, the L10 passive
    "Brewing": 92085,         # Cauldron Brewer, the L10 passive
    "Shadowhunting": 92086,   # Shadowhunter, the L10 passive
}
W.configure(needs_all=NEEDS_ALL, spec_known=SPEC_KNOWN)

_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()
W.chain_ladder()
W.settle_icon_source()
if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    W.finish((_GATED, _ANY, _CLASSED))
