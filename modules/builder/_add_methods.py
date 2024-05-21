from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from modules import anilist, imdb, mal, mojo, plex, radarr, sonarr, tmdb, trakt,util
from requests.exceptions import ConnectionError

def summary(self, method_name, method_data):
    if method_name == "summary":
        self.summaries[method_name] = str(method_data).replace("<<key_name>>", self.key_name) if self.key_name else method_data
    elif method_name == "tmdb_summary":
        self.summaries[method_name] = self.config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, "TMDb ID"), self.library.is_movie).overview
    elif method_name == "tmdb_description":
        self.summaries[method_name] = self.config.TMDb.get_list(util.regex_first_int(method_data, "TMDb List ID")).description
    elif method_name == "tmdb_biography":
        self.summaries[method_name] = self.config.TMDb.get_person(util.regex_first_int(method_data, "TMDb Person ID")).biography
    elif method_name == "tvdb_summary":
        self.summaries[method_name] = self.config.TVDb.get_tvdb_obj(method_data, is_movie=self.library.is_movie).summary
    elif method_name == "tvdb_description":
        summary, _ = self.config.TVDb.get_list_description(method_data)
        if summary:
            self.summaries[method_name] = summary
    elif method_name == "trakt_description":
        try:
            self.summaries[method_name] = self.config.Trakt.list_description(self.config.Trakt.validate_list(method_data)[0])
        except Failed as e:
            logger.error(f"Trakt Error: List description not found: {e}")
    elif method_name == "letterboxd_description":
        self.summaries[method_name] = self.config.Letterboxd.get_list_description(method_data, self.language)
    elif method_name == "icheckmovies_description":
        self.summaries[method_name] = self.config.ICheckMovies.get_list_description(method_data, self.language)

def poster(self, method_name, method_data):
    if method_name == "url_poster":
        try:
            if not method_data.startswith("https://theposterdb.com/api/assets/"):
                image_response = self.config.get(method_data, headers=util.header())
                if image_response.status_code >= 400 or image_response.headers["Content-Type"] not in util.image_content_types:
                    raise ConnectionError
            self.posters[method_name] = method_data
        except ConnectionError:
            logger.warning(f"{self.Type} Warning: No Poster Found at {method_data}")
    elif method_name == "tmdb_list_poster":
        self.posters[method_name] = self.config.TMDb.get_list(util.regex_first_int(method_data, "TMDb List ID")).poster_url
    elif method_name == "tvdb_list_poster":
        _, poster = self.config.TVDb.get_list_description(method_data)
        if poster:
            self.posters[method_name] = poster
    elif method_name == "tmdb_poster":
        self.posters[method_name] = self.config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, 'TMDb ID'), self.library.is_movie).poster_url
    elif method_name == "tmdb_profile":
        self.posters[method_name] = self.config.TMDb.get_person(util.regex_first_int(method_data, 'TMDb Person ID')).profile_url
    elif method_name == "tvdb_poster":
        self.posters[method_name] = f"{self.config.TVDb.get_tvdb_obj(method_data, is_movie=self.library.is_movie).poster_url}"
    elif method_name == "file_poster":
        if os.path.exists(os.path.abspath(method_data)):
            self.posters[method_name] = os.path.abspath(method_data)
        else:
            logger.error(f"{self.Type} Error: Poster Path Does Not Exist: {os.path.abspath(method_data)}")

def background(self, method_name, method_data):
    if method_name == "url_background":
        try:
            image_response = self.config.get(method_data, headers=util.header())
            if image_response.status_code >= 400 or image_response.headers["Content-Type"] not in util.image_content_types:
                raise ConnectionError
            self.backgrounds[method_name] = method_data
        except ConnectionError:
            logger.warning(f"{self.Type} Warning: No Background Found at {method_data}")
    elif method_name == "tmdb_background":
        self.backgrounds[method_name] = self.config.TMDb.get_movie_show_or_collection(util.regex_first_int(method_data, 'TMDb ID'), self.library.is_movie).backdrop_url
    elif method_name == "tvdb_background":
        self.posters[method_name] = f"{self.config.TVDb.get_tvdb_obj(method_data, is_movie=self.library.is_movie).background_url}"
    elif method_name == "file_background":
        if os.path.exists(os.path.abspath(method_data)):
            self.backgrounds[method_name] = os.path.abspath(method_data)
        else:
            logger.error(f"{self.Type} Error: Background Path Does Not Exist: {os.path.abspath(method_data)}")

def details(self, method_name, method_data, method_final, methods):
    if method_name == "url_theme":
        self.url_theme = method_data
    elif method_name == "file_theme":
        if os.path.exists(os.path.abspath(method_data)):
            self.file_theme = os.path.abspath(method_data)
        else:
            logger.error(f"{self.Type} Error: Theme Path Does Not Exist: {os.path.abspath(method_data)}")
    elif method_name == "tmdb_region":
        self.tmdb_region = util.parse(self.Type, method_name, method_data, options=self.config.TMDb.iso_3166_1)
    elif method_name == "collection_mode":
        try:
            self.details[method_name] = util.check_collection_mode(method_data)
        except Failed as e:
            logger.error(e)
    elif method_name == "collection_filtering":
        if method_data and str(method_data).lower() in plex.collection_filtering_options:
            self.details[method_name] = str(method_data).lower()
        else:
            logger.error(f"Config Error: {method_data} collection_filtering invalid\n\tadmin (Always the server admin user)\n\tuser (User currently viewing the content)")
    elif method_name == "minimum_items":
        self.minimum = util.parse(self.Type, method_name, method_data, datatype="int", minimum=1)
    elif method_name == "cache_builders":
        self.details[method_name] = util.parse(self.Type, method_name, method_data, datatype="int", minimum=0)
    elif method_name == "default_percent":
        self.default_percent = util.parse(self.Type, method_name, method_data, datatype="int", minimum=1, maximum=100)
    elif method_name == "server_preroll":
        self.server_preroll = util.parse(self.Type, method_name, method_data)
    elif method_name == "ignore_ids":
        self.ignore_ids.extend(util.parse(self.Type, method_name, method_data, datatype="intlist"))
    elif method_name == "ignore_imdb_ids":
        self.ignore_imdb_ids.extend(util.parse(self.Type, method_name, method_data, datatype="list"))
    elif method_name == "label":
        if "label" in methods and "label.sync" in methods:
            raise Failed(f"{self.Type} Error: Cannot use label and label.sync together")
        if "label.remove" in methods and "label.sync" in methods:
            raise Failed(f"{self.Type} Error: Cannot use label.remove and label.sync together")
        if method_final == "label" and "label_sync_mode" in methods and self.data[methods["label_sync_mode"]] == "sync":
            self.details["label.sync"] = util.get_list(method_data) if method_data else []
        else:
            self.details[method_final] = util.get_list(method_data) if method_data else []
    elif method_name == "changes_webhooks":
        self.details[method_name] = util.parse(self.Type, method_name, method_data, datatype="list") if method_data else None
    elif method_name in scheduled_boolean:
        if isinstance(method_data, bool):
            self.details[method_name] = method_data
        elif isinstance(method_data, (int, float)):
            self.details[method_name] = method_data > 0
        elif str(method_data).lower() in ["t", "true"]:
            self.details[method_name] = True
        elif str(method_data).lower() in ["f", "false"]:
            self.details[method_name] = False
        else:
            try:
                util.schedule_check(method_name, util.parse(self.Type, method_name, method_data), self.current_time, self.config.run_hour)
                self.details[method_name] = True
            except NotScheduled:
                self.details[method_name] = False
    elif method_name in boolean_details:
        default = self.details[method_name] if method_name in self.details else None
        self.details[method_name] = util.parse(self.Type, method_name, method_data, datatype="bool", default=default)
    elif method_name in string_details:
        self.details[method_name] = str(method_data)

