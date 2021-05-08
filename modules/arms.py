import logging, re, requests
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
                raise Failed(f"Arms Error: No {util.pretty_ids[to_id]} ID found for AniDB ID: {input_id}")
        else:
            raise Failed(f"Arms Error: AniDB ID: {input_id} not found")

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def _request(self, ids):
        return requests.post(self.arms_url, json=ids).json()

    def mal_to_anidb(self, mal_id):
        anime_ids = self._arms_ids(mal_ids=mal_id)
        if anime_ids[0] is None:
            raise Failed(f"Arms Error: MyAnimeList ID: {mal_id} does not exist")
        if anime_ids[0]["anidb"] is None:
            raise Failed(f"Arms Error: No AniDB ID for MyAnimeList ID: {mal_id}")
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
                    logger.error(f"Arms Error: No TVDb ID or IMDb ID found for AniDB ID: {anidb_id}")
        return movie_ids, show_ids

    def anilist_to_ids(self, anilist_ids, language):
        anidb_ids = []
        for id_set in self._arms_ids(anilist_ids=anilist_ids):
            if id_set["anidb"] is not None:
                anidb_ids.append(id_set["anidb"])
            else:
                logger.error(f"Arms Error: AniDB ID not found for AniList ID: {id_set['anilist']}")
        return self.anidb_to_ids(anidb_ids, language)

    def myanimelist_to_ids(self, mal_ids, language):
        anidb_ids = []
        for id_set in self._arms_ids(mal_ids=mal_ids):
            if id_set["anidb"] is not None:
                anidb_ids.append(id_set["anidb"])
            else:
                logger.error(f"Arms Error: AniDB ID not found for MyAnimeList ID: {id_set['myanimelist']}")
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

        for anime_ids in self._request(unconverted_ids):
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
            try:                    tmdb_id = self.config.TMDb.convert_imdb_to_tmdb(imdb_id)
            except Failed:          pass
        if not tmdb_id and not tvdb_id and self.config.TMDb:
            try:                    tvdb_id = self.config.TMDb.convert_imdb_to_tvdb(imdb_id)
            except Failed:          pass
        if not tmdb_id and not tvdb_id and self.config.Trakt:
            try:                    tmdb_id = self.convert_imdb_to_tmdb(imdb_id)
            except Failed:          pass
        if not tmdb_id and not tvdb_id and self.config.Trakt:
            try:                    tvdb_id = self.convert_imdb_to_tvdb(imdb_id)
            except Failed:          pass
        if tmdb_id and not from_cache:
            try:                    self.config.TMDb.get_movie(tmdb_id)
            except Failed:          tmdb_id = None
        if tvdb_id and not from_cache:
            try:                    self.config.TVDb.get_series(language, tvdb_id)
            except Failed:          tvdb_id = None
        if not tmdb_id and not tvdb_id:
            raise Failed(f"Arms Error: No TMDb ID or TVDb ID found for IMDb: {imdb_id}")
        if self.config.Cache:
            if tmdb_id and update_tmdb is not False:
                self.config.Cache.update_imdb("movie", update_tmdb, imdb_id, tmdb_id)
            if tvdb_id and update_tvdb is not False:
                self.config.Cache.update_imdb("show", update_tvdb, imdb_id, tvdb_id)
        return tmdb_id, tvdb_id

    def convert_tmdb_to_imdb(self, tmdb_id, is_movie=True, fail=False):
        try:
            return self.config.TMDb.convert_from(tmdb_id, "imdb_id", is_movie)
        except Failed:
            if self.config.Trakt:
                try:
                    return self.config.Trakt.convert(tmdb_id, "tmdb", "imdb", "movie" if is_movie else "show")
                except Failed:
                    pass
        if fail:
            raise Failed(f"Arms Error: No IMDb ID Found for TMDb ID: {tmdb_id}")
        return None

    def convert_imdb_to_tmdb(self, imdb_id, is_movie=True, fail=False):
        try:
            return self.config.TMDb.convert_to(imdb_id, "imdb_id", is_movie)
        except Failed:
            if self.config.Trakt:
                try:
                    return self.config.Trakt.convert(imdb_id, "imdb", "tmdb", "movie" if is_movie else "show")
                except Failed:
                    pass
        if fail:
            raise Failed(f"Arms Error: No TMDb ID Found for IMDb ID: {imdb_id}")
        return None

    def convert_tmdb_to_tvdb(self, tmdb_id, fail=False):
        try:
            return self.config.TMDb.convert_from(tmdb_id, "tvdb_id", False)
        except Failed:
            if self.config.Trakt:
                try:
                    return self.config.Trakt.convert(tmdb_id, "tmdb", "tvdb", "show")
                except Failed:
                    pass
        if fail:
            raise Failed(f"Arms Error: No TVDb ID Found for TMDb ID: {tmdb_id}")
        return None

    def convert_tvdb_to_tmdb(self, tvdb_id, fail=False):
        try:
            return self.config.TMDb.convert_to(tvdb_id, "tvdb_id", False)
        except Failed:
            if self.config.Trakt:
                try:
                    return self.config.Trakt.convert(tvdb_id, "tvdb", "tmdb", "show")
                except Failed:
                    pass
        if fail:
            raise Failed(f"Arms Error: No TMDb ID Found for TVDb ID: {tvdb_id}")
        return None

    def convert_tvdb_to_imdb(self, tvdb_id, fail=False):
        try:
            return self.convert_tmdb_to_imdb(self.convert_tvdb_to_tmdb(tvdb_id), False)
        except Failed:
            if self.config.Trakt:
                try:
                    return self.config.Trakt.convert(tvdb_id, "tvdb", "imdb", "show")
                except Failed:
                    pass
        if fail:
            raise Failed(f"Arms Error: No IMDb ID Found for TVDb ID: {tvdb_id}")
        return None

    def convert_imdb_to_tvdb(self, imdb_id, fail=False):
        try:
            return self.convert_tmdb_to_tvdb(self.convert_imdb_to_tmdb(imdb_id, False))
        except Failed:
            if self.config.Trakt:
                try:
                    return self.config.Trakt.convert(imdb_id, "imdb", "tvdb", "show")
                except Failed:
                    pass
        if fail:
            raise Failed(f"Arms Error: No TVDb ID Found for IMDb ID: {imdb_id}")
        return None

    def get_id(self, item, library, length):
        expired = None
        tmdb_id = None
        imdb_id = None
        tvdb_id = None
        anidb_id = None
        mal_id = None
        error_message = None
        if self.config.Cache:
            if library.is_movie:                            tmdb_id, expired = self.config.Cache.get_tmdb_id("movie", plex_guid=item.guid)
            else:                                           tvdb_id, expired = self.config.Cache.get_tvdb_id("show", plex_guid=item.guid)
            if not tvdb_id and library.is_show:
                tmdb_id, expired = self.config.Cache.get_tmdb_id("show", plex_guid=item.guid)
                anidb_id, expired = self.config.Cache.get_anidb_id("show", plex_guid=item.guid)
        if expired or (not tmdb_id and library.is_movie) or (not tvdb_id and not tmdb_id and library.is_show):
            guid = requests.utils.urlparse(item.guid)
            item_type = guid.scheme.split(".")[-1]
            check_id = guid.netloc

            if item_type == "plex":
                tmdb_id = []
                imdb_id = []
                tvdb_id = []
                if check_id == "movie":
                    try:
                        for guid_tag in library.get_guids(item):
                            url_parsed = requests.utils.urlparse(guid_tag.id)
                            if url_parsed.scheme == "tmdb":                 tmdb_id.append(int(url_parsed.netloc))
                            elif url_parsed.scheme == "imdb":               imdb_id.append(url_parsed.netloc)
                    except requests.exceptions.ConnectionError:
                        util.print_stacktrace()
                        logger.error(f"{'Cache | ! |' if self.config.Cache else 'Mapping Error:'} {item.guid:<46} | No External GUIDs found for {item.title}")
                        return None, None
                elif check_id == "show":
                    try:
                        for guid_tag in library.get_guids(item):
                            url_parsed = requests.utils.urlparse(guid_tag.id)
                            if url_parsed.scheme == "tvdb":                 tvdb_id.append(int(url_parsed.netloc))
                            elif url_parsed.scheme == "imdb":               imdb_id.append(url_parsed.netloc)
                            elif url_parsed.scheme == "tmdb":               tmdb_id.append(int(url_parsed.netloc))
                    except requests.exceptions.ConnectionError:
                        util.print_stacktrace()
                        logger.error(f"{'Cache | ! |' if self.config.Cache else 'Mapping Error:'} {item.guid:<46} | No External GUIDs found for {item.title}")
                        return None, None
            elif item_type == "imdb":                       imdb_id = check_id
            elif item_type == "thetvdb":                    tvdb_id = int(check_id)
            elif item_type == "themoviedb":                 tmdb_id = int(check_id)
            elif item_type == "hama":
                if check_id.startswith("tvdb"):             tvdb_id = int(re.search("-(.*)", check_id).group(1))
                elif check_id.startswith("anidb"):          anidb_id = re.search("-(.*)", check_id).group(1)
                else:                                       error_message = f"Hama Agent ID: {check_id} not supported"
            elif item_type == "myanimelist":                mal_id = check_id
            elif item_type == "local":                      error_message = "No match in Plex"
            else:                                           error_message = f"Agent {item_type} not supported"

            if not error_message:
                if mal_id and not anidb_id:
                    try:                                            anidb_id = self.mal_to_anidb(mal_id)
                    except Failed:                                  pass
                if anidb_id and not tvdb_id:
                    try:                                            tvdb_id = self.anidb_to_tvdb(anidb_id)
                    except Failed:                                  pass
                if anidb_id and not imdb_id:
                    try:                                            imdb_id = self.anidb_to_imdb(anidb_id)
                    except Failed:                                  pass
                if not tmdb_id and imdb_id:
                    if isinstance(imdb_id, list):
                        tmdb_id = []
                        new_imdb_id = []
                        for imdb in imdb_id:
                            try:
                                tmdb_id.append(self.convert_imdb_to_tmdb(imdb_id, fail=True))
                                new_imdb_id.append(imdb)
                            except Failed:
                                continue
                        imdb_id = new_imdb_id
                    else:
                        tmdb_id = self.convert_imdb_to_tmdb(imdb_id)
                if not tmdb_id and tvdb_id and library.is_show:
                    tmdb_id = self.convert_tvdb_to_tmdb(tvdb_id)
                if not imdb_id and tmdb_id and library.is_movie:
                    imdb_id = self.convert_tmdb_to_imdb(tmdb_id)
                if not imdb_id and tvdb_id and library.is_show:
                    imdb_id = self.convert_tvdb_to_imdb(tvdb_id)
                if not tvdb_id and tmdb_id and library.is_show:
                    tvdb_id = self.convert_tmdb_to_tvdb(tmdb_id)
                if not tvdb_id and imdb_id and library.is_show:
                    tvdb_id = self.convert_imdb_to_tvdb(imdb_id)

                if (not tmdb_id and library.is_movie) or (not tvdb_id and not (anidb_id and tmdb_id) and library.is_show):
                    service_name = "TMDb ID" if library.is_movie else "TVDb ID"

                    if self.config.Trakt:                                  api_name = "TMDb or Trakt"
                    else:                                           api_name = "TMDb"

                    if tmdb_id and imdb_id:                         id_name = f"TMDb ID: {tmdb_id} or IMDb ID: {imdb_id}"
                    elif imdb_id and tvdb_id:                       id_name = f"IMDb ID: {imdb_id} or TVDb ID: {tvdb_id}"
                    elif tmdb_id:                                   id_name = f"TMDb ID: {tmdb_id}"
                    elif imdb_id:                                   id_name = f"IMDb ID: {imdb_id}"
                    elif tvdb_id:                                   id_name = f"TVDb ID: {tvdb_id}"
                    else:                                           id_name = None

                    if anidb_id and not tmdb_id and not tvdb_id:    error_message = f"Unable to convert AniDB ID: {anidb_id} to TMDb ID or TVDb ID"
                    elif id_name:                                   error_message = f"Unable to convert {id_name} to {service_name} using {api_name}"
                    else:                                           error_message = f"No ID to convert to {service_name}"
            if self.config.Cache and ((tmdb_id and library.is_movie) or ((tvdb_id or (anidb_id and tmdb_id)) and library.is_show)):
                if not isinstance(tmdb_id, list):               tmdb_id = [tmdb_id]
                if not isinstance(imdb_id, list):               imdb_id = [imdb_id]
                if not isinstance(tvdb_id, list):               tvdb_id = [tvdb_id]
                try:                                            tvdb_value = tvdb_id[0]
                except IndexError:                              tvdb_value = None
                for i in range(len(tmdb_id)):
                    try:                                            imdb_value = imdb_id[i]
                    except IndexError:                              imdb_value = None
                    util.print_end(length, f"Cache | {'^' if expired is True else '+'} | {item.guid:<46} | {tmdb_id[i] if tmdb_id[i] else 'None':<6} | {imdb_value if imdb_value else 'None':<10} | {tvdb_value if tvdb_value else 'None':<6} | {anidb_id if anidb_id else 'None':<5} | {item.title}")
                    self.config.Cache.update_guid("movie" if library.is_movie else "show", item.guid, tmdb_id[i], imdb_value, tvdb_value, anidb_id, expired)

        if tmdb_id and library.is_movie:                return "movie", tmdb_id
        elif tvdb_id and library.is_show:               return "show", tvdb_id
        elif anidb_id and tmdb_id:                      return "movie", tmdb_id
        else:
            util.print_end(length, f"{'Cache | ! |' if self.config.Cache else 'Mapping Error:'} {item.guid:<46} | {error_message} for {item.title}")
            return None, None
