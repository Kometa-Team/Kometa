import logging
from modules import util
from modules.util import Failed

logger = logging.getLogger("Plex Meta Manager")

builders = ["mdblist_list"]
base_url = "https://mdblist.com/lists"

headers = { 'User-Agent': 'Plex-Meta-Manager' }

class Mdblist:
    def __init__(self, config):
        self.config = config

    def validate_mdb_lists(self, mdb_lists, language):
        valid_lists = []
        for mdb_dict in util.get_list(mdb_lists, split=False):
            if not isinstance(mdb_dict, dict):
                mdb_dict = {"url": mdb_dict}
            dict_methods = {dm.lower(): dm for dm in mdb_dict}
            if "url" not in dict_methods:
                raise Failed(f"Collection Error: mdb_list url attribute not found")
            elif mdb_dict[dict_methods["url"]] is None:
                raise Failed(f"Collection Error: mdb_list url attribute is blank")
            else:
                mdb_url = mdb_dict[dict_methods["url"]].strip()
            if not mdb_url.startswith(base_url):
                raise Failed(f"Mdblist Error: {mdb_url} must begin with: {base_url}")
            list_count = None
            if "limit" in dict_methods:
                if mdb_dict[dict_methods["limit"]] is None:
                    logger.warning(f"Collection Warning: mdb_list limit attribute is blank using 0 as default")
                else:
                    try:
                        value = int(str(mdb_dict[dict_methods["limit"]]))
                        if 0 <= value:
                            list_count = value
                    except ValueError:
                        pass
                if list_count is None:
                    logger.warning(f"Collection Warning: mdb_list limit attribute must be an integer 0 or greater using 0 as default")
            if list_count is None:
                list_count = 0
            valid_lists.append({"url": mdb_url, "limit": list_count})
        return valid_lists
        
    def get_mdblist_ids(self, method, data):
        if method == "mdblist_list":
            limit_status = f" Limit at: {data['limit']} items" if data['limit'] > 0 else ''
            logger.info(f"Processing Mdblist.com List: {data['url']}{limit_status}")
            url = f"{data['url']}?limit={data['limit']}"
            return [(i["imdb_id"], "imdb") for i in self.config.get_json(url,headers=headers)]
        else:
            raise Failed(f"Mdblist Error: Method {method} not supported")
