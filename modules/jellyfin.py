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

        self.type = item.collection_type.value
        self.is_movie = self.type == "movies"
        self.is_show = self.type == "tvshows"
        self.is_music = self.type == "music"
        self.is_playlist = self.type == "playlists"
        self.is_other = self.type == "boxsets"
        
        self._all_items = []

    def notify(self, text, collection=None, critical=True):
        self.config.notify(text, server=self._server_name, library=self.name, collection=collection, critical=critical)
    
    @property    
    def library_item_uid_name(self) -> str:
        return 'Id'
    
    @property
    def library_item_title_name(self) -> str:
        return 'Name'
    
    @property
    def library_external_id_name(self) -> str:
        return 'ProviderIds'
        
    def get_all(self, builder_level=None, load=False):        
        if load and builder_level in [None, "movies"]:
            self._all_items = []
        if self._all_items and builder_level in [None, "movies"]:
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
        search.recursive().paginate(10000)
        result = search.all

        logger.info(f"Loaded {len(result)} {builder_level.capitalize()}")

        if builder_level in [None, "movies"]:
            self._all_items = result
        return result

    def map_external_id(self, items):
        total = len(items)
        for i, item in enumerate(items, 1):
            logger.ghost(f"Processing: {i}/{total} {item.name}")
            if isinstance(item, tuple):
                item = item[0]
            
            external_id = jmespath.search("ProviderIds.Tmdb", item)
            if external_id is None:
                continue
            
            key = item.get('Id')
            
            try:
                self.config.TMDb.get_movie(external_id)
                self.movie_rating_key_map[key] = external_id
            except Failed:
                pass
        
        logger.info("")
        logger.info(f"Processed {total} {self.type}")
        
    def get_all_collections(self, label=None):
        search = self.api.items.search
        search.include_item_types = [
            self.api.generated.BaseItemKind.BOXSET
        ]
        search.recursive().paginate(10000)
        return search.all
    
    def get_collection(self, data, force_search=False, debug=True):
        print(data)

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