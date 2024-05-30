import argparse, os, platform, re, sys, time, uuid
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from modules.logs import MyLogger

if sys.version_info[0] != 3 or sys.version_info[1] < 8:
    print("Version Error: Version: %s.%s.%s incompatible please use Python 3.8+" % (sys.version_info[0], sys.version_info[1], sys.version_info[2]))
    sys.exit(0)

try:
    import arrapi, lxml, pathvalidate, PIL, plexapi, psutil, dateutil, requests, ruamel.yaml, schedule, setuptools, tmdbapis
    from dotenv import load_dotenv, version as dotenv_version
    from PIL import ImageFile
    from plexapi import server
    from plexapi.exceptions import NotFound
    from plexapi.video import Show, Season
except (ModuleNotFoundError, ImportError) as ie:
    print(f"Requirements Error: Requirements are not installed ({ie})")
    sys.exit(0)

system_versions = {
    "arrapi": arrapi.__version__,
    "GitPython": None,
    "lxml": lxml.__version__,
    "num2words": None,
    "pathvalidate": pathvalidate.__version__,
    "pillow": PIL.__version__,
    "PlexAPI": plexapi.__version__,
    "psutil": psutil.__version__,
    "python-dotenv": dotenv_version.__version__,
    "python-dateutil": dateutil.__version__, # noqa
    "requests": requests.__version__,
    "retrying": None,
    "ruamel.yaml": ruamel.yaml.__version__,
    "schedule": None,
    "setuptools": setuptools.__version__,
    "tmdbapis": tmdbapis.__version__
}

default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
load_dotenv(os.path.join(default_dir, ".env"))

arguments = {
    "config": {"args": "c", "type": "str", "help": "Run with desired *.yml file"},
    "times": {"args": ["t", "time"], "type": "str", "default": "05:00", "help": "Times to update each day use format HH:MM (Default: 05:00) (comma-separated list)"},
    "run": {"args": "r", "type": "bool", "help": "Run without the scheduler"},
    "tests": {"args": ["ts", "rt", "test", "run-test", "run-tests"], "type": "bool", "help": "Run in debug mode with only collections that have test: true"},
    "debug": {"args": "db", "type": "bool", "help": "Run with Debug Logs Reporting to the Command Window"},
    "trace": {"args": "tr", "type": "bool", "help": "Run with extra Trace Debug Logs"},
    "log-requests": {"args": ["lr", "log-request"], "type": "bool", "help": "Run with all Requests printed"},
    "timeout": {"args": "ti", "type": "int", "default": 180, "help": "Kometa Global Timeout (Default: 180)"},
    "no-verify-ssl": {"args": "nv", "type": "bool", "help": "Turns off Global SSL Verification"},
    "collections-only": {"args": ["co", "collection-only"], "type": "bool", "help": "Run only collection files"},
    "metadata-only": {"args": ["mo", "metadatas-only"], "type": "bool", "help": "Run only metadata files"},
    "playlists-only": {"args": ["po", "playlist-only"], "type": "bool", "help": "Run only playlist files"},
    "operations-only": {"args": ["op", "operation", "operations", "lo", "library-only", "libraries-only", "operation-only"], "type": "bool", "help": "Run only operations"},
    "overlays-only": {"args": ["ov", "overlay", "overlays", "overlay-only"], "type": "bool", "help": "Run only overlay files"},
    "run-collections": {"args": ["rc", "cl", "collection", "collections", "run-collection"], "type": "str", "help": "Process only specified collections (pipe-separated list '|')"},
    "run-libraries": {"args": ["rl", "l", "library", "libraries", "run-library"], "type": "str", "help": "Process only specified libraries (pipe-separated list '|')"},
    "run-files": {"args": ["rf", "rm", "m", "run-file", "metadata", "metadata-files", "run-metadata-files"], "type": "str", "help": "Process only specified Files (pipe-separated list '|')"},
    "ignore-schedules": {"args": "is", "type": "bool", "help": "Run ignoring collection schedules"},
    "ignore-ghost": {"args": "ig", "type": "bool", "help": "Run ignoring ghost logging"},
    "delete-collections": {"args": ["dc", "delete", "delete-collection"], "type": "bool", "help": "Deletes all Collections in the Plex Library before running"},
    "delete-labels": {"args": ["dl", "delete-label"], "type": "bool", "help": "Deletes all Labels in the Plex Library before running"},
    "resume": {"args": "re", "type": "str", "help": "Resume collection run from a specific collection"},
    "no-countdown": {"args": "nc", "type": "bool", "help": "Run without displaying the countdown"},
    "no-missing": {"args": "nm", "type": "bool", "help": "Run without running the missing section"},
    "no-report": {"args": "nr", "type": "bool", "help": "Run without saving a report"},
    "read-only-config": {"args": "ro", "type": "bool", "help": "Run without writing to the config"},
    "divider": {"args": "d", "type": "str", "default": "=", "help": "Character that divides the sections (Default: '=')"},
    "width": {"args": "w", "type": "int", "default": 100, "help": "Screen Width (Default: 100)"},
}

