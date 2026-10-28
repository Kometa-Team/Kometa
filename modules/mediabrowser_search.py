"""Typed selectors backed by Jellyfin/Emby item, source and stream metadata."""

import math
from datetime import datetime, timezone

from modules.local_search import compile_selector as compile_local_selector
from modules.local_search import values as common_values
from modules.util import Failed

TEXT_FIELDS = {"summary": "Overview", "original_title": "OriginalTitle", "sort_title": "SortName", "tagline": "Taglines", "show_title": "SeriesName", "album_title": "Album", "type": "Type", "status": "Status", "show_status": "Status"}
TAG_FIELDS = {"label": "Tags", "artist": "Artists", "album_artist": "AlbumArtists"}
DATE_FIELDS = {"last_played": "LastPlayedDate", "ended": "EndDate", "updated": "DateLastSaved"}
NUMBER_FIELDS = {
    "year",
    "decade",
    "duration",
    "runtime",
    "duration_seconds",
    "versions",
    "width",
    "height",
    "aspect",
    "channels",
    "bitrate",
    "file_size",
    "video_bitrate",
    "audio_bitrate",
    "video_bit_depth",
    "audio_bit_depth",
    "audio_sample_rate",
    "frame_rate",
    "reference_frames",
    "dovi_profile",
    "dovi_level",
    "audience_rating",
    "critic_rating",
    "user_rating",
    "plays",
    "progress_ratio",
    "position_seconds",
    "seasons",
    "episodes",
    "season_number",
    "episode_number",
}
BOOLEAN_FIELDS = {"duplicate", "hdr", "has_dolby_vision", "hdr10plus", "interlaced", "atmos", "has_edition", "watched", "unwatched", "unplayed", "progress", "is_favorite", "is_in_progress", "unmatched", "has_subtitles", "is_3d", "is_missing", "is_locked"}
TRACK_FIELDS = {
    "video_codec": ("Video", "Codec"),
    "video_profile": ("Video", "Profile"),
    "video_range": ("Video", "VideoRangeType"),
    "audio_codec": ("Audio", "Codec"),
    "audio_profile": ("Audio", "Profile"),
    "audio_track_title": ("Audio", "Title"),
    "subtitle_track_title": ("Subtitle", "Title"),
}
FIELD_TYPES = {
    **dict.fromkeys(TEXT_FIELDS, "text"),
    **dict.fromkeys(TAG_FIELDS, "tags"),
    **dict.fromkeys(DATE_FIELDS, "date"),
    **dict.fromkeys(NUMBER_FIELDS, "number"),
    **dict.fromkeys(BOOLEAN_FIELDS, "boolean"),
    **dict.fromkeys(TRACK_FIELDS, "text"),
    **dict.fromkeys(("title", "edition", "filepath", "folder", "container"), "text"),
    **dict.fromkeys(("genre", "studio", "country", "actor", "director", "writer", "producer", "content_rating", "resolution", "audio_language", "subtitle_language", "original_language", "collection"), "tags"),
    "release": "date",
    "added": "date",
}
FIELD_TYPES.update({"folder_location": "text", "dovi": "boolean", "type": "tags", "status": "tags", "show_status": "tags"})
MEDIA_FIELDS = set(TRACK_FIELDS) | {
    "folder_location",
    "dovi",
    "duplicate",
    "versions",
    "resolution",
    "edition",
    "filepath",
    "folder",
    "container",
    "audio_language",
    "subtitle_language",
    "original_language",
    "hdr",
    "has_dolby_vision",
    "hdr10plus",
    "interlaced",
    "atmos",
    "has_edition",
    "has_subtitles",
    "is_3d",
    "width",
    "height",
    "aspect",
    "channels",
    "bitrate",
    "file_size",
    "video_bitrate",
    "audio_bitrate",
    "video_bit_depth",
    "audio_bit_depth",
    "audio_sample_rate",
    "frame_rate",
    "reference_frames",
    "dovi_profile",
    "dovi_level",
}
SORT_FIELDS = {field for field, kind in FIELD_TYPES.items() if kind in ("number", "text", "date")}


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        parts = str(value).replace("/", ":").split(":")
        result = float(parts[0]) / float(parts[1]) if len(parts) == 2 else float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError, OverflowError, ZeroDivisionError):
        return None


def _list(value):
    return value if isinstance(value, list) else [] if value is None or value == "" else [value]


