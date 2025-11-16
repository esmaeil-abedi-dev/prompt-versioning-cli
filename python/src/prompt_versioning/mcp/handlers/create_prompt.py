"""
MCP handler for creating prompt files.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import re
from pathlib import Path
from typing import Any, Optional

import yaml

# Default prompts directory
DEFAULT_PROMPTS_DIR = "prompts"


def _generate_meaningful_name(
    system_prompt: Optional[str] = None, user_template: Optional[str] = None
) -> str:
    """
    Generate a meaningful filename from prompt content.

    Args:
        system_prompt: The system prompt content
        user_template: The user template content

    Returns:
        A meaningful filename slug (e.g., "customer-support-bot")
    """
    # Try to extract meaningful words from system prompt first
    text = system_prompt or user_template or "prompt"

    # Extract key words (lowercase, alphanumeric, convert spaces/underscores to hyphens)
    words = re.findall(r"\b[a-z]+\b", text.lower())

    # Filter out common words and take first few meaningful ones
    stop_words = {
        "you",
        "are",
        "a",
        "an",
        "the",
        "is",
        "to",
        "for",
        "and",
        "or",
        "your",
        "with",
        "in",
        "on",
        "at",
    }
    meaningful_words = [w for w in words if w not in stop_words and len(w) > 2][:3]

    if meaningful_words:
        return "-".join(meaningful_words)

    return "prompt"


async def handle_create_prompt(
    repo: Optional[Any],
    args: dict[str, Any],
    repo_path: Optional[str] = None,
    server: Optional[Any] = None,
) -> dict[str, Any]:
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
            # Try to generate a meaningful name from prompt content
            system_prompt = args.get("system")
            user_template = args.get("user_template")

            if system_prompt or user_template:
                name = _generate_meaningful_name(system_prompt, user_template)
            else:
                return {
                    "success": False,
                    "error": "Either 'file' or 'name' must be provided, or include 'system' or 'user_template' to auto-generate a name",
                }

        if not file_path:
            file_path = f"{DEFAULT_PROMPTS_DIR}/{name}.yaml"

        # Resolve relative to repo_path if provided
        if repo_path:
            file_path = Path(repo_path) / file_path
        else:
            file_path = Path(file_path)

        # If the path doesn't include a directory and doesn't start with ./
        # automatically place it in the prompts directory
        if not file_path.parent.name and file_path.parent == Path("."):
            file_path = Path(DEFAULT_PROMPTS_DIR) / file_path

        # Check if file exists and handle append mode
        existing_data: dict[str, Any] = {}
        append = args.get("append", False)

        if file_path.exists():
            if append:
                with open(file_path) as f:
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
        with open(file_path) as f:
            file_contents = f.read()

        # Read back for confirmation
        with open(file_path) as f:
            file_contents = f.read()

        return {
            "success": True,
            "message": f"Prompt file {'updated' if append else 'created'}: {file_path}",
            "path": str(file_path.resolve()),
            "contents": file_contents,
            "data": prompt_data,
            "display": f"✅ Created prompt file: {file_path}\n\nContents:\n{file_contents}",
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to create prompt: {str(e)}"}
