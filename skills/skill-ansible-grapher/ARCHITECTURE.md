# Architecture — skill-ansible-grapher

## Overview

A thin, safety-first Python/Bash wrapper around two independent upstream FOSS tools.
This skill owns no graphing logic itself — it validates inputs, translates named
profiles into the correct locally-verified CLI flags, invokes the upstream binaries as
subprocesses, and enforces output/safety invariants around them.

```
                 ┌─────────────────────────────────────────┐
                 │      justfile / scripts/* (shims)        │
                 │  discover-ansible-project, graph-*, etc. │
                 └───────────────────┬───────────────────────┘
                                      │ exec (venv python)
                                      ▼
                 ┌─────────────────────────────────────────┐
                 │        scripts/ansible-grapher            │
                 │  (single Python entrypoint, argparse)     │
                 ├─────────────────────────────────────────┤
                 │ discover │ inventory │ playbook │ project │
                 │ validate │ clean     │ profiles │ help    │
                 └───┬───────────┬────────────┬──────────────┘
                     │           │            │
        ┌────────────┘   ┌───────┘    ┌───────┘
        ▼                ▼            ▼
 ansible-inventory   ansible-inventory-grapher   ansible-playbook
 (validation only)   (DOT) → dot (SVG/PNG/PDF)   --syntax-check only
                                                   ↓
                                          ansible-playbook-grapher
                                          (SVG / Mermaid / JSON)
```

## Components

