# Adapted from the Kometa include-markdown fork; see LICENSE and NOTICE in docs/docs-extension.
"""Persistent file cache."""

from __future__ import annotations

import hashlib
import os
import stat
import time
from importlib.util import find_spec


class Cache:
    """Cache for arbitrary content, one file per entry."""

    def __init__(  # noqa: D107
        self,
        cache_dir: str,
        expiration_seconds: int = 0,
    ):
        self.cache_dir = cache_dir
        self.expiration_seconds = expiration_seconds

    def get_creation_time_from_fpath(self, fpath: str) -> int:
        """Get creation time of an entry in the cache given its path."""
        with open(fpath, "rb") as f:
            return int(f.readline())

    @classmethod
    def generate_unique_key_from_url(cls, url: str) -> str:
        """Generate a unique key from an URL."""
        return hashlib.blake2b(url.encode(), digest_size=16).digest().hex()

    def read_file(self, fpath: str, encoding: str = "utf-8") -> str:  # noqa: D102
        f = open(fpath, encoding=encoding)  # noqa: SIM115
        content = f.read().split("\n", 1)[1]
        f.close()
        return content

    def get_(self, url: str, encoding: str = "utf-8") -> str | None:  # noqa: D102
        key = self.generate_unique_key_from_url(url)
        fpath = os.path.join(self.cache_dir, key)
        try:
            is_file = stat.S_ISREG(os.stat(fpath).st_mode)
        except (FileNotFoundError, OSError):  # pragma: no cover
            return None
        if is_file:  # pragma: no branch
            creation_time = self.get_creation_time_from_fpath(fpath)
            if time.time() < creation_time + self.expiration_seconds:
                return self.read_file(fpath, encoding=encoding)
            os.remove(fpath)
        return None

    def set_(self, url: str, value: str, encoding: str = "utf-8") -> None:  # noqa: D102
        key = self.generate_unique_key_from_url(url)
        fpath = os.path.join(self.cache_dir, key)
        with open(fpath, "wb") as fp:
            now = f"{int(time.time())}\n"
            fp.write(now.encode(encoding))
            fp.write(value.encode(encoding))

    def clean(self) -> None:
        """Clean expired entries from the cache."""
        for fname in os.listdir(self.cache_dir):
            if fname == ".gitignore":
                continue
            fpath = os.path.join(self.cache_dir, fname)
            creation_time = self.get_creation_time_from_fpath(fpath)
            if time.time() > creation_time + self.expiration_seconds:
                os.remove(fpath)


def get_cache_directory(cache_dir: str) -> str | None:
    """Get cache directory."""
    if cache_dir:
        return cache_dir

    if not is_platformdirs_installed():
        return None

    try:
        from platformdirs import user_data_dir  # noqa: PLC0415
    except ImportError:  # pragma: no cover
        return None
    else:
        return user_data_dir("kometa-docs")


def initialize_cache(expiration_seconds: int, cache_dir: str) -> Cache | None:
    """Initialize a cache instance."""
    cache_directory = get_cache_directory(cache_dir)

    if cache_directory is None:
        return None

    os.makedirs(cache_directory, exist_ok=True)

    # Add a `.gitignore` file to prevent the cache directory from being
    # included in the repository. This is needed because the cache directory
    # can be configured as a relative path with `cache_dir` setting.
    gitignore = os.path.join(cache_directory, ".gitignore")
    if not os.path.exists(gitignore):
        with open(gitignore, "wb") as f:
            f.write(b"*\n")

    cache = Cache(cache_directory, expiration_seconds)
    cache.clean()
    return cache


def is_platformdirs_installed() -> bool:
    """Check if `platformdirs` package is installed without importing it."""
    return find_spec("platformdirs") is not None
