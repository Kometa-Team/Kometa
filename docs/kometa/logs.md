---
search:
  boost: 4
hide:
   - toc
---
# Log files and where to find them

### Locating Log Files

The meta.log file can be found within the `logs` folder of your Kometa config folder [right next to `config.yml`].

`meta.log` is the most recent run of Kometa.

As new log files are created, the old ones get a numeric suffix added: `meta-1.log`. **The most recent is always the one without a number at the end.**

`meta-1.log` is the previous run, `meta-2.log` is the run before that, so on and so forth.

???+ info "Old Naming Convention"

    In an older release of Kometa, prevous run logs followed the naming pattern of `meta.log.1`, `meta.log.2` etc. These files can safely be renamed if you no longer require them.

### Providing Log Files on Discord

You can drag-and-drop your meta.log file directly into [Discord](https://kometa.wiki/en/latest/discord/), 
you do not need to upload it to a third-party site unless it exceeds the 50mb size limit.

Please DO NOT manually extract, copy and paste text from your log files directly into Discord as the formatting 
can be difficult to read and can often redact parts of the log file that are important for full context.

### Basic Log File Troubleshooting

Wondering how to troubleshoot Kometa and how to read through the meta.log?

**Using a text editor like [Visual Studio Code](https://code.visualstudio.com/) or [Sublime Text](https://www.sublimetext.com/) is recommended**

In all cases, the first step is to open the [`meta.log`](#locating-log-files) with your text editor and perform these steps:

1. Check that you are running the latest [`version`](#checking-kometa-version) of your branch. Your current version can be found in the `meta.log` file either below the 
   Kometa ASCII art, or at the end of the run. If you are not on the latest version of your branch, you will see `Newest Version: X.X.X` below this. 
   Ensure you [`upgrade`](install/walkthroughs/local.md#i-want-to-update-to-the-latest-version-of-the-current-kometa-branch) to the latest version of Kometa.
2. When scanning your meta.log file, search for `[CRITICAL]` items first as these will definitely need to be fixed
3. Scan your meta.log file for `[ERROR]` and make a note of the content of the full line to start your search below on how to resolve

### Checking Kometa Version

Checking the version: You will find that in your [`meta.log`](#locating-log-files) around the 8th-10th line and will look something like this:

```
|                                 |
|     Version: 1.19.1-develop10   |
|=================================|
```

If you are not on the latest version of your branch, you will see Newest Version: X.X.X below this. Ensure you upgrade to the latest version of Kometa.

```
|                                       |
|     Version: 1.19.1-develop10         |
|     Newest Version: 1.19.1-develop20  |
|=======================================|
```

### Understanding Log File Event Types

There are five main event types that you need to be aware of when understanding the log files, detailed below:

| Type       | Short Info      | Description                                                              | Recommendation                                                                                        |
|:-----------|:----------------|:-------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------|
| `INFO`     | Information log | Informational message that does not require much attention               | No action required                                                                                    |
| `DEBUG`    | Debug Log       | Debug log message that does not require much attention                   | No action required                                                                                    |
| `WARNING`  | Warning Log     | Warning message that may require your attention                          | Read the warning and determine if this is something you need to take action on or not                 |
| `ERROR`    | Error Log       | Error message that in MOST cases requires action on your part to resolve | Read the error message, look for the message below and try recommendations                            |
| `CRITICAL` | Critical Log    | Critical message requiring you to fix it for Kometa to run properly      | Read the critical message and take appropriate action. look for message below and try recommendations |

### Common Log File Messages

This section aims to explain some commonly seen event messages that are produced in the logs.

#### CRITICAL

This table details examples of the most commonly-seen `[CRITICAL]` events and what they mean for the user.

<table>
    <thead>
        <th>Type</th>
        <th>Short Info</th>
    </thead>
    <tr>
        <td><code>CRITICAL</code></td>
        <td><code>Failed to Connect to https://api.themoviedb.org/</code></td>
    </tr>
    <tr>
        <td colspan="2"><strong>Description:</strong> Current step Kometa was on made an API call to TMDb, but it aborted and moved on<br><strong>Recommendation:</strong> Determine if TMDb was offline and not replying to API requests. Try again and see if it fails again or not.</td>
    </tr>
</table>

#### ERROR

This table details examples of the most commonly-seen `[ERROR]` events and what they mean for the user.

<table>
    <thead>
        <th>Type</th>
        <th>Short Info</th>
    </thead>
	<tr>
		<td><code>ERROR</code></td>
		<td><code>Playlist Error: Library: XYZ not defined</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Plex library XYZ is not found<br><strong>Recommendation:</strong> Ensure that your config file has defined the proper library name as found in Plex</td>
	</tr>
	<tr>
		<td><code>ERROR</code></td>
		<td><code>Plex Error: resolution: No matches found with regex pattern XYZ</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> While looking for a pattern in Plex, this one was not found<br><strong>Recommendation:</strong> This may be normal and require 0 actions. However, if you expect that Plex should have returned records, check the pattern to ensure it is working properly</td>
	</tr>
	<tr>
		<td><code>ERROR</code></td>
		<td><code>Plex Error: No Items found in Plex</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> While using the Kometa Builder, no items with that criteria were returned from Plex<br><strong>Recommendation:</strong> This may be normal and require 0 actions. However, if you expect that Plex should have returned records, check the Builder to ensure it is working properly</td>
	</tr>
	<tr>
		<td><code>ERROR</code></td>
		<td><code>IMDb Error: Failed to parse URL:</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> While using the Kometa Builder, url does not exist<br><strong>Recommendation:</strong> This may be normal and require 0 actions. However, if you expect that the URL should have returned records, check the url in your browser to ensure it is working properly</td>
	</tr>
	<tr>
		<td><code>ERROR</code></td>
		<td><code>MDBList Error: No TVDb ID found for Nightfall (2022)</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Online sources are missing information<br><strong>Recommendation:</strong> These sorts of errors indicate that the thing can't be cross-referenced between sites.</br>For example, at the time of that error, the MDBList record for "Nightfall (2022)" didn't contain a TVDb ID.</br>This could be because the record just hasn't been updated, or because "Nightfall (2022)" is not listed on TVDb.</br>The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.</td>
	</tr>
	<tr>
		<td><code>ERROR</code></td>
		<td><code>MDBList Error: Not Found</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Online sources are missing information<br><strong>Recommendation:</strong> These sorts of errors indicate that the thing can't be cross-referenced between sites. For example, at the time of that error, the MDBList record was trying to get a rating for a media item and could not find it.</td>
	</tr>
	<tr>
		<td><code>ERROR</code></td>
		<td><code>Plex Error: actor: Mel B not found</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Actor not found and hence unable to create the collection<br><strong>Recommendation:</strong> Report error in #kometa-help channel and see if there is a fix.</td>
	</tr>
	<tr>
		<td><code>ERROR</code></td>
		<td><code>Input Failed</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> A token or password is no longer valid for an online source of information<br><strong>Recommendation:</strong> Review the meta.log for more information</td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> You are using a builder that has not been configured yet.<br><strong>Recommendation:</strong> Review the meta.log for more information on what went wrong. Refer to the wiki for details on how to set this up</td>
	</tr>
</table>

#### WARNING

This table details examples of the most commonly-seen `[WARNING]` events and what they mean for the user.

<table>
	<thead>
		<th>Type</th>
		<th>Short Info</th>
	</thead>
	<tr>
		<td><code>WARNING</code></td>
		<td><code>Convert Warning: No TVDb ID Found for TMDb ID: 15733</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Online sources are missing information<br><strong>Recommendation:</strong> These sorts of errors indicate that the thing can't be cross-referenced between sites. For example, at the time of that error, the TMDb record for "The Two Mrs. Grenvilles" [ID 15733] didn't contain a TVDb ID. This could be because the record just hasn't been updated, or because "The Two Mrs. Grenvilles" is not listed on TVDB. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.</td>
	</tr>
	<tr>
		<td><code>WARNING</code></td>
		<td><code>Convert Warning: AniDB ID not found for AniList ID: 21400</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Online sources are missing information<br><strong>Recommendation:</strong> These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.</td>
	</tr>
	<tr>
		<td><code>WARNING</code></td>
		<td><code>Convert Warning: No TVDb ID or IMDb ID found for AniDB ID: 14719</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Online sources are missing information<br><strong>Recommendation:</strong> These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.</td>
	</tr>
	<tr>
		<td><code>WARNING</code></td>
		<td><code>Convert Warning: AniDB ID not found for MyAnimeList ID: 36838</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Online sources are missing information<br><strong>Recommendation:</strong> These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.</td>
	</tr>
</table>
#### INFO

This table details examples of the most commonly-seen `[INFO]` events and what they mean for the user.

<table>
	<thead>
		<th>Type</th>
		<th>Short Info</th>
	</thead>
	<tr>
		<td><code>INFO</code></td>
		<td><code>Detail: TMDb_person updated poster to [URL]</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Person image was downloaded from TMDb<br><strong>Recommendation:</strong> May require you to update the people poster image to your style or request it in the style of the Kometa defaults people posters</td>
	</tr>
</table>

### Temporary Plex image upload errors

Kometa retries poster, background, logo, and square-art uploads when Plex returns HTTP 502, 503, or 504. It makes at most three upload attempts, waiting 2 seconds before the second attempt and 5 seconds before the third. If all three attempts receive these errors, Kometa logs the item, image, and final HTTP status, skips that image update, and continues the run without a traceback. This also applies to artwork resets, overlay application, and overlay removal. Failed overlay removal keeps the overlay label and original poster backup so removal can be retried. Retry messages identify the item and image.

A gateway error does not establish that the image is missing. URL uploads still make these three attempts even if the source URL is permanently broken; this can add 7 seconds for that image on each run. Failed uploads are not cached as successes. Source URL validation and fallback are separate from these Plex retries. Other errors retain their existing handling and diagnostic details.

### Other Troubleshooting Examples

The Log files will contain a great deal of detail about what exactly is happening and why. Generally speaking, if you're having a problem with Kometa the answer will be found here. 
These logs can of course be quite technical, but often the error can be relatively clear:

Something's missing from the format of the file:

```
| Loading Collection File: config/TV Shows.yml                                                       |
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
    mdblist_list: mdblist_list: https://mdblist.com/lists/stealthgyro/marvel-cinematic-universe-mcu
```

YAML doesn't allow duplicate keys:

```
| Loading Collection File: config/Anime.yml                                                          |
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
    mdblist_list: mdblist_list: https://mdblist.com/lists/stealthgyro/marvel-cinematic-universe-mcu
```

File is not where Kometa expects it:

```
| Loading Collection File: config/Movies.yml                                              |
| YAML Error: File Error: File does not exist /Users/Lucky/Kometa/config/Movies.yml       |
```

## Source integrity

Source integrity is checked alongside the startup system information, with a maximum wait of 30 seconds for both cached file checking and baseline retrieval. The log reports `Source Integrity: Verified`, `Source Integrity: MODIFIED`, or `Source Integrity: Check unavailable` with a reason and an explanation that local files were not verified. If the startup time limit is reached, Kometa continues with `Source Integrity: Check unavailable (startup time limit reached; local files were not verified)`. There is no later integrity result during library processing. The end-of-run `Source Integrity Summary (startup check)` repeats the startup result without waiting for or adopting a late result. A timeout in this summary describes the startup check, not a detected file change. Modified installations list changed, missing, and added files. An unavailable check means the comparison could not be completed; it does not indicate detected file changes. Only `MODIFIED` reports confirmed differences. This is a support diagnostic and never prevents Kometa from running.

The diagnostic is enabled by default. Use `--no-source-integrity` or set `KOMETA_SOURCE_INTEGRITY=false` to disable it, including file checks and network requests. Use `--source-integrity` or `KOMETA_SOURCE_INTEGRITY=true` to enable it. As with other runtime options, environment variables take precedence over CLI flags. Disabled checks report `Source Integrity: Disabled (source-integrity option)` in the startup header and end-of-run summary.

The baseline comes from official upstream source pinned to the installed commit. It is cached under `.source-integrity/` in the active config directory for subsequent offline checks. After a new cache is successfully saved, Kometa retains it and the two most recently written other caches for the same repository and installation profile. This limits storage growth while allowing installations at different commits to share a config directory without evicting each other on every update. Downloads use temporary disk files. Upstream retrieval has a separate 180-second deadline, so a slow download can continue after the 30-second startup wait. If the process remains running and retrieval completes within that deadline, the worker can silently save the baseline for a later run; it does not log another result or change the startup result repeated in the summary. Scheduled starts for the same installation, config directory, and profile reuse an active check rather than launching another download. Each start still has its own 30-second wait and saved startup result. The worker is a daemon: if Kometa exits before retrieval completes, no baseline is saved and the next run retries.

Runtime config, logs, virtual environments, compiled Python files, desktop metadata, and integrity metadata are excluded. Differences consisting only of Windows versus Unix line endings are tolerated in known text files; binary files require exact bytes. Docker checks Kometa-owned files and directories rather than the container operating system. Repository-only CI/test files excluded from upstream source archives are outside the comparison.

Git installs use the installation's HEAD; Docker builds carry `KOMETA_GIT_SHA` when provided; `.kometa_sha` is an identity hint when present. The candidate commit must belong to an official upstream branch before a baseline is cached. PR and test images whose commits are outside official upstream history report Check unavailable. Older images or installations without exact commit metadata also report Check unavailable; recreate the container with an image containing that metadata. Cache corruption, unavailable upstream data, and inspection errors report Check unavailable. The diagnostic cannot protect against deliberate replacement of its own implementation or provenance metadata.
