# Local Lint Validation Split for `ansible-wifi`

## Summary
Adopt the split model for `ansible-wifi` linting and validation:

- keep repo-specific lint/check truth in `.agents/validation.md`
- keep cross-repo validation discipline in the existing `safe-change-validation` skill
- keep push-time lint enforcement local-only via a clone-local `pre-push` hook
- do not create a new lint-hook skill yet; the workflow is still repo-specific and local-only

The default `ansible-wifi` lint matrix will be:
- `ansible-inventory` on `prod` and `stage` / `ansible-playbook --syntax-check`
- `ansible-lint`
- `yamllint`
- `shellcheck`
- JSON syntax validation

Jinja2 templates will be validated through Ansible-aware checks only. `shfmt` remains optional and PHP tooling is out of scope for now.

## Key Changes
- Update `.agents/validation.md` to become the repo-specific validation source of truth.
- Keep root `AGENTS.md` thin and use it only to point to repo-local support docs.
- Update the canonical `safe-change-validation` specialist so it tells Codex to use repo-local validation docs to choose actual commands.
- Add a clone-local `pre-push` lint phase under `.git/hooks/pre-push` without introducing tracked hook infrastructure or `core.hooksPath` changes.
- Use JSON syntax checking only in v1.
- Save plan/outcome markdown under the canonical validation specialist and persist notes in MCP memory/context.

## Test Plan
- Validate `.agents/validation.md` is decision-complete and clearly separates required checks, optional checks, and applicability by change type.
- Manually run each default check once against representative repo content:
  - `ansible-inventory`
  - `ansible-playbook --syntax-check`
  - `ansible-lint`
  - `yamllint`
  - `shellcheck`
  - JSON syntax validation
- Confirm Jinja-backed Ansible templates are covered by `ansible-lint` and syntax/inventory validation rather than a separate Jinja parser step.
- Install and manually execute the local `pre-push` lint hook from the repo root.
- Confirm success path allows push to continue and failure path exits non-zero.
- Confirm no repo-tracked hook infrastructure or shared enforcement files are added.

## Assumptions
- Enforcement is clone-local only for now.
- The lint matrix is intentionally minimal:
  - `ansible-lint`
  - `yamllint`
  - `shellcheck`
  - repo-specific inventory/syntax validation
  - JSON syntax validation
- Jinja2 templates are validated through Ansible-aware tooling only.
- `shfmt` is optional and not part of the blocking pre-push gate.
- PHP tooling is deferred until there is a clear repo-owned PHP surface that justifies `phpcs` or `phpstan`.
- No new reusable lint-hook skill is created in v1 because the workflow is still specific to this repo and local-only.
