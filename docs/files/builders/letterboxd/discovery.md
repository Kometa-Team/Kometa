---
hide:
  - toc
---
# Letterboxd Discovery Builders

These builders use Letterboxd slugs instead of treating discovery and filmography pages as `letterboxd_list` URLs. The slug is the part of the Letterboxd URL that identifies the person, studio, category, or film.

All discovery builders support `limit` and `year`. All except `letterboxd_similar` also support `sort_by`.

The `sync_mode: sync` and `collection_order: custom` settings are recommended when the collection should remain synchronized and preserve Letterboxd's returned order. Custom ordering requires a single discovery builder value per collection.

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

Pass the slug directly in the string form, such as `letterboxd_studio: a24`. In the object form, use the named slug attribute shown below and add `limit`, `year`, or `sort_by` as needed.

| Builder | Slug attribute | Example values |
|:--------|:---------------|:---------------|
| `letterboxd_studio` | `studio` | `/studio/a24/` → `a24` |
| `letterboxd_country` | `country` | `/films/country/usa/` → `usa` |
| `letterboxd_language` | `language` | `/films/language/english/` → `english` |
| `letterboxd_genre` | `genre` | `/films/genre/crime/` → `crime` |
| `letterboxd_theme` | `theme` | `/films/theme/crime-drugs-and-gangsters/` → `crime-drugs-and-gangsters` |
| `letterboxd_similar` | `film` | `/film/the-godfather/similar/` → `the-godfather` |
| `letterboxd_collection` | `collection` | `/films/in/beetlejuice-collection-2/` → `beetlejuice-collection-2` |

```yaml
collections:
  A24:
    letterboxd_studio: a24

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
