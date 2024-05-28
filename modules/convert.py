import re
from modules import util
from modules.util import Failed, NonExisting
from modules.request import urlparse
from plexapi.exceptions import BadRequest
from requests.exceptions import ConnectionError

logger = util.logger

anime_lists_url = "https://raw.githubusercontent.com/Kometa-Team/Anime-IDs/master/anime_ids.json"

class Convert:
    def __init__(self, requests, cache, tmdb):
        self.requests = requests
        self.cache = cache
        self.tmdb = tmdb
        self._anidb_ids = {}
        self._mal_to_anidb = {}
        self._anidb_to_mal = {}
        self._anilist_to_anidb = {}
        self._anidb_to_imdb = {}
        self._anidb_to_tvdb = {}
        self._anidb_to_tmdb_movie = {}
        self._anidb_to_tmdb_show = {}
        self._tmdb_movie_to_anidb = {}
        self._tmdb_show_to_anidb = {}
        self._imdb_to_anidb = {}
        self._tvdb_to_anidb = {}
        self._anidb_ids = self.requests.get_json(anime_lists_url)
        for anidb_id, ids in self._anidb_ids.items():
            anidb_id = int(anidb_id)
            if "mal_id" in ids:
                for mal_id in util.get_list(ids["mal_id"], int_list=True):
                    self._mal_to_anidb[mal_id] = anidb_id
                    if anidb_id not in self._anidb_to_mal:
                        self._anidb_to_mal[anidb_id] = mal_id
            if "anilist_id" in ids:
                for anilist_id in util.get_list(ids["anilist_id"], int_list=True):
                    self._anilist_to_anidb[anilist_id] = anidb_id
            if "imdb_id" in ids and str(ids["imdb_id"]).startswith("tt"):
                self._anidb_to_imdb[anidb_id] = util.get_list(ids["imdb_id"])
                for im_id in util.get_list(ids["imdb_id"]):
                    self._imdb_to_anidb[im_id] = anidb_id
            if "tvdb_id" in ids:
                self._anidb_to_tvdb[anidb_id] = int(ids["tvdb_id"])
                if "tvdb_season" in ids and ids["tvdb_season"] in [1, -1] and ids["tvdb_epoffset"] == 0:
                    self._tvdb_to_anidb[int(ids["tvdb_id"])] = anidb_id
            if "tmdb_movie_id" in ids:
                self._anidb_to_tmdb_movie[anidb_id] = util.get_list(ids["tmdb_movie_id"])
                for tm_id in util.get_list(ids["tmdb_movie_id"]):
                    self._tmdb_movie_to_anidb[tm_id] = anidb_id
            if "tmdb_show_id" in ids:
                self._anidb_to_tmdb_show[anidb_id] = util.get_list(ids["tmdb_show_id"])
                for tm_id in util.get_list(ids["tmdb_show_id"]):
                    self._tmdb_show_to_anidb[tm_id] = anidb_id

    def imdb_to_anidb(self, imdb_id):
        if imdb_id in self._imdb_to_anidb:
            return self._imdb_to_anidb[imdb_id]
        else:
            raise Failed(f"AniDB ID not found for IMDb ID: {imdb_id}")

    def tvdb_to_anidb(self, tvdb_id):
        if int(tvdb_id) in self._tvdb_to_anidb:
            return self._tvdb_to_anidb[int(tvdb_id)]
        else:
            raise Failed(f"AniDB ID not found for TVDb ID: {tvdb_id}")

    def ids_to_anidb(self, library, rating_key, tvdb_id, imdb_id, tmdb_id):
        if rating_key in library.reverse_anidb:
            return library.reverse_anidb[rating_key]
        elif int(tvdb_id) in self._tvdb_to_anidb:
            return self._tvdb_to_anidb[int(tvdb_id)]
        else:
            tmdb_show_id = self.tvdb_to_tmdb(tvdb_id)
            if tmdb_show_id and tmdb_show_id in self._tmdb_show_to_anidb:
                return self._tmdb_show_to_anidb[tmdb_show_id]
            elif imdb_id in self._imdb_to_anidb:
                return self._imdb_to_anidb[imdb_id]
            elif tmdb_id in self._tmdb_movie_to_anidb:
                return self._tmdb_movie_to_anidb[tmdb_id]
            else:
                return None

    def anidb_to_mal(self, anidb_id):
        if anidb_id not in self._anidb_to_mal:
            raise Failed(f"Convert Warning: No MyAnimeList Found for AniDB ID: {anidb_id}")
        return self._anidb_to_mal[anidb_id]

    def anidb_to_ids(self, anidb_ids, library):
        ids = []
        anidb_list = anidb_ids if isinstance(anidb_ids, list) else [anidb_ids]
        for anidb_id in anidb_list:
            if anidb_id in library.anidb_map:
                ids.append((library.anidb_map[anidb_id], "ratingKey"))
            elif anidb_id in self._anidb_to_imdb:
                added = False
                for imdb in self._anidb_to_imdb[anidb_id]:
                    tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                    if tmdb and tmdb_type == "movie":
                        ids.append((tmdb, "tmdb"))
                        added = True
                if added is False and anidb_id in self._anidb_to_tvdb:
                    ids.append((self._anidb_to_tvdb[anidb_id], "tvdb"))
            elif anidb_id in self._anidb_to_tmdb_movie:
                added = False
                for tmdb_id in self._anidb_to_tmdb_movie[anidb_id]:
                    ids.append((tmdb_id, "tmdb"))
                    added = True
                if added is False and anidb_id in self._anidb_to_tvdb:
                    ids.append((self._anidb_to_tvdb[anidb_id], "tvdb"))
                ids.append((self._anidb_to_tmdb_movie[anidb_id], "tmdb"))
            elif anidb_id in self._anidb_to_tvdb:
                ids.append((self._anidb_to_tvdb[anidb_id], "tvdb"))
            elif anidb_id in self._anidb_to_tmdb_show:
                for tmdb_id in self._anidb_to_tmdb_show[anidb_id]:
                    try:
                        ids.append((int(self.tmdb_to_tvdb(tmdb_id, fail=True)), "tvdb"))
                    except Failed:
                        pass
                ids.append((self._anidb_to_tmdb_show[anidb_id], "tmdb"))
            elif str(anidb_id) in self._anidb_ids:
                logger.warning(f"Convert Warning: No TVDb ID or IMDb ID found for AniDB ID: {anidb_id}")
            else:
                logger.error(f"AniDB Error: No Anime found for AniDB ID: {anidb_id}")
        return ids

    def anilist_to_ids(self, anilist_ids, library):
        anidb_ids = []
        for anilist_id in anilist_ids:
            if anilist_id in self._anilist_to_anidb:
                anidb_ids.append(self._anilist_to_anidb[anilist_id])
            else:
                logger.warning(f"Convert Warning: No AniDB ID Found for AniList ID: {anilist_id}")
        return self.anidb_to_ids(anidb_ids, library)

    def myanimelist_to_ids(self, mal_ids, library):
        ids = []
        for mal_id in mal_ids:
            if int(mal_id) in library.mal_map:
                ids.append((library.mal_map[int(mal_id)], "ratingKey"))
            elif int(mal_id) in self._mal_to_anidb:
                ids.extend(self.anidb_to_ids(self._mal_to_anidb[int(mal_id)], library))
            else:
                logger.warning(f"Convert Warning: No AniDB ID Found for MyAnimeList ID: {mal_id}")
        return ids

    def tmdb_to_imdb(self, tmdb_id, is_movie=True, fail=False):
        media_type = "movie" if is_movie else "show"
        expired = False
        if self.cache and is_movie:
            cache_id, expired = self.cache.query_imdb_to_tmdb_map(tmdb_id, imdb=False, media_type=media_type)
            if cache_id and not expired:
                return cache_id
        try:
            imdb_id = self.tmdb.convert_from(tmdb_id, "imdb_id", is_movie)
            if imdb_id:
                if self.cache:
                    self.cache.update_imdb_to_tmdb_map(media_type, expired, imdb_id, tmdb_id)
                return imdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Warning: No IMDb ID Found for TMDb ID: {tmdb_id}")
        else:
            return None

    def imdb_to_tmdb(self, imdb_id, fail=False):
        expired = False
        if self.cache:
            cache_id, cache_type, expired = self.cache.query_imdb_to_tmdb_map(imdb_id, imdb=True, return_type=True)
            if cache_id and not expired:
                return cache_id, cache_type
        try:
            tmdb_id, tmdb_type = self.tmdb.convert_imdb_to(imdb_id)
            if tmdb_id:
                if self.cache:
                    self.cache.update_imdb_to_tmdb_map(tmdb_type, expired, imdb_id, tmdb_id)
                return tmdb_id, tmdb_type
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Warning: No TMDb ID Found for IMDb ID: {imdb_id}")
        else:
            return None, None

    def tmdb_to_tvdb(self, tmdb_id, fail=False):
        expired = False
        if self.cache:
            cache_id, expired = self.cache.query_tmdb_to_tvdb_map(tmdb_id, tmdb=True)
            if cache_id and not expired:
                return cache_id
        try:
            tvdb_id = self.tmdb.convert_from(tmdb_id, "tvdb_id", False)
            if tvdb_id:
                if self.cache:
                    self.cache.update_tmdb_to_tvdb_map(expired, tmdb_id, tvdb_id)
                return tvdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Warning: No TVDb ID Found for TMDb ID: {tmdb_id}")
        else:
            return None

    def tvdb_to_tmdb(self, tvdb_id, fail=False):
        expired = False
        if self.cache:
            cache_id, expired = self.cache.query_tmdb_to_tvdb_map(tvdb_id, tmdb=False)
            if cache_id and not expired:
                return cache_id
        try:
            tmdb_id = self.tmdb.convert_tvdb_to(tvdb_id)
            if tmdb_id:
                if self.cache:
                    self.cache.update_tmdb_to_tvdb_map(expired, tmdb_id, tvdb_id)
                return tmdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Warning: No TMDb ID Found for TVDb ID: {tvdb_id}")
        else:
            return None

    def tvdb_to_imdb(self, tvdb_id, fail=False):
        expired = False
        if self.cache:
            cache_id, expired = self.cache.query_imdb_to_tvdb_map(tvdb_id, imdb=False)
            if cache_id and not expired:
                return cache_id
        try:
            imdb_id = self.tmdb_to_imdb(self.tvdb_to_tmdb(tvdb_id, fail=True), is_movie=False, fail=True)
            if imdb_id:
                if self.cache:
                    self.cache.update_imdb_to_tvdb_map(expired, imdb_id, tvdb_id)
                return imdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Warning: No IMDb ID Found for TVDb ID: {tvdb_id}")
        else:
            return None

    def imdb_to_tvdb(self, imdb_id, fail=False):
        expired = False
        if self.cache:
            cache_id, expired = self.cache.query_imdb_to_tvdb_map(imdb_id, imdb=True)
            if cache_id and not expired:
                return cache_id
        try:
            tmdb_id, tmdb_type = self.imdb_to_tmdb(imdb_id, fail=True)
            if tmdb_type == "show":
                tvdb_id = self.tmdb_to_tvdb(tmdb_id, fail=True)
                if tvdb_id:
                    if self.cache:
                        self.cache.update_imdb_to_tvdb_map(expired, imdb_id, tvdb_id)
                    return tvdb_id
        except Failed:
            pass
        if fail:
            raise Failed(f"Convert Warning: No TVDb ID Found for IMDb ID: {imdb_id}")
        else:
            return None

    def ids_from_cache(self, rating_key, guid, item_type, check_id, library):
        media_id_type = None
        cache_id = None
        imdb_check = None
        expired = None
        if self.cache:
            cache_id, imdb_check, media_type, expired = self.cache.query_guid_map(guid)
            if (cache_id or imdb_check) and not expired:
                media_id_type = "movie" if "movie" in media_type else "show"
                if item_type == "hama" and check_id.startswith("anidb"):
                    anidb_id = int(re.search("-(.*)", check_id).group(1))
                    library.anidb_map[anidb_id] = rating_key
                elif item_type == "myanimelist":
                    library.mal_map[int(check_id)] = rating_key
        return media_id_type, cache_id, imdb_check, expired

    def scan_guid(self, guid_str):
        guid = urlparse(guid_str)
        return guid.scheme.split(".")[-1], guid.netloc

    def get_id(self, item, library):
        expired = None
        tmdb_id = []
        tvdb_id = []
        imdb_id = []
        anidb_id = None
        item_type, check_id = self.scan_guid(item.guid)
        media_id_type, cache_id, imdb_check, expired = self.ids_from_cache(item.ratingKey, item.guid, item_type, check_id, library)
        if (cache_id or imdb_check) and expired is False:
            return media_id_type, cache_id, imdb_check
        try:
            if item_type == "plex":
                try:
                    for guid_tag in item.guids:
                        try:
                            url_parsed = urlparse(guid_tag.id)
                            if url_parsed.scheme == "tvdb":                 tvdb_id.append(int(url_parsed.netloc))
                            elif url_parsed.scheme == "imdb":               imdb_id.append(url_parsed.netloc)
                            elif url_parsed.scheme == "tmdb":               tmdb_id.append(int(url_parsed.netloc))
                        except ValueError:
                            pass
                except ConnectionError:
                    library.query(item.refresh)
                    logger.stacktrace()
                    raise Failed("No External GUIDs found")
                if not tvdb_id and not imdb_id and not tmdb_id:
                    library.query(item.refresh)
                    raise Failed("Refresh Metadata")
            elif item_type == "imdb":                       imdb_id.append(check_id)
            elif item_type == "thetvdb":                    tvdb_id.append(int(check_id))
            elif item_type == "themoviedb":                 tmdb_id.append(int(check_id))
            elif item_type in ["xbmcnfo", "xbmcnfotv"]:
                if len(check_id) > 10:
                    raise Failed(f"XMBC NFO Local ID: {check_id}")
                try:
                    if item_type == "xbmcnfo":
                        tmdb_id.append(int(check_id))
                    else:
                        tvdb_id.append(int(check_id))
                except ValueError:
                    imdb_id.append(check_id)
            elif item_type == "hama":
                if check_id.startswith("tvdb"):
                    tvdb_id.append(int(re.search("-(.*)", check_id).group(1)))
                elif check_id.startswith("anidb"):
                    anidb_str = str(re.search("-(.*)", check_id).group(1))
                    anidb_id = int(anidb_str[1:] if anidb_str[0] == "a" else anidb_str)
                    library.anidb_map[anidb_id] = item.ratingKey
                else:
                    raise Failed(f"Hama Agent ID: {check_id} not supported")
            elif item_type == "myanimelist":
                library.mal_map[int(check_id)] = item.ratingKey
                if int(check_id) in self._mal_to_anidb:
                    anidb_id = self._mal_to_anidb[int(check_id)]
                else:
                    raise Failed(f"AniDB ID not found for MyAnimeList ID: {check_id}")
            elif item_type == "local":                      raise NonExisting("No match in Plex")
            else:                                           raise NonExisting(f"Agent {item_type} not supported")

            if anidb_id:
                if anidb_id in self._anidb_to_imdb:
                    added = False
                    for imdb in self._anidb_to_imdb[anidb_id]:
                        tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                        if tmdb and tmdb_type == "movie":
                            imdb_id.append(imdb)
                            tmdb_id.append(int(tmdb))
                            added = True
                    if added is False and anidb_id in self._anidb_to_tvdb:
                        tvdb_id.append(int(self._anidb_to_tvdb[anidb_id]))
                elif anidb_id in self._anidb_to_tvdb:
                    tvdb_id.append(int(self._anidb_to_tvdb[anidb_id]))
                else:
                    raise Failed(f"AniDB: {anidb_id} not found")
            else:
                if not tmdb_id and imdb_id:
                    for imdb in imdb_id:
                        tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                        if tmdb and ((tmdb_type == "movie" and library.is_movie) or (tmdb_type == "show" and library.is_show)):
                            tmdb_id.append(int(tmdb))

                if not imdb_id and tmdb_id and library.is_movie:
                    for tmdb in tmdb_id:
                        imdb = self.tmdb_to_imdb(tmdb)
                        if imdb:
                            imdb_id.append(imdb)

                if not tvdb_id and tmdb_id and library.is_show:
                    for tmdb in tmdb_id:
                        tvdb = self.tmdb_to_tvdb(tmdb)
                        if tvdb:
                            tvdb_id.append(int(tvdb))
                    if not tvdb_id:
                        raise Failed(f"Unable to convert TMDb ID: {', '.join([str(t) for t in tmdb_id])} to TVDb ID")

            if not imdb_id and tvdb_id:
                for tvdb in tvdb_id:
                    imdb = self.tvdb_to_imdb(tvdb)
                    if imdb:
                        imdb_id.append(imdb)

            def update_cache(cache_ids, id_type, imdb_in, guid_type):
                if self.cache:
                    cache_ids = ",".join([str(c) for c in cache_ids])
                    imdb_in = ",".join([str(i) for i in imdb_in]) if imdb_in else None
                    ids = f"{item.guid:<46} | {id_type} ID: {cache_ids:<7} | IMDb ID: {str(imdb_in):<10}"
                    logger.info(f" Cache  |  {'^' if expired else '+'}  | {ids} | {item.title}")
                    self.cache.update_guid_map(item.guid, cache_ids, imdb_in, expired, guid_type)

            if (tmdb_id or imdb_id) and library.is_movie:
                update_cache(tmdb_id, "TMDb", imdb_id, "movie")
                return "movie", tmdb_id, imdb_id
            elif (tvdb_id or imdb_id) and library.is_show:
                update_cache(tvdb_id, "TVDb", imdb_id, "show")
                return "show", tvdb_id, imdb_id
            elif anidb_id and (tmdb_id or imdb_id) and library.is_show:
                update_cache(tmdb_id, "TMDb", imdb_id, "show_movie")
                return "movie", tmdb_id, imdb_id
            else:
                logger.debug(f"TMDb: {tmdb_id}, IMDb: {imdb_id}, TVDb: {tvdb_id}")
                raise Failed(f"No ID to convert")
        except Failed as e:
            logger.info(f'Mapping Error | {item.guid:<46} | {e} for "{item.title}"')
        except NonExisting as e:
            if not library.is_other:
                logger.info(f'Mapping Error | {item.guid:<46} | {e} for "{item.title}"')
        except BadRequest:
            logger.stacktrace()
            logger.info(f'Mapping Error | {item.guid:<46} | Bad Request for "{item.title}"')
        return None, None, None
