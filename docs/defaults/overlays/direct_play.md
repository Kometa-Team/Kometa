# Direct Play Overlay

The `direct_play` Default Overlay File is used to create an overlay to indicate items that cannot be transcoded and instead only support Direct Play (i.e. if you use Tautulli to kill 4K transcoding)

![](images/direct_play.png)

## Requirements & Recommendations

Supported library types: Movie & Show

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: direct_play
  TV Shows:
    overlay_path:
      - pmm: direct_play
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

| Variable            | Default / Values                                                                |
|:--------------------|:--------------------------------------------------------------------------------|
| `horizontal_offset` | `0`                                                                             |
| `horizontal_align`  | `center`                                                                        |
| `vertical_offset`   | `150`                                                                           |
| `vertical_align`    | `bottom`                                                                        |
| `back_color`        | `#00000099`                                                                     |
| `back_radius`       | `30`                                                                            |
| `back_width`        | `305`                                                                           |
| `back_height`       | `170`                                                                           |
| `builder_level`     | **Description:** Choose the Overlay Level.<br>**Values:** `season` or `episode` |

{%
   include-markdown "../overlay_variables.md"
%}

{%
   include-markdown "../overlay_text_variables.md"
%}

## Example Template Variable Amendments

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: direct_play
        template_variables:
          builder_level: episode
```
