import logging, requests
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

availability_translation = {
    "announced": "announced",
    "cinemas": "inCinemas",
    "released": "released",
    "db": "preDB"
}

class RadarrAPI:
    def __init__(self, params):
        self.url = params["url"]
        self.token = params["token"]
        self.version = params["version"]
        self.base_url = f"{self.url}/api{'/v3' if self.version == 'v3' else ''}/"
        try:
            result = requests.get(f"{self.base_url}system/status", params={"apikey": f"{self.token}"}).json()
        except Exception:
            util.print_stacktrace()
            raise Failed(f"Radarr Error: Could not connect to Radarr at {self.url}")
        if "error" in result and result["error"] == "Unauthorized":
            raise Failed("Radarr Error: Invalid API Key")
        if "version" not in result:
            raise Failed("Radarr Error: Unexpected Response Check URL")
        self.add = params["add"]
        self.root_folder_path = params["root_folder_path"]
        self.monitor = params["monitor"]
        self.availability = params["availability"]
        self.quality_profile_id = self.get_profile_id(params["quality_profile"])
        self.tag = params["tag"]
        self.tags = self.get_tags()
        self.search = params["search"]

    def get_profile_id(self, profile_name):
        profiles = ""
        for profile in self._get("qualityProfile" if self.version == "v3" else "profile"):
            if len(profiles) > 0:
                profiles += ", "
            profiles += profile["name"]
            if profile["name"] == profile_name:
                return profile["id"]
        raise Failed(f"Radarr Error: quality_profile: {profile_name} does not exist in radarr. Profiles available: {profiles}")

    def get_tags(self):
        return {tag["label"]: tag["id"] for tag in self._get("tag")}

    def add_tags(self, tags):
        added = False
        for label in tags:
            if str(label).lower() not in self.tags:
                added = True
                self._post("tag", {"label": str(label).lower()})
        if added:
            self.tags = self.get_tags()

    def lookup(self, tmdb_id):
        results = self._get("movie/lookup", params={"term": f"tmdb:{tmdb_id}"})
        if results:
            return results[0]
        else:
            raise Failed(f"Sonarr Error: TMDb ID: {tmdb_id} not found")

    def add_tmdb(self, tmdb_ids, **options):
        logger.info("")
        util.separator(f"Adding to Radarr", space=False, border=False)
        logger.info("")
        logger.debug(f"TMDb IDs: {tmdb_ids}")
        tag_nums = []
        add_count = 0
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = options["monitor"] if "monitor" in options else self.monitor
        availability = options["availability"] if "availability" in options else self.availability
        quality_profile_id = self.get_profile_id(options["quality"]) if "quality" in options else self.quality_profile_id
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search
        if tags:
            self.add_tags(tags)
            tag_nums = [self.tags[label.lower()] for label in tags if label.lower() in self.tags]
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
                f"{'qualityProfileId' if self.version == 'v3' else 'profileId'}": quality_profile_id,
                "year": int(movie_info["year"]),
                "tmdbid": int(tmdb_id),
                "titleslug": movie_info["titleSlug"],
                "minimumAvailability": availability_translation[availability],
                "monitored": monitor,
                "rootFolderPath": folder,
                "images": [{"covertype": "poster", "url": poster_url}],
                "addOptions": {"searchForMovie": search}
            }
            if tag_nums:
                url_json["tags"] = tag_nums
            response = self._post("movie", url_json)
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
    def _get(self, url, params=None):
        url_params = {"apikey": f"{self.token}"}
        if params:
            for param in params:
                url_params[param] = params[param]
        return requests.get(f"{self.base_url}{url}", params=url_params).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _post(self, url, url_json):
        return requests.post(f"{self.base_url}{url}", json=url_json, params={"apikey": f"{self.token}"})
