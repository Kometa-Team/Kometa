from modules import util
from modules.util import Failed

logger = util.logger

builders = ["reciperr_list", "stevenlu_popular"]

stevenlu_url = "https://s3.amazonaws.com/popular-movies/movies.json"

class Reciperr:
    def __init__(self, config):
        self.config = config

    def _request(self, url, name="Reciperr"):
        response = self.config.get(url)
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
        if method == "reciperr_list":
            logger.info(f"Processing Reciperr Movies")
            return [(i["imdb_id"], "imdb") for i in self._request(data)]
        elif method == "stevenlu_popular":
            logger.info(f"Processing StevenLu Popular Movies")
            return [(i["imdb_id"], "imdb") for i in self._request(stevenlu_url, name="StevenLu")]
        else:
            raise Failed(f"Reciperr Error: Method {method} not supported")
