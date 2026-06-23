import pytest
from bs4 import BeautifulSoup
from lxml import html

import modules.letterboxd as letterboxd_module
from modules.letterboxd import Letterboxd


class FakeLogger:
    def __init__(self):
        self.warning_messages = []
        self.info_messages = []
        self.error_messages = []

    def warning(self, message):
        self.warning_messages.append(str(message))

    def info(self, message=""):
        self.info_messages.append(str(message))

    def error(self, message):
        self.error_messages.append(str(message))

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class FakeCache:
    def __init__(self, initial=None):
        self.map = initial or {}
        self.updates = []

    def query_letterboxd_map(self, letterboxd_id):
        return self.map.get(letterboxd_id), False if letterboxd_id in self.map else None

    def update_letterboxd_map(self, expired, letterboxd_id, tmdb_id):
        self.map[letterboxd_id] = tmdb_id
        self.updates.append((letterboxd_id, tmdb_id))


class FakeRequests:
    def __init__(self, html_pages=None):
        self.html_pages = html_pages or {}

    def get_cloudscrape_html(self, url, language=None):
        return html.fromstring(self.html_pages.get(url, "<html><body></body></html>"))


class FakeList:
    payloads = {}

    def __init__(self, username, slug):
        data = self.payloads[(username, slug)]
        self.movies = data.get("movies", {})
        self.description = data.get("description")


class FakeFilms:
    payloads = {}
    calls = []

    def __init__(self, url, max=None):
        self.__class__.calls.append((url, max))
        movies = self.payloads[url]
        if max:
            movies = dict(list(movies.items())[:max])
        self.movies = movies


class FakeMovie:
    payloads = {}

    def __init__(self, slug):
        data = self.payloads[slug]
        self.tmdb_id = data.get("tmdb_id")
        self.rating = data.get("rating")


class FakeWatchlist:
    payloads = {}

    def __init__(self, username):
        data = self.payloads[username]
        self.movies = data.get("movies", {})


class FakeScraper:
    html_pages = {}

    @classmethod
    def get_page(cls, url):
        return BeautifulSoup(cls.html_pages[url], "lxml")


class FakeUser:
    payloads = {}

    def __init__(self, username):
        self.username = username
        if username not in self.payloads:
            raise KeyError(username)

    def get_lists(self):
        return self.payloads[self.username].get("lists", {})

    def get_films(self):
        return {"movies": self.payloads[self.username].get("films", {})}

    def get_reviews(self):
        return {"reviews": self.payloads[self.username].get("reviews", {})}


@pytest.fixture(autouse=True)
def patch_logger(monkeypatch):
    logger = FakeLogger()
    monkeypatch.setattr(letterboxd_module, "logger", logger)
    return logger


@pytest.fixture
def adapter(monkeypatch):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "Scraper", FakeScraper)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    monkeypatch.setattr(letterboxd_module, "Watchlist", FakeWatchlist)
    FakeFilms.calls = []
    return Letterboxd(FakeRequests(), FakeCache({"cached-film": 9001}))


def test_get_user_lists_sorts_name_and_builds_slug_urls(adapter):
    FakeUser.payloads = {
        "demo": {
            "lists": {
                "lists": [
                    {"title": "Bravo", "url": "https://letterboxd.com/demo/list/bravo/"},
                    {"title": "Alpha", "slug": "alpha"},
                ]
            }
        }
    }

    assert adapter.get_user_lists("demo", "name", "en") == [
        ("https://letterboxd.com/demo/list/alpha/", "Alpha"),
        ("https://letterboxd.com/demo/list/bravo/", "Bravo"),
    ]


def test_validate_letterboxd_lists_and_description_use_list_object(adapter):
    FakeList.payloads = {
        ("demo", "staff-picks"): {
            "description": "Staff picks",
            "movies": {
                "1": {"slug": "first-film", "year": 2001, "url": "https://letterboxd.com/film/first-film/"},
            },
        }
    }

    lists = adapter.validate_letterboxd_lists("Collection", "https://letterboxd.com/demo/list/staff-picks/", "en")

    assert lists == [
        {
            "url": "https://letterboxd.com/demo/list/staff-picks/",
            "limit": 0,
            "note": None,
            "rating": None,
            "year": None,
        }
    ]
    assert adapter.get_list_description("https://letterboxd.com/demo/list/staff-picks/", "en") == "Staff picks"


