import datetime, logging, re, signal, sys, time, traceback

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

seperating_character = "="
screen_width = 100

method_alias = {
        "actors": "actor", "role": "actor", "roles": "actor",
        "content_ratings": "content_rating", "contentRating": "content_rating", "contentRatings": "content_rating",
        "countries": "country",
        "decades": "decade",
        "directors": "director",
        "genres": "genre",
        "studios": "studio", "network": "studio", "networks": "studio",
        "producers": "producer",
        "writers": "writer",
        "years": "year"
    }
filter_alias = {
    "actor": "actors",
    "audio_language": "audio_language",
    "collection": "collections",
    "content_rating": "contentRating",
    "country": "countries",
    "director": "directors",
    "genre": "genres",
    "max_age": "max_age",
    "originally_available": "originallyAvailableAt",
    "original_language": "original_language",
    "rating": "rating",
    "studio": "studio",
    "subtitle_language": "subtitle_language",
    "writer": "writers",
    "video_resolution": "video_resolution",
    "year": "year"
}
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
    "imdb_list": "IMDb List",
    "imdb_id": "IMDb ID",
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
    "tmdb_collection": "TMDb Collection",
    "tmdb_collection_details": "TMDb Collection",
    "tmdb_company": "TMDb Company",
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
    "tmdb_show": "TMDb Show",
    "tmdb_show_details": "TMDb Show",
    "tmdb_top_rated": "TMDb Top Rated",
    "tmdb_trending_daily": "TMDb Trending Daily",
    "tmdb_trending_weekly": "TMDb Trending Weekly",
    "trakt_list": "Trakt List",
    "trakt_trending": "Trakt Trending",
    "trakt_watchlist": "Trakt Watchlist",
    "tvdb_list": "TVDb List",
    "tvdb_movie": "TVDb Movie",
    "tvdb_show": "TVDb Show"
}
mal_ranked_name = {
    "mal_all": "all",
    "mal_airing": "airing",
    "mal_upcoming": "upcoming",
    "mal_tv": "tv",
    "mal_ova": "ova",
    "mal_movie": "movie",
    "mal_special": "special",
    "mal_popular": "bypopularity",
    "mal_favorite": "favorite"
}
mal_season_sort = {
    "anime_score": "anime_score",
    "anime_num_list_users": "anime_num_list_users",
    "score": "anime_score",
    "members": "anime_num_list_users"
}
mal_pretty = {
    "anime_score": "Score",
    "anime_num_list_users": "Members",
    "list_score": "Score",
    "list_updated_at": "Last Updated",
    "anime_title": "Title",
    "anime_start_date": "Start Date",
    "all": "All Anime",
    "watching": "Currently Watching",
    "completed": "Completed",
    "on_hold": "On Hold",
    "dropped": "Dropped",
    "plan_to_watch": "Plan to Watch"
}
mal_userlist_sort = {
    "score": "list_score",
    "list_score": "list_score",
    "last_updated": "list_updated_at",
    "list_updated": "list_updated_at",
    "list_updated_at": "list_updated_at",
    "title": "anime_title",
    "anime_title": "anime_title",
    "start_date": "anime_start_date",
    "anime_start_date": "anime_start_date"
}
mal_userlist_status = [
    "all",
    "watching",
    "completed",
    "on_hold",
    "dropped",
    "plan_to_watch"
]
pretty_ids = {
    "anidbid": "AniDB",
    "imdbid": "IMDb",
    "mal_id": "MyAnimeList",
    "themoviedb_id": "TMDb",
    "thetvdb_id": "TVDb",
    "tvdbid": "TVDb"
}
all_lists = [
    "anidb_id",
    "anidb_relation",
    "anidb_popular",
    "imdb_list",
    "imdb_id",
    "mal_id",
    "mal_all",
    "mal_airing",
    "mal_upcoming",
    "mal_tv",
    "mal_ova",
    "mal_movie",
    "mal_special",
    "mal_popular",
    "mal_favorite",
    "mal_season",
    "mal_suggested",
    "mal_userlist",
    "plex_collection",
    "plex_search",
    "tautulli_popular",
    "tautulli_watched",
    "tmdb_collection",
    "tmdb_collection_details",
    "tmdb_company",
    "tmdb_discover",
    "tmdb_keyword",
    "tmdb_list",
    "tmdb_list_details",
    "tmdb_movie",
    "tmdb_movie_details",
    "tmdb_network",
    "tmdb_now_playing",
    "tmdb_popular",
    "tmdb_show",
    "tmdb_show_details",
    "tmdb_top_rated",
    "tmdb_trending_daily",
    "tmdb_trending_weekly",
    "trakt_list",
    "trakt_trending",
    "trakt_watchlist",
    "tvdb_list",
    "tvdb_movie",
    "tvdb_show"
]
collectionless_lists = [
    "sort_title", "content_rating",
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography",
    "collection_order", "plex_collectionless",
    "url_poster", "tmdb_poster", "tmdb_profile", "file_poster",
    "url_background", "file_background",
    "name_mapping"
]
other_attributes = [
    "schedule",
    "sync_mode",
    "test",
    "tmdb_person"
]
dictionary_lists = [
    "filters",
    "mal_season",
    "mal_userlist",
    "plex_collectionless",
    "plex_search",
    "tautulli_popular",
    "tautulli_watched",
    "tmdb_discover"
]
plex_searches = [
    "actor", #"actor.not", # Waiting on PlexAPI to fix issue
    "country", #"country.not",
    "decade", #"decade.not",
    "director", #"director.not",
    "genre", #"genre.not",
    "producer", #"producer.not",
    "studio", #"studio.not",
    "writer", #"writer.not"
    "year" #"year.not",
]
show_only_lists = [
    "tmdb_network",
    "tmdb_show",
    "tmdb_show_details",
    "tvdb_show"
]
movie_only_lists = [
    "tmdb_collection",
    "tmdb_collection_details",
    "tmdb_movie",
    "tmdb_movie_details",
    "tmdb_now_playing",
    "tvdb_movie"
]
movie_only_searches = [
    "actor", "actor.not",
    "country", "country.not",
    "decade", "decade.not",
    "director", "director.not",
    "producer", "producer.not",
    "writer", "writer.not"
]
tmdb_searches = [
    "actor", "actor.not",
    "director", "director.not",
    "producer", "producer.not",
    "writer", "writer.not"
]
count_lists = [
    "anidb_popular",
    "mal_all",
    "mal_airing",
    "mal_upcoming",
    "mal_tv",
    "mal_ova",
    "mal_movie",
    "mal_special",
    "mal_popular",
    "mal_favorite",
    "mal_suggested",
    "tmdb_popular",
    "tmdb_top_rated",
    "tmdb_now_playing",
    "tmdb_trending_daily",
    "tmdb_trending_weekly",
    "trakt_trending"
]
tmdb_lists = [
    "tmdb_collection",
    "tmdb_collection_details",
    "tmdb_company",
    "tmdb_discover",
    "tmdb_keyword",
    "tmdb_list",
    "tmdb_list_details",
    "tmdb_movie",
    "tmdb_movie_details",
    "tmdb_network",
    "tmdb_now_playing",
    "tmdb_popular",
    "tmdb_show",
    "tmdb_show_details",
    "tmdb_top_rated",
    "tmdb_trending_daily",
    "tmdb_trending_weekly"
]
tmdb_type = {
    "tmdb_collection": "Collection",
    "tmdb_collection_details": "Collection",
    "tmdb_company": "Company",
    "tmdb_keyword": "Keyword",
    "tmdb_list": "List",
    "tmdb_list_details": "List",
    "tmdb_movie": "Movie",
    "tmdb_movie_details": "Movie",
    "tmdb_network": "Network",
    "tmdb_person": "Person",
    "tmdb_show": "Show",
    "tmdb_show_details": "Show"
}
all_filters = [
    "actor", "actor.not",
    "audio_language", "audio_language.not",
    "collection", "collection.not",
    "content_rating", "content_rating.not",
    "country", "country.not",
    "director", "director.not",
    "genre", "genre.not",
    "max_age",
    "originally_available.gte", "originally_available.lte",
    "original_language", "original_language.not",
    "rating.gte", "rating.lte",
    "studio", "studio.not",
    "subtitle_language", "subtitle_language.not",
    "video_resolution", "video_resolution.not",
    "writer", "writer.not",
    "year", "year.gte", "year.lte", "year.not"
]
movie_only_filters = [
    "audio_language", "audio_language.not",
    "country", "country.not",
    "director", "director.not",
    "original_language", "original_language.not",
    "subtitle_language", "subtitle_language.not",
    "video_resolution", "video_resolution.not",
    "writer", "writer.not"
]
all_details = [
    "sort_title", "content_rating",
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography",
    "collection_mode", "collection_order",
    "url_poster", "tmdb_poster", "tmdb_profile", "file_poster",
    "url_background", "file_background",
    "name_mapping", "add_to_arr"
]
discover_movie = [
    "language", "with_original_language", "region", "sort_by",
    "certification_country", "certification", "certification.lte", "certification.gte",
    "include_adult",
    "primary_release_year", "primary_release_date.gte", "primary_release_date.lte",
    "release_date.gte", "release_date.lte", "year",
    "vote_count.gte", "vote_count.lte",
    "vote_average.gte", "vote_average.lte",
    "with_cast", "with_crew", "with_people",
    "with_companies",
    "with_genres", "without_genres",
    "with_keywords", "without_keywords",
    "with_runtime.gte", "with_runtime.lte"
]
discover_tv = [
    "language", "with_original_language", "timezone", "sort_by",
    "air_date.gte", "air_date.lte",
    "first_air_date.gte", "first_air_date.lte", "first_air_date_year",
    "vote_count.gte", "vote_count.lte",
    "vote_average.gte", "vote_average.lte",
    "with_genres", "without_genres",
    "with_keywords", "without_keywords",
    "with_networks", "with_companies",
    "with_runtime.gte", "with_runtime.lte",
    "include_null_first_air_dates",
    "screened_theatrically"
]
discover_movie_sort = [
    "popularity.asc", "popularity.desc",
    "release_date.asc", "release_date.desc",
    "revenue.asc", "revenue.desc",
    "primary_release_date.asc", "primary_release_date.desc",
    "original_title.asc", "original_title.desc",
    "vote_average.asc", "vote_average.desc",
    "vote_count.asc", "vote_count.desc"
]
discover_tv_sort = [
    "vote_average.desc", "vote_average.asc",
    "first_air_date.desc", "first_air_date.asc",
    "popularity.desc", "popularity.asc"
]

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
        message = "Multiple {}s Found\n0) {}".format(description, "Create New Collection: {}".format(data) if description == "collection" else "Do Nothing")
        for i, d in enumerate(datalist, 1):
            if list_type == "title":
                if d.title == data:
                    return d
                message += "\n{}) {}".format(i, d.title)
            else:
                message += "\n{}) [{}] {}".format(i, d[0], d[1])
        if exact:
            return None
        print_multiline(message, info=True)
        while True:
            try:
                selection = int(logger_input("Choose {} number".format(description))) - 1
                if selection >= 0:                                          return datalist[selection]
                elif selection == -1:                                       return None
                else:                                                       logger.info("Invalid {} number".format(description))
            except IndexError:                                          logger.info("Invalid {} number".format(description))
            except TimeoutExpired:
                if list_type == "title":
                    logger.warning("Input Timeout: using {}".format(data))
                    return None
                else:
                    logger.warning("Input Timeout: using {}".format(datalist[0][1]))
                    return datalist[0][1]
    else:
        return None

