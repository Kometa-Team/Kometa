import json
from typing import cast

import pylast

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["lastfm_user_top_artists", "lastfm_user_top_albums", "lastfm_user_top_tracks", "lastfm_user_loved_tracks", "lastfm_user_recent_tracks", "lastfm_user_tags", "lastfm_tag_charts", "lastfm_chart_top_artists", "lastfm_chart_top_tracks"]
periods = ("overall", "7day", "1month", "3month", "6month", "12month")


class LastFM:
    def __init__(self, apikey):
        self.apikey = apikey
        logger.secret(apikey)
        self.network = pylast.LastFMNetwork(api_key=apikey)

    @staticmethod
    def _get_mbid(item, label):
        from modules.plex import music_mbid_pattern

        try:
            mbid = (item.get_mbid() or "").lower()
        except pylast.PyLastError as e:
            logger.debug(f"Last.fm {label} MBID unavailable: {e}")
            return ""
        return mbid if music_mbid_pattern.fullmatch(mbid) else ""

    def get_rating_keys(self, method, value, library):
        if method == "lastfm_chart_top_artists":
            try:
                items = self.network.get_top_artists(limit=value["limit"])
            except pylast.PyLastError as e:
                raise Failed(f"Last.fm Error: {e}") from e
            return self._get_artist_rating_keys(value, library, items=items)
        if method == "lastfm_chart_top_tracks":
            try:
                items = self.network.get_top_tracks(limit=value["limit"])
            except pylast.PyLastError as e:
                raise Failed(f"Last.fm Error: {e}") from e
            return self._get_track_rating_keys(method, value, library, items=items)
        if method in ("lastfm_user_tags", "lastfm_tag_charts"):
            items = self._get_tag_items(method, value)
            if value["level"] == "album":
                return self._get_album_rating_keys(value, library, items=items)
            if value["level"] == "track":
                return self._get_track_rating_keys(method, value, library, items=items)
            return self._get_artist_rating_keys(value, library, items=items)
        if method == "lastfm_user_top_albums":
            return self._get_album_rating_keys(value, library)
        if method in ("lastfm_user_top_tracks", "lastfm_user_loved_tracks", "lastfm_user_recent_tracks"):
            return self._get_track_rating_keys(method, value, library)
        return self._get_artist_rating_keys(value, library)

    def _get_tag_items(self, method, value):
        try:
            if method == "lastfm_user_tags":
                source = self.network.get_user(value["username"])
                getter = {"artist": source.get_tagged_artists, "album": source.get_tagged_albums, "track": source.get_tagged_tracks}[value["level"]]
                return [pylast.TopItem(item, 0) for item in getter(value["tag"], limit=value["limit"])]
            source = self.network.get_tag(value["tag"])
            getter = {"artist": source.get_top_artists, "album": source.get_top_albums, "track": source.get_top_tracks}[value["level"]]
            return getter(limit=value["limit"])
        except pylast.PyLastError as e:
            raise Failed(f"Last.fm Error: {e}") from e

    def _get_artist_rating_keys(self, value, library, items=None):
        from modules.plex import MusicMatcher

        matcher = MusicMatcher([library], "artist")

        if items is None:
            try:
                items = self.network.get_user(value["username"]).get_top_artists(period=value["period"], limit=value["limit"])
            except pylast.PyLastError as e:
                raise Failed(f"Last.fm Error: {e}") from e

        results = []
        seen = set()
        seen_missing = set()
        for entry in items:
            lastfm_artist = cast(pylast.Artist, entry.item)
            artist_name = str(lastfm_artist.get_name())
            mbid = self._get_mbid(lastfm_artist, f"artist {artist_name}")
            artist, reason = matcher.match(mbid=mbid, artist=artist_name)
            if artist is None:
                missing_key = (artist_name, mbid, reason)
                if missing_key not in seen_missing:
                    results.append((json.dumps({"name": artist_name, "mbid": mbid, "reason": reason}), "lastfm_missing"))
                    seen_missing.add(missing_key)
                continue
            rating_key = artist.ratingKey
            if rating_key not in seen:
                results.append((rating_key, "ratingKey"))
                seen.add(rating_key)
        return results

    def _get_album_rating_keys(self, value, library, items=None):
        from modules.plex import MusicMatcher

        matcher = MusicMatcher([library], "album")

        if items is None:
            try:
                items = self.network.get_user(value["username"]).get_top_albums(period=value["period"], limit=value["limit"])
            except pylast.PyLastError as e:
                raise Failed(f"Last.fm Error: {e}") from e

        results = []
        seen = set()
        seen_missing = set()
        for entry in items:
            lastfm_album = cast(pylast.Album, entry.item)
            album_name = str(lastfm_album.get_name())
            artist_name = str(cast(pylast.Artist, lastfm_album.get_artist()).get_name())
            mbid = self._get_mbid(lastfm_album, f"album {artist_name} - {album_name}")
            album, reason = matcher.match(mbid=mbid, artist=artist_name, album=album_name)
            if album is None:
                missing_key = (artist_name, album_name, mbid, reason)
                if missing_key not in seen_missing:
                    results.append((json.dumps({"artist": artist_name, "name": album_name, "mbid": mbid, "reason": reason}), "lastfm_album_missing"))
                    seen_missing.add(missing_key)
                continue
            rating_key = album.ratingKey
            if rating_key not in seen:
                results.append((rating_key, "ratingKey"))
                seen.add(rating_key)
        return results

    def _get_track_rating_keys(self, method, value, library, items=None):
        from modules.plex import MusicMatcher

        matcher = MusicMatcher([library], "track")
        if items is None:
            try:
                user = self.network.get_user(value["username"])
                if method == "lastfm_user_loved_tracks":
                    items = user.get_loved_tracks(limit=value["limit"])
                elif method == "lastfm_user_recent_tracks":
                    items = user.get_recent_tracks(limit=value["limit"], time_from=value.get("from"), time_to=value.get("to"), cacheable=False)
                else:
                    items = user.get_top_tracks(period=value["period"], limit=value["limit"])
            except pylast.PyLastError as e:
                raise Failed(f"Last.fm Error: {e}") from e

        results = []
        seen = set()
        seen_missing = set()
        for entry in items:
            if method in ("lastfm_user_loved_tracks", "lastfm_user_recent_tracks"):
                lastfm_track = cast(pylast.Track, getattr(entry, "track"))
            else:
                lastfm_track = cast(pylast.Track, getattr(entry, "item"))
            track_name = str(lastfm_track.get_name())
            artist_name = str(cast(pylast.Artist, lastfm_track.get_artist()).get_name())
            mbid = self._get_mbid(lastfm_track, f"track {artist_name} - {track_name}")
            track, reason = matcher.match(mbid=mbid)
            album_name = getattr(entry, "album", None) if method == "lastfm_user_recent_tracks" else None
            if track is None:
                try:
                    duration_ms = lastfm_track.get_duration()
                except pylast.PyLastError as e:
                    logger.debug(f"Last.fm duration unavailable for {artist_name} - {track_name}: {e}")
                    duration_ms = None
                duration_match, duration_reason = matcher.match_track_duration(artist_name, track_name, duration_ms)
                if duration_match is not None:
                    track, reason = duration_match, None
                elif duration_reason == "ambiguous":
                    reason = duration_reason
            if track is None and not album_name:
                try:
                    lastfm_album = lastfm_track.get_album()
                    album_name = str(lastfm_album.get_name()) if lastfm_album else None
                except pylast.PyLastError as e:
                    logger.debug(f"Last.fm album unavailable for {artist_name} - {track_name}: {e}")
            if track is None and album_name:
                track, reason = matcher.match(mbid=mbid, artist=artist_name, album=album_name, track=track_name)
            if track is None:
                missing_key = (artist_name, album_name, track_name, mbid, reason)
                if missing_key not in seen_missing:
                    results.append((json.dumps({"level": "track", "artist": artist_name, "album": album_name, "name": track_name, "mbid": mbid, "reason": reason}), "music_missing"))
                    seen_missing.add(missing_key)
                continue
            rating_key = track.ratingKey
            if rating_key not in seen:
                results.append((rating_key, "ratingKey"))
                seen.add(rating_key)
        return results
