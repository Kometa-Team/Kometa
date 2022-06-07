# Plex Attributes

Configuring [Plex](https://www.plex.tv/) is required in order to connect to your libraries.

A `plex` mapping can be either in the root of the config file as global mapping for all libraries, or you can specify the `plex` mapping individually per library.

Below is a `plex` mapping example and the full set of attributes:
```yaml
plex:
  url: http://192.168.1.12:32400
  token: ####################
  timeout: 60
  clean_bundles: true
  empty_trash: true
  optimize: false
```

| Attribute       | Allowed Values                                                         | Default | Required |
|:----------------|:-----------------------------------------------------------------------|:-------:|:--------:|
| `url`           | Plex Server URL<br><strong>Example:</strong> http://192.168.1.12:32400 |   N/A   | &#9989;  |
| `token`         | Plex Server Authentication Token                                       |   N/A   | &#9989;  |
| `timeout`       | Plex Server Timeout                                                    |   60    | &#10060; |
| `clean_bundles` | Runs Clean Bundles on the Server after all Metadata Files are run      |  false  | &#10060; |
| `empty_trash`   | Runs Empty Trash on the Server after all Metadata Files are run        |  false  | &#10060; |
| `optimize`      | Runs Optimize on the Server after all Metadata Files are run           |  false  | &#10060; |

* **Do Not Use the Plex Token found in Plex's Preferences.xml file**

* This script can be run on a remote Plex server, but be sure that the `url` provided is publicly addressable, and it's recommended to use `HTTPS`.

* If you need help finding your Plex authentication token, please see Plex's [support article](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

# Other examples:

Specifying a second Plex server for a specific library:

In this example we have two Plex servers [with the same libraries] and want to add the same collections to each.  The second Plex is less responsive, so it needs a higher timeout than the primary one.

```yaml
libraries:
  Movies:
    metadata_path:
      - file: config/Movies.yml
  Movies_on_Second_Plex:
    library_name: Movies
    metadata_path:
      - file: config/Movies.yml
    plex:
      url: http://plex.boing.bong
      token: SOME_TOKEN
      timeout: 360
...
plex:
  url: http://plex.bing.bang
  token: SOME_TOKEN
  timeout: 60
  clean_bundles: false
  empty_trash: false
  optimize: false
...
```
