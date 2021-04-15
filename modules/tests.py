import logging
from modules import util
from modules.config import Config
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

def run_tests(default_dir):
    try:
        config = Config(default_dir)
        logger.info("")
        util.separator("Mapping Tests")
        for library in config.libraries:
            config.map_guids(library)
        anidb_tests(config)
        imdb_tests(config)
        mal_tests(config)
        tautulli_tests(config)
        tmdb_tests(config)
        trakt_tests(config)
        tvdb_tests(config)
        util.separator("Finished All Plex Meta Manager Tests")
    except KeyboardInterrupt:
        util.separator("Canceled Plex Meta Manager Tests")

def anidb_tests(config):
    if config.AniDB:
        util.separator("AniDB Tests")

        try:
            config.convert_anidb_to_tvdb(69)
            logger.info("Success | Convert AniDB to TVDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert AniDB to TVDb: {e}")

        try:
            config.convert_anidb_to_imdb(112)
            logger.info("Success | Convert AniDB to IMDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert AniDB to IMDb: {e}")

        try:
            config.convert_tvdb_to_anidb(81797)
            logger.info("Success | Convert TVDb to AniDB")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert TVDb to AniDB: {e}")

        try:
            config.convert_imdb_to_anidb("tt0245429")
            logger.info("Success | Convert IMDb to AniDB")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert IMDb to AniDB: {e}")

        try:
            config.AniDB.get_items("anidb_id", 69, "en", status_message=False)
            logger.info("Success | Get AniDB ID")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get AniDB ID: {e}")

        try:
            config.AniDB.get_items("anidb_relation", 69, "en", status_message=False)
            logger.info("Success | Get AniDB Relation")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get AniDB Relation: {e}")

        try:
            config.AniDB.get_items("anidb_popular", 30, "en", status_message=False)
            logger.info("Success | Get AniDB Popular")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get AniDB Popular: {e}")

        try:
            config.AniDB.validate_anidb_list(["69", "112"], "en")
            logger.info("Success | Validate AniDB List")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Validate AniDB List: {e}")

    else:
        util.separator("AniDB Not Configured")

def imdb_tests(config):
    if config.IMDb:
        util.separator("IMDb Tests")

        tmdb_ids, tvdb_ids = config.IMDb.get_items("imdb_list", {"url": "https://www.imdb.com/search/title/?groups=top_1000", "limit": 0}, "en", status_message=False)
        if len(tmdb_ids) == 1000:                           logger.info("Success | IMDb URL get TMDb IDs")
        else:                                               logger.error(f"Failure | IMDb URL get TMDb IDs: {len(tmdb_ids)} Should be 1000")

        tmdb_ids, tvdb_ids = config.IMDb.get_items("imdb_list", {"url": "https://www.imdb.com/list/ls026173135/", "limit": 0}, "en", status_message=False)
        if len(tmdb_ids) == 250:                            logger.info("Success | IMDb URL get TMDb IDs")
        else:                                               logger.error(f"Failure | IMDb URL get TMDb IDs: {len(tmdb_ids)} Should be 250")

        tmdb_ids, tvdb_ids = config.IMDb.get_items("imdb_id", "tt0814243", "en", status_message=False)
        if len(tmdb_ids) == 1:                              logger.info("Success | IMDb ID get TMDb IDs")
        else:                                               logger.error(f"Failure | IMDb ID get TMDb IDs: {len(tmdb_ids)} Should be 1")

    else:
        util.separator("IMDb Not Configured")

def mal_tests(config):
    if config.MyAnimeList:
        util.separator("MyAnimeList Tests")

        mal_list_tests = [
            ("mal_all", 10),
            ("mal_airing", 10),
            ("mal_upcoming", 10),
            ("mal_tv", 10),
            ("mal_movie", 10),
            ("mal_ova", 10),
            ("mal_special", 10),
            ("mal_popular", 10),
            ("mal_favorite", 10),
            ("mal_suggested", 10),
            ("mal_userlist", {"limit": 10, "username": "@me", "status": "completed", "sort_by": "list_score"}),
            ("mal_season", {"limit": 10, "season": "fall", "year": 2020, "sort_by": "anime_score"})
        ]

        for mal_list_test in mal_list_tests:
            try:
                config.MyAnimeList.get_items(mal_list_test[0], mal_list_test[1], status_message=False)
                logger.info(f"Success | Get Anime using {util.pretty_names[mal_list_test[0]]}")
            except Failed as e:
                util.print_stacktrace()
                logger.error(f"Failure | Get Anime using {util.pretty_names[mal_list_test[0]]}: {e}")
    else:
        util.separator("MyAnimeList Not Configured")

