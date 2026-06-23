# Overlay Comparison Collector — Test Feature

## Overview

This branch (`feature/overlay-comparison-collector`) adds functionality to collect and log all overlay comparison strings during a Kometa run.

## What It Does

When overlays are applied, Kometa compares the cached overlay state with the current overlay configuration to determine if changes are needed. This feature captures those comparison strings and writes them to a dated file for analysis.

## Output Location

Files are written to: `config/overlay_comparisons/`

**Filename format**: `{LibraryName}_YYYY-MM-DD_HH-MM-SS.txt`

Example: `Movies_2025-06-13_14-30-45.txt`

## Output Format

Each file contains:
- Header with library name and generation timestamp
- Total count of items processed
- Per-item comparison data:
  - **Item Title & Key**: The Plex item identifier
  - **Cached overlay_compare**: The overlay state from the cache (list of comparison strings)
  - **Current compare_names keys**: The overlay names being applied now
  - **Has overlay label**: Whether item has the "overlay" label in Plex
  - **Overlay change reason**: Why an overlay change was detected (or "No change detected")
  - **Will reapply**: Whether reapply_overlays is enabled
  - **Has new backup**: Whether a new poster backup was found
  - **Changed image**: Whether the poster image hash changed

## Example Output

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
----------------------------------------------------------------------------------------------------

[2] The Dark Knight (Key: 12346)
  Cached overlay_compare: ['ratings', 'studios']
  Current compare_names keys: ['ratings', 'studios']
  Has overlay label: True
  Overlay change reason: No change detected
  Will reapply: False
  Has new backup: False
  Changed image: False
----------------------------------------------------------------------------------------------------

[3] Inception (Key: 12347)
  Cached overlay_compare: ['ratings']
  Current compare_names keys: ['ratings', 'studios']
  Has overlay label: True
  Overlay change reason: studios not in ['ratings']
  Will reapply: False
  Has new backup: False
  Changed image: False
```

## Code Changes

### `modules/overlays.py`

1. **`Overlays.__init__`**
   - Added `self.overlay_comparisons = []` to store comparison data per item

2. **Overlay application loop** (lines ~218-231)
   - After all overlay change detection logic completes
   - Appends a dict with comparison metadata for each item processed

3. **`_write_overlay_comparisons()` method** (new, lines ~594-639)
   - Called at end of `run_overlays()` before cleanup
   - Creates `config/overlay_comparisons/` directory if needed
   - Writes dated file with formatted comparison data
   - Includes error handling (warnings on write failure)

## Use Cases

This feature is useful for:

1. **Debugging overlay logic**
   - Understand why overlays are/aren't being updated
   - Identify cache inconsistencies
   - Spot patterns in overlay change detection

2. **Performance analysis**
   - See which overlays require reapplication
   - Identify items with changing posters

3. **Audit trail**
   - Track which overlays were considered per item
   - Timestamped records for each run

## Running a Test

```bash
git checkout feature/overlay-comparison-collector
python kometa.py --run --overlays-only
```

Check `config/overlay_comparisons/` for the output file. The path will be logged during the run:

```
Overlay comparison strings written to: /path/to/config/overlay_comparisons/Movies_2025-06-13_14-30-45.txt
```

## Notes

- **No breaking changes**: This is purely additive; existing functionality is unaffected
- **Minimal performance impact**: Data is collected during existing loops, just appended to a list
- **Safe file writing**: Uses UTF-8 encoding, handles exceptions gracefully
- **Per-library files**: Each library gets its own timestamped file
- **Automatic cleanup not implemented**: Old files remain; consider manual cleanup if collecting multiple runs

## Related Issue

This feature was created to support investigation of the poster update detection logic. The comparison strings help identify when and why Kometa decides overlays need reapplication.
