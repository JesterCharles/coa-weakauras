"""Build the `Cultist [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Written as CONTENT over the shared engine -- the build_chronomancer.py shape,
no convergence flags. Layout follows notes/layout-standard.md.

        [ on TARGET: your DoTs / your HoTs ]          <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 7
              [ defensive + utility       ]           <- band 7, wraps at 7
              [ long-term buffs           ]           <- band 8, active-only

Class shape (notes/requirements-cultist.md):

  * INSANITY is the class spine: ONE player aura (500706, stacks 0-100,
    duration -1, both DBs) every spec builds and manages against the Total
    Madness backfire at 100. Rendered as a ten-cell `stack_bar` at `step=10`
    -- the Stormbringer Static pattern -- so the 40/60/80 thresholds the
    specs play around read as cell counts, and the top cells lighting IS the
    cap warning. Mana (every ability costs a % of base mana) rides under it.
    Aura id is scrape-derived, not in-game verified -- requirements section 6.

  * FOUR specs, two prose ALIASES (aliases-cultist.json). Sidekick's
    godblade "Obliteration" is Hammer of Twilight (Twilight's Call refunds
    on Hammer crits); dreadnought's "Void Strikes" is Entropic Slam (the
    only Insanity-draining melee spender in the kit). "Eye of N'zoth", the
    cited godblade opener, has NO castable id in either DB -- the reaper
    Sever pattern -- so godblade ships a four-icon main row.

  * HERETIC HEALS (spec-roles.md, Sidekick-cited). Healing surface is the
    target band only (dot_bars helpful=True on the current target: Black
    Blood, Abyssal Covenant, Void Shield, Dark Infusion) plus a healing main
    row -- VuhDo owns raid frames. Everything else is scoped out on purpose.

  * PETS. Two permanent minions (Summon: Faceless Servant on corruption,
    Summon: Mindbender on heretic) render as long-term icons; the NO PET
    alert needs a pet-carried aura id nobody has proven, so it is DEFERRED
    to section 6 rather than shipped on a guess. Tentacles and the Faceless
    Destroyer are ordinary cooldown icons; Abyssal Command / Cosmic Ooze are
    the godblade tentacle-command buttons (the Tinker `Bot:` pattern).

  * NO ALERT BAND in 0.1. The candidates (missing Presence, missing
    permanent pet) both hang on aura visibility no scrape can prove, and a
    wrong-id inverse alert is permanently on screen -- the Runemaster
    reminder failure. Section 6 carries both.

  * NO TRANSFORM FACES in 0.1. Horrorbolt Volley is tracked as its 15 s
    WINDOW aura (255020 + name -> buff row + proc glow on Horrorbolt); the
    castable Volley id and Smite of the Empire are unresolved in both DBs.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build (draft bar, notes/production-run.md). Roles were assigned
# by an automated pass and cleared in bulk 2026-08-07 -- provenance in the
# buildlog; the hedged rows are listed in requirements section 6.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
# Every entry below is either the art of a SIBLING id of the same ability
# (the ally-granted Presence variants, the stale Wrath row, the ranked Void
# Resilience twin -- all served by db.ascension for those ids) or a texture
# already witnessed in icon-meta-cultist.json / the Sidekick page art.
FALLBACK = {
    "Armageddon": "spell_shadow_focusedpower",
    "Corrupting Whispers": "novart_magicspell_(85)_border",   # 706725's art
    "Dark Veil": "spell_priest_burningwill_shadow",           # Sidekick art
    "Greater Void Blessing": "spell_shadow_shadowpower",
    "Void Blessing": "spell_shadow_twilight",
    "Twilight Domain": "spell_shadow_auraofdarkness",
    "Void Resilience": "spell_shadow_sealofkings",            # 1119886's art
    "Whispers of Yogg-Saron": "spell_shadow_mindtwisting",
    "Forbidden Ritual": "inv_nullstone_shadow",               # Sidekick art
    "Restore Sanity": "achievement_boss_yoggsaron_01",
    "Satiate": "spell_shadow_siphonmana",
    "Wrath of The Black Empire": "_soulfire_shadow",          # 500724's art
    "Presence of C'Thun": "achievement_aq_cthun",             # 803355's art
    "Presence of N'Zoth": "inv_mace_1h_nzothraid_d_01",       # 803038's art
    "Presence of Y'Shaarj": "achievement_boss_warthofazshara",  # 803354's
    "Presence of Yogg-Saron": "_d3shadowpower",               # 803353's art
}
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own art.
#
# Two duplicate-art collisions, both resolved by moving the LESS depictive
# side: the Whispers of N'Zoth pair share achievement_nzothraid_nzoth in the
# godblade long-term row (the Greater raid version keeps the raid boss art);
# Doomcloak and Void Reaver share sha_spell_shadow_shadesofdarkness in the
# merged buffs row (Void Reaver keeps it -- it is that talent's Sidekick
# art; Doomcloak takes the gathering-shadows barrier).
OVERRIDE = {
    "Whispers of N'Zoth": "spell_shadow_unholyfrenzy",
    "Doomcloak": "spell_shadow_gathershadows",
}

# Not tooltip-verified in game, but read off db.ascension.gg tooltips where
# the digest linked a COMPONENT rather than the castable. Each replacement's
# tooltip was read against the skillbook text (requirements section 0).
CROSSCHECK = {
    # 354191 is rank Damage -- the expiry component. 500712 is advType Talent
    # tab 27 with the castable tooltip: instant, 30 s cd, "Generates 20
    # Insanity ... increasing all Shadow damage they take from you by 10%".
    "Ancient Curse": 500712,
    # 92131/805120 are the L10 Spec Passive. 520326 is advType Ability lvl 10
    # with the castable tooltip: 45 s cd transform, +15% output, "your
    # Insanity is reduced to 0" at the end.
    "Herald of the Depths": 520326,
    # 573277 is the Rank 2 curse component, 803354 the ally-granted Edict.
    # 803035 carries "Assume a powerful Presence ... only 1 Presence active".
    "Presence of Y'Shaarj": 803035,
    # 801560 is rank Radial machinery. 803082 carries "Assume a crazed
    # Presence ... only 1 Presence active".
    "Presence of Yogg-Saron": 803082,
    # The L10 Spec Passive (520226) TEACHES this ranked castable: 45 s cd,
    # absorbs Sta*3+Int*3 for 20 s, depletes all Insanity on expiry.
    "Dreadnought": 567524,
    # 500724's tooltip is the stale Void-Rune version. 800413 is the live
    # castable: 2 s cast, "draining 20 Insanity".
    "Wrath of The Black Empire": 800413,
}

# Identity, data and the entire build vocabulary come from wapack. init()
# runs BEFORE the star import because it is what gives the unqualified names
# below their values. No convergence flags: this class starts on every
# default.
#
# CD_PER_ROW derives from the NARROWEST main row. Dreadnought and godblade
# render FOUR main icons (the cited priorities are four buttons each once the
# unbuildable Eye of N'zoth is dropped): row_w(4) = 182 px and
# 28w - 2 <= 1.2 * 182 = 218.4 allows exactly 7.
CLS = W.init("cultist", version=VERSION, prefix="CU", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# ---- the resource system ---------------------------------------------------
# Insanity: ONE player aura, stacks 0-100, duration -1. Both DBs carry it
# ("Reaching 100 Insanity will cause you to enter Total Madness"); decoy ids
# (Insanity Bracket Checker 681258, +1 Insanity Stack 681103, the 680601-4
# bracket markers, Sanity 500727) are machinery -- requirements section 6
# holds the in-game confirmation, the Pyromancer Ember Trigger lesson.
INSANITY = 500706
INSANITY_CELLS = 10        # one cell per ten Insanity; thresholds are tens

# Abilities that hold charges rather than a plain cooldown, from live
# db.ascension tooltips: "3 Charge, 6 sec recharge" (Blade of the Empire),
# "3 Charges, 30 sec recharge" (Dark Infusion). Voidforged Edge's charge
# count appears in no tooltip -- section 6 -- so it ships as a plain icon.
CHARGES = {"Blade of the Empire": 3, "Dark Infusion": 3}

# When one of these buffs is up, the ABILITY it empowers glows. The cooldown
# swipe says "when can I press"; it cannot say "this press is empowered".
PROC_GLOW = {
    # "Eldritch Mending is a trap to hard-cast. Fire it off Malevolent
    # Power's every-third-melee proc, or off Eldritch Eye" (heretic dungeon
    # text). Both auras matched by name alongside their scraped ids.
    "Eldritch Mending": ["Eldritch Eye", "Malevolent Power"],
    # Eldritch Eye also makes the next Malevolences instant + guaranteed
    # crits (its own tooltip).
    "Malevolence": ["Eldritch Eye"],
    # "After casting 3 Horrorbolts, it transforms into Horrorbolt Volley for
    # 15 seconds" -- the window aura lights the filler it replaces.
    "Horrorbolt": ["Horrorbolt Volley"],
    # "set up with Rift for a guaranteed crit, then dump Obliteration [=
    # Hammer of Twilight]" (godblade rotation; aliases-cultist.json).
    "Hammer of Twilight": ["Rift"],
}
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row. buff_group only renders what is up, so a wrongly-kept name
# costs nothing; a wrongly-dropped one loses a real cue.
NO_BUFF = {
    "Abyssal Decay", "C'Thun's Blade", "Eldritch Devastation",
    "Psychic Suppression", "Shatter Void Rune", "Eldritch Shock",
    "Eldritch Force", "Tentacle of Y'shaarj", "Eldritch Obelisk",
    "Eldritch Tentacle", "Summon: Faceless Destroyer", "Tentacle of C'Thun",
    "Hammer of Twilight", "Blade of the Empire", "Entropic Slam",
    "Prophet of Doom", "Tentacle of N'Zoth", "Abyssal Command",
    "Cosmic Ooze", "Sudden Doom", "Empire's Grasp", "Umbral Voyage",
    "Grasp of Zek'voz", "Enslave", "Enslave Lesser Mind", "Psychic Leech",
    "Mass Nightmare", "Corrupt Mind", "Entropic Singularity",
    "Crushing Dissonance", "Horrifying Presence", "Test of Pride",
    "Restore Sanity", "Devour Curse", "Devour Magic", "Isolate",
    "Sanity Tap", "Eldritch Ritual", "Satiate", "Void Embrace",
    "Entropic Host", "Protection From Light", "Ritual of Awakening",
    "Tentacle of Yogg-Saron", "Instill Despair", "Vision of Doom",
}

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
# Cultist has NO class-wide alert band in 0.1 (module docstring; requirements
# section 5): both candidates hang on unproven aura visibility. An empty Core
# still carries the root group so the pack shape matches every other class.
CORE = []
add(B.group("CU Core", ROOT, CORE, x=0, y=0))


# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row, and reads the inventory. Three
# families:
#
#   Whispers   the ally/raid blessings ("one Whisper per Cultist"), plain and
#              Greater, one flavour per spec -- the Kings-mould pre-pull check.
#   Presences  the stance system ("only 1 Presence active at a time"), one
#              per spec. A dropped Presence is silent throughput loss; the
#              active-only icon is the passive read, the true alert is
#              section 6.
#   Pets/toggles  the permanent minions (Faceless Servant, Mindbender),
#              Twilight Domain (tank threat toggle), the raid auras
#              (Void Resilience, Voidwarding).
LONGTERM_COL = {
    "Whispers": (0.55, 0.75, 1.00),
    "Blessing": (0.55, 0.75, 1.00),
    "Presence": (0.75, 0.35, 0.95),
    "Summon": (0.95, 0.60, 0.30),
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
    `CU <Spec>` with that spec, and apply_leaf_gates puts the spec's
    signature spell on it.
    """
    band = f"CU {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = _family_col(name)
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"CU {spec_name} Longterm {name}", band,
            # By id AND name: the Whispers come in plain and Greater pairs
            # whose names are prefixes of each other, and several longterm
            # ids are ranked -- an id-or-name match covers both.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"CU {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row.
