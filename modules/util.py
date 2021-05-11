import logging, re, signal, sys, time, traceback
from datetime import datetime
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

def retry_if_not_failed(exception):
    return not isinstance(exception, Failed)

def retry_if_not_plex(exception):
    return not isinstance(exception, (BadRequest, NotFound, Unauthorized))

separating_character = "="
screen_width = 100

days_alias = {
    "monday": 0, "mon": 0, "m": 0,
    "tuesday": 1, "tues": 1, "tue": 1, "tu": 1, "t": 1,
    "wednesday": 2, "wed": 2, "w": 2,
    "thursday": 3, "thurs": 3, "thur": 3, "thu": 3, "th": 3, "r": 3,
    "friday": 4, "fri": 4, "f": 4,
    "saturday": 5, "sat": 5, "s": 5,
    "sunday": 6, "sun": 6, "su": 6, "u": 6
}
pretty_days = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}
pretty_months = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}
pretty_seasons = {
    "winter": "Winter",
    "spring": "Spring",
    "summer": "Summer",
    "fall": "Fall"
}
pretty_names = {
    "anidb_id": "AniDB ID",
    "anidb_relation": "AniDB Relation",
    "anidb_popular": "AniDB Popular",
    "anilist_genre": "AniList Genre",
    "anilist_id": "AniList ID",
    "anilist_popular": "AniList Popular",
    "anilist_relations": "AniList Relations",
    "anilist_season": "AniList Season",
    "anilist_studio": "AniList Studio",
    "anilist_tag": "AniList Tag",
    "anilist_top_rated": "AniList Top Rated",
    "imdb_list": "IMDb List",
    "imdb_id": "IMDb ID",
    "letterboxd_list": "Letterboxd List",
    "letterboxd_list_details": "Letterboxd List",
    "mal_id": "MyAnimeList ID",
    "mal_all": "MyAnimeList All",
    "mal_airing": "MyAnimeList Airing",
    "mal_upcoming": "MyAnimeList Upcoming",
    "mal_tv": "MyAnimeList TV",
    "mal_ova": "MyAnimeList OVA",
    "mal_movie": "MyAnimeList Movie",
    "mal_special": "MyAnimeList Special",
    "mal_popular": "MyAnimeList Popular",
    "mal_favorite": "MyAnimeList Favorite",
    "mal_season": "MyAnimeList Season",
    "mal_suggested": "MyAnimeList Suggested",
    "mal_userlist": "MyAnimeList Userlist",
    "plex_all": "Plex All",
    "plex_collection": "Plex Collection",
    "plex_search": "Plex Search",
    "tautulli_popular": "Tautulli Popular",
    "tautulli_watched": "Tautulli Watched",
    "tmdb_actor": "TMDb Actor",
    "tmdb_actor_details": "TMDb Actor",
    "tmdb_collection": "TMDb Collection",
    "tmdb_collection_details": "TMDb Collection",
    "tmdb_company": "TMDb Company",
    "tmdb_crew": "TMDb Crew",
    "tmdb_crew_details": "TMDb Crew",
    "tmdb_director": "TMDb Director",
    "tmdb_director_details": "TMDb Director",
    "tmdb_discover": "TMDb Discover",
    "tmdb_keyword": "TMDb Keyword",
    "tmdb_list": "TMDb List",
    "tmdb_list_details": "TMDb List",
    "tmdb_movie": "TMDb Movie",
    "tmdb_movie_details": "TMDb Movie",
    "tmdb_network": "TMDb Network",
    "tmdb_now_playing": "TMDb Now Playing",
    "tmdb_person": "TMDb Person",
    "tmdb_popular": "TMDb Popular",
    "tmdb_producer": "TMDb Producer",
    "tmdb_producer_details": "TMDb Producer",
    "tmdb_show": "TMDb Show",
    "tmdb_show_details": "TMDb Show",
    "tmdb_top_rated": "TMDb Top Rated",
    "tmdb_trending_daily": "TMDb Trending Daily",
    "tmdb_trending_weekly": "TMDb Trending Weekly",
    "tmdb_writer": "TMDb Writer",
    "tmdb_writer_details": "TMDb Writer",
    "trakt_collected": "Trakt Collected",
    "trakt_collection": "Trakt Collection",
    "trakt_list": "Trakt List",
    "trakt_list_details": "Trakt List",
    "trakt_popular": "Trakt Popular",
    "trakt_recommended": "Trakt Recommended",
    "trakt_trending": "Trakt Trending",
    "trakt_watched": "Trakt Watched",
    "trakt_watchlist": "Trakt Watchlist",
    "tvdb_list": "TVDb List",
    "tvdb_list_details": "TVDb List",
    "tvdb_movie": "TVDb Movie",
    "tvdb_movie_details": "TVDb Movie",
    "tvdb_show": "TVDb Show",
    "tvdb_show_details": "TVDb Show"
}
pretty_ids = {
    "anidbid": "AniDB",
    "imdbid": "IMDb",
    "mal_id": "MyAnimeList",
    "themoviedb_id": "TMDb",
    "thetvdb_id": "TVDb",
    "tvdbid": "TVDb"
}

