from modules import util
from modules.util import Failed

logger = util.logger

builders = ["reciperr_list", "stevenlu_popular"]

stevenlu_url = "https://s3.amazonaws.com/popular-movies/movies.json"

class Reciperr:
    def __init__(self, requests):
        self.requests = requests

    def _request(self, url, name="Reciperr"):
        response = self.requests.get(url)
        if response.status_code >= 400:
            raise Failed(f"{name} Error: JSON not found at {url}")
        return response.json()

    def validate_list(self, data):
        valid_lists = []
        for reciperr_list in util.get_list(data, split=False):
            if "imdb_id" not in self._request(reciperr_list)[0]:
                raise Failed(f"Reciperr Error: imdb_id not found in the JSON at {reciperr_list}")
            valid_lists.append(reciperr_list)
        return valid_lists

    def get_imdb_ids(self, method, data):
        name = "StevenLu" if method == "stevenlu_popular" else "Reciperr"
        logger.info(f"Processing {name} Movies")
        if method == "reciperr_list":
            ids = [(i["imdb_id"], "imdb") for i in self._request(data) if "imdb_id" in i]
        elif method == "stevenlu_popular":
            ids = [(i["imdb_id"], "imdb") for i in self._request(stevenlu_url, name="StevenLu")]
        else:
            raise Failed(f"Config Error: Method {method} not supported")
        if not ids:
            raise Failed(f"{name} Error: No IDs found.")
        return ids
