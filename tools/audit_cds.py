"""Find every ability of a class that has a cooldown, which spec owns it, and
whether it triggers the global cooldown.

    python3 audit_cds.py                 # runemaster (default)
    python3 audit_cds.py chronomancer    # any class in classes.py

Needs Firecrawl up at localhost:3002. Pages cache to tools/spellchk/ keyed by
spell id, so reruns are free and a partial run can simply be repeated.

The GCD half matters because WeakAuras cannot work it out. `use_showgcd`
substitutes the tracked global for ANY spell not already on cooldown
(`GenericTrigger.lua:2795`), with no per-spell knowledge, so an off-GCD ability
sweeps every time you press something else. The only fix is telling the builder
which abilities those are, and this is where that comes from.

db.exil.es renders a `GCD` row on the spell page when the spell is on the
global, and OMITS the row entirely when it is not. That absence is the signal
-- see `notes/off-gcd-detection.md`.
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

from classes import get, data, SP

CACHE = os.path.join(SP, "spellchk")

CLS = get(sys.argv[1] if len(sys.argv) > 1 else "runemaster")

for f in (CLS.exiles, CLS.skills):
    if not os.path.exists(data(f)):
        raise SystemExit(
            f"missing {f} -- scrape it first, see notes/class-pack-process.md "
            f"section 2")

EX = json.load(open(data(CLS.exiles)))
SKILLS = {r["name"] for r in json.load(open(data(CLS.skills)))}
SIDEKICK = {}
for s in CLS.specs:
    p = data(CLS.sidekick(s))
    if os.path.exists(p):
        SIDEKICK[s] = open(p).read()
if not SIDEKICK:
    raise SystemExit(f"no sidekick pages for {CLS.name} -- expected "
                     f"{CLS.sidekick(CLS.specs[0])} etc in resources/")

# Player-facing abilities: anything coabuildhub lists, PLUS anything Sidekick
# mentions by name. coabuildhub's list is incomplete (for Runemaster it missed
# Zenith, Hurricane, Convergence, Runic Tempest...), so intersecting on it
# alone hides real cooldowns.
ALLSK = "\n".join(SIDEKICK.values())
cands = {}
for n, v in EX.items():
    if len(n) < 4 or "DEPRECATED" in n or "unused" in n.lower():
        continue
    if n in SKILLS or n in ALLSK:
        cands[n] = v["ids"][0]


def fetch(item):
    name, sid = item
    p = os.path.join(CACHE, f"{sid}.json")
    if not (os.path.exists(p) and os.path.getsize(p) > 400):
        payload = json.dumps({"url": f"https://db.exil.es/spell/{sid}",
                              "formats": ["markdown"], "waitFor": 3000,
                              "timeout": 45000})
        try:
            subprocess.run(["curl", "-s", "-X", "POST",
                            "http://localhost:3002/v1/scrape",
                            "-H", "Content-Type: application/json",
                            "-d", payload, "-o", p], check=True, timeout=120)
        except Exception:
            return name, sid, None, None
    try:
        md = json.load(open(p))["data"].get("markdown") or ""
    except Exception:
        return name, sid, None, None
    md = re.sub(r"\s+", " ", md)

    # A page that did not render has no GCD row either, and would otherwise be
    # indistinguishable from a genuinely off-GCD ability. The Spell ID row is
    # on every real page, so it is the proof the scrape actually landed.
    # Without it we return gcd=None (unknown) rather than False (off-GCD).
    ok = re.search(r"Spell ID \| \d+", md) is not None

    m = re.search(r"Cooldown \| ([^|]+?)\|", md)
    cd = m.group(1).strip() if m else None

    g = re.search(r"GCD \| ([^|]+?)\|", md)
    gcd = g.group(1).strip() if g else (False if ok else None)
    return name, sid, cd, gcd


if __name__ == "__main__":
    os.makedirs(CACHE, exist_ok=True)
    print(f"{CLS.name} (class {CLS.id}) -- {len(cands)} candidate abilities\n")
    out, unknown = {}, []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, sid, cd, gcd in ex.map(fetch, sorted(cands.items())):
            if cd:
                specs = [s for s, t in SIDEKICK.items() if name in t]
                rec = {"id": sid, "cd": cd, "specs": specs}
                # `gcd` is the rendered value ("1.0 sec") when the ability is
                # on the global, False when the page proved it is not, and
                # omitted when the scrape could not settle it. The builder
                # treats only an explicit False as off-GCD.
                if gcd is None:
                    unknown.append(name)
                else:
                    rec["gcd"] = gcd
                out[name] = rec
    json.dump(out, open(data(CLS.cooldowns), "w"), indent=1)

    off = sorted(n for n, v in out.items() if v.get("gcd") is False)
    print(f"{len(cands)} abilities checked, {len(out)} have a cooldown")
    print(f"{len(off)} are OFF the global cooldown, {len(unknown)} unresolved\n")
    for n, v in sorted(out.items()):
        g = v.get("gcd", "?")
        g = "OFF-GCD" if g is False else ("unknown" if g == "?" else g)
        print(f"  {n:<28} id={v['id']:<8} {v['cd']:<20} {g:<10} "
              f"{','.join(v['specs']) or 'shared/none'}")
    if unknown:
        print("\nUNRESOLVED (scrape did not land, rerun to settle):")
        for n in unknown:
            print(f"  {n}")
    print(f"\nwrote {CLS.cooldowns}")