parser = argparse.ArgumentParser()
for arg_key, arg_data in arguments.items():
    temp_args = arg_data["args"] if isinstance(arg_data["args"], list) else [arg_data["args"]]
    args = [f"--{arg_key}"] + [f"--{a}" if len(a) > 2 else f"-{a}" for a in temp_args]
    kwargs = {"dest": arg_key.replace("-", "_"), "help": arg_data["help"]}
    if arg_data["type"] == "bool":
        kwargs["action"] = "store_true"
        kwargs["default"] = False # noqa
    else:
        kwargs["type"] = int if arg_data["type"] == "int" else str

    if "default" in arg_data:
        kwargs["default"] = arg_data["default"]

    parser.add_argument(*args, **kwargs)

args, unknown = parser.parse_known_args()


def get_env(env_str, default, arg_bool=False, arg_int=False):
    env_vars = [env_str] if not isinstance(env_str, list) else env_str
    final_value = None
    static_envs.extend(env_vars)
    for env_var in env_vars:
        env_value = os.environ.get(env_var)
        if env_value is not None:
            final_value = env_value
            break
    if not final_value:
        for env_var in env_vars:
            if env_var.startswith("KOMETA"):
                env_value = os.environ.get(env_var.replace("KOMETA", "PMM"))
                if env_value is not None:
                    final_value = env_value
                    break
    if final_value or (arg_int and final_value == 0):
        if arg_bool:
            if final_value is True or final_value is False:
                return final_value
            elif final_value.lower() in ["t", "true"]:
                return True
            else:
                return False
        elif arg_int:
            try:
                return int(final_value)
            except ValueError:
                return default
        else:
            return str(final_value)
    else:
        return default


static_envs = []
run_args = {}
for arg_key, arg_data in arguments.items():
    temp_args = arg_data["args"] if isinstance(arg_data["args"], list) else [arg_data["args"]]
    final_vars = [f"KOMETA_{arg_key.replace('-', '_').upper()}"] + [f"KOMETA_{a.replace('-', '_').upper()}" for a in temp_args if len(a) > 2]
    run_args[arg_key] = get_env(final_vars, getattr(args, arg_key.replace("-", "_")), arg_bool=arg_data["type"] == "bool", arg_int=arg_data["type"] == "int")

env_branch = get_env("BRANCH_NAME", "master")
is_docker = get_env("KOMETA_DOCKER", False, arg_bool=True)
is_linuxserver = get_env("KOMETA_LINUXSERVER", False, arg_bool=True)

secret_args = {}
plex_url = None
plex_token = None
i = 0
while i < len(unknown):
    test_var = str(unknown[i]).lower().replace("_", "-")
    if test_var.startswith(("--pmm-", "--kometa-")) or test_var in ["-pu", "--plex-url", "-pt", "--plex-token"]:
        if test_var in ["-pu", "--plex-url"]:
            plex_url = str(unknown[i + 1])
        elif test_var in ["-pt", "--plex-token"]:
            plex_token = str(unknown[i + 1])
        elif test_var.startswith("--kometa-"):
            secret_args[test_var[9:]] = str(unknown[i + 1])
        elif test_var.startswith("--pmm-"):
            secret_args[test_var[6:]] = str(unknown[i + 1])
        i += 1
    i += 1

plex_url = get_env("KOMETA_PLEX_URL", plex_url)
plex_token = get_env("KOMETA_PLEX_TOKEN", plex_token)

env_secrets = []
for env_name, env_data in os.environ.items():
    if env_data is not None and str(env_data).strip():
        if str(env_name).upper().startswith("KOMETA_") and str(env_name).upper() not in static_envs:
            secret_args[str(env_name).lower()[7:].replace("_", "-")] = env_data
        elif str(env_name).upper().startswith("PMM_") and str(env_name).upper() not in static_envs:
            secret_args[str(env_name).lower()[4:].replace("_", "-")] = env_data
run_arg = " ".join([f'"{s}"' if " " in s else s for s in sys.argv[:]])
for _, sv in secret_args.items():
    if sv in run_arg:
        run_arg = run_arg.replace(sv, "(redacted)")

try:
    import git # noqa
    system_versions["GitPython"] = git.__version__
    from git import Repo, InvalidGitRepositoryError # noqa
    try:
        git_branch = Repo(path=".").head.ref.name # noqa
    except InvalidGitRepositoryError:
        git_branch = None
except ImportError:
    git_branch = None

if run_args["run-collections"]:
    run_args["collections-only"] = True

if run_args["width"] < 90 or run_args["width"] > 300:
    print(f"Argument Error: width argument invalid: {run_args['width']} must be an integer between 90 and 300 using the default 100")
    run_args["width"] = 100

if run_args["config"] and os.path.exists(run_args["config"]):
    default_dir = os.path.join(os.path.dirname(os.path.abspath(run_args["config"])))
elif run_args["config"] and not os.path.exists(run_args["config"]):
    print(f"Config Error: config not found at {os.path.abspath(run_args['config'])}")
    sys.exit(0)
elif not os.path.exists(os.path.join(default_dir, "config.yml")):
    print(f"Config Error: config not found at {os.path.abspath(default_dir)}")
    sys.exit(0)

logger = MyLogger("Kometa", default_dir, run_args["width"], run_args["divider"][0], run_args["ignore-ghost"],
                  run_args["tests"] or run_args["debug"], run_args["trace"], run_args["log-requests"])

from modules import util
util.logger = logger
from modules.builder import CollectionBuilder
from modules.config import ConfigFile
from modules.request import Requests
from modules.util import Failed, FilterFailed, NonExisting, NotScheduled, Deleted

