"""
Prompt Versioning CLI - Git-like version control for LLM prompts.

This package provides tools for versioning, diffing, and auditing prompt changes
with a familiar Git-like interface.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from .core import (
    ExperimentTag,
    Prompt,
    PromptCommit,
    PromptRepository,
    PromptVersion,
    StorageBackend,
)
from .utils import DiffResult, PromptDiff

__version__ = "1.0.0"
__all__ = [
    "PromptRepository",
    "Prompt",
    "PromptCommit",
    "PromptVersion",
    "ExperimentTag",
    "StorageBackend",
    "PromptDiff",
    "DiffResult",
]
