"""Build the `Ranger [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Class CONTENT over the shared engine (`tools/wapack.py`) in the Chronomancer
shape -- no convergence flags. Requirements: `notes/requirements-ranger.md`.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your DoTs / debuffs ]            <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 9
              [ defensive + utility       ]           <- band 7, wraps at 9
              [ long-term buffs           ]           <- band 8, active-only

Three things specific to this class (notes/requirements-ranger.md):

  * ADVANTAGE IS ONE AURA STACKING TO 5. The combo-point-style secondary every
    spec builds and spends (aura 804329, duration -1, "Consumed by some
    abilities to boost their effectiveness"; its applier chain is 503830).
    Cap 5 is cited from the spender tooltips ("Spend Skullpiercer at 5
    Advantage"; "used with 5 stacks of Advantage"). It renders as a 5-cell
    `stack_bar`. FOCUS is the power resource under it -- see focus_bar().

  * THE QUIVER FAMILY IS THE CLASS'S STANCE. "Only 1 Quiver may be active at
    a time. Shares a cooldown with other Quivers" on every quiver tooltip, and
    the Archery rotation text opens with "Keep one Quiver active" -- so the
    quivers live in the long-term band and Archery gets a NO QUIVER alert.

  * NO PERMANENT PET. Farstrider's War Falcons / Dragonhawks are 6-12s
    fire-and-forget summons (the Maelstrom water-elemental shape), so there is
    no pet section and no pet alert; the player-side ramp they feed (Wingman,
    Coordination) rides the on-me row instead.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT (notes/production-run.md). Never imported in game;
# the inventory roles were machine-proposed and bulk-cleared (recorded in
# buildlog-ranger.json), and requirements §6 lists what only the client can
# settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
# FALLBACK is used only where NOTHING resolved upstream (the build's "no art
# upstream" list): 14 ranger spells carry inv_misc_questionmark on both DBs,
# and the choices below are all stock 3.3.5 hunter/rogue art so the client is
# guaranteed to have them.
FALLBACK = {
    "Quick Shot": "ability_hunter_quickshot",         # Serpent Sting's art
    "Skullpiercer": "ability_impalingbolt",           # Arcane Shot's art
    "Emerald Arrow": "inv_ammo_arrow_02",             # green-fletched arrow
    "Silent, But Deadly": "ability_trueshot",         # Trueshot Aura's art
    "Neurotoxin Arrow": "ability_theblackarrow",      # Silencing Shot's art
    "Crippling Shot": "spell_frost_stun",             # Concussive Shot's art
    "Blackjack": "ability_sap",
    "Bushwhack": "ability_cheapshot",
    "Throatpunch": "ability_kick",
    "Uncover Weakness": "ability_warrior_sunder",
    "Feral Pressure": "ability_hunter_misdirection",
    "Snapseed": "inv_misc_food_wildberries",
    "Wild Blessing": "spell_nature_resistnature",
    "Greater Footpad's Adaptation": "inv_misc_armorkit_04",
    "Horn of Alacrity": "inv_misc_horn_01",           # the haste Horn
}
OVERRIDE = {
    # ONLY deliberate choices belong here: an entry overrides the CLIENT's own
    # art for the spell. Both entries exist because the duplicate-art check
    # flagged the pair sharing one texture in one row.
    #
    # Brutal Shot and Power Shot both resolve to 5_archerskill31_border and
    # sit in the Archery offense row. Brutal Shot keeps the client art; Power
    # Shot (empowers your next 3 Quick Shots) takes the wrath Master Marksman
    # talent art, which appears in no other row of this pack.
    "Power Shot": "ability_hunter_mastermarksman",
    # Horn of Endurance and Ranger's Horn of Coordination both resolve to
    # inv_ascend_horn and share the Farstrider utility row. Endurance keeps
    # the client art; Coordination takes the stock horn, used nowhere else.
    "Ranger's Horn of Coordination": "inv_misc_horn_02",
}
# db.exil.es points at rows db.ascension.gg does not corroborate as the
# castable; corrections here are name -> id, and an in-game tooltip outranks
# them (resources/in-game-verified.json). Every entry's tooltip-read verdict
# is in requirements §0 and the inventory Notes.
CROSSCHECK = {
    # exiles 520580 is rank "Ravaging Venom Cast" -- a component. 803104 is
    # the official builder's grant and carries the full castable tooltip
    # (60 Focus, 20s cd, "Generates 2 Advantage ... 4 quick strikes").
    "Viper's Bite": 803104,
    # exiles 800251 is a bare "Summons a falcon." component. 804715 is the
    # builder grant with the full tooltip (30 Focus, 1 min cd, AoE slow).
    "Falcon's Call": 804715,
    # exiles 560425 is rank "Cleanser" ("cleanses dots"). 801435 is the class
    # tree's Knockout: 25 Focus, 18s cd incap that strips bleeds/poisons.
    "Knockout": 801435,
    # exiles 704341 is rank "Dispel Effect". 802839 is the class tree's
    # Survival Potion: 1 min cd poison/disease dispel-over-time.
    "Survival Potion": 802839,
    # exiles 520571 is rank "Leech" -- the leech component. 680276 is the
    # builder grant for the castable window.
    "Dirty Blades": 680276,
    # exiles 524872 is a thin stub; 524873 carries the full passive text.
    # (A passive: only ever referenced as a PROC_GLOW aura, never drawn.)
    "Silent, But Deadly": 524873,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- Brigand and
# Farstrider render five 44px main icons, so row_w(5) = 228px and the rule
# `28w - 2 <= 1.2 * 228` allows w <= 9.8 -> 9. Confirmed against the built
# packs by tools/rowwidths.py. Do NOT copy this number to another class.
CLS = W.init("ranger", version=VERSION, prefix="RG", cd_per_row=9,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# ---- the resource system ---------------------------------------------------
# Advantage: ONE player aura, stacks 0-5, duration -1. 804329 is the aura the
# applier chain triggers (503830 "Buffer" -> effect 64 -> 804329, db.exil.es
# JSON API); its description is the spender text verbatim. Requirements §1/§4.
ADVANTAGE = 804329
ADVANTAGE_CELLS = 5

# No ability in this class holds charges: no "N Charges" text appears in any
# tooltip of the reviewed inventory (Spread Shot does, and it is exiles-only
# and unshipped -- requirements §6.7).
CHARGES = {}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent tooltips. Aura ids for all three procs are
# unverified (requirements §6.2/§6.7): matched by id-or-name, and a glow wired
# to a wrong id never fires -- it reads as "nothing to do", never as a lie.
PROC_GLOW = {
    # "Direct Physical damage dealt now has an 8% chance to allow you to use
    # Deadshot regardless of the targets health for 8 sec" -- the execute
    # outside its own window, the archery must-press (524873).
    "Deadshot": ["Silent, But Deadly"],
    # "Instantly restores Focus and causes your next Assault to be guaranteed
    # to critically strike. Lasts 20 sec" -- press the dump inside the window.
    "Assault": ["Instinctual Combatant"],
    # "Falcon's Dive, Falconstrike, and Falcon's Call make your next Ranger's
    # Horn trigger no cooldown" (704172) -- a free Horn is the farstrider
    # jackpot; both cited Horns glow.
    "Horn of War": ["Farstrider's Command"],
    "Horn of Alacrity": ["Farstrider's Command"],
}
# None of the glow procs carries a stack count worth drawing on the button --
# the stacking states (Coordination, Wingman, Backstreet Justice) live in the
# on-me row where buff_group already shows stacks.
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: strikes, volleys and target-side marks. A name missing from
# here costs nothing but a display that never shows; a name wrongly here hides
# a running cooldown, so only the unambiguous cases are listed.
NO_BUFF = {"Brutal Shot", "Incendiary Shot", "Cannon Blast", "Quills",
           "Hydra's Bite", "Rusty Shiv", "Venom Blade", "Beastslayer",
           "Flank", "Skewer", "Falconmark", "Thalassian Brand",
           "Falcon Dive", "Falcon's Call"}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row. Ranger's long-term content is
# inventory-driven, three families:
#
#   Quiver      "Only 1 Quiver may be active at a time" -- the class stance,
#               one lights up while active.
#   Adaptation  the Adaptation stances plus the 30-min Footpad's/Woodsman's
#               ally buffs and Wild Blessing.
#   aura        the passive party auras worth a presence check: Guile of the
#               Cutthroat, Battle Prowess, Defense of the Ancients, Double
#               The Pace.
LONGTERM_COL = {
    "Quiver": (0.55, 0.95, 0.55),
    "Adaptation": (0.95, 0.85, 0.45),
    "aura": (0.60, 0.80, 1.00),
}


def _family(name):
    if "quiver" in name.lower():
        return "Quiver"
    if "adaptation" in name.lower() or name == "Wild Blessing":
        return "Adaptation"
    return "aura"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `RG <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The signature passives here arrive with the first talent
    point (level 10), so the window a levelling character goes without this
    band is days, not twenty levels.
    """
    band = f"RG {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"RG {spec_name} Longterm {name}", band,
            # By id AND name: the Adaptations come in plain and Greater pairs
            # whose names are prefixes of each other, several rows are ranked,
            # and Poison Quiver's only id is its target-debuff row -- matching
            # either covers all three failure shapes (requirements §6.3).
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"RG {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Elusive Character is the post-Elude damage window every spec has.
SHORT_ENTRIES = [
    ("Elusive Character", (0.70, 0.85, 1.00), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# NO QUIVER is ARCHERY's alert: its rotation text opens with "Keep one Quiver
# active", and a missing quiver is quiet throughput loss on every ranged hit.
# Two triggers, ALL: "no quiver aura is up" AND "you actually know a quiver"
# -- without the second, the alert is permanently on screen for a levelling
# character below the level that learns one, the retro's reminder-band
# failure. Searing Quiver (500103, dur -1, the verified castable) carries the
# Spell Known gate with exact=False so it spans ranks.
#
# The aura match lists every quiver name plus the known ids, any-of: whether
# each self-state aura reuses the castable's id is §6.3, and a name match is
# the half that survives either answer.
QUIVERS = ["Poison Quiver", "Searing Quiver", "Hunting Quiver",
           "Skirmisher's Quiver", "Light Quiver"]

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()


def archery_alerts(bands):
    band = "RG Archery Alerts"
    keys = [str(ABILITIES[q]["id"]) for q in QUIVERS if ABILITIES[q]["id"]]
    keys += QUIVERS
    d = B.icon(
        f"{band} No Quiver", band,
        [B.aura_trigger(keys, own_only=False, show_on="showOnMissing"),
         B.spell_known_trigger(sid("Searing Quiver"), exact=False)],
        ic("Searing Quiver"), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text("NO QUIVER", size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
    NEEDS_ALL.add(d["id"])      # missing-aura AND spell-known, never "any"
    add(d)
    add(B.dynamicgroup(band, "RG Archery", [d["id"]], x=0, y=Y_ALERT,
                       grow="HORIZONTAL", space=6))
    bands.append(band)


# Core carries nothing class-wide: the one reminder is archery-shaped (only
# Archery's rotation text makes the quiver mandatory) and no spec has a pet.
# The group still exists so the pack keeps the standard Core/spec skeleton.
add(B.group("RG Core", ROOT, CORE, x=0, y=0))


def focus_bar(gid, parent, y, w, h):
    """Focus is the power resource on every spec ('Focus is the primary
    resource, with Hunter-Focus or Rogue-Energy style regen' -- all three
    Resource paragraphs). WHICH UnitPower column the fork exposes it as is
    requirements §6.1 -- so the trigger reads the player's ACTIVE power
    (`use_powertype` off) rather than guessing a column: whatever bar the
    client shows under the character, this is that number.
    """
    t = B.power_trigger("player", 0)
    t["use_powertype"] = False
    add(B.aurabar(gid, parent, [t], x=0, y=y, w=w, h=h,
                  color=(0.85, 0.55, 0.25, 1.0),
                  subregions=[B.sub_text("%p", size=10, anchor="INNER_RIGHT",
                                         x=-4, justify="RIGHT")]))
    return gid


def envelope(spec_name, bands, icons=5):
    """Advantage cells + Focus bar -- the same two bands on all three specs,
    so the fixed-height envelope (~-156..-186) has no per-spec height
    variance. The WIDTH is locked to the spec's OWN main row (`icons`):
    Archery's execute makes its row six icons, the other two are five.

    Advantage sits NEAREST the main row because the finishers are played
    around it (the ordering rule in notes/layout-standard.md); no exact-count
    number is drawn -- five cells at cap five ARE the number.
    """
    w = row_w(icons)
    W.stack_bar(f"RG {spec_name} Advantage", f"RG {spec_name}", ADVANTAGE,
                ADVANTAGE_CELLS, (0.95, 0.75, 0.30), Y_BAR,
                B.health_trigger("player"), w, bands, h=14)
    bands.append(focus_bar(f"RG {spec_name} Focus", f"RG {spec_name}",
                           Y_SEG, w, BAR_H_STACKED))


# ================================================================ 2. ARCHERY
# Ranged Focus/Advantage builder-spender. Press order is the cited rotation
# (sidekick-page-ranger-archery-2026-08-07): builders Quick Shot / Hunting
# Shot, then the dungeon single-target priority "Precision Shot dump >
# Skullpiercer > Serrated Shot > Deadshot execute". Six icons -- the execute
# sits last, the widest main row in the pack.
A = []
archery_alerts(A)
A.append(cd_group("RG Archery Main", "RG Archery",
                  ["Quick Shot", "Hunting Shot", "Precision Shot",
                   "Skullpiercer", "Serrated Shot", "Deadshot"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="archery"))
envelope("Archery", A, icons=6)
# Your bleed and your poison on the target -- the two maintain states.
A.append(dot_bars("RG Archery Target", "RG Archery",
                  [("Serrated Shot", (0.90, 0.45, 0.35), {}),
                   ("Toxic Dart", (0.55, 0.90, 0.45), {})],
                  y=Y_TARGET, refresh_at=4))
_y_A = emit_bottom_block("Archery", "archery", A,
                         [("Silent, But Deadly", (1.00, 0.85, 0.40), {})],
                         SHORT_ENTRIES)
longterm_band("Archery", "archery", A, _y_A)
add(spec_group("RG Archery", A))


# ================================================================ 3. BRIGAND
# Melee dagger assassin. Press order from the cited rotation: Ravage first to
# lay the bleed, Wild Strike to build, then the spender chain "Assault/
# Viper's Bite/Skullpiercer" -- Viper's Bite ahead of Assault because the
# bleed it feeds on is up from the first press. Skewer (the 07/31 switch node
# with Viper's Bite) rides the offense row under its own Spell Known gate, so
# either build reads correctly.
BR = []
BR.append(cd_group("RG Brigand Main", "RG Brigand",
                   ["Ravage", "Wild Strike", "Viper's Bite", "Assault",
                    "Skullpiercer"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="brigand"))
envelope("Brigand", BR)
# The stacking-timer layer the Difficulty paragraph says the spec is played
# around: the Ravage bleed, Barbed Quills (4 stacks, choose-one talent --
# absent untalented, never fires), the Bounty spender-amp mark, Toxic Dart.
BR.append(dot_bars("RG Brigand Target", "RG Brigand",
                   [("Ravage", (0.90, 0.35, 0.30), {"by_name": True}),
                    ("Barbed Quills", (0.85, 0.55, 0.30), {"by_name": True}),
                    ("Bounty", (1.00, 0.80, 0.30), {"by_name": True}),
                    ("Toxic Dart", (0.55, 0.90, 0.45), {})],
                   y=Y_TARGET, refresh_at=3))
_y_B = emit_bottom_block("Brigand", "brigand", BR,
                         [("Backstreet Justice", (0.90, 0.70, 0.40), {})],
                         SHORT_ENTRIES)
longterm_band("Brigand", "brigand", BR, _y_B)
add(spec_group("RG Brigand", BR))


# ============================================================= 4. FARSTRIDER
# Augmentation-style ranged support. Press order from the cited rotation:
# Quick Shot builds, Skullpiercer / Emerald Arrow dump, Woodland Arrow chains
# the Horn cooldown down ("so a buff is active on nearly every pull"), Toxic
# Dart opens the DoT pressure. The Horns themselves are 1-min cooldowns in
# the offense row with Farstrider's Command glowing them when a falcon cast
# has made the next one free.
F = []
F.append(cd_group("RG Farstrider Main", "RG Farstrider",
                  ["Quick Shot", "Skullpiercer", "Emerald Arrow",
                   "Woodland Arrow", "Toxic Dart"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="farstrider"))
envelope("Farstrider", F)
# Your poison and your mark on the target. (Quel'dorei Poison is a PASSIVE
# rider on Woodland/Emerald Arrow -- not a refresh decision, not drawn.)
F.append(dot_bars("RG Farstrider Target", "RG Farstrider",
                  [("Toxic Dart", (0.55, 0.90, 0.45), {}),
                   ("Thalassian Brand", (0.95, 0.60, 0.30),
                    {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
# The falcon-fed player-side ramp: Coordination stacks while the birds are
# out, Wingman is the per-falcon damage cut (aura visibility is §6.4).
_y_F = emit_bottom_block("Farstrider", "farstrider", F,
                         [("Coordination", (0.60, 0.90, 0.80), {}),
                          ("Wingman", (0.70, 0.95, 0.90), {})],
                         SHORT_ENTRIES)
longterm_band("Farstrider", "farstrider", F, _y_F)
add(spec_group("RG Farstrider", F))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. The three L10
# Specialization passives are a contiguous block granted with the spec's
# first talent investment and never re-ranked -- read from the official
# talent builder (talents-ranger.json: the y=0, cost-free node per spec
# tree), exactly the "one spell unique to each spec" the gate wants. Spell
# Known on a passive is proven ground on this fork: Chronomancer's Eternity
# Warper (806301) gate was verified in game.
SPEC_KNOWN = {
    "Archery": 92115,      # Skirmisher, the L10 archery passive
    "Brigand": 92116,      # Ravager, the L10 brigand passive
    "Farstrider": 92117,   # Dream Flowers, the L10 farstrider passive
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
