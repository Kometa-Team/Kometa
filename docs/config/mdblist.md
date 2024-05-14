# MDBList Attributes

Configuring [MDBList](https://mdblist.com/) is optional but can allow you to mass edit metadata.

A `mdblist` mapping is in the root of the config file.

Below is a `mdblist` mapping example and the full set of attributes:
```yaml
mdblist:
  apikey: #########################
  cache_expiration: 60
```

| Attribute          | Allowed Values                                                            | Default |                  Required                  |
|:-------------------|:--------------------------------------------------------------------------|:--------|:------------------------------------------:|
| `apikey`           | MDBList API Key                                                           | N/A     | :fontawesome-solid-circle-check:{ .green } |
| `cache_expiration` | Number of days before each cache mapping expires and has to be re-cached. | 60      |  :fontawesome-solid-circle-xmark:{ .red }  |

???+ tip

    The MDBList apikey can be found [here](https://mdblist.com/preferences/).

    The free apikey is limited to 1000 requests per day so if you hit your limit the program should be able to pick up 
    where it left off the next day as long as the `cache` [Setting](settings.md#cache) is enabled.
