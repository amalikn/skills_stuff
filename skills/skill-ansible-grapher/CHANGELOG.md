# Changelog

## 20260701_1930 — troubleshooting doc: two real-world toolchain gaps found on ansible-wifi

### Added
- `docs/troubleshooting.md` — two new sections from a live run against the `ansible-wifi`
  repo:
  1. `couldn't resolve module/action` from the playbook grapher despite a clean
     `--syntax-check`: the grapher's isolated venv is bare `ansible-core` pip install
     with zero bundled collections, so standard-collection modules (e.g. `ansible.posix.mount`)
     fail to resolve even though `requirements.yml` is irrelevant here. Documented the
     `ANSIBLE_COLLECTIONS_PATH` env workaround (project's `./collections` + a source that
     actually has the missing collection, e.g. Homebrew's bundled `ansible` package).
  2. Graphviz renderer crash (`TypeError` sorting `NoneType` handler indices in
     `graph_model.py`'s `get_notified_handlers()`) on a development-build
     `ansible-playbook-grapher` (`2.11.0-dev0`) — playbook-specific, not a repo bug.
     Documented the `--profile playbook-mermaid` / `--renderer json` workaround.

No functional/script changes — doc-only, no version bump (`0.2.0` unchanged).

## 20260701_1800 — coherence check (report trim) + skill installed

### Changed
- `docs/reports/skill-ansible-grapher-implementation.md` trimmed to a more concise form
  (CI-workflow-specific sections condensed/generalized; `ci-light` wording generalized to
  "strict profile execution"). The underlying facts are unchanged: `.github/workflows/skill-ansible-grapher-ci.yml`
  still exists, `just ci-check` still works as documented, all 59 tests still pass.
- Coherence check: grepped for stale `37/37`/old test counts, `schema_version: 1`, and
  pre-0.2.0 version strings across the package — zero hits. Version strings (`0.2.0`),
  schema version (`2`), and test totals (`59`) confirmed consistent across
  `scripts/ansible-grapher`, `context-map.yaml`, and this file. Re-ran all four test
  suites unchanged — 59/59 still passing.

### Added
- `~/.claude/skills/skill-ansible-grapher` symlink (install into Claude Code), matching
  the current `skills_stuff` symlink-install convention.

## 0.2.0 (20260701_1500) — hardening/closure pass: runtime provenance, toolchain compatibility, structural artifact validation

Closes the remaining gaps from the 0.1.0 implementation report (see that report's
"Known limitations" and `SCRATCHPAD.md`'s "Open items").

### Added
- **Runtime provenance discovery** (`discover_tool_provenance()`): resolved path, raw
  `--version`, release status (`stable`/`prerelease`/`development`/`unknown`), venv-wrapper
  detection with direct interpreter introspection for the actual `ansible-core` version,
  and git commit/dirty state from any sibling `*-github` checkout.
- **Toolchain compatibility verdict** (`compute_toolchain_compatibility()`):
  PASS/WARN/FAIL/UNKNOWN, recorded in `manifest.json` (`toolchain_compatibility[]`,
  schema v2) and the console report. Never silently treats an unknown or mismatched
  version as compatible.
- **Policy controls**: `--strict-ansible-version-match` / `--allow-ansible-version-mismatch`,
  `--allow-development-tool-versions` / `--reject-development-tool-versions`, matching env
  vars and `config/default.yaml` → `compatibility.*` defaults. Precedence: CLI > env >
  profile > default.
- **`ci-light` hardening**: `strict_ansible_version_match: true`,
  `allow_development_tool_versions: false` (plus documented no-fallback/no-dynamic-inventory/
  no-variable-display/bounded-artifacts/no-network policy). On this machine, `ci-light`
  now correctly fails by default (installed `ansible-playbook-grapher` is a `2.11.0-dev0`
  build) unless explicitly overridden — verified both ways.
- **Managed Python runtime hardening**: `scripts/_resolve_python.sh` (sourced by all 6
  shims + the justfile) selects the managed working-cache venv and **fails clearly**
  (exit 5) if missing, instead of silently using system Python. Fallback requires
  explicit opt-in (`--allow-system-python-fallback` / `ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1`),
  always logged, recorded as `runtime_isolation: degraded` in manifest/validate output.
  `ANSIBLE_GRAPHER_VENV_PYTHON` override added for test isolation.
- **Structural artifact validation** (`validate_artifact_content()`): every generated
  SVG/JSON/Mermaid/DOT is checked for non-empty, well-formed content before promotion;
  invalid/empty artifacts are deleted, not left on disk; run reports exit `7`.
- **Strengthened `validate` mode**: managed-Python check, module-import check,
  release-status + version-alignment checks for both graphers, profile validity,
  policy-summary checks, `--format json` machine-readable report
  (`{"status": ..., "checks": [{"name", "status", "details", "remediation"}]}`).
- **New test suites**: `tests/test-toolchain-compatibility.sh` (13 checks) and
  `tests/test-partial-generation-failure.sh` (9 checks, using real fake executables
  substituted via the `ANSIBLE_GRAPHER_*_GRAPHER_BIN` override — not mocks of internal
  logic). Combined with the existing 37, **59 checks total, all passing**.
- **CI workflow**: `.github/workflows/skill-ansible-grapher-ci.yml` — installs stable
  PyPI releases of both graphers (documented as differing from this machine's dev-build
  checkout), runs all four test suites, generates + structurally validates example
  artifacts, checks determinism across two isolated runs. Structurally validated locally
  (YAML parses, no `${{ }}` expression interpolation anywhere — nothing to sanitize);
  `actionlint` is not installed on this machine so its stricter checks were not run; no
  remote GitHub Actions run has occurred (not pushed).
- `just ci-check` recipe: bounded local CI-equivalent validation + generation pass.
- `ARCHITECTURE.md`, `README.md`, `AGENTS.md`, `AI_NAVIGATION.md`, `context-map.yaml`,
  and all of `docs/*.md` updated to document the above (see those files' own history).

### Changed
- `MANIFEST_SCHEMA_VERSION` 1 → 2 (adds `toolchain_compatibility`, `runtime`).
- `SKILL_VERSION` 0.1.0 → 0.2.0.
- `cmd_validate` rewritten around a structured check list rather than ad hoc
  print/exit-code logic; `cmd_project` now aggregates per-tool compatibility into the
  manifest and applies combined-profile compatibility policy (e.g. `ci-light`) with
  correct CLI-flag-level precedence over the target inventory/playbook sub-profile.

### Fixed (found during this hardening pass)
- `python_runtime_isolation`/fallback state was not reported anywhere — added.
- `cmd_validate`'s inventory-parse check duplicated (and slightly diverged from)
  `validate_inventory()`; now reuses it directly.
- A stray `print()` in the executable-resolution loop leaked plain-text lines into
  `--format json` output, corrupting the JSON. Fixed by gating it on `not as_json`.

## 20260701_1345 — add ARCHITECTURE.md

### Added
- `ARCHITECTURE.md` — component diagram, data flow, and key implementation decisions
  (thin-wrapper design, `PYTHONHASHSEED=0` determinism fix, absolute-path resolution
  fix, working-cache Python isolation, no-install policy).
- Pointers from `README.md` (Governance pointers), `AI_NAVIGATION.md`, and
  `context-map.yaml`.

## 20260701_1330 — governance audit/refresh (skill-ai-it)

### Added
- `CLAUDE.md` — thin `@AGENTS.md` wrapper (was missing).
- `scripts/README.md` — script/task inventory with safety labels for all 7 entrypoints.
- README.md `## Governance pointers` section.

### Skipped
- `archcore init` / Graphify / Repomix bootstrap — CLIs are available on this machine,
  but this skill is a small, self-contained, portable package (not an ongoing project
  workstream); adding `.archcore/`, `graphify-out/`, and `.ai-context/` generated
  artifacts here would add tooling surface unrelated to the skill's own 20-section
  behavioral spec. Revisit if this skill grows a longer-lived roadmap/decision history.
- `ARCHITECTURE.md`, `CONVENTIONS.md`, `ROADMAP.md` — not created; `SKILL.md` +
  `docs/*.md` already cover architecture/conventions for this skill's scope, and there is
  no active multi-phase roadmap to track.

### Removed
- Leftover empty `.ai-artifacts/` directory (residue from manual example-generation
  testing during initial build; cleaned via the skill's own `clean` subcommand and an
  empty-dir removal).

## 0.1.0 — initial release

Added:
- Combined skill wrapping `ansible-inventory-grapher` and `ansible-playbook-grapher` for
  local, FOSS, documentation-only visualization of Ansible inventories and playbooks.
- Unified CLI (`scripts/ansible-grapher`) with subcommands: `discover`, `inventory`,
  `playbook`, `project`, `validate`, `clean`, `profiles`, `help`.
- Thin shell entrypoints (`scripts/discover-ansible-project`, `scripts/graph-inventory`,
  `scripts/graph-playbook`, `scripts/graph-project`, `scripts/validate-ansible-grapher`,
  `scripts/clean-generated-graphs`) and a `justfile` convenience layer.
- 11 graph profiles across inventory/playbook/combined domains
  (`config/profiles.yaml`), translated to locally-verified CLI flags.
- Safety controls: dynamic-inventory deny-by-default, variable-display suppression by
  default, secret/vault redaction in logs and manifests, output-path containment,
  overwrite refusal without `--force`, ownership-marker-gated cleanup with symlink-escape
  prevention.
- Bounded project discovery (ansible.cfg, inventory/playbook candidates, roles,
  collections, requirements, group_vars/host_vars) with a capped, non-exhaustive
  graphing recommendation.
- Deterministic output: `PYTHONHASHSEED=0` pinned for both grapher subprocesses to
  eliminate process-to-process ordering non-determinism observed in both upstream tools.
- Isolated Python runtime: `skills-working-cache/skill-ansible-grapher/.venv`
  (mise-pinned Python 3.14, PyYAML), with fallback to system `python3`.
- Full test suite: `tests/test-skill-ansible-grapher.sh` (29 checks) and
  `tests/test-output-safety.sh` (8 checks) — both passing.
- Example fixtures (YAML + INI inventory, a small no-op playbook) and matching
  `tests/fixtures/`.

Fixed (during implementation, before first release):
- `cmd_playbook` originally ran the subprocess with `cwd` set to the output directory
  while playbook paths stayed relative to the caller's cwd, breaking real-world
  invocations. Fixed by resolving playbook/inventory paths to absolute paths up front and
  removing the `cwd` override.
- `cmd_clean`'s symlink check ran after `resolve_output_dir()` had already resolved
  symlinks away, so a symlinked output root was never detected. Fixed by checking
  symlink-ness on the raw path before resolution.
- `ansible-inventory --list` exits `0` and silently falls back to "implicit localhost
  only" when every inventory plugin fails to parse a source. `validate_inventory()` (and
  `cmd_validate`, which now reuses it instead of duplicating the check) treats that
  fallback as a validation failure.
