---
search:
  boost: 4
---
# Log files and where to find them

### Locating Log Files

The meta.log file can be found within the `logs` folder of your Plex Meta Manager config folder [right next to `config.yml`].

`meta.log` is the most recent run of Plex Meta Manager, `meta.log.1` is the previous run, `meta.log.2` is the run before that, so on and so forth.

As new log files are created, the old ones get a numeric suffix added: `meta.log.1`. **The most recent is always the one without a number at the end.**

### Providing Log Files on Discord

You can drag-and-drop your meta.log file directly into [Discord](https://metamanager.wiki/en/latest/discord/), you do not need to upload it to a third-party site unless it exceeds the 50mb size limit.

Please DO NOT manually extract, copy and paste text from your log files directly into Discord as the formatting can be difficult to read and can often redact parts of the log file that are important for full context.

### Basic Log File Troubleshooting

Wondering how to troubleshoot Plex Meta Manager and how to read through the meta.log?

**Using a text editor like [Visual Studio Code](https://code.visualstudio.com/) or [Sublime Text](https://www.sublimetext.com/) is recommended**

In all cases, the first step is to open the [`meta.log`](#locating-log-files) with your text editor and perform these steps:

1. Check that you are running the latest [`version`](#checking-plex-meta-manager-version) of your branch. Your current version can be found in the `meta.log` file either below the Plex Meta Manager ASCII art, or at the end of the run. If you are not on the latest version of your branch, you will see `Newest Version: X.X.X` below this. Ensure you [`upgrade`](install/local.md#i-want-to-update-to-the-latest-version-of-pmm) to the latest version of Plex Meta Manager.
2. When scanning your meta.log file, search for `[CRITICAL]` items first as these will definitely need to be fixed
3. Scan your meta.log file for `[ERROR]` and make a note of the content of the full line to start your search below on how to resolve

### Checking Plex Meta Manager Version

Checking the version: You will find that in your [`meta.log`](#locating-log-files) around the 8th-10th line and will look something like this:

```
|                                 |
|     Version: 1.19.1-develop10   |
|=================================|
```

If you are not on the latest version of your branch, you will see Newest Version: X.X.X below this. Ensure you upgrade to the latest version of Plex Meta Manager.

```
|                                       |
|     Version: 1.19.1-develop10         |
|     Newest Version: 1.19.1-develop20  |
|=======================================|
```

### Understanding Log File Event Types

There are five main event types that you need to be aware of when understanding the log files, detailed below:

| Type       | Short Info            | Description                                                              | Recommendation                                                                                        |
|:-----------|:----------------------|:-------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------|
| `INFO`     | Information log       | Informational message that does not require much attention               | No action required                                                                                    |
| `DEBUG`    | Debug Log             | Debug log message that does not require much attention                   | No action required                                                                                    |
| `WARNING`  | Warning Log           | Warning message that may require your attention                          | Read the warning and determine if this is something you need to take action on or not                 |
| `ERROR`    | Error Log             | Error message that in MOST cases requires action on your part to resolve | Read the error message, look for the message below and try recommendations                            |
| `CRITICAL` | Critical Log          | Critical message requiring you to fix it for PMM to run properly         | Read the critical message and take appropriate action. look for message below and try recommendations |

### Common Log File Messages

This section aims to explain some commonly seen event messages that are produced in the logs.

#### CRITICAL

This table details examples of the most commonly-seen `[CRITICAL]` events and what they mean for the user.

| Type       | Short Info                                          | Description                                                                   | Recommendation                                                                                              |
|:-----------|:----------------------------------------------------|:------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------|
| `CRITICAL` | `Failed to Connect to https://api.themoviedb.org/3` | Current step PMM was on made an API call to TMDb, but it aborted and moved on | Determine if TMDb was offline and not replying to api requests. Try again and see if it fails again or not. |

#### ERROR

This table details examples of the most commonly-seen `[ERROR]` events and what they mean for the user.

| Type    | Short Info                                                        | Description                                                                      | Recommendation                                                                                                                                                                                                                                                                                                                                                                                                                   |
|:--------|:------------------------------------------------------------------|:---------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ERROR` | `Playlist Error: Library: XYZ not defined`                        | Plex library XYZ is not found                                                    | Ensure that your config file has defined the proper library name as found in Plex                                                                                                                                                                                                                                                                                                                                                |
| `ERROR` | `Plex Error: resolution: No matches found with regex pattern XYZ` | While looking for a pattern in Plex, this one was not found                      | This may be normal and require 0 actions. However, if you expect that Plex should have returned records, check the pattern to ensure it is working properly                                                                                                                                                                                                                                                                      |
| `ERROR` | `Plex Error: No Items found in Plex`                              | While using the PMM builder, no items with that criteria were returned from Plex | This may be normal and require 0 actions. However, if you expect that Plex should have returned records, check the builder to ensure it is working properly                                                                                                                                                                                                                                                                      |
| `ERROR` | `IMDb Error: Failed to parse URL:`                                | While using the PMM builder, url does not exist                                  | This may be normal and require 0 actions. However, if you expect that the URL should have returned records, check the url in your browser to ensure it is working properly                                                                                                                                                                                                                                                       |
| `ERROR` | `Trakt Error: No TVDb ID found for Nightfall (2022)`              | Online sources are missing information                                           | These sorts of errors indicate that the thing can't be cross-referenced between sites.</br>For example, at the time of that error, the Trakt record for "Nightfall (2022)" didn't contain a TVDb ID.</br>This could be because the record just hasn't been updated, or because "Nightfall (2022)" is not listed on TVDb.</br>The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data. |
| `ERROR` | `MdbList Error: Not Found`                                        | Online sources are missing information                                           | These sorts of errors indicate that the thing can't be cross-referenced between sites. For example, at the time of that error, the MDBlist record was trying to get a rating for a media item and could not find it.                                                                                                                                                                                                            |
| `ERROR` | `Plex Error: actor: Mel B not found`                              | Actor not found and hence unable to create the collection                        | Report error in #pmm-help channel and see if there is a fix.                                                                                                                                                                                                                                                                                                                                                                     |
| `ERROR` | `Input Failed`                                                    | A token or password is no longer valid for an online source of information       | Review the meta.log for more information                                                                                                                                                                                                                                                                                                                                                                                         |
| `ERROR` | `Collection Error: trakt_list requires Trakt to be configured`    | You are using a builder that has not been configured yet.                        | Review the meta.log for more information on what went wrong. Refer to the wiki for details on how to set this up (in this case Trakt)                                                                                                                                                                                                                                                                                            |

#### WARNING

This table details examples of the most commonly-seen `[WARNING]` events and what they mean for the user.

| Type      | Short Info                                                       | Description                              | Recommendation                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|:----------|:-----------------------------------------------------------------|:-----------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `WARNING` | `Convert Warning: No TVDb ID Found for TMDb ID: 15733`             | Online sources are missing information   | These sorts of errors indicate that the thing can't be cross-referenced between sites.</br>For example, at the time of that error, the TMDb record for "The Two Mrs. Grenvilles" [ID 15733] didn't contain a TVDb ID.</br>This could be because the record just hasn't been updated, or because "The Two Mrs. Grenvilles" is not listed on TVDB.</br>The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data. |
| `WARNING` | `Convert Warning: AniDB ID not found for AniList ID: 21400`        | Online sources are missing information   | These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.                                                                                                                                                                                                                                                               |
| `WARNING` | `Convert Warning: No TVDb ID or IMDb ID found for AniDB ID: 14719` | Online sources are missing information   | These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.                                                                                                                                                                                                                                                               |
| `WARNING` | `Convert Warning: AniDB ID not found for MyAnimeList ID: 36838`    | Online sources are missing information   | These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.                                                                                                                                                                                                                                                               |

#### INFO

This table details examples of the most commonly-seen `[INFO]` events and what they mean for the user.

| Type   | Short Info                                    | Description                           | Recommendation                                                                                                                |
|:-------|:----------------------------------------------|:--------------------------------------|:------------------------------------------------------------------------------------------------------------------------------|
| `INFO` | `Detail: TMDb_person updated poster to [URL]` | Person image was downloaded from TMDb | May require you to update the people poster image to your style or request it in the style of the PMM defaults people posters |

### Other Troubleshooting Examples

The Log files will contain a great deal of detail about what exactly is happening and why.  Generally speaking, if you're having a problem with PMM the answer will be found here.  These logs can of course be quite technical, but often the error can be relatively clear:

Something's missing from the format of the file:

```
| Loading Collection File: config/TV Shows.yml                                                         |
|                                                                                                    |
| YAML Error: metadata, collections, or dynamic_collections attribute is required                    |
```

The problem in that case was:

```yaml
templates:
  Collection:
    cache_builders: 30
    sync_mode: sync
    sort_title: ZZZ-<<source>>-<<collection_name>>

collections:   <<< THIS LINE WAS MISSING
  Cached for 30 Days:
    template: {name: Collection, source: Looper}
    summary: ""
    trakt_list:
      - https://trakt.tv/users/kesleyalfa/lists/year-2011
```

YAML doesn't allow duplicate keys:

```
| Loading Collection File: config/Anime.yml                                                            |
|                                                                                                    |
| YAML Error: while constructing a mapping
|   in "<unicode string>", line 27, column 5:
|         mal_favorite: 50
|         ^ (line: 27)
| found duplicate key "collection_order" with value "custom" (original value: "custom")
|   in "<unicode string>", line 32, column 5:
|         collection_order: custom
|         ^ (line: 32)
```

The problem there was something like this:

```yaml
templates:
  Collection:
    cache_builders: 30
    sync_mode: sync
    sort_title: ZZZ-<<source>>-<<collection_name>>

collections:   <<< THIS LINE WAS MISSING
  Cached for 30 Days:
    template: {name: Collection, source: Looper}
    collection_order: custom                         <<<<  THIS KEY
    summary: ""
    collection_order: custom                         <<<<  DUPLICATED HERE
    trakt_list:
      - https://trakt.tv/users/kesleyalfa/lists/year-2011
```

File is not where PMM expects it:

```
| Loading Collection File: config/Movies.yml                                                           |
| YAML Error: File Error: File does not exist /Users/Lucky/Plex-Meta-Manager/config/Movies.yml       |
```
