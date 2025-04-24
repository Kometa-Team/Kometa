---
hide:
  - toc
---
# MyAnimeList Search

Gets every anime in a MyAnimeList search. The different sub-attributes are detailed below. At least one attribute is required.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order. 

???+ warning "MyAnimeList Configuration"

    [Configuring MyAnimeList](../../../config/myanimelist.md) in the config is required for any of these builders to function.

| Attribute              | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|:-----------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `sort_by`              | **Description:** Sort Order to return<br>**Values:** `mal_id.desc`, `mal_id.asc`, `title.desc`, `title.asc`, `type.desc`, `type.asc`, `rating.desc`, `rating.asc`, `start_date.desc`, `start_date.asc`, `end_date.desc`, `end_date.asc`, `episodes.desc`, `episodes.asc`, `score.desc`, `score.asc`, `scored_by.desc`, `scored_by.asc`, `rank.desc`, `rank.asc`, `popularity.desc`, `popularity.asc`, `members.desc`, `members.asc`, `favorites.desc`, `favorites.asc` |
| `limit`                | **Description:** Don't return more than this number<br>**Values:** Number of Anime to query from MyAnimeList                                                                                                                                                                                                                                                                                                                                                           |
| `query`                | **Description:** Text query to search for                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `prefix`               | **Description:** Results must begin with this prefix                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `type`                 | **Description:** Type of Anime to search for<br>**Values:** `tv`, `movie`, `ova`, `special`, `ona`, `music`                                                                                                                                                                                                                                                                                                                                                            |
| `status`               | **Description:** Status to search for<br>**Values:** `airing`, `complete`, `upcoming`                                                                                                                                                                                                                                                                                                                                                                                  |
| `genre`                | **Description:** Comma-separated String of Genres to include using `,` for `AND` and <code>&#124;</code> for `OR`<br>**Values:** Genre Name or ID                                                                                                                                                                                                                                                                                                                      |
| `genre.not`            | **Description:** Comma-separated String of Genres to exclude using `,` for `AND` and <code>&#124;</code> for `OR`<br>**Values:** Genre Name or ID                                                                                                                                                                                                                                                                                                                      |
| `studio`               | **Description:** Comma-separated String of Genres to include using `,` for `AND` and <code>&#124;</code> for `OR`<br>**Values:** Studio Name or ID                                                                                                                                                                                                                                                                                                                     |
| `content_rating`       | **Description:** Content Rating to search for<br>**Values:** `g`, `pg`, `pg13`, `r17`, `r`, `rx`                                                                                                                                                                                                                                                                                                                                                                       |
| `score.gt`/`score.gte` | **Description:** Score must be greater than the given number<br>**Values:** Float between `0.00`-`10.00`                                                                                                                                                                                                                                                                                                                                                               |
| `score.lt`/`score.lte` | **Description:** Score must be less than the given number<br>**Values:** Float between `0.00`-`10.00`                                                                                                                                                                                                                                                                                                                                                                  |
| `sfw`                  | **Description:** Results must be Safe for Work<br>**Value:** `true`                                                                                                                                                                                                                                                                                                                                                                                                    |

* Studio options can be found on [MyAnimeList's Search](https://myanimelist.net/anime.php) Page.
* Genre options can be found on [MyAnimeList's Search](https://myanimelist.net/anime.php) Page.
* To find the ID click on a Studio or Genre in the link above and there should be a number in the URL that's the `id`.
* For example if the url is `https://myanimelist.net/anime/producer/4/Bones` the `id` would be `4` or if the url is `https://myanimelist.net/anime/genre/1/Action` the `id` would be `1`.

### Example MyAnimeList Search Builder(s)

```yaml
collections:
  Top Action Anime:
    mal_search:
      limit: 100
      sort_by: score.desc
      genre: Action
    collection_order: custom
    sync_mode: sync
```
