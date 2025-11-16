"""
Input validation utilities for CLI.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from pathlib import Path
from typing import Any

import yaml

from ...core.repository import PromptRepository
from .output import error


def validate_file_exists(file_path: str) -> Path:
    """Validate file exists and return Path object."""
    path = Path(file_path)
    if not path.exists():
        error(f"File not found: {file_path}")
    return path


def parse_prompt_file(file_path: str) -> tuple[dict[str, Any], str]:
    """
    Parse prompt file (YAML or JSON).

    Returns:
        Tuple of (prompt_data, file_format)
    """
    path = validate_file_exists(file_path)
    content = path.read_text()

    if file_path.endswith((".yaml", ".yml")):
        try:
            data = yaml.safe_load(content)
            return data, "yaml"
        except yaml.YAMLError as e:
            error(f"Invalid YAML: {e}")

    elif file_path.endswith(".json"):
        try:
            data = json.loads(content)
            return data, "json"
        except json.JSONDecodeError as e:
            error(f"Invalid JSON: {e}")

    else:
        error("File must be YAML (.yaml, .yml) or JSON (.json)")


def parse_json_string(json_str: str, field_name: str = "JSON") -> dict[str, Any]:
    """Parse JSON string and handle errors."""
    try:
        data: dict[str, Any] = json.loads(json_str)
        return data
    except json.JSONDecodeError:
        error(f"Invalid {field_name}")


def ensure_repository(path: str = ".") -> PromptRepository:
    """Ensure a repository exists at the path.

    Returns:
        PromptRepository instance

    Raises:
        Exits with error if repository doesn't exist
    """
    from ..core import get_repository

    repo = get_repository(path)
    if not repo or not repo.exists():
        error(f"No repository found at {path}. Run 'prompt init' first.")
    return repo
