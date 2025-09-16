import base64
import hashlib
import os
import re as _re
import time
import urllib.parse
from xml.etree.ElementTree import Element

import requests
from plexapi.collection import Collection
from plexapi.video import Show, Movie, Episode, Season

from modules import util
from modules.logs import ERROR
from modules.util import Failed

logger = util.logger

# import emby_client
import unicodedata
# from emby_client.rest import ApiException

# bugs: razzie + berlinale year no poster

# todo: add person link to collection with type while doing the edits / summary ?

## Helpful URLS for dev:
# https://swagger.emby.media/?staticview=true#/
# https://github.com/MediaBrowser/Emby/wiki
# https://dev.emby.media/doc/restapi/Browsing-the-Library.html
# https://docs.mdblist.com/docs/api

# New class (in developent) for replacing fake Palex objects
class EmbyItem:
    def __init__(self, base_item):
        pass

    def update_item_info(self, update_date):
        pass


class PlexMedia:
    def __init__(self, name, server_id, item_id, runtime_ticks, provider_ids, media_type, image_tags,
                 backdrop_image_tags):
        self.name = name
        self.title = name
        self.server_id = server_id
        self.ratingKey = item_id
        self.runtime_ticks = runtime_ticks
        self.provider_ids = provider_ids
        self.media_type = media_type
        self.image_tags = image_tags
        self.backdrop_image_tags = backdrop_image_tags
        # self.guid =
        # self.smart = True # needed

    def __repr__(self):
        return self


class Movie(Movie):
    def __init__(self, data):
        xml_data = self._dict_to_xml(data)
        super().__init__(None, xml_data)
        self._loadData(xml_data)

    @staticmethod
    def _dict_to_xml(data_dict):
        element = Element('Video')
        for key, value in data_dict.items():
            if value is not None:
                element.set(key, str(value))
        if 'agent' not in data_dict or not data_dict['agent']:
            element.set('agent', 'com.plexapp.agents.imdb')  # Oder den entsprechenden Agenten

        return element

class FilterChoiceEmby:
    def __init__(self, key, title, thumb=None):
        self.key = key
        self.title = title
        self.thumb = thumb


class Show(Show):
    def __init__(self, data):
        xml_data = self._dict_to_xml(data)
        super().__init__(None, xml_data)
        self._loadData(xml_data)


    @staticmethod
    def _dict_to_xml(data_dict):
        element = Element('Directory')
        for key, value in data_dict.items():
            if value is not None:
                element.set(key, str(value))
        if 'agent' not in data_dict or not data_dict['agent']:
            element.set('agent', 'com.plexapp.agents.thetvdb')  # Oder den entsprechenden Agenten

        return element


class Season(Season):
    def __init__(self, data):
        xml_data = self._dict_to_xml(data)
        super().__init__(None, xml_data)
        self._loadData(xml_data)

    def show(self):
        pass

    @staticmethod
    def _dict_to_xml(data_dict):
        element = Element('Directory')
        for key, value in data_dict.items():
            if value is not None:
                element.set(key, str(value))
        if 'agent' not in data_dict or not data_dict['agent']:
            element.set('agent', 'com.plexapp.agents.thetvdb')  # Oder den entsprechenden Agenten

        return element


class Episode(Episode):
    def __init__(self, data):
        xml_data = self._dict_to_xml(data)
        super().__init__(None, xml_data)
        self._loadData(xml_data)

    @staticmethod
    def _dict_to_xml(data_dict):
        element = Element('Video')
        for key, value in data_dict.items():
            if value is not None:
                element.set(key, str(value))
        return element


class Collection(Collection):
    # music => string error
    def __init__(self, data):
        xml_data = self._dict_to_xml(data)
        super().__init__(None, xml_data)
        self._items = []  # cache for self.items
        self._loadData(xml_data)
        self.childCount = 0

    def __len__(self):  # pragma: no cover
        return len(self.items())

    def items(self):
        """ Returns a list of all items in the collection. """
        return self._items

    @staticmethod
    def _dict_to_xml(data_dict):
        element = Element('Directory')
        for key, value in data_dict.items():
            if value is not None:
                element.set(key, str(value))
        return element

    def items(self):
        """ Returns a list of all items in the collection. """
        return self._items



class Audio:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return self._dict_to_xml(self.data)

    @staticmethod
    def _dict_to_xml(data_dict):
        element = Element('Audio')
        for key, value in data_dict.items():
            if value is not None:
                element.set(key, str(value))
        return element

class Person(Movie):
    def __init__(self, data):
        xml_data = self._dict_to_xml(data)
        super().__init__(xml_data)
        self._loadData(xml_data)

    @staticmethod
    def _dict_to_xml(data_dict):
        element = Element('Person')
        for key, value in data_dict.items():
            if value is not None:
                element.set(key, str(value))
        if 'agent' not in data_dict or not data_dict['agent']:
            element.set('agent', 'com.plexapp.agents.imdb')  # Oder den entsprechenden Agenten

        return element


class EmbyConfig:
    X_EMBY_CONTAINER_SIZE = 50  # Definiere die Standardgröße für die Anzahl der Elemente


