# Ratings Overlays

The `ratings` Default Overlay File is used to create an overlay based on the Critic Rating, Audience Rating, and User 
Rating in Plex for each item within your library.

This file only updates the overlays based on the data in Plex, it will not pull the ratings directly from any 
third-party website, see recommendations below for more info.

**Please read [PMM Ratings Explained](../../pmm/guides/ratings.md) for more understanding on how PMM interacts with 
ratings.**

![](images/ratings_overlay.png)

## Requirements & Recommendations

Supported Overlay Level: Movie, Show, Episode

Requirements: Template Variables must be configured, otherwise this file will not apply any overlays.

Recommendations: Use the [Mass * Rating Update Library Operation](../../config/operations.md) and the [Mass Episode * 
Rating Update Library Operation](../../config/operations.md) to update Plex to the Ratings you want on the Overlay.

## Config

The below YAML in your config.yml will create the overlays:

```yaml
  Movies:
    overlay_files:
      - pmm: ratings
        template_variables:
          rating1: critic
          rating2: audience
          rating3: user
          rating1_image: imdb
          rating2_image: rt_popcorn
          rating3_image: tmdb
    operations:
      mass_critic_rating_update: imdb
      mass_audience_rating_update: mdb_tomatoesaudience
      mass_user_rating_update: tmdb
  TV Shows:
    overlay_files:
      - pmm: ratings
        template_variables:
          rating1: critic
          rating2: audience
          rating3: user
          rating1_image: imdb
          rating2_image: rt_popcorn
          rating3_image: tmdb
      - pmm: ratings
        template_variables:
          builder_level: episode
          rating1: critic
          rating2: audience
          rating1_image: imdb
          rating2_image: tmdb
    operations:
      mass_critic_rating_update: imdb
      mass_audience_rating_update: mdb_tomatoesaudience
      mass_user_rating_update: tmdb
      mass_episode_critic_rating_update: imdb
      mass_episode_audience_rating_update: tmdb
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this PMM Defaults file.

    * **Overlay Template Variables** are additional variables shared across the PMM Overlay Defaults.

    * **Overlay Text Template Variables** are additional variables shared across the PMM Text Overlay Defaults.

    ??? example "Default Template Variable Values (click to expand)"

        | Variable            | Default     |
        |:--------------------|:------------|
        | `horizontal_offset` | `30`        |
        | `horizontal_align`  | `left`      |
        | `vertical_offset`   | `0`         |
        | `vertical_align`    | `center`    |
        | `back_color`        | `#00000099` |
        | `back_radius`       | `30`        |
        | `back_width`        | `160`       |
        | `back_height`       | `160`       |
        | `back_padding`      | `15`        |
        | `back_radius`       | `30`        |
        
    === "File-Specific Template Variables"

        These can be prependd with `rating1_`, `rating2_`, or `rating3_` to change that attribute on each rating 
        individually.

        ???+ warning

            To amend `horizontal_offset` and `vertical_offset` you **must** prepend the variable with `rating1_`, 
            `rating2_`, or `rating3_`

        | Variable                 | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
        |:-------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `rating1`                | **Description:** Choose the rating to display in rating1.<br>**Values:** `critic`, `audience`, or `user`                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `rating1_image`          | **Description:** Choose the rating image to display in rating1.<br>**Values:** `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, or `star`                                                                                                                                                                                                                                                                                                                                                                                 |
        | `rating1_style`          | **Description:** Choose the rating number style for rating1.<br>**Values:** <table class="clearTable"><tr><td>Ten Scale</td><td><code>""</code></td><td><code>8.7</code>, <code>9.0</code></td></tr><tr><td>Ten Scale removing <code>.0</code>  </td><td><code>"#"</code></td><td><code>8.7</code>, <code>9</code></td></tr><tr><td>Hundred Scale</td><td><code>"%"</code></td><td><code>87</code>, <code>90</code></td></tr><tr><td>Five Scale</td><td><code>"/"</code></td><td><code>8.6</code> rating in plex will show as <code>4.3</code> on the overlay</td></tr></table> |
        | `rating1_extra`          | **Description:** Extra text after rating1.<br>**Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`. <br>**Values:** Any Value                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `rating2`                | **Description:** Choose the rating to display in rating2.<br>**Values:** `critic`, `audience`, or `user`                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `rating2_image`          | **Description:** Choose the rating image to display in rating2.<br>**Values:** `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, or `star`                                                                                                                                                                                                                                                                                                                                                                                 |
        | `rating2_style`          | **Description:** Choose the rating number style for rating2.<br>**Values:** <table class="clearTable"><tr><td>Ten Scale</td><td><code>""</code></td><td><code>8.7</code>, <code>9.0</code></td></tr><tr><td>Ten Scale removing <code>.0</code>  </td><td><code>"#"</code></td><td><code>8.7</code>, <code>9</code></td></tr><tr><td>Hundred Scale</td><td><code>"%"</code></td><td><code>87</code>, <code>90</code></td></tr><tr><td>Five Scale</td><td><code>"/"</code></td><td><code>8.6</code> rating in plex will show as <code>4.3</code> on the overlay</td></tr></table> |
        | `rating2_extra`          | **Description:** Extra text after rating2.<br>**Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`. <br>**Values:** Any Value                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `rating3`                | **Description:** Choose the rating to display in rating3.<br>**Values:** `critic`, `audience`, or `user`                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `rating3_image`          | **Description:** Choose the rating image to display in rating3.<br>**Values:** `anidb`, `imdb`, `letterboxd`, `tmdb`, `metacritic`, `rt_popcorn`, `rt_tomato`, `trakt`, `mal`, `mdb`, or `star`                                                                                                                                                                                                                                                                                                                                                                                 |
        | `rating3_style`          | **Description:** Choose the rating number style for rating3.<br>**Values:** <table class="clearTable"><tr><td>Ten Scale</td><td><code>""</code></td><td><code>8.7</code>, <code>9.0</code></td></tr><tr><td>Ten Scale removing <code>.0</code>  </td><td><code>"#"</code></td><td><code>8.7</code>, <code>9</code></td></tr><tr><td>Hundred Scale</td><td><code>"%"</code></td><td><code>87</code>, <code>90</code></td></tr><tr><td>Five Scale</td><td><code>"/"</code></td><td><code>8.6</code> rating in plex will show as <code>4.3</code> on the overlay</td></tr></table> |
        | `rating3_extra`          | **Description:** Extra text after rating3.<br>**Default:** `%` for `rt_popcorn`, `rt_tomato`, `tmdb`. <br>**Values:** Any Value                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
        | `horizontal_position`    | **Description:** Choose the horizontal position for the rating group.<br>**Default:** `left`<br>**Values:** `left`, `right`, or `center`                                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `vertical_position`      | **Description:** Choose the vertical position for the rating group.<br>**Default:** `center`<br>**Values:** `top`, `bottom`, or `center`                                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `rating_alignment`       | **Description:** Choose the display alignment for the rating group.<br>**Default:** `vertical`<br>**Values:** `horizontal`, or `vertical`                                                                                                                                                                                                                                                                                                                                                                                                                                       |
        | `minimum_rating`         | **Description:** Minimum Rating to display<br>**Default:** 0.0<br>**Values:** Any Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `fresh_rating`           | **Description:** Determines when ratings are considered Fresh<br>**Default:** 6.0<br>**Values:** Any Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
        | `maximum_rating`         | **Description:** Maximum Rating to display<br>**Default:** 10.0<br>**Values:** Any Number                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
        | `addon_offset`           | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
        | `rating1_addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
        | `rating2_addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
        | `rating3_addon_offset`   | **Description:** Text Addon Image Offset from the text.<br>**Default:** `15`<br>**Values:** Any number greater than 0                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
        | `addon_position`         | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `top`<br>**Values:** `left`, `right`, `top`, `bottom`                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        | `rating1_addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `top`<br>**Values:** `left`, `right`, `top`, `bottom`                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        | `rating2_addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `top`<br>**Values:** `left`, `right`, `top`, `bottom`                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        | `rating3_addon_position` | **Description:** Text Addon Image Alignment in relation to the text.<br>**Default:** `top`<br>**Values:** `left`, `right`, `top`, `bottom`                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        | `builder_level`          | **Description:** Choose the Overlay Level.<br>**Values:** `episode`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

    === "Overlay Template Variables"

        These variables can be prepended with `rating1_`, `rating2_`, or `rating3_` to change that attribute on each 
        rating individually.

        {%
           include-markdown "../overlay_variables.md"
        %}

    === "Overlay Text Template Variables"

        These variables can be prepended with `rating1_`, `rating2_`, or `rating3_` to change that attribute on each 
        rating individually.

        {%
           include-markdown "../overlay_text_variables.md"
        %}
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.
    
    ???+ warning
    
        This example uses fonts not packaged with PMM. See [bullmoose20's 
        Configs](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/bullmoose20)

    ```yaml
      Movies:
        overlay_files:
          - pmm: ratings
            template_variables:
              rating1: critic
              rating1_image: imdb
              rating1_font: config/metadata/fonts/Impact.ttf
              rating1_font_size: 70

              rating2: audience
              rating2_image: rt_popcorn
              rating2_font: config/metadata/fonts/Adlib.ttf
              rating2_font_size: 63

              rating3: user
              rating3_image: tmdb
              rating3_font: config/metadata/fonts/Avenir_95_Black.ttf
              rating3_font_size: 70

              horizontal_position: right
        operations:
          mass_critic_rating_update: imdb
          mass_audience_rating_update: mdb_tomatoesaudience
          mass_user_rating_update: tmdb
      TV Shows:
        overlay_files:
          - pmm: ratings
            template_variables:
              rating1: critic
              rating1_image: imdb
              rating1_font: config/metadata/fonts/Impact.ttf
              rating1_font_size: 70

              rating2: audience
              rating2_image: rt_popcorn
              rating2_font: config/metadata/fonts/Adlib.ttf
              rating2_font_size: 63

              rating3: user
              rating3_image: tmdb
              rating3_font: config/metadata/fonts/Avenir_95_Black.ttf
              rating3_font_size: 70

              horizontal_position: right
          - pmm: ratings
            template_variables:
              builder_level: episode
              
              rating1: critic
              rating1_image: imdb
              rating1_font: config/metadata/fonts/Impact.ttf
              rating1_font_size: 70

              rating2: audience
              rating2_image: tmdb
              rating2_font: config/metadata/fonts/Avenir_95_Black.ttf
              rating2_font_size: 70

              horizontal_position: right
        operations:
          mass_critic_rating_update: imdb
          mass_audience_rating_update: mdb_tomatoesaudience
          mass_user_rating_update: tmdb
          mass_episode_critic_rating_update: imdb
          mass_episode_audience_rating_update: tmdb
    ```
