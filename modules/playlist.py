import logging, os, re
from datetime import datetime
from modules import plex, util
from modules.util import Failed, ImageData
from plexapi.exceptions import NotFound
from ruamel import yaml

logger = logging.getLogger("Plex Meta Manager")

github_base = "https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Configs/master/"

class PlaylistFile:
    def __init__(self, config, file_type, path):
        self.config = config
        self.type = file_type
        self.path = path
        self.playlists = {}
        self.templates = {}
        try:
            logger.info("")
            logger.info(f"Loading Playlist File {file_type}: {path}")
            if file_type in ["URL", "Git"]:
                content_path = path if file_type == "URL" else f"{github_base}{path}.yml"
                response = self.config.get(content_path)
                if response.status_code >= 400:
                    raise Failed(f"URL Error: No file found at {content_path}")
                content = response.content
            elif os.path.exists(os.path.abspath(path)):
                content = open(path, encoding="utf-8")
            else:
                raise Failed(f"File Error: File does not exist {path}")
            data, ind, bsi = yaml.util.load_yaml_guess_indent(content)
            if data and "playlists" in data:
                if data["playlists"]:
                    if isinstance(data["playlists"], dict):
                        for _name, _data in data["playlists"].items():
                            if _name in self.config.playlist_names:
                                logger.error(f"Config Warning: Skipping duplicate playlist: {_name}")
                            elif _data is None:
                                logger.error(f"Config Warning: playlist: {_name} has no data")
                            elif not isinstance(_data, dict):
                                logger.error(f"Config Warning: playlist: {_name} must be a dictionary")
                            else:
                                self.playlists[str(_name)] = _data
                    else:
                        logger.warning(f"Config Warning: playlists must be a dictionary")
                else:
                    logger.warning(f"Config Warning: playlists attribute is blank")
            if not self.playlists:
                raise Failed("YAML Error: playlists attribute is required")
            if data and "templates" in data:
                if data["templates"]:
                    if isinstance(data["templates"], dict):
                        for _name, _data in data["templates"].items():
                            self.templates[str(_name)] = _data
                    else:
                        logger.warning(f"Config Warning: templates must be a dictionary")
                else:
                    logger.warning(f"Config Warning: templates attribute is blank")

            logger.info(f"Playlist File Loaded Successfully")
        except yaml.scanner.ScannerError as ye:
            raise Failed(f"YAML Error: {util.tab_new_lines(ye)}")
        except Exception as e:
            util.print_stacktrace()
            raise Failed(f"YAML Error: {e}")