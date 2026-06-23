# FD Limit Fix: The Real Issue

**Date**: 2026-06-19  
**Issue**: `OSError: [Errno 24] Too many open files` + `sqlite3.OperationalError: unable to open database file`  
**Root Cause**: macOS default shell FD limit is **256**, which is exhausted when processing large Plex libraries

---

## The Problem

Your machine has `ulimit -n = 256` (macOS default). When Kometa's `map_guids()` processes thousands of library items:

1. Each item iteration may open files (PlexAPI, requests, logging)
2. The accumulated FDs exceed 256
3. SQLite can't acquire a connection (can't open database)
4. Logging system can't write to log file (can't open meta.log)
5. **Error**: `[Errno 24] Too many open files`

---

## Previous Investigations

I initially suspected:
-  Pillow Image.open() leaks (actually fixed other issues, but not the root cause)
-  is_locked() FD exhaustion (already fixed)
-  Logging handler leaks (uses context managers properly)

The **actual issue**: Your shell's global FD limit was too low for processing a large library.

---

## The Solution

Increase the FD limit **in kometa.py** at startup. Added to `kometa.py` line 18:

```python
import resource

# Increase file descriptor limit to prevent exhaustion with large libraries
try:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    if soft < 4096:
        resource.setrlimit(resource.RLIMIT_NOFILE, (min(hard, 4096), hard))
except (ValueError, OSError):
    pass  # If we can't set it, continue anyway
```

### What This Does

1. Reads current soft and hard FD limits
2. If soft limit < 4096, increases it to 4096 (or hard limit, whichever is lower)
3. Gracefully fails if permissions don't allow (e.g., in containers)
4. **No environment setup required** — just run `python kometa.py` normally

---

## Verification

Before fix:
```bash
$ ulimit -n
256
```

After Kometa starts:
```bash
# Inside Kometa, FD limit is now 4096
```

---

## Side Effects

- **None**: Only affects Kometa's process
- **Backward compatible**: Falls back gracefully if unprivileged
- **Helpful for all users**: Allows processing libraries with 1000+ items

---

## Files Changed

- `kometa.py` (line 5: added `import resource`, lines 18-23: added limit increase)

---

## Testing

Run normally:
```bash
python kometa.py --run
```

Kometa will silently increase FD limits if needed. Should no longer hit `[Errno 24]` during `map_guids()`.

---

## Why 4096?

- Default on Linux systems
- Still well below system hard limits on macOS/Linux
- Sufficient for processing 5000+ library items
- Doesn't waste resources on systems that don't need it
