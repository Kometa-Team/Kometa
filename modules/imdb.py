import csv, gzip, json, math, os, re, shutil, time
from modules import util
from modules.request import parse_qs, urlparse
from modules.util import Failed

logger = util.logger

builders = ["imdb_list", "imdb_id", "imdb_chart", "imdb_watchlist", "imdb_search", "imdb_award"]
movie_charts = [
    "box_office", "popular_movies", "top_movies", "top_english", "lowest_rated",
    "top_indian", "top_tamil", "top_telugu", "top_malayalam", "trending_india", "trending_tamil", "trending_telugu"
]
show_charts = ["popular_shows", "top_shows", "trending_india"]
charts = {
    "box_office": "Box Office",
    "popular_movies": "Most Popular Movies",
    "popular_shows": "Most Popular TV Shows",
    "top_movies": "Top 250 Movies",
    "top_shows": "Top 250 TV Shows",
    "top_english": "Top Rated English Movies",
    "lowest_rated": "Lowest Rated Movies",
    "top_tamil": "Top Rated Tamil Movies",
    "top_telugu": "Top Rated Telugu Movies",
    "top_malayalam": "Top Rated Malayalam Movies",
    "trending_india": "Trending Indian Movies & Shows",
    "trending_tamil": "Trending Tamil Movies",
    "trending_telugu": "Trending Telugu Movies",
    "top_indian": "Top Rated Indian Movies",
}
chart_urls = {
    "box_office": "chart/boxoffice",
    "popular_movies": "chart/moviemeter",
    "popular_shows": "chart/tvmeter",
    "top_movies": "chart/top",
    "top_shows": "chart/toptv",
    "top_english": "chart/top-english-movies",
    "lowest_rated": "chart/bottom",
    "top_indian": "india/top-rated-indian-movies",
    "top_tamil": "india/top-rated-tamil-movies",
    "top_telugu": "india/top-rated-telugu-movies",
    "top_malayalam": "india/top-rated-malayalam-movies",
    "trending_india": "india/upcoming",
    "trending_tamil": "india/tamil",
    "trending_telugu": "india/telugu",
}
imdb_search_attributes = [
    "limit", "sort_by", "title", "type", "type.not", "release.after", "release.before", "rating.gte", "rating.lte",
    "votes.gte", "votes.lte", "genre", "genre.any", "genre.not", "topic", "topic.any", "topic.not",
    "alternate_version", "alternate_version.not", "crazy_credit", "crazy_credit.not", "location", "location.not",
    "goof", "goof.not", "plot", "plot.not", "quote", "quote.not", "soundtrack", "soundtrack.not",
    "trivia", "trivia.not", "event", "event.winning", "imdb_top", "imdb_bottom", "company", "content_rating",
    "country", "country.any", "country.not", "country.origin", "keyword", "keyword.any",
    "keyword.not", "series", "series.not", "list", "list.any", "list.not", "language", "language.any", "language.not",
    "language.primary", "popularity.gte", "popularity.lte", "cast", "cast.any", "cast.not", "runtime.gte",
    "runtime.lte", "adult",
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
list_sort_by_options = {
    "custom": "LIST_ORDER",
    "popularity": "POPULARITY",
    "title": "TITLE_REGIONAL",
    "rating": "USER_RATING",
    "votes": "USER_RATING_COUNT",
    "runtime": "RUNTIME",
    "added": "DATE_ADDED",
    "release": "RELEASE_DATE",
}
list_sort_options = [f"{a}.{d}"for a in sort_by_options for d in ["asc", "desc"]]
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
topic_options = {
    "alternate_version": "ALTERNATE_VERSION",
    "award": "AWARD",
    "business_info": "BUSINESS_INFO",
    "crazy_credit": "CRAZY_CREDIT",
    "goof": "GOOF",
    "location": "LOCATION",
    "plot": "PLOT",
    "quote": "QUOTE",
    "soundtrack": "SOUNDTRACK",
    "technical": "TECHNICAL",
    "trivia": "TRIVIA",
}
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
git_base = "https://raw.githubusercontent.com/Kometa-Team/IMDb-Awards/master"
search_hash_url = "https://raw.githubusercontent.com/Kometa-Team/IMDb-Hash/master/HASH"
list_hash_url = "https://raw.githubusercontent.com/Kometa-Team/IMDb-Hash/master/LIST_HASH"
graphql_url = "https://api.graphql.imdb.com/"
list_url = f"{base_url}/list/ls"

class IMDb:
    def __init__(self, requests, cache, default_dir):
        self.requests = requests
        self.cache = cache
        self.default_dir = default_dir
        self._ratings = None
        self._genres = None
        self._episode_ratings = None
        self._events_validation = None
        self._events = {}
        self._search_hash = None
        self._list_hash = None
        self.event_url_validation = {}

    def _request(self, url, language=None, xpath=None, params=None):
        logger.trace(f"URL: {url}")
        if params:
            logger.trace(f"Params: {params}")
        response = self.requests.get_html(url, params=params, header=True, language=language)
        return response.xpath(xpath) if xpath else response

    def _graph_request(self, json_data):
        return self.requests.post_json(graphql_url, headers={"content-type": "application/json"}, json=json_data)

    @property
    def search_hash(self):
        if self._search_hash is None:
            self._search_hash = self.requests.get(search_hash_url).text.strip()
        return self._search_hash

    @property
    def list_hash(self):
        if self._list_hash is None:
            self._list_hash = self.requests.get(list_hash_url).text.strip()
        return self._list_hash

    @property
    def events_validation(self):
        if self._events_validation is None:
            self._events_validation = self.requests.get_yaml(f"{git_base}/event_validation.yml").data
        return self._events_validation

    def get_event(self, event_id):
        if event_id not in self._events:
            self._events[event_id] = self.requests.get_yaml(f"{git_base}/events/{event_id}.yml").data
        return self._events[event_id]

    def validate_imdb_lists(self, err_type, imdb_lists):
        valid_lists = []
        for imdb_dict in util.get_list(imdb_lists, split=False):
            if not isinstance(imdb_dict, dict):
                imdb_dict = {"list_id": imdb_dict}
            if "url" in imdb_dict and "list_id" not in imdb_dict:
                imdb_dict["list_id"] = imdb_dict["url"]
            dict_methods = {dm.lower(): dm for dm in imdb_dict}
            if "list_id" not in dict_methods:
                raise Failed(f"{err_type} Error: imdb_list list_id attribute not found")
            elif imdb_dict[dict_methods["list_id"]] is None:
                raise Failed(f"{err_type} Error: imdb_list list_id attribute is blank")
            else:
                imdb_url = imdb_dict[dict_methods["list_id"]].strip()
                if imdb_url.startswith(f"{base_url}/search/"):
                    raise Failed("IMDb Error: URLs with https://www.imdb.com/search/ no longer works with imdb_list use imdb_search.")
                if imdb_url.startswith(f"{base_url}/filmosearch/"):
                    raise Failed("IMDb Error: URLs with https://www.imdb.com/filmosearch/ no longer works with imdb_list use imdb_search.")
                search = re.search(r"(ls\d+)", imdb_url)
                if not search:
                    raise Failed("IMDb Error: imdb_list list_id must begin with ls (ex. ls005526372)")
                new_dict = {"list_id": search.group(1)}

            if "limit" in dict_methods:
                if imdb_dict[dict_methods["limit"]] is None:
                    logger.warning(f"{err_type} Warning: imdb_list limit attribute is blank using 0 as default")
                else:
                    try:
                        value = int(str(imdb_dict[dict_methods["limit"]]))
                        if 0 <= value:
                            new_dict["limit"] = value
                    except ValueError:
                        pass
                if "limit" not in new_dict:
                    logger.warning(f"{err_type} Warning: imdb_list limit attribute: {imdb_dict[dict_methods['limit']]} must be an integer 0 or greater using 0 as default")
            if "limit" not in new_dict:
                new_dict["limit"] = 0

            if "sort_by" in dict_methods:
                new_dict["sort_by"] = util.parse(err_type, dict_methods, imdb_dict, parent="imdb_list", default="custom.asc", options=list_sort_options)

            valid_lists.append(new_dict)
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

    def get_event_years(self, event_id):
        if event_id in self.events_validation:
            return True, self.events_validation[event_id]["years"]
        if event_id not in self.event_url_validation:
            self.event_url_validation[event_id] = []
            for event_link in self._request(f"{base_url}/event/{event_id}", xpath="//div[@class='event-history-widget']//a/@href"):
                parts = event_link.split("/")
                self.event_url_validation[event_id].append(f"{parts[3]}{f'-{parts[4]}' if parts[4] != '1' else ''}")
        return False, self.event_url_validation[event_id]

    def get_award_names(self, event_id, event_year):
        if event_id in self.events_validation:
            return self.events_validation[event_id]["awards"], self.events_validation[event_id]["categories"]
        award_names = []
        category_names = []
        event_slug = f"{event_year[0]}/1" if "-" not in event_year[0] else event_year[0].replace("-", "/")
        for text in self._request(f"{base_url}/event/{event_id}/{event_slug}/?ref_=ev_eh", xpath="//div[@class='article']/script/text()")[0].split("\n"):
            if text.strip().startswith("IMDbReactWidgets.NomineesWidget.push"):
                jsonline = text.strip()
                obj = json.loads(jsonline[jsonline.find("{"):-3])
                for award in obj["nomineesWidgetModel"]["eventEditionSummary"]["awards"]:
                    award_names.append(award["awardName"])
                    for category in award["categories"]:
                        category_names.append(category["categoryName"])
                break
        return award_names, category_names

    def _watchlist(self, user, language):
        imdb_url = f"{base_url}/user/{user}/watchlist"
        for text in self._request(imdb_url, language=language, xpath="//div[@class='article']/script/text()")[0].split("\n"):
            if text.strip().startswith("IMDbReactInitialState.push"):
                jsonline = text.strip()
                return [f for f in json.loads(jsonline[jsonline.find('{'):-2])["starbars"]]
        raise Failed(f"IMDb Error: Failed to parse URL: {imdb_url}")

    def _graphql_json(self, data, search=True):
        page_limit = 250 if search else 100
        out = {
            "locale": "en-US",
            "first": data["limit"] if "limit" in data and 0 < data["limit"] < page_limit else page_limit,
        }

        def check_constraint(bases, mods, constraint, lower="", translation=None, range_name=None):
            if not isinstance(bases, list):
                bases = [bases]
            if range_name and not isinstance(range_name, list):
                range_name = [range_name]
            for i, attr in enumerate(bases):
                attrs = [(f"{attr}.{m}" if m else attr, m, im) for m, im in mods]
                if any([m in data for m, _, _ in attrs]):
                    if constraint not in out:
                        out[constraint] = {}
                    range_data = {}
                    for full_attr, mod, imdb_mod in attrs:
                        if full_attr in data:
                            if range_name is not None:
                                range_data[imdb_mod] = data[full_attr]
                            elif translation is None:
                                out[constraint][f"{imdb_mod}{lower}"] = data[full_attr]
                            elif isinstance(translation, tuple):
                                out[constraint][f"{imdb_mod}{lower}"] = [d.replace(translation[0], translation[1]) for d in data[full_attr]]
                            elif isinstance(translation, dict):
                                out[constraint][f"{imdb_mod}{lower}"] = [translation[d] for d in data[full_attr]]
                    if range_data:
                        out[constraint][range_name[i]] = range_data

        sort = data["sort_by"] if "sort_by" in data else "popularity.asc" if search else "custom.asc"
        sort_by, sort_order = sort.split(".")

        if search:
            out["titleTypeConstraint"] = {"anyTitleTypeIds": [title_type_options[t] for t in data["type"]] if "type" in data else []}
            out["sortBy"] = sort_by_options[sort_by]
            out["sortOrder"] = sort_order.upper()

            check_constraint("type", [("not", "excludeTitleTypeIds")], "titleTypeConstraint", translation=title_type_options)
            check_constraint("release", [("after", "start"), ("before", "end")], "releaseDateConstraint", range_name="releaseDateRange")
            check_constraint("title", [("", "searchTerm")], "titleTextConstraint")
            check_constraint(["rating", "votes"], [("gte", "min"), ("lte", "max")], "userRatingsConstraint", range_name=["aggregateRatingRange", "ratingsCountRange"])
            check_constraint("genre", [("", "all"), ("any", "any"), ("not", "exclude")], "genreConstraint", lower="GenreIds", translation=genre_options)
            check_constraint("topic", [("", "all"), ("any", "any"), ("not", "no")], "withTitleDataConstraint", lower="DataAvailable", translation=topic_options)
            check_constraint("alternate_version", [("", "all"), ("any", "any")], "alternateVersionMatchingConstraint", lower="AlternateVersionTextTerms")
            check_constraint("crazy_credit", [("", "all"), ("any", "any")], "crazyCreditMatchingConstraint", lower="CrazyCreditTextTerms")
            check_constraint("location", [("", "all"), ("any", "any")], "filmingLocationConstraint", lower="Locations")
            check_constraint("goof", [("", "all"), ("any", "any")], "goofMatchingConstraint", lower="GoofTextTerms")
            check_constraint("plot", [("", "all"), ("any", "any")], "plotMatchingConstraint", lower="PlotTextTerms")
            check_constraint("quote", [("", "all"), ("any", "any")], "quoteMatchingConstraint", lower="QuoteTextTerms")
            check_constraint("soundtrack", [("", "all"), ("any", "any")], "soundtrackMatchingConstraint", lower="SoundtrackTextTerms")
            check_constraint("trivia", [("", "all"), ("any", "any")], "triviaMatchingConstraint", lower="TriviaTextTerms")

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

            check_constraint("series", [("", "any"), ("not", "exclude")], "episodicConstraint", lower="SeriesIds")
            check_constraint("list", [("", "inAllLists"), ("any", "inAnyList"), ("not", "notInAnyList")], "listConstraint")

            if "company" in data:
                company_ids = []
                for c in data["company"]:
                    if c in company_options:
                        company_ids.extend(company_options[c])
                    else:
                        company_ids.append(c)
                out["creditedCompanyConstraint"] = {"anyCompanyIds": company_ids}

            check_constraint("content_rating", [("", "anyRegionCertificateRatings")], "certificateConstraint")
            check_constraint("country", [("", "all"), ("any", "any"), ("not", "exclude"), ("origin", "anyPrimary")], "originCountryConstraint", lower="Countries")
            check_constraint("keyword", [("", "all"), ("any", "any"), ("not", "exclude")], "keywordConstraint", lower="Keywords", translation=(" ", "-"))
            check_constraint("language", [("", "all"), ("any", "any"), ("not", "exclude"), ("primary", "anyPrimary")], "languageConstraint", lower="Languages")
            check_constraint("cast", [("", "all"), ("any", "any"), ("not", "exclude")], "creditedNameConstraint", lower="NameIds")
            check_constraint("runtime", [("gte", "min"), ("lte", "max")], "runtimeConstraint", range_name="runtimeRangeMinutes")

            if "adult" in data and data["adult"]:
                out["explicitContentConstraint"] = {"explicitContentFilter": "INCLUDE_ADULT"}
        else:
            out["lsConst"] = data["list_id"]
            out["sort"] = {"by": list_sort_by_options[sort_by], "order": sort_order.upper()}

        logger.trace(out)
        return {
            "operationName": "AdvancedTitleSearch" if search else "TitleListMainPage",
            "variables": out,
            "extensions": {"persistedQuery": {"version": 1, "sha256Hash": self.search_hash if search else self.list_hash}}
        }

    def _pagination(self, data, search=True):
        json_obj = self._graphql_json(data, search=search)
        item_count = 250 if search else 100
        imdb_ids = []
        logger.ghost("Parsing Page 1")
        response_json = self._graph_request(json_obj)
        try:
            search_data = response_json["data"]["advancedTitleSearch"] if search else response_json["data"]["list"]["titleListItemSearch"]
            total = search_data["total"]
            limit = data["limit"]
            if limit < 1 or total < limit:
                limit = total
            remainder = limit % item_count
            if remainder == 0:
                remainder = item_count
            num_of_pages = math.ceil(int(limit) / item_count)
            end_cursor = search_data["pageInfo"]["endCursor"]
            imdb_ids.extend([n["node"]["title"]["id"] if search else n["listItem"]["id"] for n in search_data["edges"]])
            if num_of_pages > 1:
                for i in range(2, num_of_pages + 1):
                    start_num = (i - 1) * item_count + 1
                    logger.ghost(f"Parsing Page {i}/{num_of_pages} {start_num}-{limit if i == num_of_pages else i * item_count}")
                    json_obj["variables"]["after"] = end_cursor
                    response_json = self._graph_request(json_obj)
                    search_data = response_json["data"]["advancedTitleSearch"] if search else response_json["data"]["list"]["titleListItemSearch"]
                    end_cursor = search_data["pageInfo"]["endCursor"]
                    ids_found = [n["node"]["title"]["id"] if search else n["listItem"]["id"] for n in search_data["edges"]]
                    if i == num_of_pages:
                        ids_found = ids_found[:remainder]
                    imdb_ids.extend(ids_found)
            logger.exorcise()
            if len(imdb_ids) > 0:
                return imdb_ids
            raise Failed("IMDb Error: No IMDb IDs Found")
        except KeyError:
            logger.error(f"Response: {response_json}")
            raise

    def _award(self, data):
        final_list = []
        if data["event_id"] in self.events_validation:
            event_data = self.get_event(data["event_id"])
            if data["event_year"] == "all":
                event_years = self.events_validation[data["event_id"]]["years"]
            elif data["event_year"] == "latest":
                event_years = [self.events_validation[data["event_id"]]["years"][0]]
            else:
                event_years = data["event_year"]
            for event_year in event_years:
                for award, categories in event_data[event_year].items():
                    if data["award_filter"] and award not in data["award_filter"]:
                        continue
                    for cat in categories:
                        if data["category_filter"] and cat not in data["category_filter"]:
                            continue
                        final_list.extend(categories[cat]["winner" if data["winning"] else "nominee"])
        else:
            event_year = self.get_event_years(data["event_id"])[0] if data["event_year"] == "latest" else data["event_year"][0]
            event_slug = f"{event_year}/1" if "-" not in event_year else event_year.replace("-", "/")
            for text in self._request(f"{base_url}/event/{data['event_id']}/{event_slug}/?ref_=ev_eh", xpath="//div[@class='article']/script/text()")[0].split("\n"):
                if text.strip().startswith("IMDbReactWidgets.NomineesWidget.push"):
                    jsonline = text.strip()
                    obj = json.loads(jsonline[jsonline.find('{'):-3])
                    for award in obj["nomineesWidgetModel"]["eventEditionSummary"]["awards"]:
                        if data["award_filter"] and award["awardName"] not in data["award_filter"]:
                            continue
                        for cat in award["categories"]:
                            if data["category_filter"] and cat["categoryName"] not in data["category_filter"]:
                                continue
                            for nom in cat["nominations"]:
                                if data["winning"] and not nom["isWinner"]:
                                    continue
                                imdb_id = next((n["const"] for n in nom["primaryNominees"] + nom["secondaryNominees"] if n["const"].startswith("tt")), None)
                                if imdb_id:
                                    final_list.append(imdb_id)
                    break
        return final_list

    def keywords(self, imdb_id, language, ignore_cache=False):
        imdb_keywords = {}
        expired = None
        if self.cache and not ignore_cache:
            imdb_keywords, expired = self.cache.query_imdb_keywords(imdb_id, self.cache.expiration)
            if imdb_keywords and expired is False:
                return imdb_keywords
        keywords = self._request(f"{base_url}/title/{imdb_id}/keywords", language=language, xpath="//td[@class='soda sodavote']")
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
        if self.cache and not ignore_cache:
            self.cache.update_imdb_keywords(expired, imdb_id, imdb_keywords, self.cache.expiration)
        return imdb_keywords

    def parental_guide(self, imdb_id, ignore_cache=False):
        parental_dict = {}
        expired = None
        if self.cache and not ignore_cache:
            parental_dict, expired = self.cache.query_imdb_parental(imdb_id, self.cache.expiration)
            if parental_dict and expired is False:
                return parental_dict
        response = self._request(f"{base_url}/title/{imdb_id}/parentalguide")
        for ptype in util.parental_types:
            results = response.xpath(f"//section[@id='advisory-{ptype}']//span[contains(@class,'ipl-status-pill')]/text()")
            if results:
                parental_dict[ptype] = results[0].strip()
            else:
                raise Failed(f"IMDb Error: No Item Found for IMDb ID: {imdb_id}")
        if self.cache and not ignore_cache:
            self.cache.update_imdb_parental(expired, imdb_id, parental_dict, self.cache.expiration)
        return parental_dict

    def _ids_from_chart(self, chart, language):
        if chart not in chart_urls:
            raise Failed(f"IMDb Error: chart: {chart} not ")
        script_data = self._request(f"{base_url}/{chart_urls[chart]}", language=language, xpath="//script[@id='__NEXT_DATA__']/text()")[0]
        return [x.group(1) for x in re.finditer(r'"(tt\d+)"', script_data)]

    def get_imdb_ids(self, method, data, language):
        if method == "imdb_id":
            logger.info(f"Processing IMDb ID: {data}")
            return [(data, "imdb")]
        elif method == "imdb_list":
            logger.info(f"Processing IMDb List: {data['list_id']}")
            if data["limit"] > 0:
                logger.info(f"    Limit: {data['limit']}")
            if "sort_by" in data:
                logger.info(f"    Sort By: {data['sort_by']}")
            return [(i, "imdb") for i in self._pagination(data, search=False)]
        elif method == "imdb_chart":
            logger.info(f"Processing IMDb Chart: {charts[data]}")
            return [(_i, "imdb") for _i in self._ids_from_chart(data, language)]
        elif method == "imdb_watchlist":
            logger.info(f"Processing IMDb Watchlist: {data}")
            return [(_i, "imdb") for _i in self._watchlist(data, language)]
        elif method == "imdb_award":
            if data["event_year"] not in ["all", "latest"] and len(data["event_year"]) == 1:
                event_slug = f"{data['event_year'][0]}/1" if "-" not in data["event_year"][0] else data["event_year"][0].replace("-", "/")
                logger.info(f"Processing IMDb Award: {base_url}/event/{data['event_id']}/{event_slug}/?ref_=ev_eh")
            else:
                logger.info(f"Processing IMDb Award: {data['event_id']}")
                logger.info(f"    event_year: {data['event_year']}")
            for k in ["award_filter", "category_filter", "winning"]:
                logger.info(f"    {k}: {data[k]}")
            return [(_i, "imdb") for _i in self._award(data)]
        elif method == "imdb_search":
            logger.info(f"Processing IMDb Search:")
            for k, v in data.items():
                logger.info(f"    {k}: {v}")
            return [(_i, "imdb") for _i in self._pagination(data)]
        else:
            raise Failed(f"IMDb Error: Method {method} not supported")

    def _interface(self, interface):
        gz = os.path.join(self.default_dir, f"title.{interface}.tsv.gz")
        tsv = os.path.join(self.default_dir, f"title.{interface}.tsv")

        if os.path.exists(gz):
            os.remove(gz)
        if os.path.exists(tsv):
            os.remove(tsv)

        self.requests.get_stream(f"https://datasets.imdbws.com/title.{interface}.tsv.gz", gz, "IMDb Interface")

        with open(tsv, "wb") as f_out:
            with gzip.open(gz, "rb") as f_in:
                shutil.copyfileobj(f_in, f_out)

        with open(tsv, "r", encoding="utf-8") as t:
            if interface == "ratings":
                data = {line[0]: line[1] for line in csv.reader(t, delimiter="\t")}
            elif interface == "basics":
                data = {line[0]: str(line[-1]).split(",") for line in csv.reader(t, delimiter="\t") if str(line[-1]) != "\\N"}
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

    def get_genres(self, imdb_id):
        return self.genres[imdb_id] if imdb_id in self.genres else []

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
