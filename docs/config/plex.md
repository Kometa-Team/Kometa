---
search:
  boost: 3
hide:
  - toc
---
# Plex Attributes

Filling in your [Plex](https://www.plex.tv/) URL and Token is mandatory as Kometa cannot run without access to a Plex Media Server.

A `plex` mapping can be either in the root of the config file as global mapping for all libraries, or you can specify the `plex` mapping individually per library.

```yaml title="config.yml Plex sample"
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

<div class="annotate" markdown>

| Attribute          | Description                                                                                                                               | Allowed Values (default in **bold**)                                      |                   Required                   |
|:-------------------|:------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------|:--------------------------------------------:|
| `url`              | Plex server URL.                                                                                                                          | Any valid URL(1)<br><strong>Example:</strong> `http://192.168.1.12:32400` |  :fontawesome-solid-circle-check:{ .green }  |
| `token`            | Plex server authentication token                                                                                                          | Any valid token(2)                                                        |  :fontawesome-solid-circle-check:{ .green }  |
| `timeout`          | Timeout value for Plex server communication (in seconds)                                                                                  | Integer, e.g. **`60`**                                                    |   :fontawesome-solid-circle-xmark:{ .red }   |
| `db_cache`         | Plex database cache size (in MB). Plex defaults to 40                                                                                     | Integer, e.g. **`40`**                                                    |   :fontawesome-solid-circle-xmark:{ .red }   |
| `clean_bundles`    | Run [Clean Bundles](https://support.plex.tv/articles/226836308-help/) after all collection files have been processed.                     | `true`, **`false`**, or any [schedule option](schedule.md)                |   :fontawesome-solid-circle-xmark:{ .red }   |
| `empty_trash`      | Run [Empty Trash](https://support.plex.tv/articles/200289326-emptying-library-trash/) after all collection files have been processed.     | `true`, **`false`**, or any [schedule option](schedule.md)                |   :fontawesome-solid-circle-xmark:{ .red }   |
| `optimize`         | Run [Optimize Database](https://support.plex.tv/articles/226836308-help/) after all collection files have been processed.                 | `true`, **`false`**, or any [schedule option](schedule.md)                | :fontawesome-solid-circle-xmark:{ .red }     | 
| `verify_ssl`       | Enable or disable SSL verification for Plex only                                                                                          | `true`, **`false`**, or leave **blank**                                   |   :fontawesome-solid-circle-xmark:{ .red }   |

</div>

1.  You cannot use `https://app.plex.tv` as your `url` as that is invalid, you **must** provide the direct address you use to access your server.  There have been instances of issues when Kometa tries to communicate with Plex via a Proxy, so we suggest that Kometa is given direct, unfettered access to Plex to avoid any middle-man issues.
2.  If you need help finding your Plex Authentication Token, please see Plex's [support article](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/). **Do not** use the Plex Token found in Plex's Preferences.xml file and **do not** use the token that you get via https://app.plex.tv.

If you set `optimize: true`, you may find that Plex becomes temporarily unresponsive after Kometa has finished running,  this is normal and expected behaviour which is reproducible if you run Optimize Database within the Plex UI.

# Multi-Plex Instance Setup:

The below config.yml extract details how to set up multiple Plex servers within the one Kometa instance, in this example there are two plex servers which are receiving the same Collection File:

```yaml title="config.yml multi-Plex instances"
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

The "Movies_on_Second_Plex" library is found on the second plex server. Note that this library has its own plex section that lists the attributes that differ from the global plex instance, 
namely the `URL`, `token` and `timeout`. The library on the second server is also called "Movies", but since you can't have two keys (in this scenario, libraries) with the same name, 
it is named Movies_on_Second_Plex in the config.yml, and the `library_name:` attribute contains the name of the library on the actual plex server.


