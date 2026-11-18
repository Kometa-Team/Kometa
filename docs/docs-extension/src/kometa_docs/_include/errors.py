"""Errors raised by the include engine without a MkDocs dependency."""


class IncludeError(ValueError):
    """An include directive or its source could not be processed."""
