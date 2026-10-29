"""Native metadata writes and operation compatibility for Silo and MediaBrowser."""

from datetime import datetime
from types import SimpleNamespace

from modules.util import Failed

SILO_FIELDS = {"title": "title", "originalTitle": "original_title", "summary": "overview", "genre": "genres", "studio": "studios", "contentRating": "content_rating", "originallyAvailableAt": "release_date"}
BROWSER_FIELDS = {
    "title": "Name",
    "originalTitle": "OriginalTitle",
    "summary": "Overview",
    "genre": "Genres",
    "studio": "Studios",
    "contentRating": "OfficialRating",
    "originallyAvailableAt": "PremiereDate",
    "addedAt": "DateCreated",
    "audienceRating": "CommunityRating",
    "rating": "CriticRating",
    "label": "Tags",
}
BROWSER_LOCKABLE = {"Name", "OriginalTitle", "Overview", "Genres", "Studios", "OfficialRating", "CommunityRating", "CriticRating", "Tags"}
IMAGE_OPERATIONS = ("mass_poster_update", "mass_background_update", "mass_logo_update", "mass_square_art_update")
SCALAR_OPERATIONS = ("mass_genre_update", "mass_content_rating_update", "mass_original_title_update", "mass_studio_update", "mass_originally_available_update", "mass_added_at_update")


def is_native(library):
    return getattr(getattr(library, "server", None), "type_name", None) in ("silo", "jellyfin", "emby")


def configure_metadata_operations(params, server_type, logger):
    if server_type == "plex":
        return

    def unsupported(option, reason):
        for internal, public in (("mass_added_at_update", "mass_metadata_update.added_at"), ("mass_imdb_parental_labels", "mass_metadata_update.labels"), ("mass_square_art_update", "mass_metadata_update.square_art")):
            option = option.replace(internal, public, 1)
        logger.error(f"Config Error: {option} is not supported by {server_type}: {reason}")

    if params.get("split_duplicates"):
        reason = "Silo grouping repair requires explicit file and target selections" if server_type == "silo" else "this adapter does not implement native version splitting"
        unsupported("split_duplicates", reason)
        params["split_duplicates"] = False
    if params.get("mass_collection_mode"):
        unsupported("mass_metadata_update.collections.mode", "Plex collection visibility modes have no native equivalent")
        params["mass_collection_mode"] = None
    if server_type == "silo":
        for option in ("mass_added_at_update", "mass_imdb_parental_labels"):
            if params.get(option):
                unsupported(option, "the Silo metadata API has no writable added date" if option == "mass_added_at_update" else "Silo has no item labels")
                params[option] = None
    if params.get("metadata_backup") and params["metadata_backup"].get("sync_tags"):
        unsupported("mass_metadata_update.backup.sync_tags", "native backups store complete tag values rather than Plex tag-sync instructions")
    for option in SCALAR_OPERATIONS:
        values = params.get(option)
        if not values:
            continue
        accepted = []
        for source in values:
            if str(source).startswith("plex_"):
                unsupported(f"{option} source {source}", "requires Plex metadata")
            elif (server_type == "silo" or option in ("mass_added_at_update", "mass_originally_available_update")) and source in ("lock", "unlock"):
                unsupported(f"{option} source {source}", "these native metadata field locks cannot be represented by this adapter")
            else:
                if (server_type == "silo" or option in ("mass_added_at_update", "mass_originally_available_update")) and source in ("remove", "reset"):
                    unsupported(f"{option} {source} lock change", "the value will be cleared, but existing native locks are preserved")
                accepted.append(source)
        params[option] = accepted or None
    for option in IMAGE_OPERATIONS:
        value = params.get(option)
        if not value:
            continue
        if server_type == "silo" and option == "mass_square_art_update":
            unsupported(option, "Silo has no square artwork slot")
            params[option] = None
            continue
        sources = value.get("sources") or [value.get("source")]
        accepted = []
        for source in sources:
            if source in ("plex", "lock", "unlock", "ytmusic"):
                unsupported(f"{option} source {source}", "this provider or per-image lock control is not supported by the native adapter")
            else:
                accepted.append(source)
        if server_type == "silo" and value.get("ignore_locked"):
            unsupported(f"{option}.ignore_locked", "Silo image lock identifiers are not available; skipping this image operation")
            accepted = []
        if accepted:
            params[option] = {**value, "source": accepted[0], "sources": accepted}
        else:
            params[option] = None
    for option in ("mass_user_rating_update", "mass_episode_user_rating_update"):
        if server_type != "silo" and params.get(option):
            values = []
            for source in params[option]:
                if source in ("lock", "unlock", "remove", "reset"):
                    unsupported(f"{option} source {source}", "profile ratings do not have metadata field locks; use clear to remove a rating")
                else:
                    values.append(source)
            params[option] = values or None


