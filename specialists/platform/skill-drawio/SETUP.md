---
Title: Setup — skill-drawio
Category: setup
Status: current
Authority: canonical
Scope: Installing and running skill-drawio, both as a pack under development and from a calling project
Last reviewed: 2026-10-23
Summary: >-
  A working setup needs mise, just, Python 3.11 or later with PyYAML for flow maps, and draw.io desktop only for exporting pages to images; the pack's
  own venv lives in the skills working cache.
Depends on: justfile, .mise.toml, requirements.txt, compatibility.yaml
---

# Setup — skill-drawio

## Contents

- [Prerequisites](#prerequisites)
- [Bootstrap](#bootstrap)
- [Using it from a project](#using-it-from-a-project)
- [Environment](#environment)
- [First run](#first-run)
- [Troubleshooting](#troubleshooting)

## Prerequisites

| Tool           | Version                                         | Pinned in                                        | Needed for                                                                     |
| -------------- | ----------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------ |
| mise           | any current                                     | -                                                | Installing the pinned Python (`just bootstrap`)                                |
| just           | any current                                     | -                                                | The task catalog (`just --list`)                                               |
| Python         | 3.14 for the pack's venv; 3.11 or later for     | `.mise.toml`; `REQUIRES_PYTHON = (3, 11)` in     | Everything                                                                     |
|                |   the helpers                                   |   each front end                                 |                                                                                |
| PyYAML         | 6.0.3                                           | `tests/requirements.txt`                         | Loading a flow map (`flowmap.model`, imported at the edge); the rest is stdlib |
|                |                                                 |   (via `requirements.txt`)                       |                                                                                |
| draw.io        | 32.5.5 verified (32.4.1 earlier)                | `compatibility.yaml`                             | Only `drawio_export.py` (pages to images); reading and rendering need no app   |
|   desktop      |                                                 |                                                  |                                                                                |

## Bootstrap

`just bootstrap` (once), then `just test` and `just check`. Bootstrap copies `.mise.toml` into the working cache `/Volumes/Data/_ai/_skills/skills-working-cache/skill-drawio`, installs the pinned
Python there, builds `.venv` and installs `requirements.txt`. Nothing is installed into the pack folder. Re-running it is safe.

## Using it from a project

The skill is installed as directory symlinks back to this folder: `~/.claude/skills/skill-drawio`, `~/.codex/skills/skill-drawio` and `~/.hermes/skills/diagramming/skill-drawio`. A project runs the
front ends with its own interpreter (it needs PyYAML for maps), from the project root:

- `<python> <this pack>/scripts/render_flowmap.py --map <map>`: validate and report drift; `--write` renders, `--list` lists flows, `--audit` audits the layout.
- A project that wraps the engine puts `scripts/` on `sys.path` through one seam and loads `drawio` and `flowmap` by name (unified-network-controller: `wc-local/scripts/common/skill_paths.py`,
  `use("skill-drawio")`).

## Environment

No environment variables and no secrets. The draw.io binary is found on `PATH` (`drawio`, `draw.io`), then in the usual install paths (`scripts/drawio/export.py` `CANDIDATES`: the macOS app bundle,
`/usr/bin/drawio`, `/opt/drawio/drawio`, the Windows default); `--binary` overrides it.

## First run

`just example-check` reads the example map `examples/shop/flows.yaml` and prints that it is valid, its drawing is current and the routed pages pass every layout audit. `just drawio-export
examples/shop/drawio/flows.drawio --out-dir <folder> --pages 1` then proves the desktop export (one PNG in the folder).

## Troubleshooting

- `venv missing at ... — run: just bootstrap`: the working-cache venv is not built yet; run `just bootstrap`.
- `No module named yaml` when a project renders its map: the project's interpreter lacks PyYAML; install it in the project's environment, not here.
- Export finds no binary: install draw.io desktop or pass `--binary <path>`.
- Export hangs: each export is killed after `--timeout` seconds (default 120) and the app has its own per-file timeout; check the file opens in the app.
