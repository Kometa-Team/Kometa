import logging

from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

base_url = "https://notifiarr.com/api/v1/"
dev_url = "https://dev.notifiarr.com/api/v1/"

class NotifiarrBase:
    def __init__(self, config, apikey, develop, test, error_notification):
        self.config = config
        self.apikey = apikey
        self.develop = develop
        self.test = test
        self.error_notification = error_notification

    def _request(self, path, json=None, params=None):
        url = f"{dev_url if self.develop else base_url}" + \
              ("notification/test" if self.test else f"{path}{self.apikey}")
        logger.debug(url)
        response = self.config.get(url, json=json, params={"event": "pmm"} if self.test else params)
        response_json = response.json()
        if self.develop or self.test:
            logger.debug(json)
            logger.debug("")
            logger.debug(response_json)
        if response.status_code >= 400 or ("response" in response_json and response_json["response"] == "error"):
            raise Failed(f"({response.status_code} [{response.reason}]) {response_json}")
        return response_json

    def error(self, text, library=None, collection=None, critical=True):
        if self.error_notification:
            json = {"error": str(text), "critical": critical}
            if library:
                json["server_name"] = library.PlexServer.friendlyName
                json["library_name"] = library.name
            if collection:
                json["collection"] = str(collection)
            self._request("notification/plex/", json=json, params={"event": "collections"})

class NotifiarrFactory(NotifiarrBase):
    def __init__(self, config, params):
        super().__init__(config, params["apikey"], params["develop"], params["test"], params["error_notification"])
        if not params["test"] and not self._request("user/validate/")["details"]["response"]:
            raise Failed("Notifiarr Error: Invalid apikey")

    def getNotifiarr(self, library):
        return Notifiarr(self.config, library, self.apikey, self.develop, self.test, self.error_notification)

class Notifiarr(NotifiarrBase):
    def __init__(self, config, library, apikey, develop, test, error_notification):
        super().__init__(config, apikey, develop, test, error_notification)
        self.library = library

    def plex_collection(self, collection, created=False, additions=None, removals=None):
        thumb = None
        if collection.thumb and next((f for f in collection.fields if f.name == "thumb"), None):
            thumb = self.config.get_image_encoded(f"{self.library.url}{collection.thumb}?X-Plex-Token={self.library.token}")
        art = None
        if collection.art and next((f for f in collection.fields if f.name == "art"), None):
            art = self.config.get_image_encoded(f"{self.library.url}{collection.art}?X-Plex-Token={self.library.token}")
        json = {
            "server_name": self.library.PlexServer.friendlyName,
            "library_name": self.library.name,
            "type": "movie" if self.library.is_movie else "show",
            "collection": collection.title,
            "created": created,
            "poster": thumb,
            "background": art
        }
        if additions:
            json["additions"] = additions
        if removals:
            json["removals"] = removals
        self._request("notification/plex/", json=json, params={"event": "collections"})
