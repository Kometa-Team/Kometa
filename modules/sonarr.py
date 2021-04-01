import logging, re, requests
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class SonarrAPI:
    def __init__(self, tvdb, params, language):
        self.url_params = {"apikey": f"{params['token']}"}
        self.base_url = f"{params['url']}/api{'/v3/' if params['version'] == 'v3' else '/'}"
        try:
            result = requests.get(f"{self.base_url}system/status", params=self.url_params).json()
        except Exception:
            util.print_stacktrace()
            raise Failed(f"Sonarr Error: Could not connect to Sonarr at {params['url']}")
        if "error" in result and result["error"] == "Unauthorized":
            raise Failed("Sonarr Error: Invalid API Key")
        if "version" not in result:
            raise Failed("Sonarr Error: Unexpected Response Check URL")
        self.quality_profile_id = None
        profiles = ""
        for profile in self.send_get(f"{self.base_url}{'qualityProfile' if params['version'] == 'v3' else 'profile'}"):
            if len(profiles) > 0:
                profiles += ", "
            profiles += profile["name"]
            if profile["name"] == params["quality_profile"]:
                self.quality_profile_id = profile["id"]
        if not self.quality_profile_id:
            raise Failed(f"Sonarr Error: quality_profile: {params['quality_profile']} does not exist in sonarr. Profiles available: {profiles}")
        self.tvdb = tvdb
        self.language = language
        self.url = params["url"]
        self.version = params["version"]
        self.token = params["token"]
        self.root_folder_path = params["root_folder_path"]
        self.add = params["add"]
        self.search = params["search"]
        self.season_folder = params["season_folder"]
        self.tag = params["tag"]

    def add_tvdb(self, tvdb_ids, tag=None, folder=None):
        logger.info("")
        logger.debug(f"TVDb IDs: {tvdb_ids}")
        tag_nums = []
        add_count = 0
        if tag is None:
            tag = self.tag
        if tag:
            tag_cache = {}
            for label in tag:
                self.send_post(f"{self.base_url}tag", {"label": str(label)})
            for t in self.send_get(f"{self.base_url}tag"):
                tag_cache[t["label"]] = t["id"]
            for label in tag:
                if label in tag_cache:
                    tag_nums.append(tag_cache[label])
        for tvdb_id in tvdb_ids:
            try:
                show = self.tvdb.get_series(self.language, tvdb_id)
            except Failed as e:
                logger.error(e)
                continue

            titleslug = re.sub(r"([^\s\w]|_)+", "", show.title).replace(" ", "-").lower()

            url_json = {
                "title": show.title,
                f"{'qualityProfileId' if self.version == 'v3' else 'profileId'}": self.quality_profile_id,
                "languageProfileId": 1,
                "tvdbId": int(tvdb_id),
                "titleslug": titleslug,
                "language": self.language,
                "monitored": True,
                "seasonFolder": self.season_folder,
                "rootFolderPath": self.root_folder_path if folder is None else folder,
                "seasons": [],
                "images": [{"covertype": "poster", "url": show.poster_path}],
                "addOptions": {"searchForMissingEpisodes": self.search}
            }
            if tag_nums:
                url_json["tags"] = tag_nums
            response = self.send_post(f"{self.base_url}series", url_json)
            if response.status_code < 400:
                logger.info(f"Added to Sonarr | {tvdb_id:<6} | {show.title}")
                add_count += 1
            else:
                try:
                    logger.error(f"Sonarr Error: ({tvdb_id}) {show.title}: ({response.status_code}) {response.json()[0]['errorMessage']}")
                except KeyError:
                    logger.debug(url_json)
                    logger.error(f"Sonarr Error: {response.json()}")
        logger.info(f"{add_count} Show{'s' if add_count > 1 else ''} added to Sonarr")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_get(self, url):
        return requests.get(url, params=self.url_params).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_post(self, url, url_json):
        return requests.post(url, json=url_json, params=self.url_params)
