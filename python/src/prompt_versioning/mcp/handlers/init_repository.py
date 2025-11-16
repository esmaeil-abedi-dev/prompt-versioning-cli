"""
MCP server base handlers.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any


async def handle_init_repository(repo, args: dict[str, Any], repo_path=None, server=None) -> dict[str, Any]:
    """Initialize repository."""
    from pathlib import Path

    from ...core import PromptRepository

    # Use provided path or repo_path from server, fallback to current directory
    path = args.get("path") or repo_path or "."

    try:
        PromptRepository.init(path)

        # Reload server's repo reference if server instance is provided
        if server is not None:
            try:
                server.repo = PromptRepository(path)
            except Exception:
                pass

        return {
            "success": True,
            "message": f"Repository initialized at {Path(path).resolve()}",
            "path": str(Path(path).resolve()),
        }
    except FileExistsError:
        return {"success": False, "error": "Repository already exists"}
    except Exception as e:
        return {"success": False, "error": str(e)}
