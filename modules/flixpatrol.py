from modules import util
from modules.util import Failed

logger = util.logger

builders = ["flixpatrol_url", "flixpatrol_demographics", "flixpatrol_popular", "flixpatrol_top"]
generations = ["all", "boomers", "x", "y", "z"]
generations_translation = {"all": "all-generations", "boomers": "baby-boomers", "x": "generation-x", "y": "generation-y", "z": "generation-z"}
generations_pretty = {"all": "All generations", "boomers": "Baby Boomers", "x": "Generation X", "y": "Generation Y (Millenials)", "z": "Generation Z"}
gender = ["all", "men", "women"]
demo_locations = ["world", "brazil", "canada", "france", "germany", "india", "mexico",  "united_kingdom", "united_states"]
locations = [
    "world", "albania", "argentina", "armenia", "australia", "austria", "azerbaijan", "bahamas", "bahrain",
    "bangladesh", "belarus", "belgium", "belize", "benin", "bolivia", "bosnia_and_herzegovina", "botswana", "brazil",
    "bulgaria", "burkina_faso", "cambodia", "canada", "chile", "colombia", "costa_rica", "croatia", "cyprus",
    "czech_republic", "denmark", "dominican_republic", "ecuador", "egypt", "estonia", "finland", "france", "gabon",
    "germany", "ghana", "greece", "guatemala", "guinea_bissau", "haiti", "honduras", "hong_kong", "hungary", "iceland",
    "india", "indonesia", "ireland", "israel", "italy", "ivory_coast", "jamaica", "japan", "jordan", "kazakhstan",
    "kenya", "kuwait", "kyrgyzstan", "laos", "latvia", "lebanon", "lithuania", "luxembourg", "malaysia", "maldives",
    "mali", "malta", "mexico", "moldova", "mongolia", "montenegro", "morocco", "mozambique", "namibia", "netherlands",
    "new_zealand", "nicaragua", "niger", "nigeria", "north_macedonia", "norway", "oman", "pakistan", "panama",
    "papua_new_guinea", "paraguay", "peru", "philippines", "poland", "portugal", "qatar", "romania", "russia",
    "rwanda", "salvador", "saudi_arabia", "senegal", "serbia", "singapore", "slovakia", "slovenia", "south_africa",
    "south_korea", "spain", "sri_lanka", "sweden", "switzerland", "taiwan", "tajikistan", "tanzania", "thailand",
    "togo", "trinidad_and_tobago", "turkey", "turkmenistan", "uganda", "ukraine", "united_arab_emirates",
    "united_kingdom", "united_states", "uruguay", "uzbekistan", "venezuela", "vietnam", "zambia", "zimbabwe"
]
popular = ["movie_db", "facebook", "google", "twitter", "twitter_trends", "instagram", "instagram_trends", "youtube", "imdb", "letterboxd", "rotten_tomatoes", "tmdb", "trakt"]
platforms = ["netflix", "hbo", "disney", "amazon", "itunes", "google", "paramount_plus", "hulu", "vudu", "imdb", "amazon_prime", "star_plus", "apple_tv"]
base_url = "https://flixpatrol.com"
urls = {
    "top10": f"{base_url}/top10/",
    "popular_movies": f"{base_url}/popular/movies/",
    "popular_shows": f"{base_url}/popular/tv-shows/",
    "demographics": f"{base_url}/demographics/"
}

