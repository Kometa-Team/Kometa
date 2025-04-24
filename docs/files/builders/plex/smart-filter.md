---
hide:
  - toc
---
# Plex Smart Filter

Smart Filters allow Kometa to create Smart Collections. The results of this builder are dynamic and do not require Kometa to re-run in order to update, instead they will update automatically as the data within your Plex Library updates (i.e. if new media is added)

Smart Filter Builders use Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/) to create a smart collection based on the filter parameters provided. Any Advanced Filter made using the Plex UI should be able to be recreated using `smart_filter`. This is the normal approach used when your Builder criteria is held solely within Plex, and no third-party service involvement is required.

???+ important

    Smart Filters do not work with Playlists

Like Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/), you have to start each filter with either `any` or `all` as a base. You can only 
have one base attribute and all filter attributes must be under the base.

Inside the base attribute you can use any filter below or nest more `any` or `all`. You can have as many nested `any` 
or `all` next to each other as you want. If using multiple `any` or `all` you will have to do so in the form of a list.

**Note: To search by `season`, `episode`, `album`, or `track` you must use the `builder_level` [Setting](../settings.md) 
to change the type of items the collection holds.**

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

### Example Smart Filter Builder(s)

```yaml
collections:
  Documentaries:
    smart_filter:
      all:
        genre: Documentary
```
```yaml
collections:
  Dave Chappelle Comedy:
    smart_filter:
      all:
        actor: Dave Chappelle
        genre: Comedy
```
```yaml
collections:
  Top Action Movies:
    smart_filter:
      all:
        genre: Action
      sort_by: audience_rating.desc
      limit: 20
```
```yaml
collections:
  90s Movies:
    smart_filter:
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
    smart_filter:
      any:
        decade: 1990
```

If you specify TMDb Person ID's using the Setting `tmdb_person` and then tell either `actor`, `director`, `producer`, or 
`writer` to add `tmdb`, the script will translate the TMDb Person IDs into their names and run the filter on those names.

```yaml
collections:
  Robin Williams:
    smart_filter:
      all:
        actor: tmdb
    tmdb_person: 2157
```
```yaml
collections:
  Steven Spielberg:
    smart_filter:
      all:
        director: tmdb
    tmdb_person: https://www.themoviedb.org/person/488-steven-spielberg
```
```yaml
collections:
  Quentin Tarantino:
    smart_filter:
      any:
        actor: tmdb
        director: tmdb
        producer: tmdb
        writer: tmdb
    tmdb_person: 138
```
