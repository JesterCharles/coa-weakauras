"""Fetch the real name + icon for each spell id the pack uses, from db.exil.es."""
import json, os, re, subprocess
from concurrent.futures import ThreadPoolExecutor

SP = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(SP, "spellchk")
os.makedirs(CACHE, exist_ok=True)


def fetch(sid):
    p = os.path.join(CACHE, f"{sid}.json")
    if not (os.path.exists(p) and os.path.getsize(p) > 400):
        payload = json.dumps({"url": f"https://db.exil.es/spell/{sid}",
                              "formats": ["markdown", "rawHtml"],
                              "waitFor": 4000, "timeout": 60000})
        subprocess.run(["curl", "-s", "-X", "POST",
                        "http://localhost:3002/v1/scrape",
                        "-H", "Content-Type: application/json",
                        "-d", payload, "-o", p], check=True, timeout=180)
    try:
        d = json.load(open(p))["data"]
    except Exception:
        return sid, None, None
    title = (d.get("metadata") or {}).get("title", "") or ""
    name = title.replace("coa-db —", "").strip() or None
    h = d.get("rawHtml", "") or ""
    m = re.search(r'/icons-clean/([^"\')]+?)\.png', h)
    return sid, name, (m.group(1) if m else None)


if __name__ == "__main__":
    ids = json.load(open(os.path.join(SP, "pack-ids.json")))
    out = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for sid, name, icon in ex.map(fetch, ids):
            out[sid] = {"name": name, "icon": icon}
            print(f"{sid:>8} {str(name)[:34]:<36} {icon}")
    json.dump(out, open(os.path.join(SP, "exiles-id-meta.json"), "w"), indent=1)
    miss = [k for k, v in out.items() if not v["icon"]]
    print(f"\n{len(out)} fetched, {len(miss)} without icon: {miss}")
