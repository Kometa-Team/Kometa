---
search:
  boost: 3
hide:
  - toc
---
# Trakt Attributes

Configuring [Trakt.tv](https://trakt.tv/) is optional but is required for Trakt based collections to function. 


???+ warning "Trakt authentication changes"

    Using Trakt meaningfully with Kometa probably requires a Trakt VIP account, since Trakt has limited free accounts to having a single external application connected.  This means that if you connect Kometa to Trakt, you can't use Trakt with any other application like MDBList, and vice versa, if you connect Trakt to any other applicaiton, you can't connect it to Kometa.

    Trakt now limits free accounts to one connected application. Free users who need authenticated Kometa features must assign Kometa as that connected app. Doing so can disconnect or prevent other services, such as MDBList, from using the same Trakt account. Trakt VIP users are largely unaffected and can use Kometa alongside their other connected services.


The `trakt` attribute is found at the root of the config file.

`client_id` may be omitted to use Kometa's bundled public API key, or set to your own application ID. `client_secret` may be omitted when Kometa is only using public endpoints.

If stored authentication credentials are present, Kometa will refresh them automatically on each run. 

Trakt credentials will automatically expire after 7 days, so we recommend you run Kometa at least once per week to automatically refresh the credentials.

If the access or refresh token is expired or invalid, Kometa cannot reauthenticate them itself, and you will need to reauthenticate using the [Kometa Utilities website](https://utilities.kometa.wiki).


| Requires OAuth | Kometa features                                                                                                                                            |
|:---------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| No             | Official lists; public lists; named-user public lists; public ratings and metadata; trending, popular, and box-office charts                               |
| Yes            | `me` lists; private lists; list changes; user ratings; `trakt_user_rating` overlays; collection, watchlist, and history for `me`; recommendations; liked lists; watched/collected charts |

???+ warning

    Your config file needs to be writable by Kometa, since the `authorization` attribute gets updated when the credentials are renewed.

    If the config file is not writable, the Trakt renewal will eventually fail.


```yaml title="config.yml Trakt sample (do not use these credentials)"
trakt:
  client_id: 1a2b3c4d5e6f7g8h9i
  client_secret: 1a12b23c34d45e56f6
  authorization:
    access_token: 4cc355t0k3nh3r3
    token_type: Bearer
    expires_in: 1928374655
    refresh_token: r3fr35ht0k3nh3r3
    scope: public 
    created_at: 137946258
```

| Attribute       | Description                       | Allowed Values (default in **bold**)                        |                  Required                  |
|:----------------|:----------------------------------|:------------------------------------------------------------|:------------------------------------------:|
| `client_id`     | Trakt application client ID.      | Any valid ID or leave **blank** to use the public Kometa ID | :fontawesome-solid-circle-check:{ .green } |
| `client_secret` | Trakt application client secret.  | Any valid secret or leave **blank**                         | :fontawesome-solid-circle-check:{ .green } |

*All other attributes will be filled in as part of the authentication process*

### Authenticating Trakt

To connect to Trakt.tv you must create a Trakt application:

1. [Click here to create a Trakt API application.](https://app.trakt.tv/settings/apps/api)
2. Click the "+" in the upper right.
3. Enter a `Name` for the application.
4. Retain a valid redirect URI required by the Trakt app form if applicable; Kometa Utilities handles the authentication flow.
5. You can leave "Description" and "JavaScript (CORS) origins" blank.
6. Click the `Create` button.
7. Record the `Client ID` and `Client Secret`; you will need them later, and you only need do this process once..

Use the [Kometa Utilities website](https://utilities.kometa.wiki) to authenticate Trakt and add the generated `authorization` block to your config. Kometa will attempt to refresh those credentials automatically on subsequent runs.
