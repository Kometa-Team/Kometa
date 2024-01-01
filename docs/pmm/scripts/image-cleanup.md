# Plex Image Cleanup

Your Plex folders are growing out of control. You use overlays from [Plex Meta Manager](https://github.com/meisnate12/Plex-Meta-Manager) (PMM) or upload lots of custom art from [Title Card Maker](https://github.com/CollinHeist/TitleCardMaker) (TCM) that you no longer want to use or need to eliminate. You don't want to perform the [plex dance](https://www.plexopedia.com/plex-media-server/general/plex-dance/) if you can avoid it. This script will free up gigs of space....

As well as being able to clean the PhotoTranscoder Directory and running the Plex operations Empty Trash, Clean Bundles, and Optimize DB. 

Special Thanks to [bullmoose20](https://github.com/bullmoose20) for the original [Plex Bloat Fix](https://github.com/bullmoose20/Plex-Stuff#plex-bloat-fix) (PBF) Script this is based on.

![](images/cleanup.png)

This image shows which photos would be removed. Red is removed, Green is kept because it is the actively selected poster. The other two come standard from Plex when the posters are retrieved so Plex Meta Manager will not touch those either:

## Installing Plex Image Cleanup

Generally, Plex Image Cleanup can be installed in one of two ways:

1. Running on a system as a Python script [we will refer to this as a "local" install]
2. Running as a Docker container

GENERALLY SPEAKING, running as a Docker container is simpler, as you won't have to be concerned about installing Python, or support libraries, or any possible system conflicts generated by those actions.

For this reason, it's generally recommended that you install via Docker rather than directly on the host.

If you have some specific reason to avoid Docker, or you prefer running it as a Python script for some particular reason, then this general recommendation is not aimed at you.  It's aimed at someone who doesn't have an existing compelling reason to choose one over the other.

### Install Walkthroughs

There are no detailed walkthroughs specifically for Plex Image Cleanup but the process is extremely similar to how you would do it with [Plex Meta Manager](https://metamanager.wiki/en/latest/pmm/installation/#install-walkthroughs).

### Local Install Overview

Plex Image Cleanup is compatible with Python 3.11. Later versions may function but are untested.

These are high-level steps which assume the user has knowledge of python and pip, and the general ability to troubleshoot issues. 

1. Clone or [download and unzip](https://github.com/meisnate12/Plex-Image-Cleanup/archive/refs/heads/master.zip) the repo.

```shell
git clone https://github.com/meisnate12/Plex-Image-Cleanup
```
2. Install dependencies:

```shell
pip install -r requirements.txt
```

3. If the above command fails, run the following command:

```shell
pip install -r requirements.txt --ignore-installed
```

At this point Plex-Image-Cleanup has been installed, and you can verify installation by running:

```shell
python plex_image_cleanup.py
```

### Docker Install Overview

#### Docker Run:

```shell
docker run -v <PATH_TO_CONFIG>:/config:rw -v <PATH_TO_PLEX>:/plex:rw meisnate12/plex-image-cleanup
```
* The `-v <PATH_TO_CONFIG>:/config:rw` and `-v <PATH_TO_PLEX>:/plex:rw` flags mount the location you choose as a persistent volumes to store your files and give access to plex.
  * Change `<PATH_TO_CONFIG>` to a folder where your .env and other files are.
  * Change `<PATH_TO_PLEX>` to the folder where your Plex Folder is (It contains folders: Cache, Metadata, Plug-in Support).
  * If your directory has spaces (such as "My Documents"), place quotation marks around your directory pathing as shown here: `-v "<PATH_TO_CONFIG>:/config:rw"`

Example Docker Run command:

These docs are assuming you have a basic understanding of Docker concepts.  One place to get familiar with Docker would be the [official tutorial](https://www.docker.com/101-tutorial/).

```shell
docker run -v "X:\Media\Plex Image Cleanup\config:/config:rw" -v "X:\Plex Media Server:/plex:rw" meisnate12/plex-image-cleanup
```

#### Docker Compose:

Example Docker Compose file:
```yaml
version: "2.1"
services:
  plex-image-cleanup:
    image: meisnate12/plex-image-cleanup
    container_name: plex-image-cleanup
    environment:
      - TZ=TIMEZONE #optional
    volumes:
      - /path/to/config:/config
      - /path/to/plex:/plex
    restart: unless-stopped
```

#### Dockerfile

A `Dockerfile` is included within the GitHub repository for those who require it, although this is only suggested for those with knowledge of dockerfiles. The official Plex Image Cleanup build is available on the [Dockerhub Website](https://hub.docker.com/r/meisnate12/plex-image-cleanup).

## Usage

When running Plex Image Cleanup, make sure that you are not running any tools which may touch posters, backgrounds or title card images - namely [Plex Meta Manager](https://github.com/meisnate12/Plex-Meta-Manager) or [TitleCardMaker](https://github.com/CollinHeist/TitleCardMaker).

It is recommended to schedule Plex Image Cleanup after the above tools or Plex's Scheduled Tasks.

An example schedule would be:
* 00:00-02:00 - TitleCardMaker
* 02:00-05:00 - Plex Scheduled Tasks
* 05:00-07:00 - Plex Meta Manager
* 07:00-09:00 - Plex Image Cleanup

### Tips

* Ensure you have proper permissions to delete/rename or Plex Meta Manager will fail
* For performance purposes, it's recommended to run locally so that accessing the files is not done over a network share

## Global Options

Plex Image Cleanup has multiple Global Options to change how it runs these are set in 3 different ways listed in priority order:

1. Setting the Environment Variable.
2. Adding the Environment Variables to `config/.env` 
   * `example.env` is included as an example but is not read by Plex Meta Manager it will only read a file specifically called `.env`.
3. Use the Shell Command when launching.

### Example .env File
```
PLEX_PATH=C:\Plex Media Server
MODE=report
SCHEDULE=
PLEX_URL=http://192.168.1.12:32400
PLEX_TOKEN=123456789
DISCORD=https://discord.com/api/webhooks/###################/####################################################################
TIMEOUT=600
SLEEP=60
IGNORE_RUNNING=False
LOCAL_DB=False
USE_EXISTING=False
PHOTO_TRANSCODER=False
EMPTY_TRASH=False
CLEAN_BUNDLES=False
OPTIMIZE_DB=False
TRACE=False
LOG_REQUESTS=False
```

### Base Options

#### Plex Path

The only required Option is the `Plex Path` Option which is the Plex Config Folder containing the servers Metadata including `Cache`, `Metadata`, and `Plug-in Support`.

To set the `Plex Path` for the run: 
* **Environment Variable:** `PLEX_PATH=C:\Plex Media Server`
* **Shell Command:** `-p "C:\Plex Media Server"` or `--plex "C:\Plex Media Server"`
* Will also check `/plex` relative to the base directory of the script if neither of the above are specified.

#### Mode

How Plex Image Cleanup runs depends on the `Mode` Option that's currently set for that run.

* `report`: Metadata Directory File changes will be reported but not performed.
* `move`: Metadata Directory Files will be moved to the PIC Restore Directory. (CAN BE RESTORED)
* `restore`: Restores the Metadata Directory Files from the PIC Restore Directory.
* `clear`: Clears out the PIC Restore Directory. (CANNOT BE RESTORED)
* `remove`: Metadata Directory Files will be removed. (CANNOT BE RESTORED)
* `nothing`: Metadata Directory Files will not even be looked at.

To set the Global `Mode` for the run: 
* **Environment Variable:** `MODE=remove`
* **Shell Command:** `-m remove` or `--mode remove`

### Database

The script needs to query the server's plex database to make sure it doesn't remove actively selected images. 

#### Download From Plex API

By default, the script will expect to connect to your Plex Server to download the Database using your `Plex URL` and `Plex Token` Options ([Finding a Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)).

* **Environment Variables:** 
  * `PLEX_URL=http://192.168.1.12:32400`
  * `PLEX_TOKEN=123456789`
* **Shell Commands:** 
  * `-u "http://192.168.1.12:32400"` or `--url "http://192.168.1.12:32400"`
  * `-t "123456789"` or `--token "123456789"`

#### Copy From Local

Alternatively the database can be copied from your local config folder you supplied in the [`Plex Path`](#plex-path) Option by using the `Local DB` Option. 

* **Environment Variable:** `LOCAL_DB=True`
* **Shell Command:** `-l` or `--local`

**IMPORTANT! When Copying the Local Database, it is recommended to restart Plex before running this script and to make sure Plex is idle.**

Restarting allows for all temp SQLite files to be written to the primary Plex DB ensuring that all currently selected posters are properly known and preserved.

The script will not run when the temp SQLite files are found. To ignore this error, use the `Ignore Running` Option.

* **Environment Variable:** `IGNORE_RUNNING=True` 
* **Shell Command:** `-i` or `--ignore`

#### Use Existing

A previously downloaded or copied database can be used if it's less than 2 hours old by using the `Use Existing` Option. If the database is more than 2 hours old a new one will be downloaded or copied.

* **Environment Variable:** `USE_EXISTING=True`
* **Shell Command:** `-e` or `--existing`

### Other Operations

In addition to cleaning the Plex Metadata Directory for custom images the script can clean out your PhotoTranscoder Directory, Empty Trash, Clean Bundles, and Optimize DB.

#### Photo Transcoder

* **Environment Variable:** `PHOTO_TRANSCODER=True`
* **Shell Command:** `-pt` or `--photo-transcoder`

#### Empty Trash

* **Environment Variable:** `EMPTY_TRASH=True`
* **Shell Command:** `-et` or `--empty-trash`

#### Clean Bundles

* **Environment Variable:** `CLEAN_BUNDLES=True`
* **Shell Command:** `-cb` or `--clean-bundles`

#### Optimize DB

* **Environment Variable:** `OPTIMIZE_DB=True`
* **Shell Command:** `-od` or `--optimize-db`

### Other Options

#### Discord URL

Discord Webhook URL to send notifications to.

* **Environment Variable:** `DISCORD=https://discord.com/api/webhooks/###/###`
* **Shell Command:** `-d "https://discord.com/api/webhooks/###/###"` or `--discord "https://discord.com/api/webhooks/###/###"`

#### Timeout

Connection Timeout in seconds that's greater than 0.

* **Default:** `600`
* **Environment Variable:** `TIMEOUT=1000`
* **Shell Command:** `-ti 1000` or `--timeout 1000`

#### Sleep

Sleep Timer between Empty Trash, Clean Bundles, and Optimize DB in seconds that's greater than 0 .

* **Default:** `60`
* **Environment Variable:** `SLEEP=100`
* **Shell Command:** `-s 100` or `--sleep 100`

#### Trace

Run with extra trace logs.

* **Environment Variable:** `TRACE=True`
* **Shell Command:** `-tr` or `--trace`

#### Log Requests

Run with every request and file action logged.

* **Environment Variable:** `LOG_REQUESTS=True`
* **Shell Command:** `-lr` or `--log-requests`

### Continuous Schedule

Plex Image Cleanup can be run either immediately or on a schedule. The default behavior is to run immediately to run using a schedule simply pass in the `Schedule` Option.

Add a Schedule Block to the `Schedule` Option to run Plex Image Cleanup using a continuous schedule.

* **Shell Command:** `-sc` or `--schedule "05:00|weekly(sunday)"`
* **Environment Variable:** `SCHEDULE="05:00|weekly(sunday)"`

### Schedule Blocks

Schedule Blocks define how and when Plex Meta Manager will run.

Each Schedule Blocks has 2 required parts (`time` and `frequency`) and 1 optional part (`options`) all separated with a `|`. (Example: `time|frequency` or `time|frequency|options`)

You can have multiple Schedule Blocks separated with a `,` (`time|frequency,time|frequency|options`).

#### Schedule Block Parts

* `time`: Time in the day the run will occur.
  * **Time:** `HH:MM` 24-hour format
  * **Examples:** `00:00`-`23:59` 
* `frequency`: Frequency to schedule the run. 
  * **Frequencies:** `daily`, `weekly(day of week)`, or `monthly(day of month)`
  * **Examples:** `weekly(sunday)` or `monthly(1)`
* `options`: Options changed for the run in the format `option=value`, with multiple options separated with a `;`. 
  * **Options:** `mode`, `photo-transcoder`, `empty-trash`, `clean-bundles`, or `optimize-db`
  * **Examples:** `mode=nothing` or `photo-transcoder=true`
  * **Note: This overrides the currently set global value for just this one scheduled run**

### Schedule Block Example

```
SCHEDULE=08:00|weekly(sunday)|mode=clear,09:00|weekly(sunday)|mode=move,10:00|monthly(1)|mode=nothing;photo-transcoder=true
```

The example above is detailed out below to better explain how it works:

* Run at 8:00 AM on Sundays with the Options: `mode: clear`
  * `08:00|weekly(sunday)|mode=remove`
  * `time |frequency     |options`
* Run at 9:00 AM on Sundays with the Options: `mode: move`
  * `09:00|weekly(sunday)|mode=move`
  * `time |frequency     |options`
* Run at 10:00 AM on the 1st of each month with the Options: `mode: nothing` and `photo-transcoder: true` 
  * `10:00|monthly(1)|mode=nothing;photo-transcoder=true`
  * `time |frequency |options`