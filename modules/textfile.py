import gzip
import json
import os
import re

from modules import util
from modules.util import Failed

builders = ["text_file"]

imdb_pattern = re.compile(r"^(tt\d+)$", re.IGNORECASE)
plex_guid_pattern = re.compile(r"^plex://[a-z_]+/[0-9a-f]{24}$", re.IGNORECASE)
plex_id_pattern = re.compile(r"^[0-9a-f]{24}$", re.IGNORECASE)

json_id_keys = {
    "imdb": "imdb",
    "imdb_id": "imdb",
    "tmdb": "tmdb",
    "tmdb_id": "tmdb",
    "tvdb": "tvdb",
    "tvdb_id": "tvdb",
    "plex": "plex",
    "plex_id": "plex",
    "plex_guid": "plex",
}
typed_id_keys = {"imdb": "imdb", "tmdb": "tmdb", "tvdb": "tvdb", "plex": "plex", "url": "url"}


class TextFile:
    def __init__(self, requests):
        self.requests = requests

    def _clean_line(self, line):
        entry = str(line).strip()
        if not entry or entry.startswith("#"):
            return ""
        comment_match = re.search(r"\s+#", entry)
        if comment_match:
            entry = entry[: comment_match.start()].rstrip()
        return entry

    def _request(self, url, name="Text File"):
        response = self.requests.get(url)
        if response.status_code >= 400:
            raise Failed(f"{name} Error: JSON not found at {url}")
        try:
            return response.json()
        except ValueError:
            content = getattr(response, "content", None)
            if content is None:
                raise Failed(f"{name} Error: JSON not found at {url}")
            raw = content.encode("utf-8") if isinstance(content, str) else bytes(content)
            if raw.startswith(b"\x1f\x8b"):
                try:
                    raw = gzip.decompress(raw)
                except OSError:
                    raise Failed(f"{name} Error: JSON not found at {url}")
            try:
                return json.loads(raw)
            except (TypeError, json.JSONDecodeError, UnicodeDecodeError):
                raise Failed(f"{name} Error: JSON not found at {url}")

    def _request_list(self, url, name="Text File"):
        data = self._request(url, name=name)
        if not isinstance(data, list):
            raise Failed(f"{name} Error: JSON list not found at {url}")
        return data

    def _normalize_plex(self, value, source):
        plex_value = str(value).strip().lower()
        if plex_guid_pattern.match(plex_value) or plex_id_pattern.match(plex_value):
            return [(plex_value, "plex")]
        raise Failed(f"Text File Error: Plex ID not supported in {source}: {value}")

    def _normalize_value(self, value_type, value, source, is_movie=None):
        if value_type == "imdb":
            imdb_id = util.get_id_from_imdb_url(value) if "imdb.com/title/" in str(value) else str(value).strip()
            if imdb_pattern.match(imdb_id):
                return [(imdb_id, "imdb")]
            raise Failed(f"Text File Error: IMDb ID not supported in {source}: {value}")
        if value_type == "tmdb":
            return [(util.regex_first_int(value, "TMDb ID"), "tmdb")]
        if value_type == "tvdb":
            return [(util.regex_first_int(value, "TVDb ID"), "tvdb")]
        if value_type == "plex":
            return self._normalize_plex(value, source)
        if value_type == "url":
            return self._parse_json_url(value, is_movie=is_movie)
        raise Failed(f"Text File Error: {value_type} is not a supported ID type in {source}")

    def _parse_json_item(self, item, source, is_movie=None):
        if isinstance(item, (str, int)):
            return self._parse_line(str(item), source, is_movie=is_movie)
        if not isinstance(item, dict):
            raise Failed(f"Text File Error: Unsupported JSON item found in {source}: {item}")
        item_type = None
        item_value = None
        if "type" in item and any(k in item for k in ["id", "value"]):
            item_type = str(item["type"]).lower()
            item_value = item["id"] if "id" in item else item["value"]
        elif "source" in item and any(k in item for k in ["id", "value"]):
            item_type = str(item["source"]).lower()
            item_value = item["id"] if "id" in item else item["value"]
        else:
            for key, value_type in json_id_keys.items():
                if key in item:
                    item_type = value_type
                    item_value = item[key]
                    break
        if item_type in typed_id_keys:
            return self._normalize_value(typed_id_keys[item_type], item_value, source, is_movie=is_movie)
        raise Failed(f"Text File Error: No supported IDs found in {source}: {item}")

    def _parse_json_url(self, url, is_movie=None):
        url = str(url).strip()
        ids = []
        for i, item in enumerate(self._request_list(url), 1):
            ids.extend(self._parse_json_item(item, f"{url} item {i}", is_movie=is_movie))
        if not ids:
            raise Failed(f"Text File Error: No IDs found at {url}")
        return ids

    def _parse_line(self, line, source, is_movie=None):
        entry = self._clean_line(line)
        if not entry:
            return []
        type_match = re.match(r"^([a-z_]+):(.*)$", entry, re.IGNORECASE)
        if type_match and not entry.lower().startswith(("http://", "https://", "plex://")):
            entry_type = type_match.group(1).lower()
            if entry_type in typed_id_keys:
                return self._normalize_value(typed_id_keys[entry_type], type_match.group(2).strip(), source, is_movie=is_movie)
        if imdb_pattern.match(entry) or "imdb.com/title/" in entry:
            return self._normalize_value("imdb", entry, source)
        if plex_guid_pattern.match(entry) or plex_id_pattern.match(entry):
            return self._normalize_plex(entry, source)
        if entry.startswith(("http://", "https://")):
            return self._parse_json_url(entry, is_movie=is_movie)
        if entry.isdigit():
            numeric_id = int(entry)
            if is_movie is True:
                return [(numeric_id, "tmdb")]
            if is_movie is False:
                return [(numeric_id, "tvdb")]
            return [(numeric_id, "number")]
        raise Failed(f"Text File Error: Line not supported in {source}: {entry}")

    def validate_file(self, data):
        valid_files = []
        for text_file in util.get_list(data, split=False, return_none=False):
            file_path = os.path.abspath(str(text_file))
            if not os.path.isfile(file_path):
                raise Failed(f"Text File Error: File not found at {file_path}")
            valid_files.append(file_path)
        return valid_files

    def get_ids(self, data, is_movie=None):
        ids = []
        for file_path in util.get_list(data, split=False, return_none=False):
            if util.logger:
                util.logger.info(f"Processing Text File: {file_path}")
            with open(file_path, encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, 1):
                    ids.extend(self._parse_line(line, f"{file_path}:{line_number}", is_movie=is_movie))
        if not ids:
            raise Failed("Text File Error: No IDs found.")
        return ids
