"""Batch-search db.ascension.gg via local Firecrawl and extract spell listview rows."""
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

SP = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(SP, "dbcache")
os.makedirs(CACHE, exist_ok=True)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def fetch(url, key):
    path = os.path.join(CACHE, key + ".json")
    if os.path.exists(path) and os.path.getsize(path) > 500:
        return path
    payload = json.dumps({"url": url, "formats": ["rawHtml"], "waitFor": 5000})
    subprocess.run(
        ["curl", "-s", "-X", "POST", "http://localhost:3002/v1/scrape",
         "-H", "Content-Type: application/json", "-d", payload, "-o", path],
        check=True, timeout=300)
    return path


def rows(path):
    try:
        h = json.load(open(path))["data"]["rawHtml"]
    except Exception:
        return []
    out = []
    for m in re.finditer(r'new Listview\(\{"template":"spell".*?"data":(\[.*?\]),"name"', h, re.S):
        try:
            out += json.loads(m.group(1))
        except Exception:
            pass
    return out


def search(name):
    key = "s-" + slug(name)
    p = fetch(f"https://db.ascension.gg/?search={name.replace(' ', '+')}", key)
    return name, rows(p)


if __name__ == "__main__":
    names = json.load(open(sys.argv[1]))
    res = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for name, rs in ex.map(search, names):
            seen = {}
            for r in rs:
                nm = r["name"].lstrip("@")
                if nm.lower() != name.lower() and name.lower() not in nm.lower():
                    continue
                seen.setdefault(r["id"], {
                    "id": r["id"], "name": nm, "icon": r["icon"],
                    "level": r["level"], "rank": r.get("rank", ""),
                    "advClass": r.get("advClass"), "advTab": r.get("advTab"),
                    "isCoa": r.get("isCoaClass"), "skill": r.get("skill"),
                    "school": r.get("school"), "advType": r.get("advType"),
                })
            res[name] = sorted(seen.values(), key=lambda x: x["id"])
            print(f"{name:<26} {len(res[name])} hits", file=sys.stderr)
    json.dump(res, open(sys.argv[2], "w"), indent=1)
