---
search:
  boost: 3
---
# TMDb Attributes

Filling in your [TheMovieDb](https://www.themoviedb.org/) API key is mandatory in order to run Kometa. 

A `tmdb` mapping is in the root of the config file.

Below is a `tmdb` mapping example and the full set of attributes:
```yaml
tmdb:
  apikey: ################################
  language: en
  region: US
  cache_expiration: 60
```

| Attribute          | Allowed Values                                                                                                                                                                    | Default |                  Required                  |
|:-------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------|:------------------------------------------:|
| `apikey`           | User TMDb V3 API Key                                                                                                                                                              | N/A     | :fontawesome-solid-circle-check:{ .green } |
| `language`         | [ISO 639-1 Code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) of the User Language                                                                                      | en      |  :fontawesome-solid-circle-xmark:{ .red }  |
| `region`           | [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) of the User Region for use with [Other TMDb Builders](../files/builders/tmdb.md#other-tmdb-builders)    | None    |  :fontawesome-solid-circle-xmark:{ .red }  |
| `cache_expiration` | Number of days before each cache mapping expires and has to be re-cached.                                                                                                         | 60      |  :fontawesome-solid-circle-xmark:{ .red }  |

## Important Notes

It is important that you use a TMDb **V3** API key. If you do not already have one, follow the [TMDb Getting Started guide](https://developers.themoviedb.org/3/getting-started/introduction)

If you would like to validate your API key valid prior to running Kometa, visit the [TMDb Authentication page](https://developer.themoviedb.org/reference/authentication-validate-key), sign in with your TMDb credentials and press the "Try It!" button on the right-hand side. You should see `"success": true` in the Response box.