def tautulli_tests(config):
    if config.libraries[0].Tautulli:
        util.separator("Tautulli Tests")

        try:
            config.libraries[0].Tautulli.get_section_id(config.libraries[0].name)
            logger.info("Success | Get Section ID")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get Section ID: {e}")

        try:
            config.libraries[0].Tautulli.get_popular(config.libraries[0], status_message=False)
            logger.info("Success | Get Popular")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get Popular: {e}")

        try:
            config.libraries[0].Tautulli.get_top(config.libraries[0], status_message=False)
            logger.info("Success | Get Top")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get Top: {e}")
    else:
        util.separator("Tautulli Not Configured")

def tmdb_tests(config):
    if config.TMDb:
        util.separator("TMDb Tests")

        try:
            config.TMDb.convert_imdb_to_tmdb("tt0076759")
            logger.info("Success | Convert IMDb to TMDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert IMDb to TMDb: {e}")

        try:
            config.TMDb.convert_tmdb_to_imdb(11)
            logger.info("Success | Convert TMDb to IMDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert TMDb to IMDb: {e}")

        try:
            config.TMDb.convert_imdb_to_tvdb("tt0458290")
            logger.info("Success | Convert IMDb to TVDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert IMDb to TVDb: {e}")

        try:
            config.TMDb.convert_tvdb_to_imdb(83268)
            logger.info("Success | Convert TVDb to IMDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert TVDb to IMDb: {e}")

        tmdb_list_tests = [
            ([11], "Movie"),
            ([4194], "Show"),
            ([10], "Collection"),
            ([1], "Person"),
            ([1], "Company"),
            ([2739], "Network"),
            ([8136], "List")
        ]

        for tmdb_list_test in tmdb_list_tests:
            try:
                config.TMDb.validate_tmdb_list(tmdb_list_test[0], tmdb_type=tmdb_list_test[1])
                logger.info(f"Success | Get TMDb {tmdb_list_test[1]}")
            except Failed as e:
                util.print_stacktrace()
                logger.error(f"Failure | Get TMDb {tmdb_list_test[1]}: {e}")

        tmdb_list_tests = [
            ("tmdb_discover", {"sort_by": "popularity.desc", "limit": 100}, True),
            ("tmdb_discover", {"sort_by": "popularity.desc", "limit": 100}, False),
            ("tmdb_company", 1, True),
            ("tmdb_company", 1, False),
            ("tmdb_network", 2739, False),
            ("tmdb_keyword", 180547, True),
            ("tmdb_keyword", 180547, False),
            ("tmdb_now_playing", 10, True),
            ("tmdb_popular", 10, True),
            ("tmdb_popular", 10, False),
            ("tmdb_top_rated", 10, True),
            ("tmdb_top_rated", 10, False),
            ("tmdb_trending_daily", 10, True),
            ("tmdb_trending_daily", 10, False),
            ("tmdb_trending_weekly", 10, True),
            ("tmdb_trending_weekly", 10, False),
            ("tmdb_list", 7068209, True),
            ("tmdb_list", 7068209, False),
            ("tmdb_movie", 11, True),
            ("tmdb_collection", 10, True),
            ("tmdb_show", 4194, False)
        ]

        for tmdb_list_test in tmdb_list_tests:
            try:
                config.TMDb.get_items(tmdb_list_test[0], tmdb_list_test[1], tmdb_list_test[2], status_message=False)
                logger.info(f"Success | Get {'Movies' if tmdb_list_test[2] else 'Shows'} using {util.pretty_names[tmdb_list_test[0]]}")
            except Failed as e:
                util.print_stacktrace()
                logger.error(f"Failure | Get {'Movies' if tmdb_list_test[2] else 'Shows'} using {util.pretty_names[tmdb_list_test[0]]}: {e}")
    else:
        util.separator("TMDb Not Configured")

