"""Canonical-JSON dump of a WA import string via the reference Python codec.

Twin of wacodec.js canonicalJson(): arrays for pure array parts, prefixed
sorted keys otherwise ("n:" int / float-repr, "s:" string, "b:" bool),
ensure_ascii escaping, Python repr() floats. test.js compares byte-for-byte
against the JS dump (ADR-003 acceptance A1).

Usage: python3 prototype/editor/proto-pydump.py <pack-file-or-string-file>
Emits one line "META <root id>\\t<child count>" then the canonical JSON.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from wacodec import wa_decode  # noqa: E402


def split(t):
    acount = 0
    while (acount + 1) in t and t[acount + 1] is not None:
        acount += 1
    arr = [t[i] for i in range(1, acount + 1)]
    mp = [(k, v) for k, v in t.items()
          if not (isinstance(k, int) and not isinstance(k, bool)
                  and 1 <= k <= acount)]
    return arr, mp


def canon(v):
    if isinstance(v, dict):
        arr, mp = split(v)
        if not mp:
            return [canon(x) for x in arr]
        o = {}
        for i, x in enumerate(arr):
            o["n:%d" % (i + 1)] = canon(x)
        for k, val in mp:
            if isinstance(k, bool):
                kk = "b:true" if k else "b:false"
            elif isinstance(k, int):
                kk = "n:%d" % k
            elif isinstance(k, float):
                kk = "n:" + repr(k)
            else:
                kk = "s:" + k
            o[kk] = canon(val)
        return o
    return v


def main():
    tree = wa_decode(open(sys.argv[1]).read())
    root_id = tree["d"]["id"]
    child_count = len(tree["c"].array_part()) if "c" in tree else 0
    sys.stdout.write("META %s\t%d\n" % (root_id, child_count))
    sys.stdout.write(json.dumps(canon(tree), sort_keys=True,
                                separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
