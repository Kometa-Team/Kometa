
# Run Commands & Environment Variables

The basic command to run Plex Meta Manager is as follows:

=== "Windows / Mac / Linux"

    ``` py
    python plex_meta_manager.py
    ```

=== "Docker"

    ``` py
    docker run --rm -it -v "/<ROOT_PMM_DIRECTORY_HERE>/config:/config:rw" meisnate12/plex-meta-manager
    ```

To customize the running of Plex Meta Manager according to your needs, you can use either run commands or environmental 
variables. Environmental variables take precedence over run command attributes. However, if you encounter a race 
condition where an attribute has been set both via an environmental variable and a shell command, the environmental 
variable will be given priority.

Please note that these instructions assume that you have a basic understanding of Docker concepts. If you need to 
familiarize yourself with Docker, you can check out the official tutorial.

Another way to specify environmental variables is by adding them to a .env file located in your config folder.

Environment variables are expressed as `KEY=VALUE` depending on the context where you are specifying them, you may enter 
those two things in two different fields, or some other way.  The examples below show how you would specify the 
environment variable in a script or a `docker run` command.  Things like Portainer or a NAS Docker UI will have 
different ways to specify these things.

???+ warning "Combining Commands or Variables"

![img.png](img.png)    Some Commands or Variables can be combined in a single run, this is mainly beneficial when you want to run a specific command and have it run immediately rather than waiting until the next scheduled run.

    For example, if I want to run [Collections Only](#collections-only) to only run Collection Files, and [Run Immediately](#run) to skip waiting until my next scheduled run, I can use both commands at the same time:

    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --collections-only --run
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --collections-only --run
            ```

??? blank "Config Location&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-c`/`--config`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_CONFIG`<a class="headerlink" href="#config" title="Permanent link">¶</a>"

    <div id="config" />Specify the location of the configuration YAML file. Will default to `config/config.yml` when not 
    specified.

    <hr style="margin: 0px;">

    **Accepted Values:** Path to YAML config file

    **Shell Flags:** `-c` or `--config` (ex. `--config /data/config.yml`)

    **Environment Variable:** `PMM_CONFIG` (ex. `PMM_CONFIG=/data/config.yml`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --config /data/config.yml
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --config /data/config.yml
            ```

??? blank "Time to Run&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-t`/`--times`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_TIMES`<a class="headerlink" href="#times" title="Permanent link">¶</a>"

    <div id="times" />Specify the time of day that Plex Meta Manager will run. Will default to `05:00` when not 
    specified.

    <hr style="margin: 0px;">

    **Accepted Values:** Comma-separated list in `HH:MM` format

    **Shell Flags:** `-t` or `--times` (ex. `--times 06:00,18:00`)

    **Environment Variable:** `PMM_TIMES` (ex. `PMM_TIMES=06:00,18:00`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --times 22:00,03:00
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --times 22:00,03:00
            ```

??? blank "Run Immediately&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-r`/`--run`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_RUN`<a class="headerlink" href="#run" title="Permanent link">¶</a>"

    <div id="run" />Perform a run immediately, bypassing the time to run flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-r` or `--run` (ex. `--run`)

    **Environment Variable:** `PMM_RUN` (ex. `PMM_RUN=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --run
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run
            ```

??? blank "Run Tests&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ts`/`--tests`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_TESTS`<a class="headerlink" href="#tests" title="Permanent link">¶</a>"

    <div id="tests" />Perform a debug test run immediately, bypassing the time to run flag. **This will only run 
    collections with `test: true` in the definition.**

    <hr style="margin: 0px;">

    **Shell Flags:** `-ts` or `--tests` (ex. `--tests`)

    **Environment Variable:** `PMM_TESTS` (ex. `PMM_TESTS=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --tests
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --tests
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

??? blank "Debug&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-db`/`--debug`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_DEBUG`<a class="headerlink" href="#debug" title="Permanent link">¶</a>"

    <div id="debug" />Perform a debug test run immediately, bypassing the time to run flag. **This will only run 
    collections with `test: true` in the definition.**

    <hr style="margin: 0px;">

    **Shell Flags:** `-db` or `--debug` (ex. `--debug`)

    **Environment Variable:** `PMM_DEBUG` (ex. `PMM_DEBUG=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --debug
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --debug
            ```

??? blank "Trace&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-tr`/`--trace`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_TRACE`<a class="headerlink" href="#trace" title="Permanent link">¶</a>"

    <div id="trace" />Run with extra Trace Debug Logs.

    <hr style="margin: 0px;">

    **Shell Flags:** `-tr` or `--trace` (ex. `--trace`)

    **Environment Variable:** `PMM_TRACE` (ex. `PMM_TRACE=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --trace
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --trace
            ```

??? blank "Log Requests&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-lr`/`--log-requests`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_LOG_REQUESTS`<a class="headerlink" href="#log-requests" title="Permanent link">¶</a>"

    <div id="log-requests" />Run with every network request printed to the Logs. **This can potentially have personal 
    information in it.**

    <hr style="margin: 0px;">

    **Shell Flags:** `-lr` or `--log-requests` (ex. `--log-requests`)

    **Environment Variable:** `PMM_LOG_REQUESTS` (ex. `PMM_LOG_REQUESTS=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --log-requests
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --log-requests
            ```

??? blank "Timeout&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ti`/`--timeout`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_TIMEOUT`<a class="headerlink" href="#timeout" title="Permanent link">¶</a>"

    <div id="timeout" />Change the timeout for all non-Plex services (such as TMDb, Radarr, and Trakt). This will default to `180` when not specified and is overwritten by any timeouts mentioned for specific services in the Configuration File.

    <hr style="margin: 0px;">

    **Accepted Values:** Integer Number of Seconds

    **Shell Flags:** `-ti` or `--timeout` (ex. `--timeout 06:00,18:00`)

    **Environment Variable:** `PMM_TIMEOUT` (ex. `PMM_TIMEOUT=06:00,18:00`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --timeout 360
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --timeout 360
            ```

??? blank "Collections Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-co`/`--collections-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_COLLECTIONS_ONLY`<a class="headerlink" href="#collections-only" title="Permanent link">¶</a>"

    <div id="collections-only" />Only run collection YAML files, skip library operations, metadata, overlays, and playlists.

    <hr style="margin: 0px;">

    **Shell Flags:** `-co` or `--collections-only` (ex. `--collections-only`)

    **Environment Variable:** `PMM_COLLECTIONS_ONLY` (ex. `PMM_COLLECTIONS_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --collections-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --collections-only
            ```

??? blank "Metadata Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-mo`/`--metadata-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_METADATA_ONLY`<a class="headerlink" href="#metadata-only" title="Permanent link">¶</a>"

    <div id="metadata-only" />Only run metadata files, skip library operations, collections, overlays, and playlists.

    <hr style="margin: 0px;">

    **Shell Flags:** `-mo` or `--metadata-only` (ex. `--metadata-only`)

    **Environment Variable:** `PMM_METADATA_ONLY` (ex. `PMM_METADATA_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --metadata-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --metadata-only
            ```

??? blank "Playlists Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-po`/`--playlists-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_PLAYLISTS_ONLY`<a class="headerlink" href="#playlists-only" title="Permanent link">¶</a>"

    <div id="playlists-only" />Only run playlist YAML files, skip library operations, overlays, collections, and metadata.

    <hr style="margin: 0px;">

    **Shell Flags:** `-po` or `--playlists-only` (ex. `--playlists-only`)

    **Environment Variable:** `PMM_PLAYLISTS_ONLY` (ex. `PMM_PLAYLISTS_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --playlists-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --playlists-only
            ```

??? blank "Operations Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-op`/`--operations-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_OPERATIONS_ONLY`<a class="headerlink" href="#operations-only" title="Permanent link">¶</a>"

    <div id="operations-only" />Only run library operations skipping collections, metadata, playlists, and overlays.

    <hr style="margin: 0px;">

    **Shell Flags:** `-op` or `--operations-only` (ex. `--operations-only`)

    **Environment Variable:** `PMM_OPERATIONS_ONLY` (ex. `PMM_OPERATIONS_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --operations-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --operations-only
            ```

??? blank "Overlays Only&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ov`/`--overlays-only`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_OVERLAYS_ONLY`<a class="headerlink" href="#overlays-only" title="Permanent link">¶</a>"

    <div id="overlays-only" />Only run library overlay files skipping collections, metadata, playlists, and operations.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-ov` or `--overlays-only` (ex. `--overlays-only`)

    **Environment Variable:** `PMM_OVERLAYS_ONLY` (ex. `PMM_OVERLAYS_ONLY=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --overlays-only
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --overlays-only
            ```

??? blank "Run Collections&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-rc`/`--run-collections`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_RUN_COLLECTIONS`<a class="headerlink" href="#run-collections" title="Permanent link">¶</a>"

    <div id="run-collections" />Perform a collections run immediately to run only the pre-defined collections, bypassing 
    the time to run flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list of Collection Names to run; the "pipe" character is "|" as shown in the examples below.

    **Shell Flags:** `-rc` or `--run-collections` (ex. `--run-collections "Harry Potter|Star Wars"`)

    **Environment Variable:** `PMM_RUN_COLLECTIONS` (ex. `PMM_RUN_COLLECTIONS=Harry Potter|Star Wars`)

    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --run-collections "Harry Potter|Star Wars"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-collections "Harry Potter|Star Wars"
            ```

??? blank "Run Libraries&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-rl`/`--run-libraries`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_RUN_LIBRARIES`<a class="headerlink" href="#run-libraries" title="Permanent link">¶</a>"

    <div id="run-libraries" />Perform a libraries run immediately to run only the pre-defined libraries, bypassing the 
    time to run flag.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list of Library Names to run; the "pipe" character is "|" as shown in the examples below.

    **Shell Flags:** `-rl` or `--run-libraries` (ex. `--run-libraries "Movies - 4K|TV Shows - 4K"`)

    **Environment Variable:** `PMM_RUN_LIBRARIES` (ex. `PMM_RUN_LIBRARIES=Movies - 4K|TV Shows - 4K`)

    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --run-libraries "Movies - 4K|TV Shows - 4K"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-libraries "Movies - 4K|TV Shows - 4K"
            ```

??? blank "Run Files&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-rf`/`--run-files`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_RUN_FILES`<a class="headerlink" href="#run-files" title="Permanent link">¶</a>"

    <div id="run-files" />Perform a run immediately to run only the pre-defined Collection, Metadata or Playlist files, 
    bypassing the time to run flag. This works for all different paths i.e. `pmm`, `git`, `url`, `file`, or `repo`.

    ???+ warning
         
         Do not use this to run Overlay files, as Overlay files must run all together or not at all due to their nature.

    <hr style="margin: 0px;">

    **Accepted Values:** Pipe-separated list of Collection, Metadata or Playlist Filenames to run; the "pipe" character is "|" as shown in the examples below.

    **Shell Flags:** `-rf` or `--run-files` (ex. `--run-files "Movies.yml|MovieCharts"`)

    **Environment Variable:** `PMM_RUN_FILES` (ex. `PMM_RUN_FILES=Movies.yml|MovieCharts`)

    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --run-files "Movies.yml|MovieCharts"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-files "Movies.yml|MovieCharts"
            ```

??? blank "Ignore Schedules&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-is`/`--ignore-schedules`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_IGNORE_SCHEDULES`<a class="headerlink" href="#ignore-schedules" title="Permanent link">¶</a>"

    <div id="ignore-schedules" />Ignore all schedules for the run. Range Scheduled collections (such as Christmas 
    movies) will still be ignored.

    <hr style="margin: 0px;">

    **Shell Flags:** `-is` or `--ignore-schedules` (ex. `--ignore-schedules`)

    **Environment Variable:** `PMM_IGNORE_SCHEDULES` (ex. `PMM_IGNORE_SCHEDULES=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --ignore-schedules
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --ignore-schedules
            ```

??? blank "Ignore Ghost&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ig`/`--ignore-ghost`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_IGNORE_GHOST`<a class="headerlink" href="#ignore-ghost" title="Permanent link">¶</a>"

    <div id="ignore-ghost" />Ignore all ghost logging for the run. A ghost log is what's printed to the console to show 
    progress during steps.

    <hr style="margin: 0px;">

    **Shell Flags:** `-ig` or `--ignore-ghost` (ex. `--ignore-ghost`)

    **Environment Variable:** `PMM_IGNORE_GHOST` (ex. `PMM_IGNORE_GHOST=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --ignore-ghost
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --ignore-ghost
            ```

??? blank "Delete Collections&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-dc`/`--delete-collections`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_DELETE_COLLECTIONS`<a class="headerlink" href="#delete-collections" title="Permanent link">¶</a>"

    <div id="delete-collections" />Delete all collections in a Library prior to running collections/operations.

    ???+ warning
         
        You will lose **all** collections in the library - this will delete all collections, including ones not created 
        or maintained by Plex Meta Manager.

    <hr style="margin: 0px;">

    **Shell Flags:** `-dc` or `--delete-collections` (ex. `--delete-collections`)

    **Environment Variable:** `PMM_DELETE_COLLECTIONS` (ex. `PMM_DELETE_COLLECTIONS=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --delete-collections
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --delete-collections
            ```

??? blank "Delete Labels&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-dl`/`--delete-labels`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_DELETE_LABELS`<a class="headerlink" href="#delete-labels" title="Permanent link">¶</a>"

    <div id="delete-labels" />Delete all labels on every item in a Library prior to running collections/operations.

    ???+ warning
    
        To preserve functionality of PMM, this will **not** remove the Overlay label, which is required for PMM to know 
        which items have Overlays applied.
    
        This will impact any [Smart Label Collections](../files/builders/smart.md#smart-label) that you have in your 
        library.
    
        We do not recommend using this on a regular basis if you also use any operations or collections that update 
        labels, as you are effectively deleting and adding labels on each run.

    <hr style="margin: 0px;">

    **Shell Flags:** `-dl` or `--delete-labels` (ex. `--delete-labels`)

    **Environment Variable:** `PMM_DELETE_LABELS` (ex. `PMM_DELETE_LABELS=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --delete-labels
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --delete-labels
            ```

??? blank "Resume Run&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-re`/`--resume`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_RESUME`<a class="headerlink" href="#resume" title="Permanent link">¶</a>"

    <div id="resume" />Perform a resume run immediately resuming from the first instance of the specified collection, 
    bypassing the time to run flag.

    <hr style="margin: 0px;">

    **Shell Flags:** `-re` or `--resume` (ex. `--resume "Star Wars"`)

    **Environment Variable:** `PMM_RESUME` (ex. `PMM_RESUME=Star Wars`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --resume "Star Wars"
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --resume "Star Wars"
            ```

??? blank "No Countdown&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-nc`/`--no-countdown`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_NO_COUNTDOWN`<a class="headerlink" href="#no-countdown" title="Permanent link">¶</a>"

    <div id="no-countdown" />Run without displaying a countdown to the next scheduled run.

    <hr style="margin: 0px;">

    **Shell Flags:** `-nc` or `--no-countdown` (ex. `--no-countdown`)

    **Environment Variable:** `PMM_NO_COUNTDOWN` (ex. `PMM_NO_COUNTDOWN=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --no-countdown
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-countdown
            ```

??? blank "No Missing&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-nm`/`--no-missing`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_NO_MISSING`<a class="headerlink" href="#no-missing" title="Permanent link">¶</a>"

    <div id="no-missing" />Run without utilizing the missing movie/show functions.

    <hr style="margin: 0px;">

    **Shell Flags:** `-nm` or `--no-missing` (ex. `--no-missing`)

    **Environment Variable:** `PMM_NO_MISSING` (ex. `PMM_NO_MISSING=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --no-missing
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-missing
            ```

??? blank "No Report&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-nr`/`--no-report`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_NO_REPORT`<a class="headerlink" href="#no-report" title="Permanent link">¶</a>"

    <div id="no-report" />Run without saving the report.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-nr` or `--no-report` (ex. `--no-report`)

    **Environment Variable:** `PMM_NO_REPORT` (ex. `PMM_NO_REPORT=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --no-report
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-report
            ```

??? blank "Read Only Config&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-ro`/`--read-only-config`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_READ_ONLY_CONFIG`<a class="headerlink" href="#read-only-config" title="Permanent link">¶</a>"

    <div id="read-only-config" />Run without writing to the configuration file.

    <hr style="margin: 0px;">

    **Shell Flags:**  `-ro` or `--read-only-config` (ex. `--read-only-config`)

    **Environment Variable:** `PMM_READ_ONLY_CONFIG` (ex. `PMM_READ_ONLY_CONFIG=true`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --read-only-config
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --read-only-config
            ```

??? blank "Divider Character&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-d`/`--divider`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_DIVIDER`<a class="headerlink" href="#divider" title="Permanent link">¶</a>"

    <div id="divider" />Change the terminal output divider character. Will default to `=` if not specified.

    <hr style="margin: 0px;">

    **Accepted Values:** Any character

    **Shell Flags:** `-d` or `--divider` (ex. `--divider *`)

    **Environment Variable:** `PMM_DIVIDER` (ex. `PMM_DIVIDER=*`)
    
    !!! example
        === "Local Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --divider *
            python plex_meta_manager.py --divider *
            ```
        === "Docker Environment"
            ```
            ```

??? blank "Screen Width&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-w`/`--width`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_WIDTH`<a class="headerlink" href="#width" title="Permanent link">¶</a>"

    <div id="width" />Change the terminal output width. Will default to `100` if not specified.

    <hr style="margin: 0px;">

    **Accepted Values:** Integer between 90 and 300

    **Shell Flags:** `-w` or `--width` (ex. `--width 150`)

    **Environment Variable:** `PMM_WIDTH` (ex. `PMM_WIDTH=150`)
    
    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --width 150
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --width 150
            ```

??? blank "Config Secrets&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--pmm-***`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`PMM_***`<a class="headerlink" href="#pmm-vars" title="Permanent link">¶</a>"

    <div id="pmm-vars" />All Run Commands that are in the format `--pmm-***` and Environment Variables that are in the 
    format `PMM_***`, where `***` is the name you want to call the variable, will be loaded in as Config Secrets.
    
    These Config Secrets can be loaded into the config by placing `<<***>>` in any field in the config, where `***` is 
    whatever name you called the variable.  

    <hr style="margin: 0px;">

    **Shell Flags:** `--pmm-***` (ex. `--pmm-mysecret 123456789`)

    **Environment Variable:** `PMM_***` (ex. `PMM_MYSECRET=123456789`)

    !!! example
        === "Local Environment"
            ```
            python plex_meta_manager.py --pmm-mysecret 123456789
            ```
        === "Docker Environment"
            ```
            docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --pmm-mysecret 123456789
            ```
    
        **Example Config Usage:**
    
        ```yaml
        tmdb:
          apikey: <<mysecret>>
        ```
