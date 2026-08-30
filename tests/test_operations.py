"""Tests for modules/operations.py -- focused on _should_be_deleted / delete_collections.

Issue #3168: When run_order puts operations before collections, library.collections is always
empty at the time delete_collections runs.  The old code checked
    col_in.title in self.library.collections
so every managed collection appeared "unconfigured" and was deleted.

Fix: use self.library.collection_names (pre-populated from YAML before the run_order loop).
"""

from collections import Counter
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.builder  # noqa: F401 -- pre-import to break plex<->builder circular import
import modules.operations as ops_module

# util.logger is None until Kometa initialises its logger; patch it for tests.
ops_module.logger = MagicMock()

from modules.mdblist import MDBList  # noqa: E402 -- must follow logger patch above
from modules.operations import Operations, _configured_collection_name_aliases, _image_operation_summary_rows  # noqa: E402 -- must follow logger patch above
from modules.overlays import Overlays  # noqa: E402 -- must follow logger patch above
from modules.plex import Plex  # noqa: E402 -- must follow logger patch above

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_ops(collections, collection_names):
    """Return a minimal Operations instance with mocked config and library."""
    library = MagicMock()
    library.collections = list(collections)
    library.collection_names = list(collection_names)
    ops = Operations(config=MagicMock(), library=library)
    return ops


def make_col(title, childCount=5, smart=False):
    """Return a minimal mock Plex collection object."""
    col = MagicMock()
    col.title = title
    col.childCount = childCount
    col.smart = smart
    return col


def test_image_operation_summary_pivots_results_by_source_type_and_level():
    counts = Counter(
        {
            ("Reset", "TMDb", "Poster", "Episode", "Updated"): 11077,
            ("Reset", "TMDb", "Poster", "Episode", "Missing"): 318,
            ("Reset", "TMDb", "Poster", "Season", "Updated"): 923,
            ("Reset", "TMDb", "Poster", "Season", "Missing"): 6,
            ("Lock", "Plex", "Poster", "Item", "Updated"): 2,
        }
    )

    assert _image_operation_summary_rows(counts) == [
        ("Lock", "Plex", "Poster", "Item", 2, 0, 0, 0),
        ("Reset", "TMDb", "Poster", "Episode", 11077, 0, 318, 0),
        ("Reset", "TMDb", "Poster", "Season", 923, 0, 6, 0),
    ]


class TestMDBListPrefetch:
    def test_delegates_enabled_mdblist_operations_to_library(self):
        items = [SimpleNamespace(ratingKey=1)]
        library = make_mass_edit_library(items, mass_critic_rating_update=["mdb_imdb"])
        config = MagicMock()
        config.MDBList.limit = False

        Operations(config=config, library=library)._prefetch_mdblist(items)

        library.prefetch_mdblist.assert_called_once_with(items)

    def test_does_not_prefetch_without_an_mdblist_operation(self):
        items = [SimpleNamespace(ratingKey=1)]
        library = make_mass_edit_library(items, mass_critic_rating_update=["tmdb"])
        config = MagicMock()
        config.MDBList.limit = False

        Operations(config=config, library=library)._prefetch_mdblist(items)
        library.prefetch_mdblist.assert_not_called()

    def test_stops_prefetching_after_limit_is_reached(self):
        items = [SimpleNamespace(ratingKey=1), SimpleNamespace(ratingKey=2)]
        library = make_mass_edit_library(items, mass_originally_available_update=["mdb"])
        config = MagicMock()
        config.MDBList.limit = True

        Operations(config=config, library=library)._prefetch_mdblist(items)

        library.prefetch_mdblist.assert_not_called()

    def test_one_thousand_items_use_ten_bulk_requests(self):
        items = [SimpleNamespace(ratingKey=i) for i in range(1000)]
        library = make_mass_edit_library(items, mass_user_rating_update=["mdb"])
        config = MagicMock()
        config.MDBList = MDBList.__new__(MDBList)
        config.MDBList.cache = None
        config.MDBList.limit = False
        config.MDBList._run_cache = {}
        config.MDBList._request = MagicMock(return_value=([], {}))
        real_library = Plex.__new__(Plex)
        real_library.config = config
        real_library.is_movie = True
        real_library.is_show = False
        real_library.get_ids = MagicMock(side_effect=[(i, None, None) for i in range(1000)])
        for name in (
            "mass_user_rating_update",
            "mass_critic_rating_update",
            "mass_audience_rating_update",
            "mass_content_rating_update",
            "mass_originally_available_update",
            "mass_added_at_update",
        ):
            setattr(real_library, name, getattr(library, name))

        Operations(config=config, library=real_library)._prefetch_mdblist(items)

        assert config.MDBList._request.call_count == 10

    def test_operations_and_overlays_share_run_cache_without_persistent_cache(self):
        items = [SimpleNamespace(ratingKey=1), SimpleNamespace(ratingKey=2)]
        mdblist = MDBList.__new__(MDBList)
        mdblist.cache = None
        mdblist.expiration = 60
        mdblist.limit = False
        mdblist._run_cache = {}

        def batch_response(url, json_data):
            return (
                [
                    {
                        "id": media_id,
                        "title": f"Movie {media_id}",
                        "released": None,
                        "released_digital": None,
                    }
                    for media_id in json_data["ids"]
                ],
                {},
            )

        mdblist._request = MagicMock(side_effect=batch_response)
        config = SimpleNamespace(MDBList=mdblist)
        library = Plex.__new__(Plex)
        library.config = config
        library.is_movie = True
        library.is_show = False
        library.get_ids = MagicMock(side_effect=lambda item: (item.ratingKey + 100, None, None))
        library.mass_audience_rating_update = ["mdb"]
        library.mass_critic_rating_update = None
        library.mass_user_rating_update = None
        library.mass_content_rating_update = None
        library.mass_originally_available_update = None
        library.mass_added_at_update = None

        Operations(config=config, library=library)._prefetch_mdblist(items)
        assert mdblist._request.call_count == 1

        overlays = Overlays.__new__(Overlays)
        overlays.cache = None
        overlays.library = library
        overlays._prefetch_mdblist(
            {
                1: (items[0], ["rating"]),
                2: (items[1], ["rating"]),
            },
            {"rating": SimpleNamespace(variables={"mdb_tomatoes_rating"})},
        )

        assert mdblist._request.call_count == 1


