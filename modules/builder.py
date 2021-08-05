import logging, os, re
from datetime import datetime, timedelta
from modules import anidb, anilist, icheckmovies, imdb, letterboxd, mal, plex, radarr, sonarr, stevenlu, tautulli, tmdb, trakt, tvdb, util
from modules.util import Failed, ImageData
from PIL import Image
from plexapi.exceptions import BadRequest, NotFound
from plexapi.video import Movie, Show
from urllib.parse import quote

logger = logging.getLogger("Plex Meta Manager")

string_filters = ["title", "episode_title", "studio"]
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
all_builders = anidb.builders + anilist.builders + icheckmovies.builders + imdb.builders + letterboxd.builders + \
               mal.builders + plex.builders + stevenlu.builders + tautulli.builders + tmdb.builders + trakt.builders + tvdb.builders
show_only_builders = ["tmdb_network", "tmdb_show", "tmdb_show_details", "tvdb_show", "tvdb_show_details"]
movie_only_builders = [
    "letterboxd_list", "letterboxd_list_details", "icheckmovies_list", "icheckmovies_list_details", "stevenlu_popular",
    "tmdb_collection", "tmdb_collection_details", "tmdb_movie", "tmdb_movie_details", "tmdb_now_playing",
    "tvdb_movie", "tvdb_movie_details"
]
summary_details = [
    "summary", "tmdb_summary", "tmdb_description", "tmdb_biography", "tvdb_summary",
    "tvdb_description", "trakt_description", "letterboxd_description", "icheckmovies_description"
]
poster_details = ["url_poster", "tmdb_poster", "tmdb_profile", "tvdb_poster", "file_poster"]
background_details = ["url_background", "tmdb_background", "tvdb_background", "file_background"]
boolean_details = ["visible_library", "visible_home", "visible_shared", "show_filtered", "show_missing", "save_missing", "item_assets", "create_asset_folders", "released_missing_only"]
string_details = ["sort_title", "content_rating", "name_mapping"]
ignored_details = ["smart_filter", "smart_label", "smart_url", "run_again", "schedule", "sync_mode", "template", "test", "tmdb_person", "build_collection", "collection_order", "validate_builders"]
details = ["collection_mode", "collection_order", "label"] + boolean_details + string_details
collectionless_details = ["collection_order", "plex_collectionless", "label", "label_sync_mode", "test"] + \
                         poster_details + background_details + summary_details + string_details
item_details = ["item_label", "item_radarr_tag", "item_sonarr_tag", "item_overlay"] + list(plex.item_advance_keys.keys())
radarr_details = ["radarr_add", "radarr_folder", "radarr_monitor", "radarr_search", "radarr_availability", "radarr_quality", "radarr_tag"]
sonarr_details = ["sonarr_add", "sonarr_folder", "sonarr_monitor", "sonarr_language", "sonarr_series", "sonarr_quality", "sonarr_season", "sonarr_search", "sonarr_cutoff_search", "sonarr_tag"]
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
    "last_episode_aired", "last_episode_aired.not", "last_episode_aired.before", "last_episode_aired.after", "last_episode_aired.regex",
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
tmdb_filters = ("original_language", "tmdb_vote_count", "year")
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
show_only_filters = ["last_episode_aired", "network"]
smart_invalid = ["collection_order"]
smart_url_invalid = ["filters", "run_again", "sync_mode", "show_filtered", "show_missing", "save_missing", "smart_label"] + radarr_details + sonarr_details
custom_sort_builders = [
    "tmdb_list", "tmdb_popular", "tmdb_now_playing", "tmdb_top_rated",
    "tmdb_trending_daily", "tmdb_trending_weekly", "tmdb_discover",
    "tvdb_list",
    "imdb_list",
    "trakt_list", "trakt_trending", "trakt_popular", "trakt_recommended", "trakt_watched", "trakt_collected",
    "tautulli_popular", "tautulli_watched", "letterboxd_list", "icheckmovies_list",
    "anidb_popular",
    "anilist_top_rated", "anilist_popular", "anilist_season", "anilist_studio", "anilist_genre", "anilist_tag",
    "mal_all", "mal_airing", "mal_upcoming", "mal_tv", "mal_movie", "mal_ova", "mal_special",
    "mal_popular", "mal_favorite", "mal_suggested", "mal_userlist", "mal_season"
]