def _max(values):
    known = [number for value in values if (number := _number(value)) is not None]
    return [max(known)] if known else []


def values(item, field):
    raw = item.data.get("native", {})
    sources = raw.get("MediaSources")
    versions = sources if isinstance(sources, list) and sources else [raw]
    streams = [stream for source in versions for stream in source.get("MediaStreams") or raw.get("MediaStreams") or []]
    user = raw.get("UserData") or {}
    if field == "folder_location":
        return values(item, "folder")
    if field == "dovi":
        return values(item, "has_dolby_vision")
    if field == "sort_title":
        return _list(raw.get("ForcedSortName") or raw.get("SortName"))
    if field in TEXT_FIELDS:
        return _list(raw.get(TEXT_FIELDS[field]))
    if field == "collection":
        return raw.get("_kometa_collections")
    if field == "original_language":
        from modules.language_codes import normalize_language

        return [normalize_language(stream["Language"]) for stream in streams if stream.get("Type") == "Audio" and stream.get("IsOriginal") is True and stream.get("Language")]
    if field == "label":
        return [entry.get("Name") if isinstance(entry, dict) else entry for entry in raw.get("Tags") or raw.get("TagItems") or []]
    if field in TAG_FIELDS:
        return [entry.get("Name") if isinstance(entry, dict) else entry for entry in _list(raw.get(TAG_FIELDS[field]))]
    if field in DATE_FIELDS:
        return _list((user if field == "last_played" else raw).get(DATE_FIELDS[field]))
    if field in TRACK_FIELDS:
        kind, key = TRACK_FIELDS[field]
        found = [stream[key] for stream in streams if stream.get("Type") == kind and stream.get(key) is not None]
        if not found and field in ("audio_codec", "video_codec"):
            return _list(raw.get("AudioCodec" if field == "audio_codec" else "VideoCodec"))
        return found
    if field in ("duplicate", "versions"):
        return [len(sources) > 1 if field == "duplicate" else len(sources)] if isinstance(sources, list) else []
    if field == "aspect":
        return _max(version.get("aspect") for version in item.data.get("versions") or [])
    if field == "container":
        return [source["Container"] for source in versions if source.get("Container")]
    if field == "folder":
        return [path.rsplit("/", 1)[0].rsplit("\\", 1)[0] for path in common_values(item, "filepath")]
    if field in ("duration", "runtime", "duration_seconds"):
        ticks = _number(raw.get("RunTimeTicks"))
        if ticks is None:
            known = _max(source.get("RunTimeTicks") for source in versions)
            ticks = known[0] if known else None
        return [ticks / (10000000 if field == "duration_seconds" else 600000000)] if ticks is not None else []
    if field in ("bitrate", "file_size"):
        key = "Bitrate" if field == "bitrate" else "Size"
        numbers = _max(source.get(key) for source in versions)
        return [number / 1000 for number in numbers] if field == "bitrate" else numbers
    stream_numbers = {
        "width": ("Video", "Width"),
        "height": ("Video", "Height"),
        "channels": ("Audio", "Channels"),
        "video_bitrate": ("Video", "BitRate"),
        "audio_bitrate": ("Audio", "BitRate"),
        "video_bit_depth": ("Video", "BitDepth"),
        "audio_bit_depth": ("Audio", "BitDepth"),
        "audio_sample_rate": ("Audio", "SampleRate"),
        "frame_rate": ("Video", "AverageFrameRate"),
        "reference_frames": ("Video", "RefFrames"),
        "dovi_profile": ("Video", "DvProfile"),
        "dovi_level": ("Video", "DvLevel"),
    }
    if field in stream_numbers:
        kind, key = stream_numbers[field]
        return _max(stream.get(key, stream.get("RealFrameRate") if field == "frame_rate" else None) for stream in streams if stream.get("Type") == kind)
    if field in ("audience_rating", "critic_rating", "user_rating", "plays", "position_seconds", "season_number", "episode_number"):
        key, data, divisor = {
            "audience_rating": ("CommunityRating", raw, 1),
            "critic_rating": ("CriticRating", raw, 10),
            "user_rating": ("Rating", user, 1),
            "plays": ("PlayCount", user, 1),
            "position_seconds": ("PlaybackPositionTicks", user, 10000000),
            "season_number": ("ParentIndexNumber", raw, 1),
            "episode_number": ("IndexNumber", raw, 1),
        }[field]
        number = _number(data.get(key))
        return [number / divisor] if number is not None else []
    if field == "progress_ratio":
        return [number / 100] if (number := _number(user.get("PlayedPercentage"))) is not None else []
    if field in ("seasons", "episodes"):
        if raw.get("Type") not in ("Series", "Season") or field == "seasons" and raw.get("Type") != "Series":
            return []
        return _list(raw.get("SeasonCount", raw.get("ChildCount")) if field == "seasons" else raw.get("EpisodeCount", raw.get("ChildCount") if raw.get("Type") == "Season" else None))
    if field in ("watched", "unwatched", "unplayed", "is_favorite", "is_missing", "is_locked"):
        data, key = (user, "Played" if field in ("watched", "unwatched", "unplayed") else "IsFavorite") if field in ("watched", "unwatched", "unplayed", "is_favorite") else (raw, "IsMissing" if field == "is_missing" else "LockData")
        value = data.get(key)
        return [not value if field in ("unwatched", "unplayed") else value] if isinstance(value, bool) else []
    if field in ("is_in_progress", "progress"):
        position = _number(user.get("PlaybackPositionTicks"))
        played = user.get("Played")
        return [position > 0 and not played] if position is not None and isinstance(played, bool) else []
    if field == "unmatched":
        ids = raw.get("ProviderIds")
        return [not any(ids.values())] if isinstance(ids, dict) else []
    if field == "has_edition":
        return [bool(raw.get("EditionName"))] if "EditionName" in raw else []
    if field == "has_subtitles":
        if isinstance(raw.get("HasSubtitles"), bool):
            return [raw["HasSubtitles"]]
        return [any(stream.get("Type") == "Subtitle" for stream in streams)] if any("MediaStreams" in source for source in versions) or "MediaStreams" in raw else []
    if field == "is_3d":
        return [bool(source.get("Video3DFormat")) for source in versions if "Video3DFormat" in source]
    if field in ("hdr10plus", "interlaced"):
        key = "Hdr10PlusPresentFlag" if field == "hdr10plus" else "IsInterlaced"
        return [stream[key] for stream in streams if stream.get("Type") == "Video" and isinstance(stream.get(key), bool)]
    if field == "atmos":
        tracks = [stream for stream in streams if stream.get("Type") == "Audio" and any(stream.get(key) for key in ("Profile", "Title", "DisplayTitle", "AudioSpatialFormat"))]
        return [any("atmos" in " ".join(str(track.get(key) or "") for key in ("Profile", "Title", "DisplayTitle", "AudioSpatialFormat")).casefold() or str(track.get("Profile") or "").casefold() == "joc" for track in tracks)] if tracks else []
    return common_values(item, field)


