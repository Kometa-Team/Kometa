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
JELLYFIN_LOCKABLE = BROWSER_LOCKABLE - {"OriginalTitle", "CommunityRating", "CriticRating"}
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

    if server_type == "silo" and params.get("split_duplicates"):
        reason = "Silo grouping repair requires explicit file and target selections"
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
    for option in SCALAR_OPERATIONS:
        values = params.get(option)
        if not values:
            continue
        accepted = []
        for source in values:
            if str(source).startswith("plex_"):
                unsupported(f"{option} source {source}", "requires Plex metadata")
            elif server_type in ("jellyfin", "emby") and option == "mass_added_at_update" and source in ("remove", "reset"):
                unsupported("mass_metadata_update.added_at", "clearing the added date is not supported by the native metadata update; use a replacement date")
            elif (server_type == "silo" or option in ("mass_added_at_update", "mass_originally_available_update") or server_type == "jellyfin" and option == "mass_original_title_update") and source in ("lock", "unlock"):
                unsupported(f"{option} source {source}", "these native metadata field locks cannot be represented by this adapter")
            else:
                if (server_type == "silo" or option in ("mass_added_at_update", "mass_originally_available_update") or server_type == "jellyfin" and option == "mass_original_title_update") and source in ("remove", "reset"):
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
    return getattr(item, field, None)


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
        if browser and field == "addedAt" and control in ("remove", "reset", "clear"):
            raise Failed(f"{library.server.type_label} Error: Clearing the added date is not supported")
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
        if browser and key in (JELLYFIN_LOCKABLE if library.server.type_name == "jellyfin" else BROWSER_LOCKABLE):
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
    options = library.metadata_backup
    path = options["path"]
    document = config.Requests.file_yaml(path, create=True)
    records = document.data.setdefault("metadata", {})
    exclude = set(options.get("exclude") or [])
    sync_tags = options.get("sync_tags", False)
    count = 0

    def attributes(item):
        values = {}
        for name, attr in (
            ("title", "title"),
            ("original_title", "originalTitle"),
            ("summary", "summary"),
            ("content_rating", "contentRating"),
            ("studio", "studio"),
            ("originally_available", "originallyAvailableAt"),
            ("critic_rating", "rating"),
            ("audience_rating", "audienceRating"),
            ("user_rating", "userRating"),
        ):
            value = getattr(item, attr, None)
            if name not in exclude and value is not None and value != "":
                values[name] = value.strftime("%Y-%m-%d") if isinstance(value, datetime) else value
        tag_values = {"genre": item.genres}
        if library.server.type_name != "silo":
            tag_values["label"] = item.data.get("Tags") or []
            tag_values["country"] = item.data.get("ProductionLocations") or []
            for role in ("director", "writer", "producer"):
                tag_values[role] = [person["Name"] for person in (item.data.get("People") or []) if person.get("Type", "").lower() == role and person.get("Name")]
        else:
            tag_values["country"] = item.data.get("countries") or []
        for name, tags in tag_values.items():
            if name not in exclude and (tags or sync_tags):
                key = f"{name}.sync" if sync_tags else name
                values[key] = tags[0] if len(tags) == 1 else list(tags)
        return values

    def export(item):
        nonlocal count
        item = library.reload(item)
        count += 1
        logger.ghost(f"Backing up metadata: {item.title}")
        values = attributes(item)
        if item.type == "show":
            children = {}
            for season in item.seasons():
                season_values = export(season)
                if season_values or options.get("add_blank_entries", True):
                    children[season.seasonNumber] = season_values or None
            if children:
                values["seasons"] = children
        elif item.type == "season":
            children = {}
            for episode in item.episodes():
                episode_values = export(episode)
                if episode_values or options.get("add_blank_entries", True):
                    children[episode.episodeNumber] = episode_values or None
            if children:
                values["episodes"] = children
        return values

    used = set()
    try:
        for item in library.get_all():
            values = export(item)
            # Match the normal metadata reader: movie IDs are TMDb, show IDs are TVDb.
            mapping_id = getattr(item, "tmdb_id" if item.type == "movie" else "tvdb_id", None) or getattr(item, "imdb_id", None)
            key = mapping_id or (f"{item.title} ({item.year})" if item.year else item.title)
            match = {"title": item.title}
            if item.year:
                match["year"] = item.year
            if key in used:
                key = f"{item.title} ({item.year}) [{item.ratingKey}]"
                values["match"] = match
            elif not mapping_id and item.year:
                values["match"] = match
            used.add(key)
            if values or options.get("add_blank_entries", True):

                def merge_attributes(existing, updated):
                    for field, value in updated.items():
                        if isinstance(field, str) and field.endswith(".sync"):
                            existing.pop(field[:-5], None)
                        else:
                            existing.pop(f"{field}.sync", None)
                        if isinstance(value, dict) and isinstance(existing.get(field), dict):
                            merge_attributes(existing[field], value)
                        else:
                            existing[field] = value
                    return existing

                existing = records.get(key)
                records[key] = merge_attributes(existing, values) if isinstance(existing, dict) else values or None
    finally:
        logger.exorcise()
    document.save()
    logger.info(f"{count} metadata records backed up to {path}")


