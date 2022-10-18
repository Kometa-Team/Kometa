# Franchise Collections

The `franchise` Default Metadata File is used to create collections based on popular TV Show franchises, and can be used as a replacement to the TMDb Collections that Plex creates out-of-the-box.

Unlike most Default Metadata Files, Franchise works by placing collections inline with the main library items if your library allows it. For example, the "Pretty Little Liars" franchise collection will appear next to the "Pretty Little Liars" show in your library so that you have easy access to the other shows in the franchise.

**This file works with TV Libraries, but has a Movie Library [Counterpart](../movie/franchise).**

![](../images/showfranchise.png)

## Collections

| Collection                                                  |                         Key                         | Description                                        |
|:------------------------------------------------------------|:---------------------------------------------------:|:---------------------------------------------------|
| `<<Collection Name>>`<br>**Example:** `Pretty Little Liars` | `<<Starting TMDb Show ID>>`<br>**Example:** `31917` | Collection of Shows specified for this Collection. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  TV Shows:
    metadata_path:
      - pmm: franchise
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

**[Shared Collection Variables](../variables) are NOT available to this default file.**

| Variable                                 | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:-----------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name_<<key>>`<sup>1</sup>               | **Description:** Changes the name of the specified key's collection.<br>**Values:** New Collection Name                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `summary_<<key>>`<sup>1</sup>            | **Description:** Changes the summary of the specified key's collection.<br>**Values:** New Collection Summary                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `collection_section`                     | **Description:** Adds a sort title with this collection sections.<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `order_<<key>>`<sup>1</sup>              | **Description:** Controls the sort order of the collections in their collection section.<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `collection_mode`                        | **Description:** Controls the collection mode of all collections in this file.<br>**Values:**<table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table>                                                                                                                                                              |
| `minimum_items`                          | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                       |
| `name_mapping_<<key>>`<sup>1</sup>       | **Description:** Sets the name mapping value for using assets of the specified key's collection.<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `sort_title`                             | **Description:** Sets the sort title for all collections. Use `<<collection_name>>` to use the collection name. **Example:** `"!02_<<collection_name>>"`<br>**Values:** Any String with `<<collection_name>>`                                                                                                                                                                                                                                                                                                                                |
| `sort_title_<<key>>`<sup>1</sup>         | **Description:** Sets the sort title of the specified key's collection.<br>**Default:** `sort_title`<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                               |
| `build_collection`                       | **Description:** Controls if you want the collection to actually be built. i.e. you may just want these shows sent to Sonarr.<br>**Values:** `false` to not build the collection                                                                                                                                                                                                                                                                                                                                                             |
| `collection_order`                       | **Description:** Changes the Collection Order for all collections in this file.<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                     |
| `collection_order_<<key>>`<sup>1</sup>   | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |
| `exclude`                                | **Description:** Exclude these Collections from creating a Dynamic Collection.<br>**Values:** List of Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `data`                                   | **Description:** Overrides the [default data dictionary](#default-data). Defines the data that the custom dynamic collection processes.<br>**Values:** Dictionary List of TMDb Main Show ID                                                                                                                                                                                                                                                                                                                                                  |
| `append_data`                            | **Description:** Appends to the [default data dictionary](#default-data).<br>**Values:** Dictionary List of TMDb Main Show ID                                                                                                                                                                                                                                                                                                                                                                                                                |
| `addons`                                 | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of TMDb Show IDs                                                                                                                                                                                                                                                                                              |
| `append_addons`                          | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of TMDb Show IDs                                                                                                                                                                                                                                                                                                                                                                                                                |
| `sonarr_add_missing`                     | **Description:** Override Sonarr `add_missing` attribute for all collections in a Defaults file.<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                            |
| `sonarr_add_missing_<<key>>`<sup>1</sup> | **Description:** Override Sonarr `add_missing` attribute of the specified key's collection.<br>**Default:** `sonarr_add_missing`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                            |
| `sonarr_folder`                          | **Description:** Override Sonarr `root_folder_path` attribute for all collections in a Defaults file.<br>**Values:** Folder Path                                                                                                                                                                                                                                                                                                                                                                                                             |
| `sonarr_folder_<<key>>`<sup>1</sup>      | **Description:** Override Sonarr `root_folder_path` attribute of the specified key's collection.<br>**Default:** `sonarr_folder`<br>**Values:** Folder Path                                                                                                                                                                                                                                                                                                                                                                                  |
| `sonarr_tag`                             | **Description:** Override Sonarr `tag` attribute for all collections in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                                                                               |
| `sonarr_tag_<<key>>`<sup>1</sup>         | **Description:** Override Sonarr `tag` attribute of the specified key's collection.<br>**Default:** `sonarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                                                       |
| `item_sonarr_tag`                        | **Description:** Used to append a tag in Sonarr for every show found by the builders that's in Sonarr for all collections in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                          |
| `item_sonarr_tag_<<key>>`<sup>1</sup>    | **Description:** Used to append a tag in Sonarr for every show found by the builders that's in Sonarr of the specified key's collection.<br>**Default:** `item_sonarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                             |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - pmm: franchise
        template_variables:
          append_data:
            "31917": Pretty Little Liars
          append_addons:
            31917: [46958, 79863, 110531] # Pretty Little Liars: Ravenswood, The Perfectionists, Original Sin
          sonarr_add_missing: true
```

