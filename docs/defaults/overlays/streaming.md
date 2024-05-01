# Streaming Services Overlay

The `streaming` Default Overlay File is used to create an overlay based on the streaming service the file is found on 
for each item within your library.

![](images/streaming.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show

## Supported Streaming Services

| Streaming Service | Key           | Weight |
|:------------------|:--------------|:-------|
| Netflix           | `netflix`     | `160`  |
| Prime Video       | `amazon`      | `150`  |
| Disney+           | `disney`      | `140`  |
| Max               | `max`         | `130`  |
| Crunchyroll       | `Crunchyroll` | `120`  |
| YouTube           | `youtube`     | `110`  |
| Hulu              | `hulu`        | `100`  |
| Paramount+        | `paramount`   | `90`   |
| AppleTV           | `appletv`     | `80`   |
| Peacock           | `peacock`     | `70`   |
| Showtime          | `showtime`    | `60`   |
| discovery+        | `discovery`   | `58`   |
| Crave             | `crave`       | `55`   |
| NOW               | `now`         | `50`   |
| All 4             | `all4`        | `40`   |
| britbox           | `britbox`     | `30`   |
| BET+              | `bet`         | `20`   |
| hayu              | `hayu`        | `10`   |


## Regional Variants

Some logic is applied to allow for regional streaming service lists to be available to users depending on where they 
are, as detailed below:

| Region           | Key                              | Description                                                                                                                         |
|:-----------------|:---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| any besides `GB` | `all4`, `britbox`, `hayu`, `now` | These overlays will not be used if the region is not `uk` as these streaming services are UK-focused                                |
| any besides `CA` | `crave`                          | These overlays will not be used if the region is not `ca` as these streaming services are Canada-focused                            |
| `CA`             | `max`, `showtime`                | These overlays will not be used if the region is `ca` as these streaming services are part of the Crave streaming service in Canada |


## Config

The below YAML in your config.yml will create the overlays:

```yaml
libraries:
  Movies:
    overlay_files:
      - default: streaming
  TV Shows:
    overlay_files:
      - default: streaming
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this Kometa Defaults file.

    * **Overlay Template Variables** are additional variables shared across the Kometa Overlay Defaults.

    ??? example "Default Template Variable Values (click to expand)"

        | Variable            | Default                                                                        |
        |:--------------------|:-------------------------------------------------------------------------------|
        | `horizontal_offset` | **Description:** Change the horizontal offset.<br>**Default Value:** `15`      |
        | `horizontal_align`  | **Description:** Change the horizontal alignment.<br>**Default Value:** `left` |
        | `vertical_offset`   | **Description:** Change the vertical offset.<br>**Default Value:** `390`       |
        | `vertical_align`    | **Description:** Change the vertical alignment.<br>**Default Value:** `bottom` |
        | `back_color`        | **Description:** Change the back color.<br>**Default Value:** `#00000099`      |
        | `back_radius`       | **Description:** Change the back (lozenge) radius .<br>**Default Value:** `30` |
        | `back_width`        | **Description:** Change the back (lozenge) width.<br>**Default Value:** `305`  |
        | `back_height`       | **Description:** Change the back (lozenge) height.<br>**Default Value:** `105` |
        
    === "File-Specific Template Variables"

        | Variable                     | Description & Values                                                                                                                                                                                                                                                                                                            |
        |:-----------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `region`                     | **Description:** Changes some Streaming Service lists to regional variants (see below table for more information.<br>**Default:** `US`<br>**Values:** Any [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) of the region where the streaming information should be based on.                                                                                                                   |
        | `originals_only`             | **Description:** Changes Streaming Service overlays to only apply to original content produced by the service.<br>**Note**: Cannot be used with `region`, and only produces overlays for `amazon`, `appletv`, `disney`, `max`, `hulu`, `netflix`, `paramount`, `peacock`<br>**Default:** `false`<br>**Values:** `true`, `false` |
        | `weight_<<key>>`<sup>1</sup> | **Description:** Controls the weight of the Overlay. Higher numbers have priority.<br>**Values:** Any Number                                                                                                                                                                                                                    |

        1. Each default overlay has a `key` that when calling to effect a specific overlay you must replace `<<key>>` 
        with when calling.

    === "Overlay Template Variables"

        {%
           include-markdown "../overlay_variables.md"
        %}

???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.
    
    ```yaml
    libraries:
      Movies:
        overlay_files:
          - default: streaming
            template_variables:
              originals_only: true
              use_peacock: false
              weight_netflix: 100
    ```
