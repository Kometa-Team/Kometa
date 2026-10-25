from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from tmdbapis import TMDbException

from modules.tmdb import TMDb
from modules.util import Failed


def make_exporter(monkeypatch, authorization=None, read_token=None):
    from modules import tmdb as tmdb_module

    logger = MagicMock()
    monkeypatch.setattr(tmdb_module, "logger", logger)
    api = MagicMock()
    monkeypatch.setattr(tmdb_module, "API4", MagicMock(return_value=api))
    yaml = SimpleNamespace(data={"tmdb": {"apikey": "v3"}}, save=MagicMock())
    settings = yaml.data["tmdb"]
    if authorization:
        settings["authorization"] = authorization
    if read_token:
        settings["access_token"] = read_token
    requests = SimpleNamespace(session=MagicMock(), file_yaml=MagicMock(return_value=yaml))
    config = SimpleNamespace(data={"tmdb": settings}, read_only=False, config_path="config.yml", Requests=requests)
    exporter = TMDb.__new__(TMDb)
    exporter.config = config
    exporter.requests = requests
    exporter.language = "en"
    return exporter, api, yaml, logger


def test_tmdb_authorization_is_lazy_and_saved(monkeypatch):
    exporter, api, yaml, logger = make_exporter(monkeypatch, read_token="app-token")
    api.auth_create_request_token.return_value = {"request_token": "request-token"}
    api.auth_create_access_token.side_effect = [TMDbException("(422 [Unprocessable Entity]) {'status_code': 41, 'status_message': 'This request token has not been approved'}"), {"access_token": "user-token", "account_id": "account-id"}]
    sleep = MagicMock()
    monkeypatch.setattr("modules.tmdb.time.sleep", sleep)

    assert exporter._export_api() == (api, "account-id")
    assert yaml.data["tmdb"]["authorization"] == {"access_token": "user-token", "account_id": "account-id"}
    yaml.save.assert_called_once()
    assert exporter._export_api() == (api, "account-id")
    api.auth_create_request_token.assert_called_once()
    assert api.auth_create_access_token.call_count == 2
    sleep.assert_called_once_with(5)
    assert any("https://www.themoviedb.org/auth/access?request_token=request-token" in str(call) for call in logger.info.call_args_list)


def test_tmdb_missing_read_token_gives_noninteractive_setup_instructions(monkeypatch):
    exporter, api, yaml, _ = make_exporter(monkeypatch)
    with pytest.raises(Failed, match="tmdb.access_token in config.yml"):
        exporter._export_api()
    api.auth_create_request_token.assert_not_called()
    yaml.save.assert_not_called()


def test_tmdb_sync_only_writes_difference(monkeypatch):
    exporter, api, _, logger = make_exporter(monkeypatch, authorization={"access_token": "user-token", "account_id": "account-id"})
    api.account_get_lists.return_value = {"results": [{"id": 42, "name": "Marvel"}], "total_pages": 1}
    api.list_get_list.return_value = {"results": [{"media_type": "movie", "id": 1}, {"media_type": "movie", "id": 2}], "total_pages": 1}
    api.list_add_items.return_value = {"results": [{"success": True}]}
    api.list_remove_items.return_value = {"results": [{"success": True}]}

    exporter.sync_list("Marvel", [(2, "tmdb"), (3, "tmdb")], "sync")

    api.list_remove_items.assert_called_once_with(42, [{"media_type": "movie", "media_id": 1}])
    api.list_add_items.assert_called_once_with(42, [{"media_type": "movie", "media_id": 3}])
    assert any("https://www.themoviedb.org/list/42" in str(call) for call in logger.info.call_args_list)


def test_tmdb_sync_empty_removes_all_and_append_keeps_existing(monkeypatch):
    exporter, api, _, _ = make_exporter(monkeypatch, authorization={"access_token": "user-token", "account_id": "account-id"})
    api.account_get_lists.return_value = {"results": [{"id": 42, "name": "Marvel"}], "total_pages": 1}
    api.list_get_list.return_value = {"results": [{"media_type": "tv", "id": 2}], "total_pages": 1}
    api.list_remove_items.return_value = {"results": [{"success": True}]}

    exporter.sync_list(42, [], "sync")
    api.list_remove_items.assert_called_once_with(42, [{"media_type": "tv", "media_id": 2}])
    api.list_remove_items.reset_mock()
    exporter.sync_list(42, [], "append")
    api.list_remove_items.assert_not_called()


def test_tmdb_rejects_unowned_numeric_list(monkeypatch):
    exporter, api, _, _ = make_exporter(monkeypatch, authorization={"access_token": "user-token", "account_id": "account-id"})
    api.account_get_lists.return_value = {"results": [], "total_pages": 1}
    with pytest.raises(Failed, match="does not belong"):
        exporter.sync_list(42, [], "sync")
    api.list_create_list.assert_not_called()
