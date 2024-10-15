# MDBList Builders

You can find items using the features of [MDBList.com](https://mdblist.com/) (MDBList).

| Attribute                       | Description                                                               |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:--------------------------------|:--------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`mdblist_list`](#mdblist-list) | Gets every movie/show in a [MDBList List](https://mdblist.com/toplists/). | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |

???+ tip "Note on `mdb` sources"

     MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed. As such, the data that Kometa fetches and applies from MDBList may not be the same as you see if you visit those third-party sources directly.

## MDBList List

Finds every item in a [MDBList List](https://mdblist.com/toplists/).

The expected input is an MDBList List URL. Multiple values are supported as a list only a comma-separated string will not work.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

```yaml
collections:
  Top Movies of The Week:
    mdblist_list: https://mdblist.com/lists/linaspurinis/top-watched-movies-of-the-week
    collection_order: custom
    sync_mode: sync
```
You can also limit the number of items to search for by using the `limit` and `url` attributes under `mdblist_list`.

```yaml
collections:
  Top 10 Movies of The Week:
    mdblist_list: 
      url: https://mdblist.com/lists/linaspurinis/top-watched-movies-of-the-week
      limit: 10
    collection_order: custom
    sync_mode: sync
```
You can also sort the items by using the `sort_by` and `url` attributes under `mdblist_list`.

The default `sort_by` when it's not specified is `rank.asc`.

### Sort Options

| Option                                        | Description                    |
|:----------------------------------------------|:-------------------------------|
| `rank.asc`<br>`rank.desc`                     | Sort by MDBList Rank           |
| `score.asc`<br>`score.desc`                   | Sort by MDBList Score          |
| `score_average.asc`<br>`score_average.desc`   | Sort by MDBList Average Score  |
| `released.asc`<br>`released.desc`             | Sort by Release Date           |
| `imdbrating.asc`<br>`imdbrating.desc`         | Sort by IMDb Rating            |
| `imdbvotes.asc`<br>`imdbvotes.desc`           | Sort by IMDb Votes             |
| `imdbpopular.asc`<br>`imdbpopular.desc`       | Sort by IMDb Popular           |
| `tmdbpopular.asc`<br>`tmdbpopular.desc`       | Sort by TMDb Popular           |
| `rogerebert.asc`<br>`rogerebert.desc`         | Sort by RogerEvert Score       |
| `rtomatoes.asc`<br>`rtomatoes.desc`           | Sort by Rotten Tomatoes Score  |
| `metacritic.asc`<br>`metacritic.desc`         | Sort by Metacritic Score       |
| `myanimelist.asc`<br>`myanimelist.desc`       | Sort by MyAnimeList Score      |
| `budget.asc`<br>`budget.desc`                 | Sort by Budget                 |
| `revenue.asc`<br>`revenue.desc`               | Sort by Revenue                |
| `added.asc`<br>`added.desc`                   | Sort by Date Added             |

For these sorts to be reflected in your collection you must use `collection_order: custom`.

```yaml
collections:
  Top 10 Movies of The Week:
    mdblist_list: 
      url: https://mdblist.com/lists/linaspurinis/top-watched-movies-of-the-week
      sort_by: imdbrating.desc
    collection_order: custom
    sync_mode: sync
```