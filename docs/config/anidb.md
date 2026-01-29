---
search:
  boost: 3
hide:
  - toc
---
# AniDB Attributes

Configuring [AniDB](https://anidb.net/) is optional. The AniDB integration uses a replacement API service that doesn't require user authentication.

An `anidb` mapping is in the root of the config file, sampled below.

```yaml title="config.yml AniDB sample"
anidb:
  language: en
  cache_expiration: 60
```

| Attribute          | Description                                                             | Allowed Values (default in **bold**)                                                |                 Required                 |
|:-------------------|:------------------------------------------------------------------------|:------------------------------------------------------------------------------------|:----------------------------------------:|
| `language`         | [ISO 639-1 code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) | Two-letter code, e.g. **`en`**                                                      | :fontawesome-solid-circle-xmark:{ .red } |
| `cache_expiration` | Days before each cache mapping expires and must be re-cached.           | Integer, e.g. **`60`**                                                              | :fontawesome-solid-circle-xmark:{ .red } |
