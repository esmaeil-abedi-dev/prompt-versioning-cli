"""
File system operations for storage backend.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class FileSystemManager:
    """Manages file system structure and basic operations."""

    def __init__(self, repo_path: Path):
        """Initialize file system manager."""
        self.repo_path = Path(repo_path)
        self.prompt_vc_dir = self.repo_path / ".prompt-vc"

        # Define subdirectories
        self.commits_dir = self.prompt_vc_dir / "commits"
        self.prompts_dir = self.prompt_vc_dir / "prompts"
        self.tags_dir = self.prompt_vc_dir / "tags"

        # Define key files
        self.head_file = self.prompt_vc_dir / "HEAD"
        self.config_file = self.prompt_vc_dir / "config.json"
        self.audit_file = self.prompt_vc_dir / "audit.jsonl"

    def initialize(self) -> None:
        """
        Initialize the .prompt-vc directory structure.

        Raises:
            FileExistsError: If repository already exists
        """
        if self.prompt_vc_dir.exists():
            raise FileExistsError(f"Repository already exists at {self.repo_path}")

        # Create directory structure
        self.prompt_vc_dir.mkdir(parents=True)
        self.commits_dir.mkdir()
        self.prompts_dir.mkdir()
        self.tags_dir.mkdir()

        # Initialize HEAD (no commits yet)
        self.head_file.write_text("")

        # Initialize config
        config = {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
        }
        self.config_file.write_text(json.dumps(config, indent=2))

        # Create empty audit log
        self.audit_file.touch()

    def exists(self) -> bool:
        """Check if repository exists."""
        return self.prompt_vc_dir.exists() and self.head_file.exists()

    def get_head(self) -> Optional[str]:
        """Get the current HEAD commit hash."""
        if not self.head_file.exists():
            return None

        content = self.head_file.read_text().strip()
        return content if content else None

    def set_head(self, commit_hash: str) -> None:
        """Update HEAD to point to a commit."""
        self.head_file.write_text(commit_hash)
