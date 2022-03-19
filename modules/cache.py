import os, random, sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from modules import util

logger = util.logger

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
                cursor.execute("DROP TABLE IF EXISTS mdb_data")
                cursor.execute("DROP TABLE IF EXISTS omdb_data")
                cursor.execute("DROP TABLE IF EXISTS omdb_data2")
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
                    """CREATE TABLE IF NOT EXISTS flixpatrol_map (
                    key INTEGER PRIMARY KEY,
                    flixpatrol_id TEXT UNIQUE,
                    tmdb_id TEXT,
                    media_type TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS omdb_data3 (
                    key INTEGER PRIMARY KEY,
                    imdb_id TEXT UNIQUE,
                    title TEXT,
                    year INTEGER,
                    released TEXT,
                    content_rating TEXT,
                    genres TEXT,
                    imdb_rating REAL,
                    imdb_votes INTEGER,
                    metacritic_rating INTEGER,
                    type TEXT,
                    series_id TEXT,
                    season_num INTEGER,
                    episode_num INTEGER,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS mdb_data2 (
                    key INTEGER PRIMARY KEY,
                    key_id TEXT UNIQUE,
                    title TEXT,
                    year INTEGER,
                    released TEXT,
                    type TEXT,
                    imdbid TEXT,
                    traktid INTEGER,
                    tmdbid INTEGER,
                    score INTEGER,
                    imdb_rating REAL,
                    metacritic_rating INTEGER,
                    metacriticuser_rating REAL,
                    trakt_rating INTEGER,
                    tomatoes_rating INTEGER,
                    tomatoesaudience_rating INTEGER,
                    tmdb_rating INTEGER,
                    letterboxd_rating REAL,
                    commonsense TEXT,
                    certification TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS tmdb_movie_data (
                    key INTEGER PRIMARY KEY,
                    tmdb_id INTEGER UNIQUE,
                    title TEXT,
                    original_title TEXT,
                    studio TEXT,
                    overview TEXT,
                    tagline TEXT,
                    imdb_id TEXT,
                    poster_url TEXT,
                    backdrop_url TEXT,
                    vote_count INTEGER,
                    vote_average REAL,
                    language_iso TEXT,
                    language_name TEXT,
                    genres TEXT,
                    keywords TEXT,
                    release_date TEXT,
                    collection_id INTEGER,
                    collection_name TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS tmdb_show_data (
                    key INTEGER PRIMARY KEY,
                    tmdb_id INTEGER UNIQUE,
                    title TEXT,
                    original_title TEXT,
                    studio TEXT,
                    overview TEXT,
                    tagline TEXT,
                    imdb_id TEXT,
                    poster_url TEXT,
                    backdrop_url TEXT,
                    vote_count INTEGER,
                    vote_average REAL,
                    language_iso TEXT,
                    language_name TEXT,
                    genres TEXT,
                    keywords TEXT,
                    first_air_date TEXT,
                    last_air_date TEXT,
                    status TEXT,
                    type TEXT,
                    tvdb_id INTEGER,
                    countries TEXT,
                    seasons TEXT,
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
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS radarr_adds (
                    key INTEGER PRIMARY KEY,
                    tmdb_id TEXT,
                    library TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS sonarr_adds (
                    key INTEGER PRIMARY KEY,
                    tvdb_id TEXT,
                    library TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS list_cache (
                    key INTEGER PRIMARY KEY,
                    list_type TEXT,
                    list_data TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS list_ids (
                    key INTEGER PRIMARY KEY,
                    list_key TEXT,
                    media_id TEXT,
                    media_type TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS imdb_parental (
                    key INTEGER PRIMARY KEY,
                    imdb_id TEXT,
                    nudity TEXT,
                    violence TEXT,
                    profanity TEXT,
                    alcohol TEXT,
                    frightening TEXT,
                    expiration_date TEXT)"""
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
                                self.update_image_map(row["rating_key"], final_table, row["location"], row["compare"], overlay=row["overlay"])
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

    def query_flixpatrol_map(self, flixpatrol_id, media_type):
        return self._query_map("flixpatrol_map", flixpatrol_id, "flixpatrol_id", "tmdb_id", media_type=media_type)

    def update_flixpatrol_map(self, expired, flixpatrol_id, tmdb_id, media_type):
        self._update_map("flixpatrol_map", "flixpatrol_id", flixpatrol_id, "tmdb_id", tmdb_id, expired, media_type=media_type)

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
                    if "_" in row[to_id]:
                        id_to_return = row[to_id]
                    else:
                        try:
                            id_to_return = int(row[to_id])
                        except ValueError:
                            id_to_return = row[to_id]
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
                    sql = f"UPDATE {map_name} SET {val2_name} = ?, expiration_date = ?, media_type = ? WHERE {val1_name} = ?"
                    cursor.execute(sql, (val2, expiration_date.strftime("%Y-%m-%d"), media_type, val1))

    def query_omdb(self, imdb_id, expiration):
        omdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM omdb_data3 WHERE imdb_id = ?", (imdb_id,))
                row = cursor.fetchone()
                if row:
                    omdb_dict["imdbID"] = row["imdb_id"] if row["imdb_id"] else None
                    omdb_dict["Title"] = row["title"] if row["title"] else None
                    omdb_dict["Year"] = row["year"] if row["year"] else None
                    omdb_dict["Released"] = row["released"] if row["released"] else None
                    omdb_dict["Rated"] = row["content_rating"] if row["content_rating"] else None
                    omdb_dict["Genre"] = row["genres"] if row["genres"] else None
                    omdb_dict["imdbRating"] = row["imdb_rating"] if row["imdb_rating"] else None
                    omdb_dict["imdbVotes"] = row["imdb_votes"] if row["imdb_votes"] else None
                    omdb_dict["Metascore"] = row["metacritic_rating"] if row["metacritic_rating"] else None
                    omdb_dict["Type"] = row["type"] if row["type"] else None
                    omdb_dict["seriesID"] = row["series_id"] if row["series_id"] else None
                    omdb_dict["Season"] = row["season_num"] if row["season_num"] else None
                    omdb_dict["Episode"] = row["episode_num"] if row["episode_num"] else None
                    omdb_dict["Response"] = "True"
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return omdb_dict, expired

    def update_omdb(self, expired, omdb, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO omdb_data3(imdb_id) VALUES(?)", (omdb.imdb_id,))
                update_sql = "UPDATE omdb_data3 SET title = ?, year = ?, released = ?, content_rating = ?, genres = ?, " \
                             "imdb_rating = ?, imdb_votes = ?, metacritic_rating = ?, type = ?, series_id = ?, " \
                             "season_num = ?, episode_num = ?, expiration_date = ? WHERE imdb_id = ?"
                cursor.execute(update_sql, (
                    omdb.title, omdb.year, omdb.released.strftime("%d %b %Y") if omdb.released else None, omdb.content_rating,
                    omdb.genres_str, omdb.imdb_rating, omdb.imdb_votes, omdb.metacritic_rating, omdb.type, omdb.series_id,
                    omdb.season_num, omdb.episode_num, expiration_date.strftime("%Y-%m-%d"), omdb.imdb_id))

    def query_mdb(self, key_id, expiration):
        mdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM mdb_data2 WHERE key_id = ?", (key_id,))
                row = cursor.fetchone()
                if row:
                    mdb_dict["title"] = row["title"] if row["title"] else None
                    mdb_dict["year"] = row["year"] if row["year"] else None
                    mdb_dict["released"] = row["released"] if row["released"] else None
                    mdb_dict["type"] = row["type"] if row["type"] else None
                    mdb_dict["imdbid"] = row["imdbid"] if row["imdbid"] else None
                    mdb_dict["traktid"] = row["traktid"] if row["traktid"] else None
                    mdb_dict["tmdbid"] = row["tmdbid"] if row["tmdbid"] else None
                    mdb_dict["score"] = row["score"] if row["score"] else None
                    mdb_dict["commonsense"] = row["commonsense"] if row["commonsense"] else None
                    mdb_dict["certification"] = row["certification"] if row["certification"] else None
                    mdb_dict["ratings"] = [
                        {"source": "imdb", "value": row["imdb_rating"] if row["imdb_rating"] else None},
                        {"source": "metacritic", "value": row["metacritic_rating"] if row["metacritic_rating"] else None},
                        {"source": "metacriticuser", "value": row["metacriticuser_rating"] if row["metacriticuser_rating"] else None},
                        {"source": "trakt", "value": row["trakt_rating"] if row["trakt_rating"] else None},
                        {"source": "tomatoes", "value": row["tomatoes_rating"] if row["tomatoes_rating"] else None},
                        {"source": "tomatoesaudience", "value": row["tomatoesaudience_rating"] if row["tomatoesaudience_rating"] else None},
                        {"source": "tmdb", "value": row["tmdb_rating"] if row["tmdb_rating"] else None},
                        {"source": "letterboxd", "value": row["letterboxd_rating"] if row["letterboxd_rating"] else None}
                    ]
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return mdb_dict, expired

    def update_mdb(self, expired, key_id, mdb, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO mdb_data2(key_id) VALUES(?)", (key_id,))
                update_sql = "UPDATE mdb_data2 SET title = ?, year = ?, released = ?, type = ?, imdbid = ?, traktid = ?, " \
                             "tmdbid = ?, score = ?, imdb_rating = ?, metacritic_rating = ?, metacriticuser_rating = ?, " \
                             "trakt_rating = ?, tomatoes_rating = ?, tomatoesaudience_rating = ?, tmdb_rating = ?, " \
                             "letterboxd_rating = ?, certification = ?, commonsense = ?, expiration_date = ? WHERE key_id = ?"
                cursor.execute(update_sql, (
                    mdb.title, mdb.year, mdb.released.strftime("%Y-%m-%d") if mdb.released else None, mdb.type,
                    mdb.imdbid, mdb.traktid, mdb.tmdbid, mdb.score, mdb.imdb_rating, mdb.metacritic_rating,
                    mdb.metacriticuser_rating, mdb.trakt_rating, mdb.tomatoes_rating, mdb.tomatoesaudience_rating,
                    mdb.tmdb_rating, mdb.letterboxd_rating, mdb.content_rating, mdb.commonsense,
                    expiration_date.strftime("%Y-%m-%d"), key_id
                ))

    def query_tmdb_movie(self, tmdb_id, expiration):
        tmdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM tmdb_movie_data WHERE tmdb_id = ?", (tmdb_id,))
                row = cursor.fetchone()
                if row:
                    tmdb_dict["title"] = row["title"] if row["title"] else ""
                    tmdb_dict["original_title"] = row["original_title"] if row["original_title"] else ""
                    tmdb_dict["studio"] = row["studio"] if row["studio"] else ""
                    tmdb_dict["overview"] = row["overview"] if row["overview"] else ""
                    tmdb_dict["tagline"] = row["tagline"] if row["tagline"] else ""
                    tmdb_dict["imdb_id"] = row["imdb_id"] if row["imdb_id"] else ""
                    tmdb_dict["poster_url"] = row["poster_url"] if row["poster_url"] else ""
                    tmdb_dict["backdrop_url"] = row["backdrop_url"] if row["backdrop_url"] else ""
                    tmdb_dict["vote_count"] = row["vote_count"] if row["vote_count"] else 0
                    tmdb_dict["vote_average"] = row["vote_average"] if row["vote_average"] else 0
                    tmdb_dict["language_iso"] = row["language_iso"] if row["language_iso"] else None
                    tmdb_dict["language_name"] = row["language_name"] if row["language_name"] else None
                    tmdb_dict["genres"] = row["genres"] if row["genres"] else ""
                    tmdb_dict["keywords"] = row["keywords"] if row["keywords"] else ""
                    tmdb_dict["release_date"] = datetime.strptime(row["release_date"], "%Y-%m-%d") if row["release_date"] else None
                    tmdb_dict["collection_id"] = row["collection_id"] if row["collection_id"] else None
                    tmdb_dict["collection_name"] = row["collection_name"] if row["collection_name"] else None
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return tmdb_dict, expired

    def update_tmdb_movie(self, expired, obj, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO tmdb_movie_data(tmdb_id) VALUES(?)", (obj.tmdb_id,))
                update_sql = "UPDATE tmdb_movie_data SET title = ?, original_title = ?, studio = ?, overview = ?, tagline = ?, imdb_id = ?, " \
                             "poster_url = ?, backdrop_url = ?, vote_count = ?, vote_average = ?, language_iso = ?, " \
                             "language_name = ?, genres = ?, keywords = ?, release_date = ?, collection_id = ?, " \
                             "collection_name = ?, expiration_date = ? WHERE tmdb_id = ?"
                cursor.execute(update_sql, (
                    obj.title, obj.original_title, obj.studio, obj.overview, obj.tagline, obj.imdb_id, obj.poster_url, obj.backdrop_url,
                    obj.vote_count, obj.vote_average, obj.language_iso, obj.language_name, "|".join(obj.genres), "|".join(obj.keywords),
                    obj.release_date.strftime("%Y-%m-%d") if obj.release_date else None, obj.collection_id, obj.collection_name,
                    expiration_date.strftime("%Y-%m-%d"), obj.tmdb_id
                ))

    def query_tmdb_show(self, tmdb_id, expiration):
        tmdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM tmdb_show_data WHERE tmdb_id = ?", (tmdb_id,))
                row = cursor.fetchone()
                if row:
                    tmdb_dict["title"] = row["title"] if row["title"] else ""
                    tmdb_dict["original_title"] = row["original_title"] if row["original_title"] else ""
                    tmdb_dict["studio"] = row["studio"] if row["studio"] else ""
                    tmdb_dict["overview"] = row["overview"] if row["overview"] else ""
                    tmdb_dict["tagline"] = row["tagline"] if row["tagline"] else ""
                    tmdb_dict["imdb_id"] = row["imdb_id"] if row["imdb_id"] else ""
                    tmdb_dict["poster_url"] = row["poster_url"] if row["poster_url"] else ""
                    tmdb_dict["backdrop_url"] = row["backdrop_url"] if row["backdrop_url"] else ""
                    tmdb_dict["vote_count"] = row["vote_count"] if row["vote_count"] else 0
                    tmdb_dict["vote_average"] = row["vote_average"] if row["vote_average"] else 0
                    tmdb_dict["language_iso"] = row["language_iso"] if row["language_iso"] else None
                    tmdb_dict["language_name"] = row["language_name"] if row["language_name"] else None
                    tmdb_dict["genres"] = row["genres"] if row["genres"] else ""
                    tmdb_dict["keywords"] = row["keywords"] if row["keywords"] else ""
                    tmdb_dict["first_air_date"] = datetime.strptime(row["first_air_date"], "%Y-%m-%d") if row["first_air_date"] else None
                    tmdb_dict["last_air_date"] = datetime.strptime(row["last_air_date"], "%Y-%m-%d") if row["last_air_date"] else None
                    tmdb_dict["status"] = row["status"] if row["status"] else None
                    tmdb_dict["type"] = row["type"] if row["type"] else None
                    tmdb_dict["tvdb_id"] = row["tvdb_id"] if row["tvdb_id"] else None
                    tmdb_dict["countries"] = row["countries"] if row["countries"] else ""
                    tmdb_dict["seasons"] = row["seasons"] if row["seasons"] else ""
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return tmdb_dict, expired

    def update_tmdb_show(self, expired, obj, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO tmdb_show_data(tmdb_id) VALUES(?)", (obj.tmdb_id,))
                update_sql = "UPDATE tmdb_show_data SET title = ?, original_title = ?, studio = ?, overview = ?, tagline = ?, imdb_id = ?, " \
                             "poster_url = ?, backdrop_url = ?, vote_count = ?, vote_average = ?, language_iso = ?, " \
                             "language_name = ?, genres = ?, keywords = ?, first_air_date = ?, last_air_date = ?, status = ?, " \
                             "type = ?, tvdb_id = ?, countries = ?, seasons = ?, expiration_date = ? WHERE tmdb_id = ?"
                cursor.execute(update_sql, (
                    obj.title, obj.original_title, obj.studio, obj.overview, obj.tagline, obj.imdb_id, obj.poster_url, obj.backdrop_url,
                    obj.vote_count, obj.vote_average, obj.language_iso, obj.language_name, "|".join(obj.genres), "|".join(obj.keywords),
                    obj.first_air_date.strftime("%Y-%m-%d") if obj.first_air_date else None,
                    obj.last_air_date.strftime("%Y-%m-%d") if obj.last_air_date else None,
                    obj.status, obj.type, obj.tvdb_id, "|".join([str(c) for c in obj.countries]), "|".join([str(s) for s in obj.seasons]),
                    expiration_date.strftime("%Y-%m-%d"), obj.tmdb_id
                ))

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

    def update_remove_overlay(self, table_name, overlay):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"UPDATE {table_name} SET overlay = ? WHERE overlay = ?", ("", overlay))

    def query_image_map(self, rating_key, table_name):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM {table_name} WHERE rating_key = ?", (rating_key,))
                row = cursor.fetchone()
                if row and row["location"]:
                    return row["location"], row["compare"]
        return None, None

    def update_image_map(self, rating_key, table_name, location, compare, overlay=""):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"INSERT OR IGNORE INTO {table_name}(rating_key) VALUES(?)", (rating_key,))
                cursor.execute(f"UPDATE {table_name} SET location = ?, compare = ?, overlay = ? WHERE rating_key = ?", (location, compare, overlay, rating_key))

    def query_radarr_adds(self, tmdb_id, library):
        return self.query_arr_adds(tmdb_id, library, "radarr", "tmdb_id")

    def query_sonarr_adds(self, tvdb_id, library):
        return self.query_arr_adds(tvdb_id, library, "sonarr", "tvdb_id")

    def query_arr_adds(self, t_id, library, arr, id_type):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM {arr}_adds WHERE {id_type} = ? AND library = ?", (t_id, library))
                row = cursor.fetchone()
                if row and row[id_type]:
                    return int(row[id_type])
        return None

    def update_radarr_adds(self, tmdb_id, library):
        return self.update_arr_adds(tmdb_id, library, "radarr", "tmdb_id")

    def update_sonarr_adds(self, tvdb_id, library):
        return self.update_arr_adds(tvdb_id, library, "sonarr", "tvdb_id")

    def update_arr_adds(self, t_id, library, arr, id_type):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"INSERT OR IGNORE INTO {arr}_adds({id_type}, library) VALUES(?, ?)", (t_id, library))

    def update_list_ids(self, list_key, media_ids):
        final_ids = []
        for media_id, media_type in media_ids:
            final_ids.append((list_key, media_id, media_type))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.executemany(f"INSERT OR IGNORE INTO list_ids(list_key, media_id, media_type) VALUES(?, ?, ?)", final_ids)

    def update_list_cache(self, list_type, list_data, expired, expiration):
        list_key = None
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=expiration))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"INSERT OR IGNORE INTO list_cache(list_type, list_data) VALUES(?, ?)", (list_type, list_data))
                cursor.execute(f"UPDATE list_cache SET expiration_date = ? WHERE list_type = ? AND list_data = ?", (expiration_date.strftime("%Y-%m-%d"), list_type, list_data))
                cursor.execute(f"SELECT * FROM list_cache WHERE list_type = ? AND list_data = ?", (list_type, list_data))
                row = cursor.fetchone()
                if row and row["key"]:
                    list_key = row["key"]
        return list_key

    def query_list_cache(self, list_type, list_data, expiration):
        list_key = None
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM list_cache WHERE list_type = ? AND list_data = ?", (list_type, list_data))
                row = cursor.fetchone()
                if row and row["key"]:
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    list_key = row["key"]
                    expired = time_between_insertion.days > expiration
        return list_key, expired

    def query_list_ids(self, list_key):
        ids = []
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM list_ids WHERE list_key = ?", (list_key,))
                for row in cursor:
                    ids.append((row["media_id"], row["media_type"]))
        return ids

    def delete_list_ids(self, list_key):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"DELETE FROM list_ids WHERE list_key = ?", (list_key,))

    def query_imdb_parental(self, imdb_id, expiration):
        imdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM imdb_parental WHERE imdb_id = ?", (imdb_id,))
                row = cursor.fetchone()
                if row:
                    imdb_dict["nudity"] = row["nudity"] if row["nudity"] else "None"
                    imdb_dict["violence"] = row["violence"] if row["violence"] else "None"
                    imdb_dict["profanity"] = row["profanity"] if row["profanity"] else "None"
                    imdb_dict["alcohol"] = row["alcohol"] if row["alcohol"] else "None"
                    imdb_dict["frightening"] = row["frightening"] if row["frightening"] else "None"
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return imdb_dict, expired

    def update_imdb_parental(self, expired, imdb_id, parental, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO imdb_parental(imdb_id) VALUES(?)", (imdb_id,))
                update_sql = "UPDATE imdb_parental SET nudity = ?, violence = ?, profanity = ?, alcohol = ?, " \
                             "frightening = ?, expiration_date = ? WHERE imdb_id = ?"
                cursor.execute(update_sql, (parental["nudity"], parental["violence"], parental["profanity"], parental["alcohol"],
                                            parental["frightening"], expiration_date.strftime("%Y-%m-%d"), imdb_id))