def compile_selector(definition, server_name="Jellyfin", current_time=None):
    if isinstance(definition, dict) and "validate" in definition:
        if not isinstance(definition["validate"], bool):
            raise Failed(f"{server_name} Error: validate must be a boolean")
        definition = {key: value for key, value in definition.items() if key != "validate"}

    def resolve(group):
        if isinstance(group, list):
            return [resolve(child) for child in group]
        if not isinstance(group, dict):
            return group
        result = {}
        for key, value in group.items():
            field, _, modifier = key.partition(".")
            if key in ("all", "any"):
                value = resolve(value)
            elif field in ("year", "decade") and modifier != "regex":

                def year(entry):
                    if isinstance(entry, str):
                        entry = entry.removesuffix("s") if field == "decade" else entry
                        parts = entry.split("-", 1)
                        if parts[0] == "current_year" and (len(parts) == 1 or parts[1].isdecimal()):
                            return (current_time or datetime.now(timezone.utc)).year - (int(parts[1]) if len(parts) == 2 else 0)
                    return entry

                value = [year(entry) for entry in value] if isinstance(value, list) else year(value)
            result[key] = value
        return result

    return compile_local_selector(resolve(definition), server_name, field_values=values, field_types=FIELD_TYPES, current_time=current_time)


def requires_media(definition):
    if isinstance(definition, list):
        return any(requires_media(group) for group in definition)
    if isinstance(definition, dict):
        return any(key.partition(".")[0] in MEDIA_FIELDS or key == "sort_by" and str(value).partition(".")[0] in MEDIA_FIELDS or key in ("all", "any") and requires_media(value) for key, value in definition.items())
    return False
