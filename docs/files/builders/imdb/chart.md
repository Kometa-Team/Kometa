---
hide:
  - toc
---
# IMDb Chart

Finds every item in an IMDb Chart.

The expected input are the options below. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated and in a specific order.

| Name                                                                                 | Attribute         |             Works with Movies              |              Works with Shows              |
|:-------------------------------------------------------------------------------------|:------------------|:------------------------------------------:|:------------------------------------------:|
| [Box Office](https://www.imdb.com/chart/boxoffice)                                   | `box_office`      | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Most Popular Movies](https://www.imdb.com/chart/moviemeter)                         | `popular_movies`  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Top 250 Movies](https://www.imdb.com/chart/top)                                     | `top_movies`      | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Top Rated English Movies](https://www.imdb.com/chart/top-english-movies)            | `top_english`     | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Most Popular TV Shows](https://www.imdb.com/chart/tvmeter)                          | `popular_shows`   |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| [Top 250 TV Shows](https://www.imdb.com/chart/toptv)                                 | `top_shows`       |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
| [Lowest Rated Movies](https://www.imdb.com/chart/bottom)                             | `lowest_rated`    | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Top Rated Indian Movies](https://www.imdb.com/india/top-rated-indian-movies/)       | `top_indian`      | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Top Rated Tamil Movies](https://www.imdb.com/india/top-rated-tamil-movies/)         | `top_tamil`       | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Top Rated Telugu Movies](https://www.imdb.com/india/top-rated-telugu-movies/)       | `top_telugu`      | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Top Rated Malayalam Movies](https://www.imdb.com/india/top-rated-malayalam-movies/) | `top_malayalam`   | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Trending Indian Movies & Shows](https://www.imdb.com/india/upcoming/)               | `trending_india`  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [Trending Tamil Movies](https://www.imdb.com/india/tamil/)                           | `trending_tamil`  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [Trending Telugu Movies](https://www.imdb.com/india/telugu/)                         | `trending_telugu` | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |

### Example IMDb Chart Builder(s)

```yaml
collections:
  IMDb Top 250:
    imdb_chart: top_movies
    collection_order: custom
    sync_mode: sync
```