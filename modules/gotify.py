from json import JSONDecodeError
from modules import util
from modules.util import Failed

logger = util.logger

class Gotify:
    def __init__(self, requests, params):
        self.requests = requests
        self.token = params["token"]
        self.url = params["url"].rstrip("/")
        logger.secret(self.url)
        logger.secret(self.token)
        try:
            logger.info(f"Gotify Version: {self._request(path='version', post=False)['version']}")
        except Exception:
            logger.stacktrace()
            raise Failed("Gotify Error: Invalid URL")

    def _request(self, path="message", json=None, post=True):
        if post:
            response = self.requests.post(f"{self.url}/{path}", headers={"X-Gotify-Key": self.token}, json=json)
        else:
            response = self.requests.get(f"{self.url}/{path}")
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            logger.error(response.content)
            logger.debug(e)
            raise e
        if response.status_code >= 400:
            raise Failed(f"({response.status_code} [{response.reason}]) {response_json['errorDescription']}")
        return response_json

    def notification(self, json):
        message = ""
        if json["event"] == "run_end":
            title = "Run Completed"
            message = f"Start Time: {json['start_time']}\n" \
                      f"End Time: {json['end_time']}\n" \
                      f"Run Time: {json['run_time']}\n" \
                      f"Collections Created: {json['collections_created']}\n" \
                      f"Collections Modified: {json['collections_modified']}\n" \
                      f"Collections Deleted: {json['collections_deleted']}\n" \
                      f"Items Added: {json['items_added']}\n" \
                      f"Items Removed: {json['items_removed']}"
            if json["added_to_radarr"]:
                message += f"\n{json['added_to_radarr']} Movies Added To Radarr"
            if json["added_to_sonarr"]:
                message += f"\n{json['added_to_sonarr']} Movies Added To Sonarr"
        elif json["event"] == "run_start":
            title = "Run Started"
            message = json["start_time"]
        elif json["event"] == "version":
            title = "New Version Available"
            message = f"Current: {json['current']}\n" \
                      f"Latest: {json['latest']}\n" \
                      f"Notes: {json['notes']}"
        elif json["event"] == "delete":
            if "library_name" in json:
                title = "Collection Deleted"
            else:
                title = "Playlist Deleted"
            message = json["message"]
        else:
            new_line = "\n"
            if "server_name" in json:
                message += f"{new_line if message else ''}Server: {json['server_name']}"
            if "library_name" in json:
                message += f"{new_line if message else ''}Library: {json['library_name']}"
            if "collection" in json:
                message += f"{new_line if message else ''}Collection: {json['collection']}"
            if "playlist" in json:
                message += f"{new_line if message else ''}Playlist: {json['playlist']}"
            if json["event"] == "error":
                if "collection" in json:
                    title_name = "Collection"
                elif "playlist" in json:
                    title_name = "Playlist"
                elif "library_name" in json:
                    title_name = "Library"
                else:
                    title_name = "Global"
                title = f"{'Critical ' if json['critical'] else ''}{title_name} Error"
                message += f"{new_line if message else ''}Error Message: {json['error']}"
            else:
                title = f"{'Collection' if 'collection' in json else 'Playlist'} {'Created' if json['created'] else 'Modified'}"
                if json['radarr_adds']:
                    message += f"{new_line if message else ''}{len(json['radarr_adds'])} Radarr Additions:"
                if json['sonarr_adds']:
                    message += f"{new_line if message else ''}{len(json['sonarr_adds'])} Sonarr Additions:"
                message += f"{new_line if message else ''}{len(json['additions'])} Additions:"
                for add_dict in json['additions']:
                    message += f"\n{add_dict['title']}"
                message += f"{new_line if message else ''}{len(json['removals'])} Removals:"
                for add_dict in json['removals']:
                    message += f"\n{add_dict['title']}"

        self._request(json={"message": message, "title": title})
