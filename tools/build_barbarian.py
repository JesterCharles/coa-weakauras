"""Build the `Barbarian [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Fourth class through `notes/class-pack-process.md`, first ENERGY class, first
class with a permanent pet (Ancestry's Honored Ancestor). Layout follows
`notes/layout-standard.md`; every factual claim is cited in
`notes/requirements-barbarian.md` and `resources/citations-barbarian.json`.

        [ on TARGET: your bleeds/debuffs ]            <- active-only
        [ on me: enrages, procs, buffs   ]            <- active-only
              [  MAIN ROW - flush        ]
              [  energy bar              ]            <- fixed envelope
              [ offensive cooldowns      ]            <- wraps at 7
              [ defensive + utility      ]            <- wraps at 7
              [ long-term auras          ]            <- active-only

Three things with no precedent in the earlier classes:

  * ENERGY, not mana, on all three specs (Sidekick: 'Resource: Energy' on
    every page). `power_trigger(power_type=3)` -- 3.3.5's energy constant.
    Unverified in game; requirements §6.

  * BRUTALITY'S ENRAGE ECONOMY. Smash 'Requires Enraged', and the spec cycles
    three enrage effects (Unbridled Rage -> Onslaught -> Battle Vigor) so it
    never goes dark. The cue is `spellUsable == 0 -> desaturate` on Smash --
    IsUsableSpell reflects the requirement -- plus the three enrage auras with
    timers in the buff row. No NO-ENRAGE alert: out of combat it would be
    permanently on screen, the Runemaster reminder failure.

  * ANCESTRY'S TANKARD. Fill Level stacks a gauge aura; Ale of The God-King
    wants it FULL, Breath of The North wants it EMPTY. The max stack count is
    UNKNOWN (no source states it), so there is deliberately NO fixed-cell
    gauge: the state cues are PROC_GLOW on the two spenders driven by the
    `Full Tankard` (805814) / `Empty Tankard` (806055) auras, plus the Fill
    Level stack count in the buff row. Cheaper to be right than pretty.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Salts the uids -- WeakAuras dedupes imports on uid, so a rebuilt
# pack MUST carry a different salt or the client silently keeps the old copy.
VERSION = "1.1"

# Only deliberate choices belong here: an entry overrides the CLIENT's own art.
FALLBACK = {}
OVERRIDE = {}

# db.exil.es digest ids corrected by cross-checking (requirements §0):
CROSSCHECK = {
    # The digest links the 560932 Damage component (rank "Damage", no cd row).
    # The castable is 560933: verified on BOTH DBs -- exil.es renders Spell ID
    # + 1 min cooldown + Skill Brutality, ascension's tooltip matches.
    "Maximum Carnage": 560933,
    # exiles' 561397 is the crit-granted PASSIVE ("ranged crits grant you
    # Berserker"). 804141 is the castable candidate: Headhunting skill on both
    # DBs, 1 min cd on ascension. Hedged -- requirements §6.
    "Berserker": 804141,
}

# CD_PER_ROW derives from the NARROWEST main row: Ancestry at 4 icons is
# row_w(4) = 182px, and 28w - 2 <= 1.2 * 182 gives w <= 7.9, so 7. Verified
# against the built packs with tools/rowwidths.py. Do not copy to another class.
CLS = W.init("barbarian", version=VERSION, prefix="BB", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- after init(), see wapack

# Abilities that hold charges rather than a plain cooldown. Both tooltips say
# "3 Charges, 8 sec recharge", and Axe Volley is what Barbaric Whirl becomes on
# Headhunting (L15 passive 570234), sharing Berserker Axe's cooldown.
CHARGES = {"Berserker Axe": 3, "Axe Volley": 3}

# When one of these auras is up, the ability it empowers glows -- the same
# "press this now" cue the game gives.
PROC_GLOW = {
    # The Tankard state cues (requirements §5). Rotation: "Ale of the God-King
    # the instant your Tankard is full", "Breath of the North whenever the
    # Tankard is empty". Both aura ids resolve on both DBs; unverified as
    # player auras in game -- §6.
    "Ale of The God-King": ["Full Tankard"],
    "Breath of The North": ["Empty Tankard"],
}
PROC_STACKS = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            # Mobility, instant bursts and party pulses that leave no self-buff
            # worth a second icon in the buff row.
            no_buff={"Maximum Carnage", "Hodir's Wrath", "Berserker Rush",
                     "Axe Volley"})


# ================================================================== 1. CORE
# Barbarian has NO imbue/engraving-style kit and no class-wide 30-min buff
# family, so the class-wide reminder band is empty: there is nothing whose
# absence is both class-wide and actionable. (The Ancestry missing-pet alert
# is deliberately NOT built: no verified trigger surface reports pet presence
# on this fork, and an alert on an unverified surface is either permanently on
# screen or silently never fires -- requirements §3/§6 defer it to the
# in-game pass.)
CORE = []
add(B.group("BB Core", ROOT, CORE, x=0, y=0))


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Born in Blood is THE class sustain engine (granted by Furious
# Berserker, Vengeance For Zul'jin, Thick Skull, Warband, Savagery...) -- 4s
# base, stacks to 10 since 2026-07-31; the buff_group stack counter shows the
# live count so no cap is hardcoded.
SHORT_ENTRIES = [
    ("Born in Blood", (0.90, 0.30, 0.25), {}),
    ("Defiance", (0.60, 0.85, 1.00), {}),
    ("Thick Skull", (0.80, 0.75, 0.60), {}),
    ("Battle Vigor", (0.95, 0.60, 0.30), {}),
]


def energy_bar(gid, parent, y, w, h=None):
    """Energy, the class resource on all three specs.

    Same shape as the engine's mana_bar with power_type 3 (energy on 3.3.5)
    and the classic yellow. First energy class in the pack -- the power type
    is read off the client convention, not verified in game (§6).
    """
    add(B.aurabar(gid, parent, [B.power_trigger("player", 3)],
                  x=0, y=y, w=w, h=h or BAR_H, color=(1.00, 0.82, 0.10, 1.0),
                  subregions=[
                      B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                 justify="RIGHT"),
                  ]))
    return gid


LONGTERM_COL = {
    "Shout": (0.95, 0.60, 0.30),
    "Spirit": (0.55, 0.75, 1.00),
    "Aura": (0.95, 0.85, 0.45),
}


def _family(name):
    if "Shout" in name:
        return "Shout"
    if name.startswith("Spirit of"):
        return "Spirit"
    return "Aura"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    Shouts (30 min party buffs), Spirit auras ("only 1 Spirit spell active at
    a time") and the always-on party auras. Active-only, checked once per
    pull. Same per-spec shape Chronomancer and Pyromancer settled on -- a
    shared Core band would need a fixed offset clearing the deepest spec.
    """
    band = f"BB {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"BB {spec_name} Longterm {name}", band,
            # id AND name: several of these are unranked but generic-named.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"BB {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# ============================================================== 2. BRUTALITY
