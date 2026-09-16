# Output contract

## Root

Default: `.ai-artifacts/ansible-grapher/` inside the **calling project** (never inside
this skill directory, never beside source inventories/playbooks, never a machine-global
path). Override with `--output-dir` / `ANSIBLE_GRAPHER_OUTPUT_DIR`.

Refused output roots: `/`, `$HOME`, and any symlinked root (for `clean`).

## Layout

```
<output-dir>/
├── .ansible-grapher-owned       # ownership marker, written on first use
├── manifest.json                # only for `project` mode
├── index.md                     # only for `project` mode
├── inventory/
│   ├── inventory.dot
│   ├── inventory.svg
│   └── inventory.png / .pdf     # only if requested
├── playbooks/
│   ├── <name>.svg                # graphviz renderer
│   ├── <name>.dot                # only with --save-dot-file / playbook-detailed profile
│   ├── <name>.mmd                # mermaid-flowchart renderer
│   └── <name>.json               # json renderer
└── logs/
    └── commands.log              # JSON-lines, redacted
```

`<name>` is the source playbook's filename stem, or `combined` when multiple playbooks
are graphed in one call.

## Naming rules

- Deterministic: identical inputs + profile → identical filenames, byte-identical
  content (both grapher subprocesses run with `PYTHONHASHSEED=0` — see
  `docs/troubleshooting.md`).
- No timestamps in primary artifact filenames. Timestamps, when needed, appear only
  inside `manifest.json` metadata.
- Writes are atomic: content is written to a `.tmp.<pid>` sibling and renamed into place.
- Every artifact is structurally validated before promotion (non-empty; SVG contains
  `<svg`; JSON parses and is non-empty; Mermaid contains a graph declaration; DOT starts
  with `graph`/`digraph`) — an invalid or empty artifact is deleted, not left on disk,
  and the run exits `7` (`EXIT_PARTIAL_FAILURE`). See `tests/test-partial-generation-failure.sh`.

## Overwrite rules

- Without `--force`: an existing artifact at the target path causes the run to fail
  (exit `6`) before any subprocess is invoked for that artifact.
- With `--force`: the artifact is regenerated and replaces the existing file.
- Re-running the identical command with `--force` twice must produce byte-identical
  output (verified by `tests/test-skill-ansible-grapher.sh`: idempotency check).

## manifest.json schema (schema_version: 2)

```jsonc
{
  "schema_version": 2,
  "skill_version": "0.2.0",
  "mode": "project",
  "profile": "documentation-pack",
  "output_root": "/abs/path/.ai-artifacts/ansible-grapher",
  "generated_files": [
    {"path": "inventory/inventory.svg", "sha256": "...", "size_bytes": 1234}
  ],
  "warnings": ["..."],
  "toolchain_compatibility": [
    {
      "status": "PASS|WARN|FAIL|UNKNOWN",
      "validation_ansible_version": "2.21.1",
      "grapher_label": "ansible-playbook-grapher",
      "grapher_ansible_version": "2.18.2",
      "grapher_tool_version": "ansible-playbook-grapher 2.11.0-dev0 (with ansible 2.18.2)",
      "grapher_release_status": "development",
      "version_match": false,
      "strict_mode": false,
      "allow_development_tool_versions": true,
      "reasons": ["..."]
    }
  ],
  "runtime": {
    "python_executable": "/path/to/.venv/bin/python",
    "python_version": "3.14.5",
    "python_in_supported_range": true,
    "managed_venv_expected": "/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv",
    "python_fallback_used": false,
    "runtime_isolation": "managed"
  }
}
```

Every entry in `generated_files` has a SHA-256 and byte size. `.ansible-grapher-owned`
and `manifest.json` itself are excluded from the file list. `toolchain_compatibility` has
one entry per grapher tool actually invoked during the run (see `SKILL.md` §19). Schema
v1 (no `toolchain_compatibility`/`runtime` keys) is superseded — v1 consumers should treat
the absence of these keys as "not assessed," not "compatible."

## Cleanup ownership

- `clean` refuses to act on any directory lacking a well-formed `.ansible-grapher-owned`
  marker (`{"schema": "ansible-grapher-owned", "skill_version": "..."}`).
- `clean` refuses a symlinked output root, and never follows symlinks while walking the
  tree during deletion (matched files/dirs that are themselves symlinks are skipped, not
  deleted, and their targets are left untouched).
- Without `--force`, `clean` is a dry-run that reports what it would remove.
