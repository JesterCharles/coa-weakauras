"""Build the `Reaper [CoA]` WeakAura pack for Ascension Conquest of Azeroth.

Written as CONTENT over the shared engine -- the build_chronomancer.py shape,
no convergence flags. Layout follows notes/layout-standard.md.

        [ on TARGET: your DoTs / debuffs ]            <- band 2, active-only
        [ on me: procs, running CDs, buffs ]          <- band 3, active-only
              [  MAIN ROW - flush         ]           <- band 4
              [  resource envelope        ]           <- band 5, fixed height
              [ offensive cooldowns       ]           <- band 6, wraps at 7
              [ defensive + utility       ]           <- band 7, wraps at 7
              [ long-term buffs           ]           <- band 8, active-only

Class shape (notes/requirements-reaper.md):

  * THE SOUL CASCADE. Every spec banks the same three-layer resource: Soul
    Fragments (805077, "At 5 stacks, generate a Reaped Soul") fill Reaped
    Souls (500363, "At 3 stacks you are granted Soul Infusion"), and Soul
    Infusion (803031) gates the big spenders. The envelope renders Reaped
    Souls as a 3-cell stack_bar with the FRAGMENT count fused into the cell
    being filled -- the Pyromancer heat-in-ember pattern -- and the Runic
    Power bar underneath. Identical on every spec, so no height variance.

  * RUNIC POWER is the spent resource on all three specs (Sidekick, all three
    Resource paragraphs). Rendered via power type 6, the Wrath runic-power
    slot; whether the CoA client exposes it for REAPER is requirements §6.

  * TRANSFORM FACES. Two talents replace a main-row button with a different
    spell id: Decimation turns every 6th Reap into Decimate (500523) on
    domination, Redshade turns Reap into Thresh (505170) on harvest. The Reap
    display carries a native ["Spell Known"] trigger on the REPLACEMENT id --
    this fork resolves no spell overrides (weakauras-data-model.md §6.3), so
    the granted spell is the only signal -- and a condition swaps the icon's
    face while it fires. One display, so the row stays five slots wide and
    untalented characters see plain Reap. See transform_face().

  * NO ALERT BAND. Reaper has no pre-pull imbue/stance kit whose absence is
    silent throughput loss; the one candidate (Death's Presence) rides on a
    passive whose aura visibility is unproven, and an alert keyed on a hidden
    aura would be permanently on screen -- §6 defers it to the in-game pass.

  * DOMINATION TANKS (spec-roles.md, Sidekick-sourced). Nothing structural
    changes: its main row is the cited tanking loop, Writhe (the taunt) rides
    the utility row, and its target band carries Withering Touch.

WA_GLOW=1 additionally glows main-row icons the moment they come off cooldown.
"""
import wapack as W

# Release tag. Feeds the uid salt. WeakAuras dedupes imports on uid, so a
# rebuilt pack MUST carry a different salt or the client treats it as
# already-installed and silently keeps the old copy. Bump on any release.
#
# 0.1: first build (draft bar, notes/production-run.md). Roles were assigned by
# an automated pass and cleared in bulk 2026-08-07 -- provenance in the
# buildlog; the hedged rows are listed in requirements §6.
VERSION = "0.1"

# Only real Ascension/3.3.5 icon names -- a missing texture renders as a "?".
FALLBACK = {}
# ONLY deliberate choices belong here: an entry overrides the CLIENT's own art.
#
# Blood Siphon and Red Wake both resolve to ability_revendreth_shaman upstream
# and sit side by side in the Harvest offense row -- the collision the
# duplicate-art check exists to catch. Blood Siphon borrows Blood Fueled's
# blood-tap art: a passive (role ignore) that never renders in any row, so the
# fix cannot introduce a fresh clash. Red Wake keeps the upstream art -- it is
# the AoE wave the icon depicts.
OVERRIDE = {"Blood Siphon": "spell_deathknight_bloodtap"}

# Not tooltip-verified, but read off db.ascension.gg tooltips where the digest
# linked a COMPONENT rather than the castable. Each replacement's tooltip was
# read and matches the skillbook text (requirements §0).
CROSSCHECK = {
    # 707459 is rank Passive with duration -1 -- the passive rider. 800930
    # carries the real player tooltip: instant, 20 sec cooldown, "leap forward
    # ... swinging your scythe in an arc", in the 8009xx block.
    "Cull": 800930,
    # db.exil.es's 300979 is rank "Damage" -- the Apparition damage component.
    # 804722 carries the castable tooltip ("Mark a 10 yd area around you as a
    # Gravesite for 15 sec ... sends an Apparition after them"); 567568 is an
    # older resistance-shred variant of the same name.
    "Gravesite": 804722,
    # 570097 is rank "Aura" -- the enrage aura. 803030 is advType=Ability in
    # the class tree (matches talents-reaper.json) with the full tooltip:
    # 1 min cooldown, self-damage then +20% damage for 15 sec.
    "Masochistic Rage": 803030,
}

