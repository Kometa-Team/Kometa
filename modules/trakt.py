import time, webbrowser
from modules import util
from modules.request import urlparse
from modules.util import Failed, TimeoutExpired
from retrying import retry

logger = util.logger

redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
base_url = "https://api.trakt.tv"
builders = [
    "trakt_list", "trakt_list_details", "trakt_chart", "trakt_userlist", "trakt_boxoffice", "trakt_recommendations",
    "trakt_collected_daily", "trakt_collected_weekly", "trakt_collected_monthly", "trakt_collected_yearly", "trakt_collected_all",
    "trakt_recommended_daily", "trakt_recommended_weekly", "trakt_recommended_monthly", "trakt_recommended_yearly", "trakt_recommended_all",
    "trakt_watched_daily", "trakt_watched_weekly", "trakt_watched_monthly", "trakt_watched_yearly", "trakt_watched_all",
    "trakt_collection", "trakt_anticipated", "trakt_popular", "trakt_trending", "trakt_watchlist"
]
sorts = [
    "rank", "added", "title", "released", "runtime", "popularity",
    "percentage", "votes", "random", "my_rating", "watched", "collected"
]
status = ["returning", "production", "planned", "canceled", "ended"]
status_translation = {
    "returning": "returning series", "production": "in production",
    "planned": "planned", "canceled": "canceled", "ended": "ended"
}
userlist_options = ["favorites", "watched", "collection", "watchlist"]
periods = ["daily", "weekly", "monthly", "yearly", "all"]
id_translation = {"movie": "movie", "show": "show", "season": "show", "episode": "show", "person": "person", "list": "list"}
id_types = {
    "movie": ("tmdb", "TMDb ID"),
    "person": ("tmdb", "TMDb ID"),
    "show": ("tvdb", "TVDb ID"),
    "season": ("tvdb", "TVDb ID"),
    "episode": ("tvdb", "TVDb ID"),
    "list": ("slug", "Trakt Slug")
}

