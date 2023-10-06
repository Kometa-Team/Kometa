import re
from typing import Union
import requests
from bs4 import BeautifulSoup as bs

from modules import util
from modules.util import Failed

logger = util.logger

builders = ["boxofficemojo_latestweekend"]

bom_domain = "https://www.boxofficemojo.com/"
imdb_regex_pattern = r"tt\d+" # A string starting with "tt" and followed by digits

def _get_soup(url: str) -> bs:
    """
    Get a BeautifulSoup object from a URL.

    :param url: The URL to get a BeautifulSoup object from.
    :type url: str
    :return: A BeautifulSoup object.
    :rtype: bs
    """
    html = requests.get(url).text
    return bs(html, "html.parser")

def find_link_to_current_weekend_from_home_page(home_page_url: str) -> Union[str, None]:
    """
    Find the link to the current weekend's box office results.
    Looks for the "More" link in the "Latest Weekend" section of the home page.

    :param home_page_url: The URL of the home page.
    :type home_page_url: str
    :return: The link to the current weekend's box office results, or None if it can't be found.
    :rtype: Union[str, None]
    """
    soup = _get_soup(url=home_page_url)

    # Find a div with the class "mojo-feature-rw"
    latest_weekend = soup.find("div", {"class": "mojo-feature-rw"})
    if latest_weekend is None:
        return None

    # Find a link in the div with the class "mojo-more"
    more_link = latest_weekend.find("a", {"class": "mojo-more"})
    if more_link is None:
        return None

    # Get the href attribute of the link
    return f"{bom_domain}{more_link['href']}"

def collect_links_to_all_movies_in_current_weekend(current_weekend_url: str) -> Union[list[str], None]:
    soup = _get_soup(url=current_weekend_url)

    # Find all links with href attributes starting with "/release"
    release_links = soup.find_all("a", {"href": re.compile(r"^/release")})
    if release_links is None:
        return None

    # Get the href attributes of all the links
    hrefs = [link["href"] for link in release_links]

    # Prepend the home page URL to each href
    return [f"{bom_domain}{href}" for href in hrefs]

def extract_imdb_id_from_bom_movie_page(movie_page_url: str) -> Union[str, None]:
    soup = _get_soup(url=movie_page_url)

    # Find a link with the class "mojo-title-link"
    title_link = soup.find("a", {"class": "mojo-title-link"})
    if title_link is None:
        return None

    # Get the href attribute of the link
    href = title_link["href"]

    # Extract the IMDb ID from the href (a string starting with "/tt" and ending with "/")
    try:
        return util.get_imdb_id_from_string(in_string=href)
    except Failed:
        return None


class BoxOfficeMojo:
    def __init__(self, config):
        self.config = config

    def _get_current_weekend_imdb_ids(self) -> list[str]:
        """
        Get the IMDb IDs of all movies in the current weekend's box office results.

        NOTE: This will make a large number of requests to BoxOfficeMojo.com, which may make it slow. Please be considerate and don't run this too often.
        - Getting the home page - 1 request
        - Getting the current weekend's page - 1 request
        - Getting each movie's page - 1 request per movie (typically ~50 movies)
        - Total: ~52 requests

        :return: A list of IMDb IDs.
        :rtype: list[str]
        """
        current_weekend_link = find_link_to_current_weekend_from_home_page(home_page_url=bom_domain)
        if current_weekend_link is None:
            raise Failed("BoxOfficeMojo Error: Couldn't load current weekend's box office results.")

        movie_links = collect_links_to_all_movies_in_current_weekend(current_weekend_url=current_weekend_link)
        if movie_links is None:
            raise Failed("BoxOfficeMojo Error: Couldn't parse movies in the current weekend's box office results.")

        imdb_ids = []
        movie_count = len(movie_links)
        logger.info(f"Found {movie_count} movie(s) in the current weekend's box office results")

        for i, movie_link in enumerate(movie_links, start=1):
            logger.info("")
            logger.info(f"Processing {i}/{movie_count} BoxOfficeMojo movies")

            imdb_id = extract_imdb_id_from_bom_movie_page(movie_page_url=movie_link)

            if imdb_id is None:
                logger.warning(f"BoxOfficeMojo Warning: Couldn't parse IMDb ID for movie {movie_link}")

            imdb_ids.append(imdb_id)

        if not imdb_ids:
            raise Failed("BoxOfficeMojo Error: No movies found.")

        return imdb_ids

    def get_imdb_ids(self, method, data) -> list[str]:
        logger.info(f"Processing BoxOfficeMojo Movies")

        if method == "boxofficemojo_latestweekend":
            return self._get_current_weekend_imdb_ids()

        raise Failed(f"Config Error: Method {method} not supported")
