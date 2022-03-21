import argparse, os, sys, time, traceback
from datetime import datetime

try:
    import plexapi, requests, schedule
    from modules.logs import MyLogger
    from plexapi.exceptions import NotFound
    from plexapi.video import Show, Season
    from ruamel import yaml
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
parser.add_argument("-is", "--ignore-schedules", dest="ignore_schedules", help="Run ignoring collection schedules", action="store_true", default=False)
parser.add_argument("-ig", "--ignore-ghost", dest="ignore_ghost", help="Run ignoring ghost logging", action="store_true", default=False)
parser.add_argument("-rt", "--test", "--tests", "--run-test", "--run-tests", dest="test", help="Run in debug mode with only collections that have test: true", action="store_true", default=False)
parser.add_argument("-co", "--collection-only", "--collections-only", dest="collection_only", help="Run only collection operations", action="store_true", default=False)
parser.add_argument("-lo", "--library-only", "--libraries-only", dest="library_only", help="Run only library operations", action="store_true", default=False)
parser.add_argument("-lf", "--library-first", "--libraries-first", dest="library_first", help="Run library operations before collections", action="store_true", default=False)
parser.add_argument("-rc", "-cl", "--collection", "--collections", "--run-collection", "--run-collections", dest="collections", help="Process only specified collections (comma-separated list)", type=str)
parser.add_argument("-rl", "-l", "--library", "--libraries", "--run-library", "--run-libraries", dest="libraries", help="Process only specified libraries (comma-separated list)", type=str)
parser.add_argument("-rm", "-m", "--metadata", "--metadata-files", "--run-metadata-files", dest="metadata", help="Process only specified Metadata files (comma-separated list)", type=str)
parser.add_argument("-dc", "--delete", "--delete-collections", dest="delete", help="Deletes all Collections in the Plex Library before running", action="store_true", default=False)
parser.add_argument("-nc", "--no-countdown", dest="no_countdown", help="Run without displaying the countdown", action="store_true", default=False)
parser.add_argument("-nm", "--no-missing", dest="no_missing", help="Run without running the missing section", action="store_true", default=False)
parser.add_argument("-ro", "--read-only-config", dest="read_only_config", help="Run without writing to the config", action="store_true", default=False)
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
ignore_schedules = get_arg("PMM_IGNORE_SCHEDULES", args.ignore_schedules, arg_bool=True)
ignore_ghost = get_arg("PMM_IGNORE_GHOST", args.ignore_ghost, arg_bool=True)
collection_only = get_arg("PMM_COLLECTIONS_ONLY", args.collection_only, arg_bool=True)
library_only = get_arg("PMM_LIBRARIES_ONLY", args.library_only, arg_bool=True)
library_first = get_arg("PMM_LIBRARIES_FIRST", args.library_first, arg_bool=True)
collections = get_arg("PMM_COLLECTIONS", args.collections)
libraries = get_arg("PMM_LIBRARIES", args.libraries)
metadata_files = get_arg("PMM_METADATA_FILES", args.metadata)
delete = get_arg("PMM_DELETE_COLLECTIONS", args.delete, arg_bool=True)
resume = get_arg("PMM_RESUME", args.resume)
no_countdown = get_arg("PMM_NO_COUNTDOWN", args.no_countdown, arg_bool=True)
no_missing = get_arg("PMM_NO_MISSING", args.no_missing, arg_bool=True)
read_only_config = get_arg("PMM_READ_ONLY_CONFIG", args.read_only_config, arg_bool=True)
divider = get_arg("PMM_DIVIDER", args.divider)
screen_width = get_arg("PMM_WIDTH", args.width, arg_int=True)
debug = get_arg("PMM_DEBUG", args.debug, arg_bool=True)
trace = get_arg("PMM_TRACE", args.trace, arg_bool=True)


if screen_width < 90 or screen_width > 300:
    print(f"Argument Error: width argument invalid: {screen_width} must be an integer between 90 and 300 using the default 100")
    screen_width = 100

default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
if config_file and os.path.exists(config_file):
    default_dir = os.path.join(os.path.dirname(os.path.abspath(config_file)))
elif config_file and not os.path.exists(config_file):
    print(f"Config Error: config not found at {os.path.abspath(config_file)}")
    sys.exit(0)
elif not os.path.exists(os.path.join(default_dir, "config.yml")):
    print(f"Config Error: config not found at {os.path.abspath(default_dir)}")
    sys.exit(0)

logger = MyLogger("Plex Meta Manager", default_dir, screen_width, divider[0], ignore_ghost, test or debug or trace)

from modules import util
util.logger = logger
from modules.builder import CollectionBuilder
from modules.config import ConfigFile
from modules.meta import MetadataFile
from modules.util import Failed, NotScheduled

def my_except_hook(exctype, value, tb):
    for _line in traceback.format_exception(etype=exctype, value=value, tb=tb):
        logger.critical(_line)

sys.excepthook = my_except_hook

version = ("Unknown", "Unknown", 0)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")) as handle:
    for line in handle.readlines():
        line = line.strip()
        if len(line) > 0:
            version = util.parse_version(line)
            break

plexapi.BASE_HEADERS['X-Plex-Client-Identifier'] = "Plex-Meta-Manager"

