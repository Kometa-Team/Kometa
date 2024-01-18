from json import JSONDecodeError
from modules import util
from modules.util import Failed
from retrying import retry

logger = util.logger

class Gotify:
    def __init__(self, config, params):
        self.config = config
        self.apikey = params["apikey"]
        self.url = params["url"]
        logger.secret(self.apikey)
        try:
            self.request(path="message")
        except JSONDecodeError:
            raise Failed("Gotify Error: Invalid JSON response received")

    def notification(self, json):
        return self.request(json=json)

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def request(self, json=None, path="message"):
        if not json:
            json = {
                "message": "Well hello there.",
                "priority": 1,
                "title": "This is first contact"
            }
        response = self.config.post(f"{self.url}{path}?token={self.apikey}", json=json)
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            logger.error(response.content)
            logger.debug(e)
            raise e
        if response.status_code >= 400 or ("result" in response_json and response_json["result"] == "error"):
            logger.debug(f"Response: {response_json}")
            raise Failed(f"({response.status_code} [{response.reason}]) {response_json}")
        if not response_json["id"]:
            raise Failed("Gotify Error: Invalid apikey")
        return response
