"""Build the `Starcaller [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Written as CONTENT over the shared engine -- the build_chronomancer.py shape,
no convergence flags. Layout follows notes/layout-standard.md.

        [ on TARGET: your DoTs / your HoTs ]          <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 9
              [ defensive + utility       ]           <- band 7, wraps at 9
              [ long-term buffs           ]           <- band 8, active-only

Class shape (notes/requirements-starcaller.md):

  * DUAL RESOURCE ON EVERY SPEC. Energy funds the filler attacks and pays the
    mana back; everything with impact is priced as a % of maximum mana. All
    four Sidekick Resource paragraphs say "dual resource" in those words. The
    envelope is therefore two power bars on every spec: Energy (power_type 3,
    the Barbarian mechanism) nearest the main row, mana under it.

  * SCATTERED STARS is the class spine and it lives ON THE ENEMY -- a 30 s
    Arcane debuff, stacking 4 (+2 under Galaxy), built by every spec's
    builders and consumed by every spec's spenders. It renders in the target
    band with a stack count (`%s`), NOT in the resource envelope -- which
    also makes it correct on retarget. Aura id 804378, both DBs; the applier
    machinery ids (572320/572321/706391/804380 et al.) are requirements
    section 6.

  * FOUR specs (spec-roles.md, Sidekick-cited): moon-guard TANK, moon-priest
    HEALER, sentinel ranged DPS, warden melee DPS. The healer's surface is
    the target band only (dot_bars helpful=True on the current ally target)
    plus a healing main row -- VuhDo owns raid frames.

  * ASPECTS ("shares a cooldown with other Aspects") are the stance system:
    passive proc layers, one active at a time -- long-term band, active-only.
    AEGIS spells (Celestial / Astral / Infused) share a cooldown of their
    own: short mitigation windows -- defensive icons + buff row.

  * NO pets (requirements section 3): four "summon" mentions are a mount, a
    deployable, and two zone effects. No pet section, no NO-PET alert.

  * NO ALERT BAND in 0.1. The candidates (missing Aspect, missing Celestial
    Mind) hang on aura visibility no scrape proves, and a wrong-id inverse
    alert is permanently on screen -- the Runemaster reminder failure.
    Section 6 carries both; the long-term band shows the state passively.

  * TRANSFORM FACES in 0.1: NONE shipped. Moonblade (Blade of the Moon
    talent: Celestial Strike -> Moonblade for 8 s) and Starfire Barrage
    (every 3rd Starfire Shot) both have castable ids, but whether the server
    grants/removes the spell (the Spell Known pattern) or swaps the button by
    aura is unproven for this class -- requirements section 6. Both windows
    are tracked as buff-row entries + PROC_GLOW on the base button instead:
    an aura-keyed glow fails invisible, a wrong Spell Known face vanishes
    from the row.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build (draft bar, notes/production-run.md). Roles were assigned
# by an automated pass and cleared in bulk 2026-08-08 -- provenance in the
# buildlog; the hedged rows are listed in requirements section 6.
VERSION = "0.1"

FALLBACK = {}
# Art that neither scrape has. The build reports these 27 as "no art
# upstream" and they are deliberately NOT given placeholder art here: with
# iconSource = -1 the CLIENT resolves the spell's own texture at runtime,
# which is the right art (the Chronomancer Hasten lesson -- a placeholder
# picked from the class pool drew a clock where the game draws a boot).
# Listed so a future run does not "fix" them: Alignment, Avatar of
# Vengeance, Lunar Lance, Astral Reconstitution, Cosmic Presence, Eclipse of
# Fury, Elune's Presence, Infused Aegis, Huntress Shot, Moon Arrow,
# Trueshot, Silvercurrent, Stellar Convergence, Bonds of Justice, Vigil of
# the Moon.
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own
# art. Three duplicate-art collisions, each resolved by moving the LESS
# depictive / less pressed side; every replacement is a texture already
# witnessed in this class's own icon pool (icon-meta-starcaller.json) on a
# spell that never appears in a cooldown row.
OVERRIDE = {
    # Shares ability_argus_blightorb with Moonlit Bulwark (the more pressed
    # emergency button keeps it). Protected by the Stars' shield art -- a
    # passive, never in a row.
    "Blanket of Stars": "inv_shield_1h_artifactstormfist_d_04",
    # Shares nhi_waterstrick_border with Deluge upstream (db.ascension serves
    # the same texture for both). Flash Flood is the Lunar-Phase spender
    # burst; Moonwell Tide's water-mote art is free.
    "Flash Flood": "inv_elemental_mote_water01",
    # Shares ability_shawaterelemental_swirl with Moonwell upstream. The
    # Moonwell zone keeps the swirl; the self-liquify channel takes Bathe's
    # water-blessing art (Bathe is a passive rider, role ignore -- it renders
    # in no row, so the borrow cannot introduce a fresh clash).
    "Slipstream": "spell_shaman_ancestralawakening",
}

# Not tooltip-verified in game, but read off db.ascension.gg tooltips where
# the digest linked a COMPONENT rather than the castable (the crossdb sweep,
# requirements section 0). Each replacement's tooltip was read against the
# kit text.
CROSSCHECK = {
    # 704796 is rank "ATS Slow" -- the 10 s attack-speed component. 801996
    # carries the full castable tooltip: 10% base mana, 20 s cd, "Smash up to
    # 8 enemies ... Consuming a Scattered Star reduces the remaining cooldown
    # of Starburst by 2 sec".
    "Starburst": 801996,
    # 531757/531756 are rank "DoT"/"Teleport" components. 680822 is the
    # official tree's node spellId AND carries the castable tooltip on
    # db.ascension: 1 min cd, teleport + 25% Intellect for 30 s.
    "Avatar of Vengeance": 680822,
    # 801401 is rank "Heal" -- a component. 802203 carries the castable
    # Aspect tooltip: 5% base mana, 10 s cd, "Shares a cooldown with other
    # Aspects".
    "Aspect of the Goddess": 802203,
    # 524702's description is literally "Deprecated". 805507 carries the
    # live tooltip verbatim to the sentinel kit text: 2 min cd, "Instantly
    # regenerates 100% of your maximum mana, but reduces damage dealt by 50%
    # ... threat against all enemies is nullified".
    "Alignment": 805507,
}

# Identity, data and the entire build vocabulary come from wapack. init()
# runs BEFORE the star import because it is what gives the unqualified names
# below their values. No convergence flags: this class starts on every
# default.
#
# CD_PER_ROW derives from the NARROWEST main row. All four specs render SIX
# main icons (the cited priorities are six buttons each): row_w(6) = 274 px
# and 28w - 2 <= 1.2 * 274 = 328.8 allows 11; capped at 9, the widest row
# any shipped class carries -- confirmed with tools/rowwidths.py after the
# build.
CLS = W.init("starcaller", version=VERSION, prefix="SC", cd_per_row=9,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# ---- the resource system ---------------------------------------------------
# Scattered Stars: ON THE ENEMY, so it is target-band data (see below), not a
# bar. The envelope is the two power pools every spec runs.
SCATTERED_STARS = 804378       # 30 s, stacks 4(+), both DBs

# Abilities that hold charges rather than a plain cooldown, from the live
# db.exil.es tooltip: "2 Charges, 18 sec recharge" (Trueshot).
CHARGES = {"Trueshot": 2}

# When one of these buffs is up, the ABILITY it empowers glows. The cooldown
# swipe says "when can I press"; it cannot say "this press is empowered".
# Every pairing is quoted from the cited kit/rotation text; the window auras
# match by name alongside their scraped ids, so an unproven id fails
# invisible rather than wrong (requirements section 6).
PROC_GLOW = {
    # "Consuming Scattered Stars now has a 15% chance to transform Celestial
    # Strike into Moonblade for 8 seconds" (Blade of the Moon talent).
    "Celestial Strike": ["Moonblade"],
    # "Every 3rd Starfire Shot transforms Starfire Shot into Starfire
    # Barrage" (sentinel kit).
    "Starfire Shot": ["Starfire Barrage"],
    # "Moonflow ... Lunar Eclipse: Triggers with no cooldown and consumes
    # Scattered Stars" -- the Eclipse state makes Moonflow free.
    "Moonflow": ["Lunar Eclipse"],
    # "Touch of Moonlight ... Lunar Eclipse: This spell is instant and
    # refunds its mana cost and 1 stack of Lunar Phase."
    "Touch of Moonlight": ["Lunar Eclipse"],
}
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row. buff_group only renders what is up, so a wrongly-kept name
# costs nothing; a wrongly-dropped one loses a real cue.
NO_BUFF = {
    "Vengeance of Elune", "Celestial Impact", "Starshatter", "Moonblade",
    "Starfire Barrage", "Rain of Comets", "Lunar Storm", "Starlight",
    "Arrow of the Goddess", "Astral Flare", "Arrows In The Night",
    "Silvercurrent", "Flash Flood", "Warden's Blade", "Moonwell Splash",
    "Deluge", "Moonwater Blessing", "Stellar Convergence", "Moonwell",
    "Celestial Awakening", "Tidal Rebirth", "Geyser", "Bubble Buddy",
    "Eclipse of Fury", "Cosmic Presence",
}

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
# Starcaller has NO class-wide alert band in 0.1 (module docstring;
# requirements section 5). An empty Core still carries the root group so the
# pack shape matches every other class.
CORE = []
add(B.group("SC Core", ROOT, CORE, x=0, y=0))


# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row, and reads the inventory. Two
# families:
#
#   Aspects    the stance system ("shares a cooldown with other Aspects"),
#              one active at a time. A dropped Aspect is silent throughput
#              loss; the active-only icon is the passive read, the true
#              alert is section 6.
#   Blessings  Celestial Mind / Greater Celestial Mind (ally Intellect) and
#              the moon-guard Arcane Protections -- the Kings-mould pre-pull
#              check.
LONGTERM_COL = {
    "Aspect": (0.75, 0.55, 1.00),
    "Celestial Mind": (0.55, 0.75, 1.00),
    "Arcane Protection": (0.55, 0.95, 0.75),
}
_LONGTERM_DEFAULT_COL = (0.95, 0.85, 0.45)


def _family_col(name):
    for key, col in LONGTERM_COL.items():
        if key.lower() in name.lower():
            return col
    return _LONGTERM_DEFAULT_COL


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm" and a["id"]
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `SC <Spec>` with that spec, and apply_leaf_gates puts the spec's
    signature spell on it.
    """
    band = f"SC {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = _family_col(name)
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"SC {spec_name} Longterm {name}", band,
            # By id AND name: Celestial Mind comes in plain and Greater pairs
            # whose names are prefixes of each other, and several longterm
            # ids are ranked -- an id-or-name match covers both.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"SC {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row.
