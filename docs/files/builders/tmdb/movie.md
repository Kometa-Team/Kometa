---
hide:
  - toc
---
# TMDb Movie

Finds the movie specified.

This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

### Example TMDb Movie Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  Anaconda:
    tmdb_movie: #(1)!
      - 336560
  Wizard of Oz & Wicked:
    tmdb_movie_details: #(2)!
      - 630 #(3)!
      - 402431
```

1. You can replace `tmdb_movie` with `tmdb_movie_details` if you would like to fetch and use the TMDb show's summary, poster, and background from the list
2. You can specify multiple shows in `tmdb_movie_details` but it will only use the first one to update the collection details
3. https://www.themoviedb.org/movie/630-the-wizard-of-oz also accepted

* Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.

