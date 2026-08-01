"""Regression checks for the CoA WeakAura toolchain.

    python3 tests/run.py

Stdlib only -- no pytest, no venv, no dependencies. Run it after every change
to the builder or the engine.

Class-driven: every class with a `build_<slug>.py` in tools/ is picked up
automatically from classes.py, so a new class inherits the whole suite by
existing. There is no per-class test to remember to write.

The checks, and what each is actually protecting:

  1. Every class rebuilds to its frozen fixture, all packs.
     THE refactor gate. If this passes, the change preserved the packs.

  2-6. The comparator is honest -- five mutations it MUST catch.
     A comparator that cannot fail is decoration, and would silently bless a
     broken pack. These test the test.

  7. Load gates: class token on every leaf, spec gating on spec packs.
     The token comes from resources/class-tokens.md and is NOT derivable from
     the class name (Runemaster is SPIRITMAGE, Templar is MONK). `use_class`
     does work -- an early result suggesting otherwise was a stale
     SavedVariables state on the client, not the condition.

  8. No repeated icon art within a row.
     Two identical icons side by side means an id resolved to the wrong art.

  9. Readiness. Every spell cooldown icon desaturates on `spellUsable == 0`,
     and no escalation tier reads a bare `expirationTime` (which would fire on
     every global cooldown -- that shipped once as final12).

 10. Off-GCD. WeakAuras substitutes the tracked global for any spell not
     already on cooldown, blindly (GenericTrigger.lua:2795), so an off-GCD
     ability must not carry `use_showgcd` -- and an on-GCD one must. Which is
     which is scraped into cooldown-abilities-<class>.json, never guessed.

 11. Merging the per-spec bands into shared ones lost nothing: loading the
     all-specs pack as a given spec yields exactly the displays that spec's
     own pack contains.

     KNOWN LIMIT: both sides come from the SAME builder, so a bug in logic
     they share moves both together and cancels out. It catches the merge
     path diverging from the per-spec filter path, NOT an ability leaking to
     a spec that cannot cast it -- that one is asserted in the builder's
     assert_gated(), where the spec membership actually exists.
"""
import collections
import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
FIXTURES = os.path.join(HERE, "fixtures")

sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)

from compare import diff, diff_files, load, displays, normalise  # noqa: E402
from classes import built as built_classes, data as class_data  # noqa: E402

# Every class with a builder on disk. Checks 1 and 7-10 run against all of
# them, so a new class inherits the whole suite by existing -- there is no
# per-class test to remember to write. Checks 2-6 test the comparator itself
# and only need one pack.
UNDER_TEST = built_classes()
if not UNDER_TEST:
    raise SystemExit("no class builders found in tools/")
PACKS = [(cls, spec, name) for cls in UNDER_TEST for spec, name in cls.packs]

_fails = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        if detail:
            for line in str(detail).splitlines()[:12]:
                print(f"          {line}")
        _fails.append(name)