# Identity, data and the entire build vocabulary come from wapack. init() runs
# BEFORE the star import because it is what gives the unqualified names below
# their values. No convergence flags: this class starts on every default.
#
# CD_PER_ROW derives from the NARROWEST main row. All three specs render five
# main icons: row_w(5) = 228px and 28w - 2 <= 1.2 * 228 allows 9. 7 is taken:
# the constraint is that a cooldown row must not OVERRUN the bar, a narrower
# row is never the thing that looks broken, and 7 keeps soul's 15 offensive
# cooldowns as an even 5+5+5.
CLS = W.init("reaper", version=VERSION, prefix="RP", cd_per_row=7,
             override=OVERRIDE, fallback=FALLBACK, crosscheck=CROSSCHECK)

from wapack import *          # noqa: E402,F401,F403  -- deliberate, see above

# ---- the resource system ---------------------------------------------------
# Ids and stack counts from db.ascension tooltips (source precedence: they
# outrank the Sidekick soul page's "3 fragments" claim -- requirements §6).
REAPED_SOUL = 500363          # "At 3 stacks you are granted Soul Infusion."
SOUL_FRAGMENT = 805077        # "At 5 stacks, generate a Reaped Soul."
SOUL_INFUSION = 803031
SOUL_CELLS = 3

# Abilities that hold charges rather than a plain cooldown, from tooltips:
# "2 Charges, 60 sec recharge" (Veilwalk), "2 Charges, 40 sec recharge"
# (Ghostly Weapon), "3 Charges, 30 sec recharge" (Haunt), "2 Charges, 15 sec
# recharge" (Wraith Claw).
CHARGES = {"Veilwalk": 2, "Ghostly Weapon": 2, "Haunt": 3, "Wraith Claw": 2}

# When one of these buffs is up, the ABILITY it empowers glows. Every entry
# here keys off Soul Infusion (803031): the spenders whose tooltips carry
# "Consumes ... Soul Infusion" or "Requires Soul Infusion", plus Soulspear,
# which turns instant under it without consuming it. The cooldown swipe says
# "when can I press"; it cannot say "the cascade is charged" -- that is the
# thing you actually read mid-fight on this class.
PROC_GLOW = {
    "Reliquary of the Lost": ["Soul Infusion"],
    "Soulslam": ["Soul Infusion"],
    "Spectral Scythe": ["Soul Infusion"],
    "Tormented Souls": ["Soul Infusion"],
    "Blood Siphon": ["Soul Infusion"],
    "Soulspear": ["Soul Infusion"],
}
PROC_STACKS = set()

# Offense-row abilities that apply no self-buff worth a second icon in the
# "on me" row. buff_group only renders what is up, so a wrongly-kept name
# costs nothing but a display that never shows; a wrongly-dropped one loses a
# real cue.
NO_BUFF = {
    "Bane", "Blood Siphon", "Corporeal Flay", "Gravesite", "Murder",
    "Red Wake", "Reliquary of the Lost", "Shrieker", "Shudder Scythe",
    "Sinister Litany", "Soul Tap", "Soulrend", "Soulrot", "Soulslam",
    "Soulspear", "Spectral Scythe", "Withering Touch", "Wraithblade",
}

# Displays whose extra trigger is a GATE, not an alternative sighting: they
# must keep `disjunctive` at its "all" default. See apply_leaf_gates().
NEEDS_ALL = set()

W.configure(charges=CHARGES, proc_glow=PROC_GLOW, proc_stacks=PROC_STACKS,
            no_buff=NO_BUFF)


# ================================================================== 1. CORE
# Reaper has NO class-wide alert (module docstring; requirements §5). An empty
# Core still carries the root group so the pack shape matches every other
# class.
CORE = []
add(B.group("RP Core", ROOT, CORE, x=0, y=0))


