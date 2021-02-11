import logging, re, requests
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class RadarrAPI:
    def __init__(self, tmdb, params):
        self.url_params = {"apikey": "{}".format(params["token"])}
        self.base_url = "{}/api{}".format(params["url"], "/v3/" if params["version"] == "v3" else "/")
        try:
            response = requests.get("{}system/status".format(self.base_url), params=self.url_params)
            result = response.json()
        except Exception as e:
            util.print_stacktrace()
            raise Failed("Radarr Error: Could not connect to Radarr at {}".format(params["url"]))
        if "error" in result and result["error"] == "Unauthorized":
            raise Failed("Radarr Error: Invalid API Key")
        if "version" not in result:
            raise Failed("Radarr Error: Unexpected Response Check URL")
        response = requests.get("{}{}".format(self.base_url, "qualityProfile" if params["version"] == "v3" else "profile"), params=self.url_params)
        self.quality_profile_id = None
        profiles = ""
        for profile in response.json():
            if len(profiles) > 0:
                profiles += ", "
            profiles += profile["name"]
            if profile["name"] == params["quality_profile"]:
                self.quality_profile_id = profile["id"]
        if not self.quality_profile_id:
            raise Failed("Radarr Error: quality_profile: {} does not exist in radarr. Profiles available: {}".format(params["quality_profile"], profiles))
        self.tmdb = tmdb
        self.url = params["url"]
        self.version = params["version"]
        self.token = params["token"]
        self.root_folder_path = params["root_folder_path"]
        self.add = params["add"]
        self.search = params["search"]

    def add_tmdb(self, tmdb_ids):
        logger.info("")
        logger.debug("TMDb IDs: {}".format(tmdb_ids))
        add_count = 0
        for tmdb_id in tmdb_ids:
            try:
                movie = self.tmdb.get_movie(tmdb_id)
            except Failed as e:
                logger.error(e)
                continue

            try:
                year = movie.release_date.split("-")[0]
            except AttributeError:
                logger.error("TMDb Error: No year for ({}) {}".format(tmdb_id, movie.title))
                continue

            if year.isdigit() is False:
                logger.error("TMDb Error: No release date yet for ({}) {}".format(tmdb_id, movie.title))
                continue

            poster = "https://image.tmdb.org/t/p/original{}".format(movie.poster_path)

            titleslug = re.sub(r"([^\s\w]|_)+", "", "{} {}".format(movie.title, year)).replace(" ", "-").lower()

            url_json = {
                "title": movie.title,
                "{}".format("qualityProfileId" if self.version == "v3" else "profileId"): self.quality_profile_id,
                "year": int(year),
                "tmdbid": int(tmdb_id),
                "titleslug": titleslug,
                "monitored": True,
                "rootFolderPath": self.root_folder_path,
                "images": [{"covertype": "poster", "url": poster}],
                "addOptions": {"searchForMovie": self.search}
            }
            response = self.send_post("{}movie".format(self.base_url), url_json)
            if response.status_code < 400:
                logger.info("Added to Radarr | {:<6} | {}".format(tmdb_id, movie.title))
                add_count += 1
            else:
                try:
                    logger.error("Radarr Error: ({}) {}: ({}) {}".format(tmdb_id, movie.title, response.status_code, response.json()[0]["errorMessage"]))
                except KeyError as e:
                    logger.debug(url_json)
                    logger.debug(response)
                    logger.debug(response.status_code)
                    logger.debug(response.json())
        logger.info("{} Movie{} added to Radarr".format(add_count, "s" if add_count > 1 else ""))

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_post(self, url, url_json):
        return requests.post(url, json=url_json, params=self.url_params)
