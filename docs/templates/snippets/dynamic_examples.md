## Dynamic Collection Examples

???+ example

    ```yaml
    templates:
      genre collection: #(4)!
        smart_filter:
          limit: 100
          sort_by: critic_rating.desc
          all:
            genre: <<value>>
    dynamic_collections:
      Genres:
        type: genre #(1)!
        exclude: #(2)!
          - Talk Show
        template: genre collection #(3)!
    ```
    
    1. Uses the `genre` type to create dynamic collections based on each genre found in the library.
    2. Uses `exclude` to exclude the `Talk Show` genre.
    3. Uses the template called `genre collection` for these collections.
    4. This is the same template as the default for `genre` but the `limit` has been increased to 100 from 50.

#### Example:

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



#### Example:

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



#### Example

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




#### Example:

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




#### Example:

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



#### Example:

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




#### Example:

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


#### Example:

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


#### Example:

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




#### Example:

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



#### Example:

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
