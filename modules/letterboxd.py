import re
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen

from lxml import html as lxml_html

from modules import util
from modules.util import Failed

logger = util.logger

try:
    from letterboxdpy.core.scraper import Scraper
    from letterboxdpy.films import Films
    from letterboxdpy.list import List as LetterboxdList
    from letterboxdpy.movie import Movie
    from letterboxdpy.user import User
    from letterboxdpy.watchlist import Watchlist
except ImportError:
    Films = None
    LetterboxdList = None
    Movie = None
    Scraper = None
    User = None
    Watchlist = None

sort_options = {
    "name": "by/name/",
    "popularity": "by/popular/",
    "newest": "by/newest/",
    "oldest": "by/oldest/",
    "updated": "",
}

user_sort_options = {
    "release_date_newest": "by/release/",
    "release_date_earliest": "by/release-earliest/",
    "name": "by/name/",
    "popularity": "by/popular/",
    "when_added_newest": "by/added/",
    "when_added_earliest": "by/added-earliest/",
    "when_rated_newest": "by/rated/",
    "when_rated_earliest": "by/rated-earliest/",
    "average_rating_highest": "by/rating/",
    "average_rating_lowest": "by/rating-lowest/",
    "user_rating_highest": "by/your-rating/",
    "user_rating_lowest": "by/your-rating-lowest/",
    "length_shortest": "by/shortest/",
    "length_longest": "by/longest/",
}

builders = ["letterboxd_list", "letterboxd_list_details", "letterboxd_user_films", "letterboxd_user_films_details", "letterboxd_user_reviews", "letterboxd_user_reviews_details"]
base_url = "https://letterboxd.com"
boxd_short_url = "https://boxd.it"

list_url_pattern = re.compile(r"^https://letterboxd\.com/(?P<username>[^/]+)/list/(?P<slug>[^/]+)" r"(?:/share/(?P<share>[^/]+))?" r"(?:/detail)?" r"(?:/by/(?P<sort>[^/]+))?" r"/?$")
watchlist_url_pattern = re.compile(r"^https://letterboxd\.com/(?P<username>[^/]+)/watchlist/?$")
film_path_pattern = re.compile(r"^/film/(?P<slug>[^/]+)/?$")
film_identifier_pattern = re.compile(r"film:(?P<id>\d+)")
page_path_pattern = re.compile(r"/page/\d+/?$")
year_pattern = re.compile(r"\((\d{4})\)")


