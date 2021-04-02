import logging, re, requests
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class RadarrAPI:
    def __init__(self, params):
        self.base_url = f"{params['url']}/api{'/v3' if params['version'] == 'v3' else ''}/"
        self.token = params["token"]
        try:
            result = requests.get(f"{self.base_url}system/status", params={"apikey": f"{self.token}"}).json()
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
        self.tags = self.get_tags()
        self.url = params["url"]
        self.version = params["version"]
        self.token = params["token"]
        self.root_folder_path = params["root_folder_path"]
        self.add = params["add"]
        self.search = params["search"]
        self.tag = params["tag"]

    def get_tags(self):
        return {tag["label"]: tag["id"] for tag in self.send_get("tag")}

    def add_tags(self, tags):
        added = False
        for label in tags:
            if label not in self.tags:
                added = True
                self.send_post("tag", {"label": str(label)})
        if added:
            self.tags = self.get_tags()

    def lookup(self, tmdb_id):
        results = self.send_get("movie/lookup", params={"term": f"tmdb:{tmdb_id}"})
        if results:
            return results[0]
        else:
            raise Failed(f"Sonarr Error: TMDb ID: {tmdb_id} not found")

    def add_tmdb(self, tmdb_ids, tags=None, folder=None):
        logger.info("")
        logger.debug(f"TMDb IDs: {tmdb_ids}")
        tag_nums = []
        add_count = 0
        if tags is None:
            tags = self.tag
        if tags:
            self.add_tags(tags)
            tag_nums = [self.tags[label] for label in tags if label in self.tags]
        for tmdb_id in tmdb_ids:
            try:
                movie_info = self.lookup(tmdb_id)
            except Failed as e:
                logger.error(e)
                continue

            poster_url = None
            for image in movie_info["images"]:
                if "coverType" in image and image["coverType"] == "poster" and "remoteUrl" in image:
                    poster_url = image["remoteUrl"]

            url_json = {
                "title": movie_info["title"],
                f"{'qualityProfileId' if self.version == 'v3' else 'profileId'}": self.quality_profile_id,
                "year": int(movie_info["year"]),
                "tmdbid": int(tmdb_id),
                "titleslug": movie_info["titleSlug"],
                "monitored": True,
                "rootFolderPath": self.root_folder_path if folder is None else folder,
                "images": [{"covertype": "poster", "url": poster_url}],
                "addOptions": {"searchForMovie": self.search}
            }
            if tag_nums:
                url_json["tags"] = tag_nums
            response = self.send_post("movie", url_json)
            if response.status_code < 400:
                logger.info(f"Added to Radarr | {tmdb_id:<6} | {movie_info['title']}")
                add_count += 1
            else:
                try:
                    logger.error(f"Radarr Error: ({tmdb_id}) {movie_info['title']}: ({response.status_code}) {response.json()[0]['errorMessage']}")
                except KeyError:
                    logger.debug(url_json)
                    logger.error(f"Radarr Error: {response.json()}")
        logger.info(f"{add_count} Movie{'s' if add_count > 1 else ''} added to Radarr")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_get(self, url, params=None):
        url_params = {"apikey": f"{self.token}"}
        if params:
            for param in params:
                url_params[param] = params[param]
        return requests.get(f"{self.base_url}{url}", params=url_params).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_post(self, url, url_json):
        return requests.post(f"{self.base_url}{url}", json=url_json, params={"apikey": f"{self.token}"})
