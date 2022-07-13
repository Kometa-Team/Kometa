import re
from modules import util

logger = util.logger

base_url = "https://api.github.com/repos/meisnate12/Plex-Meta-Manager"
configs_raw_url = "https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Configs"

class GitHub:
    def __init__(self, config):
        self.config = config
        self._configs_url = None

    def latest_release_notes(self):
        response = self.config.get_json(f"{base_url}/releases/latest")
        return response["body"]

    def get_commits(self, dev_version, nightly=False):
        master_sha = self.config.get_json(f"{base_url}/commits/master")["sha"]
        response = self.config.get_json(f"{base_url}/commits", params={"sha": "nightly" if nightly else "develop"})
        commits = []
        for commit in response:
            if commit["sha"] == master_sha:
                break
            message = commit["commit"]["message"]
            match = re.match("^\\[(\\d)\\]", message)
            if match and int(match.group(1)) <= dev_version:
                break
            commits.append(message)
        return "\n".join(commits)

    @property
    def configs_url(self):
        if self._configs_url is None:
            try:
                config_tags = [r["ref"][10:] for r in self.config.get_json(f"{base_url}-Configs/git/refs/tags")]
            except TypeError:
                config_tags = []
            if self.config.version[1] in config_tags:
                self._configs_url = f"{configs_raw_url}/{self.config.version[1]}/"
            else:
                self._configs_url = f"{configs_raw_url}/master/"
        return self._configs_url
