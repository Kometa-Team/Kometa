---
hide:
  - toc
---
# Configuration Files

Kometa is configured via YAML files. These files are used to define the various components of Kometa. 
The configuration files are stored in the `/config` directory of the Kometa container.

There is one required configuration file, `config.yml`, and several optional configuration files. 

## `config.yml`

[`config.yml`](../../config/overview.md) is the main [and only required] configuration file for Kometa. This is where you configure global settings like your Plex server details, 
the libraries you want Kometa to act on, any external services you want to use, and other global settings.

Collections, overlays, and metadata changes are **not** defined in `config.yml`. These are defined in separate files.

Generally speaking, things that are documented as being part of the `config.yml` file can only be in the `config.yml` file. 
Things that are documented as being in other files can only be in those files.

There are a few exceptions to this general rule, but those exceptions are for the most part *settings* that override values that have been specified in the `config.yml`. 
For example, `config.yml` contains a default `collection_order`, and a Collection File can override that order. 
"Larger" things like collection definitions can only be in collection files.

### The Kometa Defaults

One thing that seems like a bit of an exception are the [defaults](../../defaults/guide.md). These are linked with libraries in the `config.yml` file 
and are customized with Template Variables in the `config.yml` file, a system which is generally unique to the defaults.

There are Defaults Files that create collections, overlays, and playlists. There are no default metadata files.

The Defaults Files are referenced in the `config.yml` under a library with the `default` file type:

```yaml
libraries:
  Movies:
    collection_files:
      - default: imdb
      - default: genre
    overlay_files:
      - default: resolution
      - default: ribbon
```

Typically, the Defaults Files can be customized with Template Variables:

```yaml
libraries:
  Movies:
    collection_files:
      - default: imdb
        template_variables:
          use_lowest: false 
      - default: genre
        template_variables:
          sep_style: red 
    overlay_files:
      - default: resolution
        template_variables:
          use_576p: false
          use_480p: false
      - default: ribbon
        template_variables:
          style: black
          weight_metacritic: 35
          use_common: false
```

The specifics of what Template Variables are available for a given default are found on the wiki page for each default, which you can find starting [here](../../defaults/guide.md).

Like the rest of the [external files](../../files/overview.md), these default references cannot be moved out of the `config.yml` file.

???+ tip

    Why can't I move the Defaults Files out of the `config.yml` file?

    This:
    ```yaml
        - default: whatever
    ```
    is shorthand for:
    ```yaml
        - file: internal/path/to/whatever.yml
    ```
    So, like any other file reference [`file`,`folder`,`url`,`git`,`repo`], it can't be moved out of the `config.yml` file.

## Collection files

Collections are defined in [separate collection files](../../files/collections.md). They can be used to create collections of movies, TV shows, or music.
They can also be used to apply labels or make other changes to items based on [builders](../../files/builders/overview.md) without actually creating collections.

A Collection File can contain one or more collections.

Collection files are optional; you may not want or need any of your own if you are leveraging the Defaults Files.

The simplest Collection File would look like this:

```yaml
collections: 
  Top 50 Grossing Films of All Time (Worldwide):
    tmdb_list: 10 
```

One collection with a name and a [Builder](../../files/builders/overview.md) that defines the criteria for the collection.

That would go in a file like `config/my-neat-collection.yml` and be referenced in the `config.yml` file like this:

```yaml
libraries:
  Movies:
    collection_files:
      - file: config/my-neat-collection.yml
```

## Overlay files

The next most frequently used file type is the [Overlay File](../../files/overlays.md). Overlays are used to apply graphic overlays to your posters in Plex.

A minimal Overlay File would look like this:

```yaml
overlays:
  4K:
    plex_search:
      all:
        resolution: 4K
```

One overlay with a name and a [Builder](../../files/builders/overview.md) that defines the criteria for the collection.

This would go in a file like `config/my-neat-overlay.yml` and be referenced in the `config.yml` file like this:

```yaml
libraries:
  Movies:
    overlay_files:
      - file: config/my-neat-overlay.yml
```

## Metadata files

Probably the most uncommon library-level file type is the [Metadata File](../../files/metadata.md). Metadata files are used to apply metadata changes to your items in Plex; 
these are things like changing the year, the title, the artwork, the summary, etc.

Metadata files don't use builders; they use a different format. A minimal Metadata File would look like this:

```yaml
metadata:
  Godzilla (1954):
    match:
      title: Godzilla
      year: 1954
    content_rating: R
```

One metadata change [`content_rating`] with a name and a match criteria.

Metadata files use the criteria in the `match` key to find individual items (like this one which finds a movie titled "Godzilla" released in 1954), 
and then the specified changes [in this case setting the content rating to `R`] are applied to the [probably one] thing that matches the criteria.

This would go in a file like `config/my-neat-metadata.yml` and be referenced in the `config.yml` file like this:

```yaml
libraries:
  Movies:
    metadata_files:
      - file: config/my-neat-metadata.yml
```

## Playlist files

Playlists are defined in [separate playlist files](../../files/playlists.md). They can be used to create playlists of movies, TV shows, or music.

Playlists are defined in a similar way to collections, but they can span libraries, where collections are library-specific.

A playlist file can contain one or more playlists.

The simplest playlist file would look like this:

```yaml
playlists: 
  Marvel Cinematic Universe Chronological Order:
    trakt_list: https://trakt.tv/users/donxy/lists/marvel-cinematic-universe
```

One playlist with a name and a [Builder](../../files/builders/overview.md) that produces the list of items to put in the playlist.

Kometa defaults to pulling items for the playlist from two libraries with specific names: `Movies` and `TV Shows`. 
If you want to pull from different libraries [if, for example your libraries are *not* named `Movies` and `TV Shows`], you can specify that in the playlist file.

```yaml
playlists: 
  Marvel Cinematic Universe Chronological Order:
    libraries: My Movie Library, My TV Library, My 4K Library  
    trakt_list: https://trakt.tv/users/donxy/lists/marvel-cinematic-universe
```

This would go in a file like `config/my-neat-playlist.yml` and be referenced in the `config.yml` file like this:

```yaml
libraries:
  Movies:
    ...
  TV Shows:
    ...
playlist_files:
  - file: config/my-neat-playlist.yml
```

Note that the `playlist_files` key is at the top level of the `config.yml` file, not under a specific library. This is because playlists can span libraries.
