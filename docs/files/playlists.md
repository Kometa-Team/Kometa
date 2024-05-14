# Playlist Files

Playlist files are used to create and maintain playlists on the Plex Server.

If utilized to their fullest, these files can be used to maintain the entire server's collections and playlists, and can 
be used as a backup for these in the event of a restore requirement.

???+ tip

    Playlists are defined in one or more Playlist files that are mapped in the 
    [Playlist Files Attribute](../config/playlists.md) within the Configuration File.

You can use the [`playlist_report` setting](../config/settings.md#playlist-report) to get a list of your playlists 
printed out in your log. 

## Example

This example is a Playlist file with a basic overlay which is saved in a file called `MyPlaylists.yml` within the 
location mapped as `config` in my setup.


???+ example "Example "MyPlaylists.yml""

    Click the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml
    playlists: #(1)!
      Marvel Cinematic Universe Chronological Order:
        sync_mode: sync
        libraries: Movies, TV Shows  #(2)!
        sync_to_users: User1, someone@somewhere.com, User3  #(3)!
        trakt_list: https://trakt.tv/users/donxy/lists/marvel-cinematic-universe
        summary: Marvel Cinematic Universe In Chronological Order
    ```

    1.  This must appear once and **only once** in any Playlist file
    2.  These libraries must exist in your Plex library
    3.  Leave this blank if you only only want the Playlist to sync to the server owner's account

This file would then be defined in my `config.yml` file as a `playlist_files` item:

???+ warning "Important Note"

    Playlist files are not called within the `libraries` section, they are defined at the root identation as you can see 
    in the below example.

???+ example "config.yml Example Playlists Addition"

    Click the :fontawesome-solid-circle-plus: icon to learn more

    ```yaml
    libraries:
      Movies:
        # Metadata and Overlay files here
      TV Shows:
        # Metadata and Overlay files here
    playlist_files: #(1)!
      - file: config/MyPlaylists.yml #(2)!
    ```

    1.  Note that Playlist files are not called within the `libraries` section, they are defined at the root identation 
    as you can see here
    2.  `config` refers to the location that you mapped to `config` when following the Kometa Installation Guides.

## Playlist Attributes

Kometa can automatically build and update playlists defined within the `playlists` attribute.

These are the attributes which can be utilized within the Playlist File:

| Attribute                                               | Description                                                                                                             |
|:--------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|
| [`templates`](templates.md)                             | contains definitions of templates that can be leveraged by multiple playlists                                           |
| [`external_templates`](templates.md#external-templates) | contains [file blocks](../config/files.md) that point to external templates that can be leveraged by multiple playlists |
| [`playlists`](#playlist-attributes)                     | contains definitions of playlists you wish to add to the server                                                         |

* `playlists` is required in order to run the Playlist File.
* You can find example Playlist Files in the 
[Kometa Community Configs Repository](https://github.com/Kometa-Team/Community-Configs)
* Plex does not support the "Continue Watching" feature for playlists, you can
[vote for the feature here](https://forums.plex.tv/t/playlists-remember-position-for-subsequent-resume/84866/39)


Each playlist requires its own section within the `playlists` attribute and unlike collections, playlists can only be 
built using one Builder as their ordering is inherited from the builder; it is not possible to combine builders.

```yaml
playlists:
  Marvel Cinematic Universe Chronological Order:
    # ... builder, details, and filters for this playlist
  Star Wars Clone Wars Chronological Order:
    # ... builder, details, and filters for this playlist
  etc:
    # ... builder, details, and filters for this playlist
```

There are multiple types of attributes that can be utilized within a playlist:

* [Builders](builders/overview.md)
* [Filters](filters.md)
* [Settings](settings.md)
* [Radarr/Sonarr Settings](settings.md)
* [Collection/Playlist Metadata Updates](updates.md)
* [Item Metadata Updates](item_updates.md)

### Special Playlist Attributes

| Attribute         | Description                                                                                                                                                                                                                                                                                                       |                  Required                  |
|:------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|
| `libraries`       | Determine which libraries the playlist will be built from.<br>**Options:** Comma-separated string or list of library mapping names defined in the `libraries` attribute in the base of your [Configuration File](../config/overview.md).                                                                          | :fontawesome-solid-circle-check:{ .green } |
| `sync_to_users`   | Determine which Users have the playlist synced.<br>This will override the global [`playlist_sync_to_users` Setting](../config/settings.md).<br>**Options:** Comma-separated string or list of users, `all` for every user who has server access, or leave blank for just the server owner.                        |  :fontawesome-solid-circle-xmark:{ .red }  |
| `exclude_users`   | Determine which Users will be excluded from having the playlist synced.<br>This will override the global [`playlist_excude_users` Setting](../config/settings.md).<br>**Options:** Comma-separated string or list of users, `all` for every user who has server access, or leave blank for just the server owner. |  :fontawesome-solid-circle-xmark:{ .red }  |
| `delete_playlist` | Will delete this playlist for the users defined by sync_to_users.<br>**Options:** `true` or `false`                                                                                                                                                                                                               |  :fontawesome-solid-circle-xmark:{ .red }  |

* Any defined playlist will be always be visible by The Plex Media Server owner, so it doesn't need to be defined within `sync_to_users`.

## Example Playlists

In the following example, media is pulled from the `Movies` and `TV Shows` libraries into the one Playlist, and the 
playlist is shared with a specific set of users:

```yaml
playlists:
  Marvel Cinematic Universe Chronological Order:
    sync_mode: sync
    libraries: Movies, TV Shows
    sync_to_users: User1, someone@somewhere.com, User3
    trakt_list: https://trakt.tv/users/donxy/lists/marvel-cinematic-universe?sort=rank,asc
    summary: Marvel Cinematic Universe In Chronological Order
  Star Wars Clone Wars Chronological Order:
    sync_to_users: all
    sync_mode: sync
    libraries: Movies, TV Shows
    trakt_list: https://trakt.tv/users/tomfin46/lists/star-wars-the-clone-wars-chronological-episode-order
``` 
