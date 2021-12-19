import glob, logging, os, re, signal, sys, time, traceback
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathvalidate import is_valid_filename, sanitize_filename
from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.video import Season, Episode, Movie

try:
    import msvcrt
    windows = True
except ModuleNotFoundError:
    windows = False


logger = logging.getLogger("Plex Meta Manager")

class TimeoutExpired(Exception):
    pass

class Failed(Exception):
    pass

class NotScheduled(Exception):
    pass

class ImageData:
    def __init__(self, attribute, location, prefix="", is_poster=True, is_url=True):
        self.attribute = attribute
        self.location = location
        self.prefix = prefix
        self.is_poster = is_poster
        self.is_url = is_url
        self.compare = location if is_url else os.stat(location).st_size
        self.message = f"{prefix}{'poster' if is_poster else 'background'} to [{'URL' if is_url else 'File'}] {location}"

    def __str__(self):
        return str(self.__dict__)

def retry_if_not_failed(exception):
    return not isinstance(exception, Failed)

def retry_if_not_plex(exception):
    return not isinstance(exception, (BadRequest, NotFound, Unauthorized))

separating_character = "="
screen_width = 100
spacing = 0

days_alias = {
    "monday": 0, "mon": 0, "m": 0,
    "tuesday": 1, "tues": 1, "tue": 1, "tu": 1, "t": 1,
    "wednesday": 2, "wed": 2, "w": 2,
    "thursday": 3, "thurs": 3, "thur": 3, "thu": 3, "th": 3, "r": 3,
    "friday": 4, "fri": 4, "f": 4,
    "saturday": 5, "sat": 5, "s": 5,
    "sunday": 6, "sun": 6, "su": 6, "u": 6
}
mod_displays = {
    "": "is", ".not": "is not", ".is": "is", ".isnot": "is not", ".begins": "begins with", ".ends": "ends with", ".before": "is before", ".after": "is after",
    ".gt": "is greater than", ".gte": "is greater than or equal", ".lt": "is less than", ".lte": "is less than or equal"
}
pretty_days = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
pretty_months = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}
seasons = ["winter", "spring", "summer", "fall"]
pretty_ids = {"anidbid": "AniDB", "imdbid": "IMDb", "mal_id": "MyAnimeList", "themoviedb_id": "TMDb", "thetvdb_id": "TVDb", "tvdbid": "TVDb"}

def tab_new_lines(data):
    return str(data).replace("\n", "\n|\t      ") if "\n" in str(data) else str(data)

def make_ordinal(n):
    return f"{n}{'th' if 11 <= (n % 100) <= 13 else ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"

def add_zero(number):
    return str(number) if len(str(number)) > 1 else f"0{number}"

def add_dict_list(keys, value, dict_map):
    for key in keys:
        if key in dict_map:
            dict_map[key].append(value)
        else:
            dict_map[key] = [value]

def get_list(data, lower=False, split=True, int_list=False):
    if data is None:                return None
    elif isinstance(data, list):    return data
    elif isinstance(data, dict):    return [data]
    elif split is False:            return [str(data)]
    elif lower is True:             return [d.strip().lower() for d in str(data).split(",")]
    elif int_list is True:
        try:                            return [int(d.strip()) for d in str(data).split(",")]
        except ValueError:              return []
    else:                           return [d.strip() for d in str(data).split(",")]

def get_int_list(data, id_type):
    int_values = []
    for value in get_list(data):
        try:                        int_values.append(regex_first_int(value, id_type))
        except Failed as e:         logger.error(e)
    return int_values

def validate_date(date_text, method, return_as=None):
    try:                                    date_obg = datetime.strptime(str(date_text), "%Y-%m-%d" if "-" in str(date_text) else "%m/%d/%Y")
    except ValueError:                      raise Failed(f"Collection Error: {method}: {date_text} must match pattern YYYY-MM-DD (e.g. 2020-12-25) or MM/DD/YYYY (e.g. 12/25/2020)")
    return datetime.strftime(date_obg, return_as) if return_as else date_obg

