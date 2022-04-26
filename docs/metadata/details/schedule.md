# Schedule Detail

The script is designed to run continuously and certain attributes can be scheduled using these attributes.

Below is an example of a scheduled library: 
```yaml
libraries:
  Movies:
    schedule: weekly(sunday)
    metadata_path:
      - file: config/Movies.yml
      - git: meisnate12/MovieCharts
      - git: meisnate12/Studios
      - git: meisnate12/IMDBGenres
      - git: meisnate12/People
    operations:
      mass_critic_rating_update: tmdb
```

Below is an example of a scheduled Metadata File, Overlay File, and Playlist File: 
```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
        schedule: weekly(monday)
      - git: meisnate12/MovieCharts
        schedule: weekly(tuesday)
      - git: meisnate12/Studios
        schedule: weekly(wednesday)
      - git: meisnate12/IMDBGenres
        schedule: weekly(thursday)
      - git: meisnate12/People
        schedule: weekly(friday)
    overlay_path:
      - git: PMM/overlays/imdb
        schedule: weekly(saturday)
    operations:
      mass_critic_rating_update: tmdb
playlist_files:
  - file: config/Playlists.yml
    schedule: weekly(sunday)
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
    schedule: monthly(1), monthly(15)
```

Below is an example of a scheduled pinning collection: 
```yaml
collections:
  Christmas Movies:
    imdb_list: https://www.imdb.com/list/ls000096828/
    sync_mode: sync
    visible_home: range(12/01-12-31)
```

The scheduling options are:

| Name    | Description                                     | Format                | Example              |
|:--------|:------------------------------------------------|:----------------------|:---------------------|
| Hourly  | Update only when the script is run in that hour | hourly(Hour of Day)   | `hourly(17)`         |
| Daily   | Update once a day                               | daily                 | `daily`              |
| Weekly  | Update once a week on the specified day         | weekly(Day of Week)   | `weekly(sunday)`     |
| Monthly | Update once a month on the specified day        | monthly(Day of Month) | `monthly(1)`         |
| Yearly  | Update once a year on the specified day         | yearly(MM/DD)         | `yearly(01/30)`      |
| Range   | Updates whenever the date is within the range   | range(MM/DD-MM/DD)    | `range(12/01-12/31)` |
| Never   | Never updates                                   | never                 | `never`              |

* `daily` is the default when `schedule` isn't specified.
* You can run the script multiple times per day but using the `--time` command line argument detailed on the [Run Commands & Environmental Variables Page](../../home/environmental.md#time-to-run).
* You can have multiple scheduling options just make them a list or comma-separated values.
* You can use the `delete_not_scheduled` setting to delete Collections that are skipped due to not being scheduled.