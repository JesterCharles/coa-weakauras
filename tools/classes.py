"""Per-class metadata, parsed from the reference tables in resources/.

Every tool that needs to know something about a CoA class -- its id, its
WeakAuras load token, its spec list, where its data files live -- reads it from
here, so a new class is a data change rather than an edit to four scripts.

The two markdown tables in resources/ stay authoritative and are parsed rather
than copied: `class-tokens.md` was read out of `WeakAuras.class_types` in game
and `ascension-coa-class-ids.md` off db.ascension.gg. Duplicating either into a
JSON would give the transcription a chance to drift from the source.

    from classes import CLASSES, get
    c = get("runemaster")
    c.token      -> "SPIRITMAGE"
    c.specs      -> ["glyphic", "engravement", "riftblade"]
    c.cooldowns  -> "cooldown-abilities-runemaster.json"
"""
import os
import re

SP = os.path.dirname(os.path.abspath(__file__))
RESOURCES = os.path.join(os.path.dirname(SP), "resources")
# Built import strings. One folder per class, the same shape docs/packs/ uses --
# 21 classes x 4 packs is 84 files, and flat in tools/ they sat among the
# scripts with the class name repeated in every filename. Everything here is a
# build artifact: gitignored, and regenerable by re-running the builder.
BUILD = os.path.join(SP, "packs")


def build_path(slug, name):
    """Absolute path of a built pack, creating its class folder.

    The one place the layout is written down. Builders, tests, the site
    publisher and the measuring tools all resolve through this, so moving the
    artifacts again is a one-line change rather than a hunt through eight
    scripts -- which is what the flat layout cost.
    """
    d = os.path.join(BUILD, slug)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{name}.txt")


def data(name):
    """resources/ wins, tools/ is the legacy fallback. Same resolver the
    builder uses -- see the note in build_runemaster.py about why."""
    p = os.path.join(RESOURCES, name)
    return p if os.path.exists(p) else os.path.join(SP, name)


def dest(name):
    """Where a GENERATED data file is WRITTEN. Always resources/.

    Never write through data(). It falls back to tools/ when the file does
    not exist yet -- which is precisely the case for a class being scraped
    for the first time -- so the first class through a fresh tool lands its
    output in tools/ while every established class reads from resources/.
    The fallback then hides it: the next read resolves tools/ and works, so
    nothing fails and the two directories quietly diverge.

    That is the shape of the bug that left audit_cds.py resolving against
    tools/ for weeks after the data moved. Chronomancer's first cooldown
    audit reproduced it exactly.
    """
    return os.path.join(RESOURCES, name)


def _rows(path):
    """Yield the cells of every pipe-table body row in a markdown file."""
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # skip the header and the |---|---| separator
        if not cells or not cells[0].isdigit():
            continue
        yield cells


def _clean(s):
    """Strip the markdown emphasis the tables use to highlight a row."""
    return s.replace("**", "").replace("`", "").strip()


def _slug(name):
    """"Knight of Xoroth" -> "knight-of-xoroth".

    Hyphenated, not compressed. The 91 class/spec icons already on disk under
    docs/assets/class-icons/ use this form, and so do the published docs/ URLs,
    so it is the one slug with existing commitments. Data files follow it for
    consistency -- there is exactly one slug per class, everywhere.
    """
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class ClassInfo:
    def __init__(self, class_id, name, token, specs):
        self.id = class_id
        self.name = name                      # "Runemaster", "Witch Doctor"
        self.slug = _slug(name)               # "runemaster", "witchdoctor"
        self.token = token                    # load.class.single
        self.specs = specs

    # ---- data files. All resolved through data(), so a class that has not
    # been scraped yet simply reports a path that does not exist yet.
    @property
    def exiles(self):
        return f"exiles-{self.slug}.json"

    @property
    def skills(self):
        return f"coa-{self.slug}-skills.json"

    @property
    def cooldowns(self):
        return f"cooldown-abilities-{self.slug}.json"

    def sidekick(self, spec):
        return f"sidekick-{self.slug}-{spec}.md"

    # ---- spec roles, from resources/spec-roles.md. Observed in game; not
    # derivable, and the one place it LOOKS derivable is wrong (db.exil.es
    # files Pyromancer's HEALING spec under the slug `pyromancer-destruction`).
    def spec_role(self, spec):
        """'damage' | 'healing' | 'tank', or None if nobody has played it.

        None is deliberately not 'damage'. A healer needs the target band, and
        defaulting to damage is precisely how that would go missing with
        nothing raising an error.
        """
        return SPEC_ROLES.get((self.slug, spec))

    @property
    def healers(self):
        return [s for s in self.specs if self.spec_role(s) == "healing"]

    # ---- pack naming. NOTE two different names for the same pack: the
    # builder writes `<slug>-all-specs.txt` into tools/packs/<slug>/, and
    # mksite.py republishes it to docs/packs/<slug>/ as `<slug>-coa.txt` (the
    # name players see). Tests work on the builder's output, so `packs` uses
    # the builder name. The slug stays IN the filename even under a per-class
    # folder: these get copied into WA imports, chat and bug reports, where
    # "time.txt" says nothing and "chronomancer-time.txt" says everything.
    @property
    def packs(self):
        """(spec_or_None, builder pack name), all-specs first."""
        return [(None, f"{self.slug}-all-specs")] + [
            (s, f"{self.slug}-{s}") for s in self.specs]

    def pack_path(self, name):
        """Absolute path of one of this class's built packs."""
        return build_path(self.slug, name)

    @property
    def pack_dir(self):
        return os.path.join(BUILD, self.slug)

    @property
    def core_leaves(self):
        """Expected count of Core leaves left class-wide (no spellknown gate).

        A regression guard, not a rule: Core is deliberately class-only so
        engravings and etchings still show for a levelling character who has
        not learned the spec's signature spell. The number is per-class and
        only known once the class is built.
        """
        return CORE_LEAVES.get(self.slug)

    @property
    def builder(self):
        return f"build_{self.slug}.py"

    @staticmethod
    def spec_label(spec):
        """Display name for a spec slug. Several classes use hyphenated slugs
        (`black-knight`, `moon-guard`, `mountain-king`), so title-casing the
        raw slug alone would ship "Black-Knight"."""
        return spec.replace("-", " ").title()

    @property
    def spec_labels(self):
        return [self.spec_label(s) for s in self.specs]

    def __repr__(self):
        return f"<{self.name} id={self.id} {self.token} {len(self.specs)} specs>"