def build(cls, spec):
    env = dict(os.environ)
    env.pop("WA_SPEC", None)
    env.pop("WA_GLOW", None)
    if spec:
        env["WA_SPEC"] = spec
    r = subprocess.run([sys.executable, cls.builder],
                       cwd=TOOLS, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(
            f"{cls.builder} failed (WA_SPEC={spec}):\n{r.stdout}{r.stderr}")
    return r.stdout


# --------------------------------------------------------------- 1. rebuild
print("\n1. rebuild matches frozen fixture")
built = {}
for cls, spec, name in PACKS:
    out = build(cls, spec)
    path = cls.pack_path(name)
    built[name] = out
    fixture = os.path.join(FIXTURES, f"{name}.txt")
    if not os.path.exists(fixture):
        check(f"{name}: fixture exists", False,
              f"missing {fixture} -- run tests/freeze.py to create it")
        continue
    d = diff_files(fixture, path)
    check(f"{name} ({len(displays(load(path)))} displays)", not d, "\n".join(d))


# ------------------------------------------------- 2-6. comparator honesty
# These test the comparator, not any class, so one pack is enough -- the first
# built class's all-specs pack.
print("\n2-6. comparator catches mutations")
base_path = UNDER_TEST[0].pack_path(UNDER_TEST[0].packs[0][1])
base = load(base_path)


def mutated(fn):
    m = copy.deepcopy(base)
    fn(m)
    return diff(base, m)


def first_leaf(pack):
    for d in pack["c"].values():
        if not d.get("controlledChildren"):
            return d
    raise AssertionError("no leaf found")


def first_group(pack):
    for d in pack["c"].values():
        cc = d.get("controlledChildren")
        if cc and len(cc) > 1:
            return d
    raise AssertionError("no multi-child group found")


def m_anchor(p):
    first_leaf(p)["yOffset"] = -9999


def m_drop_trigger(p):
    d = first_leaf(p)
    t = d["triggers"]
    for k in list(t):
        if isinstance(k, int):
            del t[k]
            return


def m_reparent(p):
    # move a leaf under some OTHER existing group, whichever the pack has --
    # hardcoding a group id would tie this mutation to one class.
    leaf = first_leaf(p)
    other = next(d["id"] for d in p["c"].values()
                 if d.get("controlledChildren") and d["id"] != leaf.get("parent"))
    leaf["parent"] = other


def m_reorder(p):
    g = first_group(p)
    cc = g["controlledChildren"]
    keys = sorted(k for k in cc if isinstance(k, int))
    cc[keys[0]], cc[keys[1]] = cc[keys[1]], cc[keys[0]]


def m_gate(p):
    first_leaf(p)["load"]["spellknown"] = 1


check("band anchor moved", bool(mutated(m_anchor)))
check("trigger dropped", bool(mutated(m_drop_trigger)))
check("display reparented", bool(mutated(m_reparent)))
check("row order swapped", bool(mutated(m_reorder)))
check("load gate changed", bool(mutated(m_gate)))

# and the inverse: an identical copy must NOT diff
check("identical copy reports no diff", not diff(base, copy.deepcopy(base)))
# volatile fields must be ignored
def m_uid(p):
    first_leaf(p)["uid"] = "totally-different-uid"
check("uid change ignored", not mutated(m_uid))


# ------------------------------------------------------------- 7. load gates
print("\n7. load gates")
for cls, spec, name in PACKS:
    pack = load(cls.pack_path(name))
    leaves = [d for d in pack["c"].values() if not d.get("controlledChildren")]

    # class gate on EVERY leaf, always. Without it the pack loads on every
    # character of every class. The token is NOT derivable from the class name
    # -- Runemaster is SPIRITMAGE, Templar is MONK -- so it comes from
    # resources/class-tokens.md via classes.py, never from a guess.
    bad = [d["id"] for d in leaves
           if not d.get("load", {}).get("use_class")
           or d.get("load", {}).get("class", {}).get("single") != cls.token]
    check(f"{name}: {len(leaves)} leaves class-gated to {cls.token}",
          not bad, "\n".join(bad[:8]))

    if spec:
        # a spec-scoped pack must narrow every leaf, Core included -- else the
        # Riftblade-only pack's alerts show while you are playing Glyphic.
        bad = [d["id"] for d in leaves
               if not d.get("load", {}).get("use_spellknown")
               or not d.get("load", {}).get("spellknown")]
        check(f"{name}: all leaves spec-gated", not bad, "\n".join(bad[:8]))
    else:
        # the all-specs pack keeps Core class-wide on purpose: engravings and
        # etchings apply to the whole class, and gating them on a spell would
        # break them for a levelling character who has not learned it yet.
        core = [d for d in leaves if not d.get("load", {}).get("use_spellknown")]
        specd = [d for d in leaves if d.get("load", {}).get("use_spellknown")]
        # "class-wide" now covers two legitimate cases: Core (engravings,
        # etchings, reminders -- deliberately not spell-gated so a levelling
        # character still gets them), AND abilities all specs share that live
        # in a merged band. The latter are active-only aura displays, which
        # are self-gating: they cannot show unless the buff is actually up, and
        # a buff id is not something IsSpellKnown would recognise anyway.
        want = cls.core_leaves
        if want is None:
            # class not yet pinned in classes.CORE_LEAVES -- assert the shape
            # (some Core, some spec-gated) and report the number to record.
            check(f"{name}: Core class-wide ({len(core)}), spec leaves gated "
                  f"({len(specd)}) -- add core_leaves={len(core)} to "
                  f"classes.CORE_LEAVES to pin it",
                  bool(core) and bool(specd),
                  "expected a mix of Core and spec-gated leaves")
        else:
            check(f"{name}: Core class-wide ({len(core)}), spec leaves gated ({len(specd)})",
                  len(core) == want and len(specd) == len(leaves) - want,
                  f"expected {want} Core leaves, got {len(core)}")


# -------------------------------------------------------------- 8. icon art
print("\n8. no repeated icon art within a row")
for cls, spec, name in PACKS:
    ok = "no repeated icon art within any row" in built[name]
    check(f"{name}", ok, built[name])


# ------------------------------------------------------------- 9. readiness
print("\n9. every spell cooldown icon shows readiness")


def cd_triggered(pack):
    """Leaves whose FIRST trigger is a spell cooldown -- i.e. cd_icon output.

    Aura, enchant and custom-Lua leaves are excluded: `spellUsable` lives on
    the spell cooldown prototype and means nothing on the others.
    """
    out = []
    for d in pack["c"].values():
        if d.get("controlledChildren") or d.get("regionType") != "icon":
            continue
        trs = d.get("triggers") or {}
        vals = list(trs.values()) if isinstance(trs, dict) else list(trs)
        for t in vals:
            if not isinstance(t, dict):
                continue
            tr = t.get("trigger")
            if isinstance(tr, dict) and tr.get("event") == "Cooldown Progress (Spell)":
                out.append(d)
            break
    return out


def has_usable_cond(d):
    conds = d.get("conditions") or {}
    vals = list(conds.values()) if isinstance(conds, dict) else list(conds)
    for c in vals:
        if not isinstance(c, dict):
            continue
        if (c.get("check") or {}).get("variable") == "spellUsable":
            return True
    return False


for cls, spec, name in PACKS:
    pack = load(cls.pack_path(name))
    cds = cd_triggered(pack)
    # A cooldown icon that is off cooldown but uncastable -- no mana, no
    # resource, wrong form -- reads as "press me" with nothing to say
    # otherwise. The swipe cannot show it; only `spellUsable` can.
    bad = [d["id"] for d in cds if not has_usable_cond(d)]
    check(f"{name}: {len(cds)} cooldown icons desaturate when unusable",
          cds and not bad, "\n".join(bad[:8]))

    # The GCD is reported by the same trigger (use_showgcd), so any urgency
    # tier keyed on bare expirationTime fires on every global, on every icon
    # in the row. That shipped once as final12; it must not ship again.
    def _trigger_type(d, idx):
        """Type of trigger `idx` (1-based) on display `d`."""
        trs = d.get("triggers") or {}
        t = trs.get(idx) if isinstance(trs, dict) else None
        if not isinstance(t, dict):
            return None
        tr = t.get("trigger")
        return tr.get("type") if isinstance(tr, dict) else None

    unguarded = []
    for d in cds:
        conds = d.get("conditions") or {}
        vals = list(conds.values()) if isinstance(conds, dict) else list(conds)
        for c in vals:
            chk = c.get("check") or {}
            if chk.get("variable") != "expirationTime":
                continue
            # Scope to the SPELL cooldown trigger, which is the only place the
            # bug lives: use_showgcd makes that trigger report the global, so a
            # bare tier there fires on every icon on every global (final12).
            #
            # The same variable on an AURA trigger is just the aura's remaining
            # time -- no global to contaminate it -- and is how the refresh
            # cues work (chronomancer-nnoop's Ripple does exactly this). A
            # check that cannot tell them apart forbids a correct mechanism.
            if _trigger_type(d, chk.get("trigger")) != "spell":
                continue
            unguarded.append(d["id"])
            break
    check(f"{name}: no bare expirationTime tier", not unguarded,
          "\n".join(unguarded[:8]))


# --------------------------------------------------------------- 10. off-GCD
print("\n10. off-GCD abilities do not show the global cooldown")

def off_gcd_for(cls):
    """Ability names this class's scrape proved are off the global.

    Only an explicit `gcd: false` counts. A missing key means audit_cds.py
    could not settle it, and treating unknown as off-GCD would silently drop
    the anti-clipping cue on an ability that does obey the global.
    """
    p = class_data(cls.cooldowns)
    if not os.path.exists(p):
        return None
    cd = json.load(open(p))
    return {n for n, v in cd.items() if v.get("gcd") is False}


def showgcd_of(d):
    trs = d.get("triggers") or {}
    vals = list(trs.values()) if isinstance(trs, dict) else list(trs)
    for t in vals:
        if isinstance(t, dict):
            tr = t.get("trigger")
            if isinstance(tr, dict) and "use_showgcd" in tr:
                return bool(tr["use_showgcd"])
    return None


for cls, spec, name in PACKS:
    OFF_GCD = off_gcd_for(cls)
    if OFF_GCD is None:
        check(f"{name}: {cls.cooldowns} exists", False,
              f"run: python3 tools/audit_cds.py {cls.slug}")
        continue
    pack = load(cls.pack_path(name))
    # `use_showgcd` makes WeakAuras substitute the tracked global for any spell
    # not already on cooldown -- blindly, with no per-spell knowledge
    # (GenericTrigger.lua:2795). On an ability that does not obey the global
    # that is a phantom sweep every time you press something else. Which
    # abilities those are is scraped, not guessed: db.exil.es omits the GCD row
    # for them and audit_cds.py records it as `gcd: false`.
    wrong = []
    for d in cd_triggered(pack):
        # display ids are "RM <Spec> <Row> <Ability>"; match on suffix so the
        # check does not have to know the row naming.
        ability = next((a for a in OFF_GCD if d["id"].endswith(" " + a)), None)
        if ability and showgcd_of(d) is not False:
            wrong.append(f"{d['id']} (off-GCD, but use_showgcd is on)")
    check(f"{name}: no off-GCD ability shows the global", not wrong,
          "\n".join(wrong[:8]))

    # The converse: a GCD-obeying ability that lost the flag silently drops the
    # anti-clipping cue, which is the whole reason showgcd is on by default.
    missing = []
    for d in cd_triggered(pack):
        if any(d["id"].endswith(" " + a) for a in OFF_GCD):
            continue
        if showgcd_of(d) is False:
            missing.append(f"{d['id']} (on-GCD, but use_showgcd is off)")
    check(f"{name}: every on-GCD ability keeps the sweep", not missing,
          "\n".join(missing[:8]))



# ------------------------------------------------- 11. merge preserves content
print("\n11. merged pack loads exactly what each spec's own pack contains")
SIG_TO_SPEC = {}
for cls in UNDER_TEST:
    allspecs = cls.pack_path(cls.packs[0][1])
    # map each spec's signature spell id from its own pack: every leaf there is
    # gated on it, so the most common spellknown value IS the signature.
    sig = {}
    for spec, name in cls.packs[1:]:
        pack = load(cls.pack_path(name))
        vals = collections.Counter(
            d.get("load", {}).get("spellknown")
            for d in pack["c"].values()
            if not d.get("controlledChildren")
            and d.get("load", {}).get("use_spellknown"))
        vals.pop(None, None)
        if vals:
            sig[vals.most_common(1)[0][0]] = spec

    def norm(i):
        for p in [f"RM {s.title()} " for _, s in cls.packs[1:]] + ["RM "]:
            if i.startswith(p):
                return i[len(p):]
        return i

    def content(path, spec=None):
        out = set()
        for d in load(path)["c"].values():
            if d.get("controlledChildren"):
                continue
            if spec:
                ld = d.get("load", {})
                sk = ld.get("spellknown") if ld.get("use_spellknown") else None
                if sk in sig and sig[sk] != spec:
                    continue
            out.add(norm(d["id"]))
        return out

    for spec, name in cls.packs[1:]:
        label = sig.get(next((k for k, v in sig.items() if v == spec), None), spec)
        merged = content(allspecs, spec)
        own = content(cls.pack_path(name))
        # Merging the per-spec bands into shared ones must not lose or add a
        # single display. The per-spec pack is the ground truth for what one
        # spec needs; loading the merged pack as that spec must match it
        # exactly.
        detail = ""
        if own - merged:
            detail += "missing: " + ", ".join(sorted(own - merged)[:6]) + "\n"
        if merged - own:
            detail += "extra: " + ", ".join(sorted(merged - own)[:6])
        check(f"{name}: merged pack loads the same {len(own)} displays",
              own == merged, detail)


# ----------------------------------------------- 12. changelog watcher parse
#
# Against a COMMITTED fixture, never the live page. The watcher's whole job is
# to notice when ascension.gg changes, so a test that fetches it would go red
# for the thing the tool exists to report -- and would go red on a train.
print("\n12. changelog watcher parses the committed fixture")
sys.path.insert(0, TOOLS)
import changelog_watch as CW  # noqa: E402

_FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "fixtures", "changelog-section4-page1.html")
if not os.path.exists(_FIX):
    check("changelog fixture present", False, _FIX)
