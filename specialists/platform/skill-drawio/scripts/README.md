# Script Inventory

skill-drawio's scripts: four front ends at the top of `scripts/`, the engine in two packages (`drawio/`, `flowmap/`), two small map helpers and
the pack's governance checker.

## Contents

- [How a project uses the engine](#how-a-project-uses-the-engine)
- [Runtimes](#runtimes)
- [Execution Policy](#execution-policy)
- [Preferred Execution Order](#preferred-execution-order)
- [Maintenance Rules](#maintenance-rules)
- [Task Inventory](#task-inventory)
- [Raw Script Inventory](#raw-script-inventory)
- [Safety Labels](#safety-labels)
- [Governance recipes (skill-ai-it)](#governance-recipes-skill-ai-it)

---

## How a project uses the engine

Run the front ends with the **project's own interpreter** (Python 3.11 or newer; PyYAML to read a map), by path, from the project root:

```bash
<project venv>/bin/python /Volumes/Data/_ai/_skills/skills_stuff/specialists/platform/skill-drawio/scripts/render_flowmap.py --map docs/flows/flows.yaml
```

A project with its own constants imports the packages instead: put this folder on `sys.path` through the project's one seam to the skills, build a
`flowmap.profile.Profile` and call `flowmap.pages.render` and `evaluate`. Most projects need neither: the map's `drawing:` block holds the
constants and `render_flowmap.py` is the whole renderer (unified-network-controller since 2026-10-19).

## Runtimes

| Runtime | Resolved by                                                                 | Actual                                                               |
| ------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Python  | `.venv` in the working-cache peer, built from the pin in `../.mise.toml`     | `/Volumes/Data/_ai/_skills/skills-working-cache/skill-drawio/.venv` |
| draw.io | the desktop app, found on PATH or in the usual places (`drawio/export.py`)  | 32.5.5 on the operator's Mac (`../compatibility.yaml`)               |

`just runtimes` prints what the recipes use; `just bootstrap` rebuilds the venv. Do not invoke the pack's recipes through a bare `python3`.

<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: 2026-10-14-compact-v2 -->

## Execution Policy

- Prefer the existing canonical task runner for this project.
- Prefer `just <task>` when a `justfile` is present.
- Do not run scripts marked `destructive`, `review-required`, or `unknown` without review.
- Do not assume arbitrary files under `scripts/` are safe.
- If a script is missing from this inventory, inspect it before use and update or propose an inventory entry.
- Secrets must not be documented here as values. Document only secret names and where they are expected to come from.

## Preferred Execution Order

1. Existing canonical task runner (whichever is established for this project)
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts under `scripts/` after inspection

## Maintenance Rules

- Keep this file aligned with: `justfile`, `Taskfile.yml`, `Makefile`, `package.json`, actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

<!-- END MANAGED: skill-ai-it:scripts -->

## Task Inventory

| Task                   | Purpose                                                                      | Inputs                         | Outputs                     | Safety            | Idempotent | When to use                              |
| ---------------------- | ---------------------------------------------------------------------------- | ------------------------------ | --------------------------- | ----------------- | ---------- | ---------------------------------------- |
| `just test`            | Contract and engine tests                                                    | `tests/`, pack files           | Console, exit status        | `safe`            | Yes        | Before calling any change complete       |
| `just test-matrix`     | Engine tests under each installed Python from 3.11                           | `tests/test_helpers.py`        | One line per version        | `safe`            | Yes        | After changing the engine                |
| `just check`           | Governance coherence, self-check, example check, doc freshness, roles        | Governance surfaces            | Console, exit status        | `safe`            | Yes        | Before claiming durable work complete    |
| `just self-check`      | The pack held to skill-coder's rules through skill-coder's helpers           | `scripts/`, `tests/`, code map | Console, exit status        | `safe`            | Yes        | Part of `just check`                     |
| `just example`         | Renders the example map's drawing                                            | `examples/shop/flows.yaml`     | `examples/shop/drawio/`     | `modifies-files`  | Yes        | After changing the engine or the example |
| `just example-check`   | Example map valid, drawing current, every layout audit clean                 | `examples/shop/`               | Console, exit status        | `safe`            | Yes        | Part of `just check`                     |
| `just render-flowmap`  | `scripts/render_flowmap.py` (validate, drift, `--write`, `--list`, `--audit`) | A map, its schema              | Drawing with `--write`      | `safe` (`modifies-files` with `--write`) | Yes | Drawing a project's flows       |
| `just drawio-export`   | `scripts/drawio_export.py`: pages and layers to images                       | A .drawio file                 | Images in `--out-dir`       | `modifies-files`  | Yes        | Self-review before showing a drawing     |
| `just drawio-read`     | `scripts/drawio_read.py`: an existing drawing as text or JSON                | .drawio files                  | Console, JSON with `--json` | `safe`            | Yes        | Comparing a drawing with other data      |
| `just count-crossings` | `scripts/count_crossings.py`: crossings between arrows on one page (full paths from `drawio.read`), optionally an id prefix | a .drawio file, page, prefix | Console | `safe` | Yes | Before and after an engine change that alters a consumer's drawing |
| `just flow-quality`   | `scripts/flow_quality.py`: every flow page's audit faults, arrow crossings and shared starts | a map, its schema | Console, exit status | `safe` | Yes | After a routing change, before showing a drawing |
| `just assemble-flowmap` | `scripts/assemble_flowmap.py`: build flows.yaml from its parts | parts/master.yaml | flows.yaml with `--write` | `safe` (`modifies-files` with `--write`) | Yes | After editing a part |
| `just split-flowmap`  | `scripts/split_flowmap.py`: split a map into parts, proved identical | A map | Parts and master with `--apply` | `safe` (`modifies-files` with `--apply`) | Yes | A map grown past a few hundred lines |
| `just yaml-list-patch` | `scripts/yaml_list_patch.py`: add to lists in a map, comments kept           | A YAML map, a JSON spec        | Diff, or the file with `--apply` | `safe` (`modifies-files` with `--apply`) | Yes | Adding reviewed dependencies to a map |
| `just bootstrap`       | Builds the pack's working-cache venv from the mise pin                       | `.mise.toml`, requirements     | venv outside the repo       | `modifies-files`  | Yes        | First use, or after a pin change         |
| `just inventory` / `just audit-scripts` | Tasks and this inventory; script and catalog drift          | `justfile`, this file          | Console                     | `safe`            | Yes        | Orientation, audits                      |
| `just preflight`       | runtimes, audit-scripts, test, check, lint-md                                | Pack files                     | Console                     | `safe`            | Yes        | Before commit or handoff                 |
| `just nav-upgrade-dry-run` / `just nav-upgrade` / `just nav-validate` / `just nav-check-diff` | skill-ai-it navigation layer | skill-ai-it scripts | Console, file changes on upgrade | `review-required` (upgrade) | Yes | When skill-ai-it's blocks change |

## Raw Script Inventory

| Script | Purpose | Safety |
| --- | --- | --- |
| `scripts/render_flowmap.py` | Front end: validate a flow map, report drift, render (`--write`), list flows, audit the layout | `safe` (`modifies-files` with `--write`) |
| `scripts/drawio_export.py` | Front end: export pages (from 1) and layers with the desktop CLI, each under a timeout | `modifies-files` (images only) |
| `scripts/drawio_read.py` | Front end: print an existing drawing's boxes and connections; JSON with geometry | `safe` |
| `scripts/count_crossings.py` | Front end: count crossings between routed arrows on one page (full paths from `drawio.read`), optionally an id prefix | `safe` |
| `scripts/flow_quality.py` | Front end: per flow page, layout-audit faults, arrow crossings and arrows sharing a start point; exit 1 on any | `safe` |
| `scripts/assemble_flowmap.py` | Front end: build the complete flows.yaml from parts/master.yaml and its parts (banner, no pointers); drift check, `--write` to build; refuses a stray part | `safe` (`modifies-files` with `--write`) |
| `scripts/split_flowmap.py` | Front end: split a long map into `#@include` parts (component groups, flow sections, options), proved to load the same; plan, then `--apply` | `safe` (`modifies-files` with `--apply`) |
| `scripts/yaml_list_patch.py` | Add values to flow-style lists in a YAML map's items, comments kept; plan, then `--apply` | `safe` (`modifies-files` with `--apply`) |
| `scripts/schema_lite.py` | A stdlib JSON Schema subset for maps (imported) | `safe` |
| `scripts/code_refs.py` | Check `path[:symbol]` code references in a map against the repository (imported) | `safe` |
| `scripts/drawio/__init__.py` | Package `drawio`: generic draw.io building blocks | `safe` |
| `scripts/drawio/mxfile.py` | Build pages, boxes, routed edges, labels, layers and whole uncompressed files | `safe` |
| `scripts/drawio/cell.py` | One cell's XML: a plain `mxCell`, or a `UserObject` carrying its link, tooltip and draw.io tags; `tag()` makes a tag | `safe` |
| `scripts/drawio/audit.py` | The layout audits (box crossings, diagonals, shared runs, short heads, labels, arc clashes, layers) | `safe` |
| `scripts/drawio/route.py` | Tracks, port spreading, interval tracks, crossing counts, label spots, untwist | `safe` |
| `scripts/drawio/read.py` | Read drawings: page codec, cells, group offsets, line paths, nearest-line label matching | `safe` |
| `scripts/drawio/export.py` | Find the desktop binary, build the export argv, run it under a timeout | `modifies-files` (images only) |
| `scripts/flowmap/__init__.py` | Package `flowmap`: data-first flow maps | `safe` |
| `scripts/flowmap/profile.py` | `Profile`: a project's paths, kind colours, tiers and families; `from_drawing()` defaults | `safe` |
| `scripts/flowmap/model.py` | Load and validate a map (PyYAML at the edge), cross-references, the map's questions | `safe` |
| `scripts/flowmap/overview_layout.py` | Overview geometry: layered group interiors, box text sizing, group edges and channels | `safe` |
| `scripts/flowmap/overview.py` | The Overview page: groups, thick and thin arrows, counts, dots, layers, index, legends | `safe` |
| `scripts/flowmap/e2e_grid.py` | End-to-end grid: placement, link plans, row heights, ports, channel and corridor tracks | `safe` |
| `scripts/flowmap/e2e.py` | End-to-end polylines, crossing-cutting local search, and the drawing | `safe` |
| `scripts/flowmap/overview_index.py` | The Overview's right column: flow index (decision pages linked), kind, status and arrow colour legends | `safe` |
| `scripts/flowmap/options.py` | Decision pages (never called options; optional `options` block or `decision_pages` by subject): decision flow, option step chains, aligned pros and cons | `safe` |
| `scripts/flowmap/shapes.py` | Flow page shapes (flowchart symbols): derivation per step and lane head, per-page shape legend | `safe` |
| `scripts/flowmap/flow_geometry.py` | Flow page geometry: step widths by shape (wider decisions), column gap and positions, run planning and lane room, back-arrow routes below the lanes | `safe` |
| `scripts/flowmap/lanes.py` | Flow page lanes: lane heads (structured text; symbols sized to their text inside a plain panel), room kept for arrow runs, run positions | `safe` |
| `scripts/flowmap/routing.py` | Flow page forward arrows: candidate orthogonal paths scored against what is drawn (boxes, adjacent runs, reused ports, crossings), the cheapest drawn; decision branch labels | `safe` |
| `scripts/flowmap/uncross.py` | Flow page uncrossing pass: two forward arrows that cross are redrawn in the other order, kept only when the page has fewer crossings (`drawing.look.uncross`) | `safe` |
| `scripts/flowmap/tips.py` | Hover texts (components, steps, End-to-end arrows and connectors), draw.io tags, End-to-end colour and layer groups (`look.e2e_layers`) | `safe` |
| `scripts/flowmap/pages.py` | Flow pages, `render`, `evaluate`, `write_drawing`, `flow_list` | `safe` (`write_drawing` writes the drawing) |
| `scripts/check_governance.py` | This pack's governance checker (from skill-ai-it's template) | `safe` |

## Safety Labels

| Label                  | Meaning                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| `safe`                 | Read-only or low-risk repeatable operation                        |
| `review-required`      | Needs human review before execution                               |
| `destructive`          | Deletes, overwrites, migrates, deploys, or changes external state |
| `external-network`     | Calls external services or APIs                                   |
| `modifies-files`       | Writes to repo/project files                                      |
| `requires-secrets`     | Requires secret values                                            |
| `requires-credentials` | Requires authenticated local/session credentials                  |
| `long-running`         | May take significant time                                         |
| `unknown`              | Not yet classified; do not run without inspection                 |

## Governance recipes (skill-ai-it)

- `just govern`: governance up to the current skill-ai-it standard (adoption, record budgets with `just check`, role findings); content fixes are `/skill-ai-it refresh`. `modifies-files`.
- `just roles`: root governance files outside their roles (front matter, README quick start, ROADMAP shape, duplicated sections). Read-only; `safe`.
- `just stale`: stale docs by rule (review due, superseded outside archive/, a Depends on file changed). Read-only; `safe`.
- `just docs [folder]`: one header line per file, to triage before opening. Read-only; `safe`.
- `just history <term>`: search rotated CHANGELOG (or SCRATCHPAD) entries in docs/history. Read-only; `safe`.
- `just history-show <stamp>`: print one rotated entry. Read-only; `safe`.
- `just rotate [--apply]`: move old CHANGELOG/SCRATCHPAD entries and done ROADMAP items to docs/history, verified. Plan by default; `modifies-files`.
- `just budget [--apply]`: bring governed files within budget (normalise, rotate, move reference sections, audit, check). Plan by default; `modifies-files`.
- `just changelog-entry --title ... --body-file ...`: add a CHANGELOG entry in this project's style, with its Contents line. Plan by default; `modifies-files`.
- `just move-sections ...`: move named sections verbatim to an on-need reference doc. Plan by default; `modifies-files`.
- `just outline <file.md>`: each heading with its line range, to read one section instead of the file. Read-only; `safe`.
- `just section <file.md> "<title>"`: print one section (exact title, `Parent > Child`, `#anchor`, `~text`). Read-only; `safe`.
