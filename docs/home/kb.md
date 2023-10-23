# Frequently Asked Questions & Knowledgebase

This page aims to provide knowledge based on combined user experience, and to answer the frequent questions that we are asked in our [Discord Server](https://discord.gg/gYU8wATxKw).

## Frequently Asked Questions

This sections aims to answer the most commonly asked questions that users have.

#### PMM Versions & Updating

<details class="details-tabs">
  <summary>How do I update to the latest version of Plex Meta Manager?</summary>

````{tab} OS X/Linux
[type this into your terminal]
```
cd /Users/mroche/Plex-Meta-Manager
git pull
source pmm-venv/bin/activate
python -m pip install -r requirements.txt
```
````
````{tab} Windows
[type this into your terminal]
```
cd C:\Users\mroche\Plex-Meta-Manager
git pull
.\pmm-venv\Scripts\activate
python -m pip install -r requirements.txt
```
````
````{tab} Docker
[type this into your terminal]
```
docker pull meisnate12/plex-meta-manager
```
````
</details>

<details class="details-tabs">
  <summary>How do I switch to the develop branch?</summary>

````{tab} OS X/Linux
[type this into your terminal]
```
cd /Users/mroche/Plex-Meta-Manager
git checkout develop
git pull
source pmm-venv/bin/activate
python -m pip install -r requirements.txt
```
````
````{tab} Windows
[type this into your terminal]
```
cd C:\Users\mroche\Plex-Meta-Manager
git checkout develop
git pull
.\pmm-venv\Scripts\activate
python -m pip install -r requirements.txt
```
````
</details>

<details class="details-tabs">
  <summary>How do I switch to the nightly branch</summary>

````{tab} OS X/Linux
[type this into your terminal]
```
cd /Users/mroche/Plex-Meta-Manager
git checkout nightly
git pull
source pmm-venv/bin/activate
python -m pip install -r requirements.txt
```
````
````{tab} Windows
[type this into your terminal]
```
cd C:\Users\mroche\Plex-Meta-Manager
git checkout nightly
git pull
.\pmm-venv\Scripts\activate
python -m pip install -r requirements.txt
```
````
</details>

<details class="details-tabs">
  <summary>How do I switch back to the master branch?</summary>

````{tab} OS X/Linux
[type this into your terminal]
```
cd /Users/mroche/Plex-Meta-Manager
git checkout master
git pull
source pmm-venv/bin/activate
python -m pip install -r requirements.txt
```
````
````{tab} Windows
[type this into your terminal]
```
cd C:\Users\mroche\Plex-Meta-Manager
git checkout master
git pull
.\pmm-venv\Scripts\activate
python -m pip install -r requirements.txt
```
````
</details>

#### Performance & Scheduling

<details class="details-tabs">
  <summary>Any tips on increasing PMM performance?</summary>

Use PMM Caching where possible, this allows PMM to temporarily store commonly-used information so that it can be retreived more efficiently. There are multipe things that can be cached within PMM, see the link: https://metamanager.wiki/en/latest/search.html?q=cache&check_keywords=yes&area=default

Run PMM after PLEX Scheduled Tasks, as Plex's API tends to be slower at responding whilst it is performing the tasks. By default, PMM runs at 5AM to avoid the 3-5am window that Plex suggests for Scheduled Tasks.

For users who are more technically advanced and happy to risk manipulating the Plex database, considering altering the PRAGMA_CACHE settings within Plex: https://www.reddit.com/r/PleX/comments/ic3cjr/anyone_try_giving_sqlite3_more_cache_to_help/
- NOTE: you MUST use the version of sqlite3 tool that comes with your running version of PLEX or you will mess up your PLEX DB beyond repair. See this article on how to find the proper version for your setup: https://support.plex.tv/articles/repair-a-corrupted-database/

</details>

<details class="details-tabs">
  <summary>Why does my PMM run take so long to complete?</summary>

Every time an item (media, collection, overlay) needs to be updated, PMM needs to send the request to Plex, and then receive confirmation back from Plex that the action has been completed. This can take anywhere from seconds to minutes depending on when Plex provides a response. Given that the typical run can update hundreds or even thousands of items, this can quickly add up to a lot of time. If "Mass Update" operations are used, then every single item in the library needs to go through this process, which can be lengthy. 

Overlays can be particularly cumbersome as PMM needs to perform the following actions for each of the items that need to have an overlay applied:
- Check which overlays are applicable (this will take more time depending on how many overlays you are applying)
- Compare the current poster to confirm what overlays are already applied, if changes are needed then continue with the following steps
- Grab source image from Plex and save it to disk
- Draw each overlay image on top of the source image
- save final image to disk
- Tell Plex to apply new image to the item
- Wait for Plex to responsd confirming that the change has been made

The above two points can be greatly exasterbated if PMM has to update every episode within a Show library rather than just the Shows themselves, as there can often be hundreds of thousands of episodes to be updated with mass operations or overlays.

Additionally, some collections requires a lot of computing resource to determine the critera of the collections that are to be made. This is commonly seen in the Defaults files for Actor/Director/Producer/Writer which need to get the crew information for each of the movies/shows within your library, and then calculate which ones appear the most to find out which are the most popular. The larger your library, the longer this process will take.

</details>

<details class="details-tabs">
  <summary>Can I schedule library operations and/or overlays to happen at a different time than collections?</summary>

Yes, the recommended approach is to set up a new library for the Operations/Overlays, mapping it back to the original library, and then scheduling the library, as outlined below

```yaml
libraries:
  Movie Operations:           # NAME DOESN'T MATTER BUT MUST BE UNIQUE
    library_name: Movies      # THIS MUST MATCH A LIBRARY IN PLEX
    schedule: weekly(monday)
    operations:
      split_duplicates: true
    overlay_path:
      - pmm: resolution
```

</details>

#### Errors & Issues

<details class="details-tabs">
  <summary>Why doesn't PMM let me enter my authentication information for Trakt/MAL?</summary>

PMM needs to run in an interactive mode which allows the user to enter information (such as the Trakt/MAL PIN) as part of the authentication process. This can prove troublesome in some environments, particularly NAS.

Chazlarson has developed an online tool which will allow you to perform the authentication of both Trakt and MAL outside of PMM, and will then provide you the completed code block to paste into your config.yml.

The scripts can be found here. Click the green play button, wait a little bit, then follow the prompts. 
https://replit.com/@chazlarson/MALAuth
https://replit.com/@chazlarson/TraktAuth

</details>

<details class="details-tabs">
  <summary>Why am I seeing "(500) Internal Server Error" in my log files?</summary>

A 500 Internal Server Error happens when the server has an unexpected error when responding to an API request.

There could be any number of reasons why this happens and it depends on what server PMM is talking to although its most likely coming from your Plex Server.

Most of the time these errors need to be resolved by changing something specific to your set up but some do come up that can be fixed (i.e. Plex throws one if you upload a photo larger then 10 MB)

Many Appbox Setups will throw this error when too many requests are sent, or if the central metadata repository is not properly configured to allow users to upload custom posters.

Take a look at the following logs:
:one: Settings | Manage | Console -> then filter on Error and Warning to see what might be going on
:two: Check the plex logs (container or other) for the "Busy DB Sleeping for 200ms)

There is nothing that PMM or our support staff can really do to resolve a 500 error.

</details>

## Knowledgebase

This section aims to provide some guidance on the most common issues that we see.

### Locating Log Files

The meta.log file can be found within the `logs` folder of your Plex Meta Manager config folder [right next to `config.yml`].
`meta.log` is the most recent run of Plex Meta Manager, `meta.log.1` is the previous run, `meta.log.2` is the run before that, so on and so forth.

### Basic Log File Troubleshooting

Wondering how to troubleshoot Plex Meta Manager and how to read through the meta.log?

**Using a text editor like [Visual Studio Code](https://code.visualstudio.com/) or [Sublime Text](https://www.sublimetext.com/) is recommended**

In all cases, the first step is to open the [`meta.log`](#locating-log-files) with your text editor and perform these steps:

1. Check that you are running the latest [`version`](#checking-plex-meta-manager-version) of your branch. Your current version can be found in the `meta.log` file either below the Plex Meta Manager ASCII art, or at the end of the run. If you are not on the latest version of your branch, you will see `Newest Version: X.X.X` below this. Ensure you [`upgrade`](../home/guides/local.md#i-want-to-update-to-the-latest-version-of-pmm) to the latest version of Plex Meta Manager.
2. When scanning your meta.log file, search for `[CRITICAL]` items first as these will definitely need to be fixed
3. Scan your meta.log file for `[ERROR]` and make a note of the content of the full line to start your search below on how to resolve

### Checking Plex Meta Manager Version

Checking the version: You will find that in your [`meta.log`](#locating-log-files) around the 8th-10th line and will look something like this:

```
|                                 |
|     Version: 1.17.1-develop10   |
|=================================|
```

If you are not on the latest version of your branch, you will see Newest Version: X.X.X below this. Ensure you upgrade to the latest version of Plex Meta Manager.

```
|                                       |
|     Version: 1.17.1-develop10         |
|     Newest Version: 1.17.1-develop20  |
|=======================================|
```

### Understanding Log File Event Types

There are five main event types that you need to be aware of when understanding the log files, detailed below:

| Type         | Short Info            | Description                                                               | Recommendation                                                                                        |
|:-------------|:----------------------|:--------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------|
| `[INFO]`     | Information log       | Informational message that does not require much attention                | No action required                                                                                    |
| `[DEBUG]`    | Debug Log             | Debug log message that does not require much attention                    | No action required                                                                                    |
| `[WARNING]`  | Warning Log           | Warning message that may require your attention                           | Read the warning and determine if this is something you need to take action on or not                 |
| `[ERROR]`    | Error Log             | Error message that in MOST cases requires action on your part to resolve  | Read the error message, look for the message below and try recommendations                            |
| `[CRITICAL]` | Critical Log          | Critical messaage requiring you to fix it for PMM to run properly         | Read the critical message and take appropriate action. look for message below and try recommendations |


### Common Log File Messages

This section aims to explain some commonly seen event messages that are produced in the logs.

#### CRITICAL

This table details examples of the most commonly-seen `[CRITICAL]` events and what they mean for the user.

|     Type      | Short Info                                          | Description                                                                   | Recommendation                                                                                              |
|:-------------:|:----------------------------------------------------|:------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------|
| `[CRITICAL]`  | `Failed to Connect to https://api.themoviedb.org/3` | Current step PMM was on made an API call to TMDb, but it aborted and moved on | Determine if TMDb was offline and not replying to api requests. Try again and see if it fails again or not. |                                                                                                                                                                                                                                                  |

#### ERROR

This table details examples of the most commonly-seen `[ERROR]` events and what they mean for the user.

|    Type    | Short Info                                                        | Description                                                                      | Recommendation                                                                                                                                                                                                                                                                                                                                                                                                                               |
|:----------:|:------------------------------------------------------------------|:---------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `[ERROR]`  | `Playlist Error: Library: XYZ not defined`                        | Plex library XYZ is not found                                                    | Ensure that your config file has defined the proper library name as found in Plex                                                                                                                                                                                                                                                                                                                                                            |
| `[ERROR]`  | `Plex Error: resolution: No matches found with regex pattern XYZ` | While looking for a pattern in Plex, this one was not found                      | This may be normal and require 0 actions. However, if you expect that Plex should have returned records, check the pattern to ensure it is working properly                                                                                                                                                                                                                                                                                  |
| `[ERROR]`  | `Plex Error: No Items found in Plex`                              | While using the PMM builder, no items with that criteria were returned from Plex | This may be normal and require 0 actions. However, if you expect that Plex should have returned records, check the builder to ensure it is working properly                                                                                                                                                                                                                                                                                  |
| `[ERROR]`  | `IMDb Error: Failed to parse URL:`                                | While using the PMM builder, url does not exist                                  | This may be normal and require 0 actions. However, if you expect that the URL should have returned records, check the url in your browser to ensure it is working properly                                                                                                                                                                                                                                                                   |
| `[ERROR]`  | `Trakt Error: No TVDb ID found for Nightfall (2022)`              | Online sources are missing information                                           | These sorts of errors indicate that the thing can't be cross-referenced between sites. For example, at the time of that error, the Trakt record for "Nightfall (2022)" didn't contain a TVDb ID. This could be because the record just hasn't been updated, or because "Nightfall (2022)" is not listed on TVDb. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.                         |
| `[ERROR]`  | `MdbList Error: Not Found`                                        | Online sources are missing information                                           | These sorts of errors indicate that the thing can't be cross-referenced between sites. For example, at the time of that error, the the MDBlist record was trying to get a rating for a media item and could not find it.                                                                                                                                                                                                                     |
| `[ERROR]`  | `Plex Error: actor: Mel B not found`                              | Actor not found and hence unable to create the collection                        | Report error in #pmm-help channel and see if there is a fix.                                                                                                                                                                                                                                                                                                                                                                                 |
| `[ERROR]`  | `Input Failed`                                                    | A token or password is no longer valid for an online source of information       | Review the meta.log for more information                                                                                                                                                                                                                                                                                                                                                                                                     |
| `[ERROR]`  | `Collection Error: trakt_list requires Trakt to be configured`    | You are using a builder that has not been configured yet.                        | Review the meta.log for more information on what went wrong. Refer to the wiki for details on how to set this up (in this case Trakt)                                                                                                                                                                                                                                                                                                        |

#### WARNING

This table details examples of the most commonly-seen `[WARNING]` events and what they mean for the user.

|     Type     | Short Info                                                       | Description                            | Recommendation                                                                                                                                                                                                                                                                                                                                                                                                                              |
|:------------:|:-----------------------------------------------------------------|:---------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `[WARNING]`  | `Convert Error: No TVDb ID Found for TMDb ID: 15733`             | Online sources are missing information | These sorts of errors indicate that the thing can't be cross-referenced between sites. For example, at the time of that error, the TMDb record for "The Two Mrs. Grenvilles" [ID 15733] didn't contain a TVDb ID. This could be because the record just hasn't been updated, or because "The Two Mrs. Grenvilles" is not listed on TVDB. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data. |
| `[WARNING]`  | `Convert Error: AniDB ID not found for AniList ID: 21400`        | Online sources are missing information | These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.                                                                                                                                                                                                                                                  |
| `[WARNING]`  | `Convert Error: No TVDb ID or IMDb ID found for AniDB ID: 14719` | Online sources are missing information | These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.                                                                                                                                                                                                                                                  |
| `[WARNING]`  | `Convert Error: AniDB ID not found for MyAnimeList ID: 36838`    | Online sources are missing information | These sorts of errors indicate that the thing can't be cross-referenced between sites. The fix is for someone [like you, perhaps] to go to the relevant site and fill in the missing data.                                                                                                                                                                                                                                                  |

#### INFO

This table details examples of the most commonly-seen `[INFO]` events and what they mean for the user.

|   Type    | Short Info                                    | Description                           | Recommendation                                                                                                                |
|:---------:|:----------------------------------------------|:--------------------------------------|:------------------------------------------------------------------------------------------------------------------------------|
| `[INFO]`  | `Detail: TMDb_person updated poster to [URL]` | Person image was downloaded from TMDb | May require you to update the people poster image to your style or request it in the style of the PMM defaults people posters |
