from datetime import date, timedelta

from plexapi.audio import Album, Artist, Track
from plexapi.exceptions import BadRequest
from plexapi.video import Movie, Show

from modules import util
from modules.util import Failed

logger = util.logger

builder_types = {"tautulli_popular": "popular", "tautulli_top": "top", "tautulli_watched": "top"}
builders = list(builder_types)
music_builders = builders


class Tautulli:
    def __init__(self, requests, library, params):
        self.requests = requests
        self.library = library
        self.url = params["url"]
        self.apikey = params["apikey"]
        self.api = f"{self.url}/api/v2"
        logger.secret(self.url)
        logger.secret(self.apikey)
        try:
            response = self._request("get_tautulli_info")
        except Exception:
            logger.stacktrace()
            raise Failed("Tautulli Error: Invalid URL")
        if response["response"]["result"] != "success":
            raise Failed(f"Tautulli Error: {response['response']['message']}")
        self.has_section = True if int(response["response"]["data"]["tautulli_version"].split(".")[1]) > 11 else False
        self.section_id = self.library.Plex.key

    def get_rating_keys(self, data, all_items):
        is_music = self.library.is_music
        list_type = data["list_type"]
        builder_level = data.get("builder_level", "artist") if is_music else None
        if is_music and builder_level == "track":
            return self._get_music_tracks(data, all_items)

        if is_music:
            item_type = Artist if builder_level == "artist" else Album
            item_label = "Artist" if builder_level == "artist" else "Album"
        else:
            item_type = Show if self.library.is_show else Movie
            item_label = "Shows" if self.library.is_show else "Movies"
        stat_id = f"{list_type}_{'music' if is_music else 'tv' if self.library.is_show else 'movies'}"
        logger.info(f"Processing Tautulli Most {data['list_type'].capitalize()}: {data['list_size']} {item_label}")
        item_count = int(data["list_size"])
        aggregation_multiplier = 10 if is_music else 1
        params = {"time_range": data["list_days"], "stats_count": item_count * aggregation_multiplier + int(data["list_buffer"])}
        if self.has_section and not all_items:
            params["section_id"] = self.section_id
        response = self._request("get_home_stats", params=params)
        stat_type = "users_watched" if data["list_type"] == "popular" else "total_plays"

        items = None
        for entry in response["response"]["data"]:
            if entry["stat_id"] == stat_id:
                items = entry["rows"]
                break
        if not items:
            item_label = "Artists" if is_music and builder_level == "artist" else "Albums" if is_music else item_label
            raise Failed(f"Tautulli Error: No {item_label} found")

        rating_keys = []
        music_counts = {}
        for item in items:
            if is_music:
                if item.get("media_type") != "track" or not (all_items or int(item["section_id"]) == int(self.section_id)):
                    continue
                try:
                    if builder_level == "artist":
                        target_key = item.get("grandparent_rating_key")
                    else:
                        target_key = self._music_album_key(item)
                    if target_key:
                        target_key = int(target_key)
                        music_counts[target_key] = music_counts.get(target_key, 0) + int(item.get(stat_type) or 0)
                except (BadRequest, Failed, TypeError, ValueError) as e:
                    logger.debug(f"Tautulli music item skipped: {e}")
            elif (all_items or item["section_id"] == self.section_id) and len(rating_keys) < item_count:
                if int(item[stat_type]) < data["list_minimum"]:
                    continue
                try:
                    plex_item = self.library.fetch_item(int(item["rating_key"]))
                    if not isinstance(plex_item, item_type):
                        raise BadRequest
                    rating_keys.append((item["rating_key"], "ratingKey"))
                except (BadRequest, Failed, TypeError, ValueError) as e:
                    logger.error(f"Tautulli item skipped: {e}")
        if is_music:
            for target_key, count in sorted(music_counts.items(), key=lambda entry: entry[1], reverse=True):
                if count < data["list_minimum"]:
                    continue
                try:
                    plex_item = self.library.fetch_item(int(target_key))
                    if isinstance(plex_item, item_type):
                        rating_keys.append((str(target_key), "ratingKey"))
                    else:
                        logger.debug(f"Tautulli music item skipped: Plex item {target_key} is not a {item_label}")
                except (BadRequest, Failed) as e:
                    logger.debug(f"Tautulli music item skipped: {e}")
                if len(rating_keys) >= item_count:
                    break
        return rating_keys

    def _music_album_key(self, item):
        track = self.library.fetch_item(int(item["rating_key"]))
        return track.parentRatingKey if isinstance(track, Track) else None

    def _get_music_tracks(self, data, all_items):
        logger.info(f"Processing Tautulli Most {data['list_type'].capitalize()}: {data['list_size']} Tracks")
        after = (date.today() - timedelta(days=int(data["list_days"]))).isoformat()
        params = {
            "after": after,
            "media_type": "track",
            "grouping": 0,
            "order_column": "date",
            "order_dir": "desc",
            "start": 0,
            "length": 1000,
        }
        if not all_items:
            params["section_id"] = self.section_id

        play_counts = {}
        users_by_track = {}
        start = 0
        while True:
            params["start"] = start
            response = self._request("get_history", params=params)
            history = response["response"]["data"]
            rows = history.get("data", [])
            for item in rows:
                rating_key = item.get("rating_key")
                if not rating_key:
                    continue
                key = str(rating_key)
                if data["list_type"] == "popular":
                    user_id = item.get("user_id") or item.get("user")
                    if user_id:
                        users_by_track.setdefault(key, set()).add(str(user_id))
                else:
                    play_counts[key] = play_counts.get(key, 0) + int(item.get("group_count") or 1)

            start += len(rows)
            total = int(history.get("recordsFiltered", 0))
            if not rows or start >= total:
                break

        counts = {key: len(users) for key, users in users_by_track.items()} if data["list_type"] == "popular" else play_counts
        rating_keys = []
        for rating_key, count in sorted(counts.items(), key=lambda entry: entry[1], reverse=True):
            if count < data["list_minimum"]:
                continue
            try:
                plex_item = self.library.fetch_item(int(rating_key))
                if isinstance(plex_item, Track):
                    rating_keys.append((rating_key, "ratingKey"))
                else:
                    logger.debug(f"Tautulli music item skipped: Plex item {rating_key} is not a Track")
            except (BadRequest, Failed, TypeError, ValueError) as e:
                logger.debug(f"Tautulli music item skipped: {e}")
            if len(rating_keys) >= int(data["list_size"]):
                break
        return rating_keys

    def _request(self, cmd, params=None):
        logger.trace(f"Tautulli CMD: {cmd}")
        if params:
            logger.trace(f"Tautulli Params: {params}")
        final_params = {"apikey": self.apikey, "cmd": cmd}
        if params:
            for k, v in params.items():
                final_params[k] = v
        return self.requests.get_json(self.api, params=final_params)
