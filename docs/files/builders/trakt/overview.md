---
hide:
  - toc
---
# Trakt Builders

You can find items using the features of [Trakt.tv](https://trakt.tv/) (Trakt). 

???+ warning "Trakt Configuration"

    [Configuring Trakt](../../../config/trakt.md) in the config is required for any of these builders.

| Builder                                       | Description                                                                                                                                                                                                                                                                 |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:----------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`trakt_list`](list.md)                       | Finds every movie/show in the Trakt List                                                                                                                                                                                                                                    | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`trakt_chart`](chart.md)                     | Finds the movies/shows in the Trakt Chart                                                                                                                                                                                                                                   | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`trakt_userlist`](userlist.md)               | Finds every movie/show in the Trakt UserList                                                                                                                                                                                                                                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`trakt_recommendations`](recommendations.md) | Finds the movies/shows in Trakt's Personal Recommendations for your User [Movies](https://trakt.docs.apiary.io/#reference/recommendations/movies/get-movie-recommendations)/[Shows](https://trakt.docs.apiary.io/#reference/recommendations/shows/get-show-recommendations) | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | 
| [`trakt_boxoffice`](box-office.md)            | Finds the 10 movies in Trakt's Top Box Office [Movies](https://trakt.tv/movies/boxoffice) list                                                                                                                                                                              | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } |
