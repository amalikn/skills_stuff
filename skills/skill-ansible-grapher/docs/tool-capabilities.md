# Tool capabilities (locally observed, 2026-07-01)

This is the actual `--version`/`--help` output on this machine, not upstream README
claims. Treat this as authoritative for what flags this install actually supports — do
not assume a newer/older upstream version behaves identically.

## ansible-inventory-grapher

```
ansible-inventory-grapher 2.6.0
```

```
Usage: ansible-inventory-grapher [options] pattern1 [pattern2 ...]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -i INVENTORY          specify inventory host file [['/etc/ansible/hosts']]
  -d DIRECTORY          Location to output resulting files [current directory]
  -o FORMAT, --format=FORMAT
                        python format string to name output files (e.g. {}.dot)
                        [defaults to stdout]
  -q, --no-variables    Turn off variable display in default template
  -t TEMPLATE           path to jinja2 template used for creating output
  -T                    print default template
  -a ATTRIBUTES         include top-level graphviz attributes [rankdir=TB;]
  --ask-vault-pass      prompt for vault password
  --vault-password-file=VAULT_PASSWORD_FILES
                        vault password file
  --vault-id=VAULT_IDS  the vault identity to use
  --visible-vars=VISIBLE_VARS
                        Show value of a specific variable. Repeat for multiple variables
  --show-all-values     Show values of all variables
```

**Important:** this tool only emits **DOT** to stdout (or to files via `-o`/`-d`). It
does **not** render SVG/PNG/PDF itself — this skill pipes its DOT output through system
Graphviz `dot -T<format>` for that. There is no `--rankdir` flag; orientation is set via
`-a "rankdir=LR;"` (top-level Graphviz graph attributes).

## ansible-playbook-grapher

```
ansible-playbook-grapher 2.11.0-dev0 (with ansible 2.18.2)
```

Key flags this skill uses (full `--help` output is longer — run
`scripts/graph-playbook --help` if you need the rest):

- `--renderer {graphviz,mermaid-flowchart,json}` — default `graphviz`
- `--renderer-mermaid-orientation {TD,RL,BT,LR}` — default `LR`
- `--include-role-tasks`, `--only-roles`, `--group-roles-by-name`
- `--hide-plays-without-roles`, `--hide-empty-plays`
- `--show-handlers`, `--collapsible-nodes`
- `-s`/`--save-dot-file` (only meaningful with the graphviz renderer)
- `-t`/`--tags`, `--skip-tags` (repeatable)
- `-e`/`--extra-vars` (repeatable) — always redacted in this skill's logs/manifests
- `-i`/`--inventory`, `--vault-id`, `--vault-password-file`
- `-o`/`--output-file-name` — extension added automatically per renderer
- `--view` — **never used by this skill** (no automatic viewer launch)

**Important:** this tool's own runtime uses `ansible-core 2.18.2` (pinned in its
isolated venv, per `tools_stuff/ansible-playbook-grapher/AGENTS.md`'s `<2.18.3`
constraint) — different from the system `ansible-core 2.21.1` used for
`ansible-inventory`/`ansible-playbook --syntax-check` validation. Both are valid; they
serve different purposes (graphing vs. validation). This skill does not silently
reconcile the mismatch — it is discovered, reported (WARN by default, FAIL in
`--strict-ansible-version-match` mode), and recorded in `manifest.json` as
`toolchain_compatibility`. See `SKILL.md` §19 and `docs/troubleshooting.md`.

The version string itself (`2.11.0-dev0`) is also detected as a **development** release
(not `stable`) and reported accordingly — `allow_development_tool_versions_default: true`
in `config/default.yaml` permits it for interactive use; `ci-light` disallows it by
default (see `docs/profile-reference.md`).

### Local vs. CI tool versions

`.github/workflows/skill-ansible-grapher-ci.yml` installs the latest **stable released**
versions of both graphers from PyPI — it cannot reproduce this machine's editable-checkout
dev build. Feature detection (which flags exist) is always driven by the CI-installed
version's actual `--help` output at run time, never assumed from this document. Do not
read a passing CI run as evidence about the exact local `2.11.0-dev0` build; read it as
evidence that the skill's *logic* (validation, profiles, safety controls, structural
artifact checks) works against a real, stable, independently-versioned install.

## ansible-core / Graphviz

```
ansible [core 2.21.1]
dot - graphviz version 15.0.0 (20260523.1842)
```

## Renderer → file extension mapping used by this skill

| Renderer | Extension | Notes |
|---|---|---|
| `graphviz` | `.svg` (+ optional `.dot` with `--save-dot-file`) | Rendered directly by the grapher via its own Graphviz call, not piped through this skill's `dot` invocation (that path is inventory-only) |
| `mermaid-flowchart` | `.mmd` | Raw Mermaid source; embed in Markdown with a ```` ```mermaid ```` fence |
| `json` | `.json` | Machine-readable, preserves source-location metadata |
