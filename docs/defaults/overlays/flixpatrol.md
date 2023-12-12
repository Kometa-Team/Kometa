# FlixPatrol Top Overlays

The `flixpatrol` Default Overlay File is used to create an overlay based on the Top Lists from FlixPatrol on items within your library.

![](images/flixpatrol.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show

## Supported Services

| Service     | Key         | Weight |
|:------------|:------------|:-------|
| Netflix     | `netflix`   | `60`   |
| Disney+     | `disney`    | `50`   |
| MAX         | `max`       | `40`   |
| Hulu        | `hulu`      | `30`   |
| Paramount+  | `paramount` | `20`   |
| Prime Video | `prime`     | `10`   |
| Apple+      | `apple`     | `9`    |

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_files:
      - pmm: flixpatrol
  TV Shows:
    overlay_files:
      - pmm: flixpatrol
```

## Template Variable Default Values

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

 
| Variable                       | Default / Values                                                                                                                                                                                               |
|:-------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `horizontal_offset`            | `30`                                                                                                                                                                                                           |
| `horizontal_align`             | `left`/`right`                                                                                                                                                                                                 |
| `vertical_offset`              | `465`/`670`/`875`                                                                                                                                                                                              |
| `vertical_align`               | `top`                                                                                                                                                                                                          |
| `back_color`                   | `#00000099`                                                                                                                                                                                                    |
| `back_radius`                  | `30`                                                                                                                                                                                                           |
| `back_width`                   | `160`                                                                                                                                                                                                          |
| `back_height`                  | `160`                                                                                                                                                                                                          |
| `back_padding`                 | `15`                                                                                                                                                                                                           |
| `position`                     | **Description:** Changes the position of the Overlays.<br>**Default:** `right`<br>**Values:** `right`, `left`, or List of Coordinates                                                                          |
| `style`                        | **Description:** Changes the style of the Logo Image.<br>**Default:** `round`<br>**Values:** `round` or `square`                                                                                               |
| `pre_text`                     | **Description:** Changes the text before the number.<br>**Default:** `TOP`<br>**Values:** Any String                                                                                                           |
| `limit`                        | **Description:** Changes the Builder Limit for all overlays in a Defaults file.<br>**Default:** `10`<br>**Values:** Any Number 1-10                                                                            |
| `limit_<<key>>`<sup>1</sup>    | **Description:** Changes the Builder Limit of the specified key's overlay.<br>**Default:** `limit`<br>**Values:** Any Number 1-10                                                                              |
| `location`                     | **Description:** Changes the Builder Location for all overlays in a Defaults file.<br>**Default:** `world`<br>**Values:** [`location` Attribute Options](../../builders/flixpatrol.md#top-platform-attributes) |
| `location_<<key>>`<sup>1</sup> | **Description:** Changes the Builder Location of the specified key's overlay.<br>**Default:** `location`<br>**Values:** [`location` Attribute Options](../../builders/flixpatrol.md#top-platform-attributes)   |
| `in_the_last`                          | **Description:** Changes How many days of daily Top 10 Lists to look at.<br>**Default:** `1`<br>**Values:** Any Number 1-30                                                                            |
| `in_the_last_<<key>>`<sup>1</sup>      | **Description:** Changes How many days of daily Top 10 Lists to look at.<br>**Default:** `in_the_last`<br>**Values:** Any Number 1-30                                                                  |
| `weight_<<key>>`<sup>1</sup>   | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number                                                                                                   |
| `addon_offset`                 | **Description:** Text Addon Image Offset from the text.<br>**Default:** `30`<br>**Values:** Any Number greater then 0                                                                                          |
| `addon_position`               | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `top`<br>**Values:** `left`, `right`, `top`, `bottom`                                                                     |

1. Each default overlay has a `key` that when calling to effect a specific overlay you must replace `<<key>>` with when calling.

{%
   include-markdown "../overlay_variables.md"
   end="Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored."
%}

???+ bug "Warning"

    `horizontal_offset`, `horizontal_align`, `vertical_offset`, and `vertical_align` are NOT available for use in this file

{%
   include-markdown "../overlay_variables.md"
   start="The below template variables are available for this PMM Defaults file."
%}

{%
   include-markdown "../overlay_text_variables.md"
%}

## Example Template Variable Amendments

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_files:
      - pmm: flixpatrol
        template_variables:
          location: united_states
```
