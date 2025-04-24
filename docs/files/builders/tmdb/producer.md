---
hide:
  - toc
---
# TMDb Producer

???+ tip "People Collections"

    As Plex does not allow People to be part of Collections, Kometa will instead add any media that the person is associated with based om the Builder criteria.

    You can not have a Collection of "Top 10 Actors" for example, as Plex does not allow this.

Finds every item in the TMDb Person's Producer Credits.

### Example TMDb Producer Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  Adam Sandler:
    tmdb_producer: 19292 #(3)! 
  The Wachowskis:
    tmdb_producer_details: #(1)!
      - 9339 #(2)!
      - 9340
```

1.  You can replace `tmdb_producer` with `tmdb_producer_details` if you would like to fetch and use the TMDb collection's summary, poster, and background from the list
2.  You can specify multiple producers in `tmdb_producer_details` but it will only use the first one to update the collection details
3.  https://www.themoviedb.org/person/19292-adam-sandler also accepted
