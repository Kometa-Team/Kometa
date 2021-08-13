import logging, re, requests
from modules import util
from modules.util import Failed
from plexapi.exceptions import BadRequest

logger = logging.getLogger("Plex Meta Manager")

arms_url = "https://relations.yuna.moe/api/ids"
anidb_url = "https://raw.githubusercontent.com/Anime-Lists/anime-lists/master/anime-list-master.xml"

class Convert:
    def __init__(self, config):
        self.config = config
        self.AniDBIDs = self.config.get_html(anidb_url)

    def _anidb(self, anidb_id, fail=False):
        tvdbid = self.AniDBIDs.xpath(f"//anime[contains(@anidbid, '{anidb_id}')]/@tvdbid")
        imdbid = self.AniDBIDs.xpath(f"//anime[contains(@anidbid, '{anidb_id}')]/@imdbid")
        if len(tvdbid) > 0:
            if len(imdbid[0]) > 0:
                imdb_ids = util.get_list(imdbid[0])
                tmdb_ids = []
                for imdb in imdb_ids:
                    tmdb_id, tmdb_type = self.imdb_to_tmdb(imdb)
                    if tmdb_id and tmdb_type == "movie":
                        tmdb_ids.append(tmdb_id)
                if tmdb_ids:
                    return None, imdb_ids, tmdb_ids
                else:
                    fail_text = f"Convert Error: No TMDb ID found for AniDB ID: {anidb_id}"
            else:
                try:
                    return int(tvdbid[0]), [], []
                except ValueError:
                    fail_text = f"Convert Error: No TVDb ID or IMDb ID found for AniDB ID: {anidb_id}"
        else:
            fail_text = f"Convert Error: AniDB ID: {anidb_id} not found"
        if fail:
            raise Failed(fail_text)
        return None, [], []

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
        unconverted_ids = []
        unconverted_id_sets = []

        for anime_dict in all_ids:
            for id_type, anime_id in anime_dict.items():
                query_ids = None
                expired = None
                if self.config.Cache:
                    query_ids, expired = self.config.Cache.query_anime_map(anime_id, id_type)
                    if query_ids and not expired:
                        converted_ids.append(query_ids)
                if query_ids is None or expired:
                    unconverted_ids.append(anime_dict)
                    if len(unconverted_ids) == 100:
                        unconverted_id_sets.append(unconverted_ids)
                        unconverted_ids = []
        if len(unconverted_ids) > 0:
            unconverted_id_sets.append(unconverted_ids)
        for unconverted_id_set in unconverted_id_sets:
            for anime_ids in self.config.post_json(arms_url, json=unconverted_id_set):
                if anime_ids:
                    if self.config.Cache:
                        self.config.Cache.update_anime_map(False, anime_ids)
                    converted_ids.append(anime_ids)
        return converted_ids

    def anidb_to_ids(self, anidb_list):
        ids = []
        for anidb_id in anidb_list:
            try:
                tvdb_id, _, tmdb_ids = self._anidb(anidb_id, fail=True)
                if tvdb_id:
                    ids.append((tvdb_id, "tvdb"))
                if tmdb_ids:
                    ids.extend((tmdb_ids, "tmdb"))
            except Failed as e:
                logger.error(e)
        return ids

    def anilist_to_ids(self, anilist_ids):
        anidb_ids = []
        for id_set in self._arms_ids(anilist_ids=anilist_ids):
            if id_set["anidb"] is not None:
                anidb_ids.append(id_set["anidb"])
            else:
                logger.error(f"Convert Error: AniDB ID not found for AniList ID: {id_set['anilist']}")
        return self.anidb_to_ids(anidb_ids)

    def myanimelist_to_ids(self, mal_ids):
        anidb_ids = []
        for id_set in self._arms_ids(mal_ids=mal_ids):
            if id_set["anidb"] is not None:
                anidb_ids.append(id_set["anidb"])
            else:
                logger.error(f"Convert Error: AniDB ID not found for MyAnimeList ID: {id_set['myanimelist']}")
        return self.anidb_to_ids(anidb_ids)

    def tmdb_to_imdb(self, tmdb_id, is_movie=True, fail=False):
        media_type = "movie" if is_movie else "show"
        expired = False
        if self.config.Cache and is_movie:
            cache_id, expired = self.config.Cache.query_imdb_to_tmdb_map(tmdb_id, imdb=False, media_type=media_type)
            if cache_id and not expired:
                return cache_id
        try:
            imdb_id = self.config.TMDb.convert_from(tmdb_id, "imdb_id", is_movie)
            if imdb_id:
                if self.config.Cache:
                    self.config.Cache.update_imdb_to_tmdb_map(media_type, expired, imdb_id, tmdb_id)
                return imdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Error: No IMDb ID Found for TMDb ID: {tmdb_id}")
        else:
            return None

    def imdb_to_tmdb(self, imdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, cache_type, expired = self.config.Cache.query_imdb_to_tmdb_map(imdb_id, imdb=True, return_type=True)
            if cache_id and not expired:
                return cache_id, cache_type
        try:
            tmdb_id, tmdb_type = self.config.TMDb.convert_imdb_to(imdb_id)
            if tmdb_id:
                if self.config.Cache:
                    self.config.Cache.update_imdb_to_tmdb_map(tmdb_type, expired, imdb_id, tmdb_id)
                return tmdb_id, tmdb_type
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Error: No TMDb ID Found for IMDb ID: {imdb_id}")
        else:
            return None, None

    def tmdb_to_tvdb(self, tmdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, expired = self.config.Cache.query_tmdb_to_tvdb_map(tmdb_id, tmdb=True)
            if cache_id and not expired:
                return cache_id
        try:
            tvdb_id = self.config.TMDb.convert_from(tmdb_id, "tvdb_id", False)
            if tvdb_id:
                if self.config.Cache:
                    self.config.Cache.update_tmdb_to_tvdb_map(expired, tmdb_id, tvdb_id)
                return tvdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Error: No TVDb ID Found for TMDb ID: {tmdb_id}")
        else:
            return None

    def tvdb_to_tmdb(self, tvdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, expired = self.config.Cache.query_tmdb_to_tvdb_map(tvdb_id, tmdb=False)
            if cache_id and not expired:
                return cache_id
        try:
            tmdb_id = self.config.TMDb.convert_tvdb_to(tvdb_id)
            if tmdb_id:
                if self.config.Cache:
                    self.config.Cache.update_tmdb_to_tvdb_map(expired, tmdb_id, tvdb_id)
                return tmdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Error: No TMDb ID Found for TVDb ID: {tvdb_id}")
        else:
            return None

    def tvdb_to_imdb(self, tvdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, expired = self.config.Cache.query_imdb_to_tvdb_map(tvdb_id, imdb=False)
            if cache_id and not expired:
                return cache_id
        try:
            imdb_id = self.tmdb_to_imdb(self.tvdb_to_tmdb(tvdb_id, fail=True), is_movie=False, fail=True)
            if imdb_id:
                if self.config.Cache:
                    self.config.Cache.update_imdb_to_tvdb_map(expired, imdb_id, tvdb_id)
                return imdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Error: No IMDb ID Found for TVDb ID: {tvdb_id}")
        else:
            return None

    def imdb_to_tvdb(self, imdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, expired = self.config.Cache.query_imdb_to_tvdb_map(imdb_id, imdb=True)
            if cache_id and not expired:
                return cache_id
        try:
            tmdb_id, tmdb_type = self.imdb_to_tmdb(imdb_id, fail=True)
            if tmdb_type == "show":
                tvdb_id = self.tmdb_to_tvdb(tmdb_id, fail=True)
                if tvdb_id:
                    if self.config.Cache:
                        self.config.Cache.update_imdb_to_tvdb_map(expired, imdb_id, tvdb_id)
                    return tvdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Error: No TVDb ID Found for IMDb ID: {imdb_id}")
        else:
            return None

    def get_id(self, item, library):
        expired = None
        tmdb_id = []
        tvdb_id = []
        imdb_id = []
        anidb_id = None
        if self.config.Cache:
            cache_id, imdb_check, media_type, expired = self.config.Cache.query_guid_map(item.guid)
            if cache_id and not expired:
                media_id_type = "movie" if "movie" in media_type else "show"
                return media_id_type, cache_id, imdb_check
        try:
            guid = requests.utils.urlparse(item.guid)
            item_type = guid.scheme.split(".")[-1]
            check_id = guid.netloc

            if item_type == "plex":
                try:
                    for guid_tag in library.get_guids(item):
                        url_parsed = requests.utils.urlparse(guid_tag.id)
                        if url_parsed.scheme == "tvdb":                 tvdb_id.append(int(url_parsed.netloc))
                        elif url_parsed.scheme == "imdb":               imdb_id.append(url_parsed.netloc)
                        elif url_parsed.scheme == "tmdb":               tmdb_id.append(int(url_parsed.netloc))
                except requests.exceptions.ConnectionError:
                    library.query(item.refresh)
                    util.print_stacktrace()
                    raise Failed("No External GUIDs found")
                if not tvdb_id and not imdb_id and not tmdb_id:
                    library.query(item.refresh)
                    raise Failed("Refresh Metadata")
            elif item_type == "imdb":                       imdb_id.append(check_id)
            elif item_type == "thetvdb":                    tvdb_id.append(int(check_id))
            elif item_type == "themoviedb":                 tmdb_id.append(int(check_id))
            elif item_type == "hama":
                if check_id.startswith("tvdb"):             tvdb_id.append(int(re.search("-(.*)", check_id).group(1)))
                elif check_id.startswith("anidb"):          anidb_id = re.search("-(.*)", check_id).group(1)
                else:                                       raise Failed(f"Hama Agent ID: {check_id} not supported")
            elif item_type == "myanimelist":
                anime_ids = self._arms_ids(mal_ids=check_id)
                if anime_ids[0] and anime_ids[0]["anidb"]:      anidb_id = anime_ids[0]["anidb"]
                else:                                           raise Failed(f"Unable to convert MyAnimeList ID: {check_id} to AniDB ID")
            elif item_type == "local":                      raise Failed("No match in Plex")
            else:                                           raise Failed(f"Agent {item_type} not supported")

            if anidb_id:
                ani_tvdb, ani_imdb, ani_tmdb = self._anidb(anidb_id, fail=True)
                if ani_imdb:
                    imdb_id.extend(ani_imdb)
                if ani_tmdb:
                    tmdb_id.extend(ani_tmdb)
                if ani_tvdb:
                    tvdb_id.append(ani_tvdb)
            else:
                if not tmdb_id and imdb_id:
                    for imdb in imdb_id:
                        tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                        if tmdb and ((tmdb_type == "movie" and library.is_movie) or (tmdb_type == "show" and library.is_show)):
                            tmdb_id.append(tmdb)

                if not imdb_id and tmdb_id and library.is_movie:
                    for tmdb in tmdb_id:
                        imdb = self.tmdb_to_imdb(tmdb)
                        if imdb:
                            imdb_id.append(imdb)

                if not tvdb_id and tmdb_id and library.is_show:
                    for tmdb in tmdb_id:
                        tvdb = self.tmdb_to_tvdb(tmdb)
                        if tvdb:
                            tvdb_id.append(tvdb)
                    if not tvdb_id:
                        raise Failed(f"Unable to convert TMDb ID: {', '.join([str(t) for t in tmdb_id])} to TVDb ID")

            if not imdb_id and tvdb_id:
                for tvdb in tvdb_id:
                    imdb = self.tvdb_to_imdb(tvdb)
                    if imdb:
                        imdb_id.append(imdb)

            def update_cache(cache_ids, id_type, imdb_in, guid_type):
                if self.config.Cache:
                    cache_ids = ",".join([str(c) for c in cache_ids])
                    imdb_in = ",".join([str(i) for i in imdb_in]) if imdb_in else None
                    ids = f"{item.guid:<46} | {id_type} ID: {cache_ids:<7} | IMDb ID: {str(imdb_in):<10}"
                    logger.info(util.adjust_space(f" Cache  |  {'^' if expired else '+'}  | {ids} | {item.title}"))
                    self.config.Cache.update_guid_map(item.guid, cache_ids, imdb_in, expired, guid_type)

            if tmdb_id and library.is_movie:
                update_cache(tmdb_id, "TMDb", imdb_id, "movie")
                return "movie", tmdb_id, imdb_id
            elif tvdb_id and library.is_show:
                update_cache(tvdb_id, "TVDb", imdb_id, "show")
                return "show", tvdb_id, imdb_id
            elif anidb_id and tmdb_id and library.is_show:
                update_cache(tmdb_id, "TMDb", imdb_id, "show_movie")
                return "movie", tmdb_id, imdb_id
            else:
                logger.debug(f"TMDb: {tmdb_id}, IMDb: {imdb_id}, TVDb: {tvdb_id}")
                raise Failed(f"No ID to convert")
        except Failed as e:
            logger.info(util.adjust_space(f"Mapping Error | {item.guid:<46} | {e} for {item.title}"))
        except BadRequest:
            util.print_stacktrace()
            logger.info(util.adjust_space(f"Mapping Error | {item.guid:<46} | Bad Request for {item.title}"))
        return None, None, None
