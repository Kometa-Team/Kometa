# Scheduling Parts of Kometa

Kometa allows you to schedule libraries, files, overlays, operations, and more so that runs can be tailored 
to suit your needs.

This is particularly handy for users who have a lot of libraries or run a lot of Metadata/Operations on their libraries.

### IMPORTANT:

These schedules do not trigger Kometa to run; they control what Kometa will do if it happens to be running at the scheduled 
time. `weekly(sunday)`, for example, does not mean "run Kometa on Sunday to do this thing"; it means "If Kometa is running, 
and it's Sunday, do this thing".

If you want to control when Kometa itself runs, like if you want Kometa to only run on Tuesdays and Thursdays, see [this page](../kometa/scheduling.md).

The scheduling options are:

| Name         | Description                                                                                                         | Format                                             | Example                                                              |
|:-------------|:--------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------|:---------------------------------------------------------------------|
| Hourly       | Update only when the script is run in that hour or hour range                                                       | hourly(Hour of Day)<br>hourly(Start Hour-End Hour) | `hourly(17)`<br>`hourly(17-04)`                                      |
| Daily        | Update once a day                                                                                                   | daily                                              | `daily`                                                              |
| Weekly       | Update once a week on the specified days (For multiple days, use a bar-separated (<code>&#124;</code>) list)        | weekly(Days of Week)                               | `weekly(sunday)`<br><code>weekly(sunday&#124;tuesday)</code>         |
| Monthly      | Update once a month on the specified day                                                                            | monthly(Day of Month)                              | `monthly(1)`                                                         |
| Yearly       | Update once a year on the specified day                                                                             | yearly(MM/DD)                                      | `yearly(01/30)`                                                      |
| Range        | Updates whenever the date is within the range (For multiple ranges, use a bar-separated (<code>&#124;</code>) list) | range(MM/DD-MM/DD)                                 | `range(12/01-12/31)`<br><code>range(8/01-8/15&#124;9/01-9/15)</code> |
| Never        | Never updates                                                                                                       | never                                              | `never`                                                              |
| Non Existing | Updates if it doesn't exist                                                                                         | non_existing                                       | `non_existing`                                                       |
| All          | Requires that all comma separated scheduling options inside its brackets be meet in order to run                    | all[Options]                                       | `all[weekly(sunday), hourly(17)]`                                    |

* `daily` is the default when `schedule` is not specified.
* You can run Kometa multiple times per day but using the `--time` command line argument detailed on the [Run Commands & Environmental Variables Page](../kometa/environmental.md).
* You can have multiple scheduling options as a list.
* You can use the `delete_not_scheduled` setting to delete Collections that are skipped due to not being scheduled.

## Examples

??? blank "Scheduling a Library<a class="headerlink" href="#schedule-library" title="Permanent link">¶</a>"
    
    <div id="schedule-library" />Uses the `schedule` [Library Attribute](libraries.md#Attributes) to set when a library will be run.

    Other schedule rules for files, overlays, collections, and any other attribute that can be scheduled must also be 
    met.

    ???+ example "Example"

        Below is an example of a library which has been scheduled to run every Sunday. 
       
        ```yaml
        libraries:
          Movies:
            schedule: weekly(sunday)
            collection_files:
              - file: config/Movies.yml
              - default: imdb
              - default: studio
              - default: genre
              - default: actor
            operations:
              mass_critic_rating_update: tmdb
        ```

??? blank "Scheduling Collection, Playlist, and Metadata Files<a class="headerlink" href="#schedule-files" title="Permanent link">¶</a>"
    
    <div id="schedule-files" />Uses the `schedule` [Block Attribute](files.md#Other-Block-Attributes) to set when a file
    will be run.

    Other schedule rules for collections and any other attribute that can be scheduled must also be met.

    ???+ example "Example"

        Collection Files, Playlist Files, and Metadata Files can all be individually scheduled, as seen below where 
        different files are scheduled to run on each day of the week:
        
        ```yaml
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
    
    <div id="schedule-overlays" />Uses the `schedule_overlays` [Library Attribute](libraries.md#attributes) to set when 
    overlays will run for a library.

    **Note: Overlay Files cannot be individually Scheduled, all Overlay Files must be scheduled for the same period.**

    ???+ example "Example"

        In the Example below overlays will only be run weekly on Saturday.
        
        ```yaml
        libraries:
          Movies:
            schedule_overlays: weekly(saturday)
            overlay_files:
              - default: audio_codec
              - default: resolution
              - default: video_format
        ```

??? blank "Scheduling Individual Collections<a class="headerlink" href="#schedule-collection" title="Permanent link">¶</a>"
    
    <div id="schedule-collection" />Uses the `schedule` [Definition Setting](../files/settings.md) to set when this 
    collection will run.

    ???+ example "Example"

        Below is an example of a collection which has been scheduled to run on a Sunday. In this scenario, if you run 
        Kometa on a Monday, this collection will be skipped but any other collections which do not have a scheduled defined 
        will be run.
        
        ```yaml
        collections:
          TMDb Trending Weekly:
            tmdb_trending_weekly: 30
            sync_mode: sync
            schedule: weekly(sunday)
          TMDb Top Rated:
            tmdb_top_rated: 30
            sync_mode: sync
            schedule: 
             - monthly(1)
             - monthly(15)
        ```

??? blank "Scheduling Operation Blocks<a class="headerlink" href="#schedule-operations" title="Permanent link">¶</a>"
    
    <div id="schedule-operations" />Each [Operation Block](operations.md#operation-blocks) can use the `schedule` 
    [Definition Setting](../files/settings.md) to set when that block will run.

    ???+ example "Example"

        This example shows just one Operation Block scheduled weekly on fridays.

        ```yaml
        libraries:
          Movies:
            collection_files:
              - default: imdb
            operations:
              schedule: weekly(friday)
              mass_critic_rating_update: tmdb
              split_duplicates: true
        ```
        
        This example shows 2 Operation Blocks each with a differnet schedule.

        ```yaml
        libraries:
          Movies:
            collection_files:
              - default: imdb
            operations:
              - schedule: weekly(friday)
                mass_critic_rating_update: tmdb
              - schedule: weekly(saturday)
                split_duplicates: true
        ```

??? blank "Scheduling Pinning Collections<a class="headerlink" href="#schedule-pinning" title="Permanent link">¶</a>" 
    
    <div id="schedule-pinning" />Uses the `visible_library`, `visible_home`, or `visible_shared` 
    [Collection Metadata Update](../files/updates.md) to have collections be "pinned" to your home screen while 
    scheduled.

    ???+ example "Example"

        In this example, the collection will be pinned to your home screen for the month of December and on January 1st
        will no longer be pinned (you must run Kometa on 1st January for the removal of the pin to happen)
        
        ```yaml
        collections:
          Christmas Movies:
            imdb_list: https://www.imdb.com/list/ls000096828/
            sync_mode: sync
            visible_home: range(12/01-12/31)
        ```
