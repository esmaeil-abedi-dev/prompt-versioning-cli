"""
Data models for prompt versioning.

Defines Pydantic models for prompts, commits, versions, and experiment tags.
These models ensure type safety and validation throughout the system.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    """
    Represents a prompt with its content and configuration.

    This model captures all aspects of an LLM prompt including system messages,
    user templates, and model parameters.
    """

    system: Optional[str] = Field(None, description="System message for the LLM")
    user_template: Optional[str] = Field(None, description="User message template with variables")
    assistant_prefix: Optional[str] = Field(None, description="Assistant message prefix")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: Optional[float] = Field(
        None, ge=-2.0, le=2.0, description="Frequency penalty"
    )
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    stop_sequences: Optional[list[str]] = Field(None, description="Stop sequences for generation")

    # Allow arbitrary fields for custom prompt formats
    model_config = {"extra": "allow"}

    def compute_hash(self) -> str:
        """
        Compute a deterministic hash of the prompt content.

        Returns:
            SHA-256 hash of the prompt data (first 16 characters)
        """
        # Sort keys for deterministic hashing
        content = json.dumps(self.model_dump(exclude_none=True), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class PromptCommit(BaseModel):
    """
    Represents a commit in the prompt history.

    Similar to Git commits, this captures a snapshot of a prompt at a point in time
    along with metadata about the change.
    """

    hash: str = Field(..., description="Unique commit hash")
    parent_hash: Optional[str] = Field(None, description="Hash of parent commit")
    message: str = Field(..., description="Commit message describing the change")
    author: str = Field(default="system", description="Author of the commit")
    timestamp: datetime = Field(default_factory=datetime.now, description="Commit timestamp")
    prompt_hash: str = Field(..., description="Hash of the prompt content")
    file_path: Optional[str] = Field(None, description="Path to the prompt file that was committed")
    tags: list[str] = Field(default_factory=list, description="Tags associated with this commit")

    def short_hash(self) -> str:
        """Return abbreviated commit hash (first 7 characters)."""
        return self.hash[:7]


class PromptVersion(BaseModel):
    """
    Combines a commit with its associated prompt data.

    This is the complete representation of a versioned prompt, linking
    the metadata (commit) with the actual content (prompt).
    """

    commit: PromptCommit
    prompt: Prompt

    def __str__(self) -> str:
        return f"Version {self.commit.short_hash()}: {self.commit.message}"


class ExperimentTag(BaseModel):
    """
    Tag for marking experiments with metadata.

    Used for A/B testing and tracking performance metrics across different
    prompt versions.
    """

    name: str = Field(..., description="Tag name (e.g., 'experiment-v2')")
    commit_hash: str = Field(..., description="Commit this tag points to")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Experiment metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Tag creation timestamp")

    def __str__(self) -> str:
        return f"Tag '{self.name}' -> {self.commit_hash[:7]}"


class AuditLogEntry(BaseModel):
    """
    Single entry in the compliance audit log.

    Captures all necessary information for regulatory compliance and
    change tracking.
    """

    timestamp: datetime
    action: str = Field(..., description="Action performed (commit, checkout, tag, etc.)")
    commit_hash: Optional[str] = Field(None, description="Related commit hash")
    prompt_hash: Optional[str] = Field(None, description="Hash of prompt content")
    message: str = Field(..., description="Description of the action")
    author: str = Field(..., description="User who performed the action")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional context")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "commit_hash": self.commit_hash,
            "prompt_hash": self.prompt_hash,
            "message": self.message,
            "author": self.author,
            "metadata": self.metadata,
        }
