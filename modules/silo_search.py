"""Search/filter fields backed by Silo's catalog detail and file/track contracts.

Native query support is narrower than item metadata. These readers never fetch
external metadata or infer unavailable labels, collections, or play counts.
"""

import math
from datetime import datetime, timezone

from modules.language_codes import normalize_language
from modules.local_search import compile_selector as compile_local_selector
from modules.local_search import values as common_values

TEXT_FIELDS = {
    "title": "title",
    "summary": "overview",
    "overview": "overview",
    "original_title": "original_title",
    "sort_title": "sort_title",
    "tagline": "tagline",
    "show_title": "series_title",
    "type": "type",
    "status": "status",
    "show_status": "show_status",
}
TAG_FIELDS = {"genre": "genres", "studio": "studios", "network": "networks", "country": "countries", "origin_country": "countries", "keyword": "keywords", "folder": "folder_paths"}
DATE_FIELDS = {"release": "release_date", "added": "added_at", "first_episode_aired": "first_air_date", "last_episode_aired": "last_air_date", "last_played": "viewed_at"}
NUMBER_FIELDS = {
    "year",
    "decade",
    "duration",
    "runtime",
    "duration_seconds",
    "versions",
    "channels",
    "height",
    "width",
    "aspect",
    "dovi_profile",
    "dovi_level",
    "bitrate",
    "video_bitrate",
    "audio_bitrate",
    "file_size",
    "frame_rate",
    "video_bit_depth",
    "audio_bit_depth",
    "audio_sample_rate",
    "reference_frames",
    "critic_rating",
    "audience_rating",
    "user_rating",
    "rating_imdb",
    "rating_tmdb",
    "rating_rt_critic",
    "rating_rt_audience",
    "plays",
    "progress",
    "position_seconds",
    "seasons",
    "episodes",
    "season_number",
    "episode_number",
    "advisory_age",
}
TRACK_FIELDS = {
    "audio_codec": ("audio_tracks", "codec"),
    "audio_profile": ("audio_tracks", "profile"),
    "audio_track_title": ("audio_tracks", "title"),
    "subtitle_track_title": ("subtitle_tracks", "title"),
    "video_codec": ("video_tracks", "codec"),
    "video_profile": ("video_tracks", "profile"),
    "video_range": ("video_tracks", "video_range_type"),
}
BOOLEAN_FIELDS = {"hdr", "has_dolby_vision", "hdr10plus", "atmos", "interlaced", "has_edition", "unmatched", "watched", "is_favorite", "in_watchlist", "not_interested", "is_in_progress"}
FIELD_TYPES = {
    **dict.fromkeys(TEXT_FIELDS, "text"),
    **dict.fromkeys(TAG_FIELDS, "tags"),
    **dict.fromkeys(DATE_FIELDS, "date"),
    **dict.fromkeys(NUMBER_FIELDS, "number"),
    **dict.fromkeys(TRACK_FIELDS, "text"),
    **dict.fromkeys(BOOLEAN_FIELDS, "boolean"),
    **dict.fromkeys(("actor", "director", "producer", "writer", "content_rating", "resolution", "original_language", "audio_language", "subtitle_language"), "tags"),
    "edition": "text",
    "filepath": "text",
    "folder": "text",
    "container": "text",
    "release_type": "text",
}
FIELD_TYPES.update({"type": "tags", "status": "tags", "show_status": "tags"})
SORT_FIELDS = {field: field for field in (*TEXT_FIELDS, *NUMBER_FIELDS, "content_rating", "original_language", "release", "added", "last_played")}
DETAIL_FIELDS = (
    set(TRACK_FIELDS)
    | BOOLEAN_FIELDS
    | {
        "actor",
        "director",
        "writer",
        "producer",
        "country",
        "origin_country",
        "folder",
        "edition",
        "filepath",
        "resolution",
        "audio_language",
        "subtitle_language",
        "container",
        "release_type",
        "aspect",
        "width",
        "height",
        "channels",
        "versions",
        "dovi_level",
        "dovi_profile",
        "bitrate",
        "file_size",
        "frame_rate",
        "video_bitrate",
        "audio_bitrate",
        "video_bit_depth",
        "audio_bit_depth",
        "audio_sample_rate",
        "reference_frames",
    }
)
DETAIL_FIELDS |= {"original_title", "sort_title", "tagline", "first_episode_aired", "last_played", "user_rating", "seasons", "episodes", "season_number", "episode_number", "position_seconds", "critic_rating", "audience_rating"}
DETAIL_FIELDS -= {"unmatched", "watched", "is_favorite", "in_watchlist", "not_interested"}


def requires_details(definition):
    if isinstance(definition, list):
        return any(requires_details(group) for group in definition)
    if not isinstance(definition, dict):
        return False
    return any(key.partition(".")[0] in DETAIL_FIELDS or (key in ("all", "any") and requires_details(value)) or (key == "sort_by" and str(value).partition(".")[0] in DETAIL_FIELDS) for key, value in definition.items())


