from modules import util
from modules.util import Failed
from plexapi.exceptions import BadRequest, NotFound
from plexapi.video import Movie, Show

logger = util.logger

builders = ["tautulli_popular", "tautulli_watched"]

class Tautulli:
    def __init__(self, config, library, params):
        self.config = config
        self.library = library
        self.url = params["url"]
        self.apikey = params["apikey"]
        logger.secret(self.url)
        logger.secret(self.apikey)
        try:
            response = self._request(f"{self.url}/api/v2?apikey={self.apikey}&cmd=get_library_names")
        except Exception:
            logger.stacktrace()
            raise Failed("Tautulli Error: Invalid url")
        if response["response"]["result"] != "success":
            raise Failed(f"Tautulli Error: {response['response']['message']}")

    def get_rating_keys(self, library, params, all_items):
        query_size = int(params["list_size"]) + int(params["list_buffer"])
        logger.info(f"Processing Tautulli Most {params['list_type'].capitalize()}: {params['list_size']} {'Movies' if library.is_movie else 'Shows'}")
        response = self._request(f"{self.url}/api/v2?apikey={self.apikey}&cmd=get_home_stats&time_range={params['list_days']}&stats_count={query_size}")
        stat_id = f"{'popular' if params['list_type'] == 'popular' else 'top'}_{'movies' if library.is_movie else 'tv'}"
        stat_type = "users_watched" if params['list_type'] == 'popular' else "total_plays"

        items = None
        for entry in response["response"]["data"]:
            if entry["stat_id"] == stat_id:
                items = entry["rows"]
                break
        if items is None:
            raise Failed("Tautulli Error: No Items found in the response")

        section_id = self._section_id(library.name)
        rating_keys = []
        for item in items:
            if (all_items or item["section_id"] == section_id) and len(rating_keys) < int(params['list_size']):
                if int(item[stat_type]) < params['list_minimum']:
                    continue
                try:
                    plex_item = library.fetchItem(int(item["rating_key"]))
                    if not isinstance(plex_item, (Movie, Show)):
                        raise BadRequest
                    rating_keys.append((item["rating_key"], "ratingKey"))
                except (BadRequest, NotFound):
                    new_item = library.exact_search(item["title"], year=item["year"])
                    if new_item:
                        rating_keys.append((new_item[0].ratingKey, "ratingKey"))
                    else:
                        logger.error(f"Plex Error: Item {item} not found")
        logger.debug("")
        logger.debug(f"{len(rating_keys)} Keys Found: {rating_keys}")
        return rating_keys

    def _section_id(self, library_name):
        response = self._request(f"{self.url}/api/v2?apikey={self.apikey}&cmd=get_library_names")
        section_id = None
        for entry in response["response"]["data"]:
            if entry["section_name"] == library_name:
                section_id = entry["section_id"]
                break
        if section_id:              return section_id
        else:                       raise Failed(f"Tautulli Error: No Library named {library_name} in the response")

    def _request(self, url):
        if self.config.trace_mode:
            logger.debug(f"Tautulli URL: {url}")
        return self.config.get_json(url)
