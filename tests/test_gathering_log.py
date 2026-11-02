"""Unit tests for the FFXIV gathering log package."""

from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest

from ffxiv_gathering_log.cli import build_parser, main
from ffxiv_gathering_log.export import export_all, format_table
from ffxiv_gathering_log.models import (
    Log,
    Node,
    NODE_TYPES,
    YieldRecord,
    now_iso,
    new_id,
)
from ffxiv_gathering_log.storage import Storage


class TestModels(unittest.TestCase):
    def test_node_roundtrip(self) -> None:
        node = Node(
            id=new_id(),
            name="Copper Ore",
            node_type="mining",
            location="Central Shroud",
            level=5,
            respawn_seconds=300,
            created_at=now_iso(),
        )
        restored = Node.from_dict(node.to_dict())
        self.assertEqual(restored, node)

    def test_yield_roundtrip(self) -> None:
        record = YieldRecord(
            id=new_id(),
            node_id="abc",
            item="Copper Ore",
            quantity=3,
            gathered_at=now_iso(),
        )
        restored = YieldRecord.from_dict(record.to_dict())
        self.assertEqual(restored, record)

    def test_log_find_node(self) -> None:
        log = Log()
        node = Node(
            id=new_id(),
            name="Copper Ore",
            node_type="mining",
            location="Central Shroud",
            level=5,
            respawn_seconds=300,
            created_at=now_iso(),
        )
        log.add_node(node)
        self.assertIs(log.find_node(node.id), node)
        self.assertIs(log.find_node_by_name("copper ore"), node)
        self.assertIsNone(log.find_node("missing"))
        self.assertIsNone(log.find_node_by_name("missing"))

    def test_yields_for_node_and_totals(self) -> None:
        log = Log()
        node = Node(
            id=new_id(),
            name="Copper Ore",
            node_type="mining",
            location="Central Shroud",
            level=5,
            respawn_seconds=300,
            created_at=now_iso(),
        )
        log.add_node(node)
        log.add_yield(YieldRecord(new_id(), node.id, "Copper Ore", 2, now_iso()))
        log.add_yield(YieldRecord(new_id(), node.id, "Copper Ore", 3, now_iso()))
        log.add_yield(YieldRecord(new_id(), "other", "Iron Ore", 1, now_iso()))
        self.assertEqual(len(log.yields_for_node(node.id)), 2)
        self.assertEqual(log.total_yield_for_item("Copper Ore"), 5)
        self.assertEqual(log.total_yield_for_item("Iron Ore"), 1)
        self.assertEqual(log.total_yield_for_item("Gold Ore"), 0)

    def test_node_types(self) -> None:
        self.assertIn("mining", NODE_TYPES)
        self.assertIn("botany", NODE_TYPES)
        self.assertIn("fishing", NODE_TYPES)


class TestStorage(unittest.TestCase):
    def test_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "log.json")
            storage = Storage(path)
            log = Log()
            node = Node(
                id=new_id(),
                name="Copper Ore",
                node_type="mining",
                location="Central Shroud",
                level=5,
                respawn_seconds=300,
                created_at=now_iso(),
            )
            log.add_node(node)
            storage.save(log)
            loaded = storage.load()
            self.assertEqual(len(loaded.nodes), 1)
            self.assertEqual(loaded.nodes[0].name, "Copper Ore")
            self.assertEqual(len(loaded.yields), 0)

    def test_load_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "missing.json")
            storage = Storage(path)
            log = storage.load()
            self.assertEqual(len(log.nodes), 0)
            self.assertEqual(len(log.yields), 0)


