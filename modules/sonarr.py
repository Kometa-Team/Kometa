import logging, requests
from json.decoder import JSONDecodeError
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

series_type = ["standard", "daily", "anime"]
monitor_translation = {
    "all": "all",
    "future": "future",
    "missing": "missing",
    "existing": "existing",
    "pilot": "pilot",
    "first": "firstSeason",
    "latest": "latestSeason",
    "none": "none"
}

class SonarrAPI:
    def __init__(self, params, language):
        self.url = params["url"]
        self.token = params["token"]
        self.version = params["version"]
        self.base_url = f"{self.url}/api{'/v3/' if self.version == 'v3' else '/'}"
        try:
            result = requests.get(f"{self.base_url}system/status", params={"apikey": f"{self.token}"}).json()
        except Exception:
            util.print_stacktrace()
            raise Failed(f"Sonarr Error: Could not connect to Sonarr at {self.url}")
        if "error" in result and result["error"] == "Unauthorized":
            raise Failed("Sonarr Error: Invalid API Key")
        if "version" not in result:
            raise Failed("Sonarr Error: Unexpected Response Check URL")
        self.add = params["add"]
        self.root_folder_path = params["root_folder_path"]
        self.monitor = params["monitor"]
        self.quality_profile_id = self.get_profile_id(params["quality_profile"], "quality_profile")
        self.language_profile_id = None
        if self.version == "v3" and params["language_profile"] is not None:
            self.language_profile_id = self.get_profile_id(params["language_profile"], "language_profile")
        if self.language_profile_id is None:
            self.language_profile_id = 1
        self.series_type = params["series_type"]
        self.season_folder = params["season_folder"]
        self.tag = params["tag"]
        self.tags = self.get_tags()
        self.search = params["search"]
        self.cutoff_search = params["cutoff_search"]
        self.language = language

    def get_profile_id(self, profile_name, profile_type):
        profiles = ""
        if profile_type == "quality_profile" and self.version == "v3":
            endpoint = "qualityProfile"
        elif profile_type == "language_profile":
            endpoint = "languageProfile"
        else:
            endpoint = "profile"
        for profile in self._get(endpoint):
            if len(profiles) > 0:
                profiles += ", "
            profiles += profile["name"]
            if profile["name"] == profile_name:
                return profile["id"]
        raise Failed(f"Sonarr Error: {profile_type}: {profile_name} does not exist in sonarr. Profiles available: {profiles}")

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

    def lookup(self, tvdb_id):
        results = self._get("series/lookup", params={"term": f"tvdb:{tvdb_id}"})
        if results:
            return results[0]
        else:
            raise Failed(f"Sonarr Error: TVDb ID: {tvdb_id} not found")

    def add_tvdb(self, tvdb_ids, **options):
        logger.info("")
        util.separator(f"Adding to Sonarr", space=False, border=False)
        logger.info("")
        logger.debug(f"TVDb IDs: {tvdb_ids}")
        tag_nums = []
        add_count = 0
        folder = options["folder"] if "folder" in options else self.root_folder_path
        monitor = options["monitor"] if "monitor" in options else self.monitor
        quality_profile_id = self.get_profile_id(options["quality"], "quality_profile") if "quality" in options else self.quality_profile_id
        language_profile_id = self.get_profile_id(options["language"], "language_profile") if "quality" in options else self.language_profile_id
        series = options["series"] if "series" in options else self.series_type
        season = options["season"] if "season" in options else self.season_folder
        tags = options["tag"] if "tag" in options else self.tag
        search = options["search"] if "search" in options else self.search
        cutoff_search = options["cutoff_search"] if "cutoff_search" in options else self.cutoff_search
        if tags:
            self.add_tags(tags)
            tag_nums = [self.tags[label.lower()] for label in tags if label.lower() in self.tags]
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
                f"{'qualityProfileId' if self.version == 'v3' else 'profileId'}": quality_profile_id,
                "languageProfileId": language_profile_id,
                "tvdbId": int(tvdb_id),
                "titleslug": show_info["titleSlug"],
                "language": self.language,
                "monitored": monitor != "none",
                "seasonFolder": season,
                "seriesType": series,
                "rootFolderPath": folder,
                "seasons": [],
                "images": [{"covertype": "poster", "url": poster_url}],
                "addOptions": {
                    "searchForMissingEpisodes": search,
                    "searchForCutoffUnmetEpisodes": cutoff_search,
                    "monitor": monitor_translation[monitor]
                }
            }
            if tag_nums:
                url_json["tags"] = tag_nums
            response = self._post("series", url_json)
            if response.status_code < 400:
                logger.info(f"Added to Sonarr | {tvdb_id:<6} | {show_info['title']}")
                add_count += 1
            else:
                try:
                    logger.error(f"Sonarr Error: ({tvdb_id}) {show_info['title']}: ({response.status_code}) {response.json()[0]['errorMessage']}")
                except KeyError:
                    logger.debug(url_json)
                    logger.error(f"Sonarr Error: {response.json()}")
                except JSONDecodeError:
                    logger.debug(url_json)
                    logger.error(f"Sonarr Error: {response}")

        logger.info(f"{add_count} Show{'s' if add_count > 1 else ''} added to Sonarr")

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
