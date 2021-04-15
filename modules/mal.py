import json, logging, re, requests, secrets, webbrowser
from modules import util
from modules.util import Failed, TimeoutExpired
from retrying import retry
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

builders = [
    "mal_id",
    "mal_all",
    "mal_airing",
    "mal_upcoming",
    "mal_tv",
    "mal_ova",
    "mal_movie",
    "mal_special",
    "mal_popular",
    "mal_favorite",
    "mal_season",
    "mal_suggested",
    "mal_userlist"
]
mal_ranked_name = {
    "mal_all": "all",
    "mal_airing": "airing",
    "mal_upcoming": "upcoming",
    "mal_tv": "tv",
    "mal_ova": "ova",
    "mal_movie": "movie",
    "mal_special": "special",
    "mal_popular": "bypopularity",
    "mal_favorite": "favorite"
}
season_sort = {
    "anime_score": "anime_score",
    "anime_num_list_users": "anime_num_list_users",
    "score": "anime_score",
    "members": "anime_num_list_users"
}
pretty_names = {
    "anime_score": "Score",
    "anime_num_list_users": "Members",
    "list_score": "Score",
    "list_updated_at": "Last Updated",
    "anime_title": "Title",
    "anime_start_date": "Start Date",
    "all": "All Anime",
    "watching": "Currently Watching",
    "completed": "Completed",
    "on_hold": "On Hold",
    "dropped": "Dropped",
    "plan_to_watch": "Plan to Watch"
}
userlist_sort = {
    "score": "list_score",
    "list_score": "list_score",
    "last_updated": "list_updated_at",
    "list_updated": "list_updated_at",
    "list_updated_at": "list_updated_at",
    "title": "anime_title",
    "anime_title": "anime_title",
    "start_date": "anime_start_date",
    "anime_start_date": "anime_start_date"
}
userlist_status = [
    "all",
    "watching",
    "completed",
    "on_hold",
    "dropped",
    "plan_to_watch"
]

class MyAnimeListAPI:
    def __init__(self, params, config, authorization=None):
        self.config = config
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
        if not self.save_authorization(self.authorization):
            if not self.refresh_authorization():
                self.get_authorization()

    def get_authorization(self):
        code_verifier = secrets.token_urlsafe(100)[:128]
        url = f"{self.urls['oauth_authorize']}?response_type=code&client_id={self.client_id}&code_challenge={code_verifier}"
        logger.info("")
        logger.info(f"Navigate to: {url}")
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
                logger.info(f"Saving authorization information to {self.config_path}")
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
        response = requests.get(url, headers={"Authorization": f"Bearer {new_authorization['access_token']}"}).json()
        if "error" in response:         raise Failed(f"MyAnimeList Error: {response['error']}")
        else:                           return response

    def request_and_parse_mal_ids(self, url):
        data = self.send_request(url)
        return [d["node"]["id"] for d in data["data"]] if "data" in data else []

    def get_username(self):
        return self.send_request(f"{self.urls['user']}/@me")["name"]

    def get_ranked(self, ranking_type, limit):
        url = f"{self.urls['ranking']}?ranking_type={ranking_type}&limit={limit}"
        return self.request_and_parse_mal_ids(url)

    def get_season(self, season, year, sort_by, limit):
        url = f"{self.urls['season']}/{year}/{season}?sort={sort_by}&limit={limit}"
        return self.request_and_parse_mal_ids(url)

    def get_suggestions(self, limit):
        url = f"{self.urls['suggestions']}?limit={limit}"
        return self.request_and_parse_mal_ids(url)

    def get_userlist(self, username, status, sort_by, limit):
        final_status = "" if status == "all" else f"status={status}&"
        url = f"{self.urls['user']}/{username}/animelist?{final_status}sort={sort_by}&limit={limit}"
        return self.request_and_parse_mal_ids(url)

    def get_items(self, method, data, language, status_message=True):
        if status_message:
            logger.debug(f"Data: {data}")
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        if method == "mal_id":
            mal_ids = [data]
            if status_message:
                logger.info(f"Processing {pretty}: {data}")
        elif method in mal_ranked_name:
            mal_ids = self.get_ranked(mal_ranked_name[method], data)
            if status_message:
                logger.info(f"Processing {pretty}: {data} Anime")
        elif method == "mal_season":
            mal_ids = self.get_season(data["season"], data["year"], data["sort_by"], data["limit"])
            if status_message:
                logger.info(f"Processing {pretty}: {data['limit']} Anime from {util.pretty_seasons[data['season']]} {data['year']} sorted by {pretty_names[data['sort_by']]}")
        elif method == "mal_suggested":
            mal_ids = self.get_suggestions(data)
            if status_message:
                logger.info(f"Processing {pretty}: {data} Anime")
        elif method == "mal_userlist":
            mal_ids = self.get_userlist(data["username"], data["status"], data["sort_by"], data["limit"])
            if status_message:
                logger.info(f"Processing {pretty}: {data['limit']} Anime from {self.get_username() if data['username'] == '@me' else data['username']}'s {pretty_names[data['status']]} list sorted by {pretty_names[data['sort_by']]}")
        else:
            raise Failed(f"MyAnimeList Error: Method {method} not supported")
        show_ids = []
        movie_ids = []
        for mal_id in mal_ids:
            tmdb_id, tvdb_id = self.config.covert_mal_to_id(mal_id, language)
            if tmdb_id:
                movie_ids.append(tmdb_id)
            if tvdb_id:
                show_ids.append(tvdb_id)
        if status_message:
            logger.debug(f"MyAnimeList IDs Found: {mal_ids}")
            logger.debug(f"Shows Found: {show_ids}")
            logger.debug(f"Movies Found: {movie_ids}")
        return movie_ids, show_ids
