"""
Audit log operations.

Copyright (c) 2025 Prompt Versioning Contributors
Licensed under MIT License
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..models import AuditLogEntry


class AuditLog:
    """Handles audit trail persistence."""

    def __init__(self, audit_file: Path):
        self.audit_file = audit_file

    def append(self, entry: AuditLogEntry) -> None:
        """
        Append an entry to the audit log.

        Uses JSON Lines format (one JSON object per line) for efficient appending
        and streaming reads.
        """
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def log_action(
        self,
        action: str,
        message: str,
        commit_hash: Optional[str] = None,
        prompt_hash: Optional[str] = None,
        author: str = "system",
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an action to the audit trail."""
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            action=action,
            commit_hash=commit_hash,
            prompt_hash=prompt_hash,
            message=message,
            author=author,
            metadata=metadata or {},
        )
        self.append(entry)

    def read_all(self) -> list[AuditLogEntry]:
        """Read the complete audit log."""
        if not self.audit_file.exists():
            return []

        entries = []
        with open(self.audit_file) as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    # Parse datetime
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                    entries.append(AuditLogEntry(**data))

        return entries
