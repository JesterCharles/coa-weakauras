"""Build the `Necromancer [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Class CONTENT over the shared engine (`tools/wapack.py`) in the Chronomancer
shape -- no convergence flags. Requirements: `notes/requirements-necromancer.md`.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your DoTs / debuffs ]            <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 9
              [ defensive + utility       ]           <- band 7, wraps at 9
              [ long-term buffs           ]           <- band 8, active-only

Three things specific to this class (requirements §3 -- THE PET QUESTION IS
THE CLASS):

  * THE MINION ARMY HAS NO UNIT. Raised minions are a Life-Force-budgeted
    ARMY, not the single 3.3.5 `pet` unit, and this fork has no minion-count
    trigger (Prototypes.lua: Totem / Pet Behavior / auras only). The native
    surface the client itself maintains is the "Life Force" player aura
    524901 (rank "Visual", duration -1, kept alive by the Visual Updater
    passives), so the pet budget renders as that aura's STACK COUNT on the
    Runic Power bar -- a number that cannot lie, only need relabelling after
    one in-game read (§6.1). No `unit="pet"` triggers anywhere: whether any
    raised minion occupies the pet unit is §6.3, and a display built on that
    guess would fail silently.

  * COMMANDS ARE THE PET ROTATION. Command: Undead (504868, 30 RP) is the
    generic button -- "Refer to individual Raise spells for their Command
    effect" -- and rides the animation/death main rows; the per-minion
    `Command: <Minion>` rows are read as its dispatch targets (§6.2). Rime's
    two Commands (Bonefreeze, Skeletal Mage) are their own buttons.

  * DUAL POWER + A BUDGET. Runic Power is UnitPower type 6 (tooltip cost
    lines + the fork's RUNIC_POWER entry, Types.lua:1425 -- §6.5 until seen
    in game; a wrong guess shows an empty bar, never a wrong number), mana is
    type 0, and Life Force rides the RP bar as text. The envelope is the
    standard two-band height on every spec.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT (notes/production-run.md). Never imported in game;
# the inventory roles were machine-proposed and bulk-cleared (recorded in
# buildlog-necromancer.json), and requirements §6 lists what only the client
# can settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
# FALLBACK is used only where NOTHING resolved upstream; every choice below is
# stock 3.3.5 art so the client is guaranteed to have it.
FALLBACK = {
    "Animate: Bone Construct": "inv_misc_bone_skull_02",
    "Army of the North": "spell_deathknight_armyofthedead",
    "Bone Tithe": "inv_misc_bone_humanskull_01",
    "Bone King": "inv_misc_bone_skull_01",          # buff-row proc icon
    "Death's Due": "spell_shadow_deathpact",
    "Create Frozen Reliquary": "spell_frost_wizardmark",
    "Foul Mandate": "spell_shadow_unholystrength",
    "Grim Mandate": "spell_shadow_shadowwordpain",
    "Mass Grave": "spell_shadow_psychicscream",     # AoE fear
    "Raise: Lesser Skeletal Warrior": "spell_shadow_raisedead",
    "Raise: Skeletal Rogue": "spell_shadow_animatedead",
}
OVERRIDE = {
    # ONLY deliberate choices belong here: an entry overrides the CLIENT's own
    # art for the spell. All three exist because the duplicate-art check
    # flagged the pair sharing one texture in one row; the replacement is
    # stock 3.3.5 art that appears in no other row of this pack.
    #
    # Phylactery and Create Bone Reliquary both resolve to inv_misc_urn_01
    # and share the Animation utility row. The reliquary keeps the urn (it IS
    # an urn); the Phylactery takes the soulgem.
    "Phylactery": "spell_shadow_soulgem",
    # Animate: Crypt Fiend and Raise: Crypt Fiend both resolve to `cryptfiend`
    # and share the Animation utility row. The Raise keeps the client art;
    # the (hedged, §6.9) Animate takes the web its Command shoots.
    "Animate: Crypt Fiend": "spell_nature_web",
    # Razorice and Greater Razorice share spell_frost_frostarmor in the Rime
    # utility row. Greater takes the rank-2 armor art.
    "Greater Razorice": "spell_frost_frostarmor02",
}
# db.exil.es points at rows db.ascension.gg does not corroborate as the
# castable; corrections here are name -> id, and an in-game tooltip outranks
# them (resources/in-game-verified.json). Every entry's tooltip-read verdict
# is in requirements §0 and the inventory Notes.
CROSSCHECK = {
    # exiles 500365 carries a Raise: Abomination tooltip on db.ascension.
    # 805197 matches the 07/31 changelog text: 33% mana, 3 min CD, slows +
    # raises Undead + "creating a corpse".
    "Graveyard": 805197,
    # exiles 578117 is the 15s minion buff aura (no cost, no CD). 805029 is
    # the castable: 15% mana, 3 min cooldown.
    "Unholy Frenzy": 805029,
    # exiles 578306 is rank "Passive". 802132 is the death-tree grant:
    # 30 RP, 1.5s cast, 30s CD.
    "Lichplague": 802132,
    # exiles 301007 is "Rank 4". 707007 is the animation-tree grant:
    # 40 RP, 10s CD.
    "March of the Dead": 707007,
    # exiles 500330 is the single-archer component ("You summon a Skeletal
    # Archer..."). 805040 is the tree grant: 27% mana, 30s CD, animates 3.
    "Animate: Skeletal Archer": 805040,
    # exiles 572408 is its "Cast Time Reducer Aura". 803741 is the class-tree
    # button: 22% mana, 30s CD, instant above 50 RP.
    "Mass Grave": 803741,
    # exiles 520364 has no cost and no CD. 804371 is the class-tree button:
    # 25% mana, 2 min CD.
    "Foul Invocation": 804371,
    # exiles 802084 is a bare stub. 802121: 25% mana, 2 min CD, usable while
    # stunned.
    "Bone Tithe": 802121,
    # exiles 500731 is "Phylactery Aura". 500933: 2 min CD + Corpse Dust.
    "Phylactery": 500933,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- Animation
# and Rime render five 44px main icons, so row_w(5) = 228px and the rule
# `28w - 2 <= 1.2 * 228` allows w <= 9.8 -> 9. Confirmed against the built
# packs by tools/rowwidths.py. Do NOT copy this number to another class.
CLS = W.init("necromancer", version=VERSION, prefix="NC", cd_per_row=9,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# ---- the resource system ---------------------------------------------------
# Life Force: the pet budget. ONE player aura, duration -1, rank "Visual" --
# 524901 -- kept alive by the "Life Force Visual Updater" passives (500494 /
# 500524) and "Necro Life Force Re-adder" (805602, "If life force is not
# active, apply it"). Its stack count is the one native surface for the
# minion budget (requirements §3); whether stacks mean AVAILABLE or USED is
# §6.1 and only relabels the text.
LIFE_FORCE = 524901
RP_POWER = 6          # RUNIC_POWER, Types.lua:1425 -- §6.5

# No ability in this class holds charges: no "N Charges" text appears in any
# tooltip of the reviewed inventory.
CHARGES = {}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent tooltips. Proc-aura ids are unverified (§6.6):
# matched by id-or-name, and a glow wired to a wrong id never fires -- it
# reads as "nothing to do", never as a lie.
PROC_GLOW = {
    # "treats your next 2 spells cast as the target were Frozen" (704681) --
    # the payoff window for the guaranteed-crit nuke.
    "Glacial Impact": ["Permafrost"],
    # "reset the cooldown of Ice Barrage and make your cast next within 15
    # seconds free of cost" (300940).
    "Ice Barrage": ["Refreshing Chill"],
    # "Casting Command spells now has a 15% chance to make your next
    # Lichfrost within 5 seconds instant cast" (707175, animation talent).
    "Lichfrost": ["Bone King"],
    # "Casting Command spells now has a 30% chance to cause their next use
    # within 6 seconds to be free of cost" (572772, animation L20 passive).
    "Command: Undead": ["Deadly Bond"],
}
# None of the glow procs carries a stack count worth drawing on the button --
# the stacking states (Diabolical, Underking, Frozen Bodies, Tundra Warriors)
# live in the on-me row where buff_group already shows stacks.
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: nukes, diseases and summon waves whose state lives on the
# TARGET or on the minions, never on the player. A name missing from here
# costs nothing but a display that never shows; a name wrongly here hides a
# running cooldown, so only the unambiguous cases are listed. Mutation and
# Army of the North stay OUT -- both are running windows worth seeing.
NO_BUFF = {"Corpse Explosion", "Graveyard", "Death's Due", "Blight",
           "Lich Bolt", "Foul Expedition", "Noxious Corpserot", "Plaguebomb",
           "Plaguestorm", "Ray of Rot", "Harvest Plague", "Icequake",
           "Bonefreeze", "Glacial Tap", "Animate: Bone Construct",
           "Animate: Bone Wraith", "Animate: Tomb King",
           "Animate: Plaguefather", "Animate: Zombies", "Animate: Frost Wyrm",
           "Unholy Frenzy"}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# ---- missing-buff reminders ------------------------------------------------
# NO WARD is the class-wide alert: Fetid / Glacial / Bone Ward are 30-minute
# self+minion buffs, "Only 1 Ward can be active at a time", and they persist
# through death since 07/31 -- so a missing ward is purely a "you forgot it"
# state, the missing-imbue shape. Two triggers, ALL: "no ward aura is up" AND
# "you actually know Fetid Ward" (the class-tree ward every listed build
# takes) -- without the second, the alert is permanently on screen for a
# character who has not talented a ward, the retro's reminder-band failure.
#
# The aura match lists all three ward names plus the castable ids, any-of:
# whether each 30-min self-aura reuses the castable's id is §6.7, and the
# name match is the half that survives either answer.
WARDS = ["Fetid Ward", "Glacial Ward", "Bone Ward"]

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

_ward_keys = [str(sid(w)) for w in WARDS] + WARDS
_no_ward = B.icon(
    "NC Alerts No Ward", "NC Alerts",
    [B.aura_trigger(_ward_keys, own_only=False, show_on="showOnMissing"),
     B.spell_known_trigger(sid("Fetid Ward"))],
    ic("Fetid Ward"), size=SZ_ALERT, desaturate=True,
    subregions=[B.sub_background(),
                B.sub_text("NO WARD", size=10, anchor="INNER_BOTTOM",
                           color=(1, 0.35, 0.35, 1)),
                B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                             edge=EDGE),
                B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
NEEDS_ALL.add(_no_ward["id"])
add(_no_ward)
add(B.dynamicgroup("NC Alerts", "NC Core", [_no_ward["id"]], x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
CORE.append("NC Alerts")

add(B.group("NC Core", ROOT, CORE, x=0, y=0))


# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row. Necromancer's long-term content
# is inventory-driven, three families:
#
#   Ward    "Only 1 Ward can be active at a time" -- which one is up.
#   Stance  Undead: Assault / Protect / Pacify, infinite duration, one at a
#           time (§6.4 for spec availability).
#   Form    Lich Form (rime): infinite transform, RP tick; Cryoshroud and
#           the faster Champion cooldowns key off it being up.
LONGTERM_COL = {
    "Ward": (0.55, 0.95, 0.55),
    "Stance": (0.95, 0.85, 0.45),
    "Form": (0.60, 0.80, 1.00),
}


def _family(name):
    if "Ward" in name:
        return "Ward"
    if name.startswith("Undead:"):
        return "Stance"
    return "Form"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `NC <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The signature passives here arrive with the first talent
    point (level 10), so the window a levelling character goes without this
    band is days, not twenty levels.
    """
    band = f"NC {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"NC {spec_name} Longterm {name}", band,
            # By id AND name: whether each infinite self-state aura reuses the
            # castable's id is §6.7, and a name match survives either answer.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            # No %p timer: wards are 30 min and stances/Lich Form are
            # duration -1, so a countdown here is either noise or empty.
            subregions=[B.sub_text("%s", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"NC {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Both are running defensive windows every spec has.
SHORT_ENTRIES = [
    ("Foul Invocation", (0.70, 0.95, 0.55), {}),   # 20s transform window
    ("Bone Tithe", (0.95, 0.85, 0.55), {}),        # 20s absorb shield
]


def envelope(spec_name, bands, icons=5):
    """Runic Power bar + mana bar -- the same two bands on all three specs,
    so the fixed-height envelope (~-156..-186) has no per-spec height
    variance. The WIDTH is locked to the spec's OWN main row (`icons`):
    Death's disease row is seven icons, the other two are five.

    RP sits NEAREST the main row (the spender currency the rotation is played
    around -- the ordering rule in notes/layout-standard.md); mana renders
    minor (half height, no value text). The LIFE FORCE count rides the RP
    bar's left edge as `%2.s` -- the stack count of a second, Life Force aura
    trigger (the same per-trigger text form the Pyromancer heat cell uses).
    No third band: the pet budget is a number, not a meter, and the envelope
    stays standard height.
    """
    w = row_w(icons)
    rp = B.aurabar(f"NC {spec_name} Runic Power", f"NC {spec_name}",
                   [B.power_trigger("player", RP_POWER),
                    B.aura_trigger([str(LIFE_FORCE), "Life Force"],
                                   own_only=False)],
                   x=0, y=Y_BAR, w=w, h=BAR_H_STACKED,
                   color=(0.35, 0.75, 0.95, 1.0),
                   subregions=[
                       B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                  justify="RIGHT"),
                       B.sub_text("LF %2.s", size=10, anchor="INNER_LEFT",
                                  x=4, justify="LEFT",
                                  color=(0.75, 1.0, 0.75, 1.0)),
                   ])
    # "any": the RP bar must render with no Life Force aura up -- trigger 1
    # (Power) drives the bar, trigger 2 only feeds the %2.s text.
    rp["triggers"]["disjunctive"] = "any"
    bands.append(add(rp))
    # Mana is the summon/utility pool -- real, but background next to RP:
    # minor render, half height, no value text (layout-standard prominence).
    m = B.aurabar(f"NC {spec_name} Mana", f"NC {spec_name}",
                  [B.power_trigger("player", 0)],
                  x=0, y=Y_SEG, w=w, h=SEG_H,
                  color=(0.30, 0.45, 0.95, 1.0))
    bands.append(add(m))


# =============================================================== 2. ANIMATION
# THE PET-ARMY SPEC. Press order is the cited rotation
# (sidekick-page-necromancer-animation-2026-08-07): Crypt Swarm channels the
# RP engine, Command: Undead weaves ("Command spells ... drive most of your
# passives"), Animate: Skeletal Archer is the instant RP dump, March of the
# Dead the AoE nuke, Unholy Frenzy the burst (Study of Death zombies ride
# it). The Raise family is the pre-pull ritual and lives in the utility row;
# the Animate waves are the offense row.
A = []
A.append(cd_group("NC Animation Main", "NC Animation",
                  ["Crypt Swarm", "Command: Undead",
                   "Animate: Skeletal Archer", "March of the Dead",
                   "Unholy Frenzy"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="animation"))
envelope("Animation", A)
# No target band: the cited animation rotation maintains no DoT on the
# target -- the army does the periodic damage (requirements §4).
_y_A = emit_bottom_block("Animation", "animation", A,
                         [("Diabolical", (0.85, 0.55, 1.00), {}),
                          ("Underking", (0.95, 0.80, 0.45), {}),
                          ("Bone King", (0.60, 0.90, 1.00), {}),
                          ("Deadly Bond", (1.00, 0.70, 0.40), {})],
                         SHORT_ENTRIES)
longterm_band("Animation", "animation", A, _y_A)
add(spec_group("NC Animation", A))


# =================================================================== 3. DEATH
# Disease-stack DoT spec. Press order is the cited rotation
# (sidekick-page-necromancer-death-2026-08-07): diseases on first (Plague of
# Undeath -> Flesh to Worms -> Lichplague), then the builders that stack
# Crypt Plague (Crypt Swarm 1 stack, Lichfrost 2), Command spenders for
# Expunge/Crypt Explosion, and Virulency to refresh-and-copy the whole stack
# on cooldown. Seven icons -- the widest main row in the pack.
D = []
D.append(cd_group("NC Death Main", "NC Death",
                  ["Plague of Undeath", "Flesh to Worms", "Lichplague",
                   "Crypt Swarm", "Lichfrost", "Command: Undead",
                   "Virulency"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="death"))
envelope("Death", D, icons=7)
# The stack list the Difficulty paragraph says the spec is played around:
# the three cast diseases with refresh glow, plus the Crypt Plague and
# Expunge stack counts. Crypt Plague / Expunge / Harvest Plague are matched
# id-or-name -- their exiles rows are the passive/dummy, and the debuff the
# server applies may carry another id (dot_bars by_name provenance case).
D.append(dot_bars("NC Death Target", "NC Death",
                  [("Plague of Undeath", (0.55, 0.90, 0.45), {}),
                   ("Flesh to Worms", (0.85, 0.65, 0.35), {}),
                   ("Lichplague", (0.60, 0.80, 1.00), {"by_name": True}),
                   ("Harvest Plague", (0.90, 0.45, 0.35), {"by_name": True}),
                   ("Crypt Plague", (0.75, 0.95, 0.55), {"by_name": True}),
                   ("Expunge", (1.00, 0.80, 0.30), {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_D = emit_bottom_block("Death", "death", D, [], SHORT_ENTRIES)
longterm_band("Death", "death", D, _y_D)
add(spec_group("NC Death", D))


# ==================================================================== 4. RIME
# Freeze-then-detonate frost caster with a single raised pet. Press order is
# the cited rotation (sidekick-page-necromancer-rime-2026-08-07): Lichfrost
# builds, Ice Barrage channels into the end-of-channel entomb, Glacial
# Impact detonates Frozen targets (guaranteed crit via Glacier Lord),
# Command: Bonefreeze freezes groups, Command: Skeletal Mage is the RP burst.
# The Skeletal Mage raise rides the utility row; NO PET alert deliberately
# not built -- no player-visible presence surface is known (§6.3).
R = []
R.append(cd_group("NC Rime Main", "NC Rime",
                  ["Lichfrost", "Ice Barrage", "Glacial Impact",
                   "Command: Bonefreeze", "Command: Skeletal Mage"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="rime"))
envelope("Rime", R)
# Deathchill is the freeze-setup stack the passives build (10 stacks -> Icy
# Tomb) and Icequake consumes -- the one rime-owned target read.
R.append(dot_bars("NC Rime Target", "NC Rime",
                  [("Deathchill", (0.55, 0.85, 1.00), {"by_name": True})],
                  y=Y_TARGET, refresh_at=None))
_y_R = emit_bottom_block("Rime", "rime", R,
                         [("Permafrost", (0.60, 0.90, 1.00), {}),
                          ("Tundra Warriors", (0.70, 0.95, 0.85), {}),
                          ("Frozen Bodies", (0.85, 0.95, 1.00), {}),
                          ("Refreshing Chill", (0.50, 0.80, 1.00), {})],
                         SHORT_ENTRIES)
longterm_band("Rime", "rime", R, _y_R)
add(spec_group("NC Rime", R))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. The three L10
# spec passives are a contiguous block granted with the spec's first talent
# investment and never re-ranked -- read from the official talent builder
# (talents-necromancer.json: the free, y=0 node per spec tree), exactly the
# "one spell unique to each spec" the gate wants. Spell Known on a passive is
# proven ground on this fork: Chronomancer's Eternity Warper (806301) gate
# was verified in game.
SPEC_KNOWN = {
    "Animation": 92123,   # Summoning Adept, the L10 animation passive
    "Death": 92121,       # Crypt Plague, the L10 death passive
    "Rime": 92122,        # Tundra Warriors, the L10 rime passive
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
