import json, os, random, sqlite3
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
                for old_table in [
                    "guids", "guid_map", "imdb_to_tvdb_map", "tmdb_to_tvdb_map", "imdb_map",
                    "mdb_data", "mdb_data2", "mdb_data3", "mdb_data4", "omdb_data", "omdb_data2",
                    "tvdb_data", "tvdb_data2", "tvdb_data3", "tmdb_show_data", "tmdb_show_data2",
                    "overlay_ratings", "anidb_data", "anidb_data2", "anidb_data3", "mal_data"
                ]:
                    cursor.execute(f"DROP TABLE IF EXISTS {old_table}")
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
                    """CREATE TABLE IF NOT EXISTS mojo_map (
                    key INTEGER PRIMARY KEY,
                    mojo_url TEXT UNIQUE,
                    imdb_id TEXT,
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
                    """CREATE TABLE IF NOT EXISTS mdb_data5 (
                    key INTEGER PRIMARY KEY,
                    key_id TEXT UNIQUE,
                    title TEXT,
                    year INTEGER,
                    released TEXT,
                    released_digital TEXT,
                    type TEXT,
                    imdbid TEXT,
                    traktid INTEGER,
                    tmdbid INTEGER,
                    score INTEGER,
                    average INTEGER,
                    imdb_rating REAL,
                    metacritic_rating INTEGER,
                    metacriticuser_rating REAL,
                    trakt_rating INTEGER,
                    tomatoes_rating INTEGER,
                    tomatoesaudience_rating INTEGER,
                    tmdb_rating INTEGER,
                    letterboxd_rating REAL,
                    myanimelist_rating REAL,
                    certification TEXT,
                    commonsense TEXT,
                    age_rating TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS anidb_data4 (
                    key INTEGER PRIMARY KEY,
                    anidb_id INTEGER UNIQUE,
                    main_title TEXT,
                    titles TEXT,
                    studio TEXT,
                    rating REAL,
                    average REAL,
                    score REAL,
                    released TEXT,
                    tags TEXT,
                    mal_id INTEGER,
                    imdb_id TEXT,
                    tmdb_id INTEGER,
                    tmdb_type TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS mal_data2 (
                    key INTEGER PRIMARY KEY,
                    mal_id INTEGER UNIQUE,
                    title TEXT,
                    title_english TEXT,
                    title_japanese TEXT,
                    status TEXT,
                    airing TEXT,
                    aired TEXT,
                    rating TEXT,
                    score REAL,
                    rank INTEGER,
                    popularity TEXT,
                    genres TEXT,
                    studio TEXT,
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
                    """CREATE TABLE IF NOT EXISTS tmdb_show_data3 (
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
                    """CREATE TABLE IF NOT EXISTS tmdb_episode_data (
                    key INTEGER PRIMARY KEY,
                    tmdb_id INTEGER UNIQUE,
                    title TEXT,
                    air_date TEXT,
                    overview TEXT,
                    episode_number INTEGER,
                    season_number INTEGER,
                    still_url TEXT,
                    vote_count INTEGER,
                    vote_average REAL,
                    imdb_id TEXT,
                    tvdb_id INTEGER,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS tvdb_data4 (
                    key INTEGER PRIMARY KEY,
                    tvdb_id INTEGER UNIQUE,
                    type TEXT,
                    title TEXT,
                    status TEXT,
                    summary TEXT,
                    poster_url TEXT,
                    background_url TEXT,
                    release_date TEXT,
                    genres TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS tvdb_map (
                    key INTEGER PRIMARY KEY,
                    tvdb_url TEXT UNIQUE,
                    tvdb_id INTEGER,
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
                    """CREATE TABLE IF NOT EXISTS imdb_keywords (
                    key INTEGER PRIMARY KEY,
                    imdb_id TEXT,
                    keywords TEXT,
                    expiration_date TEXT)"""
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
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS ergast_race (
                    key INTEGER PRIMARY KEY,
                    season INTEGER,
                    round INTEGER,
                    name TEXT,
                    date TEXT,
                    expiration_date TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS overlay_special_text (
                    key INTEGER PRIMARY KEY,
                    rating_key INTEGER,
                    type TEXT,
                    text TEXT)"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS testing (
                    key INTEGER PRIMARY KEY,
                    name TEXT,
                    value1 TEXT,
                    value2 TEXT,
                    success TEXT)"""
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

    def query_mojo_map(self, mojo_url):
        return self._query_map("mojo_map", mojo_url, "mojo_url", "imdb_id")

    def update_mojo_map(self, expired, mojo_url, imdb_id):
        self._update_map("mojo_map", "mojo_url", mojo_url, "imdb_id", imdb_id, expired)

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
                cursor.execute("SELECT * FROM mdb_data5 WHERE key_id = ?", (key_id,))
                row = cursor.fetchone()
                if row:
                    mdb_dict["title"] = row["title"] if row["title"] else None
                    mdb_dict["year"] = row["year"] if row["year"] else None
                    mdb_dict["released"] = row["released"] if row["released"] else None
                    mdb_dict["released_digital"] = row["released_digital"] if row["released_digital"] else None
                    mdb_dict["type"] = row["type"] if row["type"] else None
                    mdb_dict["imdbid"] = row["imdbid"] if row["imdbid"] else None
                    mdb_dict["traktid"] = row["traktid"] if row["traktid"] else None
                    mdb_dict["tmdbid"] = row["tmdbid"] if row["tmdbid"] else None
                    mdb_dict["score"] = row["score"] if row["score"] else None
                    mdb_dict["score_average"] = row["average"] if row["average"] else None
                    mdb_dict["certification"] = row["certification"] if row["certification"] else None
                    mdb_dict["commonsense"] = row["commonsense"] if row["commonsense"] else None
                    mdb_dict["age_rating"] = row["age_rating"] if row["age_rating"] else None
                    mdb_dict["ratings"] = [
                        {"source": "imdb", "value": row["imdb_rating"] if row["imdb_rating"] else None},
                        {"source": "metacritic", "value": row["metacritic_rating"] if row["metacritic_rating"] else None},
                        {"source": "metacriticuser", "value": row["metacriticuser_rating"] if row["metacriticuser_rating"] else None},
                        {"source": "trakt", "value": row["trakt_rating"] if row["trakt_rating"] else None},
                        {"source": "tomatoes", "value": row["tomatoes_rating"] if row["tomatoes_rating"] else None},
                        {"source": "tomatoesaudience", "value": row["tomatoesaudience_rating"] if row["tomatoesaudience_rating"] else None},
                        {"source": "tmdb", "value": row["tmdb_rating"] if row["tmdb_rating"] else None},
                        {"source": "letterboxd", "value": row["letterboxd_rating"] if row["letterboxd_rating"] else None},
                        {"source": "myanimelist_rating", "value": row["myanimelist_rating"] if row["myanimelist_rating"] else None}
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
                cursor.execute("INSERT OR IGNORE INTO mdb_data5(key_id) VALUES(?)", (key_id,))
                update_sql = "UPDATE mdb_data5 SET title = ?, year = ?, released = ?, released_digital = ?, type = ?, imdbid = ?, traktid = ?, " \
                             "tmdbid = ?, score = ?, average = ?, imdb_rating = ?, metacritic_rating = ?, metacriticuser_rating = ?, " \
                             "trakt_rating = ?, tomatoes_rating = ?, tomatoesaudience_rating = ?, tmdb_rating = ?, " \
                             "letterboxd_rating = ?, myanimelist_rating = ?, certification = ?, commonsense = ?, age_rating = ?, expiration_date = ? WHERE key_id = ?"
                cursor.execute(update_sql, (
                    mdb.title, mdb.year, mdb.released.strftime("%Y-%m-%d") if mdb.released else None,
                    mdb.released_digital.strftime("%Y-%m-%d") if mdb.released_digital else None, mdb.type,
                    mdb.imdbid, mdb.traktid, mdb.tmdbid, mdb.score, mdb.average, mdb.imdb_rating, mdb.metacritic_rating,
                    mdb.metacriticuser_rating, mdb.trakt_rating, mdb.tomatoes_rating, mdb.tomatoesaudience_rating,
                    mdb.tmdb_rating, mdb.letterboxd_rating, mdb.myanimelist_rating, mdb.content_rating, mdb.commonsense, mdb.age_rating,
                    expiration_date.strftime("%Y-%m-%d"), key_id
                ))

    def query_anidb(self, anidb_id, expiration):
        anidb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM anidb_data4 WHERE anidb_id = ?", (anidb_id,))
                row = cursor.fetchone()
                if row:
                    anidb_dict["main_title"] = row["main_title"]
                    anidb_dict["titles"] = row["titles"] if row["titles"] else None
                    anidb_dict["studio"] = row["studio"] if row["studio"] else None
                    anidb_dict["rating"] = row["rating"] if row["rating"] else None
                    anidb_dict["average"] = row["average"] if row["average"] else None
                    anidb_dict["score"] = row["score"] if row["score"] else None
                    anidb_dict["released"] = row["released"] if row["released"] else None
                    anidb_dict["tags"] = row["tags"] if row["tags"] else None
                    anidb_dict["mal_id"] = row["mal_id"] if row["mal_id"] else None
                    anidb_dict["imdb_id"] = row["imdb_id"] if row["imdb_id"] else None
                    anidb_dict["tmdb_id"] = row["tmdb_id"] if row["tmdb_id"] else None
                    anidb_dict["tmdb_type"] = row["tmdb_type"] if row["tmdb_type"] else None
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return anidb_dict, expired

    def update_anidb(self, expired, anidb_id, anidb, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO anidb_data4(anidb_id) VALUES(?)", (anidb_id,))
                update_sql = "UPDATE anidb_data4 SET main_title = ?, titles = ?, studio = ?, rating = ?, average = ?, score = ?, " \
                             "released = ?, tags = ?, mal_id = ?, imdb_id = ?, tmdb_id = ?, tmdb_type = ?, expiration_date = ? WHERE anidb_id = ?"
                cursor.execute(update_sql, (
                    anidb.main_title, json.dumps(anidb.titles), anidb.studio, anidb.rating, anidb.average, anidb.score,
                    anidb.released.strftime("%Y-%m-%d") if anidb.released else None, json.dumps(anidb.tags),
                    anidb.mal_id, anidb.imdb_id, anidb.tmdb_id, anidb.tmdb_type,
                    expiration_date.strftime("%Y-%m-%d"), anidb_id
                ))

    def query_mal(self, mal_id, expiration):
        mal_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM mal_data2 WHERE mal_id = ?", (mal_id,))
                row = cursor.fetchone()
                if row:
                    mal_dict["title"] = row["title"]
                    mal_dict["title_english"] = row["title_english"] if row["title_english"] else None
                    mal_dict["title_japanese"] = row["title_japanese"] if row["title_japanese"] else None
                    mal_dict["status"] = row["status"] if row["status"] else None
                    mal_dict["airing"] = row["airing"] if row["airing"] else None
                    mal_dict["aired"] = row["aired"] if row["aired"] else None
                    mal_dict["rating"] = row["rating"] if row["rating"] else None
                    mal_dict["score"] = row["score"] if row["score"] else None
                    mal_dict["rank"] = row["rank"] if row["rank"] else None
                    mal_dict["popularity"] = row["popularity"] if row["popularity"] else None
                    mal_dict["genres"] = row["genres"] if row["genres"] else None
                    mal_dict["studio"] = row["studio"] if row["studio"] else None
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return mal_dict, expired

    def update_mal(self, expired, mal_id, mal, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO mal_data2(mal_id) VALUES(?)", (mal_id,))
                update_sql = "UPDATE mal_data2 SET title = ?, title_english = ?, title_japanese = ?, status = ?, airing = ?, " \
                             "aired = ?, rating = ?, score = ?, rank = ?, popularity = ?, genres = ?, studio = ?, expiration_date = ? WHERE mal_id = ?"
                cursor.execute(update_sql, (
                    mal.title, mal.title_english, mal.title_japanese, mal.status, mal.airing, mal.aired.strftime("%Y-%m-%d") if mal.aired else None,
                    mal.rating, mal.score, mal.rank, mal.popularity, "|".join(mal.genres), mal.studio, expiration_date.strftime("%Y-%m-%d"), mal_id
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
                cursor.execute("SELECT * FROM tmdb_show_data3 WHERE tmdb_id = ?", (tmdb_id,))
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
                cursor.execute("INSERT OR IGNORE INTO tmdb_show_data3(tmdb_id) VALUES(?)", (obj.tmdb_id,))
                update_sql = "UPDATE tmdb_show_data3 SET title = ?, original_title = ?, studio = ?, overview = ?, tagline = ?, imdb_id = ?, " \
                             "poster_url = ?, backdrop_url = ?, vote_count = ?, vote_average = ?, language_iso = ?, " \
                             "language_name = ?, genres = ?, keywords = ?, first_air_date = ?, last_air_date = ?, status = ?, " \
                             "type = ?, tvdb_id = ?, countries = ?, seasons = ?, expiration_date = ? WHERE tmdb_id = ?"
                cursor.execute(update_sql, (
                    obj.title, obj.original_title, obj.studio, obj.overview, obj.tagline, obj.imdb_id, obj.poster_url, obj.backdrop_url,
                    obj.vote_count, obj.vote_average, obj.language_iso, obj.language_name, "|".join(obj.genres), "|".join(obj.keywords),
                    obj.first_air_date.strftime("%Y-%m-%d") if obj.first_air_date else None,
                    obj.last_air_date.strftime("%Y-%m-%d") if obj.last_air_date else None,
                    obj.status, obj.type, obj.tvdb_id, "|".join([str(c) for c in obj.countries]), "%|%".join([str(s) for s in obj.seasons]),
                    expiration_date.strftime("%Y-%m-%d"), obj.tmdb_id
                ))

    def query_tmdb_episode(self, tmdb_id, season_number, episode_number, expiration):
        tmdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    "SELECT * FROM tmdb_episode_data WHERE tmdb_id = ? AND season_number = ? AND episode_number = ?",
                    (tmdb_id, season_number, episode_number)
                )
                row = cursor.fetchone()
                if row:
                    tmdb_dict["title"] = row["title"] if row["title"] else ""
                    tmdb_dict["air_date"] = datetime.strptime(row["air_date"], "%Y-%m-%d") if row["air_date"] else None
                    tmdb_dict["overview"] = row["overview"] if row["overview"] else ""
                    tmdb_dict["still_url"] = row["still_url"] if row["still_url"] else ""
                    tmdb_dict["vote_count"] = row["vote_count"] if row["vote_count"] else 0
                    tmdb_dict["vote_average"] = row["vote_average"] if row["vote_average"] else 0
                    tmdb_dict["imdb_id"] = row["imdb_id"] if row["imdb_id"] else ""
                    tmdb_dict["tvdb_id"] = row["tvdb_id"] if row["tvdb_id"] else None
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return tmdb_dict, expired

    def update_tmdb_episode(self, expired, obj, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    "INSERT OR IGNORE INTO tmdb_episode_data(tmdb_id, season_number, episode_number) VALUES(?, ?, ?)",
                    (obj.tmdb_id, obj.season_number, obj.episode_number)
                )
                update_sql = "UPDATE tmdb_episode_data SET title = ?, air_date = ?, overview = ?, still_url = ?, " \
                             "vote_count = ?, vote_average = ?, imdb_id = ?, tvdb_id = ?, " \
                             "expiration_date = ? WHERE tmdb_id = ? AND season_number = ? AND episode_number = ?"
                cursor.execute(update_sql, (
                    obj.title, obj.air_date.strftime("%Y-%m-%d") if obj.air_date else None, obj.overview, obj.still_url,
                    obj.vote_count, obj.vote_average, obj.imdb_id, obj.tvdb_id,
                    expiration_date.strftime("%Y-%m-%d"), obj.tmdb_id, obj.season_number, obj.episode_number
                ))

    def query_tvdb(self, tvdb_id, is_movie, expiration):
        tvdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM tvdb_data4 WHERE tvdb_id = ? and type = ?", (tvdb_id, "movie" if is_movie else "show"))
                row = cursor.fetchone()
                if row:
                    tvdb_dict["tvdb_id"] = int(row["tvdb_id"]) if row["tvdb_id"] else 0
                    tvdb_dict["type"] = row["type"] if row["type"] else ""
                    tvdb_dict["title"] = row["title"] if row["title"] else ""
                    tvdb_dict["status"] = row["status"] if row["status"] else ""
                    tvdb_dict["summary"] = row["summary"] if row["summary"] else ""
                    tvdb_dict["poster_url"] = row["poster_url"] if row["poster_url"] else ""
                    tvdb_dict["background_url"] = row["background_url"] if row["background_url"] else ""
                    tvdb_dict["release_date"] = datetime.strptime(row["release_date"], "%Y-%m-%d") if row["release_date"] else None
                    tvdb_dict["genres"] = row["genres"] if row["genres"] else ""
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return tvdb_dict, expired

    def update_tvdb(self, expired, obj, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO tvdb_data4(tvdb_id, type) VALUES(?, ?)", (obj.tvdb_id, "movie" if obj.is_movie else "show"))
                update_sql = "UPDATE tvdb_data4 SET title = ?, status = ?, summary = ?, poster_url = ?, background_url = ?, " \
                             "release_date = ?, genres = ?, expiration_date = ? WHERE tvdb_id = ? AND type = ?"
                tvdb_date = f"{str(obj.release_date.year).zfill(4)}-{str(obj.release_date.month).zfill(2)}-{str(obj.release_date.day).zfill(2)}" if obj.release_date else None
                cursor.execute(update_sql, (
                    obj.title, obj.status, obj.summary, obj.poster_url, obj.background_url, tvdb_date, "|".join(obj.genres),
                    expiration_date.strftime("%Y-%m-%d"), obj.tvdb_id, "movie" if obj.is_movie else "show"
                ))

    def query_tvdb_map(self, tvdb_url, expiration):
        tvdb_id = None
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM tvdb_map WHERE tvdb_url = ?", (tvdb_url, ))
                row = cursor.fetchone()
                if row:
                    tvdb_id = int(row["tvdb_id"]) if row["tvdb_id"] else None
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return tvdb_id, expired

    def update_tvdb_map(self, expired, tvdb_url, tvdb_id, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO tvdb_map(tvdb_url) VALUES(?)", (tvdb_url, ))
                cursor.execute("UPDATE tvdb_map SET tvdb_id = ?, expiration_date = ? WHERE tvdb_url = ?", (tvdb_id, expiration_date.strftime("%Y-%m-%d"), tvdb_url))

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
                    cursor.execute(
                        f"""CREATE TABLE IF NOT EXISTS {table_name}_overlays (
                        key INTEGER PRIMARY KEY,
                        rating_key TEXT UNIQUE,
                        overlay TEXT,
                        compare TEXT,
                        location TEXT)"""
                    )
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
                        cursor.execute(
                            f"""CREATE TABLE IF NOT EXISTS {table_name}_overlays (
                            key INTEGER PRIMARY KEY,
                            rating_key TEXT UNIQUE,
                            overlay TEXT,
                            compare TEXT,
                            location TEXT)"""
                        )
        return table_name

    def query_image_map(self, rating_key, table_name):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM {table_name} WHERE rating_key = ?", (rating_key,))
                row = cursor.fetchone()
                if row:
                    return row["location"], row["compare"], row["overlay"]
        return None, None, None

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

    def update_list_ids(self, list_key, media_ids):
        final_ids = []
        for media_id, media_type in media_ids:
            final_ids.append((list_key, media_id, media_type))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.executemany(f"INSERT OR IGNORE INTO list_ids(list_key, media_id, media_type) VALUES(?, ?, ?)", final_ids)

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

    def query_imdb_keywords(self, imdb_id, expiration):
        imdb_dict = {}
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM imdb_keywords WHERE imdb_id = ?", (imdb_id,))
                row = cursor.fetchone()
                if row:
                    keywords = row["keywords"] if row["keywords"] else ""
                    imdb_dict = {k.split(":")[0]: (int(k.split(":")[1]), int(k.split(":")[2])) for k in keywords.split("|")}
                    datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                    time_between_insertion = datetime.now() - datetime_object
                    expired = time_between_insertion.days > expiration
        return imdb_dict, expired

    def update_imdb_keywords(self, expired, imdb_id, keywords, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO imdb_keywords(imdb_id) VALUES(?)", (imdb_id,))
                update_sql = "UPDATE imdb_keywords SET keywords = ?, expiration_date = ? WHERE imdb_id = ?"
                cursor.execute(update_sql, ("|".join([f"{k}:{u}:{v}" for k, (u, v) in keywords.items()]), expiration_date.strftime("%Y-%m-%d"), imdb_id))

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

    def query_ergast(self, year, expiration):
        ergast_list = []
        expired = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM ergast_race WHERE season = ?", (year,))
                for row in cursor.fetchall():
                    if row:
                        ergast_list.append({
                            "season": row["season"] if row["season"] else None,
                            "round": row["round"] if row["round"] else None,
                            "raceName": row["name"] if row["name"] else None,
                            "date": row["date"] if row["date"] else None
                        })
                        if not expired:
                            datetime_object = datetime.strptime(row["expiration_date"], "%Y-%m-%d")
                            time_between_insertion = datetime.now() - datetime_object
                            expired = time_between_insertion.days > expiration
        return ergast_list, expired

    def update_ergast(self, expired, season, races, expiration):
        expiration_date = datetime.now() if expired is True else (datetime.now() - timedelta(days=random.randint(1, expiration)))
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("DELETE FROM ergast_race WHERE season = ?", (season,))
                cursor.executemany("INSERT OR IGNORE INTO ergast_race(season, round) VALUES(?, ?)", [(r.season, r.round) for r in races])
                cursor.executemany("UPDATE ergast_race SET name = ?, date = ?, expiration_date = ? WHERE season = ? AND round = ?",
                                   [(r.name, r.date.strftime("%Y-%m-%d") if r.date else None,
                                     expiration_date.strftime("%Y-%m-%d"), r.season, r.round) for r in races])

    def query_overlay_special_text(self, rating_key):
        attrs = {}
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("SELECT * FROM overlay_special_text WHERE rating_key = ?", (rating_key, ))
                for row in cursor.fetchall():
                    if row:
                        attrs[row["type"]] = row["text"]
        return attrs

    def update_overlay_special_text(self, rating_key, data_type, text):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute("INSERT OR IGNORE INTO overlay_special_text(rating_key, type) VALUES(?, ?)", (rating_key, data_type))
                cursor.execute("UPDATE overlay_special_text SET text = ? WHERE rating_key = ? AND type = ?", (text, rating_key, data_type))

    def query_testing(self, name):
        value1 = None
        value2 = None
        success = None
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT * FROM testing WHERE name = ?", (name,))
                row = cursor.fetchone()
                if row:
                    value1 = row["value1"]
                    value2 = row["value2"]
                    success = True if row["success"] == "True" else False
        return value1, value2, success

    def update_testing(self, name, value1, value2, success):
        with sqlite3.connect(self.cache_path) as connection:
            connection.row_factory = sqlite3.Row
            with closing(connection.cursor()) as cursor:
                cursor.execute(f"INSERT OR IGNORE INTO testing(name) VALUES(?)", (name,))
                sql = f"UPDATE testing SET value1 = ?, value2 = ?, success = ? WHERE name = ?"
                cursor.execute(sql, (value1, value2, success, name))
