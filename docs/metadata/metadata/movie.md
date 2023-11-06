# Movie Library Metadata

You can have the script edit the metadata of Movies by adding them to the `metadata` mapping of a Metadata File.

An example of multiple metadata edits in a movie library is below:

```yaml
metadata:
  Godzilla (1954):
    match:
      title: Godzilla
      year: 1954
    content_rating: R
  Godzilla (1998):
    match:
      title: Godzilla
      year: 1998
    sort_title: Godzilla 03
    content_rating: PG-13
  Shin Godzilla:
    sort_title: Godzilla 06
    content_rating: R
  Godzilla 1985:
    content_rating: PG
  "Godzilla 2000: Millennium":
    originally_available: 1999-08-18
  Godzilla Against MechaGodzilla:
    originally_available: 2002-03-23
  Godzilla Raids Again:
    content_rating: G
    originally_available: 1955-05-21
  Godzilla vs. Biollante:
    content_rating: PG
  Godzilla vs. Destoroyah:
    content_rating: PG
    originally_available: 1995-01-19
  Godzilla vs. Gigan:
    content_rating: G
    originally_available: 1972-09-14
  Godzilla vs. Hedorah:
    content_rating: G
    originally_available: 1971-04-01
  Godzilla vs. King Ghidorah:
    content_rating: PG
    originally_available: 1991-04-28
  Godzilla vs. Mechagodzilla:
    content_rating: G
    originally_available: 1974-03-24
  Godzilla vs. Mechagodzilla II:
    content_rating: PG
  Godzilla vs. Megaguirus:
    content_rating: PG
    originally_available: 2000-08-31
  Godzilla vs. Megalon:
    content_rating: G
    originally_available: 1973-03-17
  Godzilla vs. Mothra:
    content_rating: PG
    originally_available: 1992-04-28
  Godzilla vs. SpaceGodzilla:
    content_rating: PG
    originally_available: 1994-01-19
  Godzilla, King of the Monsters!:
    content_rating: G
  "Godzilla, Mothra and King Ghidorah: Giant Monsters All-Out Attack":
    content_rating: PG
    originally_available: 2001-08-31
  "Godzilla: Final Wars":
    content_rating: PG
    originally_available: 2004-12-13
  "Godzilla: Tokyo S.O.S.":
    originally_available: 2003-12-14
  Halloween (Rob Zombie):
    match:
      title: 
        - Halloween (Rob Zombie)
        - Halloween
    year: 2007
  "Halo 4: Forward Unto Dawn":
    match:
      title:
        - Halo 4: Forward Unto Dawn
        - Halo 4 Forward Unto Dawn
    tmdb_show: 56295
    content_rating: R
```

## Matching Movies

The `match` attribute is used to match movies within Plex to that definition within the Metadata file. One definition can match and edit multiple movies. The available matching options are outlined below.

| Attribute                      | Description                                                                                                       |
|:-------------------------------|:------------------------------------------------------------------------------------------------------------------|
| `title`<sup>1</sup>            | Only matches movies that exactly match the movie's Title. Can be a list (only one needs to match).                |
| `year`                         | Only matches movies that were released in the given year.                                                         |
| `mapping_id`<sup>2</sup>       | Only matches movies that have the given TMDb or IMDb ID.                                                          |
| `edition`<sup>3</sup>          | Only matches movies that exactly match the movie's Edition. Can be a list (only one needs to match).              |
| `edition_contains`<sup>3</sup> | Only matches movies where the movie's Edition contains the given string. Can be a list (only one needs to match). |
| `blank_edition`<sup>3</sup>    | Only matches movies that have no Edition.<br>**Default:** `false`<br>**Values:** `true` or `false`                |                                                                                                                                                                                         

1. When `title` is not provided and the mapping name was not specified as an ID, the default behaviour is to use the mapping name as `title` for matching.
2. When `mapping_id` is not provided and the mapping name was specified as an ID, the default behaviour is to use the mapping name as `mapping_id` for matching.
3. When the server does not have a Plex Pass then the Edition Field is not accessible. In this scenario, PMM will check the movie's filepath for `{edition-...}` to determine what the edition is.

### Examples

Below are some examples on how movies can be matched.

#### Example 1 - `title` and `mapping_id` 

The below example shows how `title` and `mapping_id` can be used to match movies.

```yaml
metadata:
  movie1:                   # Matches via the title "Star Wars"
    match:
      title: Star Wars
    edits...
  movie2:                   # Matches via TMDb ID: 299534
    match:
      mapping_id: 299534
    edits...
  movie3:                   # Matches via IMDb ID: tt4154756
    match:
      mapping_id: tt4154756
    edits...
  movie4:                   # Matches via the title "9" 
    match:
      title: 9
    edits...
```

The Mapping Name can also be used to reduce line-count, as shown here:

```yaml
metadata:
  Star Wars:    # Matches via the title "Star Wars"
    edits...
  299534:       # Matches via TMDb ID: 299534
    edits...
  tt4154756:    # Matches via IMDb ID: tt4154756
    edits...
  "9":          # Matches via the title "9" 
    edits...
```

**Note:** to search for a movie titled with a number from the mapping name you must surround the number in quotes like in the example below. Otherwise, it will look for the movie associated with that TMDb ID.

