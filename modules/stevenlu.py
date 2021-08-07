import logging
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

builders = ["stevenlu_popular"]
base_url = "https://s3.amazonaws.com/popular-movies/movies.json"

class StevenLu:
    def __init__(self, config):
        self.config = config

    def get_stevenlu_ids(self, method):
        if method == "stevenlu_popular":
            logger.info(f"Processing StevenLu Popular Movies")
            return [(i["imdb_id"], "imdb") for i in self.config.get_json(base_url)]
        else:
            raise Failed(f"StevenLu Error: Method {method} not supported")
