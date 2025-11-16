"""
Prompt content storage operations.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from pathlib import Path
from typing import Optional

import yaml

from ..models import Prompt


class PromptStorage:
    """Handles prompt content persistence."""

    def __init__(self, prompts_dir: Path):
        self.prompts_dir = prompts_dir

    def save(self, prompt: Prompt) -> str:
        """
        Save prompt content to storage.

        Returns:
            Hash of the saved prompt
        """
        prompt_hash = prompt.compute_hash()
        prompt_path = self.prompts_dir / f"{prompt_hash}.yaml"

        # Don't overwrite if already exists (content-addressable storage)
        if not prompt_path.exists():
            content = prompt.model_dump(exclude_none=True)
            prompt_path.write_text(yaml.dump(content, sort_keys=True))

        return prompt_hash

    def load(self, prompt_hash: str) -> Optional[Prompt]:
        """Load a prompt by hash."""
        prompt_path = self.prompts_dir / f"{prompt_hash}.yaml"
        if not prompt_path.exists():
            return None

        data = yaml.safe_load(prompt_path.read_text())
        return Prompt(**data)
