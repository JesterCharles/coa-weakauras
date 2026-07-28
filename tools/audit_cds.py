"""Find every Runemaster ability that has a cooldown, and which spec owns it."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

SP = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(SP, "spellchk")
EX = json.load(open(f"{SP}/exiles-runemaster.json"))
SKILLS = {r["name"] for r in json.load(open(f"{SP}/coa-runemaster-skills.json"))}
SB = os.path.expanduser("~/second-brain/projects/coa-weakauras/resources")
SIDEKICK = {s: open(f"{SB}/sidekick-runemaster-{s}.md").read()
            for s in ("glyphic", "engravement", "riftblade")}

# Player-facing abilities: anything coabuildhub lists, PLUS anything Sidekick
# mentions by name. coabuildhub's 150 is incomplete (no Zenith, Hurricane,
# Convergence, Runic Tempest...), so intersecting on it alone hides real
# cooldowns.
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
            return name, sid, None
    try:
        md = json.load(open(p))["data"].get("markdown") or ""
    except Exception:
        return name, sid, None
    md = re.sub(r"\s+", " ", md)
    m = re.search(r"Cooldown \| ([^|]+?)\|", md)
    return name, sid, (m.group(1).strip() if m else None)


if __name__ == "__main__":
    out = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, sid, cd in ex.map(fetch, sorted(cands.items())):
            if cd:
                specs = [s for s, t in SIDEKICK.items() if name in t]
                out[name] = {"id": sid, "cd": cd, "specs": specs}
    json.dump(out, open(f"{SP}/cooldown-abilities.json", "w"), indent=1)
    print(f"{len(cands)} abilities checked, {len(out)} have a cooldown\n")
    for n, v in sorted(out.items()):
        print(f"  {n:<28} id={v['id']:<8} {v['cd']:<20} {','.join(v['specs']) or 'shared/none'}")