else:
    _entries = CW.parse(open(_FIX, encoding="utf-8").read())

    check(f"parses {len(_entries)} entries", len(_entries) == 100,
          f"expected 100 entries on a full page, got {len(_entries)}")

    # Every entry must land under a date. A None date means the header-offset
    # binding broke, which would silently make every entry undateable and
    # therefore unable to invalidate a citation.
    _undated = [e for e in _entries if not e["date"]]
    check("every entry binds to a date header", not _undated,
          f"{len(_undated)} undated, first: {_undated[0]['text'][:70]}"
          if _undated else "")

    # The two tag shapes that an exact-match parser drops silently.
    check("a misspelled class tag still resolves",
          CW.tag_to_slug("Strombringer") == ("stormbringer", None, True),
          f'got {CW.tag_to_slug("Strombringer")}')
    check("a class-and-spec tag resolves to both",
          CW.tag_to_slug("Witch Hunter - Inquisition")
          == ("witch-hunter", "inquisition", True),
          f'got {CW.tag_to_slug("Witch Hunter - Inquisition")}')

    # An unknown tag must report as unrecognised rather than resolving to
    # something. Silently attributing it to the wrong class is worse than
    # saying "I do not know what this is".
    check("an unknown tag is not attributed",
          CW.tag_to_slug("Nonsense Class")[2] is False)

    # Nothing in the fixture should be unattributable: every tag on it is
    # either a known class or a known non-class. If this fails, the fixture
    # was refreshed and a new tag appeared -- add it, do not ignore it.
    _unknown = sorted({e["tag"] for e in _entries
                       if e["tag"] and not e["recognised"]
                       and e["tag"].strip().lower() not in CW.NON_CLASS_TAGS})
    check("no unattributable tags in the fixture", not _unknown,
          "unrecognised: " + ", ".join(_unknown) if _unknown else "")

    # The hash keys on attributed text, so re-tagging a typo is not "new".
    check("re-tagging a typo does not read as a new entry",
          CW.parse('<p class="text-neutral-300">[Strombringer] X.</p>'
                   )[0]["hash"]
          == CW.parse('<p class="text-neutral-300">[Stormbringer] X.</p>'
                      )[0]["hash"])

    # The known drift this tool was written for. If the fixture ever stops
    # carrying it, the fixture was replaced and this test is meaningless.
    _rm = [e for e in _entries if e["slug"] == "runemaster"]
    check(f"finds the {len(_rm)} Runemaster entries that postdate its 1.0",
          len(_rm) == 9, f"expected 9, got {len(_rm)}")


