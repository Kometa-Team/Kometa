import csv, gzip, json, math, os, re, requests, shutil, time
from modules import util
from modules.util import Failed
from urllib.parse import urlparse, parse_qs

logger = util.logger

builders = ["imdb_list", "imdb_id", "imdb_chart", "imdb_watchlist", "imdb_search"]
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
imdb_search_attributes = [
    "sort_by", "title", "type", "type.not", "release.after", "release.before", "rating.gte", "rating.lte",
    "votes.gte", "votes.lte", "genre", "genre.any", "genre.not", "event", "event.winning", "series", "series.any", "series.not",
    "imdb_top", "imdb_bottom", "company", "content_rating", "country", "country.any", "country.not", "country.origin",
    "keyword", "keyword.any", "keyword.not", "language", "language.any", "language.not", "language.primary",
    "popularity.gte", "popularity.lte", "cast", "cast.any", "cast.not", "runtime.gte", "runtime.lte", "adult",
]
sort_by_options = {
    "popularity": "POPULARITY",
    "title": "TITLE_REGIONAL",
    "rating": "USER_RATING",
    "votes": "USER_RATING_COUNT",
    "box_office": "BOX_OFFICE_GROSS_DOMESTIC",
    "runtime": "RUNTIME",
    "year": "YEAR",
    "release": "RELEASE_DATE",
}
sort_options = [f"{a}.{d}"for a in sort_by_options for d in ["asc", "desc"]]
title_type_options = {
    "movie": "movie", "tv_series": "tvSeries", "short": "short", "tv_episode": "tvEpisode", "tv_mini_series": "tvMiniSeries",
    "tv_movie": "tvMovie", "tv_special": "tvSpecial", "tv_short": "tvShort", "video_game": "videoGame", "video": "video",
    "music_video": "musicVideo", "podcast_series": "podcastSeries", "podcast_episode": "podcastEpisode"
}
genre_options = {a.lower(): a for a in [
    "Action", "Adventure", "Animation", "Biography", "Comedy", "Documentary", "Drama", "Crime", "Family", "History",
    "News", "Short", "Western", "Sport", "Reality-TV", "Horror", "Fantasy", "Film-Noir", "Music", "Romance",
    "Talk-Show", "Thriller", "War", "Sci-Fi", "Musical", "Mystery", "Game-Show"
]}
company_options = {
    "fox": ["co0000756", "co0176225", "co0201557", "co0017497"],
    "dreamworks": ["co0067641", "co0040938", "co0252576", "co0003158"],
    "mgm": ["co0007143", "co0026841"],
    "paramount": ["co0023400"],
    "sony": ["co0050868", "co0026545", "co0121181"],
    "universal": ["co0005073", "co0055277", "co0042399"],
    "disney": ["co0008970", "co0017902", "co0098836", "co0059516", "co0092035", "co0049348"],
    "warner": ["co0002663", "co0005035", "co0863266", "co0072876", "co0080422", "co0046718"],
}
event_options = {
    "cannes": {"eventId": "ev0000147"},
    "choice": {"eventId": "ev0000133"},
    "spirit": {"eventId": "ev0000349"},
    "sundance": {"eventId": "ev0000631"},
    "bafta": {"eventId": "ev0000123"},
    "oscar": {"eventId": "ev0000003"},
    "emmy": {"eventId": "ev0000223"},
    "golden": {"eventId": "ev0000292"},
    "oscar_picture": {"eventId": "ev0000003", "searchAwardCategoryId": "bestPicture"},
    "oscar_director": {"eventId": "ev0000003", "searchAwardCategoryId": "bestDirector"},
    "national_film_board_preserved": {"eventId": "ev0000468"},
    "razzie": {"eventId": "ev0000558"},
}
base_url = "https://www.imdb.com"
graphql_url = "https://api.graphql.imdb.com/"
urls = {
    "lists": f"{base_url}/list/ls",
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

    def _graph_request(self, json_data):
        return self.config.post_json(graphql_url, headers={"content-type": "application/json"}, json=json_data)

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
        if limit < 1 or total < limit:
            limit = total
        remainder = limit % item_count
        if remainder == 0:
            remainder = item_count
        num_of_pages = math.ceil(int(limit) / item_count)
        for i in range(1, num_of_pages + 1):
            start_num = (i - 1) * item_count + 1
            logger.ghost(f"Parsing Page {i}/{num_of_pages} {start_num}-{limit if i == num_of_pages else i * item_count}")
            params["page"] = i # noqa
            ids_found = self._request(imdb_base, language=language, xpath="//div[contains(@class, 'lister-item-image')]//a/img//@data-tconst", params=params)
            if i == num_of_pages:
                ids_found = ids_found[:remainder]
            imdb_ids.extend(ids_found)
            time.sleep(2)
        logger.exorcise()
        if len(imdb_ids) > 0:
            return imdb_ids
        raise Failed(f"IMDb Error: No IMDb IDs Found at {imdb_url}")

    def _search_json(self, data):
        out = {
            "locale": "en-US",
            "first": data["limit"] if "limit" in data and data["limit"] < 250 else 250,
            "titleTypeConstraint": {"anyTitleTypeIds": [title_type_options[t] for t in data["type"]] if "type" in data else []},
        }
        sort = data["sort_by"] if "sort_by" in data else "popularity.asc"
        sort_by, sort_order = sort.split(".")
        out["sortBy"] = sort_by_options[sort_by]
        out["sortOrder"] = sort_order.upper()

        if "type.not" in data:
            out["titleTypeConstraint"]["excludeTitleTypeIds"] = [title_type_options[t] for t in data["type.not"]]

        if "release.after" in data or "release.before" in data:
            num_range = {}
            if "release.after" in data:
                num_range["start"] = data["release.after"]
            if "release.before" in data:
                num_range["end"] = data["release.before"]
            out["releaseDateConstraint"] = {"releaseDateRange": num_range}

        if "title" in data:
            out["titleTextConstraint"] = {"searchTerm": data["title"]}

        if any([a in data for a in ["rating.gte", "rating.lte", "votes.gte", "votes.lte"]]):
            out["userRatingsConstraint"] = {}
            num_range = {}
            if "rating.gte" in data:
                num_range["min"] = data["rating.gte"]
            if "rating.lte" in data:
                num_range["max"] = data["rating.lte"]
            out["userRatingsConstraint"]["aggregateRatingRange"] = num_range
            num_range = {}
            if "votes.gte" in data:
                num_range["min"] = data["votes.gte"]
            if "votes.lte" in data:
                num_range["max"] = data["votes.lte"]
            out["userRatingsConstraint"]["ratingsCountRange"] = num_range

        if any([a in data for a in ["genre", "genre.any", "genre.not"]]):
            out["genreConstraint"] = {}
            if "genre" in data:
                out["genreConstraint"]["allGenreIds"] = [genre_options[g] for g in data["genre"]]
            if "genre.any" in data:
                out["genreConstraint"]["anyGenreIds"] = [genre_options[g] for g in data["genre.any"]]
            if "genre.not" in data:
                out["genreConstraint"]["excludeGenreIds"] = [genre_options[g] for g in data["genre.not"]]

        if "event" in data or "event.winning" in data:
            input_list = []
            if "event" in data:
                input_list.extend([event_options[a] if a in event_options else {"eventId": a} for a in data["event"]])
            if "event.winning" in data:
                for a in data["event.winning"]:
                    award_dict = event_options[a] if a in event_options else {"eventId": a}
                    award_dict["winnerFilter"] = "WINNER_ONLY"
                    input_list.append(award_dict)
            out["awardConstraint"] = {"allEventNominations": input_list}

        if any([a in data for a in ["imdb_top", "imdb_bottom", "popularity.gte", "popularity.lte"]]):
            ranges = []
            if "imdb_top" in data:
                ranges.append({"rankRange": {"max": data["imdb_top"]}, "rankedTitleListType": "TOP_RATED_MOVIES"})
            if "imdb_bottom" in data:
                ranges.append({"rankRange": {"max": data["imdb_bottom"]}, "rankedTitleListType": "LOWEST_RATED_MOVIES"})
            if "popularity.gte" in data or "popularity.lte" in data:
                num_range = {}
                if "popularity.lte" in data:
                    num_range["max"] = data["popularity.lte"]
                if "popularity.gte" in data:
                    num_range["min"] = data["popularity.gte"]
                ranges.append({"rankRange": num_range, "rankedTitleListType": "TITLE_METER"})
            out["rankedTitleListConstraint"] = {"allRankedTitleLists": ranges}

        if any([a in data for a in ["series", "series.any", "series.not"]]):
            out["episodicConstraint"] = {}
            if "series" in data:
                out["episodicConstraint"]["allSeriesIds"] = data["series"]
            if "series.any" in data:
                out["episodicConstraint"]["anySeriesIds"] = data["series.any"]
            if "series.not" in data:
                out["episodicConstraint"]["excludeSeriesIds"] = data["series.not"]

        if any([a in data for a in ["list", "list.any", "list.not"]]):
            out["listConstraint"] = {}
            if "list" in data:
                out["listConstraint"]["inAllLists"] = data["list"]
            if "list.any" in data:
                out["listConstraint"]["inAnyList"] = data["list.any"]
            if "list.not" in data:
                out["listConstraint"]["notInAnyList"] = data["list.not"]

        if "company" in data:
            company_ids = []
            for c in data["company"]:
                if c in company_options:
                    company_ids.extend(company_options[c])
                else:
                    company_ids.append(c)
            out["creditedCompanyConstraint"] = {"anyCompanyIds": company_ids}

        if "content_rating" in data:
            out["certificateConstraint"] = {"anyRegionCertificateRatings": data["content_rating"]}

        if any([a in data for a in ["country", "country.any", "country.not", "country.origin"]]):
            out["originCountryConstraint"] = {}
            if "country" in data:
                out["originCountryConstraint"]["allCountries"] = data["country"]
            if "country.any" in data:
                out["originCountryConstraint"]["anyCountries"] = data["country.any"]
            if "country.not" in data:
                out["originCountryConstraint"]["excludeCountries"] = data["country.not"]
            if "country.origin" in data:
                out["originCountryConstraint"]["anyPrimaryCountries"] = data["country.origin"]

        if any([a in data for a in ["keyword", "keyword.any", "keyword.not"]]):
            out["keywordConstraint"] = {}
            if "keyword" in data:
                out["keywordConstraint"]["allKeywords"] = data["keyword"]
            if "keyword.any" in data:
                out["keywordConstraint"]["anyKeywords"] = data["keyword.any"]
            if "keyword.not" in data:
                out["keywordConstraint"]["excludeKeywords"] = data["keyword.not"]

        if any([a in data for a in ["language", "language.any", "language.not", "language.primary"]]):
            out["languageConstraint"] = {}
            if "language" in data:
                out["languageConstraint"]["allLanguages"] = data["language"]
            if "language.any" in data:
                out["languageConstraint"]["anyLanguages"] = data["language.any"]
            if "language.not" in data:
                out["languageConstraint"]["excludeLanguages"] = data["language.not"]
            if "language.primary" in data:
                out["languageConstraint"]["anyPrimaryLanguages"] = data["language.primary"]

        if any([a in data for a in ["cast", "cast.any", "cast.not"]]):
            out["creditedNameConstraint"] = {}
            if "cast" in data:
                out["creditedNameConstraint"]["allNameIds"] = data["cast"]
            if "cast.any" in data:
                out["creditedNameConstraint"]["anyNameIds"] = data["cast.any"]
            if "cast.not" in data:
                out["creditedNameConstraint"]["excludeNameIds"] = data["cast.not"]

        if "runtime.gte" in data or "runtime.lte" in data:
            num_range = {}
            if "runtime.gte" in data:
                num_range["min"] = data["runtime.gte"]
            if "runtime.lte" in data:
                num_range["max"] = data["runtime.lte"]
            out["runtimeConstraint"] = {"runtimeRangeMinutes": num_range}

        if "adult" in data and data["adult"]:
            out["explicitContentConstraint"] = {"explicitContentFilter": "INCLUDE_ADULT"}

        logger.trace(out)
        return {
            "operationName": "AdvancedTitleSearch",
            "variables": out,
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "7327d144ec84b57c93f761affe0d0609b0d495f85e8e47fdc76291679850cfda"
                }
            }
        }

    def _search(self, data):
        json_obj = self._search_json(data)
        item_count = 250
        imdb_ids = []
        logger.ghost("Parsing Page 1")
        response_json = self._graph_request(json_obj)
        total = response_json["data"]["advancedTitleSearch"]["total"]
        limit = data["limit"] if "limit" in data else 0
        if limit < 1 or total < limit:
            limit = total
        remainder = limit % item_count
        if remainder == 0:
            remainder = item_count
        num_of_pages = math.ceil(int(limit) / item_count)
        end_cursor = response_json["data"]["advancedTitleSearch"]["pageInfo"]["endCursor"]
        imdb_ids.extend([n["node"]["title"]["id"] for n in response_json["data"]["advancedTitleSearch"]["edges"]])
        if num_of_pages > 1:
            for i in range(2, num_of_pages + 1):
                start_num = (i - 1) * item_count + 1
                logger.ghost(f"Parsing Page {i}/{num_of_pages} {start_num}-{limit if i == num_of_pages else i * item_count}")
                json_obj["variables"]["after"] = end_cursor
                response_json = self._graph_request(json_obj)
                end_cursor = response_json["data"]["advancedTitleSearch"]["pageInfo"]["endCursor"]
                ids_found = [n["node"]["title"]["id"] for n in response_json["data"]["advancedTitleSearch"]["edges"]]
                if i == num_of_pages:
                    ids_found = ids_found[:remainder]
                imdb_ids.extend(ids_found)
        logger.exorcise()
        if len(imdb_ids) > 0:
            return imdb_ids
        raise Failed("IMDb Error: No IMDb IDs Found")

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
        links = self._request(f"https://www.imdb.com/{url}", language=language, xpath="//li//a[@class='ipc-title-link-wrapper']/@href")
        return [re.search("(tt\\d+)", l).group(1) for l in links]

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
        elif method == "imdb_search":
            logger.info(f"Processing IMDb Search:")
            for k, v in data.items():
                logger.info(f"    {k}: {v}")
            return [(_i, "imdb") for _i in self._search(data)]
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
