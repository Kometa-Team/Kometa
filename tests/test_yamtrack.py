import pytest

from modules.util import Failed
from modules.yamtrack import YamTrack


class FakeResponse:
    def __init__(self, content, url="https://yamtrack.example/list/1", status_code=200):
        self.content = content.encode("utf-8")
        self.url = url
        self.status_code = status_code


class FakeRequests:
    def __init__(self, html):
        self.html = html
        self.gets = []
        self.posts = []

    def get(self, url, **kwargs):
        self.gets.append((url, kwargs))
        return FakeResponse(self.html, url=url)

    def post(self, url, **kwargs):
        self.posts.append((url, kwargs))
        return FakeResponse("", url="https://yamtrack.example/")


def get_yamtrack(html):
    return YamTrack(FakeRequests(html), {"url": "https://yamtrack.example", "username": "user", "password": "pass"})


def test_yamtrack_list_extracts_tmdb_movie_and_show_ids():
    html = """
    <a href="/details/tmdb/movie/550/fight-club">Fight Club</a>
    <a href="/details/tmdb/tv/1396/breaking-bad">Breaking Bad</a>
    <a href="/details/tmdb/tv/1396/breaking-bad">Duplicate</a>
    """

    assert get_yamtrack(html).get_tmdb_ids("yamtrack_list", "https://yamtrack.example/list/1") == [(550, "tmdb"), (1396, "tmdb_show")]


def test_yamtrack_list_filters_by_library_type():
    html = """
    <a href="/details/tmdb/movie/550/fight-club">Fight Club</a>
    <a href="/details/tmdb/tv/1396/breaking-bad">Breaking Bad</a>
    """
    yamtrack = get_yamtrack(html)

    assert yamtrack.get_tmdb_ids("yamtrack_list", "https://yamtrack.example/list/1", is_movie=True) == [(550, "tmdb")]
    assert yamtrack.get_tmdb_ids("yamtrack_list", "https://yamtrack.example/list/1", is_movie=False) == [(1396, "tmdb_show")]


def test_yamtrack_rejects_lookalike_hosts():
    with pytest.raises(Failed, match="must start with https://yamtrack.example"):
        get_yamtrack("").get_tmdb_ids("yamtrack_list", "https://yamtrack.example.evil/list/1")


def test_yamtrack_list_details_extracts_description():
    html = '<textarea name="description">this is a test wow</textarea>'

    assert get_yamtrack(html).list_description("https://yamtrack.example/list/1") == "this is a test wow"


def test_yamtrack_login_posts_django_allauth_fields():
    login_html = """
    <form method="post" action="/accounts/login/">
      <input type="hidden" name="csrfmiddlewaretoken" value="token">
      <input type="text" name="login">
      <input type="password" name="password">
      <input type="hidden" name="next" value="/list/1">
    </form>
    """
    requests = FakeRequests(login_html)
    yamtrack = YamTrack(requests, {"url": "https://yamtrack.example", "username": "user", "password": "pass"})

    yamtrack._login("/list/1")

    assert requests.posts[0][0] == "https://yamtrack.example/accounts/login/"
    assert requests.posts[0][1]["data"] == {
        "login": "user",
        "username": "user",
        "password": "pass",
        "next": "/list/1",
        "csrfmiddlewaretoken": "token",
    }


def test_yamtrack_tracked_extracts_enabled_statuses():
    html = """
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/movie/550/fight-club">Fight Club</a>
      <div class="w-4 h-4 text-red-400"></div>
    </div>
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/tv/80350/new-amsterdam">New Amsterdam</a>
      <div class="w-4 h-4 text-sky-400"></div>
    </div>
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/tv/60574/peaky-blinders"
         class="text-sm font-semibold text-white hover:text-indigo-400">Peaky Blinders</a>
      <div class="w-4 h-4 text-indigo-400"></div>
    </div>
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/tv/93405/squid-game">Squid Game</a>
      <div class="w-4 h-4 text-orange-400"></div>
    </div>
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/tv/48866/the-100">The 100</a>
      <div class="w-4 h-4 text-emerald-400"></div>
    </div>
    """
    requests = FakeRequests(html)
    yamtrack = YamTrack(requests, {"url": "https://yamtrack.example", "username": "user", "password": "pass"})
    tracked = yamtrack.validate_tracked(
        "Collection",
        {
            "movies": {"dropped": False, "planning": True, "in_progress": True, "paused": False, "completed": False},
            "tv_shows": {"dropped": False, "planning": True, "in_progress": True, "paused": False, "completed": False},
        },
    )

    assert yamtrack.get_tracked_tmdb_ids(tracked) == [(80350, "tmdb_show"), (60574, "tmdb_show")]
    assert requests.gets[0][0] == "https://yamtrack.example/user/movie"
    assert requests.gets[1][0] == "https://yamtrack.example/user/tv"