# ------------------------------ 13. every rendered ability has an inventory row
#
# The coverage floor, and the one direction the scrapes cannot cover. The
# skillbook and the cooldown audit are both somebody else's page; a pack cannot
# reference an ability it does not have. Runemaster shipped with 150 skillbook
# entries that omitted Runeblade and Runic Explosion while rendering both, and
# coverage measured against that inventory read 100%.
#
# Judged on triggers, not display ids: a resource bar has no ability behind it
# and must not be counted, or the number never reaches zero and stops meaning
# anything.
def _rows_of(path):
    """{ability: cells} from an inventory table."""
    out = {}
    for line in open(path, encoding="utf-8"):
        if line.startswith("| ") and line.count("|") >= 6:
            c = [x.strip() for x in line.split("|")[1:-1]]
            if c[0] and c[0] != "Ability" and set(c[0]) != {"-"}:
                out[c[0]] = c
    return out


# NOTE pack_refs reads docs/packs/ -- the PUBLISHED copy, which mksite.py
# writes. The builder writes tools/packs/, so a rebuild alone leaves this
# reading the previous release. Run mksite.py before trusting a result here.
print("\n13. every ability the pack renders has an inventory row")
import json as _json  # noqa: E402
import mkabilities as MK  # noqa: E402

def _load(name):
    p = class_data(name)
    return _json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


