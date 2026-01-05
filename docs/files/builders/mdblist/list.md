---
hide:
  - toc
---
# MDBList List


???+ tip "Note on `mdb` sources"

     MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed. As such, the data that Kometa fetches and applies from MDBList may not be the same as you see if you visit those third-party sources directly.
 
Finds every item in a [MDBList List](https://mdblist.com/toplists/).

The expected input is an MDBList List URL. Multiple values are supported as a list only a comma-separated string will not work.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

## Sort Options

For these sorts to be reflected in your collection you **must** use `collection_order: custom`.

| Option                                        | Description                            |
|:----------------------------------------------|:---------------------------------------|
| `rank.asc`<br>`rank.desc`                     | Sort by MDBList Rank                   |
| `score.asc`<br>`score.desc`                   | Sort by MDBList Score                  |
| `score_average.asc`<br>`score_average.desc`   | Sort by MDBList Average Score          |
| `released.asc`<br>`released.desc`             | Sort by Release Date                   |
| `releasedigital.asc`<br>`releasedigital.desc` | Sort by Digital Release Date           |
| `imdbrating.asc`<br>`imdbrating.desc`         | Sort by IMDb Rating                    |
| `imdbvotes.asc`<br>`imdbvotes.desc`           | Sort by IMDb Votes                     |
| `imdbpopular.asc`<br>`imdbpopular.desc`       | Sort by IMDb Popular                   |
| `tmdbpopular.asc`<br>`tmdbpopular.desc`       | Sort by TMDb Popular                   |
| `rogerebert.asc`<br>`rogerebert.desc`         | Sort by RogerEbert Score               |
| `rtomatoes.asc`<br>`rtomatoes.desc`           | Sort by Rotten Tomatoes Score          |
| `rtaudience.asc`<br>`rtaudience.desc`         | Sort by Rotten Tomatoes Audience Score |
| `metacritic.asc`<br>`metacritic.desc`         | Sort by Metacritic Score               |
| `myanimelist.asc`<br>`myanimelist.desc`       | Sort by MyAnimeList Score              |
| `letterrating.asc`<br>`letterrating.desc`     | Sort by Letterboxd Rating              |
| `lettervotes.asc`<br>`lettervotes.desc`       | Sort by Letterboxd Votes               |
| `last_air_date.asc`<br>`last_air_date.desc`   | Sort by Last Air Date                  |
| `budget.asc`<br>`budget.desc`                 | Sort by Budget                         |
| `revenue.asc`<br>`revenue.desc`               | Sort by Revenue                        |
| `runtime.asc`<br>`runtime.desc`               | Sort by Runtime                        |
| `title.asc`<br>`title.desc`                   | Sort by Title                          |
| `sort_title.asc`<br>`sort_title.desc`         | Sort by Sort Title                     |
| `random.asc`<br>`random.desc`                 | Sort by Random (Randomized Daily)      |

### Example MDBList List Builder(s)

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

```yaml
collections:
  Top 10 Movies of The Week:
    mdblist_list: 
      url: https://mdblist.com/lists/linaspurinis/top-watched-movies-of-the-week
      sort_by: imdbrating.desc
    collection_order: custom
    sync_mode: sync
```

### "External" MDBList(s)

MDBList supports "external lists", which basically mirror a list from another site.  For example, this one:
```
https://mdblist.com/lists/chazlarson/external/2868
```
Which mirrors:
```
https://imdb.com/list/ls089009459
```

These lists can be used with Kometa, **provided** one or the other of these criteria are true:

1. The owner of the MDBList API Key also owns the MDBList external list OR
2. The owner of the MDBList external list has **unchecked** the `Make your external lists private` setting in their MDBList account settings.

```yaml
collections:
  Esquire 60 Scariest Movies of All Time:
    mdblist_list: https://mdblist.com/lists/chazlarson/external/2868
    collection_order: custom
    sync_mode: sync
```
