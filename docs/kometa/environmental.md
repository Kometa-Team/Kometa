---
hide:
  - toc
---
# Run Commands & Environment Variables

## What does it mean to run Kometa?

Starting Kometa and running your configuration are separate steps. By default, Kometa waits until 5:00 AM, processes your configuration, then waits until the same time the next day. Add [`--run`](#run) to process your configuration immediately and exit when finished.

Processing your configuration means carrying out the collection, metadata, overlay, playlist, and library tasks you have configured. In this documentation and on Discord, a "run" refers to this processing step.

Start Kometa with its default schedule:

=== "Windows / Mac / Linux"

    ```shell
    uv run python kometa.py
    ```

=== "Docker"

    ```shell
    docker run --rm -it -v "/<ROOT_KOMETA_DIRECTORY_HERE>/config:/config:rw" kometateam/kometa
    ```

To run immediately and exit:

=== "Windows / Mac / Linux"

    ```shell
    uv run python kometa.py --run
    ```

=== "Docker"

    ```shell
    docker run --rm -it -v "/<ROOT_KOMETA_DIRECTORY_HERE>/config:/config:rw" kometateam/kometa --run
    ```

## Customize runtime behavior

The options below are optional. Use them to change how Kometa runs, including overriding supported settings without editing your configuration file. If you do not set an option, Kometa uses its default behavior or the applicable configuration setting.

Each option lists its command-line flags and environment variable:

- **Command-line flags** are added to the command that starts Kometa, such as `--run`.
- **Environment variables** are values Kometa reads when it starts. Set them in your shell, a script, your Docker container, or a `.env` file.

Local examples use `uv run` from your Kometa checkout, following the [local installation guide](install/index.md#path-local). These examples assume familiarity with command-line tools and, for container installations, Docker.

## Which value takes precedence?

**Environment variables take precedence over command-line flags.** For example:

```shell
export KOMETA_CONFIG=/path/to/environment/config.yml
uv run python kometa.py --config /path/to/runtime-var/config.yml
```

Kometa uses `/path/to/environment/config.yml` because `KOMETA_CONFIG` overrides `--config`.

## Save options in a .env file

To reuse several environment variables across runs, add them to a `.env` file in your config folder:

```env
KOMETA_CONFIG=/path/to/your-config-file.yml
KOMETA_TIMES=06:00|18:00
KOMETA_TRACE=true
KOMETA_LOG_REQUESTS=true
KOMETA_TIMEOUT=360
KOMETA_NO_VERIFY_SSL=true
KOMETA_COLLECTIONS_ONLY=true
```

Choose the variables you need from the reference below. Kometa loads the file at startup, so you do not need to set those variables manually for every run.

???+ warning "Combining Commands or Variables"

    Some Commands or Variables can be combined in a single run, this is mainly beneficial when you want to run a specific
    command and have it run immediately rather than waiting until the next scheduled run.

    For example, if I want to run [Collections Only](#collections-only) to only run Collection Files, and [Run Immediately](#run)
    to skip waiting until my next scheduled run, I can use both commands at the same time:

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --collections-only --run
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --collections-only --run
            ```

## All available runtime flags/environment variables

### Configuration and scheduling

??? info "Config Location &middot; `-c`/`--config` &middot; `KOMETA_CONFIG`<a class='operation-admonition-link' data-copy-permalink='true' href='#config' title='Copy link'>¶</a>"

    <div id="config" />Kometa looks for its config file at `config/config.yml`. If you want to change that, perhaps to use a special-purpose `config.yml` or the like,
    you can use this flag to specify the location of the configuration YAML file.

    <hr style="margin: 0px;">

    **Accepted Values:** Path to YAML config file

    **Shell Flags:** `-c` or `--config` (ex. `--config /some/path/to/your-config-file.yml`)

    **Environment Variable:** `KOMETA_CONFIG` (ex. `KOMETA_CONFIG=/some/path/to/your-config-file.yml`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --config /some/path/to/your-config-file.yml
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -v "Z:\some\path:/data:rw" kometateam/kometa --config /data/your-config-file.yml
            ```

??? info "Time to Run &middot; `-t`/`--times` &middot; `KOMETA_TIMES`<a class='operation-admonition-link' data-copy-permalink='true' href='#times' title='Copy link'>¶</a>"

    <div id="times" />Kometa wakes up at 5:00 AM to process the config file. If you want to change that time, or tell Kometa to wake up at multiple times, use this flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list in `HH:MM` format

    **Shell Flags:** `-t` or `--times` (ex. `--times "06:00|18:00"`)

    **Environment Variable:** `KOMETA_TIMES` (ex. `KOMETA_TIMES=06:00|18:00`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --times '22:00|03:00'
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --times "22:00|03:00"
            ```

??? info "Run Immediately &middot; `-r`/`--run` &middot; `KOMETA_RUN`<a class='operation-admonition-link' data-copy-permalink='true' href='#run' title='Copy link'>¶</a>"

    <div id="run" />If you want Kometa to run immediately rather than waiting until 5AM, set this flag to `true`.

    <hr style="margin: 0px;">

    **Shell Flags:** `-r` or `--run` (ex. `--run`)

    **Environment Variable:** `KOMETA_RUN` (ex. `KOMETA_RUN=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --run
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --run
            ```

??? info "Resume Run &middot; `-re`/`--resume` &middot; `KOMETA_RESUME`<a class='operation-admonition-link' data-copy-permalink='true' href='#resume' title='Copy link'>¶</a>"

    <div id="resume" />Perform an [immediate run](#run) starting from the first instance of the specified collection, bypassing the time to run flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-re` or `--resume` (ex. `--resume "Star Wars"`)

    **Environment Variable:** `KOMETA_RESUME` (ex. `KOMETA_RESUME=Star Wars`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --resume "Star Wars"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --resume "Star Wars"
            ```

??? info "Ignore Schedules &middot; `-is`/`--ignore-schedules` &middot; `KOMETA_IGNORE_SCHEDULES`<a class='operation-admonition-link' data-copy-permalink='true' href='#ignore-schedules' title='Copy link'>¶</a>"

    <div id="ignore-schedules" />Ignore all schedules for the run. Range Scheduled collections (such as Christmas movies) will still be ignored.

    <hr style="margin: 0px;">

    **Shell Flags:** `-is` or `--ignore-schedules` (ex. `--ignore-schedules`)

    **Environment Variable:** `KOMETA_IGNORE_SCHEDULES` (ex. `KOMETA_IGNORE_SCHEDULES=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --ignore-schedules
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --ignore-schedules
            ```

??? info "Read Only Config &middot; `-ro`/`--read-only-config` &middot; `KOMETA_READ_ONLY_CONFIG`<a class='operation-admonition-link' data-copy-permalink='true' href='#read-only-config' title='Copy link'>¶</a>"

    <div id="read-only-config" />Kometa reads in and then writes out a properly formatted version of your `config.yml` on each run;this makes the formatting consistent and ensures
    that you have visibility into new settings that get added. If you want to disable this behavior and tell Kometa to leave your `config.yml` as-is, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-ro` or `--read-only-config` (ex. `--read-only-config`)

    **Environment Variable:** `KOMETA_READ_ONLY_CONFIG` (ex. `KOMETA_READ_ONLY_CONFIG=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --read-only-config
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --read-only-config
            ```

??? info "Config Secrets &middot; `--kometa-***` &middot; `KOMETA_***`<a class='operation-admonition-link' data-copy-permalink='true' href='#kometa-vars' title='Copy link'>¶</a>"

    <div id="kometa-vars" />All Run Commands that are in the format `--kometa-***` and Environment Variables that are in the
    format `KOMETA_***`, where `***` is the name you want to call the variable, will be loaded in as Config Secrets.

    These Config Secrets can be loaded into the config by placing `<<***>>` in any field in the config, where `***` is whatever name you called the variable.

    <hr style="margin: 0px;">

    **Shell Flags:** `--kometa-***` (ex. `--kometa-mysecret 123456789`)

    **Environment Variable:** `KOMETA_***` (ex. `KOMETA_MYSECRET=123456789`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --kometa-mysecret 123456789
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --kometa-mysecret 123456789
            ```

        **Example Config Usage:**

        ```yaml
        tmdb:
          apikey: <<mysecret>>
        ```

        **IMPORTANT: DO NOT use underscores in the secret name. `<<mysecret>>` works, `<<my_secret>>` will not.**

### Choose what runs

??? info "Collections Only &middot; `-co`/`--collections-only` &middot; `KOMETA_COLLECTIONS_ONLY`<a class='operation-admonition-link' data-copy-permalink='true' href='#collections-only' title='Copy link'>¶</a>"

    <div id="collections-only" />Only run collection YAML files, skip library operations, metadata, overlays, and playlists.

    <hr style="margin: 0px;">

    **Shell Flags:** `-co` or `--collections-only` (ex. `--collections-only`)

    **Environment Variable:** `KOMETA_COLLECTIONS_ONLY` (ex. `KOMETA_COLLECTIONS_ONLY=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --collections-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --collections-only
            ```
    **IMPORTANT:** only **one** of these `--SOMETHING-only` flags can be active at one time.  If you enable more than one, like perhaps one as an env var and one as a runtime flag, Kometa will exit early with an error.

??? info "Metadata Only &middot; `-mo`/`--metadata-only` &middot; `KOMETA_METADATA_ONLY`<a class='operation-admonition-link' data-copy-permalink='true' href='#metadata-only' title='Copy link'>¶</a>"

    <div id="metadata-only" />Only run metadata files, skip library operations, collections, overlays, and playlists.

    <hr style="margin: 0px;">

    **Shell Flags:** `-mo` or `--metadata-only` (ex. `--metadata-only`)

    **Environment Variable:** `KOMETA_METADATA_ONLY` (ex. `KOMETA_METADATA_ONLY=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --metadata-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --metadata-only
            ```
    **IMPORTANT:** only **one** of these `--SOMETHING-only` flags can be active at one time.  If you enable more than one, like perhaps one as an env var and one as a runtime flag, Kometa will exit early with an error.

??? info "Playlists Only &middot; `-po`/`--playlists-only` &middot; `KOMETA_PLAYLISTS_ONLY`<a class='operation-admonition-link' data-copy-permalink='true' href='#playlists-only' title='Copy link'>¶</a>"

    <div id="playlists-only" />Only run playlist YAML files, skip library operations, overlays, collections, and metadata.

    <hr style="margin: 0px;">

    **Shell Flags:** `-po` or `--playlists-only` (ex. `--playlists-only`)

    **Environment Variable:** `KOMETA_PLAYLISTS_ONLY` (ex. `KOMETA_PLAYLISTS_ONLY=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --playlists-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --playlists-only
            ```
    **IMPORTANT:** only **one** of these `--SOMETHING-only` flags can be active at one time.  If you enable more than one, like perhaps one as an env var and one as a runtime flag, Kometa will exit early with an error.

??? info "Operations Only &middot; `-op`/`--operations-only` &middot; `KOMETA_OPERATIONS_ONLY`<a class='operation-admonition-link' data-copy-permalink='true' href='#operations-only' title='Copy link'>¶</a>"

    <div id="operations-only" />Only run library operations skipping collections, metadata, playlists, and overlays.

    <hr style="margin: 0px;">

    **Shell Flags:** `-op` or `--operations-only` (ex. `--operations-only`)

    **Environment Variable:** `KOMETA_OPERATIONS_ONLY` (ex. `KOMETA_OPERATIONS_ONLY=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --operations-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --operations-only
            ```
    **IMPORTANT:** only **one** of these `--SOMETHING-only` flags can be active at one time.  If you enable more than one, like perhaps one as an env var and one as a runtime flag, Kometa will exit early with an error.

??? info "Overlays Only &middot; `-ov`/`--overlays-only` &middot; `KOMETA_OVERLAYS_ONLY`<a class='operation-admonition-link' data-copy-permalink='true' href='#overlays-only' title='Copy link'>¶</a>"

    <div id="overlays-only" />Only run library overlay files skipping collections, metadata, playlists, and operations.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-ov` or `--overlays-only` (ex. `--overlays-only`)

    **Environment Variable:** `KOMETA_OVERLAYS_ONLY` (ex. `KOMETA_OVERLAYS_ONLY=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --overlays-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --overlays-only
            ```
    **IMPORTANT:** only **one** of these `--SOMETHING-only` flags can be active at one time.  If you enable more than one, like perhaps one as an env var and one as a runtime flag, Kometa will exit early with an error.

??? info "Run Collections &middot; `-rc`/`--run-collections` &middot; `KOMETA_RUN_COLLECTIONS`<a class='operation-admonition-link' data-copy-permalink='true' href='#run-collections' title='Copy link'>¶</a>"

    <div id="run-collections" />Perform an [immediate run](#run) to run only the named collections, bypassing the time to run flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list of Collection Names to run; the "pipe" character is "|" as shown in the examples below.

    **Shell Flags:** `-rc` or `--run-collections` (ex. `--run-collections "Harry Potter|Star Wars"`)

    **Environment Variable:** `KOMETA_RUN_COLLECTIONS` (ex. `KOMETA_RUN_COLLECTIONS=Harry Potter|Star Wars`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --run-collections "Harry Potter|Star Wars"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --run-collections "Harry Potter|Star Wars"
            ```

??? info "Run Libraries &middot; `-rl`/`--run-libraries` &middot; `KOMETA_RUN_LIBRARIES`<a class='operation-admonition-link' data-copy-permalink='true' href='#run-libraries' title='Copy link'>¶</a>"

    <div id="run-libraries" />Perform an [immediate run](#run) to run only the named libraries, bypassing the time to run flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list of Library Names to run; the "pipe" character is "|" as shown in the examples below.

    **Shell Flags:** `-rl` or `--run-libraries` (ex. `--run-libraries "Movies - 4K|TV Shows - 4K"`)

    **Environment Variable:** `KOMETA_RUN_LIBRARIES` (ex. `KOMETA_RUN_LIBRARIES=Movies - 4K|TV Shows - 4K`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --run-libraries "Movies - 4K|TV Shows - 4K"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --run-libraries "Movies - 4K|TV Shows - 4K"
            ```

??? info "Run Files &middot; `-rf`/`--run-files` &middot; `KOMETA_RUN_FILES`<a class='operation-admonition-link' data-copy-permalink='true' href='#run-files' title='Copy link'>¶</a>"

    <div id="run-files" />Perform an [immediate run](#run) to run only the named Collection, Metadata or Playlist files,
    bypassing the time to run flag. This works for all different paths i.e. `default`, `git`, `url`, `file`, or `repo`.

    ???+ warning

         Do not use this to run Overlay files, as Overlay files must run all together or not at all due to their nature.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list of Collection, Metadata or Playlist Filenames to run; the "pipe" character is "|" as shown in the examples below.

    **Shell Flags:** `-rf` or `--run-files` (ex. `--run-files "Movies.yml|MovieCharts"`)

    **Environment Variable:** `KOMETA_RUN_FILES` (ex. `KOMETA_RUN_FILES=Movies.yml|MovieCharts`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --run-files "Movies.yml|MovieCharts"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --run-files "Movies.yml|MovieCharts"
            ```

??? info "Run Mode &middot; `--mode` &middot; `KOMETA_MODE`<a class='operation-admonition-link' data-copy-permalink='true' href='#mode' title='Copy link'>¶</a>"

    <div id="mode" />Set the [library schedule mode](../config/schedule.md#library-schedule-modes) for every library in this run. This overrides configured library schedule modes, including libraries without a matching schedule. Other schedule rules still apply. 

    ???+ tip "Best practices and examples"

        See the [Scheduling Kometa and Library Runs guide](guides/scheduling.md#try-a-mode-with-a-runtime-flag) for the best practices and some examples of how to use `--mode` effectively against your server.

    <hr style="margin: 0px;">

    **Shell Flag:** `--mode` (ex. `--run --mode 'items(imdb:tt1232829|tmdb:187017)'`)

    **Environment Variable:** `KOMETA_MODE` (ex. `KOMETA_MODE=added(7)`)

    | Mode | What it does | Example command |
    |:--|:--|:--|
    | `full` | Processes every top-level item in each library. | `uv run python kometa.py --run --mode full` |
    | `items(ids)` | Processes only the listed items. Separate IDs with a pipe character. Movies match TMDb IDs, shows match TVDb IDs, and TMDb show IDs are converted to TVDb IDs. IMDb IDs and top-level Plex rating keys work for either. | `uv run python kometa.py --run --mode 'items(imdb:tt0133093)'` |
    | `added(duration)` | Processes items added to Plex within the last duration. Use a positive integer with `m` (minutes), `h` (hours), or `d` (24-hour days); a bare integer means days. For shows, it also includes shows with recently added episodes. | `uv run python kometa.py --run --mode 'added(30m)'` |
    | `diff` | Processes items missing from Kometa's previous library cache snapshot. For shows, it compares each season's Plex update time. Requires a persistent Kometa cache. | `uv run python kometa.py --run --mode diff` |
    | `index(A-Z)` | Processes titles whose first letter is in the inclusive A through Z range. Uses the Plex Sort Title when available. | `uv run python kometa.py --run --mode 'index(A-F)'` |
    | `index(A-Z#)` | Processes the A through Z range plus titles beginning with a number or symbol. | `uv run python kometa.py --run --mode 'index(A-F#)'` |

    Replace the IDs with those of items in your library. To select multiple items, use a pipe between IDs, for example `uv run python kometa.py --run --mode 'items(imdb:tt0133093|tmdb:550|tvdb:350396|plex:42)'`. Keep the single quotes around modes containing parentheses when using PowerShell. See [Library Schedule Modes](../config/schedule.md#library-schedule-modes) for identifier and matching details.

??? info "Ignore Ghost &middot; `-ig`/`--ignore-ghost` &middot; `KOMETA_IGNORE_GHOST`<a class='operation-admonition-link' data-copy-permalink='true' href='#ignore-ghost' title='Copy link'>¶</a>"

    <div id="ignore-ghost" />Kometa prints some things to the log that don't actually go into the log file on disk.
    Typically these are things like status messages while loading and/or filtering. If you want to hide all ghost logging for the run, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-ig` or `--ignore-ghost` (ex. `--ignore-ghost`)

    **Environment Variable:** `KOMETA_IGNORE_GHOST` (ex. `KOMETA_IGNORE_GHOST=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --ignore-ghost
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --ignore-ghost
            ```

??? info "Run Tests &middot; `-ts`/`--tests` &middot; `KOMETA_TESTS`<a class='operation-admonition-link' data-copy-permalink='true' href='#tests' title='Copy link'>¶</a>"

    <div id="tests" />If you set this flag to `true`, Kometa will run only collections that you have marked as `test` immediately, as [KOMETA_RUN](#run).

    **NOTE: This will only run collections with `test: true` in the definition.**

    <hr style="margin: 0px;">

    **Shell Flags:** `-ts` or `--tests` (ex. `--tests`)

    **Environment Variable:** `KOMETA_TESTS` (ex. `KOMETA_TESTS=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --tests
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --tests
            ```
        === "Example Collection File"

            In my collection YAML file, I would set `true: false` like this:

            ```yaml
            collections:
              Marvel Cinematic Universe:
                test: true                  # HERE
                mdblist_list: mdblist_list: https://mdblist.com/lists/stealthgyro/marvel-cinematic-universe-mcu
                smart_label: release.desc
            ```

### Diagnostics and logging

??? info "Debug &middot; `-db`/`--debug` &middot; `KOMETA_DEBUG`<a class='operation-admonition-link' data-copy-permalink='true' href='#debug' title='Copy link'>¶</a>"

    <div id="debug" />To show debug messages in the command window or Docker console output, set this flag to `true`. Detailed log files such as `meta.log` include debug messages regardless of this setting so they retain the diagnostic information needed for troubleshooting.

    <hr style="margin: 0px;">

    **Shell Flags:** `-db` or `--debug` (ex. `--debug`)

    **Environment Variable:** `KOMETA_DEBUG` (ex. `KOMETA_DEBUG=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --debug
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --debug
            ```

??? info "Trace &middot; `-tr`/`--trace` &middot; `KOMETA_TRACE`<a class='operation-admonition-link' data-copy-permalink='true' href='#trace' title='Copy link'>¶</a>"

    <div id="trace" />To increase the verbosity of the logs even more than [debug](#debug), set this flag to `true`.

    Trace logs include a message before each Plex request with its method, item path, and configured timeout, followed by completion or failure and elapsed time. If a run appears stuck, a `Plex request starting` line without a matching completion or failure identifies the pending query. Query parameters, headers, and request bodies are omitted. The timeout applies to connection and read operations; it is not a total request deadline.

    <hr style="margin: 0px;">

    **Shell Flags:** `-tr` or `--trace` (ex. `--trace`)

    **Environment Variable:** `KOMETA_TRACE` (ex. `KOMETA_TRACE=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --trace
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --trace
            ```

??? info "Log Requests &middot; `-lr`/`--log-requests` &middot; `KOMETA_LOG_REQUESTS`<a class='operation-admonition-link' data-copy-permalink='true' href='#log-requests' title='Copy link'>¶</a>"

    <div id="log-requests" />If you enable this, every external network request made by Kometa will be logged, along with the data that is returned.
    This will add a lot of data to the logs, and will probably contain things like tokens, since the auto-redaction of such things is not generalized
    enough to catch any token that may be in any URL.

    **This can potentially have personal information in it.**

    <hr style="margin: 0px;">

    **Shell Flags:** `-lr` or `--log-requests` (ex. `--log-requests`)

    **Environment Variable:** `KOMETA_LOG_REQUESTS` (ex. `KOMETA_LOG_REQUESTS=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --log-requests
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --log-requests
            ```

??? info "Timing Instrumentation &middot; `--timings`/`--timing` &middot; `KOMETA_TIMINGS`<a class='operation-admonition-link' data-copy-permalink='true' href='#timings' title='Copy link'>¶</a>"

    <div id="timings" />Run with lightweight timing instrumentation enabled. Kometa times network calls, cache lookups, and major per-collection/per-library phases, then prints a summary to the log at the end of the run and exports a full per-source/per-library breakdown as JSON and CSV files to the logs directory.

    Disabled by default, with negligible overhead when off.

    <hr style="margin: 0px;">

    **Shell Flags:** `--timings` or `--timing` (ex. `--timings`)

    **Environment Variable:** `KOMETA_TIMINGS` or `KOMETA_TIMING` (ex. `KOMETA_TIMINGS=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --run --timings
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -e KOMETA_TIMINGS=true kometateam/kometa --run
            ```

??? info "Source Integrity &middot; `--source-integrity`/`--no-source-integrity` &middot; `KOMETA_SOURCE_INTEGRITY`<a class='operation-admonition-link' data-copy-permalink='true' href='#source-integrity' title='Copy link'>¶</a>"

    <div id="source-integrity" />Check distributed Kometa files against official source for the exact installed commit. Enabled by default; checking waits up to 30 seconds during startup and never prevents Kometa from running. Results appear with the startup system information, with no integrity messages during library processing. The end-of-run summary repeats the startup result. See [Source integrity](help.md#source-integrity) for states, caching, and exclusions.

    <hr style="margin: 0px;">

    **Shell Flags:** `--source-integrity` enables checking; `--no-source-integrity` disables it.

    **Environment Variable:** `KOMETA_SOURCE_INTEGRITY` (ex. `KOMETA_SOURCE_INTEGRITY=false`). Environment variables take precedence over CLI flags.

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --run --no-source-integrity
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -e KOMETA_SOURCE_INTEGRITY=false kometateam/kometa --run
            ```

??? info "Deep Profiling &middot; `KOMETA_PROFILE`<a class='operation-admonition-link' data-copy-permalink='true' href='#deep-profiling' title='Copy link'>¶</a>"

    <div id="deep-profiling" />Run a single Kometa run under [`pyinstrument`](https://github.com/joerick/pyinstrument), writing an HTML profile report to the logs directory. Intended for maintainers diagnosing a specific slow run in more depth than Timing Instrumentation's summary provides.

    <hr style="margin: 0px;">

    **Environment Variable:** `KOMETA_PROFILE` set to `pyinstrument` (ex. `KOMETA_PROFILE=pyinstrument`)

    !!! example
        === "Local Environment"
            ```
            KOMETA_PROFILE=pyinstrument uv run python kometa.py --run
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -e KOMETA_PROFILE=pyinstrument kometateam/kometa --run
            ```

??? info "No Countdown &middot; `-nc`/`--no-countdown` &middot; `KOMETA_NO_COUNTDOWN`<a class='operation-admonition-link' data-copy-permalink='true' href='#no-countdown' title='Copy link'>¶</a>"

    <div id="no-countdown" />Typically, when **not** doing an [immediate run](#run), Kometa displays a countdown in the terminal where it's running.
    If you want to hide this countdown, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-nc` or `--no-countdown` (ex. `--no-countdown`)

    **Environment Variable:** `KOMETA_NO_COUNTDOWN` (ex. `KOMETA_NO_COUNTDOWN=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --no-countdown
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --no-countdown
            ```

??? info "Divider Character &middot; `-d`/`--divider` &middot; `KOMETA_DIVIDER`<a class='operation-admonition-link' data-copy-permalink='true' href='#divider' title='Copy link'>¶</a>"

    <div id="divider" />The log is split into sections with lines of `=`. If you wish to change that character to a different one, you can do that with this flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Any character

    **Shell Flags:** `-d` or `--divider` (ex. `--divider *`)

    **Environment Variable:** `KOMETA_DIVIDER` (ex. `KOMETA_DIVIDER=*`)

    !!! example
        === "Local Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --divider *
            uv run python kometa.py --divider *
            ```
        === "Docker Environment"
            ```
            ```

??? info "Screen Width &middot; `-w`/`--width` &middot; `KOMETA_WIDTH`<a class='operation-admonition-link' data-copy-permalink='true' href='#width' title='Copy link'>¶</a>"

    <div id="width" />The log is formatted to fit within a certain width. If you wish to change that width, you can do that with this flag.
    Not that long lines are not wrapped or truncated to this width; this controls the minimum width of the log.

    <hr style="margin: 0px;">

    **Accepted Values:** Integer between 90 and 300

    **Shell Flags:** `-w` or `--width` (ex. `--width 150`)

    **Environment Variable:** `KOMETA_WIDTH` (ex. `KOMETA_WIDTH=150`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --width 150
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --width 150
            ```

### Connections and process settings

??? info "Timeout &middot; `-ti`/`--timeout` &middot; `KOMETA_TIMEOUT`<a class='operation-admonition-link' data-copy-permalink='true' href='#timeout' title='Copy link'>¶</a>"

    <div id="timeout" />Change the timeout in seconds for all non-Plex services (such as TMDb and Radarr).
    This will default to `180` when not specified and is overwritten by any timeouts mentioned for specific services in the Configuration File.

    <hr style="margin: 0px;">

    **Accepted Values:** Integer (value is in seconds)

    **Shell Flags:** `-ti` or `--timeout` (ex. `--timeout 360`)

    **Environment Variable:** `KOMETA_TIMEOUT` (ex. `KOMETA_TIMEOUT=360`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --timeout 360
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --timeout 360
            ```

??? info "No Verify SSL &middot; `-nv`/`--no-verify-ssl` &middot; `KOMETA_NO_VERIFY_SSL`<a class='operation-admonition-link' data-copy-permalink='true' href='#no-verify-ssl' title='Copy link'>¶</a>"

    <div id="no-verify-ssl" />Turn SSL Verification off.

    ???+ note

        set to false if your log file shows any errors similar to "SSL: CERTIFICATE_VERIFY_FAILED"

        IMPORTANT: This will disable TLS checks for all outbound services (TMDb, MAL, etc.). Only flip this switch if you are comfortable with this.

    <hr style="margin: 0px;">

    **Shell Flags:** `-nv` or `--no-verify-ssl` (ex. `--no-verify-ssl`)

    **Environment Variable:** `KOMETA_NO_VERIFY_SSL` (ex. `KOMETA_NO_VERIFY_SSL=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --no-verify-ssl
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --no-verify-ssl
            ```

??? info "Priority &middot; `-lp`/`--low-priority` &middot; `KOMETA_LOW_PRIORITY`<a class='operation-admonition-link' data-copy-permalink='true' href='#priority' title='Copy link'>¶</a>"

    <div id="priority" />Run the Kometa process at a lower priority. Will default to normal priority if not specified.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-lp` or `--low-priority` (ex. `--low-priority`)

    **Environment Variable:** `KOMETA_LOW_PRIORITY` (ex. `KOMETA_LOW_PRIORITY=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --low-priority
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --low-priority
            ```

### Missing items and reports

??? info "No Missing &middot; `-nm`/`--no-missing` &middot; `KOMETA_NO_MISSING`<a class='operation-admonition-link' data-copy-permalink='true' href='#no-missing' title='Copy link'>¶</a>"

    <div id="no-missing" />Kometa can take various actions on missing items, such as sending them to Radarr, listing them in the log, or saving a report.
    If you want to disable all of these actions, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-nm` or `--no-missing` (ex. `--no-missing`)

    **Environment Variable:** `KOMETA_NO_MISSING` (ex. `KOMETA_NO_MISSING=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --no-missing
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --no-missing
            ```

??? info "No Report &middot; `-nr`/`--no-report` &middot; `KOMETA_NO_REPORT`<a class='operation-admonition-link' data-copy-permalink='true' href='#no-report' title='Copy link'>¶</a>"

    <div id="no-report" />Kometa can produce a report of missing items, collections, and other information.
    If you have this report enabled but want to disable it for a specific run, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-nr` or `--no-report` (ex. `--no-report`)

    **Environment Variable:** `KOMETA_NO_REPORT` (ex. `KOMETA_NO_REPORT=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --no-report
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --no-report
            ```

### Cleanup

??? info "Delete Collections &middot; `-dc`/`--delete-collections` &middot; `KOMETA_DELETE_COLLECTIONS`<a class='operation-admonition-link' data-copy-permalink='true' href='#delete-collections' title='Copy link'>¶</a>"

    <div id="delete-collections" />Delete all collections in each library as the first step in the run.

    ???+ warning

        You will lose **all** collections in the library - this will delete all collections, including ones not created or maintained by Kometa.

    <hr style="margin: 0px;">

    **Shell Flags:** `-dc` or `--delete-collections` (ex. `--delete-collections`)

    **Environment Variable:** `KOMETA_DELETE_COLLECTIONS` (ex. `KOMETA_DELETE_COLLECTIONS=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --delete-collections
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --delete-collections
            ```

??? info "Delete Labels &middot; `-dl`/`--delete-labels` &middot; `KOMETA_DELETE_LABELS`<a class='operation-admonition-link' data-copy-permalink='true' href='#delete-labels' title='Copy link'>¶</a>"

    <div id="delete-labels" />Delete all labels [save one, see below] on every item in a Library prior to running collections/operations.

    ???+ warning

        To preserve functionality of Kometa, this will **not** remove the Overlay label, which is required for Kometa to know which items have Overlays applied.

        This will impact any [Smart Label Collections](../files/settings.md#smart-label-definitions) that you have in your library.
        We do not recommend using this on a regular basis if you also use any operations or collections that update labels,
        as you are effectively deleting and adding labels on each run.

    <hr style="margin: 0px;">

    **Shell Flags:** `-dl` or `--delete-labels` (ex. `--delete-labels`)

    **Environment Variable:** `KOMETA_DELETE_LABELS` (ex. `KOMETA_DELETE_LABELS=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --delete-labels
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --delete-labels
            ```

??? info "Delete Collections + Labels &middot; `--delete-collections-labels` &middot; `KOMETA_DELETE_COLLECTIONS_LABELS`<a class='operation-admonition-link' data-copy-permalink='true' href='#delete-collections-labels' title='Copy link'>¶</a>"

    <div id="delete-collections-labels" />Delete all collections in each library as the first step in the run, same as [Delete Collections](#delete-collections) above. For any deleted collection whose title matches an existing Plex label of the same name - the default for [Smart Label Collections](../files/settings.md#smart-label-definitions) - also batch-removes that one label from just the items that currently have it, instead of the full library-wide label wipe [Delete Labels](#delete-labels) does.

    ???+ note

        This only detects Smart Label collections using the default label name (the collection's own title). A collection using a custom `smart_label` name won't be matched, since that name isn't known until the config is parsed - use [Delete Labels](#delete-labels) for those.

        This flag has no short form - `-dc` and `-dl` are single-dash because they're exactly 2 characters (Kometa's own convention for short flags); anything longer would collide with an existing single-character flag (e.g. `-d`/`--divider`) when typed with a single dash. Use `--delete-collections-labels` or `--delete-collection-label` in full.

    <hr style="margin: 0px;">

    **Shell Flags:** `--delete-collections-labels` or `--delete-collection-label` (ex. `--delete-collections-labels`)

    **Environment Variable:** `KOMETA_DELETE_COLLECTIONS_LABELS` (ex. `KOMETA_DELETE_COLLECTIONS_LABELS=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --delete-collections-labels
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --delete-collections-labels
            ```

### Validation

??? info "Validate Config &middot; `-va`/`--validate-config` &middot; `KOMETA_VALIDATE`<a class='operation-admonition-link' data-copy-permalink='true' href='#validate' title='Copy link'>¶</a>"

    <div id="validate" />Parse and validate `config.yml` and all YAML files linked from it, print a structured report, then exit — without performing a normal run.

    Exits with code `0` if validation passes, `1` if there are any errors. Warnings do not affect the exit code.

    Use [`--validate-level`](#validate-level) to control how deep the validation goes. Combine with [`--validate-schema`](#validate-schema) to also check files against their JSON schemas.

    <hr style="margin: 0px;">

    **Shell Flags:** `-va`, `--validate-config`, or `--validate` (ex. `--validate`)

    **Environment Variable:** `KOMETA_VALIDATE` (ex. `KOMETA_VALIDATE=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --validate
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --validate
            ```

??? info "Validate Level &middot; `-vl`/`--validate-level` &middot; `KOMETA_VALIDATE_LEVEL`<a class='operation-admonition-link' data-copy-permalink='true' href='#validate-level' title='Copy link'>¶</a>"

    <div id="validate-level" />Controls how deep the validation goes when [`--validate`](#validate) is set. Default is `structure`.

    | Level | What it checks |
    |-------|----------------|
    | `syntax` | Parses `config.yml` and all linked local YAML files; reports any YAML syntax errors. Remote references (`url:`, `git:`, `default:`, `repo:`) are skipped. |
    | `structure` | Everything in `syntax`, plus: checks for required keys (`libraries`, `tmdb`), warns on deprecated keys (`metadata_path`, `overlay_path`), and errors on local `file:` paths that don't exist on disk. |
    | `full` | Calls the full Kometa config initialisation (connects to Plex and all configured APIs) without actually running any collections, overlays, or operations. |

    <hr style="margin: 0px;">

    **Accepted Values:** `syntax`, `structure`, or `full`

    **Shell Flags:** `-vl` or `--validate-level` (ex. `--validate-level syntax`)

    **Environment Variable:** `KOMETA_VALIDATE_LEVEL` (ex. `KOMETA_VALIDATE_LEVEL=syntax`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --validate --validate-level syntax
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --validate --validate-level syntax
            ```

??? info "Validate Schema &middot; `-vs`/`--validate-schemas` &middot; `KOMETA_VALIDATE_SCHEMA`<a class='operation-admonition-link' data-copy-permalink='true' href='#validate-schema' title='Copy link'>¶</a>"

    <div id="validate-schema" />When set alongside [`--validate`](#validate), each YAML file is also checked against its corresponding JSON schema in the `json-schema/` directory.

    Schema violations are split into two categories:

    - **Errors** — type mismatches, failed `required` checks, and other constraint violations. These cause exit code `1`.
    - **Schema gaps** — keys found in your files that are not defined in the schema (`additionalProperties` violations). These are reported separately as a gap report and do **not** affect the exit code. They are useful for identifying where the JSON schemas need to be extended.

    <hr style="margin: 0px;">

    **Shell Flags:** `-vs`, `--validate-schemas`, or `--validate-schema` (ex. `--validate-schema`)

    **Environment Variable:** `KOMETA_VALIDATE_SCHEMA` (ex. `KOMETA_VALIDATE_SCHEMA=true`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --validate --validate-schema
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --validate --validate-schema
            ```

??? info "Schema Path &middot; `-sp`/`--schema-path` &middot; `KOMETA_SCHEMA_PATH`<a class='operation-admonition-link' data-copy-permalink='true' href='#schema-path' title='Copy link'>¶</a>"

    <div id="schema-path" />Override the path to the `json-schema/` directory used by [`--validate-schema`](#validate-schema). Defaults to the `json-schema/` folder next to `kometa.py`.

    <hr style="margin: 0px;">

    **Accepted Values:** Path to a directory containing JSON schema files

    **Shell Flags:** `-sp` or `--schema-path` (ex. `--schema-path /some/path/to/json-schema`)

    **Environment Variable:** `KOMETA_SCHEMA_PATH` (ex. `KOMETA_SCHEMA_PATH=/some/path/to/json-schema`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --validate --validate-schema --schema-path /some/path/to/json-schema
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --validate --validate-schema --schema-path /some/path/to/json-schema
            ```

??? info "Validate File &middot; `-vf`/`--validate-files` &middot; `KOMETA_VALIDATE_FILE`<a class='operation-admonition-link' data-copy-permalink='true' href='#validate-file' title='Copy link'>¶</a>"

    <div id="validate-file" />Validate a single YAML file against its auto-detected JSON schema and print a gap report. The schema is inferred from the file's root keys: `collections:` → collection schema, `overlays:` → overlay schema, `playlists:` → playlist schema, `metadata:` → metadata schema, `libraries:`/`plex:`/`tmdb:` → config schema.

    Exits with code `0` if no errors, `1` if any errors. Use [`--schema-path`](#schema-path) to override the schema directory.

    <hr style="margin: 0px;">

    **Accepted Values:** Path to a YAML file

    **Shell Flags:** `-vf`, `--validate-files`, or `--validate-file` (ex. `--validate-file /path/to/collections.yml`)

    **Environment Variable:** `KOMETA_VALIDATE_FILE` (ex. `KOMETA_VALIDATE_FILE=/path/to/collections.yml`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --validate-file /path/to/collections.yml
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -v "/path/to/files:/files:ro" kometateam/kometa --validate-file /files/collections.yml
            ```

??? info "Validate Directory &middot; `-vd`/`--validate-directory` &middot; `KOMETA_VALIDATE_DIR`<a class='operation-admonition-link' data-copy-permalink='true' href='#validate-dir' title='Copy link'>¶</a>"

    <div id="validate-dir" />Walk a directory recursively, validate every `.yml` and `.yaml` file found against its auto-detected JSON schema, and print a combined report. Files with an unrecognised structure are skipped with a warning (not an error). Clean files are silent; only files with errors are reported individually.

    After all files, a single aggregate gap report is printed showing keys present in your files but missing from the schemas, ranked by how many files contain each key. This is the primary tool for improving the `json-schema/` files.

    Exits with code `0` if no file had errors, `1` if any file had errors. Use [`--schema-path`](#schema-path) to override the schema directory.

    <hr style="margin: 0px;">

    **Accepted Values:** Path to a directory

    **Shell Flags:** `-vd`, `--validate-directory`, or `--validate-dir` (ex. `--validate-dir /path/to/configs`)

    **Environment Variable:** `KOMETA_VALIDATE_DIR` (ex. `KOMETA_VALIDATE_DIR=/path/to/configs`)

    !!! example
        === "Local Environment"
            ```
            uv run python kometa.py --validate-dir /path/to/community-configs
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -v "/path/to/configs:/data:ro" kometateam/kometa --validate-dir /data
            ```