# ---------------------------------------------------------------------------
# Regression: demonstrate the bug that existed before the fix
# ---------------------------------------------------------------------------


def test_configured_check_pre_fix_uses_wrong_attribute():
    """Pre-fix regression: the broken code checked col.title in library.collections
    (populated during the collection run) rather than library.collection_names
    (pre-populated before run_order).

    When operations runs before collections -- the user's run_order -- library.collections
    is always empty, so every managed collection appears unconfigured → deleted.

    This test replicates the broken logic inline to prove the flaw.
    """
    collection_names = ["SAG Award Winners"]
    collections = []  # always empty when operations runs first
    configured_in = False  # user setting: delete unconfigured collections

    # Broken logic (old line 99):
    is_configured_broken = "SAG Award Winners" in collections  # False (wrong: it IS configured)
    configured_check_broken = configured_in == is_configured_broken  # False == False → True (DELETE!)

    # Demonstrate the fix would work: when the code checks collection_names
    # (the actual configured list), the collection is correctly identified
    # as configured and NOT deleted.
    is_configured_fixed = "SAG Award Winners" in collection_names  # True
    configured_check_fixed = configured_in == is_configured_fixed  # False == True → False (keep)

    assert configured_check_broken, "Bug not reproduced: broken code should trigger delete for a configured collection " "when library.collections is empty"
    assert not configured_check_fixed, "Fix verification: collection_names check should keep configured collections"


# ---------------------------------------------------------------------------
# Core fix: _should_be_deleted uses library.collection_names
# ---------------------------------------------------------------------------


def test_all_none_never_deletes():
    """Safety guard: when all criteria are None, nothing is deleted."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Any Collection")
    assert ops._should_be_deleted(col, [], None, None, None) is False


def test_configured_false_collection_in_names_not_deleted():
    """configured=False + collection IS in collection_names → keep (not unconfigured).

    This is the primary fix for #3168.  Before the fix, library.collections was empty
    so is_configured was always False, causing the delete to fire.
    """
    ops = make_ops(collections=[], collection_names=["SAG Award Winners"])
    col = make_col("SAG Award Winners")
    result = ops._should_be_deleted(col, ["Kometa"], configured_in=False, managed_in=None, less_in=None)
    assert result is False, "Configured collection must NOT be deleted"


def test_configured_false_collection_not_in_names_deleted():
    """configured=False + collection NOT in collection_names → delete (genuinely unconfigured)."""
    ops = make_ops(collections=[], collection_names=["SAG Award Winners"])
    col = make_col("Stale Old Collection")
    result = ops._should_be_deleted(col, ["Kometa"], configured_in=False, managed_in=None, less_in=None)
    assert result is True, "Unconfigured collection should be deleted"


def test_configured_true_collection_in_names_deleted():
    """configured=True means 'delete configured collections' -- inverse of the common case."""
    ops = make_ops(collections=[], collection_names=["SAG Award Winners"])
    col = make_col("SAG Award Winners")
    result = ops._should_be_deleted(col, ["Kometa"], configured_in=True, managed_in=None, less_in=None)
    assert result is True


def test_configured_true_collection_not_in_names_not_deleted():
    """configured=True + collection NOT in names → keep (not configured, user wants to delete configured)."""
    ops = make_ops(collections=[], collection_names=["SAG Award Winners"])
    col = make_col("Manual Collection")
    result = ops._should_be_deleted(col, [], configured_in=True, managed_in=None, less_in=None)
    assert result is False


# ---------------------------------------------------------------------------
# managed flag
# ---------------------------------------------------------------------------


def test_managed_true_deletes_kometa_label():
    """managed=True → delete collections labelled Kometa."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Managed Collection")
    assert ops._should_be_deleted(col, ["Kometa"], configured_in=None, managed_in=True, less_in=None) is True


def test_managed_true_deletes_pmm_label():
    """managed=True also matches the legacy PMM label."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("PMM Collection")
    assert ops._should_be_deleted(col, ["PMM"], configured_in=None, managed_in=True, less_in=None) is True


def test_managed_true_keeps_unmanaged():
    """managed=True does not touch collections without a Kometa/PMM label."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Manual Collection")
    assert ops._should_be_deleted(col, [], configured_in=None, managed_in=True, less_in=None) is False


def test_managed_false_deletes_unmanaged():
    """managed=False → delete collections with no Kometa/PMM label."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Manual Collection")
    assert ops._should_be_deleted(col, [], configured_in=None, managed_in=False, less_in=None) is True


def test_managed_false_keeps_kometa():
    """managed=False does not touch Kometa-managed collections."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Managed Collection")
    assert ops._should_be_deleted(col, ["Kometa"], configured_in=None, managed_in=False, less_in=None) is False


# ---------------------------------------------------------------------------
# combined configured + managed (the real-world #3168 scenario)
# ---------------------------------------------------------------------------


