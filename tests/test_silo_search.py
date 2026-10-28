from types import SimpleNamespace

import pytest

from modules.local_search import compile_selector
from modules.util import Failed


def item(**data):
    return SimpleNamespace(data=data)


def test_nested_resolution_regex_matches_any_available_version():
    predicate = compile_selector({"all": {"any": {"resolution.regex": "(?i)2160|4k", "title.is": "Fallback"}, "hdr": True}})
    assert predicate(item(title="Example", versions=[{"resolution": "1080p", "hdr": False}, {"resolution": "2160p", "hdr": True}]))
    assert not predicate(item(title="Example", versions=[{"resolution": "1080p", "hdr": True}]))
    assert not predicate(item(title="Fallback", versions=[{"resolution": "1080p", "hdr": False}]))


def test_filename_edition_and_summary_metadata():
    data = item(versions=[{"file_path": "/Movies/Example.2024.DV.HDR10+.mkv", "edition_raw": "Director's Cut"}], overlay_summary={"resolution": "4K", "hdr": "Dolby Vision"})
    assert compile_selector({"resolution.regex": "(?i)2160|4k", "filepath.regex": ["never", r"(?i)\bdv.HDR10(\+|P(lus)?\b)"], "edition": "Director", "has_dolby_vision": True})(data)


def test_missing_metadata_does_not_match_positive_or_negative_searches():
    assert not compile_selector({"resolution.regex": "4K"})(item())
    assert not compile_selector({"filepath.not": "Director"})(item(versions=[{"file_name": "Director.mkv"}]))


@pytest.mark.parametrize("definition", [{}, {"all": {}}, {"resolution.regex": "["}, {"label": "Kometa"}, {"title.gte": "x"}, {"hdr": "false"}])
def test_invalid_search_is_rejected_before_execution(definition):
    with pytest.raises(Failed, match="Silo Error"):
        compile_selector(definition)
