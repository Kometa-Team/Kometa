from datetime import UTC, datetime, timedelta
from typing import ClassVar

from modules import tracker, util
from modules.util import Failed

logger = util.logger

base_url = "https://api.wetrakr.com"
utilities_client_ids_url = "https://raw.githubusercontent.com/Kometa-Team/Kometa-Utilities/main/CLIENT_IDS"
sync_batch_size = 5000
list_page_limit = 100
compact_page_limit = 1000
refresh_margin_seconds = 86400
builders = ["wetrakr_list", "wetrakr_list_details", "wetrakr_user_lists", "wetrakr_tracking", "wetrakr_favorites", "wetrakr_ratings"]
tracking_statuses = ["planning", "watching", "waiting", "watched", "paused", "dropped"]
movie_tracking_statuses = ["planning", "watched", "dropped"]
show_tracking_statuses = ["planning", "watching", "waiting", "watched", "paused", "dropped"]


class WeTrakr(tracker.TrackerAPI):
    service = "WeTrakr"
    base_url = base_url
    page_count_header = "X-Pagination-Page-Count"
    page_params: ClassVar[dict] = {"limit": list_page_limit}

    def __init__(self, requests, read_only, params):
        super().__init__(requests, read_only)
        self.client_id = params.get("client_id") or self._get_public_client_id()
        self.config_path = params["config_path"]
        authorization = params.get("authorization") or {}
        self.access_token = authorization.get("access_token")
        self.refresh_token = authorization.get("refresh_token")
        self.expires_at = self._parse_expires_at(authorization.get("expires_at"))
        self.user_agent = f"Kometa/{self.requests.local} (+https://kometa.wiki)"
        self._refreshed_this_call = False
        self._refreshed_this_run = False
        self._read_cache = {}
        if logger:
            if self.access_token:
                logger.secret(self.access_token)
            if self.refresh_token:
                logger.secret(self.refresh_token)
        if not self.access_token or not self.refresh_token:
            raise Failed("WeTrakr Error: authorization is blank; run the Kometa Utilities WeTrakr page and paste the resulting block into your config")

    def _get_public_client_id(self):
        response = self.requests.get(utilities_client_ids_url)
        if response.status_code != 200:
            raise Failed(f"WeTrakr Error: Unable to fetch public Client IDs from {utilities_client_ids_url}: ({response.status_code}) {response.reason}")
        for line in response.text.splitlines():
            key, separator, value = line.partition("=")
            if key.strip() == "WETRAKR_CLIENT_ID" and separator and value.strip():
                return value.strip()
        raise Failed(f"WeTrakr Error: Unable to find WETRAKR_CLIENT_ID in {utilities_client_ids_url}")

    @staticmethod
    def _parse_expires_at(value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            return None

    def test_connection(self):
        self._ensure_fresh_before_run()
        me = self._request("/account/settings") or {}
        username = (me.get("info") or {}).get("username")
        plan = me.get("plan")
        if logger:
            logger.info(f"WeTrakr Connected as {username} ({plan})" if username else "WeTrakr Connection Successful")

    def _ensure_fresh_before_run(self):
        if self.read_only:
            if self.expires_at is not None and self.expires_at <= datetime.now(UTC):
                raise Failed("WeTrakr Error: token has expired and `read_only` is set, so Kometa cannot rotate it; re-auth via the Kometa Utilities WeTrakr page every 7 days, or turn off `read_only`")
            return
        if self.expires_at is None or self.expires_at <= datetime.now(UTC) + timedelta(seconds=refresh_margin_seconds):
            self._refresh_token()

    def _headers(self, anonymous=False):
        headers = {"wetrakr-api-key": self.client_id, "wetrakr-api-version": "1", "Content-Type": "application/json", "User-Agent": self.user_agent}
        if not anonymous:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _retry_wait(self, response):
        # Daily-quota 429s never recover by waiting (resets at midnight UTC) - fail fast instead of looping.
        body = self._safe_json(response)
        if isinstance(body, dict) and body.get("error") == "QUOTA_EXCEEDED":
            raise Failed(f"WeTrakr Error: daily quota exceeded ({body.get('message') or 'no message'}); it resets at midnight UTC, waiting won't help this run")
        try:
            return float(response.headers.get("RateLimit-Reset"))
        except (TypeError, ValueError):
            return self.default_retry_wait

    def _send(self, path, url, headers, params, json_data, method):
        response = super()._send(path, url, headers, params, json_data, method)
        if response.status_code != 401 or path == "/oauth/token/refresh" or self.read_only or self._refreshed_this_call:
            return response
        self._refresh_token()
        self._refreshed_this_call = True
        try:
            retry_headers = dict(headers)
            if "Authorization" in retry_headers:
                retry_headers["Authorization"] = f"Bearer {self.access_token}"
            response = super()._send(path, url, retry_headers, params, json_data, method)
        finally:
            self._refreshed_this_call = False
        return response

    def _raise_for_status(self, path, response, ignore_404):
        if response.status_code == 401:
            raise Failed("WeTrakr Error: authorization was rejected; re-run the Kometa Utilities WeTrakr page and paste the new block")
        if response.status_code == 400 and path.startswith("/lists/"):
            raise Failed(f"WeTrakr Error: list at {path} is private or friends-only")
        if response.status_code == 403:
            raise Failed(f"WeTrakr Error: app key rejected or blocked at the edge (check User-Agent); {self._parse_error_body(response)}")
        if response.status_code == 420:
            body = self._safe_json(response)
            upgrade_url = (body.get("upgrade") or {}).get("url") if isinstance(body, dict) else None
            suffix = f" ({upgrade_url})" if upgrade_url else ""
            raise Failed(f"WeTrakr Error: {self._parse_error_body(response)}{suffix}")
        if response.status_code == 423:
            raise Failed("WeTrakr Error: Kometa's WeTrakr app key is suspended; report this in Kometa's Discord, not to WeTrakr")
        if response.status_code == 426:
            raise Failed(f"WeTrakr Error: this needs WeTrakr VIP; {self._parse_error_body(response)}")
        return super()._raise_for_status(path, response, ignore_404)

    @staticmethod
    def _safe_json(response):
        try:
            return response.json()
        except ValueError:
            return None

    def _refresh_token(self):
        if self._refreshed_this_run:
            raise Failed("WeTrakr Error: authorization was rejected; re-run the Kometa Utilities WeTrakr page and paste the new block")
        self._refreshed_this_run = True
        if logger:
            logger.info("Refreshing WeTrakr Access Token...")
        response = self.requests.post(f"{self.base_url}/oauth/token/refresh", json={"refresh_token": self.refresh_token}, headers=self._headers(anonymous=True))
        if response.status_code != 200:
            raise Failed("WeTrakr Error: authorization was rejected; re-run the Kometa Utilities WeTrakr page and paste the new block")
        data = response.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("new_refresh_token") or data.get("refresh_token")
        try:
            self.expires_at = datetime.now(UTC) + timedelta(seconds=int(data.get("expires_in")))
        except (TypeError, ValueError):
            self.expires_at = None
        if logger:
            logger.secret(self.access_token)
            logger.secret(self.refresh_token)
        self._save_authorization()

    def _save_authorization(self):
        yaml = self.requests.file_yaml(self.config_path)
        yaml.data.setdefault("wetrakr", {})["authorization"] = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.strftime("%Y-%m-%dT%H:%M:%SZ") if self.expires_at else None,
        }
        if logger:
            logger.info(f"Saving WeTrakr authorization to {self.config_path}")
        yaml.save()

    def _request_cursor(self, path, params=None):
        """Cursor-walked (compact=true) pagination: X-Pagination-Next -> after, no page param, stops when the header is absent."""
        url = f"{self.base_url}{path}"
        headers = self._headers()
        results = []
        base_params = dict(params or {})
        base_params.setdefault("compact", "true")
        base_params.setdefault("limit", compact_page_limit)
        after = None
        while True:
            call_params = dict(base_params)
            if after:
                call_params["after"] = after
            response = self._send(path, url, headers, call_params, None, "GET")
            if self._raise_for_status(path, response, False):
                return results
            if response.status_code == 204 or not response.content:
                return results
            try:
                data = response.json()
            except ValueError:
                raise Failed(f"{self.service} Error: {path} returned a non-JSON response body")
            if isinstance(data, list):
                results.extend(data)
            after = response.headers.get("X-Pagination-Next")
            if not after:
                return results

    def _memo(self, key, fetch):
        # Per-run memo (plan D8): the same personal read (e.g. three wetrakr_ratings ranges) walks the API once.
        if key not in self._read_cache:
            self._read_cache[key] = fetch()
        return self._read_cache[key]

    @staticmethod
    def _type_of(item):
        return {"movie": "movie", "show": "show"}.get(item.get("type"))

    def _parse_media(self, items, is_movie):
        # Season/episode/person rows are skipped cleanly (D12) rather than falling through to parse_ids' generic imdb match.
        filtered = []
        skipped = 0
        for item in items:
            if item.get("type") in ("movie", "show"):
                filtered.append(item)
            else:
                skipped += 1
        if skipped and logger:
            logger.debug(f"WeTrakr Debug: skipped {skipped} season/episode/person row(s)")
        return tracker.parse_ids(
            filtered,
            is_movie,
            service=self.service,
            type_of=self._type_of,
            native_id_of=lambda item: ("wetrakr", item.get("type"), item.get("id")),
        )

    @staticmethod
    def _target_for(is_movie):
        return "movies" if is_movie else ("shows" if is_movie is False else "all")

    @staticmethod
    def _parse_list_id(value):
        if isinstance(value, bool):
            raise Failed(f"WeTrakr Error: Could not parse a list id from {value}")
        if isinstance(value, int):
            return value
        text = str(value).strip()
        if text.isdigit():
            return int(text)
        candidate = text.rstrip("/").rsplit("/", 1)[-1]
        if candidate.isdigit():
            return int(candidate)
        raise Failed(f"WeTrakr Error: Could not parse a list id from {value}")

    def validate_lists(self, err_type, method_data):
        valid_ids = []
        for value in util.get_list(method_data, split=False, return_none=False):
            if isinstance(value, dict):
                raise Failed(f"{err_type} Error: WeTrakr List cannot be a dictionary")
            valid_ids.append(self._parse_list_id(value))
        if not valid_ids:
            raise Failed(f"{err_type} Error: No valid WeTrakr Lists")
        return valid_ids

    @staticmethod
    def _parse_user_id(value):
        # wetrakr.com profile URLs are username-based (/user/<name>), not numeric, so a URL can't be parsed into an id either - see WETRAKR-INTEGRATION-PLAN.md #13 item 2.
        text = str(value).strip() if not isinstance(value, bool) else ""
        if not text.isdigit():
            raise Failed("WeTrakr Error: wetrakr_user_lists needs a numeric WeTrakr user id; username lookup isn't available yet (WETRAKR-INTEGRATION-PLAN.md #13 item 2)")
        return int(text)

    @staticmethod
    def validate_user_id(err_type, method_data):
        try:
            return WeTrakr._parse_user_id(method_data)
        except Failed:
            raise Failed(f"{err_type} Error: wetrakr_user_lists needs a numeric WeTrakr user id; username lookup isn't available yet (WETRAKR-INTEGRATION-PLAN.md #13 item 2)")

    @staticmethod
    def validate_flag(err_type, method_name, method_data):
        return tracker.validate_flag(err_type, method_name, method_data)

    @staticmethod
    def validate_ratings(err_type, method_data):
        return tracker.validate_rating_range(err_type, "wetrakr_ratings", method_data)

    @staticmethod
    def validate_tracking(err_type, method_data):
        if method_data is None or isinstance(method_data, bool):
            enabled = method_data is not False
            return {status: enabled for status in tracking_statuses}
        if not isinstance(method_data, dict):
            raise Failed(f"{err_type} Error: wetrakr_tracking must be blank, true, false, or a dictionary of statuses")
        dict_methods = {dm.lower(): dm for dm in method_data}
        result = {}
        for status in tracking_statuses:
            if status in dict_methods:
                # Only run explicitly-named statuses through util.parse - passing an absent key's None through it
                # too would log a spurious "attribute is blank, using True as default" warning for every status
                # the user never mentioned.
                result[status] = util.parse(err_type, f"wetrakr_tracking {status}", method_data[dict_methods[status]], datatype="bool", default=True)
            else:
                result[status] = True
        if not any(result.values()):
            raise Failed(f"{err_type} Error: wetrakr_tracking has no enabled statuses")
        return result

    @staticmethod
    def _log_info(message):
        if logger:
            logger.info(message)

    def list_description(self, list_id):
        data = self._request(f"/lists/{list_id}") or {}
        description = data.get("description") or ""
        if not description:
            return ""
        link = f"https://wetrakr.com/lists/{list_id}" if data.get("privacy") == "public" else "https://wetrakr.com"
        return f"{description}\n\nList from WeTrakr: {link}"

    def _list_ids(self, list_id_or_url, is_movie):
        list_id = self._parse_list_id(list_id_or_url)
        target = self._target_for(is_movie)
        items = self._memo(("list_items", list_id, target), lambda: self._request_paginated(f"/lists/{list_id}/items/{target}") or [])
        return self._parse_media(items, is_movie)

    def _user_lists_ids(self, value, is_movie):
        user_id = self._parse_user_id(value)
        lists = self._memo(("user_lists", user_id), lambda: self._request_paginated(f"/users/{user_id}/lists", ignore_404=True))
        if lists is None:
            raise Failed(f"WeTrakr Error: user {user_id} not found")
        if not lists:
            raise Failed(f"WeTrakr Error: user {user_id} has no public lists (or their lists section is private)")
        self._log_info(f"Processing WeTrakr User Lists: {len(lists)} lists from user {user_id}")
        target = self._target_for(is_movie)
        ids = []
        seen = set()
        for entry in lists:
            list_id = entry.get("id")
            if list_id is None:
                continue
            if entry.get("privacy") != "public" or entry.get("locked"):
                if logger:
                    logger.debug(f"WeTrakr Debug: skipping list {list_id} ({'locked' if entry.get('locked') else 'not public'})")
                continue
            items = self._memo(("list_items", list_id, target), lambda list_id=list_id: self._request_paginated(f"/lists/{list_id}/items/{target}") or [])
            for item_id in self._parse_media(items, is_movie):
                if item_id not in seen:
                    seen.add(item_id)
                    ids.append(item_id)
        return ids

    def _tracking_ids(self, statuses, is_movie):
        allowed = movie_tracking_statuses if is_movie else (show_tracking_statuses if is_movie is False else tracking_statuses)
        enabled = [status for status in tracking_statuses if statuses.get(status) and status in allowed]
        if not enabled:
            library_kind = "movie" if is_movie else ("show" if is_movie is False else "mixed")
            raise Failed(f"WeTrakr Error: wetrakr_tracking has no statuses valid for a {library_kind} library")
        self._log_info(f"Processing WeTrakr Tracking: {', '.join(enabled)}")
        target = self._target_for(is_movie)
        items = []
        for status in enabled:
            items.extend(self._memo(("tracking", status, target), lambda status=status, target=target: self._request_cursor(f"/sync/tracking/{status}/{target}")))
        return self._parse_media(items, is_movie)

    def _favorites_ids(self, is_movie):
        target = self._target_for(is_movie)
        items = self._memo(("favorites", target), lambda: self._request_cursor(f"/sync/favorites/{target}"))
        return self._parse_media(items, is_movie)

    def _ratings_ids(self, value, is_movie):
        minimum = value.get("minimum") if isinstance(value, dict) else None
        maximum = value.get("maximum") if isinstance(value, dict) else None
        target = self._target_for(is_movie)
        items = self._memo(("ratings", target), lambda: self._request_cursor(f"/sync/ratings/{target}"))
        filtered = []
        for item in items:
            rating = item.get("rating")
            if rating is None:
                continue
            if minimum is not None and rating < minimum:
                continue
            if maximum is not None and rating > maximum:
                continue
            filtered.append(item)
        return self._parse_media(filtered, is_movie)

    def get_wetrakr_ids(self, method, value, is_movie):
        pretty = method.replace("_", " ").title()
        if method in ("wetrakr_list", "wetrakr_list_details"):
            self._log_info(f"Processing {pretty}: {value}")
            return self._list_ids(value, is_movie)
        if method == "wetrakr_user_lists":
            return self._user_lists_ids(value, is_movie)
        if method == "wetrakr_tracking":
            return self._tracking_ids(value, is_movie)
        if method == "wetrakr_favorites":
            self._log_info(f"Processing {pretty}")
            return self._favorites_ids(is_movie)
        if method == "wetrakr_ratings":
            self._log_info(f"Processing {pretty}")
            return self._ratings_ids(value, is_movie)
        raise Failed(f"WeTrakr Error: Method {method} not supported")
