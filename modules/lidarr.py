import re
from datetime import datetime
from typing import Any, cast

from modules import timings, util
from modules.util import Failed

logger = util.logger

apply_tags_translation = {"": "add", "sync": "replace", "remove": "remove"}
builders = ["lidarr_all", "lidarr_taglist"]
monitor_options = ["all", "future", "missing", "existing", "first", "latest", "none"]
monitor_new_albums_options = ["all", "none", "new"]
monitor_descriptions = {
    "all": "All Albums",
    "future": "Future Albums",
    "missing": "Missing Albums",
    "existing": "Existing Albums",
    "first": "First Album",
    "latest": "Latest Album",
    "none": "None",
}
monitor_new_albums_descriptions = {"all": "All Albums", "none": "No New Albums", "new": "New Albums"}
mbid_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)
JsonObject = dict[str, Any]


class Lidarr:

    def __init__(self, requests, cache, library, params):
        self.requests = requests
        self.cache = cache
        self.library = library
        self.url = params["url"].rstrip("/")
        self.token = params["token"]
        self.headers = {"X-Api-Key": self.token}
        logger.secret(self.url)
        logger.secret(self.token)
        timings.registry.register_arr_host(self.url, "lidarr")

        self.add_missing = params["add_missing"]
        self.add_existing = params["add_existing"]
        self.upgrade_existing = params["upgrade_existing"]
        self.monitor_existing = params["monitor_existing"]
        self.root_folder_path = params["root_folder_path"]
        self.monitor = params["monitor"]
        self.monitor_new_albums = params["monitor_new_albums"]
        self.quality_profile = params["quality_profile"]
        self.tag = params["tag"]
        self.search = params["search"]
        self.lidarr_path = params["lidarr_path"] if params["lidarr_path"] and params["plex_path"] else ""
        self.plex_path = params["plex_path"] if params["lidarr_path"] and params["plex_path"] else ""
        self.ignore_cache = params["ignore_cache"]
        self._artist_names = None

        try:
            self._get_object("/system/status")
            self.profiles = self._get_list("/qualityprofile")
            self.metadata_profiles = self._get_list("/metadataprofile")
            self._validate_root_folder()
            self.quality_profile_id = self._quality_profile_id(self.quality_profile)
            self.metadata_profile_id = self.metadata_profiles[0]["id"]
        except Failed:
            raise
        except Exception as e:
            raise Failed(f"Lidarr Error: {e}") from e

    def _request(self, method, path, **kwargs) -> Any:
        try:
            response = self.requests.session.request(method, f"{self.url}/api/v1{path}", headers=self.headers, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except Exception as e:
            raise Failed(f"Lidarr Error: {e}") from e

    def _get(self, path, params=None) -> Any:
        return self._request("GET", path, params=params)

    def _get_object(self, path, params=None) -> JsonObject:
        data = self._get(path, params=params)
        if not isinstance(data, dict):
            raise Failed(f"Lidarr Error: Expected an object from {path}")
        return cast(JsonObject, data)

    def _get_list(self, path, params=None) -> list[JsonObject]:
        data = self._get(path, params=params)
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise Failed(f"Lidarr Error: Expected a list of objects from {path}")
        return cast(list[JsonObject], data)

    def _post(self, path, data) -> Any:
        return self._request("POST", path, json=data)

    def _put(self, path, data) -> Any:
        return self._request("PUT", path, json=data)

    def _delete(self, path, data=None) -> Any:
        return self._request("DELETE", path, json=data)

    def _validate_root_folder(self):
        folders = self._get_list("/rootfolder")
        if not any(folder["path"] == self.root_folder_path for folder in folders):
            raise Failed(f"Lidarr Error: Invalid Root Folder: {self.root_folder_path}")

    def _quality_profile_id(self, profile):
        for quality_profile in self.profiles:
            if quality_profile["id"] == profile or quality_profile["name"].casefold() == str(profile).casefold():
                return quality_profile["id"]
        names = [quality_profile["name"] for quality_profile in self.profiles]
        raise Failed(f"Lidarr Error: Invalid Quality Profile: {profile}. Options: {names}")

    def _tag_ids(self, tags, create=True):
        current_tags = self._get_list("/tag")
        labels = {tag["label"].lower(): tag["id"] for tag in current_tags}
        tag_ids = []
        for tag in tags or []:
            label = str(tag).lower()
            if label not in labels and create:
                response = self._post("/tag", {"label": label})
                if not isinstance(response, dict) or "id" not in response:
                    raise Failed("Lidarr Error: Expected a tag object when creating a tag")
                labels[label] = response["id"]
            if label in labels:
                tag_ids.append(labels[label])
        return tag_ids

    @staticmethod
    def valid_mbid(mbid):
        return bool(mbid and mbid_pattern.fullmatch(mbid))

    def all_artists(self) -> list[JsonObject]:
        return self._get_list("/artist")

    def get_artist_name(self, mbid):
        if self._artist_names is None:
            self._artist_names = {artist.get("foreignArtistId"): artist.get("artistName") for artist in self.all_artists()}
        return self._artist_names.get(mbid, "Unknown Artist")

    def _set_album_monitoring(self, artist_id, monitor):
        albums = self._get_list("/album", params={"artistId": artist_id})
        if monitor == "none":
            album_ids = [album["id"] for album in albums]
            monitored = False
        elif monitor == "all":
            album_ids = [album["id"] for album in albums]
            monitored = True
        elif monitor == "future":
            album_ids = [album["id"] for album in albums if album.get("releaseDate", "9999") > datetime.now().strftime("%Y-%m-%d")]
            monitored = True
        elif monitor == "missing":
            album_ids = [album["id"] for album in albums if album.get("statistics", {}).get("trackFileCount", 0) == 0]
            monitored = True
        elif monitor == "existing":
            album_ids = [album["id"] for album in albums if album.get("statistics", {}).get("trackFileCount", 0) > 0]
            monitored = True
        else:
            dated = sorted((album for album in albums if album.get("releaseDate")), key=lambda album: album["releaseDate"])
            album_ids = [dated[0 if monitor == "first" else -1]["id"]] if dated else []
            monitored = True
        all_album_ids = [album["id"] for album in albums]
        if monitor not in ["all", "none"] and all_album_ids:
            self._put("/album/monitor", {"albumIds": all_album_ids, "monitored": False})
        if album_ids:
            self._put("/album/monitor", {"albumIds": album_ids, "monitored": monitored})

    def add_artists(self, artist_mbids, **options):
        """Add or update artists identified by MusicBrainz artist IDs only."""
        root_folder_path = options.get("folder", self.root_folder_path)
        quality_profile_id = self._quality_profile_id(options.get("quality", self.quality_profile))
        monitored = options.get("monitor", self.monitor)
        monitor_new_albums = options.get("monitor_new_albums", self.monitor_new_albums)
        tags = self._tag_ids(options.get("tag", self.tag))
        search = options.get("search", self.search)
        upgrade_existing = options.get("upgrade_existing", self.upgrade_existing)
        monitor_existing = options.get("monitor_existing", self.monitor_existing)
        existing = {artist.get("foreignArtistId"): artist for artist in self.all_artists()}
        added = []

        for artist_data in artist_mbids:
            mbid, plex_artist_name = artist_data if isinstance(artist_data, tuple) else (artist_data, None)
            if not self.valid_mbid(mbid):
                logger.warning(f"Lidarr Warning: Invalid MusicBrainz Artist ID: {mbid}")
                continue
            if self.cache and not self.ignore_cache and self.cache.query_lidarr_adds(mbid, self.library.original_mapping_name):
                artist_name = existing.get(mbid, {}).get("artistName") or plex_artist_name or "Unknown Artist"
                logger.info(f"Skipped In Change | {artist_name} (MBID: {mbid})")
                continue
            if mbid in existing:
                artist = existing[mbid]
                changes = {}
                if upgrade_existing and artist.get("qualityProfileId") != quality_profile_id:
                    changes["qualityProfileId"] = quality_profile_id
                if monitor_existing and artist.get("monitored") != (monitored != "none"):
                    changes["monitored"] = monitored != "none"
                if monitor_existing and artist.get("monitorNewItems") != monitor_new_albums:
                    changes["monitorNewItems"] = monitor_new_albums
                if changes:
                    artist.update(changes)
                    self._put(f"/artist/{artist['id']}", artist)
                if monitor_existing:
                    self._set_album_monitoring(artist["id"], monitored)
                    logger.info(f"Updated in Lidarr | {artist['artistName']}")
                else:
                    logger.info(f"Already in Lidarr | {artist['artistName']}")
                if self.cache:
                    self.cache.update_lidarr_adds(mbid, self.library.original_mapping_name)
                continue

            lookup = self._get_list("/artist/lookup", params={"term": f"lidarr:{mbid}"})
            if not lookup:
                logger.warning(f"Lidarr Warning: MusicBrainz Artist ID not found: {mbid}")
                continue
            artist = lookup[0]
            artist.update(
                {
                    "qualityProfileId": quality_profile_id,
                    "metadataProfileId": artist.get("metadataProfileId") or self.metadata_profile_id,
                    "rootFolderPath": root_folder_path,
                    "monitored": monitored != "none",
                    "monitorNewItems": monitor_new_albums,
                    "tags": tags,
                    "addOptions": {"monitor": monitored, "searchForMissingAlbums": search},
                }
            )
            self._post("/artist", artist)
            added.append(mbid)
            if self.cache:
                self.cache.update_lidarr_adds(mbid, self.library.original_mapping_name)
            logger.info(f"Added to Lidarr | {artist['artistName']}")
        return added

    def edit_tags(self, artist_mbids, tags, apply_tags):
        tag_ids = self._tag_ids(tags)
        artist_lookup = {artist.get("foreignArtistId"): artist for artist in self.all_artists()}
        for mbid in artist_mbids:
            artist = artist_lookup.get(mbid)
            if not artist:
                logger.warning(f"MusicBrainz Artist ID Not in Lidarr | {mbid}")
                continue
            existing_tags = artist.get("tags", [])
            if apply_tags_translation[apply_tags] == "add":
                artist["tags"] = list(dict.fromkeys([*existing_tags, *tag_ids]))
            elif apply_tags_translation[apply_tags] == "remove":
                artist["tags"] = [tag for tag in existing_tags if tag not in tag_ids]
            else:
                artist["tags"] = tag_ids
            self._put(f"/artist/{artist['id']}", artist)

    def remove_all_with_tags(self, tags):
        wanted_tags = set(self._tag_ids(tags, create=False))
        for artist in self.all_artists():
            if wanted_tags and wanted_tags.issubset(set(artist.get("tags", []))):
                self._delete(f"/artist/{artist['id']}", {"deleteFiles": False, "addImportListExclusion": False})
                logger.info(f"Removed from Lidarr | {artist['artistName']}")

    def get_mbid_ids(self, method, data):
        allowed = {tag["id"] for tag in self._get_list("/tag") if tag["label"].lower() in data} if method == "lidarr_taglist" else set()
        ids = []
        artists = self.all_artists()
        self._artist_names = {artist.get("foreignArtistId"): artist.get("artistName") for artist in artists}
        for artist in artists:
            if method == "lidarr_all" or (method == "lidarr_taglist" and ((not data and not artist.get("tags")) or (data and allowed.issubset(set(artist.get("tags", [])))))):
                mbid = artist.get("foreignArtistId")
                if self.valid_mbid(mbid):
                    ids.append((mbid, "mbid"))
        return ids