def item_details(self, method_name, method_data, method_mod, method_final, methods):
    if method_name == "item_label":
        if "item_label" in methods and "item_label.sync" in methods:
            raise Failed(f"{self.Type} Error: Cannot use item_label and item_label.sync together")
        if "item_label.remove" in methods and "item_label.sync" in methods:
            raise Failed(f"{self.Type} Error: Cannot use item_label.remove and item_label.sync together")
        self.item_details[method_final] = util.get_list(method_data) if method_data else []
    if method_name == "item_genre":
        if "item_genre" in methods and "item_genre.sync" in methods:
            raise Failed(f"{self.Type} Error: Cannot use item_genre and item_genre.sync together")
        if "item_genre.remove" in methods and "item_genre.sync" in methods:
            raise Failed(f"{self.Type} Error: Cannot use item_genre.remove and item_genre.sync together")
        self.item_details[method_final] = util.get_list(method_data) if method_data else []
    elif method_name == "item_edition":
        self.item_details[method_final] = str(method_data) if method_data else "" # noqa
    elif method_name == "non_item_remove_label":
        if not method_data:
            raise Failed(f"{self.Type} Error: non_item_remove_label is blank")
        self.item_details[method_final] = util.get_list(method_data)
    elif method_name in ["item_radarr_tag", "item_sonarr_tag"]:
        if method_name in methods and f"{method_name}.sync" in methods:
            raise Failed(f"{self.Type} Error: Cannot use {method_name} and {method_name}.sync together")
        if f"{method_name}.remove" in methods and f"{method_name}.sync" in methods:
            raise Failed(f"{self.Type} Error: Cannot use {method_name}.remove and {method_name}.sync together")
        if method_name in methods and f"{method_name}.remove" in methods:
            raise Failed(f"{self.Type} Error: Cannot use {method_name} and {method_name}.remove together")
        self.item_details[method_name] = util.get_list(method_data, lower=True)
        self.item_details["apply_tags"] = method_mod[1:] if method_mod else ""
    elif method_name == "item_refresh_delay":
        self.item_details[method_name] = util.parse(self.Type, method_name, method_data, datatype="int", default=0, minimum=0)
    elif method_name in item_bool_details:
        if util.parse(self.Type, method_name, method_data, datatype="bool", default=False):
            self.item_details[method_name] = True
        elif method_name in item_false_details:
            self.item_details[method_name] = False
    elif method_name in plex.item_advance_keys:
        key, options = plex.item_advance_keys[method_name]
        if method_name in advance_new_agent and self.library.agent not in plex.new_plex_agents:
            logger.error(f"Metadata Error: {method_name} attribute only works for with the New Plex Movie Agent and New Plex TV Agent")
        elif method_name in advance_show and not self.library.is_show:
            logger.error(f"Metadata Error: {method_name} attribute only works for show libraries")
        elif str(method_data).lower() not in options:
            logger.error(f"Metadata Error: {method_data} {method_name} attribute invalid")
        else:
            self.item_details[method_name] = str(method_data).lower() # noqa

def radarr(self, method_name, method_data):
    if method_name in ["radarr_add_missing", "radarr_add_existing", "radarr_upgrade_existing", "radarr_monitor_existing", "radarr_search", "radarr_monitor", "radarr_ignore_cache"]:
        self.radarr_details[method_name[7:]] = util.parse(self.Type, method_name, method_data, datatype="bool")
    elif method_name == "radarr_folder":
        self.radarr_details["folder"] = method_data
    elif method_name == "radarr_availability":
        if str(method_data).lower() in radarr.availability_translation:
            self.radarr_details["availability"] = str(method_data).lower()
        else:
            raise Failed(f"{self.Type} Error: {method_name} attribute must be either announced, cinemas, released or db")
    elif method_name == "radarr_quality":
        self.radarr_details["quality"] = method_data
    elif method_name == "radarr_tag":
        self.radarr_details["tag"] = util.get_list(method_data, lower=True)
    elif method_name == "radarr_taglist":
        self.builders.append((method_name, util.get_list(method_data, lower=True)))
    elif method_name == "radarr_all":
        self.builders.append((method_name, True))

def sonarr(self, method_name, method_data):
    if method_name in ["sonarr_add_missing", "sonarr_add_existing", "sonarr_upgrade_existing", "sonarr_monitor_existing", "sonarr_season", "sonarr_search", "sonarr_cutoff_search", "sonarr_ignore_cache"]:
        self.sonarr_details[method_name[7:]] = util.parse(self.Type, method_name, method_data, datatype="bool")
    elif method_name in ["sonarr_folder", "sonarr_quality", "sonarr_language"]:
        self.sonarr_details[method_name[7:]] = method_data
    elif method_name == "sonarr_monitor":
        if str(method_data).lower() in sonarr.monitor_translation:
            self.sonarr_details["monitor"] = str(method_data).lower()
        else:
            raise Failed(f"{self.Type} Error: {method_name} attribute must be either all, future, missing, existing, pilot, first, latest or none")
    elif method_name == "sonarr_series":
        if str(method_data).lower() in sonarr.series_types:
            self.sonarr_details["series"] = str(method_data).lower()
        else:
            raise Failed(f"{self.Type} Error: {method_name} attribute must be either standard, daily, or anime")
    elif method_name == "sonarr_tag":
        self.sonarr_details["tag"] = util.get_list(method_data, lower=True)
    elif method_name == "sonarr_taglist":
        self.builders.append((method_name, util.get_list(method_data, lower=True)))
    elif method_name == "sonarr_all":
        self.builders.append((method_name, True))

def anidb(self, method_name, method_data):
    if method_name == "anidb_popular":
        self.builders.append((method_name, util.parse(self.Type, method_name, method_data, datatype="int", default=30, maximum=30)))
    elif method_name in ["anidb_id", "anidb_relation"]:
        for anidb_id in self.config.AniDB.validate_anidb_ids(method_data):
            self.builders.append((method_name, anidb_id))
    elif method_name == "anidb_tag":
        for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
            dict_methods = {dm.lower(): dm for dm in dict_data}
            new_dictionary = {}
            if "tag" not in dict_methods:
                raise Failed(f"{self.Type} Error: anidb_tag tag attribute is required")
            elif not dict_data[dict_methods["tag"]]:
                raise Failed(f"{self.Type} Error: anidb_tag tag attribute is blank")
            else:
                new_dictionary["tag"] = util.regex_first_int(dict_data[dict_methods["tag"]], "AniDB Tag ID")
            new_dictionary["limit"] = util.parse(self.Type, "limit", dict_data, datatype="int", methods=dict_methods, default=0, parent=method_name, minimum=0)
            self.builders.append((method_name, new_dictionary))

