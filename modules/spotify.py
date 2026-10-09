import base64
import re
import secrets
import time
import webbrowser
from urllib.parse import parse_qs, urlencode, urlparse

from modules import util
from modules.util import Failed, TimeoutExpired

logger = util.logger

authorize_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
api_url = "https://api.spotify.com/v1"
scopes = "playlist-read-private playlist-read-collaborative user-library-read user-read-recently-played user-top-read"
builders = ["spotify_list", "spotify_list_details", "spotify_liked", "spotify_top", "spotify_recent", "spotify_saved"]
playlist_id_pattern = re.compile(r"^[A-Za-z0-9]{22}$")


def parse_playlist_id(value):
    """Return a Spotify playlist ID from either a bare ID or Spotify URL."""
    value = str(value).strip()
    if value.startswith("spotify:playlist:"):
        value = value.removeprefix("spotify:playlist:")
    elif value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.netloc not in ["open.spotify.com", "www.open.spotify.com"] or len(parts) != 2 or parts[0] != "playlist":
            raise Failed(f"Spotify Error: Invalid playlist URL: {value}")
        value = parts[1]
    if not playlist_id_pattern.fullmatch(value):
        raise Failed(f"Spotify Error: Invalid playlist ID: {value}")
    return value


class Spotify:
    def __init__(self, requests, read_only, params):
        self.requests = requests
        self.read_only = read_only
        self.client_id = params["client_id"]
        self.client_secret = params["client_secret"]
        self.redirect_uri = params["redirect_uri"]
        self._validate_redirect_uri()
        self.config_path = params["config_path"]
        self.authorization = dict(params.get("authorization") or {})
        self.access_token = None
        logger.secret(self.client_secret)
        if self.authorization.get("refresh_token"):
            logger.secret(self.authorization["refresh_token"])
        if self.authorization.get("access_token") and self._access_token_is_current() and self._has_requested_scopes():
            self.access_token = self.authorization["access_token"]
        elif self.authorization.get("refresh_token") and self._has_requested_scopes():
            try:
                self._refresh()
            except Failed:
                logger.info("Spotify authorization has expired; authorizing again.")
                self._authorize()
        else:
            self._authorize()

    def _basic_auth(self):
        credentials = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        return {"Authorization": f"Basic {base64.b64encode(credentials).decode('ascii')}"}

    def _validate_redirect_uri(self):
        parsed = urlparse(self.redirect_uri)
        is_loopback = parsed.scheme == "http" and parsed.hostname == "127.0.0.1"
        if not parsed.netloc or (parsed.scheme != "https" and not is_loopback):
            raise Failed("Spotify Error: redirect_uri must use HTTPS or http://127.0.0.1 for local authorization.")

    def _access_token_is_current(self):
        try:
            return float(self.authorization.get("expires_at", 0)) > time.time()
        except (TypeError, ValueError):
            return False

    def _has_requested_scopes(self):
        return set(scopes.split()).issubset(set(str(self.authorization.get("scope", "")).split()))

    def _authorize(self):
        state = secrets.token_urlsafe(32)
        url = f"{authorize_url}?{urlencode({'response_type': 'code', 'client_id': self.client_id, 'redirect_uri': self.redirect_uri, 'scope': scopes, 'state': state})}"
        logger.info(f"Navigate to: {url}")
        webbrowser.open(url, new=2)
        try:
            callback = util.logger_input("Spotify redirect URL").strip()
        except TimeoutExpired:
            raise Failed("Spotify Error: Redirect URL required.")
        query = parse_qs(urlparse(callback).query)
        if query.get("state", [None])[0] != state:
            raise Failed("Spotify Error: Invalid redirect URL state.")
        if query.get("error", [None])[0]:
            raise Failed(f"Spotify Error: Authorization was denied ({query['error'][0]}).")
        code = query.get("code", [None])[0]
        if not code:
            raise Failed("Spotify Error: Invalid redirect URL.")
        self._token({"grant_type": "authorization_code", "code": code, "redirect_uri": self.redirect_uri})

    def _refresh(self):
        self._token({"grant_type": "refresh_token", "refresh_token": self.authorization["refresh_token"]})

    def _token(self, data):
        response = self.requests.post_json(token_url, data=data, headers=self._basic_auth())
        if not isinstance(response, dict) or not response.get("access_token"):
            raise Failed(f"Spotify Error: Authorization failed{self._error_suffix(response)}")
        self.authorization.update(response)
        self.authorization["expires_at"] = int(time.time()) + int(response.get("expires_in", 3600))
        self.access_token = self.authorization["access_token"]
        logger.secret(self.access_token)
        if not self.read_only and self.config_path and hasattr(self.requests, "file_yaml"):
            yaml = self.requests.file_yaml(self.config_path)
            if "spotify" not in yaml.data or not isinstance(yaml.data["spotify"], dict):
                yaml.data["spotify"] = {}
            yaml.data["spotify"]["authorization"] = self.authorization
            logger.info(f"Saving Spotify authorization information to {self.config_path}")
            yaml.save()

    def get_playlist_tracks(self, playlist_id):
        playlist_id = self.resolve_playlist_id(playlist_id)
        return self._get_tracks(f"{api_url}/playlists/{playlist_id}/items", "playlist", item_key=("item", "track"))

    def get_playlist_details(self, playlist_id):
        playlist_id = self.resolve_playlist_id(playlist_id)
        data = self._get_json(f"{api_url}/playlists/{playlist_id}", "playlist details")
        if not isinstance(data, dict):
            raise Failed("Spotify Error: Unable to read playlist details.")
        images = self._get_json(f"{api_url}/playlists/{playlist_id}/images", "playlist artwork")
        if isinstance(images, list):
            data["images"] = images
        return data

    def get_liked_tracks(self):
        return self._get_tracks(f"{api_url}/me/tracks", "liked songs")

    def get_top_tracks(self, period):
        return self._get_tracks(f"{api_url}/me/top/tracks?time_range={period}_term&limit=50", f"top {period} term tracks", item_key=None)

    def get_recent_tracks(self):
        return self._get_tracks(f"{api_url}/me/player/recently-played?limit=50", "recently played tracks")

    def get_saved_albums(self):
        return [item["album"] for item in self._get_items(f"{api_url}/me/albums", "saved albums") if item.get("album")]

    def resolve_playlist_id(self, value):
        try:
            return parse_playlist_id(value)
        except Failed:
            name = str(value).strip()
            if not name or name.startswith("spotify:") or name.startswith("http://") or name.startswith("https://"):
                raise
        matches = [playlist for playlist in self._get_items(f"{api_url}/me/playlists", "your playlists") if playlist.get("name", "").casefold() == name.casefold()]
        if not matches:
            raise Failed(f"Spotify Error: Playlist named '{name}' not found in your Spotify library.")
        if len(matches) > 1:
            options = ", ".join(f"https://open.spotify.com/playlist/{playlist['id']}" for playlist in matches if playlist.get("id"))
            raise Failed(f"Spotify Error: More than one playlist named '{name}' was found in your Spotify library. Use its URL or ID instead: {options}")
        if not matches[0].get("id"):
            raise Failed(f"Spotify Error: Playlist named '{name}' has no Spotify ID.")
        return matches[0]["id"]

    def _get_tracks(self, url, source, item_key="track"):
        items = self._get_items(url, source)
        if item_key is None:
            return items
        item_keys = item_key if isinstance(item_key, tuple) else (item_key,)
        return [next((item[key] for key in item_keys if item.get(key)), None) for item in items if any(item.get(key) for key in item_keys)]

    def _get_items(self, url, source):
        items = []
        while url:
            data = self._get_json(url, source)
            if not isinstance(data, dict):
                raise Failed(f"Spotify Error: Unable to read {source}: Spotify returned an invalid response.")
            if "items" not in data:
                raise Failed(f"Spotify Error: Unable to read {source}: Spotify returned no items.")
            items.extend(item for item in data["items"] if isinstance(item, dict))
            url = data.get("next")
        return items

    def _get_json(self, url, source):
        try:
            data = self.requests.get_json(url, headers={"Authorization": f"Bearer {self.access_token}"})
        except ValueError as e:
            raise Failed(f"Spotify Error: Unable to read {source}: Spotify returned invalid JSON.") from e
        if isinstance(data, dict) and "error" in data:
            raise Failed(f"Spotify Error: Unable to read {source}{self._error_suffix(data)}")
        return data

    @staticmethod
    def _error_suffix(data):
        error = data.get("error") if isinstance(data, dict) else None
        if isinstance(error, dict):
            message = error.get("message")
            status = error.get("status")
            if message and status:
                return f" ({status}: {message})"
            if message:
                return f" ({message})"
        return ""
