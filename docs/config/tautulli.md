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
|:----------|:------------------------------------------------------|:--------|:--------:|
| `url`     | Tautulli URL<br>**Example:** http://192.168.1.12:8659 | N/A     | :fontawesome-solid-circle-check:{ .green }  |
| `apikey`  | Tautulli API Key                                      | N/A     | :fontawesome-solid-circle-check:{ .green }  |

???+ tip
    
    The apikey can be found by going to Tautulli > Settings > Web Interface > API > API Key

# Other examples

Specifying a second Tautulli instance for a specific library:

In this example we have a separate Tautulli instance for TV.

```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
  TV Shows:
    metadata_path:
      - file: config/TV.yml
    tautulli:
      url: http://192.168.1.14:8659
      apikey: SOME_KEY
...
tautulli:
  url: http://192.168.1.12:8659
  apikey: SOME_KEY
...
```