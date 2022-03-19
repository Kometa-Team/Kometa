# Reciperr Builders

You can find movies using a Reciperr list on [reciperr.com](https://reciperr.com/) (Reciperr). 

No configuration is required for this builder.

| Attribute                         | Description                                    | Works with Movies | Works with Shows | Works with Playlists and Custom Sort |
|:----------------------------------|:-----------------------------------------------|:-----------------:|:----------------:|:------------------------------------:|
| [`reciperr_list`](#reciperr-list) | Finds every movie at a Reciperr JSON data URL. |      &#9989;      |     &#10060;     |               &#9989;                |

## Reciperr List

Finds every movie on Reciperr a list.

The expected input is the url that points to the JSON data or a list of urls that do.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  Reciperr Movies:
    reciperr_list: https://reciperr.com/api/recipe/list/params?recipeMetadataId=62354f0e89a919001d650fa3
    collection_order: custom
    sync_mode: sync
```