def start(attrs):
    logger.add_main_handler()
    logger.separator()
    logger.info("")
    logger.info_center(" ____  _             __  __      _          __  __                                   ")
    logger.info_center("|  _ \\| | _____  __ |  \\/  | ___| |_ __ _  |  \\/  | __ _ _ __   __ _  __ _  ___ _ __ ")
    logger.info_center("| |_) | |/ _ \\ \\/ / | |\\/| |/ _ \\ __/ _` | | |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__|")
    logger.info_center("|  __/| |  __/>  <  | |  | |  __/ || (_| | | |  | | (_| | | | | (_| | (_| |  __/ |   ")
    logger.info_center("|_|   |_|\\___/_/\\_\\ |_|  |_|\\___|\\__\\__,_| |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|   ")
    logger.info_center("                                                                     |___/           ")
    logger.info(f"    Version: {version[0]}")

    latest_version = util.current_version()
    new_version = latest_version[0] if latest_version and (version[1] != latest_version[1] or (version[2] and version[2] < latest_version[2])) else None
    if new_version:
        logger.info(f"    Newest Version: {new_version}")
    if "time" in attrs and attrs["time"]:                   start_type = f"{attrs['time']} "
    elif "test" in attrs and attrs["test"]:                 start_type = "Test "
    elif "collections" in attrs and attrs["collections"]:   start_type = "Collections "
    elif "libraries" in attrs and attrs["libraries"]:       start_type = "Libraries "
    else:                                                   start_type = ""
    start_time = datetime.now()
    if "time" not in attrs:
        attrs["time"] = start_time.strftime("%H:%M")
    attrs["time_obj"] = start_time
    attrs["read_only"] = read_only_config
    attrs["version"] = version
    attrs["latest_version"] = latest_version
    logger.separator(debug=True)
    logger.debug(f"--config (PMM_CONFIG): {config_file}")
    logger.debug(f"--time (PMM_TIME): {times}")
    logger.debug(f"--run (PMM_RUN): {run}")
    logger.debug(f"--run-tests (PMM_TEST): {test}")
    logger.debug(f"--collections-only (PMM_COLLECTIONS_ONLY): {collection_only}")
    logger.debug(f"--libraries-only (PMM_LIBRARIES_ONLY): {library_only}")
    logger.debug(f"--libraries-first (PMM_LIBRARIES_FIRST): {library_first}")
    logger.debug(f"--run-collections (PMM_COLLECTIONS): {collections}")
    logger.debug(f"--run-libraries (PMM_LIBRARIES): {libraries}")
    logger.debug(f"--run-metadata-files (PMM_METADATA_FILES): {metadata_files}")
    logger.debug(f"--ignore-schedules (PMM_IGNORE_SCHEDULES): {ignore_schedules}")
    logger.debug(f"--ignore-ghost (PMM_IGNORE_GHOST): {ignore_ghost}")
    logger.debug(f"--delete-collections (PMM_DELETE_COLLECTIONS): {delete}")
    logger.debug(f"--resume (PMM_RESUME): {resume}")
    logger.debug(f"--no-countdown (PMM_NO_COUNTDOWN): {no_countdown}")
    logger.debug(f"--no-missing (PMM_NO_MISSING): {no_missing}")
    logger.debug(f"--read-only-config (PMM_READ_ONLY_CONFIG): {read_only_config}")
    logger.debug(f"--divider (PMM_DIVIDER): {divider}")
    logger.debug(f"--width (PMM_WIDTH): {screen_width}")
    logger.debug(f"--debug (PMM_DEBUG): {debug}")
    logger.debug(f"--trace (PMM_TRACE): {trace}")
    logger.debug("")
    logger.separator(f"Starting {start_type}Run")
    config = None
    stats = {"created": 0, "modified": 0, "deleted": 0, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0}
    try:
        config = ConfigFile(default_dir, attrs)
    except Exception as e:
        logger.stacktrace()
        logger.critical(e)
    else:
        try:
            stats = update_libraries(config)
        except Exception as e:
            config.notify(e)
            logger.stacktrace()
            logger.critical(e)
    logger.info("")
    end_time = datetime.now()
    run_time = str(end_time - start_time).split('.')[0]
    if config:
        try:
            config.Webhooks.end_time_hooks(start_time, end_time, run_time, stats)
        except Failed as e:
            logger.stacktrace()
            logger.error(f"Webhooks Error: {e}")
    version_line = f"Version: {version[0]}"
    if new_version:
        version_line = f"{version_line}        Newest Version: {new_version}"
    logger.separator(f"Finished {start_type}Run\n{version_line}\nFinished: {end_time.strftime('%H:%M:%S %Y-%m-%d')} Run Time: {run_time}")
    logger.remove_main_handler()