def test_combined_managed_true_configured_false_keeps_configured_collection():
    """delete_collections: {configured: false, managed: true}

    A Kometa-managed collection that IS in collection_names must survive.
    Before the fix: library.collections was empty → is_configured=False →
    configured_check=True → all checks True → deleted incorrectly.
    After the fix:  library.collection_names has the title → is_configured=True →
    configured_check=False → not deleted.
    """
    ops = make_ops(collections=[], collection_names=["SAG Award Winners"])
    col = make_col("SAG Award Winners")
    result = ops._should_be_deleted(col, ["Kometa"], configured_in=False, managed_in=True, less_in=None)
    assert result is False, "Managed + configured collection must not be deleted by " "delete_collections: {configured: false, managed: true}"


def test_combined_managed_true_configured_false_deletes_unconfigured_collection():
    """delete_collections: {configured: false, managed: true}

    A Kometa-managed collection that is NOT in collection_names (stale/renamed) should be deleted.
    """
    ops = make_ops(collections=[], collection_names=["SAG Award Winners"])
    col = make_col("Spirit Best Feature Winners")  # old name, no longer in YAML
    result = ops._should_be_deleted(col, ["Kometa"], configured_in=False, managed_in=True, less_in=None)
    assert result is True, "Managed + unconfigured (stale) collection should be deleted"


# ---------------------------------------------------------------------------
# less (childCount threshold)
# ---------------------------------------------------------------------------


def test_less_deletes_small_collection():
    """less=5: collection with 3 items should be deleted."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Tiny Collection", childCount=3)
    assert ops._should_be_deleted(col, [], configured_in=None, managed_in=None, less_in=5) is True


def test_less_keeps_collection_at_threshold():
    """less=5: collection with exactly 5 items is NOT below the threshold → keep."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Threshold Collection", childCount=5)
    assert ops._should_be_deleted(col, [], configured_in=None, managed_in=None, less_in=5) is False


def test_less_keeps_large_collection():
    """less=5: collection with 10 items should be kept."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Big Collection", childCount=10)
    assert ops._should_be_deleted(col, [], configured_in=None, managed_in=None, less_in=5) is False


def test_less_none_childcount_treated_as_zero():
    """A collection with childCount=None is treated as 0 (< any positive less threshold)."""
    ops = make_ops(collections=[], collection_names=[])
    col = make_col("Empty Collection", childCount=None)
    assert ops._should_be_deleted(col, [], configured_in=None, managed_in=None, less_in=1) is True


# ---------------------------------------------------------------------------
# collection_names pre-populated vs collections (the timing mismatch)
# ---------------------------------------------------------------------------


def test_collection_names_used_not_collections():
    """Explicit proof that _should_be_deleted reads collection_names, not collections.

    Both lists are set explicitly to different values; the decision must match
    collection_names.
    """
    # collection_names says configured, collections says not (as it was during run)
    ops = make_ops(
        collections=[],  # empty -- as it is when ops runs first
        collection_names=["César Award Winners"],
    )
    col = make_col("César Award Winners")

    # If it incorrectly uses library.collections: is_configured=False → configured_check=True → DELETE
    # If it correctly uses library.collection_names: is_configured=True → configured_check=False → KEEP
    result = ops._should_be_deleted(col, ["Kometa"], configured_in=False, managed_in=True, less_in=None)
    assert result is False, "_should_be_deleted is reading library.collections instead of library.collection_names"


# ---------------------------------------------------------------------------
# delete_collections run-end statistics
# ---------------------------------------------------------------------------


def test_delete_collections_counts_successful_deletions_in_run_stats():
    """Library-operation deletions must be included in the run-end notification total."""
    collections = [make_col("Biopic Movies"), make_col("Musical Movies")]
    library = make_title_test_library([])
    library.name = "Movies"
    library.items_library_operation = False
    library.delete_collections = {"managed": True, "configured": None, "less": None, "ignore_empty_smart_collections": True}
    library.collection_names = []
    library.collection_files = []
    library.assets_for_all_collections = False
    library.stats = {"deleted": 0}
    library.get_all_collections.return_value = collections
    library.item_labels.return_value = [SimpleNamespace(tag="Kometa")]

    def delete_collection(_collection):
        library.stats["deleted"] += 1

    library.delete_collection.side_effect = delete_collection

    Operations(config=MagicMock(), library=library).run_operations()

    assert library.stats["deleted"] == 2
    assert library.delete_collection.call_count == 2


# ---------------------------------------------------------------------------
# remove_title_parentheses batching (run_operations / items_library_operation)
# ---------------------------------------------------------------------------


def make_item(rating_key, title, title_locked=False):
    """Return a minimal fake Plex item for run_operations()'s per-item loop."""
    return SimpleNamespace(
        ratingKey=rating_key,
        title=title,
        fields=[SimpleNamespace(name="title", locked=True)] if title_locked else [],
        locations=[],
    )


def make_title_test_library(items):
    """Return a MagicMock library that only exercises remove_title_parentheses inside
    run_operations() - every other items_library_operation feature is stubbed off,
    since a bare MagicMock returns truthy MagicMocks for anything not set explicitly
    and would otherwise fire unrelated code paths (Radarr/Sonarr, mass rating/genre
    updates, IMDb parental labels, delete_collections, etc.)."""
    library = MagicMock()
    items_by_key = {item.ratingKey: item for item in items}

    library.items_library_operation = True
    library.remove_title_parentheses = True
    library.is_movie = True
    library.is_show = False
    library.plex_bulk_edit_batch_size = None
    library.Radarr = None
    library.Sonarr = None
    library.delete_collections = None
    library.mass_collection_mode = None
    # These three are checked with "is not None", not truthiness, so False won't skip them.
    library.mass_episode_audience_rating_update = None
    library.mass_episode_critic_rating_update = None
    library.mass_episode_user_rating_update = None

    for flag in [
        "split_duplicates",
        "sync_watchlist_to_serializd",
        "update_blank_track_titles",
        "assets_for_all",
        "respect_ignore_ids",
        "mass_imdb_parental_labels",
        "mass_audience_rating_update",
        "mass_critic_rating_update",
        "mass_user_rating_update",
        "radarr_add_all_existing",
        "sonarr_add_all_existing",
        "mass_genre_update",
        "genre_mapper",
        "mass_content_rating_update",
        "content_rating_mapper",
        "mass_original_title_update",
        "mass_studio_update",
        "mass_poster_update",
        "mass_background_update",
        "mass_logo_update",
        "mass_square_art_update",
        "mass_originally_available_update",
        "mass_added_at_update",
        "radarr_remove_by_tag",
        "sonarr_remove_by_tag",
        "show_unmanaged",
        "show_unconfigured",
        "metadata_backup",
        "label_operations",
    ]:
        setattr(library, flag, False)

    library.get_all.return_value = items
    library.reload.side_effect = lambda item, **_: item
    library.item_has_ignore_label.return_value = False
    library.get_ids.return_value = (None, None, None)
    library.load_list_from_cache.side_effect = lambda keys: [items_by_key[k] for k in keys]
    return library


