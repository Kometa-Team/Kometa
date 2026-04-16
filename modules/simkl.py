from modules import util
from modules.util import Failed

logger = util.logger

builders = ["simkl_trending", "simkl_dvd"]

base_url = "https://utilities.kometa.wiki/simkl-service"

trending_periods = ["today", "week", "month"]


class Simkl:
    def __init__(self, requests, cache):
        self.requests = requests
        self.cache = cache

    def _request(self, endpoint):
        url = f"{base_url}/{endpoint}"
        response = self.requests.get(url)
        if response.status_code >= 400:
            raise Failed(f"Simkl Error: {response.status_code} - {response.text}")
        return response.json()

    def validate_simkl_dict(self, error_type, method_name, method_data):
        if method_name == "simkl_trending":
            if isinstance(method_data, dict):
                dict_methods = {dm.lower(): dm for dm in method_data}
                period = util.parse(error_type, "period", method_data, methods=dict_methods, default="today").lower()
                if period not in trending_periods:
                    raise Failed(f"{error_type} Error: simkl_trending period must be one of {trending_periods}")
                limit = util.parse(error_type, "limit", method_data, datatype="int", methods=dict_methods, default=20, minimum=1, maximum=500)
            else:
                period = "today"
                limit = util.parse(error_type, method_name, method_data, datatype="int", default=20, minimum=1, maximum=500)
            return {"period": period, "limit": limit}
        elif method_name == "simkl_dvd":
            if isinstance(method_data, dict):
                dict_methods = {dm.lower(): dm for dm in method_data}
                limit = util.parse(error_type, "limit", method_data, datatype="int", methods=dict_methods, default=20, minimum=1, maximum=500)
            else:
                limit = util.parse(error_type, method_name, method_data, datatype="int", default=20, minimum=1, maximum=500)
            return {"limit": limit}
        raise Failed(f"{error_type} Error: {method_name} not supported")

    def get_simkl_ids(self, method, data, is_movie):
        if method == "simkl_trending":
            return self._get_trending_ids(data, is_movie)
        elif method == "simkl_dvd":
            return self._get_dvd_ids(data, is_movie)
        raise Failed(f"Simkl Error: Method {method} not supported")

    def _get_trending_ids(self, data, is_movie):
        period = data["period"]
        limit = data["limit"]
        size = "large" if limit > 100 else "small"

        logger.info(f"Processing Simkl Trending ({period}, limit={limit})")
        response = self._request(f"trending/{period}/{size}")

        results = []
        if is_movie is True:
            sections = [("movies", "tmdb", None)]
        elif is_movie is False:
            sections = [("tv", "tmdb_show", "tvdb"), ("anime", "tmdb_show", "tvdb")]
        else:
            sections = [("movies", "tmdb", None), ("tv", "tmdb_show", "tvdb"), ("anime", "tmdb_show", "tvdb")]

        for section, tmdb_type, tvdb_type in sections:
            for item in response.get(section, []):
                if len(results) >= limit:
                    break
                ids = item.get("ids", {})
                tmdb_id = util.check_num(ids.get("tmdb"))
                tvdb_id = util.check_num(ids.get("tvdb"))
                if tmdb_id:
                    results.append((tmdb_id, tmdb_type))
                elif tvdb_type and tvdb_id:
                    results.append((tvdb_id, tvdb_type))

        logger.info(f"Simkl Trending: {len(results)} IDs found")
        return results

    def _get_dvd_ids(self, data, is_movie):
        limit = data["limit"]
        size = "large" if limit > 100 else "small"

        logger.info(f"Processing Simkl DVD Releases (limit={limit})")
        response = self._request(f"dvd/{size}")

        results = []
        for item in response:
            if len(results) >= limit:
                break
            ids = item.get("ids", {})
            tmdb_id = util.check_num(ids.get("tmdb"))
            tvdb_id = util.check_num(ids.get("tvdb"))
            is_show = bool(tvdb_id)

            if is_movie is None:
                if not is_show and tmdb_id:
                    results.append((tmdb_id, "tmdb"))
                elif is_show and tvdb_id:
                    results.append((tvdb_id, "tvdb"))
            elif is_movie and not is_show and tmdb_id:
                results.append((tmdb_id, "tmdb"))
            elif not is_movie and is_show and tvdb_id:
                results.append((tvdb_id, "tvdb"))

        logger.info(f"Simkl DVD: {len(results)} IDs found")
        return results
