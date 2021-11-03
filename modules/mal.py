import logging, math, re, secrets, time, webbrowser
from modules import util
from modules.util import Failed, TimeoutExpired
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

builders = [
    "mal_id", "mal_all", "mal_airing", "mal_upcoming", "mal_tv", "mal_ova", "mal_movie", "mal_special",
    "mal_popular", "mal_favorite", "mal_season", "mal_suggested", "mal_userlist", "mal_genre", "mal_studio"
]
mal_ranked_name = {
    "mal_all": "all", "mal_airing": "airing", "mal_upcoming": "upcoming", "mal_tv": "tv", "mal_ova": "ova",
    "mal_movie": "movie", "mal_special": "special", "mal_popular": "bypopularity", "mal_favorite": "favorite"
}
mal_ranked_pretty = {
    "mal_all": "MyAnimeList All", "mal_airing": "MyAnimeList Airing",
    "mal_upcoming": "MyAnimeList Upcoming", "mal_tv": "MyAnimeList TV", "mal_ova": "MyAnimeList OVA",
    "mal_movie": "MyAnimeList Movie", "mal_special": "MyAnimeList Special", "mal_popular": "MyAnimeList Popular",
    "mal_favorite": "MyAnimeList Favorite", "mal_genre": "MyAnimeList Genre", "mal_studio": "MyAnimeList Studio"
}
season_sort_translation = {"score": "anime_score", "anime_score": "anime_score", "members": "anime_num_list_users", "anime_num_list_users": "anime_num_list_users"}
season_sort_options = ["score", "members"]
pretty_names = {
    "anime_score": "Score", "list_score": "Score", "anime_num_list_users": "Members", "list_updated_at": "Last Updated",
    "anime_title": "Title", "anime_start_date": "Start Date", "all": "All Anime", "watching": "Currently Watching",
    "completed": "Completed", "on_hold": "On Hold", "dropped": "Dropped", "plan_to_watch": "Plan to Watch"
}
userlist_sort_translation = {
    "score": "list_score", "list_score": "list_score",
    "last_updated": "list_updated_at", "list_updated": "list_updated_at", "list_updated_at": "list_updated_at",
    "title": "anime_title", "anime_title": "anime_title",
    "start_date": "anime_start_date", "anime_start_date": "anime_start_date"
}
userlist_sort_options = ["score", "last_updated", "title", "start_date"]
userlist_status = ["all", "watching", "completed", "on_hold", "dropped", "plan_to_watch"]
base_url = "https://api.myanimelist.net"
jiken_base_url = "https://api.jikan.moe/v3"
urls = {
    "oauth_token": f"https://myanimelist.net/v1/oauth2/token",
    "oauth_authorize": f"https://myanimelist.net/v1/oauth2/authorize",
    "ranking": f"{base_url}/v2/anime/ranking",
    "season": f"{base_url}/v2/anime/season",
    "suggestions": f"{base_url}/v2/anime/suggestions",
    "user": f"{base_url}/v2/users"
}

class MyAnimeList:
    def __init__(self, config, params):
        self.config = config
        self.client_id = params["client_id"]
        self.client_secret = params["client_secret"]
        self.config_path = params["config_path"]
        self.authorization = params["authorization"]
        if not self._save(self.authorization):
            if not self._refresh():
                self._authorization()

    def _authorization(self):
        code_verifier = secrets.token_urlsafe(100)[:128]
        url = f"{urls['oauth_authorize']}?response_type=code&client_id={self.client_id}&code_challenge={code_verifier}"
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
        new_authorization = self._oauth(data)
        if "error" in new_authorization:
            raise Failed("MyAnimeList Error: Invalid code")
        if not self._save(new_authorization):
            raise Failed("MyAnimeList Error: New Authorization Failed")

    def _check(self, authorization):
        try:
            self._request(urls["suggestions"], authorization=authorization)
            return True
        except Failed as e:
            logger.debug(e)
            return False

    def _refresh(self):
        if self.authorization and "refresh_token" in self.authorization and self.authorization["refresh_token"]:
            logger.info("Refreshing Access Token...")
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.authorization["refresh_token"],
                "grant_type": "refresh_token"
            }
            refreshed_authorization = self._oauth(data)
            return self._save(refreshed_authorization)
        return False

    def _save(self, authorization):
        if authorization is not None and "access_token" in authorization and authorization["access_token"] and self._check(authorization):
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

    def _oauth(self, data):
        return self.config.post_json(urls["oauth_token"], data=data)

    def _request(self, url, authorization=None):
        new_authorization = authorization if authorization else self.authorization
        if self.config.trace_mode:
            logger.debug(f"URL: {url}")
        response = self.config.get_json(url, headers={"Authorization": f"Bearer {new_authorization['access_token']}"})
        if self.config.trace_mode:
            logger.debug(f"Response: {response}")
        if "error" in response:         raise Failed(f"MyAnimeList Error: {response['error']}")
        else:                           return response

    def _jiken_request(self, url):
        data = self.config.get_json(f"{jiken_base_url}{url}")
        time.sleep(2)
        return data

    def _parse_request(self, url):
        data = self._request(url)
        return [d["node"]["id"] for d in data["data"]] if "data" in data else []

    def _username(self):
        return self._request(f"{urls['user']}/@me")["name"]

    def _ranked(self, ranking_type, limit):
        url = f"{urls['ranking']}?ranking_type={ranking_type}&limit={limit}"
        return self._parse_request(url)

    def _season(self, season, year, sort_by, limit):
        url = f"{urls['season']}/{year}/{season}?sort={sort_by}&limit={limit}"
        return self._parse_request(url)

    def _suggestions(self, limit):
        url = f"{urls['suggestions']}?limit={limit}"
        return self._parse_request(url)

    def _userlist(self, username, status, sort_by, limit):
        final_status = "" if status == "all" else f"status={status}&"
        url = f"{urls['user']}/{username}/animelist?{final_status}sort={sort_by}&limit={limit}"
        return self._parse_request(url)

    def _genre(self, genre_id, limit):
        data = self._jiken_request(f"/genre/anime/{genre_id}")
        if "item_count" not in data:
            raise Failed(f"MyAnimeList Error: No MyAnimeList IDs for Genre ID: {genre_id}")
        total_items = data["item_count"]
        if total_items < limit or limit <= 0:
            limit = total_items
        mal_ids = []
        num_of_pages = math.ceil(int(limit) / 100)
        current_page = 1
        chances = 0
        while current_page <= num_of_pages:
            if chances > 6:
                logger.debug(data)
                raise Failed("AniList Error: Connection Failed")
            start_num = (current_page - 1) * 100 + 1
            util.print_return(f"Parsing Page {current_page}/{num_of_pages} {start_num}-{limit if current_page == num_of_pages else current_page * 100}")
            if current_page > 1:
                data = self._jiken_request(f"/genre/anime/{genre_id}/{current_page}")
            if "anime" in data:
                chances = 0
                mal_ids.extend([anime["mal_id"] for anime in data["anime"]])
                if len(mal_ids) > limit:
                    return mal_ids[:limit]
                current_page += 1
            else:
                chances += 1
        util.print_end()
        return mal_ids

    def _studio(self, studio_id, limit):
        data = self._jiken_request(f"/producer/{studio_id}")
        if "anime" not in data:
            raise Failed(f"MyAnimeList Error: No MyAnimeList IDs for Studio ID: {studio_id}")
        mal_ids = []
        count = 1
        while True:
            if count > 1:
                data = self._jiken_request(f"/producer/{studio_id}/{count}")
            if "anime" not in data:
                break
            mal_ids.extend([anime["mal_id"] for anime in data["anime"]])
            if len(mal_ids) > limit > 0:
                return mal_ids[:limit]
            count += 1
        return mal_ids

    def get_mal_ids(self, method, data):
        if method == "mal_id":
            logger.info(f"Processing MyAnimeList ID: {data}")
            mal_ids = [data]
        elif method in mal_ranked_name:
            logger.info(f"Processing {mal_ranked_pretty[method]}: {data} Anime")
            mal_ids = self._ranked(mal_ranked_name[method], data)
        elif method == "mal_genre":
            logger.info(f"Processing {mal_ranked_pretty[method]} ID: {data['genre_id']}")
            mal_ids = self._genre(data["genre_id"], data["limit"])
        elif method == "mal_studio":
            logger.info(f"Processing {mal_ranked_pretty[method]} ID: {data['studio_id']}")
            mal_ids = self._studio(data["studio_id"], data["limit"])
        elif method == "mal_season":
            logger.info(f"Processing MyAnimeList Season: {data['limit']} Anime from {data['season'].title()} {data['year']} sorted by {pretty_names[data['sort_by']]}")
            mal_ids = self._season(data["season"], data["year"], data["sort_by"], data["limit"])
        elif method == "mal_suggested":
            logger.info(f"Processing MyAnimeList Suggested: {data} Anime")
            mal_ids = self._suggestions(data)
        elif method == "mal_userlist":
            logger.info(f"Processing MyAnimeList Userlist: {data['limit']} Anime from {self._username() if data['username'] == '@me' else data['username']}'s {pretty_names[data['status']]} list sorted by {pretty_names[data['sort_by']]}")
            mal_ids = self._userlist(data["username"], data["status"], data["sort_by"], data["limit"])
        else:
            raise Failed(f"MyAnimeList Error: Method {method} not supported")
        logger.debug("")
        logger.debug(f"{len(mal_ids)} MyAnimeList IDs Found: {mal_ids}")
        return mal_ids
