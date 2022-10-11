# Subtitle Language Collections

The `subtitle_language` Default Metadata File is used to dynamically create collections based on the subtitle languages available in your library.

**This file works with Movie and TV Libraries.**

![](../images/subtitle_language.png)

## Collections Section 11

| Collection                                               |                    Key                    | Description                                                  |
|:---------------------------------------------------------|:-----------------------------------------:|:-------------------------------------------------------------|
| `Subtitle Language Collections`                          |                `separator`                | Separator Collection to denote the Section of Collections.   |
| `<<Subtitle Language>> Audio`<br>**Example:** `Japanese` | `<<ISO 639-1 Code>>`<br>**Example:** `ja` | Collection of Movies/Shows that have this Subtitle Language. |
| `Other Subtitles`                                        |                  `other`                  | Collection of Movies/Shows that are less common Languages.   |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: subtitle_language
  TV Shows:
    metadata_path:
      - pmm: subtitle_language
```

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

| Variable                          | Description & Values                                                                                                                                                                                                 |
|:----------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_separator`                   | **Description:** Turn the separator collection off.<br>**Values:** `false` to turn of the collection                                                                                                                 |
| `sep_style`                       | **Description:** Separator Style.<br>**Default:** `orig`<br>**Values:** `orig`, `red`, `blue`, `green`, `gray`, `purple`, or `stb`                                                                                   |         
| `limit`                           | **Description:** Changes the Builder Limit for all collections in a Defaults file.<br>**Values:** Number Greater then 0                                                                                              |
| `limit_<<key>>`                   | **Description:** Changes the Builder Limit of the specified key's collection.<br>**Default:** `limit`<br>**Values:** Number Greater then 0                                                                           |
| `sort_by`                         | **Description:** Changes the Smart Filter Sort for all collections in a Defaults file.<br>**Default:** `release.desc`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options) |
| `sort_by_<<key>>`                 | **Description:** Changes the Smart Filter Sort of the specified key's collection.<br>**Default:** `sort_by`<br>**Values:** [Any `smart_filter` Sort Option](../../metadata/builders/smart.md#sort-options)           |
| `include`                         | **Description:** Overrides the [default include list](#default-include)<br>**Values:** List of [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)                                              |
| `exclude`                         | **Description:** Exclude these Subtitle Languages from creating a Dynamic Collection.<br>**Values:** List of [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)                                |
| `append_include`                  | **Description:** Appends to the [default include list](#default-include)<br>**Values:** List of [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)                                             |
| `subtitle_language_name`          | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>> Subtitles`<br>**Values:** Any string with `<<key_name>>` in it.                                                  |
| `subtitle_language_other_name`    | **Description:** Changes the Other Collection name.<br>**Default:** `Other Subtitles`<br>**Values:** Any string.                                                                                                     |
| `subtitle_language_summary`       | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s with <<key_name>> Subtitles.`<br>**Values:** Any string.                                          |
| `subtitle_language_other_summary` | **Description:** Changes the Other Collection summary.<br>**Default:** `<<library_translationU>>s with other uncommon Subtitles.`<br>**Values:** Any string.                                                         |

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: subtitle_language
        template_variables:
          use_other: false
          use_separator: false
          sep_style: purple
          exclude:
            - fr  # Exclude French
          sort_by: title.asc
```

## Default `include`

```yaml
include:
  - ab     # Abkhazian
  - aa     # Afar
  - af     # Afrikaans
  - ak     # Akan
  - sq     # Albanian
  - am     # Amharic
  - ar     # Arabic
  - an     # Aragonese
  - hy     # Armenian
  - as     # Assamese
  - av     # Avaric
  - ae     # Avestan
  - ay     # Aymara
  - az     # Azerbaijani
  - bm     # Bambara
  - ba     # Bashkir
  - eu     # Basque
  - be     # Belarusian
  - bn     # Bengali
  - bi     # Bislama
  - bs     # Bosnian
  - br     # Breton
  - bg     # Bulgarian
  - my     # Burmese
  - ca     # Catalan, Valencian
  - km     # Central Khmer
  - ch     # Chamorro
  - ce     # Chechen
  - ny     # Chichewa, Chewa, Nyanja 
  - zh     # Chinese
  - cu     # Church Slavic, Old Slavonic, Church Slavonic, Old Bulgarian, Old Church Slavonic
  - cv     # Chuvash
  - kw     # Cornish
  - co     # Corsican
  - cr     # Cree
  - hr     # Croatian
  - cs     # Czech
  - da     # Danish
  - dv     # Divehi, Dhivehi, Maldivian
  - nl     # Dutch, Flemish
  - dz     # Dzongkha
  - en     # English
  - eo     # Esperanto
  - et     # Estonian
  - ee     # Ewe
  - fo     # Faroese
  - fj     # Fijian
  - fil    # Filipino
  - fi     # Finnish
  - fr     # French
  - ff     # Fulah
  - gd     # Gaelic, Scottish Gaelic
  - gl     # Galician
  - lg     # Ganda
  - ka     # Georgian
  - de     # German
  - el     # Greek, Modern (1453–)
  - gn     # Guarani
  - gu     # Gujarati
  - ht     # Haitian, Haitian Creole
  - ha     # Hausa
  - he     # Hebrew
  - hz     # Herero
  - hi     # Hindi
  - ho     # Hiri Motu
  - hu     # Hungarian
  - is     # Icelandic
  - io     # Ido
  - ig     # Igbo
  - id     # Indonesian
  - ia     # Interlingua (International Auxiliary Language Association)
  - ie     # Interlingue, Occidental
  - iu     # Inuktitut
  - ik     # Inupiaq
  - ga     # Irish
  - it     # Italian
  - ja     # Japanese
  - jv     # Javanese
  - kl     # Kalaallisut, Greenlandic
  - kn     # Kannada
  - kr     # Kanuri
  - ks     # Kashmiri
  - kk     # Kazakh
  - ki     # Kikuyu, Gikuyu
  - rw     # Kinyarwanda
  - ky     # Kirghiz, Kyrgyz
  - kv     # Komi
  - kg     # Kongo
  - ko     # Korean
  - kj     # Kuanyama, Kwanyama
  - ku     # Kurdish
  - lo     # Lao
  - la     # Latin
  - lv     # Latvian
  - li     # Limburgan, Limburger, Limburgish
  - ln     # Lingala
  - lt     # Lithuanian
  - lu     # Luba-Katanga
  - lb     # Luxembourgish, Letzeburgesch
  - mk     # Macedonian
  - mg     # Malagasy
  - ms     # Malay
  - ml     # Malayalam
  - mt     # Maltese
  - gv     # Manx
  - mi     # Maori
  - mr     # Marathi
  - mh     # Marshallese
  - mn     # Mongolian
  - na     # Nauru
  - nv     # Navajo, Navaho
  - ng     # Ndonga
  - ne     # Nepali
  - nd     # North Ndebele
  - se     # Northern Sami
  - no     # Norwegian
  - nb     # Norwegian Bokmål
  - nn     # Norwegian Nynorsk
  - oc     # Occitan
  - oj     # Ojibwa
  - or     # Oriya
  - om     # Oromo
  - os     # Ossetian, Ossetic
  - pi     # Pali
  - ps     # Pashto, Pushto
  - fa     # Persian
  - pl     # Polish
  - pt     # Portuguese
  - pa     # Punjabi, Panjabi
  - qu     # Quechua
  - ro     # Romanian, Moldavian, Moldovan
  - rm     # Romansh
  - rn     # Rundi
  - ru     # Russian
  - sm     # Samoan
  - sg     # Sango
  - sa     # Sanskrit
  - sc     # Sardinian
  - sr     # Serbian
  - sn     # Shona
  - ii     # Sichuan Yi, Nuosu
  - sd     # Sindhi
  - si     # Sinhala, Sinhalese
  - sk     # Slovak
  - sl     # Slovenian
  - so     # Somali
  - nr     # South Ndebele
  - st     # Southern Sotho
  - es     # Spanish, Castilian
  - su     # Sundanese
  - sw     # Swahili
  - ss     # Swati
  - sv     # Swedish
  - tl     # Tagalog
  - ty     # Tahitian
  - tg     # Tajik
  - ta     # Tamil
  - tt     # Tatar
  - te     # Telugu
  - th     # Thai
  - bo     # Tibetan
  - ti     # Tigrinya
  - to     # Tonga (Tonga Islands)
  - ts     # Tsonga
  - tn     # Tswana
  - tr     # Turkish
  - tk     # Turkmen
  - tw     # Twi
  - ug     # Uighur, Uyghur
  - uk     # Ukrainian
  - ur     # Urdu
  - uz     # Uzbek
  - ve     # Venda
  - vi     # Vietnamese
  - vo     # Volapük
  - wa     # Walloon
  - cy     # Welsh
  - fy     # Western Frisian
  - wo     # Wolof
  - xh     # Xhosa
  - yi     # Yiddish
  - yo     # Yoruba
  - za     # Zhuang, Chuang
  - zu     # Zulu
```