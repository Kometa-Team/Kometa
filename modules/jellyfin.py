import os, re, time, jmespath
from datetime import datetime, timedelta
from modules import builder, util
from modules.library import Library
from modules.poster import ImageData
from modules.request import parse_qs, quote_plus, urlparse
from modules.util import Failed
from PIL import Image
from requests.exceptions import ConnectionError, ConnectTimeout
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_not_exception_type
from xml.etree.ElementTree import ParseError
from plexapi.video import Movie
from uuid import UUID

import jellyfin
from jellyfin.items import Item
from jellyfin.generated import BaseItemDto

logger = util.logger

class Jellyfin(Library):
    def __init__(self, config, params):
        """ Initializes Jellyfin Object 
        
        Args:
            config (modules.config.ConfigFile): Config object
            params (dict): Dictionary of Jellyfin parameters
        """
        # TODO: https://github.com/Kometa-Team/Kometa/pull/2788
        params["plex"] = {}
        params["plex"]["optimize"] = None
        params["plex"]["clean_bundles"] = None
        params["plex"]["empty_trash"] = None
        super().__init__(config, params)
        self.jellyfin = params["jellyfin"]
        self.url = self.jellyfin["url"]
        self.session = self.config.Requests.session
        
        # not used by jellyfin
        self.clean_bundles = False
        self.empty_trash = False
        self.optimize = False
        
        # the builder make reference to Plex directly so we set it here
        self.Plex = PlexWrapper(self)

        # some api methods require a user context, so we store the user here
        self.user = self.jellyfin["user"]

        if self.jellyfin["verify_ssl"] is False and self.config.Requests.global_ssl is True:
            logger.debug("Overriding verify_ssl to False for Jellyfin connection")
            self.session = self.config.Requests.create_session(verify_ssl=False)
        if self.jellyfin["verify_ssl"] is True and self.config.Requests.global_ssl is False:
            logger.debug("Overriding verify_ssl to True for Jellyfin connection")
            self.session = self.config.Requests.create_session()

        self.token = self.jellyfin["token"]
        self.timeout = self.jellyfin["timeout"]
        
        self.api = jellyfin.api(self.url, self.token)
        self.api.register_client(client_name="Kometa")

        logger.info(self.url)
        logger.secret(self.token)
        try:
            self._server_version = self.api.system.info.version
            self._server_name = self.api.system.info.server_name

            logger.info(f"Connected to server {self._server_name} version {self._server_version}")
        except Exception as e:
            logger.info(f"Jellyfin Error: Jellyfin connection attempt failed")
            logger.stacktrace()
            raise Failed(f"Jellyfin Error: {e}")
        
        libraries = self.api.items.search.only_library().add('name_starts_with', self.name).all
        
        if len(libraries) > 1:
            names = [f"'{item.id.hex}'" for item in libraries.items]
            raise Failed(f"Jellyfin Library '{params['name']}' is not unique. Options: {names}")

        if len(libraries) < 1:
            raise Failed(f"Jellyfin Library '{params['name']}' not found.")

        item = libraries.first
        self.Jellyfin = item
        self.type = item.collection_type.value
        
        if item.collection_type == jellyfin.generated.CollectionType.MOVIES:
            self.type = "Movie"

        self.is_movie = self.type == "Movie"
        self.is_show = self.type == "TVShow"
        self.is_music = self.type == "Music"
        self.is_playlist = self.type == "Playlist"
        self.is_other = self.type == "Boxset"

        self._all_items = []

    def notify(self, text, collection=None, critical=True):
        self.config.notify(text, server=self._server_name, library=self.name, collection=collection, critical=critical)
        
    @property
    def language(self) -> str:
        return "en"
    
    @property
    def PlexServer(self):
        return ServerWrapper(self.api)

    def get_all(self, builder_level=None, load=False):
        if load and builder_level in [None, "movie"]:
            self._all_items = []
        if self._all_items and builder_level in [None, "movie"]:
            return self._all_items
        builder_level = self.type
        
        logger.info(f"Loading All {builder_level.capitalize()} from Library: {self.name}")
        
        search = self.api.items.search
        search.include_item_types = [
            self.api.generated.BaseItemKind.MOVIE
        ]
        search.fields = [
            self.api.generated.ItemFields.PROVIDERIDS, 
            self.api.generated.ItemFields.PATH
        ]
        search.recursive()
        result = []

        for item in search.all:
            result.append(ItemMovieWrapper(item))

        logger.info(f"Loaded {len(result)} {builder_level.capitalize()}")

        if builder_level in [None, "movie"]:
            self._all_items = result
        return result
        
    def get_all_collections(self, label=None):
        search = self.api.items.search
        search.include_item_types = [
            self.api.generated.BaseItemKind.BOXSET
        ]
        
        result = []
        for item in search.all:
            result.append(ItemMovieWrapper(item))
        return result

    def get_collection(self, data, force_search=False, debug=True):        
        search = self.api.items.search
        search.include_item_types = [
            self.api.generated.BaseItemKind.BOXSET
        ]
        collections = search.recursive().all
        for collection in collections:
            if collection.name == data:
                return ItemMovieWrapper(collection)

        item = Item(BaseItemDto())
        item.name = data
        return ItemMovieWrapper(item)

    def split(self, text):
        attribute, modifier = os.path.splitext(str(text).lower())
        final = f"{attribute}{modifier}"
        return attribute, modifier, final
    
    def fetch_item(self, item):
        key = item
        if key in self.cached_items:
            return self.cached_items[key][0]
        raise Failed(f"Jellyfin Error: Item {item} not found")

    def get_collection_items(self, collection, smart_label_collection):
        name = collection if isinstance(collection, str) else collection.title
        item = self.get_collection(name)
        
        if item.ratingKey == 0:
            return []

        search = self.api.items.search.recursive()
        search.include_item_types = [
            self.api.generated.BaseItemKind.MOVIE
        ]
        search.parent_id = item.id
        result = []
        for movie in search.all:
            result.append(ItemMovieWrapper(movie))
        return result
    
    def get_collection_name_and_items(self, collection, smart_label_collection):
        name = collection if isinstance(collection, str) else collection.title
        return name, self.get_collection_items(collection, smart_label_collection)

    def alter_collection(self, items, collection: str, smart_label_collection=False, add=True) -> None:
        warn_msg = "Jellyfin alter_collection method not implemented yet"
        logger.warning(warn_msg)
        pass

    def item_reload(self, item):
        return item
    
    def delete(self, obj):
        warn_msg = "Jellyfin delete method not implemented yet"
        logger.warning(warn_msg)
        
    def fetchItem(self, data):
        warn_msg = "Jellyfin fetchItem method not implemented yet"
        logger.warning(warn_msg)
        return None
        
    def fetchItems(self, uri_args):
        if uri_args is not None:
            warn_msg = "Jellyfin fetchItems method not implemented yet"
            logger.warning(warn_msg)
            return []

        results = []
        for item in self.api.items.search.recursive().all:
            results.append(ItemMovieWrapper(item))
        return results

    def _upload_image(self, item, image):
        warn_msg = "Jellyfin _upload_image method not implemented yet"
        logger.warning(warn_msg)
        
    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None, do_print=True, locked=True, is_locked=None):
        warn_msg = "Jellyfin edit_tags method not implemented yet"
        logger.warning(warn_msg)
    
    def find_poster_url(self, item):
        warn_msg = "Jellyfin find_poster_url method not implemented yet"
        logger.warning(warn_msg)

    def get_rating_keys(self, method, data, is_playlist=False):
        warn_msg = "Jellyfin get_rating_keys method not implemented yet"
        logger.warning(warn_msg)

    def image_update(self, item, image, tmdb=None, title=None, poster=True):
        warn_msg = "Jellyfin image_update method not implemented yet"
        logger.warning(warn_msg)

    def item_labels(self, item):
        pass
    
    def item_posters(self, item):
        warn_msg = "Jellyfin item_posters method not implemented yet"
        logger.warning(warn_msg)
    
    def notify_delete(self, message_id):
        warn_msg = "Jellyfin notify_delete method not implemented yet"
        logger.warning(warn_msg)

    def reload(self, item, force=False):
        warn_msg = "Jellyfin reload method not implemented yet"
        logger.warning(warn_msg)
    
    def upload_poster(self, item, image, tmdb=None, title=None):
        warn_msg = "Jellyfin upload_poster method not implemented yet"
        logger.warning(warn_msg)
        
    def collection_order_query(self, collection, data):
        warn_msg = "Jellyfin dont support collection order"
        logger.warning(warn_msg)
        
    def find_item_assets(self, item, item_asset_directory=None, asset_directory=None, folder_name=None):
        warn_msg = "Jellyfin find_item_assets method not implemented yet"
        logger.warning(warn_msg)
        return None, None, None, item_asset_directory, folder_name
    
    def upload_images(self, item, poster=None, background=None, logo=None, overlay=False):
        warn_msg = "Jellyfin upload_images will not work with cache without change sqlite rating_key on cache to TEXT"
        logger.warning(warn_msg)
        return False, False, False
    
    def playlist_report(self):
        warn_msg = "Jellyfin playlist_report method not implemented yet"
        logger.warning(warn_msg)
        return {}
    
    def moveItem(self, obj, item, after):
        warn_msg = "Jellyfin moveItem method not implemented yet"
        logger.warning(warn_msg)

