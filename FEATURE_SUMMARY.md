#  Overlay Comparison Collector Feature — Complete

## Branch Created
- **Branch name**: `feature/overlay-comparison-collector`
- **Based on**: `nightly` (latest)
- **Commit**: `6c76b4f8`

## What Was Built

A test feature that collects all **overlay comparison strings** during a Kometa overlay run and writes them to a dated file for analysis.

### Code Changes

**File modified**: `modules/overlays.py` (+54 lines)

1. **Initialization** (line 24)
   ```python
   self.overlay_comparisons = []  # Initialize empty list
   ```

2. **Data Capture** (lines 218-231)
   - During the overlay application loop, after all change detection logic
   - Appends a dict with:
     - `item_title`: Display name
     - `item_key`: Plex rating key
     - `cached_overlay_compare`: What was cached from previous run
     - `current_compare_names`: Overlays being applied now
     - `overlay_change_reason`: Why change was/wasn't detected
     - `has_overlay_label`: Overlay label present?
     - `will_reapply`: Reapply flag enabled?
     - `has_new_backup`: New poster found?
     - `has_changed_image`: Poster hash changed?

3. **File Writer** (lines 594-639)
   ```python
   def _write_overlay_comparisons(self):
       """Write all overlay comparison strings to a dated file."""
   ```
   - Creates `config/overlay_comparisons/` directory
   - Filename: `{LibraryName}_YYYY-MM-DD_HH-MM-SS.txt`
   - Includes summary header + formatted per-item data
   - Called at end of `run_overlays()` before cleanup

### Example Output

```
Overlay Comparison Strings for Movies Library
Generated: 2025-06-13 14:30:45
Total items processed: 1024
====================================================================================================

[1] The Shawshank Redemption (Key: 12345)
  Cached overlay_compare: []
  Current compare_names keys: ['ratings', 'studios']
  Has overlay label: False
  Overlay change reason: No Overlay Label
  Will reapply: False
  Has new backup: False
  Changed image: False
====================================================================================================

[2] The Dark Knight (Key: 12346)
  Cached overlay_compare: ['ratings', 'studios']
  Current compare_names keys: ['ratings', 'studios']
  Has overlay label: True
  Overlay change reason: No change detected
  ...
```

## How to Test

```bash
# Verify you're on the new branch
git checkout feature/overlay-comparison-collector

# Run Kometa with overlays
python kometa.py --run --overlays-only

# Check output
ls -la config/overlay_comparisons/
cat config/overlay_comparisons/Movies_*.txt
```

## File Location

Output files: **`config/overlay_comparisons/`**

Format: `{LibraryName}_YYYY-MM-DD_HH-MM-SS.txt`

Example: `Movies_2025-06-13_14-30-45.txt`

## Why This Helps

This feature is designed to help debug the **overlay comparison logic**:

1. **See what comparisons are being made** — The exact `overlay_compare` strings from cache
2. **Understand change detection** — Why Kometa decides to reapply overlays
3. **Identify poster changes** — Track when `changed_image` flags are set
4. **Audit trail** — Timestamped records for analysis
5. **Spot patterns** — See which overlays/items trigger reapplication consistently

## Technical Notes

-  **No breaking changes** — Purely additive
-  **Minimal overhead** — Data collected during existing loops
-  **Error handling** — Logs warnings on write failure
-  **Per-library files** — Each library gets timestamped output
-  **UTF-8 encoded** — Safe for special characters
-  **Code style** — Passes black, isort, flake8

## Next Steps

1. Run a test on your config with overlays enabled
2. Review the generated comparison data
3. Look for patterns or unexpected comparison strings
4. Share findings if you want further investigation/refinement

---

**Status**: Ready to test! 

The feature is committed and waiting on `feature/overlay-comparison-collector` branch.
