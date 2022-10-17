# Schedule Detail

Libraries, Collections and individual Metadata/ Playlist files can be individually scheduled to only run when scheduled.

**NOTE** Overlay files cannot be individually scheduled, and are designed to run in an all-or-nothing fashion. Trying to individually schedule one Overlay file will result in all Overlay files within the library adopting the same schedule.

The below demonstrates a library will not run any metadata/overlay/operations on any day of the week apart from a Friday.

```yaml
libraries:
  Movies:
    schedule: weekly(friday)
    metadata_path:
      - file: config/Movies.yml
      - pmm: imdb
      - pmm: studio
      - pmm: genre
      - pmm: actor
    operations:
      mass_critic_rating_update: tmdb
```

The below showcases a library which has different Metadata files run on each day of the week, and a Playlist file which will run on a Saturday only.
```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
        schedule: weekly(monday)
      - pmm: imdb
        schedule: weekly(tuesday)
      - pmm: studio
        schedule: weekly(wednesday)
      - pmm: genre
        schedule: weekly(thursday)
      - pmm: actor
        schedule: weekly(friday)
playlist_files:
  - file: config/Playlists.yml
    schedule: weekly(saturday)
```

Below is an example of scheduling overlays to only run on a Sunday by utilizing the library_name attribute.

```yaml
libraries:
  Movies:
    schedule: weekly(friday)
    metadata_path:
      - file: config/Movies.yml
      - pmm: imdb
      - pmm: studio
      - pmm: genre
      - pmm: actor
  Movies Overlays:
    library_name: Movies
    schedule: weekly(sunday)
    overlay_path:
      - pmm: resolution
      - pmm: mediastinger
```

Below is an example of a scheduled collection: 
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

Below is an example of a scheduled pinning collection: 
```yaml
collections:
  Christmas Movies:
    imdb_list: https://www.imdb.com/list/ls000096828/
    sync_mode: sync
    visible_home: range(12/01-12/31)
```

The scheduling options are:

| Name         | Description                                                                                      | Format                | Example                           |
|:-------------|:-------------------------------------------------------------------------------------------------|:----------------------|:----------------------------------|
| Hourly       | Update only when the script is run in that hour                                                  | hourly(Hour of Day)   | `hourly(17)`                      |
| Daily        | Update once a day                                                                                | daily                 | `daily`                           |
| Weekly       | Update once a week on the specified day                                                          | weekly(Day of Week)   | `weekly(sunday)`                  |
| Monthly      | Update once a month on the specified day                                                         | monthly(Day of Month) | `monthly(1)`                      |
| Yearly       | Update once a year on the specified day                                                          | yearly(MM/DD)         | `yearly(01/30)`                   |
| Range        | Updates whenever the date is within the range                                                    | range(MM/DD-MM/DD)    | `range(12/01-12/31)`              |
| Never        | Never updates                                                                                    | never                 | `never`                           |
| Non Existing | Updates if it doesn't exist                                                                      | non_existing          | `non_existing`                    |
| All          | Requires that all comma separated scheduling options inside its brackets be meet in order to run | all[Options]          | `all[weekly(sunday), hourly(17)]` |

* `daily` is the default when `schedule` isn't specified.
* You can run the script multiple times per day but using the `--time` command line argument detailed on the [Run Commands & Environmental Variables Page](../../home/environmental.md#time-to-run).
* You can have multiple scheduling options as a list.
* You can use the `delete_not_scheduled` setting to delete Collections that are skipped due to not being scheduled.
