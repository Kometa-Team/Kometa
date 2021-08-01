import logging
from modules import util
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

builders = ["stevenlu_popular"]
base_url = "https://s3.amazonaws.com/popular-movies/movies.json"

class StevenLu:
    def __init__(self, config):
        self.config = config

    def get_items(self, method):
        pretty = util.pretty_names[method] if method in util.pretty_names else method
        movie_ids = []
        fail_ids = []
        if method == "stevenlu_popular":
            logger.info(f"Processing {pretty} Movies")
            for i in self.config.get_json(base_url):
                tmdb_id = self.config.Convert.imdb_to_tmdb(i["imdb_id"])
                if tmdb_id:
                    movie_ids.append(tmdb_id)
                else:
                    logger.error(f"Convert Error: No TMDb ID found for IMDb: {i['imdb_id']}")
                    fail_ids.append(i["imdb_id"])
        else:
            raise Failed(f"StevenLu Error: Method {method} not supported")
        logger.debug("")
        logger.debug(f"{len(fail_ids)} IMDb IDs Failed to Convert: {fail_ids}")
        logger.debug(f"{len(movie_ids)} TMDb IDs Found: {movie_ids}")
        return movie_ids, []
