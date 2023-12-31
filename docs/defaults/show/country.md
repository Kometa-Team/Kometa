# Country Collections

The `country` Default Collection File is used to dynamically create collections based on the countries available in your library.

**This file has a Movie Library [Counterpart](../movie/country.md).**

![](../images/country1.png)

## Requirements & Recommendations

Supported Library Types: Show

## Collections Section 080

| Collection                              | Key                                                | Description                                                                    |
|:----------------------------------------|:---------------------------------------------------|:-------------------------------------------------------------------------------|
| `Country Collections`                   | `separator`                                        | [Separator Collection](../separators.md) to denote the Section of Collections. |
| `<<Country>>`<br>**Example:** `Germany` | `<<2 digit ISO 3166-1 code>>`<br>**Example:** `de` | Collection of TV Shows that have this Country.                                 |
| `Other Countries`                       | `other`                                            | Collection of TV Shows that are in other uncommon Countries.                   |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  TV Shows:
    collection_files:
      - pmm: country
```

## Color Style

Below is a screenshot of the alternative Color (`color`) style which can be set via the `style` template variable.

![](../images/country2.png)

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified will use its default value if it has one if not it's just ignored.

??? info "Click to expand"

    === "File-Specific Template Variables"

        The below template variables are available specifically for this PMM Defaults file.

        Be sure to also check out the "Shared Template Variables" tab for additional variables.

        This file contains a [Separator](../separators.md) so all [Shared Separator Variables](../separators.md#shared-separator-variables) are available as well.

        | Variable                        | Description & Values                                                                                                                                                                                                                                                                             |
        |:--------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | `style`                         | **Description:** Controls the visual theme of the collections created<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>white</code></td><td>White Theme</td></tr><tr><td><code>color</code></td><td>Color Theme</td></tr></table>                                                 |
        | `limit`                         | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater than 0                                                                                                                                                                          |
        | `limit_<<key>>`<sup>1</sup>     | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater than 0                                                                                                                                                       |
        | `sync_mode`                     | **Description:** Changes the Sync Mode for all collections in a Defaults file.<br>**Default:** `sync`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sync_mode_<<key>>`<sup>1</sup> | **Description:** Changes the Sync Mode of the specified key's collection.<br>**Default:** `sync_mode`<br>**Values:**<table class="clearTable"><tr><td>`sync`</td><td>Add and Remove Items based on Builders</td></tr><tr><td>`append`</td><td>Only Add Items based on Builders</td></tr></table> |
        | `sort_by`                       | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                      |
        | `sort_by_<<key>>`<sup>1</sup>   | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../files/builders/smart.md#sort-options)                                                                                                |
        | `include`                       | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                         |
        | `exclude`                       | **Description:** Exclude these Countries from creating a Dynamic Collection.<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                     |
        | `addons`                        | **Description:** Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                   |
        | `append_include`                | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                        |
        | `remove_include`                | **Description:** Removes from the [default include list](#default-include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                      |
        | `append_addons`                 | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                         |
        | `remove_addons`                 | **Description:** Removes from the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                       |
        | `key_name_override`             | **Description:** Overrides the [default key_name_override dictionary](#default-key_name_override).<br>**Values:** Dictionary with `key: new_key_name` entries                                                                                                                                    |
        | `name_format`                   | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                        |
        | `summary_format`                | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s filmed in <<key_name>>.`<br>**Values:** Any string.                                                                                                                           |

        1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

    === "Shared Template Variables"

        {%
          include-markdown "../collection_variables.md"
        %}

    ### Example Template Variable Amendments

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    ???+ tip

        Anywhere you see this icon:
      
        > :fontawesome-solid-circle-plus:
      
        That's a tooltip, you can press them to get more information.

    ```yaml
    libraries:
      Movies:
        collection_files:
          - pmm: country
            template_variables:
              use_other: false #(1)!
              use_separator: false #(2)!
              style: color #(3)!
              exclude:
                - France #(4)!
              sort_by: title.asc
    ```

    1.  Do not create the "Other Countries" collection
    2.  Do not create a "Country Collections" separator
    3.  Set the [Color Style](#color-style)
    4.  Exclude "France" from the list of collections that are created

## Default values

??? tip

    These are lists provided for reference to show what values will be in use if you do no customization.  **These do not show how to change a name or a list.**

    If you want to customize these values, use the methods described above.

    **Default `include`**:

    ```yaml
    include:
          # Northern Africa:
            - dz                    # Algeria
            - eg                    # Egypt
            - ly                    # Libya
            - ma                    # Morocco
            - sd                    # Sudan
            - tn                    # Tunisia
            - eh                    # Western Sahara
          # Eastern Africa:
            - io                    # British Indian Ocean Territory
            - bi                    # Burundi
            - km                    # Comoros
            - dj                    # Djibouti
            - er                    # Eritrea
            - et                    # Ethiopia
            - tf                    # French Southern Territories
            - ke                    # Kenya
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
            - ug                    # Uganda
            - tz                    # Tanzania [United Republic of Tanzania]
            - zm                    # Zambia
            - zw                    # Zimbabwe
          # Central Africa:
            - ao                    # Angola
            - cm                    # Cameroon
            - cf                    # Central African Republic
            - td                    # Chad
            - cg                    # Republic of the Congo [Congo]
            - cd                    # Democratic Republic of the Congo
            - gq                    # Equatorial Guinea
            - ga                    # Gabon
            - st                    # São Tomé and Príncipe [Sao Tome and Principe]
          # Southern Africa:
            - bw                    # Botswana
            - sz                    # Eswatini [Swaziland]
            - ls                    # Lesotho
            - na                    # Namibia
            - za                    # South Africa
          # Western Africa:
            - bj                    # Benin
            - bf                    # Burkina Faso
            - cv                    # Cape Verde [Cabo Verde]
            - ci                    # Côte d'Ivoire [Côte d’Ivoire] [Ivory Coast]
            - gm                    # Gambia
            - gh                    # Ghana
            - gn                    # Guinea
            - gw                    # Guinea-Bissau
            - lr                    # Liberia
            - ml                    # Mali
            - mr                    # Mauritania
            - ne                    # Niger
            - ng                    # Nigeria
            - sh                    # Saint Helena, Ascension and Tristan da Cunha [Ascension] [Tristan da Cunha] [Saint Helena]
            - sn                    # Senegal
            - sl                    # Sierra Leone
            - tg                    # Togo
          # Caribbean:
            - ai                    # Anguilla
            - ag                    # Antigua and Barbuda [Antigua] [Barbuda]
            - aw                    # Aruba
            - bs                    # Bahamas
            - bb                    # Barbados
            - bq                    # Bonaire, Sint Eustatius and Saba [Bonaire] [Sint Eustatius] [Saba]
            - an                    # Netherlands Antilles
            - vg                    # British Virgin Islands
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
            - kn                    # Saint Kitts and Nevis
            - lc                    # Saint Lucia
            - mf                    # Saint Martin
            - vc                    # Saint Vincent and the Grenadines
            - sx                    # Sint Maarten
            - tt                    # Trinidad and Tobago
            - tc                    # Turks and Caicos Islands
            - vi                    # US Virgin Islands [U.S. Virgin Islands] [United States Virgin Islands]
          # Central America:
            - bz                    # Belize
            - cr                    # Costa Rica
            - sv                    # El Salvador
            - gt                    # Guatemala
            - hn                    # Honduras
            - mx                    # Mexico
            - ni                    # Nicaragua
            - pa                    # Panama
          # South America:
            - ar                    # Argentina
            - bo                    # Bolivia [Plurinational State of Bolivia]
            - bv                    # Bouvet Island
            - br                    # Brazil
            - cl                    # Chile
            - co                    # Colombia
            - ec                    # Ecuador
            - fk                    # Falkland Islands [Malvinas]
            - gf                    # French Guiana
            - gy                    # Guyana
            - py                    # Paraguay
            - pe                    # Peru
            - gs                    # South Georgia and the South Sandwich Islands [South Georgia] [South Sandwich Islands]
            - sr                    # Suriname
            - uy                    # Uruguay
            - ve                    # Venezuela [Bolivarian Republic of Venezuela]
          # North America:
            - bm                    # Bermuda
            - ca                    # Canada
            - gl                    # Greenland
            - pm                    # Saint Pierre and Miquelon
            - us                    # United States [United States of America]
          # Antarctica:
            - aq                    # Antarctica
          # Central Asia:
            - kz                    # Kazakhstan
            - kg                    # Kyrgyzstan
            - tj                    # Tajikistan
            - tm                    # Turkmenistan
            - uz                    # Uzbekistan
          # Eastern Asia:
            - cn                    # China
            - hk                    # Hong Kong
            - mo                    # Macao
            - kp                    # North Korea [Democratic People's Republic of Korea]
            - jp                    # Japan
            - mn                    # Mongolia
            - kr                    # South Korea [Republic of Korea] [Korea]
            - tw                    # Taiwan [Taiwan, Province of China]
          # South-Eastern Asia:
            - bn                    # Brunei [Brunei Darussalam]
            - kh                    # Cambodia
            - id                    # Indonesia
            - la                    # Laos [Lao People's Democratic Republic] [Lao]
            - my                    # Malaysia
            - mm                    # Myanmar
            - ph                    # Philippines
            - sg                    # Singapore
            - th                    # Thailand
            - tp                    # East Timor
            - vn                    # Vietnam [Viet Nam]
          # Southern Asia:
            - af                    # Afghanistan
            - bd                    # Bangladesh
            - bt                    # Bhutan
            - in                    # India
            - ir                    # Iran [Islamic Republic of Iran]
            - mv                    # Maldives
            - np                    # Nepal
            - pk                    # Pakistan
            - lk                    # Sri Lanka
          # Western Asia:
            - am                    # Armenia
            - az                    # Azerbaijan
            - bh                    # Bahrain
            - cy                    # Cyprus
            - ge                    # Georgia
            - iq                    # Iraq
            - il                    # Israel
            - jo                    # Jordan
            - kw                    # Kuwait
            - lb                    # Lebanon
            - om                    # Oman
            - qa                    # Qatar
            - sa                    # Saudi Arabia
            - ps                    # Palestine [State of Palestine]
            - sy                    # Syria [Syrian Arab Republic]
            - tr                    # Turkey [Türkiye]
            - ae                    # United Arab Emirates
            - ye                    # Yemen
          # Eastern Europe:
            - by                    # Belarus
            - bg                    # Bulgaria
            - cz                    # Czech Republic [Czechia]
            - hu                    # Hungary
            - pl                    # Poland
            - md                    # Moldova [Republic of Moldova]
            - ro                    # Romania
            - ru                    # Russia [Russian Federation]
            - sk                    # Slovakia
            - ua                    # Ukraine
          # Northern Europe:
            - ax                    # Åland Islands
            - gg                    # Guernsey
            - je                    # Jersey
            - cq                    # Sark
            - dk                    # Denmark
            - ee                    # Estonia
            - fo                    # Faroe Islands
            - fi                    # Finland
            - is                    # Iceland
            - ie                    # Ireland
            - im                    # Isle of Man
            - lv                    # Latvia
            - lt                    # Lithuania
            - no                    # Norway
            - sj                    # Svalbard and Jan Mayen Islands [Svalbard and Jan Mayen]
            - se                    # Sweden
            - gb                    # United Kingdom
          # Southern Europe:
            - al                    # Albania
            - ad                    # Andorra
            - ba                    # Bosnia and Herzegovina
            - hr                    # Croatia
            - gi                    # Gibraltar
            - gr                    # Greece
            - xk                    # Kosovo
            - va                    # Vatican City [Holy See]
            - it                    # Italy
            - mt                    # Malta
            - me                    # Montenegro
            - mk                    # North Macedonia [Macedonia] [Republic of North Macedonia]
            - pt                    # Portugal
            - sm                    # San Marino
            - rs                    # Serbia
            - si                    # Slovenia
            - es                    # Spain
            - yu                    # Yugoslavia
          # Western Europe:
            - at                    # Austria
            - be                    # Belgium
            - fr                    # France [French Republic]
            - de                    # Germany
            - li                    # Liechtenstein
            - lu                    # Luxembourg
            - mc                    # Monaco
            - nl                    # Netherlands
            - ch                    # Switzerland
          # Australia and New Zealand:
            - au                    # Australia
            - cx                    # Christmas Island
            - cc                    # Cocos (Keeling) Islands
            - hm                    # Heard Island and McDonald Islands
            - nz                    # New Zealand
            - nf                    # Norfolk Island
          # Melanesia:
            - fj                    # Fiji
            - nc                    # New Caledonia
            - pg                    # Papua New Guinea [New Guinea]
            - sb                    # Solomon Islands
            - vu                    # Vanuatu
          # Micronesia:
            - gu                    # Guam
            - ki                    # Kiribati
            - mh                    # Marshall Islands
            - fm                    # Micronesia [Federated States of Micronesia]
            - nr                    # Nauru
            - mp                    # Northern Mariana Islands
            - pw                    # Palau
            - um                    # US Minor Outlying Islands
          # Polynesia:
            - as                    # American Samoa
            - ck                    # Cook Islands
            - pf                    # French Polynesia
            - nu                    # Niue
            - pn                    # Pitcairn [Pitcairn Islands]
            - ws                    # Samoa
            - tk                    # Tokelau
            - to                    # Tonga
            - tv                    # Tuvalu
            - wf                    # Wallis and Futuna Islands
    ```

    **Default `addons`**:

    ```yaml
        addons:
          cd:                       # Democratic Republic of the Congo
            - zr                    # Zaire
          mm:                       # Myanmar
            - bu                    # Burma
          tp:                       # East Timor
            - tl                    # Timor-Leste
          cz:                       # Czech Republic
            - cs                    # Czechoslovakia
          ru:                       # Russia
            - su                    # Soviet Union
          de:                       # Germany
            - dd                    # East Germany
    ```