# ---- long-term buffs -------------------------------------------------------
# DATA, not displays: the band is emitted once per spec by longterm_band(),
# anchored under that spec's own utility row, and reads the inventory rather
# than hand-listing names. Three families:
#
#   Rites      ally/raid stat rites (Perseverance on dom, Power / Resolve on
#              harvest) -- the blessing shape, checked once per pull.
#   Toggles    Soulless (harvest: -healing for -damage/+damage), Dark Pact
#              (soul: +AP with downsides) -- build-defining persistent states.
#   Links      Reaper's Pact (dom, 10 min ally damage-link), Death's Presence
#              (soul party damage aura -- active-only, so if its aura is a
#              hidden passive the icon simply never renders; §6).
LONGTERM_COL = {
    "Rite": (0.55, 0.75, 1.00),
    "Pact": (0.95, 0.60, 0.30),
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
    `RP <Spec>` with that spec, and apply_leaf_gates puts the spec's signature
    spell on it. The levelling tradeoff is mild -- the three signature spells
    are L4 / L1 / L8 (see SPEC_KNOWN).
    """
    band = f"RP {spec_name} Longterm"
    out = []
    for name in longterm_for(spec_key):
        col = _family_col(name)
        sid_ = ABILITIES[name]["id"]
        out.append(add(B.icon(
            f"RP {spec_name} Longterm {name}", band,
            # By id AND name: the Rites come in plain and Greater pairs whose
            # names are prefixes of each other; an id match settles it.
            [B.aura_trigger([str(sid_), name], own_only=False)],
            ic(name), size=SZ_SMALL,
            subregions=[B.sub_text("%p", size=9, anchor="INNER_BOTTOM",
                                   color=col + (1.0,)),
                        thin()])))
    if not out:
        return
    add(B.dynamicgroup(band, f"RP {spec_name}", out, x=0, y=y - LONG_GAP,
                       grow="HORIZONTAL", space=GAP))
    bands.append(band)


# Class-wide short buffs, merged per spec into that spec's "what is up right
# now" row.
#
#   Soul Infusion   the cascade's payoff state -- the icon IS "spenders are
#                   armed", the same fact the proc glows repeat per button.
#   Ghost           Sinister Litany's next-hit damage buff (talent rider).
#   Tormented Souls the DR-charge stacks being eaten by hits.
#   Jailer's Bargain the 30%-max-HP shield while it holds.
SHORT_ENTRIES = [
    ("Soul Infusion", (0.75, 0.35, 0.95), {}),
    ("Ghost", (0.70, 0.80, 1.00), {}),
    ("Tormented Souls", (0.60, 0.85, 1.00), {}),
    ("Jailer's Bargain", (0.95, 0.75, 0.30), {}),
]


def envelope(spec_name, bands):
    """Reaped Souls + Runic Power. Identical on all three specs.

    Reaped Souls sit NEAREST the main row because the bank-or-spend call is
    the spec's real resource decision (all three Sidekick Resource
    paragraphs); Runic Power is the slower pool underneath.

    The FRAGMENT count rides inside the cell being filled (feeder): at full
    Reaped Souls the number turns warn-colour at 3 fragments and danger at 4,
    the window in which the next mint would be wasted -- requirements §6
    carries the overcap question.
    """
    W.stack_bar(f"RP {spec_name} Souls", f"RP {spec_name}", REAPED_SOUL,
                SOUL_CELLS, (0.55, 0.85, 1.00), Y_BAR,
                B.health_trigger("player"), row_w(5), bands, h=14,
                feeder=(SOUL_FRAGMENT, 3, 4))
    bands.append(rp_bar(f"RP {spec_name} Runic Power", f"RP {spec_name}",
                        Y_SEG, w=row_w(5)))


def rp_bar(gid, parent, y, w):
    """Runic Power is power type 6 on a 3.3.5 client. mana_bar hardcodes 0,
    so this is the same aurabar with the right powertype -- the one
    class-content divergence the resource envelope needs. §6: confirm the CoA
    client exposes type 6 for REAPER."""
    add(B.aurabar(gid, parent, [B.power_trigger("player", 6)],
                  x=0, y=y, w=w, h=BAR_H_STACKED,
                  color=(0.35, 0.75, 0.95, 1.0),
                  subregions=[
                      B.sub_text("%p", size=10, anchor="INNER_RIGHT", x=-4,
                                 justify="RIGHT"),
                  ]))
    return gid


# Displays whose icon is chosen by a CONDITION at runtime. They need
# iconSource = 0 or SetIcon has no effect -- state.icon wins and the swap is
# invisible (the Ripple lesson). Registry so settle_icon_source cannot quietly
# reset them.
NEEDS_MANUAL_ICON = set()


def transform_face(d, rep_name, rep_id):
    """Give a main-row button its talent-replacement FACE -- the Ripple
    pattern, one display rather than a sixth slot.

    Decimation turns every 6th Reap into Decimate, Redshade turns Reap into
    Thresh. This fork resolves no spell overrides (`effectiveSpellId` is the
    id you typed, weakauras-data-model.md §6.3), so the signal that the button
    has changed is the REPLACEMENT spell being KNOWN -- a native
    ["Spell Known"] trigger on its NUMERIC id (Prototypes.lua:8271 turns a
    string into spell 0 silently). While it fires, a condition swaps
    `displayIcon` to the replacement's art, so the Reap slot reads as the
    thing you are actually about to press.

    ONE display, not two: rowwidths.py collapses variants by tracked spell,
    so a second display tracking a different id would count the row 6 wide
    against a bar locked to 5 -- and 6 icons at 274px over a 228px bar is
    1.20x, the exact overrun the check exists to refuse.

    `disjunctive` must be "any": trigger 1 alone keeps the button on screen
    untalented -- the conditions, not the trigger logic, pick the face.
    ⚠️ iconSource = 0 or the swap is invisible: UpdateIcon() prefers
    state.icon at -1 and the cooldown trigger supplies Reap's art every frame.
    """
    d["iconSource"] = 0
    NEEDS_MANUAL_ICON.add(d["id"])
    trs = triggers_of(d)
    trs.append(B.spell_known_trigger(rep_id))
    conds = list((d.get("conditions") or {}).values()) \
        if isinstance(d.get("conditions"), dict) else list(d.get("conditions") or [])
    conds.append(B.cond(
        B.T({"trigger": len(trs), "variable": "show", "value": 1}),
        [B.change("displayIcon", ic(rep_name))]))
    d["triggers"] = B._trigger_wrap(trs)
    d["triggers"]["disjunctive"] = "any"
    d["conditions"] = B.arr(conds)
    return d


def main_row(spec_name, spec_key, names, transform=None):
    """The main rotation row, hand-built so a transform face can be wired.

    `transform` is (base_name, replacement_name, replacement_id).
    """
    band = f"RP {spec_name} Main"
    ids = []
    for n in names:
        d = cd_icon(f"{band} {n}", band, n, SZ_MAIN, spec=spec_key)
        if transform and n == transform[0]:
            transform_face(d, transform[1], transform[2])
        ids.append(add(d))
    add(B.dynamicgroup(band, f"RP {spec_name}", ids, x=0, y=Y_MAIN,
                       grow="HORIZONTAL", space=GAP))
    return band


# ============================================================= 2. DOMINATION
# THE TANK. Row order is the ROTATION, from the cited Sidekick text: "you
# cycle Reap, whose every 6th cast turns into a Decimate via Decimation, the
# cone Dreadwake, and the AoE Requiem", with Soul Strike as the Runic Power
# spender and Deathwind laid down for sustain -- the numbered solo rotation
# runs Reap -> Soul Strike -> Dreadwake -> Requiem -> Deathwind.
D = []
D.append(main_row("Domination", "domination",
                  ["Reap", "Soul Strike", "Dreadwake", "Requiem", "Deathwind"],
                  transform=("Reap", "Decimate", 500523)))
envelope("Domination", D)
# Your debuffs on the target: the 60s armor/magic shred you maintain.
D.append(dot_bars("RP Domination Target", "RP Domination",
                  [("Withering Touch", (0.75, 0.55, 1.00), {})],
                  y=Y_TARGET, refresh_at=8))
_y_D = emit_bottom_block("Domination", "domination", D,
                         [("Eater of Souls", (0.55, 0.95, 0.55)),
                          ("Bolstered Form", (0.60, 0.85, 1.00)),
                          ("Dark Deal", (0.95, 0.45, 0.75)),
                          ("Counterscythe", (0.80, 0.70, 0.50)),
                          # TE-tree parry proc; no inventory row (talent), the
                          # aura matches by name and never shows untalented.
                          ("Soul Knight", (0.95, 0.85, 0.45)),
                          ("Spectral Warden", (0.70, 0.80, 1.00))],
                         SHORT_ENTRIES)
longterm_band("Domination", "domination", D, _y_D)
add(spec_group("RP Domination", D))


# ================================================================ 3. HARVEST
# Leech melee: Harvester turns 20% of all damage into healing. Row order is
# the cited numbered rotation: Crow's Harvest opener -> Doomrend (anti-heal
# shield + bleed) -> Reap filler -> Murder (free fragments, Ruin) -> Slaughter
# the moment a target drops below 35%. Redshade's Thresh shares the Reap slot.
H = []
H.append(main_row("Harvest", "harvest",
                  ["Crow's Harvest", "Doomrend", "Reap", "Murder",
                   "Slaughter"],
                  transform=("Reap", "Thresh", 505170)))
envelope("Harvest", H)
# The anti-heal shield and the rolling bleeds are the spec's tracked output.
# Darkrend Scythe / Ruin / Blood Frenzy are applied BY passives and burst
# windows, so their on-target aura may not share the passive's id -- match by
# name as well (the dot_bars by_name path).
H.append(dot_bars("RP Harvest Target", "RP Harvest",
                  [("Doomrend", (0.90, 0.35, 0.85), {}),
                   ("Darkrend Scythe", (0.85, 0.45, 0.35), {"by_name": True}),
                   ("Ruin", (0.70, 0.60, 1.00), {"by_name": True}),
                   ("Blood Frenzy", (1.00, 0.55, 0.20), {"by_name": True})],
                  y=Y_TARGET, refresh_at=4))
_y_H = emit_bottom_block("Harvest", "harvest", H,
                         [("Crimson Thirst", (0.95, 0.35, 0.35)),
                          ("Extinction", (0.90, 0.60, 0.20)),
                          ("Souls for the Slaughter", (0.75, 0.55, 1.00)),
                          ("Painmail", (0.80, 0.70, 0.50)),
                          ("Harvest Time", (1.00, 0.85, 0.40))],
                         SHORT_ENTRIES)
longterm_band("Harvest", "harvest", H, _y_H)
add(spec_group("RP Harvest", H))


# =================================================================== 4. SOUL
# Fragment-cascade melee. Row order is the cited rotation: Deathchaser opener
# (repeating Shadowfrost, RP generator) -> Wraithblade (hardest hit, +3 Reaped
# Souls) -> Dirge (main sustained button, 2 fragments) -> Reap filler ->
# Reliquary of the Lost whenever Soul Infusion is up.
S = []
S.append(cd_group("RP Soul Main", "RP Soul",
                  ["Deathchaser", "Wraithblade", "Dirge", "Reap",
                   "Reliquary of the Lost"],
                  y=Y_MAIN, size=SZ_MAIN, glow=GLOW, text_size=14,
                  spec="soul"))
envelope("Soul", S)
# The spec's maintained enemy state. Weakened Soul (803433) is applied by the
# L10 passive, so its aura id is not the passive's -- by name.
S.append(dot_bars("RP Soul Target", "RP Soul",
                  [("Deathchaser", (0.60, 0.75, 0.95), {}),
                   ("Soulrend", (0.85, 0.45, 0.35), {}),
                   ("Soulrot", (0.70, 0.60, 1.00), {}),
                   ("Weakened Soul", (0.90, 0.35, 0.85), {"by_name": True}),
                   ("Withering Touch", (0.75, 0.55, 1.00), {})],
                  y=Y_TARGET, refresh_at=4))
_y_S = emit_bottom_block("Soul", "soul", S,
                         [("Fatesealer", (0.95, 0.85, 0.45)),
                          ("Purgatory", (0.75, 0.35, 0.95)),
                          ("Endbringer", (0.90, 0.35, 0.35)),
                          ("Ghostly Weapon", (0.55, 0.85, 1.00))],
                         SHORT_ENTRIES)
longterm_band("Soul", "soul", S, _y_S)
add(spec_group("RP Soul", S))


W.configure(merge_bands=MERGE_BANDS)
merge_bands()

# One spell unique to each spec, for load.use_spellknown. Picked as the LOWEST
# gateable spec-unique id -- gateable meaning spell-meta says IsSpellKnown can
# be trusted with it, which rules out every ranked spell, every component and
# the three L10 Specialization passives (92145/6/7). All three are early
# (L4 / L1 / L8), so a levelling character loses almost nothing to the gate.
SPEC_KNOWN = {
    "Domination": 561289,   # Soul Capture, L4
    "Harvest": 807234,      # Wraith Claw, L1
    "Soul": 803989,         # Soul Shock, L8
}
W.configure(needs_all=NEEDS_ALL, spec_known=SPEC_KNOWN)

_GATED, _ANY, _CLASSED = apply_leaf_gates()
assert_gated()

W.chain_ladder()
# The two transform faces are the displays whose art is a runtime choice, so
# their iconSource=0 must survive the blanket pass.
W.settle_icon_source(NEEDS_MANUAL_ICON)
if SPEC_ONLY:
    restrict_to_spec()


if __name__ == "__main__":
    W.finish((_GATED, _ANY, _CLASSED))
