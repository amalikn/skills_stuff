# Repository guidance

<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: 2026-08-11-governance-checks-layer-v1 -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](AI_NAVIGATION.md).
2. Read [context-map.yaml](context-map.yaml).
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Load relevant `memory-bank/` files if present.
6. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
7. Before making durable changes, inspect companion-file rules in `context-map.yaml update_rules`. Update all companion files when changing source files.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory-bank.
10. Do not treat Graphify (`graphify-out/`) or Repomix (`.ai-context/`) output as canonical truth. These are generated support artifacts only, always rebuildable.
11. Before running scripts or automation, inspect `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`, and `package.json` when present. Prefer `just --list` and `just <task>` when a `justfile` exists.
12. Treat uncataloged scripts as `unknown` safety until inspected.
13. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
14. If `scripts/check_governance.py` exists, run it before claiming any durable change is complete. When it fails, fix the project, not the check. Adding a new artifact class, generated output, or a constant restated across files requires extending its registries in the same pass.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->

## Scope

Protect the distinction between evidence, assumptions, calculations, recommendations, and approvals. Do not add a claimed regulatory, tax, customs, product-compliance, or market fact without a source record and an evidence label.

## Implementation rules

- Use `Decimal` for monetary and percentage calculations; do not use binary floats for financial outputs.
- Put deterministic rules in `src/bftoolkit/calculators/` and test exact rounding behaviour.
- Keep LLM integrations behind `src/bftoolkit/llm/contracts.py`; no provider SDK may be a core dependency.
- Domain packs ask structured questions and name evidence required. They never decide eligibility or insert jurisdictional rules from memory.
- A human approval is required for an `APPROVED` decision. Never make an external write, purchase, filing, listing, or communication from a skill by default.

## Validation

Run `uv run pytest` and `python tools/validate_repository.py`. Do not claim a regulatory pack is current merely because its checklist passes.
