# Metadata and Playlist Files

Metadata and Playlist files are used to create and maintain collections within the Plex libraries and playlists on the server.

If utilized to their fullest, these files can be used to maintain the entire server's collections and playlists, and can be used as a backup for these in the event of a restore requirement.

## Metadata Files

Collections, templates, metadata, and dynamic collections are defined within one or more Metadata files, which are linked to libraries in the [Libraries Attribute](../config/libraries) within the [Configuration File](../config/configuration.md).

These are the attributes which can be used within the Metadata File:

| Attribute                                               | Description                                                                                                                                                                       |
|:--------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `metadata`                                              | contains definitions of metadata changes to [movie](metadata/movie), [show](metadata/show), or [music](metadata/music) library's items [movie titles, episode descriptions, etc.] |
| [`templates`](templates)                                | contains definitions of templates that can be leveraged by multiple collections                                                                                                   |
| [`external_templates`](templates.md#external-templates) | contains [path types](../config/paths) that point to external templates that can be leveraged by multiple collections                                                             |
| [`collections`](#collections-and-playlists-mappings)    | contains definitions of collections you wish to add to one or more libraries                                                                                                      |
| [`dynamic_collections`](dynamic)                        | contains definitions of dynamic collections you wish to create in one or more libraries                                                                                           |

* One of `metadata`, `collections` or `dynamic_collections` must be present for the Metadata File to execute.
* Example Metadata Files can be found in the [Plex Meta Manager Configs Repository](https://github.com/meisnate12/Plex-Meta-Manager-Configs)

## Playlist Files

Playlists are defined in one or more Playlist files that are mapped in the [Playlist Files Attribute](../config/playlist) within the Configuration File.

There are two attributes which can be utilized within the Playlist File:

| Attribute                                               | Description                                                                                                         |
|:--------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|
| [`templates`](templates)                                | contains definitions of templates that can be leveraged by multiple playlists                                       |
| [`external_templates`](templates.md#external-templates) | contains [path types](../config/paths) that point to external templates that can be leveraged by multiple playlists |
| [`playlists`](#additional-playlist-attributes)          | contains definitions of playlists you wish to add to the server                                                     |

* `playlists` is required in order to run the Playlist File.
* You can find example Playlist Files in the [Plex Meta Manager Configs Repository](https://github.com/meisnate12/Plex-Meta-Manager-Configs)
* Plex does not support the "Continue Watching" feature for playlists, you can [vote for the feature here](https://forums.plex.tv/t/playlists-remember-position-for-subsequent-resume/84866/39)

## Collections and Playlists Mappings

Plex Meta Manager can run a number of different operations within `collections:` and `playlists:` such as:

* Automatically build and update collections and playlists
* Sync the collection with the source list if one is used
* Send missing media to Sonarr/Radarr (Lidarr not supported at this time)
* Show and Hide collections and playlists at set intervals (i.e. show Christmas collections in December only)


## Dynamic Collection Mappings

Plex Meta Manager can automatically create dynamic collections based on different criteria, such as

* Collections for the top `X` popular people on TMDb (Bruce Willis, Tom Hanks etc.)
* Collections for each decade represented in the library (Best of 1990s, Best of 2000s etc.)
* Collections for each of the moods/styles within a Music library (A Cappella, Pop Rock etc.)

Below is an example dynamic collection which will create a collection for each of the decades represented within the library:

```yaml
dynamic_collections:
  Decades:
    type: decade
```

## Collection and Playlist Attributes

There are three types of attributes that can be utilized within a collection/playlist:

### Builders

Builders use third-party services to source items to be added to the collection/playlist. Multiple builders can be used in the same collection/playlist from a variety of sources listed below.

* [Plex Builders](builders/plex)
* [Smart Builders](builders/smart)
* [TMDb Builders](builders/tmdb)
* [TVDb Builders](builders/tvdb)
* [IMDb Builders](builders/imdb)
* [Trakt Builders](builders/trakt)
* [Tautulli Builders](builders/tautulli)
* [Letterboxd Builders](builders/letterboxd)
* [ICheckMovies Builders](builders/icheckmovies)
* [FlixPatrol Builders](builders/flixpatrol)
* [StevenLu Builders](builders/stevenlu)
* [AniDB Builders](builders/anidb)
* [AniList Builders](builders/anilist)
* [MyAnimeList Builders](builders/myanimelist)

## Details

These can alter any aspect of the collection/playlist or the media items within them.

* [Setting Details](details/setting)
* [Schedule Detail](details/schedule)
* [Image Overlay Detail](details/overlay)
* [Metadata Details](details/metadata)
* [Arr Details](details/arr)

## Filters

These filter media items added to the collection by any of the Builders.

* [Filters](filters)

## Additional Playlist Attributes

Playlist operations requires the `libraries` attribute, which instructs the operation to look in the specified libraries. This allows media to be combined from multiple libraries into one playlist. The mappings that you define in the `libraries` attribute must match the library names in your [Configuration File](../config/configuration).

The playlist can also use the `sync_to_users` attributes to control who has visibility of the playlist. This will override the global [`playlist_sync_to_users` Setting](../config/settings.md#playlist-sync-to-users). `sync_to_users` can be set to `all` to sync to all users who have access to the Plex Media Server, or a list/comma-separated string of users. The Plex Media Server owner will always have visibility of the Playlists, so does not need to be defined within the attribute. Leaving `sync_to_users` empty will make the playlist visible to the Plex Media Server owner only.

In the following example, media is pulled from the `Movies` and `TV Shows` libraries into the one Playlist, and the playlist is shared with a specific set of users:

```yaml
playlists:
  Marvel Cinematic Universe:
    sync_mode: sync
    libraries: Movies, TV Shows
    sync_to_users: User1, someone@somewhere.com, User3
    trakt_list: https://trakt.tv/users/donxy/lists/marvel-cinematic-universe?sort=rank,asc
    summary: Marvel Cinematic Universe In Chronological Order
```
* Unlike collections, playlists can only be built using one Builder as their ordering is inherited from the builder; it is not possible to combine builders.