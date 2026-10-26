# WeTrakr Builders

Collect lists, tracking data, favorites, and ratings from [WeTrakr](https://wetrakr.com/).
All builders support movies, shows, playlists, and custom sorting.

!!! warning "Configure WeTrakr first"

    All builders require [WeTrakr configuration](../../../config/wetrakr.md).
    Personal-data and ratings builders use the account associated with the
    configured `authorization`.

## Choose a builder

| Builder | Finds |
|:--------|:------|
| [`wetrakr_list`](#wetrakr_list) | Items in specific lists |
| [`wetrakr_user_lists`](#wetrakr_user_lists) | Items across a user's public lists |
| [`wetrakr_tracking`](#wetrakr_tracking) | Tracked items, optionally filtered by status |
| [`wetrakr_favorites`](#wetrakr_favorites) | Favorites |
| [`wetrakr_ratings`](#wetrakr-ratings) | Rated items, optionally filtered by score |

Use `collection_order: custom` to retain returned order and `sync_mode: sync`
to keep collection membership synchronized as the source changes.

## Lists {#wetrakr-list}

### Specific lists {#wetrakr_list}

`wetrakr_list` accepts a list URL, such as `https://wetrakr.com/lists/13255`, or a
numeric list ID. For multiple sources, use a YAML list or comma-separated string.
Private and friends-only lists are readable only when owned by the authenticated
account; an inaccessible private list produces an error naming the list.

Use `wetrakr_list_details` to also copy the description into the collection summary.
With multiple lists, **only the first supplies the description**.

<span id="example-wetrakr-list-builders"></span>

=== "URL string"

    Follows list 13255 in its returned order. The full URL is a string.

    ```yaml
    collections:
      WeTrakr Picks:
        wetrakr_list: https://wetrakr.com/lists/13255
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiple IDs and summary"

    Combines items from two numeric list IDs using a YAML list. The collection
    summary comes from list 13255, the first entry. The sources are combined,
    rather than used as AND/OR filters.

    ```yaml
    collections:
      Combined WeTrakr Picks:
        wetrakr_list_details:
          - 13255
          - 1033032976
        collection_order: custom
        sync_mode: sync
    ```

### A user's public lists {#wetrakr_user_lists}

`wetrakr_user_lists` accepts a numeric user ID, username, or profile URL such as
`https://wetrakr.com/user/some_username`. Usernames and URLs are resolved through
search using an exact, case-insensitive username match.

Locked or non-public lists are skipped. More public lists require more requests;
Kometa logs the number found before processing them.

<span id="example-wetrakr-user-lists-builder"></span>

Combines items across user 275's public lists. Replace `275` with the desired user
ID, or supply their username or profile URL instead.

```yaml
collections:
  WeTrakr Community Picks:
    wetrakr_user_lists: 275
    collection_order: custom
    sync_mode: sync
```

## Personal data {#wetrakr-personal-data}

### Tracking {#wetrakr_tracking}

`wetrakr_tracking` accepts a blank value or `true` for every status valid for the
library type. `false` disables the builder; a dictionary selects specific statuses.

| Status | Movies | Shows |
|:-------|:-------|:------|
| `planning`, `watched`, `dropped` | Supported | Supported |
| `watching`, `waiting`, `paused` | Skipped | Supported |

=== "All valid statuses"

    Selects all tracked items valid for the library type. `true` is an unquoted
    boolean; leaving the value blank has the same effect.

    ```yaml
    collections:
      WeTrakr Tracking:
        wetrakr_tracking: true
        collection_order: custom
        sync_mode: sync
    ```

=== "One status"

    In a show library, selects shows marked watching. The nested `true` enables
    that status; movie libraries skip it because watching is a show-only status.

    ```yaml
    collections:
      WeTrakr Currently Watching:
        wetrakr_tracking:
          watching: true
        collection_order: custom
        sync_mode: sync
    ```

### Favorites {#wetrakr_favorites}

Accepts a blank value or `true`. This example selects all favorites from the
configured account, rather than a public user's lists.

```yaml
collections:
  WeTrakr Favorites:
    wetrakr_favorites: true
    collection_order: custom
    sync_mode: sync
```

## Ratings {#wetrakr-ratings}

`wetrakr_ratings` accepts a blank value or `true` for all rated items, a number
for a minimum score, or a dictionary of rating bounds. Scores use a 0-10 scale
with one decimal place.

### Rating bounds {#attributes}

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `minimum` | Number, 0-10; optional | Lowest rating to include |
| `maximum` | Number, 0-10; optional | Highest rating to include |

<span id="example-wetrakr-ratings-builders"></span>

=== "All rated items"

    Selects every rated item, regardless of score. A blank value also selects all.

    ```yaml
    collections:
      WeTrakr Rated:
        wetrakr_ratings: true
        sync_mode: sync
    ```

=== "Decimal threshold"

    Selects items rated at least 7.5. This number is a minimum rating, not an item limit.

    ```yaml
    collections:
      WeTrakr Rated 7.5 and Above:
        wetrakr_ratings: 7.5
        sync_mode: sync
    ```

=== "Dictionary range"

    Selects items rated from 7 through 9. Either bound can be omitted for a
    one-sided filter.

    ```yaml
    collections:
      WeTrakr Rated 7 to 9:
        wetrakr_ratings:
          minimum: 7
          maximum: 9
        sync_mode: sync
    ```
