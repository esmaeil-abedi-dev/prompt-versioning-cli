"""
MCP handler for creating prompt files.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path
from typing import Any

import yaml


async def handle_create_prompt(repo, args: dict[str, Any], repo_path=None, server=None) -> dict[str, Any]:
    """
    Create or update a prompt YAML file.

    Args:
        file: Path to prompt file (default: prompts/<name>.yaml)
        name: Prompt name (for automatic file naming)
        system: System message
        user_template: User template message
        temperature: Temperature (0.0-2.0)
        max_tokens: Maximum tokens
        top_p: Top-p sampling (0.0-1.0)
        frequency_penalty: Frequency penalty (-2.0-2.0)
        presence_penalty: Presence penalty (-2.0-2.0)
        stop_sequences: Stop sequences (list)
        append: Append to existing file instead of creating new
        additional_fields: Any additional fields as a dictionary
    """
    try:
        # Get file path
        file_path = args.get("file")
        name = args.get("name")

        if not file_path and not name:
            return {"success": False, "error": "Either 'file' or 'name' must be provided"}

        if not file_path:
            file_path = f"prompts/{name}.yaml"

        # Resolve relative to repo_path if provided
        if repo_path:
            file_path = Path(repo_path) / file_path
        else:
            file_path = Path(file_path)

        # Check if file exists and handle append mode
        existing_data = {}
        append = args.get("append", False)

        if file_path.exists():
            if append:
                with open(file_path, "r") as f:
                    existing_data = yaml.safe_load(f) or {}
            elif not args.get("overwrite", False):
                return {
                    "success": False,
                    "error": f"File {file_path} already exists. Use 'append' or 'overwrite' option.",
                }

        # Build prompt data
        prompt_data = existing_data.copy()

        # Add provided fields
        field_mapping = {
            "system": "system",
            "user_template": "user_template",
            "assistant_prefix": "assistant_prefix",
            "temperature": "temperature",
            "max_tokens": "max_tokens",
            "top_p": "top_p",
            "frequency_penalty": "frequency_penalty",
            "presence_penalty": "presence_penalty",
            "stop_sequences": "stop_sequences",
        }

        for arg_name, field_name in field_mapping.items():
            if arg_name in args and args[arg_name] is not None:
                prompt_data[field_name] = args[arg_name]

        # Add any additional fields
        if "additional_fields" in args and isinstance(args["additional_fields"], dict):
            prompt_data.update(args["additional_fields"])

        # Validate minimum required fields
        if "system" not in prompt_data and "user_template" not in prompt_data:
            return {
                "success": False,
                "error": "Prompt must have at least 'system' or 'user_template' field",
            }

        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(file_path, "w") as f:
            yaml.dump(prompt_data, f, default_flow_style=False, sort_keys=False)

        # Read back for confirmation
        with open(file_path, "r") as f:
            file_contents = f.read()

        return {
            "success": True,
            "message": f"Prompt file {'updated' if append else 'created'}: {file_path}",
            "path": str(file_path.resolve()),
            "contents": file_contents,
            "data": prompt_data,
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to create prompt: {str(e)}"}
