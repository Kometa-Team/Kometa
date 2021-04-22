import logging, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class ArmsAPI:
    def __init__(self, config):
        self.config = config
        self.arms_url = "https://relations.yuna.moe/api/ids"
        self.anidb_url = "https://raw.githubusercontent.com/Anime-Lists/anime-lists/master/anime-list-master.xml"
        self.AniDBIDs = self._get_anidb()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _get_anidb(self):
        return html.fromstring(requests.get(self.anidb_url).content)

    def anidb_to_tvdb(self, anidb_id):          return self._anidb(anidb_id, "tvdbid")
    def anidb_to_imdb(self, anidb_id):          return self._anidb(anidb_id, "imdbid")
    def _anidb(self, input_id, to_id):
        ids = self.AniDBIDs.xpath(f"//anime[contains(@anidbid, '{input_id}')]/@{to_id}")
        if len(ids) > 0:
            try:
                if len(ids[0]) > 0:
                    return ids[0].split(",") if to_id == "imdbid" else int(ids[0])
                raise ValueError
            except ValueError:
                raise Failed(f"AniDB Error: No {util.pretty_ids[to_id]} ID found for AniDB ID: {input_id}")
        else:
            raise Failed(f"AniDB Error: AniDB ID: {input_id} not found")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def send_request(self, ids):
        return requests.post(self.arms_url, json=ids).json()

    def mal_to_anidb(self, mal_id):
        anime_ids = self._arms_ids(mal_ids=mal_id)
        if anime_ids[0] is None:
            raise Failed(f"Arms Server Error: MyAnimeList ID: {mal_id} does not exist")
        if anime_ids[0]["anidb"] is None:
            raise Failed(f"Arms Server Error: No AniDB ID for MyAnimeList ID: {mal_id}")
        return anime_ids[0]["anidb"]

    def anidb_to_ids(self, anidb_list, language):
        show_ids = []
        movie_ids = []
        for anidb_id in anidb_list:
            try:
                for imdb_id in self.anidb_to_imdb(anidb_id):
                    tmdb_id, _ = self.imdb_to_ids(imdb_id, language)
                    if tmdb_id:
                        movie_ids.append(tmdb_id)
                        break
                    else:
                        raise Failed
            except Failed:
                try:
                    tvdb_id = self.anidb_to_tvdb(anidb_id)
                    if tvdb_id:
                        show_ids.append(tvdb_id)
                except Failed:
                    logger.error(f"AniDB Error: No TVDb ID or IMDb ID found for AniDB ID: {anidb_id}")
        return movie_ids, show_ids

    def anilist_to_ids(self, anilist_ids, language):
        anidb_ids = []
        for id_set in self._arms_ids(anilist_ids=anilist_ids):
            if id_set["anidb"] is not None:
                anidb_ids.append(id_set["anidb"])
            else:
                logger.error(f"Convert Error: AniDB ID not found for AniList ID: {id_set['anilist']}")
        return self.anidb_to_ids(anidb_ids, language)

    def myanimelist_to_ids(self, mal_ids, language):
        anidb_ids = []
        for id_set in self._arms_ids(mal_ids=mal_ids):
            if id_set["anidb"] is not None:
                anidb_ids.append(id_set["anidb"])
            else:
                logger.error(f"Convert Error: AniDB ID not found for MyAnimeList ID: {id_set['myanimelist']}")
        return self.anidb_to_ids(anidb_ids, language)

    def _arms_ids(self, anilist_ids=None, anidb_ids=None, mal_ids=None):
        all_ids = []
        def collect_ids(ids, id_name):
            if ids:
                if isinstance(ids, list):
                    all_ids.extend([{id_name: a_id} for a_id in ids])
                else:
                    all_ids.append({id_name: ids})
        collect_ids(anilist_ids, "anilist")
        collect_ids(anidb_ids, "anidb")
        collect_ids(mal_ids, "myanimelist")
        converted_ids = []
        if self.config.Cache:
            unconverted_ids = []
            for anime_dict in all_ids:
                for id_type, anime_id in anime_dict.items():
                    query_ids, update = self.config.Cache.query_anime_map(anime_id, id_type)
                    if not update and query_ids:
                        converted_ids.append(query_ids)
                    else:
                        unconverted_ids.append({id_type: anime_id})
        else:
            unconverted_ids = all_ids

        for anime_ids in self.send_request(unconverted_ids):
            if anime_ids:
                if self.config.Cache:
                    self.config.Cache.update_anime(False, anime_ids)
                converted_ids.append(anime_ids)
        return converted_ids

    def imdb_to_ids(self, imdb_id, language):
        update_tmdb = False
        update_tvdb = False
        if self.config.Cache:
            tmdb_id, tvdb_id = self.config.Cache.get_ids_from_imdb(imdb_id)
            update_tmdb = False
            if not tmdb_id:
                tmdb_id, update_tmdb = self.config.Cache.get_tmdb_from_imdb(imdb_id)
                if update_tmdb:
                    tmdb_id = None
            update_tvdb = False
            if not tvdb_id:
                tvdb_id, update_tvdb = self.config.Cache.get_tvdb_from_imdb(imdb_id)
                if update_tvdb:
                    tvdb_id = None
        else:
            tmdb_id = None
            tvdb_id = None
        from_cache = tmdb_id is not None or tvdb_id is not None

        if not tmdb_id and not tvdb_id and self.config.TMDb:
            try:
                tmdb_id = self.config.TMDb.convert_imdb_to_tmdb(imdb_id)
            except Failed:
                pass
        if not tmdb_id and not tvdb_id and self.config.TMDb:
            try:
                tvdb_id = self.config.TMDb.convert_imdb_to_tvdb(imdb_id)
            except Failed:
                pass
        if not tmdb_id and not tvdb_id and self.config.Trakt:
            try:
                tmdb_id = self.config.Trakt.convert_imdb_to_tmdb(imdb_id)
            except Failed:
                pass
        if not tmdb_id and not tvdb_id and self.config.Trakt:
            try:
                tvdb_id = self.config.Trakt.convert_imdb_to_tvdb(imdb_id)
            except Failed:
                pass
        try:
            if tmdb_id and not from_cache:              self.config.TMDb.get_movie(tmdb_id)
        except Failed:                              tmdb_id = None
        try:
            if tvdb_id and not from_cache:              self.config.TVDb.get_series(language, tvdb_id)
        except Failed:                              tvdb_id = None
        if not tmdb_id and not tvdb_id:             raise Failed(f"IMDb Error: No TMDb ID or TVDb ID found for IMDb: {imdb_id}")
        if self.config.Cache:
            if tmdb_id and update_tmdb is not False:
                self.config.Cache.update_imdb("movie", update_tmdb, imdb_id, tmdb_id)
            if tvdb_id and update_tvdb is not False:
                self.config.Cache.update_imdb("show", update_tvdb, imdb_id, tvdb_id)
        return tmdb_id, tvdb_id
