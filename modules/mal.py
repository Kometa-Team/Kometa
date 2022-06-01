import re, secrets, time, webbrowser
from json import JSONDecodeError
from modules import util
from modules.util import Failed, TimeoutExpired, YAML

logger = util.logger

builders = [
    "mal_id", "mal_all", "mal_airing", "mal_upcoming", "mal_tv", "mal_ova", "mal_movie", "mal_special",
    "mal_popular", "mal_favorite", "mal_season", "mal_suggested", "mal_userlist", "mal_genre", "mal_studio", "mal_search"
]
mal_ranked_name = {
    "mal_all": "all", "mal_airing": "airing", "mal_upcoming": "upcoming", "mal_tv": "tv", "mal_ova": "ova",
    "mal_movie": "movie", "mal_special": "special", "mal_popular": "bypopularity", "mal_favorite": "favorite"
}
mal_ranked_pretty = {
    "mal_all": "MyAnimeList All", "mal_airing": "MyAnimeList Airing", "mal_search": "MyAnimeList Search",
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
search_types = ["tv", "movie", "ova", "special", "ona", "music"]
search_status = ["airing", "complete", "upcoming"]
search_ratings = ["g", "pg", "pg13", "r17", "r", "rx"]
search_sorts = ["mal_id", "title", "type", "rating", "start_date", "end_date", "episodes", "score", "scored_by", "rank", "popularity", "members", "favorites"]
search_combos = [f"{s}.{d}" for s in search_sorts for d in ["desc", "asc"]]
base_url = "https://api.myanimelist.net/v2/"
jiken_base_url = "https://api.jikan.moe/v4/"
urls = {
    "oauth_token": "https://myanimelist.net/v1/oauth2/token",
    "oauth_authorize": "https://myanimelist.net/v1/oauth2/authorize",
    "ranking": f"{base_url}anime/ranking",
    "season": f"{base_url}anime/season",
    "suggestions": f"{base_url}anime/suggestions",
    "user": f"{base_url}users"
}

class MyAnimeList:
    def __init__(self, config, params):
        self.config = config
        self.client_id = params["client_id"]
        self.client_secret = params["client_secret"]
        self.config_path = params["config_path"]
        self.authorization = params["authorization"]
        logger.secret(self.client_secret)
        if not self._save(self.authorization):
            if not self._refresh():
                self._authorization()
        self._genres = None
        self._studios = None

    @property
    def genres(self):
        if not self._genres:
            self._genres = {}
            for data in self._jiken_request("genres/anime")["data"]:
                self._genres[data["name"]] = int(data["mal_id"])
                self._genres[data["name"].lower()] = int(data["mal_id"])
                self._genres[str(data["mal_id"])] = int(data["mal_id"])
                self._genres[int(data["mal_id"])] = data["name"]
        return self._genres

    @property
    def studios(self):
        if not self._studios:
            for data in self._jiken_request("producers")["data"]:
                self._studios[data["name"]] = int(data["mal_id"])
                self._studios[data["name"].lower()] = int(data["mal_id"])
                self._studios[str(data["mal_id"])] = int(data["mal_id"])
                self._studios[int(data["mal_id"])] = data["name"]
        return self._studios

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
            if self.authorization != authorization and not self.config.read_only:
                yaml = YAML(self.config_path)
                yaml.data["mal"]["authorization"] = {
                    "access_token": authorization["access_token"],
                    "token_type": authorization["token_type"],
                    "expires_in": authorization["expires_in"],
                    "refresh_token": authorization["refresh_token"]
                }
                logger.info(f"Saving authorization information to {self.config_path}")
                yaml.save()
                logger.secret(authorization["access_token"])
            self.authorization = authorization
            return True
        return False

    def _oauth(self, data):
        return self.config.post_json(urls["oauth_token"], data=data)

    def _request(self, url, authorization=None):
        token = authorization["access_token"] if authorization else self.authorization["access_token"]
        if self.config.trace_mode:
            logger.debug(f"URL: {url}")
        try:
            response = self.config.get_json(url, headers={"Authorization": f"Bearer {token}"})
            if self.config.trace_mode:
                logger.debug(f"Response: {response}")
            if "error" in response:         raise Failed(f"MyAnimeList Error: {response['error']}")
            else:                           return response
        except JSONDecodeError:
            raise Failed(f"MyAnimeList Error: Connection Failed")

    def _jiken_request(self, url, params=None):
        data = self.config.get_json(f"{jiken_base_url}{url}", params=params)
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

    def _pagination(self, endpoint, params=None, limit=None):
        data = self._jiken_request(endpoint, params)
        last_visible_page = data["pagination"]["last_visible_page"]
        if limit is not None:
            total_items = data["pagination"]["items"]["total"]
            if total_items == 0:
                raise Failed("MyAnimeList Error: No MyAnimeList IDs for Search")
            if total_items < limit or limit <= 0:
                limit = total_items
        per_page = len(data["data"])
        mal_ids = []
        current_page = 1
        chances = 0
        while current_page <= last_visible_page:
            if chances > 6:
                logger.debug(data)
                raise Failed("AniList Error: Connection Failed")
            start_num = (current_page - 1) * per_page + 1
            end_num = limit if limit and (current_page == last_visible_page or limit < start_num + per_page) else current_page * per_page
            logger.ghost(f"Parsing Page {current_page}/{last_visible_page} {start_num}-{end_num}")
            if current_page > 1:
                if params is None:
                    params = {}
                params["page"] = current_page
                data = self._jiken_request(endpoint, params)
            if "data" in data:
                chances = 0
                mal_ids.extend(data["data"])
                if limit and len(mal_ids) >= limit:
                    return mal_ids[:limit]
                current_page += 1
            else:
                chances += 1
        logger.exorcise()
        return mal_ids

    def get_mal_ids(self, method, data):
        if method == "mal_id":
            logger.info(f"Processing MyAnimeList ID: {data}")
            mal_ids = [data]
        elif method in mal_ranked_name:
            logger.info(f"Processing {mal_ranked_pretty[method]}: {data} Anime")
            mal_ids = self._ranked(mal_ranked_name[method], data)
        elif method == "mal_search":
            logger.info(f"Processing {data[1]}")
            mal_ids = [mal_data["mal_id"] for mal_data in self._pagination("anime", params=data[0], limit=data[2])]
        elif method == "mal_genre":
            logger.info(f"Processing {mal_ranked_pretty[method]} ID: {data['genre_id']}")
            mal_ids = [mal_data["mal_id"] for mal_data in self._pagination("anime", params={"genres": data["genre_id"]}, limit=data["limit"])]
        elif method == "mal_studio":
            logger.info(f"Processing {mal_ranked_pretty[method]} ID: {data['studio_id']}")
            mal_ids = [mal_data["mal_id"] for mal_data in self._pagination("anime", params={"producers": data["studio_id"]}, limit=data["limit"])]
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