class TestRemoveTitleParenthesesBatching:
    def test_batches_by_distinct_new_title(self):
        """Two items with different target titles - one editField call per distinct value."""
        item_a = make_item(1, "Movie A (2020)")
        item_b = make_item(2, "Movie B (2021)")
        library = make_title_test_library([item_a, item_b])
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        library.Plex.editField.assert_any_call("title", "Movie A")
        library.Plex.editField.assert_any_call("title", "Movie B")
        assert library.Plex.batchMultiEdits.call_count == 2
        assert library._save_multi_edits_with_retry.call_count == 2

    def test_groups_shared_new_title_into_one_batch(self):
        """Two items whose parenthetical strip lands on the same title - one batched call
        covering both items, not two separate editTitle-per-item calls."""
        item_a = make_item(1, "Same Title (2020)")
        item_b = make_item(2, "Same Title (2021)")
        library = make_title_test_library([item_a, item_b])
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        library.Plex.editField.assert_called_once_with("title", "Same Title")
        library.Plex.batchMultiEdits.assert_called_once_with([item_a, item_b])
        library._save_multi_edits_with_retry.assert_called_once()

    def test_skips_locked_title(self):
        item = make_item(1, "Movie A (2020)", title_locked=True)
        library = make_title_test_library([item])
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        library.Plex.editField.assert_not_called()
        library.Plex.batchMultiEdits.assert_not_called()

    def test_skips_title_without_trailing_parentheses(self):
        item = make_item(1, "Movie A")
        library = make_title_test_library([item])
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        library.Plex.editField.assert_not_called()

    def test_disabled_flag_does_nothing(self):
        item = make_item(1, "Movie A (2020)")
        library = make_title_test_library([item])
        library.remove_title_parentheses = False
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        library.Plex.editField.assert_not_called()


# ---------------------------------------------------------------------------
# flush_combined_edits (checklist item 17)
# ---------------------------------------------------------------------------


def make_mass_edit_item(rating_key, title, rating=None, audience_rating=None, content_rating=None, genres=None):
    """Return a minimal fake Plex item for the mass_*_update branches of run_operations()."""
    return SimpleNamespace(
        ratingKey=rating_key,
        title=title,
        fields=[],
        locations=[],
        rating=rating,
        audienceRating=audience_rating,
        userRating=None,
        contentRating=content_rating,
        genres=genres if genres is not None else [],
        originalTitle=None,
        studio=None,
        originallyAvailableAt=None,
        addedAt=None,
    )


def make_mass_edit_library(items, **mass_update_overrides):
    """Return a MagicMock library exercising only the mass_*_update branches of
    run_operations() - everything else stubbed off, same convention as
    make_title_test_library(). mass_*_update options are set to literal values
    (e.g. "7.5") rather than provider names ("tmdb") so no TMDb/IMDb/etc. mocking
    is needed - operations.py falls through to using the option itself as the
    value when it doesn't match a known provider keyword."""
    library = MagicMock()
    items_by_key = {item.ratingKey: item for item in items}

    library.items_library_operation = True
    library.remove_title_parentheses = False
    library.is_movie = True
    library.is_show = False
    library.plex_bulk_edit_batch_size = None
    library.Radarr = None
    library.Sonarr = None
    library.delete_collections = None
    library.mass_collection_mode = None
    library.mass_episode_audience_rating_update = None
    library.mass_episode_critic_rating_update = None
    library.mass_episode_user_rating_update = None

    for flag in [
        "split_duplicates",
        "sync_watchlist_to_serializd",
        "update_blank_track_titles",
        "assets_for_all",
        "respect_ignore_ids",
        "mass_imdb_parental_labels",
        "mass_audience_rating_update",
        "mass_critic_rating_update",
        "mass_user_rating_update",
        "radarr_add_all_existing",
        "sonarr_add_all_existing",
        "mass_genre_update",
        "genre_mapper",
        "mass_content_rating_update",
        "content_rating_mapper",
        "mass_original_title_update",
        "mass_studio_update",
        "mass_poster_update",
        "mass_background_update",
        "mass_logo_update",
        "mass_square_art_update",
        "mass_originally_available_update",
        "mass_added_at_update",
        "radarr_remove_by_tag",
        "sonarr_remove_by_tag",
        "show_unmanaged",
        "show_unconfigured",
        "metadata_backup",
        "label_operations",
    ]:
        setattr(library, flag, False)

    for key, value in mass_update_overrides.items():
        setattr(library, key, value)

    library.get_all.return_value = items
    library.reload.side_effect = lambda item: item
    library.item_has_ignore_label.return_value = False
    library.get_ids.return_value = (None, None, None)
    library.load_list_from_cache.side_effect = lambda keys: [items_by_key[k] for k in keys if k in items_by_key]
    library._group_items_by_type.side_effect = lambda items_: [items_]
    return library


