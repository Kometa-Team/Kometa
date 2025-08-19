import base64
import hashlib
import json
import os
import re
import time
import urllib.parse
from xml.etree.ElementTree import Element

import requests
from plexapi.collection import Collection
from plexapi.video import Show, Movie, Episode

from modules.logs import ERROR, WARNING
from modules.util import Failed

# bugs: razzie + berlinale year no poster

# todo: add person link to collection with type while doing the edits / summary ?

## Helpful URLS for dev:
# https://swagger.emby.media/?staticview=true#/
# https://github.com/MediaBrowser/Emby/wiki
# https://dev.emby.media/doc/restapi/Browsing-the-Library.html
# https://docs.mdblist.com/docs/api


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

    class Person:
        def __init__(self):
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


class Season:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return self._dict_to_xml(self.data)

    @staticmethod
    def _dict_to_xml(data_dict):
        element = Element('Directory')
        for key, value in data_dict.items():
            if value is not None:
                element.set(key, str(value))
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


class EmbyConfig:
    X_EMBY_CONTAINER_SIZE = 50  # Definiere die Standardgröße für die Anzahl der Elemente


class EmbyServer:

    def __init__(self, server_url, user_id, api_key, library_name = None):

        # ToDo: Merge the cache
        self.people_lib_cache = {}
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
                    print(s)
                    break

        # self.cache_filenames()

        # Configure API key authorization: apikeyauth
        # configuration = emby_client.Configuration()
        # configuration.api_key['api_key'] = api_key

        # Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
        # configuration.api_key_prefix['api_key'] = 'Bearer'

        # create an instance of the API class
        # client = emby_client.ApiClient(configuration)

    def get_people(self, library_id: str, role: str):
        if f"{library_id}-{role}" in self.people_lib_cache.keys():
            return self.people_lib_cache[f"{library_id}-{role}"]
        endpoint = f"/emby/Persons?ParentId={library_id}&PersonTypes={role}&api_key={self.api_key}"
        url = self.emby_server_url + endpoint
        response = requests.get(url, headers=self.headers)
        items = response.json().get("Items", [])
        self.people_lib_cache[f"{library_id}-{role}"] = items
        return items

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
                match = re.search(resolution_regex, file_name)
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
                "Fields": "Path,Studios,People,ProductionLocations,ProviderIds"
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
                    # if re.search('1080', item_media_path):
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
                print(f"Failed to fetch all resolutions: {e}")
            # self.production_countries = allcountries
            # return self.production_countries

    def get_emby_countries(self, library_id):
        """
        Fetches years for all items in the database and caches the results.
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

            print(f"Country cache populated with {len(self.production_countries)} entries.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch all countries: {e}")
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

            print(f"Genre cache populated with {len(self.emby_genres)} entries.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch all genres: {e}")
        # self.production_countries = allcountries
        return self.emby_genres

    def get_system_info(self):
        endpoint = "/emby/System/Info"
        url = self.emby_server_url + endpoint
        try:
            response = requests.get(url, headers=self.headers)
            return response.json()
        except Exception as e:
            print(
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
            print(f"Error occurred while getting users: {e}")
            return None

    def update_collection_display_order(self, collection_id, sort_order):
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
            print(f"Actor not found: {name}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error occurred while searching for actor: {e}")
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
            print(initpath)
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


    def get_boxsets_from_library(self, title=None, library_id= None, label = None) ->[Collection]:
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



        my_search = f"{self.emby_server_url}/Users/{self.user_id}/Items?Recursive=true{search_title}{search_tag}{get_fields}&ParentId={self.library_id}&IncludeItemTypes=BoxSet&api_key={self.api_key}"
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

        plex_collections = self.convert_emby_to_plex(my_return)
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

        print(f"111 Retrieved and converted {len(collection_items)} boxsets from library '{library_id}'.")

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

        print(f"Retrieved and converted {len(plex_collections)} boxsets from library '{library_id}'.")

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

        print(f"Retrieved and converted {len(plex_collections)} boxsets from library '{library_id}'.")

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
            print("Collection ID is None. Cannot fetch items.")
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
                print(f"Error occurred while getting items in collection ID {collection_id}.")
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
            print("Can't create collection, no items to add to it.")
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
                print(f"create_collection: Error creating {collection_name}, response: {response.text}")
                return None

            # Parse the response to get the collection ID
            data = response.json()
            collection_id = data.get('Id')
            print(f"Successfully created collection {collection_name}")

            # Process remaining items in batches of 100
            batch_size = 100
            for i in range(batch_size, len(item_ids), batch_size):
                batch = item_ids[i:i + batch_size]
                # string_ids = ','.join(batch)
                batch_response = requests.post(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items?api_key={self.api_key}&Ids={self.__ids_to_str(batch)}"
                )

                if batch_response.status_code != 204:
                    print(
                        f"Error adding batch {i // batch_size + 1} to collection {collection_name}, response: {batch_response.text}")

            # Lock the collection if specified
            if locked:
                self.lock_collection(collection_id)

            # Optional: Update the display order
            self.update_collection_display_order(collection_id, "test")

            time.sleep(1)  # Add a short delay to avoid API rate limits
            return collection_id
        except Exception as e:
            print(f"Collection creation failed. - {e}")

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
            print(f"No items found matching the criteria.")
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
        return response.json().get('Items', [])

    def get_library_data(self, library_id):
        endpoint = f"{self.emby_server_url}/emby/Library/Sections/{library_id}"
        response = self.session.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_item(self, item_id) -> dict:
        endpoint = f"/emby/users/{self.user_id}/items/{item_id}?api_key={self.api_key}"
        url = self.emby_server_url + endpoint
        try:
            return requests.get(url, headers=self.headers).json()
        except Exception as e:
            print(f"Error occurred while getting item: {e}. URL: {url}.")
            return None

    def get_item_images(self, item_id) -> dict:
        endpoint = f"/emby/Items/{item_id}/Images?api_key={self.api_key}"
        url = self.emby_server_url + endpoint
        try:
            return requests.get(url, headers=self.headers).json()
        except Exception as e:
            print(f"Error occurred while getting item image: {e}. URL: {url}.")
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
            print(f"Error refreshing item {item_id}, response: {response}")
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
                    print(
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
                print(f"Error during sorting by {sort_key}: {e}")
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
                print(f"Invalid Limit value: {query_params['Limit']}")
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
            print(
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
            print(
                f"Error marking item {item_id} as a favorite for user {user_id}: {response.content}"
            )
            return False

    import os, hashlib, requests

    def set_image_smart(
            self,
            item_id: str,
            image_path: str,
            image_type: str = "Primary",
            provider_name: str = "MDBList Collection Creator script",
    ) -> bool:
        """
        Setzt ein Bild nur dann, wenn es sich vom bereits in Emby hinterlegten Bild unterscheidet.
        Vergleicht zuerst Content-Length & Content-Type (schnell), danach optional per SHA-256 Hash.
        Nutzt einen kleinen In-Memory-Cache, gebunden an den Emby-ImageTag.

        Rückgabe:
          True  -> Bild gesetzt ODER übersprungen (identisch)
          False -> harter Fehler beim Setzen
        """
        # --- kleiner Cache auf dem Objekt (einmalig angelegt) ---
        if not hasattr(self, "_image_hash_cache"):
            self._image_hash_cache = {}  # key: (item_id, image_type, image_tag) -> sha256_hex

        # --- Content-Type Mapping nur für lokale Dateien ---
        ext_to_ct = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tbn": "image/jpeg",
            ".webp": "image/webp",
        }

        def sha256_stream(iterable):
            h = hashlib.sha256()
            for chunk in iterable:
                if chunk:
                    h.update(chunk)
            return h.hexdigest()

        # 1) aktuelle Bildgröße/-typ aus Emby (HEAD auf Originalbild)
        cur_url = (
            f"{self.emby_server_url}/emby/Items/{item_id}/Images/{image_type}"
            f"?EnableImageEnhancers=false&Format=original"
        )
        try:
            cur_head = requests.head(
                cur_url,
                headers={"X-Emby-Token": self.api_key},
                timeout=10,
                allow_redirects=True,
            )
            if not cur_head.ok:
                cur_size, cur_ct = None, None
            else:
                cur_size = int(cur_head.headers.get("Content-Length", "0") or "0") or None
                cur_ct = cur_head.headers.get("Content-Type")
        except Exception:
            cur_size, cur_ct = None, None

        # Wenn kein aktuelles Bild ermittelbar -> direkt setzen
        if cur_size is None:
            if image_path.startswith("http"):
                return self.__set_remote_image(item_id, image_path, image_type, provider_name)
            else:
                return self.__upload_image(item_id, image_path, image_type)

        # 2) Kandidat: Größe & Typ bestimmen (ohne großen Download)
        if image_path.startswith("http"):
            try:
                cand_head = requests.head(image_path, timeout=10, allow_redirects=True)
                if cand_head.ok:
                    cand_size = int(cand_head.headers.get("Content-Length", "0") or "0") or None
                    cand_ct = cand_head.headers.get("Content-Type")
                else:
                    cand_size, cand_ct = None, None
            except Exception:
                cand_size, cand_ct = None, None
        else:
            try:
                cand_size = os.path.getsize(image_path)
            except Exception:
                cand_size = None
            ext = os.path.splitext(image_path)[1].lower()
            cand_ct = ext_to_ct.get(ext)

        # 3) Schnelle Entscheidung: Größe/Typ verschieden -> setzen
        if (cand_size is None) or (cand_size != cur_size) or (cur_ct and cand_ct and cur_ct != cand_ct):
            if image_path.startswith("http"):
                return self.__set_remote_image(item_id, image_path, image_type, provider_name)
            else:
                return self.__upload_image(item_id, image_path, image_type)

        # 4) Größe & Typ gleich -> Hash-Vergleich (mit Tag-gebundenem Cache)
        #    a) ImageTag holen (billig)
        image_tag = None
        try:
            meta = requests.get(
                f"{self.emby_server_url}/emby/Items/{item_id}",
                params={"Fields": "PrimaryImageTag,ImageTags", "api_key": self.api_key},
                timeout=10,
            )
            if meta.ok:
                d = meta.json()
                if image_type.lower() == "primary":
                    image_tag = d.get("PrimaryImageTag")
                else:
                    tags = d.get("ImageTags") or {}
                    image_tag = tags.get(image_type) or tags.get(image_type.capitalize())
        except Exception:
            pass

        cache_key = (item_id, image_type, image_tag)
        cur_hash = self._image_hash_cache.get(cache_key)

        #    b) aktuellen Hash ggf. streamend berechnen
        if cur_hash is None:
            try:
                r = requests.get(
                    cur_url,
                    headers={"X-Emby-Token": self.api_key},
                    stream=True,
                    timeout=30,
                )
                if r.ok:
                    cur_hash = sha256_stream(r.iter_content(131072))
                    if image_tag:
                        self._image_hash_cache[cache_key] = cur_hash
            except Exception:
                cur_hash = None

        #    c) Kandidaten-Hash bestimmen
        if image_path.startswith("http"):
            try:
                r = requests.get(image_path, stream=True, timeout=30)
                cand_hash = sha256_stream(r.iter_content(131072)) if r.ok else None
            except Exception:
                cand_hash = None
        else:
            try:
                with open(image_path, "rb") as f:
                    cand_hash = sha256_stream(iter(lambda: f.read(131072), b""))
            except Exception:
                cand_hash = None

        # 5) Gleich? -> Skip; sonst setzen
        if cur_hash and cand_hash and cur_hash == cand_hash:
            print(f"Skip: identisches {image_type}-Bild für Item {item_id}.")
            return True

        if image_path.startswith("http"):
            return self.__set_remote_image(item_id, image_path, image_type, provider_name)
        else:
            return self.__upload_image(item_id, image_path, image_type)

    def set_image(
        self,
        item_id,
        image_path,
        image_type="Primary",
        provider_name="MDBList Collection Creator script",
    ):
        """
        Can take local or remote path and set as image for item.

        Args:
            item_id (str): The ID of the item.
            image_path (str): The path to the image. Either local or remote.
            image_type (str): The type of the image. Defaults to "Primary".
            provider_name (str): The name of the image provider. Defaults to "MDBList Collection Creator script".

        Returns:
            bool: True if the image is uploaded successfully, False otherwise.
        """
        if image_path.startswith("http"):
            return self.__set_remote_image(
                item_id, image_path, image_type, provider_name
            )
        else:
            return self.__upload_image(item_id, image_path, image_type)

    def __set_remote_image(
        self,
        item_id,
        image_url,
        image_type="Primary",
        provider_name="MDBList Collection Creator script",
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
            "ProviderName": provider_name,
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
                print(f"Error setting image for item {item_id}, response: {response}")
                return False

        except Exception as e:
            print(f"Exception occurred while downloading image: {str(e)}")
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
            print(f"Error: Image file not found: {image_path}")
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
            print(f"Unsupported image format. Must be one of: {', '.join(ext_to_content_type.keys())}")
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
                print(f"Error uploading image for item {item_id}, response: {response}")
                return False

        except Exception as e:
            print(f"Exception occurred while uploading image: {str(e)}")
            return False

    # Konvertierungsfunktion, um Emby-Daten in Plex-Klassenobjekte zu konvertieren
    def convert_emby_to_plex(self, emby_data_list):
        plex_objects = []
        if not emby_data_list or len(emby_data_list) == 0:
            return []
        # emby_data_list = sorted(set(emby_data_list))
        for item in emby_data_list:
            # print(item)
            if item is None:
                print("Item is None")
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
                if year:
                    year= int(year)
                people = item.get("People", [])
                plex_actors = []
                # for person in people:
                #     print(person)
                #     # List[PlexObjectT]
                #     if person.get('Type') == 'Actor':
                #         new_person = PLEXOBJECTS.get("actor")()
                #         # new_person.tag = 'actor'
                #         new_person.id = person.get('Id')
                #         new_person.name = person.get('Name')
                #         plex_actors.append(new_person)

                # print(people)
                # {'Id': '12917', 'Name': 'Hideko Takamine', 'PrimaryImageTag': '243089fe465d5f5402eb21462e0d915e', 'Role': 'Keiko Yashiro', 'Type': 'Actor'}
                # print(people)
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
                    # not working
                    # 'media': [item.get('Path')],
                    # 'locations':[item.get('Path')] # todo: working?
                    # 'roles':plex_actors
                }
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

                    allitems = self.get_items_in_boxset(new_col.ratingKey)
                    new_col._items = allitems
                    new_col.childCount= len((allitems))

                    plex_object=new_col

                elif media_type == "Audio":
                    plex_object=Audio(data)
                else:
                    print(f"error converting Emby object")
                    continue
                plex_object.locations = [item.get("Path", [])]
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
        self.__update_item(item_id,data)

    def __update_item(self, item_id, data, item = None):
        if not item:
            item = self.get_item(item_id)
        if item is None:
            return None
        if "ForcedSortName" in data and "SortName" not in item["LockedFields"]:
            # If adding "ForcedSortName" to data, we must have "SortName" in LockedFields
            # see https://emby.media/community/index.php?/topic/108814-itemupdateservice-cannot-change-the-sortname-and-forcedsortname/
            item["LockedFields"].append("SortName")
        item.update(data)
        update_item_url = (
            f"{self.emby_server_url}/emby/Items/{item_id}?api_key={self.api_key}"
        )
        try:
            response = requests.post(update_item_url, json=item, headers=self.headers)
            # print(
            #     f"Updated item {item_id} with {data}. Waiting {self.seconds_between_requests} seconds."
            # )
            time.sleep(self.seconds_between_requests)
            return response
        except Exception as e:
            print(f"Error occurred while updating item: {e}")
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

        print(
            f"Processing {collection_name} with '{operation}' in {num_batches} batches"
        )

        for i in range(num_batches):
            start_index = i * batch_size
            end_index = min((i + 1) * batch_size, len(item_ids))
            batch_item_ids = item_ids[start_index:end_index]
            print(".", end="", flush=True)

            if operation == "add":
                response = requests.post(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items/?api_key={self.api_key}&Ids={self.__ids_to_str(batch_item_ids)}"
                )
            elif operation == "delete":
                response = requests.delete(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items/?api_key={self.api_key}&Ids={self.__ids_to_str(batch_item_ids)}"
                )

            if response.status_code != 204:
                print(
                    f"Error processing collection with operation '{operation}', response: {response}"
                )
                return affected_count

            affected_count += len(batch_item_ids)
            time.sleep(self.seconds_between_requests)

        print()
        print(f"Finished '{operation}' with {len(item_ids)} items in {collection_name}")

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

        print(
            f"Processing {collection_name} with '{operation}' in {num_batches} batches"
        )

        for i in range(num_batches):
            start_index = i * batch_size
            end_index = min((i + 1) * batch_size, len(item_ids))
            batch_item_ids = item_ids[start_index:end_index]
            print(".", end="", flush=True)

            if operation == "add":
                response = requests.post(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items/?api_key={self.api_key}&Ids={self.__ids_to_str(batch_item_ids)}"
                )
            elif operation == "delete":
                response = requests.delete(
                    f"{self.emby_server_url}/Collections/{collection_id}/Items/?api_key={self.api_key}&Ids={self.__ids_to_str(batch_item_ids)}"
                )

            if response.status_code != 204:
                print(
                    f"Error processing collection with operation '{operation}', response: {response}"
                )
                return affected_count

            affected_count += len(batch_item_ids)
            time.sleep(self.seconds_between_requests)

        print()
        print(f"Finished '{operation}' with {len(item_ids)} items in {collection_name}")

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
            print(f'Successfully deleted collection with ID "{collection_id}"')
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
                    print(f"Batch {i // batch_size + 1}: Erfolgreich gelöscht")
                else:
                    print(f"Batch {i // batch_size + 1}: Fehler beim Löschen - {response.status_code}")
                    print("Antwort:", response.text)            # all_ids = [item.get("Id") for item in all_items]
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
                print(f"BoxSet with ID '{collection_id}' successfully removed.")
                return True
            else:
                print(
                    f"Failed to remove BoxSet with ID '{collection_id}'. Response: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error removing BoxSet with ID '{collection_id}': {e}")
            return False


    def get_emby_item_tags(self, plex_object, library_id="", search_all= False,from_cache=True):
        """
        Retrieve and print all tags for an Emby item based on a Plex object.

        Args:
            plex_object: The Plex object containing the 'ratingKey' that maps to the Emby 'Id'.

        Returns:
            list: A list of tags for the Emby item.
        """

        if from_cache and search_all and self.all_tags:
            return self.all_tags

        emby_item_id = None
        from modules.plex import Plex

        if hasattr(plex_object, 'ratingKey'):
            emby_item_id = plex_object.ratingKey
        elif isinstance(plex_object, str) or isinstance(plex_object, int):
            emby_item_id = plex_object
        elif isinstance(plex_object, Plex):
            pass
            # if not called properly, retrieve all the lib tags
            search_all= True
        else:
            raise WARNING(f"Emby item tag object is not configured {plex_object}")
            # print(f"error - no plex object: {plex_object}")
            return []
        ids = ""
        parent_id = ""
        if search_all:
            my_url = f"{self.emby_server_url}/emby/Tags?Recursive=true&ParentId={library_id}&api_key={self.api_key}"
        elif emby_item_id:
            my_url = f"{self.emby_server_url}/emby/Items?Fields=Tags&Ids={emby_item_id}&api_key={self.api_key}"
            # ids = f"Ids={emby_item_id}&"
        else:
            raise Failed("Plex object not specified for tag search.")
            # parent_id= f"ParentId={library_id}&"
        # # Make a request to get the Emby item details
        response = requests.get(my_url)

        # response = requests.get(
        #     f"{self.emby_server_url}/emby/Tags?{ids}Recursive=true&{library_id}api_key={self.api_key}'"
        # )


        # tags empty for collections
        if response.status_code != 200:
            raise Failed(
                f"Failed to retrieve item details for ID {emby_item_id}. "
                f"Response: {response.status_code} - {response.text}"
            )

        found_tags = []
        item_details = response.json()
        all_items = item_details.get('Items',[])
        if search_all:
            for item in all_items:
                found_tags.append(item.get("Name"))
        else:
            if len(all_items) > 0:
                for tag_item in all_items[0].get("TagItems", []):
                    found_tags.append(tag_item.get('Name'))
            # if str(emby_item_id) in kometa_labels:
            #     all_tags.extend(kometa_labels[str(emby_item_id)])

        if search_all:
            self.all_tags= sorted(set(found_tags))
            return self.all_tags
        return sorted(set(found_tags))

    def get_emby_item_genres(self, plex_object, library_id="", search_all= False,from_cache=True):
        """
        Retrieve and print all tags for an Emby item based on a Plex object.

        Args:
            plex_object: The Plex object containing the 'ratingKey' that maps to the Emby 'Id'.

        Returns:
            list: A list of tags for the Emby item.
        """


        emby_item_id = None
        from modules.plex import Plex

        if hasattr(plex_object, 'ratingKey'):
            emby_item_id = plex_object.ratingKey
        elif isinstance(plex_object, str) or isinstance(plex_object, int):
            emby_item_id = plex_object
        elif isinstance(plex_object, Plex):
            pass
            # if not called properly, retrieve all the lib tags
            search_all= True
        else:
            raise WARNING(f"Emby item genre object is not configured {plex_object}")
            # print(f"error - no plex object: {plex_object}")
            return []
        ids = ""
        parent_id = ""
        if search_all:
            my_url = f"{self.emby_server_url}/emby/Genres?Recursive=true&ParentId={library_id}&api_key={self.api_key}"
        elif emby_item_id:
            my_url = f"{self.emby_server_url}/emby/Items?Fields=Genres&Ids={emby_item_id}&api_key={self.api_key}"
            # ids = f"Ids={emby_item_id}&"
        else:
            raise Failed("Plex object not specified for tag search.")
            # parent_id= f"ParentId={library_id}&"
        # # Make a request to get the Emby item details
        response = requests.get(my_url)

        # response = requests.get(
        #     f"{self.emby_server_url}/emby/Tags?{ids}Recursive=true&{library_id}api_key={self.api_key}'"
        # )


        # tags empty for collections
        if response.status_code != 200:
            raise Failed(
                f"Failed to retrieve item details for ID {emby_item_id}. "
                f"Response: {response.status_code} - {response.text}"
            )

        found_tags = []
        item_details = response.json()
        all_items = item_details.get('Items',[])
        if search_all:
            for item in all_items:
                found_tags.append(item.get("Name"))
        else:
            if len(all_items) > 0:
                for tag_item in all_items[0].get("GenreItems", []):
                    found_tags.append(tag_item.get('Name'))
            # if str(emby_item_id) in kometa_labels:
            #     all_tags.extend(kometa_labels[str(emby_item_id)])

        return sorted(set(found_tags))

    def get_emby_studios(self, plex_object, library_id):
        """
        Retrieve and print all tags for an Emby item based on a Plex object.

        Args:
            plex_object: The Plex object containing the 'ratingKey' that maps to the Emby 'Id'.

        Returns:
            list: A list of tags for the Emby item.
        """
        emby_item_id = None
        from modules.plex import Plex

        if hasattr(plex_object, 'ratingKey'):
            emby_item_id = plex_object.ratingKey
        elif isinstance(plex_object, str) or isinstance(plex_object, int):
            emby_item_id = plex_object
        elif isinstance(plex_object, Plex):
            pass
            # if not called properly, retrieve all the lib tags
            search_all= True
        else:
            raise WARNING(f"Emby item tag object is not configured {plex_object}")
            # print(f"error - no plex object: {plex_object}")
            return []
        ids = ""
        parent_id = ""

        my_url = f"{self.emby_server_url}/emby/Studios?Recursive=true&ParentId={library_id}&api_key={self.api_key}"

        # # Make a request to get the Emby item details
        response = requests.get(my_url)

        # response = requests.get(
        #     f"{self.emby_server_url}/emby/Tags?{ids}Recursive=true&{library_id}api_key={self.api_key}'"
        # )


        # tags empty for collections
        if response.status_code != 200:
            raise Failed(
                f"Failed to retrieve item details for ID {emby_item_id}. "
                f"Response: {response.status_code} - {response.text}"
            )

        all_studios = []
        item_details = response.json()
        all_items = item_details.get('Items',[])

        for item in all_items:
            # TODO: Use Emby Studio for Studios and Networks. Too much work with auto updates.
            # if str(item.get("Name",'')).startswith('📡'):
            #     continue
            all_studios.append(item.get("Name"))


        all_studios= sorted(set(all_studios))
        return all_studios

    def get_emby_networks(self, plex_object, library_id):
        """
        Retrieve and print all tags for an Emby item based on a Plex object.

        Args:
            plex_object: The Plex object containing the 'ratingKey' that maps to the Emby 'Id'.

        Returns:
            list: A list of tags for the Emby item.
        """
        emby_item_id = None
        from modules.plex import Plex

        if hasattr(plex_object, 'ratingKey'):
            emby_item_id = plex_object.ratingKey
        elif isinstance(plex_object, str) or isinstance(plex_object, int):
            emby_item_id = plex_object
        elif isinstance(plex_object, Plex):
            pass
            # if not called properly, retrieve all the lib tags
            search_all= True
        else:
            raise WARNING(f"Emby item tag object is not configured {plex_object}")
            # print(f"error - no plex object: {plex_object}")
            return []
        ids = ""
        parent_id = ""

        my_url = f"{self.emby_server_url}/emby/Studios?Recursive=true&ParentId={library_id}&api_key={self.api_key}"

        # # Make a request to get the Emby item details
        response = requests.get(my_url)

        # response = requests.get(
        #     f"{self.emby_server_url}/emby/Tags?{ids}Recursive=true&{library_id}api_key={self.api_key}'"
        # )


        # tags empty for collections
        if response.status_code != 200:
            raise Failed(
                f"Failed to retrieve item details for ID {emby_item_id}. "
                f"Response: {response.status_code} - {response.text}"
            )

        all_studios = []
        item_details = response.json()
        all_items = item_details.get('Items',[])

        for item in all_items:
            # TODO: Use Emby Studio for Studios and Networks. Too much work with auto updates.
            # if not str(item.get("Name",'')).startswith('📡'):
            #     continue
            # all_studios.append(str(item.get("Name", ''))[2:])
            all_studios.append(str(item.get("Name", '')))


        all_studios= sorted(set(all_studios))
        return all_studios

    def get_library_studios(self, name = None):

        if not self.studio_list:
            my_url = f"{self.emby_server_url}/emby/Studios?ParentId={self.library_id}&api_key={self.api_key}"
            response = requests.get(my_url)

            # response = requests.get(
            #     f"{self.emby_server_url}/emby/Tags?{ids}Recursive=true&{library_id}api_key={self.api_key}'"
            # )

            # tags empty for collections
            if response.status_code != 200:
                return []
                raise Failed(
                    f"Failed to retrieve item details for ID {self.library_id}. "
                    f"Response: {response.status_code} - {response.text}"
                )

            all_studios = []
            item_details = response.json()
            all_items = item_details.get('Items', [])

            for item in all_items:
                all_studios.append(item.get("Name"))
            self.studio_list = sorted(set(all_studios))

        if name:
            if isinstance(name,str):
                if name in self.studio_list:
                    return self.studio_list
                else:
                    if re.search(",", name):
                        names = name.split(',')
                        for n in names:
                            if n in self.studio_list:
                                return self.studio_list
        return []

        return self.studio_list



        # # Make a request to get the Emby item details


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
            print(".", end="", flush=True)
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
                response = requests.get(my_url)

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







