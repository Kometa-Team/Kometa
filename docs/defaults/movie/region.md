# Region Collections

The `region` Default Metadata File is used to dynamically create collections based on the countries within your library. The collection aims to be inclusive, with all 230 countries incorporated into 39 countries or collections of countries. Some care has been taken to ensure all countries are included, and the groupings won't fit well with everyone's collections.  Western and Southern Europe, Oceania, and North America could be useful groupings for those libraries with more of an Asian focus, for instance. Please see the comments in the yml below where a decision point might be seen as controversial. You are welcome to edit this to fit your own audience's needs.

**This file has a Show Library [Counterpart](../show/region).**

![](../images/region1.png)

## Requirements & Recommendations

Supported Library Types: Movie

## Collections Section 081

| Collection                            | Key                                     | Description                                                                 |
|:--------------------------------------|:----------------------------------------|:----------------------------------------------------------------------------|
| `Region Collections`                  | `separator`                             | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<Region>>`<br>**Example:** `Nordic` | `<<Region>>`<br>**Example:** `Nordic`   | Collection of Movies that have been tagged with countries in this region.   |
| `Other Regions`                       | `other`                                 | Collection of Movies that are in other uncommon Regions.                    |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: region
```

## Color Style

Below is a screenshot of the alternative Color (`color`) style which can be set via the `style` template variable.

![](../images/region2.png)

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
      - pmm: region
        template_variables:
          use_other: false
          use_separator: false
          style: color
          sep_style: purple
          exclude:
            - French
          sort_by: title.asc
```

## Default values

The following yaml is provided for reference to show what values will be in use if you do no customization.  If you want to customize these values, use the methods described above.  These do not show how to change a name or a list.

### Default `include`

```yaml
      
# List of countries other countries will be grouped into

    include:
     - Afghanistan
     - Antarctica
     - Argentina
     - Armenia
     - Australia
     - Bahamas
     - Belgium
     - Brazil
     - Canada
     - Chad
     - China
     - Costa Rica
     - Croatia
     - Denmark
     - France
     - Germany
     - Greece
     - Hong Kong
     - India
     - Ireland
     - Italy
     - Japan
     - Kenya
     - Korea
     - Mexico
     - Morocco
     - New Zealand
     - Nigeria
     - Peru
     - Poland
     - Russia
     - South Africa
     - Spain
     - Switzerland
     - Taiwan
     - Thailand
     - Turkey
     - United Kingdom
     - United States of America

# renaming of the above countries

    key_name_override:
      Afghanistan: Central Asian
      Antarctica: Antarctica Region
      Argentina: Southern Cone
      Armenia: Caucasian
      Australia: Australian
      Bahamas: Caribbean
      Belgium: Benelux
      Brazil: Brazilian
      Canada: Canadian
      Chad: Central African               # Based on UN geoscheme 
      China: Chinese and Mongolian
      Costa Rica: Central American
      Croatia: Balkan
      Denmark: Nordic
      France: French
      Japan: Japanese
      Germany: German
      Greece: Greek
      Hong Kong: Hong Kong and Macao
      India: South Asian
      Ireland: Irish
      Italy: Italian
      Kenya: Eastern African              # Based on UN geoscheme 
      Korea: Korean
      Mexico: Mexican
      Morocco: Northern African           # Based on UN geoscheme 
      New Zealand: Pacific Island
      Nigeria: Western African           # Based on UN geoscheme 
      Peru: Andean
      Poland: Eastern European             # Eastern European generally considerd to be ex-USSR countries of Russia, Belarus, and Ukraine. This grouping is more ex-iron curtain European countries excluding Russia and Balkans
      Russia: Russian
      South Africa: Southern African
      Spain: Iberian
      Switzerland: Central European
      Taiwan: Taiwanese
      Thailand: South-East Asia
      Turkey: Middle Eastern
      United Kingdom: UK
      United States of America: USA
      

    addons:

