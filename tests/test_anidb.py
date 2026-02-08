"""
Comprehensive test suite for the AniDB module.

Tests cover:
- AniDBTitles class functionality (loading, searching)
- AniDBObj class data parsing from XML and dict
- AniDB class request handling, caching, authorization
- API rate limiting and error handling
- Popular anime, relations, and ID validation
"""

import pytest
import os
import tempfile
import shutil
import gzip
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, mock_open
from lxml import etree
import json

# Import the module to test
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the logger before importing anidb
from unittest.mock import Mock
import modules.util as util
util.logger = Mock()

from modules.anidb import AniDBTitles, AniDBObj, AniDB
from modules.util import Failed


# Fixtures
@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory for testing."""
    temp_dir = tempfile.mkdtemp()
    cache_dir = os.path.join(temp_dir, "config", "anidb_cache")
    os.makedirs(cache_dir, exist_ok=True)
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_requests():
    """Mock requests object."""
    return Mock()


@pytest.fixture
def mock_cache():
    """Mock cache object."""
    cache = Mock()
    cache.query_anidb = Mock(return_value=(None, True))
    cache.update_anidb = Mock()
    cache.update_testing = Mock()
    return cache


@pytest.fixture
def anidb_no_titles(mock_requests, mock_cache):
    """Create AniDB instance without loading titles database."""
    with patch.object(AniDBTitles, '_load', return_value=None):
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        anidb.titles_db.title_map = {}  # Empty title map for tests
        return anidb


@pytest.fixture
def sample_anime_xml():
    """Sample anime XML response for testing."""
    xml_str = """<?xml version="1.0" encoding="UTF-8"?>
    <anime id="1" restricted="0">
        <type>TV Series</type>
        <episodecount>26</episodecount>
        <startdate>1998-07-07</startdate>
        <enddate>1998-09-28</enddate>
        <title xml:lang="x-jat" type="main">Serial Experiments Lain</title>
        <title xml:lang="en" type="official">Serial Experiments Lain</title>
        <title xml:lang="ja" type="official">シリアルエクスペリメンツレイン</title>
        <title xml:lang="fr" type="official">Serial Experiments Lain</title>
        <creators>
            <name type="Animation Work">Triangle Staff</name>
        </creators>
        <ratings>
            <permanent>8.51</permanent>
            <temporary>8.35</temporary>
            <review>7.9</review>
        </ratings>
        <resources>
            <resource type="2">
                <externalentity>
                    <identifier>339</identifier>
                </externalentity>
            </resource>
            <resource type="43">
                <externalentity>
                    <identifier>tt0500092</identifier>
                </externalentity>
            </resource>
            <resource type="44">
                <externalentity>
                    <identifier>tv</identifier>
                </externalentity>
            </resource>
            <resource type="44">
                <externalentity>
                    <identifier>12345</identifier>
                </externalentity>
            </resource>
        </resources>
        <relatedanime>
            <anime aid="17" type="Sequel"/>
            <anime aid="23" type="Prequel"/>
        </relatedanime>
    </anime>"""
    return etree.fromstring(xml_str.encode())


@pytest.fixture
def sample_titles_xml():
    """Sample titles XML for testing AniDBTitles."""
    xml_str = """<?xml version="1.0" encoding="UTF-8"?>
    <animes>
        <anime aid="1">
            <title>Serial Experiments Lain</title>
            <title>Lain</title>
            <title>シリアルエクスペリメンツレイン</title>
        </anime>
        <anime aid="99">
            <title>Cowboy Bebop</title>
            <title>カウボーイビバップ</title>
        </anime>
        <anime aid="107">
            <title>Test Anime</title>
        </anime>
    </animes>"""
    return xml_str


@pytest.fixture
def sample_popular_xml():
    """Sample popular feed XML."""
    xml_str = """<?xml version="1.0" encoding="UTF-8"?>
    <rss>
        <channel>
            <item>
                <guid>1</guid>
            </item>
            <item>
                <guid>99</guid>
            </item>
            <item>
                <guid>107</guid>
            </item>
        </channel>
    </rss>"""
    return etree.fromstring(xml_str.encode())


@pytest.fixture
def sample_tag_search_xml():
    """Sample tag search results XML."""
    xml_str = """<?xml version="1.0" encoding="UTF-8"?>
    <search>
        <anime aid="1"/>
        <anime aid="25"/>
        <anime aid="42"/>
        <anime aid="99"/>
    </search>"""
    return etree.fromstring(xml_str.encode())


# AniDBTitles Tests
class TestAniDBTitles:
    """Tests for AniDBTitles class."""

    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_init_with_fresh_cache(self, mock_getmtime, mock_exists, mock_requests, temp_cache_dir, sample_titles_xml):
        """Test initialization when cache is fresh (< 24 hours)."""
        cache_file = os.path.join(temp_cache_dir, "config", "anidb_cache", "anime-titles.xml")
        
        # Setup: cache exists and is fresh
        mock_exists.return_value = True
        mock_getmtime.return_value = datetime.now().timestamp() - 3600  # 1 hour old
        
        # Create actual cache file
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            f.write(sample_titles_xml)
        
        with patch.object(AniDBTitles, 'CACHE_FILE', cache_file):
            titles = AniDBTitles(mock_requests)
        
        # Should not download (no request made)
        mock_requests.get.assert_not_called()
        
        # Should have parsed titles
        assert titles.search("Serial Experiments Lain") == 1
        assert titles.search("cowboy bebop") == 99

    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_init_downloads_when_old(self, mock_getmtime, mock_exists, mock_requests, temp_cache_dir, sample_titles_xml):
        """Test initialization downloads when cache is old (> 24 hours)."""
        cache_file = os.path.join(temp_cache_dir, "config", "anidb_cache", "anime-titles.xml")
        
        # Setup: cache is old
        mock_exists.return_value = True
        mock_getmtime.return_value = datetime.now().timestamp() - (25 * 3600)  # 25 hours old
        
        # Mock download
        compressed = gzip.compress(sample_titles_xml.encode())
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = compressed
        mock_requests.get.return_value = mock_response
        
        with patch.object(AniDBTitles, 'CACHE_FILE', cache_file):
            titles = AniDBTitles(mock_requests)
        
        # Should have downloaded
        mock_requests.get.assert_called_once()
        
        # Should have saved file
        assert os.path.exists(cache_file)

    def test_search_case_insensitive(self, mock_requests, temp_cache_dir, sample_titles_xml):
        """Test that search is case-insensitive."""
        cache_file = os.path.join(temp_cache_dir, "config", "anidb_cache", "anime-titles.xml")
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            f.write(sample_titles_xml)
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getmtime', return_value=datetime.now().timestamp()), \
             patch.object(AniDBTitles, 'CACHE_FILE', cache_file):
            titles = AniDBTitles(mock_requests)
        
        assert titles.search("SERIAL EXPERIMENTS LAIN") == 1
        assert titles.search("serial experiments lain") == 1
        assert titles.search("Serial Experiments Lain") == 1

    def test_search_returns_none_for_unknown(self, mock_requests, temp_cache_dir, sample_titles_xml):
        """Test that search returns None for unknown titles."""
        cache_file = os.path.join(temp_cache_dir, "config", "anidb_cache", "anime-titles.xml")
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            f.write(sample_titles_xml)
        
        with patch('os.path.exists', return_value=True), \
             patch('os.path.getmtime', return_value=datetime.now().timestamp()), \
             patch.object(AniDBTitles, 'CACHE_FILE', cache_file):
            titles = AniDBTitles(mock_requests)
        
        assert titles.search("Unknown Anime Title") is None


# AniDBObj Tests
class TestAniDBObj:
    """Tests for AniDBObj class."""

    def test_parse_from_xml(self, anidb_no_titles, sample_anime_xml):
        """Test parsing anime data from XML."""
        obj = AniDBObj(anidb_no_titles, 1, sample_anime_xml)
        
        assert obj.anidb_id == 1
        assert obj.main_title == "Serial Experiments Lain"
        assert obj.official_title == "Serial Experiments Lain"
        assert obj.studio == "Triangle Staff"
        assert obj.rating == 8.51
        assert obj.average == 8.35
        assert obj.score == 7.9
        assert obj.mal_id == 339
        assert obj.imdb_id == "tt0500092"
        assert obj.tmdb_id == 12345
        assert obj.tmdb_type == "tv"
        assert obj.released == datetime(1998, 7, 7)

    def test_parse_from_dict_cache(self, anidb_no_titles):
        """Test parsing anime data from cache dictionary."""
        
        cache_dict = {
            "main_title": "Test Anime",
            "titles": json.dumps({"en": "Test Anime", "ja": "テスト"}),
            "studio": "Test Studio",
            "rating": "8.5",
            "average": "8.0",
            "score": "7.5",
            "released": "2020-01-15",
            "tags": "",
            "mal_id": "12345",
            "imdb_id": "tt1234567",
            "tmdb_id": "54321",
            "tmdb_type": "movie"
        }
        
        obj = AniDBObj(anidb_no_titles, 999, cache_dict)
        
        assert obj.main_title == "Test Anime"
        assert obj.official_title == "Test Anime"
        assert obj.studio == "Test Studio"
        assert obj.rating == 8.5
        assert obj.mal_id == 12345

    def test_parse_with_missing_data(self, anidb_no_titles):
        """Test parsing with missing optional fields."""
        xml_str = """<?xml version="1.0" encoding="UTF-8"?>
        <anime id="1">
            <title xml:lang="x-jat" type="main">Minimal Anime</title>
        </anime>"""
        xml = etree.fromstring(xml_str.encode())
        
        obj = AniDBObj(anidb_no_titles, 1, xml)
        
        assert obj.main_title == "Minimal Anime"
        assert obj.studio is None
        assert obj.rating is None
        assert obj.mal_id is None
        assert obj.imdb_id is None

    def test_parse_fails_without_main_title(self, anidb_no_titles):
        """Test that parsing fails when main title is missing."""
        xml_str = """<?xml version="1.0" encoding="UTF-8"?>
        <anime id="1">
            <title xml:lang="en" type="official">No Main Title</title>
        </anime>"""
        xml = etree.fromstring(xml_str.encode())
        
        with pytest.raises(Failed, match="Data point 'main_title' not found"):
            AniDBObj(anidb_no_titles, 1, xml)

    def test_language_fallback(self, mock_requests, mock_cache):
        """Test that official_title falls back to main_title when language not available."""
        xml_str = """<?xml version="1.0" encoding="UTF-8"?>
        <anime id="1">
            <title xml:lang="x-jat" type="main">Japanese Title</title>
            <title xml:lang="en" type="official">English Title</title>
            <title xml:lang="fr" type="official">French Title</title>
        </anime>"""
        xml = etree.fromstring(xml_str.encode())
        
        # Request German (not available)
        anidb = AniDB(mock_requests, mock_cache, {"language": "de", "expiration": 60})
        anidb.titles_db.title_map = {}
        obj = AniDBObj(anidb, 1, xml)
        
        assert obj.official_title == "Japanese Title"  # Falls back to main_title


# AniDB Tests
class TestAniDB:
    """Tests for main AniDB class."""

    def test_init(self, mock_requests, mock_cache):
        """Test AniDB initialization."""
        anidb = AniDB(mock_requests, mock_cache, {
            "language": "en",
            "expiration": 30
        })
        
        assert anidb.language == "en"
        assert anidb.expiration == 30
        assert anidb.username == "kometa_admin"
        assert anidb.password == "kometa_is_cool"
        assert not anidb.is_authorized

    def test_init_with_defaults(self, mock_requests, mock_cache):
        """Test AniDB initialization with default values."""
        anidb = AniDB(mock_requests, mock_cache, {})
        
        assert anidb.language == "en"
        assert anidb.expiration == 60

    @patch('time.perf_counter')
    def test_request_rate_limiting(self, mock_time, mock_requests, mock_cache, temp_cache_dir):
        """Test that requests have minimal delay (0.1s)."""
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        # Mock time to simulate rapid requests
        mock_time.side_effect = [0, 0.05, 0.05, 0.2]  # Elapsed time checks
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<?xml version="1.0"?><anime id="1"><title type="main">Test</title></anime>'
        mock_requests.get.return_value = mock_response
        
        with patch('time.sleep') as mock_sleep, \
             patch('os.path.exists', return_value=False):
            anidb._request(api_params={'aid': 1}, cache_days=0)
        
        # Should have slept to enforce minimal rate limit
        assert mock_sleep.called

    def test_request_uses_cache(self, mock_requests, mock_cache, temp_cache_dir, sample_anime_xml):
        """Test that requests use cached files when available and fresh."""
        cache_file = os.path.join(temp_cache_dir, "config", "anidb_cache", "anime_1.xml")
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
        # Write cache file
        with open(cache_file, 'wb') as f:
            f.write(etree.tostring(sample_anime_xml))
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        # Mock file operations to use our temp cache file
        with patch('os.path.exists') as mock_exists, \
             patch('os.path.getmtime', return_value=datetime.now().timestamp()), \
             patch('time.perf_counter', return_value=0):
            
            # First call checks if file exists (for cache check)
            # Second call would be for makedirs if we were writing
            mock_exists.side_effect = [True, True]
            
            with patch('builtins.open', mock_open(read_data=etree.tostring(sample_anime_xml))):
                result = anidb._request(api_params={'aid': 1}, cache_days=7)
        
        # Should not make HTTP request when cache is fresh
        mock_requests.get.assert_not_called()
        
        # Should return parsed XML
        assert result is not None

    def test_request_handles_gzip(self, mock_requests, mock_cache, temp_cache_dir):
        """Test that gzip-compressed responses are decompressed."""
        xml_content = b'<?xml version="1.0"?><anime id="1"><title type="main">Test</title></anime>'
        compressed = gzip.compress(xml_content)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = compressed
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             patch('builtins.open', mock_open()):
            result = anidb._request(api_params={'aid': 1}, cache_days=0)
        
        assert result is not None
        assert result.get('id') == '1'

    def test_request_handles_403_banned(self, mock_requests, mock_cache):
        """Test that 403 errors raise appropriate exception."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             pytest.raises(Failed, match="403 Banned"):
            anidb._request(api_params={'aid': 1}, cache_days=0)

    def test_authorize_success(self, mock_requests, mock_cache, sample_anime_xml):
        """Test successful authorization."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_anime_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             patch('builtins.open', mock_open()):
            anidb.authorize(30)
        
        assert anidb.is_authorized
        assert anidb.expiration == 30

    def test_authorize_failure(self, mock_requests, mock_cache):
        """Test failed authorization."""
        mock_requests.get.side_effect = Exception("Connection error")
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             pytest.raises(Failed, match="Authorization Failed"):
            anidb.authorize(30)
        
        assert not anidb.is_authorized

    def test_popular(self, mock_requests, mock_cache, sample_popular_xml):
        """Test fetching popular anime."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_popular_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0):
            result = anidb._popular()
        
        assert result == [1, 99, 107]

    def test_relations(self, mock_requests, mock_cache, sample_anime_xml):
        """Test fetching related anime."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_anime_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             patch('builtins.open', mock_open()):
            result = anidb._relations(1)
        
        assert 17 in result
        assert 23 in result

    def test_validate_valid_id(self, mock_requests, mock_cache, sample_anime_xml):
        """Test validating a valid AniDB ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_anime_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             patch('builtins.open', mock_open()):
            result = anidb._validate(1)
        
        assert result == 1

    def test_validate_invalid_id(self, mock_requests, mock_cache):
        """Test validating an invalid AniDB ID."""
        mock_requests.get.side_effect = Exception("Not found")
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             pytest.raises(Failed, match="not found"):
            anidb._validate(99999)

    def test_get_anime_from_api(self, mock_requests, mock_cache, sample_anime_xml):
        """Test fetching anime from API."""
        mock_cache.query_anidb.return_value = (None, True)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_anime_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             patch('builtins.open', mock_open()):
            obj = anidb.get_anime(1)
        
        assert obj.anidb_id == 1
        assert obj.main_title == "Serial Experiments Lain"
        mock_cache.update_anidb.assert_called_once()

    def test_get_anime_from_cache(self, mock_requests, mock_cache):
        """Test fetching anime from cache."""
        cache_dict = {
            "main_title": "Cached Anime",
            "titles": json.dumps({"en": "Cached Anime"}),
            "studio": None,
            "rating": None,
            "average": None,
            "score": None,
            "released": None,
            "tags": "",
            "mal_id": None,
            "imdb_id": None,
            "tmdb_id": None,
            "tmdb_type": None
        }
        mock_cache.query_anidb.return_value = (cache_dict, False)
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        obj = anidb.get_anime(1)
        
        # Should not make HTTP request
        mock_requests.get.assert_not_called()
        assert obj.main_title == "Cached Anime"

    def test_get_anidb_ids_popular(self, mock_requests, mock_cache, sample_popular_xml):
        """Test getting IDs via anidb_popular method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_popular_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('time.perf_counter', return_value=0):
            result = anidb.get_anidb_ids("anidb_popular", 2)
        
        assert result == [1, 99]  # Limited to 2

    def test_get_anidb_ids_single_id(self, mock_requests, mock_cache):
        """Test getting IDs via anidb_id method."""
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        result = anidb.get_anidb_ids("anidb_id", 123)
        
        assert result == [123]

    def test_get_anidb_ids_relation(self, mock_requests, mock_cache, sample_anime_xml):
        """Test getting IDs via anidb_relation method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_anime_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('time.perf_counter', return_value=0), \
             patch('builtins.open', mock_open()):
            result = anidb.get_anidb_ids("anidb_relation", 1)
        
        assert 17 in result
        assert 23 in result

    def test_search_by_tags_single(self, mock_requests, mock_cache, sample_tag_search_xml):
        """Test searching anime by a single tag."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_tag_search_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0):
            result = anidb._search_by_tags("action")
        
        assert result == [1, 25, 42, 99]
        # Verify the request was made with correct parameters
        call_args = mock_requests.get.call_args
        assert "search/tags" in call_args[0][0]
        assert call_args[1]['params']['tags'] == "action"

    def test_search_by_tags_multiple(self, mock_requests, mock_cache, sample_tag_search_xml):
        """Test searching anime by multiple tags."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_tag_search_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0):
            result = anidb._search_by_tags(["action", "comedy"], min_weight=300)
        
        assert result == [1, 25, 42, 99]
        # Verify the request parameters
        call_args = mock_requests.get.call_args
        assert call_args[1]['params']['tags'] == "action,comedy"
        assert call_args[1]['params']['min_weight'] == 300

    def test_search_by_tags_with_auth(self, mock_requests, mock_cache, sample_tag_search_xml):
        """Test that tag search includes authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_tag_search_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0):
            result = anidb._search_by_tags("action")
        
        # Verify authentication credentials are included
        call_args = mock_requests.get.call_args
        assert call_args[1]['params']['username'] == "kometa_admin"
        assert call_args[1]['params']['password'] == "kometa_is_cool"

    def test_get_anidb_ids_tag_simple(self, mock_requests, mock_cache, sample_tag_search_xml):
        """Test getting IDs via anidb_tag method with simple string."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_tag_search_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0):
            result = anidb.get_anidb_ids("anidb_tag", "action")
        
        assert result == [1, 25, 42, 99]

    def test_get_anidb_ids_tag_with_dict(self, mock_requests, mock_cache, sample_tag_search_xml):
        """Test getting IDs via anidb_tag method with dict parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_tag_search_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0):
            result = anidb.get_anidb_ids("anidb_tag", {
                "tags": ["action", "comedy"],
                "min_weight": 400
            })
        
        assert result == [1, 25, 42, 99]
        # Verify parameters were passed correctly
        call_args = mock_requests.get.call_args
        assert call_args[1]['params']['min_weight'] == 400

    def test_request_uses_new_endpoint_structure(self, mock_requests, mock_cache, sample_anime_xml):
        """Test that requests use the new REST-style endpoint structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_anime_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             patch('builtins.open', mock_open()):
            anidb._request(api_params={'aid': 1}, cache_days=0)
        
        # Verify URL structure
        call_args = mock_requests.get.call_args
        assert "utilities.kometa.wiki/anidb-service/anime/1" in call_args[0][0]

    def test_request_includes_hardcoded_auth(self, mock_requests, mock_cache, sample_anime_xml):
        """Test that all requests include hardcoded authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_anime_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             patch('builtins.open', mock_open()):
            anidb._request(api_params={'aid': 1}, cache_days=0)
        
        # Verify auth params are included
        call_args = mock_requests.get.call_args
        assert call_args[1]['params']['username'] == "kometa_admin"
        assert call_args[1]['params']['password'] == "kometa_is_cool"


# Integration Tests
class TestAniDBIntegration:
    """Integration tests for complete workflows."""

    def test_full_workflow_with_caching(self, mock_requests, mock_cache, temp_cache_dir, sample_anime_xml):
        """Test complete workflow with file caching."""
        cache_file = os.path.join(temp_cache_dir, "config", "anidb_cache", "anime_1.xml")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = etree.tostring(sample_anime_xml)
        mock_requests.get.return_value = mock_response
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        # First request - should hit API
        with patch('os.path.exists', side_effect=[False, True]), \
             patch('time.perf_counter', return_value=0), \
             patch('os.makedirs'), \
             patch('builtins.open', mock_open()):
            obj1 = anidb.get_anime(1)
        
        assert mock_requests.get.called
        assert obj1.main_title == "Serial Experiments Lain"

    def test_error_handling_chain(self, mock_requests, mock_cache):
        """Test error handling through the request chain."""
        mock_requests.get.side_effect = Exception("Network error")
        
        anidb = AniDB(mock_requests, mock_cache, {"language": "en", "expiration": 60})
        
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('time.perf_counter', return_value=0), \
             pytest.raises(Exception, match="Network error"):
            anidb.get_anime(1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
