import gzip
import json
import os
import tempfile

from modules.textfile import TextFile


class FakeResponse:
    def __init__(self, payload=None, status_code=200, content=None, headers=None, json_error=None):
        self.payload = payload
        self.status_code = status_code
        self.content = json.dumps(payload).encode("utf-8") if content is None and payload is not None else content
        self.headers = headers or {}
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.payload


class FakeRequests:
    def __init__(self, payloads):
        self.payloads = payloads

    def get(self, url):
        payload = self.payloads[url]
        return payload if isinstance(payload, FakeResponse) else FakeResponse(payload)


def _write_temp_file(content):
    handle = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
    handle.write(content)
    handle.close()
    return handle.name


def test_text_file_preserves_order_and_normalizes_movie_sources():
    path = _write_temp_file("# comment\n" "tt1234567 # imdb\n" "12345 # tmdb\n" "plex://movie/5d7768244de0ee001fcc7ff0 # plex guid\n" "5d7768244de0ee001fcc7ff1\n" "url:https://example.com/list.json\n" "plex:5d7768244de0ee001fcc7ff4 # typed plex\n")
    try:
        text_builder = TextFile(
            FakeRequests(
                {
                    "https://example.com/list.json": [
                        {"tmdb_id": 67890},
                        {"plex_guid": "plex://movie/5d7768244de0ee001fcc7ff2"},
                        "tt7654321",
                        {"type": "plex", "id": "5d7768244de0ee001fcc7ff3"},
                    ]
                }
            )
        )

        ids = text_builder.get_ids(path, is_movie=True)

        assert ids == [
            ("tt1234567", "imdb"),
            (12345, "tmdb"),
            ("plex://movie/5d7768244de0ee001fcc7ff0", "plex"),
            ("5d7768244de0ee001fcc7ff1", "plex"),
            (67890, "tmdb"),
            ("plex://movie/5d7768244de0ee001fcc7ff2", "plex"),
            ("tt7654321", "imdb"),
            ("5d7768244de0ee001fcc7ff3", "plex"),
            ("5d7768244de0ee001fcc7ff4", "plex"),
        ]
    finally:
        os.unlink(path)


def test_text_file_preserves_url_fragments_while_allowing_inline_comments():
    path = _write_temp_file("https://example.com/list.json#frag\n" "url:https://example.com/typed.json # typed url\n")
    try:
        text_builder = TextFile(FakeRequests({"https://example.com/list.json#frag": ["tt1234567"], "https://example.com/typed.json": ["tt7654321"]}))

        assert text_builder.get_ids(path, is_movie=True) == [("tt1234567", "imdb"), ("tt7654321", "imdb")]
    finally:
        os.unlink(path)


def test_text_file_accepts_gzip_compressed_json_url():
    path = _write_temp_file("https://example.com/compressed.json\n")
    try:
        compressed = gzip.compress(json.dumps(["tt1234567", {"tmdb_id": 67890}]).encode("utf-8"))
        text_builder = TextFile(
            FakeRequests(
                {
                    "https://example.com/compressed.json": FakeResponse(
                        content=compressed,
                        headers={"Content-Type": "application/gzip"},
                        json_error=ValueError("not json"),
                    )
                }
            )
        )

        assert text_builder.get_ids(path, is_movie=True) == [("tt1234567", "imdb"), (67890, "tmdb")]
    finally:
        os.unlink(path)


def test_text_file_accepts_show_plex_guid():
    path = _write_temp_file("plex://show/63e3eedd166819851638a316\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=False) == [("plex://show/63e3eedd166819851638a316", "plex")]
    finally:
        os.unlink(path)


def test_text_file_concatenates_multiple_files_in_order():
    first_path = _write_temp_file("tt1234567\n12345\n")
    second_path = _write_temp_file("plex://movie/5d7768244de0ee001fcc7ff0\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids([first_path, second_path], is_movie=True) == [
            ("tt1234567", "imdb"),
            (12345, "tmdb"),
            ("plex://movie/5d7768244de0ee001fcc7ff0", "plex"),
        ]
    finally:
        os.unlink(first_path)
        os.unlink(second_path)


def test_text_file_uses_tvdb_for_numeric_show_entries():
    path = _write_temp_file("12345\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=False) == [(12345, "tvdb")]
    finally:
        os.unlink(path)


def test_text_file_keeps_numeric_entries_generic_without_library_type():
    path = _write_temp_file("12345\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=None) == [(12345, "number")]
    finally:
        os.unlink(path)
