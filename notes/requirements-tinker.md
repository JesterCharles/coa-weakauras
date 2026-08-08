---
title: Tinker — class pack requirements (Phase 0)
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, tinker, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
  - "[[sidekick-tinker-demolition]]"
  - "[[sidekick-tinker-invention]]"
  - "[[sidekick-tinker-mechanics]]"
---

# Tinker — requirements

Class **28**, token `TINKER`, specs **Demolition** (ranged explosives damage),
**Invention** (healer), **Mechanics** (ranged/pet hybrid). No pack exists yet;
this is the Phase 0 document for the first build.

Research sources: the three Sidekick spec pages scraped **2026-08-07** to
`resources/sidekick-tinker-<spec>.md`; the db.exil.es class digest
(`exiles-tinker.json`, 759 spells, fetched 2026-08-07); the Sidekick skillbook
(`coa-tinker-skills.json`, 274 entries, blob snapshot 2026-08-02, upstream
unchanged on the 2026-08-07 re-check); `spell-meta-tinker.json` (759 ids);
db.ascension.gg `?spell=<id>&power` tooltips for individual verdicts.

**Spec roles are NOT in `resources/spec-roles.md`** (that file is observed in
game, one class at a time, and has no Tinker rows). The role claims here are
**Sidekick's**, not the game's:

| Spec | Role (Sidekick's claim) | Source line |
|---|---|---|
| Demolition | ranged damage | "Demolition is a fully-ranged explosives gunner" (Playstyle) |
| Invention | **healer** | "Invention is a healer spec, so soloing is slow" (Rotations) |
| Mechanics | ranged damage + permanent pet | "Mechanics is a Scrap-fueled ranged/pet hybrid" (Playstyle) |

`UNKNOWN — in-game confirmation of the three roles; spec-roles.md gains Tinker
rows only from the client.` The pack is built to Sidekick's claims (the only
citable source), with Invention treated as the healing spec.

---

## −1. Changelog — run FIRST

`changelog_watch.py --class tinker --pages 6`, scanned 600 entries over
2026/07/31..2026/08/07.

- [x] changelog scanned, newest tinker entry: **2026-07-31** (7 entries)
- [x] every entry triaged below
- [ ] `--accept` after the entries are acted on (deferred to end of research)

| Entry (2026/07/31) | Category | Where it lands |
|---|---|---|
| "Mechanical Enhancements now reduces damage taken from bleeds by 20%, up from 10%" | numbers | none |
| "The Mechano-Bear now generates increased threat with Mechano-Growl" | numbers (pet threat) | §3 — confirms Mechano-Bear is a live pet model |
| "Macro Designer now increases the duration of Beacons by an additional second (+5 → +6 sec)" | numbers | none (Beacon zones are ground effects, untracked — §4) |
| "Goblin Depravity now creates a Crash Site instead of Tear Gas, now deals Fire Damage instead of Nature Damage" | reworked | §2 — **Sidekick is stale on this talent** (its page still says Tear Gas). WA impact: none — the talent modifies Air Strike's ground effect; Air Strike stays a cooldown icon either way |
| "Build: Restorative Beacon base value doubled, scaling increased by 6%" | numbers | none |
| "Range of Med Pack increased from 10 yds to 30 yds" | numbers | none |
| "Emergency Heal base value increased by 30%, cast time reduced 1.8 → 1.5 sec" | numbers | §4 — confirms Emergency Heal is live Invention kit; it must have an inventory row |

Sidekick snapshot recency: the spec pages were scraped 2026-08-07 and the
skillbook blob is dated 2026-08-02 — both AFTER the newest tinker changelog
entry (07/31) — **except** the Goblin Depravity talent text, where the page
still carries the pre-rework wording. That one claim is dated; nothing the
pack draws depends on it.

---

## 0. Ability surface — both databases

Inventory seeded from the skillbook (274 entries) unioned with the cooldown
audit; ids resolved through `exiles-tinker.json`; the whole inventory swept
against db.ascension.gg by `crossdb_sweep.py` (verdicts in
`crossdb-tinker.json` and in the inventory Notes cells).

- [x] every inventory row with an id cross-checked against both DBs —
      `crossdb_sweep.py tinker`, **271/271 asked, 266 record, 5 no-record**,
      verdicts in `resources/crossdb-tinker.json`
- [x] all 5 `no-record` rows resolved by name re-ask with tooltip reads,
      recorded in their Notes cells:

