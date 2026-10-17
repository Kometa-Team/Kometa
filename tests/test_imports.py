"""Import smoke check in a fresh process, using the CLI's builder-first order.

The pytest process pre-imports many modules during collection. A child process
keeps those cached imports and patched globals from hiding startup failures.
This checks module-level imports, not imports inside uncalled functions.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_NAMES = sorted(f"modules.{path.stem}" for path in (REPO_ROOT / "modules").glob("*.py") if not path.name.startswith("_"))


@pytest.mark.timeout(90)
def test_modules_import_in_fresh_process():
    assert MODULE_NAMES, "No production modules discovered"
    script = "import importlib, sys; import modules.builder; [importlib.import_module(name) for name in sys.argv[1:]]"
    result = subprocess.run([sys.executable, "-c", script, *MODULE_NAMES], cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
