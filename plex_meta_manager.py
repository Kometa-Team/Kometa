import argparse, logging, os, re, sys, time
from datetime import datetime
try:
    import schedule
    from modules import tests, util
    from modules.config import Config
except ModuleNotFoundError:
    print("Error: Requirements are not installed")
    sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("--my-tests", dest="tests", help=argparse.SUPPRESS, action="store_true", default=False)
parser.add_argument("--debug", dest="debug", help=argparse.SUPPRESS, action="store_true", default=False)
parser.add_argument("-c", "--config", dest="config", help="Run with desired *.yml file", type=str)
parser.add_argument("-t", "--time", dest="time", help="Time to update each day use format HH:MM (Default: 03:00)", default="03:00", type=str)
parser.add_argument("-re", "--resume", dest="resume", help="Resume collection run from a specific collection", type=str)
parser.add_argument("-r", "--run", dest="run", help="Run without the scheduler", action="store_true", default=False)
parser.add_argument("-rt", "--test", "--tests", "--run-test", "--run-tests", dest="test", help="Run in debug mode with only collections that have test: true", action="store_true", default=False)
parser.add_argument("-cl", "--collection", "--collections", dest="collections", help="Process only specified collections (comma-separated list)", type=str)
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

my_tests = check_bool("PMM_TESTS", args.tests)
test = check_bool("PMM_TEST", args.test)
debug = check_bool("PMM_DEBUG", args.debug)
run = check_bool("PMM_RUN", args.run)
collections = os.environ.get("PMM_COLLECTIONS") if os.environ.get("PMM_COLLECTIONS") else args.collections
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
cmd_handler.setLevel(logging.DEBUG if my_tests or test or debug else logging.INFO)

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
util.centered("    Version: 1.7.1-beta.1                                                            ")
util.separator()

if my_tests:
    tests.run_tests(default_dir)
    sys.exit(0)

def start(config_path, is_test, daily, collections_to_run, resume_from):
    if daily:               start_type = "Daily "
    elif is_test:           start_type = "Test "
    elif collections_to_run:       start_type = "Collections "
    else:                   start_type = ""
    start_time = datetime.now()
    util.separator(f"Starting {start_type}Run")
    try:
        config = Config(default_dir, config_path)
        config.update_libraries(is_test, collections_to_run, resume_from)
    except Exception as e:
        util.print_stacktrace()
        logger.critical(e)
    logger.info("")
    util.separator(f"Finished {start_type}Run\nRun Time: {str(datetime.now() - start_time).split('.')[0]}")

try:
    if run or test or collections or resume:
        start(config_file, test, False, collections, resume)
    else:
        length = 0
        schedule.every().day.at(time_to_run).do(start, config_file, False, True, None, None)
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

            length = util.print_return(length, f"Current Time: {current} | {time_str} until the daily run at {time_to_run}")
            time.sleep(1)
except KeyboardInterrupt:
    util.separator("Exiting Plex Meta Manager")
