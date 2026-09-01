from datetime import datetime
from json import JSONDecodeError

from modules import util
from modules.util import Failed

logger = util.logger

base_url = "http://www.omdbapi.com/"


class OMDbObj:
    def __init__(self, imdb_id, data):
        self._imdb_id = imdb_id
        self._data = data
        self._invalid_rating_values = []
        if data["Response"] == "False":
            raise Failed(f"OMDb Error: {data['Error']} IMDb ID: {imdb_id}")

        def _parse(key, is_int=False, is_float=False, is_date=False, replace=None):
            try:
                value = str(data[key]).replace(replace, "") if replace else data[key]
                if is_int:
                    return int(value)
                elif is_float:
                    return float(value)
                elif is_date:
                    return datetime.strptime(value, "%d %b %Y")
                elif value == "N/A":
                    return None
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
        self.rotten_tomatoes = None
        try:
            for rating in data["Ratings"]:
                if rating["Source"] == "Rotten Tomatoes":
                    data["tempRT"] = rating["Value"]  # This is a hack to allow _parse to work without changes
                    self.rotten_tomatoes = _parse("tempRT", is_int=True, replace="%")
                    break
        except KeyError:
            pass

        for source, value, maximum, replace in [
            ("imdb", data.get("imdbRating"), 10, None),
            ("metacritic", data.get("Metascore"), 100, None),
            ("tomatoes", data.get("tempRT"), 100, "%"),
        ]:
            if replace and isinstance(value, str):
                value = value.replace(replace, "")
            if not util.is_missing_rating(value) and not util.is_valid_rating(value, maximum=maximum):
                self._invalid_rating_values.append((source, value))

        self.imdb_id = _parse("imdbID")
        self.type = _parse("Type")
        self.series_id = _parse("seriesID")
        self.season_num = _parse("Season", is_int=True)
        self.episode_num = _parse("Episode", is_int=True)
        if logger:
            for source, value in self._invalid_rating_values:
                logger.warning(f"OMDb Warning: {source} rating value {value} is invalid; expected a finite value in the provider's supported range; response will not be cached")

    @property
    def ratings_valid(self):
        return not self._invalid_rating_values


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
                cached = OMDbObj(imdb_id, omdb_dict)
                if cached.ratings_valid:
                    return cached
                expired = True
        logger.trace(f"IMDb ID: {imdb_id}")
        response = self.requests.get(base_url, params={"apikey": self.apikey, "i": imdb_id})
        if response.status_code < 400:
            omdb = OMDbObj(imdb_id, response.json())
            if self.cache and not ignore_cache and omdb.ratings_valid:
                self.cache.update_omdb(expired, omdb, self.expiration)
            return omdb
        else:
            try:
                error = response.json()["Error"]
                if error == "Request limit reached!":
                    self.limit = True
            except JSONDecodeError:
                error = f"Invalid JSON: {response.content}"
            raise Failed(f"OMDb Error: {error}")
