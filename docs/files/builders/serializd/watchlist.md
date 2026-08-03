---
search:
  boost: 2
---

# Serializd Watchlist

The `serializd_watchlist` builder finds every show in a Serializd watchlist using its JSON API.

Use `me` for the account authenticated in `config.yml`:

```yaml
collections:
  My Serializd Watchlist:
    serializd_watchlist: me
    collection_order: custom
    sync_mode: sync
```

Use a username or complete watchlist URL for another public user:

```yaml
collections:
  Someone Else's Watchlist:
    serializd_watchlist: somebodys_username
```

```yaml
collections:
  Noah's Serializd Watchlist:
    serializd_watchlist: https://www.serializd.com/user/somebodys_username/watchlist
```