def my_except_hook(exctype, value, tb):
    if issubclass(exctype, KeyboardInterrupt):
        sys.__excepthook__(exctype, value, tb)
    else:
        logger.critical("Uncaught Exception", exc_info=(exctype, value, tb))

sys.excepthook = my_except_hook

old_send = requests.Session.send

def new_send(*send_args, **kwargs):
    if kwargs.get("timeout", None) is None:
        kwargs["timeout"] = run_args["timeout"]
    return old_send(*send_args, **kwargs)

requests.Session.send = new_send

local_version = "Unknown"
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")) as handle:
    for line in handle.readlines():
        line = line.strip()
        if len(line) > 0:
            local_version = line
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
ImageFile.LOAD_TRUNCATED_IMAGES = True

def process(attrs):
    with ProcessPoolExecutor(max_workers=1) as executor:
        executor.submit(start, *[attrs])

def start(attrs):
    try:
        logger.add_main_handler()
        logger.separator()
        logger.info("")
        logger.info_center(" __  ___  ______    ___  ___   _______  __________    ___      ")
        logger.info_center("|  |/  / /  __  \\  |   \\/   | |   ____||          |  /   \\     ")
        logger.info_center("|  '  / |  |  |  | |  \\  /  | |  |__   `---|  |---` /  ^  \\    ")
        logger.info_center("|    <  |  |  |  | |  |\\/|  | |   __|      |  |    /  /_\\  \\   ")
        logger.info_center("|  .  \\ |  `--`  | |  |  |  | |  |____     |  |   /  _____  \\  ")
        logger.info_center("|__|\\__\\ \\______/  |__|  |__| |_______|    |__|  /__/     \\__\\ ")
        logger.info("")
        my_requests = Requests(local_version, env_branch, git_branch, verify_ssl=False if run_args["no-verify-ssl"] else True)
        if is_linuxserver or is_docker:
            system_ver = f"{'Linuxserver' if is_linuxserver else 'Docker'}: {env_branch}"
        else:
            system_ver = f"Python {platform.python_version()}) ({f'Git: {git_branch}' if git_branch else f'Branch: {my_requests.branch}'}"
        logger.info(f"    Version: {my_requests.local} ({system_ver})")
        if my_requests.newest:
            logger.info(f"    Newest Version: {my_requests.newest}")
        logger.info(f"    Platform: {platform.platform()}")
        logger.info(f"    Total Memory: {round(psutil.virtual_memory().total / (1024.0 ** 3))} GB")
        logger.info(f"    Available Memory: {round(psutil.virtual_memory().available / (1024.0 ** 3))} GB")
        if not is_docker and not is_linuxserver:
            try:
                with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "requirements.txt")), "r") as file:
                    required_versions = {ln.split("==")[0]: ln.split("==")[1].strip() for ln in file.readlines()}
                for req_name, sys_ver in system_versions.items():
                    if sys_ver and sys_ver != required_versions[req_name]:
                        logger.info(f"    {req_name} version: {sys_ver} requires an update to: {required_versions[req_name]}")
            except FileNotFoundError:
                logger.error("    File Error: requirements.txt not found")
        if "time" in attrs and attrs["time"]:                   start_type = f"{attrs['time']} "
        elif run_args["tests"]:                                 start_type = "Test "
        elif "collections" in attrs and attrs["collections"]:   start_type = "Collections "
        elif "libraries" in attrs and attrs["libraries"]:       start_type = "Libraries "
        else:                                                   start_type = ""
        start_time = datetime.now()
        if "time" not in attrs:
            attrs["time"] = start_time.strftime("%H:%M")
        attrs["time_obj"] = start_time
        attrs["config_file"] = run_args["config"]
        attrs["ignore_schedules"] = run_args["ignore-schedules"]
        attrs["read_only"] = run_args["read-only-config"]
        attrs["no_missing"] = run_args["no-missing"]
        attrs["no_report"] = run_args["no-report"]
        attrs["collection_only"] = run_args["collections-only"]
        attrs["metadata_only"] = run_args["metadata-only"]
        attrs["playlist_only"] = run_args["playlists-only"]
        attrs["operations_only"] = run_args["operations-only"]
        attrs["overlays_only"] = run_args["overlays-only"]
        attrs["plex_url"] = plex_url
        attrs["plex_token"] = plex_token
        logger.separator(debug=True)
        logger.debug(f"Run Command: {run_arg}")
        for akey, adata in arguments.items():
            if isinstance(adata["help"], str):
                ext = '"' if adata["type"] == "str" and run_args[akey] not in [None, "None"] else ""
                logger.debug(f"--{akey} (KOMETA_{akey.replace('-', '_').upper()}): {ext}{run_args[akey]}{ext}")
        logger.debug("")
        if secret_args:
            logger.debug("Kometa Secrets Read:")
            for sec in secret_args:
                logger.debug(f"--kometa-{sec} (KOMETA_{sec.upper().replace('-', '_')}): (redacted)")
            logger.debug("")
        logger.separator(f"Starting {start_type}Run")
        config = None
        stats = {"created": 0, "modified": 0, "deleted": 0, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0, "names": []}
        try:
            config = ConfigFile(my_requests, default_dir, attrs, secret_args)
        except Exception as e:
            logger.stacktrace()
            logger.critical(e)
        else:
            try:
                stats = run_config(config, stats)
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
        version_line = f"Version: {my_requests.local}"
        if my_requests.newest:
            version_line = f"{version_line}        Newest Version: {my_requests.newest}"
        try:
            log_data = {}
            no_overlays = []
            no_overlays_count = 0
            convert_errors = {}

            other_log_groups = [
                ("No Items found for", r"No Items found for .* \(\d+\) (.*)"),
                ("Convert Warning: No TVDb ID or IMDb ID found for AniDB ID:", r"Convert Warning: No TVDb ID or IMDb ID found for AniDB ID: (.*)"),
                ("Convert Warning: No AniDB ID Found for AniList ID:", r"Convert Warning: No AniDB ID Found for AniList ID: (.*)"),
                ("Convert Warning: No AniDB ID Found for MyAnimeList ID:", r"Convert Warning: No AniDB ID Found for MyAnimeList ID: (.*)"),
                ("Convert Warning: No IMDb ID Found for TMDb ID:", r"Convert Warning: No IMDb ID Found for TMDb ID: (.*)"),
                ("Convert Warning: No TMDb ID Found for IMDb ID:", r"Convert Warning: No TMDb ID Found for IMDb ID: (.*)"),
                ("Convert Warning: No TVDb ID Found for TMDb ID:", r"Convert Warning: No TVDb ID Found for TMDb ID: (.*)"),
                ("Convert Warning: No TMDb ID Found for TVDb ID:", r"Convert Warning: No TMDb ID Found for TVDb ID: (.*)"),
                ("Convert Warning: No IMDb ID Found for TVDb ID:", r"Convert Warning: No IMDb ID Found for TVDb ID: (.*)"),
                ("Convert Warning: No TVDb ID Found for IMDb ID:", r"Convert Warning: No TVDb ID Found for IMDb ID: (.*)"),
                ("Convert Warning: No AniDB ID to Convert to MyAnimeList ID for Guid:", r"Convert Warning: No AniDB ID to Convert to MyAnimeList ID for Guid: (.*)"),
                ("Convert Warning: No MyAnimeList Found for AniDB ID:", r"Convert Warning: No MyAnimeList Found for AniDB ID: (.*) of Guid: .*"),
            ]
            other_message = {}

            with open(logger.main_log, encoding="utf-8") as f:
                for log_line in f:
                    for err_type in ["WARNING", "ERROR", "CRITICAL"]:
                        if f"[{err_type}]" in log_line:
                            log_line = log_line.split("|")[1].strip()
                            other = False
                            for key, reg in other_log_groups:
                                if log_line.startswith(key):
                                    other = True
                                    _name = re.match(reg, log_line).group(1)
                                    if key not in other_message:
                                        other_message[key] = {"list": [], "count": 0}
                                    other_message[key]["count"] += 1
                                    if _name not in other_message[key]:
                                        other_message[key]["list"].append(_name)
                            if other is False:
                                if err_type not in log_data:
                                    log_data[err_type] = []
                                log_data[err_type].append(log_line)

            if "No Items found for" in other_message:
                logger.separator(f"Overlay Errors Summary", space=False, border=False)
                logger.info("")
                logger.info(f"No Items found for {other_message['No Items found for']['count']} Overlays: {other_message['No Items found for']['list']}")
                logger.info("")

            convert_title = False
            for key, _ in other_log_groups:
                if key.startswith("Convert Warning") and key in other_message:
                    if convert_title is False:
                        logger.separator("Convert Summary", space=False, border=False)
                        logger.info("")
                        convert_title = True
                    logger.info(f"{key[17:]}")
                    logger.info(", ".join(other_message[key]["list"]))
            if convert_title:
                logger.info("")

            for err_type in ["WARNING", "ERROR", "CRITICAL"]:
                if err_type not in log_data:
                    continue
                logger.separator(f"{err_type.lower().capitalize()} Summary", space=False, border=False)

                logger.info("")
                logger.info("Count | Message")
                logger.separator(f"{logger.separating_character * 5}|", space=False, border=False, side_space=False, left=True)
                for k, v in Counter(log_data[err_type]).most_common():
                    logger.info(f"{v:>5} | {k}")
                logger.info("")
        except Failed as e:
            logger.stacktrace()
            logger.error(f"Report Error: {e}")

        logger.separator(f"Finished {start_type}Run\n{version_line}\nFinished: {end_time.strftime('%H:%M:%S %Y-%m-%d')} Run Time: {run_time}")
        logger.remove_main_handler()
    except Exception as e:
        logger.stacktrace()
        logger.critical(e)

