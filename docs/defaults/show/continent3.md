# Continent Collections

The `continent` Default Metadata File is used to dynamically create collections based on the countries items are tagged with in your library. The collection aims to be inclusive, with all 230 countries incorporated into seven continents.

**This file has a Movie Library [Counterpart](../movie/continent).**

![](../images/continent1.png)

## Requirements & Recommendations

Supported Library Types: Show

## Collections Section 082

| Collection                              | Key                                                | Description                                                                 |
|:----------------------------------------|:---------------------------------------------------|:----------------------------------------------------------------------------|
| `Continent Collections`                   | `separator`                                        | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<Continent>>`<br>**Example:** `South America` | `<<2 digit ISO 3166-1 code>>`<br>**Example:** `br` | Collection of TV Shows that have this Continent.                              |
| `Other Continents`                       | `other`                                            | Collection of TV Shows that are in other uncommon Continents.                |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  TV Shows:
    metadata_path:
      - pmm: continent
```

## Color Style

Below is a screenshot of the alternative Color (`color`) style which can be set via the `style` template variable.

![](../images/continent2.png)

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../collection_variables) are available as well as the additional Variables below which can be used to customize the file.

This file contains a [Separator](../separators) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

| Variable                        | Description & Values                                                                                                                                                                                                                                                                             |
|:--------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `style`                         | **Description:** Controls the visual theme of the collections created<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>white</code></td><td>White Theme</td></tr><tr><td><code>color</code></td><td>Color Theme</td></tr></table>                                                 |
| `limit`                         | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                                                          |
| `limit_<<key>>`<sup>1</sup>     | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                                                       |
| `sync_mode`                     | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
| `sync_mode_<<key>>`<sup>1</sup> | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
| `sort_by`                       | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                                             |
| `sort_by_<<key>>`<sup>1</sup>   | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                                                       |
| `include`                       | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_continent_codes)                                                                                                         |
| `exclude`                       | **Description:** Exclude these Countries from creating a Dynamic Collection.<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_continent_codes)                                                                                                     |
| `addons`                        | **Description:** Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_continent_codes)                                   |
| `append_include`                | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_continent_codes)                                                                                                        |
| `key_name_override`             | **Description:** Overrides the [default key_name_override dictionary](#default-key_name_override).<br>**Values:** Dictionary with `key: new_key_name` entries                                                                                                                                    |
| `name_format`                   | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                        |
| `summary_format`                | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s filmed in <<key_name>>.`<br>**Values:** Any string.                                                                                                                           |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - pmm: continent
        template_variables:
          use_other: false
          use_separator: false
          sep_style: purple
          exclude:
            - nz
          sort_by: title.asc
```

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
# Countries where other countries will be grouped into
    
include:
  - aq                       # Antarctica
  - nz                       # New Zealand
  - br                       # Brazil
  - cn                       # China
  - za                       # South Africa
  - gb                       # United Kingdom
  - us                       # United States of America
```

### Default `key_name_override`

```yaml
# Name changes for the above countries

key_name_override:
  nz: Oceania
  br: South America
  cn: Asia
  za: Africa
  gb: Europe
  us: North America
```
### Default `addons`

```yaml
# Grouping of countries into continents

    addons:
      aq:                     # Antarctica  
        - bv                    # Bouvet Island             
      cn:                     # China - Asia
        - af                    # Afghanistan
        - kz                    # Kazakhstan
        - kg                    # Kyrgyzstan
        - tj                    # Tajikistan
        - tm                    # Turkmenistan
        - uz                    # Uzbekistan
        - mn                    # Mongolia
        - in                    # India
        - pk                    # Pakistan
        - bt                    # Bhutan
        - bd                    # Bangladesh
        - np                    # Nepal
        - lk                    # Sri Lanka
        - mv                    # Maldives
        - jp                    # Japan
        - hk                    # Hong Kong
        - mo                    # Macao 
        - th                    # Thailand
        - bn                    # Brunei
        - kh                    # Cambodia
        - id                    # Indonesia
        - la                    # Lao
        - my                    # Malaysia
        - mm                    # Myanmar
        - ph                    # Philippines
        - sg                    # Singapore
        - vn                    # Vietnam        
        - tr                    # Turkey
        - bh                    # Bahrain
        - cy                    # Cyprus
        - eg                    # Egypt                
        - ir                    # Iran
        - iq                    # Iraq
        - il                    # Israel
        - jo                    # Jordan
        - kw                    # Kuwait
        - lb                    # Lebanon
        - om                    # Oman
        - ps                    # Palestine
        - qa                    # Qatar
        - sa                    # Saudi Arabia
        - sy                    # Syria
        - ae                    # United Arab Emirates
        - ye                    # Yemen
        - tw                    # Taiwan
        - kr                    # Korea
      br:                     # Brazil - South America
        - ar                    # Argentina
        - cl                    # Chile
        - py                    # Paraguay   
        - uy                    # Uruguay
        - fk                    # Falkland Islands
        - cr                    # Costa Rica
        - bz                    # Belize
        - sv                    # El Salvador
        - gt                    # Guatemala
        - hn                    # Honduras
        - ni                    # Nicaragua
        - pa                    # Panama
        - pe                    # Peru
        - bo                    # Bolivia
        - co                    # Colombia
        - ec                    # Ecuador
        - ve                    # Venezuela
        - gf                    # French Guiana
        - gy                    # Guyana
        - sr                    # Suriname           
      gb:                     # United Kingdom - Europe
        - am                    # Armenia
        - az                    # Azerbaijan
        - ge                    # Georgia
        - be                    # Belgium
        - lu                    # Luxembourg
        - nl                    # Netherlands
        - hr                    # Croatia 
        - al                    # Albania
        - ba                    # Bosnia and Herzegovina
        - bg                    # Bulgaria
        - mk                    # Macedonia
        - me                    # Montenegro
        - ro                    # Romania
        - rs                    # Serbia
        - si                    # Slovenia
        - dk                    # Denmark
        - ax                    # Åland Islands
        - fo                    # Faroe Islands
        - fi                    # Finland
        - gl                    # Greenland
        - is                    # Iceland
        - no                    # Norway
        - sj                    # Svalbard and Jan Mayen
        - se                    # Sweden
        - ie                    # Ireland
        - gr                    # Greece
        - pl                    # Poland
        - by                    # Belarus
        - cz                    # Czech Republic
        - ee                    # Estonia
        - hu                    # Hungary
        - lv                    # Latvia
        - lt                    # Lithuania
        - md                    # Moldova
        - sk                    # Slovakia
        - ua                    # Ukraine
        - es                    # Spain
        - ad                    # Andorra 
        - pt                    # Portugal
        - ch                    # Switzerland
        - at                    # Austria
        - li                    # Liechtenstein
        - ru                    # Russia
        - gg                    # Guernsey
        - gi                    # Gibraltar
        - im                    # Isle of Man
        - je                    # Jersey
        - mt                    # Malta
        - de                    # Germany
        - fr                    # France
        - mc                    # Monaco
        - it                    # Italy 
        - va                    # Holy See
        - sm                    # San Marino
      us:                     # United States of America - North America
        - bs                    # Bahamas
        - ai                    # Anguilla
        - ag                    # Antigua
        - aw                    # Aruba
        - bb                    # Barbados
        - bm                    # Bermuda
        - bq                    # Bonaire
        - ky                    # Cayman Islands
        - cu                    # Cuba
        - cw                    # Curaçao
        - dm                    # Dominica
        - do                    # Dominican Republic
        - gd                    # Grenada
        - gp                    # Guadeloupe
        - ht                    # Haiti
        - jm                    # Jamaica
        - mq                    # Martinique
        - ms                    # Montserrat
        - pr                    # Puerto Rico
        - bl                    # Saint Barthélemy
        - lc                    # Saint Lucia
        - tt                    # Trinidad and Tobago
        - tc                    # Turks and Caicos
        - ca                    # Canada
        - mx                    # Mexico
      za:                     # South Africa - Africa
        - td                    # Chad
        - ao                    # Angola
        - cm                    # Cameroon
        - cf                    # Central African Republic
        - cg                    # Congo
        - gq                    # Equatorial Guinea
        - ga                    # Gabon
        - st                    # Sao Tome and Principe
        - ke                    # Kenya
        - bi                    # Burundi
        - km                    # Comoros
        - dj                    # Djibouti
        - er                    # Eritrea
        - et                    # Ethiopia
        - mg                    # Madagascar
        - mw                    # Malawi
        - mu                    # Mauritius
        - yt                    # Mayotte
        - mz                    # Mozambique
        - re                    # Réunion
        - rw                    # Rwanda
        - sc                    # Seychelles
        - so                    # Somalia
        - ss                    # South Sudan
        - tz                    # Tanzania
        - ug                    # Uganda
        - zm                    # Zambia
        - zw                    # Zimbabwe  
        - ma                    # Morocco   
        - dz                    # Algeria
        - eg                    # Egypt
        - ly                    # Libya       
        - sd                    # Sudan
        - tn                    # Tunisia  
        - ng                    # Nigeria
        - bj                    # Benin
        - bf                    # Burkina Faso
        - cv                    # Cabo Verde
        - ci                    # Côte d'Ivoire
        - gm                    # Gambia
        - gh                    # Ghana
        - gn                    # Guinea
        - gw                    # Guinea-Bissau
        - lr                    # Liberia
        - ml                    # Mali
        - mr                    # Mauritania
        - ne                    # Niger
        - sn                    # Senegal
        - sl                    # Sierra Leone
        - tg                    # Togo 
        - bw                    # Botswana
        - sz                    # Eswatini
        - ls                    # Lesotho
        - na                    # Namibia        
      nz:                     # New Zealand - Oceania
        - au                    # Australia
        - cx                    # Christmas Island
        - cc                    # Cocos (Keeling) Islands
        - pg                    # New Guinea    
        - tl                    # Timor-Leste 
        - ck                    # Cook Islands
        - fj                    # Fiji
        - pf                    # French Polynesia
        - gu                    # Guam
        - ki                    # Kiribati
        - mh                    # Marshall Islands
        - fm                    # Micronesia
        - nr                    # Nauru
        - nc                    # New Caledonia
        - nu                    # Niue
        - nf                    # Norfolk Island
        - pw                    # Palau
        - pn                    # Pitcairn
        - ws                    # Samoa
        - sb                    # Solomon Islands
        - tk                    # Tokelau
        - to                    # Tonga
        - tv                    # Tuvalu
        - vu                    # Vanuatu
```