import pytest

import modules.simkl as simkl_module
from modules.simkl import Simkl
from modules.util import Failed
from tests.conftest import FakeLogger, FakeRequests, FakeResponse


@pytest.fixture(autouse=True)
def patch_logger(monkeypatch):
    monkeypatch.setattr(simkl_module, "logger", FakeLogger())


def make_tv_item(tmdb="95557", tvdb="368207", simkl_id=1151762):
    return {
        "title": "Invincible",
        "ids": {
            "simkl_id": simkl_id,
            "imdb": "tt6741278",
            "tvdb": tvdb,
            "tmdb": tmdb,
        },
    }


def make_movie_item(tmdb="550", simkl_id=28):
    return {
        "title": "Fight Club",
        "ids": {
            "simkl_id": simkl_id,
            "imdb": "tt0137523",
            "tmdb": tmdb,
        },
    }


def make_anime_item(tmdb="95479", tvdb="377543", simkl_id=2333706):
    return {
        "title": "Jujutsu Kaisen",
        "ids": {
            "simkl_id": simkl_id,
            "imdb": "tt12343534",
            "tvdb": tvdb,
            "tmdb": tmdb,
        },
    }


def make_dvd_item(tmdb=None, tvdb=None, simkl_id=1):
    ids = {"simkl_id": simkl_id}
    if tmdb:
        ids["tmdb"] = tmdb
    if tvdb:
        ids["tvdb"] = tvdb
    return {"title": "Some Title", "ids": ids}


BASE_URL = "https://utilities.kometa.wiki/simkl-service"

TRENDING_SMALL_URL = f"{BASE_URL}/trending/today/small"
TRENDING_WEEK_SMALL_URL = f"{BASE_URL}/trending/week/small"
TRENDING_MONTH_SMALL_URL = f"{BASE_URL}/trending/month/small"
TRENDING_LARGE_URL = f"{BASE_URL}/trending/today/large"
DVD_SMALL_URL = f"{BASE_URL}/dvd/small"
DVD_LARGE_URL = f"{BASE_URL}/dvd/large"


# ---------------------------------------------------------------------------
# validate_simkl_dict
# ---------------------------------------------------------------------------


class TestValidateSimklDict:
    def test_trending_defaults(self):
        simkl = Simkl(FakeRequests({}), None)
        result = simkl.validate_simkl_dict("Collection", "simkl_trending", 20)
        assert result == {"period": "today", "limit": 20}

    def test_trending_int_shorthand(self):
        simkl = Simkl(FakeRequests({}), None)
        result = simkl.validate_simkl_dict("Collection", "simkl_trending", 50)
        assert result == {"period": "today", "limit": 50}

    def test_trending_dict_with_period_and_limit(self):
        simkl = Simkl(FakeRequests({}), None)
        result = simkl.validate_simkl_dict("Collection", "simkl_trending", {"period": "week", "limit": 100})
        assert result == {"period": "week", "limit": 100}

    def test_trending_period_month(self):
        simkl = Simkl(FakeRequests({}), None)
        result = simkl.validate_simkl_dict("Collection", "simkl_trending", {"period": "month", "limit": 10})
        assert result["period"] == "month"

    def test_trending_invalid_period_raises(self):
        simkl = Simkl(FakeRequests({}), None)
        with pytest.raises(Failed, match="period"):
            simkl.validate_simkl_dict("Collection", "simkl_trending", {"period": "yesterday", "limit": 10})

    def test_dvd_defaults(self):
        simkl = Simkl(FakeRequests({}), None)
        result = simkl.validate_simkl_dict("Collection", "simkl_dvd", 20)
        assert result == {"limit": 20}

    def test_dvd_int_shorthand(self):
        simkl = Simkl(FakeRequests({}), None)
        result = simkl.validate_simkl_dict("Collection", "simkl_dvd", 75)
        assert result == {"limit": 75}

    def test_dvd_dict(self):
        simkl = Simkl(FakeRequests({}), None)
        result = simkl.validate_simkl_dict("Collection", "simkl_dvd", {"limit": 50})
        assert result == {"limit": 50}


