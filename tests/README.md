# Kometa Test Suite

## Running the tests

```bash
# Full suite (~7s)
pytest tests/

# With coverage
pytest tests/ --cov=modules --cov-report=term-missing

# Only fast checks (lint-style)
pytest tests/test_schema_validation.py
```

The CI pipeline at `.github/workflows/test.yml` runs the full suite plus
schema validation, regression checks, performance timing, and a smoke test on
every PR to `nightly`.

## Test layout

One file per module is the goal. Most modules already follow this:

```
tests/
├── conftest.py            # Shared fakes: FakeLogger, FakeRequests, FakeCache
├── test_cache.py          # tests for modules/cache.py
├── test_config.py         # tests for modules/config.py
├── test_plex.py           # tests for modules/plex.py
└── ...
```

When you add tests for an existing module, put them in that module's
test file. Only create a catch-all file (e.g. `test_small_modules.py`)
for genuinely tiny modules that don't need their own file.

## Shared fakes

`tests/conftest.py` exports:

| Fake             | Purpose                                                |
| ---------------- | ------------------------------------------------------ |
| `FakeLogger`     | Captures log calls; satisfies the `logger` module API. |
| `FakeResponse`   | A `requests.Response` lookalike with `.json()`/`.text`. |
| `FakeRequests`   | A `Requests` wrapper that returns canned responses.    |
| `FakeCache`      | An in-memory stand-in for `modules.cache.Cache`.       |

Use these instead of `MagicMock` when you can — they catch typos in
attribute names that `MagicMock` would silently allow.

## Regression test convention

Tests that exist specifically to prevent a fixed bug from coming back
use one of these name prefixes (the CI `regression` job filters with
`-k "regression or issue_ or bug_"`):

```python
def test_regression_<short_slug>():     # general regression test
def test_issue_<gh_number>():           # ties to a GitHub issue
def test_bug_<short_slug>():            # internal/unreported bug
```

Always include a docstring that links to the issue/PR and a one-line
description of the bug:

```python
def test_issue_3168_anime_map_writes_to_wrong_column():
    """Regression for #3168 — cache.update_anime_map() was writing the
    anidb id into the anilist column on UPDATE (worked on INSERT).
    See modules/cache.py around line 1234.
    """
    cache = Cache(":memory:")
    cache.update_anime_map(anidb=111, anilist=222, ...)

    row = cache.query_anime_map(anidb=111)
    assert row["anilist"] == 222  # was 111 before the fix
```

This convention serves three purposes:

1. **CI surfaces them as a named suite** — "all 7 regression tests
   passed" is a stronger signal than "441 tests passed".
2. **Future-you knows why the test exists** — random asserts age badly.
3. **PR reviewers can grep for `test_issue_<number>`** to verify a fix
   landed with the test that protects it.

## Coverage gate

CI enforces **20% line coverage on `modules/`** (current baseline is
~22.5%). If your PR drops coverage below the threshold, the `test` job
fails. The gate ratchets up over time as coverage improves — bump it in
`.github/workflows/test.yml` after a sustained increase.

## Skipping tests

Avoid `@pytest.mark.skip` unless the skip is conditional. If a test is
broken, fix it or delete it — a permanently-skipped test is dead code
that gives false confidence.
