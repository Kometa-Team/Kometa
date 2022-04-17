from json import JSONDecodeError
from modules import util
from modules.util import Failed

logger = util.logger

class Webhooks:
    def __init__(self, config, system_webhooks, library=None, notifiarr=None):
        self.config = config
        self.error_webhooks = system_webhooks["error"] if "error" in system_webhooks else []
        self.version_webhooks = system_webhooks["version"] if "version" in system_webhooks else []
        self.run_start_webhooks = system_webhooks["run_start"] if "run_start" in system_webhooks else []
        self.run_end_webhooks = system_webhooks["run_end"] if "run_end" in system_webhooks else []
        self.library = library
        self.notifiarr = notifiarr

    def _request(self, webhooks, json):
        if self.config.trace_mode:
            logger.separator("Webhooks", space=False, border=False, debug=True)
            logger.debug("")
            logger.debug(f"JSON: {json}")
        for webhook in list(set(webhooks)):
            response = None
            if self.config.trace_mode:
                logger.debug(f"Webhook: {webhook}")
            if webhook == "notifiarr":
                if self.notifiarr:
                    url, params = self.notifiarr.get_url("notification/pmm/")
                    for x in range(6):
                        response = self.config.get(url, json=json, params=params)
                        if response.status_code < 500:
                            break
            else:
                response = self.config.post(webhook, json=json)
            if response:
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
            self._request(self.run_start_webhooks, {"start_time": start_time.strftime("%Y-%m-%d %H:%M:%S")})

    def version_hooks(self, version, latest_version):
        if self.version_webhooks:
            notes = None
            if version[1] != latest_version[1]:
                notes = self.config.GitHub.latest_release_notes()
            elif version[2] and version[2] < latest_version[2]:
                notes = self.config.GitHub.get_develop_commits(version[2])
            self._request(self.version_webhooks, {"current": version[0], "latest": latest_version[0], "notes": notes})

    def end_time_hooks(self, start_time, end_time, run_time, stats):
        if self.run_end_webhooks:
            self._request(self.run_end_webhooks, {
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "run_time": run_time,
                "collections_created": stats["created"],
                "collections_modified": stats["modified"],
                "collections_deleted": stats["deleted"],
                "items_added": stats["added"],
                "items_removed": stats["removed"],
                "added_to_radarr": stats["radarr"],
                "added_to_sonarr": stats["sonarr"],
                "names": stats["names"]
            })

    def error_hooks(self, text, server=None, library=None, collection=None, playlist=None, critical=True):
        if self.error_webhooks:
            json = {"error": str(text), "critical": critical}
            if server:          json["server_name"] = str(server)
            if library:         json["library_name"] = str(library)
            if collection:      json["collection"] = str(collection)
            if playlist:        json["playlist"] = str(playlist)
            self._request(self.error_webhooks, json)

    def collection_hooks(self, webhooks, collection, poster_url=None, background_url=None, created=False, deleted=False,
                         additions=None, removals=None, radarr=None, sonarr=None, playlist=False):
        if self.library:
            thumb = None
            if not poster_url and collection.thumb and next((f for f in collection.fields if f.name == "thumb"), None):
                thumb = self.config.get_image_encoded(f"{self.library.url}{collection.thumb}?X-Plex-Token={self.library.token}")
            art = None
            if not playlist and not background_url and collection.art and next((f for f in collection.fields if f.name == "art"), None):
                art = self.config.get_image_encoded(f"{self.library.url}{collection.art}?X-Plex-Token={self.library.token}")
            self._request(webhooks, {
                "server_name": self.library.PlexServer.friendlyName,
                "library_name": self.library.name,
                "playlist" if playlist else "collection": collection.title,
                "created": created,
                "deleted": deleted,
                "poster": thumb,
                "background": art,
                "poster_url": poster_url,
                "background_url": background_url,
                "additions": additions if additions else [],
                "removals": removals if removals else [],
                "radarr_adds": radarr if radarr else [],
                "sonarr_adds": sonarr if sonarr else [],
            })