| Component | Role |
|---|---|
| `scripts/ansible-grapher` | Single source of truth for all logic: config loading, executable resolution, safety checks, subprocess invocation, manifest/report generation. Everything else calls into this. |
| `scripts/discover-ansible-project`, `graph-inventory`, `graph-playbook`, `graph-project`, `validate-ansible-grapher`, `clean-generated-graphs` | Thin Bash shims exposing stable, individually-named entrypoints (per the required file list) that just `exec` into the venv Python + `ansible-grapher <subcommand>`. |
| `justfile` | Convenience layer over the same shims/CLI for human/agent use with `just <task>`. |
| `config/default.yaml` | Runtime defaults (output paths, thresholds, redaction patterns, dynamic-inventory/variable policy). Overridable by env vars, then CLI flags. Never overrides a safety invariant defined in `SKILL.md`. |
| `config/profiles.yaml` | Named profiles → concrete CLI flags for each upstream tool, checked against this install's actual `--help` output (`docs/tool-capabilities.md`). |
| `templates/*.tmpl` | Reference shape for `manifest.json`/`index.md`/combined report — documents the canonical output structure; the live implementation builds equivalent output directly in Python for determinism (no Jinja2 dependency). |
| `examples/`, `tests/fixtures/` | Small, safe, local, no-op fixtures (YAML + INI inventory, a debug-only playbook) used for manual trial and automated tests. |
| `scripts/_resolve_python.sh` | Sourced (not executed) by every shim + the justfile. Selects the managed working-cache venv Python; fails clearly (exit 5) if missing rather than silently using system Python; only falls back on explicit opt-in. |
| `tests/test-skill-ansible-grapher.sh` | 29 functional checks: CLI behavior, validation, generation (DOT/SVG/Mermaid/JSON), profiles, redaction, discovery, idempotency. |
| `tests/test-output-safety.sh` | 8 focused safety checks: path containment, overwrite/cleanup/ownership/symlink behavior. |
| `tests/test-toolchain-compatibility.sh` | 13 checks: version-alignment PASS/WARN/FAIL/UNKNOWN, dev-version detection/policy, managed-venv-missing handling, fallback degradation reporting, manifest provenance fields. |
| `tests/test-partial-generation-failure.sh` | 9 checks: fake upstream graphers (via the `ANSIBLE_GRAPHER_*_GRAPHER_BIN` override) that exit 0 but produce no/empty/invalid output — verifies none are ever promoted as successful. |
| `tests/fixtures/fake-tools/` | Small fake executables used only by the two test suites above; never touch the real installed graphers. |
| `.github/workflows/skill-ansible-grapher-ci.yml` | CI workflow: installs stable PyPI releases of both graphers (not this machine's dev-build checkout), runs all four test suites, generates + structurally validates example artifacts, checks determinism across two isolated runs. |
| `docs/*.md` | Reference material: locally-observed tool capabilities, output contract, security model, troubleshooting, profile guide. |

## Data flow

1. **Validate** — every `inventory`/`playbook`/`project` run validates its inputs first
   (`ansible-inventory --list`, `ansible-playbook --syntax-check`) using the *system*
   `ansible-core` (2.21.1), independent of whichever `ansible-core` version each grapher
   tool's own isolated venv happens to pin.
2. **Resolve** — executables are resolved at runtime (CLI flag → env var → `PATH`);
   nothing is hardcoded into committed config.
3. **Assess toolchain compatibility** — `discover_tool_provenance()` introspects the
   resolved grapher binary (raw version, release status, and — for this stack's
   `exec "$VENV/bin/tool"` launcher pattern — the venv's *actual* `ansible-core` version
   via direct interpreter introspection, plus git commit/dirty state from any sibling
   `*-github` checkout). `compute_toolchain_compatibility()` combines that with the
   validation Ansible version into a PASS/WARN/FAIL/UNKNOWN verdict, honoring the
   strict-match and allow-development-versions policies (CLI > env > profile > default —
   see `SKILL.md` §19). A `FAIL` aborts before any graph is generated.
4. **Translate** — the chosen profile name is looked up in `config/profiles.yaml` and
   turned into an argv list for the relevant grapher binary.
5. **Invoke** — `subprocess.run(argv, shell=False, env=deterministic_env())`. Both
   grapher subprocesses get `PYTHONHASHSEED=0` to eliminate process-to-process
   ordering non-determinism (see Key decisions below).
6. **Render** (inventory only) — DOT output is piped through system Graphviz `dot` for
   SVG/PNG/PDF. The playbook grapher renders its own SVG/Mermaid/JSON directly.
7. **Validate artifact content** — `validate_artifact_content()` checks every generated
   file is non-empty and structurally well-formed for its kind (SVG/JSON/Mermaid/DOT)
   *before* it's promoted; an invalid file is deleted and the run reports failure
   (exit 7) rather than silently trusting the upstream tool's exit code.
8. **Write** — atomic write (temp file + rename) into the ownership-marker-tagged output
   directory; refuses to clobber existing files without `--force`.
9. **Report** — manifest (SHA-256 per file, `toolchain_compatibility[]`, `runtime`) +
   Markdown index (for `project`) + a redacted `logs/commands.log` + a console summary
   showing the compatibility verdict and runtime isolation state. Never claims success if
   an expected primary artifact is missing or invalid.

## Key decisions

- **One Python implementation, many thin entrypoints.** The spec calls for 7 named
  scripts; rather than duplicating logic 7 times (and 7 places to introduce drift), all
  behavior lives in `scripts/ansible-grapher` and the other 6 are one-line `exec` shims.
- **`PYTHONHASHSEED=0` for grapher subprocesses.** Both upstream tools iterate Python
  sets/dicts of group/role names without sorting; discovered during build that this made
  output non-deterministic across process runs (same input, different DOT bytes) —
  violates the "idempotent/deterministic" requirement. Pinning the hash seed for those
  two subprocess calls fixes it without touching upstream code.
- **`ansible-inventory --list` fallback detection.** That command exits `0` and silently
  produces an "implicit localhost only" result when every inventory plugin fails to
  parse a source. Treating exit-0 as "valid" would let a broken inventory pass
  validation; `validate_inventory()` additionally checks stderr for the fallback warning.
- **Absolute-path resolution before subprocess dispatch.** `cmd_playbook` originally ran
  with `cwd` pointed at the output directory while playbook paths stayed relative to the
  caller's cwd — this broke real invocations. Fixed by resolving playbook/inventory
  paths to absolute paths immediately and dropping the `cwd` override entirely.
- **Working-cache Python isolation, no silent fallback.** Per this stack's
  runtime-isolation policy, the skill's only Python dependency (PyYAML) lives in a
  dedicated `mise`-pinned venv under `skills-working-cache/skill-ansible-grapher/.venv`,
  not system Python. Originally the shims fell back to system `python3` silently when
  that venv was missing; hardened so `scripts/_resolve_python.sh` now fails clearly
  (exit 5) instead, requiring explicit opt-in (`--allow-system-python-fallback` /
  `ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1`) that is always logged and recorded
  as `runtime_isolation: degraded` when used.
- **No installation logic anywhere.** Both upstream graphers are external, pre-installed
  dependencies. If missing, the skill reports the gap by name (exit `5`) and stops; it
  never attempts `pip install`/`brew install`/upgrade on the user's behalf. The CI
  workflow installs stable released versions from PyPI for testing purposes only — it
  never reinstalls or modifies this machine's local dev-build checkout.
- **Toolchain compatibility is assessed, never assumed.** Discovered during hardening
  that the system `ansible-core` (2.21.1) and `ansible-playbook-grapher`'s own venv
  `ansible-core` (2.18.2) genuinely differ, and that the installed playbook grapher is a
  `2.11.0-dev0` development build — both previously undetected. Added provenance
  discovery, a PASS/WARN/FAIL/UNKNOWN verdict, and strict/permissive policy controls
  rather than silently treating name-matching tools as environment-matching ones.
- **Structural artifact validation.** An upstream tool exiting `0` was previously trusted
  as proof of success. Hardened so every generated SVG/JSON/Mermaid/DOT is checked for
  non-empty, well-formed content before promotion — verified with fake executables in
  `tests/test-partial-generation-failure.sh` that exit 0 while producing no/empty/invalid
  output.
