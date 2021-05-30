import argparse, logging, os, re, sys, time
from datetime import datetime
try:
    import schedule
    from modules import util
    from modules.builder import CollectionBuilder
    from modules.config import Config
    from modules.util import Failed
except ModuleNotFoundError:
    print("Requirements Error: Requirements are not installed")
    sys.exit(0)

if sys.version_info[0] != 3 or sys.version_info[1] < 6:
    print("Version Error: Version: %s.%s.%s incompatible please use Python 3.6+" % (sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("-db", "--debug", dest="debug", help=argparse.SUPPRESS, action="store_true", default=False)
parser.add_argument("-c", "--config", dest="config", help="Run with desired *.yml file", type=str)
parser.add_argument("-t", "--time", dest="time", help="Times to update each day use format HH:MM (Default: 03:00) (comma-separated list)", default="03:00", type=str)
parser.add_argument("-re", "--resume", dest="resume", help="Resume collection run from a specific collection", type=str)
parser.add_argument("-r", "--run", dest="run", help="Run without the scheduler", action="store_true", default=False)
parser.add_argument("-rt", "--test", "--tests", "--run-test", "--run-tests", dest="test", help="Run in debug mode with only collections that have test: true", action="store_true", default=False)
parser.add_argument("-co", "--collection-only", "--collections-only", dest="collection_only", help="Run only collection operations", action="store_true", default=False)
parser.add_argument("-lo", "--library-only", "--libraries-only", dest="library_only", help="Run only library operations", action="store_true", default=False)
parser.add_argument("-rc", "-cl", "--collection", "--collections", "--run-collection", "--run-collections", dest="collections", help="Process only specified collections (comma-separated list)", type=str)
parser.add_argument("-rl", "-l", "--library", "--libraries", "--run-library", "--run-libraries", dest="libraries", help="Process only specified libraries (comma-separated list)", type=str)
parser.add_argument("-nc", "--no-countdown", dest="no_countdown", help="Run without displaying the countdown", action="store_true", default=False)
parser.add_argument("-d", "--divider", dest="divider", help="Character that divides the sections (Default: '=')", default="=", type=str)
parser.add_argument("-w", "--width", dest="width", help="Screen Width (Default: 100)", default=100, type=int)
args = parser.parse_args()

def check_bool(env_str, default):
    env_var = os.environ.get(env_str)
    if env_var is not None:
        if env_var is True or env_var is False:
            return env_var
        elif env_var.lower() in ["t", "true"]:
            return True
        else:
            return False
    else:
        return default

test = check_bool("PMM_TEST", args.test)
debug = check_bool("PMM_DEBUG", args.debug)
run = check_bool("PMM_RUN", args.run)
no_countdown = check_bool("PMM_NO_COUNTDOWN", args.no_countdown)
library_only = check_bool("PMM_LIBRARIES_ONLY", args.library_only)
collection_only = check_bool("PMM_COLLECTIONS_ONLY", args.collection_only)
collections = os.environ.get("PMM_COLLECTIONS") if os.environ.get("PMM_COLLECTIONS") else args.collections
libraries = os.environ.get("PMM_LIBRARIES") if os.environ.get("PMM_LIBRARIES") else args.libraries
resume = os.environ.get("PMM_RESUME") if os.environ.get("PMM_RESUME") else args.resume

times_to_run = util.get_list(os.environ.get("PMM_TIME") if os.environ.get("PMM_TIME") else args.time)
for time_to_run in times_to_run:
    if not re.match("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", time_to_run):
        raise util.Failed(f"Argument Error: time argument invalid: {time_to_run} must be in the HH:MM format")

util.separating_character = os.environ.get("PMM_DIVIDER")[0] if os.environ.get("PMM_DIVIDER") else args.divider[0]

screen_width = os.environ.get("PMM_WIDTH") if os.environ.get("PMM_WIDTH") else args.width
if 90 <= screen_width <= 300:
    util.screen_width = screen_width
else:
    raise util.Failed(f"Argument Error: width argument invalid: {screen_width} must be an integer between 90 and 300")

config_file = os.environ.get("PMM_CONFIG") if os.environ.get("PMM_CONFIG") else args.config
default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
if config_file and os.path.exists(config_file):                     default_dir = os.path.join(os.path.dirname(os.path.abspath(config_file)))
elif config_file and not os.path.exists(config_file):               raise util.Failed(f"Config Error: config not found at {os.path.abspath(config_file)}")
elif not os.path.exists(os.path.join(default_dir, "config.yml")):   raise util.Failed(f"Config Error: config not found at {os.path.abspath(default_dir)}")

os.makedirs(os.path.join(default_dir, "logs"), exist_ok=True)

logger = logging.getLogger("Plex Meta Manager")
logger.setLevel(logging.DEBUG)

def fmt_filter(record):
    record.levelname = f"[{record.levelname}]"
    record.filename = f"[{record.filename}:{record.lineno}]"
    return True

cmd_handler = logging.StreamHandler()
cmd_handler.setLevel(logging.DEBUG if test or debug else logging.INFO)

logger.addHandler(cmd_handler)

sys.excepthook = util.my_except_hook

def start(config_path, is_test=False, time_scheduled=None, requested_collections=None, requested_libraries=None, resume_from=None):
    file_logger = os.path.join(default_dir, "logs", "meta.log")
    should_roll_over = os.path.isfile(file_logger)
    file_handler = logging.handlers.RotatingFileHandler(file_logger, delay=True, mode="w", backupCount=10, encoding="utf-8")
    util.apply_formatter(file_handler)
    file_handler.addFilter(fmt_filter)
    if should_roll_over:
        file_handler.doRollover()
    logger.addHandler(file_handler)
    util.separator()
    logger.info(util.centered("                                                                                     "))
    logger.info(util.centered(" ____  _             __  __      _          __  __                                   "))
    logger.info(util.centered("|  _ \\| | _____  __ |  \\/  | ___| |_ __ _  |  \\/  | __ _ _ __   __ _  __ _  ___ _ __ "))
    logger.info(util.centered("| |_) | |/ _ \\ \\/ / | |\\/| |/ _ \\ __/ _` | | |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__|"))
    logger.info(util.centered("|  __/| |  __/>  <  | |  | |  __/ || (_| | | |  | | (_| | | | | (_| | (_| |  __/ |   "))
    logger.info(util.centered("|_|   |_|\\___/_/\\_\\ |_|  |_|\\___|\\__\\__,_| |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|   "))
    logger.info(util.centered("                                                                     |___/           "))
    logger.info(util.centered("    Version: 1.10.0                                                                  "))
    if time_scheduled:              start_type = f"{time_scheduled} "
    elif is_test:                   start_type = "Test "
    elif requested_collections:     start_type = "Collections "
    elif requested_libraries:       start_type = "Libraries "
    else:                           start_type = ""
    start_time = datetime.now()
    if time_scheduled is None:
        time_scheduled = start_time.strftime("%H:%M")
    util.separator(f"Starting {start_type}Run")
    try:
        config = Config(default_dir, config_path=config_path, is_test=is_test,
                        time_scheduled=time_scheduled, requested_collections=requested_collections,
                        requested_libraries=requested_libraries, resume_from=resume_from)
        update_libraries(config)
    except Exception as e:
        util.print_stacktrace()
        logger.critical(e)
    logger.info("")
    util.separator(f"Finished {start_type}Run\nRun Time: {str(datetime.now() - start_time).split('.')[0]}")
    logger.removeHandler(file_handler)

def update_libraries(config):
    for library in config.libraries:
        os.makedirs(os.path.join(default_dir, "logs", library.mapping_name, "collections"), exist_ok=True)
        col_file_logger = os.path.join(default_dir, "logs", library.mapping_name, "library.log")
        should_roll_over = os.path.isfile(col_file_logger)
        library_handler = logging.handlers.RotatingFileHandler(col_file_logger, delay=True, mode="w", backupCount=3, encoding="utf-8")
        util.apply_formatter(library_handler)
        if should_roll_over:
            library_handler.doRollover()
        logger.addHandler(library_handler)

        os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
        logger.info("")
        util.separator(f"{library.name} Library")
        logger.info("")
        util.separator(f"Mapping {library.name} Library", space=False, border=False)
        logger.info("")
        library.map_guids(config)
        if not config.test_mode and not config.resume_from and not collection_only and library.mass_update:
            mass_metadata(config, library)
        for metadata in library.metadata_files:
            logger.info("")
            util.separator(f"Running Metadata File\n{metadata.path}")
            if not config.test_mode and not config.resume_from and not collection_only:
                try:
                    metadata.update_metadata(config.TMDb, config.test_mode)
                except Failed as e:
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

        if not config.test_mode and not config.requested_collections and ((library.show_unmanaged and not library_only) or (library.assets_for_all and not collection_only)):
            logger.info("")
            util.separator(f"Other {library.name} Library Operations")
            unmanaged_collections = []
            for col in library.get_all_collections():
                if col.title not in library.collections:
                    unmanaged_collections.append(col)

            if library.show_unmanaged and not library_only:
                logger.info("")
                util.separator(f"Unmanaged Collections in {library.name} Library", space=False, border=False)
                logger.info("")
                for col in unmanaged_collections:
                    logger.info(col.title)
                logger.info("")
                logger.info(f"{len(unmanaged_collections)} Unmanaged Collections")

            if library.assets_for_all and not collection_only:
                logger.info("")
                util.separator(f"All {'Movies' if library.is_movie else 'Shows'} Assets Check for {library.name} Library", space=False, border=False)
                logger.info("")
                for col in unmanaged_collections:
                    library.update_item_from_assets(col, collection_mode=True)
                for item in library.get_all():
                    library.update_item_from_assets(item)

        logger.removeHandler(library_handler)

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
                col_file_logger = os.path.join(default_dir, "logs", library.mapping_name, f"library.log")
                library_handler = logging.handlers.RotatingFileHandler(col_file_logger, mode="w", backupCount=3, encoding="utf-8")
                util.apply_formatter(library_handler)
                logger.addHandler(library_handler)
                library_handler.addFilter(fmt_filter)
                os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
                logger.info("")
                util.separator(f"{library.name} Library Run Again")
                logger.info("")
                library.map_guids(config)
                for builder in library.run_again:
                    logger.info("")
                    util.separator(f"{builder.name} Collection")
                    logger.info("")
                    try:
                        builder.run_collections_again()
                    except Failed as e:
                        util.print_stacktrace()
                        util.print_multiline(e, error=True)
                logger.removeHandler(library_handler)

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

def mass_metadata(config, library):
    logger.info("")
    util.separator(f"Mass Editing {'Movie' if library.is_movie else 'Show'} Library: {library.name}")
    logger.info("")
    radarr_adds = []
    sonarr_adds = []
    items = library.Plex.all()
    for i, item in enumerate(items, 1):
        util.print_return(f"Processing: {i}/{len(items)} {item.title}")
        tmdb_id = None
        tvdb_id = None
        imdb_id = None
        if config.Cache:
            t_id, guid_media_type, _ = config.Cache.query_guid_map(item.guid)
            if t_id:
                if "movie" in guid_media_type:
                    tmdb_id = t_id
                else:
                    tvdb_id = t_id
        if not tmdb_id and not tvdb_id:
            tmdb_id = library.get_tmdb_from_map(item)
        if not tmdb_id and not tvdb_id and library.is_show:
            tmdb_id = library.get_tvdb_from_map(item)

        if library.Radarr and library.radarr_add_all and tmdb_id:
            radarr_adds.append(tmdb_id)
        if library.Sonarr and library.sonarr_add_all and tvdb_id:
            sonarr_adds.append(tvdb_id)

        tmdb_item = None
        if library.mass_genre_update == "tmdb" or library.mass_audience_rating_update == "tmdb" or library.mass_critic_rating_update == "tmdb":
            if tvdb_id and not tmdb_id:
                tmdb_id = config.Convert.tvdb_to_tmdb(tvdb_id)
            if tmdb_id:
                try:
                    tmdb_item = config.TMDb.get_movie(tmdb_id) if library.is_movie else config.TMDb.get_show(tmdb_id)
                except Failed as e:
                    logger.info(util.adjust_space(str(e)))
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
                        logger.info(util.adjust_space(str(e)))
                else:
                    logger.info(util.adjust_space(f"{item.title[:25]:<25} | No IMDb ID for Guid: {item.guid}"))

        if not tmdb_item and not omdb_item:
            continue

        if library.mass_genre_update:
            try:
                if tmdb_item and library.mass_genre_update == "tmdb":
                    new_genres = [genre.name for genre in tmdb_item.genres]
                elif omdb_item and library.mass_genre_update in ["omdb", "imdb"]:
                    new_genres = omdb_item.genres
                else:
                    raise Failed
                item_genres = [genre.tag for genre in item.genres]
                display_str = ""
                for genre in (g for g in item_genres if g not in new_genres):
                    library.query_data(item.removeGenre, genre)
                    display_str += f"{', ' if len(display_str) > 0 else ''}-{genre}"
                for genre in (g for g in new_genres if g not in item_genres):
                    library.query_data(item.addGenre, genre)
                    display_str += f"{', ' if len(display_str) > 0 else ''}+{genre}"
                if len(display_str) > 0:
                    logger.info(util.adjust_space(f"{item.title[:25]:<25} | Genres | {display_str}"))
            except Failed:
                pass
        if library.mass_audience_rating_update or library.mass_critic_rating_update:
            try:
                if tmdb_item and library.mass_genre_update == "tmdb":
                    new_rating = tmdb_item.vote_average
                elif omdb_item and library.mass_genre_update in ["omdb", "imdb"]:
                    new_rating = omdb_item.imdb_rating
                else:
                    raise Failed
                if new_rating is None:
                    logger.info(util.adjust_space(f"{item.title[:25]:<25} | No Rating Found"))
                else:
                    if library.mass_audience_rating_update and str(item.audienceRating) != str(new_rating):
                        library.edit_query(item, {"audienceRating.value": new_rating, "audienceRating.locked": 1})
                        logger.info(util.adjust_space(f"{item.title[:25]:<25} | Audience Rating | {new_rating}"))
                    if library.mass_critic_rating_update and str(item.rating) != str(new_rating):
                        library.edit_query(item, {"rating.value": new_rating, "rating.locked": 1})
                        logger.info(util.adjust_space(f"{item.title[:25]:<25} | Critic Rating | {new_rating}"))
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

def run_collection(config, library, metadata, requested_collections):
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
        col_file_logger = os.path.join(collection_log_folder, f"collection.log")
        should_roll_over = os.path.isfile(col_file_logger)
        collection_handler = logging.handlers.RotatingFileHandler(col_file_logger, delay=True, mode="w", backupCount=3, encoding="utf-8")
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

            builder = CollectionBuilder(config, library, metadata, mapping_name, collection_attrs)
            logger.info("")

            util.separator(f"Building {mapping_name} Collection", space=False, border=False)

            if len(builder.schedule) > 0:
                util.print_multiline(builder.schedule, info=True)

            if len(builder.smart_filter_details) > 0:
                logger.info("")
                util.print_multiline(builder.smart_filter_details, info=True)

            if not builder.smart_url:
                logger.info("")
                logger.info(f"Sync Mode: {'sync' if builder.sync else 'append'}")

                if len(builder.filters) > 0:
                    logger.info("")
                    for filter_key, filter_value in builder.filters:
                        logger.info(f"Collection Filter {filter_key}: {filter_value}")

                builder.collect_rating_keys()

                if len(builder.rating_keys) > 0 and builder.build_collection:
                    logger.info("")
                    util.separator(f"Adding to {mapping_name} Collection", space=False, border=False)
                    logger.info("")
                    builder.add_to_collection()
                if len(builder.missing_movies) > 0 or len(builder.missing_shows) > 0:
                    logger.info("")
                    util.separator(f"Missing from Library", space=False, border=False)
                    logger.info("")
                    builder.run_missing()
                if builder.sync and len(builder.rating_keys) > 0 and builder.build_collection:
                    builder.sync_collection()

            if builder.build_collection:
                logger.info("")
                util.separator(f"Updating Details of {mapping_name} Collection", space=False, border=False)
                logger.info("")
                builder.update_details()

            if len(builder.item_details) > 0:
                logger.info("")
                util.separator(f"Updating Details of the Items in  {mapping_name} Collection", space=False, border=False)
                logger.info("")
                builder.update_item_details()

            if builder.run_again and (len(builder.run_again_movies) > 0 or len(builder.run_again_shows) > 0):
                library.run_again.append(builder)

        except Failed as e:
            util.print_stacktrace()
            util.print_multiline(e, error=True)
        except Exception as e:
            util.print_stacktrace()
            logger.error(f"Unknown Error: {e}")
        logger.info("")
        util.separator(f"Finished {mapping_name} Collection\nCollection Run Time: {str(datetime.now() - collection_start).split('.')[0]}")
        logger.removeHandler(collection_handler)

try:
    if run or test or collections or libraries or resume:
        start(config_file, is_test=test, requested_collections=collections, requested_libraries=libraries, resume_from=resume)
    else:
        for time_to_run in times_to_run:
            schedule.every().day.at(time_to_run).do(start, config_file, time_scheduled=time_to_run)
        while True:
            schedule.run_pending()
            if not no_countdown:
                current = datetime.now().strftime("%H:%M")
                seconds = None
                og_time_str = ""
                for time_to_run in times_to_run:
                    new_seconds = (datetime.strptime(time_to_run, "%H:%M") - datetime.strptime(current, "%H:%M")).total_seconds()
                    if new_seconds < 0:
                        new_seconds += 86400
                    if (seconds is None or new_seconds < seconds) and new_seconds > 0:
                        seconds = new_seconds
                        og_time_str = time_to_run
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                time_str = f"{hours} Hour{'s' if hours > 1 else ''} and " if hours > 0 else ""
                time_str += f"{minutes} Minute{'s' if minutes > 1 else ''}"
                util.print_return(f"Current Time: {current} | {time_str} until the next run at {og_time_str} {times_to_run}")
            time.sleep(60)
except KeyboardInterrupt:
    util.separator("Exiting Plex Meta Manager")
