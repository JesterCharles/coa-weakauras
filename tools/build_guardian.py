"""Build the `Guardian [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Sixteenth class through `notes/class-pack-process.md`. Layout follows
`notes/layout-standard.md`; every factual claim is cited in
`notes/requirements-guardian.md` and `resources/citations-guardian.json`.

        [ NO REINFORCEMENT alert         ]            <- per spec, active-only
        [ on TARGET: your debuffs/bleeds ]            <- active-only
        [ on me: blocks, stacks, procs   ]            <- active-only
              [  MAIN ROW - flush        ]
              [  energy bar              ]            <- fixed envelope
              [ offensive cooldowns      ]            <- wraps at 7
              [ defensive + utility      ]            <- wraps at 7
              [ long-term: imbues+stances]            <- active-only

Three things that define this class (requirements doc, top):

  * BLOCK, NOT ABSORBS. The batch brief predicted an absorb economy; measured
    reality is ZERO absorb mentions against ~90 block mentions. The defensive
    economy renders as Raise Shield/Brace/Counter Stance cooldowns, on-block
    stack auras (Vanguard's Shield, Fine Plating) in the on-me row, and
    Reprisal's only-after-a-block requirement carried by spellUsable
    desaturation. No bubble band exists because there are no bubbles.

  * ENERGY on all three specs (Sidekick: 'Resource: Energy' on every page).
    `power_trigger(power_type=3)`, the barbarian precedent -- still
    unverified in game (requirements §6). Glory (3) / Favor (20) / Tempo (3)
    are proc-stack states consumed automatically, not spent resources, so
    they are stack counts in the on-me row, not invented gauges (the Tankard
    precedent).

  * SHIELD REINFORCEMENTS are the engraving analogue: five 1-hour shield
    imbues, per spec. Long-term band + a per-spec NO REINFORCEMENT alert that
    fires only when none of that spec's imbues is up AND the imbue spell is
    known (the KX stance-alert shape, so a levelling character is not nagged).

Spec roles (Sidekick-cited, resources/spec-roles.md): vanguard tank,
inspiration support-damage (no ally heal), gladiator damage. No spec heals,
so every target band is helpful=False.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Salts the uids -- WeakAuras dedupes imports on uid, so a rebuilt
# pack MUST carry a different salt or the client silently keeps the old copy.
VERSION = "0.2"

# Only deliberate choices belong here: an entry overrides the CLIENT's own art.
FALLBACK = {}
OVERRIDE = {
    # Two pairs share art upstream and sit in the same utility row. Both
    # replacements are textures the class's own sources carry:
    # Counter Stance's talent-tree art is `counterstanceguardian` (its db rows
    # wear Guard's ability_warrior_vigilance), and Freedom takes Hand of
    # Freedom's classic 3.3.5 texture over Liberation's shared medallion.
    "Counter Stance": "counterstanceguardian",
    "Freedom": "spell_holy_sealofvalor",
}

# db.exil.es digest ids corrected by cross-checking (requirements §0):
CROSSCHECK = {
    # The digest links 503114, a stale line-hit+slow version whose ascension
    # record is empty. BOTH DBs carry 806220 with the live absorb-destroyer
    # text matching the Sidekick kit (1 min cd, 30% energy).
    "Linebreaker": 806220,
    # 704157 is the L24 rank-"Damage" component; the castable is 801219
    # (rank null, L58, full AE-tree tooltip verbatim on both DBs).
    "Press the Attack": 801219,
    # 300926 is the rank-Passive grantor; the castable is 355779 (rank null,
    # L20, "reflect the next harmful spell... within 3 sec" on both DBs).
    "Reflective Shield": 355779,
    # Aura-only names the buff row draws, absent from the exil.es digest.
    # Both ride [id, name] any-of triggers, so the name is the safety net if
    # the granted aura carries a different id (requirements §6).
    "High Guard": 707621,      # L50 row on ascension (504384/504586 are the
                               # L29/L34 rank steps, same art)
    "Favor": 704322,           # the L50 row the official talents payload
                               # names; three sibling ids share its art
}

# CD_PER_ROW derives from the NARROWEST main row: vanguard and inspiration at
# 4 icons are row_w(4) = 182px, and 28w - 2 <= 1.2 * 182 gives w <= 7.9, so 7.
# Verified against the built packs with tools/rowwidths.py. Do not copy.
CLS = W.init("guardian", version=VERSION, prefix="GD", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- after init(), see wapack

# Abilities that hold charges rather than a plain cooldown. Reprisal's tooltip
# says "2 Charges, 6 sec recharge" on both DBs. Inspiration's "Ram and Ballad
# run on charge bars" prose has NO charge count in any DB row (requirements
# §6), so no number is invented for them.
CHARGES = {"Reprisal": 2}

# When one of these auras is up, the ability it empowers glows -- the same
# "press this now" cue the game gives.
PROC_GLOW = {
    # High Guard (L50 vanguard): "your next Heavy Blow within 15 seconds
    # triggers no cooldown", granted by Raise Shield / Advance / Battle Rush.
    # Aura id 707621 from the talents payload -- unverified in game, §6.
    "Heavy Blow": ["High Guard"],
    # Elegant Combat (inspiration proc, 524615): "Casting a Ballad has a
    # chance to remove the cost of the next Ram and increase its critical
    # chance". Aura name unverified in game -- §6.
    "Ram": ["Elegant Combat"],
    # Harrowing Melody rider: "your next Ballad within ... is free of cost and
    # deals % increased damage". Keyed to the aura by name -- §6.
    "Ballad of the Conqueror": ["Harrowing Melody"],
    "Ballad of the Dragonslayer": ["Harrowing Melody"],
}
PROC_STACKS = set()

# Displays whose extra trigger is a GATE (missing-aura AND spell-known), so
# they must keep `disjunctive` at its "all" default. Filled by the alert
# builder below; configure() hands it to apply_leaf_gates.
NEEDS_ALL = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            # Mobility, instant strikes and ground effects that leave no
            # self-buff worth a second icon in the buff row.
            no_buff={"Hammer of the Law", "Bastion Slam", "Linebreaker",
                     "Shieldforge", "Motivating Strike", "Final Verdict",
                     "Grand Entrance", "Glorious Arena", "Song of Battle"})


# ================================================================== 1. CORE
# Guardian's class-wide reminder is the Reinforcement alert, but the imbues
# are PER SPEC (Spiked=vanguard, Weighted/Jagged=gladiator, Magic/Poised=
# inspiration), so the alerts live in the spec blocks where the spec gate
# applies. Core itself carries nothing.
CORE = []
add(B.group("GD Core", ROOT, CORE, x=0, y=0))


# Class-wide short buffs, merged into every spec's "what is up right now" row.
SHORT_ENTRIES = [
    # 8 parry charges, heals when one fires -- worth seeing it run.
    ("Counter Stance", (0.80, 0.75, 0.60), {}),
    # -50% damage taken window.
    ("Brace", (0.60, 0.85, 1.00), {}),
    # the block window everything keys off; resets via King's Guard /
    # Refuse To Die / Deflector show on its cd icon, the running state here.
    ("Raise Shield", (0.95, 0.85, 0.45), {}),
    ("Reflective Shield", (0.55, 0.75, 1.00), {}),
]


def energy_bar(gid, parent, y, w, h=None):
    """Energy, the class resource on all three specs.

    Same shape as the engine's mana_bar with power_type 3 (energy on 3.3.5)
    and the classic yellow -- the barbarian precedent; the power type is the
    client convention, not yet verified in game (requirements §6).
    """
    add(B.aurabar(gid, parent, [B.power_trigger("player", 3)],
                  x=0, y=y, w=w, h=h or BAR_H, color=(1.00, 0.82, 0.10, 1.0),
                  subregions=[
                      B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                 justify="RIGHT"),
                  ]))
    return gid


# The five shield Reinforcements -- Guardian's engraving analogue. 1-hour
# imbues, per spec; ids resolve on BOTH DBs (requirements §1).
REINFORCEMENTS = {
    "vanguard": [("Spiked Reinforcement", 653131)],
    "gladiator": [("Weighted Reinforcement", 653277),
                  ("Jagged Reinforcement", 653279)],
    "inspiration": [("Magic Reinforcement", 653280),
                    ("Poised Reinforcement", 653278)],
}


# The alert fires on ABSENCE, so no trigger can supply art -- displayIcon must
# be real or it renders as a "?". Magic/Poised Reinforcement have no upstream
# art, so Inspiration's alert borrows Weighted's texture, which cannot clash:
# Weighted never appears in any Inspiration row (the Chronomancer override
# precedent).
ALERT_ART = {
    "vanguard": "Spiked Reinforcement",
    "gladiator": "Weighted Reinforcement",
    "inspiration": "Weighted Reinforcement",
}


def reinforcement_alert(spec_name, spec_key, bands):
    """NO REINFORCEMENT: fires when NONE of the spec's shield imbues is up
    AND the lowest-level imbue spell is known (the KX stance-alert shape --
    a levelling character who cannot imbue yet is not nagged)."""
    band = f"GD {spec_name} Alerts"
    auras = REINFORCEMENTS[spec_key]
    keys = [str(i) for _n, i in auras] + [n for n, _i in auras]
    gate_id = auras[0][1]                        # first entry IS the low-level one
    d = B.icon(
        f"{band} No Reinforcement", band,
        [B.aura_trigger(keys, own_only=False, show_on="showOnMissing"),
         B.spell_known_trigger(gate_id, exact=False)],
        ic(ALERT_ART[spec_key]), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text("NO REINFORCEMENT", size=10,
                               anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
    NEEDS_ALL.add(d["id"])       # missing-aura AND spell-known, never "any"
    add(d)
    add(B.dynamicgroup(band, f"GD {spec_name}", [d["id"]], x=0, y=Y_ALERT,
                       grow="HORIZONTAL", space=6))
    bands.append(band)


LONGTERM_COL = {
    "Reinforcement": (0.95, 0.85, 0.45),
    "Formation": (0.55, 0.75, 1.00),
    "Pose": (0.55, 0.75, 1.00),
    "Honor": (0.95, 0.60, 0.30),
}


def _family(name):
    for key in LONGTERM_COL:
        if key in name:
            return key
    return "Honor"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack:
    shield Reinforcements (1 hr), Formations/Poses (dur -1 stances), and the
    30-min Honor declarations. Active-only, checked once per pull."""
    band = f"GD {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"GD {spec_name} Longterm {name}", band,
            # id AND name: stances have unranked ids, but the aura a stance
            # leaves may carry its own row -- the name covers both.
            [B.aura_trigger([sid_, name] if sid_ else [name],
                            own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"GD {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# =============================================================== 2. VANGUARD
# Block-fueled tank (Sidekick: "Closest to Protection Warrior"). Main row is
# the cited loop: "Heavy Blow on cooldown (cheap, high threat) -> Pulverize as
# your Energy-dump filler -> Ram whenever Energy allows", with Hammer of Kings
# as the pull opener. Mitigation lives in the defensive row; the block-stack
# states (Vanguard's Shield, Fine Plating) sit in the on-me row.
VG = []
reinforcement_alert("Vanguard", "vanguard", VG)
VG.append(cd_group("GD Vanguard Main", "GD Vanguard",
                   ["Heavy Blow", "Pulverize", "Ram", "Hammer of Kings"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="vanguard"))
VG.append(energy_bar("GD Vanguard Energy", "GD Vanguard", Y_BAR_SOLO,
                     w=row_w(4)))
# Your debuffs on the target. Peril is Glorious Arena's stacking mark
# ("consumed by Pulverize... at 5 stacks stuns"); Hammer of the Law's silence
# and Broad Sweep's AP cut are the other two enemy-side states the spec makes.
# All matched by name -- the debuff auras carry their own ids (§6).
VG.append(dot_bars("GD Vanguard Target", "GD Vanguard",
                   [("Peril", (0.95, 0.60, 0.30), {"by_name": True}),
                    ("Hammer of the Law", (0.70, 0.60, 1.00), {"by_name": True}),
                    ("Broad Sweep", (0.80, 0.45, 0.30), {"by_name": True})],
                   y=Y_TARGET, refresh_at=None))
_y_VG = emit_bottom_block("Vanguard", "vanguard",
                          VG,
                          # the block-economy states (requirements §1)
                          [("High Guard", (1.00, 0.85, 0.40)),
                           ("Vanguard's Shield", (0.55, 0.75, 1.00)),
                           ("Fine Plating", (0.80, 0.75, 0.60)),
                           ("Vanguard's Might", (0.60, 0.90, 0.55))],
                          SHORT_ENTRIES)
longterm_band("Vanguard", "vanguard", VG, _y_VG)
add(spec_group("GD Vanguard", VG))


# ============================================================ 3. INSPIRATION
# Melee support buffer (Sidekick: "Closest to Augmentation Evoker... a buff
# and mitigation unit wearing a shield, not a direct-heal caster"). Main row
# is the cited loop: "Ram on cooldown > cast Ballads on cooldown > Broad Sweep
# as your energy-dump filler". The Ballads are what Inspiring Leader (505344)
# transforms Pulverize/Broad Sweep into (requirements §2) -- ranked ids, so
# their icons ride name-resolved cooldown triggers and simply never fire on an
# untalented character.
IN = []
reinforcement_alert("Inspiration", "inspiration", IN)
IN.append(cd_group("GD Inspiration Main", "GD Inspiration",
                   ["Ram", "Ballad of the Conqueror",
                    "Ballad of the Dragonslayer", "Broad Sweep"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="inspiration"))
IN.append(energy_bar("GD Inspiration Energy", "GD Inspiration", Y_BAR_SOLO,
                     w=row_w(4)))
# Ballad of the Dragonslayer's AP cut and Harrowing Melody's heal cut are the
# spec's enemy-side states; Peril rides Glorious Arena here too.
IN.append(dot_bars("GD Inspiration Target", "GD Inspiration",
                   [("Ballad of the Dragonslayer", (0.70, 0.60, 1.00),
                     {"by_name": True}),
                    ("Harrowing Melody", (0.90, 0.45, 0.35), {"by_name": True}),
                    ("Peril", (0.95, 0.60, 0.30), {"by_name": True})],
                   y=Y_TARGET, refresh_at=None))
_y_IN = emit_bottom_block("Inspiration", "inspiration",
                          IN,
                          # Tempo is the rhythm (3rd stack -> Sound of War);
                          # Minstrel is the stacking haste self-ramp.
                          [("Tempo", (0.95, 0.80, 0.45)),
                           ("Minstrel", (0.60, 0.85, 1.00)),
                           ("Hero's March", (1.00, 0.70, 0.45)),
                           ("Champion's Presence", (1.00, 0.55, 0.25))],
                          SHORT_ENTRIES)
longterm_band("Inspiration", "inspiration", IN, _y_IN)
add(spec_group("GD Inspiration", IN))


# ============================================================== 4. GLADIATOR
# DPS-Prot hybrid (Sidekick: Arms-burst identity on a shield frame). Main row
# is the cited loop: "Spend Ram and Pulverize on cooldown ... Fill remaining
# energy with Reprisal and Centurion Strike ... Broad Sweep as a cheap opening
# builder ... Spear Throw when you need the healing-reduction debuff ... Save
# Final Verdict to finish an enemy below the execute threshold" (35% since the
# 2026-07-31 changelog). Glory/Favor burst states are stack counts in the
# on-me row -- proc states, not spent resources, so no gauge is invented.
GL = []
reinforcement_alert("Gladiator", "gladiator", GL)
GL.append(cd_group("GD Gladiator Main", "GD Gladiator",
                   ["Ram", "Pulverize", "Reprisal", "Centurion Strike",
                    "Broad Sweep", "Spear Throw", "Final Verdict"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="gladiator"))
GL.append(energy_bar("GD Gladiator Energy", "GD Gladiator", Y_BAR_SOLO,
                     w=row_w(7)))
# Spear Throw's healing cut is THE debuff to keep rolling ("worth far more
# landed right before an opponent tries to top up"); Net Throw's root and
# Peril complete the enemy-side picture.
GL.append(dot_bars("GD Gladiator Target", "GD Gladiator",
                   [("Spear Throw", (0.90, 0.30, 0.25), {"by_name": True}),
                    ("Net Throw", (0.70, 0.60, 0.40), {"by_name": True}),
                    ("Peril", (0.95, 0.60, 0.30), {"by_name": True})],
                   y=Y_TARGET, refresh_at=3))
_y_GL = emit_bottom_block("Gladiator", "gladiator",
                          GL,
                          [("Glory", (1.00, 0.85, 0.40)),
                           ("Favor", (1.00, 0.55, 0.25)),
                           ("Warmaster", (0.80, 0.60, 1.00))],
                          SHORT_ENTRIES)
longterm_band("Gladiator", "gladiator", GL, _y_GL)
add(spec_group("GD Gladiator", GL))


# ------------------------------------------------- transforms (requirements §2)
# Press the Attack! (301216) is a passive that TRANSFORMS Standard of Valiance
# into Press the Attack (801219). This fork resolves no spell overrides, so
# the SoV icon follows the replacement with a native ["Spell Known"] trigger
# on the numeric replacement id -- the Runemaster 1.7 mechanism.
spell_swap("Standard of Valiance",
           [("Press the Attack", 801219, (1.0, 0.6, 0.3))])

# Inspiring Leader (Pulverize/Broad Sweep -> Ballads) needs no swap call: the
# Ballads hold their own main-row slots on Inspiration, and their name-resolved
# cooldown triggers simply never fire until the talent grants them. Shield
# Tosser's mid-combat Pulverize -> Shield Toss cycle is UNKNOWN mechanism on
# this fork and deliberately not modelled (requirements §6).


# ------------------------------------------------------------------ merge
MERGE_BANDS = ("Main", "Buffs")
W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# Group triggers/conditions/load are INERT -- every leaf carries its own gate.
# One spell only that spec knows, for load.use_spellknown. Chosen as the
# lowest-level spec-unique UNRANKED castable (spell-meta is_castable):
#   Vanguard     Spiked Reinforcement 653131   L4, unranked, vanguard skillbook
#   Inspiration  Song of Battle 572329         L1, unranked; tooltip matches
#                                              the kit on BOTH DBs (its missing
#                                              exil.es cd row is noted in §6)
#   Gladiator    Weighted Reinforcement 653277 L12, unranked
SPEC_KNOWN = {
    "Vanguard": 653131,
    "Inspiration": 572329,
    "Gladiator": 653277,
}
W.configure(spec_known=SPEC_KNOWN, needs_all=NEEDS_ALL)

_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()
W.chain_ladder()
if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    W.finish((_GATED, _ANY, _CLASSED))
