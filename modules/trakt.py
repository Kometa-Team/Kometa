import logging, requests, webbrowser
from modules import util
from modules.util import Failed, TimeoutExpired
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
redirect_uri_encoded = redirect_uri.replace(":", "%3A")
base_url = "https://api.trakt.tv"
builders = [
    "trakt_collected_daily", "trakt_collected_weekly", "trakt_collected_monthly", "trakt_collected_yearly", "trakt_collected_all",
    "trakt_recommended_daily", "trakt_recommended_weekly", "trakt_recommended_monthly", "trakt_recommended_yearly", "trakt_recommended_all",
    "trakt_watched_daily", "trakt_watched_weekly", "trakt_watched_monthly", "trakt_watched_yearly", "trakt_watched_all",
    "trakt_collection", "trakt_list", "trakt_list_details", "trakt_popular", "trakt_trending", "trakt_watchlist"
]
sorts = [
    "rank", "added", "title", "released", "runtime", "popularity",
    "percentage", "votes", "random", "my_rating", "watched", "collected"
]
id_translation = {"movie": "tmdb", "show": "tvdb", "season": "TVDb Season", "episode": "TVDb Episode"}

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
        output_json = []
        pages = 1
        current = 1
        if self.config.trace_mode:
            logger.debug(f"URL: {base_url}{url}")
        while current <= pages:
            if pages == 1:
                response = self.config.get(f"{base_url}{url}", headers=headers)
                if "X-Pagination-Page-Count" in response.headers and "?" not in url:
                    pages = int(response.headers["X-Pagination-Page-Count"])
            else:
                response = self.config.get(f"{base_url}{url}?page={current}", headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                if self.config.trace_mode:
                    logger.debug(f"Response: {json_data}")
                if isinstance(json_data, dict):
                    return json_data
                else:
                    output_json.extend(response.json())
            else:
                raise Failed(f"({response.status_code}) {response.reason}")
            current += 1
        return output_json

    def user_ratings(self, is_movie):
        media = "movie" if is_movie else "show"
        id_type = "tmdb" if is_movie else "tvdb"
        return {int(i[media]["ids"][id_type]): i["rating"] for i in self._request(f"/users/me/ratings/{media}s")}

    def convert(self, external_id, from_source, to_source, media_type):
        path = f"/search/{from_source}/{external_id}"
        if from_source in ["tmdb", "tvdb"]:
            path = f"{path}?type={media_type}"
        lookup = self._request(path)
        if lookup and media_type in lookup[0] and to_source in lookup[0][media_type]["ids"]:
            return lookup[0][media_type]["ids"][to_source]
        raise Failed(f"Trakt Error: No {to_source.upper().replace('B', 'b')} ID found for {from_source.upper().replace('B', 'b')} ID: {external_id}")

    def list_description(self, data):
        try:
            return self._request(requests.utils.urlparse(data).path)["description"]
        except Failed:
            raise Failed(f"Trakt Error: List {data} not found")

    def _parse(self, items, typeless=False, item_type=None):
        ids = []
        for item in items:
            if typeless:
                data = item
                current_type = None
            elif item_type:
                data = item[item_type]
                current_type = item_type
            elif "type" in item and item["type"] in id_translation:
                data = item["movie" if item["type"] == "movie" else "show"]
                current_type = item["type"]
            else:
                continue
            id_type = "tmdb" if current_type == "movie" else "tvdb"
            if id_type in data["ids"] and data["ids"][id_type]:
                final_id = data["ids"][id_type]
                if current_type == "episode":
                    final_id = f"{final_id}_{item[current_type]['season']}"
                if current_type in ["episode", "season"]:
                    final_id = f"{final_id}_{item[current_type]['number']}"
                final_type = f"{id_type}_{current_type}" if current_type in ["episode", "season"] else id_type
                ids.append((final_id, final_type))
            else:
                logger.error(f"Trakt Error: No {id_type.upper().replace('B', 'b')} ID found for {data['title']} ({data['year']})")
        return ids

    def _user_list(self, data):
        try:
            items = self._request(f"{requests.utils.urlparse(data).path}/items")
        except Failed:
            raise Failed(f"Trakt Error: List {data} not found")
        if len(items) == 0:
            raise Failed(f"Trakt Error: List {data} is empty")
        return self._parse(items)

    def _user_items(self, list_type, data, is_movie):
        try:
            items = self._request(f"/users/{data}/{list_type}/{'movies' if is_movie else 'shows'}")
        except Failed:
            raise Failed(f"Trakt Error: User {data} not found")
        if len(items) == 0:
            raise Failed(f"Trakt Error: {data}'s {list_type.capitalize()} is empty")
        return self._parse(items, item_type="movie" if is_movie else "show")

    def _pagenation(self, pagenation, amount, is_movie):
        items = self._request(f"/{'movies' if is_movie else 'shows'}/{pagenation}?limit={amount}")
        return self._parse(items, typeless=pagenation == "popular", item_type="movie" if is_movie else "show")

    def validate_trakt(self, trakt_lists, is_movie, trakt_type="list"):
        values = util.get_list(trakt_lists, split=False)
        trakt_values = []
        for value in values:
            try:
                if trakt_type == "list":
                    self._user_list(value)
                else:
                    self._user_items(trakt_type, value, is_movie)
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

    def get_trakt_ids(self, method, data, is_movie):
        pretty = method.replace("_", " ").title()
        media_type = "Movie" if is_movie else "Show"
        if method.startswith(("trakt_trending", "trakt_popular", "trakt_recommended", "trakt_watched", "trakt_collected")):
            logger.info(f"Processing {pretty}: {data} {media_type}{'' if data == 1 else 's'}")
            terms = method.split("_")
            return self._pagenation(f"{terms[1]}{f'/{terms[2]}' if len(terms) > 2 else ''}", data, is_movie)
        elif method in ["trakt_collection", "trakt_watchlist"]:
            logger.info(f"Processing {pretty} {media_type}s for {data}")
            return self._user_items(method[6:], data, is_movie)
        elif method == "trakt_list":
            logger.info(f"Processing {pretty}: {data}")
            return self._user_list(data)
        else:
            raise Failed(f"Trakt Error: Method {method} not supported")
