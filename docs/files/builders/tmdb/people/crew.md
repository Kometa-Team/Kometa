---
hide:
  - toc
---
# TMDb Crew

???+ tip "People Collections"

    As Plex does not allow People to be part of Collections, Kometa will instead add any media that the person is associated with based om the Builder criteria.

    You can not have a Collection of "Top 10 Actors" for example, as Plex does not allow this.

Finds every item in the TMDb Person's Crew Credits.

### Example TMDb Crew Builder(s)

```yaml title="Press the + icon to learn more"
collections:
  Quentin Tarantino:
    tmdb_crew: 138 #(1)!
  The Skarsgards Family:
    tmdb_crew_details: #(2)!
      - 28846 #(3)!
      - 137905
      - 63764
      - 1640
      - 1281937
      - 2367741
```

1.  https://www.themoviedb.org/person/138-quentin-tarantino also accepted
2.  You can replace `tmdb_crew` with `tmdb_crew_details` if you would like to fetch and use the TMDb Person's biography and profile from the list
3.  You can specify multiple people in `tmdb_crew_details` but it will only use the first one to update the collection details
