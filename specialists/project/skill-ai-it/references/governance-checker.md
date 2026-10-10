---
Title: skill-ai-it reference: Governance coherence checker
Category: reference
Status: current
Authority: local-supplement
Scope: On-need reference moved verbatim from SKILL.md
Last reviewed: 2026-10-10
Summary: >-
  Governance coherence checker; moved verbatim from SKILL.md so SKILL.md stays an orchestration file within budget.
---

# skill-ai-it reference: Governance coherence checker

Moved verbatim from `SKILL.md` on 2026-10-10 to keep that file within its budget for files loaded whole.

### Governance coherence checker

Every governed project gets `scripts/check_governance.py` — a stdlib-only script that turns the project's governance **claims** into assertions that fail. Doctrine, the seven check families, and the
artifact-to-check inference table live in `patterns/governance-checks.md`; read it before generating or extending a checker.

Source template: `templates/check_governance.py`. AGENTS.md managed block: `templates/AGENTS-governance-checks-block.md`.

The checker is **self-contained per project** — no shared runtime, no import from a canonical package. Universal checks are seeded from the template; project-specific checks are authored into the same
file. A project's checker is free to diverge as its invariants diverge, which is the point.

#### What makes it intelligent rather than generic

A generic linter cannot see a project's real integrity risks, because those risks are domain-shaped. The generated checker has three tiers:

- **Tier 1 (universal)** — path resolution, index links, count claims, catalog coverage. Copied from the template and tuned. Always present.
- **Tier 2 (conditional)** — generated only when the trigger artifact exists: a task runner, a structured-document class with a declared contract, a supersession chain.
- **Tier 3 (inferred)** — encodes *this project's* stated rules. For each rule the project states, ask: **what observable state would prove this rule was violated?** That answer is the check.

Two discipline rules on Tier 3, both load-bearing:

- **Every Tier 3 check cites the project rule it enforces**, in its docstring or failure message. A check whose justification cannot be located is a check the next agent deletes when it becomes
  inconvenient.

- **Never invent an invariant the project has not stated.** Manufacturing governance the operator never agreed to is worse than leaving a gap. Report the candidate invariant as a proposal instead.

#### Self-policing coverage — how it stays fine-tuned

The hardest failure mode is not a check that breaks; it is a new file that nothing checks. So the checker must fail on **uncovered** surfaces, not only incorrect ones. Generate an orphan check for
every catalog the project maintains: a document in `docs/` that the index does not link, a script absent from `scripts/README.md`, a file restating a registered constant without being registered.

This is what converts "keep the checker updated" from an intention recorded in a document into a blocking condition. Adding a file turns the build red until it is registered somewhere — the agent
extends the checker because it cannot proceed otherwise.

The asymmetry matters and is easy to half-implement: *catalog names something that vanished* and *something exists that no catalog names* are different defects, and only the second grows silently.
Generate both directions.

#### Mode behavior

- `bootstrap`: create from template with Tier 1 only, tuned to whatever catalogs and surfaces exist. Typically 10–40 assertions. Wire it into the task runner (`just check`) and add the AGENTS.md
  managed block. Do not generate Tier 2/3 scaffolding for structure the project does not yet have.

- `navigation-add`: create if governance surfaces exist and no checker does; otherwise add the AGENTS.md block and the runner recipe only.
- `refresh`: **this is the adoption path for projects that predate the capability.** If no checker exists, create one from the template exactly as `bootstrap` would, tuned to the invariants the
  project has accumulated since it was set up — which is usually a richer set than it had at bootstrap, so expect more than the bootstrap baseline. Wire it into the task runner and add the AGENTS.md
  managed block in the same pass. If a checker already exists, extend its registries to cover artifacts added since the last run — new catalogs, new generated outputs, new constant surfaces. **Never
  narrow an existing check to make a run green.**

- `audit`: run the checker, report failures verbatim, and separately report *coverage gaps* — artifact classes present in the project that no check covers. The second list is the more valuable output.
- `promote`: promote a stable invariant to a rule/spec document when the operator asks, then cite that document from the check.

#### Non-negotiables to state in the target project's AGENTS.md

- When a check fails, **fix the project, not the check**. Broadening an ignore-list or exempting the failing file converts a real finding into a permanent blind spot.
- A new check must be **able to fail** — prove it by breaking the project deliberately and watching it go red.
- **Text matching does not verify behavior.** Grepping for a threshold's characters does not prove the logic implements it; a script's output can state a rule its code no longer applies. Where a check
  must verify behavior, execute the behavior and assert on the result.

- **Do not enforce history.** Counts recorded as past facts are evidence, not live claims — exempt them by marker rather than editing the record to satisfy a linter.
