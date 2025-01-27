---
search:
  boost: 3
---
# Trakt Attributes

Configuring [Trakt.tv](https://trakt.tv/) is optional but is required for Trakt based collections to function. 

A `trakt` mapping is in the root of the config file, sampled below.

```yaml title="config.yml Trakt sample"
trakt:
  client_id: 1a2b3c4d5e6f7g8h9i
  client_secret: 1a12b23c34d45e56f6
  pin:
  authorization:
    access_token: 4cc355t0k3nh3r3
    token_type: Bearer
    expires_in: 1928374655
    refresh_token: r3fr35ht0k3nh3r3
    scope: public 
    created_at: 137946258
```

| Attribute       | Allowed Values                  | Default |                  Required                  |
|:----------------|:--------------------------------|:--------|:------------------------------------------:|
| `client_id`     | Trakt Application Client ID     | N/A     | :fontawesome-solid-circle-check:{ .green } |
| `client_secret` | Trakt Application Client Secret | N/A     | :fontawesome-solid-circle-check:{ .green } |
| `pin`           | Trakt Pin                       | None    |  :fontawesome-solid-circle-xmark:{ .red }  |

* All other attributes will be filled in by Kometa. 

To connect to Trakt.tv you must create a Trakt application and supply Kometa the `client_id`,
`client_secret`, and `pin` provided, please do the following:

1.  [Click here to create a Trakt API application.](https://trakt.tv/oauth/applications/new)
2.  Enter a `Name` for the application.
3.  Enter `urn:ietf:wg:oauth:2.0:oob` for `Redirect uri`.
4.  Click the `SAVE APP` button.
5.  Record the `Client ID` and `Client Secret` as `client_id` and `client_secret` in your Configuration File.
6.  Click the Green Authorize Button next to the Redirect URI

    ![Trakt Authorize](images/trakt.png)

7.  Record the `PIN` as `pin` in your Configuration File.

???+ warning

    Run Kometa shortly after obtaining your PIN; the PIN may expire at some point.

## Online Authorization

{%    
  include-markdown "./authentication.md"
  start="# Trakt and MyAnimeList Authentication"
%}