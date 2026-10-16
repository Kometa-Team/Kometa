import re
from urllib.parse import urljoin

import requests
from lxml import html
from requests.exceptions import RequestException

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["spotify_chart"]
chart_types = ("daily", "weekly")
country_codes = {
    "argentina": "ar",
    "australia": "au",
    "austria": "at",
    "belarus": "by",
    "belgium": "be",
    "bolivia": "bo",
    "brazil": "br",
    "bulgaria": "bg",
    "canada": "ca",
    "chile": "cl",
    "colombia": "co",
    "costa rica": "cr",
    "croatia": "hr",
    "cyprus": "cy",
    "czech republic": "cz",
    "denmark": "dk",
    "dominican republic": "do",
    "ecuador": "ec",
    "egypt": "eg",
    "el salvador": "sv",
    "estonia": "ee",
    "finland": "fi",
    "france": "fr",
    "germany": "de",
    "greece": "gr",
    "guatemala": "gt",
    "honduras": "hn",
    "hong kong": "hk",
    "hungary": "hu",
    "iceland": "is",
    "india": "in",
    "indonesia": "id",
    "ireland": "ie",
    "israel": "il",
    "italy": "it",
    "japan": "jp",
    "kazakhstan": "kz",
    "kenya": "ke",
    "latvia": "lv",
    "lithuania": "lt",
    "luxembourg": "lu",
    "malaysia": "my",
    "mexico": "mx",
    "morocco": "ma",
    "netherlands": "nl",
    "new zealand": "nz",
    "nicaragua": "ni",
    "nigeria": "ng",
    "norway": "no",
    "panama": "pa",
    "paraguay": "py",
    "peru": "pe",
    "philippines": "ph",
    "poland": "pl",
    "portugal": "pt",
    "romania": "ro",
    "russia": "ru",
    "saudi arabia": "sa",
    "serbia": "rs",
    "singapore": "sg",
    "slovakia": "sk",
    "slovenia": "si",
    "south africa": "za",
    "south korea": "kr",
    "spain": "es",
    "sweden": "se",
    "switzerland": "ch",
    "taiwan": "tw",
    "thailand": "th",
    "turkey": "tr",
    "uk": "gb",
    "uae": "ae",
    "united arab emirates": "ae",
    "united kingdom": "gb",
    "united states": "us",
    "usa": "us",
    "uruguay": "uy",
    "venezuela": "ve",
    "vietnam": "vn",
}
country_codes.update(
    {
        "ae": "ae",
        "ar": "ar",
        "at": "at",
        "au": "au",
        "be": "be",
        "bg": "bg",
        "bo": "bo",
        "br": "br",
        "by": "by",
        "ca": "ca",
        "ch": "ch",
        "cl": "cl",
        "co": "co",
        "cr": "cr",
        "cy": "cy",
        "cz": "cz",
        "de": "de",
        "dk": "dk",
        "do": "do",
        "ec": "ec",
        "ee": "ee",
        "eg": "eg",
        "es": "es",
        "fi": "fi",
        "fr": "fr",
        "gb": "gb",
        "gr": "gr",
        "gt": "gt",
        "hk": "hk",
        "hn": "hn",
        "hr": "hr",
        "hu": "hu",
        "id": "id",
        "ie": "ie",
        "il": "il",
        "in": "in",
        "is": "is",
        "it": "it",
        "jp": "jp",
        "ke": "ke",
        "kr": "kr",
        "kz": "kz",
        "lt": "lt",
        "lu": "lu",
        "lv": "lv",
        "ma": "ma",
        "mx": "mx",
        "my": "my",
        "ng": "ng",
        "ni": "ni",
        "nl": "nl",
        "no": "no",
        "nz": "nz",
        "pa": "pa",
        "pe": "pe",
        "ph": "ph",
        "pl": "pl",
        "pt": "pt",
        "py": "py",
        "ro": "ro",
        "rs": "rs",
        "ru": "ru",
        "sa": "sa",
        "se": "se",
        "sg": "sg",
        "si": "si",
        "sk": "sk",
        "sv": "sv",
        "th": "th",
        "tr": "tr",
        "tw": "tw",
        "ua": "ua",
        "us": "us",
        "uy": "uy",
        "ve": "ve",
        "vn": "vn",
        "za": "za",
    }
)