def test_list_fallback_extracts_movies_when_letterboxdpy_returns_empty(monkeypatch, patch_logger):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    FakeList.payloads = {
        ("demo", "staff-picks"): {
            "description": "Staff picks",
            "movies": {},
        }
    }
    requests = FakeRequests({"https://letterboxd.com/demo/list/staff-picks/": """
                <html><body>
                    <ul>
                        <li class="posteritem">
                            <div class="react-component" data-item-link="/film/first-film/" data-item-name="First Film (2001)" data-postered-identifier="{&quot;uid&quot;:&quot;film:111&quot;}"></div>
                        </li>
                        <li class="posteritem">
                            <div class="react-component" data-item-link="/film/second-film/" data-item-name="Second Film (2002)" data-postered-identifier="{&quot;uid&quot;:&quot;film:222&quot;}"></div>
                        </li>
                    </ul>
                </body></html>
            """})
    adapter = Letterboxd(requests, FakeCache())

    items = adapter._get_list_items("https://letterboxd.com/demo/list/staff-picks/", 0, "en")

    assert items == [
        ("111", "/film/first-film/", 2001, None, None),
        ("222", "/film/second-film/", 2002, None, None),
    ]
    assert any("using Kometa fallback parsing" in message for message in patch_logger.warning_messages)


def test_list_url_is_normalized_before_fallback(monkeypatch):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "Scraper", FakeScraper)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    FakeList.payloads = {
        ("demo", "staff-picks"): {
            "description": "Staff picks",
            "movies": {},
        }
    }
    requests = FakeRequests({"https://letterboxd.com/demo/list/staff-picks/": """
                <html><body>
                    <ul>
                        <li class="posteritem">
                            <div class="react-component" data-item-link="/film/first-film/" data-item-name="First Film (2001)" data-postered-identifier="{&quot;uid&quot;:&quot;film:111&quot;}"></div>
                        </li>
                    </ul>
                </body></html>
            """})
    adapter = Letterboxd(requests, FakeCache())

    items = adapter._get_list_items("https://letterboxd.com/demo/list/staff-picks", 0, "en")

    assert items == [("111", "/film/first-film/", 2001, None, None)]


def test_detail_list_url_extracts_rating_from_star_glyphs():
    requests = FakeRequests({"https://letterboxd.com/demo/list/staff-picks/detail/": """
                <html><body>
                    <article class="list-detailed-entry">
                        <div class="react-component" data-item-link="/film/first-film/" data-item-name="First Film (2001)" data-postered-identifier="{&quot;uid&quot;:&quot;film:111&quot;}"></div>
                        <div class="content-reactions-strip">
                            <span class="inline-symbol inline-rating">
                                <svg><title>&#9733;&#9733;&#9733;&#9733;&#189;</title></svg>
                            </span>
                        </div>
                    </article>
                </body></html>
            """})
    adapter = Letterboxd(requests, FakeCache())

    items = adapter._get_list_items("https://letterboxd.com/demo/list/staff-picks/detail/", 0, "en")

    assert items == [("111", "/film/first-film/", 2001, None, 9)]


def test_parse_list_url_accepts_detail_segment():
    adapter = Letterboxd(None, None)

    assert adapter._parse_list_url("https://letterboxd.com/demo/list/staff-picks/detail/") == ("demo", "staff-picks")
    assert adapter._parse_list_url("https://letterboxd.com/demo/list/staff-picks/detail/by/rating/") == ("demo", "staff-picks")


def test_request_html_retries_with_scraper_on_cloudflare_challenge(monkeypatch, patch_logger):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "Scraper", FakeScraper)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    requests = FakeRequests({"https://letterboxd.com/demo/list/staff-picks/": """
                <html><head><title>Just a moment...</title></head><body>Enable JavaScript and cookies to continue</body></html>
            """})
    FakeScraper.html_pages = {"https://letterboxd.com/demo/list/staff-picks/": """
            <html><body><div data-film-id="111" data-item-link="/film/first-film/" data-item-name="First Film (2001)"></div></body></html>
        """}
    adapter = Letterboxd(requests, FakeCache())

    response = adapter._request_html("https://letterboxd.com/demo/list/staff-picks/", "en")

    assert response.xpath("//div[@data-film-id]/@data-film-id") == ["111"]
    assert any("retrying with curl_cffi" in message for message in patch_logger.warning_messages)


