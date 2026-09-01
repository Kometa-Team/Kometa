from collections import defaultdict
from datetime import datetime, timedelta, timezone
from uuid import UUID

from modules import util
from modules.util import Failed

logger = util.logger

builders = [
    "tracearr_history",
    "tracearr_popular",
    "tracearr_watched",
    "tracearr_trending",
    "tracearr_rewatched",
    "tracearr_completed",
    "tracearr_binged",
    "tracearr_transcoded",
    "tracearr_watch_time",
    "tracearr_in_progress",
]

decisions = ["directplay", "copy", "transcode"]


class Tracearr:
    def __init__(self, requests, library, params):
        self.requests = requests
        self.library = library
        self.url = params["url"].rstrip("/")
        self.apikey = str(params["apikey"]).strip() if params["apikey"] else None
        self.api = f"{self.url}/api/v1/public"
        self.history_api = f"{self.url}/api/v2/public"
        self.history_version = None
        self._history_cache = {}
        self._users_cache = None
        self._history_until = None
        logger.secret(self.url)
        logger.secret(self.apikey)
        if not self.apikey:
            raise Failed("Tracearr Error: API key is required")
        if not self.apikey.startswith("trr_pub_"):
            raise Failed("Tracearr Error: API key must begin with 'trr_pub_'")
        health = self._request("health")
        self.server_id = self._resolve_server_id(health, params.get("server_id"))
        self.history_version = 2 if self._request("docs", api=self.history_api, allow_404=True) is not None else 1
        if self.history_version == 1:
            logger.warning("Tracearr Warning: Public API v2 is unavailable; using v1 without Plex library-aware matching or v2 filters")

    def _resolve_server_id(self, health, configured_server_id):
        servers = health.get("servers") if isinstance(health, dict) else None
        if not isinstance(servers, list):
            raise Failed("Tracearr Error: /health response is missing the servers list")
        plex_servers = [server for server in servers if isinstance(server, dict) and server.get("type") == "plex" and server.get("id")]
        if configured_server_id:
            try:
                server_id = str(UUID(str(configured_server_id)))
            except ValueError:
                raise Failed(f"Tracearr Error: server_id '{configured_server_id}' is not a valid UUID")
            match = next((server for server in plex_servers if str(server["id"]).lower() == server_id), None)
            if match:
                return str(match["id"])
            raise Failed(f"Tracearr Error: server_id '{configured_server_id}' is not a configured Plex server in Tracearr")

        plex_name = str(self.library.PlexServer.friendlyName)
        name_matches = [server for server in plex_servers if str(server.get("name", "")).casefold() == plex_name.casefold()]
        if len(name_matches) == 1:
            return str(name_matches[0]["id"])
        if len(plex_servers) == 1:
            return str(plex_servers[0]["id"])

        options = ", ".join(f"{server.get('name', 'Unknown')} ({server['id']})" for server in plex_servers) or "None"
        if len(name_matches) > 1:
            reason = f"multiple Tracearr Plex servers match '{plex_name}'"
        else:
            reason = f"no Tracearr Plex server matches '{plex_name}'"
        raise Failed(f"Tracearr Error: {reason}; set tracearr server_id explicitly. Options: {options}")

    def get_rating_keys(self, data, is_playlist=False, libraries=None):
        list_type = data["list_type"]
        if list_type == "in_progress" and self.history_version != 2:
            raise Failed("Tracearr Error: tracearr_in_progress requires Tracearr Public API v2")
        pretty = "History" if list_type == "history" else list_type.capitalize()
        media_label = "Items" if is_playlist else "Movies" if self.library.is_movie else "Shows"
        logger.info(f"Processing Tracearr {pretty}: {data['list_size']} {media_label}")

        history_until = getattr(self, "_history_until", None)
        if history_until is None:
            history_until = datetime.now(timezone.utc)
            self._history_until = history_until
        cutoff = history_until - timedelta(days=int(data["list_days"]))
        user_id = self._resolve_user(data.get("user"))
        params = {
            "pageSize": 100,
            "since": cutoff.isoformat(),
            "until": history_until.isoformat(),
            "server_id": self.server_id,
        }
        if user_id and self.history_version == 2:
            params["user_id"] = user_id
        if is_playlist and list_type == "binged":
            params["media_type"] = "episode"
        elif not is_playlist and self.library.is_movie:
            params["media_type"] = "movie"
        elif not is_playlist and self.library.is_show:
            params["media_type"] = "episode"

        search_libraries = libraries if libraries else [self.library]
        library_ids = {str(search_library.Plex.key) for search_library in search_libraries} if is_playlist else None
        items = self._filter_history(self._fetch_history(params), data, user_id, library_ids=library_ids)
        aggregated = self._aggregate_history(items, list_type, int(data["list_minimum"]))
        rating_keys = []
        seen = set()
        result_seen = set()
        for item in aggregated:
            if len(rating_keys) >= int(data["list_size"]):
                break
            media_type = item["media_type"]
            title = item["title"]
            year = item["year"]
            library_id = item["library_id"]
            rating_key = item["rating_key"]
            dedupe_key = (media_type, library_id, rating_key or title, year)
            if dedupe_key in seen:
                continue
            libtype = "movie" if media_type == "movie" else "show"
            matched = False
            matching_libraries = [
                search_library
                for search_library in search_libraries
                if not ((media_type == "movie" and not search_library.is_movie) or (media_type in {"show", "episode"} and not search_library.is_show)) and (library_id is None or str(search_library.Plex.key) == str(library_id))
            ]
            if not matching_libraries:
                continue
            direct_id = self._history_item_id(item) if is_playlist else None
            if direct_id:
                if direct_id not in result_seen:
                    rating_keys.append(direct_id)
                    result_seen.add(direct_id)
                seen.add(dedupe_key)
                continue
            if is_playlist and media_type == "episode":
                logger.error(Failed(f"Tracearr Error: No Plex rating key found for episode {title}"))
                seen.add(dedupe_key)
                continue
            for search_library in matching_libraries:
                plex_item = None
                if rating_key:
                    try:
                        plex_item = search_library.fetch_item(rating_key)
                    except Failed as e:
                        logger.debug(e)
                if plex_item is None:
                    new_items = search_library.exact_search(title, libtype=libtype, year=year if media_type == "movie" else None)
                    if not new_items:
                        continue
                    plex_item = new_items[0]
                if is_playlist:
                    item_id = self._playlist_item_id(search_library, plex_item, media_type)
                    if item_id:
                        if item_id not in result_seen:
                            rating_keys.append(item_id)
                            result_seen.add(item_id)
                    else:
                        logger.error(Failed(f"Tracearr Error: No supported external ID found for {title}"))
                        continue
                else:
                    item_id = (plex_item.ratingKey, "ratingKey")
                    if item_id not in result_seen:
                        rating_keys.append(item_id)
                        result_seen.add(item_id)
                seen.add(dedupe_key)
                matched = True
                break
            if not matched:
                display_year = f" ({year})" if year else ""
                logger.error(Failed(f"Tracearr Error: {title}{display_year} not found in Plex"))

        return rating_keys

    @staticmethod
    def _history_item_id(item):
        if item["media_type"] == "movie":
            if item.get("tmdb_id"):
                return item["tmdb_id"], "tmdb"
            if item.get("imdb_id"):
                return item["imdb_id"], "imdb"
        elif item["media_type"] == "episode" and item.get("rating_key"):
            return item["rating_key"], "ratingKey"
        return None

    @staticmethod
    def _playlist_item_id(library, item, media_type):
        tmdb_id, tvdb_id, imdb_id = library.get_ids(item)
        if media_type == "movie" and tmdb_id:
            return tmdb_id, "tmdb"
        if media_type == "show" and tvdb_id:
            return tvdb_id, "tvdb"
        if imdb_id:
            return imdb_id, "imdb"
        if getattr(item, "guid", None):
            return item.guid, "plex"
        return None

    def _fetch_history(self, params):
        cache_key = tuple(sorted(params.items()))
        if not hasattr(self, "_history_cache"):
            self._history_cache = {}
        if cache_key in self._history_cache:
            return self._history_cache[cache_key]
        if self.history_version == 1:
            items = self._fetch_history_v1(params)
            self._history_cache[cache_key] = items
            return items
        items = []
        request_params = dict(params)
        cursors = set()
        while True:
            response = self._request("history", params=request_params, api=self.history_api, allow_404=not items and "cursor" not in request_params)
            if response is None:
                self.history_version = 1
                logger.warning("Tracearr Warning: Public API v2 is unavailable; falling back to v1 without Plex library-aware matching")
                items = self._fetch_history_v1(params)
                self._history_cache[cache_key] = items
                return items
            page_items = response.get("data")
            meta = response.get("meta")
            if not isinstance(page_items, list) or not isinstance(meta, dict):
                raise Failed("Tracearr Error: /history response must contain data and pagination metadata")
            items.extend(page_items)
            next_cursor = meta.get("nextCursor")
            if next_cursor is None:
                break
            if not isinstance(next_cursor, str) or not next_cursor or next_cursor in cursors:
                raise Failed("Tracearr Error: /history response contains invalid pagination metadata")
            cursors.add(next_cursor)
            request_params["cursor"] = next_cursor
        self._history_cache[cache_key] = items
        return items

    def _resolve_user(self, user):
        if not user:
            return None
        user_value = str(user).strip()
        if self.history_version != 2:
            return user_value
        users_cache = getattr(self, "_users_cache", None)
        if users_cache is None:
            users_cache = []
            self._users_cache = users_cache
            request_params: dict[str, object] = {"pageSize": 100}
            cursors = set()
            while True:
                response = self._request("users", params=request_params, api=self.history_api)
                if not isinstance(response, dict):
                    raise Failed("Tracearr Error: Invalid response from /users")
                page_users = response.get("data")
                meta = response.get("meta")
                if not isinstance(page_users, list) or not isinstance(meta, dict):
                    raise Failed("Tracearr Error: /users response must contain data and pagination metadata")
                users_cache.extend(page_users)
                next_cursor = meta.get("nextCursor")
                if next_cursor is None:
                    break
                if not isinstance(next_cursor, str) or not next_cursor or next_cursor in cursors:
                    raise Failed("Tracearr Error: /users response contains invalid pagination metadata")
                cursors.add(next_cursor)
                request_params["cursor"] = next_cursor

        folded = user_value.casefold()
        matches = []
        for identity in users_cache:
            values = [identity.get("id"), identity.get("username"), identity.get("plex_account_id")]
            for account in identity.get("accounts") or []:
                values.extend([account.get("external_user_id"), account.get("username")])
            if any(str(value).casefold() == folded for value in values if value is not None):
                matches.append(identity)
        unique_matches = {str(identity.get("id")): identity for identity in matches if identity.get("id")}
        if len(unique_matches) == 1:
            return next(iter(unique_matches))
        if not unique_matches:
            options = ", ".join(sorted(str(identity.get("username")) for identity in users_cache if identity.get("username"))) or "None"
            raise Failed(f"Tracearr Error: user '{user_value}' not found. Options: {options}")
        options = ", ".join(sorted(f"{identity.get('username')} ({identity_id})" for identity_id, identity in unique_matches.items()))
        raise Failed(f"Tracearr Error: user '{user_value}' is ambiguous. Matches: {options}")

    def _filter_history(self, items, data, user_id, library_ids=None):
        filtered = []
        in_progress = data["list_type"] == "in_progress"
        for item in items:
            library_id = self._field(item, "library_id", "libraryId")
            if library_ids and library_id is not None and str(library_id) not in library_ids:
                continue
            user = item.get("user") or {}
            if user_id and not (str(user.get("id", "")).casefold() == str(user_id).casefold() or str(user.get("username", "")).casefold() == str(data.get("user", "")).casefold()):
                continue
            if not in_progress and data.get("watched") is not None and (item.get("watched") is True) != data["watched"]:
                continue
            percent_complete = self._percent_complete(item)
            if not in_progress and data.get("minimum_progress") is not None and (percent_complete is None or float(percent_complete) < data["minimum_progress"]):
                continue
            if not in_progress and data.get("maximum_progress") is not None and (percent_complete is None or float(percent_complete) > data["maximum_progress"]):
                continue
            is_transcode = (
                self._field(item, "is_transcode", "isTranscode") is True
                or str(self._field(item, "video_decision", "videoDecision") or "").casefold() == "transcode"
                or str(self._field(item, "audio_decision", "audioDecision") or "").casefold() == "transcode"
            )
            if data.get("transcode") is not None and is_transcode != data["transcode"]:
                continue
            if not self._matches_value(item, data, "video_decision", "videoDecision") or not self._matches_value(item, data, "audio_decision", "audioDecision"):
                continue
            if not self._matches_value(item, data, "platform") or not self._matches_value(item, data, "device") or not self._matches_value(item, data, "resolution"):
                continue
            if not self._matches_value(item, data, "source_video_codec", "sourceVideoCodec") or not self._matches_value(item, data, "source_audio_codec", "sourceAudioCodec"):
                continue
            subtitle = self._field(item, "subtitle_info", "subtitleInfo") or {}
            if data.get("subtitle_decision") and str(subtitle.get("decision", "")).casefold() != str(data["subtitle_decision"]).casefold():
                continue
            transcode_info = self._field(item, "transcode_info", "transcodeInfo") or {}
            if data.get("transcode_reason") and not any(str(data["transcode_reason"]).casefold() in str(reason).casefold() for reason in transcode_info.get("reasons") or []):
                continue
            genres = item.get("genres") or []
            if data.get("genre") and not any(str(genre).casefold() == str(data["genre"]).casefold() for genre in genres):
                continue
            filtered.append(item)

        if in_progress:
            latest = {}
            for item in filtered:
                source_media_type = str(self._field(item, "media_type", "mediaType") or "").lower()
                title = self._field(item, "media_title", "mediaTitle") if source_media_type == "movie" else self._field(item, "show_title", "showTitle")
                identity = self._field(item, "media_id", "mediaId") if source_media_type == "movie" else self._field(item, "show_media_id", "showMediaId")
                user = item.get("user") or {}
                key = (user.get("id") or user.get("username"), source_media_type, identity or title)
                timestamp = self._parse_ts(self._field(item, "stopped_at", "stoppedAt") or self._field(item, "started_at", "startedAt"))
                if key not in latest or (timestamp or datetime.min.replace(tzinfo=timezone.utc)) > latest[key][0]:
                    latest[key] = (timestamp or datetime.min.replace(tzinfo=timezone.utc), item)
            filtered = []
            for _, item in latest.values():
                percent_complete = self._percent_complete(item)
                if item.get("watched") is True or percent_complete is None:
                    continue
                if data.get("minimum_progress") is not None and float(percent_complete) < data["minimum_progress"]:
                    continue
                if data.get("maximum_progress") is not None and float(percent_complete) > data["maximum_progress"]:
                    continue
                filtered.append(item)
        return filtered

    def _matches_value(self, item, data, snake_case, camel_case=None):
        expected = data.get(snake_case)
        if expected is None:
            return True
        actual = self._field(item, snake_case, camel_case)
        return actual is not None and str(actual).casefold() == str(expected).casefold()

    def _percent_complete(self, item):
        percent_complete = self._field(item, "percent_complete", "percentComplete")
        if percent_complete is not None:
            return float(percent_complete)
        progress = self._field(item, "progress_ms", "progressMs")
        total = self._field(item, "total_duration_ms", "totalDurationMs")
        if progress is not None and total:
            return min(float(progress) / float(total) * 100, 100)
        return None

    def _fetch_history_v1(self, params):
        request_params = {
            "page": 1,
            "pageSize": params["pageSize"],
            "startDate": str(params["since"])[:10],
            "endDate": str(params["until"])[:10],
            "serverId": params["server_id"],
        }
        if "media_type" in params:
            request_params["mediaType"] = params["media_type"]
        items = []
        while True:
            response = self._request("history", params=request_params)
            if response is None:
                raise Failed("Tracearr Error: Invalid response from /api/v1/public/history")
            page_items = response.get("data")
            meta = response.get("meta")
            if not isinstance(page_items, list) or not isinstance(meta, dict):
                raise Failed("Tracearr Error: /history response must contain data and pagination metadata")
            if not page_items:
                break
            items.extend(page_items)
            try:
                total = int(meta["total"])
            except (KeyError, TypeError, ValueError):
                raise Failed("Tracearr Error: /history response contains invalid pagination metadata")
            if len(items) >= total or len(page_items) < int(request_params["pageSize"]):
                break
            request_params["page"] += 1
        return items

    @staticmethod
    def _field(item, snake_case, camel_case=None):
        if snake_case in item:
            return item[snake_case]
        return item.get(camel_case) if camel_case else None

    def _aggregate_history(self, items, list_type, minimum):
        grouped = defaultdict(
            lambda: {
                "media_type": None,
                "title": None,
                "year": None,
                "library_id": None,
                "rating_key": None,
                "total_sessions": 0,
                "completed_sessions": 0,
                "unique_users": set(),
                "sessions_by_user": defaultdict(int),
                "last_played": None,
                "last_completed": None,
                "repeat_plays": 0,
                "rewatching_users": 0,
                "watched_episodes_by_user": defaultdict(set),
                "binged_episodes": 0,
                "binging_users": 0,
                "transcoded_sessions": 0,
                "watch_time_ms": 0,
                "tmdb_id": None,
                "imdb_id": None,
            }
        )

        for item in items:
            item_server_id = self._field(item, "server_id", "serverId")
            if item_server_id and item_server_id != self.server_id:
                continue

            source_media_type = str(self._field(item, "media_type", "mediaType") or "").lower()
            if source_media_type not in {"movie", "episode"}:
                continue
            if source_media_type == "movie":
                media_type = "movie"
            elif list_type == "in_progress":
                media_type = "episode"
            else:
                media_type = "show"
            title = self._field(item, "media_title", "mediaTitle") if media_type in {"movie", "episode"} else self._field(item, "show_title", "showTitle")
            if not title:
                continue
            year = self._field(item, "year") if media_type in {"movie", "episode"} else None
            library_id = self._field(item, "library_id", "libraryId")
            rating_key = self._field(item, "rating_key", "ratingKey") if media_type in {"movie", "episode"} else self._field(item, "grandparent_rating_key", "grandparentRatingKey")
            canonical_id = self._field(item, "media_id", "mediaId") if media_type in {"movie", "episode"} else self._field(item, "show_media_id", "showMediaId")
            media_identity = rating_key or canonical_id or (title, year)
            key = (media_type, str(library_id) if library_id is not None else None, media_identity)
            entry = grouped[key]
            entry["media_type"] = media_type
            entry["title"] = title
            entry["year"] = year
            entry["library_id"] = library_id
            entry["rating_key"] = rating_key
            entry["tmdb_id"] = entry["tmdb_id"] or self._field(item, "tmdb_id", "tmdbId")
            entry["imdb_id"] = entry["imdb_id"] or self._field(item, "imdb_id", "imdbId")
            entry["total_sessions"] += 1
            entry["watch_time_ms"] += int(self._field(item, "duration_ms", "durationMs") or 0)
            watched = item.get("watched") is True
            if watched:
                entry["completed_sessions"] += 1
            user = item.get("user") or {}
            user_id = user.get("id") or user.get("username")
            if user_id:
                user_key = str(user_id)
                entry["unique_users"].add(user_key)
                entry["sessions_by_user"][user_key] += 1
            if watched and media_type == "show" and user_id:
                season_number = self._field(item, "season_number", "seasonNumber")
                episode_number = self._field(item, "episode_number", "episodeNumber")
                episode_rating_key = self._field(item, "rating_key", "ratingKey")
                episode_key = episode_rating_key or ((season_number, episode_number) if season_number is not None or episode_number is not None else self._field(item, "media_title", "mediaTitle"))
                if episode_key:
                    entry["watched_episodes_by_user"][str(user_id)].add(episode_key)
            if self._field(item, "is_transcode", "isTranscode") is True or str(self._field(item, "video_decision", "videoDecision") or "").lower() == "transcode" or str(self._field(item, "audio_decision", "audioDecision") or "").lower() == "transcode":
                entry["transcoded_sessions"] += 1
            ts = self._field(item, "stopped_at", "stoppedAt") or self._field(item, "started_at", "startedAt")
            parsed_ts = self._parse_ts(ts)
            if parsed_ts and (entry["last_played"] is None or parsed_ts > entry["last_played"]):
                entry["last_played"] = parsed_ts
            if watched and parsed_ts and (entry["last_completed"] is None or parsed_ts > entry["last_completed"]):
                entry["last_completed"] = parsed_ts

        ranked = []
        for entry in grouped.values():
            session_counts = list(entry["sessions_by_user"].values())
            entry["repeat_plays"] = sum(max(count - 1, 0) for count in session_counts)
            entry["rewatching_users"] = sum(1 for count in session_counts if count >= 2)
            episode_counts = [len(episodes) for episodes in entry["watched_episodes_by_user"].values()]
            entry["binged_episodes"] = max(episode_counts, default=0)
            entry["binging_users"] = sum(1 for count in episode_counts if count >= 2)
            if list_type in {"watched", "completed"} and not entry["completed_sessions"]:
                continue
            if list_type == "rewatched" and not entry["repeat_plays"]:
                continue
            if list_type == "binged" and (entry["media_type"] != "show" or entry["binged_episodes"] < 2):
                continue
            if list_type == "transcoded" and not entry["transcoded_sessions"]:
                continue
            if list_type == "in_progress" and entry["completed_sessions"]:
                continue
            count_value = {
                "popular": len(entry["unique_users"]),
                "watched": entry["completed_sessions"],
                "trending": entry["total_sessions"],
                "rewatched": entry["repeat_plays"],
                "completed": entry["completed_sessions"],
                "binged": entry["binged_episodes"],
                "transcoded": entry["transcoded_sessions"],
                "watch_time": entry["watch_time_ms"] // 60000,
                "in_progress": entry["total_sessions"],
                "history": entry["total_sessions"],
            }.get(list_type, entry["total_sessions"])
            if count_value < minimum:
                continue
            ranked.append(entry)

        sort_map = {
            "history": lambda e: (e["last_played"] or datetime.min.replace(tzinfo=timezone.utc), e["total_sessions"], len(e["unique_users"])),
            "popular": lambda e: (len(e["unique_users"]), e["total_sessions"], e["last_played"] or datetime.min.replace(tzinfo=timezone.utc)),
            "watched": lambda e: (e["completed_sessions"], e["total_sessions"], e["last_played"] or datetime.min.replace(tzinfo=timezone.utc)),
            "trending": lambda e: (e["total_sessions"], len(e["unique_users"]), e["last_played"] or datetime.min.replace(tzinfo=timezone.utc)),
            "rewatched": lambda e: (e["repeat_plays"], e["rewatching_users"], e["total_sessions"], e["last_played"] or datetime.min.replace(tzinfo=timezone.utc)),
            "completed": lambda e: (e["last_completed"] or datetime.min.replace(tzinfo=timezone.utc), e["completed_sessions"], e["total_sessions"]),
            "binged": lambda e: (e["binged_episodes"], e["binging_users"], e["completed_sessions"], e["last_completed"] or datetime.min.replace(tzinfo=timezone.utc)),
            "transcoded": lambda e: (e["transcoded_sessions"], len(e["unique_users"]), e["last_played"] or datetime.min.replace(tzinfo=timezone.utc)),
            "watch_time": lambda e: (e["watch_time_ms"], e["total_sessions"], e["last_played"] or datetime.min.replace(tzinfo=timezone.utc)),
            "in_progress": lambda e: (e["last_played"] or datetime.min.replace(tzinfo=timezone.utc), e["watch_time_ms"]),
        }
        ranked.sort(key=sort_map.get(list_type, sort_map["history"]), reverse=True)
        return ranked

    def _parse_ts(self, ts):
        if not ts:
            return None
        try:
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except ValueError:
            return None

    def _headers(self):
        return {"Authorization": f"Bearer {self.apikey}"}

    def _request(self, endpoint, params=None, api=None, allow_404=False):
        request_api = api or self.api
        logger.trace(f"Tracearr CMD: {endpoint}")
        if params:
            logger.trace(f"Tracearr Params: {params}")
        try:
            response = self.requests.get(f"{request_api}/{endpoint}", params=params, headers=self._headers())
        except Exception as e:
            raise Failed(f"Tracearr Error: Unable to connect to {self.url}: {e}") from e
        if response.status_code == 404 and allow_404:
            return None
        try:
            payload = response.json()
        except ValueError as e:
            raise Failed(f"Tracearr Error: Non-JSON response from {request_api.removeprefix(self.url)}/{endpoint} (HTTP {response.status_code})") from e
        if response.status_code >= 400:
            detail = (payload.get("message") or payload.get("error")) if isinstance(payload, dict) else None
            suffix = f": {detail}" if detail else ""
            if response.status_code in {401, 403}:
                raise Failed(f"Tracearr Error: API key was rejected (HTTP {response.status_code}){suffix}")
            raise Failed(f"Tracearr Error: HTTP {response.status_code} on {request_api.removeprefix(self.url)}/{endpoint}{suffix}")
        if not isinstance(payload, dict):
            raise Failed(f"Tracearr Error: Invalid response from {request_api.removeprefix(self.url)}/{endpoint}")
        return payload
