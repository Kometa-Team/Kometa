# Separators Default Metadata Files

Separators are a special form of collections which are used similar to index cards in a library, they help to "split up" collections by identifying categories (such as "Studio Collections" and "Holiday Collections").

These are empty collections which do not contain any movies/shows themselves, but highlight that the collections which follow it are of a certain category.

Below is an example of a separator, which can be seen surrounded by a red square.

![](images/separators.jpg)

Separators are enabled by default, but can be disabled/enabled per-file and per-library.

An example of disabling separators at the library-level cam be seen here

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

## Separator Files

These are all the files that contain a separator.

| Collection Name                   | Default File        | Collection Section |
|:----------------------------------|:--------------------|:------------------:|
| Seasonal Collections              | `seasonal`          |        `00`        |
| Chart Collections                 | `separator_chart`   |        `01`        |
| Universe Collections              | `universe`          |        `02`        |
| Streaming Collections             | `streaming`         |        `03`        |
| Network Collections               | `network`           |        `04`        |
| Genre Collections                 | `genre`             |        `06`        |
| Studio Collections                | `studio`            |        `07`        |
| Country Collections               | `country`           |        `09`        |
| Audio Language Collections        | `audio_language`    |        `10`        |
| Subtitle Language Collections     | `subtitle_language` |        `11`        |
| Decade Collections                | `decade`            |        `12`        |
| Year Collections                  | `year`              |        `13`        |
| Ratings Collections               | `content_rating*`   |        `14`        |
| Resolution Collections            | `resolution*`       |        `15`        |
| Award Collections                 | `separator_award`   |        `16`        |
| Actors Collections                | `actor`             |        `17`        |
| Directors Collections             | `director`          |        `18`        |
| Producers Collections             | `producer`          |        `19`        |
| Writers Collections               | `writer`            |        `20`        |

## Alternative Styles

Multiple styles are available for Separators, to match Plex's "categories" feature.

The available styles avaiable are:

| Style           | Value  |
|:----------------|:-------|
| Original        | orig   |
| Blue            | blue   |
| Brown           | stb    |
| Gray            | gray   |
| Green           | green  |
| Purple          | purple |
| Red             | red    |

This image shows an example separator in each of the above styles

![](images/separators2.jpg)

The style of separator can be defined per-file and per-library.

An example of disabling separators at the library-level cam be seen here

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