for cls in UNDER_TEST:
    inv_path = class_data(f"abilities-{cls.slug}.md")
    if not os.path.exists(inv_path):
        check(f"{cls.slug}: inventory exists", False, inv_path)
        continue

    known = set(MK.read(inv_path))
    refs = MK.pack_refs(cls, _load(cls.exiles),
                        _load(f"spell-meta-{cls.slug}.json"))
    # The reverse direction, for the one role that is NOT derived. Offensive,
    # defensive and utility rows reach the pack through _named(), so assigning
    # one has a visible effect. The TARGET band is a hand-written list in the
    # builder, so `role: target` on a row does nothing at all unless somebody
    # also edits that list -- a silent no-op, and exactly how Shifting Sands
    # sat assigned-but-invisible until this check existed.
    drawn = {n for r in refs.values() for n in r}
    inert = sorted(n for n, cells in _rows_of(inv_path).items()
                   if "target" in cells[3] and n not in drawn)
    check(f"{cls.slug}: every `target` row actually renders", not inert,
          "assigned target but drawn nowhere -- add it to the dot_bars() list "
          "in the builder: " + ", ".join(inert))

    missing = {d: r for d, r in refs.items() if r and not (r & known)}
    detail = "\n".join(f"{d} -> {', '.join(sorted(r)[:4])}"
                       for d, r in sorted(missing.items()))
    check(f"{cls.slug}: {len(refs)} displays, all covered by the inventory",
          not missing, detail)


