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


print()
if _fails:
    print(f"{len(_fails)} FAILED: {', '.join(_fails)}")
    raise SystemExit(1)
print("all checks passed")
