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
| [`letterboxd_user_films`](user_films.md) | Finds every movie in a user's watched films | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
| [`letterboxd_user_reviews`](user_reviews.md) | Finds every movie in a user's reviewed films | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-xmark:{ .red } | :fontawesome-solid-circle-check:{ .green } |
