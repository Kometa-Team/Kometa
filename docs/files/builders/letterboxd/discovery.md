---
hide:
  - toc
---
# Letterboxd Discovery Builders

These builders use Letterboxd slugs instead of treating discovery and filmography pages as `letterboxd_list` URLs. The slug is the part of the Letterboxd URL that identifies the person, studio, category, or film.

All discovery builders support `limit` and `year`. All except `letterboxd_similar` also support `sort_by`.

## Crew

`letterboxd_crew` requires a `role` and `person`.

| Attribute | Values |
|:----------|:-------|
| `role` | `actor`, `director`, `writer`, `casting`, `editor`, `cinematography`, or `composer` |
| `person` | Letterboxd person slug, such as `marlon-brando` |

```yaml
collections:
  Marlon Brando:
    letterboxd_crew:
      role: actor
      person: marlon-brando

  Francis Ford Coppola:
    letterboxd_crew:
      role: director
      person: francis-ford-coppola
```

## Other Discovery Builders

The string form accepts the slug directly. Use the object form to add `limit`, `year`, or `sort_by`.

| Builder | Slug attribute | Example source URL |
|:--------|:---------------|:-------------------|
| `letterboxd_studio` | `studio` | `/studio/a24/` |
| `letterboxd_country` | `country` | `/films/country/usa/` |
| `letterboxd_language` | `language` | `/films/language/english/` |
| `letterboxd_genre` | `genre` | `/films/genre/crime/` |
| `letterboxd_theme` | `theme` | `/films/theme/crime-drugs-and-gangsters/` |
| `letterboxd_similar` | `film` | `/film/the-godfather/similar/` |
| `letterboxd_collection` | `collection` | `/films/in/beetlejuice-collection-2/` |

```yaml
collections:
  A24 by Release:
    letterboxd_studio:
      studio: a24
      sort_by: release_date_newest

  English Language:
    letterboxd_language:
      language: english
      limit: 10

  Crime:
    letterboxd_genre:
      genre: crime
      limit: 20

  Crime, Drugs and Gangsters:
    letterboxd_theme:
      theme: crime-drugs-and-gangsters
      sort_by: best_match
      limit: 20

  Similar to The Godfather:
    letterboxd_similar: the-godfather

  Beetlejuice Collection:
    letterboxd_collection:
      collection: beetlejuice-collection-2
      sort_by: release_date_earliest
```
