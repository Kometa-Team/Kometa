from modules import util, webhooks
from modules.util import Failed

logger = util.logger


class Ntfy:
    def __init__(self, requests, params):
        self.requests = requests
        self.token = params["token"]
        self.url = params["url"].rstrip("/")
        self.topic = params["topic"]

        logger.secret(self.url)
        logger.secret(self.token)

        self._test_url()

    def _test_url(self):
        try:
            self._request(message="Kometa - Testing ntfy Access", priority=1)
        except Exception:
            logger.stacktrace()
            raise Failed("ntfy Error: Invalid details")

    def _request(self, message: str, title: str = None, priority: int = 3):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Icon": "https://kometa.wiki/en/latest/assets/icon.png",
            "Priority": str(priority)
        }
        if title:
            headers["Title"] = title

        response = self.requests.post(f"{self.url}/{self.topic}", headers=headers, data=message)

        if not response:
            raise Failed(f"({response.status_code} [{response.reason}]) {response.content}")

        return response

    def notification(self, json):
        message, title, priority = webhooks.get_message(json)
        self._request(message=message, title=title, priority=priority)
