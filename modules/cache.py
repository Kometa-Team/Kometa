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
                cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='guid_map'")
                if cursor.fetchone()[0] == 0:
                    logger.info(f"Initializing cache database at {cache}")
                else:
                    logger.info(f"Using cache database at {cache}")
                cursor.execute("DROP TABLE IF EXISTS guids")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS guid_map (
                    INTEGER PRIMARY KEY,
                    plex_guid TEXT UNIQUE,
                    t_id TEXT,
                    media_type TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS imdb_map (
                    INTEGER PRIMARY KEY,
                    imdb_id TEXT UNIQUE,
                    t_id TEXT,
                    media_type TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS letterboxd_map (
                    INTEGER PRIMARY KEY,
                    letterboxd_id TEXT UNIQUE,
                    tmdb_id TEXT,
                    expiration_date TEXT)"""
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
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS anime_map (
                    INTEGER PRIMARY KEY,
                    anidb TEXT UNIQUE,
                    anilist TEXT,
                    myanimelist TEXT,
                    kitsu TEXT,
                    expiration_date TEXT)"""
                )
        self.expiration = expiration
        self.cache_path = cache

    def query_guid_map(self, plex_guid):
        id_to_return = None
        media_type = None
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM guid_map WHERE plex_guid = ?", (plex_guid,))
                row = cursor.fetchone()
                if row:
                    time_between_insertion = datetime.now() - datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    id_to_return = row["t_id"]
                    media_type = row["media_type"]
                    expired = time_between_insertion.days > self.expiration
        return id_to_return, media_type, expired

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
                cursor.execute(f"SELECT * FROM guid_map WHERE {key_type} = ? AND media_type = ?", (key, media_type))
                row = cursor.fetchone()
                if row:
                    if row["plex_guid"]:                    ids_to_return["plex"] = row["plex_guid"]
                    if row["tmdb_id"]:                      ids_to_return["tmdb"] = int(row["tmdb_id"])
                    if row["imdb_id"]:                      ids_to_return["imdb"] = row["imdb_id"]
                    if row["tvdb_id"]:                      ids_to_return["tvdb"] = int(row["tvdb_id"])
                    if row["anidb_id"]:                     ids_to_return["anidb"] = int(row["anidb_id"])
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > self.expiration
        return ids_to_return, expired

    def update_guid(self, media_type, plex_guid, t_id, expired):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO guid_map(plex_guid) VALUES(?)", (plex_guid,))
                cursor.execute("UPDATE guid_map SET t_id = ?, media_type = ?, expiration_date = ? WHERE plex_guid = ?", (t_id, media_type, expiration_date.strftime("%Y-%m-%d"), plex_guid))

    def get_tmdb_from_imdb(self, imdb_id):              return self._imdb_map("movie", imdb_id)
    def get_tvdb_from_imdb(self, imdb_id):              return self._imdb_map("show", imdb_id)
    def _imdb_map(self, media_type, imdb_id):
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

    def query_letterboxd_map(self, letterboxd_id):
        tmdb_id = None
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM letterboxd_map WHERE letterboxd_id = ?", (letterboxd_id, ))
                row = cursor.fetchone()
                if row and row["tmdb_id"]:
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    tmdb_id = int(row["tmdb_id"])
                    expired = time_between_insertion.days > self.expiration
        return tmdb_id, expired

    def update_letterboxd(self, expired, letterboxd_id, tmdb_id):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO letterboxd_map(letterboxd_id) VALUES(?)", (letterboxd_id,))
                cursor.execute("UPDATE letterboxd_map SET tmdb_id = ?, expiration_date = ? WHERE letterboxd_id = ?", (tmdb_id, expiration_date.strftime("%Y-%m-%d"), letterboxd_id))

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
                    expired = time_between_insertion.days > self.expiration
        return omdb_dict, expired

    def update_omdb(self, expired, omdb):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO omdb_data(imdb_id) VALUES(?)", (omdb.imdb_id,))
                update_sql = "UPDATE omdb_data SET title = ?, year = ?, content_rating = ?, genres = ?, imdb_rating = ?, imdb_votes = ?, metacritic_rating = ?, type = ?, expiration_date = ? WHERE imdb_id = ?"
                cursor.execute(update_sql, (omdb.title, omdb.year, omdb.content_rating, omdb.genres_str, omdb.imdb_rating, omdb.imdb_votes, omdb.metacritic_rating, omdb.type, expiration_date.strftime("%Y-%m-%d"), omdb.imdb_id))

    def query_anime_map(self, anime_id, id_type):
        ids = None
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM anime_map WHERE {id_type} = ?", (anime_id, ))
                row = cursor.fetchone()
                if row and row["anidb"]:
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    ids = {
                        "anilist": int(row["anilist"]) if row["anilist"] else None,
                        "anidb": int(row["anidb"]) if row["anidb"] else None,
                        "myanimelist": int(row["myanimelist"]) if row["myanimelist"] else None,
                        "kitsu": int(row["kitsu"]) if row["kitsu"] else None
                    }
                    expired = time_between_insertion.days > self.expiration
        return ids, expired

    def update_anime(self, expired, anime_ids):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO anime_map(anidb) VALUES(?)", (anime_ids["anidb"],))
                cursor.execute("UPDATE anime_map SET anilist = ?, myanimelist = ?, kitsu = ?, expiration_date = ? WHERE anidb = ?", (anime_ids["anidb"], anime_ids["myanimelist"], anime_ids["kitsu"], expiration_date.strftime("%Y-%m-%d"), anime_ids["anidb"]))
