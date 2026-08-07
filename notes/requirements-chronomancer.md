---
title: Chronomancer — class pack requirements (filled in RETROSPECTIVELY)
date: 2026-08-07
type: note
status: budding
tags: [weakauras, conquest-of-azeroth, chronomancer, requirements]
sources:
  - "[[class-requirements-template]]"
  - "[[class-pack-process]]"
---

# Chronomancer requirements

⚠️ **This is a retrofit, and it should be read as one.** Chronomancer shipped
1.2 (verified in game 2026-08-02, all three specs) *before* Phase 0 existed.
Every other class fills this in before a band is written; this one is being
reconstructed from a pack that already runs. The value is not that it gates the
build — that ship has sailed — it is that the gaps below are now *written down*
instead of waiting to arrive as bug reports.

The bar is not perfection. The site publishes a credible standard per class and
spec and converges it on player feedback, so the question for every gap here is
**"would this silently mislead a player?"** — a dead button or a bar that never
fills, yes; a debatable press order, no, that is a feedback question.

---

## −1. Changelog

```bash
python3 tools/changelog_watch.py --class chronomancer --pages 6
```

- [x] changelog scanned, newest entry: **2026-08-03**
- [x] every `replaced with` / `now reads` / `now baseline` / `new spell` /
      `reworked` entry triaged
- [x] `--accept` run 2026-08-07, **after** triage, chronomancer only

21 entries (2026/07/31 and 2026/08/03). Full reasoning lives in the Notes cells
of `resources/abilities-chronomancer.md`; the categories:

