# STATUS

## What was built

A local-first Python CLI for FFXIV gatherers that logs gathering nodes,
respawn timers, and item yields, with CSV export. Built for Asdale Dynamics,
LLC.

Components:
- `ffxiv_gathering_log/models.py` — `Node`, `YieldRecord`, and `Log` data
  models with JSON serialization helpers
- `ffxiv_gathering_log/storage.py` — local-first JSON read/write storage
  (atomic save via temp file + `os.replace`)
- `ffxiv_gathering_log/export.py` — CSV export for nodes and yields, plus a
  simple text-table formatter used by the CLI
- `ffxiv_gathering_log/cli.py` — argparse CLI with subcommands:
  `node add/list`, `yield add/list`, `timers`, `stats`, `export`
- `tests/test_gathering_log.py` — 15 unit tests covering models, storage,
  export, and the CLI
- `pyproject.toml` — packaging with a `ffxiv-gather-log` console entry point
- `LICENSE` — MIT, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — credits Asdale Dynamics, LLC; beginner-friendly usage guide
- `.gitignore` — excludes local data, Python caches, and build artifacts
- `mypy.ini` — static type-check configuration

## How to run it

Run without installing:

```bash
python3 -m ffxiv_gathering_log.cli --help
```

Install for the `ffxiv-gather-log` command:

```bash
python3 -m pip install -e .
```

Example session:

```bash
ffxiv-gather-log node add --name "Copper Ore" --type mining \
  --location "Central Shroud" --level 5 --respawn 300
ffxiv-gather-log yield add --node "Copper Ore" --item "Copper Ore" --qty 4
ffxiv-gather-log timers
ffxiv-gather-log stats
ffxiv-gather-log export --dir export
```

Data is stored locally in `data/gathering_log.json` by default; use
`--data <path>` to choose another location.

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

Run the type checker:

```bash
python3 -m mypy ffxiv_gathering_log tests
```

## Verification results

- `python3 -m unittest discover -s tests` — 15 tests, OK
- `python3 -m mypy ffxiv_gathering_log tests` — no issues found
- `python3 -m pip install -e .` — builds and installs successfully
- `ffxiv-gather-log --help` — entry point works
- End-to-end smoke test: add node, add yield, view timers, export CSV — all
  produce correct output; `next_spawn` is computed and written to CSV

## Known gaps

- `next_spawn` is computed at yield time and shown in `timers`, but there is
  no explicit "refresh timers" command independent of gathering.
- No GUI or TUI beyond the command line; intended for users comfortable with a
  terminal.
- No node grouping by zone or map; nodes are a flat list.
- Packaging install requires `--break-system-packages` on PEP 668-managed
  systems (e.g. this environment); running via `python3 -m` avoids that.
- Tests use the real local filesystem (temp directories) and do not mock
  `datetime.now`, so timer values depend on wall-clock time.

## Credit

Built and published by Asdale Dynamics, LLC. Copyright (c) 2026 Asdale
Dynamics, LLC. MIT License.
