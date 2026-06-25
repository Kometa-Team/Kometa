"""
Scenario tests for the overlay change detection logic and the cache-poisoning fix.

These tests exercise the cache layer (query/update/delete overlay_state) to verify
the interaction patterns that overlays.py relies on. They document the expected
state transitions for:

  1. No change  → render skipped (cached state matches current)
  2. New overlay → render triggered (mapping_name absent from cached state)
  3. Removed overlay → render triggered (cached key not in current set)
  4. Config change → render triggered (definition_hash differs)
  5. Poisoning fix → unresolved overlay absent from state, retried next run

The actual change-detection comparisons in overlays.py are pure dict logic;
these tests verify the cache layer produces the right state for those comparisons.
"""
import sqlite3

import pytest

from modules import cache as cache_module
from modules.cache import Cache
from unittest.mock import MagicMock


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_module, "logger", MagicMock())
    return Cache(str(tmp_path / "test.yml"), 60)


def _setup_table(cache):
    table_name = cache.get_image_table_name("TestLib")
    return f"{table_name}_overlay_state"


# ── Helpers that mirror what overlays.py does each run ────────────────────────

def _write_state(cache, state_table, rating_key, overlays):
    """Simulate the post-render cache write: delete all then write resolved overlays.
    overlays: dict of {mapping_name: (definition_hash, resolved_value_or_None)}
    """
    cache.delete_overlay_state(rating_key, state_table)
    for mapping_name, (definition_hash, resolved_value) in overlays.items():
        cache.update_overlay_state(rating_key, mapping_name, state_table, definition_hash, resolved_value)


def _detect_change(cached_state, current_hashes):
    """Mirror of the change-detection algorithm in overlays.py run_overlays()."""
    for cached_key in cached_state:
        if cached_key not in current_hashes:
            return f"Overlay Removed: {cached_key}"
    for mapping_name, current_hash in current_hashes.items():
        if mapping_name not in cached_state:
            return f"New Overlay: {mapping_name}"
        if cached_state[mapping_name][0] != current_hash:
            return f"Overlay Changed: {mapping_name}"
    return ""


# ── Change detection scenarios ─────────────────────────────────────────────────

def test_no_change_detected_when_state_matches(cache):
    state_table = _setup_table(cache)
    # Run 1: write state for two overlays.
    _write_state(cache, state_table, 5173, {
        "Overlay File (0) Rating1Fresh": ("hashA", "7.3"),
        "Overlay File (0) 4K":           ("hashB", None),
    })
    # Run 2: same overlays, same hashes.
    cached_state = cache.query_overlay_state(5173, state_table)
    current_hashes = {"Overlay File (0) Rating1Fresh": "hashA", "Overlay File (0) 4K": "hashB"}
    assert _detect_change(cached_state, current_hashes) == ""


def test_new_overlay_triggers_change(cache):
    state_table = _setup_table(cache)
    # Run 1: only 4K overlay cached.
    _write_state(cache, state_table, 5173, {"Overlay File (0) 4K": ("hashB", None)})
    # Run 2: Rating1Fresh added.
    cached_state = cache.query_overlay_state(5173, state_table)
    current_hashes = {"Overlay File (0) 4K": "hashB", "Overlay File (0) Rating1Fresh": "hashA"}
    change = _detect_change(cached_state, current_hashes)
    assert change.startswith("New Overlay:")


def test_removed_overlay_triggers_change(cache):
    state_table = _setup_table(cache)
    # Run 1: both overlays cached.
    _write_state(cache, state_table, 5173, {
        "Overlay File (0) Rating1Fresh": ("hashA", "7.3"),
        "Overlay File (0) 4K":           ("hashB", None),
    })
    # Run 2: 4K removed from config.
    cached_state = cache.query_overlay_state(5173, state_table)
    current_hashes = {"Overlay File (0) Rating1Fresh": "hashA"}
    change = _detect_change(cached_state, current_hashes)
    assert change.startswith("Overlay Removed:")