# Grouping of countries into sub-regions. Some license has been taken here to ensure all countries are included, and the groupings won't fit well with everyone's collections. 
# Western, Southern, and Central Europe, Oceania, and North America could be useful groupings for those libraries with more of an Asian focus, for instance
# Comments added where a decision point might seen as controversial

      Afghanistan:                     # Afghanistan rarely included as part of Central Asian, the 'stans', but often in South Asian
        - Kazakhstan
        - Kyrgyzstan
        - Tajikistan
        - Turkmenistan
        - Uzbekistan
      Argentina:
        - Chile
        - Paraguay                     # Not always included as part of Southern Cone
        - Uruguay
        - Falkland Islands             # Also in UK
      Armenia:
        - Azerbaijan
        - Georgia
      Bahamas:
        - Anguilla
        - Antigua
        - Aruba
        - Barbados
        - Bermuda
        - Bonaire
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
        - Montserrat
        - Puerto Rico
        - Saint Barthélemy
        - Saint Lucia
        - Trinidad and Tobago
        - Turks and Caicos
      Belgium:
        - Luxembourg
        - Netherlands
      Chad:
        - Angola
        - Cameroon
        - Central African Republic
        - Congo
        - Democratic Republic of the Congo    # Duplicating smart filter functionality
        - Equatorial Guinea
        - Gabon
        - Republic of the Congo
        - Sao Tome and Principe
      Costa Rica:
        - Belize
        - El Salvador
        - Guatemala
        - Honduras
        - Nicaragua
        - Panama
      Croatia:
        - Albania
        - Bosnia and Herzegovina
        - Bulgaria
        - Macedonia
        - Montenegro
        - Republic of North Macedonia         # Duplicating smart filter functionality
        - Romania
        - Serbia
        - Slovenia
      Denmark:
        - Åland Islands
        - Faroe Islands
        - Finland
        - Greenland
        - Iceland
        - Norway
        - Svalbard and Jan Mayen
        - Sweden
      India:
        - Pakistan
        - Bhutan
        - Bangladesh
        - Nepal
        - Sri Lanka
        - Maldives
      Kenya:
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
      Morocco:
        - Algeria
        - Egypt                 # Also in Middle Eastern
        - Libya       
        - Sudan
        - Tunisia
      New Zealand:
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
      Nigeria:
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
      Peru:
        - Bolivarian Republic of Venezuela    # Duplicating smart filter functionality
        - Bolivia
        - Colombia
        - Ecuador
        - Plurinational State of Bolivia      # Duplicating smart filter functionality
        - Venezuela
      Poland:
        - Belarus
        - Czech Republic
        - Estonia
        - Hungary
        - Latvia
        - Lithuania
        - Moldova
        - Slovakia
        - Ukraine
      South Africa:
        - Botswana
        - Eswatini
        - Lesotho
        - Namibia
      Spain:
        - Andorra              # Also in French
        - Gibraltar            # Also in UK
        - Portugal
      Switzerland:
        - Austria
        - Liechtenstein            
      Thailand:
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
      Turkey:
        - Bahrain
        - Cyprus
        - Egypt                 # Also in Northern African
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

# Grouping of micro-states into existing countries. Some are obviously right, others added as they've nowhere else fitting to go. 

      Antarctica:
        - Bouvet Island             # Also in Nordic
      Australia:
        - Christmas Island
        - Cocos (Keeling) Islands
        - New Guinea                # Also in Pacific Island
        - Timor-Leste               # Also in Pacific Island
      Brazil:
        - French Guiana
        - Guyana
        - Suriname           
      France:
        - Monaco
        - Andorra            # Also in Iberian
      Italy:
        - Holy See
        - Malta              # Also in UK and Northern African
        - San Marino
      Korea:
        - Democratic People's Republic of Korea
        - North Korea
        - Republic of Korea         # Added as default addon for Korea overridden
        - South Korea               # Added as default addon for Korea overridden

      United Kingdom:
        - Falkland Islands          # Also in Southern Cone
        - Guernsey
        - Gibraltar          # Also in Iberian
        - Isle of Man
        - Jersey
        - Malta              # Also in Italian and Northern African

# Duplicating smart filter functionality

      Taiwan:
        - Taiwan, Province of China
      Russia:
        - Russian Federation

```

