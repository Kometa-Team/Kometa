# Multi-server library validation

Run from the repository root, using the environment containing Kometa's runtime dependencies and pytest.
All committed YAML uses fake credentials. No live server is contacted by the offline command.

```bash
.venv/bin/python scripts/validate_multi_server.py offline
```

The offline suite uses the real `ConfigFile` parser and server configuration objects, with API clients and library adapters mocked. It checks:

| Area | Automated coverage |
| --- | --- |
| Dispatch and inheritance | Shared YAML reaches Plex, Silo, and Emby constructors with the correct remote library names; no top-level Plex block is required. |
| Selection | Shared name selects every target; a target identity or pipe-separated selection selects only those targets. |
| Connection failure | A deliberately failed first adapter leaves later targets connected and present in the library map. |
| State isolation | Creating real `Library` instances produces distinct default cache table names, report paths, overlay backup paths, and report dictionaries. |
| Invalid input | Empty targets, conflicting selectors, unknown servers, wrong override container types, and nested selectors fail. |
| Playlists | Explicit target references resolve; implicit references use expanded identities. |
| Overlays and operations | Generated overlay and metadata backup settings reach each adapter through the real parser. Mock runs require stage completions, target summaries, local artifacts, and no logged errors, including selected-target cases. |
| Schema | Basic valid/invalid structures, plus two strict expected failures for unknown override attributes and invalid override value types. |
| Harness | Preparation cannot overwrite configs; fake process runs prove that missing collection completions, error output, unsuccessful exit codes, and missing surviving targets fail validation. |

The two schema tests use `xfail(strict=True)`: they remain visible as unresolved gaps. Once the schema is fixed, their unexpected success fails the suite so the markers can be removed.
Offline mocks do not establish live adapter compatibility, remote writes, full playlist construction, or correctness of timing summaries.

## Prepare a live run

Use a new output directory for each validation run. The script copies only TMDb settings and the three selected server connections from your source file, with no unrelated libraries, operations, webhooks, or file definitions. The source config is never modified.

```bash
.venv/bin/python scripts/validate_multi_server.py prepare \
  --source config/test-config.yml \
  --output config/multi-server-validation-01
```

The default source names are `my-plex`, `my-silo`, and `my-emby`. If `my-plex` is absent, preparation uses the source's top-level `plex` connection.
For different source server names, pass `--plex NAME`, `--silo NAME`, and `--emby NAME`.
The generated aliases remain `my-plex`, `my-silo`, and `my-emby` so playlist fixtures have stable references.

Preparation infers a remote library name when exactly one source library uses that named server; otherwise it uses `Movies`.
Inspect the generated `config.yml` and set its remote library names before running.
You can also set them during preparation:

```bash
.venv/bin/python scripts/validate_multi_server.py prepare \
  --source config/test-config.yml \
  --output config/multi-server-validation-02 \
  --library my-plex=Movies \
  --library my-silo=Cinema \
  --library my-emby=Films
```

Generated configs contain credentials. On Linux and macOS they are created with mode `0600`, and run directories with mode `0700`; Windows uses inherited file access rules. Keep them under your ignored `config/` directory. If the source uses environment substitutions, run with the same environment. Generated collection paths are absolute.

## Run live cases

The default cases write to your servers: they create/update a collection named **Kometa Multi-Server Validation**, with at most three items, and a Plex playlist named **Kometa Multi-Server Validation Playlist**. The collection uses sync mode, so use these names only for this test. Nonempty movie libraries are required. Overlay and operation cases are available explicitly; the default sequence remains unchanged.

```bash
.venv/bin/python scripts/validate_multi_server.py live \
  --directory config/multi-server-validation-01
```

The default sequence is:

1. `shared`: run the collection on all three targets and require three connection successes, three collection completions, and three distinct summary headings.
2. `selected`: run only `Movies@my-silo` and require exactly one connection and collection completion. Use `--target my-plex` or `--target my-emby` to change it.
3. `failure`: prepend an unavailable Plex target at `127.0.0.1:1`, then require that target to fail and every real target to connect and complete its collection.
4. `playlist`: run a playlist referencing `Movies@my-plex`, and require playlist completion without logged errors.

To run individual cases, repeat `--case` as needed. Each case directory must be new; the script refuses to overwrite previous artifacts.

```bash
.venv/bin/python scripts/validate_multi_server.py live \
  --directory config/multi-server-validation-01 \
  --case playlist-cross-server
```

The optional negative playlist case references Plex and Emby and requires the explicit “All defined libraries must be on the same server” rejection. An unexpected exception fails this check, exposing an adapter compatibility issue. It is excluded from the default sequence because it intentionally attempts an unsupported playlist.

### Overlay and operation cases

| Case | Targets | Action and checks |
| --- | --- | --- |
| `operations` | All configured targets | Export library metadata to a separate local YAML file per target; require completion, target summaries, and a nonempty metadata mapping in each file. |
| `operations-selected` | `--target` only | The same backup operation with exactly one connection and completion. |
| `overlays` | All configured targets | Apply a text badge to at most three title-sorted movies per target; require completion, upload messages, target summaries, and original poster files in separate target backup folders. |
| `overlays-selected` | `--target` only | The same overlay definition with exactly one connection and completion. |

