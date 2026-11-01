"""Data models for the FFXIV gathering log."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


NODE_TYPES = ("mining", "botany", "fishing")


def now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    """Return a new unique identifier."""
    return str(uuid.uuid4())


@dataclass
class Node:
    """A gatherable node in FFXIV."""

    id: str
    name: str
    node_type: str
    location: str
    level: int
    respawn_seconds: int
    created_at: str
    last_gathered: str | None = None
    next_spawn: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type,
            "location": self.location,
            "level": self.level,
            "respawn_seconds": self.respawn_seconds,
            "created_at": self.created_at,
            "last_gathered": self.last_gathered,
            "next_spawn": self.next_spawn,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        return cls(
            id=data["id"],
            name=data["name"],
            node_type=data["node_type"],
            location=data["location"],
            level=int(data["level"]),
            respawn_seconds=int(data["respawn_seconds"]),
            created_at=data["created_at"],
            last_gathered=data.get("last_gathered"),
            next_spawn=data.get("next_spawn"),
        )


@dataclass
class YieldRecord:
    """A single gathering yield event."""

    id: str
    node_id: str
    item: str
    quantity: int
    gathered_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "node_id": self.node_id,
            "item": self.item,
            "quantity": self.quantity,
            "gathered_at": self.gathered_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "YieldRecord":
        return cls(
            id=data["id"],
            node_id=data["node_id"],
            item=data["item"],
            quantity=int(data["quantity"]),
            gathered_at=data["gathered_at"],
        )


@dataclass
class Log:
    """In-memory collection of nodes and yield records."""

    nodes: list[Node] = field(default_factory=list)
    yields: list[YieldRecord] = field(default_factory=list)

    def find_node(self, node_id: str) -> Node | None:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def find_node_by_name(self, name: str) -> Node | None:
        for node in self.nodes:
            if node.name.lower() == name.lower():
                return node
        return None

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def add_yield(self, record: YieldRecord) -> None:
        self.yields.append(record)

    def yields_for_node(self, node_id: str) -> list[YieldRecord]:
        return [y for y in self.yields if y.node_id == node_id]

    def total_yield_for_item(self, item: str) -> int:
        return sum(y.quantity for y in self.yields if y.item.lower() == item.lower())
