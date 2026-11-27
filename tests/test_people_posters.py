import os
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO
from types import SimpleNamespace

import pytest
from PIL import Image, ImageDraw

from modules import people_posters as people_posters_module
from modules import util
from modules.cache import Cache
from modules.people_posters import PeoplePosters
from modules.util import Failed
from tests.conftest import FakeLogger

TRANSPARENT = "Kometa-Team/People-Images-transparent-1500"
ORIGINAL = "Kometa-Team/People-Images-1500"
TREE_URL = f"https://api.github.com/repos/{TRANSPARENT}/git/trees/master?recursive=1"


def _png():
    image = Image.new("RGBA", (1000, 1500))
    ImageDraw.Draw(image).ellipse((250, 100, 750, 1500), fill=(200, 60, 40, 255))
    buffer = BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()


PNG = _png()


class Response:
    def __init__(self, status_code=200, payload=None, content=b"", headers=None):
        self.status_code = status_code
        self.reason = "OK" if status_code < 400 else "Error"
        self.payload = payload
        self.content = content
        self.headers = headers or {}

    def json(self):
        return self.payload


class Requests:
    def __init__(self, people=None, etag='"v1"'):
        self.calls = []
        self.etag = etag
        self.tree_status = 200
        self.set_people(people or {"Tom Hanks": "sha-tom"})

    def set_people(self, people):
        self.people = people
        self.tree = [{"path": f"{name[0].upper()}/Images/{name}.png", "type": "blob", "sha": sha} for name, sha in people.items()]
        self.tree.append({"path": "README.md", "type": "blob", "sha": "readme"})

    def get(self, url, headers=None):
        self.calls.append((url, dict(headers or {})))
        if url.startswith("https://api.github.com/"):
            if self.tree_status != 200:
                return Response(self.tree_status)
            if headers and headers.get("If-None-Match") == self.etag:
                return Response(304)
            return Response(payload={"tree": self.tree, "truncated": False}, headers={"ETag": self.etag})
        return Response(content=PNG, headers={"Content-Type": "image/png"})

    def downloads(self):
        return [url for url, _ in self.calls if url.startswith("https://raw.githubusercontent.com/")]

    def tree_calls(self):
        return [headers for url, headers in self.calls if url.startswith("https://api.github.com/")]


@pytest.fixture(autouse=True)
def fake_logger(monkeypatch):
    logger = FakeLogger()
    monkeypatch.setattr(people_posters_module, "logger", logger)
    monkeypatch.setattr(util, "logger", logger)
    from modules import cache as cache_module

    monkeypatch.setattr(cache_module, "logger", logger)
    return logger


def _params(**overrides):
    params = {"original_repo": ORIGINAL, "transparent_repo": TRANSPARENT, "branch": "master", "prune_days": 90, "render_limit": 0}
    params.update(overrides)
    return params


def _make(tmp_path, requests, cache=True, token=None, **overrides):
    cache_obj = Cache(config_path=str(tmp_path / "config.yml"), expiration=60) if cache is True else cache
    github = SimpleNamespace(token=token, headers={"Authorization": f"token {token}"} if token else None)
    return PeoplePosters(requests, github, cache_obj, str(tmp_path), _params(**overrides))


def test_renders_and_caches_poster(tmp_path):
    requests = Requests()
    posters = _make(tmp_path, requests)
    image = posters.get("Tom Hanks", "rainier")
    assert image.location == os.path.join(str(tmp_path), "cache", "people_posters", "rainier", "T", "Tom Hanks.jpg")
    assert image.is_url is False
    assert image.compare.startswith("sha-tom:")
    with Image.open(image.location) as saved:
        assert saved.size == (1000, 1500)
    assert posters.rendered == 1
    assert len(requests.downloads()) == 1


def test_second_run_reuses_cached_poster(tmp_path):
    requests = Requests()
    first = _make(tmp_path, requests).get("Tom Hanks", "rainier")
    requests.calls.clear()
    posters = _make(tmp_path, requests)
    second = posters.get("Tom Hanks", "rainier")
    assert second.compare == first.compare
    assert posters.rendered == 0 and posters.reused == 1
    assert requests.downloads() == []
    assert requests.tree_calls()[0]["If-None-Match"] == '"v1"'


def test_changed_source_sha_rerenders(tmp_path):
    requests = Requests()
    first = _make(tmp_path, requests).get("Tom Hanks", "rainier")
    requests.set_people({"Tom Hanks": "sha-tom-2"})
    requests.etag = '"v2"'
    posters = _make(tmp_path, requests)
    second = posters.get("Tom Hanks", "rainier")
    assert posters.rendered == 1
    assert second.compare.startswith("sha-tom-2:") and second.compare != first.compare


