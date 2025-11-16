"""
Audit operations for prompt repository.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import csv
import io
import json
from typing import Any, Union

from ..models import AuditLogEntry
from ..storage import StorageBackend


class AuditOperations:
    """Handles audit logging operations."""

    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def generate_audit_log(self, format: str = "json") -> Union[str, list[dict[str, Any]]]:
        """
        Generate compliance audit log.

        Args:
            format: Output format ('json', 'csv', or 'dict')

        Returns:
            Audit log in requested format
        """
        entries = self.storage.read_audit_log()

        if format == "dict":
            return [entry.to_dict() for entry in entries]
        elif format == "csv":
            return self._format_csv(entries)
        else:  # json
            return json.dumps([entry.to_dict() for entry in entries], indent=2)

    def _format_csv(self, entries: list[AuditLogEntry]) -> str:
        """Format audit entries as CSV."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "timestamp",
                "action",
                "commit_hash",
                "prompt_hash",
                "message",
                "author",
                "metadata",
            ],
        )
        writer.writeheader()

        for entry in entries:
            row = entry.to_dict()
            # Convert metadata dict to string for CSV
            row["metadata"] = json.dumps(row["metadata"])
            writer.writerow(row)

        return output.getvalue()