def logger_input(prompt, timeout=60):
    if windows:                             return windows_input(prompt, timeout)
    elif hasattr(signal, "SIGALRM"):        return unix_input(prompt, timeout)
    else:                                   raise SystemError("Input Timeout not supported on this system")

def header(language="en-US,en;q=0.5"):
    return {"Accept-Language": "eng" if language == "default" else language, "User-Agent": "Mozilla/5.0 x64"}

def alarm_handler(signum, frame):
    raise TimeoutExpired

def unix_input(prompt, timeout=60):
    prompt = f"| {prompt}: "
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
    try:                return input(prompt)
    except EOFError:    raise Failed("Input Failed")
    finally:            signal.alarm(0)

def windows_input(prompt, timeout=5):
    sys.stdout.write(f"| {prompt}: ")
    sys.stdout.flush()
    result = []
    start_time = time.time()
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwche()
            if ord(char) == 13: # enter_key
                out = "".join(result)
                print("")
                logger.debug(f"{prompt}: {out}")
                return out
            elif ord(char) >= 32: #space_char
                result.append(char)
        if (time.time() - start_time) > timeout:
            print("")
            raise TimeoutExpired

def print_multiline(lines, info=False, warning=False, error=False, critical=False):
    for i, line in enumerate(str(lines).split("\n")):
        if critical:        logger.critical(line)
        elif error:         logger.error(line)
        elif warning:       logger.warning(line)
        elif info:          logger.info(line)
        else:               logger.debug(line)
        if i == 0:
            logger.handlers[1].setFormatter(logging.Formatter(" " * 65 + "| %(message)s"))
    logger.handlers[1].setFormatter(logging.Formatter("[%(asctime)s] %(filename)-27s %(levelname)-10s | %(message)s"))

def print_stacktrace():
    print_multiline(traceback.format_exc())

def my_except_hook(exctype, value, tb):
    for line in traceback.format_exception(etype=exctype, value=value, tb=tb):
        print_multiline(line, critical=True)

def get_id_from_imdb_url(imdb_url):
    match = re.search("(tt\\d+)", str(imdb_url))
    if match:           return match.group(1)
    else:               raise Failed(f"Regex Error: Failed to parse IMDb ID from IMDb URL: {imdb_url}")

def regex_first_int(data, id_type, default=None):
    match = re.search("(\\d+)", str(data))
    if match:
        return int(match.group(1))
    elif default:
        logger.warning(f"Regex Warning: Failed to parse {id_type} from {data} using {default} as default")
        return int(default)
    else:
        raise Failed(f"Regex Error: Failed to parse {id_type} from {data}")

def centered(text, sep=" "):
    if len(text) > screen_width - 2:
        return text
    space = screen_width - len(text) - 2
    text = f" {text} "
    if space % 2 == 1:
        text += sep
        space -= 1
    side = int(space / 2) - 1
    final_text = f"{sep * side}{text}{sep * side}"
    return final_text

def separator(text=None, space=True, border=True, debug=False):
    sep = " " if space else separating_character
    for handler in logger.handlers:
        apply_formatter(handler, border=False)
    border_text = f"|{separating_character * screen_width}|"
    if border and debug:
        logger.debug(border_text)
    elif border:
        logger.info(border_text)
    if text:
        text_list = text.split("\n")
        for t in text_list:
            if debug:
                logger.debug(f"|{sep}{centered(t, sep=sep)}{sep}|")
            else:
                logger.info(f"|{sep}{centered(t, sep=sep)}{sep}|")
        if border and debug:
            logger.debug(border_text)
        elif border:
            logger.info(border_text)
    for handler in logger.handlers:
        apply_formatter(handler)

def apply_formatter(handler, border=True):
    text = f"| %(message)-{screen_width - 2}s |" if border else f"%(message)-{screen_width - 2}s"
    if isinstance(handler, RotatingFileHandler):
        text = f"[%(asctime)s] %(filename)-27s %(levelname)-10s {text}"
    handler.setFormatter(logging.Formatter(text))

def adjust_space(display_title):
    display_title = str(display_title)
    space_length = spacing - len(display_title)
    if space_length > 0:
        display_title += " " * space_length
    return display_title

def print_return(text):
    print(adjust_space(f"| {text}"), end="\r")
    global spacing
    spacing = len(text) + 2

