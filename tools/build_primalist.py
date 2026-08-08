"""Build the `Primalist [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Class CONTENT over the shared engine (`tools/wapack.py`) in the Chronomancer
shape -- no convergence flags. Requirements: `notes/requirements-primalist.md`.
Second FOUR-spec class through the pipeline (after Witch Hunter), and the first
with one spec of each role plus a pet spec: Geomancy (ranged caster DPS),
Grovekeeper (melee healer/support), Mountain King (tank), Wildwalker (melee
pet DPS). Roles are Sidekick-cited, pending in-game (resources/spec-roles.md).

        [ alerts: NO BOON / NO PET ]                  <- active-only
        [ on TARGET: your DoTs / your HoTs ]          <- active-only
        [ on me: procs, running CDs, buffs ]          <- active-only
              [  MAIN ROW - flush         ]
              [  rage + mana envelope     ]           <- fixed height
              [ offensive cooldowns       ]           <- wraps at 7
              [ defensive + utility       ]           <- wraps at 7
              [ long-term buffs           ]           <- active-only

Three things without an analogue in the earlier classes:

  * EVERY SPEC RUNS ON RAGE, mana second. The envelope is two power bars on
    all four specs: rage full-height nearest the main row, mana under it --
    full-height where the kit taxes mana hard (Geomancy "Mana pays for nearly
    every hard-hitting nuke", Grovekeeper "Mana fuels the heal and utility
    kit"), half-height `minor` where it is a side pool (Mountain King "a small
    secondary pool", Wildwalker "a secondary layer").

  * WILDWALKER IS A TAMED-BEAST PET SPEC. Any beast can be the pet (Spirit
    Beast Master, L10), so the NO PET alert asks the PET unit for the
    `Primalist Pet Scaling Aura` family rather than one creature's own aura --
    the Tinker Mechanics shape. The family ids are db.exil.es-sourced and not
    tooltip-verified (requirements §6). Pet Focus is deliberately NOT a bar:
    the player never spends it (requirements §3).

  * THE BOON FAMILY IS THE CLASS STANCE. "Only 1 Boon may be active at a
    time", and every spec's cited rotation opens with one -- so the class-wide
    alert is NO BOON, the exact NO SKIN shape from Pyromancer.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT. Never imported in game; the inventory roles were
# machine-proposed and bulk-cleared (recorded in buildlog-primalist.json), and
# requirements §6 lists what only the client can settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
# Filled after the first build's art survey; empty means every drawn id
# resolved art from the scrapes.
FALLBACK = {
    # db.ascension.gg serves no art for these ids (fetch_spell_icons "no art
    # upstream" + the build's own no-art survey); classic/wrath-client icons,
    # distinct within every row each name appears in. Sidekick's art for the
    # Seismic family is custom webp the 3.3.5 client does not ship.
    "Ancient of Lore": "inv_misc_herb_talandrasrose",
    "Ancient of War": "inv_misc_herb_ancientlichen",
    "Boon of the Turtle": "inv_misc_head_turtle_01",
    "Aftershock": "spell_nature_earthquake",
    "Seismic Tremor": "spell_nature_earthquake",
    "Seismic Crash": "spell_nature_stoneclawtotem",
    "Seismic Spike": "spell_nature_strengthofearthtotem02",
    "Seismic Smash": "spell_nature_rockbiter",
    "Seismic Grasp": "spell_nature_stranglevines",
    "Seismic Wave": "spell_nature_healingwavegreater",
    "Earthquake": "spell_nature_earthquake",
    # NOT inv_elemental_primal_earth: Geomolding's upstream art is that
    # texture and both share the merged Buffs row.
    "Primal Convergence": "spell_nature_earthelemental_totem",
    "Earthen Endurance": "spell_nature_unyeildingstamina",
    "Greater Earthen Endurance": "spell_nature_skinofearth",
    "Grove Instinct": "spell_nature_manaregentotem",
    "Greater Grove Instinct": "spell_frost_wizardmark",
    "Greater Primal Instinct": "ability_druid_ferociousbite",
    "Essence of Convergence": "spell_arcane_arcaneresilience",
    "Greater Essence of Convergence": "spell_arcane_arcanetorrent",
    "Essence of Dispersion": "spell_magic_lesserinvisibilty",
    "Greater Essence of Nature": "spell_nature_resistnature",
    "Tears of the Earthmother": "spell_nature_rejuvenation",
}
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own art
# for the spell.
OVERRIDE = {
    # Both Primal Weapon stances resolve to inv_axe_117 upstream and share the
    # Wildwalker long-term row -- the duplicate-art check fires on it. The
    # two-hander stance takes a two-hander icon.
    "Primal Weapon: Primal Might": "inv_axe_09",
}
# db.exil.es points at rows db.ascension.gg does not corroborate as the
# castable; corrections are name -> id, and an in-game tooltip outranks them
# (resources/in-game-verified.json). Both crossdb no-records resolved to
# other-id PASSIVES (Bear's Maw, Hammer of Life) and neither is drawn, so
# nothing needs correcting yet.
CROSSCHECK = {}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- Wildwalker
# renders four 44px main icons (its cited rotation is exactly four buttons),
# so row_w(4) = 182px and the rule `28w - 2 <= 1.2 * 182` allows w <= 7.8 -> 7.
# Confirmed against the built packs by tools/rowwidths.py. Do NOT copy this
# number to another class.
CLS = W.init("primalist", version=VERSION, prefix="PR", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# Abilities that hold charges rather than a plain cooldown. Counts are
# tooltip-read (db.exil.es renders no Charges row for them): Quake "2 Charges,
# 8 sec recharge", Rylak's Bite "2 Charges, 10 sec recharge", Rock Barrier
# "2 Charges, 20 sec recharge", Waters of Neptulon "2 Charges 10 sec recharge".
CHARGES = {"Quake": 2, "Rylak's Bite": 2, "Rock Barrier": 2,
           "Waters of Neptulon": 2}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text.
PROC_GLOW = {
    # "Aftershock: Your next Geode Barrage or Earthquake within 15 seconds is
    # now instant cast and costs -75% less" (Grove Training / Mountain Giant /
    # Seismic Smash all grant it).
    "Geode Barrage": ["Aftershock", "Lithic Lance"],
    "Earthquake": ["Aftershock"],
    # "Lithic Lance: Generating Earthshaping now has a % chance to transform
    # your next Geode Barrage within [8s] into Lithic Lance" -- the conversion
    # is the thing geomancy fishes for ("watching for the Lithic Lance
    # conversion"), and Geode Barrage is the button it lands on. Listed above
    # alongside Aftershock; the aura simply never exists off-spec.
    # "Wrath of Al'Akir: causing your next Wildclaw to strike two additional
    # times" (Fist of Al'Akir).
    "Wildclaw": ["Wrath of Al'Akir"],
}
# Of those, the ones whose proc also STACKS. None: Aftershock, the conversion
# and Wrath of Al'Akir are all single-shot windows.
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: party externals, enemy debuff CDs and ground bursts. A name
# missing from here costs nothing but a display that never shows; a name
# wrongly here hides a running cooldown, so only the unambiguous cases are
# listed.
NO_BUFF = {"Earthquake", "Magma Fissure", "Ruptured Earth", "Seismic Crash",
           "Seismic Spike", "Seismic Smash", "Neptulon's Wrath",
           "Primal Awakening", "Flourishing Growth", "Unstable Fracture",
           "Bring Me Their Bones"}

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own cooldown stack. Primalist's long-term content
# is inventory-driven, four families:
#
#   Boon      "Only 1 Boon may be active at a time" -- the class stance.
#   Instinct  30-min ally buffs, "one Instinct per Primalist" -- the blessing.
#   Weapon    Primal Weapon: * -- permanent weapon stances.
#   other     party auras (Molten Fervor, Ring of Life, Heart of the
#             Mountain...) and the 30-min ally stat buffs.
LONGTERM_COL = {
    "Boon": (0.95, 0.85, 0.45),
    "Instinct": (0.55, 0.75, 1.00),
    "Weapon": (0.60, 0.85, 0.75),
    "other": (0.75, 0.70, 1.00),
}


def _family(name):
    low = name.lower()
    if "boon" in low:
        return "Boon"
    if "instinct" in low:
        return "Instinct"
    if "primal weapon" in low:
        return "Weapon"
    return "other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `PR <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The four gates are the L10 Specialization passives, which
    arrive with the first talent point -- the levelling window without this
    band is days, not levels.
    """
    band = f"PR {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"PR {spec_name} Longterm {name}", band,
            # By id AND name: the Instincts and Endurances come in plain and
            # Greater pairs whose names contain each other, and several rows
            # are ranked -- matching either covers both failure shapes.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"PR {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Aftershock is the one proc three specs share; Earth's Rage is the
