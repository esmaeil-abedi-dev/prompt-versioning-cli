"""
Semantic diffing engine for prompts.

Provides intelligent comparison of prompts that goes beyond simple text diff,
highlighting changes in templates, parameters, and structure.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import difflib
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..core.models import Prompt


class ChangeType(Enum):
    """Type of change detected in a diff."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class FieldChange:
    """Represents a change to a specific field."""

    field_name: str
    change_type: ChangeType
    old_value: Any
    new_value: Any

    def __str__(self) -> str:
        """Format field change for display."""
        if self.change_type == ChangeType.ADDED:
            return f"+ {self.field_name}: {self.new_value}"
        elif self.change_type == ChangeType.REMOVED:
            return f"- {self.field_name}: {self.old_value}"
        elif self.change_type == ChangeType.MODIFIED:
            return f"~ {self.field_name}: {self.old_value} → {self.new_value}"
        else:
            return f"  {self.field_name}: {self.old_value}"


class DiffResult:
    """
    Contains the results of comparing two prompts.

    Provides both structured access to changes and formatted output
    for human consumption.
    """

    def __init__(self, prompt1: Prompt, prompt2: Prompt):
        """
        Initialize diff result.

        Args:
            prompt1: Original prompt
            prompt2: New prompt
        """
        self.prompt1 = prompt1
        self.prompt2 = prompt2
        self.changes: list[FieldChange] = []
        self._compute_changes()

    def _compute_changes(self) -> None:
        """Compute field-by-field changes between prompts."""
        data1 = self.prompt1.model_dump(exclude_none=True)
        data2 = self.prompt2.model_dump(exclude_none=True)

        # Get all unique fields
        all_fields = set(data1.keys()) | set(data2.keys())

        for field in sorted(all_fields):
            val1 = data1.get(field)
            val2 = data2.get(field)

            if val1 is None and val2 is not None:
                # Field added
                self.changes.append(
                    FieldChange(
                        field_name=field,
                        change_type=ChangeType.ADDED,
                        old_value=None,
                        new_value=val2,
                    )
                )
            elif val1 is not None and val2 is None:
                # Field removed
                self.changes.append(
                    FieldChange(
                        field_name=field,
                        change_type=ChangeType.REMOVED,
                        old_value=val1,
                        new_value=None,
                    )
                )
            elif val1 != val2:
                # Field modified
                self.changes.append(
                    FieldChange(
                        field_name=field,
                        change_type=ChangeType.MODIFIED,
                        old_value=val1,
                        new_value=val2,
                    )
                )

    def has_changes(self) -> bool:
        """Check if there are any changes between the prompts."""
        return len(self.changes) > 0

    def format(self, context_lines: int = 3) -> str:
        """
        Format the diff for human-readable output.

        Args:
            context_lines: Number of context lines for text diffs

        Returns:
            Formatted diff string
        """
        if not self.has_changes():
            return "No changes detected."

        lines = []
        lines.append("=" * 60)
        lines.append("PROMPT DIFF")
        lines.append("=" * 60)

        for change in self.changes:
            lines.append("")

            # Special handling for text fields (system, user_template)
            if change.field_name in ["system", "user_template", "assistant_prefix"]:
                lines.append(f"Field: {change.field_name}")
                lines.append("-" * 60)

                if change.change_type == ChangeType.ADDED:
                    lines.append(f"+ {change.new_value}")
                elif change.change_type == ChangeType.REMOVED:
                    lines.append(f"- {change.old_value}")
                elif change.change_type == ChangeType.MODIFIED:
                    # Use difflib for line-by-line text diff
                    old_lines = str(change.old_value).splitlines(keepends=True)
                    new_lines = str(change.new_value).splitlines(keepends=True)

                    diff = difflib.unified_diff(old_lines, new_lines, lineterm="", n=context_lines)

                    for line in diff:
                        if line.startswith("---") or line.startswith("+++"):
                            continue  # Skip file headers
                        if line.startswith("@@"):
                            continue  # Skip hunk headers
                        lines.append(line.rstrip())
            else:
                # Simple field changes
                lines.append(str(change))

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    def format_summary(self) -> str:
        """
        Format a brief summary of changes.

        Returns:
            One-line summary string
        """
        if not self.has_changes():
            return "No changes"

        added = sum(1 for c in self.changes if c.change_type == ChangeType.ADDED)
        removed = sum(1 for c in self.changes if c.change_type == ChangeType.REMOVED)
        modified = sum(1 for c in self.changes if c.change_type == ChangeType.MODIFIED)

        parts = []
        if added:
            parts.append(f"{added} added")
        if removed:
            parts.append(f"{removed} removed")
        if modified:
            parts.append(f"{modified} modified")

        return ", ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert diff result to dictionary for programmatic access.

        Returns:
            Dictionary with changes data
        """
        return {
            "has_changes": self.has_changes(),
            "summary": self.format_summary(),
            "changes": [
                {
                    "field": c.field_name,
                    "type": c.change_type.value,
                    "old_value": c.old_value,
                    "new_value": c.new_value,
                }
                for c in self.changes
            ],
        }


class PromptDiff:
    """
    High-level interface for comparing prompts.

    Provides semantic diffing capabilities that understand prompt structure
    and highlight meaningful changes.
    """

    @staticmethod
    def compare(prompt1: Prompt, prompt2: Prompt) -> DiffResult:
        """
        Compare two prompts and return a diff result.

        Args:
            prompt1: Original prompt
            prompt2: New prompt

        Returns:
            DiffResult containing changes
        """
        return DiffResult(prompt1, prompt2)

    @staticmethod
    def detect_template_variable_changes(prompt1: Prompt, prompt2: Prompt) -> list[str]:
        """
        Detect changes in template variables (e.g., {variable_name}).

        Args:
            prompt1: Original prompt
            prompt2: New prompt

        Returns:
            List of variable changes detected
        """
        import re

        var_pattern = r"\{([^}]+)\}"

        changes = []

        # Check user_template variables
        if prompt1.user_template or prompt2.user_template:
            vars1 = set(re.findall(var_pattern, prompt1.user_template or ""))
            vars2 = set(re.findall(var_pattern, prompt2.user_template or ""))

            added = vars2 - vars1
            removed = vars1 - vars2

            for var in added:
                changes.append(f"Added template variable: {{{var}}}")
            for var in removed:
                changes.append(f"Removed template variable: {{{var}}}")

        return changes

    @staticmethod
    def detect_parameter_changes(prompt1: Prompt, prompt2: Prompt) -> list[str]:
        """
        Detect changes in model parameters (temperature, max_tokens, etc.).

        Args:
            prompt1: Original prompt
            prompt2: New prompt

        Returns:
            List of parameter changes
        """
        param_fields = [
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
        ]

        changes = []

        for field in param_fields:
            val1 = getattr(prompt1, field, None)
            val2 = getattr(prompt2, field, None)

            if val1 != val2:
                if val1 is None:
                    changes.append(f"Added {field}: {val2}")
                elif val2 is None:
                    changes.append(f"Removed {field}: {val1}")
                else:
                    changes.append(f"Changed {field}: {val1} → {val2}")

        return changes