# ------------------------------------------- 14. the source policy gate holds
#
# Cheap to test and expensive to get wrong: the cost of fetching something an
# operator asked us not to fetch lands on their server, not ours.
print("\n14. external source policy gate")
import sources as SRC  # noqa: E402

check("an unlisted host is blocked, not allowed by default",
      not SRC.allowed("https://example.com/anything")[0])
check("a use=reference source is not fetchable",
      not SRC.allowed("https://coa.ascensionlogs.gg/api/home/phases")[0])
check("the changelog source is fetchable",
      SRC.allowed("https://ascension.gg/en/changelog/4")[0])
check("the sidekick bundle is fetchable",
      SRC.allowed("https://ascensionsidekick.com/data.js")[0])
check("www. and case do not change the answer",
      SRC.allowed("https://WWW.Ascension.gg/en/changelog/4")[0])
# A blocked answer that says nothing is a blocked answer someone overrides.
check("every refusal explains itself",
      all(len(SRC.allowed(u)[1]) > 60 for u in
          ("https://example.com/x",
           "https://coa.ascensionlogs.gg/api/home/phases")))
check("every declared source names what it is and when it was checked",
      all(s.get("what") and s.get("checked") for s in SRC.SOURCES.values()))


# ------------------------------------------------ 15. rotation citation corpus
print("\n15. rotation citations")
import citations as CIT  # noqa: E402

for cls in UNDER_TEST:
    cites = CIT.load(cls)
    names = CIT.inventory_names(cls)
    alias = CIT.load_aliases(cls)
    check(f"{cls.slug}: {len(cites)} citation(s) present", bool(cites),
          "no citations -- every priority this class renders is uncited")

    # Synthetic bad record: the validator must object to all five faults.
    bogus = {"x": {"class": cls.slug, "spec": "nope", "source": "evil.example",
                   "origin": "invalid", "retrieved_at": "2026-01-01",
                   "claims": {"priority": ["No Such Ability"], "junk": ["y"]}}}
    faults = {w for _, w in CIT.validate(cls, bogus, names)}
    check(f"{cls.slug}: validator rejects an unknown spec",
          any("unknown spec" in f for f in faults))
    check(f"{cls.slug}: validator rejects an undeclared source",
          any("not in sources.py" in f for f in faults))
    check(f"{cls.slug}: validator rejects an ability with no inventory row",
          any("no inventory row" in f for f in faults))
    check(f"{cls.slug}: validator rejects an unknown claim bucket",
          any("unknown claim bucket" in f for f in faults))

    # Structural faults in the REAL corpus are a build problem. A name that
    # does not resolve is NOT: it means a source disagrees with our inventory,
    # which is information to act on, not a broken tree. Surfaced, not failed --
    # the same treatment mkabilities gives its Candidates list.
    # An alias is only useful if it actually resolves. Build one synthetic
    # citation per alias and confirm the validator accepts it: a rename that
    # maps to a canonical row must pass, and a name recorded as unbuildable
    # (canonical: null) must NOT come back as an outstanding gap -- somebody
    # already looked, and rediscovering it every refresh is the failure.
    def _cite(n):
        return {"t": {"class": cls.slug, "spec": cls.specs[0],
                      "source": "ascensionsidekick.com", "origin": "scheduled",
                      "retrieved_at": "2026-01-01",
                      "claims": {"priority": [n]}}}

    for _name, _a in sorted(alias.items()):
        gaps = [w for _, w in CIT.validate(cls, _cite(_name), names, alias)
                if "no inventory row" in w]
        kind = ("unbuildable" if _a.get("canonical") is None
                else f"-> {_a['canonical']}")
        check(f"{cls.slug}: alias {_name!r} resolves ({kind})", not gaps,
              "; ".join(gaps))
    # An unaliased nonsense name must still be reported, or the alias file
    # would be hiding gaps rather than explaining them.
    check(f"{cls.slug}: an unaliased unknown name is still a gap",
          any("no inventory row" in w for _, w in
              CIT.validate(cls, _cite("Definitely Not An Ability"), names,
                           alias)))

    real = CIT.validate(cls, cites, names, alias)
    structural = [(c, w) for c, w in real if "no inventory row" not in w]
    check(f"{cls.slug}: every citation is structurally valid", not structural,
          "\n".join(f"{c}: {w}" for c, w in structural))
    unresolved = sorted({w.split("'")[1] for c, w in real
                         if "no inventory row" in w})
    if unresolved:
        print(f"          NOTE {cls.slug}: {len(unresolved)} cited name(s) "
              f"with no inventory row -- a source disagrees with us: "
              f"{', '.join(unresolved)}")


