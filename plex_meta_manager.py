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
parser.add_argument("-r", "--run", dest="run", help="Run without the scheduler", action="store_true", default=False)
parser.add_argument("-rt", "--test", "--tests", "--run-test", "--run-tests", dest="test", help="Run in debug mode with only collections that have test: true", action="store_true", default=False)
parser.add_argument("-cl", "--collection", "--collections", dest="collections", help="Process only specified collections (comma-separated list)", type=str, default="")
parser.add_argument("-d", "--divider", dest="divider", help="Character that divides the sections (Default: '=')", default="=", type=str)
parser.add_argument("-w", "--width", dest="width", help="Screen Width (Default: 100)", default=100, type=int)
args = parser.parse_args()

if not re.match("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", args.time):
    raise util.Failed(f"Argument Error: time argument invalid: {args.time} must be in the HH:MM format")

util.separating_character = args.divider[0]
if 90 <= args.width <= 300:
    util.screen_width = args.width
else:
    raise util.Failed(f"Argument Error: width argument invalid: {args.width} must be an integer between 90 and 300")

default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
if args.config and os.path.exists(args.config):                     default_dir = os.path.join(os.path.dirname(os.path.abspath(args.config)))
elif args.config and not os.path.exists(args.config):               raise util.Failed(f"Config Error: config not found at {os.path.abspath(args.config)}")
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
cmd_handler.setLevel(logging.DEBUG if args.tests or args.test or args.debug else logging.INFO)

logger.addHandler(cmd_handler)
logger.addHandler(file_handler)

sys.excepthook = util.my_except_hook

util.separator()
logger.info(util.get_centered_text("                                                                                     "))
logger.info(util.get_centered_text(" ____  _             __  __      _          __  __                                   "))
logger.info(util.get_centered_text("|  _ \\| | _____  __ |  \\/  | ___| |_ __ _  |  \\/  | __ _ _ __   __ _  __ _  ___ _ __ "))
logger.info(util.get_centered_text("| |_) | |/ _ \\ \\/ / | |\\/| |/ _ \\ __/ _` | | |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__|"))
logger.info(util.get_centered_text("|  __/| |  __/>  <  | |  | |  __/ || (_| | | |  | | (_| | | | | (_| | (_| |  __/ |   "))
logger.info(util.get_centered_text("|_|   |_|\\___/_/\\_\\ |_|  |_|\\___|\\__\\__,_| |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|   "))
logger.info(util.get_centered_text("                                                                     |___/           "))
logger.info(util.get_centered_text("    Version: 1.4.0                                                                   "))
util.separator()

if args.tests:
    tests.run_tests(default_dir)
    sys.exit(0)

def start(config_path, test, daily, collections):
    if daily:               start_type = "Daily "
    elif test:              start_type = "Test "
    elif collections:       start_type = "Collections "
    else:                   start_type = ""
    start_time = datetime.now()
    util.separator(f"Starting {start_type}Run")
    try:
        config = Config(default_dir, config_path)
        config.update_libraries(test, collections)
    except Exception as e:
        util.print_stacktrace()
        logger.critical(e)
    logger.info("")
    util.separator(f"Finished {start_type}Run\nRun Time: {str(datetime.now() - start_time).split('.')[0]}")

try:
    if args.run or args.test or args.collections:
        start(args.config, args.test, False, args.collections)
    else:
        length = 0
        schedule.every().day.at(args.time).do(start, args.config, False, True, None)
        while True:
            schedule.run_pending()
            current = datetime.now().strftime("%H:%M")
            seconds = (datetime.strptime(args.time, "%H:%M") - datetime.strptime(current, "%H:%M")).total_seconds()
            hours = int(seconds // 3600)
            if hours < 0:
                hours += 24
            minutes = int((seconds % 3600) // 60)
            time_str = f"{hours} Hour{'s' if hours > 1 else ''} and " if hours > 0 else ""
            time_str += f"{minutes} Minute{'s' if minutes > 1 else ''}"

            length = util.print_return(length, f"Current Time: {current} | {time_str} until the daily run at {args.time}")
            time.sleep(1)
except KeyboardInterrupt:
    util.separator("Exiting Plex Meta Manager")
