"""Generate db.ascension.gg WeakAura submission entries.

    python3 tools/mksubmit.py

Their form wants three fields per aura: name, description, import string.
This emits one ready-to-paste file per pack under submissions/, plus an
INDEX.md listing everything so you can see at a glance what still needs
submitting or updating.

Counts and spec lists are read out of the decoded pack, so the description
cannot drift from what the string actually contains -- which matters when a
submission is a copy-paste job repeated 21 times.
"""
import os
import re
import sys

SP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SP)
RESOURCES = os.path.join(ROOT, "resources")
OUT = os.path.join(ROOT, "submissions")

sys.path.insert(0, SP)
from wacodec import wa_decode  # noqa: E402

SITE = "https://github.com/JesterCharles/coa-weakauras"

# class slug -> (display name, builder script, [(pack label, built file)])
PACKS = {
    "runemaster": (
        "Runemaster", "build_runemaster.py",
        [("All Specs", "runemaster-all-specs.txt"),
         ("Glyphic", "runemaster-glyphic.txt"),
         ("Engravement", "runemaster-engravement.txt"),
         ("Riftblade", "runemaster-riftblade.txt")],
    ),
}


def version_of(builder):
    src = open(os.path.join(SP, builder)).read()
    m = re.search(r'^VERSION = "([^"]+)"', src, re.M)
    return m.group(1) if m else "?"


def read_classes():
    out = {}
    for line in open(os.path.join(RESOURCES, "ascension-coa-class-ids.md")):
        m = re.match(r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if m:
            cid, name, specs = m.groups()
            out[name.lower().replace(" ", "-")] = {
                "id": int(cid), "name": name,
                "specs": [s.strip() for s in specs.split(",")],
            }
    return out


def analyse(path):
    """Everything the description needs, straight out of the export."""
    d = wa_decode(open(path).read().strip())
    kids = list(d["c"].values())
    by_id = {k["id"]: k for k in kids}
    by_parent = {}
    for k in kids:
        by_parent.setdefault(k.get("parent"), []).append(k)
    leaves = [k for k in kids if not k.get("controlledChildren")]

    tops = [by_id[i] for i in (d["d"].get("controlledChildren") or {}).values()
            if i in by_id]
    specs = []
    for t in tops:
        label = re.sub(r"^RM\s+", "", t["id"])
        if label.lower() == "core":
            continue
        bands = 0
        icons = 0
        for g in by_parent.get(t["id"], []):
            if not g.get("controlledChildren") or not g.get("yOffset"):
                continue
            n = len([c for c in by_parent.get(g["id"], [])
                     if not c.get("controlledChildren")])
            if n:
                bands += 1
                icons += n
        specs.append((label, bands, icons))

    return {
        "root": d["d"].get("id", ""),
        "displays": len(kids),
        "leaves": len(leaves),
        "specs": specs,
        "bytes": os.path.getsize(path),
    }


def describe(cls, label, info, version, is_all):
    """Player-facing copy for the submission's description field."""
    name = cls["name"]
    speclist = ", ".join(s[0] for s in info["specs"]) or label

    if is_all:
        opener = (
            f"Complete rotation and cooldown pack for {name}, covering all "
            f"{len(info['specs'])} specs ({speclist}) in a single import."
        )
        scope = (
            "Only the spec you are currently playing is shown. Switching spec "
            "swaps the whole display over; nothing from the other specs "
            "renders or costs you anything."
        )
    else:
        opener = (
            f"Rotation and cooldown pack for {name} — {label} only. A smaller "
            f"import if you never play the other specs; grab the All Specs "
            f"version instead if you do."
        )
        scope = (
            f"Everything is gated to {label}, so it stays hidden on your other "
            f"specs."
        )

    # Paragraphs are deliberately unwrapped -- this goes into a web form
    # textarea, which does its own wrapping. Hard-wrapping here produces ragged
    # lines once the form re-wraps them.
    lines = [
        opener,
        "",
        f"{scope} Every display is also locked to {name}, so it will not load "
        f"on any other class — import as many class packs as you like without "
        f"paying for the ones you are not playing.",
        "",
        "WHAT YOU GET",
        "- Main damage row, always visible, glows when a proc says to press something",
        "- Offensive cooldown and defensive/utility rows, dimmed while on cooldown and escalating as they come back: timer at 20s, glow at 10s, urgent glow at 5s",
        "- One active-only row for everything currently up — procs, running cooldowns, your buffs and your target's debuffs",
        "- Resource bars locked to the width of the main row so they can never drift",
        "- Missing-buff reminders that only appear when something is actually missing",
        "- Long-term buffs (tattoos, engravings, raid auras) pinned at the bottom",
        "",
        "NOTES",
        "- Everything is centred on your character. The layout is identical across every class pack in this series, so learning one teaches you the rest.",
        "- No on-use trinket displays. Trinkets are personal gear rather than class kit — add your own two icons if you want them.",
        "- Spell IDs are verified against in-game tooltips first, then db.exil.es and db.ascension.gg. The art and the trigger always come from the same ID, so an icon can never disagree with its tooltip.",
        "",
        f"Version {version}. Source, changelog and the other class packs: {SITE}",
    ]
    return "\n".join(lines)


def main():
    classes = read_classes()
    os.makedirs(OUT, exist_ok=True)
    index = ["# Submission queue — db.ascension.gg",
             "",
             "One file per pack. Each holds the three fields the submission "
             "form asks for: name, description, import string.",
             "",
             "| Class | Pack | Name | Displays | Version | File |",
             "|---|---|---|---|---|---|"]

    for slug, (disp, builder, packs) in PACKS.items():
        cls = classes.get(slug)
        if not cls:
            print(f"  !! unknown class slug: {slug}")
            continue
        version = version_of(builder)
        cdir = os.path.join(OUT, slug)
        os.makedirs(cdir, exist_ok=True)

        for label, built in packs:
            src = os.path.join(SP, built)
            if not os.path.exists(src):
                print(f"  !! missing build artifact: {built}")
                continue
            info = analyse(src)
            is_all = label.lower().startswith("all")
            aura_name = (f"{cls['name']} [CoA]" if is_all
                         else f"{cls['name']} {label} [CoA]")
            desc = describe(cls, label, info, version, is_all)
            string = open(src).read().strip()

            fname = f"{slug}-{label.lower().replace(' ', '-')}.md"
            path = os.path.join(cdir, fname)
            open(path, "w").write(f"""# {aura_name}

Ready to paste into the db.ascension.gg WeakAura submission form.
Generated by `tools/mksubmit.py` — edit the generator, not this file.

---

## 1. Name

```
{aura_name}
```

## 2. Description

```
{desc}
```

## 3. Import string

{info['displays']} displays, {info['bytes'] // 1024} KB. Paste the whole thing — it is one unbroken string with no newlines.

```
{string}
```
""")
            index.append(
                f"| {cls['name']} | {label} | `{aura_name}` | "
                f"{info['displays']} | {version} | "
                f"[{fname}]({slug}/{fname}) |")
            print(f"  wrote {slug}/{fname}  ({info['displays']} displays)")

    open(os.path.join(OUT, "INDEX.md"), "w").write("\n".join(index) + "\n")
    print(f"\nsubmissions written to submissions/")


if __name__ == "__main__":
    main()
