import logging, requests, time
from lxml.etree import ParserError
from modules import util
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

builders = ["tvdb_list", "tvdb_list_details", "tvdb_movie", "tvdb_movie_details", "tvdb_show", "tvdb_show_details"]
base_url = "https://www.thetvdb.com"
alt_url = "https://thetvdb.com"
urls = {
    "list": f"{base_url}/lists/", "alt_list": f"{alt_url}/lists/",
    "series": f"{base_url}/series/", "alt_series": f"{alt_url}/series/",
    "movies": f"{base_url}/movies/", "alt_movies": f"{alt_url}/movies/",
    "series_id": f"{base_url}/dereferrer/series/", "movie_id": f"{base_url}/dereferrer/movie/"
}
language_translation = {
    "ab": "abk", "aa": "aar", "af": "afr", "ak": "aka", "sq": "sqi", "am": "amh", "ar": "ara", "an": "arg", "hy": "hye",
    "as": "asm", "av": "ava", "ae": "ave", "ay": "aym", "az": "aze", "bm": "bam", "ba": "bak", "eu": "eus", "be": "bel",
    "bn": "ben", "bi": "bis", "bs": "bos", "br": "bre", "bg": "bul", "my": "mya", "ca": "cat", "ch": "cha", "ce": "che",
    "ny": "nya", "zh": "zho", "cv": "chv", "kw": "cor", "co": "cos", "cr": "cre", "hr": "hrv", "cs": "ces", "da": "dan",
    "dv": "div", "nl": "nld", "dz": "dzo", "en": "eng", "eo": "epo", "et": "est", "ee": "ewe", "fo": "fao", "fj": "fij",
    "fi": "fin", "fr": "fra", "ff": "ful", "gl": "glg", "ka": "kat", "de": "deu", "el": "ell", "gn": "grn", "gu": "guj",
    "ht": "hat", "ha": "hau", "he": "heb", "hz": "her", "hi": "hin", "ho": "hmo", "hu": "hun", "ia": "ina", "id": "ind",
    "ie": "ile", "ga": "gle", "ig": "ibo", "ik": "ipk", "io": "ido", "is": "isl", "it": "ita", "iu": "iku", "ja": "jpn",
    "jv": "jav", "kl": "kal", "kn": "kan", "kr": "kau", "ks": "kas", "kk": "kaz", "km": "khm", "ki": "kik", "rw": "kin",
    "ky": "kir", "kv": "kom", "kg": "kon", "ko": "kor", "ku": "kur", "kj": "kua", "la": "lat", "lb": "ltz", "lg": "lug",
    "li": "lim", "ln": "lin", "lo": "lao", "lt": "lit", "lu": "lub", "lv": "lav", "gv": "glv", "mk": "mkd", "mg": "mlg",
    "ms": "msa", "ml": "mal", "mt": "mlt", "mi": "mri", "mr": "mar", "mh": "mah", "mn": "mon", "na": "nau", "nv": "nav",
    "nd": "nde", "ne": "nep", "ng": "ndo", "nb": "nob", "nn": "nno", "no": "nor", "ii": "iii", "nr": "nbl", "oc": "oci",
    "oj": "oji", "cu": "chu", "om": "orm", "or": "ori", "os": "oss", "pa": "pan", "pi": "pli", "fa": "fas", "pl": "pol",
    "ps": "pus", "pt": "por", "qu": "que", "rm": "roh", "rn": "run", "ro": "ron", "ru": "rus", "sa": "san", "sc": "srd",
    "sd": "snd", "se": "sme", "sm": "smo", "sg": "sag", "sr": "srp", "gd": "gla", "sn": "sna", "si": "sin", "sk": "slk",
    "sl": "slv", "so": "som", "st": "sot", "es": "spa", "su": "sun", "sw": "swa", "ss": "ssw", "sv": "swe", "ta": "tam",
    "te": "tel", "tg": "tgk", "th": "tha", "ti": "tir", "bo": "bod", "tk": "tuk", "tl": "tgl", "tn": "tsn", "to": "ton",
    "tr": "tur", "ts": "tso", "tt": "tat", "tw": "twi", "ty": "tah", "ug": "uig", "uk": "ukr", "ur": "urd", "uz": "uzb",
    "ve": "ven", "vi": "vie", "vo": "vol", "wa": "wln", "cy": "cym", "wo": "wol", "fy": "fry", "xh": "xho", "yi": "yid",
    "yo": "yor", "za": "zha", "zu": "zul"}