def get_list(data, lower=False):
    if isinstance(data, list):      return data
    elif isinstance(data, dict):    return [data]
    elif lower is True:             return [d.strip().lower() for d in str(data).split(",")]
    else:                           return [d.strip() for d in str(data).split(",")]

def get_int_list(data, id_type):
    values = get_list(data)
    int_values = []
    for value in values:
        try:                        int_values.append(regex_first_int(value, id_type))
        except Failed as e:         logger.error(e)
    return int_values

def get_year_list(data, method):
    values = get_list(data)
    final_years = []
    current_year = datetime.datetime.now().year
    for value in values:
        try:
            if "-" in value:
                year_range = re.search("(\\d{4})-(\\d{4}|NOW)", str(value))
                start = year_range.group(1)
                end = year_range.group(2)
                if end == "NOW":
                    end = current_year
                if int(start) < 1800 or int(start) > current_year:      logger.error("Collection Error: Skipping {} starting year {} must be between 1800 and {}".format(method, start, current_year))
                elif int(end) < 1800 or int(end) > current_year:        logger.error("Collection Error: Skipping {} ending year {} must be between 1800 and {}".format(method, end, current_year))
                elif int(start) > int(end):                             logger.error("Collection Error: Skipping {} starting year {} cannot be greater then ending year {}".format(method, start, end))
                else:
                    for i in range(int(start), int(end) + 1):
                        final_years.append(i)
            else:
                year = re.search("(\\d+)", str(value)).group(1)
                if int(start) < 1800 or int(start) > current_year:
                    logger.error("Collection Error: Skipping {} year {} must be between 1800 and {}".format(method, year, current_year))
                else:
                    if len(str(year)) != len(str(value)):
                        logger.warning("Collection Warning: {} can be replaced with {}".format(value, year))
                    final_years.append(year)
        except AttributeError:
            logger.error("Collection Error: Skipping {} failed to parse year from {}".format(method, value))
    return final_years

