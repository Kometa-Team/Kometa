import pytest

from modules.util import remove_trakt


def test_legacy_trakt_configuration_is_removed():
    data, found = remove_trakt({"collections": {"Legacy": {"trakt_list": "https://trakt.tv/users/example/lists/legacy"}}, "trakt": {"client_id": "old-key"}})

    assert found is True
    assert data == {}


@pytest.mark.parametrize(
    "key",
    [
        "trakt_chart",
        "trakt_userlist",
        "trakt_list",
        "trakt_list_details",
        "trakt_watchlist",
        "trakt_collection",
        "trakt_trending",
        "trakt_popular",
        "trakt_boxoffice",
        "trakt_collected_daily",
        "trakt_recommendations",
        "trakt_recommended_personal",
        "trakt_watched_all",
        "sync_to_trakt_list",
        "sync_missing_to_trakt_list",
        "TRAKT_LIST",  # key matching is case-insensitive
    ],
)
def test_known_trakt_attribute_keys_are_removed(key):
    data, found = remove_trakt({"collections": {"Example": {key: "value", "summary": "keep me"}}})

    assert found is True
    assert key not in data["collections"]["Example"]
    assert data["collections"]["Example"]["summary"] == "keep me"


def test_mdblist_url_mentioning_trakt_is_not_removed():
    # Regression: an mdblist_list URL whose slug happens to contain "trakt" (because the
    # underlying curated list is *about* Trakt data, fetched entirely through MDBList's own
    # API) must survive - this isn't Kometa's removed Trakt integration.
    collection = {
        "summary": "Popular shows on IMDb, Trakt and TMDb over the past few months.",
        "mdblist_list": "https://mdblist.com/lists/k0meta/trakt-popular",
    }
    data, found = remove_trakt({"collections": {"Popular": collection}})

    assert found is False
    assert data == {"collections": {"Popular": collection}}


def test_collection_named_after_trakt_is_not_removed():
    # Regression: a collection (or any other) name that merely mentions "trakt" must not be
    # treated as a Trakt attribute key and deleted wholesale.
    collection = {"tmdb_popular": 100}
    data, found = remove_trakt({"collections": {"Trakt Favorites": collection}})

    assert found is False
    assert data == {"collections": {"Trakt Favorites": collection}}
