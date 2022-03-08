# Tautulli Builders

You can find items in your Plex using the features of [Tautulli](https://tautulli.com/).

[Configuring Tautulli](../../config/tautulli) in the config is required for any of these builders.

It has watch analytics that can show the most watched or most popular Movies/Shows in each Library.

| Attribute                                      | Description                         | Works with Movies | Works with Shows | Works with Playlists and Custom Sort |
|:-----------------------------------------------|:------------------------------------|:-----------------:|:----------------:|:------------------------------------:|
| [`tautulli_popular`](#tautulli-popularwatched) | Gets the Tautulli Most Popular List |      &#9989;      |     &#9989;      |               &#9989;                |
| [`tautulli_watched`](#tautulli-popularwatched) | Gets the Tautulli Most Watched List |      &#9989;      |     &#9989;      |               &#9989;                |

## Tautulli Popular/Watched

Both Tautulli Popular and Tautulli Watched have the same sub-attributes detailed below.

| Attribute      | Description                                                                          | Required | Default |
|:---------------|:-------------------------------------------------------------------------------------|:--------:|:-------:|
| `list_days`    | Number of Days to look back of the list                                              | &#10060; |   30    |
| `list_minimum` | Minimum Number of Users Watching/Plays to add to the list                            | &#10060; |   30    |
| `list_size`    | Number of Movies/Shows to add to this list                                           | &#10060; |   10    |
| `list_buffer`  | Number of extra Movies/Shows to grab in case you have multiple show/movie Libraries. | &#10060; |   10    |

If you have multiple movie Libraries or multiple show Libraries Tautulli combines those in the popular/watched lists so there might not be 10 movies/shows from the library to make your `list_size`.

In order to get around that, you can use the `list_buffer` attribute that defaults to 10. This will get that number more movies from Tautulli but only add to the collection until the size reaches the number in `list_size`.

So if your collection doesn't have as many movies/shows as your `list_size` attribute increase the number in the `list_buffer` attribute.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Most Popular Movies (30 Days):
    sync_mode: sync
    collection_order: custom
    tautulli_popular:
      list_days: 30
      list_size: 10
```
```yaml
collections:
  Most Watched Movies (30 Days):
    sync_mode: sync
    collection_order: custom
    tautulli_watched:
      list_days: 30
      list_size: 10
      list_buffer: 20
```
```yaml
collections:
  Plex Popular:
    tautulli_popular:
      list_days: 30
      list_size: 20
      list_buffer: 20
    tautulli_watched:
      list_days: 30
      list_size: 20
      list_buffer: 20
    sync_mode: sync
    summary: Movies Popular on Plex
    collection_order: alpha
```
```yaml
playlists:
  Plex Popular:
    libraries: Movies
    tautulli_popular:
      list_days: 30
      list_size: 20
      list_buffer: 20
    sync_mode: sync
    summary: Movies Popular on Plex
```
