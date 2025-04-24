---
hide:
  - toc
---
# TMDb Collection

Finds every item in the TMDb collection.

This Builder is expected to have the full URL to the item or the TMDb ID of the item. Multiple values are supported as either a list :material-information-outline:{ data-tooltip data-tooltip-id="tippy-yaml-lists" } or a comma-separated string.

### Example TMDb Collection Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  The Lord of the Rings:
    tmdb_collection: 
        - 121938 #(3)!
  The Hobbit:
    tmdb_collection:  https://www.themoviedb.org/collection/119 
  Middle Earth:
    tmdb_collection_details: #(1)!
      - 119 #(2)!
      - https://www.themoviedb.org/collection/121938
```

1. You can replace `tmdb_collection` with `tmdb_collection_details` if you would like to fetch and use the TMDb collection's summary, poster, and background from the list. 
2. You can specify multiple collections in `tmdb_collection_details` but it will only use the first one to update the collection details.
3. https://www.themoviedb.org/collection/121938-the-hobbit-collection also accepted

* Posters and background in the library's asset directory will be used over the collection details unless `tmdb_poster`/`tmdb_background` is also specified.

