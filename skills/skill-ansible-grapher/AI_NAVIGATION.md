# AI Navigation — skill-ansible-grapher

Read order and file authority for agents working in this skill directory.

| Order | File | Authority | Purpose |
|---|---|---|---|
| 1 | `SKILL.md` | **Authoritative** for runtime behavior | Modes, safety contract, exit codes, workflows |
| 2 | `AGENTS.md` | Agent operating rules | Supplements SKILL.md; does not override it |
| 3 | `README.md` | User-facing | Quick start, prerequisites, troubleshooting pointer |
| 3b | `ARCHITECTURE.md` | Reference | Component diagram, data flow, key implementation decisions |
| 4 | `context-map.yaml` | Machine-readable | File relationship graph for tooling |
| 5 | `config/default.yaml` | Defaults | Non-authoritative for safety invariants (SKILL.md wins) |
| 6 | `config/profiles.yaml` | Profile definitions | Translated to CLI flags by `scripts/ansible-grapher` |
| 7 | `docs/*.md` | Reference | Tool capabilities, output contract, security, troubleshooting, profiles |
| 8 | `SCRATCHPAD.md` | Non-authoritative | Development notes only — never cite as behavior |
| 9 | `CHANGELOG.md` | Historical | Version history |

## Rule

If `config/*.yaml` ever appears to conflict with a safety invariant in `SKILL.md`
(e.g. dynamic-inventory deny-by-default, variable suppression by default, overwrite
refusal, no-silent-Python-fallback, toolchain-compatibility FAIL aborting the run),
`SKILL.md` wins. Configuration defines *defaults*, not *invariants*.

## Entry points

- CLI: `scripts/ansible-grapher <discover|inventory|playbook|project|validate|clean|profiles|help>`
- Thin shims: `scripts/discover-ansible-project`, `scripts/graph-inventory`,
  `scripts/graph-playbook`, `scripts/graph-project`, `scripts/validate-ansible-grapher`,
  `scripts/clean-generated-graphs` — all source `scripts/_resolve_python.sh` for Python
  runtime selection (managed venv by default, no silent fallback).
- Convenience: `justfile` (recipes wrap the same CLI; `just ci-check` runs a bounded
  local CI-equivalent pass)
- Tests: `tests/test-skill-ansible-grapher.sh` (29), `tests/test-output-safety.sh` (8),
  `tests/test-toolchain-compatibility.sh` (13), `tests/test-partial-generation-failure.sh` (9)
- CI: `.github/workflows/skill-ansible-grapher-ci.yml`
