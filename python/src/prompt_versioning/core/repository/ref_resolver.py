"""
Reference resolver for commit references.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from typing import Optional

from ..storage import StorageBackend


class ReferenceResolver:
    """Resolves commit references (HEAD, short hashes, etc.)."""

    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def resolve(self, ref: str) -> Optional[str]:
        """
        Resolve a commit reference to a full hash.

        Supports:
        - Full hashes
        - Short hashes (prefix matching)
        - Special refs like 'HEAD', 'HEAD~1', 'HEAD~2', etc.

        Args:
            ref: Commit reference string

        Returns:
            Full commit hash or None if not found
        """
        # Handle HEAD references
        if ref == "HEAD":
            return self.storage.get_head()
        elif ref.startswith("HEAD~"):
            try:
                steps_back = int(ref.split("~")[1])
                commits = self.storage.list_commits()
                if steps_back < len(commits):
                    return commits[steps_back]
            except (ValueError, IndexError):
                return None

        # Try exact match first
        commit = self.storage.load_commit(ref)
        if commit:
            return ref

        # Try prefix match
        return self.storage.find_commit_by_prefix(ref)
