"""Build the `Tinker [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Seventh class through the process in `notes/class-pack-process.md`. Layout
follows `notes/layout-standard.md`. Requirements: `notes/requirements-tinker.md`
(Phase 0, sealed 2026-08-07); rotation sources are the three Sidekick spec
pages transcribed into `citations-tinker.json`.

        [ alerts: NO AUGMENT / NO PET  ]              <- per spec, active-only
        [ on TARGET: your DoTs / HoTs  ]              <- band 2, active-only
        [ on me: procs, running CDs    ]              <- band 3, active-only
              [  MAIN ROW - flush      ]              <- band 4
              [  mana bar              ]              <- band 5, fixed envelope
              [ offensive cooldowns    ]              <- band 6, wraps at 9
              [ defensive + utility    ]              <- band 7, wraps at 9
              [ long-term: gun augments]              <- band 8, active-only

Three things here have no earlier-class analogue, all from Phase 0:

  * MECHANICS IS A PERMANENT-PET SPEC with FOUR interchangeable bot models
    (Scrapmaw, Mechano-Bear, Rusthound, Clockwork Assistant), all "until
    dismissed". The NO PET alert asks the PET unit for the Tinker Pet Scaling
    Aura family and fires on absence, gated on knowing Build: Scrapmaw --
    the same absent-unit mechanism Stormbringer ships, flagged unverified in
    requirements 6.2. Pet commands (Bot: *) are ordinary cooldown rows.

  * THE MECHSUIT is a Scrap-fueled self-transformation that unlocks its own
    buttons (Combustion / Laser Beam / Activate Jets). They are drawn as
    ordinary cd_icons on their own numeric ids; `spellUsable == 0 ->
    desaturate` carries the "not in the suit" state (requirements 6.6). The
    upgraded-model bars (Spider Tank: *, Vanguard X-*: *) are `ignore` in 0.1.

  * NO SCRAP BAR. Scrap (0-100, the suit fuel) has no UnitAura-visible
    counter in either database -- 707470 is a 0.2s checker dummy and the
    "At Least N Scrap" markers are hidden-clientside machinery. Shipping a
    bar on a guessed id would fail silently, so 0.1 ships without one;
    requirements 6.1 holds the in-game probe that settles it.

Invention is the healing spec (Sidekick's claim -- spec-roles.md has no
Tinker rows yet). Its healing surface is the TARGET BAND only, per the
settled healing-spec scope: your own HoTs/absorbs on your current target,
`dot_bars(helpful=True)`. VuhDo/Grid own raid frames; Beacon ZONES are
ground effects and stay cooldown icons.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt (WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client silently keeps the
# old copy) and the group name, so a screenshot identifies its own build.
VERSION = "0.2"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {}
OVERRIDE = {
    # ONLY deliberate choices belong here, because an entry here overrides the
    # CLIENT's own art for the spell. Three pairs genuinely share art upstream
    # and can appear side by side, which is what the duplicate-art check is
    # for. Every replacement is borrowed from the class's own resolved art
    # pool (icon-meta-tinker.json), so each texture is Ascension-present, and
    # each donor spell never appears in a cooldown row.
    #
    # 806169 shares the uberspanner with Build: Mechsuit. Art borrowed from
    # Arclight Rumbler (706899), the same Arclight family.
    "Arclight Smash": "ability_golemthunderclap",
    # 804166 shares achievement_alliedrace_mechagnome with Core Augment:
    # Warcore. The borrowed texture is literally a deploy-turret icon.
    "Deploy Turret Wall": "ability_ironmaidens_deployturret",
    # 806757 shares nhi_tech_steammachine_border with Machine Synergy
    # (707277) -- the client's own DBC art, db.exil.es serves the same
    # icons-clean texture for both, and both are Mechanics buff icons that
    # can be up side by side. Machine Synergy keeps the client art; the
    # overclock takes the supercharged-engine art (donor 503569, icon-meta --
    # renders in no row, so the borrow cannot introduce a fresh clash).
    "Overclocked Machine": "inv_eng_superchargedengine",
}
# db.exil.es links a row that is not the live entity; each entry names the
# verdict from the crossdb sweep (see requirements 0 and the inventory Notes).
CROSSCHECK = {
    # exil.es 502507 is a different "Boomshot" -- a gunshot from the cut
    # Rounds minigame. The live entity is the every-4th-Scrap-Shot proc
    # PASSIVE, ascension 707249; the buff row matches the aura by name and
    # this id keeps the art resolution on the living row.
    "Boomshot": 707249,
}

# CD_PER_ROW derives from the NARROWEST main row: all three Tinker specs run
# 5-icon main rows (row_w(5) = 228px), and 28w - 2 <= 1.2 * 228 gives w <= 9.8,
# so 9 -- recomputed for this class, never copied. Confirmed by rowwidths.py.
CLS = W.init("tinker", version=VERSION, prefix="TK", cd_per_row=9,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above


# Abilities that hold charges rather than a plain cooldown. Counts from the
# db tooltips ("3 Charges, 15 sec recharge" etc.), quoted in the sidekick
# scrapes committed 2026-08-07.
CHARGES = {
    "Build: Firepot Drone": 3,
    "Makeshift Dynamite": 2,
    "Rocket Boots": 3,
    "Build: Alarm Beacon": 3,
    "Build: Restorative Beacon": 3,
    "Build: Shield Beacon": 3,
    "Build: Replenishment Beacon": 3,
}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "press this now" cue the game gives you. Sources: requirements 1.
PROC_GLOW = {
    # Boomshot: every 4th Scrap Shot empowers the next. Aftermath: the
    # post-Sticky-Bomb window makes the next two faster and harder. Innate
    # Brilliance: every 4th under Aether Augmentation. Blasting Charge: "next
    # Scrap Shot within ... deals increased damage and fires faster".
    "Scrap Shot": ["Boomshot", "Aftermath", "Innate Brilliance",
                   "Blasting Charge"],
    # Bombastic: "your next Bomb Toss triggers no cooldown, global cooldown,
    # or cost" after Build: Spider Bomb.
    "Bomb Toss": ["Bombastic"],
}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW,
            # Deployables and pet commands apply no self-buff worth a second
            # icon in the buff row; anything not listed that applies none
            # simply never shows (active-only), so this list is the deliberate
            # subset, not an exhaustive one.
            no_buff={"Air Strike", "Deathball", "Build: Spider Bomb",
                     "Build: Spider Bomb Factory", "Build: Oil-Spill Pylon",
                     "Build: Sentry Turret", "Build: Battle Turret X-13",
                     "Build: Power Foundry", "Shrapnel Mine",
                     "Deploy Blast Mine", "The Big One",
                     "Bot: C.U.R.B Stomp", "Bot: Flamespill",
                     "Bot: Hydraulic Strike", "Nanobot Deconstruction",
                     "Build: ZIGGI-6K", "Build: Shield Beacon",
                     "Build: Replenishment Beacon"})


# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

# ================================================================== 1. CORE
# Core carries nothing class-wide: the imbue reminder is per spec (each spec
# has its own augmentation set, Mechanics has none) and the pet alert is
# Mechanics-only. The group still exists so the pack keeps the standard
# Core/spec skeleton.
CORE = []
add(B.group("TK Core", ROOT, CORE, x=0, y=0))


# ---- long-term band --------------------------------------------------------
# GUN AUGMENTATIONS: 1-hour gun imbues, the Tinker equivalent of Runemaster's
# weapon engravings ("Add a X Augmentation to your gun for 1 hour"). The
# inventory carries them as `longterm`; each spec's band shows whichever are
# up. Mechanics has no gun augmentation, so its band simply never renders.
LONGTERM_COL = {
    "Augmentation": (0.95, 0.85, 0.45),
    "Bot Augment": (0.60, 0.90, 0.80),
    "other": (0.75, 0.70, 1.00),
}


def _family(name):
    if "Augmentation" in name:
        return "Augmentation"
    if name.split(":")[0].endswith("Augment"):
        return "Bot Augment"       # Chassis / Combat / Core Augment: <metal>
    return "other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `TK <Spec>` with that spec, and apply_leaf_gates puts the spec's L10
    Specialization passive on it -- so the levelling window without this band
    is ten levels, not twenty.
    """
    band = f"TK {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        fam = _family(name)
        col = LONGTERM_COL[fam]
        sid_ = ABILITIES[name]["id"]
        # Bot augments (Mechanics) sit on the PET, not the player -- the
        # applied state rides the bot the way a gun augmentation rides you.
        # Whether the aura carries the castable's id or name is the same
        # requirements 6.3 unknown as the gun imbues, so id AND name.
        unit = "pet" if fam == "Bot Augment" else "player"
        out.append(add(B.icon(
            f"TK {spec_name} Longterm {name}", band,
            # By id AND name: whether the 1-hour buff carries the castable's
            # id is requirements 6.3, so the trigger covers both readings.
            [B.aura_trigger([str(sid_), name], own_only=False, unit=unit)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"TK {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Kinetic Shield reads as "this ally/self is shielded"; Innate
# Brilliance and Blasting Charge are PROC_GLOW sources and appear there.
SHORT_ENTRIES = [
    ("Kinetic Shield", (0.60, 0.85, 1.00), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# NO AUGMENT is PER SPEC: each damage/healing spec has its own set of 1-hour
# gun imbues and Mechanics has none. The absence trigger lists every
# augmentation the spec owns (fires only when NONE is up -- nagging for the
# one you deliberately did not take would be permanently on screen, the
# retro's reminder-band failure), ANDed with a Spell Known gate so a
# levelling character who cannot buy one yet is not nagged.
AUGMENTS = {
    # spec label -> ([augmentation names], gate spell id)
    "Demolition": (["Piercing Augmentation", "Explosive Augmentation",
                    "Tracer Augmentation"], 653245),
    "Invention": (["Aether Augmentation", "Magic Augmentation",
                   "Stim Augmentation"], 653130),
}


def spec_alerts(spec_name, bands, extra=()):
    """The per-spec alert band: NO AUGMENT where the spec has gun imbues,
    plus anything the spec adds (Mechanics adds NO PET)."""
    band = f"TK {spec_name} Alerts"
    out = []
    if spec_name in AUGMENTS:
        names, gate_id = AUGMENTS[spec_name]
        d = B.icon(
            f"{band} No Augment", band,
            [B.aura_trigger([str(ABILITIES[n]["id"]) for n in names] + names,
                            own_only=False, show_on="showOnMissing"),
             # exact=False resolves by name, so the "Augmentation"-ranked ids
             # cannot pin the gate to a row the character never learns.
             B.spell_known_trigger(gate_id, exact=False)],
            ic(names[0]), size=SZ_ALERT, desaturate=True,
            subregions=[B.sub_background(),
                        B.sub_text("NO AUGMENT", size=10,
                                   anchor="INNER_BOTTOM",
                                   color=(1, 0.35, 0.35, 1)),
                        B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                     edge=EDGE),
                        B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
        NEEDS_ALL.add(d["id"])      # missing-aura AND spell-known, never "any"
        out.append(add(d))
    out.extend(extra)
    if not out:
        return
    add(B.dynamicgroup(band, f"TK {spec_name}", out, x=0, y=Y_ALERT,
                       grow="HORIZONTAL", space=6))
    bands.append(band)


def envelope(spec_name, bands):
    """Mana only, on every spec -- the whole fixed-height envelope.

    Demolition and Invention are mana-only by their own Sidekick Resource
    paragraphs (the "Mana + Ammo" page header is a class-level template
    string contradicted by every spec's own text). Mechanics also runs
    Scrap, but Scrap has NO UnitAura-visible surface in either database
    (requirements 6.1), so drawing a bar for it would be a silent lie --
    0.1 ships mana only and the probe settles the rest.
    """
    bands.append(mana_bar(f"TK {spec_name} Mana", f"TK {spec_name}",
                          Y_BAR_SOLO, (0.30, 0.45, 0.95, 1.0), w=row_w(5)))


# ============================================================== 2. DEMOLITION
# Fully-ranged explosives gunner. Press order from the cited rotation
# (sidekick-page-tinker-demolition-2026-08-07): Bomb Toss opener (armor shred
# + reset chain), Sticky Bomb to arm the explosion engine, Scrap Shot woven
# constantly (every 4th empowers via Boomshot), Firepot Drones as the Napalm
# spender, Rocket Launcher as the heavy nuke (guaranteed crit on
# Sticky-Bombed targets).
D = []
spec_alerts("Demolition", D)
D.append(cd_group("TK Demolition Main", "TK Demolition",
                  ["Bomb Toss", "Sticky Bomb", "Scrap Shot",
                   "Build: Firepot Drone", "Rocket Launcher"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="demolition"))
envelope("Demolition", D)
# Your state on the enemy: Napalm stacks (the Fire amp the whole spec feeds),
# the armed Sticky Bomb window (Rocket Launcher's guaranteed crit reads off
# it), Bomb Toss armor shred stacks, and Tracer Augmentation marks.
#
# Napalm and Tracer are by_name: the inventory ids are the teaching passive
# (92138) and the 1-hour self-imbue (653245), while the aura on the TARGET is
# applied by them -- the Inferno provenance case, matched by id OR name.
D.append(dot_bars("TK Demolition Target", "TK Demolition",
                  [("Napalm", (1.00, 0.55, 0.15), {"by_name": True}),
                   ("Sticky Bomb", (1.00, 0.80, 0.30), {}),
                   ("Bomb Toss", (0.85, 0.60, 0.35), {}),
                   ("Tracer Augmentation", (0.95, 0.40, 0.30),
                    {"by_name": True})],
                  y=Y_TARGET, refresh_at=3))
_y_D = emit_bottom_block("Demolition", "demolition", D,
                         [("Boomshot", (1.00, 0.85, 0.40)),
                          ("Aftermath", (1.00, 0.70, 0.30)),
                          ("Bombastic", (1.00, 0.55, 0.20)),
                          ("Blasting Charge", (0.95, 0.75, 0.45)),
                          ("Innate Brilliance", (0.60, 0.85, 1.00))],
                         SHORT_ENTRIES)
longterm_band("Demolition", "demolition", D, _y_D)
add(spec_group("TK Demolition", D))


# =============================================================== 3. INVENTION
# THE HEALING SPEC (Sidekick's claim; spec-roles.md has no Tinker rows yet --
# requirements top table). Healing surfaces are scoped to the TARGET BAND:
# your own HoTs and absorbs on whoever you have selected, glowing when one
# needs a refresh. Press order from the cited rotation: Repair Shot on the
# tank, Zap! for instant top-offs (guaranteed crit on Nanobot wearers),
# Nanobot Reconstruction maintained, Restorative Beacon zones, Med Pack held
# as the emergency cleanse-heal.
I = []
spec_alerts("Invention", I)
I.append(cd_group("TK Invention Main", "TK Invention",
                  ["Repair Shot", "Zap!", "Nanobot Reconstruction",
                   "Build: Restorative Beacon", "Med Pack"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="invention"))
envelope("Invention", I)
# YOUR heals and absorbs on YOUR TARGET. Nanobot Reconstruction can only be
# on 1 target at a time, so its remaining time on the current target is the
# spec's most-acted-on number. The device/shield entries are by_name: the
# aura each leaves is applied by the castable and may carry its own id
# (requirements 6.3 shape).
I.append(dot_bars("TK Invention Target", "TK Invention",
                  [("Nanobot Reconstruction", (0.45, 0.90, 0.55), {}),
                   ("Med Pack", (0.60, 0.85, 0.55), {}),
                   ("Auto Resuscitation Device", (1.00, 0.85, 0.40),
                    {"by_name": True}),
                   ("Kinetic Shield", (0.60, 0.85, 1.00),
                    {"by_name": True}),
                   ("Nanobot Barrier", (0.70, 0.80, 1.00), {})],
                  y=Y_TARGET, helpful=True, refresh_at=4))
_y_I = emit_bottom_block("Invention", "invention", I,
                         [("Overcharge", (1.00, 0.85, 0.40)),
                          ("Beacon Charging", (0.60, 0.85, 1.00)),
                          ("Innate Brilliance", (0.60, 0.85, 1.00))],
                         SHORT_ENTRIES)
longterm_band("Invention", "invention", I, _y_I)
add(spec_group("TK Invention", I))


# =============================================================== 4. MECHANICS
# THE PET SPEC. A permanent bot (Scrapmaw / Mechano-Bear / Rusthound /
# Clockwork Assistant, one out at a time, "until dismissed") fights alongside
# while the player builds Scrap and periodically enters the Mechsuit. Press
# order from the cited rotation: Scrap Shot to build, Makeshift Dynamite as
# the charge-based hard hitter (Arclight Core marks for the pet), Sticky
# Bomb woven on cooldown, then the suit cycle of Combustion and Laser Beam.
M = []

# NO PET: the spec hangs on the bot being alive. Trigger 1 asks the PET unit
# for the Tinker Pet Scaling Aura family and fires on absence; trigger 2
# gates on knowing Build: Scrapmaw at all, so a levelling character who
# cannot summon yet is not nagged. Both the absent-unit mechanism and the
# aura ids are UNVERIFIED on this fork -- requirements 6.2, the same flag
# Stormbringer ships under. exact=False on the gate resolves by name.
_no_pet = B.icon(
    "TK Mechanics Alerts No Pet", "TK Mechanics Alerts",
    [B.aura_trigger(["520510", "524064", "524065", "524066", "524067",
                     "Tinker Pet Scaling Aura"], unit="pet",
                    own_only=False, show_on="showOnMissing"),
     B.spell_known_trigger(sid("Build: Scrapmaw"), exact=False)],
    ic("Build: Scrapmaw"), size=SZ_ALERT, desaturate=True,
    subregions=[B.sub_background(),
                B.sub_text("NO PET", size=10, anchor="INNER_BOTTOM",
                           color=(1, 0.35, 0.35, 1)),
                B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                             edge=EDGE),
                B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
NEEDS_ALL.add(_no_pet["id"])
spec_alerts("Mechanics", M, extra=[add(_no_pet)])

M.append(cd_group("TK Mechanics Main", "TK Mechanics",
                  ["Scrap Shot", "Makeshift Dynamite", "Sticky Bomb",
                   "Mechsuit: Combustion", "Mechsuit: Laser Beam"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="mechanics"))
envelope("Mechanics", M)
# The Arclight Core mark the pet consumes, and the Sticky Bomb window. Both
# by_name: the mark is applied by Makeshift Dynamite and its own aura id is
# uncaptured (the Inferno provenance case).
M.append(dot_bars("TK Mechanics Target", "TK Mechanics",
                  [("Arclight Core", (0.60, 0.85, 1.00), {"by_name": True}),
                   ("Sticky Bomb", (1.00, 0.80, 0.30), {})],
                  y=Y_TARGET, refresh_at=3))
# The pet's ramp rides the on-me row with unit="pet" -- Machine Synergy
# stacks from Scrap Shot; Overclocked Machine is the pet burst window.
_y_M = emit_bottom_block("Mechanics", "mechanics", M,
                         [("Overload", (1.00, 0.70, 0.30)),
                          ("Machine Synergy", (0.60, 0.90, 0.80),
                           {"unit": "pet"}),
                          ("Master Technician", (0.75, 0.70, 1.00)),
                          ("Junker", (0.80, 0.75, 0.55))],
                         SHORT_ENTRIES)
longterm_band("Mechanics", "mechanics", M, _y_M)
add(spec_group("TK Mechanics", M))


merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. The three L10
# Specialization passives are a contiguous block (92138/92140/92141), each
# the spec's teaching passive and never re-ranked -- exactly the "one spell
# unique to each spec" the gate wants, the same shape Stormbringer verified
# (92096-8) and Chronomancer proved in game (Eternity Warper 806301).
SPEC_KNOWN = {
    "Demolition": 92138,   # Napalm, the L10 demolition passive
    "Invention": 92140,    # Build: ZIGGI-6K, the L10 invention passive
    "Mechanics": 92141,    # Build: Mechsuit, the L10 mechanics passive
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
