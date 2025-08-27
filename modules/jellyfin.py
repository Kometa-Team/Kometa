import os, re, time
from datetime import datetime, timedelta
from modules import builder, util
from modules.library import Library
from modules.poster import ImageData
from modules.request import parse_qs, quote_plus, urlparse
from modules.util import Failed
from PIL import Image
from jellyfin_apiclient_python import JellyfinClient
from jellyfin_apiclient_python.api import API
from requests.exceptions import ConnectionError, ConnectTimeout
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_not_exception_type
from xml.etree.ElementTree import ParseError

logger = util.logger

class JellyfinAPI(API):
    def __init__(self, client, *args, **kwargs):
        super().__init__(client, *args, **kwargs)

    def get_system_info(self):
        """Override to get system info"""
        return self._get("System/Info")

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
        
        # some api methods require a user context, so we store the user here
        self.user_id = self.jellyfin["user_id"]

        if self.jellyfin["verify_ssl"] is False and self.config.Requests.global_ssl is True:
            logger.debug("Overriding verify_ssl to False for Jellyfin connection")
            self.session = self.config.Requests.create_session(verify_ssl=False)
        if self.jellyfin["verify_ssl"] is True and self.config.Requests.global_ssl is False:
            logger.debug("Overriding verify_ssl to True for Jellyfin connection")
            self.session = self.config.Requests.create_session()

        self.token = self.jellyfin["token"]
        self.timeout = self.jellyfin["timeout"]
        
        self.client = JellyfinClient()
        self.client.jellyfin = JellyfinAPI(self.client.http)
        self.client.config.data["auth.ssl"] = self.jellyfin["verify_ssl"]
        self.client.config.data["auth.user_id"] = self.user_id
        self.client.config.data["http.timeout"] = self.timeout

        logger.info(self.url)
        logger.secret(self.token)
        try:
            self.client.authenticate(
                {"Servers": [{"AccessToken": self.token, "address": self.url}]},
                discover=False
            )

            system_info = self.client.jellyfin.get_system_info()
            self._server_version = system_info.get("Version")
            self._server_name = system_info.get("ServerName")

            logger.info(f"Connected to server {self._server_name} version {self._server_version}")
        except Exception as e:
            logger.info(f"Jellyfin Error: Jellyfin connection attempt failed")
            logger.stacktrace()
            raise Failed(f"Jellyfin Error: {e}")
        
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
    
    def item_labels(self, item, labels):
        raise NotImplementedError("Jellyfin item_labels method not implemented yet")
    
    def item_posters(self, item):
        raise NotImplementedError("Jellyfin item_posters method not implemented yet")
    
    def notify(self, message, title=None, level="info", sound=False):
        raise NotImplementedError("Jellyfin notify method not implemented yet")
    
    def notify_delete(self, message_id):
        raise NotImplementedError("Jellyfin notify_delete method not implemented yet")
    
    def reload(self):
        raise NotImplementedError("Jellyfin reload method not implemented yet")
    
    def upload_poster(self, item, image, tmdb=None, title=None):
        raise NotImplementedError("Jellyfin upload_poster method not implemented yet")

    def get_all(self, lib, media_type, include_collections=False):
        raise NotImplementedError("Jellyfin get_all_items method not implemented yet")