"""
List tags handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any


async def handle_list_tags(repo, args: dict[str, Any]) -> dict[str, Any]:
    """List all tags."""
    if not repo or not repo.exists():
        return {"success": False, "error": "Repository not initialized"}

    try:
        tags = repo.list_tags()

        tag_list = []
        for tag in tags:
            tag_list.append(
                {
                    "name": tag.name,
                    "commit_hash": tag.commit_hash,
                    "created_at": tag.created_at.isoformat(),
                    "metadata": tag.metadata,
                }
            )

        return {"success": True, "count": len(tag_list), "tags": tag_list}
    except Exception as e:
        return {"success": False, "error": str(e)}
