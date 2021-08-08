import logging, os, random, sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from modules import util

logger = logging.getLogger("Plex Meta Manager")

class Cache:
    def __init__(self, config_path, expiration):
        self.cache_path = f"{os.path.splitext(config_path)[0]}.cache"
        self.expiration = expiration
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='guid_map'")
                if cursor.fetchone()[0] == 0:
                    logger.info(f"Initializing cache database at {self.cache_path}")
                else:
                    logger.info(f"Using cache database at {self.cache_path}")
                cursor.execute("DROP TABLE IF EXISTS guids")
                cursor.execute("DROP TABLE IF EXISTS guid_map")
                cursor.execute("DROP TABLE IF EXISTS imdb_to_tvdb_map")
                cursor.execute("DROP TABLE IF EXISTS tmdb_to_tvdb_map")
                cursor.execute("DROP TABLE IF EXISTS imdb_map")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS guids_map (
                    key INTEGER PRIMARY KEY,
                    plex_guid TEXT UNIQUE,
                    t_id TEXT,
                    imdb_id TEXT,
                    media_type TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS imdb_to_tmdb_map (
                    key INTEGER PRIMARY KEY,
                    imdb_id TEXT UNIQUE,
                    tmdb_id TEXT,
                    media_type TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS imdb_to_tvdb_map2 (
                    key INTEGER PRIMARY KEY,
                    imdb_id TEXT UNIQUE,
                    tvdb_id TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS tmdb_to_tvdb_map2 (
                    key INTEGER PRIMARY KEY,
                    tmdb_id TEXT UNIQUE,
                    tvdb_id TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS letterboxd_map (
                    key INTEGER PRIMARY KEY,
                    letterboxd_id TEXT UNIQUE,
                    tmdb_id TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS omdb_data (
                    key INTEGER PRIMARY KEY,
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
                    key INTEGER PRIMARY KEY,
                    anidb TEXT UNIQUE,
                    anilist TEXT,
                    myanimelist TEXT,
                    kitsu TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS image_maps (
                    key INTEGER PRIMARY KEY,
                    library TEXT UNIQUE)"""
                )
                cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='image_map'")
                if cursor.fetchone()[0] > 0:
                    cursor.execute(f"SELECT DISTINCT library FROM image_map")
                    for library in cursor.fetchall():
                        table_name = self.get_image_table_name(library["library"])
                        cursor.execute(f"SELECT DISTINCT * FROM image_map WHERE library='{library['library']}'")
                        for row in cursor.fetchall():
                            if row["type"] == "poster":
                                final_table = table_name if row["type"] == "poster" else f"{table_name}_backgrounds"
                                self.update_image_map(row["rating_key"], final_table, row["location"], row["compare"], row["overlay"])
                    cursor.execute("DROP TABLE IF EXISTS image_map")

    def query_guid_map(self, plex_guid):
        id_to_return = None
        imdb_id = None
        media_type = None
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM guids_map WHERE plex_guid = ?", (plex_guid,))
                row = cursor.fetchone()
                if row:
                    time_between_insertion = datetime.now() - datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    id_to_return = util.get_list(row["t_id"], int_list=True)
                    imdb_id = util.get_list(row["imdb_id"])
                    media_type = row["media_type"]
                    expired = time_between_insertion.days > self.expiration
        return id_to_return, imdb_id, media_type, expired

    def update_guid_map(self, plex_guid, t_id, imdb_id, expired, media_type):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"INSERT OR IGNORE INTO guids_map(plex_guid) VALUES(?)", (plex_guid,))
                if media_type is None:
                    sql = f"UPDATE guids_map SET t_id = ?, imdb_id = ?, expiration_date = ? WHERE plex_guid = ?"
                    cursor.execute(sql, (t_id, imdb_id, expiration_date.strftime("%Y-%m-%d"), plex_guid))
                else:
                    sql = f"UPDATE guids_map SET t_id = ?, imdb_id = ?, expiration_date = ?, media_type = ? WHERE plex_guid = ?"
                    cursor.execute(sql, (t_id, imdb_id, expiration_date.strftime("%Y-%m-%d"), media_type, plex_guid))

    def query_imdb_to_tmdb_map(self, _id, imdb=True, media_type=None, return_type=False):
        from_id = "imdb_id" if imdb else "tmdb_id"
        to_id = "tmdb_id" if imdb else "imdb_id"
        return self._query_map("imdb_to_tmdb_map", _id, from_id, to_id, media_type=media_type, return_type=return_type)

    def update_imdb_to_tmdb_map(self, media_type, expired, imdb_id, tmdb_id):
        self._update_map("imdb_to_tmdb_map", "imdb_id", imdb_id, "tmdb_id", tmdb_id, expired, media_type=media_type)

    def query_imdb_to_tvdb_map(self, _id, imdb=True):
        from_id = "imdb_id" if imdb else "tvdb_id"
        to_id = "tvdb_id" if imdb else "imdb_id"
        return self._query_map("imdb_to_tvdb_map2", _id, from_id, to_id)

    def update_imdb_to_tvdb_map(self, expired, imdb_id, tvdb_id):
        self._update_map("imdb_to_tvdb_map2", "imdb_id", imdb_id, "tvdb_id", tvdb_id, expired)

    def query_tmdb_to_tvdb_map(self, _id, tmdb=True):
        from_id = "tmdb_id" if tmdb else "tvdb_id"
        to_id = "tvdb_id" if tmdb else "tmdb_id"
        return self._query_map("tmdb_to_tvdb_map2", _id, from_id, to_id)

    def update_tmdb_to_tvdb_map(self, expired, tmdb_id, tvdb_id):
        self._update_map("tmdb_to_tvdb_map2", "tmdb_id", tmdb_id, "tvdb_id", tvdb_id, expired)

    def query_letterboxd_map(self, letterboxd_id):
        return self._query_map("letterboxd_map", letterboxd_id, "letterboxd_id", "tmdb_id")

    def update_letterboxd_map(self, expired, letterboxd_id, tmdb_id):
        self._update_map("letterboxd_map", "letterboxd_id", letterboxd_id, "tmdb_id", tmdb_id, expired)

    def _query_map(self, map_name, _id, from_id, to_id, media_type=None, return_type=False):
        id_to_return = None
        expired = None
        out_type = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                if media_type is None:
                    cursor.execute(f"SELECT * FROM {map_name} WHERE {from_id} = ?", (_id,))
                else:
                    cursor.execute(f"SELECT * FROM {map_name} WHERE {from_id} = ? AND media_type = ?", (_id, media_type))
                row = cursor.fetchone()
                if row and row[to_id]:
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    id_to_return = row[to_id] if to_id == "imdb_id" else int(row[to_id])
                    expired = time_between_insertion.days > self.expiration
                    out_type = row["media_type"] if return_type else None
        if return_type:
            return id_to_return, out_type, expired
        else:
            return id_to_return, expired

    def _update_map(self, map_name, val1_name, val1, val2_name, val2, expired, media_type=None):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"INSERT OR IGNORE INTO {map_name}({val1_name}) VALUES(?)", (val1,))
                if media_type is None:
                    sql = f"UPDATE {map_name} SET {val2_name} = ?, expiration_date = ? WHERE {val1_name} = ?"
                    cursor.execute(sql, (val2, expiration_date.strftime("%Y-%m-%d"), val1))
                else:
                    sql = f"UPDATE {map_name} SET {val2_name} = ?, expiration_date = ?{'' if media_type is None else ', media_type = ?'} WHERE {val1_name} = ?"
                    cursor.execute(sql, (val2, expiration_date.strftime("%Y-%m-%d"), media_type, val1))

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
                    omdb_dict["Response"] = "True"
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

    def update_anime_map(self, expired, anime_ids):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, self.expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO anime_map(anidb) VALUES(?)", (anime_ids["anidb"],))
                cursor.execute("UPDATE anime_map SET anilist = ?, myanimelist = ?, kitsu = ?, expiration_date = ? WHERE anidb = ?", (anime_ids["anidb"], anime_ids["myanimelist"], anime_ids["kitsu"], expiration_date.strftime("%Y-%m-%d"), anime_ids["anidb"]))

    def get_image_table_name(self, library):
        table_name = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM image_maps WHERE library = ?", (library,))
                row = cursor.fetchone()
                if row and row["key"]:
                    table_name = f"image_map_{row['key']}"
                else:
                    cursor.execute("INSERT OR IGNORE INTO image_maps(library) VALUES(?)", (library,))
                    cursor.execute(f"SELECT * FROM image_maps WHERE library = ?", (library,))
                    row = cursor.fetchone()
                    if row and row["key"]:
                        table_name = f"image_map_{row['key']}"
                        cursor.execute(
                            f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            key INTEGER PRIMARY KEY,
                            rating_key TEXT UNIQUE,
                            overlay TEXT,
                            compare TEXT,
                            location TEXT)"""
                        )
                        cursor.execute(
                            f"""CREATE TABLE IF NOT EXISTS {table_name}_backgrounds (
                            key INTEGER PRIMARY KEY,
                            rating_key TEXT UNIQUE,
                            overlay TEXT,
                            compare TEXT,
                            location TEXT)"""
                        )
        return table_name

    def query_image_map_overlay(self, table_name, overlay):
        rks = []
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM {table_name} WHERE overlay = ?", (overlay,))
                rows = cursor.fetchall()
                for row in rows:
                    rks.append(int(row["rating_key"]))
        return rks

    def query_image_map(self, rating_key, table_name):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM {table_name} WHERE rating_key = ?", (rating_key,))
                row = cursor.fetchone()
                if row and row["location"]:
                    return row["location"], row["compare"], row["overlay"]
        return None, None, None

    def update_image_map(self, rating_key, table_name, location, compare, overlay):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"INSERT OR IGNORE INTO {table_name}(rating_key) VALUES(?)", (rating_key,))
                cursor.execute(f"UPDATE {table_name} SET location = ?, compare = ?, overlay = ? WHERE rating_key = ?", (location, compare, overlay, rating_key))