def print_end():
    print(adjust_space(" "), end="\r")
    global spacing
    spacing = 0

def validate_filename(filename):
    if is_valid_filename(filename):
        return filename, None
    else:
        mapping_name = sanitize_filename(filename)
        return mapping_name, f"Log Folder Name: {filename} is invalid using {mapping_name}"

def item_title(item):
    if isinstance(item, Season):
        if f"Season {item.index}" == item.title:
            return f"{item.parentTitle} {item.title}"
        else:
            return f"{item.parentTitle} Season {item.index}: {item.title}"
    elif isinstance(item, Episode):
        text = f"{item.grandparentTitle} S{add_zero(item.parentIndex)}E{add_zero(item.index)}"
        if f"Season {item.parentIndex}" == item.parentTitle:
            return f"{text}: {item.title}"
        else:
            return f"{text}: {item.parentTitle}: {item.title}"
    elif isinstance(item, Movie) and item.year:
        return f"{item.title} ({item.year})"
    else:
        return item.title

def item_set(item, item_id):
    return {"title": item_title(item), "tmdb" if isinstance(item, Movie) else "tvdb": item_id}

def is_locked(filepath):
    locked = None
    file_object = None
    if os.path.exists(filepath):
        try:
            file_object = open(filepath, 'a', 8)
            if file_object:
                locked = False
        except IOError:
            locked = True
        finally:
            if file_object:
                file_object.close()
    return locked

def time_window(tw):
    today = datetime.now()
    if tw == "today":
        return f"{today:%Y-%m-%d}"
    elif tw == "yesterday":
        return f"{today - timedelta(days=1):%Y-%m-%d}"
    elif tw == "this_week":
        return f"{today:%Y-0%V}"
    elif tw == "last_week":
        return f"{today - timedelta(weeks=1):%Y-0%V}"
    elif tw == "this_month":
        return f"{today:%Y-%m}"
    elif tw == "last_month":
        return f"{today.year}-{today.month - 1 or 12}"
    elif tw == "this_year":
        return f"{today.year}"
    elif tw == "last_year":
        return f"{today.year - 1}"
    else:
        return tw

def glob_filter(filter_in):
    filter_in = filter_in.translate({ord("["): "[[]", ord("]"): "[]]"}) if "[" in filter_in else filter_in
    return glob.glob(filter_in)

def is_date_filter(value, modifier, data, final, current_time):
    if value is None:
        return True
    if modifier in ["", ".not"]:
        threshold_date = current_time - timedelta(days=data)
        if (modifier == "" and (value is None or value < threshold_date)) \
                or (modifier == ".not" and value and value >= threshold_date):
            return True
    elif modifier in [".before", ".after"]:
        filter_date = validate_date(data, final)
        if (modifier == ".before" and value >= filter_date) or (modifier == ".after" and value <= filter_date):
            return True
    elif modifier == ".regex":
        jailbreak = True
        for check_data in data:
            if re.compile(check_data).match(value.strftime("%m/%d/%Y")):
                jailbreak = True
                break
        if not jailbreak:
            return True
    return False

def is_number_filter(value, modifier, data):
    return value is None or (modifier == ".gt" and value <= data) \
            or (modifier == ".gte" and value < data) \
            or (modifier == ".lt" and value >= data) \
            or (modifier == ".lte" and value > data)

def is_boolean_filter(value, data):
    return (data and not value) or (not data and value)

def is_string_filter(values, modifier, data):
    jailbreak = False
    for value in values:
        for check_value in data:
            if (modifier in ["", ".not"] and check_value.lower() in value.lower()) \
                    or (modifier in [".is", ".isnot"] and value.lower() == check_value.lower()) \
                    or (modifier == ".begins" and value.lower().startswith(check_value.lower())) \
                    or (modifier == ".ends" and value.lower().endswith(check_value.lower())) \
                    or (modifier == ".regex" and re.compile(check_value).match(value)):
                jailbreak = True
                break
        if jailbreak: break
    return (jailbreak and modifier in [".not", ".isnot"]) or (not jailbreak and modifier in ["", ".is", ".begins", ".ends", ".regex"])


