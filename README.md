# Conquest of Azeroth WeakAuras

WeakAura packs for [Ascension](https://ascension.gg)'s Conquest of Azeroth
custom classes, on the 3.3.5a client (WeakAuras fork reporting 5.21.2 Beta).

**→ [Get the packs](https://jestercharles.github.io/coa-weakauras/)**

One consistent layout across every class, so learning one pack teaches you all
of them. Every display is gated to its class and spec, so you can import as
many as you like — the ones you are not playing do not load and cost nothing.

**Status:** Runemaster (class 32) shipped. Chronomancer (class 22) next.

## For players

Everything you need is on the [site](https://jestercharles.github.io/coa-weakauras/).
Copy a string, `/wa`, Import, paste.

Each class ships four packs: **all specs** in one, plus a smaller **per-spec**
pack if you only ever play the one.

## For anyone poking at the code

The packs are not hand-built in the WeakAuras UI. `tools/` emits `!WA:2!`
import strings from scraped spell data plus a per-class categorisation, which
is what makes 21 classes tractable — a class pack becomes a data job rather
than an authoring job.

```bash
python3 tools/build_runemaster.py                    # all specs
WA_SPEC=glyphic python3 tools/build_runemaster.py    # one spec
python3 tests/run.py                                 # regression suite
python3 tools/mksite.py                              # regenerate docs/
```

### Read these first

| Doc | What it is |
|---|---|
| `notes/class-pack-process.md` | **Start here.** Step-by-step process for a new class |
| `notes/layout-standard.md` | The band layout and load-gating contract every class follows |
| `notes/weakauras-data-model.md` | Field-level reference from the WeakAuras source |
| `notes/runemaster-retro.md` | Ten bugs that cost iterations, and why |
| `notes/wa-import-string-format.md` | How `!WA:2!` encoding works |
| `notes/pipeline-plan.md` | Where this is going: shared engine + per-class config |

### Tools

| Script | Does |
|---|---|
| `wacodec.py` | encode/decode `!WA:2!` strings |
| `wabuild.py` | region/trigger/subregion constructors |
| `build_runemaster.py` | the Runemaster pack (template for other classes) |
| `mkguide.py` | annotated layout guide from a built pack |
| `mksite.py` | generates `docs/` for GitHub Pages |
| `audit_cds.py` | find every ability with a cooldown |
| `fetch_icons.py` | resolve real name + icon per spell id |
| `dbsearch.py` | batch search db.ascension.gg |
| `crosscheck.py` | ask both spell databases about every raid-utility row |
| `build_dump.py` | in-game diagnostic aura (`/rmdump`) |

### Data

| File | Contents |
|---|---|
| `resources/in-game-verified.json` | **Top precedence.** Ids read off tooltips |
| `resources/class-tokens.md` | class → WeakAuras load token, all 21 |
| `resources/exiles-runemaster.json` | 689 name→id pairs from db.exil.es |
| `resources/exiles-id-meta.json` | real name + icon per spell id |
| `resources/cooldown-abilities.json` | every ability with a cooldown, per spec |
| `resources/ascension-coa-class-ids.md` | class ids 12–32 and scraping notes |
| `resources/cross-source.json` | which raid-utility spells both databases have |
| `resources/import-strings/` | decoded community packs — the reference |

Source precedence: **in-game tooltip → db.exil.es → db.ascension.gg →
coabuildhub → ascensionsidekick**. Sidekick is best for mechanics, worst for
names.

### The two things that will bite you

**Bump `VERSION` on every release.** It feeds the uid salt, and WeakAuras
dedupes imports on uid — a rebuilt pack carrying the old salt is silently
discarded and the client keeps the old copy.

**Gate at the leaf.** A group's triggers, conditions and load are inert;
WeakAuras skips load-scanning anything with `controlledChildren`. Every leaf
carries its own `load.use_class`, and spec displays additionally carry
`load.use_spellknown`. `tests/run.py` fails the build if any leaf is ungated,
because an ungated pack loads on every character of every class — which is
exactly the bug that shipped in `final8`.

## Credits

Spell data is cached from db.exil.es, db.ascension.gg and ascensionsidekick.com
— see [NOTICE](NOTICE). Unofficial community tool, not affiliated with Blizzard
Entertainment.
