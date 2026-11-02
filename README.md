# ffxiv-gathering-log

A local-first command-line tool for logging FFXIV gathering nodes, respawn
timers, and yields, with CSV export. Published by Asdale Dynamics, LLC.

## Who this is for

This is for FFXIV gatherers who want a simple, private way to keep track of
where nodes are, how often they respawn, and what they have gathered. It is
built to be approachable: plain commands, no accounts, no API keys, no network
calls, and nothing sent anywhere but your own computer.

It is part of Asdale Dynamics, LLC's line of practical, beginner-friendly,
open-source tools. Asdale Dynamics, LLC is the small business of Dylan Asdale,
a registered nurse turned AI author and founder. His book *The Massive AI
Manual* and hub site dylanasdale.github.io explain AI "like a friend would":
plain English, step by step, never condescending.

## What it does

- Log gathering nodes (mining, botany, fishing) with a name, location, level,
  and respawn time
- Log yield events (an item and a quantity) tied to a node
- Show respawn timers: how long until each node is ready to gather again
- Show totals per item across all your yields
- Export your nodes and yields to CSV files so you can open them in a
  spreadsheet or back them up
- Keep everything local-first: your data lives in a JSON file on your machine
  (`data/gathering_log.json` by default, or any path you choose)

There are no secrets, no API keys, no personal data collected, and no network
access of any kind.

## Install

You can run it straight from this folder without installing:

```bash
python3 -m ffxiv_gathering_log.cli --help
```

Or install it so the `ffxiv-gather-log` command is available everywhere:

```bash
python3 -m pip install -e .
```

## Usage

Add a gathering node:

```bash
ffxiv-gather-log node add \
  --name "Copper Ore" \
  --type mining \
  --location "Central Shroud" \
  --level 5 \
  --respawn 300
```

List your nodes:

```bash
ffxiv-gather-log node list
```

Log a yield (what you gathered):

```bash
ffxiv-gather-log yield add \
  --node "Copper Ore" \
  --item "Copper Ore" \
  --qty 4
```

View your yields:

```bash
ffxiv-gather-log yield list
```

See total quantities gathered per item:

```bash
ffxiv-gather-log stats
```

Check respawn timers:

```bash
ffxiv-gather-log timers
```

Export everything to CSV:

```bash
ffxiv-gather-log export --dir export
```

This writes `export/nodes.csv` and `export/yields.csv`. You can also export
just one file:

```bash
ffxiv-gather-log export --nodes nodes.csv --yields yields.csv
```

Use `--data <path>` to store your log somewhere other than the default.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## About

Asdale Dynamics, LLC (Indiana, formed October 2026) focuses on beginner-friendly
AI education, books and guides, and practical tools that the LLC can publish or
sell. This FFXIV gathering log is one of those practical tools: open source,
tested, and local-first.

Credit: Asdale Dynamics, LLC

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
