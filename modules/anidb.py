import json, time, os
from datetime import datetime, timedelta
from lxml import etree
from modules import util
from modules.util import Failed, logger
import gzip
import io
import traceback
import xml.etree.ElementTree as ET

logger = util.logger

builders = ["anidb_id", "anidb_relation", "anidb_tag", "anidb_tag_name"]
base_url = "https://anidb.net"
api_url = "https://utilities.kometa.wiki/anidb-service"

kometa_client = "kometaofficial"
kometa_client_version = 1

weights = {"anidb": 1000, "anidb_3_0": 600, "anidb_2_5": 500, "anidb_2_0": 400, "anidb_1_5": 300, "anidb_1_0": 200, "anidb_0_5": 100}

class AniDBTitles:
    TITLES_URL = "https://anidb.net/api/anime-titles.xml.gz"
    CACHE_FILE = "config/anidb_cache/anime-titles.xml"

    def __init__(self, requests_obj):
        self.requests = requests_obj
        self.title_map = {} # Maps title string -> AID
        self._load()

    def _load(self):
        try:
            """Downloads if missing/old, then parses into memory."""
            # 1. Update check (24-hour rule)
            refresh_needed = True
            if os.path.exists(self.CACHE_FILE):
                age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(self.CACHE_FILE))
                if age < timedelta(hours=24):
                    refresh_needed = False

            if refresh_needed:
                logger.info("Downloading Master Title List from AniDB...")

                # AniDB requires a non-generic User-Agent and often checks identity
                headers = {
                    'User-Agent': f'Kometa/1.0 ({kometa_client})',
                    'Accept-Encoding': 'gzip, deflate',
                    'Host': 'anidb.net'
                }
                response = self.requests.get(self.TITLES_URL, headers=headers)
                if response.status_code == 200:
                    # Decompress Gzip in memory and save as plain XML
                    content = gzip.decompress(response.content)
                    os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
                    with open(self.CACHE_FILE, 'wb') as f:
                        f.write(content)
                else:
                    logger.error("Failed to download title list.")
            else:
                logger.info("Using cached Master Title List from AniDB.")


            # 2. Parse XML into a searchable Dictionary
            if os.path.exists(self.CACHE_FILE):
                tree = etree.parse(self.CACHE_FILE)
                for anime in tree.xpath("//anime"):
                    aid = anime.get("aid")
                    # Grab every title (main, official, synonym, short)
                    titles = anime.xpath("title/text()")
                    for t in titles:
                        self.title_map[t.lower()] = int(aid)
        except Exception as e:
            print("--- ACTUAL ERROR BELOW ---")
            traceback.print_exc()
            print("--- END OF ERROR ---")
            raise e

    def search(self, query):
        """Returns the AID for a given title string, or None."""
        return self.title_map.get(query.lower())

