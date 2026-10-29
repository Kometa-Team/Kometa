# AniList Builders

Collect anime from [AniList](https://anilist.co/) IDs, studios, relations, charts,
and user lists. For detailed filters, see [Advanced Search](search.md).
All builders support movie and show libraries.

## Choose a builder

| Builder | Finds | Playlists / custom sort |
|:--------|:------|:-----------------------|
| [`anilist_id`](#anilist-id) | Specific anime | No |
| [`anilist_relations`](#anilist-relations) | Anime and its related entries | No |
| [`anilist_studio`](#anilist-studio) | Anime from a studio | No |
| [`anilist_top_rated`](#anilist-top-rated) | Top-rated anime | Yes |
| [`anilist_popular`](#anilist-popular) | Popular anime | Yes |
| [`anilist_trending`](#anilist-trending) | Trending anime | Yes |
| [`anilist_userlist`](#anilist-userlist) | A user's named list, optionally filtered by score | Yes |
| [`anilist_search`](search.md) | Anime matching detailed filters | Yes |

For charts, user lists, and searches, use `collection_order: custom` to preserve
returned order and `sync_mode: sync` to keep membership synchronized.

## IDs, relations, and studios

These builders accept numeric IDs. Supply multiple values as a YAML list or a
comma-separated string. An anime ID and a studio ID identify different things,
even when the numbers happen to match.

### Specific anime {#anilist-id}

<span id="example-anilist-id-builders"></span>

Selects the two Cowboy Bebop entries by anime ID. The quoted value is a
comma-separated string; a YAML list of integers is also accepted.

```yaml
collections:
  Cowboy Bebop:
    anilist_id: "23,219"
```

### Relations {#anilist-relations}

<span id="example-anilist-relations-builders"></span>

Selects One Piece (ID 21) and its relation tree, excluding Character and Other
relations. This expands beyond the single specified anime.

```yaml
collections:
  One Piece:
    anilist_relations: 21
```

### Studios {#anilist-studio}

<span id="example-anilist-studio-builders"></span>

Selects anime associated with Studio Ghibli. Here `21` is a **studio ID**,
not the One Piece anime ID used above.

```yaml
collections:
  Studio Ghibli:
    anilist_studio: 21
```

## Charts

Each builder takes an integer specifying how many anime to query.

| Builder | Chart |
|:--------|:------|
| <span id="anilist-top-rated"></span>`anilist_top_rated` | [Top rated](https://anilist.co/search/anime?sort=SCORE_DESC) |
| <span id="anilist-popular"></span>`anilist_popular` | [Popular](https://anilist.co/search/anime/popular) |
| <span id="anilist-trending"></span>`anilist_trending` | [Trending](https://anilist.co/search/anime/trending) |

<span id="example-anilist-top-rated-builders"></span>
<span id="example-anilist-popular-builders"></span>
<span id="example-anilist-trending-builders"></span>

Selects up to 30 top-rated anime in returned order. Replace `anilist_top_rated`
with another chart builder to select that chart instead; `30` is a result count.

```yaml
collections:
  Top Rated Anime:
    anilist_top_rated: 30
    collection_order: custom
    sync_mode: sync
```

## User lists {#anilist-userlist}

Both `username` and `list_name` are required. Score filters use a 0-10 scale.
`.gt` / `.lt` exclude the boundary; `.gte` / `.lte` include it.

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `username` | String, required | AniList username |
| `list_name` | String, required | Name of the user's list |
| `score.gt`, `score.gte` | Number, 0.0-10.0 | Minimum score, exclusive / inclusive |
| `score.lt`, `score.lte` | Number, 0.0-10.0 | Maximum score, exclusive / inclusive |
| `sort_by` | Sort name; default `score` | `score`, `popularity`, `status`, `progress`, `last_updated`, `last_added`, `start_date`, `completed_date` |

<span id="example-anilist-userlist-builders"></span>

Selects items in the user's Watching list with a score of at least 7.5, sorted
by user score. Replace the placeholder username and list name as needed.
The names are strings and `7.5` is a decimal threshold.

```yaml
collections:
  Highly Rated Watching Anime:
    anilist_userlist:
      username: some_anilist_username
      list_name: Watching
      score.gte: 7.5
      sort_by: score
    collection_order: custom
    sync_mode: sync
```
