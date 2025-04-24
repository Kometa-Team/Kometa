---
hide:
  - toc
---
# Trakt List

Finds every item in the Trakt List.

The expected input is a Trakt List URL. Multiple values are supported only as a list.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order. 

**Trakt Lists cannot be sorted through the API, but the list is always returned to the default list order if you own 
the list.**

???+ warning "Trakt Configuration"

    [Configuring Trakt](../../../config/trakt.md) in the config is required for any of these builders.

You can replace `trakt_list` with `trakt_list_details` if you would like to fetch and use the description from the list

If you have [authorized Trakt](../../../config/trakt.md) then you can use private Trakt Lists, this is not possible if 
you have not authorized Trakt.

When you link to a private list, set the list to `private` and then use the standard browser link:

```
https://trakt.tv/users/YOURTRAKTUSERNAME/lists/YOURLISTNAME
```

**DO NOT** set the list to `Share` and attempt to use the "Share link"; Kometa cannot use that address for the list.


???+ warning

    Trakt lists and users come and go, and Kometa has no control over this. The list URLs found in this documentation 
    are used here as examples and are available and working at time of writing, but they may disappear at any time. Do not take their use here as a guarantee that they exist or are working when you read this.

### Example Trakt List Builder(s)

```yaml
collections:
  Christmas:
    trakt_list:
      - https://trakt.tv/users/movistapp/lists/christmas-movies
      - https://trakt.tv/users/2borno2b/lists/christmas-movies-extravanganza
    sync_mode: sync
```
```yaml
collections:
  Reddit Top 250:
    trakt_list: https://trakt.tv/users/jaygreene/lists/reddit-top-250-2019-edition
    collection_order: custom
    sync_mode: sync
```

* You can update the collection details with the Trakt List's description by using `trakt_list_details`.
* You can specify multiple collections in `trakt_list_details` but it will only use the first one to update the collection summary.

```yaml
collections:
  Reddit Top 250:
    trakt_list_details: https://trakt.tv/users/jaygreene/lists/reddit-top-250-2019-edition
    collection_order: custom
    sync_mode: sync
```
