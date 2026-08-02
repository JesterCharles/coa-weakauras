"""Build the `Pyromancer [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Third class through `notes/class-pack-process.md`, and the first written on the
shared engine rather than copied from the class before it. That is the point of
it: Runemaster and Chronomancer were 1632 and 2222 lines, most of which was the
same machinery twice. This file is class CONTENT.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your DoTs / your absorbs ]       <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 7
              [ defensive + utility       ]           <- band 7, wraps at 7
              [ long-term buffs           ]           <- band 8, active-only

Two things here have no analogue in either earlier class:

  * THE FUSED RESOURCE. Heat is not an independent resource -- it is what
    FILLS an Ember. 100 Heat converts to one Ember and empties the bar, and at
    5 Embers the next one is LOST. So heat renders as the number inside the
    ember cell it is currently filling, and the last cell glows yellow from 50
    heat and orange from 80 to warn before the waste lands. A separate heat bar
    could not say that -- it looks identical whether the next Ember arrives or
    evaporates. See notes/layout-standard.md, `fused`.

  * FLAMEWEAVING HEALS. Second healing spec in any pack here after
    Chronomancer's Time, and it takes the same shape: raid frames stay out
    (VuhDo/Grid own that on 3.3.5a), the target band carries what YOU have on
    whoever you are targeting, and for a healer that means absorbs rather than
    DoTs.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt and the group name. WeakAuras dedupes imports
# on uid, so a rebuilt pack MUST carry a different salt or the client treats it
# as already-installed and silently keeps the old copy.
#
# 0.1: first build. NOT confirmed in game, and the inventory roles behind it
# were machine-proposed rather than read row by row -- see the provenance note
# in notes/class-pack-process.md before trusting any band.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {}
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own art
# for the spell.
OVERRIDE = {
    # Breath of Neltharion and Petrifying Visage both resolve to
    # achievment_boss_madnessofdeathwing upstream, and both sit in Draconic's
    # utility row -- so they render as two identical icons side by side, which
    # is exactly what the duplicate-art check exists to catch. Overriding the
    # one whose effect is the more literal: this disarms.
    "Breath of Neltharion": "ability_warrior_disarm",
}
# Not tooltip-verified, but db.exil.es points at a spell db.ascension.gg does
# not mark as an ability. Empty so far: Pyromancer's two load-bearing ids
# (Heat, Ember Trigger) were confirmed in game and live in
# resources/in-game-verified.json, which outranks this.
CROSSCHECK = {}


# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: this class starts on every default, which
# is what a new class should look like.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack, because every
# resource band is width-locked to its own spec's main row and a cooldown row
# that overruns the narrowest one looks broken on that spec. All three specs
# render six main icons, so row_w(6) = 274px and 28w - 2 <= 1.2 * 274 allows
# 11. 7 is taken instead: the constraint is that a cooldown row must not
# OVERRUN the bar, and a narrower row is never the thing that looks broken.
# 7 also lays Flameweaving's 14 utility icons out as two even rows.
CLS = W.init("pyromancer", version=VERSION, prefix="PY", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# ---- the resource system ---------------------------------------------------
# Both ids confirmed in game 2026-08-02 via diag-7-pyro-resource, and recorded
# in resources/in-game-verified.json. The scrape had the right numbers; what it
# could NOT say was which of three ids means "embers held" -- `Ember Trigger`
# and `Ember Consume` carry the same tooltip verbatim.
EMBER = 807534          # stacks == embers held, 0-5
HEAT = 807389           # stacks == current heat, 0-100; converts at 100
EMBER_CELLS = 5
# Heat at which the LAST ember cell warns that the next ember will be wasted.
# The orange tier is the "spend now" cue. Both are a judgement call about how
# much warning is useful, not a fact about the class -- move them freely.
HEAT_WARN, HEAT_DANGER = 50, 80

# Abilities that hold charges rather than a plain cooldown. Overheat (802565)
# has two, and is deliberately absent: it is not in Sidekick's skillbook, so it
# never reaches the inventory. See the gap note at the bottom of this file.
CHARGES = {}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text.
PROC_GLOW = {
    # "Your next Destroyer's Maw or Firefall within 10 sec is instant cast and
    # free of cost and deals 25% increased damage."
    "Destroyer's Maw": ["Legacy of Deathwing"],
    "Firefall": ["Legacy of Deathwing"],
    # Slag Barrage spends Flames of Focus: "Consumes Flames of Focus. Hurl
    # spheres of molten slag for each stack consumed."
    "Slag Barrage": ["Flames of Focus"],
}
# Of those, the ones whose proc also STACKS -- drawn as a number on the icon
# rather than as a bar of its own. Flames of Focus stacks 3 and Slag Barrage
# fires one sphere per stack, so the count is the thing you are reading.
PROC_STACKS = {"Slag Barrage"}

# Offense-row abilities that apply no buff worth a second icon in the "on me"
# row. buff_group only renders what is actually up, so a name missing from here
# costs nothing but a display that never shows.
NO_BUFF = {"Draconic Invocation", "Firestorm", "Ignis Ultimatus",
           "Pillar of Flame", "Pyroclasm", "Burning Spheres"}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row. One shared band in Core would
# need a fixed offset clearing the DEEPEST spec, which costs every shallower
# spec a dead row -- the mistake both earlier classes shipped and then undid.
#
# Pyromancer's long-term content is genuinely per-spec, so this reads it off
# the inventory rather than hand-listing it. Three families:
#
#   Skins       "Can only have 1 Skin active at a time" -- 30 min, mutually
#               exclusive. Every spec has at least one, which is why the
#               reminder below is class-wide.
#   Seals       30 min party/raid buffs. Flameweaving only.
#   Ascensions  permanent, "Only 1 Ascension spell can be active at a time" --
#               the same shape as Chronomancer's Aeons.
LONGTERM_COL = {
    "Skin": (0.95, 0.60, 0.30),
    "Seal": (0.55, 0.75, 1.00),
    "Ascension": (0.95, 0.85, 0.45),
}


def _family(name):
    for key in LONGTERM_COL:
        if key.lower() in name.lower():
            return key
    return "Ascension"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `PY <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it.

    The levelling tradeoff is the same one both earlier classes took, and it is
    WORSE here. Incineration's only gateable spec-unique spell is Spellburn at
    L24, so an Incineration Pyromancer below 24 sees no long-term band at all.
    Skins are available from L1. If a levelling report complains, the fix is to
    move the Skins into Core (class-wide, no spec gate) and leave only the
    Ascensions per-spec -- NOT to go back to one shared band.
    """
    band = f"PY {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"PY {spec_name} Longterm {name}", band,
            # By id AND name: the Seals come in plain and Greater pairs whose
            # names are prefixes of each other, and an id match settles it.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"PY {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row.
