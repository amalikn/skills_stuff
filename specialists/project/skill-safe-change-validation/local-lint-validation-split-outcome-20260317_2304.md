# Local Lint Validation Split Outcome

## Implemented
- Expanded `ansible-wifi/.agents/validation.md` into the repo-specific validation source of truth.
- Kept root `AGENTS.md` thin; no detailed command logic was moved into it.
- Updated the canonical `safe-change-validation` specialist and installed runtime skill so they now tell Codex to inspect repo-local validation docs first and separate blocking checks from deeper manual validation.
- Extended the existing clone-local `.git/hooks/pre-push` hook so it now:
  - runs repo knowledge capture first
  - routes changed files into blocking lint checks
  - blocks push on lint failure
  - stays local-only with no tracked hook infrastructure
- Hardened the hook to use writable temp/cache paths:
  - `ANSIBLE_LOCAL_TEMP` under `/tmp`
  - `XDG_CACHE_HOME` under `/tmp`

## Validation Results
### Repo-local docs and skill updates
- `ansible-wifi/.agents/validation.md` now documents:
  - blocking pre-push checks
  - targeted manual checks
  - applicability by change type
  - optional checks
  - JSON syntax-only scope
  - Jinja2 as Ansible-aware validation only
- Canonical `safe-change-validation` `RUNBOOK.md` and `CHANGELOG.md` updated.
- Runtime `~/.codex/skills/safe-change-validation/SKILL.md` updated.

### Command-level checks
- `ansible-inventory -i inventories/rcp/prod --playbook-dir . --list`
  - passed once `ANSIBLE_LOCAL_TEMP` was redirected to `/tmp`
- `ansible-inventory -i inventories/rcp/stage --playbook-dir . --list`
  - passed once `ANSIBLE_LOCAL_TEMP` was redirected to `/tmp`
- `ansible-playbook --syntax-check smc_bases.yml -i inventories/rcp/prod`
  - passed once `ANSIBLE_LOCAL_TEMP` was redirected to `/tmp`
- `ansible-lint smc_bases.yml`
  - failed due local environment mismatch:
    - Ansible CLI `2.20.3`
    - python module `2.17.4`
- `yamllint smc_bases.yml inventories/rcp/topology_vars/pia-wadjari.yml`
  - failed on existing repo lint debt, including line-length, trailing-spaces, truthy, colons, and newline issues
- `python3 -m json.tool roles/prometheus_grafana/files/grafana.json`
  - passed
- `shellcheck roles/teleport_core/ec2-bootstrap.sh`
  - could not run because `shellcheck` is not installed in the current environment

### Hook behavior
- `bash -n .git/hooks/pre-push`
  - passed
- Empty-diff success path simulation:
  - passed
  - created snapshot `20260317_2235`
  - reported `no changed tracked files to validate`
- Real changed-diff path on current branch:
  - failed as designed
  - blocked on `ansible-lint` environment mismatch after running capture and inventory validation

## Operational Meaning
- The split model is now in place.
- The hook correctly enforces local-only blocking validation.
- Actual push success for Ansible-related changes now depends on fixing the local Ansible-lint environment and, where applicable, repo lint debt.
- Shell-related changes will also block until `shellcheck` is installed.

## Follow-up Gaps
- Install `shellcheck` locally if shell-heavy templates/scripts are part of normal work.
- Fix the Ansible / ansible-lint environment mismatch.
- Decide whether current repo YAML lint debt should be accepted as-is or whether blocking rules need scoped relaxations.
