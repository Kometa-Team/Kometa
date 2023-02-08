# Country Collections

The `country` Default Metadata File is used to dynamically create collections based on the countries available in your library.

**This file has a Movie Library [Counterpart](../movie/country).**

![](../images/country1.png)

## Requirements & Recommendations

Supported Library Types: Show

## Collections Section 080

| Collection                              | Key                                                | Description                                                                 |
|:----------------------------------------|:---------------------------------------------------|:----------------------------------------------------------------------------|
| `Country Collections`                   | `separator`                                        | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<Country>>`<br>**Example:** `Germany` | `<<2 digit ISO 3166-1 code>>`<br>**Example:** `de` | Collection of TV Shows that have this Country.                              |
| `Other Countries`                       | `other`                                            | Collection of TV Shows that are in other uncommon Countries.                |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  TV Shows:
    metadata_path:
      - pmm: country
```

## Color Style

Below is a screenshot of the alternative Color (`color`) style which can be set via the `style` template variable.

![](../images/country2.png)

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
| `include`                       | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                         |
| `exclude`                       | **Description:** Exclude these Countries from creating a Dynamic Collection.<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                     |
| `addons`                        | **Description:** Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                   |
| `append_include`                | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of [2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)                                                                                                        |
| `key_name_override`             | **Description:** Overrides the [default key_name_override dictionary](#default-key_name_override).<br>**Values:** Dictionary with `key: new_key_name` entries                                                                                                                                    |
| `country_name`                  | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                                                        |
| `country_other_name`            | **Description:** Changes the Other Collection name.<br>**Default:** `Other Countries`<br>**Values:** Any string.                                                                                                                                                                                 |
| `country_summary`               | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s filmed in <<key_name>>.`<br>**Values:** Any string.                                                                                                                           |
| `country_other_summary`         | **Description:** Changes the Other Collection summary.<br>**Default:** `<<library_translationU>>s filmed in other uncommon Countries.`<br>**Values:** Any string.                                                                                                                                |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  TV Shows:
    metadata_path:
      - pmm: country
        template_variables:
          use_other: false
          use_separator: false
          sep_style: purple
          exclude:
            - fr
          sort_by: title.asc
```

## Default values

These are lists provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
include:
  # - af     # Afghanistan
  # - ax     # Åland Islands
  # - al     # Albania
  # - dz     # Algeria
  # - ad     # Andorra
  # - ao     # Angola
  # - ai     # Anguilla
  # - aq     # Antarctica
  # - ag     # Antigua
  - ar     # Argentina
  # - am     # Armenia
  # - aw     # Aruba
  - au     # Australia
  - at     # Austria
  # - az     # Azerbaijan
  - bs     # Bahamas
  # - bh     # Bahrain
  # - bd     # Bangladesh
  # - bb     # Barbados
  # - by     # Belarus
  - be     # Belgium
  # - bz     # Belize
  # - bj     # Benin
  # - bm     # Bermuda
  # - bt     # Bhutan
  # - bo     # Bolivia
  # - bq     # Bonaire
  # - ba     # Bosnia and Herzegovina
  # - bw     # Botswana
  # - bv     # Bouvet Island
  - br     # Brazil
  # - bn     # Brunei
  - bg     # Bulgaria
  # - bf     # Burkina Faso
  # - bi     # Burundi
  # - cv     # Cabo Verde
  # - kh     # Cambodia
  # - cm     # Cameroon
  - ca     # Canada
  # - ky     # Cayman Islands
  # - cf     # Central African Republic
  # - td     # Chad
  - cl     # Chile
  - cn     # China
  # - cx     # Christmas Island
  # - cc     # Cocos (Keeling) Islands
  # - co     # Colombia
  # - km     # Comoros
  # - cg     # Congo
  # - ck     # Cook Islands
  - cr     # Costa Rica
  # - ci     # Côte d'Ivoire
  - hr     # Croatia
  # - cu     # Cuba
  # - cw     # Curaçao
  # - cy     # Cyprus
  - cz     # Czech Republic
  - dk     # Denmark
  # - dj     # Djibouti
  # - dm     # Dominica
  - do     # Dominican Republic
  # - ec     # Ecuador
  - eg     # Egypt
  # - sv     # El Salvador
  # - gq     # Equatorial Guinea
  # - er     # Eritrea
  - ee     # Estonia
  # - sz     # Eswatini
  # - et     # Ethiopia
  # - fk     # Falkland Islands
  # - fo     # Faroe Islands
  # - fj     # Fiji
  - fi     # Finland
  - fr     # France
  # - gf     # French Guiana
  # - pf     # French Polynesia
  # - ga     # Gabon
  # - gm     # Gambia
  # - ge     # Georgia
  - de     # Germany
  # - gh     # Ghana
  # - gi     # Gibraltar
  - gr     # Greece
  # - gl     # Greenland
  # - gd     # Grenada
  # - gp     # Guadeloupe
  # - gu     # Guam
  # - gt     # Guatemala
  # - gg     # Guernsey
  # - gn     # Guinea
  # - gw     # Guinea-Bissau
  # - gy     # Guyana
  # - ht     # Haiti
  # - va     # Holy See
  # - hn     # Honduras
  - hk     # Hong Kong
  - hu     # Hungary
  - is     # Iceland
  - in     # India
  - id     # Indonesia
  - ir     # Iran
  # - iq     # Iraq
  - ie     # Ireland
  # - im     # Isle of Man
  - il     # Israel
  - it     # Italy
  # - jm     # Jamaica
  - jp     # Japan
  # - je     # Jersey
  # - jo     # Jordan
  # - kz     # Kazakhstan
  # - ke     # Kenya
  # - ki     # Kiribati
  - kr     # Korea
  # - kw     # Kuwait
  # - kg     # Kyrgyzstan
  # - la     # Lao
  - lv     # Latvia
  # - lb     # Lebanon
  # - ls     # Lesotho
  # - lr     # Liberia
  # - ly     # Libya
  # - li     # Liechtenstein
  # - lt     # Lithuania
  - lu     # Luxembourg
  # - mo     # Macao
  # - mg     # Madagascar
  # - mw     # Malawi
  - my     # Malaysia
  # - mv     # Maldives
  # - ml     # Mali
  # - mt     # Malta
  # - mh     # Marshall Islands
  # - mq     # Martinique
  # - mr     # Mauritania
  # - mu     # Mauritius
  # - yt     # Mayotte
  - mx     # Mexico
  # - fm     # Micronesia
  # - md     # Moldova
  # - mc     # Monaco
  # - mn     # Mongolia
  # - me     # Montenegro
  # - ms     # Montserrat
  - ma     # Morocco
  # - mz     # Mozambique
  # - mm     # Myanmar
  # - na     # Namibia
  # - nr     # Nauru
  # - np     # Nepal
  - nl     # Netherlands
  # - nc     # New Caledonia
  - nz     # New Zealand
  # - ni     # Nicaragua
  # - ne     # Niger
  # - ng     # Nigeria
  # - nu     # Niue
  # - nf     # Norfolk Island
  # - mk     # Macedonia
  - no     # Norway
  # - om     # Oman
  - pk     # Pakistan
  # - pw     # Palau
  # - ps     # Palestine
  - pa     # Panama
  # - pg     # New Guinea
  # - py     # Paraguay
  - pe     # Peru
  - ph     # Philippines
  # - pn     # Pitcairn
  - pl     # Poland
  - pt     # Portugal
  # - pr     # Puerto Rico
  - qa     # Qatar
  # - re     # Réunion
  - ro     # Romania
  - ru     # Russia
  # - rw     # Rwanda
  # - bl     # Saint Barthélemy
  # - lc     # Saint Lucia
  # - ws     # Samoa
  # - sm     # San Marino
  # - st     # Sao Tome and Principe
  - sa     # Saudi Arabia
  # - sn     # Senegal
  - rs     # Serbia
  # - sc     # Seychelles
  # - sl     # Sierra Leone
  - sg     # Singapore
  # - sk     # Slovakia
  # - si     # Slovenia
  # - sb     # Solomon Islands
  # - so     # Somalia
  - za     # South Africa
  # - ss     # South Sudan
  - es     # Spain
  - lk     # Sri Lanka
  # - sd     # Sudan
  # - sr     # Suriname
  - se     # Sweden
  - ch     # Switzerland
  # - sy     # Syria
  # - tw     # Taiwan
  # - tj     # Tajikistan
  # - tz     # Tanzania
  - th     # Thailand
  # - tl     # Timor-Leste
  # - tg     # Togo
  # - tk     # Tokelau
  # - to     # Tonga
  # - tt     # Trinidad and Tobago
  # - tn     # Tunisia
  - tr     # Turkey
  # - tm     # Turkmenistan
  # - tc     # Turks and Caicos
  # - tv     # Tuvalu
  # - ug     # Uganda
  - ua     # Ukraine
  - ae     # United Arab Emirates
  - gb     # United Kingdom
  - us     # United States of America
  # - uy     # Uruguay
  # - uz     # Uzbekistan
  # - vu     # Vanuatu
  # - ve     # Venezuela
  - vn     # Vietnam
  # - ye     # Yemen
  # - zm     # Zambia
  # - zw     # Zimbabwe
```

### Default `key_name_override`

```yaml
key_name_override:
  kr: Korea
```