class TestExport(unittest.TestCase):
    def test_export_nodes_and_yields(self) -> None:
        log = Log()
        node = Node(
            id=new_id(),
            name="Copper Ore",
            node_type="mining",
            location="Central Shroud",
            level=5,
            respawn_seconds=300,
            created_at=now_iso(),
        )
        log.add_node(node)
        log.add_yield(YieldRecord(new_id(), node.id, "Copper Ore", 2, now_iso()))
        with tempfile.TemporaryDirectory() as tmp:
            nodes_path = os.path.join(tmp, "nodes.csv")
            yields_path = os.path.join(tmp, "yields.csv")
            n_count, y_count = export_all(log, nodes_path, yields_path)
            self.assertEqual(n_count, 1)
            self.assertEqual(y_count, 1)
            with open(nodes_path, encoding="utf-8") as handle:
                header = handle.readline().strip()
            self.assertIn("name", header)
            self.assertIn("node_type", header)

    def test_format_table(self) -> None:
        out = format_table(
            [["Copper Ore", "2"], ["Iron Ore", "1"]], ["item", "qty"]
        )
        self.assertIn("Copper Ore", out)
        self.assertIn("Iron Ore", out)
        self.assertIn("item", out)


class TestCLI(unittest.TestCase):
    def _run(self, argv: list[str]) -> tuple[int, str]:
        parser = build_parser()
        args = parser.parse_args(argv)
        storage = Storage(self.path)
        log = storage.load()
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            code = args.func(args, log, storage)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        storage.save(log)
        return code, output

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "log.json")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_add_and_list_node(self) -> None:
        code, out = self._run(
            [
                "--data",
                self.path,
                "node",
                "add",
                "--name",
                "Copper Ore",
                "--type",
                "mining",
                "--location",
                "Central Shroud",
                "--level",
                "5",
            ]
        )
        self.assertEqual(code, 0)
        self.assertIn("Added node: Copper Ore", out)

        code, out = self._run(["--data", self.path, "node", "list"])
        self.assertEqual(code, 0)
        self.assertIn("Copper Ore", out)
        self.assertIn("mining", out)

    def test_add_duplicate_node(self) -> None:
        self._run(
            [
                "--data",
                self.path,
                "node",
                "add",
                "--name",
                "Copper Ore",
                "--type",
                "mining",
                "--location",
                "Central Shroud",
                "--level",
                "5",
            ]
        )
        code, out = self._run(
            [
                "--data",
                self.path,
                "node",
                "add",
                "--name",
                "Copper Ore",
                "--type",
                "mining",
                "--location",
                "Central Shroud",
                "--level",
                "5",
            ]
        )
        self.assertNotEqual(code, 0)

    def test_add_yield_and_stats(self) -> None:
        self._run(
            [
                "--data",
                self.path,
                "node",
                "add",
                "--name",
                "Copper Ore",
                "--type",
                "mining",
                "--location",
                "Central Shroud",
                "--level",
                "5",
            ]
        )
        code, out = self._run(
            [
                "--data",
                self.path,
                "yield",
                "add",
                "--node",
                "Copper Ore",
                "--item",
                "Copper Ore",
                "--qty",
                "4",
            ]
        )
        self.assertEqual(code, 0)
        self.assertIn("Logged yield", out)

        code, out = self._run(["--data", self.path, "stats"])
        self.assertEqual(code, 0)
        self.assertIn("Copper Ore", out)
        self.assertIn("4", out)

    def test_timers(self) -> None:
        self._run(
            [
                "--data",
                self.path,
                "node",
                "add",
                "--name",
                "Copper Ore",
                "--type",
                "mining",
                "--location",
                "Central Shroud",
                "--level",
                "5",
            ]
        )
        code, out = self._run(["--data", self.path, "timers"])
        self.assertEqual(code, 0)
        self.assertIn("Copper Ore", out)

    def test_export_dir(self) -> None:
        self._run(
            [
                "--data",
                self.path,
                "node",
                "add",
                "--name",
                "Copper Ore",
                "--type",
                "mining",
                "--location",
                "Central Shroud",
                "--level",
                "5",
            ]
        )
        outdir = os.path.join(self.tmpdir.name, "export")
        code, out = self._run(["--data", self.path, "export", "--dir", outdir])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(os.path.join(outdir, "nodes.csv")))
        self.assertTrue(os.path.exists(os.path.join(outdir, "yields.csv")))

    def test_invalid_node_type(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "--data",
                    self.path,
                    "node",
                    "add",
                    "--name",
                    "X",
                    "--type",
                    "cooking",
                    "--location",
                    "L",
                    "--level",
                    "1",
                ]
            )


if __name__ == "__main__":
    unittest.main()
