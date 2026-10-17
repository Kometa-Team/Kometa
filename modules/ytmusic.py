import json
import re
from urllib.parse import parse_qs, urlparse

from requests.exceptions import RequestException
from ytmusicapi import YTMusic
from ytmusicapi.exceptions import YTMusicError

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["ytmusic_list", "ytmusic_top_artists"]
chart_sections = ("videos", "genres", "languages")
dynamic_chart_types = {f"ytmusic_{section[:-1] if section.endswith('s') else section}_charts": section for section in chart_sections}
countries = (
    "AE",
    "AR",
    "AT",
    "AU",
    "BE",
    "BO",
    "BR",
    "CA",
    "CH",
    "CL",
    "CO",
    "CR",
    "CZ",
    "DE",
    "DK",
    "DO",
    "EC",
    "EE",
    "EG",
    "ES",
    "FI",
    "FR",
    "GB",
    "GT",
    "HK",
    "HN",
    "HU",
    "ID",
    "IE",
    "IL",
    "IN",
    "IS",
    "IT",
    "JP",
    "KE",
    "KR",
    "LU",
    "MX",
    "MY",
    "NG",
    "NI",
    "NL",
    "NO",
    "NZ",
    "PA",
    "PE",
    "PH",
    "PL",
    "PT",
    "PY",
    "RO",
    "RS",
    "RU",
    "SA",
    "SE",
    "SG",
    "SV",
    "TH",
    "TR",
    "TW",
    "TZ",
    "UA",
    "UG",
    "US",
    "UY",
    "VN",
    "ZA",
    "ZW",
    "ZZ",
)
playlist_id_pattern = re.compile(r"^[A-Za-z0-9_-]+$")


def playlist_id(value):
    value = str(value).strip()
    if value.startswith(("http://", "https://")):
        parsed = urlparse(value)
        if parsed.scheme != "https" or parsed.hostname not in ("music.youtube.com", "www.youtube.com", "youtube.com") or parsed.path != "/playlist":
            raise Failed(f"YouTube Music Error: {value} is not a supported playlist URL")
        ids = parse_qs(parsed.query).get("list", [])
        value = ids[0] if len(ids) == 1 else ""
    if not playlist_id_pattern.fullmatch(value):
        raise Failed(f"YouTube Music Error: {value} is not a valid playlist ID")
    return value


