"""
Get status handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any


async def handle_get_status(repo, args: dict[str, Any]) -> dict[str, Any]:
    """Get repository status."""
    if not repo or not repo.exists():
        return {"success": False, "initialized": False, "message": "Repository not initialized"}

    try:
        current = repo.get_current_version()

        if not current:
            return {
                "success": True,
                "initialized": True,
                "has_commits": False,
                "message": "No commits yet",
            }

        return {
            "success": True,
            "initialized": True,
            "has_commits": True,
            "current_commit": {
                "hash": current.commit.hash,
                "short_hash": current.commit.short_hash(),
                "message": current.commit.message,
                "author": current.commit.author,
                "timestamp": current.commit.timestamp.isoformat(),
                "tags": current.commit.tags,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