class EmbyServer:

    #ToDo: use the ProvideId field for saving item rating instead of overwriting custom rating field
    def __init__(self, server_url, user_id, api_key, config, library_name = None):

        # ToDo: Merge the cache
        self._person_already_demoted = []
        self._items_cache: dict[str, dict] = {}
        self._items_cache_fields: dict[str, set[str]] = {}
        self._items_cache_ts: dict[str, float] = {}
        # anpassbar von außen: self.items_cache_ttl = 0 deaktiviert das Altern (immer frisch)
        self.items_cache_ttl: int = 300
        self.cached_person_names = []
        self._person_name_cache = {}
        self._bulk_person_cache = {}
        self.people_index = {}
        self.platformVersion = "" # - undefined??
        self._person_dupe_redirect_last = {}
        self._person_dupes_last = {}
        self._person_dupes_choice_last = {}
        self._http_session = requests.Session()
        self.cached_tmdb_ids = {}
        self.config = config
        self._roman_name_cache = {}  # key: tmdb_person_id(str) -> latin_name(str)|None
        self.people_cache = {}
        self._image_hash_cache = {}
        self.people_lib_cache = {}
        self.item_cache: dict[int, dict] = {}
        self.dirty_items: set[int] = set()   # statt Liste        self.people_lib_cache = {}
        self.emby_genres = None
        self.cached_plex_objects = {}
        self.all_tags = None
        self.cached_runtime = {}
        self.cached_locations = {}
        self.cached_people = {}
        self.cached_studios = {}
        self.cached_provider_ids={}
        self.file_names = {}

        self.studio_list =None
        self.media_by_resolution = {}
        self.production_countries = None
        self._person_name_fix_cache = set()

        self.production_search = {}
        self.emby_server_url = server_url
        self.user_id = user_id
        self.api_key = api_key
        self.headers = {"X-MediaBrowser-Token": api_key}
        # To prevent too long URLs, queries are done in batches of n
        self.api_batch_size = 50
        self.seconds_between_requests = 0.05
        # get system info to see if it works
        self.system_info = self.get_system_info()
        self.friendlyName = self.system_info.get("ServerName", "")
        self.version = self.system_info.get("Version", "")
        self.platform = self.system_info.get("OperatingSystemDisplayName", "")
        self.session = requests.Session()
        self.year_cache = {}
        self.library_id = None

        if library_name:
            for s in self.get_libraries():
                if s["Name"] == library_name:
                    self.library_id = s['Id']
                    # print(s)
                    break

        # configuration = emby_client.Configuration()
        # configuration.api_key['api_key'] = self.api_key
        # configuration.host = self.emby_server_url
        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # configuration.api_key_prefix['api_key'] = 'Bearer'

        # create an instance of the API class
        # client = emby_client.ApiClient(configuration)
        # activity_log_service = emby_client.ActivityLogServiceApi(client)
        # activity_log_service.
        # my_test = emby_client.api.user_library_service_api
        # pass
        # self.cache_filenames()

        # Configure API key authorization: apikeyauth
        # configuration = emby_client.Configuration()
        # configuration.api_key['api_key'] = api_key

        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # configuration.api_key_prefix['api_key'] = 'Bearer'

        # create an instance of the API class
        # client = emby_client.ApiClient(configuration)

    # -------------------------------------------------------------
    # Nutzt DEINE bestehende get_people() – nichts Neues erfunden.
    # Fügt nur die fehlenden Bausteine zusammen & integriert library_id.
    # -------------------------------------------------------------

    def _normalize_person(self, p: dict) -> dict:
        # Vergleichsrelevante Felder; PrimaryImageTag etc. ignorieren
        out = {
            "Id": str(p.get("Id")) if p.get("Id") is not None else None,
            "Name": p.get("Name"),
            "Type": p.get("Type"),
        }
        if p.get("Type") == "Actor" and p.get("Role"):
            out["Role"] = p["Role"]
        return out

    def _lists_equal_ordered(self, a: list[dict], b: list[dict]) -> bool:
        # Order-sensitiver Vergleich
        if len(a) != len(b):
            return False
        for x, y in zip(a, b):
            if self._normalize_person(x) != self._normalize_person(y):
                return False
        return True

    def _resolve_person_fast(self, people_index, role: str, provider: str, tmdb_id, person_name: str):
        """
        Verwendet NUR den vorgewärmten Index (keine HTTP-Calls).
        Rückgabe: (emby_id, linked_bool)
        - linked_bool True, wenn wir im Person-Objekt eine fehlende ProviderId ergänzen mussten
          (nur intern markiert; hier KEIN Update-POST – das machst du weiterhin wo du willst).
        """
        prov = (provider or "Tmdb")
        tmdb_id_str = str(tmdb_id)
        buckets = people_index.get(role) or {}
        by_tmdb = buckets.get("by_tmdb", {})
        by_name = buckets.get("by_name", {})

        # 1) TMDb-Treffer?
        if tmdb_id_str in by_tmdb:
            person = by_tmdb[tmdb_id_str]
            return person.get("Id"), False

        # 2) Name-Treffer?
        name_l = (person_name or "").strip().lower()
        person = by_name.get(name_l)
        if person and person.get("Id"):
            # ProviderIds lokal „ergänzen“ (kein Netz-Call hier)
            prov_ids = person.get("ProviderIds") or {}
            if (prov not in prov_ids) or (str(prov_ids.get(prov)) != tmdb_id_str):
                prov_ids[prov] = tmdb_id_str
                person["ProviderIds"] = prov_ids
                # In-Index auch per tmdb map auffindbar machen
                by_tmdb[tmdb_id_str] = person
                return person["Id"], True
            return person["Id"], False

        # 3) Nichts gefunden
        return None, False

    def _pkey(self, p: dict):
        """Eindeutiger Schlüssel je Person/Typ für Vergleich."""
        return (str(p.get("Id")) if p.get("Id") is not None else None, p.get("Type"))

    def _pname(self, p: dict):
        """Anzeigeformat Name (inkl. Rolle bei Actors)."""
        t = p.get("Type")
        n = p.get("Name") or "?"
        if t == "Actor" and p.get("Role"):
            return f"{n} (Actor: {p['Role']})"
        return f"{n} ({t})" if t else n

    def summarize_people_changes(self, current_people: list[dict], desired_people: list[dict],
                                 reorder_preview_max: int = 6) -> str:
        """Schöner Klartext-Diff für Cast & Crew (inkl. Order-Check)."""
        cur_map = {self._pkey(p): p for p in current_people if p.get("Id") and p.get("Type")}
        des_map = {self._pkey(p): p for p in desired_people if p.get("Id") and p.get("Type")}

        # Adds & Removes
        added_keys = [k for k in des_map.keys() if k not in cur_map]
        removed_keys = [k for k in cur_map.keys() if k not in des_map]

        added = [self._pname(des_map[k]) for k in added_keys]
        removed = [self._pname(cur_map[k]) for k in removed_keys]

        # Updates (Name/Role)
        updates = []
        for k in set(cur_map.keys()).intersection(des_map.keys()):
            cur = cur_map[k];
            des = des_map[k]
            if (cur.get("Name") or "") != (des.get("Name") or ""):
                updates.append(f"Name: {cur.get('Name') or '?'} → {des.get('Name') or '?'} ({des.get('Type')})")
            if des.get("Type") == "Actor":
                cur_role = cur.get("Role") or ""
                des_role = des.get("Role") or ""
                if cur_role != des_role:
                    person = des.get("Name") or cur.get("Name") or "?"
                    updates.append(f"Role: {person}: {cur_role or '—'} → {des_role or '—'}")

        # Reorder nur wenn keine Adds/Removes
        reordered_list = []
        if not added_keys and not removed_keys:
            cur_order = [self._pkey(p) for p in current_people if self._pkey(p) in des_map]
            des_order = [self._pkey(p) for p in desired_people if self._pkey(p) in cur_map]
            if cur_order != des_order:
                des_index = {k: i for i, k in enumerate(des_order)}
                moved = [k for i, k in enumerate(cur_order) if des_index.get(k) is not None and des_index[k] != i]
                names = [self._pname(des_map[k]) for k in moved]
                if len(names) > reorder_preview_max:
                    names = names[:reorder_preview_max] + [f"… +{len(moved) - reorder_preview_max} more"]
                reordered_list = names

        parts = []
        if added:
            parts.append("+ " + ", ".join(added))
        if removed:
            parts.append("- " + ", ".join(removed))
        if updates:
            parts.append("~ " + "; ".join(updates))
        if reordered_list:
            parts.append("↔ Reordered: " + ", ".join(reordered_list))

        return " | ".join(parts) if parts else "no changes"


    def get_years(self, library_id: str):
        endpoint = f"/emby/Years?Recursive=True&ParentId={library_id}&api_key={self.api_key}"
        url = self.emby_server_url + endpoint
        response = requests.get(url, headers=self.headers)
        return response.json().get("Items", [])

    def get_official_age_ratings(self, library_id: str):
        endpoint = f"/emby/OfficialRatings?Recursive=True&ParentId={library_id}&api_key={self.api_key}"
        url = self.emby_server_url + endpoint
        response = requests.get(url, headers=self.headers)
        return response.json().get("Items", [])


    def get_resolutions(self):
        """
        Fetches years for all items in the database and caches the results.
        """
        if not self.file_names:
            return []
        # MinWidth
        # MinHeight

        my_resolutions = {
            "4k": "(?i)2160|4k",
            "1080p": "(?i)1080|2k",
            "720p": "(?i)720|hd",
            "576p": "(?i)576",
            "480p": "(?i)480|sd",
            # HDR
            "hdr": r"(?i)\bHDR10\b",  # HDR

            "plus": r'(?i)\bhdr10(\+|p(lus)?\b)',  # HDR10+
            "dvhdr": r'(?i)\bdv(.hdr10?\b)',  # DV HDR10
            "dvhdrplus": r'(?i)\bdv.HDR10(\+|P(lus)?\b)',  # DV HDR10+
        }

        all_choices = []
        found_matches = []

        # self.media_by_resolution = {}
        # Durchsuche die filenames nach Auflösungen und Editionen
        for file_key, file_name in self.file_names.items():
            from modules import util
            logger = util.logger
            # logger.info(f"file name: {file_name}")
            # Suche nach Auflösungen
            for resolution_key, resolution_regex in my_resolutions.items():
                match = _re.search(resolution_regex, file_name)
                if match:
                    found_regex = match.group(0)
                    if resolution_key not in self.media_by_resolution:
                        self.media_by_resolution[resolution_key] = [file_key]
                    else:
                        self.media_by_resolution[resolution_key].append(file_key)
                    if found_regex not in found_matches:
                        filter_choice = FilterChoiceEmby(key=found_regex, title=resolution_key)
                        all_choices.append(filter_choice)
                        found_matches.append(found_regex)

            # Suche nach Editionen

        return all_choices

    def cache_filenames(self, imported_items):
        if not imported_items:
            return

        for item in imported_items:
            # item_media_sources = item.get('MediaSources')
            # item_media_path = item.get('Path')
            self.file_names[item.get('Id')] = os.path.basename(item.get('Path'))

            self.cached_studios[item.get('Id')] = item.get('Studios')
            self.cached_people[item.get('Id')] = item.get('People')
            self.cached_locations[item.get('Id')] = item.get('ProductionLocations')  # Meet english
            self.cached_runtime[item.get('Id')] = item.get('RunTimeTicks')
            self.cached_provider_ids[item.get('Id')] = item.get('ProviderIds')

        return
        if not self.library_id:
            return
        if self.file_names is None:
            endpoint = f"{self.emby_server_url}/emby/Items"
            params = {
                "Recursive": "true",
                "IncludeItemTypes": "Movie,Series,Episodes",
                "ParentId": self.library_id,
                "api_key": self.api_key,
                "Fields": "Budget,Chapters,DateCreated,Genres,HomePageUrl,IndexOptions,MediaStreams,Overview,ParentId,Path,People,ProviderIds,PrimaryImageAspectRatio,Revenue,SortName,Studios,Taglines"
            }
            try:
                response = requests.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                items = response.json().get("Items", [])

                for item in items:
                    # item_media_sources = item.get('MediaSources')
                    # item_media_path = item.get('Path')
                    self.file_names[item.get('Id')] = item.get('Path')
                    self.cached_studios[item.get('Id')] = item.get('Studios')
                    self.cached_people[item.get('Id')] = item.get('People')
                    self.cached_locations[item.get('Id')] = item.get('ProductionLocations') # Meet english
                    self.cached_runtime[item.get('Id')] = item.get('RunTimeTicks')
                    self.cached_provider_ids[item.get('Id')] = item.get('ProviderIds')
                    # if _re.search('1080', item_media_path):
                    #     print(the_search)
                    #     print(item_media_path)

                # Collect all IDs for batch year lookup
                # self.production_countries += [item["ProductionLocations"] for item in items if "ProductionLocations" in item]
                # for item in items:
                #     self.production_search[item.get('Id')] = item.get('ProductionLocations', [])
                # Flache die Liste ab und entferne Duplikate mit Set-Comprehension
                # unique_countries = {country for sublist in self.production_countries for country in sublist}

                # Konvertiere das Set zurück in eine (sortierte) Liste
                # self.production_countries = sorted(unique_countries)

                # print(f"Resolution cache populated with {len(self.production_countries)} entries.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch all resolutions: {e}")
            # self.production_countries = allcountries
            # return self.production_countries

    def get_emby_countries(self, library_id):
        """
        Fetches countries for all items in the database and caches the results.
        """
        if self.production_countries:
            return self.production_countries
        self.production_countries=[]
        endpoint = f"{self.emby_server_url}/emby/Items"
        params = {
            "Recursive": "true",
            "IncludeItemTypes": "Movie,Series,MusicArtist",
            "ParentId": library_id,
            "Fields": "ProductionLocations",
            "api_key": self.api_key
        }
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            items = response.json().get("Items", [])

            # Collect all IDs for batch year lookup
            self.production_countries += [item["ProductionLocations"] for item in items if "ProductionLocations" in item]
            for item in items:
                self.production_search[item.get('Id')] = item.get('ProductionLocations', [])
            # Flache die Liste ab und entferne Duplikate mit Set-Comprehension
            unique_countries = {country for sublist in self.production_countries for country in sublist}

            # Konvertiere das Set zurück in eine (sortierte) Liste
            self.production_countries = sorted(unique_countries)

            logger.info(f"Country cache populated with {len(self.production_countries)} entries.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch all countries: {e}")
        # self.production_countries = allcountries
        return self.production_countries

    def get_emby_genres(self, library_id):
        """
        Fetches years for all items in the database and caches the results.
        """
        if self.emby_genres:
            return self.emby_genres
        self.emby_genres=[]
        endpoint = f"{self.emby_server_url}/emby/Genres"
        params = {
            "Recursive": "true",
            # "IncludeItemTypes": "Movie,Series,MusicArtist",
            "ParentId": library_id,
            "api_key": self.api_key
        }
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            items = response.json().get("Items", [])

            # Collect all IDs for batch year lookup
            self.emby_genres += [item["Name"] for item in items if "Name" in item]

            # Konvertiere das Set zurück in eine (sortierte) Liste
            # self.emby_genres = sorted(production_countries)

            logger.info(f"Genre cache populated with {len(self.emby_genres)} entries.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch all genres: {e}")
        # self.production_countries = allcountries
        return self.emby_genres

    def get_system_info(self):
        endpoint = "/emby/System/Info"
        url = self.emby_server_url + endpoint
        try:
            response = requests.get(url, headers=self.headers)
            return response.json()
        except Exception as e:
            logger.error(
                f"Error occurred while getting Emby system info, check your configuration. Check your Emby url and port, user ID and API key: {e}"
            )
            raise SystemExit

    def get_users(self):
        user_list_endpoint = "/emby/Users"
        user_list_url = self.emby_server_url + user_list_endpoint
        user_list_response = requests.get(user_list_url, headers=self.headers)
        try:
            return user_list_response.json()
        except Exception as e:
            logger.error(f"Error occurred while getting users: {e}")
            return None

    def update_collection_display_order(self, collection_id, sort_order):
        # BUG: There's only one sorting field per item in Emby, while Plex suppoorts individual sortings by collection. So return, do nithing.
        # PremiereDate, SortName
        # c0e0098d2c574fbee1ee5505dc68f5bd
        return

        # sort order not settable in Emby other than item sort name
        emby_url_name = f"{self.emby_server_url}/emby/Users/{self.user_id}/Items/{collection_id}?api_key={self.api_key}"
        _name = requests.get(emby_url_name, headers=self.headers)
        response_name = requests.get(emby_url_name, headers=self.headers)
        response_name.raise_for_status()
        data_name = response_name.json()

    #added
    def get_actor_id(self, name):
        """
        Get the actor ID from Emby based on the actor's name.
        :param name: The name of the actor to search for.
        :return: The ID of the actor if found, else None.
        """
        # Define the search endpoint for Emby
        search_endpoint = f"/emby/Items"
        search_url = self.emby_server_url + search_endpoint

        # Search parameters for Emby
        params = {
            "SearchTerm": name,
            "IncludePeople": "true",
            "Recursive": "true"
        }

        try:
            # Perform the GET request to search for the actor
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()

            # Parse the response JSON
            search_results = response.json()
            for result in search_results.get('Items', []):
                # Check if the result is a person and matches the name
                if result.get("Type") == "Person" and result.get("Name") == name:
                    # print(f"get_actor_id: {name} - {result.get('Id')}")
                    # print(result.get("Id"))
                    return result.get("Id")

            # If no matching actor is found
            logger.info(f"Actor not found: {name}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while searching for actor: {e}")
            return None
    #added

    def findItems(self, cls=None, initpath=None, parent_id=None,builder_type=None, **kwargs):
        """
        Find and build all items from the Emby library that match specified criteria.

        Args:
            cls (optional): A class type to filter the items (e.g., Movie, Series, etc.).
            initpath (str, optional): The path to initialize the search from.
            **kwargs: Additional search attributes to filter items.

        Returns:
            list: List of items that match the specified search criteria.
        """
        # Initial path to begin search, if specified, otherwise search all items
        if parent_id:
            items = self.get_items(params={"ParentId": parent_id},include_item_types = [f"{builder_type.capitalize()}"] )
        else:
            # print(initpath)
            items = self.get_items()

        # If `cls` is specified, filter items by type (e.g., 'Movie', 'Series')
        if cls and hasattr(cls, 'TYPE'):
            items = [item for item in items if item.get('Type') == cls.TYPE]

        # Apply any additional filters specified in kwargs
        filtered_items = []
        for item in items:
            match = all(item.get(key, None) == value for key, value in kwargs.items())
            if match:
                filtered_items.append(item)


        return self.convert_emby_to_plex(filtered_items)
        # Build list of EmbyCollection instances



    def get_items_starting_with_sort_name(self, filter, limit=20):
        """
        Retrieves all movies and series whose SortName starts with the specified filter.
        Must be queried like this because it's not possible to search for SortName directly.

        Args:
            filter (str): The filter to match the SortName against.

        Returns:
            list: A list of items (movies and series) whose SortName starts with the filter.
        """
        limit = 50
        start_index = 0
        filtered_items = []
        found_sort_name = True

        while found_sort_name:

            items = self.get_items(
                fields=["SortName"],
                include_item_types=["Movie", "Series"],
                sort_by="SortName",
                limit=limit,
                start_index=start_index,
                getAll=False,
            )

            for item in items:
                if item["SortName"].startswith(filter):
                    filtered_items.append(item)
                else:
                    found_sort_name = False
                    break

            time.sleep(self.seconds_between_requests)
            start_index += limit

        return filtered_items

    def get_items_with_imdb_id(self, imdb_ids, item_types=None):
        batch_size = self.api_batch_size
        returned_items = []
        gotten_item_names = []

        if item_types is None:
            item_types = ["Movie", "Series"]
        else:
            item_types = [
                (
                    "Series"
                    if item_type.lower() in ["tv", "show"]
                    else "Movie" if item_type.lower() == "movie" else item_type
                )
                for item_type in item_types
            ]

        for i in range(0, len(imdb_ids), batch_size):
            batch_imdb_ids = imdb_ids[i : i + batch_size]
            # Remove any ids from batch_imdb_ids that are None
            batch_imdb_ids = [
                imdb_id for imdb_id in batch_imdb_ids if imdb_id is not None
            ]
            imdb_ids_str = ",".join(["imdb." + imdb_id for imdb_id in batch_imdb_ids])

            items = self.get_items(
                params={"AnyProviderIdEquals": imdb_ids_str},
                fields=["ChildCount", "RecursiveItemCount"],
                include_item_types=item_types,
                limit=batch_size,
            )

            for item in items:
                if item["Name"] not in gotten_item_names:
                    returned_items.append(item["Id"])
                    gotten_item_names.append(item["Name"])

        return returned_items

    # def get_items_with_tvdb_id(self, tvdb_ids, item_types=None):
    #     batch_size = self.api_batch_size
    #     returned_items = []
    #     gotten_item_names = []
    #
    #     if item_types is None:
    #         item_types = ["Movie", "Series", "Episode"]
    #     else:
    #         item_types = [
    #             (
    #                 "Series"
    #                 if item_type.lower() in ["tv", "show"]
    #                 else (
    #                     "Movie"
    #                     if item_type.lower() == "movie"
    #                     else "Episode" if item_type.lower() == "episode" else item_type
    #                 )
    #             )
    #             for item_type in item_types
    #         ]
    #
    #     for i in range(0, len(tvdb_ids), batch_size):
    #         batch_tvdb_ids = tvdb_ids[i : i + batch_size]
    #         tvdb_ids_str = ",".join(["tvdb." + tvdb_id for tvdb_id in batch_tvdb_ids])
    #
    #         items = self.get_items(
    #             params={"AnyProviderIdEquals": tvdb_ids_str},
    #             fields=["ChildCount", "RecursiveItemCount"],
    #             include_item_types=item_types,
    #             limit=batch_size,
    #         )
    #
    #         for item in items:
    #             if item["Name"] not in gotten_item_names:
    #                 returned_items.append(item["Id"])
    #                 gotten_item_names.append(item["Name"])
    #
    #     return returned_items

    def set_tags(self, item_id, tags: list):
        """
        Setzt die Tags eines Items.
        """
        return self.__update_item(item_id, {
            "Tags": tags,
            "TagItems": tags
        }
                                  )
    def set_genres(self, item_id, tags: list):
        """
        Setzt die Tags eines Items.
        """
        return self.__update_item(item_id, {
            "Genres": tags,
            "GenreItems": tags
        }
                                  )




    def is_in_filtertype(self, tag, libtype):
        """ Returns a :class:`~plexapi.library.FilteringType` for a specified libtype.

            Parameters:
                libtype (str, optional): The library type to filter (movie, show, season, episode,
                    artist, album, track, photoalbum, photo, collection).

            Raises:
                :exc:`~plexapi.exceptions.NotFound`: Unknown libtype for this library.
        """

        #lib type show:
        # ['genre', 'year', 'contentRating', 'studio', 'network', 'country', 'collection', 'director', 'actor', 'writer', 'producer', 'unwatchedLeaves', 'unmatched', 'label']

        # lib type movie:
        # ['genre', 'year', 'decade', 'contentRating', 'collection', 'director', 'actor', 'writer', 'producer', 'country', 'studio', 'resolution', 'hdr', 'unwatched', 'inProgress', 'unmatched', 'audioLanguage', 'subtitleLanguage', 'editionTitle', 'label', 'duplicate']

        #lib type movie
        my_list = []
        if libtype == "show":
            my_list = ['genre', 'year', 'contentRating', 'studio', 'network', 'country', 'collection', 'director', 'actor', 'writer', 'producer', 'unwatchedLeaves', 'unmatched', 'label', 'show.label', 'show.studio']
        else:
            my_list = ['genre', 'year', 'decade', 'contentRating', 'collection', 'director', 'actor', 'writer', 'producer', 'composer', 'country', 'studio', 'resolution', 'hdr', 'unwatched', 'inProgress', 'unmatched', 'audioLanguage', 'subtitleLanguage', 'editionTitle', 'label', 'duplicate']

        return tag in my_list

        try:
            return next(f for f in self.filterTypes() if f.type == libtype)
        except StopIteration:
            availableLibtypes = [f.type for f in self.filterTypes()]
            from plexapi.exceptions import NotFound
            raise NotFound(f'Unknown libtype "{libtype}" for this library. '
                           f'Available libtypes: {availableLibtypes}') from None



    def get_provider_ids(self, item):

        if str(item.ratingKey) in self.cached_provider_ids:
            current_provider_ids = self.cached_provider_ids[str(item.ratingKey)]
        else:
            emby_item = self.get_item(item.ratingKey)

            # item_type = ""
            # Hole die existierenden ProviderIds
            current_provider_ids = emby_item.get("ProviderIds", {})

        normalized_prov_ids = {key.lower(): value for key, value in current_provider_ids.items()}

        imdb = normalized_prov_ids.get("imdb",None)
        tvdb = normalized_prov_ids.get("tvdb",None)
        tmdb = normalized_prov_ids.get("tmdb",None)

        # item_type = "show" if emby_item.get('Type')=="Series" else "movie"

        return [imdb, tvdb, tmdb]


    def search(self, title=None, sort=None, maxresults=None, libtype=None, **kwargs):
        """
        Searches the Emby server and returns results in batches of 100.

        Args:
            title (str): The title to search for.
            sort (str): The sort order of the results.
            maxresults (int): The maximum number of results to return.
            libtype (str): The type of library items to include in the search.
            **kwargs: Additional parameters to pass to the search query.

        Returns:
            list: A list of search results.
        """
        endpoint = "/emby/Items"
        batch_size = 100
        start_index = 0
        all_results = []

        if kwargs == "":
            pass

        # Log unknown parameters
        valid_params = {"title", "sort", "maxresults", "libtype", "label"}
        unknown_params = {k: v for k, v in kwargs.items() if k not in valid_params}
        if unknown_params:
            raise Warning(f"Unknown parameters passed to EMBY search: {unknown_params}")
        my_label = kwargs.get("label", "")
        while True:
            # Build the query parameters
            params = {
                "SearchTerm": title,
                "SortBy": sort,
                "Limit": batch_size,
                "StartIndex": start_index,
                "IncludeItemTypes": libtype,
                "Tags": my_label,
                "EnableImages": 'true',
                "api_key": self.api_key,
            }
            # Merge with any additional kwargs
            params.update(kwargs)

            # Perform the API request
            try:
                url = f"{self.emby_server_url}{endpoint}"
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                batch_results = data.get("Items", [])
                all_results.extend(batch_results)

                # If fewer results than the batch size, we are done
                if len(batch_results) < batch_size:
                    break

                # Increment the start index for the next batch
                start_index += batch_size

                # Respect the maxresults limit if provided
                if maxresults and len(all_results) >= maxresults:
                    return all_results[:maxresults]

            except requests.exceptions.RequestException as e:
                raise ERROR(f"Error occurred during search: {e}")

        return self.convert_emby_to_plex(all_results)


    def get_boxsets_from_library(self, title=None, library_id= None, label = None, native = False) ->[Collection]:
        """
        Retrieve all boxsets from the library with CollectionType 'boxsets'.
        Optionally, filter boxsets by a specific title.

        Args:
            title (str, optional): The title of the boxset to search for. Defaults to None.

        Returns:
            list: A list of Plex-compatible boxset objects.
        """
        search_title=""
        search_tag=""
        get_fields=f"&Fields=ParentId"
        if title:
            search_title= f"&SearchTerm={urllib.parse.quote(title).replace("&","%26")}"
        if label:
            search_tag = f"&Tags={urllib.parse.quote(label)}"
        # else:
        #     search_tag = f"&Tags=Kometa"

        # if library_id:

        if not library_id:
            library_id = self.library_id

        my_search = f"{self.emby_server_url}/Users/{self.user_id}/Items?Recursive=true{search_title}{search_tag}{get_fields}&ParentId={library_id}&IncludeItemTypes=BoxSet&api_key={self.api_key}"
        # my_search = f"{self.emby_server_url}/Items?Recursive=true&SearchTerm={title}&IncludeItemTypes=BoxSets&api_key={self.api_key}"

        title_response = requests.get(
            my_search
        ).json().get("Items", [])
        my_return = list(title_response)
        # if len(title_response) > 0:
        #     for title in title_response:
        #         if title.get("Type")!= "Boxset":
        #             my_return.remove(title)
        #             continue
        #         my_items= self.get_items_in_boxset(title.get("Id"))
        #         if len(my_items) == 0:
        #             self.delete_collection(title.get("Id"),is_id=True)
        #             my_return.remove(title)

        plex_collections = self.convert_emby_to_plex(my_return, native)
        return plex_collections

                # print(f"Title not found in collections: {title}")
            # print(title_response)

            # 'https://piratensenderpowerplay.myqnapcloud.com:18096/emby/Items?Recursive=true&SearchTerm=IMDb%20Lowest%20Rated&api_key=1a0798043dc549a5ace4f9a216980308' \


        # todo: nur die collections der library finden
        # 1. alle collections abfragen
        response = requests.get(
            f"{self.emby_server_url}/Items?IncludeItemTypes=BoxSet&ParentId={library_id}&api_key={self.api_key}"
        )
        collections_with_items = []
        collection_items = response.json().get("Items", [])

        plex_collections = self.convert_emby_to_plex(collection_items)

        logger.info(f"EmbyServer retrieved and converted {len(collection_items)} boxsets from library '{library_id}'.")

        return plex_collections


        for collection_item in collection_items:
            # todo add ParentId as selector?
            all_items_in_box_set = self.get_items_in_boxset(collection_item.get("Id",""),native=True)
            for item in all_items_in_box_set:
                if item.get("ParentId") == library_id:
                    collections_with_items.append(collection_item)
                    print(f"{collection_item.get("Name","UNKNOWN")} found in Library")
                    break
            # if collection_item.get("ParentId") == library_id:

        plex_collections = self.convert_emby_to_plex(collections_with_items)

        logger.info(f"Retrieved and converted {len(plex_collections)} boxsets from library '{library_id}'.")

        return plex_collections


        # 2. alle inhalte der collections abfragen
        # 3. alle medien der lib_id abfragen
        # 4. abgleich mit den inhalten der collection
        # 5. => boxsets from library

        # Schritt 3: Alle Items in der Bibliothek abrufen
        response = requests.get(
            f"{self.emby_server_url}/Items?ParentId={library_id}&IncludeItemTypes=BoxSet&Recursive=True&s&api_key={self.api_key}"
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve items from library with ID {library_id}. "
                f"Response: {response.status_code} - {response.text}"
            )

        items = response.json().get("Items", [])
        if not items:
            return []
            raise Failed(f"No boxsets found in library '{library_id}'.")

        # print(items)
        # Schritt 4: Filtere die Items mit Type 'BoxSet'
        # boxsets = [item for item in items if item.get("Type") == "BoxSet"]


        # Schritt 5: Filtere nach Titel, falls angegeben

        # if not boxsets:
        #     raise Failed(f"No boxsets matching the title '{title}' were found.") if title else print("No boxsets found.")


        # Schritt 6: Konvertiere die Boxsets zu Plex-kompatiblen Objekten
        plex_collections = self.convert_emby_to_plex(items)

        logger.info(f"Retrieved and converted {len(plex_collections)} boxsets from library '{library_id}'.")

        return plex_collections

    def get_items_in_boxset(self, collection_id: str, include: str = "Movie,Series,Episode,MusicArtist",
                            fields: str = "ProviderIds,ParentId,ProductionYear,People", native: bool = False):
        """
        Retrieves all items in a collection based on the provided collection ID in batches of 100 items.

        Args:
            collection_id (str): The ID of the collection.
            include (str): The types of items to include. Defaults to "Movie,Series,Episode,MusicArtist".
            fields (str): The fields to include in the response. Defaults to "ProviderIds,ParentId,ProductionYear,People".
            native (bool): If True, return the native response from Emby. Otherwise, convert to Plex format.

        Returns:
            list: A list of items (dictionaries) from the collection, with the year added to each item.
        """
        if collection_id is None:
            logger.error("Collection ID is None. Cannot fetch items.")
            return []

        if include == "Show":
            include = "Series"

        items = []
        batch_size = 100
        start_index = 0

        while True:
            # Build the API endpoint with batching parameters
            endpoint = (f"/emby/Items?ParentId={collection_id}&IncludeItemTypes={include}&Fields={fields}&StartIndex={start_index}&Limit={batch_size}&api_key={self.api_key}")
            url = self.emby_server_url + endpoint

            try:
                # Perform the API request
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                items_data = response.json()
                batch_items = items_data.get("Items", [])

                # Add the retrieved items to the list
                items.extend(batch_items)

                # If fewer than batch_size items were returned, we are at the end
                if len(batch_items) < batch_size:
                    break

                # Increment the start index for the next batch
                start_index += batch_size

            except:# requests.exceptions.RequestException as e:
                logger.error(f"Error occurred while getting items in collection ID {collection_id}.")
                # print(f"Error occurred while getting items in collection ID {collection_id}: {e}")
                return []
                break

        if native:
            return items
        else:
            return self.convert_emby_to_plex(items)

    def create_collection(self, collection_name, item_ids, parent_id, locked=False) -> bool:
        """
        Check if collection exists, creates if not, then adds items to it in batches.
        Must add at least one item when creating collection.

        Args:
            collection_name (str): The name of the collection to be created.
            item_ids (list): A list of item IDs to be added to the collection.
            parent_id (str): The parent ID for the collection.
            locked (bool): Whether the collection should be locked after creation.

        Returns:
            bool: True if the collection is created successfully, False otherwise.
        """
        if not item_ids:
            logger.error("Can't create collection, no items to add to it.")
            return None

        try:
            # item_ids = [str(item_id) for item_id in item_ids]
            # Format the collection name for the API
            collection_name = collection_name.replace('+', '%2B').replace('&', '%26')

            # Create the collection with the first batch of items
            first_batch = item_ids[:100]  # Use the first 100 items for initial creation
            response = requests.post(
                f"{self.emby_server_url}/Collections?api_key={self.api_key}&IsLocked=true&ParentId={parent_id}&Name={collection_name}&Ids={self.__ids_to_str(first_batch)}"
            )

            if response.status_code != 200:
                logger.error(f"create_collection: Error creating {collection_name}, response: {response.text}")
                return None

            # Parse the response to get the collection ID
            data = response.json()
            collection_id = data.get('Id')
            logger.info(f"Successfully created collection {collection_name}")

            # Process remaining items in batches of 100
            batch_size = 100
            for i in range(batch_size, len(item_ids), batch_size):
                batch = item_ids[i:i + batch_size]
                # string_ids = ','.join(batch)
                batch_response = requests.post(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items?api_key={self.api_key}&Ids={self.__ids_to_str(batch)}"
                )

                if batch_response.status_code != 204:
                    logger.error(
                        f"Error adding batch {i // batch_size + 1} to collection {collection_name}, response: {batch_response.text}")

            # Lock the collection if specified
            if locked:
                self.lock_collection(collection_id)

            # Optional: Update the display order
            self.update_collection_display_order(collection_id, "test")

            time.sleep(1)  # Add a short delay to avoid API rate limits
            return collection_id
        except Exception as e:
            logger.error(f"Collection creation failed. - {e}")

    def create_smart_collection(self, title, smart_type, my_items, ignore_blank_results, parent_id):
        """
        Emulate smart playlists in Emby by interpreting uri_args,
        querying the Emby API for matching items, and adding them to a new collection.

        Args:
            title (str): The name of the collection to be created.
            smart_type (str): The type of smart playlist (e.g., '1' for movies).
            uri_args (str): The URI arguments specifying the filters and sorting.
            ignore_blank_results (bool): Whether to proceed if no items match the criteria.
        """
        # Parse uri_args
        # args = parse_qs(uri_args.lstrip('?'))

        # Initialize Emby API query parameters
        emby_query_params = {}
        unknown_params = {}



        if len(my_items) == 0:
            logger.info(f"No items found matching the criteria.")
            if not ignore_blank_results:
                return None
        else:
            # Get item IDs
            item_ids = [item.ratingKey for item in my_items]

            # Create collection with the found items
            return self.create_collection(title, item_ids, parent_id)
            print(f"Successfully created smart collection '{title}' with {len(item_ids)} items.")
    # Not tested and not working for collections.
    def delete_item(self, item_id) -> bool:
        """
        Deletes an item from the Emby server.

        Args:
            item_id (str): The ID of the item to be deleted.

        Returns:
            bool: True if the item is deleted successfully, False otherwise.
        """

        url = f"{self.emby_server_url}/Items?{item_id}&api_key={self.api_key}"
        response = requests.delete(url)
        if response.status_code == 200:
            return True
        else:
            return False

    # If you need to cache the library property
    from functools import cached_property

    @cached_property
    def library(self):
        """ Library to browse or search your media. """
        try:
            data = self.get_library_data(self.library_id)
        except Exception as e:
            # Handle exceptions as needed
            data = {}
        return data

    def get_libraries(self):
        endpoint = f"{self.emby_server_url}/emby/Library/MediaFolders"
        response = self.session.get(endpoint, headers=self.headers)
        response.raise_for_status()
        # ToDo: maybe add section as Fields
        return response.json().get('Items', [])

    def get_library_data(self, library_id):
        endpoint = f"{self.emby_server_url}/emby/Library/Sections/{library_id}"
        response = self.session.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def invalidate_item(self, item_id: int) -> None:
        """Von außen aufrufen, wenn du ein Item (z.B. Genres) geändert hast."""
        self.dirty_items.add(item_id)
        self.item_cache.pop(item_id, None)

    def _resolve_item_id(self, plex_object) -> int:
        # ratingKey auf Plex-Objekten
        if hasattr(plex_object, "ratingKey"):
            return int(getattr(plex_object, "ratingKey"))

        # direkte ID (int) oder als String
        if isinstance(plex_object, int):
            return plex_object
        if isinstance(plex_object, str):
            return int(plex_object.strip())

        # Korrekt: echten Exception-Typ werfen, NICHT WARNING (logging-level int)
        raise Failed(f"Cannot resolve Emby item id from type={type(plex_object).__name__}: {plex_object!r}")

    # ToDo: Merge with fetch_item, also merge item cache
    def get_item(self, item_id: int | str, *, force_refresh: bool = False) -> dict | None:
        try:
            item_id = int(item_id)
        except: # will be triggered if item doesnt exist yet
            return None

        if not force_refresh and item_id in self.item_cache and item_id not in self.dirty_items:
            return self.item_cache[item_id]

        endpoint = f"/emby/users/{self.user_id}/Items/{item_id}?api_key={self.api_key}"
        url = self.emby_server_url + endpoint
        try:
            resp = requests.get(url, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            self.item_cache[item_id] = data
            self.dirty_items.discard(item_id)  # wieder „sauber“
            return data
        except Exception as e:
            logger.ghost(f"Error occurred while getting item: {e}. URL: {url}.")
            return None

    def get_item_images(self, item_id) -> dict:
        endpoint = f"/emby/Items/{item_id}/Images?api_key={self.api_key}"
        url = self.emby_server_url + endpoint
        try:
            return requests.get(url, headers=self.headers).json()
        except Exception as e:
            logger.error(f"Error occurred while getting item image: {e}. URL: {url}.")
            return None

    def set_item_property(self, item_id, property_name, property_value):
        return self.__update_item(item_id, {property_name: property_value})

    def get_collection_id(self, collection_name:str):
        all_collections = self.get_boxsets_from_library(title=collection_name)
        collection_found = False
        collection_id = None
        for collection in all_collections:
            # print(collection)
            if collection_name == collection.title:
                collection_found = True
                collection_id = collection.ratingKey
                break

        if not collection_found:
            return None

        return collection_id

    def add_to_collection(self, collection_name, item_ids: list) -> int:
        # Returns the number of items added to the collection
        return self.__add_remove_from_collection(collection_name, item_ids, "add")

    def delete_from_collection(self, collection_name, item_ids: list) -> int:
        # Returns the number of items deleted from the collection
        return self.__add_remove_from_collection(collection_name, item_ids, "delete")

    def refresh_item(self, item_id):
        # Refreshes metadata for a specific item
        response = requests.post(
            f"{self.emby_server_url}/Items/{item_id}/Refresh?api_key={self.api_key}&ReplaceAllMetadata=true"
        )
        time.sleep(self.seconds_between_requests)
        if response.status_code != 204:
            logger.error(f"Error refreshing item {item_id}, response: {response}")
            return False
        return True

    def custom_encode(self, params):
        """
        Custom encoder to handle the `Tags` parameter without re-encoding certain characters.
        """
        encoded_parts = []
        for key, value in params.items():
            # input_string = str(value).replace("+", "%2B") # Apple TV+
            encoded_parts.append(f"{key}={urllib.parse.quote(str(value), safe='|,')}")
        return "&".join(encoded_parts)

    def get_items(
            self,
            params=None,
            fields=None,
            include_item_types=None,
            filters=None,
            sort_by=None,
            limit=None,
            start_index=0,
            getAll=True,
    ):
        """
        Generic method to retrieve all items from Emby, querying in batches.

        Args:
            params (dict): Additional parameters to include in the query.
            fields (list): List of fields to include in the response.
            include_item_types (list): Types of items to include (e.g., ['Movie', 'Series']).
            filters (list): Filters to apply to the query.
            sort_by (str): Field to sort the results by.
            limit (int): Number of items to query in each batch.
            start_index (int): Index to start querying from.
            getAll (bool): Flag to indicate whether to retrieve all items or just the first batch.

        Returns:
            list: All items retrieved from the Emby API.
        """
        endpoint = f"/emby/Users/{self.user_id}/Items"
        query_params = {}
        query_params["api_key"] = self.api_key

        if fields:
            query_params["Fields"] = fields
        else:
            query_params["Fields"] = "Studios,CustomRating,CriticRating,CommunityRating"

        if include_item_types:
            query_params["IncludeItemTypes"] = ",".join(include_item_types)
        if filters:
            query_params["Filters"] = ",".join(filters)
        if sort_by:
            query_params["SortBy"] = sort_by
        if limit:
            query_params["Limit"] = limit

        if params:
            query_params.update(params)

        if "Tags" in query_params:
            query_params["Tags"] = query_params["Tags"].replace("&", "%26")


        if "Studios" in query_params:
            the_studio = self.get_library_studios(query_params["Studios"])
            if len(the_studio) == 0:
                return []

        limit_query = 100
        if not "Ids" in query_params:
            query_params["Recursive"] = "true"

        url = self.emby_server_url + endpoint
        all_items = []

        if "Ids" in query_params:
            ids = query_params["Ids"].split(",")
            batches = [ids[i:i + limit_query] for i in range(0, len(ids), limit_query)]
        else:
            batches = [None]  # Single batch when no Ids are specified

        for batch in batches:
            if batch:
                query_params["Ids"] = ",".join(batch)
            start_index = 0

            while True:
                time.sleep(self.seconds_between_requests)
                query_params["StartIndex"] = start_index
                encoded_query = self.custom_encode(query_params)
                full_url = f"{url}?{encoded_query}"

                response = requests.get(full_url, headers=self.headers)
                try:
                    response_data = response.json()
                except Exception as e:
                    logger.error(
                        f"Error getting items using URL {url} params {query_params} with response {response.content}. Error: {e}"
                    )
                    return None

                if "Items" in response_data:
                    items = response_data["Items"]
                    all_items.extend(items)
                    if len(items) < limit_query:
                        break  # All items retrieved
                    start_index += limit_query
                else:
                    break

                if not getAll:
                    break

        # Filter and keep items based on ratings or studios
        filtered_results = list(all_items)
        if "SortBy" in query_params:
            sort_key = query_params["SortBy"]
            reverse_order = query_params.get("SortOrder", "Ascending").lower() == "descending"

            try:
                # Sortiere basierend auf dem SortBy-Schlüssel
                filtered_results.sort(key=lambda item: item.get(sort_key, 0), reverse=reverse_order)
            except Exception as e:
                logger.error(f"Error during sorting by {sort_key}: {e}")
                raise Failed(f"Sorting failed for key: {sort_key}")
        if (
                "MaxCriticRating" in query_params or "MaxCommunityRating" in query_params or "MaxCustomRating" in query_params or
                "MinCriticRating" in query_params or "MinCommunityRating" in query_params or "MinCustomRating" in query_params
        ):
            updated_results = []

            for item in all_items:
                keep_item = True
                if "MaxCriticRating" in query_params:
                    critic_rating = int(item.get("CriticRating", 0))
                    max_rating = int(query_params.get("MaxCriticRating"))
                    if critic_rating > max_rating or critic_rating == 0:
                        keep_item = False

                if "MaxCommunityRating" in query_params:
                    community_rating = float(item.get("CommunityRating", 0))
                    max_rating = float(query_params.get("MaxCommunityRating"))
                    if community_rating > max_rating or community_rating == 0:
                        keep_item = False

                if "MaxCustomRating" in query_params:
                    custom_rating = float(item.get("CustomRating", 0))
                    max_rating = float(query_params.get("MaxCustomRating"))
                    if custom_rating > max_rating or custom_rating == 0:
                        keep_item = False

                if "MinCriticRating" in query_params:
                    critic_rating = int(item.get("CriticRating", 0))
                    min_rating = int(query_params.get("MinCriticRating"))
                    if critic_rating < min_rating or critic_rating == 0:
                        keep_item = False

                if "MinCommunityRating" in query_params:
                    community_rating = float(item.get("CommunityRating", 0))
                    min_rating = float(query_params.get("MinCommunityRating"))
                    if community_rating < min_rating or community_rating == 0:
                        keep_item = False

                if "MinCustomRating" in query_params:
                    custom_rating = float(item.get("CustomRating", 0))
                    min_rating = float(query_params.get("MinCustomRating"))
                    if custom_rating < min_rating or custom_rating == 0:
                        keep_item = False

                if keep_item:
                    updated_results.append(item)

            filtered_results = updated_results

        # Studio search logic
        if "Studios" in query_params:
            studio_filter_results = []
            studio_names = query_params["Studios"].split(",")
            for item in filtered_results:
                item_studios = item.get("Studios", [])
                for studio in item_studios:
                    if studio.get("Name") in studio_names:
                        studio_filter_results.append(item)
                        break  # Avoid duplicate entries for the same item
            filtered_results = studio_filter_results

        if "Limit" in query_params:
            try:
                # Konvertiere Limit in eine Zahl und begrenze die Anzahl der zurückgegebenen Ergebnisse
                limit = int(query_params["Limit"])
                filtered_results = filtered_results[:limit]
            except ValueError:
                logger.error(f"Invalid Limit value: {query_params['Limit']}")
                raise Failed(f"Invalid Limit value: {query_params['Limit']}")
        return filtered_results

    def set_item_as_played(self, user_id, item_id):
        """
        Set an item as played for a specific user.

        Args:
            user_id (str): The ID of the user.
            item_id (str): The ID of the item to mark as played.

        Returns:
            bool: True if the item was marked as played successfully, False otherwise.
        """
        endpoint = f"/emby/Users/{user_id}/PlayedItems/{item_id}"
        url = self.emby_server_url + endpoint
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            return True
        else:
            logger.error(
                f"Error marking item {item_id} as played for user {user_id}: {response.content}"
            )
            return False

    def set_item_as_favorite(self, user_id, item_id):
        """
        Set an item as a favorite for a specific user.

        Args:
            user_id (str): The ID of the user.
            item_id (str): The ID of the item to mark as a favorite.

        Returns:
            bool: True if the item was marked as a favorite successfully, False otherwise.
        """
        endpoint = f"/emby/Users/{user_id}/FavoriteItems/{item_id}"
        url = self.emby_server_url + endpoint
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            return True
        else:
            logger.error(
                f"Error marking item {item_id} as a favorite for user {user_id}: {response.content}"
            )
            return False

    def set_image_smart(
            self,
            item_id: str,
            image_path: str,
            image_type: str = "Primary"
    ) -> bool:
        if image_path.startswith("http"):
            return self.__set_remote_image(item_id, image_path, image_type)
        else:
            return self.__upload_image(item_id, image_path, image_type)


    def __set_remote_image(
        self,
        item_id,
        image_url,
        image_type="Primary",
    ):
        """
        Downloads a remote image for an item.

        Args:
            item_id (str): The ID of the item.
            image_url (str): The URL of the image to download.
            image_type (str): The type of the image. Defaults to "Primary".
            provider_name (str): The name of the image provider. Defaults to "MDBList Collection Creator script".

        Returns:
            bool: True if the image is downloaded successfully, False otherwise.
        """
        endpoint = f"/emby/Items/{item_id}/RemoteImages/Download"
        url = self.emby_server_url + endpoint

        params = {
            "Type": image_type,
            "ImageUrl": image_url,
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=params,
            )

            if response.status_code == 204:
                return True
            else:
                # logger.error(f"Error setting image for item {item_id}, response: {response}")
                return False

        except Exception as e:
            logger.error(f"Exception occurred while downloading image: {str(e)}")
            return False

    def __upload_image(self, item_id, image_path, image_type="Primary"):
        """
        Uploads a poster image to a collection. Allows for .jpg, .jpeg, .png, and .tbn formats.

        Args:
            item_id (str): The ID of the item.
            image_path (str): The path to the image to upload.
            image_type (str): The type of the image. Defaults to "Primary".

        Returns:
            bool: True if the image is uploaded successfully, False otherwise.
        """

        if not os.path.exists(image_path):
            logger.error(f"Error: Image file not found: {image_path}")
            return False


        ext_to_content_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tbn": "image/jpeg",  # .tbn ist technisch JPEG
            ".webp": "image/webp",
        }

        ext = os.path.splitext(image_path)[1].lower()
        if ext not in ext_to_content_type:
            logger.error(f"Unsupported image format. Must be one of: {', '.join(ext_to_content_type.keys())}")
            return False

        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            image_data_base64 = base64.b64encode(image_data)

            endpoint = (
                f"/emby/Items/{item_id}/Images/{image_type}?api_key={self.api_key}"
            )
            url = self.emby_server_url + endpoint
            headers = {
                "Content-Type": "image/jpeg",
                "X-Emby-Token": self.api_key,
            }

            response = requests.post(
                url,
                headers=headers,
                data=image_data_base64,
            )

            if response.status_code == 204:
                return True
            else:
                logger.error(f"Error uploading image for item {item_id}, response: {response}")
                return False

        except Exception as e:
            logger.error(f"Exception occurred while uploading image: {str(e)}")
            return False

    # Konvertierungsfunktion, um Emby-Daten in Plex-Klassenobjekte zu konvertieren
    def convert_emby_to_plex(self, emby_data_list, use_native_emby = False):
        plex_objects = []
        if not emby_data_list or len(emby_data_list) == 0:
            return []

        # emby_data_list = sorted(set(emby_data_list))
        for item in emby_data_list:
            # print(item)
            if item is None:
                logger.info("Item is None")
                continue
            if item.get("Id") in self.cached_plex_objects:
                plex_object = self.cached_plex_objects[item.get("Id")]
            else:

                # if isinstance(item, str):
                #     print("Ich bin string!!!")
                name = item.get("Name")
                studio_entries =item.get("Studios")
                studio = ""
                if studio_entries:
                    # fix multiple studios when updating, only one allowed
                    if len(studio_entries) > 1:
                        for entry in studio_entries:
                            studio += f"{entry.get('Name')}"
                    else:
                        studio= studio_entries[0].get("Name")

                genres = item.get("Genres")
                server_id = item.get("ServerId")
                item_id = item.get("Id")
                item_overview = item.get("Overview")
                runtime_ticks = item.get("RunTimeTicks")
                if runtime_ticks:
                    runtime_ticks= int(runtime_ticks) / 10000
                # provider_ids = item.get("ProviderIds", {})
                media_type = item.get("Type")
                image_tags = item.get("ImageTags", {})
                backdrop_image_tags = item.get("BackdropImageTags", [])
                year = item.get("ProductionYear", None)
                series_id = item.get("SeriesId")
                if year:
                    year= int(year)
                people = item.get("People", [])
                plex_actors = []
                # for person in people:
                #     # List[PlexObjectT]
                #     if person.get('Type') == 'Actor':
                #         new_person = PLEXOBJECTS.get("actor")()
                #         # new_person.tag = 'actor'
                #         new_person.id = person.get('Id')
                #         new_person.name = person.get('Name')
                #         plex_actors.append(new_person)
                # {'Id': '12917', 'Name': 'Hideko Takamine', 'PrimaryImageTag': '243089fe465d5f5402eb21462e0d915e', 'Role': 'Keiko Yashiro', 'Type': 'Actor'}
                # Erstelle ein Datenobjekt, das der Plex-API-Struktur ähnelt
                crit_rat = item.get("CriticRating")
                if crit_rat: # prevent constant updates, fake plex its original value
                    crit_rat = float(crit_rat) /10
                data = {
                    'title': name,
                    'ratingKey': item_id,
                    'duration': runtime_ticks,
                    'guid': item_id,
                    'posterUrl': image_tags.get('Primary', ''),
                    'thumbUrl': image_tags.get('Art', ''),
                    'type': media_type.lower(),
                    'backdrop': ','.join(backdrop_image_tags),
                    'year': year,
                    'summary':item_overview,
                    'grandparentTitle':item.get('SeriesName'),
                    'audienceRating': item.get("CommunityRating"),
                    'rating': crit_rat,
                    'userRating': item.get("CustomRating"),
                    'studio': studio, # only one
                    'genres': genres,
                    'titleSort': item.get('SortName'),
                    # not working
                    # 'media': [item.get('Path')],
                    # 'locations':[item.get('Path')] # todo: working?
                    # 'roles':plex_actors
                }
                if item.get("Type") == "Series":

                    pass
                elif item.get("Type") == "Season":
                    new_data={
                        'index': item.get('IndexNumber'),
                        'parentTitle': item.get('SeriesName')
                    }
                    data.update(new_data)
                    pass
                elif item.get("Type") == "Episode":
                    pass

            # print(media_type)
                if media_type == "Movie":
                    plex_object = Movie(data)
                elif media_type == "Series":
                    plex_object = Show(data)
                elif media_type == "Season":
                    plex_object= Season(data)
                elif media_type == "Episode":
                    plex_object=Episode(data)
                elif media_type == "BoxSet":
                    new_col = Collection(data)
                    if not use_native_emby:
                        allitems = self.get_items_in_boxset(new_col.ratingKey)
                        new_col._items = allitems
                        new_col.childCount= len((allitems))

                    plex_object=new_col

                elif media_type == "Audio":
                    plex_object=Audio(data)
                elif media_type == "Person":
                    plex_object=Person(data)
                else:
                    logger.error(f"error converting Emby object")
                    continue
                plex_object.locations = [item.get("Path", [])]
                if not use_native_emby:
                    self.cached_plex_objects[item.get("Id")] = plex_object

            plex_objects.append(plex_object)
            # else:
            #     plex_objects.append(
            #         PlexMedia(name, server_id, item_id, runtime_ticks, provider_ids, media_type, image_tags,
            #                   backdrop_image_tags))

        return plex_objects


    def add_tags(self, item_id:int, add_tags:[]):
        """
        Fügt einen Tag hinzu.
        """
        item = self.get_item(item_id)
        if not item:
            return False
        current_tags = item.get("TagItems", [])
        new_tags = []
        for tag_item in current_tags:
            new_tags.append(tag_item.get('Name'))

        for tag in add_tags:
            if tag not in new_tags:
                new_tags.append(tag)

        # db_tags = ",".join(new_tags)


        return self.__update_item(item_id, {"Tags": new_tags, "TagItems": new_tags}, item)


    def remove_tags(self, item_id, tags):
        """
        Entfernt einen Tag.
        """
        item = self.get_item(item_id)
        if not item:
            return False

        current_tags = item.get("TagItems", [])
        new_tags = []
        for tag_item in current_tags:
            if tag_item.get('Name') not in tags:
                new_tags.append(tag_item.get('Name'))


        return self.__update_item(item_id, {"Tags": new_tags, "TagItems": new_tags}, item)

    def update_item(self, item_id, data):
        return self.__update_item(item_id,data)

    def __update_item(self, item_id, data, item = None):
        if not item:
            item = self.get_item(item_id)
        if item is None:
            return None
        self._ensure_http_session()

        if "LockedFields" not in item:
            item["LockedFields"] = []

        if "ForcedSortName" in data:
            item["ForcedSortName"] = data["ForcedSortName"]
            item["SortName"] = data["ForcedSortName"]

            if "SortName" not in item["LockedFields"]:
                item["LockedFields"].append("SortName")

        unchanged = all(item.get(k) == v for k, v in data.items())
        if unchanged:
            return None

        item.update(data)

        update_item_url = (
            f"{self.emby_server_url}/emby/Items/{item_id}?api_key={self.api_key}"
        )
        my_= str(item)
        try:
            response = self._http_session.post(update_item_url, json=item)
            # print(
            #     f"Updated item {item_id} with {data}. Waiting {self.seconds_between_requests} seconds."
            # )
            # time.sleep(self.seconds_between_requests)
            self.invalidate_item(item_id)
            return response
        except Exception as e:
            logger.warning(f"Emby item not longer present, not updated: {item_id}")
            return None

    def __add_remove_from_collection(
        self, collection_name: str, item_ids: list, operation: str
    ) -> int:

        affected_count = 0
        if not item_ids:
            return None

        collection_id = self.get_collection_id(collection_name)

        if collection_id is None:
            return None

        batch_size = self.api_batch_size
        num_batches = (len(item_ids) + batch_size - 1) // batch_size

        logger.info(
            f"Processing {collection_name} with '{operation}' in {num_batches} batches"
        )

        for i in range(num_batches):
            start_index = i * batch_size
            end_index = min((i + 1) * batch_size, len(item_ids))
            batch_item_ids = item_ids[start_index:end_index]
            # print(".", end="", flush=True)

            if operation == "add":
                response = requests.post(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items/?api_key={self.api_key}&Ids={self.__ids_to_str(batch_item_ids)}"
                )
            elif operation == "delete":
                response = requests.delete(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items/?api_key={self.api_key}&Ids={self.__ids_to_str(batch_item_ids)}"
                )

            if response.status_code != 204:
                logger.error(
                    f"Error processing collection with operation '{operation}', response: {response}"
                )
                return affected_count

            affected_count += len(batch_item_ids)
            time.sleep(self.seconds_between_requests)

        # print()
        logger.info(f"Finished '{operation}' with {len(item_ids)} items in {collection_name}")

        return affected_count

    def add_remove_plex_object_from_collection(
        self, collection_name: str, plex_objects: list, operation: str, collection_id = None) -> int:
        item_ids = []
        for item in plex_objects:
            item_ids.append(item.ratingKey)

        affected_count = 0
        if not item_ids:
            return affected_count

        if not collection_id:
            collection_id = self.get_collection_id(collection_name)

        if collection_id is None:
            return affected_count

        batch_size = self.api_batch_size
        num_batches = (len(item_ids) + batch_size - 1) // batch_size

        logger.info(
            f"Processing {collection_name} with '{operation}' in {num_batches} batches"
        )

        for i in range(num_batches):
            start_index = i * batch_size
            end_index = min((i + 1) * batch_size, len(item_ids))
            batch_item_ids = item_ids[start_index:end_index]
            # print(".", end="", flush=True)

            if operation == "add":
                response = requests.post(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items/?api_key={self.api_key}&Ids={self.__ids_to_str(batch_item_ids)}"
                )
            elif operation == "delete":
                response = requests.delete(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items/?api_key={self.api_key}&Ids={self.__ids_to_str(batch_item_ids)}"
                )

            if response.status_code != 204:
                logger.error(
                    f"Error processing collection with operation '{operation}', response: {response}"
                )
                return affected_count

            affected_count += len(batch_item_ids)
            time.sleep(self.seconds_between_requests)

        # print()
        logger.info(f"Finished '{operation}' with {len(item_ids)} items in {collection_name}")

        return affected_count

    def delete_collection(self, collection,is_id = False):
        if is_id:
            collection_id = collection
        else:
            collection_id = collection.ratingKey
        delete_url = f'{self.emby_server_url}/Items/{collection_id}/Delete?api_key={self.api_key}'
        headers = { 'accept': '*/*'}
        response = requests.post(delete_url, headers=headers)
        if response.status_code == 204:
            logger.info(f'Successfully deleted collection with ID "{collection_id}"')
        else:

            # response = requests.get(f"{self.emby_server_url}/Items?Recursive=true&ParentId={collection_id}", headers=self.headers)
            # response.raise_for_status()
            # all_items = response.json().get("Items", [])
            all_items = self.get_items_in_boxset(collection_id,native=True)
            batch_size = 100  # Größe der Batches
            all_ids = [item.get("Id") for item in all_items]
            # Teile `all_ids` in Batches auf
            for i in range(0, len(all_ids), batch_size):
                batch_ids = all_ids[i:i + batch_size]  # Nimm einen Batch von 100 IDs
                string_ids = ','.join(batch_ids)  # Verbinde die IDs zu einem String
                response = requests.delete(
                    f"{self.emby_server_url}/emby/Collections/{collection_id}/Items?Ids={string_ids}&api_key={self.api_key}"
                )

                # Optional: Überprüfe die Antwort und logge den Status
                if response.status_code == 204:
                    logger.ghost(f"Batch {i // batch_size + 1}: Erfolgreich gelöscht")
                else:
                    logger.ghost(f"Batch {i // batch_size + 1}: Fehler beim Löschen - {response.status_code} - {response.text}")
                                # all_ids = [item.get("Id") for item in all_items]
            # print(f'Error deleting collection with ID "{collection_id}": {response.text}')
    # def remove_tags_from_collection(
    #         self, collection_name: str, tags_to_remove: list
    # ) -> int:
    #     """
    #     Removes specific tags from all items in a given Emby collection.
    #
    #     Args:
    #         collection_name (str): The name of the collection.
    #         tags_to_remove (list): A list of tags to remove from items in the collection.
    #
    #     Returns:
    #         int: The number of items updated.
    #     """
    #     updated_count = 0
    #
    #     # Retrieve the collection ID
    #     collection_id = self.get_collection_id(collection_name)
    #
    #     if collection_id is None:
    #         print(f"Collection '{collection_name}' not found.")
    #         return updated_count
    #
    #     # Get all items in the collection
    #     response = requests.get(
    #         f"{self.emby_server_url}/Collections/{collection_id}/Items?api_key={self.api_key}"
    #     )
    #
    #     if response.status_code != 200:
    #         print(
    #             f"Failed to retrieve items from collection '{collection_name}'. Response: {response.status_code} - {response.text}"
    #         )
    #         return updated_count
    #
    #     items = response.json().get("Items", [])
    #
    #     if not items:
    #         print(f"No items found in collection '{collection_name}'.")
    #         return updated_count
    #
    #     print(f"Removing tags {tags_to_remove} from {len(items)} items in '{collection_name}'.")
    #
    #     # Iterate over items and remove tags
    #     for item in items:
    #         item_id = item["Id"]
    #         item_response = requests.get(
    #             f"{self.emby_server_url}/Items/{item_id}?api_key={self.api_key}"
    #         )
    #
    #         if item_response.status_code != 200:
    #             print(
    #                 f"Failed to retrieve details for item ID {item_id}. Response: {item_response.status_code} - {item_response.text}"
    #             )
    #             continue
    #
    #         item_details = item_response.json()
    #         current_tags = item_details.get("Tags", [])
    #
    #         # Remove the specified tags
    #         updated_tags = [tag for tag in current_tags if tag not in tags_to_remove]
    #
    #         if set(current_tags) == set(updated_tags):
    #             # Skip if no tags need to be removed
    #             continue
    #
    #         # Update the item's tags
    #         update_response = requests.post(
    #             f"{self.emby_server_url}/Items/{item_id}?api_key={self.api_key}",
    #             json={"Tags": updated_tags},
    #         )
    #
    #         if update_response.status_code == 204:
    #             updated_count += 1
    #             print(f"Tags updated for item ID {item_id}.")
    #         else:
    #             print(
    #                 f"Failed to update tags for item ID {item_id}. Response: {update_response.status_code} - {update_response.text}"
    #             )
    #
    #         time.sleep(self.seconds_between_requests)
    #
    #     print(f"Finished removing tags from {updated_count} items in '{collection_name}'.")
    #     return updated_count

    # def remove_collection(self, collection_name: str, locked: bool = True) -> None:
    #     """
    #     Remove a collection in Emby.
    #
    #     Args:
    #         collection_name (str): Name of the collection to remove.
    #         locked (bool): True to lock items after removal, False otherwise.
    #
    #     Returns:
    #         None
    #     """
    #     # Retrieve the collection ID
    #     collection_id = self.get_collection_id(collection_name)
    #
    #     if not collection_id:
    #         print(f"Collection '{collection_name}' does not exist.")
    #         return
    #
    #     # Remove the collection
    #     response = requests.delete(
    #         f"{self.emby_server_url}/Collections/{collection_id}?api_key={self.api_key}"
    #     )
    #
    #     if response.status_code != 204:
    #         raise Exception(
    #             f"Failed to delete collection '{collection_name}'. "
    #             f"Response: {response.status_code} - {response.text}"
    #         )
    #
    #     print(f"Collection '{collection_name}' successfully removed.")

    # def remove_kometa_tags_from_collection(self, collection_name: str, locked=True) -> int:
    #     """
    #     Remove tags starting with 'kometa_' from all items in a given Emby collection.
    #
    #     Args:
    #         collection_name (str): Name of the collection.
    #         locked (bool): True to lock the tags field after removal, False otherwise.
    #
    #     Returns:
    #         int: The number of items that had tags removed.
    #     """
    #     updated_count = 0
    #
    #     # Retrieve the collection ID
    #     collection_id = self.get_collection_id(collection_name)
    #
    #     if collection_id is None:
    #         print(f"Collection '{collection_name}' not found.")
    #         return updated_count
    #
    #     # Get all items in the collection
    #     response = requests.get(
    #         f"{self.emby_server_url}/Collections/{collection_id}/Items?api_key={self.api_key}"
    #     )
    #
    #     if response.status_code != 200:
    #         print(
    #             f"Failed to retrieve items from collection '{collection_name}'. Response: {response.status_code} - {response.text}"
    #         )
    #         return updated_count
    #
    #     items = response.json().get("Items", [])
    #
    #     if not items:
    #         print(f"No items found in collection '{collection_name}'.")
    #         return updated_count
    #
    #     print(f"Removing 'kometa_' tags from {len(items)} items in '{collection_name}'.")
    #
    #     # Iterate over items and remove 'kometa_' tags
    #     for item in items:
    #         item_id = item["Id"]
    #         item_response = requests.get(
    #             f"{self.emby_server_url}/Items/{item_id}?api_key={self.api_key}"
    #         )
    #
    #         if item_response.status_code != 200:
    #             print(
    #                 f"Failed to retrieve details for item ID {item_id}. Response: {item_response.status_code} - {item_response.text}"
    #             )
    #             continue
    #
    #         item_details = item_response.json()
    #         current_tags = item_details.get("Tags", [])
    #
    #         # Filter out tags that start with 'kometa_'
    #         updated_tags = [tag for tag in current_tags if not tag.startswith("kometa_")]
    #
    #         if set(current_tags) == set(updated_tags):
    #             # Skip if no 'kometa_' tags need to be removed
    #             continue
    #
    #         # Update the item's tags
    #         payload = {"Tags": updated_tags}
    #         if locked:
    #             payload["LockTags"] = True
    #
    #         update_response = requests.post(
    #             f"{self.emby_server_url}/Items/{item_id}?api_key={self.api_key}",
    #             json=payload,
    #         )
    #
    #         if update_response.status_code == 204:
    #             updated_count += 1
    #             print(f"'kometa_' tags updated for item ID {item_id}.")
    #         else:
    #             print(
    #                 f"Failed to update tags for item ID {item_id}. Response: {update_response.status_code} - {update_response.text}"
    #             )
    #
    #         time.sleep(self.seconds_between_requests)
    #
    #     print(f"Finished removing 'kometa_' tags from {updated_count} items in '{collection_name}'.")
    #     return updated_count

    @staticmethod
    def __ids_to_str(ids: list) -> str:
        item_ids = [str(item_id) for item_id in ids]
        return ",".join(item_ids)

    # def add_collection(self, collection_name: str, item_ids: list, locked: bool = True) -> None:
    #     """
    #     Add a collection in Emby.
    #
    #     Args:
    #         collection_name (str): The name of the collection to create or update.
    #         item_ids (list): List of item IDs to add to the collection.
    #         locked (bool): True to lock the collection, False otherwise.
    #
    #     Returns:
    #         None
    #     """
    #     # Check if collection exists
    #     collection_id = self.get_collection_id(collection_name)
    #
    #     if not collection_id:
    #         # Create a new collection if it doesn't exist
    #         response = requests.post(
    #             f"{self.emby_server_url}/Collections?api_key={self.api_key}",
    #             json={"Name": collection_name}
    #         )
    #
    #         if response.status_code != 200:
    #             raise Exception(
    #                 f"Failed to create collection '{collection_name}'. "
    #                 f"Response: {response.status_code} - {response.text}"
    #             )
    #
    #         collection_id = response.json().get("Id")
    #
    #     # Add items to the collection
    #     response = requests.post(
    #         f"{self.emby_server_url}/Collections/{collection_id}/Items?api_key={self.api_key}&Ids={','.join(map(str, item_ids))}"
    #     )
    #
    #     if response.status_code != 204:
    #         raise Exception(
    #             f"Failed to add items to collection '{collection_name}'. "
    #             f"Response: {response.status_code} - {response.text}"
    #         )
    #
    #     # Lock the collection (if applicable)
    #     if locked:
    #         self.lock_collection(collection_id)



    def lock_collection(self, collection_id: str) -> None:
        """
        Lock a collection in Emby.

        Args:
            collection_id (str): ID of the collection to lock.

        Returns:
            None
        """
        response = requests.post(
            f"{self.emby_server_url}/Items/{collection_id}?api_key={self.api_key}",
            json={"LockData": True}
        )

        if response.status_code != 204:
            raise Exception(
                f"Failed to lock collection ID {collection_id}. "
                f"Response: {response.status_code} - {response.text}"
            )


    def remove_boxset(self, collection_name, collection_id = None):
        """
        Remove a BoxSet collection from Emby.

        Args:
            collection_id (str): The ID of the collection (BoxSet) to remove.

        Returns:
            bool: True if the BoxSet was successfully removed, False otherwise.
        """
        if collection_id is None:
            collection_id = self.get_collection_id(collection_name)
        try:
            # API-Endpunkt für das Löschen einer Sammlung
            response = requests.delete(
                f"{self.emby_server_url}/Items/{collection_id}?api_key={self.api_key}"
            )

            if response.status_code == 204:
                logger.info(f"BoxSet with ID '{collection_id}' successfully removed.")
                return True
            else:
                logger.error(
                    f"Failed to remove BoxSet with ID '{collection_id}'. Response: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error removing BoxSet with ID '{collection_id}': {e}")
            return False

    def get_emby_item_tags(self, plex_object, library_id: str = "", search_all: bool = False,
                           from_cache: bool = True) -> list[str]:
        # Item-spezifisch (häufigster Fall)
        if not search_all:
            item_id = self._resolve_item_id(plex_object)
            item = self.get_item(item_id, force_refresh=(item_id in self.dirty_items))
            if not item:
                return []
            # Emby liefert entweder "Tags": ["A","B"] oder "TagItems": [{"Name":"A"}, ...]
            if isinstance(item.get("Tags"), list):
                tags = {t for t in item["Tags"] if t}
            else:
                tags = {ti.get("Name") for ti in (item.get("TagItems") or []) if ti.get("Name")}
            return sorted(tags)

        # Library-weit: erst versuchen, aus bereits gecachten Items zu aggregieren
        agg = set()
        for cached in self.item_cache.values():
            if library_id and str(cached.get("LibraryId") or cached.get("ParentId") or "") != str(library_id):
                continue
            if isinstance(cached.get("Tags"), list):
                agg.update({t for t in cached["Tags"] if t})
            else:
                agg.update({ti.get("Name") for ti in (cached.get("TagItems") or []) if ti.get("Name")})
        if agg:
            return sorted(agg)

        # Fallback: einmaliger API-Call (falls nichts im Cache bekannt ist)
        url = f"{self.emby_server_url}/emby/Tags?Recursive=true&ParentId={library_id}&api_key={self.api_key}"
        data = requests.get(url, headers=self.headers).json()
        return sorted({it.get("Name") for it in data.get("Items", []) if it.get("Name")})

    def get_emby_item_genres(self, plex_object, library_id: str = "", search_all: bool = False,
                             from_cache: bool = True) -> list[str]:
        if not search_all:
            item_id = self._resolve_item_id(plex_object)
            item = self.get_item(item_id, force_refresh=(item_id in self.dirty_items))
            if not item:
                return []
            # "Genres": ["Comedy"] oder "GenreItems": [{"Name":"Comedy"}]
            if isinstance(item.get("Genres"), list):
                genres = {g for g in item["Genres"] if g}
            else:
                genres = {gi.get("Name") for gi in (item.get("GenreItems") or []) if gi.get("Name")}
            return sorted(genres)

        agg = set()
        for cached in self.item_cache.values():
            if library_id and str(cached.get("LibraryId") or cached.get("ParentId") or "") != str(library_id):
                continue
            if isinstance(cached.get("Genres"), list):
                agg.update({g for g in cached["Genres"] if g})
            else:
                agg.update({gi.get("Name") for gi in (cached.get("GenreItems") or []) if gi.get("Name")})
        if agg:
            return sorted(agg)

        url = f"{self.emby_server_url}/emby/Genres?Recursive=true&ParentId={library_id}&api_key={self.api_key}"
        data = requests.get(url, headers=self.headers).json()
        return sorted({it.get("Name") for it in data.get("Items", []) if it.get("Name")})

    def _resolve_item_id_safe(self, plex_object):
        """Nutzt deine Helferfunktion, wenn vorhanden; einfacher Fallback sonst."""
        if hasattr(plex_object, "ratingKey"):
            return plex_object.ratingKey
        elif isinstance(plex_object, int):
            return str(plex_object)
        elif isinstance(plex_object, str):
            return str(plex_object)

        return None
        # if isinstance(plex_object, Plex):
        #     return None  # bedeutet: Library-weit arbeiten
        # raise WARNING(f"Emby item object is not configured {plex_object!r}")

    def _studios_from_item_cached(self,item: dict) -> list[str]:
        """Extrahiert Studio-Namen robust aus einem gecachten Emby-Item."""
        studios = item.get("Studios") or []
        out = []
        if isinstance(studios, list):
            for s in studios:
                if isinstance(s, dict):
                    n = s.get("Name") or s.get("name")
                    if n: out.append(str(n).strip())
                elif isinstance(s, str):
                    n = s.strip()
                    if n: out.append(n)
        elif isinstance(studios, str):
            out.extend([p.strip() for p in studios.split(",") if p.strip()])
        return out

    def get_emby_studios(self, plex_object, library_id) -> list[str]:
        """
        Studios für ein Item (oder – wenn kein Item angegeben – für die ganze Library).
        Primär aus self.item_cache; API-Fallback nur wenn nötig.
        """
        studios = set()
        item_id = self._resolve_item_id_safe(plex_object)

        # 1) Item-spezifisch
        if item_id:
            item = self.item_cache.get(str(item_id)) or self.get_item(item_id)
            if not item:
                return []
            for s in self._studios_from_item_cached(item):
                # TODO: Wenn du später Networks via Unicode '📡' trennen willst,
                #       und Studios OHNE dieses Präfix behalten möchtest:
                # if s.startswith('📡'):
                #     continue
                studios.add(s)
            return sorted(studios)

        # 2) Aggregiert aus Cache (optional nach Library gefiltert)
        for it in self.item_cache.values():
            if library_id and str(it.get("LibraryId") or it.get("ParentId") or "") != str(library_id):
                continue
            for s in self._studios_from_item_cached(it):
                # TODO: Unicode-Trennung siehe oben:
                # if s.startswith('📡'):
                #     continue
                studios.add(s)

        if studios:
            return sorted(studios)

        # 3) Fallback: Studios-Endpunkt
        url = f"{self.emby_server_url}/emby/Studios?Recursive=true&ParentId={library_id}&api_key={self.api_key}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Failed(
                f"Failed to retrieve studios for library {library_id}. "
                f"Response: {response.status_code} - {response.text}"
            )

        for item in response.json().get("Items", []):
            name = str(item.get("Name", "")).strip()
            if not name:
                continue
            # TODO: Unicode-Trennung (Studios ohne '📡'):
            # if name.startswith('📡'):
            #     continue
            studios.add(name)

        return sorted(studios)

    def get_emby_networks(self, plex_object, library_id: str):
        """
        Gibt 'Networks' zurück – aktuell identisch zu Emby-Studios (später per Unicode trennbar).
        Nutzt primär den Runtime-Cache (self.item_cache); API-Fallback nur wenn nötig.
        """
        nets = set()
        item_id = self._resolve_item_id_safe(plex_object)

        # 1) Item-spezifisch
        if item_id:
            item = self.item_cache.get(str(item_id)) or self.get_item(item_id)
            if not item:
                return []
            for n in self._studios_from_item_cached(item):
                # TODO: Unicode-Trennung aktivieren, wenn du echte Networks separierst:
                # if not n.startswith('📡'):
                #     continue
                # n = n[2:]
                nets.add(n)
            return sorted(nets)

        # 2) Aggregiert aus Cache (optional nach Library gefiltert)
        for it in self.item_cache.values():
            if library_id and str(it.get("LibraryId") or it.get("ParentId") or "") != str(library_id):
                continue
            for n in self._studios_from_item_cached(it):
                # TODO: Unicode-Trennung aktivieren, wenn du echte Networks separierst:
                # if not n.startswith('📡'):
                #     continue
                # n = n[2:]
                nets.add(n)

        if nets:
            return sorted(nets)

        # 3) Fallback auf Studios-Endpunkt, falls Cache leer
        url = f"{self.emby_server_url}/emby/Studios?Recursive=true&ParentId={library_id}&api_key={self.api_key}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Failed(f"Failed to retrieve studios for library {library_id}. "
                         f"Response: {response.status_code} - {response.text}")
        for item in response.json().get("Items", []):
            name = str(item.get("Name", "")).strip()
            if not name:
                continue
            # TODO: Unicode-Trennung aktivieren, wenn du echte Networks separierst:
            # if not name.startswith('📡'):
            #     continue
            # name = name[2:]
            nets.add(name)

        return sorted(nets)

    def get_library_studios(self, name: str | list[str] | None = None) -> list[str]:
        """
        Studios der aktuellen Library.
        - Primär aus self.item_cache (schnell), sonst API-Fallback.
        - Wenn 'name' gesetzt ist, wird die Schnittmenge (Treffer) zurückgegeben.
        """
        if not self.studio_list:
            studios = set()
            # 1) Aus Cache
            for it in self.item_cache.values():
                if str(it.get("LibraryId") or it.get("ParentId") or "") != str(self.library_id):
                    continue
                for s in self._studios_from_item_cached(it):
                    # Hinweis: Hier KEINE Trennung – dies sind „Studios“,
                    # Unicode-Filter wäre nur für „Networks“ sinnvoll:
                    # if s.startswith('📡'):
                    #     continue
                    studios.add(s)

            # 2) Fallback API
            if not studios:
                url = f"{self.emby_server_url}/emby/Studios?ParentId={self.library_id}&api_key={self.api_key}"
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    raise Failed(f"Failed to retrieve studios for library {self.library_id}. "
                                 f"Response: {response.status_code} - {response.text}")
                for item in response.json().get("Items", []):
                    n = str(item.get("Name", "")).strip()
                    if n:
                        # Unicode-Logik hier bewusst auskommentiert (nur Networks):
                        # if n.startswith('📡'):
                        #     continue
                        studios.add(n)

            self.studio_list = sorted(studios)

        # Filter nach 'name' (validiere und gib nur gefundene zurück)
        if name:
            haystack = set(self.studio_list)
            if isinstance(name, str):
                wanted = {p.strip() for p in name.split(",") if p.strip()}
            else:
                wanted = {str(p).strip() for p in name if str(p).strip()}
            hits = sorted(haystack & wanted)
            return hits

        return self.studio_list

    def multiEditRatings(self, rating_edits):
        """
        Bearbeitet die Bewertungen für die übergebenen Item-IDs.
        Jede Item-ID wird nur einmal bearbeitet, und fehlende Bewertungen werden mit leeren Feldern behandelt.

        :param rating_edits: Ein Dictionary mit Bewertungen (audienceRating, rating, userRating) und zugehörigen Item-IDs.
        """
        # Sammele alle zu bearbeitenden Items
        update_items = {}

        for field_attr, edits in rating_edits.items():
            for rating_value, item_ids in edits.items():
                for item_id in item_ids:
                    # Initialisiere das Dictionary für diese Item-ID, falls es noch nicht existiert
                    if item_id not in update_items:
                        update_items[item_id] = {}

                    # Aktualisiere das entsprechende Feld basierend auf `field_attr`
                    if field_attr == "audienceRating":
                        update_items[item_id]["CommunityRating"] = rating_value
                    elif field_attr == "rating":
                        update_items[item_id]["CriticRating"] = float(rating_value) * 10 if rating_value else ''
                    elif field_attr == "userRating":
                        update_items[item_id]["CustomRating"] = rating_value

        # Wende die Updates an
        for item_id, rating_data in update_items.items():
            # Führe das Update für das Item aus
            # print(".", end="", flush=True)
            updates = {}
            if "CommunityRating" in rating_data:
                updates["CommunityRating"] = rating_data["CommunityRating"]
            if "CriticRating" in rating_data:
                updates["CriticRating"] = float(rating_data["CriticRating"])*10
            if "CustomRating" in rating_data:
                updates["CustomRating"] = rating_data["CustomRating"]

            self.__update_item(
                item_id,
                updates
            )
        return update_items

    # ToDo: Implementation
    def multiEditField(self, rating_keys,field_attr=None, new_value=None, locked=False):
        # raise Warning(f"multiEditField not implemented for {rating_keys} - {field_attr} - {new_value} {locked}")
        # return

        self._ensure_http_session()


        for item in rating_keys:
            item_id = item.ratingKey
            changes ={}
            if field_attr == "audienceRating":
                changes["CommunityRating"] = new_value
                item.audienceRating = new_value
            elif field_attr == "rating":
                changes["CriticRating"] = float(new_value)*10
                item.rating = new_value
                # self.__update_item(item_id,{"CriticRating": new_value})
            elif field_attr == "userRating": # ToDo: use ProviderId instead of age rating
                changes["CustomRating"] = new_value
                item.userRating = new_value
            elif field_attr == "contentRating":
                changes["OfficialRating"] = new_value
                item.contentRating = new_value # item update still needed?
            elif field_attr == "studio":
                # id = self.get

                my_url = f"{self.emby_server_url}/emby/Studios/{new_value}?api_key={self.api_key}"

                # # Make a request to get the Emby item details
                response = self._http_session.get(my_url)

                # response = requests.get(
                #     f"{self.emby_server_url}/emby/Tags?{ids}Recursive=true&{library_id}api_key={self.api_key}'"
                # )

                # tags empty for collections
                if response.status_code != 200:
                    studio_id = new_value
                else:
                    item_details = response.json()
                    studio_id = item_details.get('Id')


                changes["Studios"] = {"Name":new_value, "Id": studio_id}
                item.studio = new_value
                # self.__update_item(item_id,{"CustomRating": new_value})
            self.__update_item(item_id,changes)

        if field_attr in ["audienceRating","rating","userRating","studio","contentRating"]:
            # CustomRating ?
            return

        raise Warning(f"multiEditField not implemented for {rating_keys} - {field_attr} - {new_value} {locked}")

    def multi_edit(self,rating_keys, **kwargs):
        raise Warning(f"multi_edit not implemented for {rating_keys} - {kwargs}")

        # raise Warning(f"multi_edit not implemented for {new_studio}")

    def editItemTitle(self, ratingKey, new_title):
        raise Warning(f"editItemTitle not implemented for {ratingKey} - {new_title}")

    # ==== Session einmalig bereitstellen (falls nicht vorhanden) ====
    # ==== HTTP-Session mit Retry/Backoff (einmalig in __init__ oder lazy) ====
    def _ensure_http_session(self):
        if self.session:
            return
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST", "PUT", "PATCH"])
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    # ==== Leichte Normalisierung statt DeepDiff ====
    def _normalize_people_for_compare(self, people_list):
        """
        Vergleicht nur die Felder, die für die Gleichheit relevant sind – in Ordnung (Order zählt).
        Ignoriert 'PrimaryImageTag' und sonstige irrelevante Felder.
        """
        norm = []
        for p in people_list or []:
            norm.append((
                str(p.get("Id") if p.get("Id") is not None else p.get("Name", "")).strip().casefold(),
                (p.get("Name") or "").strip().casefold(),
                p.get("Type") or "",
                (p.get("Role") or "").strip()
            ))
        return norm

    # ==== zentraler Personen-Index je Library+Rolle ====
    def _build_people_index(self, role: str):
        """
        Baut (und cached) einen Index für die Komplettriege der Personen einer Library+Rolle.
        Maps:
          - by_id[str(Id)] -> person-dict
          - by_name[name.casefold()] -> list[person-dict] (für exakte Namensmatches)
          - by_provider[(prov_case, tmdb_id_str)] -> person-dict
        """

        key = f"{role}"
        if key in self.people_index:
            return self.people_index[key]

        # Vollständige Liste einmal ziehen (mit Session & Keep-Alive)
        self._ensure_http_session()
        base_url = self.emby_server_url + "/emby/Persons"
        params = {
            # "ParentId": library_id,
            "PersonTypes": role,
            "Fields": "ProviderIds,ImageTags",
            "api_key": self.api_key,
        }
        try:
            r = self._http_session.get(base_url, headers=self.headers, params=params, timeout=60)
            r.raise_for_status()
            items = r.json().get("Items", [])
        except Exception:
            items = []

        by_id, by_name, by_provider = {}, {}, {}
        for it in items:
            pid = it.get("Id")
            if pid:
                by_id[str(pid)] = it
            name = (it.get("Name") or "").strip()
            if name:
                by_name.setdefault(name.casefold(), []).append(it)
            prov = it.get("ProviderIds") or {}
            for k, v in prov.items():
                if v is None:
                    continue
                by_provider[(str(k).casefold(), str(v))] = it

        idx = {"by_id": by_id, "by_name": by_name, "by_provider": by_provider, "all": items}
        self.people_index[key] = idx
        return idx

    # ==== get_people: nutzt Index & gezielte Suche, aber macht keine Duplikat-Requests mehr ====
    def get_people(self, role: str, person_list=None):
        """
        - Ohne person_list: komplette (gecachte) Liste via Index (ein Request pro Library+Rolle).
        - Mit person_list: exakte Namensmatches aus dem Index, fällt bei Bedarf auf minimale Such-Requests zurück
          (nur wenn wirklich keine Namens-Treffer im Index existieren).
        Cached zusätzlich: self.people_lib_cache[term.lower()]
        """

        idx = self._build_people_index(role)

        # Vollständige Liste
        if not person_list:
            return idx["all"]

        results_by_id = {}
        for term in person_list:
            if not term:
                continue
            search = str(term).strip()
            if not search:
                continue
            ck = search.lower()

            # 1) Cache für gezielte Suchliste?
            if ck in self.people_lib_cache:
                for it in self.people_lib_cache[ck]:
                    if it and it.get("Id"):
                        results_by_id[it["Id"]] = it
                continue

            # 2) Exaktes Namensmatch aus dem Index (0 Requests)
            exact = idx["by_name"].get(ck, [])
            if exact:
                ordered = exact  # exakte Treffer bevorzugen
                self.people_lib_cache[ck] = ordered
                for it in ordered:
                    if it and it.get("Id"):
                        results_by_id[it["Id"]] = it
                continue

            # 3) Fallback: einmalige Emby-Suche mit SearchTerm
            self._ensure_http_session()
            base_url = self.emby_server_url + "/emby/Persons"
            params = {
                "PersonTypes": role,
                "Fields": "ProviderIds,ImageTags",
                "SearchTerm": search,
                "api_key": self.api_key,
            }
            try:
                r = self._http_session.get(base_url, headers=self.headers, params=params, timeout=20)
                r.raise_for_status()
                items = r.json().get("Items", [])
            except Exception:
                items = []

            # Exakte Namens-Treffer bevorzugen
            exact = [p for p in items if (p.get("Name") or "").strip().lower() == ck]
            ordered = exact or items

            # lokalen Index NICHT überschreiben; aber Suchcache füllen
            self.people_lib_cache[ck] = ordered
            for it in ordered:
                if it and it.get("Id"):
                    results_by_id[it["Id"]] = it

        return list(results_by_id.values())
    
    def get_person_by_name(self, person_name):
        """
        - Ohne person_list: komplette (gecachte) Liste via Index (ein Request pro Library+Rolle).
        - Mit person_list: exakte Namensmatches aus dem Index, fällt bei Bedarf auf minimale Such-Requests zurück
          (nur wenn wirklich keine Namens-Treffer im Index existieren).
        Cached zusätzlich: self.people_lib_cache[term.lower()]
        """

        # 3) Fallback: einmalige Emby-Suche mit SearchTerm
        self._ensure_http_session()
        base_url = self.emby_server_url + "/emby/Persons"
        params = {
            "SearchTerm": person_name,
            "Fields": "ProviderIds,ImageTags",
            "api_key": self.api_key,
        }
        try:
            r = self._http_session.get(base_url, headers=self.headers, params=params, timeout=20)
            r.raise_for_status()
            items = r.json().get("Items", [])
        except Exception:
            items = []

        # Exakte Namens-Treffer bevorzugen

        return items

    def _get_person_by_name_cached(self, clean_name: str):
        key = (clean_name or "").strip()
        hit = self.cached_person_names.get(key)
        if hit is None:
            try:
                hit = self.get_person_by_name(key) or []
            except Exception:
                hit = []
            self.cached_person_names[key] = hit
            # if len(self.cached_person_names) > 200_000:
            #     self.cached_person_names.clear()
        return hit

    def get_person_info_via_library(self, role: str, provider: str, tmdb_id: int | str,
                                    person_name: str):
        """
        STRIKTE Disambiguierung für Massenlauf:
          1) exakte Provider-ID im Index? -> sofortiger Treffer
          2) exakter Name im Index und EIN eindeutiger Kandidat -> Treffer
          3) mehrere gleichnamige Kandidaten:
             - behalte nur Kandidaten OHNE abweichende ProviderId (falls vorhanden)
             - wenn danach EIN Kandidat übrig bleibt -> Treffer
             - sonst: KEIN Auto-Link (Platzhalter verwenden)
        Liefert (emby_person_id, linked_bool[=müsste ProviderId gesetzt/ergänzt werden]) oder (None, False).
        """
        prov = (provider or "Tmdb")
        prov_key = prov.casefold()
        tmdb_id_str = str(tmdb_id)
        cache_key = f"{prov}-{tmdb_id_str}"

        def _cand_has_provider(person: dict, prov_key: str, ext_id: str) -> bool:
            pids = person.get("ProviderIds") or {}
            return (pids.get(prov_key) == ext_id) or (pids.get(prov_key.capitalize()) == ext_id)

        def _dedupe_by_id(items):
            seen, out = set(), []
            for it in items or []:
                pid = it.get("Id")
                if pid and pid not in seen:
                    seen.add(pid);
                    out.append(it)
            return out

        if str(tmdb_id) == "64796":
            pass

        # schneller Pos/Neg-Cache
        if cache_key in self.people_cache:
            emby_id = self.people_cache[cache_key]
            return (emby_id, False) if emby_id else (None, False)

        # Index für die Rolle laden
        idx = self._build_people_index(role)

        # 1) Provider-First (perfekt disambiguiert)
        byprov = idx["by_provider"].get((prov_key, tmdb_id_str))
        if byprov and byprov.get("Id"):
            self.people_cache[cache_key] = byprov["Id"]
            # Provider ist schon korrekt -> kein Änderungsbedarf
            return byprov["Id"], False

        # 2) Exakter Namensmatch (nur eindeutige Treffer akzeptieren)
        name_l = (person_name or "").strip().casefold()
        candidates = _dedupe_by_id(idx["by_name"].get(name_l, []))

        if len(candidates) == 1:
            # genau ein Kandidat -> ok
            person = candidates[0]
            person_id = person.get("Id")
            if not person_id:
                self.people_cache[cache_key] = None
                return None, False

            # Prüfe, ob ProviderIds ergänzt werden müssten
            will_change = not _cand_has_provider(person, prov_key, tmdb_id_str)
            self.people_cache[cache_key] = person_id
            return person_id, will_change

        if len(candidates) > 1:
            # 3) Mehrdeutigkeit entschärfen:
            #    Schließe Kandidaten aus, die bereits eine ABWEICHENDE ProviderId für diesen Provider tragen.
            filtered = []
            for p in candidates:
                pids = p.get("ProviderIds") or {}
                # Wenn es bereits eine Tmdb-Id gibt, die NICHT zu tmdb_id_str passt -> Kandidat verwerfen
                if prov in pids or prov_key in pids:
                    if _cand_has_provider(p, prov_key, tmdb_id_str):
                        filtered.append(p)  # passt exakt
                    # sonst raus
                else:
                    # keine Tmdb verknüpft -> neutral (behalten)
                    filtered.append(p)

            filtered = _dedupe_by_id(filtered)

            if len(filtered) == 1:
                person = filtered[0]
                person_id = person.get("Id")
                will_change = not _cand_has_provider(person, prov_key, tmdb_id_str)
                self.people_cache[cache_key] = person_id
                return person_id, will_change

            # weiterhin mehrdeutig -> sicher bleiben, NICHT auto-linken
            self.people_cache[cache_key] = None
            return None, False

        # 4) Gar kein Namensmatch -> kein Auto-Link
        self.people_cache[cache_key] = None
        return None, False

    def get_person_info_bulk(self, tmdb_ids: list, provider: str = "tmdb", chunk_size: int = 200):
        """
        Liefert dict[tmdb_id:int] -> emby_person_id:str.
        - nutzt self.session (Connection-Pooling)
        - bewertet Dupe-Sets nur pro Batch (kein Mehrfach-Demote)
        - wählt die kleinste Emby-ID als kanonisch
        - demote pro falscher PID nur einmal (idempotent)
        - behält Dupe-Listen für Logging/Persistenz bei
        """
        if not tmdb_ids:
            return {}


        # IDs normalisieren
        try:
            norm_ids = sorted({int(x) for x in tmdb_ids if x is not None and str(x).strip() != ""})
        except ValueError:
            norm_ids = sorted({int(x) for x in tmdb_ids if str(x).isdigit()})
        if not norm_ids:
            return {}

        self._ensure_http_session()
        result: dict[int, str] = {}

        base_url = f"{self.emby_server_url}/emby/Users/{self.user_id}/Items"

        # In Batches abfragen und JE Batch separat bewerten/demoten
        for i in range(0, len(norm_ids), chunk_size):
            batch = norm_ids[i:i + chunk_size]
            provider_ids = ",".join(f"{provider}.{pid}" for pid in batch)

            params = {
                "Recursive": "true",
                "Fields": "ProviderIds",
                "IncludeItemTypes": "Person",
                "AnyProviderIdEquals": provider_ids,
                "api_key": self.api_key,
            }

            try:
                resp = self.session.get(base_url, headers=self.headers, params=params, timeout=20)
                resp.raise_for_status()
                payload = resp.json() or {}
            except Exception as e:
                try:
                    logger.warning(f"[get_person_info_bulk] Request-Fehler (Batch {i // chunk_size + 1}): {e}")
                except Exception:
                    pass
                continue

            items = (payload.get("Items") or payload.get("items") or []) or []

            # Batch-lokale Sammelstrukturen
            tmdb_to_ids: dict[int, set[str]] = {}
            tid_to_name: dict[int, str] = {}

            # Treffer sammeln
            for item in items:
                emby_id = item.get("Id")
                if not emby_id:
                    continue
                name = (item.get("Name") or "").strip()
                prov = item.get("ProviderIds") or {}

                # Provider-ID robust lesen (tmdb/Tmdb/TMDb)
                tmdb_id_raw = (
                        prov.get(provider.lower())
                        or prov.get(provider.capitalize())
                        or prov.get("TMDb")
                )
                if tmdb_id_raw is None:
                    continue

                try:
                    tmdb_id = int(tmdb_id_raw)
                except (TypeError, ValueError):
                    continue

                s = tmdb_to_ids.setdefault(tmdb_id, set())
                s.add(str(emby_id))

                if name:
                    prev = tid_to_name.get(tmdb_id)
                    if prev is None or (prev == "John Doe" and name != "John Doe"):
                        tid_to_name[tmdb_id] = name

            # Dupe-Bewertung NUR für diesen Batch
            for tid, idset in tmdb_to_ids.items():
                ids_sorted = sorted({str(x) for x in idset}, key=lambda x: int(x))  # numerische Sortierung
                chosen = ids_sorted[0]
                result[tid] = chosen

                if len(ids_sorted) > 1:
                    # Dupe-Infos für Logs/Persistenz
                    try:
                        tid_int = int(tid)
                    except Exception:
                        tid_int = tid
                    self._person_dupes_last[tid_int] = ids_sorted
                    self._person_dupes_choice_last[tid_int] = chosen

                    # Persistentes Mapping (gewollt hart abbrechen auf Fehler)
                    try:
                        self.config.Cache.update_tmdb_person_map(
                            expired=False,
                            tmdb_id=int(tid),
                            emby_id=str(chosen),
                            expiration=self.config.Cache.expiration
                        )
                    except Exception:
                        raise Failed
                        pass  # bewusst beibehalten

                    # Nicht-kanonische Personen demoten (pro PID nur einmal)
                    wrong_ids = ids_sorted[1:]
                    for wrong_pid in wrong_ids:
                        if wrong_pid in self._person_already_demoted:
                            continue
                        try:
                            self._demote_duplicate_person(wrong_pid)
                            self._person_already_demoted.append(wrong_pid)
                            try:
                                logger.info(f"[get_person_info_bulk] Demoted person Emby id {wrong_pid}")
                            except Exception:
                                pass
                        except Exception as e:
                            try:
                                logger.warning(f"[get_person_info_bulk] demote failed for pid={wrong_pid}: {e}")
                            except Exception:
                                pass

                    # Zusammenfassung loggen
                    pname = tid_to_name.get(tid)
                    label = f"{tid} - {pname}" if pname else f"{tid}"
                    try:
                        logger.warning(
                            f"[get_person_info_bulk] TMDb-Person-ID {label} ist mehreren Emby-IDs zugeordnet: "
                            f"{ids_sorted}. Verwende {chosen}; demoted {wrong_ids}"
                        )
                    except Exception:
                        pass

        return result

    def _strip_alias_suffix(self, name: str, tmdb_id) -> str:
        s = (name or "").strip()
        if not s or not s.endswith(tmdb_id):
            return s
        while s.endswith(tmdb_id):
            s = s[:-len(tmdb_id)]
        return s.strip()

    def _norm_name(self, s: str) -> str:
        import unicodedata
        s = unicodedata.normalize("NFKD", s or "")
        s = "".join(c for c in s if not unicodedata.combining(c))
        return _re.sub(r"\s+", " ", s).strip().casefold()

    def _attach_tmdb_to_person(self, emby_person_id: str, tmdb_id: int) -> None:
        if not (emby_person_id and tmdb_id):
            return
        self._ensure_http_session()
        url = f"{self.emby_server_url}/emby/Items/RemoteSearch/Apply/{emby_person_id}"
        params = {"api_key": self.api_key}
        data = {"ProviderIds": {"tmdb": str(tmdb_id)}}
        try:
            self.session.post(url, headers=self.headers, params=params, json=data, timeout=20)
        except Exception:
            pass

    def _demote_duplicate_person(self, emby_person_id: str) -> None:
        try:
            logger.info(f"Cleared person {emby_person_id} and renamed to 'John Doe'")

            self.update_item(emby_person_id, {"Id": emby_person_id, "Name": "John Doe", "ProviderIds": {}})
        except Exception:
            pass

    # ==== build_emby_people_from_tmdb: unverändert in Logik, aber ohne unnötige Requests ====
    def build_emby_people_from_tmdb(self, my_cast, my_crew, provider: str = "tmdb"):
        """
        Baut die gewünschte Emby-Personenliste (Cast + Crew) auf Basis von TMDb-Daten.
        Nutzt Bulk-Lookup gegen Emby (self.get_person_info_bulk) und aktualisiert einen Cache:
            self.cached_tmdb_ids: dict[int -> str]  (tmdb_id -> emby_id)
            self.missing_tmdb_ids: set[int]         (tmdb_ids, die in Emby nicht existieren)
        """

        # ------- Job-Mapping (Type + optionale Crew-Role) -------
        # Schlüssel immer lower-case!
        job_to_type_role = {
            # Director
            "director": ("Director", None),

            # Writers
            "writer": ("Writer", "Autor"),
            "screenplay": ("Writer", None),
            "screenwriter": ("Writer", None),
            "teleplay": ("Writer", None),
            "author": ("Writer", "Autor"),
            "novel": ("Writer", "Romanvorlage"),
            "adaptation": ("Writer", "Adaption"),
            "story": ("Writer", "Story"),
            "comic book": ("Writer", "Comicvorlage"),
            "original story": ("Writer", "Story"),
            "theatre play": ("Writer", "Theaterstück"),

            # Music
            "composer": ("Composer", None),
            "original music composer": ("Composer", "Filmmusik"),
            "lyricist": ("Lyricist", None),
            "songs": ("Lyricist", "Songs"),  # dein Beispiel
            "theme song performance": ("Lyricist", "Theme Song"),  # dein Beispiel

            # Other crew types you already support
            "producer": ("Producer", None),
            "conductor": ("Conductor", None),
        }
        allowed_jobs = set(job_to_type_role.keys())

        def map_job(job: str):
            jl = (job or "").strip().lower()
            return job_to_type_role.get(jl)  # -> (etype, role) oder None

        # ---------- Dedup-Key jetzt inkl. Role ----------
        def key_for(emby_id, name, etype, role):
            # bevorzugt ID, sonst Name (casefold). Role ist Teil der Identität.
            return (("id", str(emby_id)) if emby_id else ("name", (name or "").casefold()), etype, (role or None))

        per_key = {}
        ordered_cast = []
        crew_buckets = {"Director": [], "Writer": [], "Producer": [], "Composer": [], "Conductor": [], "Lyricist": []}

        # --- Robuste Filter ---
        cast_filtered = [
            a for a in (my_cast or [])
            if not _re.search(r"\buncredited\b", (a.get("character") or ""), flags=_re.IGNORECASE)
        ]
        crew_filtered = [
            m for m in (my_crew or [])
            if (m.get("job") and (m.get("job").strip().lower() in allowed_jobs))
        ]

        # --- IDs sammeln (aus bereits gecachten Listen) ---
        tmdb_ids = [c.get("person_id") for c in (cast_filtered + crew_filtered) if c.get("person_id")]
        tmdb_ids = [int(t) for t in tmdb_ids if str(t).isdigit()]

        # --- 1) DB-Cache vorwärmen: emby_id + alias ---
        db_map, db_missing, db_expired = (
            self.config.Cache.query_tmdb_person_map_bulk(tmdb_ids, 3)
            if self.config and self.config.Cache else ({}, set(tmdb_ids), set())
        )
        # for tid, rec in db_map.items():
        #     l = rec.get("emby_id")
        #     if l and tid not in self.cached_tmdb_ids.keys() and tid not in db_expired:
        #         self.cached_tmdb_ids[tid] = rec["emby_id"]

        # --- Cache-Validierung nur für die in diesem Lauf benötigten Mappings ---
        def _validate_cached_person_mappings_local(t2e: dict):
            if not t2e:
                return set()
            emby_ids = sorted({str(e) for e in t2e.values() if e})
            items = []
            CHUNK = 100
            for i in range(0, len(emby_ids), CHUNK):
                chunk = ",".join(emby_ids[i:i + CHUNK])
                endpoint = f"/emby/Items?Ids={chunk}&Fields=ProviderIds,Type,Id&api_key={self.api_key}"
                url = self.emby_server_url + endpoint
                try:
                    r = requests.get(url, headers=self.headers, timeout=10)
                    data = r.json() or {}
                    items.extend(data.get("Items") or data.get("items") or [])
                except Exception as e:
                    try:
                        logger.error(e)
                    except Exception:
                        pass
            by_id = {str(it.get("Id")): it for it in items if it and it.get("Id") is not None}
            stale = set()
            provider_key = "Tmdb" if (provider or "").lower() == "tmdb" else provider
            for tid, eid in t2e.items():
                it = by_id.get(str(eid))
                if not it or it.get("Type") != "Person":
                    stale.add(tid);
                    continue
                prov = it.get("ProviderIds") or {}
                v1 = str(prov.get(provider_key))
                v2 = str(prov.get(provider_key + "Id"))
                if str(tid) not in {v1, v2}:
                    stale.add(tid)
            for tid in stale:
                self.cached_tmdb_ids.pop(tid, None)
                try:
                    if self.config and self.config.Cache:
                        self.config.Cache.update_tmdb_person_map(
                            expired=True, tmdb_id=int(tid), emby_id=None, expiration=self.config.Cache.expiration
                        )
                except Exception:
                    pass
            return stale

        # needed_cached_map = {tid: self.cached_tmdb_ids.get(tid) for tid in tmdb_ids if tid in self.cached_tmdb_ids}
        # stale_due_validation = _validate_cached_person_mappings_local(needed_cached_map)

        # --- 2) Nur fehlende/abgelaufene gegen Emby auflösen ---
        to_resolve = sorted({
            tid for tid in tmdb_ids
            if (tid not in self.cached_tmdb_ids) or (tid in db_expired)
        })
        # to_resolve = tmdb_ids
        resolved = {}
        if to_resolve:
            try:
                resolved = self.get_person_info_bulk(to_resolve, provider=provider)  # {tmdb_id:int -> emby_id:str}
            except Exception as e:
                logger.error(e)
                resolved = {}
        if resolved:
            self.cached_tmdb_ids.update({int(k): str(v) for k, v in resolved.items()})
        # === Aktuelle Emby-Namen prefetchen ===
        needed_emby_ids =[]
        for my_tmdb_id in tmdb_ids:
            if int(my_tmdb_id) in self.cached_tmdb_ids.keys():
                needed_emby_ids.append(self.cached_tmdb_ids.get(int(my_tmdb_id), ""))
        # known_emby_ids = list({str(v) for v in self.cached_tmdb_ids.values()})
        emby_name_by_id = {}
        if needed_emby_ids:
            try:
                id_to_item = self.get_items_bulk(needed_emby_ids)
            except Exception:
                id_to_item = {}
            for pid, item in (id_to_item or {}).items():
                nm = item.get("Name")
                if nm:
                    emby_name_by_id[str(pid)] = nm
        pass
        # Map TMDb -> aktueller Emby-Name (falls vorhanden)
        # emby_name_by_tid = {}
        # for tid, pid in self.cached_tmdb_ids.items():
        #     nm = emby_name_by_id.get(str(pid))
        #     if nm:
        #         try:
        #             # emby_name_by_tid[int(tid)] = nm
        #         # except Exception:
        #             pass

        # =================
        # ----- CAST ------
        # =================
        for c in (cast_filtered or []):
            tmdb_id = c.get("person_id")
            name = c.get("name")
            role = c.get("character") or None
            if not tmdb_id or not name:
                continue

            try:
                tmdb_id_int = int(tmdb_id)
            except Exception:
                tmdb_id_int = None

            emby_id = self.cached_tmdb_ids.get(tmdb_id_int if tmdb_id_int is not None else tmdb_id)

            # Emby-ID bekannt? → aktuellen Emby-Namen verwenden
            if emby_id:
                entry_name = emby_name_by_id.get(str(emby_id)) or name
                try:
                    self.ensure_person_latin_name(str(emby_id),
                                                  int(tmdb_id_int if tmdb_id_int is not None else tmdb_id),
                                                  entry_name)
                except Exception:
                    pass
            else:
                entry_name = name

            if not emby_id:
                # Platzhalter deduplizieren (inkl. Role)
                k_name = key_for(None, entry_name, "Actor", role)
                if k_name not in per_key:
                    entry = {"Id": entry_name, "Name": entry_name, "Type": "Actor", "Tmdb": tmdb_id}
                    if role:
                        entry["Role"] = role
                    per_key[k_name] = entry
                    ordered_cast.append(entry)
                else:
                    if role and "Role" not in per_key[k_name]:
                        per_key[k_name]["Role"] = role
                continue

            # Emby-ID vorhanden → über ID deduplizieren (inkl. Role)
            k_id = key_for(emby_id, entry_name, "Actor", role)
            k_name = key_for(None, entry_name, "Actor", role)
            if k_name in per_key:
                entry = per_key.pop(k_name)
                entry["Id"] = str(emby_id)
                entry["Name"] = entry_name
                entry["Tmdb"] = tmdb_id
                per_key[k_id] = entry
            elif k_id not in per_key:
                entry = {"Id": str(emby_id), "Name": entry_name, "Type": "Actor", "Tmdb": tmdb_id}
                if role:
                    entry["Role"] = role
                per_key[k_id] = entry
                ordered_cast.append(entry)
            else:
                if role and "Role" not in per_key[k_id]:
                    per_key[k_id]["Role"] = role

        # =================
        # ----- CREW ------
        # =================
        for m in (crew_filtered or []):
            tmdb_id = m.get("person_id")
            name = m.get("name")
            mapped = map_job(m.get("job"))
            if not (tmdb_id and name and mapped):
                continue

            etype, crew_role = mapped  # z.B. ("Writer", "Screenplay") oder ("Writer", None)

            try:
                tmdb_id_int = int(tmdb_id)
            except Exception:
                tmdb_id_int = None

            emby_id = self.cached_tmdb_ids.get(tmdb_id_int if tmdb_id_int is not None else tmdb_id)

            if emby_id:
                entry_name = emby_name_by_id.get(str(emby_id)) or name
                try:
                    self.ensure_person_latin_name(str(emby_id),
                                                  int(tmdb_id_int if tmdb_id_int is not None else tmdb_id),
                                                  entry_name)
                except Exception:
                    pass
            else:
                entry_name = name

            if not emby_id:
                k_name = key_for(None, entry_name, etype, crew_role)
                if k_name not in per_key:
                    entry = {"Id": entry_name, "Name": entry_name, "Type": etype, "Tmdb": tmdb_id}
                    if crew_role:
                        entry["Role"] = crew_role
                    per_key[k_name] = entry
                    crew_buckets[etype].append(entry)
                continue

            k_id = key_for(emby_id, entry_name, etype, crew_role)
            k_name = key_for(None, entry_name, etype, crew_role)
            if k_name in per_key:
                entry = per_key.pop(k_name)
                entry["Id"] = str(emby_id)
                entry["Name"] = entry_name
                entry["Tmdb"] = tmdb_id
                if crew_role:
                    entry["Role"] = crew_role
                per_key[k_id] = entry
            elif k_id not in per_key:
                entry = {"Id": str(emby_id), "Name": entry_name, "Type": etype, "Tmdb": tmdb_id}
                if crew_role:
                    entry["Role"] = crew_role
                per_key[k_id] = entry
                crew_buckets[etype].append(entry)

        desired = []
        desired.extend(ordered_cast)
        for t in ("Director", "Writer", "Producer", "Composer", "Conductor", "Lyricist"):
            desired.extend(crew_buckets[t])

        return desired

    # --- Helfer: Akzente entfernen (für SortName o.ä.) ---
    def _strip_accents(self, s: str) -> str:
        if not s:
            return s
        return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

    def _compute_sort_name(self, name: str) -> str:
        # einfache, robuste Sortierform: akzentfrei
        return self._strip_accents(name or "").strip()

    # --- Helfer: Vergleichssignatur ohne Name (nur Id/Type/Role & Reihenfolge) ---
    def _people_signature_no_name(self, people_list):
        return [
            (
                str(p.get("Id") or ""),
                p.get("Type") or "",
                (p.get("Role") or None)
            )
            for p in (people_list or [])
        ]

    # --- Helfer: Finde reine Namens-Abweichungen (mapping über Id) ---
    def _collect_person_name_fixes(self, current_people, desired_people):
        desired_by_id = {
            str(p.get("Id")): (p.get("Name") or "")
            for p in (desired_people or [])
            if p.get("Id") is not None
        }
        fixes = []  # [(person_id:str, desired_name:str)]
        for p in (current_people or []):
            pid = str(p.get("Id") or "")
            if not pid or pid not in desired_by_id:
                continue
            cur_name = p.get("Name") or ""
            des_name = desired_by_id[pid]
            if des_name and cur_name != des_name:
                fixes.append((pid, cur_name, des_name))
        return fixes

    # --- Helfer: Person direkt korrigieren (verwendet deine update_item) ---
    def _update_person_name_if_needed(self, person_id: str, desired_name: str):
        # Optional: einmal pro Lauf fixen
        if person_id in self._person_name_fix_cache:
            return None

        payload = {
            "Name": desired_name,
            # sinnvolle Sortierung ohne Akzente
            "ForcedSortName": self._compute_sort_name(desired_name),
        }
        resp = self.update_item(person_id, payload)
        self._person_name_fix_cache.add(person_id)
        return resp

    @property
    def items_cache(self):
        """
        Lazy-initialized Item-Cache.
          - _items_cache:        id -> zuletzt gemergtes Item-Dict
          - _items_cache_fields: id -> Set[str] der vorhandenen Fields
          - _items_cache_ts:     id -> float (Unix-Zeitpunkt des letzten Refresh)
          - items_cache_ttl:     Sekunden, die ein Cache-Eintrag als 'frisch' gilt (Default 300)
        """
        return self._items_cache

    # ==== Bulk-Fetch: /emby/Items?Ids=...&Fields=... ====
    # ==== Bulk-Fetch: /emby/Items?Ids=...&Fields=... ====
    def get_items_bulk(self, ids: list[str], fields: list[str] | None = None) -> dict[str, dict]:
        """
        Holt Emby-Items in Batches (Ids=...), gibt dict[id] -> item zurück.
        Nutzt einen lokalen Cache, lädt nur fehlende/abgelaufene/unvollständige Einträge nach.
        """
        import time  # lokal, um keine Modulweite Änderung zu erzwingen

        self._ensure_http_session()

        if not ids:
            return {}

        # Nur numerische/echte IDs abfragen (Platzhalter-Namen überspringen)
        fetch_ids_all = [str(i) for i in ids if str(i).isdigit()]
        if not fetch_ids_all:
            return {}

        # Felder normalisieren (Mengenvergleich), Request-Parameter aber in stabiler Reihenfolge senden
        fields = fields or []
        req_fields_set = {f for f in fields if f}
        fields_param = ",".join(sorted(req_fields_set)) if req_fields_set else ""

        CHUNK = 200  # konservativ; Emby kommt damit gut klar
        out: dict[str, dict] = {}

        now = time.time()
        ttl = getattr(self, "items_cache_ttl", 300)

        def is_fresh(ts: float) -> bool:
            if not ttl:
                return True  # ttl == 0 => nie ablaufen lassen
            return (now - ts) <= ttl

        # 1) Aufteilen in bekannte (frisch + Feld-Superset) und nachzuladende IDs
        to_fetch: list[str] = []
        for id_ in fetch_ids_all:
            cached_item = self._items_cache.get(id_)
            cached_fields = self._items_cache_fields.get(id_, set())
            ts = self._items_cache_ts.get(id_, 0.0)

            if cached_item and is_fresh(ts) and req_fields_set.issubset(cached_fields):
                out[id_] = cached_item
            else:
                to_fetch.append(id_)

        # 2) Fehlende/nicht vollständige Items in Batches nachladen
        if to_fetch:
            url = f"{self.emby_server_url}/emby/Items"
            for i in range(0, len(to_fetch), CHUNK):
                batch = to_fetch[i:i + CHUNK]
                params = {"Ids": ",".join(batch), "api_key": self.api_key}
                if fields_param:
                    params["Fields"] = fields_param

                resp = self.session.get(url, headers=self.headers, params=params, timeout=20)
                resp.raise_for_status()
                data = resp.json() or {}
                items = data.get("Items") or data.get("items") or []

                now_fetch = time.time()
                for it in items:
                    it_id = str(it.get("Id") or "")
                    if not it_id:
                        continue

                    # Bestehendes Cache-Objekt erweitern/überschreiben (merge)
                    if it_id in self._items_cache:
                        self._items_cache[it_id].update(it)
                        # wir wissen, dass mindestens die angeforderten Fields zurückkamen:
                        self._items_cache_fields[it_id] |= req_fields_set
                    else:
                        self._items_cache[it_id] = it
                        self._items_cache_fields[it_id] = set(req_fields_set)

                    self._items_cache_ts[it_id] = now_fetch
                    out[it_id] = self._items_cache[it_id]

        return out

    # ==== Provider-IDs normalisieren ====
    def _norm_provider_ids(self, provider_ids: dict | None):
        """Gibt (lowercased_dict, tmdb_id_str|None) zurück."""
        d = {(k or "").lower(): v for k, v in (provider_ids or {}).items()}
        # Manche Emby-Instanzen speichern als int; alles in str
        tmdb_val = d.get("tmdb") or d.get("tmdbid") or d.get("themoviedb") or None
        tmdb_str = str(tmdb_val) if tmdb_val not in (None, "", 0) else None
        return d, tmdb_str


    def sync_people(self, emby_item: dict, my_cast: list, my_crew: list):
        # ---------- Init ----------
        changed = False
        log = {
            "tmdb_added": [],
            "aliases_prepared": [],
            "aliases_reverted": [],
            "demoted": [],
            "created": [],
            "created_pending": 0,
            "namefix": [],  # keine Sofort-Namefixes
            "item_updated": False,
        }

        # interne Caches (einmalig pro Prozesslauf)

        def _cheap_key(lst, with_id=False):
            # Multiset über (Type, Role, BaseName) – optional mit Id
            key = {}
            for p in (lst or []):
                typ = p.get("Type") or ""
                role = p.get("Role") or None
                name = (p.get("Name") or "").strip()
                base = _re.sub(r"(?:-\d+)+$", "", name).strip()  # Alias-Suffixe wie "-12345" weg
                k = (typ, role, base) if not with_id else (typ, role, base, str(p.get("Id") or ""))
                key[k] = key.get(k, 0) + 1
            return key

        current_people = emby_item.get("People", []) or []
        desired_people = self.build_emby_people_from_tmdb(my_cast, my_crew, provider="Tmdb")
        # return False, [], []
        # 1) Alias/ID-unabhängige Struktur (Type, Role, BaseName)
        # names_eq = (_cheap_key(current_people, with_id=False) ==
        #             _cheap_key(desired_people, with_id=False))

        # 2) Streng inkl. Id (falls du unterscheiden willst, ob nur Id/Name abweichen)
        # full_eq = (_cheap_key(current_people, with_id=True) ==
        #            _cheap_key(desired_people, with_id=True))

        # if names_eq and full_eq:
        #     # wirklich gar nichts zu tun
        #     return False, [], []

        # ... dein _cheap_key / names_eq / full_eq oben ...

        # if names_eq and not full_eq:
        #     # Schneller „REPLACE-only“-Pfad
        #     people_payload = []
        #     people_alias_revert = []  # (pid, (alias_name, clean_name, tid))
        #     _seen_ar = set()
        #
        #     for dp in (desired_people or []):
        #         typ = dp.get("Type") or ""
        #         role = dp.get("Role")
        #         pid_raw = str(dp.get("Id") or "")
        #         name_raw = (dp.get("Name") or "").strip()
        #         tid = dp.get("Tmdb") or dp.get("tmdb")
        #
        #         # Alias-Basename (entfernt evtl. vorhandene -\d Suffixe)
        #         base = _re.sub(r"(?:-\d+)+$", "", name_raw).strip()
        #
        #         if (not pid_raw.isdigit()) and tid:
        #             # NEU: Nicht-numerische Id -> Alias in Name UND Id schreiben
        #             alias = f"{base}-{int(tid)}"
        #             q = {"Id": alias, "Name": alias, "Type": typ}
        #             if role is not None:
        #                 q["Role"] = role
        #             people_payload.append(q)
        #             # (Noch keine people_alias_revert, da keine numerische PID existiert)
        #             continue
        #
        #         # Standardfall (numerische PID oder kein TMDb vorhanden)
        #         q = {"Id": pid_raw, "Name": name_raw, "Type": typ}
        #         if role is not None:
        #             q["Role"] = role
        #         people_payload.append(q)
        #
        #         # Downstream-Rename einsammeln, falls numerische PID + Alias im Namen
        #         if "-" in name_raw:
        #             base2, suf = name_raw.rsplit("-", 1)
        #             if base2 and suf.isdigit() and pid_raw.isdigit():
        #                 key = (pid_raw, name_raw)
        #                 if key not in _seen_ar:
        #                     _seen_ar.add(key)
        #                     people_alias_revert.append((pid_raw, (name_raw, base2.strip(), suf)))
        #
        #     # Hard-Replace nur wenn PIDs entfernt wurden
        #     prev_ids = {str(p.get("Id") or "") for p in (current_people or [])}
        #     next_ids = {str(p.get("Id") or "") for p in (people_payload or [])}
        #     removed_ids_present = bool(prev_ids - next_ids)
        #
        #     if removed_ids_present and current_people:
        #         try:
        #             self.update_item(emby_item["Id"], {"People": []})
        #         except Exception:
        #             pass
        #
        #     # Zielzustand schreiben
        #     self.update_item(emby_item["Id"], {"People": people_payload})
        #
        #     # Kompakte Edits sind optional – wenn du nichts loggen willst, gib leer zurück
        #     return False, None, people_alias_revert

        # else: Struktur wirklich anders -> normaler (langsamer) Pfad

        # ---- EARLY PATH 2: gleiche Struktur (Type,Role,Basename), aber Id/Name differieren ----



        people_alias_revert = []  # (pid, (alias_name/old_name, clean_name/new_name, tmdb_id))
        _seen_alias_reverts = set()  # (pid, alias_or_old_name)

        # ---- Helpers (keine neuen Imports) ----
        def _alias_parts(name: str):
            s = (name or "").strip()
            if not s:
                return None, None
            s = s.replace("–", "-").replace("—", "-")  # Unicode-Hyphen
            m = _re.match(r"^(?P<clean>.+?)(?:-(?P<tid>\d+))+$", s)
            if not m:
                return None, None
            clean = (m.group("clean") or "").strip()
            tid = m.group("tid")
            return clean, tid

        def _base_name(nm: str) -> str:
            return _re.sub(r"(?:-\d+)+$", "", (nm or "")).strip()

        def _strip_alias_suffix(name, tmdb_id):
            try:
                suf = f"-{int(tmdb_id)}"
            except Exception:
                return (name or "").strip()
            s = (name or "").strip()
            if not s.endswith(suf):
                return s
            while s.endswith(suf):
                s = s[: -len(suf)]
            return s.strip()

        def _alias_once(name, tmdb_id):
            base = _strip_alias_suffix(name, tmdb_id)
            try:
                return f"{base}-{int(tmdb_id)}"
            except Exception:
                return base

        def _pid_tmdb_from_bulk(bulk_map, pid: str):
            it = bulk_map.get(str(pid)) or {}
            prov, e_tmdb = self._norm_provider_ids(it.get("ProviderIds"))
            return e_tmdb

        def _tmdb_from_person_hit(hit):
            prov, e_tmdb = self._norm_provider_ids((hit or {}).get("ProviderIds"))
            return e_tmdb

        def _hard_replace_people(item_id: str, people: list):
            """setzt People exakt (kein Merge)"""
            try:
                self.update_item(item_id, {"People": []})
            except TypeError:
                self.update_item(item_id, {"People": []})
            self.update_item(item_id, {"People": people})

        # ---------- Crash-Recovery: vorhandene Aliase vormerken (sehr billig) ----------
        for p in (current_people or []):
            nm = (p.get("Name") or "").strip()
            clean, tid = _alias_parts(nm)
            if not (clean and tid):
                continue
            pid = str(p.get("Id") or "")
            if not pid:
                continue
            key = (pid, nm)
            if key in _seen_alias_reverts:
                continue
            people_alias_revert.append((pid, (nm, clean, tid)))
            _seen_alias_reverts.add(key)

        # ---------- Super-schneller Fast-Path (No-Op) ----------
        # Wenn Struktur & Basenamen 1:1 gleich sind, können wir vorzeitig raus.
        def _cheap_key(lst):
            # (Type, Id, Role, BaseName(Name)) -> Set
            out = set()
            for p in (lst or []):
                out.add((
                    p.get("Type") or "",
                    str(p.get("Id") or ""),
                    p.get("Role") or None,
                    _base_name(p.get("Name")),
                ))
            return out

        if _cheap_key(current_people) == _cheap_key(desired_people):
            # Nichts zu tun – auch keine teuren lookups nötig
            return False, [], people_alias_revert

        # ---------- PHASE A: Duplikate (gleiche TMDb) vorbereiten (per Cache) ----------
        numeric_pids = set(
            [str(p.get("Id")) for p in current_people if str(p.get("Id") or "").isdigit()] +
            [str(p.get("Id")) for p in desired_people if str(p.get("Id") or "").isdigit()]
        )
        missing = [pid for pid in numeric_pids if pid not in self._bulk_person_cache]
        if missing:
            fetched = self.get_items_bulk(sorted(missing), fields=["ProviderIds", "Name"]) or {}
            # cache auffüllen
            for k, v in (fetched or {}).items():
                self._bulk_person_cache[str(k)] = v
        # lokales Bild zusammensetzen
        id_to_item = {pid: self._bulk_person_cache.get(pid, {}) for pid in numeric_pids}

        desired_pid_by_tmdb = {}
        for dp in (desired_people or []):
            tid = dp.get("Tmdb") or dp.get("tmdb")
            pid = str(dp.get("Id") or "")
            if tid and str(pid).isdigit() and (tid not in desired_pid_by_tmdb):
                try:
                    desired_pid_by_tmdb[int(tid)] = pid
                except Exception:
                    pass

        tmdb_groups = {}
        for pid in numeric_pids:
            tmdb_id = _pid_tmdb_from_bulk(id_to_item, pid)
            if not tmdb_id:
                continue
            k = str(tmdb_id)
            tmdb_groups.setdefault(k, set()).add(str(pid))

        # Demote führen wir SPÄTER aus (nach dem Film-Write) und nie für PIDs, die verwendet werden.

        # ---------- PHASE B: Vergleichs-Signaturen (ohne Namen) ----------
        current_people_norm = list(current_people)
        cur_sig = self._people_signature_no_name(current_people_norm)
        des_sig = self._people_signature_no_name(desired_people)

        # Index aktuelle Personen nach (Type,Role,BaseName)
        cur_idx = {
            (p.get("Type") or "", p.get("Role") or None, _base_name(p.get("Name"))): p
            for p in current_people_norm
        }

        # ---------- PHASE C: TMDb an bestehender Person ergänzen (idempotent) ----------
        for dp in desired_people:
            key = (dp.get("Type") or "", dp.get("Role") or None, _base_name(dp.get("Name")))
            cp = cur_idx.get(key)
            if not cp:
                continue
            dp_tmdb = dp.get("Tmdb") or dp.get("tmdb")
            if not dp_tmdb:
                continue
            cp_id = str(cp.get("Id") or "")
            dp_id = str(dp.get("Id") or "")
            if cp_id != dp_id or not cp_id.isdigit():
                continue
            e_tmdb = _pid_tmdb_from_bulk(id_to_item, cp_id)
            if not e_tmdb:
                # nur schreiben, wenn wirklich fehlt
                self.update_item(cp_id, {"Id": cp_id, "ProviderIds": {"Tmdb": str(dp_tmdb)}})
                log["tmdb_added"].append((cp_id, key[2], dp_tmdb))
                changed = True

        # ---------- PHASE D: temporäre Aliase nur wenn nötig ----------
        # Name->PID Index (Alias + Basename mappen)
        cur_by_name = {}
        for p in (current_people or []):
            nm = (p.get("Name") or "").strip()
            pid = str(p.get("Id") or "")
            if not nm:
                continue
            cur_by_name[nm] = pid
            base = _base_name(nm)
            if base and base != nm and base not in cur_by_name:
                cur_by_name[base] = pid

        # Name -> Menge unterschiedlicher Ziel-IDs
        name_to_target_ids = {}
        for dp in (desired_people or []):
            tid = dp.get("Tmdb") or dp.get("tmdb")
            clean = _strip_alias_suffix(dp.get("Name") or "", tid)
            pid = str(dp.get("Id") or "")
            target = pid if pid.isdigit() else (f"{clean}-{tid}" if tid else clean)
            s = name_to_target_ids.get(clean)
            if s is None:
                s = set()
                name_to_target_ids[clean] = s
            s.add(target)
        need_alias_names = {nm for nm, ids in name_to_target_ids.items() if len(ids) > 1}

        # Kandidaten für globale Dubletten nur einmal pro Name suchen (Cache)
        def _global_hits_for(clean_name: str):
            if clean_name in self._person_name_cache:
                return self._person_name_cache[clean_name]
            try:
                hits = self.get_person_by_name(clean_name) or []
            except Exception:
                hits = []
            self._person_name_cache[clean_name] = hits
            return hits

        temp_renames = {}  # emby_pid -> (alias_name, clean_name, tmdb)
        people_payload = []  # gewünschte Liste (ohne Tmdb-Key)

        for dp in (desired_people or []):
            pid = str(dp.get("Id") or "")
            typ = dp.get("Type") or ""
            role = dp.get("Role")
            tid = dp.get("Tmdb") or dp.get("tmdb")
            clean = _strip_alias_suffix(dp.get("Name") or "", tid)

            if not pid.isdigit():
                if not tid:
                    continue
                alias = _alias_once(clean, tid)
                q = {"Id": alias, "Name": alias, "Type": typ}
                if role:
                    q["Role"] = role
                people_payload.append(q)
                continue

            need_alias = False
            if clean in need_alias_names:
                need_alias = True
            if not need_alias:
                cur_pid = cur_by_name.get(clean)
                if cur_pid and cur_pid != pid:
                    need_alias = True
                    self._demote_duplicate_person(cur_pid)
            if not need_alias:
                cur_pid = cur_by_name.get(clean)
                if (not cur_pid) or (cur_pid != pid):
                    for it in _global_hits_for(clean):
                        if (it.get("Name") or "") != clean:
                            continue
                        hit_id = str(it.get("Id") or "")
                        if hit_id == pid:
                            continue
                        hit_tmdb = _tmdb_from_person_hit(it)
                        if hit_tmdb and tid and str(hit_tmdb) != str(tid):
                            need_alias = True
                            break

            if need_alias and tid:
                alias = _alias_once(clean, tid)
                temp_renames[pid] = (alias, clean, tid)
                q = {"Id": pid, "Name": alias, "Type": typ}
            else:
                q = {"Id": pid, "Name": clean, "Type": typ}
            if role:
                q["Role"] = role
            people_payload.append(q)

        # ----- Update-Entscheidung (idempotent) -----
        def _namekey(lst):
            def _norm_role(r): return "" if r is None else str(r)

            out = []
            for p in (lst or []):
                out.append((
                    str(p.get("Type") or ""),
                    str(p.get("Id") or ""),
                    _norm_role(p.get("Role")),
                    (p.get("Name") or "").strip(),
                ))
            out.sort()
            return out

        current_namekey = _namekey(current_people)
        desired_namekey = _namekey(people_payload)

        need_struct_update = (cur_sig != des_sig) or any(not str(p.get("Id") or "").isdigit() for p in people_payload)
        need_name_update = (current_namekey != desired_namekey)
        need_item_update = need_struct_update or need_name_update

        # 3) Demote jetzt, aber nie PIDs demoten, die wir eben verwenden
        used_pids_now = {str(p.get("Id") or "") for p in (people_payload or [])}
        for tmdb_id, pids in tmdb_groups.items():
            if len(pids) <= 1:
                continue
            # Kanonische PID wählen
            canonical = None
            try:
                t_int = int(tmdb_id)
            except Exception:
                t_int = None
            if t_int is not None:
                cand = desired_pid_by_tmdb.get(t_int)
                if cand and cand in pids:
                    canonical = cand
            if not canonical:
                canonical = sorted(pids, key=lambda s: int(s))[0]
            for pid in pids:
                if pid == canonical or pid in used_pids_now:
                    continue
                # idempotent: nur setzen, wenn Name nicht schon "John Doe" oder ProviderIds nicht leer
                cur_it = self._bulk_person_cache.get(pid) or {}
                cur_nm = (cur_it.get("Name") or "").strip()
                cur_pids = (cur_it.get("ProviderIds") or {}) or {}
                if cur_nm == "John Doe" and not cur_pids:
                    continue
                payload = {"Id": pid, "Name": "John Doe", "PrimaryImageTag": None, "ProviderIds": {}}
                self.update_item(pid, payload)
                # Cache anpassen
                self._bulk_person_cache[pid] = {"Name": "John Doe", "ProviderIds": {}}
                log["demoted"].append((tmdb_id, pid))
                changed = True

        if need_item_update:
            # 1) Aliase setzen (nur wenn nötig; idempotent)
            for emby_pid, (alias_name, clean_name, tid) in temp_renames.items():
                # idempotent: nur schreiben, wenn Name != alias_name
                cur_info = self._bulk_person_cache.get(str(emby_pid)) or {}
                cur_name_now = (cur_info.get("Name") or "").strip()
                if cur_name_now != alias_name:
                    if not self.update_item(emby_pid, {"Id": emby_pid, "Name": alias_name, "ProviderIds": {"Tmdb": tid}}):
                        continue
                    # Cache aktualisieren, um Folge-Calls zu sparen
                    cur_info = dict(cur_info)
                    cur_info["Name"] = alias_name
                    cur_info["ProviderIds"] = {"Tmdb": tid}
                    self._bulk_person_cache[str(emby_pid)] = cur_info
                    log["aliases_prepared"].append((emby_pid, alias_name))
                    changed = True

                key = (str(emby_pid), alias_name)
                if key not in _seen_alias_reverts:
                    people_alias_revert.append(
                        (str(emby_pid), (alias_name, clean_name, str(tid) if tid is not None else None)))
                    _seen_alias_reverts.add(key)

            # 2) Film-Update EXAKT (kein Merge), aber nur wenn wirklich unterschiedlich
            _hard_replace_people(emby_item["Id"], people_payload)
            log["item_updated"] = True
            changed = True


        # ---------- PHASE E: Name-Fixes (nur sammeln; keine Sofort-Updates) ----------
        def _is_alias_name(nm: str) -> bool:
            s = (nm or "").strip()
            if "-" in s:
                suf = s.rsplit("-", 1)[-1]
                return suf.isdigit()
            return False

        has_aliases = any(_is_alias_name(p.get("Name")) for p in (people_payload or []))
        cur_sig2 = self._people_signature_no_name(people_payload)
        des_sig2 = self._people_signature_no_name(desired_people)

        if (cur_sig2 == des_sig2) and not has_aliases:
            tmdb_by_pid = {
                str(p.get("Id")): p.get("Tmdb")
                for p in desired_people
                if str(p.get("Id") or "").isdigit() and p.get("Tmdb")
            }
            desired_for_namefix = []
            for dp in desired_people:
                nm = dp.get("Name") or ""
                tid = dp.get("Tmdb")
                if tid and str(nm).endswith(f"-{tid}"):
                    dp2 = dict(dp)
                    dp2["Name"] = nm[:-(len(str(tid)) + 1)]
                    desired_for_namefix.append(dp2)
                else:
                    desired_for_namefix.append(dp)

            fixes = self._collect_person_name_fixes(current_people_norm, desired_for_namefix) or []
            for pid, cur_name, new_name in fixes:
                tid = tmdb_by_pid.get(str(pid))
                tid_str = str(tid) if tid is not None else None
                clean_cur, tid_cur = _alias_parts(cur_name)
                if clean_cur:
                    key = (str(pid), cur_name)
                    if key not in _seen_alias_reverts:
                        people_alias_revert.append((str(pid), (cur_name, clean_cur, tid_cur or tid_str)))
                        _seen_alias_reverts.add(key)
                    continue
                key = (str(pid), cur_name)
                if key not in _seen_alias_reverts:
                    people_alias_revert.append((str(pid), (cur_name, new_name, tid_str)))
                    _seen_alias_reverts.add(key)
                # kein sofortiges Update

        # ---------- Defensiver Fallback: finalen Payload scannen ----------
        try:
            for p in (people_payload or []):
                pid = str(p.get("Id") or "")
                nm = (p.get("Name") or "").strip()
                clean, tid = _alias_parts(nm)
                if pid.isdigit() and clean and tid:
                    key = (pid, nm)
                    if key not in _seen_alias_reverts:
                        people_alias_revert.append((pid, (nm, clean, tid)))
                        _seen_alias_reverts.add(key)
        except Exception:
            pass

        # ---------- Zusammenfassung ----------
        def build_people_change_events(current_people, desired_people, log=None):
            log = log or {}
            events = []

            def _nm(p):
                return (p.get("Name") or "").strip()

            def _role(p):
                return p.get("Role") or None

            def _type(p):
                return (p.get("Type") or "")

            def _pkey(p):
                return (_type(p), str(p.get("Id") or ""), _role(p))

            def _is_uncredited(p):
                r = (_role(p) or "").lower()
                n = _nm(p).lower()
                return "uncredited" in r or "uncredited" in n

            def _fmt_people_list(persons, limit=6, with_pid=True, with_role=True):
                out = []
                for p in persons[:limit]:
                    parts = [_nm(p)]
                    meta = []
                    if with_role and _role(p):
                        meta.append(f"role={_role(p)}")
                    if with_pid:
                        meta.append(f"pid={p.get('Id')}")
                    if meta:
                        parts.append(f"({', '.join(meta)})")
                    out.append(" ".join(parts))
                if len(persons) > limit:
                    out.append(f"... +{len(persons) - limit} weitere")
                return "; ".join(out)

            def _tr_key(tr):
                typ, role = tr
                return (str(typ or ""), "" if role is None else str(role))

            prev_map = {_pkey(p): p for p in (current_people or [])}
            next_source = desired_people or []  # = people_payload
            next_map = {_pkey(p): p for p in next_source}

            added_keys = list(next_map.keys() - prev_map.keys())
            removed_keys = list(prev_map.keys() - next_map.keys())
            added_people = [next_map[k] for k in added_keys]
            removed_people = [prev_map[k] for k in removed_keys]

            from collections import defaultdict
            add_by_tr = defaultdict(list)
            rem_by_tr = defaultdict(list)
            for p in added_people:
                add_by_tr[(_type(p), _role(p))].append(p)
            for p in removed_people:
                rem_by_tr[(_type(p), _role(p))].append(p)

            replaced_pairs = []
            for tr in sorted(set(add_by_tr.keys()) | set(rem_by_tr.keys()), key=_tr_key):
                adds = add_by_tr.get(tr, [])
                rems = rem_by_tr.get(tr, [])
                while adds and rems:
                    a = adds.pop(0)
                    r = rems.pop(0)
                    replaced_pairs.append((r, a))
                add_by_tr[tr] = adds
                rem_by_tr[tr] = rems

            def _group_by_type(lst):
                g = defaultdict(list)
                for p in (lst or []):
                    g[_type(p)].append(p)
                return g

            grouped_adds = _group_by_type([p for lst in add_by_tr.values() for p in lst])
            grouped_rems = _group_by_type([p for lst in rem_by_tr.values() for p in lst])

            for typ in sorted(grouped_adds.keys(), key=lambda s: s or ""):
                persons = grouped_adds[typ]
                events.append(f"ADD {typ}: " + _fmt_people_list(persons, limit=6, with_pid=True, with_role=True))

            for typ in sorted(grouped_rems.keys(), key=lambda s: s or ""):
                persons = grouped_rems[typ]
                credited = [p for p in persons if not _is_uncredited(p)]
                uncred = [p for p in persons if _is_uncredited(p)]
                if credited:
                    events.append(
                        f"REMOVE {typ}: " + _fmt_people_list(credited, limit=6, with_pid=True, with_role=True))
                if uncred:
                    events.append(f"REMOVE {typ} (uncredited): {len(uncred)} entfernt")

            for r, a in replaced_pairs:
                role_txt = f" role={_role(a)}" if _role(a) else ""
                events.append(
                    f"REPLACE {_type(a)}{role_txt}: {_nm(r)} (pid={r.get('Id')}) -> {_nm(a)} (pid={a.get('Id')})"
                    + (f", tmdb={a.get('Tmdb')}" if a.get('Tmdb') else "")
                )

            tmdb_added = log.get("tmdb_added") or []
            if tmdb_added:
                preview = "; ".join([f"{name} (pid={pid}, tmdb={tm})" for pid, name, tm in tmdb_added[:6]])
                more = f"; ... +{len(tmdb_added) - 6} weitere" if len(tmdb_added) > 6 else ""
                events.append("TMDB_ADD: " + preview + more)

            aliases_prep = log.get("aliases_prepared") or []
            if aliases_prep:
                preview = "; ".join([f"{alias} (pid={pid})" for pid, alias in aliases_prep[:6]])
                more = f"; ... +{len(aliases_prep) - 6} weitere" if len(aliases_prep) > 6 else ""
                events.append("ALIAS_PREPARE: " + preview + more)

            dem = log.get("demoted") or []
            if dem:
                preview = "; ".join([f"tmdb={t} pid={p}" for t, p in dem[:8]])
                more = f"; ... +{len(dem) - 8} weitere" if len(dem) > 8 else ""
                events.append("DEMOTED: " + preview + more)

            if log.get("created_pending"):
                events.append(f"CREATED_PENDING x{int(log['created_pending'])}")

            return events

        # ---------- Return ----------
        # dedupe & sort für saubere Downstream-Liste
        if people_alias_revert:
            dedup = []
            seen = set()
            for pid, (alias, clean, tid) in people_alias_revert:
                key = (str(pid), str(alias))
                if key in seen:
                    continue
                seen.add(key)
                dedup.append((str(pid), (alias, clean, tid)))
            people_alias_revert = sorted(dedup, key=lambda t: (t[1][0].casefold(), t[0]))

        if not changed:
            return False, [], people_alias_revert

        item_edits = build_people_change_events(
            current_people=current_people,
            desired_people=people_payload,  # gegen tatsächlichen Schreibzustand diffen
            log=log
        )
        return True, "; ".join(item_edits), people_alias_revert

    # --- Zeichentests / Normalisierung ---
    def _is_latin_string(self, s: str) -> bool:
        if not s:
            return False
        # akzeptiere Basis- und erweiterte Latin-Blocks + übliche Satzzeichen/Leerzeichen
        return all(
            (('LATIN' in unicodedata.name(ch, '')) or not ch.isalpha())
            for ch in s
        )

    def _ascii_sort(self, s: str) -> str:
        return self._strip_accents(s or '').strip()

    # --- TMDb: helper, robust gegen fehlende Felder ---
    def _tmdb_person_translated_name_en(self, person_id: int | str) -> str | None:
        """
        Holt /person/{id}/translations und gibt data.name für 'en' oder 'en-US' zurück, falls vorhanden.
        """
        try:
            # tmdbapis RAW-V3: person_get_translations
            my_tmdb= self.config.TMDb
            data = my_tmdb.API3.person_get_translations(int(person_id))
            trs = (data or {}).get("translations") or []
            # erst en-US, dann en
            for pref in ("en-US", "en"):
                for t in trs:
                    if (t.get("iso_639_1") == "en" and (t.get("iso_3166_1") in (None, "", "US"))) or \
                            (f'{t.get("iso_639_1", "")}-{t.get("iso_3166_1", "")}' == pref):
                        name = ((t.get("data") or {}).get("name") or "").strip()
                        if name:
                            return name
            # generisch: irgendeine englische Übersetzung
            for t in trs:
                if t.get("iso_639_1") == "en":
                    name = ((t.get("data") or {}).get("name") or "").strip()
                    if name:
                        return name
        except Exception:
            pass
        return None

    def _tmdb_person_alias_latin(self, person_id: int | str) -> str | None:
        """
        Holt /person/{id} (Details) und wählt einen latinischen Alias aus also_known_as.
        """
        try:
            # RAW-V3: person_get_details; language hier egal, Name/Aliase sind nicht lokalisiert
            my_tmdb= self.config.TMDb
            p = my_tmdb.API3.person_get_details(int(person_id))
            aliases = (p or {}).get("also_known_as") or []
            for alias in aliases:
                a = (alias or "").strip()
                if a and self._is_latin_string(self, a):
                    return a
        except Exception:
            pass
        return None

    def _romanize_local(self, name: str) -> str:
        """
        Letzter Fallback: lokale Transliteration (optional).
        """
        try:
            from unidecode import unidecode
            r = unidecode(name or "").strip()
            return r if r else name
        except Exception:
            # notfalls Akzente nur strippen
            return self._strip_accents(name or "").strip()


    def get_romanized_person_name(self, tmdb_person_id: int | str, original_name: str) -> str | None:
        """
        Liefert eine latinische Schreibweise für die Person oder None, wenn nichts Brauchbares gefunden wurde.
        Reihenfolge: translations(en) -> alias -> local translit.
        """
        key = str(tmdb_person_id)
        if key in self._roman_name_cache:
            return self._roman_name_cache[key]

        if self._is_latin_string(original_name or ""):
            self._roman_name_cache[key] = original_name
            return original_name

        # 1) Übersetzung (en)
        name = None
        # name = self._tmdb_person_translated_name_en(tmdb_person_id)
        if not name:
            pass
            # 2) Alias
            # name = self._tmdb_person_alias_latin(tmdb_person_id)
        if not name:
            # 3) Lokale Transliteration (optional)
            name = self._romanize_local(original_name or "")

        # Validieren: wirklich latinisch?
        if name and self._is_latin_string(name):
            self._roman_name_cache[key] = name
            return name

        self._roman_name_cache[key] = None
        return None

    # --- Anwenden beim Personen-Fix (zentraler Emby-Person-Datensatz) ---
    def ensure_person_latin_name(self, emby_person_id: str, tmdb_person_id: int | str, current_name: str):
        """
        Sorgt dafür, dass der zentrale Emby-Personendatensatz einen latinischen Namen hat.
        Setzt zusätzlich ForcedSortName (akzentfrei), damit die Sortierung stimmt.
        """
        return current_name

        # if tmdb_person_id == 21909 or current_name == "鄭伊健":
        #     # Identitäten zeigen (rein zu Debug-Zwecken)
        #     print("old_name:", repr(old_name))
        #     print("current_name:", repr(current_name))
        #     pass
        latin = self.get_romanized_person_name(tmdb_person_id, current_name)

        # if tmdb_person_id == 21909 or current_name == "鄭伊健":
        # print(f"Item {tmdb_person_id} - {current_name} - {latin}")

        if not latin or latin == current_name:
            # print(f"Is None or not equal: {tmdb_person_id} - {current_name} - {latin}")
            return None  # nichts zu tun

        # --- Debug VOR ascii_sort, damit du etwas siehst, falls ascii_sort crasht ---
        # print(f"About to rename: tmdb={tmdb_person_id} emby={emby_person_id} '{current_name}' -> '{latin}'")

        # --- Hart absichern: ascii_sort kann crashen ---
        try:
            forced = self._ascii_sort(latin)
        except Exception as e:
            print(f"[ascii_sort ERROR] tmdb={tmdb_person_id} latin={latin!r} err={e!r}")
            forced = latin  # Fallback: notfalls identisch vergeben

        payload = {
            "Name": latin,
            "ForcedSortName": forced,
        }
        changed_name = f"{current_name}' → '{latin}"
        print(f"Changed person name '{current_name}' to '{latin}'")
        return self.update_item(emby_person_id, payload)


    def _bind_placeholders_to_existing(self, current_people: list[dict], desired_people: list[dict]) -> bool:
        """
        Sucht in current_people (ohne Alias) passende Personen per Name+Type und
        ersetzt Platzhalter in desired_people durch die vorhandene Emby-ID.
        Hängt der gefundenen Person sofort die TMDb-ProviderId an.
        """
        # Index: (etype, norm_name) -> emby_id
        by_name = {}
        for p in (current_people or []):
            et = p.get("Type") or ""
            nm = self._norm_name(p.get("Name") or "")
            if et and nm:
                by_name[(et, nm)] = str(p.get("Id") or "")

        changed = False
        for dp in (desired_people or []):
            et = dp.get("Type") or ""
            tmdb = dp.get("Tmdb")
            nm_clean = self._strip_alias_suffix(dp.get("Name") or "", tmdb)
            # nur Platzhalter (Id nicht numerisch) binden
            if str(dp.get("Id") or "").isdigit():
                continue
            emby_existing = by_name.get((et, self._norm_name(nm_clean)))
            emby_existing_dupe = by_name.get((et, self._norm_name(f"{dp.get("Name")}-{tmdb}")))
            if emby_existing_dupe:
                pass
            if emby_existing or emby_existing_dupe:
                dp["Id"] = emby_existing or emby_existing_dupe
                dp["Name"] = nm_clean  # Alias weg
                # provider sofort an die Person hängen
                if tmdb:
                    self._attach_tmdb_to_person(emby_existing or emby_existing_dupe, int(tmdb))
                    if self.config.Cache:
                        self.config.Cache.update_tmdb_person_map(False, int(tmdb), emby_id=emby_existing or emby_existing_dupe,
                                                          name=nm_clean, alias=None,
                                                          expiration=self.config.Cache.expiration)
                changed = True
        return changed