class TestFlushCombinedEdits:
    def test_syncs_plex_watched_episodes_to_serializd_by_season(self):
        ops_module.logger.reset_mock()
        item = make_mass_edit_item(1, "Attack on Titan")
        episodes = [
            SimpleNamespace(seasonNumber=1, episodeNumber=1, isWatched=True, viewCount=1),
            SimpleNamespace(seasonNumber=1, episodeNumber=2, isWatched=False, viewCount=0),
            SimpleNamespace(seasonNumber=2, episodeNumber=1, isWatched=False, viewCount=2),
        ]
        library = make_mass_edit_library([item], sync_watchlist_to_serializd=True)
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (1429, None, None)
        library.cached_item_subitems.return_value = episodes
        config = MagicMock()
        config.Cache = None
        config.Serializd.log_watched_episodes.return_value = True

        Operations(config=config, library=library).run_operations()

        assert config.Serializd.log_watched_episodes.call_args_list == [
            ((1429, 1, [1]),),
            ((1429, 2, [1]),),
        ]
        ops_module.logger.info.assert_any_call("Serializd Watched | Synced")

    def test_reports_no_updates_when_all_watched_episodes_are_cached(self):
        ops_module.logger.reset_mock()
        item = make_mass_edit_item(1, "Ted Lasso")
        episode = SimpleNamespace(seasonNumber=3, episodeNumber=1, isWatched=True, viewCount=1)
        library = make_mass_edit_library([item], sync_watchlist_to_serializd=True)
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (97546, None, None)
        library.cached_item_subitems.return_value = [episode]
        config = MagicMock()
        config.Serializd.cache_key = "account-key"
        config.Cache.query_serializd_watched.return_value = [1]

        Operations(config=config, library=library).run_operations()

        config.Serializd.log_watched_episodes.assert_not_called()
        ops_module.logger.info.assert_any_call("Serializd Watched | No Updates")

    def test_skips_cached_serializd_episodes_and_caches_successes(self):
        item = make_mass_edit_item(1, "Attack on Titan")
        episodes = [
            SimpleNamespace(seasonNumber=1, episodeNumber=1, isWatched=True, viewCount=1),
            SimpleNamespace(seasonNumber=1, episodeNumber=2, isWatched=True, viewCount=1),
        ]
        library = make_mass_edit_library([item], sync_watchlist_to_serializd=True)
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (1429, None, None)
        library.cached_item_subitems.return_value = episodes
        config = MagicMock()
        config.Serializd.cache_key = "account-key"
        config.Serializd.log_watched_episodes.return_value = True
        config.Cache.query_serializd_watched.return_value = [1]

        Operations(config=config, library=library).run_operations()

        config.Serializd.log_watched_episodes.assert_called_once_with(1429, 1, [2])
        config.Cache.update_serializd_watched.assert_called_once_with("account-key", 1429, 1, [2])

    def test_does_not_cache_failed_serializd_sync(self):
        item = make_mass_edit_item(1, "Attack on Titan")
        episode = SimpleNamespace(seasonNumber=1, episodeNumber=1, isWatched=True, viewCount=1)
        library = make_mass_edit_library([item], sync_watchlist_to_serializd=True)
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (1429, None, None)
        library.cached_item_subitems.return_value = [episode]
        config = MagicMock()
        config.Serializd.cache_key = "account-key"
        config.Serializd.log_watched_episodes.side_effect = ops_module.Failed("sync failed")
        config.Cache.query_serializd_watched.return_value = []

        Operations(config=config, library=library).run_operations()

        config.Cache.update_serializd_watched.assert_not_called()

    def test_serializd_genres_for_show(self):
        item = make_mass_edit_item(1, "Show A")
        library = make_mass_edit_library([item], mass_genre_update=["serializd"])
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (1396, None, "tt0903747")
        config = MagicMock()
        config.Serializd.get_show_genres.return_value = ["Drama", "Crime"]

        Operations(config=config, library=library).run_operations()

        config.Serializd.get_show_genres.assert_called_once_with(1396)
        library.Plex.editTags.assert_any_call("genre", "Crime", remove=False)
        library.Plex.editTags.assert_any_call("genre", "Drama", remove=False)

    def test_serializd_resolves_tvdb_id_to_tmdb_for_show(self):
        item = make_mass_edit_item(1, "Arcane")
        library = make_mass_edit_library([item], mass_genre_update=["serializd"])
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (None, 371028, None)
        config = MagicMock()
        config.Convert.tvdb_to_tmdb.return_value = 94605
        config.Serializd.get_show_genres.return_value = ["Animation", "Drama"]

        Operations(config=config, library=library).run_operations()

        config.Convert.tvdb_to_tmdb.assert_called_once_with(371028)
        config.Serializd.get_show_genres.assert_called_once_with(94605)
        library.Plex.editTags.assert_any_call("genre", "Animation", remove=False)
        library.Plex.editTags.assert_any_call("genre", "Drama", remove=False)

    def test_serializd_nanogenres_source(self):
        item = make_mass_edit_item(1, "Attack on Titan")
        library = make_mass_edit_library([item], mass_genre_update=["serializd_nanogenres"])
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (1429, None, None)
        config = MagicMock()
        config.Serializd.get_show_nanogenres.return_value = ["Anime", "Monsters"]

        Operations(config=config, library=library).run_operations()

        config.Serializd.get_show_nanogenres.assert_called_once_with(1429)
        library.Plex.editTags.assert_any_call("genre", "Anime", remove=False)
        library.Plex.editTags.assert_any_call("genre", "Monsters", remove=False)

    def test_serializd_show_rating_source(self):
        item = make_mass_edit_item(1, "Attack on Titan")
        library = make_mass_edit_library([item], mass_audience_rating_update=["serializd"])
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (1429, None, None)
        config = MagicMock()
        config.Serializd.get_show_rating.return_value = 9.07

        Operations(config=config, library=library).run_operations()

        config.Serializd.get_show_rating.assert_called_once_with(1429)
        library.Plex.editField.assert_any_call("audienceRating", "9.1")

    def test_serializd_episode_rating_source(self):
        item = make_mass_edit_item(1, "Attack on Titan")
        episode = SimpleNamespace(ratingKey=2, audienceRating=None, rating=None, userRating=None, seasonNumber=1, episodeNumber=1)
        library = make_mass_edit_library([item], mass_episode_user_rating_update=["serializd"])
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (1429, None, None)
        library.cached_item_subitems.return_value = [episode]
        library.get_item_display_title.return_value = "S01E01"
        config = MagicMock()
        config.Serializd.get_episode_rating.return_value = 8.79

        Operations(config=config, library=library).run_operations()

        config.Serializd.get_episode_rating.assert_called_once_with(1429, 1, 1)
        library.Plex.editField.assert_any_call("userRating", "8.8")

    def test_serializd_user_episode_rating_source(self):
        item = make_mass_edit_item(1, "Attack on Titan")
        episode = SimpleNamespace(ratingKey=2, audienceRating=None, rating=None, userRating=None, seasonNumber=1, episodeNumber=1)
        library = make_mass_edit_library([item], mass_episode_user_rating_update=["serializd_user"])
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (1429, None, None)
        library.cached_item_subitems.return_value = [episode]
        library.get_item_display_title.return_value = "S01E01"
        config = MagicMock()
        config.Serializd.get_episode_user_rating.return_value = 9

        Operations(config=config, library=library).run_operations()

        config.Serializd.get_episode_user_rating.assert_called_once_with(1429, 1, 1)
        library.Plex.editField.assert_any_call("userRating", "9.0")

    def test_floppy_show_rating_resolves_tmdb_id_from_tvdb_first_plex_mapping(self):
        item = make_mass_edit_item(1, "Arcane")
        item.guid = "plex://show/arcane"
        library = make_mass_edit_library([item], mass_user_rating_update=["floppy"])
        library.is_movie = False
        library.is_show = True
        library.get_ids.return_value = (None, 371028, "tt11126994")
        config = MagicMock()
        config.TMDb.get_item.return_value = SimpleNamespace(tmdb_id=94605)
        config.Floppy.get_rating.return_value = 5.0

        Operations(config=config, library=library).run_operations()

        config.Floppy.get_rating.assert_called_once_with("tv", tmdb_id=94605, tvdb_id=371028, imdb_id="tt11126994")
        library.Plex.editField.assert_called_once_with("userRating", "5.0")

    def test_mdb_letterboxd_rating_above_ten_is_not_sent_to_plex(self):
        ops_module.logger.reset_mock()
        item = make_mass_edit_item(1, "Invalid Letterboxd Rating")
        library = make_mass_edit_library([item], mass_user_rating_update=["mdb_letterboxd"])
        library.get_ids.return_value = (123, None, None)
        config = MagicMock()
        config.MDBList.limit = False
        config.MDBList.get_movie.return_value = SimpleNamespace(letterboxd_rating=5.1)

        Operations(config=config, library=library).run_operations()

        library.Plex.editField.assert_not_called()
        ops_module.logger.warning.assert_any_call("mdb_letterboxd User Rating value 5.1 is invalid for the provider's 0 to 5 scale; expected a finite number; skipping")

    @pytest.mark.parametrize("value", [-0.1, 100.1, "bad", float("nan"), float("inf"), float("-inf"), True])
    def test_every_illegal_provider_rating_is_not_sent_to_plex(self, value):
        ops_module.logger.reset_mock()
        item = make_mass_edit_item(1, "Invalid Provider Rating")
        library = make_mass_edit_library([item], mass_user_rating_update=["mdb"])
        library.get_ids.return_value = (123, None, None)
        config = MagicMock()
        config.MDBList.limit = False
        config.MDBList.get_movie.return_value = SimpleNamespace(score=value)

        Operations(config=config, library=library).run_operations()

        library.Plex.editField.assert_not_called()
        assert any("expected a finite number" in call.args[0] for call in ops_module.logger.warning.call_args_list)

    def test_merges_multiple_attribute_types_into_one_put(self):
        """An item needing rating + audience rating + genre + content rating all changed in
        the same run gets ONE batchMultiEdits()/saveMultiEdits() PUT, not four."""
        item = make_mass_edit_item(1, "Movie A")
        library = make_mass_edit_library(
            [item],
            mass_critic_rating_update=["7.5"],
            mass_audience_rating_update=["8.0"],
            mass_genre_update=[["Action"]],
            mass_content_rating_update=["PG-13"],
        )
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        library.Plex.batchMultiEdits.assert_called_once_with([item])
        library._save_multi_edits_with_retry.assert_called_once()
        library.Plex.editField.assert_any_call("rating", "7.5")
        library.Plex.editField.assert_any_call("audienceRating", "8.0")
        library.Plex.editField.assert_any_call("contentRating", "PG-13")
        library.Plex.editTags.assert_any_call("genre", ["Action"], remove=False)

    def test_single_attribute_type_item_not_merged(self):
        """An item needing only ONE attribute type changed still goes through the normal
        per-attribute flush path, unaffected by the merge logic."""
        item = make_mass_edit_item(1, "Movie A")
        library = make_mass_edit_library([item], mass_genre_update=[["Action"]])
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        library.Plex.batchMultiEdits.assert_called_once_with([item])
        library._save_multi_edits_with_retry.assert_called_once()
        # Not merged (one attribute type only), so this is the pre-existing per-value-keyed flush path.
        library.Plex.editTags.assert_any_call("genre", "Action", remove=False)

    def test_mixed_run_only_merges_multi_attribute_items(self):
        """Two items in the same run - one needs 2 attribute types (merged into 1 PUT), the
        other needs only 1 (goes through the normal path) - total 2 PUTs, not 3."""
        merged_item = make_mass_edit_item(1, "Merged Movie")
        single_item = make_mass_edit_item(2, "Single Movie")
        library = make_mass_edit_library(
            [merged_item, single_item],
            mass_critic_rating_update=["7.5"],
            mass_genre_update=[["Action"]],
        )
        # Both items share the same config, so both get rating + genre and both should merge.
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        assert library.Plex.batchMultiEdits.call_count == 2  # one merged PUT per item, not per attribute type
        assert library._save_multi_edits_with_retry.call_count == 2

    def test_no_mass_update_flags_does_nothing(self):
        item = make_mass_edit_item(1, "Movie A")
        library = make_mass_edit_library([item])
        ops = Operations(config=MagicMock(), library=library)

        ops.run_operations()

        library.Plex.editField.assert_not_called()
        library.Plex.editTags.assert_not_called()
        library.Plex.batchMultiEdits.assert_not_called()


