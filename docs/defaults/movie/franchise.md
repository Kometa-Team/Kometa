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

It is important to disable Plex's in-built Automatic Collections if you are using this Default file. Please see the below video showing how to do this.

<video controls>
<source src="../../images/automatic_collections.mp4" type="video/mp4">
</video>

You'll also need to delete any Collections created automatically by Plex prior to Kometa running this file. You can use the [`delete_collections` operation](../../config/operations.md#delete-collections) to do this, or any other method.

## <a id="collection_section"></a>Collections

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
        | `summary_<<key>>`<sup>1</sup>            | **Description:** Changes the summary of the [key's](#collection_section) collection.<br>**Values:** New Collection Summary                                                                                                                                                                                                                                                                                                                                                                                                                             |
        | `collection_section`                     | **Description:** Adds a sort title with this collection sections.<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                                               |
        | `order_<<key>>`<sup>1</sup>              | **Description:** Controls the sort order of the collections in their collection section.<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                        |
        | `collection_mode`                        | **Description:** Controls the collection mode of all collections in this file.<br>**Values:**<table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table>                                                                                                                                                           |
        | `minimum_items`                          | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                    |
        | `movie_<<key>>`<sup>1</sup>              | **Description:** Adds the TMDb Movie IDs given to the [key's](#collection_section) collection. Overrides the [default movie](#default-values) for that collection if used.<br>**Values:** List of TMDb Movie IDs                                                                                                                                                                                                                                                                                                                                                |
        | `name_mapping_<<key>>`<sup>1</sup>       | **Description:** Sets the name mapping value for using assets of the [key's](#collection_section) collection.Overrides the [default name_mapping](#default-values) for that collection if used.<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                |
        | `sort_title`                             | **Description:** Sets the sort title for all collections. Use `<<collection_name>>` to use the collection name. **Example:** `"!02_<<collection_name>>"`<br>**Values:** Any String with `<<collection_name>>`                                                                                                                                                                                                                                                                                                                             |
        | `sort_title_<<key>>`<sup>1</sup>         | **Description:** Sets the sort title of the [key's](#collection_section) collection.<br>**Default:** `sort_title`<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                            |
        | `build_collection`                       | **Description:** Controls if you want the collection to actually be built. i.e. you may just want these movies sent to Radarr.<br>**Values:** `false` to not build the collection                                                                                                                                                                                                                                                                                                                                                         |
        | `sync_mode`                              | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `sync_mode_<<key>>`<sup>1</sup>          | **Description:** Changes the Sync Mode of the [key's](#collection_section) collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                          |
        | `collection_order`                       | **Description:** Changes the Collection Order for all collections in this file.<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                     |
        | `collection_order_<<key>>`<sup>1</sup>   | **Description:** Changes the Collection Order of the [key's](#collection_section) collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../files/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |
        | `title_override`                         | **Description:** Overrides the [default title_override dictionary](#default-values).<br>**Values:** Dictionary with `key: new_title` entries                                                                                                                                                                                                                                                                                                                                                                                              |
        | `exclude`                                | **Description:** Exclude these TMDb Collections from creating a Dynamic Collection.<br>**Values:** List of TMDb Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                            |
        | `addons`                                 | **Description:** Overrides the [default addons dictionary](#default-values). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of TMDb Collection IDs                                                                                                                                                                                                                                                                                             |
        | `append_addons`                          | **Description:** Appends to the [default addons dictionary](#default-values).<br>**Values:** Dictionary List of TMDb Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                               |
        | `remove_addons`                          | **Description:** Removes from the [default addons dictionary](#default-values).<br>**Values:** Dictionary List of TMDb Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                             |
        | `radarr_add_missing`                     | **Description:** Override Radarr `add_missing` attribute for all collections in a Defaults file.<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                         |
        | `radarr_add_missing_<<key>>`<sup>1</sup> | **Description:** Override Radarr `add_missing` attribute of the [key's](#collection_section) collection.<br>**Default:** `radarr_add_missing`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                         |
        | `radarr_folder`                          | **Description:** Override Radarr `root_folder_path` attribute for all collections in a Defaults file.<br>**Values:** Folder Path                                                                                                                                                                                                                                                                                                                                                                                                          |
        | `radarr_folder_<<key>>`<sup>1</sup>      | **Description:** Override Radarr `root_folder_path` attribute of the [key's](#collection_section) collection.<br>**Default:** `radarr_folder`<br>**Values:** Folder Path                                                                                                                                                                                                                                                                                                                                                                               |
        | `radarr_tag`                             | **Description:** Override Radarr `tag` attribute for all collections in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                                                                            |
        | `radarr_tag_<<key>>`<sup>1</sup>         | **Description:** Override Radarr `tag` attribute of the [key's](#collection_section) collection.<br>**Default:** `radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                                                    |
        | `item_radarr_tag`                        | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr for all collections in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                      |
        | `item_radarr_tag_<<key>>`<sup>1</sup>    | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr of the [key's](#collection_section) collection.<br>**Default:** `item_radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                         |

        1. Each default collection has a `key` [see here]() that you must replace 
        `<<key>>` with when using this template variable.  These keys are found in the table at the top of this page.
    
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

Unless you customize them as described above, these collections use default lists and searches to create the collections.

If you are interested in customizing the default values, you can find that information [here](#template-variables).

If you are interested in seeing what those default builders are, you can find that information [here](../sources.md).
