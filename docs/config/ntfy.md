---
hide:
  - toc
---
# ntfy Attributes

Configuring [ntfy](https://ntfy.sh/) is optional but can allow you to send the [webhooks](webhooks.md) straight to ntfy.

A `ntfy` mapping is in the root of the config file, sampled below.

```yaml title="config.yml ntfy sample"
ntfy:
  url: https://ntfy.sh  # or a different ntfy server URL
  token: tk_thisismyaccesstoken
  topic: kometa  # or a different topic name
```

| Attribute | Description               | Allowed Values (default in **bold**)        | Required                                   |
|:----------|:---------------------------|:--------------------------------------------|:------------------------------------------:|
| `url`     | ntfy server URL.           | Any valid URL or leave **blank**            | :fontawesome-solid-circle-check:{ .green } |
| `token`   | ntfy user access token.    | Any valid token or leave **blank**          | :fontawesome-solid-circle-check:{ .green } |
| `topic`   | ntfy topic name.           | Any valid topic or leave **blank**          | :fontawesome-solid-circle-check:{ .green } |

## Setup

Users can either use the [public ntfy server](https://ntfy.sh), or [host their own ntfy server](https://docs.ntfy.sh/install/).

### Retrieving Access Token and Topic

#### Using the Public Server

1. Visit https://ntfy.sh/login and login or sign up for an account (it's free).
2. Select "[Account](https://ntfy.sh/account)" from the side menu and scroll to "Access Tokens" to generate an access token.
3. Copy the access token and paste it into the `token` attribute in your config file. Enter `https://ntfy.sh` into the `url` attribute.
4. Click "Subscribe to topic" from the side menu and enter a topic name.
   - Pro subscribers can reserve specific topics, but any free tier user can subscribe and publish to any non-reserved topic.
   - Common topics such as `kometa` are likely already reserved or at least used by other public ntfy users (and these topics 
     may be visible to the general public). It's recommended to use a random topic name to keep your notifications semi-private.
5. Enter the topic name into the `topic` attribute in the config file.


#### Using a Self-Hosted Server

If you are a standard (non-admin) user of a [ntfy server other than the official one](https://docs.ntfy.sh/integrations/#alternative-ntfy-servers), 
you can follow the same steps as above, but with the server URL and token provided by the server.

If you are an admin of your own ntfy server, you can follow these steps:

1. Follow the [installation instructions](https://docs.ntfy.sh/install/) to set up your own ntfy server. 
2. Follow the same steps above for creating an account and access token, or use the `ntfy` command line tool to 
   [create a user](https://docs.ntfy.sh/config/#users-and-roles)and [generate an access token](https://docs.ntfy.sh/config/#access-tokens).
4. Follow the same steps as above for generating/reserving a topic, but with the server URL and token provided by your server.

Use the URL, topic and token to configure `ntfy` in the root of the config file.

Once you have added the configuration data to your `config.yml`, you can add `ntfy` to any [webhook](webhooks.md) to send that notification to ntfy.

```yaml title="config.yml ntfy webhooks sample"
webhooks:
  error: ntfy
  version: ntfy
  run_start: ntfy
  run_end: ntfy
  changes: ntfy
```