def anilist(self, method_name, method_data):
    if method_name in ["anilist_id", "anilist_relations", "anilist_studio"]:
        for anilist_id in self.config.AniList.validate_anilist_ids(method_data, studio=method_name == "anilist_studio"):
            self.builders.append((method_name, anilist_id))
    elif method_name in ["anilist_popular", "anilist_trending", "anilist_top_rated"]:
        self.builders.append((method_name, util.parse(self.Type, method_name, method_data, datatype="int", default=10)))
    elif method_name == "anilist_userlist":
        for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
            dict_methods = {dm.lower(): dm for dm in dict_data}
            new_dictionary = {
                "username": util.parse(self.Type, "username", dict_data, methods=dict_methods, parent=method_name),
                "list_name": util.parse(self.Type, "list_name", dict_data, methods=dict_methods, parent=method_name),
                "sort_by": util.parse(self.Type, "sort_by", dict_data, methods=dict_methods, parent=method_name, default="score", options=anilist.userlist_sort_options),
            }
            score_dict = {}
            for search_method, search_data in dict_data.items():
                search_attr, modifier = os.path.splitext(str(search_method).lower())
                if search_attr == "score" and modifier in [".gt", ".gte", ".lt", ".lte"]:
                    score = util.parse(self.Type, search_method, dict_data, methods=dict_methods, datatype="int", default=-1, minimum=0, maximum=10, parent=method_name)
                    if score > -1:
                        score_dict[modifier] = score
                elif search_attr not in ["username", "list_name", "sort_by"]:
                    raise Failed(f"{self.Type} Error: {method_name} {search_method} attribute not supported")
            new_dictionary["score"] = score_dict
            self.builders.append((method_name, self.config.AniList.validate_userlist(new_dictionary)))
    elif method_name == "anilist_search":
        if self.current_time.month in [12, 1, 2]:           current_season = "winter"
        elif self.current_time.month in [3, 4, 5]:          current_season = "spring"
        elif self.current_time.month in [6, 7, 8]:          current_season = "summer"
        else:                                               current_season = "fall"
        default_year = self.current_year + 1 if self.current_time.month == 12 else self.current_year
        for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
            dict_methods = {dm.lower(): dm for dm in dict_data}
            new_dictionary = {}
            for search_method, search_data in dict_data.items():
                lower_method = str(search_method).lower()
                search_attr, modifier = os.path.splitext(lower_method)
                if lower_method not in anilist.searches:
                    raise Failed(f"{self.Type} Error: {method_name} {search_method} attribute not supported")
                elif search_attr == "season":
                    new_dictionary[search_attr] = util.parse(self.Type, search_attr, search_data, parent=method_name, default=current_season, options=util.seasons)
                    if new_dictionary[search_attr] == "current":
                        new_dictionary[search_attr] = current_season
                    if "year" not in dict_methods:
                        logger.warning(f"Collection Warning: {method_name} year attribute not found using this year: {default_year} by default")
                        new_dictionary["year"] = default_year
                elif search_attr == "year":
                    new_dictionary[search_attr] = util.parse(self.Type, search_attr, search_data, datatype="int", parent=method_name, default=default_year, minimum=1917, maximum=default_year + 1)
                elif search_data is None:
                    raise Failed(f"{self.Type} Error: {method_name} {search_method} attribute is blank")
                elif search_attr == "adult":
                    new_dictionary[search_attr] = util.parse(self.Type, search_attr, search_data, datatype="bool", parent=method_name)
                elif search_attr == "country":
                    new_dictionary[search_attr] = util.parse(self.Type, search_attr, search_data, options=anilist.country_codes, parent=method_name)
                elif search_attr == "source":
                    new_dictionary[search_attr] = util.parse(self.Type, search_attr, search_data, options=anilist.media_source, parent=method_name)
                elif search_attr in ["episodes", "duration", "score", "popularity"]:
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, datatype="int", parent=method_name)
                elif search_attr in ["format", "status", "genre", "tag", "tag_category"]:
                    new_dictionary[lower_method] = self.config.AniList.validate(search_attr.replace("_", " ").title(), util.parse(self.Type, search_method, search_data))
                elif search_attr in ["start", "end"]:
                    new_dictionary[search_attr] = util.parse(self.Type, search_attr, search_data, datatype="date", parent=method_name, date_return="%m/%d/%Y")
                elif search_attr == "min_tag_percent":
                    new_dictionary[search_attr] = util.parse(self.Type, search_attr, search_data, datatype="int", parent=method_name, minimum=0, maximum=100)
                elif search_attr == "search":
                    new_dictionary[search_attr] = str(search_data)
                elif lower_method not in ["sort_by", "limit"]:
                    raise Failed(f"{self.Type} Error: {method_name} {search_method} attribute not supported")
            if len(new_dictionary) == 0:
                raise Failed(f"{self.Type} Error: {method_name} must have at least one valid search option")
            new_dictionary["sort_by"] = util.parse(self.Type, "sort_by", dict_data, methods=dict_methods, parent=method_name, default="score", options=anilist.sort_options)
            new_dictionary["limit"] = util.parse(self.Type, "limit", dict_data, datatype="int", methods=dict_methods, default=0, parent=method_name)
            self.builders.append((method_name, new_dictionary))

def icheckmovies(self, method_name, method_data):
    if method_name.startswith("icheckmovies_list"):
        icheckmovies_lists = self.config.ICheckMovies.validate_icheckmovies_lists(method_data, self.language)
        for icheckmovies_list in icheckmovies_lists:
            self.builders.append(("icheckmovies_list", icheckmovies_list))
        if method_name.endswith("_details"):
            self.summaries[method_name] = self.config.ICheckMovies.get_list_description(icheckmovies_lists[0], self.language)

