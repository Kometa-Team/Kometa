import glob, logging, os, re
from datetime import datetime, timedelta
from modules import util
from modules.util import Failed
from plexapi.collection import Collections
from plexapi.exceptions import BadRequest, NotFound

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
        self.missing_movies = []
        self.missing_shows = []
        self.methods = []
        self.filters = []
        self.posters = {}
        self.backgrounds = {}
        self.summaries = {}
        self.schedule = ""
        self.rating_key_map = {}
        current_time = datetime.now()
        current_year = current_time.year

        if "template" in data:
            if not self.library.templates:
                raise Failed("Collection Error: No templates found")
            elif not data["template"]:
                raise Failed("Collection Error: template attribute is blank")
            else:
                for data_template in util.get_list(data["template"], split=False):
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
                                raise Failed(f"Collection Error: template sub-attribute {data_template[tm]} is blank")

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

                        for m in template:
                            if m not in self.data and m not in ["default", "optional"]:
                                if template[m]:
                                    def replace_txt(txt):
                                        txt = str(txt)
                                        for option in optional:
                                            if option not in data_template and f"<<{option}>>" in txt:
                                                raise Failed("remove attribute")
                                        for template_method in data_template:
                                            if template_method != "name" and f"<<{template_method}>>" in txt:
                                                txt = txt.replace(f"<<{template_method}>>", str(data_template[template_method]))
                                        if "<<collection_name>>" in txt:
                                            txt = txt.replace("<<collection_name>>", str(self.name))
                                        for dm in default:
                                            if f"<<{dm}>>" in txt:
                                                txt = txt.replace(f"<<{dm}>>", str(default[dm]))
                                        if txt in ["true", "True"]:                     return True
                                        elif txt in ["false", "False"]:                 return False
                                        else:
                                            try:                                            return int(txt)
                                            except ValueError:                              return txt
                                    try:
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
                                    except Failed:
                                        continue
                                    self.data[m] = attr
                                else:
                                    raise Failed(f"Collection Error: template attribute {m} is blank")

        skip_collection = True
        if "schedule" not in data:
            skip_collection = False
        elif not data["schedule"]:
            logger.error("Collection Error: schedule attribute is blank. Running daily")
            skip_collection = False
        else:
            schedule_list = util.get_list(data["schedule"])
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

        self.collectionless = "plex_collectionless" in data
        self.run_again = "run_again" in data

        if "tmdb_person" in data:
            if data["tmdb_person"]:
                valid_names = []
                for tmdb_id in util.get_int_list(data["tmdb_person"], "TMDb Person ID"):
                    person = config.TMDb.get_person(tmdb_id)
                    valid_names.append(person.name)
                    if hasattr(person, "biography") and person.biography:
                        self.summaries["tmdb_person"] = person.biography
                    if hasattr(person, "profile_path") and person.profile_path:
                        self.posters["tmdb_person"] = f"{config.TMDb.image_url}{person.profile_path}"
                if len(valid_names) > 0:                                        self.details["tmdb_person"] = valid_names
                else:                                                           raise Failed(f"Collection Error: No valid TMDb Person IDs in {data['tmdb_person']}")
            else:
                raise Failed("Collection Error: tmdb_person attribute is blank")

        for m in data:
            if "tmdb" in m and not config.TMDb:                             raise Failed(f"Collection Error: {m} requires TMDb to be configured")
            elif "trakt" in m and not config.Trakt:                         raise Failed(f"Collection Error: {m} requires Trakt todo be configured")
            elif "imdb" in m and not config.IMDb:                           raise Failed(f"Collection Error: {m} requires TMDb or Trakt to be configured")
            elif "tautulli" in m and not self.library.Tautulli:             raise Failed(f"Collection Error: {m} requires Tautulli to be configured")
            elif "mal" in m and not config.MyAnimeList:                     raise Failed(f"Collection Error: {m} requires MyAnimeList to be configured")
            elif data[m] is not None:
                logger.debug("")
                logger.debug(f"Method: {m}")
                logger.debug(f"Value: {data[m]}")
                if m in util.method_alias:
                    method_name = util.method_alias[m]
                    logger.warning(f"Collection Warning: {m} attribute will run as {method_name}")
                else:
                    method_name = m
                if method_name in util.show_only_lists and self.library.is_movie:
                    raise Failed(f"Collection Error: {method_name} attribute only works for show libraries")
                elif method_name in util.movie_only_lists and self.library.is_show:
                    raise Failed(f"Collection Error: {method_name} attribute only works for movie libraries")
                elif method_name in util.movie_only_searches and self.library.is_show:
                    raise Failed(f"Collection Error: {method_name} plex search only works for movie libraries")
                elif method_name not in util.collectionless_lists and self.collectionless:
                    raise Failed(f"Collection Error: {method_name} attribute does not work for Collectionless collection")
                elif method_name == "summary":
                    self.summaries[method_name] = data[m]
                elif method_name == "tmdb_summary":
                    self.summaries[method_name] = config.TMDb.get_movie_show_or_collection(util.regex_first_int(data[m], "TMDb ID"), self.library.is_movie).overview
                elif method_name == "tmdb_description":
                    self.summaries[method_name] = config.TMDb.get_list(util.regex_first_int(data[m], "TMDb List ID")).description
                elif method_name == "tmdb_biography":
                    self.summaries[method_name] = config.TMDb.get_person(util.regex_first_int(data[m], "TMDb Person ID")).biography
                elif method_name == "collection_mode":
                    if data[m] in ["default", "hide", "hide_items", "show_items", "hideItems", "showItems"]:
                        if data[m] == "hide_items":                                 self.details[method_name] = "hideItems"
                        elif data[m] == "show_items":                               self.details[method_name] = "showItems"
                        else:                                                       self.details[method_name] = data[m]
                    else:
                        raise Failed(f"Collection Error: {data[m]} collection_mode Invalid\n| \tdefault (Library default)\n| \thide (Hide Collection)\n| \thide_items (Hide Items in this Collection)\n| \tshow_items (Show this Collection and its Items)")
                elif method_name == "collection_order":
                    if data[m] in ["release", "alpha"]:
                        self.details[method_name] = data[m]
                    else:
                        raise Failed(f"Collection Error: {data[m]} collection_order Invalid\n| \trelease (Order Collection by release dates)\n| \talpha (Order Collection Alphabetically)")
                elif method_name == "url_poster":
                    self.posters[method_name] = data[m]
                elif method_name == "tmdb_poster":
                    self.posters[method_name] = f"{config.TMDb.image_url}{config.TMDb.get_movie_show_or_collection(util.regex_first_int(data[m], 'TMDb ID'), self.library.is_movie).poster_path}"
                elif method_name == "tmdb_profile":
                    self.posters[method_name] = f"{config.TMDb.image_url}{config.TMDb.get_person(util.regex_first_int(data[m], 'TMDb Person ID')).profile_path}"
                elif method_name == "file_poster":
                    if os.path.exists(data[m]):                                 self.posters[method_name] = os.path.abspath(data[m])
                    else:                                                       raise Failed(f"Collection Error: Poster Path Does Not Exist: {os.path.abspath(data[m])}")
                elif method_name == "url_background":
                    self.backgrounds[method_name] = data[m]
                elif method_name == "tmdb_background":
                    self.backgrounds[method_name] = f"{config.TMDb.image_url}{config.TMDb.get_movie_show_or_collection(util.regex_first_int(data[m], 'TMDb ID'), self.library.is_movie).poster_path}"
                elif method_name == "file_background":
                    if os.path.exists(data[m]):                                 self.backgrounds[method_name] = os.path.abspath(data[m])
                    else:                                                       raise Failed(f"Collection Error: Background Path Does Not Exist: {os.path.abspath(data[m])}")
                elif method_name == "label_sync_mode":
                    if data[m] in ["append", "sync"]:                           self.details[method_name] = data[m]
                    else:                                                       raise Failed("Collection Error: label_sync_mode attribute must be either 'append' or 'sync'")
                elif method_name == "sync_mode":
                    if data[m] in ["append", "sync"]:                           self.details[method_name] = data[m]
                    else:                                                       raise Failed("Collection Error: sync_mode attribute must be either 'append' or 'sync'")
                elif method_name in ["arr_tag", "label"]:
                    self.details[method_name] = util.get_list(data[m])
                elif method_name in util.boolean_details:
                    if isinstance(data[m], bool):                               self.details[method_name] = data[m]
                    else:                                                       raise Failed(f"Collection Error: {method_name} attribute must be either true or false")
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
                        def get_int(parent, method, data_in, default_in, minimum=1, maximum=None):
                            if method not in data_in:                                   logger.warning(f"Collection Warning: {parent} {method} attribute not found using {default} as default")
                            elif not data_in[method]:                                   logger.warning(f"Collection Warning: {parent} {method} attribute is blank using {default} as default")
                            elif isinstance(data_in[method], int) and data_in[method] >= minimum:
                                if maximum is None or data_in[method] <= maximum:           return data_in[method]
                                else:                                                       logger.warning(f"Collection Warning: {parent} {method} attribute {data_in[method]} invalid must an integer <= {maximum} using {default} as default")
                            else:                                                       logger.warning(f"Collection Warning: {parent} {method} attribute {data_in[method]} invalid must an integer >= {minimum} using {default} as default")
                            return default_in
                        if method_name == "filters":
                            for f in data[m]:
                                if f in util.method_alias or (f.endswith(".not") and f[:-4] in util.method_alias):
                                    filter_method = (util.method_alias[f[:-4]] + f[-4:]) if f.endswith(".not") else util.method_alias[f]
                                    logger.warning(f"Collection Warning: {f} filter will run as {filter_method}")
                                else:
                                    filter_method = f
                                if filter_method in util.movie_only_filters and self.library.is_show:
                                    raise Failed(f"Collection Error: {filter_method} filter only works for movie libraries")
                                elif data[m][f] is None:
                                    raise Failed(f"Collection Error: {filter_method} filter is blank")
                                elif filter_method == "year":
                                    filter_data = util.get_year_list(data[m][f], f"{filter_method} filter")
                                elif filter_method in ["max_age", "duration.gte", "duration.lte", "tmdb_vote_count.gte", "tmdb_vote_count.lte"]:
                                    filter_data = util.check_number(data[m][f], f"{filter_method} filter", minimum=1)
                                elif filter_method in ["year.gte", "year.lte"]:
                                    filter_data = util.check_number(data[m][f], f"{filter_method} filter", minimum=1800, maximum=current_year)
                                elif filter_method in ["rating.gte", "rating.lte"]:
                                    filter_data = util.check_number(data[m][f], f"{filter_method} filter", number_type="float", minimum=0.1, maximum=10)
                                elif filter_method in ["originally_available.gte", "originally_available.lte"]:
                                    filter_data = util.check_date(data[m][f], f"{filter_method} filter")
                                elif filter_method == "original_language":
                                    filter_data = util.get_list(data[m][f], lower=True)
                                elif filter_method == "collection":
                                    filter_data = data[m][f] if isinstance(data[m][f], list) else [data[m][f]]
                                elif filter_method in util.all_filters:
                                    filter_data = util.get_list(data[m][f])
                                else:
                                    raise Failed(f"Collection Error: {filter_method} filter not supported")
                                self.filters.append((filter_method, filter_data))
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
                                    logger.warning(f"Collection Warning: {s} plex search attribute will run as {search}")
                                else:
                                    search = s
                                if search in util.movie_only_searches and self.library.is_show:
                                    raise Failed(f"Collection Error: {search} plex search attribute only works for movie libraries")
                                elif util.remove_not(search) in used:
                                    raise Failed(f"Collection Error: Only one instance of {search} can be used try using it as a filter instead")
                                elif search in ["year", "year.not"]:
                                    years = util.get_year_list(data[m][s], search)
                                    if len(years) > 0:
                                        used.append(util.remove_not(search))
                                        searches.append((search, util.get_int_list(data[m][s], util.remove_not(search))))
                                elif search in util.plex_searches:
                                    used.append(util.remove_not(search))
                                    searches.append((search, util.get_list(data[m][s])))
                                else:
                                    logger.error(f"Collection Error: {search} plex search attribute not supported")
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
                                                raise Failed(f"Collection Error: {m} attribute {attr}: {attr_data} must match pattern ([a-z]{{2}})-([A-Z]{{2}}) e.g. en-US")
                                        elif attr == "region":
                                            if re.compile("^[A-Z]{2}$").match(str(attr_data)):
                                                new_dictionary[attr] = str(attr_data)
                                            else:
                                                raise Failed(f"Collection Error: {m} attribute {attr}: {attr_data} must match pattern ^[A-Z]{{2}}$ e.g. US")
                                        elif attr == "sort_by":
                                            if (self.library.is_movie and attr_data in util.discover_movie_sort) or (self.library.is_show and attr_data in util.discover_tv_sort):
                                                new_dictionary[attr] = attr_data
                                            else:
                                                raise Failed(f"Collection Error: {m} attribute {attr}: {attr_data} is invalid")
                                        elif attr == "certification_country":
                                            if "certification" in data[m] or "certification.lte" in data[m] or "certification.gte" in data[m]:
                                                new_dictionary[attr] = attr_data
                                            else:
                                                raise Failed(f"Collection Error: {m} attribute {attr}: must be used with either certification, certification.lte, or certification.gte")
                                        elif attr in ["certification", "certification.lte", "certification.gte"]:
                                            if "certification_country" in data[m]:
                                                new_dictionary[attr] = attr_data
                                            else:
                                                raise Failed(f"Collection Error: {m} attribute {attr}: must be used with certification_country")
                                        elif attr in ["include_adult", "include_null_first_air_dates", "screened_theatrically"]:
                                            if attr_data is True:
                                                new_dictionary[attr] = attr_data
                                        elif attr in ["primary_release_date.gte", "primary_release_date.lte", "release_date.gte", "release_date.lte", "air_date.gte", "air_date.lte", "first_air_date.gte", "first_air_date.lte"]:
                                            new_dictionary[attr] = util.check_date(attr_data, f"{m} attribute {attr}", return_string=True)
                                        elif attr in ["primary_release_year", "year", "first_air_date_year"]:
                                            new_dictionary[attr] = util.check_number(attr_data, f"{m} attribute {attr}", minimum=1800, maximum=current_year + 1)
                                        elif attr in ["vote_count.gte", "vote_count.lte", "vote_average.gte", "vote_average.lte", "with_runtime.gte", "with_runtime.lte"]:
                                            new_dictionary[attr] = util.check_number(attr_data, f"{m} attribute {attr}", minimum=1)
                                        elif attr in ["with_cast", "with_crew", "with_people", "with_companies", "with_networks", "with_genres", "without_genres", "with_keywords", "without_keywords", "with_original_language", "timezone"]:
                                            new_dictionary[attr] = attr_data
                                        else:
                                            raise Failed(f"Collection Error: {m} attribute {attr} not supported")
                                    elif attr == "limit":
                                        if isinstance(attr_data, int) and attr_data > 0:
                                            new_dictionary[attr] = attr_data
                                        else:
                                            raise Failed(f"Collection Error: {m} attribute {attr}: must be a valid number greater then 0")
                                    else:
                                        raise Failed(f"Collection Error: {m} attribute {attr} not supported")
                                else:
                                    raise Failed(f"Collection Error: {m} parameter {attr} is blank")
                            if len(new_dictionary) > 1:
                                self.methods.append((method_name, [new_dictionary]))
                            else:
                                raise Failed(f"Collection Error: {m} had no valid fields")
                        elif "tautulli" in method_name:
                            new_dictionary = {}
                            if method_name == "tautulli_popular":                   new_dictionary["list_type"] = "popular"
                            elif method_name == "tautulli_watched":                 new_dictionary["list_type"] = "watched"
                            else:                                                   raise Failed(f"Collection Error: {method_name} attribute not supported")

                            new_dictionary["list_days"] = get_int(method_name, "list_days", data[m], 30)
                            new_dictionary["list_size"] = get_int(method_name, "list_size", data[m], 10)
                            new_dictionary["list_buffer"] = get_int(method_name, "list_buffer", data[m], 20)
                            self.methods.append((method_name, [new_dictionary]))
                        elif method_name == "mal_season":
                            new_dictionary = {"sort_by": "anime_num_list_users"}
                            if "sort_by" not in data[m]:                            logger.warning("Collection Warning: mal_season sort_by attribute not found using members as default")
                            elif not data[m]["sort_by"]:                            logger.warning("Collection Warning: mal_season sort_by attribute is blank using members as default")
                            elif data[m]["sort_by"] not in util.mal_season_sort:    logger.warning(f"Collection Warning: mal_season sort_by attribute {data[m]['sort_by']} invalid must be either 'members' or 'score' using members as default")
                            else:                                                   new_dictionary["sort_by"] = util.mal_season_sort[data[m]["sort_by"]]

                            if current_time.month in [1, 2, 3]:                     new_dictionary["season"] = "winter"
                            elif current_time.month in [4, 5, 6]:                   new_dictionary["season"] = "spring"
                            elif current_time.month in [7, 8, 9]:                   new_dictionary["season"] = "summer"
                            elif current_time.month in [10, 11, 12]:                new_dictionary["season"] = "fall"

                            if "season" not in data[m]:                             logger.warning(f"Collection Warning: mal_season season attribute not found using the current season: {new_dictionary['season']} as default")
                            elif not data[m]["season"]:                             logger.warning(f"Collection Warning: mal_season season attribute is blank using the current season: {new_dictionary['season']} as default")
                            elif data[m]["season"] not in util.pretty_seasons:      logger.warning(f"Collection Warning: mal_season season attribute {data[m]['season']} invalid must be either 'winter', 'spring', 'summer' or 'fall' using the current season: {new_dictionary['season']} as default")
                            else:                                                   new_dictionary["season"] = data[m]["season"]

                            new_dictionary["year"] = get_int(method_name, "year", data[m], current_time.year, minimum=1917, maximum=current_time.year + 1)
                            new_dictionary["limit"] = get_int(method_name, "limit", data[m], 100, maximum=500)
                            self.methods.append((method_name, [new_dictionary]))
                        elif method_name == "mal_userlist":
                            new_dictionary = {"status": "all", "sort_by": "list_score"}
                            if "username" not in data[m]:                           raise Failed("Collection Error: mal_userlist username attribute is required")
                            elif not data[m]["username"]:                           raise Failed("Collection Error: mal_userlist username attribute is blank")
                            else:                                                   new_dictionary["username"] = data[m]["username"]

                            if "status" not in data[m]:                             logger.warning("Collection Warning: mal_season status attribute not found using all as default")
                            elif not data[m]["status"]:                             logger.warning("Collection Warning: mal_season status attribute is blank using all as default")
                            elif data[m]["status"] not in util.mal_userlist_status: logger.warning(f"Collection Warning: mal_season status attribute {data[m]['status']} invalid must be either 'all', 'watching', 'completed', 'on_hold', 'dropped' or 'plan_to_watch' using all as default")
                            else:                                                   new_dictionary["status"] = util.mal_userlist_status[data[m]["status"]]

                            if "sort_by" not in data[m]:                            logger.warning("Collection Warning: mal_season sort_by attribute not found using score as default")
                            elif not data[m]["sort_by"]:                            logger.warning("Collection Warning: mal_season sort_by attribute is blank using score as default")
                            elif data[m]["sort_by"] not in util.mal_userlist_sort:  logger.warning(f"Collection Warning: mal_season sort_by attribute {data[m]['sort_by']} invalid must be either 'score', 'last_updated', 'title' or 'start_date' using score as default")
                            else:                                                   new_dictionary["sort_by"] = util.mal_userlist_sort[data[m]["sort_by"]]

                            new_dictionary["limit"] = get_int(method_name, "limit", data[m], 100, maximum=1000)
                            self.methods.append((method_name, [new_dictionary]))
                    else:
                        raise Failed(f"Collection Error: {m} attribute is not a dictionary: {data[m]}")
                elif method_name in util.count_lists:
                    list_count = util.regex_first_int(data[m], "List Size", default=20)
                    if list_count < 1:
                        logger.warning(f"Collection Warning: {method_name} must be an integer greater then 0 defaulting to 20")
                        list_count = 20
                    self.methods.append((method_name, [list_count]))
                elif method_name in util.tmdb_lists:
                    values = config.TMDb.validate_tmdb_list(util.get_int_list(data[m], f"TMDb {util.tmdb_type[method_name]} ID"), util.tmdb_type[method_name])
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
                elif method_name in util.all_lists:
                    self.methods.append((method_name, util.get_list(data[m])))
                elif method_name not in util.other_attributes:
                    raise Failed(f"Collection Error: {method_name} attribute not supported")
            else:
                raise Failed(f"Collection Error: {m} attribute is blank")

        self.sync = self.library.sync_mode == "sync"
        if "sync_mode" in data:
            if not data["sync_mode"]:                                       logger.warning(f"Collection Warning: sync_mode attribute is blank using general: {self.library.sync_mode}")
            elif data["sync_mode"] not in ["append", "sync"]:               logger.warning(f"Collection Warning: {self.library.sync_mode} sync_mode invalid using general: {data['sync_mode']}")
            else:                                                           self.sync = data["sync_mode"] == "sync"

        self.do_arr = False
        if self.library.Radarr:
            self.do_arr = self.details["add_to_arr"] if "add_to_arr" in self.details else self.library.Radarr.add
        if self.library.Sonarr:
            self.do_arr = self.details["add_to_arr"] if "add_to_arr" in self.details else self.library.Sonarr.add

    def run_methods(self, collection_obj, collection_name, rating_key_map, movie_map, show_map):
        items_found = 0
        for method, values in self.methods:
            logger.debug("")
            logger.debug(f"Method: {method}")
            logger.debug(f"Values: {values}")
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
                logger.debug(f"Value: {value}")
                if method == "plex_all":
                    logger.info(f"Processing {pretty} {'Movies' if self.library.is_movie else 'Shows'}")
                    items = self.library.Plex.all()
                    items_found += len(items)
                elif method == "plex_collection":
                    items = value.items()
                    items_found += len(items)
                elif method == "plex_search":
                    search_terms = {}
                    for i, attr_pair in enumerate(value):
                        search_list = attr_pair[1]
                        final_method = attr_pair[0][:-4] + "!" if attr_pair[0][-4:] == ".not" else attr_pair[0]
                        if self.library.is_show:
                            final_method = "show." + final_method
                        search_terms[final_method] = search_list
                        ors = ""
                        for o, param in enumerate(attr_pair[1]):
                            or_des = " OR " if o > 0 else f"{attr_pair[0]}("
                            ors += f"{or_des}{param}"
                        logger.info(f"\t\t      AND {ors})" if i > 0 else f"Processing {pretty}: {ors})")
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
                        length = util.print_return(length, f"Processing: {i}/{len(all_items)} {item.title}")
                        add_item = True
                        for collection in item.collections:
                            if collection.tag.lower() in good_collections:
                                add_item = False
                                break
                        if add_item:
                            items.append(item)
                    items_found += len(items)
                    util.print_end(length, f"Processed {len(all_items)} {'Movies' if self.library.is_movie else 'Shows'}")
                elif "tautulli" in method:
                    items = self.library.Tautulli.get_items(self.library, time_range=value["list_days"], stats_count=value["list_size"], list_type=value["list_type"], stats_count_buffer=value["list_buffer"])
                    items_found += len(items)
                elif "anidb" in method:                             items_found += check_map(self.config.AniDB.get_items(method, value, self.library.Plex.language))
                elif "mal" in method:                               items_found += check_map(self.config.MyAnimeList.get_items(method, value))
                elif "tvdb" in method:                              items_found += check_map(self.config.TVDb.get_items(method, value, self.library.Plex.language))
                elif "imdb" in method:                              items_found += check_map(self.config.IMDb.get_items(method, value, self.library.Plex.language))
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
                        if self.do_arr and self.library.Radarr:
                            self.library.Radarr.add_tmdb([missing_id for title, missing_id in missing_movies_with_names], tag=self.details["arr_tag"])
                        if self.run_again:
                            self.missing_movies.extend([missing_id for title, missing_id in missing_movies_with_names])
                    if len(missing_shows) > 0 and self.library.is_show:
                        missing_shows_with_names = []
                        for missing_id in missing_shows:
                            try:
                                title = str(self.config.TVDb.get_series(self.library.Plex.language, tvdb_id=missing_id).title.encode("ascii", "replace").decode())
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
                        if self.do_arr and self.library.Sonarr:
                            self.library.Sonarr.add_tvdb([missing_id for title, missing_id in missing_shows_with_names], tag=self.details["arr_tag"])
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
        elif "tmdb_summary" in self.summaries:              summary = get_summary("tmdb_summary", self.summaries)
        elif "tmdb_biography" in self.summaries:            summary = get_summary("tmdb_biography", self.summaries)
        elif "tmdb_person" in self.summaries:               summary = get_summary("tmdb_person", self.summaries)
        elif "tmdb_collection_details" in self.summaries:   summary = get_summary("tmdb_collection_details", self.summaries)
        elif "tmdb_list_details" in self.summaries:         summary = get_summary("tmdb_list_details", self.summaries)
        elif "tmdb_actor_details" in self.summaries:        summary = get_summary("tmdb_actor_details", self.summaries)
        elif "tmdb_crew_details" in self.summaries:         summary = get_summary("tmdb_crew_details", self.summaries)
        elif "tmdb_director_details" in self.summaries:     summary = get_summary("tmdb_director_details", self.summaries)
        elif "tmdb_producer_details" in self.summaries:     summary = get_summary("tmdb_producer_details", self.summaries)
        elif "tmdb_writer_details" in self.summaries:       summary = get_summary("tmdb_writer_details", self.summaries)
        elif "tmdb_movie_details" in self.summaries:        summary = get_summary("tmdb_movie_details", self.summaries)
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
            if "label_sync_mode" in self.details and self.details["label_sync_mode"] == "sync":
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
                        folder = os.path.basename(os.path.dirname(item.locations[0]))
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
                        else:
                            logger.warning(f"No Folder: {os.path.join(path, folder)}")

        def set_image(image_method, images, is_background=False):
            if image_method in ['file_poster', 'asset_directory']:
                if is_background:                                   collection.uploadArt(filepath=images[image_method])
                else:                                               collection.uploadPoster(filepath=images[image_method])
                image_location = "File"
            else:
                if is_background:                                   collection.uploadArt(url=images[image_method])
                else:                                               collection.uploadPoster(url=images[image_method])
                image_location = "URL"
            logger.info(f"Detail: {image_method} updated collection {'background' if is_background else 'poster'} to [{image_location}] {images[image_method]}")

        if len(self.posters) > 1:
            logger.info(f"{len(self.posters)} posters found:")
            for p in self.posters:
                logger.info(f"Method: {p} Poster: {self.posters[p]}")

        if "url_poster" in self.posters:                    set_image("url_poster", self.posters)
        elif "file_poster" in self.posters:                 set_image("file_poster", self.posters)
        elif "tmdb_poster" in self.posters:                 set_image("tmdb_poster", self.posters)
        elif "tmdb_profile" in self.posters:                set_image("tmdb_profile", self.posters)
        elif "asset_directory" in self.posters:             set_image("asset_directory", self.posters)
        elif "tmdb_person" in self.posters:                 set_image("tmdb_person", self.posters)
        elif "tmdb_collection_details" in self.posters:     set_image("tmdb_collection", self.posters)
        elif "tmdb_actor_details" in self.posters:          set_image("tmdb_actor_details", self.posters)
        elif "tmdb_crew_details" in self.posters:           set_image("tmdb_crew_details", self.posters)
        elif "tmdb_director_details" in self.posters:       set_image("tmdb_director_details", self.posters)
        elif "tmdb_producer_details" in self.posters:       set_image("tmdb_producer_details", self.posters)
        elif "tmdb_writer_details" in self.posters:         set_image("tmdb_writer_details", self.posters)
        elif "tmdb_movie_details" in self.posters:          set_image("tmdb_movie", self.posters)
        elif "tmdb_show_details" in self.posters:           set_image("tmdb_show", self.posters)
        else:                                               logger.info("No poster to update")

        logger.info("")

        if len(self.backgrounds) > 1:
            logger.info(f"{len(self.backgrounds)} backgrounds found:")
            for b in self.backgrounds:
                logger.info(f"Method: {b} Background: {self.backgrounds[b]}")

        if "url_background" in self.backgrounds:            set_image("url_background", self.backgrounds, is_background=True)
        elif "file_background" in self.backgrounds:         set_image("file_poster", self.backgrounds, is_background=True)
        elif "tmdb_background" in self.backgrounds:         set_image("tmdb_poster", self.backgrounds, is_background=True)
        elif "asset_directory" in self.backgrounds:         set_image("asset_directory", self.backgrounds, is_background=True)
        elif "tmdb_collection_details" in self.backgrounds: set_image("tmdb_collection", self.backgrounds, is_background=True)
        elif "tmdb_movie_details" in self.backgrounds:      set_image("tmdb_movie", self.backgrounds, is_background=True)
        elif "tmdb_show_details" in self.backgrounds:       set_image("tmdb_show", self.backgrounds, is_background=True)
        else:                                               logger.info("No background to update")

    def run_collections_again(self, library, collection_obj, movie_map, show_map):
        collection_items = collection_obj.items() if isinstance(collection_obj, Collections) else []
        name = collection_obj.title if isinstance(collection_obj, Collections) else collection_obj
        rating_keys = [movie_map[mm] for mm in self.missing_movies if mm in movie_map]
        if library.is_show:
            rating_keys.extend([show_map[sm] for sm in self.missing_shows if sm in show_map])

        if len(rating_keys) > 0:
            for rating_key in rating_keys:
                try:
                    current = library.fetchItem(int(rating_key))
                except (BadRequest, NotFound):
                    logger.error(f"Plex Error: Item {rating_key} not found")
                    continue
                if current in collection_items:
                    logger.info(f"{name} Collection | = | {current.title}")
                else:
                    current.addCollection(name)
                    logger.info(f"{name} Collection | + | {current.title}")
            logger.info(f"{len(rating_keys)} {'Movie' if library.is_movie else 'Show'}{'s' if len(rating_keys) > 1 else ''} Processed")

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

        if len(self.missing_shows) > 0 and library.is_show:
            logger.info("")
            for missing_id in self.missing_shows:
                if missing_id not in show_map:
                    try:
                        title = str(self.config.TVDb.get_series(self.library.Plex.language, tvdb_id=missing_id).title.encode("ascii", "replace").decode())
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.details["show_missing"] is True:
                        logger.info(f"{name} Collection | ? | {title} (TVDb: {missing_id})")
            logger.info(f"{len(self.missing_shows)} Show{'s' if len(self.missing_shows) > 1 else ''} Missing")
