---
hide:
  - toc
---
# MyAnimeList Seasonal

Gets anime in MyAnimeList's [Seasonal Anime](https://myanimelist.net/anime/season) list the options are detailed below. 

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

???+ warning "MyAnimeList Configuration"

    [Configuring MyAnimeList](../../../config/myanimelist.md) in the config is required for any of these builders to function.

| Attribute       | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|:----------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `season`        | **Description:** Season to search<br>**Default:** `current`<br>**Values:**<table class="clearTable"><tr><td>`winter`</td><td>For winter season January, February, March</td></tr><tr><td>`spring`</td><td>For spring season April, May, June</td></tr><tr><td>`summer`</td><td>For summer season July, August, September</td></tr><tr><td>`fall`</td><td>For fall season October, November, December</td></tr><tr><td>`current`</td><td>For the current Season</td></tr></table> |
| `year`          | **Description:** Year to search<br>**Default:** Current Year<br>**Values:** Number between `1917` and the current year.                                                                                                                                                                                                                                                                                                                                                          |
| `sort_by`       | **Description:** Sort Order<br>**Default:** `members`<br>**Values:**<table class="clearTable"><tr><td>`members`</td><td>Sort by Most Members</td></tr><tr><td>`score`</td><td>Sort by Score ([not working properly](https://myanimelist.net/forum/?topicid=2030371))</td></tr></table>                                                                                                                                                                                                                                                                    |
| `limit`         | **Description:** Don't return more than this number<br>**Default:** `100`<br>**Values:** Number of Anime to query from MyAnimeList (max: 500)                                                                                                                                                                                                                                                                                                                                    |
| `starting_only` | **Description:** Return only anime that began airing in the selected season<br>**Default:** `False`<br>**Values:** `True` or `False`                                                                                                                                                                                                                                                                                                                                             |

### Example MyAnimeList Seasonal Builder(s)

```yaml
collections:
  Current Anime Season:
    mal_season:
      sort_by: members
      limit: 50
    collection_order: custom
    sync_mode: sync
```
```yaml
collections:
  Fall 2020 Anime:
    mal_season:
      season: fall
      year: 2020
      limit: 50
    collection_order: custom
    sync_mode: sync
```