class CollectionBuilder:
    def __init__(self, config, library, metadata, name, data):
        self.config = config
        self.library = library
        self.metadata = metadata
        self.name = name
        self.data = data
        self.language = self.library.Plex.language
        self.details = {
            "show_filtered": self.library.show_filtered,
            "show_missing": self.library.show_missing,
            "save_missing": self.library.save_missing,
            "released_missing_only": self.library.released_missing_only,
            "create_asset_folders": self.library.create_asset_folders,
            "item_assets": False
        }
        self.item_details = {}
        self.radarr_options = {}
        self.sonarr_options = {}
        self.missing_movies = []
        self.missing_shows = []
        self.builders = []
        self.filters = []
        self.tmdb_filters = []
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
            logger.debug("")
            logger.debug("Validating Method: template")
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
            logger.debug("")
            logger.debug("Validating Method: schedule")
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
                                    self.schedule += f"\nScheduled to run only on the {util.make_ordinal(int(param))} hour"
                                    if self.config.run_hour == int(param):
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
                                    self.schedule += f"\nScheduled monthly on the {util.make_ordinal(int(param))}"
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

        self.collectionless = "plex_collectionless" in methods

        self.validate_builders = True
        if "validate_builders" in methods:
            logger.debug("")
            logger.debug("Validating Method: validate_builders")
            logger.debug(f"Value: {data[methods['validate_builders']]}")
            self.validate_builders = util.parse("validate_builders", self.data, datatype="bool", methods=methods, default=True)

        self.run_again = False
        if "run_again" in methods:
            logger.debug("")
            logger.debug("Validating Method: run_again")
            logger.debug(f"Value: {data[methods['run_again']]}")
            self.run_again = util.parse("run_again", self.data, datatype="bool", methods=methods, default=False)

        self.build_collection = True
        if "build_collection" in methods:
            logger.debug("")
            logger.debug("Validating Method: build_collection")
            logger.debug(f"Value: {data[methods['build_collection']]}")
            self.build_collection = util.parse("build_collection", self.data, datatype="bool", methods=methods, default=True)

        self.sync = self.library.sync_mode == "sync"
        if "sync_mode" in methods:
            logger.debug("")
            logger.debug("Validating Method: sync_mode")
            if not self.data[methods["sync_mode"]]:
                logger.warning(f"Collection Warning: sync_mode attribute is blank using general: {self.library.sync_mode}")
            else:
                logger.debug(f"Value: {self.data[methods['sync_mode']]}")
                if self.data[methods["sync_mode"]].lower() not in ["append", "sync"]:
                    logger.warning(f"Collection Warning: {self.data[methods['sync_mode']]} sync_mode invalid using general: {self.library.sync_mode}")
                else:
                    self.sync = self.data[methods["sync_mode"]].lower() == "sync"

        self.custom_sort = False
        if "collection_order" in methods:
            logger.debug("")
            logger.debug("Validating Method: collection_order")
            if self.data[methods["collection_order"]] is None:
                raise Failed(f"Collection Warning: collection_order attribute is blank")
            else:
                logger.debug(f"Value: {self.data[methods['collection_order']]}")
                if self.data[methods["collection_order"]].lower() in plex.collection_order_options:
                    self.details["collection_order"] = self.data[methods["collection_order"]].lower()
                    if self.data[methods["collection_order"]].lower() == "custom" and self.build_collection:
                        self.custom_sort = True
                else:
                    raise Failed(f"Collection Error: {self.data[methods['collection_order']]} collection_order invalid\n\trelease (Order Collection by release dates)\n\talpha (Order Collection Alphabetically)\n\tcustom (Custom Order Collection)")

        if "tmdb_person" in methods:
            logger.debug("")
            logger.debug("Validating Method: tmdb_person")
            if not self.data[methods["tmdb_person"]]:
                raise Failed("Collection Error: tmdb_person attribute is blank")
            else:
                logger.debug(f"Value: {self.data[methods['tmdb_person']]}")
                valid_names = []
                for tmdb_id in util.get_int_list(self.data[methods["tmdb_person"]], "TMDb Person ID"):
                    person = self.config.TMDb.get_person(tmdb_id)
                    valid_names.append(person.name)
                    if hasattr(person, "biography") and person.biography:
                        self.summaries["tmdb_person"] = person.biography
                    if hasattr(person, "profile_path") and person.profile_path:
                        self.posters["tmdb_person"] = f"{self.config.TMDb.image_url}{person.profile_path}"
                if len(valid_names) > 0:
                    self.details["tmdb_person"] = valid_names
                else:
                    raise Failed(f"Collection Error: No valid TMDb Person IDs in {self.data[methods['tmdb_person']]}")

        self.smart_sort = "random"
        self.smart_label_collection = False
        if "smart_label" in methods:
            logger.debug("")
            logger.debug("Validating Method: smart_label")
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
            logger.debug("")
            logger.debug("Validating Method: smart_url")
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
            method_name, method_mod, method_final = self._split(method_key)
            if method_name in ignored_details:
                continue
            logger.debug("")
            logger.debug(f"Validating Method: {method_key}")
            logger.debug(f"Value: {method_data}")
            try:
                if method_data is None and method_name in all_builders + plex.searches:     raise Failed(f"Collection Error: {method_final} attribute is blank")
                elif method_data is None:                                                   logger.warning(f"Collection Warning: {method_final} attribute is blank")
                elif not self.config.Trakt and "trakt" in method_name:                      raise Failed(f"Collection Error: {method_final} requires Trakt to be configured")
                elif not self.library.Radarr and "radarr" in method_name:                   raise Failed(f"Collection Error: {method_final} requires Radarr to be configured")
                elif not self.library.Sonarr and "sonarr" in method_name:                   raise Failed(f"Collection Error: {method_final} requires Sonarr to be configured")
                elif not self.library.Tautulli and "tautulli" in method_name:               raise Failed(f"Collection Error: {method_final} requires Tautulli to be configured")
                elif not self.config.MyAnimeList and "mal" in method_name:                  raise Failed(f"Collection Error: {method_final} requires MyAnimeList to be configured")
                elif self.library.is_movie and method_name in show_only_builders:           raise Failed(f"Collection Error: {method_final} attribute only works for show libraries")
                elif self.library.is_show and method_name in movie_only_builders:           raise Failed(f"Collection Error: {method_final} attribute only works for movie libraries")
                elif self.library.is_show and method_name in plex.movie_only_searches:      raise Failed(f"Collection Error: {method_final} plex search only works for movie libraries")
                elif self.library.is_movie and method_name in plex.show_only_searches:      raise Failed(f"Collection Error: {method_final} plex search only works for show libraries")
                elif self.smart and method_name in smart_invalid:                           raise Failed(f"Collection Error: {method_final} attribute only works with normal collections")
                elif self.collectionless and method_name not in collectionless_details:     raise Failed(f"Collection Error: {method_final} attribute does not work for Collectionless collection")
                elif self.smart_url and method_name in all_builders + smart_url_invalid:    raise Failed(f"Collection Error: {method_final} builder not allowed when using smart_filter")
                elif method_name in summary_details:                                        self._summary(method_name, method_data)
                elif method_name in poster_details:                                         self._poster(method_name, method_data)
                elif method_name in background_details:                                     self._background(method_name, method_data)
                elif method_name in details:                                                self._details(method_name, method_data, method_final, methods)
                elif method_name in item_details:                                           self._item_details(method_name, method_data, method_mod, method_final, methods)
                elif method_name in radarr_details:                                         self._radarr(method_name, method_data)
                elif method_name in sonarr_details:                                         self._sonarr(method_name, method_data)
                elif method_name in anidb.builders:                                         self._anidb(method_name, method_data)
                elif method_name in anilist.builders:                                       self._anilist(method_name, method_data)
                elif method_name in icheckmovies.builders:                                  self._icheckmovies(method_name, method_data)
                elif method_name in letterboxd.builders:                                    self._letterboxd(method_name, method_data)
                elif method_name in imdb.builders:                                          self._imdb(method_name, method_data)
                elif method_name in mal.builders:                                           self._mal(method_name, method_data)
                elif method_name in plex.builders or method_final in plex.searches:         self._plex(method_name, method_data)
                elif method_name in stevenlu.builders:                                      self._stevenlu(method_name, method_data)
                elif method_name in tautulli.builders:                                      self._tautulli(method_name, method_data)
                elif method_name in tmdb.builders:                                          self._tmdb(method_name, method_data)
                elif method_name in trakt.builders:                                         self._trakt(method_name, method_data)
                elif method_name in tvdb.builders:                                          self._tvdb(method_name, method_data)
                elif method_name == "filters":                                              self._filters(method_name, method_data)
                else:                                                                       raise Failed(f"Collection Error: {method_final} attribute not supported")
            except Failed as e:
                if self.validate_builders:
                    raise
                else:
                    logger.error(e)

        self.tmdb_filters = [(fm, fd) for fm, fd in self.filters if fm.startswith(tmdb_filters)]

        if self.custom_sort and len(self.builders) > 1:
            raise Failed("Collection Error: collection_order: custom can only be used with a single builder per collection")

        if self.custom_sort and self.builders[0][0] not in custom_sort_builders:
            raise Failed(f"Collection Error: collection_order: custom cannot be used with {self.builders[0][0]}")

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

    def _summary(self, method_name, method_data):
        if method_name == "summary":
            self.summaries[method_name] = method_data
        elif method_name == "tmdb_summary":
            self.summaries[method_name] = self.config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, "TMDb ID"), self.library.is_movie).overview
        elif method_name == "tmdb_description":
            self.summaries[method_name] = self.config.TMDb.get_list(util.regex_first_int(method_data, "TMDb List ID")).description
        elif method_name == "tmdb_biography":
            self.summaries[method_name] = self.config.TMDb.get_person(util.regex_first_int(method_data, "TMDb Person ID")).biography
        elif method_name == "tvdb_summary":
            self.summaries[method_name] = self.config.TVDb.get_movie_or_show(method_data, self.language, self.library.is_movie).summary
        elif method_name == "tvdb_description":
            self.summaries[method_name] = self.config.TVDb.get_list_description(method_data, self.language)
        elif method_name == "trakt_description":
            self.summaries[method_name] = self.config.Trakt.list_description(self.config.Trakt.validate_trakt(method_data, self.library.is_movie)[0])
        elif method_name == "letterboxd_description":
            self.summaries[method_name] = self.config.Letterboxd.get_list_description(method_data, self.language)
        elif method_name == "icheckmovies_description":
            self.summaries[method_name] = self.config.ICheckMovies.get_list_description(method_data, self.language)

    def _poster(self, method_name, method_data):
        if method_name == "url_poster":
            self.posters[method_name] = method_data
        elif method_name == "tmdb_poster":
            url_slug = self.config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, 'TMDb ID'), self.library.is_movie).poster_path
            self.posters[method_name] = f"{self.config.TMDb.image_url}{url_slug}"
        elif method_name == "tmdb_profile":
            url_slug = self.config.TMDb.get_person(util.regex_first_int(method_data, 'TMDb Person ID')).profile_path
            self.posters[method_name] = f"{self.config.TMDb.image_url}{url_slug}"
        elif method_name == "tvdb_poster":
            self.posters[method_name] = f"{self.config.TVDb.get_item(method_data, self.language, self.library.is_movie).poster_path}"
        elif method_name == "file_poster":
            if os.path.exists(method_data):
                self.posters[method_name] = os.path.abspath(method_data)
            else:
                raise Failed(f"Collection Error: Poster Path Does Not Exist: {os.path.abspath(method_data)}")

    def _background(self, method_name, method_data):
        if method_name == "url_background":
            self.backgrounds[method_name] = method_data
        elif method_name == "tmdb_background":
            url_slug = self.config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, 'TMDb ID'), self.library.is_movie).poster_path
            self.backgrounds[method_name] = f"{self.config.TMDb.image_url}{url_slug}"
        elif method_name == "tvdb_background":
            self.posters[method_name] = f"{self.config.TVDb.get_item(method_data, self.language, self.library.is_movie).background_path}"
        elif method_name == "file_background":
            if os.path.exists(method_data):
                self.backgrounds[method_name] = os.path.abspath(method_data)
            else:
                raise Failed(f"Collection Error: Background Path Does Not Exist: {os.path.abspath(method_data)}")

    def _details(self, method_name, method_data, method_final, methods):
        if method_name == "collection_mode":
            if str(method_data).lower() in plex.collection_mode_options:
                self.details[method_name] = plex.collection_mode_options[str(method_data).lower()]
            else:
                raise Failed(f"Collection Error: {method_data} collection_mode invalid\n\tdefault (Library default)\n\thide (Hide Collection)\n\thide_items (Hide Items in this Collection)\n\tshow_items (Show this Collection and its Items)")
        elif method_name == "label":
            if "label" in methods and "label.sync" in methods:
                raise Failed("Collection Error: Cannot use label and label.sync together")
            if "label.remove" in methods and "label.sync" in methods:
                raise Failed("Collection Error: Cannot use label.remove and label.sync together")
            if method_final == "label" and "label_sync_mode" in methods and self.data[methods["label_sync_mode"]] == "sync":
                self.details["label.sync"] = util.get_list(method_data)
            else:
                self.details[method_final] = util.get_list(method_data)
        elif method_name in boolean_details:
            default = self.details[method_name] if method_name in self.details else None
            self.details[method_name] = util.parse(method_name, method_data, datatype="bool", default=default)
        elif method_name in string_details:
            self.details[method_name] = str(method_data)

    def _item_details(self, method_name, method_data, method_mod, method_final, methods):
        if method_name == "item_label":
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
            overlay = os.path.join(self.config.default_dir, "overlays", method_data, "overlay.png")
            if not os.path.exists(overlay):
                raise Failed(f"Collection Error: {method_data} overlay image not found at {overlay}")
            if method_data in self.library.overlays:
                raise Failed("Each Overlay can only be used once per Library")
            self.library.overlays.append(method_data)
            self.item_details[method_name] = method_data
        elif method_name in plex.item_advance_keys:
            key, options = plex.item_advance_keys[method_name]
            if method_name in advance_new_agent and self.library.agent not in plex.new_plex_agents:
                logger.error(
                    f"Metadata Error: {method_name} attribute only works for with the New Plex Movie Agent and New Plex TV Agent")
            elif method_name in advance_show and not self.library.is_show:
                logger.error(f"Metadata Error: {method_name} attribute only works for show libraries")
            elif str(method_data).lower() not in options:
                logger.error(f"Metadata Error: {method_data} {method_name} attribute invalid")
            else:
                self.item_details[method_name] = str(method_data).lower()

    def _radarr(self, method_name, method_data):
        if method_name == "radarr_add":
            self.add_to_radarr = util.parse(method_name, method_data, datatype="bool")
        elif method_name == "radarr_folder":
            self.radarr_options["folder"] = method_data
        elif method_name in ["radarr_monitor", "radarr_search"]:
            self.radarr_options[method_name[7:]] = util.parse(method_name, method_data, datatype="bool")
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

    def _sonarr(self, method_name, method_data):
        if method_name == "sonarr_add":
            self.add_to_sonarr = util.parse(method_name, method_data, datatype="bool")
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
            self.sonarr_options[method_name[7:]] = util.parse(method_name, method_data, datatype="bool")
        elif method_name == "sonarr_tag":
            self.sonarr_options["tag"] = util.get_list(method_data)

    def _anidb(self, method_name, method_data):
        if method_name == "anidb_popular":
            self.builders.append((method_name, util.parse(method_name, method_data, datatype="int", default=30, maximum=30)))
        elif method_name in ["anidb_id", "anidb_relation"]:
            for anidb_id in self.config.AniDB.validate_anidb_ids(method_data, self.language):
                self.builders.append((method_name, anidb_id))
        elif method_name == "anidb_tag":
            for dict_data, dict_methods in util.parse(method_name, method_data, datatype="dictlist"):
                new_dictionary = {}
                if "tag" not in dict_methods:
                    raise Failed("Collection Error: anidb_tag tag attribute is required")
                elif not dict_data[dict_methods["tag"]]:
                    raise Failed("Collection Error: anidb_tag tag attribute is blank")
                else:
                    new_dictionary["tag"] = util.regex_first_int(dict_data[dict_methods["username"]], "AniDB Tag ID")
                new_dictionary["limit"] = util.parse("limit", dict_data, datatype="int", methods=dict_methods, default=0, parent=method_name, minimum=0)
                self.builders.append((method_name, new_dictionary))

    def _anilist(self, method_name, method_data):
        if method_name in ["anilist_id", "anilist_relations", "anilist_studio"]:
            for anilist_id in self.config.AniList.validate_anilist_ids(method_data, studio=method_name == "anilist_studio"):
                self.builders.append((method_name, anilist_id))
        elif method_name in ["anilist_popular", "anilist_top_rated"]:
            self.builders.append((method_name, util.parse(method_name, method_data, datatype="int", default=10)))
        elif method_name in ["anilist_season", "anilist_genre", "anilist_tag"]:
            for dict_data, dict_methods in util.parse(method_name, method_data, datatype="dictlist"):
                new_dictionary = {}
                if method_name == "anilist_season":
                    if self.current_time.month in [12, 1, 2]:       new_dictionary["season"] = "winter"
                    elif self.current_time.month in [3, 4, 5]:      new_dictionary["season"] = "spring"
                    elif self.current_time.month in [6, 7, 8]:      new_dictionary["season"] = "summer"
                    elif self.current_time.month in [9, 10, 11]:    new_dictionary["season"] = "fall"
                    new_dictionary["season"] = util.parse("season", dict_data, methods=dict_methods, parent=method_name, default=new_dictionary["season"], options=["winter", "spring", "summer", "fall"])
                    new_dictionary["year"] = util.parse("year", dict_data, datatype="int", methods=dict_methods, default=self.current_time.year, parent=method_name, minimum=1917, maximum=self.current_time.year + 1)
                elif method_name == "anilist_genre":
                    new_dictionary["genre"] = self.config.AniList.validate_genre(util.parse("genre", dict_data, methods=dict_methods, parent=method_name))
                elif method_name == "anilist_tag":
                    new_dictionary["tag"] = self.config.AniList.validate_tag(util.parse("tag", dict_data, methods=dict_methods, parent=method_name))
                new_dictionary["sort_by"] = util.parse("sort_by", dict_data, methods=dict_methods, parent=method_name, default="score", options=["score", "popular"])
                new_dictionary["limit"] = util.parse("limit", dict_data, datatype="int", methods=dict_methods, default=0, parent=method_name, maximum=500)
                self.builders.append((method_name, new_dictionary))

    def _icheckmovies(self, method_name, method_data):
        if method_name.startswith("icheckmovies_list"):
            icheckmovies_lists = self.config.ICheckMovies.validate_icheckmovies_lists(method_data, self.language)
            for icheckmovies_list in icheckmovies_lists:
                self.builders.append(("icheckmovies_list", icheckmovies_list))
            if method_name.endswith("_details"):
                self.summaries[method_name] = self.config.ICheckMovies.get_list_description(icheckmovies_lists[0], self.language)

    def _imdb(self, method_name, method_data):
        if method_name == "imdb_id":
            for value in util.get_list(method_data):
                if str(value).startswith("tt"):
                    self.builders.append((method_name, value))
                else:
                    raise Failed(f"Collection Error: imdb_id {value} must begin with tt")
        elif method_name == "imdb_list":
            for imdb_dict in self.config.IMDb.validate_imdb_lists(method_data, self.language):
                self.builders.append((method_name, imdb_dict))

    def _letterboxd(self, method_name, method_data):
        if method_name.startswith("letterboxd_list"):
            letterboxd_lists = self.config.Letterboxd.validate_letterboxd_lists(method_data, self.language)
            for letterboxd_list in letterboxd_lists:
                self.builders.append(("letterboxd_list", letterboxd_list))
            if method_name.endswith("_details"):
                self.summaries[method_name] = self.config.Letterboxd.get_list_description(letterboxd_lists[0], self.language)

    def _mal(self, method_name, method_data):
        if method_name == "mal_id":
            for mal_id in util.get_int_list(method_data, "MyAnimeList ID"):
                self.builders.append((method_name, mal_id))
        elif method_name in ["mal_all", "mal_airing", "mal_upcoming", "mal_tv", "mal_ova", "mal_movie", "mal_special", "mal_popular", "mal_favorite", "mal_suggested"]:
            self.builders.append((method_name, util.parse(method_name, method_data, datatype="int", default=10)))
        elif method_name in ["mal_season", "mal_userlist"]:
            for dict_data, dict_methods in util.parse(method_name, method_data, datatype="dictlist"):
                new_dictionary = {}
                if method_name == "mal_season":
                    if self.current_time.month in [1, 2, 3]:            new_dictionary["season"] = "winter"
                    elif self.current_time.month in [4, 5, 6]:          new_dictionary["season"] = "spring"
                    elif self.current_time.month in [7, 8, 9]:          new_dictionary["season"] = "summer"
                    elif self.current_time.month in [10, 11, 12]:       new_dictionary["season"] = "fall"
                    new_dictionary["season"] = util.parse("season", dict_data, methods=dict_methods, parent=method_name, default=new_dictionary["season"], options=["winter", "spring", "summer", "fall"])
                    new_dictionary["sort_by"] = util.parse("sort_by", dict_data, methods=dict_methods, parent=method_name, default="members", options=mal.season_sort_options, translation=mal.season_sort_translation)
                    new_dictionary["year"] = util.parse("year", dict_data, datatype="int", methods=dict_methods, default=self.current_time.year, parent=method_name, minimum=1917, maximum=self.current_time.year + 1)
                    new_dictionary["limit"] = util.parse("limit", dict_data, datatype="int", methods=dict_methods, default=100, parent=method_name, maximum=500)
                elif method_name == "mal_userlist":
                    new_dictionary["username"] = util.parse("username", dict_data, methods=dict_methods, parent=method_name)
                    new_dictionary["status"] = util.parse("status", dict_data, methods=dict_methods, parent=method_name, default="all", options=mal.userlist_status)
                    new_dictionary["sort_by"] = util.parse("sort_by", dict_data, methods=dict_methods, parent=method_name, default="score", options=mal.userlist_sort_options, translation=mal.userlist_sort_translation)
                    new_dictionary["limit"] = util.parse("limit", dict_data, datatype="int", methods=dict_methods, default=100, parent=method_name, maximum=1000)
                self.builders.append((method_name, new_dictionary))

    def _plex(self, method_name, method_data):
        if method_name == "plex_all":
            self.builders.append((method_name, True))
        elif method_name in ["plex_search", "plex_collectionless"]:
            for dict_data, dict_methods in util.parse(method_name, method_data, datatype="dictlist"):
                new_dictionary = {}
                if method_name == "plex_search":
                    new_dictionary = self.build_filter("plex_search", dict_data)
                elif method_name == "plex_collectionless":
                    prefix_list = util.parse("exclude_prefix", dict_data, datatype="list", methods=dict_methods)
                    exact_list = util.parse("exclude", dict_data, datatype="list", methods=dict_methods)
                    if len(prefix_list) == 0 and len(exact_list) == 0:
                        raise Failed("Collection Error: you must have at least one exclusion")
                    exact_list.append(self.name)
                    new_dictionary["exclude_prefix"] = prefix_list
                    new_dictionary["exclude"] = exact_list
                self.builders.append((method_name, new_dictionary))
        else:
            self.builders.append(("plex_search", self.build_filter("plex_search", {"any": {method_name: method_data}})))

    def _stevenlu(self, method_name, method_data):
        self.builders.append((method_name, util.parse(method_name, method_data, "bool")))

    def _tautulli(self, method_name, method_data):
        for dict_data, dict_methods in util.parse(method_name, method_data, datatype="dictlist"):
            self.builders.append((method_name, {
                "list_type": "popular" if method_name == "tautulli_popular" else "watched",
                "list_days": util.parse("list_days", dict_data, datatype="int", methods=dict_methods, default=30, parent=method_name),
                "list_size": util.parse("list_size", dict_data, datatype="int", methods=dict_methods, default=10, parent=method_name),
                "list_buffer": util.parse("list_buffer", dict_data, datatype="int", methods=dict_methods, default=20, parent=method_name)
            }))

    def _tmdb(self, method_name, method_data):
        if method_name == "tmdb_discover":
            for dict_data, dict_methods in util.parse(method_name, method_data, datatype="dictlist"):
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
                                new_dictionary[discover_final] = util.validate_date(discover_data, f"{method_name} attribute {discover_final}", return_as="%m/%d/%Y")
                            elif discover_final in ["primary_release_year", "year", "first_air_date_year"]:
                                new_dictionary[discover_final] = util.parse(discover_final, discover_data, datatype="int", parent=method_name, minimum=1800, maximum=self.current_year + 1)
                            elif discover_final in ["vote_count.gte", "vote_count.lte", "vote_average.gte", "vote_average.lte", "with_runtime.gte", "with_runtime.lte"]:
                                new_dictionary[discover_final] = util.parse(discover_final, discover_data, datatype="int", parent=method_name)
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
                    self.builders.append((method_name, new_dictionary))
                else:
                    raise Failed(f"Collection Error: {method_name} had no valid fields")
        elif method_name in ["tmdb_popular", "tmdb_top_rated", "tmdb_now_playing", "tmdb_trending_daily", "tmdb_trending_weekly"]:
            self.builders.append((method_name, util.parse(method_name, method_data, datatype="int", default=10)))
        else:
            values = self.config.TMDb.validate_tmdb_ids(method_data, method_name)
            if method_name.endswith("_details"):
                if method_name.startswith(("tmdb_collection", "tmdb_movie", "tmdb_show")):
                    item = self.config.TMDb.get_movie_show_or_collection(values[0], self.library.is_movie)
                    if hasattr(item, "overview") and item.overview:
                        self.summaries[method_name] = item.overview
                    if hasattr(item, "backdrop_path") and item.backdrop_path:
                        self.backgrounds[method_name] = f"{self.config.TMDb.image_url}{item.backdrop_path}"
                    if hasattr(item, "poster_path") and item.poster_path:
                        self.posters[method_name] = f"{self.config.TMDb.image_url}{item.poster_path}"
                elif method_name.startswith(("tmdb_actor", "tmdb_crew", "tmdb_director", "tmdb_producer", "tmdb_writer")):
                    item = self.config.TMDb.get_person(values[0])
                    if hasattr(item, "biography") and item.biography:
                        self.summaries[method_name] = item.biography
                    if hasattr(item, "profile_path") and item.profile_path:
                        self.posters[method_name] = f"{self.config.TMDb.image_url}{item.profile_path}"
                elif method_name.startswith("tmdb_list"):
                    item = self.config.TMDb.get_list(values[0])
                    if hasattr(item, "description") and item.description:
                        self.summaries[method_name] = item.description
            for value in values:
                self.builders.append((method_name[:-8] if method_name.endswith("_details") else method_name, value))

    def _trakt(self, method_name, method_data):
        if method_name.startswith("trakt_list"):
            trakt_lists = self.config.Trakt.validate_trakt(method_data, self.library.is_movie)
            for trakt_list in trakt_lists:
                self.builders.append(("trakt_list", trakt_list))
            if method_name.endswith("_details"):
                self.summaries[method_name] = self.config.Trakt.list_description(trakt_lists[0])
        elif method_name in ["trakt_trending", "trakt_popular", "trakt_recommended", "trakt_watched", "trakt_collected"]:
            self.builders.append((method_name, util.parse(method_name, method_data, datatype="int", default=10)))
        elif method_name in ["trakt_watchlist", "trakt_collection"]:
            for trakt_list in self.config.Trakt.validate_trakt(method_data, self.library.is_movie, trakt_type=method_name[6:]):
                self.builders.append((method_name, trakt_list))

    def _tvdb(self, method_name, method_data):
        values = util.get_list(method_data)
        if method_name.endswith("_details"):
            if method_name.startswith(("tvdb_movie", "tvdb_show")):
                item = self.config.TVDb.get_item(self.language, values[0], method_name.startswith("tvdb_movie"))
                if hasattr(item, "description") and item.description:
                    self.summaries[method_name] = item.description
                if hasattr(item, "background_path") and item.background_path:
                    self.backgrounds[method_name] = f"{self.config.TMDb.image_url}{item.background_path}"
                if hasattr(item, "poster_path") and item.poster_path:
                    self.posters[method_name] = f"{self.config.TMDb.image_url}{item.poster_path}"
            elif method_name.startswith("tvdb_list"):
                self.summaries[method_name] = self.config.TVDb.get_list_description(values[0], self.language)
        for value in values:
            self.builders.append((method_name[:-8] if method_name.endswith("_details") else method_name, value))

    def _filters(self, method_name, method_data):
        for dict_data, dict_methods in util.parse(method_name, method_data, datatype="dictlist"):
            validate = True
            if "validate" in dict_data:
                if dict_data["validate"] is None:
                    raise Failed("Collection Error: validate filter attribute is blank")
                if not isinstance(dict_data["validate"], bool):
                    raise Failed("Collection Error: validate filter attribute must be either true or false")
                validate = dict_data["validate"]
            for filter_method, filter_data in dict_data.items():
                filter_attr, modifier, filter_final = self._split(filter_method)
                message = None
                if filter_final not in all_filters:
                    message = f"Collection Error: {filter_final} is not a valid filter attribute"
                elif filter_final in movie_only_filters and self.library.is_show:
                    message = f"Collection Error: {filter_final} filter attribute only works for movie libraries"
                elif filter_final in show_only_filters and self.library.is_movie:
                    message = f"Collection Error: {filter_final} filter attribute only works for show libraries"
                elif filter_final is None:
                    message = f"Collection Error: {filter_final} filter attribute is blank"
                else:
                    self.filters.append((filter_final, self.validate_attribute(filter_attr, modifier, f"{filter_final} filter", filter_data, validate)))
                if message:
                    if validate:
                        raise Failed(message)
                    else:
                        logger.error(message)

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
                movie_rating_keys = []
                for movie_id in movie_ids:
                    if movie_id in self.library.movie_map:
                        movie_rating_keys.append(self.library.movie_map[movie_id][0])
                    elif movie_id not in self.missing_movies:
                        self.missing_movies.append(movie_id)
                add_rating_keys(movie_rating_keys)
            if len(show_ids) > 0:
                items_found_inside += len(show_ids)
                show_rating_keys = []
                for show_id in show_ids:
                    if show_id in self.library.show_map:
                        show_rating_keys.append(self.library.show_map[show_id][0])
                    elif show_id not in self.missing_shows:
                        self.missing_shows.append(show_id)
                add_rating_keys(show_rating_keys)
            return items_found_inside
        for method, value in self.builders:
            logger.debug("")
            logger.debug(f"Builder: {method}: {value}")
            logger.info("")
            if "plex" in method:                                add_rating_keys(self.library.get_items(method, value))
            elif "tautulli" in method:                          add_rating_keys(self.library.Tautulli.get_items(self.library, value))
            elif "anidb" in method:                             check_map(self.config.AniDB.get_items(method, value, self.language))
            elif "anilist" in method:                           check_map(self.config.AniList.get_items(method, value))
            elif "mal" in method:                               check_map(self.config.MyAnimeList.get_items(method, value))
            elif "tvdb" in method:                              check_map(self.config.TVDb.get_items(method, value, self.language))
            elif "imdb" in method:                              check_map(self.config.IMDb.get_items(method, value, self.language, self.library.is_movie))
            elif "icheckmovies" in method:                      check_map(self.config.ICheckMovies.get_items(method, value, self.language))
            elif "letterboxd" in method:                        check_map(self.config.Letterboxd.get_items(method, value, self.language))
            elif "stevenlu" in method:                          check_map(self.config.StevenLu.get_items(method))
            elif "tmdb" in method:                              check_map(self.config.TMDb.get_items(method, value, self.library.is_movie))
            elif "trakt" in method:                             check_map(self.config.Trakt.get_items(method, value, self.library.is_movie))
            else:                                               logger.error(f"Collection Error: {method} method not supported")

    def tmdb_filter(self, item_id, is_movie, item=None):
        filter_missing = False
        if self.tmdb_filters or self.details["released_missing_only"]:
            try:
                if item is None:
                    item = self.config.TMDb.get_movie(item_id) if is_movie else self.config.TMDb.get_movie(self.config.Convert.tvdb_to_tmdb(item_id))
                if self.details["released_missing_only"]:
                    if util.validate_date(item.release_date if is_movie else item.first_air_date, "") > self.current_time:
                        return True
                for filter_method, filter_data in self.tmdb_filters:
                    if (filter_method == "original_language" and item.original_language not in filter_data) \
                            or (filter_method == "original_language.not" and item.original_language in filter_data) \
                            or (filter_method == "tmdb_vote_count.gt" and item.vote_count <= filter_data) \
                            or (filter_method == "tmdb_vote_count.gte" and item.vote_count < filter_data) \
                            or (filter_method == "tmdb_vote_count.lt" and item.vote_count >= filter_data) \
                            or (filter_method == "tmdb_vote_count.lte" and item.vote_count > filter_data) \
                            or (filter_method == "year.gt" and item.year <= filter_data) \
                            or (filter_method == "year.gte" and item.year < filter_data) \
                            or (filter_method == "year.lt" and item.year >= filter_data) \
                            or (filter_method == "year.lte" and item.year > filter_data):
                        return True
            except Failed:
                return True
        return filter_missing

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
                    arg_key = plex.show_translation[arg_key] if self.library.is_show and arg_key in plex.show_translation else arg_key
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
                return util.parse(final, data, datatype="int", maximum=30)
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
        elif attribute in ["year", "episode_year"] and modifier in [".gt", ".gte", ".lt", ".lte"]:
            return util.parse(final, data, datatype="int", minimum=1800, maximum=self.current_year)
        elif attribute in plex.date_attributes and modifier in [".before", ".after"]:
            return util.validate_date(data, final, return_as="%Y-%m-%d")
        elif attribute in plex.number_attributes and modifier in ["", ".not", ".gt", ".gte", ".lt", ".lte"]:
            return util.parse(final, data, datatype="int")
        elif attribute in plex.float_attributes and modifier in [".gt", ".gte", ".lt", ".lte"]:
            return util.parse(final, data, datatype="float", minimum=0, maximum=10)
        elif attribute in ["decade", "year", "episode_year"] and modifier in ["", ".not"]:
            final_years = []
            values = util.get_list(data)
            for value in values:
                final_years.append(util.parse(final, value, datatype="int", minimum=1800, maximum=self.current_year))
            return smart_pair(final_years)
        elif attribute in plex.boolean_attributes:
            return util.parse(attribute, data, datatype="bool")
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
            for filter_method, filter_data in self.filters:
                filter_attr, modifier, filter_final = self._split(filter_method)
                filter_actual = filter_translation[filter_attr] if filter_attr in filter_translation else filter_attr
                if filter_attr in ["tmdb_vote_count", "original_language", "last_episode_aired"]:
                    if (self.library.is_movie and current.ratingKey not in self.library.movie_rating_key_map) \
                            or (self.library.is_show and current.ratingKey not in self.library.show_rating_key_map):
                        logger.warning(f"Filter Error: No {'TMDb' if self.library.is_movie else 'TVDb'} ID found for {current.title}")
                        return False
                    try:
                        if self.library.is_movie:
                            tmdb_item = self.config.TMDb.get_movie(self.library.movie_rating_key_map[current.ratingKey])
                        else:
                            tmdb_item = self.config.TMDb.get_show(self.config.Convert.tvdb_to_tmdb(self.library.show_rating_key_map[current.ratingKey]))
                    except Failed as e:
                        logger.error(e)
                        return False
                else:
                    tmdb_item = None
                if filter_attr in ["release", "added", "last_played", "last_episode_aired"] and modifier != ".regex":
                    if filter_attr == "last_episode_aired":
                        if tmdb_item.last_air_date is None:
                            return False
                        current_data = util.validate_date(tmdb_item.last_air_date, "TMDB Last Air Date")
                    else:
                        current_data = getattr(current, filter_actual)
                    if current_data is None:
                        return False
                    if modifier in ["", ".not"]:
                        threshold_date = self.current_time - timedelta(days=filter_data)
                        if (modifier == "" and (current_data is None or current_data < threshold_date)) \
                                or (modifier == ".not" and current_data and current_data >= threshold_date):
                            return False
                    elif modifier in [".before", ".after"]:
                        filter_date = util.validate_date(filter_data, filter_final)
                        if (modifier == ".before" and current_data >= filter_date) or (modifier == ".after" and current_data <= filter_date):
                            return False
                    elif modifier == ".regex":
                        jailbreak = False
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
                        if item_date.month != self.current_time.month or item_date.day != self.current_time.day:
                            return False
                    elif filter_data == "month":
                        if item_date.month != self.current_time.month:
                            return False
                    else:
                        date_match = False
                        for i in range(filter_data):
                            check_date = self.current_time - timedelta(days=i)
                            if item_date.month == check_date.month and item_date.day == check_date.day:
                                date_match = True
                        if date_match is False:
                            return False
                elif filter_attr == "original_language":
                    if (modifier == ".not" and tmdb_item.original_language in filter_data) \
                            or (modifier == "" and tmdb_item.original_language not in filter_data):
                        return False
                elif modifier in [".gt", ".gte", ".lt", ".lte"]:
                    if filter_attr == "tmdb_vote_count":
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
        if len(self.missing_movies) > 0:
            missing_movies_with_names = []
            for missing_id in self.missing_movies:
                try:
                    movie = self.config.TMDb.get_movie(missing_id)
                except Failed as e:
                    logger.error(e)
                    continue
                current_title = f"{movie.title} ({util.validate_date(movie.release_date, 'test').year})" if movie.release_date else movie.title
                if self.tmdb_filter(missing_id, True, item=movie):
                    if self.details["show_filtered"] is True and self.details["show_missing"] is True:
                        logger.info(f"{self.name} Collection | X | {current_title} (TMDb: {missing_id})")
                else:
                    missing_movies_with_names.append((current_title, missing_id))
                    if self.details["show_missing"] is True:
                        logger.info(f"{self.name} Collection | ? | {current_title} (TMDb: {missing_id})")
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
                    show = self.config.TVDb.get_series(self.language, missing_id)
                except Failed as e:
                    logger.error(e)
                    continue
                current_title = str(show.title.encode("ascii", "replace").decode())
                if self.tmdb_filter(missing_id, False):
                    if self.details["show_filtered"] is True and self.details["show_missing"] is True:
                        logger.info(f"{self.name} Collection | X | {current_title} (TVDb: {missing_id})")
                else:
                    missing_shows_with_names.append((current_title, missing_id))
                    if self.details["show_missing"] is True:
                        logger.info(f"{self.name} Collection | ? | {current_title} (TVDB: {missing_id})")
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
                rating_keys = self.config.Cache.query_image_map_overlay(self.library.image_table_name, overlay_name)
            overlay_folder = os.path.join(self.config.default_dir, "overlays", overlay_name)
            overlay_image = Image.open(os.path.join(overlay_folder, "overlay.png")).convert("RGBA")
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
                self.config.Cache.update_image_map(item.ratingKey, self.library.image_table_name, "", "", "")

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

    def sort_collection(self):
        items = self.library.get_collection_items(self.obj, self.smart_label_collection)
        keys = {item.ratingKey: item for item in items}
        previous = None
        logger.debug(keys)
        logger.debug(self.rating_keys)
        for key in self.rating_keys:
            logger.info(f"Moving {keys[key].title} {'after {}'.format(keys[previous].title) if previous else 'to the beginning'}")
            self.library.move_item(self.obj, key, after=previous)
            previous = key

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
                        current_title = f"{movie.title} ({util.validate_date(movie.release_date, 'test').year})" if movie.release_date else movie.title
                        logger.info(f"{name} Collection | ? | {current_title} (TMDb: {missing_id})")
            logger.info("")
            logger.info(f"{len(self.run_again_movies)} Movie{'s' if len(self.run_again_movies) > 1 else ''} Missing")

        if len(self.run_again_shows) > 0 and self.library.is_show:
            logger.info("")
            for missing_id in self.run_again_shows:
                if missing_id not in self.library.show_map:
                    try:
                        title = str(self.config.TVDb.get_series(self.language, missing_id).title.encode("ascii", "replace").decode())
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.details["show_missing"] is True:
                        logger.info(f"{name} Collection | ? | {title} (TVDb: {missing_id})")
            logger.info(f"{len(self.run_again_shows)} Show{'s' if len(self.run_again_shows) > 1 else ''} Missing")
