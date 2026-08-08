"""Build the `Felsworn [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Fourth class through `notes/class-pack-process.md`, written as CONTENT over the
shared engine -- the build_chronomancer.py shape, no convergence flags.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your Banes / debuffs ]           <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 7
              [ defensive + utility       ]           <- band 7, wraps at 7
              [ long-term buffs           ]           <- band 8, active-only

Three things specific to this class (notes/requirements-felsworn.md):

  * FELFURY. All three specs run the same builder-spender loop over Energy:
    Felfury is aura 800058 ("Represents your Felfury charges"), cap 6
    (Demonic Embrace / The Demon Within both key off 6). It renders as a
    6-cell stack_bar; Energy is the power bar under it. The envelope is
    IDENTICAL on every spec, so there is no per-spec height variance.

  * THE INNER DEMON WINDOW. Inner Demon (804216) consumes all Felfury and
    lasts 5s per stack; every spec has "Inner Demon:" riders. Which aura id
    the window leaves on the player is unsettled -- 804216's own aura or
    `Demon Form` (804221) -- so the buff row carries BOTH as active-only
    entries; whichever the client exposes is the one that renders. No spell
    is REPLACED inside the window (riders, not overrides), so no Spell Known
    variant tracking is needed.

  * TYRANT TANKS. First tank spec in any pack here (spec-roles.md, Sidekick-
    sourced). Nothing structural changes: its main row is the cited tanking
    rotation and its target band is skipped -- the spec maintains no tracked
    debuff worth a bar.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt and the group name. WeakAuras dedupes imports
# on uid, so a rebuilt pack MUST carry a different salt or the client treats it
# as already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build (draft bar, notes/production-run.md). Roles were assigned by
# an automated pass and cleared in bulk 2026-08-07 -- provenance in the
# buildlog; the hedged rows are listed in requirements §6.
VERSION = "0.2"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {}
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own art.
#
# Two pairs share art upstream and sit side by side in one row, which is what
# the duplicate-art check exists to catch:
#   * Chaos Storm and Fury Unleashed both resolve to the dual-glaive
#     (inv_glaive_1h_artifactaldrochi_d_03dual) in the Slayer offense row.
#     Chaos Storm takes the classic whirlwind -- it IS a spin.
#   * Man'ari Intuition and its Greater pair share ability_demonhunter_
#     demonictrample in the Tyrant long-term row. Greater borrows Betrayer's
#     Inclinations' art, which lives in the SLAYER long-term row and can
#     never co-render with the tyrant one.
OVERRIDE = {
    "Chaos Storm": "ability_whirlwind",
    "Greater Man'ari Intuition": "inv_archaeology_70_demon_malformedabyssal",
}

# Not tooltip-verified, but read off db.ascension.gg tooltips where the digest
# linked a COMPONENT rather than the castable. tools/spellmeta.py flags these
# by rank_text; each replacement's tooltip was read and matches the skillbook.
CROSSCHECK = {
    # 500497 is rank "Heal" with no cost, cooldown or body -- the heal
    # component. 800209 carries the full player tooltip: 45s cd, "Generates 1
    # Felfury ... reducing Physical damage taken by 30% ... heal 3% max health"
    # and sits in the 8002xx block with Carve/Felrend/Immolation Aura.
    "Demonic Will": 800209,
    # 520259 has cd 0 / dur 4s -- a component. 805239 is the castable: 2 min
    # cooldown, "Enrages you, instantly generating 6 Felfury ... leech ... for
    # 15 sec", exactly the skillbook text.
    "Burning Hatred": 805239,
    # Every Sunder id on both DBs carries a component tag (Placer / Expander /
    # Explosion / DoT Persistent / ATK Reducer). 707508 "Placer" is the one
    # with the real player tooltip and geometry (4 yd line) -- the best
    # candidate for the castable. In-game confirmation is §6.
    "Sunder": 707508,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: this class starts on every default.
#
# CD_PER_ROW derives from the NARROWEST main row. All three specs render five
# main icons: row_w(5) = 228px and 28w - 2 <= 1.2 * 228 allows 9. 7 is taken:
# the constraint is that a cooldown row must not OVERRUN the bar, a narrower
# row is never the thing that looks broken, and 7 keeps slayer's 11 offensive
# cooldowns as an even 6+5.
CLS = W.init("felsworn", version=VERSION, prefix="FS", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# ---- the resource system ---------------------------------------------------
# Felfury: ONE aura whose stack count is the resource (the ember/fragment
# shape, aura_stacks). 800058 is the db.exil.es digest row whose entire
# description is "Represents your Felfury charges" -- the id is on both DBs.
# Cap 6 baseline; infernal's Fel Addict raises it by an unstated amount (§6),
# and a talented cap above 6 renders as a full bar early, which fails safe.
FELFURY = 800058
FELFURY_CELLS = 6

# Abilities that hold charges rather than a plain cooldown, from tooltips:
# "3 Charges, 10 sec recharge" / "2 Charges, 1.5 recharge".
CHARGES = {"Chaos Rush": 3, "Fury of the Illidari": 2}

# When one of these buffs is up, the ABILITY it empowers glows. Keyed
# ability -> the procs that light it, taken from the tooltips.
#
# Deliberately short. Legionfall ("next Annihilan Strike costs 50% less") and
# Vengeance Is Mine ("next 10 Twin Slice instances hit harder") are real
# must-press windows whose proc AURA ids exist in no source -- a glow wired to
# a wrong id never fires and reads as "nothing to do". Both are §6.
PROC_GLOW = {
    # Reckoning: "For [the duration], your Fel Fireball is free of cost,
    # instant cast, and strikes up to N targets." The window is pressed, the
    # payoff is the filler -- so the filler glows while it runs.
    "Fel Fireball": ["Reckoning"],
}
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row. buff_group only renders what is up, so a wrongly-kept name
# costs nothing but a display that never shows; a wrongly-dropped one loses a
# real cue.
NO_BUFF = {
    "Illidari Smite", "Bane of Power", "Bane of Fire", "Bane of Betrayal",
    "Oblivion", "Chaos Storm", "Sunder", "Tyrant's Gaze", "Infernal",
    "Sargeras Embrace",
}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# Felsworn has NO class-wide alert: the pre-pull families (Pacts, Intuitions,
# toggles) are all spec-owned, so the alerts live inside each spec block where
# the spec gate applies to them. An empty Core still carries the root group so
# the pack shape matches every other class.
add(B.group("FS Core", ROOT, CORE, x=0, y=0))


# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row, and reads the inventory rather
# than hand-listing names. Three families:
#
#   Pacts        "Only 1 Pact can be active per player at a time" -- toggle
#                auras (Demonfire / Slayer's / Dreadlord's / Legionfel /
#                Vengeful), the paladin-aura shape.
#   Intuitions   30-min ally buffs (Illidari on slayer, Man'ari on tyrant),
#                the blessing shape.
#   Toggles      Agonizing Presence, Betrayer's Inclinations, Fel Empowerment
#                -- persistent self states checked once per pull.
LONGTERM_COL = {
    "Pact": (0.95, 0.60, 0.30),
    "Intuition": (0.55, 0.75, 1.00),
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
    `FS <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The levelling tradeoff is mild here -- the three signature
    spells are L4 / L6 / L1 (see SPEC_KNOWN).
    """
    band = f"FS {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = _family_col(name)
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"FS {spec_name} Longterm {name}", band,
            # By id AND name: the Intuitions come in plain and Greater pairs
            # whose names are prefixes of each other; an id match settles it.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"FS {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row.
