---
hide:
  - toc
---
# WeTrakr Ratings

Finds every item the configured WeTrakr account has rated.

???+ warning "WeTrakr Configuration"

    [Configuring WeTrakr](../../../config/wetrakr.md) in the config is required for this builder.

`wetrakr_ratings` accepts a blank value or `true` for every rated item, a number as a minimum rating, or an
object with `minimum`/`maximum` bounds. WeTrakr ratings are on a 0–10 scale with one decimal place.

## Example WeTrakr Ratings Builder(s)

```yaml
collections:
  WeTrakr Rated:
    wetrakr_ratings:
    sync_mode: sync
```

```yaml
collections:
  WeTrakr Rated 7+:
    wetrakr_ratings: 7
    sync_mode: sync
```

```yaml
collections:
  WeTrakr Rated 7 to 9:
    wetrakr_ratings:
      minimum: 7
      maximum: 9
    sync_mode: sync
```

## Attributes

| Attribute | Description               | Values                 |
|:----------|:--------------------------|:------------------------|
| `minimum` | Lowest rating to include  | Number, 0–10, optional |
| `maximum` | Highest rating to include | Number, 0–10, optional |