## Default `data`

```yaml
data:
  "44006": One Chicago
  "75219": 9-1-1
  "253": Star Trek
  "1412": Arrowverse
  "85536": Star Wars
  "121": Doctor Who
  "1402": The Walking Dead
  "4629": Stargate
  "519": Law & Order
  "5614": NCIS
  "1431": CSI
  "951": Archie Comics
  "31917": Pretty Little Liars
  "6357": The Twilight Zone
```

## Default `addons`

```yaml
addons:
  44006: [58841, 62650, 67993] # Chicago Fire: Med, PD, Justice
  75219: 89393 # 9-1-1: 9-1-1 Lone Star
  253: [655, 1855, 314, 67198, 85949] # Star Trek, The Next Generation, Voyager, Enterprise, Discovery, Picard
  1412: [60735, 62688, 62643, 71663, 89247]  # Arrow: The Flash, Supergirl, Legends of Tomorrow, Black Lightning, Batwoman
  85536: [71412, 3478, 105971, 92830, 83867, 60554, 82856, 115036, 114461, 202879, 114462, 114476, 114478, 79093] # Star Wars Galaxy of Adventures: Forces of Destiny, The Clone Wars, The Bad Batch, Obi-Wan Kenobi, Andor, Rebels, The Mandalorian, The Book of Boba Fett, Ahsoka, Skeleton Crew, Rangers of the New Republic, Lando, Visions, Resistance
  121: [57243, 1057, 424, 203, 64073]  # Doctor Who: K-9 & Company, Torchwood, The Sarah Jane Adventures, Class
  1402: [62286, 94305] # The Walking Dead: Fear the Walking Dead, World Beyond
  4629: [2290, 5148, 72925] # Stargate SG-1: Atlantis, Universe, Origins
  549: [2734, 4601, 3357, 32632, 72496, 157088, 106158]  #Law & Order, Special Victims Unit, Criminal Intent, Trial by Jury, LA, True Crime, Hate Crimes, Organized Crime
  5614: [17610, 124271, 61387, 4376]  # NCIS, Los Angeles, New Orleans, Hawaii, JAG
  1431: [1620, 2458, 122194, 61811] # CSI: Miami, NY, Cyber, Vegas
  951: [25641, 4489, 24211, 9829, 605, 69050, 79242, 87539] # The Archie Show, Sabrina, The Teenage Witch, Josie and the Pussycats, Josie and the Pussycats in Outer Space, The New Archies, Riverdale, Chilling Adventures of Sabrina, Katy Keene
  31917: [46958, 79863, 110531] # Pretty Little Liars: Ravenswood, The Perfectionists, Original Sin
  6357: [1918, 83135, 16399]  # The Twilight Zone (multiple)
```
