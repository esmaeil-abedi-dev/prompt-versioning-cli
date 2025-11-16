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
            name="promptvc_create_prompt",
            description="Create or update a prompt YAML file. Always provide a meaningful 'name' (e.g., 'customer-support-bot') or 'file' path to ensure readable filenames.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to prompt file (e.g., 'prompts/customer-bot.yaml'). If not provided, will use 'name' parameter.",
                    },
                    "name": {
                        "type": "string",
                        "description": "Meaningful prompt name for automatic file naming (e.g., 'support-bot', 'email-writer'). Will create file as 'prompts/<name>.yaml'.",
                    },
                    "system": {"type": "string", "description": "System message for the LLM"},
                    "user_template": {
                        "type": "string",
                        "description": "User message template with {variable} placeholders",
                    },
                    "assistant_prefix": {
                        "type": "string",
                        "description": "Assistant message prefix",
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Sampling temperature (0.0-2.0)",
                        "minimum": 0.0,
                        "maximum": 2.0,
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens to generate",
                        "minimum": 1,
                    },
                    "top_p": {
                        "type": "number",
                        "description": "Nucleus sampling parameter (0.0-1.0)",
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                    "frequency_penalty": {
                        "type": "number",
                        "description": "Frequency penalty (-2.0-2.0)",
                        "minimum": -2.0,
                        "maximum": 2.0,
                    },
                    "presence_penalty": {
                        "type": "number",
                        "description": "Presence penalty (-2.0-2.0)",
                        "minimum": -2.0,
                        "maximum": 2.0,
                    },
                    "stop_sequences": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Stop sequences for generation",
                    },
                    "append": {
                        "type": "boolean",
                        "description": "Append to existing file instead of creating new",
                        "default": False,
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Overwrite existing file without prompting",
                        "default": False,
                    },
                    "additional_fields": {
                        "type": "object",
                        "description": "Any additional custom fields",
                    },
                },
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
