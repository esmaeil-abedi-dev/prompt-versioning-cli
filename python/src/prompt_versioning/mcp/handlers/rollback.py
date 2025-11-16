"""
Rollback handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any

from .checkout_version import handle_checkout_version


async def handle_rollback(repo, args: dict[str, Any]) -> dict[str, Any]:
    """Rollback to a previous version."""
    version = args.get("version")
    return await handle_checkout_version(repo, {"version": version})
