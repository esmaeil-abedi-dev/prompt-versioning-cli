"""
Get status handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any, Optional


async def handle_get_status(repo: Optional[Any], args: dict[str, Any]) -> dict[str, Any]:
    """Get repository status."""
    if not repo or not repo.exists():
        return {
            "success": False,
            "initialized": False,
            "message": "Repository not initialized",
            "display": "❌ Repository not initialized. Run 'promptvc init' to create a new repository.",
        }

    try:
        current = repo.get_current_version()

        if not current:
            return {
                "success": True,
                "initialized": True,
                "has_commits": False,
                "message": "No commits yet",
                "display": "✓ Repository initialized\n❌ No commits yet. Use 'promptvc commit' to create your first commit.",
            }

        # Format tags
        tags_str = f"\nTags: {', '.join(current.commit.tags)}" if current.commit.tags else ""

        # Format display output
        display = f"""✓ Repository Status

Commit:     {current.commit.short_hash()}
Message:    {current.commit.message}
Author:     {current.commit.author}
Date:       {current.commit.timestamp.strftime('%Y-%m-%d %H:%M:%S')}{tags_str}"""

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
            "display": display,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "display": f"❌ Error: {str(e)}"}