#### Example 2 - `title` and `year`

The below example shows how `title` and `year` can be used to match movies. 

In this example, there are two movies in the library called "Godzilla", so the `year` attribute is used to identify which movie is being matched.

```yaml
metadata:
  Godzilla (1954):                   # Matches via the title "Godzilla" released in 1954
    match:
      title: Godzilla
      year: 1954
    edits...
  Godzilla (1998):                   # Matches via the title "Godzilla" released in 1998
    match:
      title: Godzilla
      year: 1998
    edits...
```

#### Example 3 - using `editions`

The edition attributes can be used to further specify which version of a movie should be matched within Plex.

This can be combined with Example 1 as follows

```yaml
metadata:
  movie1:                   # Matches via the title "Star Wars" and edition containing "4K77"
    match:
      title: Star Wars
      edition_contains: 4K77
    edits...
```

If you wanted to specify the version of Star Wars which does not have an edition, then the `blank_edition` attribute can be used as shown below:

```yaml
metadata:
  movie1:                   # Matches via the title "Star Wars" and checks for no edition version
    match:
      title: Star Wars
      blank_edition: true
    edits...
```

## Metadata Edits

The available attributes for editing movies are as follows

### Special Attributes

| Attribute        | Description                                                                                                                                                                                                                                                                              |
|:-----------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `tmdb_show`      | TMDb Show ID to use for metadata. Used when the Movie in your library is actually a miniseries on TMDb. (Example: [Halo 4: Forward Unto Dawn](https://www.themoviedb.org/tv/56295) or [IT](https://www.themoviedb.org/tv/19614)) **This is not used to say this movie is the given ID.** |
| `run_definition` | Used to specify if this definition runs.<br>Multiple can be used for one definition as a list or comma separated string. One `false` or unmatched library type will cause it to fail.<br>**Values:** `movie`, `show`, `artist`, `true`, `false`                                          |

1. If the server does not have a Plex Pass then the Edition Field is not accessible. In this case PMM will check the movies filepath for `{edition-MOVIES EDITION}` to determine what the edition is.

### General Attributes

| Attribute              | Allowed Values                                                 |
|:-----------------------|:---------------------------------------------------------------|
| `title`                | Text to change Title.                                          |
| `sort_title`           | Text to change Sort Title.                                     |
| `edition`<sup>1</sup>  | Text to change Edition.                                        |
| `original_title`       | Text to change Original Title.                                 |
| `originally_available` | Date to change Originally Available.<br>**Format:** YYYY-MM-DD |
| `content_rating`       | Text to change Content Rating.                                 |
| `user_rating`          | Number to change User Rating.                                  |
| `audience_rating`      | Number to change Audience Rating.                              |
| `critic_rating`        | Number to change Critic Rating.                                |
| `studio`               | Text to change Studio.                                         |
| `tagline`              | Text to change Tagline.                                        |
| `summary`              | Text to change Summary.                                        |

1. Requires Plex Pass

### Tag Attributes

You can add `.remove` to any tag attribute to only remove those tags i.e. `genre.remove`.

You can add `.sync` to any tag attribute to sync all tags vs just appending the new ones i.e. `genre.sync`.

| Attribute    | Allowed Values                                       |
|:-------------|:-----------------------------------------------------|
| `director`   | List or comma-separated text of each Director Tag.   |
| `country`    | List or comma-separated text of each Country Tag.    |
| `genre`      | List or comma-separated text of each Genre Tag.      |
| `writer`     | List or comma-separated text of each Writer Tag.     |
| `producer`   | List or comma-separated text of each Producer Tag.   |
| `collection` | List or comma-separated text of each Collection Tag. |
| `label`      | List or comma-separated text of each Label Tag.      |

### Image Attributes

| Attribute         | Allowed Values                                   |
|:------------------|:-------------------------------------------------|
| `url_poster`      | URL of image publicly available on the internet. |
| `file_poster`     | Path to image in the file system.                |
| `url_background`  | URL of image publicly available on the internet. |
| `file_background` | Path to image in the file system.                |

### Advanced Attributes

| Attribute                        | Allowed Values                                                                                                                                                                                                                                                                                                                                                                                      |
|:---------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `metadata_language`<sup>1</sup>  | `default`, `ar-SA`, `ca-ES`, `cs-CZ`, `da-DK`, `de-DE`, `el-GR`, `en-AU`, `en-CA`, `en-GB`, `en-US`, `es-ES`, `es-MX`, `et-EE`, `fa-IR`, `fi-FI`, `fr-CA`, `fr-FR`, `he-IL`, `hi-IN`, `hu-HU`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `lt-LT`, `lv-LV`, `nb-NO`, `nl-NL`, `pl-PL`, `pt-BR`, `pt-PT`, `ro-RO`, `ru-RU`, `sk-SK`, `sv-SE`, `th-TH`, `tr-TR`, `uk-UA`, `vi-VN`, `zh-CN`, `zh-HK`, `zh-TW` |
| `use_original_title`<sup>1</sup> | `default`: Library default<br>`no`: No<br>`yes`: Yes                                                                                                                                                                                                                                                                                                                                                |

1. Must be using the **New Plex Movie Agent**.