def check_day(_m, _d):
    if _m in [1, 3, 5, 7, 8, 10, 12] and _d > 31:
        return _m, 31
    elif _m in [4, 6, 9, 11] and _d > 30:
        return _m, 30
    elif _m == 2 and _d > 28:
        return _m, 28
    else:
        return _m, _d

def schedule_check(data, current_time, run_hour):
    skip_collection = True
    schedule_list = get_list(data)
    next_month = current_time.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    schedule_str = ""
    for schedule in schedule_list:
        run_time = str(schedule).lower()
        if run_time.startswith(("day", "daily")):
            skip_collection = False
        elif run_time == "never":
            schedule_str += f"\nNever scheduled to run"
        elif run_time.startswith(("hour", "week", "month", "year", "range")):
            match = re.search("\\(([^)]+)\\)", run_time)
            if not match:
                logger.error(f"Schedule Error: failed to parse schedule: {schedule}")
                continue
            param = match.group(1)
            if run_time.startswith("hour"):
                try:
                    if 0 <= int(param) <= 23:
                        schedule_str += f"\nScheduled to run only on the {make_ordinal(int(param))} hour"
                        if run_hour == int(param):
                            skip_collection = False
                    else:
                        raise ValueError
                except ValueError:
                    logger.error(f"Schedule Error: hourly schedule attribute {schedule} invalid must be an integer between 0 and 23")
            elif run_time.startswith("week"):
                if param.lower() not in days_alias:
                    logger.error(f"Schedule Error: weekly schedule attribute {schedule} invalid must be a day of the week i.e. weekly(Monday)")
                    continue
                weekday = days_alias[param.lower()]
                schedule_str += f"\nScheduled weekly on {pretty_days[weekday]}"
                if weekday == current_time.weekday():
                    skip_collection = False
            elif run_time.startswith("month"):
                try:
                    if 1 <= int(param) <= 31:
                        schedule_str += f"\nScheduled monthly on the {make_ordinal(int(param))}"
                        if current_time.day == int(param) or (
                                current_time.day == last_day.day and int(param) > last_day.day):
                            skip_collection = False
                    else:
                        raise ValueError
                except ValueError:
                    logger.error(f"Schedule Error: monthly schedule attribute {schedule} invalid must be an integer between 1 and 31")
            elif run_time.startswith("year"):
                try:
                    if "/" in param:
                        opt = param.split("/")
                        month = int(opt[0])
                        day = int(opt[1])
                        schedule_str += f"\nScheduled yearly on {pretty_months[month]} {make_ordinal(day)}"
                        if current_time.month == month and (current_time.day == day or (
                                current_time.day == last_day.day and day > last_day.day)):
                            skip_collection = False
                    else:
                        raise ValueError
                except ValueError:
                    logger.error(
                        f"Schedule Error: yearly schedule attribute {schedule} invalid must be in the MM/DD format i.e. yearly(11/22)")
            elif run_time.startswith("range"):
                match = re.match("^(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])-(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])$", param)
                if not match:
                    logger.error(f"Schedule Error: range schedule attribute {schedule} invalid must be in the MM/DD-MM/DD format i.e. range(12/01-12/25)")
                    continue
                month_start, day_start = check_day(int(match.group(1)), int(match.group(2)))
                month_end, day_end = check_day(int(match.group(3)), int(match.group(4)))
                month_check, day_check = check_day(current_time.month, current_time.day)
                check = datetime.strptime(f"{month_check}/{day_check}", "%m/%d")
                start = datetime.strptime(f"{month_start}/{day_start}", "%m/%d")
                end = datetime.strptime(f"{month_end}/{day_end}", "%m/%d")
                schedule_str += f"\nScheduled between {pretty_months[month_start]} {make_ordinal(day_start)} and {pretty_months[month_end]} {make_ordinal(day_end)}"
                if start <= check <= end if start < end else (check <= end or check >= start):
                    skip_collection = False
        else:
            logger.error(f"Schedule Error: schedule attribute {schedule} invalid")
    if len(schedule_str) == 0:
        skip_collection = False
    if skip_collection:
        raise NotScheduled(schedule_str)
