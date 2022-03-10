import operator, os, re
from datetime import datetime
from modules import plex, util
from modules.util import Failed, ImageData
from plexapi.exceptions import NotFound
from tmdbapis import NotFound as TMDbNotFound
from ruamel import yaml

logger = util.logger

github_base = "https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Configs/master/"

all_auto = ["genre"]
ms_auto = ["actor", "year", "original_language", "tmdb_popular_people", "trakt_user_lists", "trakt_liked_lists", "trakt_people_list"]
auto = {
    "Movie": ["tmdb_collection", "decade", "country", "director", "producer", "writer"] + all_auto + ms_auto,
    "Show": ["network"] + all_auto + ms_auto,
    "Artist": ["mood", "style", "country"] + all_auto,
    "Video": ["country"] + all_auto
}
default_templates = {
    "actor": {"tmdb_person": f"<<actor>>", "plex_search": {"all": {"actor": "tmdb"}}},
    "director": {"tmdb_person": f"<<director>>", "plex_search": {"all": {"director": "tmdb"}}},
    "producer": {"tmdb_person": f"<<producer>>", "plex_search": {"all": {"producer": "tmdb"}}},
    "writer": {"tmdb_person": f"<<writer>>", "plex_search": {"all": {"writer": "tmdb"}}},
    "original_language": {"plex_all": True, "filters": {"original_language": "<<original_language>>"}},
    "tmdb_collection": {"tmdb_collection_details": "<<tmdb_collection>>"},
    "trakt_user_lists": {"trakt_list_details": "<<trakt_user_lists>>"},
    "trakt_liked_lists": {"trakt_list_details": "<<trakt_liked_lists>>"},
    "tmdb_popular_people": {"tmdb_person": f"<<tmdb_popular_people>>", "plex_search": {"all": {"actor": "tmdb"}}},
    "trakt_people_list": {"tmdb_person": f"<<trakt_people_list>>", "plex_search": {"all": {"actor": "tmdb"}}}
}

def get_dict(attribute, attr_data, check_list=None):
    if check_list is None:
        check_list = []
    if attr_data and attribute in attr_data:
        if attr_data[attribute]:
            if isinstance(attr_data[attribute], dict):
                new_dict = {}
                for _name, _data in attr_data[attribute].items():
                    if _name in check_list:
                        logger.warning(f"Config Warning: Skipping duplicate {attribute[:-1] if attribute[-1] == 's' else attribute}: {_name}")
                    elif _data is None:
                        logger.warning(f"Config Warning: {attribute[:-1] if attribute[-1] == 's' else attribute}: {_name} has no data")
                    elif not isinstance(_data, dict):
                        logger.warning(f"Config Warning: {attribute[:-1] if attribute[-1] == 's' else attribute}: {_name} must be a dictionary")
                    else:
                        new_dict[str(_name)] = _data
                return new_dict
            else:
                logger.error(f"Config Error: {attribute} must be a dictionary")
        else:
            logger.error(f"Config Error: {attribute} attribute is blank")
    return {}


