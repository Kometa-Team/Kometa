import logging, os, random, sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

class Cache:
    def __init__(self, config_path, expiration):
        cache = f"{os.path.splitext(config_path)[0]}.cache"
        with sqlite3.connect(cache) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='guids'")
                if cursor.fetchone()[0] == 0:
                    logger.info(f"Initializing cache database at {cache}")
                else:
                    logger.info(f"Using cache database at {cache}")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS guids (
                    INTEGER PRIMARY KEY,
                    plex_guid TEXT UNIQUE,
                    tmdb_id TEXT,
                    imdb_id TEXT,
                    tvdb_id TEXT,
                    anidb_id TEXT,
                    mal_id TEXT,
                    expiration_date TEXT,
                    media_type TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS imdb_map (
                    INTEGER PRIMARY KEY,
                    imdb_id TEXT UNIQUE,
                    t_id TEXT,
                    expiration_date TEXT,
                    media_type TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS omdb_data (
                    INTEGER PRIMARY KEY,
                    imdb_id TEXT UNIQUE,
                    title TEXT,
                    year INTEGER,
                    content_rating TEXT,
                    genres TEXT,
                    imdb_rating REAL,
                    imdb_votes INTEGER,
                    metacritic_rating INTEGER,
                    type TEXT,
                    expiration_date TEXT)"""
                )
        self.expiration = expiration
        self.cache_path = cache
        self.omdb_expiration = expiration

    def get_ids_from_imdb(self, imdb_id):
        tmdb_id, tmdb_expired = self.get_tmdb_id("movie", imdb_id=imdb_id)
        tvdb_id, tvdb_expired = self.get_tvdb_id("show", imdb_id=imdb_id)
        return tmdb_id, tvdb_id

    def get_tmdb_id(self, media_type, plex_guid=None, imdb_id=None, tvdb_id=None, anidb_id=None, mal_id=None):
        return self.get_id_from(media_type, "tmdb_id", plex_guid=plex_guid, imdb_id=imdb_id, tvdb_id=tvdb_id, anidb_id=anidb_id, mal_id=mal_id)

    def get_imdb_id(self, media_type, plex_guid=None, tmdb_id=None, tvdb_id=None, anidb_id=None, mal_id=None):
        return self.get_id_from(media_type, "imdb_id", plex_guid=plex_guid, tmdb_id=tmdb_id, tvdb_id=tvdb_id, anidb_id=anidb_id, mal_id=mal_id)

    def get_tvdb_id(self, media_type, plex_guid=None, tmdb_id=None, imdb_id=None, anidb_id=None, mal_id=None):
        return self.get_id_from(media_type, "tvdb_id", plex_guid=plex_guid, tmdb_id=tmdb_id, imdb_id=imdb_id, anidb_id=anidb_id, mal_id=mal_id)

    def get_anidb_id(self, media_type, plex_guid=None, tmdb_id=None, imdb_id=None, tvdb_id=None, mal_id=None):
        return self.get_id_from(media_type, "anidb_id", plex_guid=plex_guid, tmdb_id=tmdb_id, imdb_id=imdb_id, tvdb_id=tvdb_id, mal_id=mal_id)

    def get_mal_id(self, media_type, plex_guid=None, tmdb_id=None, imdb_id=None, tvdb_id=None, anidb_id=None):
        return self.get_id_from(media_type, "anidb_id", plex_guid=plex_guid, tmdb_id=tmdb_id, imdb_id=imdb_id, tvdb_id=tvdb_id, anidb_id=anidb_id)

    def get_id_from(self, media_type, id_from, plex_guid=None, tmdb_id=None, imdb_id=None, tvdb_id=None, anidb_id=None, mal_id=None):
        if plex_guid:           return self.get_id(media_type, "plex_guid", id_from, plex_guid)
        elif tmdb_id:           return self.get_id(media_type, "tmdb_id", id_from, tmdb_id)
        elif imdb_id:           return self.get_id(media_type, "imdb_id", id_from, imdb_id)
        elif tvdb_id:           return self.get_id(media_type, "tvdb_id", id_from, tvdb_id)
        elif anidb_id:          return self.get_id(media_type, "anidb_id", id_from, anidb_id)
        elif mal_id:            return self.get_id(media_type, "mal_id", id_from, mal_id)
        else:                   return None, None

    def get_id(self, media_type, from_id, to_id, key):
        id_to_return = None
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM guids WHERE {from_id} = ? AND media_type = ?", (key, media_type))
                row = cursor.fetchone()
                if row and row[to_id]:
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    id_to_return = int(row[to_id])
                    expired = time_between_insertion.days > self.expiration
        return id_to_return, expired

    def get_ids(self, media_type, plex_guid=None, tmdb_id=None, imdb_id=None, tvdb_id=None):
        ids_to_return = {}
        expired = None
        if plex_guid:
            key = plex_guid
            key_type = "plex_guid"
        elif tmdb_id:
            key = tmdb_id
            key_type = "tmdb_id"
        elif imdb_id:
            key = imdb_id
            key_type = "imdb_id"
        elif tvdb_id:
            key = tvdb_id
            key_type = "tvdb_id"
        else:
            raise Failed("ID Required")
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM guids WHERE {key_type} = ? AND media_type = ?", (key, media_type))
                row = cursor.fetchone()
                if row:
                    if row["plex_guid"]:                    ids_to_return["plex"] = row["plex_guid"]
                    if row["tmdb_id"]:                      ids_to_return["tmdb"] = int(row["tmdb_id"])
                    if row["imdb_id"]:                      ids_to_return["imdb"] = row["imdb_id"]
                    if row["tvdb_id"]:                      ids_to_return["tvdb"] = int(row["tvdb_id"])
                    if row["anidb_id"]:                     ids_to_return["anidb"] = int(row["anidb_id"])
                    if row["mal_id"]:                       ids_to_return["mal"] = int(row["mal_id"])
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > self.expiration
        return ids_to_return, expired

    def update_guid(self, media_type, plex_guid, tmdb_id, imdb_id, tvdb_id, anidb_id, mal_id, expired):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO guids(plex_guid) VALUES(?)", (plex_guid,))
                cursor.execute(
                """UPDATE guids SET
                tmdb_id = ?,
                imdb_id = ?,
                tvdb_id = ?,
                anidb_id = ?,
                mal_id = ?,
                expiration_date = ?,
                media_type = ?
                WHERE plex_guid = ?""", (tmdb_id, imdb_id, tvdb_id, anidb_id, mal_id, expiration_date.strftime("%Y-%m-%d"), media_type, plex_guid))
                if imdb_id and (tmdb_id or tvdb_id):
                    cursor.execute("INSERT OR IGNORE INTO imdb_map(imdb_id) VALUES(?)", (imdb_id,))
                    cursor.execute("UPDATE imdb_map SET t_id = ?, expiration_date = ?, media_type = ? WHERE imdb_id = ?", (tmdb_id if media_type == "movie" else tvdb_id, expiration_date.strftime("%Y-%m-%d"), media_type, imdb_id))

    def get_tmdb_from_imdb(self, imdb_id):              return self.query_imdb_map("movie", imdb_id)
    def get_tvdb_from_imdb(self, imdb_id):              return self.query_imdb_map("show", imdb_id)
    def query_imdb_map(self, media_type, imdb_id):
        id_to_return = None
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM imdb_map WHERE imdb_id = ? AND media_type = ?", (imdb_id, media_type))
                row = cursor.fetchone()
                if row and row["t_id"]:
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    id_to_return = int(row["t_id"])
                    expired = time_between_insertion.days > self.expiration
        return id_to_return, expired

    def update_imdb(self, media_type, expired, imdb_id, t_id):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO imdb_map(imdb_id) VALUES(?)", (imdb_id,))
                cursor.execute("UPDATE imdb_map SET t_id = ?, expiration_date = ?, media_type = ? WHERE imdb_id = ?", (t_id, expiration_date.strftime("%Y-%m-%d"), media_type, imdb_id))

    def query_omdb(self, imdb_id):
        omdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM omdb_data WHERE imdb_id = ?", (imdb_id,))
                row = cursor.fetchone()
                if row:
                    omdb_dict["imdbID"] = row["imdb_id"] if row["imdb_id"] else None
                    omdb_dict["Title"] = row["title"] if row["title"] else None
                    omdb_dict["Year"] = row["year"] if row["year"] else None
                    omdb_dict["Rated"] = row["content_rating"] if row["content_rating"] else None
                    omdb_dict["Genre"] = row["genres"] if row["genres"] else None
                    omdb_dict["imdbRating"] = row["imdb_rating"] if row["imdb_rating"] else None
                    omdb_dict["imdbVotes"] = row["imdb_votes"] if row["imdb_votes"] else None
                    omdb_dict["Metascore"] = row["metacritic_rating"] if row["metacritic_rating"] else None
                    omdb_dict["Type"] = row["type"] if row["type"] else None
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > self.omdb_expiration
        return omdb_dict, expired

    def update_omdb(self, expired, omdb):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.omdb_expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO omdb_data(imdb_id) VALUES(?)", (omdb.imdb_id,))
                update_sql = "UPDATE omdb_data SET title = ?, year = ?, content_rating = ?, genres = ?, imdb_rating = ?, imdb_votes = ?, metacritic_rating = ?, type = ?, expiration_date = ? WHERE imdb_id = ?"
                cursor.execute(update_sql, (omdb.title, omdb.year, omdb.content_rating, omdb.genres_str, omdb.imdb_rating, omdb.imdb_votes, omdb.metacritic_rating, omdb.type, expiration_date.strftime("%Y-%m-%d"), omdb.imdb_id))
