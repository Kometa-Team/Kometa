from types import SimpleNamespace

from plexapi.exceptions import NotFound

import modules.builder as builder_module
from modules.builder import CollectionBuilder, parts_collection_valid


class FakeShowLibrary:
    def __init__(self):
        self.plex_map = {}
        self.is_show = True
        self.ensure_calls = []

    def ensure_plex_map(self, builder_level):
        self.ensure_calls.append(builder_level)
        if builder_level == "show":
            self.plex_map["plex://show/63e3eedd166819851638a316"] = [101]
        elif builder_level == "episode":
            self.plex_map["plex://episode/63e3eedd166819851638a317"] = [201]


class FakeLogger:
    def __init__(self):
        self.info_messages = []
        self.warning_messages = []

    def info(self, message=""):
        self.info_messages.append(str(message))

    def warning(self, message):
        self.warning_messages.append(str(message))

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class FakeEpisode:
    def __init__(self, rating_key, title):
        self.ratingKey = rating_key
        self.title = title


class FakeSeason:
    def __init__(self, episodes):
        self._episodes = episodes

    def episodes(self):
        return self._episodes


class FakeShow:
    def __init__(self, title, seasons=None, episodes=None):
        self.title = title
        self._seasons = seasons or {}
        self._episodes = episodes or {}

    def season(self, season):
        if season not in self._seasons:
            raise NotFound(f"Season {season} not found")
        return self._seasons[season]

    def episode(self, season, episode):
        if (season, episode) not in self._episodes:
            raise NotFound(f"Episode {season}/{episode} not found")
        return self._episodes[(season, episode)]


class FakeTVDbLibrary:
    def __init__(self, show_item, tvdb_id=383275, rating_key=101):
        self.show_map = {tvdb_id: [rating_key]}
        self._show_item = show_item

    def fetch_item(self, rating_key):
        if rating_key != 101:
            raise AssertionError(f"Unexpected rating key: {rating_key}")
        return self._show_item


def _episode_builder(library):
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.Type = "Collection"
    builder.builder_level = "episode"
    builder.playlist = False
    builder.libraries = [library]
    builder.ignore_imdb_ids = []
    builder.ignore_ids = []
    builder.missing_parts = []
    builder.missing_shows = []
    builder.do_missing = True
    builder.filters = []
    builder.details = {"show_filtered": False, "show_unfiltered": False, "only_filter_missing": False}
    builder.filtered_keys = {}
    builder.found_items = []
    builder.do_report = False
    builder.obj = None
    builder.name = "Test Collection"
    builder.check_filters = lambda item, display: True
    return builder


def test_find_plex_keys_loads_show_map_for_show_guid():
    library = FakeShowLibrary()
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.libraries = [library]
    builder.builder_level = "show"
    builder.playlist = False

    assert builder._find_plex_keys("plex://show/63e3eedd166819851638a316") == [101]
    assert library.ensure_calls == ["show"]


def test_textfile_registers_multiple_files_as_single_builder():
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.builders = []
    builder.config = SimpleNamespace(TextFile=SimpleNamespace(validate_file=lambda data: ["/tmp/priority.txt", "/tmp/overflow.txt"]))

    builder._textfile("text_file", ["config/lists/priority.txt", "config/lists/overflow.txt"])

    assert builder.builders == [("text_file", ["/tmp/priority.txt", "/tmp/overflow.txt"])]


def test_find_plex_keys_loads_episode_map_for_episode_guid():
    library = FakeShowLibrary()
    builder = CollectionBuilder.__new__(CollectionBuilder)
    builder.libraries = [library]
    builder.builder_level = "episode"
    builder.playlist = False

    assert builder._find_plex_keys("plex://episode/63e3eedd166819851638a317") == [201]
    assert library.ensure_calls == ["episode"]


def test_textfile_is_allowed_for_episode_or_season_collections():
    assert "text_file" in parts_collection_valid


def test_filter_and_save_items_records_missing_tvdb_season_for_episode_builder(monkeypatch):
    logger = FakeLogger()
    monkeypatch.setattr(builder_module, "logger", logger)
    builder = _episode_builder(FakeTVDbLibrary(FakeShow("Example Show")))

    assert builder.filter_and_save_items([("383275_2", "tvdb_season")]) is None
    assert builder.missing_parts == ["Example Show Season: 2 Missing"]
    assert any("tvdb_season:383275_2 -> Example Show Season: 2 Missing" in m for m in logger.warning_messages)
    assert "0 Episodes Expanded from 1 ID" in logger.info_messages
    assert "0 Unique Episodes Kept" in logger.info_messages


def test_filter_and_save_items_records_missing_tvdb_episode_for_episode_builder(monkeypatch):
    logger = FakeLogger()
    monkeypatch.setattr(builder_module, "logger", logger)
    builder = _episode_builder(FakeTVDbLibrary(FakeShow("Example Show")))

    assert builder.filter_and_save_items([("383275_2_1", "tvdb_episode")]) is None
    assert builder.missing_parts == ["Example Show Season: 2 Episode: 1 Missing"]
    assert any("tvdb_episode:383275_2_1 -> Example Show Season: 2 Episode: 1 Missing" in m for m in logger.warning_messages)


def test_filter_and_save_items_expands_tvdb_season_into_episodes_for_episode_builder(monkeypatch):
    monkeypatch.setattr(builder_module, "logger", FakeLogger())
    monkeypatch.setattr(builder_module, "Episode", FakeEpisode)
    monkeypatch.setattr(builder_module.util, "item_title", lambda item: item.title)
    episodes = [FakeEpisode(201, "Episode 1"), FakeEpisode(202, "Episode 2")]
    builder = _episode_builder(FakeTVDbLibrary(FakeShow("Example Show", seasons={2: FakeSeason(episodes)})))

    builder.filter_and_save_items([("383275_2", "tvdb_season")])

    assert builder.found_items == episodes


def test_filter_and_save_items_logs_expanded_and_unique_episode_counts(monkeypatch):
    logger = FakeLogger()
    monkeypatch.setattr(builder_module, "logger", logger)
    monkeypatch.setattr(builder_module, "Episode", FakeEpisode)
    monkeypatch.setattr(builder_module.util, "item_title", lambda item: item.title)
    episode_one = FakeEpisode(201, "Episode 1")
    episode_two = FakeEpisode(202, "Episode 2")
    builder = _episode_builder(
        FakeTVDbLibrary(
            FakeShow(
                "Example Show",
                seasons={2: FakeSeason([episode_one, episode_two])},
                episodes={(2, 1): episode_one},
            )
        )
    )

    builder.filter_and_save_items([("383275_2", "tvdb_season"), ("383275_2_1", "tvdb_episode")])

    assert "3 Episodes Expanded from 2 IDs" in logger.info_messages
    assert "2 Unique Episodes Kept" in logger.info_messages


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


def test_text_file_tmdb_prefix_returns_tmdb_when_library_type_unknown():
    path = _write_temp_file("tmdb:12345\n")
    try:
        text_builder = TextFile(FakeRequests({}))
        assert text_builder.get_ids(path, is_movie=None) == [(12345, "tmdb")]
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
