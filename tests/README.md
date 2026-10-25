# Kometa Test Suite

## Running tests

```bash
uv sync --group dev
uv run pytest tests/
uv run pytest tests/ -n auto
uv run pytest tests/ --cov=modules --cov-report=term-missing
uv run pytest tests/ --timeout=30 --durations=10 --durations-min=2.0
```

`-n auto` runs the suite in parallel with `pytest-xdist` (about 15s instead of
35s on a recent laptop) and can be added to any of the other commands.

CI runs the full suite in parallel on Ubuntu and Windows, on Python 3.12 (the
minimum) and 3.13 (the Docker image's version), including schema validation,
regression cases, fresh-process imports, per-test timeouts, and duration reporting.
CLI smoke checks separately verify `--help` and the expected missing-config
error on the same matrix. Line coverage is measured on Ubuntu with Python 3.13,
which enforces a 48% floor (measured coverage is about 51%); raise the floor in
`.github/workflows/test.yml` when coverage rises. Coverage is a guard against
accidental losses, not a reason to add tests that repeat implementation details.

## Where tests belong

Group tests by the behavior or production module they exercise. Add a separate
file when it makes a substantial area easier to navigate, rather than creating
one file per issue. Issue and PR references belong in short comments explaining
why a non-obvious case matters.

Shared `FakeLogger`, `FakeRequests`, `FakeResponse`, and `FakeCache` live in
`conftest.py`. Shared builder, Plex, and `Requests` factories live in `factories.py`;
do not import helpers from another `test_*.py` file.

The factories bypass constructors intentionally for isolated method tests.
Use real construction for initialization regressions and tests spanning the
collection lifecycle. Prefer explicit small fakes or mocks with a spec over
unrestricted mocks where the object contract matters.

## Choosing useful cases

Each case should protect a distinct behavior or boundary:

- Test production code, not a copied implementation of its algorithm.
- Assert outputs and meaningful side effects. A request merely happening or a
  result having the right length is often insufficient.
- Test rendering and summaries by their output, rather than matching Python
  source text. Structural checks remain appropriate for schema/catalog contracts.
- Parameterize equivalent setups, but avoid multiplying independent inputs into
  a Cartesian product unless their interactions are relevant.
- Preserve empty, missing, invalid, and boundary cases. Different example titles
  or positive counts alone rarely justify separate cases.
- Keep regressions for distinct failures. A narrow bug can still expose an
  important contract; avoid deleting coverage merely to reduce the test count.

Run focused tests while editing, then the full suite for shared fixtures or
production refactors. Do not add live Plex or external API requirements to unit
tests. Fix or remove obsolete tests rather than permanently skipping them.

## Regression cases

Use descriptive behavior names. Existing `test_regression_*`, `test_issue_*`, and
`test_bug_*` names remain valid; all run as part of the main suite. For a focused
local investigation, use:

```bash
uv run pytest tests/ -k "regression or issue_ or bug_"
```

The import smoke check runs in a fresh process with the builder-first import
order used by the CLI. It checks module-level imports, not imports inside uncalled
functions. The child process has its own timeout and a larger pytest timeout to
allow startup on both platforms.
