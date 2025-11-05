---
hide:
  - toc
---
# TMDb Director

???+ tip "People Collections"

    As Plex does not allow People to be part of Collections, Kometa will instead add any media that the person is associated with based om the Builder criteria.

    You can not have a Collection of "Top 10 Actors" for example, as Plex does not allow this.

Finds every item in the TMDb Person's Director Credits.

### Example TMDb Director Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  Steven Spielberg:
    tmdb_director: 488 #(1)!
  The Russo Brothers:
    tmdb_director_details: #(2)!
      - 19271 #(3)!
      - 19272
```

1.  https://www.themoviedb.org/person/488-steven-spielberg also accepted
1.  You can replace `tmdb_director` with `tmdb_director_details` if you would like to fetch and use the TMDb Person's biography and profile from the list
3.  You can specify multiple people in `tmdb_director_details` but it will only use the first one to update the collection details
