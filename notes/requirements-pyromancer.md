---
title: Pyromancer — class pack requirements (Phase 0)
date: 2026-08-06
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, pyromancer, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[sidekick-pyromancer-incineration]]"
  - "[[sidekick-pyromancer-flameweaving]]"
  - "[[sidekick-pyromancer-draconic]]"
---

# Pyromancer — requirements

Class **24**, token `PYROMANCER`, specs **Incineration** (damage),
**Flameweaving** (healing), **Draconic** (damage). Current pack is **v0.1,
unverified, never imported**.

Research source for everything below unless stated: the three Sidekick spec
pages, scraped 2026-08-06 and committed to
`resources/sidekick-pyromancer-<spec>.md`. **These did not exist before this
pass** — Pyromancer was built with no mechanics source at all, which is the
root of most of what follows.

Cross-database verdicts are from `?spell=<id>&power` on db.ascension.gg, run
against every ability named in a rotation (40 asked).

## −1. Changelog — 11 entries, and one of them invalidated this document

`changelog_watch.py --class pyromancer`, newest entry **2026/08/06**. This was
run AFTER the first Phase 0 pass rather than before it, which is the mistake the
process now forbids — the Sidekick pages had already been scraped and believed.

| Entry (2026/07/31) | Category | Where it lands |
|---|---|---|
| **"Phoenix Egg is now permanent, up from 1 minute, but has a cast time to resummon."** | duration | **§3 — rewritten below.** Sidekick still says "for 1 minute" |
| **"Draconic Invocation is now baseline, learned from the trainer at level 24."** | now baseline | §2/§4 — it is not a talent; the main-row slot it was given is *more* correct, and it needs no talent gate |
| **"Inferno has been reworked"** — 50% chance on direct healing crits to apply Inferno; heals 3 nearby allies/sec for 5s, then a raid heal at expiry; 5s ICD | reworked | §1 — a **Flameweaving proc worth tracking**, and the 5s ICD is a real "can it even fire" question |
| "Phoenix Dive now hits up to 10 targets" + coefficient double-apply fixed | numbers | none |
| Volcanic Shell Rank 1-5 absorb increases | numbers | none |
| "Pyroclasm damage now obeys PVP mods properly" | numbers | none |
| "Fixed a bug where Inferno was not contributing … in the combat log" | bug | none |

⚠️ **Rotation citations for Pyromancer are STALE** by `citations.py`'s own
measure — they were imported 2026-08-06 from pages that predate the 07/31
rework. Re-import after the next Sidekick refresh.

**Not `--accept`ed.** The Inferno rework is not yet built.

**Status after the first implementation pass (v0.2).** Everything that did not
depend on an in-game unknown is built; `tests/run.py` is fully green for the
first time. What is DONE is marked ✅ inline. What is left is §6, and all of it
needs the client, not more research — `tools/build_probe.py pyromancer` was
written to answer it in one trip.

---

## 0. Ability surface — both databases

39 of 40 rotation abilities return `record` on both databases. One does not:

| Ability | ID | Verdict | Consequence |
|---|---|---|---|
| **Stoke** | 803952 | **`no-record` on db.ascension.gg** | ⚠️ currently on the **Flameweaving main row** |

`Stoke` is a **name collision**, and the collision is the answer:

- db.exil.es 803952 — *"Instantly deals 89 Fire Damage… Adds 10 sec to the
  duration of active Ignite and Blaze"*, 10s CD, level 17. A castable button.
- Sidekick's **Flameweaving** kit lists **`Stoke T`** — the `T` marks a
  **talent** — *"Critical strikes with Ignite and Infernus now extend their…"*.
  A passive.

So the thing the healing spec actually has is a passive, and the castable
version is the one the second database has never heard of. **Stoke must come
off the Flameweaving main row.** It is also one of the ten rows
`class-pack-process.md` already flags as bulk-cleared without a human read —
the flag was right.

- [x] rotation abilities cross-checked (40)
- [ ] **remaining 176 inventory rows still unchecked** — the full sweep is
      outstanding and is a blocker for shipping, not for planning
- [ ] `Kael's Command` (680375) carries `TESTING SPELL` in its Rank column and
      still renders. Confirm it is live before it ships.

---

## 1. Mandatory buffs

