---
hide:
  - toc
---
# TMDb Actor

???+ tip "People Collections"

    As Plex does not allow People to be part of Collections, Kometa will instead add any media that the person is associated with based om the Builder criteria.

    You can not have a Collection of "Top 10 Actors" for example, as Plex does not allow this.

Finds every item in the TMDb Person's Actor Credits.

### Example TMDb Actor Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  Robin Williams:
    tmdb_actor: 2157 #(1)!
  Hemsworth Brothers:
    tmdb_actor_details: #(2)!
      - 74568 #(3)!
      - 96066
      - 216986
```

1.  https://www.themoviedb.org/person/2157-robin-williams also accepted
2.  You can replace `tmdb_actor` with `tmdb_actor_details` if you would like to fetch and use the TMDb Person's biography and profile from the list
3.  You can specify multiple people in `tmdb_actor_details` but it will only use the first one to update the collection details
