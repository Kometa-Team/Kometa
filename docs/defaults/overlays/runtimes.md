# Runtimes Overlay

The `runtimes` Default Overlay File is used to create an overlay of the movie runtime, episode runtime, or average episode runtime for all items in your library.

![](images/runtimes.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show, Season, Episode

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_files:
      - pmm: runtimes
  TV Shows:
    overlay_files:
      - pmm: runtimes
      - pmm: runtimes
        template_variables:
          builder_level: episode
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

| Variable            | Default / Values                                                                                                                         |
|:--------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|
| `horizontal_offset` | `15`                                                                                                                                     |
| `horizontal_align`  | `right`                                                                                                                                  |
| `vertical_offset`   | `30`                                                                                                                                     |
| `vertical_align`    | `bottom`                                                                                                                                 |
| `back_color`        | `#00000099`                                                                                                                              |
| `back_radius`       | `30`                                                                                                                                     |
| `back_width`        | `600`                                                                                                                                    |
| `back_height`       | `105`                                                                                                                                    |
| `text`              | **Description:** Choose the text that appears prior to the runtime on the Overlay.<br>**Default:** `Runtime: `<br>**Values:** Any String |

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
  TV Shows:
    overlay_files:
      - pmm: runtimes
        template_variables:
          builder_level: episode
        font: fonts/Inter-Bold.ttf
```
