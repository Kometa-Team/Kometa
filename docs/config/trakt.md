# Trakt Attributes

Configuring [Trakt.tv](https://trakt.tv/) is optional but is required for Trakt based collections to function. 

A `trakt` mapping is in the root of the config file.

Below is a `trakt` mapping example and the full set of attributes:
```yaml
trakt:
  client_id: ################################################################
  client_secret: ################################################################
  authorization:
    access_token:
    token_type:
    expires_in:
    refresh_token:
    scope:
    created_at:
```

| Attribute       | Allowed Values                  | Default | Required |
|:----------------|:--------------------------------|:-------:|:--------:|
| `client_id`     | Trakt Application Client ID     |   N/A   | &#9989;  |
| `client_secret` | Trakt Application Client Secret |   N/A   | &#9989;  |

* All other attributes will be filled in by the script. 

* To connect to Trakt.tv you must create a Trakt application and supply the script the `client id` and `client secret` provided, please do the following:
1. [Click here to create a Trakt API application.](https://trakt.tv/oauth/applications/new)
2. Enter a `Name` for the application.
3. Enter `urn:ietf:wg:oauth:2.0:oob` for `Redirect uri`.
4. Click the `SAVE APP` button.
5. Record the `Client ID` and `Client Secret`.

* On the first run, the script will walk the user through the OAuth flow by producing a Trakt URL for the user to follow. Once authenticated at the Trakt URL, the user needs to return the code to the script. If the code is correct, the script will populate the `authorization` sub-attributes to use in subsequent runs.

<h4>OAuth Flow using Docker</h4>

To authenticate Trakt the first time, you need run the container with the `-it` flags in order to walk through the OAuth flow mentioned above. Once you have the Trakt authentication data saved into the YAML, you'll be able to run the container normally.

<h4>OAuth Flow using unRAID Docker</h4>

Directions on how to authenticate Trakt on unRAID can be found on the [unRAID Walkthrough](../home/guides/unraid.md#advanced-installation-authenticating-trakt-or-myanimelist) page.
