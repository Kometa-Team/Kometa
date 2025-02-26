from modules import util
from modules.util import Failed

logger = util.logger

builders = ["icheckmovies_list", "icheckmovies_list_details"]
base_url = "https://www.icheckmovies.com/lists/"

class ICheckMovies:
    def __init__(self, requests):
        self.requests = requests

    def _request(self, url, xpath):
        logger.trace(f"URL: {url}")
        return self.requests.get_scrape_html(url).xpath(xpath)

    def _parse_list(self, list_url):
        imdb_urls = self._request(list_url, "//a[@class='optionIcon optionIMDB external']/@href")
        return [(t[t.find("/tt") + 1:-1], "imdb") for t in imdb_urls]

    def get_list_description(self, list_url):
        descriptions = self._request(list_url, "//div[@class='span-19 last']/p/em/text()")
        return descriptions[0] if len(descriptions) > 0 and len(descriptions[0]) > 0 else None

    def validate_icheckmovies_lists(self, icheckmovies_lists):
        valid_lists = []
        for icheckmovies_list in util.get_list(icheckmovies_lists, split=False):
            list_url = icheckmovies_list.strip()
            if not list_url.startswith(base_url):
                raise Failed(f"ICheckMovies Error: {list_url} must begin with: {base_url}")
            elif len(self._parse_list(list_url)) > 0:
                valid_lists.append(list_url)
            else:
                raise Failed(f"ICheckMovies Error: {list_url} failed to parse")
        return valid_lists

    def get_imdb_ids(self, method, data):
        if method == "icheckmovies_list":
            logger.info(f"Processing ICheckMovies List: {data}")
            return self._parse_list(data)
        else:
            raise Failed(f"ICheckMovies Error: Method {method} not supported")
