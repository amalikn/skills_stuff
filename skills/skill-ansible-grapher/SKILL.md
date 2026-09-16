---
name: skill-ansible-grapher
description: "Visualize Ansible inventory/playbook execution as SVG/DOT/Mermaid diagrams."
metadata:
  short-description: Graph Ansible inventories and playbooks
---

# Skill: Ansible Grapher

## 1. Purpose

Produce local, FOSS, reproducible visualizations and documentation of:

- **Inventory topology** (groups, child-group relationships, host membership) via
  [`ansible-inventory-grapher`](https://github.com/willthames/ansible-inventory-grapher).
- **Playbook execution structure** (plays, tasks, roles, blocks, includes, handlers) via
  [`ansible-playbook-grapher`](https://github.com/haidaraM/ansible-playbook-grapher).

Both tools are already installed on this machine (see `docs/tool-capabilities.md`). This
skill does not install, upgrade, downgrade, or otherwise modify them.

## 2. When to use

- Documenting or reviewing an Ansible repo's inventory topology or playbook structure.
- Onboarding, architecture review, change review, or troubleshooting that benefits from a
  diagram of "what groups/hosts exist" or "what a playbook actually does, structurally."
- CI artifact generation for Ansible repos (deterministic, low-cost `ci-light` profile).

## 3. When NOT to use

- To execute, apply, or "run" a playbook. This skill never invokes `ansible-playbook`
  without `--syntax-check`, and never invokes bare `ansible`/ad hoc commands.
- To modify inventories, playbooks, roles, variables, vaults, or `ansible.cfg`. If
  remediation is needed, that is a separate, explicitly-requested task.
- To prove runtime correctness. Static graphs show parsed structure, not execution
  outcome — see §19 Known limitations.
- To graph a dynamic/cloud inventory plugin without explicit user approval (§15).

## 4. Tool selection rules

| Question | Tool |
|---|---|
| "What hosts/groups exist and how do they relate?" | `ansible-inventory-grapher` (`inventory` subcommand) |
| "What does this playbook do, structurally — plays/tasks/roles/handlers?" | `ansible-playbook-grapher` (`playbook` subcommand) |
| "Both, as a documentation pack" | `project` subcommand (combined) |
| "What's in this repo and what should I graph?" | `discover` subcommand |
| "Are my tools/inputs even valid?" | `validate` subcommand (no graphs generated) |

Never substitute one tool for the other — inventory topology and playbook execution
structure are different domains with different CLI surfaces (see `docs/tool-capabilities.md`).

## 5. Safety contract

This is a **visualization and documentation skill**, not an execution skill:

- Never runs a playbook against managed hosts.
- Never invokes `ansible-playbook` without `--syntax-check`.
- Never runs ad hoc `ansible` commands.
- Never modifies inventories, playbooks, roles, variables, vaults, or `ansible.cfg`.
- Never decrypts, prints, copies, embeds, or exposes vault secrets.
- Never treats successful graph generation as proof of runtime correctness.
- Denies dynamic/cloud inventory execution by default (§15).
- Suppresses inventory variable display by default (§16).
- Refuses to overwrite existing artifacts without `--force`.
- Refuses to clean any directory lacking this skill's ownership marker.
- Redacts vault/extra-vars/secret-like values in logs and manifests, always.

## 6. Project discovery workflow

1. `ansible-grapher discover --project-root <path> [--output-dir <path>]`
2. Discovery walks the tree (bounded by `config/default.yaml` → `discovery.max_files_scanned`
   / `max_recursion_depth`), skipping `.git`, `.venv`, `node_modules`, etc.
3. It identifies `ansible.cfg`, inventory candidates (validated with `ansible-inventory`,
   never selected just because the filename contains "hosts"), playbook candidates
   (validated by checking for playbook-shaped top-level YAML keys), `roles/`, collections,
   `requirements.yml`, `group_vars/`, `host_vars/`.
4. It recommends a **bounded** graphing plan (primary inventory, a capped number of
   primary playbooks, suggested profiles, and risks) — it does not graph everything found.
5. Read the recommendation before running `inventory`/`playbook`/`project`.

## 7. Inventory graph workflow

1. Validate first: `ansible-inventory -i <inventory> --list` must succeed and actually
   parse (a `0` exit with "no inventory was parsed" fallback is treated as failure).
2. Deny dynamic inventory unless `--allow-dynamic-inventory` was explicitly given (§15).
3. Run `ansible-inventory-grapher` to produce DOT (variables suppressed unless
   `--show-variables`).
4. Render DOT → requested formats (svg/png/pdf) via system Graphviz `dot`.
5. `ansible-grapher inventory --inventory <path> [--pattern P] [--profile NAME] [--format svg,...] [--show-variables] [--output-dir DIR] [--force]`

## 8. Playbook graph workflow

1. Validate first: `ansible-playbook --syntax-check <playbook>` for every playbook (with
   `-i` only if an inventory was supplied).
2. Run `ansible-playbook-grapher` with the profile's flags (see `config/profiles.yaml`
   and `docs/profile-reference.md`), any `--tags`/`--skip-tags`, `-e` extra-vars.
3. `ansible-grapher playbook --playbook <path> [--playbook <path> ...] [--inventory <path>] [--profile NAME] [--renderer graphviz|mermaid-flowchart|json] [--tags T] [--skip-tags T] [--extra-vars V] [--output-dir DIR] [--force]`
4. Extra-vars values are never echoed to chat output and are redacted in
   `logs/commands.log` and `manifest.json`.

## 9. Combined graph workflow

`ansible-grapher project --project-root <path> [--inventory <path>] [--playbook <path> ...] [--profile documentation-pack|ci-light] [--output-dir DIR] [--force]`

Produces inventory SVG+DOT, playbook SVG (+ Mermaid + JSON for `documentation-pack`),
`manifest.json`, and `index.md` under one output root.

## 10. Validation workflow

`ansible-grapher validate [--project-root P] [--inventory I] [--playbook B ...] [--output-dir D] [--format text|json] [--strict-ansible-version-match] [--allow-ansible-version-mismatch] [--allow-development-tool-versions] [--reject-development-tool-versions]`

Checks: managed Python environment, executable resolution, tool versions + release
status, Ansible-version alignment (§21), Graphviz availability, renderer support, profile
validity, output path safety, inventory parseability, playbook syntax, and the
dynamic-inventory/development-version/strict-compatibility policy in effect. Generates
**no graphs**. Each check reports PASS/WARN/FAIL/UNKNOWN; `--format json` emits a
machine-readable `{"status": ..., "checks": [...]}` report. Exit `0` unless overall
status is `FAIL` (strict mode promotes WARN → FAIL — see §21).

## 11. Output contract

See `docs/output-contract.md` for the full schema. Summary:

- Default root: `.ai-artifacts/ansible-grapher/` in the calling project — never beside
  source inventories/playbooks, never machine-global.
- Deterministic filenames, no timestamps in primary artifact names.
- `manifest.json` (schema v2: versions, sources, generated files + SHA-256, warnings,
  `toolchain_compatibility[]`, `runtime`) and `index.md` on every `project` run.
- Existing artifacts are never overwritten without `--force`.
- Every generated artifact (SVG/JSON/Mermaid/DOT) passes a structural sanity check
  before being promoted — an upstream tool exiting `0` is not treated as proof it
  produced valid output (§21, §12).

## 12. Error handling

- Missing executable → exit `5`, names the missing tool, never attempts to install it.
- Invalid inventory/playbook → exit `4`, reports the parser error, generates nothing.
- Unsafe output path (`/`, `$HOME`, symlink escape) → exit `6`, refuses to proceed.
- Partial generation (expected primary artifact missing, empty, or structurally invalid
  after a "successful" subprocess call) → exit `7`, never claims success, never leaves
  an invalid or partial artifact on disk (see `tests/test-partial-generation-failure.sh`).
- Toolchain compatibility `FAIL` (strict mode + version mismatch/unknown, or a
  disallowed development-version tool) → exit `4`, before any graph is generated (§21).
- Managed Python venv missing and no fallback opt-in given → exit `5`, from the shim
  layer, before Python even starts (§21).

## 13. Large-project strategy

- Inventory host count above `thresholds.max_inventory_hosts_before_warning` (default 200)
  triggers a warning recommending a narrower `--pattern` or the `inventory-summary` profile.
- Discovery caps auto-recommended playbooks at `thresholds.max_auto_selected_playbooks`
  (default 5) and reports how many were dropped.
- Prefer SVG over PNG for large graphs; prefer Mermaid/JSON for repo-native docs.
- Never generate a graph for every YAML file found — discovery recommends, it does not
  auto-execute across the whole repo.

## 14. Dynamic inventory policy

**Deny by default.** An inventory source that is an executable file without a
`.yml`/`.yaml`/`.ini` extension is treated as a dynamic/plugin inventory and refused
(exit `6`) unless `--allow-dynamic-inventory` (or
`ANSIBLE_GRAPHER_ALLOW_DYNAMIC_INVENTORY=1`) is set — and that should only happen after
explicit user approval, because such sources may execute local code or contact AWS,
Azure, GCP, VMware, NetBox, or similar external systems. Discovery may *identify* a
dynamic source; it never executes one.

## 15. Vault and secret policy

- Vault password files/IDs may be passed through to the underlying tools; this skill
  never reads their contents.
- `--ask-vault-pass`/interactive vault prompts are not appropriate for unattended runs.
- `--extra-vars` values and any `redaction.redact_flags` (see `config/default.yaml`) are
  replaced with `***REDACTED***` in `logs/commands.log` and `manifest.json`.
- Never copy graph contents into chat output when `--show-variables` was used — report
  only artifact paths; the caller inspects the file locally.

## 16. Cleanup and overwrite policy

- Every generated output root gets a `.ansible-grapher-owned` marker on first write.
- `ansible-grapher clean --output-dir <path>` without `--force` is a dry-run.
- `--force` deletes only if the marker is present and well-formed; refuses symlinked
  roots; never follows symlinks while walking.
- Re-running the same command into the same output dir without `--force` fails with a
  clear "refusing to overwrite" error; with `--force` it succeeds and is idempotent.

## 17. Required final run report

Every run prints: mode, profile, validated inputs, output directory, generated artifact
paths, warnings, and the next command to inspect output (`ls -la <dir>`). Never claim
success if a requested primary artifact was not produced (exit `7` instead).

## 18. Example invocations

```bash
# Discover a repo and get a bounded recommendation
scripts/discover-ansible-project --project-root /path/to/ansible-repo

# Graph an inventory (variables suppressed)
scripts/graph-inventory --inventory /path/to/hosts.yml --profile inventory-summary

# Graph a playbook as Mermaid for embedding in Markdown
scripts/graph-playbook --playbook /path/to/site.yml --profile playbook-mermaid

# Full documentation pack for a project
scripts/graph-project --project-root /path/to/ansible-repo \
  --inventory /path/to/hosts.yml --playbook /path/to/site.yml

# Validate only, no graphs
scripts/validate-ansible-grapher --inventory /path/to/hosts.yml --playbook /path/to/site.yml

# just recipes (see justfile)
just inventory /path/to/hosts.yml inventory-left-right
just playbook /path/to/site.yml playbook-roles
just clean .ai-artifacts/ansible-grapher --force

# Machine-readable validation report
scripts/validate-ansible-grapher --format json

# ci-light with explicit override (this machine's playbook grapher is a dev build — §19)
scripts/graph-project --project-root /path/to/repo --inventory /path/to/hosts.yml \
  --playbook /path/to/site.yml --profile ci-light \
  --allow-ansible-version-mismatch --allow-development-tool-versions
```

Machine-specific setup (this install): set
`ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN` and `ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN` to the
`tools_stuff` launcher scripts — see `README.md` §Prerequisites.

## 19. Runtime provenance and toolchain compatibility policy

Each grapher runs in its **own isolated venv** with its own `ansible-core` version,
independent of the system `ansible-core` used for `--syntax-check`/`--list` validation
(see `docs/tool-capabilities.md`). This skill discovers and reports that, rather than
assuming matching tool names imply matching environments.

**Provenance discovered per tool:** resolved executable path, raw `--version` output,
release status (`stable`/`prerelease`/`development`/`unknown`), whether it's a
venv-wrapper launcher, the venv's actual `ansible-core` version (via direct interpreter
introspection, not guesswork), and — when the launcher points at a local `*-github`
checkout — commit SHA and dirty/clean state (nothing else from that repo is read).

