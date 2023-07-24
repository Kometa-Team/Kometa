# Continent Collections

The `continent` Default Metadata File is used to dynamically create collections based on the countries within your library. The collection aims to be inclusive, with all 230 countries incorporated into seven continents.

**This file has a Show Library [Counterpart](../show/continent).**

![](../images/continent1.png)

## Requirements & Recommendations

Supported Library Types: Movie

## Collections Section 082

| Collection                                      | Key                                             | Description                                                                 |
|:------------------------------------------------|:------------------------------------------------|:----------------------------------------------------------------------------|
| `Continent Collections`                         | `separator`                                     | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<Continent>>`<br>**Example:** `South America` | `<<Continent>>`<br>**Example:** `South America` | Collection of Movies that have this Continent.                              |
| `Other Continents`                              | `other`                                         | Collection of Movies that are in other uncommon Continents.                 |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
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

| Variable                      | Description & Values                                                                                                                                                                                                                                              |
|:------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `style`                       | **Description:** Controls the visual theme of the collections created<table class="clearTable"><tr><th>Values:</th></tr><tr><td><code>white</code></td><td>White Theme</td></tr><tr><td><code>color</code></td><td>Color Theme</td></tr></table>                  |
| `limit`                       | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                                                                           |
| `limit_<<key>>`<sup>1</sup>   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                                                                        |
| `sort_by`                     | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                              |
| `sort_by_<<key>>`<sup>1</sup> | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)                                                        |
| `include`                     | **Description:** Overrides the [default include list](#default-include).<br>**Values:** List of Countries found in your library                                                                                                                                   |
| `exclude`                     | **Description:** Exclude these Countries from creating a Dynamic Collection.<br>**Values:** List of Countries found in your library                                                                                                                               |
| `addons`                      | **Description:** Overrides the [default addons dictionary](#default-addons). Defines how multiple keys can be combined under a parent key. The parent key doesn't have to already exist in Plex<br>**Values:** Dictionary List of Countries found in your library |
| `append_include`              | **Description:** Appends to the [default include list](#default-include).<br>**Values:** List of Countries found in your library                                                                                                                                  |
| `append_addons`               | **Description:** Appends to the [default addons dictionary](#default-addons).<br>**Values:** Dictionary List of Countries found in your library                                                                                                                   |
| `name_format`                 | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                         |
| `summary_format`              | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s filmed in <<key_name>>.`<br>**Values:** Any string.                                                                                            |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: continent
        template_variables:
          use_other: false
          use_separator: false
          style: color
          sep_style: purple
          exclude:
            - Europe
          sort_by: title.asc
