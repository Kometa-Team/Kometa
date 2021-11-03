import logging

from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

base_url = "https://notifiarr.com/api/v1/"
dev_url = "https://dev.notifiarr.com/api/v1/"


class Notifiarr:
    def __init__(self, config, params):
        self.config = config
        self.apikey = params["apikey"]
        self.develop = params["develop"]
        self.test = params["test"]
        url, _ = self.get_url("user/validate/")
        response = self.config.get(url)
        response_json = response.json()
        if response.status_code >= 400 or ("result" in response_json and response_json["result"] == "error"):
            logger.debug(f"Response: {response_json}")
            raise Failed(f"({response.status_code} [{response.reason}]) {response_json}")
        if not params["test"] and not response_json["details"]["response"]:
            raise Failed("Notifiarr Error: Invalid apikey")

    def get_url(self, path):
        url = f"{dev_url if self.develop else base_url}{'notification/test' if self.test else f'{path}{self.apikey}'}"
        logger.debug(url.replace(self.apikey, "APIKEY"))
        params = {"event": "pmm" if self.test else "collections"}
        return url, params

