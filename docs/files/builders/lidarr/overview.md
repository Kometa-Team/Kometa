# Lidarr Builders

Lidarr builders create artist collections from artists already tracked in Lidarr. They require a configured Lidarr connection and a Plex music library.

Kometa first matches each Lidarr artist's MusicBrainz artist ID to a Plex `mbid://` GUID. If the ID cannot identify one artist, it accepts an exact, case-insensitive Lidarr artist-name match only when it is unique in Plex. Artists without a unique match are reported as missing and are not added to the collection.

- [All](all.md) includes every Lidarr artist.
- [Taglist](taglist.md) includes artists with specified Lidarr tags.
