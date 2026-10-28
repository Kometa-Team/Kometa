"""Shared parsing for library schedule modes."""

import re
from datetime import timedelta

_ADDED_MODE = re.compile(r"added\((0*[1-9][0-9]*)([mhd]?)\)", re.IGNORECASE)


def cached_item_key(key):
    """Restore numeric Plex keys while preserving other servers' string IDs."""
    value = str(key)
    return int(value) if value.isascii() and value.isdecimal() else value


def parse_added_duration(mode: str) -> timedelta:
    """Return the lookback for added(N[m|h|d]); bare N means days."""
    match = _ADDED_MODE.fullmatch(mode)
    if match is None:
        raise ValueError("expected added(<positive integer>[m|h|d]); no unit means days")
    amount, unit = match.groups()
    argument = {"m": "minutes", "h": "hours", "d": "days", "": "days"}[unit.lower()]
    try:
        return timedelta(**{argument: int(amount)})
    except OverflowError as error:
        raise ValueError("added duration is too large") from error
