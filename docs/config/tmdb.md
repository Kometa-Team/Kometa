---
search:
  boost: 3
hide:
  - toc
---
# TMDb Attributes

Filling in your [TheMovieDb](https://www.themoviedb.org/) API key is mandatory in order to run Kometa. 

A `tmdb` mapping is in the root of the config file, sampled below.

```yaml title="config.yml TMDb sample"
tmdb:
  apikey: 147abc258def369ghi
  language: en
  region: US
  cache_expiration: 60
```

| Attribute             | Description                                                                                                                                                                    | Allowed Values (default in **bold**)   |                  Required                  |
|:----------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------|:------------------------------------------:|
| `apikey`              | User TMDb V3 API key.                                                                                                                                                          | Any valid API key                      | :fontawesome-solid-circle-check:{ .green } |
| `language`            | [ISO 639-1 code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) for user language.                                                                                     | Two-letter ISO code, e.g. **`en`**     |  :fontawesome-solid-circle-xmark:{ .red }  |
| `region`              | [ISO 3166-1 code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) for user region.<br>Used with [TMDb Chart Builders](../files/builders/tmdb.md#tmdb-chart-builders).  | Two-letter code or leave **blank**     |  :fontawesome-solid-circle-xmark:{ .red }  |
| `cache_expiration`    | Number of days before each cache mapping expires and is re-cached.                                                                                                             | Integer, e.g. **`60`**                 |  :fontawesome-solid-circle-xmark:{ .red }  |

## Important Notes

It is important that you use a TMDb **V3** API key. If you do not already have one, follow the [TMDb Getting Started guide](https://developers.themoviedb.org/3/getting-started/introduction).

If you would like to validate your API key valid prior to running Kometa, visit the [TMDb Authentication page](https://developer.themoviedb.org/reference/authentication-validate-key), 
sign in with your TMDb credentials and press the "Try It!" button on the right-hand side. You should see `"success": true` in the Response box.