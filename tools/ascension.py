"""db.ascension.gg as a SUPPLEMENT to the db.exil.es mirror. Fill-only.

The mirror under `tools/spellchk/` stays authoritative for everything it
carries. This module only ever fills a hole in it, and never overwrites a
value, because the two are different snapshots of the same TrinityCore tables
and where they disagree we have no way to tell which is newer.

WHAT IT IS FOR. Three holes the mirror has and this one does not:

    cooldown   74 spells whose mirror `cooldown_ms` is 0 have a real cooldown
               on Ascension. Eight of them are raid-utility rows -- Guardian's
               `Hammer of the Law` is a 40 second silence that this page has
               been printing as having no cooldown at all.
    reagents   The mirror has NO reagent field of any kind. Ascension has one,
               which is what finally fills the Battle Rez column that
               `spell-observed.json` has been carrying by hand (and empty).
    cast time  The mirror stores a ranged-weapon marker as `cast_time_ms` of
               -1000000, which the page renders `Instant*` with a footnote.
               Ascension resolves those to a plain 0.

THE ROUNDING TRAP, MEASURED. Ascension renders a cooldown as human text, so
"90 sec" comes back as "1 min". Checked against 60 ids whose exact value we
already had: exact on 30 of 30 "N sec" values, wrong on 6 of 30 "N min" ones,
and every miss was 90000ms shown as "1 min". So SECONDS are promoted as exact
and MINUTES are kept as a lower bound and rendered `>=1m` -- printing a bound
as though it were exact is the one failure this file must not have, because a
raid lead plans around the number.

NOT CARRIED, deliberately: names (4 conflicts, unresolved, and the mirror
wins), descriptions (formulas unresolved), effects (English prose where every
classifier needs the numeric ids), spec names (the mirror's own
`skill_line.name` is already right and free) and damage magnitudes (the two
snapshots do not reconcile and nobody has explained why).

COVERAGE. 3,099 of 12,005 mirror ids, 25.8%. The 21 class listviews are the
only polite enumeration db.ascension.gg offers -- its sitemap names no spells
-- so the rest would be one request per id and is not worth it.
"""
import json
import os

SP = os.path.dirname(os.path.abspath(__file__))
_DATA = None


def _load():
    global _DATA
    if _DATA is None:
        p = os.path.join(os.path.dirname(SP), "resources",
                         "ascension-spells.json")
        try:
            _DATA = json.load(open(p, encoding="utf-8")).get("ids") or {}
        except Exception:
            _DATA = {}
    return _DATA


def get(sid):
    return _load().get(str(sid)) or {}


def enrich(d):
    """Fill the holes in one mirror spell dict, in place. Returns it.

    Only ever writes where the mirror is empty. The private keys it adds --
    `_cd_from`, `_cd_floor`, `_cast_from` -- exist so the renderers can say
    where a number came from rather than presenting a supplement as though the
    primary source had it.
    """
    a = get(d.get("id"))
    if not a:
        return d
    if not d.get("cooldown_ms"):
        if a.get("cooldown_ms"):
            d["cooldown_ms"] = a["cooldown_ms"]
            d["_cd_from"] = "ascension"
        elif a.get("cooldown_ms_floor"):
            # A BOUND, NOT A VALUE. Ascension renders this one as "N min",
            # which covers a 30 second range, so it is stored separately and
            # rendered with a >= rather than promoted into cooldown_ms where
            # every sort and every grid cell would treat it as exact.
            d["_cd_floor"] = a["cooldown_ms_floor"]
    # -1000000 is this server's ranged-weapon marker, not a cast time.
    if (d.get("cast_time_ms") or 0) < 0 and (a.get("cast_time_ms") or 0) >= 0:
        d["cast_time_ms"] = a.get("cast_time_ms") or 0
        d["_cast_from"] = "ascension"
    return d


def reagents():
    """spell id -> reagent text. `"none"` means CONFIRMED NONE; absent = unknown.

    That distinction is the whole value here. The Battle Rez column has always
    been blank, and a blank cell reads as "no reagent" when it actually meant
    "nobody has checked" -- the same trap `spell-observed.json` documents for
    its boss column. 5,415 spells come back with an explicitly empty reagent
    list, which turns those blanks into a fact.
    """
    out = {}
    for sid, a in _load().items():
        r = a.get("reagents")
        if r is None:
            continue
        # "none", not "". The empty string is what an UNKNOWN renders as, so
        # returning it here would throw away the entire finding. `none` is the
        # word spell-observed.json already uses for "confirmed to need
        # nothing", and the renderer treats it the same way.
        out[sid] = (", ".join(x.get("name") or str(x.get("item")) for x in r)
                    if r else "none")
    return out