def imdb(self, method_name, method_data):
    if method_name == "imdb_id":
        for value in util.get_list(method_data):
            if str(value).startswith("tt"):
                self.builders.append((method_name, value))
            else:
                raise Failed(f"{self.Type} Error: imdb_id {value} must begin with tt")
    elif method_name == "imdb_list":
        try:
            for imdb_dict in self.config.IMDb.validate_imdb_lists(self.Type, method_data, self.language):
                self.builders.append((method_name, imdb_dict))
        except Failed as e:
            logger.error(e)
    elif method_name == "imdb_chart":
        for value in util.get_list(method_data):
            if value in imdb.movie_charts and not self.library.is_movie:
                raise Failed(f"{self.Type} Error: chart: {value} does not work with show libraries")
            elif value in imdb.show_charts and self.library.is_movie:
                raise Failed(f"{self.Type} Error: chart: {value} does not work with movie libraries")
            elif value in imdb.movie_charts or value in imdb.show_charts:
                self.builders.append((method_name, value))
            else:
                raise Failed(f"{self.Type} Error: chart: {value} is invalid options are {[i for i in imdb.charts]}")
    elif method_name == "imdb_watchlist":
        for imdb_user in self.config.IMDb.validate_imdb_watchlists(self.Type, method_data, self.language):
            self.builders.append((method_name, imdb_user))
    elif method_name == "imdb_award":
        for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
            dict_methods = {dm.lower(): dm for dm in dict_data}
            event_id = util.parse(self.Type, "event_id", dict_data, parent=method_name, methods=dict_methods, regex=(r"(ev\d+)", "ev0000003"))
            git_event, year_options = self.config.IMDb.get_event_years(event_id)
            if not year_options:
                raise Failed(f"{self.Type} Error: imdb_award event_id attribute: No event found at {imdb.base_url}/event/{event_id}")
            if "event_year" not in dict_methods:
                raise Failed(f"{self.Type} Error: imdb_award event_year attribute not found")
            og_year = dict_data[dict_methods["event_year"]]
            if not og_year:
                raise Failed(f"{self.Type} Error: imdb_award event_year attribute is blank")
            if og_year in ["all", "latest"]:
                event_year = og_year
            elif not isinstance(og_year, list) and "-" in str(og_year) and len(str(og_year)) > 7:
                try:
                    min_year, max_year = og_year.split("-")
                    min_year = int(min_year)
                    max_year = int(max_year) if max_year != "current" else None
                    event_year = []
                    for option in year_options:
                        check = int(option.split("-")[0] if "-" in option else option)
                        if check >= min_year and (max_year is None or check <= max_year):
                            event_year.append(option)
                except ValueError:
                    raise Failed(f"{self.Type} Error: imdb_award event_year attribute invalid: {og_year}")
            else:
                event_year = util.parse(self.Type, "event_year", og_year, parent=method_name, datatype="strlist", options=year_options)
            if (event_year == "all" or len(event_year) > 1) and not git_event:
                raise Failed(f"{self.Type} Error: Only specific events work when using multiple years. Event Options: [{', '.join([k for k in self.config.IMDb.events_validation])}]")
            award_filters = []
            if "award_filter" in dict_methods:
                if not dict_data[dict_methods["award_filter"]]:
                    raise Failed(f"{self.Type} Error: imdb_award award_filter attribute is blank")
                award_filters = util.parse(self.Type, "award_filter", dict_data[dict_methods["award_filter"]], datatype="lowerlist")
            category_filters = []
            if "category_filter" in dict_methods:
                if not dict_data[dict_methods["category_filter"]]:
                    raise Failed(f"{self.Type} Error: imdb_award category_filter attribute is blank")
                category_filters = util.parse(self.Type, "category_filter", dict_data[dict_methods["category_filter"]], datatype="lowerlist")
            final_category = []
            final_awards = []
            if award_filters or category_filters:
                award_names, category_names = self.config.IMDb.get_award_names(event_id, year_options[0] if event_year == "latest" else event_year)
                lower_award = {a.lower(): a for a in award_names if a}
                for award_filter in award_filters:
                    if award_filter in lower_award:
                        final_awards.append(lower_award[award_filter])
                    else:
                        raise Failed(f"{self.Type} Error: imdb_award award_filter attribute invalid: {award_filter} must be in in [{', '.join([v for _, v in lower_award.items()])}]")
                lower_category = {c.lower(): c for c in category_names if c}
                for category_filter in category_filters:
                    if category_filter in lower_category:
                        final_category.append(lower_category[category_filter])
                    else:
                        raise Failed(f"{self.Type} Error: imdb_award category_filter attribute invalid: {category_filter} must be in in [{', '.join([v for _, v in lower_category.items()])}]")
            self.builders.append((method_name, {
                "event_id": event_id, "event_year": event_year, "award_filter": final_awards if final_awards else None, "category_filter": final_category if final_category else None,
                "winning": util.parse(self.Type, "winning", dict_data, parent=method_name, methods=dict_methods, datatype="bool", default=False)
            }))
    elif method_name == "imdb_search":
        for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
            dict_methods = {dm.lower(): dm for dm in dict_data}
            new_dictionary = {"limit": util.parse(self.Type, "limit", dict_data, datatype="int", methods=dict_methods, minimum=0, default=100, parent=method_name)}
            for search_method, search_data in dict_data.items():
                lower_method = str(search_method).lower()
                search_attr, modifier = os.path.splitext(lower_method)
                if search_data is None:
                    raise Failed(f"{self.Type} Error: {method_name} {search_method} attribute is blank")
                elif lower_method not in imdb.imdb_search_attributes:
                    raise Failed(f"{self.Type} Error: {method_name} {search_method} attribute not supported")
                elif search_attr == "sort_by":
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, parent=method_name, options=imdb.sort_options)
                elif search_attr == "title":
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, parent=method_name)
                elif search_attr == "type":
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name, options=imdb.title_type_options)
                elif search_attr == "topic":
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name, options=imdb.topic_options)
                elif search_attr == "release":
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, datatype="date", parent=method_name, date_return="%Y-%m-%d")
                elif search_attr == "rating":
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, datatype="float", parent=method_name, minimum=0.1, maximum=10)
                elif search_attr in ["votes", "imdb_top", "imdb_bottom", "popularity", "runtime"]:
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, datatype="int", parent=method_name, minimum=0)
                elif search_attr == "genre":
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name, options=imdb.genre_options)
                elif search_attr == "event":
                    events = []
                    for event in util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name):
                        if event in imdb.event_options:
                            events.append(event)
                        else:
                            res = re.search(r'(ev\d+)', event)
                            if res:
                                events.append(res.group(1))
                            else:
                                raise Failed(f"{method_name} {search_method} attribute: {search_data} must match pattern ev\\d+ e.g. ev0000292 or be one of {', '.join([e for e in imdb.event_options])}")
                    if events:
                        new_dictionary[lower_method] = events
                elif search_attr == "company":
                    companies = []
                    for company in util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name):
                        if company in imdb.company_options:
                            companies.append(company)
                        else:
                            res = re.search(r'(co\d+)', company)
                            if res:
                                companies.append(res.group(1))
                            else:
                                raise Failed(f"{method_name} {search_method} attribute: {search_data} must match pattern co\\d+ e.g. co0098836 or be one of {', '.join([e for e in imdb.company_options])}")
                    if companies:
                        new_dictionary[lower_method] = companies
                elif search_attr == "content_rating":
                    final_list = []
                    for content in util.get_list(search_data):
                        if content:
                            final_dict = {"region": "US", "rating": None}
                            if not isinstance(content, dict):
                                final_dict["rating"] = str(content)
                            else:
                                if "rating" not in content or not content["rating"]:
                                    raise Failed(f"{method_name} {search_method} attribute: rating attribute is required")
                                final_dict["rating"] = str(content["rating"])
                                if "region" not in content or not content["region"]:
                                    logger.warning(f"{method_name} {search_method} attribute: region attribute not found defaulting to 'US'")
                                elif len(str(content["region"])) != 2:
                                    logger.warning(f"{method_name} {search_method} attribute: region attribute: {str(content['region'])} must be only 2 characters defaulting to 'US'")
                                else:
                                    final_dict["region"] = str(content["region"]).upper()
                            final_list.append(final_dict)
                    if final_list:
                        new_dictionary[lower_method] = final_list
                elif search_attr == "country":
                    countries = []
                    for country in util.parse(self.Type, search_method, search_data, datatype="upperlist", parent=method_name):
                        if country:
                            if len(str(country)) != 2:
                                raise Failed(f"{method_name} {search_method} attribute: {country} must be only 2 characters i.e. 'US'")
                            countries.append(str(country))
                    if countries:
                        new_dictionary[lower_method] = countries
                elif search_attr in ["keyword", "language", "alternate_version", "crazy_credit", "location", "goof", "plot", "quote", "soundtrack", "trivia"]:
                    new_dictionary[lower_method] = util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name)
                elif search_attr == "cast":
                    casts = []
                    for cast in util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name):
                        res = re.search(r'(nm\d+)', cast)
                        if res:
                            casts.append(res.group(1))
                        else:
                            raise Failed(f"{method_name} {search_method} attribute: {search_data} must match pattern nm\\d+ e.g. nm00988366")
                    if casts:
                        new_dictionary[lower_method] = casts
                elif search_attr == "series":
                    series = []
                    for show in util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name):
                        res = re.search(r'(tt\d+)', show)
                        if res:
                            series.append(res.group(1))
                        else:
                            raise Failed(f"{method_name} {search_method} attribute: {search_data} must match pattern tt\\d+ e.g. tt00988366")
                    if series:
                        new_dictionary[lower_method] = series
                elif search_attr == "list":
                    lists = []
                    for new_list in util.parse(self.Type, search_method, search_data, datatype="lowerlist", parent=method_name):
                        res = re.search(r'(ls\d+)', new_list)
                        if res:
                            lists.append(res.group(1))
                        else:
                            raise Failed(f"{method_name} {search_method} attribute: {search_data} must match pattern ls\\d+ e.g. ls000024621")
                    if lists:
                        new_dictionary[lower_method] = lists
                elif search_attr == "adult":
                    if util.parse(self.Type, search_method, search_data, datatype="bool", parent=method_name):
                        new_dictionary[lower_method] = True
                elif search_attr != "limit":
                    raise Failed(f"{self.Type} Error: {method_name} {search_method} attribute not supported")
            if len(new_dictionary) > 1:
                self.builders.append((method_name, new_dictionary))
            else:
                raise Failed(f"{self.Type} Error: {method_name} had no valid fields")

