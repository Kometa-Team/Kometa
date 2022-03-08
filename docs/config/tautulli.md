# Tautulli Attributes

Configuring [Tautulli](https://tautulli.com/) is optional but can allow you to create Collections based on Tautulli's Watch Statistics.

A `tautulli` mapping can be either in the root of the config file as global mapping for all libraries, or you can specify the `tautulli` mapping individually per library.

Below is a `tautulli` mapping example and the full set of attributes:

```yaml
tautulli:
  url: http://192.168.1.12:8659
  apikey: ################################
```

| Attribute | Allowed Values                                        | Default | Required |
|:----------|:------------------------------------------------------|:-------:|:--------:|
| `url`     | Tautulli URL<br>**Example:** http://192.168.1.12:8659 |   N/A   | &#9989;  |
| `apikey`  | Tautulli API Key                                      |   N/A   | &#9989;  |

* The apikey can be found by going to Tautulli > Settings > Web Interface > API > API Key
