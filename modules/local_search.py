"""Local evaluation of the supported Plex-style selectors on normalized media server metadata."""

import math
import operator
import re
from datetime import datetime, timedelta, timezone

from modules.language_codes import normalize_language
from modules.util import Failed

FIELDS = {
    "duplicate",
    "title",
    "year",
    "decade",
    "audio_language",
    "subtitle_language",
    "content_rating",
    "resolution",
    "edition",
    "filepath",
    "hdr",
    "has_dolby_vision",
    "genre",
    "studio",
    "country",
    "release",
    "added",
    "actor",
    "director",
    "writer",
    "producer",
}


def values(item, field):
    data = item.data
    if field == "duplicate":
        return [data["duplicate"]] if isinstance(data.get("duplicate"), bool) else []
    if field == "decade":
        year = data.get("year")
        return [int(year) // 10 * 10] if not isinstance(year, bool) and str(year).isascii() and str(year).isdecimal() and 1 <= int(year) <= 9999 else []
    if field in ("audio_language", "subtitle_language"):
        track_fields = ("audio_tracks",) if field == "audio_language" else ("subtitle_tracks", "external_subtitles")
        return [normalize_language(track["language"]) for version in data.get("versions") or [] for track_field in track_fields for track in version.get(track_field) or [] if isinstance(track.get("language"), str) and track["language"].strip()]
    if field == "content_rating":
        rating = data.get(field)
        return [rating.strip()] if isinstance(rating, str) and rating.strip() else []
    if field in ("actor", "director", "writer", "producer"):
        return data.get(field) or [person.tag for person in getattr(item, f"{field}s", [])]
    overlay = data.get("overlay_summary") or {}
    versions = data.get("versions") or []
    if field == "filepath":
        return [v["file_path"] for v in versions if v.get("file_path")]
    if field == "resolution":
        return [v["resolution"] for v in versions if v.get("resolution")] or ([overlay["resolution"]] if overlay.get("resolution") else [])
    if field == "edition":
        return [v.get("edition_raw") or v.get("edition_key") for v in versions if v.get("edition_raw") or v.get("edition_key")] or ([overlay["edition"]] if overlay.get("edition") else [])
    if field == "hdr":
        return [v["hdr"] for v in versions if isinstance(v.get("hdr"), bool)] or ([bool(overlay["hdr"])] if overlay.get("hdr") else [])
    if field == "has_dolby_vision":
        known = [v["dolby_vision"] for v in versions if isinstance(v.get("dolby_vision"), bool)]
        if known:
            return known
        return ["dolby vision" in str(overlay["hdr"]).lower()] if "hdr" in overlay else []
    if field in ("genre", "studio", "country"):
        return data.get({"genre": "genres", "studio": "studios", "country": "countries"}[field]) or []
    return [data[field]] if data.get(field) is not None else []


def compile_selector(definition, server_name="Silo", field_values=None, field_types=None, current_time=None):
    """Validate before fetching items; unknown fields never become broad matches."""
    if not isinstance(definition, dict) or not definition:
        raise Failed(f"{server_name} Error: Search groups must be nonempty mappings")
    tests = []
    read_values = field_values or values
    types = field_types or {}
    for key, expected in definition.items():
        if key in ("all", "any"):
            groups = expected if isinstance(expected, list) else [expected]
            nested = [compile_selector(group, server_name, field_values, field_types, current_time) for group in groups]
            tests.append(lambda item, nested=nested, match=all if key == "all" else any: match(test(item) for test in nested))
            # Within an any mapping, its individual entries are alternatives.
            if key == "any" and isinstance(expected, dict):
                nested = [compile_selector({name: value}, server_name, field_values, field_types, current_time) for name, value in expected.items()]
                tests[-1] = lambda item, nested=nested: any(test(item) for test in nested)
            continue
        field, _, modifier = key.partition(".")
        kind = types.get(field)
        modifiers = {"", "is", "not", "isnot", "regex", "begins", "ends"}
        if kind == "number":
            modifiers |= {"gt", "gte", "lt", "lte"}
        if kind == "tags":
            modifiers |= {"and", "and.not", "count_gt", "count_gte", "count_lt", "count_lte"}
        if kind == "date":
            modifiers |= {"before", "after", "last", "notlast"}
        if (field not in FIELDS and field not in types) or modifier not in modifiers:
            raise Failed(f"{server_name} Error: Unsupported local search field or modifier: {key}")
        choices = expected if isinstance(expected, list) else [expected]
        tag_field = kind == "tags" or field in ("genre", "studio", "country", "actor", "director", "writer", "producer", "content_rating", "resolution", "audio_language", "subtitle_language", "original_language")
        if tag_field and isinstance(expected, str) and modifier != "regex" and not modifier.startswith("count_"):
            choices = [value.strip() for value in expected.split(",") if value.strip()]
        if not choices or any(value is None for value in choices):
            raise Failed(f"{server_name} Error: Search value for {key} must not be empty")
        if field in ("audio_language", "subtitle_language", "original_language") and modifier != "regex":
            choices = [normalize_language(value) for value in choices]
        if field == "resolution" and modifier != "regex":
            choices = [{"4k": "2160p", "8k": "4320p", "2k": "1440p", "sd": "480p"}.get(str(value).lower(), f"{value}p" if str(value).isdecimal() else str(value).lower()) for value in choices]
        if kind == "number" and modifier in ("", "is", "not", "isnot", "gt", "gte", "lt", "lte") or modifier.startswith("count_"):
            try:
                if any(isinstance(value, bool) or not math.isfinite(float(value)) for value in choices):
                    raise ValueError()
                numbers = [float(value) for value in choices]
            except (TypeError, ValueError, OverflowError) as error:
                raise Failed(f"{server_name} Error: {key} requires finite numbers") from error
            comparison = {"gt": operator.gt, "gte": operator.ge, "lt": operator.lt, "lte": operator.le}.get(modifier.removeprefix("count_"), operator.eq)

            def numeric_test(item, field=field, modifier=modifier, numbers=numbers, comparison=comparison):
                raw = read_values(item, field)
                if raw is None:
                    return False
                actual = [len(set(map(str, raw)))] if modifier.startswith("count_") else raw
                actual = [float(value) for value in actual if not isinstance(value, bool) and _finite_number(value)]
                if not actual:
                    return False
                matched = any(comparison(value, choice) for value in actual for choice in numbers)
                return not matched if modifier in ("not", "isnot") else matched

            tests.append(numeric_test)
            continue
        if kind == "date" and modifier in ("before", "after"):
            try:
                dates = [_date(value) for value in choices]
            except (ValueError, TypeError) as error:
                raise Failed(f"{server_name} Error: {key} requires dates (YYYY-MM-DD)") from error

            def absolute_date_test(item, field=field, modifier=modifier, dates=dates):
                for value in read_values(item, field):
                    try:
                        actual = _date(value)
                    except (ValueError, TypeError):
                        continue
                    if any(actual < target if modifier == "before" else actual > target for target in dates):
                        return True
                return False

            tests.append(absolute_date_test)
            continue
        if (field in ("release", "added") or kind == "date") and modifier != "regex":
            if modifier not in ("", "is", "not", "isnot", "last", "notlast") or any(isinstance(value, bool) or not str(value).isascii() or not str(value).isdecimal() or not 0 < int(value) <= 365000 for value in choices):
                raise Failed(f"{server_name} Error: {key} requires positive day counts")
            now = _date(current_time) if current_time is not None else datetime.now(timezone.utc)
            cutoffs = [now - timedelta(days=int(value)) for value in choices]

            def date_test(item, field=field, modifier=modifier, now=now, cutoffs=cutoffs):
                dates = []
                for raw in read_values(item, field):
                    try:
                        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
                        dates.append(parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc))
                    except (ValueError, TypeError):
                        continue
                if not dates:
                    return False
                matched = any(cutoff <= date <= now for cutoff in cutoffs for date in dates)
                return not matched if modifier in ("not", "isnot", "notlast") else matched

            tests.append(date_test)
            continue
        if (field in ("duplicate", "hdr", "has_dolby_vision") or kind == "boolean") and (modifier not in ("", "is", "not", "isnot") or any(not isinstance(value, bool) for value in choices)):
            raise Failed(f"{server_name} Error: {key} requires boolean values")
        try:
            patterns = [re.compile(str(value)) for value in choices] if modifier == "regex" else []
        except re.error as error:
            raise Failed(f"{server_name} Error: Invalid regex for {key}: {error}") from error

        def test(item, field=field, modifier=modifier, choices=choices, patterns=patterns, kind=kind):
            actual = read_values(item, field)
            if not actual:
                if field == "content_rating" and modifier in ("", "is"):
                    return any(str(choice).casefold() == "none" for choice in choices)
                return False
            if modifier == "regex":
                return any(pattern.search(str(value)) for pattern in patterns for value in actual)
            pairs = [(str(value).casefold(), str(choice).casefold()) for value in actual for choice in choices]
            if field == "resolution":
                pairs = [(_resolution(value), _resolution(choice)) for value, choice in pairs]
            if modifier in ("and", "and.not"):
                matched = all(
                    any(value == choice or field in ("audio_language", "subtitle_language", "original_language") and value.startswith(choice + "-") for value, pair_choice in pairs if pair_choice == choice) for choice in {pair[1] for pair in pairs}
                )
                return not matched if modifier == "and.not" else matched
            if modifier == "begins":
                return any(value.startswith(choice) for value, choice in pairs)
            if modifier == "ends":
                return any(value.endswith(choice) for value, choice in pairs)
            exact = (
                kind in ("tags", "boolean")
                or modifier in ("is", "isnot")
                or field in ("duplicate", "year", "decade", "audio_language", "subtitle_language", "content_rating", "hdr", "has_dolby_vision", "resolution", "genre", "studio", "country", "actor", "director", "writer", "producer")
            )
            matched = any((value == choice or field in ("audio_language", "subtitle_language", "original_language") and value.startswith(choice + "-")) if exact else choice in value for value, choice in pairs)
            return not matched if modifier in ("not", "isnot") else matched

        tests.append(test)
    return lambda item: all(test(item) for test in tests)


def _finite_number(value):
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _date(value):
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _resolution(value):
    value = str(value).strip().lower()
    return {"4k": "2160p", "8k": "4320p", "2k": "1440p", "uhd": "2160p", "sd": "480p"}.get(value, f"{value}p" if value.isascii() and value.isdecimal() else value)
