# Dynamic Collection Types

Specifies the type of dynamic collection to be created.

Depending on the `type` of dynamic collection, `data` is used to specify the options that are required to fulfill the requirements of creating the collection.

| Type Option                                   | Description                                                                                                 | Uses<br>`data` |  Movies  |  Shows   |  Music   |  Video   |
|:----------------------------------------------|:------------------------------------------------------------------------------------------------------------|:--------------:|:--------:|:--------:|:--------:|:--------:|
| [`tmdb_collection`](#tmdb-collection)         | Create a collection for each TMDb Collection associated with an item in the library                         |    &#10060;    | &#9989;  | &#10060; | &#10060; | &#10060; |
| [`tmdb_popular_people`](#tmdb-popular-people) | Create a collection for each actor found on [TMDb's Popular People List](https://www.themoviedb.org/person) |    &#9989;     | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`original_language`](#original-language)     | Create a collection for each TMDb original language associated with an item in the library                  |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`origin_country`](#origin-country)           | Create a collection for each TMDb origin country associated with an item in the library                     |    &#10060;    | &#10060; | &#9989;  | &#10060; | &#10060; |
| [`trakt_user_lists`](#trakt-user-lists)       | Create a collection for each list from specific trakt users                                                 |    &#9989;     | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`trakt_liked_lists`](#trakt-liked-lists)     | Create a collection for each list the authenticated trakt user likes                                        |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`trakt_people_list`](#trakt-people-list)     | Create a collection for each actor found in the trakt list                                                  |    &#9989;     | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`actor`](#actor)                             | Create a collection for each actor found in the library                                                     |    &#9989;     | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`director`](#director)                       | Create a collection for each director found in the library                                                  |    &#9989;     | &#9989;  | &#10060; | &#10060; | &#10060; |
| [`writer`](#writer)                           | Create a collection for each writer found in the library                                                    |    &#9989;     | &#9989;  | &#10060; | &#10060; | &#10060; |
| [`producer`](#producer)                       | Create a collection for each producer found in the library                                                  |    &#9989;     | &#9989;  | &#10060; | &#10060; | &#10060; |
| [`genre`](#genre)                             | Create a collection for each genre found in the library                                                     |    &#10060;    | &#9989;  | &#9989;  | &#9989;  | &#9989;  |
| [`album_genre`](#album-genre)                 | Create a collection for each album genre found in the library                                               |    &#10060;    | &#10060; | &#10060; | &#9989;  | &#10060; |
| [`content_rating`](#content-rating)           | Create a collection for each content rating found in the library                                            |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#9989;  |
| [`year`](#year)                               | Create a collection for each year found in the library                                                      |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`episode_year`](#episode-year)               | Create a collection for each episode year found in the library                                              |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`decade`](#decade.md)                           | Create a collection for each decade found in the library                                                    |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`country`](#country.md)                         | Create a collection for each country found in the library                                                   |    &#10060;    | &#9989;  | &#10060; | &#9989;  | &#9989;  |
| [`resolution`](#resolution)                   | Create a collection for each resolution found in the library                                                |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`subtitle_language`](#subtitle-language)     | Create a collection for each subtitle language found in the library                                         |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`audio_language`](#audio-language)           | Create a collection for each audio language found in the library                                            |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`studio`](#studio)                           | Create a collection for each studio found in the library                                                    |    &#10060;    | &#9989;  | &#9989;  | &#10060; | &#10060; |
| [`edition`](#edition)                         | Create a collection for each edition found in the library                                                   |    &#10060;    | &#9989;  | &#10060; | &#10060; | &#10060; |
| [`network`](#network)                         | Create a collection for each network found in the library                                                   |    &#10060;    | &#10060; | &#9989;  | &#10060; | &#10060; |
| [`mood`](#mood)                               | Create a collection for each artist mood found in the library                                               |    &#10060;    | &#10060; | &#10060; | &#9989;  | &#10060; |
| [`album_mood`](#album-mood)                   | Create a collection for each album mood found in the library                                                |    &#10060;    | &#10060; | &#10060; | &#9989;  | &#10060; |
| [`track_mood`](#track-mood)                   | Create a collection for each track mood found in the library                                                |    &#10060;    | &#10060; | &#10060; | &#9989;  | &#10060; |
| [`style`](#style)                             | Create a collection for each artist style found in the library                                              |    &#10060;    | &#10060; | &#10060; | &#9989;  | &#10060; |
| [`album_style`](#album-style)                 | Create a collection for each album style found in the library                                               |    &#10060;    | &#10060; | &#10060; | &#9989;  | &#10060; |
| [`number`](#number)                           | Creates a collection for each number defined                                                                |    &#9989;     | &#9989;  | &#9989;  | &#9989;  | &#9989;  |
| [`custom`](#custom)                           | Creates a collection for each custom `key: key_name` pair defined.                                          |    &#9989;     | &#9989;  | &#9989;  | &#9989;  | &#9989;  |

## TMDb Collection

Create collections based on the TMDb Collections associated with items in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>tmdb_collection</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>TMDb Collection ID</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>TMDb Collection Title</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  tmdb_collection_details: <<value>>
  minimum_items: 2
```

</td>
  </tr>
</table>

### Example: Create collection for every TMDb Collection found in the library.

```yaml
dynamic_collections:
  TMDb Collections:          # This name is the mapping name
    type: tmdb_collection
    remove_suffix: Collection
    remove_prefix: The
```

## TMDb Popular People

Create collections based on each actor found on [TMDb's Popular People List](https://www.themoviedb.org/person).

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>tmdb_popular_people</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Number greater than 0</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>TMDb Person ID</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>TMDb Person Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  tmdb_person: <<value>>
  plex_search:
    all:
      actor: tmdb
```

</td>
  </tr>
</table>

### Example: Create collection for the top 10 popular people

```yaml
dynamic_collections:
  TMDb Popular People:          # This name is the mapping name
    type: tmdb_popular_people
    data: 10
```

## Original Language

Create collections based on the TMDb original language associated with items in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>original_language</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td><a href="https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes">ISO 639-1 Code</a></td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>ISO Language Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  plex_all: true
  filters:
    original_language: <<value>>
```

</td>
  </tr>
</table>

### Example: Create collection for every TMDb Original Language found in the library.

```yaml
dynamic_collections:
  TMDb Languages:          # This name is the mapping name
    type: original_language
```

## Origin Country

Create collections based on the TMDb origin country associated with items in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>origin_country</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td><a href="https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2">ISO 3166-1 alpha-2 country code</a></td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>ISO Country Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  plex_all: true
  filters:
    origin_country: <<value>>
```

</td>
  </tr>
</table>

### Example: Create collection for every TMDb Origin Country found in the library.

```yaml
dynamic_collections:
  TMDb Countries:          # This name is the mapping name
    type: origin_country
```

## Trakt User Lists

Create collections for each of the Trakt lists for the specified users. Use `me` to reference the authenticated user.

* Requires [Trakt Authentication](../config/trakt.md) to be configured within the Configuration File

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>trakt_user_lists</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>List of Trakt Users</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Trakt List URL</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Trakt List Title</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  trakt_list_details: <<value>>
```

</td>
  </tr>
</table>

### Example: Create collections for each of the lists that the users have created

```yaml
dynamic_collections:
  Trakt User Lists:          # This name is the mapping name
    type: trakt_user_lists
    data:
     - me
     - yozoraxcii
```

## Trakt Liked Lists

Create collections for each of the Trakt lists that the authenticated user has liked.

* Requires [Trakt Authentication](../config/trakt.md) to be configured within the Configuration File

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>trakt_liked_lists</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Trakt List URL</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Trakt List Title</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  trakt_list_details: <<value>>
```

</td>
  </tr>
</table>

### Example: Create collections for each of the lists that the user has liked within Trakt

```yaml
dynamic_collections:
  Trakt Liked Lists:          # This name is the mapping name
    type: trakt_liked_lists
```

## Trakt People List

Create collections for each of the people found within Trakt lists that the user specifies.

* Requires [Trakt Authentication](../config/trakt.md) to be configured within the Configuration File

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>trakt_people_list</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>List of Trakt URLs</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>TMDb Person ID</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>TMDb Person Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  tmdb_person: <<value>>
  plex_search:
    all:
      actor: tmdb
```

</td>
  </tr>
</table>

### Example: Create a collection for each of the people on the trakt list
```yaml
dynamic_collections:
  Trakt People Lists:
    type: trakt_people_list
    data:
     - https://trakt.tv/users/ash9001/lists/all-time-top-actors
```

## Actor

Create a collection for each actor found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>actor</code></td>
  </tr>
  <tr>
    <th><code>data</code>s</th>
    <td>
        <table class="clearTable">
            <tr>
                <th>Attribute</th>
                <th>Description & Values</th>
            </tr>
            <tr>
                <td><code>depth</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 3</td>
            </tr>
            <tr>
                <td><code>minimum</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 3</td>
            </tr>
            <tr>
                <td><code>limit</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> None</td>
            </tr>
        </table>
    </td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Person Name</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Person Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  plex_search:
    any:
      actor: <<value>>
```

</td>
  </tr>
</table>

* `depth` determines how many top billed actor per item they are in. (i.e. if they play a cameo role, this is unlikely to be counted)
* `minimum` determines the minimum number of times the actor must appear within `depth` for the collection to be created.
* `limit` determines the number of actor collection to max out at. (i.e. if to make collections for the top 25 actors)

### Example:

* Create a collection for the top 25 actors who appear in the top 5 billing credits of movies

```yaml
dynamic_collections:
  Top Actors:         # mapping name does not matter just needs to be unique
    type: actor
    data:
      depth: 5
      limit: 25
```

### Example:

* Create a collection for actors who appear in the top 5 billing credits of movies
* Only create the collection if they are in the top 5 billing credits of at least 20 movies

```yaml
dynamic_collections:
  Actors:         # mapping name does not matter just needs to be unique
    type: actor
    data:
      depth: 5
      minimum: 20
```

## Director

Create a collection for each director found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>director</code></td>
  </tr>
  <tr>
    <th><code>data</code>s</th>
    <td>
        <table class="clearTable">
            <tr>
                <th>Attribute</th>
                <th>Description & Values</th>
            </tr>
            <tr>
                <td><code>depth</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 3</td>
            </tr>
            <tr>
                <td><code>minimum</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 3</td>
            </tr>
            <tr>
                <td><code>limit</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> None</td>
            </tr>
        </table>
    </td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Person Name</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Person Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  plex_search:
    any:
      director: <<value>>
```

</td>
  </tr>
</table>

* `depth` determines how many directors are looked at per item.
* `minimum` determines the minimum number of times the director must appear within `depth` for the collection to be created.
* `limit` determines the number of director collection to max out at. (i.e. if to make collections for the top 25 directors)

### Example:

* Create a collection for the top 5 directors who appear in the top director credit of movies

```yaml
dynamic_collections:
  Top Directors:         # mapping name does not matter just needs to be unique
    type: director
    data:
      depth: 1
      limit: 5
```

### Example:

* Create a collection for directors who appear in the top director credits of movies
* Only create the collection if they are in the top director credits of at least 10 movies

```yaml
dynamic_collections:
  Directors:         # mapping name does not matter just needs to be unique
    type: director
    data:
      depth: 1
      minimum: 10
```

## Writer

Create a collection for each writer found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>writer</code></td>
  </tr>
  <tr>
    <th><code>data</code>s</th>
    <td>
        <table class="clearTable">
            <tr>
                <th>Attribute</th>
                <th>Description & Values</th>
            </tr>
            <tr>
                <td><code>depth</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 3</td>
            </tr>
            <tr>
                <td><code>minimum</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 3</td>
            </tr>
            <tr>
                <td><code>limit</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> None</td>
            </tr>
        </table>
    </td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Person Name</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Person Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  plex_search:
    any:
      writer: <<value>>
```

</td>
  </tr>
</table>

* `depth` determines how many writers are looked at per item.
* `minimum` determines the minimum number of times the writer must appear within `depth` for the collection to be created.
* `limit` determines the number of writer collection to max out at. (i.e. if to make collections for the top 25 writers)

### Example:

* Create a collection for the top 5 writers who appear in the top writer credit of movies

```yaml
dynamic_collections:
  Top Writers:         # mapping name does not matter just needs to be unique
    type: writer
    data:
      depth: 1
      limit: 5
```

### Example:

* Create a collection for writers who appear in the top writer credits of movies
* Only create the collection if they are in the top writer credits of at least 10 movies

```yaml
dynamic_collections:
  Writers:         # mapping name does not matter just needs to be unique
    type: writer
    data:
      depth: 1
      minimum: 10
```

## Producer

Create a collection for each producer found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>producer</code></td>
  </tr>
  <tr>
    <th><code>data</code>s</th>
    <td>
        <table class="clearTable">
            <tr>
                <th>Attribute</th>
                <th>Description & Values</th>
            </tr>
            <tr>
                <td><code>depth</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 3</td>
            </tr>
            <tr>
                <td><code>minimum</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 3</td>
            </tr>
            <tr>
                <td><code>limit</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> None</td>
            </tr>
        </table>
    </td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Person Name</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Person Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  plex_search:
    all:
      producer: <<value>>
```

</td>
  </tr>
</table>

* `depth` determines how many producers are looked at per item.
* `minimum` determines the minimum number of times the producer must appear within `depth` for the collection to be created.
* `limit` determines the number of producer collection to max out at. (i.e. if to make collections for the top 25 producers)

### Example:

* Create a collection for the top 5 producers who appear in the top producer credit of movies

```yaml
dynamic_collections:
  Top Producers:         # mapping name does not matter just needs to be unique
    type: producer
    data:
      depth: 1
      limit: 5
```

### Example:

* Create a collection for producers who appear in the top producer credits of movies
* Only create the collection if they are in the top producer credits of at least 10 movies

```yaml
dynamic_collections:
  Producers:         # mapping name does not matter just needs to be unique
    type: producers
    data:
      depth: 1
      minimum: 10
```

## Genre

Create a collection for each genre found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>genre</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Genre</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Genre</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      genre: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create dynamic collections based on each genre found in the library (TV and Movies)
* Amend the template to increase the limit from 50 to 100
* Exclude the "Talk Show" genre
* Name the collection "Top [Genre] Movies" or "Top [Genre] Shows"

```yaml
templates:
  genre collection:
    smart_filter:
      limit: 100
      sort_by: critic_rating.desc
      all:
        genre: <<value>>
dynamic_collections:
  Genres:         # mapping name does not matter just needs to be unique
    type: genre
    exclude:
      - Talk Show
    title_format: Top <<key_name>> <<library_type>>s
    template: genre collection
```

## Album Genre

Create a collection for each album genre found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>album_genre</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Genre</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Genre</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; Albums</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: plays.desc
    any:
      album_genre: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create dynamic collections based on each Album genre found in the library
* Amend the template to increase the limit from 10 to 20 
* Exclude the "Pop" genre
* Name the collection "Top 20 [Genre] Albums"

```yaml
templates:
  genre collection:
    smart_filter:
      limit: 100
      sort_by: plays.desc
      all:
        album_genre: <<value>>
dynamic_collections:
  Genres:         # mapping name does not matter just needs to be unique
    type: album_genre
    exclude:
      - Pop
    title_format: Top 20 <<key_name>> <<library_type>>s
    template: genre collection
```

## Content Rating

Create a collection for each content rating found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>content_rating</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Content Rating</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Content Rating</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      content_rating: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create dynamic collections based on each content rating found in the library (TV and Movies)
* Amend the template to increase the limit from 50 to 100

```yaml
templates:
  content rating collection:
    smart_filter:
      limit: 100
      sort_by: critic_rating.desc
      all:
        content_rating: <<value>>
dynamic_collections:
  Content Ratings:         # mapping name does not matter just needs to be unique
    type: content_rating
    template: content rating collection
```

## Year

Create a collection for each year found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>year</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Year</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Year</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Best &lt;&lt;library_type&gt;&gt;s of &lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      year: <<value>>
```

</td>
  </tr>
</table>

### Example

* Create dynamic collections based on each year found in the library (TV and Movies)
* Use the `include` attribute to only show collections for years "2020", "2021" and "2022"
* Name the collection "Best of [Year]"

```yaml
dynamic_collections:
  Years:         # mapping name does not matter just needs to be unique
    type: year
    include:
      - 2020
      - 2021
      - 2022
    title_format: Best of <<key_name>>
```

## Episode Year

Create a collection for each episode year found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>episode_year</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Episode Year</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Year</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Best &lt;&lt;library_type&gt;&gt;s of &lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      episode_year: <<value>>
```

</td>
  </tr>
</table>

### Example

* Create dynamic collections based on each year found in the library (TV and Movies)
* Use the `include` attribute to only show collections for years "2020", "2021" and "2022"
* Name the collection "Best of [Year]"

```yaml
dynamic_collections:
  Years:         # mapping name does not matter just needs to be unique
    type: episode_year
    include:
      - 2020
      - 2021
      - 2022
    title_format: Best of <<key_name>>
```

## Decade

Create a collection for each decade found in the library

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>decade</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Decade</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Decade</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Best &lt;&lt;library_type&gt;&gt;s of &lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      decade: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for each decade found in the library (TV and Movies)
* Name the collection "Top [Decade] Movies"
* Rename the `2020` collection name to "Top 2020 Movies (so far)"

```yaml
dynamic_collections:
  Decades:         # mapping name does not matter just needs to be unique
    type: decade
    title_format: Top <<key_name>> <<library_type>>s
    title_override:
      2020: Top 2020 Movies (so far)
```

## Country

Create a collection for each country found in the library

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>country</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Country</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Country</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      country: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for the top movies from each country found in the library
* Name the collection "Top [Country] Cinema"
* The `key_name_override` attribute is used here in combination with the `title_format` to change the collection name from "France" which would be the default title, to "Top French Cinema"

```yaml
dynamic_collections:
  Countries:         # mapping name does not matter just needs to be unique
    type: country
    title_format: Top <<key_name>> Cinema
    key_name_override:
      France: French
      Germany: German
      India: Indian
```

## Resolution

Create a collection for each resolution found in the library

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>resolution</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Resolution</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Resolution</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: title.asc
    any:
      resolution: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for each resolution found in the library
* Name the collection "[Resolution] Movies"
* Combine 480p, 576p and SD into a collection called "SD Movies"
```yaml
dynamic_collections:
  Resolutions:         # mapping name does not matter just needs to be unique
    type: resolution
    addons:
      480p:
        - 576p
        - SD
    title_override:
      480p: SD Movies
```

## Subtitle Language

Create a collection for each subtitle language found in the library

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>subtitle_language</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td><a href="https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes">ISO 639-1 Code</a></td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Subtitle Language Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.asc
    any:
      subtitle_language: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for each subtitle language found in the library

```yaml
dynamic_collections:
  Subtitle Languages:         # mapping name does not matter just needs to be unique
    type: subtitle_language
```

## Audio Language

Create a collection for each audio language found in the library

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>audio_language</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td><a href="https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes">ISO 639-1 Code</a></td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Audio Language Name</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.asc
    any:
      audio_language: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for each audio language found in the library

```yaml
dynamic_collections:
  Audio Languages:         # mapping name does not matter just needs to be unique
    type: audio_language
```

## Studio

Create a collection for each studio found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>studio</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Studio</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Studio</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      studio: <<value>>
```

</td>
  </tr>
</table>


### Example:

* Create a collection for each studio found in a Movies library

```yaml
templates:
  studio collection:
    smart_filter:
      sort_by: critic_rating.desc
      all:
        studio: <<value>>
dynamic_collections:
  Studios:         # mapping name does not matter just needs to be unique
    type: studio
    title_format: <<key_name>>
    template: studio collection
```

## Edition

Create a collection for each edition found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>edition</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Editions</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Edition</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      edition: <<value>>
```

</td>
  </tr>
</table>


### Example:

* Create a collection for each edition found in a Movies library

```yaml
templates:
  edition collection:
    smart_filter:
      sort_by: critic_rating.desc
      all:
        edition: <<value>>
dynamic_collections:
  Sditions:         # mapping name does not matter just needs to be unique
    type: edition
    title_format: <<key_name>>
    template: edition collection
```

## Network

Create a collection for each network found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>network</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Network</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Network</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Top &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: critic_rating.desc
    any:
      network: <<value>>
```

</td>
  </tr>
</table>


### Example:

* Create a collection for each network found in a TV Shows library

```yaml
templates:
  network collection:
    smart_filter:
      sort_by: critic_rating.desc
      all:
        network: <<value>>
dynamic_collections:
  Networks:         # mapping name does not matter just needs to be unique
    type: network
    title_format: <<key_name>>
    template: network collection
```

## Mood

Create a collection for each artist mood found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>mood</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Mood</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Mood</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Most Played &lt;&lt;value&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 10
    sort_by: plays.desc
    any:
      artist_mood: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for the top 20 artists for each mood found in the Music library
* Amend the template to increase the limit from 10 to 20 
* Name the collection "Top 20 [Mood] Artists"

```yaml
templates:
  mood collection:
    smart_filter:
      limit: 20
      sort_by: plays.desc
      all:
        artist_mood: <<value>>
dynamic_collections:
  Moods:         # mapping name does not matter just needs to be unique
    type: mood
    title_format: Top 20 <<key_name>> Artists
    template: mood collection
```

## Album Mood

Create a collection for each album mood found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>album_mood</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Mood</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Mood</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Most Played &lt;&lt;value&gt;&gt; Albums</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 10
    sort_by: plays.desc
    any:
      album_mood: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for the top 20 albums for each mood found in the Music library
* Amend the template to increase the limit from 10 to 20 
* Name the collection "Top 20 [Mood] Albums"

```yaml
templates:
  mood collection:
    smart_filter:
      limit: 20
      sort_by: plays.desc
      all:
        album_mood: <<value>>
dynamic_collections:
  Moods:         # mapping name does not matter just needs to be unique
    type: album_mood
    title_format: Top 20 <<key_name>> Albums
    template: mood collection
```

## Track Mood

Create a collection for each track mood found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>track_mood</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Mood</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Mood</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Most Played &lt;&lt;value&gt;&gt; Tracks</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 50
    sort_by: plays.desc
    any:
      track_mood: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for the top 100 tracks for each mood found in the Music library
* Amend the template to increase the limit from 50 to 100 
* Name the collection "Top 100 [Mood] Tracks"

```yaml
templates:
  mood collection:
    smart_filter:
      limit: 100
      sort_by: plays.desc
      all:
        track_mood: <<value>>
dynamic_collections:
  Moods:         # mapping name does not matter just needs to be unique
    type: track_mood
    title_format: Top 100 <<key_name>> Tracks
    template: mood collection
```

## Style

Create a collection for each artist style found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>style</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Style</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Style</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Most Played &lt;&lt;key_name&gt;&gt; &lt;&lt;library_type&gt;&gt;s</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 10
    sort_by: plays.desc
    any:
      artist_style: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for the top 10 artists for each style found in the Music library
* Name the collection "Top [Style] Artists"

```yaml
templates:
  style collection:
    smart_filter:
      limit: 10
      sort_by: plays.desc
      all:
        artist_style: <<value>>
dynamic_collections:
  Styles:         # mapping name does not matter just needs to be unique
    type: style
    title_format: Top <<key_name>> <<library_type>>
    template: style collection
```

## Album Style

Create a collection for each album style found in the library.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>album_style</code></td>
  </tr>
  <tr>
    <th><code>data</code></th>
    <td>Not Used</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Style</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Style</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>Most Played &lt;&lt;key_name&gt;&gt; Albums</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>

```yaml
default_template:
  smart_filter:
    limit: 10
    sort_by: plays.desc
    any:
      album_style: <<value>>
```

</td>
  </tr>
</table>

### Example:

* Create a collection for the top 10 albums for each style found in the Music library
* Name the collection "Top [Style] Albums"

```yaml
templates:
  style collection:
    builder_level: album
    smart_filter:
      limit: 10
      sort_by: plays.desc
      all:
        album_style: <<value>>
dynamic_collections:
  Styles:         # mapping name does not matter just needs to be unique
    type: album_style
    title_format: Top <<key_name>> Albums
    template: style collection
```

## Number

Creates a collection for each number defined.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>number</code></td>
  </tr>
  <tr>
    <th><code>data</code>s</th>
    <td>
        <table class="clearTable">
            <tr>
                <th>Attribute</th>
                <th>Description & Values</th>
            </tr>
            <tr>
                <td><code>starting</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 0</td>
            </tr>
            <tr>
                <td><code>ending</code></td>
                <td><strong>Values:</strong> Number greater than 1</td>
                <td><strong>Default:</strong> 1</td>
            </tr>
            <tr>
                <td><code>increment</code></td>
                <td><strong>Values:</strong> Number greater than 0</td>
                <td><strong>Default:</strong> 1</td>
            </tr>
        </table>
        <ul>
          <li><strong><code>starting</code> and <code>ending</code> can also have the value <code>current_year</code></strong></li>
          <li><strong>You can also use a value relative to the <code>current_year</code> by doing <code>current_year-5</code></strong></li>
        </ul>
    </td>
  </tr>
  <tr>
    <th>Keys</th>
    <td>Number</td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td>Number</td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td>**None**</td>
  </tr>
</table>


### Example:

* Create a collection for the Oscar Winner by Year for the last 5 years
* Name the collection "Oscars Winners [Number]"

```yaml
templates:
  Oscars:
    summary: Academy Awards (Oscars) Winners for <<key>>
    imdb_list: https://www.imdb.com/search/title/?release_date=<<key>>-01-01,<<key>>-12-31&groups=oscar_winner&sort=moviemeter,asc
    sync_mode: sync
    collection_order: custom
dynamic_collections:
  Oscars Winners Awards:
    type: number
    sync: true
    data:
      starting: current_year-5
      ending: current_year
    title_format: Oscars Winners <<key_name>>
    template:
      - Oscars
```

## Custom

Creates a collection for each custom `key: key_name` pair defined.

<table class="dualTable colwidths-auto align-default table">
  <tr>
    <th><code>type</code></th>
    <td><code>custom</code></td>
  </tr>
  <tr>
    <th><code>data</code>s</th>
    <td>Strings to iterate</td>
  </tr>
  <tr>
    <th>Keys</th>
    <td><code>key</code></td>
  </tr>
  <tr>
    <th>Key Names</th>
    <td><code>key_name</code></td>
  </tr>
  <tr>
    <th>Default <code>title_format</code></th>
    <td><code>&lt;&lt;key_name&gt;&gt;</code></td>
  </tr>
  <tr>
    <th>Default Template</th>
    <td><strong>None</strong></td>
  </tr>
</table>

### Example:

* Create a collection for the various Streaming Services
* Name the collection "[Key Name] Movies"

```yaml


templates:
  streaming:
    cache_builders: 1
    smart_label: release.desc
    sync_mode: sync
    mdblist_list: https://mdblist.com/lists/plexmetamanager/<<key>>-movies
    url_poster: https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Images/master/streaming/<<key_name_encoded>>.jpg

dynamic_collections:
  Streaming:
    type: custom
    data:
      all-4: All 4
      appletv: Apple TV+
      bet: BET+
      britbox: BritBox
      disney: Disney+
      max: Max
      hulu: Hulu
      netflix: Netflix
      now: NOW
      paramount: Paramount+
      peacock: Peacock
      amazon-prime-video: Prime Video
    title_format: <<key_name>> Movies
    template:
      - streaming
      - shared
```

## Exclude

Exclude this list of `keys` from being created into collections.

For example when making a `genre` dynamic collection definition you can exclude "Horror" from having a collection created from the key.

```yaml
dynamic_collections:
  Genres:         # mapping name does not matter, just needs to be unique
    type: genre
    exclude:
      - Horror
```

## Addons

Defines how multiple `keys` can be combined under a parent key.

For example, the `addons` attribute can be used to combine multiple `keys`, i.e. merging "MTV2", "MTV3" and "MTV (UK)" into the  "MTV" collection.

```yaml
dynamic_collections:
  networks:
    type: network
    addons:
      MTV:
        - MTV2
        - MTV3
        - MTV (UK)
```

You can also define custom keys under addons if the main key doesn't exist as a key it will be considered a custom key combining all keys into one key.

## Template

Name of the template to use for these dynamic collections. Each `type` has its own default template, but if you want to define and use your own template you can.

Each template is passed a few template variables you can use.
* `value`: The list of keys and addons
* `key`: The dynamic key
* `key_name`: The key after `key_name_override`, `remove_prefix`, or `remove_suffix` are run on it.

For example, the template below removes the limit on the `smart_filter` so it shows all items in each network

```yaml
templates:
  network collection:
    smart_filter:
      sort_by: critic_rating.desc
      all:
        network: <<value>>
dynamic_collections:
  Networks:         # mapping name does not matter just needs to be unique
    type: network
    title_format: <<key_name>>
    template: network collection
```

## Template Variables

Defines how template variables can be defined by key.

For example, when using `type: tmdb_collection` and you want to define a poster url for some collections

```yaml
templates:
  my_template:
    optional:
      - my_collection_poster
    tmdb_collection_details: <<value>>
    collection_order: release
    url_poster: <<my_collection_poster>>
dynamic_collections:
  TMDb Collections:          # This name is the mapping name
    type: tmdb_collection
    remove_suffix: "Collection"
    template: my_template
    template_variables:
      my_collection_poster:
        119: https://www.themoviedb.org/t/p/original/oENY593nKRVL2PnxXsMtlh8izb4.jpg
        531241: https://www.themoviedb.org/t/p/original/nogV4th2P5QWYvQIMiWHj4CFLU9.jpg
```

## Other Template

Name of the template to use for the other collection. Will use the same template as the rest of the dynamic collections unless specified.

Each template is passed a few template variables you can use.
* `value`: The list of keys and addons
* `key`: The dynamic key
* `key_name`: The key after `key_name_override`, `remove_prefix`, or `remove_suffix` are run on it.
* `included_keys`: The list of included keys
* `used_keys`: The list of all keys used (included_keys and their addon keys)

## Remove Prefix/Suffix

Removes the defined prefixes/suffixes from the key before it’s used in the collection title.

For example, when using `type: tmdb_collection` you may not want every collection title to end with `Collection`

```yaml
dynamic_collections:
  TMDb Collections:          # This name is the mapping name
    type: tmdb_collection
    remove_suffix: "Collection"
```

## Title Format

This is the format for the collection titles.

there are two special tags you can include in the `title_format`
* `<<key_name>>` is required and is what will be replaced by the dynamic key name.
* `<<library_type>>` will be replaced with either Movie, Show, or Artist depending on your library type.

Here's an example using `title_format`.

```yaml
dynamic_collections:
  Genres:         # mapping name does not matter just needs to be unique
    type: genre
    title_format: Top 50 <<key_name>> <<library_type>>s
```

## Key Name Override

Defines how key names can be overridden before they are formatted into collection titles.

This example uses the `key_name_override` attribute to change the formatting of "France" to "French" so that a collection can be named "French Cinema" instead of simply "France"
  * This particular example also uses the `title_format` attribute to manipulate the naming convention of the collections.

```yaml
dynamic_collections:
  Countries:         # mapping name does not matter, just needs to be unique
    type: country
    title_format: <<key_name>> Cinema
    key_name_override:
      France: French
```

## Title Override

Defines how collection titles can be overridden ignoring title formatting.

Here's an example using `title_override` that will override the TMDb Star Wars collection which has an TMDb ID of `10` with `Star Wars Universe.

```yaml
dynamic_collections:
  TMDb Collections:          # mapping name does not matter, just needs to be unique
    type: tmdb_collection
    remove_suffix: "Collection"
    title_override:
      10: Star Wars Universe
```

## Custom Keys

Defines if custom keys are allowed. Can be `true` or `false`. Defaults to `true`.

Here's an example using `custom_keys`.

```yaml
dynamic_collections:
  TMDb Collections:          # mapping name does not matter, just needs to be unique
    type: tmdb_collection
    remove_suffix: "Collection"
    custom_keys: false
```

## Test

Will add `test: true` to all collections for test runs.

Here's an example using `test`.

```yaml
dynamic_collections:
  Genres:         # mapping name does not matter just needs to be unique
    type: genre
    test: true
```

## Sync

Will remove dynamic collections that are no longer in the creation list.

The mapping name is added as a label to any collection created using dynamic and because of this when `sync` is true all collections with that label not found in this run will be deleted.

Here's an example using `sync`.

```yaml
dynamic_collections:
  Trakt Liked Lists:          # mapping name does not matter just needs to be unique
    type: trakt_liked_lists
    sync: true
```

## Include

Define a list of keys to be made into collections.

This cannot be used with `exclude`.

Here's an example using `include`.

```yaml
dynamic_collections:
  Genres:         # mapping name does not matter just needs to be unique
    type: genre
    include:
      - Action
      - Adventure
      - Animation
      - Comedy
      - Family
      - Fantasy
      - Horror
      - Romance
      - Science Fiction
      - War
```

## Other Name

Used in combination with `include`. When defined, all keys not in `include` or `addons` will be combined into this collection.

This is the main reason to use `include`. It allows a catch all collection for everything not defined in the config file.

Here's an example using `other_name`.

```yaml
dynamic_collections:
  Genres:         # mapping name does not matter just needs to be unique
    type: genre
    other_name: Top Other Movies
    include:
      - Action
      - Adventure
      - Animation
      - Comedy
      - Family
      - Fantasy
      - Horror
      - Romance
      - Science Fiction
      - War
```
