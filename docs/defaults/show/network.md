# Network Collections

The `network` Default Metadata File is used to dynamically create collections based on the networks available in your library.

![](../images/network.png)

## Requirements & Recommendations

Supported Library Types: Show

## Collections Section 050

| Collection                          | Key                                 | Description                                                                 |
|:------------------------------------|:------------------------------------|:----------------------------------------------------------------------------|
| `Network Collections`               | `separator`                         | [Separator Collection](../separators.md) to denote the Section of Collections. |
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

All [Shared Collection Variables](../collection_variables.md) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators.md) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                      | Description & Values                                                                                                                                                                                                                                             |
|:------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                          |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                       |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../builders/smart.md#sort-options)                                             |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../builders/smart.md#sort-options)                                                       |
| `include`                     | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of Networks found in your library                                                                                                                                   |
| `exclude`                     | **Description:** Exclude these Networks from creating a Dynamic Collection.<br>**Values:** List of Networks found in your library                                                                                                                                |
| `addons`                      | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Networks found in your library |
| `append_include`              | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of Networks found in your library                                                                                                                                  |
| `remove_include`              | **Description:** Removes from the [default include list](#default-include).<br>**Values:** List of Networks found in your library                                                                                                                                |
| `append_addons`               | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Networks found in your library                                                                                                                   |
| `remove_addons`               | **Description:** Removes from the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Networks found in your library                                                                                                                 |
| `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                        |
| `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s broadcast on <<key_name>>.`<br>**Values:** Any string.                                                                                        |

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
    - "#0"
    - ABC
    - ABC Family
    - ABC Kids
    - ABC TV
    - ABS-CBN
    - Acorn TV
    - Adult Swim
    - AHC
    - Alibi
    - ALTBalaji
    - Amazon Kids+
    - AMC
    - AMC+
    - Animal Planet
    - Antena 3
    - Apple TV+
    - ARD
    - Arte
    - Atresplayer Premium
    - AT-X
    - Audience
    - AXN
    - Azteca Uno
    - A&E
    - BBC America
    - BBC Four
    - BBC iPlayer
    - BBC One
    - BBC Three
    - BBC Two
    - BET
    - BET+
    - bilibili
    - BluTV
    - Boomerang
    - Bravo
    - BritBox
    - C More
    - Canale 5
    - Canal+
    - Cartoon Network
    - Cartoonito
    - CBC
    - CBC Television
    - Cbeebies
    - CBS
    - Channel 3
    - Channel 4
    - Channel 5
    - CHCH-DT
    - Cinemax
    - Citytv
    - CNN
    - Comedy Central
    - Cooking Channel
    - Crackle
    - Criterion Channel
    - Crunchyroll
    - CTV
    - Cuatro
    - Curiosity Stream
    - Dave
    - DC Universe
    - Discovery
    - Discovery Kids
    - discovery+
    - Disney Channel
    - Disney Junior
    - Disney XD
    - Disney+
    - DR1
    - Eden
    - Elisa Viihde
    - Elisa Viihde Viaplay
    - Epix
    - ESPN
    - E!
    - Facebook Watch
    - Family Channel
    - Ficción Producciones
    - Flooxer
    - Food Network
    - FOX
    - Fox Kids
    - France 2
    - Freeform
    - Freevee
    - Fuji TV
    - FX
    - FXX
    - GAİN
    - Game Show Network
    - Global TV
    - Globoplay
    - GMA Network
    - Hallmark
    - HBO
    - HBO Max
    - HGTV
    - History
    - HOT3
    - Hulu
    - ICTV
    - IFC
    - IMDb TV
    - Investigation Discovery
    - ION Television
    - iQiyi
    - ITV
    - ITV Encore
    - ITV1
    - ITV2
    - ITV3
    - ITV4
    - ITVBe
    - ITVX
    - joyn
    - Kan 11
    - KBS2
    - Kids WB
    - La 1
    - La Une
    - Las Estrellas
    - Lifetime
    - Lionsgate+
    - Logo
    - MasterClass
    - Max
    - MBC
    - MGM+
    - mitele
    - Movistar Plus+
    - MTV
    - M-Net
    - National Geographic
    - NBC
    - Netflix
    - Network 10
    - NHK
    - Nick
    - Nick Jr
    - Nickelodeon
    - Nicktoons
    - Nine Network
    - Nippon TV
    - NRK1
    - OCS City
    - OCS Max
    - ORF
    - Oxygen
    - Pantaya
    - Paramount Network
    - Paramount+
    - PBS
    - PBS Kids
    - Peacock
    - Planète+ A&E
    - Prime Video
    - Rai 1
    - Reelz
    - The Roku Channel
    - RTÉ One
    - RTL
    - RTL Télé
    - RTP1
    - RÚV
    - S4C
    - SAT.1
    - SBS
    - Science
    - Shahid
    - Showcase
    - Showmax
    - Showtime
    - Shudder
    - Sky
    - Smithsonian
    - Space
    - Spectrum
    - Spike
    - Stan
    - Starz
    - STAR+
    - Sundance TV
    - SVT1
    - Syfy
    - Syndication
    - TBS
    - Telecinco
    - Telefe
    - Telemundo
    - Televisión de Galicia
    - Televisión Pública Argentina
    - Tencent Video
    - TF1
    - The CW
    - The Roku Channel
    - The WB
    - TLC
    - TNT
    - Tokyo MX
    - Travel Channel
    - truTV
    - Turner Classic Movies
    - TV 2
    - tv asahi
    - TV Globo
    - TV Land
    - TV Tokyo
    - TV3
    - TV4
    - TVB Jade
    - tving
    - tvN
    - TVNZ 1
    - TVP1
    - UKTV
    - UniMás
    - Universal Kids
    - Universal TV
    - Univision
    - UPN
    - USA Network
    - VH1
    - Viaplay
    - Vice
    - Virgin Media One
    - ViuTV
    - ViX+
    - VRT 1
    - VTM
    - W
    - WE tv
    - YLE
    - Youku
    - YouTube
    - ZDF
    - ZEE5
```

### Default `addons`

```yaml

addons:
  ABC:
    - ABC.com
  ABC TV:
    - ABC (AU)
    - ABC Comedy
    - ABC Me
    - ABC News
    - ABC iview
  AMC:
    - AMC.com
  Animal Planet:
    - Animal Planet Brasil
    - Animal Planet Deutschland
  BET:
    - BET Her
  Canal+:
    - Canal+ Poland
    - Canal+ Family
    - Canal+ Discovery
    - Canal+ Afrique
  Cartoon Network:
    - Cartoon Network Latin America
    - Cartoon Network Anything
  CBC:
    - CBCDrama
  CBC Television:
    - CBC Gem
    - CBC News Network
    - CBC Comedy
  CBS:
    - CBS.com
    - CBS All Access
  CTV:
    - CTV Two
    - CTV News Channel
    - CTV Sci-Fi Channel
    - CTV Comedy Channel
    - CTV Life Channel
    - ctv.ca
  Discovery:
    - Discovery Health Channel
    - Discovery Channel
    - Discovery Home & Health Brasil
    - Discovery Family
    - Discovery Real Time
    - Discovery Asia
    - Discovery Home & Health
    - Discovery Life
    - Discovery World
    - Discovery Science
  Disney Channel:
    - Toon Disney
    - Playhouse Disney
    - Disney Channel Asia
    - disney.com
    - Disney Channel Middle East
  Disney Junior:
    - Disney Junior Latin America
    - Disney Junior Brasil
  Disney+:
    - Disney+ Hotstar
  ESPN:
    - ESPN2
    - ESPN+
    - ESPN Classic
    - ESPNU
    - ESPNews
    - ESPN Australia
    - Sony ESPN
    - ESPN.com
    - ESPN Deportes
  FOX:
    - Fox
    - Fox News Channel
    - Fox Sports
    - Fox Reality Channel
    - Fox Sports Networks
    - Fox Latin America
    - Fox Brasil
    - Fox Soccer
    - Fox Sports 2
    - Fox Nation
    - Fox Sports 1
    - fox.com
    - Fox Sports Detroit
  Freevee:
    - Amazon Freevee
  Hallmark:
    - Hallmark Channel
    - Hallmark Drama
    - Hallmark Movie & Mysteries
    - Hallmark Movies Now
  HBO:
    - HBO Brasil
    - HBO Europe
    - HBO Asia
    - HBO Latin America
    - HBO España
    - HBO Nordic
    - HBO Canada
    - HBO Family
    - HBO Mundi
  HGTV:
    - HGTV Canada
  History:
    - History Channel Italia
    - H2
  Lifetime:
    - Lifetime Movies
  Max:
    - HBO Go
    - HBO Max
  MTV:
    - MTV2
    - MTV3
    - MTV Lebanon
    - MTV Latin America
    - MTV Italia
    - MTV Australia
    - MTV Canada
    - MTV Global
    - MTV Nederland
  National Geographic:
    - National Geographic Channel
    - National Geographic Brasil
    - National Geographic Latinoamerica
    - National Geographic India
  NBC:
    - CNBC
    - MSNBC
    - NBCSN
    - CNBC Europe
    - CNBC Asia
    - WNBC
    - Nikkei CNBC
    - KNBC
    - CNBC World
    - CNBC TV18
    - NBC Weather Plus
    - NBC Radio Network
  Network Ten:
    - Network 10
  Nickelodeon:
    - Nick at Nite
  ReelzChannel:
    - Reelz
  Sky:
    - Sky One
    - Sky Atlantic
    - Sky Arts
    - Sky History
    - Sky Living
    - Sky Crime
    - Sky Uno
    - Sky Max
    - Sky Sports
    - Sky Documentaries
    - Sky Nature
    - Sky News
    - Sky Cinema
    - Sky News Australia
    - Sky Italia
    - Sky Comedy
    - Sky Sports F1
    - Sky Two
    - Sky Witness
    - sky Travel
    - Sky Vision
    - Sky News Weather Channel
    - SkyShowtime
  Smithsonian:
    - Smithsonian Channel
    - Smithsonian Earth
  Spike:
    - Spike TV
  Starz:
    - Starz Encore
  Sundance TV:
    - SundanceTV
  TBS:
    - TBS.com
    - TBS Brasil
  The CW:
    - CW seed
  TNT:
    - TNT Comedy
    - TNT Latin America
    - TNT España
    - TNT Serie
    - TNT Glitz
  Travel Channel:
    - Travel Channel United Kingdom
  VH1:
    - VH1 Classic
  Vice:
    - Viceland
    - Vice TV
    - Vice.com
```