def current_value(item, field):
    value = getattr(item, field, None)
    if field == "rating" and item.library.server.type_name in ("jellyfin", "emby") and value is not None:
        return float(value) / 10
    return value


def apply_edit(library, item, fields=None, tags=None, control=None):
    fields = dict(fields or {})
    browser = library.server.type_name != "silo"
    mapping = BROWSER_FIELDS if browser else SILO_FIELDS
    payload = {}
    locks = list(item.data.get("LockedFields") or [])
    if tags:
        for field, (add, remove) in tags.items():
            key = mapping.get(field)
            if not key:
                raise Failed(f"{library.server.type_label} Error: Metadata field {field} is not supported")
            before = item.tags if field == "label" else item.genres
            names = [getattr(value, "tag", value) for value in before]
            fields[field] = list(dict.fromkeys([value for value in names if value not in remove] + list(add)))
    user = fields.pop("userRating", ...) if not control else ...
    if control and "userRating" in fields:
        if control != "clear":
            raise Failed(f"{library.server.type_label} Error: Profile rating locks are not supported")
        fields.pop("userRating")
        user = None
    for field, value in fields.items():
        key = mapping.get(field)
        if not browser and field == "originallyAvailableAt":
            key = "first_air_date" if item.type == "show" else "air_date" if item.type in ("season", "episode") else key
        if not key:
            raise Failed(f"{library.server.type_label} Error: Metadata field {field} is not supported")
        if control in ("remove", "reset", "clear"):
            value = [] if field in ("genre", "studio", "label") else None
        if not control or control in ("remove", "reset", "clear"):
            if field == "studio" and value is not None:
                value = value if isinstance(value, list) else [value]
                if browser:
                    value = [{"Name": name} for name in value]
            if browser and field in ("rating", "audienceRating") and value is not None:
                value = float(value) * (10 if field == "rating" else 1)
            if field in ("originallyAvailableAt", "addedAt") and value is not None:
                value = value.strftime("%Y-%m-%d") if isinstance(value, datetime) else str(value)[:10]
                if browser:
                    value += "T00:00:00Z"
            payload[key] = value
        if browser and key in BROWSER_LOCKABLE:
            if control in ("unlock", "reset"):
                locks = [name for name in locks if name != key]
            elif control != "clear" and key not in locks:
                locks.append(key)
    if browser:
        if fields and locks != list(item.data.get("LockedFields") or []):
            payload["LockedFields"] = locks
        if payload:
            item.apply(library.client.update_item(item.ratingKey, payload))
        if user is not ...:
            result = library.client.update_user_data(item.ratingKey, {"Rating": None if user is None else float(user)})
            item.data["UserData"] = result
            item.apply({})
    else:
        if user is not ...:
            raise Failed("Silo Error: Use the explicit native profile rating operation")
        if payload:
            result = library.client.update_metadata(item.content_id, payload)
            item.apply({**payload, **result} if isinstance(result, dict) else payload)
    if "_search_details" in library.__dict__:
        library._search_details[item.ratingKey] = item
    library.__dict__.get("_native_rating_details", {}).pop(item.ratingKey, None)
    return payload