# Per-class regression guards that only exist once the class is built. Add an
# entry when a class ships; tests skip the check for classes not listed.
CORE_LEAVES = {
    # 30 -> 15 when the long-term band moved out of Core into one band per
    # spec, so its 15 icons stopped being class-wide leaves. Core now holds
    # the two reminder alerts and the engraving/etching trackers only.
    "runemaster": 15,
    # 23 -> 12 for the same reason Runemaster went 30 -> 15: the long-term band
    # moved out of Core into one band per spec, so its 11 icons stopped being
    # class-wide leaves. Core now holds the two reminder alerts and the
    # class-wide trackers only.
    "chronomancer": 12,
    # First pin (0.1). TP Core is an empty skeleton (both alerts are
    # spec-shaped: NO GIFT on Zealot, NO STAND on Oathkeeper) -- the 7 are
    # the Core group plus six merged all-spec Buffs leaves (Glory, Libram of
    # Fervor, the three typed Oaths, Sacred Restraint) that hold the class
    # gate alone, for the standing reason: buff icons are self-gating and a
    # buff id is not something IsSpellKnown recognises.
    "templar": 7,
}


def _spec_roles():
    """(class-slug, spec) -> role, parsed from resources/spec-roles.md.

    Two tables in that file start with a digit and _rows() yields both, so
    filter on the role vocabulary rather than on position -- the corroboration
    table's third cell is a ratio, not a role, and would otherwise land here.
    """
    out = {}
    for cells in _rows(data("spec-roles.md")):
        if len(cells) < 4:
            continue
        role = _clean(cells[3]).lower()
        if role not in ("damage", "healing", "tank"):
            continue
        out[(_slug(_clean(cells[1])), _clean(cells[2]).lower())] = role
    return out


SPEC_ROLES = _spec_roles()


def _load():
    tokens, specs = {}, {}
    for cells in _rows(data("class-tokens.md")):
        tokens[int(cells[0])] = (_clean(cells[1]), _clean(cells[2]))
    for cells in _rows(data("ascension-coa-class-ids.md")):
        specs[int(cells[0])] = [s.strip() for s in _clean(cells[2]).split(",")]

    out = {}
    for cid, (name, token) in sorted(tokens.items()):
        if cid not in specs:
            continue
        info = ClassInfo(cid, name, token, specs[cid])
        out[info.slug] = info
    return out


CLASSES = _load()


def get(slug):
    c = CLASSES.get(_slug(slug))
    if c is None:
        raise SystemExit(
            f"unknown class {slug!r}. Known: {', '.join(sorted(CLASSES))}")
    return c


def built():
    """Classes that actually have a builder on disk -- what tests should run
    against. Keeps tests/run.py from failing on the 20 classes not started."""
    return [c for c in CLASSES.values()
            if os.path.exists(os.path.join(SP, c.builder))]


if __name__ == "__main__":
    for c in sorted(CLASSES.values(), key=lambda x: x.id):
        mark = "BUILT" if os.path.exists(os.path.join(SP, c.builder)) else ""
        print(f"  {c.id:>3}  {c.name:<18} {c.token:<16} "
              f"{len(c.specs)} specs  {','.join(c.specs):<52} {mark}")
    print(f"\n{len(CLASSES)} classes, {len(built())} with a builder")
