---
hide:
  - toc
---
# Letterboxd Builders

You can find items using the lists on [Letterboxd.com](https://letterboxd.com/) (Letterboxd). 

Letterboxd support is powered by `letterboxdpy`. Builder inputs stay the same, but behavior that previously depended on Kometa's custom Letterboxd scraping now follows the fields exposed by `letterboxdpy`.

| Builder                      | Description                              |             Works with Movies              |             Works with Shows             |    Works with Playlists and Custom Sort    |
|:-----------------------------|:-----------------------------------------|:------------------------------------------:|:----------------------------------------:|:------------------------------------------:|
| [`letterboxd_list`](list.md) | Finds every movie in the Letterboxd List | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_crew`](discovery.md#crew) | Finds movies credited to a person in a selected role | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_studio`](discovery.md#other-discovery-builders) | Finds movies from a studio | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_country`](discovery.md#other-discovery-builders) | Finds movies from a country | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_language`](discovery.md#other-discovery-builders) | Finds movies in a language | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_genre`](discovery.md#other-discovery-builders) | Finds movies in a genre | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_theme`](discovery.md#other-discovery-builders) | Finds movies in a theme | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_similar`](discovery.md#other-discovery-builders) | Finds movies similar to a film | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_collection`](discovery.md#other-discovery-builders) | Finds movies in a film collection | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_user_films`](user_films.md) | Finds every movie in a user's watched films | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_user_reviews`](user_reviews.md) | Finds every movie in a user's reviewed films | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