def test_changed_renderer_fingerprint_rerenders_without_download(tmp_path, monkeypatch):
    requests = Requests()
    first = _make(tmp_path, requests).get("Tom Hanks", "rainier")
    requests.calls.clear()
    monkeypatch.setattr("modules.people_render.RENDERER_VERSION", "changed")
    posters = _make(tmp_path, requests)
    second = posters.get("Tom Hanks", "rainier")
    assert posters.rendered == 1
    assert second.compare != first.compare
    assert requests.downloads() == []


def test_styles_share_one_source_download(tmp_path):
    requests = Requests()
    posters = _make(tmp_path, requests)
    for style in ("bw", "rainier", "signature"):
        posters.get("Tom Hanks", style)
    assert posters.rendered == 3
    assert len(requests.downloads()) == 1


def test_deleted_poster_file_is_rerendered(tmp_path):
    requests = Requests()
    os.remove(_make(tmp_path, requests).get("Tom Hanks", "rainier").location)
    posters = _make(tmp_path, requests)
    assert os.path.exists(posters.get("Tom Hanks", "rainier").location)
    assert posters.rendered == 1


def test_same_poster_is_rendered_once_per_run(tmp_path):
    posters = _make(tmp_path, Requests())
    assert posters.get("Tom Hanks", "bw") is posters.get("Tom Hanks", "bw")
    assert posters.rendered == 1


def test_tree_is_requested_once_per_run(tmp_path):
    requests = Requests({"Tom Hanks": "a", "Meryl Streep": "b"})
    posters = _make(tmp_path, requests)
    posters.get("Tom Hanks", "bw")
    posters.get("Meryl Streep", "bw")
    assert len(requests.tree_calls()) == 1


def test_github_token_is_sent(tmp_path):
    requests = Requests()
    _make(tmp_path, requests, token="abc").get("Tom Hanks", "bw")
    assert requests.tree_calls()[0]["Authorization"] == "token abc"


def test_missing_person_fails(tmp_path):
    posters = _make(tmp_path, Requests())
    with pytest.raises(Failed, match="No image for Meryl Streep"):
        posters.get("Meryl Streep", "bw")
    assert posters.missing == 1


@pytest.mark.parametrize("name", ["Zoë Saldaña", "50 Cent", "'Weird Al' Yankovic", "İlker Kaleli"])
def test_lookup_uses_file_name_not_folder(tmp_path, name):
    posters = _make(tmp_path, Requests({name: "sha"}))
    assert posters.get(name, "bw").compare.startswith("sha:")


def test_lookup_matches_decomposed_unicode(tmp_path):
    posters = _make(tmp_path, Requests({"Zoë Saldaña": "sha"}))
    assert posters.get("Zoe\u0308 Saldan\u0303a", "bw") is not None


def test_unknown_style_fails(tmp_path):
    with pytest.raises(Failed, match="Unknown style"):
        _make(tmp_path, Requests()).get("Tom Hanks", "sepia")


def test_invalid_repo_fails(tmp_path):
    with pytest.raises(Failed, match="not a valid GitHub repository"):
        _make(tmp_path, Requests(), transparent_repo="https://github.com/Kometa-Team/People")


def test_render_limit_skips_and_warns_once(tmp_path, fake_logger):
    requests = Requests({"Tom Hanks": "a", "Meryl Streep": "b", "Viola Davis": "c"})
    posters = _make(tmp_path, requests, render_limit=1)
    assert posters.get("Tom Hanks", "bw") is not None
    assert posters.get("Meryl Streep", "bw") is None
    assert posters.get("Viola Davis", "bw") is None
    assert posters.skipped == 2
    assert len([m for m in fake_logger.warning_messages if "render limit" in m]) == 1
    posters.finish()
    assert any("2 posters were not generated" in m for m in fake_logger.warning_messages)


def test_render_limit_does_not_block_cached_posters(tmp_path):
    requests = Requests({"Tom Hanks": "a", "Meryl Streep": "b"})
    _make(tmp_path, requests).get("Tom Hanks", "bw")
    posters = _make(tmp_path, requests, render_limit=1)
    assert posters.get("Meryl Streep", "bw") is not None
    assert posters.get("Tom Hanks", "bw") is not None
    assert posters.reused == 1