def test_get_tmdb_ids_for_films_page_respects_filters_and_cache(adapter):
    FakeFilms.payloads = {
        "https://letterboxd.com/films/popular/": {
            "cached-film": {"slug": "cached-film", "year": 1999, "rating": 4.5, "url": "https://letterboxd.com/film/cached-film/"},
            "new-film": {"slug": "new-film", "year": 2005, "rating": 4.0, "url": "https://letterboxd.com/film/new-film/"},
            "old-film": {"slug": "old-film", "year": 1985, "rating": 4.2, "url": "https://letterboxd.com/film/old-film/"},
        }
    }
    FakeMovie.payloads = {"new-film": {"tmdb_id": 1002}, "old-film": {"tmdb_id": 1003}}

    ids = adapter.get_tmdb_ids(
        "letterboxd_list",
        {"url": "https://letterboxd.com/films/popular/", "limit": 0, "note": None, "rating": "8-10", "year": "1990-2010"},
        "en",
    )

    assert ids == [(9001, "tmdb"), (1002, "tmdb")]
    assert adapter.cache.updates == [("new-film", 1002)]


def test_watchlist_url_is_supported_through_letterboxd_list(adapter):
    FakeWatchlist.payloads = {
        "demo": {
            "movies": {
                "watch-1": {"slug": "watch-1", "year": 2008, "url": "https://letterboxd.com/film/watch-1/"},
                "watch-2": {"slug": "watch-2", "year": 2010, "url": "https://letterboxd.com/film/watch-2/"},
            }
        }
    }
    FakeMovie.payloads = {"watch-1": {"tmdb_id": 4001}, "watch-2": {"tmdb_id": 4002}}

    lists = adapter.validate_letterboxd_lists("Collection", "https://letterboxd.com/demo/watchlist", "en")
    ids = adapter.get_tmdb_ids(
        "letterboxd_list",
        {"url": "https://letterboxd.com/demo/watchlist", "limit": 0, "note": None, "rating": None, "year": "2005-2015"},
        "en",
    )

    assert lists == [
        {
            "url": "https://letterboxd.com/demo/watchlist",
            "limit": 0,
            "note": None,
            "rating": None,
            "year": None,
        }
    ]
    assert ids == [(4001, "tmdb"), (4002, "tmdb")]


def test_watchlist_falls_back_when_letterboxdpy_returns_empty(monkeypatch, patch_logger):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "Scraper", FakeScraper)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    monkeypatch.setattr(letterboxd_module, "Watchlist", FakeWatchlist)
    FakeWatchlist.payloads = {"demo": {"movies": {}}}
    requests = FakeRequests({"https://letterboxd.com/demo/watchlist/": """
                <html><body>
                    <ul>
                        <li class="griditem">
                            <div class="react-component" data-item-link="/film/watch-fallback/" data-item-name="Watch Fallback (2023)" data-postered-identifier="{&quot;uid&quot;:&quot;film:555&quot;}"></div>
                        </li>
                    </ul>
                </body></html>
            """})
    adapter = Letterboxd(requests, FakeCache())

    items = adapter._get_list_items("https://letterboxd.com/demo/watchlist", 0, "en")

    assert items == [("555", "/film/watch-fallback/", 2023, None, None)]
    assert any("watchlist" in message and "using Kometa fallback parsing" in message for message in patch_logger.warning_messages)


def test_validate_global_letterboxd_films_page_samples_single_item(adapter):
    FakeFilms.payloads = {
        "https://letterboxd.com/films/popular/": {
            "film-1": {"slug": "film-1", "year": 2001, "rating": 0.5, "url": "https://letterboxd.com/film/film-1/"},
            "film-2": {"slug": "film-2", "year": 2002, "rating": 0.5, "url": "https://letterboxd.com/film/film-2/"},
        }
    }

    lists = adapter.validate_letterboxd_lists("Collection", "https://letterboxd.com/films/popular/", "en")

    assert lists == [
        {
            "url": "https://letterboxd.com/films/popular/",
            "limit": 0,
            "note": None,
            "rating": None,
            "year": None,
        }
    ]
    assert FakeFilms.calls == [("https://letterboxd.com/films/popular/", 1)]


