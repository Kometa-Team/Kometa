import logging, re, requests
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class SonarrAPI:
    def __init__(self, params, language):
        self.base_url = f"{params['url']}/api{'/v3/' if params['version'] == 'v3' else '/'}"
        self.token = params["token"]
        try:
            result = requests.get(f"{self.base_url}system/status", params={"apikey": f"{self.token}"}).json()
        except Exception:
            util.print_stacktrace()
            raise Failed(f"Sonarr Error: Could not connect to Sonarr at {params['url']}")
        if "error" in result and result["error"] == "Unauthorized":
            raise Failed("Sonarr Error: Invalid API Key")
        if "version" not in result:
            raise Failed("Sonarr Error: Unexpected Response Check URL")
        self.quality_profile_id = None
        profiles = ""
        for profile in self.send_get("qualityProfile" if params["version"] == "v3" else "profile"):
            if len(profiles) > 0:
                profiles += ", "
            profiles += profile["name"]
            if profile["name"] == params["quality_profile"]:
                self.quality_profile_id = profile["id"]
        if not self.quality_profile_id:
            raise Failed(f"Sonarr Error: quality_profile: {params['quality_profile']} does not exist in sonarr. Profiles available: {profiles}")

        self.language_profile_id = None
        if params["version"] == "v3" and params["language_profile"] is not None:
            profiles = ""
            for profile in self.send_get("languageProfile"):
                if len(profiles) > 0:
                    profiles += ", "
                profiles += profile["name"]
                if profile["name"] == params["language_profile"]:
                    self.language_profile_id = profile["id"]
            if not self.quality_profile_id:
                raise Failed(f"Sonarr Error: language_profile: {params['language_profile']} does not exist in sonarr. Profiles available: {profiles}")

        if self.language_profile_id is None:
            self.language_profile_id = 1

        self.tags = self.get_tags()
        self.language = language
        self.version = params["version"]
        self.root_folder_path = params["root_folder_path"]
        self.add = params["add"]
        self.search = params["search"]
        self.season_folder = params["season_folder"]
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

    def lookup(self, tvdb_id):
        results = self.send_get("series/lookup", params={"term": f"tvdb:{tvdb_id}"})
        if results:
            return results[0]
        else:
            raise Failed(f"Sonarr Error: TVDb ID: {tvdb_id} not found")

    def add_tvdb(self, tvdb_ids, tags=None, folder=None):
        logger.info("")
        logger.debug(f"TVDb IDs: {tvdb_ids}")
        tag_nums = []
        add_count = 0
        if tags is None:
            tags = self.tag
        if tags:
            self.add_tags(tags)
            tag_nums = [self.tags[label] for label in tags if label in self.tags]
        for tvdb_id in tvdb_ids:
            try:
                show_info = self.lookup(tvdb_id)
            except Failed as e:
                logger.error(e)
                continue

            poster_url = None
            for image in show_info["images"]:
                if "coverType" in image and image["coverType"] == "poster" and "remoteUrl" in image:
                    poster_url = image["remoteUrl"]

            url_json = {
                "title": show_info["title"],
                f"{'qualityProfileId' if self.version == 'v3' else 'profileId'}": self.quality_profile_id,
                "languageProfileId": self.language_profile_id,
                "tvdbId": int(tvdb_id),
                "titleslug": show_info["titleSlug"],
                "language": self.language,
                "monitored": True,
                "seasonFolder": self.season_folder,
                "rootFolderPath": self.root_folder_path if folder is None else folder,
                "seasons": [],
                "images": [{"covertype": "poster", "url": poster_url}],
                "addOptions": {"searchForMissingEpisodes": self.search}
            }
            if tag_nums:
                url_json["tags"] = tag_nums
            response = self.send_post("series", url_json)
            if response.status_code < 400:
                logger.info(f"Added to Sonarr | {tvdb_id:<6} | {show_info['title']}")
                add_count += 1
            else:
                try:
                    logger.error(f"Sonarr Error: ({tvdb_id}) {show_info['title']}: ({response.status_code}) {response.json()[0]['errorMessage']}")
                except KeyError:
                    logger.debug(url_json)
                    logger.error(f"Sonarr Error: {response.json()}")
        logger.info(f"{add_count} Show{'s' if add_count > 1 else ''} added to Sonarr")

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
