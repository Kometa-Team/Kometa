"""Contract tests: InMemoryYAMLRequests must match the real YAML class on the .data / .save() surface that ConfigFile uses."""

import pytest

import modules.builder  # noqa: F401
from modules.util import Failed
from tests.conftest import FakeRequests, InMemoryYAMLRequests

CONTENT = """
settings:
  cache: false
libraries:
  Movies:
    collection_files: []
blank:
"""
EXPECTED = {"settings": {"cache": False}, "libraries": {"Movies": {"collection_files": []}}, "blank": None}


@pytest.fixture(params=[FakeRequests, InMemoryYAMLRequests], ids=["real", "in_memory"])
def yaml_requests(request):
    return request.param()


@pytest.fixture
def path(tmp_path):
    config = tmp_path / "config.yml"
    config.write_text(CONTENT, encoding="utf-8")
    return str(config)


def test_data_matches_the_file(yaml_requests, path):
    assert yaml_requests.file_yaml(path).data == EXPECTED


def test_mutation_is_not_visible_until_saved(yaml_requests, path):
    handle = yaml_requests.file_yaml(path)
    handle.data["settings"]["added"] = 1
    assert yaml_requests.file_yaml(path).data == EXPECTED


def test_saved_mutation_is_visible_to_the_next_load(yaml_requests, path):
    handle = yaml_requests.file_yaml(path)
    handle.data["settings"]["added"] = 1
    handle.save()
    assert yaml_requests.file_yaml(path).data["settings"] == {"cache": False, "added": 1}


def test_handles_are_independent(yaml_requests, path):
    first, second = yaml_requests.file_yaml(path), yaml_requests.file_yaml(path)
    first.data["settings"]["added"] = 1
    assert second.data == EXPECTED


def test_missing_parent_can_be_created_and_saved(yaml_requests, path):
    """Mirrors ConfigFile.check_for_attribute writing a default under a parent that does not exist yet."""
    handle = yaml_requests.file_yaml(path)
    handle.data["mal"] = {"client_secret": "x"}
    handle.save()
    assert yaml_requests.file_yaml(path).data["mal"] == {"client_secret": "x"}


def test_successive_saves_accumulate(yaml_requests, path):
    for key in ("a", "b", "c"):
        handle = yaml_requests.file_yaml(path)
        handle.data["settings"][key] = key
        handle.save()
    assert yaml_requests.file_yaml(path).data["settings"] == {"cache": False, "a": "a", "b": "b", "c": "c"}


def test_empty_file_loads_as_an_empty_mapping(yaml_requests, tmp_path):
    empty = tmp_path / "empty.yml"
    empty.write_text("", encoding="utf-8")
    assert yaml_requests.file_yaml(str(empty)).data == {}


def test_missing_file_raises_failed(yaml_requests, tmp_path):
    with pytest.raises(Failed):
        yaml_requests.file_yaml(str(tmp_path / "nope.yml"))


def test_read_only_kwarg_reaches_the_real_yaml(yaml_requests, path):
    handle = yaml_requests.file_yaml(path, read_only=True)
    with pytest.raises(Failed):
        handle.save()
