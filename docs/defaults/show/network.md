# Network Collections

The `network` Default Metadata File is used to dynamically create collections based on the networks available in your library.

![](../images/network.png)

## Requirements & Recommendations

Supported Library Types: Show

## Collections Section 050

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
  # TMDb Most Common & Most Watched Network Rankings
  - ABC # American Broadcasting Company
  - CBS
  - Discovery
  - FOX
  - History
  - MTV
  - National Geographic
  - NBC
  - TBS

  ## TMDb Most Common & Top Streaming Service
  - Amazon
  - discovery+
  - iQiyi
  - Netflix
  - Tencent Video

  ## Most Watched Network & Top Streaming Service
  - AMC # 78 shows across networks

  ## TMDb Most Common ##
  - ABC TV # Australian Broadcasting Corporation
  - ABS-CBN # ABS-CBN Corporation
  - AT-X # Japanese anime television network
  - ARD # Joint organisation of Germany's regional public-service broadcasters
  - Arte # European public service channel dedicated to culture
  - BBC One # British free-to-air public broadcast television channel
  - BBC Two # British free-to-air public broadcast television channel
  - BBC Four # British free-to-air public broadcast television channel
  - bilibili # B Site, a video sharing website based in Shanghai
  - CBC Television # Canadian English-language broadcast television network
  - Channel 3 # Thai free-to-air television network
  - Channel 4 # British free-to-air public broadcast television channel
  - Channel 5 # British free-to-air public broadcast television channel
  - Fuji TV # Japanese television station based
  - GMA Network # Philippine free-to-air television
  - ITV # British free-to-air public broadcast television network
  - KBS2 # Korean Broadcasting System, an entertainment oriented network
  - Las Estrellas # A TelevisaUnivision network
  - MBC # Munhwa Broadcasting Corporation - South Korea Channel 11
  - Nippon TV # JOAX-DTV, the flagship station of the Nippon News Network and the Nippon Television Network System
  - PBS # Public Broadcasting Service is an American public broadcaster and non-commercial, free-to-air television network
  - SVT1 # Swedish public service broadcaster Sveriges Television
  - TF1 # French commercial television network owned by TF1 Group
  - Tokyo MX # JOMX-DTV, an independent television station in Tokyo, Japan, owned by the Tokyo Metropolitan Television Broadcasting Corporation
  - tv asahi # JOEX-DTV, a television station owned and operated by the TV Asahi Corporation
  - TV Globo # Brazilian free-to-air television network
  - TV Tokyo # JOTX-DTV, a television station headquartered in the Sumitomo Fudosan Roppongi Grand Tower in Roppongi, Minato, Tokyo, Japan
  - TVB Jade # Hong Kong Cantonese-language free-to-air television channel
  - tvN # South Korean nationwide pay television network owned by CJ E&M
  - RTL # Luxembourg-based international media conglomerate
  - Youku # A video hosting service based in Beijing, China
  - YouTube # online video sharing and social media platform headquartered in San Bruno, California
  - ZDF # German public-service television broadcaster based in Mainz, Rhineland-Palatinate

  ## Identical Network Names in TMDb (but different id's)
  - SBS # Special Broadcasting Service & Seoul Broadcasting System appears to be identical in TMDb
  - TV 2 # Norwegian terrestrial television channel & Danish government-owned broadcast and subscription television station
  - TV3 # Catalan public broadcaster Televisió de Catalunya & Malaysian free-to-air television channel

  ## Most Watched Network Rankings ##
  - A&E
  - Animal Planet
  - BET
  - Bravo
  - CNN
  - Comedy Central
  - ESPN
  - Food Network
  - Freeform
  - FX
  - Game Show Network
  - Hallmark
  - HGTV
  - Investigation Discovery
  - ION Television
  - Lifetime
  - Nickelodeon
  - Oxygen
  - Paramount Network # 24 shows, probably gets rolled into Paramount+ or vice versa
  - Syfy
  - Telemundo
  - The CW
  - TLC
  - TNT
  - Travel Channel
  - TV Land
  - UniMás # TelevisaUnivision channel
  - Univision # Now TelevisaUnivision
  - USA Network
  - WE tv

  ## Most Subscribed Streaming Service w/ min 50 shows
  - ALTBalaji # 61 shows
  - Apple TV+ # 153 shows
  - BluTV # 58 shows
  - Canal+ # 296 shows across networks
  - Disney+ # 285 shows
  - Globoplay # 118 shows
  - Max # 206 shows
  - Hulu # 258 shows
  - Paramount+ # 125 shows
  - Peacock # 124 shows
  - Shahid # 193 shows
  - Starz # 65 shows across networks
  - tving # 82 shows
  - Viaplay # 168 shows
  - ViuTV # 59 shows
  - ZEE5 # 184 shows

  ## Addtional Thoughts
  - ABC Family # 92 shows - addon to ABC or Freeform depending on user pref
  - BET+ # 19 shows
  - Network 10
  ## Networks with posters already made
  - ABC Kids # Should be ABC TV addon
  - Acorn TV # 17 shows
  - Adult Swim # 126 shows
  - Amazon Kids+ # 5 shows
  - Antena 3 # 179 shows
  - BBC America # 37 shows
  - Boomerang # 20 shows
  - BritBox # 17 shows
  - Cartoon Network # 236 shows across networks
  - Cartoonito # 5 shows
  - CBC # 93 shows across networks - Different than CBC Television
  - Cbeebies # 121 shows
  - Cinemax # 36 shows across networks
  - Citytv # 38 shows
  - Cooking Channel # 48 shows
  - Crunchyroll # 14 shows
  - CTV # 233 shows across networks
  - Curiosity Stream # 54 shows
  - Dave # 55 shows
  - Discovery Kids # 38 shows across network
  - Disney Channel # 532 shows across networks
  - Disney Junior # 89 shows across networks
  - Disney XD # 82 shows - could get rolled to Disney+ or Disney Channel depending on user pref
  - E! # 149 shows
  - Epix # 30 shows
  - FXX # 16 shows - mostly all also part of FX
  - Family Channel # 40 shows
  - Fox Kids # 29 shows across networks
  - Freevee # 15 shows
  - Global TV # 86 shows
  - HBO # 462 shows across networks
  - IFC # 50 shows across networks
  - IMDb TV # 11 shows
  - Nick Jr # 35 shows
  - Nicktoons # 27 shows
  - PBS Kids # 45 shows
  - Showcase # 35 shows
  - Showtime # 212 shows
  - Shudder # 18 shows
  - Sky # a lot
  - Smithsonian # 125 shows across networks
  - Spike # 139 shows
  - Stan # 24 shows
  - Sundance TV # 33 shows
  - Turner Classic Movies # 5 shows
  - truTV # 99 shows
  - UPN # 108 shows
  - USA Network #155 shows
  - Universal Kids # 23 shows
  - VH1 # 225 shows
  - Vice
```

### Default `addons`

```yaml
addons:
  ABC:
    - ABC.com
  ABC TV:
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
  CTV:
    - CTV Two
    - CTV News Channel
    - CTV Sci-Fi Channel
    - CTV Comedy Channel
    - CTV Life Channel
    - ctv.ca
  The CW:
    - CW seed
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
  Max:
    - HBO Go
  HGTV:
    - HGTV Canada
  History:
    - History Channel Italia
  Lifetime:
    - Lifetime Movies
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
  Nickelodeon:
    - Nick at Nite
  Paramount+:
    - CBS All Access # Rebranded on Mar 4, 2021
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
  Smithsonian:
    - Smithsonian Channel
    - Smithsonian Earth
  Starz:
    - Starz Encore
  TBS:
    - TBS.com
    - TBS Brasil
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
