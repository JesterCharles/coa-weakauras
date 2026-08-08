"""Build the `Bloodmage [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Class CONTENT over the shared engine (`tools/wapack.py`) in the Chronomancer
shape -- no convergence flags. Requirements: `notes/requirements-bloodmage.md`.
Third FOUR-spec class through the pipeline, with one spec of each role plus a
second DPS: Sanguine (ranged caster DPS, health-cost economy), Accursed
(form-swap melee DPS), Eternal (tank), Fleshweaver (healer). Roles are
Sidekick-cited, pending in-game (resources/spec-roles.md).

        [ alerts: NO SHIELD / NO CURSE / LOW BLOOD ]  <- active-only, per spec
        [ on TARGET: your DoTs / your HoTs ]          <- active-only
        [ on me: procs, running CDs, buffs ]          <- active-only
              [  MAIN ROW - flush         ]
              [  rage (+ stack bar) envelope ]        <- fixed height
              [ offensive cooldowns       ]           <- wraps at 7
              [ defensive + utility       ]           <- wraps at 7
              [ long-term buffs           ]           <- active-only

Three things without an analogue in the earlier classes:

  * THE HEALTH-COST ECONOMY. Sanguine and Fleshweaver spend the player's own
    health bar as a resource. The pack does NOT duplicate the health bar --
    the default UI owns that surface. It carries the three cues the economy
    actually needs: the Thirst / Pooled Vitality stack bars (the rate
    limiters on health spend), the Insatiable red entry (the cost of
    overcasting), and a LOW BLOOD alert at <=35% -- the threshold the kit's
    own passives key off (Essence Harvester, Blood Scent, Enduring).

  * NO MANA, ANYWHERE. Every spec runs on Rage ("Pure Rage economy, with no
    mana anywhere in the kit" -- fleshweaver; "no mana pool is spent" --
    sanguine). The envelope holds a rage bar per spec, plus a 10-cell stack
    bar on the two stack-metered specs; accursed and eternal get the solo
    full-height bar.

  * FORM STATE IS A BUFF, NOT AN ALERT, except on Eternal. Accursed flips
    Mortal <-> Cursed Form deliberately, so its form state rides the on-me
    row. Eternal's whole tank kit hangs on staying in Eternal Curse ("Stay
    transformed ... as your default"), so a dropped stance earns the NO CURSE
    alert -- the NO BOON shape, spec-gated.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT. Never imported in game; the inventory roles were
# machine-proposed and bulk-cleared (recorded in buildlog-bloodmage.json), and
# requirements §6 lists what only the client can settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
# Filled from the first build's "no art upstream" survey; classic-client
# icons, checked distinct within every row each name appears in.
FALLBACK = {
    "Accursed Form": "spell_shadow_demonform",
    "Apotheosis": "spell_shadow_lifedrain02",
    "Atherann's Anguish": "spell_shadow_corpseexplode",
    "Blood-Cursed Armor": "spell_nature_spiritarmor",
    "Blood Feast": "spell_shadow_lifedrain",
    "Blood Veil": "spell_shadow_shadowward",
    "Bloodgale": "spell_shadow_teleport",
    "Bloodsoaked Offering": "inv_potion_24",
    "Bloodthorns": "spell_nature_thorns",
    "Claw Sweep": "ability_druid_swipe",
    "Crimson Maw": "inv_misc_monsterfang_01",
    "Darkfallen Lament": "spell_shadow_soulleech_3",
    "Endure the Curse": "spell_shadow_antishadow",
    "Final Embrace": "spell_shadow_unholyfrenzy",
    "Gore Barrage": "inv_misc_bone_10",
    "Greater Bloodthorns": "spell_nature_needlecastspeed",
    "Hemostasis": "spell_shadow_painspike",
    "Invigorated Flesh": "spell_nature_undyingstrength",
    "Ravenous Bite": "ability_druid_ferociousbite",
    "Sanguine Essence": "inv_misc_gem_bloodstone_02",
    "Slaughterhouse Offering": "inv_misc_bone_08",
    "Transgression": "spell_shadow_unholystrength",
    "Vital Shield": "inv_elemental_primal_life",
}
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own art
# for the spell.
OVERRIDE = {
    # Both resolve trade_engineering upstream (a placeholder, not art) and
    # share the Sanguine utility row -- the duplicate-art check fires on it.
    # The interrupt takes the classic counterspell shock; the blood-pool
    # immunity takes bloodboil.
    "Aneurysm": "spell_frost_iceshock",
    "Liquify": "spell_shadow_bloodboil",
}
# db.exil.es points at rows db.ascension.gg does not corroborate as the
# castable; corrections are name -> id, and an in-game tooltip outranks them
# (resources/in-game-verified.json). The four crossdb no-records resolved
# without an id correction (requirements §0): Atherann's Anguish is other-id
# but the exiles id is the castable-shaped one; Curse of the Worgen and the
# Gore Barrage button do not ship; Infuse ships on the exiles id.
CROSSCHECK = {
    # The eternal main row's bite. db.exil.es carries it only as "Ravenous
    # Bite (Packleader)" (560365, Rank 1); the inventory row records the same
    # id with the §6 caveat -- an in-game tooltip would settle it.
    "Ravenous Bite": 560365,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- Eternal
# renders four 44px main icons (its cited rotation is exactly four buttons),
# so row_w(4) = 182px and the rule `28w - 2 <= 1.2 * 182` allows w <= 7.8 -> 7.
# Confirmed against the built packs by tools/rowwidths.py. Do NOT copy this
# number to another class.
CLS = W.init("bloodmage", version=VERSION, prefix="BM", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# Abilities that hold charges rather than a plain cooldown. Rotclaw's count is
# tooltip-read ("2 Charges, 6 sec recharge" -- db.exil.es renders no Charges
# row for it).
CHARGES = {"Rotclaw": 2}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent/kit text.
PROC_GLOW = {
    # "Essence Harvester: Being struck while below 35% health instantly
    # resets the cooldown of your Vampiric Fang and grants you Wretched."
    "Vampiric Fang": ["Wretched"],
    # "Final Embrace: ... transforming your Bloodfang Bite into Crimson Maw."
    # The transform is a 20s AURA window, not a learn event, so this is a
    # glow, not a Spell Known swap (requirements §2).
    "Crimson Maw": ["Final Embrace"],
    # "Saturating Sutures: periodic damage and healing has a 15% chance to
    # reduce the cost of your next Sanguine Mend by -100% for 8 seconds."
    "Sanguine Mend": ["Saturating Sutures"],
}
# Of those, the ones whose proc also STACKS. None cited.
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: summons, enemy strikes and channels on the target.
NO_BUFF = {"Animated Blood", "Finger of Death", "Eviscerated", "Infuse"}

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
# Core carries nothing class-wide: every reminder in this pack is spec-shaped
# (Shields exist on two specs, the stance on one, the health economy on two),
# so each lives under its spec group where the spec gate applies. The empty
# Core keeps the standard Core/spec skeleton (the Witch Hunter shape).
CORE = []
add(B.group("BM Core", ROOT, CORE, x=0, y=0))


# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own cooldown stack. Bloodmage's long-term content
# is inventory-driven, three families:
#
#   Shield    "Only 1 Shield can be active at a time" -- the class's imbue
#             analogue. Fleshweaver has three, Sanguine one.
#   Offering  30-min ally buffs (Sanguine).
#   other     party auras ("Does not stack with similar effects") and the
#             30-min ally thorns; Eternal Curse, the tank stance.
LONGTERM_COL = {
    "Shield": (0.85, 0.35, 0.35),
    "Offering": (0.95, 0.85, 0.45),
    "other": (0.75, 0.70, 1.00),
}


def _family(name):
    low = name.lower()
    if "shield" in low:
        return "Shield"
    if "offering" in low:
        return "Offering"
    return "other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `BM <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The four gates are the L10 spec passives, which arrive with
    the first talent point.
    """
    band = f"BM {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        # By id AND name where an id exists; by name alone where none does
        # (Blood-Cursed Armor and Invigorated Flesh resolve in no digest --
        # requirements §6). The Offerings come in plain and Greater pairs
        # whose names contain each other, and several rows are ranked --
        # matching either covers both failure shapes.
        keys = [str(sid_), name] if sid_ else [name]
        out.append(add(B.icon(
            f"BM {spec_name} Longterm {name}", band,
            [B.aura_trigger(keys, own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"BM {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Blood Rush is the one class-tree proc every spec can take; the
# two defensives get running state here because they live in the utility row,
# which cd_buffs does not derive from.
SHORT_ENTRIES = [
    ("Blood Rush", (0.60, 0.90, 1.00), {}),
    ("Blood Pact", (0.80, 0.70, 1.00), {}),
    ("Wicked Howl", (0.85, 0.45, 0.45), {}),
]


def _alert_icon(id_, band, triggers, art, label, needs_all=False):
    """The missing-buff alert shape (NO BOON / NO SKIN, in-game verified on
    the Pyromancer and Primalist packs)."""
    d = B.icon(
        id_, band, triggers,
        ic(art), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text(label, size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
    if needs_all:
        NEEDS_ALL.add(d["id"])
    return d


def low_blood_trigger(pct=35):
    """Player health at or below `pct` percent.

    The Health prototype on THIS fork carries `percenthealth` with
    `conditionType = "number"` and a multiEntry spec, and ConstructTest's
    multiEntry branch requires TABLE values (`type(trigger[name]) == "table"`
    ... ipairs) -- a plain string never matches. Both read off
    Ascension-Addons/WeakAuras-Ascension Prototypes.lua / GenericTrigger.lua,
    2026-08-08. So the filter is emitted as one-element arrays.

    35 is the kit's own threshold: Essence Harvester, Blood Scent and
    Enduring all key off "below 35% health" (requirements §5).
    """
    t = B.health_trigger("player")
    t["use_percenthealth"] = True
    t["percenthealth"] = B.arr([str(pct)])
    t["percenthealth_operator"] = B.arr(["<="])
    return t


def spec_alerts(spec_name, bands, entries):
    """One alerts band per spec, at the standard alert anchor."""
    band = f"BM {spec_name} Alerts"
    ids = [add(d) for d in entries]
    add(B.dynamicgroup(band, f"BM {spec_name}", ids, x=0, y=Y_ALERT,
                       grow="HORIZONTAL", space=6))
    bands.append(band)


def rage_envelope(spec_name, bands, icons, stack=None):
    """The resource envelope: Rage (power type 1 on 3.3.5) on every spec --
    the class spends NO mana anywhere (requirements §4), so no mana bar.

    `stack=(prefix, aura_key, col)` adds the 10-cell stack bar under a
    stacked-height rage bar; without it the rage bar takes the whole envelope.
    `icons` is the SPEC'S OWN main-row icon count: every resource band's width
    derives from its own spec's main row, never another spec's.
    """
    w = row_w(icons)
    rage_col = (0.85, 0.30, 0.25, 1.0)
    gid = f"BM {spec_name} Rage"
    add(B.aurabar(gid, f"BM {spec_name}", [B.power_trigger("player", 1)],
                  x=0, y=Y_BAR if stack else Y_BAR_SOLO, w=w,
                  h=BAR_H_STACKED if stack else BAR_H_SOLO, color=rage_col,
                  subregions=[B.sub_text("%p", size=10, anchor="INNER_RIGHT",
                                         x=-4, justify="RIGHT")]))
    bands.append(gid)
    if stack:
        prefix, aura_key, col = stack
        # 10 cells, matched by NAME: the resolvable "Thirst" / "Pooled
        # Vitality" ids are the L10 teaching passives (the Aeon-of-Resilience
        # shape), so an exact-id match could bind to a hidden passive and
        # never light. A name match reads whatever the server actually stacks
        # on the player; if the buff name differs in game the cells stay dark,
        # which is visible on the first import (requirements §6).
        stack_bar(prefix, f"BM {spec_name}", aura_key, 10, col,
                  Y_SEG, B.health_trigger("player"), w, bands)


# =============================================================== 2. SANGUINE
# Ranged caster DPS paying health to cast. Press order is the cited rotation
# (sidekick-bloodmage-sanguine, 2026-08-07): Bloodmoon Blast is "the main
# filler to build Thirst and Rage", Atherann's Anguish is planted for its
# detonation, Sanguine Rupture covers the pack and builds Thirst, Vampiric
# Fang dumps Thirst "before it caps at 10", Valanar's Vengeance and Keleseth's
# Calamity are the Thirst-cheapened nukes. The DoT set (Taldaram's Torment,
# Hematophage, Malediction, Shadow Hemorrhage, Twisted Magic) lives on the
# target band, where the refresh cue is.
S = []
spec_alerts("Sanguine", S, [
    # Shadowfang Shield is the spec's Shield-family slot -- a 30-min self
    # sustain tick that is quietly gone when dropped.
    _alert_icon("BM Sanguine Alerts No Shield", "BM Sanguine Alerts",
                [B.aura_trigger([str(sid("Shadowfang Shield")),
                                 "Shadowfang Shield"],
                                own_only=False, show_on="showOnMissing")],
                "Shadowfang Shield", "NO SHIELD"),
    # The health economy's floor: "Over-casting without dumping Thirst or
    # lifestealing it back can kill you, not just leave you unable to act."
    _alert_icon("BM Sanguine Alerts Low Blood", "BM Sanguine Alerts",
                [low_blood_trigger(35)], "Blood Craving", "LOW BLOOD"),
])
S.append(cd_group("BM Sanguine Main", "BM Sanguine",
                  ["Bloodmoon Blast", "Atherann's Anguish", "Sanguine Rupture",
                   "Vampiric Fang", "Valanar's Vengeance",
                   "Keleseth's Calamity"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="sanguine"))
rage_envelope("Sanguine", S, 6,
              stack=("BM Thirst", "Thirst", (0.90, 0.25, 0.30)))
# Your DoTs on the target. Ranked ids fall back to name automatically;
# Malediction, Shadow Hemorrhage and Twisted Magic are passive-provenance or
# unranked ids, so they match by name deliberately.
S.append(dot_bars("BM Sanguine Target", "BM Sanguine",
                  [("Taldaram's Torment", (0.80, 0.35, 0.35), {}),
                   ("Hematophage", (0.70, 0.55, 0.30), {}),
                   ("Malediction", (0.60, 0.40, 0.85), {"by_name": True}),
                   ("Shadow Hemorrhage", (0.55, 0.35, 0.60), {"by_name": True}),
                   ("Twisted Magic", (0.45, 0.50, 0.90), {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_S = emit_bottom_block("Sanguine", "sanguine", S,
                         [("Transgression", (0.85, 0.45, 0.85)),
                          ("Wretched", (1.00, 0.85, 0.40)),
                          ("The Cup Runneth Over", (0.95, 0.60, 0.35)),
                          ("Sovereignty", (0.60, 0.85, 0.60)),
                          # The cost of missing the Vampiric Fang dump: the
                          # 10-Thirst self-penalty, drawn red and HARMFUL.
                          ("Insatiable", (1.00, 0.25, 0.20),
                           {"helpful": False}),
                          ("Blood Craving", (0.85, 0.30, 0.30)),
                          ("Sacrificial Rite", (0.95, 0.75, 0.40))],
                         SHORT_ENTRIES)
longterm_band("Sanguine", "sanguine", S, _y_S)
add(spec_group("BM Sanguine", S))


# =============================================================== 3. ACCURSED
# Form-swap melee DPS. Press order from the cited rotation: transformed
# priority "Reave (best value when the target is bleeding, below 35%, or
# you're behind it) > cleave freely > Ravenous Strike spammed in the gaps";
# caster phase "weave Bloodbolt, Veinburst and Hemoburst on cooldown to build
# Rage". Both modes share the row -- form flips are deliberate here, so form
# state rides the on-me row (Blood Curse's aura via cd_buffs), never an alert.
A = []
A.append(cd_group("BM Accursed Main", "BM Accursed",
                  ["Reave", "Ravenous Strike", "Puncturing Fangs", "Bloodbolt",
                   "Veinburst", "Hemoburst"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="accursed"))
rage_envelope("Accursed", A, 6)
# Your marks on the target: Taldaram's Torment is refreshed from the accursed
# kit (Finger of Death, Shards of Torment), Eviscerated's bleed and Grimclaw
# are passive-applied -- all by name.
A.append(dot_bars("BM Accursed Target", "BM Accursed",
                  [("Taldaram's Torment", (0.80, 0.35, 0.35),
                    {"by_name": True}),
                   ("Eviscerated", (0.85, 0.55, 0.30), {"by_name": True}),
                   ("Grimclaw", (0.60, 0.70, 0.45), {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_A = emit_bottom_block("Accursed", "accursed", A,
                         [("Ultra Instinct", (0.95, 0.80, 0.40)),
                          ("Sanguine Scripture", (0.60, 0.85, 1.00)),
                          # crossdb: ascension 807777 says Gore Barrage is a
                          # stacking aura spent by Bloodmoon Blast/Veinburst;
                          # the on-me row reads it, no button ships (§0/§6).
                          ("Gore Barrage", (0.80, 0.45, 0.45)),
                          ("Endure the Curse", (0.70, 0.70, 0.90))],
                         SHORT_ENTRIES)
longterm_band("Accursed", "accursed", A, _y_A)
add(spec_group("BM Accursed", A))


# ================================================================ 4. ETERNAL
# THE TANK ("a shapeshifting bruiser/tank"). Press order from the cited
# rotation: "Ravenous Bite and Bloodfang Bite carry both your threat and your
# self-healing. Rotclaw keeps a bleed and your Rage up, and Claw Sweep spreads
# threat across the pack." Blood Howl is per-pull (utility row), Monstrous
# Hunger has no id in either DB (requirements §6) -- its window glows
# Bloodfang Bite below instead of holding a dead slot.
E = []
spec_alerts("Eternal", E, [
    # "Stay transformed via Eternal Curse as your default grinding stance" --
    # the armor/Stamina/threat stance. Aura by NAME: the resolvable id 92114
    # is the L10 teach (§6). Show-on-missing, so it is invisible while the
    # stance is up.
    _alert_icon("BM Eternal Alerts No Curse", "BM Eternal Alerts",
                [B.aura_trigger(["Eternal Curse"],
                                own_only=False, show_on="showOnMissing")],
                "Eternal Curse", "NO CURSE"),
])
E.append(cd_group("BM Eternal Main", "BM Eternal",
                  ["Ravenous Bite", "Bloodfang Bite", "Rotclaw", "Claw Sweep"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="eternal"))
rage_envelope("Eternal", E, 4)
# Your bleeds and wounds on the target: Rotclaw's own bleed rides its ranked
# castable; Bite Wound (556234, applied by Bloodfang Bite) and Infection's
# stacking crit-taken debuff are passive-applied, so by name.
E.append(dot_bars("BM Eternal Target", "BM Eternal",
                  [("Rotclaw", (0.75, 0.50, 0.30), {}),
                   ("Bite Wound", (0.85, 0.40, 0.35), {"by_name": True}),
                   ("Infection", (0.60, 0.75, 0.40), {"by_name": True})],
                  y=Y_TARGET, refresh_at=3))
_y_E = emit_bottom_block("Eternal", "eternal", E,
                         [("Ironhide", (0.70, 0.70, 0.60)),
                          ("Eternal Resolve", (0.90, 0.55, 0.35)),
                          ("Apotheosis", (0.75, 0.40, 0.60))],
                         SHORT_ENTRIES)
longterm_band("Eternal", "eternal", E, _y_E)
add(spec_group("BM Eternal", E))


# ============================================================ 5. FLESHWEAVER
# THE HEALER ("Pure Rage economy... You track Rage the way a Warrior does").
# Raid frames stay out (VuhDo/Grid own that on 3.3.5a); the target band
# carries what YOU have on whoever you are targeting. Press order from the
# cited rotation: Sanguine Mend "as your primary tank/spot heal", Dark
# Liturgy links through Blood Rituals, Crimson Tide and Heartbreak chip and
# top the group, Blood Tap is THE Rage builder, Vampyr's Kiss the refund.
# Hemoglobe is a 3-min CD -> offense (healing CD) row, not a main slot.
F = []
spec_alerts("Fleshweaver", F, [
    # Three Shields, mutually exclusive ("Only 1 Shield can be active at a
    # time" on all three tooltips) -- fires only when NONE is up, the NO
    # WISDOM shape, so the one you deliberately did not take never nags.
    _alert_icon("BM Fleshweaver Alerts No Shield", "BM Fleshweaver Alerts",
                [B.aura_trigger([str(sid("Blood Shield")),
                                 str(sid("Coagulated Shield")),
                                 str(sid("Vital Shield")),
                                 "Blood Shield", "Coagulated Shield",
                                 "Vital Shield"],
                                own_only=False, show_on="showOnMissing")],
                "Blood Shield", "NO SHIELD"),
    # "The cold start is Rage-gated... an ambush at 0 Rage leaves you no
    # shield and no panic button" -- and every builder costs health.
    _alert_icon("BM Fleshweaver Alerts Low Blood", "BM Fleshweaver Alerts",
                [low_blood_trigger(35)], "Blood Tap", "LOW BLOOD"),
])
F.append(cd_group("BM Fleshweaver Main", "BM Fleshweaver",
                  ["Sanguine Mend", "Dark Liturgy", "Crimson Tide",
                   "Heartbreak", "Blood Tap", "Vampyr's Kiss"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="fleshweaver"))
rage_envelope("Fleshweaver", F, 6,
              stack=("BM Vitality", "Pooled Vitality", (0.55, 0.85, 0.55)))
# helpful=True: on a FRIENDLY target this shows what YOU have on them -- the
# absorb, the thorns, the Blood Rituals mark that Dark Liturgy / Darkfallen
# Lament heal through. All passive-provenance or ranked, so all by name.
F.append(dot_bars("BM Fleshweaver Target", "BM Fleshweaver",
                  [("Blood Veil", (0.55, 0.75, 1.00), {"by_name": True}),
                   ("Blood Rituals", (0.85, 0.45, 0.45), {"by_name": True}),
                   ("Bloodthorns", (0.60, 0.85, 0.55), {"by_name": True})],
                  y=Y_TARGET, unit="target", helpful=True, refresh_at=4))
_y_F = emit_bottom_block("Fleshweaver", "fleshweaver", F,
                         [("Sanguine Essence", (0.90, 0.40, 0.60)),
                          ("Saturating Sutures", (0.60, 0.90, 0.80)),
                          # check 22: no castable Darkfallen Lament id exists
                          # in either DB (every ascension row is a component)
                          # -- the active channel state rides here by name,
                          # no button ships (requirements §6).
                          ("Darkfallen Lament", (0.70, 0.50, 0.85)),
                          ("Blood Feast", (0.80, 0.55, 0.35))],
                         SHORT_ENTRIES)
longterm_band("Fleshweaver", "fleshweaver", F, _y_F)
add(spec_group("BM Fleshweaver", F))


# ------------------------------------------- Monstrous Hunger -> Bloodfang
def monstrous_hunger_glow():
    """Glow Bloodfang Bite while the Monstrous Hunger window runs.

    Monstrous Hunger is cited ("pop Monstrous Hunger to turn your next 6
    Bloodfang Bites into halved-GCD enrage hits") but resolves to NO id in
    either database (requirements §6), so it cannot go through PROC_GLOW --
    sid() would record a miss and the build would stop claiming every tracked
    name resolved. The window aura is matched by NAME ONLY, which is exactly
    the claim we can back: if the aura's in-game name differs, the glow never
    fires and the icon is an ordinary cooldown icon.

    Same post-pass shape as Chronomancer's clone/rewind pairing: find by
    NAME, and a pairing that matches nothing is a build failure, not a quiet
    no-op.
    """
    tgt = "BM Eternal Main Bloodfang Bite"
    for c in children:
        if c["id"] != tgt:
            continue
        subs = c.get("subRegions") or {}
        subs = ([subs[k] for k in sorted(k for k in subs if isinstance(k, int))]
                if not isinstance(subs, list) else list(subs))
        subs.append(B.sub_glow(False, "buttonOverlay", (1.0, 0.9, 0.45, 1.0)))
        gi = len(subs)
        c["subRegions"] = B.arr(subs)
        trs = triggers_of(c)
        trs.append(B.aura_trigger(["Monstrous Hunger"], own_only=False))
        c["triggers"] = B._trigger_wrap(trs)
        conds = c.get("conditions") or {}
        conds = ([conds[k] for k in sorted(k for k in conds
                                           if isinstance(k, int))]
                 if not isinstance(conds, list) else list(conds))
        conds.append(B.cond(
            B.T({"trigger": len(trs), "variable": "show", "value": 1}),
            [B.change(f"sub.{gi}.glow", True)]))
        c["conditions"] = B.arr(conds)
        return
    raise SystemExit(
        "monstrous_hunger_glow matched no BM Eternal Main Bloodfang Bite -- "
        "check the eternal main row in resources/abilities-bloodmage.md.")


monstrous_hunger_glow()

W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. Three of the four
# are the contiguous L10 spec passives (92112-92114, the Witch Hunter block
# shape); fleshweaver's slot in that block is not in the digest, so its gate
# is the spec passive that names it outright. Spell Known on a passive is
# proven ground on this fork (Chronomancer's Eternity Warper gate, verified
# in game).
SPEC_KNOWN = {
    "Sanguine": 92112,       # Thirst, the L10 spec passive
    "Accursed": 92113,       # Unchained, the L10 spec passive
    "Eternal": 92114,        # Eternal Curse, the L10 spec passive
    "Fleshweaver": 681079,   # "Fleshweaver Son of Arugal", the Spec Passive
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