# ---------------------------------------------------------------------------
# _request error handling
# ---------------------------------------------------------------------------


class TestRequest:
    def test_raises_on_http_error(self):
        simkl = Simkl(FakeRequests({TRENDING_SMALL_URL: FakeResponse({}, status_code=503)}), None)
        with pytest.raises(Failed, match="Simkl Error"):
            simkl._request("trending/today/small")


# ---------------------------------------------------------------------------
# get_simkl_ids — trending
# ---------------------------------------------------------------------------


class TestTrendingIds:
    def _simkl(self, response, url=TRENDING_SMALL_URL):
        return Simkl(FakeRequests({url: response}), None)

    def test_movie_library_returns_movie_tmdb_ids(self):
        response = {"movies": [make_movie_item("550"), make_movie_item("551")], "tv": [], "anime": []}
        ids = self._simkl(response).get_simkl_ids("simkl_trending", {"period": "today", "limit": 10}, is_movie=True)
        assert ids == [(550, "tmdb"), (551, "tmdb")]

    def test_show_library_returns_tv_and_anime_tmdb_show_ids(self):
        response = {"movies": [make_movie_item()], "tv": [make_tv_item("95557", "368207")], "anime": [make_anime_item("95479", "377543")]}
        ids = self._simkl(response).get_simkl_ids("simkl_trending", {"period": "today", "limit": 10}, is_movie=False)
        assert (95557, "tmdb_show") in ids
        assert (95479, "tmdb_show") in ids
        assert (550, "tmdb") not in ids

    def test_playlist_returns_movies_and_shows(self):
        response = {"movies": [make_movie_item("550")], "tv": [make_tv_item("95557", "368207")], "anime": []}
        ids = self._simkl(response).get_simkl_ids("simkl_trending", {"period": "today", "limit": 10}, is_movie=None)
        assert (550, "tmdb") in ids
        assert (95557, "tmdb_show") in ids

    def test_falls_back_to_tvdb_when_tmdb_missing(self):
        item = {"title": "No TMDb Show", "ids": {"simkl_id": 999, "tvdb": "368207"}}
        response = {"movies": [], "tv": [item], "anime": []}
        ids = self._simkl(response).get_simkl_ids("simkl_trending", {"period": "today", "limit": 10}, is_movie=False)
        assert ids == [(368207, "tvdb")]

    def test_skips_items_with_no_usable_ids(self):
        item = {"title": "No IDs", "ids": {"simkl_id": 999}}
        response = {"movies": [], "tv": [item], "anime": []}
        ids = self._simkl(response).get_simkl_ids("simkl_trending", {"period": "today", "limit": 10}, is_movie=False)
        assert ids == []

    def test_limit_is_respected(self):
        items = [make_tv_item(str(i), str(i)) for i in range(1, 21)]
        response = {"movies": [], "tv": items, "anime": []}
        ids = self._simkl(response).get_simkl_ids("simkl_trending", {"period": "today", "limit": 5}, is_movie=False)
        assert len(ids) == 5

    def test_large_endpoint_used_when_limit_exceeds_100(self):
        response = {"movies": [], "tv": [], "anime": []}
        simkl = Simkl(FakeRequests({TRENDING_LARGE_URL: response}), None)
        ids = simkl.get_simkl_ids("simkl_trending", {"period": "today", "limit": 101}, is_movie=False)
        assert ids == []

    def test_week_period_hits_correct_url(self):
        response = {"movies": [], "tv": [make_tv_item()], "anime": []}
        simkl = Simkl(FakeRequests({TRENDING_WEEK_SMALL_URL: response}), None)
        ids = simkl.get_simkl_ids("simkl_trending", {"period": "week", "limit": 10}, is_movie=False)
        assert (95557, "tmdb_show") in ids

    def test_month_period_hits_correct_url(self):
        response = {"movies": [], "tv": [make_tv_item()], "anime": []}
        simkl = Simkl(FakeRequests({TRENDING_MONTH_SMALL_URL: response}), None)
        ids = simkl.get_simkl_ids("simkl_trending", {"period": "month", "limit": 10}, is_movie=False)
        assert (95557, "tmdb_show") in ids

    def test_movie_ids_are_integers(self):
        response = {"movies": [make_movie_item("550")], "tv": [], "anime": []}
        ids = self._simkl(response).get_simkl_ids("simkl_trending", {"period": "today", "limit": 10}, is_movie=True)
        assert all(isinstance(id_val, int) for id_val, _ in ids)

    def test_empty_response_sections_return_empty(self):
        response = {"movies": [], "tv": [], "anime": []}
        ids = self._simkl(response).get_simkl_ids("simkl_trending", {"period": "today", "limit": 10}, is_movie=False)
        assert ids == []


