# Separators Default Metadata Files

Separators are a special form of collections which are used similar to index cards in a library, they help to "split up" collections by identifying categories (such as "Studio Collections" and "Holiday Collections").

These are empty collections which do not contain any movies/shows themselves, but highlight that the collections which follow it are of a certain category.

Below is an example of a separator, which can be seen surrounded by a red square.

![](images/separators.jpg)

## Important Note:

Plex does not support creating these empty collections natively through its UI, so they can behave strangely in some cases, primarily related to showing/hiding them in the main library view.  As a workaround, you can use a `placeholder_` [template variable](#shared-separator-variables) to specify a single movie/show to add to these collections so they have one thing in them and will then behave as expected.  For example, `placeholder_imdb_id: tt0068646` will place The Godfather inside the separator in a movie library.

## Separator Files

These are all the files that contain a separator 

| Collection Name               | Default File        |
|-------------------------------|:--------------------|
| Seasonal Collections          | `seasonal`          |
| Chart Collections             | `separator_chart`   |
| Universe Collections          | `universe`          |
| Streaming Collections         | `streaming`         |
| Network Collections           | `network`           |
| Genre Collections             | `genre`             |
| Studio Collections            | `studio`            |
| Country Collections           | `country`           |
| Audio Language Collections    | `audio_language`    |
| Subtitle Language Collections | `subtitle_language` |
| Decade Collections            | `decade`            |
| Year Collections              | `year`              |
| Ratings Collections           | `content_rating*`   |
| Resolution Collections        | `resolution*`       |
| Award Collections             | `separator_award`   |
| Actors Collections            | `actor`             |
| Directors Collections         | `director`          |
| Producers Collections         | `producer`          |
| Writers Collections           | `writer`            |
| Based On... Collections       | `based`             |

## Shared Separator Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

**[Shared Variables](collection_variables) are NOT available to separator collections in any default file.**

| Variable                 | Description & Values                                                                                                                                                                                                                                                                                                                                                                  |
|:-------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_separator`          | **Description:** Turn the [Separator Collection](#use-separators) off.<br>**Values:** `false` to turn of the collection                                                                                                                                                                                                                                                               |
| `sep_style`              | **Description:** Choose the [Separator Style](#separator-styles).<br>**Default:** `orig`<br>**Values:** `amethyst`, `aqua`, `blue`, `forest`, `fuchsia`, `gold`, `gray`, `green`, `navy`, `ocean`, `olive`, `orchid`, `orig`, `pink`, `plum`, `purple`, `red`, `rust`, `salmon`, `sand`, `stb`, or `tan`                                                                           |         
| `sort_prefix`            | **Description:** Changes the prefix of the sort title.<br>**Default:** `!`<br>**Values:** Any String                                                                                                                                                                                                                                                                                  |
| `sort_title`             | **Description:** Changes the sort title of all collections.<br>**Default:** `<<sort_prefix>><<collection_section>>_!<<title>>`<br>**Values:** Any String                                                                                                                                                                                                                              |
| `placeholder_tmdb_movie` | **Description:** Add a placeholder Movie to the Separator.  Only valid for Movie libraries.<br>**Values:** TMDb Movie ID                                                                                                                                                                                                                                                              |
| `placeholder_tvdb_show`  | **Description:** Add a placeholder Show to the Separator.  Only valid for Show libraries.<br>**Values:** TVDb Show ID                                                                                                                                                                                                                                                                 |
| `placeholder_imdb_id`    | **Description:** Add a placeholder Movie/Show to the Separator.  Valid for Movie or Show libraries assuming the ID points to an item of the correct type.<br>**Values:** IMDb ID                                                                                                                                                                                                      |
| `name_separator`         | **Description:** Changes the name of the specified key's collection.<br>**Values:** New Collection Name                                                                                                                                                                                                                                                                               |
| `summary_separator`      | **Description:** Changes the summary of the specified key's collection.<br>**Values:** New Collection Summary                                                                                                                                                                                                                                                                         |
| `collection_section`     | **Description:** Changes the sort order of the collection sections against other default collection sections.<br>**Values:** Any number                                                                                                                                                                                                                                               |
| `collection_mode`        | **Description:** Controls the collection mode of all collections in a Defaults file.<br>**Values:**<table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table> |
| `url_poster_separator`   | **Description:** Changes the poster url of the specified key's collection.<br>**Values:** URL directly to the Image                                                                                                                                                                                                                                                                   |

## Use Separators

Separators are enabled by default, but can be disabled/enabled per-file and per-library.

An example of disabling separators at the library-level can be seen here

```yaml
libraries:
  Movies:
    template_variables:
      use_separator: false
```

And at the file-level

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio
        template_variables:
          use_separator: false
```

## Separator Styles

Multiple styles are available for Separators, to match Plex's "categories" feature.

The available styles available are:

| Style    | Value      |
|:---------|:-----------|
| Original | `orig`     |  
| Amethyst | `amethyst` |  
| Aqua     | `aqua`     |   
| Blue     | `blue`     |  
| Forest   | `green`    | 
| Fuchsia  | `fuchsia`  |
| Gold     | `gold`     |   
| Gray     | `gray`     |  
| Green    | `green`    |   
| Navy     | `navy`     |  
| Ocean    | `ocean`    | 
| Olive    | `olive`    |
| Orchid   | `orchid`   |   
| Pink     | `pink`     |  
| Plum     | `plum`     |   
| Purple   | `purple`   |  
| Red      | `red`      | 
| Rust     | `rust`     |
| Salmon   | `salmon`   |   
| Sand     | `sand`     |  
| Brown    | `stb`      |   
| Tan      | `tan`      |  

This image shows an example separator in each of the above styles

![](images/separators2.jpg)

An example of changing the separator style at the library-level can be seen here

```yaml
libraries:
  Movies:
    template_variables:
      sep_style: red
```

And at the file-level

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio
        template_variables:
          sep_style: stb
```
