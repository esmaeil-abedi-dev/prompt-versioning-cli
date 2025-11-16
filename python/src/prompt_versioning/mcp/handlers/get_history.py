"""
Get history handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any


async def handle_get_history(repo, args: dict[str, Any]) -> dict[str, Any]:
    """Get commit history."""
    if not repo or not repo.exists():
        return {"success": False, "error": "Repository not initialized"}

    max_count = args.get("max_count")

    try:
        versions = repo.log(max_count)

        history = []
        for version in versions:
            history.append(
                {
                    "hash": version.commit.hash,
                    "short_hash": version.commit.short_hash(),
                    "message": version.commit.message,
                    "author": version.commit.author,
                    "timestamp": version.commit.timestamp.isoformat(),
                    "tags": version.commit.tags,
                }
            )

        return {"success": True, "count": len(history), "commits": history}
    except Exception as e:
        return {"success": False, "error": str(e)}
