---
search:
  boost: 4
hide:
   - toc
---
# Log files and where to find them

### Locating Log Files

The meta.log file can be found within the `logs` folder of your Kometa config folder [right next to `config.yml`].

`meta.log` is the most recent run of Kometa, `meta.log.1` is the previous run, `meta.log.2` is the run before that, so on and so forth.

As new log files are created, the old ones get a numeric suffix added: `meta.log.1`. **The most recent is always the one without a number at the end.**

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
		<td><code>Trakt Error: No TVDb ID found for Nightfall (2022)</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> Online sources are missing information<br><strong>Recommendation:</strong> These sorts of errors indicate that the thing can't be cross-referenced between sites.</br>For example, at the time of that error, the Trakt record for "Nightfall (2022)" didn't contain a TVDb ID.</br>This could be because the record just hasn't been updated, or because "Nightfall (2022)" is not listed on TVDb.</br>The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.</td>
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
		<td><code>ERROR</code></td>
		<td><code>Collection Error: trakt_list requires Trakt to be configured</code></td>
	</tr>
	<tr>
		<td colspan="2"><strong>Description:</strong> You are using a builder that has not been configured yet.<br><strong>Recommendation:</strong> Review the meta.log for more information on what went wrong. Refer to the wiki for details on how to set this up (in this case Trakt)</td>
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
    trakt_list:
      - https://trakt.tv/users/kesleyalfa/lists/year-2011
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
    trakt_list:
      - https://trakt.tv/users/kesleyalfa/lists/year-2011
```

File is not where Kometa expects it:

```
| Loading Collection File: config/Movies.yml                                              |
| YAML Error: File Error: File does not exist /Users/Lucky/Kometa/config/Movies.yml       |
```
