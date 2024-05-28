from datetime import datetime
from modules import util
from modules.util import Failed
from json import JSONDecodeError

logger = util.logger

base_url = "http://www.omdbapi.com/"

class OMDbObj:
    def __init__(self, imdb_id, data):
        self._imdb_id = imdb_id
        self._data = data
        if data["Response"] == "False":
            raise Failed(f"OMDb Error: {data['Error']} IMDb ID: {imdb_id}")
        def _parse(key, is_int=False, is_float=False, is_date=False, replace=None):
            try:
                value = str(data[key]).replace(replace, '') if replace else data[key]
                if is_int:
                    return int(value)
                elif is_float:
                    return float(value)
                elif is_date:
                    return datetime.strptime(value, "%d %b %Y")
                else:
                    return value
            except (ValueError, TypeError, KeyError):
                return None
        self.title = _parse("Title")
        self.year = _parse("Year", is_int=True)
        self.released = _parse("Released", is_date=True)
        self.content_rating = _parse("Rated")
        self.genres_str = _parse("Genre")
        self.genres = util.get_list(self.genres_str)
        self.imdb_rating = _parse("imdbRating", is_float=True)
        self.imdb_votes = _parse("imdbVotes", is_int=True, replace=",")
        self.metacritic_rating = _parse("Metascore", is_int=True)
        self.imdb_id = _parse("imdbID")
        self.type = _parse("Type")
        self.series_id = _parse("seriesID")
        self.season_num = _parse("Season", is_int=True)
        self.episode_num = _parse("Episode", is_int=True)


class OMDb:
    def __init__(self, requests, cache, params):
        self.requests = requests
        self.cache = cache
        self.apikey = params["apikey"]
        self.expiration = params["expiration"]
        self.limit = False
        logger.secret(self.apikey)
        self.get_omdb("tt0080684", ignore_cache=True)

    def get_omdb(self, imdb_id, ignore_cache=False):
        expired = None
        if self.cache and not ignore_cache:
            omdb_dict, expired = self.cache.query_omdb(imdb_id, self.expiration)
            if omdb_dict and expired is False:
                return OMDbObj(imdb_id, omdb_dict)
        logger.trace(f"IMDb ID: {imdb_id}")
        response = self.requests.get(base_url, params={"i": imdb_id, "apikey": self.apikey})
        if response.status_code < 400:
            omdb = OMDbObj(imdb_id, response.json())
            if self.cache and not ignore_cache:
                self.cache.update_omdb(expired, omdb, self.expiration)
            return omdb
        else:
            try:
                error = response.json()['Error']
                if error == "Request limit reached!":
                    self.limit = True
            except JSONDecodeError:
                error = f"Invalid JSON: {response.content}"
            raise Failed(f"OMDb Error: {error}")
