
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

To customize the running of Plex Meta Manager according to your needs, you can use either run commands or environmental variables. Environmental variables take precedence over run command attributes. However, if you encounter a race condition where an attribute has been set both via an environmental variable and a shell command, the environmental variable will be given priority.

Please note that these instructions assume that you have a basic understanding of Docker concepts. If you need to familiarize yourself with Docker, you can check out the official tutorial.

Another way to specify environmental variables is by adding them to a .env file located in your config folder.

[official tutorial](https://www.docker.com/101-tutorial/).


| Attribute                                             | Shell Command                                 | Environment Variable      |
|:------------------------------------------------------|:----------------------------------------------|:--------------------------|
| [Config](#config)                                     | `-c` or `--config`                            | `PMM_CONFIG`              |
| [Time to Run](#time-to-run)                           | `-t` or `--times`                             | `PMM_TIMES`               |
| [Run Immediately](#run-immediately)                   | `-r` or `--run`                               | `PMM_RUN`                 |
| [Run Tests](#run-tests)                               | `-rt`, `--tests`, or `--run-tests`            | `PMM_TESTS`                |
| [Debug](#debug)                                       | `-db` or `--debug`                            | `PMM_DEBUG`               |
| [Trace](#trace)                                       | `-tr` or `--trace`                            | `PMM_TRACE`               |
| [Log Requests](#log-requests)                         | `-lr` or `--log-requests`                     | `PMM_LOG_REQUESTS`        |
| [Timeout](#timeout)                                   | `-ti` or `--timeout`                          | `PMM_TIMEOUT`             |
| [Collections Only](#collections-only)                 | `-co` or `--collections-only`                 | `PMM_COLLECTIONS_ONLY`    |
| [Playlists Only](#playlists-only)                     | `-po` or `--playlists-only`                   | `PMM_PLAYLISTS_ONLY`      |
| [Operations Only](#operations-only)                   | `-op`, `--operations`, or `--operations-only` | `PMM_OPERATIONS_ONLY`     |
| [Overlays Only](#overlays-only)                       | `-ov`, `--overlays`, or `--overlays-only`     | `PMM_OVERLAYS_ONLY`       |
| [Run Collections](#run-collections)                   | `-rc` or `--run-collections`                  | `PMM_RUN_COLLECTIONS`     |
| [Run Libraries](#run-libraries.md)                       | `-rl` or `--run-libraries`                    | `PMM_RUN_LIBRARIES`       |
| [Run Metadata Files](#run-metadata-files)             | `-rm` or `--run-metadata-files`               | `PMM_RUN_METADATA_FILES`  |
| [Libraries First](#libraries-first)                   | `-lf` or `--libraries-first`                  | `PMM_LIBRARIES_FIRST`     |
| [Ignore Schedules](#ignore-schedules)                 | `-is` or `--ignore-schedules`                 | `PMM_IGNORE_SCHEDULES`    |
| [Ignore Ghost](#ignore-ghost)                         | `-ig` or `--ignore-ghost`                     | `PMM_IGNORE_GHOST`        |
| [Delete Collections](#delete-collections)             | `-dc` or `--delete-collections`               | `PMM_DELETE_COLLECTIONS`  |
| [Delete Labels](#delete-labels)                       | `-dl` or `--delete-labels`                    | `PMM_DELETE_LABELS`       |
| [Resume Run](#resume-run)                             | `-re` or `--resume`                           | `PMM_RESUME`              |
| [No Countdown](#no-countdown)                         | `-nc` or `--no-countdown`                     | `PMM_NO_COUNTDOWN`        |
| [No Missing](#no-missing)                             | `-nm` or `--no-missing`                       | `PMM_NO_MISSING`          |
| [No Report](#no-report)                               | `-nr` or `--no-report`                        | `PMM_NO_REPORT`           |
| [Read Only Config](#read-only-config)                 | `-ro` or `--read-only-config`                 | `PMM_READ_ONLY_CONFIG`    |
| [Divider Character](#divider-character--screen-width) | `-d` or `--divider`                           | `PMM_DIVIDER`             |
| [Screen Width](#divider-character--screen-width)      | `-w` or `--width`                             | `PMM_WIDTH`               |
| [Config Secrets](#config-secrets)                     | `--pmm-***`                                   | `PMM_***`                 |

Further explanation and examples of each command can be found below.

Environment variables are expressed as `KEY=VALUE` depending on the context where you are specifying them, you may enter those two things in two different fields, or some other way.  The examples below show how you would specify the environment variable in a script or a `docker run` command.  Things like Portainer or a NAS Docker UI will have different ways to specify these things.

## Config

Specify the location of the configuration YAML file.

|           | Shell                       | Environment                   |
|-----------|-----------------------------|-------------------------------|
| Flags     | `-c` or `--config`          | `PMM_CONFIG`                  |
| Example   | `--config /data/config.yml` | `PMM_CONFIG=/data/config.yml` |
| Default   | `config/config.yml`         | `config/config.yml`           |
| Values    | Path to YAML config file    | Path to YAML config file      |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --config /data/config.yml
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --config /data/config.yml
        ```

### Time to Run

Specify the time of day that Plex Meta Manager will run.

|                  | Shell Command                                      | Environment Variable       |
|:-----------------|:---------------------------------------------------|:---------------------------|
| Flags            | `-t` or `--times`                                  | `PMM_TIMES`                |
| Example          | `--times 06:00,18:00`                              | `PMM_TIMES=06:00,18:00`    |
| Default Value    | <code>05:00</code>                                 |
| Available Values | comma-separated list in <code>HH:MM</code> format  |
!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --times 22:00,03:00
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --times 22:00,03:00
        ```

### Run Immediately

Perform a run immediately, bypassing the time to run flag.

|         | Shell Command   | Environment Variable  |
|:--------|:----------------|:----------------------|
| Flags   | `-r` or `--run` | `PMM_RUN`             |
| Example | `--run`         | `PMM_RUN=true`        |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --run
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run
        ```

### Run Tests

Perform a debug test run immediately, bypassing the time to run flag. This will only run collections with `test: true` in the definition.

|          | Shell Command                      | Environment Variable |
|:---------|:-----------------------------------|:---------------------|
| Flags    | `-rt`, `--tests`, or `--run-tests` | `PMM_TESTS`           |
| Example  | `--run-tests`                      | `PMM_TESTS=true`      |


* Only collections with `test: true` enabled will be run

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --run-tests
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-tests
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
collections:
  Marvel Cinematic Universe:
    trakt_list: https://trakt.tv/users/jawann2002/lists/marvel-cinematic-universe-movies?sort=rank,asc
    smart_label: release.desc


### Debug

Run with Debug Logs Reporting to the Command Window.

|         | Shell Command      | Environment Variable  |
|:--------|:-------------------|:----------------------|
| Flags   | `-db` or `--debug` | `PMM_DEBUG`           |
| Example | `--debug`          | `PMM_DEBUG=true`      |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --debug
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --debug
        ```

### Trace

Run with extra Trace Debug Logs.

|          | Shell Command      | Environment Variable |
|:---------|:-------------------|:---------------------|
| Flags    | `-tr` or `--trace` | `PMM_TRACE`          |
| Example  | `--trace`          | `PMM_TRACE=true`     |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --trace
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --trace
        ```

### Log Requests

Run with every network request printed to the Logs. **This can potentially have personal information in it.**

|          | Shell Command                                | Environment Variable    |
|----------|----------------------------------------------|-------------------------|
| Flags    | `-lr` or `--log-request` or `--log-requests` | `PMM_LOG_REQUESTS`      |
| Example  | `--log-requests`                             | `PMM_LOG_REQUESTS=true` | 

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --log-requests
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --log-requests
        ```

### Timeout

Change the timeout for all non-Plex services (such as TMDb, Radarr, and Trakt). This is overwritten by any timeouts mentioned for specific services in the Configuration File.

|         | Shell Command              | Environment Variable |
|:--------|:---------------------------|----------------------|
| Flags   | `-ti` or `--timeout`       | `PMM_TIMEOUT`        |
| Example | `--timeout 360`            | `PMM_TIMEOUT=360`    |
| Values  | Integer Number of Seconds  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --timeout 360
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --timeout 360
        ```

### Collections Only

Only run collection metadata/YAML files, skip library operations, overlays, and playlists.

|          | Shell Command                 | Environment Variable         |
|:---------|:------------------------------|:-----------------------------|
| Flags    | `-co` or `--collections-only` | `PMM_COLLECTIONS_ONLY`       |
| Example  | `--collections-only`          | `PMM_COLLECTIONS_ONLY=true`  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --collections-only
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --collections-only
        ```

### Playlists Only

Only run playlist metadata/YAML files, skip library operations, overlays, and collections/metadata.

|         | Shell Command                | Environment Variable      |
|:--------|:-----------------------------|:--------------------------|
| Flags   | `-po` or `--playlists-only`  | `PMM_PLAYLISTS_ONLY`      |
| Example | `--playlists-only`           | `PMM_PLAYLISTS_ONLY=true` |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --playlists-only
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --playlists-only
        ```

### Operations Only

Only run library operations skipping collections/metadata, playlists, and overlays.

|          | Shell Command           | Environment Variable       |
|:---------|:------------------------|:---------------------------|
| Flags    | `-op` or `--operations` | `PMM_OPERATIONS_ONLY`      |
| Example  | `--operations`          | `PMM_OPERATIONS_ONLY=true` |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --operations
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --operations
        ```

### Overlays Only

Only run library overlays skipping collections/metadata, playlists, and operations.

|         | Shell Command         | Environment Variable      |
|:--------|:----------------------|:--------------------------|
| Flags   | `-ov` or `--overlays` | `PMM_OVERLAYS_ONLY`       |
| Example | `--overlays`          | `PMM_OVERLAYS_ONLY=true`  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --overlays
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --overlays
        ```

### Run Collections

Perform a collections run immediately to run only the pre-defined collections, bypassing the time to run flag.

|         | Shell Command                                     | Environment Variable                         |
|:--------|:--------------------------------------------------|:---------------------------------------------|
| Flags   | `-rc` or `--run-collections`                      | `PMM_RUN_COLLECTIONS`                        |
| Example | --run-collections "Harry Potter&#124;Star Wars"   | PMM_COLLECTIONS=Harry Potter&#124;Star Wars  |
| Values  | Pipe-separated list of Collection Names to run    |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --run-collections "Harry Potter|Star Wars"
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-collections "Harry Potter|Star Wars"
        ```

### Run Libraries

Perform a libraries run immediately to run only the pre-defined libraries, bypassing the time to run flag.

|         | Shell Command                                     | Environment Variable                           |
|:--------|:--------------------------------------------------|:-----------------------------------------------|
| Flags   | `-rl` or `--run-libraries`                        | `PMM_RUN_LIBRARIES`                            |
| Example | --run-libraries "Movies - 4K&#124;TV Shows - 4K"  | PMM_LIBRARIES=Movies - 4K&#124;TV Shows - 4K`  |
| Values  | Pipe-separated list of Library Names to run       |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --run-libraries "Movies - 4K|TV Shows - 4K"
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-libraries "Movies - 4K|TV Shows - 4K"
        ```

### Run Metadata Files

Perform a metadata files run immediately to run only the pre-defined metadata files, bypassing the time to run flag.

???+ warning
     
     Do not use this to run Overlay files, as Overlay files must run all together or not at all due to their nature.

|                  | Shell Command                                           | Environment Variable                           |
|:-----------------|:--------------------------------------------------------|:-----------------------------------------------|
| Flags            | `-rm` or `--run-metadata-files`                         | `PMM_RUN_METADATA_FILES`                       |
| Example          | --run-metadata-files "Movies.yml&#124;MovieCharts"      | PMM_METADATA_FILES=Movies.yml&#124;MovieCharts |
| Available Values | Pipe-separated list of Metadata Filenames to run        |


* This works for all different metadata paths i.e. `pmm`, `git`, `url`, `file`, or `repo`.

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --run-metadata-files "Movies.yml|seasonal|genre"
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-metadata-files "Movies.yml|seasonal|genre"
        ```

### Libraries First

Run library operations prior to running collections.

|         | Shell Command                | Environment Variable       |
|:--------|:-----------------------------|:---------------------------|
| Flags   | `-lf` or `--libraries-first` | `PMM_LIBRARIES_FIRST`      |
| Example | `--libraries-first`          | `PMM_LIBRARIES_FIRST=true` |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --libraries-first
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --libraries-first
        ```

### Ignore Schedules

Ignore all schedules for the run.

|          | Shell Command                 | Environment Variable         |
|:---------|:------------------------------|:-----------------------------|
| Flags    | `-is` or `--ignore-schedules` | `PMM_IGNORE_SCHEDULES`       |
| Example  | `--ignore-schedules`          | `PMM_IGNORE_SCHEDULES=true`  |


* Range Scheduled collections (such as Christmas movies) will still be ignored.

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --ignore-schedules
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --ignore-schedules
        ```

### Ignore Ghost

Ignore all ghost logging for the run. A ghost log is what's printed to the console to show progress during steps.

|          | Shell Command             | Environment Variable     |
|:---------|:--------------------------|:-------------------------|
| Flags    | `-ig` or `--ignore-ghost` | `PMM_IGNORE_GHOST`       |
| Example  | `--ignore-ghost`          | `PMM_IGNORE_GHOST=true`  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --ignore-ghost
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --ignore-ghost
        ```

### Delete Collections

Delete all collections in a Library prior to running collections/operations.

???+ warning
     
     You will lose **all** collections in the library - this will delete all collections, including ones not created or maintained by Plex Meta Manager.

|          | Shell Command                   | Environment Variable           |
|:---------|:--------------------------------|:-------------------------------|
| Flags    | `-dc` or `--delete-collections` | `PMM_DELETE_COLLECTIONS`       |
| Example  | `--delete-collections`          | `PMM_DELETE_COLLECTIONS=true`  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --delete-collections
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --delete-collections
        ```

### Delete Labels

Delete all labels on every item in a Library prior to running collections/operations.

???+ warning

     To preserve functionality of PMM, this will **not** remove the Overlay label, which is required for PMM to know which items have Overlays applied.

     This will impact any [Smart Label Collections](../../builders/smart.md#smart-label) that you have in your library.

     We do not recommend using this on a regular basis if you also use any operations or collections that update labels, as you are effectively deleting and adding labels on each run.

|          | Shell Command              | Environment Variable      |
|:---------|:---------------------------|:--------------------------|
| Flags    | `-dl` or `--delete-labels` | `PMM_DELETE_LABELS`       |
| Example  | `--delete-labels`          | `PMM_DELETE_LABELS=true`  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --delete-labels
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --delete-labels
        ```

### Resume Run

Perform a resume run immediately resuming from the first instance of the specified collection, bypassing the time to run flag.

|                   | Shell Command                      | Environment Variable   |
|:------------------|:-----------------------------------|:-----------------------|
| Flags             | `-re` or `--resume`                | `PMM_RESUME`           |
| Example           | `--resume "Star Wars"`             | `PMM_RESUME=Star Wars` |
| Available Values  | Name of collection to resume from  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --resume "Star Wars"
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --resume "Star Wars"
        ```

### No Countdown

Run without displaying a countdown to the next scheduled run.

|         | Shell Command             | Environment Variable    |
|:--------|:--------------------------|:------------------------|
| Flags   | `-nc` or `--no-countdown` | `PMM_NO_COUNTDOWN`      |
| Example | `--no-countdown`          | `PMM_NO_COUNTDOWN=true` |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --no-countdown
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-countdown
        ```

### No Missing

Run without utilizing the missing movie/show functions.

|         | Shell Command           | Environment Variable   |
|:--------|:------------------------|:-----------------------|
| Flags   | `-nm` or `--no-missing` | `PMM_NO_MISSING`       |
| Example | `--no-missing`          | `PMM_NO_MISSING=true`  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --no-missing
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-missing
        ```

### No Report

Run without saving the report.

|          | Shell Command          | Environment Variable  |
|:---------|:-----------------------|:----------------------|
| Flags    | `-nr` or `--no-report` | `PMM_NO_REPORT`       |
| Example  | `--no-report`          | `PMM_NO_REPORT=true`  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --no-report
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-report
        ```

### Read Only Config

Run without writing to the configuration file.

|          | Shell Command                 | Environment Variable         |
|:---------|:------------------------------|:-----------------------------|
| Flags    | `-ro` or `--read-only-config` | `PMM_READ_ONLY_CONFIG`       |
| Example  | `--read-only-config`          | `PMM_READ_ONLY_CONFIG=true`  |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --read-only-config
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --read-only-config
        ```

### Divider Character & Screen Width

Change the terminal output divider character or width.

#### Divider Character

|         | Shell Command       | Environment Variable  |
|:--------|:--------------------|:----------------------|
| Flags   | `-d` or `--divider` | `PMM_DIVIDER`         |
| Example | `--divider *`       | `PMM_DIVIDER=*`       |
| Default | `=`                 |
| Values  | Any character       |


#### Screen Width

|         | Shell Command                | Environment Variable |
|:--------|:-----------------------------|:---------------------|
| Flags   | `-w` or `--width`            | `PMM_WIDTH`          |
| Example | `--width 150`                | `PMM_WIDTH=150`      |
| Default | Integer between 90 and 300   |
| Values  | Any character                |

!!! example
    === "Local Environment"
        ```
        python plex_meta_manager.py --divider * --width 200
        ```
    === "Docker Environment"
        ```
        docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --divider * --width 200
        ```

### Config Secrets

All Run Commands that start with `--pmm-***` and Environment Variables that start with `PMM_***` will be loaded in as Config Secrets.

These Config Secrets can be loaded into the config by placing `<<***>>` in any field in the config, where `***` is whatever name you want to call the variable.  

|          | Shell Command               | Environment Variable      |
|:---------|:----------------------------|:--------------------------|
| Flags    | `--pmm-***`                 | `PMM_***`                 |
| Example  | `--pmm-mysecret 123456789`  | `PMM_MYSECRET=123456789`  |

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
