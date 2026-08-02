"""Every external source we read, and what its operator permits.

    python3 tools/sources.py                 # the table
    python3 tools/sources.py --check <url>   # may I fetch this?

WHY THIS EXISTS. This project reads four third-party sites, and they have made
four different decisions about automated access. Those decisions are not
guessable from the URL, they change without notice, and the cost of getting one
wrong lands on somebody else's server.

The rule that produced this file: `coa.ascensionlogs.gg` disallows ClaudeBot in
robots.txt AND returns a hand-written `{"error":"Forbidden","message":"API
access not allowed"}` on every /api/ route unless a browser Origin is present.
That is a deliberate control, and it is trivially bypassable by setting a
header -- which is exactly why the decision to not bypass it has to live
somewhere a future tool will actually look, rather than in one person's memory.

So: a fetching tool calls allowed() BEFORE it requests, and gets a reason it
can print when the answer is no. Adding a source means adding a row here, which
means someone read the robots.txt once, on purpose.

POLICY VALUES

    open        robots allows general access. Fetch, cache, be polite.
    user-agent  allowed for user-initiated/search agents, blocked for training
                crawlers. Our use qualifies; a bulk training scrape would not.
    reference   robots permits citing and linking, but an access control blocks
                programmatic reads. LINK, do not fetch. Not a technical
                obstacle to route around -- an answer.
    ask         no policy published, or the policy is unclear. Ask first.

`reference` is the interesting one, because it is not "no". It means the
operator is happy to be cited and linked and unhappy to be crawled, and both
halves are real. Link-outs to a `reference` source are encouraged; fetches are
not.
"""
import sys
from urllib.parse import urlparse

SOURCES = {
    "ascension.gg": {
        "policy": "open",
        "what": "official changelog + the CoA talent builder",
        "robots": "User-agent: * Allow: / ; ClaudeBot, GPTBot, PerplexityBot "
                  "all explicitly Allow, with a comment inviting citation",
        "checked": "2026-08-01",
        "notes": "The talent builder at /en/v2/coa-builder/voljin is the "
                 "AUTHORITATIVE talent tree -- the game operator's own "
                 "definition, which beats inferring a tree from what players "
                 "happened to pick.",
    },
    "ascensionsidekick.com": {
        "policy": "user-agent",
        "what": "class kits, per-spec ability lists, rotation priorities",
        "robots": "Allows Claude-User, Claude-SearchBot, OAI-SearchBot, "
                  "Perplexity-User (search / user-initiated). Disallows "
                  "ClaudeBot, GPTBot, CCBot, anthropic-ai (training). The file "
                  "documents the split deliberately.",
        "checked": "2026-08-01",
        "notes": "Our use is a user-initiated fetch of /data.js to build the "
                 "user's own tool, which is the allowed half. A bulk crawl for "
                 "model training is the blocked half. Do not blur them.",
    },
    "coa.ascensionlogs.gg": {
        "policy": "reference",
        "what": "phase rankings, character armory (talents + gear)",
        "robots": "User-agent: * Allow: / with "
                  "Content-Signal: search=yes, ai-train=no, use=reference. "
                  "ClaudeBot, GPTBot, CCBot and friends Disallow: /",
        "checked": "2026-08-01",
        "notes": "Separately from robots, /api/* returns a hand-written "
                 "'API access not allowed' unless a browser Origin is sent. "
                 "The site is a SPA, so its pages only render BY calling that "
                 "API -- rendering it headlessly makes the same blocked "
                 "requests. Swapping the fetcher does not change the answer. "
                 "LINK OUT instead; permission has been requested.",
    },
    "db.exil.es": {
        "policy": "user-agent",
        "what": "spell ids, ranks, cooldowns, costs, per-class spell digests",
        "robots": "Disallows ~25 named training crawlers (ClaudeBot, GPTBot, "
                  "CCBot, anthropic-ai, Google-Extended, Bytespider, ...). "
                  "For User-agent: * it allows the site but Disallows /search "
                  "and /static/icons*. Pages also carry "
                  "<meta name=robots content='noai, noimageai'>.",
        "checked": "2026-08-02",
        "notes": "UPGRADED from `ask` on 2026-08-02: the site DOES publish a "
                 "policy, at /llms.txt, and it draws exactly the split this "
                 "file's `user-agent` value is for -- 'Inference-time agents "
                 "(assistants helping a human read these pages) are welcome. "
                 "Training-time crawlers are not.' Our use is the welcome "
                 "half. The earlier row said `no policy published`, which was "
                 "wrong, and the wrong answer was the restrictive one. "
                 "TWO THINGS TO HONOUR. (1) /search is Disallow'd for general "
                 "crawlers -- do not build name lookups on it. (2) The "
                 "operator publishes purpose-built digests FOR agents, so use "
                 "them instead of scraping HTML: /llms.txt indexes per-category "
                 "guides, and `/class/{slug}/llms.txt` returns one class's "
                 "whole spell list with ids plus every Mind-of-Ascension tree "
                 "in a single 40KB request. tools/exiles.py uses that. "
                 "The site also asks not to be treated as authoritative WoW "
                 "data: it is one private server's snapshot and says outright "
                 "that some rows are unverified scrape output.",
    },
    "db.ascension.gg": {
        "policy": "open",
        "what": "ability pages, cooldown and GCD rows, icon art per spell id",
        "robots": "User-agent: * Allow: / , with Disallow on the query-string "
                  "routes only (?admin=, ?account=, ?compare=, ?filter=, "
                  "?search=, ?go-to-comment=). Publishes a sitemap.",
        "checked": "2026-08-02",
        "notes": "UPGRADED from `ask` on 2026-08-02: robots.txt allows every "
                 "agent on the spell pages we actually read. Honour the "
                 "query-string Disallows -- ?search= and ?filter= are off "
                 "limits, so resolve by spell id, which is what "
                 "fetch_spell_icons.py already does. audit_cds.py caches "
                 "every response under tools/spellchk/ so a re-run costs "
                 "nothing.",
    },
}