#
# Inner Demon appears TWICE on purpose: the window's player aura is either
# 804216's own aura or the separate `Demon Form` spell (804221) -- the fork's
# data cannot say which (§6). Both entries are active-only, so the wrong one
# simply never renders and the right one carries the window.
SHORT_ENTRIES = [
    ("Inner Demon", (0.75, 0.35, 0.95), {}),
    ("Demon Form", (0.75, 0.35, 0.95), {}),
    ("Hateforged Barrier", (0.60, 0.85, 1.00), {}),
]


def alerts_band(spec_name, bands, entries):
    """Missing-buff reminders for ONE spec -- fires only on ABSENCE.

    Pacts are self-emanating ("Emanate an aura...") and mutually exclusive
    ("Only 1 Pact can be active per player"), so "no Pact at all" is a real,
    actionable gap while nagging per-Pact would be permanently on screen for
    the ones you deliberately did not run -- the Chronomancer Wisdom rule.

    NO Intuition alert is built: the base Intuitions are ally-targeted
    ("Empowers an ally...") and no source says they are self-castable, so the
    alert could nag a solo player forever. §6, deferred to in-game.
    """
    band = f"FS {spec_name} Alerts"
    out = []
    for label, art, members in entries:
        out.append(add(B.icon(
            f"{band} {label.title()}", band,
            [B.aura_trigger([str(ABILITIES[n]["id"]) for n in members]
                            + list(members),
                            own_only=False, show_on="showOnMissing")],
            ic(art), size=SZ_ALERT, desaturate=True,
            subregions=[B.sub_background(),
                        B.sub_text(label, size=10, anchor="INNER_BOTTOM",
                                   color=(1, 0.35, 0.35, 1)),
                        B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                     edge=EDGE),
                        B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])))
    add(B.dynamicgroup(band, f"FS {spec_name}", out, x=0, y=Y_ALERT,
                       grow="HORIZONTAL", space=6))
    bands.append(band)


