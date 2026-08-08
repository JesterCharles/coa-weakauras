"""Build the `Venomancer [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Class CONTENT over the shared engine (`tools/wapack.py`) in the Chronomancer
shape -- no convergence flags. Requirements: `notes/requirements-venomancer.md`.
Third FOUR-spec class through the pipeline, with one spec of each role plus a
second damage spec: Fortitude (tank, Rage), Rot (ranged DoT caster, mana),
Stalking (melee builder/finisher, Energy + Brood Marks), Vizier (HoT healer,
mana). Roles are Sidekick-cited, pending in-game (resources/spec-roles.md).

        [ alerts: NO VENOM / NO <FORM> ]              <- active-only
        [ on TARGET: your DoTs / your HoTs ]          <- active-only
        [ on me: procs, stacks, running CDs ]         <- active-only
              [  MAIN ROW - flush         ]
              [  resource envelope        ]           <- fixed height
              [ offensive cooldowns       ]           <- wraps at 11
              [ defensive + utility       ]           <- wraps at 11
              [ long-term: form + venoms  ]           <- active-only

Three things without an analogue in the earlier classes:

  * THE VENOM SYSTEM is the class stance-family: 2-hour self-buffs, "You can
    have a maximum of 2 unique Venoms active at a time", and every spec's
    cited rotation activates them. So the class-wide alert is NO VENOM --
    fires only when ZERO venom auras are up, never per-venom, because which
    2 of 7 you run is a choice (the NO BOON / NO WISDOM shape).

  * BROOD MARKS LIVE ON THE TARGET (804972, no duration since 07/31), so the
    stalking "combo point" meter renders in the TARGET BAND with a stack
    count rather than as an envelope stack bar: per-target state must vanish
    on retarget, which the target band does for free and an envelope bar
    would fake.

  * EXPOSED FLESH IS A DEBUFF ON YOURSELF that fortitude deliberately banks
    and sheds; its stack cap is unknown (Unbreakable raises it), so it is an
    on-me stack count (helpful=False), not a segmented bar (requirements §6).

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT. Never imported in game; the inventory roles were
# machine-proposed with cited reasoning and bulk-cleared (recorded in
# buildlog-venomancer.json), and requirements §6 lists what only the client
# can settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
# EMPTY on purpose. 18 drawn names have no art on db.ascension.gg (the
# build's own survey lists them), and the Hasten lesson says leave exactly
# these to resolve from the trigger: iconSource stays -1, so the CLIENT's own
# spell texture -- which exists even where the database serves a
# questionmark, and is what the player recognises from their action bar --
# wins at runtime. A placeholder picked from a scrape drew the wrong art for
# Hasten; do not "fix" these with invented texture names.
FALLBACK = {}
# db.ascension.gg serves no art for these names' resolved ids (build survey,
# 2026-08-08). Deliberately NOT given art -- they draw from the trigger in
# game. Listed so a future run does not re-litigate them.
NO_UPSTREAM_ART = {
    "Exposed Flesh", "Widow's Kiss", "Beetle Form", "Beetle Pheromones",
    "Greater Beetle Pheromones", "Carapace Crash", "Hivebreak",
    "Serpent's Fang", "Shadra's Balm", "Miasma", "Sepsis Bloom", "Brood Trap",
    "Fungify", "Spindlebind", "Venomwing Form",
}
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own art
# for the spell. None yet.
OVERRIDE = {}
# db.exil.es points at a COMPONENT of the ability rather than the ability --
# the component is never castable and never known, so the icon draws wrong
# art AND its gate silently fails. Corrections are name -> id from
# db.ascension.gg's own name search, both tooltips read; an in-game tooltip
# outranks them (resources/in-game-verified.json).
CROSSCHECK = {
    # 503929 is rank "Damage", the summon's damage effect. 504344 is the
    # castable on ascension: "11% of base mana, Instant, 1 min cooldown,
    # Summon a Fungarian... instantly apply Debilitating Venom" -- the exact
    # cited ability.
    "Fungal Assailant": 504344,
    # 504351 is rank "proc" (empty tooltip). 504352 is the castable: "19% of
    # base mana, 3 min cooldown, Envelop an ally... reducing all damage taken
    # by 20%".
    "Shadra's Aid": 504352,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- all four
# venomancer main rows are six 44px icons (row_w(6) = 274px), and the rule
# `28w - 2 <= 1.2 * 274` allows w <= 11.8 -> 11. Confirmed against the built
# packs by tools/rowwidths.py. Do NOT copy this number to another class.
CLS = W.init("venomancer", version=VERSION, prefix="VN", cd_per_row=11,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# Abilities that hold charges rather than a plain cooldown. Counts are
# tooltip-read: Alkahest "2 Charges, 12 sec recharge", Carapace Regeneration
# "3 Charges, 20 sec recharge", Skitter "dashes on three charges" ("Can be
# used 3 times within before triggering a cooldown"), Spindlebind 2 under the
# Tunneler talent (count harmless on the untalented version -- the Fabric of
# Time precedent).
CHARGES = {"Alkahest": 2, "Carapace Regeneration": 3, "Skitter": 3,
           "Spindlebind": 2}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that
# light it, taken from the spec pages' own text (aura names assumed to match
# the granting talent; requirements §6).
PROC_GLOW = {
    # "Rot Lich can reset and grant an instant Serpent's Fang" (L10 spec
    # passive 92142: "20% chance to reset the cooldown of Serpent's Fang").
    "Serpent's Fang": ["Rot Lich"],
    # "increase the healing of your next Shadra's Prayer by 20% and make it
    # instant cast" (Surprise Strategy, class kit).
    "Shadra's Prayer": ["Surprise Strategy"],
    # "Skulk (stealth) makes Venom Fang free and hard-hitting for openers";
    # "Death Spray: chance to remove the Energy cost from your next Venom
    # Fang... and increase its damage by 20%".
    "Venom Fang": ["Skulk", "Death Spray"],
}
# Of those, the ones whose proc also STACKS. None: Skulk, Rot Lich, Death
# Spray and Surprise Strategy are all single-shot windows.
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: summons, ground zones, target debuff CDs and instant heals.
# A name missing from here costs nothing but a display that never shows; a
# name wrongly here hides a running cooldown, so only the unambiguous cases
# are listed.
NO_BUFF = {"Fungal Assailant", "Mycelial Ring", "Suffocating Coil",
           "Venoxis Fang", "Rime", "Sepsis Bloom", "Decay", "Miasma",
           "Hive Instinct", "Toxic Communion", "Unity", "Toxic Sludge",
           "Toxflinger", "Serpent's Fang"}

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own cooldown stack. Venomancer's long-term
# content is inventory-driven, three families:
#
#   Venom  2-hour self-buffs, "maximum of 2 unique Venoms active at a time".
#   Form   the shapeshift stances (Beetle / Weaver / Spider / Vizier).
#   other  pheromones and Envenomed Weapons -- 30-min ally buffs, the
#          Instinct shape ("Does not stack with other similar effects").
LONGTERM_COL = {
    "Venom": (0.55, 0.90, 0.45),
    "Form": (0.95, 0.85, 0.45),
    "other": (0.75, 0.70, 1.00),
}


def _family(name):
    low = name.lower()
    if "venom" in low:
        return "Venom"
    if "form" in low:
        return "Form"
    return "other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `VN <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. Three of the four gates are the L10 Specialization passives;
    Vizier's is L20 (requirements §6), so a level-10-19 vizier misses this
    band -- forms and venoms are later content anyway.
    """
    band = f"VN {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"VN {spec_name} Longterm {name}", band,
            # By id AND name: several venom/form rows are teaching-passive or
            # proc-shaped ids (requirements §6), so the aura is matched by
            # either -- covering both failure shapes.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"VN {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Tome of Ahn'kahet (next spell free) and Surprise Strategy (next