Operations use only `metadata_backup`: they read the whole library and write local files, without editing remote metadata. This tests operation dispatch and backup isolation; it does not test mass metadata writes or deletion operations. Large libraries may need a longer timeout.

Run overlay cases only against dedicated test libraries with posters. The overlay engine reconciles the library's existing overlays, so a three-item builder limit does not prevent removal of other existing overlays. The badge says `MULTI SERVER TEST` and uses a bundled font. Retain the case directory: its original poster backups are needed to restore artwork. All new cases reject logged errors even when Kometa exits zero.

```bash
.venv/bin/python scripts/validate_multi_server.py live \
  --directory config/multi-server-validation-03 \
  --case operations --case operations-selected

# Prepare a separate directory pointing at dedicated test libraries first.
.venv/bin/python scripts/validate_multi_server.py live \
  --directory config/multi-server-overlay-validation-01 \
  --case overlays-selected --target my-silo
```

Use `--case overlays` for the shared overlay run. Each case uses its own cache and original poster directory. The selected overlay case therefore performs a fresh overlay run, rather than checking reuse of the shared case's cache. Avoid running it over posters already modified by another case: restore originals between cases, or run the cases separately on clean test libraries. For restoration, set `remove_overlays: true` under the shared `Movies` library in the same case config, then run Kometa with that config and `--overlays-only`. For a selected case, also pass `--libraries Movies@ALIAS` to preserve its scope. Inspect the restored posters before deleting any backups.

Each case gets its own config, console output, Kometa logs, cache, and timing artifacts. `results.json` records each assertion and the process return code. Timeout defaults to 900 seconds per case; override with `--timeout SECONDS`.
Kometa can exit zero despite logged errors, so the harness checks connection, completion, and summary markers as well. These checks are smoke-test evidence, not remote state verification.

### Shelf case

The explicit `shelves` case creates or updates four collections, each with at most three items, on every configured server:

- `Kometa Multi-Server Shelf Custom One` uses a template-provided `silo_shelf`.
- `Kometa Multi-Server Shelf Custom Two` uses a direct `silo_shelf`.
- `Kometa Multi-Server Shelf Automatic` inherits its file's disabled separator heading through `silo_shelves: true`.
- `Kometa Multi-Server Shelf Earlier` inherits a different heading with section `020`, loaded after the `060` category to verify section ordering.

On Silo, the first three land on **Kometa Multi-Server Validation Shelf** (section `060`); the fourth lands on **Kometa Multi-Server Earlier Shelf** (section `020`). Both category shelves must appear at the top, with the earlier shelf preceding the validation shelf despite file order; shelves without sections follow alphabetically by name, including “No heading”. Plex and Emby still build the collections and skip Silo-specific shelf attributes. The case requires all collection completions and target summaries, an assignment or unchanged membership message for each Silo collection, a section-order confirmation, and no logged errors. The shelf API confirms membership before these messages are emitted. No separator collection is created by these fixtures.

```bash
.venv/bin/python scripts/validate_multi_server.py live \
  --directory config/multi-server-validation-03 --case shelves
```

Repeat from a newly prepared run directory to check shelf reuse: membership messages should say `Unchanged`. Inspect Silo's Collections tab to verify both shelves, their order, and all four collections, and confirm any existing shelf members are still present. These log checks do not independently read back the full remote shelves after the run. Delete the four named validation collections on each server afterward, then remove the two validation shelves manually if no longer needed. Existing shelves are never deleted automatically. The `shelves` case is excluded from the default sequence.

## Inspect after a live run

- On each server, confirm the validation collection exists in the configured library, contains no more than three items, and contains items belonging to that server. Compare the selected-target case against the shared case: the other targets should not be modified by the selected run.
- In the failure case's logs, confirm the unavailable target failed first and later targets completed. Review any other errors; expected connection errors are allowed in that case.
- On Plex, confirm the validation playlist exists and contains at most three items. Confirm the optional cross-server playlist was not created. Offline reference checks alone do not test the complete playlist builder.
- For overlay cases, inspect the badge on each selected poster and compare the original poster backups under `CASE/overlays/Movies@ALIAS Original Posters/`. Check that other targets were untouched by a selected run. Local backup files and successful logs do not prove that remote artwork looks correct or that restoration works.
- For operation cases, inspect `CASE/Movies@ALIAS_Metadata_Backup.yml` and compare records with that server's library. Check that selected runs produce only the selected target's backup. These files may contain private library metadata.
- For an explicit-path collision check, set the same `report_path` on every target in a prepared config and inspect the resulting shared file; then override it per target and rerun in a fresh directory. Explicit paths are currently used verbatim and are not automatically isolated.
- Inspect timing output files and duplicate remote-name summaries. Repeat with the same remote library name on multiple servers if available. Timing data still has paths keyed by `library.name`, so this remains an audit item; distinct summary headings alone do not prove timing isolation.
- Run repository checks separately: `prek run --all-files --show-diff-on-failure`. The offline script does not claim to replace this gate.

Delete the named validation collections and playlists manually afterward. Restore overlay artwork before removing overlay run directories; keep metadata backups private. Remove local artifacts when no longer needed. The harness never removes server objects or previous run artifacts automatically.
