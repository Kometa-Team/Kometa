import logging
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

builders = ["mdblist_list"]
base_url = "https://mdblist.com/lists"

headers = { 'User-Agent': 'Plex-Meta-Manager' }

class Mdblist:
    def __init__(self, config):
        self.config = config

    def get_mdblist_ids(self, method, data):
        if method == "mdblist_list":
            logger.info(f"Processing Mdblist.com List: {data}")
            return [(i["imdb_id"], "imdb") for i in self.config.get_json(data,headers=headers)]
        else:
            raise Failed(f"Mdblist Error: Method {method} not supported")
