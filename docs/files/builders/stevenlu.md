# StevenLu Builders

You can find items using StevenLu's Popular Movies list on [StevenLu.com](https://movies.stevenlu.com/) (StevenLu). 

No configuration is required for this builder.

| Attribute                                            | Description                                                                          |             Works with Movies              |             Works with Shows             |    Works with Playlists and Custom Sort    |
|:-----------------------------------------------------|:-------------------------------------------------------------------------------------|:------------------------------------------:|:----------------------------------------:|:------------------------------------------:|
| [`stevenlu_popular`](#stevenlus-popular-movies-list) | Finds every movie on [StevenLu's Popular Movies List](https://movies.stevenlu.com/). | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |

## StevenLu's Popular Movies List

Finds every movie on [StevenLu's Popular Movies List](https://movies.stevenlu.com/).

The expected input is `true`.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

```yaml
collections:
  StevenLu's Popular Movies:
    stevenlu_popular: true
    collection_order: custom
    sync_mode: sync
```