class AniDBObj:
    def __init__(self, anidb, anidb_id, data):
        self._anidb = anidb
        self.anidb_id = anidb_id
        self._data = data


        # def _parse(self, field_name, xpath, is_dict=False):
        #     # Find all elements matching the XPath
        #     nodes = self.xml_root.xpath(xpath) 
            
        #     if not nodes:
        #         return {} if is_dict else []

        #     if is_dict:
        #         result = {}
        #         for node in nodes:
        #             # Use the 'id' attribute as the primary key
        #             tag_id = node.get('id')
                    
        #             # Map internal children to dictionary keys
        #             tag_data = {
        #                 'name': node.findtext('name'),
        #                 'weight': node.get('weight'),
        #                 'description': node.findtext('description'),
        #                 'parentid': node.get('parentid')
        #             }
        #             result[tag_id] = tag_data
        #         return result
            
        #     # Default behavior for non-dict parsing
        #     return [node.text for node in nodes]
 
        def _parse(attr, xpath, is_list=False, is_dict=False, is_int=False, is_float=False, is_date=False, fail=False):
            try:
                # Handle data if it's coming from a dictionary (Cache)
                if isinstance(data, dict):
                    lookup_attr = attr if not attr == 'tmdb' else 'tmdb_id'
                    
                    if lookup_attr == "tmdb_id":
                        result = [str(data['tmdb_id']), str(data['tmdb_type'])] if 'tmdb_id' in data and data['tmdb_id'] else []
                        return result

                    if is_list: return data[lookup_attr].split("|") if data[lookup_attr] else []
                    if is_dict: return json.loads(data[lookup_attr]) if data[lookup_attr] else {}
                    if is_int or is_float: return util.check_num(data[lookup_attr], is_int=is_int)
                    if is_date: return datetime.strptime(data[lookup_attr], "%Y-%m-%d") if data[lookup_attr] else None
                    return data[lookup_attr]

                # Handle data if it's an XML Element (Fresh API Response)
                parse_results = data.xpath(xpath)

                if attr == "tmdb":
                    # Return text results as strings
                    result = [str(r).strip() if isinstance(r, str) else str(r.text).strip() if hasattr(r, 'text') else str(r) for r in parse_results] if parse_results else []
                    return result

                if attr == "tags":
                    return {ta.xpath("name/text()")[0]: 1001 if ta.get("infobox") else int(ta.get("weight")) for ta in parse_results}

                if  attr == "titles":
                    # API Titles: <title xml:lang="en" type="official">Title</title>
                    return {ta.get("{http://www.w3.org/XML/1998/namespace}lang"): ta.text for ta in parse_results}

                # if attr == "tags":
                #     result = {}
                #     for node in parse_results:
                #         # Use the 'id' attribute as the primary key
                #         tag_id = node.get('id')
                        
                #         # Map internal children to dictionary keys
                #         tag_data = {
                #             'name': node.findtext('name'),
                #             'weight': node.get('weight'),
                #             'description': node.findtext('description'),
                #             'parentid': node.get('parentid')
                #         }
                #         result[tag_id] = tag_data
                #     return result

                if parse_results:
                    if is_list:
                        return [r.text.strip() if hasattr(r, 'text') else str(r).strip() for r in parse_results]
                    # 
                    val = parse_results[0]
                    text_val = val.text if hasattr(val, 'text') else str(val)
                    
                    if is_int or is_float: return util.check_num(text_val.strip(), is_int=is_int)
                    if is_date: return datetime.strptime(text_val.strip(), "%Y-%m-%d")
                    return text_val.strip()

            except (ValueError, TypeError, IndexError):
                pass

            if fail:
                raise Failed(f"AniDB Error: Data point '{attr}' not found for ID: {self.anidb_id}")
            return [] if is_list else {} if is_dict else None

        # Standard API XPaths
        self.main_title = _parse("main_title", "//title[@type='main']/text()", fail=True)
        self.titles = _parse("titles", "//title[@type='official']", is_dict=True)
        self.official_title = self.titles.get(self._anidb.language, self.main_title)
        
        self.studio = _parse("studio", "//creators/name[@type='Animation Work']/text()")
        self.rating = _parse("rating", "//ratings/permanent/text()", is_float=True)
        self.average = _parse("average", "//ratings/temporary/text()", is_float=True)
        self.score = _parse("score", "//ratings/review/text()", is_float=True)
        self.released = _parse("released", "//startdate/text()", is_date=True)
        
        self.tags = _parse("tags", "//anime/tags/tag", is_dict=True)

        # Resources (External Links)
        self.mal_id = _parse("mal_id", "//resource[@type='2']/externalentity/identifier/text()", is_int=True)
        self.imdb_id = _parse("imdb_id", "//resource[@type='43']/externalentity/identifier/text()")
        
        # TMDB handling (Type 44)
        tmdb_list = _parse("tmdb", "//resource[@type='44']/externalentity/identifier/text()", is_list=True)
        self.tmdb_id = None
        self.tmdb_type = None
        for item in tmdb_list:
            if isinstance(item, str) and item.isdigit():
                self.tmdb_id = int(item)
            elif isinstance(item, str):
                self.tmdb_type = item