SHORT_ENTRIES = [
    ("Superheated", (1.00, 0.70, 0.30), {}),
    ("Flamecasting", (1.00, 0.85, 0.40), {}),
    ("Legacy of Deathwing", (0.95, 0.45, 0.30), {}),
    ("Flames of Focus", (1.00, 0.80, 0.35), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# High and central, and invisible once you are buffed -- fires only on ABSENCE.
# Every spec has at least one Skin and they are mutually exclusive, so "no Skin
# at all" is a real, class-wide, actionable gap. Nagging per-Skin would be
# permanently on screen for the three you deliberately did not take, which is
# the exact failure Runemaster's reminder band had.
ALERTS = []
_SKINS = sorted(n for n, a in ABILITIES.items()
                if a["default"] == "longterm" and "skin" in n.lower())
if _SKINS:
    ALERTS.append(add(B.icon(
        "PY Alerts No Skin", "PY Alerts",
        [B.aura_trigger([str(ABILITIES[n]["id"]) for n in _SKINS] + _SKINS,
                        own_only=False, show_on="showOnMissing")],
        ic(_SKINS[0]), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text("NO SKIN", size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])))

add(B.dynamicgroup("PY Alerts", "PY Core", ALERTS, x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
CORE.append("PY Alerts")
add(B.group("PY Core", ROOT, CORE, x=0, y=0))


def envelope(spec_name, bands):
    """Mana + the fused ember bar. Identical on all three specs.

    Ember sits NEAREST the main row because it is the thing you read most --
    the ordering rule in notes/layout-standard.md. It is also the taller of the
    two bands, which inverts Chronomancer's stacked envelope (mana thick, stack
    bar thin) for a reason: the ember cells carry the heat NUMBER inside them,
    and at SEG_H the digits would be 6px.
    """
    W.stack_bar(f"PY {spec_name} Ember", f"PY {spec_name}", EMBER, EMBER_CELLS,
                (1.00, 0.55, 0.15), Y_BAR, B.health_trigger("player"),
                row_w(6), bands, h=14,
                feeder=(HEAT, HEAT_WARN, HEAT_DANGER))
    bands.append(mana_bar(f"PY {spec_name} Mana", f"PY {spec_name}", Y_SEG,
                          (0.30, 0.45, 0.95, 1.0), w=row_w(6),
                          h=BAR_H_STACKED))


# ========================================================== 2. INCINERATION
# Fire DoT spec. Ignite and Blaze are maintained, Lava Shard generates the
# Ember, and Pyroclasm consumes the DoTs for burst.
I = []
I.append(cd_group("PY Incineration Main", "PY Incineration",
                  ["Ignite", "Blaze", "Wildfire", "Lava Shard", "Explode",
                   "Melt"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="incineration"))
envelope("Incineration", I)
# Your DoTs on the target. Scalding Brand is extended by Firefall and Lava
# Shard, so its remaining time is a thing you act on.
I.append(dot_bars("PY Incineration Target", "PY Incineration",
                  [("Ignite", (1.00, 0.55, 0.20), {}),
                   ("Blaze", (0.95, 0.35, 0.25), {}),
                   ("Scalding Brand", (1.00, 0.75, 0.35), {})],
                  y=Y_TARGET, refresh_at=4))
_y_I = emit_bottom_block("Incineration", "incineration", I,
                         [("Flames of Focus", (1.0, 0.80, 0.35)),
                          ("Superheated", (1.0, 0.70, 0.30))],
                         SHORT_ENTRIES)
longterm_band("Incineration", "incineration", I, _y_I)
add(spec_group("PY Incineration", I))


# ========================================================== 3. FLAMEWEAVING
# THE HEALING SPEC. Cinderheart and Kindle are the direct heals, Ember Touch is
# the Ember spender, and Phoenix Dive lays an absorb along the Phoenix's path.
F = []
F.append(cd_group("PY Flameweaving Main", "PY Flameweaving",
                  ["Kindle", "Cinderheart", "Ember Touch", "Cleansing Flames",
                   "Phoenix Dive", "Stoke"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="flameweaving"))
envelope("Flameweaving", F)
# helpful=True: on a FRIENDLY target this shows what YOU have on them. The
# spec's tracked output is absorbs rather than HoTs -- Pyromancer heals
# directly -- so this band is the two shields, and it is the whole of the
# healing surface by design. Raid-wide state belongs to VuhDo/Grid.
F.append(dot_bars("PY Flameweaving Target", "PY Flameweaving",
                  [("Phoenix Dive", (1.00, 0.65, 0.25), {}),
                   ("Inferno Barrier", (0.95, 0.45, 0.20), {})],
                  y=Y_TARGET, unit="target", helpful=True, refresh_at=5))
_y_F = emit_bottom_block("Flameweaving", "flameweaving", F,
                         [("Dormant", (0.60, 0.85, 1.00)),
                          ("Flames of Focus", (1.0, 0.80, 0.35))],
                         SHORT_ENTRIES)
longterm_band("Flameweaving", "flameweaving", F, _y_F)
add(spec_group("PY Flameweaving", F))


# ============================================================== 4. DRACONIC
# Direct-damage spec. Flare Bolt and Flames of Neltharion fill, Echo of
# Nozdormu and Destroyer's Maw are the hits, and Legacy of Deathwing makes the
# next Maw or Firefall free.
D = []
D.append(cd_group("PY Draconic Main", "PY Draconic",
                  ["Echo of Nozdormu", "Destroyer's Maw", "Firefall",
                   "Dragonfire", "Flames of Neltharion", "Flare Bolt"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="draconic"))
envelope("Draconic", D)
D.append(dot_bars("PY Draconic Target", "PY Draconic",
                  [("Wildfire", (1.00, 0.50, 0.20), {}),
                   ("Burning Brand", (0.95, 0.70, 0.30), {})],
                  y=Y_TARGET, refresh_at=4))
_y_D = emit_bottom_block("Draconic", "draconic", D,
                         [("Legacy of Deathwing", (0.95, 0.45, 0.30)),
                          ("Superheated", (1.0, 0.70, 0.30))],
                         SHORT_ENTRIES)
longterm_band("Draconic", "draconic", D, _y_D)
add(spec_group("PY Draconic", D))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# One spell unique to each spec, for load.use_spellknown. Picked as the LOWEST
# gateable spec-unique id -- gateable meaning spell-meta says IsSpellKnown can
# be trusted with it, which rules out every ranked spell and every component.
#
# Incineration's is L24 and that is the worst of the three by a distance; the
# other two are L1 and L8. Everything gated behind it is invisible to a
# levelling Incineration Pyromancer until 24. See longterm_band's docstring.
SPEC_KNOWN = {
    "Incineration": 800808,   # Spellburn, L24
    "Flameweaving": 805487,   # Firepower, L1
    "Draconic": 681314,       # Dragon Skin, L8
}
W.configure(spec_known=SPEC_KNOWN)

_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()

W.chain_ladder()
W.settle_icon_source()
if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    W.finish((_GATED, _ANY, _CLASSED))
    # KNOWN GAP. Pyromancer's resource SYSTEM is built (the ember bar above)
    # but three of its spells never reach the inventory, because Sidekick's
    # skillbook does not list them and mkabilities seeds from the skillbook:
    #
    #     Heat            807389   the bar itself -- used directly above
    #     Ember Trigger   807534   the counter -- used directly above
    #     Overheat        802565   2 charges, 10s recharge, "Empowers your next
    #                              spell to trigger its Overheat effect"
    #
    # The first two are fine: this file names them as constants and the pack
    # renders them. OVERHEAT IS NOT. It is a real button with charges, at least
    # five abilities have an "Overheat:" clause in their tooltip, and it is in
    # neither the main row nor a cooldown row nor CHARGES. Chronomancer hit the
    # same shape with Echo Fragment and the fix was a hand-added row.
    print("  GAP: Overheat (802565) is not in the inventory and not rendered "
          "-- see the note in __main__")
