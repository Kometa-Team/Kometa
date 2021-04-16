import logging, requests, time
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

builders = [
    "anilist_genre",
    "anilist_id",
    "anilist_popular",
    "anilist_relations",
    "anilist_season",
    "anilist_studio",
    "anilist_tag",
    "anilist_top_rated"
]
pretty_names = {
    "score": "Average Score",
    "popular": "Popularity"
}

class AniListAPI:
    def __init__(self, config):
        self.config = config
        self.url = "https://graphql.anilist.co"
        self.tags = {}
        self.genres = {}

        for tag in self.send_request("query{MediaTagCollection {name}}", {})["data"]["MediaTagCollection"]:
            self.tags[tag["name"].lower()] = tag["name"]
        for genre in self.send_request("query{GenreCollection}", {})["data"]["GenreCollection"]:
            self.genres[genre.lower()] = genre

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def post(self, query, variables):
        return requests.post(self.url, json={"query": query, "variables": variables})

    @retry(stop_max_attempt_number=2, retry_on_exception=util.retry_if_not_failed)
    def send_request(self, query, variables):
        response = self.post(query, variables)
        json_obj = response.json()
        if "errors" in json_obj:
            if json_obj['errors'][0]['message'] == "Too Many Requests.":
                if "Retry-After" in response.headers:
                    time.sleep(int(response.headers["Retry-After"]))
                raise ValueError
            else:
                raise Failed(f"AniList Error: {json_obj['errors'][0]['message']}")
        else:
            time.sleep(0.4)
        return json_obj

    def anilist_id(self, anilist_id):
        query = "query ($id: Int) {Media(id: $id) {id title{romaji english}}}"
        media = self.send_request(query, {"id": anilist_id})["data"]["Media"]
        if media["id"]:
            return media["id"], media["title"]["english" if media["title"]["english"] else "romaji"]
        raise Failed(f"AniList Error: No AniList ID found for {anilist_id}")

    def get_pagenation(self, query, limit=0, variables=None):
        anilist_ids = []
        count = 0
        page_num = 0
        if variables is None:
            variables = {}
        next_page = True
        while next_page:
            page_num += 1
            variables["page"] = page_num
            json_obj = self.send_request(query, variables)
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

    def top_rated(self, limit):
        query = """
            query ($page: Int) {
              Page(page: $page) {
                pageInfo {hasNextPage}
                media(averageScore_greater: 3, sort: SCORE_DESC, type: ANIME) {id}
              }
            }
        """
        return self.get_pagenation(query, limit=limit)

    def popular(self, limit):
        query = """
            query ($page: Int) {
              Page(page: $page) {
                pageInfo {hasNextPage}
                media(popularity_greater: 1000, sort: POPULARITY_DESC, type: ANIME) {id}
              }
            }
        """
        return self.get_pagenation(query, limit=limit)

    def season(self, season, year, sort, limit):
        query = """
            query ($page: Int, $season: MediaSeason, $year: Int, $sort: [MediaSort]) {
              Page(page: $page){
                pageInfo {hasNextPage}
                media(season: $season, seasonYear: $year, type: ANIME, sort: $sort){id}
              }
            }
        """
        variables = {"season": season.upper(), "year": year, "sort": "SCORE_DESC" if sort == "score" else "POPULARITY_DESC"}
        return self.get_pagenation(query, limit=limit, variables=variables)

    def genre(self, genre, sort, limit):
        query = """
            query ($page: Int, $genre: String, $sort: [MediaSort]) {
              Page(page: $page){
                pageInfo {hasNextPage}
                media(genre: $genre, sort: $sort){id}
              }
            }
        """
        variables = {"genre": genre, "sort": "SCORE_DESC" if sort == "score" else "POPULARITY_DESC"}
        return self.get_pagenation(query, limit=limit, variables=variables)

    def tag(self, tag, sort, limit):
        query = """
            query ($page: Int, $tag: String, $sort: [MediaSort]) {
              Page(page: $page){
                pageInfo {hasNextPage}
                media(tag: $tag, sort: $sort){id}
              }
            }
        """
        variables = {"tag": tag, "sort": "SCORE_DESC" if sort == "score" else "POPULARITY_DESC"}
        return self.get_pagenation(query, limit=limit, variables=variables)

    def studio(self, studio_id):
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
            json_obj = self.send_request(query, {"id": studio_id, "page": page_num})
            if not name:
                name = json_obj["data"]["Studio"]["name"]
            next_page = json_obj["data"]["Studio"]["media"]["pageInfo"]["hasNextPage"]
            for media in json_obj["data"]["Studio"]["media"]["nodes"]:
                if media["id"] and media["type"] == "ANIME":
                    anilist_ids.append(media["id"])
        return anilist_ids, name

    def relations(self, anilist_id, ignore_ids=None):
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
            anilist_id, name = self.anilist_id(anilist_id)
            anilist_ids.append(anilist_id)
        json_obj = self.send_request(query, {"id": anilist_id})
        edges = [media["node"]["id"] for media in json_obj["data"]["Media"]["relations"]["edges"]
                 if media["relationType"] not in ["CHARACTER", "OTHER"] and media["node"]["type"] == "ANIME"]
        for media in json_obj["data"]["Media"]["relations"]["nodes"]:
            if media["id"] and media["id"] not in ignore_ids and media["id"] in edges and media["type"] == "ANIME":
                new_anilist_ids.append(media["id"])
                ignore_ids.append(media["id"])
                anilist_ids.append(media["id"])

        for next_id in new_anilist_ids:
            new_relation_ids, ignore_ids, _ = self.relations(next_id, ignore_ids=ignore_ids)
            anilist_ids.extend(new_relation_ids)

        return anilist_ids, ignore_ids, name

    def validate_genre(self, genre):
        if genre.lower() in self.genres:
            return self.genres[genre.lower()]
        raise Failed(f"AniList Error: Genre: {genre} does not exist")

    def validate_tag(self, tag):
        if tag.lower() in self.tags:
            return self.tags[tag.lower()]
        raise Failed(f"AniList Error: Tag: {tag} does not exist")

    def validate_anilist_ids(self, anilist_ids, studio=False):
        anilist_values = []
        for anilist_id in anilist_ids:
            if studio:              query = "query ($id: Int) {Studio(id: $id) {name}}"
            else:                   query = "query ($id: Int) {Media(id: $id) {id}}"
            try:
                self.send_request(query, {"id": anilist_id})
                anilist_values.append(anilist_id)
            except Failed as e:     logger.error(e)
        if len(anilist_values) > 0:
            return anilist_values
        raise Failed(f"AniList Error: No valid AniList IDs in {anilist_ids}")

    def get_items(self, method, data, language, status_message=True):
        if status_message:
            logger.debug(f"Data: {data}")
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        if method == "anilist_id":
            anilist_id, name = self.anilist_id(data)
            anilist_ids = [anilist_id]
            if status_message:
                logger.info(f"Processing {pretty}: ({data}) {name}")
        elif method in ["anilist_popular", "anilist_top_rated"]:
            anilist_ids = self.popular(data) if method == "anilist_popular" else self.top_rated(data)
            if status_message:
                logger.info(f"Processing {pretty}: {data} Anime")
        elif method == "anilist_season":
            anilist_ids = self.season(data["season"], data["year"], data["sort_by"], data["limit"])
            if status_message:
                logger.info(f"Processing {pretty}: {data['limit'] if data['limit'] > 0 else 'All'} Anime from {util.pretty_seasons[data['season']]} {data['year']} sorted by {pretty_names[data['sort_by']]}")
        elif method == "anilist_genre":
            anilist_ids = self.genre(data["genre"], data["sort_by"], data["limit"])
            if status_message:
                logger.info(f"Processing {pretty}: {data['limit'] if data['limit'] > 0 else 'All'} Anime from the Genre: {data['genre']} sorted by {pretty_names[data['sort_by']]}")
        elif method == "anilist_tag":
            anilist_ids = self.tag(data["tag"], data["sort_by"], data["limit"])
            if status_message:
                logger.info(f"Processing {pretty}: {data['limit'] if data['limit'] > 0 else 'All'} Anime from the Tag: {data['tag']} sorted by {pretty_names[data['sort_by']]}")
        elif method in ["anilist_studio", "anilist_relations"]:
            if method == "anilist_studio":          anilist_ids, name = self.studio(data)
            else:                                   anilist_ids, _, name = self.relations(data)
            if status_message:
                logger.info(f"Processing {pretty}: ({data}) {name} ({len(anilist_ids)} Anime)")
        else:
            raise Failed(f"AniList Error: Method {method} not supported")
        movie_ids, show_ids = self.config.convert_anilist_list(anilist_ids, language)
        if status_message:
            logger.debug(f"AniList IDs Found: {anilist_ids}")
            logger.debug(f"Shows Found: {show_ids}")
            logger.debug(f"Movies Found: {movie_ids}")
        return movie_ids, show_ids