def _present(value):
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def _list(value):
    return value if isinstance(value, list) else [value] if _present(value) else []


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        parts = str(value).replace("/", ":").split(":")
        number = float(parts[0]) / float(parts[1]) if len(parts) == 2 else float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError, ZeroDivisionError, OverflowError):
        return None


def _max(values):
    numbers = [number for value in values if (number := _number(value)) is not None]
    return [max(numbers)] if numbers else []


def _rating(data, field):
    score = _number(data.get(field))
    maximum = 10 if field in ("rating_imdb", "rating_tmdb") else 100
    if score is not None and 0 <= score <= maximum:
        return score
    source = {"rating_imdb": "imdb", "rating_tmdb": "tmdb", "rating_rt_critic": "rt_critic", "rating_rt_audience": "rt_audience"}[field]
    for entry in [*(data.get("rating_sources") or []), *(data.get("ratings") or [])]:
        if entry.get("source") == source and (number := _number(entry.get("score"))) is not None and 0 <= number <= 100:
            return number / 10 if maximum == 10 else number
    return None


def values(item, field):
    data = item.data
    versions = data.get("versions") or []
    overlay = data.get("overlay_summary") or {}
    video = [track for version in versions for track in version.get("video_tracks") or []]
    audio = [track for version in versions for track in version.get("audio_tracks") or []]
    if field in TEXT_FIELDS:
        return _list(data.get(TEXT_FIELDS[field]))
    if field in TAG_FIELDS:
        if TAG_FIELDS[field] not in data:
            return None
        return [name for value in _list(data.get(TAG_FIELDS[field])) if _present(name := value.get("name") if isinstance(value, dict) else value)]
    if field in DATE_FIELDS:
        return _list((data.get("sort_metrics") or {}).get("viewed_at") if field == "last_played" else data.get(DATE_FIELDS[field]))
    if field == "original_language":
        return [normalize_language(value) for value in _list(data.get(field))]
    if field in TRACK_FIELDS:
        tracks, attribute = TRACK_FIELDS[field]
        found = [track[attribute] for version in versions for track in version.get(tracks) or [] if _present(track.get(attribute))]
        if not found and field in ("audio_codec", "video_codec"):
            found = [version[key] for version in versions if _present(version.get(key := "codec_audio" if field == "audio_codec" else "codec_video"))]
        if field == "subtitle_track_title":
            found += [track["title"] for track in (data.get("subtitles") or []) if _present(track.get("title"))]
            found += [track["title"] for version in versions for track in version.get("external_subtitles") or [] if _present(track.get("title"))]
        if field == "audio_track_title":
            found += [track["embedded_title"] for track in audio if _present(track.get("embedded_title"))]
        return found
    if field == "container":
        return [version[field] for version in versions if _present(version.get(field))] or _list(overlay.get(field))
    if field == "release_type":
        return _list(overlay.get(field))
    if field == "aspect":
        ratios = []
        for track in video:
            ratio = _number(track.get("aspect_ratio"))
            if ratio is None and (_number(track.get("height")) or 0) > 0:
                ratio = (_number(track.get("width")) or 0) / _number(track["height"])
            if ratio is not None and ratio > 0:
                ratios.append(round(ratio, 2))
        if not ratios and (ratio := _number(overlay.get("aspect_ratio"))) is not None and ratio > 0:
            ratios = [round(ratio, 2)]
        return _max(ratios)
    if field in ("width", "height", "video_bit_depth", "reference_frames", "frame_rate", "video_bitrate"):
        attribute = {"video_bit_depth": "bit_depth", "video_bitrate": "bitrate"}.get(field, field)
        return _max(track.get(attribute) for track in video)
    if field in ("channels", "audio_bit_depth", "audio_sample_rate", "audio_bitrate"):
        attribute = {"audio_bit_depth": "bit_depth", "audio_sample_rate": "sample_rate", "audio_bitrate": "bitrate"}.get(field, field)
        return _max(track.get(attribute) for track in audio)
    if field in ("dovi_profile", "dovi_level"):
        return [number for track in video if (number := _number(track.get("dv_profile" if field == "dovi_profile" else "dv_level"))) is not None]
    if field in ("hdr10plus", "interlaced"):
        return [track[key] for track in video if isinstance(track.get(key := "hdr10_plus" if field == "hdr10plus" else field), bool)]
    if field == "atmos":
        known = [track for track in audio if any(_present(track.get(key)) for key in ("profile", "title", "embedded_title"))]
        return [any("atmos" in " ".join(str(track.get(key) or "") for key in ("profile", "title", "embedded_title")).casefold() or str(track.get("profile") or "").casefold() == "joc" for track in known)] if known else []
    if field == "has_dolby_vision":
        known = [track for track in video if any(key in track for key in ("dv_profile", "dv_config_present", "dolby_vision"))]
        if known:
            return [any((_number(track.get("dv_profile")) or 0) > 0 or track.get("dv_config_present") is True or str(track.get("dolby_vision") or "").casefold() not in ("", "none", "false") for track in known)]
    if field == "has_edition":
        editions = common_values(item, "edition")
        return [bool(editions)] if "versions" in data or editions else []
    if field == "unmatched":
        return [data["status"] == "unmatched"] if data.get("status") in ("matched", "unmatched") else []
    if field in ("watched", "is_favorite", "in_watchlist", "not_interested"):
        return _list((data.get("user_state") or {}).get("played" if field == "watched" else field))
    if field == "is_in_progress":
        return _list((data.get("user_data") or {}).get(field))
    if field in ("duration", "runtime"):
        if _number(data.get("runtime")) is not None:
            return _list(data["runtime"])
        seconds = _number(data.get("duration_seconds"))
        return [seconds / 60] if seconds is not None else _max(number / 60 for version in versions if (number := _number(version.get("duration"))) is not None)
    if field == "versions":
        return [len(versions)] if "versions" in data else []
    if field in ("bitrate", "file_size"):
        return _max(version.get(field) for version in versions)
    if field in ("critic_rating", "audience_rating", "user_rating"):
        key, scale = {"critic_rating": ("rating_rt_critic", 0.1), "audience_rating": ("rating_rt_audience", 0.1), "user_rating": ("user_rating", 2)}[field]
        number = _number(data.get(key)) if field == "user_rating" else _rating(data, key)
        return [round(number * scale, 4)] if number is not None else []
    if field in ("rating_imdb", "rating_tmdb", "rating_rt_critic", "rating_rt_audience"):
        return _list(_rating(data, field))
    if field == "duration_seconds" and not _present(data.get(field)):
        if (minutes := _number(data.get("runtime"))) is not None:
            return [minutes * 60]
        return _max(version.get("duration") for version in versions)
    if field in ("plays", "progress"):
        return _list((data.get("sort_metrics") or {}).get("play_count" if field == "plays" else "progress_ratio"))
    if field == "position_seconds":
        return _list((data.get("user_data") or {}).get(field, data.get(field)))
    if field in ("seasons", "episodes"):
        return _list(data.get("season_count" if field == "seasons" else "episode_count"))
    if field in NUMBER_FIELDS and field not in ("year", "decade"):
        return _list(data.get(field))
    if field in ("audio_language", "subtitle_language"):
        found = common_values(item, field)
        if field == "subtitle_language":
            found += [normalize_language(track["language"]) for track in data.get("subtitles") or [] if _present(track.get("language"))]
        return list(dict.fromkeys(found))
    if field == "hdr" and not any(isinstance(version.get("hdr"), bool) for version in versions):
        ranges = [track.get("video_range_type") or track.get("video_range") for track in video]
        known = [str(value).casefold() for value in ranges if _present(value) and str(value).casefold() != "unknown"]
        if known:
            return [value != "sdr" for value in known]
        if str(overlay.get("hdr") or "").casefold() in ("sdr", "none"):
            return [False]
    return common_values(item, field)