def restore_browser_metadata(library, item, metadata, logger):
    """Apply regular backup attributes without relying on PlexAPI item methods."""
    from modules import util

    scalar_fields = {
        "title": "title",
        "original_title": "originalTitle",
        "summary": "summary",
        "studio": "studio",
        "content_rating": "contentRating",
        "originally_available": "originallyAvailableAt",
        "critic_rating": "rating",
        "audience_rating": "audienceRating",
        "user_rating": "userRating",
    }
    tag_fields = {"genre": "Genres", "label": "Tags", "country": "ProductionLocations"}
    people_roles = {"director", "writer", "producer"}
    allowed = set(scalar_fields) | {"match", "mapping_id", "year", "seasons", "episodes"}
    allowed.update(f"{tag}{suffix}" for tag in set(tag_fields) | people_roles for suffix in ("", ".sync", ".remove"))
    metadata = {str(key).lower(): value for key, value in metadata.items()}
    unsupported = set(metadata) - allowed
    if unsupported:
        raise Failed(f"{library.server.type_label} Metadata Error: Unsupported attributes: {', '.join(sorted(unsupported))}")
    fields = {}
    for name, field in scalar_fields.items():
        if name not in metadata:
            continue
        value = metadata[name]
        if name in ("critic_rating", "audience_rating", "user_rating"):
            try:
                value = float(value)
                if not 0 <= value <= 10:
                    raise ValueError
            except (ValueError, TypeError):
                raise Failed(f"Metadata Error: {name} must be a number between 0 and 10")
        elif name == "originally_available":
            value = util.validate_date(value, return_as="%Y-%m-%d")
        elif value is None:
            raise Failed(f"Metadata Error: {name} attribute is blank")
        fields[field] = value
    payload = {}
    people = list(item.data.get("People") or [])
    for name in set(tag_fields) | people_roles:
        present = [key for key in (name, f"{name}.sync", f"{name}.remove") if key in metadata]
        if not present:
            continue
        if f"{name}.sync" in present and len(present) > 1:
            raise Failed(f"Metadata Error: Cannot combine {name}.sync with add/remove attributes")
        before = [person["Name"] for person in people if person.get("Type", "").lower() == name and person.get("Name")] if name in people_roles else list(item.data.get(tag_fields[name]) or [])
        if f"{name}.sync" in metadata:
            after = util.get_list(metadata[f"{name}.sync"], return_none=False)
        else:
            removed = util.get_list(metadata.get(f"{name}.remove"), return_none=False)
            after = [value for value in before if value not in removed] + util.get_list(metadata.get(name), return_none=False)
        after = list(dict.fromkeys(after))
        if name in people_roles:
            retained = [person for person in people if person.get("Type", "").lower() != name or person.get("Name") in after]
            retained.extend({"Name": value, "Type": name.title()} for value in after if value not in before)
            people = retained
            payload["People"] = people
        else:
            payload[tag_fields[name]] = after
    # All attributes are validated before writing any of this item's metadata.
    if fields:
        apply_edit(library, item, fields)
    if payload:
        item.apply(library.client.update_item(item.ratingKey, payload))
    logger.info(f"{item.title} Metadata Update Successful")
    for section, children in (("seasons", item.seasons if item.type == "show" else None), ("episodes", item.episodes if item.type == "season" else None)):
        if section not in metadata:
            continue
        if children is None:
            raise Failed(f"Metadata Error: {section} is not valid for {item.type}")
        indexed = {str(child.seasonNumber if section == "seasons" else child.episodeNumber): child for child in children()}
        for number, values in (metadata[section] or {}).items():
            if str(number) not in indexed:
                raise Failed(f"Metadata Error: {item.title} {section} {number} not found")
            if values:
                child = library.reload(indexed[str(number)])
                restore_browser_metadata(library, child, values, logger)
