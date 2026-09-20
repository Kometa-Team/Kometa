from modules.util import remove_trakt


def test_legacy_trakt_configuration_is_removed():
    data, found = remove_trakt({"collections": {"Legacy": {"trakt_list": "https://trakt.tv/users/example/lists/legacy"}}, "trakt": {"client_id": "old-key"}})

    assert found is True
    assert data == {}
