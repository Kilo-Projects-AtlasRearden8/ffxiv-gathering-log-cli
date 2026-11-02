"""CSV export for the FFXIV gathering log."""

from __future__ import annotations

import csv
from typing import Iterable

from .models import Log, Node, YieldRecord


def export_nodes(log: Log, path: str) -> int:
    """Export nodes to CSV. Returns the number of rows written."""
    fields = [
        "id",
        "name",
        "node_type",
        "location",
        "level",
        "respawn_seconds",
        "created_at",
        "last_gathered",
        "next_spawn",
    ]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        count = 0
        for node in log.nodes:
            writer.writerow(node.to_dict())
            count += 1
    return count


def export_yields(log: Log, path: str) -> int:
    """Export yield records to CSV. Returns the number of rows written."""
    fields = ["id", "node_id", "item", "quantity", "gathered_at"]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        count = 0
        for record in log.yields:
            writer.writerow(record.to_dict())
            count += 1
    return count


def export_all(log: Log, nodes_path: str, yields_path: str) -> tuple[int, int]:
    """Export nodes and yields. Returns (node_count, yield_count)."""
    return export_nodes(log, nodes_path), export_yields(log, yields_path)


def format_table(rows: Iterable[Iterable[str]], headers: list[str]) -> str:
    """Format rows as a simple aligned text table."""
    rows = [list(row) for row in rows]
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def line(row: Iterable[str]) -> str:
        return " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))

    out = [line(headers), "-+-".join("-" * w for w in widths)]
    for row in rows:
        out.append(line(row))
    return "\n".join(out)