class DataFile:
    def __init__(self, config, file_type, path):
        self.config = config
        self.type = file_type
        self.path = path
        self.data_type = ""
        self.templates = {}

    def get_file_name(self):
        data = f"{github_base}{self.path}.yml" if self.type == "GIT" else self.path
        if "/" in data:
            return data[data.rfind("/") + 1:-4]
        elif "\\" in data:
            return data[data.rfind("\\") + 1:-4]
        else:
            return data

    def load_file(self):
        try:
            if self.type in ["URL", "Git", "Repo"]:
                if self.type == "Repo" and not self.config.custom_repo:
                    raise Failed("Config Error: No custom_repo defined")
                content_path = self.path if self.type == "URL" else f"{self.config.custom_repo if self.type == 'Repo' else github_base}{self.path}.yml"
                response = self.config.get(content_path)
                if response.status_code >= 400:
                    raise Failed(f"URL Error: No file found at {content_path}")
                content = response.content
            elif os.path.exists(os.path.abspath(self.path)):
                content = open(self.path, encoding="utf-8")
            else:
                raise Failed(f"File Error: File does not exist {os.path.abspath(self.path)}")
            data, _, _ = yaml.util.load_yaml_guess_indent(content)
            return data
        except yaml.scanner.ScannerError as ye:
            raise Failed(f"YAML Error: {util.tab_new_lines(ye)}")
        except Exception as e:
            logger.stacktrace()
            raise Failed(f"YAML Error: {e}")

    def apply_template(self, name, data, template_call):
        if not self.templates:
            raise Failed(f"{self.data_type} Error: No templates found")
        elif not template_call:
            raise Failed(f"{self.data_type} Error: template attribute is blank")
        else:
            logger.debug(f"Value: {template_call}")
            for variables in util.get_list(template_call, split=False):
                if not isinstance(variables, dict):
                    raise Failed(f"{self.data_type} Error: template attribute is not a dictionary")
                elif "name" not in variables:
                    raise Failed(f"{self.data_type} Error: template sub-attribute name is required")
                elif not variables["name"]:
                    raise Failed(f"{self.data_type} Error: template sub-attribute name is blank")
                elif variables["name"] not in self.templates:
                    raise Failed(f"{self.data_type} Error: template {variables['name']} not found")
                elif not isinstance(self.templates[variables["name"]], dict):
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

                    if self.data_type == "Collection" and "collection_name" not in variables:
                        variables["collection_name"] = str(name)
                    if self.data_type == "Playlist" and "playlist_name" not in variables:
                        variables["playlist_name"] = str(name)

                    template_name = variables["name"]
                    template = self.templates[template_name]

                    default = {}
                    if "default" in template:
                        if template["default"]:
                            if isinstance(template["default"], dict):
                                for dv in template["default"]:
                                    if str(dv) not in optional:
                                        if template["default"][dv] is not None:
                                            final_value = str(template["default"][dv])
                                            if "<<collection_name>>" in final_value:
                                                final_value = final_value.replace("<<collection_name>>", str(name))
                                            if "<<playlist_name>>" in final_value:
                                                final_value = final_value.replace("<<playlist_name>>", str(name))
                                            default[dv] = final_value
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
                                else:
                                    logger.warning(f"Template Warning: variable {op} cannot be optional if it has a default")
                        else:
                            raise Failed(f"{self.data_type} Error: template sub-attribute optional is blank")

                    if "move_prefix" in template or "move_collection_prefix" in template:
                        prefix = None
                        if "move_prefix" in template:
                            prefix = template["move_prefix"]
                        elif "move_collection_prefix" in template:
                            logger.warning(f"{self.data_type} Error: template sub-attribute move_collection_prefix will run as move_prefix")
                            prefix = template["move_collection_prefix"]
                        if prefix:
                            for op in util.get_list(prefix):
                                variables["collection_name"] = variables["collection_name"].replace(f"{str(op).strip()} ", "") + f", {str(op).strip()}"
                        else:
                            raise Failed(f"{self.data_type} Error: template sub-attribute move_prefix is blank")

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

                    new_attributes = {}
                    for method_name, attr_data in template.items():
                        if method_name not in data and method_name not in ["default", "optional", "move_collection_prefix", "move_prefix"]:
                            if attr_data is None:
                                logger.error(f"Template Error: template attribute {method_name} is blank")
                                continue
                            try:
                                new_attributes[method_name] = check_data(method_name, attr_data)
                            except Failed:
                                continue
                    return new_attributes


