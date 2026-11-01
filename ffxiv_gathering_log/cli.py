"""Command-line interface for the FFXIV gathering log."""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from .export import export_all, format_table
from .models import Log, Node, NODE_TYPES, YieldRecord, now_iso, new_id
from .storage import Storage


def _node_type(value: str) -> str:
    if value.lower() not in NODE_TYPES:
        raise argparse.ArgumentTypeError(
            f"invalid node type: {value!r}. Choose from {', '.join(NODE_TYPES)}"
        )
    return value.lower()


def cmd_add_node(args: argparse.Namespace, log: Log, storage: Storage) -> int:
    if log.find_node_by_name(args.name) is not None:
        print(f"Node already exists: {args.name}", file=sys.stderr)
        return 1
    node = Node(
        id=new_id(),
        name=args.name,
        node_type=args.type,
        location=args.location,
        level=args.level,
        respawn_seconds=args.respawn,
        created_at=now_iso(),
    )
    log.add_node(node)
    storage.save(log)
    print(f"Added node: {args.name} ({args.type}) level {args.level}")
    return 0


def cmd_list_nodes(args: argparse.Namespace, log: Log, storage: Storage) -> int:
    if not log.nodes:
        print("No nodes logged yet.")
        return 0
    rows = [
        [
            node.name,
            node.node_type,
            node.location,
            str(node.level),
            str(node.respawn_seconds),
            node.last_gathered or "-",
            node.next_spawn or "-",
        ]
        for node in log.nodes
    ]
    print(
        format_table(
            rows,
            ["name", "type", "location", "level", "respawn_s", "last_gathered", "next_spawn"],
        )
    )
    return 0


def cmd_add_yield(args: argparse.Namespace, log: Log, storage: Storage) -> int:
    node = log.find_node_by_name(args.node) or log.find_node(args.node)
    if node is None:
        print(f"Unknown node: {args.node}", file=sys.stderr)
        return 1
    record = YieldRecord(
        id=new_id(),
        node_id=node.id,
        item=args.item,
        quantity=args.qty,
        gathered_at=now_iso(),
    )
    node.last_gathered = record.gathered_at
    log.add_yield(record)
    storage.save(log)
    print(
        f"Logged yield: {args.qty}x {args.item} from {node.name} at {record.gathered_at}"
    )
    return 0


def cmd_list_yields(args: argparse.Namespace, log: Log, storage: Storage) -> int:
    records = log.yields
    if args.node:
        node = log.find_node_by_name(args.node) or log.find_node(args.node)
        if node is None:
            print(f"Unknown node: {args.node}", file=sys.stderr)
            return 1
        records = log.yields_for_node(node.id)
    if not records:
        print("No yield records.")
        return 0
    rows = [
        [record.item, str(record.quantity), record.gathered_at, record.node_id[:8]]
        for record in records
    ]
    print(format_table(rows, ["item", "qty", "gathered_at", "node_id"]))
    return 0


def cmd_timers(args: argparse.Namespace, log: Log, storage: Storage) -> int:
    if not log.nodes:
        print("No nodes logged yet.")
        return 0
    rows = []
    for node in log.nodes:
        status = "gathered recently" if node.last_gathered else "never gathered"
        rows.append([node.name, node.node_type, str(node.respawn_seconds), status])
    print(format_table(rows, ["name", "type", "respawn_s", "status"]))
    return 0


def cmd_stats(args: argparse.Namespace, log: Log, storage: Storage) -> int:
    totals: dict[str, int] = {}
    for record in log.yields:
        totals[record.item] = totals.get(record.item, 0) + record.quantity
    if not totals:
        print("No yields logged yet.")
        return 0
    rows = sorted(totals.items(), key=lambda pair: pair[0])
    print(format_table([[item, str(qty)] for item, qty in rows], ["item", "total_qty"]))
    return 0


def cmd_export(args: argparse.Namespace, log: Log, storage: Storage) -> int:
    if args.nodes:
        node_count, _ = export_all(log, args.nodes, args.yields or "/dev/null")
        print(f"Exported {node_count} nodes to {args.nodes}")
    elif args.yields:
        _, yield_count = export_all(log, "/dev/null", args.yields)
        print(f"Exported {yield_count} yields to {args.yields}")
    elif args.dir:
        os.makedirs(args.dir, exist_ok=True)
        node_path = os.path.join(args.dir, "nodes.csv")
        yield_path = os.path.join(args.dir, "yields.csv")
        node_count, yield_count = export_all(log, node_path, yield_path)
        print(
            f"Exported {node_count} nodes to {node_path} and {yield_count} yields to {yield_path}"
        )
    else:
        print("Nothing to export: use --nodes, --yields, or --dir", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ffxiv-gather-log",
        description="Local-first FFXIV gathering node, timer, and yield logger.",
    )
    parser.add_argument(
        "--data",
        default=Storage.default_path(),
        help="Path to the local JSON log file (default: data/gathering_log.json)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_node = sub.add_parser("node", help="Manage gathering nodes")
    node_sub = p_node.add_subparsers(dest="action", required=True)
    p_node_add = node_sub.add_parser("add", help="Add a node")
    p_node_add.add_argument("--name", required=True)
    p_node_add.add_argument("--type", required=True, type=_node_type)
    p_node_add.add_argument("--location", required=True)
    p_node_add.add_argument("--level", required=True, type=int)
    p_node_add.add_argument("--respawn", type=int, default=300)
    p_node_add.set_defaults(func=cmd_add_node)
    p_node_list = node_sub.add_parser("list", help="List nodes")
    p_node_list.set_defaults(func=cmd_list_nodes)

    p_yield = sub.add_parser("yield", help="Log gathering yields")
    yield_sub = p_yield.add_subparsers(dest="action", required=True)
    p_yield_add = yield_sub.add_parser("add", help="Add a yield record")
    p_yield_add.add_argument("--node", required=True)
    p_yield_add.add_argument("--item", required=True)
    p_yield_add.add_argument("--qty", required=True, type=int)
    p_yield_add.set_defaults(func=cmd_add_yield)
    p_yield_list = yield_sub.add_parser("list", help="List yield records")
    p_yield_list.add_argument("--node", default=None)
    p_yield_list.set_defaults(func=cmd_list_yields)

    p_timers = sub.add_parser("timers", help="Show node respawn timers")
    p_timers.set_defaults(func=cmd_timers)

    p_stats = sub.add_parser("stats", help="Show total yields per item")
    p_stats.set_defaults(func=cmd_stats)

    p_export = sub.add_parser("export", help="Export log to CSV")
    p_export.add_argument("--nodes", default=None)
    p_export.add_argument("--yields", default=None)
    p_export.add_argument("--dir", default=None)
    p_export.set_defaults(func=cmd_export)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage = Storage(args.data)
    log = storage.load()
    return args.func(args, log, storage)


if __name__ == "__main__":
    sys.exit(main())