```

## Default values

The following yml is provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
        
# List of countries other countries will be grouped into

    include:
      - Antarctica
      - New Zealand
      - Brazil
      - China
      - South Africa
      - United Kingdom
      - United States of America

# renaming of the above countries to continents

    key_name_override:
      New Zealand: Oceania
      Brazil: South America
      China: Asia
      South Africa: Africa
      United Kingdom: Europe
      United States of America: North America

# Grouping of countries into continents

    addons:
      Antarctica:
        - Bouvet Island
		
      China:
        - Afghanistan
        - Kazakhstan
        - Kyrgyzstan
        - Tajikistan
        - Turkmenistan
        - Uzbekistan
        - Japan
        - Hong Kong
        - Macao
        - India
        - Mongolia
        - Pakistan
        - Bhutan
        - Bangladesh
        - Nepal
        - Sri Lanka
        - Maldives
        - Thailand
        - Brunei
        - Cambodia
        - Indonesia
        - Lao
        - Malaysia
        - Myanmar
        - Philippines
        - Singapore
        - Vietnam
        - Viet Nam              # Duplicating smart filter functionality
        - Turkey
        - Bahrain
        - Cyprus
        - Egypt
        - Iran
        - Iraq
        - Israel
        - Jordan
        - Kuwait
        - Lebanon
        - Oman
        - Palestine
        - Qatar
        - Saudi Arabia
        - Syria
        - United Arab Emirates
        - Yemen
        - Islamic Republic of Iran           # Duplicating smart filter functionality
        - Taiwan
        - Taiwan, Province of China          # Duplicating smart filter functionality
        - Korea
        - Democratic People's Republic of Korea
        - North Korea
        - Republic of Korea 
        - South Korea 
		
      Brazil:
        - Argentina
        - Chile
        - Paraguay             
        - Uruguay
        - Falkland Islands    
        - Costa Rica
        - Belize
        - El Salvador
        - Guatemala
        - Honduras
        - Nicaragua
        - Panama
        - Peru
        - Bolivarian Republic of Venezuela    # Duplicating smart filter functionality
        - Bolivia
        - Colombia
        - Ecuador
        - Plurinational State of Bolivia      # Duplicating smart filter functionality
        - Venezuela
        - French Guiana
        - Guyana
        - Suriname
		
      United Kingdom:
        - Armenia
        - Azerbaijan
        - Georgia
        - Belgium
        - Luxembourg
        - Netherlands
        - Croatia
        - Albania
        - Bosnia and Herzegovina
        - Bulgaria
        - Macedonia
        - Montenegro
        - Republic of North Macedonia         # Duplicating smart filter functionality
        - Romania
        - Serbia
        - Slovenia
        - Denmark
        - Åland Islands
        - Faroe Islands
        - Finland
        - Greenland
        - Iceland
        - Norway
        - Svalbard and Jan Mayen
        - Sweden
        - Ireland
        - Greece
        - Poland
        - Belarus
        - Czech Republic
        - Estonia
        - Hungary
        - Latvia
        - Lithuania
        - Moldova
        - Slovakia
        - Ukraine
        - Spain
        - Andorra
        - Gibraltar 
        - Portugal
        - Austria
        - Switzerland
        - Liechtenstein
        - Russia
        - Russian Federation        # Duplicating smart filter functionality
        - Guernsey
        - Gibraltar 
        - Isle of Man
        - Jersey
        - Malta
        - Germany
        - France
        - Monaco
        - Italy
        - Holy See
        - Malta
        - San Marino
		
      United States of America:
        - Anguilla
        - Antigua
        - Aruba
        - Bahamas
        - Barbados
        - Bermuda
        - Bonaire
        - Canada
        - Cayman Islands
        - Cuba
        - Curaçao
        - Dominica
        - Dominican Republic
        - Grenada
        - Guadeloupe
        - Haiti
        - Jamaica
        - Martinique
        - Mexico
        - Montserrat
        - Puerto Rico
        - Saint Barthélemy
        - Saint Lucia
        - Trinidad and Tobago
        - Turks and Caicos

      South Africa:
        - Chad
        - Angola
        - Cameroon
        - Central African Republic
        - Congo
        - Democratic Republic of the Congo    # Duplicating smart filter functionality
        - Equatorial Guinea
        - Gabon
        - Republic of the Congo
        - Sao Tome and Principe
        - Kenya
        - Burundi
        - Comoros
        - Djibouti
        - Eritrea
        - Ethiopia
        - Madagascar
        - Malawi
        - Mauritius
        - Mayotte
        - Mozambique
        - Réunion
        - Rwanda
        - Seychelles
        - Somalia
        - South Sudan
        - Tanzania
        - Uganda
        - Zambia
        - Zimbabwe           
        - Morocco
        - Algeria
        - Egypt
        - Libya       
        - Sudan
        - Tunisia
        - Nigeria
        - Benin
        - Burkina Faso
        - Cabo Verde
        - Côte d'Ivoire
        - Gambia
        - Ghana
        - Guinea
        - Guinea-Bissau
        - Liberia
        - Mali
        - Mauritania
        - Niger
        - Senegal
        - Sierra Leone
        - Togo
        - Botswana
        - Eswatini
        - Lesotho
        - Namibia
		
      New Zealand:
        - Australia
        - Christmas Island
        - Cocos (Keeling) Islands
        - New Guinea 
        - Timor-Leste 
        - Cook Islands
        - Fiji
        - French Polynesia
        - Guam
        - Kiribati
        - Marshall Islands
        - Micronesia
        - Nauru
        - New Caledonia
        - Niue
        - Norfolk Island
        - Palau
        - Pitcairn
        - Samoa
        - Solomon Islands
        - Tokelau
        - Tonga
        - Tuvalu
        - Vanuatu
```