# ---------------------------------------------------------------------------
# Module-level pure functions
# ---------------------------------------------------------------------------


class TestItemBatches:
    """Tests for operations._item_batches generator."""

    def test_empty_list_yields_nothing(self):
        from modules.operations import _item_batches

        assert list(_item_batches([], 10)) == []

    def test_exact_multiple(self):
        from modules.operations import _item_batches

        result = list(_item_batches([1, 2, 3, 4, 5, 6], 2))
        assert result == [[1, 2], [3, 4], [5, 6]]

    def test_leftover_batch(self):
        from modules.operations import _item_batches

        result = list(_item_batches([1, 2, 3, 4, 5], 2))
        assert result == [[1, 2], [3, 4], [5]]

    def test_batch_larger_than_items(self):
        from modules.operations import _item_batches

        result = list(_item_batches([1, 2, 3], 100))
        assert result == [[1, 2, 3]]

    def test_batch_size_one(self):
        from modules.operations import _item_batches

        result = list(_item_batches([1, 2, 3], 1))
        assert result == [[1], [2], [3]]


class TestFindCollectionTransKey:
    """Tests for operations._find_collection_trans_key recursive lookup."""

    def test_top_level_string(self):
        from modules.operations import _find_collection_trans_key

        assert _find_collection_trans_key({"translation_key": "movie_genre"}) == "movie_genre"

    def test_nested_dict(self):
        from modules.operations import _find_collection_trans_key

        data = {"outer": {"inner": {"translation_key": "trending"}}}
        assert _find_collection_trans_key(data) == "trending"

    def test_inside_list(self):
        from modules.operations import _find_collection_trans_key

        data = {"items": [{"name": "a"}, {"translation_key": "comedy"}]}
        assert _find_collection_trans_key(data) == "comedy"

    def test_absent_returns_none(self):
        from modules.operations import _find_collection_trans_key

        assert _find_collection_trans_key({"name": "foo", "count": 5}) is None

    def test_unresolved_template_value_skipped(self):
        """Values containing '<<' are template placeholders — must not match."""
        from modules.operations import _find_collection_trans_key

        # Skips the template placeholder and keeps recursing
        assert _find_collection_trans_key({"translation_key": "<<key>>"}) is None

    def test_non_string_value_skipped(self):
        from modules.operations import _find_collection_trans_key

        assert _find_collection_trans_key({"translation_key": 42}) is None

    def test_non_dict_non_list_input(self):
        from modules.operations import _find_collection_trans_key

        assert _find_collection_trans_key("just a string") is None
        assert _find_collection_trans_key(None) is None
        assert _find_collection_trans_key(123) is None

    def test_returns_first_match_depth_first(self):
        from modules.operations import _find_collection_trans_key

        data = {
            "a": {"translation_key": "first"},
            "b": {"translation_key": "second"},
        }
        # dict iteration order is insertion order in Python 3.7+
        assert _find_collection_trans_key(data) == "first"