def logger_input(prompt, timeout=60):
    if windows:                             return windows_input(prompt, timeout)
    elif hasattr(signal, "SIGALRM"):        return unix_input(prompt, timeout)
    else:                                   raise SystemError("Input Timeout not supported on this system")

def alarm_handler(signum, frame):
    raise TimeoutExpired

def unix_input(prompt, timeout=60):
    prompt = "| {}: ".format(prompt)
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
    try:            return input(prompt)
    finally:        signal.alarm(0)

def old_windows_input(prompt, timeout=60, timer=time.monotonic):
    prompt = "| {}: ".format(prompt)
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche())
            if result[-1] == "\n":
                out = "".join(result[:-1])
                logger.debug("{}{}".format(prompt[2:], out))
                return out
        time.sleep(0.04)
    raise TimeoutExpired

def windows_input(prompt, timeout=5):
    sys.stdout.write("| {}: ".format(prompt))
    sys.stdout.flush()
    result = []
    start_time = time.time()
    while True:
        if msvcrt.kbhit():
            chr = msvcrt.getwche()
            if ord(chr) == 13: # enter_key
                out = "".join(result)
                print("")
                logger.debug("{}: {}".format(prompt, out))
                return out
            elif ord(chr) >= 32: #space_char
                result.append(chr)
        if (time.time() - start_time) > timeout:
            print("")
            raise TimeoutExpired


