import logging, math, re, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class IMDbAPI:
    def __init__(self, config):
        self.config = config
        self.urls = {
            "list": "https://www.imdb.com/list/ls",
            "search": "https://www.imdb.com/search/title/?"
        }

    def get_imdb_ids_from_url(self, imdb_url, language, limit):
        imdb_url = imdb_url.strip()
        if not imdb_url.startswith(self.urls["list"]) and not imdb_url.startswith(self.urls["search"]):
            raise Failed(f"IMDb Error: {imdb_url} must begin with either:\n| {self.urls['list']} (For Lists)\n| {self.urls['search']} (For Searches)")

        if imdb_url.startswith(self.urls["list"]):
            try:                                list_id = re.search("(\\d+)", str(imdb_url)).group(1)
            except AttributeError:              raise Failed(f"IMDb Error: Failed to parse List ID from {imdb_url}")
            current_url = f"{self.urls['search']}lists=ls{list_id}"
        else:
            current_url = imdb_url
        header = {"Accept-Language": language}
        length = 0
        imdb_ids = []
        try:                                results = self.send_request(current_url, header).xpath("//div[@class='desc']/span/text()")[0].replace(",", "")
        except IndexError:                  raise Failed(f"IMDb Error: Failed to parse URL: {imdb_url}")
        try:                                total = int(re.findall("(\\d+) title", results)[0])
        except IndexError:                  raise Failed(f"IMDb Error: No Results at URL: {imdb_url}")
        if "&start=" in current_url:        current_url = re.sub("&start=\\d+", "", current_url)
        if "&count=" in current_url:        current_url = re.sub("&count=\\d+", "", current_url)
        if limit < 1 or total < limit:      limit = total
        remainder = limit % 250
        if remainder == 0:                  remainder = 250
        num_of_pages = math.ceil(int(limit) / 250)
        for i in range(1, num_of_pages + 1):
            start_num = (i - 1) * 250 + 1
            length = util.print_return(length, f"Parsing Page {i}/{num_of_pages} {start_num}-{limit if i == num_of_pages else i * 250}")
            response = self.send_request(f"{current_url}&count={remainder if i == num_of_pages else 250}&start={start_num}", header)
            imdb_ids.extend(response.xpath("//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst"))
        util.print_end(length)
        if imdb_ids:                        return imdb_ids
        else:                               raise Failed(f"IMDb Error: No Movies Found at {imdb_url}")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_request(self, url, header):
        return html.fromstring(requests.get(url, headers=header).content)

    def get_items(self, method, data, language, status_message=True):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        if status_message:
            logger.debug(f"Data: {data}")
        show_ids = []
        movie_ids = []
        if method == "imdb_id":
            if status_message:
                logger.info(f"Processing {pretty}: {data}")
            tmdb_id, tvdb_id = self.config.convert_from_imdb(data, language)
            if tmdb_id:                     movie_ids.append(tmdb_id)
            if tvdb_id:                     show_ids.append(tvdb_id)
        elif method == "imdb_list":
            if status_message:
                status = f"{data['limit']} Items at " if data['limit'] > 0 else ''
                logger.info(f"Processing {pretty}: {status}{data['url']}")
            imdb_ids = self.get_imdb_ids_from_url(data["url"], language, data["limit"])
            total_ids = len(imdb_ids)
            length = 0
            for i, imdb_id in enumerate(imdb_ids, 1):
                length = util.print_return(length, f"Converting IMDb ID {i}/{total_ids}")
                try:
                    tmdb_id, tvdb_id = self.config.convert_from_imdb(imdb_id, language)
                    if tmdb_id:                     movie_ids.append(tmdb_id)
                    if tvdb_id:                     show_ids.append(tvdb_id)
                except Failed as e:             logger.warning(e)
            util.print_end(length, f"Processed {total_ids} IMDb IDs")
        else:
            raise Failed(f"IMDb Error: Method {method} not supported")
        if status_message:
            logger.debug(f"TMDb IDs Found: {movie_ids}")
            logger.debug(f"TVDb IDs Found: {show_ids}")
        return movie_ids, show_ids