def test_yamtrack_tracked_filters_by_library_type():
    html = """
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/movie/550/fight-club">Fight Club</a>
      <div class="w-4 h-4 text-sky-400"></div>
    </div>
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/tv/80350/new-amsterdam">New Amsterdam</a>
      <div class="w-4 h-4 text-sky-400"></div>
    </div>
    """
    yamtrack = get_yamtrack(html)
    tracked = yamtrack.validate_tracked("Collection", {"movies": {"planning": True}, "tv_shows": {"planning": True}})

    assert yamtrack.get_tracked_tmdb_ids(tracked, is_movie=True) == [(550, "tmdb")]
    assert yamtrack.get_tracked_tmdb_ids(tracked, is_movie=False) == [(80350, "tmdb_show")]


def test_yamtrack_tracked_sections_are_optional():
    html = """
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/movie/550/fight-club">Fight Club</a>
      <div class="w-4 h-4 text-sky-400"></div>
    </div>
    """
    requests = FakeRequests(html)
    yamtrack = YamTrack(requests, {"url": "https://yamtrack.example", "username": "user", "password": "pass"})
    tracked = yamtrack.validate_tracked("Collection", {"movies": {"planning": True}})

    assert yamtrack.get_tracked_tmdb_ids(tracked) == [(550, "tmdb")]
    assert [get[0] for get in requests.gets] == ["https://yamtrack.example/user/movie"]
    assert all(enabled is False for enabled in tracked["anime"].values())


def test_yamtrack_tracked_statuses_default_true_when_section_exists():
    html = """
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/movie/550/fight-club">Fight Club</a>
      <div class="w-4 h-4 text-red-400"></div>
    </div>
    <div x-data="{ trackOpen: false }">
      <a href="/details/tmdb/movie/551/another-movie">Another Movie</a>
      <div class="w-4 h-4 text-emerald-400"></div>
    </div>
    """
    requests = FakeRequests(html)
    yamtrack = YamTrack(requests, {"url": "https://yamtrack.example", "username": "user", "password": "pass"})
    tracked = yamtrack.validate_tracked("Collection", {"movies": {}})

    assert all(enabled is True for enabled in tracked["movies"].values())
    assert all(enabled is False for enabled in tracked["tv_shows"].values())
    assert all(enabled is False for enabled in tracked["anime"].values())
    assert yamtrack.get_tracked_tmdb_ids(tracked) == [(550, "tmdb"), (551, "tmdb")]


def test_yamtrack_tracked_extracts_anime_mal_ids():
    html = """
    <tr x-data="{ trackOpen: false }">
      <td><a href="/details/mal/anime/813/dragon-ball-z">Dragon Ball Z</a></td>
      <td class="p-2 text-center">Planning</td>
    </tr>
    <tr x-data="{ trackOpen: false }">
      <td><a href="/details/mal/anime/14837/dragon-ball-z-movie-14-kami-to-kami">Dragon Ball Z Movie 14: Kami to Kami</a></td>
      <td class="p-2 text-center">Completed</td>
    </tr>
    <tr x-data="{ trackOpen: false }">
      <td><a href="/details/mal/anime/902/dragon-ball-z-movie-09">Dragon Ball Z Movie 09</a></td>
      <td class="p-2 text-center">Paused</td>
    </tr>
    """
    requests = FakeRequests(html)
    yamtrack = YamTrack(requests, {"url": "https://yamtrack.example", "username": "user", "password": "pass"})
    tracked = yamtrack.validate_tracked("Collection", {"anime": {"planning": True, "completed": True, "paused": False}})

    ids, mal_ids = yamtrack.get_tracked_ids(tracked)

    assert ids == []
    assert mal_ids == [813, 14837]
    assert [get[0] for get in requests.gets] == ["https://yamtrack.example/user/anime"]


def test_yamtrack_tracked_anime_is_valid_for_movie_and_show_libraries():
    yamtrack = get_yamtrack("")

    movie_tracked = yamtrack.validate_tracked("Collection", {"anime": {"planning": True}}, is_movie=True)
    show_tracked = yamtrack.validate_tracked("Collection", {"anime": {"planning": True}}, is_movie=False)

    assert movie_tracked["anime"]["planning"] is True
    assert show_tracked["anime"]["planning"] is True
    assert all(enabled is False for enabled in movie_tracked["tv_shows"].values())
    assert all(enabled is False for enabled in show_tracked["movies"].values())


def test_yamtrack_tracked_validation_is_limited_to_library_type():
    yamtrack = get_yamtrack("")

    movie_tracked = yamtrack.validate_tracked("Collection", {"movies": {"planning": True}, "tv_shows": {"planning": "bad"}}, is_movie=True)
    show_tracked = yamtrack.validate_tracked("Collection", {"movies": {"planning": "bad"}, "tv_shows": {"planning": True}}, is_movie=False)

    assert movie_tracked["movies"]["planning"] is True
    assert all(enabled is False for enabled in movie_tracked["tv_shows"].values())
    assert all(enabled is False for enabled in movie_tracked["anime"].values())
    assert show_tracked["tv_shows"]["planning"] is True
    assert all(enabled is False for enabled in show_tracked["movies"].values())
    assert all(enabled is False for enabled in show_tracked["anime"].values())


def test_yamtrack_tracked_present_section_must_be_dictionary():
    yamtrack = get_yamtrack("")

    with pytest.raises(Failed, match="yamtrack_tracked anime must be a dictionary"):
        yamtrack.validate_tracked("Collection", {"anime": True}, is_movie=True)
