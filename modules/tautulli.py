import logging, requests
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class TautulliAPI:
    def __init__(self, params):
        try:
            response = requests.get("{}/api/v2?apikey={}&cmd=get_library_names".format(params["url"], params["apikey"])).json()
        except Exception:
            util.print_stacktrace()
            raise Failed("Tautulli Error: Invalid url")
        if response["response"]["result"] != "success":
            raise Failed("Tautulli Error: {}".format(response["response"]["message"]))
        self.url = params["url"]
        self.apikey = params["apikey"]

    def get_popular(self, library, time_range=30, stats_count=20, stats_count_buffer=20, status_message=True):
        return self.get_items(library, time_range=time_range, stats_count=stats_count, list_type="popular", stats_count_buffer=stats_count_buffer, status_message=status_message)

    def get_top(self, library, time_range=30, stats_count=20, stats_count_buffer=20, status_message=True):
        return self.get_items(library, time_range=time_range, stats_count=stats_count, list_type="top", stats_count_buffer=stats_count_buffer, status_message=status_message)

    def get_items(self, library, time_range=30, stats_count=20, list_type="popular", stats_count_buffer=20, status_message=True):
        if status_message:
            logger.info("Processing Tautulli Most {}: {} {}".format("Popular" if list_type == "popular" else "Watched", stats_count, "Movies" if library.is_movie else "Shows"))
        response = self.send_request("{}/api/v2?apikey={}&cmd=get_home_stats&time_range={}&stats_count={}".format(self.url, self.apikey, time_range, int(stats_count) + int(stats_count_buffer)))
        stat_id = "{}_{}".format("popular" if list_type == "popular" else "top", "movies" if library.is_movie else "tv")

        items = None
        for entry in response["response"]["data"]:
            if entry["stat_id"] == stat_id:
                items = entry["rows"]
                break
        if items is None:
            raise Failed("Tautulli Error: No Items found in the response")

        section_id = self.get_section_id(library.name)
        rating_keys = []
        count = 0
        for item in items:
            if item["section_id"] == section_id and count < int(stats_count):
                rating_keys.append(item["rating_key"])
                count += 1
        return rating_keys

    def get_section_id(self, library_name):
        response = self.send_request("{}/api/v2?apikey={}&cmd=get_library_names".format(self.url, self.apikey))
        section_id = None
        for entry in response["response"]["data"]:
            if entry["section_name"] == library_name:
                section_id = entry["section_id"]
                break
        if section_id:              return section_id
        else:                       raise Failed("Tautulli Error: No Library named {} in the response".format(library_name))

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_request(self, url):
        logger.debug("Tautulli URL: {}".format(url.replace(self.apikey, "################################")))
        return requests.get(url).json()
