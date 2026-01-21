---
hide:
  - toc
---
# Letterboxd User Reviews

Finds every movie in a Letterboxd user's reviewed films page.

The expected input is a username or a dictionary with the username and optional parameters. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

You can add different filters directly to this Builder.

| Filter Attribute                                                                                  | Description                                                                                                                                                                                                |
|:--------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `username`                                                                                        | **Description:** Letterboxd username<br>**Values:** Username string (required)                                                                                                                          |
| `sort_by`                                                                                         | **Description:** Sort order for the reviews<br>**Default:** `release_date_newest`<br>**Values:** `release_date_newest`, `release_date_earliest`, `name`, `popularity`, `when_added_newest`, `when_added_earliest`, `when_rated_newest`, `when_rated_earliest`, `average_rating_highest`, `average_rating_lowest`, `user_rating_highest`, `user_rating_lowest`, `length_shortest`, `length_longest` |
| `min_rating` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-letterboxd-filters-1" } | **Description:** Filter by minimum user rating (on 10-point scale)<br>**Values:** number from `0` to `10`                                                                                                  |
| `limit`                                                                                           | **Description:** Max number of items per returned.<br>**Values:** number greater than `1`                                                                                                                  |
| `year` :material-numeric-1-circle:{ data-tooltip data-tooltip-id="tippy-letterboxd-filters-1" }   | **Description:** Search for the specified year range.<br>**Values:** range of int i.e. `1990-1999`                                                                                                         |
| `note` :material-numeric-2-circle:{ data-tooltip data-tooltip-id="tippy-letterboxd-filters-2" }   | **Description:** Search for the specified value in the note. The note is the user's note for the film.<br>**Values:** Any String                                                               |
| `incremental`                                                                                      | **Description:** Enable incremental parsing to only parse new items since last run (improves performance for large collections)<br>**Default:** `false`<br>**Values:** `true` or `false`<br>**Note:** When enabled, automatically uses `when_added_newest` sort and tracks parsed items |

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

???+ tip "Incremental Parsing"

    Incremental parsing is disabled by default. When enabled with `incremental: true`, only new items added since the last run will be parsed, significantly improving performance for large collections. On the first run, all items are parsed and the state is saved. Subsequent runs will only process new items. This is useful for users with very large collections who frequently add new reviews.

Using the `limit` filter attribute is recommended when using a user with many reviewed films as the number of results returned could be very large.

???+ tip "Details Builder"

    You can replace `letterboxd_user_reviews` with `letterboxd_user_reviews_details` if you would like to use the details variant (currently no description is available for user pages, but this maintains consistency with other builders).


### Example Letterboxd User Reviews Builder(s)

```yaml
collections:
  User Reviewed Films:
    letterboxd_user_reviews: {username}
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  User Top Rated Reviews:
    letterboxd_user_reviews:
      username: {username}
      min_rating: 9
      sort_by: user_rating_highest
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  User Recent Reviews:
    letterboxd_user_reviews:
      username: {username}
      sort_by: when_rated_newest
      limit: 50
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  Multiple Users' Reviewed Films:
    letterboxd_user_reviews:
      - {username1}
      - {username2}
      - {username3}
    collection_order: custom
    sync_mode: sync
```

```yaml
collections:
  Multiple Users' Top Rated Reviews:
    letterboxd_user_reviews:
      - username: {username1}
        min_rating: 9
        sort_by: user_rating_highest
      - username: {username2}
        min_rating: 8
        sort_by: user_rating_highest
    collection_order: custom
    sync_mode: sync
```
