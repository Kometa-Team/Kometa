---
hide:
  - toc
---
# MDBList Attributes

Configuring [MDBList](https://mdblist.com/) is optional but can allow you to mass edit metadata.

A `mdblist` mapping is in the root of the config file, sampled below.

```yaml title="config.yml MDBList sample"
mdblist:
  apikey: thisismyapikey
  cache_expiration: 60
```

| Attribute          | Description                                                                  | Allowed Values (default in **bold**)            | Required                                   |
|:-------------------|:-----------------------------------------------------------------------------|:------------------------------------------------|:------------------------------------------:|
| `apikey`           | MDBList API key.                                                             | Any valid key or leave **blank**                | :fontawesome-solid-circle-check:{ .green } |
| `cache_expiration` | Days before each cache mapping expires and must be re-cached.                | Integer, e.g. **`60`**                          | :fontawesome-solid-circle-xmark:{ .red }   |

???+ tip

    The MDBList apikey can be found [here](https://mdblist.com/preferences/).

    The free apikey is limited to 1000 requests per day so if you hit your limit the program should be able to pick up 
    where it left off the next day as long as the `cache` [Setting](settings.md#cache) is enabled.