def update_libraries(config):
    for library in config.libraries:
        if library.skip_library:
            logger.info("")
            logger.separator(f"Skipping {library.name} Library")
            continue
        try:
            logger.add_library_handler(library.mapping_name)
            plexapi.server.TIMEOUT = library.timeout
            logger.info("")
            logger.separator(f"{library.name} Library")

            if config.library_first and library.library_operation and not config.test_mode and not collection_only:
                library_operations(config, library)

            logger.debug("")
            logger.debug(f"Mapping Name: {library.original_mapping_name}")
            logger.debug(f"Folder Name: {library.mapping_name}")
            logger.debug(f"Missing Path: {library.missing_path}")
            for ad in library.asset_directory:
                logger.debug(f"Asset Directory: {ad}")
            logger.debug(f"Asset Folders: {library.asset_folders}")
            logger.debug(f"Create Asset Folders: {library.create_asset_folders}")
            logger.debug(f"Download URL Assets: {library.download_url_assets}")
            logger.debug(f"Sync Mode: {library.sync_mode}")
            logger.debug(f"Minimum Items: {library.minimum_items}")
            logger.debug(f"Delete Below Minimum: {library.delete_below_minimum}")
            logger.debug(f"Delete Not Scheduled: {library.delete_not_scheduled}")
            logger.debug(f"Default Collection Order: {library.default_collection_order}")
            logger.debug(f"Missing Only Released: {library.missing_only_released}")
            logger.debug(f"Only Filter Missing: {library.only_filter_missing}")
            logger.debug(f"Show Unmanaged: {library.show_unmanaged}")
            logger.debug(f"Show Filtered: {library.show_filtered}")
            logger.debug(f"Show Missing: {library.show_missing}")
            logger.debug(f"Show Missing Assets: {library.show_missing_assets}")
            logger.debug(f"Save Missing: {library.save_missing}")
            logger.debug(f"Clean Bundles: {library.clean_bundles}")
            logger.debug(f"Empty Trash: {library.empty_trash}")
            logger.debug(f"Optimize: {library.optimize}")
            logger.debug(f"Timeout: {library.timeout}")

            if config.delete_collections:
                logger.info("")
                logger.separator(f"Deleting all Collections from the {library.name} Library", space=False, border=False)
                logger.info("")
                for collection in library.get_all_collections():
                    logger.info(f"Collection {collection.title} Deleted")
                    library.query(collection.delete)
            if not library.is_other and not library.is_music and (library.metadata_files or library.original_mapping_name in config.library_map) and not library_only:
                logger.info("")
                logger.separator(f"Mapping {library.name} Library", space=False, border=False)
                logger.info("")
                library.map_guids()
            for metadata in library.metadata_files:
                metadata_name = metadata.get_file_name()
                if config.requested_metadata_files and metadata_name not in config.requested_metadata_files:
                    logger.info("")
                    logger.separator(f"Skipping {metadata_name} Metadata File")
                    continue
                logger.info("")
                logger.separator(f"Running {metadata_name} Metadata File\n{metadata.path}")
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
                    logger.separator(f"{'Test ' if config.test_mode else ''}Collections")
                    logger.remove_library_handler(library.mapping_name)
                    run_collection(config, library, metadata, collections_to_run)
                    logger.re_add_library_handler(library.mapping_name)

            if not config.library_first and library.library_operation and not config.test_mode and not collection_only:
                library_operations(config, library)

            logger.remove_library_handler(library.mapping_name)
        except Exception as e:
            library.notify(e)
            logger.stacktrace()
            logger.critical(e)

    playlist_status = {}
    playlist_stats = {}
    if config.playlist_files:
        logger.add_playlists_handler()
        playlist_status, playlist_stats = run_playlists(config)
        logger.remove_playlists_handler()

    has_run_again = False
    for library in config.libraries:
        if library.run_again:
            has_run_again = True
            break

    amount_added = 0
    if has_run_again and not library_only:
        logger.info("")
        logger.separator("Run Again")
        logger.info("")
        for x in range(1, config.general["run_again_delay"] + 1):
            logger.ghost(f"Waiting to run again in {config.general['run_again_delay'] - x + 1} minutes")
            for y in range(60):
                time.sleep(1)
        logger.exorcise()
        for library in config.libraries:
            if library.run_again:
                try:
                    logger.re_add_library_handler(library.mapping_name)
                    os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
                    logger.info("")
                    logger.separator(f"{library.name} Library Run Again")
                    logger.info("")
                    library.map_guids()
                    for builder in library.run_again:
                        logger.info("")
                        logger.separator(f"{builder.name} Collection in {library.name}")
                        logger.info("")
                        try:
                            amount_added += builder.run_collections_again()
                        except Failed as e:
                            library.notify(e, collection=builder.name, critical=False)
                            logger.stacktrace()
                            logger.error(e)
                    logger.remove_library_handler(library.mapping_name)
                except Exception as e:
                    library.notify(e)
                    logger.stacktrace()
                    logger.critical(e)

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

    longest = 20
    for library in config.libraries:
        for title in library.status:
            if len(title) > longest:
                longest = len(title)
    if playlist_status:
        for title in playlist_status:
            if len(title) > longest:
                longest = len(title)

    def print_status(section, status):
        logger.info("")
        logger.separator(f"{section} Summary", space=False, border=False)
        logger.info("")
        logger.info(f"{'Title':^{longest}} |  +  |  =  |  -  | {'Status':^13}")
        breaker = f"{logger.separating_character * longest}|{logger.separating_character * 5}|{logger.separating_character * 5}|{logger.separating_character * 5}|"
        logger.separator(breaker, space=False, border=False, side_space=False, left=True)
        for name, data in status.items():
            logger.info(f"{name:<{longest}} | {data['added']:^3} | {data['unchanged']:^3} | {data['removed']:^3} | {data['status']}")
            if data["errors"]:
                for error in data["errors"]:
                    logger.info(error)
                logger.info("")

    logger.separator("Summary")
    for library in config.libraries:
        print_status(library.name, library.status)
    if playlist_status:
        print_status("Playlists", playlist_status)

    stats = {"created": 0, "modified": 0, "deleted": 0, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0, "names": []}
    stats["added"] += amount_added
    for library in config.libraries:
        stats["created"] += library.stats["created"]
        stats["modified"] += library.stats["modified"]
        stats["deleted"] += library.stats["deleted"]
        stats["added"] += library.stats["added"]
        stats["unchanged"] += library.stats["unchanged"]
        stats["removed"] += library.stats["removed"]
        stats["radarr"] += library.stats["radarr"]
        stats["sonarr"] += library.stats["sonarr"]
        stats["names"].extend([{"name": n, "library": library.name} for n in library.stats["names"]])
    if playlist_stats:
        stats["created"] += playlist_stats["created"]
        stats["modified"] += playlist_stats["modified"]
        stats["deleted"] += playlist_stats["deleted"]
        stats["added"] += playlist_stats["added"]
        stats["unchanged"] += playlist_stats["unchanged"]
        stats["removed"] += playlist_stats["removed"]
        stats["radarr"] += playlist_stats["radarr"]
        stats["sonarr"] += playlist_stats["sonarr"]
        stats["names"].extend([{"name": n, "library": "PLAYLIST"} for n in playlist_stats["names"]])
    return stats

