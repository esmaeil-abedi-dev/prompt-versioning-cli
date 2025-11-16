"""
Commit operations for prompt repository.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import hashlib
from datetime import datetime
from typing import Any, Optional, Union

from ..models import Prompt, PromptCommit, PromptVersion
from ..storage import StorageBackend


class CommitOperations:
    """Handles commit-related operations."""

    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def create_commit(
        self, message: str, prompt_data: Union[dict[str, Any], Prompt], author: str = "system", file_path: Optional[str] = None
    ) -> PromptCommit:
        """
        Create a new commit with the given prompt.

        Args:
            message: Commit message describing the change
            prompt_data: Prompt data (dict or Prompt object)
            author: Author of the commit
            file_path: Path to the file being committed (optional)

        Returns:
            Created PromptCommit object

        Raises:
            ValueError: If repository doesn't exist
        """
        if not self.storage.exists():
            raise ValueError("Repository not initialized. Run 'promptvc init' first.")

        # Convert dict to Prompt if needed
        if isinstance(prompt_data, dict):
            prompt = Prompt(**prompt_data)
        else:
            prompt = prompt_data

        # Save prompt content and get hash
        prompt_hash = self.storage.save_prompt(prompt)

        # Get parent commit (current HEAD)
        parent_hash = self.storage.get_head()

        # Generate commit hash (based on content + metadata)
        commit_data = f"{prompt_hash}{message}{author}{datetime.now().isoformat()}"
        commit_hash = hashlib.sha256(commit_data.encode()).hexdigest()[:16]

        # Create commit object
        commit = PromptCommit(
            hash=commit_hash,
            parent_hash=parent_hash,
            message=message,
            author=author,
            timestamp=datetime.now(),
            prompt_hash=prompt_hash,
            file_path=file_path,
        )

        # Save commit and update HEAD
        self.storage.save_commit(commit)
        self.storage.set_head(commit_hash)

        # Log to audit trail
        self.storage.log_action(
            action="commit",
            message=message,
            commit_hash=commit_hash,
            prompt_hash=prompt_hash,
            author=author,
        )

        return commit

    def get_history(self, max_count: Optional[int] = None) -> list[PromptVersion]:
        """
        Get commit history.

        Args:
            max_count: Maximum number of commits to return (None for all)

        Returns:
            List of PromptVersion objects (newest first)
        """
        if not self.storage.exists():
            return []

        commit_hashes = self.storage.list_commits()

        if max_count:
            commit_hashes = commit_hashes[:max_count]

        versions = []
        for commit_hash in commit_hashes:
            commit = self.storage.load_commit(commit_hash)
            if commit:
                prompt = self.storage.load_prompt(commit.prompt_hash)
                if prompt:
                    versions.append(PromptVersion(commit=commit, prompt=prompt))

        return versions

    def get_current_version(self) -> Optional[PromptVersion]:
        """
        Get the current HEAD version.

        Returns:
            Current PromptVersion or None if no commits
        """
        head_hash = self.storage.get_head()
        if not head_hash:
            return None

        commit = self.storage.load_commit(head_hash)
        if not commit:
            return None

        prompt = self.storage.load_prompt(commit.prompt_hash)
        if not prompt:
            return None

        return PromptVersion(commit=commit, prompt=prompt)
