"""Missing People-Images artwork must leave other poster candidates usable."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from requests.exceptions import ReadTimeout

from modules.util import Failed
from tests.test_builder import make_builder
from tests.test_plex import make_plex
from tests.test_request import _FakeImageResponse, make_image_requests

PEOPLE_URL = "https://raw.githubusercontent.com/Kometa-Team/People-Images-bw/master/G/Images/Gil%20Netter.jpg"
TMDB_URL = "https://image.tmdb.org/t/p/original/person.jpg"


@pytest.mark.parametrize("status, expected_attribute, expected_location", [(404, "tmdb_person", TMDB_URL), (200, "url_poster", PEOPLE_URL)])
def test_person_poster_selection_uses_validated_candidates(monkeypatch, status, expected_attribute, expected_location):
    requests, mock_get, mock_head = make_image_requests()
    mock_head.return_value = _FakeImageResponse(status_code=status)
    test_logger = MagicMock()
    monkeypatch.setattr("modules.builder.logger", test_logger)
    library = make_plex(config=SimpleNamespace(Requests=requests))
    monkeypatch.setattr("modules.library.logger", test_logger)

    # Multiple definitions sharing the same person image make only one HEAD request.
    for _ in range(2):
        builder = make_builder(config=SimpleNamespace(Requests=requests), posters={"tmdb_person": TMDB_URL})
        builder._poster("url_poster", PEOPLE_URL)
        image = library.pick_image("Gil Netter (Producer)", builder.posters, False, False, None)
        assert image.attribute == expected_attribute
        assert image.location == expected_location
        assert ("url_poster" in builder.posters) is (status == 200)

    mock_head.assert_called_once_with(PEOPLE_URL, header=True)
    mock_get.assert_not_called()
    test_logger.stacktrace.assert_not_called()
    if status == 404:
        assert test_logger.warning.call_count == 2
        assert test_logger.warning.call_args.args[0] == f"Collection Warning: No Poster Found at {PEOPLE_URL}"
    else:
        test_logger.warning.assert_not_called()


def test_cached_missing_validation_does_not_poison_downloads_or_later_runs():
    requests, mock_get, mock_head = make_image_requests()
    mock_head.return_value = _FakeImageResponse(status_code=404)
    mock_get.return_value = _FakeImageResponse()
    for _ in range(2):
        with pytest.raises(Failed, match="Not Found on Image URL"):
            requests.get_image(PEOPLE_URL, validate_only=True)
    assert mock_head.call_count == 1
    assert requests.get_image(PEOPLE_URL) is mock_get.return_value
    mock_get.assert_called_once_with(PEOPLE_URL, header=True)

    next_run, _, next_head = make_image_requests()
    next_head.return_value = _FakeImageResponse()
    assert next_run.get_image(PEOPLE_URL, validate_only=True) is next_head.return_value
    next_head.assert_called_once_with(PEOPLE_URL, header=True)


@pytest.mark.parametrize("status", [403, 429, 500, 502, 503, 504])
def test_temporary_or_access_failure_is_not_cached_as_missing(status):
    requests, _, mock_head = make_image_requests()
    mock_head.side_effect = [_FakeImageResponse(status_code=status), _FakeImageResponse()]
    with pytest.raises(Failed, match=str(status)):
        requests.get_image(PEOPLE_URL, validate_only=True)
    assert requests.get_image(PEOPLE_URL, validate_only=True).status_code == 200
    assert mock_head.call_count == 2


def test_network_failure_is_not_cached_as_missing():
    requests, _, mock_head = make_image_requests()
    mock_head.side_effect = [ReadTimeout("timeout"), _FakeImageResponse()]
    with pytest.raises(Failed, match="Unable to reach Image URL"):
        requests.get_image(PEOPLE_URL, validate_only=True)
    assert requests.get_image(PEOPLE_URL, validate_only=True).status_code == 200
    assert mock_head.call_count == 2


def test_session_validation_caches_missing_response():
    requests, _, mock_head = make_image_requests()
    session = MagicMock()
    session.head.return_value = _FakeImageResponse(status_code=404)
    for _ in range(2):
        with pytest.raises(Failed, match="Not Found on Image URL"):
            requests.get_image(PEOPLE_URL, session=session, validate_only=True)
    assert session.head.call_count == 1
    mock_head.assert_not_called()
