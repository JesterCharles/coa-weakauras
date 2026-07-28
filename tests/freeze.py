"""Freeze the current build output as the regression fixture.

    python3 tests/freeze.py

Run this ONLY when the current output is known-good -- i.e. it has been
confirmed in game, or the structural diff against the previous fixture has
been reviewed line by line and every delta was intended.

Re-baselining without reading the diff defeats the entire safety net.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
FIXTURES = os.path.join(HERE, "fixtures")

PACKS = [
    (None, "runemaster-all-specs"),
    ("glyphic", "runemaster-glyphic"),
    ("engravement", "runemaster-engravement"),
    ("riftblade", "runemaster-riftblade"),
]

os.makedirs(FIXTURES, exist_ok=True)

for spec, name in PACKS:
    env = dict(os.environ)
    env.pop("WA_SPEC", None)
    env.pop("WA_GLOW", None)
    if spec:
        env["WA_SPEC"] = spec
    r = subprocess.run([sys.executable, "build_runemaster.py"],
                       cwd=TOOLS, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"build failed (WA_SPEC={spec}):\n{r.stdout}{r.stderr}")
    src = os.path.join(TOOLS, f"{name}.txt")
    dst = os.path.join(FIXTURES, f"{name}.txt")
    shutil.copy2(src, dst)
    print(f"froze {name}.txt  ({os.path.getsize(dst)} bytes)")

print("\nfixtures written to tests/fixtures/")