def tab_new_lines(data):
    return str(data).replace("\n", "\n|\t      ") if "\n" in str(data) else str(data)

def adjust_space(old_length, display_title):
    display_title = str(display_title)
    space_length = old_length - len(display_title)
    if space_length > 0:
        display_title += " " * space_length
    return display_title

def make_ordinal(n):
    n = int(n)
    suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    return str(n) + suffix

def choose_from_list(datalist, description, data=None, list_type="title", exact=False):
    if len(datalist) > 0:
        if len(datalist) == 1 and (description != "collection" or datalist[0].title == data):
            return datalist[0]
        zero_option = f"Create New Collection: {data}" if description == "collection" else "Do Nothing"
        message = f"Multiple {description}s Found\n0) {zero_option}"
        for i, d in enumerate(datalist, 1):
            if list_type == "title":
                if d.title == data:
                    return d
                message += f"\n{i}) {d.title}"
            else:
                message += f"\n{i}) [{d[0]}] {d[1]}"
        if exact:
            return None
        print_multiline(message, info=True)
        while True:
            try:
                selection = int(logger_input(f"Choose {description} number")) - 1
                if selection >= 0:                                          return datalist[selection]
                elif selection == -1:                                       return None
                else:                                                       logger.info(f"Invalid {description} number")
            except IndexError:                                          logger.info(f"Invalid {description} number")
            except TimeoutExpired:
                if list_type == "title":
                    logger.warning(f"Input Timeout: using {data}")
                    return None
                else:
                    logger.warning(f"Input Timeout: using {datalist[0][1]}")
                    return datalist[0]
    else:
        return None

def get_bool(method_name, method_data):
    if isinstance(method_data, bool):
        return method_data
    elif str(method_data).lower() in ["t", "true"]:
        return True
    elif str(method_data).lower() in ["f", "false"]:
        return False
    else:
        raise Failed(f"Collection Error: {method_name} attribute: {method_data} invalid must be either true or false")

def compile_list(data):
    if isinstance(data, list):
        text = ""
        for item in data:
            text += f"{',' if len(text) > 0 else ''}{item}"
        return text
    else:
        return data


def get_list(data, lower=False, split=True, int_list=False):
    if isinstance(data, list):      return data
    elif isinstance(data, dict):    return [data]
    elif split is False:            return [str(data)]
    elif lower is True:             return [d.strip().lower() for d in str(data).split(",")]
    elif int_list is True:          return [int(d.strip()) for d in str(data).split(",")]
    else:                           return [d.strip() for d in str(data).split(",")]

def get_int_list(data, id_type):
    values = get_list(data)
    int_values = []
    for value in values:
        try:                        int_values.append(regex_first_int(value, id_type))
        except Failed as e:         logger.error(e)
    return int_values

