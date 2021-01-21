import logging, math, re, requests, time
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class IMDbAPI:
    def __init__(self, Cache=None, TMDb=None, Trakt=None, TVDb=None):
        if TMDb is None and Trakt is None:
            raise Failed("IMDb Error: IMDb requires either TMDb or Trakt")
        self.Cache = Cache
        self.TMDb = TMDb
        self.Trakt = Trakt
        self.TVDb = TVDb

    def get_imdb_ids_from_url(self, imdb_url, language, limit):
        imdb_url = imdb_url.strip()
        if not imdb_url.startswith("https://www.imdb.com/list/ls") and not imdb_url.startswith("https://www.imdb.com/search/title/?"):
            raise Failed("IMDb Error: {} must begin with either:\n| https://www.imdb.com/list/ls (For Lists)\n| https://www.imdb.com/search/title/? (For Searches)".format(imdb_url))

        if imdb_url.startswith("https://www.imdb.com/list/ls"):
            try:                                list_id = re.search("(\\d+)", str(imdb_url)).group(1)
            except AttributeError:              raise Failed("IMDb Error: Failed to parse List ID from {}".format(imdb_url))
            current_url = "https://www.imdb.com/search/title/?lists=ls{}".format(list_id)
        else:
            current_url = imdb_url
        header = {"Accept-Language": language}
        length = 0
        imdb_ids = []
        try:                                results = self.send_request(current_url, header).xpath("//div[@class='desc']/span/text()")[0].replace(",", "")
        except IndexError:                  raise Failed("IMDb Error: Failed to parse URL: {}".format(imdb_url))
        try:                                total = int(re.findall("(\\d+) title", results)[0])
        except IndexError:                  raise Failed("IMDb Error: No Results at URL: {}".format(imdb_url))
        if "&start=" in current_url:        current_url = re.sub("&start=\d+", "", current_url)
        if "&count=" in current_url:        current_url = re.sub("&count=\d+", "", current_url)
        if limit < 1 or total < limit:      limit = total
        remainder = limit % 250
        if remainder == 0:                  remainder = 250
        num_of_pages = math.ceil(int(limit) / 250)
        for i in range(1, num_of_pages + 1):
            start_num = (i - 1) * 250 + 1
            length = util.print_return(length, "Parsing Page {}/{} {}-{}".format(i, num_of_pages, start_num, limit if i == num_of_pages else i * 250))
            response = self.send_request("{}&count={}&start={}".format(current_url, remainder if i == num_of_pages else 250, start_num), header)
            imdb_ids.extend(response.xpath("//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst"))
        util.print_end(length)
        if imdb_ids:                        return imdb_ids
        else:                               raise Failed("IMDb Error: No Movies Found at {}".format(imdb_url))

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_request(self, url, header):
        return html.fromstring(requests.get(url, headers=header).content)

    def get_items(self, method, data, language, status_message=True):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        if status_message:
            logger.debug("Data: {}".format(data))
        show_ids = []
        movie_ids = []
        if method == "imdb_id":
            if status_message:
                logger.info("Processing {}: {}".format(pretty, data))
            tmdb_id, tvdb_id = self.convert_from_imdb(data, language)
            if tmdb_id:                     movie_ids.append(tmdb_id)
            if tvdb_id:                     show_ids.append(tvdb_id)
        elif method == "imdb_list":
            if status_message:
                logger.info("Processing {}: {}".format(pretty,"{} Items at {}".format(data["limit"], data["url"]) if data["limit"] > 0 else data["url"]))
            imdb_ids = self.get_imdb_ids_from_url(data["url"], language, data["limit"])
            total_ids = len(imdb_ids)
            length = 0
            for i, imdb_id in enumerate(imdb_ids, 1):
                length = util.print_return(length, "Converting IMDb ID {}/{}".format(i, total_ids))
                try:
                    tmdb_id, tvdb_id = self.convert_from_imdb(imdb_id, language)
                    if tmdb_id:                     movie_ids.append(tmdb_id)
                    if tvdb_id:                     show_ids.append(tvdb_id)
                except Failed as e:             logger.warning(e)
            util.print_end(length, "Processed {} IMDb IDs".format(total_ids))
        else:
            raise Failed("IMDb Error: Method {} not supported".format(method))
        if status_message:
            logger.debug("TMDb IDs Found: {}".format(movie_ids))
            logger.debug("TVDb IDs Found: {}".format(show_ids))
        return movie_ids, show_ids

    def convert_from_imdb(self, imdb_id, language):
        if self.Cache:
            tmdb_id, tvdb_id = self.Cache.get_ids_from_imdb(imdb_id)
            update_tmdb = False
            if not tmdb_id:
                tmdb_id, update_tmdb = self.Cache.get_tmdb_from_imdb(imdb_id)
                if update_tmdb:
                    tmdb_id = None
            update_tvdb = False
            if not tvdb_id:
                tvdb_id, update_tvdb = self.Cache.get_tvdb_from_imdb(imdb_id)
                if update_tvdb:
                    tvdb_id = None
        else:
            tmdb_id = None
            tvdb_id = None
        from_cache = tmdb_id is not None or tvdb_id is not None

        if not tmdb_id and not tvdb_id and self.TMDb:
            try:                                        tmdb_id = self.TMDb.convert_imdb_to_tmdb(imdb_id)
            except Failed:                              pass
        if not tmdb_id and not tvdb_id and self.TMDb:
            try:                                        tvdb_id = self.TMDb.convert_imdb_to_tvdb(imdb_id)
            except Failed:                              pass
        if not tmdb_id and not tvdb_id and self.Trakt:
            try:                                        tmdb_id = self.Trakt.convert_imdb_to_tmdb(imdb_id)
            except Failed:                              pass
        if not tmdb_id and not tvdb_id and self.Trakt:
            try:                                        tvdb_id = self.Trakt.convert_imdb_to_tvdb(imdb_id)
            except Failed:                              pass
        try:
            if tmdb_id and not from_cache:              self.TMDb.get_movie(tmdb_id)
        except Failed:                              tmdb_id = None
        try:
            if tvdb_id and not from_cache:              self.TVDb.get_series(language, tvdb_id=tvdb_id)
        except Failed:                              tvdb_id = None
        if not tmdb_id and not tvdb_id :            raise Failed("IMDb Error: No TMDb ID or TVDb ID found for IMDb: {}".format(imdb_id))
        if self.Cache:
            if tmdb_id and update_tmdb is not False:
                self.Cache.update_imdb("movie", update_tmdb, imdb_id, tmdb_id)
            if tvdb_id and update_tvdb is not False:
                self.Cache.update_imdb("show", update_tvdb, imdb_id, tvdb_id)
        return tmdb_id, tvdb_id
