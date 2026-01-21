import re, time
from datetime import datetime
from lxml import html as lxml_html
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
        # Use cloudscraper for Letterboxd to bypass Cloudflare protection
        response = self.requests.get_scrape_html(url)
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
        # User pages don't use /ajax/ endpoints, use regular URL
        response = self._request(page_url, language)
        letterboxd_elements = response.xpath("//div[@data-film-id]")
        # Try fallback selectors if primary fails
        if len(letterboxd_elements) == 0:
            logger.debug(f"Primary XPath found 0 elements, trying fallback selectors for {page_url}")
            letterboxd_elements = response.xpath("//li[@data-film-id]")
            if len(letterboxd_elements) == 0:
                letterboxd_elements = response.xpath("//article[@data-film-id]")
            if len(letterboxd_elements) == 0:
                # Try finding any element with data-film-id
                letterboxd_elements = response.xpath("//*[@data-film-id]")
        logger.debug(f"Parsing {page_url}: Found {len(letterboxd_elements)} elements with data-film-id attribute")
        # Verify page loaded correctly by checking for common Letterboxd elements
        if len(letterboxd_elements) == 0:
            # Check if page has any content at all
            page_title = response.xpath("//title/text()")
            title_text = page_title[0] if page_title else 'Unknown'
            logger.debug(f"Page title: {title_text}")
            # Check for pagination or other Letterboxd elements
            pagination = response.xpath("//div[@class='pagination']")
            logger.debug(f"Found {len(pagination)} pagination elements")
            # Check if we got a Cloudflare challenge page
            if "cloudflare" in title_text.lower() or "just a moment" in title_text.lower():
                logger.warning(f"Letterboxd page may be blocked by Cloudflare protection for {page_url}")
            # Log a sample of the HTML to help diagnose
            try:
                html_text = lxml_html.tostring(response, encoding='unicode', method='html')[:1000] if hasattr(response, 'getroottree') else str(response)[:1000]
                logger.trace(f"HTML sample (first 1000 chars): {html_text}")
            except Exception:
                logger.trace(f"Could not extract HTML sample from response")
        items = []
        for letterboxd_element in letterboxd_elements:
            slug_list = letterboxd_element.xpath("@data-target-link")
            letterboxd_id_list = letterboxd_element.xpath("@data-film-id")
            if not slug_list or not letterboxd_id_list:
                continue
            slug = slug_list[0]
            letterboxd_id = letterboxd_id_list[0]
            comments = letterboxd_element.xpath(f"parent::article/div[@class='body']/div/p/text()")
            ratings = letterboxd_element.xpath("parent::article/div[@class='body']/div/span/@class")
            if not ratings:
                ratings = letterboxd_element.xpath("parent::li/p/span[contains(@class, 'rating')]/@class")
            years = letterboxd_element.xpath(f"parent::article/div[@class='body']/div/header/span/span/a/text()")
            # Try to extract when_added date from data attributes or text
            when_added = None
            date_attrs = letterboxd_element.xpath("@data-added-date")
            if not date_attrs:
                # Try to find date in nearby elements
                date_text = letterboxd_element.xpath("parent::article//time/@datetime")
                if date_text:
                    when_added = date_text[0]
            else:
                when_added = date_attrs[0]
            rating = None
            if ratings:
                match = re.search("rated-(\\d+)", ratings[0])
                if match:
                    rating = int(match.group(1))
            items.append((letterboxd_id, slug, int(years[0]) if years else None, comments[0] if comments else None, rating, when_added))
        next_url = response.xpath("//a[@class='next']/@href")
        return items, next_url

    def _parse_user_films(self, username, sort_by, limit, language, incremental=False, last_timestamp=None, last_item_ids=None):
        # Force when_added_newest sort for incremental
        if incremental:
            sort_by = "when_added_newest"
        sort_path = user_sort_options.get(sort_by, "")
        if sort_path:
            url = f"{base_url}/{username}/films/{sort_path}"
        else:
            url = f"{base_url}/{username}/films/"
        logger.debug(f"Fetching Letterboxd films from: {url}")
        items, next_url = self._parse_user_page(url, language)
        initial_item_count = len(items)
        logger.debug(f"Initial parse returned {initial_item_count} items from {username}")
        
        # Handle incremental parsing
        if incremental and last_item_ids:
            items_before_filter = len(items)
            items = [item for item in items if item[0] not in last_item_ids]  # Filter out already seen items
            items_after_id_filter = len(items)
            if items_before_filter > 0 and items_after_id_filter == 0:
                logger.debug(f"Incremental parsing filtered out all {items_before_filter} items from first page (already processed)")
            # Stop if we hit items older than last_timestamp
            if last_timestamp and items:
                try:
                    last_dt = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                    filtered_items = []
                    for item in items:
                        if item[5] and item[5] != "":  # when_added exists
                            try:
                                item_dt = datetime.fromisoformat(item[5].replace('Z', '+00:00'))
                                if item_dt > last_dt:
                                    filtered_items.append(item)
                                else:
                                    break  # Stop when we hit items older than last_timestamp
                            except (ValueError, AttributeError):
                                filtered_items.append(item)  # Include if date parsing fails
                        else:
                            filtered_items.append(item)  # Include if no date
                    items = filtered_items
                except (ValueError, AttributeError):
                    pass  # If timestamp parsing fails, continue with item ID filtering
        
        while len(next_url) > 0 and (not limit or len(items) < limit):
            if incremental and last_item_ids and items:
                # Check if we should stop (all new items processed)
                if all(item[0] in last_item_ids for item in items[-10:]):  # Check last 10 items
                    break
            time.sleep(2)
            new_items, next_url = self._parse_user_page(f"{base_url}{next_url[0]}", language)
            
            # Apply incremental filtering to new items
            if incremental and last_item_ids:
                new_items = [item for item in new_items if item[0] not in last_item_ids]
                if last_timestamp and new_items:
                    try:
                        last_dt = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                        filtered_new = []
                        for item in new_items:
                            if item[5] and item[5] != "":
                                try:
                                    item_dt = datetime.fromisoformat(item[5].replace('Z', '+00:00'))
                                    if item_dt > last_dt:
                                        filtered_new.append(item)
                                    else:
                                        break
                                except (ValueError, AttributeError):
                                    filtered_new.append(item)
                            else:
                                filtered_new.append(item)
                        new_items = filtered_new
                        if not new_items:
                            break
                    except (ValueError, AttributeError):
                        pass
            
            items.extend(new_items)
            if limit and len(items) >= limit:
                final_items = items[:limit]
                if incremental and initial_item_count > 0 and len(final_items) == 0:
                    logger.debug(f"Incremental parsing: All {initial_item_count} items from {username} were already processed")
                return final_items
        
        # Log summary if incremental parsing filtered out all items
        if incremental and initial_item_count > 0 and len(items) == 0:
            logger.debug(f"Incremental parsing: All items from {username} were already processed (no new items)")
        return items

    def _parse_user_reviews(self, username, sort_by, limit, language, incremental=False, last_timestamp=None, last_item_ids=None):
        # Force when_added_newest sort for incremental
        if incremental:
            sort_by = "when_added_newest"
        sort_path = user_sort_options.get(sort_by, "")
        if sort_path:
            url = f"{base_url}/{username}/reviews/{sort_path}"
        else:
            url = f"{base_url}/{username}/reviews/"
        logger.debug(f"Fetching Letterboxd reviews from: {url}")
        items, next_url = self._parse_user_page(url, language)
        initial_item_count = len(items)
        logger.debug(f"Initial parse returned {initial_item_count} items from {username}")
        
        # Handle incremental parsing
        if incremental and last_item_ids:
            items_before_filter = len(items)
            items = [item for item in items if item[0] not in last_item_ids]
            items_after_id_filter = len(items)
            if items_before_filter > 0 and items_after_id_filter == 0:
                logger.debug(f"Incremental parsing filtered out all {items_before_filter} items from first page (already processed)")
            if last_timestamp and items:
                from datetime import datetime
                try:
                    last_dt = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                    filtered_items = []
                    for item in items:
                        if item[5] and item[5] != "":
                            try:
                                item_dt = datetime.fromisoformat(item[5].replace('Z', '+00:00'))
                                if item_dt > last_dt:
                                    filtered_items.append(item)
                                else:
                                    break
                            except (ValueError, AttributeError):
                                filtered_items.append(item)
                        else:
                            filtered_items.append(item)
                    items = filtered_items
                except (ValueError, AttributeError):
                    pass
        
        while len(next_url) > 0 and (not limit or len(items) < limit):
            if incremental and last_item_ids and items:
                if all(item[0] in last_item_ids for item in items[-10:]):
                    break
            time.sleep(2)
            new_items, next_url = self._parse_user_page(f"{base_url}{next_url[0]}", language)
            
            if incremental and last_item_ids:
                new_items = [item for item in new_items if item[0] not in last_item_ids]
                if last_timestamp and new_items:
                    try:
                        last_dt = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                        filtered_new = []
                        for item in new_items:
                            if item[5] and item[5] != "":
                                try:
                                    item_dt = datetime.fromisoformat(item[5].replace('Z', '+00:00'))
                                    if item_dt > last_dt:
                                        filtered_new.append(item)
                                    else:
                                        break
                                except (ValueError, AttributeError):
                                    filtered_new.append(item)
                            else:
                                filtered_new.append(item)
                        new_items = filtered_new
                        if not new_items:
                            break
                    except (ValueError, AttributeError):
                        pass
            
            items.extend(new_items)
            if limit and len(items) >= limit:
                final_items = items[:limit]
                if incremental and initial_item_count > 0 and len(final_items) == 0:
                    logger.debug(f"Incremental parsing: All {initial_item_count} items from {username} were already processed")
                return final_items
        
        # Log summary if incremental parsing filtered out all items
        if incremental and initial_item_count > 0 and len(items) == 0:
            logger.debug(f"Incremental parsing: All items from {username} were already processed (no new items)")
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
        # Check if input is a dict with usernames list and shared parameters
        # Handle patterns:
        # 1. {usernames: [user1, user2], min_rating: 8}
        # 2. {0: user1, 1: user2, min_rating: 8} (when YAML parses list with dict keys)
        shared_params = {}
        usernames_list = None
        
        if isinstance(letterboxd_user_pages, dict):
            dict_methods = {dm.lower(): dm for dm in letterboxd_user_pages}
            # Check for explicit usernames key
            if "usernames" in dict_methods and isinstance(letterboxd_user_pages[dict_methods["usernames"]], list):
                usernames_list = letterboxd_user_pages[dict_methods["usernames"]]
            elif "username" in dict_methods and isinstance(letterboxd_user_pages[dict_methods["username"]], str):
                # Single username - handle normally
                pass
            else:
                # Look for numeric keys (0, 1, 2) or list-like structure indicating a list was parsed
                numeric_keys = [k for k in letterboxd_user_pages.keys() if isinstance(k, (int, str)) and str(k).isdigit()]
                if numeric_keys:
                    # This might be a list parsed as dict (YAML can do this in some cases)
                    sorted_numeric = sorted([int(k) for k in numeric_keys])
                    if len(sorted_numeric) == len(numeric_keys) and sorted_numeric == list(range(len(numeric_keys))):
                        # Looks like a list parsed as dict
                        usernames_list = [letterboxd_user_pages[str(i)] for i in sorted_numeric if isinstance(letterboxd_user_pages[str(i)], str)]
                else:
                    # Look for any list value that contains strings (usernames)
                    for key, value in letterboxd_user_pages.items():
                        if isinstance(value, list) and all(isinstance(item, str) for item in value):
                            usernames_list = value
                            break
            
            # Extract shared parameters (exclude username/usernames and numeric keys)
            for param_key in ["min_rating", "limit", "note", "year", "sort_by", "incremental"]:
                if param_key in dict_methods:
                    shared_params[param_key] = letterboxd_user_pages[dict_methods[param_key]]
        
        # Process usernames from extracted list with shared parameters
        if usernames_list and isinstance(usernames_list, list):
            # Apply shared parameters to each username (if any)
            for username in usernames_list:
                if isinstance(username, str):
                    letterboxd_dict = {"username": username}
                    if shared_params:
                        letterboxd_dict.update(shared_params)
                    valid_pages.append(self._validate_single_user_page(err_type, letterboxd_dict, page_type, language))
        else:
            # Normal processing - iterate through list/dict
            for letterboxd_dict in util.get_list(letterboxd_user_pages, split=False):
                if not isinstance(letterboxd_dict, dict):
                    letterboxd_dict = {"username": letterboxd_dict}
                valid_pages.append(self._validate_single_user_page(err_type, letterboxd_dict, page_type, language))
        
        return valid_pages
    
    def _validate_single_user_page(self, err_type, letterboxd_dict, page_type, language):
        dict_methods = {dm.lower(): dm for dm in letterboxd_dict}
        incremental = util.parse(err_type, "incremental", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}", datatype="bool", default=True) if "incremental" in dict_methods else True
        sort_by = util.parse(err_type, "sort_by", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}", options=user_sort_options, default="release_date_newest")
        
        # If incremental is enabled, force sort to when_added_newest
        if incremental and sort_by != "when_added_newest":
            logger.warning(f"{err_type} Warning: incremental parsing requires 'when_added_newest' sort. Disabling incremental or using when_added_newest.")
            if sort_by != "when_added_newest":
                incremental = False
        
        final = {
            "username": util.parse(err_type, "username", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}").strip(),
            "sort_by": sort_by,
            "incremental": incremental,
            "min_rating": util.parse(err_type, "min_rating", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", minimum=0, maximum=10) if "min_rating" in dict_methods else None,
            "limit": util.parse(err_type, "limit", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", default=0) if "limit" in dict_methods else 0,
            "note": util.parse(err_type, "note", letterboxd_dict, methods=dict_methods, parent=f"letterboxd_user_{page_type}") if "note" in dict_methods else None,
            "year": util.parse(err_type, "year", letterboxd_dict, methods=dict_methods, datatype="int", parent=f"letterboxd_user_{page_type}", minimum=1000, maximum=3000, range_split="-") if "year" in dict_methods else None
        }
        # Test if the page is accessible and parseable
        test_url = f"{base_url}/{final['username']}/{page_type}/"
        try:
            test_items, _ = self._parse_user_page(test_url, language)
            # Allow empty pages - user might not have any films/reviews/watchlist items
            # Just verify the page is accessible (no exception means it parsed successfully)
        except Failed:
            # Re-raise Failed exceptions as-is
            raise
        except Exception as e:
            raise Failed(f"{err_type} Error: {final['username']}'s {page_type} page failed to parse: {type(e).__name__}: {e}")
        return final

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
            
            # Check if incremental parsing is enabled
            incremental_enabled = data.get("incremental", True)
            
            # Get incremental state if enabled
            last_timestamp = None
            last_item_ids = []
            if incremental_enabled and self.cache:
                last_timestamp, last_item_ids = self.cache.query_letterboxd_incremental_state(data["username"], page_type)
                if last_timestamp or last_item_ids:
                    logger.info(f"Incremental parsing: Found {len(last_item_ids)} previously parsed items")
            
            if page_type == "films":
                items = self._parse_user_films(data["username"], data["sort_by"], data["limit"], language, 
                                               incremental_enabled, last_timestamp, last_item_ids)
            else:
                items = self._parse_user_reviews(data["username"], data["sort_by"], data["limit"], language,
                                                 incremental_enabled, last_timestamp, last_item_ids)
            total_items = len(items)
            if total_items > 0:
                ids = []
                filtered_ids = []
                # Update incremental state with new items
                new_item_ids = []
                new_timestamp = None
                for i, item in enumerate(items, 1):
                    letterboxd_id, slug, year, note, rating, when_added = item
                    new_item_ids.append(letterboxd_id)
                    # Track newest timestamp
                    if when_added and (not new_timestamp or when_added > new_timestamp):
                        new_timestamp = when_added
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
                
                # Update incremental state if we have new items
                if data.get("incremental", True) and self.cache and new_item_ids:
                    # Keep last 100 item IDs to handle edge cases
                    updated_item_ids = (last_item_ids + new_item_ids)[-100:]
                    # Use newest timestamp or keep existing if no new timestamp
                    final_timestamp = new_timestamp if new_timestamp else last_timestamp
                    self.cache.update_letterboxd_incremental_state(data["username"], page_type, final_timestamp, updated_item_ids)
                    logger.info(f"Incremental state updated: {len(new_item_ids)} new items, {len(updated_item_ids)} total tracked")
                elif data.get("incremental", True) and self.cache and not last_timestamp and not last_item_ids and total_items == 0:
                    # First run with no items - create initial state to mark as processed
                    self.cache.update_letterboxd_incremental_state(data["username"], page_type, None, [])
                
                logger.info(f"Processed {total_items} TMDb IDs")
                if filtered_ids:
                    logger.info(f"Filtered: {filtered_ids}")
                return ids
            else:
                # Handle empty results
                # First run with no items - create initial state
                if incremental_enabled and self.cache and not last_timestamp and not last_item_ids:
                    self.cache.update_letterboxd_incremental_state(data["username"], page_type, None, [])
                
                # If incremental parsing was used and returned 0 items, this is valid (all items already processed)
                if incremental_enabled and (last_timestamp or last_item_ids):
                    logger.info(f"No new {page_type} found for {data['username']} (incremental parsing: all items already processed)")
                    return []
                
                # Return empty list instead of raising error to allow collection to continue with other users
                logger.warning(f"No {page_type} found for {data['username']} - this may indicate an empty account or parsing issue, but continuing with other users")
                return []
        else:
            raise Failed(f"Letterboxd Error: Method {method} not supported")
