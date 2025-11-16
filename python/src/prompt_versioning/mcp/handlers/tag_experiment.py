"""
Tag experiment handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any


async def handle_tag_experiment(repo, args: dict[str, Any]) -> dict[str, Any]:
    """Tag an experiment."""
    if not repo or not repo.exists():
        return {"success": False, "error": "Repository not initialized"}

    name = args.get("name")
    version = args.get("version")
    metadata = args.get("metadata")

    try:
        tag = repo.tag(name, version, metadata)

        return {
            "success": True,
            "tag_name": tag.name,
            "commit_hash": tag.commit_hash,
            "metadata": tag.metadata,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