| Ability | exil.es id | Resolution |
|---|---|---|
| Bot: Hydraulic Strike | 800570 | **other-id** — ascension castable is 524910 (6% mana, 12s cd, "Commands your Clockwork Assistant"). 800570 is Rank 1, so the icon matches by NAME and rank drift cannot hide it. Live |
| Distracto Shot | 560470 | **other-id** — 561269 on ascension, same interrupt+silence (the documented crosscheck example). Live |
| Boomshot | 502507 | **name collision** — 502507 is a different Boomshot (a gunshot from the cut Rounds minigame, "Fires 1 Round…"); the live entity is the every-4th-Scrap-Shot proc PASSIVE, ascension 707249. Row repointed |
| Blackpowder Barrage | 801822 | **dead** — 0 name hits on ascension; its desc is the Rounds/Reload gun minigame SK demolition explicitly says no longer exists. `ignore` |
| Telescopic Focusing Lens | 801819 | **dead** — 0 name hits; own exil.es desc is "Deprecated Spell". `ignore` |

- [x] deprecated/unused/placeholder names filtered (`WIP`/`TEST`/`SLS` names
      → ignore; Magic-Cleanser 4000X rank "Deprecate" → ignore)

Known before the sweep, from individual `?spell=<id>&power` asks:

| Ability | Note |
|---|---|
| Build: ZIGGI-6K | only id in either digest is 92140, the L10 teaching passive ("Teaches you Build: ZIGGI-6K", Specialization). The CASTABLE summon has no id in the exil.es digest — §6.8 |
| Build: Mechsuit | same shape: 92141 is the L10 teaching passive; the castable's own id is not in the digest. The suit ABILITIES (Combustion 801387, Laser Beam 805372, Activate Jets 801389) all carry real ids |
| Scrap (meter) | 707470 is a 0.2s "Mechanics Passive Checker" dummy; threshold markers are hidden-clientside — §6.1 |

---

## 1. Mandatory buffs

**From the class kit — GUN AUGMENTATIONS are the imbue analogue.** 1-hour gun
imbues, exactly Runemaster's engraving shape ("Add a X Augmentation to your
gun for 1 hour"):

| Buff | Spec | Why the rotation needs it | Where it renders |
|---|---|---|---|
| Piercing / Explosive / Tracer Augmentation | Demolition | 1-hour gun imbue; Augmentor/War Crimes key off it; forgetting it is a silent throughput loss | long-term band + **NO AUGMENT alert** (fires when none of the three is up) |
| Aether / Magic / Stim Augmentation | Invention | same shape; Stim splashes direct heals to 3 allies | long-term band + **NO AUGMENT alert** |
| (Mechanics has no gun augmentation) | — | its augment kit applies to the bot (§3) | no alert |

**From abilities — procs that say "press this now"** (§5 wires them):

| Buff | Spec | Cue |
|---|---|---|
| Boomshot ("every 4th Scrap Shot… next deals 25% more") | Demolition | glow Scrap Shot |
| Aftermath ("next 2 Scrap Shots faster and harder" after Sticky Bomb) | Demolition | glow Scrap Shot |
| Innate Brilliance (every 4th Scrap Shot under Aether Aug.) | class talent | glow Scrap Shot |
| Bombastic ("next Bomb Toss free, no cooldown" after Spider Bomb) | Demolition | glow Bomb Toss |
| Overload (Combustion / Laser Beam strike extra times) | Mechanics | on-me row |
| Machine Synergy (pet+turret stacks from Scrap Shot) | Mechanics | on-me row, `unit="pet"` |

