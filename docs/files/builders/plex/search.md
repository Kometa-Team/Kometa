---
hide:
  - toc
---
# Plex Search

Uses Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/) to find all items based on the search parameters provided.

Any Advanced Filter made using the Plex UI should be able to be recreated using `plex_search`. If you're having trouble 
getting `plex_search` to work correctly, build the collection you want inside of Plex's Advanced Filters and take a 
screenshot of the parameters in the Plex UI and post it in either the 
[Discussions](https://github.com/Kometa-Team/Kometa/discussions) or on [Discord](https://kometa.wiki/en/latest/discord/), 
and I'll do my best to help you. 

like Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/) you have to start each search with either `any` or `all` as a base. You can only 
have one base attribute and all search attributes must be under the base.

Inside the base attribute you can use any search below or nest more `any` or `all`. You can have as many nested `any` 
or `all` next to each other as you want. If using multiple `any` or `all` you will have to do so in the form of a list.

**Note: To search by `season`, `episode`, `album`, or `track` you must use the `builder_level` [Setting](../settings.md) to change 
the type of items the collection holds.**

{%
    include-markdown "./search-options.md"
%}

{%
    include-markdown "./sort-options.md"
%}

## Plex Builder Attributes

The majority of Smart and Manual Builders utilize the same Builder Attributes. Any deviation from this will be highlighted against the specific Builder.

| Attribute  | Description & Values                                                                                                                                                                                                                               |
|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`    | **Description:** The max number of item for the filter.<br>**Default:** `all`<br>**Values:** `all` or a number greater than 0                                                                                                                      |
| `sort_by`  | **Description:** This will control how the filter is sorted in your library. You can do a multi-level sort using a list.<br>**Default:** `random`<br>**Values:** Any sort options for your filter type in the [Sorts Options Table](#sort-options) |
| `validate` | **Description:** Determines if a collection will fail on a validation error<br>**Default:** `true`<br>**Values**: `true` or `false`                                                                                                                |

### Example Plex Search Builder(s)

```yaml
collections:
  Documentaries:
    plex_search:
      all:
        genre: Documentary
```
```yaml
collections:
  Dave Chappelle Comedy:
    plex_search:
      all:
        actor: Dave Chappelle
        genre: Comedy
```
```yaml
collections:
  Top Action Movies:
    collection_order: custom
    plex_search:
      all:
        genre: Action
      sort_by: audience_rating.desc
      limit: 20
```
```yaml
collections:
  90s Movies:
    plex_search:
      any:
        year:
          - 1990
          - 1991
          - 1992
          - 1993
          - 1994
          - 1995
          - 1996
          - 1997
          - 1998
          - 1999
```
```yaml
collections:
  90s Movies:
    plex_search:
      any:
        decade: 1990
```
```yaml
collections:
  Best 2010+ Movies:
    collection_order: custom
    plex_search:
      all:
        year.gte: 2010
      sort_by:
        - year.desc
        - audience_rating.desc
      limit: 20
```

Here's an example of an episode collection using `plex_search`.

```yaml
 collections:
   Top 100 Simpsons Episodes:
     collection_order: custom
     builder_level: episode
     plex_search:
       type: episode
       sort_by: audience_rating.desc
       limit: 100
       all:
         title.ends: "Simpsons"
     summary: A collection of the highest rated simpsons episodes.
```

If you specify TMDb Person ID's using the Setting `tmdb_person` and then tell either `actor`, `director`, `producer`, or 
`writer` to add `tmdb`, the script will translate the TMDb Person IDs into their names and run the search on those names.

```yaml
collections:
  Robin Williams:
    plex_search:
      all:
        actor: tmdb
    tmdb_person: 2157
```
```yaml
collections:
  Steven Spielberg:
    plex_search:
      all:
        director: tmdb
    tmdb_person: https://www.themoviedb.org/person/488-steven-spielberg
```
```yaml
collections:
  Quentin Tarantino:
    plex_search:
      any:
        actor: tmdb
        director: tmdb
        producer: tmdb
        writer: tmdb
    tmdb_person: 138
```