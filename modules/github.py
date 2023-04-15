import re
from modules import util
from modules.util import Failed

logger = util.logger

raw_url = "https://raw.githubusercontent.com"
base_url = "https://api.github.com"
pmm_base = f"{base_url}/repos/meisnate12/Plex-Meta-Manager"
configs_raw_url = f"{raw_url}/meisnate12/Plex-Meta-Manager-Configs"

class GitHub:
    def __init__(self, config):
        self.config = config
        self.images_raw_url = f"{raw_url}/meisnate12/PMM-Image-Sets/master/"
        self.translation_url = f"{raw_url}/meisnate12/PMM-Translations/master/defaults/"
        self._configs_url = None
        self._config_tags = []
        self._translation_keys = []
        self._translations = {}

    def get_top_tree(self, repo):
        if not str(repo).startswith("/"):
            repo = f"/{repo}"
        if not str(repo).endswith("/"):
            repo = f"{repo}/"
        response = self.config.get(f"{base_url}/repos{repo}commits")
        if response.status_code >= 400:
            raise Failed(f"Git Error: No repo found at https://github.com{repo}")
        return self.get_tree(response.json()[0]["commit"]["tree"]["url"]), repo

    def get_tree(self, tree_url):
        response = self.config.get(tree_url)
        if response.status_code >= 400:
            raise Failed(f"Git Error: No tree found at {tree_url}")
        return {i["path"]: i for i in response.json()["tree"]}

    def latest_release_notes(self):
        response = self.config.get_json(f"{pmm_base}/releases/latest")
        return response["body"]

    def get_commits(self, dev_version, nightly=False):
        master_sha = self.config.get_json(f"{pmm_base}/commits/master")["sha"]
        response = self.config.get_json(f"{pmm_base}/commits", params={"sha": "nightly" if nightly else "develop"})
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
    def config_tags(self):
        if not self._config_tags:
            try:
                self._config_tags = [r["ref"][11:] for r in self.config.get_json(f"{pmm_base}-Configs/git/refs/tags")]
            except TypeError:
                pass
        return self._config_tags

    @property
    def configs_url(self):
        if self._configs_url is None:
            self._configs_url = f"{configs_raw_url}/master/"
            if self.config.version[1] in self.config_tags and (
                    self.config.latest_version[1] != self.config.version[1]
                    or (not self.config.check_nightly and 0 <= self.config.version[2] <= util.get_develop()[2])
            ):
                self._configs_url = f"{configs_raw_url}/v{self.config.version[1]}/"
        return self._configs_url

    @property
    def translation_keys(self):
        if not self._translation_keys:
            tree, repo = self.get_top_tree("meisnate12/PMM-Translations")
            self._translation_keys = [tk[:-4] for tk in self.get_tree(tree["defaults"]["url"])]
        return self._translation_keys

    def translation_yaml(self, translation_key):
        if translation_key not in self._translations:
            url = f"{self.translation_url}{translation_key}.yml"
            yaml = util.YAML(input_data=self.config.get(url).content).data
            output = {"collections": {}, "key_names": {}, "variables": {}}
            for k in output:
                if k in yaml:
                    output[k] = yaml[k]
            self._translations[translation_key] = output
        return self._translations[translation_key]
