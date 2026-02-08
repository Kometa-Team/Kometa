"""
Pytest configuration and shared fixtures for Kometa tests.

This file is automatically loaded by pytest and provides:
- Shared fixtures used across multiple test files
- Test configuration
- Common test utilities
"""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path

# Add the project root to sys.path so modules can be imported
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock the logger before any modules that use it are imported
from unittest.mock import Mock, patch
import modules.util as util
if util.logger is None:
    util.logger = Mock()


@pytest.fixture(autouse=True)
def mock_anidb_titles_for_most_tests(request):
    """
    Automatically mock AniDBTitles loading for all tests except those testing AniDBTitles itself.
    """
    # Skip mocking for tests that are specifically testing AniDBTitles
    if 'TestAniDBTitles' in str(request.node.nodeid):
        yield
        return
    
    # For all other tests, mock the _load method
    with patch('modules.anidb.AniDBTitles._load', return_value=None):
        yield


@pytest.fixture(scope="session")
def project_root_dir():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir():
    """Create a temporary directory that is cleaned up after the test."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def temp_config_dir(temp_dir):
    """Create a temporary config directory structure."""
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    # Create subdirectories that modules might need
    os.makedirs(os.path.join(config_dir, "anidb_cache"), exist_ok=True)
    
    return config_dir


@pytest.fixture
def clean_environment(monkeypatch):
    """Provide a clean environment for testing."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Clear test-related env vars
    for key in list(os.environ.keys()):
        if key.startswith('TEST_'):
            monkeypatch.delenv(key, raising=False)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset module state between tests to avoid interference."""
    yield
    # Add cleanup code here if needed for specific modules


# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "network: marks tests that require network access"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test items during collection."""
    # Add markers to tests based on their location or name
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests (tests that take > 1 second typically)
        if any(keyword in item.nodeid.lower() for keyword in ["slow", "large", "full"]):
            item.add_marker(pytest.mark.slow)
        
        # Mark network tests
        if any(keyword in item.nodeid.lower() for keyword in ["api", "request", "download"]):
            item.add_marker(pytest.mark.network)


# Utility functions for tests
class TestHelpers:
    """Helper utilities for tests."""
    
    @staticmethod
    def create_mock_response(status_code=200, content=b"", headers=None):
        """Create a mock HTTP response object."""
        from unittest.mock import Mock
        
        response = Mock()
        response.status_code = status_code
        response.content = content
        response.headers = headers or {}
        response.text = content.decode() if isinstance(content, bytes) else content
        
        return response
    
    @staticmethod
    def create_sample_xml(root_tag, attributes=None, children=None):
        """Create a simple XML element for testing."""
        from lxml import etree
        
        root = etree.Element(root_tag, **(attributes or {}))
        
        if children:
            for child_tag, child_text, child_attrs in children:
                child = etree.SubElement(root, child_tag, **(child_attrs or {}))
                if child_text:
                    child.text = child_text
        
        return root


@pytest.fixture
def test_helpers():
    """Provide test helper utilities."""
    return TestHelpers()
