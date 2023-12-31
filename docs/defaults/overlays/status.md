# Status Overlay

The `status` Default Overlay File is used to create an overlay on a show detailing its Current Airing Status for all shows in your library.

![](images/status.png)

## Requirements & Recommendations

Supported Overlay Level: Show

## Supported Status

| Status    | Key         | Weight |
|:----------|:------------|:-------|
| AIRING    | `airing`    | `40`   |
| RETURNING | `returning` | `30`   |
| CANCELED  | `canceled`  | `20`   |
| ENDED     | `ended`     | `10`   |

## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  TV Shows:
    overlay_files:
      - pmm: status
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Overlay Template Variables" tab for additional variables.

        | Variable                     | Default / Values                                                                                                                                                                                                                                                                                                                                    |
        |:-----------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `horizontal_offset`          | `15`                                                                                                                                                                                                                                                                                                                                                |
        | `horizontal_align`           | `left`                                                                                                                                                                                                                                                                                                                                              |
        | `vertical_offset`            | `330`                                                                                                                                                                                                                                                                                                                                               |
        | `vertical_align`             | `top`                                                                                                                                                                                                                                                                                                                                               |
        | `back_color`                 | `#00000099`                                                                                                                                                                                                                                                                                                                                         |
        | `back_radius`                | `30`                                                                                                                                                                                                                                                                                                                                                |
        | `back_width`                 | `305`                                                                                                                                                                                                                                                                                                                                               |
        | `back_height`                | `105`                                                                                                                                                                                                                                                                                                                                               |
        | `last`                       | **Description:** Episode Air Date in the last number of days for the AIRING Overlay.<br>**Default:** `14`<br>**Values:** Any number greater than 0                                                                                                                                                                                                  |
        | `text_<<key>>`<sup>1</sup>   | **Description:** Choose the text for the Overlay.<br>**Default:** <table class="clearTable"><tr><th>Key</th><th>Default</th></tr><tr><td>`airing`</td><td>`AIRING`</td></tr><tr><td>`returning`</td><td>`RETURNING`</td></tr><tr><td>`canceled`</td><td>`CANCELED`</td></tr><tr><td>`ended`</td><td>`ENDED`</td></tr></table>**Values:** Any String |
        | `weight_<<key>>`<sup>1</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number                                                                                                                                                                                                                                        |

        1. Each default overlay has a `key` that when calling to effect a specific overlay you must replace `<<key>>` with when calling.

    === "Overlay Template Variables"

        {%
           include-markdown "../overlay_text_variables.md"
        %}

        {%
           include-markdown "../overlay_variables.md"
        %}

    ### Example Template Variable Amendments

    The below is an example config.yml extract with some Template Variables added in to change how the file works.


    ```yaml
    libraries:
      TV Shows:
        overlay_files:
          - pmm: status
            template_variables:
              text_canceled: "C A N C E L L E D"
    ```
