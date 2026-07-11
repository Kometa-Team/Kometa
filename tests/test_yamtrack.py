from modules.yamtrack import YamTrack


class FakeResponse:
    def __init__(self, content, url="https://yamtrack.example/list/1", status_code=200):
        self.content = content.encode("utf-8")
        self.url = url
        self.status_code = status_code


class FakeRequests:
    def __init__(self, html):
        self.html = html
        self.posts = []

    def get(self, url, **kwargs):
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
