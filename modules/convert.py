import re, requests
from modules import util
from modules.util import Failed, NonExisting
from plexapi.exceptions import BadRequest

logger = util.logger

anime_lists_url = "https://raw.githubusercontent.com/Kometa-Team/Anime-IDs/master/anime_ids.json"

class Convert:
    def __init__(self, config):
        self.config = config
        self._anidb_id = {}
        self._mal_to_anidb = {}
        self._anidb_to_mal = {}
        self._anilist_to_anidb = {}
        self._anidb_to_imdb = {}
        self._anidb_to_tvdb = {}
        self._anidb_to_tmdb = {}
        self._imdb_to_anidb = {}
        self._tvdb_to_anidb = {}
        self._tmdb_to_anidb = {}
        self._anidb_ids = self.config.get_json(anime_lists_url)
        for anidb_id, ids in self._anidb_ids.items():
            anidb_id = int(anidb_id)
            if "mal_id" in ids:
                for mal_id in util.get_list(ids["mal_id"], int_list=True):
                    if mal_id not in self._mal_to_anidb:
                        self._mal_to_anidb[mal_id] = [anidb_id]
                    else:
                        self._mal_to_anidb[mal_id].append(anidb_id)
                    if anidb_id not in self._anidb_to_mal:
                        self._anidb_to_mal[anidb_id] = [mal_id]
                    else:
                        self._anidb_to_mal[anidb_id].append(mal_id)
            if "anilist_id" in ids:
                for anilist_id in util.get_list(ids["anilist_id"], int_list=True):
                    if anilist_id not in self._anilist_to_anidb:
                        self._anilist_to_anidb[anilist_id] = [anidb_id]
                    else:
                        self._anilist_to_anidb[anilist_id].append(anidb_id)
            if "imdb_id" in ids:
                for imdb_id in util.get_list(ids["imdb_id"]):
                    if str(imdb_id).startswith("tt"):
                        if imdb_id not in self._imdb_to_anidb:
                            self._imdb_to_anidb[imdb_id] = [anidb_id]
                        else:
                            self._imdb_to_anidb[imdb_id].append(anidb_id)
                        if anidb_id not in self._anidb_to_imdb:
                            self._anidb_to_imdb[anidb_id] = [imdb_id]
                        else:
                            self._anidb_to_imdb[anidb_id].append(imdb_id)
            if "tvdb_id" in ids:
                tvdb_id = int(ids["tvdb_id"])
                if tvdb_id not in self._tvdb_to_anidb:
                    self._tvdb_to_anidb[tvdb_id] = [[anidb_id, int(ids["tvdb_season"]), int(ids["tvdb_epoffset"])]]
                else:
                    self._tvdb_to_anidb[tvdb_id].append([anidb_id, int(ids["tvdb_season"]), int(ids["tvdb_epoffset"])])
                if anidb_id not in self._anidb_to_tvdb:
                    self._anidb_to_tvdb[anidb_id] = [tvdb_id]
                else:
                    self._anidb_to_tvdb[anidb_id].append(tvdb_id)
            if "tmdb_movie_id" in ids:
                for tmdb_id in util.get_list(ids["tmdb_movie_id"], int_list=True):
                    if tmdb_id not in self._tmdb_to_anidb:
                        self._tmdb_to_anidb[tmdb_id] = [[anidb_id, "movie"]]
                    else:
                        self._tmdb_to_anidb[tmdb_id].append([[anidb_id, "movie"]])
                    if anidb_id not in self._anidb_to_mal:
                        self._anidb_to_tmdb[anidb_id] = [[tmdb_id, "movie"]]
                    else:
                        self._anidb_to_tmdb[anidb_id].append([tmdb_id, "movie"])
            if "tmdb_tv_id" in ids:
                for tmdb_id in util.get_list(ids["tmdb_tv_id"], int_list=True):
                    if tmdb_id not in self._tmdb_to_anidb:
                        self._tmdb_to_anidb[tmdb_id] = [[anidb_id, "show"]]
                    else:
                        self._tmdb_to_anidb[tmdb_id].append([[anidb_id, "show"]])
                    if anidb_id not in self._anidb_to_mal:
                        self._anidb_to_tmdb[anidb_id] = [[tmdb_id, "show"]]
                    else:
                        self._anidb_to_tmdb[anidb_id].append([tmdb_id, "show"])

    def anidb_to_imdb(self, anidb_id, fail=False):
        anidb_id = int(anidb_id)
        if anidb_id in self._anidb_to_imdb:
            return self._anidb_to_imdb[anidb_id]
        elif fail:
            raise Failed(f"IMDb ID not found for AniDB ID: {anidb_id}")
        else:
            return []

    def anidb_to_mal(self, anidb_id, fail=False):
        anidb_id = int(anidb_id)
        if anidb_id in self._anidb_to_mal:
            return self._anidb_to_mal[anidb_id]
        elif fail:
            raise Failed(f"MAL ID not found for AniDB ID: {anidb_id}")
        else:
            return []

    def anidb_to_tvdb(self, anidb_id, fail=False):
        anidb_id = int(anidb_id)
        if anidb_id in self._anidb_to_tvdb:
            return self._anidb_to_tvdb[anidb_id]
        elif fail:
            raise Failed(f"TVDb ID not found for AniDB ID: {anidb_id}")
        else:
            return []

    def anidb_to_tmdb(self, anidb_id, library_type=["movie","show"], fail=False):
        ids = []
        anidb_id = int(anidb_id)
        library_type = library_type if isinstance(library_type, list) else [library_type]
        if anidb_id in self._anidb_to_tmdb:
            for tmdb_id, tmdb_type in self._anidb_to_tmdb[anidb_id]:
                if (tmdb_type in library_type):
                    ids.append([tmdb_id, tmdb_type])
        if fail and not ids:
            raise Failed(f"TMDb ID not found for AniDB ID: {anidb_id}")
        return ids

    def anilist_to_anidb(self, anilist_id, fail=False):
        anilist_id = int(anilist_id)
        if anilist_id in self._anilist_to_anidb:
            return self._anilist_to_anidb[anilist_id]
        elif fail:
            raise Failed(f"AniDB ID not found for AniList ID: {anilist_id}")
        else:
            return []

    def imdb_to_anidb(self, imdb_id, fail=False):
        if imdb_id in self._imdb_to_anidb:
            return self._imdb_to_anidb[imdb_id]
        elif fail:
            raise Failed(f"AniDB ID not found for IMDb ID: {imdb_id}")
        else:
            return []

    def mal_to_anidb(self, mal_id, fail=False):
        mal_id = int(mal_id)
        if mal_id in self._mal_to_anidb:
            return self._mal_to_anidb[mal_id]
        elif fail:
            raise Failed(f"AniDB ID not found for MAL ID: {mal_id}")
        else:
            return []

    def tvdb_to_anidb(self, tvdb_id, season=[1,-1], epoffset=[0], fail=False):
        ids = []
        tvdb_id = int(tvdb_id)
        season = season if isinstance(season, list) else [season]
        epoffset = epoffset if isinstance(epoffset, list) else [epoffset]
        if tvdb_id in self._tvdb_to_anidb:
            for anidb_id, season_id, epoffset_id in self._tvdb_to_anidb[tvdb_id]:
                if (season_id in season and epoffset_id in epoffset):
                    ids.append([anidb_id, season_id, epoffset_id])
        if fail and not ids:
            raise Failed(f"AniDB ID not found for TVDb ID: {tvdb_id}")
        return ids

    def tmdb_to_anidb(self, tmdb_id, library_type=["movie","show"], fail=False):
        ids = []
        tmdb_id = int(tmdb_id)
        library_type = library_type if isinstance(library_type, list) else [library_type]
        if tmdb_id in self._tmdb_to_anidb:
            for anidb_id, tmdb_type in self._tmdb_to_anidb[tmdb_id]:
                if (tmdb_type in library_type):
                    ids.append([anidb_id, tmdb_type])
        if fail and not ids:
            raise Failed(f"AniDB ID not found for TMDb ID: {tmdb_id}")
        return ids

    def anidb_to_ids(self, anidb_ids, library):
        ids = []
        anidb_list = anidb_ids if isinstance(anidb_ids, list) else [anidb_ids]
        for anidb_id in anidb_list:
            added = False
            if anidb_id in library.anidb_map:
                added = True
                ids.append((library.anidb_map[anidb_id], "ratingKey"))
            for tmdb, tmdb_type in anidb_to_tmdb(anidb_id):
                added = True
                ids.append((int(tmdb), "tmdb", tmdb_type))
            for tvdb in anidb_to_tvdb(anidb_id):
                added = True
                ids.append((int(tvdb), "tvdb"))
            for imdb in anidb_to_imdb(anidb_id):
                ids.append((imdb, "imdb"))
                tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                if tmdb and tmdb_type:
                    added = True
                    ids.append((tmdb, "tmdb", tmdb_type))
            if not added and str(anidb_id) in self._anidb_ids:
                logger.warning(f"Convert Warning: No TVDb ID, IMDb ID, nor TMDb ID found for AniDB ID: {anidb_id}")
            elif not added:
                logger.error(f"AniDB Error: No Anime found for AniDB ID: {anidb_id}")
        return ids

    def anilist_to_ids(self, anilist_ids, library):
        anidb_ids = []
        for anilist_id in anilist_ids:
            anidb_id = self.anilist_to_anidb(anilist_id)
            if anidb_id:
                anidb_ids.append(anidb_id[0])
            else:
                logger.warning(f"Convert Warning: No AniDB ID Found for AniList ID: {anilist_id}")
        return self.anidb_to_ids(anidb_ids, library)

    def myanimelist_to_ids(self, mal_ids, library):
        ids = []
        for mal_id in mal_ids:
            if int(mal_id) in library.mal_map:
                ids.append((library.mal_map[int(mal_id)], "ratingKey"))
            else:
                anidb_id = self.mal_to_anidb(anilist_id)
                if anidb_id:
                    ids.extend(self.anidb_to_ids(anidb_id[0], library))
                else:
                    logger.warning(f"Convert Warning: No AniDB ID Found for MyAnimeList ID: {mal_id}")
        return ids

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
            raise Failed(f"Convert Warning: No IMDb ID Found for TMDb ID: {tmdb_id}")
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
            raise Failed(f"Convert Warning: No TMDb ID Found for IMDb ID: {imdb_id}")
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
            raise Failed(f"Convert Warning: No TVDb ID Found for TMDb ID: {tmdb_id}")
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
            raise Failed(f"Convert Warning: No TMDb ID Found for TVDb ID: {tvdb_id}")
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
            raise Failed(f"Convert Warning: No IMDb ID Found for TVDb ID: {tvdb_id}")
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
            raise Failed(f"Convert Warning: No TVDb ID Found for IMDb ID: {imdb_id}")
        else:
            return None

    def ids_from_cache(self, ratingKey, guid, item_type, check_id, library):
        media_id_type = None
        cache_id = None
        library_id = None
        imdb_check = None
        expired = None
        if self.config.Cache:
            cache_id, imdb_check, media_type, expired = self.config.Cache.query_guid_map(guid)
            if (cache_id or imdb_check) and not expired:
                media_id_type = "movie" if "movie" in media_type else "show"
                library_id = "TVDb" if "show" == media_type else "TMDb"
                if item_type == "hama" and check_id.startswith("anidb"):
                    anidb_id = int(re.search("-(.*)", check_id).group(1))
                    library.anidb_map[anidb_id] = ratingKey
                elif item_type == "myanimelist":
                    library.mal_map[int(check_id)] = ratingKey
        return media_id_type, cache_id, library_id, imdb_check, expired

    def scan_guid(self, guid_str):
        guid = requests.utils.urlparse(guid_str)
        return guid.scheme.split(".")[-1], guid.netloc

    def get_id(self, item, library):
        expired = None
        tmdb_movie_id = []
        tmdb_show_id = []
        tvdb_id = []
        imdb_id = []
        anidb_id = []
        item_type, check_id = self.scan_guid(item.guid)
        media_id_type, cache_id, library_id, imdb_check, expired = self.ids_from_cache(item.ratingKey, item.guid, item_type, check_id, library)
        if (cache_id or imdb_check) and expired is False:
            return media_id_type, cache_id, library_id, imdb_check
        try:
            if item_type == "plex":
                try:
                    for guid_tag in item.guids:
                        try:
                            url_parsed = requests.utils.urlparse(guid_tag.id)
                            if url_parsed.scheme == "tvdb":
                                tvdb_id.append(int(url_parsed.netloc))
                            elif url_parsed.scheme == "imdb":
                                imdb_id.append(url_parsed.netloc)
                            elif url_parsed.scheme == "tmdb" and check_id == "movie":
                                tmdb_movie_id.append(int(url_parsed.netloc))
                            elif url_parsed.scheme == "tmdb" and check_id == "show":
                                tmdb_show_id.append(int(url_parsed.netloc))
                        except ValueError:
                            pass
                except requests.exceptions.ConnectionError:
                    library.query(item.refresh)
                    logger.stacktrace()
                    raise Failed("No External GUIDs found")
                if not tvdb_id and not imdb_id and not tmdb_movie_id and not tmdb_show_id:
                    library.query(item.refresh)
                    raise Failed("Refresh Metadata")
            elif item_type == "imdb":                       imdb_id.append(check_id)
            elif item_type == "thetvdb":                    tvdb_id.append(int(check_id))
            elif item_type == "themoviedb":                 tmdb_movie_id.append(int(check_id))
            elif item_type in ["xbmcnfo", "xbmcnfotv"]:
                if len(check_id) > 10:
                    raise Failed(f"XMBC NFO Local ID: {check_id}")
                try:
                    if item_type == "xbmcnfo":
                        tmdb_movie_id.append(int(check_id))
                    else:
                        tvdb_id.append(int(check_id))
                except ValueError:
                    imdb_id.append(check_id)
            elif item_type == "hama":
                if check_id.startswith("tvdb"):
                    tvdb_id.append(int(re.search("-(.*)", check_id).group(1)))
                elif check_id.startswith("anidb"):
                    anidb_str = str(re.search("-(.*)", check_id).group(1))
                    anidb_id = [int(anidb_str[1:] if anidb_str[0] == "a" else anidb_str)]
                    library.anidb_map[anidb_id[0]] = item.ratingKey
                else:
                    raise Failed(f"Hama Agent ID: {check_id} not supported")
            elif item_type == "myanimelist":
                library.mal_map[int(check_id)] = item.ratingKey
                anidb_id = self.mal_to_anidb(check_id)
                if not anidb_id:
                    raise Failed(f"AniDB ID not found for MyAnimeList ID: {check_id}")
            elif item_type == "local":                      raise NonExisting("No match in Plex")
            else:                                           raise NonExisting(f"Agent {item_type} not supported")

            if anidb_id:
                added = False
                for anidb in anidb_id:
                    for tmdb, tmdb_type in self.anidb_to_tmdb(anidb):
                        added = True
                        if tmdb_type == "movie":
                            tmdb_movie_id.append(tmdb)
                        if tmdb_type == "show":
                            tmdb_show_id.append(tmdb)
                    for imdb in self.anidb_to_imdb(anidb):
                        imdb_id.append(imdb)
                        tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                        if tmdb:
                            added = True
                            if tmdb_type == "movie":
                                tmdb_movie_id.append(tmdb)
                            if tmdb_type == "show":
                                tmdb_show_id.append(tmdb)
                    for tvdb in self.anidb_to_tvdb(anidb):
                        added = True
                        tvdb_id.append(tvdb)
                if not added:
                    raise Failed(f"AniDB: {anidb_id} not found")
            else:
                if not tmdb_movie_id and imdb_id:
                    for imdb in imdb_id:
                        tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                        if tmdb_type == "movie":
                            tmdb_movie_id.append(tmdb)
                        if tmdb_type == "show":
                            tmdb_show_id.append(tmdb)

                if not imdb_id and tmdb_movie_id and library.is_movie:
                    for tmdb in tmdb_movie_id:
                        imdb = self.tmdb_to_imdb(tmdb)
                        if imdb:
                            imdb_id.append(imdb)

                if not tvdb_id and tmdb_show_id and library.is_show:
                    for tmdb in tmdb_show_id:
                        tvdb = self.tmdb_to_tvdb(tmdb)
                        if tvdb:
                            tvdb_id.append(int(tvdb))

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
                    logger.info(f" Cache  |  {'^' if expired else '+'}  | {ids} | {item.title}")
                    self.config.Cache.update_guid_map(item.guid, cache_ids, imdb_in, expired, guid_type)

            if (tmdb_movie_id or imdb_id) and library.is_movie:
                update_cache(tmdb_movie_id, "TMDb", imdb_id, "movie")
                return "movie", tmdb_movie_id, "TMDb", imdb_id
            elif (tvdb_id or imdb_id) and library.is_show:
                update_cache(tvdb_id, "TVDb", imdb_id, "show")
                return "show", tvdb_id, "TVDb", imdb_id
            elif anidb_id and tmdb_movie_id and library.is_show:
                update_cache(tmdb_movie_id, "TMDb", imdb_id, "show_movie")
                return "movie", tmdb_movie_id, "TMDb", imdb_id
            elif tmdb_show_id and library.is_show:
                update_cache(tmdb_show_id, "TMDb", imdb_id, "show_tmdb")
                return "show", tmdb_show_id, "TMDb", imdb_id
            else:
                logger.debug(f"TMDb: {tmdb_movie_id}, TMDb-Show: {tmdb_show_id}, IMDb: {imdb_id}, TVDb: {tvdb_id}")
                raise Failed(f"No ID to convert")
        except Failed as e:
            logger.info(f'Mapping Error | {item.guid:<46} | {e} for "{item.title}"')
        except NonExisting as e:
            if not library.is_other:
                logger.info(f'Mapping Error | {item.guid:<46} | {e} for "{item.title}"')
        except BadRequest:
            logger.stacktrace()
            logger.info(f'Mapping Error | {item.guid:<46} | Bad Request for "{item.title}"')
        return None, None, None, None
