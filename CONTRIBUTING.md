# Contributing to Kometa

Thanks for taking the time to contribute! This document covers everything you need to know before opening a PR.

## Before you start

- **Bugs and support** - use the [Kometa Discord](https://kometa.wiki/en/latest/discord/) for support questions. Bug reports go through [GitHub Issues](https://github.com/Kometa-Team/Kometa/issues) using the provided template.
- **Feature requests** - submit and vote at [features.kometa.wiki](https://features.kometa.wiki). Do not open feature request issues on GitHub.
- **Pull requests** - all PRs must target the `nightly` branch. PRs to `master` or `develop` will be rejected automatically by CI.

## Branching model

| Branch | Purpose |
| ------ | ------- |
| `nightly` | Active development - all PRs target here |
| `develop` | Pre-release staging |
| `master` | Stable releases only |

Create your branch from `nightly` and keep it rebased against `nightly` before opening a PR.

## Versioning

Kometa follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **Patch** (`x.y.Z`) - backwards-compatible bug fixes only.
- **Minor** (`x.Y.0`) - new features or enhancements that don't break existing behaviour.
- **Major** (`X.0.0`) - breaking changes.

The `VERSION` file in the repo root drives the build numbering. When the team decides to bump to the next release (e.g. `2.4.0`), the VERSION file is updated from `2.3.x-buildN` to `2.4.0-build0`. Every subsequent PR merged to `nightly` that touches code, defaults, fonts, or the Dockerfile will auto-increment the build number via CI.

## Setting up your environment

```bash
# Clone and install dev dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt

# Install pre-commit hooks (runs black, isort, flake8, and spellcheck automatically)
pre-commit install
```

Python 3.12+ is required.

## Code style

All code must pass the following before CI will accept it. The pre-commit hooks run these automatically on each commit.

| Tool | Purpose | Config |
| ---- | ------- | ------ |
| `black` | Formatting | `pyproject.toml` - line length 256 |
| `isort` | Import ordering | `pyproject.toml` - black profile |
| `flake8` | Linting | line length 256, ignores `E203 W503 E501` |
| `mypy` | Type checking | `pyproject.toml` |
| `bandit` | Security scanning | excludes `tests/`, `config/`, `.venv/` |

Run them manually at any time:

```bash
black .
isort .
flake8 .
mypy .
bandit -r modules/
```

## Testing

```bash
pytest tests/

# Single file
pytest tests/test_builder.py

# Single test
pytest tests/test_builder.py::TestName
```

Tests live in `tests/test_builder.py` and `tests/test_textfile.py`. Run the full suite locally before opening a PR. If your change touches a builder or text file path, add or update a test.

## Changelog

Any PR beyond a minor tweak (typo fix, value replacement) must include a `CHANGELOG.md` entry under `## [Unreleased]`.

Use the appropriate section - standard keepachangelog types take priority; Kometa-specific sections are also available:

| Section | Use for |
| ------- | ------- |
| `### Added` | New features, builders, CLI flags, config options |
| `### Changed` | Changes to existing behaviour |
| `### Deprecated` | Features that will be removed in a future release |
| `### Removed` | Removed features |
| `### Fixed` | Bug fixes |
| `### Security` | Security fixes |
| `### Requirements` | Dependency additions or version bumps |
| `### Performance` | Performance improvements |
| `### Docs` | Documentation-only changes |
| `### Defaults` | Changes to the shipped default collection/overlay files |

Keep entries concise and user-facing - describe what changed and why it matters to the user, not implementation detail. Reference the related issue number where applicable (e.g. `#3006`).

## Pull request checklist

- [ ] Branch is up to date with `nightly` (`git rebase upstream/nightly`)
- [ ] All pre-commit hooks pass
- [ ] Tests pass locally
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] Documentation updated if the change affects user-facing behaviour
- [ ] PR is kept small and focused - one logical change per PR where possible
- [ ] PR description explains what the change does and how it was tested

Use [Draft PRs](https://github.blog/2019-02-14-introducing-draft-pull-requests/) for work in progress. Avoid force-pushing to a PR branch once it has received review comments.
