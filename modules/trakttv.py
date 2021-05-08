import logging, requests, webbrowser
from modules import util
from modules.util import Failed, TimeoutExpired
from retrying import retry
from ruamel import yaml
from trakt import Trakt
from trakt.objects.episode import Episode
from trakt.objects.movie import Movie
from trakt.objects.season import Season
from trakt.objects.show import Show

logger = logging.getLogger("Plex Meta Manager")

builders = [
    "trakt_collected",
    "trakt_collection",
    "trakt_list",
    "trakt_list_details",
    "trakt_popular",
    "trakt_recommended",
    "trakt_trending",
    "trakt_watched",
    "trakt_watchlist"
]

class TraktAPI:
    def __init__(self, params, authorization=None):
        self.base_url = "https://api.trakt.tv"
        self.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        self.aliases = {
            "trakt_trending": "Trakt Trending",
            "trakt_watchlist": "Trakt Watchlist",
            "trakt_list": "Trakt List"
        }
        self.client_id = params["client_id"]
        self.client_secret = params["client_secret"]
        self.config_path = params["config_path"]
        self.authorization = authorization
        Trakt.configuration.defaults.client(self.client_id, self.client_secret)
        if not self._save(self.authorization):
            if not self._refresh():
                self._authorization()

    def _authorization(self):
        url = Trakt["oauth"].authorize_url(self.redirect_uri)
        logger.info(f"Navigate to: {url}")
        logger.info("If you get an OAuth error your client_id or client_secret is invalid")
        webbrowser.open(url, new=2)
        try:                                pin = util.logger_input("Trakt pin (case insensitive)", timeout=300).strip()
        except TimeoutExpired:              raise Failed("Input Timeout: Trakt pin required.")
        if not pin:                         raise Failed("Trakt Error: No input Trakt pin required.")
        new_authorization = Trakt["oauth"].token(pin, self.redirect_uri)
        if not new_authorization:
            raise Failed("Trakt Error: Invalid trakt pin. If you're sure you typed it in correctly your client_id or client_secret may be invalid")
        if not self._save(new_authorization):
            raise Failed("Trakt Error: New Authorization Failed")

    def _check(self, authorization):
        try:
            with Trakt.configuration.oauth.from_response(authorization, refresh=True):
                if Trakt["users/settings"].get():
                    return True
        except ValueError: pass
        return False

    def _refresh(self):
        if self.authorization and "refresh_token" in self.authorization and self.authorization["refresh_token"]:
            logger.info("Refreshing Access Token...")
            refreshed_authorization = Trakt["oauth"].token_refresh(self.authorization["refresh_token"], self.redirect_uri)
            return self._save(refreshed_authorization)
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
            Trakt.configuration.defaults.oauth.from_response(self.authorization)
            return True
        return False

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def convert(self, external_id, from_source, to_source, media_type):
        lookup = Trakt["search"].lookup(external_id, from_source, media_type)
        if lookup:
            lookup = lookup[0] if isinstance(lookup, list) else lookup
            if lookup.get_key(to_source):
                return lookup.get_key(to_source) if to_source == "imdb" else int(lookup.get_key(to_source))
        raise Failed(f"Trakt Error: No {to_source.upper().replace('B', 'b')} ID found for {from_source.upper().replace('B', 'b')} ID: {external_id}")

    def collection(self, data, is_movie):
        return self._user_list("collection", data, is_movie)

    def _watchlist(self, data, is_movie):
        return self._user_list("watchlist", data, is_movie)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def _user_list(self, list_type, data, is_movie):
        items = Trakt[f"users/{data}/{list_type}"].movies() if is_movie else Trakt[f"users/{data}/{list_type}"].shows()
        if items is None:                   raise Failed("Trakt Error: No List found")
        else:                               return [i for i in items]

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def standard_list(self, data):
        try:                                trakt_list = Trakt[requests.utils.urlparse(data).path].get()
        except AttributeError:              trakt_list = None
        if trakt_list is None:              raise Failed("Trakt Error: No List found")
        else:                               return trakt_list

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _request(self, url):
        return requests.get(url, headers={"Content-Type": "application/json", "trakt-api-version": "2", "trakt-api-key": self.client_id}).json()

    def _collection(self, username, is_movie):
        items = self._request(f"{self.base_url}/users/{username}/collection/{'movies' if is_movie else 'shows'}")
        if is_movie:                                return [item["movie"]["ids"]["tmdb"] for item in items], []
        else:                                       return [], [item["show"]["ids"]["tvdb"] for item in items]

    def _pagenation(self, pagenation, amount, is_movie):
        items = self._request(f"{self.base_url}/{'movies' if is_movie else 'shows'}/{pagenation}?limit={amount}")
        if pagenation == "popular" and is_movie:    return [item["ids"]["tmdb"] for item in items], []
        elif pagenation == "popular":               return [], [item["ids"]["tvdb"] for item in items]
        elif is_movie:                              return [item["movie"]["ids"]["tmdb"] for item in items], []
        else:                                       return [], [item["show"]["ids"]["tvdb"] for item in items]

    def validate_trakt(self, values, trakt_type=None, is_movie=None):
        trakt_values = []
        for value in values:
            try:
                if trakt_type == "watchlist" and is_movie is not None:
                    self._watchlist(value, is_movie)
                elif trakt_type == "collection" and is_movie is not None:
                    self._collection(value, is_movie)
                else:
                    self.standard_list(value)
                trakt_values.append(value)
            except Failed as e:
                logger.error(e)
        if len(trakt_values) == 0:
            if trakt_type == "watchlist" and is_movie is not None:
                raise Failed(f"Trakt Error: No valid Trakt Watchlists in {values}")
            elif trakt_type == "collection" and is_movie is not None:
                raise Failed(f"Trakt Error: No valid Trakt Collections in {values}")
            else:
                raise Failed(f"Trakt Error: No valid Trakt Lists in {values}")
        return trakt_values

    def get_items(self, method, data, is_movie, status_message=True):
        if status_message:
            logger.debug(f"Data: {data}")
        pretty = self.aliases[method] if method in self.aliases else method
        media_type = "Movie" if is_movie else "Show"
        if method in ["trakt_trending", "trakt_popular", "trakt_recommended", "trakt_watched", "trakt_collected"]:
            movie_ids, show_ids = self._pagenation(method[6:], data, is_movie)
            if status_message:
                logger.info(f"Processing {pretty}: {data} {media_type}{'' if data == 1 else 's'}")
        elif method == "trakt_collection":
            movie_ids, show_ids = self._collection(data, is_movie)
            if status_message:
                logger.info(f"Processing {pretty} {media_type}s for {data}")
        else:
            show_ids = []
            movie_ids = []
            if method == "trakt_watchlist":             trakt_items = self._watchlist(data, is_movie)
            elif method == "trakt_list":                trakt_items = self.standard_list(data).items()
            else:                                       raise Failed(f"Trakt Error: Method {method} not supported")
            if status_message:                          logger.info(f"Processing {pretty}: {data}")
            for trakt_item in trakt_items:
                if isinstance(trakt_item, Movie):
                    movie_ids.append(int(trakt_item.get_key("tmdb")))
                elif isinstance(trakt_item, Show) and trakt_item.pk[1] not in show_ids:
                    show_ids.append(int(trakt_item.pk[1]))
                elif (isinstance(trakt_item, (Season, Episode))) and trakt_item.show.pk[1] not in show_ids:
                    show_ids.append(int(trakt_item.show.pk[1]))
            if status_message:
                logger.debug(f"Trakt {media_type} Found: {trakt_items}")
        if status_message:
            logger.debug(f"TMDb IDs Found: {movie_ids}")
            logger.debug(f"TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids
