---
hide:
  - toc
---
# TVDb Movie

Finds the movie specified

The expected input is a TVDb Movie ID or TVDb Movie URL. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a 
comma-separated string.

???+ tip "Details Builder"

    You can replace `tvdb_movie` with `tvdb_movie_details` if you would like to fetch and use the description from the list

### Example TVDb Movie Builder(s)

```yaml
collections:
  The Lord of the Rings:
    tvdb_movie: 107, 157, 74
```
```yaml
collections:
  The Lord of the Rings:
    tvdb_movie:
      - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-fellowship-of-the-ring
      - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-two-towers
      - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-return-of-the-king
```

* You can update the collection details with the TVDb movie's summary, poster, and background by using `tvdb_movie_details`.
* You can specify multiple movies in `tvdb_movie_details` but it will only use the first one to update the collection details.
* Posters and background in the library's asset directory will be used over the collection details unless `tvdb_poster`/`tvdb_background` is also specified.

```yaml
collections:
  The Lord of the Rings:
    tvdb_movie_details:
      - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-fellowship-of-the-ring
      - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-two-towers
      - https://www.thetvdb.com/movies/the-lord-of-the-rings-the-return-of-the-king
```