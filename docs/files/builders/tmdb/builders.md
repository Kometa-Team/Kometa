# TMDb Builders

Find movies and shows using [The Movie Database](https://www.themoviedb.org/) (TMDb).
Select titles by ID or URL, follow a chart, or collect a person's credits. For detailed search filters, use Discover for [movies](discover/movie.md) or [shows](discover/show.md).

## Choose a builder

- [IDs and URLs](#tmdb-standard-builders): collections, lists, specific titles, companies, networks, and keywords.
- [Charts](#tmdb-chart-builders): popular, top-rated, trending, and currently airing titles.
- [People](#tmdb-people-builders): acting, directing, writing, producing, and other crew credits.

## By ID or URL {#tmdb-standard-builders}

| Builder | Finds | Supports | Playlists / custom sort |
|:--------|:------|:---------|:-----------------------|
| [`tmdb_collection`](#tmdb-collection) | Movies in a TMDb collection | Movies | No |
| [`tmdb_list`](#tmdb-list) | Items in a TMDb list | Movies, shows | Yes |
| [`tmdb_movie`](#tmdb-movie) | Specific movies | Movies | No |
| [`tmdb_show`](#tmdb-show) | Specific shows | Shows | No |
| [`tmdb_company`](#tmdb-company) | Titles associated with a company | Movies, shows | No |
| [`tmdb_network`](#tmdb-network) | Shows associated with a network | Shows | No |
| [`tmdb_keyword`](#tmdb-keyword) | Titles tagged with a keyword | Movies, shows | No |

### Using IDs and URLs

The collection, list, movie, show, company, network, and keyword builders below accept a TMDb ID or full URL.
For multiple values, use a YAML list or a comma-separated string.
The same formats apply to their supported [`_details` variants](#copy-metadata-from-tmdb).

=== "Single ID"

    ```yaml
    collections:
      The Hobbit:
        tmdb_collection: 121938
    ```

=== "Full URL"

    ```yaml
    collections:
      The Hobbit:
        tmdb_collection: https://www.themoviedb.org/collection/121938-the-hobbit-collection
    ```

=== "Multiple values"

    ```yaml
    collections:
      Middle Earth:
        tmdb_collection:
          - 119
          - 121938
    ```

    You can mix IDs and full URLs in a YAML list. A comma-separated value such as
    `tmdb_collection: 119, 121938` is also accepted.

### Collection {#tmdb-collection}

Find every movie in a TMDb collection.

<span id="example-tmdb-collection-builders"></span>

```yaml
collections:
  The Hobbit:
    tmdb_collection: 121938
```

Find the ID in the collection URL: `themoviedb.org/collection/121938`.

### List {#tmdb-list}

Find every item in a TMDb list.

<span id="example-tmdb-list-builders"></span>

```yaml
collections:
  Top 50 Grossing Films of All Time (Worldwide):
    tmdb_list: 10
    collection_order: custom
    sync_mode: sync
```

Find the ID in the list URL: `themoviedb.org/list/10`.

Use `collection_order: custom` to preserve the list's order and `sync_mode: sync`
to keep collection membership in sync as the list changes.

### Movie {#tmdb-movie}

Find specific movies.

<span id="example-tmdb-movie-builders"></span>

```yaml
collections:
  Wizard of Oz & Wicked:
    tmdb_movie:
      - 630
      - 402431
```

Find the ID in the movie URL: `themoviedb.org/movie/630-the-wizard-of-oz`.

### Show {#tmdb-show}

Find specific shows.

<span id="example-tmdb-show-builders"></span>

```yaml
collections:
  Star Wars (Animated Shows):
    tmdb_show:
      - 4194
      - 60554
```

Find the ID in the show URL: `themoviedb.org/tv/4194-star-wars-the-clone-wars`.

### Company {#tmdb-company}

Find movies or shows associated with a TMDb company.

<span id="example-tmdb-company-builders"></span>

```yaml
collections:
  Studio Ghibli:
    tmdb_company: 10342
```

Find the ID in the company URL: `themoviedb.org/company/10342`.

### Network {#tmdb-network}

Find shows associated with a TMDb network.

<span id="example-tmdb-network-builders"></span>

```yaml
collections:
  CBS:
    tmdb_network: 16
```

Find the ID in the network URL: `themoviedb.org/network/16`.

### Keyword {#tmdb-keyword}

Find movies or shows tagged with a TMDb keyword.

<span id="example-tmdb-keyword-builders"></span>

```yaml
collections:
  Marvel Cinematic Universe:
    tmdb_keyword: 180547
```

Find the ID in the keyword URL: `themoviedb.org/keyword/180547`.

## Chart builders {#tmdb-chart-builders}

Choose a chart and set its value to the **number of items to query**, such as `30`.
All chart builders support playlists and custom sorting.

| Builder | Chart | Supports | Region option |
|:--------|:------|:---------|:--------------|
| <span id="tmdb-popular"></span>`tmdb_popular` | [Popular](https://www.themoviedb.org/movie) | Movies, shows | Yes |
| <span id="tmdb-top-rated"></span>`tmdb_top_rated` | [Top rated](https://www.themoviedb.org/movie/top-rated) | Movies, shows | Yes |
| <span id="tmdb-now-playing"></span>`tmdb_now_playing` | [Now playing](https://www.themoviedb.org/movie/now-playing) | Movies | Yes |
| <span id="tmdb-upcoming"></span>`tmdb_upcoming` | [Upcoming](https://www.themoviedb.org/movie/upcoming) | Movies | Yes |
| <span id="tmdb-airing-today"></span>`tmdb_airing_today` | [Airing today](https://www.themoviedb.org/tv/airing-today) | Shows | No |
| <span id="tmdb-on-the-air"></span>`tmdb_on_the_air` | [On the air](https://www.themoviedb.org/tv/on-the-air) | Shows | No |
| <span id="tmdb-trending-daily"></span>`tmdb_trending_daily` | Trending today | Movies, shows | No |
| <span id="tmdb-trending-weekly"></span>`tmdb_trending_weekly` | Trending this week | Movies, shows | No |

```yaml
collections:
  TMDb Popular:
    tmdb_popular: 30
    collection_order: custom
    sync_mode: sync
```

Replace `tmdb_popular` with any chart builder above. Use `collection_order: custom`
to preserve chart order and `sync_mode: sync` to keep membership synchronized.
For builders with a region option, add [`tmdb_region`](../../settings.md) to select a region.

## People builders {#tmdb-people-builders}

Find movies and shows associated with a person, using their TMDb person ID or URL.
The [ID and URL formats](#using-ids-and-urls) also apply here, including multiple people.
All people builders support movies and shows; none support playlists or custom sorting.

| Builder | Credits to include |
|:--------|:-------------------|
| <span id="tmdb-actor"></span>`tmdb_actor` | Acting |
| <span id="tmdb-crew"></span>`tmdb_crew` | All crew roles |
| <span id="tmdb-director"></span>`tmdb_director` | Directing |
| <span id="tmdb-producer"></span>`tmdb_producer` | Producing |
| <span id="tmdb-writer"></span>`tmdb_writer` | Writing |

```yaml
collections:
  Robin Williams:
    tmdb_actor: 2157
```

Find the ID in the person URL: `themoviedb.org/person/2157-robin-williams`.
Replace `tmdb_actor` with another role to select that person's corresponding credits.
Each role also has a [`_details` variant](#copy-metadata-from-tmdb) for copying the person's metadata.

!!! note "Collections contain media"

    Plex collections contain movies and shows, rather than people. For example,
    `tmdb_actor` creates a collection of a person's acting credits, not a collection of actors.

## Copy metadata from TMDb

Use a `_details` variant to find the same items and copy metadata to your Kometa collection.

| Builder | Metadata variant | Copies |
|:--------|:-----------------|:-------|
| `tmdb_collection` | `tmdb_collection_details` | Summary, poster, background |
| `tmdb_list` | `tmdb_list_details` | Summary, poster, background |
| `tmdb_movie` | `tmdb_movie_details` | Summary, poster, background |
| `tmdb_show` | `tmdb_show_details` | Summary, poster, background |
| `tmdb_actor` | `tmdb_actor_details` | Biography, profile |
| `tmdb_crew` | `tmdb_crew_details` | Biography, profile |
| `tmdb_director` | `tmdb_director_details` | Biography, profile |
| `tmdb_producer` | `tmdb_producer_details` | Biography, profile |
| `tmdb_writer` | `tmdb_writer_details` | Biography, profile |

```yaml
collections:
  Middle Earth:
    tmdb_collection_details:
      - 119
      - 121938
```

This example includes movies from both TMDb collections, but copies metadata
from **only the first entry** (`119`). The same first-entry rule applies to all
`_details` variants, including people: the first person supplies the biography and profile.

!!! note "Artwork priority"

    Posters and backgrounds in your library's asset directory take priority over
    artwork copied by a `_details` builder, unless `tmdb_poster` or
    `tmdb_background` is also specified.
