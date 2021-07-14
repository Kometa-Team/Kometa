import logging, os, re
from datetime import datetime, timedelta
from modules import anidb, anilist, icheckmovies, imdb, letterboxd, mal, plex, radarr, sonarr, tautulli, tmdb, trakttv, tvdb, util
from modules.util import Failed, ImageData
from PIL import Image
from plexapi.exceptions import BadRequest, NotFound
from plexapi.video import Movie, Show
from urllib.parse import quote

logger = logging.getLogger("Plex Meta Manager")

string_filters = ["title", "episode_title", "studio"]
image_file_details = ["file_poster", "file_background", "asset_directory"]
advance_new_agent = ["item_metadata_language", "item_use_original_title"]
advance_show = ["item_episode_sorting", "item_keep_episodes", "item_delete_episodes", "item_season_display", "item_episode_sorting"]
method_alias = {
    "actors": "actor", "role": "actor", "roles": "actor",
    "show_actor": "actor", "show_actors": "actor", "show_role": "actor", "show_roles": "actor",
    "collections": "collection", "plex_collection": "collection",
    "show_collections": "collection", "show_collection": "collection",
    "content_ratings": "content_rating", "contentRating": "content_rating", "contentRatings": "content_rating",
    "countries": "country",
    "decades": "decade",
    "directors": "director",
    "genres": "genre",
    "labels": "label",
    "rating": "critic_rating",
    "show_user_rating": "user_rating",
    "video_resolution": "resolution",
    "play": "plays", "show_plays": "plays", "show_play": "plays", "episode_play": "episode_plays",
    "originally_available": "release", "episode_originally_available": "episode_air_date",
    "episode_release": "episode_air_date", "episode_released": "episode_air_date",
    "show_originally_available": "release", "show_release": "release", "show_air_date": "release",
    "released": "release", "show_released": "release", "max_age": "release",
    "studios": "studio",
    "networks": "network",
    "producers": "producer",
    "writers": "writer",
    "years": "year", "show_year": "year", "show_years": "year",
    "show_title": "title"
}
filter_translation = {
    "actor": "actors",
    "audience_rating": "audienceRating",
    "collection": "collections",
    "content_rating": "contentRating",
    "country": "countries",
    "critic_rating": "rating",
    "director": "directors",
    "genre": "genres",
    "label": "labels",
    "producer": "producers",
    "release": "originallyAvailableAt",
    "added": "addedAt",
    "last_played": "lastViewedAt",
    "plays": "viewCount",
    "user_rating": "userRating",
    "writer": "writers"
}
modifier_alias = {".greater": ".gt", ".less": ".lt"}
all_builders = anidb.builders + anilist.builders + icheckmovies.builders + imdb.builders + letterboxd.builders + mal.builders + plex.builders + tautulli.builders + tmdb.builders + trakttv.builders + tvdb.builders
dictionary_builders = [
    "filters",
    "anidb_tag",
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
    "icheckmovies_list",
    "icheckmovies_list_details",
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
smart_collection_invalid = ["collection_order"]
smart_url_collection_invalid = [
    "run_again", "sync_mode", "show_filtered", "show_missing", "save_missing", "smart_label",
    "radarr_add", "radarr_folder", "radarr_monitor", "radarr_availability", 
    "radarr_quality", "radarr_tag", "radarr_search",
    "sonarr_add", "sonarr_folder", "sonarr_monitor", "sonarr_quality", "sonarr_language", 
    "sonarr_series", "sonarr_season", "sonarr_tag", "sonarr_search", "sonarr_cutoff_search",
    "filters"
]
summary_details = [
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography", "tvdb_summary",
    "tvdb_description", "trakt_description", "letterboxd_description", "icheckmovies_description"
]
poster_details = [
    "url_poster", "tmdb_poster", "tmdb_profile", "tvdb_poster", "file_poster"
]
background_details = [
    "url_background", "tmdb_background", "tvdb_background", "file_background"
]
boolean_details = [
    "visible_library",
    "visible_home",
    "visible_shared",
    "show_filtered",
    "show_missing",
    "save_missing",
    "item_assets"
]
string_details = [
    "sort_title",
    "content_rating",
    "name_mapping"
]
ignored_details = [
    "smart_filter",
    "smart_label",
    "smart_url",
    "run_again",
    "schedule",
    "sync_mode",
    "template",
    "test",
    "tmdb_person",
    "build_collection"
]
collectionless_details = [
    "collection_order", "plex_collectionless",
    "label", "label_sync_mode", "test"
] + poster_details + background_details + summary_details + string_details
all_filters = [
    "actor", "actor.not",
    "audio_language", "audio_language.not",
    "audio_track_title", "audio_track_title.not", "audio_track_title.begins", "audio_track_title.ends", "audio_track_title.regex",
    "collection", "collection.not",
    "content_rating", "content_rating.not",
    "country", "country.not",
    "director", "director.not",
    "filepath", "filepath.not", "filepath.begins", "filepath.ends", "filepath.regex",
    "genre", "genre.not",
    "label", "label.not",
    "producer", "producer.not",
    "release", "release.not", "release.before", "release.after", "release.regex", "history",
    "added", "added.not", "added.before", "added.after", "added.regex",
    "last_played", "last_played.not", "last_played.before", "last_played.after", "last_played.regex",
    "title", "title.not", "title.begins", "title.ends", "title.regex",
    "plays.gt", "plays.gte", "plays.lt", "plays.lte",
    "tmdb_vote_count.gt", "tmdb_vote_count.gte", "tmdb_vote_count.lt", "tmdb_vote_count.lte",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte",
    "original_language", "original_language.not",
    "user_rating.gt", "user_rating.gte", "user_rating.lt", "user_rating.lte",
    "audience_rating.gt", "audience_rating.gte", "audience_rating.lt", "audience_rating.lte",
    "critic_rating.gt", "critic_rating.gte", "critic_rating.lt", "critic_rating.lte",
    "studio", "studio.not", "studio.begins", "studio.ends", "studio.regex",
    "subtitle_language", "subtitle_language.not",
    "resolution", "resolution.not",
    "writer", "writer.not",
    "year", "year.gt", "year.gte", "year.lt", "year.lte", "year.not"
]
movie_only_filters = [
    "audio_language", "audio_language.not",
    "audio_track_title", "audio_track_title.not", "audio_track_title.begins", "audio_track_title.ends", "audio_track_title.regex",
    "country", "country.not",
    "director", "director.not",
    "duration.gt", "duration.gte", "duration.lt", "duration.lte",
    "original_language", "original_language.not",
    "subtitle_language", "subtitle_language.not",
    "resolution", "resolution.not",
    "writer", "writer.not"
]
show_only_filters = ["network"]

class CollectionBuilder:
    def __init__(self, config, library, metadata, name, data):
        self.config = config
        self.library = library
        self.metadata = metadata
        self.name = name
        self.data = data
        self.details = {
            "show_filtered": self.library.show_filtered,
            "show_missing": self.library.show_missing,
            "save_missing": self.library.save_missing,
            "item_assets": False
        }
        self.item_details = {}
        self.radarr_options = {}
        self.sonarr_options = {}
        self.missing_movies = []
        self.missing_shows = []
        self.methods = []
        self.filters = []
        self.rating_keys = []
        self.run_again_movies = []
        self.run_again_shows = []
        self.posters = {}
        self.backgrounds = {}
        self.summaries = {}
        self.schedule = ""
        self.add_to_radarr = None
        self.add_to_sonarr = None
        self.current_time = datetime.now()
        self.current_year = self.current_time.year

        methods = {m.lower(): m for m in self.data}

        if "template" in methods:
            logger.info("")
            logger.info("Validating Method: template")
            if not self.metadata.templates:
                raise Failed("Collection Error: No templates found")
            elif not self.data[methods["template"]]:
                raise Failed("Collection Error: template attribute is blank")
            else:
                logger.debug(f"Value: {self.data[methods['template']]}")
                for variables in util.get_list(self.data[methods["template"]], split=False):
                    if not isinstance(variables, dict):
                        raise Failed("Collection Error: template attribute is not a dictionary")
                    elif "name" not in variables:
                        raise Failed("Collection Error: template sub-attribute name is required")
                    elif not variables["name"]:
                        raise Failed("Collection Error: template sub-attribute name is blank")
                    elif variables["name"] not in self.metadata.templates:
                        raise Failed(f"Collection Error: template {variables['name']} not found")
                    elif not isinstance(self.metadata.templates[variables["name"]], dict):
                        raise Failed(f"Collection Error: template {variables['name']} is not a dictionary")
                    else:
                        for tm in variables:
                            if not variables[tm]:
                                raise Failed(f"Collection Error: template sub-attribute {tm} is blank")
                        if "collection_name" not in variables:
                            variables["collection_name"] = str(self.name)

                        template_name = variables["name"]
                        template = self.metadata.templates[template_name]

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

                        def check_data(_data):
                            if isinstance(_data, dict):
                                final_data = {}
                                for sm, sd in _data.items():
                                    try:
                                        final_data[sm] = check_data(sd)
                                    except Failed:
                                        continue
                            elif isinstance(_data, list):
                                final_data = []
                                for li in _data:
                                    try:
                                        final_data.append(check_data(li))
                                    except Failed:
                                        continue
                            else:
                                txt = str(_data)
                                def scan_text(og_txt, var, var_value):
                                    if og_txt == f"<<{var}>>":
                                        return str(var_value)
                                    elif f"<<{var}>>" in str(og_txt):
                                        return str(og_txt).replace(f"<<{var}>>", str(var_value))
                                    else:
                                        return og_txt
                                for option in optional:
                                    if option not in variables and f"<<{option}>>" in txt:
                                        raise Failed
                                for variable, variable_data in variables.items():
                                    if variable != "name":
                                        txt = scan_text(txt, variable, variable_data)
                                for dm, dd in default.items():
                                    txt = scan_text(txt, dm, dd)
                                if txt in ["true", "True"]:
                                    final_data = True
                                elif txt in ["false", "False"]:
                                    final_data = False
                                else:
                                    try:
                                        num_data = float(txt)
                                        final_data = int(num_data) if num_data.is_integer() else num_data
                                    except (ValueError, TypeError):
                                        final_data = txt
                            return final_data

                        for method_name, attr_data in template.items():
                            if method_name not in self.data and method_name not in ["default", "optional"]:
                                if attr_data is None:
                                    logger.error(f"Template Error: template attribute {method_name} is blank")
                                    continue
                                try:
                                    self.data[method_name] = check_data(attr_data)
                                    methods[method_name.lower()] = method_name
                                except Failed:
                                    continue

        if "schedule" in methods:
            logger.info("")
            logger.info("Validating Method: schedule")
            if not self.data[methods["schedule"]]:
                raise Failed("Collection Error: schedule attribute is blank")
            else:
                logger.debug(f"Value: {self.data[methods['schedule']]}")
                skip_collection = True
                schedule_list = util.get_list(self.data[methods["schedule"]])
                next_month = self.current_time.replace(day=28) + timedelta(days=4)
                last_day = next_month - timedelta(days=next_month.day)
                for schedule in schedule_list:
                    run_time = str(schedule).lower()
                    if run_time.startswith(("day", "daily")):
                        skip_collection = False
                    elif run_time.startswith(("hour", "week", "month", "year")):
                        match = re.search("\\(([^)]+)\\)", run_time)
                        if not match:
                            logger.error(f"Collection Error: failed to parse schedule: {schedule}")
                            continue
                        param = match.group(1)
                        if run_time.startswith("hour"):
                            try:
                                if 0 <= int(param) <= 23:
                                    self.schedule += f"\nScheduled to run only on the {util.make_ordinal(param)} hour"
                                    if config.run_hour == int(param):
                                        skip_collection = False
                                else:
                                    raise ValueError
                            except ValueError:
                                logger.error(f"Collection Error: hourly schedule attribute {schedule} invalid must be an integer between 0 and 23")
                        elif run_time.startswith("week"):
                            if param.lower() not in util.days_alias:
                                logger.error(f"Collection Error: weekly schedule attribute {schedule} invalid must be a day of the week i.e. weekly(Monday)")
                                continue
                            weekday = util.days_alias[param.lower()]
                            self.schedule += f"\nScheduled weekly on {util.pretty_days[weekday]}"
                            if weekday == self.current_time.weekday():
                                skip_collection = False
                        elif run_time.startswith("month"):
                            try:
                                if 1 <= int(param) <= 31:
                                    self.schedule += f"\nScheduled monthly on the {util.make_ordinal(param)}"
                                    if self.current_time.day == int(param) or (self.current_time.day == last_day.day and int(param) > last_day.day):
                                        skip_collection = False
                                else:
                                    raise ValueError
                            except ValueError:
                                logger.error(f"Collection Error: monthly schedule attribute {schedule} invalid must be an integer between 1 and 31")
                        elif run_time.startswith("year"):
                            match = re.match("^(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])$", param)
                            if not match:
                                logger.error(f"Collection Error: yearly schedule attribute {schedule} invalid must be in the MM/DD format i.e. yearly(11/22)")
                                continue
                            month = int(match.group(1))
                            day = int(match.group(2))
                            self.schedule += f"\nScheduled yearly on {util.pretty_months[month]} {util.make_ordinal(day)}"
                            if self.current_time.month == month and (self.current_time.day == day or (self.current_time.day == last_day.day and day > last_day.day)):
                                skip_collection = False
                    else:
                        logger.error(f"Collection Error: schedule attribute {schedule} invalid")
                if len(self.schedule) == 0:
                    skip_collection = False
                if skip_collection:
                    raise Failed(f"{self.schedule}\n\nCollection {self.name} not scheduled to run")

        self.run_again = "run_again" in methods
        self.collectionless = "plex_collectionless" in methods

        self.run_again = False
        if "run_again" in methods:
            logger.info("")
            logger.info("Validating Method: run_again")
            if not self.data[methods["run_again"]]:
                logger.warning(f"Collection Warning: run_again attribute is blank defaulting to false")
            else:
                logger.debug(f"Value: {self.data[methods['run_again']]}")
                self.run_again = util.get_bool("run_again", self.data[methods["run_again"]])

        self.sync = self.library.sync_mode == "sync"
        if "sync_mode" in methods:
            logger.info("")
            logger.info("Validating Method: sync_mode")
            if not self.data[methods["sync_mode"]]:
                logger.warning(f"Collection Warning: sync_mode attribute is blank using general: {self.library.sync_mode}")
            else:
                logger.debug(f"Value: {self.data[methods['sync_mode']]}")
                if self.data[methods["sync_mode"]].lower() not in ["append", "sync"]:
                    logger.warning(f"Collection Warning: {self.data[methods['sync_mode']]} sync_mode invalid using general: {self.library.sync_mode}")
                else:
                    self.sync = self.data[methods["sync_mode"]].lower() == "sync"

        self.build_collection = True
        if "build_collection" in methods:
            logger.info("")
            logger.info("Validating Method: build_collection")
            if self.data[methods["build_collection"]] is None:
                logger.warning(f"Collection Warning: build_collection attribute is blank defaulting to true")
            else:
                logger.debug(f"Value: {self.data[methods['build_collection']]}")
                self.build_collection = util.get_bool("build_collection", self.data[methods["build_collection"]])

        if "tmdb_person" in methods:
            logger.info("")
            logger.info("Validating Method: tmdb_person")
            if not self.data[methods["tmdb_person"]]:
                raise Failed("Collection Error: tmdb_person attribute is blank")
            else:
                logger.debug(f"Value: {self.data[methods['tmdb_person']]}")
                valid_names = []
                for tmdb_id in util.get_int_list(self.data[methods["tmdb_person"]], "TMDb Person ID"):
                    person = config.TMDb.get_person(tmdb_id)
                    valid_names.append(person.name)
                    if hasattr(person, "biography") and person.biography:
                        self.summaries["tmdb_person"] = person.biography
                    if hasattr(person, "profile_path") and person.profile_path:
                        self.posters["tmdb_person"] = f"{config.TMDb.image_url}{person.profile_path}"
                if len(valid_names) > 0:
                    self.details["tmdb_person"] = valid_names
                else:
                    raise Failed(f"Collection Error: No valid TMDb Person IDs in {self.data[methods['tmdb_person']]}")

        self.smart_sort = "random"
        self.smart_label_collection = False
        if "smart_label" in methods:
            logger.info("")
            logger.info("Validating Method: smart_label")
            self.smart_label_collection = True
            if not self.data[methods["smart_label"]]:
                logger.warning("Collection Error: smart_label attribute is blank defaulting to random")
            else:
                logger.debug(f"Value: {self.data[methods['smart_label']]}")
                if (self.library.is_movie and str(self.data[methods["smart_label"]]).lower() in plex.movie_sorts) \
                        or (self.library.is_show and str(self.data[methods["smart_label"]]).lower() in plex.show_sorts):
                    self.smart_sort = str(self.data[methods["smart_label"]]).lower()
                else:
                    logger.warning(f"Collection Error: smart_label attribute: {self.data[methods['smart_label']]} is invalid defaulting to random")

        self.smart_url = None
        self.smart_type_key = None
        self.smart_filter_details = ""
        if "smart_url" in methods:
            logger.info("")
            logger.info("Validating Method: smart_url")
            if not self.data[methods["smart_url"]]:
                raise Failed("Collection Error: smart_url attribute is blank")
            else:
                logger.debug(f"Value: {self.data[methods['smart_url']]}")
                try:
                    self.smart_url, self.smart_type_key = self.library.get_smart_filter_from_uri(self.data[methods["smart_url"]])
                except ValueError:
                    raise Failed("Collection Error: smart_url is incorrectly formatted")

        if "smart_filter" in methods:
            self.smart_type_key, self.smart_filter_details, self.smart_url = self.build_filter("smart_filter", self.data[methods["smart_filter"]], smart=True)

        def cant_interact(attr1, attr2, fail=False):
            if getattr(self, attr1) and getattr(self, attr2):
                message = f"Collection Error: {attr1} & {attr2} attributes cannot go together"
                if fail:
                    raise Failed(message)
                else:
                    setattr(self, attr2, False)
                    logger.info("")
                    logger.warning(f"{message} removing {attr2}")

        cant_interact("smart_label_collection", "collectionless")
        cant_interact("smart_url", "collectionless")
        cant_interact("smart_url", "run_again")
        cant_interact("smart_label_collection", "smart_url", fail=True)

        self.smart = self.smart_url or self.smart_label_collection

        for method_key, method_data in self.data.items():
            if method_key.lower() in ignored_details:
                continue
            logger.info("")
            logger.info(f"Validating Method: {method_key}")
            if "trakt" in method_key.lower() and not config.Trakt:                      raise Failed(f"Collection Error: {method_key} requires Trakt todo be configured")
            elif "imdb" in method_key.lower() and not config.IMDb:                      raise Failed(f"Collection Error: {method_key} requires TMDb or Trakt to be configured")
            elif "radarr" in method_key.lower() and not self.library.Radarr:            raise Failed(f"Collection Error: {method_key} requires Radarr to be configured")
            elif "sonarr" in method_key.lower() and not self.library.Sonarr:            raise Failed(f"Collection Error: {method_key} requires Sonarr to be configured")
            elif "tautulli" in method_key.lower() and not self.library.Tautulli:        raise Failed(f"Collection Error: {method_key} requires Tautulli to be configured")
            elif "mal" in method_key.lower() and not config.MyAnimeList:                raise Failed(f"Collection Error: {method_key} requires MyAnimeList to be configured")
            elif method_data is not None:
                logger.debug(f"Value: {method_data}")
                method_name, method_mod, method_final = self._split(method_key)
                if method_name in show_only_builders and self.library.is_movie:
                    raise Failed(f"Collection Error: {method_name} attribute only works for show libraries")
                elif method_name in movie_only_builders and self.library.is_show:
                    raise Failed(f"Collection Error: {method_name} attribute only works for movie libraries")
                elif method_name in plex.movie_only_searches and self.library.is_show:
                    raise Failed(f"Collection Error: {method_name} plex search only works for movie libraries")
                elif method_name in plex.show_only_searches and self.library.is_movie:
                    raise Failed(f"Collection Error: {method_name} plex search only works for show libraries")
                elif method_name in smart_collection_invalid and self.smart:
                    raise Failed(f"Collection Error: {method_name} attribute only works with normal collections")
                elif method_name not in collectionless_details and self.collectionless:
                    raise Failed(f"Collection Error: {method_name} attribute does not work for Collectionless collection")
                elif self.smart_url and (method_name in all_builders or method_name in smart_url_collection_invalid):
                    raise Failed(f"Collection Error: {method_name} builder not allowed when using smart_filter")
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
                elif method_name == "icheckmovies_description":
                    self.summaries[method_name] = config.ICheckMovies.get_list_description(method_data, self.library.Plex.language)
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
                elif method_name == "label":
                    if "label" in methods and "label.sync" in methods:
                        raise Failed("Collection Error: Cannot use label and label.sync together")
                    if "label.remove" in methods and "label.sync" in methods:
                        raise Failed("Collection Error: Cannot use label.remove and label.sync together")
                    if method_final == "label" and "label_sync_mode" in methods and self.data[methods["label_sync_mode"]] == "sync":
                        self.details["label.sync"] = util.get_list(method_data)
                    else:
                        self.details[method_final] = util.get_list(method_data)
                elif method_name == "item_label":
                    if "item_label" in methods and "item_label.sync" in methods:
                        raise Failed(f"Collection Error: Cannot use item_label and item_label.sync together")
                    if "item_label.remove" in methods and "item_label.sync" in methods:
                        raise Failed(f"Collection Error: Cannot use item_label.remove and item_label.sync together")
                    self.item_details[method_final] = util.get_list(method_data)
                elif method_name in ["item_radarr_tag", "item_sonarr_tag"]:
                    if method_name in methods and f"{method_name}.sync" in methods:
                        raise Failed(f"Collection Error: Cannot use {method_name} and {method_name}.sync together")
                    if f"{method_name}.remove" in methods and f"{method_name}.sync" in methods:
                        raise Failed(f"Collection Error: Cannot use {method_name}.remove and {method_name}.sync together")
                    if method_name in methods and f"{method_name}.remove" in methods:
                        raise Failed(f"Collection Error: Cannot use {method_name} and {method_name}.remove together")
                    self.item_details[method_name] = util.get_list(method_data)
                    self.item_details["apply_tags"] = method_mod[1:] if method_mod else ""
                elif method_name == "item_overlay":
                    overlay = os.path.join(config.default_dir, "overlays", method_data, "overlay.png")
                    if not os.path.exists(overlay):
                        raise Failed(f"Collection Error: {method_data} overlay image not found at {overlay}")
                    if method_data in self.library.overlays:
                        raise Failed("Each Overlay can only be used once per Library")
                    self.library.overlays.append(method_data)
                    self.item_details[method_name] = method_data
                elif method_name in plex.item_advance_keys:
                    key, options = plex.item_advance_keys[method_name]
                    if method_name in advance_new_agent and self.library.agent not in plex.new_plex_agents:
                        logger.error(f"Metadata Error: {method_name} attribute only works for with the New Plex Movie Agent and New Plex TV Agent")
                    elif method_name in advance_show and not self.library.is_show:
                        logger.error(f"Metadata Error: {method_name} attribute only works for show libraries")
                    elif str(method_data).lower() not in options:
                        logger.error(f"Metadata Error: {method_data} {method_name} attribute invalid")
                    else:
                        self.item_details[method_name] = str(method_data).lower()
                elif method_name in boolean_details:
                    self.details[method_name] = util.get_bool(method_name, method_data)
                elif method_name in string_details:
                    self.details[method_name] = str(method_data)
                elif method_name == "radarr_add":
                    self.add_to_radarr = util.get_bool(method_name, method_data)
                elif method_name == "radarr_folder":
                    self.radarr_options["folder"] = method_data
                elif method_name in ["radarr_monitor", "radarr_search"]:
                    self.radarr_options[method_name[7:]] = util.get_bool(method_name, method_data)
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
                    self.add_to_sonarr = util.get_bool(method_name, method_data)
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
                    self.sonarr_options[method_name[7:]] = util.get_bool(method_name, method_data)
                elif method_name == "sonarr_tag":
                    self.sonarr_options["tag"] = util.get_list(method_data)
                elif method_final in plex.searches:
                    self.methods.append(("plex_search", [self.build_filter("plex_search", {"any": {method_name: method_data}})]))
                elif method_name == "plex_all":
                    self.methods.append((method_name, [""]))
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
                                imdb_url = config.IMDb.validate_imdb_url(imdb_list[dict_methods["url"]], self.library.Plex.language)
                            else:
                                raise Failed("Collection Error: imdb_list attribute url is required")
                            if "limit" in dict_methods and imdb_list[dict_methods["limit"]]:
                                list_count = util.regex_first_int(imdb_list[dict_methods["limit"]], "List Limit", default=0)
                            else:
                                list_count = 0
                        else:
                            imdb_url = config.IMDb.validate_imdb_url(str(imdb_list), self.library.Plex.language)
                            list_count = 0
                        new_list.append({"url": imdb_url, "limit": list_count})
                    self.methods.append((method_name, new_list))
                elif method_name == "icheckmovies_list":
                    valid_lists = []
                    for icheckmovies_list in util.get_list(method_data, split=False):
                        valid_lists.append(config.ICheckMovies.validate_icheckmovies_list(icheckmovies_list, self.library.Plex.language))
                    self.methods.append((method_name, valid_lists))
                elif method_name == "icheckmovies_list_details":
                    valid_lists = []
                    for icheckmovies_list in util.get_list(method_data, split=False):
                        valid_lists.append(config.ICheckMovies.validate_icheckmovies_list(icheckmovies_list, self.library.Plex.language))
                    self.methods.append((method_name[:-8], valid_lists))
                    self.summaries[method_name] = config.ICheckMovies.get_list_description(method_data, self.library.Plex.language)
                elif method_name == "letterboxd_list":
                    self.methods.append((method_name, util.get_list(method_data, split=False)))
                elif method_name == "letterboxd_list_details":
                    values = util.get_list(method_data, split=False)
                    self.summaries[method_name] = config.Letterboxd.get_list_description(values[0], self.library.Plex.language)
                    self.methods.append((method_name[:-8], values))
                elif method_name in dictionary_builders:
                    for dict_data in util.get_list(method_data):
                        if isinstance(dict_data, dict):
                            def get_int(parent, int_method, data_in, methods_in, default_in, minimum=1, maximum=None):
                                if int_method not in methods_in:
                                    logger.warning(f"Collection Warning: {parent} {int_method} attribute not found using {default_in} as default")
                                elif not data_in[methods_in[int_method]]:
                                    logger.warning(f"Collection Warning: {parent} {methods_in[int_method]} attribute is blank using {default_in} as default")
                                elif isinstance(data_in[methods_in[int_method]], int) and data_in[methods_in[int_method]] >= minimum:
                                    if maximum is None or data_in[methods_in[int_method]] <= maximum:
                                        return data_in[methods_in[int_method]]
                                    else:
                                        logger.warning(f"Collection Warning: {parent} {methods_in[int_method]} attribute {data_in[methods_in[int_method]]} invalid must an integer <= {maximum} using {default_in} as default")
                                else:
                                    logger.warning(f"Collection Warning: {parent} {methods_in[int_method]} attribute {data_in[methods_in[int_method]]} invalid must an integer >= {minimum} using {default_in} as default")
                                return default_in
                            if method_name == "filters":
                                validate = True
                                if "validate" in dict_data:
                                    if dict_data["validate"] is None:
                                        raise Failed("Collection Error: validate filter attribute is blank")
                                    if not isinstance(dict_data["validate"], bool):
                                        raise Failed("Collection Error: validate filter attribute must be either true or false")
                                    validate = dict_data["validate"]
                                for filter_method, filter_data in dict_data.items():
                                    filter_attr, modifier, filter_final = self._split(filter_method)
                                    if filter_final not in all_filters:
                                        raise Failed(f"Collection Error: {filter_final} is not a valid filter attribute")
                                    elif filter_final in movie_only_filters and self.library.is_show:
                                        raise Failed(f"Collection Error: {filter_final} filter attribute only works for movie libraries")
                                    elif filter_final in show_only_filters and self.library.is_movie:
                                        raise Failed(f"Collection Error: {filter_final} filter attribute only works for show libraries")
                                    elif filter_final is None:
                                        raise Failed(f"Collection Error: {filter_final} filter attribute is blank")
                                    else:
                                        self.filters.append((filter_final, self.validate_attribute(filter_attr, modifier, f"{filter_final} filter", filter_data, validate)))
                            elif method_name == "plex_collectionless":
                                new_dictionary = {}
                                dict_methods = {dm.lower(): dm for dm in dict_data}
                                prefix_list = []
                                if "exclude_prefix" in dict_methods and dict_data[dict_methods["exclude_prefix"]]:
                                    if isinstance(dict_data[dict_methods["exclude_prefix"]], list):
                                        prefix_list.extend([exclude for exclude in dict_data[dict_methods["exclude_prefix"]] if exclude])
                                    else:
                                        prefix_list.append(str(dict_data[dict_methods["exclude_prefix"]]))
                                exact_list = []
                                if "exclude" in dict_methods and dict_data[dict_methods["exclude"]]:
                                    if isinstance(dict_data[dict_methods["exclude"]], list):
                                        exact_list.extend([exclude for exclude in dict_data[dict_methods["exclude"]] if exclude])
                                    else:
                                        exact_list.append(str(dict_data[dict_methods["exclude"]]))
                                if len(prefix_list) == 0 and len(exact_list) == 0:
                                    raise Failed("Collection Error: you must have at least one exclusion")
                                exact_list.append(self.name)
                                new_dictionary["exclude_prefix"] = prefix_list
                                new_dictionary["exclude"] = exact_list
                                self.methods.append((method_name, [new_dictionary]))
                            elif method_name == "plex_search":
                                self.methods.append((method_name, [self.build_filter("plex_search", dict_data)]))
                            elif method_name == "tmdb_discover":
                                new_dictionary = {"limit": 100}
                                for discover_name, discover_data in dict_data.items():
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
                                                if "certification" in dict_data or "certification.lte" in dict_data or "certification.gte" in dict_data:
                                                    new_dictionary[discover_final] = discover_data
                                                else:
                                                    raise Failed(f"Collection Error: {method_name} attribute {discover_final}: must be used with either certification, certification.lte, or certification.gte")
                                            elif discover_final in ["certification", "certification.lte", "certification.gte"]:
                                                if "certification_country" in dict_data:
                                                    new_dictionary[discover_final] = discover_data
                                                else:
                                                    raise Failed(f"Collection Error: {method_name} attribute {discover_final}: must be used with certification_country")
                                            elif discover_final in ["include_adult", "include_null_first_air_dates", "screened_theatrically"]:
                                                if discover_data is True:
                                                    new_dictionary[discover_final] = discover_data
                                            elif discover_final in tmdb.discover_dates:
                                                new_dictionary[discover_final] = util.check_date(discover_data, f"{method_name} attribute {discover_final}", return_string=True)
                                            elif discover_final in ["primary_release_year", "year", "first_air_date_year"]:
                                                new_dictionary[discover_final] = util.check_number(discover_data, f"{method_name} attribute {discover_final}", minimum=1800, maximum=self.current_year + 1)
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
                                dict_methods = {dm.lower(): dm for dm in dict_data}
                                new_dictionary["list_days"] = get_int(method_name, "list_days", dict_data, dict_methods, 30)
                                new_dictionary["list_size"] = get_int(method_name, "list_size", dict_data, dict_methods, 10)
                                new_dictionary["list_buffer"] = get_int(method_name, "list_buffer", dict_data, dict_methods, 20)
                                self.methods.append((method_name, [new_dictionary]))
                            elif method_name == "mal_season":
                                new_dictionary = {"sort_by": "anime_num_list_users"}
                                dict_methods = {dm.lower(): dm for dm in dict_data}
                                if "sort_by" not in dict_methods:
                                    logger.warning("Collection Warning: mal_season sort_by attribute not found using members as default")
                                elif not dict_data[dict_methods["sort_by"]]:
                                    logger.warning("Collection Warning: mal_season sort_by attribute is blank using members as default")
                                elif dict_data[dict_methods["sort_by"]] not in mal.season_sort:
                                    logger.warning(f"Collection Warning: mal_season sort_by attribute {dict_data[dict_methods['sort_by']]} invalid must be either 'members' or 'score' using members as default")
                                else:
                                    new_dictionary["sort_by"] = mal.season_sort[dict_data[dict_methods["sort_by"]]]

                                if self.current_time.month in [1, 2, 3]:                new_dictionary["season"] = "winter"
                                elif self.current_time.month in [4, 5, 6]:              new_dictionary["season"] = "spring"
                                elif self.current_time.month in [7, 8, 9]:              new_dictionary["season"] = "summer"
                                elif self.current_time.month in [10, 11, 12]:           new_dictionary["season"] = "fall"

                                if "season" not in dict_methods:
                                    logger.warning(f"Collection Warning: mal_season season attribute not found using the current season: {new_dictionary['season']} as default")
                                elif not dict_data[dict_methods["season"]]:
                                    logger.warning(f"Collection Warning: mal_season season attribute is blank using the current season: {new_dictionary['season']} as default")
                                elif dict_data[dict_methods["season"]] not in util.pretty_seasons:
                                    logger.warning(f"Collection Warning: mal_season season attribute {dict_data[dict_methods['season']]} invalid must be either 'winter', 'spring', 'summer' or 'fall' using the current season: {new_dictionary['season']} as default")
                                else:
                                    new_dictionary["season"] = dict_data[dict_methods["season"]]

                                new_dictionary["year"] = get_int(method_name, "year", dict_data, dict_methods, self.current_time.year, minimum=1917, maximum=self.current_time.year + 1)
                                new_dictionary["limit"] = get_int(method_name, "limit", dict_data, dict_methods, 100, maximum=500)
                                self.methods.append((method_name, [new_dictionary]))
                            elif method_name == "mal_userlist":
                                new_dictionary = {"status": "all", "sort_by": "list_score"}
                                dict_methods = {dm.lower(): dm for dm in dict_data}
                                if "username" not in dict_methods:
                                    raise Failed("Collection Error: mal_userlist username attribute is required")
                                elif not dict_data[dict_methods["username"]]:
                                    raise Failed("Collection Error: mal_userlist username attribute is blank")
                                else:
                                    new_dictionary["username"] = dict_data[dict_methods["username"]]

                                if "status" not in dict_methods:
                                    logger.warning("Collection Warning: mal_season status attribute not found using all as default")
                                elif not dict_data[dict_methods["status"]]:
                                    logger.warning("Collection Warning: mal_season status attribute is blank using all as default")
                                elif dict_data[dict_methods["status"]] not in mal.userlist_status:
                                    logger.warning(f"Collection Warning: mal_season status attribute {dict_data[dict_methods['status']]} invalid must be either 'all', 'watching', 'completed', 'on_hold', 'dropped' or 'plan_to_watch' using all as default")
                                else:
                                    new_dictionary["status"] = mal.userlist_status[dict_data[dict_methods["status"]]]

                                if "sort_by" not in dict_methods:
                                    logger.warning("Collection Warning: mal_season sort_by attribute not found using score as default")
                                elif not dict_data[dict_methods["sort_by"]]:
                                    logger.warning("Collection Warning: mal_season sort_by attribute is blank using score as default")
                                elif dict_data[dict_methods["sort_by"]] not in mal.userlist_sort:
                                    logger.warning(f"Collection Warning: mal_season sort_by attribute {dict_data[dict_methods['sort_by']]} invalid must be either 'score', 'last_updated', 'title' or 'start_date' using score as default")
                                else:
                                    new_dictionary["sort_by"] = mal.userlist_sort[dict_data[dict_methods["sort_by"]]]

                                new_dictionary["limit"] = get_int(method_name, "limit", dict_data, dict_methods, 100, maximum=1000)
                                self.methods.append((method_name, [new_dictionary]))
                            elif method_name == "anidb_tag":
                                new_dictionary = {}
                                dict_methods = {dm.lower(): dm for dm in dict_data}
                                if "tag" not in dict_methods:
                                    raise Failed("Collection Error: anidb_tag tag attribute is required")
                                elif not dict_data[dict_methods["tag"]]:
                                    raise Failed("Collection Error: anidb_tag tag attribute is blank")
                                else:
                                    new_dictionary["tag"] = util.regex_first_int(dict_data[dict_methods["username"]], "AniDB Tag ID")
                                new_dictionary["limit"] = get_int(method_name, "limit", dict_data, dict_methods, 0, minimum=0)
                                self.methods.append((method_name, [new_dictionary]))
                            elif "anilist" in method_name:
                                new_dictionary = {"sort_by": "score"}
                                dict_methods = {dm.lower(): dm for dm in dict_data}
                                if method_name == "anilist_season":
                                    if self.current_time.month in [12, 1, 2]:               new_dictionary["season"] = "winter"
                                    elif self.current_time.month in [3, 4, 5]:              new_dictionary["season"] = "spring"
                                    elif self.current_time.month in [6, 7, 8]:              new_dictionary["season"] = "summer"
                                    elif self.current_time.month in [9, 10, 11]:            new_dictionary["season"] = "fall"

                                    if "season" not in dict_methods:
                                        logger.warning(f"Collection Warning: anilist_season season attribute not found using the current season: {new_dictionary['season']} as default")
                                    elif not dict_data[dict_methods["season"]]:
                                        logger.warning(f"Collection Warning: anilist_season season attribute is blank using the current season: {new_dictionary['season']} as default")
                                    elif dict_data[dict_methods["season"]] not in util.pretty_seasons:
                                        logger.warning(f"Collection Warning: anilist_season season attribute {dict_data[dict_methods['season']]} invalid must be either 'winter', 'spring', 'summer' or 'fall' using the current season: {new_dictionary['season']} as default")
                                    else:
                                        new_dictionary["season"] = dict_data[dict_methods["season"]]

                                    new_dictionary["year"] = get_int(method_name, "year", dict_data, dict_methods, self.current_time.year, minimum=1917, maximum=self.current_time.year + 1)
                                elif method_name == "anilist_genre":
                                    if "genre" not in dict_methods:
                                        raise Failed(f"Collection Warning: anilist_genre genre attribute not found")
                                    elif not dict_data[dict_methods["genre"]]:
                                        raise Failed(f"Collection Warning: anilist_genre genre attribute is blank")
                                    else:
                                        new_dictionary["genre"] = self.config.AniList.validate_genre(dict_data[dict_methods["genre"]])
                                elif method_name == "anilist_tag":
                                    if "tag" not in dict_methods:
                                        raise Failed(f"Collection Warning: anilist_tag tag attribute not found")
                                    elif not dict_data[dict_methods["tag"]]:
                                        raise Failed(f"Collection Warning: anilist_tag tag attribute is blank")
                                    else:
                                        new_dictionary["tag"] = self.config.AniList.validate_tag(dict_data[dict_methods["tag"]])

                                if "sort_by" not in dict_methods:
                                    logger.warning(f"Collection Warning: {method_name} sort_by attribute not found using score as default")
                                elif not dict_data[dict_methods["sort_by"]]:
                                    logger.warning(f"Collection Warning: {method_name} sort_by attribute is blank using score as default")
                                elif str(dict_data[dict_methods["sort_by"]]).lower() not in ["score", "popular"]:
                                    logger.warning(f"Collection Warning: {method_name} sort_by attribute {dict_data[dict_methods['sort_by']]} invalid must be either 'score' or 'popular' using score as default")
                                else:
                                    new_dictionary["sort_by"] = dict_data[dict_methods["sort_by"]]

                                new_dictionary["limit"] = get_int(method_name, "limit", dict_data, dict_methods, 0, maximum=500)

                                self.methods.append((method_name, [new_dictionary]))
                        else:
                            raise Failed(f"Collection Error: {method_name} attribute is not a dictionary: {dict_data}")
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

        if self.add_to_radarr is None:
            self.add_to_radarr = self.library.Radarr.add if self.library.Radarr else False
        if self.add_to_sonarr is None:
            self.add_to_sonarr = self.library.Sonarr.add if self.library.Sonarr else False
            
        if self.smart_url:
            self.add_to_radarr = False
            self.add_to_sonarr = False

        if self.collectionless:
            self.add_to_radarr = False
            self.add_to_sonarr = False
            self.details["collection_mode"] = "hide"
            self.sync = True

        if self.build_collection:
            try:
                self.obj = self.library.get_collection(self.name)
                if (self.smart and not self.obj.smart) or (not self.smart and self.obj.smart):
                    logger.info("")
                    logger.error(f"Collection Error: Converting {self.obj.title} to a {'smart' if self.smart else 'normal'} collection")
                    self.library.query(self.obj.delete)
                    self.obj = None
            except Failed:
                self.obj = None

            self.plex_map = {}
            if self.sync and self.obj:
                for item in self.library.get_collection_items(self.obj, self.smart_label_collection):
                    self.plex_map[item.ratingKey] = item
        else:
            self.obj = None
            self.sync = False
            self.run_again = False
        logger.info("")
        logger.info("Validation Successful")

    def collect_rating_keys(self):
        filtered_keys = {}
        name = self.obj.title if self.obj else self.name
        def add_rating_keys(keys):
            if not isinstance(keys, list):
                keys = [keys]
            total = len(keys)
            max_length = len(str(total))
            if self.filters and self.details["show_filtered"] is True:
                logger.info("")
                logger.info("Filtering Builder:")
            for i, key in enumerate(keys, 1):
                if key not in self.rating_keys:
                    if key in filtered_keys:
                        if self.details["show_filtered"] is True:
                            logger.info(f"{name} Collection | X | {filtered_keys[key]}")
                    else:
                        try:
                            current = self.fetch_item(key)
                        except Failed as e:
                            logger.error(e)
                            continue
                        current_title = f"{current.title} ({current.year})" if current.year else current.title
                        if self.check_filters(current, f"{(' ' * (max_length - len(str(i))))}{i}/{total}"):
                            self.rating_keys.append(key)
                        else:
                            if key not in filtered_keys:
                                filtered_keys[key] = current_title
                            if self.details["show_filtered"] is True:
                                logger.info(f"{name} Collection | X | {current_title}")
        def check_map(input_ids):
            movie_ids, show_ids = input_ids
            items_found_inside = 0
            if len(movie_ids) > 0:
                items_found_inside += len(movie_ids)
                for movie_id in movie_ids:
                    if movie_id in self.library.movie_map:
                        add_rating_keys(self.library.movie_map[movie_id])
                    elif movie_id not in self.missing_movies:
                        self.missing_movies.append(movie_id)
            if len(show_ids) > 0:
                items_found_inside += len(show_ids)
                for show_id in show_ids:
                    if show_id in self.library.show_map:
                        add_rating_keys(self.library.show_map[show_id])
                    elif show_id not in self.missing_shows:
                        self.missing_shows.append(show_id)
            return items_found_inside
        for method, values in self.methods:
            for value in values:
                logger.debug("")
                logger.debug(f"Builder: {method}: {value}")
                logger.info("")
                if "plex" in method:                                add_rating_keys(self.library.get_items(method, value))
                elif "tautulli" in method:                          add_rating_keys(self.library.Tautulli.get_items(self.library, value))
                elif "anidb" in method:                             check_map(self.config.AniDB.get_items(method, value, self.library.Plex.language))
                elif "anilist" in method:                           check_map(self.config.AniList.get_items(method, value))
                elif "mal" in method:                               check_map(self.config.MyAnimeList.get_items(method, value))
                elif "tvdb" in method:                              check_map(self.config.TVDb.get_items(method, value, self.library.Plex.language))
                elif "imdb" in method:                              check_map(self.config.IMDb.get_items(method, value, self.library.Plex.language, self.library.is_movie))
                elif "icheckmovies" in method:                      check_map(self.config.ICheckMovies.get_items(method, value, self.library.Plex.language))
                elif "letterboxd" in method:                        check_map(self.config.Letterboxd.get_items(method, value, self.library.Plex.language))
                elif "tmdb" in method:                              check_map(self.config.TMDb.get_items(method, value, self.library.is_movie))
                elif "trakt" in method:                             check_map(self.config.Trakt.get_items(method, value, self.library.is_movie))
                else:                                               logger.error(f"Collection Error: {method} method not supported")

    def build_filter(self, method, plex_filter, smart=False):
        if smart:
            logger.info("")
            logger.info(f"Validating Method: {method}")
        if plex_filter is None:
            raise Failed(f"Collection Error: {method} attribute is blank")
        if not isinstance(plex_filter, dict):
            raise Failed(f"Collection Error: {method} must be a dictionary: {plex_filter}")
        if smart:
            logger.debug(f"Value: {plex_filter}")

        filter_alias = {m.lower(): m for m in plex_filter}

        if "any" in filter_alias and "all" in filter_alias:
            raise Failed(f"Collection Error: Cannot have more then one base")

        if smart and "type" in filter_alias and self.library.is_show:
            if plex_filter[filter_alias["type"]] not in ["shows", "seasons", "episodes"]:
                raise Failed(f"Collection Error: type: {plex_filter[filter_alias['type']]} is invalid, must be either shows, season, or episodes")
            sort_type = plex_filter[filter_alias["type"]]
        elif self.library.is_show:
            sort_type = "shows"
        else:
            sort_type = "movies"
        ms = method.split("_")
        filter_details = f"{ms[0].capitalize()} {sort_type.capitalize()[:-1]} {ms[1].capitalize()}\n"
        type_key, sorts = plex.sort_types[sort_type]

        sort = "random" if smart else "title.asc"
        if "sort_by" in filter_alias:
            if plex_filter[filter_alias["sort_by"]] is None:
                raise Failed(f"Collection Error: sort_by attribute is blank")
            if plex_filter[filter_alias["sort_by"]] not in sorts:
                raise Failed(f"Collection Error: sort_by: {plex_filter[filter_alias['sort_by']]} is invalid")
            sort = plex_filter[filter_alias["sort_by"]]
        filter_details += f"Sort By: {sort}\n"

        limit = None
        if "limit" in filter_alias:
            if plex_filter[filter_alias["limit"]] is None:
                raise Failed("Collection Error: limit attribute is blank")
            if not isinstance(plex_filter[filter_alias["limit"]], int) or plex_filter[filter_alias["limit"]] < 1:
                raise Failed("Collection Error: limit attribute must be an integer greater then 0")
            limit = plex_filter[filter_alias["limit"]]
            filter_details += f"Limit: {limit}\n"

        validate = True
        if "validate" in filter_alias:
            if plex_filter[filter_alias["validate"]] is None:
                raise Failed("Collection Error: validate attribute is blank")
            if not isinstance(plex_filter[filter_alias["validate"]], bool):
                raise Failed("Collection Error: validate attribute must be either true or false")
            validate = plex_filter[filter_alias["validate"]]
            filter_details += f"Validate: {validate}\n"

        def _filter(filter_dict, is_all=True, level=1):
            output = ""
            display = f"\n{'  ' * level}Match {'all' if is_all else 'any'} of the following:"
            level += 1
            indent = f"\n{'  ' * level}"
            conjunction = f"{'and' if is_all else 'or'}=1&"
            for _key, _data in filter_dict.items():
                attr, modifier, final_attr = self._split(_key)

                def build_url_arg(arg, mod=None, arg_s=None, mod_s=None):
                    arg_key = plex.search_translation[attr] if attr in plex.search_translation else attr
                    if mod is None:
                        mod = plex.modifier_translation[modifier] if modifier in plex.modifier_translation else modifier
                    if arg_s is None:
                        arg_s = arg
                    if attr in string_filters and modifier in ["", ".not"]:
                        mod_s = "does not contain" if modifier == ".not" else "contains"
                    elif mod_s is None:
                        mod_s = plex.mod_displays[modifier]
                    param_s = plex.search_display[attr] if attr in plex.search_display else attr.title().replace('_', ' ')
                    display_line = f"{indent}{param_s} {mod_s} {arg_s}"
                    return f"{arg_key}{mod}={arg}&", display_line

                if final_attr not in plex.searches and not final_attr.startswith(("any", "all")):
                    raise Failed(f"Collection Error: {final_attr} is not a valid {method} attribute")
                elif final_attr in plex.movie_only_searches and self.library.is_show:
                    raise Failed(f"Collection Error: {final_attr} {method} attribute only works for movie libraries")
                elif final_attr in plex.show_only_searches and self.library.is_movie:
                    raise Failed(f"Collection Error: {final_attr} {method} attribute only works for show libraries")
                elif _data is None:
                    raise Failed(f"Collection Error: {final_attr} {method} attribute is blank")
                elif final_attr.startswith(("any", "all")):
                    dicts = util.get_list(_data)
                    results = ""
                    display_add = ""
                    for dict_data in dicts:
                        if not isinstance(dict_data, dict):
                            raise Failed(f"Collection Error: {attr} must be either a dictionary or list of dictionaries")
                        inside_filter, inside_display = _filter(dict_data, is_all=attr == "all", level=level)
                        if len(inside_filter) > 0:
                            display_add += inside_display
                            results += f"{conjunction if len(results) > 0 else ''}push=1&{inside_filter}pop=1&"
                else:
                    validation = self.validate_attribute(attr, modifier, final_attr, _data, validate, pairs=True)
                    if validation is None:
                        continue
                    elif attr in plex.date_attributes and modifier in ["", ".not"]:
                        last_text = "is not in the last" if modifier == ".not" else "is in the last"
                        last_mod = "%3E%3E" if modifier == "" else "%3C%3C"
                        results, display_add = build_url_arg(f"-{validation}d", mod=last_mod, arg_s=f"{validation} Days", mod_s=last_text)
                    elif attr == "duration" and modifier in [".gt", ".gte", ".lt", ".lte"]:
                        results, display_add = build_url_arg(validation * 60000)
                    elif attr in plex.boolean_attributes:
                        bool_mod = "" if validation else "!"
                        bool_arg = "true" if validation else "false"
                        results, display_add = build_url_arg(1, mod=bool_mod, arg_s=bool_arg, mod_s="is")
                    elif (attr in ["title", "episode_title", "studio", "decade", "year", "episode_year"] or attr in plex.tags) and modifier in ["", ".not", ".begins", ".ends"]:
                        results = ""
                        display_add = ""
                        for og_value, result in validation:
                            built_arg = build_url_arg(quote(result) if attr in string_filters else result, arg_s=og_value)
                            display_add += built_arg[1]
                            results += f"{conjunction if len(results) > 0 else ''}{built_arg[0]}"
                    else:
                        results, display_add = build_url_arg(validation)
                display += display_add
                output += f"{conjunction if len(output) > 0 else ''}{results}"
            return output, display

        if "any" not in filter_alias and "all" not in filter_alias:
            base_dict = {}
            any_dicts = []
            for alias_key, alias_value in filter_alias.items():
                _, _, final = self._split(alias_key)
                if final in plex.and_searches:
                    base_dict[alias_value[:-4]] = plex_filter[alias_value]
                elif final in plex.or_searches:
                    any_dicts.append({alias_value: plex_filter[alias_value]})
                elif final in plex.searches:
                    base_dict[alias_value] = plex_filter[alias_value]
            if len(any_dicts) > 0:
                base_dict["any"] = any_dicts
            base_all = True
            if len(base_dict) == 0:
                raise Failed(f"Collection Error: Must have either any or all as a base for {method}")
        else:
            base = "all" if "all" in filter_alias else "any"
            base_all = base == "all"
            if plex_filter[filter_alias[base]] is None:
                raise Failed(f"Collection Error: {base} attribute is blank")
            if not isinstance(plex_filter[filter_alias[base]], dict):
                raise Failed(f"Collection Error: {base} must be a dictionary: {plex_filter[filter_alias[base]]}")
            base_dict = plex_filter[filter_alias[base]]
        built_filter, filter_text = _filter(base_dict, is_all=base_all)
        filter_details = f"{filter_details}Filter:{filter_text}"
        if len(built_filter) > 0:
            final_filter = built_filter[:-1] if base_all else f"push=1&{built_filter}pop=1"
            filter_url = f"?type={type_key}&{f'limit={limit}&' if limit else ''}sort={sorts[sort]}&{final_filter}"
        else:
            raise Failed("Collection Error: No Filter Created")

        return type_key, filter_details, filter_url

    def validate_attribute(self, attribute, modifier, final, data, validate, pairs=False):
        def smart_pair(list_to_pair):
            return [(t, t) for t in list_to_pair] if pairs else list_to_pair
        if modifier == ".regex":
            regex_list = util.get_list(data, split=False)
            valid_regex = []
            for reg in regex_list:
                try:
                    re.compile(reg)
                    valid_regex.append(reg)
                except re.error:
                    util.print_stacktrace()
                    err = f"Collection Error: Regular Expression Invalid: {reg}"
                    if validate:
                        raise Failed(err)
                    else:
                        logger.error(err)
            return valid_regex
        elif attribute in ["title", "studio", "episode_title", "audio_track_title"] and modifier in ["", ".not", ".begins", ".ends"]:
            return smart_pair(util.get_list(data, split=False))
        elif attribute == "original_language":
            return util.get_list(data, lower=True)
        elif attribute == "filepath":
            return util.get_list(data)
        elif attribute == "history":
            try:
                return util.check_number(data, final, minimum=1, maximum=30)
            except Failed:
                if str(data).lower() in ["day", "month"]:
                    return data.lower()
            raise Failed(f"Collection Error: history attribute invalid: {data} must be a number between 1-30, day, or month")
        elif attribute in plex.tags and modifier in ["", ".not"]:
            if attribute in plex.tmdb_attributes:
                final_values = []
                for value in util.get_list(data):
                    if value.lower() == "tmdb" and "tmdb_person" in self.details:
                        for name in self.details["tmdb_person"]:
                            final_values.append(name)
                    else:
                        final_values.append(value)
            else:
                final_values = util.get_list(data)
            search_choices = self.library.get_search_choices(attribute, title=not pairs)
            valid_list = []
            for value in final_values:
                if str(value).lower() in search_choices:
                    if pairs:
                        valid_list.append((value, search_choices[str(value).lower()]))
                    else:
                        valid_list.append(search_choices[str(value).lower()])
                else:
                    error = f"Plex Error: {attribute}: {value} not found"
                    if validate:
                        raise Failed(error)
                    else:
                        logger.error(error)
            return valid_list
        elif attribute in ["year", "episode_year"] and modifier in [".gt", ".gte", ".lt", ".lte"]:#
            return util.check_year(data, self.current_year, final)
        elif attribute in plex.date_attributes and modifier in [".before", ".after"]:#
            return util.check_date(data, final, return_string=True, plex_date=True)
        elif attribute in plex.number_attributes and modifier in ["", ".not", ".gt", ".gte", ".lt", ".lte"]:
            return util.check_number(data, final, minimum=1)
        elif attribute in plex.float_attributes and modifier in [".gt", ".gte", ".lt", ".lte"]:
            return util.check_number(data, final, number_type="float", minimum=0, maximum=10)
        elif attribute in ["decade", "year", "episode_year"] and modifier in ["", ".not"]:
            return smart_pair(util.get_year_list(data, self.current_year, final))
        elif attribute in plex.boolean_attributes:
            return util.get_bool(attribute, data)
        else:
            raise Failed(f"Collection Error: {final} attribute not supported")

    def _split(self, text):
        attribute, modifier = os.path.splitext(str(text).lower())
        attribute = method_alias[attribute] if attribute in method_alias else attribute
        modifier = modifier_alias[modifier] if modifier in modifier_alias else modifier

        if attribute == "add_to_arr":
            attribute = "radarr_add" if self.library.is_movie else "sonarr_add"
        elif attribute in ["arr_tag", "arr_folder"]:
            attribute = f"{'rad' if self.library.is_movie else 'son'}{attribute}"
        elif attribute in plex.date_attributes and modifier in [".gt", ".gte"]:
            modifier = ".after"
        elif attribute in plex.date_attributes and modifier in [".lt", ".lte"]:
            modifier = ".before"
        final = f"{attribute}{modifier}"
        if text != final:
            logger.warning(f"Collection Warning: {text} attribute will run as {final}")
        return attribute, modifier, final

    def fetch_item(self, item):
        try:
            current = self.library.fetchItem(item.ratingKey if isinstance(item, (Movie, Show)) else int(item))
            if not isinstance(current, (Movie, Show)):
                raise NotFound
            return current
        except (BadRequest, NotFound):
            raise Failed(f"Plex Error: Item {item} not found")

    def add_to_collection(self):
        name, collection_items = self.library.get_collection_name_and_items(self.obj if self.obj else self.name, self.smart_label_collection)
        total = len(self.rating_keys)
        for i, item in enumerate(self.rating_keys, 1):
            try:
                current = self.fetch_item(item)
            except Failed as e:
                logger.error(e)
                continue
            current_title = f"{current.title} ({current.year})" if current.year else current.title
            current_operation = "=" if current in collection_items else "+"
            logger.info(util.adjust_space(f"{name} Collection | {current_operation} | {current_title}"))
            if current in collection_items:
                self.plex_map[current.ratingKey] = None
            elif self.smart_label_collection:
                self.library.query_data(current.addLabel, name)
            else:
                self.library.query_data(current.addCollection, name)
        media_type = f"{'Movie' if self.library.is_movie else 'Show'}{'s' if total > 1 else ''}"
        util.print_end()
        logger.info("")
        logger.info(f"{total} {media_type} Processed")

    def check_filters(self, current, display):
        if self.filters:
            util.print_return(f"Filtering {display} {current.title}")
            current_date = datetime.now()
            for filter_method, filter_data in self.filters:
                filter_attr, modifier, filter_final = self._split(filter_method)
                filter_actual = filter_translation[filter_attr] if filter_attr in filter_translation else filter_attr
                if filter_attr in ["release", "added", "last_played"] and modifier != ".regex":
                    current_data = getattr(current, filter_actual)
                    if modifier in ["", ".not"]:
                        threshold_date = current_date - timedelta(days=filter_data)
                        if (modifier == "" and (current_data is None or current_data < threshold_date)) \
                                or (modifier == ".not" and current_data and current_data >= threshold_date):
                            return False
                    elif (modifier == ".before" and (current_data is None or current_data >= filter_data)) \
                            or (modifier == ".after" and (current_data is None or current_data <= filter_data)):
                        return False
                elif filter_attr in ["release", "added", "last_played"] and modifier == ".regex":
                    jailbreak = False
                    current_data = getattr(current, filter_actual)
                    if current_data is None:
                        return False
                    for check_data in filter_data:
                        if re.compile(check_data).match(current_data.strftime("%m/%d/%Y")):
                            jailbreak = True
                            break
                    if not jailbreak:
                        return False
                elif filter_attr == "audio_track_title":
                    jailbreak = False
                    for media in current.media:
                        for part in media.parts:
                            for audio in part.audioStreams():
                                for check_title in filter_data:
                                    title = audio.title if audio.title else ""
                                    if (modifier in ["", ".not"] and check_title.lower() in title.lower()) \
                                            or (modifier == ".begins" and title.lower().startswith(check_title.lower())) \
                                            or (modifier == ".ends" and title.lower().endswith(check_title.lower())) \
                                            or (modifier == ".regex" and re.compile(check_title).match(title)):
                                        jailbreak = True
                                        break
                                if jailbreak: break
                            if jailbreak: break
                        if jailbreak: break
                    if (jailbreak and modifier == ".not") or (not jailbreak and modifier in ["", ".begins", ".ends", ".regex"]):
                        return False
                elif filter_attr == "filepath":
                    jailbreak = False
                    for location in current.locations:
                        for check_text in filter_data:
                            if (modifier in ["", ".not"] and check_text.lower() in location.lower()) \
                                    or (modifier == ".begins" and location.lower().startswith(check_text.lower())) \
                                    or (modifier == ".ends" and location.lower().endswith(check_text.lower())) \
                                    or (modifier == ".regex" and re.compile(check_text).match(location)):
                                jailbreak = True
                                break
                        if jailbreak: break
                    if (jailbreak and modifier == ".not") or (not jailbreak and modifier in ["", ".begins", ".ends", ".regex"]):
                        return False
                elif filter_attr in ["title", "studio"]:
                    jailbreak = False
                    current_data = getattr(current, filter_actual)
                    for check_data in filter_data:
                        if (modifier in ["", ".not"] and check_data.lower() in current_data.lower()) \
                                or (modifier == ".begins" and current_data.lower().startswith(check_data.lower())) \
                                or (modifier == ".ends" and current_data.lower().endswith(check_data.lower())) \
                                or (modifier == ".regex" and re.compile(check_data).match(current_data)):
                            jailbreak = True
                            break
                    if (jailbreak and modifier == ".not") or (not jailbreak and modifier in ["", ".begins", ".ends", ".regex"]):
                        return False
                elif filter_attr == "history":
                    item_date = current.originallyAvailableAt
                    if item_date is None:
                        return False
                    elif filter_data == "day":
                        if item_date.month != current_date.month or item_date.day != current_date.day:
                            return False
                    elif filter_data == "month":
                        if item_date.month != current_date.month:
                            return False
                    else:
                        date_match = False
                        for i in range(filter_data):
                            check_date = current_date - timedelta(days=i)
                            if item_date.month == check_date.month and item_date.day == check_date.day:
                                date_match = True
                        if date_match is False:
                            return False
                elif filter_attr == "original_language":
                    movie = None
                    for key, value in self.library.movie_map.items():
                        if current.ratingKey in value:
                            try:
                                movie = self.config.TMDb.get_movie(key)
                                break
                            except Failed:
                                pass
                    if movie is None:
                        logger.warning(f"Filter Error: No TMDb ID found for {current.title}")
                        continue
                    if (modifier == ".not" and movie.original_language in filter_data) \
                            or (modifier == "" and movie.original_language not in filter_data):
                        return False
                elif modifier in [".gt", ".gte", ".lt", ".lte"]:
                    if filter_attr == "tmdb_vote_count":
                        tmdb_item = None
                        for key, value in self.library.movie_map.items():
                            if current.ratingKey in value:
                                try:
                                    tmdb_item = self.config.TMDb.get_movie(key) if self.library.is_movie else self.config.TMDb.get_show(key)
                                    break
                                except Failed:
                                    pass
                        if tmdb_item is None:
                            logger.warning(f"Filter Error: No TMDb ID found for {current.title}")
                            continue
                        attr = tmdb_item.vote_count
                    elif filter_attr == "duration":
                        attr = getattr(current, filter_actual) / 60000
                    else:
                        attr = getattr(current, filter_actual)
                    if attr is None or (modifier == ".gt" and attr <= filter_data) \
                            or (modifier == ".gte" and attr < filter_data) \
                            or (modifier == ".lt" and attr >= filter_data) \
                            or (modifier == ".lte" and attr > filter_data):
                        return False
                else:
                    attrs = []
                    if filter_attr in ["resolution", "audio_language", "subtitle_language"]:
                        for media in current.media:
                            if filter_attr == "resolution":
                                attrs.extend([media.videoResolution])
                            for part in media.parts:
                                if filter_attr == "audio_language":
                                    attrs.extend([a.language for a in part.audioStreams()])
                                if filter_attr == "subtitle_language":
                                    attrs.extend([s.language for s in part.subtitleStreams()])
                    elif filter_attr in ["content_rating", "year", "rating"]:
                        attrs = [str(getattr(current, filter_actual))]
                    elif filter_attr in ["actor", "country", "director", "genre", "label", "producer", "writer", "collection"]:
                        attrs = [attr.tag for attr in getattr(current, filter_actual)]
                    else:
                        raise Failed(f"Filter Error: filter: {filter_final} not supported")

                    if (not list(set(filter_data) & set(attrs)) and modifier == "") \
                            or (list(set(filter_data) & set(attrs)) and modifier == ".not"):
                        return False
            util.print_return(f"Filtering {display} {current.title}")
        return True

    def run_missing(self):
        arr_filters = []
        for filter_method, filter_data in self.filters:
            if (filter_method.startswith("original_language") and self.library.is_movie) or filter_method.startswith("tmdb_vote_count"):
                arr_filters.append((filter_method, filter_data))
        if len(self.missing_movies) > 0:
            missing_movies_with_names = []
            for missing_id in self.missing_movies:
                try:
                    movie = self.config.TMDb.get_movie(missing_id)
                except Failed as e:
                    logger.error(e)
                    continue
                match = True
                for filter_method, filter_data in arr_filters:
                    if (filter_method == "original_language" and movie.original_language not in filter_data) \
                            or (filter_method == "original_language.not" and movie.original_language in filter_data) \
                            or (filter_method == "tmdb_vote_count.gt" and movie.vote_count <= filter_data) \
                            or (filter_method == "tmdb_vote_count.gte" and movie.vote_count < filter_data) \
                            or (filter_method == "tmdb_vote_count.lt" and movie.vote_count >= filter_data) \
                            or (filter_method == "tmdb_vote_count.lte" and movie.vote_count > filter_data):
                        match = False
                        break
                current_title = f"{movie.title} ({util.check_date(movie.release_date, 'test', plex_date=True).year})" if movie.release_date else movie.title
                if match:
                    missing_movies_with_names.append((current_title, missing_id))
                    if self.details["show_missing"] is True:
                        logger.info(f"{self.name} Collection | ? | {current_title} (TMDb: {missing_id})")
                elif self.details["show_filtered"] is True:
                    logger.info(f"{self.name} Collection | X | {current_title} (TMDb: {missing_id})")
            logger.info("")
            logger.info(f"{len(missing_movies_with_names)} Movie{'s' if len(missing_movies_with_names) > 1 else ''} Missing")
            if self.details["save_missing"] is True:
                self.library.add_missing(self.name, missing_movies_with_names, True)
            if (self.add_to_radarr and self.library.Radarr) or self.run_again:
                missing_tmdb_ids = [missing_id for title, missing_id in missing_movies_with_names]
                if self.add_to_radarr and self.library.Radarr:
                    try:
                        self.library.Radarr.add_tmdb(missing_tmdb_ids, **self.radarr_options)
                    except Failed as e:
                        logger.error(e)
                if self.run_again:
                    self.run_again_movies.extend(missing_tmdb_ids)
        if len(self.missing_shows) > 0 and self.library.is_show:
            missing_shows_with_names = []
            for missing_id in self.missing_shows:
                try:
                    title = str(self.config.TVDb.get_series(self.library.Plex.language, missing_id).title.encode("ascii", "replace").decode())
                except Failed as e:
                    logger.error(e)
                    continue
                match = True
                if arr_filters:
                    show = self.config.TMDb.get_show(self.config.Convert.tvdb_to_tmdb(missing_id))
                    for filter_method, filter_data in arr_filters:
                        if (filter_method == "tmdb_vote_count.gt" and show.vote_count <= filter_data) \
                                or (filter_method == "tmdb_vote_count.gte" and show.vote_count < filter_data) \
                                or (filter_method == "tmdb_vote_count.lt" and show.vote_count >= filter_data) \
                                or (filter_method == "tmdb_vote_count.lte" and show.vote_count > filter_data):
                            match = False
                            break
                if match:
                    missing_shows_with_names.append((title, missing_id))
                    if self.details["show_missing"] is True:
                        logger.info(f"{self.name} Collection | ? | {title} (TVDB: {missing_id})")
                elif self.details["show_filtered"] is True:
                    logger.info(f"{self.name} Collection | X | {title} (TVDb: {missing_id})")
            logger.info("")
            logger.info(f"{len(missing_shows_with_names)} Show{'s' if len(missing_shows_with_names) > 1 else ''} Missing")
            if self.details["save_missing"] is True:
                self.library.add_missing(self.name, missing_shows_with_names, False)
            if (self.add_to_sonarr and self.library.Sonarr) or self.run_again:
                missing_tvdb_ids = [missing_id for title, missing_id in missing_shows_with_names]
                if self.add_to_sonarr and self.library.Sonarr:
                    try:
                        self.library.Sonarr.add_tvdb(missing_tvdb_ids, **self.sonarr_options)
                    except Failed as e:
                        logger.error(e)
                if self.run_again:
                    self.run_again_shows.extend(missing_tvdb_ids)

    def sync_collection(self):
        count_removed = 0
        for ratingKey, item in self.plex_map.items():
            if item is not None:
                if count_removed == 0:
                    logger.info("")
                    util.separator(f"Removed from {self.name} Collection", space=False, border=False)
                    logger.info("")
                self.library.reload(item)
                logger.info(f"{self.name} Collection | - | {item.title}")
                if self.smart_label_collection:
                    self.library.query_data(item.removeLabel, self.name)
                else:
                    self.library.query_data(item.removeCollection, self.name)
                count_removed += 1
        if count_removed > 0:
            logger.info("")
            logger.info(f"{count_removed} {'Movie' if self.library.is_movie else 'Show'}{'s' if count_removed == 1 else ''} Removed")

    def update_item_details(self):
        add_tags = self.item_details["item_label"] if "item_label" in self.item_details else None
        remove_tags = self.item_details["item_label.remove"] if "item_label.remove" in self.item_details else None
        sync_tags = self.item_details["item_label.sync"] if "item_label.sync" in self.item_details else None

        if self.build_collection:
            items = self.library.get_collection_items(self.obj, self.smart_label_collection)
        else:
            items = []
            for rk in self.rating_keys:
                try:
                    items.append(self.fetch_item(rk))
                except Failed as e:
                    logger.error(e)

        overlay = None
        overlay_folder = None
        rating_keys = []
        if "item_overlay" in self.item_details:
            overlay_name = self.item_details["item_overlay"]
            if self.config.Cache:
                rating_keys = self.config.Cache.query_image_map_overlay(self.library.original_mapping_name, "poster", overlay_name)
            overlay_folder = os.path.join(self.config.default_dir, "overlays", overlay_name)
            overlay_image = Image.open(os.path.join(overlay_folder, "overlay.png"))
            temp_image = os.path.join(overlay_folder, f"temp.png")
            overlay = (overlay_name, overlay_folder, overlay_image, temp_image)

        tmdb_ids = []
        tvdb_ids = []
        for item in items:
            if int(item.ratingKey) in rating_keys:
                rating_keys.remove(int(item.ratingKey))
            if self.details["item_assets"] or overlay is not None:
                try:
                    self.library.update_item_from_assets(item, overlay=overlay)
                except Failed as e:
                    logger.error(e)
            self.library.edit_tags("label", item, add_tags=add_tags, remove_tags=remove_tags, sync_tags=sync_tags)
            if "item_radarr_tag" in self.item_details and item.ratingKey in self.library.movie_rating_key_map:
                tmdb_ids.append(self.library.movie_rating_key_map[item.ratingKey])
            if "item_sonarr_tag" in self.item_details and item.ratingKey in self.library.show_rating_key_map:
                tvdb_ids.append(self.library.show_rating_key_map[item.ratingKey])
            advance_edits = {}
            for method_name, method_data in self.item_details.items():
                if method_name in plex.item_advance_keys:
                    key, options = plex.item_advance_keys[method_name]
                    if getattr(item, key) != options[method_data]:
                        advance_edits[key] = options[method_data]
            self.library.edit_item(item, item.title, "Movie" if self.library.is_movie else "Show", advance_edits, advanced=True)

        if len(tmdb_ids) > 0:
            self.library.Radarr.edit_tags(tmdb_ids, self.item_details["item_radarr_tag"], self.item_details["apply_tags"])

        if len(tvdb_ids) > 0:
            self.library.Sonarr.edit_tags(tvdb_ids, self.item_details["item_sonarr_tag"], self.item_details["apply_tags"])

        for rating_key in rating_keys:
            try:
                item = self.fetch_item(rating_key)
            except Failed as e:
                logger.error(e)
                continue
            og_image = os.path.join(overlay_folder, f"{rating_key}.png")
            if os.path.exists(og_image):
                self.library.upload_file_poster(item, og_image)
                os.remove(og_image)
                self.config.Cache.update_image_map(item.ratingKey, self.library.original_mapping_name, "poster", "", "", "")

    def update_details(self):
        if not self.obj and self.smart_url:
            self.library.create_smart_collection(self.name, self.smart_type_key, self.smart_url)
        elif self.smart_label_collection:
            try:
                smart_type, self.smart_url = self.library.smart_label_url(self.name, self.smart_sort)
                if not self.obj:
                    self.library.create_smart_collection(self.name, smart_type, self.smart_url)
            except Failed:
                raise Failed(f"Collection Error: Label: {self.name} was not added to any items in the Library")
        self.obj = self.library.get_collection(self.name)

        if self.smart_url and self.smart_url != self.library.smart_filter(self.obj):
            self.library.update_smart_collection(self.obj, self.smart_url)
            logger.info(f"Detail: Smart Filter updated to {self.smart_url}")

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
        elif "letterboxd_list_details" in self.summaries:   summary = get_summary("letterboxd_list_details", self.summaries)
        elif "icheckmovies_list_details" in self.summaries: summary = get_summary("icheckmovies_list_details", self.summaries)
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
            if str(summary) != str(self.obj.summary):
                edits["summary.value"] = summary
                edits["summary.locked"] = 1

        if "sort_title" in self.details:
            if str(self.details["sort_title"]) != str(self.obj.titleSort):
                edits["titleSort.value"] = self.details["sort_title"]
                edits["titleSort.locked"] = 1
                logger.info(f"Detail: sort_title updated Collection Sort Title to {self.details['sort_title']}")

        if "content_rating" in self.details:
            if str(self.details["content_rating"]) != str(self.obj.contentRating):
                edits["contentRating.value"] = self.details["content_rating"]
                edits["contentRating.locked"] = 1
                logger.info(f"Detail: content_rating updated Collection Content Rating to {self.details['content_rating']}")

        if "collection_mode" in self.details:
            if int(self.obj.collectionMode) not in plex.collection_mode_keys\
                    or plex.collection_mode_keys[int(self.obj.collectionMode)] != self.details["collection_mode"]:
                self.library.collection_mode_query(self.obj, self.details["collection_mode"])
                logger.info(f"Detail: collection_mode updated Collection Mode to {self.details['collection_mode']}")

        if "collection_order" in self.details:
            if int(self.obj.collectionSort) not in plex.collection_order_keys\
                    or plex.collection_order_keys[int(self.obj.collectionSort)] != self.details["collection_order"]:
                self.library.collection_order_query(self.obj, self.details["collection_order"])
                logger.info(f"Detail: collection_order updated Collection Order to {self.details['collection_order']}")

        if "visible_library" in self.details or "visible_home" in self.details or "visible_shared" in self.details:
            visibility = self.library.collection_visibility(self.obj)
            visible_library = None
            visible_home = None
            visible_shared = None

            if "visible_library" in self.details and self.details["visible_library"] != visibility["library"]:
                visible_library = self.details["visible_library"]

            if "visible_home" in self.details and self.details["visible_home"] != visibility["library"]:
                visible_home = self.details["visible_home"]

            if "visible_shared" in self.details and self.details["visible_shared"] != visibility["library"]:
                visible_shared = self.details["visible_shared"]

            if visible_library is not None or visible_home is not None or visible_shared is not None:
                self.library.collection_visibility_update(self.obj, visibility=visibility, library=visible_library, home=visible_home, shared=visible_shared)
                logger.info("Detail: Collection visibility updated")

        add_tags = self.details["label"] if "label" in self.details else None
        remove_tags = self.details["label.remove"] if "label.remove" in self.details else None
        sync_tags = self.details["label.sync"] if "label.sync" in self.details else None
        self.library.edit_tags("label", self.obj, add_tags=add_tags, remove_tags=remove_tags, sync_tags=sync_tags)

        if len(edits) > 0:
            logger.debug(edits)
            self.library.edit_query(self.obj, edits)
            logger.info("Details: have been updated")

        if self.library.asset_directory:
            name_mapping = self.name
            if "name_mapping" in self.details:
                if self.details["name_mapping"]:                    name_mapping = self.details["name_mapping"]
                else:                                               logger.error("Collection Error: name_mapping attribute is blank")
            poster_image, background_image = self.library.find_collection_assets(self.obj, name=name_mapping)
            if poster_image:
                self.posters["asset_directory"] = poster_image
            if background_image:
                self.backgrounds["asset_directory"] = background_image

        poster = None
        if len(self.posters) > 0:
            logger.debug(f"{len(self.posters)} posters found:")
            for p in self.posters:
                logger.debug(f"Method: {p} Poster: {self.posters[p]}")

            if "url_poster" in self.posters:                    poster = ImageData("url_poster", self.posters["url_poster"])
            elif "file_poster" in self.posters:                 poster = ImageData("file_poster", self.posters["file_poster"], is_url=False)
            elif "tmdb_poster" in self.posters:                 poster = ImageData("tmdb_poster", self.posters["tmdb_poster"])
            elif "tmdb_profile" in self.posters:                poster = ImageData("tmdb_poster", self.posters["tmdb_profile"])
            elif "tvdb_poster" in self.posters:                 poster = ImageData("tvdb_poster", self.posters["tvdb_poster"])
            elif "asset_directory" in self.posters:             poster = self.posters["asset_directory"]
            elif "tmdb_person" in self.posters:                 poster = ImageData("tmdb_person", self.posters["tmdb_person"])
            elif "tmdb_collection_details" in self.posters:     poster = ImageData("tmdb_collection_details", self.posters["tmdb_collection_details"])
            elif "tmdb_actor_details" in self.posters:          poster = ImageData("tmdb_actor_details", self.posters["tmdb_actor_details"])
            elif "tmdb_crew_details" in self.posters:           poster = ImageData("tmdb_crew_details", self.posters["tmdb_crew_details"])
            elif "tmdb_director_details" in self.posters:       poster = ImageData("tmdb_director_details", self.posters["tmdb_director_details"])
            elif "tmdb_producer_details" in self.posters:       poster = ImageData("tmdb_producer_details", self.posters["tmdb_producer_details"])
            elif "tmdb_writer_details" in self.posters:         poster = ImageData("tmdb_writer_details", self.posters["tmdb_writer_details"])
            elif "tmdb_movie_details" in self.posters:          poster = ImageData("tmdb_movie_details", self.posters["tmdb_movie_details"])
            elif "tvdb_movie_details" in self.posters:          poster = ImageData("tvdb_movie_details", self.posters["tvdb_movie_details"])
            elif "tvdb_show_details" in self.posters:           poster = ImageData("tvdb_show_details", self.posters["tvdb_show_details"])
            elif "tmdb_show_details" in self.posters:           poster = ImageData("tmdb_show_details", self.posters["tmdb_show_details"])
        else:
            logger.info("No poster collection detail or asset folder found")

        background = None
        if len(self.backgrounds) > 0:
            logger.debug(f"{len(self.backgrounds)} backgrounds found:")
            for b in self.backgrounds:
                logger.debug(f"Method: {b} Background: {self.backgrounds[b]}")

            if "url_background" in self.backgrounds:            background = ImageData("url_background", self.backgrounds["url_background"], is_poster=False)
            elif "file_background" in self.backgrounds:         background = ImageData("file_background", self.backgrounds["file_background"], is_poster=False, is_url=False)
            elif "tmdb_background" in self.backgrounds:         background = ImageData("tmdb_background", self.backgrounds["tmdb_background"], is_poster=False)
            elif "tvdb_background" in self.backgrounds:         background = ImageData("tvdb_background", self.backgrounds["tvdb_background"], is_poster=False)
            elif "asset_directory" in self.backgrounds:         background = self.backgrounds["asset_directory"]
            elif "tmdb_collection_details" in self.backgrounds: background = ImageData("tmdb_collection_details", self.backgrounds["tmdb_collection_details"], is_poster=False)
            elif "tmdb_movie_details" in self.backgrounds:      background = ImageData("tmdb_movie_details", self.backgrounds["tmdb_movie_details"], is_poster=False)
            elif "tvdb_movie_details" in self.backgrounds:      background = ImageData("tvdb_movie_details", self.backgrounds["tvdb_movie_details"], is_poster=False)
            elif "tvdb_show_details" in self.backgrounds:       background = ImageData("tvdb_show_details", self.backgrounds["tvdb_show_details"], is_poster=False)
            elif "tmdb_show_details" in self.backgrounds:       background = ImageData("tmdb_show_details", self.backgrounds["tmdb_show_details"], is_poster=False)
        else:
            logger.info("No background collection detail or asset folder found")

        if poster or background:
            self.library.upload_images(self.obj, poster=poster, background=background)

    def run_collections_again(self):
        self.obj = self.library.get_collection(self.name)
        name, collection_items = self.library.get_collection_name_and_items(self.obj, self.smart_label_collection)
        rating_keys = []
        for mm in self.run_again_movies:
            if mm in self.library.movie_map:
                rating_keys.extend(self.library.movie_map[mm])
        if self.library.is_show:
            for sm in self.run_again_shows:
                if sm in self.library.show_map:
                    rating_keys.extend(self.library.show_map[sm])
        if len(rating_keys) > 0:
            for rating_key in rating_keys:
                try:
                    current = self.library.fetchItem(int(rating_key))
                except (BadRequest, NotFound):
                    logger.error(f"Plex Error: Item {rating_key} not found")
                    continue
                current_title = f"{current.title} ({current.year})" if current.year else current.title
                if current in collection_items:
                    logger.info(f"{name} Collection | = | {current_title}")
                else:
                    self.library.query_data(current.addLabel if self.smart_label_collection else current.addCollection, name)
                    logger.info(f"{name} Collection | + | {current_title}")
            logger.info(f"{len(rating_keys)} {'Movie' if self.library.is_movie else 'Show'}{'s' if len(rating_keys) > 1 else ''} Processed")

        if len(self.run_again_movies) > 0:
            logger.info("")
            for missing_id in self.run_again_movies:
                if missing_id not in self.library.movie_map:
                    try:
                        movie = self.config.TMDb.get_movie(missing_id)
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.details["show_missing"] is True:
                        current_title = f"{movie.title} ({util.check_date(movie.release_date, 'test', plex_date=True).year})" if movie.release_date else movie.title
                        logger.info(f"{name} Collection | ? | {current_title} (TMDb: {missing_id})")
            logger.info("")
            logger.info(f"{len(self.run_again_movies)} Movie{'s' if len(self.run_again_movies) > 1 else ''} Missing")

        if len(self.run_again_shows) > 0 and self.library.is_show:
            logger.info("")
            for missing_id in self.run_again_shows:
                if missing_id not in self.library.show_map:
                    try:
                        title = str(self.config.TVDb.get_series(self.library.Plex.language, missing_id).title.encode("ascii", "replace").decode())
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.details["show_missing"] is True:
                        logger.info(f"{name} Collection | ? | {title} (TVDb: {missing_id})")
            logger.info(f"{len(self.run_again_shows)} Show{'s' if len(self.run_again_shows) > 1 else ''} Missing")
