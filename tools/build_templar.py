"""Build the `Templar [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Class 19, token MONK (from resources/class-tokens.md -- not derivable from the
name). Specs: Zealot (dual-wield melee DPS), Oathkeeper (TANK -- the Keeping
the Oath stagger, taunts, Divine Stand threat), Crusader (2H melee DPS).
Layout follows `notes/layout-standard.md`; every factual claim is cited in
`notes/requirements-templar.md` and `resources/citations-templar.json`.

        [ alerts: NO GIFT / NO STAND ]                <- per-spec, active-only
        [ on TARGET: your DoTs        ]               <- active-only
        [ on me: Oaths, procs, buffs  ]               <- active-only
              [  MAIN ROW - flush     ]
              [  energy bar           ]               <- fixed envelope:
              [  Oath Chain bar       ]               <-   power + Chain aura
              [ offensive cooldowns   ]               <- wraps at 11
              [ defensive + utility   ]               <- wraps at 11
              [ long-term auras       ]               <- active-only

Three things specific to this class:

  * THE OATH ECONOMY. Every spec banks Oaths (typed buffs, capped at 10 since
    2026/08/06) that ride ONE shared container aura, Oath Chain (704576):
    "Allows you to hold Oath buffs. Once 10 stacks are reached you are unable
    to build more Oaths." The Chain bar in the envelope carries its timer AND
    its stack count -- letting it lapse wipes the whole bank (crusader page).

  * TWO TALENT TRANSFORMS, both from the changelog (Sidekick's prose is a
    generation stale on each): Divine Fury (500689) now transforms VINDICATION
    (08/06, was Titanstrike), and Scarlet Training turns ARGENT BLADE into
    Scarlet Hammer (07/31, was Chastise). This fork resolves no spell
    overrides, so each is one display whose FACE swaps on a native
    ["Spell Known"] trigger on the replacement's NUMERIC id -- the Reaper
    Decimate/Thresh pattern.

  * ENERGY, not mana, on all three specs ("Primarily Energy-driven", zealot;
    "Energy, Rogue and Monk style", oathkeeper; crusader likewise). The small
    mana pool "pays for a couple of utility spells and nothing else", so it
    gets no bar -- never render a resource the class does not spend.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Salts the uids -- WeakAuras dedupes imports on uid, so a rebuilt
# pack MUST carry a different salt or the client silently keeps the old copy.
VERSION = "0.2"

# Art for ids with no art at ALL on either database. The Gift family serves
# nothing upstream, and the NO GIFT alert is a showOnMissing display -- there
# is no trigger state to fall back on, so without this it draws a grey
# question mark. Greater Blessing of Kings' art is the classic 3.3.5
# stats-blessing icon, which is exactly what a Gift is.
FALLBACK = {"Gift of Zeal": "spell_holy_greaterblessingofkings",
            # The inventory carries the skillbook name; the live spell is
            # "Greater Gift of Zeal" 680306, so db.exil.es never resolves the
            # NAME and ic() cannot reach the id route. templar_buff_1 IS the
            # client's own art for 680306 (db.exil.es page ogImage,
            # 2026-08-08), so this fallback draws what the game draws.
            "Greater Zealous Oath": "templar_buff_1"}
OVERRIDE = {
    # Two pairs share art upstream and appear side by side, which is what the
    # duplicate-art check exists for. Both replacements are real art the class
    # already resolves and neither appears in the clashing row:
    #
    # Harmony shares `spell_priest_vowofunity` with Interdict in the
    # Oathkeeper utility row. Harmony is the detection-radius/stealth aura, so
    # it borrows the classic 3.3.5 invisibility art.
    "Harmony": "spell_nature_invisibilty",
    # Oath: Argent Blade shares `nhi_holyslash_border` with Oath: Holy Cleave
    # in the merged Buffs row. It borrows Argent Blade's own art
    # (`wakeoffashes`, real on Ascension), which only appears in the Crusader
    # MAIN row -- a different band, so no fresh clash.
    "Oath: Argent Blade": "wakeoffashes",
}

# db.exil.es digest ids corrected by cross-checking (requirements §0):
CROSSCHECK = {
    # The digest's only "Scarlet Hammer" (500752) is the LEVEL 10 DEBUFF
    # ("Gives each melee attack against the target a chance to heal...").
    # The castable is 807035: level 30 -- Scarlet Training's level -- and its
    # db.ascension tooltip is the talent text ("Drop a scarlet hammer on an
    # enemy for 155% Weapon Damage...", 2H-weapon gated).
    "Scarlet Hammer": 807035,
    # 520659 is rank "Proc" with an EMPTY tooltip -- the documented wrong-id
    # smell. 800424 renders the real thing: "Taunt all enemies within 8 yds
    # for 4 sec and increase your movement speed by 50%", 2 min cooldown.
    # (The inventory row already carries 800424; kept here so a reseed cannot
    # quietly regress it.)
    "Absolution": 800424,
    # The digest's Libram of Zeal (575328) is rank "Proc" -- check 22 caught
    # it holding an offense-row slot. The castable is 801466: level 27,
    # "Instant cast, 3 min cooldown, Read from your Libram..." on
    # db.ascension.gg, matching the audit's Libram cadence.
    "Libram of Zeal": 801466,
}

# CD_PER_ROW derives from the NARROWEST main row: Zealot and Oathkeeper at 6
# icons are row_w(6) = 274px, and 28w - 2 <= 1.2 * 274 gives w <= 11.8, so 11.
# Verified against the built packs with tools/rowwidths.py. Do not copy.
CLS = W.init("templar", version=VERSION, prefix="TP", cd_per_row=11,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- after init(), see wapack

# Abilities that hold charges rather than a plain cooldown. Temple Guardian's
# own tooltip: "3 Charges, 35 sec recharge".
CHARGES = {"Temple Guardian": 3}

# When one of these auras is up, the ability it empowers glows -- the same
# "press this now" cue the game gives.
PROC_GLOW = {
    # High General (524617): "Your next Chastise consumes all stacks of
    # Scarlet Champion to deal 25% increased direct damage, and be guaranteed
    # to critically strike" -- the crusader's one unambiguous press-now proc.
    "Chastise": ["High General"],
    # Warrior of Dawn: "Melee damage dealt now has a 10% chance to reduce the
    # Energy cost of your next Argent Blade by -50%" -- and casting Argent
    # Blade in that window is what arms the Scarlet Hammer transform
    # (Scarlet Training). The aura is matched by NAME: 560648 is the granting
    # passive, no separate proc id is captured (requirements §6).
    "Argent Blade": ["Warrior of Dawn"],
}
PROC_STACKS = set()

# Offense-row abilities that leave no self-buff worth a second icon in the
# "on me" row. Norgannon's Wrath is a leap-nuke with a target-side debuff.
NO_BUFF = {"Norgannon's Wrath"}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()
# Displays whose icon is chosen by a CONDITION at runtime; they need
# iconSource = 0 or SetIcon has no effect (state.icon wins otherwise).
NEEDS_MANUAL_ICON = set()


# ================================================================== 1. CORE
# Templar's upkeep alerts are spec-shaped (the Gifts are zealot/oathkeeper
# blessings, Divine Stand is the tank stance), so Core carries nothing
# class-wide -- the group exists to keep the standard Core/spec skeleton.
CORE = []
add(B.group("TP Core", ROOT, CORE, x=0, y=0))

# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. The three class-wide typed Oaths (ids from the exiles digest,
# requirements §6) plus the Testament lockout:
#   Oath: Righteous Lunge 804904  "abilities damage or heal for 5% more"
#   Oath: Condemn         804922  "+3% critical strike chance"
#   Oath: Holy Cleave     804903  "abilities strike an additional enemy"
#   Sacred Restraint      102208  the 1 min Testament lockout DEBUFF -- shown
#                                 so the Fortitude/Hope/Strength clash is
#                                 visible before a wasted press
SHORT_ENTRIES = [
    ("Oath: Righteous Lunge", (0.95, 0.80, 0.45), {}),
    ("Oath: Condemn", (0.90, 0.45, 0.30), {}),
    ("Oath: Holy Cleave", (0.60, 0.85, 1.00), {}),
    ("Sacred Restraint", (0.75, 0.55, 0.75), {"helpful": False}),
]


def energy_bar(gid, parent, y, w, h=None):
    """Energy, the class resource on all three specs (power_type 3 on 3.3.5,
    the barbarian/felsworn precedent). The classic yellow."""
    add(B.aurabar(gid, parent, [B.power_trigger("player", 3)],
                  x=0, y=y, w=w, h=h or BAR_H, color=(1.00, 0.82, 0.10, 1.0),
                  subregions=[
                      B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                 justify="RIGHT"),
                  ]))
    return gid


def oath_chain_bar(gid, parent, y, w):
    """The Oath Chain container aura (704576): timer as the bar, STACK COUNT
    as the left-hand number -- the stacks ARE the banked Oaths ("Once 10
    stacks are reached you are unable to build more"). Letting the timer
    empty wipes the bank, so the low-time cue is the one warning this class
    is played around.

    Active-only by nature (an aurabar with no matching aura shows nothing),
    which is correct: no Chain running means nothing banked, nothing to lose.
    """
    add(B.aurabar(gid, parent,
                  [B.aura_trigger(["704576", "Oath Chain"])],
                  x=0, y=y, w=w, h=12, color=(0.95, 0.80, 0.45, 1.0),
                  subregions=[
                      B.sub_text("%s", size=10, anchor="INNER_LEFT", x=4),
                      B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                 justify="RIGHT"),
                  ]))
    return gid


def envelope(spec_name, bands, n_main):
    """The fixed-height resource envelope, identical shape on every spec:
    Energy (power) on top, the Oath Chain bar under it."""
    bands.append(energy_bar(f"TP {spec_name} Energy", f"TP {spec_name}",
                            Y_BAR, w=row_w(n_main), h=BAR_H_STACKED))
    bands.append(oath_chain_bar(f"TP {spec_name} Oath Chain",
                                f"TP {spec_name}", Y_SEG, w=row_w(n_main)))


def transform_face(d, rep_name, rep_id):
    """Give a main-row button its talent-replacement FACE -- the Reaper
    Decimate pattern, one display rather than an extra slot.

    This fork resolves no spell overrides (`effectiveSpellId` is the id you
    typed), so the signal that the button changed is the REPLACEMENT spell
    being KNOWN -- a native ["Spell Known"] trigger on its NUMERIC id
    (Prototypes.lua:8271 turns a string into spell 0 silently). While it
    fires, a condition swaps `displayIcon` to the replacement's art.

    `disjunctive` must be "any": trigger 1 alone keeps the button on screen
    untalented/untransformed -- the conditions, not the trigger logic, pick
    the face. iconSource = 0 or the swap is invisible (UpdateIcon prefers
    state.icon at -1 and the cooldown trigger supplies the base art).
    """
    d["iconSource"] = 0
    NEEDS_MANUAL_ICON.add(d["id"])
    trs = triggers_of(d)
    trs.append(B.spell_known_trigger(rep_id))
    conds = list((d.get("conditions") or {}).values()) \
        if isinstance(d.get("conditions"), dict) \
        else list(d.get("conditions") or [])
    conds.append(B.cond(
        B.T({"trigger": len(trs), "variable": "show", "value": 1}),
        [B.change("displayIcon", ic(rep_name))]))
    d["triggers"] = B._trigger_wrap(trs)
    d["triggers"]["disjunctive"] = "any"
    d["conditions"] = B.arr(conds)
    return d


def main_row(spec_name, spec_key, names, transform=None):
    """The main rotation row, hand-built so a transform face can be wired.
    `transform` is (base_name, replacement_name, replacement_id)."""
    band = f"TP {spec_name} Main"
    ids = []
    for n in names:
        d = cd_icon(f"{band} {n}", band, n, SZ_MAIN, spec=spec_key)
        if transform and n == transform[0]:
            transform_face(d, transform[1], transform[2])
        ids.append(add(d))
    add(B.dynamicgroup(band, f"TP {spec_name}", ids, x=0, y=Y_MAIN,
                       grow="HORIZONTAL", space=GAP))
    return band


LONGTERM_COL = {
    "Tithe": (0.95, 0.85, 0.45),
    "Gift": (0.45, 0.90, 0.55),
    "Stand": (0.90, 0.35, 0.35),
    "Other": (0.55, 0.75, 1.00),
}


def _lt_family(name):
    if name.startswith("Tithe"):
        return "Tithe"
    if "Gift" in name or "Oath" in name:      # Gifts + the renamed Greater Oath
        return "Gift"
    if name == "Divine Stand":
        return "Stand"
    return "Other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack:
    Gifts (single-target blessings, persist through death since 07/31), the
    raid-wide Greater versions, the Tithe party auras (oathkeeper), Divine
    Stand (the tank threat stance) and Call of the Monastery. Active-only,
    checked once per pull."""
    band = f"TP {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_lt_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"TP {spec_name} Longterm {name}", band,
            # id AND name: the Gift/Oath family is mid-rename (Greater
            # Crusader's Oath -> Greater Gift of Fervor, 08/06) and several
            # entries are ranked, so the name covers what the id misses.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"TP {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


def alert_icon(band, disp, art, label, aura_keys, known_id, helpful=True):
    """A missing-buff alert: aura ABSENT (showOnMissing) AND the enabling
    spell KNOWN -- the ranger No Quiver shape. NEEDS_ALL, never "any"."""
    d = B.icon(
        disp, band,
        [B.aura_trigger(aura_keys, own_only=False, helpful=helpful,
                        show_on="showOnMissing"),
         B.spell_known_trigger(known_id, exact=False)],
        ic(art), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text(label, size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
    NEEDS_ALL.add(d["id"])
    add(d)
    return d["id"]


# ================================================================== 2. ZEALOT
# Dual-wield melee DPS. Main row is the cited loop: "Stack Condemn early...
# keep it up. Build Oaths with Righteous Lunge and Vindication... Righteous
# Upheaval when you've triggered enough Zealotry to max its stacks, otherwise
# Blade of Faith... spread Condemn across a pack with Holy Cleave."
#
# Vindication carries the Divine Fury face: the 08/06 changelog moved the
# transform to Vindication ("Divine Fury now transforms Vindication instead of
# Titanstrike") -- db.ascension's Divine Fury tooltip agrees post-patch
# ("Scales with modifiers to Vindication and grants Oath: Vindication").
ZE = []

# NO GIFT: the paladin-blessing upkeep shape. Fires only when NONE of the four
# Gift family auras is on you AND you can actually cast Gift of Zeal (706634,
# any rank) -- a levelling character without it is never nagged.
_no_gift = alert_icon(
    "TP Zealot Alerts", "TP Zealot Alerts No Gift", "Gift of Zeal", "NO GIFT",
    ["706634", "680306", "572629", "572630",
     "Gift of Zeal", "Greater Gift of Zeal", "Gift of Fervor",
     "Greater Gift of Fervor", "Greater Crusader's Oath"],
    706634)
add(B.dynamicgroup("TP Zealot Alerts", "TP Zealot", [_no_gift], x=0,
                   y=Y_ALERT, grow="HORIZONTAL", space=6))
ZE.append("TP Zealot Alerts")

ZE.append(main_row("Zealot", "zealot",
                   ["Condemn", "Righteous Lunge", "Vindication",
                    "Righteous Upheaval", "Blade of Faith", "Holy Cleave"],
                   transform=("Vindication", "Divine Fury", 500689)))
envelope("Zealot", ZE, n_main=6)
# Your DoTs on the target: Condemn (21s, stacking) and Blade of Faith (30s)
# are "where most of your damage lives"; Iron Penance is the Zealotry-driven
# phys-taken debuff (10 stacks). Ranked spells fall back to name matching
# inside dot_bars; Iron Penance is a talent id so it matches by name too.
ZE.append(dot_bars("TP Zealot Target", "TP Zealot",
                   [("Condemn", (0.90, 0.45, 0.30), {}),
                    ("Blade of Faith", (0.95, 0.85, 0.45), {}),
                    ("Iron Penance", (0.75, 0.60, 0.50), {"by_name": True})],
                   y=Y_TARGET, refresh_at=4))
_y_ZE = emit_bottom_block("Zealot", "zealot", ZE,
                          [("Oath: Vindication", (0.95, 0.70, 0.35)),
                           ("Oath: Retribution", (1.00, 0.60, 0.30)),
                           ("Heaven's Finest", (0.60, 0.85, 1.00)),
                           ("Unbroken Creed", (0.85, 0.75, 0.55)),
                           ("Might of Aggramar", (1.00, 0.85, 0.40))],
                          SHORT_ENTRIES)
longterm_band("Zealot", "zealot", ZE, _y_ZE)
add(spec_group("TP Zealot", ZE))


# ============================================================== 3. OATHKEEPER
# THE TANK. "Strong main-tank for raid bosses... AoE pulls and threat";
# Keeping the Oath staggers 40% of direct damage, Absolution/Beckon taunt,
# Divine Stand is the threat stance (+150% Holy threat since 08/06). Main row
# is the cited loop: Sacred Swing off dodges/parries, Righteous Lunge the
# unconditional builder, "Reckoning as your default Oath Breaker",
# "bank toward Benediction by default", Holy Cleave on packs, and
# "Reckoning/Chastise only when a pull needs to die faster".
#
# Sacred Swing's "Only usable after avoiding an attack" gate reads through the
# spellUsable desaturate (check 9's mechanism) -- IsUsableSpell reflects it.
# No healing-spec surfaces: Benediction is a tank's reactive self/ally
# sustain, not healer throughput (spec-roles.md provenance).
OK = []

# NO STAND: the Righteous-Fury-shaped tank stance alert. Divine Stand's
# tooltip has no duration line (a toggle), so absence while the spell is
# known is a threat bug waiting to happen. ⚠️ The aura surface is UNVERIFIED
# (no buff text on either DB) -- requirements §6 makes this the FIRST thing
# the in-game pass checks; if the aura name differs this alert is permanently
# on for oathkeepers and gets pulled.
_no_stand = alert_icon(
    "TP Oathkeeper Alerts", "TP Oathkeeper Alerts No Stand", "Divine Stand",
    "NO STAND", ["807729", "Divine Stand"], 807729)
add(B.dynamicgroup("TP Oathkeeper Alerts", "TP Oathkeeper", [_no_stand], x=0,
                   y=Y_ALERT, grow="HORIZONTAL", space=6))
OK.append("TP Oathkeeper Alerts")

OK.append(cd_group("TP Oathkeeper Main", "TP Oathkeeper",
                   ["Sacred Swing", "Righteous Lunge", "Reckoning",
                    "Benediction", "Holy Cleave", "Chastise"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="oathkeeper"))
envelope("Oathkeeper", OK, n_main=6)
_y_OK = emit_bottom_block("Oathkeeper", "oathkeeper", OK,
                          [("Oathkeeper", (0.80, 0.70, 0.50)),
                           ("Staffguard", (0.60, 0.85, 1.00)),
                           ("Mending Ward", (0.45, 0.90, 0.55)),
                           ("Oath: Argent Blade", (0.95, 0.70, 0.35))],
                          SHORT_ENTRIES)
longterm_band("Oathkeeper", "oathkeeper", OK, _y_OK)
add(spec_group("TP Oathkeeper", OK))


# ================================================================ 4. CRUSADER
# 2H melee DPS on the typed-Oath engine. Main row is the cited build order:
# "Open with Righteous Lunge... Holy Cleave for the extra-strike Oath...
# Condemn for the crit Oath and its stacking DoT. Keep the Oath Chain alive
# with Argent Blade... Dump into Chastise... or Blade of Faith... Titanstrike
# is your execute below 35%."
#
# Argent Blade carries the Scarlet Hammer face (Scarlet Training, 07/31:
# "transforms your Argent Blade into Scarlet Hammer, instead of Chastise").
# Post-08/06 Argent Blade triggers Scourgebane rather than extending the
# Chain -- Titanstrike (+3 sec) is the button-side extender now.
CR = []
CR.append(main_row("Crusader", "crusader",
                   ["Righteous Lunge", "Holy Cleave", "Condemn",
                    "Argent Blade", "Chastise", "Titanstrike",
                    "Blade of Faith"],
                   transform=("Argent Blade", "Scarlet Hammer", 807035)))
envelope("Crusader", CR, n_main=7)
CR.append(dot_bars("TP Crusader Target", "TP Crusader",
                   [("Condemn", (0.90, 0.45, 0.30), {}),
                    ("Blade of Faith", (0.95, 0.85, 0.45), {})],
                   y=Y_TARGET, refresh_at=4))
_y_CR = emit_bottom_block("Crusader", "crusader", CR,
                          [("Scarlet Champion", (0.95, 0.40, 0.35)),
                           ("High General", (1.00, 0.75, 0.30)),
                           ("Warrior of Dawn", (1.00, 0.85, 0.40)),
                           ("Divine Strikes", (0.90, 0.55, 0.30)),
                           ("Oath: Argent Blade", (0.95, 0.70, 0.35)),
                           ("Oath: Retribution", (1.00, 0.60, 0.30)),
                           ("Unbroken Creed", (0.85, 0.75, 0.55))],
                          SHORT_ENTRIES)
longterm_band("Crusader", "crusader", CR, _y_CR)
add(spec_group("TP Crusader", CR))


# ------------------------------------------------------------------ merge
MERGE_BANDS = ("Main", "Buffs")
W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# Group triggers/conditions/load are INERT -- every leaf carries its own gate.
# One spell only that spec knows, for load.use_spellknown. Chosen as the
# lowest-level spec-unique UNRANKED castable (spell-meta is_castable), because
# IsSpellKnown is exact and a ranked or component id fails silently:
#   Zealot      Force of Golganneth 500694   L31 -- the lowest CERTAIN gate
#               the spec has (everything earlier is ranked); a zealot below
#               31 sees Core only. Requirements §6.
#   Oathkeeper  Aggramar's Will 572573       L8, unranked, oathkeeper-only
#   Crusader    Reflect Magic 801440         L1, unranked, crusader-only
SPEC_KNOWN = {
    "Zealot": 500694,
    "Oathkeeper": 572573,
    "Crusader": 801440,
}
W.configure(needs_all=NEEDS_ALL, spec_known=SPEC_KNOWN)

_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()
W.chain_ladder()
# The two transform hosts are the displays whose art is a build-time choice.
W.settle_icon_source(NEEDS_MANUAL_ICON)
if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    W.finish((_GATED, _ANY, _CLASSED))
