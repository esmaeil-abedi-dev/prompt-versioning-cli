"""
Test suite for diff functionality.

Tests the semantic diffing engine for prompts.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

from prompt_versioning.core.models import Prompt
from prompt_versioning.utils import ChangeType
from prompt_versioning.utils.diff import PromptDiff


class TestPromptDiff:
    """Test cases for prompt diffing."""

    def test_no_changes(self):
        """Test diff when prompts are identical."""
        prompt1 = Prompt(system="Test", temperature=0.7)
        prompt2 = Prompt(system="Test", temperature=0.7)

        diff = PromptDiff.compare(prompt1, prompt2)

        assert not diff.has_changes()
        assert len(diff.changes) == 0

    def test_field_added(self):
        """Test detection of added fields."""
        prompt1 = Prompt(system="Test")
        prompt2 = Prompt(system="Test", temperature=0.7)

        diff = PromptDiff.compare(prompt1, prompt2)

        assert diff.has_changes()
        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == ChangeType.ADDED
        assert diff.changes[0].field_name == "temperature"

    def test_field_removed(self):
        """Test detection of removed fields."""
        prompt1 = Prompt(system="Test", temperature=0.7)
        prompt2 = Prompt(system="Test")

        diff = PromptDiff.compare(prompt1, prompt2)

        assert diff.has_changes()
        assert len(diff.changes) == 1
        assert diff.changes[0].change_type == ChangeType.REMOVED
        assert diff.changes[0].field_name == "temperature"

    def test_field_modified(self):
        """Test detection of modified fields."""
        prompt1 = Prompt(system="Old text", temperature=0.5)
        prompt2 = Prompt(system="New text", temperature=0.9)

        diff = PromptDiff.compare(prompt1, prompt2)

        assert diff.has_changes()
        assert len(diff.changes) == 2  # Both fields changed

        # Find system change
        system_change = next(c for c in diff.changes if c.field_name == "system")
        assert system_change.change_type == ChangeType.MODIFIED
        assert system_change.old_value == "Old text"
        assert system_change.new_value == "New text"

    def test_template_variable_detection(self):
        """Test detection of template variable changes."""
        prompt1 = Prompt(user_template="Help me with {issue}")
        prompt2 = Prompt(user_template="Help me with {problem} and {context}")

        changes = PromptDiff.detect_template_variable_changes(prompt1, prompt2)

        assert len(changes) == 3  # 1 removed + 2 added
        assert any("Removed" in c and "issue" in c for c in changes)
        assert any("Added" in c and "problem" in c for c in changes)
        assert any("Added" in c and "context" in c for c in changes)

    def test_parameter_changes_detection(self):
        """Test detection of model parameter changes."""
        prompt1 = Prompt(temperature=0.5, max_tokens=100)
        prompt2 = Prompt(temperature=0.9, max_tokens=200, top_p=0.95)

        changes = PromptDiff.detect_parameter_changes(prompt1, prompt2)

        assert len(changes) == 3
        assert any("temperature" in c for c in changes)
        assert any("max_tokens" in c for c in changes)
        assert any("top_p" in c for c in changes)

    def test_diff_format(self):
        """Test formatted diff output."""
        prompt1 = Prompt(system="Old", temperature=0.5)
        prompt2 = Prompt(system="New", temperature=0.9)

        diff = PromptDiff.compare(prompt1, prompt2)
        formatted = diff.format()

        assert "PROMPT DIFF" in formatted
        assert "system" in formatted
        assert "temperature" in formatted

    def test_diff_summary(self):
        """Test diff summary generation."""
        prompt1 = Prompt(system="Test")
        prompt2 = Prompt(system="Test", temperature=0.7, max_tokens=100)

        diff = PromptDiff.compare(prompt1, prompt2)
        summary = diff.format_summary()

        assert "2 added" in summary

    def test_diff_to_dict(self):
        """Test converting diff to dictionary."""
        prompt1 = Prompt(system="Old")
        prompt2 = Prompt(system="New", temperature=0.7)

        diff = PromptDiff.compare(prompt1, prompt2)
        diff_dict = diff.to_dict()

        assert diff_dict["has_changes"] is True
        assert "changes" in diff_dict
        assert len(diff_dict["changes"]) == 2

    def test_multiline_text_diff(self):
        """Test diff of multiline text fields."""
        prompt1 = Prompt(system="Line 1\nLine 2\nLine 3")
        prompt2 = Prompt(system="Line 1\nModified Line 2\nLine 3")

        diff = PromptDiff.compare(prompt1, prompt2)

        assert diff.has_changes()
        formatted = diff.format()
        assert "Line" in formatted

    def test_complex_field_changes(self):
        """Test diff with list fields."""
        prompt1 = Prompt(stop_sequences=["STOP", "END"])
        prompt2 = Prompt(stop_sequences=["STOP", "FINISH"])

        diff = PromptDiff.compare(prompt1, prompt2)

        assert diff.has_changes()

    def test_no_template_variables(self):
        """Test template variable detection with no variables."""
        prompt1 = Prompt(user_template="Simple text")
        prompt2 = Prompt(user_template="Different text")

        changes = PromptDiff.detect_template_variable_changes(prompt1, prompt2)

        assert len(changes) == 0
