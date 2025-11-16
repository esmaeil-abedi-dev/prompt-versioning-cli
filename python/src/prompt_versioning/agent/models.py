"""
Data models for the LLM agent.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class ConversationMessage:
    """A single message in the conversation history."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from the LLM agent."""

    message: str
    command: Optional[str] = None
    command_args: Optional[dict[str, Any]] = None
    needs_confirmation: bool = False
    error: Optional[str] = None
