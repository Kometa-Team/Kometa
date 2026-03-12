from modules import util
from modules.util import Failed

logger = util.logger

builders = ["stevenlu_popular"]

stevenlu_url = "https://s3.amazonaws.com/popular-movies/movies.json"


class StevenLu:
    def __init__(self, requests):
        self.requests = requests

    def _request(self, url):
        response = self.requests.get(url)
        if response.status_code >= 400:
            raise Failed(f"StevenLu Error: JSON not found at {url}")
        return response.json()

    def get_imdb_ids(self, method, data):
        logger.info("Processing StevenLu Movies")
        if method == "stevenlu_popular":
            id_data = self._request(stevenlu_url) or []
        else:
            raise Failed(f"Config Error: Method {method} not supported")
        ids = [(i["imdb_id"], "imdb") for i in id_data if "imdb_id" in i]
        if not ids:
            if id_data:
                logger.error(f"StevenLu Error Data: {id_data}")
            raise Failed("StevenLu Error: No IDs found.")
        return ids