def letterboxd(self, method_name, method_data):
    if method_name.startswith("letterboxd_list"):
        letterboxd_lists = self.config.Letterboxd.validate_letterboxd_lists(self.Type, method_data, self.language)
        for letterboxd_list in letterboxd_lists:
            self.builders.append(("letterboxd_list", letterboxd_list))
        if method_name.endswith("_details"):
            self.summaries[method_name] = self.config.Letterboxd.get_list_description(letterboxd_lists[0]["url"], self.language)

def mal(self, method_name, method_data):
    if method_name == "mal_id":
        for mal_id in util.get_int_list(method_data, "MyAnimeList ID"):
            self.builders.append((method_name, mal_id))
    elif method_name in ["mal_all", "mal_airing", "mal_upcoming", "mal_tv", "mal_ova", "mal_movie", "mal_special", "mal_popular", "mal_favorite", "mal_suggested"]:
        self.builders.append((method_name, util.parse(self.Type, method_name, method_data, datatype="int", default=10, maximum=100 if method_name == "mal_suggested" else 500)))
    elif method_name in ["mal_season", "mal_userlist", "mal_search"]:
        for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
            dict_methods = {dm.lower(): dm for dm in dict_data}
            if method_name == "mal_season":
                if self.current_time.month in [1, 2, 3]:            default_season = "winter"
                elif self.current_time.month in [4, 5, 6]:          default_season = "spring"
                elif self.current_time.month in [7, 8, 9]:          default_season = "summer"
                else:                                               default_season = "fall"
                season = util.parse(self.Type, "season", dict_data, methods=dict_methods, parent=method_name, default=default_season, options=util.seasons)
                if season == "current":
                    season = default_season
                self.builders.append((method_name, {
                    "season": season,
                    "sort_by": util.parse(self.Type, "sort_by", dict_data, methods=dict_methods, parent=method_name, default="members", options=mal.season_sort_options, translation=mal.season_sort_translation),
                    "year": util.parse(self.Type, "year", dict_data, datatype="int", methods=dict_methods, default=self.current_year, parent=method_name, minimum=1917, maximum=self.current_year + 1),
                    "limit": util.parse(self.Type, "limit", dict_data, datatype="int", methods=dict_methods, default=100, parent=method_name, maximum=500),
                    "starting_only": util.parse(self.Type, "starting_only", dict_data, datatype="bool", methods=dict_methods, default=False, parent=method_name)
                }))
            elif method_name == "mal_userlist":
                self.builders.append((method_name, {
                    "username": util.parse(self.Type, "username", dict_data, methods=dict_methods, parent=method_name),
                    "status": util.parse(self.Type, "status", dict_data, methods=dict_methods, parent=method_name, default="all", options=mal.userlist_status),
                    "sort_by": util.parse(self.Type, "sort_by", dict_data, methods=dict_methods, parent=method_name, default="score", options=mal.userlist_sort_options, translation=mal.userlist_sort_translation),
                    "limit": util.parse(self.Type, "limit", dict_data, datatype="int", methods=dict_methods, default=100, parent=method_name, maximum=1000)
                }))
            elif method_name == "mal_search":
                final_attributes = {}
                final_text = "MyAnimeList Search"
                if "sort_by" in dict_methods:
                    sort = util.parse(self.Type, "sort_by", dict_data, methods=dict_methods, parent=method_name, options=mal.search_combos)
                    sort_type, sort_direction = sort.split(".")
                    final_text += f"\nSorted By: {sort}"
                    final_attributes["order_by"] = sort_type
                    final_attributes["sort"] = sort_direction
                limit = 0
                if "limit" in dict_methods:
                    limit = util.parse(self.Type, "limit", dict_data, datatype="int", default=0, methods=dict_methods, parent=method_name)
                    final_text += f"\nLimit: {limit if limit else 'None'}"
                if "query" in dict_methods:
                    final_attributes["q"] = util.parse(self.Type, "query", dict_data, methods=dict_methods, parent=method_name)
                    final_text += f"\nQuery: {final_attributes['q']}"
                if "prefix" in dict_methods:
                    final_attributes["letter"] = util.parse(self.Type, "prefix", dict_data, methods=dict_methods, parent=method_name)
                    final_text += f"\nPrefix: {final_attributes['letter']}"
                if "type" in dict_methods:
                    type_list = util.parse(self.Type, "type", dict_data, datatype="commalist", methods=dict_methods, parent=method_name, options=mal.search_types)
                    final_attributes["type"] = ",".join(type_list)
                    final_text += f"\nType: {' or '.join(type_list)}"
                if "status" in dict_methods:
                    final_attributes["status"] = util.parse(self.Type, "status", dict_data, methods=dict_methods, parent=method_name, options=mal.search_status)
                    final_text += f"\nStatus: {final_attributes['status']}"
                if "genre" in dict_methods:
                    genre_str = str(util.parse(self.Type, "genre", dict_data, methods=dict_methods, parent=method_name))
                    out_text, out_ints = util.parse_and_or(self.Type, 'Genre', genre_str, self.config.MyAnimeList.genres)
                    final_text += f"\nGenre: {out_text}"
                    final_attributes["genres"] = out_ints
                if "genre.not" in dict_methods:
                    genre_str = str(util.parse(self.Type, "genre.not", dict_data, methods=dict_methods, parent=method_name))
                    out_text, out_ints = util.parse_and_or(self.Type, 'Genre', genre_str, self.config.MyAnimeList.genres)
                    final_text += f"\nNot Genre: {out_text}"
                    final_attributes["genres_exclude"] = out_ints
                if "studio" in dict_methods:
                    studio_str = str(util.parse(self.Type, "studio", dict_data, methods=dict_methods, parent=method_name))
                    out_text, out_ints = util.parse_and_or(self.Type, 'Studio', studio_str, self.config.MyAnimeList.studios)
                    final_text += f"\nStudio: {out_text}"
                    final_attributes["producers"] = out_ints
                if "content_rating" in dict_methods:
                    final_attributes["rating"] = util.parse(self.Type, "content_rating", dict_data, methods=dict_methods, parent=method_name, options=mal.search_ratings)
                    final_text += f"\nContent Rating: {final_attributes['rating']}"
                if "score.gte" in dict_methods:
                    final_attributes["min_score"] = util.parse(self.Type, "score.gte", dict_data, datatype="float", methods=dict_methods, parent=method_name, minimum=0, maximum=10)
                    final_text += f"\nScore Greater Than or Equal: {final_attributes['min_score']}"
                elif "score.gt" in dict_methods:
                    original_score = util.parse(self.Type, "score.gt", dict_data, datatype="float", methods=dict_methods, parent=method_name, minimum=0, maximum=10)
                    final_attributes["min_score"] = original_score + 0.01
                    final_text += f"\nScore Greater Than: {original_score}"
                if "score.lte" in dict_methods:
                    final_attributes["max_score"] = util.parse(self.Type, "score.lte", dict_data, datatype="float", methods=dict_methods, parent=method_name, minimum=0, maximum=10)
                    final_text += f"\nScore Less Than or Equal: {final_attributes['max_score']}"
                elif "score.lt" in dict_methods:
                    original_score = util.parse(self.Type, "score.lt", dict_data, datatype="float", methods=dict_methods, parent=method_name, minimum=0, maximum=10)
                    final_attributes["max_score"] = original_score - 0.01
                    final_text += f"\nScore Less Than: {original_score}"
                if "min_score" in final_attributes and "max_score"  in final_attributes and final_attributes["max_score"] <= final_attributes["min_score"]:
                    raise Failed(f"{self.Type} Error: mal_search score.lte/score.lt attribute must be greater than score.gte/score.gt")
                if "sfw" in dict_methods:
                    sfw = util.parse(self.Type, "sfw", dict_data, datatype="bool", methods=dict_methods, parent=method_name)
                    if sfw:
                        final_attributes["sfw"] = 1
                        final_text += f"\nSafe for Work: {final_attributes['sfw']}"
                if not final_attributes:
                    raise Failed(f"{self.Type} Error: no mal_search attributes found")
                self.builders.append((method_name, (final_attributes, final_text, limit)))
    elif method_name in ["mal_genre", "mal_studio"]:
        logger.warning(f"Config Warning: {method_name} will run as a mal_search")
        item_list = util.parse(self.Type, method_name[4:], method_data, datatype="commalist")
        all_items = self.config.MyAnimeList.genres if method_name == "mal_genre" else self.config.MyAnimeList.studios
        final_items = [str(all_items[i]) for i in item_list if i in all_items]
        final_text = f"MyAnimeList Search\n{method_name[4:].capitalize()}: {' or '.join([str(all_items[i]) for i in final_items])}"
        self.builders.append(("mal_search", ({"genres" if method_name == "mal_genre" else "producers": ",".join(final_items)}, final_text, 0)))

