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

## Artist

Each artist is defined by the mapping name which must be the same as the artist name in the library unless an `alt_title` is specified.

### Albums

To edit the metadata of a particular Album for an Artist use the `albums` attribute on its artist.

The mapping name is the album name.

### Tracks

To edit the metadata of a particular Track on an Album use the `tracks` attribute on its album.

The mapping name is the track number on that Album, or the title of the Track.

## Metadata Edits

The available attributes for editing artists, albums, and tracks are as follows

### Special Attributes

| Attribute   | Values                        | Artists  |  Album   |  Tracks  |
|:------------|:------------------------------|:--------:|:--------:|:--------:|
| `alt_title` | Alternative title to look for | &#9989;  | &#9989;  | &#9989;  |
| `albums`    | Mapping to define Albums      | &#9989;  | &#10060; | &#10060; |
| `tracks`    | Mapping to define Tracks      | &#10060; | &#9989;  | &#10060; |

* If you know of another Title your item might exist under, but you want it titled differently you can use `alt_title` to specify another title to look under and then be changed to the mapping name. For Example the Artist `Kesha` used to be stylized as `Ke$ha`, and might still be found that way in Metadata results.
    ```yaml
    metadata:
      "Kesha":
        alt_title: "Ke$ha"
    ```
    This would change the name of the default `Ke$ha` to `Kesha` and would not mess up any subsequent runs.
``
### General Attributes

| Attribute              | Values                                                        | Artists  |  Album   |  Tracks  |
|:-----------------------|:--------------------------------------------------------------|:--------:|:--------:|:--------:|
| `title`                | Text to change Title                                          | &#10060; | &#10060; | &#9989;  |
| `sort_title`           | Text to change Sort Title                                     | &#9989;  | &#9989;  | &#9989;  |
| `user_rating`          | Number to change User Rating                                  | &#9989;  | &#9989;  | &#9989;  |
| `critic_rating`        | Number to change Critic Rating                                | &#10060; | &#9989;  | &#10060; |
| `originally_available` | Date to change Originally Available<hr>**Format:** YYYY-MM-DD | &#10060; | &#9989;  | &#10060; |
| `record_label`         | Text to change Record Label                                   | &#10060; | &#9989;  | &#10060; |
| `summary`              | Text to change Summary                                        | &#9989;  | &#9989;  | &#9989;  |
| `track`                | Text to change Track                                          | &#10060; | &#10060; | &#9989;  |
| `disc`                 | Text to change Disc                                           | &#10060; | &#10060; | &#9989;  |
| `original_artist`      | Text to change Original Artist                                | &#10060; | &#10060; | &#9989;  |

### Tag Attributes

You can add `.remove` to any tag attribute to only remove those tags i.e. `genre.remove`.

You can add `.sync` to any tag attribute to sync all tags vs just appending the new ones i.e. `genre.sync`.

| Attribute        | Values                                                  | Artists  |  Album   |  Tracks  |
|:-----------------|:--------------------------------------------------------|:--------:|:--------:|:--------:|
| `genre`          | List or comma-separated text of each Genre Tag          | &#9989;  | &#9989;  | &#10060; |
| `collection`     | List or comma-separated text of each Collection Tag     | &#9989;  | &#9989;  | &#9989;  |
| `label`          | List or comma-separated text of each Label Tag          | &#10060; | &#9989;  | &#10060; |
| `style`          | List or comma-separated text of each Style Tag          | &#9989;  | &#9989;  | &#10060; |
| `mood`           | List or comma-separated text of each Mood Tag           | &#9989;  | &#9989;  | &#9989;  |
| `country`        | List or comma-separated text of each Country Tag        | &#9989;  | &#10060; | &#10060; |
| `similar_artist` | List or comma-separated text of each Similar Artist Tag | &#9989;  | &#10060; | &#10060; |

### Image Attributes

| Attribute         | Values                                          | Artists |  Album  |  Tracks  |
|:------------------|:------------------------------------------------|:-------:|:-------:|:--------:|
| `url_poster`      | URL of image publicly available on the internet | &#9989; | &#9989; | &#10060; |
| `file_poster`     | Path to image in the file system                | &#9989; | &#9989; | &#10060; |
| `url_background`  | URL of image publicly available on the internet | &#9989; | &#9989; | &#10060; |
| `file_background` | Path to image in the file system                | &#9989; | &#9989; | &#10060; |

### Advanced Attributes

All these attributes only work with Artists.

| Attribute       | Values                                                                                                                                                                                                                                           |
|:----------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `album_sorting` | <table class="clearTable"><tbody><tr><td>`default`</td><td>Library default</td></tr><tr><td>`oldest`</td><td>Oldest first</td></tr><tr><td>`newest`</td><td>Newest first</td></tr><tr><td>`name`</td><td>Alphabetical</td></tr></tbody></table>  |

