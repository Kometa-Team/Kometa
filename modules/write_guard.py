"""
Write Guard for Kometa Web UI

A minimal, isolated module that intercepts Plex write operations when dry-run mode is enabled.
This module only activates when KOMETA_DRY_RUN=true is set in the environment.

SAFETY: This module is designed to be completely transparent to existing CLI usage.
- When DRY_RUN is not enabled, all operations pass through unchanged
- When DRY_RUN is enabled, write operations are logged but not executed

Usage:
    # At the start of a run, call:
    from modules.write_guard import WriteGuard
    WriteGuard.initialize()

    # In write operations, wrap the call:
    if WriteGuard.can_write():
        # Perform write operation
    else:
        WriteGuard.log_blocked("operation_name", details)
"""

import os
from functools import wraps
from typing import Callable, Any, Optional

# Try to import the logger from Kometa's util module
try:
    from modules import util
    logger = util.logger
except ImportError:
    # Fallback for testing
    import logging
    logger = logging.getLogger("write_guard")


class WriteGuard:
    """
    Singleton class to manage write protection for Kometa.

    When dry-run mode is enabled:
    - All Plex write operations are blocked
    - Blocked operations are logged with details
    - The run completes without modifying Plex

    When dry-run mode is disabled:
    - All operations proceed normally
    - This class has zero overhead
    """

    _initialized: bool = False
    _dry_run: bool = False
    _blocked_operations: list = []

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize the Write Guard.
        Reads DRY_RUN setting from environment variable.
        """
        cls._dry_run = os.environ.get("KOMETA_DRY_RUN", "").lower() == "true"
        cls._initialized = True
        cls._blocked_operations = []

        if cls._dry_run:
            logger.info("")
            logger.info("=" * 60)
            logger.info("DRY RUN MODE ENABLED")
            logger.info("No changes will be made to Plex")
            logger.info("All write operations will be logged but not executed")
            logger.info("=" * 60)
            logger.info("")

    @classmethod
    def is_dry_run(cls) -> bool:
        """Check if dry-run mode is enabled."""
        if not cls._initialized:
            cls.initialize()
        return cls._dry_run

    @classmethod
    def can_write(cls) -> bool:
        """Check if write operations are allowed."""
        if not cls._initialized:
            cls.initialize()
        return not cls._dry_run

    @classmethod
    def log_blocked(cls, operation: str, details: str = "", item: Any = None) -> None:
        """
        Log a blocked write operation.

        Args:
            operation: Name of the operation (e.g., "edit_metadata", "upload_poster")
            details: Additional details about what would have been written
            item: The Plex item that would have been modified
        """
        item_str = ""
        if item:
            try:
                item_str = f" on '{item.title}'" if hasattr(item, "title") else f" on {item}"
            except Exception:
                item_str = ""

        message = f"[DRY RUN] Would {operation}{item_str}"
        if details:
            message += f": {details}"

        logger.info(message)

        cls._blocked_operations.append({
            "operation": operation,
            "details": details,
            "item": str(item) if item else None
        })

    @classmethod
    def get_blocked_operations(cls) -> list:
        """Get list of all blocked operations during this run."""
        return cls._blocked_operations.copy()

    @classmethod
    def get_summary(cls) -> dict:
        """Get a summary of blocked operations."""
        if not cls._blocked_operations:
            return {"total": 0, "by_operation": {}}

        by_operation = {}
        for op in cls._blocked_operations:
            name = op["operation"]
            by_operation[name] = by_operation.get(name, 0) + 1

        return {
            "total": len(cls._blocked_operations),
            "by_operation": by_operation
        }

    @classmethod
    def print_summary(cls) -> None:
        """Print a summary of blocked operations at the end of a dry run."""
        if not cls._dry_run:
            return

        summary = cls.get_summary()

        logger.info("")
        logger.info("=" * 60)
        logger.info("DRY RUN SUMMARY")
        logger.info("=" * 60)

        if summary["total"] == 0:
            logger.info("No write operations were attempted during this run.")
        else:
            logger.info(f"Total operations that would have been performed: {summary['total']}")
            logger.info("")
            logger.info("Operations by type:")
            for op_name, count in sorted(summary["by_operation"].items()):
                logger.info(f"  - {op_name}: {count}")

        logger.info("")
        logger.info("To apply these changes, run without --dry-run flag")
        logger.info("=" * 60)


def guard_write(operation_name: str):
    """
    Decorator to guard a write operation.

    When dry-run is enabled, the decorated function will:
    1. Log what would have been done
    2. Return None without executing the function

    When dry-run is disabled, the function executes normally.

    Usage:
        @guard_write("edit_metadata")
        def edit_query(self, item, edits, advanced=False):
            # ... original implementation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if WriteGuard.can_write():
                return func(*args, **kwargs)
            else:
                # Log the blocked operation
                item = args[1] if len(args) > 1 else kwargs.get("item")
                details = str(kwargs) if kwargs else str(args[2:]) if len(args) > 2 else ""
                WriteGuard.log_blocked(operation_name, details, item)
                return None
        return wrapper
    return decorator


def guard_write_async(operation_name: str):
    """
    Async version of guard_write decorator.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if WriteGuard.can_write():
                return await func(*args, **kwargs)
            else:
                item = args[1] if len(args) > 1 else kwargs.get("item")
                details = str(kwargs) if kwargs else str(args[2:]) if len(args) > 2 else ""
                WriteGuard.log_blocked(operation_name, details, item)
                return None
        return wrapper
    return decorator
