"""Local evaluation of the supported Plex-style selectors on normalized media server metadata."""

import re
from datetime import datetime, timedelta, timezone

from modules.language_codes import normalize_language
from modules.util import Failed

FIELDS = {"title", "year", "decade", "audio_language", "subtitle_language", "content_rating", "resolution", "edition", "filepath", "hdr", "has_dolby_vision", "genre", "studio", "country", "release", "added", "actor", "director", "writer", "producer"}


def values(item, field):
    data = item.data
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


def compile_selector(definition, server_name="Silo"):
    """Validate before fetching items; unknown fields never become broad matches."""
    if not isinstance(definition, dict) or not definition:
        raise Failed(f"{server_name} Error: Search groups must be nonempty mappings")
    tests = []
    for key, expected in definition.items():
        if key in ("all", "any"):
            groups = expected if isinstance(expected, list) else [expected]
            nested = [compile_selector(group, server_name) for group in groups]
            tests.append(lambda item, nested=nested, match=all if key == "all" else any: match(test(item) for test in nested))
            # Within an any mapping, its individual entries are alternatives.
            if key == "any" and isinstance(expected, dict):
                nested = [compile_selector({name: value}, server_name) for name, value in expected.items()]
                tests[-1] = lambda item, nested=nested: any(test(item) for test in nested)
            continue
        field, _, modifier = key.partition(".")
        if field not in FIELDS or modifier not in ("", "is", "not", "isnot", "regex", "begins", "ends"):
            raise Failed(f"{server_name} Error: Unsupported local search field or modifier: {key}")
        choices = expected if isinstance(expected, list) else [expected]
        if not choices or any(value is None for value in choices):
            raise Failed(f"{server_name} Error: Search value for {key} must not be empty")
        if field in ("audio_language", "subtitle_language") and modifier != "regex":
            choices = [normalize_language(value) for value in choices]
        if field == "resolution" and modifier != "regex":
            choices = [{"4k": "2160p", "8k": "4320p", "2k": "1440p", "sd": "480p"}.get(str(value).lower(), f"{value}p" if str(value).isdecimal() else str(value).lower()) for value in choices]
        if field in ("release", "added"):
            if modifier not in ("", "is", "not", "isnot") or any(isinstance(value, bool) or not str(value).isascii() or not str(value).isdecimal() or not 0 < int(value) <= 365000 for value in choices):
                raise Failed(f"{server_name} Error: {key} requires positive day counts")
            now = datetime.now(timezone.utc)
            cutoffs = [now - timedelta(days=int(value)) for value in choices]

            def date_test(item, field=field, modifier=modifier, now=now, cutoffs=cutoffs):
                dates = []
                for raw in values(item, field):
                    try:
                        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
                        dates.append(parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc))
                    except (ValueError, TypeError):
                        continue
                if not dates:
                    return False
                matched = any(cutoff <= date <= now for cutoff in cutoffs for date in dates)
                return not matched if modifier in ("not", "isnot") else matched

            tests.append(date_test)
            continue
        if field in ("hdr", "has_dolby_vision") and (modifier not in ("", "is", "not", "isnot") or any(not isinstance(value, bool) for value in choices)):
            raise Failed(f"{server_name} Error: {key} requires boolean values")
        try:
            patterns = [re.compile(str(value)) for value in choices] if modifier == "regex" else []
        except re.error as error:
            raise Failed(f"{server_name} Error: Invalid regex for {key}: {error}") from error

        def test(item, field=field, modifier=modifier, choices=choices, patterns=patterns):
            actual = values(item, field)
            if not actual:
                return False
            if modifier == "regex":
                return any(pattern.search(str(value)) for pattern in patterns for value in actual)
            pairs = [(str(value).casefold(), str(choice).casefold()) for value in actual for choice in choices]
            if modifier == "begins":
                return any(value.startswith(choice) for value, choice in pairs)
            if modifier == "ends":
                return any(value.endswith(choice) for value, choice in pairs)
            exact = modifier in ("is", "isnot") or field in ("year", "decade", "audio_language", "subtitle_language", "content_rating", "hdr", "has_dolby_vision", "resolution", "genre", "studio", "country", "actor", "director", "writer", "producer")
            matched = any(value == choice if exact else choice in value for value, choice in pairs)
            return not matched if modifier in ("not", "isnot") else matched

        tests.append(test)
    return lambda item: all(test(item) for test in tests)
