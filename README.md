# ffxiv-gathering-log

Local-first CLI for logging FFXIV gathering nodes, respawn timers, and yields,
with CSV export. Built and published by [Asdale Dynamics, LLC](https://dylanasdale.github.io).

## Who this is for

FFXIV gatherers who want a simple, private, local-first tool to track where
nodes are, when they respawn, and what they've gathered. No accounts, no API
keys, no network calls. Your data stays on your machine in a JSON file you
own.

This is part of Asdale Dynamics, LLC's line of practical, beginner-friendly,
open-source tools: small utilities anyone can read, run, and extend.

## Features

- Log gathering nodes (mining, botany, fishing) with name, location, level, and respawn time
- Log yield events (item + quantity) tied to a node
- View respawn timers and gathering stats
- Export nodes and yields to CSV
- Entirely local-first: data lives in `data/gathering_log.json` (or a path you choose)
- No secrets, no API keys, no personal data, no network access

## Install

```bash
git clone https://github.com/Asdale-Dynamics/ffxiv-gathering-log-cli.git
cd ffxiv-gathering-log-cli
python3 -m pip install -e .
```

Or run without installing:

```bash
python3 -m ffxiv_gathering_log.cli --help
```

## Usage

Add a node:

```bash
ffxiv-gather-log node add --name "Copper Ore" --type mining --location "Central Shroud" --level 5 --respawn 300
```

List nodes:

```bash
ffxiv-gather-log node list
```

Log a yield:

```bash
ffxiv-gather-log yield add --node "Copper Ore" --item "Copper Ore" --qty 4
```

View yields and stats:

```bash
ffxiv-gather-log yield list
ffxiv-gather-log stats
```

Check respawn timers:

```bash
ffxiv-gather-log timers
```

Export to CSV:

```bash
ffxiv-gather-log export --dir export
# or
ffxiv-gather-log export --nodes nodes.csv --yields yields.csv
```

Use `--data <path>` to store the log somewhere else (default: `data/gathering_log.json`).

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## About

Asdale Dynamics, LLC (Indiana, formed October 2026) is the small business of
Dylan Asdale, a registered nurse turned AI author and founder. His book *The
Massive AI Manual* and hub site dylanasdale.github.io explain AI "like a
friend would": plain English, step by step, never condescending.

Asdale Dynamics, LLC focuses on beginner-friendly AI education, books and
guides, and practical tools that the LLC can publish or sell — including
open-source apps and templates like this one.

Credit: Asdale Dynamics, LLC

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
