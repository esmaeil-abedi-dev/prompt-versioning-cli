"""
Integration tests for end-to-end workflows.

Tests complete user journeys through the CLI and API.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from prompt_versioning.core import PromptRepository


class TestIntegration:
    """End-to-end integration tests."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_complete_workflow(self, temp_repo):
        """
        Test a complete workflow: init → commit → log → diff → checkout → tag.
        """
        # 1. Initialize repository
        repo = PromptRepository.init(temp_repo)
        assert repo.exists()

        # 2. Create first prompt
        prompt1_data = {
            "system": "You are a friendly customer support agent.",
            "user_template": "Help me with: {issue}",
            "temperature": 0.7,
            "max_tokens": 500,
        }
        commit1 = repo.commit("Initial support prompt", prompt1_data)
        assert commit1.hash

        # 3. Create second prompt (iteration)
        prompt2_data = {
            "system": "You are a warm, empathetic customer support agent.",
            "user_template": "Help me with: {issue}",
            "temperature": 0.7,
            "max_tokens": 500,
        }
        commit2 = repo.commit("Made tone more empathetic", prompt2_data)
        assert commit2.parent_hash == commit1.hash

        # 4. View log
        versions = repo.log()
        assert len(versions) == 2
        assert versions[0].commit.hash == commit2.hash  # Newest first

        # 5. Compare versions
        diff = repo.diff(commit1.hash, commit2.hash)
        assert diff.has_changes()
        assert any(c.field_name == "system" for c in diff.changes)

        # 6. Tag experiment
        tag = repo.tag(
            "experiment-empathy-v1", metadata={"conversion_rate": 0.68, "model": "gpt-4"}
        )
        assert tag.commit_hash == commit2.hash

        # 7. Rollback to previous version
        version = repo.checkout(commit1.hash)
        assert version.commit.hash == commit1.hash
        current = repo.get_current_version()
        assert current.commit.hash == commit1.hash

        # 8. Generate audit log
        audit_data = repo.audit_log(format="dict")
        assert len(audit_data) >= 5  # init + 2 commits + tag + checkout

    def test_ab_testing_workflow(self, temp_repo):
        """Test A/B testing with multiple experiments."""
        repo = PromptRepository.init(temp_repo)

        # Baseline prompt
        baseline = {"system": "You are helpful.", "temperature": 0.5}
        repo.commit("Baseline", baseline)
        repo.tag("experiment-baseline", metadata={"accuracy": 0.80})

        # Variant A: Higher temperature
        variant_a = {"system": "You are helpful.", "temperature": 0.9}
        repo.commit("Variant A: Higher temp", variant_a)
        repo.tag("experiment-variant-a", metadata={"accuracy": 0.82})

        # Variant B: Different system message
        variant_b = {"system": "You are very helpful.", "temperature": 0.5}
        repo.commit("Variant B: Better system", variant_b)
        repo.tag("experiment-variant-b", metadata={"accuracy": 0.85})

        # Compare all variants
        tags = repo.list_tags()
        assert len(tags) == 3

        # Find best performing variant
        best_tag = max(tags, key=lambda t: t.metadata.get("accuracy", 0))
        assert best_tag.name == "experiment-variant-b"

        # Checkout winning variant
        repo.checkout(best_tag.commit_hash)
        current = repo.get_current_version()
        assert current.prompt.system == "You are very helpful."

    def test_file_based_commits(self, temp_repo):
        """Test committing from YAML files."""
        repo = PromptRepository.init(temp_repo)

        # Create a prompt file
        prompt_file = temp_repo / "prompt.yaml"
        prompt_data = {
            "system": "Test system message",
            "temperature": 0.7,
        }
        prompt_file.write_text(yaml.dump(prompt_data))

        # Load and commit
        loaded_data = yaml.safe_load(prompt_file.read_text())
        repo.commit("From file", loaded_data)

        # Verify
        version = repo.get_current_version()
        assert version.prompt.system == "Test system message"

    def test_concurrent_experiments(self, temp_repo):
        """Test managing multiple concurrent experiments."""
        repo = PromptRepository.init(temp_repo)

        # Create base prompt
        base = {"system": "Base prompt"}
        repo.commit("Base", base)

        # Create multiple experiment branches (simulated)
        experiments = []
        for i in range(5):
            prompt = {
                "system": f"Experiment {i} prompt",
                "temperature": 0.5 + (i * 0.1),
            }
            commit = repo.commit(f"Experiment {i}", prompt)
            tag = repo.tag(f"exp-{i}", metadata={"exp_id": i})
            experiments.append((commit, tag))

        # Verify all experiments tracked
        tags = repo.list_tags()
        assert len(tags) == 5

        # Checkout specific experiment
        repo.checkout(experiments[2][0].hash)
        current = repo.get_current_version()
        assert "Experiment 2" in current.prompt.system

    def test_audit_trail_compliance(self, temp_repo):
        """Test audit trail for compliance requirements."""
        repo = PromptRepository.init(temp_repo)

        # Perform various operations
        repo.commit("Commit 1", {"system": "V1"}, author="user1")
        repo.commit("Commit 2", {"system": "V2"}, author="user2")
        commit3 = repo.commit("Commit 3", {"system": "V3"}, author="user3")
        repo.tag("production", metadata={"deployed": True})
        repo.checkout(commit3.hash)

        # Generate audit log
        audit_entries = repo.audit_log(format="dict")

        # Verify all actions logged
        actions = [e["action"] for e in audit_entries]
        assert "init" in actions
        assert actions.count("commit") == 3
        assert "tag" in actions
        assert "checkout" in actions

        # Verify authors tracked
        authors = [e["author"] for e in audit_entries if e["action"] == "commit"]
        assert "user1" in authors
        assert "user2" in authors
        assert "user3" in authors

        # Verify timestamps present
        for entry in audit_entries:
            assert "timestamp" in entry
            assert entry["timestamp"]  # Not empty

    def test_csv_export(self, temp_repo):
        """Test CSV audit log export."""
        repo = PromptRepository.init(temp_repo)

        repo.commit("Test", {"system": "Test"})

        # Export as CSV
        csv_output = repo.audit_log(format="csv")

        lines = csv_output.strip().split("\n")
        assert len(lines) >= 2  # Header + at least one entry
        assert "timestamp" in lines[0]
        assert "action" in lines[0]

    def test_short_hash_usage(self, temp_repo):
        """Test using abbreviated commit hashes."""
        repo = PromptRepository.init(temp_repo)

        commit1 = repo.commit("First", {"system": "V1"})
        commit2 = repo.commit("Second", {"system": "V2"})

        # Use 7-character short hash
        short_hash = commit1.hash[:7]

        # Should work for diff
        diff = repo.diff(short_hash, commit2.hash[:7])
        assert diff.has_changes()

        # Should work for checkout
        version = repo.checkout(short_hash)
        assert version.commit.hash == commit1.hash

    def test_head_references(self, temp_repo):
        """Test HEAD and HEAD~N reference usage."""
        repo = PromptRepository.init(temp_repo)

        repo.commit("First", {"system": "V1"})
        repo.commit("Second", {"system": "V2"})
        repo.commit("Third", {"system": "V3"})

        # Compare HEAD with HEAD~1
        diff = repo.diff("HEAD~1", "HEAD")
        assert diff.has_changes()

        # Compare HEAD~2 with HEAD
        diff = repo.diff("HEAD~2", "HEAD")
        assert diff.has_changes()

    def test_empty_repository_operations(self, temp_repo):
        """Test operations on empty repository."""
        repo = PromptRepository.init(temp_repo)

        # Log should be empty
        assert len(repo.log()) == 0

        # Current version should be None
        assert repo.get_current_version() is None

        # Tags should be empty
        assert len(repo.list_tags()) == 0

        # Audit log should only have init
        audit_data = repo.audit_log(format="dict")
        assert len(audit_data) == 1
        assert audit_data[0]["action"] == "init"
