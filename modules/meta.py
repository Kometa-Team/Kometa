import math, operator, os, re
from datetime import datetime
from modules import plex, ergast, util
from modules.request import quote
from modules.util import Failed, NotScheduled
from plexapi.exceptions import NotFound, BadRequest

logger = util.logger

all_auto = ["genre", "number", "custom"]
ms_auto = [
    "actor", "year", "content_rating", "original_language", "tmdb_popular_people", "trakt_user_lists", "studio",
    "trakt_liked_lists", "trakt_people_list", "subtitle_language", "audio_language", "resolution", "decade", "imdb_awards"
]
auto = {
    "Movie": ["tmdb_collection", "edition", "country", "director", "producer", "writer"] + all_auto + ms_auto,
    "Show": ["network", "origin_country", "episode_year"] + all_auto + ms_auto,
    "Artist": ["mood", "style", "country", "album_genre", "album_mood", "album_style", "track_mood"] + all_auto,
    "Video": ["country", "content_rating"] + all_auto
}
dynamic_attributes = [
    "type", "data", "exclude", "addons", "template", "template_variables", "other_template", "remove_suffix", "custom_keys",
    "remove_prefix", "title_format", "key_name_override", "title_override", "test", "sync", "include", "other_name"
]
auto_type_translation = {
    "content_rating": "contentRating", "subtitle_language": "subtitleLanguage", "audio_language": "audioLanguage",
    "album_genre": "album.genre", "album_style": "album.style", "album_mood": "album.mood", "track_mood": "track.mood",
    "edition": "editionTitle", "episode_year": "episode.year"
}
default_templates = {
    "original_language": {"plex_all": True, "filters": {"original_language": "<<value>>"}},
    "origin_country": {"plex_all": True, "filters": {"origin_country": "<<value>>"}},
    "tmdb_collection": {"tmdb_collection_details": "<<value>>", "minimum_items": 2},
    "trakt_user_lists": {"trakt_list_details": "<<value>>"},
    "trakt_liked_lists": {"trakt_list_details": "<<value>>"},
    "tmdb_popular_people": {"tmdb_person": "<<value>>", "plex_search": {"all": {"actor": "tmdb"}}},
    "trakt_people_list": {"tmdb_person": "<<value>>", "plex_search": {"all": {"actor": "tmdb"}}}
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
                        continue
                    elif attribute != "queues" and not isinstance(_data, dict):
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
    def __init__(self, config, file_type, path, temp_vars, asset_directory, data_type):
        if file_type != "Data":
            logger.info("")
            logger.info(f"Loading {data_type} {file_type}: {path}")
            logger.info("")
        self.config = config
        self.library = None
        self.type = file_type
        self.path = path
        self.temp_vars = temp_vars
        self.language = "en"
        if "language" in self.temp_vars and self.temp_vars["language"]:
            if self.temp_vars["language"].lower() not in self.config.GitHub.translation_keys:
                logger.warning(f"Config Error: Language: {self.temp_vars['language'].lower()} Not Found using en. Options: {', '.join(self.config.GitHub.translation_keys)}")
            else:
                self.language = self.temp_vars["language"].lower()
        self.asset_directory = asset_directory
        self.data_type = ""
        self.templates = {}
        filename = self.get_file_name()
        if config.requested_files and filename not in config.requested_files:
            raise NotScheduled(filename)

    def get_file_name(self):
        data = f"{self.config.GitHub.configs_url}{self.path}.yml" if self.type == "GIT" else self.path
        if "/" in data:
            if data.endswith(".yml"):
                return data[data.rfind("/") + 1:-4]
            elif data.endswith(".yaml"):
                return data[data.rfind("/") + 1:-5]
            else:
                return data[data.rfind("/") + 1:]
        elif "\\" in data:
            if data.endswith(".yml"):
                return data[data.rfind("\\") + 1:-4]
            elif data.endswith(".yaml"):
                return data[data.rfind("/") + 1:-5]
            else:
                return data[data.rfind("\\") + 1:]
        else:
            return data

    def load_file(self, file_type, file_path, overlay=False, translation=False, images=False, folder=""):
        if translation:
            if file_path.endswith(".yml"):
                file_path = file_path[:-4]
            elif file_path.endswith(".yaml"):
                file_path = file_path[:-5]
        if not translation and not file_path.endswith((".yml", ".yaml")):
            file_path = f"{file_path}.yml"
        if file_type in ["URL", "Git", "Repo"] or (images and file_type == "Default"):
            if file_type == "Repo" and not self.config.custom_repo:
                raise Failed("Config Error: No custom_repo defined")
            if file_type == "URL":
                content_path = file_path
            elif file_type == "Repo":
                content_path = f"{self.config.custom_repo}{file_path}"
            elif file_type == "Default":
                content_path = f"{self.config.GitHub.images_raw_url}{folder}{file_path}"
            else:
                content_path = f"{self.config.GitHub.configs_url}{file_path}"
            dir_path = content_path
            if translation:
                content_path = f"{content_path}/default.yml"
            yaml = self.config.Requests.get_yaml(content_path, check_empty=True)
        else:
            if file_type == "Default":
                if not overlay and file_path.startswith(("movie/", "chart/", "award/")):
                    file_path = file_path[6:]
                elif not overlay and file_path.startswith(("show/", "both/")):
                    file_path = file_path[5:]
                elif overlay and file_path.startswith("overlays/"):
                    file_path = file_path[9:]
                defaults_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "defaults")
                if overlay:
                    defaults_path = os.path.join(defaults_path, "overlays")
                if os.path.exists(os.path.join(defaults_path, file_path)):
                    file_path = os.path.join(defaults_path, file_path)
                elif self.library:
                    for default_folder in [self.library.type.lower(), "both", "chart", "award"]:
                        if os.path.exists(os.path.join(defaults_path, default_folder, file_path)):
                            file_path = os.path.join(defaults_path, default_folder, file_path)
                            break
            content_path = os.path.abspath(os.path.join(file_path, "default.yml") if translation else file_path)
            dir_path = file_path
            if not os.path.exists(content_path):
                if file_type == "Default":
                    raise Failed(f"File Error: Default does not exist {file_path}")
                else:
                    raise Failed(f"File Error: File does not exist {content_path}")
            yaml = self.config.Requests.file_yaml(content_path, check_empty=True)
        if not translation:
            logger.debug(f"File Loaded From: {content_path}")
            return yaml.data
        if "translations" not in yaml.data:
            raise Failed(f"URL Error: Top Level translations attribute not found in {content_path}")
        translations = {k: {"default": v} for k, v in yaml.data["translations"].items()}
        lib_type = self.library.type.lower() if self.library else "item"
        logger.trace(f"Translations Loaded From: {dir_path}")
        key_names = {}
        variables = {k: {"default": v[lib_type]} for k, v in yaml.data["variables"].items()}

        def add_translation(yaml_path, yaml_key, url=False):
            if url:
                yaml_content = self.config.Requests.get_yaml(yaml_path, check_empty=True)
            else:
                yaml_content = self.config.Requests.file_yaml(yaml_path, check_empty=True)
            if "variables" in yaml_content.data and yaml_content.data["variables"]:
                for var_key, var_value in yaml_content.data["variables"].items():
                    if lib_type in var_value:
                        if var_key not in variables:
                            variables[var_key] = {}
                        variables[var_key][yaml_key] = var_value[lib_type]

            if "translations" in yaml_content.data and yaml_content.data["translations"]:
                for translation_key in translations:
                    if translation_key in yaml_content.data["translations"]:
                        translations[translation_key][yaml_key] = yaml_content.data["translations"][translation_key]
                    else:
                        logger.trace(f"Translation Error: translations attribute {translation_key} not found in {yaml_path}")
            else:
                logger.trace(f"Config Error: Top Level translations attribute not found in {yaml_path}")

            if "key_names" in yaml_content.data and yaml_content.data["key_names"]:
                for kn, vn in yaml_content.data["key_names"].items():
                    if kn not in key_names:
                        key_names[kn] = {}
                    key_names[kn][yaml_key] = vn

        if file_type in ["URL", "Git", "Repo"]:
            if "languages" in yaml.data and isinstance(yaml.data["language"], list):
                for language in yaml.data["language"]:
                    try:
                        add_translation(f"{dir_path}/{language}.yml", language, url=True)
                    except Failed:
                        logger.error(f"URL Error: Language file not found at {dir_path}/{language}.yml")
        else:
            for file in os.listdir(dir_path):
                if file.endswith(".yml") and file != "default.yml":
                    add_translation(os.path.abspath(f"{dir_path}/{file}"), file[:-4])
        return translations, key_names, variables

    def apply_template(self, call_name, mapping_name, data, template_call, extra_variables):
        if not self.templates:
            raise Failed(f"{self.data_type} Error: No templates found")
        elif not template_call:
            raise Failed(f"{self.data_type} Error: template attribute is blank")
        else:
            new_attributes = {}
            for original_variables in util.get_list(template_call, split=False):
                if original_variables["name"] not in self.templates:
                    raise Failed(f"{self.data_type} Error: template {original_variables['name']} not found")
                elif not isinstance(self.templates[original_variables["name"]][0], dict):
                    raise Failed(f"{self.data_type} Error: template {original_variables['name']} is not a dictionary")
                else:
                    logger.separator(f"Template {original_variables['name']}", space=False, border=False, trace=True)
                    logger.trace("")
                    logger.trace(f"Original: {original_variables}")

                    remove_variables = []
                    optional = []
                    for tm in original_variables.copy():
                        if original_variables[tm] is None:
                            remove_variables.append(tm)
                            original_variables.pop(tm)
                            optional.append(str(tm))

                    template, temp_vars = self.templates[original_variables["name"]]

                    if call_name:
                        name = call_name
                    elif "name" in template:
                        name = template["name"]
                    else:
                        name = mapping_name

                    name_var = f"{self.data_type.lower()}_name"
                    now = datetime.now()
                    original_variables[name_var] = str(name)
                    original_variables["mapping_name"] = mapping_name
                    original_variables["current_year"] = now.year
                    original_variables["current_month"] = now.month
                    original_variables["current_day"] = now.day
                    original_variables["library_type"] = self.library.type.lower() if self.library else "item"
                    original_variables["library_typeU"] = self.library.type if self.library else "Item"
                    original_variables["library_name"] = self.library.name if self.library else "playlist"

                    def replace_var(input_item, search_dicts):
                        if not isinstance(search_dicts, list):
                            search_dicts = [search_dicts]
                        return_item = input_item
                        for search_dict in search_dicts:
                            for rk, rv in search_dict.items():
                                if rk not in ["name_format", "summary_format"]:
                                    if f"<<{rk}>>" == str(return_item):
                                        return_item = rv
                                    if f"<<{rk}>>" in str(return_item):
                                        return_item = str(return_item).replace(f"<<{rk}>>", str(rv))
                        return return_item

                    conditionals = {}
                    if "conditionals" in template:
                        if not template["conditionals"]:
                            raise Failed(f"{self.data_type} Error: template sub-attribute conditionals is blank")
                        if not isinstance(template["conditionals"], dict):
                            raise Failed(f"{self.data_type} Error: template sub-attribute conditionals is not a dictionary")
                        for ck, cv in template["conditionals"].items():
                            conditionals[ck] = cv

                    added_vars = {}
                    init_defaults = {}
                    if "default" in template:
                        if not template["default"]:
                            raise Failed(f"{self.data_type} Error: template sub-attribute default is blank")
                        if not isinstance(template["default"], dict):
                            raise Failed(f"{self.data_type} Error: template sub-attribute default is not a dictionary")
                        init_defaults = template["default"]
                    all_init_defaults = {k: v for k, v in init_defaults.items()}

                    variables = {}
                    temp_conditionals = {}
                    for input_dict, input_type, overwrite_call in [
                        (original_variables, "Call", False),
                        (temp_vars, "External", False),
                        (extra_variables, "Definition", False),
                        (self.temp_vars, "Config", True)
                    ]:
                        logger.trace("")
                        logger.trace(f"{input_type}: {input_dict}")
                        for input_key, input_value in input_dict.items():
                            if input_key == "conditionals":
                                if not input_value:
                                    raise Failed(f"{self.data_type} Error: {input_type} template sub-attribute conditionals is blank")
                                if not isinstance(input_value, dict):
                                    raise Failed(f"{self.data_type} Error: {input_type} template sub-attribute conditionals is not a dictionary")
                                for ck, cv in input_value.items():
                                    temp_conditionals[ck] = cv
                            elif input_key == "default":
                                if not input_value:
                                    raise Failed(f"{self.data_type} Error: {input_type} template sub-attribute default is blank")
                                if not isinstance(input_value, dict):
                                    raise Failed(f"{self.data_type} Error: {input_type} template sub-attribute default is not a dictionary")
                                for dk, dv in input_value.items():
                                    all_init_defaults[dk] = dv
                            else:
                                input_key = replace_var(input_key, original_variables)
                                if input_value is None:
                                    optional.append(str(input_key))
                                    if input_key in variables:
                                        variables.pop(input_key)
                                    if input_key in added_vars:
                                        added_vars.pop(input_key)
                                elif overwrite_call:
                                    variables[input_key] = input_value
                                elif input_key not in added_vars:
                                    added_vars[input_key] = input_value
                    for k, v in added_vars.items():
                        if k not in variables:
                            variables[k] = v
                    for k, v in temp_conditionals.items():
                        if k not in variables:
                            conditionals[k] = v

                    if "key_name" in variables:
                        variables["original_key_name"] = variables["key_name"]
                        first_letter = str(variables["key_name"]).upper()[0]
                        variables["key_name_first_letter"] = first_letter if first_letter.isalpha() else "#"

                    default = {}
                    if all_init_defaults:
                        var_default = {replace_var(dk, variables): replace_var(dv, variables) for dk, dv in all_init_defaults.items() if dk not in variables}
                        for d_key, d_value in var_default.items():
                            final_key = replace_var(d_key, var_default)
                            if final_key not in optional and final_key not in variables and final_key not in conditionals:
                                default[final_key] = d_value
                                if "<<" in str(d_value):
                                    default[f"{final_key}_encoded"] = re.sub(r'<<(.+)>>', r'<<\1_encoded>>', d_value)
                                else:
                                    default[f"{final_key}_encoded"] = quote(d_value)

                    if "optional" in template:
                        if template["optional"]:
                            for op in util.get_list(template["optional"]):
                                op = replace_var(op, variables)
                                if op not in default and op not in conditionals:
                                    optional.append(str(op))
                                    optional.append(f"{op}_encoded")
                                elif op in init_defaults:
                                    logger.debug("")
                                    logger.debug(f"Template Warning: variable {op} cannot be optional if it has a default")
                        else:
                            raise Failed(f"{self.data_type} Error: template sub-attribute optional is blank")

                    for con_key, con_value in conditionals.items():
                        logger.debug("")
                        logger.debug(f"Conditional: {con_key}")
                        if not isinstance(con_value, dict):
                            raise Failed(f"{self.data_type} Error: conditional {con_key} is not a dictionary")
                        final_key = replace_var(con_key, [variables, default])
                        if final_key != con_key:
                            logger.trace(f"Variable: {final_key}")
                        if final_key in variables:
                            logger.debug(f'Conditional Variable: {final_key} overwritten to "{variables[final_key]}"')
                            continue
                        if "conditions" not in con_value:
                            raise Failed(f"{self.data_type} Error: conditions sub-attribute required")
                        conditions = con_value["conditions"]
                        if isinstance(conditions, dict):
                            conditions = [conditions]
                        if not isinstance(conditions, list):
                            raise Failed(f"{self.data_type} Error: conditions sub-attribute must be a list or dictionary")
                        condition_found = False
                        for i, condition in enumerate(conditions, 1):
                            if not isinstance(condition, dict):
                                raise Failed(f"{self.data_type} Error: each condition must be a dictionary")
                            if "value" not in condition:
                                raise Failed(f"{self.data_type} Error: each condition must have a result value")
                            condition_passed = True
                            for var_key, var_value in condition.items():
                                if var_key == "value":
                                    continue
                                error_text = ""
                                con_var_value = ""
                                var_key = replace_var(var_key, [variables, default])
                                var_value = replace_var(var_value, [variables, default])
                                if var_key.endswith(".exists"):
                                    con_var_value = util.parse(self.data_type, var_key, var_value, datatype="bool", default=False)
                                    if con_var_value:
                                        if var_key[:-7] not in variables or variables[var_key[:-7]] is None:
                                            error_text = "- does not exist"
                                    elif var_key[:-7] in variables and variables[var_key[:-7]] is not None:
                                        error_text = "- exists"
                                    con_var_value = var_key[:-7]
                                elif var_key.endswith(".not"):
                                    if var_key[:-4] in variables:
                                        con_var_value = variables[var_key[:-4]]
                                        if isinstance(var_value, list):
                                            if con_var_value in var_value:
                                                error_text = f'in {var_value}'
                                        elif str(con_var_value) == str(var_value):
                                            error_text = f'is "{var_value}"'
                                elif var_key.endswith(".notdefault"):
                                    var_name = var_key[:-11]
                                    if var_name in variables or var_name in default:
                                        con_var_value = variables[var_name] if var_name in variables else default[var_name]
                                        if isinstance(var_value, list):
                                            if con_var_value in var_value:
                                                error_text = f'in {var_value}'
                                        elif str(con_var_value) == str(var_value):
                                            error_text = f'is "{var_value}"'
                                elif var_key in variables or var_key in default:
                                    con_var_value = variables[var_key] if var_key in variables else default[var_key]
                                    if isinstance(var_value, list):
                                        if con_var_value not in var_value:
                                            error_text = f'not in {var_value}'
                                    elif str(con_var_value) != str(var_value):
                                        error_text = f'is not "{var_value}"'
                                else:
                                    error_text = " is not a variable provided or a default variable"
                                if error_text:
                                    if con_var_value:
                                        error_text = f': "{con_var_value}" {error_text}'
                                    logger.trace(f'Condition {i} Failed: {var_key}{error_text}')
                                    condition_passed = False
                            if condition_passed:
                                logger.trace(f'Conditional Variable: {final_key} is "{condition["value"]}"')
                                condition_found = True
                                if condition["value"] is not None:
                                    variables[final_key] = condition["value"]
                                    variables[f"{final_key}_encoded"] = quote(condition["value"])
                                else:
                                    optional.append(final_key)
                                break
                        if not condition_found:
                            if "default" in con_value:
                                logger.trace(f'Conditional Variable: {final_key} defaults to "{con_value["default"]}"')
                                variables[final_key] = con_value["default"]
                                variables[f"{final_key}_encoded"] = quote(con_value["default"])
                            else:
                                logger.trace(f"Conditional Variable: {final_key} added as optional variable")
                                optional.append(str(final_key))
                                optional.append(f"{final_key}_encoded")

                    sort_name = None
                    sort_mapping = None
                    if "move_prefix" in template or "move_collection_prefix" in template:
                        prefix = None
                        if "move_prefix" in template:
                            prefix = template["move_prefix"]
                        elif "move_collection_prefix" in template:
                            logger.debug("")
                            logger.debug(f"{self.data_type} Warning: template sub-attribute move_collection_prefix will run as move_prefix")
                            prefix = template["move_collection_prefix"]
                        if prefix:
                            for op in util.get_list(prefix):
                                if not sort_name and variables[name_var].startswith(f"{op} "):
                                    sort_name = f"{variables[name_var][len(op):].strip()}, {op}"
                                if not sort_mapping and variables["mapping_name"].startswith(f"{op} "):
                                    sort_mapping = f"{variables['mapping_name'][len(op):].strip()}, {op}"
                                if sort_name and sort_mapping:
                                    break
                        else:
                            raise Failed(f"{self.data_type} Error: template sub-attribute move_prefix is blank")
                    variables[f"{self.data_type.lower()}_sort"] = sort_name if sort_name else variables[name_var]
                    variables["mapping_sort"] = sort_mapping if sort_mapping else variables["mapping_name"]

                    for key, value in variables.copy().items():
                        if "<<" in key and ">>" in key:
                            for k, v in variables.items():
                                if f"<<{k}>>" in key:
                                    key = key.replace(f"<<{k}>>", f"{v}")
                            for k, v in default.items():
                                if f"<<{k}>>" in key:
                                    key = key.replace(f"<<{k}>>", f"{v}")
                            if key not in variables:
                                variables[key] = value
                    for key, value in variables.copy().items():
                        variables[f"{key}_encoded"] = quote(value)

                    default = {k: v for k, v in default.items() if k not in variables}
                    og_optional = optional
                    optional = []
                    for key in og_optional:
                        if "<<" in key and ">>" in key:
                            for k, v in variables.items():
                                if f"<<{k}>>" in key:
                                    key = key.replace(f"<<{k}>>", f"{v}")
                            for k, v in default.items():
                                if f"<<{k}>>" in key:
                                    key = key.replace(f"<<{k}>>", f"{v}")
                        if key not in variables and key not in default:
                            optional.append(key)

                    logger.trace("")
                    logger.trace(f"Variables: {variables}")
                    logger.trace("")
                    logger.trace(f"Defaults: {default}")
                    logger.trace("")
                    logger.trace(f"Optional: {optional}")
                    logger.trace("")

                    def check_for_var(_method, _data, _debug):
                        def scan_text(og_txt, var, actual_value, second=False):
                            if og_txt is None:
                                return og_txt
                            elif str(og_txt) == f"<<{var}>>":
                                return actual_value
                            elif f"<<{var}" in str(og_txt):
                                final = str(og_txt).replace(f"<<{var}>>", str(actual_value)) if f"<<{var}>>" in str(og_txt) else str(og_txt)
                                if f"<<{var}" in final and second:
                                    match = re.search(f"<<({var}([+-])(\\d+))>>", final)
                                    if match:
                                        try:
                                            final = final.replace(f"<<{match.group(1)}>>", str(int(actual_value) + (int(match.group(3)) * (-1 if match.group(2) == "-" else 1))))
                                        except (ValueError, TypeError):
                                            logger.error(f"Template Error: {actual_value} must be a number to use {match.group(1)}")
                                            raise Failed
                                return final
                            else:
                                return og_txt
                        if _debug:
                            logger.trace(f"Start {_method}: {_data}")
                        try:
                            for i_check in range(8):
                                for option in optional:
                                    if option not in variables and f"<<{option}>>" in str(_data):
                                        raise Failed
                                for option in [False, True]:
                                    for variable, variable_data in variables.items():
                                        if (variable == "collection_name" or variable == "playlist_name") and _method in ["radarr_tag", "item_radarr_tag", "sonarr_tag", "item_sonarr_tag"]:
                                            _data = scan_text(_data, variable, variable_data.replace(",", ""), second=option)
                                        elif (variable == "name_format" and _method != "name") or (variable == "summary_format" and _method != "summary"):
                                            continue
                                        elif variable != "name" and (_method not in ["name", "summary"] or variable != "key_name"):
                                            _data = scan_text(_data, variable, variable_data, second=option)
                                for dm, dd in default.items():
                                    if (dm == "name_format" and _method != "name") or (dm == "summary_format" and _method != "summary"):
                                        continue
                                    elif _method not in ["name", "summary"] or dm != "key_name":
                                        _data = scan_text(_data, dm, dd)
                        except Failed:
                            if _debug:
                                logger.trace(f"Failed {_method}: {_data}")
                            raise
                        if _debug:
                            logger.trace(f"End {_method}: {_data}")
                        return _data

                    def check_data(_method, _data, _debug):
                        if isinstance(_data, dict):
                            final_data = {}
                            for sm, sd in _data.items():
                                try:
                                    final_data[check_for_var(_method, sm, _debug)] = check_data(_method, sd, _debug)
                                except Failed:
                                    continue
                            if not final_data:
                                raise Failed
                        elif isinstance(_data, list):
                            final_data = []
                            for li in _data:
                                try:
                                    final_data.append(check_data(_method, li, _debug))
                                except Failed:
                                    continue
                            if not final_data:
                                raise Failed
                        else:
                            final_data = check_for_var(_method, _data, _debug)
                        return final_data

                    for method_name, attr_data in template.items():
                        if method_name not in data and method_name not in ["default", "optional", "conditionals", "move_collection_prefix", "move_prefix"]:
                            try:
                                debug_template = False
                                new_name = check_for_var(method_name, method_name, debug_template)
                                if new_name in new_attributes:
                                    logger.trace("")
                                    logger.trace(f"Template Warning: template attribute: {new_name} from {variables['name']} skipped")
                                else:
                                    new_attributes[new_name] = check_data(new_name, attr_data, debug_template)
                            except Failed:
                                continue
                    logger.trace(f"Current Final: {new_attributes}")
                    logger.trace("")
            logger.separator(f"Final Template Attributes", space=False, border=False, debug=True)
            logger.debug("")
            logger.debug(new_attributes)
            logger.debug("")
            return new_attributes

    def external_templates(self, data, overlay=False):
        if data and "external_templates" in data and data["external_templates"]:
            files, _ = util.load_files(data["external_templates"], "external_templates")
            if not files:
                logger.error("Config Error: No Paths Found for external_templates")
            for file_type, template_file, temp_vars, _ in files:
                temp_data = self.load_file(file_type, template_file, overlay=overlay)
                if temp_data and isinstance(temp_data, dict) and "templates" in temp_data and temp_data["templates"] and isinstance(temp_data["templates"], dict):
                    self.templates.update({k: (v, temp_vars) for k, v in temp_data["templates"].items() if k not in self.templates})