def normalize_country(value):
    country = str(value).strip().casefold()
    if country in country_codes:
        return country_codes[country]
    if re.fullmatch(r"[a-z]{2}", country):
        return country
    raise Failed(f"Spotify Chart Error: country '{value}' is invalid")


def parse_chart_page(content, url):
    try:
        document = html.fromstring(content)
    except (ValueError, TypeError) as e:
        raise Failed(f"Spotify Chart Error: unable to parse chart page: {e}") from e

    tables = document.xpath("//table")
    if not tables:
        raise Failed(f"Spotify Chart Error: no chart table found at {url}")
    rows = []
    for row in tables[0].xpath(".//tr"):
        cells = row.xpath("./th|./td")
        if not cells:
            continue
        values = [" ".join(cell.itertext()).strip() for cell in cells]
        if values and values[0].casefold() in ("pos", "position"):
            continue
        if len(values) < 3:
            continue
        try:
            position = int(values[0])
        except ValueError:
            continue
        title_cells = cells[2].xpath(".//div")
        links = title_cells[0].xpath(".//a") if title_cells else []
        if len(links) >= 2:
            artist, title = " ".join(links[0].itertext()).strip(), " ".join(links[1].itertext()).strip()
        else:
            artist_title = " ".join(title_cells[0].itertext()).strip() if title_cells else values[2]
            if " - " not in artist_title:
                continue
            artist, title = artist_title.split(" - ", 1)
        artist, title = artist.strip(), title.strip()
        if artist and title:
            rows.append({"position": position, "artist": artist, "title": title})
    if not rows:
        raise Failed(f"Spotify Chart Error: no chart entries found at {url}")
    return sorted(rows, key=lambda entry: entry["position"])


class SpotifyChart:
    base_url = "https://kworb.net/spotify/country/"

    def __init__(self, session=None):
        self.session = session or requests.Session()

    @staticmethod
    def validate(value):
        if not isinstance(value, dict):
            raise Failed("Spotify Chart Error: spotify_chart must be a dictionary with country and chart")
        methods = {str(key).lower(): key for key in value}
        country = value.get(methods.get("country"))
        chart_type = value.get(methods.get("chart"))
        if country is None or not str(country).strip():
            raise Failed("Spotify Chart Error: country is required")
        if chart_type is None or str(chart_type).strip().lower() not in chart_types:
            raise Failed("Spotify Chart Error: chart must be daily or weekly")
        unexpected = set(methods) - {"country", "chart"}
        if unexpected:
            raise Failed(f"Spotify Chart Error: unsupported attributes: {', '.join(sorted(unexpected))}")
        return {"country": normalize_country(country), "chart": str(chart_type).strip().lower()}

    def get_chart(self, value):
        url = urljoin(self.base_url, f"{value['country']}_{value['chart']}.html")
        try:
            response = self.session.get(url, timeout=30, headers={"User-Agent": "Kometa/SpotifyChart"})
            response.raise_for_status()
        except RequestException as e:
            raise Failed(f"Spotify Chart Error: unable to load {url}: {e}") from e
        return parse_chart_page(response.content, url)

    def get_rating_keys(self, value, library):
        from modules.plex import MusicMatcher

        chart = self.get_chart(value)
        matcher = MusicMatcher([library], "track", load_dates=True)
        results = []
        seen = set()
        self.chart_order = {}
        for entry in chart:
            match, _ = matcher.match_earliest_track(entry["artist"], entry["title"])
            if match is not None and match.ratingKey not in seen:
                results.append((match.ratingKey, "ratingKey"))
                seen.add(match.ratingKey)
                self.chart_order[match.ratingKey] = entry["position"]
        return results