def print_multiline(lines, info=False, warning=False, error=False, critical=False):
    for i, line in enumerate(lines.split("\n")):
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
    else:               raise Failed("Regex Error: Failed to parse IMDb ID from IMDb URL: {}".format(imdb_url))

def regex_first_int(data, id_type, default=None):
    match = re.search("(\\d+)", str(data))
    if match:
        return int(match.group(1))
    elif default:
        logger.warning("Regex Warning: Failed to parse {} from {} using {} as default".format(id_type, data, default))
        return int(default)
    else:
        raise Failed("Regex Error: Failed to parse {} from {}".format(id_type, data))

def remove_not(method):
    return method[:-4] if method.endswith(".not") else method

def get_centered_text(text):
    if len(text) > screen_width - 2:
        raise Failed("text must be shorter then screen_width")
    space = screen_width - len(text) - 2
    if space % 2 == 1:
        text += " "
        space -= 1
    side = int(space / 2)
    return "{}{}{}".format(" " * side, text, " " * side)

def seperator(text=None):
    logger.handlers[0].setFormatter(logging.Formatter("%(message)-{}s".format(screen_width - 2)))
    logger.handlers[1].setFormatter(logging.Formatter("[%(asctime)s] %(filename)-27s %(levelname)-10s %(message)-{}s".format(screen_width - 2)))
    logger.info("|{}|".format(seperating_character * screen_width))
    if text:
        logger.info("| {} |".format(get_centered_text(text)))
        logger.info("|{}|".format(seperating_character * screen_width))
    logger.handlers[0].setFormatter(logging.Formatter("| %(message)-{}s |".format(screen_width - 2)))
    logger.handlers[1].setFormatter(logging.Formatter("[%(asctime)s] %(filename)-27s %(levelname)-10s | %(message)-{}s |".format(screen_width - 2)))

def print_return(length, text):
    print(adjust_space(length, "| {}".format(text)), end="\r")
    return len(text) + 2

def print_end(length, text=None):
    if text:        logger.info(adjust_space(length, text))
    else:           print(adjust_space(length, " "), end="\r")
