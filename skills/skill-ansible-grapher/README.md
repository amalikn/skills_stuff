# skill-ansible-grapher

Visualize Ansible **inventory topology** and **playbook execution structure** — locally,
reproducibly, and without ever executing anything against managed hosts.

## What this does

Two separate upstream FOSS tools, one consistent interface:

| Tool | Domain | Output |
|---|---|---|
| [ansible-inventory-grapher](https://github.com/willthames/ansible-inventory-grapher) | Inventory groups, child-group relationships, host membership | DOT (rendered to SVG/PNG/PDF via Graphviz) |
| [ansible-playbook-grapher](https://github.com/haidaraM/ansible-playbook-grapher) | Plays, tasks, roles, blocks, includes, handlers | Graphviz SVG, Mermaid, or JSON |

They are not interchangeable — inventory topology and playbook structure are different
questions. See `docs/tool-capabilities.md`.

## Prerequisites

Both tools are already installed on this machine under `tools_stuff/`. This skill does
not install or modify them. Point the wrapper at their launcher scripts:

```bash
export ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN=/Volumes/Data/_ai/_tools/tools_stuff/ansible-inventory-grapher/scripts/ansible-inventory-grapher.sh
export ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN=/Volumes/Data/_ai/_tools/tools_stuff/ansible-playbook-grapher/scripts/ansible-playbook-grapher.sh
```

(Add these to your shell profile, or a project-local `.envrc`/`.env` that you source
before invoking this skill — the skill itself never hardcodes them.)

Also required: `ansible-inventory`, `ansible-playbook` (from any local `ansible-core`),
and Graphviz `dot`. Run `just validate` (or `scripts/validate-ansible-grapher`) to check.

The skill's own Python dependency (PyYAML) is isolated in a working-cache venv — see
`.mise.toml` and **Environment isolation** below. You do not need to install PyYAML
system-wide.

## Toolchain compatibility

Each grapher runs in its own isolated venv with its own `ansible-core` version,
independent of the system `ansible-core` used for validation. This skill detects and
reports that (never silently), with a `PASS`/`WARN`/`FAIL`/`UNKNOWN` verdict recorded in
`manifest.json` and the console report. Default is warn-only; `--strict-ansible-version-match`
makes mismatches (and unknown versions) hard failures. `ci-light` enables strict mode and
rejects development/prerelease tool builds by default — **on this machine that means
`ci-light` fails without an explicit override**, because the installed
`ansible-playbook-grapher` is a `2.11.0-dev0` build. See `SKILL.md` §19 and
`docs/profile-reference.md`.

```bash
# Interactive default: warns, doesn't fail
just validate

# Machine-readable, same checks
scripts/validate-ansible-grapher --format json

# ci-light needs an explicit override on this machine (dev-build playbook grapher)
scripts/graph-project --project-root . --inventory hosts.yml --playbook site.yml \
  --profile ci-light --allow-ansible-version-mismatch --allow-development-tool-versions
```

## Supported modes

- `discover` — bounded recommendation of what to graph in an unfamiliar repo.
- `inventory` — graph an inventory (variables suppressed by default).
- `playbook` — graph one or more playbooks (graphviz/mermaid/json).
- `project` — combined documentation pack (inventory + playbook + manifest + index).
- `validate` — check tools/inputs/output-path safety without generating graphs.
- `clean` — safely remove a previously generated output directory.
- `profiles` — list available profiles.

## Quick start

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/skills/skill-ansible-grapher

# via just (recommended)
just validate
just discover /path/to/ansible-repo
just inventory /path/to/hosts.yml inventory-summary
just playbook /path/to/site.yml playbook-summary
just project /path/to/ansible-repo /path/to/hosts.yml /path/to/site.yml

# via scripts directly
scripts/validate-ansible-grapher --inventory /path/to/hosts.yml
scripts/graph-inventory --inventory /path/to/hosts.yml --profile inventory-summary
scripts/graph-playbook --playbook /path/to/site.yml --profile playbook-mermaid
```

## Profiles

See `config/profiles.yaml` and `docs/profile-reference.md` for the full list:
`inventory-summary`, `inventory-detailed`, `inventory-left-right`, `inventory-uml`,
`playbook-summary`, `playbook-roles`, `playbook-detailed`, `playbook-mermaid`,
`playbook-json`, `documentation-pack`, `ci-light`.

## Output layout

```
.ai-artifacts/ansible-grapher/
├── .ansible-grapher-owned      # ownership marker (required for `clean`)
├── manifest.json
├── index.md
├── inventory/{inventory.dot,inventory.svg,...}
├── playbooks/{name.svg,name.mmd,name.json,...}
└── logs/commands.log            # redacted command record
```

See `docs/output-contract.md`.

## Safety model

Visualization/documentation only. Never executes a playbook (only `--syntax-check`),
never modifies inventories/playbooks/vaults, denies dynamic inventory by default,
suppresses variable display by default, redacts secrets in logs/manifests, refuses
unsafe output paths, only cleans directories it owns, never silently falls back to
system Python, and never promotes an empty/invalid generated artifact as a success.
Full details in `docs/security-and-safety.md`, `SKILL.md` §5, and `SKILL.md` §19
(runtime provenance and toolchain compatibility).

## Limitations

Static graphs show parsed structure, not runtime truth — see `SKILL.md` §19 and
`docs/tool-capabilities.md`.

## Environment isolation

Per this stack's runtime-isolation policy, the skill's Python dependency (PyYAML) lives
in a dedicated `mise`-pinned venv under
`/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv`
(Python 3.14 — the pinned default; 3.10–3.14 is the documented supported range, not a
hard requirement). `scripts/*` and the `justfile` resolve that venv's `python`
automatically and **fail clearly (exit 5)** if it's missing — they do not silently fall
back to system `python3`. To rebuild it:

```bash
cd /Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher
mise install
mise exec -- python -m venv .venv
.venv/bin/python -m pip install PyYAML
```

To explicitly opt into a system-Python fallback instead (e.g. a throwaway environment
without the venv), pass `--allow-system-python-fallback` or set
`ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1` — this is always logged and recorded as
`runtime_isolation: degraded`, never silent. See `SKILL.md` §19 and
`docs/security-and-safety.md`.

## Troubleshooting

See `docs/troubleshooting.md`.

## Codex / Claude Code / local LLM usage

- **Codex / Claude Code**: invoke via the `scripts/` entrypoints or `justfile` recipes
  above; read `SKILL.md` first for the full behavioral contract.
- **Local LLM agents**: the same `scripts/ansible-grapher` CLI works standalone —
  `python3 scripts/ansible-grapher --help` (or the venv python) needs no network access
  and no cloud credentials.

## Upstream projects

- https://github.com/willthames/ansible-inventory-grapher
- https://github.com/haidaraM/ansible-playbook-grapher

Both are FOSS (see their respective LICENSE files); this skill only wraps their CLIs.

## Tests

```bash
just test
# or directly:
bash tests/test-skill-ansible-grapher.sh          # 29 checks
bash tests/test-output-safety.sh                  # 8 checks
bash tests/test-toolchain-compatibility.sh         # 13 checks
bash tests/test-partial-generation-failure.sh      # 9 checks
```

59 checks total. See `.github/workflows/skill-ansible-grapher-ci.yml` for the CI
workflow (installs stable released grapher versions from PyPI — see
`docs/tool-capabilities.md` § Local vs. CI tool versions for why that necessarily
differs from this machine's dev-build install).

## Governance pointers

- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Local agent guidance: [AGENTS.md](AGENTS.md)
- Claude Code entrypoint: [CLAUDE.md](CLAUDE.md)
- AI navigation entrypoint: [AI_NAVIGATION.md](AI_NAVIGATION.md)
- Machine-readable context map: [context-map.yaml](context-map.yaml)
- Script/task inventory: [scripts/README.md](scripts/README.md)
- Change history: [CHANGELOG.md](CHANGELOG.md)
- Parent skills guidance: [../../AGENTS.md](../../AGENTS.md)
- Canonical governance root: `/Volumes/Data/_ai/governance/README.md`