FETCHABLE = {"open", "user-agent"}


def host_of(url):
    h = (urlparse(url).hostname or url).lower()
    return h[4:] if h.startswith("www.") else h


def allowed(url):
    """(ok, reason). Call this BEFORE fetching, and print the reason on False."""
    host = host_of(url)
    src = SOURCES.get(host)
    if src is None:
        return False, (
            f"{host} is not in tools/sources.py. Read its robots.txt, add a "
            f"row with what it permits, and then fetch -- an unlisted host is "
            f"an unread policy, not a missing entry.")
    if src["policy"] in FETCHABLE:
        return True, src["policy"]
    if src["policy"] == "reference":
        return False, (
            f"{host} publishes use=reference: cite it and link to it, do not "
            f"fetch it. {src['notes']}")
    return False, (
        f"{host} publishes no access policy. Ask the operator before "
        f"automating against it. {src['notes']}")


def require(url):
    """allowed(), but exits nonzero instead of returning False."""
    ok, why = allowed(url)
    if not ok:
        raise SystemExit(f"sources: refusing to fetch {url}\n  {why}")
    return why


def main(argv):
    if len(argv) > 1 and argv[0] == "--check":
        ok, why = allowed(argv[1])
        print(f"{'ALLOWED' if ok else 'BLOCKED'}  {argv[1]}\n  {why}")
        return 0 if ok else 1
    w = max(len(h) for h in SOURCES)
    for host, s in sorted(SOURCES.items(), key=lambda kv: kv[1]["policy"]):
        print(f"  {host:<{w}}  {s['policy']:<10}  {s['what']}")
    print(f"\n  fetchable: {', '.join(sorted(FETCHABLE))}")
    print("  reference = link to it, do not fetch it")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