**Compatibility verdict** (`PASS`/`WARN`/`FAIL`/`UNKNOWN`) combines version alignment and
development-tool-version policy:

| Condition | Non-strict (default) | Strict (`--strict-ansible-version-match`) |
|---|---|---|
| Versions match | PASS | PASS |
| Versions differ | WARN | FAIL |
| Version(s) unknown | UNKNOWN | FAIL |
| Dev/prerelease tool, allowed | WARN | (combines with above) |
| Dev/prerelease tool, disallowed | FAIL | FAIL |

A `FAIL` verdict aborts the run (exit `4`) **before** any graph is generated — it is
never silently downgraded to a warning to keep a command "succeeding."

**Policy resolution precedence** (highest wins): CLI flag > environment variable >
profile value > `config/default.yaml` default.

| Policy | CLI flags | Env var | Config key |
|---|---|---|---|
| Strict version match | `--strict-ansible-version-match` / `--allow-ansible-version-mismatch` | `ANSIBLE_GRAPHER_STRICT_ANSIBLE_VERSION_MATCH` | `compatibility.strict_ansible_version_match_default` (false) |
| Allow dev/prerelease tools | `--allow-development-tool-versions` / `--reject-development-tool-versions` | `ANSIBLE_GRAPHER_ALLOW_DEVELOPMENT_TOOL_VERSIONS` | `compatibility.allow_development_tool_versions_default` (true) |

