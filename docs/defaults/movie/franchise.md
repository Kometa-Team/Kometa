# Franchise Collections

The `franchise` Default Metadata File is used to create collections based on popular Movie franchises, and can be used as a replacement to the TMDb Collections that Plex creates out-of-the-box.

Unlike most Default Metadata Files, Franchise works by placing collections inline with the main library items if your library allows it. For example, the "Iron Man" franchise collection will appear next to the "Iron Man" movies within your library.

**This file works with Movie Libraries, but has a Show Library [Counterpart](../show/franchise).**

![](../images/moviefranchise.png)

## Collections

| Collection                                       | Key                                               | Description                                            |
|:-------------------------------------------------|:--------------------------------------------------|:-------------------------------------------------------|
| `<<Collection Name>>`<br>**Example:** `Iron Man` | `<<TMDb Collection ID>>`<br>**Example:** `131292` | Collection of Movies found in this Collection on TMDb. |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: franchise
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

**[Shared Collection Variables](../collection_variables) are NOT available to this default file.**

| Variable                                 | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:-----------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name_<<key>>`<sup>1</sup>               | **Description:** Changes the name of the specified key's collection.<br>**Values:** New Collection Name                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `summary_<<key>>`<sup>1</sup>            | **Description:** Changes the summary of the specified key's collection.<br>**Values:** New Collection Summary                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `collection_section`                     | **Description:** Adds a sort title with this collection sections.<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `order_<<key>>`<sup>1</sup>              | **Description:** Controls the sort order of the collections in their collection section.<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `collection_mode`                        | **Description:** Controls the collection mode of all collections in this file.<br>**Values:**<table class="clearTable"><tr><td>`default`</td><td>Library default</td></tr><tr><td>`hide`</td><td>Hide Collection</td></tr><tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr><tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr></table>                                                                                                                                                              |
| `minimum_items`                          | **Description:** Controls the minimum items that the collection must have to be created.<br>**Default:** `2`<br>**Values:** Any number                                                                                                                                                                                                                                                                                                                                                                                                       |
| `movie_<<key>>`<sup>1</sup>              | **Description:** Adds the TMDb Movie IDs given to the specified key's collection. Overrides the [default movie](#default-movie) for that collection if used.<br>**Values:** List of TMDb Movie IDs                                                                                                                                                                                                                                                                                                                                           |
| `name_mapping_<<key>>`<sup>1</sup>       | **Description:** Sets the name mapping value for using assets of the specified key's collection.Overrides the [default name_mapping](#default-name_mapping) for that collection if used.<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                           |
| `sort_title`                             | **Description:** Sets the sort title for all collections. Use `<<collection_name>>` to use the collection name. **Example:** `"!02_<<collection_name>>"`<br>**Values:** Any String with `<<collection_name>>`                                                                                                                                                                                                                                                                                                                                |
| `sort_title_<<key>>`<sup>1</sup>         | **Description:** Sets the sort title of the specified key's collection.<br>**Default:** `sort_title`<br>**Values:** Any String                                                                                                                                                                                                                                                                                                                                                                                                               |
| `build_collection`                       | **Description:** Controls if you want the collection to actually be built. i.e. you may just want these movies sent to Radarr.<br>**Values:** `false` to not build the collection                                                                                                                                                                                                                                                                                                                                                            |
| `sync_mode`                              | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `sync_mode_<<key>>`<sup>1</sup>          | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table>                                                                                                                                                                                                                                             |
| `collection_order`                       | **Description:** Changes the Collection Order for all collections in this file.<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table>                                     |
| `collection_order_<<key>>`<sup>1</sup>   | **Description:** Changes the Collection Order of the specified key's collection.<br>**Default:** `collection_order`<br>**Values:**<table class="clearTable"><tr><td>`release`</td><td>Order Collection by Release Dates</td></tr><tr><td>`alpha`</td><td>Order Collection Alphabetically</td></tr><tr><td>`custom`</td><td>Order Collection Via the Builder Order</td></tr><tr><td>[Any `plex_search` Sort Option](../../metadata/builders/plex.md#sort-options)</td><td>Order Collection by any `plex_search` Sort Option</td></tr></table> |
| `title_override`                         | **Description:** Overrides the [default title_override dictionary](#default-title_override).<br>**Values:** Dictionary with `key: new_title` entries                                                                                                                                                                                                                                                                                                                                                                                         |
| `exclude`                                | **Description:** Exclude these TMDb Collections from creating a Dynamic Collection.<br>**Values:** List of TMDb Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                               |
| `addons`                                 | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of TMDb Collection IDs                                                                                                                                                                                                                                                                                        |
| `append_addons`                          | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of TMDb Collection IDs                                                                                                                                                                                                                                                                                                                                                                                                          |
| `radarr_add_missing`                     | **Description:** Override Radarr `add_missing` attribute for all collections in a Defaults file.<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                                                            |
| `radarr_add_missing_<<key>>`<sup>1</sup> | **Description:** Override Radarr `add_missing` attribute of the specified key's collection.<br>**Default:** `radarr_add_missing`<br>**Values:** `true` or `false`                                                                                                                                                                                                                                                                                                                                                                            |
| `radarr_folder`                          | **Description:** Override Radarr `root_folder_path` attribute for all collections in a Defaults file.<br>**Values:** Folder Path                                                                                                                                                                                                                                                                                                                                                                                                             |
| `radarr_folder_<<key>>`<sup>1</sup>      | **Description:** Override Radarr `root_folder_path` attribute of the specified key's collection.<br>**Default:** `radarr_folder`<br>**Values:** Folder Path                                                                                                                                                                                                                                                                                                                                                                                  |
| `radarr_tag`                             | **Description:** Override Radarr `tag` attribute for all collections in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                                                                               |
| `radarr_tag_<<key>>`<sup>1</sup>         | **Description:** Override Radarr `tag` attribute of the specified key's collection.<br>**Default:** `radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                                                       |
| `item_radarr_tag`                        | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr for all collections in a Defaults file.<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                                                         |
| `item_radarr_tag_<<key>>`<sup>1</sup>    | **Description:** Used to append a tag in Radarr for every movie found by the builders that's in Radarr of the specified key's collection.<br>**Default:** `item_radarr_tag`<br>**Values:** List or comma-separated string of tags                                                                                                                                                                                                                                                                                                            |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: franchise
        template_variables:
          collection_order: alpha
          collection_section: "02"
          build_collection: false
          movie_105995: 336560
          radarr_add_missing: true