def run_config(config, stats):
    library_status = run_libraries(config)

    playlist_status = {}
    playlist_stats = {}
    if (config.playlist_files or config.general["playlist_report"]) and not run_args["overlays-only"] and not run_args["metadata-only"] and not run_args["operations-only"] and not run_args["collections-only"] and not config.requested_files:
        #logger.add_playlists_handler()
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
        #logger.remove_playlists_handler()

    amount_added = 0
    if not run_args["operations-only"] and not run_args["overlays-only"] and not run_args["playlists-only"]:
        has_run_again = False
        for library in config.libraries:
            if library.run_again:
                has_run_again = True
                break

        if has_run_again:
            logger.info("")
            logger.separator("Run Again")
            logger.info("")
            for x in range(0, config.general["run_again_delay"]):
                logger.ghost(f"Waiting to run again in {config.general['run_again_delay'] - x} minutes")
                time.sleep(60)
            logger.exorcise()
            for library in config.libraries:
                if library.run_again:
                    try:
                        #logger.re_add_library_handler(library.mapping_name)
                        os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
                        logger.info("")
                        logger.separator(f"{library.name} Library Run Again")
                        logger.info("")
                        library.map_guids(library.cache_items())
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
                        #logger.remove_library_handler(library.mapping_name)
                    except Exception as e:
                        library.notify(e)
                        logger.stacktrace()
                        logger.critical(e)

    if not run_args["collections-only"] and not run_args["overlays-only"] and not run_args["playlists-only"]:
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

    def print_status(status):
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
        if library.name in library_status:
            for text, value in library_status[library.name].items():
                logger.info(f"{text:<27} | {value:>8} |")
        logger.info("")
        print_status(library.status)
    if playlist_status:
        logger.info("")
        logger.separator(f"Playlists Summary", space=False, border=False)
        logger.info("")
        print_status(playlist_status)

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

