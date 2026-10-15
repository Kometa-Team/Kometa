# Last.fm Attributes

Kometa uses [pyLast](https://github.com/pylast/pylast) to read Last.fm data for music collection builders. Create an [API key](https://www.last.fm/api/account/create) and add it to your configuration file:

```yaml title="config.yml"
lastfm:
  apikey: YOUR_LASTFM_API_KEY
```

| Attribute | Description |
| --- | --- |
| `apikey` | Your Last.fm API key. A secret and account login are not needed for the read-only builder. |
