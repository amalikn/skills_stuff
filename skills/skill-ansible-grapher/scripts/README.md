# scripts/ — inventory

Task runner: `justfile` at the skill root (`just --list`). All entries below are thin
wrappers around `scripts/ansible-grapher`; prefer `just <task>` over calling these
directly unless you need a flag `just` doesn't expose yet.

| Script | Purpose | Inputs | Outputs | Side effects | Safety |
|---|---|---|---|---|---|
| `ansible-grapher` | Primary implementation (Python). All subcommands. | CLI args, `config/*.yaml`, env vars | Graphs, `manifest.json`, `index.md`, logs | Writes under `--output-dir` only | `safe` |
| `discover-ansible-project` | Shim → `ansible-grapher discover` | `--project-root`, `--output-dir` | JSON/Markdown discovery report | Reads only (writes report if `--output-dir` given) | `safe` |
| `graph-inventory` | Shim → `ansible-grapher inventory` | `--inventory`, profile/format flags | DOT/SVG/PNG/PDF | Writes under `--output-dir` | `safe` |
| `graph-playbook` | Shim → `ansible-grapher playbook` | `--playbook`, profile/renderer flags | SVG/Mermaid/JSON | Writes under `--output-dir`; runs `--syntax-check` only, never executes | `safe` |
| `graph-project` | Shim → `ansible-grapher project` | project root, inventory, playbooks | Combined documentation pack | Writes under `--output-dir` | `safe` |
| `validate-ansible-grapher` | Shim → `ansible-grapher validate` | Same as above | Console report only | None (no graphs, no writes) | `safe` |
| `clean-generated-graphs` | Shim → `ansible-grapher clean` | `--output-dir`, `--force` | Console report | Deletes only ownership-marker-verified directories; `modifies-files` when `--force` used | `review-required` (only with `--force`) |

All scripts resolve their Python interpreter from the working-cache venv
(`/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv`), falling
back to system `python3` if that venv is missing.

None of these scripts require network access, secrets, or credentials. None modify
inventories, playbooks, roles, or `ansible.cfg` — see `docs/security-and-safety.md`.