# Shadra's Prayer instant) are class procs; Harden and Lifeblood are the two
# class defensives, which live in the utility row that cd_buffs does not
# derive from, so their running state is listed here explicitly.
SHORT_ENTRIES = [
    ("Tome of Ahn'kahet", (1.00, 0.85, 0.40), {}),
    ("Surprise Strategy", (0.60, 0.95, 0.80), {}),
    ("Harden", (0.75, 0.75, 0.60), {}),
    ("Lifeblood", (0.55, 0.90, 0.55), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# High and central, and invisible once you are buffed -- fires only on
# ABSENCE. Every spec's cited rotation activates a Venom and they are limited
# to 2 of 7, so "no Venom at all" is a real, class-wide, actionable gap.
# Nagging per-venom would be permanently on screen for the five you
# deliberately did not take -- the exact failure Runemaster's reminder band
# had. The trigger matches ANY venom by id or name, and the alert shows only
# when none of them is up.
#
# NOT any of the four Forms here: forms are per-spec and two of them are
# actively shifted OUT of mid-fight (requirements §1/§6), so the form alerts
# live in the spec blocks below and only where the kit text is explicit.
ALERTS = []
_VENOMS = sorted(n for n, a in ABILITIES.items()
                 if a["default"] == "longterm" and _family(n) == "Venom")
if _VENOMS:
    ALERTS.append(add(B.icon(
        "VN Alerts No Venom", "VN Alerts",
        [B.aura_trigger([str(ABILITIES[n]["id"]) for n in _VENOMS] + _VENOMS,
                        own_only=False, show_on="showOnMissing")],
        ic("Adrenal Venom"), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text("NO VENOM", size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])))

add(B.dynamicgroup("VN Alerts", "VN Core", ALERTS, x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
CORE.append("VN Alerts")
add(B.group("VN Core", ROOT, CORE, x=0, y=0))


def form_alert(spec_name, form_name, label, bands):
    """Per-spec NO <FORM> alert -- the show-on-missing shape, spec-gated.

    Only for the two specs whose kit text is explicit that the form IS the
    rotation: stalking ("Requires Spider Form" on the finishers) and vizier
    ("Pre-pull: Vizier Form up"). Beetle and Weaver Form are swapped in and
    out deliberately, so alerting on them would nag correct play
    (requirements §6).
    """
    gid = f"VN {spec_name} Alerts"
    sid_ = ABILITIES[form_name]["id"]
    add(B.icon(
        f"{gid} No {form_name}", gid,
        [B.aura_trigger([str(sid_), form_name], own_only=False,
                        show_on="showOnMissing")],
        ic(form_name), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text(label, size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))]))
    add(B.dynamicgroup(gid, f"VN {spec_name}", [f"{gid} No {form_name}"],
                       x=0, y=Y_ALERT, grow="HORIZONTAL", space=6))
    bands.append(gid)


# ================================================================ 2. FORTITUDE
# THE TANK (spec-roles.md; Brewmaster analog). Press order from the cited
# rotation: Chitin Rush is "your main rage-spender", Venomtip Poison the wide
# DoT + attack-speed slow, Hivebreak before Carapace Crash because Toxic
# Expulsion makes Hivebreak the Venomtip consumer, Barbed Stinger the
# single-target Nature amp + shed, Expulsion the AoE shed payout. The other
# shed (Regrow Exoskeleton, off-GCD 1 min) is the defensive row's lead.
# Rage only: "Its buttons all spend Rage".
F = []
F.append(cd_group("VN Fortitude Main", "VN Fortitude",
                  ["Chitin Rush", "Venomtip Poison", "Hivebreak",
                   "Carapace Crash", "Barbed Stinger", "Expulsion"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="fortitude"))
_w_F = row_w(6)
_gid = "VN Fortitude Rage"
add(B.aurabar(_gid, "VN Fortitude", [B.power_trigger("player", 1)],
              x=0, y=Y_BAR_SOLO, w=_w_F, h=BAR_H_SOLO,
              color=(0.85, 0.30, 0.25, 1.0),
              subregions=[B.sub_text("%p", size=10, anchor="INNER_RIGHT",
                                     x=-4, justify="RIGHT")]))
F.append(_gid)
# The tank's maintained pressure on the target: Venomtip's DoT/slow, the
# crit-applied Wicked Poison, and Barbed Stinger's vulnerability window (the
# rider's own name is unresolved -- requirements §6 -- so both by name).
F.append(dot_bars("VN Fortitude Target", "VN Fortitude",
                  [("Venomtip Poison", (0.55, 0.90, 0.45), {}),
                   ("Wicked Poison", (0.80, 0.45, 0.35), {"by_name": True}),
                   ("Barbed Stinger", (0.95, 0.75, 0.40), {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_F = emit_bottom_block("Fortitude", "fortitude", F,
                         [("Exposed Flesh", (0.95, 0.45, 0.35),
                           {"helpful": False}),
                          ("Alacrity", (0.60, 0.85, 1.00), {}),
                          ("Protogenesis", (0.55, 0.90, 0.55), {}),
                          ("Carapace Regeneration", (0.75, 0.75, 0.60), {}),
                          ("Regrow Exoskeleton", (0.80, 0.70, 1.00), {})],
                         SHORT_ENTRIES)
longterm_band("Fortitude", "fortitude", F, _y_F)
add(spec_group("VN Fortitude", F))


# ===================================================================== 3. ROT
# Ranged DoT caster (Affliction analog). Press order from the cited rotation:
# "apply Wilt and Spore, then Venom Bolt and Serpent's Fang to build Fungal
# Growth... Cast Mycosis for a big direct hit plus the healing-absorb shield.
# Layer Decay for the AoE mushroom burst." Mana only.
R = []
R.append(cd_group("VN Rot Main", "VN Rot",
                  ["Wilt", "Spore", "Venom Bolt", "Serpent's Fang",
                   "Mycosis", "Decay"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="rot"))
R.append(mana_bar("VN Rot Mana", "VN Rot", Y_BAR_SOLO,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(6)))
# The maintained-DoT read that IS this spec: "Managing DoT refreshes so you
# aren't re-applying early is the main way to stretch the pool." Venom Bolt
# stacks a healing cut; Mycosis carries the healing-absorb shield; Fungal
# Growth is the ramp ON THE TARGET (30s aura 804971, granted by a passive,
# so by name).
R.append(dot_bars("VN Rot Target", "VN Rot",
                  [("Wilt", (0.55, 0.90, 0.45), {}),
                   ("Spore", (0.70, 0.60, 1.00), {}),
                   ("Venom Bolt", (0.45, 0.80, 0.55), {}),
                   ("Mycosis", (0.90, 0.75, 0.40), {}),
                   ("Suffocating Coil", (0.60, 0.75, 0.95), {}),
                   ("Fungal Growth", (0.95, 0.55, 0.85), {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_R = emit_bottom_block("Rot", "rot", R,
                         [("Rot Lich", (0.80, 0.55, 1.00), {}),
                          ("Cycle of Decay", (0.60, 0.90, 0.60), {}),
                          ("A Pit of Snakes", (0.95, 0.85, 0.45), {})],
                         SHORT_ENTRIES)
longterm_band("Rot", "rot", R, _y_R)
add(spec_group("VN Rot", R))


# ================================================================ 4. STALKING
# Melee builder/finisher (Feral analog). Press order from the cited rotation:
# Venom Fang builds Marks, Nerubian Sting "on cooldown", Withering Venom
# "ramp its DoT alongside" (and generates a Mark since 07/31), then the
# Mark-consuming finishers Facemelter / Rotfang, and Widowmaker under 35%.
# Energy primary + a separate mana pool for the utility layer (minor).
S = []
form_alert("Stalking", "Spider Form", "NO SPIDER FORM", S)
S.append(cd_group("VN Stalking Main", "VN Stalking",
                  ["Venom Fang", "Nerubian Sting", "Withering Venom",
                   "Facemelter", "Rotfang", "Widowmaker"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="stalking"))
_w_S = row_w(6)
_gid = "VN Stalking Energy"
add(B.aurabar(_gid, "VN Stalking", [B.power_trigger("player", 3)],
              x=0, y=Y_BAR, w=_w_S, h=BAR_H_STACKED,
              color=(0.95, 0.85, 0.25, 1.0),
              subregions=[B.sub_text("%p", size=10, anchor="INNER_RIGHT",
                                     x=-4, justify="RIGHT")]))
S.append(_gid)
_gid = "VN Stalking Mana"
add(B.aurabar(_gid, "VN Stalking", [B.power_trigger("player", 0)],
              x=0, y=Y_SEG, w=_w_S, h=10, color=(0.30, 0.45, 0.95, 1.0)))
S.append(_gid)
# Brood Mark leads the band: it is the spec meter, ON THE TARGET on purpose
# (per-target state vanishes on retarget -- an envelope bar would fake it).
# No duration since 07/31, so the stacks carry the read and %p stays empty.
S.append(dot_bars("VN Stalking Target", "VN Stalking",
                  [("Brood Mark", (0.95, 0.85, 0.45), {"by_name": True}),
                   ("Withering Venom", (0.55, 0.90, 0.45), {}),
                   ("Facemelter", (0.90, 0.60, 0.30), {}),
                   ("Rotfang", (0.75, 0.55, 0.35), {}),
                   ("Nerubian Sting", (0.70, 0.60, 1.00), {})],
                  y=Y_TARGET, refresh_at=4))
_y_S = emit_bottom_block("Stalking", "stalking", S,
                         [("Skulk", (0.60, 0.60, 0.85), {}),
                          ("Widow's Kiss", (0.95, 0.55, 0.75), {}),
                          ("Acidfang", (0.60, 0.90, 0.60), {})],
                         SHORT_ENTRIES)
longterm_band("Stalking", "stalking", S, _y_S)
add(spec_group("VN Stalking", S))


# ================================================================== 5. VIZIER
# THE HEALER (spec-roles.md). Raid frames stay out (VuhDo/Grid own that on
# 3.3.5a); the target band carries what YOU have on whoever you are
# targeting. Press order from the cited text: "Lead with Serpent's Fang into
# your HoTs -- Shadra's Prayer, Balm, Mending Mist"; Green Salve the fast
# seeking heal; Alkahest's charges top and extend Shadra's Prayer. Pure mana.
V = []
form_alert("Vizier", "Vizier Form", "NO VIZIER FORM", V)
V.append(cd_group("VN Vizier Main", "VN Vizier",
                  ["Serpent's Fang", "Shadra's Prayer", "Shadra's Balm",
                   "Mending Mist", "Green Salve", "Alkahest"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="vizier"))
V.append(mana_bar("VN Vizier Mana", "VN Vizier", Y_BAR_SOLO,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(6)))
# helpful=True: on a FRIENDLY target this shows what YOU have on them -- the
# HoT blanket, the Vigil amp, and the Shadra's Aid save. Vigil and
# Rejuvenating Venom are passive/venom-applied, so by name.
V.append(dot_bars("VN Vizier Target", "VN Vizier",
                  [("Shadra's Prayer", (0.55, 0.90, 0.55), {}),
                   ("Shadra's Balm", (0.45, 0.80, 0.95), {}),
                   ("Green Salve", (0.60, 0.95, 0.60), {}),
                   ("Mending Mist", (0.70, 0.85, 1.00), {}),
                   ("Shadra's Vigil", (0.95, 0.85, 0.45), {"by_name": True}),
                   ("Shadra's Aid", (0.80, 0.70, 1.00), {"by_name": True}),
                   ("Rejuvenating Venom", (0.90, 0.60, 0.80),
                    {"by_name": True})],
                  y=Y_TARGET, unit="target", helpful=True, refresh_at=4))
_y_V = emit_bottom_block("Vizier", "vizier", V,
                         [("Venom Shield", (0.60, 0.75, 0.95), {})],
                         SHORT_ENTRIES)
longterm_band("Vizier", "vizier", V, _y_V)
add(spec_group("VN Vizier", V))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. Three are the L10
# Specialization passives (the contiguous 92142-44 block); Vizier's L10
# passive (Shadra's Vigil) has no resolvable teaching id -- 505203 is the 20s
# aura -- so its gate is Serpent's Mist, the L20 Specialization (requirements
# §6: a vizier below 20 loses spec displays, the documented trade). Spell
# Known on a Specialization passive is proven ground on this fork
# (Chronomancer's Eternity Warper gate, verified in game; Primalist's four).
SPEC_KNOWN = {
    "Fortitude": 92144,    # Exposed Flesh, the L10 passive
    "Rot": 92142,          # Rot Lich, the L10 passive
    "Stalking": 92143,     # Brood Marks, the L10 passive
    "Vizier": 573305,      # Serpent's Mist, the L20 passive (see above)
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
