"""Build the `Chronomancer [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Second class through the process in `notes/class-pack-process.md`, and the one
that tests whether that process is real. Layout follows
`notes/layout-standard.md` -- flush icon bands at fixed offsets, DESATURATION
carrying availability rather than glow on everything.

        [ reminders ]                                 <- band 1, active-only
        [ on TARGET: your HoTs / your DoTs ]          <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 9
              [ defensive + utility       ]           <- band 7, wraps at 9
              [ long-term buffs           ]           <- band 8, active-only

Three things here have no Runemaster analogue:

  * The TIME spec is the first HEALING spec in any pack. Healing surfaces are
    deliberately scoped OUT -- raid frames belong to VuhDo/Grid on 3.3.5a. What
    the pack does carry is the target band: your own HoTs/absorbs on your
    current target, glowing when one needs a refresh.

  * The four AEONS are mutually-exclusive infinite self-buffs that reshape both
    Epoch and Ripple. `Eternity Warper` (806301) gives Ripple a different effect
    per Aeon, so Ripple is emitted as FIVE displays -- one per Aeon plus a
    no-Aeon default -- and the dynamic group lays out whichever one is showing.
    That reuses the same loaded-and-showing mechanism that lets one band serve
    three specs, instead of betting the main rotation icon on icon-swap
    conditions.

  * ARTIFICER spends combo points alongside mana, so its resource envelope
    holds two bands where Engravement and Riftblade held one.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt and the group name. WeakAuras dedupes imports
# on uid, so a rebuilt pack MUST carry a different salt or the client treats it
# as already-installed and silently keeps the old copy. Bump on any release.
#
# It ALSO reaches the group name ("Chronomancer [CoA] v1.2"), so the loaded
# version is readable in the WeakAuras list and a screenshot identifies its own
# build. That is what makes a community bug report triageable.
#
# 1.1: six abilities the 1.0 inventory never carried a row for. Five
# single-spec castables -- Accelerate, Decelerate (artificer), Chronostasis
# (infinite), Moment's Reprieve, Rehatch (time) -- plus Shifting Sands, an 8s
# attack-power debuff on the Infinite target band.
# 1.2: one long-term band per spec, anchored under that spec's own ladder.
VERSION = "1.2"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {}
OVERRIDE = {
    # ONLY deliberate choices belong here, because an entry here overrides the
    # CLIENT's own art for the spell (see the iconSource note below).
    #
    # Two pairs share art upstream and can appear side by side, which is what
    # the duplicate-art check is for. Both replacements are borrowed from
    # Chronomancer spells that carry real art and never appear in a cooldown
    # row, so the fix cannot introduce a fresh clash.
    "Slow Time": "achievement_challengemode_auchindoun_hourglass",
    "Incarnation of Order": "spell_arcane_portal_valeofblossoms",
}

# Art that db.ascension.gg does not have. It serves a questionmark on these
# spells' own pages -- but the CLIENT does, and its texture is the right one.
# Hasten is the proof: db.ascension has no art, the game draws a boot, and a
# placeholder picked from the class's icon pool drew a clock instead.
#
# RESOLVED 2026-08-08, all but Fray Magic: db.exil.es spell PAGES serve the
# client's own DBC texture as the og:image icons-clean name (the earlier "no
# icon field" finding was about its JSON API). Those textures now sit in
# icon-meta-chronomancer.json keyed by the id the trigger uses (Hasten 801304
# -> nhi_magicspeed_border, the boot), so displayIcon matches the client
# instead of guessing at it. Fray Magic (800053) stays: its exil.es page has
# no og:image and db.ascension answers questionmark, so it still resolves
# from the trigger alone.
NO_UPSTREAM_ART = {"Fray Magic"}
# Not tooltip-verified, but db.exil.es points at a spell db.ascension.gg does
# not mark as an ability while ascension.gg has a clear Ability/Talent entry.
# Replace with a tooltip id when one is captured.
# db.exil.es maps "Aeon of Resilience" to 92119, which is the LEVEL 10 PASSIVE
# whose entire tooltip is "Teaches you Aeon of Resilience" -- it has no cooldown
# row, the documented smell for a wrong id, and it is flagged Passive. The
# castable stance is 806291.
#
# Two independent routes agree: 806291 is the hole in the otherwise contiguous
# 806290/806292/806293 Aeon block, and a working community pack uses it
# alongside the other three. The cooldown audit corroborates by omission -- it
# found the other three Aeons at 10 sec and could not find Resilience at all.
CROSSCHECK = {
    "Aeon of Resilience": 806291,
    # db.exil.es links a COMPONENT of the ability rather than the ability, and
    # the component is never castable and never known -- so the icon draws the
    # wrong art AND its gate silently fails. tools/spellmeta.py flags these by
    # rank_text; all three were caught in game first.
    "Temporal Focus": 806165,     # 528056 is rank "DR", the mitigation aura
    "Singularity Core": 804438,   # 804437 is rank "Damage", the damage effect
    "Infinite Clone": 804492,     # 704154 is rank "Player Aura"
}


# Identity, data and the entire build vocabulary come from wapack. CD_PER_ROW
# is derived from the NARROWEST main row in the pack -- see the note there.
# Chronomancer's is five icons (182px): 28w - 2 <= 1.2 * 182 gives w <= 7.8,
# so 7. Do NOT copy that number to another class; recompute it.
#
# init() runs BEFORE the star import because it is what gives the unqualified
# names below their values. Chronomancer is on every convergence default, so
# it passes no flags -- a new class should look exactly like this.
CLS = W.init("chronomancer", version=VERSION, prefix="CM", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above


# Abilities that hold charges rather than a plain cooldown. These get a count
# drawn in the corner; everything else would just show a meaningless "1".
# Zenith only has charges once Runelord is talented (it becomes 712389), but
# the count is harmless on the base version.
# Fabric of Time gains a second charge from Timeblender; the count is
# harmless on the base version.
CHARGES = {"Fabric of Time": 2}


# Artificer's Continuum spells. Mutually exclusive -- "you can only have 1
# Continuum spell active at a time" -- and each empowers your wand for a window
# that grows as you spend Echo Fragments.
CONTINUUM = ["Singularity Core", "Flux Emitter", "Paradox Cannon",
             "Aether Compression"]

# When one of these buffs is up, the ABILITY it empowers glows -- the same
# "use this now" cue the game gives you. Keyed ability -> the procs that light
# it, taken from the talent text.
PROC_GLOW = {
    # Each Continuum glows while its OWN 5 sec buff is running. The cooldown
    # swipe answers "when can I swap"; it cannot answer "which one is empowering
    # my wand right now", which is the thing you actually read mid-fight.
    "Singularity Core": ["Singularity Core"],
    "Flux Emitter": ["Flux Emitter"],
    "Paradox Cannon": ["Paradox Cannon"],
    "Aether Compression": ["Aether Compression"],
    # ability -> the procs that say "press this now"
    "Artificer's Wand": ["Clocked In"],     # next wand instant, banks a fragment
    "Chromatic Shard": ["Chaos Fusion"],    # castable while moving
    "Melt Reality": ["Chaotic Time"],       # amped and replicated
    "Epoch": ["Sands of Time"],             # -20% cast time per stack
    "Reverse Wound": ["Endless Sands"],     # -20% cast time per stack, to 5
}

# Abilities whose PROC_GLOW buff also STACKS, drawn as a number on the icon
# rather than as a bar of its own. Endless Sands is a Reverse Wound modifier
# (-20% cast time per stack, up to 5) built by Epoch and Correct the Mistake,
# so it belongs on the button it changes -- a second segmented bar under the
# Sands of Time one would put two five-stack meters side by side and make the
# player read which is which mid-cast.
PROC_STACKS = {"Reverse Wound"}
# Class content the engine reads while it lays bands out. Everything here is
# Chronomancer's own; the engine has no defaults for any of it.
W.configure(charges=CHARGES, continuum=CONTINUUM, proc_glow=PROC_GLOW,
            proc_stacks=PROC_STACKS,
            # Mobility and self-rescue apply no buff worth a second icon in the
            # buff row, so they are skipped rather than listed in a tail.
            no_buff={"Displacement", "Backtrack", "Rewind", "Infinite Clone"})


# ================================================================== 1. CORE
CORE = []

# ---- long-term buffs -------------------------------------------------------
# Active-only row at the bottom: state you check once per pull rather than
# react to. Runemaster filled this with runic tattoos and weapon engravings;
# Chronomancer has no imbue kit at all, so it carries the class Intellect buff
# and -- on Time -- which AEON is currently up.
#
# DATA, not displays. The band is emitted once per spec by longterm_band()
# below, anchored under that spec's own utility row. It used to be a single
# band in CM Core at a fixed Y_LONG clearing the DEEPEST spec, which cost
# Artificer and Time a dead row each -- the one gap the un-merge could not
# remove, and the last thing Runemaster had that Chronomancer did not.

# The 30-minute self-buff family. This is Chronomancer's equivalent of
# Runemaster's tattoos and weapon engravings: things you set once at the start
# of a session and only notice when they have dropped.
#
# WISDOMS ARE MUTUALLY EXCLUSIVE. Chromie's Wisdom says it outright -- "Only
# one Wisdom per Chronomancer can be active" -- so Intellect and Spirit are a
# choice, not a stack. That is why the reminder below fires on NONE of the four
# rather than per-buff: nagging for the one you deliberately did not take would
# be permanently on screen, which is the exact failure the reminder band had on
# Runemaster.
WISDOMS = [
    ("Nozdormu's Wisdom", 572391, (0.55, 0.75, 1.00)),          # +Intellect
    ("Greater Nozdormu's Wisdom", 572396, (0.55, 0.75, 1.00)),
    ("Chromie's Wisdom", 801523, (0.95, 0.80, 0.45)),           # +Spirit
    ("Greater Chromie's Wisdom", 680307, (0.95, 0.80, 0.45)),
]
# The three "Surround yourself with <school> magic" buffs, all 30 min, all
# self-cast. Whether these are ALSO mutually exclusive is unconfirmed -- the
# tooltips do not say so and only the Wisdoms carry the exclusivity line. The
# band is active-only either way, so it renders correctly under both readings;
# worth one in-game check before the reminder below is trusted.
TEMPORALS = [
    ("Temporal Restoration", 680456, (0.45, 0.90, 0.55)),   # mana regen in combat
    ("Temporal Resilience", 680389, (0.80, 0.70, 0.50)),    # armor + slows attackers
    ("Temporal Swiftness", 680390, (0.60, 0.85, 1.00)),     # spell haste from Spirit
]
# The four Aeons. Infinite-duration mutually-exclusive self-buffs that reshape
# BOTH Epoch and Ripple, so which one is up is persistent state rather than a
# proc -- long-term is exactly the band for it.
#
# MATCH BY SPELL ID, NEVER BY NAME. Two decoys share the namespace: 807158 is
# a second "Aeon of Resilience" teaching passive, and 583921 is
# "Aeon of Oblivion SLS", a stale stub carrying the same name AND the same
# icon with 1% crit against the live 30%. A name match takes either one.
#
# Resilience is 806291, NOT the 92119 db.exil.es reports -- that id is the
# level 10 passive whose whole tooltip is "Teaches you Aeon of Resilience",
# and it has no cooldown row, which is the documented smell for a wrong id.
# Two independent routes agree on 806291: it is the hole in the otherwise
# contiguous 806290/806292/806293 block, and a working community pack uses it
# alongside the other three.
#
# NO `%p` TIMER on these. duration_ms is -1, so UnitAura reports duration 0 and
# expirationTime 0; a timer subregion would render empty forever.
AEONS = [
    ("Renewal",    806290, (0.45, 0.90, 0.55)),
    ("Resilience", 806291, (0.95, 0.85, 0.45)),
    ("Protection", 806292, (0.55, 0.75, 1.00)),
    ("Oblivion",   806293, (0.90, 0.35, 0.35)),
]

def longterm_band(spec_name, bands, y):
    """The long-term row -- Wisdoms, Temporals, Aeons -- ONE PER SPEC,
    anchored under that spec's own cooldown stack.

    Runemaster made this move first and the reasoning carries over exactly. A
    Core band has ONE yOffset for the whole pack, so it had to clear the spec
    that stacks deepest: Artificer and Time each wrap 5 rows where Infinite
    takes 5 too, but the fixed anchor is computed from `_DEEPEST` and holds
    that depth on every spec whatever it renders. The gap is invisible in the
    in-play view because these displays are active-only, which is why it went
    unnoticed for so long -- it only appears once a long-term buff is up.

    Per-spec costs one copy of each icon per spec, and the gate comes free:
    the merge tags any leaf whose parent chain reaches `CM <Spec>` with that
    spec, and apply_leaf_gates then puts the spec's signature spell on it.

    The tradeoff, taken knowingly and the same one Runemaster took: a
    Chronomancer below level 10 has no signature spell yet (Maw of Chaos L10,
    Shatter Echo and Ripple L11) and so will not see this band. The Aeons are
    far later content and the Wisdoms are self-buffs rather than reminders, so
    nothing that character needs to react to is hidden. If a levelling report
    says otherwise, the fix is to leave the Wisdoms in Core and move only the
    Aeons, not to go back to one shared band.
    """
    band = f"CM {spec_name} Longterm"
    out = []
    for name, aura, col in WISDOMS + TEMPORALS:
        out.append(add(B.icon(
            f"CM {spec_name} Longterm {name}", band,
            [B.aura_trigger([str(aura), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    for label, aura, col in AEONS:
        out.append(add(B.icon(
            f"CM {spec_name} Longterm Aeon of {label}", band,
            [B.aura_trigger([str(aura)], exact_id=True)],
            ic(f"Aeon of {label}"), size=SZ_SMALL,
            subregions=[B.sub_text(label[:3].upper(), size=9,
                                   anchor="INNER_BOTTOM", color=col + (1.0,)),
                        thin()])))
    add(B.dynamicgroup(band, f"CM {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)

# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row. Data here rather than displays, same as Runemaster.
SHORT_ENTRIES = [
    ("Temporal Focus", (0.70, 0.80, 1.00), {}),
    ("Time Out!", (1.00, 0.60, 0.30), {}),
    ("Hasten", (0.50, 0.90, 1.00), {}),
    ("Timeguard", (0.80, 0.70, 1.00), {}),
    ("Shield of the Ages", (0.60, 0.85, 1.00), {}),
]

# ---- missing-buff reminders ------------------------------------------------
# High and central, and invisible once you are buffed -- each fires only on
# ABSENCE. Chronomancer has one class-wide case; Time adds its own no-Aeon
# reminder inside the spec block, where the spec gate applies to it.
ALERTS = []

for _label, _set, _art in (("NO WISDOM", WISDOMS, "Nozdormu's Wisdom"),
                           ("NO TEMPORAL", TEMPORALS, "Temporal Restoration")):
    ALERTS.append(add(B.icon(
        f"CM Alerts {_label.title()}", "CM Alerts",
        [B.aura_trigger([str(a) for _n, a, _c in _set]
                        + [_n for _n, _a, _c in _set],
                        own_only=False, show_on="showOnMissing")],
        ic(_art), size=SZ_ALERT, desaturate=True,
        subregions=[B.sub_background(),
                    B.sub_text(_label, size=10, anchor="INNER_BOTTOM",
                               color=(1, 0.35, 0.35, 1)),
                    B.sub_border(color=(1, 0.2, 0.2, 1), size=2, offset=1,
                                 edge=EDGE),
                    B.sub_glow(True, "buttonOverlay", (1, 0.3, 0.3, 1))])))

add(B.dynamicgroup("CM Alerts", "CM Core", ALERTS, x=0, y=Y_ALERT,
                   grow="HORIZONTAL", space=6))
CORE.append("CM Alerts")

add(B.group("CM Core", ROOT, CORE, x=0, y=0))


# ============================================================== 2. ARTIFICER
# Ranged wand spec. Artificer's Wand is the filler and the Echo Fragment
# generator; fragments are spent on Distortion spells and on extending whichever
# Continuum spell is active (only one at a time).
A = []
A.append(cd_group("CM Artificer Main", "CM Artificer",
                  ["Artificer's Wand", "Wand of Time", "Discordance",
                   "Shatter Echo", "Decomposition"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="artificer"))
A.append(mana_bar("CM Artificer Mana", "CM Artificer", Y_BAR,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5), h=BAR_H_STACKED))
# Echo Fragments: "Used to empower some abilities. Stacks 5 times." One aura
# (804455) whose stack count fills the row, so this is stack_bar rather than
# seg_bar -- there is no set of five distinct auras to match.
stack_bar("CM Fragment", "CM Artificer", 804455, 5, (0.55, 0.85, 1.00),
          Y_SEG, B.health_trigger("player"), row_w(5), A)
# Your DoT on the target. Threads of Eternity rides Discordance.
# "Thread of Eternity" (572127) is the DOT. "ThreadS of Eternity" (806209) is
# the PASSIVE that applies it -- rank "Passive", duration -1, never on a target.
# One letter apart, and the band showed nothing because of it.
A.append(dot_bars("CM Artificer Target", "CM Artificer",
                  [("Thread of Eternity", (0.75, 0.55, 1.00), {})],
                  y=Y_TARGET, refresh_at=4))
_y_A = emit_bottom_block("Artificer", "artificer", A,
                         [("Discovery", (0.6, 0.9, 1.0)),
                          ("Clocked In", (1.0, 0.85, 0.4)),
                          ("Singularity Core", (0.8, 0.6, 1.0)),
                          ("Flux Emitter", (0.5, 0.9, 0.8)),
                          ("Aether Compression", (0.7, 0.8, 1.0)),
                          ("Paradox Cannon", (1.0, 0.7, 0.4))],
                         SHORT_ENTRIES)
longterm_band("Artificer", A, _y_A)
add(spec_group("CM Artificer", A))

# =============================================================== 3. INFINITE
# Chaos DoT caster. Mana only -- Sidekick is explicit that there is "no dual
# Order/Chaos economy" -- so the resource envelope holds one full-height bar
# and no segment row.
I = []
I.append(cd_group("CM Infinite Main", "CM Infinite",
                  ["Chromatic Shard", "Melt Reality", "Timerend", "Unmake",
                   "Discordance"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="infinite"))
I.append(mana_bar("CM Infinite Mana", "CM Infinite", Y_BAR_SOLO,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5)))
# The spec IS its DoTs -- Anomaly Spikes, the haste stacks and the cooldown
# shave all key off periodic damage, so anything dropping is a real loss.
I.append(dot_bars("CM Infinite Target", "CM Infinite",
                  [("Melt Reality", (0.90, 0.35, 0.85), {}),
                   ("Timerend", (0.70, 0.60, 1.00), {}),
                   ("Unmake", (0.85, 0.45, 0.35), {}),
                   ("Decomposition", (0.60, 0.85, 0.55), {}),
                   # 8s attack-power cut, off-GCD and cheap, so the useful cue
                   # is the timer rather than the button. Sidekick buckets it
                   # as `maintain` for the same reason.
                   ("Shifting Sands", (1.00, 0.80, 0.35), {})],
                  y=Y_TARGET, refresh_at=5))
_y_I = emit_bottom_block("Infinite", "infinite", I,
                         [("Anomaly Spikes", (0.9, 0.5, 1.0)),
                          ("Hourglass of Eternity", (0.5, 0.9, 1.0)),
                          ("Infinite Power", (1.0, 0.85, 0.4)),
                          ("Chaos Fusion", (1.0, 0.5, 0.3)),
                          ("Chaotic Time", (0.8, 0.4, 0.9))],
                         SHORT_ENTRIES)
longterm_band("Infinite", I, _y_I)
add(spec_group("CM Infinite", I))

# =================================================================== 4. TIME
# The first HEALING spec in any CoA pack. Healing surfaces are scoped OUT by
# design -- no raid frames, no multi-target HoT grid. What it gets instead is
# the target band above, carrying your own HoTs and absorbs on whoever you have
# selected, glowing when one needs a refresh.
T = []

# Ripple is FIVE displays, not one. `Eternity Warper` (806301) gives the Ripple
# channel a different effect per active Aeon, and each of those four effects is
# its own spell with its own art. So each variant is gated on its Aeon's aura
# and only the matching one is ever showing -- the dynamic group lays out
# exactly one, the same loaded-and-showing mechanism that lets a single band
# serve three specs.
#
# The alternative -- one display with four aura triggers swapping displayIcon
# by condition -- is fewer displays but bets the MAIN ROTATION ICON on
# condition reliability, and conditions in this fork have misfired before.
#
# The fifth is not padding. A character who has never cast an Aeon has none:
# the level 10 passive only TEACHES Aeon of Resilience, it does not apply the
# stance. That state is reachable and it needs an icon.
# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

# Displays whose icon is chosen by a CONDITION at runtime. They need
# iconSource = 0 or SetIcon has no effect -- state.icon wins and the swap
# is invisible. Kept as a registry so the blanket pass below cannot quietly
# reset them the way it did once already.
NEEDS_MANUAL_ICON = set()

# (label, Aeon aura id, Eternity Warper's Ripple spell id, art name)
#
# The icon shows WHICH Ripple you are about to cast, so you never have to check
# your Aeon first -- Aeon of Oblivion means Ripple reads as Rippling Oblivion.
#
# Two ids per row and the trigger matches EITHER. `auraspellids` is an
# any-of list, so one aura2 trigger covers both without touching disjunctive:
#   * the Aeon stance itself (806290..806293), infinite duration; and
#   * the `Rippling *` spell Eternity Warper grants (560382..560395), which the
#     research flagged as a duration -1 self aura the server may swap in when
#     the Aeon changes.
# Whichever the client actually exposes, the icon resolves. Matching only the
# Aeon left Ripple stuck on its default face in game.
RIPPLE_MODES = [
    ("Renewal",    806290, 560382, "Rippling Renewal"),
    ("Resilience", 806291, 560395, "Rippling Resilience"),
    ("Protection", 806292, 560393, "Rippling Protection"),
    ("Oblivion",   806293, 560386, "Rippling Oblivion"),
]

# The main row is built by hand rather than through cd_group, because Ripple
# is five icons that occupy ONE slot. Each variant carries Ripple's own
# cooldown trigger PLUS its Aeon's aura, so exactly one is ever loaded-and-
# showing, and the dynamic group lays out the row around whichever that is.
_time_main = []
# Press order. Reverse Wound sits next to Accelerated Recovery because that is
# what it is read against: it is the spot heal between HoT refreshes, and the
# Endless Sands count on its corner says how cheap the next cast is.
for _n in ("Epoch", "Accelerated Recovery", "Reverse Wound",
           "Correct the Mistake"):
    _time_main.append(add(cd_icon(f"CM Time Main {_n}", "CM Time Main", _n,
                                  SZ_MAIN, spec="time")))

# Ripple is ONE display whose ICON changes with the active Aeon, so you can see
# which effect you are about to get without checking your stance first.
#
# This is what the Icon region is built for. `RegionTypes/Icon.lua` declares
#     displayIcon = { display = {L["Icon"], L["Manual"]}, setter = "SetIcon",
#                     type = "icon" }
# as a CONDITION PROPERTY, so a condition may call SetIcon at runtime.
#
# ⚠️ It only works with `iconSource = 0`. UpdateIcon() resolves:
#       iconSource == -1 -> state.icon   (whatever the TRIGGER supplies)
#       iconSource ==  0 -> displayIcon  (what we set)
#     iconPath = iconPath or self.displayIcon or QUESTIONMARK
# Every icon we emit carried -1, which is why five different Rippling textures
# all drew as the same staff: the trigger tracks spell 806296 for all of them,
# so state.icon won and displayIcon was never more than a fallback.
_ripple = cd_icon("CM Time Main Ripple", "CM Time Main", "Ripple", SZ_MAIN,
                  spec="time")
_ripple["iconSource"] = 0
NEEDS_MANUAL_ICON.add(_ripple["id"])
_rip_conds = list((_ripple.get("conditions") or {}).values()) \
    if isinstance(_ripple.get("conditions"), dict) else list(_ripple.get("conditions") or [])
_rip_trigs = triggers_of(_ripple)

# Trigger 2 is ETERNITY WARPER itself (806301) -- the level 50 passive that
# gives Ripple its per-Aeon behaviour in the first place.
#
# Without it the icon LIES to a levelling character: Aeon of Resilience is
# taught at level 10, so a level 20 Chronomancer with an Aeon up would see
# "Rippling Oblivion" and be promised an effect the passive has not granted.
# Every face is therefore ANDed with this, and below 50 Ripple stays on its
# own icon, which is exactly what it does.
#
# ⚠️ NOT an aura trigger. 806301 is `effect=6 aura=4` -- APPLY_AURA /
# SPELL_AURA_DUMMY on self -- which is how 3.3.5 implements a passive, and
# those are hidden from UnitAura. An aura2 trigger on it never fires, so every
# AND below failed and Ripple stayed on its default face no matter the Aeon.
#
# "Spell Known" is the prototype built for this question: it runs
# `WeakAuras.IsSpellKnown(806301)` off SPELLS_CHANGED / PLAYER_TALENT_UPDATE,
# so it is true exactly when the character actually has Eternity Warper, and
# it re-checks on a respec.
_rip_trigs.append(B.spell_known_trigger(806301))
_EW = len(_rip_trigs)

# Match the AEON STANCES only (806290..806293). They are genuinely mutually
# exclusive -- one Aeon at a time, shared cooldown.
#
# NOT the `Rippling *` spells: those are `aura=42` PROC_TRIGGER_SPELL auras on
# self with duration -1, so if the server grants all four when Eternity Warper
# is learned they would all match at once and the last condition would win,
# pinning the icon to one face permanently.
for _label, _aeon, _rip, _art in RIPPLE_MODES:
    _rip_trigs.append(B.aura_trigger([str(_aeon)], exact_id=True))
    _rip_conds.append(B.cond(
        B.check_and(
            B.T({"trigger": len(_rip_trigs), "variable": "show", "value": 1}),
            B.T({"trigger": _EW, "variable": "show", "value": 1})),
        [B.change("displayIcon", ic(_art))]))
_ripple["triggers"] = B._trigger_wrap(_rip_trigs)
# "any": trigger 1 alone must keep Ripple on screen with no Aeon and no
# Eternity Warper. The conditions, not the trigger logic, pick the face.
_ripple["triggers"]["disjunctive"] = "any"
_ripple["conditions"] = B.arr(_rip_conds)
_time_main.append(add(_ripple))

add(B.dynamicgroup("CM Time Main", "CM Time", _time_main, x=0, y=Y_MAIN,
                   grow="HORIZONTAL", space=GAP))
T.append("CM Time Main")
# row_w(5): Epoch + Accelerated Recovery + Reverse Wound + Correct the Mistake
# + exactly ONE Ripple variant. Five Ripple displays are stored but only one is
# ever loaded-and-showing, so the row a player sees is five icons wide and the
# bar has to lock to that -- it was row_w(4) before Reverse Wound joined the row.
T.append(mana_bar("CM Time Mana", "CM Time", Y_BAR,
                  (0.30, 0.45, 0.95, 1.0), w=row_w(5), h=BAR_H_STACKED))
# Sands of Time: "stacking 5 times. Upon spending the 5th stack, all stacks are
# consumed." Built by casting Epoch, so it is the spec's real spend meter.
# 804488 is the BUFF; 501843 is the castable that grants it -- both are
# legitimately named "Sands of Time", which is why this matches by id.
stack_bar("CM Sands", "CM Time", 804488, 5, (0.95, 0.80, 0.45),
          Y_SEG, B.health_trigger("player"), row_w(5), T)
# YOUR HoTs and absorbs on YOUR TARGET, glowing when one is nearly out. This is
# the band the whole healing-scope decision turns on.
# YOUR heals and absorbs on YOUR TARGET, glowing when one is nearly out.
#
# The previous contents could never appear: "Aeon of Protection" is the STANCE
# you stand in (duration -1, on you), not the absorb it puts on the target, and
# "Mark of Order" is a passive. The real per-target effects are the four Aeon
# ones, each named for its Aeon without the "Aeon of" prefix:
#     Protection 560374  absorb          rework keeps a shield on the target
#     Renewal    560355  HoT             rework moved it 3s -> 6s, accumulating
#     Resilience 560373  was a 6s DR     ⚠️ see below
#     Oblivion   560376  was a 5s buff   ⚠️ see below
#
# ⚠️ ALL FOUR AEONS WERE REWORKED ON 2026/07/31 AND TWO OF THESE BARS MAY NOW BE
# DEAD. The durations above are pre-rework and the last two effects are not in
# the new text at all:
#     Aeon of Resilience  Epoch now makes Accelerated Recovery BOUNCE to another
#                         target. No per-target aura is described. Highest risk.
#     Aeon of Oblivion    Epoch now deals 100% of its healing as damage to a
#                         NEARBY ENEMY -- a splash, which may put nothing on the
#                         target you have selected.
# Both spell ids still resolve on db.ascension.gg, but a spell surviving in the
# database says nothing about whether anything still applies it. Pack 1.2 was
# verified in game on 2026-08-02, after the rework, so these displays were on
# screen -- nobody was checking whether a bar ever FILLS, which is the failure a
# post-rework verification pass does not catch by accident.
# UNKNOWN, and the thing that settles it is one trip: cast Epoch under each Aeon
# in turn and watch the band. Do not delete a bar on the strength of changelog
# prose -- `no-record` is a stop, not a delete-list, and the same applies here.
T.append(dot_bars("CM Time Target", "CM Time",
                  [("Accelerated Recovery", (0.50, 0.90, 0.60), {}),
                   ("Protection", (0.55, 0.75, 1.00), {}),
                   ("Renewal", (0.45, 0.90, 0.55), {}),
                   ("Resilience", (0.95, 0.85, 0.45), {}),
                   ("Oblivion", (0.90, 0.35, 0.35), {})],
                  y=Y_TARGET, helpful=True, refresh_at=4))
_y_T = emit_bottom_block("Time", "time", T,
                         [("Sands of Time", (0.95, 0.8, 0.45)),
                          ("Endless Sands", (1.0, 0.9, 0.6)),
                          ("Ripple in Time", (0.6, 0.85, 1.0)),
                          ("Cadence of Time", (0.8, 0.7, 1.0)),
                          ("Shield of the Ages", (0.6, 0.85, 1.0)),
                          ("Fabric of Time", (0.9, 0.75, 1.0))],
                         SHORT_ENTRIES)
longterm_band("Time", T, _y_T)
add(spec_group("CM Time", T))


# ------------------------------------------------- Infinite Clone -> Rewind
# One slot, two faces. Casting Infinite Clone (804492, 3 min) leaves a 10 sec
# player aura (704154) during which Rewind (801294) returns you to the clone's
# health, mana and position. You almost always want to spend it before it
# lapses, so the icon becomes Rewind for those ten seconds and its glow
# escalates as the window closes.
#
# Same mechanism as the Ripple variants and the shared bands: both displays
# live in the row, exactly one is ever loaded-and-showing, so the row lays out
# around whichever it is. `disjunctive` must be ALL (its default) or the
# always-true cooldown trigger shows both at once.
CLONE_WINDOW = 704154          # the 10 sec "Infinite Clone" player aura


def _subglow_index(display):
    """1-based index of the glow subregion, for a `sub.N.glow` property."""
    subs = display.get("subRegions") or []
    subs = list(subs.values()) if isinstance(subs, dict) else list(subs)
    for i, sub in enumerate(subs, 1):
        if isinstance(sub, dict) and sub.get("type") == "subglow":
            return i
    return None


def pair_clone_rewind():
    """Infinite Clone and Rewind share ONE slot.

    Casting Infinite Clone (804492, 3 min) leaves a 10 sec player aura
    (704154). While it is up, Rewind (801294) returns you to the clone's
    health, mana and position -- and you almost always want to spend it before
    it lapses, so the icon becomes Rewind for those ten seconds and the glow
    escalates as the window closes.

    Exactly one of the two is ever loaded-and-showing, so the row lays out
    around whichever it is.

    ⚠️ Finds them by NAME, not by band. An earlier version filtered on
    `" Offense " in id`; when Rewind was recategorised as defensive both
    displays moved to the Utility band, this matched nothing, and the pairing
    silently vanished -- no window trigger, no glow, two unrelated icons. The
    assert at the end is why that cannot repeat: a pairing that matches
    nothing is a build failure, not a quiet no-op.
    """
    CLONE_WINDOW = 704154            # the 10 sec "Infinite Clone" player aura
    found = {}
    for c in list(children):
        for suffix in (" Infinite Clone", " Rewind"):
            if not c["id"].endswith(suffix):
                continue
            is_rewind = suffix == " Rewind"
            trs = triggers_of(c)
            trs.append(B.aura_trigger([str(CLONE_WINDOW)], exact_id=True)
                       if is_rewind
                       else B.aura_trigger([str(CLONE_WINDOW)], exact_id=True,
                                           show_on="showOnMissing"))
            c["triggers"] = B._trigger_wrap(trs)
            c["triggers"].pop("disjunctive", None)   # ALL: cooldown AND window
            NEEDS_ALL.add(c["id"])
            found.setdefault(c["id"].rsplit(suffix, 1)[0], set()).add(suffix)
            if not is_rewind:
                continue
            # Escalate on the WINDOW's remaining time, not Rewind's own
            # cooldown -- the thing you can lose is the window. On an aura2
            # trigger `expirationTime` is seconds remaining and needs no GCD
            # guard; that guard is only for spell-cooldown triggers.
            gi = _subglow_index(c)
            if gi is None:
                continue
            n = len(trs)
            conds = list((c.get("conditions") or {}).values()) \
                if isinstance(c.get("conditions"), dict) else list(c.get("conditions") or [])
            for secs, colour in ((5, (1.0, 0.85, 0.35, 1.0)),
                                 (3, (1.0, 0.30, 0.20, 1.0))):
                conds.append(B.cond(
                    B.T({"trigger": n, "variable": "expirationTime",
                         "op": "<=", "value": str(secs)}),
                    [B.change(f"sub.{gi}.glow", True),
                     B.change(f"sub.{gi}.glowColor", B.rgba(*colour))]))
            c["conditions"] = B.arr(conds)

    paired = [k for k, v in found.items() if len(v) == 2]
    if not paired:
        raise SystemExit(
            "pair_clone_rewind matched no Infinite Clone / Rewind pair. They "
            "must share a band -- check their Role in the ability inventory.")
    for band, halves in found.items():
        if len(halves) != 2:
            raise SystemExit(
                f"{band}: found only {sorted(halves)}. Infinite Clone and "
                f"Rewind share one slot, so they need the SAME role in "
                f"resources/abilities-{CLS.slug}.md.")
    print(f"  clone/rewind paired in {len(paired)} band(s)")


pair_clone_rewind()
# Offense and Utility are deliberately NOT merged.
#
# A merged band has ONE yOffset, so the band under it must clear the spec that
# wraps DEEPEST -- Infinite's 17 offensive cooldowns at three rows. Every
# shallower spec then carries the unused rows as dead vertical space, which in
# game is a 30px hole under the row and another under the next one. Time and
# Artificer both wrap at two.
#
# Un-merging costs displays (a shared cooldown gets one copy per spec instead
# of one total) and hands back part of the final16 saving. It buys a ladder
# that is tight on EVERY spec, which is the whole point of a fixed layout.
#
# Main and Buffs stay merged: Main is one row on every spec so there is nothing
# to reserve, and Buffs is active-only, so its stored length never becomes
# vertical space.
MERGE_BANDS = ("Main", "Buffs")
W.configure(merge_bands=MERGE_BANDS)


merge_bands()

# ---------------------------------------------------------------- leaf gating
# A plain `group`'s triggers/conditions/load are INERT: WeakAuras skips
# load-scanning for any aura with controlledChildren, and never registers a
# group with the trigger system. Gating on the group therefore did nothing and
# all three spec groups rendered at once, stacked at identical coordinates --
# the overlapping duplication seen in game. Every leaf carries its own gate.
#
# Verified against three working community packs: none of their 31 groups
# carries a meaningful trigger; they all gate at the leaf.
# Spell that only this spec knows. Used as the leaf load condition.
# One spell only that spec knows, for load.use_spellknown. Chosen as the
# lowest-level spec-unique ability in each tree, because a levelling character
# who has not learned it yet loses the whole spec's displays -- the gate holds
# ONE id and a wrong or late one fails silently.
SPEC_KNOWN = {
    "Artificer": 804503,   # Shatter Echo, L11
    "Infinite": 806316,    # Maw of Chaos, L10
    "Time": 806296,        # Ripple, L11
}
W.configure(needs_all=NEEDS_ALL, spec_known=SPEC_KNOWN)


_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()
W.chain_ladder()
# Ripple is the one display whose art is a build-time choice rather than an
# override, so it has to be named here.
W.settle_icon_source(NEEDS_MANUAL_ICON)
if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    W.finish((_GATED, _ANY, _CLASSED))
