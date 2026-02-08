# AniDB Test Updates

This document summarizes the test updates made to support the new AniDB replacement API.

## Updated Tests

### Authentication Tests
- **Updated `test_init`**: Now verifies hardcoded credentials (`kometa_admin` / `kometa_is_cool`)
- **Removed `test_verify_user_success`**: No longer needed since authentication is hardcoded
- **Removed `test_verify_user_no_mature_access`**: No longer needed since authentication is hardcoded

### Rate Limiting Tests
- **Updated `test_request_rate_limiting`**: Changed from 4.1s to 0.1s minimal delay to reflect new API

### Request Tests
- **Updated multiple request tests**: Changed from old `request=anime&aid=X` format to new REST-style `/anime/{aid}` endpoints
- All tests now properly mock the new endpoint structure

### Authorization Tests
- **Updated `test_authorize_success`**: Removed client/clientver parameters (no longer needed)
- **Updated `test_authorize_failure`**: Removed client/clientver parameters (no longer needed)

## New Tests Added

### Tag Search Tests

1. **`test_search_by_tags_single`**
   - Tests searching anime by a single tag
   - Verifies correct endpoint usage (`/search/tags`)
   - Validates result parsing

2. **`test_search_by_tags_multiple`**
   - Tests searching with multiple tags and min_weight parameter
   - Verifies tags are comma-separated in request
   - Validates min_weight parameter is included

3. **`test_search_by_tags_with_auth`**
   - Verifies that tag search requests include hardcoded authentication credentials
   - Ensures `username` and `password` params are present

4. **`test_get_anidb_ids_tag_simple`**
   - Tests the `anidb_tag` builder method with a simple string tag
   - Verifies integration with `get_anidb_ids`

5. **`test_get_anidb_ids_tag_with_dict`**
   - Tests the `anidb_tag` builder method with dict parameters
   - Validates both `tags` and `min_weight` are properly passed

### API Structure Tests

6. **`test_request_uses_new_endpoint_structure`**
   - Verifies requests use the new REST-style URL structure
   - Checks that URLs contain `utilities.kometa.wiki/anidb-service/anime/{aid}`

7. **`test_request_includes_hardcoded_auth`**
   - Ensures all API requests include hardcoded authentication
   - Verifies credentials are properly added to request parameters

## New Fixtures

### `sample_tag_search_xml`
Sample XML response for tag search results:
```xml
<search>
    <anime aid="1"/>
    <anime aid="25"/>
    <anime aid="42"/>
    <anime aid="99"/>
</search>
```

## Running the Tests

```bash
# Run all AniDB tests
pytest tests/test_anidb.py -v

# Run only tag search tests
pytest tests/test_anidb.py -k "tag" -v

# Run with coverage
pytest tests/test_anidb.py --cov=modules.anidb --cov-report=term
```

## Test Coverage

The updated test suite covers:
- ✅ Hardcoded authentication
- ✅ New REST-style endpoints
- ✅ Tag search functionality
- ✅ Reduced rate limiting (0.1s vs 4.1s)
- ✅ Backward compatibility with existing builders
- ✅ Error handling
- ✅ Caching behavior
- ✅ XML parsing from new API responses

## Expected Results

All tests should pass with the new API implementation. The test suite validates:
- API connectivity to `utilities.kometa.wiki/anidb-service`
- Proper authentication with hardcoded credentials
- Tag search endpoint functionality
- Existing builder methods (popular, id, relation)
- File caching and cache expiration
- Error handling and edge cases
