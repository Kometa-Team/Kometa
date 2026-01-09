import re, time
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
    "length_longest": "by/longest/"
}

builders = ["letterboxd_list", "letterboxd_list_details", "letterboxd_user_films", "letterboxd_user_films_details", "letterboxd_user_reviews", "letterboxd_user_reviews_details"]
base_url = "https://letterboxd.com"

class Letterboxd:
    def __init__(self, requests, cache=None):
        self.requests = requests
        self.cache = cache

    def _request(self, url, language, xpath=None):
        logger.trace(f"URL: {url}")
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
            comments = letterboxd_element.xpath(f"parent::article/div[@class='body']/div/p/text()")
            ratings = letterboxd_element.xpath("parent::article/div[@class='body']/div/span/@class")
            if not ratings:
                ratings = letterboxd_element.xpath("parent::li/p/span[contains(@class, 'rating')]/@class")
            years = letterboxd_element.xpath(f"parent::article/div[@class='body']/div/header/span/span/a/text()")
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

    def _parse_user_page(self, page_url, language):
        if "ajax" not in page_url:
            if page_url.endswith("/"):
                page_url = page_url.rstrip("/") + "/ajax/"
            else:
                page_url = page_url + "/ajax/"
        response = self._request(page_url, language)
        letterboxd_elements = response.xpath("//div[@data-film-id]")
        items = []
        for letterboxd_element in letterboxd_elements:
            slug = letterboxd_element.xpath("@data-target-link")[0]
            letterboxd_id = letterboxd_element.xpath("@data-film-id")[0]
            comments = letterboxd_element.xpath(f"parent::article/div[@class='body']/div/p/text()")
            ratings = letterboxd_element.xpath("parent::article/div[@class='body']/div/span/@class")
            if not ratings:
                ratings = letterboxd_element.xpath("parent::li/p/span[contains(@class, 'rating')]/@class")
            years = letterboxd_element.xpath(f"parent::article/div[@class='body']/div/header/span/span/a/text()")
            rating = None
            if ratings:
                match = re.search("rated-(\\d+)", ratings[0])
                if match:
                    rating = int(match.group(1))
            items.append((letterboxd_id, slug, int(years[0]) if years else None, comments[0] if comments else None, rating))
        next_url = response.xpath("//a[@class='next']/@href")
        return items, next_url

    def _parse_user_films(self, username, sort_by, limit, language):
        sort_path = user_sort_options.get(sort_by, "")
        if sort_path:
            url = f"{base_url}/{username}/films/{sort_path}"
        else:
            url = f"{base_url}/{username}/films/"
        items, next_url = self._parse_user_page(url, language)
        while len(next_url) > 0:
            time.sleep(2)
            new_items, next_url = self._parse_user_page(f"{base_url}{next_url[0]}", language)
            items.extend(new_items)
            if limit and len(items) >= limit:
                return items[:limit]
        return items

    def _parse_user_reviews(self, username, sort_by, limit, language):
        sort_path = user_sort_options.get(sort_by, "")
        if sort_path:
            url = f"{base_url}/{username}/reviews/{sort_path}"
        else:
            url = f"{base_url}/{username}/reviews/"
        items, next_url = self._parse_user_page(url, language)
        while len(next_url) > 0:
            time.sleep(2)
            new_items, next_url = self._parse_user_page(f"{base_url}{next_url[0]}", language)
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
            elif not self._parse_page(final["url"], language)[0]:
                raise Failed(f"{err_type} Error: {final['url']} failed to parse")
            valid_lists.append(final)
        return valid_lists

    def validate_letterboxd_user_pages(self, err_type, letterboxd_user_pages, page_type, language):
        valid_pages = []
        for letterboxd_dict in util.get_list(letterboxd_user_pages, split=False):
            if not isinstance(letterboxd_dict, dict):
                letterboxd_dict = {"username": letterboxd_dict}
            dict_methods = {dm.lower(): dm for dm in letterboxd_dict}
            final = {
                "username": util.parse(err_type, "username", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}").strip(),
                "sort_by": util.parse(err_type, "sort_by", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}", options=user_sort_options, default="release_date_newest") if "sort_by" in dict_methods else "release_date_newest",
                "min_rating": util.parse(err_type, "min_rating", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", minimum=0, maximum=10) if "min_rating" in dict_methods else None,
                "limit": util.parse(err_type, "limit", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", default=0) if "limit" in dict_methods else 0,
                "note": util.parse(err_type, "note", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}") if "note" in dict_methods else None,
                "year": util.parse(err_type, "year", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", minimum=1000, maximum=3000, range_split="-") if "year" in dict_methods else None
            }
            # Test if the page is accessible
            test_url = f"{base_url}/{final['username']}/{page_type}/"
            try:
                test_items, _ = self._parse_user_page(test_url, language)
                if not test_items:
                    raise Failed(f"{err_type} Error: {final['username']}'s {page_type} page failed to parse or is empty")
            except Exception as e:
                raise Failed(f"{err_type} Error: {final['username']}'s {page_type} page failed to parse: {e}")
            valid_pages.append(final)
        return valid_pages

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
        elif method in ["letterboxd_user_films", "letterboxd_user_reviews"]:
            page_type = "films" if method == "letterboxd_user_films" else "reviews"
            logger.info(f"Processing Letterboxd User {page_type.capitalize()}: {data['username']}")
            if page_type == "films":
                items = self._parse_user_films(data["username"], data["sort_by"], data["limit"], language)
            else:
                items = self._parse_user_reviews(data["username"], data["sort_by"], data["limit"], language)
            total_items = len(items)
            if total_items > 0:
                ids = []
                filtered_ids = []
                for i, item in enumerate(items, 1):
                    letterboxd_id, slug, year, note, rating = item
                    filtered = False
                    if data["min_rating"]:
                        if not rating or rating < data["min_rating"]:
                            filtered = True
                    if data["year"]:
                        start_year, end_year = data["year"].split("-")
                        if not year or int(end_year) < year or year < int(start_year):
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
                raise Failed(f"Letterboxd Error: No {page_type.capitalize()} Items found for {data['username']}")
        else:
            raise Failed(f"Letterboxd Error: Method {method} not supported")