**`ci-light` hardens both**: `strict_ansible_version_match: true` and
`allow_development_tool_versions: false` — see `docs/profile-reference.md`. On this
machine, `ci-light` **without an override fails** because the installed
`ansible-playbook-grapher` is a development build (`2.11.0-dev0`) whose venv pins a
different `ansible-core` than the system validator. That is the policy working as
designed, not a defect — pass `--allow-ansible-version-mismatch
--allow-development-tool-versions` (or use `documentation-pack`/interactive profiles) to
proceed anyway.

**Managed Python runtime.** The managed working-cache venv
(`skills-working-cache/skill-ansible-grapher/.venv`) is used by default. If it is
missing, `scripts/*` and the `justfile` **fail clearly** (exit `5`) rather than silently
using system Python — see `scripts/_resolve_python.sh`. Fallback requires explicit opt-in
(`--allow-system-python-fallback` or `ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1`),
is always logged as a warning, and is recorded in the manifest/validate output as
`runtime_isolation: degraded` (compatibility status floors at `WARN`).

**Structural artifact validation.** Every generated SVG/JSON/Mermaid/DOT artifact is
checked for non-empty, well-formed content before being promoted to the output
directory — an upstream tool exiting `0` is not treated as proof it produced valid
output. See `tests/test-partial-generation-failure.sh`.

