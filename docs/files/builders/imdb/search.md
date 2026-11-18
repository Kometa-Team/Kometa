# IMDb Advanced Search

Find movies, shows, or episodes with `imdb_search`, using [IMDb Advanced Title Search](https://www.imdb.com/search/title/). For IDs, charts, lists, watchlists, or awards, see [IMDb builders](builders.md).

## Quick start

```yaml
collections:
  IMDb Popular Movies:
    collection_order: custom
    sync_mode: sync
    imdb_search:
      type: movie
      sort_by: popularity.asc
      limit: 50
```

Use `collection_order: custom` to preserve search order and `sync_mode: sync`
to keep collection membership synchronized as results change. Check your chosen
filters on [IMDb Search](https://www.imdb.com/search/) when setting up a query.

## Value types

- **String:** text, an IMDb ID, or a code. Quote comma-separated values, such as `"action,comedy"`.
- **Integer:** a whole number; most numeric filters require a value greater than zero. `limit` also accepts `0` for all results.
- **Number:** a decimal or whole number; rating filters accept `0.1` through `10.0`.
- **Boolean:** unquoted `true` or `false`.
- **Date:** `YYYY-MM-DD`, such as `2020-01-01`, or `today`.
- **Dictionary:** named fields, as used by `content_rating` for `rating` and `region`.

### Ranges and multiple values

`.gte` sets an inclusive minimum; `.lte` sets an inclusive maximum. Use either
on its own or both for a range. Release dates use `.after` and `.before` instead.

Where a table row lists a base attribute alongside `.any` and `.not`, use:

| Form | Match | Example |
|:-----|:------|:--------|
| Base attribute | All values (AND) | `genre: "action,comedy"` |
| `.any` | At least one value (OR) | `genre.any: "action,comedy"` |
| `.not` | None of the values | `genre.not: horror` |

Supply multiple values as a comma-separated string. IMDb uses these attribute
variants for AND/OR logic, rather than TMDb's pipe separator. Some attributes
match **any** value even without `.any`; their table descriptions state this.
Separate filters in the same query must all be satisfied.

## Search attributes

All attributes below belong under `imdb_search:`. Grouped rows list each supported
variant explicitly; they share the same allowed values.

### Results and titles

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `limit` | Integer | Maximum results; default `100`. Use `0` for all. |
| `sort_by` | Sort option | Default `popularity.asc`; see [sort options](#sort-options). |
| `title` | String | Title name. |
| `type`, `type.not` | Title types | Include any listed type, or exclude all listed types with `.not`. See [allowed values](#allowed-values). |
| `adult` | Boolean | Include adult titles in results. |

### Dates, ratings, and runtime

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `release.after`, `release.before` | Date | Released after / before the given date. |
| `rating.gte`, `rating.lte` | Number, 0.1-10.0 | Minimum / maximum IMDb rating. |
| `votes.gte`, `votes.lte` | Positive integer | Minimum / maximum vote count. |
| `runtime.gte`, `runtime.lte` | Positive integer | Minimum / maximum runtime. |
| `popularity.gte`, `popularity.lte` | Positive integer | Minimum / maximum popularity value. |
| `imdb_top`, `imdb_bottom` | Positive integer | Titles in the given top / bottom number of movies. |

### Genres, interests, and keywords

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `genre`, `genre.any`, `genre.not` | Genre names | All / any / none of the genres in [allowed values](#allowed-values). |
| `interests`, `interests.any`, `interests.not` | Interest values | All / any / none; see the [interests reference](#interests-reference). |
| `keyword`, `keyword.any`, `keyword.not` | Keywords | All / any / none of the valid [IMDb keywords](https://www.imdb.com/search/keyword/). |

### People, series, and lists

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `cast`, `cast.any`, `cast.not` | Person IDs | All / any / none of the cast members, such as `nm0000138`. |
| `character` | Strings | Any character name listed in the credits. |
| `series`, `series.not` | Title IDs | Any listed series, or exclude listed series with `.not`; for example `tt0096697`. |
| `list`, `list.any`, `list.not` | List IDs | All / any / none of the lists, such as `ls000024621`. |
| `company` | Company names or IDs | Any company; see [allowed values](#allowed-values). |

### Countries, languages, and certification

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `country`, `country.any`, `country.not` | Country codes | All / any / none of the two-letter ISO 3166 country codes. |
| `country.origin` | Country codes | Any listed country as the country of origin. |
| `language`, `language.any`, `language.not` | Language codes | Base and `.any` match any listed ISO 639-2 language code; `.not` excludes them. |
| `language.primary` | Language codes | Any listed ISO 639-2 code as the primary language. |
| `content_rating` | Dictionary or list of dictionaries | Use `rating` for the certification and `region` for its two-letter ISO 3166 country code; see [examples](#example-imdb-search-builders). |

### Awards and page content

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `event`, `event.winning` | Events | Nomination / win at a listed event; see [allowed values](#allowed-values). |
| `topic`, `topic.not` | Topic names | Has any listed topic, or excludes those topics; see [allowed values](#allowed-values). |
| `alternate_version`, `alternate_version.any`, `alternate_version.not` | Strings | All / any / none of the strings in alternate versions. |
| `crazy_credit`, `crazy_credit.any`, `crazy_credit.not` | Strings | All / any / none of the strings in crazy credits. |
| `location`, `location.any`, `location.not` | Strings | All / any / none of the strings in locations. |
| `goof`, `goof.any`, `goof.not` | Strings | All / any / none of the strings in goofs. |
| `plot`, `plot.any`, `plot.not` | Strings | All / any / none of the strings in plot text. |
| `quote`, `quote.any`, `quote.not` | Strings | All / any / none of the strings in quotes. |
| `soundtrack`, `soundtrack.any`, `soundtrack.not` | Strings | All / any / none of the strings in soundtrack information. |
| `trivia`, `trivia.any`, `trivia.not` | Strings | All / any / none of the strings in trivia. |

## Sort options

Append `.asc` for ascending or `.desc` for descending order, such as `rating.desc`.
The default is `popularity.asc`.

| Field | Orders by |
|:------|:----------|
| `popularity` | Popularity |
| `title` | Title |
| `rating` | IMDb rating |
| `votes` | Vote count |
| `box_office` | Box office |
| `runtime` | Runtime |
| `year` | Year |
| `release` | Release date |

## Allowed values

### Title types

`movie`, `tv_series`, `short`, `tv_episode`, `tv_mini_series`, `tv_movie`, `tv_special`, `tv_short`, `video_game`, `video`, `music_video`, `podcast_series`, `podcast_episode`

### Genres

`action`, `adventure`, `animation`, `biography`, `comedy`, `documentary`, `drama`, `crime`, `family`, `history`, `news`, `short`, `western`, `sport`, `reality-tv`, `horror`, `fantasy`, `film-noir`, `music`, `romance`, `talk-show`, `thriller`, `war`, `sci-fi`, `musical`, `mystery`, `game-show`

### Events

`cannes`, `choice`, `spirit`, `sundance`, `bafta`, `oscar`, `emmy`, `golden`, `oscar_picture`, `oscar_director`, `national_film_board_preserved`, `razzie`, or any [IMDb Event ID](https://www.imdb.com/event/all/) (ex. `ev0050888`)

### Companies

`fox`, `dreamworks`, `mgm`, `paramount`, `sony`, `universal`, `disney`, `warner`, or any IMDb Company ID (ex. `co0023400`)

### Page topics

`alternate_version`, `award`, `business_info`, `crazy_credit`, `goof`, `location`, `plot`, `quote`, `soundtrack`, `technical`, `trivia`

### Interests reference

??? info "Full interests reference"

    You can use the Key or the ID for interests. This list is a snapshot; IMDb's interest catalog
    changes over time, and Kometa refreshes it automatically from
    [`INTERESTS.json`](https://raw.githubusercontent.com/Kometa-Team/IMDb-Interests/main/INTERESTS.json)
    at runtime (falling back to a bundled copy). That file is the authoritative, always-current list.

    | Name                             | Key                                | ID          |
    |:---------------------------------|:-----------------------------------|-------------|
    | 90 Day Fiancé                    | `90_day_fiancé`                    | `in0000262` |
    | Action                           | `action`                           | `in0000001` |
    | Action Epic                      | `action_epic`                      | `in0000002` |
    | Adult Animation                  | `adult_animation`                  | `in0000025` |
    | Adventure                        | `adventure`                        | `in0000012` |
    | Adventure Epic                   | `adventure_epic`                   | `in0000015` |
    | Alien                            | `alien`                            | `in0000265` |
    | Alien Invasion                   | `alien_invasion`                   | `in0000157` |
    | Animal Adventure                 | `animal_adventure`                 | `in0000092` |
    | Animation                        | `animation`                        | `in0000026` |
    | Anime                            | `anime`                            | `in0000027` |
    | Arabic                           | `arabic`                           | `in0000213` |
    | Artificial Intelligence          | `artificial_intelligence`          | `in0000158` |
    | Avatar: The Last Airbender       | `avatar:_the_last_airbender`       | `in0000312` |
    | B-Action                         | `b_action`                         | `in0000003` |
    | B-Horror                         | `b_horror`                         | `in0000108` |
    | Baseball                         | `baseball`                         | `in0000167` |
    | Basketball                       | `basketball`                       | `in0000168` |
    | Battlestar Galactica             | `battlestar_galactica`             | `in0000278` |
    | Beauty Competition               | `beauty_competition`               | `in0000102` |
    | Beauty Makeover                  | `beauty_makeover`                  | `in0000123` |
    | Bengali                          | `bengali`                          | `in0000214` |
    | Big Brother                      | `big_brother`                      | `in0000263` |
    | Biography                        | `biography`                        | `in0000072` |
    | Blade Runner                     | `blade_runner`                     | `in0000296` |
    | Body Horror                      | `body_horror`                      | `in0000109` |
    | Body Swap Comedy                 | `body_swap_comedy`                 | `in0000031` |
    | Boxing                           | `boxing`                           | `in0000169` |
    | Breaking Bad                     | `breaking_bad`                     | `in0000274` |
    | Buddy Comedy                     | `buddy_comedy`                     | `in0000032` |
    | Buddy Cop                        | `buddy_cop`                        | `in0000033` |
    | Buffyverse                       | `buffyverse`                       | `in0000311` |
    | Bumbling Detective               | `bumbling_detective`               | `in0000136` |
    | Business Reality TV              | `business_reality_tv`              | `in0000142` |
    | Cantonese                        | `cantonese`                        | `in0000215` |
    | Caper                            | `caper`                            | `in0000050` |
    | Car Action                       | `car_action`                       | `in0000004` |
    | Classic Musical                  | `classic_musical`                  | `in0000131` |
    | Classical Western                | `classical_western`                | `in0000187` |
    | Comedy                           | `comedy`                           | `in0000034` |
    | Coming-of-Age                    | `coming_of_age`                    | `in0000073` |
    | Computer Animation               | `computer_animation`               | `in0000028` |
    | Concert                          | `concert`                          | `in0000129` |
    | Conspiracy Thriller              | `conspiracy_thriller`              | `in0000176` |
    | Contemporary Western             | `contemporary_western`             | `in0000188` |
    | Cooking & Food                   | `cooking_&_food`                   | `in0000124` |
    | Cooking Competition              | `cooking_competition`              | `in0000103` |
    | Cop Drama                        | `cop_drama`                        | `in0000051` |
    | Costume Drama                    | `costume_drama`                    | `in0000074` |
    | Cozy Mystery                     | `cozy_mystery`                     | `in0000137` |
    | Crime                            | `crime`                            | `in0000052` |
    | Crime Documentary                | `crime_documentary`                | `in0000059` |
    | Crime Reality TV                 | `crime_reality_tv`                 | `in0000143` |
    | Cyber Thriller                   | `cyber_thriller`                   | `in0000177` |
    | Cyberpunk                        | `cyberpunk`                        | `in0000159` |
    | Danish                           | `danish`                           | `in0000242` |
    | Dark Comedy                      | `dark_comedy`                      | `in0000035` |
    | Dark Fantasy                     | `dark_fantasy`                     | `in0000095` |
    | Dark Romance                     | `dark_romance`                     | `in0000149` |
    | Dating Reality TV                | `dating_reality_tv`                | `in0000144` |
    | DC                               | `dc`                               | `in0000244` |
    | Degrassi                         | `degrassi`                         | `in0000264` |
    | Desert Adventure                 | `desert_adventure`                 | `in0000013` |
    | Despicable Me                    | `despicable_me`                    | `in0000267` |
    | Dinosaur Adventure               | `dinosaur_adventure`               | `in0000014` |
    | Disaster                         | `disaster`                         | `in0000005` |
    | Doctor Who                       | `doctor_who`                       | `in0000270` |
    | Docudrama                        | `docudrama`                        | `in0000075` |
    | Documentary                      | `documentary`                      | `in0000060` |
    | Docuseries                       | `docuseries`                       | `in0000061` |
    | Docusoap Reality TV              | `docusoap_reality_tv`              | `in0000145` |
    | Dragon Ball                      | `dragon_ball`                      | `in0000250` |
    | Drama                            | `drama`                            | `in0000076` |
    | Drug Crime                       | `drug_crime`                       | `in0000053` |
    | Dune                             | `dune`                             | `in0000297` |
    | Dutch                            | `dutch`                            | `in0000216` |
    | Dystopian Sci-Fi                 | `dystopian_sci_fi`                 | `in0000160` |
    | Epic                             | `epic`                             | `in0000077` |
    | Erotic Thriller                  | `erotic_thriller`                  | `in0000178` |
    | Evangelion                       | `evangelion`                       | `in0000255` |
    | Evil Dead                        | `evil_dead`                        | `in0000290` |
    | Extreme Sport                    | `extreme_sport`                    | `in0000170` |
    | Fairy Tale                       | `fairy_tale`                       | `in0000097` |
    | Faith & Spirituality Documentary | `faith_&_spirituality_documentary` | `in0000062` |
    | Family                           | `family`                           | `in0000093` |
    | Fantasy                          | `fantasy`                          | `in0000098` |
    | Fantasy Epic                     | `fantasy_epic`                     | `in0000096` |
    | Farce                            | `farce`                            | `in0000036` |
    | Fast & Furious                   | `fast_&_furious`                   | `in0000273` |
    | Feel-Good Romance                | `feel_good_romance`                | `in0000151` |
    | Filipino                         | `filipino`                         | `in0000217` |
    | Film Noir                        | `film_noir`                        | `in0000054` |
    | Financial Drama                  | `financial_drama`                  | `in0000078` |
    | Finnish                          | `finnish`                          | `in0000218` |
    | Folk Horror                      | `folk_horror`                      | `in0000110` |
    | Food Documentary                 | `food_documentary`                 | `in0000063` |
    | Football                         | `football`                         | `in0000171` |
    | Found Footage Horror             | `found_footage_horror`             | `in0000111` |
    | French                           | `french`                           | `in0000219` |
    | Frozen                           | `frozen`                           | `in0000293` |
    | Game Show                        | `game_show`                        | `in0000105` |
    | Gangster                         | `gangster`                         | `in0000055` |
    | German                           | `german`                           | `in0000220` |
    | Giallo                           | `giallo`                           | `in0000179` |
    | Globetrotting Adventure          | `globetrotting_adventure`          | `in0000016` |
    | Godzilla                         | `godzilla`                         | `in0000285` |
    | Golmaal                          | `golmaal`                          | `in0000306` |
    | Greek                            | `greek`                            | `in0000221` |
    | Gun Fu                           | `gun_fu`                           | `in0000197` |
    | Gundam                           | `gundam`                           | `in0000256` |
    | Hand-Drawn Animation             | `hand_drawn_animation`             | `in0000029` |
    | Hard-boiled Detective            | `hard_boiled_detective`            | `in0000138` |
    | Harry Potter                     | `harry_potter`                     | `in0000281` |
    | Heist                            | `heist`                            | `in0000056` |
    | Hidden Camera                    | `hidden_camera`                    | `in0000146` |
    | High-Concept Comedy              | `high_concept_comedy`              | `in0000037` |
    | Hindi                            | `hindi`                            | `in0000222` |
    | Historical Epic                  | `historical_epic`                  | `in0000079` |
    | History                          | `history`                          | `in0000080` |
    | History Documentary              | `history_documentary`              | `in0000064` |
    | Holiday                          | `holiday`                          | `in0000192` |
    | Holiday Animation                | `holiday_animation`                | `in0000193` |
    | Holiday Comedy                   | `holiday_comedy`                   | `in0000194` |
    | Holiday Family                   | `holiday_family`                   | `in0000195` |
    | Holiday Romance                  | `holiday_romance`                  | `in0000196` |
    | Home Improvement                 | `home_improvement`                 | `in0000125` |
    | Horror                           | `horror`                           | `in0000112` |
    | Housefull                        | `housefull`                        | `in0000308` |
    | Indiana Jones                    | `indiana_jones`                    | `in0000298` |
    | Isekai                           | `isekai`                           | `in0000201` |
    | Italian                          | `italian`                          | `in0000223` |
    | Iyashikei                        | `iyashikei`                        | `in0000202` |
    | James Bond                       | `james_bond`                       | `in0000266` |
    | Japanese                         | `japanese`                         | `in0000224` |
    | Jason Statham Action             | `jason_statham_action`             | `in0000315` |
    | John Wick                        | `john_wick`                        | `in0000291` |
    | Josei                            | `josei`                            | `in0000203` |
    | Jukebox Musical                  | `jukebox_musical`                  | `in0000132` |
    | Jungle Adventure                 | `jungle_adventure`                 | `in0000017` |
    | Jurassic Park                    | `jurassic_park`                    | `in0000283` |
    | Kaiju                            | `kaiju`                            | `in0000161` |
    | Kamen Rider                      | `kamen_rider`                      | `in0000257` |
    | Kannada                          | `kannada`                          | `in0000241` |
    | Korean                           | `korean`                           | `in0000225` |
    | Korean Drama                     | `korean_drama`                     | `in0000209` |
    | Kung Fu                          | `kung_fu`                          | `in0000198` |
    | Kung Fu Panda                    | `kung_fu_panda`                    | `in0000294` |
    | Legal Drama                      | `legal_drama`                      | `in0000081` |
    | Legal Thriller                   | `legal_thriller`                   | `in0000180` |
    | Lego                             | `lego`                             | `in0000249` |
    | Lifestyle                        | `lifestyle`                        | `in0000126` |
    | Love Is Blind                    | `love_is_blind`                    | `in0000261` |
    | Love Island                      | `love_island`                      | `in0000254` |
    | Maddock Horror Comedy Universe   | `maddock_horror_comedy_universe`   | `in0000305` |
    | Malayalam                        | `malayalam`                        | `in0000240` |
    | Mandarin                         | `mandarin`                         | `in0000226` |
    | Marathi                          | `marathi`                          | `in0000227` |
    | Martial Arts                     | `martial_arts`                     | `in0000006` |
    | Marvel                           | `marvel`                           | `in0000248` |
    | Masters of the Universe          | `masters_of_the_universe`          | `in0000280` |
    | Mecha                            | `mecha`                            | `in0000204` |
    | Medical Drama                    | `medical_drama`                    | `in0000082` |
    | Micro-Drama                      | `micro_drama`                      | `in0000310` |
    | Military Documentary             | `military_documentary`             | `in0000065` |
    | Mission: Impossible              | `mission:_impossible`              | `in0000284` |
    | Mockumentary                     | `mockumentary`                     | `in0000038` |
    | Monster Horror                   | `monster_horror`                   | `in0000113` |
    | Motorsport                       | `motorsport`                       | `in0000172` |
    | Mountain Adventure               | `mountain_adventure`               | `in0000018` |
    | Music                            | `music`                            | `in0000130` |
    | Music Documentary                | `music_documentary`                | `in0000066` |
    | Musical                          | `musical`                          | `in0000133` |
    | Mystery                          | `mystery`                          | `in0000139` |
    | Naruto                           | `naruto`                           | `in0000258` |
    | Nature Documentary               | `nature_documentary`               | `in0000067` |
    | News                             | `news`                             | `in0000211` |
    | Norwegian                        | `norwegian`                        | `in0000228` |
    | One Piece                        | `one_piece`                        | `in0000251` |
    | One-Person Army Action           | `one_person_army_action`           | `in0000007` |
    | Paranormal Reality TV            | `paranormal_reality_tv`            | `in0000147` |
    | Parody                           | `parody`                           | `in0000039` |
    | Period Drama                     | `period_drama`                     | `in0000083` |
    | Persian                          | `persian`                          | `in0000229` |
    | Pitch Perfect                    | `pitch_perfect`                    | `in0000302` |
    | Planet of the Apes               | `planet_of_the_apes`               | `in0000275` |
    | Pokémon                          | `pokémon`                          | `in0000252` |
    | Police Procedural                | `police_procedural`                | `in0000057` |
    | Political Documentary            | `political_documentary`            | `in0000068` |
    | Political Drama                  | `political_drama`                  | `in0000084` |
    | Political Thriller               | `political_thriller`               | `in0000181` |
    | Pop Musical                      | `pop_musical`                      | `in0000134` |
    | Portuguese                       | `portuguese`                       | `in0000230` |
    | Power Rangers                    | `power_rangers`                    | `in0000246` |
    | Predator                         | `predator`                         | `in0000276` |
    | Prison Drama                     | `prison_drama`                     | `in0000085` |
    | Psychological Drama              | `psychological_drama`              | `in0000086` |
    | Psychological Horror             | `psychological_horror`             | `in0000114` |
    | Psychological Thriller           | `psychological_thriller`           | `in0000182` |
    | Punjabi                          | `punjabi`                          | `in0000231` |
    | Quest                            | `quest`                            | `in0000019` |
    | Quirky Comedy                    | `quirky_comedy`                    | `in0000040` |
    | Quiz Show                        | `quiz_show`                        | `in0000104` |
    | Raunchy Comedy                   | `raunchy_comedy`                   | `in0000041` |
    | Reality TV                       | `reality_tv`                       | `in0000148` |
    | Resident Evil                    | `resident_evil`                    | `in0000314` |
    | Road Trip                        | `road_trip`                        | `in0000020` |
    | Rock Musical                     | `rock_musical`                     | `in0000135` |
    | Rohit Shetty Cop Universe        | `rohit_shetty_cop_universe`        | `in0000307` |
    | Romance                          | `romance`                          | `in0000152` |
    | Romantic Comedy                  | `romantic_comedy`                  | `in0000153` |
    | Romantic Epic                    | `romantic_epic`                    | `in0000150` |
    | RuPaul's Drag Race               | `rupaul's_drag_race`               | `in0000253` |
    | Russian                          | `russian`                          | `in0000232` |
    | Samurai                          | `samurai`                          | `in0000199` |
    | Satire                           | `satire`                           | `in0000042` |
    | Saw                              | `saw`                              | `in0000277` |
    | Sci-Fi                           | `sci_fi`                           | `in0000162` |
    | Sci-Fi Epic                      | `sci_fi_epic`                      | `in0000163` |
    | Science & Technology Documentary | `science_&_technology_documentary` | `in0000069` |
    | Scooby-Doo                       | `scooby_doo`                       | `in0000309` |
    | Scream                           | `scream`                           | `in0000292` |
    | Screwball Comedy                 | `screwball_comedy`                 | `in0000043` |
    | Sea Adventure                    | `sea_adventure`                    | `in0000021` |
    | Seinen                           | `seinen`                           | `in0000205` |
    | Serial Killer                    | `serial_killer`                    | `in0000183` |
    | Short                            | `short`                            | `in0000212` |
    | Showbiz Drama                    | `showbiz_drama`                    | `in0000087` |
    | Shrek                            | `shrek`                            | `in0000268` |
    | Shōjo                            | `shōjo`                            | `in0000207` |
    | Shōnen                           | `shōnen`                           | `in0000206` |
    | Sitcom                           | `sitcom`                           | `in0000044` |
    | Sketch Comedy                    | `sketch_comedy`                    | `in0000045` |
    | Slapstick                        | `slapstick`                        | `in0000046` |
    | Slasher Horror                   | `slasher_horror`                   | `in0000115` |
    | Slice of Life                    | `slice_of_life`                    | `in0000208` |
    | Soap Opera                       | `soap_opera`                       | `in0000088` |
    | Soccer                           | `soccer`                           | `in0000173` |
    | Space Sci-Fi                     | `space_sci_fi`                     | `in0000164` |
    | Spaghetti Western                | `spaghetti_western`                | `in0000190` |
    | Spanish                          | `spanish`                          | `in0000233` |
    | Splatter Horror                  | `splatter_horror`                  | `in0000116` |
    | SpongeBob SquarePants            | `spongebob_squarepants`            | `in0000288` |
    | Sport                            | `sport`                            | `in0000174` |
    | Sports Documentary               | `sports_documentary`               | `in0000070` |
    | Spy                              | `spy`                              | `in0000184` |
    | Spy Universe Yash Raj Films      | `spy_universe_yash_raj_films`      | `in0000301` |
    | Stand-Up                         | `stand_up`                         | `in0000047` |
    | Star Trek                        | `star_trek`                        | `in0000247` |
    | Star Wars                        | `star_wars`                        | `in0000243` |
    | Stargate                         | `stargate`                         | `in0000295` |
    | Steampunk                        | `steampunk`                        | `in0000165` |
    | Steamy Romance                   | `steamy_romance`                   | `in0000154` |
    | Stoner Comedy                    | `stoner_comedy`                    | `in0000048` |
    | Stop Motion Animation            | `stop_motion_animation`            | `in0000030` |
    | Super Mario Bros                 | `super_mario_bros`                 | `in0000299` |
    | Superhero                        | `superhero`                        | `in0000008` |
    | Supernatural Fantasy             | `supernatural_fantasy`             | `in0000099` |
    | Supernatural Horror              | `supernatural_horror`              | `in0000117` |
    | Survival                         | `survival`                         | `in0000185` |
    | Survival Competition             | `survival_competition`             | `in0000106` |
    | Suspense Mystery                 | `suspense_mystery`                 | `in0000140` |
    | Swashbuckler                     | `swashbuckler`                     | `in0000022` |
    | Swedish                          | `swedish`                          | `in0000234` |
    | Sword & Sandal                   | `sword_&_sandal`                   | `in0000009` |
    | Sword & Sorcery                  | `sword_&_sorcery`                  | `in0000100` |
    | Talent Competition               | `talent_competition`               | `in0000107` |
    | Talk Show                        | `talk_show`                        | `in0000127` |
    | Tamil                            | `tamil`                            | `in0000235` |
    | Teen Adventure                   | `teen_adventure`                   | `in0000023` |
    | Teen Comedy                      | `teen_comedy`                      | `in0000049` |
    | Teen Drama                       | `teen_drama`                       | `in0000089` |
    | Teen Fantasy                     | `teen_fantasy`                     | `in0000101` |
    | Teen Horror                      | `teen_horror`                      | `in0000118` |
    | Teen Romance                     | `teen_romance`                     | `in0000155` |
    | Teenage Mutant Ninja Turtles     | `teenage_mutant_ninja_turtles`     | `in0000271` |
    | Telenovela                       | `telenovela`                       | `in0000210` |
    | Telugu                           | `telugu`                           | `in0000236` |
    | Terminator                       | `terminator`                       | `in0000286` |
    | Thai                             | `thai`                             | `in0000237` |
    | The Addams Family                | `the_addams_family`                | `in0000313` |
    | The Chronicles of Narnia         | `the_chronicles_of_narnia`         | `in0000289` |
    | The Conjuring Universe           | `the_conjuring_universe`           | `in0000287` |
    | The Hunger Games                 | `the_hunger_games`                 | `in0000303` |
    | The Lord of the Rings            | `the_lord_of_the_rings`            | `in0000279` |
    | The Matrix                       | `the_matrix`                       | `in0000304` |
    | The Real Housewives              | `the_real_housewives`              | `in0000269` |
    | The Walking Dead                 | `the_walking_dead`                 | `in0000282` |
    | The Witcher                      | `the_witcher`                      | `in0000300` |
    | Thriller                         | `thriller`                         | `in0000186` |
    | Time Travel                      | `time_travel`                      | `in0000166` |
    | Toy Story                        | `toy_story`                        | `in0000272` |
    | Tragedy                          | `tragedy`                          | `in0000090` |
    | Tragic Romance                   | `tragic_romance`                   | `in0000156` |
    | Transformers                     | `transformers`                     | `in0000245` |
    | Travel                           | `travel`                           | `in0000128` |
    | Travel Documentary               | `travel_documentary`               | `in0000071` |
    | True Crime                       | `true_crime`                       | `in0000058` |
    | Turkish                          | `turkish`                          | `in0000238` |
    | Urban Adventure                  | `urban_adventure`                  | `in0000024` |
    | Urdu                             | `urdu`                             | `in0000239` |
    | Vampire Horror                   | `vampire_horror`                   | `in0000119` |
    | War                              | `war`                              | `in0000010` |
    | War Epic                         | `war_epic`                         | `in0000011` |
    | Water Sport                      | `water_sport`                      | `in0000175` |
    | Werewolf Horror                  | `werewolf_horror`                  | `in0000120` |
    | Western                          | `western`                          | `in0000191` |
    | Western Epic                     | `western_epic`                     | `in0000189` |
    | Whodunnit                        | `whodunnit`                        | `in0000141` |
    | Witch Horror                     | `witch_horror`                     | `in0000121` |
    | Workplace Drama                  | `workplace_drama`                  | `in0000091` |
    | Wuxia                            | `wuxia`                            | `in0000200` |
    | Yu-Gi-Oh!                        | `yu_gi_oh!`                        | `in0000259` |
    | Zombie Horror                    | `zombie_horror`                    | `in0000122` |

## Examples {#example-imdb-search-builders}

Each tab provides a complete collection definition and explains the filters it uses.

=== "Strings and booleans"

    Finds movies with "Star Wars" in the title, excluding adult titles. `"Star Wars"` is a string and `false` is an unquoted boolean.

    ```yaml
    collections:
      Star Wars Movies:
        collection_order: custom
        sync_mode: sync
        imdb_search:
          type: movie
          title: "Star Wars"
          adult: false
    ```

=== "Dates and numbers"

    Finds action movies released after January 1, 1990, rated at least 7.5 with at least 100,000 votes. Returns up to 100, highest rated first. The date uses `YYYY-MM-DD`; `7.5` is a number and the vote count and limit are integers.

    ```yaml
    collections:
      Highly Rated Action Movies:
        collection_order: custom
        sync_mode: sync
        imdb_search:
          type: movie
          release.after: 1990-01-01
          rating.gte: 7.5
          votes.gte: 100000
          genre: action
          sort_by: rating.desc
          limit: 100
    ```

=== "AND / OR"

    The first collection requires both action and comedy; the second accepts either genre. Both exclude horror. All multi-value strings use commas; `.any` changes the matching to OR.

    ```yaml
    collections:
      Action Comedies:
        collection_order: custom
        sync_mode: sync
        imdb_search:
          type: movie
          genre: "action,comedy"
          genre.not: horror

      Action or Comedy:
        collection_order: custom
        sync_mode: sync
        imdb_search:
          type: movie
          genre.any: "action,comedy"
          genre.not: horror
    ```

=== "Certification dictionary"

    Finds movies with a US content rating of PG. `content_rating` is a dictionary containing a rating string and a region code.

    ```yaml
    collections:
      US PG Movies:
        collection_order: custom
        sync_mode: sync
        imdb_search:
          type: movie
          content_rating:
            rating: "PG"
            region: "US"
    ```

=== "Episodes"

    Selects the 100 highest-rated episodes of The Simpsons. `series` is the show's IMDb ID; `builder_level: episode` makes the collection contain episodes.

    ```yaml
    collections:
      The Simpsons Top 100 Episodes:
        collection_order: custom
        sync_mode: sync
        builder_level: episode
        imdb_search:
          type: tv_episode
          series: tt0096697
          sort_by: rating.desc
          limit: 100
    ```
