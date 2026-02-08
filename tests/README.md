# Kometa Tests

This directory contains the test suite for the Kometa project.

## Setup

Install test dependencies:

```bash
pip install pytest pytest-cov pytest-mock
```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests for a specific module:
```bash
pytest tests/test_anidb.py
```

Run tests with coverage:
```bash
pytest --cov=modules --cov-report=html --cov-report=term
```

Run only unit tests:
```bash
pytest -m unit
```

Run with verbose output:
```bash
pytest -v
```

## Test Structure

- `test_anidb.py` - Tests for the AniDB module
  - `TestAniDBTitles` - Tests for the title database functionality
  - `TestAniDBObj` - Tests for anime object data parsing
  - `TestAniDB` - Tests for the main AniDB class
  - `TestAniDBIntegration` - Integration tests

## Writing Tests

Tests use pytest with the following fixtures:
- `temp_cache_dir` - Temporary directory for cache files
- `mock_requests` - Mocked requests object
- `mock_cache` - Mocked cache object
- `sample_anime_xml` - Sample XML response data
- `sample_titles_xml` - Sample title database XML
- `sample_popular_xml` - Sample popular feed XML

Example test:
```python
def test_example(mock_requests, mock_cache):
    """Test description."""
    anidb = AniDB(mock_requests, mock_cache, {"language": "en"})
    result = anidb.some_method()
    assert result == expected_value
```

## Coverage

To generate a coverage report:
```bash
pytest --cov=modules --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

## CI/CD

Tests should be run in CI/CD pipelines before merging pull requests.
