---
search:
  boost: 3
hide:
  - toc
---
# AniDB Attributes

Configuring [AniDB](https://anidb.net/) using `username` and `password` is optional but allows you to access mature content with AniDB Builders.

**All AniDB Builders still work without this, they will just not have mature content**

An `anidb` mapping is in the root of the config file, sampled below.

```yaml title="config.yml AniDB sample"
anidb:
  language: en
  cache_expiration: 60
  username: ######
  password: ######
```

| Attribute          | Description                                                             | Allowed Values (default in **bold**)                                                |                 Required                 |
|:-------------------|:------------------------------------------------------------------------|:------------------------------------------------------------------------------------|:----------------------------------------:|
| `language`         | [ISO 639-1 code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) | Two-letter code, e.g. **`en`**                                                      | :fontawesome-solid-circle-xmark:{ .red } |
| `cache_expiration` | Days before each cache mapping expires and must be re-cached.           | Integer, e.g. **`60`**                                                              | :fontawesome-solid-circle-xmark:{ .red } |
| `username`         | AniDB username.                                                         | Any valid username or leave **blank**                                               | :fontawesome-solid-circle-xmark:{ .red } |
| `password`         | AniDB password.                                                         | Any valid password or leave **blank**                                               | :fontawesome-solid-circle-xmark:{ .red } |