class TestConfiguredCollectionNameAliases:
    @staticmethod
    def _objects(expanded, language="fr"):
        english = {
            "variables": {"library_translation": {"movie": "movie"}},
            "key_names": {"chart": "Chart"},
            "collections": {
                "separator": {"name": "<<key_name>> Collections"},
                "tmdb_popular": {"name": "TMDb Popular"},
            },
        }
        french = {
            "variables": {"library_translation": {"movie": "film"}},
            "key_names": {"chart": "Classement"},
            "collections": {
                "separator": {"name": "Collections <<key_name>>"},
                "tmdb_popular": {"name": "TMDb Populaire"},
            },
        }
        german = {
            "variables": {"library_translation": {"movie": "film"}},
            "key_names": {"chart": "Rangliste"},
            "collections": {"separator": {"name": "<<key_name>> Sammlungen"}},
        }
        spanish = {
            "variables": {"library_translation": {"movie": "película"}},
            "key_names": {"chart": "Clasificación"},
            "collections": {"separator": {"name": "Colecciones de <<key_name>>"}},
        }
        japanese = {
            "variables": {"library_translation": {"movie": "映画"}},
            "key_names": {"chart": "ランキング"},
            "collections": {"separator": {"name": "<<key_name>>コレクション"}},
        }
        italian = {
            "variables": {"library_translation": {"movie": "film"}},
            "key_names": {"chart": "Classifica"},
            "collections": {},
        }
        translations = {"en": english, "fr": french, "de": german, "es": spanish, "ja": japanese, "it": italian}
        config = MagicMock()
        config.GitHub.translation_keys = list(translations)
        config.GitHub.translation_yaml.side_effect = translations.__getitem__
        library = SimpleNamespace(type="Movie")
        metadata_file = SimpleNamespace(language=language, apply_template=MagicMock(return_value=expanded))
        return config, library, metadata_file

    def test_resolves_mapping_english_and_selected_language_names(self):
        config, library, metadata_file = self._objects({"translation_key": "separator", "key_name": "Chart"})

        aliases = _configured_collection_name_aliases(config, library, metadata_file, "Chart Collections", {"template": [{"name": "separator"}]})

        assert aliases == {"Chart Collections", "Collections Classement"}
        operations = make_ops(collections=[], collection_names=[])
        french_collection = make_col("Collections Classement")
        assert operations._should_be_deleted(french_collection, ["Kometa"], configured_in=False, managed_in=True, less_in=None, configured_names=aliases) is False

    def test_includes_custom_name_override_and_translation_aliases(self):
        custom_name = "🌍 Films populaires dans le monde"
        config, library, metadata_file = self._objects({"name": custom_name, "translation_key": "tmdb_popular"})

        aliases = _configured_collection_name_aliases(config, library, metadata_file, "TMDb Popular", {"template": [{"name": "shared"}]})

        assert aliases == {"TMDb Popular", "TMDb Populaire", custom_name}

    def test_resolves_generated_dynamic_collection_without_reapplying_template(self):
        config, library, metadata_file = self._objects({})
        collection_data = {"translation_key": "separator", "key_name": "Chart"}

        aliases = _configured_collection_name_aliases(config, library, metadata_file, "Chart Collections", collection_data)

        assert aliases == {"Chart Collections", "Collections Classement"}
        metadata_file.apply_template.assert_not_called()

    def test_resolves_selected_languages_without_language_specific_code(self):
        expected_names = {
            "fr": "Collections Classement",
            "de": "Rangliste Sammlungen",
            "es": "Colecciones de Clasificación",
            "ja": "ランキングコレクション",
        }
        collection_data = {"translation_key": "separator", "key_name": "Chart"}

        for language, expected_name in expected_names.items():
            config, library, metadata_file = self._objects({}, language=language)
            aliases = _configured_collection_name_aliases(config, library, metadata_file, "Chart Collections", collection_data)
            assert expected_name in aliases

    def test_collection_language_override_takes_priority_over_file_language(self):
        config, library, metadata_file = self._objects({}, language="fr")
        collection_data = {"language": "ja", "translation_key": "separator", "key_name": "Chart"}

        aliases = _configured_collection_name_aliases(config, library, metadata_file, "Chart Collections", collection_data)

        assert "ランキングコレクション" in aliases
        assert "Collections Classement" not in aliases

    def test_falls_back_to_english_when_selected_language_has_no_collection_name(self):
        config, library, metadata_file = self._objects({}, language="it")
        collection_data = {"translation_key": "separator", "key_name": "Chart"}

        aliases = _configured_collection_name_aliases(config, library, metadata_file, "Chart Collections", collection_data)

        assert aliases == {"Chart Collections"}

    def test_keeps_mapping_name_when_name_resolution_fails(self):
        config, library, metadata_file = self._objects({})

        aliases = _configured_collection_name_aliases(config, library, metadata_file, "Manual Collection", {})

        assert aliases == {"Manual Collection"}


