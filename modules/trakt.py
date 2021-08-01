import logging, requests, webbrowser
from modules import util
from modules.util import Failed, TimeoutExpired
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
redirect_uri_encoded = redirect_uri.replace(":", "%3A")
base_url = "https://api.trakt.tv"
builders = [
    "trakt_collected", "trakt_collection", "trakt_list", "trakt_list_details", "trakt_popular",
    "trakt_recommended", "trakt_trending", "trakt_watched", "trakt_watchlist"
]
sorts = [
    "rank", "added", "title", "released", "runtime", "popularity",
    "percentage", "votes", "random", "my_rating", "watched", "collected"
]

class Trakt:
    def __init__(self, config, params):
        self.config = config
        self.client_id = params["client_id"]
        self.client_secret = params["client_secret"]
        self.config_path = params["config_path"]
        self.authorization = params["authorization"]
        if not self._save(self.authorization):
            if not self._refresh():
                self._authorization()

    def _authorization(self):
        url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={self.client_id}&redirect_uri={redirect_uri_encoded}"
        logger.info(f"Navigate to: {url}")
        logger.info("If you get an OAuth error your client_id or client_secret is invalid")
        webbrowser.open(url, new=2)
        try:                                pin = util.logger_input("Trakt pin (case insensitive)", timeout=300).strip()
        except TimeoutExpired:              raise Failed("Input Timeout: Trakt pin required.")
        if not pin:                         raise Failed("Trakt Error: No input Trakt pin required.")
        json = {
            "code": pin,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = self.config.post(f"{base_url}/oauth/token", json=json, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            raise Failed("Trakt Error: Invalid trakt pin. If you're sure you typed it in correctly your client_id or client_secret may be invalid")
        elif not self._save(response.json()):
            raise Failed("Trakt Error: New Authorization Failed")

    def _check(self, authorization=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authorization['access_token'] if authorization is None else authorization['access_token']}",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id
        }
        response = self.config.get(f"{base_url}/users/settings", headers=headers)
        return response.status_code == 200

    def _refresh(self):
        if self.authorization and "refresh_token" in self.authorization and self.authorization["refresh_token"]:
            logger.info("Refreshing Access Token...")
            json = {
                "refresh_token": self.authorization["refresh_token"],
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "refresh_token"
              }
            response = self.config.post(f"{base_url}/oauth/token", json=json, headers={"Content-Type": "application/json"})
            if response.status_code != 200:
                return False
            return self._save(response.json())
        return False

    def _save(self, authorization):
        if authorization and self._check(authorization):
            if self.authorization != authorization:
                yaml.YAML().allow_duplicate_keys = True
                config, ind, bsi = yaml.util.load_yaml_guess_indent(open(self.config_path))
                config["trakt"]["authorization"] = {
                    "access_token": authorization["access_token"],
                    "token_type": authorization["token_type"],
                    "expires_in": authorization["expires_in"],
                    "refresh_token": authorization["refresh_token"],
                    "scope": authorization["scope"],
                    "created_at": authorization["created_at"]
                }
                logger.info(f"Saving authorization information to {self.config_path}")
                yaml.round_trip_dump(config, open(self.config_path, "w"), indent=ind, block_seq_indent=bsi)
                self.authorization = authorization
            return True
        return False

    def _request(self, url):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authorization['access_token']}",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id
        }
        response = self.config.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Failed(f"({response.status_code}) {response.reason}")

    def convert(self, external_id, from_source, to_source, media_type):
        path = f"/search/{from_source}/{external_id}"
        if from_source in ["tmdb", "tvdb"]:
            path = f"{path}?type={media_type}"
        lookup = self._request(f"{base_url}{path}")
        if lookup and media_type in lookup[0] and to_source in lookup[0][media_type]["ids"]:
            return lookup[0][media_type]["ids"][to_source]
        raise Failed(f"Trakt Error: No {to_source.upper().replace('B', 'b')} ID found for {from_source.upper().replace('B', 'b')} ID: {external_id}")

    def list_description(self, data):
        try:
            return self._request(f"{base_url}{requests.utils.urlparse(data).path}")["description"]
        except Failed:
            raise Failed(f"Trakt Error: List {data} not found")

    def _user_list(self, list_type, data, is_movie):
        path = f"{requests.utils.urlparse(data).path}/items" if list_type == "list" else f"/users/{data}/{list_type}"
        try:
            items = self._request(f"{base_url}{path}/{'movies' if is_movie else 'shows'}")
        except Failed:
            raise Failed(f"Trakt Error: {'List' if list_type == 'list' else 'User'} {data} not found")
        if len(items) == 0:
            if list_type == "list":
                raise Failed(f"Trakt Error: List {data} is empty")
            else:
                raise Failed(f"Trakt Error: {data}'s {list_type.capitalize()} is empty")
        if is_movie:                                return [item["movie"]["ids"]["tmdb"] for item in items], []
        else:                                       return [], [item["show"]["ids"]["tvdb"] for item in items]

    def _pagenation(self, pagenation, amount, is_movie):
        items = self._request(f"{base_url}/{'movies' if is_movie else 'shows'}/{pagenation}?limit={amount}")
        if pagenation == "popular" and is_movie:    return [item["ids"]["tmdb"] for item in items], []
        elif pagenation == "popular":               return [], [item["ids"]["tvdb"] for item in items]
        elif is_movie:                              return [item["movie"]["ids"]["tmdb"] for item in items], []
        else:                                       return [], [item["show"]["ids"]["tvdb"] for item in items]

    def validate_trakt(self, trakt_lists, is_movie, trakt_type="list"):
        values = util.get_list(trakt_lists, split=False)
        trakt_values = []
        for value in values:
            try:
                self._user_list(trakt_type, value, is_movie)
                trakt_values.append(value)
            except Failed as e:
                logger.error(e)
        if len(trakt_values) == 0:
            if trakt_type == "watchlist":
                raise Failed(f"Trakt Error: No valid Trakt Watchlists in {values}")
            elif trakt_type == "collection":
                raise Failed(f"Trakt Error: No valid Trakt Collections in {values}")
            else:
                raise Failed(f"Trakt Error: No valid Trakt Lists in {values}")
        return trakt_values

    def get_items(self, method, data, is_movie):
        pretty = method.replace("_", " ").title()
        media_type = "Movie" if is_movie else "Show"
        if method in ["trakt_trending", "trakt_popular", "trakt_recommended", "trakt_watched", "trakt_collected"]:
            movie_ids, show_ids = self._pagenation(method[6:], data, is_movie)
            logger.info(f"Processing {pretty}: {data} {media_type}{'' if data == 1 else 's'}")
        elif method in ["trakt_collection", "trakt_watchlist"]:
            movie_ids, show_ids = self._user_list(method[6:], data, is_movie)
            logger.info(f"Processing {pretty} {media_type}s for {data}")
        elif method == "trakt_list":
            movie_ids, show_ids = self._user_list(method[6:], data, is_movie)
            logger.info(f"Processing {pretty}: {data}")
        else:
            raise Failed(f"Trakt Error: Method {method} not supported")
        logger.debug("")
        logger.debug(f"{len(movie_ids)} TMDb IDs Found: {movie_ids}")
        logger.debug(f"{len(show_ids)} TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids
