import json, logging, re, requests, secrets, webbrowser
from modules import util
from modules.util import Failed, TimeoutExpired
from retrying import retry
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

class MyAnimeListIDList:
    def __init__(self):
        self.ids = json.loads(requests.get("https://raw.githubusercontent.com/Fribb/anime-lists/master/animeMapping_full.json").content)

    def convert_mal_to_tvdb(self, mal_id):              return self.convert_mal(mal_id, "mal_id", "thetvdb_id")
    def convert_mal_to_tmdb(self, mal_id):              return self.convert_mal(mal_id, "mal_id", "themoviedb_id")
    def convert_tvdb_to_mal(self, tvdb_id):             return self.convert_mal(tvdb_id, "thetvdb_id", "mal_id")
    def convert_tmdb_to_mal(self, tmdb_id):             return self.convert_mal(tmdb_id, "themoviedb_id", "mal_id")
    def convert_mal(self, input_id, from_id, to_id):
        for attrs in self.ids:
            if from_id in attrs and int(attrs[from_id]) == int(input_id) and to_id in attrs and int(attrs[to_id]) > 0:
                return attrs[to_id]
        raise Failed("MyAnimeList Error: {} ID not found for {}: {}".format(util.pretty_ids[to_id], util.pretty_ids[from_id], input_id))

    def find_mal_ids(self, mal_id):
        for mal in self.ids:
            if "mal_id" in mal and int(mal["mal_id"]) == int(mal_id):
                return mal
        raise Failed("MyAnimeList Error: MyAnimeList ID: {} not found".format(mal_id))

class MyAnimeListAPI:
    def __init__(self, params, MyAnimeListIDList, authorization=None):
        self.urls = {
            "oauth_token": "https://myanimelist.net/v1/oauth2/token",
            "oauth_authorize": "https://myanimelist.net/v1/oauth2/authorize",
            "ranking": "https://api.myanimelist.net/v2/anime/ranking",
            "season": "https://api.myanimelist.net/v2/anime/season",
            "suggestions": "https://api.myanimelist.net/v2/anime/suggestions",
            "user": "https://api.myanimelist.net/v2/users"
        }
        self.client_id = params["client_id"]
        self.client_secret = params["client_secret"]
        self.config_path = params["config_path"]
        self.authorization = authorization
        self.MyAnimeListIDList = MyAnimeListIDList
        if not self.save_authorization(self.authorization):
            if not self.refresh_authorization():
                self.get_authorization()

    def get_authorization(self):
        code_verifier = secrets.token_urlsafe(100)[:128]
        url = "{}?response_type=code&client_id={}&code_challenge={}".format(self.urls["oauth_authorize"], self.client_id, code_verifier)
        logger.info("")
        logger.info("Navigate to: {}".format(url))
        logger.info("")
        logger.info("Login and click the Allow option. You will then be redirected to a localhost")
        logger.info("url that most likely won't load, which is fine. Copy the URL and paste it below")
        webbrowser.open(url, new=2)
        try:                                url = util.logger_input("URL").strip()
        except TimeoutExpired:              raise Failed("Input Timeout: URL required.")
        if not url:                         raise Failed("MyAnimeList Error: No input MyAnimeList code required.")
        match = re.search("code=([^&]+)", str(url))
        if not match:
            raise Failed("MyAnimeList Error: Invalid URL")
        code = match.group(1)
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code"
        }
        new_authorization = self.oauth_request(data)
        if "error" in new_authorization:
            raise Failed("MyAnimeList Error: Invalid code")
        if not self.save_authorization(new_authorization):
            raise Failed("MyAnimeList Error: New Authorization Failed")

    def check_authorization(self, authorization):
        try:
            self.send_request(self.urls["suggestions"], authorization=authorization)
            return True
        except Failed as e:
            logger.debug(e)
            return False

    def refresh_authorization(self):
        if self.authorization and "refresh_token" in self.authorization and self.authorization["refresh_token"]:
            logger.info("Refreshing Access Token...")
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.authorization["refresh_token"],
                "grant_type": "refresh_token"
            }
            refreshed_authorization = self.oauth_request(data)
            return self.save_authorization(refreshed_authorization)
        return False

    def save_authorization(self, authorization):
        if authorization is not None and "access_token" in authorization and authorization["access_token"] and self.check_authorization(authorization):
            if self.authorization != authorization:
                yaml.YAML().allow_duplicate_keys = True
                config, ind, bsi = yaml.util.load_yaml_guess_indent(open(self.config_path))
                config["mal"]["authorization"] = {
                    "access_token": authorization["access_token"],
                    "token_type": authorization["token_type"],
                    "expires_in": authorization["expires_in"],
                    "refresh_token": authorization["refresh_token"]
                }
                logger.info("Saving authorization information to {}".format(self.config_path))
                yaml.round_trip_dump(config, open(self.config_path, "w"), indent=ind, block_seq_indent=bsi)
            self.authorization = authorization
            return True
        return False

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def oauth_request(self, data):
        return requests.post(self.urls["oauth_token"], data).json()

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def send_request(self, url, authorization=None):
        new_authorization = authorization if authorization else self.authorization
        response = requests.get(url, headers={"Authorization": "Bearer {}".format(new_authorization["access_token"])}).json()
        if "error" in response:         raise Failed("MyAnimeList Error: {}".format(response["error"]))
        else:                           return response

    def parse_mal_ids(self, data):
        mal_ids = []
        if "data" in data:
            for d in data["data"]:
                mal_ids.append(d["node"]["id"])
        return mal_ids

    def get_username(self):
        return self.send_request("{}/@me".format(self.urls["user"]))["name"]

    def get_ranked(self, ranking_type, limit):
        url = "{}?ranking_type={}&limit={}".format(self.urls["ranking"], ranking_type, limit)
        return self.parse_mal_ids(self.send_request(url))

    def get_season(self, season, year, sort_by, limit):
        url = "{}/{}/{}?sort={}&limit={}".format(self.urls["season"], year, season, sort_by, limit)
        return self.parse_mal_ids(self.send_request(url))

    def get_suggestions(self, limit):
        url = "{}?limit={}".format(self.urls["suggestions"], limit)
        return self.parse_mal_ids(self.send_request(url))

    def get_userlist(self, username, status, sort_by, limit):
        url = "{}/{}/animelist?{}sort={}&limit={}".format(self.urls["user"], username, "" if status == "all" else "status={}&".format(status), sort_by, limit)
        return self.parse_mal_ids(self.send_request(url))

    def get_items(self, method, data, status_message=True):
        if status_message:
            logger.debug("Data: {}".format(data))
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        if method == "mal_id":
            mal_ids = [data]
            if status_message:
                logger.info("Processing {}: {}".format(pretty, data))
        elif method in util.mal_ranked_name:
            mal_ids = self.get_ranked(util.mal_ranked_name[method], data)
            if status_message:
                logger.info("Processing {}: {} Anime".format(pretty, data))
        elif method == "mal_season":
            mal_ids = self.get_season(data["season"], data["year"], data["sort_by"], data["limit"])
            if status_message:
                logger.info("Processing {}: {} Anime from {} {} sorted by {}".format(pretty, data["limit"], util.pretty_seasons[data["season"]], data["year"], util.mal_pretty[data["sort_by"]]))
        elif method == "mal_suggested":
            mal_ids = self.get_suggestions(data)
            if status_message:
                logger.info("Processing {}: {} Anime".format(pretty, data))
        elif method == "mal_userlist":
            mal_ids = self.get_userlist(data["username"], data["status"], data["sort_by"], data["limit"])
            if status_message:
                logger.info("Processing {}: {} Anime from {}'s {} list sorted by {}".format(pretty, data["limit"], self.get_username() if data["username"] == "@me" else data["username"], util.mal_pretty[data["status"]], util.mal_pretty[data["sort_by"]]))
        else:
            raise Failed("MyAnimeList Error: Method {} not supported".format(method))
        show_ids = []
        movie_ids = []
        for mal_id in mal_ids:
            try:
                ids = self.MyAnimeListIDList.find_mal_ids(mal_id)
                if "thetvdb_id" in ids and int(ids["thetvdb_id"]) > 0:                  show_ids.append(int(ids["thetvdb_id"]))
                elif "themoviedb_id" in ids and int(ids["themoviedb_id"]) > 0:          movie_ids.append(int(ids["themoviedb_id"]))
                else:                                                                   raise Failed("MyAnimeList Error: MyAnimeList ID: {} has no other IDs associated with it".format(mal_id))
            except Failed as e:
                if status_message:
                    logger.error(e)
        if status_message:
            logger.debug("MyAnimeList IDs Found: {}".format(mal_ids))
            logger.debug("Shows Found: {}".format(show_ids))
            logger.debug("Movies Found: {}".format(movie_ids))
        return movie_ids, show_ids