def envelope(spec_name, bands):
    """Felfury + Energy. Identical on all three specs.

    Felfury sits NEAREST the main row because it is the thing you read most --
    every spender costs 2 and Inner Demon consumes the lot. Energy is the
    slower pool underneath.
    """
    W.stack_bar(f"FS {spec_name} Felfury", f"FS {spec_name}", FELFURY,
                FELFURY_CELLS, (0.55, 0.95, 0.35), Y_BAR,
                B.health_trigger("player"), row_w(5), bands, h=14)
    bands.append(energy_bar(f"FS {spec_name} Energy", f"FS {spec_name}",
                            Y_SEG, w=row_w(5)))


def energy_bar(gid, parent, y, w):
    """Energy is power type 3. mana_bar hardcodes 0, so this is the same
    aurabar with the right powertype -- the one class-content divergence the
    resource envelope needs."""
    add(B.aurabar(gid, parent, [B.power_trigger("player", 3)],
                  x=0, y=y, w=w, h=BAR_H_STACKED,
                  color=(0.95, 0.80, 0.15, 1.0),
                  subregions=[
                      B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                 justify="RIGHT"),
                  ]))
    return gid


# ================================================================== 2. SLAYER
# Dual-wield melee. Row order is the ROTATION, from the cited Sidekick text:
# Azzinoth's Assault on cooldown as the armor-shred spender, Annihilan Strike
# as the main hard hit (generates 2 Felfury), Twin Slice as the filler
# generator, Immolation Aura opening pulls, and the Bane of Frailty opener/
# maintain from the Playstyle paragraph. "Glaiving", which the rotation prose
# also names, is NOT a button -- 560578 is a Fury Unleashed passive
# (aliases-felsworn.json) -- so the prose's glaive weaving is the Dancing
# Blades proc engine, not a slot.
S = []
alerts_band("Slayer", S, [
    ("NO PACT", "Demonfire Pact",
     ("Demonfire Pact", "Slayer's Pact")),
])
S.append(cd_group("FS Slayer Main", "FS Slayer",
                  ["Azzinoth's Assault", "Annihilan Strike", "Twin Slice",
                   "Immolation Aura", "Bane of Frailty"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="slayer"))
envelope("Slayer", S)
# Your debuffs on the target: the Bane you are maintaining (one per target)
# and Cripple's decaying stack count (post-07/31 it ticks down 8%/stack, so
# the stacks ARE the state).
S.append(dot_bars("FS Slayer Target", "FS Slayer",
                  [("Bane of Frailty", (0.75, 0.55, 1.00), {}),
                   ("Bane of Power", (0.95, 0.45, 0.75), {}),
                   ("Cripple", (0.60, 0.75, 0.95), {})],
                  y=Y_TARGET, refresh_at=4))
_y_S = emit_bottom_block("Slayer", "slayer", S,
                         [("Immolation Aura", (1.00, 0.55, 0.20))],
                         SHORT_ENTRIES)
longterm_band("Slayer", "slayer", S, _y_S)
add(spec_group("FS Slayer", S))


# ================================================================ 3. INFERNAL
# Ranged Felfury caster. Fel Fireball filler (1 Felfury, castable moving),
# Sargeron Smite at 3+ Felfury when Energy is low, Ruin as the hardest nuke
# (pierces absorbs), Felwrath on packs, Bane of Chaos kept rolling.
I = []
I.append(cd_group("FS Infernal Main", "FS Infernal",
                  ["Fel Fireball", "Sargeron Smite", "Ruin", "Felwrath",
                   "Bane of Chaos"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="infernal"))
envelope("Infernal", I)
# The spec's tracked output is its Banes ("keep a Bane of Chaos rolling, only
# one Bane at a time") plus Cripple.
I.append(dot_bars("FS Infernal Target", "FS Infernal",
                  [("Bane of Chaos", (0.90, 0.35, 0.85), {}),
                   ("Bane of Fire", (1.00, 0.55, 0.20), {}),
                   ("Bane of Betrayal", (0.70, 0.60, 1.00), {}),
                   ("Cripple", (0.60, 0.75, 0.95), {})],
                  y=Y_TARGET, refresh_at=4))
_y_I = emit_bottom_block("Infernal", "infernal", I,
                         [("Sculptor of Doom", (0.85, 0.45, 0.95))],
                         SHORT_ENTRIES)
longterm_band("Infernal", "infernal", I, _y_I)
add(spec_group("FS Infernal", I))


# ================================================================== 4. TYRANT
# THE TANK. Survival is the win condition (Sidekick: "You end fights still
# standing far more often than with a kill. That's the design."). Main row is
# the cited tanking loop: Felrend for AoE threat, Carve as the charged channel
# spender, Demonic Will on cooldown (physical DR + heal-on-damage), Twin Slice
# feeding Felfury, Burning Hatred's 6-Felfury leech enrage.
#
# No target band: the spec maintains no tracked debuff worth a bar -- its
# enemy-side riders (Doomscarring, Sunder's fissures) are passives or ground
# effects, not refreshable aura state.
T = []
alerts_band("Tyrant", T, [
    ("NO PACT", "Dreadlord's Pact",
     ("Dreadlord's Pact", "Legionfel Pact")),
])
T.append(cd_group("FS Tyrant Main", "FS Tyrant",
                  ["Felrend", "Carve", "Demonic Will", "Twin Slice",
                   "Burning Hatred"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="tyrant"))
envelope("Tyrant", T)
_y_T = emit_bottom_block("Tyrant", "tyrant", T,
                         [("Demonic Will", (0.60, 0.85, 1.00)),
                          ("Burning Hatred", (1.00, 0.45, 0.30)),
                          ("Tyrannical Resolve", (0.95, 0.75, 0.30))],
                         SHORT_ENTRIES)
longterm_band("Tyrant", "tyrant", T, _y_T)
add(spec_group("FS Tyrant", T))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# One spell unique to each spec, for load.use_spellknown. Picked as the LOWEST
# gateable spec-unique id -- gateable meaning spell-meta says IsSpellKnown can
# be trusted with it, which rules out every ranked spell and every component.
# All three are early (L4 / L6 / L1-ish), so a levelling character loses
# almost nothing to the gate.
SPEC_KNOWN = {
    "Slayer": 800031,     # Demonfire Pact, L4
    "Infernal": 707901,   # Bane of Fire, L6
    "Tyrant": 803488,     # Dreadlord's Pact
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
