"""
Generate audit handler.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Any


async def handle_generate_audit(repo, args: dict[str, Any]) -> dict[str, Any]:
    """Generate audit log."""
    if not repo or not repo.exists():
        return {"success": False, "error": "Repository not initialized"}

    format_type = args.get("format", "json")

    try:
        audit_data = repo.audit_log(format=format_type)

        return {"success": True, "format": format_type, "data": audit_data}
    except Exception as e:
        return {"success": False, "error": str(e)}
