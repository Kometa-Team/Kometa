import logging, math, re, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

builders = ["imdb_list", "imdb_id"]

class IMDbAPI:
    def __init__(self, config):
        self.config = config
        self.urls = {
            "list": "https://www.imdb.com/list/ls",
            "search": "https://www.imdb.com/search/title/?",
            "keyword": "https://www.imdb.com/search/keyword/?"
        }

    def validate_imdb_url(self, imdb_url, language):
        imdb_url = imdb_url.strip()
        if not imdb_url.startswith(self.urls["list"]) and not imdb_url.startswith(self.urls["search"]) and not imdb_url.startswith(self.urls["keyword"]):
            raise Failed(f"IMDb Error: {imdb_url} must begin with either:\n{self.urls['list']} (For Lists)\n{self.urls['search']} (For Searches)\n{self.urls['keyword']} (For Keyword Searches)")
        total, _ = self._total(self._fix_url(imdb_url), language)
        if total > 0:
            return imdb_url
        raise Failed(f"IMDb Error: {imdb_url} failed to parse")

    def _fix_url(self, imdb_url):
        if imdb_url.startswith(self.urls["list"]):
            try:                                list_id = re.search("(\\d+)", str(imdb_url)).group(1)
            except AttributeError:              raise Failed(f"IMDb Error: Failed to parse List ID from {imdb_url}")
            return f"{self.urls['search']}lists=ls{list_id}"
        elif imdb_url.endswith("/"):
            return imdb_url[:-1]
        else:
            return imdb_url

    def _total(self, imdb_url, language):
        header = {"Accept-Language": language}
        if imdb_url.startswith(self.urls["keyword"]):
            results = self._request(imdb_url, header).xpath("//div[@class='desc']/text()")
            total = None
            for result in results:
                if "title" in result:
                    try:
                        total = int(re.findall("(\\d+) title", result)[0])
                        break
                    except IndexError:
                        pass
            if total is None:
                raise Failed(f"IMDb Error: No Results at URL: {imdb_url}")
            return total, 50
        else:
            try:                                results = self._request(imdb_url, header).xpath("//div[@class='desc']/span/text()")[0].replace(",", "")
            except IndexError:                  raise Failed(f"IMDb Error: Failed to parse URL: {imdb_url}")
            try:                                total = int(re.findall("(\\d+) title", results)[0])
            except IndexError:                  raise Failed(f"IMDb Error: No Results at URL: {imdb_url}")
            return total, 250

    def _ids_from_url(self, imdb_url, language, limit):
        current_url = self._fix_url(imdb_url)
        total, item_count = self._total(current_url, language)
        header = {"Accept-Language": language}
        length = 0
        imdb_ids = []
        if "&start=" in current_url:        current_url = re.sub("&start=\\d+", "", current_url)
        if "&count=" in current_url:        current_url = re.sub("&count=\\d+", "", current_url)
        if "&page=" in current_url:         current_url = re.sub("&page=\\d+", "", current_url)
        if limit < 1 or total < limit:      limit = total

        remainder = limit % item_count
        if remainder == 0:                  remainder = item_count
        num_of_pages = math.ceil(int(limit) / item_count)
        for i in range(1, num_of_pages + 1):
            start_num = (i - 1) * item_count + 1
            length = util.print_return(length, f"Parsing Page {i}/{num_of_pages} {start_num}-{limit if i == num_of_pages else i * item_count}")
            if imdb_url.startswith(self.urls["keyword"]):
                response = self._request(f"{current_url}&page={i}", header)
            else:
                response = self._request(f"{current_url}&count={remainder if i == num_of_pages else item_count}&start={start_num}", header)
            if imdb_url.startswith(self.urls["keyword"]) and i == num_of_pages:
                imdb_ids.extend(response.xpath("//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst")[:remainder])
            else:
                imdb_ids.extend(response.xpath("//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst"))
        util.print_end(length)
        if imdb_ids:                        return imdb_ids
        else:                               raise Failed(f"IMDb Error: No IMDb IDs Found at {imdb_url}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _request(self, url, header):
        return html.fromstring(requests.get(url, headers=header).content)

    def get_items(self, method, data, language):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        logger.debug(f"Data: {data}")
        show_ids = []
        movie_ids = []
        if method == "imdb_id":
            logger.info(f"Processing {pretty}: {data}")
            tmdb_id = self.config.Convert.imdb_to_tmdb(data)
            tvdb_id = self.config.Convert.imdb_to_tvdb(data)
            if not tmdb_id and not tvdb_id:
                logger.error(f"Convert Error: No TMDb ID or TVDb ID found for IMDb: {data}")
            if tmdb_id:                     movie_ids.append(tmdb_id)
            if tvdb_id:                     show_ids.append(tvdb_id)
        elif method == "imdb_list":
            status = f"{data['limit']} Items at " if data['limit'] > 0 else ''
            logger.info(f"Processing {pretty}: {status}{data['url']}")
            imdb_ids = self._ids_from_url(data["url"], language, data["limit"])
            total_ids = len(imdb_ids)
            length = 0
            for i, imdb_id in enumerate(imdb_ids, 1):
                length = util.print_return(length, f"Converting IMDb ID {i}/{total_ids}")
                tmdb_id = self.config.Convert.imdb_to_tmdb(imdb_id)
                tvdb_id = self.config.Convert.imdb_to_tvdb(imdb_id)
                if not tmdb_id and not tvdb_id:
                    logger.error(f"Convert Error: No TMDb ID or TVDb ID found for IMDb: {imdb_id}")
                if tmdb_id:                     movie_ids.append(tmdb_id)
                if tvdb_id:                     show_ids.append(tvdb_id)
            util.print_end(length, f"Processed {total_ids} IMDb IDs")
        else:
            raise Failed(f"IMDb Error: Method {method} not supported")
        logger.debug(f"TMDb IDs Found: {movie_ids}")
        logger.debug(f"TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids
