# TMDb Attributes

Configuring [TheMovieDb](https://www.themoviedb.org/) is required in order to run the script. 

A `tmdb` mapping is in the root of the config file.

Below is a `tmdb` mapping example and the full set of attributes:
```yaml
tmdb:
  apikey: ################################
  language: en
```

| Attribute          | Allowed Values                                                                                            | Default | Required |
|:-------------------|:----------------------------------------------------------------------------------------------------------|:-------:|:--------:|
| `apikey`           | User TMDb V3 API Key                                                                                      |   N/A   | &#9989;  |
| `language`         | [ISO 639-1 Code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) of the User Language              |   en    | &#10060; |
| `region`           | [ISO 3166-1 Code](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) of the User Region for Searches |  None   | &#10060; |
| `cache_expiration` | Number of days before each cache mapping expires and has to be re-cached.                                 |   60    | &#10060; |

If you do not have a TMDb V3 API key please refer to this [guide](https://developers.themoviedb.org/3/getting-started/introduction).
