"""
MCP tool definitions and schemas.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from dataclasses import asdict

from .models import MCPTool


def get_tool_definitions() -> list[dict]:
    """Get all MCP tool definitions."""
    tools = [
        MCPTool(
            name="promptvc_init_repository",
            description="Initialize a new prompt version control repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Repository path (default: current directory)",
                    }
                },
            },
        ),
        MCPTool(
            name="promptvc_commit",
            description="Commit a prompt to the repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message"},
                    "prompt": {
                        "type": "object",
                        "description": "Prompt data (system, user_template, etc.)",
                    },
                    "author": {"type": "string", "description": "Commit author (default: system)"},
                },
                "required": ["message", "prompt"],
            },
        ),
        MCPTool(
            name="promptvc_get_history",
            description="Get commit history",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_count": {
                        "type": "integer",
                        "description": "Maximum number of commits to return",
                    }
                },
            },
        ),
        MCPTool(
            name="promptvc_diff",
            description="Compare two prompt versions",
            inputSchema={
                "type": "object",
                "properties": {
                    "version1": {
                        "type": "string",
                        "description": "First version hash or reference (e.g., HEAD~1)",
                    },
                    "version2": {
                        "type": "string",
                        "description": "Second version hash or reference (e.g., HEAD)",
                    },
                },
                "required": ["version1", "version2"],
            },
        ),
        MCPTool(
            name="promptvc_checkout",
            description="Checkout a specific version",
            inputSchema={
                "type": "object",
                "properties": {
                    "version": {"type": "string", "description": "Version hash or reference"}
                },
                "required": ["version"],
            },
        ),
        MCPTool(
            name="promptvc_tag",
            description="Tag a version for experiment tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Tag name"},
                    "version": {"type": "string", "description": "Version hash (default: HEAD)"},
                    "metadata": {"type": "object", "description": "Experiment metadata"},
                },
                "required": ["name"],
            },
        ),
        MCPTool(
            name="promptvc_list_tags",
            description="List all experiment tags",
            inputSchema={"type": "object", "properties": {}},
        ),
        MCPTool(
            name="promptvc_get_status",
            description="Get repository status",
            inputSchema={"type": "object", "properties": {}},
        ),
        MCPTool(
            name="promptvc_generate_audit",
            description="Generate compliance audit log",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["json", "csv"],
                        "description": "Output format (default: json)",
                    }
                },
            },
        ),
        MCPTool(
            name="promptvc_rollback",
            description="Rollback to a previous version",
            inputSchema={
                "type": "object",
                "properties": {
                    "version": {
                        "type": "string",
                        "description": "Version hash or reference to rollback to",
                    }
                },
                "required": ["version"],
            },
        ),
    ]

    return [asdict(tool) for tool in tools]
