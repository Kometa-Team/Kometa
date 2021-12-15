import argparse, logging, os, sys, time
from datetime import datetime
from logging.handlers import RotatingFileHandler
try:
    import plexapi, schedule
    from modules import util
    from modules.builder import CollectionBuilder
    from modules.config import ConfigFile
    from modules.meta import MetadataFile
    from modules.util import Failed, NotScheduled
except ModuleNotFoundError:
    print("Requirements Error: Requirements are not installed")
    sys.exit(0)

if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    print("Version Error: Version: %s.%s.%s incompatible please use Python 3.6+" % (sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("-db", "--debug", dest="debug", help=argparse.SUPPRESS, action="store_true", default=False)
parser.add_argument("-tr", "--trace", dest="trace", help=argparse.SUPPRESS, action="store_true", default=False)
parser.add_argument("-c", "--config", dest="config", help="Run with desired *.yml file", type=str)
parser.add_argument("-t", "--time", "--times", dest="times", help="Times to update each day use format HH:MM (Default: 03:00) (comma-separated list)", default="03:00", type=str)
parser.add_argument("-re", "--resume", dest="resume", help="Resume collection run from a specific collection", type=str)
parser.add_argument("-r", "--run", dest="run", help="Run without the scheduler", action="store_true", default=False)
parser.add_argument("-rt", "--test", "--tests", "--run-test", "--run-tests", dest="test", help="Run in debug mode with only collections that have test: true", action="store_true", default=False)
parser.add_argument("-co", "--collection-only", "--collections-only", dest="collection_only", help="Run only collection operations", action="store_true", default=False)
parser.add_argument("-lo", "--library-only", "--libraries-only", dest="library_only", help="Run only library operations", action="store_true", default=False)
parser.add_argument("-rc", "-cl", "--collection", "--collections", "--run-collection", "--run-collections", dest="collections", help="Process only specified collections (comma-separated list)", type=str)
parser.add_argument("-rl", "-l", "--library", "--libraries", "--run-library", "--run-libraries", dest="libraries", help="Process only specified libraries (comma-separated list)", type=str)
parser.add_argument("-nc", "--no-countdown", dest="no_countdown", help="Run without displaying the countdown", action="store_true", default=False)
parser.add_argument("-nm", "--no-missing", dest="no_missing", help="Run without running the missing section", action="store_true", default=False)
parser.add_argument("-d", "--divider", dest="divider", help="Character that divides the sections (Default: '=')", default="=", type=str)
parser.add_argument("-w", "--width", dest="width", help="Screen Width (Default: 100)", default=100, type=int)
args = parser.parse_args()

def get_arg(env_str, default, arg_bool=False, arg_int=False):
    env_var = os.environ.get(env_str)
    if env_var:
        if arg_bool:
            if env_var is True or env_var is False:
                return env_var
            elif env_var.lower() in ["t", "true"]:
                return True
            else:
                return False
        elif arg_int:
            return int(env_var)
        else:
            return str(env_var)
    else:
        return default

config_file = get_arg("PMM_CONFIG", args.config)
times = get_arg("PMM_TIME", args.times)
run = get_arg("PMM_RUN", args.run, arg_bool=True)
test = get_arg("PMM_TEST", args.test, arg_bool=True)
collection_only = get_arg("PMM_COLLECTIONS_ONLY", args.collection_only, arg_bool=True)
library_only = get_arg("PMM_LIBRARIES_ONLY", args.library_only, arg_bool=True)
collections = get_arg("PMM_COLLECTIONS", args.collections)
libraries = get_arg("PMM_LIBRARIES", args.libraries)
resume = get_arg("PMM_RESUME", args.resume)
no_countdown = get_arg("PMM_NO_COUNTDOWN", args.no_countdown, arg_bool=True)
no_missing = get_arg("PMM_NO_MISSING", args.no_missing, arg_bool=True)
divider = get_arg("PMM_DIVIDER", args.divider)
screen_width = get_arg("PMM_WIDTH", args.width, arg_int=True)
debug = get_arg("PMM_DEBUG", args.debug, arg_bool=True)
trace = get_arg("PMM_TRACE", args.trace, arg_bool=True)
stats = {}

util.separating_character = divider[0]

if screen_width < 90 or screen_width > 300:
    print(f"Argument Error: width argument invalid: {screen_width} must be an integer between 90 and 300 using the default 100")
    screen_width = 100
util.screen_width = screen_width

default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
if config_file and os.path.exists(config_file):
    default_dir = os.path.join(os.path.dirname(os.path.abspath(config_file)))
elif config_file and not os.path.exists(config_file):
    print(f"Config Error: config not found at {os.path.abspath(config_file)}")
    sys.exit(0)
elif not os.path.exists(os.path.join(default_dir, "config.yml")):
    print(f"Config Error: config not found at {os.path.abspath(default_dir)}")
    sys.exit(0)

os.makedirs(os.path.join(default_dir, "logs"), exist_ok=True)

logger = logging.getLogger("Plex Meta Manager")
logger.setLevel(logging.DEBUG)

def fmt_filter(record):
    record.levelname = f"[{record.levelname}]"
    record.filename = f"[{record.filename}:{record.lineno}]"
    return True

cmd_handler = logging.StreamHandler()
cmd_handler.setLevel(logging.DEBUG if test or debug or trace else logging.INFO)

logger.addHandler(cmd_handler)

sys.excepthook = util.my_except_hook

version = "Unknown"
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")) as handle:
    for line in handle.readlines():
        line = line.strip()
        if len(line) > 0:
            version = line
            break

def start(attrs):
    file_logger = os.path.join(default_dir, "logs", "meta.log")
    should_roll_over = os.path.isfile(file_logger)
    file_handler = RotatingFileHandler(file_logger, delay=True, mode="w", backupCount=10, encoding="utf-8")
    util.apply_formatter(file_handler)
    file_handler.addFilter(fmt_filter)
    if should_roll_over:
        file_handler.doRollover()
    logger.addHandler(file_handler)
    util.separator()
    logger.info("")
    logger.info(util.centered(" ____  _             __  __      _          __  __                                   "))
    logger.info(util.centered("|  _ \\| | _____  __ |  \\/  | ___| |_ __ _  |  \\/  | __ _ _ __   __ _  __ _  ___ _ __ "))
    logger.info(util.centered("| |_) | |/ _ \\ \\/ / | |\\/| |/ _ \\ __/ _` | | |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__|"))
    logger.info(util.centered("|  __/| |  __/>  <  | |  | |  __/ || (_| | | |  | | (_| | | | | (_| | (_| |  __/ |   "))
    logger.info(util.centered("|_|   |_|\\___/_/\\_\\ |_|  |_|\\___|\\__\\__,_| |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|   "))
    logger.info(util.centered("                                                                     |___/           "))
    logger.info(f"    Version: {version}")
    if "time" in attrs and attrs["time"]:                   start_type = f"{attrs['time']} "
    elif "test" in attrs and attrs["test"]:                 start_type = "Test "
    elif "collections" in attrs and attrs["collections"]:   start_type = "Collections "
    elif "libraries" in attrs and attrs["libraries"]:       start_type = "Libraries "
    else:                                                   start_type = ""
    start_time = datetime.now()
    if "time" not in attrs:
        attrs["time"] = start_time.strftime("%H:%M")
    attrs["time_obj"] = start_time
    util.separator(debug=True)
    logger.debug(f"--config (PMM_CONFIG): {config_file}")
    logger.debug(f"--time (PMM_TIME): {times}")
    logger.debug(f"--run (PMM_RUN): {run}")
    logger.debug(f"--run-tests (PMM_TEST): {test}")
    logger.debug(f"--collections-only (PMM_COLLECTIONS_ONLY): {collection_only}")
    logger.debug(f"--libraries-only (PMM_LIBRARIES_ONLY): {library_only}")
    logger.debug(f"--run-collections (PMM_COLLECTIONS): {collections}")
    logger.debug(f"--run-libraries (PMM_LIBRARIES): {libraries}")
    logger.debug(f"--resume (PMM_RESUME): {resume}")
    logger.debug(f"--no-countdown (PMM_NO_COUNTDOWN): {no_countdown}")
    logger.debug(f"--no-missing (PMM_NO_MISSING): {no_missing}")
    logger.debug(f"--divider (PMM_DIVIDER): {divider}")
    logger.debug(f"--width (PMM_WIDTH): {screen_width}")
    logger.debug(f"--debug (PMM_DEBUG): {debug}")
    logger.debug(f"--trace (PMM_TRACE): {trace}")
    logger.debug("")
    util.separator(f"Starting {start_type}Run")
    config = None
    global stats
    stats = {"created": 0, "modified": 0, "deleted": 0, "added": 0, "removed": 0, "radarr": 0, "sonarr": 0}
    try:
        config = ConfigFile(default_dir, attrs)
    except Exception as e:
        util.print_stacktrace()
        util.print_multiline(e, critical=True)
    else:
        try:
            update_libraries(config)
        except Exception as e:
            config.notify(e)
            util.print_stacktrace()
            util.print_multiline(e, critical=True)
    logger.info("")
    end_time = datetime.now()
    run_time = str(end_time - start_time).split('.')[0]
    if config:
        try:
            config.Webhooks.end_time_hooks(start_time, end_time, run_time, stats)
        except Failed as e:
            util.print_stacktrace()
            logger.error(f"Webhooks Error: {e}")
    util.separator(f"Finished {start_type}Run\nRun Time: {run_time}")
    logger.removeHandler(file_handler)

def update_libraries(config):
    global stats
    for library in config.libraries:
        try:
            os.makedirs(os.path.join(default_dir, "logs", library.mapping_name, "collections"), exist_ok=True)
            col_file_logger = os.path.join(default_dir, "logs", library.mapping_name, "library.log")
            should_roll_over = os.path.isfile(col_file_logger)
            library_handler = RotatingFileHandler(col_file_logger, delay=True, mode="w", backupCount=3, encoding="utf-8")
            util.apply_formatter(library_handler)
            if should_roll_over:
                library_handler.doRollover()
            logger.addHandler(library_handler)

            plexapi.server.TIMEOUT = library.timeout
            logger.info("")
            util.separator(f"{library.name} Library")

            logger.debug("")
            logger.debug(f"Mapping Name: {library.original_mapping_name}")
            logger.debug(f"Folder Name: {library.mapping_name}")
            logger.debug(f"Missing Path: {library.missing_path}")
            for ad in library.asset_directory:
                logger.debug(f"Asset Directory: {ad}")
            logger.debug(f"Asset Folders: {library.asset_folders}")
            logger.debug(f"Create Asset Folders: {library.create_asset_folders}")
            logger.debug(f"Sync Mode: {library.sync_mode}")
            logger.debug(f"Collection Minimum: {library.collection_minimum}")
            logger.debug(f"Delete Below Minimum: {library.delete_below_minimum}")
            logger.debug(f"Delete Not Scheduled: {library.delete_not_scheduled}")
            logger.debug(f"Missing Only Released: {library.missing_only_released}")
            logger.debug(f"Only Filter Missing: {library.only_filter_missing}")
            logger.debug(f"Show Unmanaged: {library.show_unmanaged}")
            logger.debug(f"Show Filtered: {library.show_filtered}")
            logger.debug(f"Show Missing: {library.show_missing}")
            logger.debug(f"Show Missing Assets: {library.show_missing_assets}")
            logger.debug(f"Save Missing: {library.save_missing}")
            logger.debug(f"Assets For All: {library.assets_for_all}")
            logger.debug(f"Delete Collections With Less: {library.delete_collections_with_less}")
            logger.debug(f"Delete Unmanaged Collections: {library.delete_unmanaged_collections}")
            logger.debug(f"Mass Genre Update: {library.mass_genre_update}")
            logger.debug(f"Mass Audience Rating Update: {library.mass_audience_rating_update}")
            logger.debug(f"Mass Critic Rating Update: {library.mass_critic_rating_update}")
            logger.debug(f"Mass Trakt Rating Update: {library.mass_trakt_rating_update}")
            logger.debug(f"Split Duplicates: {library.split_duplicates}")
            logger.debug(f"Radarr Add All: {library.radarr_add_all}")
            logger.debug(f"Sonarr Add All: {library.sonarr_add_all}")
            logger.debug(f"TMDb Collections: {library.tmdb_collections}")
            logger.debug(f"Genre Mapper: {library.genre_mapper}")
            logger.debug(f"Clean Bundles: {library.clean_bundles}")
            logger.debug(f"Empty Trash: {library.empty_trash}")
            logger.debug(f"Optimize: {library.optimize}")
            logger.debug(f"Timeout: {library.timeout}")

            if not library.is_other:
                logger.info("")
                util.separator(f"Mapping {library.name} Library", space=False, border=False)
                logger.info("")
                library.map_guids()
            for metadata in library.metadata_files:
                logger.info("")
                util.separator(f"Running Metadata File\n{metadata.path}")
                if not config.test_mode and not config.resume_from and not collection_only:
                    try:
                        metadata.update_metadata()
                    except Failed as e:
                        library.notify(e)
                        logger.error(e)
                collections_to_run = metadata.get_collections(config.requested_collections)
                if config.resume_from and config.resume_from not in collections_to_run:
                    logger.info("")
                    logger.warning(f"Collection: {config.resume_from} not in Metadata File: {metadata.path}")
                    continue
                if collections_to_run and not library_only:
                    logger.info("")
                    util.separator(f"{'Test ' if config.test_mode else ''}Collections")
                    logger.removeHandler(library_handler)
                    run_collection(config, library, metadata, collections_to_run)
                    logger.addHandler(library_handler)
            if library.run_sort:
                logger.info("")
                util.separator(f"Sorting {library.name} Library's Collections", space=False, border=False)
                logger.info("")
                for builder in library.run_sort:
                    logger.info("")
                    util.separator(f"Sorting {builder.name} Collection", space=False, border=False)
                    logger.info("")
                    builder.sort_collection()

            if not config.test_mode and not collection_only:
                library_operations(config, library)

            logger.removeHandler(library_handler)
        except Exception as e:
            library.notify(e)
            util.print_stacktrace()
            util.print_multiline(e, critical=True)

    has_run_again = False
    for library in config.libraries:
        if library.run_again:
            has_run_again = True
            break

    if has_run_again and not library_only:
        logger.info("")
        util.separator("Run Again")
        logger.info("")
        for x in range(1, config.general["run_again_delay"] + 1):
            util.print_return(f"Waiting to run again in {config.general['run_again_delay'] - x + 1} minutes")
            for y in range(60):
                time.sleep(1)
        util.print_end()
        for library in config.libraries:
            if library.run_again:
                try:
                    col_file_logger = os.path.join(default_dir, "logs", library.mapping_name, f"library.log")
                    library_handler = RotatingFileHandler(col_file_logger, mode="w", backupCount=3, encoding="utf-8")
                    util.apply_formatter(library_handler)
                    logger.addHandler(library_handler)
                    library_handler.addFilter(fmt_filter)
                    os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
                    logger.info("")
                    util.separator(f"{library.name} Library Run Again")
                    logger.info("")
                    library.map_guids()
                    for builder in library.run_again:
                        logger.info("")
                        util.separator(f"{builder.name} Collection")
                        logger.info("")
                        try:
                            builder.run_collections_again()
                        except Failed as e:
                            library.notify(e, collection=builder.name, critical=False)
                            util.print_stacktrace()
                            util.print_multiline(e, error=True)
                    logger.removeHandler(library_handler)
                except Exception as e:
                    library.notify(e)
                    util.print_stacktrace()
                    util.print_multiline(e, critical=True)

    used_url = []
    for library in config.libraries:
        if library.url not in used_url:
            used_url.append(library.url)
            if library.empty_trash:
                library.query(library.PlexServer.library.emptyTrash)
            if library.clean_bundles:
                library.query(library.PlexServer.library.cleanBundles)
            if library.optimize:
                library.query(library.PlexServer.library.optimize)

def library_operations(config, library):
    logger.info("")
    util.separator(f"{library.name} Library Operations")
    logger.info("")
    logger.debug(f"Assets For All: {library.assets_for_all}")
    logger.debug(f"Delete Collections With Less: {library.delete_collections_with_less}")
    logger.debug(f"Delete Unmanaged Collections: {library.delete_unmanaged_collections}")
    logger.debug(f"Mass Genre Update: {library.mass_genre_update}")
    logger.debug(f"Mass Audience Rating Update: {library.mass_audience_rating_update}")
    logger.debug(f"Mass Critic Rating Update: {library.mass_critic_rating_update}")
    logger.debug(f"Mass Trakt Rating Update: {library.mass_trakt_rating_update}")
    logger.debug(f"Split Duplicates: {library.split_duplicates}")
    logger.debug(f"Radarr Add All: {library.radarr_add_all}")
    logger.debug(f"Sonarr Add All: {library.sonarr_add_all}")
    logger.debug(f"TMDb Collections: {library.tmdb_collections}")
    logger.debug(f"Genre Mapper: {library.genre_mapper}")
    tmdb_operation = library.assets_for_all or library.mass_genre_update or library.mass_audience_rating_update \
                     or library.mass_critic_rating_update or library.mass_trakt_rating_update \
                     or library.tmdb_collections or library.radarr_add_all or library.sonarr_add_all
    logger.debug(f"TMDb Operation: {tmdb_operation}")

    if library.split_duplicates:
        items = library.search(**{"duplicate": True})
        for item in items:
            item.split()
            logger.info(util.adjust_space(f"{item.title[:25]:<25} | Splitting"))

    if tmdb_operation:
        items = library.get_all()
        radarr_adds = []
        sonarr_adds = []
        tmdb_collections = {}
        trakt_ratings = config.Trakt.user_ratings(library.is_movie) if library.mass_trakt_rating_update else []

        for i, item in enumerate(items, 1):
            try:
                library.reload(item)
            except Failed as e:
                logger.error(e)
                continue
            util.print_return(f"Processing: {i}/{len(items)} {item.title}")
            if library.assets_for_all:
                library.update_item_from_assets(item, create=library.create_asset_folders)
            tmdb_id = None
            tvdb_id = None
            imdb_id = None
            if config.Cache:
                t_id, i_id, guid_media_type, _ = config.Cache.query_guid_map(item.guid)
                if t_id:
                    if "movie" in guid_media_type:
                        tmdb_id = t_id[0]
                    else:
                        tvdb_id = t_id[0]
                if i_id:
                    imdb_id = i_id[0]
            if not tmdb_id and not tvdb_id:
                tmdb_id = library.get_tmdb_from_map(item)
            if not tmdb_id and not tvdb_id and library.is_show:
                tvdb_id = library.get_tvdb_from_map(item)

            if library.mass_trakt_rating_update:
                try:
                    if library.is_movie and tmdb_id in trakt_ratings:
                        new_rating = trakt_ratings[tmdb_id]
                    elif library.is_show and tvdb_id in trakt_ratings:
                        new_rating = trakt_ratings[tvdb_id]
                    else:
                        raise Failed
                    if str(item.userRating) != str(new_rating):
                        library.edit_query(item, {"userRating.value": new_rating, "userRating.locked": 1})
                        logger.info(util.adjust_space(f"{item.title[:25]:<25} | User Rating | {new_rating}"))
                except Failed:
                    pass

            path = os.path.dirname(str(item.locations[0])) if library.is_movie else str(item.locations[0])
            if library.Radarr and library.radarr_add_all and tmdb_id:
                path = path.replace(library.Radarr.plex_path, library.Radarr.radarr_path)
                path = path[:-1] if path.endswith(('/', '\\')) else path
                radarr_adds.append((tmdb_id, path))
            if library.Sonarr and library.sonarr_add_all and tvdb_id:
                path = path.replace(library.Sonarr.plex_path, library.Sonarr.sonarr_path)
                path = path[:-1] if path.endswith(('/', '\\')) else path
                sonarr_adds.append((tvdb_id, path))

            tmdb_item = None
            if library.tmdb_collections or library.mass_genre_update == "tmdb" or library.mass_audience_rating_update == "tmdb" or library.mass_critic_rating_update == "tmdb":
                if tvdb_id and not tmdb_id:
                    tmdb_id = config.Convert.tvdb_to_tmdb(tvdb_id)
                if tmdb_id:
                    try:
                        tmdb_item = config.TMDb.get_movie(tmdb_id) if library.is_movie else config.TMDb.get_show(tmdb_id)
                    except Failed as e:
                        logger.error(util.adjust_space(str(e)))
                else:
                    logger.info(util.adjust_space(f"{item.title[:25]:<25} | No TMDb ID for Guid: {item.guid}"))

            omdb_item = None
            if library.mass_genre_update in ["omdb", "imdb"] or library.mass_audience_rating_update in ["omdb", "imdb"] or library.mass_critic_rating_update in ["omdb", "imdb"]:
                if config.OMDb.limit is False:
                    if tmdb_id and not imdb_id:
                        imdb_id = config.Convert.tmdb_to_imdb(tmdb_id)
                    elif tvdb_id and not imdb_id:
                        imdb_id = config.Convert.tvdb_to_imdb(tvdb_id)
                    if imdb_id:
                        try:
                            omdb_item = config.OMDb.get_omdb(imdb_id)
                        except Failed as e:
                            logger.error(util.adjust_space(str(e)))
                        except Exception:
                            logger.error(f"IMDb ID: {imdb_id}")
                            raise
                    else:
                        logger.info(util.adjust_space(f"{item.title[:25]:<25} | No IMDb ID for Guid: {item.guid}"))

            tvdb_item = None
            if library.mass_genre_update == "tvdb":
                if tvdb_id:
                    try:
                        tvdb_item = config.TVDb.get_item(tvdb_id, library.is_movie)
                    except Failed as e:
                        logger.error(util.adjust_space(str(e)))
                else:
                    logger.info(util.adjust_space(f"{item.title[:25]:<25} | No TVDb ID for Guid: {item.guid}"))

            if library.tmdb_collections and tmdb_item and tmdb_item.belongs_to_collection:
                tmdb_collections[tmdb_item.belongs_to_collection.id] = tmdb_item.belongs_to_collection.name

            if library.mass_genre_update:
                try:
                    if tmdb_item and library.mass_genre_update == "tmdb":
                        new_genres = [genre.name for genre in tmdb_item.genres]
                    elif omdb_item and library.mass_genre_update in ["omdb", "imdb"]:
                        new_genres = omdb_item.genres
                    elif tvdb_item and library.mass_genre_update == "tvdb":
                        new_genres = tvdb_item.genres
                    else:
                        raise Failed
                    library.edit_tags("genre", item, sync_tags=new_genres)
                except Failed:
                    pass
            if library.mass_audience_rating_update:
                try:
                    if tmdb_item and library.mass_audience_rating_update == "tmdb":
                        new_rating = tmdb_item.vote_average
                    elif omdb_item and library.mass_audience_rating_update in ["omdb", "imdb"]:
                        new_rating = omdb_item.imdb_rating
                    else:
                        raise Failed
                    if new_rating is None:
                        logger.info(util.adjust_space(f"{item.title[:25]:<25} | No Rating Found"))
                    else:
                        if library.mass_audience_rating_update and str(item.audienceRating) != str(new_rating):
                            library.edit_query(item, {"audienceRating.value": new_rating, "audienceRating.locked": 1})
                            logger.info(util.adjust_space(f"{item.title[:25]:<25} | Audience Rating | {new_rating}"))
                except Failed:
                    pass
            if library.mass_critic_rating_update:
                try:
                    if tmdb_item and library.mass_critic_rating_update == "tmdb":
                        new_rating = tmdb_item.vote_average
                    elif omdb_item and library.mass_critic_rating_update in ["omdb", "imdb"]:
                        new_rating = omdb_item.imdb_rating
                    else:
                        raise Failed
                    if new_rating is None:
                        logger.info(util.adjust_space(f"{item.title[:25]:<25} | No Rating Found"))
                    else:
                        if library.mass_critic_rating_update and str(item.rating) != str(new_rating):
                            library.edit_query(item, {"rating.value": new_rating, "rating.locked": 1})
                            logger.info(util.adjust_space(f"{item.title[:25]:<25} | Critic Rating | {new_rating}"))
                except Failed:
                    pass
            if library.genre_mapper:
                try:
                    adds = []
                    deletes = []
                    library.reload(item)
                    for genre in item.genres:
                        if genre.tag in library.genre_mapper:
                            deletes.append(genre.tag)
                            adds.append(library.genre_mapper[genre.tag])
                    library.edit_tags("genre", item, add_tags=adds, remove_tags=deletes)
                except Failed:
                    pass

        if library.Radarr and library.radarr_add_all:
            try:
                library.Radarr.add_tmdb(radarr_adds)
            except Failed as e:
                logger.error(e)

        if library.Sonarr and library.sonarr_add_all:
            try:
                library.Sonarr.add_tvdb(sonarr_adds)
            except Failed as e:
                logger.error(e)

        if tmdb_collections:
            logger.info("")
            util.separator(f"Starting TMDb Collections")
            logger.info("")
            metadata = MetadataFile(config, library, "Data", {
                "collections": {
                    _n.replace(library.tmdb_collections["remove_suffix"], "").strip() if library.tmdb_collections["remove_suffix"] else _n:
                    {"template": {"name": "TMDb Collection", "collection_id": _i}}
                    for _i, _n in tmdb_collections.items() if int(_i) not in library.tmdb_collections["exclude_ids"]
                },
                "templates": {
                    "TMDb Collection": library.tmdb_collections["template"]
                }
            })
            run_collection(config, library, metadata, metadata.get_collections(None))

    if library.delete_collections_with_less is not None or library.delete_unmanaged_collections:
        logger.info("")
        suffix = ""
        unmanaged = ""
        if library.delete_collections_with_less is not None and library.delete_collections_with_less > 0:
            suffix = f" with less then {library.delete_collections_with_less} item{'s' if library.delete_collections_with_less > 1 else ''}"
        if library.delete_unmanaged_collections:
            if library.delete_collections_with_less is None:
                unmanaged = "Unmanaged Collections "
            elif library.delete_collections_with_less > 0:
                unmanaged = "Unmanaged Collections and "
        util.separator(f"Deleting All {unmanaged}Collections{suffix}", space=False, border=False)
        logger.info("")
    unmanaged_collections = []
    for col in library.get_all_collections():
        if (library.delete_collections_with_less is not None
            and (library.delete_collections_with_less == 0 or col.childCount < library.delete_collections_with_less)) \
            or (col.title not in library.collections and library.delete_unmanaged_collections):
            library.query(col.delete)
            logger.info(f"{col.title} Deleted")
        elif col.title not in library.collections:
            unmanaged_collections.append(col)

    if library.show_unmanaged and len(unmanaged_collections) > 0:
        logger.info("")
        util.separator(f"Unmanaged Collections in {library.name} Library", space=False, border=False)
        logger.info("")
        for col in unmanaged_collections:
            logger.info(col.title)
        logger.info("")
        logger.info(f"{len(unmanaged_collections)} Unmanaged Collection{'s' if len(unmanaged_collections) > 1 else ''}")
    elif library.show_unmanaged:
        logger.info("")
        util.separator(f"No Unmanaged Collections in {library.name} Library", space=False, border=False)
        logger.info("")

    if library.assets_for_all and len(unmanaged_collections) > 0:
        logger.info("")
        util.separator(f"Unmanaged Collection Assets Check for {library.name} Library", space=False, border=False)
        logger.info("")
        for col in unmanaged_collections:
            poster, background = library.find_collection_assets(col, create=library.create_asset_folders)
            library.upload_images(col, poster=poster, background=background)

def run_collection(config, library, metadata, requested_collections):
    global stats
    logger.info("")
    for mapping_name, collection_attrs in requested_collections.items():
        collection_start = datetime.now()
        if config.test_mode and ("test" not in collection_attrs or collection_attrs["test"] is not True):
            no_template_test = True
            if "template" in collection_attrs and collection_attrs["template"]:
                for data_template in util.get_list(collection_attrs["template"], split=False):
                    if "name" in data_template \
                            and data_template["name"] \
                            and metadata.templates \
                            and data_template["name"] in metadata.templates \
                            and metadata.templates[data_template["name"]] \
                            and "test" in metadata.templates[data_template["name"]] \
                            and metadata.templates[data_template["name"]]["test"] is True:
                        no_template_test = False
            if no_template_test:
                continue

        if config.resume_from and config.resume_from != mapping_name:
            continue
        elif config.resume_from == mapping_name:
            config.resume_from = None
            logger.info("")
            util.separator(f"Resuming Collections")

        if "name_mapping" in collection_attrs and collection_attrs["name_mapping"]:
            collection_log_name, output_str = util.validate_filename(collection_attrs["name_mapping"])
        else:
            collection_log_name, output_str = util.validate_filename(mapping_name)
        collection_log_folder = os.path.join(default_dir, "logs", library.mapping_name, "collections", collection_log_name)
        os.makedirs(collection_log_folder, exist_ok=True)
        col_file_logger = os.path.join(collection_log_folder, "collection.log")
        should_roll_over = os.path.isfile(col_file_logger)
        collection_handler = RotatingFileHandler(col_file_logger, delay=True, mode="w", backupCount=3, encoding="utf-8")
        util.apply_formatter(collection_handler)
        if should_roll_over:
            collection_handler.doRollover()
        logger.addHandler(collection_handler)

        try:
            util.separator(f"{mapping_name} Collection")
            logger.info("")
            if output_str:
                logger.info(output_str)
                logger.info("")

            util.separator(f"Validating {mapping_name} Attributes", space=False, border=False)

            builder = CollectionBuilder(config, library, metadata, mapping_name, no_missing, collection_attrs)
            logger.info("")

            util.separator(f"Running {mapping_name} Collection", space=False, border=False)

            if len(builder.schedule) > 0:
                util.print_multiline(builder.schedule, info=True)

            if len(builder.smart_filter_details) > 0:
                logger.info("")
                util.print_multiline(builder.smart_filter_details, info=True)

            items_added = 0
            items_removed = 0
            if not builder.smart_url and builder.builders:
                logger.info("")
                logger.info(f"Sync Mode: {'sync' if builder.sync else 'append'}")

                if builder.filters or builder.tmdb_filters:
                    logger.info("")
                    for filter_key, filter_value in builder.filters:
                        logger.info(f"Collection Filter {filter_key}: {filter_value}")
                    for filter_key, filter_value in builder.tmdb_filters:
                        logger.info(f"Collection Filter {filter_key}: {filter_value}")

                builder.find_rating_keys()

                if len(builder.rating_keys) >= builder.minimum and builder.build_collection:
                    logger.info("")
                    util.separator(f"Adding to {mapping_name} Collection", space=False, border=False)
                    logger.info("")
                    items_added = builder.add_to_collection()
                    stats["added"] += items_added
                    items_removed = 0
                    if builder.sync:
                        items_removed = builder.sync_collection()
                        stats["removed"] += items_removed
                elif len(builder.rating_keys) < builder.minimum and builder.build_collection:
                    logger.info("")
                    logger.info(f"Collection Minimum: {builder.minimum} not met for {mapping_name} Collection")
                    if builder.details["delete_below_minimum"] and builder.obj:
                        builder.delete_collection()
                        builder.deleted = True
                        logger.info("")
                        logger.info(f"Collection {builder.obj.title} deleted")

                if builder.do_missing and (len(builder.missing_movies) > 0 or len(builder.missing_shows) > 0):
                    if builder.details["show_missing"] is True:
                        logger.info("")
                        util.separator(f"Missing from Library", space=False, border=False)
                        logger.info("")
                    radarr_add, sonarr_add = builder.run_missing()
                    stats["radarr"] += radarr_add
                    stats["sonarr"] += sonarr_add

            run_item_details = True
            if builder.build_collection and (builder.builders or builder.smart_url):
                try:
                    builder.load_collection()
                    if builder.created:
                        stats["created"] += 1
                    elif items_added > 0 or items_removed > 0:
                        stats["modified"] += 1
                except Failed:
                    util.print_stacktrace()
                    run_item_details = False
                    logger.info("")
                    util.separator("No Collection to Update", space=False, border=False)
                else:
                    builder.update_details()
                    if builder.custom_sort or builder.sort_by:
                        library.run_sort.append(builder)
                        # builder.sort_collection()

            if builder.deleted:
                stats["deleted"] += 1

            if builder.server_preroll is not None:
                library.set_server_preroll(builder.server_preroll)
                logger.info("")
                logger.info(f"Plex Server Movie pre-roll video updated to {builder.server_preroll}")

            if builder.item_details and run_item_details and builder.builders:
                try:
                    builder.load_collection_items()
                except Failed:
                    logger.info("")
                    util.separator("No Items Found", space=False, border=False)
                else:
                    builder.update_item_details()

            builder.send_notifications()

            if builder.run_again and (len(builder.run_again_movies) > 0 or len(builder.run_again_shows) > 0):
                library.run_again.append(builder)


        except NotScheduled as e:
            util.print_multiline(e, info=True)
        except Failed as e:
            library.notify(e, collection=mapping_name)
            util.print_stacktrace()
            util.print_multiline(e, error=True)
        except Exception as e:
            library.notify(f"Unknown Error: {e}", collection=mapping_name)
            util.print_stacktrace()
            logger.error(f"Unknown Error: {e}")
        logger.info("")
        util.separator(f"Finished {mapping_name} Collection\nCollection Run Time: {str(datetime.now() - collection_start).split('.')[0]}")
        logger.removeHandler(collection_handler)

try:
    if run or test or collections or libraries or resume:
        start({
            "config_file": config_file,
            "test": test,
            "collections": collections,
            "libraries": libraries,
            "resume": resume,
            "trace": trace
        })
    else:
        times_to_run = util.get_list(times)
        valid_times = []
        for time_to_run in times_to_run:
            try:
                valid_times.append(datetime.strftime(datetime.strptime(time_to_run, "%H:%M"), "%H:%M"))
            except ValueError:
                if time_to_run:
                    raise Failed(f"Argument Error: time argument invalid: {time_to_run} must be in the HH:MM format")
                else:
                    raise Failed(f"Argument Error: blank time argument")
        for time_to_run in valid_times:
            schedule.every().day.at(time_to_run).do(start, {"config_file": config_file, "time": time_to_run, "trace": trace})
        while True:
            schedule.run_pending()
            if not no_countdown:
                current_time = datetime.now().strftime("%H:%M")
                seconds = None
                og_time_str = ""
                for time_to_run in valid_times:
                    new_seconds = (datetime.strptime(time_to_run, "%H:%M") - datetime.strptime(current_time, "%H:%M")).total_seconds()
                    if new_seconds < 0:
                        new_seconds += 86400
                    if (seconds is None or new_seconds < seconds) and new_seconds > 0:
                        seconds = new_seconds
                        og_time_str = time_to_run
                if seconds is not None:
                    hours = int(seconds // 3600)
                    minutes = int((seconds % 3600) // 60)
                    time_str = f"{hours} Hour{'s' if hours > 1 else ''} and " if hours > 0 else ""
                    time_str += f"{minutes} Minute{'s' if minutes > 1 else ''}"
                    util.print_return(f"Current Time: {current_time} | {time_str} until the next run at {og_time_str} | Runs: {', '.join(times_to_run)}")
                else:
                    logger.error(f"Time Error: {valid_times}")
            time.sleep(60)
except KeyboardInterrupt:
    util.separator("Exiting Plex Meta Manager")
