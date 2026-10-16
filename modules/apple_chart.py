from datetime import date, datetime
from urllib.parse import urljoin

import requests
from lxml import html
from requests.exceptions import RequestException

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["apple_chart", "itunes_chart"]
country_codes = {"US": "US", "UK": "UK", "JP": "JP", "DE": "DE", "FR": "FR", "IT": "IT", "RU": "RU"}
eu_countries = {"FR", "IT", "RU"}
chart_levels = {"track": "track", "song": "track", "album": "album"}


def validate(method, value):
    if not isinstance(value, dict):
        raise Failed(f"{method} Error: {method} must be a dictionary with country and optional type")
    methods = {str(key).lower(): key for key in value}
    country = value.get(methods.get("country"))
    chart_type = value.get(methods.get("type"), "track")
    if country is None or str(country).strip().upper() not in country_codes:
        raise Failed(f"{method} Error: country must be one of US, UK, JP, DE, FR, IT, or RU")
    normalized_type = str(chart_type).strip().lower()
    if normalized_type not in chart_levels:
        raise Failed(f"{method} Error: type must be track, song, or album")
    unexpected = set(methods) - {"country", "type"}
    if unexpected:
        raise Failed(f"{method} Error: unsupported attributes: {', '.join(sorted(unexpected))}")
    return {"country": str(country).strip().upper(), "type": chart_levels[normalized_type]}


def chart_url(method, country, chart_type):
    eu = country in eu_countries
    if method == "apple_chart":
        page = f"apple_{'albums' if chart_type == 'album' else 'songs'}{'_eu' if eu else ''}/"
    elif method == "itunes_chart":
        page = {("track", False): "ww/", ("track", True): "eu/", ("album", False): "aww/", ("album", True): "eua/"}[(chart_type, eu)]
    else:
        raise Failed(f"Unknown music chart builder: {method}")
    return urljoin("https://kworb.net/", page)


def parse_chart_page(content, country, url):
    try:
        document = html.fromstring(content)
    except (ValueError, TypeError) as e:
        raise Failed(f"Kworb Chart Error: unable to parse chart page: {e}") from e
    tables = document.xpath("//table")
    if not tables:
        raise Failed(f"Kworb Chart Error: no chart table found at {url}")
    rows = []
    headers = None
    for row in tables[0].xpath(".//tr"):
        cells = row.xpath("./th|./td")
        values = [" ".join(cell.itertext()).strip() for cell in cells]
        if not values:
            continue
        if any(value.casefold() in ("pos", "position") for value in values):
            headers = [value.strip().upper() for value in values]
            continue
        if headers is None or country not in headers or len(values) != len(headers):
            continue
        try:
            rank = int(values[headers.index(country)].replace(",", ""))
        except (ValueError, IndexError):
            continue
        if rank < 1:
            continue
        try:
            position = int(values[0])
        except ValueError:
            position = rank
        title_index = next((i for i, value in enumerate(headers) if value in ("ARTIST AND TITLE", "ARTIST & TITLE")), 2)
        title_cell = cells[title_index]
        links = title_cell.xpath(".//a")
        if len(links) >= 2:
            artist, title = (" ".join(link.itertext()).strip() for link in links[:2])
        else:
            text = " ".join(title_cell.itertext()).strip()
            if " - " not in text:
                continue
            artist, title = text.split(" - ", 1)
        artist, title = artist.strip(), title.strip()
        if artist and title:
            rows.append({"position": position, "rank": rank, "artist": artist, "title": title})
    if not rows:
        raise Failed(f"Kworb Chart Error: no ranked {country} entries found at {url}")
    return sorted(rows, key=lambda entry: (entry["rank"], entry["position"]))


class MusicChart:
    def __init__(self, method, session=None):
        self.method = method
        self.session = session or requests.Session()
        self.chart_order = {}

    def get_chart(self, value):
        url = chart_url(self.method, value["country"], value["type"])
        try:
            response = self.session.get(url, timeout=30, headers={"User-Agent": "Kometa/KworbChart"})
            response.raise_for_status()
        except RequestException as e:
            raise Failed(f"Kworb Chart Error: unable to load {url}: {e}") from e
        return parse_chart_page(response.content, value["country"], url)

    def get_rating_keys(self, value, library):
        from modules.plex import MusicMatcher

        chart = self.get_chart(value)
        matcher = MusicMatcher([library], value["type"], load_dates=True)
        results, seen = [], set()
        self.chart_order = {}
        for entry in chart:
            if value["type"] == "track":
                match, _ = matcher.match_earliest_track(entry["artist"], entry["title"])
            else:
                from modules.plex import music_title_key

                candidates = matcher.by_title.get((music_title_key(entry["artist"]), music_title_key(entry["title"])), [])

                def release_key(item):
                    release = getattr(item, "originallyAvailableAt", None)
                    if release is None:
                        release = getattr(item, "year", None)
                    if isinstance(release, (date, datetime)):
                        return release.year, getattr(release, "month", 1), getattr(release, "day", 1), item.ratingKey
                    if release is None:
                        return 9999, 12, 31, item.ratingKey
                    try:
                        return int(release), 1, 1, item.ratingKey
                    except (TypeError, ValueError):
                        return 9999, 12, 31, item.ratingKey

                match = min(candidates, key=release_key) if candidates else None
            if match is not None and match.ratingKey not in seen:
                results.append((match.ratingKey, "ratingKey"))
                seen.add(match.ratingKey)
                self.chart_order[match.ratingKey] = entry["rank"]
        return results
