# `scripts/`

Developer-facing utilities. Anything in here is meant to be invoked by
contributors or by CI — never imported as a library by `modules/` or
`kometa.py`.

## `pyright_baseline.py` — ratcheting type-check gate

We use [pyright](https://github.com/microsoft/pyright) for static type
checking in basic mode. Because Kometa is a large, historically untyped
codebase, requiring zero pyright errors is unrealistic. Instead we use a
**ratcheting baseline**: CI fails only when the per-file error count
*increases*. Fixing errors silently lowers the bar; new errors trip the
gate.

### The three operations

```bash
# Show what's in the current baseline
python scripts/pyright_baseline.py --show

# Check current state vs baseline (what CI runs)
python scripts/pyright_baseline.py --check

# Regenerate the baseline after intentionally fixing or accepting errors
python scripts/pyright_baseline.py --regenerate
```

### How the gate decides

* **Per-file count went UP** → CI fails. Message tells you which file.
* **Per-file count went DOWN** → CI passes. Message suggests
  regenerating the baseline so future PRs are held to the new (lower)
  bar.
* **All counts the same** → CI passes silently.

We chose per-file (not a single global total) because a global counter
lets you swap one error in `builder.py` for one in `plex.py` and the
gate never notices. Per-file catches that. We chose count (not
line/rule fingerprints) because anything more granular breaks on
formatting changes and refactors.

### When to regenerate the baseline

| Situation | What to do |
| --- | --- |
| You fixed real pyright errors in your PR | `python scripts/pyright_baseline.py --regenerate`, commit the new `.pyright-baseline.json` |
| You moved code between files | Same — net delta is what matters |
| You're intentionally accepting a NEW error | Don't. Either fix it, suppress just that line with `# pyright: ignore[ruleName]`, or open an issue and discuss |
| You added a new module | Run `--regenerate`; the new file appears with its starting count |
| The baseline drifts because pyright shipped a new version | Regenerate and call it out in the commit message |

### Suppressing a single line

When you genuinely need to ignore one error (e.g. dynamic dispatch
that pyright can't follow), prefer the narrow form:

```python
foo.bar  # pyright: ignore[reportOptionalMemberAccess]
```

Avoid the broad `# pyright: ignore` or `# type: ignore` — they silence
everything on the line, including new errors that show up later.

### Opting a file into strict mode

If you write a new, well-typed module, you can hold it to a higher
standard by adding this to the top of the file:

```python
# pyright: strict
```

That file then participates in pyright's strict mode regardless of the
project-wide `typeCheckingMode = "basic"` setting. The baseline still
applies, but you've raised the floor for that one file.
