from modules import util
from modules.util import Failed

logger = util.logger

base_url = "https://raw.githubusercontent.com/meisnate12/PMM-TOP10/master/"
builders = ["flixpatrol_top"]


class FlixPatrol:
    def __init__(self, config):
        self.config = config
        self._platforms = None
        self._locations = None
        self.country_data = {}

    def load_info(self):
        info = self.config.load_yaml(f"{base_url}info.yml")
        self._platforms = info["platforms"]
        self._locations = info["locations"]

    def get_country(self, country):
        if country not in self.country_data:
            self.country_data[country] = self.config.load_yaml(f"{base_url}lists/{country}.yml")
        return self.country_data[country]

    @property
    def platforms(self):
        if self._platforms is None:
            self.load_info()
        return self._platforms

    @property
    def locations(self):
        if self._locations is None:
            self.load_info()
        return self._locations

    def get_tmdb_ids(self, method, data, is_movie):
        flix_items = []
        media_type = "movies" if is_movie else "shows"
        if method == "flixpatrol_top":
            logger.info(f"Processing FlixPatrol Top {media_type.capitalize()}:")
            logger.info(f"\tPlatform: {data['platform'].replace('_', ' ').title()}")
            logger.info(f"\tLocation: {data['location'].replace('_', ' ').title()}")
            logger.info(f"\tIn The Last: {data['in_the_last']}")
            logger.info(f"\tLimit: {data['limit']}")
            country_info = self.get_country(data["location"])
            for key in [k for k in country_info][:data["in_the_last"]]:
                if data["platform"] in country_info[key] and media_type in country_info[key][data["platform"]]:
                    for item in country_info[key][data["platform"]][media_type]:
                        if item not in flix_items and len(flix_items) < data["limit"]:
                            flix_items.append(item)
        items = [(i, "tmdb" if is_movie else "tmdb_show") for i in flix_items]
        if len(items) > 0:
            logger.info(f"Processed {len(items)} TMDb IDs")
            return items
        else:
            raise Failed(f"FlixPatrol Error: No {media_type.capitalize()} Found for {data['platform'].replace('_', ' ').title()} in {data['location'].replace('_', ' ').title()}")
