# SCRATCHPAD (non-authoritative — dev notes only)

Status: v0.2.0 hardening/closure pass complete, 2026-07-01. All tests passing (59: 29 + 8 + 13 + 9).
Installed into Claude Code the same day: `~/.claude/skills/skill-ansible-grapher` is a
symlink to this canonical source (matches the current skills_stuff install convention —
no copy, single edit point). Implementation report subsequently trimmed to a more
concise form (CI-workflow specifics condensed) — underlying facts (CI workflow file,
`just ci-check`, 59/59 tests) unchanged; project-coherence check on 2026-07-01 found no
stale references anywhere else in the package. <!-- KEEP -->

## Environment notes for this machine

- `ansible-inventory-grapher` 2.6.0 (stable; its own venv's `ansible-core` is 2.21.1 —
  genuinely matches the system validator). `ansible-playbook-grapher` 2.11.0-dev0
  (development build; its own venv's `ansible-core` is 2.18.2 — genuinely differs from
  the system 2.21.1). Both facts are now detected and reported automatically by
  `ansible-grapher validate` / the toolchain-compatibility check, not just noted here.
- Launcher scripts (not on PATH by default):
  - `/Volumes/Data/_ai/_tools/tools_stuff/ansible-inventory-grapher/scripts/ansible-inventory-grapher.sh`
  - `/Volumes/Data/_ai/_tools/tools_stuff/ansible-playbook-grapher/scripts/ansible-playbook-grapher.sh`
  Export `ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN` / `ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN`
  to these paths before running (see README.md).
- Skill's own Python venv: `/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv`
  (Python 3.14.5 via mise, PyYAML installed). Rebuild with `mise install && mise exec --
  python -m venv .venv && .venv/bin/python -m pip install PyYAML`. Since 0.2.0, the
  shims/justfile **no longer silently fall back** to system Python if this is missing —
  see `scripts/_resolve_python.sh`.
- `ci-light` **fails by default on this machine** without
  `--allow-ansible-version-mismatch --allow-development-tool-versions` — this is the
  strict/dev-version-rejection policy working as designed, not a bug (see SKILL.md §19).

## Things discovered during build (see CHANGELOG.md "Fixed" for the safety-relevant ones)

- Both grapher tools' node/edge ordering depends on `PYTHONHASHSEED` (they iterate
  Python sets/dicts of group/role names without sorting). Fixed by pinning
  `PYTHONHASHSEED=0` in the subprocess environment — see `deterministic_env()` in
  `scripts/ansible-grapher`.
- `ansible-inventory-grapher --help` options actually available on this install: `-i`,
  `-d`, `-o`/`--format`, `-q`/`--no-variables`, `-t`/`-T` (templates), `-a` (graphviz
  attrs), `--ask-vault-pass`, `--vault-password-file`, `--vault-id`, `--visible-vars`,
  `--show-all-values`. No `--rankdir` flag — attributes go through `-a`.
- `ansible-playbook-grapher --help` supports `--renderer {graphviz,mermaid-flowchart,json}`,
  `--include-role-tasks`, `--only-roles`, `--group-roles-by-name`,
  `--hide-plays-without-roles`, `--hide-empty-plays`, `--show-handlers`,
  `--collapsible-nodes`, `-s`/`--save-dot-file`, `-t`/`--skip-tags`, `-e`, `-i`,
  `--vault-id`/`--vault-password-file`. All profile flags in `config/profiles.yaml` were
  checked against this exact `--help` output.
- (0.2.0) `ansible-inventory-grapher`'s launcher script is `exec "$VENV/bin/tool" "$@"` —
  this exact pattern is what `find_venv_python_for_launcher()`'s `VENV=` regex depends
  on; a differently-shaped launcher would need a different provenance-discovery strategy.

## Resolved (previously "Open items" in 0.1.0's report)

- ~~Partial-generation-failure test~~ — `tests/test-partial-generation-failure.sh` (9
  checks) now exercises this directly with fake executables via the
  `ANSIBLE_GRAPHER_*_GRAPHER_BIN` override.
- ~~No CI integration~~ — `.github/workflows/skill-ansible-grapher-ci.yml` added,
  structurally validated (YAML parses; no `${{ }}` expression interpolation anywhere).
  No remote run has occurred (not pushed) — see the implementation report's "Remote CI
  evidence status" for the precise distinction between locally-executed and
  workflow-definition-only evidence.

## Open items / not fully covered (post-0.2.0)

- `actionlint` is not installed on this machine; the CI workflow was validated by
  parsing the YAML and manually reviewing every `run:` block for injection risk (none
  use `${{ github.event.* }}` or any other interpolated untrusted input), not by running
  `actionlint` itself.
- No remote GitHub Actions run has been observed — the workflow's correctness beyond
  local structural validation and the local CI-equivalent (`just ci-check`) run is
  unverified until it actually executes on `github.com`.
- `find_git_checkout_provenance()` only recognizes this stack's specific
  `<project>/<tool>-github/` sibling-checkout convention; a differently-organized
  upstream checkout would report `git: null`, not an error.

## Memory pointers (navigation only — content is above / in CHANGELOG.md) <!-- KEEP -->

- memory-keeper channel: `skill-ansible-graphe` (note: `skill-ansible-grapher` truncates
  to 21 chars on save — a real tool quirk, not a typo) — keys: `skill-ansible-grapher.decisions`,
  `skill-ansible-grapher.build.v0.1.0`, `skill-ansible-grapher.hardening.v0.2.0`,
  `skill-ansible-grapher.key-facts`, `skill-ansible-grapher.open-items`,
  `skill-ansible-grapher.installed`, `skill-ansible-grapher.coherence.20260701`
- memory-keeper checkpoints: `slurp-20260701-skill-ansible-grapher` (ID `7bde6040`),
  `slurp-20260701-skill-ansible-grapher-install` (ID `79692f73`),
  `slurp-20260701-skill-ansible-grapher-coherence` (ID `fe26b76e`)
- mcp-project-context project: `skills_stuff` (ID `b8c5525e-3e2f-4fb5-bf87-e5751f3ad49c`),
  channel `skill-ansible-grapher`
- mcp-project-context checkpoints: `slurp-20260701-skill-ansible-grapher`
  (ID `ad565456-cbda-4cc7-99d2-8b60dd547e57`), `slurp-20260701-skill-ansible-grapher-install`
  (ID `30b3a2f5-ee84-45e4-bc21-bb7fbe1afed3`), `slurp-20260701-skill-ansible-grapher-coherence`
  (ID `958de0a8-0687-46a5-9adb-bfbe71bfd94b`)
- Related, separate prior work: memory-keeper channel `ansible-grapher` (2026-06-26,
  the original tools_stuff *tool installation*, not this skill package).
