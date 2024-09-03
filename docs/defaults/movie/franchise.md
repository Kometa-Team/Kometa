# Franchise Collections

The `franchise` Default Collection File is used to create collections based on popular Movie franchises, and can be used 
as a replacement to the TMDb Collections that Plex creates out-of-the-box.

Unlike most Default Collection Files, Franchise works by placing collections inline with the main library items if your 
library allows it. For example, the "Iron Man" franchise collection will appear next to the "Iron Man" movies within 
your library.

**[This file has a Show Library Counterpart.](../show/franchise.md)**

![](../images/moviefranchise.png)

## Requirements & Recommendations

Supported Library Types: Movie

## Collections

| Collection                                       | Key                                               | Description                                            |
|:-------------------------------------------------|:--------------------------------------------------|:-------------------------------------------------------|
| `<<Collection Name>>`<br>**Example:** `Iron Man` | `<<TMDb Collection ID>>`<br>**Example:** `131292` | Collection of Movies found in this Collection on TMDb. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    collection_files:
      - default: franchise
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to 
make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults 
work. Any value not specified will use its default value if it has one if not it's just ignored.

??? abstract "Variable Lists (click to expand)"

    * **File-Specific Template Variables** are variables available specifically for this Kometa Defaults file.

    ???+ warning

        [Shared Collection Variables](../collection_variables.md) are NOT available to this default file.

    === "File-Specific Template Variables"

        | Variable                                 | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
        |:-----------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `summary_<<key>>`<sup>1</sup>            | **Description:** Changes the summary of the specified key's collection.<br>**Values:** New Collection Summary                                                                                                                                                                                                                                                                                                                                                                                                                             |
        | `collection_section`                     | **Description:** Adds a sort title with this collection sections.<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                                               |
        | `order_<<key>>`<sup>1</sup>              | **Description:** Controls the sort order of the collections in their collection section.<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `collection_mode`                        | **Description:** Controls the collection mode of all collections in this file.<br>**Values:**<table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table>                                                                                                                                                           |
        | `minimum_items`                          | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                    |
        | `movie_<<key>>`<sup>1</sup>              | **Description:** Adds the TMDb Movie IDs given to the specified key's collection. Overrides the [default movie](#movie) for that collection if used.<br>**Values:** List of TMDb Movie IDs                                                                                                                                                                                                                                                                                                                                                |
        | `name_mapping_<<key>>`<sup>1</sup>       | **Description:** Sets the name mapping value for using assets of the specified key's collection.Overrides the [default name_mapping](#name-mapping) for that collection if used.<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                |
        | `sort_title`                             | **Description:** Sets the sort title for all collections. Use `<<collection_name>>` to use the collection name. **Example:** `"!02_<<collection_name>>"`<br>**Values:** Any String with `<<collection_name>>`                                                                                                                                                                                                                                                                                                                             |
        | `sort_title_<<key>>`<sup>1</sup>         | **Description:** Sets the sort title of the specified key's collection.<br>**Default:** `sort_title`<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                            |
        | `build_collection`                       | **Description:** Controls if you want the collection to actually be built. i.e. you may just want these movies sent to Radarr.<br>**Values:** `false` to not build the collection                                                                                                                                                                                                                                                                                                                                                         |
        | `sync_mode`                              | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `sync_mode_<<key>>`<sup>1</sup>          | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `collection_order`                       | **Description:** Changes the Collection Order for all collections in this file.<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                     |
        | `collection_order_<<key>>`<sup>1</sup>   | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |
        | `title_override`                         | **Description:** Overrides the [default title_override dictionary](#title-override).<br>**Values:** Dictionary with `key: new_title` entries                                                                                                                                                                                                                                                                                                                                                                                              |
        | `exclude`                                | **Description:** Exclude these TMDb Collections from creating a Dynamic Collection.<br>**Values:** List of TMDb Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                            |
        | `addons`                                 | **Description:** Overrides the [default addons dictionary](#addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of TMDb Collection IDs                                                                                                                                                                                                                                                                                             |
        | `append_addons`                          | **Description:** Appends to the [default addons dictionary](#addons).<br>**Values:** Dictionary List of TMDb Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                               |
        | `remove_addons`                          | **Description:** Removes from the [default addons dictionary](#addons).<br>**Values:** Dictionary List of TMDb Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                             |
        | `radarr_add_missing`                     | **Description:** Override Radarr `add_missing` attribute for all collections in a Defaults file.<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                         |
        | `radarr_add_missing_<<key>>`<sup>1</sup> | **Description:** Override Radarr `add_missing` attribute of the specified key's collection.<br>**Default:** `radarr_add_missing`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                         |
        | `radarr_folder`                          | **Description:** Override Radarr `root_folder_path` attribute for all collections in a Defaults file.<br>**Values:** Folder Path                                                                                                                                                                                                                                                                                                                                                                                                          |
        | `radarr_folder_<<key>>`<sup>1</sup>      | **Description:** Override Radarr `root_folder_path` attribute of the specified key's collection.<br>**Default:** `radarr_folder`<br>**Values:** Folder Path                                                                                                                                                                                                                                                                                                                                                                               |
        | `radarr_tag`                             | **Description:** Override Radarr `tag` attribute for all collections in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                                                                            |
        | `radarr_tag_<<key>>`<sup>1</sup>         | **Description:** Override Radarr `tag` attribute of the specified key's collection.<br>**Default:** `radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                                                    |
        | `item_radarr_tag`                        | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr for all collections in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                      |
        | `item_radarr_tag_<<key>>`<sup>1</sup>    | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr of the specified key's collection.<br>**Default:** `item_radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                         |

        1. Each default collection has a `key` that when calling to effect a specific collection you must replace 
        `<<key>>` with when calling.
    
???+ example "Example Template Variable Amendments"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    Click the :fontawesome-solid-circle-plus: icon to learn more
    
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: franchise
            template_variables:
              build_collection: false #(1)!
              movie_105995: 336560 #(2)!
              radarr_add_missing: true #(3)!
    ```

    1.  Do not create any physical collections in Plex (normally used when you want to perform an "operation" instead, 
    see the third tooltip for the example)
    2.  Add [TMDb Movie 336560](https://www.themoviedb.org/movie/336560-lake-placid-vs-anaconda) to 
    [TMDb Collection 105995](https://www.themoviedb.org/collection/105995-anaconda-collection) 
    3.  Add items missing from your library in Plex to Radarr. When used in this particular file, hundreds if not 
    thousands of items may be sent to Radarr - proceed with caution!

## Default Values

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not 
show how to change a name or a list.**

If you want to customize these values, use the methods described above.

??? example "Default `addons` (click to expand) <a class="headerlink" href="#addons" title="Permanent link">¶</a>"

    <div id="addons" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    addons: {%    
      include-markdown "../../../defaults/movie/franchise.yml" 
      comments=false
      preserve-includer-indent=false
      start="addons:"
      end="title_override:"
    %}
    ```

??? example "Default `title_override` (click to expand) <a class="headerlink" href="#title-override" title="Permanent link">¶</a>"

    <div id="title-override" />

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    title_override: {%    
      include-markdown "../../../defaults/movie/franchise.yml" 
      comments=false
      preserve-includer-indent=false
      start="title_override:"
      end="template_variables:"
    %}
    ```

??? example "Default Template Variable `movie` (click to expand) <a class="headerlink" href="#movie" title="Permanent link">¶</a>"

    <div id="movie" />

    ???+ tip 

        Pass `movie_<<key>>` to the file as template variables to change this value per collection. 

    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../defaults/movie/franchise.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check1"
      end="# check2"
    %}
    ```

??? example "Default Template Variable `name_mapping` (click to expand) <a class="headerlink" href="#name-mapping" title="Permanent link">¶</a>"

    <div id="name-mapping" />
    
    ???+ tip 
    
        Pass `name_mapping_<<key>>` to the file as template variables to change this value per collection. 
    
    ```{ .dtd .no-copy }
    ###############################################################################
    ################################## IMPORTANT ##################################
    #####################  THIS DATA IS PROVIDED FOR REFERENCE ####################
    ##  DO NOT COPY/PASTE THIS INTO YOUR CONFIG FILE, IT WILL ONLY CAUSE ERRORS ###
    #############  SEE ABOVE FOR HOW TO MODIFY OR AUGMENT THESE VALUES ############
    ###############################################################################
    {%    
      include-markdown "../../../defaults/movie/franchise.yml" 
      comments=false
      preserve-includer-indent=true
      dedent=true
      start="# check2"
    %}
    ```
