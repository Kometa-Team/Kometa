# Run Commands & Environment Variables

This table outlines the run commands and environment variables that can be utilized to customize the running of Plex Meta Manager to the user's requirements. Environment Variable values are used over Shell Command values.

If you run into a race condition where you have set an Environment Variable within your system and also use a Shell Command for the same attribute, then the Environment Variable will take priority.

These docs are assuming you have a basic understanding of Docker concepts.  One place to get familiar with Docker would be the [official tutorial](https://www.docker.com/101-tutorial/).

Environment Variables can also be placed inside a `.env` file inside your config folder.

| Attribute                                             | Shell Command                                 | Environment Variable     |
|:------------------------------------------------------|:----------------------------------------------|:-------------------------|
| [Config](#config)                                     | `-c` or `--config`                            | `PMM_CONFIG`             |
| [Time to Run](#time-to-run)                           | `-t` or `--times`                             | `PMM_TIMES`              |
| [Run Immediately](#run-immediately)                   | `-r` or `--run`                               | `PMM_RUN`                |
| [Run Tests](#run-tests)                               | `-rt`, `--tests`, or `--run-tests`            | `PMM_TESTS`              |
| [Debug](#debug)                                       | `-db` or `--debug`                            | `PMM_DEBUG`              |
| [Trace](#trace)                                       | `-tr` or `--trace`                            | `PMM_TRACE`              |
| [Log Requests](#log-requests)                         | `-lr` or `--log-requests`                     | `PMM_LOG_REQUESTS`       |
| [Timeout](#timeout)                                   | `-ti` or `--timeout`                          | `PMM_TIMEOUT`            |
| [Collections Only](#collections-only)                 | `-co` or `--collections-only`                 | `PMM_COLLECTIONS_ONLY`   |
| [Playlists Only](#playlists-only)                     | `-po` or `--playlists-only`                   | `PMM_PLAYLISTS_ONLY`     |
| [Operations Only](#operations-only)                   | `-op`, `--operations`, or `--operations-only` | `PMM_OPERATIONS_ONLY`    |
| [Overlays Only](#overlays-only)                       | `-ov`, `--overlays`, or `--overlays-only`     | `PMM_OVERLAYS_ONLY`      |
| [Run Collections](#run-collections)                   | `-rc` or `--run-collections`                  | `PMM_RUN_COLLECTIONS`    |
| [Run Libraries](#run-libraries)                       | `-rl` or `--run-libraries`                    | `PMM_RUN_LIBRARIES`      |
| [Run Metadata Files](#run-metadata-files)             | `-rm` or `--run-metadata-files`               | `PMM_RUN_METADATA_FILES` |
| [Libraries First](#libraries-first)                   | `-lf` or `--libraries-first`                  | `PMM_LIBRARIES_FIRST`    |
| [Ignore Schedules](#ignore-schedules)                 | `-is` or `--ignore-schedules`                 | `PMM_IGNORE_SCHEDULES`   |
| [Ignore Ghost](#ignore-ghost)                         | `-ig` or `--ignore-ghost`                     | `PMM_IGNORE_GHOST`       |
| [Cache Libraries](#cache-libraries)                   | `-ca` or `--cache-libraries`                  | `PMM_CACHE_LIBRARIES`    |
| [Delete Collections](#delete-collections)             | `-dc` or `--delete-collections`               | `PMM_DELETE_COLLECTIONS` |
| [Delete Labels](#delete-labels)                       | `-dl` or `--delete-labels`                    | `PMM_DELETE_LABELS`      |
| [Resume Run](#resume-run)                             | `-re` or `--resume`                           | `PMM_RESUME`             |
| [No Countdown](#no-countdown)                         | `-nc` or `--no-countdown`                     | `PMM_NO_COUNTDOWN`       |
| [No Missing](#no-missing)                             | `-nm` or `--no-missing`                       | `PMM_NO_MISSING`         |
| [No Report](#no-report)                               | `-nr` or `--no-report`                        | `PMM_NO_REPORT`          |
| [Read Only Config](#read-only-config)                 | `-ro` or `--read-only-config`                 | `PMM_READ_ONLY_CONFIG`   |
| [Divider Character](#divider-character--screen-width) | `-d` or `--divider`                           | `PMM_DIVIDER`            |
| [Screen Width](#divider-character--screen-width)      | `-w` or `--width`                             | `PMM_WIDTH`              |
| [Config Secrets](#config-secrets)                     | `--pmm-***`                                   | `PMM_***`                |

Further explanation and examples of each command can be found below.

## Run Command Attribute Examples

Environment variables are expressed as `KEY=VALUE`  Depending on the context where you are specifying them, you may enter those two things in two different fields, or some other way.  The examples below show how you would specify the environment variable in a script or a `docker run` command.  Things like Portainer or a NAS Docker UI will have different ways to specify these things.

### Config

Specify the location of the configuration YAML file.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-c</code> or <code>--config</code></td>
    <td><code>PMM_CONFIG</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--config /data/config.yml</code></td>
    <td><code>PMM_CONFIG=/data/config.yml</code></td>
  </tr>
  <tr>
    <th>Default</th>
    <td colspan="2"><code>config/config.yml</code></td>
  </tr>
  <tr>
    <th>Values</th>
    <td colspan="2">Path to YAML config file</td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --config <path_to_config>
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --config <path_to_config>
```
````

### Time to Run

Specify the time of day that Plex Meta Manager will run.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-t</code> or <code>--times</code></td>
    <td><code>PMM_TIMES</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--times 06:00,18:00</code></td>
    <td><code>PMM_TIMES=06:00,18:00</code></td>
  </tr>
  <tr>
    <th>Default Value</th>
    <td colspan="2"><code>05:00</code></td>
  </tr>
  <tr>
    <th>Available Values</th>
    <td colspan="2">comma-separated list in <code>HH:MM</code> format</td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --times 22:00,03:00
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --times 22:00,03:00
```
````

### Run Immediately

Perform a run immediately, bypassing the time to run flag.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-r</code> or <code>--run</code></td>
    <td><code>PMM_RUN</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run</code></td>
    <td><code>PMM_RUN=true</code></td>
  </tr>
</table>

````{tab} Local Environment

```
python plex_meta_manager.py --run
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run
```
````

### Run Tests

Perform a debug test run immediately, bypassing the time to run flag. This will only run collections with `test: true` in the definition.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-rt</code>, <code>--tests</code>, or <code>--run-tests</code></td>
    <td><code>PMM_TESTS</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run-tests</code></td>
    <td><code>PMM_TESTS=true</code></td>
  </tr>
</table>

* Only collections with `test: true` enabled will be run

````{tab} Local Environment
```
python plex_meta_manager.py --run-tests
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-tests
```
````

### Debug

Run with Debug Logs Reporting to the Command Window.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-db</code> or <code>--debug</code></td>
    <td><code>PMM_DEBUG</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--debug</code></td>
    <td><code>PMM_DEBUG=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --debug
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --debug
```
````

### Trace

Run with extra Trace Debug Logs.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-tr</code> or <code>--trace</code></td>
    <td><code>PMM_TRACE</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--trace</code></td>
    <td><code>PMM_TRACE=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --trace
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --trace
```
````

### Log Requests

Run with every network request printed to the Logs. **This can potentially have personal information in it.**

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-lr</code> or <code>--log-request</code> or <code>--log-requests</code></td>
    <td><code>PMM_LOG_REQUESTS</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--log-requests</code></td>
    <td><code>PMM_LOG_REQUESTS=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --log-requests
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --log-requests
```
````

### Timeout

Change the timeout for all non-Plex services (such as TMDb, Radarr, and Trakt). This is overwritten by any timeouts mentioned for specific services in the Configuration File.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-ti</code> or <code>--timeout</code></td>
    <td><code>PMM_TIMEOUT</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--timeout 360</code></td>
    <td><code>PMM_TIMEOUT=360</code></td>
  </tr>
  <tr>
    <th>Values</th>
    <td colspan="2">Integer Number of Seconds</td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --timeout 360
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --timeout 360
```
````

### Collections Only

Only run collection metadata/YAML files, skip library operations, overlays, and playlists.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>

  <tr>
    <th>Flags</th>
    <td><code>-co</code> or <code>--collections-only</code></td>
    <td><code>PMM_COLLECTIONS_ONLY</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--collections-only</code></td>
    <td><code>PMM_COLLECTIONS_ONLY=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --collections-only
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --collections-only
```
````

### Playlists Only

Only run playlist metadata/YAML files, skip library operations, overlays, and collections/metadata.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-po</code> or <code>--playlists-only</code></td>
    <td><code>PMM_PLAYLISTS_ONLY</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--playlists-only</code></td>
    <td><code>PMM_PLAYLISTS_ONLY=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --playlists-only
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --playlists-only
```
````

### Operations Only

Only run library operations skipping collections/metadata, playlists, and overlays.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-op</code>, <code>--operations</code>, or <code>--operations-only</code></td>
    <td><code>PMM_OPERATIONS_ONLY</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--operations-only</code></td>
    <td><code>PMM_OPERATIONS_ONLY=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --operations-only
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --operations-only
```
````

### Overlays Only

Only run library overlays skipping collections/metadata, playlists, and operations.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-ov</code>, <code>--overlays</code>, or <code>--overlays-only</code></td>
    <td><code>PMM_OVERLAYS_ONLY</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--overlays-only</code></td>
    <td><code>PMM_OVERLAYS_ONLY=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --overlays-only
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --overlays-only
```
````

### Run Collections

Perform a collections run immediately to run only the pre-defined collections, bypassing the time to run flag.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-rc</code> or <code>--run-collections</code></td>
    <td><code>PMM_RUN_COLLECTIONS</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run-collections "Harry Potter|Star Wars"</code></td>
    <td><code>PMM_RUN_COLLECTIONS=Harry Potter|Star Wars</code></td>
  </tr>
  <tr>
    <th>Values</th>
    <td colspan="2">Pipe-separated list of Collection Names to run</td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --run-collections "Harry Potter|Star Wars"
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-collections "Harry Potter|Star Wars"
```
````

### Run Libraries

Perform a libraries run immediately to run only the pre-defined libraries, bypassing the time to run flag.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-rl</code> or <code>--run-libraries</code></td>
    <td><code>PMM_RUN_LIBRARIES</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run-libraries "Movies - 4K|TV Shows - 4K"</code></td>
    <td><code>PMM_RUN_LIBRARIES=Movies - 4K|TV Shows - 4K</code></td>
  </tr>
  <tr>
    <th>Values</th>
    <td colspan="2">Pipe-separated list of Library Names to run</td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --run-libraries "TV Shows"
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-libraries "TV Shows"
```
````

### Run Metadata Files

Perform a metadata files run immediately to run only the pre-defined metadata files, bypassing the time to run flag.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-rm</code> or <code>--run-metadata-files</code></td>
    <td><code>PMM_RUN_METADATA_FILES</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run-metadata-files "Movies.yml|MovieCharts"</code></td>
    <td><code>PMM_RUN_METADATA_FILES=Movies.yml|MovieCharts</code></td>
  </tr>
  <tr>
    <th>Available Values</th>
    <td colspan="2">Pipe-separated list of Metadata Filenames to run</td>
  </tr>
</table>

* This works for all different metadata paths i.e. `git`, `url`, `file`, or `repo`.
````{tab} Local Environment
```
python plex_meta_manager.py --run-metadata-files "Movies"
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-metadata-files "Movies"
```
````

### Libraries First

Run library operations prior to running collections.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-lf</code> or <code>--libraries-first</code></td>
    <td><code>PMM_LIBRARIES_FIRST</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--libraries-first</code></td>
    <td><code>PMM_LIBRARIES_FIRST=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --libraries-first
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --libraries-first
```
````

### Ignore Schedules

Ignore all schedules for the run.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-is</code> or <code>--ignore-schedules</code></td>
    <td><code>PMM_IGNORE_SCHEDULES</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--ignore-schedules</code></td>
    <td><code>PMM_IGNORE_SCHEDULES=true</code></td>
  </tr>
</table>

* Range Scheduled collections (such as Christmas movies) will still be ignored.
````{tab} Local Environment
```
python plex_meta_manager.py --ignore-schedules
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --ignore-schedules
```
````

### Ignore Ghost

Ignore all ghost logging for the run. A ghost log is what's printed to the console to show progress during steps.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-ig</code> or <code>--ignore-ghost</code></td>
    <td><code>PMM_IGNORE_GHOST</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--ignore-ghost</code></td>
    <td><code>PMM_IGNORE_GHOST=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --ignore-ghost
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --ignore-ghost
```
````

### Cache Libraries

Cache the library Load for 1 day.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-ca</code> or <code>--cache-libraries</code></td>
    <td><code>PMM_CACHE_LIBRARIES</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--cache-libraries</code></td>
    <td><code>PMM_CACHE_LIBRARIES=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --cache-libraries
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --cache-libraries
```
````

### Delete Collections

Delete all collections in a Library prior to running collections/operations.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-dc</code> or <code>--delete-collections</code></td>
    <td><code>PMM_DELETE_COLLECTIONS</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--delete-collections</code></td>
    <td><code>PMM_DELETE_COLLECTIONS=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --delete-collections
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --delete-collections
```
````

### Delete Labels

Delete all labels on every item in a Library prior to running collections/operations.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-dl</code> or <code>--delete-labels</code></td>
    <td><code>PMM_DELETE_LABELS</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--delete-labels</code></td>
    <td><code>PMM_DELETE_LABELS=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --delete-labels
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --delete-labels
```
````

### Resume Run

Perform a resume run immediately resuming from the first instance of the specified collection, bypassing the time to run flag.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-re</code> or <code>--resume</code></td>
    <td><code>PMM_RESUME</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--resume "Star Wars"</code></td>
    <td><code>PMM_RESUME=Star Wars</code></td>
  </tr>
  <tr>
    <th>Available Values</th>
    <td colspan="2">Name of collection to resume from</td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --resume "Star Wars"
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --resume "Star Wars"
```
````

### No Countdown

Run without displaying a countdown to the next scheduled run.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-nc</code> or <code>--no-countdown</code></td>
    <td><code>PMM_NO_COUNTDOWN</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--no-countdown</code></td>
    <td><code>PMM_NO_COUNTDOWN=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --no-countdown
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-countdown
```
````

### No Missing

Run without utilizing the missing movie/show functions.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-nm</code> or <code>--no-missing</code></td>
    <td><code>PMM_NO_MISSING</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--no-missing</code></td>
    <td><code>PMM_NO_MISSING=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --no-missing
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-missing
```
````

### No Report

Run without saving the report.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-nr</code> or <code>--no-report</code></td>
    <td><code>PMM_NO_REPORT</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--no-report</code></td>
    <td><code>PMM_NO_REPORT=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --no-report
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-report
```
````

### Read Only Config

Run without writing to the configuration file.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-ro</code> or <code>--read-only-config</code></td>
    <td><code>PMM_READ_ONLY_CONFIG</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--read-only-config</code></td>
    <td><code>PMM_READ_ONLY_CONFIG=true</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --read-only-config
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --read-only-config
```
````

### Divider Character & Screen Width

Change the terminal output divider character or width.

#### Divider Character

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-d</code> or <code>--divider</code></td>
    <td><code>PMM_DIVIDER</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--divider *</code></td>
    <td><code>PMM_DIVIDER=*</code></td>
  </tr>
  <tr>
    <th>Default</th>
    <td colspan="2"><code>=</code></td>
  </tr>
  <tr>
    <th>Values</th>
    <td colspan="2">A character</td>
  </tr>
</table>

#### Screen Width

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-w</code> or <code>--width</code></td>
    <td><code>PMM_WIDTH</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--width 150</code></td>
    <td><code>PMM_WIDTH=150</code></td>
  </tr>
  <tr>
    <th>Default</th>
    <td colspan="2">Integer between 90 and 300</td>
  </tr>
  <tr>
    <th>Values</th>
    <td colspan="2">A character</td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --divider * --width 200
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --divider * --width 200
```
````

### Config Secrets

All Run Commands that start with `--pmm-***` and Environment Variables that start with `PMM_***` will be loaded in as Config Secrets.

These Config Secrets can be loaded into the config by placing `<<***>>` in any field in the config, where `***` is whatever name you want to call the variable.  

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #1d1d1d;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>--pmm-***</code></td>
    <td><code>PMM_***</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--pmm-mysecret 123456789</code></td>
    <td><code>PMM_MYSECRET=123456789</code></td>
  </tr>
</table>

````{tab} Local Environment
```
python plex_meta_manager.py --pmm-mysecret 123456789
```
````
````{tab} Docker Environment
```
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --pmm-mysecret 123456789
```
````

#### Example Config Usage

```yaml
tmdb:
  apikey: <<mysecret>>
```
