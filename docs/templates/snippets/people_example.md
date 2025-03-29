```yaml
libraries:
  Movies:
    collection_files:
      - default: CODE_NAME
        template_variables:
          data:
            depth: 10 #(1)!
            limit: 20 #(2)!
          style: rainier #(3)!
          sort_by: title.asc
          tmdb_person_offset_Richard Brooks: 1 #(4)!
```

1. Check the first 10 casting credits in each movie
2. Create 20 collections maximum
3. use the [rainier Style](#rainier-style)
4. There are two Richard Brooks, so use the 2nd [Richard Brooks](https://www.themoviedb.org/search?query=Richard%20Brooks) found on TMDb