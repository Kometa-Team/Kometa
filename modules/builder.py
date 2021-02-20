import glob, logging, os, re
from datetime import datetime, timedelta
from modules import util
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

class CollectionBuilder:
    def __init__(self, config, library, name, data):
        self.config = config
        self.library = library
        self.name = name
        self.data = data
        self.details = {
            "arr_tag": None,
            "show_filtered": library.show_filtered,
            "show_missing": library.show_missing,
            "save_missing": library.save_missing
        }
        self.methods = []
        self.filters = []
        self.posters = []
        self.backgrounds = []
        self.schedule = None

        if "template" in data:
            if not self.library.templates:
                raise Failed("Collection Error: No templates found")
            elif not data["template"]:
                raise Failed("Collection Error: template attribute is blank")
            else:
                template_list = data["template"] if isinstance(data["template"], list) else [data["template"]]
                for data_template in template_list:
                    if not isinstance(data_template, dict):
                        raise Failed("Collection Error: template attribute is not a dictionary")
                    elif "name" not in data_template:
                        raise Failed("Collection Error: template sub-attribute name is required")
                    elif not data_template["name"]:
                        raise Failed("Collection Error: template sub-attribute name is blank")
                    elif data_template["name"] not in self.library.templates:
                        raise Failed("Collection Error: template {} not found".format(data_template["name"]))
                    elif not isinstance(self.library.templates[data_template["name"]], dict):
                        raise Failed("Collection Error: template {} is not a dictionary".format(data_template["name"]))
                    else:
                        for tm in data_template:
                            if not data_template[tm]:
                                raise Failed("Collection Error: template sub-attribute {} is blank".format(data_template[tm]))

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
                                            raise Failed("Collection Error: template default sub-attribute {} is blank".format(dv))
                                else:
                                    raise Failed("Collection Error: template sub-attribute default is not a dictionary")
                            else:
                                raise Failed("Collection Error: template sub-attribute default is blank")



                        for m in template:
                            if m not in self.data and m != "default":
                                if template[m]:
                                    attr = None
                                    def replace_txt(txt):
                                        txt = str(txt)
                                        for tm in data_template:
                                            if tm != "name" and "<<{}>>".format(tm) in txt:
                                                txt = txt.replace("<<{}>>".format(tm), str(data_template[tm]))
                                        if "<<collection_name>>" in txt:
                                            txt = txt.replace("<<collection_name>>", str(self.name))
                                        for dm in default:
                                            if "<<{}>>".format(dm) in txt:
                                                txt = txt.replace("<<{}>>".format(dm), str(default[dm]))
                                        if txt in ["true", "True"]:                     return True
                                        elif txt in ["false", "False"]:                 return False
                                        else:
                                            try:                                            return int(txt)
                                            except ValueError:                              return txt
                                    if isinstance(template[m], dict):
                                        attr = {}
                                        for sm in template[m]:
                                            if isinstance(template[m][sm], list):
                                                temp_list = []
                                                for li in template[m][sm]:
                                                    temp_list.append(replace_txt(li))
                                                attr[sm] = temp_list
                                            else:
                                                attr[sm] = replace_txt(template[m][sm])
                                    elif isinstance(template[m], list):
                                        attr = []
                                        for li in template[m]:
                                            if isinstance(li, dict):
                                                temp_dict = {}
                                                for sm in li:
                                                    temp_dict[sm] = replace_txt(li[sm])
                                                attr.append(temp_dict)
                                            else:
                                                attr.append(replace_txt(li))
                                    else:
                                        attr = replace_txt(template[m])
                                    self.data[m] = attr
                                else:
                                    raise Failed("Collection Error: template attribute {} is blank".format(m))

        skip_collection = True
        if "schedule" not in data:
            skip_collection = False
        elif not data["schedule"]:
            logger.error("Collection Error: schedule attribute is blank. Running daily")
            skip_collection = False
        else:
            schedule_list = util.get_list(data["schedule"])
            current_time = datetime.now()
            next_month = current_time.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
            for schedule in schedule_list:
                run_time = str(schedule).lower()
                if run_time.startswith("day") or run_time.startswith("daily"):
                    skip_collection = False
                if run_time.startswith("week") or run_time.startswith("month") or run_time.startswith("year"):
                    match = re.search("\\(([^)]+)\\)", run_time)
                    if match:
                        param = match.group(1)
                        if run_time.startswith("week"):
                            if param.lower() in util.days_alias:
                                weekday = util.days_alias[param.lower()]
                                self.schedule += "\nScheduled weekly on {}".format(util.pretty_days[weekday])
                                if weekday == current_time.weekday():
                                    skip_collection = False
                            else:
                                logger.error("Collection Error: weekly schedule attribute {} invalid must be a day of the weeek i.e. weekly(Monday)".format(schedule))
                        elif run_time.startswith("month"):
                            try:
                                if 1 <= int(param) <= 31:
                                    self.schedule += "\nScheduled monthly on the {}".format(util.make_ordinal(param))
                                    if current_time.day == int(param) or (current_time.day == last_day.day and int(param) > last_day.day):
                                        skip_collection = False
                                else:
                                    logger.error("Collection Error: monthly schedule attribute {} invalid must be between 1 and 31".format(schedule))
                            except ValueError:
                                logger.error("Collection Error: monthly schedule attribute {} invalid must be an integer".format(schedule))
                        elif run_time.startswith("year"):
                            match = re.match("^(1[0-2]|0?[1-9])/(3[01]|[12][0-9]|0?[1-9])$", param)
                            if match:
                                month = int(match.group(1))
                                day = int(match.group(2))
                                self.schedule += "\nScheduled yearly on {} {}".format(util.pretty_months[month], util.make_ordinal(day))
                                if current_time.month == month and (current_time.day == day or (current_time.day == last_day.day and day > last_day.day)):
                                    skip_collection = False
                            else:
                                logger.error("Collection Error: yearly schedule attribute {} invalid must be in the MM/DD format i.e. yearly(11/22)".format(schedule))
                    else:
                        logger.error("Collection Error: failed to parse schedule: {}".format(schedule))
                else:
                    logger.error("Collection Error: schedule attribute {} invalid".format(schedule))
        if self.schedule is None:
            skip_collection = False
        if skip_collection:
            raise Failed("Skipping Collection {}".format(c))

        logger.info("Scanning {} Collection".format(self.name))

        self.collectionless = "plex_collectionless" in data

        self.sync = self.library.sync_mode == "sync"
        if "sync_mode" in data:
            if not data["sync_mode"]:                                       logger.warning("Collection Warning: sync_mode attribute is blank using general: {}".format(self.library.sync_mode))
            elif data["sync_mode"] not in ["append", "sync"]:               logger.warning("Collection Warning: {} sync_mode invalid using general: {}".format(self.library.sync_mode, data["sync_mode"]))
            else:                                                           self.sync = data["sync_mode"] == "sync"

        if "tmdb_person" in data:
            if data["tmdb_person"]:
                valid_names = []
                for tmdb_id in util.get_int_list(data["tmdb_person"], "TMDb Person ID"):
                    person = config.TMDb.get_person(tmdb_id)
                    valid_names.append(person.name)
                    if "summary" not in self.details and hasattr(person, "biography") and person.biography:
                        self.details["summary"] = person.biography
                    if "poster" not in self.details and hasattr(person, "profile_path") and person.profile_path:
                        self.details["poster"] = ("url", "{}{}".format(config.TMDb.image_url, person.profile_path), "tmdb_person")
                if len(valid_names) > 0:                                        self.details["tmdb_person"] = valid_names
                else:                                                           raise Failed("Collection Error: No valid TMDb Person IDs in {}".format(data["tmdb_person"]))
            else:
                raise Failed("Collection Error: tmdb_person attribute is blank")

        for m in data:
            if "tmdb" in m and not config.TMDb:                             raise Failed("Collection Error: {} requires TMDb to be configured".format(m))
            elif "trakt" in m and not config.Trakt:                         raise Failed("Collection Error: {} requires Trakt todo be configured".format(m))
            elif "imdb" in m and not config.IMDb:                           raise Failed("Collection Error: {} requires TMDb or Trakt to be configured".format(m))
            elif "tautulli" in m and not self.library.Tautulli:             raise Failed("Collection Error: {} requires Tautulli to be configured".format(m))
            elif "mal" in m and not config.MyAnimeList:                     raise Failed("Collection Error: {} requires MyAnimeList to be configured".format(m))
            elif data[m] is not None:
                logger.debug("")
                logger.debug("Method: {}".format(m))
                logger.debug("Value: {}".format(data[m]))
                if m in util.method_alias:
                    method_name = util.method_alias[m]
                    logger.warning("Collection Warning: {} attribute will run as {}".format(m, method_name))
                else:
                    method_name = m
                if method_name in util.show_only_lists and self.library.is_movie:
                    raise Failed("Collection Error: {} attribute only works for show libraries".format(method_name))
                elif method_name in util.movie_only_lists and self.library.is_show:
                    raise Failed("Collection Error: {} attribute only works for movie libraries".format(method_name))
                elif method_name in util.movie_only_searches and self.library.is_show:
                    raise Failed("Collection Error: {} plex search only works for movie libraries".format(method_name))
                elif method_name not in util.collectionless_lists and self.collectionless:
                    raise Failed("Collection Error: {} attribute does not work for Collectionless collection".format(method_name))
                elif method_name == "tmdb_summary":
                    self.details["summary"] = config.TMDb.get_movie_show_or_collection(util.regex_first_int(data[m], "TMDb ID"), self.library.is_movie).overview
                elif method_name == "tmdb_description":
                    self.details["summary"] = config.TMDb.get_list(util.regex_first_int(data[m], "TMDb List ID")).description
                elif method_name == "tmdb_biography":
                    self.details["summary"] = config.TMDb.get_person(util.regex_first_int(data[m], "TMDb Person ID")).biography
                elif method_name == "collection_mode":
                    if data[m] in ["default", "hide", "hide_items", "show_items", "hideItems", "showItems"]:
                        if data[m] == "hide_items":                                 self.details[method_name] = "hideItems"
                        elif data[m] == "show_items":                               self.details[method_name] = "showItems"
                        else:                                                       self.details[method_name] = data[m]
                    else:
                        raise Failed("Collection Error: {} collection_mode Invalid\n| \tdefault (Library default)\n| \thide (Hide Collection)\n| \thide_items (Hide Items in this Collection)\n| \tshow_items (Show this Collection and its Items)".format(data[m]))
                elif method_name == "collection_order":
                    if data[m] in ["release", "alpha"]:
                        self.details[method_name] = data[m]
                    else:
                        raise Failed("Collection Error: {} collection_order Invalid\n| \trelease (Order Collection by release dates)\n| \talpha (Order Collection Alphabetically)".format(data[m]))
                elif method_name == "url_poster":
                    self.posters.append(("url", data[m], method_name))
                elif method_name == "tmdb_poster":
                    self.posters.append(("url", "{}{}".format(config.TMDb.image_url, config.TMDb.get_movie_show_or_collection(util.regex_first_int(data[m], "TMDb ID"), self.library.is_movie).poster_path), method_name))
                elif method_name == "tmdb_profile":
                    self.posters.append(("url", "{}{}".format(config.TMDb.image_url, config.TMDb.get_person(util.regex_first_int(data[m], "TMDb Person ID")).profile_path), method_name))
                elif method_name == "file_poster":
                    if os.path.exists(data[m]):                                 self.posters.append(("file", os.path.abspath(data[m]), method_name))
                    else:                                                       raise Failed("Collection Error: Poster Path Does Not Exist: {}".format(os.path.abspath(data[m])))
                elif method_name == "url_background":
                    self.backgrounds.append(("url", data[m], method_name))
                elif method_name == "tmdb_background":
                    self.backgrounds.append(("url", "{}{}".format(config.TMDb.image_url, config.TMDb.get_movie_show_or_collection(util.regex_first_int(data[m], "TMDb ID"), self.library.is_movie).poster_path), method_name))
                elif method_name == "file_background":
                    if os.path.exists(data[m]):                                 self.backgrounds.append(("file", os.path.abspath(data[m]), method_name))
                    else:                                                       raise Failed("Collection Error: Background Path Does Not Exist: {}".format(os.path.abspath(data[m])))
                elif method_name == "arr_tag":
                    self.details[method_name] = util.get_list(data[m])
                elif method_name in util.boolean_details:
                    if isinstance(data[m], bool):                               self.details[method_name] = data[m]
                    else:                                                       raise Failed("Collection Error: {} must be either true or false".format(method_name))
                elif method_name in util.all_details:
                    self.details[method_name] = data[m]
                elif method_name in ["year", "year.not"]:
                    self.methods.append(("plex_search", [[(method_name, util.get_year_list(data[m], method_name))]]))
                elif method_name in ["decade", "decade.not"]:
                    self.methods.append(("plex_search", [[(method_name, util.get_int_list(data[m], util.remove_not(method_name)))]]))
                elif method_name in util.tmdb_searches:
                    final_values = []
                    for value in util.get_list(data[m]):
                        if value.lower() == "tmdb" and "tmdb_person" in self.details:
                            for name in self.details["tmdb_person"]:
                                final_values.append(name)
                        else:
                            final_values.append(value)
                    self.methods.append(("plex_search", [[(method_name, final_values)]]))
                elif method_name in util.plex_searches:
                    self.methods.append(("plex_search", [[(method_name, util.get_list(data[m]))]]))
                elif method_name == "plex_all":
                    self.methods.append((method_name, [""]))
                elif method_name == "plex_collection":
                    self.methods.append((method_name, self.library.validate_collections(data[m] if isinstance(data[m], list) else [data[m]])))
                elif method_name == "anidb_popular":
                    list_count = util.regex_first_int(data[m], "List Size", default=40)
                    if 1 <= list_count <= 30:
                        self.methods.append((method_name, [list_count]))
                    else:
                        logger.warning("Collection Error: anidb_popular must be an integer between 1 and 30 defaulting to 30")
                        self.methods.append((method_name, [30]))
                elif method_name == "mal_id":
                    self.methods.append((method_name, util.get_int_list(data[m], "MyAnimeList ID")))
                elif method_name in ["anidb_id", "anidb_relation"]:
                    self.methods.append((method_name, config.AniDB.validate_anidb_list(util.get_int_list(data[m], "AniDB ID"), self.library.Plex.language)))
                elif method_name == "trakt_list":
                    self.methods.append((method_name, config.Trakt.validate_trakt_list(util.get_list(data[m]))))
                elif method_name == "trakt_watchlist":
                    self.methods.append((method_name, config.Trakt.validate_trakt_watchlist(util.get_list(data[m]), self.library.is_movie)))
                elif method_name == "imdb_list":
                    new_list = []
                    for imdb_list in util.get_list(data[m], split=False):
                        new_dictionary = {}
                        if isinstance(imdb_list, dict):
                            if "url" in imdb_list and imdb_list["url"]:                 imdb_url = imdb_list["url"]
                            else:                                                       raise Failed("Collection Error: imdb_list attribute url is required")
                            list_count = util.regex_first_int(imdb_list["limit"], "List Limit", default=0) if "limit" in imdb_list and imdb_list["limit"] else 0
                        else:
                            imdb_url = str(imdb_list)
                            list_count = 0
                        new_list.append({"url": imdb_url, "limit": list_count})
                    self.methods.append((method_name, new_list))
                elif method_name in util.dictionary_lists:
                    if isinstance(data[m], dict):
                        def get_int(parent, method, data, default, min=1, max=None):
                            if method not in data:                                      logger.warning("Collection Warning: {} {} attribute not found using {} as default".format(parent, method, default))
                            elif not data[method]:                                      logger.warning("Collection Warning: {} {} attribute is blank using {} as default".format(parent, method, default))
                            elif isinstance(data[method], int) and data[method] >= min:
                                if max is None or data[method] <= max:                      return data[method]
                                else:                                                       logger.warning("Collection Warning: {} {} attribute {} invalid must an integer <= {} using {} as default".format(parent, method, data[method], max, default))
                            else:                                                       logger.warning("Collection Warning: {} {} attribute {} invalid must an integer >= {} using {} as default".format(parent, method, data[method], min, default))
                            return default
                        if method_name == "filters":
                            for f in data[m]:
                                if f in util.method_alias or (f.endswith(".not") and f[:-4] in util.method_alias):
                                    filter = (util.method_alias[f[:-4]] + f[-4:]) if f.endswith(".not") else util.method_alias[f]
                                    logger.warning("Collection Warning: {} filter will run as {}".format(f, filter))
                                else:
                                    filter = f
                                if filter in util.movie_only_filters and self.library.is_show:   raise Failed("Collection Error: {} filter only works for movie libraries".format(filter))
                                elif data[m][f] is None:                                    raise Failed("Collection Error: {} filter is blank".format(filter))
                                elif filter in util.all_filters:                            self.filters.append((filter, data[m][f]))
                                else:                                                       raise Failed("Collection Error: {} filter not supported".format(filter))
                        elif method_name == "plex_collectionless":
                            new_dictionary = {}
                            prefix_list = []
                            if "exclude_prefix" in data[m] and data[m]["exclude_prefix"]:
                                if isinstance(data[m]["exclude_prefix"], list):             prefix_list.extend(data[m]["exclude_prefix"])
                                else:                                                       prefix_list.append(str(data[m]["exclude_prefix"]))
                            exact_list = []
                            if "exclude" in data[m] and data[m]["exclude"]:
                                if isinstance(data[m]["exclude"], list):                    exact_list.extend(data[m]["exclude"])
                                else:                                                       exact_list.append(str(data[m]["exclude"]))
                            if len(prefix_list) == 0 and len(exact_list) == 0:              raise Failed("Collection Error: you must have at least one exclusion")
                            self.details["add_to_arr"] = False
                            self.details["collection_mode"] = "hide"
                            self.sync = True
                            new_dictionary["exclude_prefix"] = prefix_list
                            new_dictionary["exclude"] = exact_list
                            self.methods.append((method_name, [new_dictionary]))
                        elif method_name == "plex_search":
                            searches = []
                            used = []
                            for s in data[m]:
                                if s in util.method_alias or (s.endswith(".not") and s[:-4] in util.method_alias):
                                    search = (util.method_alias[s[:-4]] + s[-4:]) if s.endswith(".not") else util.method_alias[s]
                                    logger.warning("Collection Warning: {} plex search attribute will run as {}".format(s, search))
                                else:
                                    search = s
                                if search in util.movie_only_searches and self.library.is_show:
                                    raise Failed("Collection Error: {} plex search attribute only works for movie libraries".format(search))
                                elif util.remove_not(search) in used:
                                    raise Failed("Collection Error: Only one instance of {} can be used try using it as a filter instead".format(search))
                                elif search in ["year", "year.not"]:
                                    years = util.get_year_list(data[m][s], search)
                                    if len(years) > 0:
                                        used.append(util.remove_not(search))
                                        searches.append((search, util.get_int_list(data[m][s], util.remove_not(search))))
                                elif search in util.plex_searches:
                                    used.append(util.remove_not(search))
                                    searches.append((search, util.get_list(data[m][s])))
                                else:
                                    logger.error("Collection Error: {} plex search attribute not supported".format(search))
                            self.methods.append((method_name, [searches]))
                        elif method_name == "tmdb_discover":
                            new_dictionary = {"limit": 100}
                            for attr in data[m]:
                                if data[m][attr]:
                                    attr_data = data[m][attr]
                                    if (self.library.is_movie and attr in util.discover_movie) or (self.library.is_show and attr in util.discover_tv):
                                        if attr == "language":
                                            if re.compile("([a-z]{2})-([A-Z]{2})").match(str(attr_data)):
                                                new_dictionary[attr] = str(attr_data)
                                            else:
                                                raise Failed("Collection Error: {} attribute {}: {} must match pattern ([a-z]{2})-([A-Z]{2}) e.g. en-US".format(m, attr, attr_data))
                                        elif attr == "region":
                                            if re.compile("^[A-Z]{2}$").match(str(attr_data)):
                                                new_dictionary[attr] = str(attr_data)
                                            else:
                                                raise Failed("Collection Error: {} attribute {}: {} must match pattern ^[A-Z]{2}$ e.g. US".format(m, attr, attr_data))
                                        elif attr == "sort_by":
                                            if (self.library.is_movie and attr_data in util.discover_movie_sort) or (self.library.is_show and attr_data in util.discover_tv_sort):
                                                new_dictionary[attr] = attr_data
                                            else:
                                                raise Failed("Collection Error: {} attribute {}: {} is invalid".format(m, attr, attr_data))
                                        elif attr == "certification_country":
                                            if "certification" in data[m] or "certification.lte" in data[m] or "certification.gte" in data[m]:
                                                new_dictionary[attr] = attr_data
                                            else:
                                                raise Failed("Collection Error: {} attribute {}: must be used with either certification, certification.lte, or certification.gte".format(m, attr))
                                        elif attr in ["certification", "certification.lte", "certification.gte"]:
                                            if "certification_country" in data[m]:
                                                new_dictionary[attr] = attr_data
                                            else:
                                                raise Failed("Collection Error: {} attribute {}: must be used with certification_country".format(m, attr))
                                        elif attr in ["include_adult", "include_null_first_air_dates", "screened_theatrically"]:
                                            if attr_data is True:
                                                new_dictionary[attr] = attr_data
                                        elif attr in ["primary_release_date.gte", "primary_release_date.lte", "release_date.gte", "release_date.lte", "air_date.gte", "air_date.lte", "first_air_date.gte", "first_air_date.lte"]:
                                            if re.compile("[0-1]?[0-9][/-][0-3]?[0-9][/-][1-2][890][0-9][0-9]").match(str(attr_data)):
                                                the_date = str(attr_data).split("/") if "/" in str(attr_data) else str(attr_data).split("-")
                                                new_dictionary[attr] = "{}-{}-{}".format(the_date[2], the_date[0], the_date[1])
                                            elif re.compile("[1-2][890][0-9][0-9][/-][0-1]?[0-9][/-][0-3]?[0-9]").match(str(attr_data)):
                                                the_date = str(attr_data).split("/") if "/" in str(attr_data) else str(attr_data).split("-")
                                                new_dictionary[attr] = "{}-{}-{}".format(the_date[0], the_date[1], the_date[2])
                                            else:
                                                raise Failed("Collection Error: {} attribute {}: {} must match pattern MM/DD/YYYY e.g. 12/25/2020".format(m, attr, attr_data))
                                        elif attr in ["primary_release_year", "year", "first_air_date_year"]:
                                            if isinstance(attr_data, int) and 1800 < attr_data and attr_data < 2200:
                                                new_dictionary[attr] = attr_data
                                            else:
                                                raise Failed("Collection Error: {} attribute {}: must be a valid year e.g. 1990".format(m, attr))
                                        elif attr in ["vote_count.gte", "vote_count.lte", "vote_average.gte", "vote_average.lte", "with_runtime.gte", "with_runtime.lte"]:
                                            if (isinstance(attr_data, int) or isinstance(attr_data, float)) and 0 < attr_data:
                                                new_dictionary[attr] = attr_data
                                            else:
                                                raise Failed("Collection Error: {} attribute {}: must be a valid number greater then 0".format(m, attr))
                                        elif attr in ["with_cast", "with_crew", "with_people", "with_companies", "with_networks", "with_genres", "without_genres", "with_keywords", "without_keywords", "with_original_language", "timezone"]:
                                            new_dictionary[attr] = attr_data
                                        else:
                                            raise Failed("Collection Error: {} attribute {} not supported".format(m, attr))
                                    elif attr == "limit":
                                        if isinstance(attr_data, int) and attr_data > 0:
                                            new_dictionary[attr] = attr_data
                                        else:
                                            raise Failed("Collection Error: {} attribute {}: must be a valid number greater then 0".format(m, attr))
                                    else:
                                        raise Failed("Collection Error: {} attribute {} not supported".format(m, attr))
                                else:
                                    raise Failed("Collection Error: {} parameter {} is blank".format(m, attr))
                            if len(new_dictionary) > 1:
                                self.methods.append((method_name, [new_dictionary]))
                            else:
                                raise Failed("Collection Error: {} had no valid fields".format(m))
                        elif "tautulli" in method_name:
                            new_dictionary = {}
                            if method_name == "tautulli_popular":                   new_dictionary["list_type"] = "popular"
                            elif method_name == "tautulli_watched":                 new_dictionary["list_type"] = "watched"
                            else:                                                   raise Failed("Collection Error: {} attribute not supported".format(method_name))

                            new_dictionary["list_days"] = get_int(method_name, "list_days", data[m], 30)
                            new_dictionary["list_size"] = get_int(method_name, "list_size", data[m], 10)
                            new_dictionary["list_buffer"] = get_int(method_name, "list_buffer", data[m], 20)
                            self.methods.append((method_name, [new_dictionary]))
                        elif method_name == "mal_season":
                            new_dictionary = {"sort_by": "anime_num_list_users"}
                            if "sort_by" not in data[m]:                            logger.warning("Collection Warning: mal_season sort_by attribute not found using members as default")
                            elif not data[m]["sort_by"]:                            logger.warning("Collection Warning: mal_season sort_by attribute is blank using members as default")
                            elif data[m]["sort_by"] not in util.mal_season_sort:    logger.warning("Collection Warning: mal_season sort_by attribute {} invalid must be either 'members' or 'score' using members as default".format(data[m]["sort_by"]))
                            else:                                                   new_dictionary["sort_by"] = util.mal_season_sort[data[m]["sort_by"]]

                            current_time = datetime.now()
                            if current_time.month in [1, 2, 3]:                     new_dictionary["season"] = "winter"
                            elif current_time.month in [4, 5, 6]:                   new_dictionary["season"] = "spring"
                            elif current_time.month in [7, 8, 9]:                   new_dictionary["season"] = "summer"
                            elif current_time.month in [10, 11, 12]:                new_dictionary["season"] = "fall"

                            if "season" not in data[m]:                             logger.warning("Collection Warning: mal_season season attribute not found using the current season: {} as default".format(new_dictionary["season"]))
                            elif not data[m]["season"]:                             logger.warning("Collection Warning: mal_season season attribute is blank using the current season: {} as default".format(new_dictionary["season"]))
                            elif data[m]["season"] not in util.pretty_seasons:      logger.warning("Collection Warning: mal_season season attribute {} invalid must be either 'winter', 'spring', 'summer' or 'fall' using the current season: {} as default".format(data[m]["season"], new_dictionary["season"]))
                            else:                                                   new_dictionary["season"] = data[m]["season"]

                            new_dictionary["year"] = get_int(method_name, "year", data[m], current_time.year, min=1917, max=current_time.year + 1)
                            new_dictionary["limit"] = get_int(method_name, "limit", data[m], 100, max=500)
                            self.methods.append((method_name, [new_dictionary]))
                        elif method_name == "mal_userlist":
                            new_dictionary = {"status": "all", "sort_by": "list_score"}
                            if "username" not in data[m]:                           raise Failed("Collection Error: mal_userlist username attribute is required")
                            elif not data[m]["username"]:                           raise Failed("Collection Error: mal_userlist username attribute is blank")
                            else:                                                   new_dictionary["username"] = data[m]["username"]

                            if "status" not in data[m]:                             logger.warning("Collection Warning: mal_season status attribute not found using all as default")
                            elif not data[m]["status"]:                             logger.warning("Collection Warning: mal_season status attribute is blank using all as default")
                            elif data[m]["status"] not in util.mal_userlist_status: logger.warning("Collection Warning: mal_season status attribute {} invalid must be either 'all', 'watching', 'completed', 'on_hold', 'dropped' or 'plan_to_watch' using all as default".format(data[m]["status"]))
                            else:                                                   new_dictionary["status"] = util.mal_userlist_status[data[m]["status"]]

                            if "sort_by" not in data[m]:                            logger.warning("Collection Warning: mal_season sort_by attribute not found using score as default")
                            elif not data[m]["sort_by"]:                            logger.warning("Collection Warning: mal_season sort_by attribute is blank using score as default")
                            elif data[m]["sort_by"] not in util.mal_userlist_sort:  logger.warning("Collection Warning: mal_season sort_by attribute {} invalid must be either 'score', 'last_updated', 'title' or 'start_date' using score as default".format(data[m]["sort_by"]))
                            else:                                                   new_dictionary["sort_by"] = util.mal_userlist_sort[data[m]["sort_by"]]

                            new_dictionary["limit"] = get_int(method_name, "limit", data[m], 100, max=1000)
                            self.methods.append((method_name, [new_dictionary]))
                    else:
                        raise Failed("Collection Error: {} attribute is not a dictionary: {}".format(m, data[m]))
                elif method_name in util.count_lists:
                    list_count = util.regex_first_int(data[m], "List Size", default=20)
                    if list_count < 1:
                        logger.warning("Collection Warning: {} must be an integer greater then 0 defaulting to 20".format(method_name))
                        list_count = 20
                    self.methods.append((method_name, [list_count]))
                elif method_name in util.tmdb_lists:
                    values = config.TMDb.validate_tmdb_list(util.get_int_list(data[m], "TMDb {} ID".format(util.tmdb_type[method_name])), util.tmdb_type[method_name])
                    if method_name[-8:] == "_details":
                        if method_name in ["tmdb_collection_details", "tmdb_movie_details", "tmdb_show_details"]:
                            item = config.TMDb.get_movie_show_or_collection(values[0], self.library.is_movie)
                            if "summary" not in self.details and hasattr(item, "overview") and item.overview:
                                self.details["summary"] = item.overview
                            if "background" not in self.details and hasattr(item, "backdrop_path") and item.backdrop_path:
                                self.details["background"] = ("url", "{}{}".format(config.TMDb.image_url, item.backdrop_path), method_name[:-8])
                            if "poster" not in self.details and hasattr(item, "poster_path") and item.poster_path:
                                self.details["poster"] = ("url", "{}{}".format(config.TMDb.image_url, item.poster_path), method_name[:-8])
                        else:
                            item = config.TMDb.get_list(values[0])
                            if "summary" not in self.details and hasattr(item, "description") and item.description:
                                self.details["summary"] = item.description
                        self.methods.append((method_name[:-8], values))
                    else:
                        self.methods.append((method_name, values))
                elif method_name in util.all_lists:
                    self.methods.append((method_name, util.get_list(data[m])))
                elif method_name not in util.other_attributes:
                    raise Failed("Collection Error: {} attribute not supported".format(method_name))
            else:
                raise Failed("Collection Error: {} attribute is blank".format(m))

        self.do_arr = False
        if self.library.Radarr:
            self.do_arr = self.details["add_to_arr"] if "add_to_arr" in self.details else self.library.Radarr.add
        if self.library.Sonarr:
            self.do_arr = self.details["add_to_arr"] if "add_to_arr" in self.details else self.library.Sonarr.add

    def run_methods(self, collection_obj, collection_name, map, movie_map, show_map):
        items_found = 0
        for method, values in self.methods:
            logger.debug("")
            logger.debug("Method: {}".format(method))
            logger.debug("Values: {}".format(values))
            pretty = util.pretty_names[method] if method in util.pretty_names else method
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
                            if movie_id in movie_map:                           items.append(movie_map[movie_id])
                            else:                                               missing_movies.append(movie_id)
                    if len(show_ids) > 0:
                        items_found_inside += len(show_ids)
                        for show_id in show_ids:
                            if show_id in show_map:                             items.append(show_map[show_id])
                            else:                                               missing_shows.append(show_id)
                    return items_found_inside
                logger.info("")
                logger.debug("Value: {}".format(value))
                if method == "plex_all":
                    logger.info("Processing {} {}".format(pretty, "Movies" if self.library.is_movie else "Shows"))
                    items = self.library.Plex.all()
                    items_found += len(items)
                elif method == "plex_collection":
                    items = value.items()
                    items_found += len(items)
                elif method == "plex_search":
                    search_terms = {}
                    output = ""
                    for i, attr_pair in enumerate(value):
                        search_list = attr_pair[1]
                        final_method = attr_pair[0][:-4] + "!" if attr_pair[0][-4:] == ".not" else attr_pair[0]
                        if self.library.is_show:
                            final_method = "show." + final_method
                        search_terms[final_method] = search_list
                        ors = ""
                        for o, param in enumerate(attr_pair[1]):
                            ors += "{}{}".format(" OR " if o > 0 else "{}(".format(attr_pair[0]), param)
                        logger.info("\t\t      AND {})".format(ors) if i > 0 else "Processing {}: {})".format(pretty, ors))
                    items = self.library.Plex.search(**search_terms)
                    items_found += len(items)
                elif method == "plex_collectionless":
                    good_collections = []
                    for col in self.library.get_all_collections():
                        keep_collection = True
                        for pre in value["exclude_prefix"]:
                            if col.title.startswith(pre) or (col.titleSort and col.titleSort.startswith(pre)):
                                keep_collection = False
                                break
                        for ext in value["exclude"]:
                            if col.title == ext or (col.titleSort and col.titleSort == ext):
                                keep_collection = False
                                break
                        if keep_collection:
                            good_collections.append(col.title.lower())

                    all_items = self.library.Plex.all()
                    length = 0
                    for i, item in enumerate(all_items, 1):
                        length = util.print_return(length, "Processing: {}/{} {}".format(i, len(all_items), item.title))
                        add_item = True
                        for collection in item.collections:
                            if collection.tag.lower() in good_collections:
                                add_item = False
                                break
                        if add_item:
                            items.append(item)
                    items_found += len(items)
                    util.print_end(length, "Processed {} {}".format(len(all_items), "Movies" if self.library.is_movie else "Shows"))
                elif "tautulli" in method:
                    items = self.library.Tautulli.get_items(self.library, time_range=value["list_days"], stats_count=value["list_size"], list_type=value["list_type"], stats_count_buffer=value["list_buffer"])
                    items_found += len(items)
                elif "anidb" in method:                             items_found += check_map(self.config.AniDB.get_items(method, value, self.library.Plex.language))
                elif "mal" in method:                               items_found += check_map(self.config.MyAnimeList.get_items(method, value))
                elif "tvdb" in method:                              items_found += check_map(self.config.TVDb.get_items(method, value, self.library.Plex.language))
                elif "imdb" in method:                              items_found += check_map(self.config.IMDb.get_items(method, value, self.library.Plex.language))
                elif "tmdb" in method:                              items_found += check_map(self.config.TMDb.get_items(method, value, self.library.is_movie))
                elif "trakt" in method:                             items_found += check_map(self.config.Trakt.get_items(method, value, self.library.is_movie))
                else:                                               logger.error("Collection Error: {} method not supported".format(method))

                if len(items) > 0:                                  map = self.library.add_to_collection(collection_obj if collection_obj else collection_name, items, self.filters, self.details["show_filtered"], map, movie_map, show_map)
                else:                                               logger.error("No items found to add to this collection ")

                if len(missing_movies) > 0 or len(missing_shows) > 0:
                    logger.info("")
                    if len(missing_movies) > 0:
                        not_lang = None
                        terms = None
                        for filter_method, filter_data in self.filters:
                            if filter_method.startswith("original_language"):
                                terms = util.get_list(filter_data, lower=True)
                                not_lang = filter_method.endswith(".not")
                                break

                        missing_movies_with_names = []
                        for missing_id in missing_movies:
                            try:
                                movie = self.config.TMDb.get_movie(missing_id)
                                title = str(movie.title)
                                if not_lang is None or (not_lang is True and movie.original_language not in terms) or (not_lang is False and movie.original_language in terms):
                                    missing_movies_with_names.append((title, missing_id))
                                    if self.details["show_missing"] is True:
                                        logger.info("{} Collection | ? | {} (TMDb: {})".format(collection_name, title, missing_id))
                                elif self.details["show_filtered"] is True:
                                    logger.info("{} Collection | X | {} (TMDb: {})".format(collection_name, title, missing_id))
                            except Failed as e:
                                logger.error(e)
                        logger.info("{} Movie{} Missing".format(len(missing_movies_with_names), "s" if len(missing_movies_with_names) > 1 else ""))
                        if self.details["save_missing"] is True:
                            self.library.add_missing(collection_name, missing_movies_with_names, True)
                        if self.do_arr and self.library.Radarr:
                            self.library.Radarr.add_tmdb([missing_id for title, missing_id in missing_movies_with_names], tag=self.details["arr_tag"])
                    if len(missing_shows) > 0 and self.library.is_show:
                        missing_shows_with_names = []
                        for missing_id in missing_shows:
                            try:
                                title = str(self.config.TVDb.get_series(self.library.Plex.language, tvdb_id=missing_id).title.encode("ascii", "replace").decode())
                                missing_shows_with_names.append((title, missing_id))
                                if self.details["show_missing"] is True:
                                    logger.info("{} Collection | ? | {} (TVDB: {})".format(collection_name, title, missing_id))
                            except Failed as e:
                                logger.error(e)
                        logger.info("{} Show{} Missing".format(len(missing_shows_with_names), "s" if len(missing_shows_with_names) > 1 else ""))
                        if self.details["save_missing"] is True:
                            self.library.add_missing(c, missing_shows_with_names, False)
                        if self.do_arr and self.library.Sonarr:
                            self.library.Sonarr.add_tvdb([missing_id for title, missing_id in missing_shows_with_names], tag=self.details["arr_tag"])

        if self.sync and items_found > 0:
            logger.info("")
            count_removed = 0
            for ratingKey, item in map.items():
                if item is not None:
                    logger.info("{} Collection | - | {}".format(collection_name, item.title))
                    item.removeCollection(collection_name)
                    count_removed += 1
            logger.info("{} {}{} Removed".format(count_removed, "Movie" if self.library.is_movie else "Show", "s" if count_removed == 1 else ""))
        logger.info("")

    def update_details(self, collection):
        edits = {}
        if "sort_title" in self.details:
            edits["titleSort.value"] = self.details["sort_title"]
            edits["titleSort.locked"] = 1
        if "content_rating" in self.details:
            edits["contentRating.value"] = self.details["content_rating"]
            edits["contentRating.locked"] = 1
        if "summary" in self.details:
            edits["summary.value"] = self.details["summary"]
            edits["summary.locked"] = 1
        if len(edits) > 0:
            logger.debug(edits)
            collection.edit(**edits)
            collection.reload()
            logger.info("Details: have been updated")
        if "collection_mode" in self.details:
            collection.modeUpdate(mode=self.details["collection_mode"])
        if "collection_order" in self.details:
            collection.sortUpdate(sort=self.details["collection_order"])

        if self.library.asset_directory:
            name_mapping = self.name
            if "name_mapping" in self.details:
                if self.details["name_mapping"]:                        name_mapping = self.details["name_mapping"]
                else:                                                   logger.error("Collection Error: name_mapping attribute is blank")
            path = os.path.join(self.library.asset_directory, "{}".format(name_mapping), "poster.*")
            matches = glob.glob(path)
            if len(matches) > 0:
                for match in matches:
                    self.posters.append(("file", os.path.abspath(match), "asset_directory"))
            elif len(self.posters) == 0 and "poster" not in self.details:
                logger.warning("poster not found at: {}".format(os.path.abspath(path)))
            path = os.path.join(self.library.asset_directory, "{}".format(name_mapping), "background.*")
            matches = glob.glob(path)
            if len(matches) > 0:
                for match in matches:
                    self.backgrounds.append(("file", os.path.abspath(match), "asset_directory"))
            elif len(self.backgrounds) == 0 and "background" not in self.details:
                logger.warning("background not found at: {}".format(os.path.abspath(path)))

        poster = util.choose_from_list(self.posters, "poster", list_type="tuple")
        if not poster and "poster" in self.details:             poster = self.details["poster"]
        if poster:
            if poster[0] == "url":                                  collection.uploadPoster(url=poster[1])
            else:                                                   collection.uploadPoster(filepath=poster[1])
            logger.info("Detail: {} updated poster to [{}] {}".format(poster[2], poster[0], poster[1]))

        background = util.choose_from_list(self.backgrounds, "background", list_type="tuple")
        if not background and "background" in self.details:     background = self.details["background"]
        if background:
            if background[0] == "url":                              collection.uploadArt(url=background[1])
            else:                                                   collection.uploadArt(filepath=background[1])
            logger.info("Detail: {} updated background to [{}] {}".format(background[2], background[0], background[1]))

        if self.library.asset_directory:
            path = os.path.join(self.library.asset_directory, "{}".format(name_mapping))
            if os.path.isdir(path):
                dirs = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
                if len(dirs) > 0:
                    for item in collection.items():
                        folder = os.path.basename(os.path.dirname(item.locations[0]))
                        if folder in dirs:
                            files = [file for file in os.listdir(os.path.join(path, folder)) if os.path.isfile(os.path.join(path, folder, file))]
                            poster_path = None
                            background_path = None
                            for file in files:
                                if poster_path is None and file.startswith("poster."):
                                    poster_path = os.path.join(path, folder, file)
                                if background_path is None and file.startswith("background."):
                                    background_path = os.path.join(path, folder, file)
                            if poster_path:
                                item.uploadPoster(filepath=poster_path)
                                logger.info("Detail: asset_directory updated {}'s poster to [file] {}".format(item.title, poster_path))
                            if background_path:
                                item.uploadArt(filepath=background_path)
                                logger.info("Detail: asset_directory updated {}'s background to [file] {}".format(item.title, background_path))
                            if poster_path is None and background_path is None:
                                logger.warning("No Files Found: {}".format(os.path.join(path, folder)))
                        else:
                            logger.warning("No Folder: {}".format(os.path.join(path, folder)))
