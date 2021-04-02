import logging, re, requests
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class RadarrAPI:
    def __init__(self, tmdb, params):
        self.url_params = {"apikey": f"{params['token']}"}
        self.base_url = f"{params['url']}/api{'/v3' if params['version'] == 'v3' else ''}/"
        try:
            result = requests.get(f"{self.base_url}system/status", params=self.url_params).json()
        except Exception:
            util.print_stacktrace()
            raise Failed(f"Radarr Error: Could not connect to Radarr at {params['url']}")
        if "error" in result and result["error"] == "Unauthorized":
            raise Failed("Radarr Error: Invalid API Key")
        if "version" not in result:
            raise Failed("Radarr Error: Unexpected Response Check URL")
        self.quality_profile_id = None
        profiles = ""
        for profile in self.send_get("qualityProfile" if params["version"] == "v3" else "profile"):
            if len(profiles) > 0:
                profiles += ", "
            profiles += profile["name"]
            if profile["name"] == params["quality_profile"]:
                self.quality_profile_id = profile["id"]
        if not self.quality_profile_id:
            raise Failed(f"Radarr Error: quality_profile: {params['quality_profile']} does not exist in radarr. Profiles available: {profiles}")
        self.tmdb = tmdb
        self.url = params["url"]
        self.version = params["version"]
        self.token = params["token"]
        self.root_folder_path = params["root_folder_path"]
        self.add = params["add"]
        self.search = params["search"]
        self.tag = params["tag"]

    def add_tmdb(self, tmdb_ids, tag=None, folder=None):
        logger.info("")
        logger.debug(f"TMDb IDs: {tmdb_ids}")
        tag_nums = []
        add_count = 0
        if tag is None:
            tag = self.tag
        if tag:
            tag_cache = {}
            for label in tag:
                self.send_post("tag", {"label": str(label)})
            for t in self.send_get("tag"):
                tag_cache[t["label"]] = t["id"]
            for label in tag:
                if label in tag_cache:
                    tag_nums.append(tag_cache[label])
        for tmdb_id in tmdb_ids:
            try:
                movie = self.tmdb.get_movie(tmdb_id)
            except Failed as e:
                logger.error(e)
                continue

            try:
                year = movie.release_date.split("-")[0]
            except AttributeError:
                logger.error(f"TMDb Error: No year for ({tmdb_id}) {movie.title}")
                continue

            if year.isdigit() is False:
                logger.error(f"TMDb Error: No release date yet for ({tmdb_id}) {movie.title}")
                continue

            poster = f"https://image.tmdb.org/t/p/original{movie.poster_path}"

            titleslug = re.sub(r"([^\s\w]|_)+", "", f"{movie.title} {year}").replace(" ", "-").lower()

            url_json = {
                "title": movie.title,
                f"{'qualityProfileId' if self.version == 'v3' else 'profileId'}": self.quality_profile_id,
                "year": int(year),
                "tmdbid": int(tmdb_id),
                "titleslug": titleslug,
                "monitored": True,
                "rootFolderPath": self.root_folder_path if folder is None else folder,
                "images": [{"covertype": "poster", "url": poster}],
                "addOptions": {"searchForMovie": self.search}
            }
            if tag_nums:
                url_json["tags"] = tag_nums
            response = self.send_post("movie", url_json)
            if response.status_code < 400:
                logger.info(f"Added to Radarr | {tmdb_id:<6} | {movie.title}")
                add_count += 1
            else:
                try:
                    logger.error(f"Radarr Error: ({tmdb_id}) {movie.title}: ({response.status_code}) {response.json()[0]['errorMessage']}")
                except KeyError:
                    logger.debug(url_json)
                    logger.error(f"Radarr Error: {response.json()}")
        logger.info(f"{add_count} Movie{'s' if add_count > 1 else ''} added to Radarr")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_get(self, url):
        return requests.get(f"{self.base_url}{url}", params=self.url_params).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_post(self, url, url_json):
        return requests.post(f"{self.base_url}{url}", json=url_json, params=self.url_params)