class Letterboxd:
    def __init__(self, requests, cache=None):
        self.requests = requests
        self.cache = cache
        self._warned = set()
        self._films_cls = Films
        self._list_cls = LetterboxdList
        self._movie_cls = Movie
        self._scraper_cls = Scraper
        self._user_cls = User
        self._watchlist_cls = Watchlist

    def _require_library(self):
        if not all([self._films_cls, self._list_cls, self._movie_cls, self._scraper_cls, self._user_cls, self._watchlist_cls]):
            raise Failed("Letterboxd Error: letterboxdpy is required. Install the pinned project dependency and try again.")

    def _info_once(self, key, message):
        if key not in self._warned:
            logger.info(message)
            self._warned.add(key)

    def _warn_once(self, key, message):
        if key not in self._warned:
            logger.warning(message)
            self._warned.add(key)

    def _url_type(self, url):
        parsed = urlparse(url)
        if "/films/" in parsed.path:
            return "films"
        if parsed.path.rstrip("/").endswith("/watchlist"):
            return "watchlist"
        return "list"

    @staticmethod
    def _uses_letterboxdpy_films(url):
        parsed = urlparse(url)
        return parsed.path.startswith("/films/")

    @staticmethod
    def _resolve_boxd_url(url):
        url = url.strip()
        parsed = urlparse(url)

        if parsed.netloc.lower() not in ["boxd.it", "www.boxd.it"]:
            return url

        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            with urlopen(request, timeout=15) as response:
                resolved_url = response.geturl()
        except Exception as e:
            raise Failed(f"Letterboxd Error: Failed to resolve short Letterboxd URL {url}: {e}") from e

        if not resolved_url.startswith(base_url):
            raise Failed(f"Letterboxd Error: Short Letterboxd URL {url} resolved to unsupported URL: {resolved_url}")

        return resolved_url

    @staticmethod
    def _normalize_url(url):
        url = Letterboxd._resolve_boxd_url(url.strip())
        parsed = urlparse(url)
        path = parsed.path if parsed.path.endswith("/") else f"{parsed.path}/"
        return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))

    @staticmethod
    def _warning_url_key(url):
        parsed = urlparse(url)
        path = page_path_pattern.sub("/", parsed.path)
        if path != "/" and not path.endswith("/"):
            path = f"{path}/"
        return urlunparse((parsed.scheme, parsed.netloc.lower(), path.lower(), "", "", ""))

    def _parse_list_url(self, list_url):
        match = list_url_pattern.match(list_url.strip())
        if not match:
            raise Failed(f"Letterboxd Error: Unsupported list URL: {list_url}")
        return match.group("username"), match.group("slug")

    def _parse_watchlist_url(self, watchlist_url):
        match = watchlist_url_pattern.match(watchlist_url.strip())
        if not match:
            raise Failed(f"Letterboxd Error: Unsupported watchlist URL: {watchlist_url}")
        return match.group("username")

    def _slug_path(self, url):
        parsed = urlparse(url if url.startswith("http") else f"{base_url}{url}")
        match = film_path_pattern.match(parsed.path)
        if not match:
            raise Failed(f"Letterboxd Error: Could not determine film slug from {url}")
        return f"/film/{match.group('slug')}/"

    def _request_html(self, url, language):
        if not self.requests:
            raise Failed("Letterboxd Error: Requests client unavailable for Letterboxd fallback parsing")
        logger.trace(f"URL: {url}")
        response = self.requests.get_cloudscrape_html(url, language=language)
        if self._is_cloudflare_challenge(response):
            self._warn_once(("cloudflare_fetch", self._warning_url_key(url)), f"Letterboxd Warning: cloudscraper hit a Cloudflare challenge for {self._warning_url_key(url)}; retrying with curl_cffi.")
            return self._request_html_with_scraper(url)
        return response

    @staticmethod
    def _is_cloudflare_challenge(response):
        title = response.xpath("string(//title)")
        body_text = " ".join(t.strip() for t in response.xpath("//body//text()") if t and t.strip())
        return bool(title and "just a moment" in title.lower() or body_text and "enable javascript and cookies to continue" in body_text.lower())

    def _request_html_with_scraper(self, url):
        self._require_library()
        try:
            soup = self._scraper_cls.get_page(url)
        except Exception as e:
            raise Failed(f"Letterboxd Error: Failed to load {url} with curl_cffi fallback: {e}") from e
        return lxml_html.fromstring(str(soup))

    @staticmethod
    def _first_xpath_value(element, xpath):
        values = element.xpath(xpath)
        if isinstance(values, list):
            return values[0] if values else None
        return values

    def _extract_film_id(self, element):
        film_id = self._first_xpath_value(element, "@data-film-id")
        if film_id:
            return str(film_id)

        posted_identifier = self._first_xpath_value(element, "@data-postered-identifier")
        if not posted_identifier:
            return None

        match = film_identifier_pattern.search(posted_identifier)
        return match.group("id") if match else None

    def _extract_slug(self, element):
        for attr in ["data-target-link", "data-film-link", "data-item-link"]:
            slug = self._first_xpath_value(element, f"@{attr}")
            if slug and slug != "/":
                return self._slug_path(slug)

        slug = self._first_xpath_value(element, "@data-item-slug | @data-film-slug")
        if slug:
            return f"/film/{slug}/"
        return None

    def _extract_year(self, element):
        year = self._first_xpath_value(element, "@data-film-release-year | @data-release-year")
        if year:
            return self._coerce_year(year)

        item_name = self._first_xpath_value(element, "@data-item-name | @data-item-full-display-name")
        if item_name:
            match = year_pattern.search(item_name)
            if match:
                return self._coerce_year(match.group(1))

        for text in element.xpath(".//span/text() | .//small/text()"):
            stripped = text.strip()
            if stripped.isdigit() and len(stripped) == 4:
                return self._coerce_year(stripped)
        return None

    @staticmethod
    def _extract_rating_from_classes(class_values):
        for class_value in class_values:
            for class_name in class_value.split():
                if class_name.startswith("rated-") and class_name.split("-")[-1].isdigit():
                    return int(class_name.split("-")[-1])
                if "rating" in class_name and "-" in class_name:
                    suffix = class_name.split("-")[-1]
                    if suffix.isdigit():
                        return int(suffix)
        return None

    @staticmethod
    def _extract_rating_from_stars(star_values):
        for star_value in star_values:
            if not star_value or "★" not in star_value:
                continue
            full_stars = star_value.count("★")
            half_star = 1 if "½" in star_value else 0
            return full_stars * 2 + half_star
        return None

    @staticmethod
    def _extract_like_from_classes(class_values):
        return any("like" in class_name for class_value in class_values for class_name in class_value.split())

    def _extract_review_text(self, article):
        review = self._first_xpath_value(
            article,
            ".//div[contains(@class,'body-text') or contains(@class,'js-review-body') or contains(@class,'activity-list-description')]",
        )
        if review is None:
            return None

        paragraphs = [p.strip() for p in review.xpath(".//p//text()") if p.strip()]
        filtered = [p for p in paragraphs if "contains spoilers" not in p.lower()]
        if filtered:
            return "\n".join(filtered)

        text = " ".join(t.strip() for t in review.xpath(".//text()") if t.strip())
        return text or None

    @staticmethod
    def _normalize_fallback_date(value):
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
        except ValueError:
            pass

        try:
            dt = datetime.strptime(value, "%d %b %Y")
            return dt.strftime("%Y-%m-%dT00:00:00.000000Z")
        except ValueError:
            return value

    def _fallback_item_tuple(self, film_id, slug, year):
        return str(film_id), self._slug_path(slug), self._coerce_year(year), None, None

    def _extract_fallback_react_component(self, element):
        film_id = self._extract_film_id(element)
        slug = self._extract_slug(element)
        if not film_id or not slug:
            return None

        return self._fallback_item_tuple(film_id, slug, self._extract_year(element))

    def _extract_fallback_list_page(self, page_url, language):
        response = self._request_html(page_url, language)
        items = []
        for element in response.xpath("//div[@data-film-id] | //li[contains(@class,'posteritem')]//div[contains(@class,'react-component')]"):
            item = self._extract_fallback_react_component(element)
            if item:
                items.append(item)
        next_url = response.xpath("//a[contains(@class, 'next')]/@href")
        return items, next_url[0] if next_url else None

    def _extract_fallback_list_detail_page(self, page_url, language):
        response = self._request_html(page_url, language)
        items = []
        for article in response.xpath("//article[contains(@class,'list-detailed-entry')]"):
            react = self._first_xpath_value(article, ".//div[contains(@class,'react-component')]")
            if react is None:
                continue
            film_id = self._extract_film_id(react)
            slug = self._extract_slug(react)
            if not film_id or not slug:
                continue
            star_values = article.xpath(".//span[contains(@class,'inline-rating')]//title/text()")
            rating = self._extract_rating_from_stars(star_values)
            note = self._extract_review_text(article)
            items.append((str(film_id), slug, self._extract_year(react), note, rating))
        next_url = response.xpath("//a[contains(@class, 'next')]/@href")
        return items, next_url[0] if next_url else None

    def _extract_fallback_films_page(self, page_url, language):
        response = self._request_html(page_url, language)
        items = []
        seen = set()
        containers = response.xpath(
            "//li[contains(@class,'griditem') or contains(@class,'poster-container') or contains(@class,'posteritem')]"
            " | //div[contains(@class,'poster-container') or contains(@class,'posteritem')]"
            " | //div[contains(@class,'react-component') and (@data-film-id or @data-postered-identifier)]"
        )
        for container in containers:
            item = self._extract_fallback_user_film(container)
            if item:
                film_id, slug, year, note, rating, when_added = item
                if film_id not in seen:
                    items.append((film_id, slug, year, note, rating))
                    seen.add(film_id)
        if not items:
            for element in response.xpath(
                "//div[@data-film-id]"
                " | //div[contains(@class,'react-component') and (@data-item-link or @data-film-link or @data-target-link or @data-item-slug or @data-film-slug)]"
                " | //li[contains(@class,'posteritem')]//div[contains(@class,'react-component')]"
            ):
                item = self._extract_fallback_react_component(element)
                if item:
                    if item[0] not in seen:
                        items.append(item)
                        seen.add(item[0])
        next_url = response.xpath("//a[contains(@class, 'next')]/@href")
        return items, next_url[0] if next_url else None

    def _get_list_items_fallback(self, list_url, limit, language, extractor=None):
        items = []
        next_url = list_url
        extractor = extractor or self._extract_fallback_list_page
        while next_url:
            page_items, next_href = extractor(next_url, language)
            items.extend(page_items)
            if limit and len(items) >= limit:
                return items[:limit]
            next_url = f"{base_url}{next_href}" if next_href else None
        return items

    @staticmethod
    def _user_page_url(username, page_type):
        suffix = "films/reviews/" if page_type == "reviews" else "films/"
        return f"{base_url}/{username}/{suffix}"

    def _extract_fallback_user_film(self, container):
        react = None
        container_classes = " ".join(container.get("class") or [])
        if getattr(container, "tag", None) == "div" and ("react-component" in container_classes or container.get("data-film-id") or container.get("data-postered-identifier")):
            react = container
        if react is None:
            react = self._first_xpath_value(container, ".//div[contains(@class,'react-component')]")
        if react is None:
            react = self._first_xpath_value(container, ".//div[@data-film-id]")
        if react is None:
            return None

        film_id = self._extract_film_id(react)
        slug = self._extract_slug(react)
        if not film_id or not slug:
            return None

        class_values = container.xpath(".//p[contains(@class,'poster-viewingdata')]//span/@class | .//span[contains(@class,'rating')]/@class")
        rating = self._extract_rating_from_classes(class_values)
        return str(film_id), slug, self._extract_year(react), None, rating, None

    def _extract_fallback_review(self, article):
        react = self._first_xpath_value(article, "../div[contains(@class,'react-component')]")
        if react is None:
            react = self._first_xpath_value(article, "ancestor::li[1]//div[contains(@class,'react-component')][1]")
        if react is None:
            react = self._first_xpath_value(article, "ancestor::div[contains(@class,'poster-container') or contains(@class,'posteritem')][1]//div[contains(@class,'react-component')][1]")
        if react is None:
            return None

        film_id = self._extract_film_id(react)
        slug = self._extract_slug(react)
        if not film_id or not slug:
            return None

        class_values = article.xpath(".//span[contains(@class,'rating')]/@class")
        rating = self._extract_rating_from_classes(class_values)
        date_value = self._first_xpath_value(article, ".//span[contains(@class,'date')]//time/@datetime")
        if not date_value:
            date_value = self._first_xpath_value(article, ".//span[contains(@class,'date')]/@datetime")
        if not date_value:
            date_value = self._first_xpath_value(article, "normalize-space(.//span[contains(@class,'date')])")

        return (
            str(film_id),
            slug,
            self._extract_year(article) or self._extract_year(react),
            self._extract_review_text(article),
            rating,
            self._normalize_fallback_date(date_value),
        )

    def _extract_fallback_user_page(self, page_url, page_type, language):
        response = self._request_html(page_url, language)
        if page_type == "reviews":
            elements = response.xpath("//div[contains(@class,'viewing-list')]//article")
            items = [item for item in (self._extract_fallback_review(element) for element in elements) if item]
        else:
            elements = response.xpath(
                "//li[contains(@class,'griditem') or contains(@class,'poster-container') or contains(@class,'posteritem')]"
                " | //div[contains(@class,'poster-container') or contains(@class,'posteritem')]"
                " | //div[contains(@class,'react-component') and (@data-film-id or @data-postered-identifier)]"
            )
            items = []
            seen = set()
            for element in elements:
                item = self._extract_fallback_user_film(element)
                if item and item[0] not in seen:
                    items.append(item)
                    seen.add(item[0])
        next_url = response.xpath("//a[contains(@class, 'next')]/@href")
        return items, next_url[0] if next_url else None

    def _get_user_entries_fallback(self, username, page_type, language):
        page_url = self._user_page_url(username, page_type)
        items = []
        next_url = page_url
        while next_url:
            page_items, next_href = self._extract_fallback_user_page(next_url, page_type, language)
            items.extend(page_items)
            next_url = f"{base_url}{next_href}" if next_href else None
        return items

    def _tmdb(self, slug_path, language):
        self._require_library()
        try:
            movie = self._movie_cls(self._slug_path(slug_path).strip("/").split("/")[1])
        except Exception as e:
            raise Failed(f"Letterboxd Error: Failed to load {slug_path}: {e}") from e
        tmdb_id = util.check_num(getattr(movie, "tmdb_id", None))
        if tmdb_id:
            return tmdb_id
        else:
            # tmdb_id = None
            # tmdb_link = 'https://www.themoviedb.org/tv/318745/'
            tmdb_link = getattr(movie, "tmdb_link", None)
            if tmdb_link and "themoviedb.org" in tmdb_link:
                logger.info(f"Letterboxd: TMDb Movie ID not found for {slug_path}; found TMDb link {tmdb_link} during fallback parsing.")
                tmdb_id_match = re.search(r"themoviedb\.org/(movie|tv)/(\d+)", tmdb_link)
                if tmdb_id_match:
                    tmdb_type = tmdb_id_match.group(1)
                    tmdb_id = int(tmdb_id_match.group(2))
                    if tmdb_type == "movie":
                        return tmdb_id
                    else:
                        logger.warning(f"Letterboxd Warning: TMDb link for {slug_path} is for a TV show, not a movie; ignoring TMDb ID {tmdb_id} from link.")

        raise Failed(f"Letterboxd Error: TMDb Movie ID not found at {base_url}{self._slug_path(slug_path)} item is type {tmdb_type if 'tmdb_type' in locals() else 'unknown'} with tmdb_id {tmdb_id if 'tmdb_id' in locals() else 'unknown'}.")

    @staticmethod
    def _coerce_year(value):
        return util.check_num(value)

    @staticmethod
    def _coerce_rating_10(value):
        if value is None or value == "":
            return None
        try:
            rating = float(value)
        except (TypeError, ValueError):
            return None
        if rating <= 5:
            return int(round(rating * 2))
        return int(round(rating))

    @staticmethod
    def _year_in_range(year_value, year_range):
        if not year_range:
            return True
        start_year, end_year = year_range.split("-")
        return bool(year_value and int(start_year) <= int(year_value) <= int(end_year))

    @staticmethod
    def _rating_in_range(rating_value, rating_range):
        if not rating_range:
            return True
        start_rating, end_rating = rating_range.split("-")
        return bool(rating_value and int(start_rating) <= int(rating_value) <= int(end_rating))

    @staticmethod
    def _note_matches(note_value, note_filter):
        if not note_filter:
            return True
        return bool(note_value and note_filter in note_value)

    def _get_list_object(self, list_url):
        self._require_library()
        list_url = self._normalize_url(list_url)
        if self._url_type(list_url) == "watchlist":
            username = self._parse_watchlist_url(list_url)
            try:
                return self._watchlist_cls(username)
            except Exception as e:
                raise Failed(f"Letterboxd Error: Failed to load watchlist {list_url}: {e}") from e
        username, slug = self._parse_list_url(list_url)
        try:
            return self._list_cls(username, slug)
        except Exception as e:
            raise Failed(f"Letterboxd Error: Failed to load list {list_url}: {e}") from e

    def _get_list_items(self, list_url, limit, language):
        self._require_library()
        list_url = self._normalize_url(list_url)
        items = []
        if self._url_type(list_url) == "films":
            if self._uses_letterboxdpy_films(list_url):
                try:
                    film_results = self._films_cls(list_url, max=limit or None)
                except Exception as e:
                    raise Failed(f"Letterboxd Error: Failed to load films page {list_url}: {e}") from e
                for item_id, item in film_results.movies.items():
                    slug_path = self._slug_path(item.get("url", f"{base_url}/film/{item.get('slug')}/"))
                    items.append((str(item_id), slug_path, self._coerce_year(item.get("year")), None, self._coerce_rating_10(item.get("rating"))))
            else:
                self._warn_once(("films_user_fallback", list_url), f"Letterboxd Warning: letterboxdpy does not reliably support user-scoped films URLs like {list_url}; using Kometa fallback parsing.")
                items = self._get_list_items_fallback(list_url, limit, language, extractor=self._extract_fallback_films_page)
        elif self._url_type(list_url) == "watchlist":
            watchlist_obj = self._get_list_object(list_url)
            try:
                movies = watchlist_obj.movies
            except Exception as e:
                self._warn_once(("watchlist_fallback_error", list_url), f"Letterboxd Warning: letterboxdpy failed to extract films for watchlist {list_url}; using Kometa fallback parsing. Error: {e}")
                movies = {}
            if movies:
                for item_id, item in movies.items():
                    slug_path = self._slug_path(item.get("url", f"{base_url}/film/{item.get('slug')}/"))
                    items.append((str(item_id), slug_path, self._coerce_year(item.get("year")), None, None))
            else:
                self._warn_once(("watchlist_fallback_empty", list_url), f"Letterboxd Warning: letterboxdpy returned no films for watchlist {list_url}; using Kometa fallback parsing.")
                items = self._get_list_items_fallback(list_url, limit, language, extractor=self._extract_fallback_films_page)
        else:
            # letterboxdpy doesn't support parameters in urls (for shuffling the list before fetching it) or unlisted lists.
            parsed_path = urlparse(list_url).path
            if "/detail/" in parsed_path:
                items = self._get_list_items_fallback(list_url, limit, language, extractor=self._extract_fallback_list_detail_page)
            elif "/share/" in parsed_path or "/by/" in parsed_path:
                items = self._get_list_items_fallback(list_url, limit, language)
            else:
                list_obj = self._get_list_object(list_url)
                try:
                    movies = list_obj.movies
                except Exception as e:
                    self._warn_once(("list_fallback_error", list_url), f"Letterboxd Warning: letterboxdpy failed to extract films for {list_url}; using Kometa fallback parsing. Error: {e}")
                    movies = {}
                if movies:
                    for item_id, item in movies.items():
                        slug_path = self._slug_path(item.get("url", f"{base_url}/film/{item.get('slug')}/"))
                        items.append((str(item_id), slug_path, self._coerce_year(item.get("year")), None, None))
                else:
                    self._warn_once(("list_fallback_empty", list_url), f"Letterboxd Warning: letterboxdpy returned no films for {list_url}; using Kometa fallback parsing.")
                    items = self._get_list_items_fallback(list_url, limit, language)
        return items[:limit] if limit else items

    def _get_user_entries(self, username, page_type, language="en"):
        self._require_library()
        try:
            user = self._user_cls(username)
        except Exception as e:
            raise Failed(f"Letterboxd Error: Failed to load user {username}: {e}") from e

        items = []
        if page_type == "films":
            try:
                payload = user.get_films()
            except Exception as e:
                self._warn_once(("films_fallback_error", username), f"Letterboxd Warning: letterboxdpy failed to extract watched films for {username}; using Kometa fallback parsing. Error: {e}")
                payload = {}
            movies = payload.get("movies", {}) if isinstance(payload, dict) else {}
            if movies:
                for slug, item in movies.items():
                    items.append(
                        (
                            str(item.get("id") or slug),
                            f"/film/{slug}/",
                            self._coerce_year(item.get("year")),
                            None,
                            self._coerce_rating_10(item.get("rating")),
                            None,
                        )
                    )
            else:
                self._warn_once(("films_fallback_empty", username), f"Letterboxd Warning: letterboxdpy returned no watched films for {username}; using Kometa fallback parsing.")
                items = self._get_user_entries_fallback(username, page_type, language)
        else:
            try:
                payload = user.get_reviews()
            except Exception as e:
                self._warn_once(("reviews_fallback_error", username), f"Letterboxd Warning: letterboxdpy failed to extract reviews for {username}; using Kometa fallback parsing. Error: {e}")
                payload = {}
            reviews = payload.get("reviews", {}) if isinstance(payload, dict) else {}
            if reviews:
                for review_id, item in reviews.items():
                    movie = item.get("movie", {})
                    review = item.get("review", {})
                    items.append(
                        (
                            str(movie.get("id") or review_id),
                            f"/film/{movie.get('slug')}/",
                            self._coerce_year(movie.get("release")),
                            review.get("content"),
                            self._coerce_rating_10(item.get("rating")),
                            item.get("date"),
                        )
                    )
            else:
                self._warn_once(("reviews_fallback_empty", username), f"Letterboxd Warning: letterboxdpy returned no reviews for {username}; using Kometa fallback parsing.")
                items = self._get_user_entries_fallback(username, page_type, language)
        return items

    def _filter_user_items(self, items, data, page_type):
        filtered_items = []
        filtered_ids = []
        for item in items:
            letterboxd_id, slug, year, note, rating, when_added = item
            if data["min_rating"] and (not rating or rating < data["min_rating"]):
                filtered_ids.append(slug)
                continue
            if not self._year_in_range(year, data["year"]):
                filtered_ids.append(slug)
                continue
            if page_type == "reviews" and not self._note_matches(note, data["note"]):
                filtered_ids.append(slug)
                continue
            filtered_items.append(item)
        return filtered_items, filtered_ids

    def _normalize_user_lists(self, username, raw_lists, sort):
        entries = []
        source = raw_lists
        if isinstance(raw_lists, dict):
            if "lists" in raw_lists:
                source = raw_lists["lists"]
            elif all(isinstance(v, dict) for v in raw_lists.values()):
                source = raw_lists.values()
            else:
                source = []

        for entry in source if isinstance(source, list) else list(source):
            if isinstance(entry, str):
                continue
            if not isinstance(entry, dict):
                continue
            title = entry.get("title") or entry.get("name")
            url = entry.get("url") or entry.get("link")
            if not url and entry.get("slug"):
                url = f"{base_url}/{username}/list/{entry['slug']}/"
            if url and title:
                entries.append((url.rstrip("/") + "/", title))

        if sort == "name":
            entries.sort(key=lambda item: item[1].lower())
        return entries

    def get_user_lists(self, username, sort, language):
        self._require_library()
        try:
            user = self._user_cls(username)
            raw_lists = user.get_lists()
        except Exception as e:
            raise Failed(f"Letterboxd Error: Failed to load lists for {username}: {e}") from e
        if sort != "updated":
            self._warn_once(("user_lists_sort", sort), f"Letterboxd Warning: sort_by '{sort}' for letterboxd_user_lists is not guaranteed by letterboxdpy; using available order.")
        return self._normalize_user_lists(username, raw_lists, sort)

    def get_list_description(self, list_url, language):
        if self._url_type(list_url) != "list":
            return None
        description = getattr(self._get_list_object(list_url), "description", None)
        return description if description else None

    def validate_letterboxd_lists(self, err_type, letterboxd_lists, language):
        valid_lists = []
        for letterboxd_dict in util.get_list(letterboxd_lists, split=False):
            if not isinstance(letterboxd_dict, dict):
                letterboxd_dict = {"url": letterboxd_dict}
            dict_methods = {dm.lower(): dm for dm in letterboxd_dict}
            final = {
                "url": util.parse(err_type, "url", letterboxd_dict, methods=dict_methods, parent="letterboxd_list").strip(),
                "limit": util.parse(err_type, "limit", letterboxd_dict, methods=dict_methods, datatype="int", parent="letterboxd_list", default=0) if "limit" in dict_methods else 0,
                "note": util.parse(err_type, "note", letterboxd_dict, methods=dict_methods, parent="letterboxd_list") if "note" in dict_methods else None,
                "rating": util.parse(err_type, "rating", letterboxd_dict, methods=dict_methods, datatype="int", parent="letterboxd_list", maximum=10, range_split="-") if "rating" in dict_methods else None,
                "year": util.parse(err_type, "year", letterboxd_dict, methods=dict_methods, datatype="int", parent="letterboxd_list", minimum=1000, maximum=3000, range_split="-") if "year" in dict_methods else None,
            }
            if not final["url"].startswith(base_url) and not final["url"].startswith(boxd_short_url):
                raise Failed(f"{err_type} Error: {final['url']} must begin with: {base_url} or {boxd_short_url}")

            final["url"] = self._normalize_url(final["url"])

            try:
                validation_limit = 1 if self._url_type(final["url"]) == "films" else final["limit"]
                if not self._get_list_items(final["url"], validation_limit, language)[0:1]:
                    logger.warning(f"{err_type} Warning: {final['url']} returned no items during validation")
            except Failed as e:
                logger.warning(f"{err_type} Warning: Could not validate {final['url']}: {e}")
            valid_lists.append(final)
        return valid_lists

    def validate_letterboxd_user_pages(self, err_type, letterboxd_user_pages, page_type, language):
        valid_pages = []
        shared_params = {}
        usernames_list = None

        if isinstance(letterboxd_user_pages, dict):
            dict_methods = {dm.lower(): dm for dm in letterboxd_user_pages}
            if "usernames" in dict_methods and isinstance(letterboxd_user_pages[dict_methods["usernames"]], list):
                usernames_list = letterboxd_user_pages[dict_methods["usernames"]]
            elif "username" not in dict_methods:
                numeric_keys = [k for k in letterboxd_user_pages.keys() if isinstance(k, (int, str)) and str(k).isdigit()]
                if numeric_keys:
                    sorted_numeric = sorted([int(k) for k in numeric_keys])
                    if sorted_numeric == list(range(len(numeric_keys))):
                        usernames_list = [letterboxd_user_pages[str(i)] for i in sorted_numeric if isinstance(letterboxd_user_pages[str(i)], str)]
                else:
                    for value in letterboxd_user_pages.values():
                        if isinstance(value, list) and all(isinstance(item, str) for item in value):
                            usernames_list = value
                            break

            for param_key in ["min_rating", "limit", "note", "year", "sort_by", "incremental"]:
                if param_key in dict_methods:
                    shared_params[param_key] = letterboxd_user_pages[dict_methods[param_key]]

        if usernames_list and isinstance(usernames_list, list):
            for username in usernames_list:
                if isinstance(username, str):
                    letterboxd_dict = {"username": username}
                    letterboxd_dict.update(shared_params)
                    valid_pages.append(self._validate_single_user_page(err_type, letterboxd_dict, page_type, language))
        else:
            for letterboxd_dict in util.get_list(letterboxd_user_pages, split=False):
                if not isinstance(letterboxd_dict, dict):
                    letterboxd_dict = {"username": letterboxd_dict}
                valid_pages.append(self._validate_single_user_page(err_type, letterboxd_dict, page_type, language))

        return valid_pages

    def _validate_single_user_page(self, err_type, letterboxd_dict, page_type, language):
        dict_methods = {dm.lower(): dm for dm in letterboxd_dict}
        incremental = util.parse(err_type, "incremental", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}", datatype="bool", default=True) if "incremental" in dict_methods else True
        sort_by = util.parse(err_type, "sort_by", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}", options=user_sort_options, default="release_date_newest")

        if incremental:
            self._warn_once((page_type, "incremental"), f"{err_type} Warning: letterboxdpy does not expose stable incremental state for Letterboxd {page_type}; disabling incremental parsing.")
            incremental = False
        if sort_by != "release_date_newest":
            self._warn_once((page_type, "sort", sort_by), f"{err_type} Warning: sort_by '{sort_by}' is not guaranteed by letterboxdpy for Letterboxd {page_type}; using the default page order.")

        final = {
            "username": util.parse(err_type, "username", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}").strip(),
            "sort_by": sort_by,
            "incremental": incremental,
            "min_rating": util.parse(err_type, "min_rating", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", minimum=0, maximum=10) if "min_rating" in dict_methods else None,
            "limit": util.parse(err_type, "limit", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", default=0) if "limit" in dict_methods else 0,
            "note": util.parse(err_type, "note", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}") if "note" in dict_methods else None,
            "year": util.parse(err_type, "year", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", minimum=1000, maximum=3000, range_split="-") if "year" in dict_methods else None,
        }

        self._get_user_entries(final["username"], page_type, language)
        return final

    def get_tmdb_ids(self, method, data, language):
        if method == "letterboxd_list":
            logger.info(f"Processing Letterboxd List: {data}")
            items = self._get_list_items(data["url"], data["limit"], language)
            total_items = len(items)
            if total_items <= 0:
                raise Failed(f"Letterboxd Error: No List Items found in {data}")

            ids = []
            filtered_ids = []
            supports_note = self._url_type(data["url"]) == "films" or "/detail/" in urlparse(data["url"]).path
            supports_rating = self._url_type(data["url"]) == "films" or "/detail/" in urlparse(data["url"]).path
            if data["note"] and not supports_note:
                self._warn_once(("list_note", data["url"]), "Letterboxd Warning: letterboxdpy does not expose per-item list notes for standard Letterboxd lists; ignoring note filter.")
            if data["rating"] and not supports_rating:
                self._warn_once(("list_rating", data["url"]), "Letterboxd Warning: letterboxdpy does not expose per-item owner ratings for standard Letterboxd lists; ignoring rating filter.")

            for i, item in enumerate(items, 1):
                letterboxd_id, slug, year, note, rating = item
                if not self._year_in_range(year, data["year"]):
                    filtered_ids.append(slug)
                    continue
                if supports_rating and not self._rating_in_range(rating, data["rating"]):
                    filtered_ids.append(slug)
                    continue
                if supports_note and not self._note_matches(note, data["note"]):
                    filtered_ids.append(slug)
                    continue
                tmdb_id = None
                expired = None
                if self.cache:
                    tmdb_id, expired = self.cache.query_letterboxd_map(letterboxd_id)
                if not tmdb_id or expired is not False:
                    logger.ghost(f"Finding TMDb ID {i}/{total_items}")
                    try:
                        tmdb_id = self._tmdb(slug, language)
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.cache:
                        self.cache.update_letterboxd_map(expired, letterboxd_id, tmdb_id)
                ids.append((tmdb_id, "tmdb"))

            logger.info(f"Processed {total_items} TMDb IDs")
            if filtered_ids:
                logger.info(f"Filtered: {filtered_ids}")
            return ids

        if method not in ["letterboxd_user_films", "letterboxd_user_reviews"]:
            raise Failed(f"Letterboxd Error: Method {method} not supported")

        page_type = "films" if method == "letterboxd_user_films" else "reviews"
        logger.info(f"Processing Letterboxd User {page_type.capitalize()}: {data['username']}")

        all_items = self._get_user_entries(data["username"], page_type, language)
        total_items = len(all_items)
        if total_items <= 0:
            raise Failed(f"Letterboxd Error: No {page_type.capitalize()} Items found for {data['username']}")

        if page_type == "films" and data["note"]:
            self._warn_once(("films_note", data["username"]), "Letterboxd Warning: letterboxdpy does not expose user-film notes for watched items; ignoring note filter.")
        items, filtered_ids = self._filter_user_items(all_items, data, page_type)
        if data["limit"]:
            items = items[: data["limit"]]
        ids = []

        for i, item in enumerate(items, 1):
            letterboxd_id, slug, year, note, rating, when_added = item
            tmdb_id = None
            expired = None
            if self.cache:
                tmdb_id, expired = self.cache.query_letterboxd_map(letterboxd_id)
            if not tmdb_id or expired is not False:
                logger.ghost(f"Finding TMDb ID {i}/{len(items)}")
                try:
                    tmdb_id = self._tmdb(slug, language)
                except Failed as e:
                    logger.error(e)
                    continue
                if self.cache:
                    self.cache.update_letterboxd_map(expired, letterboxd_id, tmdb_id)
            ids.append((tmdb_id, "tmdb"))

        logger.info(f"Processed {len(items)} TMDb IDs")
        if filtered_ids:
            logger.info(f"Filtered: {filtered_ids}")
        return ids