def mojo(self, method_name, method_data):
    for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
        dict_methods = {dm.lower(): dm for dm in dict_data}
        final = {}
        if method_name == "mojo_record":
            final["chart"] = util.parse(self.Type, "chart", dict_data, methods=dict_methods, parent=method_name, options=mojo.top_options)
        elif method_name == "mojo_world":
            if "year" not in dict_methods:
                raise Failed(f"{self.Type} Error: {method_name} year attribute not found")
            og_year = dict_data[dict_methods["year"]]
            if not og_year:
                raise Failed(f"{self.Type} Error: {method_name} year attribute is blank")
            if og_year == "current":
                final["year"] = str(self.current_year) # noqa
            elif str(og_year).startswith("current-"):
                try:
                    final["year"] = str(self.current_year - int(og_year.split("-")[1])) # noqa
                    if final["year"] not in mojo.year_options:
                        raise Failed(f"{self.Type} Error: {method_name} year attribute final value must be 1977 or greater: {og_year}")
                except ValueError:
                    raise Failed(f"{self.Type} Error: {method_name} year attribute invalid: {og_year}")
            else:
                final["year"] = util.parse(self.Type, "year", dict_data, methods=dict_methods, parent=method_name, options=mojo.year_options)
        elif method_name == "mojo_all_time":
            final["chart"] = util.parse(self.Type, "chart", dict_data, methods=dict_methods, parent=method_name, options=mojo.chart_options)
            final["content_rating_filter"] = util.parse(self.Type, "content_rating_filter", dict_data, methods=dict_methods, parent=method_name, options=mojo.content_rating_options) if "content_rating_filter" in dict_methods else None
        elif method_name == "mojo_never":
            final["chart"] = util.parse(self.Type, "chart", dict_data, methods=dict_methods, parent=method_name, default="domestic", options=self.config.BoxOfficeMojo.never_options)
            final["never"] = str(util.parse(self.Type, "never", dict_data, methods=dict_methods, parent=method_name, default="1", options=mojo.never_in_options)) if "never" in dict_methods else "1"
        elif method_name in ["mojo_domestic", "mojo_international"]:
            dome = method_name == "mojo_domestic"
            final["range"] = util.parse(self.Type, "range", dict_data, methods=dict_methods, parent=method_name, options=mojo.dome_range_options if dome else mojo.intl_range_options)
            if not dome:
                final["chart"] = util.parse(self.Type, "chart", dict_data, methods=dict_methods, parent=method_name, default="international", options=self.config.BoxOfficeMojo.intl_options)
            chart_date = self.current_time
            if final["range"] != "daily":
                _m = "range_data" if final["range"] == "yearly" and "year" not in dict_methods and "range_data" in dict_methods else "year"
                if _m not in dict_methods:
                    raise Failed(f"{self.Type} Error: {method_name} {_m} attribute not found")
                og_year = dict_data[dict_methods[_m]]
                if not og_year:
                    raise Failed(f"{self.Type} Error: {method_name} {_m} attribute is blank")
                if str(og_year).startswith("current-"):
                    try:
                        chart_date = self.current_time - relativedelta(years=int(og_year.split("-")[1]))
                    except ValueError:
                        raise Failed(f"{self.Type} Error: {method_name} {_m} attribute invalid: {og_year}")
                else:
                    _y = util.parse(self.Type, _m, dict_data, methods=dict_methods, parent=method_name, default="current", options=mojo.year_options)
                    if _y != "current":
                        chart_date = self.current_time - relativedelta(years=self.current_time.year - _y)
            if final["range"] != "yearly":
                if "range_data" not in dict_methods:
                    raise Failed(f"{self.Type} Error: {method_name} range_data attribute not found")
                og_data = dict_data[dict_methods["range_data"]]
                if not og_data:
                    raise Failed(f"{self.Type} Error: {method_name} range_data attribute is blank")

                if final["range"] == "holiday":
                    final["range_data"] = util.parse(self.Type, "range_data", dict_data, methods=dict_methods, parent=method_name, options=mojo.holiday_options)
                elif final["range"] == "daily":
                    if og_data == "current":
                        final["range_data"] = datetime.strftime(self.current_time, "%Y-%m-%d") # noqa
                    elif str(og_data).startswith("current-"):
                        try:
                            final["range_data"] = datetime.strftime(self.current_time - timedelta(days=int(og_data.split("-")[1])), "%Y-%m-%d") # noqa
                        except ValueError:
                            raise Failed(f"{self.Type} Error: {method_name} range_data attribute invalid: {og_data}")
                    else:
                        final["range_data"] = util.parse(self.Type, "range_data", dict_data, methods=dict_methods, parent=method_name, default="current", datatype="date", date_return="%Y-%m-%d")
                        if final["range_data"] == "current":
                            final["range_data"] = datetime.strftime(self.current_time, "%Y-%m-%d") # noqa
                elif final["range"] in ["weekend", "weekly"]:
                    if str(og_data).startswith("current-"):
                        try:
                            final_date = chart_date - timedelta(weeks=int(og_data.split("-")[1]))
                            final_iso = final_date.isocalendar()
                            final["range_data"] = final_iso.week
                            final["year"] = final_iso.year
                        except ValueError:
                            raise Failed(f"{self.Type} Error: {method_name} range_data attribute invalid: {og_data}")
                    else:
                        _v = util.parse(self.Type, "range_data", dict_data, methods=dict_methods, parent=method_name, default="current", options=["current"] + [str(i) for i in range(1, 54)])
                        current_iso = chart_date.isocalendar()
                        final["range_data"] = current_iso.week if _v == "current" else _v
                        final["year"] = current_iso.year
                elif final["range"] == "monthly":
                    if str(og_data).startswith("current-"):
                        try:
                            final_date = chart_date - relativedelta(months=int(og_data.split("-")[1]))
                            final["range_data"] = final_date.month
                            final["year"] = final_date.year
                        except ValueError:
                            raise Failed(f"{self.Type} Error: {method_name} range_data attribute invalid: {og_data}")
                    else:
                        _v = util.parse(self.Type, "range_data", dict_data, methods=dict_methods, parent=method_name, default="current", options=["current"] + util.lower_months)
                        final["range_data"] = chart_date.month if _v == "current" else util.lower_months[_v]
                elif final["range"] == "quarterly":
                    if str(og_data).startswith("current-"):
                        try:
                            final_date = chart_date - relativedelta(months=int(og_data.split("-")[1]) * 3)
                            final["range_data"] = mojo.quarters[final_date.month]
                            final["year"] = final_date.year
                        except ValueError:
                            raise Failed(f"{self.Type} Error: {method_name} range_data attribute invalid: {og_data}")
                    else:
                        _v = util.parse(self.Type, "range_data", dict_data, methods=dict_methods, parent=method_name, default="current", options=mojo.quarter_options)
                        final["range_data"] = mojo.quarters[chart_date.month] if _v == "current" else _v
                elif final["range"] == "season":
                    _v = util.parse(self.Type, "range_data", dict_data, methods=dict_methods, parent=method_name, default="current", options=mojo.season_options)
                    final["range_data"] = mojo.seasons[chart_date.month] if _v == "current" else _v
            else:
                final["range_data"] = chart_date.year
            if "year" not in final:
                final["year"] = chart_date.year
            if final["year"] < 1977:
                raise Failed(f"{self.Type} Error: {method_name} attribute final date value must be on year 1977 or greater: {final['year']}")

        final["limit"] = util.parse(self.Type, "limit", dict_data, methods=dict_methods, parent=method_name, default=0, datatype="int", maximum=1000) if "limit" in dict_methods else 0
        self.builders.append((method_name, final))

