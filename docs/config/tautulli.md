---
hide:
  - toc
---
# Tautulli Attributes

Configuring [Tautulli](https://tautulli.com/) is optional but can allow you to create Collections based on Tautulli's Watch Statistics.

A `tautulli` mapping can be either in the root of the config file as global mapping for all libraries, or you can specify the `tautulli` mapping individually per library.

Below is a `tautulli` mapping example and the full set of attributes:

```yaml title="config.yml Tautulli sample"
tautulli:
  url: http://192.168.1.12:8659
  apikey: ################################
```

| Attribute | Description               | Allowed Values (default in **bold**)                                    |                  Required                   |
|:----------|:--------------------------|:------------------------------------------------------------------------|:-------------------------------------------:|
| `url`     | Tautulli URL.             | Any valid URL<br><strong>Example:</strong> `http://192.168.1.12:8659`   | :fontawesome-solid-circle-check:{ .green }  |
| `apikey`  | Tautulli API key.         | Any valid key or leave **blank**                                        | :fontawesome-solid-circle-check:{ .green }  |

???+ tip
    
    The apikey can be found by going to Tautulli > Settings > Web Interface > API > API Key.

# Other examples

Specifying a second Tautulli instance for a specific library:

In this example we have a separate Tautulli instance for TV.

```yaml
libraries:
  Movies:
    collection_files:
      - file: config/Movies.yml
  TV Shows:
    collection_files:
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