# Enrage-fuelled melee cleave (Sidekick: "Closest to retail Fury Warrior").
# Main row is the cited loop: "Smash and Ancestral Strike as your Energy
# fillers -> Brutal Swing when 2+ targets are clumped -> Crush to stun ->
# Decapitate below 35%", with Barbaric Whirl for 3+ pulls. Smash desaturates
# whenever no enrage is active (spellUsable), which is the anti-"goes dark"
# cue the enrage cycle needs.
BR = []
BR.append(cd_group("BB Brutality Main", "BB Brutality",
                   ["Smash", "Ancestral Strike", "Brutal Swing",
                    "Barbaric Whirl", "Crush", "Decapitate"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="brutality"))
BR.append(energy_bar("BB Brutality Energy", "BB Brutality", Y_BAR_SOLO,
                     w=row_w(6)))
# Carnage is the one enemy-side state the spec tracks: "Some attacks consume
# Carnage for increased effect. Stacks 5 times." Matched by id OR name -- the
# stack aura's provenance is a talent chain, so exact-id could miss it.
BR.append(dot_bars("BB Brutality Target", "BB Brutality",
                   [("Carnage", (0.90, 0.45, 0.25), {"by_name": True})],
                   y=Y_TARGET, refresh_at=None))
_y_BR = emit_bottom_block("Brutality", "brutality",
                          BR,
                          [("Unbridled Rage", (1.00, 0.55, 0.25)),
                           ("Onslaught", (1.00, 0.80, 0.35)),
                           ("Blood Pact", (0.85, 0.35, 0.35)),
                           ("Fervor", (1.00, 0.70, 0.45)),
                           ("Bloodthirsty Rage", (0.95, 0.40, 0.30))],
                          SHORT_ENTRIES)
longterm_band("Brutality", "brutality", BR, _y_BR)
add(spec_group("BB Brutality", BR))


# ============================================================ 3. HEADHUNTING
# Thrown-weapon melee/ranged weave (Sidekick: "Closest to retail Survival
# Hunter"). The cited priority: "maintain Puncture Wounds uptime (Spear
# crits) > Berserker Rush on cooldown > Axe Twirling > Barbed Spear >
# Berserker during Enrage > filler Throw Weapon/Berserker Axe". The bleed
# uptime lives in the target band; the main row is the press loop.
HH = []
HH.append(cd_group("BB Headhunting Main", "BB Headhunting",
                   ["Barbed Spear", "Throw Weapon", "Berserker Axe",
                    "Gutspiller", "Impaling Spear"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="headhunting"))
HH.append(energy_bar("BB Headhunting Energy", "BB Headhunting", Y_BAR_SOLO,
                     w=row_w(5)))
# Your bleeds and debuffs on the target. Puncture Wound (804143, 6s) is
# priority #1 to keep rolling; Guts Spilled (520577) is Gutspiller's 12s
# bleed; Barbed Spear's row is its 10s -30% healing cut.
HH.append(dot_bars("BB Headhunting Target", "BB Headhunting",
                   [("Puncture Wound", (0.90, 0.30, 0.25), {"by_name": True}),
                    ("Guts Spilled", (0.80, 0.45, 0.30), {"by_name": True}),
                    ("Barbed Spear", (0.70, 0.60, 0.40), {})],
                   y=Y_TARGET, refresh_at=2))
_y_HH = emit_bottom_block("Headhunting", "headhunting",
                          HH,
                          # Axe Twirling is a TOGGLE since 2026-07-31 (no cd,
                          # no duration, -15% damage while on): its whole
                          # tracker is this active-only aura icon.
                          [("Axe Twirling", (1.00, 0.75, 0.30)),
                           ("Unbridled Rage", (1.00, 0.55, 0.25)),
                           ("Berserker", (0.95, 0.50, 0.35)),
                           ("Onslaught", (1.00, 0.80, 0.35))],
                          SHORT_ENTRIES)
longterm_band("Headhunting", "headhunting", HH, _y_HH)
add(spec_group("BB Headhunting", HH))


# ================================================================ 4. ANCESTRY
# Enhancement-shaman-shaped support melee with the permanent Honored Ancestor
# pet. Main row is the numbered rotation: "1) Keep Ancestral Combat rolling
# 2) Keg Smash on cooldown 3) Ale of the God-King the instant your Tankard is
# full 4) Breath of the North whenever the Tankard is empty". The Tankard
# state cues are the Full/Empty glows on the two spenders (PROC_GLOW above);
# Fill Level's live stack count sits in the buff row -- no fixed-cell gauge,
# because its maximum is UNKNOWN (§6) and an invented cap would be a lie
# drawn 16px tall.
AN = []
AN.append(cd_group("BB Ancestry Main", "BB Ancestry",
                   ["Ancestral Combat", "Keg Smash", "Ale of The God-King",
                    "Breath of The North"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="ancestry"))
AN.append(energy_bar("BB Ancestry Energy", "BB Ancestry", Y_BAR_SOLO,
                     w=row_w(4)))
_y_AN = emit_bottom_block("Ancestry", "ancestry",
                          AN,
                          # Fill Level by name (the 92083 passive teaches it;
                          # the stack aura may carry its own id, and the name
                          # covers both). Full/Empty Tankard are the state
                          # auras the spender glows key off -- shown here too
                          # so the state is readable even mid-glow.
                          [("Fill Level", (0.95, 0.80, 0.45)),
                           ("Full Tankard", (1.00, 0.85, 0.30)),
                           ("Empty Tankard", (0.55, 0.75, 1.00)),
                           ("Ancestral Combat", (0.55, 0.85, 1.00)),
                           ("Frozen Blades", (0.60, 0.90, 1.00)),
                           ("Ramhorn Rage", (0.45, 0.90, 0.55))],
                          SHORT_ENTRIES)
longterm_band("Ancestry", "ancestry", AN, _y_AN)
add(spec_group("BB Ancestry", AN))


# ------------------------------------------------------------------ merge
MERGE_BANDS = ("Main", "Buffs")
W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# Group triggers/conditions/load are INERT -- every leaf carries its own gate.
# One spell only that spec knows, for load.use_spellknown. Chosen as the
# lowest-level spec-unique UNRANKED castable (spell-meta is_castable), because
# IsSpellKnown is exact and a ranked or component id fails silently:
#   Brutality    Break 560934          L14, unranked, brutality skillbook
#   Headhunting  Deathmatch 800950     unranked castable; the only clean one
#                                      the spec has (level unknown -- §6)
#   Ancestry     Ancestral Combat 801782  L17, the spec's own engine button
SPEC_KNOWN = {
    "Brutality": 560934,
    "Headhunting": 800950,
    "Ancestry": 801782,
}
W.configure(spec_known=SPEC_KNOWN)

_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()
W.chain_ladder()
if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    W.finish((_GATED, _ANY, _CLASSED))
