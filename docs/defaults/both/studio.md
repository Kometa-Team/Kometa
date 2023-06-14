# Studio Collections

The `studio` Default Metadata File is used to dynamically create collections based on the studios available in your library.

This file also merges similarly named studios (such as "20th Century Fox" and "20th Century Animation") into one ("20th Century Studios")

![](../images/studio.png)

## Requirements & Recommendations

Supported Library Types: Movie, Show

## Collections Section 070

| Collection                                           | Key                                                  | Description                                                                 |
|:-----------------------------------------------------|:-----------------------------------------------------|:----------------------------------------------------------------------------|
| `Studio Collections`                                 | `separator`                                          | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<Studio>>`<br>**Example:** `Blumhouse Productions` | `<<Studio>>`<br>**Example:** `Blumhouse Productions` | Collection of Movies/Shows that have this Studio.                           |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio
  TV Shows:
    metadata_path:
      - pmm: studio
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                      | Description & Values                                                                                                                                                                                                                                            |
|:------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                         |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                      |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                            |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                      |
| `include`                     | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of Studios found in your library                                                                                                                                   |
| `exclude`                     | **Description:** Exclude these Studios from creating a Dynamic Collection.<br>**Values:** List of Studios found in your library                                                                                                                                 |
| `addons`                      | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Studios found in your library |
| `append_include`              | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of Studios found in your library                                                                                                                                  |
| `append_addons`               | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Studios found in your library                                                                                                                   |
| `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> <<library_translationU>>s`<br>**Values:** Any string with `<<key_name>>` in it.                                                                             |
| `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s that have the resolution <<key_name>>.`<br>**Values:** Any string.                                                                           |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: studio
        template_variables:
          append_include:
            - Big Bull Productions
          sort_by: title.asc
          collection_section: 4
          collection_mode: show_items
          use_separator: false
          sep_style: gray
```

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
include:
  - 3 Arts Entertainment
  - 6th & Idaho
  - 8bit
  - 20th Century Animation
  - 20th Century Studios
  - 20th Century Fox Television
  - 21 Laps Entertainment
  - 87North Productions
  - 101 Studios
  - A+E Studios
  - A-1 Pictures
  - A.C.G.T.
  - A24
  - ABC Signature
  - ABC Studios
  - Acca effe
  - Actas
  - AGBO
  - AIC
  - Ajia-Do
  - Akatsuki
  - Amazon Studios
  - Amblin Entertainment
  - AMC Studios
  - Animation Do
  - Ankama
  - APPP
  - Ardustry Entertainment
  - Arms
  - Artland
  - Artmic
  - Arvo Animation
  - Asahi Production
  - Ashi Productions
  - asread.
  - AtelierPontdarc
  - B.CMAY PICTURES
  - Bad Hat Harry Productions
  - Bad Robot
  - Bad Wolf
  - Bakken Record
  - Bandai Namco Pictures
  - Bardel Entertainment
  - BBC Studios
  - Bee Train
  - Berlanti Productions
  - Bibury Animation Studios
  - bilibili
  - Blade
  - Blown Deadline Productions
  - Blue Sky Studios
  - Blumhouse Productions
  - Blur Studio
  - Bones
  - Bosque Ranch Productions
  - Box to Box Films
  - Brain's Base
  - Brandywine Productions
  - Bridge
  - C-Station
  - C2C
  - Calt Production
  - Canal+
  - Carnival Films
  - Castle Rock Entertainment
  - CBS Productions
  - CBS Studios
  - Centropolis Entertainment
  - Chernin Entertainment
  - Children's Playground Entertainment
  - Chimp Television
  - Cinergi Pictures Entertainment
  - Cloud Hearts
  - CloverWorks
  - Colored Pencil Animation
  - Columbia Pictures
  - CoMix Wave Films
  - Connect
  - Constantin Film
  - Cowboy Films
  - Craftar Studios
  - Creators in Pack
  - CygamesPictures
  - Dark Horse Entertainment
  - David Production
  - DC Comics
  - Dino De Laurentiis Company
  - Diomedéa
  - DLE
  - Doga Kobo
  - domerica
  - Doozer
  - Dreams Salon Entertainment Culture
  - DreamWorks Studios
  - DreamWorks Pictures
  - Drive
  - Eleventh Hour Films
  - EMT Squared
  - Encourage Films
  - Endeavor Content
  - ENGI
  - Entertainment One
  - Eon Productions
  - Expectation Entertainment
  - Fandango
  - feel.
  - Felix Film
  - Fenz
  - FilmDistrict
  - FilmNation Entertainment
  - Fortiche Production
  - Frederator Studios
  - Fuqua Films
  - GAINAX
  - Gallop
  - Gallagher Films Ltd
  - Gary Sanchez Productions
  - Gaumont
  - Geek Toys
  - Gekkou
  - Gemba
  - GENCO
  - Generator Entertainment
  - Geno Studio
  - GoHands
  - Gonzo
  - Graphinica
  - Grindstone Entertainment Group
  - Group Tac
  - Hal Film Maker
  - Hallmark Channel
  - Haoliners Animation League
  - Happy Madison Productions
  - Hartswood Films
  - HBO
  - Hoods Entertainment
  - Hotline
  - Illumination Entertainment
  - Imagin
  - Imperative Entertainment
  - Ingenious Media
  - J.C.Staff
  - Jerry Bruckheimer Films
  - Jumondou
  - Kadokawa
  - Kazak Productions
  - Kennedy Miller Productions
  - Khara
  - Kilter Films
  - Kinema Citrus
  - Kjam Media
  - Kudos
  - Kyoto Animation
  - Lan Studio
  - LandQ Studio
  - Landscape Entertainment
  - Laura Ziskin Productions
  - Lay-duce
  - Legendary Pictures
  - Lerche
  - Let's Not Turn This Into a Whole Big Production
  - LIDENFILMS
  - Lionsgate
  - Lord Miller Productions
  - Lucasfilm Ltd
  - M.S.C
  - Madhouse
  - Magic Bus
  - Maho Film
  - Malevolent Films
  - Mandarin
  - Mandarin Motion Pictures Limited
  - Manglobe
  - MAPPA
  - Marvel Animation
  - Marvel Studios
  - Maximum Effort
  - Media Res
  - Metro-Goldwyn-Mayer
  - Millennium Films
  - Millepensee
  - Miramax
  - Namu Animation
  - NAZ
  - New Line Cinema
  - Nexus
  - Nickelodeon Animation Studio
  - Nippon Animation
  - Nomad
  - Nut
  - Okuruto Noboru
  - OLM
  - Orange
  - Ordet
  - Original Film
  - Orion Pictures
  - OZ
  - P.A. Works
  - P.I.C.S.
  - Paramount Animation
  - Paramount Pictures
  - Paramount Television Studios
  - Passione
  - Pb Animation Co. Ltd
  - Pierrot
  - Piki Films
  - Pine Jam
  - Pixar
  - Plan B Entertainment
  - Platinum Vision
  - PlayStation Productions
  - Plum Pictures
  - Polygon Pictures
  - Pony Canyon
  - Powerhouse Animation Studios
  - PRA
  - Production +h.
  - Production I.G
  - Production IMS
  - Production Reed
  - Project No.9
  - Prospect Park
  - Pulse Films
  - Quad
  - Radix
  - RatPac Entertainment
  - Red Dog Culture House
  - Regency Pictures
  - Reveille Productions
  - Revoroot
  - RocketScience
  - Saetta
  - SANZIGEN
  - Satelight
  - Science SARU
  - Scott Free Productions
  - Sean Daniel Company
  - Secret Hideout
  - See-Saw Films
  - Sentai Filmworks
  - Seven Arcs
  - Shaft
  - Shin-Ei Animation
  - Shogakukan
  - Showtime Networks
  - Shuka
  - Signal.MD
  - Sil-Metropole Organisation
  - SILVER LINK.
  - SISTER
  - Sixteen String Jack Productions
  - Sky studios
  - Skydance
  - Sony Pictures Animation
  - Sony Pictures
  - Spyglass Entertainment
  - Staple Entertainment
  - Studio 3Hz
  - Studio A-CAT
  - Studio Babelsberg
  - Studio Bind
  - Studio Blanc.
  - Studio Chizu
  - Studio Comet
  - Studio Deen
  - Studio Dragon
  - Studio Elle
  - Studio Flad
  - Studio Ghibli
  - Studio Gokumi
  - Studio Guts
  - Studio Hibari
  - Studio Kafka
  - Studio Kai
  - Studio Mir
  - studio MOTHER
  - Studio Palette
  - Studio Rikka
  - Studio Signpost
  - Studio VOLN
  - STUDIO4°C
  - Summit Entertainment
  - Sunrise Beyond
  - Sunrise
  - Syfy
  - Syncopy
  - SynergySP
  - Tall Ship Productions
  - Tatsunoko Production
  - Team Downey
  - Telecom Animation Film
  - Tezuka Productions
  - The Donners' Company
  - The Kennedy-Marshall Company
  - The Linson Company
  - The Littlefield Company
  - The Mark Gordon Company
  - The Weinstein Company
  - Titmouse
  - TMS Entertainment
  - TNK
  - Toei Animation
  - Tomorrow Studios
  - Topcraft
  - Touchstone Pictures
  - Touchstone Television
  - Triangle Staff
  - Trigger
  - TriStar Pictures
  - TROYCA
  - TYO Animations
  - Typhoon Graphics
  - UCP
  - ufotable
  - Universal Animation Studios
  - Universal Pictures
  - Universal Television
  - V1 Studio
  - Village Roadshow Pictures
  - W-Toon Studio
  - W. Chump and Sons
  - Walt Disney Animation Studios
  - Walt Disney Pictures
  - Warner Animation Group
  - Warner Bros. Pictures
  - Warner Bros. Television
  - Wawayu Animation
  - Wayfare Entertainment
  - White Fox
  - Wiedemann & Berg Television
  - Wit Studio
  - Wolfsbane
  - Xebec
  - Yokohama Animation Lab
  - Yostar Pictures
  - Yumeta Company
  - Zero-G
  - Zexcs
