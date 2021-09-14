import logging, re, requests
from modules import util
from modules.util import Failed
from plexapi.exceptions import BadRequest

logger = logging.getLogger("Plex Meta Manager")

anime_lists_url = "https://raw.githubusercontent.com/Fribb/anime-lists/master/anime-list-full.json"

class Convert:
    def __init__(self, config):
        self.config = config
        self.anidb_ids = {}
        self.mal_to_anidb = {}
        self.anilist_to_anidb = {}
        self.anidb_to_imdb = {}
        self.anidb_to_tvdb = {}
        for anime_id in self.config.get_json(anime_lists_url):
            if "anidb_id" in anime_id:
                self.anidb_ids[anime_id["anidb_id"]] = anime_id
                if "mal_id" in anime_id:
                    self.mal_to_anidb[int(anime_id["mal_id"])] = int(anime_id["anidb_id"])
                if "anilist_id" in anime_id:
                    self.anilist_to_anidb[int(anime_id["anilist_id"])] = int(anime_id["anidb_id"])
                if "imdb_id" in anime_id and str(anime_id["imdb_id"]).startswith("tt"):
                    self.anidb_to_imdb[int(anime_id["anidb_id"])] = util.get_list(anime_id["imdb_id"])
                if "thetvdb_id" in anime_id:
                    self.anidb_to_tvdb[int(anime_id["anidb_id"])] = int(anime_id["thetvdb_id"])

    def anidb_to_ids(self, anidb_ids, library):
        ids = []
        anidb_list = anidb_ids if isinstance(anidb_ids, list) else [anidb_ids]
        for anidb_id in anidb_list:
            if anidb_id in library.anidb_map:
                ids.append((library.anidb_map[anidb_id], "ratingKey"))
            elif anidb_id in self.anidb_to_imdb:
                added = False
                for imdb in self.anidb_to_imdb[anidb_id]:
                    tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                    if tmdb and tmdb_type == "movie":
                        ids.append((tmdb, "tmdb"))
                        added = True
                if added is False and anidb_id in self.anidb_to_tvdb:
                    ids.append((self.anidb_to_tvdb[anidb_id], "tvdb"))
            elif anidb_id in self.anidb_to_tvdb:
                ids.append((self.anidb_to_tvdb[anidb_id], "tvdb"))
            elif anidb_id in self.anidb_ids:
                logger.error(f"Convert Error: No TVDb ID or IMDb ID found for AniDB ID: {anidb_id}")
            else:
                logger.error(f"Convert Error: AniDB ID: {anidb_id} not found")
        return ids

    def anilist_to_ids(self, anilist_ids, library):
        anidb_ids = []
        for anilist_id in anilist_ids:
            if anilist_id in self.anilist_to_anidb:
                anidb_ids.append(self.anilist_to_anidb[anilist_id])
            else:
                logger.error(f"Convert Error: AniDB ID not found for AniList ID: {anilist_id}")
        return self.anidb_to_ids(anidb_ids, library)

    def myanimelist_to_ids(self, mal_ids, library):
        ids = []
        for mal_id in mal_ids:
            if int(mal_id) in library.mal_map:
                ids.append((library.mal_map[int(mal_id)], "ratingKey"))
            elif int(mal_id) in self.mal_to_anidb:
                ids.extend(self.anidb_to_ids(self.mal_to_anidb[int(mal_id)], library))
            else:
                logger.error(f"Convert Error: AniDB ID not found for MyAnimeList ID: {mal_id}")
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
        guid = requests.utils.urlparse(item.guid)
        item_type = guid.scheme.split(".")[-1]
        check_id = guid.netloc
        if self.config.Cache:
            cache_id, imdb_check, media_type, expired = self.config.Cache.query_guid_map(item.guid)
            if cache_id and not expired:
                media_id_type = "movie" if "movie" in media_type else "show"
                if item_type == "hama" and check_id.startswith("anidb"):
                    anidb_id = int(re.search("-(.*)", check_id).group(1))
                    library.anidb_map[anidb_id] = item.ratingKey
                elif item_type == "myanimelist":
                    library.mal_map[int(check_id)] = item.ratingKey
                return media_id_type, cache_id, imdb_check
        try:
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
                if check_id.startswith("tvdb"):
                    tvdb_id.append(int(re.search("-(.*)", check_id).group(1)))
                elif check_id.startswith("anidb"):
                    anidb_id = int(re.search("-(.*)", check_id).group(1))
                    library.anidb_map[anidb_id] = item.ratingKey
                else:
                    raise Failed(f"Hama Agent ID: {check_id} not supported")
            elif item_type == "myanimelist":
                library.mal_map[int(check_id)] = item.ratingKey
                if int(check_id) in self.mal_to_anidb:
                    anidb_id = self.mal_to_anidb[int(check_id)]
                else:
                    raise Failed(f"Convert Error: AniDB ID not found for MyAnimeList ID: {check_id}")
            elif item_type == "local":                      raise Failed("No match in Plex")
            else:                                           raise Failed(f"Agent {item_type} not supported")

            if anidb_id:
                if anidb_id in self.anidb_to_imdb:
                    added = False
                    for imdb in self.anidb_to_imdb[anidb_id]:
                        tmdb, tmdb_type = self.imdb_to_tmdb(imdb)
                        if tmdb and tmdb_type == "movie":
                            imdb_id.append(imdb)
                            tmdb_id.append(tmdb)
                            added = True
                    if added is False and anidb_id in self.anidb_to_tvdb:
                        tvdb_id.append(self.anidb_to_tvdb[anidb_id])
                elif anidb_id in self.anidb_to_tvdb:
                    tvdb_id.append(self.anidb_to_tvdb[anidb_id])
                else:
                    raise Failed(f"AniDB: {anidb_id} not found")
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
