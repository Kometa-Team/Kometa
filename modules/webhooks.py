import logging
from json import JSONDecodeError

from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

class Webhooks:
    def __init__(self, config, system_webhooks, library=None, notifiarr=None):
        self.config = config
        self.error_webhooks = system_webhooks["error"] if "error" in system_webhooks else []
        self.run_start_webhooks = system_webhooks["run_start"] if "run_start" in system_webhooks else []
        self.run_end_webhooks = system_webhooks["run_end"] if "run_end" in system_webhooks else []
        self.library = library
        self.notifiarr = notifiarr

    def _request(self, webhooks, json):
        if self.config.trace_mode:
            logger.debug("")
            logger.debug(f"JSON: {json}")
        for webhook in list(set(webhooks)):
            if self.config.trace_mode:
                logger.debug(f"Webhook: {webhook}")
            if webhook == "notifiarr":
                url, params = self.notifiarr.get_url("notification/plex/")
                for x in range(6):
                    response = self.config.get(url, json=json, params=params)
                    if response.status_code < 500:
                        break
            else:
                response = self.config.post(webhook, json=json)
            try:
                response_json = response.json()
                if self.config.trace_mode:
                    logger.debug(f"Response: {response_json}")
                if "result" in response_json and response_json["result"] == "error" and "details" in response_json and "response" in response_json["details"]:
                    raise Failed(f"Notifiarr Error: {response_json['details']['response']}")
                if response.status_code >= 400 or ("result" in response_json and response_json["result"] == "error"):
                    raise Failed(f"({response.status_code} [{response.reason}]) {response_json}")
            except JSONDecodeError:
                if response.status_code >= 400:
                    raise Failed(f"({response.status_code} [{response.reason}])")

    def start_time_hooks(self, start_time):
        if self.run_start_webhooks:
            self._request(self.run_start_webhooks, {"start_time": start_time})

    def end_time_hooks(self, start_time, run_time, stats):
        if self.run_end_webhooks:
            self._request(self.run_end_webhooks, {
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "run_time": run_time,
                "collections_created": stats["created"],
                "collections_modified": stats["modified"],
                "collections_deleted": stats["deleted"],
                "items_added": stats["added"],
                "items_removed": stats["removed"],
                "added_to_radarr": stats["radarr"],
                "added_to_sonarr": stats["sonarr"],
            })

    def error_hooks(self, text, library=None, collection=None, critical=True):
        if self.error_webhooks:
            json = {"error": str(text), "critical": critical}
            if library:
                json["server_name"] = library.PlexServer.friendlyName
                json["library_name"] = library.name
            if collection:
                json["collection"] = str(collection)
            self._request(self.error_webhooks, json)

    def collection_hooks(self, webhooks, collection, created=False, additions=None, removals=None):
        if self.library:
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
            self._request(webhooks, json)
