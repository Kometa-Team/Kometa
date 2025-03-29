---
hide:
  - toc
---
# TVDb Builders

You can find items using the features of [TheTVDb.com](https://www.thetvdb.com/) (TVDb).

| Builder                     | Description                                                                                                                                                                                         |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:----------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`tvdb_list`](#tvdb-list)   | Finds every item in a [TVDb List](https://www.thetvdb.com/lists) or [TVDb UserList](https://www.thetvdb.com/lists/custom)                                                                           | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`tvdb_show`](#tvdb-show)   | Finds the series specified                                                                                                                                                                          |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | 
| [`tvdb_movie`](#tvdb-movie) | Finds the movie specified                                                                                                                                                                           | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |  :fontawesome-solid-circle-xmark:{ .red }  |

=== "TVDb List"
    
    Finds every item in a [TVDb List](https://www.thetvdb.com/lists) or [TVDb UserList](https://www.thetvdb.com/lists/custom)
    
    The expected input is a TVDb List URL or TVDb UserList URL. Multiple values are supported as either a list or a 
    comma-separated string.
    
    The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
    and in a specific order.

    ???+ tip "Details Builder"

        You can replace `tvdb_list` with `tvdb_list_details` if you would like to fetch and use the description from the list

    ### Example TVDb List Builder(s)

    ```yaml
    collections:
      Arrowverse:
        tvdb_list: https://www.thetvdb.com/lists/arrowverse
        collection_order: custom
        sync_mode: sync
    ```
    ```yaml
    collections:
      Saved by the Bell:
        tvdb_list: https://www.thetvdb.com/lists/6957
        collection_order: custom
        sync_mode: sync
    ```

    * You can update the collection details with the TVDb list's description and poster by using `tvdb_list_details`.
    * You can specify multiple lists in `tvdb_list_details` but it will only use the first one to update the collection details.
    
    ```yaml
    collections:
      Arrowverse:
        tvdb_list_details: https://www.thetvdb.com/lists/arrowverse
        collection_order: custom
        sync_mode: sync
    ```

=== "TVDb Show"
    
    Finds the show specified
    
    The expected input is a TVDb Series ID or TVDb Series URL. Multiple values are supported as either a list or a 
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

=== "TVDb Movie"

    Finds the movie specified
    
    The expected input is a TVDb Movie ID or TVDb Movie URL. Multiple values are supported as either a list or a 
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