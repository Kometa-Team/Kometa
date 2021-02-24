import logging, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class AniDBAPI:
    def __init__(self, Cache=None, TMDb=None, Trakt=None):
        self.Cache = Cache
        self.TMDb = TMDb
        self.Trakt = Trakt
        self.urls = {
            "anime": "https://anidb.net/anime",
            "popular": "https://anidb.net/latest/anime/popular/?h=1",
            "relation": "/relation/graph"
        }
        self.id_list = html.fromstring(requests.get("https://raw.githubusercontent.com/Anime-Lists/anime-lists/master/anime-list-master.xml").content)

    def convert_anidb_to_tvdb(self, anidb_id):          return self.convert_anidb(anidb_id, "anidbid", "tvdbid")
    def convert_anidb_to_imdb(self, anidb_id):          return self.convert_anidb(anidb_id, "anidbid", "imdbid")
    def convert_tvdb_to_anidb(self, tvdb_id):           return self.convert_anidb(tvdb_id, "tvdbid", "anidbid")
    def convert_imdb_to_anidb(self, imdb_id):           return self.convert_anidb(imdb_id, "imdbid", "anidbid")
    def convert_anidb(self, input_id, from_id, to_id):
        ids = self.id_list.xpath("//anime[contains(@{}, '{}')]/@{}".format(from_id, input_id, to_id))
        if len(ids) > 0:
            if from_id == "tvdbid":                             return [int(i) for i in ids]
            if len(ids[0]) > 0:
                try:                                                return ids[0].split(",") if to_id == "imdbid" else int(ids[0])
                except ValueError:                                  raise Failed("AniDB Error: No {} ID found for {} ID: {}".format(util.pretty_ids[to_id], util.pretty_ids[from_id], input_id))
            else:                                               raise Failed("AniDB Error: No {} ID found for {} ID: {}".format(util.pretty_ids[to_id], util.pretty_ids[from_id], input_id))
        else:                                               raise Failed("AniDB Error: {} ID: {} not found".format(util.pretty_ids[from_id], input_id))

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_request(self, url, language):
        return html.fromstring(requests.get(url, headers={"Accept-Language": language, "User-Agent": "Mozilla/5.0 x64"}).content)

    def get_popular(self, language):
        response = self.send_request(self.urls["popular"], language)
        return util.get_int_list(response.xpath("//td[@class='name anime']/a/@href"), "AniDB ID")

    def validate_anidb_id(self, anidb_id, language):
        response = self.send_request("{}/{}".format(self.urls["anime"], anidb_id), language)
        ids = response.xpath("//*[text()='a{}']/text()".format(anidb_id))
        if len(ids) > 0:
            return util.regex_first_int(ids[0], "AniDB ID")
        raise Failed("AniDB Error: AniDB ID: {} not found".format(anidb_id))

    def get_anidb_relations(self, anidb_id, language):
        response = self.send_request("{}/{}{}".format(self.urls["anime"], anidb_id, self.urls["relation"]), language)
        return util.get_int_list(response.xpath("//area/@href"), "AniDB ID")

    def validate_anidb_list(self, anidb_list, language):
        anidb_values = []
        for anidb_id in anidb_list:
            try:
                anidb_values.append(self.validate_anidb_id(anidb_id, language))
            except Failed as e:
                logger.error(e)
        if len(anidb_values) > 0:
            return anidb_values
        raise Failed("AniDB Error: No valid AniDB IDs in {}".format(anidb_list))

    def get_items(self, method, data, language, status_message=True):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        if status_message:
            logger.debug("Data: {}".format(data))
        anime_ids = []
        if method == "anidb_popular":
            if status_message:
                logger.info("Processing {}: {} Anime".format(pretty, data))
            anime_ids.extend(self.get_popular(language)[:data])
        else:
            if status_message:                                  logger.info("Processing {}: {}".format(pretty, data))
            if method == "anidb_id":                            anime_ids.append(data)
            elif method == "anidb_relation":                    anime_ids.extend(self.get_anidb_relations(data, language))
            else:                                               raise Failed("AniDB Error: Method {} not supported".format(method))
        show_ids = []
        movie_ids = []
        for anidb_id in anime_ids:
            try:
                tmdb_id = self.convert_from_imdb(self.convert_anidb_to_imdb(anidb_id))
                if tmdb_id:                                         movie_ids.append(tmdb_id)
                else:                                               raise Failed
            except Failed:
                try:                                                show_ids.append(self.convert_anidb_to_tvdb(anidb_id))
                except Failed:                                      logger.error("AniDB Error: No TVDb ID or IMDb ID found for AniDB ID: {}".format(anidb_id))
        if status_message:
            logger.debug("AniDB IDs Found: {}".format(anime_ids))
            logger.debug("TMDb IDs Found: {}".format(movie_ids))
            logger.debug("TVDb IDs Found: {}".format(show_ids))
        return movie_ids, show_ids

    def convert_from_imdb(self, imdb_id):
        output_tmdb_ids = []
        if not isinstance(imdb_id, list):
            imdb_id = [imdb_id]

        for imdb in imdb_id:
            expired = False
            if self.Cache:
                tmdb_id, tvdb_id = self.Cache.get_ids_from_imdb(imdb)
                if not tmdb_id:
                    tmdb_id, expired = self.Cache.get_tmdb_from_imdb(imdb)
                    if expired:
                        tmdb_id = None
            else:
                tmdb_id = None
            from_cache = tmdb_id is not None

            if not tmdb_id and self.TMDb:
                try:                                        tmdb_id = self.TMDb.convert_imdb_to_tmdb(imdb)
                except Failed:                              pass
            if not tmdb_id and self.Trakt:
                try:                                        tmdb_id = self.Trakt.convert_imdb_to_tmdb(imdb)
                except Failed:                              pass
            try:
                if tmdb_id and not from_cache:              self.TMDb.get_movie(tmdb_id)
            except Failed:                              tmdb_id = None
            if tmdb_id:                                 output_tmdb_ids.append(tmdb_id)
            if self.Cache and tmdb_id and expired is not False:
                self.Cache.update_imdb("movie", expired, imdb, tmdb_id)
        if len(output_tmdb_ids) == 0:               raise Failed("AniDB Error: No TMDb ID found for IMDb: {}".format(imdb_id))
        elif len(output_tmdb_ids) == 1:             return output_tmdb_ids[0]
        else:                                       return output_tmdb_ids
