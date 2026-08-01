---
search:
  boost: 3
hide:
  - toc
---
# Trakt Attributes

Configuring [Trakt.tv](https://trakt.tv/) is optional but is required for Trakt based collections to function. 


???+ warning

    Using Trakt meaningfully with Kometa probably requires a Trakt VIP account, since Trakt has limited free accounts to having a single external application connected.  This means that if you connect Kometa to Trakt, you can't use Trakt with any other application like MDBList, and vice versa, if you connect Trakt to any other applicaiton, you can't connect it to Kometa.


The `trakt` attribute is found at the root of the config file.

Kometa uses Trakt's Device Code Flow. When authorization is required, it displays a complete activation URL. Open it in any browser and approve access; the short-lived code is already included in the URL.

Kometa automatically refreshes the stored credentials before they expire.

???+ warning

    Your config file needs to be writable by Kometa, since the `authorization` attribute gets updated when the credentials are renewed.

    If the config file is not writable, the Trakt renewal will eventually fail.


```yaml title="config.yml Trakt sample (do not use these credentials)"
trakt:
  client_id: 1a2b3c4d5e6f7g8h9i
  client_secret: 1a12b23c34d45e56f6
  force_refresh: false
  authorization:
    access_token: 4cc355t0k3nh3r3
    token_type: Bearer
    expires_in: 1928374655
    refresh_token: r3fr35ht0k3nh3r3
    scope: public 
    created_at: 137946258
```

| Attribute       | Description                       | Allowed Values (default in **bold**) |                  Required                  |
|:----------------|:----------------------------------|:-------------------------------------|:------------------------------------------:|
| `client_id`     | Trakt application client ID.      | Any valid ID or leave **blank**      | :fontawesome-solid-circle-check:{ .green } |
| `client_secret` | Trakt application client secret.  | Any valid secret or leave **blank**  | :fontawesome-solid-circle-check:{ .green } |
| `force_refresh` | Refresh credentials on every run, verifying that the app is still authorized. | 'true' or 'false'                    |  :fontawesome-solid-circle-xmark:{ .red }  |

*All other attributes will be filled in as part of the authentication process*

### Authenticating Trakt

To connect to Trakt.tv you must create a Trakt application:

1. [Click here to create a Trakt API application.](https://app.trakt.tv/settings/apps/api)
2. Click the "+" in the upper right.
3. Enter a `Name` for the application.
4. A redirect URI is not used by Device Code Flow; retain a valid URI required by the Trakt app form if applicable.
5. You can leave "Description" and "JavaScript (CORS) origins" blank.
6. Click the `Create` button.
7. Record the `Client ID` and `Client Secret`; you will need them later, and you only need do this process once..

Start Kometa and open the displayed Trakt activation URL. The browser can be on a different device from Kometa. Approve access and Kometa saves the generated `authorization` block automatically.

### Headless authentication

On a headless server, read the activation URL from the logs, or configure [`webhooks.trakt_pin`](webhooks.md#trakt-authorization-notifications) to send it to ntfy, Gotify, Apprise, Slack, Discord, or a direct webhook. The URL contains a short-lived code, so treat that notification as urgent.

```yaml
webhooks:
  trakt_pin: ntfy
```