class TVDbObj:
    def __init__(self, tvdb_url, language, is_movie, config):
        self.tvdb_url = tvdb_url.strip()
        self.language = language
        self.is_movie = is_movie
        self.config = config
        if not self.is_movie and self.tvdb_url.startswith((urls["series"], urls["alt_series"], urls["series_id"])):
            self.media_type = "Series"
        elif self.is_movie and self.tvdb_url.startswith((urls["movies"], urls["alt_movies"], urls["movie_id"])):
            self.media_type = "Movie"
        else:
            raise Failed(f"TVDb Error: {self.tvdb_url} must begin with {urls['movies'] if self.is_movie else urls['series']}")

        if self.config.trace_mode:
            logger.debug(f"URL: {tvdb_url}")
        try:
            response = self.config.get_html(self.tvdb_url, headers=util.header(self.language))
        except ParserError:
            raise Failed(f"TVDb Error: Could not parse {self.tvdb_url}")
        results = response.xpath(f"//*[text()='TheTVDB.com {self.media_type} ID']/parent::node()/span/text()")
        if len(results) > 0:
            self.id = int(results[0])
        elif self.tvdb_url.startswith(urls["movie_id"]):
            raise Failed(f"TVDb Error: Could not find a TVDb Movie using TVDb Movie ID: {self.tvdb_url[len(urls['movie_id']):]}")
        elif self.tvdb_url.startswith(urls["series_id"]):
            raise Failed(f"TVDb Error: Could not find a TVDb Series using TVDb Series ID: {self.tvdb_url[len(urls['series_id']):]}")
        else:
            raise Failed(f"TVDb Error: Could not find a TVDb {self.media_type} ID at the URL {self.tvdb_url}")

        def parse_page(xpath):
            parse_results = response.xpath(xpath)
            if len(parse_results) > 0:
                parse_results = [r.strip() for r in parse_results if len(r) > 0]
            return parse_results[0] if len(parse_results) > 0 else None

        def parse_title_summary(lang=None):
            place = "//div[@class='change_translation_text' and "
            place += f"@data-language='{lang}']" if lang else "not(@style='display:none')]"
            return parse_page(f"{place}/@data-title"), parse_page(f"{place}/p/text()[normalize-space()]")

        self.title, self.summary = parse_title_summary(lang=self.language)
        if not self.title and self.language in language_translation:
            self.title, self.summary = parse_title_summary(lang=language_translation[self.language])
        if not self.title:
            self.title, self.summary = parse_title_summary()
        if not self.title:
            raise Failed(f"TVDb Error: Name not found from TVDb URL: {self.tvdb_url}")

        self.poster_path = parse_page("//div[@class='row hidden-xs hidden-sm']/div/img/@src")
        self.background_path = parse_page("(//h2[@class='mt-4' and text()='Backgrounds']/following::div/a/@href)[1]")
        if self.is_movie:
            self.directors = parse_page("//strong[text()='Directors']/parent::li/span/a/text()[normalize-space()]")
            self.writers = parse_page("//strong[text()='Writers']/parent::li/span/a/text()[normalize-space()]")
            self.studios = parse_page("//strong[text()='Studio']/parent::li/span/a/text()[normalize-space()]")
        else:
            self.networks = parse_page("//strong[text()='Networks']/parent::li/span/a/text()[normalize-space()]")
        self.genres = parse_page("//strong[text()='Genres']/parent::li/span/a/text()[normalize-space()]")

        tmdb_id = None
        imdb_id = None
        if self.is_movie:
            results = response.xpath("//*[text()='TheMovieDB.com']/@href")
            if len(results) > 0:
                try:
                    tmdb_id = util.regex_first_int(results[0], "TMDb ID")
                except Failed:
                    pass
            results = response.xpath("//*[text()='IMDB']/@href")
            if len(results) > 0:
                try:
                    imdb_id = util.get_id_from_imdb_url(results[0])
                except Failed:
                    pass
            if tmdb_id is None and imdb_id is None:
                raise Failed(f"TVDB Error: No TMDb ID or IMDb ID found for {self.title}")
        self.tmdb_id = tmdb_id
        self.imdb_id = imdb_id