**On the target** (target band, §4): Napalm (10 stacks, Fire amp), Sticky Bomb
(the armed window — Rocket Launcher's guaranteed crit reads off it), Bomb
Toss armor shred stacks, Tracer Augmentation marks; Invention helpful-side:
Nanobot Reconstruction HoT, Med Pack HoT, Auto Resuscitation Device,
Kinetic Shield.

---

## 2. Talent-driven rotation changes

| Talent | What changes | Rotation impact | WA adaptation |
|---|---|---|---|
| **Build: Mechsuit** (L10 spec passive 92141) | teaches the suit; entering it unlocks Mechsuit: Combustion 801387 / Laser Beam 805372 / Activate Jets 801389 (+ Sawblade 801381, Artillery Rush 801391 on upgraded models) | the suit window IS the Mechanics burst | suit abilities drawn as ordinary `cd_icon`s on their own numeric ids; `spellUsable==0 → desaturate` (check 9) carries the "not in suit" state. §6 flags the open question of whether the suit GRANTS the spells (Spell-Known flicker) or leaves them known-but-unusable |
| **Upgrade Mechsuit: Spider Tank 801710 / Vanguard X-42 801393** | swaps the suit model and its ability set | different suit buttons | both upgrade CASTABLES are utility rows; the model-specific extras stay drawn — an unusable one desaturates. No exact-id swap needed: nothing replaces Combustion/Laser Beam ids |
| **Bombastic / Bomber Man** (Demolition passives) | Spider Bomb resets Bomb Toss; Bomb Toss shaves Sticky Bomb CD | resets mid-loop | PROC_GLOW on Bomb Toss (Bombastic aura); cooldown icons already re-read the real CD |
| **Boomshot / Aftermath** (Demolition) | every-4th / post-Sticky-Bomb Scrap Shot empowerment | filler windows | PROC_GLOW on Scrap Shot |
| **Rocket Barrage** (Demolition talent 801168) | Tracer stacks +5, Bomb Toss at 10 stacks launches a barrage | more Tracer value | active-only; correct with and without (no display keys on stack cap) |
| **Innate Brilliance** (class tree, choose-one) | every 4th Scrap Shot under Aether Aug. grants a buff | filler window | PROC_GLOW on Scrap Shot; absent without the talent (active-only, correct both ways) |
| **Goblin Depravity** (class tree; changelog 07/31: Crash Site, Fire) | modifies Air Strike's ground effect | none for the pack | Air Strike stays a cooldown icon |
| **Sprocket Loaded** (Mechanics 807500) | Makeshift Dynamite resets Mechsuit abilities | suit weave | nothing to draw — the suit icons' own cooldown triggers re-read the reset |

No talent found that REPLACES a tracked ability with a different spell id (no
Zenith/Runelord analogue in any of the three trees or the class tree as
scraped). The Mechsuit is a self-transformation that ADDS buttons, handled
above; every added button is tracked on its own numeric id.

Each row reads correctly with and without the talent: proc rows are
active-only, cooldown icons re-read the client's cooldown, and no display is
gated on a talent-only aura except the proc displays themselves.

---

## 3. Pets — yes, Mechanics; deployables everywhere

**Mechanics is a permanent-pet spec.** Four interchangeable bot models, one
out at a time, all "accompany the Tinker until dismissed" (`Dismiss
Assistant` 803406 family):

| Pet | Summoned by | Duration | Track | Where it renders |
|---|---|---|---|---|
| Clockwork Assistant | Build: Clockwork Assistant 524974 | permanent | presence; Machine Synergy stacks (`unit="pet"`) | NO PET alert + on-me row |
| Scrapmaw | Build: Scrapmaw 500242 | permanent | same (the cited DPS model) | same |
| Mechano-Bear | Build: Mechano-Bear 803405 | permanent | same (changelog 07/31: threat model) | same |
| Rusthound | Build: Rusthound 803437 | permanent | same | same |

- Pet **commands the player presses**: Bot: C.U.R.B Stomp 800581,
  Bot: Flamespill 800572, Bot: Hydraulic Strike 800570 — **real cooldown
  rows**, not `ignore` (the mkabilities pet default is overridden here).
- Pet buffs worth tracking: Machine Synergy (pet stacks), Overclocked Machine
  (burst window), Junker/Master Technician stacks — on-me row entries, pet
  ones with `unit="pet"`.
- **NO PET alert** (mechanics only): aura trigger `unit="pet"`,
  `showOnMissing`, ANDed with Spell Known on **Build: Scrapmaw 500242**
  (exact=False) so a levelling character is not nagged. NOT gated on
  Clockwork Assistant: its exil.es row 524974 carries rank "NOT IN USE" —
  the live models are the other three, and the ascension Bot: tooltips
  still say "Clockwork Assistant", so the name survives as the bot's
  generic label. The pet-side aura id is UNVERIFIED (§6.2): candidates are
  the Tinker Pet Scaling Aura family 520508/520510/524064–524067 — the
  same absent-unit mechanism Stormbringer ships flagged.
- Pet resource: none found in any source. No bar.

**Deployables are NOT pets** — decided per tooltip, per the process note:

| Deployable | Spec | Tooltip shape | Verdict |
|---|---|---|---|
| Build: Firepot Drone (3 charges) | Demolition | flies to target, explodes | charge-counted cooldown icon |
| Build: Spider Bomb / Spider Bomb Factory | Demolition | runs to target, detonates | cooldown icons |
| Build: Oil-Spill Pylon | Demolition | zone for a duration | cooldown icon |
| Build: Sentry Turret 500239 | Mechanics (class-tree talents also modify it — Notes) | toggle build/deconstruct, "only 1 up", no duration | cooldown icon; uptime deliberately untracked in 0.1 (§6.4) |
| Build: Battle Turret X-13 / Power Foundry / Deploy Turret Wall | Mechanics | duration summons | cooldown icons |
| Build: Destructo-Bot / Repulsion Unit / Alarm Beacon (3 ch.) | class | controlled bomb / zone / zone | cooldown icons |
| Build: Restorative / Shield / Replenishment Beacon (3 ch. each), Build: Battery Recharge Station, Build: ZIGGI-6K, Refreshment Bot!, Build: Noise Box | Invention | thrown zones with durations | cooldown icons (Restorative Beacon in the main healing row) |

None of these is a pet: every one is player-side state (a cooldown, charges,
or a zone), tracked exactly like any cooldown. Only the permanent bot gets
pet treatment.

---

## 4. Primary damage source and the main row

| Spec | Primary source | Main row, press order (cited) | Icons | Resource / segments |
|---|---|---|---|---|
| Demolition | Sticky Bomb explosion engine + Scrap Shot filler | Bomb Toss · Sticky Bomb · Scrap Shot · Build: Firepot Drone · Rocket Launcher | 5 | mana bar only ("There's no ammo, Rounds or reload minigame here" — Resource §) |
| Invention | healing: Repair Shot cast + Zap! instant | Repair Shot · Zap! · Nanobot Reconstruction · Build: Restorative Beacon · Med Pack | 5 | mana bar only |
| Mechanics | pet + Scrap-fueled Mechsuit | Scrap Shot · Makeshift Dynamite · Sticky Bomb · Mechsuit: Combustion · Mechsuit: Laser Beam | 5 | mana bar; **Scrap meter has no buildable surface yet — §6.1** |

Press order sources: the per-spec Rotations paragraphs of the 2026-08-07
Sidekick scrapes, transcribed into `citations-tinker.json`
(`sidekick-page-tinker-<spec>-2026-08-07`).

- The Sidekick header "Resource: Mana + Ammo" appears verbatim on all three
  spec pages and is contradicted by each page's own spec-specific Resource
  paragraph — it is a class-level template string, not a claim. Mana is the
  only power bar on all three specs.
- Demolition's mana economy is crit-refund driven (Explosives Expert); the
  mana bar carries that read.
- Invention healing surfaces: **target band only** (your HoTs/absorbs on your
  current target, `dot_bars(helpful=True)`) per the settled healing-spec
  scope. VuhDo/Grid own raid frames. Beacon ZONES are ground effects with no
  target aura and are deliberately untracked beyond their cooldown icons.
- `CD_PER_ROW` derives from the narrowest main row (all three are 5 icons =
  218px at 44px/2px… computed by rowwidths at build time), recomputed for
  this class, never copied.

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Gun Augmentation (Demolition/Invention) | silent %-loss for an hour | NO AUGMENT alert (reminder band, fires on absence of all three) | same shape as RM NO ENGRAVING, verified pattern; in-game trip confirms the aura names (§6.3) |
| Pet dead/missing (Mechanics) | most of the spec's damage | NO PET alert | mechanism flagged unverified (§6.2) — same shape Stormbringer ships |
| Sticky Bomb window | the explosion engine stops | main-row cooldown swipe + Sticky Bomb debuff in target band | check 9/10 on the icon; target band is active-only aura (name match) |
| Napalm stacks dropping | Fire amp lost | Napalm stacks in target band | active-only aura display |
| Boomshot / Aftermath / Bombastic / Innate Brilliance procs | wasted empowerment | PROC_GLOW on Scrap Shot / Bomb Toss | proc rows are aura-triggered; names verified by crossdb; final proof is the in-game pass |
| Rocket Launcher into un-Stickied target | loses guaranteed crit | Sticky Bomb visible in target band next to the launcher's icon | draft accepts the read; no condition ties them (§6.5) |
| Off-cooldown Mechsuit abilities outside the suit | none (unusable) | `spellUsable == 0 → desaturate` | check 9 enforces the condition exists |
| Overclocked Machine / burst CDs drifting | throughput | escalation tiers on cooldown rows (20s timer / 10s glow / 5s urgent) ANDed `onCooldown == 1` | check 9 (no bare expirationTime), check 10 (GCD flags from scraped data) |
| Nanobot Reconstruction dropping on the focus-heal target | HoT gap | Invention target band glow at refresh threshold | dot_bars refresh_at; healing band is active-only |

Every cooldown icon: `use_showgcd` per scraped GCD data (check 10),
desaturate-when-unusable (check 9).

---

## 6. Open questions

- [ ] **6.1 UNKNOWN — the Scrap meter has no buildable surface.** Scrap is
  real (0–100, generated by Scrap Shot/Sticky Bomb/Makeshift Dynamite/
  Cogmaster crits, drained as Mechsuit fuel), but no UnitAura-visible counter
  exists in either DB: `Scrap` 707470 is a 0.2s "Mechanics Passive Checker"
  dummy, and the `At Least 25/50/100 Scrap` markers (704455/704453/704456)
  carry attr0 256 (hidden clientside) with -0.001s duration — server
  machinery, not auras. **0.1 ships without a Scrap bar.** What settles it: an
  in-game `/rmdump`-style UnitAura scan while building Scrap; if a stacking
  aura exists, it becomes a `stack_bar(step=10)` like Stormbringer's Static.
- [ ] **6.2 UNKNOWN — NO PET alert mechanism.** Whether an absent pet unit
  reports "aura missing" on this fork, and which aura rides every bot model
  (candidates: Tinker Pet Scaling Aura family 520508/520510/524064–524067).
  Built anyway, flagged, same as Stormbringer §6.6.
- [ ] **6.3 UNKNOWN — Augmentation buff names/ids as seen by UnitAura.** The
  castables are 653234/653236/653245 (Demolition) and 653130/(Magic)/653239
  (Invention); whether the 1-hour buff carries the same name is the standard
  name-error class the draft tolerates. Alert matches id AND name, any-of.
- [ ] **6.4 UNKNOWN — Sentry Turret uptime surface.** "Can only have 1 Sentry
  Turret up at a time", no duration row; whether a player-side aura reflects
  an active turret is unknown. 0.1 tracks only the button's cooldown.
- [ ] **6.5 deferred** — no condition ties Rocket Launcher's glow to the
  Sticky Bomb debuff (would need a target-aura AND on a cooldown icon; kept
  simple for 0.1, feedback decides).
- [ ] **6.6 UNKNOWN — does entering the Mechsuit GRANT the Mechsuit: spells
  or are they known-but-unusable outside the suit?** 0.1 assumes
  known-but-unusable (desaturate carries it). If the client instead grants
  them on entry, the icons vanish outside the suit — which also reads
  correctly, just louder. One in-game look settles it.
- [ ] **6.7 UNKNOWN — Overcharge (Invention, 524835)** has no ascension
  record under that id; exil.es shows a castable. Shipped as a cooldown icon
  on the exil.es id; if it never lights, the in-game pass captures the real
  id.
- [ ] **6.8 UNKNOWN — Build: ZIGGI-6K castable id.** Only the L10 teaching
  passive (92140) exists in both DBs. The ZIGGI cooldown icon is therefore
  tracked by NAME (cooldown trigger by name resolves whatever the client
  knows); if that fails in game, capture the id.
- [ ] **6.9** Hedged inventory rows from the automated role pass (25, marker
  `hedged:` in their Notes cells): Arcane Bionics, Battery Swap, Blasting
  Powder, Bomb Specialist, Build: Bounce Pad!, Chaos Shift, Cloaking Device,
  Combat Symbiosis, Control Mechanical, Deconstruct Sentry Turret, Dismiss
  Assistant, E.M.P, Emergency Module, Freeze Ray, Greater Mana Module,
  Greater Power Module, Guardian Module, Hasta la Vista, Invisibility Cloak,
  Landstrider Keys!, Re-Build, Shield Combatant, Spare Parts, Strength
  Bionics, Torment. Mostly Modules/Bionics/gadget utilities with a cooldown
  but no cited role — feedback and the in-game sweep are their checklist.
- [ ] **6.10** Upgraded-suit model ability bars (Spider Tank: Flak
  Guns/Scurry/Stomp, Vanguard X-173: Onslaught/Shield Crush, Vanguard X-42:
  Fuselight Furnace/Imposing Presence) are `ignore` in 0.1 — only the
  base-suit buttons are drawn. If feedback says the model bars matter, they
  become spec rows.
