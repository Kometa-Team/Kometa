import math, operator, os, re, requests
from datetime import datetime
from modules import plex, ergast, util
from modules.util import Failed, YAML
from plexapi.exceptions import NotFound, BadRequest

logger = util.logger

all_auto = ["genre", "number", "list"]
ms_auto = [
    "actor", "year", "content_rating", "original_language", "tmdb_popular_people", "trakt_user_lists", "studio",
    "trakt_liked_lists", "trakt_people_list", "subtitle_language", "audio_language", "resolution", "decade"
]
auto = {
    "Movie": ["tmdb_collection", "country", "director", "producer", "writer"] + all_auto + ms_auto,
    "Show": ["network", "origin_country"] + all_auto + ms_auto,
    "Artist": ["mood", "style", "country"] + all_auto,
    "Video": ["country", "content_rating"] + all_auto
}
dynamic_attributes = [
    "type", "data", "exclude", "addons", "template", "template_variables", "other_template", "remove_suffix",
    "remove_prefix", "title_format", "key_name_override", "title_override", "test", "sync", "include", "other_name"
]
auto_type_translation = {"content_rating": "contentRating", "subtitle_language": "subtitleLanguage", "audio_language": "audioLanguage"}
default_templates = {
    "original_language": {"plex_all": True, "filters": {"original_language": "<<value>>"}},
    "origin_country": {"plex_all": True, "filters": {"origin_country": "<<value>>"}},
    "tmdb_collection": {"tmdb_collection_details": "<<value>>", "minimum_items": 2},
    "trakt_user_lists": {"trakt_list_details": "<<value>>"},
    "trakt_liked_lists": {"trakt_list_details": "<<value>>"},
    "tmdb_popular_people": {"tmdb_person": f"<<value>>", "plex_search": {"all": {"actor": "tmdb"}}},
    "trakt_people_list": {"tmdb_person": f"<<value>>", "plex_search": {"all": {"actor": "tmdb"}}}
}

def get_dict(attribute, attr_data, check_list=None, make_str=False):
    if check_list is None:
        check_list = []
    if attr_data and attribute in attr_data:
        if attr_data[attribute]:
            if isinstance(attr_data[attribute], dict):
                new_dict = {}
                for _name, _data in attr_data[attribute].items():
                    if make_str and str(_name) in check_list or not make_str and _name in check_list:
                        new_name = f'"{str(_name)}"' if make_str or not isinstance(_name, int) else _name
                        logger.warning(f"Config Warning: Skipping duplicate {attribute[:-1] if attribute[-1] == 's' else attribute}: {new_name}")
                    elif _data is None:
                        logger.warning(f"Config Warning: {attribute[:-1] if attribute[-1] == 's' else attribute}: {_name} has no data")
                    elif not isinstance(_data, dict):
                        logger.warning(f"Config Warning: {attribute[:-1] if attribute[-1] == 's' else attribute}: {_name} must be a dictionary")
                    elif attribute == "templates":
                        new_dict[str(_name)] = (_data, {})
                    else:
                        new_dict[str(_name) if make_str else _name] = _data
                return new_dict
            else:
                logger.error(f"Config Error: {attribute} must be a dictionary")
        else:
            logger.error(f"Config Error: {attribute} attribute is blank")
    return {}


class DataFile:
    def __init__(self, config, file_type, path, temp_vars, asset_directory):
        self.config = config
        self.library = None
        self.type = file_type
        self.path = path
        self.temp_vars = temp_vars
        self.asset_directory = asset_directory
        self.data_type = ""
        self.templates = {}

    def get_file_name(self):
        data = f"{util.github_base}{self.path}.yml" if self.type == "GIT" else self.path
        if "/" in data:
            return data[data.rfind("/") + 1:-4]
        elif "\\" in data:
            return data[data.rfind("\\") + 1:-4]
        else:
            return data

    def load_file(self, file_type, file_path):
        if file_type in ["URL", "Git", "Repo"]:
            if file_type == "Repo" and not self.config.custom_repo:
                raise Failed("Config Error: No custom_repo defined")
            content_path = file_path if file_type == "URL" else f"{self.config.custom_repo if file_type == 'Repo' else util.github_base}{file_path}.yml"
            response = self.config.get(content_path)
            if response.status_code >= 400:
                raise Failed(f"URL Error: No file found at {content_path}")
            yaml = YAML(input_data=response.content, check_empty=True)
        elif os.path.exists(os.path.abspath(file_path)):
            yaml = YAML(path=os.path.abspath(file_path), check_empty=True)
        else:
            raise Failed(f"File Error: File does not exist {os.path.abspath(file_path)}")
        return yaml.data

    def apply_template(self, name, data, template_call):
        if not self.templates:
            raise Failed(f"{self.data_type} Error: No templates found")
        elif not template_call:
            raise Failed(f"{self.data_type} Error: template attribute is blank")
        else:
            logger.debug(f"Value: {template_call}")
            new_attributes = {}
            for variables in util.get_list(template_call, split=False):
                if not isinstance(variables, dict):
                    raise Failed(f"{self.data_type} Error: template attribute is not a dictionary")
                elif "name" not in variables:
                    raise Failed(f"{self.data_type} Error: template sub-attribute name is required")
                elif not variables["name"]:
                    raise Failed(f"{self.data_type} Error: template sub-attribute name is blank")
                elif variables["name"] not in self.templates:
                    raise Failed(f"{self.data_type} Error: template {variables['name']} not found")
                elif not isinstance(self.templates[variables["name"]][0], dict):
                    raise Failed(f"{self.data_type} Error: template {variables['name']} is not a dictionary")
                else:
                    remove_variables = []
                    for tm in variables:
                        if variables[tm] is None:
                            remove_variables.append(tm)
                    optional = []
                    for remove_variable in remove_variables:
                        variables.pop(remove_variable)
                        optional.append(str(remove_variable))

                    name_var = f"{self.data_type.lower()}_name"
                    if name_var not in variables:
                        variables[name_var] = str(name)

                    variables["library_type"] = self.library.type.lower() if self.library else "items"

                    template_name = variables["name"]
                    template, temp_vars = self.templates[template_name]

                    for temp_key, temp_value in temp_vars.items():
                        variables[temp_key] = temp_value

                    for temp_key, temp_value in self.temp_vars.items():
                        variables[temp_key] = temp_value

                    for key, value in variables.copy().items():
                        variables[f"{key}_encoded"] = requests.utils.quote(str(value))

                    default = {}
                    if "default" in template:
                        if template["default"]:
                            if isinstance(template["default"], dict):
                                for dv in template["default"]:
                                    if str(dv) not in optional:
                                        if template["default"][dv] is not None:
                                            final_value = template["default"][dv]
                                            for key, value in variables.items():
                                                if f"<<{key}>>" in str(final_value):
                                                    final_value = str(final_value).replace(f"<<{key}>>", str(value))
                                            default[dv] = final_value
                                            default[f"{dv}_encoded"] = requests.utils.quote(str(final_value))
                                        else:
                                            raise Failed(f"{self.data_type} Error: template default sub-attribute {dv} is blank")
                            else:
                                raise Failed(f"{self.data_type} Error: template sub-attribute default is not a dictionary")
                        else:
                            raise Failed(f"{self.data_type} Error: template sub-attribute default is blank")

                    if "optional" in template:
                        if template["optional"]:
                            for op in util.get_list(template["optional"]):
                                if op not in default:
                                    optional.append(str(op))
                                    optional.append(f"{op}_encoded")
                                else:
                                    logger.warning(f"Template Warning: variable {op} cannot be optional if it has a default")
                        else:
                            raise Failed(f"{self.data_type} Error: template sub-attribute optional is blank")

                    sort_name = None
                    if "move_prefix" in template or "move_collection_prefix" in template:
                        prefix = None
                        if "move_prefix" in template:
                            prefix = template["move_prefix"]
                        elif "move_collection_prefix" in template:
                            logger.warning(f"{self.data_type} Error: template sub-attribute move_collection_prefix will run as move_prefix")
                            prefix = template["move_collection_prefix"]
                        if prefix:
                            for op in util.get_list(prefix):
                                if variables[name_var].startswith(op):
                                    sort_name = f"{variables[name_var][len(op):]}, {op}"
                                    break
                        else:
                            raise Failed(f"{self.data_type} Error: template sub-attribute move_prefix is blank")
                    variables[f"{self.data_type.lower()}_sort"] = sort_name if sort_name else variables[name_var]

                    def check_data(_method, _data):
                        if isinstance(_data, dict):
                            final_data = {}
                            for sm, sd in _data.items():
                                try:
                                    final_data[sm] = check_data(_method, sd)
                                except Failed:
                                    continue
                        elif isinstance(_data, list):
                            final_data = []
                            for li in _data:
                                try:
                                    final_data.append(check_data(_method, li))
                                except Failed:
                                    continue
                        else:
                            final_data = _data
                            def scan_text(og_txt, var, var_value):
                                if str(og_txt) == f"<<{var}>>":
                                    return var_value
                                elif f"<<{var}>>" in str(og_txt):
                                    return str(og_txt).replace(f"<<{var}>>", str(var_value))
                                else:
                                    return og_txt

                            for option in optional:
                                if option not in variables and f"<<{option}>>" in str(final_data):
                                    raise Failed
                            for variable, variable_data in variables.items():
                                if (variable == "collection_name" or variable == "playlist_name") and _method in ["radarr_tag", "item_radarr_tag", "sonarr_tag", "item_sonarr_tag"]:
                                    final_data = scan_text(final_data, variable, variable_data.replace(",", ""))
                                elif variable != "name":
                                    final_data = scan_text(final_data, variable, variable_data)
                            for dm, dd in default.items():
                                final_data = scan_text(final_data, dm, dd)
                        return final_data

                    for method_name, attr_data in template.items():
                        if method_name not in data and method_name not in ["default", "optional", "move_collection_prefix", "move_prefix"]:
                            if attr_data is None:
                                logger.error(f"Template Error: template attribute {method_name} is blank")
                                continue
                            if method_name in new_attributes:
                                logger.warning(f"Template Warning: template attribute: {method_name} from {variables['name']} skipped")
                            else:
                                try:
                                    new_attributes[method_name] = check_data(method_name, attr_data)
                                except Failed:
                                    continue
            return new_attributes

    def external_templates(self, data):
        if data and "external_templates" in data and data["external_templates"]:
            files = util.load_files(data["external_templates"], "external_templates")
            if not files:
                logger.error("Config Error: No Paths Found for external_templates")
            for file_type, template_file, temp_vars, _ in files:
                temp_data = self.load_file(file_type, template_file)
                if temp_data and isinstance(temp_data, dict) and "templates" in temp_data and temp_data["templates"] and isinstance(temp_data["templates"], dict):
                    for temp_key, temp_value in temp_data["templates"].items():
                        if temp_key not in self.templates:
                            self.templates[temp_key] = (temp_value, temp_vars)

