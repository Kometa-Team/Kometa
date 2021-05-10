import argparse, logging, os, re, sys, time
from datetime import datetime
try:
    import schedule
    from modules import util
    from modules.builder import CollectionBuilder
    from modules.config import Config
    from modules.util import Failed
    from plexapi.exceptions import BadRequest
except ModuleNotFoundError:
    print("Error: Requirements are not installed")
    sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("-db", "--debug", dest="debug", help=argparse.SUPPRESS, action="store_true", default=False)
parser.add_argument("-c", "--config", dest="config", help="Run with desired *.yml file", type=str)
parser.add_argument("-t", "--time", dest="time", help="Time to update each day use format HH:MM (Default: 03:00)", default="03:00", type=str)
parser.add_argument("-re", "--resume", dest="resume", help="Resume collection run from a specific collection", type=str)
parser.add_argument("-r", "--run", dest="run", help="Run without the scheduler", action="store_true", default=False)
parser.add_argument("-rt", "--test", "--tests", "--run-test", "--run-tests", dest="test", help="Run in debug mode with only collections that have test: true", action="store_true", default=False)
parser.add_argument("-cl", "--collection", "--collections", dest="collections", help="Process only specified collections (comma-separated list)", type=str)
parser.add_argument("-l", "--library", "--libraries", dest="libraries", help="Process only specified libraries (comma-separated list)", type=str)
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
collections = os.environ.get("PMM_COLLECTIONS") if os.environ.get("PMM_COLLECTIONS") else args.collections
libraries = os.environ.get("PMM_LIBRARIES") if os.environ.get("PMM_LIBRARIES") else args.libraries
resume = os.environ.get("PMM_RESUME") if os.environ.get("PMM_RESUME") else args.resume

time_to_run = os.environ.get("PMM_TIME") if os.environ.get("PMM_TIME") else args.time
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

file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(default_dir, "logs", "meta.log"), when="midnight", backupCount=10, encoding="utf-8")
file_handler.addFilter(fmt_filter)
file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(filename)-27s %(levelname)-10s | %(message)-100s |"))

cmd_handler = logging.StreamHandler()
cmd_handler.setFormatter(logging.Formatter("| %(message)-100s |"))
cmd_handler.setLevel(logging.DEBUG if test or debug else logging.INFO)

logger.addHandler(cmd_handler)
logger.addHandler(file_handler)

sys.excepthook = util.my_except_hook

util.separator()
util.centered("                                                                                     ")
util.centered(" ____  _             __  __      _          __  __                                   ")
util.centered("|  _ \\| | _____  __ |  \\/  | ___| |_ __ _  |  \\/  | __ _ _ __   __ _  __ _  ___ _ __ ")
util.centered("| |_) | |/ _ \\ \\/ / | |\\/| |/ _ \\ __/ _` | | |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__|")
util.centered("|  __/| |  __/>  <  | |  | |  __/ || (_| | | |  | | (_| | | | | (_| | (_| |  __/ |   ")
util.centered("|_|   |_|\\___/_/\\_\\ |_|  |_|\\___|\\__\\__,_| |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|   ")
util.centered("                                                                     |___/           ")
util.centered("    Version: 1.9.0-beta3                                                             ")
util.separator()

def start(config_path, is_test, daily, requested_collections, requested_libraries, resume_from):
    if daily:                       start_type = "Daily "
    elif is_test:                   start_type = "Test "
    elif requested_collections:     start_type = "Collections "
    elif requested_libraries:       start_type = "Libraries "
    else:                           start_type = ""
    start_time = datetime.now()
    util.separator(f"Starting {start_type}Run")
    try:
        config = Config(default_dir, config_path, requested_libraries)
        update_libraries(config, is_test, requested_collections, resume_from)
    except Exception as e:
        util.print_stacktrace()
        logger.critical(e)
    logger.info("")
    util.separator(f"Finished {start_type}Run\nRun Time: {str(datetime.now() - start_time).split('.')[0]}")

