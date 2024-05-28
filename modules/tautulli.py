from modules import util
from modules.util import Failed
from plexapi.exceptions import BadRequest
from plexapi.video import Movie, Show

logger = util.logger

builders = ["tautulli_popular", "tautulli_watched"]

class Tautulli:
    def __init__(self, requests, library, params):
        self.requests = requests
        self.library = library
        self.url = params["url"]
        self.apikey = params["apikey"]
        self.api = f"{self.url}/api/v2"
        logger.secret(self.url)
        logger.secret(self.apikey)
        try:
            response = self._request("get_tautulli_info")
        except Exception:
            logger.stacktrace()
            raise Failed("Tautulli Error: Invalid URL")
        if response["response"]["result"] != "success":
            raise Failed(f"Tautulli Error: {response['response']['message']}")
        self.has_section = True if int(response["response"]["data"]["tautulli_version"].split(".")[1]) > 11 else False
        self.section_id = self.library.Plex.key

    def get_rating_keys(self, data, all_items):
        logger.info(f"Processing Tautulli Most {data['list_type'].capitalize()}: {data['list_size']} {'Movies' if self.library.is_movie else 'Shows'}")
        params = {"time_range": data["list_days"], "stats_count": int(data["list_size"]) + int(data["list_buffer"])}
        if self.has_section and not all_items:
            params["section_id"] = self.section_id
        response = self._request("get_home_stats", params=params)
        stat_id = f"{'popular' if data['list_type'] == 'popular' else 'top'}_{'movies' if self.library.is_movie else 'tv'}"
        stat_type = "users_watched" if data['list_type'] == 'popular' else "total_plays"

        items = None
        for entry in response["response"]["data"]:
            if entry["stat_id"] == stat_id:
                items = entry["rows"]
                break
        if items is None:
            raise Failed("Tautulli Error: No Items found in the response")

        rating_keys = []
        for item in items:
            if (all_items or item["section_id"] == self.section_id) and len(rating_keys) < int(data['list_size']):
                if int(item[stat_type]) < data['list_minimum']:
                    continue
                try:
                    plex_item = self.library.fetch_item(int(item["rating_key"]))
                    if not isinstance(plex_item, (Movie, Show)):
                        raise BadRequest
                    rating_keys.append((item["rating_key"], "ratingKey"))
                except Failed as e:
                    new_item = self.library.exact_search(item["title"], year=item["year"])
                    if new_item:
                        rating_keys.append((new_item[0].ratingKey, "ratingKey"))
                    else:
                        logger.error(e)
        return rating_keys

    def _request(self, cmd, params=None):
        logger.trace(f"Tautulli CMD: {cmd}")
        if params:
            logger.trace(f"Tautulli Params: {params}")
        final_params = {"apikey": self.apikey, "cmd": cmd}
        if params:
            for k, v in params.items():
                final_params[k] = v
        return self.requests.get_json(self.api, params=final_params)