**Class-wide.** All three specs run the same two-layer economy — Sidekick's
header on every page reads `Resource: Mana + Breath Charges`, and the body
describes a **Heat → Ember** builder-spender on top of mana.

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| **Heat / Ember** | class economy | Ember is the spender currency; every spec's payoff is an Ember dump | ✅ already built — `stack_bar` with a Heat feeder |
| **Breath Charges** | **Draconic**, not class-wide | Sidekick's Draconic spec text is the only thing that says what they do: "build Breath Charges to **unleash your breath weapon**". The class header saying "Mana, Breath Charges" reads class-wide and the spec text does not support it | ❌ **not represented anywhere, and not buildable yet** — see §6.3 |
| **Flamecasting** | proc, all specs | stacking haste/crit proc, explicitly "functionally a Hot-Streak" — the thing you bank spenders for | ❌ missing |
| **Fired Up!** (704823) | Incineration proc | makes Ember spenders **instant** — a must-press window | ❌ missing |
| **Legacy of Deathwing** (520823) | Draconic proc | resets Destroyer's Maw + Firefall; next one is empowered | ✅ in the Draconic proc row |
| **Aspect's Blessing** (802168) | Draconic CD | next Echo of Nozdormu / Flames of Neltharion is a guaranteed crit | ❌ missing |
| **Draconic Aspect** (92128) | Draconic, L30 | explicit **pre-pull** requirement | ❌ verify it is in longterm |
| **Inner Flame** (301974) | Draconic, party crit | explicit **pre-pull** requirement | ❌ verify it is in longterm |
| **Spirit of the Phoenix** (92126) | Flameweaving, L10 | cheat-death; while transformed **spells cost no mana** — a total rotation change | ❌ `ignore`. See §3 |
| **Ashes of the Phoenix** (573230) | Flameweaving | 10-minute ICD saying the cheat-death is **gone** | ❌ missing |
| **Dormant** (800128) | Flameweaving | +150% mana regen while the Phoenix is dormant | ✅ in the proc row |

**Missing-buff alerts.** The pack has a `NO SKIN` alert. Add: `NO ASPECT` for
Draconic (pre-pull, stated twice) and `NO PHOENIX` for Flameweaving (§3).

---

## 2. Talent-driven rotation changes

**One outright transform, and it is the Runemaster failure again:**

| Talent | What changes | Rotation impact | WA adaptation |
|---|---|---|---|
| **Echo of Nozdormu** (802174) | *"**Transforms your Explode into Echo of Nozdormu**"* | Draconic's single-target Ember spender | ⚠️ see below |
| Legacy of Deathwing | Ember spend → 30% reset of Maw + Firefall, grants a buff | keep both on CD to fish resets | `PROC_GLOW` |
| Aspect's Blessing | next spender guaranteed crit, 15s | the burst window | `PROC_GLOW` |
| Earthwarder | next Flare Bolt instant, 8s | filler becomes mobile | `PROC_GLOW` |
| Flames of Fate | Aspect's Blessing affects 2 more casts, CD doubled | changes burst cadence | build-defining; layout unaffected |
| Invocation of Flames | Draconic Invocation also grants 5 Flamecasting | stacks the haste proc | feeds Flamecasting tracking |
| Burning Crescendo / Eternal Flame | Phoenix Egg ticks faster / lower CD | Phoenix uptime | §3 |
| Offering of Executus | Phoenix death/expiry heals 30yd | makes expiry a *payoff*, not just a loss | §3 |
| Invigoration | Phoenix healing generates 5 Heat | ties the pet to the resource economy | §3 |
| Lucifron's Rage | Phoenix healing buffs allies' Fire damage | raid-facing pet value | §3 |

### The Explode → Echo of Nozdormu problem

`Explode` is **800792**; `Echo of Nozdormu` is **802174** — two different
spells, and the talent swaps one for the other. The current builder hardcodes
`Echo of Nozdormu` on the Draconic main row, which means:

- talented → correct
- **untalented → the row shows an ability the player does not have, and the
  Explode they *do* have is nowhere**

This is the Zenith bug with the polarity flipped: Runemaster tracked only the
base, Pyromancer tracks only the replacement. Both are half-right.

**Requirement:** the Draconic main row must read correctly in **both** states.
Approach, per `class-pack-process.md`: keep the base and put a `["Spell Known"]`
trigger on the replacement, so the icon follows whichever the player has.
Record the pair in `tools/in-game-verified.json` under `variants` once a tooltip
confirms it.

⚠️ **UNKNOWN — does the transform also change the spell on Incineration?**
`Explode` is on Incineration's main row too. If an Incineration player can take
this talent the same fix is needed there. Settle in game.