def update_libraries(config, is_test, requested_collections, resume_from):
    for library in config.libraries:
        os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
        logger.info("")
        util.separator(f"{library.name} Library")
        logger.info("")
        util.separator(f"Mapping {library.name} Library")
        logger.info("")
        movie_map, show_map = map_guids(config, library)
        if not is_test and not resume_from and library.mass_update:
            mass_metadata(config, library, movie_map, show_map)
        for metadata in library.metadata_files:
            logger.info("")
            util.separator(f"Running Metadata File\n{metadata.path}")
            if not is_test and not resume_from:
                try:
                    metadata.update_metadata(config.TMDb, is_test)
                except Failed as e:
                    logger.error(e)
            logger.info("")
            util.separator(f"{'Test ' if is_test else ''}Collections")
            collections_to_run = metadata.get_collections(requested_collections)
            if resume_from and resume_from not in collections_to_run:
                logger.warning(f"Collection: {resume_from} not in Metadata File: {metadata.path}")
                continue
            if collections_to_run:
                resume_from = run_collection(config, library, metadata, collections_to_run, is_test, resume_from, movie_map, show_map)

        if library.show_unmanaged is True and not is_test and not requested_collections:
            logger.info("")
            util.separator(f"Unmanaged Collections in {library.name} Library")
            logger.info("")
            unmanaged_count = 0
            collections_in_plex = [str(plex_col) for plex_col in library.collections]
            for col in library.get_all_collections():
                if col.title not in collections_in_plex:
                    logger.info(col.title)
                    unmanaged_count += 1
            logger.info("{} Unmanaged Collections".format(unmanaged_count))

        if library.assets_for_all is True and not is_test and not requested_collections:
            logger.info("")
            util.separator(f"All {'Movies' if library.is_movie else 'Shows'} Assets Check for {library.name} Library")
            logger.info("")
            for item in library.get_all():
                library.update_item_from_assets(item)
    has_run_again = False
    for library in config.libraries:
        if library.run_again:
            has_run_again = True
            break

    if has_run_again:
        logger.info("")
        util.separator("Run Again")
        logger.info("")
        length = 0
        for x in range(1, config.general["run_again_delay"] + 1):
            length = util.print_return(length, f"Waiting to run again in {config.general['run_again_delay'] - x + 1} minutes")
            for y in range(60):
                time.sleep(1)
        util.print_end(length)
        for library in config.libraries:
            if library.run_again:
                os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
                logger.info("")
                util.separator(f"{library.name} Library Run Again")
                logger.info("")
                movie_map, show_map = map_guids(config, library)
                for builder in library.run_again:
                    logger.info("")
                    util.separator(f"{builder.name} Collection")
                    logger.info("")
                    try:
                        collection_obj = library.get_collection(builder.name)
                    except Failed as e:
                        util.print_multiline(e, error=True)
                        continue
                    builder.run_collections_again(collection_obj, movie_map, show_map)

def run_collection(config, library, metadata, requested_collections, is_test, resume_from, movie_map, show_map):
    for mapping_name, collection_attrs in requested_collections.items():
        if is_test and ("test" not in collection_attrs or collection_attrs["test"] is not True):
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
        try:
            if resume_from and resume_from != mapping_name:
                continue
            elif resume_from == mapping_name:
                resume_from = None
                logger.info("")
                util.separator(f"Resuming Collections")

            logger.info("")
            util.separator(f"{mapping_name} Collection")
            logger.info("")

            try:
                builder = CollectionBuilder(config, library, metadata, mapping_name, collection_attrs)
            except Failed as f:
                util.print_stacktrace()
                util.print_multiline(f, error=True)
                continue
            except Exception as e:
                util.print_stacktrace()
                logger.error(e)
                continue

            try:
                collection_obj = library.get_collection(mapping_name)
                collection_name = collection_obj.title
                collection_smart = library.smart(collection_obj)
                if (builder.smart and not collection_smart) or (not builder.smart and collection_smart):
                    logger.info("")
                    logger.error(f"Collection Error: Converting {collection_obj.title} to a {'smart' if builder.smart else 'normal'} collection")
                    library.query(collection_obj.delete)
                    collection_obj = None
            except Failed:
                collection_obj = None
                collection_name = mapping_name

            if len(builder.schedule) > 0:
                util.print_multiline(builder.schedule, info=True)

            rating_key_map = {}
            logger.info("")
            if builder.sync:
                logger.info("Sync Mode: sync")
                if collection_obj:
                    for item in library.get_collection_items(collection_obj, builder.smart_label_collection):
                        rating_key_map[item.ratingKey] = item
            else:
                logger.info("Sync Mode: append")

            for i, f in enumerate(builder.filters):
                if i == 0:
                    logger.info("")
                logger.info(f"Collection Filter {f[0]}: {f[1]}")

            if not builder.smart_url:
                builder.run_methods(collection_obj, collection_name, rating_key_map, movie_map, show_map)

            try:
                if not collection_obj and builder.smart_url:
                    library.create_smart_collection(collection_name, builder.smart_type_key, builder.smart_url)
                elif not collection_obj and builder.smart_label_collection:
                    library.create_smart_labels(collection_name, sort=builder.smart_sort)
                plex_collection = library.get_collection(collection_name)
            except Failed as e:
                util.print_stacktrace()
                logger.error(e)
                continue

            builder.update_details(plex_collection)

            if builder.run_again and (len(builder.missing_movies) > 0 or len(builder.missing_shows) > 0):
                library.run_again.append(builder)

        except Exception as e:
            util.print_stacktrace()
            logger.error(f"Unknown Error: {e}")
    return resume_from

