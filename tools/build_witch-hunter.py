"""Build the `Witch Hunter [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Sixth class through `notes/class-pack-process.md`, class CONTENT over the
shared engine (`tools/wapack.py`) in the Chronomancer shape -- no convergence
flags. Requirements: `notes/requirements-witch-hunter.md`. First FOUR-spec
class through the pipeline.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your DoTs / debuffs ]            <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 9
              [ defensive + utility       ]           <- band 7, wraps at 9
              [ long-term buffs           ]           <- band 8, active-only

Three things here have no analogue in the earlier classes:

  * A DUAL POWER ENVELOPE ON EVERY SPEC. Rage and mana are both real for all
    four specs ("Dual Rage and Mana" -- Sidekick, boltslinger/houndmaster;
    "Mana- and Rage-hybrid" -- black-knight; "Mana ... Hunt layers on a small
    secondary pool of Rage" -- inquisition). Both are UnitPower reads, so the
    envelope holds two `power` bars: the spec's PRIMARY (Sidekick's own
    Resource line) full-height nearest the main row, the other half-height
    with no value text -- `minor` prominence per notes/layout-standard.md.

  * HOUNDMASTER IS A PERMANENT-PET SPEC. The Shadowhound is summoned once
    (Houndmaster's Whistle, free at the top of the tree since 2026-08-01) and
    the spec's damage is the hounds. It gets a NO HOUND alert and its proc row
    tracks the HOUND's ramp (Shadow Rage) with a `unit="pet"` aura trigger.
    Requirements §6.1 flags the absent-unit inverse as fork-unverified.

  * EXECUTE GATES CARRIED BY USABILITY, LIFTED BY PROCS. Damnation (<=35%),
    Stake (<=35%), Quickdraw (after a crit) and Desecrate (after an avoid)
    are all "not castable right now" states -- `spellUsable == 0 ->
    desaturate` reads them without any custom health machinery -- and the
    procs that LIFT the execute gates (Slinging Bolts, Heartstopper) glow the
    button through PROC_GLOW.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build, DRAFT. Never imported in game; the inventory roles were
# machine-proposed and bulk-cleared (recorded in buildlog-witch-hunter.json),
# and requirements §6 lists what only the client can settle.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
# FALLBACK fills ids with NO art in any scrape (db.ascension.gg serves a
# questionmark on these spells' own pages): the six Edicts and the Purity
# stack aura. Classic-client scroll/seal icons, none of which appears in any
# other row of this pack.
FALLBACK = {
    # plain and Greater share a long-term row, so each pair gets DISTINCT art
    # or the duplicate-art check fires on its own fallback.
    "Knight's Edict": "inv_scroll_07",
    "Greater Knight's Edict": "inv_scroll_08",
    "Inquisitor's Edict": "inv_scroll_02",
    "Greater Inquisitor's Edict": "inv_scroll_09",
    "Witching Edict": "inv_scroll_05",
    "Greater Witching Edict": "inv_scroll_10",
    "Purity": "spell_holy_sealofvalor",
}
OVERRIDE = {
    # ONLY deliberate choices belong here: an entry overrides the CLIENT's own
    # art for the spell. Empty until the duplicate-art check demands one --
    # the first build's row-level art survey found no collision inside any
    # single row (Dark Intuition and Night's Watch share art but never share
    # a band).
}
# db.exil.es points at rows db.ascension.gg / the official builder do not
# corroborate as the castable; corrections here are name -> id, and an
# in-game tooltip outranks them (resources/in-game-verified.json).
CROSSCHECK = {
    # db.exil.es's "Houndmaster's Call" rows are 706332 (rank "Damage", the
    # strike component) and 680240 ("(Energize)") -- neither is the button.
    # The OFFICIAL Vol'jin builder's tree node grants 802273
    # (talents-witch-hunter.json), which is the id the character learns.
    # Requirements §6.3; tooltip read settles it.
    "Houndmaster's Call": 802273,
    # TWO db.exil.es rows one capitalisation apart: "Unleash The Hounds"
    # 800768 is rank "UNUSED"; "Unleash the Hounds" 807918 is Rank 1, 10 s
    # cooldown, 20 s duration -- and the official tree grants 807918.
    "Unleash the Hounds": 807918,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: a new class starts on every default.
#
# CD_PER_ROW is derived from the NARROWEST main row in the pack -- every spec
# here renders five 44px main icons, so row_w(5) = 228px and the rule
# `28w - 2 <= 1.2 * 228` allows w <= 9.8 -> 9. Confirmed against the built
# packs by tools/rowwidths.py. Do NOT copy this number to another class.
CLS = W.init("witch-hunter", version=VERSION, prefix="WH", cd_per_row=9,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# Abilities that hold charges rather than a plain cooldown. Counts are
# tooltip-read (db.exil.es renders no Charges row): Hunt is "2 Charges, 25 sec
# recharge" in its own talent text. Purified Bola's 2 charges belong to the
# TALENT's replacement spell, not to the base Bola Throw the pack draws --
# a "2" on the untalented button would lie (requirements §6.6).
CHARGES = {"Hunt": 2}

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text.
PROC_GLOW = {
    # "which can be consumed by casting Heartseeking Bolt to deal an
    # additional ... damage, stacking 2 times" (Bounty Hunter) and "Your next
    # Heartseeking Bolt within 10 seconds deals 25% more damage and incurs no
    # cooldown" (Bolt and Dash) -- both say press THIS button now.
    "Heartseeking Bolt": ["Bounty Hunter", "Bolt and Dash"],
    # "Your next Damnation is usable regardless of the target's current
    # health. Lasts 20 seconds." -- the execute outside its window.
    "Damnation": ["Slinging Bolts"],
    # "allow the use of Stake within 8 seconds regardless of the target's
    # health percentage" (Heartstopper, L40 passive).
    "Stake": ["Heartstopper"],
    # "Your next Dawn Blade within 15 seconds is free of cost and deals 25%
    # increased damage" (Dawn Knight, L50 passive) -- the Sidekick React
    # bucket: "fire the empowered ability the instant it lights up".
    "Dawn Blade": ["Dawn Knight"],
}
# Bounty Hunter stacks twice and Heartseeking Bolt spends it, so the count is
# drawn on the button it charges. First proc group owns the stack read.
PROC_STACKS = {"Heartseeking Bolt"}

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row: target debuffs and ground/burst effects. A name missing from
# here costs nothing but a display that never shows; a name wrongly here hides
# a running cooldown, so only the unambiguous cases are listed.
NO_BUFF = {"Slayer's Mark", "Grimshade Arbalest", "Witchblight",
           "Fiery Judgement", "Smite Evil", "Darkslayer's Lantern",
           "Witchblood Fever"}

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row. Witch Hunter's long-term content
# is inventory-driven, three families:
#
#   Edicts   Inquisitor's / Knight's / Witching, plain + Greater -- 30-minute
#            ally/raid empowerments that persist through death (2026-07-31
#            changelog), the class's tattoo-equivalent.
#   Stances  Crossbow / Musket / Blade -- each spec's weapon stance
#            (requirements §6.2: stance-as-aura is fork-unverified, so these
#            are active-only trackers and there is NO missing-stance alert).
#   other    Dark Aura, Night's Watch (the tank's threat toggle), Night Hunter.
LONGTERM_COL = {
    "Edict": (0.95, 0.85, 0.45),
    "Stance": (0.60, 0.85, 0.75),
    "other": (0.75, 0.70, 1.00),
}


def _family(name):
    if "edict" in name.lower():
        return "Edict"
    if "stance" in name.lower():
        return "Stance"
    return "other"


def longterm_for(spec_key):
    """Every `longterm` inventory row this spec can actually cast."""
    return sorted(n for n, a in ABILITIES.items()
                  if a["default"] == "longterm"
                  and (a["specs"] is None or spec_key in a["specs"]))


def longterm_band(spec_name, spec_key, bands, y):
    """The long-term row for ONE spec, anchored under its own cooldown stack.

    The gate comes free: the merge tags any leaf whose parent chain reaches
    `WH <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The levelling tradeoff is the standing one -- the L10
    passives gating each spec arrive with the first talent point, so the
    window a levelling character goes without this band is days, not levels.
    """
    band = f"WH {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = LONGTERM_COL[_family(name)]
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"WH {spec_name} Longterm {name}", band,
            # By id AND name: the Edicts come in plain and Greater pairs whose
            # names are suffixes of each other, and several rows are ranked --
            # matching either covers both failure shapes.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"WH {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. The tonics live here because they are defensive-row cooldowns
# whose 10 s windows (post-07/31) would otherwise have no running-state icon
# -- cd_buffs only derives from the offense row.
SHORT_ENTRIES = [
    ("Dark Intuition", (0.80, 0.70, 1.00), {}),
    ("Witchblood Tonic", (0.60, 0.50, 0.90), {}),
    ("Vampiric Tonic", (0.90, 0.35, 0.35), {}),
]

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

# Core carries nothing class-wide: the one reminder in this pack (NO HOUND)
# is spec-shaped. The group still exists so the pack keeps the standard
# Core/spec skeleton.
add(B.group("WH Core", ROOT, CORE, x=0, y=0))


def envelope(spec_name, bands, primary="rage"):
    """Rage + mana, two power bars in the fixed-height envelope (~-156..-186).

    The spec's PRIMARY (Sidekick's Resource line) renders full-height nearest
    the main row; the secondary renders under it at half height with no value
    text -- `minor` prominence, full width kept so the width-lock invariant
    holds (notes/layout-standard.md). Every spec gets the same two-band
    depth, so no anchor below the envelope moves between specs.
    """
    w = row_w(5)
    rage = (0.85, 0.30, 0.25, 1.0)
    mana = (0.30, 0.45, 0.95, 1.0)

    def bar(kind, y, h, minor=False):
        gid = f"WH {spec_name} {'Rage' if kind else 'Mana'}"
        subs = [] if minor else [B.sub_text("%p", size=10,
                                            anchor="INNER_RIGHT", x=-4,
                                            justify="RIGHT")]
        add(B.aurabar(gid, f"WH {spec_name}",
                      [B.power_trigger("player", kind)],
                      x=0, y=y, w=w, h=h,
                      color=rage if kind else mana,
                      subregions=subs))
        bands.append(gid)

    if primary == "rage":
        bar(1, Y_BAR, BAR_H_STACKED)            # rage, full height, on top
        bar(0, Y_SEG, 10, minor=True)           # mana, minor
    else:
        bar(0, Y_BAR, BAR_H_STACKED)            # mana, full height, on top
        bar(1, Y_SEG, 10, minor=True)           # rage, minor


# ============================================================== 2. BOLTSLINGER
# Mobile crossbow skirmisher. Press order is the cited rotation
# (sidekick-witch-hunter-boltslinger, 2026-08-07): Darkslayer builds Bounty
# Hunter and Rage while moving, Witchbane channels, Tormentor's DoT rolls,
# the charged Heartseeking Bolt is the payoff, Damnation dumps Rage in the
# execute window (Slinging Bolts lifts the gate).
BS = []
BS.append(cd_group("WH Boltslinger Main", "WH Boltslinger",
                   ["Darkslayer", "Witchbane", "Tormentor",
                    "Heartseeking Bolt", "Damnation"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="boltslinger"))
envelope("Boltslinger", BS, primary="rage")
# Your DoT on the target -- "Open with Tormentor to lay its DoT" -- plus the
# healing cut Heartseeking Bolt leaves.
BS.append(dot_bars("WH Boltslinger Target", "WH Boltslinger",
                   [("Tormentor", (0.70, 0.60, 1.00), {})],
                   y=Y_TARGET, refresh_at=4))
_y_BS = emit_bottom_block("Boltslinger", "boltslinger", BS,
                          [("Bounty Hunter", (1.00, 0.85, 0.40)),
                           ("Slinging Bolts", (1.00, 0.60, 0.30)),
                           ("Bolt and Dash", (0.60, 0.85, 1.00)),
                           ("The Bane of Witches", (0.80, 0.55, 1.00))],
                          SHORT_ENTRIES)
longterm_band("Boltslinger", "boltslinger", BS, _y_BS)
add(spec_group("WH Boltslinger", BS))


# ============================================================== 3. HOUNDMASTER
# THE PET SPEC. A permanent Shadowhound (plus temporary lesser hounds) does
# the damage while ranged autos generate Rage. Press order from the cited
# rotation: keep hounds out (Unleash the Hounds), fire Quickdraw when a crit
# enables it, send Houndmaster's Call, channel Darkflock; Shadowblast is the
# builder that feeds the hound Shadow Rage and regenerates mana.
HM = []

# NO HOUND: the whole spec hangs on the Shadowhound being alive. Trigger 1
# asks the PET unit for the hound's own permanent aura and fires on absence;
# trigger 2 gates on knowing the summon at all, so a character who cannot
# whistle yet is not nagged. Whether an absent unit reports "missing" on this
# fork is requirements §6.1 -- the one alert in the pack built on unverified
# ground, flagged there rather than silently trusted. The hound aura id
# (Shadowhound Visual 500036, rank "Scaling", duration -1) is the same §6.1
# question; the name is matched alongside it.
_no_hound = B.icon(
    "WH Houndmaster Alerts No Hound", "WH Houndmaster Alerts",
    [B.aura_trigger(["500036", "Shadowhound Visual"], unit="pet",
                    own_only=False, show_on="showOnMissing"),
     B.spell_known_trigger(sid("Houndmaster's Whistle"))],
    ic("Houndmaster's Whistle"), size=SZ_ALERT, desaturate=True,
    subregions=[B.sub_background(),
                B.sub_text("NO HOUND", size=10, anchor="INNER_BOTTOM",
                           color=(1, 0.35, 0.35, 1)),
                B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                             edge=EDGE),
                B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])
NEEDS_ALL.add(_no_hound["id"])      # missing-aura AND spell-known, never "any"
add(_no_hound)
add(B.dynamicgroup("WH Houndmaster Alerts", "WH Houndmaster",
                   ["WH Houndmaster Alerts No Hound"], x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
HM.append("WH Houndmaster Alerts")

HM.append(cd_group("WH Houndmaster Main", "WH Houndmaster",
                   ["Shadowblast", "Quickdraw", "Houndmaster's Call",
                    "Darkflock", "Unleash the Hounds"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="houndmaster"))
envelope("Houndmaster", HM, primary="rage")
# The hound's ramp rides the on-me row with unit="pet". Decimate's caster
# half (07/31) arrives through cd_buffs off the offense row.
_y_HM = emit_bottom_block("Houndmaster", "houndmaster", HM,
                          [("Shadow Rage", (0.70, 0.50, 0.95),
                            {"unit": "pet"}),
                           ("Scent of Magic", (0.55, 0.85, 1.00))],
                          SHORT_ENTRIES)
longterm_band("Houndmaster", "houndmaster", HM, _y_HM)
add(spec_group("WH Houndmaster", HM))


# ============================================================= 4. BLACK KNIGHT
# THE TANK (Sidekick: "Solid main-tank for raid bosses"). Auto-attacks feed
# the two-hander kit; press order from the cited rotation: Noctis Blade on
# cooldown (the self-heal), Pommel Smash builds its stacks and procs
# Shadowstorm, Desecrate after an avoid, Dawn Blade rides the Dawn Knight
# proc, March of the Black King refunds Rage and holds AoE threat.
BK = []
BK.append(cd_group("WH Black Knight Main", "WH Black Knight",
                   ["Noctis Blade", "Pommel Smash", "Desecrate",
                    "Dawn Blade", "March of the Black King"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="black-knight"))
envelope("Black Knight", BK, primary="mana")
# The threat maintain and its riders, all on the enemy target. Every row
# matches by id AND name: Shadow Brand / Witchblood Fever are applied by
# passives (the aura's own id is uncaptured) and Pommel Smash's stack debuff
# rides its Rank 1 castable.
BK.append(dot_bars("WH Black Knight Target", "WH Black Knight",
                   [("Shadow Brand", (0.70, 0.50, 0.95), {"by_name": True}),
                    ("Pommel Smash", (0.95, 0.80, 0.45), {"by_name": True}),
                    ("Knight's Seal", (0.60, 0.85, 0.75), {"by_name": True}),
                    ("Witchblood Fever", (0.90, 0.35, 0.35),
                     {"by_name": True})],
                   y=Y_TARGET, refresh_at=3))
_y_BK = emit_bottom_block("Black Knight", "black-knight", BK,
                          [("Dawn Knight", (1.00, 0.85, 0.40)),
                           ("Witching", (0.70, 0.80, 1.00)),
                           ("Undying", (0.90, 0.35, 0.35)),
                           ("Clinch Fighting", (1.00, 0.60, 0.30))],
                          SHORT_ENTRIES)
longterm_band("Black Knight", "black-knight", BK, _y_BK)
add(spec_group("WH Black Knight", BK))


# ============================================================== 5. INQUISITION
# Dual-wield build-and-spend melee. Press order from the cited rotation:
# Dawn Blade grants Flames of Sin, Purifier's Edge and Torchlight spend the
# Purity & Wickedness / Dawn / Dusk stacks, Dusk Blade is the health siphon,
# Stake is the execute (Heartstopper lifts the gate).
IQ = []
IQ.append(cd_group("WH Inquisition Main", "WH Inquisition",
                   ["Dawn Blade", "Purifier's Edge", "Dusk Blade",
                    "Torchlight", "Stake"],
                   y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                   spec="inquisition"))
envelope("Inquisition", IQ, primary="mana")
# The main-hand / off-hand marks you are stacking on the target. By name:
# the stack auras (Purity 681413 / Wickedness 681523) are rank "Proc" rows,
# the documented component smell, so the name carries the match.
IQ.append(dot_bars("WH Inquisition Target", "WH Inquisition",
                   [("Purity", (1.00, 0.85, 0.40), {"by_name": True}),
                    ("Wickedness", (0.70, 0.50, 0.95), {"by_name": True})],
                   y=Y_TARGET, refresh_at=3))
_y_IQ = emit_bottom_block("Inquisition", "inquisition", IQ,
                          [("Flames of Sin", (1.00, 0.60, 0.30)),
                           ("Dawn", (1.00, 0.85, 0.40)),
                           ("Dusk", (0.60, 0.60, 0.95)),
                           ("Searing Hilt", (1.00, 0.75, 0.35)),
                           ("Torch the Wicked!", (0.95, 0.55, 0.25)),
                           ("Cycle of Despair", (0.80, 0.70, 1.00))],
                          SHORT_ENTRIES)
longterm_band("Inquisition", "inquisition", IQ, _y_IQ)
add(spec_group("WH Inquisition", IQ))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# ---------------------------------------------------------------- leaf gating
# One spell only that spec knows, for load.use_spellknown. Three of the four
# L10 spec passives are a contiguous block the official builder marks as the
# tree-top Ability grant (talents-witch-hunter.json: 92091 / 92093 / 92094);
# Spell Known on a passive is proven ground on this fork (Chronomancer's
# Eternity Warper gate, verified in game). Black Knight's tree-top node is
# typed Talent rather than Ability and grants 707064 (Grasp of the Undying)
# -- the one gate id here that is builder-sourced rather than digest-sourced.
# Requirements §6.5 carries the Deadeye-rename caveat on 92093.
SPEC_KNOWN = {
    "Boltslinger": 92091,     # Boltslinger, the L10 passive
    "Houndmaster": 92093,     # Houndmaster (renamed Deadeye 08/01; id kept)
    "Black Knight": 707064,   # Grasp of the Undying, the tree-top grant
    "Inquisition": 92094,     # Flames of Sin, the L10 passive
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