---

## 3. Pets — YES. A Phoenix, on Flameweaving, and it is load-bearing

The inventory bins most of the Phoenix cluster to `ignore`. That is wrong here.

**Phoenix Egg** (707110) — Sidekick: *"Summon a Phoenix for 1 minute at the
target location that heals nearby party members every 5 sec. You may only have
1 Phoenix active at a time."* Talent, requires 21 points (level 50).

⚠️ **Sidekick is STALE on the duration.** Changelog 2026/07/31:

    [pyromancer] Phoenix Egg is now permanent, up from 1 minute,
                 but has a cast time to resummon.

**The Phoenix is permanent.** That changes the requirement substantially:

- ❌ **No expiry timer.** A 60s countdown would be wrong, and would have been
  the first thing built.
- ✅ **Presence tracking still matters, and arguably matters more.** A permanent
  pet is one you stop thinking about — and it can still die, at which point two
  cooldowns go dead and the *resummon now has a cast time*, so noticing late is
  more expensive than it used to be.
- The cue is therefore **binary presence + a `NO PHOENIX` alert**, not a
  duration bar. `Offering of Executus` (heals 30yd when it dies or expires)
  means death is a real event with a payoff, not just a loss.

**Two abilities are dead buttons without an active Phoenix:**

| Ability | ID | Text |
|---|---|---|
| **Phoenix Dive** | 706854 | *"**Command your Phoenix** to swoop to the target ally and shield allies in their path"* — 30s absorb |
| **Kael's Command** | 680375 | *"**Command your Phoenix** to go dormant for 10s. While dormant it radiates healing"* — generates 50 Heat |

Both are currently on the Flameweaving pack with **no indication of whether the
Phoenix exists**. Phoenix Dive is on the main row.

Answers to the template's checklist:

- **Summons a pet?** Yes — temporary, **60 seconds**, **capped at 1 active**.
- **Player-pressed pet abilities?** Yes, two, both cooldown-gated.
- **Applies buffs worth tracking?** Yes — Phoenix Dive's absorb (already in the
  target band), the Dormant window, and the Egg's healing zone.
- **Does absence gate the rotation?** **Yes.** Two cooldowns and the passive
  healing zone all evaporate. This is exactly the "missing weapon imbue" shape
  that earned Runemaster an alert.
- **Pet resource?** No. But **Invigoration** routes pet healing into *your*
  Heat, so the pet feeds the player's economy.

**Requirement — a Phoenix section on Flameweaving:**

| Need | Mechanism |
|---|---|
| **Phoenix present / absent** (not a timer — it is permanent) | the single most important missing display on this spec |
| Phoenix absent while Egg is off CD | `NO PHOENIX` alert, missing-buff shape. Resummon has a cast time, so this wants to fire early |
| Phoenix Dive / Kael's Command unusable without it | desaturate or gate on Phoenix uptime |
| Dormant window (10s) | ✅ already in the proc row |

⚠️ **UNKNOWN — is the Phoenix a real `pet` unit or a ground effect?** "Summon a
Phoenix **at the target location**" reads like a stationary totem/zone, not a
controllable pet. This decides everything: `unit = "pet"` aura triggers and the
`petspell` toggle only work for a real pet unit; a zone needs a player-side
aura or a summon-duration timer instead. **`/rmprobe`-style check, or read
`UnitExists("pet")` with a Phoenix out.** Do not build the tracker until this is
answered — it is the one thing that decides which mechanism is even available.

**Narrowed 2026-08-07 — the totem branch is very likely dead.** Three spells in
this family say "pet" in their own tooltip text, and `Flames of Al'ar` says it
in **both databases, identically**:

| Spell | Id | Tooltip |
|---|---|---|
| Flames of Al'ar | 500202 | "Transforms your **Phoenix Hatchling pet** into a fully empowered Phoenix" |
| Kiss of Al'ar | 704280 | "**The Phoenix** heals an ally target" |
| Phoenix Dive | 706854 | "**Command your Phoenix** to swoop to the target ally" |

Plus `Hatched!` (520734) and `Hatching!` (520687) as egg states. Nothing in the
family uses totem language, and `GetTotemInfo` covers numbered totem slots that
nothing here claims. **So do not build against `["Totem"]`.**

