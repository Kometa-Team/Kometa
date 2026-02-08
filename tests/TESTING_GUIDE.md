# Testing Quick Reference for Kometa

## Installation

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Or with the project in development mode
pip install -e ".[dev]"
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_anidb.py

# Run specific test class
pytest tests/test_anidb.py::TestAniDB

# Run specific test function
pytest tests/test_anidb.py::TestAniDB::test_init

# Run tests matching a pattern
pytest -k "test_parse"
```

### With Coverage

```bash
# Basic coverage
pytest --cov=modules

# Coverage with HTML report
pytest --cov=modules --cov-report=html

# Coverage for specific module
pytest --cov=modules.anidb tests/test_anidb.py
```

### Using Markers

```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run tests without network requirements
pytest -m "not network"
```

### Output Options

```bash
# Verbose output
pytest -v

# Very verbose (show all details)
pytest -vv

# Show local variables on failure
pytest -l

# Stop on first failure
pytest -x

# Show summary of all test types
pytest -ra
```

## Test Structure

### Test File Naming
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test

```python
import pytest
from modules.anidb import AniDB
from modules.util import Failed

class TestAniDB:
    """Test suite for AniDB class."""
    
    def test_init(self, mock_requests, mock_cache):
        """Test AniDB initialization."""
        anidb = AniDB(mock_requests, mock_cache, {
            "language": "en",
            "expiration": 30
        })
        
        assert anidb.language == "en"
        assert anidb.expiration == 30
    
    def test_invalid_id(self, mock_requests, mock_cache):
        """Test that invalid IDs raise Failed exception."""
        anidb = AniDB(mock_requests, mock_cache, {})
        
        with pytest.raises(Failed, match="not found"):
            anidb._validate(99999)
```

## Available Fixtures

### Built-in Fixtures
- `temp_cache_dir` - Temporary cache directory
- `mock_requests` - Mocked requests object
- `mock_cache` - Mocked cache object
- `sample_anime_xml` - Sample anime XML data
- `sample_titles_xml` - Sample titles XML data
- `test_helpers` - Utility helper class

### Pytest Fixtures
- `tmp_path` - Temporary directory (pathlib.Path)
- `monkeypatch` - Modify objects/env vars
- `capsys` - Capture stdout/stderr
- `caplog` - Capture log messages

## Mocking Examples

### Mock HTTP Response

```python
from unittest.mock import Mock

def test_api_call(mock_requests):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'<xml>data</xml>'
    mock_requests.get.return_value = mock_response
    
    # Your test code here
```

### Mock File System

```python
from unittest.mock import patch, mock_open

def test_file_read():
    with patch('builtins.open', mock_open(read_data='file content')):
        # Your test code here
        pass
```

### Mock Time

```python
from unittest.mock import patch

def test_time_dependent():
    with patch('time.time', return_value=1234567890):
        # Your test code here
        pass
```

## Assertions

```python
# Equality
assert value == expected

# Identity
assert value is None

# Membership
assert item in collection

# Exceptions
with pytest.raises(ValueError, match="error message"):
    function_that_raises()

# Approximate equality (for floats)
assert value == pytest.approx(3.14159, rel=1e-5)

# Multiple assertions with context
with pytest.raises(Failed) as exc_info:
    risky_function()
assert "specific error" in str(exc_info.value)
```

## Debugging Tests

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb

# Show print statements
pytest -s

# Show locals on failure
pytest -l --tb=long
```

## CI/CD Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

See `.github/workflows/tests.yml` for CI configuration.

## Coverage Goals

- Overall coverage target: 80%+
- Critical modules (anidb, cache, etc.): 90%+
- View coverage report: `htmlcov/index.html`

## Tips

1. **Write tests first**: Consider TDD approach for new features
2. **One assertion per test**: Makes failures easier to diagnose
3. **Use descriptive names**: Test names should describe what's being tested
4. **Test edge cases**: Don't just test the happy path
5. **Keep tests fast**: Mock external dependencies (APIs, files, etc.)
6. **Isolate tests**: Each test should be independent
7. **Use fixtures**: Share common setup across tests
8. **Document complex tests**: Add docstrings explaining what's being tested

## Common Issues

### Import Errors
```bash
# Make sure you're in the project root
cd /path/to/Kometa

# Or set PYTHONPATH
export PYTHONPATH=/path/to/Kometa:$PYTHONPATH
```

### Fixture Not Found
- Check fixture is in `conftest.py` or imported
- Verify fixture scope matches usage

### Tests Pass Locally but Fail in CI
- Check for hard-coded paths
- Verify all dependencies are in requirements
- Look for OS-specific code

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
