---
hide:
  - toc
---
# Trakt Chart

Finds movies and shows from Trakt charts.

???+ warning "Trakt Configuration"

    [Configuring Trakt](../../../config/trakt.md) in the config is required for any of these builders.

## Chart types

| Chart | Description | Authentication required |
|:------|:------------|:------------------------:|
| `trending` | Trakt's Trending Movies/Shows | No |
| `popular` | Trakt's Popular Movies/Shows | No |
| `recommended` | Trakt's Recommended Movies/Shows | :lock: **Yes** |
| `watched` | Trakt's Watched Movies/Shows | :lock: **Yes** |
| `collected` | Trakt's Collected Movies/Shows | :lock: **Yes** |

Links to each chart are available for `daily`, `weekly`, `monthly`, `yearly`, and `all` time periods. The `time_period` option does not apply to `trending` or `popular`.

## Options

| Option | Description | Default / values |
|:-------|:------------|:-----------------|
| `chart` | The Trakt chart to query. | `trending`, `popular`, `recommended`, `watched`, or `collected` |
| `time_period` | The time period for the chart. | `weekly`; `daily`, `weekly`, `monthly`, `yearly`, or `all` |
| `limit` | Limits the number of returned items. | `10`; any number of items |
| `query` | Searches titles and descriptions. | Any string |
| `years` | Searches for specific years or year ranges. | `1950` or `1950-1959` |
| `genres` | Filters by movie or show genres. | See the [genre values](#genre-values) below |
| `languages` | Filters by movie or show languages. | See the expandable [language and country values](#language-and-country-values) below |
| `countries` | Filters by movie or show countries. | See the expandable [language and country values](#language-and-country-values) below |
| `certifications` | Filters by certification. | Movie: `g`, `pg`, `pg-13`, `r`, `nr`; show: `tv-y`, `tv-y7`, `tv-g`, `tv-pg`, `tv-14`, `tv-ma`, `nr` |
| `runtimes` | Filters by runtime in minutes. | A range such as `0-60` |
| `ratings` / `votes` | Filters by Trakt rating or vote count ranges. | A range such as `80-100` |
| `tmdb_ratings` / `tmdb_votes` | Filters by TMDb rating or vote count ranges. | A range such as `8.5-10.0` |
| `imdb_ratings` / `imdb_votes` | Filters by IMDb rating or vote count ranges. | A range such as `80-100` |
| `rt_meters` / `rt_user_meters` | Filters by Rotten Tomatoes scores. | A range from `0-100` |
| `metascores` | Filters by Metacritic score. | A range from `0-100` |
| `studio_ids` / `network_ids` | Filters by studio or network IDs. | A comma-separated list |
| `status` | Filters shows by status. | `returning`, `production`, `planned`, `canceled`, or `ended` |

???+ note "Genre values"

    | Library Type | Values |
    |:--------|:-------|
    | Movies | `action`, `adventure`, `animation`, `anime`, `comedy`, `crime`, `documentary`, `drama`, `family`, `fantasy`, `history`, `holiday`, `horror`, `music`, `musical`, `mystery`, `none`, `romance`, `science-fiction`, `short`, `sporting-event`, `superhero`, `suspense`, `thriller`, `war`, `western` |
    | Shows | `action`, `adventure`, `animation`, `anime`, `biography`, `children`, `comedy`, `crime`, `documentary`, `drama`, `family`, `fantasy`, `game-show`, `history`, `holiday`, `home-and-garden`, `horror`, `mini-series`, `music`, `musical`, `mystery`, `news`, `none`, `reality`, `romance`, `science-fiction`, `short`, `soap`, `special-interest`, `sporting-event`, `superhero`, `suspense`, `talk-show`, `thriller`, `war`, `western` |

???+ note "Language values"

    The following values are supported. Use the movie or show list appropriate to the content being filtered.

    | Library Type | Values |
    |:--------|:-------|
    | Movies | `ab`, `af`, `ak`, `sq`, `am`, `ar`, `an`, `hy`, `as`, `av`, `ay`, `az`, `bm`, `ba`, `eu`, `be`, `bn`, `bi`, `nb`, `bs`, `bg`, `my`, `ca`, `km`, `ch`, `ce`, `ny`, `zh`, `kw`, `co`, `cr`, `hr`, `cs`, `da`, `dv`, `nl`, `dz`, `en`, `eo`, `et`, `fo`, `fj`, `fi`, `fr`, `ff`, `gd`, `gl`, `lg`, `ka`, `de`, `el`, `gn`, `gu`, `ht`, `ha`, `he`, `hi`, `hu`, `is`, `ig`, `id`, `ie`, `iu`, `ik`, `ga`, `it`, `ja`, `jv`, `kl`, `kn`, `ks`, `kk`, `rw`, `ky`, `kg`, `ko`, `ku`, `lo`, `la`, `lv`, `li`, `ln`, `lt`, `lb`, `mk`, `mg`, `ms`, `ml`, `mt`, `mi`, `mr`, `mh`, `mn`, `nv`, `ne`, `se`, `no`, `nn`, `oc`, `oj`, `or`, `om`, `os`, `pi`, `pa`, `fa`, `pl`, `pt`, `ps`, `qu`, `ro`, `rm`, `rn`, `ru`, `sm`, `sg`, `sa`, `sc`, `sr`, `sn`, `ii`, `sd`, `si`, `sk`, `sl`, `so`, `st`, `es`, `su`, `sw`, `ss`, `sv`, `tl`, `ty`, `tg`, `ta`, `tt`, `te`, `th`, `bo`, `ti`, `to`, `ts`, `tn`, `tr`, `tk`, `tw`, `ug`, `uk`, `ur`, `uz`, `vi`, `cy`, `fy`, `wo`, `xh`, `yi`, `yo`, `za`, `zu` |
    | Shows | `ab`, `af`, `sq`, `am`, `ar`, `hy`, `eu`, `be`, `bn`, `nb`, `bs`, `bg`, `ca`, `km`, `zh`, `hr`, `cs`, `da`, `dv`, `nl`, `en`, `et`, `fi`, `fr`, `gl`, `ka`, `de`, `el`, `gu`, `he`, `hi`, `hu`, `is`, `id`, `ga`, `it`, `ja`, `kn`, `ko`, `lo`, `la`, `lv`, `lt`, `lb`, `mk`, `ms`, `ml`, `mt`, `mi`, `mr`, `ne`, `se`, `no`, `nn`, `pa`, `fa`, `pl`, `pt`, `ro`, `ru`, `sr`, `si`, `sk`, `sl`, `es`, `sv`, `tl`, `ta`, `te`, `th`, `tr`, `tw`, `uk`, `ur`, `uz`, `vi`, `cy` |

???+ note "Country values"

    | Library Type | Values |
    |:--------|:-------|
    | Movies | `af`, `al`, `dz`, `as`, `ad`, `ao`, `ai`, `aq`, `ag`, `ar`, `am`, `aw`, `au`, `at`, `az`, `bs`, `bh`, `bd`, `bb`, `by`, `be`, `bz`, `bj`, `bm`, `bt`, `bo`, `ba`, `bw`, `bv`, `br`, `io`, `bn`, `bg`, `bf`, `bi`, `cv`, `kh`, `cm`, `ca`, `ky`, `cf`, `td`, `cl`, `cn`, `cx`, `co`, `km`, `cg`, `cd`, `ck`, `cr`, `hr`, `cu`, `cy`, `cz`, `ci`, `dk`, `dj`, `dm`, `do`, `ec`, `eg`, `sv`, `gq`, `er`, `ee`, `sz`, `et`, `fk`, `fo`, `fj`, `fi`, `fr`, `gf`, `pf`, `tf`, `ga`, `gm`, `ge`, `de`, `gh`, `gi`, `gr`, `gl`, `gd`, `gp`, `gu`, `gt`, `gn`, `gw`, `gy`, `ht`, `va`, `hn`, `hk`, `hu`, `is`, `in`, `id`, `ir`, `iq`, `ie`, `il`, `it`, `jm`, `jp`, `jo`, `kz`, `ke`, `ki`, `kp`, `kr`, `kw`, `kg`, `la`, `lv`, `lb`, `ls`, `lr`, `ly`, `li`, `lt`, `lu`, `mo`, `mg`, `mw`, `my`, `mv`, `ml`, `mt`, `mh`, `mq`, `mr`, `mu`, `yt`, `mx`, `md`, `mc`, `mn`, `me`, `ms`, `ma`, `mz`, `mm`, `na`, `nr`, `np`, `nl`, `nc`, `nz`, `ni`, `ne`, `ng`, `nf`, `mk`, `mp`, `no`, `om`, `pk`, `pw`, `ps`, `pa`, `pg`, `py`, `pe`, `ph`, `pn`, `pl`, `pt`, `pr`, `qa`, `ro`, `ru`, `rw`, `re`, `sh`, `kn`, `lc`, `vc`, `ws`, `sm`, `st`, `sa`, `sn`, `rs`, `sc`, `sl`, `sg`, `sk`, `si`, `sb`, `so`, `za`, `ss`, `es`, `lk`, `sd`, `sr`, `se`, `ch`, `sy`, `tw`, `tj`, `tz`, `th`, `tl`, `tg`, `tk`, `to`, `tt`, `tn`, `tr`, `tm`, `tc`, `tv`, `ug`, `ua`, `ae`, `gb`, `us`, `um`, `uy`, `uz`, `vu`, `ve`, `vn`, `vg`, `vi`, `wf`, `eh`, `ye`, `zm`, `zw` |
    | Shows | `af`, `ad`, `ar`, `am`, `au`, `at`, `bd`, `by`, `be`, `bz`, `ba`, `bw`, `br`, `io`, `bg`, `kh`, `ca`, `td`, `cl`, `cn`, `co`, `hr`, `cu`, `cy`, `cz`, `dk`, `do`, `ec`, `eg`, `ee`, `sz`, `fi`, `fr`, `ge`, `de`, `gr`, `hn`, `hk`, `hu`, `is`, `in`, `id`, `ir`, `iq`, `ie`, `il`, `it`, `jp`, `jo`, `kz`, `kp`, `kr`, `kw`, `la`, `lv`, `lb`, `lt`, `lu`, `my`, `mv`, `mt`, `mx`, `md`, `mc`, `me`, `ma`, `np`, `nl`, `nz`, `ng`, `mk`, `mp`, `no`, `pk`, `pa`, `py`, `pe`, `ph`, `pl`, `pt`, `pr`, `qa`, `ro`, `ru`, `sa`, `sn`, `rs`, `sg`, `sk`, `si`, `za`, `es`, `lk`, `se`, `ch`, `sy`, `tw`, `th`, `tg`, `tn`, `tr`, `ua`, `ae`, `gb`, `us`, `uy`, `ve`, `vn` |

The `sync_mode: sync` and `collection_order: custom` settings are recommended because these lists are continuously updated and returned in a specific order.

## Example

```yaml
collections:
  Trakt Trending:
    trakt_chart:
      chart: trending
      time_period: weekly
      limit: 10
    collection_order: custom
    sync_mode: sync
```
