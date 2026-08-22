---
hide:
  - toc
---
# FlickList Ratings

Finds every item the configured FlickList API key's account has rated.

???+ warning "FlickList Configuration"

    [Configuring FlickList](../../../config/flicklist.md) in the config is required for this builder.

`flicklist_ratings` accepts a blank value or `true` for every rated item, a number as a minimum rating, or an
object with `minimum`/`maximum` bounds. FlickList ratings are documented as half-point increments (0.5–10) but
the API does not currently enforce that, so a fractional rating like `5.3` can come back from FlickList itself.

## Example FlickList Ratings Builder(s)

```yaml
collections:
  FlickList Rated:
    flicklist_ratings:
    sync_mode: sync
```

```yaml
collections:
  FlickList Rated 7+:
    flicklist_ratings: 7
    sync_mode: sync
```

```yaml
collections:
  FlickList Rated 7 to 9:
    flicklist_ratings:
      minimum: 7
      maximum: 9
    sync_mode: sync
```

## Attributes

| Attribute | Description               | Values                   |
|:----------|:--------------------------|:-------------------------|
| `minimum` | Lowest rating to include  | Number, 0.5–10, optional |
| `maximum` | Highest rating to include | Number, 0.5–10, optional |
