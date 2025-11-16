"""
List tags handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any, Optional


async def handle_list_tags(repo: Optional[Any], args: dict[str, Any]) -> dict[str, Any]:
    """List all tags."""
    if not repo or not repo.exists():
        return {
            "success": False,
            "error": "Repository not initialized",
            "display": "❌ Repository not initialized. Run 'promptvc init' to create a new repository.",
        }

    try:
        tags = repo.list_tags()

        tag_list = []
        display_lines = ["🏷️  Experiment Tags\n"]

        for tag in tags:
            tag_list.append(
                {
                    "name": tag.name,
                    "commit_hash": tag.commit_hash,
                    "created_at": tag.created_at.isoformat(),
                    "metadata": tag.metadata,
                }
            )

            # Format display
            metadata_str = f" | {tag.metadata}" if tag.metadata else ""
            display_lines.append(
                f"• {tag.name} → {tag.commit_hash[:8]}\n"
                f"  Created: {tag.created_at.strftime('%Y-%m-%d %H:%M:%S')}{metadata_str}"
            )

        display = (
            "\n\n".join(display_lines)
            if tag_list
            else "No tags yet. Use 'promptvc tag' to create experiment tags."
        )

        return {"success": True, "count": len(tag_list), "tags": tag_list, "display": display}
    except Exception as e:
        return {"success": False, "error": str(e), "display": f"❌ Error: {str(e)}"}
