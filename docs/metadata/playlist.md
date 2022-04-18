# Playlist Files

Playlist files are used to create and maintain playlists on the Plex Server.

If utilized to their fullest, these files can be used to maintain the entire server's collections and playlists, and can be used as a backup for these in the event of a restore requirement.

Playlists are defined in one or more Playlist files that are mapped in the [Playlist Files Attribute](../config/libraries.md#playlist-files-attribute) within the Configuration File.

These are the attributes which can be utilized within the Playlist File:

| Attribute                                               | Description                                                                                                         |
|:--------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|
| [`templates`](templates)                                | contains definitions of templates that can be leveraged by multiple playlists                                       |
| [`external_templates`](templates.md#external-templates) | contains [path types](../config/paths) that point to external templates that can be leveraged by multiple playlists |
| [`playlists`](#playlist-attributes)                     | contains definitions of playlists you wish to add to the server                                                     |

* `playlists` is required in order to run the Playlist File.
* You can find example Playlist Files in the [Plex Meta Manager Configs Repository](https://github.com/meisnate12/Plex-Meta-Manager-Configs/tree/master/PMM)
* Plex does not support the "Continue Watching" feature for playlists, you can [vote for the feature here](https://forums.plex.tv/t/playlists-remember-position-for-subsequent-resume/84866/39)

## Playlist Attributes

Plex Meta Manager can automatically build and update playlists defined within the `playlists` attribute.

Each playlist requires its own section within the `playlists` attribute and unlike collections, playlists can only be built using one Builder as their ordering is inherited from the builder; it is not possible to combine builders.

```yaml
playlists:
  Marvel Cinematic Universe Chronological Order:
    # ... builder, details, and filters for this playlist
  Star Wars Clone Wars Chronological Order:
    # ... builder, details, and filters for this playlist
  etc:
    # ... builder, details, and filters for this playlist
```

Playlists require the `libraries` attribute, which instructs the operation to look in the specified libraries. This allows media to be combined from multiple libraries into one playlist. The mappings that you define in the `libraries` attribute must match the library names in your [Configuration File](../config/configuration).

The playlist can also use the `sync_to_users` attributes to control who has visibility of the playlist. This will override the global [`playlist_sync_to_users` Setting](../config/settings.md#playlist-sync-to-users). `sync_to_users` can be set to `all` to sync to all users who have access to the Plex Media Server, or a list/comma-separated string of users. The Plex Media Server owner will always have visibility of the Playlists, so does not need to be defined within the attribute. Leaving `sync_to_users` empty will make the playlist visible to the Plex Media Server owner only.

There are three types of attributes that can be utilized within a playlist:

### Builders

Builders use third-party services to source items to be added to the playlist. Multiple builders can be used in the same playlist from a variety of sources listed below.

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

### Details

These can alter any aspect of the playlist or the media items within them.

* [Setting Details](details/setting)
* [Schedule Detail](details/schedule)
* [Metadata Details](details/metadata)
* [Arr Details](details/arr)

### Filters

These filter media items added to the playlist by any of the Builders.

* [Filters](filters)

## Example

In the following example, media is pulled from the `Movies` and `TV Shows` libraries into the one Playlist, and the playlist is shared with a specific set of users:

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
