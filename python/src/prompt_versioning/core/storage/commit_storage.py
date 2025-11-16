"""
Commit storage operations.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from pathlib import Path
from typing import Optional

from ..models import PromptCommit


class CommitStorage:
    """Handles commit persistence."""

    def __init__(self, commits_dir: Path):
        self.commits_dir = commits_dir

    def save(self, commit: PromptCommit) -> None:
        """Save a commit to storage."""
        commit_path = self.commits_dir / f"{commit.hash}.json"
        commit_path.write_text(commit.model_dump_json(indent=2))

    def load(self, commit_hash: str) -> Optional[PromptCommit]:
        """Load a commit by hash."""
        commit_path = self.commits_dir / f"{commit_hash}.json"
        if not commit_path.exists():
            return None

        data = json.loads(commit_path.read_text())
        return PromptCommit(**data)

    def list_all(self) -> list[str]:
        """List all commit hashes in chronological order (newest first)."""
        if not self.commits_dir.exists():
            return []

        # Load all commits and sort by timestamp
        commits = []
        for commit_file in self.commits_dir.glob("*.json"):
            commit_hash = commit_file.stem
            commit = self.load(commit_hash)
            if commit:
                commits.append(commit)

        # Sort by timestamp (newest first)
        commits.sort(key=lambda c: c.timestamp, reverse=True)
        return [c.hash for c in commits]

    def find_by_prefix(self, hash_prefix: str) -> Optional[str]:
        """Find a commit hash by prefix (like Git's short hash lookup)."""
        matches = []
        for commit_file in self.commits_dir.glob("*.json"):
            if commit_file.stem.startswith(hash_prefix):
                matches.append(commit_file.stem)

        # Return None if no match or ambiguous
        return matches[0] if len(matches) == 1 else None
