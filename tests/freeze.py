"""Freeze the current build output as the regression fixture.

    python3 tests/freeze.py                # every built class
    python3 tests/freeze.py runemaster     # just one

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

sys.path.insert(0, TOOLS)
from classes import built as built_classes, get  # noqa: E402

CLASSES = [get(a) for a in sys.argv[1:]] or built_classes()

os.makedirs(FIXTURES, exist_ok=True)

for cls in CLASSES:
    for spec, name in cls.packs:
        env = dict(os.environ)
        env.pop("WA_SPEC", None)
        env.pop("WA_GLOW", None)
        if spec:
            env["WA_SPEC"] = spec
        r = subprocess.run([sys.executable, cls.builder],
                           cwd=TOOLS, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(
                f"{cls.builder} failed (WA_SPEC={spec}):\n{r.stdout}{r.stderr}")
        src = os.path.join(TOOLS, f"{name}.txt")
        dst = os.path.join(FIXTURES, f"{name}.txt")
        shutil.copy2(src, dst)
        print(f"froze {name}.txt  ({os.path.getsize(dst)} bytes)")

print("\nfixtures written to tests/fixtures/")
