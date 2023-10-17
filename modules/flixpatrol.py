from modules import util
from modules.util import Failed

logger = util.logger

ids_url = "https://raw.githubusercontent.com/meisnate12/PMM-TOP10/master/top10.yml"
builders = ["flixpatrol_top"]


class FlixPatrol:
    def __init__(self, config):
        self.config = config
        self._data = None
        self._platforms = None
        self._locations = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.config.load_yaml(ids_url)
        return self._data

    @property
    def platforms(self):
        if self._platforms is None:
            self._platforms = [platform for platform in self.data]
            self._platforms.sort()
        return self._platforms

    @property
    def locations(self):
        if self._locations is None:
            self._locations = []
            for platform in self.data:
                self._locations.extend([loc for loc in self.data[platform] if loc not in self._locations and loc != "world"])
            self._locations.sort()
            self._locations = ["world"] + self._locations
        return self._locations

    def get_tmdb_ids(self, method, data, is_movie):
        if method == "flixpatrol_top":
            logger.info("Processing FlixPatrol Top:")
            logger.info(f"\tPlatform: {data['platform'].replace('_', ' ').title()}")
            logger.info(f"\tLocation: {data['location'].replace('_', ' ').title()}")
            logger.info(f"\tLimit: {data['limit']}")
        total_items = self.data[data["platform"]][data["location"]]["movies" if is_movie else "shows"][:data["limit"]]
        if total_items > 0:
            logger.info(f"Processed {total_items} TMDb IDs")
            return total_items
        else:
            raise Failed(f"FlixPatrol Error: No List Items found in {data}")
