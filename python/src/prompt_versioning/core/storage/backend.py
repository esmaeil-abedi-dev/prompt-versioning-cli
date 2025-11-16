"""
Main storage backend that orchestrates all storage operations.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path
from typing import Any, Optional

from ..models import AuditLogEntry, ExperimentTag, Prompt, PromptCommit
from .audit_log import AuditLog
from .commit_storage import CommitStorage
from .filesystem import FileSystemManager
from .prompt_storage import PromptStorage
from .tag_storage import TagStorage


class StorageBackend:
    """
    Manages file-based storage for the prompt version control system.

    Directory structure:
    .prompt-vc/
        ├── HEAD                 # Current commit hash
        ├── config.json          # Repository configuration
        ├── commits/             # Commit metadata
        │   └── <hash>.json
        ├── prompts/             # Prompt content
        │   └── <hash>.yaml
        ├── tags/                # Experiment tags
        │   └── <name>.json
        └── audit.jsonl          # Audit log (JSON Lines format)
    """

    def __init__(self, repo_path: Path):
        """Initialize storage backend."""
        self.repo_path = Path(repo_path)

        # Initialize filesystem manager
        self._fs = FileSystemManager(repo_path)

        # Initialize specialized storage modules
        self._commits = CommitStorage(self._fs.commits_dir)
        self._prompts = PromptStorage(self._fs.prompts_dir)
        self._tags = TagStorage(self._fs.tags_dir)
        self._audit = AuditLog(self._fs.audit_file)

    # ==================== Repository Management ====================

    def initialize(self) -> None:
        """Initialize the .prompt-vc directory structure."""
        self._fs.initialize()
        # Log initialization
        self._audit.log_action("init", "Initialized prompt repository", author="system")

    def exists(self) -> bool:
        """Check if repository exists."""
        return self._fs.exists()

    # ==================== HEAD Management ====================

    def get_head(self) -> Optional[str]:
        """Get the current HEAD commit hash."""
        return self._fs.get_head()

    def set_head(self, commit_hash: str) -> None:
        """Update HEAD to point to a commit."""
        self._fs.set_head(commit_hash)

    # ==================== Commit Operations ====================

    def save_commit(self, commit: PromptCommit) -> None:
        """Save a commit to storage."""
        self._commits.save(commit)

    def load_commit(self, commit_hash: str) -> Optional[PromptCommit]:
        """Load a commit by hash."""
        return self._commits.load(commit_hash)

    def list_commits(self) -> list[str]:
        """List all commit hashes in chronological order (newest first)."""
        return self._commits.list_all()

    def find_commit_by_prefix(self, hash_prefix: str) -> Optional[str]:
        """Find a commit hash by prefix (like Git's short hash lookup)."""
        return self._commits.find_by_prefix(hash_prefix)

    # ==================== Prompt Operations ====================

    def save_prompt(self, prompt: Prompt) -> str:
        """Save prompt content to storage. Returns hash of the saved prompt."""
        return self._prompts.save(prompt)

    def load_prompt(self, prompt_hash: str) -> Optional[Prompt]:
        """Load a prompt by hash."""
        return self._prompts.load(prompt_hash)

    # ==================== Tag Operations ====================

    def save_tag(self, tag: ExperimentTag) -> None:
        """Save an experiment tag."""
        self._tags.save(tag)

    def load_tag(self, tag_name: str) -> Optional[ExperimentTag]:
        """Load a tag by name."""
        return self._tags.load(tag_name)

    def list_tags(self) -> list[str]:
        """List all tag names."""
        return self._tags.list_all()

    # ==================== Audit Operations ====================

    def log_action(
        self,
        action: str,
        message: str,
        commit_hash: Optional[str] = None,
        prompt_hash: Optional[str] = None,
        author: str = "system",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an action to the audit trail."""
        self._audit.log_action(action, message, commit_hash, prompt_hash, author, metadata)

    def read_audit_log(self) -> list[AuditLogEntry]:
        """Read the complete audit log."""
        return self._audit.read_all()
