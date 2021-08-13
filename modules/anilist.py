import logging, time
from modules import util
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

builders = [
    "anilist_genre", "anilist_id", "anilist_popular", "anilist_relations",
    "anilist_season", "anilist_studio", "anilist_tag", "anilist_top_rated"
]
pretty_names = {"score": "Average Score", "popular": "Popularity"}
search_translation = {
    "season": "MediaSeason", "seasonYear": "Int", "isAdult": "Boolean",
    "startDate_greater": "FuzzyDateInt", "startDate_lesser": "FuzzyDateInt", "endDate_greater": "FuzzyDateInt", "endDate_lesser": "FuzzyDateInt",
    "format_in": "[MediaFormat]", "format_not_in": "[MediaFormat]", "status_in": "[MediaStatus]", "status_not_in": "[MediaStatus]",
    "episodes_greater": "Int", "episodes_lesser": "Int", "duration_greater": "Int", "duration_lesser": "Int",
    "genre_in": "[String]", "genre_not_in": "[String]", "tag_in": "[String]", "tag_not_in": "[String]",
    "averageScore_greater": "Int", "averageScore_lesser": "Int", "popularity_greater": "Int", "popularity_lesser": "Int"
}
base_url = "https://graphql.anilist.co"
tag_query = "query{MediaTagCollection {name, category}}"
genre_query = "query{GenreCollection}"

class AniList:
    def __init__(self, config):
        self.config = config
        self.tags = {}
        self.categories = {}
        for media_tag in self._request(tag_query, {})["data"]["MediaTagCollection"]:
            self.tags[media_tag["name"].lower().replace(" ", "-")] = media_tag["name"]
            self.categories[media_tag["category"].lower().replace(" ", "-")] = media_tag["category"]
        self.genres = {g.lower().replace(" ", "-"): g for g in self._request(genre_query, {})["data"]["GenreCollection"]}

    def _request(self, query, variables):
        response = self.config.post(base_url, json={"query": query, "variables": variables})
        json_obj = response.json()
        if "errors" in json_obj:
            logger.debug(json_obj)
            if json_obj['errors'][0]['message'] == "Too Many Requests.":
                if "Retry-After" in response.headers:
                    time.sleep(int(response.headers["Retry-After"]))
                raise ValueError
            else:
                raise Failed(f"AniList Error: {json_obj['errors'][0]['message']}")
        else:
            time.sleep(0.4)
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

    def _top_rated(self, limit):
        return self._search(limit=limit, averageScore_greater=3)

    def _popular(self, limit):
        return self._search(sort="popular", limit=limit, popularity_greater=1000)

    def _season(self, season, year, sort, limit):
        return self._search(sort=sort, limit=limit, season=season.upper(), year=year)

    def _search(self, sort="score", limit=0, **kwargs):
        query_vars = "$page: Int, $sort: [MediaSort]"
        media_vars = "sort: $sort, type: ANIME"
        variables = {"sort": "SCORE_DESC" if sort == "score" else "POPULARITY_DESC"}
        for key, value in kwargs.items():
            query_vars += f", ${key}: {search_translation[key]}"
            media_vars += f", {key}: ${key}"
            variables[key] = value
        query = f"query ({query_vars}) {{Page(page: $page){{pageInfo {{hasNextPage}}media({media_vars}){{id}}}}}}"
        logger.info(query)
        return self._pagenation(query, limit=limit, variables=variables)

    def _genre(self, genre, sort, limit):
        return self._search(sort=sort, limit=limit, genre=genre)

    def _tag(self, tag, sort, limit):
        return self._search(sort=sort, limit=limit, tag=tag)

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

    def validate_tag(self, tag):
        return self._validate(tag, self.tags, "Tag")

    def validate_category(self, category):
        return self._validate(category, self.categories, "Category")

    def validate_genre(self, genre):
        return self._validate(genre, self.genres, "Genre")

    def _validate(self, data, options, name):
        data_check = data.lower().replace(" / ", "-").replace(" ", "-")
        if data_check in options:
            return options[data_check]
        raise Failed(f"AniList Error: {name}: {data} does not exist\nOptions: {', '.join([v for k, v in options.items()])}")

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
        elif method == "anilist_popular":
            logger.info(f"Processing AniList Popular: {data} Anime")
            anilist_ids = self._popular(data)
        elif method == "anilist_top_rated":
            logger.info(f"Processing AniList Top Rated: {data} Anime")
            anilist_ids = self._top_rated(data)
        elif method == "anilist_season":
            logger.info(f"Processing AniList Season: {data['limit'] if data['limit'] > 0 else 'All'} Anime from {util.pretty_seasons[data['season']]} {data['year']} sorted by {pretty_names[data['sort_by']]}")
            anilist_ids = self._season(data["season"], data["year"], data["sort_by"], data["limit"])
        elif method == "anilist_genre":
            logger.info(f"Processing AniList Genre: {data['limit'] if data['limit'] > 0 else 'All'} Anime from the Genre: {data['genre']} sorted by {pretty_names[data['sort_by']]}")
            anilist_ids = self._genre(data["genre"], data["sort_by"], data["limit"])
        elif method == "anilist_tag":
            logger.info(f"Processing AniList Tag: {data['limit'] if data['limit'] > 0 else 'All'} Anime from the Tag: {data['tag']} sorted by {pretty_names[data['sort_by']]}")
            anilist_ids = self._tag(data["tag"], data["sort_by"], data["limit"])
        elif method == "anilist_studio":
            anilist_ids, name = self._studio(data)
            logger.info(f"Processing AniList Studio: ({data}) {name} ({len(anilist_ids)} Anime)")
        elif method == "anilist_relations":
            anilist_ids, _, name = self._relations(data)
            logger.info(f"Processing AniList Relations: ({data}) {name} ({len(anilist_ids)} Anime)")
        else:
            raise Failed(f"AniList Error: Method {method} not supported")
        logger.debug("")
        logger.debug(f"{len(anilist_ids)} AniList IDs Found: {anilist_ids}")
        return anilist_ids
