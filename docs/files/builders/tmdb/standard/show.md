---
hide:
  - toc
---
# TMDb Show

Finds the show specified.

This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

### Example TMDb Show Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  Star Wars (Animated Shows):
    tmdb_show:
      - 4194 #(1)!
      - 60554
    Pokémon Evolutions & Chronicles:
      tmdb_show_details: #(2)!
        - 132636 #(3)!
        - 13230
```

1. https://www.themoviedb.org/tv/4194-star-wars-the-clone-wars also accepted
2. You can replace `tmdb_show` with `tmdb_show_details` if you would like to fetch and use the TMDb show's summary, poster, and background from the list
3. You can specify multiple shows in `tmdb_show_details` but it will only use the first one to update the collection details

* Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.
