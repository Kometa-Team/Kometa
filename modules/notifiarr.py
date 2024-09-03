from json import JSONDecodeError
from modules import util
from modules.util import Failed
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_not_exception_type

logger = util.logger

base_url = "https://notifiarr.com/api/v1/"


class Notifiarr:
    def __init__(self, requests, params):
        self.requests = requests
        self.apikey = params["apikey"]
        self.header = {"X-API-Key": self.apikey}
        logger.secret(self.apikey)
        self._request(path="user", params={"fetch": "settings"})

    def notification(self, json):
        return self._request(json=json)

    @retry(stop=stop_after_attempt(6), wait=wait_fixed(10), retry=retry_if_not_exception_type(Failed))
    def _request(self, json=None, path="notification", params=None):
        response = self.requests.get(f"{base_url}{path}/pmm/", json=json, headers=self.header, params=params)
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            logger.debug(f"Content: {response.content}")
            logger.error(e)
            raise Failed("Notifiarr Error: Invalid JSON response received")
        if response.status_code >= 400 or ("result" in response_json and response_json["result"] == "error"):
            logger.debug(f"Response: {response_json}")
            raise Failed(f"({response.status_code} [{response.reason}]) {response_json}")
        if not response_json["details"]["response"]:
            raise Failed("Notifiarr Error: Invalid apikey")
        return response