## 20. Known limitations

- Static analysis cannot fully resolve runtime facts, dynamic variables, loops,
  conditionals, or variable-dependent includes. A generated graph is evidence of parsed
  structure, not proof of execution order or successful deployment.
- `ansible-inventory-grapher` only emits DOT; SVG/PNG/PDF come from Graphviz `dot`
  rendering that DOT, not from the grapher itself.
- Both graphers iterate Python collections whose default ordering depends on
  `PYTHONHASHSEED`; this skill pins `PYTHONHASHSEED=0` for grapher subprocesses to keep
  output byte-for-byte reproducible (see `docs/troubleshooting.md`).
- `ansible-inventory --list` exits `0` and silently falls back to "implicit localhost
  only" when every inventory plugin fails to parse a source; this skill treats that
  fallback as a validation failure rather than a valid empty inventory.

## 21. Completion criteria

A run is complete only when: validation passed, every requested primary artifact exists
on disk **and passes structural validation**, `manifest.json`/`index.md` were written
(for `project`), toolchain compatibility was `PASS`/`WARN` (or an explicit override was
given for a `FAIL`), no source file was modified, and the final report was printed. See
`tests/test-skill-ansible-grapher.sh`, `tests/test-output-safety.sh`,
`tests/test-toolchain-compatibility.sh`, and `tests/test-partial-generation-failure.sh`
for the automated version of these checks (59 checks total), and
`.github/workflows/skill-ansible-grapher-ci.yml` for the CI-equivalent run.
