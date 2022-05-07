import argparse, os, sys, time, traceback, uuid
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

if sys.version_info[0] != 3 or sys.version_info[1] < 7:
    print("Version Error: Version: %s.%s.%s incompatible please use Python 3.7+" % (sys.version_info[0], sys.version_info[1], sys.version_info[2]))
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
parser.add_argument("-op", "--operation", "--operations", "-lo", "--library-only", "--libraries-only", "--operation-only", "--operations-only", dest="operations", help="Run only operations", action="store_true", default=False)
parser.add_argument("-ov", "--overlay", "--overlays", "--overlay-only", "--overlays-only", dest="overlays", help="Run only overlays", action="store_true", default=False)
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
    env_vars = [env_str] if not isinstance(env_str, list) else env_str
    final_value = None
    for env_var in env_vars:
        env_value = os.environ.get(env_var)
        if env_value is not None:
            final_value = env_value
            break
    if final_value is not None:
        if arg_bool:
            if final_value is True or final_value is False:
                return final_value
            elif final_value.lower() in ["t", "true"]:
                return True
            else:
                return False
        elif arg_int:
            return int(final_value)
        else:
            return str(final_value)
    else:
        return default

config_file = get_arg("PMM_CONFIG", args.config)
times = get_arg("PMM_TIME", args.times)
run = get_arg("PMM_RUN", args.run, arg_bool=True)
test = get_arg("PMM_TEST", args.test, arg_bool=True)
ignore_schedules = get_arg("PMM_IGNORE_SCHEDULES", args.ignore_schedules, arg_bool=True)
ignore_ghost = get_arg("PMM_IGNORE_GHOST", args.ignore_ghost, arg_bool=True)
collection_only = get_arg("PMM_COLLECTIONS_ONLY", args.collection_only, arg_bool=True)
operations_only = get_arg(["PMM_OPERATIONS", "PMM_LIBRARIES_ONLY"], args.operations, arg_bool=True)
overlays_only = get_arg(["PMM_OVERLAYS", "PMM_OVERLAYS_ONLY"], args.overlays, arg_bool=True)
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

if collections or metadata_files:
    collection_only = True

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

uuid_file = os.path.join(default_dir, "UUID")
uuid_num = None
if os.path.exists(uuid_file):
    with open(uuid_file) as handle:
        for line in handle.readlines():
            line = line.strip()
            if len(line) > 0:
                uuid_num = line
                break
if not uuid_num:
    uuid_num = uuid.uuid4()
    with open(uuid_file, "w") as handle:
        handle.write(str(uuid_num))

