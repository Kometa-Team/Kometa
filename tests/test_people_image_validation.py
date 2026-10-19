"""Missing People-Images artwork must leave other poster candidates usable."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from requests.exceptions import ReadTimeout

from modules.util import Failed
from tests.factories import FakeImageResponse, make_builder, make_image_requests, make_plex

PEOPLE_URL = "https://raw.githubusercontent.com/Kometa-Team/People-Images-bw/master/G/Images/Gil%20Netter.jpg"
TMDB_URL = "https://image.tmdb.org/t/p/original/person.jpg"


@pytest.mark.parametrize("status, expected_attribute, expected_location", [(404, "tmdb_person", TMDB_URL), (200, "url_poster", PEOPLE_URL)])
def test_person_poster_selection_uses_validated_candidates(monkeypatch, status, expected_attribute, expected_location):
    requests, mock_get, mock_head = make_image_requests()
    mock_head.return_value = FakeImageResponse(status_code=status)
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
    mock_head.return_value = FakeImageResponse(status_code=404)
    mock_get.return_value = FakeImageResponse()
    for _ in range(2):
        with pytest.raises(Failed, match="Not Found on Image URL"):
            requests.get_image(PEOPLE_URL, validate_only=True)
    assert mock_head.call_count == 1
    assert requests.get_image(PEOPLE_URL) is mock_get.return_value
    mock_get.assert_called_once_with(PEOPLE_URL, header=True)

    next_run, _, next_head = make_image_requests()
    next_head.return_value = FakeImageResponse()
    assert next_run.get_image(PEOPLE_URL, validate_only=True) is next_head.return_value
    next_head.assert_called_once_with(PEOPLE_URL, header=True)


@pytest.mark.parametrize("status", [403, 429, 500, 502, 503, 504])
def test_temporary_or_access_failure_is_not_cached_as_missing(status):
    requests, _, mock_head = make_image_requests()
    mock_head.side_effect = [FakeImageResponse(status_code=status), FakeImageResponse()]
    with pytest.raises(Failed, match=str(status)):
        requests.get_image(PEOPLE_URL, validate_only=True)
    assert requests.get_image(PEOPLE_URL, validate_only=True).status_code == 200
    assert mock_head.call_count == 2


def test_network_failure_is_not_cached_as_missing():
    requests, _, mock_head = make_image_requests()
    mock_head.side_effect = [ReadTimeout("timeout"), FakeImageResponse()]
    with pytest.raises(Failed, match="Unable to reach Image URL"):
        requests.get_image(PEOPLE_URL, validate_only=True)
    assert requests.get_image(PEOPLE_URL, validate_only=True).status_code == 200
    assert mock_head.call_count == 2


def test_session_validation_caches_missing_response():
    requests, _, mock_head = make_image_requests()
    session = MagicMock()
    session.head.return_value = FakeImageResponse(status_code=404)
    for _ in range(2):
        with pytest.raises(Failed, match="Not Found on Image URL"):
            requests.get_image(PEOPLE_URL, session=session, validate_only=True)
    assert session.head.call_count == 1
    mock_head.assert_not_called()


@pytest.mark.parametrize("failure", ["rate_limit", "server_error", "timeout"])
def test_temporary_validation_failure_is_reported_distinctly_and_can_recover(monkeypatch, failure):
    from requests import Response

    from modules.request import Requests

    requests, _, _ = make_image_requests()
    requests.head = Requests.head.__get__(requests, Requests)
    requests.session = MagicMock()
    monkeypatch.setattr(Requests.head.retry, "sleep", lambda seconds: None)
    response = Response()
    response.status_code = 429 if failure == "rate_limit" else 503
    response.url = PEOPLE_URL
    response.headers["Retry-After"] = "0"
    success = Response()
    success.status_code = 200
    success.headers["Content-Type"] = "image/jpeg"
    attempts = 1 if failure == "server_error" else 6
    error = ReadTimeout("network timeout") if failure == "timeout" else response
    requests.session.head.side_effect = [error] * attempts + [success]
    test_logger = MagicMock()
    monkeypatch.setattr("modules.builder.logger", test_logger)
    library = make_plex(config=SimpleNamespace(Requests=requests))
    monkeypatch.setattr("modules.library.logger", test_logger)

    for expected_attribute in ["tmdb_person", "url_poster"]:
        builder = make_builder(config=SimpleNamespace(Requests=requests), posters={"tmdb_person": TMDB_URL})
        builder._poster("url_poster", PEOPLE_URL)
        selected = library.pick_image("Gil Netter (Producer)", builder.posters, False, False, None)
        assert selected.attribute == expected_attribute

    assert requests.session.head.call_count == attempts + 1
    test_logger.warning.assert_called_once()
    message = test_logger.warning.call_args.args[0]
    assert "Poster validation failed" in message
    assert "No Poster Found" not in message
    assert "Trying another available poster source" in message
    assert {"rate_limit": "Too many requests", "server_error": "503", "timeout": "Unable to reach Image URL"}[failure] in message
    test_logger.stacktrace.assert_not_called()
