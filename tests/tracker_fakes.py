"""Shared fakes for tracker-connector tests. test_flicklist.py keeps its own inline copies (it
predates this file and editing it isn't part of Layer 0's zero-edit acceptance test) - this file
is for test_tracker.py and future connector test files (test_wetrakr.py, ...) to import instead
of redefining the same fakes a third time."""


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, headers=None, content=b"{}", text=None, reason="OK", raise_on_json=False):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = headers or {}
        self.content = content
        self.text = text if text is not None else ("" if content == b"" else content.decode("utf-8", errors="ignore"))
        self.reason = reason
        self._raise_on_json = raise_on_json

    def json(self):
        if self._raise_on_json:
            raise ValueError("not JSON")
        return self._json_data


class FakeSession:
    def __init__(self, parent):
        self._parent = parent

    def delete(self, url, json=None, headers=None, timeout=None):
        self._parent.deletes.append((url, json, headers))
        return self._parent._responses.pop(0)


class FakeYaml:
    """Stand-in for modules.util.YAML, as returned by Requests.file_yaml() - records whether save() was called."""

    def __init__(self, data=None):
        self.data = data if data is not None else {}
        self.saved = False

    def save(self):
        self.saved = True


class FakeRequests:
    def __init__(self, responses, config_data=None):
        self.local = "2.4.8-build5"
        self._responses = list(responses)
        self.gets = []
        self.posts = []
        self.deletes = []
        self.session = FakeSession(self)
        self._yaml = FakeYaml(config_data)

    def get(self, url, headers=None, params=None):
        self.gets.append((url, headers, params))
        return self._responses.pop(0)

    def post(self, url, json=None, headers=None):
        self.posts.append((url, json, headers))
        return self._responses.pop(0)

    def file_yaml(self, path):
        return self._yaml


class FakeConvert:
    """Stand-in for modules.convert.Convert, controllable per test."""

    def __init__(self, tvdb_to_tmdb_map=None, imdb_to_tmdb_map=None):
        self._tvdb_to_tmdb_map = tvdb_to_tmdb_map or {}
        self._imdb_to_tmdb_map = imdb_to_tmdb_map or {}

    def tvdb_to_tmdb(self, tvdb_id, fail=False):
        return self._tvdb_to_tmdb_map.get(tvdb_id)

    def imdb_to_tmdb(self, imdb_id, fail=False):
        return self._imdb_to_tmdb_map.get(imdb_id, (None, None))
