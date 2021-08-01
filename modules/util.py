import logging, os, re, signal, sys, time, traceback
from datetime import datetime
from pathvalidate import is_valid_filename, sanitize_filename
from plexapi.exceptions import BadRequest, NotFound, Unauthorized

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

class ImageData:
    def __init__(self, attribute, location, prefix="", is_poster=True, is_url=True):
        self.attribute = attribute
        self.location = location
        self.prefix = prefix
        self.is_poster = is_poster
        self.is_url = is_url
        self.compare = location if is_url else os.stat(location).st_size
        self.message = f"{prefix}{'poster' if is_poster else 'background'} to [{'URL' if is_url else 'File'}] {location}"

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
pretty_days = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
pretty_months = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}
pretty_seasons = {"winter": "Winter", "spring": "Spring", "summer": "Summer", "fall": "Fall"}
pretty_ids = {"anidbid": "AniDB", "imdbid": "IMDb", "mal_id": "MyAnimeList", "themoviedb_id": "TMDb", "thetvdb_id": "TVDb", "tvdbid": "TVDb"}

def tab_new_lines(data):
    return str(data).replace("\n", "\n|\t      ") if "\n" in str(data) else str(data)

def make_ordinal(n):
    return f"{n}{'th' if 11 <= (n % 100) <= 13 else ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"

def compile_list(data):
    if isinstance(data, list):
        text = ""
        for item in data:
            text += f"{',' if len(text) > 0 else ''}{item}"
        return text
    else:
        return data

def get_list(data, lower=False, split=True, int_list=False):
    if data is None:                return None
    elif isinstance(data, list):    return data
    elif isinstance(data, dict):    return [data]
    elif split is False:            return [str(data)]
    elif lower is True:             return [d.strip().lower() for d in str(data).split(",")]
    elif int_list is True:          return [int(d.strip()) for d in str(data).split(",")]
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
    return {"Accept-Language": language, "User-Agent": "Mozilla/5.0 x64"}

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
            logger.info(f"|{sep}{centered(t, sep=sep)}{sep}|")
        if border and debug:
            logger.debug(border_text)
        elif border:
            logger.info(border_text)
    for handler in logger.handlers:
        apply_formatter(handler)

def apply_formatter(handler, border=True):
    text = f"| %(message)-{screen_width - 2}s |" if border else f"%(message)-{screen_width - 2}s"
    if isinstance(handler, logging.handlers.RotatingFileHandler):
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

def parse(attribute, data, datatype=None, methods=None, parent=None, default=None, options=None, translation=None, minimum=1, maximum=None):
    display = f"{parent + ' ' if parent else ''}{attribute} attribute"
    if options is None and translation is not None:
        options = [o for o in translation]
    value = data[methods[attribute]] if methods and attribute in methods else data

    if datatype == "list":
        if methods and attribute in methods and data[methods[attribute]]:
            return [v for v in value if v] if isinstance(value, list) else [str(value)]
        return []
    elif datatype == "dictlist":
        final_list = []
        for dict_data in get_list(value):
            if isinstance(dict_data, dict):
                final_list.append((dict_data, {dm.lower(): dm for dm in dict_data}))
            else:
                raise Failed(f"Collection Error: {display} {dict_data} is not a dictionary")
        return final_list
    elif methods and attribute not in methods:
        message = f"{display} not found"
    elif value is None:
        message = f"{display} is blank"
    elif datatype == "bool":
        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return value > 0
        elif str(value).lower() in ["t", "true"]:
            return True
        elif str(value).lower() in ["f", "false"]:
            return False
        else:
            message = f"{display} must be either true or false"
    elif datatype in ["int", "float"]:
        try:
            value = int(str(value)) if datatype == "int" else float(str(value))
            if (maximum is None and minimum <= value) or (maximum is not None and minimum <= value <= maximum):
                return value
        except ValueError:
            pass
        pre = f"{display} {value} must {'an integer' if datatype == 'int' else 'a number'}"
        if maximum is None:
            message = f"{pre} {minimum} or greater"
        else:
            message = f"{pre} between {minimum} and {maximum}"
    elif (translation is not None and str(value).lower() not in translation) or \
            (options is not None and translation is None and str(value).lower() not in options):
        message = f"{display} {value} must be in {options}"
    else:
        return translation[value] if translation is not None else value

    if default is None:
        raise Failed(f"Collection Error: {message}")
    else:
        logger.warning(f"Collection Warning: {message} using {default} as default")
        return translation[default] if translation is not None else default
