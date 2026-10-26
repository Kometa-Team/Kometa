# Letterboxd Builders

Collect movies from [Letterboxd](https://letterboxd.com/) lists, user pages,
filmographies, and discovery categories. All builders support **movies, playlists,
and custom sorting**; they do not support shows.

## Choose a builder

| Builder | Finds |
|:--------|:------|
| [`letterboxd_list`](#letterboxd-list) | Movies in lists or films-search pages |
| [`letterboxd_user_films`](#letterboxd-user-films) | A user's watched films |
| [`letterboxd_user_reviews`](#letterboxd-user-reviews) | A user's reviewed films |
| [`letterboxd_crew`](#crew) | A person's credits in a selected role |
| [Other discovery builders](#other-discovery-builders) | Studio, country, language, genre, theme, similar films, or film collection |

Use `collection_order: custom` to preserve the returned order and `sync_mode: sync`
to keep membership synchronized. **Discovery custom ordering requires a single
builder value per collection.** User pages use their default returned order,
rather than a requested sort (see [compatibility options](#compatibility-options)).

## Lists and film searches {#letterboxd-list}

`letterboxd_list` accepts a supported Letterboxd URL, including standard user lists,
`/films/...` searches, and private links starting with `https://boxd.it/`.
Supply multiple URLs as a YAML list or comma-separated string to combine sources.
For people and discovery categories, use the dedicated [discovery builders](#discovery-and-filmographies).

Use a URL string directly, or a dictionary with `url` and filters:

| Attribute | Value | Applies to |
|:----------|:------|:-----------|
| `url` | Supported URL string | Lists and films searches |
| `limit` | Integer greater than 1 | Lists and films searches; recommended for large searches |
| `year` | Year-range string, such as `"1990-1999"` | Lists and films searches |
| `rating` | Rating-range string, such as `"8-10"` | `/films/...` URLs only; uses the owner's rating on a 10-point scale |
| `note` | Text string | `/films/...` URLs only; matches the owner's note |

!!! note "URL-specific filters"

    Standard user lists do not expose per-item owner ratings or notes through
    `letterboxdpy`, so `rating` and `note` are ignored for those URLs. They are
    available only on `/films/...` pages that expose the relevant fields.

<span id="example-letterboxd-list-builders"></span>

=== "List URL"

    Follows Vulture's 101 Best Movie Endings list in source order. The builder
    value is a full URL string.

    ```yaml
    collections:
      Vulture's 101 Best Movie Endings:
        letterboxd_list: https://letterboxd.com/brianformo/list/vultures-101-best-movie-endings/
        collection_order: custom
        sync_mode: sync
    ```

=== "Year range and summary"

    Selects only the 1990s movies from that list and copies its description to
    the collection summary. `year` is a quoted range string, not a single year.

    ```yaml
    collections:
      Vulture's Best Movie Endings From the 90s:
        letterboxd_list_details:
          url: https://letterboxd.com/brianformo/list/vultures-101-best-movie-endings/
          year: "1990-1999"
        collection_order: custom
        sync_mode: sync
    ```

`letterboxd_list_details` selects the same items as `letterboxd_list` and copies
the source description. With multiple lists, **only the first supplies the summary**.

## User films and reviews

<span id="letterboxd-user-films"></span>
<span id="letterboxd-user-reviews"></span>

Use `letterboxd_user_films` for watched films or `letterboxd_user_reviews` for
reviewed films. Both accept a username string or a dictionary with the options
below. Multiple users can be supplied as a YAML list or comma-separated string;
use a YAML list of dictionaries for different per-user filters.

| Attribute | Value | Purpose |
|:----------|:------|:--------|
| `username` | String, required in dictionary form | User whose films or reviews to collect |
| `min_rating` | Number, 0-10 | Minimum user rating on a 10-point scale |
| `limit` | Integer greater than 1 | Cap results; recommended for large user histories |
| `year` | Year-range string, such as `"1990-1999"` | Filter release years |
| `note` | Text string | Match review text for reviews; ignored for watched films |

The details variants, `letterboxd_user_films_details` and
`letterboxd_user_reviews_details`, are accepted for consistency, but user pages
currently provide no description to copy.

### Compatibility options

Letterboxd access uses `letterboxdpy`. The following options remain accepted for
older configurations, but do not control fetching as their names might suggest:

| Attribute | Accepted value | Current behaviour |
|:----------|:---------------|:------------------|
| `sort_by` | Sort name below; default `release_date_newest` | Uses default page order; a non-default request logs a warning |
| `incremental` | Boolean; runtime default `false` | Always fetches normally; `true` logs a warning rather than enabling incremental fetching |

??? info "Accepted legacy sort names"

    `release_date_newest`, `release_date_earliest`, `name`, `popularity`,
    `when_added_newest`, `when_added_earliest`, `when_rated_newest`, `when_rated_earliest`,
    `average_rating_highest`, `average_rating_lowest`, `user_rating_highest`,
    `user_rating_lowest`, `length_shortest`, `length_longest`.

<span id="example-letterboxd-user-films-builders"></span>
<span id="example-letterboxd-user-reviews-builders"></span>

Replace the placeholder usernames in these examples with real Letterboxd usernames.

=== "Username string"

    Selects the user's watched films in the default returned order. The username
    is a string, rather than an ID or a URL.

    ```yaml
    collections:
      User Watched Films:
        letterboxd_user_films: some_letterboxd_username
        collection_order: custom
        sync_mode: sync
    ```

=== "Multiple users and ratings"

    Combines watched films rated at least 8 by the first user with films rated
    at least 9 by the second. The YAML list combines sources; it does not require
    both users to have rated the same film. Ratings use a 10-point scale.

    ```yaml
    collections:
      Friends' Highly Rated Films:
        letterboxd_user_films:
          - username: first_letterboxd_username
            min_rating: 8
          - username: second_letterboxd_username
            min_rating: 9
        collection_order: custom
        sync_mode: sync
    ```

=== "Review text and limits"

    Selects up to 50 reviewed films matching the user's review text filter
    "favorite", rated at least 7.5. `note` is a string, `min_rating` is a decimal
    number, and `limit` is an integer. This does not request a different sort order.

    ```yaml
    collections:
      User Favorite Reviews:
        letterboxd_user_reviews:
          username: some_letterboxd_username
          note: "favorite"
          min_rating: 7.5
          limit: 50
        collection_order: custom
        sync_mode: sync
    ```

## Discovery and filmographies

Discovery builders use **slugs**, the identifying part of a Letterboxd URL,
rather than passing those pages to `letterboxd_list`. For example, `/studio/a24/`
uses the slug `a24`.

All discovery builders accept `limit` and `year`. All except `letterboxd_similar`
also accept `sort_by`. Use dictionary form to add these options. Keep one discovery
builder value per collection when using custom ordering.

| Option | Purpose |
|:-------|:--------|
| `limit` | Cap returned movies |
| `year` | Filter release years |
| `sort_by` | Request discovery order; unavailable for `letterboxd_similar` |

### Crew {#crew}

`letterboxd_crew` requires both of these string attributes:

| Attribute | Allowed values |
|:----------|:---------------|
| `role` | `actor`, `director`, `writer`, `casting`, `editor`, `cinematography`, `composer` |
| `person` | Person slug, such as `marlon-brando` |

This collection selects Francis Ford Coppola's directing credits. Change `role`
to select another supported credit type, using the appropriate person slug.

```yaml
collections:
  Francis Ford Coppola:
    letterboxd_crew:
      role: director
      person: francis-ford-coppola
    collection_order: custom
    sync_mode: sync
```

### Other discovery builders {#other-discovery-builders}

Pass a slug directly as a string, or use the named attribute in dictionary form.

| Builder | Dictionary attribute | URL path and slug |
|:--------|:---------------------|:------------------|
| `letterboxd_studio` | `studio` | `/studio/a24/`: `a24` |
| `letterboxd_country` | `country` | `/films/country/usa/`: `usa` |
| `letterboxd_language` | `language` | `/films/language/english/`: `english` |
| `letterboxd_genre` | `genre` | `/films/genre/crime/`: `crime` |
| `letterboxd_theme` | `theme` | `/films/theme/crime-drugs-and-gangsters/`: `crime-drugs-and-gangsters` |
| `letterboxd_similar` | `film` | `/film/the-godfather/similar/`: `the-godfather` |
| `letterboxd_collection` | `collection` | `/films/in/beetlejuice-collection-2/`: `beetlejuice-collection-2` |

=== "Slug string"

    Selects movies similar to The Godfather. The value is the film slug, not
    its full URL. This builder does not accept `sort_by`.

    ```yaml
    collections:
      Similar to The Godfather:
        letterboxd_similar: the-godfather
        collection_order: custom
        sync_mode: sync
    ```

=== "Studio and ordering"

    Selects A24 movies, requesting newest release dates first. Unlike user-page
    sorting, discovery `sort_by` is supported for this builder.

    ```yaml
    collections:
      A24 by Release:
        letterboxd_studio:
          studio: a24
          sort_by: release_date_newest
        collection_order: custom
        sync_mode: sync
    ```

=== "Theme and limit"

    Selects up to 20 movies in the Crime, Drugs and Gangsters theme, requesting
    best-match order. The theme slug and sort name are strings; the limit is an integer.

    ```yaml
    collections:
      Crime, Drugs and Gangsters:
        letterboxd_theme:
          theme: crime-drugs-and-gangsters
          sort_by: best_match
          limit: 20
        collection_order: custom
        sync_mode: sync
    ```
