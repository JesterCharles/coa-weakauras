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
        "policy": "ask",
        "what": "spell ids, ranks, cooldowns, costs",
        "robots": "no policy published",
        "checked": "2026-08-01",
        "notes": "Already used by spellmeta.py and audit_cds.py at low volume "
                 "with local caching. No published policy either way; keep the "
                 "volume low and the cache warm.",
    },
    "db.ascension.gg": {
        "policy": "ask",
        "what": "ability pages, cooldown and GCD rows",
        "robots": "no policy published",
        "checked": "2026-08-01",
        "notes": "Same posture as db.exil.es. audit_cds.py caches every "
                 "response under tools/spellchk/ so a re-run costs nothing.",
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