def trakt_tests(config):
    if config.Trakt:
        util.separator("Trakt Tests")

        try:
            config.Trakt.convert_imdb_to_tmdb("tt0076759")
            logger.info("Success | Convert IMDb to TMDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert IMDb to TMDb: {e}")

        try:
            config.Trakt.convert_tmdb_to_imdb(11)
            logger.info("Success | Convert TMDb to IMDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert TMDb to IMDb: {e}")

        try:
            config.Trakt.convert_imdb_to_tvdb("tt0458290")
            logger.info("Success | Convert IMDb to TVDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert IMDb to TVDb: {e}")

        try:
            config.Trakt.convert_tvdb_to_imdb(83268)
            logger.info("Success | Convert TVDb to IMDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert TVDb to IMDb: {e}")

        try:
            config.Trakt.convert_tmdb_to_tvdb(11)
            logger.info("Success | Convert TMDb to TVDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert TMDb to TVDb: {e}")

        try:
            config.Trakt.convert_tvdb_to_tmdb(83268)
            logger.info("Success | Convert TVDb to TMDb")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Convert TVDb to TMDb: {e}")

        try:
            config.Trakt.validate_trakt_list(["https://trakt.tv/users/movistapp/lists/christmas-movies"])
            logger.info("Success | Get List")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get List: {e}")

        try:
            config.Trakt.validate_trakt_watchlist(["me"], True)
            logger.info("Success | Get Watchlist Movies")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get Watchlist Movies: {e}")

        try:
            config.Trakt.validate_trakt_watchlist(["me"], False)
            logger.info("Success | Get Watchlist Shows")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | Get Watchlist Shows: {e}")

        trakt_list_tests = [
            ("trakt_list", "https://trakt.tv/users/movistapp/lists/christmas-movies", True),
            ("trakt_trending", 10, True),
            ("trakt_trending", 10, False),
            ("trakt_watchlist", "me", True),
            ("trakt_watchlist", "me", False)
        ]

        for trakt_list_test in trakt_list_tests:
            try:
                config.Trakt.get_items(trakt_list_test[0], trakt_list_test[1], trakt_list_test[2], status_message=False)
                logger.info(f"Success | Get {'Movies' if trakt_list_test[2] else 'Shows'} using {util.pretty_names[trakt_list_test[0]]}")
            except Failed as e:
                util.print_stacktrace()
                logger.error(f"Failure | Get {'Movies' if trakt_list_test[2] else 'Shows'} using {util.pretty_names[trakt_list_test[0]]}: {e}")
    else:
        util.separator("Trakt Not Configured")

def tvdb_tests(config):
    if config.TVDb:
        util.separator("TVDb Tests")

        tmdb_ids, tvdb_ids = config.TVDb.get_items("tvdb_list", "https://www.thetvdb.com/lists/arrowverse", "en", status_message=False)
        if len(tvdb_ids) == 10 and len(tmdb_ids) == 0:      logger.info("Success | TVDb URL get TVDb IDs and TMDb IDs")
        else:                                               logger.error(f"Failure | TVDb URL get TVDb IDs and TMDb IDs: {len(tvdb_ids)} Should be 10 and {len(tmdb_ids)} Should be 0")

        tmdb_ids, tvdb_ids = config.TVDb.get_items("tvdb_list", "https://www.thetvdb.com/lists/6957", "en", status_message=False)
        if len(tvdb_ids) == 4 and len(tmdb_ids) == 2:       logger.info("Success | TVDb URL get TVDb IDs and TMDb IDs")
        else:                                               logger.error(f"Failure | TVDb URL get TVDb IDs and TMDb IDs: {len(tvdb_ids)} Should be 4 and {len(tmdb_ids)} Should be 2")

        try:
            config.TVDb.get_items("tvdb_show", "https://www.thetvdb.com/series/arrow", "en", status_message=False)
            logger.info("Success | TVDb URL get TVDb Series ID")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | TVDb URL get TVDb Series ID: {e}")

        try:
            config.TVDb.get_items("tvdb_show", 279121, "en", status_message=False)
            logger.info("Success | TVDb ID get TVDb Series ID")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | TVDb ID get TVDb Series ID: {e}")

        try:
            config.TVDb.get_items("tvdb_movie", "https://www.thetvdb.com/movies/the-lord-of-the-rings-the-fellowship-of-the-ring", "en", status_message=False)
            logger.info("Success | TVDb URL get TVDb Movie ID")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | TVDb URL get TVDb Movie ID: {e}")

        try:
            config.TVDb.get_items("tvdb_movie", 107, "en", status_message=False)
            logger.info("Success | TVDb ID get TVDb Movie ID")
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Failure | TVDb ID get TVDb Movie ID: {e}")

    else:
        util.separator("TVDb Not Configured")