plexapi.BASE_HEADERS["X-Plex-Client-Identifier"] = str(uuid_num)

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
    latest_version = util.current_version(version)
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
    attrs["no_missing"] = no_missing
    attrs["collection_only"] = collection_only
    attrs["operations_only"] = operations_only
    attrs["overlays_only"] = overlays_only
    logger.separator(debug=True)
    logger.debug(f"--config (PMM_CONFIG): {config_file}")
    logger.debug(f"--time (PMM_TIME): {times}")
    logger.debug(f"--run (PMM_RUN): {run}")
    logger.debug(f"--run-tests (PMM_TEST): {test}")
    logger.debug(f"--collections-only (PMM_COLLECTIONS_ONLY): {collection_only}")
    logger.debug(f"--operations (PMM_OPERATIONS): {operations_only}")
    logger.debug(f"--overlays (PMM_OVERLAYS): {overlays_only}")
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
    run_time = str(end_time - start_time).split(".")[0]
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
    library_status = {}
    for library in config.libraries:
        if library.skip_library:
            logger.info("")
            logger.separator(f"Skipping {library.name} Library")
            continue
        library_status[library.name] = {}
        try:
            logger.add_library_handler(library.mapping_name)
            plexapi.server.TIMEOUT = library.timeout
            logger.info("")
            logger.separator(f"{library.name} Library")

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
                time_start = datetime.now()
                logger.info("")
                logger.separator(f"Deleting all Collections from the {library.name} Library", space=False, border=False)
                logger.info("")
                for collection in library.get_all_collections():
                    logger.info(f"Collection {collection.title} Deleted")
                    library.query(collection.delete)
                library_status[library.name]["All Collections Deleted"] = str(datetime.now() - time_start).split('.')[0]

            temp_items = library.cache_items()
            if not library.is_other and not library.is_music:
                time_start = datetime.now()
                logger.info("")
                logger.separator(f"Mapping {library.name} Library", space=False, border=False)
                logger.info("")
                library.map_guids(temp_items)
                library_status[library.name]["Library Loading and Mapping"] = str(datetime.now() - time_start).split('.')[0]

            if config.library_first and not config.test_mode and not collection_only:
                if not overlays_only and library.library_operation:
                    library_status[library.name]["Library Operations"] = library.Operations.run_operations()
                if not operations_only and (library.overlay_files or library.remove_overlays):
                    library_status[library.name]["Library Overlays"] = library.Overlays.run_overlays()

            if not operations_only and not overlays_only:
                time_start = datetime.now()
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
                    if collections_to_run:
                        logger.info("")
                        logger.separator(f"{'Test ' if config.test_mode else ''}Collections")
                        logger.remove_library_handler(library.mapping_name)
                        run_collection(config, library, metadata, collections_to_run)
                        logger.re_add_library_handler(library.mapping_name)
                library_status[library.name]["Library Metadata Files"] = str(datetime.now() - time_start).split('.')[0]

            if not config.library_first and not config.test_mode and not collection_only:
                if not overlays_only and library.library_operation:
                    library_status[library.name]["Library Operations"] = library.Operations.run_operations()
                if not operations_only and (library.overlay_files or library.remove_overlays):
                    library_status[library.name]["Library Overlays"] = library.Overlays.run_overlays()

            logger.remove_library_handler(library.mapping_name)
        except Exception as e:
            library.notify(e)
            logger.stacktrace()
            logger.critical(e)

    playlist_status = {}
    playlist_stats = {}
    if config.playlist_files or config.general["playlist_report"]:
        logger.add_playlists_handler()
        if config.playlist_files:
            playlist_status, playlist_stats = run_playlists(config)
        if config.general["playlist_report"]:
            ran = []
            for library in config.libraries:
                if library.PlexServer.machineIdentifier in ran:
                    continue
                ran.append(library.PlexServer.machineIdentifier)
                logger.info("")
                logger.separator(f"{library.PlexServer.friendlyName} Playlist Report")
                logger.info("")
                report = library.playlist_report()
                max_length = 0
                for playlist_name in report:
                    if len(playlist_name) > max_length:
                        max_length = len(playlist_name)
                logger.info(f"{'Playlist Title':<{max_length}} | Users")
                logger.separator(f"{logger.separating_character * max_length}|", space=False, border=False, side_space=False, left=True)
                for playlist_name, users in report.items():
                    logger.info(f"{playlist_name:<{max_length}} | {'all' if len(users) == len(library.users) + 1 else ', '.join(users)}")
        logger.remove_playlists_handler()

    has_run_again = False
    for library in config.libraries:
        if library.run_again:
            has_run_again = True
            break

    amount_added = 0
    if has_run_again and not operations_only and not overlays_only:
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

    def print_status( status):
        logger.info(f"{'Title':^{longest}} |   +   |   =   |   -   | Run Time | {'Status'}")
        breaker = f"{logger.separating_character * longest}|{logger.separating_character * 7}|{logger.separating_character * 7}|{logger.separating_character * 7}|{logger.separating_character * 10}|"
        logger.separator(breaker, space=False, border=False, side_space=False, left=True)
        for name, data in status.items():
            logger.info(f"{name:<{longest}} | {data['added']:>5} | {data['unchanged']:>5} | {data['removed']:>5} | {data['run_time']:>8} | {data['status']}")
            if data["errors"]:
                for error in data["errors"]:
                    logger.info(error)
                logger.info("")

    logger.info("")
    logger.separator("Summary")
    for library in config.libraries:
        logger.info("")
        logger.separator(f"{library.name} Summary", space=False, border=False)
        logger.info("")
        logger.info(f"{'Title':<27} | Run Time |")
        logger.info(f"{logger.separating_character * 27} | {logger.separating_character * 8} |")
        for text, value in library_status[library.name].items():
            logger.info(f"{text:<27} | {value:>8} |")
        logger.info("")
        print_status(library.status)
    if playlist_status:
        logger.info("")
        logger.separator(f"Playlists Summary", space=False, border=False)
        logger.info("")
        print_status(playlist_status)

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
                            and metadata.templates[data_template["name"]][0] \
                            and "test" in metadata.templates[data_template["name"]][0] \
                            and metadata.templates[data_template["name"]][0]["test"] is True:
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
        library.status[mapping_name] = {"status": "Unchanged", "errors": [], "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0}

        try:
            builder = CollectionBuilder(config, metadata, mapping_name, collection_attrs, library=library, extra=output_str)
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

                for method, value in builder.builders:
                    logger.debug("")
                    logger.debug(f"Builder: {method}: {value}")
                    logger.info("")
                    builder.filter_and_save_items(builder.gather_ids(method, value))

                if builder.filters or builder.tmdb_filters:
                    logger.info("")
                    for filter_key, filter_value in builder.filters:
                        logger.info(f"Collection Filter {filter_key}: {filter_value}")
                    for filter_key, filter_value in builder.tmdb_filters:
                        logger.info(f"Collection Filter {filter_key}: {filter_value}")

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
            if builder.build_collection and not builder.blank_collection and (
                    (builder.smart_url and len(library.get_filter_items(builder.smart_url)) < builder.minimum)
                    or (not builder.smart_url and len(builder.added_items) + builder.beginning_count < builder.minimum)
            ):
                logger.info("")
                logger.info(f"Collection Minimum: {builder.minimum} not met for {mapping_name} Collection")
                delete_status = f"Minimum {builder.minimum} Not Met"
                valid = False
                if builder.details["delete_below_minimum"] and builder.obj:
                    logger.info("")
                    logger.info(builder.delete())
                    library.stats["deleted"] += 1
                    delete_status = f"Deleted; {delete_status}"
                library.status[mapping_name]["status"] = delete_status

            run_item_details = True
            if valid and builder.build_collection and (builder.builders or builder.smart_url or builder.blank_collection):
                try:
                    builder.load_collection()
                    if builder.created:
                        library.stats["created"] += 1
                        library.status[mapping_name]["status"] = "Created"
                    elif items_added > 0 or items_removed > 0:
                        library.stats["modified"] += 1
                        library.status[mapping_name]["status"] = "Modified"
                except Failed:
                    logger.stacktrace()
                    run_item_details = False
                    logger.info("")
                    logger.separator("No Collection to Update", space=False, border=False)
                else:
                    details_list = builder.update_details()
                    if details_list:
                        pre = ""
                        if library.status[mapping_name]["status"] != "Unchanged":
                            pre = f"{library.status[mapping_name]['status']} and "
                        library.status[mapping_name]["status"] = f"{pre}Updated {', '.join(details_list)}"

            if builder.server_preroll is not None:
                library.set_server_preroll(builder.server_preroll)
                logger.info("")
                logger.info(f"Plex Server Movie pre-roll video updated to {builder.server_preroll}")

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

            builder.send_notifications()

            if builder.run_again and (len(builder.run_again_movies) > 0 or len(builder.run_again_shows) > 0):
                library.run_again.append(builder)

        except NotScheduled as e:
            logger.info(e)
            if str(e).endswith("and was deleted"):
                library.stats["deleted"] += 1
                library.status[mapping_name]["status"] = "Deleted Not Scheduled"
            else:
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
        collection_run_time = str(datetime.now() - collection_start).split('.')[0]
        library.status[mapping_name]["run_time"] = collection_run_time
        logger.info("")
        logger.separator(f"Finished {mapping_name} Collection\nCollection Run Time: {collection_run_time}")
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
                                and playlist_file.templates[data_template["name"]][0] \
                                and "test" in playlist_file.templates[data_template["name"]][0] \
                                and playlist_file.templates[data_template["name"]][0]["test"] is True:
                            no_template_test = False
                if no_template_test:
                    continue

            if "name_mapping" in playlist_attrs and playlist_attrs["name_mapping"]:
                playlist_log_name, output_str = util.validate_filename(playlist_attrs["name_mapping"])
            else:
                playlist_log_name, output_str = util.validate_filename(mapping_name)
            logger.add_playlist_handler(playlist_log_name)
            status[mapping_name] = {"status": "Unchanged", "errors": [], "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0}
            server_name = None
            library_names = None
            try:
                builder = CollectionBuilder(config, playlist_file, mapping_name, playlist_attrs, extra=output_str)
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
                        ids.extend(pl_library.Tautulli.get_rating_keys(value, True))
                else:
                    ids = builder.gather_ids(method, value)

                builder.filter_and_save_items(ids)

                if builder.filters or builder.tmdb_filters:
                    logger.info("")
                    for filter_key, filter_value in builder.filters:
                        logger.info(f"Playlist Filter {filter_key}: {filter_value}")
                    for filter_key, filter_value in builder.tmdb_filters:
                        logger.info(f"Playlist Filter {filter_key}: {filter_value}")

                if len(builder.added_items) > 0 and len(builder.added_items) + builder.beginning_count >= builder.minimum:
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
                    delete_status = f"Minimum {builder.minimum} Not Met"
                    valid = False
                    if builder.details["delete_below_minimum"] and builder.obj:
                        logger.info("")
                        logger.info(builder.delete())
                        stats["deleted"] += 1
                        delete_status = f"Deleted; {delete_status}"
                    status[mapping_name]["status"] = delete_status

                if builder.do_missing and (len(builder.missing_movies) > 0 or len(builder.missing_shows) > 0):
                    radarr_add, sonarr_add = builder.run_missing()
                    stats["radarr"] += radarr_add
                    status[mapping_name]["radarr"] += radarr_add
                    stats["sonarr"] += sonarr_add
                    status[mapping_name]["sonarr"] += sonarr_add

                run_item_details = True
                if valid and builder.builders:
                    try:
                        builder.load_collection()
                        if builder.created:
                            stats["created"] += 1
                            status[mapping_name]["status"] = "Created"
                        elif items_added > 0 or items_removed > 0:
                            stats["modified"] += 1
                            status[mapping_name]["status"] = "Modified"
                    except Failed:
                        logger.stacktrace()
                        run_item_details = False
                        logger.info("")
                        logger.separator("No Playlist to Update", space=False, border=False)
                    else:
                        details_list = builder.update_details()
                        if details_list:
                            pre = ""
                            if status[mapping_name]["status"] != "Unchanged":
                                pre = f"{status[mapping_name]['status']} and "
                            status[mapping_name]["status"] = f"{pre}Updated {', '.join(details_list)}"

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
                if str(e).endswith("and was deleted"):
                    stats["deleted"] += 1
                    status[mapping_name]["status"] = "Deleted Not Scheduled"
                else:
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
            playlist_run_time = str(datetime.now() - playlist_start).split('.')[0]
            status[mapping_name]["run_time"] = playlist_run_time
            logger.info("")
            logger.separator(f"Finished {mapping_name} Playlist\nPlaylist Run Time: {playlist_run_time}")
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
                    raise Failed(f"Argument Error: time argument invalid: {time_to_run} must be in the HH:MM format between 00:00-23:59")
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
