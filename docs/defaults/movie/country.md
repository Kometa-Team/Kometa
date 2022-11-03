# Country Collections

The `country` Default Metadata File is used to dynamically create collections based on the countries available in your library.

**This file works with Movie Libraries, but has a Show Library [Counterpart](../show/country).**

![](../images/country1.png)

## Collections Section 09

| Collection                              |                   Key                   | Description                                                                 |
|:----------------------------------------|:---------------------------------------:|:----------------------------------------------------------------------------|
| `Country Collections`                   |               `separator`               | [Separator Collection](../separators) to denote the Section of Collections. |
| `<<Country>>`<br>**Example:** `Germany` | `<<Country>>`<br>**Example:** `Germany` | Collection of Movies that have this Country.                                |
| `Other Countries`                       |                 `other`                 | Collection of Movies that are in other uncommon Countries.                  |

## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: country
```

## Color Style

Below is a screenshot of the alternative Color (`color`) style which can be set via the `style` template variable.

![](../images/country2.png)

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `templates_variables:` section only needs to be used if you do want to actually change how the defaults work. Any value not specified is its default value if it has one if not it's just ignored.

All [Shared Collection Variables](../variables) are available as well as the additional Variables below which can be used to customize the file.

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
| `country_name`                | **Description:** Changes the title format of the Dynamic Collections.<br>**Default:** `<<key_name>>`<br>**Values:** Any string with `<<key_name>>` in it.                                                                                                         |
| `country_other_name`          | **Description:** Changes the Other Collection name.<br>**Default:** `Other Countries`<br>**Values:** Any string.                                                                                                                                                  |
| `country_summary`             | **Description:** Changes the summary format of the Dynamic Collections.<br>**Default:** `<<library_translationU>>s filmed in <<key_name>>.`<br>**Values:** Any string.                                                                                            |
| `country_other_summary`       | **Description:** Changes the Other Collection summary.<br>**Default:** `<<library_translationU>>s filmed in other uncommon Countries.`<br>**Values:** Any string.                                                                                                 |

1. Each default collection has a `key` that when calling to effect a specific collection you must replace `<<key>>` with when calling.

The below is an example config.yml extract with some Template Variables added in to change how the file works.

```yaml
libraries:
  Movies:
    metadata_path:
      - pmm: country
        template_variables:
          use_other: false
          use_separator: false
          sep_style: purple
          exclude:
            - France
          sort_by: title.asc