class MetadataFile(DataFile):
    def __init__(self, config, library, file_type, path, temp_vars, asset_directory):
        super().__init__(config, file_type, path, temp_vars, asset_directory)
        self.data_type = "Collection"
        self.library = library
        if file_type == "Data":
            self.metadata = None
            self.collections = get_dict("collections", path, library.collections)
            self.templates = get_dict("templates", path)
        else:
            logger.info("")
            logger.separator(f"Loading Metadata {file_type}: {path}")
            logger.info("")
            data = self.load_file(self.type, self.path)
            self.metadata = get_dict("metadata", data, library.metadatas)
            self.templates = get_dict("templates", data)
            self.external_templates(data)
            self.collections = get_dict("collections", data, library.collections)
            self.dynamic_collections = get_dict("dynamic_collections", data)
            col_names = library.collections + [c for c in self.collections]
            for map_name, dynamic in self.dynamic_collections.items():
                logger.info("")
                logger.separator(f"Building {map_name} Dynamic Collections", space=False, border=False)
                logger.info("")
                try:
                    methods = {dm.lower(): dm for dm in dynamic}
                    for m in methods:
                        if m not in dynamic_attributes:
                            logger.warning(f"Config Warning: {methods[m]} attribute is invalid. Options: {', '.join(dynamic_attributes)}")
                    if "type" not in methods:
                        raise Failed(f"Config Error: {map_name} type attribute not found")
                    elif not dynamic[methods["type"]]:
                        raise Failed(f"Config Error: {map_name} type attribute is blank")
                    elif dynamic[methods["type"]].lower() not in auto[library.type]:
                        raise Failed(f"Config Error: {map_name} type attribute {dynamic[methods['type']].lower()} invalid Options: {auto[library.type]}")
                    elif dynamic[methods["type"]].lower() == "network" and library.agent not in plex.new_plex_agents:
                        raise Failed(f"Config Error: {map_name} type attribute: network only works with the New Plex TV Agent")
                    elif dynamic[methods["type"]].lower().startswith("trakt") and not self.config.Trakt:
                        raise Failed(f"Config Error: {map_name} type attribute: {dynamic[methods['type']]} requires trakt to be configured")
                    else:
                        auto_type = dynamic[methods["type"]].lower()
                        og_exclude = []
                        if "exclude" in self.temp_vars:
                            og_exclude = util.parse("Config", "exclude", self.temp_vars["exclude"], parent="template_variable", datatype="strlist")
                        elif "exclude" in methods:
                            og_exclude = util.parse("Config", "exclude", dynamic, parent=map_name, methods=methods, datatype="strlist")
                        include = []
                        if "include" in self.temp_vars:
                            include = util.parse("Config", "include", self.temp_vars["include"], parent="template_variable", datatype="strlist")
                        elif "include" in methods:
                            include = util.parse("Config", "include", dynamic, parent=map_name, methods=methods, datatype="strlist")
                        addons = util.parse("Config", "addons", dynamic, parent=map_name, methods=methods, datatype="dictliststr") if "addons" in methods else {}
                        exclude = [str(e) for e in og_exclude]
                        for k, v in addons.items():
                            if k in v:
                                logger.warning(f"Config Warning: {k} cannot be an addon for itself")
                            exclude.extend([y for y in v if y != k and y not in exclude])
                        default_title_format = "<<key_name>>"
                        default_template = None
                        auto_list = {}
                        all_keys = []
                        dynamic_data = None
                        logger.debug(exclude)
                        def _check_dict(check_dict):
                            for ck, cv in check_dict.items():
                                all_keys.append(ck)
                                if str(ck) not in exclude and str(cv) not in exclude:
                                    auto_list[str(ck)] = cv
                        if auto_type == "decade" and library.is_show:
                            all_items = library.get_all()
                            if addons:
                                raise Failed(f"Config Error: addons cannot be used with show decades")
                            addons = {}
                            all_keys = []
                            for i, item in enumerate(all_items, 1):
                                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                                if item.year:
                                    decade = str(int(math.floor(item.year / 10) * 10))
                                    if decade not in addons:
                                        addons[decade] = []
                                    if item.year not in addons[decade]:
                                        addons[decade].append(item.year)
                                        all_keys.append(item.year)
                            auto_list = {str(k): f"{k}s" for k in addons if str(k) not in exclude and f"{k}s" not in exclude}
                            default_template = {"smart_filter": {"limit": 50, "sort_by": "critic_rating.desc", "any": {"year": f"<<value>>"}}}
                            default_title_format = "Best <<library_type>>s of <<key_name>>"
                        elif auto_type in ["genre", "mood", "style", "country", "studio", "network", "year", "decade", "content_rating", "subtitle_language", "audio_language", "resolution"]:
                            search_tag = auto_type_translation[auto_type] if auto_type in auto_type_translation else auto_type
                            if library.is_show and auto_type in ["resolution", "subtitle_language", "audio_language"]:
                                tags = library.get_tags(f"episode.{search_tag}")
                            else:
                                tags = library.get_tags(search_tag)
                            if auto_type in ["subtitle_language", "audio_language"]:
                                all_keys = []
                                auto_list = {}
                                for i in tags:
                                    all_keys.append(str(i.key))
                                    final_title = self.config.TMDb.TMDb._iso_639_1[str(i.key)].english_name if str(i.key) in self.config.TMDb.TMDb._iso_639_1 else str(i.title)
                                    if all([x not in exclude for x in [final_title, str(i.title), str(i.key)]]):
                                        auto_list[str(i.key)] = final_title
                            elif auto_type in ["resolution", "decade"]:
                                all_keys = [str(i.key) for i in tags]
                                auto_list = {str(i.key): i.title for i in tags if str(i.title) not in exclude and str(i.key) not in exclude}
                            else:
                                all_keys = [str(i.title) for i in tags]
                                auto_list = {str(i.title): i.title for i in tags if str(i.title) not in exclude}
                            if library.is_music:
                                default_template = {"smart_filter": {"limit": 50, "sort_by": "plays.desc", "any": {f"artist_{auto_type}": f"<<value>>"}}}
                                default_title_format = "Most Played <<key_name>> <<library_type>>s"
                            elif auto_type == "resolution":
                                default_template = {"smart_filter": {"sort_by": "title.asc", "any": {auto_type: f"<<value>>"}}}
                                default_title_format = "<<key_name>> <<library_type>>s"
                            else:
                                default_template = {"smart_filter": {"limit": 50, "sort_by": "critic_rating.desc", "any": {f"{auto_type}.is" if auto_type == "studio" else auto_type: "<<value>>"}}}
                                default_title_format = "Best <<library_type>>s of <<key_name>>" if auto_type in ["year", "decade"] else "Top <<key_name>> <<library_type>>s"
                        elif auto_type == "tmdb_collection":
                            all_items = library.get_all()
                            for i, item in enumerate(all_items, 1):
                                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                                tmdb_id, tvdb_id, imdb_id = library.get_ids(item)
                                tmdb_item = config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=True)
                                if tmdb_item and tmdb_item.collection_id:
                                    all_keys.append(str(tmdb_item.collection_id))
                                    if str(tmdb_item.collection_id) not in exclude and tmdb_item.collection_name not in exclude:
                                        auto_list[str(tmdb_item.collection_id)] = tmdb_item.collection_name
                            logger.exorcise()
                        elif auto_type == "original_language":
                            all_items = library.get_all()
                            for i, item in enumerate(all_items, 1):
                                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                                tmdb_id, tvdb_id, imdb_id = library.get_ids(item)
                                tmdb_item = config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=library.type == "Movie")
                                if tmdb_item and tmdb_item.language_iso:
                                    all_keys.append(tmdb_item.language_iso)
                                    if tmdb_item.language_iso not in exclude and tmdb_item.language_name not in exclude:
                                        auto_list[tmdb_item.language_iso] = tmdb_item.language_name
                            logger.exorcise()
                            default_title_format = "<<key_name>> <<library_type>>s"
                        elif auto_type == "origin_country":
                            all_items = library.get_all()
                            for i, item in enumerate(all_items, 1):
                                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                                tmdb_id, tvdb_id, imdb_id = library.get_ids(item)
                                tmdb_item = config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=library.type == "Movie")
                                if tmdb_item and tmdb_item.countries:
                                    for country in tmdb_item.countries:
                                        all_keys.append(country.iso_3166_1.lower())
                                        if country.iso_3166_1.lower() not in exclude and country.name not in exclude:
                                            auto_list[country.iso_3166_1.lower()] = country.name
                            logger.exorcise()
                            default_title_format = "<<key_name>> <<library_type>>s"
                        elif auto_type in ["actor", "director", "writer", "producer"]:
                            people = {}
                            if "data" not in methods:
                                raise Failed(f"Config Error: {map_name} data attribute not found")
                            elif "data" in self.temp_vars:
                                dynamic_data = util.parse("Config", "data", self.temp_vars["data"], datatype="dict")
                            else:
                                dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="dict")
                            person_methods = {am.lower(): am for am in dynamic_data}
                            if "actor_depth" in person_methods:
                                person_methods["depth"] = person_methods.pop("actor_depth")
                            if "actor_minimum" in person_methods:
                                person_methods["minimum"] = person_methods.pop("actor_minimum")
                            if "number_of_actors" in person_methods:
                                person_methods["limit"] = person_methods.pop("number_of_actors")
                            person_depth = util.parse("Config", "depth", dynamic_data, parent=f"{map_name} data", methods=person_methods, datatype="int", default=3, minimum=1)
                            person_minimum = util.parse("Config", "minimum", dynamic_data, parent=f"{map_name} data", methods=person_methods, datatype="int", default=3, minimum=1) if "minimum" in person_methods else None
                            person_limit = util.parse("Config", "limit", dynamic_data, parent=f"{map_name} data", methods=person_methods, datatype="int", default=25, minimum=1) if "limit" in person_methods else None
                            for i, item in enumerate(library.get_all(), 1):
                                try:
                                    item = self.library.reload(item)
                                    for person in getattr(item, f"{auto_type}s")[:person_depth]:
                                        if person.id not in people:
                                            people[person.id] = {"name": person.tag, "count": 0}
                                        people[person.id]["count"] += 1
                                except Failed as e:
                                    logger.error(f"Plex Error: {e}")
                            roles = [data for _, data in people.items()]
                            roles.sort(key=operator.itemgetter('count'), reverse=True)
                            if not person_minimum:
                                person_minimum = 1 if person_limit else 3
                            if not person_limit:
                                person_limit = len(roles)
                            person_count = 0
                            for role in roles:
                                if person_count < person_limit and role["count"] >= person_minimum and role["name"] not in exclude:
                                    auto_list[role["name"]] = role["name"]
                                    all_keys.append(role["name"])
                                    person_count += 1
                            default_template = {"plex_search": {"any": {auto_type: "<<value>>"}}}
                        elif auto_type == "number":
                            if "data" not in methods:
                                raise Failed(f"Config Error: {map_name} data attribute not found")
                            elif "data" in self.temp_vars:
                                dynamic_data = util.parse("Config", "data", self.temp_vars["data"], datatype="dict")
                            else:
                                dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="dict")
                            number_methods = {nm.lower(): nm for nm in dynamic_data}
                            if "starting" in number_methods and str(dynamic_data[number_methods["starting"]]).startswith("current_year"):
                                year_values = str(dynamic_data[number_methods["starting"]]).split("-")
                                starting = datetime.now().year - (0 if len(year_values) == 1 else int(year_values[1].strip()))
                            else:
                                starting = util.parse("Config", "starting", dynamic_data, parent=f"{map_name} data", methods=number_methods, datatype="int", default=0, minimum=0)
                            if "ending" in number_methods and str(dynamic_data[number_methods["ending"]]).startswith("current_year"):
                                year_values = str(dynamic_data[number_methods["ending"]]).split("-")
                                ending = datetime.now().year - (0 if len(year_values) == 1 else int(year_values[1].strip()))
                            else:
                                ending = util.parse("Config", "ending", dynamic_data, parent=f"{map_name} data", methods=number_methods, datatype="int", default=0, minimum=1)
                            increment = util.parse("Config", "increment", dynamic_data, parent=f"{map_name} data", methods=number_methods, datatype="int", default=1, minimum=1) if "increment" in number_methods else 1
                            if starting > ending:
                                raise Failed(f"Config Error: {map_name} data ending must be greater than starting")
                            current = starting
                            while starting <= ending:
                                all_keys.append(str(current))
                                if str(current) not in exclude and current not in exclude:
                                    auto_list[str(current)] = str(current)
                                current += increment
                        elif auto_type == "list":
                            if "data" not in methods:
                                raise Failed(f"Config Error: {map_name} data attribute not found")
                            for list_item in util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="strlist"):
                                all_keys.append(list_item)
                                if list_item not in exclude:
                                    auto_list[list_item] = list_item
                        elif auto_type == "trakt_user_lists":
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="list")
                            for option in dynamic_data:
                                _check_dict({self.config.Trakt.build_user_url(u[0], u[1]): u[2] for u in self.config.Trakt.all_user_lists(option)})
                        elif auto_type == "trakt_liked_lists":
                            _check_dict(self.config.Trakt.all_liked_lists())
                        elif auto_type == "tmdb_popular_people":
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="int", minimum=1)
                            _check_dict(self.config.TMDb.get_popular_people(dynamic_data))
                        elif auto_type == "trakt_people_list":
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="list")
                            for option in dynamic_data:
                                _check_dict(self.config.Trakt.get_people(option))
                        else:
                            raise Failed(f"Config Error: {map_name} type attribute {dynamic[methods['type']]} invalid")
                    for add_key, combined_keys in addons.items():
                        if add_key not in all_keys:
                            final_keys = [ck for ck in combined_keys if ck in all_keys]
                            if final_keys:
                                if include:
                                    include.append(add_key)
                                auto_list[add_key] = add_key
                                addons[add_key] = final_keys
                            else:
                                logger.warning(f"Config Error: {add_key} Custom Key must have at least one Key")
                    title_format = default_title_format
                    if "title_format" in self.temp_vars:
                        title_format = util.parse("Config", "title_format", self.temp_vars["title_format"], parent="template_variable", default=default_title_format)
                    elif "title_format" in methods:
                        title_format = util.parse("Config", "title_format", dynamic, parent=map_name, methods=methods, default=default_title_format)
                    if "<<key_name>>" not in title_format and "<<title>>" not in title_format:
                        logger.error(f"Config Error: <<key_name>> not in title_format: {title_format} using default: {default_title_format}")
                        title_format = default_title_format
                    if "post_format_override" in methods:
                        methods["title_override"] = methods.pop("post_format_override")
                    if "pre_format_override" in methods:
                        methods["key_name_override"] = methods.pop("pre_format_override")
                    title_override = util.parse("Config", "title_override", dynamic, parent=map_name, methods=methods, datatype="strdict") if "title_override" in methods else {}
                    key_name_override = util.parse("Config", "key_name_override", dynamic, parent=map_name, methods=methods, datatype="strdict") if "key_name_override" in methods else {}
                    test = util.parse("Config", "test", dynamic, parent=map_name, methods=methods, default=False, datatype="bool") if "test" in methods else False
                    sync = util.parse("Config", "sync", dynamic, parent=map_name, methods=methods, default=False, datatype="bool") if "sync" in methods else False
                    if "<<library_type>>" in title_format:
                        title_format = title_format.replace("<<library_type>>", library.type)
                    template_variables = util.parse("Config", "template_variables", dynamic, parent=map_name, methods=methods, datatype="dictdict") if "template_variables" in methods else {}
                    if "template" in methods:
                        template_names = util.parse("Config", "template", dynamic, parent=map_name, methods=methods, datatype="strlist")
                        has_var = False
                        for template_name in template_names:
                            if template_name not in self.templates:
                                raise Failed(f"Config Error: {map_name} template: {template_name} not found")
                            if "<<value>>" in str(self.templates[template_name][0]) or f"<<{auto_type}>>" in str(self.templates[template_name][0]):
                                has_var = True
                        if not has_var:
                            raise Failed(f"Config Error: One {map_name} template: {template_names} is required to have the template variable <<value>>")
                    elif auto_type in ["number", "list"]:
                        raise Failed(f"Config Error: {map_name} template required for type: {auto_type}")
                    else:
                        self.templates[map_name] = (default_template if default_template else default_templates[auto_type], {})
                        template_names = [map_name]
                    remove_prefix = []
                    if "remove_prefix" in self.temp_vars:
                        remove_prefix = util.parse("Config", "remove_prefix", self.temp_vars["remove_prefix"], parent="template_variable", datatype="commalist")
                    elif "remove_prefix" in methods:
                        remove_prefix = util.parse("Config", "remove_prefix", dynamic, parent=map_name, methods=methods, datatype="commalist")
                    remove_suffix = []
                    if "remove_suffix" in self.temp_vars:
                        remove_suffix = util.parse("Config", "remove_suffix", self.temp_vars["remove_suffix"], parent="template_variable", datatype="commalist")
                    elif "remove_suffix" in methods:
                        remove_suffix = util.parse("Config", "remove_suffix", dynamic, parent=map_name, methods=methods, datatype="commalist")
                    sync = {i.title: i for i in self.library.get_all_collections(label=str(map_name))} if sync else {}
                    other_name = None
                    if "other_name" in self.temp_vars and include:
                        other_name = util.parse("Config", "other_name", self.temp_vars["remove_suffix"], parent="template_variable")
                    elif "other_name" in methods and include:
                        other_name = util.parse("Config", "other_name", dynamic, parent=map_name, methods=methods)
                    other_templates = util.parse("Config", "other_template", dynamic, parent=map_name, methods=methods, datatype="strlist") if "other_template" in methods and include else None
                    if other_templates:
                        for other_template in other_templates:
                            if other_template not in self.templates:
                                raise Failed(f"Config Error: {map_name} other template: {other_template} not found")
                    else:
                        other_templates = template_names
                    other_keys = []
                    logger.debug(f"Mapping Name: {map_name}")
                    logger.debug(f"Type: {auto_type}")
                    logger.debug(f"Data: {dynamic_data}")
                    logger.debug(f"Exclude: {exclude}")
                    logger.debug(f"Addons: {addons}")
                    logger.debug(f"Template: {template_names}")
                    logger.debug(f"Other Template: {other_templates}")
                    logger.debug(f"Template Variables: {template_variables}")
                    logger.debug(f"Remove Prefix: {remove_prefix}")
                    logger.debug(f"Remove Suffix: {remove_suffix}")
                    logger.debug(f"Title Format: {title_format}")
                    logger.debug(f"Key Name Override: {key_name_override}")
                    logger.debug(f"Title Override: {title_override}")
                    logger.debug(f"Test: {test}")
                    logger.debug(f"Sync: {sync}")
                    logger.debug(f"Include: {include}")
                    logger.debug(f"Other Name: {other_name}")
                    logger.debug(f"Keys (Title)")
                    for key, value in auto_list.items():
                        logger.info(f"  - {key}{'' if key == value else f' ({value})'}")

                    used_keys = []
                    for key, value in auto_list.items():
                        if include and key not in include:
                            if key not in exclude:
                                other_keys.append(key)
                            continue
                        if key in key_name_override:
                            key_name = key_name_override[key]
                        else:
                            key_name = value
                            for prefix in remove_prefix:
                                if key_name.startswith(prefix):
                                    key_name = key_name[len(prefix):].strip()
                            for suffix in remove_suffix:
                                if key_name.endswith(suffix):
                                    key_name = key_name[:-len(suffix)].strip()
                        key_value = [key] if key in all_keys else []
                        if key in addons:
                            key_value.extend([a for a in addons[key] if a in all_keys and a != key])
                        used_keys.extend(key_value)
                        og_call = {"value": key_value, auto_type: key_value, "key_name": key_name, "key": key}
                        for k, v in template_variables.items():
                            if key in v:
                                og_call[k] = v[key]
                        template_call = []
                        for template_name in template_names:
                            new_call = og_call.copy()
                            new_call["name"] = template_name
                            template_call.append(new_call)
                        if key in title_override:
                            collection_title = title_override[key]
                        else:
                            collection_title = title_format.replace("<<title>>", key_name).replace("<<key_name>>", key_name)
                        if collection_title in col_names:
                            logger.warning(f"Config Warning: Skipping duplicate collection: {collection_title}")
                        else:
                            col = {"template": template_call, "label": str(map_name)}
                            if test:
                                col["test"] = True
                            if collection_title in sync:
                                sync.pop(collection_title)
                            self.collections[collection_title] = col
                    if other_name:
                        og_other = {
                            "value": other_keys, "included_keys": include, "used_keys": used_keys,
                            auto_type: other_keys, "key_name": other_name, "key": "other"
                        }
                        for k, v in template_variables.items():
                            if "other" in v:
                                og_other[k] = v["other"]
                        other_call = []
                        for other_template in other_templates:
                            new_call = og_other.copy()
                            new_call["name"] = other_template
                            other_call.append(new_call)
                        col = {"template": other_call, "label": str(map_name)}
                        if test:
                            col["test"] = True
                        if other_name in sync:
                            sync.pop(other_name)
                        self.collections[other_name] = col
                    for col_title, col in sync.items():
                        col.delete()
                        logger.info(f"{map_name} Dynamic Collection: {col_title} Deleted")
                except Failed as e:
                    logger.error(e)
                    logger.error(f"{map_name} Dynamic Collection Failed")
                    continue

            if not self.metadata and not self.collections:
                raise Failed("YAML Error: metadata, collections, or dynamic_collections attribute is required")
            logger.info("")
            logger.info(f"Metadata File Loaded Successfully")

    def get_collections(self, requested_collections):
        if requested_collections:
            return {c: self.collections[c] for c in util.get_list(requested_collections) if c in self.collections}
        else:
            return self.collections

    def edit_tags(self, attr, obj, group, alias, extra=None):
        if attr in alias and f"{attr}.sync" in alias:
            logger.error(f"Metadata Error: Cannot use {attr} and {attr}.sync together")
        elif f"{attr}.remove" in alias and f"{attr}.sync" in alias:
            logger.error(f"Metadata Error: Cannot use {attr}.remove and {attr}.sync together")
        elif attr in alias and not group[alias[attr]]:
            logger.error(f"Metadata Error: {attr} attribute is blank")
        elif f"{attr}.remove" in alias and not group[alias[f"{attr}.remove"]]:
            logger.error(f"Metadata Error: {attr}.remove attribute is blank")
        elif f"{attr}.sync" in alias and not group[alias[f"{attr}.sync"]]:
            logger.error(f"Metadata Error: {attr}.sync attribute is blank")
        elif attr in alias or f"{attr}.remove" in alias or f"{attr}.sync" in alias:
            add_tags = util.get_list(group[alias[attr]]) if attr in alias else []
            if extra:
                add_tags.extend(extra)
            remove_tags = util.get_list(group[alias[f"{attr}.remove"]]) if f"{attr}.remove" in alias else None
            sync_tags = util.get_list(group[alias[f"{attr}.sync"]]) if f"{attr}.sync" in alias else None
            return len(self.library.edit_tags(attr, obj, add_tags=add_tags, remove_tags=remove_tags, sync_tags=sync_tags)) > 0
        return False

    def update_metadata(self):
        if not self.metadata:
            return None
        logger.info("")
        logger.separator("Running Metadata")
        logger.info("")
        next_year = datetime.now().year + 1
        for mapping_name, meta in self.metadata.items():
            methods = {mm.lower(): mm for mm in meta}

            logger.info("")
            if (isinstance(mapping_name, int) or mapping_name.startswith("tt")) and not self.library.is_music:
                if isinstance(mapping_name, int):
                    id_type = "TMDb" if self.library.is_movie else "TVDb"
                else:
                    id_type = "IMDb"
                logger.separator(f"{id_type} ID: {mapping_name} Metadata", space=False, border=False)
                logger.info("")
                item = []
                if self.library.is_movie and mapping_name in self.library.movie_map:
                    for item_id in self.library.movie_map[mapping_name]:
                        item.append(self.library.fetchItem(item_id))
                elif self.library.is_show and mapping_name in self.library.show_map:
                    for item_id in self.library.show_map[mapping_name]:
                        item.append(self.library.fetchItem(item_id))
                elif mapping_name in self.library.imdb_map:
                    for item_id in self.library.imdb_map[mapping_name]:
                        item.append(self.library.fetchItem(item_id))
                else:
                    logger.error(f"Metadata Error: {id_type} ID not mapped")
                    continue
                title = None
                if "title" in methods:
                    if meta[methods["title"]] is None:
                        logger.error("Metadata Error: title attribute is blank")
                    else:
                        title = meta[methods["title"]]
            else:
                logger.separator(f"{mapping_name} Metadata", space=False, border=False)
                logger.info("")
                year = None
                if "year" in methods and not self.library.is_music:
                    if meta[methods["year"]] is None:
                        raise Failed("Metadata Error: year attribute is blank")
                    try:
                        year_value = int(str(meta[methods["year"]]))
                        if 1800 <= year_value <= next_year:
                            year = year_value
                    except ValueError:
                        pass
                    if year is None:
                        raise Failed(f"Metadata Error: year attribute must be an integer between 1800 and {next_year}")

                title = mapping_name
                if "title" in methods:
                    if meta[methods["title"]] is None:
                        logger.error("Metadata Error: title attribute is blank")
                    else:
                        title = meta[methods["title"]]

                item = self.library.search_item(title, year=year)

                if item is None and "alt_title" in methods:
                    if meta[methods["alt_title"]] is None:
                        logger.error("Metadata Error: alt_title attribute is blank")
                    else:
                        alt_title = meta[methods["alt_title"]]
                        item = self.library.search_item(alt_title, year=year)
                        if item is None:
                            item = self.library.search_item(alt_title)

                if item is None:
                    logger.error(f"Skipping {mapping_name}: Item {mapping_name} not found")
                    continue
            if not isinstance(item, list):
                item = [item]
            for i in item:
                self.update_metadata_item(i, title, mapping_name, meta, methods)

    def update_metadata_item(self, item, title, mapping_name, meta, methods):

        updated = False

        def add_edit(name, current_item, group=None, alias=None, key=None, value=None, var_type="str"):
            nonlocal updated
            if value or name in alias:
                if value or group[alias[name]]:
                    if key is None:         key = name
                    if value is None:       value = group[alias[name]]
                    try:
                        current = str(getattr(current_item, key, ""))
                        final_value = None
                        if var_type == "date":
                            final_value = util.validate_date(value, name, return_as="%Y-%m-%d")
                            current = current[:-9]
                        elif var_type == "float":
                            try:
                                value = float(str(value))
                                if 0 <= value <= 10:
                                    final_value = value
                            except ValueError:
                                pass
                            if final_value is None:
                                raise Failed(f"Metadata Error: {name} attribute must be a number between 0 and 10")
                        elif var_type == "int":
                            try:
                                final_value = int(str(value))
                            except ValueError:
                                pass
                            if final_value is None:
                                raise Failed(f"Metadata Error: {name} attribute must be an integer")
                        else:
                            final_value = value
                        if current != str(final_value):
                            if key == "title":
                                current_item.editTitle(final_value)
                            else:
                                current_item.editField(key, final_value)
                            logger.info(f"Detail: {name} updated to {final_value}")
                            updated = True
                    except Failed as ee:
                        logger.error(ee)
                else:
                    logger.error(f"Metadata Error: {name} attribute is blank")

        def finish_edit(current_item, description):
            nonlocal updated
            if updated:
                try:
                    current_item.saveEdits()
                    logger.info(f"{description} Details Update Successful")
                except BadRequest:
                    logger.error(f"{description} Details Update Failed")

        tmdb_item = None
        tmdb_is_movie = None
        if not self.library.is_music and ("tmdb_show" in methods or "tmdb_id" in methods) and "tmdb_movie" in methods:
            logger.error("Metadata Error: Cannot use tmdb_movie and tmdb_show when editing the same metadata item")

        if not self.library.is_music and "tmdb_show" in methods or "tmdb_id" in methods or "tmdb_movie" in methods:
            try:
                if "tmdb_show" in methods or "tmdb_id" in methods:
                    data = meta[methods["tmdb_show" if "tmdb_show" in methods else "tmdb_id"]]
                    if data is None:
                        logger.error("Metadata Error: tmdb_show attribute is blank")
                    else:
                        tmdb_is_movie = False
                        tmdb_item = self.config.TMDb.get_show(util.regex_first_int(data, "Show"))
                elif "tmdb_movie" in methods:
                    if meta[methods["tmdb_movie"]] is None:
                        logger.error("Metadata Error: tmdb_movie attribute is blank")
                    else:
                        tmdb_is_movie = True
                        tmdb_item = self.config.TMDb.get_movie(util.regex_first_int(meta[methods["tmdb_movie"]], "Movie"))
            except Failed as e:
                logger.error(e)

        originally_available = None
        original_title = None
        rating = None
        studio = None
        tagline = None
        summary = None
        genres = []
        if tmdb_item:
            originally_available = datetime.strftime(tmdb_item.release_date if tmdb_is_movie else tmdb_item.first_air_date, "%Y-%m-%d")

            if tmdb_item.original_title != tmdb_item.title:
                original_title = tmdb_item.original_title
            rating = tmdb_item.vote_average
            studio = tmdb_item.studio
            tagline = tmdb_item.tagline if len(tmdb_item.tagline) > 0 else None
            summary = tmdb_item.overview
            genres = tmdb_item.genres

        item.batchEdits()
        if title:
            add_edit("title", item, meta, methods, value=title)
        add_edit("sort_title", item, meta, methods, key="titleSort")
        add_edit("user_rating", item, meta, methods, key="userRating", var_type="float")
        if not self.library.is_music:
            add_edit("originally_available", item, meta, methods, key="originallyAvailableAt", value=originally_available, var_type="date")
            add_edit("critic_rating", item, meta, methods, value=rating, key="rating", var_type="float")
            add_edit("audience_rating", item, meta, methods, key="audienceRating", var_type="float")
            add_edit("content_rating", item, meta, methods, key="contentRating")
            add_edit("original_title", item, meta, methods, key="originalTitle", value=original_title)
            add_edit("studio", item, meta, methods, value=studio)
            add_edit("tagline", item, meta, methods, value=tagline)
        add_edit("summary", item, meta, methods, value=summary)
        for tag_edit in util.tags_to_edit[self.library.type]:
            if self.edit_tags(tag_edit, item, meta, methods, extra=genres if tag_edit == "genre" else None):
                updated = True
        finish_edit(item, f"{self.library.type}: {mapping_name}")

        if self.library.type in util.advance_tags_to_edit:
            advance_edits = {}
            prefs = [p.id for p in item.preferences()]
            for advance_edit in util.advance_tags_to_edit[self.library.type]:
                if advance_edit in methods:
                    if advance_edit in ["metadata_language", "use_original_title"] and self.library.agent not in plex.new_plex_agents:
                        logger.error(f"Metadata Error: {advance_edit} attribute only works for with the New Plex Movie Agent and New Plex TV Agent")
                    elif meta[methods[advance_edit]]:
                        ad_key, options = plex.item_advance_keys[f"item_{advance_edit}"]
                        method_data = str(meta[methods[advance_edit]]).lower()
                        if method_data not in options:
                            logger.error(f"Metadata Error: {meta[methods[advance_edit]]} {advance_edit} attribute invalid")
                        elif ad_key in prefs and getattr(item, ad_key) != options[method_data]:
                            advance_edits[ad_key] = options[method_data]
                            logger.info(f"Detail: {advance_edit} updated to {method_data}")
                    else:
                        logger.error(f"Metadata Error: {advance_edit} attribute is blank")
            if advance_edits:
                if self.library.edit_advance(item, advance_edits):
                    updated = True
                    logger.info(f"{mapping_name} Advanced Details Update Successful")
                else:
                    logger.error(f"{mapping_name} Advanced Details Update Failed")

        logger.info(f"{self.library.type}: {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")

        asset_location = self.library.item_images(item, meta, methods)

        if "seasons" in methods and self.library.is_show:
            if not meta[methods["seasons"]]:
                logger.error("Metadata Error: seasons attribute is blank")
            elif not isinstance(meta[methods["seasons"]], dict):
                logger.error("Metadata Error: seasons attribute must be a dictionary")
            else:
                seasons = {}
                for season in item.seasons():
                    seasons[season.title] = season
                    seasons[int(season.index)] = season
                for season_id, season_dict in meta[methods["seasons"]].items():
                    updated = False
                    logger.info("")
                    logger.info(f"Updating season {season_id} of {mapping_name}...")
                    if season_id in seasons:
                        season = seasons[season_id]
                    else:
                        logger.error(f"Metadata Error: Season: {season_id} not found")
                        continue
                    season_methods = {sm.lower(): sm for sm in season_dict}
                    season.batchEdits()
                    add_edit("title", season, season_dict, season_methods)
                    add_edit("summary", season, season_dict, season_methods)
                    add_edit("user_rating", season, season_dict, season_methods, key="userRating", var_type="float")
                    if self.edit_tags("label", season, season_dict, season_methods):
                        updated = True
                    finish_edit(season, f"Season: {season_id}")
                    self.library.item_images(season, season_dict, season_methods, asset_location=asset_location, top_item=item,
                                             title=f"{item.title} Season {season.seasonNumber}",
                                             image_name=f"Season{'0' if season.seasonNumber < 10 else ''}{season.seasonNumber}")
                    logger.info(f"Season {season_id} of {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")

                    if "episodes" in season_methods and self.library.is_show:
                        if not season_dict[season_methods["episodes"]]:
                            logger.error("Metadata Error: episodes attribute is blank")
                        elif not isinstance(season_dict[season_methods["episodes"]], dict):
                            logger.error("Metadata Error: episodes attribute must be a dictionary")
                        else:
                            episodes = {}
                            for episode in season.episodes():
                                episodes[episode.title] = episode
                                episodes[int(episode.index)] = episode
                            for episode_str, episode_dict in season_dict[season_methods["episodes"]].items():
                                updated = False
                                logger.info("")
                                logger.info(f"Updating episode {episode_str} in {season_id} of {mapping_name}...")
                                if episode_str in episodes:
                                    episode = episodes[episode_str]
                                else:
                                    logger.error(f"Metadata Error: Episode {episode_str} in Season {season_id} not found")
                                    continue
                                episode_methods = {em.lower(): em for em in episode_dict}
                                episode.batchEdits()
                                add_edit("title", episode, episode_dict, episode_methods)
                                add_edit("sort_title", episode, episode_dict, episode_methods, key="titleSort")
                                add_edit("critic_rating", episode, episode_dict, episode_methods, key="rating", var_type="float")
                                add_edit("audience_rating", episode, episode_dict, episode_methods, key="audienceRating", var_type="float")
                                add_edit("user_rating", episode, episode_dict, episode_methods, key="userRating", var_type="float")
                                add_edit("originally_available", episode, episode_dict, episode_methods, key="originallyAvailableAt", var_type="date")
                                add_edit("summary", episode, episode_dict, episode_methods)
                                for tag_edit in ["director", "writer", "label"]:
                                    if self.edit_tags(tag_edit, episode, episode_dict, episode_methods):
                                        updated = True
                                finish_edit(episode, f"Episode: {episode_str} in Season: {season_id}")
                                self.library.item_images(episode, episode_dict, episode_methods, asset_location=asset_location, top_item=item,
                                                         title=f"{item.title} {episode.seasonEpisode.upper()}",
                                                         image_name=episode.seasonEpisode.upper())
                                logger.info(f"Episode {episode_str} in Season {season_id} of {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")

        if "episodes" in methods and self.library.is_show:
            if not meta[methods["episodes"]]:
                logger.error("Metadata Error: episodes attribute is blank")
            elif not isinstance(meta[methods["episodes"]], dict):
                logger.error("Metadata Error: episodes attribute must be a dictionary")
            else:
                for episode_str, episode_dict in meta[methods["episodes"]].items():
                    updated = False
                    logger.info("")
                    match = re.search("[Ss]\\d+[Ee]\\d+", episode_str)
                    if not match:
                        logger.error(f"Metadata Error: episode {episode_str} invalid must have S##E## format")
                        continue
                    output = match.group(0)[1:].split("E" if "E" in match.group(0) else "e")
                    season_id = int(output[0])
                    episode_id = int(output[1])
                    logger.info(f"Updating episode S{season_id}E{episode_id} of {mapping_name}...")
                    try:
                        episode = item.episode(season=season_id, episode=episode_id)
                    except NotFound:
                        logger.error(f"Metadata Error: episode {episode_id} of season {season_id} not found")
                        continue
                    episode_methods = {em.lower(): em for em in episode_dict}
                    episode.batchEdits()
                    add_edit("title", episode, episode_dict, episode_methods)
                    add_edit("sort_title", episode, episode_dict, episode_methods, key="titleSort")
                    add_edit("critic_rating", episode, episode_dict, episode_methods, key="rating", var_type="float")
                    add_edit("audience_rating", episode, episode_dict, episode_methods, key="audienceRating", var_type="float")
                    add_edit("user_rating", episode, episode_dict, episode_methods, key="userRating", var_type="float")
                    add_edit("originally_available", episode, episode_dict, episode_methods, key="originallyAvailableAt", var_type="date")
                    add_edit("summary", episode, episode_dict, episode_methods)
                    for tag_edit in ["director", "writer", "label"]:
                        if self.edit_tags(tag_edit, episode, episode_dict, episode_methods):
                            updated = True
                    finish_edit(episode, f"Episode: {episode_str} in Season: {season_id}")
                    self.library.item_images(episode, episode_dict, episode_methods, asset_location=asset_location, top_item=item,
                                             title=f"{item.title} {episode.seasonEpisode.upper()}",
                                             image_name=episode.seasonEpisode.upper())
                    logger.info(f"Episode S{season_id}E{episode_id} of {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")

        if "albums" in methods and self.library.is_music:
            if not meta[methods["albums"]]:
                logger.error("Metadata Error: albums attribute is blank")
            elif not isinstance(meta[methods["albums"]], dict):
                logger.error("Metadata Error: albums attribute must be a dictionary")
            else:
                albums = {album.title: album for album in item.albums()}
                for album_name, album_dict in meta[methods["albums"]].items():
                    updated = False
                    title = None
                    album_methods = {am.lower(): am for am in album_dict}
                    logger.info("")
                    logger.info(f"Updating album {album_name} of {mapping_name}...")
                    if album_name in albums:
                        album = albums[album_name]
                    elif "alt_title" in album_methods and album_dict[album_methods["alt_title"]] and album_dict[album_methods["alt_title"]] in albums:
                        album = albums[album_dict[album_methods["alt_title"]]]
                        title = album_name
                    else:
                        logger.error(f"Metadata Error: Album: {album_name} not found")
                        continue
                    if not title:
                        title = album.title
                    album.batchEdits()
                    add_edit("title", album, album_dict, album_methods, value=title)
                    add_edit("sort_title", album, album_dict, album_methods, key="titleSort")
                    add_edit("critic_rating", album, album_dict, album_methods, key="rating", var_type="float")
                    add_edit("user_rating", album, album_dict, album_methods, key="userRating", var_type="float")
                    add_edit("originally_available", album, album_dict, album_methods, key="originallyAvailableAt", var_type="date")
                    add_edit("record_label", album, album_dict, album_methods, key="studio")
                    add_edit("summary", album, album_dict, album_methods)
                    for tag_edit in ["genre", "style", "mood", "collection", "label"]:
                        if self.edit_tags(tag_edit, album, album_dict, album_methods):
                            updated = True
                    finish_edit(album, f"Album: {title}")
                    self.library.item_images(album, album_dict, album_methods, asset_location=asset_location, top_item=item,
                                             title=f"{item.title} Album {album.title}", image_name=album.title)
                    logger.info(f"Album: {title} of {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")

                    if "tracks" in album_methods:
                        if not album_dict[album_methods["tracks"]]:
                            logger.error("Metadata Error: tracks attribute is blank")
                        elif not isinstance(album_dict[album_methods["tracks"]], dict):
                            logger.error("Metadata Error: tracks attribute must be a dictionary")
                        else:
                            tracks = {}
                            for track in album.tracks():
                                tracks[track.title] = track
                                tracks[int(track.index)] = track
                            for track_num, track_dict in album_dict[album_methods["tracks"]].items():
                                updated = False
                                title = None
                                track_methods = {tm.lower(): tm for tm in track_dict}
                                logger.info("")
                                logger.info(f"Updating track {track_num} on {album_name} of {mapping_name}...")
                                if track_num in tracks:
                                    track = tracks[track_num]
                                elif "alt_title" in track_methods and track_dict[track_methods["alt_title"]] and track_dict[track_methods["alt_title"]] in tracks:
                                    track = tracks[track_dict[track_methods["alt_title"]]]
                                    title = track_num
                                else:
                                    logger.error(f"Metadata Error: Track: {track_num} not found")
                                    continue

                                if not title:
                                    title = track.title
                                track.batchEdits()
                                add_edit("title", track, track_dict, track_methods, value=title)
                                add_edit("user_rating", track, track_dict, track_methods, key="userRating", var_type="float")
                                add_edit("track", track, track_dict, track_methods, key="index", var_type="int")
                                add_edit("disc", track, track_dict, track_methods, key="parentIndex", var_type="int")
                                add_edit("original_artist", track, track_dict, track_methods, key="originalTitle")
                                for tag_edit in ["mood", "collection", "label"]:
                                    if self.edit_tags(tag_edit, track, track_dict, track_methods):
                                        updated = True
                                finish_edit(track, f"Track: {title}")
                                logger.info(f"Track: {track_num} on Album: {title} of {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")

        if "f1_season" in methods and self.library.is_show:
            f1_season = None
            current_year = datetime.now().year
            if meta[methods["f1_season"]] is None:
                raise Failed("Metadata Error: f1_season attribute is blank")
            try:
                year_value = int(str(meta[methods["f1_season"]]))
                if 1950 <= year_value <= current_year:
                    f1_season = year_value
            except ValueError:
                pass
            if f1_season is None:
                raise Failed(f"Metadata Error: f1_season attribute must be an integer between 1950 and {current_year}")
            round_prefix = False
            if "round_prefix" in methods:
                if meta[methods["round_prefix"]] is True:
                    round_prefix = True
                else:
                    logger.error("Metadata Error: round_prefix must be true to do anything")
            shorten_gp = False
            if "shorten_gp" in methods:
                if meta[methods["shorten_gp"]] is True:
                    shorten_gp = True
                else:
                    logger.error("Metadata Error: shorten_gp must be true to do anything")
            f1_language = None
            if "f1_language" in methods:
                if str(meta[methods["f1_language"]]).lower() in ergast.translations:
                    f1_language = str(meta[methods["f1_language"]]).lower()
                else:
                    logger.error(f"Metadata Error: f1_language must be a language code PMM has a translation for. Options: {ergast.translations}")
            logger.info(f"Setting Metadata of {item.title} to F1 Season {f1_season}")
            races = self.config.Ergast.get_races(f1_season, f1_language)
            race_lookup = {r.round: r for r in races}
            for season in item.seasons():
                if not season.seasonNumber:
                    continue
                sprint_weekend = False
                for episode in season.episodes():
                    if "sprint" in episode.locations[0].lower():
                        sprint_weekend = True
                        break
                if season.seasonNumber in race_lookup:
                    race = race_lookup[season.seasonNumber]
                    title = race.format_name(round_prefix, shorten_gp)
                    updated = False
                    season.batchEdits()
                    add_edit("title", season, value=title)
                    finish_edit(season, f"Season: {title}")
                    logger.info(f"Race {season.seasonNumber} of F1 Season {f1_season}: Details Update {'Complete' if updated else 'Not Needed'}")
                    for episode in season.episodes():
                        if len(episode.locations) > 0:
                            ep_title, session_date = race.session_info(episode.locations[0], sprint_weekend)
                            episode.batchEdits()
                            add_edit("title", episode, value=ep_title)
                            add_edit("originally_available", episode, key="originallyAvailableAt", var_type="date", value=session_date)
                            finish_edit(episode, f"Season: {season.seasonNumber} Episode: {episode.episodeNumber}")
                            logger.info(f"Session {episode.title}: Details Update {'Complete' if updated else 'Not Needed'}")
                else:
                    logger.warning(f"Ergast Error: No Round: {season.seasonNumber} for Season {f1_season}")


class PlaylistFile(DataFile):
    def __init__(self, config, file_type, path, temp_vars, asset_directory):
        super().__init__(config, file_type, path, temp_vars, asset_directory)
        self.data_type = "Playlist"
        logger.info("")
        logger.info(f"Loading Playlist {file_type}: {path}")
        data = self.load_file(self.type, self.path)
        self.playlists = get_dict("playlists", data, self.config.playlist_names)
        self.templates = get_dict("templates", data)
        self.external_templates(data)
        if not self.playlists:
            raise Failed("YAML Error: playlists attribute is required")
        logger.info(f"Playlist File Loaded Successfully")


class OverlayFile(DataFile):
    def __init__(self, config, library, file_type, path, temp_vars, asset_directory):
        super().__init__(config, file_type, path, temp_vars, asset_directory)
        self.library = library
        self.data_type = "Overlay"
        logger.info("")
        logger.info(f"Loading Overlay {file_type}: {path}")
        data = self.load_file(self.type, self.path)
        self.overlays = get_dict("overlays", data, self.library.overlays)
        self.templates = get_dict("templates", data)
        self.external_templates(data)
        if not self.overlays:
            raise Failed("YAML Error: overlays attribute is required")
        logger.info(f"Overlay File Loaded Successfully")
