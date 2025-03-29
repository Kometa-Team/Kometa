---
hide:
  - toc
---
# OMDb Attributes

Configuring [OMDb](https://www.omdbapi.com/) is optional but can allow you to mass edit metadata using IMDb.

A `omdb` mapping is in the root of the config file sampled below.

```yaml title="config.yml OMDb sample"
omdb:
  apikey: 1a2b3c4d
  cache_expiration: 60
```

| Attribute          | Description                                                             | Allowed Values (default in **bold**)          |                   Required                   |
|:-------------------|:------------------------------------------------------------------------|:----------------------------------------------|:--------------------------------------------:|
| `apikey`           | OMDb API key.                                                           | Any valid key or leave **blank**              |  :fontawesome-solid-circle-check:{ .green }  |
| `cache_expiration` | Days before each cache mapping expires and must be re-cached.           | Integer, e.g. **`60`**                        | :fontawesome-solid-circle-xmark:{ .red }     |

???+ tip

    The OMDb apikey can be generated [here](http://www.omdbapi.com/apikey.aspx).

    The free apikey is limited to 1000 requests per day so if you hit your limit the program should be able to pick up 
    where it left off the next day as long as the `cache` [Setting](settings.md#cache) is enabled. 
