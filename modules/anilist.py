import time
from modules import util
from modules.util import Failed

logger = util.logger

builders = ["anilist_id", "anilist_popular", "anilist_trending", "anilist_relations", "anilist_studio", "anilist_top_rated", "anilist_search", "anilist_userlist"]
pretty_names = {"score": "Average Score", "popular": "Popularity", "trending": "Trending"}
pretty_user = {
    "status": "Status", "score": "User Score", "progress": "Progress", "last_updated": "Last Updated",
    "last_added": "Last Added", "start_date": "Start Date", "completed_date": "Completed Date", "popularity": "Popularity"
}
attr_translation = {
    "year": "seasonYear", "adult": "isAdult", "start": "startDate", "end": "endDate", "tag_category": "tagCategory",
    "score": "averageScore", "min_tag_percent": "minimumTagRank", "country": "countryOfOrigin",
}
mod_translation = {"": "in", "not": "not_in", "before": "greater", "after": "lesser", "gt": "greater", "gte": "greater", "lt": "lesser", "lte": "lesser"}
mod_searches = [
    "start.before", "start.after", "end.before", "end.after",
    "format", "format.not", "status", "status.not", "genre", "genre.not", "tag", "tag.not", "tag_category", "tag_category.not",
    "episodes.gt", "episodes.gte", "episodes.lt", "episodes.lte", "duration.gt", "duration.gte", "duration.lt", "duration.lte",
    "score.gt", "score.gte", "score.lt", "score.lte", "popularity.gt", "popularity.gte", "popularity.lt", "popularity.lte"
]
no_mod_searches = ["search", "season", "year", "adult", "min_tag_percent", "limit", "sort_by", "source", "country"]
searches = mod_searches + no_mod_searches
sort_options = {"score": "SCORE_DESC", "popular": "POPULARITY_DESC", "trending": "TRENDING_DESC"}
userlist_sort_options = {
    "score": "SCORE_DESC", "status": "STATUS_DESC", "progress": "PROGRESS_DESC",
    "last_updated": "UPDATED_TIME_DESC", "last_added": "ADDED_TIME_DESC", "start_date": "STARTED_ON_DESC",
    "completed_date": "FINISHED_ON_DESC", "popularity": "MEDIA_POPULARITY_DESC"
}
media_season = {"winter": "WINTER", "spring": "SPRING", "summer": "SUMMER", "fall": "FALL"}
media_format = {"tv": "TV", "short": "TV_SHORT", "movie": "MOVIE", "special": "SPECIAL", "ova": "OVA", "ona": "ONA", "music": "MUSIC"}
media_status = {"finished": "FINISHED", "airing": "RELEASING", "not_yet_aired": "NOT_YET_RELEASED", "cancelled": "CANCELLED", "hiatus": "HIATUS"}
media_source = {
    "original": "ORIGINAL", "manga": "MANGA", "light_novel": "LIGHT_NOVEL", "visual_novel": "VISUAL_NOVEL",
    "video_game": "VIDEO_GAME", "other": "OTHER", "novel": "NOVEL", "doujinshi": "DOUJINSHI", "anime": "ANIME"
}
base_url = "https://graphql.anilist.co"
tag_query = "query{MediaTagCollection {name, category}}"
genre_query = "query{GenreCollection}"
country_codes = [
    "af", "ax", "al", "dz", "as", "ad", "ao", "ai", "aq", "ag", "ar", "am", "aw", "au", "at", "az", "bs", "bh", "bd",
    "bb", "by", "be", "bz", "bj", "bm", "bt", "bo", "bq", "ba", "bw", "bv", "br", "io", "bn", "bg", "bf", "bi", "cv",
    "kh", "cm", "ca", "ky", "cf", "td", "cl", "cn", "cx", "cc", "co", "km", "cg", "cd", "ck", "cr", "ci", "hr", "cu",
    "cw", "cy", "cz", "dk", "dj", "dm", "do", "ec", "eg", "sv", "gq", "er", "ee", "sz", "et", "fk", "fo", "fj", "fi",
    "fr", "gf", "pf", "tf", "ga", "gm", "ge", "de", "gh", "gi", "gr", "gl", "gd", "gp", "gu", "gt", "gg", "gn", "gw",
    "gy", "ht", "hm", "va", "hn", "hk", "hu", "is", "in", "id", "ir", "iq", "ie", "im", "il", "it", "jm", "jp", "je",
    "jo", "kz", "ke", "ki", "kp", "kr", "kw", "kg", "la", "lv", "lb", "ls", "lr", "ly", "li", "lt", "lu", "mo", "mg",
    "mw", "my", "mv", "ml", "mt", "mh", "mq", "mr", "mu", "yt", "mx", "fm", "md", "mc", "mn", "me", "ms", "ma", "mz",
    "mm", "na", "nr", "np", "nl", "nc", "nz", "ni", "ne", "ng", "nu", "nf", "mk", "mp", "no", "om", "pk", "pw", "ps",
    "pa", "pg", "py", "pe", "ph", "pn", "pl", "pt", "pr", "qa", "re", "ro", "ru", "rw", "bl", "sh", "kn", "lc", "mf",
    "pm", "vc", "ws", "sm", "st", "sa", "sn", "rs", "sc", "sl", "sg", "sx", "sk", "si", "sb", "so", "za", "gs", "ss",
    "es", "lk", "sd", "sr", "sj", "se", "ch", "sy", "tw", "tj", "tz", "th", "tl", "tg", "tk", "to", "tt", "tn", "tr",
    "tm", "tc", "tv", "ug", "ua", "ae", "gb", "us", "um", "uy", "uz", "vu", "ve", "vn", "vg", "vi", "wf", "eh", "ye",
    "zm", "zw",
]