def test_definition_hash_change_triggers_change(cache):
    state_table = _setup_table(cache)
    # Run 1: overlay with hashA.
    _write_state(cache, state_table, 5173, {"Overlay File (0) Rating1Fresh": ("hashA", "7.3")})
    # Run 2: user tweaked font size → new hash.
    cached_state = cache.query_overlay_state(5173, state_table)
    current_hashes = {"Overlay File (0) Rating1Fresh": "hashA_modified"}
    change = _detect_change(cached_state, current_hashes)
    assert change.startswith("Overlay Changed:")


def test_resolved_value_change_is_visible_in_state(cache):
    state_table = _setup_table(cache)
    # Run 1: rating was 7.3.
    _write_state(cache, state_table, 5173, {"Overlay File (0) Rating1Fresh": ("hashA", "7.3")})
    # Run 2: rating changed to 7.5 after re-fetch.
    _write_state(cache, state_table, 5173, {"Overlay File (0) Rating1Fresh": ("hashA", "7.5")})
    states = cache.query_overlay_state(5173, state_table)
    assert states["Overlay File (0) Rating1Fresh"] == ("hashA", "7.5")


# ── Poisoning fix ──────────────────────────────────────────────────────────────

def test_unresolved_overlay_absent_from_state_is_retried(cache):
    """The cache-poisoning fix: when a rating fetch fails (overlay goes into 'unresolved'),
    its mapping_name is skipped in the state write. On the next run, the overlay is absent
    from cached_state → treated as 'New Overlay' → retried. Never stuck as 'done'.
    """
    state_table = _setup_table(cache)

    # Simulate a render where Rating1Fresh resolved (rating=7.3) but HDR did not (no image).
    over_names = ["Overlay File (0) Rating1Fresh", "Overlay File (0) HDR"]
    unresolved = {"Overlay File (0) HDR"}
    resolved_values = {"Overlay File (0) Rating1Fresh": "7.3"}
    current_hashes = {"Overlay File (0) Rating1Fresh": "hashA", "Overlay File (0) HDR": "hashB"}

    cache.delete_overlay_state(5173, state_table)
    for mapping_name in over_names:
        if mapping_name in unresolved:
            continue  # the poisoning fix
        cache.update_overlay_state(5173, mapping_name, state_table, current_hashes[mapping_name], resolved_values.get(mapping_name))

    states = cache.query_overlay_state(5173, state_table)

    # Rating1Fresh was resolved — must be in cache.
    assert "Overlay File (0) Rating1Fresh" in states
    assert states["Overlay File (0) Rating1Fresh"] == ("hashA", "7.3")

    # HDR was unresolved — must be ABSENT, so next run triggers "New Overlay" rather than skipping it.
    assert "Overlay File (0) HDR" not in states
    change = _detect_change(states, current_hashes)
    assert change == "New Overlay: Overlay File (0) HDR"


def test_previously_unresolved_overlay_written_once_it_resolves(cache):
    """Once the item acquires the resource that previously failed (e.g. rating arrives),
    the overlay resolves and its state is written. Subsequent runs then skip it correctly.
    """
    state_table = _setup_table(cache)

    # Run 1: HDR unresolved — not written to state.
    cache.delete_overlay_state(5173, state_table)
    cache.update_overlay_state(5173, "Overlay File (0) Rating1Fresh", state_table, "hashA", "7.3")
    # HDR skipped (unresolved)

    # Run 2: HDR now resolves.
    _write_state(cache, state_table, 5173, {
        "Overlay File (0) Rating1Fresh": ("hashA", "7.3"),
        "Overlay File (0) HDR":          ("hashB", None),
    })
    states = cache.query_overlay_state(5173, state_table)
    assert "Overlay File (0) HDR" in states

    # Run 3: both in cache — no change.
    current_hashes = {"Overlay File (0) Rating1Fresh": "hashA", "Overlay File (0) HDR": "hashB"}
    assert _detect_change(states, current_hashes) == ""