class MetadataFile(DataFile):
    def __init__(self, config, library, file_type, path, temp_vars, asset_directory, file_style):
        self.file_style = file_style
        self.type_str = f"{file_style.capitalize()} File"
        super().__init__(config, file_type, path, temp_vars, asset_directory, self.type_str)
        self.data_type = "Collection"
        self.library = library
        self.metadata = None
        self.collections = None
        self.dynamic_collections = []
        self.templates = None
        self.update_collections = True
        self.update_seasons = True
        self.update_episodes = True
        self.set_collections = {}
        self.style_priority = []
        if self.file_style == "image":
            self.metadata = {}
            if self.type == "Default":
                if self.path.endswith(".yml"):
                    self.path = self.path[:-4]
                elif self.path.endswith(".yaml"):
                    self.path = self.path[:-5]
                data = self.load_file(self.type, "set", images=True, folder=f"{self.path}/")
            else:
                data = self.load_file(self.type, self.path, images=True)
            methods = {t.lower(): t for t in self.temp_vars}

            use_all = True if "use_all" in methods and self.temp_vars[methods["use_all"]] else False
            logger.info(f"Use All Sections: {use_all}")

            exclude = []
            if "exclude" in methods:
                if not use_all:
                    raise Failed(f"Image Set Error: exclude only works when use_all is true")
                exclude = util.parse("Images", "exclude", self.temp_vars, datatype="list", methods=methods)
                logger.info(f"Exclude: {exclude}")

            include = []
            if "include" in methods:
                if use_all:
                    raise Failed(f"Image Set Error: include only works when use_all is false")
                include = util.parse("Images", "include", self.temp_vars, datatype="list", methods=methods)
                logger.info(f"Include: {include}")

            if "style_priority" in methods:
                self.style_priority = util.parse("Images", "style_priority", self.temp_vars, datatype="list", methods=methods)
                logger.info(f"Style Priority: {self.style_priority}")

            if "update_collections" in methods:
                self.update_collections = util.parse("Images", "update_collections", self.temp_vars, datatype="bool", methods=methods, default=True)
            logger.info(f"Update Collections: {self.update_collections}")

            if "update_seasons" in methods:
                self.update_seasons = util.parse("Images", "update_seasons", self.temp_vars, datatype="bool", methods=methods, default=True)
            logger.info(f"Update Seasons: {self.update_seasons}")

            if "update_episodes" in methods:
                self.update_episodes = util.parse("Images", "update_episodes", self.temp_vars, datatype="bool", methods=methods, default=True)
            logger.info(f"Update Episodes: {self.update_episodes}")
            item_attr = "movies" if self.library.is_movie else "shows"
            for section_key, section_data in get_dict("sections", data).items():
                if not isinstance(section_data, dict):
                    raise Failed("Image Set Error: Section Data must be a dictionary")
                if "builders" not in section_data or not section_data["builders"]:
                    logger.trace(f"Skipping No Builder for Section: {section_key}")
                    continue
                elif item_attr not in section_data:
                    raise Failed(f"Section Data must have the {item_attr} attribute")
                elif not section_data[item_attr]:
                    raise Failed(f"Section Data attribute {item_attr} is empty")
                elif "styles" not in section_data:
                    raise Failed("Image Section Error: Section Data must have the styles attribute")
                styles = util.parse("Section Data", "styles", section_data["styles"], datatype="dictlist")
                if not styles:
                    raise Failed("Image Section Error: Section Data styles attribute is empty")
                default_style = None
                for sk, sv in styles.items():
                    default_style = sk
                    break
                if not default_style:
                    raise Failed(f"Image Section Error: No styles found for section: {section_key}")
                use_key = None
                if f"use_{section_key}" in methods:
                    use_key = util.parse("Images", f"use_{section_key}", self.temp_vars, datatype="bool", methods=methods, default=False)
                    logger.info(f"Use {section_key}: {use_key}")
                if use_key is False:
                    logger.trace(f"Skipped as use_{section_key} is false")
                    continue
                elif use_all and section_key in exclude:
                    logger.trace(f"Skipped as {section_key} is in the exclude list")
                    continue
                elif not use_all and use_key is None and section_key not in include:
                    logger.trace(f"Skipped as use_all is false and use_{section_key} is not set{f' and {section_key} not in the include list' if include else ''}")
                    continue
                prioritized_style = None
                for ps in self.style_priority:
                    if ps in styles:
                        prioritized_style = ps
                        break
                if f"style_{section_key}" in methods:
                    style_key = util.parse("Images", f"style_{section_key}", self.temp_vars, methods=methods, default=default_style)
                    logger.info(f"Style {section_key}: {style_key}")
                    if style_key not in styles:
                        p_warning = f"Image Section Warning: {section_key} has no style: {style_key} using"
                        if prioritized_style:
                            logger.warning(f"{p_warning} Prioritized Style: {prioritized_style}")
                            style_key = prioritized_style
                        else:
                            logger.warning(f"{p_warning} default: {default_style}. Options: {', '.join([s for s in styles])}")
                            style_key = default_style
                elif prioritized_style:
                    logger.info(f"Using Prioritized Style: {prioritized_style}")
                    style_key = prioritized_style
                else:
                    style_key = default_style
                if self.update_collections and "collections" in section_data and section_data["collections"]:
                    self.set_collections[section_key] = section_data["collections"]

                if f"style_file_{section_key}" in methods:
                    style_file = self.temp_vars[methods[f"style_file_{section_key}"]]
                elif not styles[style_key]:
                    style_file = [{"pmm": f"{section_key}/{style_key}"}]
                else:
                    style_file = styles[style_key]
                if not style_file:
                    raise Failed("Image Style Error: style file call attribute is blank")
                style_dict = style_file[0] if isinstance(style_file, list) else style_file
                if not isinstance(style_dict, dict):
                    raise Failed(f"Image Style Error: style file call attribute: {style_dict} is not a dictionary")
                elif not style_dict:
                    raise Failed("Image Style Error: style file call attribute dictionary is empty")
                style_data = self.get_style_data(style_dict, section_key, items_data=section_data[item_attr])
                for item_name, item_data in section_data[item_attr].items():
                    if item_name not in style_data or not style_data[item_name]:
                        continue
                    if isinstance(item_data, dict):
                        if "mapping_id" not in item_data:
                            raise Failed(f"Image Section Error: {section_key}: {item_name}: No mapping ID found")
                        meta_data = item_data
                    else:
                        meta_data = {"mapping_id": item_data}
                    meta_data["style_data"] = style_data[item_name]
                    meta_data["section_key"] = section_key
                    meta_data["style_key"] = style_key
                    if "seasons" in style_data[item_name] and style_data[item_name]["seasons"]:
                        season_dict = {}
                        for season_num, season_data in style_data[item_name]["seasons"].items():
                            season_dict[season_num] = {}
                            if season_data and "episodes" in season_data:
                                episode_dict = {}
                                for episode_num in season_data["episodes"]:
                                    episode_dict[episode_num] = {}
                                season_dict[season_num]["episodes"] = episode_dict
                        meta_data["seasons"] = season_dict
                    self.metadata[item_name] = meta_data
            if not self.metadata:
                raise Failed(f"{self.type_str} Error: No metadata items added")
            logger.info("")
            logger.info("Images File Loaded Successfully")
        elif file_type == "Data":
            self.collections = get_dict("collections", path, library.collections)
            self.templates = get_dict("templates", path)
        else:
            logger.info("")
            logger.separator(f"Loading {self.type_str} {file_type}: {path}")
            logger.info("")
            data = self.load_file(self.type, self.path)
            if self.file_style == "metadata":
                self.metadata = get_dict("metadata", data, library.metadatas)
            self.templates = get_dict("templates", data)
            self.external_templates(data)
            if self.file_style == "collection":
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
                        auto_type = dynamic[methods["type"]].lower()
                        og_exclude = []
                        if "exclude" in self.temp_vars:
                            og_exclude = util.parse("Config", "exclude", self.temp_vars["exclude"], parent="template_variables", datatype="strlist")
                        elif "exclude" in methods:
                            og_exclude = util.parse("Config", "exclude", dynamic, parent=map_name, methods=methods, datatype="strlist")
                        if "append_exclude" in self.temp_vars:
                            og_exclude.extend(util.parse("Config", "append_exclude", self.temp_vars["append_exclude"], parent="template_variables", datatype="strlist"))
                        if "remove_exclude" in self.temp_vars:
                            for word in util.parse("Config", "remove_exclude", self.temp_vars["remove_exclude"], parent="template_variables", datatype="strlist"):
                                og_exclude.remove(word)
                        include = []
                        if "include" in self.temp_vars:
                            include = util.parse("Config", "include", self.temp_vars["include"], parent="template_variables", datatype="strlist")
                        elif "include" in methods:
                            include = [i for i in util.parse("Config", "include", dynamic, parent=map_name, methods=methods, datatype="strlist") if i not in og_exclude]
                        if "append_include" in self.temp_vars:
                            include.extend(util.parse("Config", "append_include", self.temp_vars["append_include"], parent="template_variables", datatype="strlist"))
                        if "remove_include" in self.temp_vars:
                            for word in util.parse("Config", "remove_include", self.temp_vars["remove_include"], parent="template_variables", datatype="strlist"):
                                include.remove(word)
                        addons = {}
                        if "addons" in self.temp_vars:
                            addons = util.parse("Config", "addons", self.temp_vars["addons"], parent="template_variables", datatype="dictliststr")
                        elif "addons" in methods:
                            addons = util.parse("Config", "addons", dynamic, parent=map_name, methods=methods, datatype="dictliststr")
                        if "append_addons" in self.temp_vars:
                            append_addons = util.parse("Config", "append_addons", self.temp_vars["append_addons"], parent=map_name, methods=methods, datatype="dictliststr")
                            for k, v in append_addons.items():
                                if k not in addons:
                                    addons[k] = []
                                addons[k].extend(v)
                        if "remove_addons" in self.temp_vars:
                            remove_addons = util.parse("Config", "remove_addons", self.temp_vars["remove_addons"], parent=map_name, methods=methods, datatype="dictliststr")
                            for k, v in remove_addons.items():
                                if k in addons:
                                    for word in v:
                                        addons[k].remove(word)

                        exclude = [str(e) for e in og_exclude]
                        for k, v in addons.items():
                            if k in v:
                                logger.warning(f"Config Warning: {k} cannot be an addon for itself")
                            exclude.extend([y for y in v if y != k and y not in exclude])
                        default_title_format = "<<key_name>>"
                        default_template = None
                        auto_list = {}
                        all_keys = {}
                        extra_template_vars = {}
                        dynamic_data = None
                        def _check_dict(check_dict):
                            for ck, cv in check_dict.items():
                                all_keys[str(ck)] = cv
                                if str(ck) not in exclude and str(cv) not in exclude:
                                    auto_list[str(ck)] = cv
                        if auto_type == "decade" and library.is_show:
                            all_items = library.get_all()
                            if addons:
                                raise Failed(f"Config Error: addons cannot be used with show decades")
                            addons = {}
                            all_keys = {}
                            for i, item in enumerate(all_items, 1):
                                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                                if item.year:
                                    decade = str(int(math.floor(item.year / 10) * 10))
                                    if decade not in addons:
                                        addons[decade] = []
                                    if str(item.year) not in addons[decade]:
                                        addons[decade].append(str(item.year))
                                        all_keys[str(item.year)] = str(item.year)
                            auto_list = {str(k): f"{k}s" for k in addons if str(k) not in exclude and f"{k}s" not in exclude}
                            default_template = {"smart_filter": {"limit": 50, "sort_by": "critic_rating.desc", "any": {"year": "<<value>>"}}}
                            default_title_format = "Best <<library_type>>s of the <<key_name>>"
                        elif auto_type in ["genre", "mood", "style", "album_genre", "album_mood", "album_style", "track_mood", "country", "studio", "edition", "network", "year", "episode_year", "decade", "content_rating", "subtitle_language", "audio_language", "resolution"]:
                            search_tag = auto_type_translation[auto_type] if auto_type in auto_type_translation else auto_type
                            if library.is_show and auto_type in ["resolution", "subtitle_language", "audio_language"]:
                                tags = library.get_tags(f"episode.{search_tag}")
                            else:
                                tags = library.get_tags(search_tag)
                            if auto_type in ["subtitle_language", "audio_language"]:
                                all_keys = {}
                                auto_list = {}
                                for i in tags:
                                    final_title = self.config.TMDb.TMDb._iso_639_1[str(i.key)].english_name if str(i.key) in self.config.TMDb.TMDb._iso_639_1 else str(i.title) # noqa
                                    all_keys[str(i.key)] = final_title
                                    if all([x not in exclude for x in [final_title, str(i.title), str(i.key)]]):
                                        auto_list[str(i.key)] = final_title
                            elif auto_type in ["resolution", "decade"]:
                                all_keys = {str(i.key): i.title for i in tags}
                                auto_list = {str(i.key): i.title for i in tags if str(i.title) not in exclude and str(i.key) not in exclude}
                            else:
                                all_keys = {str(i.title): i.title for i in tags}
                                auto_list = {str(i.title): i.title for i in tags if str(i.title) not in exclude}
                            if library.is_music:
                                final_var = auto_type if auto_type.startswith(("album", "track")) else f"artist_{auto_type}"
                                default_template = {"smart_filter": {"limit": 50 if auto_type.startswith("track") else 10, "sort_by": "plays.desc", "any": {final_var: "<<value>>"}}}
                                music_type = "<<library_type>>"
                                if auto_type.startswith(("album", "track")):
                                    default_template["builder_level"] = "album" if auto_type.startswith("album") else "track"
                                    music_type = "Album" if auto_type.startswith("album") else "Track"
                                default_title_format = f"Most Played <<key_name>> {music_type}s"
                            elif auto_type == "resolution":
                                default_template = {"smart_filter": {"sort_by": "title.asc", "any": {auto_type: "<<value>>"}}}
                                default_title_format = "<<key_name>> <<library_type>>s"
                            else:
                                default_template = {"smart_filter": {"limit": 50, "sort_by": "critic_rating.desc", "any": {f"{auto_type}.is" if auto_type == "studio" else auto_type: "<<value>>"}}}
                                if auto_type.startswith("episode"):
                                    default_template["builder_level"] = "episode"
                                    default_title_format = "Best Episodes of <<key_name>>"
                                elif auto_type == "year":
                                    default_title_format = "Best <<library_type>>s of <<key_name>>"
                                elif auto_type == "decade":
                                    default_title_format = "Best <<library_type>>s of the <<key_name>>"
                                else:
                                    default_title_format = "Top <<key_name>> <<library_type>>s"
                        elif auto_type == "tmdb_collection":
                            all_items = library.get_all()
                            for i, item in enumerate(all_items, 1):
                                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                                tmdb_id, tvdb_id, imdb_id = library.get_ids(item)
                                tmdb_item = config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=True)
                                if tmdb_item and tmdb_item.collection_id and tmdb_item.collection_name:
                                    all_keys[str(tmdb_item.collection_id)] = tmdb_item.collection_name
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
                                    all_keys[tmdb_item.language_iso] = tmdb_item.language_name
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
                                        all_keys[country.iso_3166_1.lower()] = country.name
                                        if country.iso_3166_1.lower() not in exclude and country.name not in exclude:
                                            auto_list[country.iso_3166_1.lower()] = country.name
                            logger.exorcise()
                            default_title_format = "<<key_name>> <<library_type>>s"
                        elif auto_type in ["actor", "director", "writer", "producer"]:
                            people = {}
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="dict")
                            if "data" in self.temp_vars:
                                temp_data = util.parse("Config", "data", self.temp_vars["data"], datatype="dict")
                                for k, v in temp_data.items():
                                    dynamic_data[k] = v
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
                            lib_all = library.get_all()
                            include_cols = []
                            for i, item in enumerate(lib_all, 1):
                                logger.ghost(f"Scanning: {i}/{len(lib_all)} {item.title}")
                                try:
                                    item = self.library.reload(item)
                                    for person in getattr(item, f"{auto_type}s")[:person_depth]:
                                        if person.tag in include:
                                            if person.tag not in include_cols:
                                                include_cols.append(person.tag)
                                        else:
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
                            for inc in include_cols:
                                auto_list[inc] = inc
                                all_keys[inc] = inc
                                person_count += 1
                            for role in roles:
                                if person_count < person_limit and role["count"] >= person_minimum and role["name"] not in exclude:
                                    auto_list[role["name"]] = role["name"]
                                    all_keys[role["name"]] = role["name"]
                                    person_count += 1
                            default_template = {"plex_search": {"any": {auto_type: "<<value>>"}}}
                        elif auto_type == "imdb_awards":
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="dict")
                            if "data" in self.temp_vars:
                                temp_data = util.parse("Config", "data", self.temp_vars["data"], datatype="dict")
                                for k, v in temp_data.items():
                                    dynamic_data[k] = v
                            award_methods = {am.lower(): am for am in dynamic_data}
                            event_id = util.parse("Config", "event_id", dynamic_data, parent=f"{map_name} data", methods=award_methods, regex=(r"(ev\d+)", "ev0000003"))
                            extra_template_vars["event_id"] = event_id
                            if event_id not in self.config.IMDb.events_validation:
                                raise Failed(f"Config Error: {map_name} data only specific Event IDs work with imdb_awards. Event Options: [{', '.join([k for k in self.config.IMDb.events_validation])}]")
                            _, event_years = self.config.IMDb.get_event_years(event_id)
                            year_options = [event_years[len(event_years) - i] for i in range(1, len(event_years) + 1)]

                            def get_position(attr):
                                if attr not in award_methods:
                                    return 0 if attr == "starting" else len(year_options)
                                position_value = str(dynamic_data[award_methods[attr]])
                                if not position_value:
                                    raise Failed(f"Config Error: {map_name} data {attr} attribute is blank")
                                if position_value.startswith(("first", "latest", "current_year")):
                                    is_first = position_value.startswith("first")
                                    int_values = position_value.split("+" if is_first else "-")
                                    try:
                                        if len(int_values) == 1:
                                            return 1 if is_first else len(year_options)
                                        else:
                                            return (int(int_values[1].strip()) + (1 if is_first else 0)) * (1 if is_first else -1)
                                    except ValueError:
                                        raise Failed(f"Config Error: {map_name} data {attr} attribute modifier invalid '{int_values[1]}'")
                                elif position_value in year_options:
                                    return year_options.index(position_value) + 1
                                else:
                                    raise Failed(f"Config Error: {map_name} data {attr} attribute invalid: {position_value}")

                            found_options = year_options[get_position("starting") - 1:get_position("ending")]

                            if not found_options:
                                raise Failed(f"Config Error: {map_name} data starting/ending range found no valid events")
                            for option in event_years:
                                all_keys[option] = option
                                if option not in exclude and option in found_options:
                                    auto_list[option] = option
                            default_template = {"imdb_award": {"event_id": "<<event_id>>", "event_year": "<<value>>", "winning": True}}
                        elif auto_type == "number":
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="dict")
                            if "data" in self.temp_vars:
                                temp_data = util.parse("Config", "data", self.temp_vars["data"], datatype="dict")
                                for k, v in temp_data.items():
                                    dynamic_data[k] = v
                            number_methods = {nm.lower(): nm for nm in dynamic_data}
                            if "starting" in number_methods and str(dynamic_data[number_methods["starting"]]).startswith("current_year"):
                                year_values = str(dynamic_data[number_methods["starting"]]).split("-")
                                try:
                                    starting = datetime.now().year - (0 if len(year_values) == 1 else int(year_values[1].strip()))
                                except ValueError:
                                    raise Failed(f"Config Error: {map_name} data starting attribute modifier invalid '{year_values[1]}'")
                            else:
                                starting = util.parse("Config", "starting", dynamic_data, parent=f"{map_name} data", methods=number_methods, datatype="int", default=0, minimum=0)
                            if "ending" in number_methods and str(dynamic_data[number_methods["ending"]]).startswith("current_year"):
                                year_values = str(dynamic_data[number_methods["ending"]]).split("-")
                                try:
                                    ending = datetime.now().year - (0 if len(year_values) == 1 else int(year_values[1].strip()))
                                except ValueError:
                                    raise Failed(f"Config Error: {map_name} data ending attribute modifier invalid '{year_values[1]}'")
                            else:
                                ending = util.parse("Config", "ending", dynamic_data, parent=f"{map_name} data", methods=number_methods, datatype="int", default=0, minimum=1)
                            increment = util.parse("Config", "increment", dynamic_data, parent=f"{map_name} data", methods=number_methods, datatype="int", default=1, minimum=1) if "increment" in number_methods else 1
                            if starting > ending:
                                raise Failed(f"Config Error: {map_name} data ending must be greater than starting")
                            current = starting
                            while current <= ending:
                                all_keys[str(current)] = str(current)
                                if str(current) not in exclude and current not in exclude:
                                    auto_list[str(current)] = str(current)
                                current += increment
                        elif auto_type == "custom":
                            if "data" in self.temp_vars:
                                dynamic_data = util.parse("Config", "data", self.temp_vars["data"], datatype="strdict")
                            else:
                                dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="strdict")
                            if "remove_data" in self.temp_vars:
                                for k in util.parse("Config", "remove_data", self.temp_vars["remove_data"], datatype="strlist"):
                                    if k in dynamic_data:
                                        dynamic_data.pop(k)
                            if "append_data" in self.temp_vars:
                                for k, v in util.parse("Config", "append_data", self.temp_vars["append_data"], datatype="strdict").items():
                                    dynamic_data[k] = v
                            for k, v in dynamic_data.items():
                                all_keys[k] = v
                                if k not in exclude and v not in exclude:
                                    auto_list[k] = v
                        elif auto_type == "trakt_liked_lists":
                            _check_dict(self.config.Trakt.all_liked_lists())
                        elif auto_type == "tmdb_popular_people":
                            if "data" in self.temp_vars:
                                dynamic_data = util.parse("Config", "data", self.temp_vars["data"], datatype="int", minimum=1)
                            else:
                                dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="int", minimum=1)
                            _check_dict(self.config.TMDb.get_popular_people(dynamic_data))
                        elif auto_type in ["trakt_people_list", "trakt_user_lists"]:
                            if "data" in self.temp_vars:
                                dynamic_data = util.parse("Config", "data", self.temp_vars["data"], datatype="strlist")
                            else:
                                dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="strlist")
                            if "remove_data" in self.temp_vars:
                                for k in util.parse("Config", "remove_data", self.temp_vars["remove_data"], datatype="strlist"):
                                    if k in dynamic_data:
                                        dynamic_data.remove(k)
                            if "append_data" in self.temp_vars:
                                for k in util.parse("Config", "append_data", self.temp_vars["append_data"], datatype="strlist"):
                                    if k not in dynamic_data:
                                        dynamic_data.append(k)
                            for option in dynamic_data:
                                if auto_type == "trakt_user_lists":
                                    _check_dict({self.config.Trakt.build_user_url(u[0], u[1]): u[2] for u in self.config.Trakt.all_user_lists(option)})
                                else:
                                    _check_dict(self.config.Trakt.get_people(option))
                        else:
                            raise Failed(f"Config Error: {map_name} type attribute {dynamic[methods['type']]} invalid")

                        if "append_data" in self.temp_vars:
                            for k, v in util.parse("Config", "append_data", self.temp_vars["append_data"], parent=map_name, methods=methods, datatype="strdict").items():
                                all_keys[k] = v
                                if k not in exclude and v not in exclude:
                                    auto_list[k] = v
                        custom_keys = True
                        if "custom_keys" in self.temp_vars:
                            custom_keys = util.parse("Config", "custom_keys", self.temp_vars["custom_keys"], parent="template_variables", default=custom_keys)
                        elif "custom_keys" in methods:
                            custom_keys = util.parse("Config", "custom_keys", dynamic, parent=map_name, methods=methods, default=custom_keys)
                        for add_key, combined_keys in addons.items():
                            if add_key not in all_keys and add_key not in og_exclude:
                                final_keys = [ck for ck in combined_keys if ck in all_keys]
                                if custom_keys and final_keys:
                                    auto_list[add_key] = add_key
                                    addons[add_key] = final_keys
                                elif custom_keys:
                                    logger.trace(f"Config Warning: {add_key} Custom Key must have at least one Key")
                                else:
                                    for final_key in final_keys:
                                        auto_list[final_key] = all_keys[final_key]
                        title_format = default_title_format
                        if "title_format" in self.temp_vars:
                            title_format = util.parse("Config", "title_format", self.temp_vars["title_format"], parent="template_variables", default=default_title_format)
                        elif "title_format" in methods:
                            title_format = util.parse("Config", "title_format", dynamic, parent=map_name, methods=methods, default=default_title_format)
                        if "<<key_name>>" not in title_format and "<<title>>" not in title_format:
                            logger.error(f"Config Error: <<key_name>> not in title_format: {title_format} using default: {default_title_format}")
                            title_format = default_title_format
                        if "post_format_override" in methods:
                            methods["title_override"] = methods.pop("post_format_override")
                        if "pre_format_override" in methods:
                            methods["key_name_override"] = methods.pop("pre_format_override")
                        title_override = {}
                        if "title_override" in self.temp_vars:
                            title_override = util.parse("Config", "title_override", self.temp_vars["title_override"], parent="template_variables", datatype="strdict")
                        elif "title_override" in methods:
                            title_override = util.parse("Config", "title_override", dynamic, parent=map_name, methods=methods, datatype="strdict")
                        key_name_override = {}
                        if "key_name_override" in self.temp_vars:
                            key_name_override = util.parse("Config", "key_name_override", self.temp_vars["key_name_override"], parent="template_variables", datatype="strdict")
                        elif "key_name_override" in methods:
                            key_name_override = util.parse("Config", "key_name_override", dynamic, parent=map_name, methods=methods, datatype="strdict")
                        test_override = []
                        for k, v in key_name_override.items():
                            if v in test_override:
                                logger.warning(f"Config Warning: {v} can only be used once skipping {k}: {v}")
                                key_name_override.pop(k)
                            else:
                                test_override.append(v)
                        test = False
                        if "test" in self.temp_vars:
                            test = util.parse("Config", "test", self.temp_vars["test"], parent="template_variables", datatype="bool")
                        elif "test" in methods:
                            test = util.parse("Config", "test", dynamic, parent=map_name, methods=methods, default=False, datatype="bool")
                        sync = False
                        if "sync" in self.temp_vars:
                            sync = util.parse("Config", "sync", self.temp_vars["sync"], parent="template_variables", datatype="bool")
                        elif "sync" in methods:
                            sync = util.parse("Config", "sync", dynamic, parent=map_name, methods=methods, default=False, datatype="bool")
                        if "<<library_type>>" in title_format:
                            title_format = title_format.replace("<<library_type>>", library.type.lower())
                        if "<<library_typeU>>" in title_format:
                            title_format = title_format.replace("<<library_typeU>>", library.type)
                        if "limit" in self.temp_vars and "<<limit>>" in title_format:
                            title_format = title_format.replace("<<limit>>", str(self.temp_vars["limit"]))
                        template_variables = util.parse("Config", "template_variables", dynamic, parent=map_name, methods=methods, datatype="dictdict") if "template_variables" in methods else {}
                        if "template" in methods:
                            template_names = util.parse("Config", "template", dynamic, parent=map_name, methods=methods, datatype="strlist")
                            has_var = False
                            for template_name in template_names:
                                if template_name not in self.templates:
                                    raise Failed(f"Config Error: {map_name} template: {template_name} not found")
                                if any([a in str(self.templates[template_name][0]) for a in ["<<value", "<<key", f"<<{auto_type}"]]):
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
                            remove_prefix = util.parse("Config", "remove_prefix", self.temp_vars["remove_prefix"], parent="template_variables", datatype="commalist")
                        elif "remove_prefix" in methods:
                            remove_prefix = util.parse("Config", "remove_prefix", dynamic, parent=map_name, methods=methods, datatype="commalist")
                        remove_suffix = []
                        if "remove_suffix" in self.temp_vars:
                            remove_suffix = util.parse("Config", "remove_suffix", self.temp_vars["remove_suffix"], parent="template_variables", datatype="commalist")
                        elif "remove_suffix" in methods:
                            remove_suffix = util.parse("Config", "remove_suffix", dynamic, parent=map_name, methods=methods, datatype="commalist")
                        sync = {i.title: i for i in self.library.get_all_collections(label=str(map_name))} if sync else {}
                        other_name = None
                        if "other_name" in self.temp_vars and include:
                            other_name = util.parse("Config", "other_name", self.temp_vars["remove_suffix"], parent="template_variables")
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
                        logger.debug(f"Exclude: {og_exclude}")
                        logger.debug(f"Exclude Final: {exclude}")
                        logger.debug(f"Addons: {addons}")
                        logger.debug(f"Template: {template_names}")
                        logger.debug(f"Other Template: {other_templates}")
                        logger.debug(f"Library Variables: {self.temp_vars}")
                        logger.debug(f"Template Variables: {template_variables}")
                        logger.debug(f"Remove Prefix: {remove_prefix}")
                        logger.debug(f"Remove Suffix: {remove_suffix}")
                        logger.debug(f"Title Format: {title_format}")
                        logger.debug(f"Key Name Override: {key_name_override}")
                        logger.debug(f"Title Override: {title_override}")
                        logger.debug(f"Custom Keys: {custom_keys}")
                        logger.debug(f"Test: {test}")
                        logger.debug(f"Sync: {sync}")
                        logger.debug(f"Include: {include}")
                        logger.debug(f"Other Name: {other_name}")
                        logger.debug(f"All Keys: {all_keys.keys()}")
                        if not auto_list:
                            raise Failed("No Keys found to create a set of Dynamic Collections")
                        logger.debug(f"Keys (Title):")
                        for key, value in auto_list.items():
                            logger.debug(f"  - {key}{'' if key == value else f' ({value})'}")

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
                                key_value.extend([a for a in addons[key] if (a in all_keys or auto_type == "custom") and a != key])
                            used_keys.extend(key_value)
                            og_call = {"value": key_value, auto_type: key_value, "key_name": key_name, "key": key}
                            for k, v in template_variables.items():
                                if k in self.temp_vars:
                                    og_call[k] = self.temp_vars[k]
                                elif key in v:
                                    og_call[k] = v[key]
                                elif "default" in v:
                                    og_call[k] = v["default"]
                            for k, v in extra_template_vars.items():
                                if k not in og_call:
                                    og_call[k] = v
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
                                logger.info(template_call)
                                col = {"template": template_call, "append_label": str(map_name)}
                                if test:
                                    col["test"] = True
                                if collection_title in sync:
                                    sync.pop(collection_title)
                                col_names.append(collection_title)
                                self.collections[collection_title] = col
                        if other_name and not other_keys:
                            logger.warning(f"Config Warning: Other Collection {other_name} not needed")
                        elif other_name:
                            og_other = {
                                "value": other_keys, "included_keys": include, "used_keys": used_keys,
                                auto_type: other_keys, "key_name": other_name, "key": "other"
                            }
                            for k, v in template_variables.items():
                                if k in self.temp_vars and "other" in self.temp_vars[k]:
                                    og_other[k] = self.temp_vars[k]["other"]
                                elif k in self.temp_vars and "default" in self.temp_vars[k]:
                                    og_other[k] = self.temp_vars[k]["default"]
                                if "other" in v:
                                    og_other[k] = v["other"]
                                elif "default" in v:
                                    og_other[k] = v["default"]
                            other_call = []
                            for other_template in other_templates:
                                new_call = og_other.copy()
                                new_call["name"] = other_template
                                other_call.append(new_call)
                            col = {"template": other_call, "append_label": str(map_name)}
                            if test:
                                col["test"] = True
                            if other_name in sync:
                                sync.pop(other_name)
                            self.collections[other_name] = col
                        for col_title, col in sync.items():
                            try:
                                self.library.delete(col)
                                logger.info(f"{map_name} Dynamic Collection: {col_title} Deleted")
                            except Failed as e:
                                logger.error(e)
                    except Failed as e:
                        logger.error(e)
                        logger.error(f"{map_name} Dynamic Collection Failed")
                        continue

            if self.file_style == "metadata" and not self.metadata:
                raise Failed("YAML Error: metadata attribute is required")
            if self.file_style == "collection" and not self.collections:
                raise Failed("YAML Error: collections or dynamic_collections attribute is required")
            logger.info("")
            logger.info(f"{self.type_str} Loaded Successfully")

    def get_style_data(self, style_file, section_key, items_data=None):
        style_id = ""
        for k, v in style_file.items():
            style_id = f"{k}: {v}"
            break
        if style_id in self.library.image_styles:
            return self.library.image_styles[style_id]
        if "git_style" in style_file:
            if not style_file["git_style"]:
                raise Failed("Image Set Error: git_style cannot be blank")
            if not items_data:
                raise Failed("Image Set Error: items_data cannot be blank")
            top_tree, repo = self.config.GitHub.get_top_tree(style_file["git_style"])
            sub = style_file["git_subfolder"] if "git_subfolder" in style_file and style_file["git_subfolder"] else ""
            sub = sub.replace("\\", "/")
            if sub.startswith("/"):
                sub = sub[1:]
            if sub.endswith("/"):
                sub = sub[:-1]
            if sub:
                sub_str = ""
                for folder in sub.split("/"):
                    folder_encode = quote(folder)
                    sub_str += f"{folder_encode}/"
                    if folder not in top_tree:
                        raise Failed(f"Image Set Error: Subfolder {folder} Not Found at https://github.com{repo}tree/master/{sub_str}")
                    top_tree = self.config.GitHub.get_tree(top_tree[folder]["url"])
                sub = sub_str

            def repo_url(u):
                return f"https://raw.githubusercontent.com{repo}master/{sub}{u}"

            def from_repo(u):
                return self.config.Requests.get(repo_url(u)).content.decode().strip()

            def check_for_definition(check_key, check_tree, is_poster=True, git_name=None):
                attr_name = "poster" if is_poster and (git_name is None or "background" not in git_name) else "background"
                if (git_name and git_name.lower().endswith(".tpdb")) or (not git_name and f"{attr_name}.tpdb" in check_tree):
                    return f"tpdb_{attr_name}", from_repo(f"{check_key}/{quote(git_name) if git_name else f'{attr_name}.tpdb'}")
                elif (git_name and git_name.lower().endswith(".url")) or (not git_name and f"{attr_name}.url" in check_tree):
                    return f"url_{attr_name}", from_repo(f"{check_key}/{quote(git_name) if git_name else f'{attr_name}.url'}")
                elif git_name:
                    if git_name in check_tree:
                        return f"url_{attr_name}", repo_url(f"{check_key}/{quote(git_name)}")
                else:
                    for ct in check_tree:
                        if ct.lower().startswith(attr_name):
                            return f"url_{attr_name}", repo_url(f"{check_key}/{quote(ct)}")
                return None, None

            def init_set(check_key, check_tree):
                _data = {}
                attr, attr_data = check_for_definition(check_key, check_tree)
                if attr:
                    _data[attr] = attr_data
                attr, attr_data = check_for_definition(check_key, check_tree, is_poster=False)
                if attr:
                    _data[attr] = attr_data
                return _data

            style_data = {}
            for k in items_data:
                if k not in top_tree:
                    logger.info(f"Image Set Warning: {k} not found at https://github.com{repo}tree/master/{sub}")
                    continue
                k_encoded = quote(k)
                item_folder = self.config.GitHub.get_tree(top_tree[k]["url"])
                item_data = init_set(k_encoded, item_folder)
                seasons = {}
                for ik in item_folder:
                    match = re.search(r"(\d+)", ik)
                    if match:
                        season_path = f"{k_encoded}/{quote(ik)}"
                        season_num = int(match.group(1))
                        season_folder = self.config.GitHub.get_tree(item_folder[ik]["url"])
                        season_data = init_set(season_path, season_folder)
                        episodes = {}
                        for sk in season_folder:
                            match = re.search(r"(\d+)(?!.*\d)", sk)
                            if match:
                                episode_num = int(match.group(1))
                                if episode_num not in episodes:
                                    episodes[episode_num] = {}
                                    a, ad = check_for_definition(season_path, season_folder, git_name=sk)
                                    if a:
                                        episodes[episode_num][a] = ad
                        if episodes:
                            season_data["episodes"] = episodes
                        seasons[season_num] = season_data
                if seasons:
                    item_data["seasons"] = seasons
                style_data[k] = item_data

            self.library.image_styles[style_id] = style_data

            if section_key and section_key in self.set_collections and "collections" in top_tree:
                collections_folder = self.config.GitHub.get_tree(top_tree["collections"]["url"])
                for k, alts in self.set_collections[section_key].items():
                    if k in collections_folder:
                        collection_data = init_set(f"collections/{k}", self.config.GitHub.get_tree(collections_folder[k]["url"]))
                        self.library.collection_images[k] = collection_data
                        for alt in alts:
                            self.library.collection_images[alt] = collection_data
        else:
            files, _ = util.load_files(style_file, "style_file", err_type=self.type_str, single=True)
            if not files:
                raise Failed(f"{self.type_str} Error: No Path Found for style_file")
            file_type, style_path, _, _ = files[0]
            temp_data = self.load_file(file_type, style_path, images=True, folder=f"{self.path}/styles/")
            item_attr = "movies" if self.library.is_movie else "shows"
            if not isinstance(temp_data, dict):
                raise Failed("Image Style Error: base must be a dictionary")
            if item_attr not in temp_data:
                raise Failed(f"Image Style Error: Image Styles must use the base attribute {item_attr}")
            if not temp_data[item_attr]:
                raise Failed(f"Image Style Error: {item_attr} attribute is empty")
            if not isinstance(temp_data[item_attr], dict):
                raise Failed(f"Image Style Error: {item_attr} attribute must be a dictionary")
            self.library.image_styles[style_id] = temp_data[item_attr]
            if section_key and section_key in self.set_collections and "collections" in temp_data and temp_data["collections"]:
                for k, alts in self.set_collections[section_key].items():
                    if k in temp_data["collections"]:
                        self.library.collection_images[k] = temp_data["collections"][k]
                        if alts:
                            for alt in alts:
                                self.library.collection_images[alt] = temp_data["collections"][k]
        return self.library.image_styles[style_id]

    def get_collections(self, requested_collections):
        if requested_collections:
            return {c: self.collections[c] for c in util.get_list(requested_collections) if c in self.collections}
        else:
            return self.collections

    def edit_tags(self, attr, obj, group, alias, extra=None):
        if attr in alias and f"{attr}.sync" in alias:
            logger.error(f"{self.type_str} Error: Cannot use {attr} and {attr}.sync together")
        elif f"{attr}.remove" in alias and f"{attr}.sync" in alias:
            logger.error(f"{self.type_str} Error: Cannot use {attr}.remove and {attr}.sync together")
        elif attr in alias and not group[alias[attr]]:
            logger.warning(f"{self.type_str} Error: {attr} attribute is blank")
        elif f"{attr}.remove" in alias and not group[alias[f"{attr}.remove"]]:
            logger.warning(f"{self.type_str} Error: {attr}.remove attribute is blank")
        elif f"{attr}.sync" in alias and not group[alias[f"{attr}.sync"]]:
            logger.warning(f"{self.type_str} Error: {attr}.sync attribute is blank")
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
        logger.separator(f"Running {self.type_str}")
        logger.info("")
        next_year = datetime.now().year + 1
        for mapping_name, meta in self.metadata.items():
            try:
                methods = {mm.lower(): mm for mm in meta}

                logger.info("")
                logger.separator(f"{mapping_name} {self.type_str}")

                if "template" in methods:
                    logger.debug("")
                    logger.separator(f"Building Definition From Templates", space=False, border=False)
                    logger.debug("")
                    named_templates = []
                    for original_variables in util.get_list(meta[methods["template"]], split=False):
                        if not isinstance(original_variables, dict):
                            raise Failed(f"{self.type_str} Error: template attribute is not a dictionary")
                        elif "name" not in original_variables:
                            raise Failed(f"{self.type_str} Error: template sub-attribute name is required")
                        elif not original_variables["name"]:
                            raise Failed(f"{self.type_str} Error: template sub-attribute name cannot be blank")
                        named_templates.append(original_variables["name"])
                    logger.debug(f"Templates Called: {', '.join(named_templates)}")
                    new_variables = {}
                    if "variables" in methods:
                        logger.debug("")
                        logger.debug("Validating Method: variables")
                        if not isinstance(meta[methods["variables"]], dict):
                            raise Failed(f"{self.type_str} Error: variables must be a dictionary (key: value pairs)")
                        logger.trace(meta[methods["variables"]])
                        new_variables = meta[methods["variables"]]
                    name = meta[methods["name"]] if "name" in methods else None
                    new_attributes = self.apply_template(name, mapping_name, meta, meta[methods["template"]], new_variables)
                    for attr in new_attributes:
                        if attr.lower() not in methods:
                            meta[attr] = new_attributes[attr]
                            methods[attr.lower()] = attr

                if "run_definition" in methods:
                    logger.debug("")
                    logger.debug("Validating Method: run_definition")
                    if meta[methods["run_definition"]] is None:
                        raise NotScheduled("Skipped because run_definition has no value")
                    logger.debug(f"Value: {meta[methods['run_definition']]}")
                    valid_options = ["true", "false"] + plex.library_types
                    for library_type in util.get_list(meta[methods["run_definition"]], lower=True):
                        if library_type not in valid_options:
                            raise Failed(f"{self.type_str} Error: {library_type} is invalid. Options: true, false, {', '.join(plex.library_types)}")
                        elif library_type == "false":
                            raise NotScheduled(f"Skipped because run_definition is false")
                        elif library_type != "true" and self.library and library_type != self.library.Plex.type:
                            raise NotScheduled(f"Skipped because run_definition library_type: {library_type} doesn't match")

                match_data = None
                match_methods = {}
                if "match" in methods:
                    logger.debug("")
                    logger.debug("Validating Method: match")
                    match_data = meta[methods["match"]]
                    match_methods = {mm.lower(): mm for mm in match_data}

                mapping_id = None
                item = []
                if ("mapping_id" in match_methods or "mapping_id" in methods) and not self.library.is_music:
                    logger.debug("")
                    logger.debug("Validating Method: mapping_id")
                    value = match_data[match_methods["mapping_id"]] if "mapping_id" in match_methods else meta[methods["mapping_id"]]
                    if not value:
                        raise Failed(f"{self.type_str} Error: mapping_id attribute is blank")
                    logger.debug(f"Value: {value}")
                    mapping_id = value

                if mapping_id is None and (isinstance(mapping_name, int) or mapping_name.startswith("tt")) and not self.library.is_music:
                    mapping_id = mapping_name

                if mapping_id is not None:
                    if str(mapping_id).startswith("tt"):
                        id_type = "IMDb"
                    else:
                        id_type = "TMDb" if self.library.is_movie else "TVDb"
                    logger.info("")
                    logger.info(f"{id_type} ID Mapping: {mapping_id}")
                    if self.library.is_movie and mapping_id in self.library.movie_map:
                        item.extend([self.library.fetch_item(i) for i in self.library.movie_map[mapping_id]])
                    elif self.library.is_show and mapping_id in self.library.show_map:
                        item.extend([self.library.fetch_item(i) for i in self.library.show_map[mapping_id]])
                    elif mapping_id in self.library.imdb_map:
                        item.extend([self.library.fetch_item(i) for i in self.library.imdb_map[mapping_id]])
                    else:
                        logger.error(f"{self.type_str} Error: {id_type} ID not mapped")
                        continue

                blank_edition = False
                edition_titles = []
                edition_contains = []
                if self.library.is_movie:
                    if "blank_edition" in match_methods or "blank_edition" in methods:
                        logger.debug("")
                        logger.debug("Validating Method: blank_edition")
                        value = match_data[match_methods["blank_edition"]] if "blank_edition" in match_methods else meta[methods["blank_edition"]]
                        logger.debug(f"Value: {value}")
                        blank_edition = util.parse(self.type_str, "blank_edition", value, datatype="bool", default=False)
                    if "edition" in match_methods or "edition_filter" in methods:
                        logger.debug("")
                        logger.debug("Validating Method: edition_filter")
                        value = match_data[match_methods["edition"]] if "edition" in match_methods else meta[methods["edition_filter"]]
                        logger.debug(f"Value: {value}")
                        edition_titles = util.parse(self.type_str, "edition", value, datatype="strlist")
                    if "edition_contains" in match_methods or "edition_contains" in methods:
                        logger.debug("")
                        logger.debug("Validating Method: edition_contains")
                        value = match_data[match_methods["edition_contains"]] if "edition_contains" in match_methods else meta[methods["edition_contains"]]
                        logger.debug(f"Value: {value}")
                        edition_contains = util.parse(self.type_str, "edition_contains", value, datatype="strlist")

                if not item:
                    titles = []
                    if "title" in match_methods:
                        logger.debug("")
                        logger.debug("Validating Method: title")
                        value = match_data[match_methods["title"]]
                        if not value:
                            raise Failed(f"{self.type_str} Error: title attribute is blank")
                        titles.extend(util.parse(self.type_str, "title", value, datatype="strlist"))

                    if not titles:
                        titles.append(str(mapping_name))

                    if "alt_title" in methods:
                        logger.debug("")
                        logger.debug("Validating Method: alt_title")
                        value = meta[methods["alt_title"]]
                        if not value:
                            raise Failed(f"{self.type_str} Error: alt_title attribute is blank")
                        titles.append(value)

                    year = None
                    if "year" in match_methods or "year" in methods:
                        logger.debug("")
                        logger.debug("Validating Method: year")
                        value = match_data[match_methods["year"]] if "year" in match_methods else meta[methods["year"]]
                        if not value:
                            raise Failed(f"{self.type_str} Error: year attribute is blank")
                        logger.debug(f"Value: {value}")
                        year = util.parse(self.type_str, "year", value, datatype="int", minimum=1800, maximum=next_year)

                    for title in titles:
                        temp_items = self.library.search_item(title, year=year)
                        item.extend(temp_items)

                    if not item:
                        logger.error(f"Skipping {mapping_name}: Item not found")
                        continue

                if not isinstance(item, list):
                    item = [item]
                if blank_edition or edition_titles or edition_contains:
                    new_item = []
                    logger.trace("")
                    logger.trace("Edition Filtering: ")
                    if not self.library.plex_pass:
                        logger.warning("Plex Warning: Plex Pass is required to use the Edition Field scanning filenames instead")
                    for i in item:
                        i = self.library.reload(i)
                        if self.library.plex_pass:
                            check = i.editionTitle if i.editionTitle else ""
                        else:
                            values = [loc for loc in i.locations if loc]
                            if not values:
                                raise Failed(f"Plex Error: No Filepaths found for {i.title}")
                            res = re.search(r'(?i)[\[{]edition-([^}\]]*)', values[0])
                            check = res.group(1) if res else ""
                        if blank_edition and not check:
                            logger.trace(f"  Found {i.title} with no Edition")
                            new_item.append(i)
                        elif edition_titles and check in edition_titles:
                            logger.trace(f"  Found {i.title} with Edition: {check}")
                            new_item.append(i)
                        else:
                            found = False
                            if edition_contains:
                                for ec in edition_contains:
                                    if ec in check:
                                        found = True
                                        logger.trace(f"  Found {i.title} with Edition: {check} containing {ec}")
                                        new_item.append(i)
                                        break
                            if not found:
                                if check:
                                    logger.trace(f"  {i.title} with Edition: {check} ignored")
                                else:
                                    logger.trace(f"  {i.title} with no Edition ignored")
                    item = new_item
                for i in item:
                    try:
                        logger.info("")
                        logger.separator(f"Updating {i.title}", space=False, border=False)
                        logger.info("")
                        self.update_metadata_item(i, mapping_name, meta, methods)
                    except Failed as e:
                        logger.error(e)
            except NotScheduled as e:
                logger.info(e)
            except Failed as e:
                logger.error(e)

    def update_metadata_item(self, item, mapping_name, meta, methods):

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
                            try:
                                final_value = util.validate_date(value, return_as="%Y-%m-%d")
                            except Failed as ei:
                                raise Failed(f"{self.type_str} Error: {name} {ei}")
                            current = current[:-9]
                        elif var_type == "float":
                            try:
                                value = float(str(value))
                                if 0 <= value <= 10:
                                    final_value = value
                            except ValueError:
                                pass
                            if final_value is None:
                                raise Failed(f"{self.type_str} Error: {name} attribute must be a number between 0 and 10")
                        elif var_type == "int":
                            try:
                                final_value = int(str(value))
                            except ValueError:
                                pass
                            if final_value is None:
                                raise Failed(f"{self.type_str} Error: {name} attribute must be an integer")
                        else:
                            final_value = value
                        if current != str(final_value):
                            if key == "title":
                                current_item.editTitle(final_value)
                            else:
                                current_item.editField(key, final_value)
                            logger.info(f"Metadata: {name} updated to {final_value}")
                            updated = True
                    except Failed as ee:
                        logger.error(ee)
                else:
                    logger.error(f"{self.type_str} Error: {name} attribute is blank")

        def finish_edit(current_item, description):
            nonlocal updated
            if updated:
                try:
                    logger.info(f"{description} Metadata Update Successful")
                except BadRequest:
                    logger.error(f"{description} Metadata Update Failed")

        tmdb_item = None
        tmdb_is_movie = None
        if not self.library.is_music and ("tmdb_show" in methods or "tmdb_id" in methods) and "tmdb_movie" in methods:
            logger.error(f"{self.type_str} Error: Cannot use tmdb_movie and tmdb_show when editing the same metadata item")

        if not self.library.is_music and "tmdb_show" in methods or "tmdb_id" in methods or "tmdb_movie" in methods:
            try:
                if "tmdb_show" in methods or "tmdb_id" in methods:
                    data = meta[methods["tmdb_show" if "tmdb_show" in methods else "tmdb_id"]]
                    if data is None:
                        logger.error(f"{self.type_str} Error: tmdb_show attribute is blank")
                    else:
                        tmdb_is_movie = False
                        tmdb_item = self.config.TMDb.get_show(util.regex_first_int(data, "Show"))
                elif "tmdb_movie" in methods:
                    if meta[methods["tmdb_movie"]] is None:
                        logger.error(f"{self.type_str} Error: tmdb_movie attribute is blank")
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

        add_edit("title", item, meta, methods)
        add_edit("sort_title", item, meta, methods, key="titleSort")
        if self.library.is_movie:
            if "edition" in methods and not self.library.plex_pass:
                logger.error("Plex Error: Plex Pass is Required to edit Edition")
            else:
                add_edit("edition", item, meta, methods, key="editionTitle")
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
            prefs = None
            for advance_edit in util.advance_tags_to_edit[self.library.type]:
                if advance_edit in methods:
                    if advance_edit in ["metadata_language", "use_original_title"] and self.library.agent not in plex.new_plex_agents:
                        logger.error(f"{self.type_str} Error: {advance_edit} attribute only works for with the New Plex Movie Agent and New Plex TV Agent")
                    elif meta[methods[advance_edit]]:
                        ad_key, options = plex.item_advance_keys[f"item_{advance_edit}"]
                        method_data = str(meta[methods[advance_edit]]).lower()
                        if prefs is None:
                            prefs = [p.id for p in item.preferences()]
                        if method_data not in options:
                            logger.error(f"{self.type_str} Error: {meta[methods[advance_edit]]} {advance_edit} attribute invalid")
                        elif ad_key in prefs and getattr(item, ad_key) != options[method_data]:
                            advance_edits[ad_key] = options[method_data]
                            logger.info(f"Metadata: {advance_edit} updated to {method_data}")
                    else:
                        logger.error(f"{self.type_str} Error: {advance_edit} attribute is blank")
            if advance_edits:
                if self.library.edit_advance(item, advance_edits):
                    updated = True
                    logger.info(f"{mapping_name} Advanced Metadata Update Successful")
                else:
                    logger.error(f"{mapping_name} Advanced Metadata Update Failed")

        style_data = None
        if "style_data" in methods:
            style_data = meta[methods["style_data"]]
            logger.trace(f"Style Data: {style_data}")

        asset_location, folder_name, ups = self.library.item_images(item, meta, methods, initial=True, asset_directory=self.asset_directory + self.library.asset_directory if self.asset_directory else None, style_data=style_data)
        if ups:
            updated = True
        if "f1_season" not in methods:
            logger.info(f"{self.library.type}: {mapping_name} Metadata Update {'Complete' if updated else 'Not Needed'}")

        update_seasons = self.update_seasons
        if "update_seasons" in methods and self.library.is_show:
            logger.debug("")
            logger.debug("Validating Method: update_seasons")
            if not meta[methods["update_seasons"]]:
                logger.warning(f"{self.type_str} Warning: update_seasons has no value and season updates will be performed")
            else:
                logger.debug(f"Value: {meta[methods['update_seasons']]}")
                for library_type in util.get_list(meta[methods["run_definition"]], lower=True):
                    if library_type not in ["true", "false"]:
                        raise Failed(f"{self.type_str} Error: {library_type} is invalid. Options: true or false")
                    elif library_type == "false":
                        update_seasons = False

        update_episodes = self.update_episodes
        if "update_episodes" in methods and self.library.is_show:
            logger.debug("")
            logger.debug("Validating Method: update_episodes")
            if not meta[methods["update_episodes"]]:
                logger.warning(f"{self.type_str} Warning: update_episodes has no value and episode updates will be performed")
            else:
                logger.debug(f"Value: {meta[methods['update_episodes']]}")
                for library_type in util.get_list(meta[methods["run_definition"]], lower=True):
                    if library_type not in ["true", "false"]:
                        raise Failed(f"{self.type_str} Error: {library_type} is invalid. Options: true or false")
                    elif library_type == "false":
                        update_episodes = False

        if "seasons" in methods and self.library.is_show and (update_seasons or update_episodes):
            if not meta[methods["seasons"]]:
                logger.error(f"{self.type_str} Error: seasons attribute is blank")
            elif not isinstance(meta[methods["seasons"]], dict):
                logger.error(f"{self.type_str} Error: seasons attribute must be a dictionary")
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
                        logger.error(f"{self.type_str} Error: Season: {season_id} not found")
                        continue
                    season_methods = {sm.lower(): sm for sm in season_dict}
                    season_style_data = None
                    if update_seasons:
                        add_edit("title", season, season_dict, season_methods)
                        add_edit("summary", season, season_dict, season_methods)
                        add_edit("user_rating", season, season_dict, season_methods, key="userRating", var_type="float")
                        if self.edit_tags("label", season, season_dict, season_methods):
                            updated = True
                        finish_edit(season, f"Season: {season_id}")
                        if style_data and "seasons" in style_data and style_data["seasons"] and season_id in style_data["seasons"]:
                            season_style_data = style_data["seasons"][season_id]
                        _, _, ups = self.library.item_images(season, season_dict, season_methods, asset_location=asset_location,
                                                             title=f"{item.title} Season {season.seasonNumber}",
                                                             image_name=f"Season{'0' if season.seasonNumber < 10 else ''}{season.seasonNumber}",
                                                             folder_name=folder_name, style_data=season_style_data)

                        advance_edits = {}
                        prefs = None
                        for advance_edit in util.advance_tags_to_edit["Season"]:
                            if advance_edit in season_methods:
                                if season_dict[season_methods[advance_edit]]:
                                    ad_key, options = plex.item_advance_keys[f"item_{advance_edit}"]
                                    method_data = str(season_dict[season_methods[advance_edit]]).lower()
                                    if prefs is None:
                                        prefs = [p.id for p in season.preferences()]
                                    if method_data not in options:
                                        logger.error(f"{self.type_str} Error: {meta[methods[advance_edit]]} {advance_edit} attribute invalid")
                                    elif ad_key in prefs and getattr(season, ad_key) != options[method_data]:
                                        advance_edits[ad_key] = options[method_data]
                                        logger.info(f"Metadata: {advance_edit} updated to {method_data}")
                                else:
                                    logger.error(f"{self.type_str} Error: {advance_edit} attribute is blank")
                        if advance_edits:
                            if self.library.edit_advance(season, advance_edits):
                                updated = True
                                logger.info("Advanced Metadata Update Successful")
                            else:
                                logger.error("Advanced Metadata Update Failed")
                        if ups:
                            updated = True
                        logger.info(f"Season {season_id} of {mapping_name} Metadata Update {'Complete' if updated else 'Not Needed'}")

                    if "episodes" in season_methods and update_episodes and self.library.is_show:
                        if not season_dict[season_methods["episodes"]]:
                            logger.error(f"{self.type_str} Error: episodes attribute is blank")
                        elif not isinstance(season_dict[season_methods["episodes"]], dict):
                            logger.error(f"{self.type_str} Error: episodes attribute must be a dictionary")
                        else:
                            episodes = {}
                            for episode in season.episodes():
                                episodes[episode.title] = episode
                                if episode.index:
                                    episodes[int(episode.index)] = episode
                                elif episode.originallyAvailableAt:
                                    available = episode.originallyAvailableAt
                                    episodes[f"{available.month:02}/{available.day:02}"] = episode
                                    episodes[f"{available.month}/{available.day}"] = episode
                                    episodes[f"{available.month:02}-{available.day:02}"] = episode
                                    episodes[f"{available.month}-{available.day}"] = episode
                            for episode_id, episode_dict in season_dict[season_methods["episodes"]].items():
                                updated = False
                                logger.info("")
                                logger.info(f"Updating episode {episode_id} in {season_id} of {mapping_name}...")
                                if episode_id in episodes:
                                    episode = episodes[episode_id]
                                else:
                                    logger.error(f"{self.type_str} Error: Episode {episode_id} in Season {season_id} not found")
                                    continue
                                episode_methods = {em.lower(): em for em in episode_dict}
                                add_edit("title", episode, episode_dict, episode_methods)
                                add_edit("sort_title", episode, episode_dict, episode_methods, key="titleSort")
                                add_edit("content_rating", episode, episode_dict, episode_methods, key="contentRating")
                                add_edit("critic_rating", episode, episode_dict, episode_methods, key="rating", var_type="float")
                                add_edit("audience_rating", episode, episode_dict, episode_methods, key="audienceRating", var_type="float")
                                add_edit("user_rating", episode, episode_dict, episode_methods, key="userRating", var_type="float")
                                add_edit("originally_available", episode, episode_dict, episode_methods, key="originallyAvailableAt", var_type="date")
                                add_edit("summary", episode, episode_dict, episode_methods)
                                for tag_edit in ["director", "writer", "label"]:
                                    if self.edit_tags(tag_edit, episode, episode_dict, episode_methods):
                                        updated = True
                                finish_edit(episode, f"Episode: {episode_id} in Season: {season_id}")
                                episode_style_data = None
                                if season_style_data and "episodes" in season_style_data and season_style_data["episodes"] and episode_id in season_style_data["episodes"]:
                                    episode_style_data = season_style_data["episodes"][episode_id]
                                _, _, ups = self.library.item_images(episode, episode_dict, episode_methods, asset_location=asset_location,
                                                                     title=f"{item.title} {episode.seasonEpisode.upper()}",
                                                                     image_name=episode.seasonEpisode.upper(), folder_name=folder_name,
                                                                     style_data=episode_style_data)
                                if ups:
                                    updated = True
                                logger.info(f"Episode {episode_id} in Season {season_id} of {mapping_name} Metadata Update {'Complete' if updated else 'Not Needed'}")

        if "episodes" in methods and update_episodes and self.library.is_show:
            if not meta[methods["episodes"]]:
                logger.error(f"{self.type_str} Error: episodes attribute is blank")
            elif not isinstance(meta[methods["episodes"]], dict):
                logger.error(f"{self.type_str} Error: episodes attribute must be a dictionary")
            else:
                for episode_str, episode_dict in meta[methods["episodes"]].items():
                    updated = False
                    logger.info("")
                    match = re.search("[Ss]\\d+[Ee]\\d+", episode_str)
                    if not match:
                        logger.error(f"{self.type_str} Error: episode {episode_str} invalid must have S##E## format")
                        continue
                    output = match.group(0)[1:].split("E" if "E" in match.group(0) else "e")
                    season_id = int(output[0])
                    episode_id = int(output[1])
                    logger.info(f"Updating episode S{season_id}E{episode_id} of {mapping_name}...")
                    try:
                        episode = item.episode(season=season_id, episode=episode_id)
                    except NotFound:
                        logger.error(f"{self.type_str} Error: episode {episode_id} of season {season_id} not found")
                        continue
                    episode_methods = {em.lower(): em for em in episode_dict}
                    add_edit("title", episode, episode_dict, episode_methods)
                    add_edit("sort_title", episode, episode_dict, episode_methods, key="titleSort")
                    add_edit("content_rating", episode, episode_dict, episode_methods, key="contentRating")
                    add_edit("critic_rating", episode, episode_dict, episode_methods, key="rating", var_type="float")
                    add_edit("audience_rating", episode, episode_dict, episode_methods, key="audienceRating", var_type="float")
                    add_edit("user_rating", episode, episode_dict, episode_methods, key="userRating", var_type="float")
                    add_edit("originally_available", episode, episode_dict, episode_methods, key="originallyAvailableAt", var_type="date")
                    add_edit("summary", episode, episode_dict, episode_methods)
                    for tag_edit in ["director", "writer", "label"]:
                        if self.edit_tags(tag_edit, episode, episode_dict, episode_methods):
                            updated = True
                    finish_edit(episode, f"Episode: {episode_str} in Season: {season_id}")
                    _, _, ups = self.library.item_images(episode, episode_dict, episode_methods, asset_location=asset_location,
                                                         title=f"{item.title} {episode.seasonEpisode.upper()}",
                                                         image_name=episode.seasonEpisode.upper(), folder_name=folder_name)
                    if ups:
                        updated = True
                    logger.info(f"Episode S{season_id}E{episode_id} of {mapping_name} Metadata Update {'Complete' if updated else 'Not Needed'}")

        if "albums" in methods and self.library.is_music:
            if not meta[methods["albums"]]:
                logger.error(f"{self.type_str} Error: albums attribute is blank")
            elif not isinstance(meta[methods["albums"]], dict):
                logger.error(f"{self.type_str} Error: albums attribute must be a dictionary")
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
                        logger.error(f"{self.type_str} Error: Album: {album_name} not found")
                        continue
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
                    if not title:
                        title = album.title
                    finish_edit(album, f"Album: {title}")
                    _, _, ups = self.library.item_images(album, album_dict, album_methods, asset_location=asset_location,
                                                         title=f"{item.title} Album {album.title}", image_name=album.title, folder_name=folder_name)
                    if ups:
                        updated = True
                    logger.info(f"Album: {title} of {mapping_name} Metadata Update {'Complete' if updated else 'Not Needed'}")

                    if "tracks" in album_methods:
                        if not album_dict[album_methods["tracks"]]:
                            logger.error(f"{self.type_str} Error: tracks attribute is blank")
                        elif not isinstance(album_dict[album_methods["tracks"]], dict):
                            logger.error(f"{self.type_str} Error: tracks attribute must be a dictionary")
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
                                    logger.error(f"{self.type_str} Error: Track: {track_num} not found")
                                    continue

                                add_edit("title", track, track_dict, track_methods, value=title)
                                add_edit("user_rating", track, track_dict, track_methods, key="userRating", var_type="float")
                                add_edit("track", track, track_dict, track_methods, key="index", var_type="int")
                                add_edit("disc", track, track_dict, track_methods, key="parentIndex", var_type="int")
                                add_edit("original_artist", track, track_dict, track_methods, key="originalTitle")
                                for tag_edit in ["mood", "collection", "label"]:
                                    if self.edit_tags(tag_edit, track, track_dict, track_methods):
                                        updated = True
                                if not title:
                                    title = track.title
                                finish_edit(track, f"Track: {title}")
                                logger.info(f"Track: {track_num} on Album: {title} of {mapping_name} Metadata Update {'Complete' if updated else 'Not Needed'}")

        if "f1_season" in methods and self.library.is_show:
            f1_season = None
            current_year = datetime.now().year
            if meta[methods["f1_season"]] is None:
                raise Failed(f"{self.type_str} Error: f1_season attribute is blank")
            try:
                year_value = int(str(meta[methods["f1_season"]]))
                if 1950 <= year_value <= current_year:
                    f1_season = year_value
            except ValueError:
                pass
            if f1_season is None:
                raise Failed(f"{self.type_str} Error: f1_season attribute must be an integer between 1950 and {current_year}")
            round_prefix = False
            if "round_prefix" in methods:
                if meta[methods["round_prefix"]] is True:
                    round_prefix = True
                else:
                    logger.error(f"{self.type_str} Error: round_prefix must be true to do anything")
            shorten_gp = False
            if "shorten_gp" in methods:
                if meta[methods["shorten_gp"]] is True:
                    shorten_gp = True
                else:
                    logger.error(f"{self.type_str} Error: shorten_gp must be true to do anything")
            f1_language = None
            if "f1_language" in methods:
                if str(meta[methods["f1_language"]]).lower() in ergast.translations:
                    f1_language = str(meta[methods["f1_language"]]).lower()
                else:
                    logger.error(f"{self.type_str} Error: f1_language must be a language code Kometa has a translation for. Options: {ergast.translations}")
            logger.info(f"Setting {item.title} of {self.type_str} to F1 Season {f1_season}")
            races = self.config.Ergast.get_races(f1_season, f1_language)
            race_lookup = {r.round: r for r in races}
            logger.trace(race_lookup)
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
                    add_edit("title", season, value=title)
                    finish_edit(season, f"Season: {title}")
                    _, _, ups = self.library.item_images(season, {}, {}, asset_location=asset_location, title=title,
                                                         image_name=f"Season{'0' if season.seasonNumber < 10 else ''}{season.seasonNumber}", folder_name=folder_name)
                    if ups:
                        updated = True
                    logger.info(f"Race {season.seasonNumber} of F1 Season {f1_season}: Metadata Update {'Complete' if updated else 'Not Needed'}")
                    for episode in season.episodes():
                        if len(episode.locations) > 0:
                            ep_title, session_date = race.session_info(episode.locations[0], sprint_weekend)
                            add_edit("title", episode, value=ep_title)
                            add_edit("originally_available", episode, key="originallyAvailableAt", var_type="date", value=session_date)
                            finish_edit(episode, f"Season: {season.seasonNumber} Episode: {episode.episodeNumber}")
                            _, _, ups = self.library.item_images(episode, {}, {}, asset_location=asset_location, title=ep_title,
                                                                 image_name=episode.seasonEpisode.upper(), folder_name=folder_name)
                            if ups:
                                updated = True
                            logger.info(f"Session {episode.title}: Metadata Update {'Complete' if updated else 'Not Needed'}")
                else:
                    logger.warning(f"Ergast Error: No Round: {season.seasonNumber} for Season {f1_season}")

