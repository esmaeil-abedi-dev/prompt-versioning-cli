"""
Repository context management for CLI.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from ...core import PromptRepository
from ..utils import error


def get_repository(path: str = ".") -> PromptRepository:
    """
    Get repository instance with error handling.

    Args:
        path: Repository path

    Returns:
        PromptRepository instance
    """
    try:
        return PromptRepository(path)
    except Exception as e:
        error(f"Error: {e}")


def init_repository(path: str = ".") -> PromptRepository:
    """
    Initialize repository with error handling.

    Args:
        path: Repository path

    Returns:
        Initialized PromptRepository instance
    """
    try:
        return PromptRepository.init(path)
    except FileExistsError:
        error("Repository already exists")
    except Exception as e:
        error(f"Error: {e}")