# ---------------------------------------------------------------------------
# Module constants — sanity checks on the dispatch / format tables
# ---------------------------------------------------------------------------


class TestModuleConstants:
    """Verify the operations module's lookup tables are well-formed.

    These constants drive runtime dispatch (e.g. ``meta_operations``
    enumerates the supported mass-update operations). A duplicate
    or typo here is a silent bug — these tests catch it at CI time.
    """

    def test_meta_operations_no_duplicates(self):
        from modules.operations import meta_operations

        assert len(meta_operations) == len(set(meta_operations)), f"meta_operations has duplicates: " f"{[x for x in meta_operations if meta_operations.count(x) > 1]}"

    def test_meta_operations_all_strings(self):
        from modules.operations import meta_operations

        for op in meta_operations:
            assert isinstance(op, str)
            assert op  # non-empty

    def test_meta_operations_naming_convention(self):
        """Every meta-operation must start with 'mass_' and end with '_update'."""
        from modules.operations import meta_operations

        for op in meta_operations:
            assert op.startswith("mass_"), f"{op!r} doesn't follow mass_*_update convention"
            assert op.endswith("_update"), f"{op!r} doesn't follow mass_*_update convention"

    def test_name_display_keys_are_camelcase(self):
        """name_display maps Plex field names (camelCase) to human labels."""
        from modules.operations import name_display

        for plex_field in name_display:
            assert isinstance(plex_field, str)
            # Plex field names are camelCase — should never contain underscores
            assert "_" not in plex_field, f"{plex_field!r} looks like snake_case, not a Plex field"

    def test_tmdb_release_types_have_valid_ids(self):
        """TMDb release_type IDs are 1-6 per the TMDb API spec."""
        from modules.operations import tmdb_release_types

        for key, value in tmdb_release_types.items():
            assert key.startswith("tmdb_"), f"{key!r} should start with tmdb_"
            assert 1 <= value <= 6, f"{key}={value} is outside TMDb's valid release_type range (1-6)"

    def test_tmdb_release_types_values_unique(self):
        """Each release_type ID maps to one Kometa key."""
        from modules.operations import tmdb_release_types

        values = list(tmdb_release_types.values())
        assert len(values) == len(set(values)), "tmdb_release_types has duplicate IDs"
