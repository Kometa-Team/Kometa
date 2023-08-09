# Ribbon Overlays

The `ribbon` Default Overlay File is used to create a ribbon overlay based on the Top Lists of various sites on each item within your library.

![](images/ribbon.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show

## Supported Ribbon

| Ribbon                          | Key               | Weight |
|:--------------------------------|:------------------|:-------|
| Oscars Best Picture             | `oscars`          | `50`   |
| Oscars Best Director            | `oscars_director` | `45`   |
| IMDb Top 250                    | `imdb`            | `40`   |
| Rotten Tomatoes Certified Fresh | `rotten`          | `30`   |
| Metacritic Must See             | `metacritic`      | `20`   |
| Commonsense Selection           | `common`          | `10`   |
| Golden Globe Winner             | `golden`          | `6`    |
| Emmys Winner                    | `emmys`           | `4`    |
| Razzies Winner                  | `razzie`          | `2`    |
## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: ribbon
  TV Shows:
    overlay_path:
      - pmm: ribbon
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Overlay Variables](../overlay_variables) are available with the default values below as well as the additional Variables below which can be used to customize the file.

| Variable            | Default   |
|:--------------------|:----------|
| `horizontal_offset` | `0`       |
| `horizontal_align`  | `right`   |
| `vertical_offset`   | `0`       |
| `vertical_align`    | `bottom`  |

| Variable                     | Description & Values                                                                                                    |
|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------|
| `weight_<<key>>`<sup>1</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number            |
| `style`                      | **Description:** Controls the color of the ribbon. <br>**Default:** `yellow` <br>**Values:** `yellow, gray, black, red` |

1. Each default overlay has a `key` that when calling to effect a specific overlay you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: ribbon
        template_variables:
          style: black
          weight_metacritic: 35
          use_common: false
```
