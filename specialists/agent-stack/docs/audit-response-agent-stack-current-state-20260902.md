# Agent Stack Current-State Audit Response

**Audit date:** 2026-09-02
**Scope:** The live working tree at `specialists/agent-stack`, its declared working-cache evaluation evidence, and the audit brief in `../audit-agent-stack.md`.
**Method:** Read-only reconstruction from source, configuration, tests, result rows, and accepted `.archcore` records. Historical audits were used only to identify legacy findings, not as proof of
  their current status.

## Contents

- [1. Executive Assessment](#1-executive-assessment)
- [2. What Agent Stack Is Now](#2-what-agent-stack-is-now)
- [3. Canonical Sources and Repository Inventory](#3-canonical-sources-and-repository-inventory)
- [4. Persona Architecture](#4-persona-architecture)
- [5. Skill Architecture](#5-skill-architecture)
- [6. Routing Architecture](#6-routing-architecture)
- [7. Capability Taxonomy](#7-capability-taxonomy)
- [8. Gates and Gate Scoring](#8-gates-and-gate-scoring)
- [9. Precedence and Ownership](#9-precedence-and-ownership)
- [10. Deterministic Closure](#10-deterministic-closure)
- [11. Route Invariants](#11-route-invariants)
- [12. Eval Harness and Scoring](#12-eval-harness-and-scoring)
- [13. Provenance and Freeze Model](#13-provenance-and-freeze-model)
- [14. Development Corpus Status](#14-development-corpus-status)
- [15. Historical Baseline Reconstruction](#15-historical-baseline-reconstruction)
- [16. Cross-Model Results](#16-cross-model-results)
- [17. Unseen Holdout Status](#17-unseen-holdout-status)
- [18. Real-World Evaluation Readiness](#18-real-world-evaluation-readiness)
- [19. Runtime and Environment](#19-runtime-and-environment)
- [20. Installation and Symlink Model](#20-installation-and-symlink-model)
- [21. Safety and Human Control](#21-safety-and-human-control)
- [22. Governance](#22-governance)
- [23. Legacy Audit Findings A1–A7](#23-legacy-audit-findings-a1a7)
- [24. Staleness Residuals](#24-staleness-residuals)
- [25. Test and Governance Coverage](#25-test-and-governance-coverage)
- [26. Complexity / Overengineering Review](#26-complexity-overengineering-review)
- [27. Remaining P0–P3 Findings](#27-remaining-p0p3-findings)
- [28. Production-Readiness Matrix](#28-production-readiness-matrix)
- [29. Recommended Next Actions](#29-recommended-next-actions)
- [30. Final Verdict](#30-final-verdict)
## 1. Executive Assessment

**Overall verdict: SOUND WITH MATERIAL GAPS.**

Agent Stack has a coherent architecture for an operator-controlled routing library. The system has a canonical inventory, an explicit routing catalogue, a capability model that distinguishes
obligations from decision ownership, deterministic closure that is deliberately constrained, and a behavioural evaluator that records the inputs needed to reproduce a run. Current static validation,
governance validation, corpus validation, and unit tests all passed during this audit.

The material gap is no longer the original routing design. It is the transition from development evidence to credible production evidence. The current 24-case unseen holdout was executed under a
passing freeze check, but five of its 24 invocations produced runner failures. The valid result is 16/19 passed with a 71.1 mean, while the corpus is spent under the repository's own single-use rule.
That leaves only partial fresh evidence and exposes runner reliability as a release gate. In addition, durable project status documents still describe this holdout as unexecuted and as future work.
Those documents now misstate the current evaluation state.

**Classification conventions:** FACT means a direct source or result-row observation. INFERENCE is a constrained conclusion from that evidence. FINDING identifies a present weakness. Recommendations
do not change the repository.

## 2. What Agent Stack Is Now

FACT: Agent Stack is an English-only extraction of personas and skills from Auto Company. Its deliberate product boundary excludes the upstream autonomous loop, consensus mechanism, and daemon. The
canonical source is this repository; distribution is a manifest-driven, symlink-only installation. Evidence: [AGENTS.md](AGENTS.md), [manifest.yaml](manifest.yaml), and [.archcore ADR
0001](.archcore/adr/0001-autonomy-is-excluded-by-design.md).

FACT: Its routing contract has four distinct structures in [routing.toml](routing.toml): capabilities describe what providers supply, gates state obligations, precedence selects one primary owner in a
contested decision, and route invariants state what invalidates a finished route. `[[routing_rules]]` remain advisory hints. Evidence: [routing.toml](routing.toml#L437-L451),
[routing.toml](routing.toml#L673-L846), and [.archcore Spec 0003](.archcore/specs/0003-routing-catalogue-contract.md).

INFERENCE: This is no longer a prompt collection with optional routing advice. It is a small policy-and-validation system that uses a model for task interpretation and ownership, then applies
deterministic validation and repair to finite catalogue rules.

## 3. Canonical Sources and Repository Inventory

| Surface | Current role | Authority / treatment |
| --- | --- | --- |
| `manifest.yaml` | Inventory and installation contract | Authoritative for shipped personas and skills |
| `routing.toml` | Routing catalogue | Authoritative for provider capabilities, gates, precedence, and invariants |
| `personas/` and `skills/` | Canonical content | Authoritative source material |
| `skills/orchestrator/SKILL.md` | Production routing procedure | Its marked contract block is consumed by the evaluator |
| `scripts/` and `tests/` | Executable validation and maintenance tooling | Current implementation evidence |
| `evals/routing-cases.toml` | Frozen 60-case development corpus | Regression data, not unseen evidence |
| `evals/holdout-cases.toml` | 24-case holdout | Now spent; see section 17 |
| `MEMORY.md` | Measurements, traps, current routing knowledge | High authority, but presently stale on holdout status |
| `.archcore/` | Accepted decisions, rules, contracts, plans | Highest authority for settled decisions |
| `skills-working-cache/agent-stack/routing-results/` | Rebuildable result evidence | Evidence only; not source-of-truth policy |
| `audit-agent-stack*.md` | Historical audit material | Evidence of prior state only |

FACT: `manifest.yaml` contains 52 capability entries: 15 personas and 37 skill entries. The latter comprise 36 package skills plus `skills/frontend-design.md` as a single-file skill. `just check`
reported exactly those counts.

FACT: The repository’s Git worktree is highly dirty, including the Agent Stack source and surrounding specialist content. Per-row provenance hashes remain useful for routing runs, but a Git commit
alone cannot identify the full current working-tree state. This is a reproducibility caveat, not a claim that the routing artefacts themselves are invalid.

## 4. Persona Architecture

FACT: Every persona has an operational Markdown contract and a routing record. The static validator requires a mandate, use cases, non-use boundary, decision lens, operating method, boundaries, and
output contract, and rejects a persona shorter than 60 lines. Evidence: [scripts/validate_agent_stack.py](scripts/validate_agent_stack.py#L11-L27) and
[scripts/validate_agent_stack.py](scripts/validate_agent_stack.py#L224-L230).

| Persona | Ownership domain | Primary capabilities | Boundary / hand-off interpretation |
| --- | --- | --- | --- |
| `ceo-bezos` | Enterprise direction, priorities, resource allocation | commercial strategy | Defers economic guardrails to CFO and delivery detail to domain owners |
| `cfo-campbell` | Economic viability, pricing economics | financial analysis | Owns financial verdicts, not evidence gathering |
| `critic-munger` | Independent challenge | independent challenge, risk analysis, evidence critique | Escalated when independence itself is required |
| `cto-vogels` | Technical architecture and strategy | architecture analysis, security review | Consults domain and delivery specialists; owns architecture or security posture |
| `devops-hightower` | Delivery mechanism and operational readiness | release readiness, migration planning | Owns operations and deployment, not generic application implementation |
| `fullstack-dhh` | Application implementation | implementation, code-quality review | Owns implementation against settled requirements |
| `interaction-cooper` | Interaction behaviour | product definition | Owns workflow and interaction mechanics, not visual styling |
| `marketing-godin` | Market message and channel | commercial strategy | Owns messaging and marketing-channel work |
| `operations-pg` | Operating process and pilot design | operations design | Owns workflows, sourcing processes, and operational pilots |
| `orchestrator-follett` | Routing, coordination, synthesis | none | Coordinates; does not own architecture of itself |
| `product-norman` | Product outcome and scope | product definition | Owns unresolved requirements and success criteria |
| `qa-bach` | Quality risk and release confidence | validation, release readiness | Escalates for release, security-sensitive, or irreversible validation |
| `research-thompson` | Evidence synthesis | research, source validation | Owns gathering and triangulating evidence, not the financial choice derived from it |
| `sales-ross` | Sales process and qualification | commercial strategy | Owns sales execution and qualification |
| `ui-duarte` | Visual interface | product definition | Owns visual treatment; interaction and implementation remain separate |

FINDING P2: The routing catalogue makes most ownership boundaries operational through four precedence rules, but it does not encode every boundary visible in the persona prose. This is acceptable
while the corpus and real-world replay show stable outcomes. Add precedence only when repeated ambiguous routes demonstrate that a named discriminator is missing; do not attempt to turn every hand-off
into a rule.

## 5. Skill Architecture

FACT: The routing catalogue has 37 skill records. Tool skills carry `execution = "tool"`, a runtime or safety declaration, and primary `tool-execution`; analysis skills do not. The validator rejects
disagreement and rejects any persona claiming `tool-execution`. Evidence: [routing.toml](routing.toml#L125-L435) and [scripts/validate_agent_stack.py](scripts/validate_agent_stack.py#L108-L118).

| Skill | Class | Primary capabilities | Runtime / principal associations |
| --- | --- | --- | --- |
| `agent-browser` | tool | tool execution | `agent-browser-cli`; Research, QA |
| `code-review-security` | analysis | code-quality review, validation | CTO, Full-Stack, QA |
| `cold-email-sequence-generator` | analysis | commercial strategy | Sales, Marketing |
| `community-led-growth` | analysis | commercial strategy | Marketing, Operations |
| `competitive-intelligence-analyst` | analysis | research, market analysis | Research, Marketing, CEO |
| `content-strategy` | analysis | commercial strategy | Marketing |
| `deep-analysis` | analysis | evidence critique | Critic, CTO, Research |
| `deep-reading-analyst` | analysis | evidence critique | Research, Critic |
| `deep-research` | tool | research, source validation, tool execution | Python 3.10+; Research |
| `devops` | tool | implementation, tool execution | provider CLI; DevOps, CTO |
| `email-sequence` | analysis | commercial strategy | Marketing, Sales |
| `financial-unit-economics` | analysis | financial analysis | CFO |
| `find-skills` | tool | tool execution | installation requires explicit authority |
| `frontend-design` | analysis | implementation | UI, Full-Stack |
| `github-explorer` | tool | research, tool execution | GitHub access; Research, CTO, Full-Stack |
| `market-sizing-analysis` | analysis | market analysis, research | Research, CFO, CEO |
| `micro-saas-launcher` | analysis | commercial strategy | Operations, Product, Marketing |
| `orchestrator` | analysis | none | Orchestrator persona |
| `ph-community-outreach` | analysis | commercial strategy | Marketing |
| `premortem` | analysis | independent challenge, risk analysis | Critic |
| `pricing-strategy` | analysis | commercial strategy, financial analysis | CFO, Marketing |
| `product-strategist` | analysis | product definition, commercial strategy | Product, CEO |
| `scientific-critical-thinking` | analysis | independent challenge, evidence critique | Research, Critic |
| `security-audit` | analysis | security review, validation | CTO, QA |
| `senior-qa` | tool | validation, tool execution | Python 3.10+; QA |
| `seo-audit` | analysis | none | Marketing |
| `seo-content-strategist` | analysis | commercial strategy | Marketing |
| `skill-creator` | tool | implementation, tool execution | Python 3.10+ and PyYAML; Orchestrator |
| `startup-business-models` | analysis | commercial strategy, financial analysis | CEO, CFO, Operations |
| `startup-financial-modeling` | analysis | financial analysis | CFO |
| `tailwind-v4-shadcn` | tool | implementation, tool execution | Node, Tailwind v4, shadcn; UI, Full-Stack |
| `team` | analysis | none | Orchestrator |
| `user-persona-creation` | analysis | product definition | Product, Interaction, Marketing, Sales |
| `user-research-synthesis` | analysis | product definition | Research, Product, Interaction |
| `ux-audit-rethink` | analysis | product definition | Product, Interaction, UI |
| `web-scraping` | tool | research, tool execution | web access; Research |
| `websh` | tool | research, tool execution | `websh-runtime`; Research |

FACT: The advertised count matches the repository. The package-skill validator passed for every package skill. The original missing `startup-business-models` resources are present and tested.
Evidence: [tests/test_skill_contract.py](tests/test_skill_contract.py#L10-L33).

## 6. Routing Architecture

FACT: The evaluator implements the intended flow: load catalogue and cases; construct a prompt that includes the production routing contract; invoke the supplied command; parse a JSON plan; optionally
call deterministic closure; score the closed plan; stamp provenance; and optionally write JSONL rows. Evidence: [scripts/evaluate_routing.py](scripts/evaluate_routing.py#L66-L113),
[scripts/evaluate_routing.py](scripts/evaluate_routing.py#L241-L307), and [scripts/evaluate_routing.py](scripts/evaluate_routing.py#L524-L600).

```text
Task and case expectation
  -> model judges ownership, gates, tags, and initial route
  -> capability / strength closure checks the completed route
  -> runtime requirement is recomputed from selected tool skills
  -> runtime prerequisites are reported
  -> scorer evaluates the repaired plan and stores provenance
```

FACT: `routing_rules` are advisory. The catalogue comments define their allowed role; the validator rejects `require_personas` and rule IDs ending in `-gate`. Evidence:
[routing.toml](routing.toml#L437-L451) and [scripts/validate_agent_stack.py](scripts/validate_agent_stack.py#L195-L206).

CONCLUSION: The previous two-persona-model defect is closed. There is one mandatory routing model: gates, precedence, and route invariants. Advisory keywords can still bias a model, but they cannot
declare a persona mandatory in the catalogue schema.

## 7. Capability Taxonomy

FACT: The capability registry exists in `routing.toml`, and every persona and skill declares both primary and supporting capabilities. Gates reference `required_capability`; `satisfied_by_skills` is
prohibited. A provider must hold a capability at the gate’s minimum strength. Evidence: [routing.toml](routing.toml#L525-L670) and
[scripts/validate_agent_stack.py](scripts/validate_agent_stack.py#L79-L160).

The primary/supporting distinction is doing important work. `financial-unit-economics` supports risk analysis but does not provide research. `deep-analysis` supports risk analysis but does not provide
`independent-challenge`. Only `critic-munger`, `premortem`, and `scientific-critical-thinking` declare independent challenge at primary strength. This prevents a plausible analytical skill from being
silently promoted into a critic merely because it discusses risk.

FINDING P2: Taxonomy correctness is structurally checked, but semantic honesty still rests on review. This is unavoidable: no static test can prove that a prose procedure genuinely provides
“independent challenge.” The project correctly treats this as a governed human judgement in [.archcore rule 0007](.archcore/rules/0007-capability-annotations-are-honest.md). Do not automate semantic
capability promotion from keyword similarity.

## 8. Gates and Gate Scoring

| Gate | Trigger meaning | Required capability | Strength | Persona escalation | Deterministic portion | Principal risk |
| --- | --- | --- | --- | --- | --- | --- |
| Research | New external facts or source validation are needed | research | primary | contested evidence, regulatory, source-validation, market-sizing tags | Satisfaction and provider selection | Treating supplied evidence as an acquisition task |
| Critic | Consequential or hard-to-reverse judgement | independent challenge | primary | high-consequence, irreversible, security-sensitive, thin-evidence-high-commitment tags | Satisfaction and provider selection | Inflating ordinary routes with a challenger |
| QA | Code/configuration/release changes or readiness judgement | validation | primary | release, go/no-go, security-sensitive, irreversible rollout, production-change tags | Satisfaction and provider selection | Confusing general analysis with validation |
| Runtime | Any selected tool-class skill | tool execution | computed | never | Flag calculation and prerequisite check | Offering an unavailable tool route |

FACT: Research means external evidence still needs acquisition, not merely that the answer cites evidence. Critic tracks consequential judgement. QA tracks validation and release/change readiness.
Runtime is computed from the selected skill classes. Evidence: [routing.toml](routing.toml#L673-L746) and [skills/orchestrator/SKILL.md](skills/orchestrator/SKILL.md#L181-L211).

FACT: The evaluator treats a missing expected gate as a hard failure and an extra asserted gate as a soft five-point penalty. It tracks both separately. Runtime uses the computed value rather than
model self-report. Evidence: [scripts/evaluate_routing.py](scripts/evaluate_routing.py#L264-L307) and [tests/test_routing_behavior.py](tests/test_routing_behavior.py#L67-L102).

CONCLUSION: “Set every gate true” is no longer a free strategy. The implementation matches the desired asymmetry: false negatives invalidate a contract; false positives reduce efficiency without
deciding the pass/fail verdict.

## 9. Precedence and Ownership

FACT: Four precedence rules yield distinct ownership outcomes: product versus implementation, artefact versus domain review, component self-review, and research versus economics. Each holds two
different owners and a discriminator. The validator rejects unknown, identical, or incomplete branches. Evidence: [routing.toml](routing.toml#L761-L810) and
[scripts/validate_agent_stack.py](scripts/validate_agent_stack.py#L177-L193).

The rules resolve concrete historic ambiguities without requiring broad persona mandates. Product owns an open requirement; Full-Stack owns settled implementation. Full-Stack owns code-quality review;
CTO owns architecture or security posture. CTO owns review of the orchestration system instead of the Orchestrator persona. Research owns evidence collection; CFO owns a financial verdict.

INFERENCE: The limited number of precedence rules is proportionate. They cover demonstrated ambiguous pairs rather than encoding the whole organisation chart. Add a rule only after replay or shadow
evidence shows a repeated, stable ambiguity.

## 10. Deterministic Closure

FACT: `close_route.py` adds only a provider for an unmet gate capability, escalates the named persona only when a model-supplied tag matches the gate’s escalation tags, recomputes `runtime_required`,
and reports unconfirmed tool prerequisites. It does not change `primary_owner`, decide whether a gate is true, remove model choices, or breach the persona cap. Evidence:
[scripts/close_route.py](scripts/close_route.py#L108-L170) and [.archcore Spec 0004](.archcore/specs/0004-route-closure-contract.md).

FACT: Provider selection is deterministic: the gate’s default skill qualifies first; otherwise closure prefers a skill to a persona, a provider that opens no new runtime prerequisite, a provider
already related to the route, then lexical order. This avoids arbitrary provider churn while retaining a narrow repair scope.

CONCLUSION: The separation is correct. The model still judges task classification, gate truth, tags, and primary owner. The system then satisfies finite catalogue obligations. The closure code does
not contain a hidden ownership router.

FINDING P2: The closure layer may add a skill that was not a natural semantic fit beyond its capability. This is intentional for contract satisfaction, but it should remain observable. Keep reporting
repair actions and review real-task replay for routes where a formally valid provider creates an unhelpful route. Do not expand closure into a semantic recommender.

## 11. Route Invariants

FACT: Three invariants map to specific scorer violations and repair descriptions:

| Invariant | Violation | Repair behaviour |
| --- | --- | --- |
| Gate-capability closure | `gate-unsatisfied` | Add the narrowest primary provider, escalating only when independence is required |
| Gate-strength closure | `capability-strength-insufficient` | Ignore supporting strength for a primary obligation and close it correctly |
| Runtime-prerequisite closure | `runtime-prerequisite-missing` | Confirm prerequisite, use an analysis alternative, or report a blocker |

Evidence: [routing.toml](routing.toml#L824-L846) and [scripts/validate_agent_stack.py](scripts/validate_agent_stack.py#L162-L175).

CONCLUSION: These are genuine completion properties rather than aspirational procedure steps. Additional invariants should require evidence of a recurring class of invalid finished routes. Adding
generic “minimal route” or “good owner” invariants would turn subjective quality into false determinism.

## 12. Eval Harness and Scoring

FACT: The evaluator handles failed command execution as `execution-error`, excludes those rows from the corrected pass-rate and mean denominator, and prints the uncorrected figures for reconciliation.
Evidence: [scripts/evaluate_routing.py](scripts/evaluate_routing.py#L560-L600) and [.archcore rule 0008](.archcore/rules/0008-execution-errors-are-not-scores.md).

FACT: `--limit` applies only after case/family selection. The evaluator reports coverage against the pre-limit pool and warns when a partial run is not a baseline. The 53-of-60 regression is
specifically tested. Evidence: [scripts/evaluate_routing.py](scripts/evaluate_routing.py#L452-L550) and [tests/test_routing_behavior.py](tests/test_routing_behavior.py#L104-L122).

FACT: When `--repair` is used, scoring follows closure. The stored plan records the repaired route, and `closure_sha` is recorded as a score-affecting non-prompt input. This order is correct; the
score answers whether the final route satisfies the contract.

FINDING P1: The harness correctly excludes execution errors from quality metrics but does not prevent a large share of a single-use holdout from being lost to runner failure. The 24-case holdout lost
5 invocations. A smoke check exists conceptually, but the holdout recipe did not prove full-run runner reliability before spending the corpus. This is a runner-operational weakness, not a scoring
defect.

## 13. Provenance and Freeze Model

FACT: `run_provenance` stamps routing catalogue, selected corpus, marked orchestrator contract, evaluator harness, closure implementation, provider, model, runner, command, and timestamp. It declares
the prompt-input subset separately. Evidence: [scripts/evaluate_routing.py](scripts/evaluate_routing.py#L85-L113).

FACT: `check_freeze.py` imports the evaluator’s provenance function rather than reimplementing hashing. It checks the five run stamps and the holdout corpus hash, exits non-zero on drift, names the
differing artefact, and writes nothing. `just freeze-check` passed in this audit. Evidence: [scripts/check_freeze.py](scripts/check_freeze.py) and the direct command result.

CONCLUSION: The distinction is sound: `just preflight` tests current internal validity; `just freeze-check` tests equality with one historical measurement snapshot. Freeze checking is correctly
excluded from universal preflight so a legitimate catalogue change can be valid without pretending to reproduce an old experiment.

## 14. Development Corpus Status

FACT: `evals/routing-cases.toml` contains 60 cases in six families and is validated by `just routing-eval-check`. The test suite checks size, family coverage, route references, hard contract
behaviour, gate scoring, coverage reporting, and current freeze record.

FACT: `MEMORY.md` records the frozen development-corpus hash as `cb548b83cf203346`; `just freeze-check` confirmed it against the live file before this audit.

CONCLUSION: The corpus is regression data. It has been used to shape the contract and closure system, so its 50/60 post-closure reading demonstrates regression stability, not generalisation. The
project policy correctly says not to tune it further except for a genuinely new routing concept.

## 15. Historical Baseline Reconstruction

| Baseline | Model / corpus | Closure | Result | Interpretation |
| --- | --- | --- | --- | --- |
| v1 first | DeepSeek V4 Flash / 60 | no | 23/60, mean 76.4 | Undefined gates dominated failures |
| v1 after gate definitions | Flash / 60 | no | 28/60, mean 80.6 | Defined obligations removed missing-gate failures |
| v2 | Flash / 60 | no | 33/59 corrected, mean 83.0 | Capability-first gates and precedence; one execution error excluded |
| v3 | Flash / 60 | no | 34/60, mean 83.0 | Prompt-visible closure/invariants were a valid near-null result |
| v3 stored-route repair | v3 rows / 60 | deterministic | 47/60 | Closure repaired unmet finite obligations without model calls |
| v4 live closure | Flash/Pro/Claude, prior 20-case holdout | deterministic | 13/20, 15/19, 16/20 | Closure raised all tested model arms materially |

FACT: These numbers are recorded in [MEMORY.md](MEMORY.md#L66-L107) and result files exist in the working cache. The correction from v2’s published 81.6 mean to 83.0 follows the explicit
execution-error rule; it is not a model improvement.

CONCLUSION: The strongest historical conclusion survives source inspection: prompt-only instructions did not close gates reliably, while deterministic capability closure produced a large gain. Some
later gains are contract/scorer corrections and must not be described as model improvement.

## 16. Cross-Model Results

FACT: The earlier 20-case cross-model run without closure reported Flash 40%, Pro 50%, and Claude 40%. With deterministic closure, the recorded live results were Flash 13/20 (65.0%), Pro 15/19
(78.9%), and Claude 16/20 (80.0%). The per-row provenance permits comparison within those frozen arms. Evidence: [MEMORY.md](MEMORY.md#L91-L102).

INFERENCE: Deterministic closure mattered more than model tier for the defect it targets. Closure raised each arm by 25 to 40 points, while the two stronger arms converged near 80% once finite route
constraints were repaired.

CAVEAT: This evidence uses the earlier 20-case holdout, which has now served as development evidence. It supports the architecture decision but cannot establish current out-of-sample performance after
later contract changes.

## 17. Unseen Holdout Status

FACT: The new corpus has 24 cases: 5 networking/infrastructure, 5 JDM import, 4 software/AI engineering, 4 atar import, 3 business/research, and 3 direct/adversarial. Its shape and references pass
tests. Evidence: [evals/holdout-cases.toml](evals/holdout-cases.toml) and [tests/test_routing_behavior.py](tests/test_routing_behavior.py#L141-L185).

FACT: It was executed. The stored freeze receipt shows a successful check immediately before a command using `evals/holdout-cases.toml`, `--repair`, labelled provider/model/runner, and a JSONL output.
The corresponding log reports 24 selected, 19 valid scored rows, 16 passes, mean 71.1, and five execution errors. Evidence:
[`holdout24-claude-20260902.freeze.txt`](/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/routing-results/holdout24-claude-20260902.freeze.txt) and
[`holdout24-claude-20260902.log`](/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/routing-results/holdout24-claude-20260902.log).

| Family | Cases | Observed outcome in this run |
| --- | ---: | --- |
| networking-infrastructure | 5 | 3 passed, 2 owner/team failures |
| software-ai-engineering | 4 | 4 passed |
| jdm-import | 5 | 4 passed, 1 owner failure |
| atar-import | 4 | 4 passed |
| business-research | 3 | 1 passed, 2 runner failures |
| direct-adversarial | 3 | 3 runner failures |

FINDING P1: The holdout is spent but incomplete. The evaluator correctly excludes five infrastructure errors from the denominator, so 16/19 is a valid conditional routing result. It does not, however,
represent a complete 24-case independent measurement. The three valid routing failures are ownership/team-shape failures, and the five runner failures cluster in two families. Do not tune the
catalogue against these 24 cases or rerun them as fresh evidence. Treat the run as partial evidence and create a new holdout only after runner reliability is demonstrated.

FINDING P1: Several current-status surfaces contradict this execution fact. `SCRATCHPAD.md` says the 24 cases are “not executed”; `MEMORY.md` and `.archcore` next-phase material still describe an
unseen holdout as the next evidence step. The result files and freeze receipt are later, direct evidence. This is a current-state governance defect.

## 18. Real-World Evaluation Readiness

The project has a sensible intended sequence: unseen holdout, historical-task replay, then shadow mode. Evidence: [.archcore plan 0001](.archcore/plans/0001-next-evaluation-phase.md).

FINDING P1: The sequence must now change because the unseen holdout is spent. The next valid evidence is not “run the holdout”; it is: establish runner reliability with a non-evidence smoke corpus,
preserve the 24-case result as a partial spent measurement, author a new blind holdout after the reliability fix is frozen, then conduct historical replay and shadow routing.

Historical replay needs a task corpus with provenance of what was known at the original decision time and a comparison rubric that does not treat the historical human route as ground truth. Shadow
mode needs a durable, non-actioning log that captures initial plan, repaired plan, prerequisites, human-selected route, disagreement reason, and eventual outcome. Current evaluator tooling can score
routing plans, but neither replay inputs nor a shadow-log schema appear in the repository. Those are the minimum missing artefacts before broad production readiness.

## 19. Runtime and Environment

FACT: The maintenance venv lives at `/Volumes/Data/_ai/_skills/skills-working-cache/agent-stack/venv`, outside the source tree. Recipes use the explicit `{{py}}` path and `_require-venv`; the
governance gate has a deliberate standard-library fallback. `just runtimes` and `just check` passed during this audit. Evidence: [RUNTIME.md](RUNTIME.md), [justfile](justfile), and
[scripts/README.md](scripts/README.md).

FACT: Tool skills declare runtime requirements in the catalogue. The validator requires either a runtime declaration or a safety declaration for tool skills. Consumer projects retain ownership of
their own dependency environment.

FINDING P2: Skill-level runtime guidance remains uneven. Some imported skills contain historical global-path examples or upstream tooling assumptions, even when `routing.toml` accurately describes
their requirements. A runtime readiness matrix for every tool skill would improve operator diagnosis, but it is not required to validate the core routing model.

## 20. Installation and Symlink Model

FACT: Installation is manifest-driven and symlink-only for Claude, Codex, and compatible agent directories. Preflight detects collisions across all chosen destinations, never overwrites existing
entries, verifies created links, and rolls back links created during a failed install. Uninstall removes only links that still resolve to the exact canonical source. Evidence:
[scripts/install_global.py](scripts/install_global.py#L134-L218) and [tests/test_install_global.py](tests/test_install_global.py).

FACT: The installer allows a distribution archive as canonical when applicable and rejects an inappropriate Git worktree. Tests cover dry run, collision behaviour, stale links, idempotence,
skill-creator exclusion, rollback, and archive-compatible handling.

CONCLUSION: A `just doctor` command and a link helper would improve supportability, but the present installer has the critical safety properties. Classify both as P3 developer-experience improvements
rather than release blockers.

## 21. Safety and Human Control

FACT: The repository’s central constraint excludes unattended loops, daemons, implicit persistent state, and material commitments without explicit authority. It is codified in [AGENTS.md](AGENTS.md)
and [.archcore ADR 0001](.archcore/adr/0001-autonomy-is-excluded-by-design.md).

FACT: `websh` begins with an Agent Stack safety adaptation that overrides upstream background crawling, implicit `.websh` state, and background subagents. Its adaptation explicitly says that
project-local safety and the Orchestrator override later permissive sections. Evidence: [skills/websh/SKILL.md](skills/websh/SKILL.md#L8-L22).

FACT: `deep-research` adds an Agent Stack file/state policy and a bounded-continuation policy that forbids automatic continuation agents, hidden continuation state, daemon-like chains, default
Documents output, and automatic viewer launch. Evidence: [skills/deep-research/SKILL.md](skills/deep-research/SKILL.md#L205-L217) and
[skills/deep-research/SKILL.md](skills/deep-research/SKILL.md#L409-L417).

FINDING P2: Both adapted skills retain extensive upstream prose below the adaptation that instructs background work, persistence, global paths, and viewer output. The adaptations control Agent Stack
interpretation, and the test confirms their presence, but a consumer who follows an unadapted later subsection can still receive contradictory procedural instructions. Consolidate or fence the
upstream material so the only executable instruction path is the safe one. This is a documentation safety debt, not evidence that the prohibited automation currently executes.

## 22. Governance

FACT: Governance is unusually strong for a small routing library: authoritative context routing, accepted architectural records, a stdlib-only coherence gate, explicit frozen-input checks, script
inventory, changelog, and an intentional split among contracts, measurements, and scratchpad state. `just governance` reported 600 passing checks.

FACT: The governance checker covers path resolution, documentation/index links, counts, catalogue agreement, task recipe existence, manifest/library agreement, SKILL.md presence, venv placement, and
bare interpreter use. Evidence: [scripts/check_governance.py](scripts/check_governance.py) and [scripts/README.md](scripts/README.md#L32-L48).

FINDING P1: Governance did not prevent a known status fact from going stale after the holdout execution. The issue is not that it lacks checks in aggregate; it lacks a check or controlled update path
that ties a produced holdout result to `MEMORY.md`, `SCRATCHPAD.md`, and the next-phase plan. Fix the lifecycle gap rather than adding unrelated check count.

## 23. Legacy Audit Findings A1–A7

| Finding | Current status | Evidence | Close? | Remaining action |
| --- | --- | --- | --- | --- |
| A1: non-atomic sync apply | Staged files and atomic state writes now exist | [sync script](scripts/sync_auto_company.py#L51-L60), [ADR 0009](.archcore/adr/0009-sync-apply-is-atomic.md) | CLOSED | Add fault-injection tests for promotion/state failure if maintenance risk rises |
| A2: symlink escape in sync | Source links are refused; source and destination containment are checked | [sync script](scripts/sync_auto_company.py#L99-L134), [rule 0010](.archcore/rules/0010-sync-refuses-symlinks.md) | CLOSED | Add a direct symlink negative test; source protection is otherwise present |
| A3: `websh` autonomy/persistence | Top-level adaptation prohibits the unsafe defaults | [websh adaptation](skills/websh/SKILL.md#L8-L22) | PARTIALLY CLOSED | Remove or fence contradictory upstream execution prose |
| A4: `deep-research` continuation/state/viewers | Adaptation forbids the unsafe defaults | [deep-research policy](skills/deep-research/SKILL.md#L205-L217), [bounded continuation](skills/deep-research/SKILL.md#L409-L417) | PARTIALLY CLOSED | Remove or fence contradictory later upstream workflow prose |
| A5: validator failure/schema drift | Package validation passes; tests validate all packages | [tests/test_skill_contract.py](tests/test_skill_contract.py#L10-L20) | CLOSED | Maintain metadata-key tests with future imports |
| A6: startup skill resources | Required assets, references, and source registry exist and are tested | [tests/test_skill_contract.py](tests/test_skill_contract.py#L21-L33) | CLOSED | None beyond normal link validation |
| A7: no behavioural routing eval | 60-case evaluator, scorer, regression tests, provenance, and closure exist | [scripts/evaluate_routing.py](scripts/evaluate_routing.py), [ROUTING_EVALS.md](ROUTING_EVALS.md) | CLOSED | Continue with new holdout, replay, and shadow evidence |

## 24. Staleness Residuals

FACT: The two formal staleness-audit residuals are a JSONC TypeScript configuration that a strict JSON loader cannot parse and package-internal resource directories flagged by an inverse sweep despite
being registered by package. The changelog calls these tool-versus-project mismatches and records the audit gate as failed rather than falsely passed. Evidence: [CHANGELOG.md](CHANGELOG.md#L221-L255).

CONCLUSION: They are accepted limitations / false-positive classes, not defects in Agent Stack’s routing or installation. Before the next staleness audit, the project should either add explicit
parser/domain adapters or formally accept the residuals in the governing status surface. Do not weaken the sweep or hide the paths simply to turn a meaningful residual into a green result.

## 25. Test and Governance Coverage

| Check | Audit result | What it establishes |
| --- | --- | --- |
| `just check` | PASS: 52 capabilities, 15 personas, 37 skills | Inventory and static routing/skill contract validity |
| `just governance` | PASS: 600 checks | Governed paths, counts, references, contracts, interpreter placement |
| `just routing-eval-check` | PASS: 60 selected of 60 | Development corpus parses and references resolve |
| `just test` | PASS: 55 tests | Closure, installer, routing contract/behaviour, skill contracts, sync behaviours |
| `just freeze-check` | PASS | Current frozen input set matches recorded hashes |

The test suite includes regression tests for closure idempotence, canonical provider selection, capability strength, tool avoidance, tag escalation, team caps, execution-error denominator handling,
asymmetric gates, partial-run warnings, holdout shape, and installer rollback/collisions.

FINDING P2: Tests do not demonstrate end-to-end runner reliability under a full 24-case external invocation, nor do they validate the current-status documentation against emitted result files. Those
omissions directly relate to the two material readiness gaps found here.

## 26. Complexity / Overengineering Review

The routing catalogue is substantial, but its complexity earns its place. Capability metadata eliminates duplicated satisfier lists. Gates model obligations rather than persona summoning. Precedence
makes known ownership conflicts explicit. Invariants define invalid routes. Closure makes finite rules reliable. The evaluator and freeze model turn claims into measured evidence.

The weak complexity boundary is documentation duplication, not routing logic. Historical and accepted records have accumulated several current-state statements, and no mechanism reconciles them after
a run. The new holdout status conflict demonstrates the cost.

Do not remove the capability registry, strength distinction, gates, precedence, closure, or per-row provenance. Each corresponds to a prior observed defect. Prefer two simplifications: retire or fence
superseded upstream autonomous instructions within imported skill bodies, and establish one machine-readable evaluation-run index from which status documents can be generated or checked.

## 27. Remaining P0–P3 Findings

| Priority | Finding | Evidence / impact | Recommended disposition |
| --- | --- | --- | --- |
| P0 | None found | No evidence of destructive automatic action, corrupted state, or fundamentally invalid routing evaluation | None |
| P1 | Spent holdout has only 19 valid rows because 5/24 runner invocations failed | Fresh evidence is partial; failed calls cluster in business and direct-adversarial families | Treat as partial and spent; prove runner reliability before authoring a new holdout |
| P1 | Current operational documents say the holdout is unexecuted | Results and freeze receipt directly contradict `SCRATCHPAD.md` and next-phase status text | Reconcile `MEMORY.md`, `SCRATCHPAD.md`, plans, and status docs with an evidence link |
| P1 | No real-task replay or shadow-mode evidence artefact exists | Architecture has only development and partial holdout evidence | Create replay corpus and non-actioning shadow log before broad rollout |
| P2 | Safety adaptations coexist with contradictory upstream procedure text | `websh` and `deep-research` contain lower, permissive inherited passages | Fence/remove/rewrite those passages under the Agent Stack adaptation |
| P2 | Tool runtime guidance is uneven | Some skill bodies retain global-path or upstream assumptions | Add a concise runtime support matrix and consistent failure guidance |
| P2 | Sync hardening lacks direct fault/symlink negative coverage in visible test names | Code prevents both original classes; future maintenance could regress it | Add focused negative tests when touching sync again |
| P3 | No `just doctor` or symlink helper | Installer correctness is tested | Add only if operators encounter repeated diagnosis friction |

## 28. Production-Readiness Matrix

| Area | Rating | Basis |
| --- | --- | --- |
| Persona model | READY WITH MINOR GAPS | Operational contracts and ownership records exist; some boundaries remain evidence-driven |
| Skill model | READY WITH MINOR GAPS | Manifest/catalogue alignment and package validation pass; imported runtime prose needs cleanup |
| Routing contract | READY | One persona model, capabilities, gates, precedence, and invariants are coherent and validated |
| Gate logic | READY | Obligations, strength, escalation, and asymmetric scoring are explicit and tested |
| Capability taxonomy | READY WITH MINOR GAPS | Structurally strong; semantic honesty remains a review obligation |
| Deterministic closure | READY | Narrow, deterministic, idempotent, and prohibited from changing judgement ownership |
| Behavioral evaluation | READY WITH MINOR GAPS | Harness/scoring/provenance are strong; external runner reliability remains weak |
| Holdout methodology | MATERIAL GAPS | Design and freeze were valid; execution lost 5/24 cases and spent the evidence |
| Governance | READY WITH MINOR GAPS | 600 checks pass; current evaluation-state reconciliation is missing |
| Runtime/tooling | READY WITH MINOR GAPS | Isolation and explicit interpreter selection are sound; skill-level guidance varies |
| Installation | READY | Symlink-only, collision-safe, rollback-aware, tested |
| Upstream sync | READY WITH MINOR GAPS | A1/A2 are fixed; add direct fault-injection coverage later |
| Safety/human control | READY WITH MINOR GAPS | Policy/adaptations exist; imported contradictory prose should be removed or fenced |

## 29. Recommended Next Actions

1. Record the spent holdout as current truth. Link its freeze receipt, log, and JSONL result from `MEMORY.md`, `SCRATCHPAD.md`, the evaluation plan, and relevant routing documentation. State 16/19
   corrected, 5 runner errors, and that the corpus is spent.
2. Build a non-evidence runner qualification suite. It should exercise a representative command repeatedly, validate JSON extraction, record command exit reliability, and block any future single-use
   run when the runner is unstable. It must not use a holdout corpus.
3. Preserve the 24-case result without changing its cases or expectations. Classify its three valid routing failures and five runner failures separately. Do not optimise `routing.toml` from it.
4. Define the historical replay input contract: original task text, contemporaneous constraints/evidence, historical resolution, model initial route, repaired route, human review, and outcome. Use it
   to challenge ownership and team decisions without treating past practice as automatically correct.
5. Define a shadow-mode log and run it beside normal work with no delegated action. Measure disagreements, rejected routes, runtime blockers, human overrides, and outcome quality.
6. After the runner qualification process is frozen, author a new blind holdout. Keep the development 60 and spent 24 isolated from its authoring process.
7. Consolidate the `websh` and `deep-research` safety adaptations with the imported body text so unsafe historical instructions cannot be followed as operational steps.

Explicitly do **not** change the frozen 60 to chase a higher score, remove deterministic closure, merge gates into personas, weaken primary-strength requirements, turn advisory routing rules back into
mandates, or downgrade execution errors into model scores.

## 30. Final Verdict

1. **Is the current Agent Stack architecturally sound?** Yes. Its core model is coherent, source-backed, and materially stronger than the earlier audited state.
2. **Is the routing model now coherent?** Yes. Gates, capabilities, ownership precedence, advisory hints, invariants, and closure have distinct roles and are guarded against the former
   two-persona-model failure.
3. **Is deterministic closure correctly separated from model judgement?** Yes. It repairs finite catalogue obligations, recomputes runtime, and does not select the primary owner or decide gate truth.
4. **Are personas and skills sufficiently defined?** Largely yes. Personas are operational and skill metadata/runtime classing is complete. Imported skill safety text still needs consolidation.
5. **Are routing evals trustworthy?** Their scorer, provenance, coverage, and denominator treatment are trustworthy. The current external runner reliability is not sufficient for a full single-use
   evidence run.
6. **Has the development corpus been overfit?** It should be treated as overfit risk by design. It is frozen regression data; the project should not tune it further.
7. **Is the unseen holdout methodology valid?** Its authoring, freeze, and scoring method were valid. The executed measurement is partial because five calls failed, and the corpus is spent.
8. **What remains before broad production readiness?** Reconcile current status, establish reliable runner qualification, obtain a fresh complete out-of-sample measurement, conduct historical replay,
   and operate in shadow mode.
9. **Which old audit findings can now be closed?** A1, A2, A5, A6, and A7 are closed. A3 and A4 are partially closed because safety adaptations are present but coexist with contradictory inherited
   instructions.
10. **What should explicitly not be changed?** The capability-first model, primary/supporting strength rule, advisory-only routing rules, precedence structure, deterministic closure boundary, frozen
    development corpus, and execution-error denominator rule.

The decisive answer is therefore conditional: Agent Stack is ready to continue controlled evaluation and shadow deployment, but it is not ready for broad production routing until it replaces the
partial spent holdout with reliable fresh evidence and closes the status/governance loop exposed by that run.
