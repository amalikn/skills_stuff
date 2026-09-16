# AI Navigation — skill-ansible-repo-intelligence (skill-ari)

Context entrypoint for AI agents. Router, not a knowledge dump. Tells you where
project truth lives, what to read first, and what to update after work.

<!-- BEGIN skill-ai-it:navigation -->

## Mandatory read order

Before answering, planning, editing, or creating files here:

1. `SKILL.md` — the agent contract (what this tool is, bounded-retrieval workflow).
2. `AGENTS.md` — invariants (no execution, no secret exposure, bounded retrieval).
3. `ARCHITECTURE.md` — module ownership + data flow.
4. `context-map.yaml` — machine-readable routing.
5. `SCRATCHPAD.md` — current state / open items (KEEP-marked).
6. Recent `CHANGELOG.md` entries.
7. `.archcore/` documents, if present.

## Source priority (on conflict)

1. `.archcore/` accepted ADRs, rules, specs, guides, plans
2. `AGENTS.md` / `CLAUDE.md`
3. `SKILL.md` (agent contract)
4. `AI_NAVIGATION.md` / `context-map.yaml`
5. `ARCHITECTURE.md`
6. `ROADMAP.md` / `CHANGELOG.md`
7. `SCRATCHPAD.md` (transient unless `KEEP`)
8. `docs/reports/*` (point-in-time; newest wins)

## Task routing

| Question | Read |
|---|---|
| What does the tool do / how do agents use it | `SKILL.md`, `README.md` |
| How is the code structured / where does X live | `ARCHITECTURE.md`, then `src/ansible_repo_intelligence/<module>.py` |
| What are the rules / invariants | `AGENTS.md`, `.archcore/rules/` |
| What's the status / what's next | `SCRATCHPAD.md`, `ROADMAP.md`, latest `docs/reports/*` |
| Coding style | `CONVENTIONS.md` |
| How to run tests/scan/query | `justfile` (`just --list`), `README.md`, `SKILL.md` |
| Why a design choice was made | `ARCHITECTURE.md` "Key decisions", `CHANGELOG.md` |

## Scripts and tasks

Prefer `just --list` then `just <task>`. Test/scan/benchmark entrypoints live in
the `justfile`. The runtime venv is **outside** the tree at
`skills-working-cache/skill-ansible-repo-intelligence/venv/` — never create a
repo-local `.venv`.

## Update rules

| Change | Update |
|---|---|
| New durable decision | `.archcore/adr/` (via `/skill-ai-it promote`) |
| New invariant/rule | `AGENTS.md`, `.archcore/rules/` |
| Architecture change | `ARCHITECTURE.md` |
| Phase/status change | `ROADMAP.md`, `SCRATCHPAD.md` |
| Any governance/nav change | append `CHANGELOG.md` |
| New/changed CLI or module | `SKILL.md`, `README.md`, `ARCHITECTURE.md` |

## Drift handling

If files disagree: stop, name the conflicting files, state which has higher
authority, propose the smallest fix. Do not silently merge.

## Answer contract

Prefer cited file paths. Do not invent project state. Say "not found in project
context" if unsupported. Distinguish confirmed facts from assumptions.

<!-- END skill-ai-it:navigation -->
