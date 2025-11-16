"""
Main LLM-powered agent for conversational prompt versioning.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..core import PromptRepository
from .backends import AnthropicBackend, LLMBackend, OllamaBackend, OpenAIBackend
from .models import AgentResponse, ConversationMessage


class PromptVCAgent:
    """
    Main LLM-powered agent for conversational prompt versioning.

    Interprets natural language commands and translates them to promptvc operations.
    Maintains conversation context for multi-turn interactions.
    """

    SYSTEM_PROMPT = """You are an expert assistant for a Git-like prompt version control system called promptvc.

Your job is to help users manage their LLM prompts through natural language commands. You can:
- Initialize repositories (promptvc init)
- Commit prompts (promptvc commit -m "message" -f file.yaml)
- View history (promptvc log)
- Compare versions (promptvc diff hash1 hash2)
- Checkout versions (promptvc checkout hash)
- Tag experiments (promptvc tag name hash)

When a user asks you to do something, respond with:
1. A friendly confirmation of what you'll do
2. The exact command to execute (wrapped in ```command...```)
3. Any relevant context or warnings

For destructive operations (checkout, etc.), ask for confirmation first.

Current working directory: {cwd}
Repository status: {repo_status}

Be concise, helpful, and precise. Format commands clearly so they can be extracted and executed.
"""

    def __init__(
        self,
        backend: Optional[LLMBackend] = None,
        repo_path: str = ".",
        conversation_history: Optional[list[ConversationMessage]] = None,
    ):
        """
        Initialize the agent.

        Args:
            backend: LLM backend to use (auto-detects if None)
            repo_path: Path to the prompt repository
            conversation_history: Optional existing conversation to resume
        """
        self.backend = backend or self._auto_detect_backend()
        self.repo_path = Path(repo_path)
        self.conversation_history = conversation_history or []

        # Try to load repository
        self.repo: Optional[PromptRepository]
        try:
            self.repo = PromptRepository(repo_path)
            self.repo_exists = self.repo.exists()
        except Exception:
            self.repo = None
            self.repo_exists = False

    def _auto_detect_backend(self) -> LLMBackend:
        """Auto-detect available LLM backend."""
        # Try in order of preference
        backends = [
            ("OpenAI", lambda: OpenAIBackend()),
            ("Anthropic", lambda: AnthropicBackend()),
            ("Ollama", lambda: OllamaBackend()),
        ]

        for _name, factory in backends:
            try:
                backend = factory()
                if backend.is_available():
                    return backend
            except Exception:
                continue

        raise RuntimeError(
            "No LLM backend available. Please:\n"
            "1. Set OPENAI_API_KEY environment variable, or\n"
            "2. Set ANTHROPIC_API_KEY environment variable, or\n"
            "3. Install and run Ollama (https://ollama.ai)"
        )

    def _get_repo_status(self) -> str:
        """Get current repository status for system prompt."""
        if not self.repo_exists or not self.repo:
            return "Not initialized (needs 'promptvc init')"

        try:
            versions = self.repo.log(max_count=1)
            if versions:
                latest = versions[0]
                return f"Initialized, HEAD at {latest.commit.short_hash()}"
            else:
                return "Initialized, no commits yet"
        except Exception:
            return "Initialized"

    def _build_system_prompt(self) -> str:
        """Build system prompt with current context."""
        return self.SYSTEM_PROMPT.format(
            cwd=self.repo_path.resolve(), repo_status=self._get_repo_status()
        )

    def _extract_command(self, response: str) -> Optional[tuple[str, dict[str, Any]]]:
        """
        Extract command from LLM response.

        Looks for patterns like:
        - ```command promptvc init```
        - ```bash promptvc commit -m "message" -f file.yaml```

        Returns:
            Tuple of (command_string, parsed_args) or None
        """
        # Look for code blocks with commands
        pattern = r"```(?:command|bash|shell)?\s*(promptvc\s+[^`]+)```"
        match = re.search(pattern, response, re.IGNORECASE)

        if match:
            cmd = match.group(1).strip()
            # Parse command into structured format
            args = self._parse_command(cmd)
            return (cmd, args)

        return None

    def _parse_command(self, cmd: str) -> dict[str, Any]:
        """
        Parse promptvc command string into structured arguments.

        Example: "promptvc commit -m 'message' -f file.yaml"
        Returns: {"action": "commit", "message": "message", "file": "file.yaml"}
        """
        parts = cmd.split()
        if not parts or parts[0] != "promptvc":
            return {}

        result = {"action": parts[1] if len(parts) > 1 else None}

        # Simple argument parsing
        i = 2
        while i < len(parts):
            if parts[i].startswith("-"):
                flag = parts[i].lstrip("-")
                if i + 1 < len(parts) and not parts[i + 1].startswith("-"):
                    result[flag] = parts[i + 1].strip("'\"")
                    i += 2
                else:
                    result[flag] = "true"
                    i += 1
            else:
                i += 1

        return result

    def process_message(self, user_input: str) -> AgentResponse:
        """
        Process a user message and generate response.

        Args:
            user_input: Natural language command from user

        Returns:
            AgentResponse with message and optional command to execute
        """
        # Add user message to history
        self.conversation_history.append(ConversationMessage(role="user", content=user_input))

        # Build messages for LLM
        messages = [{"role": "system", "content": self._build_system_prompt()}]

        # Add conversation history (last 10 messages to avoid token limits)
        for msg in self.conversation_history[-10:]:
            if msg.role in ["user", "assistant"]:
                messages.append({"role": msg.role, "content": msg.content})

        try:
            # Generate response
            llm_response = self.backend.generate(messages, temperature=0.3)

            # Store assistant response
            self.conversation_history.append(
                ConversationMessage(role="assistant", content=llm_response)
            )

            # Extract command if present
            command_data = self._extract_command(llm_response)

            if command_data:
                cmd, args = command_data
                # Check if destructive operation needs confirmation
                needs_confirmation = args.get("action") in ["checkout", "init"]

                return AgentResponse(
                    message=llm_response,
                    command=cmd,
                    command_args=args,
                    needs_confirmation=needs_confirmation,
                )
            else:
                return AgentResponse(message=llm_response)

        except Exception as e:
            return AgentResponse(
                message="I encountered an error processing your request.", error=str(e)
            )

    def save_conversation(self, filepath: Path) -> None:
        """Save conversation history to JSON file."""
        data = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata,
            }
            for msg in self.conversation_history
        ]

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_conversation(
        cls, filepath: Path, backend: Optional[LLMBackend] = None, repo_path: str = "."
    ) -> "PromptVCAgent":
        """Load conversation history from JSON file."""
        with open(filepath) as f:
            data = json.load(f)

        history = [
            ConversationMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
                metadata=msg.get("metadata", {}),
            )
            for msg in data
        ]

        return cls(backend=backend, repo_path=repo_path, conversation_history=history)


def get_default_backend() -> LLMBackend:
    """
    Get the default LLM backend based on environment.

    Returns:
        Configured LLMBackend instance

    Raises:
        RuntimeError: If no backend is available
    """
    agent = PromptVCAgent(repo_path=".")
    return agent.backend
