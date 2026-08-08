"""Build the `Sun Cleric [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Class CONTENT over the shared engine (`tools/wapack.py`) in the Chronomancer
shape -- no convergence flags. Requirements: `notes/requirements-sun-cleric.md`.
Four specs, one of each role plus a second DPS: Blessings (single-ally
"bodyguard" healer), Piety (ranged Holy/Fire caster DPS), Seraphim (block
tank), Valkyrie (melee DPS). Roles are Sidekick-cited, pending in-game
(resources/spec-roles.md).

        [ alerts: NO VOW ]                            <- active-only
        [ on TARGET: your DoTs / your HoTs ]          <- active-only
        [ on me: procs, running CDs, buffs ]          <- active-only
              [  MAIN ROW - flush         ]
              [  solar power + mana       ]           <- fixed height
              [ offensive cooldowns       ]           <- wraps at 7
              [ defensive + utility       ]           <- wraps at 7
              [ long-term: Vows, Devotions]           <- active-only

Three things specific to this class:

  * THE VOW FAMILY IS THE CLASS STANCE. "Only 1 Vow can be active at a time",
    the 2026/07/31 changelog moved Vows onto the stance bar, and every spec's
    Solar Power generation hangs on one -- so the class-wide alert is NO VOW,
    the exact NO BOON shape. The Vows themselves are per-spec long-term rows;
    several resolvable ids are component rows (rank Energize/Heal/Damage/
    Trigger), so the aura displays match by id OR name (requirements §6).

  * SOLAR POWER IS ONE AURA STACKING 0-20 (500149, "You may unleash Dawn at
    20 stacks", dur -1) -- the aura_stacks shape, rendered as a 10-cell
    stack_bar at step=2 (the Stormbringer Static precedent: cells read in
    twos, a full row means Dawn is ready). Dawn itself rides the on-me row.

  * TEMPORARY PROC TRANSFORMS, NOT BUTTON SWAPS. Burning Heat turns the next
    Sunflare into Sun Ray and Herald of Dawn (renamed from Adjudication,
    2026/07/31) empowers the next Dawnsear -- both are the Lithic Lance
    shape: the proc glows the base button, the transform face holds no slot.
    The one permanent transform (Valkyrie L15 turns Vow of Radiance into Vow
    of the Valkyr) needs no Spell Known swap: the Vow rows are per-spec
    active-only aura displays, so a transformed-away Vow simply never lights.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT. Never imported in game; the inventory roles were
# machine-proposed and bulk-cleared (recorded in buildlog-sun-cleric.json),
# and requirements §6 lists what only the client can settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
# Filled from the build's own no-art survey (fetch_spell_icons reported 44 ids
# with no art upstream); classic/wrath-client icons, distinct within every row
# each name appears in.
FALLBACK = {
    "Dawn": "spell_holy_aspiration",
    "Herald of Dawn": "spell_holy_surgeoflight",
    "Champion of the Sun": "spell_holy_avenginewrath",
    "Chosen of the Light": "spell_holy_holyprotection",
    "Cultivate Divinity": "ability_priest_bindingprayers",
    # Plain/Greater Devotion pairs take the classic plain/greater blessing
    # art so the two can share a long-term row without colliding.
    "Devotion of Grace": "spell_holy_blessingofwisdom",
    "Greater Devotion of Grace": "spell_holy_greaterblessingofwisdom",
    "Devotion of Dawn": "spell_holy_blessingofstrength",
    "Greater Devotion of Dawn": "spell_holy_greaterblessingofmight",
    "Devotion of Emperors": "spell_magic_magearmor",
    "Greater Devotion of Emperors": "spell_magic_greaterblessingofkings",
    "Devotion of Radiance": "spell_holy_sealofsalvation",
    "Greater Devotion of Radiance": "spell_holy_greaterblessingofsalvation",
    "Divine Retribution": "spell_holy_retributionaura",
    "Solar Invigoration": "spell_holy_divineillumination",
    "Sunstorm": "spell_holy_searinglightpriest",
    "Vow of Grace": "spell_holy_sealofwisdom",
    "Vow of Light": "spell_holy_sealofblessing",
    "Vow of Radiance": "spell_holy_sealofwrath",
    "Vow of Benediction": "spell_holy_sealofprotection",
    "Vow of Dawn": "spell_holy_mindvision",
    "Vow of the Eclipse": "spell_shadow_sealofkings",
    "Vow of the Valkyr": "spell_holy_sealofvengeance",
    "March of the Valkyr": "inv_valkiergoldpet",
    "Battle Priest": "spell_holy_innerfire",
    "Sun Disc": "spell_holy_circleofrenewal",
    "The Chosen": "spell_holy_powerwordshield",
    "Lord Commander": "spell_holy_lightsgrace",
    "Sunslam": "ability_paladin_hammeroftherighteous",
    "Rejuvenating Rays": "spell_holy_holynova",
    "Mercy": "ability_paladin_selflesshealer",
    "Learning Light": "spell_holy_mindsooth",
    "Blinding Light": "spell_holy_searinglight",
    "Scorch Marks": "spell_fire_soulburn",
    "Spears of Glory": "inv_spear_07",
    "Twin Flames": "spell_fire_twilightflamestrike",
    "Sun Power": "spell_holy_searinglight",
    "Sunrise": "spell_nature_enchantarmor",
    "Sunset": "spell_shadow_twilight",
    "Sunwalker": "spell_holy_flashheal",
    "Ancient Etchings": "inv_inscription_tarotdarkmoon",
    "Vitality": "spell_holy_wordfortitude",
    "Sunsworn": "ability_paladin_swiftretribution",
    "Angelic Presence": "ability_priest_angelicfeather",
    "Bastion of Hope": "spell_holy_fanaticism",
    "Gleaming Armor": "spell_holy_greaterblessingoflight",
    "Celestial Protection": "spell_holy_sealofprotection",
}
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own art
# for the spell.
OVERRIDE = {
    # Solar Embrace and Solar Invocation: Resplendence both resolve to
    # ability_priest_rayofhope upstream and share the Blessings offense row.
    # The group heal takes the group-heal icon.
    "Solar Embrace": "spell_holy_prayerofhealing02",
    # Angelic Presence and Lord Commander both resolve to
    # ability_paladin_conviction upstream and share the Seraphim buff row.
    "Lord Commander": "spell_holy_lightsgrace",
}
# db.exil.es points at rows db.ascension.gg does not corroborate as the
# castable; corrections are name -> id, and an in-game tooltip outranks them
# (resources/in-game-verified.json). Both settled by the crossdb name
# re-ask: db.exil.es only carries the PROC rows (562311, 503650) while
# db.ascension carries full castable tooltips under these ids.
CROSSCHECK = {
    # 20% base mana, instant, 1 min cooldown, "For 15 sec, your allies take
    # 20% increased healing..." -- the cited ally-amp cooldown.
    "Solar Invigoration": 806123,
    # 21% base mana, instant, "abolishing 2 disease effects, repeating every
    # 3 sec for 12 sec" -- the cited disease cleanse.
    "Mercy": 504848,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- Valkyrie
# renders four 44px main icons (its cited rotation is exactly four buttons),
# so row_w(4) = 182px and the rule `28w - 2 <= 1.2 * 182` allows w <= 7.8 -> 7.
# Confirmed against the built packs by tools/rowwidths.py. Do NOT copy this
# number to another class.
CLS = W.init("sun-cleric", version=VERSION, prefix="SC", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# Abilities that hold charges rather than a plain cooldown. Tooltip-read:
# Seraphic Bulwark "2 Charges, 25 sec recharge" (db.exil.es 560095).
CHARGES = {"Seraphic Bulwark": 2}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text. Aura NAMES are the trigger match, and three
# of the five granted-aura names are unverified (requirements §6) -- a wrong
# name fails to an absent glow, never a false one.
PROC_GLOW = {
    # "Herald of Dawn: Casting Rapture now causes your next Dawnsear within
    # [10s] to strike your target twice" (renamed from Adjudication 07/31).
    "Dawnsear": ["Herald of Dawn"],
    # "Burning Heat: Casting Sunflare now has a % chance to transform your
    # next Sunflare into Sun Ray. Horusath Blast is now guaranteed to" --
    # the Lithic Lance shape: the proc glows the base button.
    "Sunflare": ["Burning Heat"],
    # "Sunwalker: Reduces the cast time and mana cost of your next Shine by
    # %, stacking [5] times."
    "Shine": ["Sunwalker"],
    # "Lord Commander: Blocking an attack grants Daybreak" (seraphim) -- the
    # free reactive heal.
    "Daybreak": ["Lord Commander"],
    # "Prioritize [Illumination] while Angelic Presence is active for the
    # empowered version and to feed The Chosen shield" (seraphim page).
    "Illumination": ["Angelic Presence"],
}
# Of those, the ones whose proc also STACKS: Sunwalker stacks its discount.
PROC_STACKS = {"Sunwalker"}

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: ally externals, target debuffs, ground zones and plain nukes.
# A name missing from here costs nothing but a display that never shows; a
# name wrongly here hides a running cooldown, so only unambiguous cases.
NO_BUFF = {"Blessing of Absolution", "Solar Embrace",
           "Solar Invocation: Ascension", "Flash", "Gavel of Grace",
           "Gavel of Light", "Gavel of Wrath", "Horusath Blast",
           "Judgement Day", "Sun Down", "Dawnbringer", "Rapture",
           "Solar Nova", "Divine Retribution", "Blessing of Triumph",
           "Dawnfall", "Pendant of the Sun"}

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own cooldown stack. Sun Cleric's long-term
# content is inventory-driven, three families:
#
#   Vow       "Only 1 Vow can be active at a time" -- the class stance
#             (stance bar since 07/31). Several ids are component rows, so
#             the display matches by id OR name.
#   Devotion  30-min ally buffs, "one Devotion per Sun Cleric" -- the
#             blessing (the Primalist Instinct shape; it sits on the ALLY,
#             the Greater variants cover the whole party including you).
#   other     Holy Form (form until cancelled), Battle Priest, Sun Disc,
#             March of the Valkyr (aura displays -- each reads correctly
#             whether the game implements it as a toggle or a passive).
LONGTERM_COL = {
    "Vow": (0.95, 0.85, 0.45),
    "Devotion": (0.55, 0.75, 1.00),
    "other": (0.75, 0.70, 1.00),
}


def _family(name):
    low = name.lower()
    if low.startswith("vow of"):
        return "Vow"
    if "devotion" in low:
        return "Devotion"
    return "other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `SC <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it.
    """
    band = f"SC {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"SC {spec_name} Longterm {name}", band,
            # By id AND name: the Vow ids are component rows (rank Energize/
            # Heal/Damage/Trigger), the Devotions come in plain and Greater
            # pairs whose names contain each other, and Holy Form is ranked --
            # matching either covers every failure shape at once.
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
# now" row. Dawn is the payoff state every page plays around; Gleaming Vigil
# is the party barrier (lasts until destroyed) whose castable lives in the
# utility row, which cd_buffs does not derive from.
SHORT_ENTRIES = [
    ("Dawn", (1.00, 0.90, 0.45), {}),
    ("Gleaming Vigil", (0.75, 0.75, 0.60), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# High and central, and invisible once you are vowed -- fires only on
# ABSENCE. Every spec's Solar Power generation hangs on a Vow ("Keep a Vow
# active so Solar Power builds"; "get a Vow rolling"; the pre-pull Vow), the
# Vows are mutually exclusive, and 07/31 put them on the stance bar -- so
# "no Vow at all" is a real, class-wide, actionable gap. The trigger matches
# ANY Vow by id or name and the alert shows only when none of them is up.
ALERTS = []
_VOWS = sorted(n for n, a in ABILITIES.items()
               if a["default"] == "longterm" and _family(n) == "Vow")
if _VOWS:
    ALERTS.append(add(B.icon(
        "SC Alerts No Vow", "SC Alerts",
        [B.aura_trigger([str(ABILITIES[n]["id"]) for n in _VOWS] + _VOWS,
                        own_only=False, show_on="showOnMissing")],
        ic(_VOWS[0]), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text("NO VOW", size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])))

add(B.dynamicgroup("SC Alerts", "SC Core", ALERTS, x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
CORE.append("SC Alerts")
add(B.group("SC Core", ROOT, CORE, x=0, y=0))


def envelope(spec_name, bands, icons, mana="full"):
    """Solar Power + mana, the fixed-height envelope (~-156..-186).

    Solar Power is ONE aura (500149) stacking 0-20 -- "You may unleash Dawn
    at 20 stacks" -- rendered as a 10-cell stack_bar at step=2 nearest the
    main row on every spec: it is the thing every page says to track, and a
    full row means Dawn is ready. Mana renders under it: full-height with
    value text where the kit taxes it hard (blessings "mana management is
    your real constraint", piety "Mana funds the Holy/Fire spells"),
    half-height `minor` where it is a self-replenishing side pool (seraphim,
    valkyrie -- both kits refund it passively). Every spec gets the same
    two-band depth, so no anchor below the envelope moves between specs.

    `icons` is the SPEC'S OWN main-row icon count: every resource band's
    width is derived from its own spec's main row, never from another spec's.
    """
    w = row_w(icons)
    solar_col = (1.00, 0.85, 0.30)
    mana_col = (0.30, 0.45, 0.95, 1.0)
    # 10 cells reading in twos; cell 10 lights at 20 stacks = Dawn ready.
    stack_bar(f"SC {spec_name} Solar", f"SC {spec_name}", 500149, 10,
              solar_col, Y_BAR, B.health_trigger("player"), w, bands,
              step=2)
    gid = f"SC {spec_name} Mana"
    subs = [B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                       justify="RIGHT")] if mana == "full" else []
    add(B.aurabar(gid, f"SC {spec_name}", [B.power_trigger("player", 0)],
                  x=0, y=Y_SEG, w=w, h=BAR_H_STACKED if mana == "full" else 10,
                  color=mana_col, subregions=subs))
    bands.append(gid)


# ============================================================== 2. BLESSINGS
# THE HEALING SPEC (Sidekick: "Strong in arena as a healer", Holy Paladin /
# Disc feel; 36/55 spec abilities mention heal/absorb/shield). Raid frames
# stay out (VuhDo/Grid own that on 3.3.5a); the target band carries what YOU
# have on whoever you are targeting. Press order from the cited rotation:
# "alternate Illumination/Shine as primary heals, and keep Daybreak and a
# rolling Bless on the tank... Keep Radiant Cascade for spread-healing
# bounces". The Blessing externals (Purity/Retribution/Triumph/Absolution)
# ride the cooldown rows and light up ON THE TARGET band when running.
BL = []
BL.append(cd_group("SC Blessings Main", "SC Blessings",
                   ["Illumination", "Shine", "Daybreak", "Radiant Cascade",
                    "Bless"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="blessings"))
envelope("Blessings", BL, 5, mana="full")
# helpful=True: on a FRIENDLY target this shows what YOU have on them -- the
# rolling Bless, the Sunshine HoT, and the Blessing externals' windows.
# Bless and Blessing of Triumph are unranked ids (exact match); Sunshine is
# ranked and Purity/Retribution land as ally auras a scrape never captured,
# so those match by name.
BL.append(dot_bars("SC Blessings Target", "SC Blessings",
                   [("Bless", (0.55, 0.90, 0.55), {}),
                    ("Sunshine", (0.95, 0.85, 0.45), {}),
                    ("Blessing of Purity", (0.75, 0.75, 1.00),
                     {"by_name": True}),
                    ("Blessing of Retribution", (0.90, 0.70, 0.95),
                     {"by_name": True}),
                    ("Blessing of Triumph", (1.00, 0.70, 0.40), {})],
                   y=Y_TARGET, unit="target", helpful=True, refresh_at=4))
_y_BL = emit_bottom_block("Blessings", "blessings", BL,
                          [("Sunwalker", (0.95, 0.85, 0.45)),
                           ("Cultivate Divinity", (0.70, 0.85, 1.00)),
                           ("Vitality", (0.60, 0.90, 0.60)),
                           ("Holy Form", (0.95, 0.95, 0.70))],
                          SHORT_ENTRIES)
longterm_band("Blessings", "blessings", BL, _y_BL)
add(spec_group("SC Blessings", BL))


# ================================================================== 3. PIETY
# Ranged Holy/Fire caster DPS on the Sunrise/Sunset lock-in. Press order is
# the cited difficulty text verbatim: "Build with Dawnsear and Sunflare,
# channel Radiant Flame, fire Horusath Blast and Rapture off cooldown, and it
# functions fine." Sun Ray is the Burning Heat transform face of Sunflare
# (the Lithic Lance shape) -- it glows the button instead of holding a slot.
P = []
P.append(cd_group("SC Piety Main", "SC Piety",
                  ["Dawnsear", "Sunflare", "Radiant Flame", "Horusath Blast",
                   "Rapture"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="piety"))
envelope("Piety", P, 5, mana="full")
# Your DoTs and amps on the target: Burning Light is crit-applied and
# Purgation / Sins of the Father are applied by passives, so all three match
# by name (the passive-provenance shape).
P.append(dot_bars("SC Piety Target", "SC Piety",
                  [("Burning Light", (0.95, 0.55, 0.25), {"by_name": True}),
                   ("Purgation", (0.85, 0.65, 0.40), {"by_name": True}),
                   ("Sins of the Father", (0.75, 0.55, 1.00),
                    {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_P = emit_bottom_block("Piety", "piety", P,
                         [("Sunrise", (1.00, 0.85, 0.45)),
                          ("Sunset", (0.75, 0.60, 1.00)),
                          ("Twin Flames", (0.95, 0.55, 0.25)),
                          ("Sun Power", (1.00, 0.90, 0.55)),
                          ("Herald of Dawn", (0.95, 0.75, 0.40)),
                          ("Scorch Marks", (0.90, 0.50, 0.30)),
                          ("Spears of Glory", (0.85, 0.80, 0.55)),
                          ("Learning Light", (0.60, 0.85, 1.00)),
                          ("Blinding Light", (1.00, 0.95, 0.70)),
                          ("Ancient Etchings", (0.70, 0.70, 0.85))],
                         SHORT_ENTRIES)
longterm_band("Piety", "piety", P, _y_P)
add(spec_group("SC Piety", P))


# =============================================================== 4. SERAPHIM
# THE TANK (Sidekick: "a Strength/Stamina block tank with a one-hand weapon
# and shield"). Press order from the cited rotation: Justicar's Wrath "on
# cooldown: high threat + Adjudicator self-heal", Dawnbreak "off your shield
# as your AoE cone", Hammer of Kings' encircling aura, Solar Nova "for burst
# AoE", Illumination "as your single-target heal" (feeds The Chosen shield),
# Seraphic Bulwark held "for the exact burst window" -- the tank's in-row
# mitigation, the Mountain King Rock Barrier precedent. CHARGES=2.
S = []
S.append(cd_group("SC Seraphim Main", "SC Seraphim",
                  ["Justicar's Wrath", "Dawnbreak", "Hammer of Kings",
                   "Solar Nova", "Illumination", "Seraphic Bulwark"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="seraphim"))
envelope("Seraphim", S, 6, mana="minor")
# Your marks on the target: Justicar's Wrath's spell-damage-taken amp (ranked
# id, name carries) and Purging Flames (applied by Dawnbringer/Shining Ray --
# passive-provenance, by name).
S.append(dot_bars("SC Seraphim Target", "SC Seraphim",
                  [("Justicar's Wrath", (0.95, 0.80, 0.40), {}),
                   ("Purging Flames", (0.90, 0.55, 0.30), {"by_name": True})],
                  y=Y_TARGET, refresh_at=3))
_y_S = emit_bottom_block("Seraphim", "seraphim", S,
                         [("Angelic Presence", (1.00, 0.95, 0.70)),
                          ("Sunsworn", (0.95, 0.75, 0.40)),
                          ("Bastion of Hope", (0.60, 0.85, 1.00)),
                          ("Gleaming Armor", (0.75, 0.75, 0.60)),
                          ("Celestial Protection", (0.70, 0.90, 0.70)),
                          ("The Chosen", (0.85, 0.85, 1.00)),
                          ("Chosen of the Light", (1.00, 0.85, 0.55)),
                          ("Lord Commander", (0.95, 0.90, 0.60))],
                         SHORT_ENTRIES)
longterm_band("Seraphim", "seraphim", S, _y_S)
add(spec_group("SC Seraphim", S))


# =============================================================== 5. VALKYRIE
# Melee DPS on the auto-attack Solar Power engine. Press order from the cited
# difficulty text: "Justice and Glorious Execution on cooldown ... is enough
# to function", Horusath Blast "as filler", Sunslam "while Dawn is active" --
# its Dawn gate reads through spellUsable desaturation (check 9), no extra
# trigger. Judgement Day / Champion of the Sun / Sunstorm (the 07/31
# capstone) ride the offense row.
V = []
V.append(cd_group("SC Valkyrie Main", "SC Valkyrie",
                  ["Glorious Execution", "Justice", "Horusath Blast",
                   "Sunslam"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="valkyrie"))
envelope("Valkyrie", V, 4, mana="minor")
# Your setup on the target: Judgement Day's disorient-amp window (unranked
# id), the Vow of the Eclipse burn and Divine Retribution's accumulator
# (both passive-provenance component ids, by name).
V.append(dot_bars("SC Valkyrie Target", "SC Valkyrie",
                  [("Judgement Day", (0.95, 0.85, 0.45), {}),
                   ("Vow of the Eclipse", (0.75, 0.55, 1.00),
                    {"by_name": True}),
                   ("Divine Retribution", (1.00, 0.60, 0.30),
                    {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_V = emit_bottom_block("Valkyrie", "valkyrie", V, [], SHORT_ENTRIES)
longterm_band("Valkyrie", "valkyrie", V, _y_V)
add(spec_group("SC Valkyrie", V))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. Three are the L10
# Specialization passives -- a contiguous grant block (92135-92137), and
# Spell Known on a passive is proven ground on this fork (Chronomancer's
# Eternity Warper gate, verified in game). Valkyrie has no L10 row in either
# database; its earliest unique passive is the L15 Specialization (681084,
# the Vow transform), so the valkyrie-gated leaves arrive at 15 rather than
# 10 -- a five-level window, noted in requirements §6.
SPEC_KNOWN = {
    "Blessings": 92136,       # Sunlight, the L10 passive
    "Piety": 92135,           # Sunrise and Sunset, the L10 passive
    "Seraphim": 92137,        # Angelic Presence, the L10 passive
    "Valkyrie": 681084,       # Valkyrie - Level 15 Passive (earliest unique)
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
