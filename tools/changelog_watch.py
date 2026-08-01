"""Watch ascension.gg's Conquest of Azeroth changelog for class changes.

    python3 tools/changelog_watch.py                    # what is new since last accept
    python3 tools/changelog_watch.py --class runemaster # one class
    python3 tools/changelog_watch.py --accept           # mark everything seen now
    python3 tools/changelog_watch.py --pages 5          # scan deeper
    python3 tools/changelog_watch.py --fixture <path>   # parse a local file, no network

Exit 0 when nothing is new, 1 when something is, 2 on an error. The nonzero
exit is the point: this runs unattended, and a watcher that reports drift only
in prose that nobody reads is a watcher that does nothing.

WHY THIS EXISTS. Runemaster shipped 1.0 on 2026-07-28. The changelog dated
2026-07-31 changed eight Runemaster abilities, two of them press-priority
changes rather than number tweaks:

    [Runemaster] Tempo now additionally increases the damage of Runic Brand.
    [Runemaster] Runic Explosion base damage has been increased by ~25%.

Three days, and nothing in the repo noticed. On the same day Chronomancer got
a rework that introduced an ability the inventory has never heard of (Rapid
Acceleration, replacing Cycling Aeons) and a new interrupt (Fray Magic). At 21
classes against a server that rebalances every couple of weeks, noticing by
hand is not a plan.

THE URL SHAPE, because it reads wrong. `/en/changelog/<N>` is a SECTION id,
not a page number: /1 is general, /4 is Conquest of Azeroth, /5 is the Live
realm's base classes, and /2 and /3 return "No changelogs found". Pagination
is `?page=N` INSIDE a section, up to ~307 pages of history. Reading <N> as a
page number is the obvious mistake and it silently searches the wrong realm.

THE ENTRY GRAMMAR. Each entry is a `<p class="text-neutral-300">` whose text
begins with a bracketed tag. Dates are page-level headers ("Changes made on:
2026/08/01") that GROUP the entries after them, so an entry's date is the
nearest date header above it -- there is no per-entry date and no per-entry id.
Change detection is therefore a content hash, not an id diff.

TAGS ARE FREE TEXT TYPED BY DEVELOPERS, which is the whole difficulty:

    [Runemaster]                    a class
    [Witch Hunter - Inquisition]    a class and a spec
    [Strombringer]                  a typo for Stormbringer, seen live
    [General]                       not a class at all

So an exact name match drops real entries silently, which is the same shape of
bug as inferring specs from Sidekick mention counts (see mkabilities.py: 11 of
80 wrong, and a wrong narrow hides an ability). Unrecognised tags are therefore
REPORTED, never dropped -- if this tool cannot attribute a tag it says so and
fails the run rather than quietly showing you nothing.
"""
import argparse
import hashlib
import html as _html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import sources  # noqa: E402
from classes import CLASSES, built, dest, data  # noqa: E402

SECTION = 4                     # Conquest of Azeroth
BASE = "https://ascension.gg/en/changelog"
STATE = "changelog-seen.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

# Tags that are real and deliberately not a class. Listed rather than pattern
# matched: the point of the unknown-tag report is that anything NOT written
# down here gets a human's attention exactly once.
NON_CLASS_TAGS = {
    "general", "talents & abilities", "pending restart", "free pick",
    "darkmoon", "dawnrise", "blood presence", "going live monday, 3 august",
    "pvp", "items", "quests", "dungeons", "raids", "professions", "ui",
}

# Misspellings seen in the live changelog. A typo is not a reason to miss a
# balance change, and the devs are writing prose, not filling in a form.
TAG_TYPOS = {
    "strombringer": "stormbringer",
    "runemster": "runemaster",
    "chronomacer": "chronomancer",
}


def _slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def tag_to_slug(tag):
    """Resolve a changelog tag to (slug, spec_or_None, recognised).

    `recognised` is False for anything this tool cannot place, INCLUDING
    non-class tags -- the caller decides whether to report or ignore, and the
    distinction between "known non-class" and "no idea" is made by the caller
    against NON_CLASS_TAGS. Splitting it here would bury the unknowns.
    """
    raw = tag.strip()
    spec = None
    # "[Witch Hunter - Inquisition]" -- em dash, en dash and hyphen all seen.
    m = re.match(r"^(.*?)\s*[-–—]\s*(.+)$", raw)
    head = raw
    if m:
        head, spec = m.group(1), m.group(2)
    key = _slugify(head)
    key = TAG_TYPOS.get(key, key)
    if key in CLASSES:
        cls = CLASSES[key]
        spec_slug = _slugify(spec) if spec else None
        if spec_slug and spec_slug not in cls.specs:
            spec_slug = None      # a spec we do not recognise is not a reason
        return cls.slug, spec_slug, True     # to drop the class attribution
    return key, None, False


def fetch(page, section=SECTION, retries=2):
    url = f"{BASE}/{section}" + (f"?page={page}" if page > 1 else "")
    sources.require(url)        # policy gate -- see tools/sources.py
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status != 200:
                    raise urllib.error.HTTPError(
                        url, r.status, "unexpected status", r.headers, None)
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if attempt == retries:
                raise SystemExit(f"changelog_watch: fetch failed for {url}: {e}")
            time.sleep(1.5 * (attempt + 1))