class AniDB:
    def __init__(self, requests_obj, cache, data):
        self.requests = requests_obj
        self.cache = cache
        self.language = data.get("language", "en")
        self.expiration = data.get("expiration", 60)
        self.enable_mature = data.get("enable_mature", False)
        self.last_request_time = 0
        self.min_delay = 0.1  # New API has no rate limiting, minimal delay for safety
        self._is_authorized = False
        self.titles_db = AniDBTitles(self.requests)

    def get_id_by_name(self, name):
        aid = self.titles_db.search(name)
        if aid:
            return aid
        raise Failed(f"AniDB Error: Title '{name}' not found in local database.")

    @property
    def is_authorized(self):
        """
        Returns True if the client has been configured and authorized.
        External code can access this via self.AniDB.is_authorized
        """
        return self._is_authorized

    def authorize(self, expiration):
        self.expiration = expiration
        self._is_authorized = False

        # Verify connectivity by requesting a known anime (Serial Experiments Lain: ID 99)
        try:
            self.get_anime(99, ignore_cache=True)
            if self.cache:
                self.cache.update_testing("anidb_login", kometa_client, kometa_client_version, "True")
            self._is_authorized = True
        except Exception as e:
            raise Failed(f"AniDB Authorization Failed: {e}")

    def _request(self, api_params=None, rss_url=None, cache_days=7, endpoint=None):
        # 1. Rate Limiting Check (minimal delay for new API)
        elapsed = time.perf_counter() - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)

        # 2. Check Cache
        aid = api_params.get('aid') if api_params else None
        cache_file = f"config/anidb_cache/anime_{aid}.xml" if aid else None
        if cache_file and os.path.exists(cache_file) and cache_days > 0:
            file_age = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_age < timedelta(days=cache_days):
                with open(cache_file, 'rb') as f:
                    return etree.fromstring(f.read())

        # 3. Setup Target and Headers
        if rss_url:
            target_url = rss_url
        elif endpoint:
            target_url = f"{api_url}/{endpoint}"
        else:
            # Default to anime endpoint with aid
            target_url = f"{api_url}/anime/{aid}" if aid else api_url
            
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': f'Kometa/1.0 ({kometa_client})'
        }
        
        # Build query parameters (for search endpoints)
        payload = {}
        if api_params and 'aid' not in api_params:
            payload.update(api_params)
        
        # Add mature flag as query parameter
        payload['mature'] = 'true' if self.enable_mature else 'false'

        # 4. Execute Request
        response = self.requests.get(target_url, params=payload if payload else None, headers=headers)
        self.last_request_time = time.perf_counter()

        if response.status_code == 200:
            content = response.content
            
            # 5. Manual Gzip Decompression Check
            # Even if 'requests' fails to auto-decode, we check the magic bytes for gzip (\x1f\x8b)
            if content.startswith(b'\x1f\x8b'):
                try:
                    content = gzip.decompress(content)
                except Exception as e:
                    raise Failed(f"AniDB Error: Failed to decompress Gzip response: {e}")

            # Check if content is empty or invalid
            if not content or len(content.strip()) == 0:
                logger.warning(f"AniDB Warning: Empty response from {target_url}")
                return None

            # 6. Check if response is JSON (for tag endpoints)
            content_type = response.headers.get('content-type', '')
            if 'json' in content_type or content.strip().startswith(b'{') or content.strip().startswith(b'['):
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"AniDB Error: Invalid JSON response from {target_url}")
                    raise Failed(f"AniDB Error: Invalid JSON response - {e}")

            # 7. Parse XML with error handling
            try:
                xml_result = etree.fromstring(content)
            except etree.XMLSyntaxError as e:
                logger.error(f"AniDB Error: Invalid XML response from {target_url}")
                logger.error(f"Response content type: {response.headers.get('content-type', 'unknown')}")
                try:
                    logger.error(f"Response preview: {content[:500].decode('utf-8', errors='replace')}")
                except:
                    logger.error(f"Response preview (bytes): {content[:500]}")
                raise Failed(f"AniDB Error: Endpoint may not be implemented - {target_url}")
            
            # 8. Save to cache
            if cache_file:
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                with open(cache_file, 'wb') as f:
                    f.write(content)
            
            return xml_result
        
        elif response.status_code == 403:
            raise Failed("AniDB Error: 403 Banned (Too many requests or invalid Client ID)")
        elif response.status_code == 404:
            logger.warning(f"AniDB Warning: 404 Not Found - {target_url}")
            return None
        else:
            logger.error(f"AniDB Error: HTTP {response.status_code} from {target_url}")
            return None
            
        return None

    def _relations(self, anidb_id):
        xml = self._request(api_params={'aid': anidb_id})
        return util.get_int_list(xml.xpath("//relatedanime/anime/@id"), "AniDB ID") if xml is not None else []

    def _validate(self, anidb_id):
        """
        Verifies if an ID exists.
        Checks Local Master List -> Local XML Cache -> AniDB API.
        """
        aid = int(anidb_id)

        # 1. Check the local Master Title List (Fastest - No network)
        if hasattr(self, 'titles_db') and aid in self.titles_db.title_map.values():
            return aid

        # 2. Check the Local XML Cache or fallback to API
        try:
            # get_anime handles the filesystem check and the 2.1s rate-limited API call
            anime = self.get_anime(aid)
            return int(anime.anidb_id)
        except Exception:
            raise Failed(f"AniDB Error: AniDB ID: {aid} not found")

    def validate_anidb_ids(self, anidb_ids):
        """
        Validates a list of AniDB IDs. 
        Returns a list of valid integer IDs.
        """
        anidb_list = util.get_int_list(anidb_ids, "AniDB ID")
        anidb_values = []
        
        for anidb_id in anidb_list:
            try:
                anidb_values.append(self._validate(anidb_id))
            except Failed as e:
                logger.error(e)
        
        if not anidb_values:
            raise Failed(f"AniDB Error: No valid AniDB IDs found in input: {anidb_ids}")
            
        return anidb_values

    def get_anime(self, anidb_id, ignore_cache=False):
        # 1. Check Module Cache (SQLite/JSON)
        expired = None
        anidb_dict = None
        if self.cache and not ignore_cache:
            anidb_dict, expired = self.cache.query_anidb(anidb_id, self.expiration)

        # 2. If not in Module Cache, check File Cache/API via _request
        if expired or not anidb_dict:
            # This calls the method that handles the delay and XML file caching
            anidb_xml = self._request(api_params={"aid": anidb_id})
            # http://utilities.kometa.wiki/anidb-service/anime/{aid}
            if anidb_xml is None:
                raise Failed(f"AniDB Error: Could not fetch Anime ID {anidb_id}")
            data_source = anidb_xml
        else:
            data_source = anidb_dict

        # 3. Create the Object
        obj = AniDBObj(self, anidb_id, data_source)
        
        # 4. Update Module Cache
        if self.cache and not ignore_cache:
            self.cache.update_anidb(expired, anidb_id, obj, self.expiration)
        return obj

    def _search_by_tags(self, tag_id, limit=None):
        """
        Search anime by tag ID using the new API endpoint.
        Args:
            tag_id: The AniDB tag ID (e.g., 36 for "military")
            limit: Maximum number of results to return (default: API default)
        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        
        response = self._request(api_params=params, endpoint=f"tags/{tag_id}", cache_days=1)
        if response is None:
            return []
        
        # Handle JSON response
        if isinstance(response, dict):
            results = response.get('results', [])
            return [anime['aid'] for anime in results if 'aid' in anime]
        
        # Fallback to XML parsing if needed
        return util.get_int_list(response.xpath("//anime/@id"), "AniDB ID")

    def _search_by_tag_names(self, tags, min_weight=0):
        """
        Search anime by tag names using the search/tags endpoint.
        Args:
            tags: Single tag name or list of tag names (e.g., ['action', 'comedy'])
            min_weight: Minimum tag weight filter (default: 0)
        """
        tag_list = tags if isinstance(tags, list) else [tags]
        params = {
            'tags': ','.join(tag_list),
            'min_weight': min_weight
        }
        
        response = self._request(api_params=params, endpoint="search/tags", cache_days=1)
        if response is None:
            return []
        
        # Handle JSON response
        if isinstance(response, dict):
            results = response.get('results', [])
            return [anime['aid'] for anime in results if 'aid' in anime]
        
        # Fallback to XML parsing if needed
        return util.get_int_list(response.xpath("//anime/@id"), "AniDB ID")

    def get_anidb_ids(self, method, data):
        # Utilizes helper methods for various search types
        anidb_ids = []
        if method == "anidb_id":
            anidb_ids.append(data)
        elif method == "anidb_relation":
            anidb_ids.extend(self._relations(data))
        elif method == "anidb_tag":
            # data should be a dict with 'tag_id' and optionally 'limit'
            tag_id = data.get('tag_id', data) if isinstance(data, dict) else data
            limit = data.get('limit') if isinstance(data, dict) else None
            anidb_ids.extend(self._search_by_tags(tag_id, limit))
        elif method == "anidb_tag_name":
            # data should be a dict with 'tags' (list or string) and optionally 'min_weight'
            tags = data.get('tags', data) if isinstance(data, dict) else data
            min_weight = data.get('min_weight', 0) if isinstance(data, dict) else 0
            anidb_ids.extend(self._search_by_tag_names(tags, min_weight))
        
        logger.debug(f"{len(anidb_ids)} AniDB IDs Found via {method}")
        return anidb_ids