def test_tree_failure_uses_previous_list(tmp_path, fake_logger):
    requests = Requests()
    _make(tmp_path, requests).get("Tom Hanks", "bw")
    requests.tree_status = 500
    posters = _make(tmp_path, requests)
    assert posters.get("Tom Hanks", "bw") is not None
    assert any("using the list from a previous run" in m for m in fake_logger.warning_messages)


def test_tree_failure_without_previous_list_fails_once(tmp_path):
    requests = Requests()
    requests.tree_status = 403
    posters = _make(tmp_path, requests)
    with pytest.raises(Failed, match="Add a GitHub token"):
        posters.get("Tom Hanks", "bw")
    with pytest.raises(Failed, match="unavailable this run"):
        posters.get("Tom Hanks", "rainier")
    assert len(requests.tree_calls()) == 1


def test_blank_branch_uses_repository_default_branch(tmp_path):
    requests = Requests()
    posters = _make(tmp_path, requests, branch=None)
    posters.get("Tom Hanks", "bw")
    assert requests.calls[0][0] == f"https://api.github.com/repos/{TRANSPARENT}/git/trees/HEAD?recursive=1"
    assert requests.downloads() == [f"https://raw.githubusercontent.com/{TRANSPARENT}/HEAD/T/Images/Tom%20Hanks.png"]
    assert posters.original_url("Tom Hanks").startswith(f"https://raw.githubusercontent.com/{ORIGINAL}/HEAD/")


def test_original_url_comes_from_original_repo(tmp_path):
    requests = Requests({"Tom Hanks": "sha"})
    posters = _make(tmp_path, requests, original_repo=TRANSPARENT)
    assert posters.original_url("Tom Hanks") == f"https://raw.githubusercontent.com/{TRANSPARENT}/master/T/Images/Tom%20Hanks.png"


def test_prune_removes_unused_posters_and_sources(tmp_path):
    requests = Requests()
    posters = _make(tmp_path, requests, prune_days=30)
    location = posters.get("Tom Hanks", "bw").location
    old = (datetime.now() - timedelta(days=31)).isoformat(timespec="seconds")
    with sqlite3.connect(posters.cache.cache_path) as connection:
        connection.execute("UPDATE people_posters SET last_used = ?", (old,))
    source_dir = os.path.join(posters.cache_dir, "_source")
    sources = [os.path.join(d, f) for d, _, files in os.walk(source_dir) for f in files]
    old_time = (datetime.now() - timedelta(days=31)).timestamp()
    for source in sources:
        os.utime(source, (old_time, old_time))
    assert posters.prune() == 2
    assert not os.path.exists(location)
    assert not any(files for _, _, files in os.walk(source_dir))
    assert posters.cache.query_people_poster("bw|tom hanks") is None


def test_prune_keeps_recent_posters(tmp_path):
    posters = _make(tmp_path, Requests(), prune_days=30)
    location = posters.get("Tom Hanks", "bw").location
    assert posters.prune() == 0
    assert os.path.exists(location)


def test_prune_days_zero_never_prunes(tmp_path):
    posters = _make(tmp_path, Requests(), prune_days=0)
    posters.get("Tom Hanks", "bw")
    with sqlite3.connect(posters.cache.cache_path) as connection:
        connection.execute("UPDATE people_posters SET last_used = '2000-01-01T00:00:00'")
    assert posters.prune() == 0


def test_cache_disabled_uses_temporary_directory(tmp_path):
    requests = Requests()
    posters = _make(tmp_path, requests, cache=None)
    location = posters.get("Tom Hanks", "bw").location
    assert not location.startswith(str(tmp_path))
    assert os.path.exists(location)
    assert posters.get("Tom Hanks", "bw").location == location
    temp_dir = posters.cache_dir
    posters.finish()
    assert not os.path.exists(temp_dir)
    assert not os.path.exists(os.path.join(str(tmp_path), "cache", "people_posters"))


def test_cache_disabled_creates_no_directory_until_needed(tmp_path, monkeypatch):
    created = []
    monkeypatch.setattr(people_posters_module.tempfile, "mkdtemp", lambda **kwargs: created.append(kwargs) or str(tmp_path / "temp"))
    _make(tmp_path, Requests(), cache=None).finish()
    assert created == []


def test_cache_disabled_always_fetches_full_tree(tmp_path):
    requests = Requests()
    _make(tmp_path, requests, cache=None).get("Tom Hanks", "bw")
    _make(tmp_path, requests, cache=None).get("Tom Hanks", "bw")
    assert all("If-None-Match" not in headers for headers in requests.tree_calls())