class FlixPatrol:
    def __init__(self, config):
        self.config = config

    def _request(self, url, language, xpath):
        logger.trace(f"URL: {url}")
        return self.config.get_html(url, headers=util.header(language)).xpath(xpath)

    def _tmdb(self, flixpatrol_url, language):
        ids = self._request(flixpatrol_url, language, "//script[@type='application/ld+json']/text()")
        if len(ids) > 0 and ids[0]:
            if "https://www.themoviedb.org" in ids[0]:
                return util.regex_first_int(ids[0].split("https://www.themoviedb.org")[1], "TMDb Movie ID")
        raise Failed(f"FlixPatrol Error: TMDb Movie ID not found at {flixpatrol_url}")

    def _parse_list(self, list_url, language, is_movie, limit=0):
        flixpatrol_urls = []
        logger.trace(f"URL: {list_url}")
        if list_url.startswith(urls["top10"]):
            platform = list_url[len(urls["top10"]):].split("/")[0]
            flixpatrol_urls = self._request(
                list_url, language,
                f"//div[@id='{platform}-{'1' if is_movie else '2'}']//a[@class='hover:underline']/@href"
            )
            logger.info(flixpatrol_urls)
            if not flixpatrol_urls:
                flixpatrol_urls = self._request(
                    list_url, language,
                    f"//h3[text() = '{'TOP 10 Movies' if is_movie else 'TOP 10 TV Shows'}']/following-sibling::div//a[@class='hover:underline']/@href"
                )
                logger.info(flixpatrol_urls)
        elif list_url.startswith(tuple([v for k, v in urls.items()])):
            flixpatrol_urls = self._request(
                list_url, language,
                f"//a[contains(@class, 'flex group') and .//span[.='{'Movie' if is_movie else 'TV Show'}']]/@href"
            )
        return flixpatrol_urls if limit == 0 else flixpatrol_urls[:limit]

    def validate_flixpatrol_lists(self, flixpatrol_lists, language, is_movie):
        valid_lists = []
        for flixpatrol_list in util.get_list(flixpatrol_lists, split=False):
            list_url = flixpatrol_list.strip()
            if not list_url.startswith(tuple([v for k, v in urls.items()])):
                fails = "\n".join([f"{v} (For {k.replace('_', ' ').title()})" for k, v in urls.items()])
                raise Failed(f"FlixPatrol Error: {list_url} must begin with either:\n{fails}")
            elif len(self._parse_list(list_url, language, is_movie)) > 0:
                valid_lists.append(list_url)
            else:
                raise Failed(f"FlixPatrol Error: {list_url} failed to parse")
        return valid_lists

    def validate_flixpatrol_dict(self, method, data, language, is_movie):
        return len(self.validate_flixpatrol_lists(self.get_url(method, data, is_movie), language, is_movie)) > 0

    def get_url(self, method, data, is_movie):
        if method == "flixpatrol_demographics":
            return f"{urls['demographics']}" \
                   f"{generations_translation[data['generation']]}/" \
                   f"{'all-genders' if data['gender'] == 'all' else data['gender']}/" \
                   f"{data['location'].replace('_', '-')}/"
        elif method == "flixpatrol_popular":
            return f"{urls['popular_movies'] if is_movie else urls['popular_shows']}" \
                   f"{data['source'].replace('_', '-')}/" \
                   f"{util.time_window(data['time_window'])}/"
        elif method == "flixpatrol_top":
            return f"{urls['top10']}" \
                   f"{data['platform'].replace('_', '-')}/" \
                   f"{data['location'].replace('_', '-')}/" \
                   f"{util.time_window(data['time_window'])}/full/"
        elif method == "flixpatrol_url":
            return data
        else:
            raise Failed(f"FlixPatrol Error: Method {method} not supported")

    def get_tmdb_ids(self, method, data, language, is_movie):
        if method == "flixpatrol_demographics":
            logger.info("Processing FlixPatrol Demographics:")
            logger.info(f"\tGeneration: {generations_pretty[data['generation']]}")
            logger.info(f"\tGender: {'All genders' if data['gender'] == 'all' else data['gender'].capitalize()}")
            logger.info(f"\tLocation: {data['location'].replace('_', ' ').title()}")
            logger.info(f"\tLimit: {data['limit']}")
        elif method == "flixpatrol_popular":
            logger.info("Processing FlixPatrol Popular:")
            logger.info(f"\tSource: {data['source'].replace('_', ' ').title()}")
            logger.info(f"\tTime Window: {data['time_window'].replace('_', ' ').title()}")
            logger.info(f"\tLimit: {data['limit']}")
        elif method == "flixpatrol_top":
            logger.info("Processing FlixPatrol Top:")
            logger.info(f"\tPlatform: {data['platform'].replace('_', ' ').title()}")
            logger.info(f"\tLocation: {data['location'].replace('_', ' ').title()}")
            logger.info(f"\tTime Window: {data['time_window'].replace('_', ' ').title()}")
            logger.info(f"\tLimit: {data['limit']}")
        elif method == "flixpatrol_url":
            logger.info(f"Processing FlixPatrol URL: {data}")
        url = self.get_url(method, data, is_movie)

        items = self._parse_list(url, language, is_movie, limit=data["limit"] if isinstance(data, dict) else 0)
        media_type = "movie" if is_movie else "show"
        total_items = len(items)
        if total_items > 0:
            ids = []
            for i, item in enumerate(items, 1):
                logger.ghost(f"Finding TMDb ID {i}/{total_items}")
                tmdb_id = None
                expired = None
                if self.config.Cache:
                    tmdb_id, expired = self.config.Cache.query_flixpatrol_map(item, media_type)
                if not tmdb_id or expired is not False:
                    try:
                        tmdb_id = self._tmdb(f"{base_url}{item}", language)
                    except Failed as e:
                        logger.error(e)
                        continue
                    if self.config.Cache:
                        self.config.Cache.update_flixpatrol_map(expired, item, tmdb_id, media_type)
                ids.append((tmdb_id, "tmdb" if is_movie else "tmdb_show"))
            logger.info(f"Processed {total_items} TMDb IDs")
            return ids
        else:
            raise Failed(f"FlixPatrol Error: No List Items found in {data}")
