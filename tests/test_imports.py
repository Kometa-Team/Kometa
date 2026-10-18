"""Import smoke check in a fresh process, using the CLI's builder-first order.

The pytest process pre-imports many modules during collection. A child process
keeps those cached imports and patched globals from hiding startup failures.
This checks module-level imports, not imports inside uncalled functions. Every failing
module is reported, not just the first.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_NAMES = sorted(f"modules.{path.stem}" for path in (REPO_ROOT / "modules").glob("*.py") if not path.name.startswith("_"))


# Child process: import the builder first like the CLI, then every module, collecting all failures.
CHILD_SCRIPT = """
import importlib
import sys
import traceback

import modules.builder

failures = []
for name in sys.argv[1:]:
    try:
        importlib.import_module(name)
    except Exception:
        failures.append(f"{name}:\\n{traceback.format_exc()}")
if failures:
    print("\\n".join(failures))
    sys.exit(1)
"""


@pytest.mark.timeout(90)
def test_modules_import_in_fresh_process():
    assert MODULE_NAMES, "No production modules discovered"
    result = subprocess.run([sys.executable, "-c", CHILD_SCRIPT, *MODULE_NAMES], cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