def library_operations(config, library):
    logger.info("")
    logger.separator(f"{library.name} Library Operations")
    logger.info("")
    logger.debug(f"Assets For All: {library.assets_for_all}")
    logger.debug(f"Delete Collections With Less: {library.delete_collections_with_less}")
    logger.debug(f"Delete Unmanaged Collections: {library.delete_unmanaged_collections}")
    logger.debug(f"Mass Genre Update: {library.mass_genre_update}")
    logger.debug(f"Mass Audience Rating Update: {library.mass_audience_rating_update}")
    logger.debug(f"Mass Critic Rating Update: {library.mass_critic_rating_update}")
    logger.debug(f"Mass Content Rating Update: {library.mass_content_rating_update}")
    logger.debug(f"Mass Originally Available Update: {library.mass_originally_available_update}")
    logger.debug(f"Mass IMDb Parental Labels: {library.mass_imdb_parental_labels}")
    logger.debug(f"Mass Trakt Rating Update: {library.mass_trakt_rating_update}")
    logger.debug(f"Mass Collection Mode Update: {library.mass_collection_mode}")
    logger.debug(f"Split Duplicates: {library.split_duplicates}")
    logger.debug(f"Radarr Add All Existing: {library.radarr_add_all_existing}")
    logger.debug(f"Radarr Remove by Tag: {library.radarr_remove_by_tag}")
    logger.debug(f"Sonarr Add All Existing: {library.sonarr_add_all_existing}")
    logger.debug(f"Sonarr Remove by Tag: {library.sonarr_remove_by_tag}")
    logger.debug(f"Update Blank Track Titles: {library.update_blank_track_titles}")
    logger.debug(f"TMDb Collections: {library.tmdb_collections}")
    logger.debug(f"Genre Collections: {library.genre_collections}")
    logger.debug(f"Genre Mapper: {library.genre_mapper}")
    logger.debug(f"Content Rating Mapper: {library.content_rating_mapper}")
    logger.debug(f"Metadata Backup: {library.metadata_backup}")
    logger.debug(f"Item Operation: {library.items_library_operation}")
    logger.debug("")

    if library.split_duplicates:
        items = library.search(**{"duplicate": True})
        for item in items:
            item.split()
            logger.info(f"{item.title[:25]:<25} | Splitting")

    if library.update_blank_track_titles:
        tracks = library.get_all(collection_level="track")
        num_edited = 0
        for i, item in enumerate(tracks, 1):
            logger.ghost(f"Processing Track: {i}/{len(tracks)} {item.title}")
            if not item.title and item.titleSort:
                library.edit_query(item, {"title.locked": 1, "title.value": item.titleSort})
                num_edited += 1
                logger.info(f"Track: {item.titleSort} was updated with sort title")
        logger.info(f"{len(tracks)} Tracks Processed; {num_edited} Blank Track Titles Updated")

    tmdb_collections = {}
    if library.items_library_operation:
        items = library.get_all(load=True)
        radarr_adds = []
        sonarr_adds = []
        trakt_ratings = config.Trakt.user_ratings(library.is_movie) if library.mass_trakt_rating_update else []

        reverse_anidb = {}
        if library.mass_genre_update == "anidb":
            for k, v in library.anidb_map.items():
                reverse_anidb[v] = k

        for i, item in enumerate(items, 1):
            try:
                library.reload(item)
            except Failed as e:
                logger.error(e)
                continue
            logger.ghost(f"Processing: {i}/{len(items)} {item.title}")
            if library.assets_for_all:
                library.find_assets(item)
            tmdb_id, tvdb_id, imdb_id = library.get_ids(item)

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
                        logger.info(f"{item.title[:25]:<25} | User Rating | {new_rating}")
                except Failed:
                    pass

            if library.mass_imdb_parental_labels:
                try:
                    parental_guide = config.IMDb.parental_guide(imdb_id)
                    labels = [f"{k.capitalize()}:{v}" for k, v in parental_guide.items() if library.mass_imdb_parental_labels == "with_none" or v != "None"]
                    library.edit_tags("label", item, append_tags=labels)
                except Failed:
                    pass

            path = os.path.dirname(str(item.locations[0])) if library.is_movie else str(item.locations[0])
            if library.Radarr and library.radarr_add_all_existing and tmdb_id:
                path = path.replace(library.Radarr.plex_path, library.Radarr.radarr_path)
                path = path[:-1] if path.endswith(('/', '\\')) else path
                radarr_adds.append((tmdb_id, path))
            if library.Sonarr and library.sonarr_add_all_existing and tvdb_id:
                path = path.replace(library.Sonarr.plex_path, library.Sonarr.sonarr_path)
                path = path[:-1] if path.endswith(('/', '\\')) else path
                sonarr_adds.append((tvdb_id, path))

            tmdb_item = None
            if library.tmdb_collections or library.mass_genre_update == "tmdb" or library.mass_audience_rating_update == "tmdb" \
                    or library.mass_critic_rating_update == "tmdb" or library.mass_originally_available_update == "tmdb" \
                    or library.mass_content_rating_update == "tmdb":
                tmdb_item = config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=library.is_movie)

            omdb_item = None
            if library.mass_genre_update == "omdb" or library.mass_audience_rating_update == "omdb" \
                    or library.mass_critic_rating_update == "omdb" or library.mass_content_rating_update == "omdb" \
                    or library.mass_originally_available_update == "omdb":
                if config.OMDb.limit is False:
                    if tmdb_id and not imdb_id:
                        imdb_id = config.Convert.tmdb_to_imdb(tmdb_id)
                    elif tvdb_id and not imdb_id:
                        imdb_id = config.Convert.tvdb_to_imdb(tvdb_id)
                    if imdb_id:
                        try:
                            omdb_item = config.OMDb.get_omdb(imdb_id)
                        except Failed as e:
                            logger.error(str(e))
                        except Exception:
                            logger.error(f"IMDb ID: {imdb_id}")
                            raise
                    else:
                        logger.info(f"{item.title[:25]:<25} | No IMDb ID for Guid: {item.guid}")

            tvdb_item = None
            if library.mass_genre_update == "tvdb" or library.mass_originally_available_update == "tvdb":
                if tvdb_id:
                    try:
                        tvdb_item = config.TVDb.get_item(tvdb_id, library.is_movie)
                    except Failed as e:
                        logger.error(str(e))
                else:
                    logger.info(f"{item.title[:25]:<25} | No TVDb ID for Guid: {item.guid}")

            anidb_item = None
            if library.mass_genre_update == "anidb":
                if item.ratingKey in reverse_anidb:
                    anidb_id = reverse_anidb[item.ratingKey]
                elif tvdb_id in config.Convert._tvdb_to_anidb:
                    anidb_id = config.Convert._tvdb_to_anidb[tvdb_id]
                elif imdb_id in config.Convert._imdb_to_anidb:
                    anidb_id = config.Convert._imdb_to_anidb[imdb_id]
                else:
                    anidb_id = None
                    logger.info(f"{item.title[:25]:<25} | No AniDB ID for Guid: {item.guid}")
                if anidb_id:
                    try:
                        anidb_item = config.AniDB.get_anime(anidb_id)
                    except Failed as e:
                        logger.error(str(e))

            mdb_item = None
            if library.mass_audience_rating_update in util.mdb_types or library.mass_critic_rating_update in util.mdb_types \
                    or library.mass_content_rating_update in ["mdb", "mdb_commonsense"] or library.mass_originally_available_update == "mdb":
                if config.Mdblist.limit is False:
                    if tmdb_id and not imdb_id:
                        imdb_id = config.Convert.tmdb_to_imdb(tmdb_id)
                    elif tvdb_id and not imdb_id:
                        imdb_id = config.Convert.tvdb_to_imdb(tvdb_id)
                    if imdb_id:
                        try:
                            mdb_item = config.Mdblist.get_imdb(imdb_id)
                        except Failed as e:
                            logger.error(str(e))
                        except Exception:
                            logger.error(f"IMDb ID: {imdb_id}")
                            raise
                    else:
                        logger.info(f"{item.title[:25]:<25} | No IMDb ID for Guid: {item.guid}")

            if library.tmdb_collections and tmdb_item and tmdb_item.collection_id:
                tmdb_collections[tmdb_item.collection_id] = tmdb_item.collection_name

            def get_rating(attribute):
                if tmdb_item and attribute == "tmdb":
                    return tmdb_item.vote_average
                elif omdb_item and attribute == "omdb":
                    return omdb_item.imdb_rating
                elif mdb_item and attribute == "mdb":
                    return mdb_item.score / 10 if mdb_item.score else None
                elif mdb_item and attribute == "mdb_imdb":
                    return mdb_item.imdb_rating if mdb_item.imdb_rating else None
                elif mdb_item and attribute == "mdb_metacritic":
                    return mdb_item.metacritic_rating / 10 if mdb_item.metacritic_rating else None
                elif mdb_item and attribute == "mdb_metacriticuser":
                    return mdb_item.metacriticuser_rating if mdb_item.metacriticuser_rating else None
                elif mdb_item and attribute == "mdb_trakt":
                    return mdb_item.trakt_rating / 10 if mdb_item.trakt_rating else None
                elif mdb_item and attribute == "mdb_tomatoes":
                    return mdb_item.tomatoes_rating / 10 if mdb_item.tomatoes_rating else None
                elif mdb_item and attribute == "mdb_tomatoesaudience":
                    return mdb_item.tomatoesaudience_rating / 10 if mdb_item.tomatoesaudience_rating else None
                elif mdb_item and attribute == "mdb_tmdb":
                    return mdb_item.tmdb_rating / 10 if mdb_item.tmdb_rating else None
                elif mdb_item and attribute == "mdb_letterboxd":
                    return mdb_item.letterboxd_rating * 2 if mdb_item.letterboxd_rating else None
                elif anidb_item and attribute == "anidb_rating":
                    return anidb_item.rating
                elif anidb_item and attribute == "anidb_average":
                    return anidb_item.average
                else:
                    raise Failed

            if library.mass_genre_update or library.genre_mapper:
                try:
                    new_genres = []
                    if library.mass_genre_update:
                        if tmdb_item and library.mass_genre_update == "tmdb":
                            new_genres = tmdb_item.genres
                        elif omdb_item and library.mass_genre_update == "omdb":
                            new_genres = omdb_item.genres
                        elif tvdb_item and library.mass_genre_update == "tvdb":
                            new_genres = tvdb_item.genres
                        elif anidb_item and library.mass_genre_update == "anidb":
                            new_genres = anidb_item.tags
                        else:
                            raise Failed
                        if not new_genres:
                            logger.info(f"{item.title[:25]:<25} | No Genres Found")
                    if library.genre_mapper:
                        if not new_genres:
                            new_genres = [g.tag for g in item.genres]
                        mapped_genres = []
                        for genre in new_genres:
                            if genre in library.genre_mapper:
                                if library.genre_mapper[genre]:
                                    mapped_genres.append(library.genre_mapper[genre])
                            else:
                                mapped_genres.append(genre)
                        new_genres = mapped_genres
                    library.edit_tags("genre", item, sync_tags=new_genres)
                except Failed:
                    pass
            if library.mass_audience_rating_update:
                try:
                    new_rating = get_rating(library.mass_audience_rating_update)
                    if new_rating is None:
                        logger.info(f"{item.title[:25]:<25} | No Rating Found")
                    elif str(item.audienceRating) != str(new_rating):
                        library.edit_query(item, {"audienceRating.value": new_rating, "audienceRating.locked": 1})
                        logger.info(f"{item.title[:25]:<25} | Audience Rating | {new_rating}")
                except Failed:
                    pass
            if library.mass_critic_rating_update:
                try:
                    new_rating = get_rating(library.mass_critic_rating_update)
                    if new_rating is None:
                        logger.info(f"{item.title[:25]:<25} | No Rating Found")
                    elif str(item.rating) != str(new_rating):
                        library.edit_query(item, {"rating.value": new_rating, "rating.locked": 1})
                        logger.info(f"{item.title[:25]:<25} | Critic Rating | {new_rating}")
                except Failed:
                    pass
            if library.mass_content_rating_update or library.content_rating_mapper:
                try:
                    new_rating = None
                    if library.mass_content_rating_update:
                        if omdb_item and library.mass_content_rating_update == "omdb":
                            new_rating = omdb_item.content_rating
                        elif mdb_item and library.mass_content_rating_update == "mdb":
                            new_rating = mdb_item.content_rating if mdb_item.content_rating else None
                        elif mdb_item and library.mass_content_rating_update == "mdb_commonsense":
                            new_rating = mdb_item.commonsense if mdb_item.commonsense else None
                        elif tmdb_item and library.mass_content_rating_update == "tmdb":
                            new_rating = tmdb_item.content_rating if tmdb_item.content_rating else None
                        else:
                            raise Failed
                        if new_rating is None:
                            logger.info(f"{item.title[:25]:<25} | No Content Rating Found")
                    if library.content_rating_mapper:
                        if new_rating is None:
                            new_rating = item.contentRating
                        if new_rating in library.content_rating_mapper:
                            new_rating = library.content_rating_mapper[new_rating]
                    if str(item.contentRating) != str(new_rating):
                        library.edit_query(item, {"contentRating.value": new_rating, "contentRating.locked": 1})
                        logger.info(f"{item.title[:25]:<25} | Content Rating | {new_rating}")
                except Failed:
                    pass
            if library.mass_originally_available_update:
                try:
                    if omdb_item and library.mass_originally_available_update == "omdb":
                        new_date = omdb_item.released
                    elif mdb_item and library.mass_originally_available_update == "mdb":
                        new_date = mdb_item.released
                    elif tvdb_item and library.mass_originally_available_update == "tvdb":
                        new_date = tvdb_item.released
                    elif tmdb_item and library.mass_originally_available_update == "tmdb":
                        new_date = tmdb_item.release_date if library.is_movie else tmdb_item.first_air_date
                    elif anidb_item and library.mass_originally_available_update == "anidb":
                        new_date = anidb_item.released
                    else:
                        raise Failed
                    if new_date is None:
                        logger.info(f"{item.title[:25]:<25} | No Originally Available Date Found")
                    elif str(item.rating) != str(new_date):
                        library.edit_query(item, {"originallyAvailableAt.value": new_date.strftime("%Y-%m-%d"), "originallyAvailableAt.locked": 1})
                        logger.info(f"{item.title[:25]:<25} | Originally Available Date | {new_date.strftime('%Y-%m-%d')}")
                except Failed:
                    pass

        if library.Radarr and library.radarr_add_all_existing:
            try:
                library.Radarr.add_tmdb(radarr_adds)
            except Failed as e:
                logger.error(e)

        if library.Sonarr and library.sonarr_add_all_existing:
            try:
                library.Sonarr.add_tvdb(sonarr_adds)
            except Failed as e:
                logger.error(e)

    if tmdb_collections or library.genre_collections:
        logger.info("")
        logger.separator(f"Starting Automated Collections")
        logger.info("")
        new_collections = {}
        templates = {}

        if tmdb_collections:
            templates["TMDb Collection"] = library.tmdb_collections["template"]
            for _i, _n in tmdb_collections.items():
                if int(_i) not in library.tmdb_collections["exclude_ids"]:
                    template = {"name": "TMDb Collection", "collection_id": _i}
                    for k, v in library.tmdb_collections["dictionary_variables"].items():
                        if int(_i) in v:
                            template[k] = v[int(_i)]
                    for suffix in library.tmdb_collections["remove_suffix"]:
                        if _n.endswith(suffix):
                            _n = _n[:-len(suffix)]
                    new_collections[_n.strip()] = {"template": template}

        if library.genre_collections:
            templates["Genre Collection"] = library.genre_collections["template"]
            for genre in library.get_tags("genre"):
                if genre.title not in library.genre_collections["exclude_genres"]:
                    template = {"name": "Genre Collection", "genre": genre.title}
                    for k, v in library.genre_collections["dictionary_variables"].items():
                        if genre.title in v:
                            template[k] = v[genre.title]
                    title = library.genre_collections["title_format"]
                    title = title.replace("<<genre>>", genre.title)
                    if "<<library_type>>" in title:
                        title = title.replace("<<library_type>>", library.type)
                    new_collections[title] = {"template": template}

        metadata = MetadataFile(config, library, "Data", {"collections": new_collections, "templates": templates})
        if metadata.collections:
            library.collections.extend([c for c in metadata.collections])
        run_collection(config, library, metadata, metadata.get_collections(None))

    if library.radarr_remove_by_tag:
        library.Radarr.remove_all_with_tags(library.radarr_remove_by_tag)
    if library.sonarr_remove_by_tag:
        library.Sonarr.remove_all_with_tags(library.sonarr_remove_by_tag)

    if library.delete_collections_with_less is not None or library.delete_unmanaged_collections:
        logger.info("")
        print_suffix = ""
        unmanaged = ""
        if library.delete_collections_with_less is not None and library.delete_collections_with_less > 0:
            print_suffix = f" with less then {library.delete_collections_with_less} item{'s' if library.delete_collections_with_less > 1 else ''}"
        if library.delete_unmanaged_collections:
            if library.delete_collections_with_less is None:
                unmanaged = "Unmanaged Collections "
            elif library.delete_collections_with_less > 0:
                unmanaged = "Unmanaged Collections and "
        logger.separator(f"Deleting All {unmanaged}Collections{print_suffix}", space=False, border=False)
        logger.info("")
    unmanaged_collections = []
    for col in library.get_all_collections():
        if (library.delete_collections_with_less and col.childCount < library.delete_collections_with_less) \
            or (library.delete_unmanaged_collections and col.title not in library.collections):
            library.query(col.delete)
            logger.info(f"{col.title} Deleted")
        elif col.title not in library.collections:
            unmanaged_collections.append(col)
    if library.mass_collection_mode:
        logger.info("")
        logger.separator(f"Mass Collection Mode for {library.name} Library", space=False, border=False)
        logger.info("")
        for col in library.get_all_collections():
            library.collection_mode_query(col, library.mass_collection_mode)

    if library.show_unmanaged and len(unmanaged_collections) > 0:
        logger.info("")
        logger.separator(f"Unmanaged Collections in {library.name} Library", space=False, border=False)
        logger.info("")
        for col in unmanaged_collections:
            logger.info(col.title)
        logger.info("")
        logger.info(f"{len(unmanaged_collections)} Unmanaged Collection{'s' if len(unmanaged_collections) > 1 else ''}")
    elif library.show_unmanaged:
        logger.info("")
        logger.separator(f"No Unmanaged Collections in {library.name} Library", space=False, border=False)
        logger.info("")

    if library.assets_for_all and len(unmanaged_collections) > 0:
        logger.info("")
        logger.separator(f"Unmanaged Collection Assets Check for {library.name} Library", space=False, border=False)
        logger.info("")
        for col in unmanaged_collections:
            library.find_assets(col)

    if library.metadata_backup:
        logger.info("")
        logger.separator(f"Metadata Backup for {library.name} Library", space=False, border=False)
        logger.info("")
        logger.info(f"Metadata Backup Path: {library.metadata_backup['path']}")
        logger.info("")
        meta = None
        if os.path.exists(library.metadata_backup["path"]):
            try:
                meta, _, _ = yaml.util.load_yaml_guess_indent(open(library.metadata_backup["path"]))
            except yaml.scanner.ScannerError as e:
                logger.error(f"YAML Error: {util.tab_new_lines(e)}")
                filename, file_extension = os.path.splitext(library.metadata_backup["path"])
                i = 1
                while os.path.exists(f"{filename}{i}{file_extension}"):
                    i += 1
                os.rename(library.metadata_backup["path"], f"{filename}{i}{file_extension}")
                logger.error(f"Backup failed to load saving copy to {filename}{i}{file_extension}")
        if not meta:
            meta = {}
        if "metadata" not in meta:
            meta["metadata"] = {}
        items = library.get_all(load=True)
        titles = [i.title for i in items]
        for i, item in enumerate(items, 1):
            logger.ghost(f"Processing: {i}/{len(items)} {item.title}")
            map_key, attrs = library.get_locked_attributes(item, titles)
            if attrs or library.metadata_backup["add_blank_entries"]:
                def get_dict(attrs_dict):
                    return {ak: get_dict(av) if isinstance(av, dict) else av for ak, av in attrs_dict.items()} if isinstance(attrs_dict, dict) else attrs_dict
                meta["metadata"][map_key] = get_dict(attrs)
        logger.exorcise()
        try:
            yaml.round_trip_dump(meta, open(library.metadata_backup["path"], "w", encoding="utf-8"), block_seq_indent=2)
            logger.info(f"{len(meta['metadata'])} {library.type.capitalize()}{'s' if len(meta['metadata']) > 1 else ''} Backed Up")
        except yaml.scanner.ScannerError as e:
            logger.error(f"YAML Error: {util.tab_new_lines(e)}")

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
            logger.separator(f"Resuming Collections")

        if "name_mapping" in collection_attrs and collection_attrs["name_mapping"]:
            collection_log_name, output_str = util.validate_filename(collection_attrs["name_mapping"])
        else:
            collection_log_name, output_str = util.validate_filename(mapping_name)
        logger.add_collection_handler(library.mapping_name, collection_log_name)
        library.status[mapping_name] = {"status": "", "errors": [], "created": False, "modified": False, "deleted": False, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0}

        try:
            logger.separator(f"{mapping_name} Collection in {library.name}")
            logger.info("")
            if output_str:
                logger.info(output_str)
                logger.info("")

            logger.separator(f"Validating {mapping_name} Attributes", space=False, border=False)

            builder = CollectionBuilder(config, metadata, mapping_name, no_missing, collection_attrs, library=library)
            library.stats["names"].append(builder.name)
            logger.info("")

            logger.separator(f"Running {mapping_name} Collection", space=False, border=False)

            if len(builder.schedule) > 0:
                logger.info(builder.schedule)

            if len(builder.smart_filter_details) > 0:
                logger.info("")
                logger.info(builder.smart_filter_details)

            items_added = 0
            items_removed = 0
            if not builder.smart_url and builder.builders and not builder.blank_collection:
                logger.info("")
                logger.info(f"Sync Mode: {'sync' if builder.sync else 'append'}")

                if builder.filters or builder.tmdb_filters:
                    logger.info("")
                    for filter_key, filter_value in builder.filters:
                        logger.info(f"Collection Filter {filter_key}: {filter_value}")
                    for filter_key, filter_value in builder.tmdb_filters:
                        logger.info(f"Collection Filter {filter_key}: {filter_value}")

                for method, value in builder.builders:
                    logger.debug("")
                    logger.debug(f"Builder: {method}: {value}")
                    logger.info("")
                    builder.filter_and_save_items(builder.gather_ids(method, value))

                if len(builder.added_items) > 0 and len(builder.added_items) + builder.beginning_count >= builder.minimum and builder.build_collection:
                    items_added, items_unchanged = builder.add_to_collection()
                    library.stats["added"] += items_added
                    library.status[mapping_name]["added"] = items_added
                    library.stats["unchanged"] += items_unchanged
                    library.status[mapping_name]["unchanged"] = items_unchanged
                    items_removed = 0
                    if builder.sync:
                        items_removed = builder.sync_collection()
                        library.stats["removed"] += items_removed
                        library.status[mapping_name]["removed"] = items_removed

                if builder.do_missing and (len(builder.missing_movies) > 0 or len(builder.missing_shows) > 0):
                    radarr_add, sonarr_add = builder.run_missing()
                    library.stats["radarr"] += radarr_add
                    library.status[mapping_name]["radarr"] += radarr_add
                    library.stats["sonarr"] += sonarr_add
                    library.status[mapping_name]["sonarr"] += sonarr_add

            valid = True
            if builder.build_collection and (
                    (builder.smart_url and len(library.get_filter_items(builder.smart_url)) < builder.minimum)
                    or (not builder.smart_url and len(builder.added_items) + builder.beginning_count < builder.minimum)
            ):
                logger.info("")
                logger.info(f"Collection Minimum: {builder.minimum} not met for {mapping_name} Collection")
                valid = False
                if builder.details["delete_below_minimum"] and builder.obj:
                    logger.info("")
                    logger.info(builder.delete())
                    builder.deleted = True

            run_item_details = True
            if valid and builder.build_collection and (builder.builders or builder.smart_url or builder.blank_collection):
                try:
                    builder.load_collection()
                    if builder.created:
                        library.stats["created"] += 1
                        library.status[mapping_name]["created"] = True
                    elif items_added > 0 or items_removed > 0:
                        library.stats["modified"] += 1
                        library.status[mapping_name]["modified"] = True
                except Failed:
                    logger.stacktrace()
                    run_item_details = False
                    logger.info("")
                    logger.separator("No Collection to Update", space=False, border=False)
                else:
                    builder.update_details()

            if builder.deleted:
                library.stats["deleted"] += 1
                library.status[mapping_name]["deleted"] = True

            if builder.server_preroll is not None:
                library.set_server_preroll(builder.server_preroll)
                logger.info("")
                logger.info(f"Plex Server Movie pre-roll video updated to {builder.server_preroll}")

            if (builder.item_details or builder.custom_sort) and run_item_details and builder.builders:
                try:
                    builder.load_collection_items()
                except Failed:
                    logger.info("")
                    logger.separator("No Items Found", space=False, border=False)
                else:
                    if builder.item_details:
                        builder.update_item_details()
                    if builder.custom_sort:
                        builder.sort_collection()

            builder.send_notifications()

            if builder.run_again and (len(builder.run_again_movies) > 0 or len(builder.run_again_shows) > 0):
                library.run_again.append(builder)

            if library.status[mapping_name]["created"]:
                library.status[mapping_name]["status"] = "Created"
            elif library.status[mapping_name]["deleted"]:
                library.status[mapping_name]["status"] = "Deleted"
            elif library.status[mapping_name]["modified"]:
                library.status[mapping_name]["status"] = "Modified"
            else:
                library.status[mapping_name]["status"] = "Unchanged"
        except NotScheduled as e:
            logger.info(e)
            library.status[mapping_name]["status"] = "Not Scheduled"
        except Failed as e:
            library.notify(e, collection=mapping_name)
            logger.stacktrace()
            logger.error(e)
            library.status[mapping_name]["status"] = "PMM Failure"
            library.status[mapping_name]["errors"].append(e)
        except Exception as e:
            library.notify(f"Unknown Error: {e}", collection=mapping_name)
            logger.stacktrace()
            logger.error(f"Unknown Error: {e}")
            library.status[mapping_name]["status"] = "Unknown Error"
            library.status[mapping_name]["errors"].append(e)
        logger.info("")
        logger.separator(f"Finished {mapping_name} Collection\nCollection Run Time: {str(datetime.now() - collection_start).split('.')[0]}")
        logger.remove_collection_handler(library.mapping_name, collection_log_name)

