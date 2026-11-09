# AGENTS.md — skill-ansible-grapher

`SKILL.md` is the authoritative behavioral contract for this skill. This file adds
agent-operating rules; it does not restate SKILL.md content.

## Read order

1. `SKILL.md` — behavioral contract (modes, safety contract, profiles, exit codes).
2. `AI_NAVIGATION.md` — file authority map.
3. `docs/security-and-safety.md` — before running against any real/unfamiliar inventory.
4. `config/default.yaml` + `config/profiles.yaml` — before choosing flags/profiles.

## Operating rules

- Treat `ansible-inventory-grapher-github/` and `ansible-playbook-grapher-github/`
  (in the sibling `tools_stuff` repos) as read-only upstream source. Never edit them.
- Never invoke `ansible-playbook` without `--syntax-check`. Never invoke `ansible-playbook`
  at all with real target hosts.
- Never enable `--show-variables` / dynamic inventory without the user having explicitly
  asked for it in this conversation turn — both default to off/deny.
- Never paste generated SVG/DOT/Mermaid/JSON content into chat output when variables were
  shown — report the artifact path only.
- Prefer `scripts/discover-ansible-project` before graphing an unfamiliar repo; do not
  graph every playbook found — respect the discovery recommendation's bounded plan.
- Resolve tool executables via `ANSIBLE_GRAPHER_INVENTORY_GRAPHER_BIN` /
  `ANSIBLE_GRAPHER_PLAYBOOK_GRAPHER_BIN` (or PATH) — never hardcode a machine path in a
  reply as if it were guaranteed to exist elsewhere.
- If a required executable is missing, report it by name and stop. Do not attempt to
  `pip install` / `brew install` / upgrade anything to "fix" it unless the user
  explicitly asks for that as a separate task.
- Never treat an Ansible-version mismatch between validation and a grapher as silently
  compatible — it must be reported (WARN by default) or, in strict/`ci-light` contexts,
  a `FAIL` that requires an explicit `--allow-ansible-version-mismatch` /
  `--allow-development-tool-versions` override from the user before proceeding.
- Never silently use system Python when the managed venv is missing — that requires
  explicit user opt-in (`--allow-system-python-fallback` /
  `ANSIBLE_GRAPHER_ALLOW_SYSTEM_PYTHON_FALLBACK=1`); otherwise report the exit-5 error
  and offer the rebuild command from `README.md` § Environment isolation.
- Run `just test` (or all four `tests/*.sh` scripts directly) after any change to
  `scripts/ansible-grapher`, `scripts/_resolve_python.sh`, or `config/*.yaml`.

## Canonical governance linkage

- Parent skills root: [`../../AGENTS.md`](../../AGENTS.md)
- Cross-repo governance root: `/Volumes/Data/_ai/governance/README.md`
- Working-cache (Python venv, rebuildable): `/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/`

## Code changes

Invoke `skill-coder` before adding or changing any script in this pack (operator, 2026-10-20; the skills_stuff root rule): its rules apply
(purpose header, docstrings, `--apply` for writes, timeouts, tests, measured runtime) and the session owes it a write-back.