def run_libraries(config):
    library_status = {}
    for library in config.libraries:
        if library.skip_library:
            logger.info("")
            logger.separator(f"Skipping {library.original_mapping_name} Library")
            continue
        library_status[library.name] = {}
        try:
            #logger.add_library_handler(library.mapping_name)
            plexapi.server.TIMEOUT = library.timeout
            os.environ["PLEXAPI_PLEXAPI_TIMEOUT"] = str(library.timeout)
            logger.info("")
            logger.separator(f"{library.original_mapping_name} Library")

            logger.debug("")
            logger.debug(f"Library Name: {library.name}")
            logger.debug(f"Run Order: {', '.join(library.run_order)}")
            logger.debug(f"Folder Name: {library.mapping_name}")
            for ad in library.asset_directory:
                logger.debug(f"Asset Directory: {ad}")
            logger.debug(f"Asset Folders: {library.asset_folders}")
            logger.debug(f"Asset Depth: {library.asset_depth}")
            logger.debug(f"Create Asset Folders: {library.create_asset_folders}")
            logger.debug(f"Prioritize Assets: {library.prioritize_assets}")
            logger.debug(f"Dimensional Asset Rename: {library.dimensional_asset_rename}")
            logger.debug(f"Download URL Assets: {library.download_url_assets}")
            logger.debug(f"Show Missing Assets: {library.show_missing_assets}")
            logger.debug(f"Show Missing Season Assets: {library.show_missing_season_assets}")
            logger.debug(f"Show Missing Episode Assets: {library.show_missing_episode_assets}")
            logger.debug(f"Show Assets Not Needed: {library.show_asset_not_needed}")
            logger.debug(f"Sync Mode: {library.sync_mode}")
            logger.debug(f"Minimum Items: {library.minimum_items}")
            logger.debug(f"Delete Below Minimum: {library.delete_below_minimum}")
            logger.debug(f"Delete Not Scheduled: {library.delete_not_scheduled}")
            logger.debug(f"Default Collection Order: {library.default_collection_order}")
            logger.debug(f"Missing Only Released: {library.missing_only_released}")
            logger.debug(f"Only Filter Missing: {library.only_filter_missing}")
            logger.debug(f"Show Unmanaged: {library.show_unmanaged}")
            logger.debug(f"Show Unconfigured: {library.show_unconfigured}")
            logger.debug(f"Show Filtered: {library.show_filtered}")
            logger.debug(f"Show Options: {library.show_options}")
            logger.debug(f"Show Missing: {library.show_missing}")
            logger.debug(f"Save Report: {library.save_report}")
            logger.debug(f"Report Path: {library.report_path}")
            logger.debug(f"Ignore IDs: {library.ignore_ids}")
            logger.debug(f"Ignore IMDb IDs: {library.ignore_imdb_ids}")
            logger.debug(f"Item Refresh Delay: {library.item_refresh_delay}")
            logger.debug(f"Clean Bundles: {library.clean_bundles}")
            logger.debug(f"Empty Trash: {library.empty_trash}")
            logger.debug(f"Optimize: {library.optimize}")
            logger.debug(f"Timeout: {library.timeout}")

            if run_args["delete-collections"] and not run_args["playlists-only"]:
                time_start = datetime.now()
                logger.info("")
                logger.separator(f"Deleting all Collections from the {library.name} Library", space=False, border=False)
                logger.info("")
                for collection in library.get_all_collections():
                    try:
                        library.delete(collection)
                        logger.info(f"Collection {collection.title} Deleted")
                    except Failed as e:
                        logger.error(e)
                library_status[library.name]["All Collections Deleted"] = str(datetime.now() - time_start).split('.')[0]

            if run_args["delete-labels"] and not run_args["playlists-only"]:
                time_start = datetime.now()
                logger.info("")
                logger.separator(f"Deleting all Labels from All items in the {library.name} Library", space=False, border=False)
                logger.info("")
                if library.is_show:
                    library_types = ["show", "season", "episode"]
                elif library.is_music:
                    library_types = ["artist", "album", "track"]
                else:
                    library_types = ["movie"]
                for library_type in library_types:
                    for item in library.get_all(builder_level=library_type):
                        try:
                            sync = ["Overlay"] if "Overlay" in [lbl.tag for lbl in item.labels] else []
                            library.edit_tags("label", item, sync_tags=sync)
                        except NotFound:
                            logger.error(f"{item.title[:25]:<25} | Labels Failed to be Removed")
                library_status[library.name]["All Labels Deleted"] = str(datetime.now() - time_start).split('.')[0]

            time_start = datetime.now()
            temp_items = None
            list_key = None
            if config.Cache:
                list_key, _ = config.Cache.query_list_cache("library", library.mapping_name, 1)

            if not temp_items:
                temp_items = library.cache_items()
                if config.Cache and list_key:
                    config.Cache.delete_list_ids(list_key)
            if not library.is_music:
                logger.info("")
                logger.separator(f"Mapping {library.original_mapping_name} Library", space=False, border=False)
                logger.info("")
                library.map_guids(temp_items)
            library_status[library.name]["Library Loading and Mapping"] = str(datetime.now() - time_start).split('.')[0]

            runs = {
                "metadata": all([not run_args[x] for x in ["tests", "operations-only", "overlays-only", "playlists-only", "collections-only"]]),
                "collections": all([not run_args[x] for x in ["operations-only", "overlays-only", "playlists-only", "metadata-only"]]),
                "operations": all([not run_args[x] for x in ["tests", "collections-only", "overlays-only", "playlists-only", "metadata-only"]]),
                "overlays": all([not run_args[x] for x in ["tests", "collections-only", "operations-only", "playlists-only", "metadata-only"]]),
            }
            for run_type in library.run_order:
                if run_type == "collections" and runs[run_type]:
                    time_start = datetime.now()
                    for metadata in library.collection_files:
                        metadata_name = metadata.get_file_name()
                        if config.requested_files and metadata_name not in config.requested_files:
                            logger.info("")
                            logger.separator(f"Skipping {metadata_name} Collection File")
                            continue
                        logger.info("")
                        logger.separator(f"Running {metadata_name} Collection File\n{metadata.path}")
                        collections_to_run = metadata.get_collections(config.requested_collections)
                        if run_args["resume"] and run_args["resume"] not in collections_to_run:
                            logger.info("")
                            logger.warning(f"Collection: {run_args['resume']} not in Collection File: {metadata.path}")
                            continue
                        if collections_to_run:
                            logger.info("")
                            logger.separator(f"{'Test ' if run_args['tests'] else ''}Collections")
                            # logger.remove_library_handler(library.mapping_name)
                            run_collection(config, library, metadata, collections_to_run)
                            # logger.re_add_library_handler(library.mapping_name)
                    library_status[library.name]["Library Collection Files"] = str(datetime.now() - time_start).split('.')[0]
                elif run_type == "metadata" and runs[run_type]:
                    time_start = datetime.now()
                    for images in library.images_files:
                        images_name = images.get_file_name()
                        if config.requested_files and images_name not in config.requested_files:
                            logger.info("")
                            logger.separator(f"Skipping {images_name} Images File")
                            continue
                        logger.info("")
                        logger.separator(f"Running {images_name} Images File\n{images.path}")
                        if not run_args["tests"] and not run_args["resume"] and not run_args["collections-only"]:
                            try:
                                images.update_metadata()
                            except Failed as e:
                                library.notify(e)
                                logger.error(e)
                    library_status[library.name]["Library Images Files"] = str(datetime.now() - time_start).split('.')[0]

                    time_start = datetime.now()
                    for metadata in library.metadata_files:
                        metadata_name = metadata.get_file_name()
                        if config.requested_files and metadata_name not in config.requested_files:
                            logger.info("")
                            logger.separator(f"Skipping {metadata_name} Metadata File")
                            continue
                        logger.info("")
                        logger.separator(f"Running {metadata_name} Metadata File\n{metadata.path}")
                        try:
                            metadata.update_metadata()
                        except Failed as e:
                            library.notify(e)
                            logger.error(e)
                    library_status[library.name]["Library Metadata Files"] = str(datetime.now() - time_start).split('.')[0]
                elif run_type == "operations" and runs[run_type] and not config.requested_files and library.library_operation:
                    library_status[library.name]["Library Operations"] = library.Operations.run_operations()
                elif run_type == "overlays" and runs[run_type] and (library.overlay_files or (library.remove_overlays and not config.requested_files)):
                    library_status[library.name]["Library Overlay Files"] = library.Overlays.run_overlays()
            #logger.remove_library_handler(library.mapping_name)
        except Exception as e:
            library.notify(e)
            logger.stacktrace()
            logger.critical(e)
    return library_status

