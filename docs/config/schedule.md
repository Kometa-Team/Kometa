---
search:
  boost: 2
hide:
  - toc
---
# Scheduling Parts of Kometa

Kometa allows you to schedule libraries, files, overlays, operations, and more so that runs can be tailored to suit your needs.

This is particularly handy for users who have a lot of libraries or run a lot of Metadata/Operations on their libraries.

### IMPORTANT:

These schedules do not trigger Kometa to run; they control what Kometa will do if it happens to be running at the scheduled time. `weekly(sunday)`, 
for example, does not mean "run Kometa on Sunday to do this thing"; it means "If Kometa is running, and it's Sunday, do this thing".

If you want to control when Kometa itself runs, like if you want Kometa to only run on Tuesdays and Thursdays, see [this page](../kometa/guides/scheduling.md).

The scheduling options are:

| Name         | Description                                                                                                          | Format                                             | Example                                                              |
|:-------------|:---------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------|:---------------------------------------------------------------------|
| Hourly       | Update only when the script is run in that hour or hour range.                                                       | hourly(Hour of Day)<br>hourly(Start Hour-End Hour) | `hourly(17)`<br>`hourly(17-04)`                                      |
| Daily        | Update once a day.                                                                                                   | daily                                              | `daily`                                                              |
| Weekly       | Update once a week on the specified days. (For multiple days, use a bar-separated (<code>&#124;</code>) list)        | weekly(Days of Week)                               | `weekly(sunday)`<br><code>weekly(sunday&#124;tuesday)</code>         |
| Monthly      | Update once a month on the specified day. (multiple days not supported as a parameter)                               | monthly(Day of Month)                              | `monthly(1)`                                                         |
| Yearly       | Update once a year on the specified day. (multiple days not supported as a parameter)                                | yearly(MM/DD)                                      | `yearly(01/30)`                                                      |
| Date         | Update on a specific date.                                                                                           | date(MM/DD/YYYY)                                   |                                                                      |
| Range        | Updates whenever the date is within the range. (For multiple ranges, use a bar-separated (<code>&#124;</code>) list) | range(MM/DD-MM/DD)                                 | `range(12/01-12/31)`<br><code>range(8/01-8/15&#124;9/01-9/15)</code> |
| Never        | Never updates.                                                                                                       | never                                              | `never`                                                              |
| Non Existing | Updates if it doesn't exist.                                                                                         | non_existing                                       | `non_existing`                                                       |
| All          | Requires that all comma separated scheduling options inside its brackets be meet in order to run.                    | all[Options]                                       | `all[weekly(sunday), hourly(17)]`                                    |

* `daily` is the default when `schedule` is not specified.
* You can run Kometa multiple times per day but using the `--time` command line argument detailed on the [Run Commands & Environmental Variables Page](../kometa/environmental.md).
* You can have multiple scheduling options as a list.
* You can use the `delete_not_scheduled` setting to delete Collections that are skipped due to not being scheduled.

## Examples

??? blank "Scheduling a Library<a class="headerlink" href="#schedule-library" title="Permanent link">¶</a>"
    
    <div id="schedule-library" />Uses the `schedule` [Library Attribute](libraries.md#attributes) to set when a library will be run.

    Other schedule rules for files, overlays, collections, and any other attribute that can be scheduled must also be met.

    Press the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml title="Library Scheduled to Run on Sunday"
    libraries:
      Movies:
        schedule: weekly(sunday) #(1)!
        collection_files:
          - file: config/Movies.yml
          - default: imdb
          - default: studio
          - default: genre
          - default: actor
        operations:
          mass_critic_rating_update: tmdb
    ```
    
    1. If you run Kometa on any day apart from Sunday,\n this library will not be processed at all

??? blank "Scheduling Collection, Playlist, and Metadata Files<a class="headerlink" href="#schedule-files" title="Permanent link">¶</a>"
    
    <div id="schedule-files" />Uses the `schedule` [Block Attribute](files.md#other-block-attributes) to set when a file will be run.

    Other schedule rules for collections and any other attribute that can be scheduled must also be met.

    Collection Files, Playlist Files, and Metadata Files can all be individually scheduled.
    
    ```yaml title="Files Scheduled for Different Days"
    libraries:
      Movies:
        collection_files:
          - file: config/Movies.yml
            schedule: weekly(monday)
          - default: imdb
            schedule: weekly(tuesday)
          - folder: config/Movies/
            schedule: weekly(wednesday)
          - default: genre
            schedule: weekly(thursday)
          - default: actor
            schedule: weekly(friday)
        metadata_files:
          - file: config/metadata.yml
            schedule: weekly(saturday)
    playlist_files:
      - file: config/Playlists.yml
        schedule: weekly(sunday)
    ```

??? blank "Scheduling Overlays<a class="headerlink" href="#schedule-overlays" title="Permanent link">¶</a>"
    
    <div id="schedule-overlays" />Uses the `schedule_overlays` [Library Attribute](libraries.md#attributes) to set when overlays will run for a library.

    ???+ danger "Scheduling Overlay Warning"

        Overlay Files cannot be individually Scheduled, all Overlay Files **MUST** be scheduled for the same period.

    Press the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml title="Overlays Scheduled for Saturday"
    libraries:
      Movies:
        schedule_overlays: weekly(saturday) #(1)!
        overlay_files:
          - default: audio_codec
          - default: resolution
          - default: video_format
    ```

    1. You **MUST** use the `schedule_overlays` attribute. You cannot schedule individual Overlay Files.

??? blank "Scheduling Individual Collections<a class="headerlink" href="#schedule-collection" title="Permanent link">¶</a>"
    
    <div id="schedule-collection" />Uses the `schedule` [Definition Setting](../files/settings.md) to set when each collection will run.

    Press the :fontawesome-solid-circle-plus: icon to learn more
 
    ```yaml title="Collections Scheduled for Different Days"
    collections:
      TMDb Trending Weekly:
        tmdb_trending_weekly: 30
        sync_mode: sync
        schedule: weekly(sunday)
      TMDb Top Rated:
        tmdb_top_rated: 30
        sync_mode: sync
        schedule: #(1)!
         - monthly(1)
         - monthly(15)
    ```

    1. This Collection will run on the 1st and the 15th of each month only

??? blank "Scheduling Operation Blocks<a class="headerlink" href="#schedule-operations" title="Permanent link">¶</a>"
    
    <div id="schedule-operations" />Each [Operation Block](operations.md#operation-blocks) can use the `schedule` [Definition Setting](../files/settings.md) to set when that block will run.

    Press the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml title="All Operations Scheduled for Friday"
    libraries:
      Movies:
        collection_files:
          - default: imdb
        operations:
          schedule: weekly(friday) #(1)!
          mass_critic_rating_update: tmdb
          split_duplicates: true
    ```
    
    1. All Operations will be processed on a Friday only

    ```yaml title="Operations Scheduled for Different Days"
    libraries:
      Movies:
        collection_files:
          - default: imdb
        operations:
          - schedule: weekly(friday) #(1)!
            mass_critic_rating_update: tmdb
          - schedule: weekly(saturday) #(2)!
            split_duplicates: true
    ```

    1. This Operation will be processed on a Friday only
    2. This Operation will be processed on a Saturday only

??? blank "Scheduling Pinning Collections<a class="headerlink" href="#schedule-pinning" title="Permanent link">¶</a>" 
    
    <div id="schedule-pinning" />Uses the `visible_library`, `visible_home`, or `visible_shared` [Collection Metadata Update](../files/updates.md) 
    to have collections be "pinned" toyour home screen while scheduled.

    Press the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml title="Pin Christmas Collection to Home in December"
    collections:
      Christmas:
        imdb_list: https://www.imdb.com/list/ls000096828/
        sync_mode: sync
        visible_home: range(12/01-12/31) #(1)!
    ```

    1. This Collection will appear on the server owner's home screen for the month of December, and once Kometa runs on January 1st the Collection will
        be unpinned and no longer visible on the home screen.