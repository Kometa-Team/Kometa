# Letterboxd Builders

You can find items using the lists on [Letterboxd.com](https://letterboxd.com/) (Letterboxd). 

No configuration is required for these builders.

| Attribute                                     | Description                                                                                                     | Works with Movies | Works with Shows  | Works with Playlists and Custom Sort |
|:----------------------------------------------|:----------------------------------------------------------------------------------------------------------------|:-----------------:|:-----------------:|:------------------------------------:|
| [`letterboxd_list`](#letterboxd-list)         | Finds every movie in the Letterboxd List                                                                        |      &#9989;      |     &#10060;      |               &#9989;                |
| [`letterboxd_list_details`](#letterboxd-list) | Finds every movie in the Letterboxd List and updates the collection with the description of the Letterboxd list |      &#9989;      |     &#10060;      |               &#9989;                |

## Letterboxd List

Finds every movie in the Letterboxd List.

The expected input is a Letterboxd List URL. Multiple values are supported as either a list or a comma-separated string.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Vulture’s 101 Best Movie Endings:
    letterboxd_list: https://letterboxd.com/brianformo/list/vultures-101-best-movie-endings/
    collection_order: custom
    sync_mode: sync
```

* You can update the collection details with the Letterboxd List's description by using `letterboxd_list_details`.
* You can specify multiple collections in `letterboxd_list_details` but it will only use the first one to update the collection summary.

```yaml
collections:
  Vulture’s 101 Best Movie Endings:
    letterboxd_list_details: https://letterboxd.com/brianformo/list/vultures-101-best-movie-endings/
    collection_order: custom
    sync_mode: sync
```
