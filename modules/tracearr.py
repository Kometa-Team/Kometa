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
]


class Tracearr:
    def __init__(self, requests, library, params):
        self.requests = requests
        self.library = library
        self.url = params["url"].rstrip("/")
        self.apikey = str(params["apikey"]).strip() if params["apikey"] else None
        self.api = f"{self.url}/api/v1/public"
        logger.secret(self.url)
        logger.secret(self.apikey)
        if not self.apikey:
            raise Failed("Tracearr Error: API key is required")
        if not self.apikey.startswith("trr_pub_"):
            raise Failed("Tracearr Error: API key must begin with 'trr_pub_'")
        health = self._request("health")
        self.server_id = self._resolve_server_id(health, params.get("server_id"))

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
        pretty = "History" if list_type == "history" else list_type.capitalize()
        media_label = "Items" if is_playlist else "Movies" if self.library.is_movie else "Shows"
        logger.info(f"Processing Tracearr {pretty}: {data['list_size']} {media_label}")

        cutoff = datetime.now(timezone.utc) - timedelta(days=int(data["list_days"]))
        params = {
            "page": 1,
            "pageSize": 100,
            "startDate": cutoff.date().isoformat(),
            "endDate": datetime.now(timezone.utc).date().isoformat(),
            "serverId": self.server_id,
        }
        if is_playlist and list_type == "binged":
            params["mediaType"] = "episode"
        elif not is_playlist and self.library.is_movie:
            params["mediaType"] = "movie"
        elif not is_playlist and self.library.is_show:
            params["mediaType"] = "episode"

        items = self._fetch_history(params)
        aggregated = self._aggregate_history(items, list_type, int(data["list_minimum"]))
        rating_keys = []
        seen = set()
        search_libraries = libraries if libraries else [self.library]
        for item in aggregated:
            if len(rating_keys) >= int(data["list_size"]):
                break
            media_type = item["media_type"]
            title = item["title"]
            year = item["year"]
            dedupe_key = (media_type, title, year)
            if dedupe_key in seen:
                continue
            libtype = "movie" if media_type == "movie" else "show"
            matched = False
            for search_library in search_libraries:
                if (media_type == "movie" and not search_library.is_movie) or (media_type == "show" and not search_library.is_show):
                    continue
                new_item = search_library.exact_search(title, libtype=libtype, year=year if media_type == "movie" else None)
                if not new_item:
                    continue
                if is_playlist:
                    item_id = self._playlist_item_id(search_library, new_item[0], media_type)
                    if item_id:
                        rating_keys.append(item_id)
                    else:
                        logger.error(Failed(f"Tracearr Error: No supported external ID found for {title}"))
                        continue
                else:
                    rating_keys.append((new_item[0].ratingKey, "ratingKey"))
                seen.add(dedupe_key)
                matched = True
                break
            if not matched:
                display_year = f" ({year})" if year else ""
                logger.error(Failed(f"Tracearr Error: {title}{display_year} not found in Plex"))

        return rating_keys

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
        items = []
        request_params = dict(params)
        while True:
            response = self._request("history", params=request_params)
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

    def _aggregate_history(self, items, list_type, minimum):
        grouped = defaultdict(
            lambda: {
                "media_type": None,
                "title": None,
                "year": None,
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
            }
        )

        for item in items:
            if item.get("serverId") and item["serverId"] != self.server_id:
                continue

            source_media_type = str(item.get("mediaType") or "").lower()
            if source_media_type not in {"movie", "episode"}:
                continue
            media_type = "movie" if source_media_type == "movie" else "show"
            title = item.get("mediaTitle") if media_type == "movie" else item.get("showTitle")
            if not title:
                continue
            year = item.get("year") if media_type == "movie" else None
            key = (media_type, title, year)
            entry = grouped[key]
            entry["media_type"] = media_type
            entry["title"] = title
            entry["year"] = year
            entry["total_sessions"] += 1
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
                season_number = item.get("seasonNumber")
                episode_number = item.get("episodeNumber")
                episode_key = (season_number, episode_number) if season_number is not None or episode_number is not None else item.get("mediaTitle")
                if episode_key:
                    entry["watched_episodes_by_user"][str(user_id)].add(episode_key)
            if item.get("isTranscode") is True or str(item.get("videoDecision") or "").lower() == "transcode" or str(item.get("audioDecision") or "").lower() == "transcode":
                entry["transcoded_sessions"] += 1
            ts = item.get("stoppedAt") or item.get("startedAt")
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
            count_value = {
                "popular": len(entry["unique_users"]),
                "watched": entry["completed_sessions"],
                "trending": entry["total_sessions"],
                "rewatched": entry["repeat_plays"],
                "completed": entry["completed_sessions"],
                "binged": entry["binged_episodes"],
                "transcoded": entry["transcoded_sessions"],
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

    def _request(self, endpoint, params=None):
        logger.trace(f"Tracearr CMD: {endpoint}")
        if params:
            logger.trace(f"Tracearr Params: {params}")
        try:
            response = self.requests.get(f"{self.api}/{endpoint}", params=params, headers=self._headers())
        except Exception as e:
            raise Failed(f"Tracearr Error: Unable to connect to {self.url}: {e}") from e
        try:
            payload = response.json()
        except ValueError as e:
            raise Failed(f"Tracearr Error: Non-JSON response from /api/v1/public/{endpoint} (HTTP {response.status_code})") from e
        if response.status_code >= 400:
            detail = (payload.get("message") or payload.get("error")) if isinstance(payload, dict) else None
            suffix = f": {detail}" if detail else ""
            if response.status_code in {401, 403}:
                raise Failed(f"Tracearr Error: API key was rejected (HTTP {response.status_code}){suffix}")
            raise Failed(f"Tracearr Error: HTTP {response.status_code} on /api/v1/public/{endpoint}{suffix}")
        if not isinstance(payload, dict):
            raise Failed(f"Tracearr Error: Invalid response from /api/v1/public/{endpoint}")
        return payload