class PlaylistFile(DataFile):
    def __init__(self, config, file_type, path, temp_vars, asset_directory):
        super().__init__(config, file_type, path, temp_vars, asset_directory, "Playlist File")
        self.data_type = "Playlist"
        data = self.load_file(self.type, self.path)
        self.playlists = get_dict("playlists", data, self.config.playlist_names)
        self.templates = get_dict("templates", data)
        self.external_templates(data)
        if not self.playlists:
            raise Failed("YAML Error: playlists attribute is required")
        logger.info("Playlist File Loaded Successfully")

class OverlayFile(DataFile):
    def __init__(self, config, library, file_type, path, temp_vars, asset_directory, queue_current):
        self.file_num = len(library.overlay_files)
        super().__init__(config, file_type, path, temp_vars, asset_directory, f"Overlay File {self.file_num}")
        self.library = library
        self.data_type = "Overlay"
        data = self.load_file(self.type, self.path, overlay=True)
        self.overlays = get_dict("overlays", data)
        self.templates = get_dict("templates", data)
        queues = get_dict("queues", data)
        self.queues = {}
        self.queue_names = {}
        position = temp_vars["position"] if "position" in temp_vars and temp_vars["position"] else None
        overlay_limit = util.parse("Config", "overlay_limit", temp_vars["overlay_limit"], datatype="int", default=0, minimum=0) if "overlay_limit" in temp_vars else None
        for queue_name, queue in queues.items():
            queue_position = temp_vars[f"position_{queue_name}"] if f"position_{queue_name}" in temp_vars and temp_vars[f"position_{queue_name}"] else position
            initial_queue = None
            defaults = {"horizontal_align": None, "vertical_align": None, "horizontal_offset": None, "vertical_offset": None}
            if isinstance(queue, dict) and "default" in queue and queue["default"] and isinstance(queue["default"], dict):
                for k, v in queue["default"].items():
                    if k == "position":
                        if not queue_position:
                            queue_position = v
                    elif k == "overlay_limit":
                        if overlay_limit is None:
                            overlay_limit = util.parse("Config", "overlay_limit", v, datatype="int", default=0, minimum=0)
                    elif k == "conditionals":
                        if not v:
                            raise Failed(f"Queue Error: default sub-attribute conditionals is blank")
                        if not isinstance(v, dict):
                            raise Failed(f"Queue Error: default sub-attribute conditionals is not a dictionary")
                        for con_key, con_value in v.items():
                            if not isinstance(con_value, dict):
                                raise Failed(f"Queue Error: conditional {con_key} is not a dictionary")
                            if "default" not in con_value:
                                raise Failed(f"Queue Error: default sub-attribute required for conditional {con_key}")
                            if "conditions" not in con_value:
                                raise Failed(f"Queue Error: conditions sub-attribute required for conditional {con_key}")
                            conditions = con_value["conditions"]
                            if isinstance(conditions, dict):
                                conditions = [conditions]
                            if not isinstance(conditions, list):
                                raise Failed(f"{self.data_type} Error: conditions sub-attribute must be a list or dictionary")
                            condition_found = False
                            for i, condition in enumerate(conditions, 1):
                                if not isinstance(condition, dict):
                                    raise Failed(f"{self.data_type} Error: each condition must be a dictionary")
                                if "value" not in condition:
                                    raise Failed(f"{self.data_type} Error: each condition must have a result value")
                                condition_passed = True
                                for var_key, var_value in condition.items():
                                    if var_key == "value":
                                        continue
                                    if var_key.endswith(".exists"):
                                        var_value = util.parse(self.data_type, var_key, var_value, datatype="bool", default=False)
                                        if (not var_value and var_key[:-7] in temp_vars and temp_vars[var_key[:-7]]) or (var_value and (var_key[:-7] not in temp_vars or not temp_vars[var_key[:-7]])):
                                            logger.debug(f"Condition {i} Failed: {var_key}: {'true does not exist' if var_value else 'false exists'}")
                                            condition_passed = False
                                    elif var_key.endswith(".not"):
                                        if (isinstance(var_value, list) and temp_vars[var_key] in var_value) or \
                                                (not isinstance(var_value, list) and str(temp_vars[var_key]) == str(var_value)):
                                            if isinstance(var_value, list):
                                                logger.debug(f'Condition {i} Failed: {var_key} "{temp_vars[var_key]}" in {var_value}')
                                            else:
                                                logger.debug(f'Condition {i} Failed: {var_key} "{temp_vars[var_key]}" is "{var_value}"')
                                            condition_passed = False
                                    elif var_key in temp_vars:
                                        if (isinstance(var_value, list) and temp_vars[var_key] not in var_value) or \
                                                (not isinstance(var_value, list) and str(temp_vars[var_key]) != str(var_value)):
                                            if isinstance(var_value, list):
                                                logger.debug(f'Condition {i} Failed: {var_key} "{temp_vars[var_key]}" not in {var_value}')
                                            else:
                                                logger.debug(f'Condition {i} Failed: {var_key} "{temp_vars[var_key]}" is not "{var_value}"')
                                            condition_passed = False
                                    else:
                                        logger.debug(f"Condition {i} Failed: {var_key} is not a variable provided or a default variable")
                                        condition_passed = False
                                    if condition_passed is False:
                                        break
                                if condition_passed:
                                    condition_found = True
                                    defaults[con_key] = condition["value"]
                                    break
                            if not condition_found:
                                defaults[con_key] = con_value["default"]
                    else:
                        defaults[k] = v
            if queue_position and isinstance(queue_position, list):
                initial_queue = queue_position
            elif isinstance(queue, list):
                initial_queue = queue
            elif isinstance(queue, dict):
                if queue_position:
                    pos_str = str(queue_position)
                    for x in range(4):
                        dict_to_use = temp_vars if x < 2 else defaults
                        for k, v in dict_to_use.items():
                            if f"<<{k}>>" in pos_str:
                                pos_str = pos_str.replace(f"<<{k}>>", str(v))
                    if pos_str in queue:
                        initial_queue = queue[pos_str]
                if not initial_queue:
                    initial_queue = next((v for k, v in queue.items() if k != "default"), None)
            if not isinstance(initial_queue, list):
                raise Failed(f"Config Error: queue {queue_name} must be a list")
            final_queue = []
            for pos in initial_queue:
                if not pos:
                    pos = {}
                defaults["horizontal_align"] = pos["horizontal_align"] if "horizontal_align" in pos else defaults["horizontal_align"]
                defaults["vertical_align"] = pos["vertical_align"] if "vertical_align" in pos else defaults["vertical_align"]
                defaults["horizontal_offset"] = pos["horizontal_offset"] if "horizontal_offset" in pos else defaults["horizontal_offset"]
                defaults["vertical_offset"] = pos["vertical_offset"] if "vertical_offset" in pos else defaults["vertical_offset"]
                new_pos = {
                    "horizontal_align": defaults["horizontal_align"], "vertical_align": defaults["vertical_align"],
                    "horizontal_offset": defaults["horizontal_offset"], "vertical_offset": defaults["vertical_offset"]
                }
                for pk, pv in new_pos.items():
                    if pv is None:
                        raise Failed(f"Config Error: queue missing {pv} attribute")
                final_queue.append(util.parse_cords(new_pos, f"{queue_name} queue", required=True))
                if overlay_limit and len(final_queue) >= overlay_limit:
                    break
            self.queues[queue_current] = final_queue
            self.queue_names[queue_name] = queue_current
            queue_current += 1
        self.external_templates(data, overlay=True)
        if not self.overlays:
            raise Failed("YAML Error: overlays attribute is required")
        logger.info(f"Overlay File Loaded Successfully")