class PlexWrapper:
    def __init__(self, library: Library):
        self.library = library
        
    @property
    def type(self) -> str:
        return self.library.type.lower()

    def __getattr__(self, name):
        return getattr(self.library, name)

class ServerWrapper:
    def __init__(self, api):
        self.api = api
        
    @property
    def machineIdentifier(self) -> str:
        return self.api.system.info.id
    
    @property
    def friendlyName(self) -> str:
        return self.api.system.info.server_name

class ItemMovieWrapper(Movie):
    def __init__(self, item):
        self.item = item
        
    @property
    def smart(self) -> bool:
        return False
    
    @property
    def title(self) -> str:
        return self.item.name if self.item.name else ""
    
    @property
    def summary(self) -> str:
        return self.item.overview if self.item.overview else ""
    
    @property
    def ratingKey(self) -> int:
        return self.item.id.int if self.item.id else 0
    
    @property
    def year(self) -> int:
        return self.item.production_year if self.item.production_year else 0

    @property
    def collectionSort(self) -> int:
        return 0
    
    @property
    def titleSort(self) -> str:
        if self.item.sort_name is None:
            return ""
        return self.item.sort_name

    def editSummary(self, summary: str) -> None:
        self.item.overview = summary
        
    def editSortTitle(self, new_sort_title: str) -> None:
        self.item.sort_name = new_sort_title

    @property
    def guid(self) -> str:
        if self.item.provider_ids and "Tmdb" in self.item.provider_ids:
            return f"themoviedb://{self.item.provider_ids['Tmdb']}"
        elif self.item.provider_ids and "Imdb" in self.item.provider_ids:
            return f"imdb://{self.item.provider_ids['Imdb']}"
        return None

    @property
    def childCount(self) -> int:
        return self.item.child_count if self.item.child_count else 0
    
    def __getattr__(self, name):
        return getattr(self.item, name)
    
    def __eq__(self, other):
        if isinstance(other, ItemMovieWrapper):
            return self.ratingKey == other.ratingKey
        return False

    def __hash__(self):
        return hash(self.ratingKey)

    def __repr__(self):
        return (
            f"<ItemMovieWrapper\n  id={self.item.id.hex}\n  ratingKey={self.ratingKey}\n  title={self.title}\n>"
        )