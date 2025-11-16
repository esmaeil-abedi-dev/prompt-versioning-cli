"""
Diff versions handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any, Optional


async def handle_diff_versions(repo: Optional[Any], args: dict[str, Any]) -> dict[str, Any]:
    """Compare two versions."""
    if not repo or not repo.exists():
        return {
            "success": False,
            "error": "Repository not initialized",
            "display": "❌ Repository not initialized. Run 'promptvc init' to create a new repository.",
        }

    version1 = args.get("version1")
    version2 = args.get("version2")

    try:
        diff_result = repo.diff(version1, version2)
        diff_text = diff_result.format()

        if diff_result.has_changes():
            display = f"📊 Comparing {version1} → {version2}\n\n{diff_text}"
        else:
            display = f"✓ No changes between {version1} and {version2}"

        return {
            "success": True,
            "has_changes": diff_result.has_changes(),
            "diff_text": diff_text,
            "display": display,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "display": f"❌ Error: {str(e)}"}
