"""Regression checks for the CoA WeakAura toolchain.

    python3 tests/run.py

Stdlib only -- no pytest, no venv, no dependencies. Run it after every change
to the builder or the engine.

The checks, and what each is actually protecting:

  1. Runemaster rebuilds to the frozen fixture, all four packs.
     THE refactor gate. If this passes, the extraction preserved the pack.

  2-6. The comparator is honest -- five mutations it MUST catch.
     A comparator that cannot fail is decoration, and would silently bless a
     broken pack. These test the test.

  7. Every leaf carries a spellknown gate.
     `use_class` is inert on this fork, so a leaf without `use_spellknown`
     loads on every character of every class.

  8. No repeated icon art within a row.
     Two identical icons side by side means an id resolved to the wrong art.
"""
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

PACKS = [
    (None, "runemaster-all-specs"),
    ("glyphic", "runemaster-glyphic"),
    ("engravement", "runemaster-engravement"),
    ("riftblade", "runemaster-riftblade"),
]

_fails = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        if detail:
            for line in str(detail).splitlines()[:12]:
                print(f"          {line}")
        _fails.append(name)


def build(spec):
    env = dict(os.environ)
    env.pop("WA_SPEC", None)
    env.pop("WA_GLOW", None)
    if spec:
        env["WA_SPEC"] = spec
    r = subprocess.run([sys.executable, "build_runemaster.py"],
                       cwd=TOOLS, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"build failed (WA_SPEC={spec}):\n{r.stdout}{r.stderr}")
    return r.stdout


# --------------------------------------------------------------- 1. rebuild
print("\n1. rebuild matches frozen fixture")
built = {}
for spec, name in PACKS:
    out = build(spec)
    path = os.path.join(TOOLS, f"{name}.txt")
    built[name] = out
    fixture = os.path.join(FIXTURES, f"{name}.txt")
    if not os.path.exists(fixture):
        check(f"{name}: fixture exists", False,
              f"missing {fixture} -- run tests/freeze.py to create it")
        continue
    d = diff_files(fixture, path)
    check(f"{name} ({len(displays(load(path)))} displays)", not d, "\n".join(d))


# ------------------------------------------------- 2-6. comparator honesty
print("\n2-6. comparator catches mutations")
base_path = os.path.join(TOOLS, "runemaster-all-specs.txt")
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
    first_leaf(p)["parent"] = "RM Core"


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
CLASS_TOKEN = "SPIRITMAGE"
for spec, name in PACKS:
    pack = load(os.path.join(TOOLS, f"{name}.txt"))
    leaves = [d for d in pack["c"].values() if not d.get("controlledChildren")]

    # class gate on EVERY leaf, always. Without it the pack loads on every
    # character of every class.
    bad = [d["id"] for d in leaves
           if not d.get("load", {}).get("use_class")
           or d.get("load", {}).get("class", {}).get("single") != CLASS_TOKEN]
    check(f"{name}: {len(leaves)} leaves class-gated", not bad, "\n".join(bad[:8]))

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
        check(f"{name}: Core class-wide ({len(core)}), spec leaves gated ({len(specd)})",
              len(core) == 17 and len(specd) == len(leaves) - 17,
              f"expected 17 Core leaves, got {len(core)}")


# -------------------------------------------------------------- 8. icon art
print("\n8. no repeated icon art within a row")
for spec, name in PACKS:
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


for spec, name in PACKS:
    pack = load(os.path.join(TOOLS, f"{name}.txt"))
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
    unguarded = []
    for d in cds:
        conds = d.get("conditions") or {}
        vals = list(conds.values()) if isinstance(conds, dict) else list(conds)
        for c in vals:
            chk = c.get("check") or {}
            if chk.get("variable") == "expirationTime":
                unguarded.append(d["id"])
                break
    check(f"{name}: no bare expirationTime tier", not unguarded,
          "\n".join(unguarded[:8]))


# --------------------------------------------------------------- 10. off-GCD
print("\n10. off-GCD abilities do not show the global cooldown")

COOLDOWNS = json.load(open(os.path.join(ROOT, "resources",
                                        "cooldown-abilities.json")))
OFF_GCD = {n for n, v in COOLDOWNS.items() if v.get("gcd") is False}


def showgcd_of(d):
    trs = d.get("triggers") or {}
    vals = list(trs.values()) if isinstance(trs, dict) else list(trs)
    for t in vals:
        if isinstance(t, dict):
            tr = t.get("trigger")
            if isinstance(tr, dict) and "use_showgcd" in tr:
                return bool(tr["use_showgcd"])
    return None


for spec, name in PACKS:
    pack = load(os.path.join(TOOLS, f"{name}.txt"))
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


print()
if _fails:
    print(f"{len(_fails)} FAILED: {', '.join(_fails)}")
    raise SystemExit(1)
print("all checks passed")
