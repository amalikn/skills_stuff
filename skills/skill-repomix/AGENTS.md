# Agent Maintenance Rules

- Preserve the profile schema in `docs/profile-schema.md`.
- Update tests when adding or changing profiles.
- Never weaken secret or mutable-state exclusions.
- Never add support for `--no-security-check`.
- Keep shell scripts portable across macOS and Linux.
- Avoid GNU-only commands.
- Update `CHANGELOG.md` for every functional change.
- Keep `SKILL.md` authoritative for workflow behaviour.
- Keep `templates/repomix-mcp-routing-policy.md` authoritative for routing policy.
- Token thresholds must remain synchronised between `SKILL.md` and `patterns/token-budgeting.md`.
- Run-report schema changes require updates to both `scripts/validate-skill.sh` and `tests/test-skill-repomix.sh`.
- Retry behaviour must not be weakened without an explicit security or correctness justification.
- Audience and authority boundaries between `SKILL.md` and `README.md` must remain explicit.

## Code changes

Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule): its rules apply
(purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime) and the session owes it a write-back.
