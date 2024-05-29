import base64, os, ruamel.yaml, requests
from lxml import html
from modules import util
from modules.poster import ImageData
from modules.util import Failed
from requests.exceptions import ConnectionError
from retrying import retry
from urllib import parse

logger = util.logger

image_content_types = ["image/png", "image/jpeg", "image/webp"]

def get_header(headers, header, language):
    if headers:
        return headers
    else:
        if header and not language:
            language = "en-US,en;q=0.5"
        if language:
            return {
                "Accept-Language": "eng" if language == "default" else language,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"
            }


def parse_version(version, text="develop"):
    version = version.replace("develop", text)
    split_version = version.split(f"-{text}")
    return version, split_version[0], int(split_version[1]) if len(split_version) > 1 else 0


def quote(data):
    return parse.quote(str(data))


def quote_plus(data):
    return parse.quote_plus(str(data))


def parse_qs(data):
    return parse.parse_qs(data)


def urlparse(data):
    return parse.urlparse(str(data))

class Requests:
    def __init__(self, file_version, env_version, git_branch, verify_ssl=True):
        self.file_version = file_version
        self.env_version = env_version
        self.git_branch = git_branch
        self.image_content_types = ["image/png", "image/jpeg", "image/webp"]
        self.nightly_version = None
        self.develop_version = None
        self.master_version = None
        self.session = self.create_session()
        self.global_ssl = verify_ssl
        if not self.global_ssl:
            self.no_verify_ssl()
        self.branch = self.guess_branch()
        self.version = (self.file_version[0].replace("develop", self.branch), self.file_version[1].replace("develop", self.branch), self.file_version[2])
        self.latest_version = self.current_version(self.version, branch=self.branch)
        self.new_version = self.latest_version[0] if self.latest_version and (self.version[1] != self.latest_version[1] or (self.version[2] and self.version[2] < self.latest_version[2])) else None

    def create_session(self, verify_ssl=True):
        session = requests.Session()
        if not verify_ssl:
            self.no_verify_ssl(session)
        return session

    def no_verify_ssl(self, session=None):
        if session is None:
            session = self.session
        session.verify = False
        if session.verify is False:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def has_new_version(self):
        return self.version[0] != "Unknown" and self.latest_version[0] != "Unknown" and self.version[1] != self.latest_version[1] or (self.version[2] and self.version[2] < self.latest_version[2])

    def download_image(self, title, image_url, download_directory, is_poster=True, filename=None):
        response = self.get_image(image_url)
        new_image = os.path.join(download_directory, f"{filename}") if filename else download_directory
        if response.headers["Content-Type"] == "image/jpeg":
            new_image += ".jpg"
        elif response.headers["Content-Type"] == "image/webp":
            new_image += ".webp"
        else:
            new_image += ".png"
        with open(new_image, "wb") as handler:
            handler.write(response.content)
        return ImageData("asset_directory", new_image, prefix=f"{title}'s ", is_poster=is_poster, is_url=False)

    def file_yaml(self, path_to_file, check_empty=False, create=False, start_empty=False):
        return YAML(path=path_to_file, check_empty=check_empty, create=create, start_empty=start_empty)

    def get_yaml(self, url, headers=None, params=None, check_empty=False):
        response = self.get(url, headers=headers, params=params)
        if response.status_code >= 400:
            raise Failed(f"URL Error: No file found at {url}")
        return YAML(input_data=response.content, check_empty=check_empty)

    def get_image(self, url):
        response = self.get(url, header=True)
        if response.status_code == 404:
            raise Failed(f"Image Error: Not Found on Image URL: {url}")
        if response.status_code >= 400:
            raise Failed(f"Image Error: {response.status_code} on Image URL: {url}")
        if "Content-Type" not in response.headers or response.headers["Content-Type"] not in self.image_content_types:
            raise Failed("Image Not PNG, JPG, or WEBP")

    def get_stream(self, url, location, info="Item"):
        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = r.headers.get('content-length')
            if total_length is not None:
                total_length = int(total_length)
            dl = 0
            with open(location, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    dl += len(chunk)
                    f.write(chunk)
                    logger.ghost(f"Downloading {info}: {dl / total_length * 100:6.2f}%")
                logger.exorcise()

    def get_html(self, url, headers=None, params=None, header=None, language=None):
        return html.fromstring(self.get(url, headers=headers, params=params, header=header, language=language).content)

    def get_json(self, url, json=None, headers=None, params=None, header=None, language=None):
        response = self.get(url, json=json, headers=headers, params=params, header=header, language=language)
        try:
            return response.json()
        except ValueError:
            logger.error(str(response.content))
            raise

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def get(self, url, json=None, headers=None, params=None, header=None, language=None):
        return self.session.get(url, json=json, headers=get_header(headers, header, language), params=params)

    def get_image_encoded(self, url):
        return base64.b64encode(self.get(url).content).decode('utf-8')

    def post_html(self, url, data=None, json=None, headers=None, header=None, language=None):
        return html.fromstring(self.post(url, data=data, json=json, headers=headers, header=header, language=language).content)

    def post_json(self, url, data=None, json=None, headers=None, header=None, language=None):
        response = self.post(url, data=data, json=json, headers=headers, header=header, language=language)
        try:
            return response.json()
        except ValueError:
            logger.error(str(response.content))
            raise

    @retry(stop_max_attempt_number=6, wait_fixed=10000)
    def post(self, url, data=None, json=None, headers=None, header=None, language=None):
        return self.session.post(url, data=data, json=json, headers=get_header(headers, header, language))

    def guess_branch(self):
        if self.git_branch:
            return self.git_branch
        elif self.env_version:
            return self.env_version
        elif self.file_version[2] > 0:
            dev_version = self.get_develop()
            if self.file_version[1] != dev_version[1] or self.file_version[2] <= dev_version[2]:
                return "develop"
            else:
                return "nightly"
        else:
            return "master"

    def current_version(self, version, branch=None):
        if branch == "develop":
            return self.get_develop()
        elif branch:
            return self.get_nightly()
        elif version[2] > 0:
            new_version = self.get_develop()
            if version[1] != new_version[1] or new_version[2] >= version[2]:
                return new_version
            return self.get_nightly()
        else:
            return self.get_master()

    def get_nightly(self):
        if self.nightly_version is None:
            self.nightly_version = self.get_version("nightly")
        return self.nightly_version

    def get_develop(self):
        if self.develop_version is None:
            self.develop_version = self.get_version("develop")
        return self.develop_version

    def get_master(self):
        if self.master_version is None:
            self.master_version = self.get_version("master")
        return self.master_version

    def get_version(self, level):
        try:
            url = f"https://raw.githubusercontent.com/Kometa-Team/Kometa/{level}/VERSION"
            return parse_version(self.get(url).content.decode().strip(), text=level)
        except ConnectionError:
            return "Unknown", "Unknown", 0


class YAML:
    def __init__(self, path=None, input_data=None, check_empty=False, create=False, start_empty=False):
        self.path = path
        self.input_data = input_data
        self.yaml = ruamel.yaml.YAML()
        self.yaml.width = 100000
        self.yaml.indent(mapping=2, sequence=2)
        try:
            if input_data:
                self.data = self.yaml.load(input_data)
            else:
                if start_empty or (create and not os.path.exists(self.path)):
                    with open(self.path, 'w'):
                        pass
                    self.data = {}
                else:
                    with open(self.path, encoding="utf-8") as fp:
                        self.data = self.yaml.load(fp)
        except ruamel.yaml.error.YAMLError as e:
            e = str(e).replace("\n", "\n      ")
            raise Failed(f"YAML Error: {e}")
        except Exception as e:
            raise Failed(f"YAML Error: {e}")
        if not self.data or not isinstance(self.data, dict):
            if check_empty:
                raise Failed("YAML Error: File is empty")
            self.data = {}

    def save(self):
        if self.path:
            with open(self.path, 'w', encoding="utf-8") as fp:
                self.yaml.dump(self.data, fp)
