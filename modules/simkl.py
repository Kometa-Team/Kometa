import time

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["simkl_trending", "simkl_dvd"]

base_url = "https://utilities.kometa.wiki/simkl-service"
oauth_token_url = "https://api.simkl.com/oauth2/token"
client_id = "1d2dc22b74616b53206f8dc1f65509abb9948b353a9a56b5554e234dde75c74a"
user_agent = "Kometa Official V2"
refresh_token_lifetime = 180 * 24 * 60 * 60
authenticated_user_url = "https://api.simkl.com/users/settings"

trending_periods = ["today", "week", "month"]


class Simkl:
    def __init__(self, requests, cache, read_only=False, config_path=None, authorization=None):
        self.requests = requests
        self.cache = cache
        self.read_only = read_only
        self.config_path = config_path
        self.authorization = dict(authorization) if isinstance(authorization, dict) else {}
        self.access_token = None
        self.token_type = self.authorization.get("token_type", "Bearer")

        for token_name in ["user_token", "access_token", "refresh_token"]:
            if self.authorization.get(token_name):
                logger.secret(self.authorization[token_name])

        if self.authorization.get("user_token") and not self.authorization.get("refresh_token"):
            logger.warning("Simkl Error: The configured user_token is an AUTH V1 token. Generate a new AUTH V2 refresh_token at https://utilities.kometa.wiki/simkl-oauth and replace the simkl config block.")
            return

        force_refresh = self.authorization.get("force_refresh") is True
        if force_refresh:
            try:
                self._refresh()
                self._authenticate_access_token()
            except Failed as e:
                self.access_token = None
                logger.error(e)
            return

        if self.authorization.get("access_token"):
            try:
                self._authenticate_access_token()
                return
            except Failed as e:
                logger.info(f"Simkl access token authentication failed; attempting refresh: {e}")

        if self.authorization.get("refresh_token"):
            try:
                self._refresh()
                self._authenticate_access_token()
            except Failed as e:
                self.access_token = None
                logger.error(e)
        elif self.authorization.get("access_token"):
            logger.error("Simkl Error: Authentication failed and no AUTH V2 refresh_token is configured. Generate a new token at https://utilities.kometa.wiki/simkl-oauth.")

    def _authenticate_access_token(self):
        access_token = self.authorization.get("access_token")
        if not access_token:
            raise Failed("Simkl Error: No access token is available for authentication.")
        self._validate_access_token(access_token)
        self.access_token = access_token
        self.token_type = self.authorization.get("token_type", "Bearer")

    def _validate_access_token(self, access_token):
        try:
            response = self.requests.get_json(
                authenticated_user_url,
                headers={"Authorization": f"Bearer {access_token}", "User-Agent": user_agent},
                params={"client_id": client_id},
            )
        except Exception as e:
            raise Failed("Simkl Error: Access token authentication failed.") from e

        if not isinstance(response, dict) or response.get("error"):
            error = response.get("error", "Invalid authentication response") if isinstance(response, dict) else "Invalid authentication response"
            raise Failed(f"Simkl Error: Access token authentication failed ({error}).")

        return response

    def _refresh(self):
        refresh_token = self.authorization.get("refresh_token")
        if not refresh_token:
            raise Failed("Simkl Error: No AUTH V2 refresh_token is configured. Generate one at https://utilities.kometa.wiki/simkl-oauth.")

        logger.info("Refreshing Simkl Access Token...")
        try:
            response = self.requests.post_json(
                oauth_token_url,
                data={"grant_type": "refresh_token", "client_id": client_id, "refresh_token": refresh_token},
                headers={"User-Agent": user_agent},
            )
        except Exception as e:
            raise Failed("Simkl Error: Failed to refresh the AUTH V2 token. Check the connection and try again.") from e

        if not isinstance(response, dict) or response.get("error") or not isinstance(response.get("access_token"), str) or not response.get("access_token"):
            error = response.get("error", "Invalid token response") if isinstance(response, dict) else "Invalid token response"
            raise Failed(f"Simkl Error: Token refresh failed ({error}). Generate a new AUTH V2 refresh_token at https://utilities.kometa.wiki/simkl-oauth.")

        try:
            expires_in = int(response["expires_in"])
            if expires_in <= 0:
                raise ValueError
        except (KeyError, TypeError, ValueError) as e:
            raise Failed("Simkl Error: Token refresh returned an invalid expires_in value. Generate a new AUTH V2 refresh_token at https://utilities.kometa.wiki/simkl-oauth.") from e

        now = int(time.time())
        self.authorization.pop("user_token", None)
        self.authorization.update(
            {
                "access_token": response["access_token"],
                "token_type": response.get("token_type", "Bearer"),
                "expires_in": expires_in,
                "access_token_expires_at": now + expires_in,
                "refresh_token": response.get("refresh_token") or refresh_token,
                "refresh_token_expires_at": now + refresh_token_lifetime,
            }
        )
        if response.get("scope"):
            self.authorization["scope"] = response["scope"]

        self.token_type = self.authorization["token_type"]
        logger.secret(self.authorization["access_token"])
        logger.secret(self.authorization["refresh_token"])
        try:
            self._save_authorization()
        except Exception:
            logger.warning(f"Simkl Warning: Access token was refreshed but could not be saved to {self.config_path}; it may refresh again on the next run.")

    def get_access_token(self):
        """Return the in-memory access token; refresh during client initialization when needed."""
        if not self.access_token:
            raise Failed("Simkl Error: No AUTH V2 refresh_token is configured. Generate one at https://utilities.kometa.wiki/simkl-oauth.")
        return self.access_token

    def _save_authorization(self):
        if not self.read_only and self.config_path and self.requests and hasattr(self.requests, "file_yaml"):
            yaml = self.requests.file_yaml(self.config_path)
            if "simkl" not in yaml.data or not isinstance(yaml.data["simkl"], dict):
                yaml.data["simkl"] = {}
            yaml.data["simkl"].pop("user_token", None)
            yaml.data["simkl"].update(self.authorization)
            logger.info(f"Saving SIMKL authorization information to {self.config_path}")
            yaml.save()

    def _request(self, endpoint):
        url = f"{base_url}/{endpoint}"
        response = self.requests.get(url)
        if response.status_code >= 400:
            raise Failed(f"Simkl Error: {response.status_code} - {response.text}")
        return response.json()

    def validate_simkl_dict(self, error_type, method_name, method_data):
        if method_name == "simkl_trending":
            if isinstance(method_data, dict):
                dict_methods = {dm.lower(): dm for dm in method_data}
                period = util.parse(error_type, "period", method_data, methods=dict_methods, default="today").lower()
                if period not in trending_periods:
                    raise Failed(f"{error_type} Error: simkl_trending period must be one of {trending_periods}")
                limit = util.parse(error_type, "limit", method_data, datatype="int", methods=dict_methods, default=20, minimum=1, maximum=500)
            else:
                period = "today"
                limit = util.parse(error_type, method_name, method_data, datatype="int", default=20, minimum=1, maximum=500)
            return {"period": period, "limit": limit}
        elif method_name == "simkl_dvd":
            if isinstance(method_data, dict):
                dict_methods = {dm.lower(): dm for dm in method_data}
                limit = util.parse(error_type, "limit", method_data, datatype="int", methods=dict_methods, default=20, minimum=1, maximum=500)
            else:
                limit = util.parse(error_type, method_name, method_data, datatype="int", default=20, minimum=1, maximum=500)
            return {"limit": limit}
        raise Failed(f"{error_type} Error: {method_name} not supported")

    def get_simkl_ids(self, method, data, is_movie):
        if method == "simkl_trending":
            return self._get_trending_ids(data, is_movie)
        elif method == "simkl_dvd":
            return self._get_dvd_ids(data, is_movie)
        raise Failed(f"Simkl Error: Method {method} not supported")

    def _get_trending_ids(self, data, is_movie):
        period = data["period"]
        limit = data["limit"]
        size = "large" if limit > 100 else "small"

        logger.info(f"Processing Simkl Trending ({period}, limit={limit})")
        response = self._request(f"trending/{period}/{size}")

        results = []
        if is_movie is True:
            sections = [("movies", "tmdb", None)]
        elif is_movie is False:
            sections = [("tv", "tmdb_show", "tvdb"), ("anime", "tmdb_show", "tvdb")]
        else:
            sections = [("movies", "tmdb", None), ("tv", "tmdb_show", "tvdb"), ("anime", "tmdb_show", "tvdb")]

        for section, tmdb_type, tvdb_type in sections:
            for item in response.get(section, []):
                if len(results) >= limit:
                    break
                ids = item.get("ids", {})
                tmdb_id = util.check_num(ids.get("tmdb"))
                tvdb_id = util.check_num(ids.get("tvdb"))
                if tmdb_id:
                    results.append((tmdb_id, tmdb_type))
                elif tvdb_type and tvdb_id:
                    results.append((tvdb_id, tvdb_type))

        logger.info(f"Simkl Trending: {len(results)} IDs found")
        return results

    def _get_dvd_ids(self, data, is_movie):
        limit = data["limit"]
        size = "large" if limit > 100 else "small"

        logger.info(f"Processing Simkl DVD Releases (limit={limit})")
        response = self._request(f"dvd/{size}")

        results = []
        for item in response:
            if len(results) >= limit:
                break
            ids = item.get("ids", {})
            tmdb_id = util.check_num(ids.get("tmdb"))
            tvdb_id = util.check_num(ids.get("tvdb"))
            is_show = bool(tvdb_id)

            if is_movie is None:
                if not is_show and tmdb_id:
                    results.append((tmdb_id, "tmdb"))
                elif is_show and tvdb_id:
                    results.append((tvdb_id, "tvdb"))
            elif is_movie and not is_show and tmdb_id:
                results.append((tmdb_id, "tmdb"))
            elif not is_movie and is_show and tvdb_id:
                results.append((tvdb_id, "tvdb"))

        logger.info(f"Simkl DVD: {len(results)} IDs found")
        return results