```

## Default `include`

```yaml
include:
  # - Afghanistan                   # af
  # - Åland Islands                 # ax
  # - Albania                       # al
  # - Algeria                       # dz
  # - Andorra                       # ad
  # - Angola                        # ao
  # - Anguilla                      # ai
  # - Antarctica                    # aq
  # - Antigua                       # ag
  - Argentina                     # ar
  # - Armenia                       # am
  # - Aruba                         # aw
  - Australia                     # au
  - Austria                       # at
  # - Azerbaijan                    # az
  - Bahamas                       # bs
  # - Bahrain                       # bh
  # - Bangladesh                    # bd
  # - Barbados                      # bb
  # - Belarus                       # by
  - Belgium                       # be
  # - Belize                        # bz
  # - Benin                         # bj
  # - Bermuda                       # bm
  # - Bhutan                        # bt
  # - Bolivia                       # bo
  # - Bonaire                       # bq
  # - Bosnia and Herzegovina        # ba
  # - Botswana                      # bw
  # - Bouvet Island                 # bv
  - Brazil                        # br
  # - Brunei                        # bn
  - Bulgaria                      # bg
  # - Burkina Faso                  # bf
  # - Burundi                       # bi
  # - Cabo Verde                    # cv
  # - Cambodia                      # kh
  # - Cameroon                      # cm
  - Canada                        # ca
  # - Cayman Islands                # ky
  # - Central African Republic      # cf
  # - Chad                          # td
  - Chile                         # cl
  - China                         # cn
  # - Christmas Island              # cx
  # - Cocos (Keeling) Islands       # cc
  # - Colombia                      # co
  # - Comoros                       # km
  # - Congo                         # cg
  # - Cook Islands                  # ck
  - Costa Rica                    # cr
  # - Côte d'Ivoire                 # ci
  - Croatia                       # hr
  # - Cuba                          # cu
  # - Curaçao                       # cw
  # - Cyprus                        # cy
  - Czech Republic                # cz
  - Denmark                       # dk
  # - Djibouti                      # dj
  # - Dominica                      # dm
  - Dominican Republic            # do
  # - Ecuador                       # ec
  - Egypt                         # eg
  # - El Salvador                   # sv
  # - Equatorial Guinea             # gq
  # - Eritrea                       # er
  - Estonia                       # ee
  # - Eswatini                      # sz
  # - Ethiopia                      # et
  # - Falkland Islands              # fk
  # - Faroe Islands                 # fo
  # - Fiji                          # fj
  - Finland                       # fi
  - France                        # fr
  # - French Guiana                 # gf
  # - French Polynesia              # pf
  # - Gabon                         # ga
  # - Gambia                        # gm
  # - Georgia                       # ge
  - Germany                       # de
  # - Ghana                         # gh
  # - Gibraltar                     # gi
  - Greece                        # gr
  # - Greenland                     # gl
  # - Grenada                       # gd
  # - Guadeloupe                    # gp
  # - Guam                          # gu
  # - Guatemala                     # gt
  # - Guernsey                      # gg
  # - Guinea                        # gn
  # - Guinea-Bissau                 # gw
  # - Guyana                        # gy
  # - Haiti                         # ht
  # - Holy See                      # va
  # - Honduras                      # hn
  - Hong Kong                     # hk
  - Hungary                       # hu
  - Iceland                       # is
  - India                         # in
  - Indonesia                     # id
  - Iran                          # ir
  # - Iraq                          # iq
  - Ireland                       # ie
  # - Isle of Man                   # im
  - Israel                        # il
  - Italy                         # it
  # - Jamaica                       # jm
  - Japan                         # jp
  # - Jersey                        # je
  # - Jordan                        # jo
  # - Kazakhstan                    # kz
  # - Kenya                         # ke
  # - Kiribati                      # ki
  - Korea                         # kr
  # - Kuwait                        # kw
  # - Kyrgyzstan                    # kg
  # - Lao                           # la
  - Latvia                        # lv
  # - Lebanon                       # lb
  # - Lesotho                       # ls
  # - Liberia                       # lr
  # - Libya                         # ly
  # - Liechtenstein                 # li
  # - Lithuania                     # lt
  - Luxembourg                    # lu
  # - Macao                         # mo
  # - Madagascar                    # mg
  # - Malawi                        # mw
  - Malaysia                      # my
  # - Maldives                      # mv
  # - Mali                          # ml
  # - Malta                         # mt
  # - Marshall Islands              # mh
  # - Martinique                    # mq
  # - Mauritania                    # mr
  # - Mauritius                     # mu
  # - Mayotte                       # yt
  - Mexico                        # mx
  # - Micronesia                    # fm
  # - Moldova                       # md
  # - Monaco                        # mc
  # - Mongolia                      # mn
  # - Montenegro                    # me
  # - Montserrat                    # ms
  - Morocco                       # ma
  # - Mozambique                    # mz
  # - Myanmar                       # mm
  # - Namibia                       # na
  # - Nauru                         # nr
  # - Nepal                         # np
  - Netherlands                   # nl
  # - New Caledonia                 # nc
  - New Zealand                   # nz
  # - Nicaragua                     # ni
  # - Niger                         # ne
  # - Nigeria                       # ng
  # - Niue                          # nu
  # - Norfolk Island                # nf
  # - Macedonia                     # mk
  - Norway                        # no
  # - Oman                          # om
  - Pakistan                      # pk
  # - Palau                         # pw
  # - Palestine                     # ps
  - Panama                        # pa
  # - New Guinea                    # pg
  # - Paraguay                      # py
  - Peru                          # pe
  - Philippines                   # ph
  # - Pitcairn                      # pn
  - Poland                        # pl
  - Portugal                      # pt
  # - Puerto Rico                   # pr
  - Qatar                         # qa
  # - Réunion                       # re
  - Romania                       # ro
  - Russia                        # ru
  # - Rwanda                        # rw
  # - Saint Barthélemy              # bl
  # - Saint Lucia                   # lc
  # - Samoa                         # ws
  # - San Marino                    # sm
  # - Sao Tome and Principe         # st
  - Saudi Arabia                  # sa
  # - Senegal                       # sn
  - Serbia                        # rs
  # - Seychelles                    # sc
  # - Sierra Leone                  # sl
  - Singapore                     # sg
  # - Slovakia                      # sk
  # - Slovenia                      # si
  # - Solomon Islands               # sb
  # - Somalia                       # so
  - South Africa                  # za
  # - South Sudan                   # ss
  - Spain                         # es
  - Sri Lanka                     # lk
  # - Sudan                         # sd
  # - Suriname                      # sr
  - Sweden                        # se
  - Switzerland                   # ch
  # - Syria                         # sy
  # - Taiwan                        # tw
  # - Tajikistan                    # tj
  # - Tanzania                      # tz
  - Thailand                      # th
  # - Timor-Leste                   # tl
  # - Togo                          # tg
  # - Tokelau                       # tk
  # - Tonga                         # to
  # - Trinidad and Tobago           # tt
  # - Tunisia                       # tn
  - Turkey                        # tr
  # - Turkmenistan                  # tm
  # - Turks and Caicos              # tc
  # - Tuvalu                        # tv
  # - Uganda                        # ug
  - Ukraine                       # ua
  - United Arab Emirates          # ae
  - United Kingdom                # gb
  - United States of America      # us
  # - Uruguay                       # uy
  # - Uzbekistan                    # uz
  # - Vanuatu                       # vu
  # - Venezuela                     # ve
  - Vietnam                       # vn
  # - Yemen                         # ye
  # - Zambia                        # zm
  # - Zimbabwe                      # zw
```

## Default `addons`

```yaml
addons:
  Korea:
    - Republic of Korea
    - South Korea
```
