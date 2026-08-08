"""Cross-decode diff of two WA import strings via the reference Python codec.

Decodes both with tools/wacodec.py and prints one line per differing field:
    <path>\t<old>\t<new>
Children of `c` are addressed by their display id. Used by test.js for
ADR-003 acceptance A3 (edit locality: exactly the edited fields differ).

Usage: python3 prototype/editor/proto-pydiff.py <original-file> <edited-file>
Exits 0 always; the caller judges the diff lines.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from wacodec import wa_decode  # noqa: E402


def keyname(k):
    return k if isinstance(k, str) else repr(k)


def diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        keys = list(a.keys()) + [k for k in b.keys() if k not in a]
        for k in keys:
            if path == "" and k == "c":
                # address children by display id
                ac = a.get(k, {})
                bc = b.get(k, {})
                idx = set(ac.keys()) | set(bc.keys())
                for i in sorted(idx, key=repr):
                    av, bv = ac.get(i), bc.get(i)
                    label = "c[%s]" % (av.get("id") if isinstance(av, dict)
                                       and "id" in av else repr(i))
                    diff(av, bv, label, out)
                continue
            sub = keyname(k) if path == "" else path + "." + keyname(k)
            if k not in a:
                out.append((sub, "<absent>", repr(b[k])))
            elif k not in b:
                out.append((sub, repr(a[k]), "<absent>"))
            else:
                diff(a[k], b[k], sub, out)
        return
    if type(a) is not type(b) or a != b:
        out.append((path, repr(a), repr(b)))


def main():
    orig = wa_decode(open(sys.argv[1]).read())
    edit = wa_decode(open(sys.argv[2]).read())
    out = []
    diff(orig, edit, "", out)
    for path, old, new in out:
        sys.stdout.write("%s\t%s\t%s\n" % (path, old, new))


if __name__ == "__main__":
    main()