def test_user_scoped_films_url_uses_fallback_not_letterboxdpy(monkeypatch, patch_logger):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "Scraper", FakeScraper)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    FakeFilms.calls = []
    requests = FakeRequests({"https://letterboxd.com/raphh11/films/rated/0.5/": """
                <html><body>
                    <ul>
                        <li class="griditem">
                            <div class="react-component" data-film-id="501" data-item-slug="half-star-one" data-item-name="Half Star One (1999)"></div>
                            <p class="poster-viewingdata"><span class="rating rated-1"></span></p>
                        </li>
                    </ul>
                </body></html>
            """})
    adapter = Letterboxd(requests, FakeCache())

    items = adapter._get_list_items("https://letterboxd.com/raphh11/films/rated/0.5/", 0, "en")

    assert items == [("501", "/film/half-star-one/", 1999, None, 1)]
    assert FakeFilms.calls == []
    assert any("user-scoped films URLs" in message for message in patch_logger.warning_messages)


def test_user_scoped_films_fallback_extracts_direct_react_components(monkeypatch):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "Scraper", FakeScraper)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    requests = FakeRequests({"https://letterboxd.com/raphh11/films/rated/0.5/": """
                <html><body>
                    <section>
                        <div class="react-component poster" data-item-link="/film/direct-react/" data-item-name="Direct React (1988)" data-postered-identifier="{&quot;uid&quot;:&quot;film:777&quot;}"></div>
                    </section>
                </body></html>
            """})
    adapter = Letterboxd(requests, FakeCache())

    items = adapter._get_list_items("https://letterboxd.com/raphh11/films/rated/0.5/", 0, "en")

    assert items == [("777", "/film/direct-react/", 1988, None, None)]


def test_validate_user_pages_disables_incremental_and_preserves_filters(adapter, patch_logger):
    FakeUser.payloads = {"reviewer": {"reviews": {}}}

    pages = adapter.validate_letterboxd_user_pages(
        "Collection",
        {"username": "reviewer", "incremental": True, "sort_by": "user_rating_highest", "min_rating": 8},
        "reviews",
        "en",
    )

    assert pages == [
        {
            "username": "reviewer",
            "sort_by": "user_rating_highest",
            "incremental": False,
            "min_rating": 8,
            "limit": 0,
            "note": None,
            "year": None,
        }
    ]
    assert any("disabling incremental parsing" in message for message in patch_logger.warning_messages)
    assert any("using the default page order" in message for message in patch_logger.warning_messages)


def test_get_tmdb_ids_for_user_reviews_filters_review_content(adapter):
    FakeUser.payloads = {
        "reviewer": {
            "reviews": {
                "r1": {
                    "movie": {"id": "review-film-1", "slug": "review-film-1", "release": 2004},
                    "rating": 4.5,
                    "review": {"content": "great practical effects"},
                    "date": "2026-01-01T00:00:00.000000Z",
                },
                "r2": {
                    "movie": {"id": "review-film-2", "slug": "review-film-2", "release": 2004},
                    "rating": 3.0,
                    "review": {"content": "fine"},
                    "date": "2026-01-02T00:00:00.000000Z",
                },
            }
        }
    }
    FakeMovie.payloads = {"review-film-1": {"tmdb_id": 2001}, "review-film-2": {"tmdb_id": 2002}}

    ids = adapter.get_tmdb_ids(
        "letterboxd_user_reviews",
        {"username": "reviewer", "sort_by": "release_date_newest", "incremental": False, "min_rating": 8, "limit": 0, "note": "practical", "year": "2000-2010"},
        "en",
    )

    assert ids == [(2001, "tmdb")]


def test_user_reviews_limit_applies_after_filters(adapter):
    FakeUser.payloads = {
        "reviewer": {
            "reviews": {
                "r1": {
                    "movie": {"id": "review-film-1", "slug": "review-film-1", "release": 2004},
                    "rating": 2.0,
                    "review": {"content": "skip me"},
                    "date": "2026-01-01T00:00:00.000000Z",
                },
                "r2": {
                    "movie": {"id": "review-film-2", "slug": "review-film-2", "release": 2004},
                    "rating": 4.5,
                    "review": {"content": "keep me"},
                    "date": "2026-01-02T00:00:00.000000Z",
                },
            }
        }
    }
    FakeMovie.payloads = {"review-film-2": {"tmdb_id": 2002}}

    ids = adapter.get_tmdb_ids(
        "letterboxd_user_reviews",
        {"username": "reviewer", "sort_by": "release_date_newest", "incremental": False, "min_rating": 8, "limit": 1, "note": "keep", "year": "2000-2010"},
        "en",
    )

    assert ids == [(2002, "tmdb")]