class TVDb:
    def __init__(self, config, tvdb_language):
        self.config = config
        self.tvdb_language = tvdb_language

    def get_item(self, tvdb_url, is_movie):
        return self.get_movie(tvdb_url) if is_movie else self.get_series(tvdb_url)

    def get_series(self, tvdb_url):
        try:
            tvdb_url = f"{urls['series_id']}{int(tvdb_url)}"
        except ValueError:
            pass
        return TVDbObj(tvdb_url, self.tvdb_language, False, self.config)

    def get_movie(self, tvdb_url):
        try:
            tvdb_url = f"{urls['movie_id']}{int(tvdb_url)}"
        except ValueError:
            pass
        return TVDbObj(tvdb_url, self.tvdb_language, True, self.config)

    def get_list_description(self, tvdb_url):
        response = self.config.get_html(tvdb_url, headers=util.header(self.tvdb_language))
        description = response.xpath("//div[@class='block']/div[not(@style='display:none')]/p/text()")
        return description[0] if len(description) > 0 and len(description[0]) > 0 else ""

    def _ids_from_url(self, tvdb_url):
        ids = []
        tvdb_url = tvdb_url.strip()
        if self.config.trace_mode:
            logger.debug(f"URL: {tvdb_url}")
        if tvdb_url.startswith((urls["list"], urls["alt_list"])):
            try:
                response = self.config.get_html(tvdb_url, headers=util.header(self.tvdb_language))
                items = response.xpath("//div[@class='col-xs-12 col-sm-12 col-md-8 col-lg-8 col-md-pull-4']/div[@class='row']")
                for item in items:
                    title = item.xpath(".//div[@class='col-xs-12 col-sm-9 mt-2']//a/text()")[0]
                    item_url = item.xpath(".//div[@class='col-xs-12 col-sm-9 mt-2']//a/@href")[0]
                    if item_url.startswith("/series/"):
                        try:
                            ids.append((self.get_series(f"{base_url}{item_url}").id, "tvdb"))
                        except Failed as e:
                            logger.error(f"{e} for series {title}")
                    elif item_url.startswith("/movies/"):
                        try:
                            movie = self.get_movie(f"{base_url}{item_url}")
                            if movie.tmdb_id:
                                ids.append((movie.tmdb_id, "tmdb"))
                            elif movie.imdb_id:
                                ids.append((movie.imdb_id, "imdb"))
                        except Failed as e:
                            logger.error(e)
                    else:
                        logger.error(f"TVDb Error: Skipping Movie: {title}")
                    time.sleep(2)
                if len(ids) > 0:
                    return ids
                raise Failed(f"TVDb Error: No TVDb IDs found at {tvdb_url}")
            except requests.exceptions.MissingSchema:
                util.print_stacktrace()
                raise Failed(f"TVDb Error: URL Lookup Failed for {tvdb_url}")
        else:
            raise Failed(f"TVDb Error: {tvdb_url} must begin with {urls['list']}")

    def get_tvdb_ids(self, method, data):
        if method == "tvdb_show":
            logger.info(f"Processing TVDb Show: {data}")
            return [(self.get_series(data).id, "tvdb")]
        elif method == "tvdb_movie":
            logger.info(f"Processing TVDb Movie: {data}")
            movie = self.get_movie(data)
            if movie.tmdb_id:
                return [(movie.tmdb_id, "tmdb")]
            elif movie.imdb_id:
                return [(movie.imdb_id, "imdb")]
        elif method == "tvdb_list":
            logger.info(f"Processing TVDb List: {data}")
            return self._ids_from_url(data)
        else:
            raise Failed(f"TVDb Error: Method {method} not supported")