| Entry | Date | Category | Where it lands |
|---|---|---|---|
| Cycling Aeons replaced with Rapid Acceleration | 07/31 | §2 replace — **but a rename, not a new spell** | Same id 570149, renamed in place, rank Passive. No display reacts. New inventory row |
| Cycling Aeons baseline; Aeon cooldowns halved | 07/31 | numbers | Aeons read as stances (Ripple's icon), not timers — nothing on screen |
| Aeon of Oblivion / Renewal / Protection / Resilience reworked | 07/31 | §2 rework | **§6 open** — two Time target bars may now be dead, see below |
| Fray Magic added (interrupt, trainer, lvl 26) | 07/31 | new spell | Already in the pack. Id not settled, see §6 |
| Timeguard: +>20%-health clause, 40%→50% | 07/31 | mechanic + number | **§6 open** — it is a 3-application buff on the ALLY |
| Temporal Anomaly releasable early | 07/31 | mechanic | **§6 open** — a press-twice ability with no second-press cue |
| Fortify Timeline extends Accelerated Recovery +5s (cap +15s) | 07/31 | mechanic | **§6 open** — press-priority question for Time |
| Chronicler reimplemented (+5s per cast, +15s cap) | 08/03 | passive | Compounds the Fortify Timeline question |
| Rewind: slow, +speed, usable while CC'd | 07/31 | mechanic | Effects on a button already displayed — nothing new |
| Gravity Bomb explodes on target death | 07/31 | mechanic | Removes a wasted cast, does not change when you press it |
| Keep Accelerating prefers untouched targets | 07/31 | passive | Targeting rule inside a passive. New inventory row |
| Moment's Reprieve cooldown/cost bug fixed | 07/31 | numbers | Our scrape predates the fix — **re-scrape owed** |
| Correct the Mistake −20% scaling | 07/31 | numbers | main row, unchanged |
| Infinite Shield range → 40 yds | 07/31 | numbers | unchanged |
| Constant Recovery −20% holy threat | 07/31 | passive | unchanged |
| Timeline Tether / Rapid Acceleration repositioned | 07/31 | tree layout | unchanged |

---

## 0. Ability surface — both databases

- [x] every inventory row cross-checked against both DBs — **251/251**,
      `resources/crossdb-chronomancer.json`, swept 2026-08-07
- [x] `no-record` rows justified in the Notes cell — **7, none removed**
- [x] deprecated/placeholder names filtered

`no-record` was a stop, not a delete-list, and every one of the seven survived
the re-ask by name:

| Ability | Id | Verdict |
|---|---|---|
| Chronobeam | 801267 | `NO_UPSTREAM_ART` gap. Ascension's 801305/804460 are stubs; ours carries the real tooltip |
| Chronurgy | 806326 | Same gap. Ascension has a Deprecated 572745, a CD-refresh 503950 and an Order/Chaos pair; ours is the base |
| Fray Magic | 800053 | Same gap, **but the id is not settled** — see §6 |
| Reflection | 801296 | Same gap. Ascension's 9906 is the vanilla spell-reflect, a different ability wearing the same word |
| Unearth | 503884 | Rank family. exil.es shows *this rank* as "Deprecated", which reads alarming and is not: the cooldown audit has a real 6s row and the `Echo` talent keys off casting it. Matched by NAME, so rank-agnostic |
| Sandblast | 501918 | Rank family. Ascension carries Rank 5 (501921) and Rank 10 (573222) and not our Rank 2 — which is what a rank family looks like from one side |
| Shifting Sands | 806317 | No record and no name hit anywhere on ascension; full exil.es tooltip. See §2, it describes a transform |

Two of the seven name hits were **different abilities wearing the same word**
(Reflection 9906, Fray Magic 560825 — a hunter passive about Serrated Shot).
That is the trap the sweep exists to catch, hit twice in one pass.

---

## 1. Mandatory buffs

| Buff | Source | Why the rotation needs it | Where it renders |
|---|---|---|---|
| The active **Aeon** (806290–806293) | class, Time | Every Epoch and every Ripple behaves differently per Aeon. Standing in the wrong one is silent | Ripple's icon face swaps to `Rippling <Aeon>`; the Aeons also sit in the Time long-term band |
| Eternity Warper (806301) | lvl-50 passive | Without it Ripple has no per-Aeon behaviour, so the icon must NOT promise one | `["Spell Known"]` trigger ANDed into every Ripple face — an aura trigger never fires, it is `effect=6 aura=4` and hidden from UnitAura |
| Sands of Time (804488) | Time, built by Epoch | 5 stacks then consumed — the spec's spend meter | `stack_bar` under the Time main row |
| Echo Fragments (804455) | Artificer | Spent on Distortion spells and on extending the active Continuum | `stack_bar` under the Artificer main row |
| Accelerated Recovery | Time, core HoT | The whole Time rotation is keeping it up, and it is now extendable to +15s | Time target band, glows at 4s |
| Anomaly Spikes, Infinite Power, Chaos Fusion, Chaotic Time | Infinite | The haste stacks and cooldown shave all key off periodic damage | Infinite buff row |
| Clocked In, Discovery, Singularity Core, Flux Emitter | Artificer | Wand-spec proc/stack state | Artificer buff row |

**No missing-buff alert exists for any of these.** Runemaster earned
`NO ENGRAVING` / `NO ETCHING` because a missing imbue is a silent throughput
loss; the Chronomancer equivalent is **standing in no Aeon at all**, which is
reachable (the lvl-10 passive only *teaches* Aeon of Resilience, it does not
apply the stance) and is already handled as a fifth Ripple face rather than an
alert. Whether it deserves a real alert is a feedback question, not a defect.

---

## 2. Talent-driven rotation changes

| Talent / effect | ID | What changes | Rotation impact | WA adaptation |
|---|---|---|---|---|
| Eternity Warper | 806301 | Gives Ripple a different effect per Aeon | Ripple becomes four abilities | Five displays in one slot; `["Spell Known"]` gate. **Built** |
| The four Aeons | 806290–806293 | Mutually exclusive stances, shared cooldown, each rewrites Epoch | Changes what every heal does | Ripple icon swap + long-term band. **Built** |
| Chaos Empowerment → Shifting Sands | 806317 | Tooltip: "Entering Chaos Empowerment **transforms this ability into Melt Reality**" | A spell swap, the Runemaster 1.3–1.6 trap exactly | **UNKNOWN**, see §6. Both names already have their own target bar, so the band survives either way |
| Rapid Acceleration (was Cycling Aeons) | 570149 | +15% AR bonus-healing scaling; AR instantly heals 15% of its periodic | Passive | None needed |
| Keep Accelerating | 520042 | AR also applies to a nearby target, preferring untouched ones | Passive | None needed |
| Chronicler | 680391 | Each Fortify Timeline extends AR a further 5s, cap +15s | Makes Fortify Timeline rotational for Time | **UNKNOWN**, see §6 |
| Protector Training | 706073 | −20% pet spell cooldowns | Pet only | See §3 |

**Does the pack read correctly with and without each?** Yes for the built rows —
Ripple's fifth face covers no-Aeon, and the Eternity Warper gate covers
sub-50. The Chaos Empowerment transform is the one that has never been watched.

---

## 3. Pets — **this section is the real gap**

- [x] Does this class summon a pet? **Yes.** A **Bronze Protector** (Time) and
      an **Infinite Protector** (Infinite) — `Rehatch` (578265) resurrects the
      Bronze one, `Dismiss Protector` dismisses it, and `Infinite Wrath`
      (804498) carries `db line = "Pet - Infinite Protector"`.
- [x] Does the pet have abilities the player reacts to? **Its own spellbook
      exists**: Breath of Time 805162, Rumble 805166, Timelink 805170,
      Infinite Shroud 805168, Chaos Embrace 805167 (deprecated).
- [x] Does it apply buffs that need tracking? **Yes** — the Artificer
      Chronobuffs (`Artificer's Magic` 804422, `Spellplate` 804431,
      `Toughness` 804420) are `rank=Chronobuff`, 40yd, and the **pet casts them
      on you**.
- [ ] Does pet presence gate the rotation? **UNKNOWN**
- [ ] Does the pet have a resource worth a bar? **UNKNOWN**

**The shipped pack has no pet section at all.** Every one of those rows is
`ignore` with the reason "pet spellbook, not a player button" — which was the
old blanket rule the template explicitly retired. `Rehatch` is the tell: a
button whose entire job is *recovering a dead pet* only earns a slot if the pet
mattered, and it is in the Time utility row today with no way to see whether the
pet is alive.

This is the highest-value unbuilt thing in the class, and it is squarely the
"would this mislead a player" category: a Chronomancer whose Protector is dead
currently gets no cue at all.

| Pet | Summoned by | Duration | To track | Where |
|---|---|---|---|---|
| Bronze Protector | UNKNOWN — no summon spell found in exiles | UNKNOWN | alive/dead; the three Chronobuffs it casts on you | not built |
| Infinite Protector | UNKNOWN — same | UNKNOWN | alive/dead; Infinite Wrath | not built |

---

## 4. Primary damage source and how the main bar reads

`CD_PER_ROW = 7`, derived from the narrowest main row in this pack (five icons,
182px: `28w − 2 <= 1.2 × 182` gives `w <= 7.8`). Do not copy it to another class.

| Spec | Primary damage | Main row, in press order | Icons | Resource / segments |
|---|---|---|---|---|
| Artificer | Artificer's Wand filler generating Echo Fragments, spent on Distortion + the active Continuum | Artificer's Wand → Wand of Time → Discordance → Shatter Echo → Decomposition | 5 | mana bar + Echo Fragments (804455, 5 stacks) |
| Infinite | Chaos DoTs; the haste stacks and cooldown shave key off periodic damage | Chromatic Shard → Melt Reality → Timerend → Unmake → Discordance | 5 | mana only, full height. Sidekick is explicit there is no dual Order/Chaos economy |
| Time (healing) | Epoch, whose behaviour is set by the active Aeon | Epoch → Accelerated Recovery → Reverse Wound → Correct the Mistake → Ripple | 5 (Ripple is 5 displays in 1 slot) | mana bar + Sands of Time (804488, 5 stacks) |

Healing surfaces are scoped out by design: no raid frames, no HoT grid. Time
gets the **target band** instead — your own HoTs and absorbs on your current
target. VuhDo/Grid own raid-wide state on 3.3.5a.

---

## 5. Miss-handling

| Ability | Cost of missing it | Cue | How we prove the cue fires |
|---|---|---|---|
| Accelerated Recovery | The Time rotation is keeping it up; dropping it is the spec's main loss | target-band bar, glow at 4s | seen in game (1.2, 2026-08-02) |
| The Infinite DoTs (Melt Reality, Timerend, Unmake, Decomposition, Shifting Sands) | Every haste stack and cooldown shave keys off periodic damage | target band, glow at 5s | seen in game (1.2) |
| Thread of Eternity | Artificer's DoT, rides Discordance | target band, glow at 4s | seen in game (1.2) |
| Ripple under the wrong Aeon | You cast the wrong effect and never know | icon face swaps per Aeon | seen in game — and it took three tries: `iconSource=-1` made all five draw the same staff, and an aura trigger on Eternity Warper never fired |
| The four Aeon per-target effects | Whichever Aeon you stand in does nothing visible | target band | **NOT PROVEN post-rework** — see §6 |
| Fray Magic (interrupt) | A cast goes through | cooldown row icon | **NOT PROVEN** — id not settled, see §6 |
| Protector dead | Losing the Chronobuffs and the pet's damage entirely | **no cue exists** | n/a — §3 |

`tests/run.py` carries the structural half: check 9 (desaturate on
`spellUsable == 0`), check 10 (GCD sweep), check 13 (reads the *published*
pack), check 22 (no damage component in a pressable row). None of them can
prove an aura lands on a target — only a trip can.

---

## 6. Open questions

The in-game checklist. Sorted by the rule that matters: **would it mislead a
player?**

**Would mislead — worth a trip:**

- [ ] **Do the Aeon target bars still fill?** Aeon of Resilience was reworked
      from a damage reduction *on the target* to "Accelerated Recovery bounces
      to another target", and Aeon of Oblivion to damage splashed on a *nearby
      enemy*. Neither new text describes a per-target aura. `Resilience`
      (560373) and `Oblivion` (560376) may now be dead bars in the Time target
      band. Both ids still resolve on db.ascension.gg, which proves nothing
      about whether anything applies them. **Settled by:** cast Epoch under each
      of the four Aeons and watch the band.
- [ ] **Is Fray Magic 800053 or 510236?** Ours is corroborated by the cooldown
      audit (real 25s row) and by two skillbook talents that name it; ascension
      has no record of it but does carry 510236, "Stop your enemies' timeline",
      30s / 27% mana — unmistakably this class's interrupt. A wrong id here is
      an interrupt icon that never appears. **Settled by:** one look at the
      spellbook.
- [ ] **Does the Protector need a section, and is there a summon spell?**
      No summon spell is in `exiles-chronomancer.json` at all, and a dead pet
      currently produces no cue. **Settled by:** the pet bar in game plus the
      spellbook.
- [ ] **Does Chaos Empowerment really swap Shifting Sands → Melt Reality?**
      This fork resolves no spell overrides, so a transform means the server
      grants one and removes the other. **Settled by:** entering Chaos
      Empowerment and watching both target bars.

**Feedback questions — ship and ask:**

- [ ] Does `Fortify Timeline` belong on the Time main row now that it extends
      Accelerated Recovery by up to 15s? It is `defensive; time:offensive`
      today. Chronicler's 08/03 reimplementation pushes the same way.
- [ ] Does `Temporal Anomaly`'s early release deserve a second-press cue?
- [ ] Should `Timeguard`'s 3 remaining applications show as a count? They are
      a buff on the *ally*, so `GetSpellCharges` will not see them.
- [ ] Does "no Aeon at all" deserve a missing-buff alert rather than just
      Ripple's fifth face?

**Owed maintenance:**

- [ ] Re-scrape `Moment's Reprieve` — our numbers predate the 07/31 cooldown
      and mana-cost fix and the row says so.
- [ ] Re-scrape Sidekick. `resources/sidekick-data.js` is dated 2026-08-02,
      which is older than the 08/03 changelog entries, so the citations are
      stale for anything those touched.
