from json import JSONDecodeError
from modules import util
from modules.util import Failed

logger = util.logger

base_url = "https://notifiarr.com/api/v1/"


class Notifiarr:
    def __init__(self, config, params):
        self.config = config
        self.apikey = params["apikey"]
        self.header = {"X-API-Key": self.apikey}
        logger.secret(self.apikey)
        response = self.config.get(f"{base_url}user/pmm/", headers=self.header, params={"fetch": "settings"})
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            logger.debug(e)
            raise Failed("Notifiarr Error: Invalid response")
        if response.status_code >= 400 or ("result" in response_json and response_json["result"] == "error"):
            logger.debug(f"Response: {response_json}")
            raise Failed(f"({response.status_code} [{response.reason}]) {response_json}")
        if not response_json["details"]["response"]:
            raise Failed("Notifiarr Error: Invalid apikey")

    def notification(self, json):
        return self.config.get(f"{base_url}notification/pmm/", json=json, headers=self.header)
