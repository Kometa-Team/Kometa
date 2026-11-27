# "Source Integrity: MODIFIED" on a stock develop image

## Summary

A user on the `kometateam/kometa:develop` image (Kometa 2.5.5-build1) sees **Source Integrity: MODIFIED**. The report lists many modified files, including `VERSION`, `kometa.py` and most of `modules/`. It also lists files as "Added", such as `modules/lidarr.py` and `modules/seerr.py`.

The most likely cause is a **stale `KOMETA_GIT_SHA` environment variable** in the container, left over from an older image. The integrity check prefers that variable to the commit baked into the image, so it compares current code against an older upstream commit. The user's code is probably unmodified.

## The report

```text
Version: 2.5.5-build1 (Docker: develop)
Source Integrity: MODIFIED
Modified: .pre-commit-config.yaml, AGENTS.md, VERSION, defaults/both/genre.yml,
          docker/Dockerfile.base, docker/uv-bootstrap.txt, kometa.py, modules/* ..., and 16 more
Added:    defaults/.../flags (ai, cw, dd, hk, mo, pr; round and square),
          modules/apple_chart.py, lastfm.py, lidarr.py, schedule_mode.py, seerr.py,
          spotify_chart.py, ytmusic.py, scripts/build_docs.py, and 1 more
Platform: Linux-3.10.105-x86_64-with-glibc2.41
```

## How the check picks its comparison commit

`check_integrity` downloads the upstream GitHub archive for a commit and compares the local tree against it. `_read_identity` in `modules/integrity.py` (line 293) chooses that commit in this order:

1. The Git HEAD of the install folder, if it is a Git checkout
2. The `KOMETA_GIT_SHA` environment variable
3. The `/.kometa_sha` file

The file is only read when neither of the first two is set.

The `Dockerfile` records the commit in both places:

- `ARG`/`ENV KOMETA_GIT_SHA` (lines 11–12), plus the `org.opencontainers.image.revision` label (line 15)
- `/.kometa_sha` (from line 34), written only if the SHA is a valid full commit and `VERSION` matches `KOMETA_VERSION`

The file is checked against `VERSION` at build time; the environment variable is not. At runtime, the environment variable can be overridden or go stale, and it still wins.

## Why this points to a stale commit

- **The "Added" files are not new.** They arrived in `nightly` between 13 and 26 October 2026:

  | File | Added to `nightly` |
  |---|---|
  | `modules/lidarr.py` | 13 Oct |
  | `modules/ytmusic.py`, `modules/lastfm.py` | 15 Oct |
  | `modules/seerr.py`, `modules/apple_chart.py`, `modules/spotify_chart.py` | 17 Oct |
  | `modules/schedule_mode.py` | 18 Oct |
  | `scripts/build_docs.py` | 26 Oct |

  Both `master` (2.5.5, 11 Nov) and `develop` contain them. Any commit matching this build has them, so the comparison commit must be from before 13 October.
- **`VERSION` shows as modified.** The local file says `2.5.5-build1`, so the comparison commit has a different `VERSION` and is a different build.
- **The kernel is Synology's.** `Linux-3.10.105` is the DSM kernel. Synology Container Manager copies an image's environment variables into the container's settings when the container is created. Pulling a newer image and restarting doesn't refresh them. Portainer's "duplicate/edit" and similar "recreate with the same settings" tools behave the same way. The `Dockerfile` already has a comment about this happening to `PATH` in "a container kept from an older image".

## How to confirm it

```bash
docker exec <container> printenv KOMETA_GIT_SHA
docker exec <container> cat /.kometa_sha
docker image inspect kometateam/kometa:develop \
  --format '{{index .Config.Labels "org.opencontainers.image.revision"}}'
```

If the first value differs from the other two, this is the cause. That commit on GitHub should be dated before 13 October.

## How the user can fix it

- In Container Manager (or the equivalent), delete `KOMETA_GIT_SHA` from the container's environment settings. Delete any other variables copied from the image too, such as `BRANCH_NAME`.
- Or recreate the container from the image, or from a compose file that doesn't set `KOMETA_GIT_SHA`.

## If the three values match

Less likely causes:

- **A bind mount over code:** a volume over `/modules`, `/defaults` or similar holding an older copy. The check skips only `config` and a few metadata paths, so mounted code is compared like any other file.
- **A self-built or fork image:** built with a stale `--build-arg KOMETA_GIT_SHA`, or from a working tree with uncommitted changes.
- **A user-set `KOMETA_GIT_SHA`** in a template or compose file that has since been updated.

## Suggested changes to Kometa

1. **Prefer the baked file in Docker.** In `_read_identity`, when running in the Docker profile and `/.kometa_sha` exists, use it. If `KOMETA_GIT_SHA` disagrees, log a warning, for example: *"KOMETA_GIT_SHA in the container environment does not match this image (probably left from an older image); remove it from the container settings."* Another option: treat a file/variable mismatch like the existing Git/variable mismatch, which raises `Unavailable("conflicting build identities")`, rather than reporting MODIFIED.
2. **Show the comparison commit.** Print the short SHA and its date in the "Source Integrity" block. In this case, a commit dated weeks before the reported version would have pointed straight at the cause.
