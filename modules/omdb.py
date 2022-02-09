import logging
from modules import util
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

base_url = "http://www.omdbapi.com/"

class OMDbObj:
    def __init__(self, imdb_id, data):
        self._imdb_id = imdb_id
        self._data = data
        if data["Response"] == "False":
            raise Failed(f"OMDb Error: {data['Error']} IMDb ID: {imdb_id}")
        self.title = data["Title"]
        try:
            self.year = int(data["Year"])
        except (ValueError, TypeError):
            self.year = None
        self.content_rating = data["Rated"]
        self.genres = util.get_list(data["Genre"])
        self.genres_str = data["Genre"]
        try:
            self.imdb_rating = float(data["imdbRating"])
        except (ValueError, TypeError):
            self.imdb_rating = None
        try:
            self.imdb_votes = int(str(data["imdbVotes"]).replace(',', ''))
        except (ValueError, TypeError):
            self.imdb_votes = None
        try:
            self.metacritic_rating = int(data["Metascore"])
        except (ValueError, TypeError):
            self.metacritic_rating = None
        self.imdb_id = data["imdbID"]
        self.type = data["Type"]
        try:
            self.series_id = data["seriesID"]
        except (ValueError, TypeError, KeyError):
            self.series_id = None
        try:
            self.season_num = int(data["Season"])
        except (ValueError, TypeError, KeyError):
            self.season_num = None
        try:
            self.episode_num = int(data["Episode"])
        except (ValueError, TypeError, KeyError):
            self.episode_num = None


class OMDb:
    def __init__(self, config, params):
        self.config = config
        self.apikey = params["apikey"]
        self.expiration = params["expiration"]
        self.limit = False
        self.get_omdb("tt0080684", ignore_cache=True)

    def get_omdb(self, imdb_id, ignore_cache=False):
        expired = None
        if self.config.Cache and not ignore_cache:
            omdb_dict, expired = self.config.Cache.query_omdb(imdb_id, self.expiration)
            if omdb_dict and expired is False:
                return OMDbObj(imdb_id, omdb_dict)
        if self.config.trace_mode:
            logger.debug(f"IMDb ID: {imdb_id}")
        response = self.config.get(base_url, params={"i": imdb_id, "apikey": self.apikey})
        if response.status_code < 400:
            omdb = OMDbObj(imdb_id, response.json())
            if self.config.Cache and not ignore_cache:
                self.config.Cache.update_omdb(expired, omdb, self.expiration)
            return omdb
        else:
            error = response.json()['Error']
            if error == "Request limit reached!":
                self.limit = True
            raise Failed(f"OMDb Error: {error}")
