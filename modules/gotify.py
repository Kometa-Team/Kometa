from json import JSONDecodeError
from modules import util, webhooks
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
        message, title, _ = webhooks.get_message(json)
        self._request(json={"message": message, "title": title})
