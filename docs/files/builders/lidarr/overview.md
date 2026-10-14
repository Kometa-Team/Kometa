# Lidarr Builders

Lidarr builders create artist collections from artists already tracked in Lidarr. They require a configured Lidarr connection and a Plex music library.

Kometa matches each Lidarr artist's MusicBrainz artist ID to the `mbid://` GUID on the Plex artist. Artists without a matching Plex artist are reported as missing and are not added to the collection.

- [All](all.md) includes every Lidarr artist.
- [Taglist](taglist.md) includes artists with specified Lidarr tags.
