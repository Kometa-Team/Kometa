"""Tests for modules/operations.py -- focused on _should_be_deleted / delete_collections.

Issue #3168: When run_order puts operations before collections, library.collections is always
empty at the time delete_collections runs.  The old code checked
    col_in.title in self.library.collections
so every managed collection appeared "unconfigured" and was deleted.

Fix: use self.library.collection_names (pre-populated from YAML before the run_order loop).
"""
from unittest.mock import MagicMock, patch

import pytest

import modules.builder  # noqa: F401 -- pre-import to break plex<->builder circular import
import modules.operations as ops_module

# util.logger is None until Kometa initialises its logger; patch it for tests.
ops_module.logger = MagicMock()

from modules.operations import Operations


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
    collections = []        # always empty when operations runs first
    configured_in = False   # user setting: delete unconfigured collections

    # Broken logic (old line 99):
    is_configured_broken = "SAG Award Winners" in collections       # False (wrong: it IS configured)
    configured_check_broken = configured_in == is_configured_broken  # False == False → True (DELETE!)

    assert configured_check_broken, (
        "Bug not reproduced: broken code should trigger delete for a configured collection "
        "when library.collections is empty"
    )


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
    assert result is False, (
        "Managed + configured collection must not be deleted by "
        "delete_collections: {configured: false, managed: true}"
    )


def test_combined_managed_true_configured_false_deletes_unconfigured_collection():
    """delete_collections: {configured: false, managed: true}

    A Kometa-managed collection that is NOT in collection_names (stale/renamed) should be deleted.
    """
    ops = make_ops(collections=[], collection_names=["SAG Award Winners"])
    col = make_col("Spirit Best Feature Winners")   # old name, no longer in YAML
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
        collections=[],                        # empty -- as it is when ops runs first
        collection_names=["César Award Winners"],
    )
    col = make_col("César Award Winners")

    # If it incorrectly uses library.collections: is_configured=False → configured_check=True → DELETE
    # If it correctly uses library.collection_names: is_configured=True → configured_check=False → KEEP
    result = ops._should_be_deleted(col, ["Kometa"], configured_in=False, managed_in=True, less_in=None)
    assert result is False, (
        "_should_be_deleted is reading library.collections instead of library.collection_names"
    )