def date_value(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


class NativeItemMetadata:
    @property
    def fields(self):
        if self.library.server.type_name == "silo":
            return []
        reverse = {value: key for key, value in BROWSER_FIELDS.items()}
        locked = self.data.get("LockedFields") or []
        result = [SimpleNamespace(name=reverse[name], locked=True) for name in locked if name in reverse]
        if self.data.get("LockData") is True:
            result.extend(SimpleNamespace(name=name, locked=True) for name in BROWSER_FIELDS)
        if "Images" in locked or self.data.get("LockData") is True:
            result.extend(SimpleNamespace(name=name, locked=True) for name in ("thumb", "art", "clearLogo", "squareArt"))
        return result

    @property
    def originalTitle(self):
        return self.data.get("original_title" if self.library.server.type_name == "silo" else "OriginalTitle")

    @property
    def studio(self):
        return next(iter(self.studios), None)

    @property
    def originallyAvailableAt(self):
        return date_value(
            (self.data.get("first_air_date") if self.type == "show" else self.data.get("air_date") if self.type in ("season", "episode") else self.data.get("release_date")) if self.library.server.type_name == "silo" else self.data.get("PremiereDate")
        )

    @property
    def addedAt(self):
        return date_value(self.data.get("added_at" if self.library.server.type_name == "silo" else "DateCreated"))

    @property
    def seasonNumber(self):
        return int((self.data.get("season_number", 0) if self.library.server.type_name == "silo" else self.data.get("IndexNumber" if self.type == "season" else "ParentIndexNumber", 0)) or 0)

    @property
    def episodeNumber(self):
        return int((self.data.get("episode_number", 0) if self.library.server.type_name == "silo" else self.data.get("IndexNumber", 0)) or 0)

    @property
    def seasonEpisode(self):
        return f"s{self.seasonNumber:02}e{self.episodeNumber:02}"

    @property
    def parentTitle(self):
        return self.data.get("series_title") or self.data.get("SeriesName") or self.title

    grandparentTitle = parentTitle

    def editOriginalTitle(self, value):
        return apply_edit(self.library, self, {"originalTitle": value})

    def show(self):
        identity = self.data.get("series_id") or self.data.get("SeriesId")
        if not identity:
            raise Failed(f"{self.library.server.type_label} Error: Parent series ID is missing for {self.title}")
        return self.library.fetch_item(identity)


def backup_metadata(config, library, logger):
    path = library.metadata_backup["path"]
    document = config.Requests.file_yaml(path, create=True)
    section = document.data.setdefault("native_metadata", {})
    identity = f"{library.server.display_name}/{library.name}"
    records = section.setdefault(identity, {"server_type": library.server.type_name, "items": {}})["items"]
    exclude = set(library.metadata_backup.get("exclude") or [])
    mapping = SILO_FIELDS if library.server.type_name == "silo" else BROWSER_FIELDS
    metadata_fields = set(mapping.values()) | (
        {"locked_fields", "air_date", "first_air_date", "last_air_date", "year", "countries", "networks", "imdb_id", "tmdb_id", "tvdb_id", "rating_imdb", "rating_tmdb", "rating_rt_critic", "rating_rt_audience", "user_rating"}
        if library.server.type_name == "silo"
        else {"LockedFields", "LockData", "ProductionYear", "ProductionLocations", "ProviderIds", "People"}
    )
    aliases = {
        "original_title": "originalTitle",
        "content_rating": "contentRating",
        "originally_available": "originallyAvailableAt",
        "added_at": "addedAt",
        "critic_rating": "rating",
        "audience_rating": "audienceRating",
        "genres": "genre",
        "labels": "label",
        "studios": "studio",
    }
    exclude.update(aliases[name] for name in list(exclude) if name in aliases)
    excluded_fields = {name.casefold() for name in exclude}
    excluded_fields.update(value.casefold() for name, value in mapping.items() if name.casefold() in excluded_fields)
    if "originallyavailableat" in excluded_fields:
        excluded_fields.update(("air_date", "first_air_date", "release_date"))
    items = list(library.get_all())
    seen = set()
    for index, item in enumerate(items, 1):
        if item.ratingKey in seen:
            continue
        seen.add(item.ratingKey)
        logger.ghost(f"Backing up native metadata: {index}/{len(items)} {item.title}")
        item = library.reload(item)
        fields = {key: value for key, value in item.data.items() if key in metadata_fields and key.casefold() not in excluded_fields}
        if library.server.type_name != "silo" and not ({"user_rating", "userrating"} & excluded_fields):
            if "Rating" in (item.data.get("UserData") or {}):
                fields["UserRating"] = item.data["UserData"]["Rating"]
        if fields or library.metadata_backup.get("add_blank_entries", True):
            records[str(item.ratingKey)] = {"title": item.title, "type": item.type, "fields": fields}
        if item.type == "show":
            items.extend(item.seasons())
        elif item.type == "season":
            items.extend(item.episodes())
    logger.exorcise()
    document.save()
    logger.info(f"{len(items)} native metadata records backed up to {path}")