def mass_metadata(config, library, movie_map, show_map):
    length = 0
    logger.info("")
    util.separator(f"Mass Editing {'Movie' if library.is_movie else 'Show'} Library: {library.name}")
    logger.info("")
    items = library.Plex.all()
    for i, item in enumerate(items, 1):
        length = util.print_return(length, f"Processing: {i}/{len(items)} {item.title}")
        tmdb_id = None
        tvdb_id = None
        imdb_id = None
        if config.Cache:
            t_id, guid_media_type, _ = config.Cache.config.Cache.query_guid_map(item.guid)
            if t_id:
                if "movie" in guid_media_type:
                    tmdb_id = t_id
                else:
                    tvdb_id = t_id
        if not tmdb_id and not tvdb_id:
            for tmdb, rating_keys in movie_map.items():
                if item.ratingKey in rating_keys:
                    tmdb_id = tmdb
                    break
        if not tmdb_id and not tvdb_id and library.is_show:
            for tvdb, rating_keys in show_map.items():
                if item.ratingKey in rating_keys:
                    tvdb_id = tvdb
                    break
        if tmdb_id:
            imdb_id = config.Convert.tmdb_to_imdb(tmdb_id)
        elif tvdb_id:
            tmdb_id = config.Convert.tvdb_to_tmdb(tvdb_id)
            imdb_id = config.Convert.tvdb_to_imdb(tvdb_id)

        tmdb_item = None
        if library.mass_genre_update == "tmdb" or library.mass_audience_rating_update == "tmdb":
            if tmdb_id:
                try:
                    tmdb_item = config.TMDb.get_movie(tmdb_id) if library.is_movie else config.TMDb.get_show(tmdb_id)
                except Failed as e:
                    util.print_end(length, str(e))
            else:
                util.print_end(length, f"{item.title[:25]:<25} | No TMDb ID for Guid: {item.guid}")

        omdb_item = None
        if library.mass_genre_update in ["omdb", "imdb"] or library.mass_audience_rating_update in ["omdb", "imdb"]:
            if config.OMDb.limit is False:
                if imdb_id:
                    try:
                        omdb_item = config.OMDb.get_omdb(imdb_id)
                    except Failed as e:
                        util.print_end(length, str(e))
                else:
                    util.print_end(length, f"{item.title[:25]:<25} | No IMDb ID for Guid: {item.guid}")

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
                    util.print_end(length, f"{item.title[:25]:<25} | Genres | {display_str}")
            except Failed:
                pass
        if library.mass_audience_rating_update:
            try:
                if tmdb_item and library.mass_genre_update == "tmdb":
                    new_rating = tmdb_item.vote_average
                elif omdb_item and library.mass_genre_update in ["omdb", "imdb"]:
                    new_rating = omdb_item.imdb_rating
                else:
                    raise Failed
                if new_rating is None:
                    util.print_end(length, f"{item.title[:25]:<25} | No Rating Found")
                elif str(item.audienceRating) != str(new_rating):
                    library.edit_query(item, {"audienceRating.value": new_rating, "audienceRating.locked": 1})
                    util.print_end(length, f"{item.title[:25]:<25} | Audience Rating | {new_rating}")
            except Failed:
                pass

def map_guids(config, library):
    movie_map = {}
    show_map = {}
    length = 0
    logger.info(f"Mapping {'Movie' if library.is_movie else 'Show'} Library: {library.name}")
    items = library.Plex.all()
    for i, item in enumerate(items, 1):
        length = util.print_return(length, f"Processing: {i}/{len(items)} {item.title}")
        try:
            id_type, main_id = config.Convert.get_id(item, library, length)
        except BadRequest:
            util.print_stacktrace()
            util.print_end(length, f"{'Cache | ! |' if config.Cache else 'Mapping Error:'} | {item.guid} for {item.title} not found")
            continue
        if not isinstance(main_id, list):
            main_id = [main_id]
        if id_type == "movie":
            for m in main_id:
                if m in movie_map:              movie_map[m].append(item.ratingKey)
                else:                           movie_map[m] = [item.ratingKey]
        elif id_type == "show":
            for m in main_id:
                if m in show_map:               show_map[m].append(item.ratingKey)
                else:                           show_map[m] = [item.ratingKey]
    util.print_end(length, f"Processed {len(items)} {'Movies' if library.is_movie else 'Shows'}")
    return movie_map, show_map

try:
    if run or test or collections or libraries or resume:
        start(config_file, test, False, collections, libraries, resume)
    else:
        time_length = 0
        schedule.every().day.at(time_to_run).do(start, config_file, False, True, None, None, None)
        while True:
            schedule.run_pending()
            current = datetime.now().strftime("%H:%M")
            seconds = (datetime.strptime(time_to_run, "%H:%M") - datetime.strptime(current, "%H:%M")).total_seconds()
            hours = int(seconds // 3600)
            if hours < 0:
                hours += 24
            minutes = int((seconds % 3600) // 60)
            time_str = f"{hours} Hour{'s' if hours > 1 else ''} and " if hours > 0 else ""
            time_str += f"{minutes} Minute{'s' if minutes > 1 else ''}"

            time_length = util.print_return(time_length, f"Current Time: {current} | {time_str} until the daily run at {time_to_run}")
            time.sleep(1)
except KeyboardInterrupt:
    util.separator("Exiting Plex Meta Manager")
