"""
Tag storage operations.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from pathlib import Path
from typing import Optional

from ..models import ExperimentTag


class TagStorage:
    """Handles experiment tag persistence."""

    def __init__(self, tags_dir: Path):
        self.tags_dir = tags_dir

    def save(self, tag: ExperimentTag) -> None:
        """Save an experiment tag."""
        tag_path = self.tags_dir / f"{tag.name}.json"
        tag_path.write_text(tag.model_dump_json(indent=2))

    def load(self, tag_name: str) -> Optional[ExperimentTag]:
        """Load a tag by name."""
        tag_path = self.tags_dir / f"{tag_name}.json"
        if not tag_path.exists():
            return None

        data = json.loads(tag_path.read_text())
        return ExperimentTag(**data)

    def list_all(self) -> list[str]:
        """List all tag names."""
        if not self.tags_dir.exists():
            return []

        return [f.stem for f in self.tags_dir.glob("*.json")]
