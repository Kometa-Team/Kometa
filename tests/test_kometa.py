"""Tests for ``kometa.py`` (the top-level entry script).

The script itself is mostly argparse + scheduling + a thin orchestration
loop, so most behaviour is covered by the per-module suites. This file
exists for regression checks that pin invariants of the entry script
itself — things that, if broken, would crash users at launch before any
other test had a chance to fire.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KOMETA_PY = REPO_ROOT / "kometa.py"


def _module_ast() -> ast.Module:
    """Parse kometa.py once and return its AST."""
    return ast.parse(KOMETA_PY.read_text(encoding="utf-8"))


def test_issue_3244_resource_import_is_guarded() -> None:
    """Regression for #3244: ``import resource`` must be wrapped in try/except.

    The ``resource`` module is POSIX-only. PR #3235 added a bare
    ``import resource`` at module scope in ``kometa.py`` to bump
    ``RLIMIT_NOFILE`` from 256 to 4096 on macOS. That import crashed
    every Windows user at launch with::

        ModuleNotFoundError: No module named 'resource'

    The fix (PR #3244) wraps the import in ``try: import resource /
    except ImportError: resource = None`` and guards every subsequent
    use with ``if resource is not None:``.

    This test enforces the guard *statically* — it does not execute
    ``kometa.py``, so it catches the regression on every platform
    (including the Linux CI runner where ``import resource`` would
    succeed and hide the bug).
    """
    tree = _module_ast()

    # Walk top-level statements only. A nested ``import resource`` inside
    # a function body is fine; the bug is specifically a module-scope
    # unconditional import.
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "resource", (
                    "Found unconditional `import resource` at module scope in kometa.py. " "This crashes on Windows (POSIX-only module). " "Wrap it in `try: import resource / except ImportError: resource = None` instead. " "See PR #3244."
                )

    # Belt-and-braces: confirm the *guarded* form is still present, so a
    # well-meaning refactor that removes the try/except (e.g. while
    # cleaning up "dead code") gets caught here too.
    guarded_import_found = False
    for node in tree.body:
        if isinstance(node, ast.Try):
            for sub in node.body:
                if isinstance(sub, ast.Import):
                    for alias in sub.names:
                        if alias.name == "resource":
                            guarded_import_found = True
                            break
    assert guarded_import_found, (
        "Expected a `try: import resource / except ImportError: ...` block at module scope "
        "in kometa.py. Either the guard was removed, or the file layout changed in a way "
        "this test doesn't recognise. If the guard is genuinely no longer needed (e.g. the "
        "code was moved into a function), update this test."
    )


def test_issue_3244_resource_uses_are_guarded() -> None:
    """Regression for #3244: every ``resource.<attr>`` access must be guarded.

    A guarded import is necessary but not sufficient — if ``resource`` is
    ``None`` on Windows, calls like ``resource.getrlimit(...)`` will
    raise ``AttributeError``. This test asserts that every reference to
    ``resource.<something>`` at module scope lives inside an ``if
    resource is not None:`` block (or another guard that proves
    ``resource`` is truthy).
    """
    tree = _module_ast()

    # Collect every ``resource.X`` Attribute reference and the line it's on.
    resource_uses: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "resource":
            resource_uses.append(node.lineno)

    if not resource_uses:
        return  # No uses at all is fine — the import is also a no-op.

    # Find the line range of every ``if resource is not None:`` block at
    # module scope so we can confirm each use sits inside one.
    guarded_ranges: list[tuple[int, int]] = []
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            # Match `resource is not None` exactly
            left = node.test.left
            ops = node.test.ops
            comparators = node.test.comparators
            if isinstance(left, ast.Name) and left.id == "resource" and len(ops) == 1 and isinstance(ops[0], ast.IsNot) and len(comparators) == 1 and isinstance(comparators[0], ast.Constant) and comparators[0].value is None:
                guarded_ranges.append((node.lineno, node.end_lineno or node.lineno))

    for use_line in resource_uses:
        inside_guard = any(start <= use_line <= end for start, end in guarded_ranges)
        assert inside_guard, f"`resource.<attr>` at kometa.py:{use_line} is not inside an `if resource is not None:` block. " f"On Windows `resource` is `None`, so this will raise AttributeError. See PR #3244."