#
#   Embrace the Void  the 80-Insanity threshold state -- and the class tree
#                     carries a same-named cheat-death (requirements
#                     section 6); active-only by name covers either.
#   Abyssal Ward      the stacking 50%-DR ward, usable while stunned.
#   Twisted Seal      the 5 s spell-deflection window.
SHORT_ENTRIES = [
    ("Embrace the Void", (0.75, 0.35, 0.95), {}),
    ("Abyssal Ward", (0.60, 0.85, 1.00), {}),
    ("Twisted Seal", (0.95, 0.75, 0.30), {}),
]


def envelope(spec_name, icons):
    """Insanity cells + mana. Identical shape on all four specs; width is
    locked to the spec's own main row.

    Insanity sits NEAREST the main row because every spec's decisions hang
    on it (thresholds at 40/60/80, the cap at 100); mana is the slower pool
    underneath. The top cells lighting IS the cap warning -- no separate
    alert display, so nothing can misfire on a wrong id.
    """
    bands = []
    W.stack_bar(f"CU {spec_name} Insanity", f"CU {spec_name}", INSANITY,
                INSANITY_CELLS, (0.72, 0.45, 0.95), Y_BAR,
                B.health_trigger("player"), row_w(icons), bands, h=14,
                step=100 // INSANITY_CELLS)
    bands.append(W.mana_bar(f"CU {spec_name} Mana", f"CU {spec_name}", Y_SEG,
                            (0.30, 0.55, 0.95, 1.0), w=row_w(icons),
                            h=BAR_H_STACKED))
    return bands


# ============================================================== 2. CORRUPTION
# Ranged shadow caster. Row order is the cited rotation: "Open at range with
# Darkwither ... Horrorbolt is your filler ... Weave Gaze of C'Thun on
# cooldown, and Ancient Curse ... Drop Wrath of the Black Empire as your big
# hit, and use Obliteration Beam once you're above 60 Insanity".
C = []
C.append(cd_group("CU Corruption Main", "CU Corruption",
                  ["Darkwither", "Horrorbolt", "Gaze of C'Thun",
                   "Ancient Curse", "Wrath of The Black Empire",
                   "Obliteration Beam"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="corruption"))
C.extend(envelope("Corruption", 6))
# Your curses on the target: the healing-taken shred, the damage-taken curse,
# and the passives' stamps (by name -- applied BY passives, so the on-target
# aura may not share the passive's id).
C.append(dot_bars("CU Corruption Target", "CU Corruption",
                  [("Darkwither", (0.75, 0.55, 1.00), {}),
                   ("Ancient Curse", (0.90, 0.35, 0.85), {}),
                   ("Madness", (1.00, 0.55, 0.20), {"by_name": True}),
                   ("Mind Rot", (0.60, 0.85, 0.60), {"by_name": True}),
                   ("Unrelenting Void", (0.55, 0.75, 1.00),
                    {"by_name": True})],
                  y=Y_TARGET, refresh_at=3))
_y_C = emit_bottom_block("Corruption", "corruption", C,
                         [("Corrupting Whispers", (0.75, 0.35, 0.95)),
                          ("Horrorbolt Volley", (0.95, 0.60, 0.30)),
                          ("Terror of the Old Gods", (0.90, 0.35, 0.35))],
                         SHORT_ENTRIES)
longterm_band("Corruption", "corruption", C, _y_C)
add(spec_group("CU Corruption", C))


# ============================================================= 3. DREADNOUGHT
# THE TANK (spec-roles.md, Sidekick-cited). Row order is the cited loop:
# "Open on approach with Dreadfall ... keeping Twilight Shieldtoss cycling
# ... Spend Insanity with Void Strikes [= Entropic Slam, aliases file]", and
# Sermon of Dread as the maintained AP shred from the dungeon text.
D = []
D.append(cd_group("CU Dreadnought Main", "CU Dreadnought",
                  ["Dreadfall", "Twilight Shieldtoss", "Entropic Slam",
                   "Sermon of Dread"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="dreadnought"))
D.extend(envelope("Dreadnought", 4))
# The tank's maintained enemy state. Sermon of Dread's shred rides an AoE
# debuff (by name); Presence of Y'Shaarj's ground curse is untracked (zone).
D.append(dot_bars("CU Dreadnought Target", "CU Dreadnought",
                  [("Sermon of Dread", (0.75, 0.55, 1.00),
                    {"by_name": True})],
                  y=Y_TARGET, refresh_at=3))
_y_D = emit_bottom_block("Dreadnought", "dreadnought", D,
                         [("Dreadnought", (0.75, 0.35, 0.95)),
                          ("Strength of the Black Empire", (0.60, 0.40, 0.85)),
                          ("Doomcloak", (0.60, 0.85, 1.00)),
                          ("Armageddon", (0.95, 0.45, 0.35)),
                          ("Entropic Retaliation", (0.95, 0.85, 0.45)),
                          ("Void Reaver", (0.55, 0.95, 0.55))],
                         SHORT_ENTRIES)
longterm_band("Dreadnought", "dreadnought", D, _y_D)
add(spec_group("CU Dreadnought", D))


# ================================================================ 4. GODBLADE
# Strength melee. Row order is the cited priority: "Keep Voidforged Edge and
# Netherstrike feeding Insanity, spend on Obliteration [= Hammer of
# Twilight], ride Shadow of the Void's stacks" with "set up with Rift for a
# guaranteed crit". The cited opener Eye of N'zoth is unbuildable (no
# castable id in either DB -- aliases file, requirements section 6), so the
# row is four wide.
G = []
G.append(cd_group("CU Godblade Main", "CU Godblade",
                  ["Voidforged Edge", "Netherstrike", "Hammer of Twilight",
                   "Rift"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="godblade"))
G.extend(envelope("Godblade", 4))
# Seething Void is applied by Entropic Strike and refreshed by melee crits --
# by name, the rune-line hedge is requirements section 6.
G.append(dot_bars("CU Godblade Target", "CU Godblade",
                  [("Seething Void", (0.85, 0.45, 0.35), {"by_name": True}),
                   ("Rift", (0.75, 0.55, 1.00), {"by_name": True})],
                  y=Y_TARGET, refresh_at=3))
_y_G = emit_bottom_block("Godblade", "godblade", G,
                         [("Shadow of the Void", (0.75, 0.35, 0.95)),
                          ("Voidborne", (0.90, 0.35, 0.35)),
                          ("Rift", (0.55, 0.75, 1.00))],
                         SHORT_ENTRIES)
longterm_band("Godblade", "godblade", G, _y_G)
add(spec_group("CU Godblade", G))


# ================================================================= 5. HERETIC
# THE HEALER (spec-roles.md, Sidekick-cited). Row order is the cited dungeon
# sustain priority read as buttons: Malevolence leads as the Black Blood
# applicator ("Black Blood kept up"), then "Blade of the Empire >
# Malevolence > Gaze of C'Thun > instant Eldritch Mending > Void Shield",
# with Sanity Tap as the ever-present Insanity->mana valve ("primary
# in-combat refill").
H = []
H.append(cd_group("CU Heretic Main", "CU Heretic",
                  ["Malevolence", "Blade of the Empire", "Gaze of C'Thun",
                   "Eldritch Mending", "Void Shield", "Sanity Tap"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="heretic"))
H.extend(envelope("Heretic", 6))
# THE HEALER'S TARGET BAND (helpful=True): your HoTs, links and absorbs on
# the CURRENT ally target, glowing at refresh. Raid-wide state is VuhDo's
# job. Black Blood's live aura id is unproven (804113 is rank UNUSED) -- by
# name, requirements section 6.
H.append(dot_bars("CU Heretic Target", "CU Heretic",
                  [("Black Blood", (0.90, 0.25, 0.35), {"by_name": True}),
                   ("Abyssal Covenant", (0.75, 0.55, 1.00),
                    {"by_name": True}),
                   ("Void Shield", (0.55, 0.75, 1.00), {"by_name": True}),
                   ("Dark Infusion", (0.95, 0.75, 0.30), {"by_name": True}),
                   ("Hand of Yogg-Saron", (0.55, 0.95, 0.55),
                    {"by_name": True})],
                  y=Y_TARGET, helpful=True, refresh_at=4))
_y_H = emit_bottom_block("Heretic", "heretic", H,
                         [("Herald of the Depths", (0.75, 0.35, 0.95)),
                          ("Eldritch Eye", (0.95, 0.85, 0.45)),
                          ("Malevolent Power", (0.95, 0.60, 0.30)),
                          ("Dark Veil", (0.55, 0.75, 1.00))],
                         SHORT_ENTRIES)
longterm_band("Heretic", "heretic", H, _y_H)
add(spec_group("CU Heretic", H))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# One spell unique to each spec, for load.use_spellknown. Picked as the
# lowest gateable spec-unique id -- gateable meaning spell-meta records no
# rank text at all, which rules out every ranked spell and every component.
# Herald of the Depths is TAUGHT by the heretic L10 spec passive, so every
# played heretic knows it; Ancient Curse and Rift are cited main-row
# buttons; Test of Pride is the tank's taunt.
SPEC_KNOWN = {
    "Corruption": 500712,   # Ancient Curse (cited main row)
    "Dreadnought": 800468,  # Test of Pride (the taunt)
    "Godblade": 806250,     # Rift, L11 (cited main row)
    "Heretic": 520326,      # Herald of the Depths (taught by the L10 passive)
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
