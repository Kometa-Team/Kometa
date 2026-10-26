# Adapted from the Kometa include-markdown fork; see LICENSE and NOTICE in docs/docs-extension.
"""Module for placeholders processing."""

# Placeholders (taken from Python-Markdown)
from __future__ import annotations

STX = "\u0002"
""" "Start of Text" marker for placeholder templates. """
ETX = "\u0003"
""" "End of Text" marker for placeholder templates. """
INLINE_PLACEHOLDER_PREFIX = f"{STX}klzzwxh:"


def build_placeholder(num: int) -> str:
    """Return a placeholder."""
    return f"{INLINE_PLACEHOLDER_PREFIX}{num}{ETX}"


def escape_placeholders(text: str) -> str:
    """Escape placeholders in the given text."""
    return text.replace(STX, f"\\{STX}").replace(ETX, f"\\{ETX}")


def unescape_placeholders(text: str) -> str:
    """Unescape placeholders in the given text."""
    return text.replace(f"\\{STX}", STX).replace(f"\\{ETX}", ETX)


def save_placeholder(
    placeholders_contents: list[tuple[str, str]],
    text_to_include: str,
) -> str:
    """Save the included text and return the placeholder."""
    inclusion_index = len(placeholders_contents)
    placeholder = build_placeholder(inclusion_index)
    placeholders_contents.append((placeholder, text_to_include))
    return placeholder
