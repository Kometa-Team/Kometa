---
search:
  boost: 3
---
# Plex Attributes

Configuring [Plex](https://www.plex.tv/) is required in order to connect to your libraries.

A `plex` mapping can be either in the root of the config file as global mapping for all libraries, or you can specify 
the `plex` mapping individually per library.

Below is a `plex` mapping example and the full set of attributes:

```yaml
plex:
  url: http://192.168.1.12:32400
  token: ####################
  timeout: 60
  db_cache: 4096
  clean_bundles: true
  empty_trash: true
  optimize: false
  verify_ssl:
```

| Attribute       | Allowed Values                                                                                                                 | Default |                  Required                  |
|:----------------|:-------------------------------------------------------------------------------------------------------------------------------|:--------|:------------------------------------------:|
| `url`           | Plex Server URL<br><strong>Example:</strong> http://192.168.1.12:32400                                                         | N/A     | :fontawesome-solid-circle-check:{ .green } |
| `token`         | Plex Server Authentication Token                                                                                               | N/A     | :fontawesome-solid-circle-check:{ .green } |
| `timeout`       | Plex Server Timeout [in seconds]                                                                                               | 60      |  :fontawesome-solid-circle-xmark:{ .red }  |
| `db_cache`      | Plex Server Database Cache Size [in MB, Plex defaults to 40]                                                                   | None    |  :fontawesome-solid-circle-xmark:{ .red }  |
| `clean_bundles` | Runs Clean Bundles on the Server after all Collection Files are run<br>(`true`, `false` or Any [schedule option](schedule.md)) | false   |  :fontawesome-solid-circle-xmark:{ .red }  |
| `empty_trash`   | Runs Empty Trash on the Server after all Collection Files are run<br>(`true`, `false` or Any [schedule option](schedule.md))   | false   |  :fontawesome-solid-circle-xmark:{ .red }  |
| `optimize`      | Runs Optimize on the Server after all Collection Files are run<br>(`true`, `false` or Any [schedule option](schedule.md))      | false   |  :fontawesome-solid-circle-xmark:{ .red }  |
| `verify_ssl`    | Turns SSL verification on/off for only Plex                                                                                    | None    |  :fontawesome-solid-circle-xmark:{ .red }  |

???+ warning
    
    Do Not Use the Plex Token found in Plex's Preferences.xml file.

    If you need help finding your Plex authentication token, please see Plex's 
    [support article](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

This script can be run on a remote Plex server, but be sure that the `url` provided is publicly addressable, and it's 
recommended to use `HTTPS`.


# Multi-Plex Instance Setup:

The below config.yml extract details how to set up multiple Plex servers within the one Kometa instance, in this example 
there are two plex servers which are receiving the same Collection File:

```yaml
libraries:
  Movies:
    collection_files:
      - file: config/Movies.yml
  Movies_on_Second_Plex:
    library_name: Movies
    collection_files:
      - file: config/Movies.yml
    plex:
      url: http://plex.boing.bong
      token: SOME_TOKEN
      timeout: 360
      db_cache: 8192
...
plex:
  url: http://plex.bing.bang
  token: SOME_TOKEN
  timeout: 60
  db_cache: 4096
  clean_bundles: false
  empty_trash: false
  optimize: false
...
```

The `plex` instance at the bottom is the "global" plex server. Unless otherwise specified, any connection to plex is 
assumed to be using that plex server. The first "Movies" library entry is on the global `plex` server.

The "Movies_on_Second_Plex" library is found on the second plex server. Note that this library has its own plex section 
that lists the attributes that differ from the global plex instance, namely the `URL`, `token` and `timeout`. The 
library on the second server is also called "Movies", but since you can't have two keys (in this scenario, libraries) 
with the same name, it is named Movies_on_Second_Plex in the config.yml, and the `library_name:` attribute contains the 
name of the library on the actual plex server.