class MetadataFile(DataFile):
    def __init__(self, config, library, file_type, path):
        super().__init__(config, file_type, path)
        self.data_type = "Collection"
        self.library = library
        if file_type == "Data":
            self.metadata = None
            self.collections = get_dict("collections", path, library.collections)
            self.templates = get_dict("templates", path)
        else:
            logger.info("")
            logger.info(f"Loading Metadata {file_type}: {path}")
            logger.info("")
            data = self.load_file()
            self.metadata = get_dict("metadata", data, library.metadata_files)
            self.templates = get_dict("templates", data)
            self.collections = get_dict("collections", data, library.collections)
            self.dynamic_collections = get_dict("dynamic_collections", data)
            col_names = library.collections + [c for c in self.collections]
            all_items = None
            if self.dynamic_collections:
                logger.info("")
                logger.separator(f"Dynamic Collections")
                logger.info("")
            for map_name, dynamic in self.dynamic_collections.items():
                try:
                    methods = {dm.lower(): dm for dm in dynamic}
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
                        exclude = util.parse("Config", "exclude", dynamic, parent=map_name, methods=methods, datatype="list") if "exclude" in methods else []
                        include = util.parse("Config", "include", dynamic, parent=map_name, methods=methods, datatype="list") if "include" in methods else []
                        if exclude and include:
                            raise Failed(f"Config Error: {map_name} cannot have both include and exclude attributes")
                        addons = util.parse("Config", "addons", dynamic, parent=map_name, methods=methods, datatype="dictlist") if "addons" in methods else {}
                        for k, v in addons.items():
                            if k in v:
                                logger.warning(f"Config Warning: {k} cannot be an addon for itself")
                            exclude.extend([vv for vv in v if vv != k])
                        default_title_format = "<<title>>"
                        default_template = None
                        auto_list = {}
                        dynamic_data = None
                        def _check_dict(check_dict):
                            for ck, cv in check_dict.items():
                                if ck not in exclude and cv not in exclude:
                                    auto_list[ck] = cv
                        if auto_type in ["genre", "mood", "style", "country", "network", "year", "decade"]:
                            auto_list = {i.title: i.title for i in library.get_tags(auto_type) if i.title not in exclude}
                            if library.is_music:
                                default_template = {"smart_filter": {"limit": 50, "sort_by": "plays.desc", "any": {f"artist_{auto_type}": f"<<{auto_type}>>"}}}
                                default_title_format = "Most Played <<title>> <<library_type>>s"
                            else:
                                default_template = {"smart_filter": {"limit": 50, "sort_by": "critic_rating.desc", "any": {auto_type: f"<<{auto_type}>>"}}}
                                default_title_format = "Best <<library_type>>s of <<title>>" if auto_type in ["year", "decade"] else "Top <<title>> <<library_type>>s"
                        elif auto_type == "tmdb_collection":
                            if not all_items:
                                all_items = library.get_all()
                            for i, item in enumerate(all_items, 1):
                                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                                tmdb_id, tvdb_id, imdb_id = library.get_ids(item)
                                tmdb_item = config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=True)
                                if tmdb_item and tmdb_item.collection and tmdb_item.collection.id not in exclude and tmdb_item.collection.name not in exclude:
                                    auto_list[tmdb_item.collection.id] = tmdb_item.collection.name
                            logger.exorcise()
                        elif auto_type == "original_language":
                            if not all_items:
                                all_items = library.get_all()
                            for i, item in enumerate(all_items, 1):
                                logger.ghost(f"Processing: {i}/{len(all_items)} {item.title}")
                                tmdb_id, tvdb_id, imdb_id = library.get_ids(item)
                                tmdb_item = config.TMDb.get_item(item, tmdb_id, tvdb_id, imdb_id, is_movie=library.type == "Movie")
                                if tmdb_item and tmdb_item.original_language  and tmdb_item.original_language.iso_639_1  not in exclude and tmdb_item.original_language.english_name not in exclude:
                                    auto_list[tmdb_item.original_language.iso_639_1] = tmdb_item.original_language.english_name
                            logger.exorcise()
                            default_title_format = "<<title>> <<library_type>>s"
                        elif auto_type in ["actor", "director", "writer", "producer"]:
                            people = {}
                            if "data" in methods:
                                dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="dict")
                            else:
                                raise Failed(f"Config Error: {map_name} data attribute not found")
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
                            if not person_minimum and not person_limit:
                                person_minimum = 3
                            if not all_items:
                                all_items = library.get_all()
                            for i, item in enumerate(all_items, 1):
                                try:
                                    self.library.reload(item)
                                    for person in getattr(item, f"{auto_type}s")[:person_depth]:
                                        if person.id not in people:
                                            people[person.id] = {"name": person.tag, "count": 0}
                                        people[person.id]["count"] += 1
                                except Failed as e:
                                    logger.error(f"Plex Error: {e}")
                            roles = [data for _, data in people.items()]
                            roles.sort(key=operator.itemgetter('count'), reverse=True)
                            person_count = 0
                            for role in roles:
                                if (person_limit and person_count >= person_limit) or (person_minimum and role["count"] < person_minimum):
                                    break
                                if role["name"] not in exclude:
                                    try:
                                        results = self.config.TMDb.search_people(role["name"])
                                        if results[0].id not in exclude:
                                            auto_list[results[0].id] = results[0].name
                                            person_count += 1
                                    except TMDbNotFound:
                                        logger.error(f"TMDb Error: Actor {role['name']} Not Found")
                        elif auto_type == "trakt_user_lists":
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="list")
                            for option in dynamic_data:
                                _check_dict(self.config.Trakt.get_user_lists(option))
                        elif auto_type == "trakt_liked_lists":
                            _check_dict(self.config.Trakt.get_liked_lists())
                        elif auto_type == "tmdb_popular_people":
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="int", minimum=1)
                            _check_dict(self.config.TMDb.get_popular_people(dynamic_data))
                        elif auto_type == "trakt_people_list":
                            dynamic_data = util.parse("Config", "data", dynamic, parent=map_name, methods=methods, datatype="list")
                            for option in dynamic_data:
                                _check_dict(self.config.Trakt.get_people(option))
                        else:
                            raise Failed(f"Config Error: {map_name} type attribute {dynamic[methods['type']]} invalid")
                    title_format = default_title_format
                    if "title_format" in methods:
                        title_format = util.parse("Config", "title_format", dynamic, parent=map_name, methods=methods, default=default_title_format)
                    if "<<title>>" not in title_format:
                        logger.error(f"Config Error: <<title>> not in title_format: {title_format} using default: {default_title_format}")
                        title_format = default_title_format
                    post_format_override = util.parse("Config", "post_format_override", dynamic, parent=map_name, methods=methods, datatype="dict") if "post_format_override" in methods else {}
                    pre_format_override = util.parse("Config", "pre_format_override", dynamic, parent=map_name, methods=methods, datatype="dict") if "pre_format_override" in methods else {}
                    test = util.parse("Config", "test", dynamic, parent=map_name, methods=methods, default=False, datatype="bool") if "test" in methods else False
                    sync = util.parse("Config", "sync", dynamic, parent=map_name, methods=methods, default=False, datatype="bool") if "sync" in methods else False
                    if "<<library_type>>" in title_format:
                        title_format = title_format.replace("<<library_type>>", library.type)
                    template_variables = util.parse("Config", "template_variables", dynamic, parent=map_name, methods=methods, datatype="dictdict") if "template_variables" in methods else {}
                    if "template" in methods:
                        template_name = util.parse("Config", "template", dynamic, parent=map_name, methods=methods)
                        if template_name not in self.templates:
                            raise Failed(f"Config Error: {map_name} template: {template_name} not found")
                        if f"<<{auto_type}>>" not in str(self.templates[template_name]):
                            raise Failed(f"Config Error: {map_name} template: {template_name} is required to have the template variable <<{auto_type}>>")
                    else:
                        self.templates[map_name] = default_template if default_template else default_templates[auto_type]
                        template_name = map_name
                    remove_prefix = util.parse("Config", "remove_prefix", dynamic, parent=map_name, methods=methods, datatype="commalist") if "remove_prefix" in methods else []
                    remove_suffix = util.parse("Config", "remove_suffix", dynamic, parent=map_name, methods=methods, datatype="commalist") if "remove_suffix" in methods else []
                    sync = {i.title: i for i in self.library.search(libtype="collection", label=str(map_name))} if sync else {}
                    other_name = util.parse("Config", "other_name", dynamic, parent=map_name, methods=methods) if "other_name" in methods and include else None
                    other_keys = []
                    logger.debug(f"Mapping Name: {map_name}")
                    logger.debug(f"Type: {auto_type}")
                    logger.debug(f"Data: {dynamic_data}")
                    logger.debug(f"Exclude: {exclude}")
                    logger.debug(f"Addons: {addons}")
                    logger.debug(f"Template: {template_name}")
                    logger.debug(f"Template Variables: {template_variables}")
                    logger.debug(f"Remove Prefix: {remove_prefix}")
                    logger.debug(f"Remove Suffix: {remove_suffix}")
                    logger.debug(f"Title Format: {title_format}")
                    logger.debug(f"Pre Format Override: {pre_format_override}")
                    logger.debug(f"Post Format Override: {post_format_override}")
                    logger.debug(f"Test: {test}")
                    logger.debug(f"Sync: {sync}")
                    logger.debug(f"Include: {include}")
                    logger.debug(f"Other Name: {other_name}")
                    logger.debug(f"Keys (Title)")
                    for key, value in auto_list.items():
                        logger.debug(f"  - {key}{'' if key == value else f' ({value})'}")

                    for key, value in auto_list.items():
                        if include and key not in include:
                            if key not in exclude:
                                other_keys.append(key)
                            continue
                        template_call = {"name": template_name, auto_type: [key] + addons[key] if key in addons else key}
                        for k, v in template_variables.items():
                            if key in v:
                                template_call[k] = v[key]
                        if key in post_format_override:
                            collection_title = post_format_override[key]
                        else:
                            if key in pre_format_override:
                                value = pre_format_override[key]
                            else:
                                for prefix in remove_prefix:
                                    if value.startswith(prefix):
                                        value = value[len(prefix):].strip()
                                for suffix in remove_suffix:
                                    if value.endswith(suffix):
                                        value = value[:-len(suffix)].strip()
                            collection_title = title_format.replace("<<title>>", value)
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
                        col = {"template": {"name": template_name, auto_type: other_keys}, "label": str(map_name)}
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
        elif attr in alias and group[alias[attr]] is None:
            logger.error(f"Metadata Error: {attr} attribute is blank")
        elif f"{attr}.remove" in alias and group[alias[f"{attr}.remove"]] is None:
            logger.error(f"Metadata Error: {attr}.remove attribute is blank")
        elif f"{attr}.sync" in alias and group[alias[f"{attr}.sync"]] is None:
            logger.error(f"Metadata Error: {attr}.sync attribute is blank")
        elif attr in alias or f"{attr}.remove" in alias or f"{attr}.sync" in alias:
            add_tags = util.get_list(group[alias[attr]]) if attr in alias else []
            if extra:
                add_tags.extend(extra)
            remove_tags = util.get_list(group[alias[f"{attr}.remove"]]) if f"{attr}.remove" in alias else None
            sync_tags = util.get_list(group[alias[f"{attr}.sync"]] if group[alias[f"{attr}.sync"]] else []) if f"{attr}.sync" in alias else None
            return self.library.edit_tags(attr, obj, add_tags=add_tags, remove_tags=remove_tags, sync_tags=sync_tags)
        return False

    def set_images(self, obj, group, alias):

        def set_image(attr, is_poster=True, is_url=True):
            if group[alias[attr]]:
                return ImageData(attr, group[alias[attr]], is_poster=is_poster, is_url=is_url)
            else:
                logger.error(f"Metadata Error: {attr} attribute is blank")

        poster = None
        background = None
        if "url_poster" in alias:
            poster = set_image("url_poster")
        elif "file_poster" in alias:
            poster = set_image("file_poster", is_url=False)
        if "url_background" in alias:
            background = set_image("url_background", is_poster=False)
        elif "file_background" in alias:
            background = set_image("file_background",is_poster=False, is_url=False)

        if poster or background:
            self.library.upload_images(obj, poster=poster, background=background)

    def update_metadata(self):
        if not self.metadata:
            return None
        logger.info("")
        logger.separator("Running Metadata")
        logger.info("")
        for mapping_name, meta in self.metadata.items():
            methods = {mm.lower(): mm for mm in meta}

            updated = False
            edits = {}

            def add_edit(name, current_item, group, alias, key=None, value=None, var_type="str"):
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
                                edits[f"{key}.value"] = final_value
                                edits[f"{key}.locked"] = 1
                                logger.info(f"Detail: {name} updated to {final_value}")
                        except Failed as ee:
                            logger.error(ee)
                    else:
                        logger.error(f"Metadata Error: {name} attribute is blank")

            logger.info("")
            logger.separator()
            logger.info("")
            year = None
            if "year" in methods and not self.library.is_music:
                next_year = datetime.now().year + 1
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
                    alt_title = meta["alt_title"]
                    item = self.library.search_item(alt_title, year=year)
                    if item is None:
                        item = self.library.search_item(alt_title)

            if item is None:
                logger.error(f"Plex Error: Item {mapping_name} not found")
                logger.error(f"Skipping {mapping_name}")
                continue

            logger.info(f"Updating {self.library.type}: {title}...")

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
                if tmdb_is_movie and tmdb_item.original_title != tmdb_item.title:
                    original_title = tmdb_item.original_title
                elif not tmdb_is_movie and tmdb_item.original_name != tmdb_item.name:
                    original_title = tmdb_item.original_name
                rating = tmdb_item.vote_average
                if tmdb_is_movie and tmdb_item.companies:
                    studio = tmdb_item.companies[0].name
                elif not tmdb_is_movie and tmdb_item.networks:
                    studio = tmdb_item.networks[0].name
                tagline = tmdb_item.tagline if len(tmdb_item.tagline) > 0 else None
                summary = tmdb_item.overview
                genres = [genre.name for genre in tmdb_item.genres]

            edits = {}
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
            if self.library.edit_item(item, mapping_name, self.library.type, edits):
                updated = True

            advance_edits = {}
            prefs = [p.id for p in item.preferences()]
            for advance_edit in util.advance_tags_to_edit[self.library.type]:
                if advance_edit in methods:
                    if advance_edit in ["metadata_language", "use_original_title"] and self.library.agent not in plex.new_plex_agents:
                        logger.error(f"Metadata Error: {advance_edit} attribute only works for with the New Plex Movie Agent and New Plex TV Agent")
                    elif meta[methods[advance_edit]]:
                        key, options = plex.item_advance_keys[f"item_{advance_edit}"]
                        method_data = str(meta[methods[advance_edit]]).lower()
                        if method_data not in options:
                            logger.error(f"Metadata Error: {meta[methods[advance_edit]]} {advance_edit} attribute invalid")
                        elif key in prefs and getattr(item, key) != options[method_data]:
                            advance_edits[key] = options[method_data]
                            logger.info(f"Detail: {advance_edit} updated to {method_data}")
                    else:
                        logger.error(f"Metadata Error: {advance_edit} attribute is blank")
            if self.library.edit_item(item, mapping_name, self.library.type, advance_edits, advanced=True):
                updated = True

            for tag_edit in util.tags_to_edit[self.library.type]:
                if self.edit_tags(tag_edit, item, meta, methods, extra=genres if tag_edit == "genre" else None):
                    updated = True

            logger.info(f"{self.library.type}: {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")

            self.set_images(item, meta, methods)

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
                        edits = {}
                        add_edit("title", season, season_dict, season_methods)
                        add_edit("summary", season, season_dict, season_methods)
                        add_edit("user_rating", season, season_dict, season_methods, key="userRating", var_type="float")
                        if self.library.edit_item(season, season_id, "Season", edits):
                            updated = True
                        self.set_images(season, season_dict, season_methods)
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
                                    edits = {}
                                    add_edit("title", episode, episode_dict, episode_methods)
                                    add_edit("sort_title", episode, episode_dict, episode_methods, key="titleSort")
                                    add_edit("critic_rating", episode, episode_dict, episode_methods, key="rating", var_type="float")
                                    add_edit("audience_rating", episode, episode_dict, episode_methods, key="audienceRating", var_type="float")
                                    add_edit("user_rating", episode, episode_dict, episode_methods, key="userRating", var_type="float")
                                    add_edit("originally_available", episode, episode_dict, episode_methods, key="originallyAvailableAt", var_type="date")
                                    add_edit("summary", episode, episode_dict, episode_methods)
                                    if self.library.edit_item(episode, f"{episode_str} in Season: {season_id}", "Episode", edits):
                                        updated = True
                                    for tag_edit in ["director", "writer"]:
                                        if self.edit_tags(tag_edit, episode, episode_dict, episode_methods):
                                            updated = True
                                    self.set_images(episode, episode_dict, episode_methods)
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
                        edits = {}
                        add_edit("title", episode, episode_dict, episode_methods)
                        add_edit("sort_title", episode, episode_dict, episode_methods, key="titleSort")
                        add_edit("critic_rating", episode, episode_dict, episode_methods, key="rating", var_type="float")
                        add_edit("audience_rating", episode, episode_dict, episode_methods, key="audienceRating", var_type="float")
                        add_edit("user_rating", episode, episode_dict, episode_methods, key="userRating", var_type="float")
                        add_edit("originally_available", episode, episode_dict, episode_methods, key="originallyAvailableAt", var_type="date")
                        add_edit("summary", episode, episode_dict, episode_methods)
                        if self.library.edit_item(episode, f"{season_id} Episode: {episode_id}", "Season", edits):
                            updated = True
                        for tag_edit in ["director", "writer"]:
                            if self.edit_tags(tag_edit, episode, episode_dict, episode_methods):
                                updated = True
                        self.set_images(episode, episode_dict, episode_methods)
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
                        edits = {}
                        add_edit("title", album, album_dict, album_methods, value=title)
                        add_edit("sort_title", album, album_dict, album_methods, key="titleSort")
                        add_edit("critic_rating", album, album_dict, album_methods, key="rating", var_type="float")
                        add_edit("user_rating", album, album_dict, album_methods, key="userRating", var_type="float")
                        add_edit("originally_available", album, album_dict, album_methods, key="originallyAvailableAt", var_type="date")
                        add_edit("record_label", album, album_dict, album_methods, key="studio")
                        add_edit("summary", album, album_dict, album_methods)
                        if self.library.edit_item(album, title, "Album", edits):
                            updated = True
                        for tag_edit in ["genre", "style", "mood", "collection", "label"]:
                            if self.edit_tags(tag_edit, album, album_dict, album_methods):
                                updated = True
                        self.set_images(album, album_dict, album_methods)
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
                                    edits = {}
                                    add_edit("title", track, track_dict, track_methods, value=title)
                                    add_edit("user_rating", track, track_dict, track_methods, key="userRating", var_type="float")
                                    add_edit("track", track, track_dict, track_methods, key="index", var_type="int")
                                    add_edit("disc", track, track_dict, track_methods, key="parentIndex", var_type="int")
                                    add_edit("original_artist", track, track_dict, track_methods, key="originalTitle")
                                    if self.library.edit_item(track, title, "Track", edits):
                                        updated = True
                                    if self.edit_tags("mood", track, track_dict, track_methods):
                                        updated = True
                                    logger.info(f"Track: {track_num} on Album: {title} of {mapping_name} Details Update {'Complete' if updated else 'Not Needed'}")


class PlaylistFile(DataFile):
    def __init__(self, config, file_type, path):
        super().__init__(config, file_type, path)
        self.data_type = "Playlist"
        self.playlists = {}
        logger.info("")
        logger.info(f"Loading Playlist File {file_type}: {path}")
        data = self.load_file()
        self.playlists = get_dict("playlists", data, self.config.playlist_names)
        self.templates = get_dict("templates", data)
        if not self.playlists:
            raise Failed("YAML Error: playlists attribute is required")
        logger.info(f"Playlist File Loaded Successfully")
