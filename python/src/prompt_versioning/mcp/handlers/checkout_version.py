"""
Checkout version handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any, Optional


async def handle_checkout_version(repo: Optional[Any], args: dict[str, Any]) -> dict[str, Any]:
    """Checkout a version."""
    if not repo or not repo.exists():
        return {"success": False, "error": "Repository not initialized"}

    version = args.get("version")

    try:
        checked_out = repo.checkout(version)

        return {
            "success": True,
            "hash": checked_out.commit.hash,
            "short_hash": checked_out.commit.short_hash(),
            "message": checked_out.commit.message,
            "prompt": checked_out.prompt.model_dump(exclude_none=True),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
