"""
Version operations for prompt repository (diff, checkout).

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Callable, Optional

from ...utils.diff import DiffResult, PromptDiff
from ..models import PromptVersion
from ..storage import StorageBackend


class VersionOperations:
    """Handles version-related operations (diff, checkout)."""

    def __init__(self, storage: StorageBackend, resolve_ref: Callable[[str], Optional[str]]):
        self.storage = storage
        self.resolve_ref = resolve_ref

    def diff(self, commit1_ref: str, commit2_ref: str) -> DiffResult:
        """
        Compare two commits.

        Args:
            commit1_ref: First commit hash (or prefix)
            commit2_ref: Second commit hash (or prefix)

        Returns:
            DiffResult showing changes

        Raises:
            ValueError: If commits not found
        """
        # Resolve commit references (support short hashes)
        hash1 = self.resolve_ref(commit1_ref)
        hash2 = self.resolve_ref(commit2_ref)

        if not hash1:
            raise ValueError(f"Commit not found: {commit1_ref}")
        if not hash2:
            raise ValueError(f"Commit not found: {commit2_ref}")

        # Load commits and prompts
        commit1 = self.storage.load_commit(hash1)
        commit2 = self.storage.load_commit(hash2)

        if not commit1 or not commit2:
            raise ValueError("Failed to load commits")

        prompt1 = self.storage.load_prompt(commit1.prompt_hash)
        prompt2 = self.storage.load_prompt(commit2.prompt_hash)

        if not prompt1 or not prompt2:
            raise ValueError("Failed to load prompt content")

        # Compute diff
        return PromptDiff.compare(prompt1, prompt2)

    def checkout(self, commit_ref: str) -> PromptVersion:
        """
        Checkout a specific commit (revert HEAD to this commit).

        Args:
            commit_ref: Commit hash (or prefix) to checkout

        Returns:
            PromptVersion of the checked-out commit

        Raises:
            ValueError: If commit not found
        """
        # Resolve commit reference
        commit_hash = self.resolve_ref(commit_ref)

        if not commit_hash:
            raise ValueError(f"Commit not found: {commit_ref}")

        # Load commit
        commit = self.storage.load_commit(commit_hash)
        if not commit:
            raise ValueError(f"Failed to load commit: {commit_hash}")

        # Update HEAD
        self.storage.set_head(commit_hash)

        # Log action
        self.storage.log_action(
            action="checkout",
            message=f"Checked out commit {commit.short_hash()}",
            commit_hash=commit_hash,
        )

        # Load and return version
        prompt = self.storage.load_prompt(commit.prompt_hash)
        return PromptVersion(commit=commit, prompt=prompt)
