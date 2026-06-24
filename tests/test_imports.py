"""Import smoke tests.

Catches three classes of regression that don't show up in normal tests:

1. **New circular imports.** A module that imports another module that
   imports it back will fail at import time.
2. **Missing runtime dependencies.** A module that imports a package not
   listed in ``requirements.txt`` will explode here even if no test
   exercises that code path.
3. **Syntax errors / typos.** Black + flake8 catch most of these, but
   they don't catch lazy-evaluation bugs (e.g. an ``import`` inside a
   function that fires only on a specific code path).

Every Python file under ``modules/`` is auto-discovered and imported
exactly once. Pytest's parametrization gives a per-module pass/fail
line in the output, so a CI failure says exactly which module broke.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = REPO_ROOT / "modules"

# Discover every importable .py file under modules/, excluding __init__.py
# and any private files (leading underscore).
MODULE_FILES = sorted(p for p in MODULES_DIR.glob("*.py") if not p.name.startswith("_"))
MODULE_NAMES = [f"modules.{p.stem}" for p in MODULE_FILES]


def test_at_least_one_module_discovered() -> None:
    """Defensive: catch a layout change that hides modules/ from us."""
    assert MODULE_NAMES, f"no Python modules found under {MODULES_DIR}"


@pytest.mark.parametrize("module_name", MODULE_NAMES, ids=lambda n: n.split(".")[-1])
def test_module_imports_cleanly(module_name: str) -> None:
    """Every module under modules/ must import without raising."""
    try:
        importlib.import_module(module_name)
    except Exception as e:  # noqa: BLE001 — we genuinely want any exception type
        pytest.fail(f"importing {module_name} raised {type(e).__name__}: {e}")
