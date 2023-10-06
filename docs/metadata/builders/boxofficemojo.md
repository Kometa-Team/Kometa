# BoxOfficeMojo Builders

You can find items using the "Latest Weekend" list on [BoxOfficeMojo.com](https://www.boxofficemojo.com/). 

No configuration is required for this builder.

| Attribute                                                         | Description                                                                                   | Works with Movies | Works with Shows | Works with Playlists and Custom Sort |
|:------------------------------------------------------------------|:----------------------------------------------------------------------------------------------|:-----------------:|:----------------:|:------------------------------------:|
| [`boxofficemojo_latestweekend`](#boxofficemojos-latest-weekend-list) | Finds every movie on [BoxOfficeMojo's "Latest Weekend" list](https://www.boxofficemojo.com/). |      &#9989;      |     &#10060;     |               &#9989;                |

## BoxOfficeMojo's "Latest Weekend" List

Finds every movie on [BoxOfficeMojo's "Latest Weekend" list](https://www.boxofficemojo.com/).

The expected input is `true`.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order (top performer to lowest performer).

```yaml
collections:
  At The Box Office:
    boxofficemojo_latestweekend: true
    collection_order: custom
    sync_mode: sync
```
