# OMDb Attributes

Configuring [OMDb](https://www.omdbapi.com/) is optional but can allow you to mass edit metadata using IMDb.

A `omdb` mapping is in the root of the config file.

Below is a `omdb` mapping example and the full set of attributes:
```yaml
omdb:
  apikey: ########
  cache_expiration: 60
```

| Attribute          | Allowed Values                                                             | Default |                  Required                  |
|:-------------------|:---------------------------------------------------------------------------|:--------|:------------------------------------------:|
| `apikey`           | OMDb API Key                                                               | N/A     | :fontawesome-solid-circle-check:{ .green } |
| `cache_expiration` | Number of days before each cache mapping expires and has to be re-cached.  | 60      |  :fontawesome-solid-circle-xmark:{ .red }  |

???+ tip

    The OMDb apikey can be generated [here](http://www.omdbapi.com/apikey.aspx).

    The free apikey is limited to 1000 requests per day so if you hit your limit the program should be able to pick up where it left off the next day as long as the `cache` [Setting](settings.md#cache) is enabled 
