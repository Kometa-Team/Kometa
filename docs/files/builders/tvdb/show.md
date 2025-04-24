---
hide:
  - toc
---
# TVDb Show

Finds the show specified

The expected input is a TVDb Series ID or TVDb Series URL. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a 
comma-separated string.

???+ tip "Details Builder"

    You can replace `tvdb_show` with `tvdb_show_details` if you would like to fetch and use the description from the list

### Example TVDb Show Builder(s)

```yaml
collections:
  Star Wars (Animated Shows):
    tvdb_show: 83268, 283468
```
```yaml
collections:
  Star Wars (Animated Shows):
    tvdb_show:
      - https://www.thetvdb.com/series/star-wars-the-clone-wars
      - https://www.thetvdb.com/series/star-wars-rebels
```

* You can update the collection details with the TVDb show's summary, poster, and background by using `tvdb_show_details`.
* You can specify multiple shows in `tvdb_show_details` but it will only use the first one to update the collection details.
* Posters and background in the library's asset directory will be used over the collection details unless `tvdb_poster`/`tvdb_background` is also specified.

```yaml
collections:
  Star Wars (Animated Shows):
    tvdb_show_details: 83268, 283468
```