def plex(self, method_name, method_data):
    if method_name in ["plex_all", "plex_pilots"]:
        self.builders.append((method_name, self.builder_level))
    elif method_name == "plex_watchlist":
        if method_data not in plex.watchlist_sorts:
            logger.warning(f"{self.Type} Warning: Watchlist sort: {method_data} invalid defaulting to added.asc")
        self.builders.append((method_name, method_data if method_data in plex.watchlist_sorts else "added.asc"))
    elif method_name in ["plex_search", "plex_collectionless"]:
        for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
            dict_methods = {dm.lower(): dm for dm in dict_data}
            if method_name == "plex_search":
                try:
                    self.builders.append((method_name, self.build_filter("plex_search", dict_data)))
                except FilterFailed as e:
                    if self.ignore_blank_results:
                        raise
                    else:
                        raise Failed(str(e))
            elif method_name == "plex_collectionless":
                prefix_list = util.parse(self.Type, "exclude_prefix", dict_data, datatype="list", methods=dict_methods) if "exclude_prefix" in dict_methods else []
                exact_list = util.parse(self.Type, "exclude", dict_data, datatype="list", methods=dict_methods) if "exclude" in dict_methods else []
                if len(prefix_list) == 0 and len(exact_list) == 0:
                    raise Failed(f"{self.Type} Error: you must have at least one exclusion")
                exact_list.append(self.name)
                self.builders.append((method_name, {"exclude_prefix": prefix_list, "exclude": exact_list}))
    else:
        try:
            self.builders.append(("plex_search", self.build_filter("plex_search", {"any": {method_name: method_data}})))
        except FilterFailed as e:
            if self.ignore_blank_results:
                raise
            else:
                raise Failed(str(e))

def reciperr(self, method_name, method_data):
    if method_name == "reciperr_list":
        for reciperr_list in self.config.Reciperr.validate_list(method_data):
            self.builders.append((method_name, reciperr_list))
    elif method_name == "stevenlu_popular":
        self.builders.append((method_name, util.parse(self.Type, method_name, method_data, "bool")))

def mdblist(self, method_name, method_data):
    for mdb_dict in self.config.MDBList.validate_mdblist_lists(self.Type, method_data):
        self.builders.append((method_name, mdb_dict))

def tautulli(self, method_name, method_data):
    for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
        dict_methods = {dm.lower(): dm for dm in dict_data}
        final_dict = {
            "list_type": "popular" if method_name == "tautulli_popular" else "watched",
            "list_days": util.parse(self.Type, "list_days", dict_data, datatype="int", methods=dict_methods, default=30, parent=method_name),
            "list_size": util.parse(self.Type, "list_size", dict_data, datatype="int", methods=dict_methods, default=10, parent=method_name),
            "list_minimum": util.parse(self.Type, "list_minimum", dict_data, datatype="int", methods=dict_methods, default=0, parent=method_name)
        }
        buff = final_dict["list_size"] * 3
        if self.library.Tautulli.has_section:
            buff = 0
        elif "list_buffer" in dict_methods:
            buff = util.parse(self.Type, "list_buffer", dict_data, datatype="int", methods=dict_methods, default=buff, parent=method_name)
        final_dict["list_buffer"] = buff
        self.builders.append((method_name, final_dict))