# ------------------------------------------------- 16. official talent trees
print("\n16. official talent tree vs inventory")
for cls in UNDER_TEST:
    tp = class_data(f"talents-{cls.slug}.json")
    if not os.path.exists(tp):
        check(f"{cls.slug}: talent tree extracted", False,
              f"{tp} missing -- run tools/talents.py {cls.slug}")
        continue
    tal = _json.load(open(tp, encoding="utf-8"))

    check(f"{cls.slug}: every spec resolved to a tree tab",
          not tal["missing_specs"],
          "unresolved: " + ", ".join(tal["missing_specs"]))

    inv = set(CIT.inventory_names(cls))
    granted = [n for group in list(tal["specs"].values()) + [tal["class_tab"]]
               for n in group if n["grants_ability"] and n["name"]]
    missing = sorted({n["name"] for n in granted if n["name"] not in inv})
    # The game's own tree is the strongest possible statement that an ability
    # exists. If it can grant a button we have no row for, that is a coverage
    # hole no scrape would report.
    check(f"{cls.slug}: all {len(granted)} talent-granted abilities tracked",
          not missing, "untracked: " + ", ".join(missing))

    # Regression guard on the flag that lies. isPassive reports 0 for 145 of
    # Runemaster's 160 nodes including pure stat passives; if a future edit
    # switches back to it, this catches the day it happens.
    raw = _json.load(open(class_data("talents-voljin.json"), encoding="utf-8"))
    rn = [n for k, v in raw["entriesByTab"].items()
          if k.startswith(f"{cls.id}:") for n in v]
    by_type = sum(1 for n in rn if n.get("entryType") == "Ability")
    by_flag = sum(1 for n in rn if not n.get("isPassive"))
    check(f"{cls.slug}: entryType and isPassive still disagree "
          f"({by_type} vs {by_flag}) -- isPassive stays unused",
          by_flag > by_type * 2)


# ------------------------------------------------------- 17. rankings records
#
# These name real players. A malformed record renders as confident nonsense
# about them, so the validator is stricter here than elsewhere and mksite drops
# the whole panel rather than publishing a half-broken one.
print("\n17. rankings records")
import rankings as RK  # noqa: E402

for cls in UNDER_TEST:
    rec = RK.load(cls)
    check(f"{cls.slug}: rankings record exists and validates",
          rec is not None and not RK.validate(cls, rec),
          "; ".join(RK.validate(cls, rec)) if rec else "no file")

    if rec is None:
        continue
    # Empty is a legitimate state and must stay distinguishable from broken:
    # Zul'Gurub released the day this shipped, so "nobody has cleared it" and
    # "we failed to collect" have to look different on the page.
    check(f"{cls.slug}: an empty record is valid, not an error",
          not RK.validate(cls, RK.blank(cls)))

    # Entries about named people without provenance is the fault worth
    # catching hardest.
    orphan = RK.blank(cls)
    orphan["categories"]["overall"]["entries"] = [dict(
        RK.TEMPLATE_ENTRY, spec=cls.specs[0])]
    check(f"{cls.slug}: entries without collected_at are rejected",
          any("collected_at" in p for p in RK.validate(cls, orphan)))

    bogus = RK.blank(cls)
    bogus["categories"]["overall"]["entries"] = [
        {"rank": 1, "character": "A", "spec": "not-a-spec",
         "build": {"status": "matches"}},
        {"rank": 1, "character": "B", "spec": cls.specs[0],
         "build": {"status": "invented"}}]
    bogus["collected_at"] = "2026-01-01"
    faults = " ".join(RK.validate(cls, bogus))
    check(f"{cls.slug}: rejects unknown spec, duplicate rank, bad status",
          "unknown spec" in faults and "twice" in faults
          and "build.status" in faults)

