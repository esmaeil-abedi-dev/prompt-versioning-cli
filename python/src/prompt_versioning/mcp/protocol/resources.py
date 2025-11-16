"""
MCP resource definitions.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from dataclasses import asdict

from .models import MCPResource


def get_resource_definitions() -> list[dict]:
    """Get all MCP resource definitions."""
    resources = [
        MCPResource(
            uri="promptvc://status",
            name="Repository Status",
            description="Current repository status",
            mimeType="application/json",
        ),
        MCPResource(
            uri="promptvc://history",
            name="Commit History",
            description="Full commit history",
            mimeType="application/json",
        ),
        MCPResource(
            uri="promptvc://tags",
            name="Experiment Tags",
            description="All experiment tags",
            mimeType="application/json",
        ),
    ]

    return [asdict(resource) for resource in resources]