#
#   Aegis windows   the three shared-cooldown mitigation windows.
#   Shooting Star   the unslowable sprint window.
SHORT_ENTRIES = [
    ("Celestial Aegis", (0.55, 0.75, 1.00), {}),
    ("Astral Aegis", (0.75, 0.55, 1.00), {}),
    ("Infused Aegis", (0.95, 0.75, 0.30), {}),
    ("Shooting Star", (0.60, 0.85, 1.00), {}),
]


def envelope(spec_name, icons):
    """Energy + mana, identical shape on all four specs; width is locked to
    the spec's own main row.

    Energy sits NEAREST the main row because it funds the moment-to-moment
    fillers on every spec ("you're rarely waiting on a global"); mana is the
    slower pool underneath -- the one whose percentage costs gate the burst.
    """
    bands = []
    gid = f"SC {spec_name} Energy"
    add(B.aurabar(gid, f"SC {spec_name}", [B.power_trigger("player", 3)],
                  x=0, y=Y_BAR, w=row_w(icons), h=BAR_H_STACKED,
                  color=(0.95, 0.85, 0.30, 1.0),
                  subregions=[B.sub_text("%p", size=10, anchor="INNER_RIGHT",
                                         x=-4, justify="RIGHT")]))
    bands.append(gid)
    bands.append(W.mana_bar(f"SC {spec_name} Mana", f"SC {spec_name}", Y_SEG,
                            (0.30, 0.55, 0.95, 1.0), w=row_w(icons),
                            h=BAR_H_STACKED))
    return bands


