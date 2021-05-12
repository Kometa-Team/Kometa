import logging, re, requests
from lxml import html
from modules import util
from modules.util import Failed
from retrying import retry

logger = logging.getLogger("Plex Meta Manager")

class Convert:
    def __init__(self, config):
        self.config = config
        self.arms_url = "https://relations.yuna.moe/api/ids"
        self.anidb_url = "https://raw.githubusercontent.com/Anime-Lists/anime-lists/master/anime-list-master.xml"
        self.AniDBIDs = self._get_anidb()

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _get_anidb(self):
        return html.fromstring(requests.get(self.anidb_url).content)

    def _anidb(self, input_id, to_id, fail=False):
        ids = self.AniDBIDs.xpath(f"//anime[contains(@anidbid, '{input_id}')]/@{to_id}")
        if len(ids) > 0:
            try:
                if len(ids[0]) > 0:
                    return util.get_list(ids[0]) if to_id == "imdbid" else int(ids[0])
                raise ValueError
            except ValueError:
                fail_text = f"Convert Error: No {util.pretty_ids[to_id]} ID found for AniDB ID: {input_id}"
        else:
            fail_text = f"Convert Error: AniDB ID: {input_id} not found"
        if fail:
            raise Failed(fail_text)
        return [] if to_id == "imdbid" else None

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _request(self, ids):
        return requests.post(self.arms_url, json=ids).json()

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
            if self.config.Cache:
                for id_type, anime_id in anime_dict.items():
                    query_ids, expired = self.config.Cache.query_anime_map(anime_id, id_type)
                    if query_ids and not expired:
                        converted_ids.append(query_ids)
                    else:
                        unconverted_ids.append({id_type: anime_id})
                        if len(unconverted_ids) == 100:
                            unconverted_id_sets.append(unconverted_ids)
                            unconverted_ids = []
            else:
                unconverted_ids.append(anime_dict)
                if len(unconverted_ids) == 100:
                    unconverted_id_sets.append(unconverted_ids)
                    unconverted_ids = []
        for unconverted_id_set in unconverted_id_sets:
            for anime_ids in self._request(unconverted_id_set):
                if anime_ids:
                    if self.config.Cache:
                        self.config.Cache.update_anime_map(False, anime_ids)
                    converted_ids.append(anime_ids)
        return converted_ids

    def anidb_to_ids(self, anidb_list):
        show_ids = []
        movie_ids = []
        for anidb_id in anidb_list:
            imdb_ids = self.anidb_to_imdb(anidb_id)
            tmdb_ids = []
            if imdb_ids:
                for imdb_id in imdb_ids:
                    tmdb_id = self.imdb_to_tmdb(imdb_id)
                    if tmdb_id:
                        tmdb_ids.append(tmdb_id)
            tvdb_id = self.anidb_to_tvdb(anidb_id)
            if tvdb_id:
                show_ids.append(tvdb_id)
            if tmdb_ids:
                movie_ids.extend(tmdb_ids)
            if not tvdb_id and not tmdb_ids:
                logger.error(f"Convert Error: No TVDb ID or IMDb ID found for AniDB ID: {anidb_id}")
        return movie_ids, show_ids

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

    def anidb_to_tvdb(self, anidb_id, fail=False):
        return self._anidb(anidb_id, "tvdbid", fail=fail)

    def anidb_to_imdb(self, anidb_id, fail=False):
        return self._anidb(anidb_id, "imdbid", fail=fail)

    def tmdb_to_imdb(self, tmdb_id, is_movie=True, fail=False):
        media_type = "movie" if is_movie else "show"
        expired = False
        if self.config.Cache and is_movie:
            cache_id, expired = self.config.Cache.query_imdb_to_tmdb_map(media_type, tmdb_id, imdb=False)
            if cache_id and not expired:
                return cache_id
        imdb_id = None
        try:
            imdb_id = self.config.TMDb.convert_from(tmdb_id, "imdb_id", is_movie)
        except Failed:
            if self.config.Trakt:
                try:
                    imdb_id = self.config.Trakt.convert(tmdb_id, "tmdb", "imdb", "movie" if is_movie else "show")
                except Failed:
                    pass
        if fail and imdb_id is None:
            raise Failed(f"Convert Error: No IMDb ID Found for TMDb ID: {tmdb_id}")
        if self.config.Cache and imdb_id:
            self.config.Cache.update_imdb_to_tmdb_map(media_type, expired, imdb_id, tmdb_id)
        return imdb_id

    def imdb_to_tmdb(self, imdb_id, is_movie=True, fail=False):
        media_type = "movie" if is_movie else "show"
        expired = False
        if self.config.Cache and is_movie:
            cache_id, expired = self.config.Cache.query_imdb_to_tmdb_map(media_type, imdb_id, imdb=True)
            if cache_id and not expired:
                return cache_id
        tmdb_id = None
        try:
            tmdb_id = self.config.TMDb.convert_to(imdb_id, "imdb_id", is_movie)
        except Failed:
            if self.config.Trakt:
                try:
                    tmdb_id = self.config.Trakt.convert(imdb_id, "imdb", "tmdb", media_type)
                except Failed:
                    pass
        if fail and tmdb_id is None:
            raise Failed(f"Convert Error: No TMDb ID Found for IMDb ID: {imdb_id}")
        if self.config.Cache and tmdb_id:
            self.config.Cache.update_imdb_to_tmdb_map(media_type, expired, imdb_id, tmdb_id)
        return tmdb_id

    def tmdb_to_tvdb(self, tmdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, expired = self.config.Cache.query_tmdb_to_tvdb_map(tmdb_id, tmdb=True)
            if cache_id and not expired:
                return cache_id
        tvdb_id = None
        try:
            tvdb_id = self.config.TMDb.convert_from(tmdb_id, "tvdb_id", False)
        except Failed:
            if self.config.Trakt:
                try:
                    tvdb_id = self.config.Trakt.convert(tmdb_id, "tmdb", "tvdb", "show")
                except Failed:
                    pass
        if fail and tvdb_id is None:
            raise Failed(f"Convert Error: No TVDb ID Found for TMDb ID: {tmdb_id}")
        if self.config.Cache and tvdb_id:
            self.config.Cache.update_tmdb_to_tvdb_map(expired, tmdb_id, tvdb_id)
        return tvdb_id

    def tvdb_to_tmdb(self, tvdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, expired = self.config.Cache.query_tmdb_to_tvdb_map(tvdb_id, tmdb=False)
            if cache_id and not expired:
                return cache_id
        tmdb_id = None
        try:
            tmdb_id = self.config.TMDb.convert_to(tvdb_id, "tvdb_id", False)
        except Failed:
            if self.config.Trakt:
                try:
                    tmdb_id = self.config.Trakt.convert(tvdb_id, "tvdb", "tmdb", "show")
                except Failed:
                    pass
        if fail and tmdb_id is None:
            raise Failed(f"Convert Error: No TMDb ID Found for TVDb ID: {tvdb_id}")
        if self.config.Cache and tmdb_id:
            self.config.Cache.update_tmdb_to_tvdb_map(expired, tmdb_id, tvdb_id)
        return tmdb_id

    def tvdb_to_imdb(self, tvdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, expired = self.config.Cache.query_imdb_to_tvdb_map(tvdb_id, imdb=False)
            if cache_id and not expired:
                return cache_id
        imdb_id = None
        try:
            imdb_id = self.tmdb_to_imdb(self.tvdb_to_tmdb(tvdb_id), False)
        except Failed:
            if self.config.Trakt:
                try:
                    imdb_id = self.config.Trakt.convert(tvdb_id, "tvdb", "imdb", "show")
                except Failed:
                    pass
        if fail and imdb_id is None:
            raise Failed(f"Convert Error: No IMDb ID Found for TVDb ID: {tvdb_id}")
        if self.config.Cache and imdb_id:
            self.config.Cache.update_imdb_to_tvdb_map(expired, imdb_id, tvdb_id)
        return imdb_id

    def imdb_to_tvdb(self, imdb_id, fail=False):
        expired = False
        if self.config.Cache:
            cache_id, expired = self.config.Cache.query_imdb_to_tvdb_map(imdb_id, imdb=True)
            if cache_id and not expired:
                return cache_id
        tvdb_id = None
        try:
            tvdb_id = self.tmdb_to_tvdb(self.imdb_to_tmdb(imdb_id, False))
        except Failed:
            if self.config.Trakt:
                try:
                    tvdb_id = self.config.Trakt.convert(imdb_id, "imdb", "tvdb", "show")
                except Failed:
                    pass
        if fail and tvdb_id is None:
            raise Failed(f"Convert Error: No TVDb ID Found for IMDb ID: {imdb_id}")
        if self.config.Cache and tvdb_id:
            self.config.Cache.update_imdb_to_tvdb_map(expired, imdb_id, tvdb_id)
        return tvdb_id

    def get_id(self, item, library, length):
        expired = None
        if self.config.Cache:
            cache_id, media_type, expired = self.config.Cache.query_guid_map(item.guid)
            if cache_id and not expired:
                media_id_type = "movie" if "movie" in media_type else "show"
                return media_id_type, util.get_list(cache_id, int_list=True)
        try:
            tmdb_id = None
            imdb_id = None
            tvdb_id = None
            anidb_id = None
            guid = requests.utils.urlparse(item.guid)
            item_type = guid.scheme.split(".")[-1]
            check_id = guid.netloc

            if item_type == "plex":
                tmdb_id = []
                imdb_id = []
                tvdb_id = []
                try:
                    for guid_tag in library.get_guids(item):
                        url_parsed = requests.utils.urlparse(guid_tag.id)
                        if url_parsed.scheme == "tvdb":                 tvdb_id.append(int(url_parsed.netloc))
                        elif url_parsed.scheme == "imdb":               imdb_id.append(url_parsed.netloc)
                        elif url_parsed.scheme == "tmdb":               tmdb_id.append(int(url_parsed.netloc))
                except requests.exceptions.ConnectionError:
                    util.print_stacktrace()
                    raise Failed("No External GUIDs found")
            elif item_type == "imdb":                       imdb_id = check_id
            elif item_type == "thetvdb":                    tvdb_id = int(check_id)
            elif item_type == "themoviedb":                 tmdb_id = int(check_id)
            elif item_type == "hama":
                if check_id.startswith("tvdb"):             tvdb_id = int(re.search("-(.*)", check_id).group(1))
                elif check_id.startswith("anidb"):          anidb_id = re.search("-(.*)", check_id).group(1)
                else:                                       raise Failed(f"Hama Agent ID: {check_id} not supported")
            elif item_type == "myanimelist":
                anime_ids = self._arms_ids(mal_ids=check_id)
                if anime_ids[0] and anime_ids[0]["anidb"]:      anidb_id = anime_ids[0]["anidb"]
                else:                                           raise Failed(f"Unable to convert MyAnimeList ID: {check_id} to AniDB ID")
            elif item_type == "local":                      raise Failed("No match in Plex")
            else:                                           raise Failed(f"Agent {item_type} not supported")

            if anidb_id:
                tvdb_id = self.anidb_to_tvdb(anidb_id)
                if not tvdb_id:
                    imdb_id = self.anidb_to_imdb(anidb_id)
                if not imdb_id and not tvdb_id:
                    raise Failed(f"Unable to convert AniDB ID: {anidb_id} to TVDb ID or IMDb ID")

            if not tmdb_id and imdb_id:
                if isinstance(imdb_id, list):
                    tmdb_id = []
                    new_imdb_id = []
                    for imdb in imdb_id:
                        try:
                            tmdb_id.append(self.imdb_to_tmdb(imdb, fail=True))
                            new_imdb_id.append(imdb)
                        except Failed:
                            continue
                    imdb_id = new_imdb_id
                else:
                    tmdb_id = self.imdb_to_tmdb(imdb_id)
                if not tmdb_id:
                    raise Failed(f"Unable to convert IMDb ID: {imdb_id} to TMDb ID")
            if not anidb_id and not tvdb_id and tmdb_id and library.is_show:
                if isinstance(tmdb_id, list):
                    tvdb_id = []
                    for tmdb in tmdb_id:
                        if tmdb:
                            tvdb_id.append(self.tmdb_to_tvdb(tmdb))
                else:
                    tvdb_id = self.tmdb_to_tvdb(tmdb_id)
                if not tvdb_id:
                    raise Failed(f"Unable to convert TMDb ID: {tmdb_id} to TVDb ID")

            def update_cache(cache_ids, id_type, guid_type):
                if self.config.Cache:
                    cache_ids = util.compile_list(cache_ids)
                    util.print_end(length, f"Cache | {'^' if expired else '+'} | {item.guid:<46} | {id_type} ID: {cache_ids:<6} | {item.title}")
                    self.config.Cache.update_guid_map(guid_type, item.guid, cache_ids, expired)

            if tmdb_id and library.is_movie:
                update_cache(tmdb_id, "TMDb", "movie")
                return "movie", tmdb_id
            elif tvdb_id and library.is_show:
                update_cache(tvdb_id, "TVDb", "show")
                return "show", tvdb_id
            elif anidb_id and tmdb_id and library.is_show:
                update_cache(tmdb_id, "TMDb", "show_movie")
                return "movie", tmdb_id
            else:
                raise Failed(f"No ID to convert")

        except Failed as e:
            util.print_end(length, f"Mapping Error | {item.guid:<46} | {e} for {item.title}")
            return None, None
