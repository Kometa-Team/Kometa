"""
Poster Fetcher for Kometa Web UI

Fetches posters from Plex and TMDb for overlay preview without running the full builder.
"""

import os
import re
import base64
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from io import BytesIO

import requests
from ruamel.yaml import YAML

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class PosterFetcher:
    """Fetches posters from Plex and TMDb for overlay preview."""

    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

        # Load config to get Plex/TMDb credentials
        self._plex_url = None
        self._plex_token = None
        self._tmdb_api_key = None
        self._load_config()

    def _load_config(self):
        """Load Plex and TMDb credentials from config."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = self.yaml.load(f)

            if config:
                # Get Plex credentials
                plex_config = config.get("plex", {})
                if isinstance(plex_config, dict):
                    self._plex_url = plex_config.get("url", "").rstrip("/")
                    self._plex_token = plex_config.get("token")

                # Get TMDb API key
                tmdb_config = config.get("tmdb", {})
                if isinstance(tmdb_config, dict):
                    self._tmdb_api_key = tmdb_config.get("apikey")

        except Exception as e:
            print(f"Warning: Failed to load config: {e}")

    @property
    def has_plex(self) -> bool:
        """Check if Plex credentials are available."""
        return bool(self._plex_url and self._plex_token)

    @property
    def has_tmdb(self) -> bool:
        """Check if TMDb API key is available."""
        return bool(self._tmdb_api_key)

    def get_status(self) -> Dict[str, Any]:
        """Get status of available poster sources."""
        return {
            "plex": {
                "available": self.has_plex,
                "url": self._plex_url if self.has_plex else None
            },
            "tmdb": {
                "available": self.has_tmdb
            }
        }

    def search_plex(self, query: str, library: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search Plex for media items."""
        if not self.has_plex:
            return []

        results = []

        try:
            # Search all libraries or specific library
            search_url = f"{self._plex_url}/search"
            params = {
                "query": query,
                "X-Plex-Token": self._plex_token,
                "limit": limit
            }

            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()

            # Parse XML response
            from xml.etree import ElementTree
            root = ElementTree.fromstring(response.content)

            for item in root.findall(".//Video") + root.findall(".//Directory"):
                item_type = item.get("type")
                if item_type not in ["movie", "show", "season", "episode"]:
                    continue

                # Filter by library if specified
                if library:
                    lib_title = item.get("librarySectionTitle", "")
                    if library.lower() not in lib_title.lower():
                        continue

                result = {
                    "rating_key": item.get("ratingKey"),
                    "title": item.get("title"),
                    "year": item.get("year"),
                    "type": item_type,
                    "library": item.get("librarySectionTitle"),
                    "thumb": item.get("thumb"),
                    "art": item.get("art"),
                    "summary": (item.get("summary") or "")[:200]
                }

                # Add parent info for seasons/episodes
                if item_type == "season":
                    result["show_title"] = item.get("parentTitle")
                    result["season_number"] = item.get("index")
                elif item_type == "episode":
                    result["show_title"] = item.get("grandparentTitle")
                    result["season_number"] = item.get("parentIndex")
                    result["episode_number"] = item.get("index")

                results.append(result)

                if len(results) >= limit:
                    break

        except Exception as e:
            print(f"Plex search error: {e}")

        return results

    def get_plex_libraries(self) -> List[Dict[str, Any]]:
        """Get list of Plex libraries."""
        if not self.has_plex:
            return []

        libraries = []

        try:
            url = f"{self._plex_url}/library/sections"
            params = {"X-Plex-Token": self._plex_token}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            from xml.etree import ElementTree
            root = ElementTree.fromstring(response.content)

            for directory in root.findall(".//Directory"):
                lib_type = directory.get("type")
                if lib_type in ["movie", "show"]:
                    libraries.append({
                        "key": directory.get("key"),
                        "title": directory.get("title"),
                        "type": lib_type,
                        "count": directory.get("count", 0)
                    })

        except Exception as e:
            print(f"Failed to get Plex libraries: {e}")

        return libraries

    def get_plex_poster_url(self, rating_key: str, poster_type: str = "thumb") -> Optional[str]:
        """Get poster URL for a Plex item."""
        if not self.has_plex:
            return None

        try:
            # Get item metadata
            url = f"{self._plex_url}/library/metadata/{rating_key}"
            params = {"X-Plex-Token": self._plex_token}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            from xml.etree import ElementTree
            root = ElementTree.fromstring(response.content)

            # Find the item
            item = root.find(".//Video") or root.find(".//Directory")
            if item is None:
                return None

            # Get thumb or art
            thumb = item.get(poster_type) or item.get("thumb")
            if thumb:
                return f"{self._plex_url}{thumb}?X-Plex-Token={self._plex_token}"

        except Exception as e:
            print(f"Failed to get Plex poster URL: {e}")

        return None

    def fetch_poster_image(
        self,
        rating_key: Optional[str] = None,
        url: Optional[str] = None,
        tmdb_id: Optional[str] = None,
        media_type: str = "movie",
        resize: Optional[Tuple[int, int]] = None
    ) -> Optional[bytes]:
        """
        Fetch a poster image from various sources.

        Args:
            rating_key: Plex rating key
            url: Direct image URL
            tmdb_id: TMDb ID for fetching from TMDb
            media_type: Type of media (movie, tv)
            resize: Optional tuple (width, height) to resize image

        Returns:
            Image bytes or None
        """
        image_url = None

        # Priority: direct URL > Plex > TMDb
        if url:
            image_url = url
        elif rating_key and self.has_plex:
            image_url = self.get_plex_poster_url(rating_key)
        elif tmdb_id and self.has_tmdb:
            image_url = self._get_tmdb_poster_url(tmdb_id, media_type)

        if not image_url:
            return None

        try:
            # Add token if it's a Plex URL without token
            if self._plex_url and image_url.startswith(self._plex_url) and "X-Plex-Token" not in image_url:
                separator = "&" if "?" in image_url else "?"
                image_url = f"{image_url}{separator}X-Plex-Token={self._plex_token}"

            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            image_data = response.content

            # Resize if requested and PIL is available
            if resize and HAS_PIL:
                img = Image.open(BytesIO(image_data))
                img = img.resize(resize, Image.Resampling.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_data = buffer.getvalue()

            return image_data

        except Exception as e:
            print(f"Failed to fetch poster image: {e}")
            return None

    def fetch_poster_base64(
        self,
        rating_key: Optional[str] = None,
        url: Optional[str] = None,
        tmdb_id: Optional[str] = None,
        media_type: str = "movie",
        resize: Optional[Tuple[int, int]] = None
    ) -> Optional[str]:
        """Fetch poster and return as base64 data URI."""
        image_data = self.fetch_poster_image(rating_key, url, tmdb_id, media_type, resize)
        if image_data:
            b64 = base64.b64encode(image_data).decode("utf-8")
            return f"data:image/png;base64,{b64}"
        return None

    def _get_tmdb_poster_url(self, tmdb_id: str, media_type: str = "movie") -> Optional[str]:
        """Get poster URL from TMDb."""
        if not self.has_tmdb:
            return None

        try:
            endpoint = "movie" if media_type == "movie" else "tv"
            url = f"https://api.themoviedb.org/3/{endpoint}/{tmdb_id}"
            params = {"api_key": self._tmdb_api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            poster_path = data.get("poster_path")

            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"

        except Exception as e:
            print(f"TMDb API error: {e}")

        return None

    def search_tmdb(self, query: str, media_type: str = "movie", limit: int = 10) -> List[Dict[str, Any]]:
        """Search TMDb for media items."""
        if not self.has_tmdb:
            return []

        results = []

        try:
            endpoint = "movie" if media_type == "movie" else "tv"
            url = f"https://api.themoviedb.org/3/search/{endpoint}"
            params = {
                "api_key": self._tmdb_api_key,
                "query": query
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            for item in data.get("results", [])[:limit]:
                result = {
                    "tmdb_id": str(item.get("id")),
                    "title": item.get("title") or item.get("name"),
                    "year": (item.get("release_date") or item.get("first_air_date") or "")[:4],
                    "type": media_type,
                    "overview": (item.get("overview") or "")[:200],
                    "poster_path": item.get("poster_path")
                }

                if result["poster_path"]:
                    result["poster_url"] = f"https://image.tmdb.org/t/p/w200{result['poster_path']}"

                results.append(result)

        except Exception as e:
            print(f"TMDb search error: {e}")

        return results

    def get_recent_items(self, library_key: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently added items from a Plex library."""
        if not self.has_plex:
            return []

        results = []

        try:
            url = f"{self._plex_url}/library/sections/{library_key}/recentlyAdded"
            params = {
                "X-Plex-Token": self._plex_token,
                "X-Plex-Container-Start": 0,
                "X-Plex-Container-Size": limit
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            from xml.etree import ElementTree
            root = ElementTree.fromstring(response.content)

            for item in root.findall(".//Video") + root.findall(".//Directory"):
                item_type = item.get("type")

                result = {
                    "rating_key": item.get("ratingKey"),
                    "title": item.get("title"),
                    "year": item.get("year"),
                    "type": item_type,
                    "thumb": item.get("thumb"),
                    "added_at": item.get("addedAt")
                }

                # Build thumbnail URL
                if result["thumb"]:
                    result["thumb_url"] = f"{self._plex_url}{result['thumb']}?X-Plex-Token={self._plex_token}&width=150&height=225"

                results.append(result)

        except Exception as e:
            print(f"Failed to get recent items: {e}")

        return results
