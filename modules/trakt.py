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
from modules.tmdb import TMDbAPI

logger = logging.getLogger("Plex Meta Manager")

class TraktAPI:
    def __init__(self, params, authorization=None):
        self.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        self.aliases = {
            "trakt_trending": "Trakt Trending",
            "trakt_watchlist": "Trakt Watchlist",
            "trakt_list": "Trakt List"
        }
        self.client_id = params["client_id"]
        self.client_secret = params["client_secret"]
        self.config_path = params["config_path"]
        self.original_languages = None
        if params["original_languages"] is not None:
            self.original_languages = [x.strip().lower() for x in params["original_languages"].split(',')]
        self.authorization = authorization
        Trakt.configuration.defaults.client(self.client_id, self.client_secret)
        if not self.save_authorization(self.authorization):
            if not self.refresh_authorization():
                self.get_authorization()

    def get_authorization(self):
        url = Trakt["oauth"].authorize_url(self.redirect_uri)
        logger.info("Navigate to: {}".format(url))
        logger.info("If you get an OAuth error your client_id or client_secret is invalid")
        webbrowser.open(url, new=2)
        try:                                pin = util.logger_input("Trakt pin (case insensitive)", timeout=300).strip()
        except TimeoutExpired:              raise Failed("Input Timeout: Trakt pin required.")
        if not pin:                         raise Failed("Trakt Error: No input Trakt pin required.")
        new_authorization = Trakt["oauth"].token(pin, self.redirect_uri)
        if not new_authorization:
            raise Failed("Trakt Error: Invalid trakt pin. If you're sure you typed it in correctly your client_id or client_secret may be invalid")
        if not self.save_authorization(new_authorization):
            raise Failed("Trakt Error: New Authorization Failed")

    def check_authorization(self, authorization):
        try:
            with Trakt.configuration.oauth.from_response(authorization, refresh=True):
                if Trakt["users/settings"].get():
                    return True
        except ValueError: pass
        return False

    def refresh_authorization(self):
        if self.authorization and "refresh_token" in self.authorization and self.authorization["refresh_token"]:
            logger.info("Refreshing Access Token...")
            refreshed_authorization = Trakt["oauth"].token_refresh(self.authorization["refresh_token"], self.redirect_uri)
            return self.save_authorization(refreshed_authorization)
        return False

    def save_authorization(self, authorization):
        if authorization and self.check_authorization(authorization):
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
                logger.info("Saving authorization information to {}".format(self.config_path))
                yaml.round_trip_dump(config, open(self.config_path, "w"), indent=ind, block_seq_indent=bsi)
            self.authorization = authorization
            Trakt.configuration.defaults.oauth.from_response(self.authorization)
            return True
        return False

    def convert_tmdb_to_imdb(self, tmdb_id, is_movie=True):         return self.convert_id(tmdb_id, "tmdb", "imdb", "movie" if is_movie else "show")
    def convert_imdb_to_tmdb(self, imdb_id, is_movie=True):         return self.convert_id(imdb_id, "imdb", "tmdb", "movie" if is_movie else "show")
    def convert_tmdb_to_tvdb(self, tmdb_id):                        return self.convert_id(tmdb_id, "tmdb", "tvdb", "show")
    def convert_tvdb_to_tmdb(self, tvdb_id):                        return self.convert_id(tvdb_id, "tvdb", "tmdb", "show")
    def convert_tvdb_to_imdb(self, tvdb_id):                        return self.convert_id(tvdb_id, "tvdb", "imdb", "show")
    def convert_imdb_to_tvdb(self, imdb_id):                        return self.convert_id(imdb_id, "imdb", "tvdb", "show")

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def convert_id(self, external_id, from_source, to_source, media_type):
        lookup = Trakt["search"].lookup(external_id, from_source, media_type)
        if lookup:
            lookup = lookup[0] if isinstance(lookup, list) else lookup
            return lookup.get_key(to_source)
        else:
            raise Failed("No {} ID found for {} ID {}".format(to_source.upper().replace("B", "b"), from_source.upper().replace("B", "b"), external_id))

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def trending(self, amount, is_movie):
        return Trakt["movies" if is_movie else "shows"].trending(per_page=amount)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def watchlist(self, data, is_movie):
        items = Trakt["users/{}/watchlist".format(data)].movies() if is_movie else Trakt["users/{}/watchlist".format(data)].shows()
        if items is None:                   raise Failed("Trakt Error: No List found")
        else:                               return [i for i in items]

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def standard_list(self, data):
        try:                                items = Trakt[requests.utils.urlparse(data).path].items()
        except AttributeError:              items = None
        if items is None:                   raise Failed("Trakt Error: No List found")
        else:                               return items

    def validate_trakt_list(self, values):
        trakt_values = []
        for value in values:
            try:
                self.standard_list(value)
                trakt_values.append(value)
            except Failed as e:
                logger.error(e)
        if len(trakt_values) == 0:
            raise Failed("Trakt Error: No valid Trakt Lists in {}".format(value))
        return trakt_values

    def validate_trakt_watchlist(self, values, is_movie):
        trakt_values = []
        for value in values:
            try:
                self.watchlist(value, is_movie)
                trakt_values.append(value)
            except Failed as e:
                logger.error(e)
        if len(trakt_values) == 0:
            raise Failed("Trakt Error: No valid Trakt Watchlists in {}".format(value))
        return trakt_values

    def get_items(self, method, data, is_movie, tmdb, status_message=True):
        if status_message:
            logger.debug("Data: {}".format(data))
        pretty = self.aliases[method] if method in self.aliases else method
        media_type = "Movie" if is_movie else "Show"
        if method == "trakt_trending":
            trakt_items = self.trending(int(data), is_movie)
            if status_message:
                logger.info("Processing {}: {} {}{}".format(pretty, data, media_type, "" if data == 1 else "s"))
        else:
            if method == "trakt_watchlist":             trakt_items = self.watchlist(data, is_movie)
            elif method == "trakt_list":                trakt_items = self.standard_list(data)
            else:                                       raise Failed("Trakt Error: Method {} not supported".format(method))
            if status_message:                          logger.info("Processing {}: {}".format(pretty, data))
        show_ids = []
        movie_ids = []
        for trakt_item in trakt_items:            
            if isinstance(trakt_item, Movie):
                try:                    
                    tmdbid = int(trakt_item.get_key("tmdb"))
                    if self.original_languages is None:
                        movie_ids.append(tmdbid)
                        continue
                    movie = tmdb.get_movie(tmdbid)
                    #logger.info("--- Movie {} ({}), TMDB original_language ({})".format(trakt_item.title, trakt_item.year, movie.original_language))
                    if movie.original_language in self.original_languages:
                        movie_ids.append(tmdbid)
                    else:
                        logger.info("--- Skipped Movie {} ({}), TMDB original_language ({}) not in original_languages attribute ({})".format(trakt_item.title, trakt_item.year, movie.original_language, self.original_languages))
                except Failed as e:
                    logger.error(e)
            elif isinstance(trakt_item, Show) and trakt_item.pk[1] not in show_ids:                          show_ids.append(int(trakt_item.pk[1]))
            elif (isinstance(trakt_item, (Season, Episode))) and trakt_item.show.pk[1] not in show_ids:      show_ids.append(int(trakt_item.show.pk[1]))
        if status_message:
            logger.debug("Trakt {} Found: {}".format(media_type, trakt_items))
            logger.debug("TMDb IDs Found: {}".format(movie_ids))
            logger.debug("TVDb IDs Found: {}".format(show_ids))        
        return movie_ids, show_ids