# ============================================================== 2. MOON GUARD
# THE TANK (spec-roles.md, Sidekick-cited). Row order is the cited loop:
# "Starburst > Starsweep > Celestial Cleave > Starsweep, repeated. Single
# target runs the same shape with the other pair: Starsunder to build, Lunar
# Lance to spend", with Celestial Strike as the Energy filler ("alternate
# Energy-funded filler swings").
MG = []
MG.append(cd_group("SC Moon Guard Main", "SC Moon Guard",
                   ["Starburst", "Starsweep", "Celestial Cleave",
                    "Starsunder", "Lunar Lance", "Celestial Strike"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="moon-guard"))
MG.extend(envelope("Moon Guard", 6))
# The tank's maintained enemy state: the star stacks every spender cashes,
# and Starburst's attack-speed slow (by name -- applied by the smash, the
# on-target aura may not share the button's id).
MG.append(dot_bars("SC Moon Guard Target", "SC Moon Guard",
                   [("Scattered Stars", (0.75, 0.55, 1.00),
                     {"by_name": True}),
                    ("Starburst", (0.95, 0.60, 0.30), {"by_name": True})],
                   y=Y_TARGET, refresh_at=4))
_y_MG = emit_bottom_block("Moon Guard", "moon-guard", MG,
                          [("Moonblade", (0.95, 0.85, 0.45)),
                           ("Vengeance of Elune", (0.90, 0.35, 0.35)),
                           ("Blanket of Stars", (0.55, 0.75, 1.00)),
                           ("Moonlit Bulwark", (0.60, 0.85, 1.00)),
                           ("Chosen of the Moon", (0.75, 0.35, 0.95)),
                           ("Starsweeper", (0.55, 0.95, 0.55))],
                          SHORT_ENTRIES)
longterm_band("Moon Guard", "moon-guard", MG, _y_MG)
add(spec_group("SC Moon Guard", MG))


# ============================================================= 3. MOON PRIEST
# THE HEALER (spec-roles.md, Sidekick-cited). Row order is the cited dungeon
# text read as buttons: "Moonflow on cooldown (or free during Lunar Eclipse),
# Prayer of Elune for stacked group damage plus a magic dispel, Hand of
# Elune / Touch of Moonlight as tank filler and single-target spike coverage.
# Keep Huntress Shot/Moon Arrow flowing to fund mana."
MP = []
MP.append(cd_group("SC Moon Priest Main", "SC Moon Priest",
                   ["Moonflow", "Prayer of Elune", "Hand of Elune",
                    "Touch of Moonlight", "Huntress Shot", "Moon Arrow"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="moon-priest"))
MP.extend(envelope("Moon Priest", 6))
# THE HEALER'S TARGET BAND (helpful=True): your HoTs, marks and absorbs on
# the CURRENT ally target, glowing at refresh. Raid-wide state is VuhDo's
# job. Every aura here is applied BY a passive or rider (Elune's Favor's HoT,
# Rippling Moonwater's Moonwater stacks, Eclipsing Arrows' mark), so all
# match by name -- requirements section 6.
MP.append(dot_bars("SC Moon Priest Target", "SC Moon Priest",
                   [("Elune's Favor", (0.55, 0.95, 0.55), {"by_name": True}),
                    ("Moonwater", (0.55, 0.75, 1.00), {"by_name": True}),
                    ("Moonwater Blessing", (0.95, 0.75, 0.30),
                     {"by_name": True}),
                    ("Celestial Mind", (0.75, 0.55, 1.00),
                     {"by_name": True}),
                    ("Aegis of Neptulon", (0.60, 0.85, 1.00),
                     {"by_name": True})],
                   y=Y_TARGET, helpful=True, refresh_at=4))
_y_MP = emit_bottom_block("Moon Priest", "moon-priest", MP,
                          [("Lunar Phase", (0.95, 0.85, 0.45)),
                           ("Lunar Eclipse", (0.75, 0.35, 0.95)),
                           ("Celestial Form", (0.90, 0.35, 0.35)),
                           ("Aspect of the Goddess", (0.55, 0.95, 0.55)),
                           ("Lunar Resplendence", (0.60, 0.85, 1.00)),
                           ("Full Moon", (0.95, 0.95, 0.75)),
                           ("New Moon", (0.55, 0.55, 0.85))],
                          SHORT_ENTRIES)
longterm_band("Moon Priest", "moon-priest", MP, _y_MP)
add(spec_group("SC Moon Priest", MP))


# ================================================================ 4. SENTINEL
# Ranged arcane build-spend. Row order is the cited rotation: "filler
# Huntress Shot ... Moon Arrow whenever Huntress Shot is down ... consume
# stacked Scattered Stars for burst via Starfire Shot, Lunar Lance, or
# Trueshot (2 charges) -> on a pack, lead Starcall."
SE = []
SE.append(cd_group("SC Sentinel Main", "SC Sentinel",
                   ["Huntress Shot", "Moon Arrow", "Starfire Shot",
                    "Lunar Lance", "Trueshot", "Starcall"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="sentinel"))
SE.extend(envelope("Sentinel", 6))
# The spend meter on the enemy, plus the talent DoT Lunar Lance leaves under
# Moonlit Lancer (by name; harmless untalented -- active-only).
SE.append(dot_bars("SC Sentinel Target", "SC Sentinel",
                   [("Scattered Stars", (0.75, 0.55, 1.00),
                     {"by_name": True}),
                    ("Lunar Lance", (0.90, 0.35, 0.85), {"by_name": True})],
                   y=Y_TARGET, refresh_at=4))
_y_SE = emit_bottom_block("Sentinel", "sentinel", SE,
                          [("Starfire Barrage", (0.95, 0.85, 0.45)),
                           ("Lunar Resplendence", (0.60, 0.85, 1.00)),
                           ("Alignment", (0.55, 0.55, 0.85))],
                          SHORT_ENTRIES)
longterm_band("Sentinel", "sentinel", SE, _y_SE)
add(spec_group("SC Sentinel", SE))


# ================================================================== 5. WARDEN
# Melee glaive burst. Row order is the cited numbered rotation read as
# sustain press priority: "3) Starsunder on entering melee 4) Celestial
# Strike as your Energy dump 5) Astral Blade on cooldown 6) Umbral Blade
# once you have 2-3 Scattered Stars", with the opener glaive and the AoE
# knives last.
WA = []
WA.append(cd_group("SC Warden Main", "SC Warden",
                   ["Starsunder", "Celestial Strike", "Astral Blade",
                    "Umbral Blade", "Sentinel Glaive", "Fan of Knives"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="warden"))
WA.extend(envelope("Warden", 6))
WA.append(dot_bars("SC Warden Target", "SC Warden",
                   [("Scattered Stars", (0.75, 0.55, 1.00),
                     {"by_name": True}),
                    ("Astral Blade", (0.90, 0.35, 0.85),
                     {"by_name": True}),
                    ("Bonds of Justice", (0.95, 0.60, 0.30),
                     {"by_name": True})],
                   y=Y_TARGET, refresh_at=4))
_y_WA = emit_bottom_block("Warden", "warden", WA,
                          [("Shadowsong's Mandate", (0.95, 0.85, 0.45)),
                           ("Avatar of Vengeance", (0.90, 0.35, 0.35)),
                           ("Aspect of the Warden", (0.75, 0.55, 1.00))],
                          SHORT_ENTRIES)
longterm_band("Warden", "warden", WA, _y_WA)
add(spec_group("SC Warden", WA))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# One spell unique to each spec, for load.use_spellknown. Picked as the
# lowest-level gateable spec-unique id -- gateable meaning spell-meta
# records no rank text, which rules out every ranked spell and component.
SPEC_KNOWN = {
    "Moon Guard": 805433,    # Moonlit Bulwark, L1
    "Moon Priest": 800386,   # Lunar Eclipse, L1
    "Sentinel": 563725,      # Arrow of the Goddess, L1
    "Warden": 805563,        # Astral Blade, L13 (cited main row)
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