```

### Default `addons`

```yaml
addons:
  8bit:
    - 8-bit
  20th Century Studios:
    - 20th Century
    - 20th Century Animation
    - 20th Century Fox
  AIC:
    - AIC ASTA
    - AIC A.S.T.A
    - AIC Build
    - AAIC PLUS+
    - AIC RIGHTS
    - AIC Spirits
  Ajia-Do:
    - Ajiado
  Amazon Studios:
    - Amazon
  Amblin Entertainment:
    - Amblin Television
  APPP:
    - A.P.P.P.
  asread.:
    - Asread
  AtelierPontdarc:
    - Atelier Pontdarc
  B.CMAY PICTURES:
    - G.CMay Animation & Film
  Bandai Namco Pictures:
    - Bandai Visual
    - Bandai Visual Company
  BBC Studios:
    - BBC
    - BBC Studios Natural History Unit
  Bibury Animation Studios:
    - Bibury Animation CG
  Blue Sky Studios:
    - Blue Sky Films
  Cloud Hearts:
    - CLOUDHEARTS
  Columbia Pictures:
    - Columbia TriStar
  CoMix Wave Films:
    - CoMix Wave
  Craftar Studios:
    - Craftar
  CygamesPictures:
    - Cygames Pictures
  DreamWorks Studios:
    - DreamWorks
    - DreamWorks Animation
    - DreamWorks Animation Television
    - DreamWorks Classics
  EMT Squared:
    - EMT²0
  feel.:
    - Feel
  Gallop:
    - Studio Gallop
  Gaumont:
    - Gaumont International Television
  Geek Toys:
    - GEEKTOYS
  Gekkou:
    - GEKKOU Production
  GoHands:
    - Go Hands
  Gonzo:
    - Gonzo Digimation
  Hallmark Channel:
    - Hallmark Entertainment
    - Hallmark Media
    - Hallmark Movies & Mysteries
    - The Hallmark Channel
  Haoliners Animation League:
    - Haoliners Huimeng Animation
    - Haoliners Animation
  Illumination Entertainment:
    - Illumination Films
  J.C.Staff:
    - J.C. Staff
  Khara:
    - Studio Khara
  Lan Studio:
    - Studio LAN
  Legendary Pictures:
    - Legendary Television
  LIDENFILMS:
    - Liden Films
  Lucasfilm Ltd:
    - Lucasfilm
    - Lucasfilm Animation
  Mandarin:
    - Mandarin Films
    - Mandarin Television
  Marvel Studios:
    - Marvel Enterprises
    - Marvel Entertainment
    - Marvel
  Metro-Goldwyn-Mayer:
    - MGM
  New Line Cinema:
    - New Line
  Nexus:
    - Nexus Factory
  P.A. Works:
    - P.A.WORKS
  Paramount Pictures:
    - Paramount
  Pierrot:
    - Pierrot Plus
    - Studio Pierrot
  Pixar:
    - Pixar Animation Studios
  Plan B Entertainment:
    - PlanB Entertainment
  Platinum Vision:
    - PlatinumVision
  Production +h.:
    - Production +h
  RatPac Entertainment:
    - Dune Entertainment
  Regency Pictures:
    - Regency Enterprises
    - New Regency Pictures
    - Monarchy Enterprises S.a.r.l.
  Science SARU:
    - Science Saru
  Seven Arcs:
    - Seven
    - Seven Arcs Pictures
  Shogakukan:
    - Shogakukan Production
  Signal.MD:
    - Signal MD
  SILVER LINK.:
    - Silver Link
  Sky studios:
    - British Sky Broadcasting
    - British Sky Broadcasting(BSkyB)
  Sony Pictures:
    - Sony
    - Sony Pictures Animation
    - Sony Pictures Television Studios
  Studio Blanc.:
    - Studio Blanc
  Studio Deen:
    - Studio DEEN
  The Kennedy-Marshall Company:
    - The Kennedy/Marshall Company
  The Mark Gordon Company:
    - Tiger Aspect Productions
  TMS Entertainment:
    - Tokyo Movie Shinsha
  TriStar Pictures:
  - TriStar
  Universal Pictures:
    - Universal
    - Universal Animation Studios
  Walt Disney Pictures:
    - Disney
  Warner Bros. Pictures:
    - Warner
    - Warner Animation Group
  Yokohama Animation Lab:
    - Yokohama Animation Laboratory
```