def run_playlists(config):
    stats = {"created": 0, "modified": 0, "deleted": 0, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0, "names": []}
    status = {}
    logger.info("")
    logger.separator("Playlists")
    logger.info("")
    for playlist_file in config.playlist_files:
        for mapping_name, playlist_attrs in playlist_file.playlists.items():
            playlist_start = datetime.now()
            if config.test_mode and ("test" not in playlist_attrs or playlist_attrs["test"] is not True):
                no_template_test = True
                if "template" in playlist_attrs and playlist_attrs["template"]:
                    for data_template in util.get_list(playlist_attrs["template"], split=False):
                        if "name" in data_template \
                                and data_template["name"] \
                                and playlist_file.templates \
                                and data_template["name"] in playlist_file.templates \
                                and playlist_file.templates[data_template["name"]] \
                                and "test" in playlist_file.templates[data_template["name"]] \
                                and playlist_file.templates[data_template["name"]]["test"] is True:
                            no_template_test = False
                if no_template_test:
                    continue

            if "name_mapping" in playlist_attrs and playlist_attrs["name_mapping"]:
                playlist_log_name, output_str = util.validate_filename(playlist_attrs["name_mapping"])
            else:
                playlist_log_name, output_str = util.validate_filename(mapping_name)
            logger.add_playlist_handler(playlist_log_name)
            status[mapping_name] = {"status": "", "errors": [], "created": False, "modified": False, "deleted": False, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0}
            server_name = None
            library_names = None
            try:
                logger.separator(f"{mapping_name} Playlist")
                logger.info("")
                if output_str:
                    logger.info(output_str)
                    logger.info("")

                logger.separator(f"Validating {mapping_name} Attributes", space=False, border=False)

                builder = CollectionBuilder(config, playlist_file, mapping_name, no_missing, playlist_attrs)
                stats["names"].append(builder.name)
                logger.info("")

                logger.separator(f"Running {mapping_name} Playlist", space=False, border=False)

                if len(builder.schedule) > 0:
                    logger.info(builder.schedule)

                items_added = 0
                items_removed = 0
                valid = True
                logger.info("")
                logger.info(f"Sync Mode: {'sync' if builder.sync else 'append'}")

                if builder.filters or builder.tmdb_filters:
                    logger.info("")
                    for filter_key, filter_value in builder.filters:
                        logger.info(f"Playlist Filter {filter_key}: {filter_value}")
                    for filter_key, filter_value in builder.tmdb_filters:
                        logger.info(f"Playlist Filter {filter_key}: {filter_value}")

                method, value = builder.builders[0]
                logger.debug("")
                logger.debug(f"Builder: {method}: {value}")
                logger.info("")
                if "plex" in method:
                    ids = []
                    for pl_library in builder.libraries:
                        ids.extend(pl_library.get_rating_keys(method, value))
                elif "tautulli" in method:
                    ids = []
                    for pl_library in builder.libraries:
                        ids.extend(pl_library.Tautulli.get_rating_keys(pl_library, value, True))
                else:
                    ids = builder.gather_ids(method, value)

                builder.filter_and_save_items(ids)

                if len(builder.added_items) >= builder.minimum:
                    items_added, items_unchanged = builder.add_to_collection()
                    stats["added"] += items_added
                    status[mapping_name]["added"] += items_added
                    stats["unchanged"] += items_unchanged
                    status[mapping_name]["unchanged"] += items_unchanged
                    items_removed = 0
                    if builder.sync:
                        items_removed = builder.sync_collection()
                        stats["removed"] += items_removed
                        status[mapping_name]["removed"] += items_removed
                elif len(builder.added_items) < builder.minimum:
                    logger.info("")
                    logger.info(f"Playlist Minimum: {builder.minimum} not met for {mapping_name} Playlist")
                    valid = False
                    if builder.details["delete_below_minimum"] and builder.obj:
                        logger.info("")
                        logger.info(builder.delete())
                        builder.deleted = True

                if builder.do_missing and (len(builder.missing_movies) > 0 or len(builder.missing_shows) > 0):
                    radarr_add, sonarr_add = builder.run_missing()
                    stats["radarr"] += radarr_add
                    status[mapping_name]["radarr"] += radarr_add
                    stats["sonarr"] += sonarr_add
                    status[mapping_name]["sonarr"] += sonarr_add

                run_item_details = True
                try:
                    builder.load_collection()
                    if builder.created:
                        stats["created"] += 1
                        status[mapping_name]["created"] = True
                    elif items_added > 0 or items_removed > 0:
                        stats["modified"] += 1
                        status[mapping_name]["modified"] = True
                except Failed:
                    logger.stacktrace()
                    run_item_details = False
                    logger.info("")
                    logger.separator("No Playlist to Update", space=False, border=False)
                else:
                    builder.update_details()

                if builder.deleted:
                    stats["deleted"] += 1
                    status[mapping_name]["deleted"] = True

                if valid and run_item_details and builder.builders and (builder.item_details or builder.custom_sort):
                    try:
                        builder.load_collection_items()
                    except Failed:
                        logger.info("")
                        logger.separator("No Items Found", space=False, border=False)
                    else:
                        if builder.item_details:
                            builder.update_item_details()
                        if builder.custom_sort:
                            builder.sort_collection()

                if valid:
                    builder.sync_playlist()

                builder.send_notifications(playlist=True)

            except NotScheduled as e:
                logger.info(e)
                status[mapping_name]["status"] = "Not Scheduled"
            except Failed as e:
                config.notify(e, server=server_name, library=library_names, playlist=mapping_name)
                logger.stacktrace()
                logger.error(e)
                status[mapping_name]["status"] = "PMM Failure"
                status[mapping_name]["errors"].append(e)
            except Exception as e:
                config.notify(f"Unknown Error: {e}", server=server_name, library=library_names, playlist=mapping_name)
                logger.stacktrace()
                logger.error(f"Unknown Error: {e}")
                status[mapping_name]["status"] = "Unknown Error"
                status[mapping_name]["errors"].append(e)
            logger.info("")
            logger.separator(f"Finished {mapping_name} Playlist\nPlaylist Run Time: {str(datetime.now() - playlist_start).split('.')[0]}")
            logger.remove_playlist_handler(playlist_log_name)
    return status, stats

try:
    if run or test or collections or libraries or metadata_files or resume:
        start({
            "config_file": config_file,
            "test": test,
            "delete": delete,
            "ignore_schedules": ignore_schedules,
            "collections": collections,
            "libraries": libraries,
            "metadata_files": metadata_files,
            "library_first": library_first,
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
            schedule.every().day.at(time_to_run).do(start, {"config_file": config_file, "time": time_to_run, "delete": delete, "library_first": library_first, "trace": trace})
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
                    logger.ghost(f"Current Time: {current_time} | {time_str} until the next run at {og_time_str} | Runs: {', '.join(times_to_run)}")
                else:
                    logger.error(f"Time Error: {valid_times}")
            time.sleep(60)
except KeyboardInterrupt:
    logger.separator("Exiting Plex Meta Manager")
