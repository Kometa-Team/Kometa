---
hide:
  - toc
---
# TMDb Writer

???+ tip "People Collections"

    As Plex does not allow People to be part of Collections, Kometa will instead add any media that the person is associated with based om the Builder criteria.

    You can not have a Collection of "Top 10 Actors" for example, as Plex does not allow this.

Finds every item in the TMDb Person's Writer Credits.

### Example TMDb Writer Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  Woody Allen:
    tmdb_writer: 
        - 1243 #(3)!
  The Daniels:
    tmdb_writer_details: #(1)!
      - 1383612 #(2)!
      - https://www.themoviedb.org/person/1317730
```

1.  You can replace `tmdb_writer` with `tmdb_writer_details` if you would like to fetch and use the TMDb collection's summary, poster, and background from the list
2.  You can specify multiple people in `tmdb_writer_details` but it will only use the first one to update the collection details
3.  https://www.themoviedb.org/person/1243-woody-allen also accepted