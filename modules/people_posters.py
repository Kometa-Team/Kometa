import hashlib
import json
import os
import re
import shutil
import tempfile
import threading
import time
import unicodedata
from io import BytesIO
from urllib.parse import quote

from pathvalidate import sanitize_filename
from PIL import Image, UnidentifiedImageError
from requests.exceptions import RequestException
from tenacity import RetryError

from modules import util
from modules.github import base_url, raw_url
from modules.people_render import STYLES, PeopleRenderer
from modules.poster import ImageData
from modules.util import Failed

logger = util.logger

DEFAULT_ORIGINAL_REPO = "Kometa-Team/People-Images-1500"
DEFAULT_TRANSPARENT_REPO = "Kometa-Team/People-Images-transparent-1500"
DEFAULT_PRUNE_DAYS = 90
DEFAULT_RENDER_LIMIT = 250
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def person_key(name):
    return unicodedata.normalize("NFC", str(name)).casefold()


def git_blob_sha(content):
    """Return the SHA-1 Git stores for a blob, which is the SHA in a repository tree listing."""
    return hashlib.sha1(f"blob {len(content)}\0".encode("ascii") + content).hexdigest()


class PeoplePosters:
    """Generates styled People Posters locally from the transparent person images on GitHub and keeps them in a persistent cache.

    Each run reads the source repository's file tree once to learn every image's blob SHA. A cached poster is reused while its source SHA and the style's
    renderer fingerprint are unchanged; otherwise the source is downloaded (or reused from the source cache) and the poster is rendered again.
    """

    def __init__(self, requests, github, cache, config_dir, params):
        self.requests = requests
        self.github = github
        self.cache = cache
        self.original_repo = params["original_repo"]
        self.transparent_repo = params["transparent_repo"]
        self.branch = params["branch"] or "HEAD"
        self.prune_days = params["prune_days"]
        self.render_limit = params["render_limit"]
        for repo in (self.original_repo, self.transparent_repo):
            if not REPO_RE.match(repo):
                raise Failed(f"People Posters Error: {repo} is not a valid GitHub repository; use the form owner/name")
        self.persistent = cache is not None
        self._cache_dir = os.path.join(config_dir, "cache", "people_posters") if self.persistent else None
        self.renderer = PeopleRenderer()
        self._lock = threading.RLock()
        self._trees = {}
        self._run_posters = {}
        self.rendered = 0
        self.reused = 0
        self.skipped = 0
        self.missing = 0

    @property
    def cache_dir(self):
        if self._cache_dir is None:
            self._cache_dir = tempfile.mkdtemp(prefix="kometa-people-posters-")
        return self._cache_dir

    def _tree_file(self, repo):
        return os.path.join(self.cache_dir, "_trees", f"{repo.replace('/', '__')}__{sanitize_filename(self.branch)}.json")

    def _load_tree_file(self, repo):
        try:
            with open(self._tree_file(repo), encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, ValueError):
            return None

    def _fetch_tree(self, repo):
        """Returns ``{normalized person name: [path, blob sha]}`` for every image in the repository."""
        tree_key = f"{repo}@{self.branch}"
        stored = self._load_tree_file(repo) if self.persistent else None
        headers = dict(self.github.headers) if self.github and self.github.headers else {}
        headers["Accept"] = "application/vnd.github+json"
        etag = self.cache.query_people_poster_tree(tree_key) if self.persistent else None
        if etag and stored is not None:
            headers["If-None-Match"] = etag
        url = f"{base_url}/repos/{repo}/git/trees/{self.branch}?recursive=1"
        try:
            response = self.requests.get(url, headers=headers)
        except (RequestException, RetryError) as e:
            response = None
            error = str(e)
        else:
            error = f"{response.status_code} {response.reason}"
        if response is not None and response.status_code == 304 and stored is not None:
            logger.debug(f"People Posters: {repo} file list unchanged")
            return stored
        if response is not None and response.status_code == 200:
            data = response.json()
            if data.get("truncated"):
                logger.warning(f"People Posters Warning: GitHub returned a partial file list for {repo}; some people may be reported as missing")
            tree = {}
            for entry in data.get("tree", []):
                path = entry.get("path", "")
                if entry.get("type") == "blob" and "/Images/" in path:
                    stem = os.path.splitext(path.rsplit("/", 1)[-1])[0]
                    tree[person_key(stem)] = [path, entry["sha"]]
            if self.persistent:
                os.makedirs(os.path.dirname(self._tree_file(repo)), exist_ok=True)
                temp_path = f"{self._tree_file(repo)}.tmp"
                with open(temp_path, "w", encoding="utf-8") as handle:
                    json.dump(tree, handle, ensure_ascii=False)
                os.replace(temp_path, self._tree_file(repo))
                self.cache.update_people_poster_tree(tree_key, response.headers.get("ETag"))
            logger.info(f"People Posters: Loaded {len(tree)} images from {repo}")
            return tree
        if stored is not None:
            logger.warning(f"People Posters Warning: Could not refresh the file list for {repo} ({error}); using the list from a previous run")
            return stored
        hint = " Add a GitHub token to raise the rate limit." if response is not None and response.status_code in (403, 429) and not (self.github and self.github.token) else ""
        raise Failed(f"People Posters Error: Could not read the file list for {repo} ({error}).{hint}")

    def _tree(self, repo):
        with self._lock:
            if repo not in self._trees:
                try:
                    self._trees[repo] = self._fetch_tree(repo)
                except Failed:
                    self._trees[repo] = None
                    raise
            if self._trees[repo] is None:
                raise Failed(f"People Posters Error: The file list for {repo} is unavailable this run")
            return self._trees[repo]

    def _lookup(self, repo, name):
        entry = self._tree(repo).get(person_key(name))
        if not entry:
            with self._lock:
                self.missing += 1
            raise Failed(f"People Posters Error: No image for {name} in {repo}")
        return entry

    def original_url(self, name):
        """Returns the raw URL of a person's original photograph, which is used as-is without rendering."""
        path, _ = self._lookup(self.original_repo, name)
        return f"{raw_url}/{self.original_repo}/{self.branch}/{quote(path)}"

    def _source_path(self, sha):
        return os.path.join(self.cache_dir, "_source", sha[:2], f"{sha}.png")

    def _discard_source(self, source_path):
        try:
            os.remove(source_path)
        except FileNotFoundError:
            pass

    def _open_source(self, content, source_path, sha):
        try:
            with Image.open(BytesIO(content)) as image:
                image.load()
                return image.copy()
        except (UnidentifiedImageError, Image.DecompressionBombError) as error:
            self._discard_source(source_path)
            raise Failed(f"People Posters Error: Source image {sha} is not a usable image ({error})") from error

    def _source(self, path, sha):
        """Returns the transparent source image, downloading it unless this exact blob is already cached."""
        source_path = self._source_path(sha)
        if os.path.exists(source_path):
            with open(source_path, "rb") as handle:
                content = handle.read()
            if git_blob_sha(content) == sha:
                os.utime(source_path)
                return self._open_source(content, source_path, sha)
            self._discard_source(source_path)
        url = f"{raw_url}/{self.transparent_repo}/{self.branch}/{quote(path)}"
        try:
            response = self.requests.get(url)
        except (RequestException, RetryError) as error:
            raise Failed(f"People Posters Error: Could not download {url} ({error})") from error
        if response.status_code != 200:
            raise Failed(f"People Posters Error: Could not download {url} ({response.status_code} {response.reason})")
        if git_blob_sha(response.content) != sha:
            raise Failed(f"People Posters Error: Downloaded {url} did not match blob {sha}")
        os.makedirs(os.path.dirname(source_path), exist_ok=True)
        temp_path = f"{source_path}.tmp"
        with open(temp_path, "wb") as handle:
            handle.write(response.content)
        os.replace(temp_path, source_path)
        return self._open_source(response.content, source_path, sha)

    def poster_path(self, name, style):
        filename = sanitize_filename(unicodedata.normalize("NFC", name)) or "_"
        return os.path.join(self.cache_dir, style, filename[0].upper(), f"{filename}.jpg")

    def get(self, name, style):
        """Returns the cached or newly rendered poster for a person, or ``None`` when this run's render limit has been reached.

        Raises ``Failed`` when the person has no transparent image or the poster can't be produced.
        """
        if style not in STYLES:
            raise Failed(f"People Posters Error: Unknown style {style}; use one of {', '.join(STYLES)}")
        path, sha = self._lookup(self.transparent_repo, name)
        fingerprint = self.renderer.fingerprint(style)
        key = f"{style}|{person_key(name)}"
        poster_path = self.poster_path(name, style)
        image = ImageData("people_poster", poster_path, prefix=f"{name}'s ", is_url=False, compare=f"{sha}:{fingerprint}")
        with self._lock:
            if key in self._run_posters:
                return self._run_posters[key]
            row = self.cache.query_people_poster(key) if self.persistent else None
            if row and row["source_sha"] == sha and row["renderer_fp"] == fingerprint and row["path"] == poster_path and os.path.exists(poster_path):
                self.cache.touch_people_poster(key)
                self.reused += 1
                self._run_posters[key] = image
                return image
            if self.render_limit and self.rendered >= self.render_limit:
                if not self.skipped:
                    logger.warning(f"People Posters Warning: Reached the render limit of {self.render_limit} posters for this run; the remaining posters will be generated on later runs")
                self.skipped += 1
                return None
            started = time.perf_counter()
            source = self._source(path, sha)
            self.renderer.save(self.renderer.render(source, name, style), poster_path)
            if self.persistent:
                self.cache.update_people_poster(key, style, name, poster_path, sha, fingerprint)
            self.rendered += 1
            logger.debug(f"People Posters: Rendered {style} poster for {name} in {time.perf_counter() - started:.2f}s")
            self._run_posters[key] = image
            return image

    def prune(self):
        if not self.persistent or not self.prune_days:
            return 0
        removed = self.cache.query_unused_people_posters(self.prune_days)
        for _, path in removed:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
        self.cache.delete_people_posters([key for key, _ in removed])
        cutoff = time.time() - self.prune_days * 86400
        source_dir = os.path.join(self.cache_dir, "_source")
        for folder, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(folder, file)
                if os.path.getmtime(file_path) < cutoff:
                    os.remove(file_path)
                    removed.append((None, file_path))
        return len(removed)

    def finish(self):
        """Logs the run's totals, prunes unused cache entries and removes the temporary cache when caching is disabled."""
        if self.rendered or self.reused or self.skipped or self.missing:
            logger.separator("People Posters", space=False, border=False)
            logger.info(f"Rendered: {self.rendered}  Reused from cache: {self.reused}  Missing source image: {self.missing}")
            if self.skipped:
                logger.warning(f"People Posters Warning: {self.skipped} posters were not generated because the render limit of {self.render_limit} was reached")
        if self.persistent:
            try:
                pruned = self.prune()
                if pruned:
                    logger.info(f"People Posters: Removed {pruned} cached files unused for {self.prune_days} days")
            except OSError as e:
                logger.error(f"People Posters Error: Could not prune the cache: {e}")
        elif self._cache_dir:
            shutil.rmtree(self._cache_dir, ignore_errors=True)
            self._cache_dir = None
