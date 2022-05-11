# Run Commands & Environment Variables

This table outlines the run commands and environment variables that can be utilized to customize the running of Plex Meta Manager to the user's requirements. Environment Variable values are used over Shell Command values.

If you run into a race condition where you have set an Environment Variable within your system and also use a Shell Command for the same attribute, then the Environment Variable will take priority.

These docs are assuming you have a basic understanding of Docker concepts.  One place to get familiar with Docker would be the [official tutorial](https://www.docker.com/101-tutorial/).

| Attribute                                             | Shell Command                      | Environment Variable     |
|:------------------------------------------------------|:-----------------------------------|:-------------------------|
| [Config](#config)                                     | `-c` or `--config`                 | `PMM_CONFIG`             |
| [Time to Run](#time-to-run)                           | `-t` or `--time`                   | `PMM_TIME`               |
| [Run](#run)                                           | `-r` or `--run`                    | `PMM_RUN`                |
| [Run Tests](#run-tests)                               | `-rt`, `--tests`, or `--run-tests` | `PMM_TEST`               |
| [Collections Only](#collections-only)                 | `-co` or `--collections-only`      | `PMM_COLLECTIONS_ONLY`   |
| [Plsylists Only](#plsylists-only)                     | `-po` or `--plsylists-only`        | `PMM_PLAYLISTS_ONLY`     |
| [Operations](#operations)                             | `-op` or `--operations`            | `PMM_OPERATIONS`         |
| [Overlays](#overlays)                                 | `-ov` or `--overlays`              | `PMM_OVERLAYS`           |
| [Run Collections](#run-collections)                   | `-rc` or `--run-collections`       | `PMM_COLLECTIONS`        |
| [Run Libraries](#run-libraries)                       | `-rl` or `--run-libraries`         | `PMM_LIBRARIES`          |
| [Run Metadata Files](#run-metadata-files)             | `-rm` or `--run-metadata-files`    | `PMM_METADATA_FILES`     |
| [Libraries First](#libraries-first)                   | `-lf` or `--libraries-first`       | `PMM_LIBRARIES_FIRST`    |
| [Ignore Schedules](#ignore-schedules)                 | `-is` or `--ignore-schedules`      | `PMM_IGNORE_SCHEDULES`   |
| [Ignore Ghost](#ignore-ghost)                         | `-ig` or `--ignore-ghost`          | `PMM_IGNORE_GHOST`       |
| [Cache Libraries](#cache-libraries)                   | `-ca` or `--cache-libraries`       | `PMM_CACHE_LIBRARIES`    |
| [Delete Collections](#delete-collections)             | `-dc` or `--delete-collections`    | `PMM_DELETE_COLLECTIONS` |
| [Resume Run](#resume-run)                             | `-re` or `--resume`                | `PMM_RESUME`             |
| [No Countdown](#no-countdown)                         | `-nc` or `--no-countdown`          | `PMM_NO_COUNTDOWN`       |
| [No Missing](#no-missing)                             | `-nm` or `--no-missing`            | `PMM_NO_MISSING`         |
| [Read Only Config](#read-only-config)                 | `-ro` or `--read-only-config`      | `PMM_READ_ONLY_CONFIG`   |
| [Divider Character](#divider-character--screen-width) | `-d` or `--divider`                | `PMM_DIVIDER`            |
| [Screen Width](#divider-character--screen-width)      | `-w` or `--width`                  | `PMM_WIDTH`              |

Further explanation and examples of each command can be found below.

## Run Command Attribute Examples

Environment variables are expressed as `KEY=VALUE`  Depending on the context where you are specifying them, you may enter those two things in two different fields, or some other way.  The examples below show how you would specify the environment variable in a script or a `docker run` command.  Things like Portainer or a NAS Docker UI will have different ways to specify these things.

### Config

Specify the location of the configuration YAML file.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --config <path_to_config>
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --config <path_to_config>
```

</details>

### Time to Run

Specify the time of day that Plex Meta Manager will run.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-t</code> or <code>--time</code></td>
    <td><code>PMM_TIME</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--time 06:00,18:00</code></td>
    <td><code>PMM_TIME=06:00,18:00</code></td>
  </tr>
  <tr>
    <th>Default Value</th>
    <td colspan="2"><code>03:00</code></td>
  </tr>
  <tr>
    <th>Available Values</th>
    <td colspan="2">comma-separated list in <code>HH:MM</code> format</td>
  </tr>
</table>

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --time 22:00,03:00
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --time 22:00,03:00
```

</details>

### Run

Perform a run immediately, bypassing the time to run flag.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --run
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run
```

</details>

### Run Tests

Run Plex Meta Manager in test/debug mode

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-rt</code>, <code>--tests</code>, or <code>--run-tests</code></td>
    <td><code>PMM_TEST</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run-tests</code></td>
    <td><code>PMM_TEST=true</code></td>
  </tr>
</table>

* Only collections with `test: true` enabled will be run

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --run-tests
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-tests
```

</details>

### Collections Only

Only run collection metadata/YAML files, skip library operations, overlays, and collections/metadata.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --collections-only
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --collections-only
```

</details>

### Playlists Only

Only run playlist metadata/YAML files, skip library operations, overlays, and collections/metadata.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --playlists-only
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --playlists-only
```

</details>

### Operations

Only run library operations skipping collections/metadata, playlists, and overlays.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-op</code> or <code>--operations</code></td>
    <td><code>PMM_OPERATIONS</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--operations</code></td>
    <td><code>PMM_OPERATIONS=true</code></td>
  </tr>
</table>

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --operations
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --operations
```

</details>

### Overlays

Only run library overlays skipping collections/metadata, playlists, and operations.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-ov</code> or <code>--overlays</code></td>
    <td><code>PMM_OVERLAYS</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--overlays</code></td>
    <td><code>PMM_OVERLAYS=true</code></td>
  </tr>
</table>

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --overlays
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --overlays
```

</details>

### Run Collections

Run only the pre-defined collections

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-rc</code> or <code>--run-collections</code></td>
    <td><code>PMM_COLLECTIONS</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run-collections "Harry Potter, Star Wars"</code></td>
    <td><code>PMM_COLLECTIONS=Harry Potter, Star Wars</code></td>
  </tr>
  <tr>
    <th>Values</th>
    <td colspan="2">Comma-separated list of Collection Names to run</td>
  </tr>
</table>

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --run-collections "Harry Potter, Star Wars"
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-collections "Harry Potter, Star Wars"
```

</details>

### Run Libraries

Run only the pre-defined libraries

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-rl</code> or <code>--run-libraries</code></td>
    <td><code>PMM_LIBRARIES</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run-libraries "Movies - 4K, TV Shows - 4K"</code></td>
    <td><code>PMM_LIBRARIES=Movies - 4K, TV Shows - 4K</code></td>
  </tr>
  <tr>
    <th>Values</th>
    <td colspan="2">Comma-separated list of Library Names to run</td>
  </tr>
</table>

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --run-libraries "TV Shows"
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-libraries "TV Shows"
```

</details>

### Run Metadata Files

Run only the pre-defined metadata files

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
    <th>Shell</th>
    <th>Environment</th>
  </tr>
  <tr>
    <th>Flags</th>
    <td><code>-rm</code> or <code>--run-metadata-files</code></td>
    <td><code>PMM_METADATA_FILES</code></td>
  </tr>
  <tr>
    <th>Example</th>
    <td><code>--run-metadata-files "Movies.yml, MovieCharts"</code></td>
    <td><code>PMM_METADATA_FILES=Movies.yml, MovieCharts</code></td>
  </tr>
  <tr>
    <th>Available Values</th>
    <td colspan="2">Comma-separated list of Metadata Filenames to run</td>
  </tr>
</table>

* This works for all different metadata paths i.e. `git`, `url`, `file`, or `repo`.
<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --run-metadata-files "Movies"
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --run-metadata-files "Movies"
```

</details>

### Libraries First

Run library operations prior to running collections.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --libraries-first
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --libraries-first
```

</details>

### Ignore Schedules

Ignore all schedules for the run.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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
<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --ignore-schedules
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --ignore-schedules
```

</details>

### Ignore Ghost

Ignore all ghost logging for the run. A ghost log is what's printed to the console to show progress during steps.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --ignore-ghost
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --ignore-ghost
```

</details>

### Cache Libraries

Cache the library Load for 1 day.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --cache-libraries
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --cache-libraries
```

</details>

### Delete Collections

Delete all collections in a Library prior to running collections/operations.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --delete-collections
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --delete-collections
```

</details>

### Resume Run
Resume a run from a specific collection use the `--resume` option.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --resume "Star Wars"
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --resume "Star Wars"
```

</details>

### No Countdown

Run without displaying a countdown to the next scheduled run.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --no-countdown
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-countdown
```

</details>

### No Missing

Run without utilizing the missing movie/show functions.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --no-missing
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --no-missing
```

</details>

### Read Only Config

Run without writing to the configuration file

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --read-only-config
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --read-only-config
```

</details>

### Divider Character & Screen Width

Change the terminal output divider character or width

#### Divider Character

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th style="background-color: #222;"></th>
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
    <th style="background-color: #222;"></th>
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

<details>
  <summary>Local Environment</summary>

```shell
python plex_meta_manager.py --divider * --width 200
```

</details>
<details>
  <summary>Docker Environment</summary>

```shell
docker run -it -v "X:\Media\Plex Meta Manager\config:/config:rw" meisnate12/plex-meta-manager --divider * --width 200
```

</details>
