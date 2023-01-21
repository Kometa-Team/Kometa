# Network Collections

The `network` Default Metadata File is used to dynamically create collections based on the networks available in your library.

![](../images/network.png)

## Requirements & Recommendations

Supported Library Types: Show

## Collections Section 04

| Collection                          | Key                                 | Description                                                                 |
|:------------------------------------|:------------------------------------|:----------------------------------------------------------------------------|
| `Network Collections`               | `separator`                         | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<network>>`<br>**Example:** `NBC` | `<<network>>`<br>**Example:** `NBC` | Collection of Shows the aired on the network.                               |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  TV Shows:
    metadata_path:
      - pmm: network
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                      | Description & Values                                                                                                                                                                                                                                             |
|:------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                          |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                       |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                             |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                       |
| `include`                     | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of Networks found in your library                                                                                                                                   |
| `exclude`                     | **Description:** Exclude these Networks from creating a Dynamic Collection.<br>**Values:** List of Networks found in your library                                                                                                                                |
| `addons`                      | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Networks found in your library |
| `append_include`              | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of Networks found in your library                                                                                                                                  |
| `append_addons`               | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Networks found in your library                                                                                                                   |
| `network_name`                | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                        |
| `network_summary`             | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s broadcast on <<key_name>>.`<br>**Values:** Any string.                                                                                        |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - pmm: network
        template_variables:
          use_separator: false
          sep_style: stb
          append_exclude:
            - BBC
          sort_by: title.asc
```


## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
include:
  - A&E
  - ABC
  - Amazon
  - AMC
  - Animal Planet
  - BBC
  - BET
  - Cartoon Network
  - Channel 4
  - Channel 5
  - CBC
  - CBS
  - Comedy Central
  - Discovery
  - Disney Channel
  - E!
  - ESPN
  - Food Network
  - FOX
  - Hallmark
  - HBO
  - HGTV
  - History
  - ITV
  - Lifetime
  - MTV
  - National Geographic
  - NBC
  - Nickelodeon
  - PBS
  - Showtime
  - Sky
  - Starz
  - The CW
  - TLC
  - TNT
  - UKTV
  - USA
  - YouTube
```

### Default `addons`

```yaml
addons:
  A&E:
    - A+E Networks UK
  ABC:
    - ABC (AU)
    - ABC (US)
    - ABC Comedy
    - ABC Family
    - ABC Kids
    - ABC Me
    - ABC Signature
    - ABC Spark
    - ABC Studios
    - ABC.com
    - Freeform
  Amazon:
    - Amazon (Japan)
    - Amazon Kids+
    - Amazon Prime Video
    - Amazon Productions
    - Amazon Studios
    - Prime
    - Prime Video
  AMC:
    - AMC+
  Animal Planet:
    - Animal Planet (CA)
    - Animal Planet (UK)
  BBC:
    - BBC Alba
    - BBC America
    - BBC Choice
    - BBC First
    - BBC Four
    - BBC HD
    - BBC iPlayer
    - BBC Kids
    - BBC Knowledge
    - BBC News
    - BBC One
    - BBC One Northern Ireland
    - BBC Scotland
    - BBC Television
    - BBC Three
    - BBC Two
    - BBC UKTV
    - BBC Wales
    - BBC World News
    - CBBC
    - CBeebies
  BET:
    - BET+
  Cartoon Network:
    - Cartoonito
  Channel 4:
    - 4seven
    - All 4
    - E4
    - More4
  Channel 5:
    - Channel 5 (UK)
    - 5Action
    - 5Select
    - 5Star
    - 5USA
  CBC:
    - CBC (CA)
    - CBC Gem
    - CBC Television
  CBS:
    - CBS All Access
    - CBS Reality
    - CBS Reality (UK)
    - CBS.com
  Comedy Central:
    - Comedy Central (UK)
  Discovery:
    - Discovery Asia
    - Discovery Channel
    - Discovery Channel (Asia)
    - Discovery Channel (AU)
    - Discovery Channel (CA)
    - Discovery Channel (UK)
    - Discovery Family
    - Discovery Health Channel
    - Discovery Kids
    - Discovery Life
    - Discovery Real Time
    - Discovery Turbo
    - Discovery Turbo UK
    - discovery+
    - Discovery+ (IN)
    - Discovery+ (NO)
    - Discovery+ (SE)
    - Discovery+ (UK)
  Disney Channel:
    - Disney Channel (CZ)
    - Disney Channel (UK)
    - Disney Junior
    - Disney XD
    - Disney+
    - Playhouse Disney
    - Toon Disney
  E!:
    - e.tv
  ESPN:
    - ESPN+
  Food Network:
    - Cooking Channel
  FOX:
    - Fox Action Movies
    - Fox Business Network
    - FOX España
    - Fox Kids
    - Fox Nation
    - Fox Premium Series
    - FOX Sports 1
    - Fox Sports Networks
    - Fox8
    - FX
    - FXX
  Hallmark:
    - Hallmark Channel
    - Hallmark Movies & Mysteries
    - Hallmark Movies Now
  HBO:
    - HBO2
    - HBO Asia
    - HBO Canada
    - HBO Comedy
    - HBO España
    - HBO Europe
    - HBO Family
    - HBO Latin America
    - HBO Nordic
    - HBO Signature
    - HBO Zone
  History:
    - History (CA)
    - History (UK)
  ITV:
    - ITV Encore
    - ITV Wales
    - ITV1
    - ITV2
    - ITV4
    - ITVBe
    - CITV
    - STV
  Lifetime:
    - Lifetime Movies
  MTV:
    - MTV (AU/NZ)
    - MTV (UK)
    - MTV Japan
    - MTV Nederland
    - MTV2
    - MTV3
  National Geographic:
    - Nat Geo Wild
    - National Geographic Brasil
    - National Geographic Channel
    - National Geographic Wild
  Nickelodeon:
    - Nick at Nite
    - Nick Jr.
    - Nicktoons
    - TeenNick
  PBS:
    - PBS Kids
  Sky:
    - Sky 1
    - Sky Arts
    - Sky Atlantic
    - "Sky Atlantic "
    - Sky Atlantic (UK)
    - Sky Cinema
    - Sky Crime
    - Sky Deutschland
    - Sky Documentaries
    - Sky History
    - Sky Living
    - Sky Max
    - Sky Nature
    - Sky One
    - Sky Showcase
    - Sky Sports
    - Sky Two
    - Sky Witness
    - Sky1
  The CW:
    - CW seed
  TLC:
    - TLC Go
    - TLC UK
  TNT:
    - TNT (US)
  UKTV:
    - UKTV Food
    - UKTV History
    - UKTV Yesterday
  USA:
    - USA Network
  YouTube:
    - YouTube Premium
```