def test_get_tmdb_ids_for_user_films_ignores_unsupported_note_filter(adapter, patch_logger):
    FakeUser.payloads = {
        "watcher": {
            "films": {
                "watch-film-1": {"id": "watch-film-1", "year": 2020, "rating": 4.5},
                "watch-film-2": {"id": "watch-film-2", "year": 2010, "rating": 3.0},
            }
        }
    }
    FakeMovie.payloads = {"watch-film-1": {"tmdb_id": 3001}, "watch-film-2": {"tmdb_id": 3002}}

    ids = adapter.get_tmdb_ids(
        "letterboxd_user_films",
        {"username": "watcher", "sort_by": "release_date_newest", "incremental": False, "min_rating": 8, "limit": 0, "note": "ignored", "year": "2015-2025"},
        "en",
    )

    assert ids == [(3001, "tmdb")]
    assert any("ignoring note filter" in message for message in patch_logger.warning_messages)


def test_user_films_limit_applies_after_filters(adapter, patch_logger):
    FakeUser.payloads = {
        "watcher": {
            "films": {
                "watch-film-1": {"id": "watch-film-1", "year": 1995, "rating": 4.5},
                "watch-film-2": {"id": "watch-film-2", "year": 2020, "rating": 4.5},
            }
        }
    }
    FakeMovie.payloads = {"watch-film-2": {"tmdb_id": 3002}}

    ids = adapter.get_tmdb_ids(
        "letterboxd_user_films",
        {"username": "watcher", "sort_by": "release_date_newest", "incremental": False, "min_rating": 8, "limit": 1, "note": None, "year": "2015-2025"},
        "en",
    )

    assert ids == [(3002, "tmdb")]


def test_user_reviews_fallback_extracts_review_entries(monkeypatch, patch_logger):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "Scraper", FakeScraper)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    FakeUser.payloads = {"reviewer": {"reviews": {}}}
    requests = FakeRequests({"https://letterboxd.com/reviewer/films/reviews/": """
                <html><body>
                    <div class="viewing-list">
                        <div class="film-detail">
                            <div class="react-component" data-film-id="444" data-item-slug="review-fallback" data-item-name="Review Fallback (2006)"></div>
                            <article data-object-id="review:1">
                                <a href="/reviewer/film/review-fallback/">Review Fallback</a>
                                <span>2006</span>
                                <span class="rating rated-9"></span>
                                <div class="body-text js-review-body"><p>Fantastic work</p></div>
                                <span class="date"><time datetime="2026-02-03T00:00:00Z"></time></span>
                            </article>
                        </div>
                    </div>
                </body></html>
            """})
    adapter = Letterboxd(requests, FakeCache())

    items = adapter._get_user_entries("reviewer", "reviews", "en")

    assert items == [("444", "/film/review-fallback/", 2006, "Fantastic work", 9, "2026-02-03T00:00:00.000000Z")]
    assert any("using Kometa fallback parsing" in message for message in patch_logger.warning_messages)


def test_user_films_fallback_extracts_watched_entries(monkeypatch, patch_logger):
    monkeypatch.setattr(letterboxd_module, "Films", FakeFilms)
    monkeypatch.setattr(letterboxd_module, "LetterboxdList", FakeList)
    monkeypatch.setattr(letterboxd_module, "Movie", FakeMovie)
    monkeypatch.setattr(letterboxd_module, "Scraper", FakeScraper)
    monkeypatch.setattr(letterboxd_module, "User", FakeUser)
    FakeUser.payloads = {"watcher": {"films": {}}}
    requests = FakeRequests({"https://letterboxd.com/watcher/films/": """
                <html><body>
                    <ul>
                        <li class="griditem">
                            <div class="react-component" data-film-id="333" data-item-slug="film-fallback" data-item-name="Film Fallback (2021)"></div>
                            <p class="poster-viewingdata">
                                <span class="rating rated-8"></span>
                                <span class="like"></span>
                            </p>
                        </li>
                    </ul>
                </body></html>
            """})
    adapter = Letterboxd(requests, FakeCache())

    items = adapter._get_user_entries("watcher", "films", "en")

    assert items == [("333", "/film/film-fallback/", 2021, None, 8, None)]
    assert any("using Kometa fallback parsing" in message for message in patch_logger.warning_messages)
