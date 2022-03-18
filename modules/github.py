import re
from modules import util
from modules.util import Failed

logger = util.logger

base_url = "https://api.github.com/repos/meisnate12/Plex-Meta-Manager"

class GitHub:
    def __init__(self, config):
        self.config = config

    def latest_release_notes(self):
        response = self.config.get_json(f"{base_url}/releases/latest")
        return response["body"]

    def get_develop_commits(self, dev_version):
        master_sha = self.config.get_json(f"{base_url}/commits/master")["sha"]
        response = self.config.get_json(f"{base_url}/commits?sha=develop")
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
        