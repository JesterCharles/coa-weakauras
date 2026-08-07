"""Build the `Stormbringer [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Fourth class through `notes/class-pack-process.md`, class CONTENT over the
shared engine (`tools/wapack.py`) in the Chronomancer shape -- no convergence
flags. Requirements: `notes/requirements-stormbringer.md`.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your DoTs / debuffs ]            <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 9
              [ defensive + utility       ]           <- band 7, wraps at 9
              [ long-term buffs           ]           <- band 8, active-only

Three things here have no analogue in the earlier classes:

  * STATIC IS ONE AURA STACKING TO 100. The class meter (803102, "Stack 100",
    decays out of combat -- db.exil.es) is a single aura whose stack count IS
    the resource. It renders as a ten-cell `stack_bar` at `step=10` -- each
    cell is ten Static, so the 20/40/50 spend thresholds read as cell counts --
    with the exact number drawn beside the bar off the same aura trigger.
    No warn tint at the cap yet: what 100 Static actually does is
    requirements §6.1, and a warning built on an unverified penalty would be
    a cue that lies.

  * WIND IS THE FIRST PERMANENT-PET SPEC. The Air Elemental is summoned once
    and everything hangs on it staying up ("its death or dispel takes your
    damage with it" -- Sidekick). So Wind gets a NO PET alert in its own
    alert band, and its proc row tracks the PET's state (Invigoration stacks,
    Unshackle, Gift of Air) with `unit="pet"` aura triggers.

  * MAELSTROM'S WHOLE LOOP IS A TALENT TRANSFORM. Tempest Sovereign (560020)
    turns Shock into Brine (807105) and Call Lightning into Torrential Wrath
    (804017) -- different spells, not modifiers. The Maelstrom rows track the
    REPLACEMENT ids directly; base Shock/Call Lightning never appear on this
    spec, so there is nothing to swap at runtime. Conductive, the builder
    meter Brine stacks, gets its own six-cell segment row (cap 6 per
    db.exil.es 92098; the 07/31 changelog says "stacks higher" -- §6.4).

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt and the group name. WeakAuras dedupes imports
# on uid, so a rebuilt pack MUST carry a different salt or the client treats it
# as already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT. Never imported in game; the inventory roles were
# machine-proposed and bulk-cleared (recorded in buildlog-stormbringer.json),
# and requirements §6 lists what only the client can settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {}
OVERRIDE = {
    # ONLY deliberate choices belong here: an entry overrides the CLIENT's own
    # art for the spell. Populated below as the duplicate-art check demands.
    #
    # Volt and Storm Chaser both resolve to shaman_pvp_staticcling upstream
    # and can sit in the same in-play view (Volt in the lightning main row,
    # Storm Chaser in the on-me row). Volt keeps the art the game draws on the
    # button; the PROC borrows Dark Skies-adjacent storm art that appears in
    # no row of this pack.
    "Storm Chaser": "inv_fish_stormray",
    # Barometric Pressure and Clear Skies both resolve to
    # achievement_zone_deadwindpass upstream and share the Wind long-term row.
    # Clear Skies keeps the art the game draws; the Pressure -- a casting-slow
    # air-thickening aura -- takes the stock wotlk winds art, which appears in
    # no other row of this pack.
    "Barometric Pressure": "spell_frost_arcticwinds",
}
# db.exil.es points at rows db.ascension.gg does not corroborate as the
# castable; corrections here are name -> id, and an in-game tooltip outranks
# them (resources/in-game-verified.json).
CROSSCHECK = {
    # db.exil.es's only "Stormcloud" row is 572128, rank "Proc" -- the cloud
    # effect, the documented wrong-id smell. db.ascension.gg 801859 is the
    # castable: 42% base mana, instant, 1 min cooldown, and its tooltip is the
    # talent text verbatim ("Summon a cloud above an enemy target's head for
    # 15 sec ... Torrential Wrath ... causes a Geyser to erupt").
    "Stormcloud": 801859,
    # db.exil.es's Freewind row 548621 is rank "Damage" -- the cone's damage
    # component. db.ascension.gg 801873 is the castable (37% base mana, 1 min
    # cooldown, the full line-gust tooltip). The same search also settled what
    # Freewind IS: 707359 is a passive that "Transforms Eye of the Storm into
    # Freewind" -- a Wind talent transform, recorded in requirements §2.
    "Freewind": 801873,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- every spec
# here renders five 44px main icons, so row_w(5) = 228px and the rule
# `28w - 2 <= 1.2 * 228` allows w <= 9.8 -> 9. Confirmed against the built
# packs by tools/rowwidths.py. Do NOT copy this number to another class.
CLS = W.init("stormbringer", version=VERSION, prefix="SB", cd_per_row=9,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# ---- the resource system ---------------------------------------------------
# Static: ONE player aura, stacks 0-100, duration -1, decays out of combat.
# Confirmed on db.exil.es/spell/803102 ("Stack 100"); requirements §4.
STATIC = 803102
STATIC_CELLS = 10          # one cell per ten Static; spend costs are tens
# Conductive: the Maelstrom builder meter. Cap 6 per db.exil.es 92098; the
# 07/31 changelog says "no longer consumes, stacks higher", so the cap is an
# open question (§6.4) -- six cells until the client says otherwise. Matched
# BY NAME because the stacking aura's own id is unverified.
CONDUCTIVE_CELLS = 6

# Abilities that hold charges rather than a plain cooldown. Counts come from
# the db.exil.es tooltips ("3 Charges, 10 sec recharge" etc.); db.exil.es
# renders no Charges row, so these are tooltip-read, not audit-derived.
CHARGES = {
    "Gale": 3,             # "3 Charges, 10 sec recharge"
    "Updraft": 2,          # "2 Charges, 10 sec recharge"
    "Stormbreaker": 3,     # "3 Charges, 12 sec recharge"
    "Raging Zephyr": 3,    # "3 Charges, 35 sec recharge"
}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text.
PROC_GLOW = {
    # "Resets the cooldown of Electrocute and makes your next usable
    # regardless of the target's health percentage" -- the execute button
    # outside its own window, the spec's must-press (Sidekick, lightning).
    "Electrocute": ["Electrocutioner"],
    # "Damage dealt by Forked Lightning has a 5% chance to transform it into
    # Thunder Wave" -- the proc aura's id is unverified (§6.5), name-matched.
    "Forked Lightning": ["Thunder Wave"],
    # "Every 30 sec, your next Storm Alert or Torrential Wrath is instant
    # cast." Torrential Wrath is the button that matters; Storm Alert is a
    # utility fear and glowing it would say "press me" about crowd control.
    "Torrential Wrath": ["Predictable Weather"],
    # "causing your next Summon: Air Elemental to be instant cast and cost no
    # mana" -- the banked recovery window after the pet dies (Sidekick, wind).
    "Summon: Air Elemental": ["Lexicon of Servitude"],
}
# None of the glow procs carries a stack count worth drawing on the button --
# the stacking states (Dark Skies, Electrical Charge, Kinetic Energy,
# Invigoration) live in the on-me row where buff_group already shows stacks.
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: ground zones and target debuffs. A name missing from here costs
# nothing but a display that never shows; a name wrongly here hides a running
# cooldown, so only the unambiguous cases are listed.
NO_BUFF = {"Conjure Storm", "Conjure Rainstorm", "Stormcloud"}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row. Stormbringer's long-term content
# is inventory-driven, three families:
#
#   Aegis      "Can only have 1 Aegis up at a time" -- one per spec (Shocking /
#              Whirlwind / Tempest), hour-class self buffs.
#   Calls      Storm Mantle / Call of the Wind / Call of the Storm and their
#              Greater raid versions -- 30-minute empowerments. Wind's and
#              Maelstrom's are mutually exclusive by tooltip.
#   Pressure   Wind's four "Only 1 Pressure spell can be active at a time"
#              persistent auras.
#   other      Electrifying Aura ("Keep Electrifying Aura active" -- Sidekick)
#              and Clear Skies, persistent party auras.
LONGTERM_COL = {
    "Aegis": (0.95, 0.85, 0.45),
    "Call": (0.55, 0.75, 1.00),
    "Pressure": (0.60, 0.85, 0.75),
    "other": (0.75, 0.70, 1.00),
}


def _family(name):
    if "aegis" in name.lower():
        return "Aegis"
    if "call of the" in name.lower() or name == "Storm Mantle":
        return "Call"
    if "pressure" in name.lower():
        return "Pressure"
    return "other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `SB <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The levelling tradeoff is the standing one -- the signature
    passives here arrive with the first talent point, so the window a
    levelling character goes without this band is days, not twenty levels.
    """
    band = f"SB {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"SB {spec_name} Longterm {name}", band,
            # By id AND name: the Calls come in plain and Greater pairs whose
            # names are prefixes of each other, and several Aegis rows are
            # ranked -- matching either covers both failure shapes.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"SB {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row.