def compile_selector(definition, server_name="Silo", current_time=None, country_names=None):
    names = country_names or {}
    aliases = {"united states": "US", "south korea": "KR", "north korea": "KP", "russia": "RU", "taiwan": "TW"}

    def country(value):
        code = aliases.get(str(value).casefold(), str(value).upper())
        return names.get(code, value)

    def resolve(group):
        if isinstance(group, list):
            return [resolve(child) for child in group]
        if not isinstance(group, dict):
            return group
        result = {}
        for key, value in group.items():
            field, _, modifier = key.partition(".")
            if FIELD_TYPES.get(field) == "tags" and isinstance(value, str) and modifier != "regex" and not modifier.startswith("count_"):
                value = [entry.strip() for entry in value.split(",") if entry.strip()]
            if key in ("all", "any"):
                value = resolve(value)
            elif field in ("country", "origin_country") and modifier != "regex" and not modifier.startswith("count_"):
                value = [country(entry) for entry in value] if isinstance(value, list) else country(value)
            elif field in ("year", "decade") and modifier != "regex":

                def year(entry):
                    if not isinstance(entry, str):
                        return entry
                    text = entry.strip().removesuffix("s") if field == "decade" else entry.strip()
                    if text.startswith("current_year"):
                        parts = text.split("-", 1)
                        if len(parts) == 1 or parts[1].isdecimal():
                            return (current_time or datetime.now(timezone.utc)).year - (int(parts[1]) if len(parts) == 2 else 0)
                    return text

                value = [year(entry) for entry in value] if isinstance(value, list) else year(value)
            result[key] = value
        return result

    def read(item, field):
        found = values(item, field)
        if field in ("country", "origin_country") and found is not None:
            return list(dict.fromkeys(country(value) for value in found))
        return found

    return compile_local_selector(resolve(definition), server_name, field_values=read, field_types=FIELD_TYPES, current_time=current_time)