```

## Default `addons`

```yaml
addons:
  8091:       # Alien
    - 135416    # Prometheus
  2806:       # American Pie
    - 298820    # American Pie (Spin-off)
  87800:      # Appleseed
    - 371526    # Appleseed XIII
  477208:     # DC Super Hero Girls
    - 557495    # LEGO DC Super Hero Girls
  86066:      # Despicable Me
    - 544669    # Minions
  9485:       # The Fast and the Furious
    - 688042    # Hobbs & Shaw
  86115:      # Garfield
    - 373918    # Garfield CGI
  91361:      # Halloween
    - 126209    # Halloween (Rob Zombie Series)
  9818:       # Mortal Kombat
    - 931431    # Mortal Kombat
  495:        # Shaft
    - 608103    # Shaft (Reboot)
  1582:       # Teenage Mutant Ninja Turtles
    - 401562    # Teenage Mutant Ninja Turtles (Remake)
  111751:     # Texas Chainsaw Massacre
    - 425175    # Texas Chainsaw (Reboot)
  2467:       # Tomb Raider
    - 621142    # Tomb Raider (Reboot)
  748:        # X-Men
    - 453993    # The Wolverine
```

## Default `title_override`

```yaml
title_override:
  10: "Star Wars: Skywalker Saga"
  535313: Godzilla (MonsterVerse)
  535790: Godzilla (Anime)
```

## Default `movie`

```yaml
105995: 336560    # Anaconda: Lake Placid vs. Anaconda
176097: 14177     # Barbershop: Beauty Shop
448150: 567604    # Deadpool: Once Upon a Deadpool
9735: 6466, 222724  # Friday the 13th: Freddy vs. Jason, Crystal Lake Memories: The Complete History of Friday the 13th
386382: 326359, 460793  # Frozen: Frozen Fever, Olaf's Frozen Adventure
2980: 43074 # Ghostbusters: Ghostbusters
374509: 18983 # Godzilla (Showa): Godzilla, King of the Monsters!
374511: 39256 # Godzilla (Heisei): Godzilla 1985
535313: 293167  # Godzilla: Kong: Skull Island
9743: 11454 # The Hannibal Lecter: Manhunter
8354: 79218, 717095, 387893 # Ice Age: Ice Age: A Mammoth Christmas, Ice Age Continental Drift: Scrat Got Your Tongue, Ice Age: The Great Egg-Scapade
70068: 658009, 643413, 450001, 751391, 44249, 182127, 44865 # Ip Man: Ip Man: Kung Fu Master, Ip Man and Four Kings, Master Z: Ip Man Legacy, Young Ip Man: Crisis Time, The Legend Is Born: Ip Man, Ip Man: The Final Fight, The Grandmaster
328: 630322 # Jurassic Park: Battle at Big Rock
8580: 38575 # The Karate Kid: The Karate Kid
14740: 161143, 25472, 270946  # Madagascar: Madly Madagascar, Merry Madagascar, Penguins of Madagascar
9818: 664767  # Mortal Kombat: Mortal Kombat Legends: Scorpion's Revenge
171732: 39410 # Rebirth of Mothra: Mothra
8581: 6466, 23437 # A Nightmare on Elm Street: Freddy vs. Jason, A Nightmare on Elm Street
627517: 13155, 68728  # Oz: Return to Oz, Oz the Great and Powerful
10789: 157433 # Pet Sematary: Pet Sematary
708816: 305470, 306264  # Power Rangers: Power Rangers, Power Rangers Super Megaforce: The Legendary Battle
190435: 687354, 11667 # Street Fighter (Animated): Street Fighter Assassin's Fist, Street Fighter
1582: 1273  # Teenage Mutant Ninja Turtles: TMNT
10194: 130925 # Toy Story: Partysaurus Rex
63043: 73362  # TRON: TRON: The Next Day
748: 567604 # X-Men: Once Upon a Deadpool
```

## Default `name_mapping`

```yaml
1565: 28 Days-Weeks Later
508334: Angels in the
115838: Escape From
386534: Has Fallen
87359: Mission Impossible
133352: Resident Evil Biohazard
115575: Star Trek Alternate Reality
115570: Star Trek The Next Generation
151: Star Trek The Original Series
10: Star Wars Skywalker Saga
```