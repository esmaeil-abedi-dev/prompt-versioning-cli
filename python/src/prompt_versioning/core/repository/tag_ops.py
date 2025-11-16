"""
Tag operations for prompt repository.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from datetime import datetime
from typing import Any, Callable, Optional

from ..models import ExperimentTag
from ..storage import StorageBackend


class TagOperations:
    """Handles tag-related operations."""

    def __init__(self, storage: StorageBackend, resolve_ref: Callable[[str], Optional[str]]):
        self.storage = storage
        self.resolve_ref = resolve_ref

    def create_tag(
        self, name: str, commit_ref: Optional[str] = None, metadata: Optional[dict[str, Any]] = None
    ) -> ExperimentTag:
        """
        Create a tag for an experiment.

        Args:
            name: Tag name (e.g., 'experiment-v2')
            commit_ref: Commit to tag (defaults to HEAD)
            metadata: Experiment metadata (metrics, config, etc.)

        Returns:
            Created ExperimentTag

        Raises:
            ValueError: If commit not found
        """
        # Default to HEAD if no commit specified
        if commit_ref is None:
            commit_hash = self.storage.get_head()
            if not commit_hash:
                raise ValueError("No commits exist yet")
        else:
            commit_hash = self.resolve_ref(commit_ref)
            if not commit_hash:
                raise ValueError(f"Commit not found: {commit_ref}")

        # Create tag
        tag = ExperimentTag(
            name=name,
            commit_hash=commit_hash,
            metadata=metadata or {},
            created_at=datetime.now(),
        )

        # Save tag
        self.storage.save_tag(tag)

        # Update commit to include tag
        commit = self.storage.load_commit(commit_hash)
        if commit and name not in commit.tags:
            commit.tags.append(name)
            self.storage.save_commit(commit)

        # Log action
        self.storage.log_action(
            action="tag",
            message=f"Created tag '{name}'",
            commit_hash=commit_hash,
            metadata=metadata,
        )

        return tag

    def get_tag(self, tag_name: str) -> Optional[ExperimentTag]:
        """
        Get a tag by name.

        Args:
            tag_name: Name of the tag

        Returns:
            ExperimentTag or None if not found
        """
        return self.storage.load_tag(tag_name)

    def list_tags(self) -> list[ExperimentTag]:
        """
        List all tags.

        Returns:
            List of ExperimentTag objects
        """
        tag_names = self.storage.list_tags()
        tags = []
        for name in tag_names:
            tag = self.storage.load_tag(name)
            if tag:
                tags.append(tag)
        return tags
