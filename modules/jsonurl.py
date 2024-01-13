from modules import util
from modules.util import Failed
from plexapi.exceptions import BadRequest
from plexapi.video import Movie, Show

logger = util.logger

builders = ["json_url"]

class JsonUrl:
    def __init__(self, config):
        self.config = config
        #self.library = library

    def _request(self, url, name="JsonUrl"):
        response = self.config.get(url)
        if response.status_code >= 400:
            raise Failed(f"{name} Error: JSON not found at {url}")
        return response.json()

    def validate_list(self, data):
        valid_lists = []
        for json_list in util.get_list(data, split=False):
            if "rating_key" not in self._request(json_list).data[0]:
                raise Failed(f"JSON URL Error: JSON structure is invalid at {json_list}")
            valid_lists.append(json_list)
        return valid_lists

    def get_imdb_ids(self, method, data):
        name = "StevenLu" if method == "stevenlu_popular" else "Reciperr"
        logger.info(f"Processing {name} Movies")
        if method == "reciperr_list":
            ids = [(i["imdb_id"], "imdb") for i in self._request(data)]
        elif method == "stevenlu_popular":
            ids = [(i["imdb_id"], "imdb") for i in self._request(stevenlu_url, name="StevenLu")]
        else:
            raise Failed(f"Config Error: Method {method} not supported")
        if not ids:
            raise Failed(f"{name} Error: No IDs found.")
        return ids

    def get_rating_keys(self, method, data):
        logger.info(f"Processing JsonUrl found at: {data}")

        response = self._request(data)

        items = None
        for entry in response["data"]:
            if "rating_key" in entry:
                items = response["data"]
                break
        if items is None:
            raise Failed("JsonUrl Error: No Items found in the response")

        rating_keys = []
        for item in items:
            rating_keys.append((item["rating_key"], "ratingKey"))
        return rating_keys