A third, independent corroboration: Sidekick's own class metadata for
Pyromancer lists the class `feature` as **"Phoenix Pet, Spell Combos"** — not a
rotation blurb this time but the structured class record, which is the half of
Sidekick that has a database behind it.

This is still database evidence, not client behaviour, and the two do not agree
about the *word*: the summon tooltip says "at the target location" while the
empower tooltip says "pet". A server can implement a guardian that reads as a
pet in prose and does not occupy the pet unit slot. **The probe question is now
sharper and smaller: does `UnitExists("pet")` return true with a Phoenix out,
and what does `UnitName("pet")` say?** One line of output settles it.

**Also unresolved and worth the same trip: where is the castable Phoenix Egg?**
The 07/31 entry ("now permanent, up from 1 minute, but has a cast time to
resummon") describes a summon with a cast time. `Phoenix Egg` 707110 is not it —
both databases give it as a Heal component with no cost, cooldown or GCD. The
60-second duration the entry replaced is still sitting on `Phoenix` (805800) and
`Phoenix abilities enabler` (681128), so our snapshot predates the patch. No
castable summon appears in either database under any Phoenix name.

**Also reclassify:** `Spirit of the Phoenix` (92126) is `ignore` but is a
*cheat-death that removes all mana costs for 15s*. It belongs in the buff row,
with `Ashes of the Phoenix` (573230, 10-min ICD) as the "it is gone" counter.

---

## 4. Primary damage/healing source and how the main bar reads

Sidekick's own framing, per spec:

| Spec | Primary source | Retail feel | Resource |
|---|---|---|---|
| Incineration | periodic Ignite/Blaze pressure dumped into spenders | Fire Mage (Ignite/Combustion snowball) | Mana + Heat/Ember |
| Flameweaving | **healing** — Kindle/Cinderheart spam + Ember Touch top-offs | Preservation Evoker | Mana + Heat/Ember, Spirit-scaled |
| Draconic | builder-spender, Embers into empowered payoffs | Devastation Evoker | Mana + Heat/Ember |

**Main row vs. researched rotation — every spec is wrong today:**

| Spec | Current main row | Rotation says | Verdict |
|---|---|---|---|
| Incineration | Ignite, Blaze, Wildfire, Lava Shard, Explode, Melt | Ignite/Blaze → **Flare Bolt**/Lava Shard filler → **Pillar of Flame** → Explode → **Flames of Neltharion**/**Pyroclasm** | ❌ missing the **main filler** (Flare Bolt) and both big spenders |
| Flameweaving | Kindle, Cinderheart, Ember Touch, Cleansing Flames, Phoenix Dive, **Stoke** | Kindle/Cinderheart → Ember Touch → Cleansing Flames → Phoenix Dive; **Inferno Barrier**, zones | ❌ `Stoke` is a passive (§0); **Inferno Barrier** missing |
| Draconic | Echo of Nozdormu, Destroyer's Maw, Firefall, **Dragonfire**, Flames of Neltharion, Flare Bolt | Flare Bolt filler → Lava Shard → Maw / Death From Above → **Draconic Invocation** → Echo/Flames spenders → Meteor | ❌ `Dragonfire` unmentioned; **Draconic Invocation** missing; Explode/Echo split unhandled (§2) |

Press order is `controlledChildren` order and is load-bearing — rebuild each row
**from the rotation text**, filler first.

`CD_PER_ROW` must be recomputed from the narrowest final main row. Do not carry
Runemaster's 9.

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | Proof it fires |
|---|---|---|---|
| Ignite / Blaze falling off | the whole spender package scales off periodic count | target band, `refresh_at=4` | ✅ built |
| **Fired Up!** window | Ember spenders stay hard-cast | `PROC_GLOW` | ❌ to build |
| **Flamecasting** stacks | spenders dumped outside the haste window | stack count on the icon | ❌ to build |
| **Legacy of Deathwing** | a free Maw/Firefall reset is wasted | `PROC_GLOW` | ✅ in proc row |
| **Aspect's Blessing** | the guaranteed-crit burst is lost | `PROC_GLOW` | ❌ to build |
| **Phoenix expiry** | **two cooldowns become uncastable** | uptime tracker + `NO PHOENIX` | ❌ to build — §3 |
| Pre-pull Draconic Aspect / Inner Flame | flat throughput loss, silent | `NO ASPECT` alert | ❌ to build |
| Spirit of the Phoenix consumed | your cheat-death is gone for 10 min | ICD debuff tracker | ❌ to build |

**How we prove a cue fires** — the rule from the Runemaster retro: not "it looks
right in the builder". Strongest first: seen in game → a named `tests/run.py`
check → a probe differ. The Explode/Echo split (§2) and the Phoenix tracker
(§3) both need the in-game proof, because both are the silent-failure shape.

---

## 6. Open questions — the in-game checklist

**Import `pyromancer-probe.txt`, get into the state, `/pyprobe`.** It watches
every player buff, whether each watched spell resolves *and* `IsSpellKnown`,
which action slot holds a watched spell and what it currently casts, all four
**totem slots**, `UnitExists("pet")` plus pet buffs, and every power type with a
non-zero max — and reports only what CHANGED. Questions 1, 2, 3, 4 and 5 below
are all answered by one log.

1. **Is the Phoenix a real `pet` unit, or a ground zone?** Decides the entire
   tracking mechanism. `UnitExists("pet")` with a Phoenix out.
2. **Explode ↔ Echo of Nozdormu** — confirm the swap by tooltip; capture both
   ids into `in-game-verified.json` `variants`. Does it apply on Incineration?
3. **Breath Charges** — ⚠️ **BLOCKED, not merely unbuilt.** The whole family is
   on disk and none of it is documented: `Breath Charge` 504373,
   `+1 Breath Charge` 504577, `Breath Charge Delayer` 520373,
   `Breath Charge Remover` 520374, `Breath Charge Exponentifier` 706865 and
   P2 706866, `Breath Charges - Malygos/Nozdormu` 681123. **All seven are
   records on BOTH databases and all seven have a bare tooltip** — no stack
   count, no maximum, no duration, no text. A `stack_bar` needs the aura id
   *and* the maximum, and a guessed maximum draws a bar that is wrong at every
   value, so this is a stop, not a judgement call. The spenders are the Breaths
   (Neltharion 511109, Malygos 555701, and a **Breath of Alexstrasza** that
   `Deep Breaths` names and that appears in **neither** database).
   **Settled by:** /pyprobe dumping the player's auras while building charges
   on Draconic — which id gains stacks, and what does it cap at.
4. **`Kael's Command`** still carries `TESTING SPELL`. Live or not?
5. **`Stoke`** — confirm the Flameweaving talent is a passive, and that the
   castable 803952 is dead. Then remove it from the main row.
6. Remaining **176 inventory rows** need the §0 cross-database sweep.
6b. ~~**Three abilities Sidekick names as cooldowns have NO inventory row** —
   `Draconic Assault`, `Firewall` (Draconic), `Comet Storm` (Incineration).~~
   **CLOSED 2026-08-07.** None was a Sidekick claim: each appears exactly once
   in the whole 3.8MB `sidekick-data.js`, inside the generated blurb "Line up
   X, Y, Z with your burst window", and Sidekick's own skill data has no record
   of any of them. `Comet Storm` 524612 is a component beside
   `Comet Storm Trigger` 524611; `Firewall` 806238 is literally described as
   "Deprecated" and the live one is `Spellguard: Firewall` 944833 (now aliased);
   `Draconic Assault` 802116 has no record on db.ascension.gg and its own
   tooltip disqualifies it — "disabling all of your abilities", "Not useable
   indoors". All three now have inventory rows carrying that reasoning.

6c. **Two real Flameweaving buttons were sitting unplaced in Candidates** —
   `Flames of Al'ar` 500202 (2 min, empowers the Phoenix) and `Kiss of Al'ar`
   704280 (15s, "The Phoenix heals an ally target"). Both are records on both
   databases. Both are **held at `ignore` on purpose** until the Phoenix section
   exists, because `build_pyromancer.py` reads roles from the inventory and an
   `offensive` there would put a third Phoenix-dependent button on a pack that
   still cannot say whether the Phoenix is alive.
   Surfaced by `citations.py --validate`. The skillbook seed missed them, which
   is the same direction that cost Runemaster its Runeblade row. Add them.
7. The other nine bulk-cleared rows flagged in `class-pack-process.md`:
   `Melt`, `Emberheart`, `Dancing Flames`, `Draconic Tempest`, `Dragon Leap`,
   `Supernova`, `Flame Swell`, `Conjure Campfire`, `Soar`.
   (`Stoke` was the tenth, and it was wrong.)
8. **0 citations** — `resources/citations-pyromancer.json` does not exist;
   `tests/run.py` check 15 fails on it. The Sidekick pages now scraped are the
   citation source.
