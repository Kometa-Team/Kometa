import csv, gzip, json, math, os, re, requests, shutil, time
from modules import util
from modules.util import Failed
from urllib.parse import urlparse, parse_qs

logger = util.logger

builders = ["imdb_list", "imdb_id", "imdb_chart", "imdb_watchlist"]
movie_charts = ["box_office", "popular_movies", "top_movies", "top_english", "top_indian", "lowest_rated"]
show_charts = ["popular_shows", "top_shows"]
charts = {
    "box_office": "Box Office",
    "popular_movies": "Most Popular Movies",
    "popular_shows": "Most Popular TV Shows",
    "top_movies": "Top 250 Movies",
    "top_shows": "Top 250 TV Shows",
    "top_english": "Top Rated English Movies",
    "top_indian": "Top Rated Indian Movies",
    "lowest_rated": "Lowest Rated Movies"
}
base_url = "https://www.imdb.com"
urls = {
    "lists": f"{base_url}/list/ls",
    "searches": f"{base_url}/search/title/",
    "title_text_searches": f"{base_url}/search/title-text/",
    "keyword_searches": f"{base_url}/search/keyword/",
    "filmography_searches": f"{base_url}/filmosearch/"
}

class IMDb:
    def __init__(self, config):
        self.config = config
        self._ratings = None
        self._genres = None
        self._episode_ratings = None

    def _request(self, url, language=None, xpath=None, params=None):
        logger.trace(f"URL: {url}")
        if params:
            logger.trace(f"Params: {params}")
        headers = util.header(language) if language else util.header()
        response = self.config.get_html(url, headers=headers, params=params)
        return response.xpath(xpath) if xpath else response

    def validate_imdb_lists(self, err_type, imdb_lists, language):
        valid_lists = []
        for imdb_dict in util.get_list(imdb_lists, split=False):
            if not isinstance(imdb_dict, dict):
                imdb_dict = {"url": imdb_dict}
            dict_methods = {dm.lower(): dm for dm in imdb_dict}
            if "url" not in dict_methods:
                raise Failed(f"{err_type} Error: imdb_list url attribute not found")
            elif imdb_dict[dict_methods["url"]] is None:
                raise Failed(f"{err_type} Error: imdb_list url attribute is blank")
            else:
                imdb_url = imdb_dict[dict_methods["url"]].strip()
            if not imdb_url.startswith(tuple([v for k, v in urls.items()])):
                fails = "\n".join([f"{v} (For {k.replace('_', ' ').title()})" for k, v in urls.items()])
                raise Failed(f"IMDb Error: {imdb_url} must begin with either:{fails}")
            self._total(imdb_url, language)
            list_count = None
            if "limit" in dict_methods:
                if imdb_dict[dict_methods["limit"]] is None:
                    logger.warning(f"{err_type} Warning: imdb_list limit attribute is blank using 0 as default")
                else:
                    try:
                        value = int(str(imdb_dict[dict_methods["limit"]]))
                        if 0 <= value:
                            list_count = value
                    except ValueError:
                        pass
                if list_count is None:
                    logger.warning(f"{err_type} Warning: imdb_list limit attribute must be an integer 0 or greater using 0 as default")
            if list_count is None:
                list_count = 0
            valid_lists.append({"url": imdb_url, "limit": list_count})
        return valid_lists

    def validate_imdb_watchlists(self, err_type, users, language):
        valid_users = []
        for user in util.get_list(users):
            user_id = None
            if user.startswith("ur"):
                try:
                    user_id = int(user[2:])
                except ValueError:
                    pass
            if not user_id:
                raise Failed(f"{err_type} Error: User {user} not in the format of 'ur########'")
            if self._watchlist(user, language):
                valid_users.append(user)
        return valid_users

    def _watchlist(self, user, language):
        imdb_url = f"{base_url}/user/{user}/watchlist"
        group = self._request(imdb_url, language=language, xpath="//span[@class='ab_widget']/script[@type='text/javascript']/text()")
        if group:
            return [k for k in json.loads(str(group[0]).split("\n")[5][35:-2])["titles"]]
        raise Failed(f"IMDb Error: Failed to parse URL: {imdb_url}")

    def _total(self, imdb_url, language):
        if imdb_url.startswith(urls["lists"]):
            xpath_total = "//div[@class='desc lister-total-num-results']/text()"
            per_page = 100
        elif imdb_url.startswith(urls["searches"]):
            xpath_total = "//div[@class='desc']/span/text()"
            per_page = 250
        elif imdb_url.startswith(urls["title_text_searches"]):
            xpath_total = "//div[@class='desc']/span/text()"
            per_page = 50
        else:
            xpath_total = "//div[@class='desc']/text()"
            per_page = 50
        results = self._request(imdb_url, language=language, xpath=xpath_total)
        total = 0
        for result in results:
            if "title" in result:
                try:
                    total = int(re.findall("(\\d+) title", result.replace(",", ""))[0])
                    break
                except IndexError:
                    pass
        if total > 0:
            return total, per_page
        raise Failed(f"IMDb Error: Failed to parse URL: {imdb_url}")

    def _ids_from_url(self, imdb_url, language, limit):
        total, item_count = self._total(imdb_url, language)
        imdb_ids = []
        parsed_url = urlparse(imdb_url)
        params = parse_qs(parsed_url.query)
        imdb_base = parsed_url._replace(query=None).geturl() # noqa
        params.pop("start", None) # noqa
        params.pop("count", None) # noqa
        params.pop("page", None) # noqa
        logger.trace(f"URL: {imdb_base}")
        logger.trace(f"Params: {params}")
        search_url = imdb_base.startswith(urls["searches"])
        if limit < 1 or total < limit:
            limit = total
        remainder = limit % item_count
        if remainder == 0:
            remainder = item_count
        num_of_pages = math.ceil(int(limit) / item_count)
        for i in range(1, num_of_pages + 1):
            start_num = (i - 1) * item_count + 1
            logger.ghost(f"Parsing Page {i}/{num_of_pages} {start_num}-{limit if i == num_of_pages else i * item_count}")
            if search_url:
                params["count"] = remainder if i == num_of_pages else item_count # noqa
                params["start"] = start_num # noqa
            elif imdb_base.startswith(urls["title_text_searches"]):
                params["start"] = start_num # noqa
            else:
                params["page"] = i # noqa
            ids_found = self._request(imdb_base, language=language, xpath="//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst", params=params)
            if not search_url and i == num_of_pages:
                ids_found = ids_found[:remainder]
            imdb_ids.extend(ids_found)
            time.sleep(2)
        logger.exorcise()
        if len(imdb_ids) > 0:
            return imdb_ids
        raise Failed(f"IMDb Error: No IMDb IDs Found at {imdb_url}")

    def keywords(self, imdb_id, language, ignore_cache=False):
        imdb_keywords = {}
        expired = None
        if self.config.Cache and not ignore_cache:
            imdb_keywords, expired = self.config.Cache.query_imdb_keywords(imdb_id, self.config.Cache.expiration)
            if imdb_keywords and expired is False:
                return imdb_keywords
        keywords = self._request(f"https://www.imdb.com/title/{imdb_id}/keywords", language=language, xpath="//td[@class='soda sodavote']")
        if not keywords:
            raise Failed(f"IMDb Error: No Item Found for IMDb ID: {imdb_id}")
        for k in keywords:
            name = k.xpath("div[@class='sodatext']/a/text()")[0]
            relevant = k.xpath("div[@class='did-you-know-actions']/div/a/text()")[0].strip()
            if "of" in relevant:
                result = re.search(r"(\d+) of (\d+).*", relevant)
                imdb_keywords[name] = (int(result.group(1)), int(result.group(2)))
            else:
                imdb_keywords[name] = (0, 0)
        if self.config.Cache and not ignore_cache:
            self.config.Cache.update_imdb_keywords(expired, imdb_id, imdb_keywords, self.config.Cache.expiration)
        return imdb_keywords

    def parental_guide(self, imdb_id, ignore_cache=False):
        parental_dict = {}
        expired = None
        if self.config.Cache and not ignore_cache:
            parental_dict, expired = self.config.Cache.query_imdb_parental(imdb_id, self.config.Cache.expiration)
            if parental_dict and expired is False:
                return parental_dict
        response = self._request(f"https://www.imdb.com/title/{imdb_id}/parentalguide")
        for ptype in util.parental_types:
            results = response.xpath(f"//section[@id='advisory-{ptype}']//span[contains(@class,'ipl-status-pill')]/text()")
            if results:
                parental_dict[ptype] = results[0].strip()
            else:
                raise Failed(f"IMDb Error: No Item Found for IMDb ID: {imdb_id}")
        if self.config.Cache and not ignore_cache:
            self.config.Cache.update_imdb_parental(expired, imdb_id, parental_dict, self.config.Cache.expiration)
        return parental_dict

    def _ids_from_chart(self, chart, language):
        if chart == "box_office":
            url = "chart/boxoffice"
        elif chart == "popular_movies":
            url = "chart/moviemeter"
        elif chart == "popular_shows":
            url = "chart/tvmeter"
        elif chart == "top_movies":
            url = "chart/top"
        elif chart == "top_shows":
            url = "chart/toptv"
        elif chart == "top_english":
            url = "chart/top-english-movies"
        elif chart == "top_indian":
            url = "india/top-rated-indian-movies"
        elif chart == "lowest_rated":
            url = "chart/bottom"
        else:
            raise Failed(f"IMDb Error: chart: {chart} not ")
        return self._request(f"https://www.imdb.com/{url}", language=language, xpath="//div[@class='wlb_ribbon']/@data-tconst")

    def get_imdb_ids(self, method, data, language):
        if method == "imdb_id":
            logger.info(f"Processing IMDb ID: {data}")
            return [(data, "imdb")]
        elif method == "imdb_list":
            status = f"{data['limit']} Items at " if data['limit'] > 0 else ''
            logger.info(f"Processing IMDb List: {status}{data['url']}")
            return [(i, "imdb") for i in self._ids_from_url(data["url"], language, data["limit"])]
        elif method == "imdb_chart":
            logger.info(f"Processing IMDb Chart: {charts[data]}")
            return [(_i, "imdb") for _i in self._ids_from_chart(data, language)]
        elif method == "imdb_watchlist":
            logger.info(f"Processing IMDb Watchlist: {data}")
            return [(_i, "imdb") for _i in self._watchlist(data, language)]
        else:
            raise Failed(f"IMDb Error: Method {method} not supported")

    def _interface(self, interface):
        gz = os.path.join(self.config.default_dir, f"title.{interface}.tsv.gz")
        tsv = os.path.join(self.config.default_dir, f"title.{interface}.tsv")

        if os.path.exists(gz):
            os.remove(gz)
        if os.path.exists(tsv):
            os.remove(tsv)

        with requests.get(f"https://datasets.imdbws.com/title.{interface}.tsv.gz", stream=True) as r:
            r.raise_for_status()
            total_length = r.headers.get('content-length')
            if total_length is not None:
                total_length = int(total_length)
            dl = 0
            with open(gz, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    dl += len(chunk)
                    f.write(chunk)
                    logger.ghost(f"Downloading IMDb Interface: {dl / total_length * 100:6.2f}%")
                logger.exorcise()

        with open(tsv, "wb") as f_out:
            with gzip.open(gz, "rb") as f_in:
                shutil.copyfileobj(f_in, f_out)

        with open(tsv, "r", encoding="utf-8") as t:
            if interface == "ratings":
                data = {line[0]: line[1] for line in csv.reader(t, delimiter="\t")}
            elif interface == "basics":
                data = {line[0]: str(line[-1]).split(",") for line in csv.reader(t, delimiter="\t")}
            else:
                data = [line for line in csv.reader(t, delimiter="\t")]

        if os.path.exists(gz):
            os.remove(gz)
        if os.path.exists(tsv):
            os.remove(tsv)

        return data

    @property
    def ratings(self):
        if self._ratings is None:
            self._ratings = self._interface("ratings")
        return self._ratings

    @property
    def genres(self):
        if self._genres is None:
            self._genres = self._interface("basics")
        return self._genres

    @property
    def episode_ratings(self):
        if self._episode_ratings is None:
            self._episode_ratings = {}
            for imdb_id, parent_id, season_num, episode_num in self._interface("episode"):
                if imdb_id not in self.ratings:
                    continue
                if parent_id not in self._episode_ratings:
                    self._episode_ratings[parent_id] = {}
                if season_num not in self._episode_ratings[parent_id]:
                    self._episode_ratings[parent_id][season_num] = {}
                self._episode_ratings[parent_id][season_num][episode_num] = self.ratings[imdb_id]
        return self._episode_ratings

    def get_rating(self, imdb_id):
        return self.ratings[imdb_id] if imdb_id in self.ratings else None

    def get_episode_rating(self, imdb_id, season_num, episode_num):
        season_num = str(season_num)
        episode_num = str(episode_num)
        if imdb_id not in self.episode_ratings or season_num not in self.episode_ratings[imdb_id] or episode_num not in self.episode_ratings[imdb_id][season_num]:
            return None
        return self.episode_ratings[imdb_id][season_num][episode_num]

    def item_filter(self, imdb_info, filter_attr, modifier, filter_final, filter_data):
        if filter_attr == "imdb_keyword":
            mr = filter_data["minimum_relevant"]
            mv = filter_data["minimum_votes"]
            mp = filter_data["minimum_percentage"]
            attrs = [k for k, (r, v) in imdb_info.items() if r >= mr and v >= mv and (v == 0 or r / v >= mp)]
            if modifier == ".regex":
                has_match = False
                for reg in filter_data:
                    for name in attrs:
                        if re.compile(reg).search(name):
                            has_match = True
                if has_match is False:
                    return False
            elif modifier in [".count_gt", ".count_gte", ".count_lt", ".count_lte"]:
                test_number = len(attrs) if attrs else 0
                modifier = f".{modifier[7:]}"
                if test_number is None or util.is_number_filter(test_number, modifier, filter_data):
                    return False
            elif (not list(set(filter_data["keywords"]) & set(attrs)) and modifier == "") \
                    or (list(set(filter_data["keywords"]) & set(attrs)) and modifier == ".not"):
                return False
        return True
