import logging, math, re, time
from modules import util
from modules.util import Failed
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger("Plex Meta Manager")

builders = ["imdb_list", "imdb_id"]
base_url = "https://www.imdb.com"
urls = {
    "list": f"{base_url}/list/ls",
    "search": f"{base_url}/search/title/",
    "keyword": f"{base_url}/search/keyword/"
}
xpath = {
    "imdb_id": "//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst",
    "list": "//div[@class='desc lister-total-num-results']/text()",
    "search": "//div[@class='desc']/span/text()",
    "keyword": "//div[@class='desc']/text()"
}
item_counts = {"list": 100, "search": 250, "keyword": 50}

class IMDb:
    def __init__(self, config):
        self.config = config

    def validate_imdb_lists(self, imdb_lists, language):
        valid_lists = []
        for imdb_dict in util.get_list(imdb_lists, split=False):
            if not isinstance(imdb_dict, dict):
                imdb_dict = {"url": imdb_dict}
            dict_methods = {dm.lower(): dm for dm in imdb_dict}
            imdb_url = util.parse("url", imdb_dict, methods=dict_methods, parent="imdb_list").strip()
            if not imdb_url.startswith((urls["list"], urls["search"], urls["keyword"])):
                raise Failed(f"IMDb Error: {imdb_url} must begin with either:\n{urls['list']} (For Lists)\n{urls['search']} (For Searches)\n{urls['keyword']} (For Keyword Searches)")
            self._total(imdb_url, language)
            list_count = util.parse("limit", imdb_dict, datatype="int", methods=dict_methods, default=0, parent="imdb_list", minimum=0) if "limit" in dict_methods else 0
            valid_lists.append({"url": imdb_url, "limit": list_count})
        return valid_lists

    def _total(self, imdb_url, language):
        headers = util.header(language)
        if imdb_url.startswith(urls["keyword"]):
            page_type = "keyword"
        elif imdb_url.startswith(urls["list"]):
            page_type = "list"
        else:
            page_type = "search"
        results = self.config.get_html(imdb_url, headers=headers).xpath(xpath[page_type])
        total = 0
        for result in results:
            if "title" in result:
                try:
                    total = int(re.findall("(\\d+) title", result.replace(",", ""))[0])
                    break
                except IndexError:
                    pass
        if total > 0:
            return total, item_counts[page_type]
        raise Failed(f"IMDb Error: Failed to parse URL: {imdb_url}")

    def _ids_from_url(self, imdb_url, language, limit):
        total, item_count = self._total(imdb_url, language)
        headers = util.header(language)
        imdb_ids = []
        parsed_url = urlparse(imdb_url)
        params = parse_qs(parsed_url.query)
        imdb_base = parsed_url._replace(query=None).geturl()
        params.pop("start", None) # noqa
        params.pop("count", None) # noqa
        params.pop("page", None) # noqa
        if self.config.trace_mode:
            logger.debug(f"URL: {imdb_base}")
            logger.debug(f"Params: {params}")

        if limit < 1 or total < limit:
            limit = total
        remainder = limit % item_count
        if remainder == 0:
            remainder = item_count
        num_of_pages = math.ceil(int(limit) / item_count)
        for i in range(1, num_of_pages + 1):
            start_num = (i - 1) * item_count + 1
            util.print_return(f"Parsing Page {i}/{num_of_pages} {start_num}-{limit if i == num_of_pages else i * item_count}")
            if imdb_base.startswith((urls["list"], urls["keyword"])):
                params["page"] = i # noqa
            else:
                params["count"] = remainder if i == num_of_pages else item_count # noqa
                params["start"] = start_num # noqa
            ids_found = self.config.get_html(imdb_base, headers=headers, params=params).xpath(xpath["imdb_id"])
            if imdb_base.startswith((urls["list"], urls["keyword"])) and i == num_of_pages:
                ids_found = ids_found[:remainder]
            imdb_ids.extend(ids_found)
            time.sleep(2)
        util.print_end()
        if len(imdb_ids) > 0:
            logger.debug(f"{len(imdb_ids)} IMDb IDs Found: {imdb_ids}")
            return imdb_ids
        raise Failed(f"IMDb Error: No IMDb IDs Found at {imdb_url}")

    def get_imdb_ids(self, method, data, language):
        if method == "imdb_id":
            logger.info(f"Processing IMDb ID: {data}")
            return [(data, "imdb")]
        elif method == "imdb_list":
            status = f"{data['limit']} Items at " if data['limit'] > 0 else ''
            logger.info(f"Processing IMDb List: {status}{data['url']}")
            return [(i, "imdb") for i in self._ids_from_url(data["url"], language, data["limit"])]
        else:
            raise Failed(f"IMDb Error: Method {method} not supported")
