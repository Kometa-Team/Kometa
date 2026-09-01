import gzip
import json
import os
import tempfile

import pytest
from ruamel.yaml import YAML

from modules.textfile import TextFile
from modules.util import Failed


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


def test_text_file_accepts_tvdb_season_and_episode_values():
    path = _write_temp_file("tvdb_season:12345/1\n" "tvdb_episode:12345-1-2\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=False) == [("12345_1", "tvdb_season"), ("12345_1_2", "tvdb_episode")]
    finally:
        os.unlink(path)


def test_text_file_accepts_episode_json_items():
    path = _write_temp_file("url:https://example.com/episodes.json\n")
    try:
        text_builder = TextFile(
            FakeRequests(
                {
                    "https://example.com/episodes.json": [
                        {"tvdb_season": "12345_1"},
                        {"tvdb_episode": {"tvdb_id": 12345, "season": 1, "episode": 2}},
                        {"type": "tvdb_episode", "id": [12345, 1, 3]},
                    ]
                }
            )
        )

        assert text_builder.get_ids(path, is_movie=False) == [
            ("12345_1", "tvdb_season"),
            ("12345_1_2", "tvdb_episode"),
            ("12345_1_3", "tvdb_episode"),
        ]
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


def test_text_file_validate_accepts_url():
    text_builder = TextFile(FakeRequests({}))

    assert text_builder.validate_file("https://example.com/list.txt") == ["https://example.com/list.txt"]


def test_text_file_accepts_plain_text_url():
    text_builder = TextFile(
        FakeRequests(
            {
                "https://example.com/list.txt": FakeResponse(
                    content="# remote list\n" "tt1234567\n" "12345 # tmdb\n" "plex://movie/5d7768244de0ee001fcc7ff0\n",
                    json_error=ValueError("not json"),
                )
            }
        )
    )

    assert text_builder.get_ids("https://example.com/list.txt", is_movie=True) == [
        ("tt1234567", "imdb"),
        (12345, "tmdb"),
        ("plex://movie/5d7768244de0ee001fcc7ff0", "plex"),
    ]


def test_text_file_accepts_json_url_as_builder_input():
    text_builder = TextFile(FakeRequests({"https://example.com/list.json": ["tt1234567", {"tmdb_id": 67890}]}))

    assert text_builder.get_ids("https://example.com/list.json", is_movie=True) == [("tt1234567", "imdb"), (67890, "tmdb")]


def test_text_file_concatenates_file_and_url_in_order():
    path = _write_temp_file("tt1234567\n")
    try:
        text_builder = TextFile(
            FakeRequests(
                {
                    "https://example.com/list.txt": FakeResponse(
                        content="67890\n",
                        json_error=ValueError("not json"),
                    )
                }
            )
        )

        assert text_builder.get_ids([path, "https://example.com/list.txt"], is_movie=True) == [("tt1234567", "imdb"), (67890, "tmdb")]
    finally:
        os.unlink(path)


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


def test_text_file_tmdb_prefix_returns_tmdb_for_movie_library():
    path = _write_temp_file("tmdb:12345\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=True) == [(12345, "tmdb")]
    finally:
        os.unlink(path)


def test_text_file_tmdb_prefix_returns_tmdb_show_for_show_library():
    path = _write_temp_file("tmdb:12345\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=False) == [(12345, "tmdb_show")]
    finally:
        os.unlink(path)


def test_text_file_tmdb_prefix_returns_both_when_library_type_unknown():
    path = _write_temp_file("tmdb:12345\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=None) == [(12345, "tmdb"), (12345, "tmdb_show")]
    finally:
        os.unlink(path)


def test_text_file_tmdb_prefix_mixed_playlist_produces_both_types():
    """Guard: in playlist mode (is_movie=None), tmdb: entries for both
    movies and shows must yield BOTH (id, "tmdb") and (id, "tmdb_show")
    so the builder can resolve against movie_map OR show_map."""
    path = _write_temp_file("tmdb:550\ntmdb:1399\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        ids = text_builder.get_ids(path, is_movie=None)
        # Movie TMDb 550 (Fight Club)
        assert (550, "tmdb") in ids
        assert (550, "tmdb_show") in ids
        # Show TMDb 1399 (Game of Thrones)
        assert (1399, "tmdb") in ids
        assert (1399, "tmdb_show") in ids
        assert len(ids) == 4  # 2 entries x 2 types each
    finally:
        os.unlink(path)


def test_text_file_tmdb_prefix_movie_library_only_tmdb_type():
    """Guard: movie library gets only (id, "tmdb")."""
    path = _write_temp_file("tmdb:550\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=True) == [(550, "tmdb")]
    finally:
        os.unlink(path)


def test_text_file_tmdb_prefix_show_library_only_tmdb_show_type():
    """Guard: show library gets only (id, "tmdb_show")."""
    path = _write_temp_file("tmdb:1399\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=False) == [(1399, "tmdb_show")]
    finally:
        os.unlink(path)


def test_text_file_json_tmdb_id_returns_tmdb_show_for_show_library():
    path = _write_temp_file("url:https://example.com/shows.json\n")
    try:
        text_builder = TextFile(
            FakeRequests(
                {
                    "https://example.com/shows.json": [
                        {"tmdb_id": 12345},
                        {"type": "tmdb", "id": 67890},
                    ]
                }
            )
        )
        assert text_builder.get_ids(path, is_movie=False) == [
            (12345, "tmdb_show"),
            (67890, "tmdb_show"),
        ]
    finally:
        os.unlink(path)


def _yaml_text(value):
    return YAML(typ="safe").load(value)["text"]


def test_text_accepts_scalar_with_yaml_comment():
    value = _yaml_text("text: tt0079945 # Star Trek: The Motion Picture\n")

    assert TextFile(FakeRequests({})).get_text_ids(value, is_movie=True) == [("tt0079945", "imdb")]


def test_text_accepts_literal_multiline_string_and_preserves_order():
    value = _yaml_text("""text: |-
  tt0079945   # Star Trek: The Motion Picture
  174         # assumed TMDb
  tmdb:154
  plex://movie/5d7768243c3c2a001fbca85b
  5d776824880197001ec901ab
""")

    assert TextFile(FakeRequests({})).get_text_ids(value, is_movie=True) == [
        ("tt0079945", "imdb"),
        (174, "tmdb"),
        (154, "tmdb"),
        ("plex://movie/5d7768243c3c2a001fbca85b", "plex"),
        ("5d776824880197001ec901ab", "plex"),
    ]


def test_text_accepts_yaml_list_with_strings_integers_and_multiline_entries():
    value = _yaml_text("""text:
  - tt0079945
  - 174
  - |-
    tmdb:154
    tvdb:361702
""")

    assert TextFile(FakeRequests({})).get_text_ids(value, is_movie=True) == [
        ("tt0079945", "imdb"),
        (174, "tmdb"),
        (154, "tmdb"),
        (361702, "tvdb"),
    ]


@pytest.mark.parametrize(
    ("is_movie", "expected"),
    [(True, [(174, "tmdb")]), (False, [(174, "tvdb")]), (None, [(174, "number")])],
)
def test_text_numeric_entries_follow_library_context(is_movie, expected):
    assert TextFile(FakeRequests({})).get_text_ids(174, is_movie=is_movie) == expected


def test_text_supports_json_list_urls_and_preserves_url_fragments():
    text_builder = TextFile(FakeRequests({"https://example.com/list.json#fragment": ["tt1234567", {"tmdb_id": 67890}]}))

    assert text_builder.get_text_ids("https://example.com/list.json#fragment", is_movie=True) == [("tt1234567", "imdb"), (67890, "tmdb")]


def test_text_supports_show_parts():
    text_builder = TextFile(FakeRequests({}))

    assert text_builder.get_text_ids(["tvdb_season:12345/1", "tvdb_episode:12345-1-2"], is_movie=False) == [
        ("12345_1", "tvdb_season"),
        ("12345_1_2", "tvdb_episode"),
    ]


@pytest.mark.parametrize("value", [None, True, 1.5, {}, [["tt1234567"]]])
def test_text_rejects_unsupported_yaml_types(value):
    with pytest.raises(Failed, match=r"Text Error: text(?: item 1)? must be"):
        TextFile(FakeRequests({})).validate_text(value)


@pytest.mark.parametrize("value", ["", "# comment only", [], ["", "# comment only"]])
def test_text_rejects_empty_or_comment_only_input(value):
    with pytest.raises(Failed, match="Text Error: No IDs found"):
        TextFile(FakeRequests({})).validate_text(value)


def test_text_error_identifies_list_item_and_line():
    with pytest.raises(Failed, match="Text Error: Line not supported in text item 2 line 2: invalid"):
        TextFile(FakeRequests({})).get_text_ids(["tt1234567", "# comment\ninvalid"], is_movie=True)