class YouTubeMusic:
    def __init__(self):
        self.artist_image_cache = {}
        try:
            self.client = YTMusic()
        except (YTMusicError, RequestException, OSError, ValueError) as e:
            raise Failed(f"YouTube Music Error: unable to initialize public client: {e}") from e

    @staticmethod
    def _count_value(value):
        if not isinstance(value, str):
            return None
        match = re.match(r"\s*([\d,.]+)\s*([KMB])?", value, flags=re.IGNORECASE)
        if not match:
            return None
        try:
            number = float(match.group(1).replace(",", ""))
        except ValueError:
            return None
        return number * {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get((match.group(2) or "").upper(), 1)

    @staticmethod
    def _artist_name(artist):
        return next((artist.get(key) for key in ("artist", "title", "name") if isinstance(artist.get(key), str)), None)

    @staticmethod
    def _high_resolution_image_url(url, background=False):
        """Request a larger rendition from YouTube's image CDN when its URL exposes a size modifier."""
        size = "1920" if background else "1200"
        url = re.sub(r"=w\d+-h\d+", f"=w{size}-h{size}", url, count=1)
        return re.sub(r"=s\d+(?=[-=]|$)", f"=s{size}", url, count=1)

    @staticmethod
    def _artist_lookup_error(error):
        if isinstance(error, KeyError) and "twoColumnBrowseResultsRenderer" in str(error):
            return "YouTube Music returned an unsupported artist page layout"
        reason = str(error).splitlines()[0].strip()
        return f"{type(error).__name__}: {reason[:120]}" if reason else type(error).__name__

    @staticmethod
    def _image_url(artist, background=False):
        thumbnails = artist.get("thumbnails")
        if not isinstance(thumbnails, list):
            return None
        images = [image for image in thumbnails if isinstance(image, dict) and isinstance(image.get("url"), str) and image["url"].startswith("https://")]
        if not images:
            return None

        def image_score(image):
            width = image.get("width") or 0
            height = image.get("height") or 0
            ratio = width / height if width and height else 1.0
            if background:
                aspect_score = (0 if ratio >= 1.35 else 1, abs(ratio - (16 / 9)))
            else:
                aspect_score = (0 if 0.8 <= ratio <= 1.2 else 1, abs(ratio - 1))
            return (*aspect_score, -(width * height))

        return YouTubeMusic._high_resolution_image_url(min(images, key=image_score)["url"], background=background)

    def artist_image_url(self, artist_name, background=False):
        """Find a public artist image by exact name, preferring profile images or landscape banners."""
        artist_name = artist_name.strip() if isinstance(artist_name, str) else ""
        if not artist_name:
            return None
        from modules.plex import music_title_key

        artist_key = music_title_key(artist_name)
        cache_key = (artist_key, background)
        if cache_key in self.artist_image_cache:
            return self.artist_image_cache[cache_key]

        try:
            results = self.client.search(artist_name, filter="artists", limit=20, ignore_spelling=True)
        except Exception as e:
            logger.warning(f"YouTube Music Warning: unable to search for an image for artist {artist_name} ({self._artist_lookup_error(e)}); continuing without an image")
            self.artist_image_cache[cache_key] = None
            return None

        exact_matches = {}
        for result in results or []:
            if not isinstance(result, dict):
                continue
            result_name = self._artist_name(result)
            channel_id = result.get("browseId")
            if isinstance(result_name, str) and music_title_key(result_name) == artist_key and isinstance(channel_id, str) and channel_id:
                exact_matches.setdefault(channel_id, result)
        if not exact_matches:
            self.artist_image_cache[cache_key] = None
            return None

        if len(exact_matches) == 1:
            only_match = next(iter(exact_matches.values()))
            image_url = self._image_url(only_match, background=background)
            if image_url:
                self.artist_image_cache[cache_key] = image_url
                return image_url

        candidates = []
        for channel_id, result in exact_matches.items():
            details = {}
            try:
                details = self.client.get_artist(channel_id)
            except Exception as e:
                logger.warning(f"YouTube Music Warning: artist details unavailable for {artist_name} ({self._artist_lookup_error(e)}); using search-result artwork if available")
            details = details if isinstance(details, dict) else {}
            detail_name = self._artist_name(details)
            if detail_name and music_title_key(detail_name) != artist_key:
                continue
            popularity = self._count_value(details.get("monthlyListeners"))
            if popularity is None:
                popularity = self._count_value(details.get("subscribers"))
            result_image = self._image_url(result, background=background)
            detail_image = self._image_url(details, background=background)
            image_url = (detail_image or result_image) if background else (result_image or detail_image)
            candidates.append((popularity, image_url))

        candidates = [(score, url) for score, url in candidates if url]
        if not candidates:
            image_url = None
        elif len(candidates) == 1:
            image_url = candidates[0][1]
        else:
            candidates.sort(key=lambda candidate: candidate[0] if candidate[0] is not None else -1, reverse=True)
            image_url = candidates[0][1] if candidates[0][0] is not None and (len(candidates) == 1 or candidates[0][0] != candidates[1][0]) else None
            if image_url is None:
                logger.warning(f"YouTube Music Warning: multiple exact artist matches for {artist_name} have no distinct popularity score; skipping poster")

        self.artist_image_cache[cache_key] = image_url
        if not image_url:
            logger.debug(f"YouTube Music: no unambiguous public artist image found for {artist_name}")
        return image_url

    def _load_playlist(self, playlist, limit=None):
        try:
            data = self.client.get_playlist(playlist, limit=limit)
        except (YTMusicError, RequestException) as e:
            raise Failed(f"YouTube Music Error: unable to load playlist {playlist}: {e}") from e
        tracks = data.get("tracks")
        if not isinstance(tracks, list):
            raise Failed(f"YouTube Music Error: playlist {playlist} did not return tracks")
        return tracks

    def get_rating_keys(self, value, library):
        playlist = value["playlist"] if isinstance(value, dict) else value
        limit = value.get("limit") if isinstance(value, dict) else None
        return self._match_tracks(self._load_playlist(playlist_id(playlist), limit=limit), library)

    def get_top_artists(self, country, library):
        from modules.plex import MusicMatcher

        try:
            charts = self.client.get_charts(country=country)
        except (YTMusicError, RequestException) as e:
            raise Failed(f"YouTube Music Error: unable to load {country} charts: {e}") from e
        artists = charts.get("artists")
        # ytmusicapi currently identifies artist carousels by their renderer only.
        # Some country responses use that same renderer for album entries, so
        # validate their browse IDs before treating the titles as artists.
        if not isinstance(artists, list) or not artists or not any(self._is_artist_chart_entry(artist) for artist in artists):
            if country != "ZZ":
                try:
                    global_charts = self.client.get_charts(country="ZZ")
                except (YTMusicError, RequestException) as e:
                    raise Failed(f"YouTube Music Error: unable to load global artist chart fallback: {e}") from e
                artists = global_charts.get("artists") if isinstance(global_charts, dict) else None
        if not isinstance(artists, list) or not artists or not any(self._is_artist_chart_entry(artist) for artist in artists):
            raise Failed(f"YouTube Music Error: artist charts are unavailable for {country}")
        matcher = MusicMatcher([library], "artist")
        results = []
        seen = set()
        for artist in artists:
            if not isinstance(artist, dict) or not isinstance(artist.get("title"), str) or not artist["title"].strip():
                continue
            name = artist["title"].strip()
            match, reason = matcher.match(artist=name)
            if match is not None:
                if match.ratingKey not in seen:
                    results.append((match.ratingKey, "ratingKey"))
                    seen.add(match.ratingKey)
            elif name.casefold() not in seen:
                results.append((json.dumps({"level": "artist", "artist": name, "name": name, "mbid": "", "reason": reason}), "music_missing"))
                seen.add(name.casefold())
        return results

    @staticmethod
    def _is_artist_chart_entry(artist):
        browse_id = artist.get("browseId") if isinstance(artist, dict) else None
        return isinstance(browse_id, str) and browse_id.startswith("UC")

    def chart_playlists(self, country, section):
        try:
            charts = self.client.get_charts(country=country)
        except (YTMusicError, RequestException) as e:
            raise Failed(f"YouTube Music Error: unable to load {country} charts: {e}") from e
        entries = charts.get(section)
        if not isinstance(entries, list) or not entries:
            available = ", ".join(name for name in chart_sections if charts.get(name)) or "none"
            raise Failed(f"YouTube Music Error: {section} charts are unavailable for {country}. Available sections: {available}.")

        countries_data = charts.get("countries")
        selected = countries_data.get("selected") if isinstance(countries_data, dict) else None
        country_name = selected.get("text") if isinstance(selected, dict) else None
        return [{**entry, "country_name": country_name} for entry in entries if isinstance(entry, dict) and entry.get("playlistId") and entry.get("title")]

    @staticmethod
    def chart_name(title, section):
        if section == "genres":
            match = re.fullmatch(r"Top \d+ (.+?) Music Videos(?: .*)?", title, flags=re.IGNORECASE)
            if match:
                return match.group(1)
        return title

    def playlist_metadata(self, playlist):
        thumbnails = None
        description = None
        try:
            details = self.client.get_playlist(playlist, limit=0)
        except (YTMusicError, RequestException, ValueError) as e:
            logger.debug(f"YouTube Music playlist metadata unavailable for {playlist}: {e}")
        else:
            if isinstance(details, dict):
                description = details.get("description")
                thumbnails = details.get("thumbnails") or thumbnails
        poster = None
        if isinstance(thumbnails, list):
            images = [image for image in thumbnails if isinstance(image, dict) and isinstance(image.get("url"), str) and image["url"].startswith("https://")]
            if images:
                poster = max(images, key=lambda image: (image.get("width") or 0) * (image.get("height") or 0))["url"]
        return description.strip() if isinstance(description, str) and description.strip() else None, poster

    @staticmethod
    def _match_tracks(tracks, library):
        from modules.plex import MusicMatcher, music_title_key

        matcher = MusicMatcher([library], "track")
        results = []
        seen = set()
        seen_missing = set()
        for source in tracks:
            if not isinstance(source, dict):
                continue
            title = source.get("title")
            if not isinstance(title, str) or not title.strip():
                continue
            artists = source.get("artists") or []
            if not isinstance(artists, list):
                artists = []
            artist_names = [artist["name"] for artist in artists if isinstance(artist, dict) and isinstance(artist.get("name"), str) and artist["name"].strip()]
            album_data = source.get("album")
            album = album_data.get("name") if isinstance(album_data, dict) else None
            if not isinstance(album, str) or not album.strip():
                album = None
            duration = source.get("duration_seconds")
            duration_ms = int(duration * 1000) if isinstance(duration, (int, float)) and not isinstance(duration, bool) and duration > 0 else None

            match = None
            reason = "not found"
            for artist in artist_names:
                match, duration_reason = matcher.match_track_duration(artist, title, duration_ms)
                if duration_reason == "ambiguous":
                    reason = duration_reason
                if match is not None:
                    break
            if match is None and album:
                for artist in artist_names:
                    match, album_reason = matcher.match(artist=artist, album=album, track=title)
                    if album_reason == "ambiguous":
                        reason = album_reason
                    if match is not None:
                        break
            if match is None:
                for artist in artist_names:
                    candidates = matcher.tracks_by_artist_title.get((music_title_key(artist), music_title_key(title)), [])
                    if len(candidates) == 1:
                        match = candidates[0]
                        break
                    elif len(candidates) > 1:
                        reason = "ambiguous"

            if match is not None:
                if match.ratingKey not in seen:
                    results.append((match.ratingKey, "ratingKey"))
                    seen.add(match.ratingKey)
            else:
                artist = artist_names[0] if artist_names else "Unknown Artist"
                missing = {"level": "track", "artist": artist, "album": album, "name": title, "mbid": "", "reason": reason}
                missing_key = (artist, album, title, reason)
                if missing_key not in seen_missing:
                    results.append((json.dumps(missing), "music_missing"))
                    seen_missing.add(missing_key)
        return results