_DATE_RE = re.compile(r"Changes made on:.*?(20\d\d/\d\d/\d\d)", re.S)
_ENTRY_RE = re.compile(r'<p class="text-neutral-300">(.*?)</p>', re.S)
_TAG_RE = re.compile(r"^\[([^\]]+)\]\s*(.*)$", re.S)


def _text(fragment):
    """Strip inner markup and unescape. Entries carry <strong>/<em> inline."""
    s = re.sub(r"<[^>]+>", "", fragment)
    return _html.unescape(s).replace(" ", " ").strip()


def parse(page_html):
    """[{date, tag, slug, spec, recognised, text, hash}], document order.

    Dates bind by OFFSET, not by DOM nesting: the header sits in a sibling
    subtree ("Changes made on:" and the date live in two spans separated by an
    HTML comment), so walking the tree to associate them is fiddly and brittle
    against a markup change. Nearest-preceding-offset is what the page means
    visually and survives a restyle.
    """
    dates = [(m.start(), m.group(1)) for m in _DATE_RE.finditer(page_html)]
    out = []
    for m in _ENTRY_RE.finditer(page_html):
        pos, text = m.start(), _text(m.group(1))
        if not text:
            continue
        date = None
        for dpos, dval in dates:
            if dpos < pos:
                date = dval
            else:
                break
        tm = _TAG_RE.match(text)
        tag, body = (tm.group(1), tm.group(2)) if tm else (None, text)
        slug = spec = None
        recognised = False
        if tag:
            slug, spec, recognised = tag_to_slug(tag)
        out.append({
            "date": date, "tag": tag, "slug": slug, "spec": spec,
            "recognised": recognised, "text": body,
            # Hash the ATTRIBUTED text, not the raw line: an entry re-tagged
            # from [Strombringer] to [Stormbringer] is the same change, and
            # re-reporting it as new would train you to ignore this tool.
            "hash": hashlib.sha256(
                f"{slug or tag or ''}|{body}".encode()).hexdigest()[:16],
        })
    return out


def load_state():
    p = data(STATE)
    if not os.path.exists(p):
        return {"section": SECTION, "entries": {}}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_state(st):
    p = dest(STATE)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--class", dest="cls", help="only report this class slug")
    ap.add_argument("--pages", type=int, default=3,
                    help="pages to scan, 100 entries each (default 3)")
    ap.add_argument("--section", type=int, default=SECTION)
    ap.add_argument("--fixture", help="parse a local HTML file, no network")
    ap.add_argument("--accept", action="store_true",
                    help="record everything seen now as known")
    ap.add_argument("--all-classes", action="store_true",
                    help="report classes with no builder too")
    args = ap.parse_args()

    if args.fixture:
        pages = [open(args.fixture, encoding="utf-8").read()]
    else:
        pages = []
        for n in range(1, args.pages + 1):
            pages.append(fetch(n, args.section))
            if n < args.pages:
                time.sleep(1.0)     # a courtesy, not a rate limit we were given

    entries = []
    for h in pages:
        entries.extend(parse(h))
    if not entries:
        print("changelog_watch: parsed 0 entries -- the page markup probably "
              "changed. Check the <p class=\"text-neutral-300\"> selector.",
              file=sys.stderr)
        return 2

    state = load_state()
    seen = state.get("entries", {})

    tracked = ({c.slug for c in CLASSES.values()} if args.all_classes
               else {c.slug for c in built()})
    if args.cls:
        tracked = {args.cls}

    new, unknown = [], {}
    for e in entries:
        if e["tag"] and not e["recognised"]:
            if e["tag"].strip().lower() not in NON_CLASS_TAGS:
                unknown.setdefault(e["tag"], 0)
                unknown[e["tag"]] += 1
            continue
        if e["slug"] in tracked and e["hash"] not in seen:
            new.append(e)

    dates = sorted({e["date"] for e in entries if e["date"]})
    print(f"scanned {len(entries)} entries over {len(pages)} page(s), "
          f"section {args.section}, dates {dates[0]}..{dates[-1]}"
          if dates else f"scanned {len(entries)} entries")

    for e in new:
        spec = f"/{e['spec']}" if e["spec"] else ""
        print(f"  NEW  {e['date']}  [{e['slug']}{spec}]  {e['text']}")

    if unknown:
        print("\n  UNRECOGNISED TAGS -- attributed to no class, so their "
              "entries were NOT checked:")
        for t, n in sorted(unknown.items(), key=lambda x: -x[1]):
            print(f"    {n:3d}x  [{t}]")
        print("    Add a real class to TAG_TYPOS, or a non-class tag to "
              "NON_CLASS_TAGS, in tools/changelog_watch.py.")

    if args.accept:
        for e in entries:
            if e["recognised"]:
                seen[e["hash"]] = {"class": e["slug"], "date": e["date"],
                                   "text": e["text"]}
        state["entries"] = seen
        state["section"] = args.section
        save_state(state)
        print(f"\naccepted: {len(seen)} entries now known")
        return 0

    if not new and not unknown:
        print("nothing new")
        return 0
    if not new:
        print("\nnothing new for tracked classes, but see unrecognised tags "
              "above")
        return 1
    print(f"\n{len(new)} new entr{'y' if len(new) == 1 else 'ies'} for "
          f"{len(sorted({e['slug'] for e in new}))} tracked class(es). "
          f"Rotation citations for those classes are now STALE: re-research "
          f"before trusting a priority. `--accept` once you have.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
