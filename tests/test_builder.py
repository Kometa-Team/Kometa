from types import SimpleNamespace

from modules.builder import CollectionBuilder


class FakeShowLibrary:
    def __init__(self):
        self.plex_map = {}
        self.is_show = True
        self.ensure_calls = []

    def ensure_plex_map(self, builder_level):
        self.ensure_calls.append(builder_level)
        if builder_level == "show":
            self.plex_map["plex://show/63e3eedd166819851638a316"] = [101]


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