class Trakt:
    def __init__(self, requests, read_only, params):
        self.requests = requests
        self.read_only = read_only
        self.client_id = params["client_id"]
        self.client_secret = params["client_secret"]
        self.pin = params["pin"]
        self.config_path = params["config_path"]
        self.authorization = params["authorization"]
        logger.secret(self.client_secret)
        if not self._save(self.authorization):
            if not self._refresh():
                self._authorization()
        self._slugs = None
        self._movie_genres = None
        self._show_genres = None
        self._movie_languages = None
        self._show_languages = None
        self._movie_countries = None
        self._show_countries = None
        self._movie_certifications = None
        self._show_certifications = None

    @property
    def slugs(self):
        if self._slugs is None:
            items = []
            try:
                items = [i["ids"]["slug"] for i in self._request(f"/users/me/lists")]
            except Failed:
                pass
            self._slugs = items
        return self._slugs

    @property
    def movie_genres(self):
        if not self._movie_genres:
            self._movie_genres = [g["slug"] for g in self._request("/genres/movies")]
        return self._movie_genres

    @property
    def show_genres(self):
        if not self._show_genres:
            self._show_genres = [g["slug"] for g in self._request("/genres/shows")]
        return self._show_genres

    @property
    def movie_languages(self):
        if not self._movie_languages:
            self._movie_languages = [g["code"] for g in self._request("/languages/movies")]
        return self._movie_languages

    @property
    def show_languages(self):
        if not self._show_languages:
            self._show_languages = [g["code"] for g in self._request("/languages/shows")]
        return self._show_languages

    @property
    def movie_countries(self):
        if not self._movie_countries:
            self._movie_countries = [g["code"] for g in self._request("/countries/movies")]
        return self._movie_countries

    @property
    def show_countries(self):
        if not self._show_countries:
            self._show_countries = [g["code"] for g in self._request("/countries/shows")]
        return self._show_countries

    @property
    def movie_certifications(self):
        if not self._movie_certifications:
            self._movie_certifications = [g["slug"] for g in self._request("/certifications/movies")["us"]]
        return self._movie_certifications

    @property
    def show_certifications(self):
        if not self._show_certifications:
            self._show_certifications = [g["slug"] for g in self._request("/certifications/shows")["us"]]
        return self._show_certifications

    def _authorization(self):
        if self.pin:
            pin = self.pin
        else:
            url = f"https://trakt.tv/oauth/authorize?response_type=code&redirect_uri={redirect_uri}&client_id={self.client_id}"
            logger.info(f"Navigate to: {url}")
            logger.info("If you get an OAuth error your client_id or client_secret is invalid")
            webbrowser.open(url, new=2)
            try:
                pin = util.logger_input("Trakt pin (case insensitive)", timeout=300).strip()
            except TimeoutExpired:
                raise Failed("Input Timeout: Trakt pin required.")
        if not pin:
            raise Failed("Trakt Error: Trakt pin required.")
        json_data = {
            "code": pin,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = self.requests.post(f"{base_url}/oauth/token", json=json_data, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            raise Failed(f"Trakt Error: ({response.status_code}) {response.reason}")
        response_json = response.json()
        logger.trace(response_json)
        if not self._save(response_json):
            raise Failed("Trakt Error: New Authorization Failed")

    def _check(self, authorization=None):
        token = self.authorization['access_token'] if authorization is None else authorization['access_token']
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id
        }
        logger.secret(token)
        response = self.requests.get(f"{base_url}/users/settings", headers=headers)
        if response.status_code == 423:
            raise Failed("Trakt Error: Account is Locked please Contact Trakt Support")
        if response.status_code != 200:
            logger.debug(f"Trakt Error: ({response.status_code}) {response.reason}")
        return response.status_code == 200

    def _refresh(self):
        if self.authorization and "refresh_token" in self.authorization and self.authorization["refresh_token"]:
            logger.info("Refreshing Access Token...")
            json_data = {
                "refresh_token": self.authorization["refresh_token"],
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "refresh_token"
              }
            response = self.requests.post(f"{base_url}/oauth/token", json=json_data, headers={"Content-Type": "application/json"})
            if response.status_code != 200:
                return False
            return self._save(response.json())
        return False

    def _save(self, authorization):
        if authorization and self._check(authorization):
            if self.authorization != authorization and not self.read_only:
                yaml = self.requests.file_yaml(self.config_path)
                yaml.data["trakt"]["pin"] = None
                yaml.data["trakt"]["authorization"] = {
                    "access_token": authorization["access_token"],
                    "token_type": authorization["token_type"],
                    "expires_in": authorization["expires_in"],
                    "refresh_token": authorization["refresh_token"],
                    "scope": authorization["scope"],
                    "created_at": authorization["created_at"]
                }
                logger.info(f"Saving authorization information to {self.config_path}")
                yaml.save()
                self.authorization = authorization
            return True
        return False

    @retry(stop_max_attempt_number=6, wait_fixed=10000, retry_on_exception=util.retry_if_not_failed)
    def _request(self, url, params=None, json_data=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authorization['access_token']}",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id
        }
        output_json = []
        if params is None:
            params = {}
        pages = 1
        current = 1
        logger.trace(f"URL: {base_url}{url}")
        if params:
            logger.trace(f"Params: {params}")
        if json_data:
            logger.trace(f"JSON: {json_data}")
        while current <= pages:
            if pages > 1:
                params["page"] = current
            if json_data is not None:
                response = self.requests.post(f"{base_url}{url}", json=json_data, headers=headers)
            else:
                response = self.requests.get(f"{base_url}{url}", headers=headers, params=params)
            if pages == 1 and "X-Pagination-Page-Count" in response.headers and not params:
                pages = int(response.headers["X-Pagination-Page-Count"])
            if response.status_code >= 400:
                raise Failed(f"({response.status_code}) {response.reason}")
            response_json = response.json()
            logger.trace(f"Headers: {response.headers}")
            logger.trace(f"Response: {response_json}")
            if isinstance(response_json, dict):
                return response_json
            else:
                output_json.extend(response_json)
            current += 1
        return output_json

    def user_ratings(self, is_movie):
        media = "movie" if is_movie else "show"
        id_type = "tmdb" if is_movie else "tvdb"
        return {int(i[media]["ids"][id_type]): i["rating"] for i in self._request(f"/users/me/ratings/{media}s")}

    def convert(self, external_id, from_source, to_source, media_type):
        path = f"/search/{from_source}/{external_id}"
        params = {"type": media_type} if from_source in ["tmdb", "tvdb"] else None
        lookup = self._request(path, params=params)
        if lookup and media_type in lookup[0] and to_source in lookup[0][media_type]["ids"]:
            return lookup[0][media_type]["ids"][to_source]
        raise Failed(f"Trakt Error: No {to_source.upper().replace('B', 'b')} ID found for {from_source.upper().replace('B', 'b')} ID: {external_id}")

    def list_description(self, data):
        try:
            return self._request(urlparse(data).path)["description"]
        except Failed:
            raise Failed(data)

    def _parse(self, items, typeless=False, item_type=None, trakt_ids=False, ignore_other=False):
        ids = []
        for item in items:
            if typeless:
                data = item
                current_type = item_type
            elif item_type:
                data = item[item_type]
                current_type = item_type
            elif "type" in item and item["type"] in id_translation:
                data = item[id_translation[item["type"]]]
                current_type = item["type"]
            else:
                continue
            if current_type in ["person", "list"] and ignore_other:
                continue
            id_type, id_display = id_types[current_type]
            if id_type in data["ids"] and data["ids"][id_type]:
                final_id = data["ids"][id_type]
                if current_type == "episode":
                    final_id = f"{final_id}_{item[current_type]['season']}"
                if current_type in ["episode", "season"]:
                    final_id = f"{final_id}_{item[current_type]['number']}"
                if current_type in ["person", "list"]:
                    final_id = (final_id, data["name"])
                final_type = f"{id_type}_{current_type}" if current_type in ["episode", "season", "person"] else id_type
                ids.append((int(item["id"]), final_id, final_type) if trakt_ids else (final_id, final_type))
            else:
                name = data["name"] if current_type in ["person", "list"] else f"{data['title']} ({data['year']})"
                logger.warning(f"Trakt Error: No {id_display} found for {name}")
        return ids

    def _build_item_json(self, ids):
        data = {}
        for input_id, id_type in ids:
            movies = id_type in ["imdb", "tmdb"]
            shows = id_type in ["imdb", "tvdb", "tmdb_show", "tvdb_season", "tvdb_episode"]
            if not movies and not shows:
                continue
            type_set = str(id_type).split("_")
            id_set = str(input_id).split("_")
            item = {"ids": {type_set[0]: id_set[0] if type_set[0] == "imdb" else int(id_set[0])}}
            if id_type in ["tvdb_season", "tvdb_episode"]:
                season_data = {"number": int(id_set[1])}
                if id_type == "tvdb_episode":
                    season_data["episodes"] = [{"number": int(id_set[2])}]
                item["seasons"] = [season_data]
            if movies:
                if "movies" not in data:
                    data["movies"] = []
                data["movies"].append(item)
            if shows:
                if "shows" not in data:
                    data["shows"] = []
                data["shows"].append(item)
        return data

    def sync_list(self, slug, ids):
        current_ids = self._list(slug, parse=False, fail=False)

        def read_result(data, obj_type, result_type, result_str=None):
            result_str = result_str if result_str else result_type.capitalize()
            if data[result_type][obj_type] > 0:
                logger.info(f"{data[result_type][obj_type]} {obj_type.capitalize()} {result_str}")

        def read_not_found(data, result_str):
            not_found = []
            for item in data["not_found"]["movies"]:
                not_found.append((item["ids"]["tmdb"], "tmdb"))
            for item in data["not_found"]["shows"]:
                not_found.append((item["ids"]["tvdb"], "tvdb"))
            for item in data["not_found"]["seasons"]:
                not_found.append((f"{item['ids']['tvdb']}_{item['seasons'][0]['number']}", "tvdb_season"))
            for item in data["not_found"]["episodes"]:
                not_found.append((f"{item['ids']['tvdb']}_{item['seasons'][0]['number']}_{item['seasons'][0]['episodes'][0]['number']}", "tvdb_episode"))
            if not_found:
                logger.error(f"{len(not_found)} Items Unable to {result_str}: {not_found}")

        add_ids = [id_set for id_set in ids if id_set not in current_ids]
        if add_ids:
            logger.info("")
            results = self._request(f"/users/me/lists/{slug}/items", json_data=self._build_item_json(add_ids))
            for object_type in ["movies", "shows", "seasons", "episodes"]:
                read_result(results, object_type, "added")
            read_not_found(results, "Add")
            time.sleep(1)

        remove_ids = [id_set for id_set in current_ids if id_set not in ids]
        if remove_ids:
            logger.info("")
            results = self._request(f"/users/me/lists/{slug}/items/remove", json_data=self._build_item_json(remove_ids))
            for object_type in ["movies", "shows", "seasons", "episodes"]:
                read_result(results, object_type, "deleted", "Removed")
            read_not_found(results, "Remove")
            time.sleep(1)

        trakt_ids = self._list(slug, parse=False, trakt_ids=True)
        trakt_lookup = {f"{ty}_{i_id}": t_id for t_id, i_id, ty in trakt_ids}
        rank_ids = [trakt_lookup[f"{ty}_{i_id}"] for i_id, ty in ids if f"{ty}_{i_id}" in trakt_lookup]
        self._request(f"/users/me/lists/{slug}/items/reorder", json_data={"rank": rank_ids})
        logger.info("")
        logger.info("Trakt List Ordered Successfully")

    def all_user_lists(self, user="me"):
        try:
            items = self._request(f"/users/{user}/lists")
        except Failed:
            raise Failed(f"Trakt Error: User {user} not found")
        if len(items) == 0:
            raise Failed(f"Trakt Error: User {user} has no lists")
        return [(user, i["ids"]["slug"], i["name"]) for i in items]

    def all_liked_lists(self):
        items = self._request(f"/users/likes/lists")
        if len(items) == 0:
            raise Failed(f"Trakt Error: No Liked lists found")
        return {self.build_user_url(i['list']['user']['ids']['slug'], i['list']['ids']['slug']): i["list"]["name"] for i in items}

    def build_user_url(self, user, name):
        return f"{base_url.replace('api.', '')}/users/{user}/lists/{name}"

    def _list(self, data, parse=True, trakt_ids=False, fail=True, ignore_other=False):
        try:
            url = urlparse(data).path.replace("/official/", "/") if parse else f"/users/me/lists/{data}"
            items = self._request(f"{url}/items")
        except Failed:
            raise Failed(f"Trakt Error: List {data} not found")
        if len(items) == 0:
            if fail:
                raise Failed(f"Trakt Error: List {data} is empty")
            else:
                return []
        return self._parse(items, trakt_ids=trakt_ids, ignore_other=ignore_other)

    def _userlist(self, list_type, user, is_movie, sort_by=None, ignore_other=False):
        try:
            url_end = "movies" if is_movie else "shows"
            if sort_by:
                url_end = f"{url_end}/{sort_by}"
            items = self._request(f"/users/{user}/{list_type}/{url_end}")
        except Failed:
            raise Failed(f"Trakt Error: User {user} not found")
        if len(items) == 0:
            raise Failed(f"Trakt Error: {user}'s {list_type.capitalize()} is empty")
        return self._parse(items, item_type="movie" if is_movie else "show", ignore_other=ignore_other)

    def _recommendations(self, limit, is_movie):
        media_type = "Movie" if is_movie else "Show"
        try:
            items = self._request(f"/recommendations/{'movies' if is_movie else 'shows'}", params={"limit": limit})
        except Failed:
            raise Failed(f"Trakt Error: failed to fetch {media_type} Recommendations")
        if len(items) == 0:
            raise Failed(f"Trakt Error: no {media_type} Recommendations were found")
        return self._parse(items, typeless=True, item_type="movie" if is_movie else "show")

    def _charts(self, chart_type, is_movie, params, time_period=None, ignore_other=False):
        chart_url = f"{chart_type}/{time_period}" if time_period else chart_type
        items = self._request(f"/{'movies' if is_movie else 'shows'}/{chart_url}", params=params)
        return self._parse(items, typeless=chart_type == "popular", item_type="movie" if is_movie else "show", ignore_other=ignore_other)

    def get_people(self, data):
        return {str(i[0][0]): i[0][1] for i in self._list(data) if i[1] == "tmdb_person"} # noqa

    def validate_list(self, trakt_lists):
        values = util.get_list(trakt_lists, split=False)
        trakt_values = []
        for value in values:
            if isinstance(value, dict):
                raise Failed("Trakt Error: List cannot be a dictionary")
            try:
                self._list(value)
                trakt_values.append(value)
            except Failed as e:
                logger.error(e)
        if len(trakt_values) == 0:
            raise Failed(f"Trakt Error: No valid Trakt Lists in {values}")
        return trakt_values

    def validate_chart(self, err_type, method_name, data, is_movie):
        valid_dicts = []
        for trakt_dict in util.get_list(data, split=False):
            if not isinstance(trakt_dict, dict):
                raise Failed(f"{err_type} Error: {method_name} must be a dictionary")
            dict_methods = {dm.lower(): dm for dm in trakt_dict}
            try:
                if method_name == "trakt_chart":
                    final_dict = {}
                    final_dict["chart"] = util.parse(err_type, "chart", trakt_dict, methods=dict_methods, parent=method_name, options=["recommended", "watched", "anticipated", "collected", "trending", "popular"])
                    final_dict["limit"] = util.parse(err_type, "limit", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", default=10)
                    final_dict["time_period"] = None
                    if final_dict["chart"] in ["recommended", "watched", "collected"] and "time_period" in dict_methods:
                        final_dict["time_period"] = util.parse(err_type, "time_period", trakt_dict, methods=dict_methods, parent=method_name, default="weekly", options=periods)
                    if "query" in dict_methods:
                        final_dict["query"] = util.parse(err_type, "query", trakt_dict, methods=dict_methods, parent=method_name)
                    if "years" in dict_methods:
                        try:
                            if trakt_dict[dict_methods["years"]] and len(str(trakt_dict[dict_methods["years"]])) == 4:
                                final_dict["years"] = util.parse(err_type, "years", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=1000, maximum=3000)
                            else:
                                final_dict["years"] = util.parse(err_type, "years", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=1000, maximum=3000, range_split="-")
                        except Failed:
                            raise Failed(f"{err_type} Error: trakt_chart year attribute must be either a 4 digit year or a range of two 4 digit year with a '-' i.e. 1950 or 1950-1959")
                    if "runtimes" in dict_methods:
                        final_dict["runtimes"] = util.parse(err_type, "runtimes", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", range_split="-")
                    if "ratings" in dict_methods:
                        final_dict["ratings"] = util.parse(err_type, "ratings", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=0, maximum=100, range_split="-")
                    if "votes" in dict_methods:
                        final_dict["votes"] = util.parse(err_type, "votes", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=0, maximum=100000, range_split="-")
                    if "tmdb_ratings" in dict_methods:
                        final_dict["tmdb_ratings"] = util.parse(err_type, "tmdb_ratings", trakt_dict, methods=dict_methods, parent=method_name, datatype="float", minimum=0, maximum=10, range_split="-")
                    if "tmdb_votes" in dict_methods:
                        final_dict["tmdb_votes"] = util.parse(err_type, "tmdb_votes", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=0, maximum=100000, range_split="-")
                    if "imdb_ratings" in dict_methods:
                        final_dict["imdb_ratings"] = util.parse(err_type, "imdb_ratings", trakt_dict, methods=dict_methods, parent=method_name, datatype="float", minimum=0, maximum=10, range_split="-")
                    if "imdb_votes" in dict_methods:
                        final_dict["imdb_votes"] = util.parse(err_type, "imdb_votes", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=0, maximum=3000000, range_split="-")
                    if "rt_meters" in dict_methods:
                        final_dict["rt_meters"] = util.parse(err_type, "rt_meters", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=0, maximum=100, range_split="-")
                    if "rt_user_meters" in dict_methods:
                        final_dict["rt_user_meters"] = util.parse(err_type, "rt_user_meters", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=0, maximum=100, range_split="-")
                    if "metascores" in dict_methods:
                        final_dict["metascores"] = util.parse(err_type, "metascores", trakt_dict, methods=dict_methods, parent=method_name, datatype="int", minimum=0, maximum=100, range_split="-")
                    if "genres" in dict_methods:
                        final_dict["genres"] = util.parse(err_type, "genres", trakt_dict, methods=dict_methods, parent=method_name, datatype="commalist", options=self.movie_genres if is_movie else self.show_genres)
                    if "languages" in dict_methods:
                        final_dict["languages"] = util.parse(err_type, "languages", trakt_dict, methods=dict_methods, parent=method_name, datatype="commalist", options=self.movie_languages if is_movie else self.show_languages)
                    if "countries" in dict_methods:
                        final_dict["countries"] = util.parse(err_type, "countries", trakt_dict, methods=dict_methods, parent=method_name, datatype="commalist", options=self.movie_countries if is_movie else self.show_countries)
                    if "certifications" in dict_methods:
                        final_dict["certifications"] = util.parse(err_type, "certifications", trakt_dict, methods=dict_methods, parent=method_name, datatype="commalist", options=self.movie_certifications if is_movie else self.show_certifications)
                    if "studio_ids" in dict_methods and not is_movie:
                        final_dict["studio_ids"] = util.parse(err_type, "studio_ids", trakt_dict, methods=dict_methods, parent=method_name, datatype="commalist")
                    if "network_ids" in dict_methods and not is_movie:
                        final_dict["network_ids"] = util.parse(err_type, "network_ids", trakt_dict, methods=dict_methods, parent=method_name, datatype="commalist")
                    if "status" in dict_methods and not is_movie:
                        final_dict["status"] = util.parse(err_type, "status", trakt_dict, methods=dict_methods, parent=method_name, datatype="commalist", options=status)
                    valid_dicts.append(final_dict)
                else:
                    if "userlist" not in dict_methods:
                        raise Failed(f"{err_type} Error: {method_name} userlist attribute not found")
                    og_list = trakt_dict[dict_methods["userlist"]]
                    if not og_list:
                        raise Failed(f"{err_type} Error: {method_name} userlist attribute is blank")
                    if og_list == "collected":
                        logger.warning(f"{err_type} Warning: userlist value collected has been deprecated using collection")
                        userlist = "collection"
                    elif og_list == "recommendations":
                        raise Failed(f"{err_type} Error: {method_name} userlist value recommendations has been deprecated")
                    else:
                        userlist = util.parse(err_type, "userlist", trakt_dict, methods=dict_methods, parent=method_name, options=userlist_options)
                    user = util.parse(err_type, "user", trakt_dict, methods=dict_methods, parent=method_name, default="me")
                    sort_by = None
                    if userlist in ["favorites", "watchlist"] and "sort_by" in dict_methods:
                        sort_by = util.parse(err_type, "sort_by", trakt_dict, methods=dict_methods, parent=method_name, default="rank", options=["rank", "added", "released", "title"])
                    self._userlist(userlist, user, is_movie, sort_by=sort_by)
                    valid_dicts.append({"userlist": userlist, "user": user, "sort_by": sort_by})
            except Failed as e:
                logger.error(e)
        if len(valid_dicts) == 0:
            raise Failed(f"{err_type} Error: No valid Trakt {method_name[6:].capitalize()}")
        return valid_dicts

    def get_trakt_ids(self, method, data, is_movie):
        pretty = method.replace("_", " ").title()
        media_type = "Movie" if is_movie else "Show"
        if method == "trakt_list":
            logger.info(f"Processing {pretty}: {data}")
            return self._list(data, ignore_other=True)
        elif method == "trakt_recommendations":
            logger.info(f"Processing {pretty}: {data} {media_type}{'' if data == 1 else 's'}")
            return self._recommendations(data, is_movie)
        elif method == "trakt_chart":
            params = {"limit": data["limit"]}
            chart_limit = f"{data['limit']} {data['time_period'].capitalize()}" if data["time_period"] else data["limit"]
            logger.info(f"Processing {pretty}: {chart_limit} {data['chart'].capitalize()} {media_type}{'' if data == 1 else 's'}")
            for attr in ["query", "years", "runtimes", "ratings", "genres", "languages", "countries", "certifications", "network_ids", "studio_ids", "status", "votes", "tmdb_ratings", "tmdb_votes", "imdb_ratings", "imdb_votes", "rt_meters", "rt_user_meters", "metascores"]:
                if attr in data:
                    logger.info(f"{attr:>22}: {','.join(data[attr]) if isinstance(data[attr], list) else data[attr]}")
                    values = [status_translation[v] for v in data[attr]] if attr == "status" else data[attr]
                    params[attr] = ",".join(values) if isinstance(values, list) else values
            return self._charts(data["chart"], is_movie, params, time_period=data["time_period"], ignore_other=True)
        elif method == "trakt_userlist":
            logger.info(f"Processing {pretty} {media_type}s from {data['user']}'s {data['userlist'].capitalize()}")
            return self._userlist(data["userlist"], data["user"], is_movie, sort_by=data["sort_by"], ignore_other=True)
        elif method == "trakt_boxoffice":
            logger.info(f"Processing {pretty}: {data} {media_type}{'' if data == 1 else 's'}")
            return self._charts("boxoffice", is_movie, {"limit": data})
        else:
            raise Failed(f"Trakt Error: Method {method} not supported")