# class-tree movement/haste stack (Stonefaced); the two defensives get running
# state here because they live in the utility row, which cd_buffs does not
# derive from.
SHORT_ENTRIES = [
    ("Aftershock", (1.00, 0.85, 0.40), {}),
    ("Earth's Rage", (0.60, 0.85, 0.60), {}),
    ("Bearskin", (0.80, 0.70, 1.00), {}),
    ("Rock Barrier", (0.75, 0.75, 0.60), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# High and central, and invisible once you are buffed -- fires only on
# ABSENCE. Every spec's cited rotation opens with a Boon and they are mutually
# exclusive, so "no Boon at all" is a real, class-wide, actionable gap.
# Nagging per-Boon would be permanently on screen for the ones you
# deliberately did not take -- the exact failure Runemaster's reminder band
# had. The trigger matches ANY Boon by id or name, and the alert shows only
# when none of them is up.
ALERTS = []
_BOONS = sorted(n for n, a in ABILITIES.items()
                if a["default"] == "longterm" and _family(n) == "Boon")
if _BOONS:
    ALERTS.append(add(B.icon(
        "PR Alerts No Boon", "PR Alerts",
        [B.aura_trigger([str(ABILITIES[n]["id"]) for n in _BOONS] + _BOONS,
                        own_only=False, show_on="showOnMissing")],
        ic(_BOONS[0]), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text("NO BOON", size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])))

add(B.dynamicgroup("PR Alerts", "PR Core", ALERTS, x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
CORE.append("PR Alerts")
add(B.group("PR Core", ROOT, CORE, x=0, y=0))


def envelope(spec_name, bands, icons, mana="full"):
    """Rage + mana, two power bars in the fixed-height envelope (~-156..-186).

    Rage (power type 1 on 3.3.5) renders full-height nearest the main row on
    every spec -- it is the primary resource on all four (requirements §4).
    Mana renders under it: full-height with value text where the kit taxes it
    hard, half-height `minor` where it is a side pool. Every spec gets the
    same two-band depth, so no anchor below the envelope moves between specs.

    `icons` is the SPEC'S OWN main-row icon count: every resource band's
    width is derived from its own spec's main row, never from another spec's
    (rowwidths.py flagged exactly this on the first build).
    """
    w = row_w(icons)
    rage_col = (0.85, 0.30, 0.25, 1.0)
    mana_col = (0.30, 0.45, 0.95, 1.0)
    gid = f"PR {spec_name} Rage"
    add(B.aurabar(gid, f"PR {spec_name}", [B.power_trigger("player", 1)],
                  x=0, y=Y_BAR, w=w, h=BAR_H_STACKED, color=rage_col,
                  subregions=[B.sub_text("%p", size=10, anchor="INNER_RIGHT",
                                         x=-4, justify="RIGHT")]))
    bands.append(gid)
    gid = f"PR {spec_name} Mana"
    subs = [B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                       justify="RIGHT")] if mana == "full" else []
    add(B.aurabar(gid, f"PR {spec_name}", [B.power_trigger("player", 0)],
                  x=0, y=Y_SEG, w=w, h=BAR_H_STACKED if mana == "full" else 10,
                  color=mana_col, subregions=subs))
    bands.append(gid)


# =============================================================== 2. GEOMANCY
# Ranged caster DPS on the Earthshaping ramp. Press order is the cited
# rotation (sidekick-primalist-geomancy, 2026-08-07): Geode Barrage is "your
# main spammable filler" and builds Earthshaping, Seismic Tremor's ramping DoT
# stays rolling, Stoneshard is "your main spender", Terrasurge is the
# armor-shredding hit "once stacks are high", Eruption comes in "once
# Earthshaping is stacked". Lithic Lance is a PASSIVE conversion of Geode
# Barrage (the Stoke lesson) -- it glows the button instead of holding a slot.
G = []
G.append(cd_group("PR Geomancy Main", "PR Geomancy",
                  ["Geode Barrage", "Seismic Tremor", "Stoneshard",
                   "Terrasurge", "Eruption"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="geomancy"))
envelope("Geomancy", G, 5, mana="full")
# Your DoT and your armor shred on the target. Both ranked ids, so both match
# by name (dot_bars falls back automatically).
G.append(dot_bars("PR Geomancy Target", "PR Geomancy",
                  [("Seismic Tremor", (0.80, 0.60, 0.35), {}),
                   ("Terrasurge", (0.95, 0.75, 0.40), {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_G = emit_bottom_block("Geomancy", "geomancy", G,
                         [("Earthshaping", (0.95, 0.80, 0.45)),
                          ("Dream", (0.70, 0.85, 1.00)),
                          ("Geomolding", (0.85, 0.65, 0.40)),
                          ("Heavy Earth", (0.75, 0.60, 0.45)),
                          ("Cracking the Earth", (1.00, 0.55, 0.25)),
                          ("Thane's Rage", (0.95, 0.70, 0.35))],
                         SHORT_ENTRIES)
longterm_band("Geomancy", "geomancy", G, _y_G)
add(spec_group("PR Geomancy", G))


# ============================================================ 3. GROVEKEEPER
# THE HEALING SPEC (Sidekick: "a dual-resource melee-healer"). Raid frames
# stay out (VuhDo/Grid own that on 3.3.5a); the target band carries what YOU
# have on whoever you are targeting. Press order from the cited rotation:
# Hand of the Earthmother the moment someone drops low, Spirit Charge to close
# and top a spike target, Seismic Wave when the group is stacked, Sacred Grove
# as the emergency, Wildclaw as the filler that feeds Rage and Hammer of
# Life's splash. Tears of the Earthmother is a PASSIVE-provenance id
# (rank=Passive, dur -1 -- the Stoke shape) so it lives in the target band by
# name, never as a button.
K = []
K.append(cd_group("PR Grovekeeper Main", "PR Grovekeeper",
                  ["Hand of the Earthmother", "Spirit Charge", "Seismic Wave",
                   "Sacred Grove", "Wildclaw"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="grovekeeper"))
envelope("Grovekeeper", K, 5, mana="full")
# helpful=True: on a FRIENDLY target this shows what YOU have on them -- the
# rejuvenates and the damage-redirect window. All three are ranked or
# passive-provenance ids, so all three match by name.
K.append(dot_bars("PR Grovekeeper Target", "PR Grovekeeper",
                  [("Hand of the Earthmother", (0.55, 0.90, 0.55), {}),
                   ("Tears of the Earthmother", (0.40, 0.80, 0.95),
                    {"by_name": True}),
                   ("Earthmother's Binding", (0.90, 0.70, 0.95),
                    {"by_name": True})],
                  y=Y_TARGET, unit="target", helpful=True, refresh_at=4))
_y_K = emit_bottom_block("Grovekeeper", "grovekeeper", K,
                         [("Battleweaver", (0.95, 0.70, 0.35)),
                          ("Infusion of Neptulon", (0.45, 0.75, 0.95)),
                          ("Running on Instinct", (0.60, 0.90, 0.60))],
                         SHORT_ENTRIES)
longterm_band("Grovekeeper", "grovekeeper", K, _y_K)
add(spec_group("PR Grovekeeper", K))


# =========================================================== 4. MOUNTAIN KING
# THE TANK (Sidekick: "Solid main-tank for raid bosses"). Press order from the
# cited rotation: Quake on cooldown (2 charges / 8 sec, the most-pressed),
# Seismic Crash as the baseline Seismic for rage and Aftershock, Geode Barrage
# for threat (Fury of the Earthmother; 07/31 Earthbreaker threat note),
# Mountain Fury to cluster a pack, Mountain Hammer as the ranged stun opener
# and caster lockout (the spec has no interrupt), Rock Barrier pressed
# reactively -- the tank's in-row mitigation, the Noctis Blade precedent.
M = []
M.append(cd_group("PR Mountain King Main", "PR Mountain King",
                  ["Quake", "Seismic Crash", "Geode Barrage", "Mountain Fury",
                   "Mountain Hammer", "Rock Barrier"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="mountain-king"))
envelope("Mountain King", M, 6, mana="minor")
# The haste cut Quake maintains on the pack -- tank mitigation on the target.
# Ranked id, so the name carries the match.
M.append(dot_bars("PR Mountain King Target", "PR Mountain King",
                  [("Quake", (0.70, 0.60, 0.45), {})],
                  y=Y_TARGET, refresh_at=3))
_y_M = emit_bottom_block("Mountain King", "mountain-king", M,
                         [("Call of the Mountain", (0.60, 0.85, 0.60)),
                          ("Thane's Rage", (0.95, 0.70, 0.35)),
                          ("Mountain Mover", (0.75, 0.75, 0.60))],
                         SHORT_ENTRIES)
longterm_band("Mountain King", "mountain-king", M, _y_M)
add(spec_group("PR Mountain King", M))


# ============================================================= 5. WILDWALKER
# THE PET SPEC. A tamed beast ("animal spirit") fights beside a rage-fuelled
# melee bruiser. Press order from the cited rotation: Wildclaw is "your main
# filler strike", Rylak's Bite closes on its two charges, Totemic Smash is the
# biggest hit on its 6s cooldown, Primal Shred swaps in on 2+ mobs (pet cleave
# + bleed). The crit-bleed engine (Legacy of Rexxar) rides the buff row.
WW = []

# NO PET: the whole spec hangs on the beast being alive -- Primal Shred,
# Rylak's Bite, Throat Clamp and the Focus economy all need it. Trigger 1 asks
# the PET unit for the Primalist Pet Scaling Aura family and fires on absence;
# trigger 2 gates on knowing Spirit Beast Master (92148, the L10 passive that
# grants taming) so a character who cannot tame yet is not nagged. The family
# ids are db.exil.es names, not tooltip-verified -- requirements §6, the one
# alert in the pack built on unverified ground, flagged there rather than
# silently trusted.
_no_pet = B.icon(
    "PR Wildwalker Alerts No Pet", "PR Wildwalker Alerts",
    [B.aura_trigger(["524057", "805948", "Primalist Pet Scaling Aura",
                     "Primalist Pet Scaling (All)"], unit="pet",
                    own_only=False, show_on="showOnMissing"),
     B.spell_known_trigger(92148)],
    ic("Call Animal Spirit"), size=SZ_ALERT, desaturate=True,
    subregions=[B.sub_background(),
                B.sub_text("NO PET", size=10, anchor="INNER_BOTTOM",
                           color=(1, 0.35, 0.35, 1)),
                B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                             edge=EDGE),
                B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
NEEDS_ALL.add(_no_pet["id"])      # missing-aura AND spell-known, never "any"
add(_no_pet)
add(B.dynamicgroup("PR Wildwalker Alerts", "PR Wildwalker",
                   ["PR Wildwalker Alerts No Pet"], x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
WW.append("PR Wildwalker Alerts")

WW.append(cd_group("PR Wildwalker Main", "PR Wildwalker",
                   ["Wildclaw", "Rylak's Bite", "Totemic Smash",
                    "Primal Shred"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="wildwalker"))
envelope("Wildwalker", WW, 4, mana="minor")
# Your bleeds on the target: Torn to Shreds stacks 2 off Totemic Smash /
# Rylak's Bite (passive-applied, so by name), Primal Shred's own bleed rides
# its ranked castable.
WW.append(dot_bars("PR Wildwalker Target", "PR Wildwalker",
                   [("Torn to Shreds", (0.90, 0.35, 0.30), {"by_name": True}),
                    ("Primal Shred", (0.80, 0.45, 0.35), {})],
                   y=Y_TARGET, refresh_at=4))
# The pet's ramp rides the on-me row with unit="pet" (Rylak's Blessing); the
# Legacy of Rexxar procs land on the player.
_y_WW = emit_bottom_block("Wildwalker", "wildwalker", WW,
                          [("Misha's Rage", (0.90, 0.55, 0.30)),
                           ("Leokk's Fury", (0.55, 0.80, 0.95)),
                           ("Wrath of Al'Akir", (0.95, 0.85, 0.40)),
                           ("Rylak's Blessing", (0.70, 0.55, 0.95),
                            {"unit": "pet"}),
                           ("Lacerations", (0.90, 0.40, 0.40)),
                           ("Sharpened Claws", (0.75, 0.70, 0.55)),
                           ("Tribalism", (0.60, 0.85, 0.60))],
                          SHORT_ENTRIES)
longterm_band("Wildwalker", "wildwalker", WW, _y_WW)
add(spec_group("PR Wildwalker", WW))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. All four are the
# L10 Specialization passives -- a contiguous grant block like Witch Hunter's
# (92091-94), and Spell Known on a passive is proven ground on this fork
# (Chronomancer's Eternity Warper gate, verified in game).
SPEC_KNOWN = {
    "Geomancy": 92149,        # Earthshaping, the L10 passive
    "Grovekeeper": 92150,     # Grove Training, the L10 passive
    "Mountain King": 680395,  # Mountain Giant, the L10 passive
    "Wildwalker": 92148,      # Spirit Beast Master, the L10 passive
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
