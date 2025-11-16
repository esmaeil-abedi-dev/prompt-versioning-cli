"""
Commit prompt handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any


async def handle_commit_prompt(repo, args: dict[str, Any]) -> dict[str, Any]:
    """Commit a prompt."""
    if not repo or not repo.exists():
        return {"success": False, "error": "Repository not initialized"}

    message = args.get("message")
    prompt_data = args.get("prompt")
    file_path = args.get("file")
    author = args.get("author", "system")

    # Support file parameter - load YAML file if provided
    if file_path and not prompt_data:
        from pathlib import Path

        import yaml
        try:
            file_full_path = Path(repo.repo_path) / file_path
            with open(file_full_path) as f:
                prompt_data = yaml.safe_load(f)
        except FileNotFoundError:
            return {"success": False, "error": f"File not found: {file_path}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to load file: {e}"}

    try:
        commit = repo.commit(message, prompt_data, author)

        return {
            "success": True,
            "hash": commit.hash,
            "commit_hash": commit.hash,
            "short_hash": commit.short_hash(),
            "message": message,
            "author": author,
            "timestamp": commit.timestamp.isoformat(),
            "display": f"✅ Committed: {commit.short_hash()}\nMessage: {message}\nAuthor: {author}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
