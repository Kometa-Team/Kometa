---
search:
  boost: 3
---
# Trakt Attributes

Configuring [Trakt.tv](https://trakt.tv/) is optional but is required for Trakt based collections to function. 

A `trakt` mapping is in the root of the config file.

Below is a `trakt` mapping example and the full set of attributes:
```yaml
trakt:
  client_id: ################################################################
  client_secret: ################################################################
  pin:
  authorization:
    access_token:
    token_type:
    expires_in:
    refresh_token:
    scope:
    created_at:
```

| Attribute       | Allowed Values                  | Default | Required |
|:----------------|:--------------------------------|:--------|:--------:|
| `client_id`     | Trakt Application Client ID     | N/A     | :fontawesome-solid-circle-check:{ .green }  |
| `client_secret` | Trakt Application Client Secret | N/A     | :fontawesome-solid-circle-check:{ .green }  |
| `pin`           | Trakt Pin                       | None    | :fontawesome-solid-circle-xmark:{ .red } |

* All other attributes will be filled in by Plex Meta Manager. 

* To connect to Trakt.tv you must create a Trakt application and supply Plex Meta Manager the `client_id`, `client_secret`, and `pin` provided, please do the following:
1. [Click here to create a Trakt API application.](https://trakt.tv/oauth/applications/new)
2. Enter a `Name` for the application.
3. Enter `urn:ietf:wg:oauth:2.0:oob` for `Redirect uri`.
4. Click the `SAVE APP` button.
5. Record the `Client ID` and `Client Secret` as `client_id` and `client_secret` in your Configuration File.
6. Click the Green Authorize Button next to the Redirect URI

    ![Trakt Authorize](trakt.png)
8. Record the `PIN` as `pin` in your Configuration File.

* Run Plex Meta Manager shortly after obtaining your PIN; the PIN may expire at some point.

## Online Authorization Script

Plex Meta Manager requires interactive mode to be able to enter the Client ID and Client Secret. Some systems (namely NAS) make this difficult to accomplish. Chazlarson has developed an online script that can be run to generate the MAL and Trakt authentication outside of Plex Meta Manager and then paste the end-result directly into the configuration file.

The Online Auth tool can be found [here](https://replit.com/@chazlarson/TraktAuth).

Simply press the play button, wait a little bit, and then follow the on-screen prompts.