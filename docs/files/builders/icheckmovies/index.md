# ICheckMovies Builders

Collect movies from [ICheckMovies](https://www.icheckmovies.com/) lists.
Both builders support **movies, playlists, and custom sorting**; they do not
support shows.

## Lists {#icheckmovies-list}

| Builder | Selects | Also copies |
|:--------|:--------|:------------|
| `icheckmovies_list` | Movies in the supplied lists | - |
| `icheckmovies_list_details` | The same movies | First list's description as the collection summary |

Both accept full list URLs. For multiple sources, use a YAML list or a
comma-separated string. The sources are combined, rather than used as AND/OR
filters. With `_details`, only the **first list supplies the summary**.

Use `collection_order: custom` to preserve the source order and `sync_mode: sync`
to keep collection membership synchronized as the lists change.

## Examples {#example-icheckmovies-list-builders}

=== "One list"

    Follows the Academy Award Best Picture list in its source order, updating
    membership as the list changes. The full URL is a string.

    ```yaml
    collections:
      Academy Award Best Picture:
        icheckmovies_list: https://www.icheckmovies.com/lists/academy+award+-+best+picture
        collection_order: custom
        sync_mode: sync
    ```

=== "Copy the description"

    Selects the same movies and copies the list's description into the collection
    summary. Use the `_details` variant when you want source metadata as well as
    list membership.

    ```yaml
    collections:
      Academy Award Best Picture:
        icheckmovies_list_details: https://www.icheckmovies.com/lists/academy+award+-+best+picture
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiple lists"

    Combines movies from two lists using a YAML list of URL strings. Replace the
    second URL with another ICheckMovies list URL. The summary comes from the
    Academy Award Best Picture list because it is first.

    ```yaml
    collections:
      Combined ICheckMovies Picks:
        icheckmovies_list_details:
          - https://www.icheckmovies.com/lists/academy+award+-+best+picture
          - https://www.icheckmovies.com/lists/your+other+list
        collection_order: custom
        sync_mode: sync
    ```
