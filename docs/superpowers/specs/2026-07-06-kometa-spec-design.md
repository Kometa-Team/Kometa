# kometa-spec: Single Source of Truth for config.yml Rules

**Date:** 2026-07-06
**Status:** Approved design, not yet implemented

## Problem

The rules for what is legal in Kometa's YAML files are encoded in Python:
`modules/config.py` has ~213 `check_for_attribute` call sites carrying types,
defaults, allowed values, and int ranges as literal kwargs. The JSON schemas in
`json-schema/` are hand-maintained copies of those rules, updated by separate
PRs. There is no single source of truth, so code and schema drift.

The Kometa-Team **QuickStart** config editor needs the same knowledge to
generate its forms, which makes a shared, external source of truth worth the
cross-repo friction.

## Scope

- **In scope (phase 1):** config.yml rules only — the `check_for_attribute`
  domain and `config-schema.json`.
- **Out of scope (later phases, same pattern):** collection / metadata /
  overlay / playlist file rules (builder.py's builder and filter registries).
- **Hard constraint:** runtime behavior is preserved exactly — same defaults
  written back to user configs, same warnings, same run outcomes. The refactor
  is invisible to users.

## Decision

**Approach A — data-first YAML spec in a shared package.** The spec is inert
YAML data in a new repo; Kometa's validation engine is untouched and only its
inputs move; a Python access layer serves both Kometa and QuickStart; the JSON
schema is emitted from the spec.

Rejected alternatives:

- *JSON Schema as the source* (custom `x-kometa-*` keywords): hand-editing a
  431 KB JSON file, poor fit for Kometa semantics (write-back, translations),
  painful diffs.
- *Python declarative models* (pydantic/dataclasses): the source of truth
  becomes Python code again, and non-Python consumers are locked out.

## The Spec Repo

**Repo:** `Kometa-Team/kometa-spec`, publishing data-only package
`kometa-spec` to PyPI.

```
kometa-spec/
  spec/config/          # the source of truth
    plex.yml
    tmdb.yml
    settings.yml
    ... (one file per config.yml top-level section, ~20 files)
  src/kometa_spec/      # thin Python access layer
    loader.py           # load + merge spec files into AttributeSpec objects
    metaschema.py       # validates the spec files themselves
    emit_jsonschema.py  # spec -> config-schema.json
  tests/
```

**Spec format.** One entry per attribute, mirroring `check_for_attribute`'s
vocabulary exactly (that vocabulary is the behavior contract). Example —
today's call:

```python
check_for_attribute(self.data, "sync_mode", parent="settings",
                    default="append", test_list=sync_modes)
```

becomes this entry in `spec/config/settings.yml`:

```yaml
sync_mode:
  type: str                # var_type
  default: append
  allowed: [append, sync]  # test_list
  description: Default sync mode for collections without one set.
  # optional keys, only when they differ from defaults:
  # default_is_none, translations, int_min / int_max, secret,
  # writeback (default true), throw, deprecated, since
```

**Key rule:** every field in the spec is a datum, never logic. Conditional
behavior (Plex token redaction, library-level overrides of settings) stays in
Kometa's engine; the spec records only per-attribute facts. QuickStart-facing
fields (`description`, `group`, `secret`) live in the same entry so one PR
updates validation, schema, and UI together.

**Meta-schema.** The spec is self-validating: unknown keys, bad types, or
`allowed`/`default` contradictions fail the spec repo's CI. `load()` also
validates at import, so a malformed spec cannot ship or start.

**Access layer.** `kometa_spec.load("config")` returns plain frozen
dataclasses with no imports from either app, so any Python consumer (or, via
the YAML directly, any non-Python consumer) can use it.

## Kometa Integration

**Runtime wiring.** Kometa depends on `kometa-spec>=1.0,<2`. A small adapter
in `config.py` sits between call sites and the untouched engine:

```python
spec = kometa_spec.load("config")

def check(attribute, parent=None, **overrides):
    entry = spec.lookup(parent, attribute)
    return check_for_attribute(self.data, attribute, parent=parent,
                               **entry.kwargs(), **overrides)
```

Call sites become `check("sync_mode", parent="settings")`. The `**overrides`
escape hatch handles the few sites where a parameter is genuinely
runtime-dependent (e.g., a default computed from another value) — those stay
in code, explicitly.

**Parity gate.** Before any call site is converted, a test extracts today's
literal kwargs from all ~213 call sites and asserts the spec produces
identical kwargs for every attribute. It remains permanently as the drift
alarm: adding an attribute in code without a spec entry (or vice versa) fails
CI.

**Schema emission.** `json-schema/config-schema.json` stays committed in
Kometa at the same path (users' `$schema` URLs keep working) but becomes a
generated file: CI regenerates it from the pinned spec version and fails the
PR if the committed file differs. `modules/validator.py` is unchanged — it
keeps reading the JSON file.

**Cross-repo dev loop.** Branch on kometa-spec, `pip install -e
../kometa-spec` locally, PR both repos, merge spec first, release (automated
tag → PyPI), bump the pin in the Kometa PR. Attribute additions are roughly
monthly, so this stays tolerable.

## QuickStart Consumption

QuickStart imports the same package and reads UI-facing fields:
`description`, `group`, `secret`, `allowed`, `default` drive form generation
(`secret: true` → password input; `allowed` → dropdown; `default` →
pre-fill). It may also call the emitter for a JSON Schema usable in the
browser. Adoption happens in their repo at their pace.

## Versioning and Release

Semver:

- **Patch** — descriptions, groupings, doc-facing metadata.
- **Minor** — new attributes, new allowed values (additive; old configs stay
  valid).
- **Major** — removing/renaming attributes, changing types or defaults, or
  changing the spec file format itself.

Both consumers pin `>=X.Y,<X+1`. Kometa's CI regenerates the schema from the
*pinned* version, so a spec release never silently changes Kometa's published
schema — changes land only when Kometa bumps its pin, in a reviewable PR.
Releases are automated (tag → PyPI); both apps can also install from a git tag
(`pip install git+...@vX.Y.Z`) so PyPI lag never blocks a nightly.

**Contributor rule, enforced by the parity test:** to change what's legal in
config.yml, you edit kometa-spec. Kometa PRs that change validation without a
spec bump fail CI with a message pointing at the spec repo.

## Error Handling

- Spec package fails loudly and early: `load()` raises on any meta-schema
  violation; Kometa treats that as a fatal startup error (a broken release
  shipped, not a user mistake).
- User-facing validation errors are unchanged: same wording, same source
  (`check_for_attribute`), because the engine and its message strings never
  move.
- An attribute present in config.yml but absent from the spec behaves exactly
  like today's unknown attributes: ignored by `check_for_attribute`, surfaced
  by the JSON-schema pre-flight as a gap. No new user-facing failure modes.

## Testing

- **Spec repo:** meta-schema tests, loader round-trip tests, emitter
  golden-file test (spec in → known-good schema fragment out).
- **Kometa:** the parity test (spec kwargs ≡ literal kwargs, all call sites)
  runs before, during, and forever after migration; existing `tests/` suite
  and `validator.py` tests are the behavioral backstop; a CI check verifies
  committed `config-schema.json` matches emission.
- **Golden config:** `json-schema/kitchen_sink_config.yml` must parse to
  identical results pre- and post-migration.

## Migration Order (each step independently shippable)

1. **Create kometa-spec repo:** format, meta-schema, loader. Spec content is
   seeded by a one-off script that parses the ~213 call-site kwargs out of
   `config.py` (mechanical extraction, then hand review).
2. **Parity test lands in Kometa** against the seeded spec — proves the
   extraction was faithful.
3. **Emitter + CI check:** generated `config-schema.json` replaces the
   hand-maintained one. *Caveat:* the first regeneration will surface existing
   code/schema drift; each discrepancy is reviewed individually ("which one is
   right?") and some may become Kometa bug fixes. This is the least mechanical
   step.
4. **Convert `config.py` call sites** to the adapter, section by section.
5. **QuickStart adopts the package** (their repo, their pace).
