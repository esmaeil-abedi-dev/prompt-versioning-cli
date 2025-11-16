"""
Get history handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any


async def handle_get_history(repo, args: dict[str, Any]) -> dict[str, Any]:
    """Get commit history."""
    if not repo or not repo.exists():
        return {
            "success": False,
            "error": "Repository not initialized",
            "display": "❌ Repository not initialized. Run 'promptvc init' to create a new repository.",
        }

    max_count = args.get("max_count")

    try:
        versions = repo.log(max_count)

        history = []
        display_lines = ["📜 Commit History\n"]

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

            # Format display
            tags_str = f" [{', '.join(version.commit.tags)}]" if version.commit.tags else ""
            display_lines.append(
                f"• {version.commit.short_hash()} - {version.commit.message}{tags_str}\n"
                f"  {version.commit.author} | {version.commit.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        display = "\n\n".join(display_lines) if history else "No commits yet."

        return {"success": True, "count": len(history), "commits": history, "display": display}
    except Exception as e:
        return {"success": False, "error": str(e), "display": f"❌ Error: {str(e)}"}
