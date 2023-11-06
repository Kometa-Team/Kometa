# Music Library Metadata

You can have the script edit the metadata of Artists, Albums, and Tracks by adding them to the `metadata` mapping of a Metadata File.

An example of multiple metadata edits in a music library is below:

```yaml
metadata:
  "Linkin Park":
    country: "United States of America"
    album_sorting: newest
    albums:
      "Hybrid Theory":
        originally_available: "2000-10-24"
        tracks:
          1:
            user_rating: 5
          "One Step Closer":
            user_rating: 5
      "Meteora":
        originally_available: "2003-03-25"
        album_sorting: newest
        tracks:
          9:
            user_rating: 5
          "Numb":
            user_rating: 5
      "Minutes To Midnight":
        originally_available: "2007-05-14"
```

## Matching Artist

The `match` attribute is used to match artists within Plex to that definition within the Metadata file. One definition can match and edit multiple artists. The available matching options are outlined below.

| Attribute                      | Allowed Values                                                                                       |
|:-------------------------------|:-----------------------------------------------------------------------------------------------------|
| `title`<sup>1</sup>            | Only matches artists that exactly match the artist's Title. Can be a list (only one needs to match). |

1. When `title` is not provided and the mapping name was not specified as an ID, the default behaviour is to use the mapping name as `title` for matching.

### Examples

Below are some examples on how artists can be matched.

#### Example 1 - `title`

The below example shows how `title` can be used to match artists.

```yaml
metadata:
  artist1:                   # Matches via the title "Ke$ha"
    match:
      title: Ke$ha
    edits...
  artist2:                   # Matches via the title "311" 
    match:
      title: 311
    edits...
```

The Mapping Name can also be used to reduce line-count, as shown here:

```yaml
metadata:
  Ke$ha:             # Matches via the Name "Ke$ha"
    edits...
  "311":             # Matches via the Name "311" 
    edits...
```

## Metadata Edits

The available attributes for editing artists, albums, and tracks are as follows

### Special Attributes

| Attribute   | Values                                                                                                                | Artists  |  Album   |  Tracks  |
|:------------|:----------------------------------------------------------------------------------------------------------------------|:--------:|:--------:|:--------:|
| `albums`    | Attribute used to edit album metadata. The mapping name is the album name.                                            | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |
| `tracks`    | Attribute used to edit track metadata. The mapping name is the track number on that Album, or the title of the Track. | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |

* If you know of another Title your item might exist under, but you want it titled differently you can use `alt_title` to specify another title to look under and then be changed to the mapping name. For Example the Artist `Kesha` used to be stylized as `Ke$ha`, and might still be found that way in Metadata results.
    ```yaml
    metadata:
      "Kesha":
        alt_title: "Ke$ha"
    ```
    This would change the name of the default `Ke$ha` to `Kesha` and would not mess up any subsequent runs.
``
### General Attributes

| Attribute              | Values                                                                                                                                                                                                                                          | Artists  |  Album   |  Tracks  |
|:-----------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|:--------:|:--------:|
| `title`                | Text to change Title.                                                                                                                                                                                                                           | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  |
| `sort_title`           | Text to change Sort Title.                                                                                                                                                                                                                      | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| `user_rating`          | Number to change User Rating.                                                                                                                                                                                                                   | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| `critic_rating`        | Number to change Critic Rating.                                                                                                                                                                                                                 | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| `originally_available` | Date to change Originally Available.<br>**Format:** YYYY-MM-DD                                                                                                                                                                                  | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| `record_label`         | Text to change Record Label.                                                                                                                                                                                                                    | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| `summary`              | Text to change Summary.                                                                                                                                                                                                                         | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| `track`                | Text to change Track.                                                                                                                                                                                                                           | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  |
| `disc`                 | Text to change Disc.                                                                                                                                                                                                                            | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  |
| `original_artist`      | Text to change Original Artist.                                                                                                                                                                                                                 | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green }  |
| `run_definition`       | Used to specify if this definition runs.<br>Multiple can be used for one definition as a list or comma separated string. One `false` or unmatched library type will cause it to fail.<br>**Values:** `movie`, `show`, `artist`, `true`, `false` | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |

### Tag Attributes

You can add `.remove` to any tag attribute to only remove those tags i.e. `genre.remove`.

You can add `.sync` to any tag attribute to sync all tags vs just appending the new ones i.e. `genre.sync`.

| Attribute        | Values                                                   | Artists  |  Album   |  Tracks  |
|:-----------------|:---------------------------------------------------------|:--------:|:--------:|:--------:|
| `genre`          | List or comma-separated text of each Genre Tag.          | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| `collection`     | List or comma-separated text of each Collection Tag.     | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| `label`          | List or comma-separated text of each Label Tag.          | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| `style`          | List or comma-separated text of each Style Tag.          | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } |
| `mood`           | List or comma-separated text of each Mood Tag.           | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-check:{ .green }  |
| `country`        | List or comma-separated text of each Country Tag.        | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |
| `similar_artist` | List or comma-separated text of each Similar Artist Tag. | :fontawesome-solid-circle-check:{ .green }  | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-xmark:{ .red } |

### Image Attributes

| Attribute         | Values                                           | Artists |  Album  |  Tracks  |
|:------------------|:-------------------------------------------------|:-------:|:-------:|:--------:|
| `url_poster`      | URL of image publicly available on the internet. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| `file_poster`     | Path to image in the file system.                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| `url_background`  | URL of image publicly available on the internet. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |
| `file_background` | Path to image in the file system.                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } |

### Advanced Attributes

All these attributes only work with Artists.

| Attribute       | Values                                                                                                                                                                                                                                           |
|:----------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `album_sorting` | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`oldest`</td><td>Oldest first</td></tr><tr><td>`newest`</td><td>Newest first</td></tr><tr><td>`name`</td><td>Alphabetical</td></tr></tbody></table>  |
