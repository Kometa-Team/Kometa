import glob, logging, os, re
from datetime import datetime, timedelta
from modules import anidb, anilist, imdb, letterboxd, mal, plex, radarr, sonarr, tautulli, tmdb, trakttv, tvdb, util
from modules.util import Failed
from plexapi.collection import Collections
from plexapi.exceptions import BadRequest, NotFound

logger = logging.getLogger("Plex Meta Manager")

image_file_details = ["file_poster", "file_background", "asset_directory"]
method_alias = {
    "actors": "actor", "role": "actor", "roles": "actor",
    "content_ratings": "content_rating", "contentRating": "content_rating", "contentRatings": "content_rating",
    "countries": "country",
    "decades": "decade",
    "directors": "director",
    "genres": "genre",
    "labels": "label",
    "rating": "critic_rating",
    "studios": "studio",
    "networks": "network",
    "producers": "producer",
    "writers": "writer",
    "years": "year"
}
all_builders = anidb.builders + anilist.builders + imdb.builders + letterboxd.builders + mal.builders + plex.builders + tautulli.builders + tmdb.builders + trakttv.builders + tvdb.builders
dictionary_builders = [
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
show_only_builders = [
    "tmdb_network",
    "tmdb_show",
    "tmdb_show_details",
    "tvdb_show",
    "tvdb_show_details"
]
movie_only_builders = [
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
numbered_builders = [
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
all_details = [
    "sort_title", "content_rating", "collection_mode", "collection_order",
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography", "tvdb_summary",
    "tvdb_description", "trakt_description", "letterboxd_description",
    "url_poster", "tmdb_poster", "tmdb_profile", "tvdb_poster", "file_poster",
    "url_background", "tmdb_background", "tvdb_background", "file_background",
    "name_mapping", "label", "show_filtered", "show_missing", "save_missing"
]
collectionless_details = [
    "sort_title", "content_rating",
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography",
    "collection_order", "plex_collectionless",
    "url_poster", "tmdb_poster", "tmdb_profile", "file_poster",
    "url_background", "file_background",
    "name_mapping", "label", "label_sync_mode", "test"
]
ignored_details = [
    "run_again",
    "schedule",
    "sync_mode",
    "template",
    "test",
    "tmdb_person"
]
boolean_details = [
    "show_filtered",
    "show_missing",
    "save_missing"
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
    "user_rating.gte", "user_rating.lte",
    "audience_rating.gte", "audience_rating.lte",
    "critic_rating.gte", "critic_rating.lte",
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

class CollectionBuilder:
    def __init__(self, config, library, name, data):
        self.config = config
        self.library = library
        self.name = name
        self.data = data
        self.details = {
            "show_filtered": library.show_filtered,
            "show_missing": library.show_missing,
            "save_missing": library.save_missing
        }
        self.radarr_options = {}
        self.sonarr_options = {}
        self.missing_movies = []
        self.missing_shows = []
        self.methods = []
        self.filters = []
        self.posters = {}
        self.backgrounds = {}
        self.summaries = {}
        self.schedule = ""
        self.rating_key_map = {}
        self.add_to_radarr = None
        self.add_to_sonarr = None
        current_time = datetime.now()
        current_year = current_time.year

        methods = {m.lower(): m for m in self.data}

        if "template" in methods:
            if not self.library.templates:
                raise Failed("Collection Error: No templates found")
            elif not self.data[methods["template"]]:
                raise Failed("Collection Error: template attribute is blank")
            else:
                for data_template in util.get_list(self.data[methods["template"]], split=False):
                    if not isinstance(data_template, dict):
                        raise Failed("Collection Error: template attribute is not a dictionary")
                    elif "name" not in data_template:
                        raise Failed("Collection Error: template sub-attribute name is required")
                    elif not data_template["name"]:
                        raise Failed("Collection Error: template sub-attribute name is blank")
                    elif data_template["name"] not in self.library.templates:
                        raise Failed(f"Collection Error: template {data_template['name']} not found")
                    elif not isinstance(self.library.templates[data_template["name"]], dict):
                        raise Failed(f"Collection Error: template {data_template['name']} is not a dictionary")
                    else:
                        for tm in data_template:
                            if not data_template[tm]:
                                raise Failed(f"Collection Error: template sub-attribute {tm} is blank")

                        template_name = data_template["name"]
                        template = self.library.templates[template_name]

                        default = {}
                        if "default" in template:
                            if template["default"]:
                                if isinstance(template["default"], dict):
                                    for dv in template["default"]:
                                        if template["default"][dv]:
                                            default[dv] = template["default"][dv]
                                        else:
                                            raise Failed(f"Collection Error: template default sub-attribute {dv} is blank")
                                else:
                                    raise Failed("Collection Error: template sub-attribute default is not a dictionary")
                            else:
                                raise Failed("Collection Error: template sub-attribute default is blank")

                        optional = []
                        if "optional" in template:
                            if template["optional"]:
                                if isinstance(template["optional"], list):
                                    for op in template["optional"]:
                                        if op not in default:
                                            optional.append(op)
                                        else:
                                            logger.warning(f"Template Warning: variable {op} cannot be optional if it has a default")
                                else:
                                    optional.append(str(template["optional"]))
                            else:
                                raise Failed("Collection Error: template sub-attribute optional is blank")

                        for method_name, attr_data in template.items():
                            if method_name not in self.data and method_name not in ["default", "optional"]:
                                if attr_data:
                                    def replace_txt(txt):
                                        txt = str(txt)
                                        for option in optional:
                                            if option not in data_template and f"<<{option}>>" in txt:
                                                raise Failed("remove attribute")
                                        for template_method in data_template:
                                            if template_method != "name" and txt == f"<<{template_method}>>":
                                                return data_template[template_method]
                                            elif template_method != "name" and f"<<{template_method}>>" in txt:
                                                txt = txt.replace(f"<<{template_method}>>", str(data_template[template_method]))
                                        if "<<collection_name>>" in txt:
                                            txt = txt.replace("<<collection_name>>", str(self.name))
                                        for dm in default:
                                            if txt == f"<<{dm}>>":
                                                txt = default[dm]
                                            elif f"<<{dm}>>" in txt:
                                                txt = txt.replace(f"<<{dm}>>", str(default[dm]))
                                        if txt in ["true", "True"]:                     return True
                                        elif txt in ["false", "False"]:                 return False
                                        else:
                                            try:                                            return int(txt)
                                            except (ValueError, TypeError):                 return txt
                                    try:
                                        if isinstance(attr_data, dict):
                                            final_data = {}
                                            for sm in attr_data:
                                                if isinstance(attr_data[sm], list):
                                                    temp_list = []
                                                    for li in attr_data[sm]:
                                                        temp_list.append(replace_txt(li))
                                                    final_data[sm] = temp_list
                                                else:
                                                    final_data[sm] = replace_txt(attr_data[sm])
                                        elif isinstance(attr_data, list):
                                            final_data = []
                                            for li in attr_data:
                                                if isinstance(li, dict):
                                                    temp_dict = {}
                                                    for sm in li:
                                                        temp_dict[sm] = replace_txt(li[sm])
                                                    final_data.append(temp_dict)
                                                else:
                                                    final_data.append(replace_txt(li))
                                        else:
                                            final_data = replace_txt(attr_data)
                                    except Failed:
                                        continue
                                    self.data[method_name] = final_data
                                    methods[method_name.lower()] = method_name
                                else:
                                    raise Failed(f"Collection Error: template attribute {method_name} is blank")

        skip_collection = True
        if "schedule" not in methods:
            skip_collection = False
        elif not self.data[methods["schedule"]]:
            logger.error("Collection Error: schedule attribute is blank. Running daily")
            skip_collection = False
        else:
            schedule_list = util.get_list(self.data[methods["schedule"]])
            next_month = current_time.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            for schedule in schedule_list:
                run_time = str(schedule).lower()
                if run_time.startswith("day") or run_time.startswith("daily"):
                    skip_collection = False
                elif run_time.startswith("week") or run_time.startswith("month") or run_time.startswith("year"):
                    match = re.search("\\(([^)]+)\\)", run_time)
                    if match:
                        param = match.group(1)
                        if run_time.startswith("week"):
                            if param.lower() in util.days_alias:
                                weekday = util.days_alias[param.lower()]
                                self.schedule += f"\nScheduled weekly on {util.pretty_days[weekday]}"
                                if weekday == current_time.weekday():
                                    skip_collection = False
                            else:
                                logger.error(f"Collection Error: weekly schedule attribute {schedule} invalid must be a day of the week i.e. weekly(Monday)")
                        elif run_time.startswith("month"):
                            try:
                                if 1 <= int(param) <= 31:
                                    self.schedule += f"\nScheduled monthly on the {util.make_ordinal(param)}"
                                    if current_time.day == int(param) or (current_time.day == last_day.day and int(param) > last_day.day):
                                        skip_collection = False
                                else:
                                    logger.error(f"Collection Error: monthly schedule attribute {schedule} invalid must be between 1 and 31")
                            except ValueError:
                                logger.error(f"Collection Error: monthly schedule attribute {schedule} invalid must be an integer")
                        elif run_time.startswith("year"):
                            match = re.match("^(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])$", param)
                            if match:
                                month = int(match.group(1))
                                day = int(match.group(2))
                                self.schedule += f"\nScheduled yearly on {util.pretty_months[month]} {util.make_ordinal(day)}"
                                if current_time.month == month and (current_time.day == day or (current_time.day == last_day.day and day > last_day.day)):
                                    skip_collection = False
                            else:
                                logger.error(f"Collection Error: yearly schedule attribute {schedule} invalid must be in the MM/DD format i.e. yearly(11/22)")
                    else:
                        logger.error(f"Collection Error: failed to parse schedule: {schedule}")
                else:
                    logger.error(f"Collection Error: schedule attribute {schedule} invalid")
        if len(self.schedule) == 0:
            skip_collection = False
        if skip_collection:
            raise Failed(f"{self.schedule}\n\nCollection {self.name} not scheduled to run")

        logger.info(f"Scanning {self.name} Collection")

        self.collectionless = "plex_collectionless" in methods
        self.run_again = "run_again" in methods

        if "tmdb_person" in methods:
            if self.data[methods["tmdb_person"]]:
                valid_names = []
                for tmdb_id in util.get_int_list(self.data[methods["tmdb_person"]], "TMDb Person ID"):
                    person = config.TMDb.get_person(tmdb_id)
                    valid_names.append(person.name)
                    if hasattr(person, "biography") and person.biography:
                        self.summaries["tmdb_person"] = person.biography
                    if hasattr(person, "profile_path") and person.profile_path:
                        self.posters["tmdb_person"] = f"{config.TMDb.image_url}{person.profile_path}"
                if len(valid_names) > 0:                                        self.details["tmdb_person"] = valid_names
                else:                                                           raise Failed(f"Collection Error: No valid TMDb Person IDs in {self.data[methods['tmdb_person']]}")
            else:
                raise Failed("Collection Error: tmdb_person attribute is blank")

        for method_key, method_data in self.data.items():
            if "trakt" in method_key.lower() and not config.Trakt:                      raise Failed(f"Collection Error: {method_key} requires Trakt todo be configured")
            elif "imdb" in method_key.lower() and not config.IMDb:                      raise Failed(f"Collection Error: {method_key} requires TMDb or Trakt to be configured")
            elif "radarr" in method_key.lower() and not self.library.Radarr:            raise Failed(f"Collection Error: {method_key} requires Radarr to be configured")
            elif "sonarr" in method_key.lower() and not self.library.Sonarr:            raise Failed(f"Collection Error: {method_key} requires Sonarr to be configured")
            elif "tautulli" in method_key.lower() and not self.library.Tautulli:        raise Failed(f"Collection Error: {method_key} requires Tautulli to be configured")
            elif "mal" in method_key.lower() and not config.MyAnimeList:                raise Failed(f"Collection Error: {method_key} requires MyAnimeList to be configured")
            elif method_data is not None:
                logger.debug("")
                logger.debug(f"Validating Method: {method_key}")
                logger.debug(f"Value: {method_data}")
                if method_key.lower() in method_alias:
                    method_name = method_alias[method_key.lower()]
                    logger.warning(f"Collection Warning: {method_key} attribute will run as {method_name}")
                elif method_key.lower() == "add_to_arr":
                    method_name = "radarr_add" if self.library.is_movie else "sonarr_add"
                    logger.warning(f"Collection Warning: {method_key} attribute will run as {method_name}")
                elif method_key.lower() in ["arr_tag", "arr_folder"]:
                    method_name = f"{'rad' if self.library.is_movie else 'son'}{method_key.lower()}"
                    logger.warning(f"Collection Warning: {method_key} attribute will run as {method_name}")
                else:
                    method_name = method_key.lower()
                if method_name in show_only_builders and self.library.is_movie:
                    raise Failed(f"Collection Error: {method_name} attribute only works for show libraries")
                elif method_name in movie_only_builders and self.library.is_show:
                    raise Failed(f"Collection Error: {method_name} attribute only works for movie libraries")
                elif method_name in plex.movie_only_searches and self.library.is_show:
                    raise Failed(f"Collection Error: {method_name} plex search only works for movie libraries")
                elif method_name in plex.show_only_searches and self.library.is_movie:
                    raise Failed(f"Collection Error: {method_name} plex search only works for show libraries")
                elif method_name not in collectionless_details and self.collectionless:
                    raise Failed(f"Collection Error: {method_name} attribute does not work for Collectionless collection")
                elif method_name == "summary":
                    self.summaries[method_name] = method_data
                elif method_name == "tmdb_summary":
                    self.summaries[method_name] = config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, "TMDb ID"), self.library.is_movie).overview
                elif method_name == "tmdb_description":
                    self.summaries[method_name] = config.TMDb.get_list(util.regex_first_int(method_data, "TMDb List ID")).description
                elif method_name == "tmdb_biography":
                    self.summaries[method_name] = config.TMDb.get_person(util.regex_first_int(method_data, "TMDb Person ID")).biography
                elif method_name == "tvdb_summary":
                    self.summaries[method_name] = config.TVDb.get_movie_or_show(method_data, self.library.Plex.language, self.library.is_movie).summary
                elif method_name == "tvdb_description":
                    self.summaries[method_name] = config.TVDb.get_list_description(method_data, self.library.Plex.language)
                elif method_name == "trakt_description":
                    self.summaries[method_name] = config.Trakt.standard_list(config.Trakt.validate_trakt(util.get_list(method_data))[0]).description
                elif method_name == "letterboxd_description":
                    self.summaries[method_name] = config.Letterboxd.get_list_description(method_data, self.library.Plex.language)
                elif method_name == "collection_mode":
                    if str(method_data).lower() == "default":
                        self.details[method_name] = "default"
                    elif str(method_data).lower() == "hide":
                        self.details[method_name] = "hide"
                    elif str(method_data).lower() in ["hide_items", "hideitems"]:
                        self.details[method_name] = "hideItems"
                    elif str(method_data).lower() in ["show_items", "showitems"]:
                        self.details[method_name] = "showItems"
                    else:
                        raise Failed(f"Collection Error: {method_data} collection_mode invalid\n\tdefault (Library default)\n\thide (Hide Collection)\n\thide_items (Hide Items in this Collection)\n\tshow_items (Show this Collection and its Items)")
                elif method_name == "collection_order":
                    if str(method_data).lower() == "release":
                        self.details[method_name] = "release"
                    elif str(method_data).lower() == "alpha":
                        self.details[method_name] = "alpha"
                    else:
                        raise Failed(f"Collection Error: {method_data} collection_order invalid\n\trelease (Order Collection by release dates)\n\talpha (Order Collection Alphabetically)")
                elif method_name == "url_poster":
                    self.posters[method_name] = method_data
                elif method_name == "tmdb_poster":
                    self.posters[method_name] = f"{config.TMDb.image_url}{config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, 'TMDb ID'), self.library.is_movie).poster_path}"
                elif method_name == "tmdb_profile":
                    self.posters[method_name] = f"{config.TMDb.image_url}{config.TMDb.get_person(util.regex_first_int(method_data, 'TMDb Person ID')).profile_path}"
                elif method_name == "tvdb_poster":
                    self.posters[method_name] = f"{config.TVDb.get_movie_or_series(method_data, self.library.Plex.language, self.library.is_movie).poster_path}"
                elif method_name == "file_poster":
                    if os.path.exists(method_data):
                        self.posters[method_name] = os.path.abspath(method_data)
                    else:
                        raise Failed(f"Collection Error: Poster Path Does Not Exist: {os.path.abspath(method_data)}")
                elif method_name == "url_background":
                    self.backgrounds[method_name] = method_data
                elif method_name == "tmdb_background":
                    self.backgrounds[method_name] = f"{config.TMDb.image_url}{config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, 'TMDb ID'), self.library.is_movie).poster_path}"
                elif method_name == "tvdb_background":
                    self.posters[method_name] = f"{config.TVDb.get_movie_or_series(method_data, self.library.Plex.language, self.library.is_movie).background_path}"
                elif method_name == "file_background":
                    if os.path.exists(method_data):                             self.backgrounds[method_name] = os.path.abspath(method_data)
                    else:                                                       raise Failed(f"Collection Error: Background Path Does Not Exist: {os.path.abspath(method_data)}")
                elif method_name == "label_sync_mode":
                    if str(method_data).lower() in ["append", "sync"]:          self.details[method_name] = method_data.lower()
                    else:                                                       raise Failed("Collection Error: label_sync_mode attribute must be either 'append' or 'sync'")
                elif method_name == "sync_mode":
                    if str(method_data).lower() in ["append", "sync"]:          self.details[method_name] = method_data.lower()
                    else:                                                       raise Failed("Collection Error: sync_mode attribute must be either 'append' or 'sync'")
                elif method_name == "label":
                    self.details[method_name] = util.get_list(method_data)
                elif method_name in boolean_details:
                    if isinstance(method_data, bool):                           self.details[method_name] = method_data
                    elif str(method_data).lower() in ["t", "true"]:             self.details[method_name] = True
                    elif str(method_data).lower() in ["f", "false"]:            self.details[method_name] = False
                    else:                                                       raise Failed(f"Collection Error: {method_name} attribute must be either true or false")
                elif method_name in all_details:
                    self.details[method_name] = method_data
                elif method_name == "radarr_add":
                    if isinstance(method_data, bool):                           self.add_to_radarr = method_data
                    elif str(method_data).lower() in ["t", "true"]:             self.add_to_radarr = True
                    elif str(method_data).lower() in ["f", "false"]:            self.add_to_radarr = False
                    else:                                                       raise Failed(f"Collection Error: {method_name} attribute must be either true or false")
                elif method_name == "radarr_folder":
                    self.radarr_options["folder"] = method_data
                elif method_name in ["radarr_monitor", "radarr_search"]:
                    if isinstance(method_data, bool):                           self.radarr_options[method_name[7:]] = method_data
                    elif str(method_data).lower() in ["t", "true"]:             self.radarr_options[method_name[7:]] = True
                    elif str(method_data).lower() in ["f", "false"]:            self.radarr_options[method_name[7:]] = False
                    else:                                                       raise Failed(f"Collection Error: {method_name} attribute must be either true or false")
                elif method_name == "radarr_availability":
                    if str(method_data).lower() in radarr.availability_translation:
                        self.radarr_options["availability"] = str(method_data).lower()
                    else:
                        raise Failed(f"Collection Error: {method_name} attribute must be either announced, cinemas, released or db")
                elif method_name == "radarr_quality":
                    self.library.Radarr.get_profile_id(method_data)
                    self.radarr_options["quality"] = method_data
                elif method_name == "radarr_tag":
                    self.radarr_options["tag"] = util.get_list(method_data)
                elif method_name == "sonarr_add":
                    if isinstance(method_data, bool):                           self.add_to_sonarr = method_data
                    elif str(method_data).lower() in ["t", "true"]:             self.add_to_sonarr = True
                    elif str(method_data).lower() in ["f", "false"]:            self.add_to_sonarr = False
                    else:                                                       raise Failed(f"Collection Error: {method_name} attribute must be either true or false")
                elif method_name == "sonarr_folder":
                    self.sonarr_options["folder"] = method_data
                elif method_name == "sonarr_monitor":
                    if str(method_data).lower() in sonarr.monitor_translation:
                        self.sonarr_options["monitor"] = str(method_data).lower()
                    else:
                        raise Failed(f"Collection Error: {method_name} attribute must be either all, future, missing, existing, pilot, first, latest or none")
                elif method_name == "sonarr_quality":
                    self.library.Sonarr.get_profile_id(method_data, "quality_profile")
                    self.sonarr_options["quality"] = method_data
                elif method_name == "sonarr_language":
                    self.library.Sonarr.get_profile_id(method_data, "language_profile")
                    self.sonarr_options["language"] = method_data
                elif method_name == "sonarr_series":
                    if str(method_data).lower() in sonarr.series_type:
                        self.sonarr_options["series"] = str(method_data).lower()
                    else:
                        raise Failed(f"Collection Error: {method_name} attribute must be either standard, daily, or anime")
                elif method_name in ["sonarr_season", "sonarr_search", "sonarr_cutoff_search"]:
                    if isinstance(method_data, bool):                           self.sonarr_options[method_name[7:]] = method_data
                    elif str(method_data).lower() in ["t", "true"]:             self.sonarr_options[method_name[7:]] = True
                    elif str(method_data).lower() in ["f", "false"]:            self.sonarr_options[method_name[7:]] = False
                    else:                                                       raise Failed(f"Collection Error: {method_name} attribute must be either true or false")
                elif method_name == "sonarr_tag":
                    self.sonarr_options["tag"] = util.get_list(method_data)
                elif method_name in ["title", "title.and", "title.not", "title.begins", "title.ends"]:
                    self.methods.append(("plex_search", [{method_name: util.get_list(method_data, split=False)}]))
                elif method_name in ["year.greater", "year.less"]:
                    self.methods.append(("plex_search", [{method_name: util.check_year(method_data, current_year, method_name)}]))
                elif method_name in ["added.before", "added.after", "originally_available.before", "originally_available.after"]:
                    self.methods.append(("plex_search", [{method_name: util.check_date(method_data, method_name, return_string=True, plex_date=True)}]))
                elif method_name in ["added", "added.not", "originally_available", "originally_available.not", "duration.greater", "duration.less"]:
                    self.methods.append(("plex_search", [{method_name: util.check_number(method_data, method_name, minimum=1)}]))
                elif method_name in ["user_rating.greater", "user_rating.less", "critic_rating.greater", "critic_rating.less", "audience_rating.greater", "audience_rating.less"]:
                    self.methods.append(("plex_search", [{method_name: util.check_number(method_data, method_name, number_type="float", minimum=0, maximum=10)}]))
                elif method_name in ["decade", "year", "year.not"]:
                    self.methods.append(("plex_search", [{method_name: util.get_year_list(method_data, current_year, method_name)}]))
                elif method_name in plex.searches:
                    if method_name in plex.tmdb_searches:
                        final_values = []
                        for value in util.get_list(method_data):
                            if value.lower() == "tmdb" and "tmdb_person" in self.details:
                                for name in self.details["tmdb_person"]:
                                    final_values.append(name)
                            else:
                                final_values.append(value)
                    else:
                        final_values = method_data
                    search = os.path.splitext(method_name)[0]
                    valid_values = self.library.validate_search_list(final_values, search)
                    if valid_values:
                        self.methods.append(("plex_search", [{method_name: valid_values}]))
                    else:
                        logger.warning(f"Collection Warning: No valid {search} values found in {final_values}")
                elif method_name == "plex_all":
                    self.methods.append((method_name, [""]))
                elif method_name == "plex_collection":
                    self.methods.append((method_name, self.library.validate_collections(method_data if isinstance(method_data, list) else [method_data])))
                elif method_name == "anidb_popular":
                    list_count = util.regex_first_int(method_data, "List Size", default=40)
                    if 1 <= list_count <= 30:
                        self.methods.append((method_name, [list_count]))
                    else:
                        logger.warning("Collection Error: anidb_popular must be an integer between 1 and 30 defaulting to 30")
                        self.methods.append((method_name, [30]))
                elif method_name == "mal_id":
                    self.methods.append((method_name, util.get_int_list(method_data, "MyAnimeList ID")))
                elif method_name in ["anidb_id", "anidb_relation"]:
                    self.methods.append((method_name, config.AniDB.validate_anidb_list(util.get_int_list(method_data, "AniDB ID"), self.library.Plex.language)))
                elif method_name in ["anilist_id", "anilist_relations", "anilist_studio"]:
                    self.methods.append((method_name, config.AniList.validate_anilist_ids(util.get_int_list(method_data, "AniList ID"), studio=method_name == "anilist_studio")))
                elif method_name == "trakt_list":
                    self.methods.append((method_name, config.Trakt.validate_trakt(util.get_list(method_data))))
                elif method_name == "trakt_list_details":
                    valid_list = config.Trakt.validate_trakt(util.get_list(method_data))
                    item = config.Trakt.standard_list(valid_list[0])
                    if hasattr(item, "description") and item.description:
                        self.summaries[method_name] = item.description
                    self.methods.append((method_name[:-8], valid_list))
                elif method_name in ["trakt_watchlist", "trakt_collection"]:
                    self.methods.append((method_name, config.Trakt.validate_trakt(util.get_list(method_data), trakt_type=method_name[6:], is_movie=self.library.is_movie)))
                elif method_name == "imdb_list":
                    new_list = []
                    for imdb_list in util.get_list(method_data, split=False):
                        if isinstance(imdb_list, dict):
                            dict_methods = {dm.lower(): dm for dm in imdb_list}
                            if "url" in dict_methods and imdb_list[dict_methods["url"]]:
                                imdb_url = config.IMDb.validate_imdb_url(imdb_list[dict_methods["url"]])
                            else:
                                raise Failed("Collection Error: imdb_list attribute url is required")
                            if "limit" in dict_methods and imdb_list[dict_methods["limit"]]:
                                list_count = util.regex_first_int(imdb_list[dict_methods["limit"]], "List Limit", default=0)
                            else:
                                list_count = 0
                        else:
                            imdb_url = config.IMDb.validate_imdb_url(str(imdb_list))
                            list_count = 0
                        new_list.append({"url": imdb_url, "limit": list_count})
                    self.methods.append((method_name, new_list))
                elif method_name == "letterboxd_list":
                    self.methods.append((method_name, util.get_list(method_data, split=False)))
                elif method_name == "letterboxd_list_details":
                    values = util.get_list(method_data, split=False)
                    self.summaries[method_name] = config.Letterboxd.get_list_description(values[0], self.library.Plex.language)
                    self.methods.append((method_name[:-8], values))
                elif method_name in dictionary_builders:
                    if isinstance(method_data, dict):
                        def get_int(parent, method, data_in, methods_in, default_in, minimum=1, maximum=None):
                            if method not in methods_in:
                                logger.warning(f"Collection Warning: {parent} {method} attribute not found using {default_in} as default")
                            elif not data_in[methods_in[method]]:
                                logger.warning(f"Collection Warning: {parent} {methods_in[method]} attribute is blank using {default_in} as default")
                            elif isinstance(data_in[methods_in[method]], int) and data_in[methods_in[method]] >= minimum:
                                if maximum is None or data_in[methods_in[method]] <= maximum:
                                    return data_in[methods_in[method]]
                                else:
                                    logger.warning(f"Collection Warning: {parent} {methods_in[method]} attribute {data_in[methods_in[method]]} invalid must an integer <= {maximum} using {default_in} as default")
                            else:
                                logger.warning(f"Collection Warning: {parent} {methods_in[method]} attribute {data_in[methods_in[method]]} invalid must an integer >= {minimum} using {default_in} as default")
                            return default_in
                        if method_name == "filters":
                            for filter_name, filter_data in method_data.items():
                                modifier = filter_name[-4:].lower()
                                modifier = modifier if modifier in [".not", ".lte", ".gte"] else ""
                                method = filter_name[:-4].lower() if modifier in [".not", ".lte", ".gte"] else filter_name.lower()
                                if method in method_alias:
                                    filter_method = f"{method_alias[method]}{modifier}"
                                    logger.warning(f"Collection Warning: {filter_name} filter will run as {filter_method}")
                                else:
                                    filter_method = f"{method}{modifier}"
                                if filter_method in movie_only_filters and self.library.is_show:
                                    raise Failed(f"Collection Error: {filter_method} filter only works for movie libraries")
                                elif filter_data is None:
                                    raise Failed(f"Collection Error: {filter_method} filter is blank")
                                elif filter_method == "year":
                                    valid_data = util.get_year_list(filter_data, current_year, f"{filter_method} filter")
                                elif filter_method in ["max_age", "duration.gte", "duration.lte", "tmdb_vote_count.gte", "tmdb_vote_count.lte"]:
                                    valid_data = util.check_number(filter_data, f"{filter_method} filter", minimum=1)
                                elif filter_method in ["year.gte", "year.lte"]:
                                    valid_data = util.check_year(filter_data, current_year, f"{filter_method} filter")
                                elif filter_method in ["user_rating.gte", "user_rating.lte", "audience_rating.gte", "audience_rating.lte", "critic_rating.gte", "critic_rating.lte"]:
                                    valid_data = util.check_number(filter_data, f"{filter_method} filter", number_type="float", minimum=0.1, maximum=10)
                                elif filter_method in ["originally_available.gte", "originally_available.lte"]:
                                    valid_data = util.check_date(filter_data, f"{filter_method} filter")
                                elif filter_method == "original_language":
                                    valid_data = util.get_list(filter_data, lower=True)
                                elif filter_method == "collection":
                                    valid_data = filter_data if isinstance(filter_data, list) else [filter_data]
                                elif filter_method in all_filters:
                                    valid_data = util.get_list(filter_data)
                                else:
                                    raise Failed(f"Collection Error: {filter_method} filter not supported")
                                self.filters.append((filter_method, valid_data))
                        elif method_name == "plex_collectionless":
                            new_dictionary = {}
                            dict_methods = {dm.lower(): dm for dm in method_data}
                            prefix_list = []
                            if "exclude_prefix" in dict_methods and method_data[dict_methods["exclude_prefix"]]:
                                if isinstance(method_data[dict_methods["exclude_prefix"]], list):
                                    prefix_list.extend([exclude for exclude in method_data[dict_methods["exclude_prefix"]] if exclude])
                                else:
                                    prefix_list.append(str(method_data[dict_methods["exclude_prefix"]]))
                            exact_list = []
                            if "exclude" in dict_methods and method_data[dict_methods["exclude"]]:
                                if isinstance(method_data[dict_methods["exclude"]], list):
                                    exact_list.extend([exclude for exclude in method_data[dict_methods["exclude"]] if exclude])
                                else:
                                    exact_list.append(str(method_data[dict_methods["exclude"]]))
                            if len(prefix_list) == 0 and len(exact_list) == 0:
                                raise Failed("Collection Error: you must have at least one exclusion")
                            new_dictionary["exclude_prefix"] = prefix_list
                            new_dictionary["exclude"] = exact_list
                            self.methods.append((method_name, [new_dictionary]))
                        elif method_name == "plex_search":
                            searches = {}
                            for search_name, search_data in method_data.items():
                                search, modifier = os.path.splitext(str(search_name).lower())
                                if search in method_alias:
                                    search = method_alias[search]
                                    logger.warning(f"Collection Warning: {str(search_name).lower()} plex search attribute will run as {search}{modifier if modifier else ''}")
                                search_final = f"{search}{modifier}"
                                if search_final in plex.movie_only_searches and self.library.is_show:
                                    raise Failed(f"Collection Error: {search_final} plex search attribute only works for movie libraries")
                                if search_final in plex.show_only_searches and self.library.is_movie:
                                    raise Failed(f"Collection Error: {search_final} plex search attribute only works for show libraries")
                                elif search_data is None:
                                    raise Failed(f"Collection Error: {search_final} plex search attribute is blank")
                                elif search == "sort_by":
                                    if str(search_data).lower() in plex.sorts:
                                        searches[search] = str(search_data).lower()
                                    else:
                                        logger.warning(f"Collection Error: {search_data} is not a valid plex search sort defaulting to title.asc")
                                elif search == "limit":
                                    if not search_data:
                                        raise Failed(f"Collection Warning: plex search limit attribute is blank")
                                    elif not isinstance(search_data, int) and search_data > 0:
                                        raise Failed(f"Collection Warning: plex search limit attribute: {search_data} must be an integer greater then 0")
                                    else:
                                        searches[search] = search_data
                                elif search == "title" and modifier in ["", ".and", ".not", ".begins", ".ends"]:
                                    searches[search_final] = util.get_list(search_data, split=False)
                                elif (search == "studio" and modifier in ["", ".and", ".not", ".begins", ".ends"]) \
                                        or (search in ["actor", "audio_language", "collection", "content_rating", "country", "director", "genre", "label", "network", "producer", "subtitle_language", "writer"] and modifier in ["", ".and", ".not"]) \
                                        or (search == "resolution" and modifier in [""]):
                                    if search_final in plex.tmdb_searches:
                                        final_values = []
                                        for value in util.get_list(search_data):
                                            if value.lower() == "tmdb" and "tmdb_person" in self.details:
                                                for name in self.details["tmdb_person"]:
                                                    final_values.append(name)
                                            else:
                                                final_values.append(value)
                                    else:
                                        final_values = search_data
                                    valid_values = self.library.validate_search_list(final_values, search)
                                    if valid_values:
                                        searches[search_final] = valid_values
                                    else:
                                        logger.warning(f"Collection Warning: No valid {search} values found in {final_values}")
                                elif search == "year" and modifier in [".greater", ".less"]:
                                    searches[search_final] = util.check_year(search_data, current_year, search_final)
                                elif search in ["added", "originally_available"] and modifier in [".before", ".after"]:
                                    searches[search_final] = util.check_date(search_data, search_final, return_string=True, plex_date=True)
                                elif (search in ["added", "originally_available"] and modifier in ["", ".not"]) or (search in ["duration"] and modifier in [".greater", ".less"]):
                                    searches[search_final] = util.check_number(search_data, search_final, minimum=1)
                                elif search in ["user_rating", "critic_rating", "audience_rating"] and modifier in [".greater", ".less"]:
                                    searches[search_final] = util.check_number(search_data, search_final, number_type="float", minimum=0, maximum=10)
                                elif (search == "decade" and modifier in [""]) or (search == "year" and modifier in ["", ".not"]):
                                    searches[search_final] = util.get_year_list(search_data, current_year, search_final)
                                elif (search in ["title", "studio"] and modifier not in ["", ".and", ".not", ".begins", ".ends"]) \
                                        or (search in ["actor", "audio_language", "collection", "content_rating", "country", "director", "genre", "label", "network", "producer", "subtitle_language", "writer"] and modifier not in ["", ".and", ".not"]) \
                                        or (search in ["resolution", "decade"] and modifier not in [""]) \
                                        or (search in ["added", "originally_available"] and modifier not in ["", ".not", ".before", ".after"]) \
                                        or (search in ["duration", "user_rating", "critic_rating", "audience_rating"] and modifier not in [".greater", ".less"]) \
                                        or (search in ["year"] and modifier not in ["", ".not", ".greater", ".less"]):
                                    raise Failed(f"Collection Error: modifier: {modifier} not supported with the {search} plex search attribute")
                                else:
                                    raise Failed(f"Collection Error: {search_final} plex search attribute not supported")
                            if len(searches) > 0:
                                self.methods.append((method_name, [searches]))
                            else:
                                raise Failed("Collection Error: no valid plex search attributes")
                        elif method_name == "tmdb_discover":
                            new_dictionary = {"limit": 100}
                            for discover_name, discover_data in method_data.items():
                                discover_final = discover_name.lower()
                                if discover_data:
                                    if (self.library.is_movie and discover_final in tmdb.discover_movie) or (self.library.is_show and discover_final in tmdb.discover_tv):
                                        if discover_final == "language":
                                            if re.compile("([a-z]{2})-([A-Z]{2})").match(str(discover_data)):
                                                new_dictionary[discover_final] = str(discover_data)
                                            else:
                                                raise Failed(f"Collection Error: {method_name} attribute {discover_final}: {discover_data} must match pattern ([a-z]{{2}})-([A-Z]{{2}}) e.g. en-US")
                                        elif discover_final == "region":
                                            if re.compile("^[A-Z]{2}$").match(str(discover_data)):
                                                new_dictionary[discover_final] = str(discover_data)
                                            else:
                                                raise Failed(f"Collection Error: {method_name} attribute {discover_final}: {discover_data} must match pattern ^[A-Z]{{2}}$ e.g. US")
                                        elif discover_final == "sort_by":
                                            if (self.library.is_movie and discover_data in tmdb.discover_movie_sort) or (self.library.is_show and discover_data in tmdb.discover_tv_sort):
                                                new_dictionary[discover_final] = discover_data
                                            else:
                                                raise Failed(f"Collection Error: {method_name} attribute {discover_final}: {discover_data} is invalid")
                                        elif discover_final == "certification_country":
                                            if "certification" in method_data or "certification.lte" in method_data or "certification.gte" in method_data:
                                                new_dictionary[discover_final] = discover_data
                                            else:
                                                raise Failed(f"Collection Error: {method_name} attribute {discover_final}: must be used with either certification, certification.lte, or certification.gte")
                                        elif discover_final in ["certification", "certification.lte", "certification.gte"]:
                                            if "certification_country" in method_data:
                                                new_dictionary[discover_final] = discover_data
                                            else:
                                                raise Failed(f"Collection Error: {method_name} attribute {discover_final}: must be used with certification_country")
                                        elif discover_final in ["include_adult", "include_null_first_air_dates", "screened_theatrically"]:
                                            if discover_data is True:
                                                new_dictionary[discover_final] = discover_data
                                        elif discover_final in tmdb.discover_dates:
                                            new_dictionary[discover_final] = util.check_date(discover_data, f"{method_name} attribute {discover_final}", return_string=True)
                                        elif discover_final in ["primary_release_year", "year", "first_air_date_year"]:
                                            new_dictionary[discover_final] = util.check_number(discover_data, f"{method_name} attribute {discover_final}", minimum=1800, maximum=current_year + 1)
                                        elif discover_final in ["vote_count.gte", "vote_count.lte", "vote_average.gte", "vote_average.lte", "with_runtime.gte", "with_runtime.lte"]:
                                            new_dictionary[discover_final] = util.check_number(discover_data, f"{method_name} attribute {discover_final}", minimum=1)
                                        elif discover_final in ["with_cast", "with_crew", "with_people", "with_companies", "with_networks", "with_genres", "without_genres", "with_keywords", "without_keywords", "with_original_language", "timezone"]:
                                            new_dictionary[discover_final] = discover_data
                                        else:
                                            raise Failed(f"Collection Error: {method_name} attribute {discover_final} not supported")
                                    elif discover_final == "limit":
                                        if isinstance(discover_data, int) and discover_data > 0:
                                            new_dictionary[discover_final] = discover_data
                                        else:
                                            raise Failed(f"Collection Error: {method_name} attribute {discover_final}: must be a valid number greater then 0")
                                    else:
                                        raise Failed(f"Collection Error: {method_name} attribute {discover_final} not supported")
                                else:
                                    raise Failed(f"Collection Error: {method_name} parameter {discover_final} is blank")
                            if len(new_dictionary) > 1:
                                self.methods.append((method_name, [new_dictionary]))
                            else:
                                raise Failed(f"Collection Error: {method_name} had no valid fields")
                        elif "tautulli" in method_name:
                            new_dictionary = {}
                            if method_name == "tautulli_popular":
                                new_dictionary["list_type"] = "popular"
                            elif method_name == "tautulli_watched":
                                new_dictionary["list_type"] = "watched"
                            else:
                                raise Failed(f"Collection Error: {method_name} attribute not supported")
                            dict_methods = {dm.lower(): dm for dm in method_data}
                            new_dictionary["list_days"] = get_int(method_name, "list_days", method_data, dict_methods, 30)
                            new_dictionary["list_size"] = get_int(method_name, "list_size", method_data, dict_methods, 10)
                            new_dictionary["list_buffer"] = get_int(method_name, "list_buffer", method_data, dict_methods, 20)
                            self.methods.append((method_name, [new_dictionary]))
                        elif method_name == "mal_season":
                            new_dictionary = {"sort_by": "anime_num_list_users"}
                            dict_methods = {dm.lower(): dm for dm in method_data}
                            if "sort_by" not in dict_methods:
                                logger.warning("Collection Warning: mal_season sort_by attribute not found using members as default")
                            elif not method_data[dict_methods["sort_by"]]:
                                logger.warning("Collection Warning: mal_season sort_by attribute is blank using members as default")
                            elif method_data[dict_methods["sort_by"]] not in mal.season_sort:
                                logger.warning(f"Collection Warning: mal_season sort_by attribute {method_data[dict_methods['sort_by']]} invalid must be either 'members' or 'score' using members as default")
                            else:
                                new_dictionary["sort_by"] = mal.season_sort[method_data[dict_methods["sort_by"]]]

                            if current_time.month in [1, 2, 3]:                     new_dictionary["season"] = "winter"
                            elif current_time.month in [4, 5, 6]:                   new_dictionary["season"] = "spring"
                            elif current_time.month in [7, 8, 9]:                   new_dictionary["season"] = "summer"
                            elif current_time.month in [10, 11, 12]:                new_dictionary["season"] = "fall"

                            if "season" not in dict_methods:
                                logger.warning(f"Collection Warning: mal_season season attribute not found using the current season: {new_dictionary['season']} as default")
                            elif not method_data[dict_methods["season"]]:
                                logger.warning(f"Collection Warning: mal_season season attribute is blank using the current season: {new_dictionary['season']} as default")
                            elif method_data[dict_methods["season"]] not in util.pretty_seasons:
                                logger.warning(f"Collection Warning: mal_season season attribute {method_data[dict_methods['season']]} invalid must be either 'winter', 'spring', 'summer' or 'fall' using the current season: {new_dictionary['season']} as default")
                            else:
                                new_dictionary["season"] = method_data[dict_methods["season"]]

                            new_dictionary["year"] = get_int(method_name, "year", method_data, dict_methods, current_time.year, minimum=1917, maximum=current_time.year + 1)
                            new_dictionary["limit"] = get_int(method_name, "limit", method_data, dict_methods, 100, maximum=500)
                            self.methods.append((method_name, [new_dictionary]))
                        elif method_name == "mal_userlist":
                            new_dictionary = {"status": "all", "sort_by": "list_score"}
                            dict_methods = {dm.lower(): dm for dm in method_data}
                            if "username" not in dict_methods:
                                raise Failed("Collection Error: mal_userlist username attribute is required")
                            elif not method_data[dict_methods["username"]]:
                                raise Failed("Collection Error: mal_userlist username attribute is blank")
                            else:
                                new_dictionary["username"] = method_data[dict_methods["username"]]

                            if "status" not in dict_methods:
                                logger.warning("Collection Warning: mal_season status attribute not found using all as default")
                            elif not method_data[dict_methods["status"]]:
                                logger.warning("Collection Warning: mal_season status attribute is blank using all as default")
                            elif method_data[dict_methods["status"]] not in mal.userlist_status:
                                logger.warning(f"Collection Warning: mal_season status attribute {method_data[dict_methods['status']]} invalid must be either 'all', 'watching', 'completed', 'on_hold', 'dropped' or 'plan_to_watch' using all as default")
                            else:
                                new_dictionary["status"] = mal.userlist_status[method_data[dict_methods["status"]]]

                            if "sort_by" not in dict_methods:
                                logger.warning("Collection Warning: mal_season sort_by attribute not found using score as default")
                            elif not method_data[dict_methods["sort_by"]]:
                                logger.warning("Collection Warning: mal_season sort_by attribute is blank using score as default")
                            elif method_data[dict_methods["sort_by"]] not in mal.userlist_sort:
                                logger.warning(f"Collection Warning: mal_season sort_by attribute {method_data[dict_methods['sort_by']]} invalid must be either 'score', 'last_updated', 'title' or 'start_date' using score as default")
                            else:
                                new_dictionary["sort_by"] = mal.userlist_sort[method_data[dict_methods["sort_by"]]]

                            new_dictionary["limit"] = get_int(method_name, "limit", method_data, dict_methods, 100, maximum=1000)
                            self.methods.append((method_name, [new_dictionary]))
                        elif "anilist" in method_name:
                            new_dictionary = {"sort_by": "score"}
                            dict_methods = {dm.lower(): dm for dm in method_data}
                            if method_name == "anilist_season":
                                if current_time.month in [12, 1, 2]:                    new_dictionary["season"] = "winter"
                                elif current_time.month in [3, 4, 5]:                   new_dictionary["season"] = "spring"
                                elif current_time.month in [6, 7, 8]:                   new_dictionary["season"] = "summer"
                                elif current_time.month in [9, 10, 11]:                 new_dictionary["season"] = "fall"

                                if "season" not in dict_methods:
                                    logger.warning(f"Collection Warning: anilist_season season attribute not found using the current season: {new_dictionary['season']} as default")
                                elif not method_data[dict_methods["season"]]:
                                    logger.warning(f"Collection Warning: anilist_season season attribute is blank using the current season: {new_dictionary['season']} as default")
                                elif method_data[dict_methods["season"]] not in util.pretty_seasons:
                                    logger.warning(f"Collection Warning: anilist_season season attribute {method_data[dict_methods['season']]} invalid must be either 'winter', 'spring', 'summer' or 'fall' using the current season: {new_dictionary['season']} as default")
                                else:
                                    new_dictionary["season"] = method_data[dict_methods["season"]]

                                new_dictionary["year"] = get_int(method_name, "year", method_data, dict_methods, current_time.year, minimum=1917, maximum=current_time.year + 1)
                            elif method_name == "anilist_genre":
                                if "genre" not in dict_methods:
                                    raise Failed(f"Collection Warning: anilist_genre genre attribute not found")
                                elif not method_data[dict_methods["genre"]]:
                                    raise Failed(f"Collection Warning: anilist_genre genre attribute is blank")
                                else:
                                    new_dictionary["genre"] = self.config.AniList.validate_genre(method_data[dict_methods["genre"]])
                            elif method_name == "anilist_tag":
                                if "tag" not in dict_methods:
                                    raise Failed(f"Collection Warning: anilist_tag tag attribute not found")
                                elif not method_data[dict_methods["tag"]]:
                                    raise Failed(f"Collection Warning: anilist_tag tag attribute is blank")
                                else:
                                    new_dictionary["tag"] = self.config.AniList.validate_tag(method_data[dict_methods["tag"]])

                            if "sort_by" not in dict_methods:
                                logger.warning(f"Collection Warning: {method_name} sort_by attribute not found using score as default")
                            elif not method_data[dict_methods["sort_by"]]:
                                logger.warning(f"Collection Warning: {method_name} sort_by attribute is blank using score as default")
                            elif str(method_data[dict_methods["sort_by"]]).lower() not in ["score", "popular"]:
                                logger.warning(f"Collection Warning: {method_name} sort_by attribute {method_data[dict_methods['sort_by']]} invalid must be either 'score' or 'popular' using score as default")
                            else:
                                new_dictionary["sort_by"] = method_data[dict_methods["sort_by"]]

                            new_dictionary["limit"] = get_int(method_name, "limit", method_data, dict_methods, 0, maximum=500)

                            self.methods.append((method_name, [new_dictionary]))
                    else:
                        raise Failed(f"Collection Error: {method_name} attribute is not a dictionary: {method_data}")
                elif method_name in numbered_builders:
                    list_count = util.regex_first_int(method_data, "List Size", default=10)
                    if list_count < 1:
                        logger.warning(f"Collection Warning: {method_name} must be an integer greater then 0 defaulting to 10")
                        list_count = 10
                    self.methods.append((method_name, [list_count]))
                elif "tvdb" in method_name:
                    values = util.get_list(method_data)
                    if method_name[-8:] == "_details":
                        if method_name == "tvdb_movie_details":
                            item = config.TVDb.get_movie(self.library.Plex.language, values[0])
                            if hasattr(item, "description") and item.description:
                                self.summaries[method_name] = item.description
                            if hasattr(item, "background_path") and item.background_path:
                                self.backgrounds[method_name] = f"{config.TMDb.image_url}{item.background_path}"
                            if hasattr(item, "poster_path") and item.poster_path:
                                self.posters[method_name] = f"{config.TMDb.image_url}{item.poster_path}"
                        elif method_name == "tvdb_show_details":
                            item = config.TVDb.get_series(self.library.Plex.language, values[0])
                            if hasattr(item, "description") and item.description:
                                self.summaries[method_name] = item.description
                            if hasattr(item, "background_path") and item.background_path:
                                self.backgrounds[method_name] = f"{config.TMDb.image_url}{item.background_path}"
                            if hasattr(item, "poster_path") and item.poster_path:
                                self.posters[method_name] = f"{config.TMDb.image_url}{item.poster_path}"
                        elif method_name == "tvdb_list_details":
                            self.summaries[method_name] = config.TVDb.get_list_description(values[0], self.library.Plex.language)
                        self.methods.append((method_name[:-8], values))
                    else:
                        self.methods.append((method_name, values))
                elif method_name in tmdb.builders:
                    values = config.TMDb.validate_tmdb_list(util.get_int_list(method_data, f"TMDb {tmdb.type_map[method_name]} ID"), tmdb.type_map[method_name])
                    if method_name[-8:] == "_details":
                        if method_name in ["tmdb_collection_details", "tmdb_movie_details", "tmdb_show_details"]:
                            item = config.TMDb.get_movie_show_or_collection(values[0], self.library.is_movie)
                            if hasattr(item, "overview") and item.overview:
                                self.summaries[method_name] = item.overview
                            if hasattr(item, "backdrop_path") and item.backdrop_path:
                                self.backgrounds[method_name] = f"{config.TMDb.image_url}{item.backdrop_path}"
                            if hasattr(item, "poster_path") and item.poster_path:
                                self.posters[method_name] = f"{config.TMDb.image_url}{item.poster_path}"
                        elif method_name in ["tmdb_actor_details", "tmdb_crew_details", "tmdb_director_details", "tmdb_producer_details", "tmdb_writer_details"]:
                            item = config.TMDb.get_person(values[0])
                            if hasattr(item, "biography") and item.biography:
                                self.summaries[method_name] = item.biography
                            if hasattr(item, "profile_path") and item.profile_path:
                                self.posters[method_name] = f"{config.TMDb.image_url}{item.profile_path}"
                        else:
                            item = config.TMDb.get_list(values[0])
                            if hasattr(item, "description") and item.description:
                                self.summaries[method_name] = item.description
                        self.methods.append((method_name[:-8], values))
                    else:
                        self.methods.append((method_name, values))
                elif method_name in all_builders:
                    self.methods.append((method_name, util.get_list(method_data)))
                elif method_name not in ignored_details:
                    raise Failed(f"Collection Error: {method_name} attribute not supported")
            elif method_key.lower() in all_builders or method_key.lower() in method_alias or method_key.lower() in plex.searches:
                raise Failed(f"Collection Error: {method_key} attribute is blank")
            else:
                logger.warning(f"Collection Warning: {method_key} attribute is blank")

        self.sync = self.library.sync_mode == "sync"
        if "sync_mode" in methods:
            if not self.data[methods["sync_mode"]]:
                logger.warning(f"Collection Warning: sync_mode attribute is blank using general: {self.library.sync_mode}")
            elif self.data[methods["sync_mode"]].lower() not in ["append", "sync"]:
                logger.warning(f"Collection Warning: {self.data[methods['sync_mode']]} sync_mode invalid using general: {self.library.sync_mode}")
            else:
                self.sync = self.data[methods["sync_mode"]].lower() == "sync"

        if self.add_to_radarr is None:
            self.add_to_radarr = self.library.Radarr.add if self.library.Radarr else False
        if self.add_to_sonarr is None:
            self.add_to_sonarr = self.library.Sonarr.add if self.library.Sonarr else False

        if self.collectionless:
            self.add_to_radarr = False
            self.add_to_sonarr = False
            self.details["collection_mode"] = "hide"
            self.sync = True

    def run_methods(self, collection_obj, collection_name, rating_key_map, movie_map, show_map):
        items_found = 0
        for method, values in self.methods:
            logger.debug("")
            logger.debug(f"Method: {method}")
            logger.debug(f"Values: {values}")
            for value in values:
                items = []
                missing_movies = []
                missing_shows = []
                def check_map(input_ids):
                    movie_ids, show_ids = input_ids
                    items_found_inside = 0
                    if len(movie_ids) > 0:
                        items_found_inside += len(movie_ids)
                        for movie_id in movie_ids:
                            if movie_id in movie_map:
                                items.append(movie_map[movie_id])
                            else:
                                missing_movies.append(movie_id)
                    if len(show_ids) > 0:
                        items_found_inside += len(show_ids)
                        for show_id in show_ids:
                            if show_id in show_map:                             items.append(show_map[show_id])
                            else:                                               missing_shows.append(show_id)
                    return items_found_inside
                logger.info("")
                logger.debug(f"Value: {value}")
                if "plex" in method:
                    items = self.library.get_items(method, value)
                    items_found += len(items)
                elif "tautulli" in method:
                    items = self.library.Tautulli.get_items(self.library, time_range=value["list_days"], stats_count=value["list_size"], list_type=value["list_type"], stats_count_buffer=value["list_buffer"])
                    items_found += len(items)
                elif "anidb" in method:                             items_found += check_map(self.config.AniDB.get_items(method, value, self.library.Plex.language))
                elif "anilist" in method:                           items_found += check_map(self.config.AniList.get_items(method, value))
                elif "mal" in method:                               items_found += check_map(self.config.MyAnimeList.get_items(method, value))
                elif "tvdb" in method:                              items_found += check_map(self.config.TVDb.get_items(method, value, self.library.Plex.language))
                elif "imdb" in method:                              items_found += check_map(self.config.IMDb.get_items(method, value, self.library.Plex.language))
                elif "letterboxd" in method:                        items_found += check_map(self.config.Letterboxd.get_items(method, value, self.library.Plex.language))
                elif "tmdb" in method:                              items_found += check_map(self.config.TMDb.get_items(method, value, self.library.is_movie))
                elif "trakt" in method:                             items_found += check_map(self.config.Trakt.get_items(method, value, self.library.is_movie))
                else:                                               logger.error(f"Collection Error: {method} method not supported")

                if len(items) > 0:                                  rating_key_map = self.library.add_to_collection(collection_obj if collection_obj else collection_name, items, self.filters, self.details["show_filtered"], rating_key_map, movie_map, show_map)
                else:                                               logger.error("No items found to add to this collection ")

                if len(missing_movies) > 0 or len(missing_shows) > 0:
                    logger.info("")
                    arr_filters = []
                    for filter_method, filter_data in self.filters:
                        if (filter_method.startswith("original_language") and self.library.is_movie) or filter_method.startswith("tmdb_vote_count"):
                            arr_filters.append((filter_method, filter_data))
                    if len(missing_movies) > 0:
                        missing_movies_with_names = []
                        for missing_id in missing_movies:
                            try:
                                movie = self.config.TMDb.get_movie(missing_id)
                            except Failed as e:
                                logger.error(e)
                                continue
                            match = True
                            for filter_method, filter_data in arr_filters:
                                if (filter_method == "original_language" and movie.original_language not in filter_data) \
                                        or (filter_method == "original_language.not" and movie.original_language in filter_data) \
                                        or (filter_method == "tmdb_vote_count.gte" and movie.vote_count < filter_data) \
                                        or (filter_method == "tmdb_vote_count.lte" and movie.vote_count > filter_data):
                                    match = False
                                    break
                            if match:
                                missing_movies_with_names.append((movie.title, missing_id))
                                if self.details["show_missing"] is True:
                                    logger.info(f"{collection_name} Collection | ? | {movie.title} (TMDb: {missing_id})")
                            elif self.details["show_filtered"] is True:
                                logger.info(f"{collection_name} Collection | X | {movie.title} (TMDb: {missing_id})")
                        logger.info(f"{len(missing_movies_with_names)} Movie{'s' if len(missing_movies_with_names) > 1 else ''} Missing")
                        if self.details["save_missing"] is True:
                            self.library.add_missing(collection_name, missing_movies_with_names, True)
                        if self.add_to_radarr and self.library.Radarr:
                            try:
                                self.library.Radarr.add_tmdb([missing_id for title, missing_id in missing_movies_with_names], **self.radarr_options)
                            except Failed as e:
                                logger.error(e)
                        if self.run_again:
                            self.missing_movies.extend([missing_id for title, missing_id in missing_movies_with_names])
                    if len(missing_shows) > 0 and self.library.is_show:
                        missing_shows_with_names = []
                        for missing_id in missing_shows:
                            try:
                                title = str(self.config.TVDb.get_series(self.library.Plex.language, missing_id).title.encode("ascii", "replace").decode())
                            except Failed as e:
                                logger.error(e)
                                continue
                            match = True
                            if arr_filters:
                                show = self.config.TMDb.get_show(self.config.TMDb.convert_tvdb_to_tmdb(missing_id))
                                for filter_method, filter_data in arr_filters:
                                    if (filter_method == "tmdb_vote_count.gte" and show.vote_count < filter_data) \
                                            or (filter_method == "tmdb_vote_count.lte" and show.vote_count > filter_data):
                                        match = False
                                        break
                            if match:
                                missing_shows_with_names.append((title, missing_id))
                                if self.details["show_missing"] is True:
                                    logger.info(f"{collection_name} Collection | ? | {title} (TVDB: {missing_id})")
                            elif self.details["show_filtered"] is True:
                                logger.info(f"{collection_name} Collection | X | {title} (TVDb: {missing_id})")
                        logger.info(f"{len(missing_shows_with_names)} Show{'s' if len(missing_shows_with_names) > 1 else ''} Missing")
                        if self.details["save_missing"] is True:
                            self.library.add_missing(collection_name, missing_shows_with_names, False)
                        if self.add_to_sonarr and self.library.Sonarr:
                            try:
                                self.library.Sonarr.add_tvdb([missing_id for title, missing_id in missing_shows_with_names], **self.sonarr_options)
                            except Failed as e:
                                logger.error(e)
                        if self.run_again:
                            self.missing_shows.extend([missing_id for title, missing_id in missing_shows_with_names])

        if self.sync and items_found > 0:
            logger.info("")
            count_removed = 0
            for ratingKey, item in rating_key_map.items():
                if item is not None:
                    logger.info(f"{collection_name} Collection | - | {item.title}")
                    item.removeCollection(collection_name)
                    count_removed += 1
            logger.info(f"{count_removed} {'Movie' if self.library.is_movie else 'Show'}{'s' if count_removed == 1 else ''} Removed")
        logger.info("")

    def update_details(self, collection):
        edits = {}
        def get_summary(summary_method, summaries):
            logger.info(f"Detail: {summary_method} updated Collection Summary")
            return summaries[summary_method]
        if "summary" in self.summaries:                     summary = get_summary("summary", self.summaries)
        elif "tmdb_description" in self.summaries:          summary = get_summary("tmdb_description", self.summaries)
        elif "letterboxd_description" in self.summaries:    summary = get_summary("letterboxd_description", self.summaries)
        elif "tmdb_summary" in self.summaries:              summary = get_summary("tmdb_summary", self.summaries)
        elif "tvdb_summary" in self.summaries:              summary = get_summary("tvdb_summary", self.summaries)
        elif "tmdb_biography" in self.summaries:            summary = get_summary("tmdb_biography", self.summaries)
        elif "tmdb_person" in self.summaries:               summary = get_summary("tmdb_person", self.summaries)
        elif "tmdb_collection_details" in self.summaries:   summary = get_summary("tmdb_collection_details", self.summaries)
        elif "trakt_list_details" in self.summaries:        summary = get_summary("trakt_list_details", self.summaries)
        elif "tmdb_list_details" in self.summaries:         summary = get_summary("tmdb_list_details", self.summaries)
        elif "tmdb_actor_details" in self.summaries:        summary = get_summary("tmdb_actor_details", self.summaries)
        elif "tmdb_crew_details" in self.summaries:         summary = get_summary("tmdb_crew_details", self.summaries)
        elif "tmdb_director_details" in self.summaries:     summary = get_summary("tmdb_director_details", self.summaries)
        elif "tmdb_producer_details" in self.summaries:     summary = get_summary("tmdb_producer_details", self.summaries)
        elif "tmdb_writer_details" in self.summaries:       summary = get_summary("tmdb_writer_details", self.summaries)
        elif "tmdb_movie_details" in self.summaries:        summary = get_summary("tmdb_movie_details", self.summaries)
        elif "tvdb_movie_details" in self.summaries:        summary = get_summary("tvdb_movie_details", self.summaries)
        elif "tvdb_show_details" in self.summaries:         summary = get_summary("tvdb_show_details", self.summaries)
        elif "tmdb_show_details" in self.summaries:         summary = get_summary("tmdb_show_details", self.summaries)
        else:                                               summary = None
        if summary:
            edits["summary.value"] = summary
            edits["summary.locked"] = 1

        if "sort_title" in self.details:
            edits["titleSort.value"] = self.details["sort_title"]
            edits["titleSort.locked"] = 1
            logger.info(f"Detail: sort_title updated Collection Sort Title to {self.details['sort_title']}")

        if "content_rating" in self.details:
            edits["contentRating.value"] = self.details["content_rating"]
            edits["contentRating.locked"] = 1
            logger.info(f"Detail: content_rating updated Collection Content Rating to {self.details['content_rating']}")

        if "collection_mode" in self.details:
            collection.modeUpdate(mode=self.details["collection_mode"])
            logger.info(f"Detail: collection_mode updated Collection Mode to {self.details['collection_mode']}")

        if "collection_order" in self.details:
            collection.sortUpdate(sort=self.details["collection_order"])
            logger.info(f"Detail: collection_order updated Collection Order to {self.details['collection_order']}")

        if "label" in self.details:
            item_labels = [label.tag for label in collection.labels]
            labels = util.get_list(self.details["label"])
            if "label_sync_mode" in self.details and str(self.details["label_sync_mode"]).lower() == "sync":
                for label in (la for la in item_labels if la not in labels):
                    collection.removeLabel(label)
                    logger.info(f"Detail: Label {label} removed")
            for label in (la for la in labels if la not in item_labels):
                collection.addLabel(label)
                logger.info(f"Detail: Label {label} added")

        if len(edits) > 0:
            logger.debug(edits)
            collection.edit(**edits)
            collection.reload()
            logger.info("Details: have been updated")

        if self.library.asset_directory:
            name_mapping = self.name
            if "name_mapping" in self.details:
                if self.details["name_mapping"]:                    name_mapping = self.details["name_mapping"]
                else:                                               logger.error("Collection Error: name_mapping attribute is blank")
            for ad in self.library.asset_directory:
                path = os.path.join(ad, f"{name_mapping}")
                if not os.path.isdir(path):
                    continue
                matches = glob.glob(os.path.join(ad, f"{name_mapping}", "poster.*"))
                if len(matches) > 0:
                    for match in matches:
                        self.posters["asset_directory"] = os.path.abspath(match)
                matches = glob.glob(os.path.join(ad, f"{name_mapping}", "background.*"))
                if len(matches) > 0:
                    for match in matches:
                        self.backgrounds["asset_directory"] = os.path.abspath(match)
                dirs = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
                if len(dirs) > 0:
                    for item in collection.items():
                        folder = os.path.basename(os.path.dirname(item.locations[0]) if self.library.is_movie else item.locations[0])
                        if folder in dirs:
                            matches = glob.glob(os.path.join(path, folder, "poster.*"))
                            poster_path = os.path.abspath(matches[0]) if len(matches) > 0 else None
                            matches = glob.glob(os.path.join(path, folder, "background.*"))
                            background_path = os.path.abspath(matches[0]) if len(matches) > 0 else None
                            if poster_path:
                                item.uploadPoster(filepath=poster_path)
                                logger.info(f"Detail: asset_directory updated {item.title}'s poster to [file] {poster_path}")
                            if background_path:
                                item.uploadArt(filepath=background_path)
                                logger.info(f"Detail: asset_directory updated {item.title}'s background to [file] {background_path}")
                            if poster_path is None and background_path is None:
                                logger.warning(f"No Files Found: {os.path.join(path, folder)}")
                            if self.library.is_show:
                                for season in item.seasons():
                                    matches = glob.glob(os.path.join(path, folder, f"Season{'0' if season.seasonNumber < 10 else ''}{season.seasonNumber}.*"))
                                    if len(matches) > 0:
                                        season_path = os.path.abspath(matches[0])
                                        season.uploadPoster(filepath=season_path)
                                        logger.info(f"Detail: asset_directory updated {item.title} Season {season.seasonNumber}'s poster to [file] {season_path}")
                        else:
                            logger.warning(f"No Folder: {os.path.join(path, folder)}")

        def set_image(image_method, images, is_background=False):
            message = f"{'background' if is_background else 'poster'} to [{'File' if image_method in image_file_details else 'URL'}] {images[image_method]}"
            try:
                if image_method in image_file_details and is_background:
                    collection.uploadArt(filepath=images[image_method])
                elif image_method in image_file_details:
                    collection.uploadPoster(filepath=images[image_method])
                elif is_background:
                    collection.uploadArt(url=images[image_method])
                else:
                    collection.uploadPoster(url=images[image_method])
                logger.info(f"Detail: {image_method} updated collection {message}")
            except BadRequest:
                logger.error(f"Detail: {image_method} failed to update {message}")

        if len(self.posters) > 0:
            logger.info("")

        if len(self.posters) > 1:
            logger.info(f"{len(self.posters)} posters found:")
            for p in self.posters:
                logger.info(f"Method: {p} Poster: {self.posters[p]}")

        if "url_poster" in self.posters:                    set_image("url_poster", self.posters)
        elif "file_poster" in self.posters:                 set_image("file_poster", self.posters)
        elif "tmdb_poster" in self.posters:                 set_image("tmdb_poster", self.posters)
        elif "tmdb_profile" in self.posters:                set_image("tmdb_profile", self.posters)
        elif "tvdb_poster" in self.posters:                 set_image("tvdb_poster", self.posters)
        elif "asset_directory" in self.posters:             set_image("asset_directory", self.posters)
        elif "tmdb_person" in self.posters:                 set_image("tmdb_person", self.posters)
        elif "tmdb_collection_details" in self.posters:     set_image("tmdb_collection_details", self.posters)
        elif "tmdb_actor_details" in self.posters:          set_image("tmdb_actor_details", self.posters)
        elif "tmdb_crew_details" in self.posters:           set_image("tmdb_crew_details", self.posters)
        elif "tmdb_director_details" in self.posters:       set_image("tmdb_director_details", self.posters)
        elif "tmdb_producer_details" in self.posters:       set_image("tmdb_producer_details", self.posters)
        elif "tmdb_writer_details" in self.posters:         set_image("tmdb_writer_details", self.posters)
        elif "tmdb_movie_details" in self.posters:          set_image("tmdb_movie_details", self.posters)
        elif "tvdb_movie_details" in self.posters:          set_image("tvdb_movie_details", self.posters)
        elif "tvdb_show_details" in self.posters:           set_image("tvdb_show_details", self.posters)
        elif "tmdb_show_details" in self.posters:           set_image("tmdb_show_details", self.posters)
        else:                                               logger.info("No poster to update")

        if len(self.backgrounds) > 0:
            logger.info("")

        if len(self.backgrounds) > 1:
            logger.info(f"{len(self.backgrounds)} backgrounds found:")
            for b in self.backgrounds:
                logger.info(f"Method: {b} Background: {self.backgrounds[b]}")

        if "url_background" in self.backgrounds:            set_image("url_background", self.backgrounds, is_background=True)
        elif "file_background" in self.backgrounds:         set_image("file_background", self.backgrounds, is_background=True)
        elif "tmdb_background" in self.backgrounds:         set_image("tmdb_background", self.backgrounds, is_background=True)
        elif "tvdb_background" in self.backgrounds:         set_image("tvdb_background", self.backgrounds, is_background=True)
        elif "asset_directory" in self.backgrounds:         set_image("asset_directory", self.backgrounds, is_background=True)
        elif "tmdb_collection_details" in self.backgrounds: set_image("tmdb_collection_details", self.backgrounds, is_background=True)
        elif "tmdb_movie_details" in self.backgrounds:      set_image("tmdb_movie_details", self.backgrounds, is_background=True)
        elif "tvdb_movie_details" in self.backgrounds:      set_image("tvdb_movie_details", self.backgrounds, is_background=True)
        elif "tvdb_show_details" in self.backgrounds:       set_image("tvdb_show_details", self.backgrounds, is_background=True)
        elif "tmdb_show_details" in self.backgrounds:       set_image("tmdb_show_details", self.backgrounds, is_background=True)
        else:                                               logger.info("No background to update")

    def run_collections_again(self, collection_obj, movie_map, show_map):
        collection_items = collection_obj.items() if isinstance(collection_obj, Collections) else []
        name = collection_obj.title if isinstance(collection_obj, Collections) else collection_obj
        rating_keys = [movie_map[mm] for mm in self.missing_movies if mm in movie_map]
        if self.library.is_show:
            rating_keys.extend([show_map[sm] for sm in self.missing_shows if sm in show_map])

        if len(rating_keys) > 0:
            for rating_key in rating_keys:
                try:
                    current = self.library.fetchItem(int(rating_key))
                except (BadRequest, NotFound):
                    logger.error(f"Plex Error: Item {rating_key} not found")
                    continue
                if current in collection_items:
                    logger.info(f"{name} Collection | = | {current.title}")
                else:
                    current.addCollection(name)
                    logger.info(f"{name} Collection | + | {current.title}")
            logger.info(f"{len(rating_keys)} {'Movie' if self.library.is_movie else 'Show'}{'s' if len(rating_keys) > 1 else ''} Processed")

        if len(self.missing_movies) > 0:
            logger.info("")
            for missing_id in self.missing_movies:
                if missing_id not in movie_map:
                    try:
                        movie = self.config.TMDb.get_movie(missing_id)
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.details["show_missing"] is True:
                        logger.info(f"{name} Collection | ? | {movie.title} (TMDb: {missing_id})")
            logger.info("")
            logger.info(f"{len(self.missing_movies)} Movie{'s' if len(self.missing_movies) > 1 else ''} Missing")

        if len(self.missing_shows) > 0 and self.library.is_show:
            logger.info("")
            for missing_id in self.missing_shows:
                if missing_id not in show_map:
                    try:
                        title = str(self.config.TVDb.get_series(self.library.Plex.language, missing_id).title.encode("ascii", "replace").decode())
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.details["show_missing"] is True:
                        logger.info(f"{name} Collection | ? | {title} (TVDb: {missing_id})")
            logger.info(f"{len(self.missing_shows)} Show{'s' if len(self.missing_shows) > 1 else ''} Missing")