def run_collection(config, library, metadata, requested_collections):
    logger.info("")
    for mapping_name, collection_attrs in requested_collections.items():
        collection_start = datetime.now()
        if run_args["tests"] and ("test" not in collection_attrs or collection_attrs["test"] is not True):
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

        if run_args["resume"] and run_args["resume"] != mapping_name:
            continue
        elif run_args["resume"] == mapping_name:
            run_args["resume"] = None
            logger.info("")
            logger.separator(f"Resuming Collections")

        if "name_mapping" in collection_attrs and collection_attrs["name_mapping"]:
            collection_log_name, output_str = util.validate_filename(collection_attrs["name_mapping"])
        else:
            collection_log_name, output_str = util.validate_filename(mapping_name)
        #logger.add_collection_handler(library.mapping_name, collection_log_name)
        library.status[str(mapping_name)] = {"status": "Unchanged", "errors": [], "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0}

        try:
            builder = CollectionBuilder(config, metadata, mapping_name, collection_attrs, library=library, extra=output_str)
            library.stats["names"].append(builder.name)
            if builder.build_collection:
                library.collection_names.append(builder.name)
            logger.info("")

            logger.separator(f"Running {builder.name} Collection", space=False, border=False)

            if len(builder.schedule) > 0:
                logger.info(builder.schedule)

            if len(builder.smart_filter_details) > 0:
                logger.info("")
                logger.info(builder.smart_filter_details)
                logger.info("")
                logger.info(f"Items Found: {builder.beginning_count}")

            items_added = 0
            items_removed = 0
            if not builder.smart_url and builder.builders and not builder.blank_collection:
                logger.info("")
                logger.info(f"Sync Mode: {'sync' if builder.sync else 'append'}")

                for method, value in builder.builders:
                    logger.debug("")
                    logger.debug(f"Builder: {method}: {value}")
                    logger.info("")
                    try:
                        builder.filter_and_save_items(builder.gather_ids(method, value))
                    except Failed as e:
                        if builder.ignore_blank_results:
                            logger.warning(e)
                        else:
                            raise Failed(e)

                builder.display_filters()

                if len(builder.found_items) > 0 and len(builder.found_items) + builder.beginning_count >= builder.minimum and builder.build_collection:
                    items_added, items_unchanged = builder.add_to_collection()
                    library.stats["added"] += items_added
                    library.status[str(mapping_name)]["added"] = items_added
                    library.stats["unchanged"] += items_unchanged
                    library.status[str(mapping_name)]["unchanged"] = items_unchanged
                    items_removed = 0
                    if builder.sync:
                        items_removed = builder.sync_collection()
                        library.stats["removed"] += items_removed
                        library.status[str(mapping_name)]["removed"] = items_removed

                if builder.do_missing and (len(builder.missing_movies) > 0 or len(builder.missing_shows) > 0):
                    radarr_add, sonarr_add = builder.run_missing()
                    library.stats["radarr"] += radarr_add
                    library.status[str(mapping_name)]["radarr"] += radarr_add
                    library.stats["sonarr"] += sonarr_add
                    library.status[str(mapping_name)]["sonarr"] += sonarr_add

                if not builder.found_items and not builder.ignore_blank_results:
                    raise NonExisting(f"{builder.Type} Warning: No items found")

            valid = True
            if builder.build_collection and not builder.blank_collection and items_added + builder.beginning_count < builder.minimum:
                logger.info("")
                logger.info(f"{builder.Type} Minimum: {builder.minimum} not met for {mapping_name} Collection")
                delete_status = f"Minimum {builder.minimum} Not Met"
                valid = False
                if builder.details["delete_below_minimum"] and builder.obj:
                    logger.info("")
                    logger.info(builder.delete())
                    library.stats["deleted"] += 1
                    delete_status = f"Deleted; {delete_status}"
                library.status[str(mapping_name)]["status"] = delete_status

            run_item_details = True
            if valid and builder.build_collection and (builder.builders or builder.smart_url or builder.blank_collection):
                try:
                    builder.load_collection()
                    if builder.created:
                        library.stats["created"] += 1
                        library.status[str(mapping_name)]["status"] = "Created"
                    elif items_added > 0 or items_removed > 0:
                        library.stats["modified"] += 1
                        library.status[str(mapping_name)]["status"] = "Modified"
                except Failed:
                    logger.stacktrace()
                    run_item_details = False
                    logger.info("")
                    logger.separator(f"No {builder.Type} to Update", space=False, border=False)
                else:
                    details_list = builder.update_details()
                    if details_list:
                        pre = ""
                        if library.status[str(mapping_name)]["status"] != "Unchanged":
                            pre = f"{library.status[str(mapping_name)]['status']} and "
                        library.status[str(mapping_name)]["status"] = f"{pre}Updated {', '.join(details_list)}"

            if builder.server_preroll is not None:
                library.set_server_preroll(builder.server_preroll)
                logger.info("")
                logger.info(f"Plex Server Movie pre-roll video updated to {builder.server_preroll}")

            if valid and run_item_details and (builder.item_details or builder.custom_sort or builder.sync_to_trakt_list):
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
                    if builder.sync_to_trakt_list:
                        builder.sync_trakt_list()

            builder.send_notifications()

            if builder.run_again and (len(builder.run_again_movies) > 0 or len(builder.run_again_shows) > 0):
                library.run_again.append(builder)

        except NonExisting as e:
            logger.warning(e)
            library.status[str(mapping_name)]["status"] = "Ignored"
        except NotScheduled as e:
            logger.info(e)
            if str(e).endswith("and was deleted"):
                library.notify_delete(e)
                library.stats["deleted"] += 1
                library.status[str(mapping_name)]["status"] = "Deleted Not Scheduled"
            elif str(e).startswith("Skipped because run_definition"):
                library.status[str(mapping_name)]["status"] = "Skipped Run Definition"
            else:
                library.status[str(mapping_name)]["status"] = "Not Scheduled"
        except FilterFailed:
            pass
        except Failed as e:
            library.notify(e, collection=mapping_name)
            logger.stacktrace()
            logger.error(e)
            library.status[str(mapping_name)]["status"] = "Kometa Failure"
            library.status[str(mapping_name)]["errors"].append(e)
        except Exception as e:
            library.notify(f"Unknown Error: {e}", collection=mapping_name)
            logger.stacktrace()
            logger.error(f"Unknown Error: {e}")
            library.status[str(mapping_name)]["status"] = "Unknown Error"
            library.status[str(mapping_name)]["errors"].append(e)
        collection_run_time = str(datetime.now() - collection_start).split('.')[0]
        library.status[str(mapping_name)]["run_time"] = collection_run_time
        logger.info("")
        logger.separator(f"Finished {mapping_name} Collection\nCollection Run Time: {collection_run_time}")
        #logger.remove_collection_handler(library.mapping_name, collection_log_name)

def run_playlists(config):
    stats = {"created": 0, "modified": 0, "deleted": 0, "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0, "names": []}
    status = {}
    logger.info("")
    logger.separator("Playlists")
    logger.info("")
    for playlist_file in config.playlist_files:
        for mapping_name, playlist_attrs in playlist_file.playlists.items():
            playlist_start = datetime.now()
            if run_args["tests"] and ("test" not in playlist_attrs or playlist_attrs["test"] is not True):
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
            #logger.add_playlist_handler(playlist_log_name)
            status[mapping_name] = {"status": "Unchanged", "errors": [], "added": 0, "unchanged": 0, "removed": 0, "radarr": 0, "sonarr": 0}
            server_name = None
            try:
                builder = CollectionBuilder(config, playlist_file, mapping_name, playlist_attrs, extra=output_str)
                stats["names"].append(builder.name)
                logger.info("")
                server_name = builder.libraries[0].PlexServer.friendlyName

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
                if method == "plex_watchlist":
                    ids = builder.libraries[0].get_rating_keys(method, value, True)
                elif "plex" in method:
                    ids = []
                    for pl_library in builder.libraries:
                        try:
                            ids.extend(pl_library.get_rating_keys(method, value, True))
                        except Failed as e:
                            if builder.validate_builders:
                                raise
                            else:
                                logger.error(e)
                elif "tautulli" in method:
                    ids = []
                    for pl_library in builder.libraries:
                        try:
                            ids.extend(pl_library.Tautulli.get_rating_keys(value, True))
                        except Failed as e:
                            if builder.validate_builders:
                                raise
                            else:
                                logger.error(e)
                else:
                    ids = builder.gather_ids(method, value)

                builder.display_filters()
                builder.filter_and_save_items(ids)

                if len(builder.found_items) > 0 and len(builder.found_items) + builder.beginning_count >= builder.minimum:
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
                elif len(builder.found_items) < builder.minimum:
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
                    builder.exclude_admin_from_playlist()

                builder.send_notifications(playlist=True)

            except Deleted as e:
                logger.info(e)
                status[mapping_name]["status"] = "Deleted"
                config.notify_delete(e, server=server_name)
            except NotScheduled as e:
                logger.info(e)
                if str(e).endswith("and was deleted"):
                    stats["deleted"] += 1
                    status[mapping_name]["status"] = "Deleted Not Scheduled"
                    config.notify_delete(e)
                else:
                    status[mapping_name]["status"] = "Not Scheduled"
            except Failed as e:
                config.notify(e, server=server_name, playlist=mapping_name)
                logger.stacktrace()
                logger.error(e)
                status[mapping_name]["status"] = "Kometa Failure"
                status[mapping_name]["errors"].append(e)
            except Exception as e:
                config.notify(f"Unknown Error: {e}", server=server_name, playlist=mapping_name)
                logger.stacktrace()
                logger.error(f"Unknown Error: {e}")
                status[mapping_name]["status"] = "Unknown Error"
                status[mapping_name]["errors"].append(e)
            logger.info("")
            playlist_run_time = str(datetime.now() - playlist_start).split('.')[0]
            status[mapping_name]["run_time"] = playlist_run_time
            logger.info("")
            logger.separator(f"Finished {mapping_name} Playlist\nPlaylist Run Time: {playlist_run_time}")
            #logger.remove_playlist_handler(playlist_log_name)
    return status, stats

if __name__ == "__main__":
    try:
        if run_args["run"] or run_args["tests"] or run_args["run-collections"] or run_args["run-libraries"] or run_args["run-files"] or run_args["resume"]:
            process({"collections": run_args["run-collections"], "libraries": run_args["run-libraries"], "files": run_args["run-files"]})
        else:
            times_to_run = util.get_list(run_args["times"])
            valid_times = []
            for time_to_run in times_to_run:
                try:
                    final_time = datetime.strftime(datetime.strptime(time_to_run, "%H:%M"), "%H:%M")
                    if final_time not in valid_times:
                        valid_times.append(final_time)
                except ValueError:
                    if time_to_run:
                        raise Failed(f"Argument Error: time argument invalid: {time_to_run} must be in the HH:MM format between 00:00-23:59")
                    else:
                        raise Failed(f"Argument Error: blank time argument")
            for time_to_run in valid_times:
                schedule.every().day.at(time_to_run).do(process, {"time": time_to_run})
            while True:
                schedule.run_pending()
                if not run_args["no-countdown"]:
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
                        logger.ghost(f"Current Time: {current_time} | {time_str} until the next run at {og_time_str} | Runs: {', '.join(valid_times)}")
                    else:
                        logger.error(f"Time Error: {valid_times}")
                time.sleep(60)
    except KeyboardInterrupt:
        logger.separator("Exiting Kometa")
