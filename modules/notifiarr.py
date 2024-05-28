from json import JSONDecodeError
from modules import util
from modules.util import Failed
from retrying import retry

logger = util.logger

base_url = "https://notifiarr.com/api/v1/"


class Notifiarr:
    def __init__(self, requests, params):
        self.requests = requests
        self.apikey = params["apikey"]
        self.header = {"X-API-Key": self.apikey}
        logger.secret(self.apikey)
        try:
            self.request(path="user", params={"fetch": "settings"})
        except JSONDecodeError:
            raise Failed("Notifiarr Error: Invalid JSON response received")

    def notification(self, json):
        return self.request(json=json)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def request(self, json=None, path="notification", params=None):
        response = self.requests.get(f"{base_url}{path}/pmm/", json=json, headers=self.header, params=params)
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            logger.error(response.content)
            logger.debug(e)
            raise e
        if response.status_code >= 400 or ("result" in response_json and response_json["result"] == "error"):
            logger.debug(f"Response: {response_json}")
            raise Failed(f"({response.status_code} [{response.reason}]) {response_json}")
        if not response_json["details"]["response"]:
            raise Failed("Notifiarr Error: Invalid apikey")
        return response
