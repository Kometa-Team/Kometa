import os, re, time, jmespath, jellyfin
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

logger = util.logger

class Jellyfin(Library):
    def __init__(self, config, params):
        """ Initializes Jellyfin Object 
        
        Args:
            config (modules.config.ConfigFile): Config object
            params (dict): Dictionary of Jellyfin parameters
        """
        super().__init__(config, params)
        self.jellyfin = params["jellyfin"]
        self.url = self.jellyfin["url"]
        self.session = self.config.Requests.session
        
        # not used by jellyfin
        self.clean_bundles = False
        self.empty_trash = False
        self.optimize = False
        
        # the builder make reference to Plex directly so we set it here
        self.Plex = self
        
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
        
        if item.collection_type.value == "movies":
            self.type = "movie"

        self.is_movie = self.type == "movie"
        self.is_show = self.type == "tvshows"
        self.is_music = self.type == "music"
        self.is_playlist = self.type == "playlists"
        self.is_other = self.type == "boxsets"
        
        self._all_items = []

    def notify(self, text, collection=None, critical=True):
        self.config.notify(text, server=self._server_name, library=self.name, collection=collection, critical=critical)
        
    @property
    def language(self) -> str:
        return "en"
        
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
        search.limit = 10
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
        return search.recursive().all

    def get_collection(self, data, force_search=False, debug=True):        
        search = self.api.items.search
        search.include_item_types = [
            self.api.generated.BaseItemKind.BOXSET
        ]
        collections = search.recursive().all
        for collection in collections:
            if collection.name == data:
                return ItemMovieWrapper(collection)
        return None

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
        return []

    def _upload_image(self, item, image):
        raise NotImplementedError("Jellyfin _upload_image method not implemented yet")
        
    def edit_tags(self, attr, obj, add_tags=None, remove_tags=None, sync_tags=None, do_print=True, locked=True, is_locked=None):
        raise NotImplementedError("Jellyfin edit_tags method not implemented yet")
    
    def find_poster_url(self, item):
        raise NotImplementedError("Jellyfin find_poster_url method not implemented yet")

    def get_rating_keys(self, method, data, is_playlist=False):
        raise NotImplementedError("Jellyfin get_rating_keys method not implemented yet")

    def image_update(self, item, image, tmdb=None, title=None, poster=True):
        raise NotImplementedError("Jellyfin image_update method not implemented yet")
    
    def item_labels(self, item):
        pass
    
    def item_posters(self, item):
        raise NotImplementedError("Jellyfin item_posters method not implemented yet")
    
    def notify_delete(self, message_id):
        raise NotImplementedError("Jellyfin notify_delete method not implemented yet")
    
    def reload(self, item, force=False):
        pass
    
    def upload_poster(self, item, image, tmdb=None, title=None):
        raise NotImplementedError("Jellyfin upload_poster method not implemented yet")

class ItemMovieWrapper(Movie):
    def __init__(self, item):
        self.item = item
        
    @property
    def smart(self) -> bool:
        return False
    
    @property
    def title(self) -> str:
        return self.item.name
    
    @property
    def ratingKey(self) -> int:
        return self.item.id.int
    
    @property
    def year(self) -> int:
        return self.item.production_year
    
    @property
    def guid(self) -> str:
        if self.item.provider_ids and "Tmdb" in self.item.provider_ids:
            return f"themoviedb://{self.item.provider_ids['Tmdb']}"
        elif self.item.provider_ids and "Imdb" in self.item.provider_ids:
            return f"imdb://{self.item.provider_ids['Imdb']}"
        return None

    @property
    def childCount(self) -> int:
        return 0
    
    def __getattr__(self, name):
        return getattr(self.item, name)
