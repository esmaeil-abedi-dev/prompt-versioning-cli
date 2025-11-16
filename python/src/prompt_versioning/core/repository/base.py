"""
Main PromptRepository class that orchestrates all operations.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path
from typing import Any, Optional, Union

from ...utils.diff import DiffResult
from ..models import ExperimentTag, Prompt, PromptCommit, PromptVersion
from ..storage import StorageBackend
from .audit_ops import AuditOperations
from .commit_ops import CommitOperations
from .ref_resolver import ReferenceResolver
from .tag_ops import TagOperations
from .version_ops import VersionOperations


class PromptRepository:
    """
    Main interface for prompt version control operations.

    Provides Git-like commands (init, commit, log, diff, checkout, tag) for
    managing prompt versions with full audit trails.
    """

    def __init__(self, repo_path: Union[str, Path]):
        """
        Initialize repository.

        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path)
        self.storage = StorageBackend(self.repo_path)

        # Initialize operation modules
        self._ref_resolver = ReferenceResolver(self.storage)
        self._commit_ops = CommitOperations(self.storage)
        self._version_ops = VersionOperations(self.storage, self._ref_resolver.resolve)
        self._tag_ops = TagOperations(self.storage, self._ref_resolver.resolve)
        self._audit_ops = AuditOperations(self.storage)

    @classmethod
    def init(cls, repo_path: Union[str, Path]) -> "PromptRepository":
        """
        Initialize a new prompt repository.

        Args:
            repo_path: Path where the repository should be created

        Returns:
            Initialized PromptRepository instance

        Raises:
            FileExistsError: If repository already exists
        """
        repo = cls(repo_path)
        repo.storage.initialize()
        return repo

    def exists(self) -> bool:
        """Check if repository exists and is valid."""
        return self.storage.exists()

    # ==================== Commit Operations ====================

    def commit(
        self, message: str, prompt_data: Union[dict[str, Any], Prompt], author: str = "system", file_path: Optional[str] = None
    ) -> PromptCommit:
        """Create a new commit with the given prompt."""
        return self._commit_ops.create_commit(message, prompt_data, author, file_path)

    def log(self, max_count: Optional[int] = None) -> list[PromptVersion]:
        """Get commit history."""
        return self._commit_ops.get_history(max_count)

    def get_current_version(self) -> Optional[PromptVersion]:
        """Get the current HEAD version."""
        return self._commit_ops.get_current_version()

    # ==================== Version Operations ====================

    def diff(self, commit1_ref: str, commit2_ref: str) -> DiffResult:
        """Compare two commits."""
        return self._version_ops.diff(commit1_ref, commit2_ref)

    def checkout(self, commit_ref: str) -> PromptVersion:
        """Checkout a specific commit."""
        return self._version_ops.checkout(commit_ref)

    # ==================== Tag Operations ====================

    def tag(
        self, name: str, commit_ref: Optional[str] = None, metadata: Optional[dict[str, Any]] = None
    ) -> ExperimentTag:
        """Create a tag for an experiment."""
        return self._tag_ops.create_tag(name, commit_ref, metadata)

    def get_tag(self, tag_name: str) -> Optional[ExperimentTag]:
        """Get a tag by name."""
        return self._tag_ops.get_tag(tag_name)

    def list_tags(self) -> list[ExperimentTag]:
        """List all tags."""
        return self._tag_ops.list_tags()

    # ==================== Audit Operations ====================

    def audit_log(self, format: str = "json") -> Union[str, list[dict[str, Any]]]:
        """Generate compliance audit log."""
        return self._audit_ops.generate_audit_log(format)
