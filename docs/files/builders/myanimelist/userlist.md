---
hide:
  - toc
---
# MyAnimeList UserList

Gets anime in MyAnimeList User's Anime list. The different sub-attributes are detailed below. The only required attribute is `username`

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

???+ warning "MyAnimeList Configuration"

    [Configuring MyAnimeList](../../../config/myanimelist.md) in the config is required for any of these builders to function.

| Attribute  | Description                                                                                                                                                                                                                                                                                                                                                                                                                       |
|:-----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `username` | **Description:** A user's MyAnimeList Username or `@me` for the authorized user                                                                                                                                                                                                                                                                                                                                                   |
| `status`   | **Description:** Status to search for<br>**Default:** `all`<br>**Values:**<table class="clearTable"><tr><td>`all`</td><td>All Anime List</td></tr><tr><td>`watching`</td><td>Currently Watching List</td></tr><tr><td>`completed`</td><td>Completed List</td></tr><tr><td>`on_hold`</td><td>On Hold List</td></tr><tr><td>`dropped`</td><td>Dropped List</td></tr><tr><td>`plan_to_watch`</td><td>Plan to Watch</td></tr></table> |
| `sort_by`  | **Description:** Sort Order to return<br>**Default:** `score`<br>**Values:**<table class="clearTable"><tr><td>`score`</td><td>Sort by Score</td></tr><tr><td>`last_updated`</td><td>Sort by Last Updated</td></tr><tr><td>`title`</td><td>Sort by Anime Title</td></tr><tr><td>`start_date`</td><td>Sort by Start Date</td></tr></table>                                                                                          |
| `limit`    | **Description:** Don't return more than this number<br>**Default:** `100`<br>**Values:** Number of Anime to query from MyAnimeList (max: 1000)                                                                                                                                                                                                                                                                                    |

### Example MyAnimeList UserList Builder(s)

```yaml
collections:
  Currently Watching Anime:
    mal_userlist:
      username: "@me"
      status: watching
      sort_by: score
      limit: 500
    collection_order: custom
    sync_mode: sync
```
