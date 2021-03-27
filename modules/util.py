import logging, re, signal, sys, time, traceback
from datetime import datetime

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

separating_character = "="
screen_width = 100

method_alias = {
    "actors": "actor", "role": "actor", "roles": "actor",
    "content_ratings": "content_rating", "contentRating": "content_rating", "contentRatings": "content_rating",
    "countries": "country",
    "decades": "decade",
    "directors": "director",
    "genres": "genre",
    "labels": "label",
    "studios": "studio", "network": "studio", "networks": "studio",
    "producers": "producer",
    "writers": "writer",
    "years": "year"
}
search_alias = {
    "audio_language": "audioLanguage",
    "content_rating": "contentRating",
    "subtitle_language": "subtitleLanguage",
    "added": "addedAt",
    "originally_available": "originallyAvailableAt",
    "rating": "userRating"
}
filter_alias = {
    "actor": "actors",
    "collection": "collections",
    "content_rating": "contentRating",
    "country": "countries",
    "director": "directors",
    "genre": "genres",
    "originally_available": "originallyAvailableAt",
    "tmdb_vote_count": "vote_count",
    "writer": "writers"
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
plex_languages = ["default", "ar-SA", "ca-ES", "cs-CZ", "da-DK", "de-DE", "el-GR", "en-AU", "en-CA", "en-GB", "en-US", "es-ES",
                     "es-MX", "et-EE", "fa-IR", "fi-FI", "fr-CA", "fr-FR", "he-IL", "hi-IN", "hu-HU", "id-ID", "it-IT",
                     "ja-JP", "ko-KR", "lt-LT", "lv-LV", "nb-NO", "nl-NL", "pl-PL", "pt-BR", "pt-PT", "ro-RO", "ru-RU",
                     "sk-SK", "sv-SE", "th-TH", "tr-TR", "uk-UA", "vi-VN", "zh-CN", "zh-HK", "zh-TW"]
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
anilist_pretty = {
    "score": "Average Score",
    "popular": "Popularity"
}
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
    "anilist_genre",
    "anilist_id",
    "anilist_popular",
    "anilist_relations",
    "anilist_season",
    "anilist_studio",
    "anilist_tag",
    "anilist_top_rated",
    "imdb_list",
    "imdb_id",
    "letterboxd_list",
    "letterboxd_list_details",
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
    "tmdb_actor",
    "tmdb_actor_details",
    "tmdb_collection",
    "tmdb_collection_details",
    "tmdb_company",
    "tmdb_crew",
    "tmdb_crew_details",
    "tmdb_director",
    "tmdb_director_details",
    "tmdb_discover",
    "tmdb_keyword",
    "tmdb_list",
    "tmdb_list_details",
    "tmdb_movie",
    "tmdb_movie_details",
    "tmdb_network",
    "tmdb_now_playing",
    "tmdb_popular",
    "tmdb_producer",
    "tmdb_producer_details",
    "tmdb_show",
    "tmdb_show_details",
    "tmdb_top_rated",
    "tmdb_trending_daily",
    "tmdb_trending_weekly",
    "tmdb_writer",
    "tmdb_writer_details",
    "trakt_collected",
    "trakt_collection",
    "trakt_list",
    "trakt_list_details",
    "trakt_popular",
    "trakt_recommended",
    "trakt_trending",
    "trakt_watched",
    "trakt_watchlist",
    "tvdb_list",
    "tvdb_list_details",
    "tvdb_movie",
    "tvdb_movie_details",
    "tvdb_show",
    "tvdb_show_details"
]
collectionless_lists = [
    "sort_title", "content_rating",
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography",
    "collection_order", "plex_collectionless",
    "url_poster", "tmdb_poster", "tmdb_profile", "file_poster",
    "url_background", "file_background",
    "name_mapping", "label", "label_sync_mode", "test"
]
other_attributes = [
    "run_again",
    "schedule",
    "sync_mode",
    "template",
    "test",
    "tmdb_person"
]
dictionary_lists = [
    "filters",
    "anilist_genre",
    "anilist_season",
    "anilist_tag",
    "mal_season",
    "mal_userlist",
    "plex_collectionless",
    "plex_search",
    "tautulli_popular",
    "tautulli_watched",
    "tmdb_discover"
]
show_only_lists = [
    "tmdb_network",
    "tmdb_show",
    "tmdb_show_details",
    "tvdb_show",
    "tvdb_show_details"
]
movie_only_lists = [
    "letterboxd_list",
    "letterboxd_list_details",
    "tmdb_collection",
    "tmdb_collection_details",
    "tmdb_movie",
    "tmdb_movie_details",
    "tmdb_now_playing",
    "tvdb_movie",
    "tvdb_movie_details"
]
count_lists = [
    "anidb_popular",
    "anilist_popular",
    "anilist_top_rated",
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
    "trakt_trending",
    "trakt_popular",
    "trakt_recommended",
    "trakt_watched",
    "trakt_collected"
]
tmdb_lists = [
    "tmdb_actor",
    "tmdb_actor_details",
    "tmdb_collection",
    "tmdb_collection_details",
    "tmdb_company",
    "tmdb_crew",
    "tmdb_crew_details",
    "tmdb_director",
    "tmdb_director_details",
    "tmdb_discover",
    "tmdb_keyword",
    "tmdb_list",
    "tmdb_list_details",
    "tmdb_movie",
    "tmdb_movie_details",
    "tmdb_network",
    "tmdb_now_playing",
    "tmdb_popular",
    "tmdb_producer",
    "tmdb_producer_details",
    "tmdb_show",
    "tmdb_show_details",
    "tmdb_top_rated",
    "tmdb_trending_daily",
    "tmdb_trending_weekly",
    "tmdb_writer",
    "tmdb_writer_details"
]
tmdb_type = {
    "tmdb_actor": "Person",
    "tmdb_actor_details": "Person",
    "tmdb_collection": "Collection",
    "tmdb_collection_details": "Collection",
    "tmdb_company": "Company",
    "tmdb_crew": "Person",
    "tmdb_crew_details": "Person",
    "tmdb_director": "Person",
    "tmdb_director_details": "Person",
    "tmdb_keyword": "Keyword",
    "tmdb_list": "List",
    "tmdb_list_details": "List",
    "tmdb_movie": "Movie",
    "tmdb_movie_details": "Movie",
    "tmdb_network": "Network",
    "tmdb_person": "Person",
    "tmdb_producer": "Person",
    "tmdb_producer_details": "Person",
    "tmdb_show": "Show",
    "tmdb_show_details": "Show",
    "tmdb_writer": "Person",
    "tmdb_writer_details": "Person"
}
plex_searches = [
    "title", "title.and", "title.not", "title.begins", "title.ends",
    "studio", "studio.and", "studio.not", "studio.begins", "studio.ends",
    "actor", "actor.and", "actor.not",
    "audio_language", "audio_language.and", "audio_language.not",
    "collection", "collection.and", "collection.not",
    "content_rating", "content_rating.and", "content_rating.not",
    "country", "country.and", "country.not",
    "director", "director.and", "director.not",
    "genre", "genre.and", "genre.not",
    "label", "label.and", "label.not",
    "producer", "producer.and", "producer.not",
    "subtitle_language", "subtitle_language.and", "subtitle_language.not",
    "writer", "writer.and", "writer.not",
    "decade", "resolution",
    "added.before", "added.after",
    "originally_available.before", "originally_available.after",
    "duration.greater", "duration.less",
    "rating.greater", "rating.less",
    "year", "year.not", "year.greater", "year.less"
]
plex_sort = {
    "title.asc": "titleSort:asc", "title.desc": "titleSort:desc",
    "originally_available.asc": "originallyAvailableAt:asc", "originally_available.desc": "originallyAvailableAt:desc",
    "critic_rating.asc": "rating:asc", "critic_rating.desc": "rating:desc",
    "audience_rating.asc": "audienceRating:asc", "audience_rating.desc": "audienceRating:desc",
    "duration.asc": "duration:asc", "duration.desc": "duration:desc",
    "added.asc": "addedAt:asc", "added.desc": "addedAt:desc"
}
plex_modifiers = {
    ".and": "&",
    ".not": "!",
    ".begins": "<",
    ".ends": ">",
    ".before": "<<",
    ".after": ">>",
    ".greater": ">>",
    ".less": "<<"
}
movie_only_searches = [
    "audio_language", "audio_language.and", "audio_language.not",
    "country", "country.and", "country.not",
    "subtitle_language", "subtitle_language.and", "subtitle_language.not",
    "decade", "resolution",
    "originally_available.before", "originally_available.after",
    "duration.greater", "duration.less"
]
tmdb_searches = [
    "actor", "actor.and", "actor.not",
    "director", "director.and", "director.not",
    "producer", "producer.and", "producer.not",
    "writer", "writer.and", "writer.not"
]
all_filters = [
    "actor", "actor.not",
    "audio_language", "audio_language.not",
    "audio_track_title", "audio_track_title.not",
    "collection", "collection.not",
    "content_rating", "content_rating.not",
    "country", "country.not",
    "director", "director.not",
    "genre", "genre.not",
    "max_age",
    "originally_available.gte", "originally_available.lte",
    "tmdb_vote_count.gte", "tmdb_vote_count.lte",
    "duration.gte", "duration.lte",
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
    "audio_track_title", "audio_track_title.not",
    "country", "country.not",
    "director", "director.not",
    "duration.gte", "duration.lte",
    "original_language", "original_language.not",
    "subtitle_language", "subtitle_language.not",
    "video_resolution", "video_resolution.not",
    "writer", "writer.not"
]
boolean_details = [
    "add_to_arr",
    "show_filtered",
    "show_missing",
    "save_missing"
]
all_details = [
    "sort_title", "content_rating",
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography", "tvdb_summary", "tvdb_description", "trakt_description", "letterboxd_description",
    "collection_mode", "collection_order",
    "url_poster", "tmdb_poster", "tmdb_profile", "tvdb_poster", "file_poster",
    "url_background", "tmdb_background", "tvdb_background", "file_background",
    "name_mapping", "add_to_arr", "arr_tag", "label",
    "show_filtered", "show_missing", "save_missing"
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
discover_dates = [
    "primary_release_date.gte", "primary_release_date.lte",
    "release_date.gte", "release_date.lte",
    "air_date.gte", "air_date.lte",
    "first_air_date.gte", "first_air_date.lte"
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

def get_list(data, lower=False, split=True):
    if isinstance(data, list):      return data
    elif isinstance(data, dict):    return [data]
    elif split is False:            return [str(data)]
    elif lower is True:             return [d.strip().lower() for d in str(data).split(",")]
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
    try:                                    date_obg = datetime.strptime(str(date_text), "%Y/%m/%d" if plex_date else "%m/%d/%Y")
    except ValueError:                      raise Failed(f"Collection Error: {method}: {date_text} must match pattern {'YYYY/MM/DD e.g. 2020/12/25' if plex_date else 'MM/DD/YYYY e.g. 12/25/2020'}")
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

def remove_not(method):
    return method[:-4] if method.endswith(".not") else method

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
