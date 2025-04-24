---
hide:
  - toc
---
# Trakt UserList

Finds every movie/show in the Trakt UserList.

The `sync_mode: sync` and `collection_order: custom` Setting are recommended since the lists are continuously updated 
and in a specific order.

???+ warning "Trakt Configuration"

    [Configuring Trakt](../../../config/trakt.md) in the config is required for any of these builders.

| Attribute  | Description & Values                                                                                                                                                                                                                                                                                                                                                                   |
|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `userlist` | **Description:** Which Trakt userlist to query<br>**Values:**<table class="clearTable"><tr><td>`watchlist`</td><td>Trakt User's Watchlist</td></tr><tr><td>`favorites`</td><td>Trakt User's Personal Favorite list</td></tr><tr><td>`watched`</td><td>Trakt User's Personal Watched list</td></tr><tr><td>`collection`</td><td>Trakt User's Personal Collection list</td></tr></table> |
| `user`     | **Description:** The User who's user lists you want to query.<br>**Default:** `me`<br>**Values:** Username of User or `me` for the authenticated user.                                                                                                                                                                                                                                 |
| `sort_by`  | **Description:** How to sort the results<br>**Default:** `rank`<br>**Values:** `rank`, `added`, `released`, `title`                                                                                                                                                                                                                                                                    |

### Example Trakt UserList Builder(s)

```yaml
collections:
  Trakt Watchlist:
    trakt_userlist: 
      userlist: watchlist
      user: me
      sort_by: released
    collection_order: custom
    sync_mode: sync
```

You can use multiple charts in one Builder using a list.

```yaml
collections:
  Trakt Watchlist:
    trakt_userlist:
      - userlist: watched
        user: me
      - userlist: collection
        user: me
    collection_order: custom
    sync_mode: sync
```
