---
search:
  boost: 4
---
# Help

<span id="help-troubleshooting"></span>

Find the cause of a failed run, understand a log message, or recover from an unwanted change.

<span id="basic-log-file-troubleshooting"></span>

## Start here

1. **Open the latest `meta.log`** in the `logs` directory beside your `config.yml`.
2. **Read `CRITICAL` messages first, then `ERROR` messages.** Include the lines around a message when investigating its cause.
3. **Check your version** near the beginning or end of the log. A `Newest Version` line means an update is available.
4. **Match your problem below.** If it remains unresolved, [share the complete log with support](#get-further-help).

- [Configuration and connection errors](#fix-common-problems)
- [Plex errors and image uploads](#plex-errors-and-image-uploads)
- [Slow runs and scheduling](#performance-and-scheduling)
- [Update Kometa](#update-kometa-or-switch-branches)
- [Undo changes](#undo-changes-and-recover)
- [Migrate an older configuration](#migration-and-older-configurations)

<span id="log-files-and-where-to-find-them"></span>

## Find and read your logs

### Log locations and rotation {#locating-log-files}

`meta.log` contains the latest run. Previous runs are numbered: `meta-1.log` is the previous run, `meta-2.log` the one before that. **Use the file without a number when sharing your latest run.**

??? info "Older log filenames"

    Older releases used `meta.log.1`, `meta.log.2`, and so on. You can rename those files if you no longer need the old naming convention.

### Checking your version {#checking-kometa-version}

Look near the beginning or end of `meta.log` for your installed version. Follow [the update guidance](#update-kometa-or-switch-branches) if a newer version is available.

### Understanding message levels {#understanding-log-file-event-types}

| Level | What to do |
|:------|:-----------|
| `CRITICAL` | Fix the reported problem so Kometa can run properly. |
| `ERROR` | Investigate the failed task; most errors need action, though an empty result may be expected. |
| `WARNING` | Read the message and decide whether it affects your intended result. |
| `INFO` / `DEBUG` | Normal progress and diagnostic information; no action is usually needed. |

<span id="other-troubleshooting-examples"></span>

## Fix common problems

### Startup and configuration errors

??? info "A required section is missing"

    `YAML Error: metadata, collections, or dynamic_collections attribute is required` means the loaded file lacks a required top-level section. For a collection file, put definitions beneath `collections:`:

    ```yaml
    collections:
      Marvel Cinematic Universe:
        mdblist_list: https://mdblist.com/lists/stealthgyro/marvel-cinematic-universe-mcu
    ```

    This example creates a collection from the linked list. Templates alone do not define a collection.

??? info "YAML reports a duplicate key"

    An error such as `found duplicate key "collection_order"` identifies a setting repeated in the same mapping. Use the line numbers in the error to find both entries, then keep the intended value once:

    ```yaml
    collections:
      Marvel Cinematic Universe:
        collection_order: custom
        mdblist_list: https://mdblist.com/lists/stealthgyro/marvel-cinematic-universe-mcu
    ```

    Here, `custom` keeps the builder's order. Adding another `collection_order` to this definition would be a duplicate.

??? info "A file does not exist"

    `YAML Error: File Error: File does not exist /Users/Lucky/Kometa/config/Movies.yml` means Kometa cannot find the file at the reported path. Check the filename, path, and, for Docker, whether the file is visible inside the container.

### Connection and authentication problems

Check the URL and credentials for the service named in the error. Start with [Plex connection settings](../config/plex.md) or the relevant service's configuration page. MyAnimeList uses [Kometa Utilities Authentication](../config/authentication.md).

`Input Failed` can mean an expired token or password, or a builder whose service has not been configured. Read the surrounding log entries to identify the service and required setup.

### Common log messages {#common-log-file-messages}

<span id="critical"></span>
<span id="error"></span>
<span id="warning"></span>
<span id="info"></span>

??? info "TMDb cannot be reached"

    **Message:** `[CRITICAL] Failed to Connect to https://api.themoviedb.org/`

    Kometa could not complete a TMDb API request and moved on from that step. Check whether TMDb is available and responding, then retry.

??? info "A Plex library, actor, or matching item is missing"

    - `Playlist Error: Library: XYZ not defined`: check that the library is defined in your config and its name matches Plex exactly.
    - `Plex Error: resolution: No matches found with regex pattern XYZ`: check the pattern if you expected matching items.
    - `Plex Error: No Items found in Plex`: check the builder criteria if you expected results.
    - `Plex Error: actor: Mel B not found`: Kometa could not find the actor to create the collection. Ask in the Discord `#kometa-help` channel if you need help resolving it.

    Empty builder or regex results can be expected and may need no action.

??? info "An IMDb URL cannot be parsed"

    **Message:** `IMDb Error: Failed to parse URL:`

    Open the URL in your browser to check that it exists and returns the expected results. Check that you are using the appropriate IMDb builder for that URL.

??? info "A source is missing an ID or rating"

    These messages mean Kometa cannot cross-reference an item between sources or retrieve the requested data:

    - `MDBList Error: No TVDb ID found for Nightfall (2022)`
    - `MDBList Error: Not Found`
    - `Convert Warning: No TVDb ID Found for TMDb ID: 15733`
    - `Convert Warning: AniDB ID not found for AniList ID: 21400`
    - `Convert Warning: No TVDb ID or IMDb ID found for AniDB ID: 14719`
    - `Convert Warning: AniDB ID not found for MyAnimeList ID: 36838`

    Check the item's record on the named source. An external ID may be missing, the corresponding item may not exist on the other service, or a requested rating may be unavailable. Correct missing data on the relevant site where possible.

    For example, TMDb ID `15733` referred to *The Two Mrs. Grenvilles* without a TVDb ID when that warning was recorded.

??? info "A person's poster was updated"

    **Message:** `[INFO] Detail: TMDb_person updated poster to [URL]`

    Kometa downloaded a person image from TMDb. No repair is needed. If you want a consistent poster style, replace it with your preferred artwork or request a matching Defaults-style people poster.

### Plex errors and image uploads

An HTTP 500 response means the server handling a request encountered an unexpected error. In this context, it often comes from Plex. Check the server named in the error before changing your Kometa configuration.

1. In Plex, open **Settings > Manage > Console** and filter for errors and warnings.
2. Check the Plex server or container logs for database messages such as `Busy DB Sleeping for 200ms`.
3. Check the image size: Plex can return a 500 error for an upload larger than 10 MB.
4. For hosted services such as Appbox, ask the provider about request limits and permissions to upload custom posters to its central metadata repository.

The fix depends on the server and setup. Kometa support cannot resolve a server-side 500 error without the underlying Plex or hosting issue being addressed.

#### Temporary Plex image upload errors

Kometa retries poster, background, logo, and square-art uploads when Plex returns HTTP 502, 503, or 504. It makes at most three upload attempts, waiting 2 seconds before the second attempt and 5 seconds before the third. If all three attempts receive these errors, Kometa logs the item, image, and final HTTP status, skips that image update, and continues the run without a traceback. This also applies to artwork resets, overlay application, and overlay removal. Failed overlay removal keeps the overlay label and original poster backup so removal can be retried. Retry messages identify the item and image.

A gateway error does not establish that the image is missing. URL uploads still make these three attempts even if the source URL is permanently broken; this can add 7 seconds for that image on each run. Failed uploads are not cached as successes. Source URL validation and fallback are separate from these Plex retries. Other errors retain their existing handling and diagnostic details.

### Source integrity

Source integrity is checked alongside the startup system information, with a maximum wait of 30 seconds for both cached file checking and baseline retrieval. The log reports `Source Integrity: Verified`, `Source Integrity: MODIFIED`, or `Source Integrity: Check unavailable` with a reason and an explanation that local files were not verified. If the startup time limit is reached, Kometa continues with `Source Integrity: Check unavailable (startup time limit reached; local files were not verified)`. There is no later integrity result during library processing. The end-of-run `Source Integrity Summary (startup check)` repeats the startup result without waiting for or adopting a late result. A timeout in this summary describes the startup check, not a detected file change. Modified installations list changed, missing, and added files. An unavailable check means the comparison could not be completed; it does not indicate detected file changes. Only `MODIFIED` reports confirmed differences. This is a support diagnostic and never prevents Kometa from running.

The diagnostic is enabled by default. Use `--no-source-integrity` or set `KOMETA_SOURCE_INTEGRITY=false` to disable it, including file checks and network requests. Use `--source-integrity` or `KOMETA_SOURCE_INTEGRITY=true` to enable it. As with other runtime options, environment variables take precedence over CLI flags. Disabled checks report `Source Integrity: Disabled (source-integrity option)` in the startup header and end-of-run summary.

??? info "Baseline caching, installation identity, and exclusions"

    The baseline comes from official upstream source pinned to the installed commit. It is cached under `.source-integrity/` in the active config directory for subsequent offline checks. After a new cache is successfully saved, Kometa retains it and the two most recently written other caches for the same repository and installation profile. This limits storage growth while allowing installations at different commits to share a config directory without evicting each other on every update. Downloads use temporary disk files. Upstream retrieval has a separate 180-second deadline, so a slow download can continue after the 30-second startup wait. If the process remains running and retrieval completes within that deadline, the worker can silently save the baseline for a later run; it does not log another result or change the startup result repeated in the summary. Scheduled starts for the same installation, config directory, and profile reuse an active check rather than launching another download. Each start still has its own 30-second wait and saved startup result. The worker is a daemon: if Kometa exits before retrieval completes, no baseline is saved and the next run retries.

    Runtime config, logs, virtual environments, compiled Python files, desktop metadata, and integrity metadata are excluded. Differences consisting only of Windows versus Unix line endings are tolerated in known text files; binary files require exact bytes. Docker checks Kometa-owned files and directories rather than the container operating system. Repository-only CI/test files excluded from upstream source archives are outside the comparison.

    Git installs use the installation's HEAD; Docker builds carry `KOMETA_GIT_SHA` when provided; `.kometa_sha` is an identity hint when present. The candidate commit must belong to an official upstream branch before a baseline is cached. PR and test images whose commits are outside official upstream history report Check unavailable. Older images or installations without exact commit metadata also report Check unavailable; recreate the container with an image containing that metadata. Cache corruption, unavailable upstream data, and inspection errors report Check unavailable. The diagnostic cannot protect against deliberate replacement of its own implementation or provenance metadata.

## Performance and scheduling

### Improving performance

Enable [Kometa caching](../config/settings.md) where appropriate, schedule runs outside Plex maintenance, and limit expensive operations and episode overlays to the libraries that need them.

### Slow runs

Plex updates require a request and a response for each affected item. A response can take seconds or minutes, so hundreds or thousands of updates add up. Mass operations may process every item in a library; episode updates can involve hundreds of thousands of items.

??? info "Why overlays and people collections take longer"

    For each item requiring an overlay update, Kometa checks the applicable overlays and compares the current poster. If changes are needed, it retrieves and saves the source artwork, draws the overlays, saves the final image, uploads it to Plex, and waits for confirmation. More overlays and more episodes increase that work.

    Actor, director, producer, and writer Defaults retrieve cast or crew data for your library and calculate who appears most often. Larger libraries take longer to process.

### Scheduling different tasks

Yes, the recommended approach is to set up a new library for the Operations/Overlays, mapping it back to the original library, 
and then scheduling the library, as outlined below

```yaml
libraries:
  Movie Operations:           # NAME DOESN'T MATTER BUT MUST BE UNIQUE
    library_name: Movies      # THIS MUST MATCH A LIBRARY IN PLEX
    schedule: weekly(monday)
    operations:
      split_duplicates: true
    overlay_files:
      - default: resolution
```

See [Scheduling runs](guides/scheduling.md) and [Schedule syntax](../config/schedule.md) for the complete procedure.

## Update Kometa or switch branches

Back up your configuration before updating. For a local Git installation, inspect `git status` and preserve any local changes before pulling updates or switching branches. Do not discard a stash or reset modified files as a routine update step.

- **Local installation:** follow the update and branch-switching instructions in the [local walkthrough](install/index.md#path-local). Use `master` for stable releases or `develop` for the public beta, and install the dependencies required by that checkout in its virtual environment.
- **Docker:** pull the desired `kometateam/kometa` image and recreate the container while retaining the configuration volume. Use `latest` for stable releases or `develop` for the public beta. Follow the [Docker walkthrough](install/index.md#path-docker) or your platform's walkthrough; see [Docker images](install/images.md) for available tags.
- **Downloaded archive:** follow the local installation instructions for the new release and retain your configuration and asset files.


## Undo changes and recover

!!! warning "Recovery depends on backups"

    Kometa does not keep a history of every change and has no global undo. Restoring Plex appdata from a backup taken before using Kometa is the only way to undo all of its changes at once.

### Collections

Delete Kometa-created collections manually in Plex or using Kometa's collection-deletion options. Collections created outside Kometa that you explicitly configured Kometa to delete cannot be restored without a backup.

### Playlists

Delete Kometa-created playlists manually in Plex.

### Overlays

Use [`remove_overlays`](../config/libraries.md#remove-overlays) to restore the clean posters that the overlays were applied to.

### Metadata

A backup made **before** the changes is needed to reliably restore custom metadata. Kometa's [metadata backup operation](../config/operations.md#mass-metadata-update) saves values such as ratings, titles, and summaries to YAML. The [metadata extractor script](https://github.com/chazlarson/Media-Scripts/blob/main/Kometa/README.md#metadata-extractorpy) by Chazlarson backs up additional metadata, including artwork.

Without a backup, the following limits apply:

#### Posters and backgrounds

Artwork set from a URL or local file replaces the previous artwork without recording its history. Kometa cannot restore the previous image from that change alone.

#### Mass updates

Genres, ratings, and similar fields can generally be reset to Plex's defaults where available. Previous custom values are lost. For example, replacing your user ratings with TMDb ratings does not preserve your original ratings.

#### Other metadata

Changes to titles, summaries, years, artwork, and other fields made through a metadata file do not retain the previous values for restoration.

## Migration and older configurations

These notes describe historical changes. Follow them only when migrating an older working configuration, then check the current reference for supported settings.

### Plex meta manager → Kometa

??? info "Historical PMM migration instructions"

    You're using Plex-Meta-Manager now and need to switch to Kometa? Here's what you have to do:

    ???+ danger "Important"

        These instructions are assuming that your existing config file is working with a recent [say 1.19 or newer] pre-rebrand Plex-Meta-Manager release.

    #### If you are using Git:

    1. cd into the directory where you installed Plex-Meta-Manager
    2. retrieve the new code and reinstall requirements [see below for commands]. This is the same thing you'd do with any upgrade.
    3. change `plex_meta_manager.py` in any run command you use to `kometa.py`. For example: `python kometa.py --run`.
    4. You're done.

    Before updating, preserve any changes reported by `git status`; do not discard them. The commands for step 2 are:

    ```
        git status
        git pull
        # activate your venv here if you use one and it is not already active
        python -m pip install -r requirements.txt
    ```

    #### If you are using Docker:

    1. change the image you are using from `meisnate12/plex-meta-manager:SOME_TAG` to `kometateam/kometa`, 
    You'll change this wherever it's specified in your situation, a `docker run` command, a docker compose file, some field in a NAS UI, wherever.
    2. If needed, rebuild the container however that happens in your context. `docker compose up -d`, clicking a button, whatever.
    3. You're done.

    #### If you downloaded it as a zip file:

    1. uncompress the zip file
    2. cd into that directory and do the same setup you did initially (create a virtual environment, maybe, then install requirements. 
    There's no way for us to know what you did when you set it up, so we can't give more specific instructions than that)
    3. copy the config directory from your Plex-Meta-Manager dir into this directory.
    4. change `plex_meta_manager.py` in any run command you use to `kometa.py`. For example: `python kometa.py --run`.
    5. You're done.

    #### Other things you can do if you wish:

    Neither of these two things are required.

    1. change `- pmm:` in the `config.yml` file to `- default:`; the docs now use `- default:`, but either will work for the foreseeable future, 
    so you do not **need** to do this. You may *want* to, and if so go ahead, but you do not *have* to.
    2. change the name of any directories you are using to "kometa". The app does not care about that part of the path. It only cares about the contents of the config directory, but it can be 
    located anywhere. You do not **have* to change `/some/path/to/Plex-Meta-Manager` to `/some/path/to/Kometa`. Again, you may *want* to, and if so go ahead, but you do not *have* to.

    For example, this:

    ```yaml
    libraries:
      Movies:
        remove_overlays: false
        collection_files:
          - pmm: basic
          - pmm: imdb
    ```

    Could, but does not have to, become:

    ```yaml
    libraries:
      Movies:
        remove_overlays: false
        collection_files:
          - default: basic
          - default: imdb
    ```

### Removed services and builders

In September 2026, Trakt blocked API access for third-party services including MDBList and SIMKL with no prior notice.

Trakt's new draft API Use Policy also prohibits using Trakt as an upstream data provider for another service and continuously synchronizing Trakt account data into a separate tracking or list platform. The restrictions were introduced with little or no advance notice to affected services. [Trakt API discussion](https://github.com/trakt/trakt-api/issues/933) · [Proposed API Use Policy](https://github.com/trakt/trakt-api/pull/941)

In light of the above, and following a pattern of changes by Trakt (which you can read about [here](https://www.reddit.com/r/Simkl/comments/1wjv7i1/the_end_of_trakt_as_we_know_it_trakt_has/)), Kometa has decided to remove Trakt support in version 2.4.9. This includes the Trakt connection, builders, collection and playlist synchronization, artwork, ratings, operations, overlays, defaults, and related configuration attributes.

Kometa logs the following error when it finds Trakt configuration and continues with the rest of the run:

> Trakt is no longer supported, please see the Announcements channel in the Kometa Discord server for further information

We suggest users remove Trakt from configuration files and instead use supported alternatives such as TMDb, IMDb, MDBList, SIMKL, FlickList, and other available builders where appropriate.

### Legacy file and overlay settings

These notes apply to configurations using older file, overlay, or builder settings.

??? info "`metadata_path` and `overlay_path` are now legacy attributes<a class="headerlink" href="#metadata-overlay-path" title="Permanent link">¶</a>"

    <div id="metadata-overlay-path" />

    The attributes `metadata_path` and `overlay_path` are now legacy, and will likely produce an error `metadata attribute is required` when running Kometa.

    We have new attributes: `collection_files`, `overlay_files` and `metadata_files` which you can read more about on the 
    [Libraries Attributes page](../config/libraries.md#attributes)

    Whilst this error can be ignored, we strongly advise you to move over to the new attributes, which can be done following this guidance:

    :fontawesome-solid-1: If your YAML file creates collections or is a Kometa Defaults Collection File then it belongs under `collection_files`. 
    
    :fontawesome-solid-2: If your YAML file creates overlays or is a Kometa Defaults Overlay File then it belongs under `overlay_files`
    
    :fontawesome-solid-3: If your YAML file edits item metadata ([see this example](../files/metadata.md#movies)) then it belongs under `metadata_files`
    
    If your file creates collections AND edits item metadata, then it should go in both `collection_files` and `metadata_files`
    
    If you are unsure on the above, the majority of `metadata_path` files  will now fall under `collection_files`, and all `overlay_path` files will now fall under `overlay_files`.

    If you require any assistance with this, please visit our Discord Server where we can assist you.

    Below is an example of the new attributes in use:

    ```yaml
    libraries:
      Movies:
        collection_files: #(1)!
          - file: config/Movies.yml #(2)!
          - default: imdb #(2)!
        metadata_files: #(3)!
          - file: config/MetadataEdits.yml #(4)!
        overlay_files: #(5)!
          - file: config/Overlays.yml #(6)!
          - default: audio_codec #(6)!
    ```

    1. This attribute used to be `metadata_path` and defines files that will relate to Collections
    2. These files are placed within `collection_files` because they define how Collections are built/maintained.
    3. This attribute used to be `metadata_path` and defines files that will relate to Metadata Edits
    4. These files are placed within `metadata_files` because they define Metadata Edits rather than collections.
    5. This attribute used to be `overlay_path` and defines files that will relate to Overlays
    6. These files are placed within `overlay_files` because they define how Overlays are built/maintained.

??? info "`remove_` `reset_` `reapply_` and `schedule_` attributes for `overlays` are now Library Attributes<a class="headerlink" href="#overlay-library-attributes" title="Permanent link">¶</a>"

    <div id="overlay-library-attributes" />

    The attributes `remove_overlays`, `reset_overlays`, `reapply_overlays` and `schedule_overlays` are now Library Attributes
    and are called at the library level rather than within `overlay_path`.

    This change has been made to make these attributes consistent with other attributes of a similar nature.

    Whilst the previous method still works, we strongly advise you to move over to the new attributes, which can be done by looking at the following sample YAML:

    ```yaml
    libraries:
      Movies:
        remove_overlays: false
        reapply_overlays: false #(1)!
        # reset_overlays: plex #(2)!
        schedule_overlays: daily
        overlay_files:
          - default: audio_codec
    ```

    1. We strongly advise never setting this to `true` as it can cause [Image Bloat](scripts/imagemaid.md)
    2. This is purely an example, you do not need to specify `reset_overlays` or any of these attributes unless you specifically need to use them.

??? info "`imdb_list` no longer works for Title or Keyword search URLs<a class="headerlink" href="#imdb-search" title="Permanent link">¶</a>"

    <div id="imdb-search" />

    As a result of IMDb changing their back-end code, `imdb_list` can no longer be used for URLs which start with 
    `https://www.imdb.com/search/title/` or `https://www.imdb.com/search/keyword/`

    All URLs used with `imdb_list` **must** start with `https://www.imdb.com/list/`

    We have introduced the [IMDb Search Builder](../files/builders/imdb/search.md) which replaces the functionality that
    `search/title/` and `search/keyword/` used to provide.

    As an example, the `imdb_search` Builder for `https://www.imdb.com/search/keyword/?keywords=christmas-movie` would be:

    ```yaml
    collections:
      Christmas Movies:
        imdb_search:
          keyword: christmas movie
    ```

    And the `imdb_search` Builder for `https://www.imdb.com/search/title/?title_type=feature,tv_movie,tv_special,video&num_votes=100,&keywords=spy,espionage` would be:

    ```yaml
    collections:
      Spy Movies:
        imdb_search:
          type: movie, tv_movie, tv_special, video
          votes.gte: 100
          keyword.any: spy, espionage
    ```

??? info "FlixPatrol Default Files and Builders have been removed<a class="headerlink" href="#flixpatrol" title="Permanent link">¶</a>"

    <div id="flixpatrol" />

    Due to FlixPatrol moving a lot of their data behind a paywall and them reworking their pages to remove IMDb IDs and 
    TMDb IDs the flixpatrol builders and default files have been removed. There currently are no plans to re-add them.

??? info "Kometa Default `other_award` replaced with individual Award files<a class="headerlink" href="#awards" title="Permanent link">¶</a>"

    <div id="awards" />

    The Kometa Default file `other_award` is now deprecated and will no longer function.

    Individual Kometa Default files have been introduced for several Awards, see the [Awards List](../defaults/award/separator.md)
    for more information on the new options.

<span id="providing-log-files-on-discord"></span>

## Get further help

Ask in the [Kometa Discord server](https://kometa.wiki/en/latest/discord/) and attach the **complete `meta.log` file** by dragging it into your message. Use a third-party upload service only if the file exceeds Discord's upload limit.

Include:

- Your Kometa version and installation method.
- What you expected to happen and what happened instead.
- The relevant configuration, if requested.

!!! warning "Share the file rather than copied excerpts"

    Copied log text can lose formatting and omit context needed to diagnose the problem. Review the file for private information before sharing it.

For other support and project links, see [Community & credits](acknowledgements.md).