class AniList:
    def __init__(self, requests):
        self.requests = requests
        self._options = None

    @property
    def options(self):
        if self._options:
            return self._options
        self._options = {
            "Tag": {}, "Tag Category": {},
            "Genre": {g.lower().replace(" ", "-"): g for g in self._request(genre_query, {})["data"]["GenreCollection"]},
            "Country": {c: c.upper() for c in country_codes},
            "Season": media_season, "Format": media_format, "Status": media_status, "Source": media_source,
        }
        for media_tag in self._request(tag_query, {})["data"]["MediaTagCollection"]:
            self._options["Tag"][media_tag["name"].lower().replace(" ", "-")] = media_tag["name"]
            self._options["Tag Category"][media_tag["category"].lower().replace(" ", "-")] = media_tag["category"]
        return self._options

    def _request(self, query, variables, level=1):
        logger.trace(f"Query: {query}")
        logger.trace(f"Variables: {variables}")
        response = self.requests.post(base_url, json={"query": query, "variables": variables})
        json_obj = response.json()
        logger.trace(f"Response: {json_obj}")
        if "errors" in json_obj:
            if json_obj['errors'][0]['message'] == "Too Many Requests.":
                wait_time = int(response.headers["Retry-After"]) if "Retry-After" in response.headers else 0
                time.sleep(wait_time if wait_time > 0 else 10)
                if level < 6:
                    return self._request(query, variables, level=level + 1)
                raise Failed(f"AniList Error: Connection Failed")
            else:
                raise Failed(f"AniList Error: {json_obj['errors'][0]['message']}")
        else:
            time.sleep(60 / 90)
        return json_obj

    def _validate_id(self, anilist_id):
        query = "query ($id: Int) {Media(id: $id) {id title{romaji english}}}"
        media = self._request(query, {"id": anilist_id})["data"]["Media"]
        if media["id"]:
            return media["id"], media["title"]["english" if media["title"]["english"] else "romaji"]
        raise Failed(f"AniList Error: No AniList ID found for {anilist_id}")

    def _pagenation(self, query, limit=0, variables=None):
        anilist_ids = []
        count = 0
        page_num = 0
        if variables is None:
            variables = {}
        next_page = True
        while next_page:
            page_num += 1
            variables["page"] = page_num
            json_obj = self._request(query, variables)
            next_page = json_obj["data"]["Page"]["pageInfo"]["hasNextPage"]
            for media in json_obj["data"]["Page"]["media"]:
                if media["id"]:
                    anilist_ids.append(media["id"])
                    count += 1
                    if 0 < limit == count:
                        break
            if 0 < limit == count:
                break
        return anilist_ids

    def _search(self, **kwargs):
        media_vars = f"sort: {sort_options[kwargs['sort_by']]}, type: ANIME"
        variables = {"sort": sort_options[kwargs['sort_by']]}
        for key, value in kwargs.items():
            if key not in ["sort_by", "limit"]:
                if "." in key:
                    attr, mod = key.split(".")
                else:
                    attr = key
                    mod = ""
                ani_attr = attr_translation[attr] if attr in attr_translation else attr
                final = ani_attr if attr in no_mod_searches else f"{ani_attr}_{mod_translation[mod]}"
                if attr in ["start", "end"]:
                    try:
                        value = int(util.validate_date(value, return_as="%Y%m%d"))
                    except Failed as e:
                        raise Failed(f"Collection Error: anilist_search {key}: {e}")
                elif attr in ["format", "status", "genre", "tag", "tag_category"]:
                    temp_value = [self.options[attr.replace('_', ' ').title()][v.lower().replace(' / ', '-').replace(' ', '-')] for v in value]
                    if attr in ["format", "status"]:
                        value = f"[{', '.join(temp_value)}]"
                    else:
                        temp = '", "'.join(temp_value)
                        value = f'["{temp}"]'
                elif attr in ["season", "source", "country"]:
                    value = self.options[attr.replace("_", " ").title()][value]
                if value is True:
                    value = "true"
                elif value is False:
                    value = "false"
                if mod == "gte":
                    value -= 1
                elif mod == "lte":
                    value += 1
                media_vars += f", {final}: {value}"
        query = f"query ($page: Int) {{Page(page: $page){{pageInfo {{hasNextPage}}media({media_vars}){{id}}}}}}"
        logger.debug(query)
        return self._pagenation(query, limit=kwargs["limit"], variables=variables)

    def _studio(self, studio_id):
        query = """
            query ($page: Int, $id: Int) {
              Studio(id: $id) {
                name
                media(page: $page) {
                  nodes {id type}
                  pageInfo {hasNextPage}
                }
              }
            }
        """
        anilist_ids = []
        page_num = 0
        next_page = True
        name = None
        while next_page:
            page_num += 1
            json_obj = self._request(query, {"id": studio_id, "page": page_num})
            if not name:
                name = json_obj["data"]["Studio"]["name"]
            next_page = json_obj["data"]["Studio"]["media"]["pageInfo"]["hasNextPage"]
            for media in json_obj["data"]["Studio"]["media"]["nodes"]:
                if media["id"] and media["type"] == "ANIME":
                    anilist_ids.append(media["id"])
        return anilist_ids, name

    def _relations(self, anilist_id, ignore_ids=None):
        query = """
            query ($id: Int) {
              Media(id: $id) {
                id
                relations {
                  edges {node{id type} relationType}
                  nodes {id type}
                }
              }
            }
        """
        new_anilist_ids = []
        anilist_ids = []
        name = ""
        if not ignore_ids:
            ignore_ids = [anilist_id]
            anilist_id, name = self._validate_id(anilist_id)
            anilist_ids.append(anilist_id)
        json_obj = self._request(query, {"id": anilist_id})
        edges = [media["node"]["id"] for media in json_obj["data"]["Media"]["relations"]["edges"]
                 if media["relationType"] not in ["CHARACTER", "OTHER"] and media["node"]["type"] == "ANIME"]
        for media in json_obj["data"]["Media"]["relations"]["nodes"]:
            if media["id"] and media["id"] not in ignore_ids and media["id"] in edges and media["type"] == "ANIME":
                new_anilist_ids.append(media["id"])
                ignore_ids.append(media["id"])
                anilist_ids.append(media["id"])

        for next_id in new_anilist_ids:
            new_relation_ids, ignore_ids, _ = self._relations(next_id, ignore_ids=ignore_ids)
            anilist_ids.extend(new_relation_ids)

        return anilist_ids, ignore_ids, name

    def _userlist(self, username, list_name, sort_by, score):
        query = """
            query ($user: String, $sort: [MediaListSort]) {
              MediaListCollection (userName: $user, sort: $sort, type: ANIME) {
                lists {
                  name 
                  entries {
                    score(format: POINT_10)
                    media{id}
                  }
                }
              }
            }
        """
        variables = {"user": username, "sort": userlist_sort_options[sort_by]}
        for alist in self._request(query, variables)["data"]["MediaListCollection"]["lists"]:
            if alist["name"] == list_name:
                return [m["media"]["id"] for m in alist["entries"] if not score or not any([util.is_number_filter(m["score"], mod, value) for mod, value in score.items()])]
        return []

    def validate_userlist(self, data):
        query = """
            query ($user: String) {
              MediaListCollection (userName: $user, type: ANIME) {
                lists {name}
              }
            }
        """
        variables = {"user": data["username"]}
        json_obj = self._request(query, variables)
        if not json_obj["data"]["MediaListCollection"]:
            raise Failed(f"AniList Error: User: {data['username']} not found")
        list_names = [n["name"] for n in json_obj["data"]["MediaListCollection"]["lists"]]
        if not list_names:
            raise Failed(f"AniList Error: User: {data['username']} has no Lists")
        if data["list_name"] in list_names:
            return data
        raise Failed(f"AniList Error: List: {data['list_name']} not found\nOptions: {', '.join(list_names)}")

    def validate(self, name, data):
        valid = []
        for d in util.get_list(data):
            if d.lower().replace(" / ", "-").replace(" ", "-") in self.options[name]:
                valid.append(d)
        if len(valid) > 0:
            return valid
        raise Failed(f"AniList Error: {name}: {data} does not exist\nOptions: {', '.join([v for k, v in self.options[name].items()])}")

    def validate_anilist_ids(self, anilist_ids, studio=False):
        anilist_id_list = util.get_int_list(anilist_ids, "AniList ID")
        anilist_values = []
        query = f"query ($id: Int) {{{'Studio(id: $id) {name}' if studio else 'Media(id: $id) {id}'}}}"
        for anilist_id in anilist_id_list:
            try:
                self._request(query, {"id": anilist_id})
                anilist_values.append(anilist_id)
            except Failed as e:     logger.error(e)
        if len(anilist_values) > 0:
            return anilist_values
        raise Failed(f"AniList Error: No valid AniList IDs in {anilist_ids}")

    def get_anilist_ids(self, method, data):
        if method == "anilist_id":
            logger.info(f"Processing AniList ID: {data}")
            anilist_id, name = self._validate_id(data)
            anilist_ids = [anilist_id]
        elif method == "anilist_studio":
            anilist_ids, name = self._studio(data)
            logger.info(f"Processing AniList Studio: ({data}) {name} ({len(anilist_ids)} Anime)")
        elif method == "anilist_relations":
            anilist_ids, _, name = self._relations(data)
            logger.info(f"Processing AniList Relations: ({data}) {name} ({len(anilist_ids)} Anime)")
        elif method == "anilist_userlist":
            anilist_ids = self._userlist(data["username"], data["list_name"], data["sort_by"], data["score"])
            logger.info(f"Processing AniList UserList: {data['list_name']} from {data['username']} sorted by {pretty_user[data['sort_by']]}")
        else:
            if method == "anilist_popular":
                data = {"limit": data, "popularity.gt": 3, "sort_by": "popular"}
            elif method == "anilist_trending":
                data = {"limit": data, "sort_by": "trending"}
            elif method == "anilist_top_rated":
                data = {"limit": data, "score.gt": 3, "sort_by": "score"}
            elif method not in builders:
                raise Failed(f"AniList Error: Method {method} not supported")
            message = f"Processing {method.replace('_', ' ').title().replace('Anilist', 'AniList')}:\n\tSort By {pretty_names[data['sort_by']]}"
            if data['limit'] > 0:
                message += f"\n\tLimit to {data['limit']} Anime"
            for key, value in data.items():
                if key not in ["limit", "sort_by"]:
                    if "." in key:
                        attr, mod = key.split(".")
                        mod = f".{mod}"
                    else:
                        attr = key
                        mod = ""
                    message += f"\n\t{attr.replace('_', ' ').title()} {util.mod_displays[mod]} {value}"
            logger.info(message)
            anilist_ids = self._search(**data)
        logger.debug("")
        logger.debug(f"{len(anilist_ids)} AniList IDs Found")
        logger.trace(f"IDs: {anilist_ids}")
        return anilist_ids
