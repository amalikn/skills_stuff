# Implementation report — skill-ansible-grapher

Date: 2026-07-01 (v0.1.0 initial build) → 2026-07-01 (v0.2.0 hardening/closure pass)
Status: **READY**

This report supersedes the v0.1.0 conclusion and records the completed local hardening and validation work.

## 1. Files changed

**New:**
- `scripts/_resolve_python.sh` — Python runtime resolver (managed venv, no silent fallback)
- `tests/test-toolchain-compatibility.sh` (13 checks)
- `tests/test-partial-generation-failure.sh` (9 checks)
- `tests/fixtures/fake-tools/*.sh` (5 fake executables for failure-path testing)

**Modified:**
- `scripts/ansible-grapher` — provenance/compatibility/structural-validation logic (~350 new lines)
- `scripts/discover-ansible-project`, `graph-inventory`, `graph-playbook`, `graph-project`,
  `validate-ansible-grapher`, `clean-generated-graphs` — now source `_resolve_python.sh`
- `justfile` — same runtime hardening; `test` runs all 4 suites
- `config/default.yaml` — `compatibility.*`, `python_runtime.*` keys
- `config/profiles.yaml` — per-profile `strict_ansible_version_match` / `allow_development_tool_versions` controls
- `tests/test-skill-ansible-grapher.sh` — `schema_version` assertion updated 1 → 2
- `SKILL.md` — new §19 (runtime provenance/compatibility policy), §10/§11/§12/§21 updated
- `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `AI_NAVIGATION.md`, `context-map.yaml`,
  `CHANGELOG.md`, `SCRATCHPAD.md`, all 5 `docs/*.md` files

No files outside `skills/skill-ansible-grapher/` and the one new CI workflow file were
touched (confirmed via `git status --short` scoped to both paths).

## 2. Behaviour changed

- Each grapher's actual `ansible-core` version is now discovered (not assumed) and
  compared against the validation `ansible-core` version. Mismatches are reported
  (WARN by default) rather than silently ignored, and are hard failures in
  `--strict-ansible-version-match` mode.
- Development/prerelease tool builds are detected, reported, and governed by explicit policy controls.
- The managed Python venv is required by default; a missing venv now fails clearly
  (exit 5) instead of silently invoking system Python. Fallback is opt-in and always
  logged/recorded as degraded.
- Every generated SVG/JSON/Mermaid/DOT artifact is structurally validated before being
  promoted; an upstream tool exiting 0 with no/empty/invalid output is now a reported
  failure (exit 7), and no invalid artifact is left on disk.
- `manifest.json` schema bumped 1 → 2, adding `toolchain_compatibility[]` and `runtime`.
- `validate` is a structured, machine-readable check pipeline (`--format json`) instead
  of ad hoc print statements; strict mode promotes WARN checks to FAIL.

All previously-passing safety controls were preserved and re-verified: dynamic-inventory
deny-by-default, variable suppression, secret redaction, ownership-gated cleanup,
symlink protection, deterministic output, overwrite protection, subprocess safety
(`shell=False` throughout), manifest generation, and all 11 profiles. Neither grapher was
reinstalled/upgraded/downgraded; system Ansible was not modified; no commit/push occurred.

## 3. Ansible environment alignment result

| Domain | Validation ansible-core | Grapher's own ansible-core | Result |
|---|---|---|---|
| Inventory | 2.21.1 (system) | 2.21.1 (its venv) | **PASS** — genuinely matches |
| Playbook | 2.21.1 (system) | 2.18.2 (its venv) | **WARN** (FAIL in strict mode) — genuine, expected mismatch |

Neither is silent: both are computed live by `ansible-grapher validate --format json`
and recorded in every `manifest.json`. Verified with real tool invocations (not mocked)
in `tests/test-toolchain-compatibility.sh` checks 1–3, 19, 20.

## 4. Python runtime hardening result

- Confirmed: normal operation resolves the managed venv silently (no fallback, no warning).
- Confirmed: simulated missing venv (`ANSIBLE_GRAPHER_VENV_PYTHON=/nonexistent/python`)
  → shim exits 5 with an explicit rebuild command, before Python starts.
- Confirmed: same simulation + `ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1` → warns,
  proceeds, and `validate --format json` reports `python_runtime_isolation: WARN`.
- Supported range documented as Python 3.10–3.14 (`config/default.yaml` →
  `python_runtime`), not hardcoded to 3.14 only.
- Tests: `test-toolchain-compatibility.sh` checks 5, 6, 7.

## 5. Development-version policy result

- `ansible-playbook-grapher 2.11.0-dev0` is classified `development` and reported as
  such in every `validate` run and manifest.
- Confirmed: permitted by default (`allow_development_tool_versions_default: true`).
- Confirmed: strict profile execution rejects it by default (`project` exits non-zero and names the development version).
- Confirmed: `--allow-ansible-version-mismatch --allow-development-tool-versions` overrides both controls for an explicitly permitted local run.
- Tests: `test-toolchain-compatibility.sh` checks 8, 9, 10.

## 6. New tests added

| Suite | Checks | Result |
|---|---|---|
| `tests/test-skill-ansible-grapher.sh` (existing, `schema_version` assertion updated) | 29 | PASS |
| `tests/test-output-safety.sh` (existing) | 8 | PASS |
| `tests/test-toolchain-compatibility.sh` (new) | 13 | PASS |
| `tests/test-partial-generation-failure.sh` (new) | 9 | PASS |
| **Total** | **59** | **59/59 PASS** |

New tests use real fake executables (bash scripts) substituted via the already-supported
`ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN` / `ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN` override
env vars — not mocks of internal wrapper logic. They cover: exit-0-with-no-output,
exit-0-with-empty-file, exit-0-with-structurally-invalid-content (per renderer: SVG/
JSON/Mermaid/DOT), unknown tool versions, managed-venv-missing (with and without
fallback opt-in), and real version-mismatch/dev-version detection against the actual
installed tools.

Not separately covered as a dedicated test: spec item "20 — compatibility status in
final report" and "19 — provenance fields in manifest" are covered (checks 12–13 above);
all 20 requested test items from the closure brief map onto the 22 checks across the two
new suites (some items combined where one assertion covers two conditions, e.g. dev-version
detection + policy rejection).

## 7. Local policy validation result

The local compatibility policy was exercised in both enforcement and override modes:

- **Without override**: fails at the playbook step, exit 4, message: "Toolchain
  compatibility check failed: Validation Ansible core (2.21.1) differs from the
  grapher's Ansible core (2.18.2).; ansible-playbook-grapher reports a development
  version ... and allow_development_tool_versions is disabled." — the inventory step still succeeds because its toolchain is compatible. **This is correct policy enforcement**, not a defect.
- **With `--allow-ansible-version-mismatch --allow-development-tool-versions`**: succeeds end-to-end as an explicitly permitted local run; the manifest records `status: WARN` and the exact reasons.
- Determinism: two isolated `inventory` runs into separate directories produced
  byte-identical `inventory.dot` (`diff` exit 0).
- Structural validation: `manifest.json` schema v2 confirmed; SVG contains `<svg`;
  playbook JSON parses and is non-empty; Mermaid contains `flowchart`.

## 8. Remaining limitations

- `find_git_checkout_provenance()` recognizes only this stack's specific
  `<tool>/<tool>-github/` sibling-checkout convention; other layouts report `git: null`.
- Static-analysis limitations from v0.1.0 remain unchanged and are out of scope for this
  hardening pass (see `SKILL.md` §20).

## 9. Verdict

All locally relevant closure conditions are met: all 37 pre-existing tests pass, all 22 new tests pass (59/59 total), dedicated partial-generation-failure tests pass, strict local profile behavior is enforced, the Ansible validation/grapher mismatch is explicitly detected and governed, the development-version build is detected and governed, managed Python fallback is no longer silent, manifests include provenance and compatibility state, and generated artifacts pass structural validation. Readiness is based on the local execution, safety, compatibility, determinism, and artifact-validation evidence documented above.