check("the rankings source is declared as link-only",
      SRC.SOURCES["coa.ascensionlogs.gg"]["policy"] == "reference")


# ------------------------------------------------- 18. publish gate
#
# docs/ IS the distribution -- Pages serves it, so copying a build in and
# committing is a release. Before this gate, regenerating the site shipped
# whatever had just been built and nothing recorded whether a human had seen it
# work; Chronomancer 1.1 went live with six untested displays that way.
print("\n18. verified-build record and publish gate")
import re  # noqa: E402
import verified as VER  # noqa: E402

_vrec = VER.load()
check("the verified-builds record parses", isinstance(_vrec, dict))

for cls in UNDER_TEST:
    ver = re.search(r'^VERSION = "([^"]+)"',
                    open(os.path.join(TOOLS, cls.builder),
                         encoding="utf-8").read(), re.M)
    ver = ver.group(1) if ver else "?"

    # Exact-match only. 1.0 being verified says nothing about 1.1 -- a version
    # bump exists precisely because the output changed.
    ok, _ = VER.status(cls, ver, _vrec)
    other = {cls.slug: {"0.0-not-this": {"specs": list(cls.specs),
                                         "verified_at": "2026-01-01"}}}
    check(f"{cls.slug}: a different recorded version does not count as this one",
          not VER.status(cls, ver, other)[0])

    # Every spec, because a pack can be right on one and wrong on another --
    # final8's ungated Core reminders looked fine on the spec that could
    # satisfy them.
    partial = {cls.slug: {ver: {"specs": [cls.specs[0]],
                                "verified_at": "2026-01-01"}}}
    check(f"{cls.slug}: a partial per-spec record does not count as verified",
          not VER.status(cls, ver, partial)[0])

    full = {cls.slug: {ver: {"specs": list(cls.specs),
                             "verified_at": "2026-01-01"}}}
    check(f"{cls.slug}: a complete record does count",
          VER.status(cls, ver, full)[0])

    # Whatever the live state is, the page must not claim more than the record
    # supports: unverified means the badge is present, verified means it is not.
    page = os.path.join(ROOT, "docs", cls.slug, "index.html")
    if os.path.exists(page):
        badged = "not verified in game" in open(page, encoding="utf-8").read()
        check(f"{cls.slug}: page badge matches the record "
              f"(v{ver} {'verified' if ok else 'unverified'})",
              badged != ok)


# --------------------------------------------- 19. the HUD preview lays out
#
# The site preview claims to be drawn to scale, so it has to be. hud.py
# simulates DynamicGroup.lua because a dynamic group stores (0,0) for every
# child and lays them out at runtime -- so any grow mode it does NOT simulate
# falls back to those zeroes and draws the whole band on one point.
#
# That is not hypothetical. GRID was documented as "a grow mode the packs do
# not use" and fell through; the moment CD_PER_ROW was wired to gridWidth the
# cooldown rows became GRID and every wrapped row on the published site
# collapsed into a pile, while the page still said drawn to scale.
print("\n19. HUD preview geometry")
import hud as HUD  # noqa: E402

for cls in UNDER_TEST:
    for spec in cls.specs:
        p = os.path.join(ROOT, "docs", "packs", cls.slug,
                         f"{cls.slug}-{spec}.txt")
        if not os.path.exists(p):
            continue
        items = HUD.displays(p, only_persistent=True)
        pos = [(round(d["x"], 2), round(d["y"], 2)) for d in items]
        dupes = {q for q in pos if pos.count(q) > 1}
        # Two displays at the identical resolved point means a band was not
        # laid out -- the exact signature of an unsimulated grow mode.
        check(f"{cls.slug}/{spec}: {len(items)} displays, none stacked",
              not dupes, f"{len(dupes)} shared position(s): "
                         f"{sorted(dupes)[:4]}")

# A wrapped band must actually occupy more than one row, or gridWidth is being
# read but not applied.
_p = os.path.join(ROOT, "docs", "packs", "chronomancer",
                  "chronomancer-artificer.txt")
if os.path.exists(_p):
    _items = HUD.displays(_p, only_persistent=True)
    _ys = {round(d["y"], 1) for d in _items}
    check(f"a wrapped pack occupies {len(_ys)} distinct rows, not 1",
          len(_ys) > 5, f"rows: {sorted(_ys)}")


print()
if _fails:
    print(f"{len(_fails)} FAILED: {', '.join(_fails)}")
    raise SystemExit(1)
print("all checks passed")
