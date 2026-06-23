# Overlay Comparison Collector — UPDATED

## Status
Branch: `feature/overlay-comparison-collector`
Commits: 2
- `6c76b4f8` — Initial implementation
- `e4e500dd` — Refactored to show full overlay comparison strings

## What It Does

Captures **all overlay comparison strings** during overlay application and writes them to a dated file. The comparison strings show the complete overlay definitions (with text templates, colors, fonts, positioning, etc.).

## Output Location

Files are written to: `config/overlay_comparisons/`

**Filename format**: `{LibraryName}_YYYY-MM-DD_HH-MM-SS.txt`

Example: `Movies_2025-06-13_14-30-45.txt`

## Output Format

### Example Output

```
Overlay Comparison Strings for Movies Library
Generated: 2025-06-13 14:30:45
Total items processed: 1024
====================================================================================================

[1] The Shawshank Redemption (Key: 12345)
  Cached overlay_compare (from previous run):
    - text(<<critic_rating%>>)rating1_group100left3030topfonts/Inter-Bold.ttf63160160centertop15(255, 255, 255, 255)(0, 0, 0, 153)30150
    - studios_studio1_group0tahoma100tahoma50
    (empty list)

  Current compare_names (overlays to be applied):
    text(<<critic_rating%>>)rating1_group100left3030topfonts/Inter-Bold.ttf63160160centertop15(255, 255, 255, 255)(0, 0, 0, 153)30150
      -> Overlay File (0) Rating1Rotten
    studios_studio1_group0tahoma100tahoma50
      -> Overlay File (1) Studios

  Has overlay label: True
  Overlay change reason: No change detected
  Will reapply: False
  Has new backup: False
  Changed image: False
====================================================================================================

[2] The Dark Knight (Key: 12346)
  Cached overlay_compare (from previous run):
    (empty list)

  Current compare_names (overlays to be applied):
    text(<<critic_rating%>>)rating1_group100left3030topfonts/Inter-Bold.ttf63160160centertop15(255, 255, 255, 255)(0, 0, 0, 153)30150
      -> Overlay File (0) Rating1Rotten
    studios_studio1_group0tahoma100tahoma50
      -> Overlay File (1) Studios

  Has overlay label: False
  Overlay change reason: No Overlay Label
  Will reapply: False
  Has new backup: False
  Changed image: False
```

## What Each Field Shows

- **`item_title`**: The Plex item display name
- **`item_key`**: Plex rating key (unique identifier)
- **`Cached overlay_compare`**: Overlay comparison strings from the PREVIOUS run (what was cached)
  - Each line is a full overlay definition string
  - Includes text templates (like `<<critic_rating%>>`), colors, fonts, positioning, etc.
  - Empty list means no overlays were applied before
- **`Current compare_names`**: Overlay comparison strings for THIS run (what will be applied)
  - Shows the full comparison string
  - Maps to the overlay name (file & internal name)
  - Empty dict means no overlays are being applied now
- **`Has overlay label`**: Whether the item currently has the "overlay" Plex label
- **`Overlay change reason`**: Why Kometa decided to reapply (or not reapply) overlays
  - "No change detected" = cached and current are identical
  - "No Overlay Label" = item doesn't have overlay label yet
  - Other reasons like "studios not in ['ratings']" = mismatch between cached and current
- **`Will reapply`**: Is `reapply_overlays: true` enabled in config?
- **`Has new backup`**: Did Kometa find a new poster backup?
- **`Changed image`**: Did the poster image hash change?

## Why This Helps Debug

Perfect for investigating the poster update issue:

1. **See exactly what comparison strings look like** — The full overlay definition format
2. **Understand cache matching** — Compare cached vs. current strings
3. **Identify why overlays reapply** — Mismatch detection logic
4. **Track overlay changes** — See which overlays are being applied per item
5. **Audit trail** — Timestamped records for analysis

## How to Test

```bash
git checkout feature/overlay-comparison-collector
python kometa.py --run --overlays-only
```

Check output:
```bash
ls -la config/overlay_comparisons/
cat config/overlay_comparisons/Movies_*.txt
```

## Code Changes

**File**: `modules/overlays.py` (+70 lines total)

1. **Init**: Added `self.overlay_comparisons = []`

2. **Capture** (during overlay loop):
   - Appends dict with:
     - Item metadata (title, key)
     - **`current_compare_names_dict`**: Full dict mapping comparison strings to overlay names
     - `cached_overlay_compare`: List of cached comparison strings
     - Change detection details (reason, flags)

3. **Write** (new `_write_overlay_comparisons()` method):
   - Creates output directory
   - Writes formatted file with:
     - Cached strings (one per line, line-by-line format)
     - Current strings (with comparison_string -> overlay_name mapping)
     - Context metadata (labels, change reason, etc.)

## Notes

- **Minimal performance impact** — Data collected during existing loops
- **Full comparison strings preserved** — No truncation or abbreviation
- **Per-library files** — Each library gets timestamped output
- **Safe file writing** — UTF-8 encoded, exception handling
- **No breaking changes** — Purely diagnostic, doesn't affect normal operation

---

**Ready to test!** The feature is committed and waiting on the branch.