SHORT_ENTRIES = [
    ("Predictable Weather", (0.70, 0.85, 1.00), {}),
    ("Storm Chaser", (1.00, 0.85, 0.40), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# NO AEGIS is PER SPEC, not Core. Each spec learns exactly one Aegis, so the
# absence trigger pairs with a Spell Known gate on that spec's own Aegis --
# without it the alert is permanently on screen for every character below the
# level that learns theirs, which is the retro's reminder-band failure.
# Two triggers, ALL: "the buff is missing" AND "you actually know the spell".
#
# Ranked Aegis ids take exact=False on the Spell Known trigger so the check
# spans ranks (the by-name resolution path; tools/build_diag.py pack 6 is the
# in-game check for that shape).
AEGIS = {
    "Lightning": ("Shocking Aegis", 680316),
    "Wind": ("Whirlwind Aegis", 680282),
    "Maelstrom": ("Tempest Aegis", 680334),
}


def spec_alerts(spec_name, bands, extra=()):
    """The per-spec alert band: NO AEGIS, plus anything the spec adds."""
    band = f"SB {spec_name} Alerts"
    aegis_name, aegis_id = AEGIS[spec_name]
    out = []
    d = B.icon(
        f"{band} No Aegis", band,
        [B.aura_trigger([str(aegis_id), aegis_name], own_only=False,
                        show_on="showOnMissing"),
         B.spell_known_trigger(aegis_id, exact=False)],
        ic(aegis_name), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text("NO AEGIS", size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
    NEEDS_ALL.add(d["id"])      # missing-aura AND spell-known, never "any"
    out.append(add(d))
    out.extend(extra)
    add(B.dynamicgroup(band, f"SB {spec_name}", out, x=0, y=Y_ALERT,
                       grow="HORIZONTAL", space=6))
    bands.append(band)


# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

# Core carries nothing class-wide: every reminder here is spec-shaped (each
# spec has its own Aegis, only Wind has a pet). The group still exists so the
# pack keeps the standard Core/spec skeleton.
add(B.group("SB Core", ROOT, CORE, x=0, y=0))


def envelope(spec_name, bands, maelstrom=False):
    """Static + mana -- plus Conductive on Maelstrom, three bands in the same
    fixed-height envelope (~-156..-186), so every anchor below is unchanged.

    Static sits NEAREST the main row because it is the thing the rotation is
    played around (the ordering rule in notes/layout-standard.md). The exact
    count is drawn at the bar's right edge off the same aura -- cells answer
    "can I afford the spender", the number answers "how close is the cap".
    """
    w = row_w(5)
    if not maelstrom:
        W.stack_bar(f"SB {spec_name} Static", f"SB {spec_name}", STATIC,
                    STATIC_CELLS, (0.55, 0.85, 1.00), Y_BAR,
                    B.health_trigger("player"), w, bands, h=14,
                    step=100 // STATIC_CELLS)
        bands.append(mana_bar(f"SB {spec_name} Mana", f"SB {spec_name}",
                              Y_SEG, (0.30, 0.45, 0.95, 1.0), w=w,
                              h=BAR_H_STACKED))
        _static_count(spec_name, Y_BAR, 14, bands)
        return
    # Maelstrom: three bands share the envelope, so each is thinner.
    W.stack_bar(f"SB {spec_name} Static", f"SB {spec_name}", STATIC,
                STATIC_CELLS, (0.55, 0.85, 1.00), -160,
                B.health_trigger("player"), w, bands, h=10,
                step=100 // STATIC_CELLS)
    bands.append(mana_bar(f"SB {spec_name} Mana", f"SB {spec_name}", -171,
                          (0.30, 0.45, 0.95, 1.0), w=w, h=10))
    W.stack_bar(f"SB {spec_name} Conductive", f"SB {spec_name}", "Conductive",
                CONDUCTIVE_CELLS, (0.45, 0.80, 0.95), -182,
                B.health_trigger("player"), w, bands, h=8)
    _static_count(spec_name, -160, 10, bands)


def _static_count(spec_name, y, h, bands):
    """The exact Static number, right of the cell bar, same aura trigger.

    Zero Static means the aura is absent, so the number simply is not there --
    which reads correctly, and costs no inverse machinery.

    ⚠️ The id MUST enter the spec group's child list (`bands`). The first
    build added the display without appending it, which is the §1.4 orphan:
    present in the payload, absent from `controlledChildren`, never anchored
    -- it renders at the WoW default position. Caught by reading the
    structural guide dump, which walks children and could not see it.
    """
    bands.append(add(B.texture(
        f"SB {spec_name} Static Count", f"SB {spec_name}",
        [B.aura_trigger([str(STATIC)])],
        tex=SOLID, x=row_w(5) // 2 + 16, y=y, w=26, h=h,
        color=(0, 0, 0, 0), blend="BLEND",
        subregions=[B.sub_text("%s", size=max(10, h - 2), anchor="CENTER",
                               color=(0.75, 0.92, 1.0, 1.0))])))


# ============================================================== 2. LIGHTNING
# Ranged Static nuker. Press order is the cited rotation
# (sidekick-page-stormbringer-lightning-2026-08-07): Volt to open and
# maintain, Forked Lightning on charges, Call Lightning as the cheap spender,
# Electrocute in the execute window, Arm of Thorim as the all-Static dump.
L = []
spec_alerts("Lightning", L)
L.append(cd_group("SB Lightning Main", "SB Lightning",
                  ["Volt", "Forked Lightning", "Call Lightning",
                   "Electrocute", "Arm of Thorim"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="lightning"))
envelope("Lightning", L)
# Your DoT and slow on the target -- the maintain bucket names Volt.
L.append(dot_bars("SB Lightning Target", "SB Lightning",
                  [("Volt", (0.55, 0.85, 1.00), {})],
                  y=Y_TARGET, refresh_at=4))
_y_L = emit_bottom_block("Lightning", "lightning", L,
                         [("Electrocutioner", (1.00, 0.85, 0.40)),
                          ("Lord of Lightning", (0.70, 0.60, 1.00)),
                          ("Dark Skies", (0.60, 0.70, 0.95)),
                          ("Electrical Charge", (1.00, 0.75, 0.35)),
                          ("Thunder Wave", (0.55, 0.85, 1.00))],
                         SHORT_ENTRIES)
longterm_band("Lightning", "lightning", L, _y_L)
add(spec_group("SB Lightning", L))


# =================================================================== 3. WIND
# THE PET SPEC. A permanent Air Elemental does the damage while the player
# buffs, shields and peels (Sidekick: "treat this spec as a
# buff-shield-and-control support"). Press order from the cited rotation:
# Gale on charges, Aeroblast as the Static dump, Updraft for ground AoE,
# Flurry to command the pet, Kiss of the Clouds re-applied on cooldown.
WI = []

# NO PET: the whole spec hangs on the elemental being alive. Trigger 1 asks
# the PET unit for the elemental's own permanent aura and fires on absence;
# trigger 2 gates on knowing the summon at all, so a levelling character who
# cannot summon yet is not nagged. Whether an absent unit reports "missing"
# on this fork is §6.6 -- the one alert in the pack built on unverified
# ground, flagged there rather than silently trusted.
_no_pet = B.icon(
    "SB Wind Alerts No Pet", "SB Wind Alerts",
    [B.aura_trigger(["806010", "Air Elemental Passive"], unit="pet",
                    own_only=False, show_on="showOnMissing"),
     B.spell_known_trigger(sid("Summon: Air Elemental"))],
    ic("Summon: Air Elemental"), size=SZ_ALERT, desaturate=True,
    subregions=[B.sub_background(),
                B.sub_text("NO PET", size=10, anchor="INNER_BOTTOM",
                           color=(1, 0.35, 0.35, 1)),
                B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                             edge=EDGE),
                B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
NEEDS_ALL.add(_no_pet["id"])
spec_alerts("Wind", WI, extra=[add(_no_pet)])

WI.append(cd_group("SB Wind Main", "SB Wind",
                   ["Gale", "Aeroblast", "Updraft", "Flurry",
                    "Kiss of the Clouds"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="wind"))
envelope("Wind", WI)
# Flurry leaves a 21s resistance-shredding DoT on the target -- the one
# wind-owned target state worth a refresh read.
WI.append(dot_bars("SB Wind Target", "SB Wind",
                   [("Flurry", (0.60, 0.90, 0.80), {"by_name": True})],
                   y=Y_TARGET, refresh_at=5))
# The pet's state rides the on-me row with unit="pet" -- Invigoration ramp,
# the Unshackle window, Gift of Air. Unshackle listed here (pet unit) is also
# what keeps cd_buffs from adding a player-unit copy.
_y_W = emit_bottom_block("Wind", "wind", WI,
                         [("Invigoration", (0.60, 0.90, 0.80),
                           {"unit": "pet"}),
                          ("Unshackle", (1.00, 0.75, 0.35), {"unit": "pet"}),
                          ("Gift of Air", (0.70, 0.95, 0.90),
                           {"unit": "pet"}),
                          ("Lexicon of Servitude", (1.00, 0.90, 0.55)),
                          ("Hurricanes", (0.95, 0.65, 0.35))],
                         SHORT_ENTRIES)
longterm_band("Wind", "wind", WI, _y_W)
add(spec_group("SB Wind", WI))


# ============================================================== 4. MAELSTROM
# Frost-flavoured dual-currency caster. Tempest Sovereign has already
# transformed Shock->Brine and Call Lightning->Torrential Wrath, so the row
# tracks the REPLACEMENT ids -- there is no override system on 3.3.5 and no
# swap to express. Press order from the cited rotation: Brine to build both
# meters, Torrential Wrath at full Conductive, the Stormflow channel on
# cooldown, Drown maintained, Deluge for packs.
M = []
spec_alerts("Maelstrom", M)
M.append(cd_group("SB Maelstrom Main", "SB Maelstrom",
                  ["Brine", "Torrential Wrath", "Stormflow", "Drown",
                   "Deluge"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="maelstrom"))
envelope("Maelstrom", M, maelstrom=True)
# Drown (the maintain bucket, stacks to 8 post-07/31) and Stormcloud (wants
# to be up before Torrential Wrath). Both ride the enemy target.
M.append(dot_bars("SB Maelstrom Target", "SB Maelstrom",
                  [("Drown", (0.45, 0.70, 0.95), {"by_name": True}),
                   ("Stormcloud", (0.70, 0.80, 0.95), {"by_name": True})],
                  y=Y_TARGET, refresh_at=3))
_y_M = emit_bottom_block("Maelstrom", "maelstrom", M,
                         [("Kinetic Energy", (1.00, 0.85, 0.40))],
                         SHORT_ENTRIES)
longterm_band("Maelstrom", "maelstrom", M, _y_M)
add(spec_group("SB Maelstrom", M))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. The three L10
# Specialization passives are a contiguous block (db.exil.es 92096/7/8), each
# granted with the spec's first talent investment and never re-ranked --
# exactly the "one spell unique to each spec" the gate wants. Spell Known on
# a passive is proven ground on this fork: Chronomancer's Eternity Warper
# (806301) gate was verified in game.
SPEC_KNOWN = {
    "Lightning": 92096,    # Electrocutioner, the L10 lightning passive
    "Wind": 92097,         # Air Elemental, the L10 wind passive
    "Maelstrom": 92098,    # Conductive, the L10 maelstrom passive
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
