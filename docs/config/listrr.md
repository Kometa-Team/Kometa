---
hide:
  - toc
---
# Listrr

Configuring [Listrr](https://listrr.pro/) is optional. `listrr_list` and `listrr_list_details` do nothing until this connection succeeds.

The `listrr` attribute is at the root of the config file.

```yaml
listrr:
  api_key: your_api_key
```

| Attribute | Description | Required |
|:----------|:------------|:------------------------------------------:|
| `api_key` | Listrr API key | :fontawesome-solid-circle-check:{ .green } |

## Getting an API key

Open the username menu on [listrr.pro](https://listrr.pro/) and copy the API key from your account profile. A blank key is ignored, and the builders stay disabled.

Listrr's website can show a list without asking you to log in. The API still requires this key, including for a list that is public on the website.

## Authorization header

Kometa sends the key as `Authorization: APIKEY <key>`. That is the scheme named by the live service when a request has no key. The published API description instead names a header called `X-API-KEY`. Kometa follows the live challenge.

A rejected key is an HTTP `401`, or an HTTP `302` redirect to the Listrr login page. Kometa logs `Listrr Connection Failed` and leaves the builders disabled.
