"""
Repository context management for CLI.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Optional

from ...core import PromptRepository
from ..utils import error


def get_repository(path: str = ".") -> Optional[PromptRepository]:
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

    Raises:
        FileExistsError: If repository already exists
        Exception: For other errors
    """
    return PromptRepository.init(path)
