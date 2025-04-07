---
hide:
  - toc
---
# Run Commands & Environment Variables

## What does it mean to "run" Kometa?

The word "run" in the Kometa context can be used in two ways; you "run" the Kometa Python script itself, using a Python or docker command, 
and then that script behaves in one of two ways:

1. It sits and waits until a particular time, wakes up and processes the config file, then goes back to sleep until that same time the next day. 
   Kometa does this unless you [specifically tell it to do otherwise](#run).
2. It processes the config file right away and then exits.

"Processes the config file" means that it will go through all the collections, metadata, overlays, playlists, 
and libraries that you have defined in your config file and do what you have told it to do with them.

That's kind of a mouthful, though, so we typically use "run" to describe that bit of the process.

In these docs, and in the discord when providing support, we'll use "run" to describe the "process the config file" bit.

The basic command to execute Kometa is as follows:

=== "Windows / Mac / Linux"

    ``` py
    python kometa.py
    ```

=== "Docker"

    ``` py
    docker run --rm -it -v "/<ROOT_KOMETA_DIRECTORY_HERE>/config:/config:rw" kometateam/kometa
    ```

As discussed above, that will start Kometa, which will then wait until 5AM to wake up and process the config file.

The basic command to execute Kometa, telling it to run right this second, is as follows:

=== "Windows / Mac / Linux"

    ``` py
    python kometa.py --run
    ```

=== "Docker"

    ``` py
    docker run --rm -it -v "/<ROOT_KOMETA_DIRECTORY_HERE>/config:/config:rw" kometateam/kometa --run
    ```

## Modifying Kometa's default (or configured) runtime behavior.

If you want to modify the way Kometa behaves when it runs, you can use the commands on this page. None of these are *required* to run Kometa.
They are all optional and can be used to customize the way Kometa runs to suit your needs.

Many of these override settings in the config file, so you can use them to change the way Kometa behaves without having to edit the config file.

You can set any of these flags as either environment variables or as command line arguments.

On all platforms, "environment variables" are a way to set variables that are available to all programs running on the system.
You can set these variables in your shell, in a script, or in a Docker container.

You might think of this as a note on your desk that tells you Sue likes a skim latte when you go to the coffee shop. 
You can use that note to remember what Sue likes when she asks "please get me a coffee".

Runtime flags are command line arguments that you can pass to Kometa when you run it to change the way it behaves. 

You might think of this as a directive Bob adds when he asks "please get me a coffee, a **flat white**". 
At "runtime", Bob is adding a "flag" to his request to indicate the type of coffee.

All these settings have defaults, which you can think of as the "standard coffee" that you get if someone doesn't specify anything. 
If Chris doesn't specify a type of coffee, and you have no note about Chris, Chris gets the **default**, a **plain black coffee**.

If you don't specify a runtime flag or environment variable, you get the standard/default behavior.

## Runtime Flags vs Environment Variables; who wins?

The ridiculous example above notwithstanding, in Kometa, environment variables take precedence over runtime flags.

For example, and it's not important what this does, but if you were to use the following script:

```shell
export KOMETA_CONFIG=/path/to/environment/config.yml      # this sets an environment variable
python kometa.py --config /path/to/runtime-var/config.yml # runtime flag for the same setting
```

Kometa would use the config file at `/path/to/environment/config.yml` because the environment variable takes precedence over the runtime flag.

Please note that these instructions assume that you have a basic understanding of command line and Docker concepts.
If you need to familiarize yourself with Docker, you can check out the official tutorial.

## I want to set a lot of these things, what's the best way?

One way to specify environmental variables is by adding them to a .env file located in your config folder.

That file would contain something like:

```env
KOMETA_CONFIG=/path/to/your-config-file.yml
KOMETA_TIMES=06:00,18:00
KOMETA_TRACE=true
KOMETA_LOG_REQUESTS=true
KOMETA_TIMEOUT=360
KOMETA_NO_VERIFY_SSL=true
KOMETA_COLLECTIONS_ONLY=true
```

Kometa will load those environment variables when it starts up, and you don't have to remember to set them every time you run Kometa.

???+ warning "Combining Commands or Variables"

    Some Commands or Variables can be combined in a single run, this is mainly beneficial when you want to run a specific
    command and have it run immediately rather than waiting until the next scheduled run.

    For example, if I want to run [Collections Only](#collections-only) to only run Collection Files, and [Run Immediately](#run) 
    to skip waiting until my next scheduled run, I can use both commands at the same time:

    !!! example
        === "Local Environment"
            ```
            python kometa.py --collections-only --run
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --collections-only --run
            ```

## All Available Runtime Flags/Environment Variables

??? blank "Config Location&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-c`/`--config`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_CONFIG`<a class="headerlink" href="#config" title="Permanent link">¶</a>"

    <div id="config" />Kometa looks for its config file at `config/config.yml`. If you want to change that, perhaps to use a special-purpose `config.yml` or the like,
    you can use this flag to specify the location of the configuration YAML file.

    <hr style="margin: 0px;">

    **Accepted Values:** Path to YAML config file

    **Shell Flags:** `-c` or `--config` (ex. `--config /some/path/to/your-config-file.yml`)

    **Environment Variable:** `KOMETA_CONFIG` (ex. `KOMETA_CONFIG=/some/path/to/your-config-file.yml`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --config /some/path/to/your-config-file.yml
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" -v "Z:\some\path:/data:rw" kometateam/kometa --config /data/your-config-file.yml
            ```

??? blank "Time to Run&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-t`/`--times`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_TIMES`<a class="headerlink" href="#times" title="Permanent link">¶</a>"

    <div id="times" />Kometa wakes up at 5:00 AM to process the config file. If you want to change that time, or tell Kometa to wake up at multiple times, use this flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Comma-separated list in `HH:MM` format

    **Shell Flags:** `-t` or `--times` (ex. `--times 06:00,18:00`)

    **Environment Variable:** `KOMETA_TIMES` (ex. `KOMETA_TIMES=06:00,18:00`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --times 22:00,03:00
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --times 22:00,03:00
            ```

??? blank "Run Immediately&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-r`/`--run`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_RUN`<a class="headerlink" href="#run" title="Permanent link">¶</a>"

    <div id="run" />If you want Kometa to run immediately rather than waiting until 5AM, set this flag to `true`.

    <hr style="margin: 0px;">

    **Shell Flags:** `-r` or `--run` (ex. `--run`)

    **Environment Variable:** `KOMETA_RUN` (ex. `KOMETA_RUN=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --run
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --run
            ```

??? blank "Run Tests&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ts`/`--tests`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_TESTS`<a class="headerlink" href="#tests" title="Permanent link">¶</a>"

    <div id="tests" />If you set this flag to `true`, Kometa will run only collections that you have marked as `test` immediately, as [KOMETA_RUN](#run).
    
    **NOTE: This will only run collections with `test: true` in the definition.**

    <hr style="margin: 0px;">

    **Shell Flags:** `-ts` or `--tests` (ex. `--tests`)

    **Environment Variable:** `KOMETA_TESTS` (ex. `KOMETA_TESTS=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --tests
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
                trakt_list: https://trakt.tv/users/jawann2002/lists/marvel-cinematic-universe-movies?sort=rank,asc
                smart_label: release.desc
            ```

??? blank "Debug&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-db`/`--debug`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_DEBUG`<a class="headerlink" href="#debug" title="Permanent link">¶</a>"

    <div id="debug" />To increase the verbosity of the logs, set this flag to `true`.

    <hr style="margin: 0px;">

    **Shell Flags:** `-db` or `--debug` (ex. `--debug`)

    **Environment Variable:** `KOMETA_DEBUG` (ex. `KOMETA_DEBUG=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --debug
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --debug
            ```

??? blank "Trace&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-tr`/`--trace`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_TRACE`<a class="headerlink" href="#trace" title="Permanent link">¶</a>"

    <div id="trace" />To increase the verbosity of the logs even more than [debug](#debug), set this flag to `true`.

    <hr style="margin: 0px;">

    **Shell Flags:** `-tr` or `--trace` (ex. `--trace`)

    **Environment Variable:** `KOMETA_TRACE` (ex. `KOMETA_TRACE=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --trace
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --trace
            ```

??? blank "Log Requests&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-lr`/`--log-requests`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_LOG_REQUESTS`<a class="headerlink" href="#log-requests" title="Permanent link">¶</a>"

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
            python kometa.py --log-requests
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --log-requests
            ```

??? blank "Timeout&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ti`/`--timeout`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_TIMEOUT`<a class="headerlink" href="#timeout" title="Permanent link">¶</a>"

    <div id="timeout" />Change the timeout in seconds for all non-Plex services (such as TMDb, Radarr, and Trakt). 
    This will default to `180` when not specified and is overwritten by any timeouts mentioned for specific services in the Configuration File.

    <hr style="margin: 0px;">

    **Accepted Values:** Integer (value is in seconds)

    **Shell Flags:** `-ti` or `--timeout` (ex. `--timeout 360`)

    **Environment Variable:** `KOMETA_TIMEOUT` (ex. `KOMETA_TIMEOUT=360`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --timeout 360
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --timeout 360
            ```

??? blank "No Verify SSL&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-nv`/`--no-verify-ssl`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_NO_VERIFY_SSL`<a class="headerlink" href="#no-verify-ssl" title="Permanent link">¶</a>"

    <div id="no-verify-ssl" />Turn SSL Verification off.
    
    ???+ note
    
        set to false if your log file shows any errors similar to "SSL: CERTIFICATE_VERIFY_FAILED"

    <hr style="margin: 0px;">

    **Shell Flags:** `-nv` or `--no-verify-ssl` (ex. `--no-verify-ssl`)

    **Environment Variable:** `KOMETA_NO_VERIFY_SSL` (ex. `KOMETA_NO_VERIFY_SSL=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --no-verify-ssl
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --no-verify-ssl
            ```

??? blank "Collections Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-co`/`--collections-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_COLLECTIONS_ONLY`<a class="headerlink" href="#collections-only" title="Permanent link">¶</a>"

    <div id="collections-only" />Only run collection YAML files, skip library operations, metadata, overlays, and playlists.

    <hr style="margin: 0px;">

    **Shell Flags:** `-co` or `--collections-only` (ex. `--collections-only`)

    **Environment Variable:** `KOMETA_COLLECTIONS_ONLY` (ex. `KOMETA_COLLECTIONS_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --collections-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --collections-only
            ```

??? blank "Metadata Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-mo`/`--metadata-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_METADATA_ONLY`<a class="headerlink" href="#metadata-only" title="Permanent link">¶</a>"

    <div id="metadata-only" />Only run metadata files, skip library operations, collections, overlays, and playlists.

    <hr style="margin: 0px;">

    **Shell Flags:** `-mo` or `--metadata-only` (ex. `--metadata-only`)

    **Environment Variable:** `KOMETA_METADATA_ONLY` (ex. `KOMETA_METADATA_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --metadata-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --metadata-only
            ```

??? blank "Playlists Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-po`/`--playlists-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_PLAYLISTS_ONLY`<a class="headerlink" href="#playlists-only" title="Permanent link">¶</a>"

    <div id="playlists-only" />Only run playlist YAML files, skip library operations, overlays, collections, and metadata.

    <hr style="margin: 0px;">

    **Shell Flags:** `-po` or `--playlists-only` (ex. `--playlists-only`)

    **Environment Variable:** `KOMETA_PLAYLISTS_ONLY` (ex. `KOMETA_PLAYLISTS_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --playlists-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --playlists-only
            ```

??? blank "Operations Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-op`/`--operations-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_OPERATIONS_ONLY`<a class="headerlink" href="#operations-only" title="Permanent link">¶</a>"

    <div id="operations-only" />Only run library operations skipping collections, metadata, playlists, and overlays.

    <hr style="margin: 0px;">

    **Shell Flags:** `-op` or `--operations-only` (ex. `--operations-only`)

    **Environment Variable:** `KOMETA_OPERATIONS_ONLY` (ex. `KOMETA_OPERATIONS_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --operations-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --operations-only
            ```

??? blank "Overlays Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ov`/`--overlays-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_OVERLAYS_ONLY`<a class="headerlink" href="#overlays-only" title="Permanent link">¶</a>"

    <div id="overlays-only" />Only run library overlay files skipping collections, metadata, playlists, and operations.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-ov` or `--overlays-only` (ex. `--overlays-only`)

    **Environment Variable:** `KOMETA_OVERLAYS_ONLY` (ex. `KOMETA_OVERLAYS_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --overlays-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --overlays-only
            ```

??? blank "Run Collections&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-rc`/`--run-collections`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_RUN_COLLECTIONS`<a class="headerlink" href="#run-collections" title="Permanent link">¶</a>"

    <div id="run-collections" />Perform an [immediate run](#run) to run only the named collections, bypassing the time to run flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list of Collection Names to run; the "pipe" character is "|" as shown in the examples below.

    **Shell Flags:** `-rc` or `--run-collections` (ex. `--run-collections "Harry Potter|Star Wars"`)

    **Environment Variable:** `KOMETA_RUN_COLLECTIONS` (ex. `KOMETA_RUN_COLLECTIONS=Harry Potter|Star Wars`)

    !!! example
        === "Local Environment"
            ```
            python kometa.py --run-collections "Harry Potter|Star Wars"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --run-collections "Harry Potter|Star Wars"
            ```

??? blank "Run Libraries&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-rl`/`--run-libraries`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_RUN_LIBRARIES`<a class="headerlink" href="#run-libraries" title="Permanent link">¶</a>"

    <div id="run-libraries" />Perform an [immediate run](#run) to run only the named libraries, bypassing the time to run flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list of Library Names to run; the "pipe" character is "|" as shown in the examples below.

    **Shell Flags:** `-rl` or `--run-libraries` (ex. `--run-libraries "Movies - 4K|TV Shows - 4K"`)

    **Environment Variable:** `KOMETA_RUN_LIBRARIES` (ex. `KOMETA_RUN_LIBRARIES=Movies - 4K|TV Shows - 4K`)

    !!! example
        === "Local Environment"
            ```
            python kometa.py --run-libraries "Movies - 4K|TV Shows - 4K"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --run-libraries "Movies - 4K|TV Shows - 4K"
            ```

??? blank "Run Files&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-rf`/`--run-files`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_RUN_FILES`<a class="headerlink" href="#run-files" title="Permanent link">¶</a>"

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
            python kometa.py --run-files "Movies.yml|MovieCharts"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --run-files "Movies.yml|MovieCharts"
            ```

??? blank "Ignore Schedules&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-is`/`--ignore-schedules`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_IGNORE_SCHEDULES`<a class="headerlink" href="#ignore-schedules" title="Permanent link">¶</a>"

    <div id="ignore-schedules" />Ignore all schedules for the run. Range Scheduled collections (such as Christmas movies) will still be ignored.

    <hr style="margin: 0px;">

    **Shell Flags:** `-is` or `--ignore-schedules` (ex. `--ignore-schedules`)

    **Environment Variable:** `KOMETA_IGNORE_SCHEDULES` (ex. `KOMETA_IGNORE_SCHEDULES=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --ignore-schedules
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --ignore-schedules
            ```

??? blank "Ignore Ghost&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ig`/`--ignore-ghost`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_IGNORE_GHOST`<a class="headerlink" href="#ignore-ghost" title="Permanent link">¶</a>"

    <div id="ignore-ghost" />Kometa prints some things to the log that don't actually go into the log file on disk.
    Typically these are things like status messages while loading and/or filtering. If you want to hide all ghost logging for the run, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-ig` or `--ignore-ghost` (ex. `--ignore-ghost`)

    **Environment Variable:** `KOMETA_IGNORE_GHOST` (ex. `KOMETA_IGNORE_GHOST=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --ignore-ghost
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --ignore-ghost
            ```

??? blank "Delete Collections&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-dc`/`--delete-collections`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_DELETE_COLLECTIONS`<a class="headerlink" href="#delete-collections" title="Permanent link">¶</a>"

    <div id="delete-collections" />Delete all collections in each library as the first step in the run.

    ???+ warning
         
        You will lose **all** collections in the library - this will delete all collections, including ones not created or maintained by Kometa.

    <hr style="margin: 0px;">

    **Shell Flags:** `-dc` or `--delete-collections` (ex. `--delete-collections`)

    **Environment Variable:** `KOMETA_DELETE_COLLECTIONS` (ex. `KOMETA_DELETE_COLLECTIONS=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --delete-collections
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --delete-collections
            ```

??? blank "Delete Labels&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-dl`/`--delete-labels`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_DELETE_LABELS`<a class="headerlink" href="#delete-labels" title="Permanent link">¶</a>"

    <div id="delete-labels" />Delete all labels [save one, see below] on every item in a Library prior to running collections/operations.

    ???+ warning
    
        To preserve functionality of Kometa, this will **not** remove the Overlay label, which is required for Kometa to know which items have Overlays applied.
    
        This will impact any [Smart Label Collections](../files/builders/plex.md#smart-label-builder) that you have in your library.
    
        We do not recommend using this on a regular basis if you also use any operations or collections that update labels,
        as you are effectively deleting and adding labels on each run.

    <hr style="margin: 0px;">

    **Shell Flags:** `-dl` or `--delete-labels` (ex. `--delete-labels`)

    **Environment Variable:** `KOMETA_DELETE_LABELS` (ex. `KOMETA_DELETE_LABELS=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --delete-labels
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --delete-labels
            ```

??? blank "Resume Run&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-re`/`--resume`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_RESUME`<a class="headerlink" href="#resume" title="Permanent link">¶</a>"

    <div id="resume" />Perform an [immediate run](#run) starting from the first instance of the specified collection, bypassing the time to run flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-re` or `--resume` (ex. `--resume "Star Wars"`)

    **Environment Variable:** `KOMETA_RESUME` (ex. `KOMETA_RESUME=Star Wars`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --resume "Star Wars"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --resume "Star Wars"
            ```

??? blank "No Countdown&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-nc`/`--no-countdown`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_NO_COUNTDOWN`<a class="headerlink" href="#no-countdown" title="Permanent link">¶</a>"

    <div id="no-countdown" />Typically, when **not** doing an [immediate run](#run), Kometa displays a countdown in the terminal where it's running. 
    If you want to hide this countdown, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-nc` or `--no-countdown` (ex. `--no-countdown`)

    **Environment Variable:** `KOMETA_NO_COUNTDOWN` (ex. `KOMETA_NO_COUNTDOWN=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --no-countdown
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --no-countdown
            ```

??? blank "No Missing&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-nm`/`--no-missing`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_NO_MISSING`<a class="headerlink" href="#no-missing" title="Permanent link">¶</a>"

    <div id="no-missing" />Kometa can take various actions on missing items, such as sending them to Radarr, listing them in the log, or saving a report. 
    If you want to disable all of these actions, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-nm` or `--no-missing` (ex. `--no-missing`)

    **Environment Variable:** `KOMETA_NO_MISSING` (ex. `KOMETA_NO_MISSING=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --no-missing
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --no-missing
            ```

??? blank "No Report&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-nr`/`--no-report`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_NO_REPORT`<a class="headerlink" href="#no-report" title="Permanent link">¶</a>"

    <div id="no-report" />Kometa can produce a report of missing items, collections, and other information. 
    If you have this report enabled but want to disable it for a specific run, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-nr` or `--no-report` (ex. `--no-report`)

    **Environment Variable:** `KOMETA_NO_REPORT` (ex. `KOMETA_NO_REPORT=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --no-report
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --no-report
            ```

??? blank "Read Only Config&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ro`/`--read-only-config`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_READ_ONLY_CONFIG`<a class="headerlink" href="#read-only-config" title="Permanent link">¶</a>"

    <div id="read-only-config" />Kometa reads in and then writes out a properly formatted version of your `config.yml` on each run;this makes the formatting consistent and ensures 
    that you have visibility into new settings that get added. If you want to disable this behavior and tell Kometa to leave your `config.yml` as-is, use this flag.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-ro` or `--read-only-config` (ex. `--read-only-config`)

    **Environment Variable:** `KOMETA_READ_ONLY_CONFIG` (ex. `KOMETA_READ_ONLY_CONFIG=true`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --read-only-config
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --read-only-config
            ```

??? blank "Divider Character&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-d`/`--divider`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_DIVIDER`<a class="headerlink" href="#divider" title="Permanent link">¶</a>"

    <div id="divider" />The log is split into sections with lines of `=`. If you wish to change that character to a different one, you can do that with this flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Any character

    **Shell Flags:** `-d` or `--divider` (ex. `--divider *`)

    **Environment Variable:** `KOMETA_DIVIDER` (ex. `KOMETA_DIVIDER=*`)
    
    !!! example
        === "Local Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --divider *
            python kometa.py --divider *
            ```
        === "Docker Environment"
            ```
            ```

??? blank "Screen Width&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-w`/`--width`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_WIDTH`<a class="headerlink" href="#width" title="Permanent link">¶</a>"

    <div id="width" />The log is formatted to fit within a certain width. If you wish to change that width, you can do that with this flag. 
    Not that long lines are not wrapped or truncated to this width; this controls the minimum width of the log.

    <hr style="margin: 0px;">

    **Accepted Values:** Integer between 90 and 300

    **Shell Flags:** `-w` or `--width` (ex. `--width 150`)

    **Environment Variable:** `KOMETA_WIDTH` (ex. `KOMETA_WIDTH=150`)
    
    !!! example
        === "Local Environment"
            ```
            python kometa.py --width 150
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --width 150
            ```

??? blank "Priority&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-lp`/`--low-priority`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_LOW_PRIORITY`<a class="headerlink" href="#priority" title="Permanent link">¶</a>"

    <div id="priority" />Run the Kometa process at a lower priority. Will default to normal priority if not specified.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-lp` or `--low-priority` (ex. `--low-priority`)

    **Environment Variable:** `KOMETA_LOW_PRIORITY` (ex. `KOMETA_LOW_PRIORITY=true`)

    !!! example
        === "Local Environment"
            ```
            python kometa.py --low-priority
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Kometa\config:/config:rw" kometateam/kometa --low-priority
            ```

??? blank "Config Secrets&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--kometa-***`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`KOMETA_***`<a class="headerlink" href="#kometa-vars" title="Permanent link">¶</a>"

    <div id="kometa-vars" />All Run Commands that are in the format `--kometa-***` and Environment Variables that are in the 
    format `KOMETA_***`, where `***` is the name you want to call the variable, will be loaded in as Config Secrets.
    
    These Config Secrets can be loaded into the config by placing `<<***>>` in any field in the config, where `***` is whatever name you called the variable.

    <hr style="margin: 0px;">

    **Shell Flags:** `--kometa-***` (ex. `--kometa-mysecret 123456789`)

    **Environment Variable:** `KOMETA_***` (ex. `KOMETA_MYSECRET=123456789`)

    !!! example
        === "Local Environment"
            ```
            python kometa.py --kometa-mysecret 123456789
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