# ---------------------------------------------------------------------------
# get_simkl_ids — dvd
# ---------------------------------------------------------------------------


class TestDvdIds:
    def _simkl(self, items, url=DVD_SMALL_URL):
        return Simkl(FakeRequests({url: items}), None)

    def test_movie_library_returns_movies_without_tvdb(self):
        items = [make_dvd_item(tmdb="550"), make_dvd_item(tmdb="551")]
        ids = self._simkl(items).get_simkl_ids("simkl_dvd", {"limit": 10}, is_movie=True)
        assert ids == [(550, "tmdb"), (551, "tmdb")]

    def test_show_library_returns_items_with_tvdb(self):
        items = [make_dvd_item(tmdb="95557", tvdb="368207")]
        ids = self._simkl(items).get_simkl_ids("simkl_dvd", {"limit": 10}, is_movie=False)
        assert ids == [(368207, "tvdb")]

    def test_movie_library_excludes_items_with_tvdb(self):
        items = [make_dvd_item(tmdb="95557", tvdb="368207"), make_dvd_item(tmdb="550")]
        ids = self._simkl(items).get_simkl_ids("simkl_dvd", {"limit": 10}, is_movie=True)
        assert ids == [(550, "tmdb")]

    def test_show_library_excludes_movies(self):
        items = [make_dvd_item(tmdb="550"), make_dvd_item(tmdb="95557", tvdb="368207")]
        ids = self._simkl(items).get_simkl_ids("simkl_dvd", {"limit": 10}, is_movie=False)
        assert ids == [(368207, "tvdb")]

    def test_playlist_returns_both_movies_and_shows(self):
        items = [make_dvd_item(tmdb="550"), make_dvd_item(tmdb="95557", tvdb="368207")]
        ids = self._simkl(items).get_simkl_ids("simkl_dvd", {"limit": 10}, is_movie=None)
        assert (550, "tmdb") in ids
        assert (368207, "tvdb") in ids

    def test_limit_is_respected(self):
        items = [make_dvd_item(tmdb=str(i), simkl_id=i) for i in range(1, 21)]
        ids = self._simkl(items).get_simkl_ids("simkl_dvd", {"limit": 5}, is_movie=True)
        assert len(ids) == 5

    def test_large_endpoint_used_when_limit_exceeds_100(self):
        simkl = Simkl(FakeRequests({DVD_LARGE_URL: []}), None)
        ids = simkl.get_simkl_ids("simkl_dvd", {"limit": 101}, is_movie=True)
        assert ids == []

    def test_skips_items_with_no_usable_ids(self):
        items = [make_dvd_item()]
        ids = self._simkl(items).get_simkl_ids("simkl_dvd", {"limit": 10}, is_movie=True)
        assert ids == []

    def test_ids_are_integers(self):
        items = [make_dvd_item(tmdb="550")]
        ids = self._simkl(items).get_simkl_ids("simkl_dvd", {"limit": 10}, is_movie=True)
        assert all(isinstance(id_val, int) for id_val, _ in ids)

    def test_empty_list_returns_empty(self):
        ids = self._simkl([]).get_simkl_ids("simkl_dvd", {"limit": 10}, is_movie=True)
        assert ids == []


# ---------------------------------------------------------------------------
# get_simkl_ids — unsupported method
# ---------------------------------------------------------------------------


def test_get_simkl_ids_raises_for_unknown_method():
    simkl = Simkl(FakeRequests({}), None)
    with pytest.raises(Failed, match="not supported"):
        simkl.get_simkl_ids("simkl_unknown", {}, is_movie=True)
