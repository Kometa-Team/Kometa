# Schedule Setting

Plex Meta Manager allows you to schedule certain libraries/files so that runs can be tailored to suit your needs.

This is particularly handy for users who have a lot of libraries or run a lot of Metadata/Operations on their libraries.

### IMPORTANT:

These schedules do not trigger PMM to run; they control what PMM will do if it happens to be running at the scheduled time.  `weekly(sunday)`, for example, does not mean "run PMM on Sunday to do this thing"; it means "If PMM is running, and it's Sunday, do this thing".

The scheduling options are:

| Name         | Description                                                                                                | Format                                             | Example                                                      |
|:-------------|:-----------------------------------------------------------------------------------------------------------|:---------------------------------------------------|:-------------------------------------------------------------|
| Hourly       | Update only when the script is run in that hour or hour range                                              | hourly(Hour of Day)<br>hourly(Start Hour-End Hour) | `hourly(17)`<br>`hourly(17-04)`                              |
| Daily        | Update once a day                                                                                          | daily                                              | `daily`                                                      |
| Weekly       | Update once a week on the specified days (For multiple days use a bar-separated (<code>&#124;</code>) list | weekly(Days of Week)                               | `weekly(sunday)`<br><code>weekly(sunday&#124;tuesday)</code> |
| Monthly      | Update once a month on the specified day                                                                   | monthly(Day of Month)                              | `monthly(1)`                                                 |
| Yearly       | Update once a year on the specified day                                                                    | yearly(MM/DD)                                      | `yearly(01/30)`                                              |
| Range        | Updates whenever the date is within the range                                                              | range(MM/DD-MM/DD)                                 | `range(12/01-12/31)`                                         |
| Never        | Never updates                                                                                              | never                                              | `never`                                                      |
| Non Existing | Updates if it doesn't exist                                                                                | non_existing                                       | `non_existing`                                               |
| All          | Requires that all comma separated scheduling options inside its brackets be meet in order to run           | all[Options]                                       | `all[weekly(sunday), hourly(17)]`                            |

* `daily` is the default when `schedule` is not specified.
* You can run the script multiple times per day but using the `--time` command line argument detailed on the [Run Commands & Environmental Variables Page](../../home/environmental.md#time-to-run).
* You can have multiple scheduling options as a list.
* You can use the `delete_not_scheduled` setting to delete Collections that are skipped due to not being scheduled.

## Examples 

Below is an example of a library which has been scheduled to run every Sunday. This will schedule everything within the library (in this case Metadata files and Operations) for the same day.


```yaml
libraries:
  Movies:
    schedule: weekly(sunday)
    metadata_path:
      - file: config/Movies.yml
      - pmm: imdb
      - pmm: studio
      - pmm: genre
      - pmm: actor
    operations:
      mass_critic_rating_update: tmdb
```

Metadata Files, Playlist Files, and Overlay Files can all be individually scheduled, as seen below where different files are scheduled to run on each day of the week: 

**Note: Overlay Files cannot be individually Scheduled, all Overlay Files must be scheduled for the same period.**

```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
        schedule: weekly(monday)
      - pmm: imdb
        schedule: weekly(tuesday)
      - folder: config/Movies/
        schedule: weekly(wednesday)
      - pmm: genre
        schedule: weekly(thursday)
      - pmm: actor
        schedule: weekly(friday)
    overlay_path:
      - schedule: weekly(saturday)
      - pmm: audio_codec
      - pmm: resolution
      - pmm: video_format
playlist_files:
  - file: config/Playlists.yml
    schedule: weekly(sunday)
```

Below is an example of a collection which has been scheduled to run on a Sunday. In this scenario, if you run PMM on a Monday, this collection will be skipped but any other collections which do not have a scheduled defined will be run.

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

You can also schedule items to be "pinned" to your homescreen on a schedule. For example, this collection will be pinned to your homescreen for the month of December and on January 1st will no longer be pinned (you must run PMM on 1st January for the removal of the pin to happen)

```yaml
collections:
  Christmas Movies:
    imdb_list: https://www.imdb.com/list/ls000096828/
    sync_mode: sync
    visible_home: range(12/01-12/31)
```

Whilst it isn't possible to schedule individual Operations, you can create additional placeholder library names and point them to the original library using `library_name`. This can be used to achieve individually scheduled operations, as seen below:
```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
  Movies Operations (Monday):       # Name doesn't matter
    library_name: Movies            # Must match your library name in Plex
    schedule: weekly(monday)
    operations:
      mass_user_rating_update: imdb
  Movies Operations (Wednesday):       # Name doesn't matter
    library_name: Movies            # Must match your library name in Plex
    schedule: weekly(wednesday)
    operations:
      mass_audience_rating_update: tmdb
  Movies Operations (Friday):       # Name doesn't matter
    library_name: Movies            # Must match your library name in Plex
    schedule: weekly(friday)
    operations:
      mass_critic_rating_update: trakt
```
