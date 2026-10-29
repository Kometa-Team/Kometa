# FlickList Builders

Collect movies and shows from [FlickList](https://flicklist.tv/) lists and account data.
All builders support playlists and custom sorting; media restrictions are shown below.

!!! warning "Configure FlickList first"

    Every builder requires the [FlickList configuration block](../../../config/flicklist.md).
    Personal-data and ratings builders use the account belonging to your configured
    `api_key`, with `read` access. Public user lists need no particular API key scope,
    but still require the configuration block.

## Choose a builder

| Builder | Finds | Supports |
|:--------|:------|:---------|
| [`flicklist_list`](#flicklist_list) | Items in specific lists | Movies, shows |
| [`flicklist_user_lists`](#flicklist_user_lists) | Items across a user's public lists | Movies, shows |
| [`flicklist_watchlist`](#flicklist-personal-data) | Entire watchlist, regardless of status | Movies, shows |
| [`flicklist_favorites`](#flicklist-personal-data) | Favorites | Movies, shows |
| [`flicklist_watched`](#flicklist-personal-data) | Actual watched history | Movies, shows |
| [`flicklist_up_next`](#flicklist-personal-data) | Next-unwatched-episode queue | Shows |
| [`flicklist_tracked`](#flicklist-personal-data) | Tracked shows | Shows |
| [`flicklist_ratings`](#flicklist-ratings) | Rated items, optionally filtered by score | Movies, shows |

Use `collection_order: custom` to preserve the source order and `sync_mode: sync`
to keep collection membership synchronized as the source changes.

## Lists {#flicklist-list}

### Specific lists {#flicklist_list}

`flicklist_list` accepts a full URL, such as `https://flicklist.tv/u/Furglitch/lists/dc-universe-chronological`,
or a numeric list ID, such as `4821`. For multiple sources, use a YAML list or
comma-separated string. The sources are combined, rather than used as AND/OR filters.

User list URLs are resolved to numeric IDs through the user's public lists. Legacy `/list/<id>` URLs remain accepted as numeric IDs even if the website no longer serves those pages.

Use `flicklist_list_details` to also copy the list description to the collection
summary. With multiple lists, **only the first list supplies the description**.

<span id="example-flicklist-list-builders"></span>

=== "One URL"

    Follows the DC Universe list in its source order. The URL is a string; collection
    membership stays synchronized as the list changes.

    ```yaml
    collections:
      FlickList Picks:
        flicklist_list: https://flicklist.tv/u/Furglitch/lists/dc-universe-chronological
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiple IDs and metadata"

    Combines items from lists 4821 and 9310 using a YAML list of numeric IDs.
    The collection summary comes from list 4821, the first entry.

    ```yaml
    collections:
      Combined FlickList Picks:
        flicklist_list_details:
          - 4821
          - 9310
        collection_order: custom
        sync_mode: sync
    ```

### A user's public lists {#flicklist_user_lists}

`flicklist_user_lists` accepts a username and combines every item across that
user's public lists. More lists require more requests; Kometa logs the number
of lists found before processing them.

<span id="example-flicklist-user-lists-builder"></span>

Replace the placeholder username with the FlickList user whose public lists you
want to follow. This selects their public lists, rather than your API key account's
personal watchlist or favorites.

```yaml
collections:
  FlickList Community Picks:
    flicklist_user_lists: some_flicklist_username
    collection_order: custom
    sync_mode: sync
```

## Personal data {#flicklist-personal-data}

The watchlist, favorites, watched, up-next, and tracked builders read from your
configured API key's account. Each accepts a **blank value or the unquoted boolean
`true`** to include all items. Only `flicklist_up_next` also accepts an integer limit.
See [Choose a builder](#choose-a-builder) for the source and media supported by each.

=== "Boolean"

    Includes every favorite from your configured account. Replace
    `flicklist_favorites` with another personal-data builder to select that source.
    `true` is a boolean, not a quoted string.

    ```yaml
    collections:
      FlickList Favorites:
        flicklist_favorites: true
        collection_order: custom
        sync_mode: sync
    ```

=== "Blank value"

    Includes the account's actual watched history. A blank builder value selects
    the entire source, just as `true` does.

    ```yaml
    collections:
      FlickList Watched:
        flicklist_watched:
        sync_mode: sync
    ```

=== "Integer limit"

    Queries up to 20 upcoming episodes from the account's next-unwatched-episode
    queue. Use this in a show library. The integer limits episodes returned by
    the source; it is not a rating threshold.

    ```yaml
    collections:
      FlickList Up Next:
        flicklist_up_next: 20
        collection_order: custom
        sync_mode: sync
    ```

!!! note "Watchlist status and watched history differ"

    `flicklist_watchlist` includes all watchlist statuses: `plan_to_watch`, `watching`,
    `completed`, `on_hold`, and `dropped`. It cannot filter to one status.
    `flicklist_watched` reflects actual movie or episode play history, rather
    than a manually assigned `completed` status.

## Ratings {#flicklist-ratings}

`flicklist_ratings` selects items rated by your configured API key's account.
A blank value or `true` selects every rated item; a number sets a minimum score;
a dictionary supplies rating bounds.

### Rating bounds {#attributes}

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `minimum` | Number, 0.5-10; optional | Lowest rating to include. |
| `maximum` | Number, 0.5-10; optional | Highest rating to include. |

FlickList documents ratings in half-point increments, but the API does not
currently enforce these increments; values such as `5.3` can appear in returned data.

<span id="example-flicklist-ratings-builders"></span>

=== "Every rated item"

    Includes every item the account has rated, regardless of score.

    ```yaml
    collections:
      FlickList Rated:
        flicklist_ratings: true
        sync_mode: sync
    ```

=== "Minimum score"

    Includes items rated at least 7.5. This scalar number is a rating threshold,
    rather than a result limit.

    ```yaml
    collections:
      FlickList Rated 7.5 and Above:
        flicklist_ratings: 7.5
        sync_mode: sync
    ```

=== "Rating range"

    Includes items rated from 7 through 9 using a dictionary of lower and upper
    bounds. Either bound can be omitted for a one-sided filter.

    ```yaml
    collections:
      FlickList Rated 7 to 9:
        flicklist_ratings:
          minimum: 7
          maximum: 9
        sync_mode: sync
    ```
