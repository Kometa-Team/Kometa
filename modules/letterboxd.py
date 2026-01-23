import re
import time
import cloudscraper
from lxml import html
from modules import util
from modules.util import Failed

logger = util.logger

sort_options = {
    "name": "by/name/",
    "popularity": "by/popular/",
    "newest": "by/newest/",
    "oldest": "by/oldest/",
    "updated": ""
}
builders = ["letterboxd_list", "letterboxd_list_details"]
base_url = "https://letterboxd.com"

class Letterboxd:
    def __init__(self, requests, cache=None):
        self.requests = requests
        self.cache = cache
        self.scraper = cloudscraper.create_scraper()

    def _request_via_cloudscraper(self, url, language):
        """Route request through cloudscraper to bypass Cloudflare protection."""
        headers = None
        if language:
            headers = {"Accept-Language": "eng" if language == "default" else language}
        
        try:
            response = self.scraper.get(url, headers=headers, timeout=30)
            if response.status_code == 403:
                time.sleep(3)
                self.scraper = cloudscraper.create_scraper()
                response = self.scraper.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                raise Failed(f"Letterboxd Error: HTTP {response.status_code} for URL: {url}")
            
            response.encoding = response.apparent_encoding
            return html.fromstring(response.content)
        except Failed:
            raise  # Re-raise Failed exceptions to preserve original error message
        except Exception as e:
            raise Failed(f"Letterboxd Error: Failed to fetch {url}: {str(e)}")

    def _request(self, url, language, xpath=None):
        logger.trace(f"URL: {url}")

        if "letterboxd.com" in url:
            response = self._request_via_cloudscraper(url, language=language)
        else:
            response = self.requests.get_html(url, language=language)
        
        return response.xpath(xpath) if xpath else response

    def _parse_page(self, list_url, language):
        if "ajax" not in list_url:
            list_url = list_url.replace("https://letterboxd.com/films", "https://letterboxd.com/films/ajax")
        response = self._request(list_url, language)
        letterboxd_elements = response.xpath("//div[@data-film-id]")
        items = []
        for letterboxd_element in letterboxd_elements:
            slug = letterboxd_element.xpath("@data-target-link")[0]
            letterboxd_id = letterboxd_element.xpath("@data-film-id")[0]
            comments = letterboxd_element.xpath("parent::article/div[@class='body']/div/p/text()")
            ratings = letterboxd_element.xpath("parent::article/div[@class='body']/div/span/@class")
            if not ratings:
                ratings = letterboxd_element.xpath("parent::li/p/span[contains(@class, 'rating')]/@class")
            years = letterboxd_element.xpath("parent::article/div[@class='body']/div/header/span/span/a/text()")
            rating = None
            if ratings:
                match = re.search("rated-(\\d+)", ratings[0])
                if match:
                    rating = int(match.group(1))
            items.append((letterboxd_id, slug, int(years[0]) if years else None, comments[0] if comments else None, rating))
        next_url = response.xpath("//a[@class='next']/@href")
        return items, next_url

    def _parse_list(self, list_url, limit, language):
        items, next_url = self._parse_page(list_url, language)
        while len(next_url) > 0:
            time.sleep(2)
            new_items, next_url = self._parse_page(f"{base_url}{next_url[0]}", language)
            items.extend(new_items)
            if limit and len(items) >= limit:
                return items[:limit]
        return items

    def _tmdb(self, letterboxd_url, language):
        ids = self._request(letterboxd_url, language, "//a[@data-track-action='TMDb' or @data-track-action='TMDB']/@href")
        if len(ids) > 0 and ids[0]:
            if "themoviedb.org/movie" in ids[0]:
                return util.regex_first_int(ids[0], "TMDb Movie ID")
            raise Failed(f"Letterboxd Error: TMDb Movie ID not found in {ids[0]}")
        raise Failed(f"Letterboxd Error: TMDb Movie ID not found at {letterboxd_url}")

    def get_user_lists(self, username, sort, language):
        next_page = [f"/{username}/lists/{sort_options[sort]}"]
        lists = []
        while next_page:
            response = self._request(f"{base_url}{next_page[0]}", language)
            sections = response.xpath("//article[@data-film-list-id]/div/div/div/h2/a")
            lists.extend([(f"{base_url}{s.xpath('@href')[0]}", s.xpath("text()")[0]) for s in sections])
            next_page = response.xpath("//div[@class='pagination']/div/a[@class='next']/@href")
        return lists

    def get_list_description(self, list_url, language):
        descriptions = self._request(f"{list_url}", language, xpath="//meta[@name='description']/@content")
        if len(descriptions) > 0 and len(descriptions[0]) > 0 and "About this list: " in descriptions[0]:
            return str(descriptions[0]).split("About this list: ")[1]
        return None

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
                "year": util.parse(err_type, "year", letterboxd_dict, methods=dict_methods, datatype="int", parent="letterboxd_list", minimum=1000, maximum=3000, range_split="-") if "year" in dict_methods else None
            }
            if not final["url"].startswith(base_url):
                raise Failed(f"{err_type} Error: {final['url']} must begin with: {base_url}")
            try:
                if not self._parse_page(final["url"], language)[0]:
                    logger.warning(f"{err_type} Warning: {final['url']} returned no items during validation")
            except Failed as e:
                logger.warning(f"{err_type} Warning: Could not validate {final['url']}: {e}")
            valid_lists.append(final)
        return valid_lists

    def get_tmdb_ids(self, method, data, language):
        if method == "letterboxd_list":
            logger.info(f"Processing Letterboxd List: {data}")
            items = self._parse_list(data["url"], data["limit"], language)
            total_items = len(items)
            if total_items > 0:
                ids = []
                filtered_ids = []
                for i, item in enumerate(items, 1):
                    letterboxd_id, slug, year, note, rating = item
                    filtered = False
                    if data["year"]:
                        start_year, end_year = data["year"].split("-")
                        if not year or int(end_year) < year or year < int(start_year):
                            filtered = True
                    if data["rating"]:
                        start_rating, end_rating = data["rating"].split("-")
                        if not rating or int(end_rating) < rating or rating < int(start_rating):
                            filtered = True
                    if data["note"]:
                        if not note or data["note"] not in note:
                            filtered = True
                    if filtered:
                        filtered_ids.append(slug)
                        continue
                    logger.ghost(f"Finding TMDb ID {i}/{total_items}")
                    tmdb_id = None
                    expired = None
                    if self.cache:
                        tmdb_id, expired = self.cache.query_letterboxd_map(letterboxd_id)
                    if not tmdb_id or expired is not False:
                        try:
                            tmdb_id = self._tmdb(f"{base_url}{slug}", language)
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
            else:
                raise Failed(f"Letterboxd Error: No List Items found in {data}")
        else:
            raise Failed(f"Letterboxd Error: Method {method} not supported")
