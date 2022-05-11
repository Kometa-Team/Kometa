# FlixPatrol Builders

You can find items using the features of [FlixPatrol.com](https://flixpatrol.com/) (FlixPatrol).

No configuration is required for this builder.

| Attribute                                             | Description                                                                                                                                                                                 | Works with Movies | Works with Shows | Works with Playlists and Custom Sort |
|:------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------:|:----------------:|:------------------------------------:|
| [`flixpatrol_top`](#flixpatrol-top-platform)          | Finds every item from [FlixPatrol's Top Platform Lists](https://flixpatrol.com/top10/) based on the attributes provided.                                                                    |      &#9989;      |     &#9989;      |               &#9989;                |
| [`flixpatrol_popular`](#flixpatrol-popular)           | Finds every movie/show from FlixPatrol's Popular [Movies](https://flixpatrol.com/popular/movies/)/[Shows](https://flixpatrol.com/popular/tv-shows/) Lists based on the attributes provided. |      &#9989;      |     &#9989;      |               &#9989;                |
| [`flixpatrol_demographics`](#flixpatrol-demographics) | Finds every item from [FlixPatrol's Demographics Lists](https://flixpatrol.com/demographics/) based on the attributes provided.                                                             |      &#9989;      |     &#9989;      |               &#9989;                |
| [`flixpatrol_url`](#flixpatrol-url)                   | Finds every item found at a FlixPatrol URL.                                                                                                                                                 |      &#9989;      |     &#9989;      |               &#9989;                |

## FlixPatrol Top Platform

Finds every item from [FlixPatrol's Top Platform Lists](https://flixpatrol.com/top10/) based on the attributes provided.

The only required attribute is `platform`.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

### Top Platform Attributes

| Attribute     | Description & Values                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:--------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `platform`    | **Description:** Streaming Platform to filter on.<br>**Values:** `netflix`, `hbo`, `disney`, `amazon`, `itunes`, `google`, `paramount_plus`, `hulu`, `vudu`, `imdb`, `amazon_prime`, `star_plus`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `location`    | **Description:** Location to filter on.<br>**Default:** `world`<br>**Values:** `world`, `albania`, `argentina`, `armenia`, `australia`, `austria`, `azerbaijan`, `bahamas`, `bahrain`, `bangladesh`, `belarus`, `belgium`, `belize`, `benin`, `bolivia`, `bosnia_and_herzegovina`, `botswana`, `brazil`, `bulgaria`, `burkina_faso`, `cambodia`, `canada`, `chile`, `colombia`, `costa_rica`, `croatia`, `cyprus`, `czech_republic`, `denmark`, `dominican_republic`, `ecuador`, `egypt`, `estonia`, `finland`, `france`, `gabon`, `germany`, `ghana`, `greece`, `guatemala`, `guinea_bissau`, `haiti`, `honduras`, `hong_kong`, `hungary`, `iceland`, `india`, `indonesia`, `ireland`, `israel`, `italy`, `ivory_coast`, `jamaica`, `japan`, `jordan`, `kazakhstan`, `kenya`, `kuwait`, `kyrgyzstan`, `laos`, `latvia`, `lebanon`, `lithuania`, `luxembourg`, `malaysia`, `maldives`, `mali`, `malta`, `mexico`, `moldova`, `mongolia`, `montenegro`, `morocco`, `mozambique`, `namibia`, `netherlands`, `new_zealand`, `nicaragua`, `niger`, `nigeria`, `north_macedonia`, `norway`, `oman`, `pakistan`, `panama`, `papua_new_guinea`, `paraguay`, `peru`, `philippines`, `poland`, `portugal`, `qatar`, `romania`, `russia`, `rwanda`, `salvador`, `saudi_arabia`, `senegal`, `serbia`, `singapore`, `slovakia`, `slovenia`, `south_africa`, `south_korea`, `spain`, `sri_lanka`, `sweden`, `switzerland`, `taiwan`, `tajikistan`, `tanzania`, `thailand`, `togo`, `trinidad_and_tobago`, `turkey`, `turkmenistan`, `uganda`, `ukraine`, `united_arab_emirates`, `united_kingdom`, `united_states`, `uruguay`, `uzbekistan`, `venezuela`, `vietnam`, `zambia`, `zimbabwe` |
| `time_window` | **Description:** Time window to filter on.<br>**Default:** `today`<br>**Values:** `today`, `yesterday`,`this_week`, `last_week`, `this_month`, `last_month`, `this_year`, `last_year`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `limit`       | **Description:** Number of items to return.<br>**Default:** `10`<br>**Values:** Integer greater than 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

```yaml
collections:
  US Netflix Monthly Top 20:
    flixpatrol_top:
      platform: netflix
      location: united_states
      time_window: this_month
      limit: 20
    collection_order: custom
    sync_mode: sync
```

## FlixPatrol Popular

Finds every movie/show from FlixPatrol's Popular [Movies](https://flixpatrol.com/popular/movies/)/[Shows](https://flixpatrol.com/popular/tv-shows/) Lists based on the attributes provided.

The only required attribute is `source`.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

### Popular Attributes

| Attribute     | Description                                                                                                                                                                                                              |
|:--------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `source`      | **Description:** Source to filter on.<br>**Values:** `movie_db`, `facebook`, `google`, `twitter`, `twitter_trends`, `instagram`, `instagram_trends`, `youtube`, `imdb`, `letterboxd`, `rotten_tomatoes`, `tmdb`, `trakt` |
| `time_window` | **Description:** Time window to filter on.<br>**Default:** `today`<br>**Values:** `today`, `yesterday`,`this_week`, `last_week`, `this_month`, `last_month`, `this_year`, `last_year`                                    |
| `limit`       | **Description:** Number of items to return.<br>**Default:** `10`<br>**Values:** Integer greater than 0                                                                                                                   |

```yaml
collections:
  Instagram Popular:
    flixpatrol_popular:
      source: instagram
      time_window: all
      limit: 20
    collection_order: custom
    sync_mode: sync
```

## FlixPatrol Demographics

Finds every item from [FlixPatrol's Demographics Lists](https://flixpatrol.com/demographics/) based on the attributes provided.

The only required attribute is `generation`.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

### Demographics Attribute

| Attribute    | Description                                                                                                                                                           |
|:-------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `generation` | Generation to filter on.<br>**Values:** `all`, `boomers`, `x`, `y`, `z`                                                                                               |
| `gender`     | Gender to filter on.<br>**Default:** `all`<br>**Values:** `all`, `men`, `women`                                                                                       |
| `location`   | Location to filter on.<br>**Default:** `world`<br>**Values:** `world`, `brazil`, `canada`, `france`, `germany`, `india`, `mexico`,  `united_kingdom`, `united_states` |
| `limit`      | Number of items to return.<br>**Default:** `10`<br>**Values:** Integer greater than 0                                                                                 |

```yaml
collections:
  Gen X Male US Demographic:
    flixpatrol_demographics:
      generation: x
      gender: men
      location: united_states 
      limit: 20
    collection_order: custom
    sync_mode: sync
```

## FlixPatrol URL

Finds every item found at a FlixPatrol URL.

The `sync_mode: sync` and `collection_order: custom` Details are recommended since the lists are continuously updated and in a specific order. 

```yaml
collections:
  US Netflix Monthly:
    flixpatrol_url: https://flixpatrol.com/top10/netflix/united-states/2021-11/full/
    collection_order: custom
    sync_mode: sync
  Instagram Monthly Popular:
    flixpatrol_url: https://flixpatrol.com/popular/movies/instagram/all-time/
    collection_order: custom
    sync_mode: sync
  Gen X Male US Demographic:
    flixpatrol_url: https://flixpatrol.com/demographics/generation-x/men/united-states/
    collection_order: custom
    sync_mode: sync
```