def get_year_list(data, current_year, method):
    final_years = []
    values = get_list(data)
    for value in values:
        final_years.append(check_year(value, current_year, method))
    return final_years

def check_year(year, current_year, method):
    return check_number(year, method, minimum=1800, maximum=current_year)

def check_number(value, method, number_type="int", minimum=None, maximum=None):
    if number_type == "int":
        try:                                                    num_value = int(str(value))
        except ValueError:                                      raise Failed(f"Collection Error: {method}: {value} must be an integer")
    elif number_type == "float":
        try:                                                    num_value = float(str(value))
        except ValueError:                                      raise Failed(f"Collection Error: {method}: {value} must be a number")
    else:                                                   raise Failed(f"Number Type: {number_type} invalid")
    if minimum is not None and maximum is not None and (num_value < minimum or num_value > maximum):
        raise Failed(f"Collection Error: {method}: {num_value} must be between {minimum} and {maximum}")
    elif minimum is not None and num_value < minimum:
        raise Failed(f"Collection Error: {method}: {num_value} is less then  {minimum}")
    elif maximum is not None and num_value > maximum:
        raise Failed(f"Collection Error: {method}: {num_value} is greater then  {maximum}")
    else:
        return num_value

def check_date(date_text, method, return_string=False, plex_date=False):
    try:                                    date_obg = datetime.strptime(str(date_text), "%Y-%m-%d" if plex_date else "%m/%d/%Y")
    except ValueError:                      raise Failed(f"Collection Error: {method}: {date_text} must match pattern {'YYYY-MM-DD e.g. 2020-12-25' if plex_date else 'MM/DD/YYYY e.g. 12/25/2020'}")
    return str(date_text) if return_string else date_obg

def logger_input(prompt, timeout=60):
    if windows:                             return windows_input(prompt, timeout)
    elif hasattr(signal, "SIGALRM"):        return unix_input(prompt, timeout)
    else:                                   raise SystemError("Input Timeout not supported on this system")

def alarm_handler(signum, frame):
    raise TimeoutExpired

def unix_input(prompt, timeout=60):
    prompt = f"| {prompt}: "
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
    try:            return input(prompt)
    finally:        signal.alarm(0)

def old_windows_input(prompt, timeout=60, timer=time.monotonic):
    prompt = f"| {prompt}: "
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche())
            if result[-1] == "\n":
                out = "".join(result[:-1])
                logger.debug(f"{prompt[2:]}{out}")
                return out
        time.sleep(0.04)
    raise TimeoutExpired

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

def centered(text, do_print=True):
    if len(text) > screen_width - 2:
        raise Failed("text must be shorter then screen_width")
    space = screen_width - len(text) - 2
    if space % 2 == 1:
        text += " "
        space -= 1
    side = int(space / 2)
    final_text = f"{' ' * side}{text}{' ' * side}"
    if do_print:
        logger.info(final_text)
    return final_text

def separator(text=None):
    logger.handlers[0].setFormatter(logging.Formatter(f"%(message)-{screen_width - 2}s"))
    logger.handlers[1].setFormatter(logging.Formatter(f"[%(asctime)s] %(filename)-27s %(levelname)-10s %(message)-{screen_width - 2}s"))
    logger.info(f"|{separating_character * screen_width}|")
    if text:
        text_list = text.split("\n")
        for t in text_list:
            logger.info(f"| {centered(t, do_print=False)} |")
        logger.info(f"|{separating_character * screen_width}|")
    logger.handlers[0].setFormatter(logging.Formatter(f"| %(message)-{screen_width - 2}s |"))
    logger.handlers[1].setFormatter(logging.Formatter(f"[%(asctime)s] %(filename)-27s %(levelname)-10s | %(message)-{screen_width - 2}s |"))

def print_return(length, text):
    print(adjust_space(length, f"| {text}"), end="\r")
    return len(text) + 2

def print_end(length, text=None):
    if text:        logger.info(adjust_space(length, text))
    else:           print(adjust_space(length, " "), end="\r")