def tmdb(self, method_name, method_data):
    if method_name == "tmdb_discover":
        for dict_data in util.parse(self.Type, method_name, method_data, datatype="listdict"):
            dict_methods = {dm.lower(): dm for dm in dict_data}
            new_dictionary = {"limit": util.parse(self.Type, "limit", dict_data, datatype="int", methods=dict_methods, default=100, parent=method_name)}
            for discover_method, discover_data in dict_data.items():
                lower_method = str(discover_method).lower()
                discover_attr, modifier = os.path.splitext(lower_method)
                if discover_data is None:
                    raise Failed(f"{self.Type} Error: {method_name} {discover_method} attribute is blank")
                elif discover_method.lower() not in tmdb.discover_all:
                    raise Failed(f"{self.Type} Error: {method_name} {discover_method} attribute not supported")
                elif self.library.is_movie and discover_attr in tmdb.discover_tv_only:
                    raise Failed(f"{self.Type} Error: {method_name} {discover_method} attribute only works for show libraries")
                elif self.library.is_show and discover_attr in tmdb.discover_movie_only:
                    raise Failed(f"{self.Type} Error: {method_name} {discover_method} attribute only works for movie libraries")
                elif discover_attr == "region":
                    new_dictionary[discover_attr] = util.parse(self.Type, discover_method, discover_data.upper(), parent=method_name, regex=("^[A-Z]{2}$", "US"))
                elif discover_attr == "sort_by":
                    options = tmdb.discover_movie_sort if self.library.is_movie else tmdb.discover_tv_sort
                    new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, parent=method_name, options=options)
                elif discover_attr == "certification_country":
                    if "certification" in dict_data or "certification.lte" in dict_data or "certification.gte" in dict_data:
                        new_dictionary[lower_method] = discover_data
                    else:
                        raise Failed(f"{self.Type} Error: {method_name} {discover_attr} attribute: must be used with either certification, certification.lte, or certification.gte")
                elif discover_attr == "certification":
                    if "certification_country" in dict_data:
                        new_dictionary[lower_method] = discover_data
                    else:
                        raise Failed(f"{self.Type} Error: {method_name} {discover_method} attribute: must be used with certification_country")
                elif discover_attr == "watch_region":
                    if "with_watch_providers" in dict_data or "without_watch_providers" in dict_data or "with_watch_monetization_types" in dict_data:
                        new_dictionary[lower_method] = discover_data.upper()
                    else:
                        raise Failed(f"{self.Type} Error: {method_name} {discover_method} attribute: must be used with either with_watch_providers, without_watch_providers, or with_watch_monetization_types")
                elif discover_attr == "with_watch_monetization_types":
                    if "watch_region" in dict_data:
                        new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, parent=method_name, options=tmdb.discover_monetization_types)
                    else:
                        raise Failed(f"{self.Type} Error: {method_name} {discover_method} attribute: must be used with watch_region")
                elif discover_attr in tmdb.discover_booleans:
                    new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, datatype="bool", parent=method_name)
                elif discover_attr == "vote_average":
                    new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, datatype="float", parent=method_name)
                elif discover_attr == "with_status":
                    new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, datatype="int", parent=method_name, minimum=0, maximum=5)
                elif discover_attr == "with_type":
                    new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, datatype="int", parent=method_name, minimum=0, maximum=6)
                elif discover_attr in tmdb.discover_dates:
                    new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, datatype="date", parent=method_name, date_return="%m/%d/%Y")
                elif discover_attr in tmdb.discover_years:
                    new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, datatype="int", parent=method_name, minimum=1800, maximum=self.current_year + 1)
                elif discover_attr in tmdb.discover_ints:
                    new_dictionary[lower_method] = util.parse(self.Type, discover_method, discover_data, datatype="int", parent=method_name)
                elif discover_attr in tmdb.discover_strings:
                    new_dictionary[lower_method] = discover_data
                elif discover_attr != "limit":
                    raise Failed(f"{self.Type} Error: {method_name} {discover_method} attribute not supported")
            if len(new_dictionary) > 1:
                self.builders.append((method_name, new_dictionary))
            else:
                raise Failed(f"{self.Type} Error: {method_name} had no valid fields")
    elif method_name in tmdb.int_builders:
        self.builders.append((method_name, util.parse(self.Type, method_name, method_data, datatype="int", default=10)))
    else:
        values = self.config.TMDb.validate_tmdb_ids(method_data, method_name)
        if method_name in tmdb.details_builders:
            if method_name.startswith(("tmdb_collection", "tmdb_movie", "tmdb_show")):
                item = self.config.TMDb.get_movie_show_or_collection(values[0], self.library.is_movie)
                if item.overview:
                    self.summaries[method_name] = item.overview
                if item.backdrop_url:
                    self.backgrounds[method_name] = item.backdrop_url
                if item.poster_url:
                    self.posters[method_name] = item.poster_url
            elif method_name.startswith(("tmdb_actor", "tmdb_crew", "tmdb_director", "tmdb_producer", "tmdb_writer")):
                item = self.config.TMDb.get_person(values[0])
                if item.biography:
                    self.summaries[method_name] = item.biography
                if item.profile_path:
                    self.posters[method_name] = item.profile_url
            elif method_name.startswith("tmdb_list"):
                item = self.config.TMDb.get_list(values[0])
                if item.description:
                    self.summaries[method_name] = item.description
                if item.poster_url:
                    self.posters[method_name] = item.poster_url
        for value in values:
            self.builders.append((method_name[:-8] if method_name in tmdb.details_builders else method_name, value))

def trakt(self, method_name, method_data):
    if method_name.startswith("trakt_list"):
        trakt_lists = self.config.Trakt.validate_list(method_data)
        for trakt_list in trakt_lists:
            self.builders.append(("trakt_list", trakt_list))
        if method_name.endswith("_details"):
            try:
                self.summaries[method_name] = self.config.Trakt.list_description(trakt_lists[0])
            except Failed as e:
                logger.error(f"Trakt Error: List description not found: {e}")
    elif method_name == "trakt_boxoffice":
        if util.parse(self.Type, method_name, method_data, datatype="bool", default=False):
            self.builders.append((method_name, 10))
        else:
            raise Failed(f"{self.Type} Error: {method_name} must be set to true")
    elif method_name == "trakt_recommendations":
        self.builders.append((method_name, util.parse(self.Type, method_name, method_data, datatype="int", default=10, maximum=100)))
    elif method_name == "sync_to_trakt_list":
        if method_data not in self.config.Trakt.slugs:
            raise Failed(f"{self.Type} Error: {method_data} invalid. Options {', '.join(self.config.Trakt.slugs)}")
        self.sync_to_trakt_list = method_data
    elif method_name == "sync_missing_to_trakt_list":
        self.sync_missing_to_trakt_list = util.parse(self.Type, method_name, method_data, datatype="bool", default=False)
    elif method_name in trakt.builders:
        if method_name in ["trakt_chart", "trakt_userlist"]:
            trakt_dicts = method_data
            final_method = method_name
        elif method_name in ["trakt_watchlist", "trakt_collection"]:
            trakt_dicts = []
            for trakt_user in util.get_list(method_data, split=False):
                trakt_dicts.append({"userlist": method_name[6:], "user": trakt_user})
            final_method = "trakt_userlist"
        else:
            terms = method_name.split("_")
            trakt_dicts = {
                "chart": terms[1],
                "limit": util.parse(self.Type, method_name, method_data, datatype="int", default=10),
                "time_period": terms[2] if len(terms) > 2 else None
            }
            final_method = "trakt_chart"
        if method_name != final_method:
            logger.warning(f"{self.Type} Warning: {method_name} will run as {final_method}")
        for trakt_dict in self.config.Trakt.validate_chart(self.Type, final_method, trakt_dicts, self.library.is_movie):
            self.builders.append((final_method, trakt_dict))

def tvdb(self, method_name, method_data):
    values = util.get_list(method_data)
    if method_name.endswith("_details"):
        if method_name.startswith(("tvdb_movie", "tvdb_show")):
            item = self.config.TVDb.get_tvdb_obj(values[0], is_movie=method_name.startswith("tvdb_movie"))
            if item.summary:
                self.summaries[method_name] = item.summary
            if item.background_url:
                self.backgrounds[method_name] = item.background_url
            if item.poster_url:
                self.posters[method_name] = item.poster_url
        elif method_name.startswith("tvdb_list"):
            description, poster = self.config.TVDb.get_list_description(values[0])
            if description:
                self.summaries[method_name] = description
            if poster:
                self.posters[method_name] = poster
    for value in values:
        self.builders.append((method_name[:-8] if method_name.endswith("_details") else method_name, value))