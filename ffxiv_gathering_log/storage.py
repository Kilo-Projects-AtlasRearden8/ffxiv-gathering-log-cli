"""Local-first JSON storage for the FFXIV gathering log."""

from __future__ import annotations

import json
import os
from typing import Optional

from .models import Log, Node, YieldRecord


class Storage:
    """Reads and writes the gathering log to a local JSON file."""

    def __init__(self, path: str) -> None:
        self.path = path

    def _ensure_parent(self) -> None:
        parent = os.path.dirname(self.path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)

    def load(self) -> Log:
        """Load the log from disk, returning an empty log if the file is absent."""
        if not os.path.exists(self.path):
            return Log()
        with open(self.path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        nodes = [Node.from_dict(item) for item in data.get("nodes", [])]
        yields = [YieldRecord.from_dict(item) for item in data.get("yields", [])]
        return Log(nodes=nodes, yields=yields)

    def save(self, log: Log) -> None:
        """Persist the log to disk."""
        self._ensure_parent()
        data = {
            "nodes": [node.to_dict() for node in log.nodes],
            "yields": [record.to_dict() for record in log.yields],
        }
        tmp_path = f"{self.path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
        os.replace(tmp_path, self.path)

    @classmethod
    def default_path(cls) -> str:
        """Return the default local data file path."""
        return os.path.join("data", "gathering_log.json")
